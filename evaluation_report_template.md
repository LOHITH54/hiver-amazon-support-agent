# AmazonHelp AI Support Agent — Evaluation Report

## 1. Problem framing
Build an AI support agent for AmazonHelp that classifies incoming customer messages, drafts a reply grounded in historical AmazonHelp resolutions, and decides whether to auto-handle or escalate.

## 2. Dataset and scope
- Source: Customer Support on Twitter dataset.
- Brand: AmazonHelp.
- Scope: English-first.
- Evaluation set: 200 cases selected for intent coverage.
- Final submission requirement: human verification of all gold labels.

## 3. Intent taxonomy
1. delivery_issue
2. order_issue
3. refund_return
4. payment_billing
5. account_access
6. prime_membership
7. product_issue
8. other

## 4. Baselines
Trivial baseline: majority-class predictor.
Simple baseline: TF-IDF word/phrase features + balanced logistic regression.

Development results currently available in `baseline_results.csv`. These must not be presented as final benchmark results until the Golden Set is independently human-verified.

## 5. Reply grounding
The system retrieves similar historical customer cases and associated AmazonHelp replies using TF-IDF cosine similarity. Evidence is used to guide the draft rather than inventing account-specific facts.

## 6. Escalation
See `escalation_policy.md`. The benchmark intentionally prefers escalation when confidence is low, the request is ambiguous, the issue is repeated/unresolved, or higher-risk/legal/fraud wording appears.

## 7. Top 5 failures
To be populated after human verification and final evaluation. Each failure should include:
- customer message
- predicted intent/decision
- expected intent/decision
- retrieved evidence
- why the system failed
- hypothesis for improvement

## 8. What is misleading about my headline number?
A single accuracy number can overstate performance because:
- the Golden Set is coverage-focused rather than naturally distributed;
- some intents are harder and have fewer examples;
- weakly labeled training data can leak linguistic shortcuts;
- retrieval similarity does not prove that the generated response is correct;
- an LLM can produce fluent but unsupported replies.

Therefore report macro-F1, per-intent scores, escalation agreement, and evidence-grounding scores alongside accuracy.

## 9. Next-week plan
- Independently verify the 200 Golden Set labels.
- Add a true semantic/LLM classifier or stronger embedding model.
- Add an explicit evidence selection/reranking step.
- Evaluate reply quality with the rubric and human agreement.
- Tune escalation threshold against false-auto-handle risk.
