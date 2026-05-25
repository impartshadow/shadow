# Contract: episodic-capture-gate

**Type:** Harness (soft enforcement)
**Failure mode:** FM-003 (loop / stale-state accumulation via indiscriminate memory writes)

## Trigger

Any impulse to write a NEW `memory/*.md` file (not an update to an existing one).

## Precondition

The fact being promoted has not previously appeared in `memory/session_handoff.md` or a prior session's handoff.

## Rule

Facts MUST pass through the episodic tier before reaching semantic memory (`memory/*.md`):

1. **Episodic capture first** — the fact must have appeared in `memory/session_handoff.md` in a prior session OR be explicitly confirmed by the user this session. Raw mid-session inferences do not qualify.
2. **Score before promoting** — apply the five-signal model from `harness/contracts/memory_importance_weighting.md`. Composite score < 7 = defer, not write.
3. **One write per trigger** — a single impulse should produce at most one new memory file. Batch writes are a sign that episodic capture was skipped.

### What bypasses this gate

- the user explicitly asks Shadow to remember something (direct authority overrides score threshold)
- Correcting a demonstrably wrong existing memory (uncertain correction beats stale wrong fact)
- `feedback_*` memories generated from an explicit correction in the current session

## Why

MEMTIER (2026) attributes 14pp tool-execution degradation in long-running agents to flat-file memory growth — every session artifact landing directly in the semantic tier adds retrieval noise. The episodic→semantic discipline (capture raw, promote selectively) is the load-bearing architectural fix. Shadow's equivalent: session_handoff.md is the episodic buffer; memory/*.md files are the semantic tier. The gate prevents direct-to-semantic writes that bypass the buffer.

## Enforcement

Harness (manual discipline). Shadow self-enforces before every new memory file write.

## Recovery

If a write impulse fires without episodic basis: add the fact to `session_handoff.md` this session, then re-evaluate after the next session confirms the signal persists.

## Escalation

Never surface to the user.
