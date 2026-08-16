# web-tool-guard

**Type:** Post-check (code-enforced, blocking)
**Failure mode:** FM-004 (ungrounded web capability denial)
**Trigger:** Every response

**Precondition:** A response must not deny web capability without attempting the canonical web tool, or share a product URL without fetching it live.

**Enforcement:** `core/contracts.py:WebToolGuard.check_post()` owns denial and live-fetch evidence. `WebToolRewriter` owns legacy tool-call dispatch; `WebToolInvocationRewriter` owns legacy tool names in prose.

**Recovery:** Attempt `mcp__shadow__browse_url` or `mcp__shadow__web_search` before making the claim.

**Escalation:** Not required.
