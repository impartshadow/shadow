# Contract: evidence-chain

## Type
Post-action audit logging — behavioral enforcement via `session_audit.py`. Severity: `warn` (non-blocking).

## Trigger
Any high-stakes mutation completes within a session:
- `git push` to any branch
- Email send via `gmail_manage.py` or any send_email tool call
- Shell write to a path containing credential material (`state/*.txt` key files, `state/*.json` auth blobs, `.netrc`-adjacent)

## Purpose
Maintain an append-only audit log (`state/evidence_chain.jsonl`) so that any authorization
decision can be reconstructed independently of the session transcript. Motivated by
proof-derived authorization research: ephemeral intent + action + outcome must be
traceable even after the conversation context is cleared.

This is an *audit trail*, not a gate. The Tier 2 upgrade path is a `CredentialPathIntentGuard`
pre-check in `core/contracts.py` that requires a justification string before execution.

## Record schema

Each line in `state/evidence_chain.jsonl` is a JSON object:

```
{
  "ts":            "ISO-8601 UTC timestamp",
  "action":        "git_push | email_send | credential_write",
  "summary":       "what was pushed/sent/written (<=120 chars)",
  "session":       "session_id or 'unknown'"
}
```

## Enforcement
`scripts/session_audit.py` — `_extract_high_stakes_actions()` reads `state/trace.jsonl`
for push/email events; `_append_evidence_chain()` writes records at session close.
See implementation notes in `session_audit.py`.

## Violation recovery
If `state/evidence_chain.jsonl` is missing records for a session with known git pushes:
```
python3 scripts/session_audit.py --evidence-only
```

## Escalation
Surface to the user if evidence chain shows > 3 credential-path writes in a single session
with no corresponding justification strings in trace.jsonl.

## Origin
- 2026-05-18: Motivated by arXiv paper "Verifiable Agentic Infrastructure: Proof-Derived
  Authorization for Sovereign AI Systems" — Shadow Gaps section identified missing evidence
  chain for git push and email sends.
