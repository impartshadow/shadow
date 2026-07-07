# Contract: slot-collection-gate

**Type:** Pre-check (code-enforced in `core/contracts.py`)
**Failure mode:** FM-012 (platform action without pre-flight)
**Class:** `WriteActionSlotGuard`

## Trigger
Fires before any tool call that performs a write action on an external system:
- `mcp__claude_ai_Google_Calendar__create_event`
- `mcp__claude_ai_Google_Calendar__update_event`
- `mcp__claude_ai_Gmail__create_draft` (when `send=true` or follow-on send tool fires)
- Echo publish calls (`scripts/echo_publish.py`, `echo/twitter.py`, browser X post)

## Precondition
All required slots for the target action must be present in `ctx.tool_params` for the pending tool call. Missing or empty slots block execution.

### Required slots by action type

| Action | Required slots |
|---|---|
| Calendar create/update | `summary` (non-empty), `start.dateTime` or `start.date`, `end.dateTime` or `end.date` |
| Email send | `to` (non-empty list), `subject` (non-empty) |
| Echo publish | `content` or `status` (non-empty, ≥ 10 chars) |

## Enforcement
Code-enforced. `WriteActionSlotGuard.check_pre()` in `core/contracts.py` inspects `ctx.tool_calls` and `ctx.tool_params` for the pending write-action tool. If a matching tool is found with a missing required slot, returns a `block`-severity Violation.

## Recovery
Collect the missing slot value explicitly from context or ask. Do not infer title from ambiguous context. Do not default dates to "now" without confirmation.

## Escalation
None — surface as a pre-check block with the specific missing slot(s) listed.

## Motivation
AI-Care (arXiv 2025, cs.AI) demonstrates that LangGraph-based agentic systems with explicit sanitize → classify → collect-slots → execute pipelines eliminate the class of write-action errors caused by parameter inference from ambiguous context. The pattern is "deployable" not just architectural. Shadow's current `PlatformActionPreCheck` validates action intent but does not inspect parameter completeness.
