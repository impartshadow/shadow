# web-tool-rewriter

**Type:** Pre-check (code-enforced, rewriting)
**Failure mode:** FM-004 (wrong tool route)
**Trigger:** WebFetch or WebSearch tool call

**Precondition:** Web access must route through MCP tools, not native Claude Code tools.

**Enforcement:** `core/contracts.py:WebToolRewriter.check_pre()` — intercepts WebFetch/WebSearch calls and rewrites them to `mcp__shadow__browse_url` / `mcp__shadow__web_search` before execution.

**Recovery:** No action needed — rewriter handles it silently. If rewrite fails, use MCP tools directly.

**Escalation:** Not required.
