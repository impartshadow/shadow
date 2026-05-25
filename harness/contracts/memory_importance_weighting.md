# memory-importance-weighting

**Type:** Harness (soft enforcement, no code gate)
**Trigger:** Before writing or updating `memory/session_handoff.md`
**FM:** FM-003 (loop / stale-state accumulation)

## Precondition

Handoff entries age. Stale low-impact facts consume space that could be used by high-signal recent context.

## Rule

When updating `memory/session_handoff.md`, apply importance weighting:

| Category | Keep full | Summarize | Drop |
|---|---|---|---|
| **Recent** (≤3 sessions ago) | Always | — | — |
| **High-impact** (standing decisions, the user-confirmed next steps) | Always | — | — |
| **Medium** (in-progress threads, open questions) | If < 2 weeks stale | If 2–4 weeks | If > 4 weeks |
| **Low** (one-off context, resolved issues) | — | If < 1 week | If > 1 week |

## Retrieval priority scoring (five-signal model)

When deciding which memory files to surface in context or which episodic facts to promote to `memory/`, score each candidate on all five signals. Higher composite score = higher priority for retention and retrieval.

| Signal | High (2 pts) | Medium (1 pt) | Low (0 pts) |
|---|---|---|---|
| **Recency** | Written/accessed < 7 days | 7–30 days | > 30 days |
| **Relevance** | Directly names current task/person | Adjacent domain | Unrelated |
| **Confidence** | `high` (the user-stated or firsthand) | `medium` (inferred) | `low` (single signal) |
| **Source authority** | the user's direct statement | Shadow's observation | External/inferred |
| **Access frequency** | Referenced 3+ times across sessions | Referenced 1–2 times | Never referenced after write |

**Score ≥ 8**: always surface, never drop  
**Score 5–7**: surface if relevant to current task  
**Score < 5**: candidate for consolidation or drop at next handoff write

This model applies to:
1. Handoff pruning decisions (which entries to summarize or drop)
2. Episodic promotion decisions (which session events earn a `memory/*.md` write)
3. Synthesized topic prioritization in `memory/synthesized/`

## Enforcement

Harness (manual discipline). Shadow self-applies on every handoff write.

## Recovery

If handoff exceeds ~80 lines: scan for entries matching Drop criteria and remove or summarize before committing.

## Escalation

Never escalate. This is routine maintenance, not a the user decision.

## Rationale

Inspired by MEMTIER (2026): tiered agent memory with PPO-tuned five-signal retrieval achieves 7.6x recall improvement over flat-file baselines on LongMemEval-S. Shadow's original contract used recency+category only; the five-signal extension captures the same dimensions MEMTIER identifies as load-bearing. The async consolidation daemon pattern (episodic→semantic promotion without blocking the main loop) maps directly onto Shadow's idle_moonshot.py architecture.
