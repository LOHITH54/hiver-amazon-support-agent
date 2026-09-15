from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent import train_classifier

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "amazon_golden_set_labeled.xlsx"

def main():
    gold = pd.read_excel(GOLD, sheet_name="Golden Set Review")
    # Only evaluate rows that have a human/verified gold label.
    gold = gold[gold["gold_intent"].notna() & (gold["gold_intent"].astype(str).str.len() > 0)].copy()
    if len(gold) == 0:
        print("No verified gold labels yet.")
        return
    vec, clf = train_classifier()
    pred = clf.predict(vec.transform(gold["customer_message"].astype(str)))
    print("N =", len(gold))
    print("Accuracy =", round(accuracy_score(gold["gold_intent"], pred), 4))
    print("Macro-F1 =", round(f1_score(gold["gold_intent"], pred, average="macro"), 4))
    print(classification_report(gold["gold_intent"], pred, zero_division=0))

if __name__ == "__main__":
    main()
