import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent import run_agent

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "amazon_golden_set_labeled.xlsx"
OUT = ROOT / "reply_evaluation_cases.csv"


def main():
    gold = pd.read_excel(GOLD, sheet_name="Golden Set Review")

    rows = []

    for i, row in gold.iterrows():
        text = str(row["customer_message"])
        result = run_agent(text)

        rows.append({
            "case_id": row["case_id"],
            "tweet_id": row["tweet_id"],
            "customer_message": text,
            "gold_intent": row["gold_intent"],
            "gold_escalate": row["gold_escalate"],
            "predicted_intent": result["intent"],
            "confidence": result["confidence"],
            "decision": result["decision"],
            "reason": result["reason"],
            "reply": result["reply"],
            "evidence_count": len(result["evidence"]),
            "top_evidence_customer": (
                result["evidence"][0]["text"]
                if result["evidence"] else ""
            ),
            "top_evidence_reply": (
                result["evidence"][0]["historical_reply"]
                if result["evidence"] else ""
            ),
        })

        print(f"Processed {i + 1}/{len(gold)}")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()