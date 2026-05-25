# Contract: ci-loop-closure

## Type
Post-push gate — code-enforced in `core/contracts.py:CILoopClosureContract`

## Trigger
Any `git push` action where `files_edited` is non-empty.

## Precondition
`ctx.action_params["ci_result"]` must be set to the output of `post_push_ci_loop()`
from `core/ci_loop.py`. The CI result must have `status == "green"` before Done is reported.

## Enforcement
**Code-enforced** in `core/contracts.py:CILoopClosureContract`:
- Missing `ci_result`: warn-severity (contract not yet wired into push workflow)
- `status == "escalate"`: block-severity (do not declare Done)
- `status == "green"`: passes

## The loop

```python
from core.ci_loop import post_push_ci_loop, format_ci_result

result = post_push_ci_loop(max_attempts=3)
# result = {"status": "green"|"escalate", "output": str, "attempts": int}

done_signal = format_ci_result(result)
# Green:    "Done. Tests: 12 passed, 0 failed (1.2s)"
# Fixed:    "Done. Tests: 12 passed — fixed on attempt 2."
# Escalate: "⚠️ CI still failing after 3 attempts. [traceback]"
```

## Done signal format

| Result | Signal |
|---|---|
| Green, 1st attempt | `Done. Tests: N passed, 0 failed (Xs)` |
| Green, Nth attempt | `Done. Tests: N passed — fixed on attempt N.` |
| Escalate | `⚠️ CI still failing after N attempts.` + traceback pasted |

## Violation recovery

If `status == "escalate"`:
1. Post `format_ci_result(result)` to Discord (channel: intake or shadow-hq)
2. Wait for the user — do not declare Done
3. Do not push additional "fix attempts" past the max without the user's input

## Iteration bound

`max_attempts=3` matches the loop-tripwire contract (which blocks 3+ commits to the same file).
These two contracts stay in sync — if loop-tripwire fires, ci-loop-closure has already escalated.

## Origin

2026-04-29: Derived from OpenAI Symphony's CI monitoring pattern. Symphony loops on CI
after every push and only marks tickets Done when CI is green. Shadow adopted the same
pattern to eliminate the round-trip where the user reports failing tests back.

## Interaction with existing contracts

- Complements `verify-before-push`: verify-before-push gates the push; ci-loop-closure gates the Done signal
- Bounded by `loop-tripwire`: max 3 fix iterations, matching the tripwire threshold
