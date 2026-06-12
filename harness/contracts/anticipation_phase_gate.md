---
name: anticipation-phase-gate
failure_mode: FM-031
type: pre-check
severity: warn
enforcement: core/contracts.py — AnticipationPhaseGate
---

## Purpose

Before an irreversible high-stakes tool call commits, the execution loop must
record a **forward-simulation preamble** that names:

1. Predicted post-action state
2. Confidence level (high / medium / low)
3. Rollback path if the prediction is wrong

This gives the loop a moment to surface hidden assumptions and prevents
"commit first, notice problem second" failure sequences.

## Trigger

Fires on `check_pre` when `ctx.action` is one of:

- `git_push`
- `send_email`
- `post_discord`
- `publish`
- `archive_emails`
- `delete_file`

## Precondition

`ctx.anticipation_preamble` (or `ctx.action_params["anticipation_preamble"]`)
must be present and at least 30 characters long.

**Autonomous skip:** if `ctx.user_message` is empty (cron-driven scripts,
heartbeat, idle moonshot pushing without a the user turn), the gate is bypassed.
The contract exists to make *the user-initiated* irreversible actions pause; it
should not spam the log for scheduled jobs. Tightened 2026-06-11 after 38
autonomous fires/24h.

## Enforcement

`AnticipationPhaseGate.check_pre()` in `core/contracts.py`.
Deterministic — no LLM calls.  Fail-open (warn, not block) at launch.

## Recovery

Set `ctx.anticipation_preamble` to a one-sentence prediction covering
the three required components, then re-run the pre-check.

Example:

> "Branch moonshot-55 will be updated with the new FM-031 contract;
>  confidence high; rollback via `git revert` if tests regress."

## Escalation

No escalation required — violation is warn-only.  If fires repeatedly on
legitimate fast-path actions (e.g. trivial file deletes), raise `_MIN_PREAMBLE_LENGTH`
threshold or extend the `_HIGH_STAKES_ACTIONS` exclusion list.
