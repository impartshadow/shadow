# Contract: ghost-profile-pre-check

**Type:** Pre-check (Haiku-judged)
**Failure mode:** FM-022
**Status:** Proposed — see Tier 2 implementation item

## Purpose

Before Shadow takes a consequential action (git push, email send, Discord post, publish), simulate Shadow's stated personality and priors to verify the planned action is consistent with who Shadow is.

Motivated by the Ghost Profile Agent pattern (ECIS 2026): an agent that simulates a specific user/entity's perspective before committing to an action, catching out-of-character behavior before it fires rather than after.

## Trigger

Actions: `git_push`, `send_email`, `discord_post`, `publish`, `calendar_create`

## Precondition

The planned action and response text must be consistent with Shadow's documented personality:
- Default-to-action (not proposal)
- Concise, direct communication
- No unnecessary hedging
- the user-aligned priorities

## Enforcement

Haiku is prompted with Shadow's personality summary and the planned action. If confidence ≥ 0.75 that the action is out-of-character, emit a warn-severity Violation.

## Recovery

Log the inconsistency to `state/mind.md`. Proceed unless severity is `block`.

## Escalation

If the same action type fires this contract 3+ times in a session, surface to the user via `#shadow-log`.

## Relationship to existing contracts

- `behavioral-haiku-guard` — post-check sibling; this contract fires pre-action
