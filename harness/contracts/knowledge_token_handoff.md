# Contract: knowledge-token-handoff

**Type:** convention (harness-enforced at session close)
**Trigger:** session end / post-push handoff update
**Failure mode:** FM-022 (self-consistency — next session contradicts findings from this one)

## What it requires

Every `session_handoff.md` update MUST include a `## Signal Summary` section populated with up to 3 knowledge tokens. Each token encodes what was learned this session in a form the next session can act on without re-reading.

## Signal Summary format

```markdown
## Signal Summary

| Direction | Finding | Confidence |
|---|---|---|
| PURSUE | <concrete next action or confirmed-working approach> | high/medium/low |
| AVOID | <approach that failed or was ruled out this session> | high/medium/low |
| WATCH | <open question or unverified assumption requiring monitoring> | high/medium/low |
```

**Rules:**
- Maximum 3 rows. If you have more findings, keep only the highest-confidence ones.
- Direction must be one of: `PURSUE`, `AVOID`, `WATCH`.
- Finding must be action-oriented (start with a verb or noun phrase), not a description of what happened.
- Confidence reflects how certain you are the signal generalizes beyond this session.
- Do NOT duplicate information already in "Up next" or "Open threads" — signal summary is for *strategic* signal, not task lists.

## Precondition

At session close, session_handoff.md contains a Signal Summary block with at least 1 row.

## Post-condition

At session open, the next session reads Signal Summary before reading any other handoff section. If a user request contradicts a PURSUE or AVOID signal, surface the conflict explicitly before acting.

## Recovery

If no clear signals emerged this session (e.g., pure execution with no learning), write a single WATCH row noting what the next session should verify.

## Enforcement

Convention — enforced by harness training. `core/contracts.py` behavioral-haiku-guard catches responses that contradict prior decisions (FM-022); this contract provides the structured surface that guard reads from.

## Escalation

None — this is a self-consistency aid, not a hard gate.
