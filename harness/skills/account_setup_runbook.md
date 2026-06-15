# Skill: Account Setup Runbook

## Overview

Account-creation and credential-setup flows (Coinbase, Stripe, Twilio, GitHub second account, Substack second account, X second account) routinely span multiple sessions: the user supplies a phone, hits 2FA, gets a code, the code expires before Shadow uses it, Shadow retries, hits a rate-limit, asks the user for a fresh code, etc. Each retry loses context. Shadow then resurfaces the same hand-off requests the user already answered.

This skill defines a per-account runbook structure that survives the full setup arc — across sessions, across restarts, across retries — and surfaces the next exact human action without re-asking.

Backlog origin: `20260614T075704_interaction_theme_an_915a` (Coinbase/CDP friction, 2026-06-14).
Related: `harness/skills/verification_state_tracking.md` (per-flow code/expiry tracking — sub-component of this skill).

## When to use

Trigger this skill on the first turn that does any of:

- the user says "set up an account" / "create a [service] account" / "register for X"
- Shadow initiates an account/credential setup autonomously (e.g., new freelancing platform, new payment processor)
- A verification-state flow in `state/verification_flows.json` reaches `stage=complete` for the first credential of a new service

Continue using until the runbook reaches `status=complete` with `credentials_in_bitwarden=true`.

## State shape

One entry per service in `state/account_runbooks.json`:

```json
{
  "service": "coinbase",
  "purpose": "CDP API for autonomous payouts",
  "status": "in_progress",           // pending | in_progress | complete | blocked
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "current_stage": "phone_verification",
  "next_action": {
    "actor": "shadow",                // shadow | will | external_provider
    "instruction": "Wait for SMS code, then submit via verification_flows",
    "expected_input": null,
    "deadline_utc": "ISO-8601 or null"
  },
  "inputs_received": {
    "email": "stored_in_bitwarden",
    "phone": "+1*** stored",
    "verification_code": "via verification_flows entry coinbase_cdp_2026-06-14T01:22"
  },
  "inputs_pending": ["2fa_backup_codes"],
  "credentials_in_bitwarden": false,
  "bitwarden_entry_name": null,
  "rate_limit_windows": {"sms_per_hour": 5, "sms_per_day": 10},
  "blockers": [],
  "history": [
    {"ts": "ISO-8601", "stage": "email_signup", "action": "submitted email", "result": "ok"},
    {"ts": "ISO-8601", "stage": "phone_verification", "action": "submitted code", "result": "rate_limited"}
  ]
}
```

Use `core/state_io.py` for reads/writes.

## Flow lifecycle

1. **Triage**: First mention of a service setup → check `state/account_runbooks.json` for an existing entry. If none, create one with `status=pending`, capture `purpose` and an explicit `next_action`.
2. **Pre-flight before any human ask**: Load the runbook, check `next_action.actor`. If `actor=will`, the existing `inputs_pending` IS the question — do not re-ask differently. If `actor=shadow`, do the work.
3. **Per attempt**: Append to `history` with `ts`, `stage`, `action`, `result`. This is the audit trail that prevents Shadow from re-asking what the user already answered.
4. **On credential acquisition**: Save to Bitwarden in the same turn (CLAUDE.md rule #31), set `credentials_in_bitwarden=true`, record `bitwarden_entry_name`.
5. **On completion**: Set `status=complete`, write a one-line receipt to `#shadow-log`: `✅ account-setup · <service> · credentials in bitwarden as <entry_name>`.
6. **On hard block**: Set `status=blocked`, list the blocker in `blockers`. Surface to the user ONLY if it qualifies under the standing-authority blocker allowlist (auth requiring the user's hands, money beyond $20/mo, legal/compliance, or irreversible high-blast-radius action).

## Hard stops

1. **No re-ask of an already-answered input** — if `inputs_received` has the field the user is being asked about, look there first.
2. **Rate-limit gates** — respect `rate_limit_windows`. If `history` shows 3+ failures within the window, HALT and tell the user.
3. **No autonomous account creation for services that bill** — accounts that immediately attach billing must surface to the user under standing-authority rule #2 (money beyond infra line).

## Why this exists

The Coinbase CDP setup on 2026-06-14 spanned ~6 turns asking for the same phone number and code, hitting rate-limits, and bouncing back to the user twice. The fix is a durable per-account state file, not chat memory.

## Reference

- Memory: `feedback_bitwarden_autosave.md` (CLAUDE.md rule #31)
- Memory: `reference_capability_inventory.md` (visual-CAPTCHA blockers)
- Skill: `harness/skills/verification_state_tracking.md` (per-code state — sub-component)
- Contract: `platform-action-precheck` (pre-flight for browser actions)
