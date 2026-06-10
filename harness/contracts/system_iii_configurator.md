# system-iii-configurator

**Type:** Code-enforced pre-check (`core/contracts.py`)
**Failure mode:** FM-030
**Enforcement:** deterministic; no LLM calls; zero-latency

## What it does

Scores each action context on a 0-1 complexity scale derived from six
observable signals, then fires a `warn`-severity violation when the score
exceeds 0.65.  The violation requests a written "forward-simulation" — a
one-paragraph plan that states the goal, expected tool sequence, and predicted
outcome — before the next tool call proceeds.

This implements the "System III" planning layer described in the improvement
queue: a configurator that intercepts execution at high-complexity inflection
points and requests deliberate simulation rather than reactive step-by-step
tool use.

## Trigger

Pre-check fires on actions: `edit_file`, `git_commit`, `git_push`, `respond`.

## Complexity signals (additive, capped at 1.0)

| Signal | Condition | Score |
|--------|-----------|-------|
| Tool call volume | ≥12 calls this session | +0.30 |
| Tool call volume | ≥8 calls | +0.20 |
| Tool call volume | ≥5 calls | +0.10 |
| Exploratory tool diversity | ≥4 Glob/Grep/Search calls | +0.20 |
| Exploratory tool diversity | ≥2 | +0.10 |
| User uncertainty markers | ≥3 matches | +0.25 |
| User uncertainty markers | ≥1 match | +0.12 |
| Cross-cutting edit scope | ≥4 top-level dirs | +0.20 |
| Cross-cutting edit scope | ≥2 top-level dirs | +0.10 |
| High-stakes file edits | any `core/` or critical script | +0.15 |
| Blind edits | ≥2 edits without prior reads | +0.10 |

## Precondition

Score ≥ 0.65.

## Enforcement

`warn`-severity only — the violation is logged and surfaced as a recovery hint
but does not block execution.  Signals are appended to
`state/system_iii_queue.jsonl` for nightly threshold analysis.

## Recovery

Write a one-paragraph forward-simulation (goal → tool sequence → predicted
outcome) before executing the next tool call.

## Escalation

No escalation.  Chronic patterns (score consistently > 0.8) are surfaced via
the nightly `scripts/session_audit.py` pipeline.

## Tuning history

| Date | Change |
|------|--------|
| 2026-06-09 | Initial implementation; threshold 0.65; warn-only |
