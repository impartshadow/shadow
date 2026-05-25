# Skill: prospective_retry

## Role sequence
Triage -> Execute -> Verify

## Purpose
When a task has already failed once in the current session, switch to Prospective mode:
enumerate the top predicted failure points BEFORE re-executing. This prevents repeating
the same failure path and surfaces hidden constraints early.

Directly motivated by SpaceMind's finding that Prospective reasoning uniquely succeeds
where nominal re-execution fails under degraded conditions.

## Trigger conditions
- Same task type has failed or been blocked in this session
- A contract violation fired during the previous attempt
- the user explicitly asks to retry something that errored

## Stage: Triage
1. Identify the failure: what contract fired, what error occurred, what assumption was wrong
2. Check if this failure type is already documented in the relevant skill file
3. If documented: follow the documented recovery path, skip to Execute
4. If undocumented: proceed with Prospective mode below

## Stage: Execute — Prospective mode
1. Before any tool calls, write out the top 3 predicted failure points for this retry:
   - What assumption might still be wrong?
   - What state might not have changed since the last failure?
   - What dependency might not be available?
2. For each predicted failure point, identify the check that would confirm or rule it out
3. Run the checks FIRST — in the order most likely to fail fast
4. Only proceed with the main task action after the checks pass
5. If a check fails: treat it as new signal, update the failure model, re-triage

## Stage: Verify
1. Confirm the task completed successfully (not just that it ran without error)
2. If success: note which predicted failure point, if any, was the actual blocker — distill
   this into the relevant skill file under '## Distilled cautions'
3. If failure again: escalate to the user with the full failure model (what was tried, what failed,
   what the 3 predicted points were, which one was the actual blocker)

## Contracts referenced
- `loop-tripwire` — 3+ retries to the same task = escalate, don't keep trying
- `pre-denial-gate` — exhausting prospective checks does not authorize claiming a capability
  is unavailable; escalate instead
- `fabricated-gap-guard` — predicted failure points must be grounded in observable state,
  not assumptions

## Output format
- Prospective check results: inline before task execution (brief, one line each)
- On success: silent unless distillation produces a new skill update
- On second failure: post to the user with structured failure model
