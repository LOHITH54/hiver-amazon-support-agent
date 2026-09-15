# Escalation Policy v1

The agent has two possible outcomes: `AUTO-HANDLE` or `ESCALATE`.

## ESCALATE when any of these apply
1. The customer uses legal/lawsuit/court/legal-notice language.
2. The customer alleges fraud, scam, counterfeit goods, identity theft, or stolen property.
3. The customer explicitly reports a repeated unresolved issue (e.g. multiple prior contacts, prolonged no-response).
4. The request requires private account/order investigation that the agent cannot perform from the public dataset.
5. Intent confidence is below the configured threshold (default 0.55).
6. The message is genuinely ambiguous or outside the supported taxonomy (`other`).

## AUTO-HANDLE otherwise
Routine, clearly classified support requests that can be answered safely using the historical-resolution evidence.

## Why this policy
The system is designed to optimize for safe handling rather than maximizing automation rate. Escalation is preferable when the cost of a wrong automated response is high.

## Limitation
This is a benchmark policy, not a claim about Amazon's real internal escalation policy. The project only simulates support behavior from the public dataset.
