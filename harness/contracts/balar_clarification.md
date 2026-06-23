# Contract: balar-clarification

## Type
Post-response guard — Haiku-judged expected-mutual-information (EMI) gate via
`core/contracts.py:BALARClarificationGuard`. Severity is `block` when EMI < 0.2
(noise-level clarification), `warn` between 0.2 and 0.5.

## Failure mode
FM-013 — asking a clarifying question that does not maximally disambiguate the
plausible interpretations of the user's request. Two sub-cases:

1. **Noise** (EMI < 0.2): the question carries essentially no information —
   either the answer is already implied by standing authority, or the choice
   between interpretations is irrelevant to the action. Block.
2. **Suboptimal** (0.2 ≤ EMI < 0.5): a question is being asked but it is not
   the *highest-information* question available. Warn.

## Trigger
Post-check. Only fires when the response contains a clarifying-question
pattern (`can you`, `do you`, `which`, `could you`, `what did you mean`, etc.)
followed by a question mark. Skipped when `ctx.user_message` is >200 chars —
long messages tend to carry their own context and Haiku scoring is noisier on
them.

## Precondition
the user sent a message short enough that latent interpretations are plausible, and
Shadow's response includes a clarifying question. The contract enumerates
latent interpretations via Haiku and rates whether the asked question maximally
disambiguates them.

## Enforcement
`_emi_score(user_message, response)` calls Haiku with a BALAR prompt — derived
from the paper "Bayesian Agentic Loop for Active Reasoning" (arXiv:2605.05386).
The model returns a 0-1 score. Failure modes of the scorer (timeout, parse
error, network) return a neutral score that does not fire the guard.

## Recovery
- EMI < 0.2: drop the question and execute the default action under standing
  authority. Standing authority covers most action paths; a near-zero EMI
  question is almost always asking permission for something already authorized.
- 0.2 ≤ EMI < 0.5: rewrite to ask the single question that best distinguishes
  the two most plausible interpretations of the user's message. If the two
  interpretations are equally cheap to execute, just execute both and report.

## Tests
`tests/test_contracts.py::TestBALARClarificationGuard` (if present) — confirms
the question-detection regex fires on the canonical clarification verbs and
that long user messages are skipped. The EMI scorer itself is not unit-tested
because it depends on a live Haiku call.

## History
- 2026-06-17: Promoted EMI < 0.2 from warn-only to block after the prior
  warn-only mode let 0.00-EMI clarifications keep shipping. Origin: backlog
  item `20260617T074925_improve_l1_non_code:_404e`.
- 2026-06-23 (gap-closer): Harness doc added. Contract fired twice in the
  prior 24h window — both at confidence 0.00 against actions that were
  authorized under standing authority. The `block` severity is doing the
  right thing; this doc exists so future readers can trace the rationale.
