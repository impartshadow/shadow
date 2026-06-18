# Contract: brief-production-while-queued

## Type
Pre-action guard — deterministic enforcement via
`core/contracts.py:BriefProductionWhileQueuedGuard.check_pre()`.
Severity: `block`.

## Failure mode
FM-033 — recurrence of a behavior the user has explicitly stopped.
Specifically: CLAUDE.md rule #17 ("Distribution before production"):
when briefs are queued in `state/research/queue.json` or
`state/ai_digest_pending.json`, Shadow's default work is
*distribution* (fix delivery, ship existing briefs), NOT producing
more briefs.

## Trigger
Pre-check on Bash / `mcp__shadow__run_shell` / `run_shell` tool
calls. The regex `_PRODUCTION_SCRIPT_RE` matches commands that
invoke one of:

- `research_produce.py`
- `lead_magnet_brief.py`
- `brief_voice_pass.py`
- `brief_outreach.py`

If the command matches AND
`state/research/queue.json` has at least one entry with
`status == "queued"`, the contract fires `block`.

## Recovery
The violation message tells the model exactly how many unsent
briefs are already queued and points at distribution scripts
(`scripts/substack_publish.py`, `scripts/echo_publish.py`,
`scripts/brief_outcome_scorer.py`) that should be run instead.
Resume production only after the queue is drained.

## Why this contract exists
PersistentCorrectionGuard catches the pattern post-hoc at
confidence 1.00 — but by then the response (and often the side-
effect) is already produced. the user then has to re-type the
correction. Three the user-corrections logged in the last 30 days
(2026-05-14, 2026-06-03, 2026-06-17). Pre-blocking the tool call
moves enforcement upstream of the response.

## Tests
`tests/test_contracts.py::TestBriefProductionWhileQueuedGuard`.

## History
- 2026-06-17: Initial implementation. Gap-closer after
  persistent-correction fired twice in 4h with directive
  "Stop producing briefs" / "you keep producing briefs. Why are
  you not working on distribution?".
