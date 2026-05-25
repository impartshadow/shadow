# Contract: memory-write-checkpoints

**Type:** Harness (soft enforcement — code gate tracked as future work)
**Failure mode:** FM-003 (loop / stale-state accumulation)

## Trigger

Any Write or Edit call targeting `memory/session_handoff.md`.

## Precondition

The write is happening mid-response — before a `git push` has been issued or before the session-close sequence has begun.

## Rule

`session_handoff.md` is a lifecycle checkpoint file. It MUST only be written at two defined points:

1. **Post-push checkpoint** — immediately after `git push origin main` completes.
2. **Session-end checkpoint** — when the user signals the session is closing or context is about to compact.

Never write `session_handoff.md` mid-response to capture an in-flight thought or intermediate state. If insight emerges mid-response, note it in the response text; defer the actual file write until the push or session-end.

**Other memory/*.md files** are less constrained but should still be batched to the end of the current turn — complete the response, then write. Never interleave memory writes with tool calls serving the primary task.

## Why

Inlining memory writes with response generation creates two problems: (1) it blocks response delivery while the write round-trips, and (2) it produces partial/racing state when a long turn generates multiple partial insights. Post-turn extraction (Invincat's `aafter_agent` pattern) avoids both.

## Enforcement

Harness (manual discipline). Shadow self-enforces. A code gate (`MemoryWriteCheckpoint` in `core/contracts.py`) is tracked as Tier 2 future work.

## Recovery

If mid-response handoff write impulse fires: finish the primary task first. Add handoff update to the end of the turn or after the next push.

## Escalation

Never surface to the user. This is internal write discipline.
