# Contract: task-reframe-guard

**Type:** Code-enforced (Python `Contract` subclass in `core/contracts.py`)
**Failure mode:** FM-025 (silent mid-session task model pivot)
**Severity:** warn (does not block)

## Trigger

Fires post-response when ALL of the following hold:

1. The response contains a task-claim phrase (`I'll …`, `I'm going to …`,
   `building …`, `creating …`, `writing …`, `adding …`, `fixing …`,
   `wiring …`, `implementing …`) at least 10 chars long.
2. A previous task claim is on file from a recent response within the
   recency window (15 minutes — `_RECENCY_SECONDS = 900`).
3. Both the previous and current task phrases have ≥4 content words
   (`_MIN_CONTENT_WORDS = 4`).
4. There is zero overlap between the content-word sets.
5. The current response does not mention any word from the previous task.

## Precondition

When Shadow shifts mid-flow from one task to a completely different one
without acknowledging the pivot, surface it so the user can correct the
direction before downstream work proceeds on the new track.

## Enforcement

`TaskReframeGuard.check_post` in `core/contracts.py`.

State is keyed at the class level (`_last_task: dict[session_key →
(task_text, ts_unix)]`); session-aware keying is a follow-up.

## Recovery

When this fires:
- If the pivot was intentional, acknowledge it explicitly:
  `"Pivoting from X to Y because …"` — the contract is silent when the
  previous task's content words appear in the response.
- If unintentional, finish the original task first.

## Why this narrowing happened (2026-06-01)

Pre-tightening, the contract fired 6 times in a single 8h session with a
high false-positive rate. The cause was the heuristic running without a
recency gate: a task claim from much earlier was compared against any
later short claim ("walk the exact path", "grab it the second it
arrives"), producing pivots that were actually fine-grained continuations
within the same logical work span.

The repair:
- Added a 15 min recency window — stale prior tasks no longer trigger.
- Raised `_MIN_CONTENT_WORDS` from 3 to 4 — three-word phrases like
  "walk the exact path" no longer have enough signal to be called a
  pivot.

## Tests

`tests/test_contracts.py::TestTaskReframeGuard`:
- `test_distant_gap_does_not_fire`
- `test_short_task_phrase_does_not_fire`
- `test_real_pivot_within_window_fires`
- `test_no_prior_task_does_not_fire`
