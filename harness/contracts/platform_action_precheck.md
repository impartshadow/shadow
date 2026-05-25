# platform-action-precheck

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-012 (unauthorized platform action)
**Trigger:** Discord post, calendar event, or publish operation

**Precondition:** Action must be within standing authority (see `state/mandate.md`). Recipient/channel must be appropriate for content.

**Enforcement:** `core/contracts.py:PlatformActionPrecheck.check_pre()` — validates channel routing and content type before platform actions.

**Recovery:** Route to correct channel. Check standing authority before taking action.

**Escalation:** Surface to the user for any platform action that isn't covered by standing authority.
