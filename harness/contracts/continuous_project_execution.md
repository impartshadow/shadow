# Continuous Project Execution Contract

## Enforcement

Runtime: `core/project_lifecycle.py` (state, prompt block, completion violation)
Wiring:  `core/discord_bot.py` (`begin_or_resume`, `observe_tool`,
`completion_violation`, `complete_if_ready`)
Tests:   `tests/test_project_lifecycle.py`, `tests/test_discord_bot.py`

## Trigger

the user initiates implementation or says `go`, `fix it`, `keep going`, `do the
full path`, or an equivalent continuation directive within an active project.

## Required lifecycle

1. Recover the concrete project scope from the current thread and durable state.
2. Inspect the complete affected surface, including parallel entrypoints.
3. Implement the root-cause fix and wire it into the production path.
4. Add regression coverage and run proportionate verification.
5. Commit and push passing changes.
6. If runtime files changed, queue the restart after commit/push.
7. Resume after restart from the durable checkpoint and verify live behavior.
8. Reconcile the original request against the completion checklist.
9. Report the operating state, receipts, and only hard blockers.

## Progress contract

Post concise Discord updates at meaningful checkpoints: investigation resolved,
implementation integrated, tests passing, commit/push complete, restart queued,
post-restart verification complete. Do not require the user to ask for status.

## Failure condition

Shadow reports a component-level success plus a known in-scope gap, then stops
and waits for another `go` despite having authority to continue.

## Exceptions

Pause only for a hard blocker in the canonical allowlist or when the next action
would materially expand beyond the project the user initiated.

## Completion receipt

Completion requires evidence for implementation, integration, tests, pushed
state, and live runtime behavior when a restart/deploy was necessary. A restart
is a checkpoint, not completion.
