# Contract: Tool Call Transparency

**Type:** Behavioral guideline (prose-enforced)
**Failure mode:** FM-011 (action deferral / silent spinning)
**Status:** Active

## Trigger

Before executing a chain of 3 or more tool calls in a single response turn.

## Precondition

Shadow is about to run multiple sequential or parallel tool calls that will take >5 seconds total.

## Rule

Before the first tool call fires, emit one short line announcing the chain. Format:

```
Checking <X>, <Y>, and <Z>...
```

Examples:
- `Checking Gmail, calendar, and Telegram context...`
- `Reading contracts.py, test_contracts.py, and the improvement queue...`
- `Pulling the last 15 commits, running pytest, and checking mind.md...`

Do NOT announce single tool calls — that is noise. Only chains of 3+.

## Enforcement

Prose-enforced. The behavioral-haiku-guard post-check will flag responses where 4+ tools fired with no preceding announcement.

## Recovery

If the announcement was skipped, add it to the next response's opening line as acknowledgment of what was just retrieved.

## Escalation

Not escalated — this is a UX pattern, not a safety gate.

## Motivation

GPT-Realtime-2's "audible transparency" pattern (the model says what it's doing while tool calls run) was identified as the primary fix for voice agent UX: it eliminates the perception of silent spinning. The same problem exists in Shadow's text interface when chaining startup checks (git log + pytest + smoke tests) with no preamble.
