# Contract: pre-denial-gate

## Type
Pre-response gate — deterministic enforcement via `core/contracts.py`

## Trigger
Any response containing denial phrases: "can't access", "don't have access",
"unavailable", "not possible", "I can't".

Also triggers on **tool-call omission phrases** — hedges that imply a tool is needed
but the tool is never called:
"I'd need to check", "I would need to look", "I'd have to browse", "I need to verify",
"I'd need to search", "I would need to fetch", "let me know and I'll check"
— when no corresponding tool call is present in the same response turn.

Also triggers on **manual-delegation phrases** — asking the user to do retrievable work:
"Could you paste", "Can you paste", "could you run and paste", "can you share the output"
— these are the same failure mode: Shadow should run the command itself.

## Precondition
Before ANY denial response, ALL of the following must be true:
1. Checked `memory/reference_capability_inventory.md`
2. Tried every listed path for that resource
3. Ran a smoke test — actually executed a command to confirm access is broken

Before ANY tool-call omission response, the following must be true:
1. The tool implied by the hedge has been attempted in the same turn
2. If the tool call failed, the error output is shown

## Enforcement
**Code-enforced** in `core/contracts.py:PreDenialGate` — scans outgoing
responses for denial phrases and flags violations when no smoke test output
is present in the conversation context.

**Code-enforced** in `core/contracts.py:CognitionActionMismatch` (Tier 2, pending) —
scans for tool-call omission phrases when no tool call is present in `ctx.tool_calls`.
Until that contract lands, treat violations manually: if you wrote "I'd need to check X",
stop, call the tool, and replace the hedge with the result.

## Known paths that have been denied then proven working

| "I can't..." | Actually can — try this |
|---|---|
| Access impartshadow Gmail | `python3 -c "from scripts.gmail_utils import get_gmail_service; svc=get_gmail_service(); msgs=svc.users().messages().list(userId='me',maxResults=5).execute(); print(msgs)"` |
| Moltbook auth failure | Run `curl -s -o /dev/null -w "%{http_code}" <moltbook-health-url>` first — 401 = expired token, 500 = server incident; do not report "expired token" without confirming HTTP status |
| See images the user sent | `ls -t state/photos/ \| head -5` then Read the file |
| Browse a webpage | `mcp__shadow__browse_url` — NOT WebFetch |
| Search the web | `mcp__shadow__web_search` — NOT WebSearch |
| Find Telegram context | Check `state/recent_context.json`, `state/research_log.json`, `state/history.json` |
| Read tweets / X posts | `mcp__shadow__browse_url` with the x.com URL |

## Known tool-call omission phrases to never emit without acting

| Omission phrase | Required action |
|---|---|
| "I'd need to check X" | Call the tool that checks X, paste the result |
| "I would need to browse" | Call `mcp__shadow__browse_url` immediately |
| "I'd need to search for" | Call `mcp__shadow__web_search` immediately |
| "I need to verify" | Run verification — don't describe needing to run it |
| "let me know and I'll look into" | Look into it now; don't defer to a future turn |
| "Could you paste / Can you paste" | Run the command yourself and show the output |

## Violation recovery
Block the denial or omission. Run the smoke test or tool call. Show the output. Then decide.

## Escalation
If all listed paths genuinely fail, include the error output and say:
"All paths failed — here's what I tried: [output]"
