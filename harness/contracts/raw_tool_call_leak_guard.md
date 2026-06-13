# Contract: raw-tool-call-leak-guard

## Type
Post-response guard — deterministic enforcement via
`core/contracts.py:RawToolCallLeakGuard`. Severity: `block`.

## Trigger
Fires on `action == "respond"` when the response text contains a raw JSON
tool-call blob occupying ≥30% of the text. Three detected shapes:
- `{"tool": "<name>", ...}` with optional args/parameters body
- `{"tool_name": "<name>", ...}` (alternative spelling)
- A pairing of `"tool": "<name>"` with `"args": {...}` within a short window

The ≥30% threshold prevents false positives on prose that mentions tool-call
shape as a teaching example. Real leaks are *the entire payload*.

## Why this exists
**Incident 2026-06-10 01:18:** Shadow emitted
`{"tool": "bash", "args": {...}}` directly to a Discord channel instead of
executing the tools. the user: "What is happening." The upstream cause is the
model occasionally rendering a tool invocation as prose rather than emitting
the actual tool-call token.

`HarnessScaffoldingLeakGuard` catches bracketed markers (`[Executing:]`,
`[Channel:]`) but does **not** match this JSON shape — different surface
form, same class of leak.

Backlog reference: `20260610T081021_daily_friction_fixer_1b57`.

## Precondition
None — the contract is a post-check that runs on every `respond` action.

## Enforcement
Code: `core/contracts.py:RawToolCallLeakGuard.check_post`.
Registered in `_ALL_CONTRACTS` after `HarnessScaffoldingLeakGuard`.

## Recovery
On block: drop the JSON blob and re-emit as either the executed tool's
output or a plain-text summary of what was done. If the intent was to
invoke a tool, retry with the actual tool call, not a JSON description.

## Escalation
None — autonomous block + regenerate. No the user-facing surfacing.

## Tests
`tests/test_contracts.py:TestRawToolCallLeakGuard` (7 cases).

## Origin
- 2026-06-10 01:18: raw blob leaked to channel (the user: "What is happening")
- 2026-06-13: contract added under backlog 1b57 during gap-closure pass
