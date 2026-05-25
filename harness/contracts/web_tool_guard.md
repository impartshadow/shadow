# web-tool-guard

**Type:** Post-check (code-enforced, warn-only)
**Failure mode:** FM-004 (wrong tool reference)
**Trigger:** Every response

**Precondition:** Response text must not mention WebFetch or WebSearch as tools to use.

**Enforcement:** `core/contracts.py:WebToolGuard.check_post()` — scans response for WebFetch/WebSearch mentions. Warn-only (does not block).

**Recovery:** Replace with `mcp__shadow__browse_url` or `mcp__shadow__web_search` references.

**Escalation:** Not required.
