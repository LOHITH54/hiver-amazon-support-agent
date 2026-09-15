\# Decision Log



\## 1. Selected AmazonHelp as the target brand

AmazonHelp was selected because it has high support volume and a relatively high rate of customer follow-up messages, providing richer evidence for historical resolution behavior.



\## 2. Used an AmazonHelp-related subset

Instead of repeatedly scanning the full Twitter dataset, an AmazonHelp-related working subset was created containing relevant customer and support tweets.



\## 3. English-first scope

The first version focuses on English customer messages so the intent taxonomy and evaluation remain consistent and tractable.



\## 4. Defined eight top-level intents

The taxonomy uses delivery\_issue, order\_issue, refund\_return, payment\_billing, account\_access, prime\_membership, product\_issue, and other. This avoids excessive fragmentation of sparse categories.



\## 5. Kept cancellation and replacement as subcases

Cancellation and replacement were not made separate top-level intents because they were relatively sparse and overlap strongly with order, refund, and product problems.



\## 6. Used keyword rules only for weak supervision

Keyword matching was used to create scalable provisional training labels, not as the final production decision rule.



\## 7. Used TF-IDF + Logistic Regression as the simple classifier

This was chosen as a transparent, lightweight baseline that can run locally without requiring an external model API.



\## 8. Excluded the evaluation cases from training

Golden-set tweet IDs are removed from classifier training to reduce direct evaluation leakage.



\## 9. Retrieved historical resolutions using response\_tweet\_id

Customer messages were linked to their actual historical Amazon support replies using the dataset's response relationship rather than treating unrelated tweets as evidence.



\## 10. Retrieved three historical examples

The agent retrieves the top three similar historical customer cases so the response can be grounded in multiple examples rather than a single potentially noisy match.



\## 11. Treated retrieval as evidence, not policy

Historical AmazonHelp replies are used as evidence of past behavior. They are not treated as guarantees that the same resolution or policy is currently valid.



\## 12. Used conservative reply templates

The system produces intent-specific drafts instead of copying historical support replies verbatim and avoids inventing customer-specific facts.



\## 13. Added narrow high-precision intent overrides

Strong phrases such as duplicate charges, refund requests, and missing delivered packages receive narrow overrides because overlapping words such as "order" and "charged" can confuse the statistical classifier.



\## 14. Added conservative escalation

The agent escalates higher-risk/legal/fraud wording, repeated or unresolved issues, low-confidence predictions, and unsupported or ambiguous cases.



\## 15. Did not present the 91.5% result as an improvement over the simple baseline

The current classifier is itself the TF-IDF + Logistic Regression simple baseline. The main contribution is the complete pipeline combining classification, historical retrieval, grounded drafting, and escalation.



\## 16. Kept the current Golden Set provisional

The 200-case Golden Set is AI-assisted and requires independent human verification before its results can honestly be presented as the assignment's final hand-labelled benchmark.



\## 17. Reported reply evaluation separately

Reply quality and evidence grounding are evaluated separately from intent accuracy because a correct intent prediction does not guarantee a useful or well-grounded response.

