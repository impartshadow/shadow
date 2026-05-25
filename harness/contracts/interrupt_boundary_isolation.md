# Contract: interrupt-boundary-isolation

**Type:** harness-enforced gate
**Trigger:** a new the user instruction arrives while `state/active_threads.json` has at least one open thread tagged `loop` or `pipeline`
**Failure mode:** FM-011 (scope overrun / objective displacement)

## What it prevents

When the user sends a new instruction mid-loop (e.g., "stop the research loop and fix the auth bug"), Shadow's default is to switch contexts immediately. The prior loop's:
- current step
- accumulated findings
- last verified checkpoint

...get silently dropped from working context. On resumption, Shadow restarts from scratch rather than picking up at the interrupt point. This is the agentic analogue of Bellman-backup contamination across macro-action boundaries: the new objective's signal bleeds into and overwrites the prior objective's progress state.

## Precondition

Before executing the new instruction, Shadow MUST:
1. Write a one-line snapshot to `session_handoff.md` under a `## Interrupted Loops` section:
   ```
   - [loop name] interrupted at step [N] — [brief state summary] — resume pending
   ```
2. Note the last verified checkpoint (the last commit or output produced by the loop).
3. Only then switch to the new instruction.

## Postcondition

When the interrupting instruction is complete, Shadow checks `## Interrupted Loops` in `session_handoff.md` and either:
- Resumes from the noted checkpoint, OR
- Explicitly closes the loop entry with a reason ("abandoned — superseded by X")

Do NOT leave stale `## Interrupted Loops` entries that are neither resumed nor closed.

## Enforcement

Harness-enforced (convention). `active_threads.json` + `step_state_tracking` contract provide the mechanism; this contract defines the interrupt protocol.

## Recovery

If Shadow switched contexts without snapshotting:
1. Re-read the last 5 commits touching the interrupted pipeline/script
2. Reconstruct the step state from git history and tool call log
3. Write the `## Interrupted Loops` entry retroactively before proceeding

## Origin

2026-05-14: MAVIC (arXiv cs.AI) — *Macro-Action Value Correction for Instruction Compliance* — formalizes the bootstrapping-target corruption that occurs when external instructions interrupt ongoing macro-actions in multi-agent systems. The theoretical fix is explicit boundary handling that cancels the incoming instruction's value contribution until handoff is complete. Shadow's implementation is the objective-snapshot pattern above: explicit checkpoint write before context switch.

## Escalation

If the interrupted loop has been stale in `session_handoff.md` for >2 sessions, surface to the user: "[loop] has been paused since [date] — close it or schedule resumption?"
