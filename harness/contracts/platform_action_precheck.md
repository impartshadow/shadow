# platform-action-precheck

## Type
**Code-enforced pre + post check** — `PlatformActionPreCheck` in `core/contracts.py` (FM-012).
Pre-check is `info` severity (advisory steering signal; trajectory event fires
for learning, but ledger write is suppressed so pre-check fires don't inflate
the ≥2/4h recurrence thresholds used by the gap-closer + intraday alarms).
Post-check is `block` severity — this is the actual UI-instruction gate.

## Trigger
**Pre-check:** Fires when the user message references a platform Shadow has tool access to.
Emits an advisory steer naming the canonical tool path so the model routes there directly
instead of describing UI steps.

Detected platforms:
- `discord` → `discord API / bot gateway` (via `core/discord.py` or `mcp__shadow__post_discord`)
- `twitter` / `x.com` / `tweet` → `twitter API / OAuth browser automation via browse_url`
- `google` / `gmail` / `gcal` / `calendar` → `Gmail/Calendar MCP tool / google API client`
- `ios` / `iphone` / `ipad` / `apple` / `shortcuts` → `Shortcuts URL scheme / device MCP tool`

**Post-check:** Fires (block) when the response contains 1+ Class B manual-instruction patterns
(reusing `ManualInstructionGuard._SIGNAL_A_PATTERNS`) and no execution tool was called this turn.

## Precondition
The action must be within standing authority (`state/mandate.md`). For posting actions, the
target channel/recipient must match content type — see `feedback_discord_routing.md`
(`#work=Epic` only, noise→`shadow-log`, user-facing→`shadow-hq`).

## Enforcement
- `core/contracts.py:PlatformActionPreCheck.check_pre()` — pre-check warn (steering signal)
- `core/contracts.py:PlatformActionPreCheck.check_post()` — post-check block
- `tests/test_contracts.py` — see `TestPlatformActionPreCheck` cases

## Carve-outs
The post-check skips a manual-instruction pattern when its containing sentence:
- Uses past-tense self-narration (`I clicked / navigated to / opened …`) — describes prior action
- Cites docs (`the docs say to …`, `per the readme …`) — quoting upstream
- Contains an exempt keyword (`programmatically`, `via the API`, `via MCP`) AND an execution
  tool was actually called this turn
- Documents a failure with evidence (`tried programmatically: … failed because …`) AND a tool
  returned an error in this turn

Discussion-mode responses (`ActionDeferralGuard._DISCUSSION_MARKERS` matches) are fully exempt.

## Recovery
- **Pre-check fire:** Route to the named canonical tool path; do NOT generate UI instructions.
- **Post-check fire:** Rewrite the response. Call the appropriate tool/API first. Manual steps
  may only appear AFTER a documented programmatic failure with error output shown inline.

## Escalation
Surface to the user only when the action falls outside standing authority — e.g., a new paid
integration, a destructive action on a shared channel, or auth requiring his hands
(CAPTCHA / 2FA / account creation). Everything else executes under standing authority.

## Related contracts
- `action_deferral_guard.md` — describes-instead-of-executes pattern (same failure family)
- `api_over_gui.md` — when an API and a GUI path both exist, route to the API
- `digest_channel_routing.md` — channel selection for posting actions
