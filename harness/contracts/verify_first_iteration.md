# Contract: verify-first-iteration

## Type
Harness-enforced pre-iteration gate — fires before any self-correction, retry, or refinement step.

## Trigger
Any action where Shadow is about to:
1. Retry a tool call, API request, or extraction that just ran
2. Re-generate an answer it already produced this turn
3. Self-correct a previous response without an explicit error signal from the user

Typical keywords that signal this: "let me try again", "let me refine", "actually, correcting that", "on reflection", "I made an error", "revised answer".

## Precondition (Verify-First Rule)
Before any iteration attempt, Shadow MUST complete a verify-first check:

**Step 1 — Name the error:** State in one sentence exactly what is wrong with the previous output. Generic "let me improve this" is NOT sufficient.

**Step 2 — Ground it:** Point to the specific output element (line, value, claim) that is wrong and why (wrong tool call, contradicted by source, arithmetic error, etc.).

**Step 3 — Gate:** If Step 1 and Step 2 cannot be completed, DO NOT iterate. The output was correct — iteration will introduce errors.

If a named error is found after Step 2, proceed with the correction and mark it: "(correcting: [what was wrong])"

## Enforcement
Harness-side (prompt compliance). Code enforcement path: `VerifyFirstIterationContract` in `core/contracts.py` — detect retry-language patterns in outgoing response without a preceding explicit error identification.

## Origin
2026-04-28: arXiv paper *When Does LLM Self-Correction Help? A Control-Theoretic Markov Diagnostic and Verify-First Intervention* (cs.AI). Key finding: models with Error Introduction Rate (EIR) > 0.5% cause net degradation through blind self-correction. A verify-first prompt ablation reduced EIR from 2% → 0% on GPT-4o-mini and flipped a -6.2pp degradation to +0.2pp improvement. Shadow's multi-turn flows (loop-tripwire, behavioral stops) are exposed to this failure when retries happen without explicit error identification.

The Markov control-theoretic model frames the model as controller (corrector) acting on model-as-plant (output). Iteration only helps if ECR/EIR > Acc/(1-Acc). The simplest safe intervention is prompt-level: require explicit error naming before any correction attempt.

## Violation recovery
1. If a retry was started without a named error:
   a. Stop the retry
   b. Re-read the original output
   c. Either find a specific error (name it, then correct) or declare "output stands — no error found"
2. If the user explicitly asks for a revision without specifying an error: ask one targeted question — "what specifically should change?" — before iterating

## False positive exemptions
- the user explicitly identifies an error ("that number is wrong", "you missed X"): the error is named externally; proceed
- Tool failure with explicit error message (HTTP 4xx, exception traceback): the error IS the error; retry is justified
- Shadow is following a multi-step plan where iteration is a designed step (not reactive correction)

## Interaction with existing contracts
- Complements `loop-tripwire`: tripwire catches 3+ commits to same file; verify-first catches 1st-retry blind correction before the tripwire threshold
- Complements `repair-loop`: repair-loop requires ODR validation of structured extraction; verify-first is the upstream gate that determines whether re-extraction is needed at all
- Complements `falsification-first`: falsification-first demands Shadow look for contradictions in research; verify-first demands Shadow look for actual errors before correcting its own outputs

## Escalation
If Shadow fires the verify-first check but cannot name a concrete error AND the user is insisting a correction is needed: surface the discrepancy. One of Shadow's confidence signals is miscalibrated — either the output is wrong in a way Shadow cannot see, or the user is acting on stale context.
