# interface-representation-gap

**Type:** Diagnostic contract (prose)
**Failure mode:** FM-022 (self-consistency / session drift)
**Status:** Active — observed in improve.py → session_handoff.md → next session pipeline

## Concept

When agents in a pipeline can't share full trajectories (different trust domains, vendor boundaries, or context limits), information is lost at each handoff. This loss is the **interface representation gap** — how much of the upstream agent's state is unrecoverable downstream.

In Shadow's pipeline:
- `improve.py` generates rich contract analysis dicts
- `session_audit.py` compresses to grade + FM scores
- `session_handoff.md` compresses further to bullet points
- Next session receives only the handoff — everything else is gone

The IC-SMDP framework (arXiv 2026) proves this gap is a bottleneck term in the finite-sample convergence bound. Smaller gap = faster policy convergence across sessions.

## Trigger

Any time a multi-step agentic pipeline passes state through `session_handoff.md`, `state/trace.jsonl`, or inter-script dicts.

## Diagnostic

Track `state/handoff_field_history.jsonl` — field count at each session boundary. Degradation signals:
- Field count dropping > 20% between sessions → information loss at boundary
- Field count growing > 60 total → bloat, downstream agent context saturation
- Bottleneck section (most fields) unchanged for 5+ sessions → stale accumulation, not live signal

## Recovery

1. If field count dropped sharply: check what was pruned in the handoff write. Restore high-signal blocks per `handoff_signal_weighting.md`.
2. If field count is bloated: compress routine entries per `handoff_signal_weighting.md` — routine session blocks to one line.
3. If a specific section is a persistent bottleneck: refactor it into a standalone state file that agents read directly, bypassing the handoff boundary.

## Design principle

The handoff is not a complete record — it is a **scalar-per-boundary coordination signal**. It should carry the minimum state needed to resume, not a log of everything that happened. When in doubt: can the next session reconstruct the essential context from this handoff alone? If yes, it's the right size. If it requires reading 10 other files to make sense, it's too compressed. If it's faster to read the handoff than the files it summarizes, it's calibrated correctly.

## Related contracts

- `handoff_signal_weighting.md` — prioritization of high-signal vs routine blocks
- `handoff_integrity_check.md` — schema conformance at pipeline stage boundaries
- `lossless_session_pointer.md` — pointer integrity when handoff references external state
- `session_handoff_append.md` — write discipline for handoff updates

## Research basis

IC-SMDP (Interface-Constrained SMDP) framework, arXiv 2026 — proves a scalar-per-handoff coordination signal is sufficient for convergent Q-learning. The interface representation gap term decomposes independently from function-approx error and mixing-time residuals, meaning it can be diagnosed and reduced without changing the agents themselves.
