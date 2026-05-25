# Contract: capability-misroute

## Type
Post-response gate — deterministic enforcement via `core/contracts.py`

## Trigger
Any response that mentions WebFetch, WebSearch, or claims web fetching/browsing
is blocked, needs permission, or is unavailable.

## Precondition
Shadow ALWAYS has web access via:
- `mcp__shadow__browse_url` — fetch any URL
- `mcp__shadow__web_search` — search the web

These are MCP tools that bypass all permission prompts. They always work.

## What this catches (FM-004 sub-patterns)
1. **Wrong tool name in response** — mentioning "WebFetch" or "WebSearch" at all
2. **Permission theater** — "I need WebFetch permission", "Could you grant access"
3. **False denial** — "Can't fetch the article", "It's being blocked" without
   having tried `mcp__shadow__browse_url`
4. **Delegation of capability** — asking the user to do something Shadow can do itself

## Enforcement
**Code-enforced** in `core/contracts.py:CapabilityMisroute`:
- Regex scan on response text for wrong tool names and denial patterns
- Only allows denial if response contains actual MCP tool error output
- Severity: **block**

## Violation recovery
1. Remove all references to WebFetch/WebSearch
2. Call `mcp__shadow__browse_url` with the URL
3. Show the result
4. Only claim failure if the MCP tool itself returns an error

## Escalation
If `mcp__shadow__browse_url` genuinely fails, show the error output and say:
"browse_url failed — here's the error: [output]. Alternative approaches: ..."
