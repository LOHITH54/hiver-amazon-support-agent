import argparse, re
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "amazon_related.csv"
GOLD = ROOT / "amazon_golden_set_labeled.xlsx"

INTENTS = [
    "delivery_issue", "order_issue", "refund_return", "payment_billing",
    "account_access", "prime_membership", "product_issue", "other"
]

PATTERNS = {
    "delivery_issue": r"\b(deliver|delivery|delivered|package|parcel|shipment|shipping|tracking|track|courier|arriv|late|delay|post office|redeliver|out for delivery)\b",
    "order_issue": r"\b(order|ordered|ordering|cancel|cancellation|wrong order)\b",
    "refund_return": r"\b(refund|return|returned|money back|reimburse|reimbursement)\b",
    "payment_billing": r"\b(payment|pay\b|paid|charge|charged|billing|bill|invoice|credit card|debit card|emi)\b",
    "account_access": r"\b(account|login|log in|sign in|password|access|locked|verification|verify)\b",
    "prime_membership": r"\b(prime|membership|member|subscription)\b",
    "product_issue": r"\b(product|item|seller|broken|damaged|defect|defective|not working|doesn.?t work|warranty|fake|counterfeit)\b",
}

def keyword_seed(text):
    hits = [k for k,p in PATTERNS.items() if re.search(p, text or "", re.I)]
    return hits[0] if len(hits) == 1 else ("other" if not hits else None)

def load_training():
    df = pd.read_csv(DATA, low_memory=False)
    df = df[df["inbound"].astype(str).str.lower().isin(["true","1"])].copy()
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df[df["text"].str.len().between(25, 400)]
    # Exclude the evaluation set completely.
    gold_ids = set()
    if GOLD.exists():
        g = pd.read_excel(GOLD, sheet_name="Golden Set Review")
        gold_ids = set(g["tweet_id"].astype(str))
    df["tweet_id"] = df["tweet_id"].astype(str)
    df = df[~df["tweet_id"].isin(gold_ids)]
    df["label"] = df["text"].map(keyword_seed)
    df = df[df["label"].notna()]
    # Cap each class to keep local training lightweight.
    parts = []
    for label in INTENTS:
        x = df[df["label"] == label]
        if len(x):
            parts.append(x.sample(min(len(x), 12000), random_state=42))
    return pd.concat(parts, ignore_index=True)

def build_retriever():
    df = pd.read_csv(DATA, low_memory=False)
    df["tweet_id"] = df["tweet_id"].astype(str)
    df["text"] = df["text"].fillna("").astype(str)
    # Customer messages that have a historical Amazon reply in response_tweet_id.
    support = df[~df["inbound"].astype(str).str.lower().isin(["true","1"])].copy()
    support_map = dict(zip(support["tweet_id"], support["text"]))
    cust = df[df["inbound"].astype(str).str.lower().isin(["true","1"])].copy()
    cust["historical_reply"] = cust["response_tweet_id"].fillna("").astype(str).map(support_map).fillna("")
    cust = cust[(cust["text"].str.len() >= 25) & (cust["historical_reply"].str.len() > 0)]
    if GOLD.exists():
        g = pd.read_excel(GOLD, sheet_name="Golden Set Review")
        cust = cust[~cust["tweet_id"].isin(set(g["tweet_id"].astype(str)))]
    cust = cust.drop_duplicates("text").head(50000).copy()
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=2, max_features=60000)
    X = vec.fit_transform(cust["text"])
    return cust.reset_index(drop=True), vec, X

def train_classifier():
    tr = load_training()
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=2, max_features=80000)
    X = vec.fit_transform(tr["text"])
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(X, tr["label"])
    return vec, clf

def escalation_decision(text, confidence, intent):
    s = text.lower()
    reasons = []
    if re.search(r"\b(lawyer|legal|lawsuit|court|legal notification|fraud|scam|counterfeit|identity theft|stolen)\b", s):
        reasons.append("higher-risk/legal/fraud wording")
    if re.search(r"\b(still no|no response|no updates|fifth time|5th time|again and again|10 days|weeks|months)\b", s):
        reasons.append("repeated or unresolved problem")
    if confidence < 0.60:
        reasons.append("low intent confidence")
    if intent == "other":
        reasons.append("unsupported or ambiguous intent")
    if reasons:
        return "ESCALATE", "; ".join(reasons)
    return "AUTO-HANDLE", "routine supported intent with sufficient confidence"

