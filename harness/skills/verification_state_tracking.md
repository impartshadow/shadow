# Skill: Verification State Tracking (Browser/Account Flows)

## Overview

Multi-step verification flows (Coinbase, Stripe, X login, Substack auth, Gmail OAuth) regularly fail mid-flow because Shadow loses track of:
- The phone number or email the user provided
- The latest verification code the user sent
- The expiry/window for that code
- The current attempt count and cooldown ceiling
- Whether retrying will trigger a rate-limit lockout

When this state is lost, Shadow asks the user to recover the flow manually — exactly the gap-catcher role the user is fatigued by.

This skill defines the required state shape and the hard stops that prevent rate-limit lockouts.

Backlog origin: `20260614T075830_daily_friction_fixer_e57c` (Coinbase CDP verification, 2026-06-14).

## When to use

Triggered when any of these are true in a single conversational turn:
- the user supplies a phone number, email, or address for an account setup
- the user pastes a 4–8-digit code (or anything matching `^\d{4,8}$`)
- A browser-automation flow requests a verification code or 2FA challenge
- Shadow initiates an account creation or password reset on the user's behalf

## State shape

A single `state/verification_flows.json` entry per active flow:

```json
{
  "flow_id": "coinbase_cdp_2026-06-14T01:22",
  "service": "coinbase",
  "stage": "phone_verification",
  "contact": {"type": "phone", "value": "+1*********", "supplied_at": "ISO-8601"},
  "latest_code": {"value": "******", "received_at": "ISO-8601", "expires_at": "ISO-8601 (typically +10min)"},
  "attempt_count": 0,
  "cooldown_until": null,
  "rate_limit_window": {"max_per_hour": 5, "max_per_day": 10},
  "blockers": [],
  "next_action": "submit code to coinbase.com/verify"
}
```

Use `core/state_io.py` for reads/writes — never write a raw file. Field rules:

- `latest_code.expires_at`: default `received_at + 10min` if the provider doesn't specify
- `attempt_count`: increment on every submission, success or failure
- `cooldown_until`: set on any 429/rate-limit response; flow must HALT until past this
- `next_action`: must be a single concrete sentence — "submit X to Y" — never vague

## Hard stops (do not bypass)

1. **Code expiry** — if `now > latest_code.expires_at`, do NOT retry the code. Ask the user for a fresh one (this is a legitimate hard blocker per the auth-requiring-the user's-hands rule).
2. **Rate-limit ceiling** — if `attempt_count >= 3` AND `cooldown_until` is null, HALT and tell the user. Three failed attempts is the universal soft-lockout threshold across Coinbase, Stripe, Twilio, Google.
3. **No code on file** — if `latest_code.value` is null but the flow is at `stage=submit_code`, HALT. Do not invent a code, do not "try the most recent code the user sent" without confirming it matches `flow_id`.

## Flow lifecycle

1. **Triage**: First mention of a verification challenge → create the flow entry, capture `contact` and `service`.
2. **Receive code**: the user pastes a digit string → update `latest_code` with `received_at` and computed `expires_at`. NEVER submit without first writing this.
3. **Submit**: Increment `attempt_count`, post the code, capture the result.
4. **On success**: Mark `stage=complete`, clear `latest_code.value`, persist.
5. **On failure**: Check expiry, then rate-limit ceiling, then either retry or HALT.
6. **On rate-limit**: Set `cooldown_until` from the response header (or +1h if absent). HALT.

## Why this exists

The Coinbase CDP setup on 2026-06-14T01:22 lost track of which phone code was current after the user sent two in quick succession. Shadow submitted the older code, hit a rate-limit, then asked the user to "send a new code" — which the user had already done. The fix is structural state, not memory.

## Reference

- Memory: `feedback_auth_failure_diagnosis.md` (check cookie mtimes first)
- Memory: `reference_capability_inventory.md` (known visual-CAPTCHA blockers)
- Contract: `platform-action-precheck` (pre-flight for browser actions)
