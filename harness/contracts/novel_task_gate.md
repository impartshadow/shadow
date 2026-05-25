# Contract: novel-task-gate

## Type
Harness-enforced gate — fires when Shadow receives a task that matches no known skill and has no similar pattern in recent git history.

## Trigger
Any task where:
1. No file in `harness/skills/` clearly applies to the request domain AND
2. `git log --oneline -50` contains no commits with keywords matching the task

## The problem this solves

Agentic systems fail silently on out-of-distribution tasks. The failure pattern: Shadow executes confidently, produces plausible-looking output, but the approach was wrong from the start because there's no established pattern for this task type. The error is discovered late (or not at all).

Detecting novelty *before* execution changes the failure mode from silent wrong-output to explicit "this is new territory" — enabling the user to add context or Shadow to surface its uncertainty before committing.

## Precondition

Before executing a task, Shadow must check:
1. Scan `harness/skills/*.md` filenames and first-line role descriptions for domain match
2. Run `git log --oneline -50` and scan for ≥2 commits with overlapping keywords

If both checks return no match: echo interpretation + flag novelty in the first response:
> "No skill pattern or precedent for [task type]. Proceeding with [approach] — flag if this diverges from expected."

## Enforcement

Harness-side. Does NOT block execution — flags and narrates. The goal is traceability, not paralysis.

Violation: executing a novel task with full confidence and no novelty flag.

## Recovery

1. If a novel task failed silently: post-mortem notes what the missing pattern was
2. If the user provides the correct approach: write a skill file so the next occurrence is no longer novel

## Interaction with existing contracts
- Complements `pre-denial-gate`: that contract prevents false denials; this one prevents false confidence
- Complements `interpretation-echo` (FM-032): both require surfacing interpretation before acting on ambiguous inputs
- When a novel task succeeds, the output becomes a candidate for `harness/skills/` — new skill extraction is the positive outcome

## Origin
May 2026: Research on agentic failure modes ("Autonomous Operations & Agentic AI"). Key finding from skeptical literature (LeCun, Marcus): agentic systems autocomplete action sequences that *look* planned but fail on out-of-distribution inputs. Flagging novelty before execution is the minimum viable defense.