def run_agent(text):
    clf_vec, clf = train_classifier()
    Xq = clf_vec.transform([text])
    probs = clf.predict_proba(Xq)[0]
    idx = probs.argmax()
    intent = clf.classes_[idx]
    confidence = float(probs[idx])

    # High-precision overrides for cases where overlapping words (e.g.
    # "order" + "charged") can confuse the statistical classifier.
    # The override is intentionally narrow and only fires on strong phrases.
    s = text.lower()
    if re.search(r"\b(charged twice|charge(d)? twice|charged two times|charged two times|double charge|duplicate charge|payment twice)\b", s):
        intent = "payment_billing"
        confidence = max(confidence, 0.90)
    elif re.search(r"\b(refund|money back|reimburse|reimbursement)\b", s):
        intent = "refund_return"
        confidence = max(confidence, 0.90)
    elif re.search(r"\b(package|parcel|shipment)\b.*\b(not received|didn.?t receive|never received|missing|lost|delivered)", s) or re.search(r"\b(delivered|delivery)\b.*\b(not received|didn.?t receive|never received|missing)", s):
        intent = "delivery_issue"
        confidence = max(confidence, 0.90)

    cases, ret_vec, ret_X = build_retriever()
    q = ret_vec.transform([text])
    sims = cosine_similarity(q, ret_X).ravel()
    top = sims.argsort()[-3:][::-1]
    evidence = cases.iloc[top].copy()

    decision, reason = escalation_decision(text, confidence, intent)

    if decision == "ESCALATE":
        reply = ("Thanks for reaching out. I’m sorry you’re dealing with this. "
                 "I’d like a support specialist to take a closer look and help resolve it.")
    elif len(evidence):
        # Use the strongest historical example to produce a conservative, intent-specific draft.
        # We do not copy the historical reply verbatim and we do not invent account/order facts.
        historical = str(evidence.iloc[0]["historical_reply"]).strip()
        h = historical.lower()
        if intent == "payment_billing" and ("authorisation" in h or "authorization" in h):
            reply = ("Thanks for reaching out. For duplicate charges, AmazonHelp has historically "
                     "checked whether one of the entries is an authorization rather than a completed "
                     "charge. Please review the two entries on your statement and contact Amazon support "
                     "through the official channel if both appear as completed charges, so the team can "
                     "investigate the billing details.")
        elif intent == "delivery_issue":
            reply = ("Thanks for reaching out. For delivery problems like this, AmazonHelp has "
                     "historically started by checking the delivery details and whether the package may "
                     "have been left at another location. If you still cannot locate it, contact Amazon "
                     "support through the official channel so the team can investigate the delivery.")
        elif intent == "refund_return":
            reply = ("Thanks for reaching out. AmazonHelp has historically directed similar return or "
                     "refund cases to the order’s return/refund support flow. Please review the return "
                     "or refund status for the order and contact Amazon support if the status does not "
                     "match what you expect.")
        elif intent == "order_issue":
            reply = ("Thanks for reaching out. AmazonHelp has historically handled similar order cases "
                     "by checking the order details and the available order-support options. Please "
                     "review the order in Amazon and use the official support channel if you need the "
                     "team to investigate it.")
        elif intent == "account_access":
            reply = ("Thanks for reaching out. AmazonHelp has historically handled similar account "
                     "issues by checking the account/access details. Please use Amazon’s official "
                     "account-support channel so the team can investigate without you sharing sensitive "
                     "account information here.")
        elif intent == "prime_membership":
            reply = ("Thanks for reaching out. AmazonHelp has historically handled similar Prime or "
                     "membership questions by checking the membership details. Please review your Prime "
                     "membership status and contact Amazon support through the official channel if it "
                     "does not look correct.")
        elif intent == "product_issue":
            reply = ("Thanks for reaching out. AmazonHelp has historically handled similar product "
                     "issues by reviewing the item and order details before suggesting the appropriate "
                     "support option. Please review the order and use the official Amazon support channel "
                     "if you need further help.")
        else:
            reply = ("Thanks for reaching out. I found a similar historical AmazonHelp case, but the "
                     "available context is not specific enough to safely recommend an exact resolution. "
                     "Please use the official Amazon support channel so a team member can investigate.")
    else:
        reply = "Thanks for reaching out. Please contact Amazon support through the official support channel so a team member can investigate."

    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "decision": decision,
        "reason": reason,
        "reply": reply,
        "evidence": evidence[["tweet_id","text","historical_reply"]].to_dict("records") if len(evidence) else []
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    args = ap.parse_args()
    result = run_agent(args.text)
    for k,v in result.items():
        print(f"\n{k.upper()}:\n{v}")
