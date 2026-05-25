# quantitative-claim-receipt

**Type:** Post-check (observe + warn)
**Failure mode:** FM-022 (self-consistency), FM-028 (outcome equivalence)
**Sources:** PRISM arXiv:2605.19382 + HalluWorld arXiv:2605.19341

## Trigger

Fires on any `respond` action whose text matches the quantitative output claim pattern:
`(produced|published|queued|processed|dispatched|sent|posted|compiled|generated) <N> (briefs|signals|posts|issues|emails|candidates|items|articles)`

## Precondition

Two conditions both required for a violation:
1. A matching claim exists in the current response.
2. A prior receipt for the same noun (e.g., "brief") exists in `state/loop_receipts.jsonl` from the same process session with a **different count**.

A first-time claim with no prior receipt always passes (only logs a receipt).

## Enforcement

Code: `QuantitativeClaimReceiptContract` in `core/contracts.py`.

Two mechanisms:
1. **Receipt emission** (always): every matched claim is appended to `state/loop_receipts.jsonl` with timestamp, session key, noun, verb, count, and a short context snippet.
2. **Reference check** (on mismatch): if the same noun was claimed with a different count earlier in the same session, fires `severity=warn` with the discrepancy. Does not block execution.

## Recovery

Check `state/loop_receipts.jsonl` and the actual state files (`state/briefs/`, queue JSONs) to confirm which count is correct before reporting numbers.

## Escalation

Warn-only. Session audit (`scripts/session_audit.py`) grades discrepancy frequency as part of FM-022 self-consistency scoring.

## Rationale

PRISM: multi-step loop pipelines should emit step receipts for cross-checking.
HalluWorld: quantitative output claims can be validated against a reference world model (the receipt log) to detect number drift between iterations.
