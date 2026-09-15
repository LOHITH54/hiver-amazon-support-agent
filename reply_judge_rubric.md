# Reply Quality + Evidence Judge Rubric

For each generated reply, score independently:

## Reply quality (0–4)
0 — Wrong, unsafe, or unrelated.
1 — Major misunderstanding or unusable response.
2 — Partially helpful but misses the main issue or gives weak/unsupported guidance.
3 — Helpful, relevant, clear, and appropriately cautious.
4 — Excellent: directly addresses the issue, concise, actionable, and avoids unsupported claims.

## Evidence grounding (0–2)
0 — Recommendation is unsupported or contradicts retrieved AmazonHelp evidence.
1 — Broadly consistent with the evidence but contains extra assumptions.
2 — The proposed action is directly supported by one or more retrieved historical AmazonHelp resolutions.

## Hallucination / policy check
Mark `FAIL` if the reply invents account/order facts, promises an outcome Amazon cannot verify, fabricates a policy, or claims to have accessed private customer data.

## Escalation
`ESCALATE` is preferred when the case is ambiguous, repeated/unresolved, legal/fraud/high-risk, or requires account-specific investigation that the agent cannot perform.
