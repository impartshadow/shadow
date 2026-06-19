# Contract: gmail-tool-guard

## Type
Pre-check (blocks before action)

## Trigger
Any tool call whose name matches `mcp__claude_ai_Gmail__*`

## Failure mode
FM-004 — wrong tool routing

## What it prevents
Using the Claude.ai Gmail MCP integration (`mcp__claude_ai_Gmail__*` tools). These tools have read-only scope and cause account routing confusion between [private-email] and [public-contact-email]. The canonical path for all Gmail operations is `gmail_manage.py` / `gmail_summary.py` via `mcp__shadow__run_shell`.

## Enforcement
Code-enforced in `core/contracts.py::GmailToolGuard`. Fires pre-action and blocks the call.

## Recovery
Route to `scripts/gmail_manage.py` or `scripts/gmail_summary.py` via shell. Specify the account explicitly (`--account shadow` or `--account personal`).

## Escalation
None — this is a deterministic routing error with a clear canonical path. No the user escalation needed.

## CLAUDE.md rule
Rule 11: "NEVER use `mcp__claude_ai_Gmail__*` tools — they have read-only scope and cause account routing confusion."
