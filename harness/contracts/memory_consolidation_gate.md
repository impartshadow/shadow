# Memory Consolidation Gate

**Type:** Behavioral contract (prose)

**Trigger:** Any action that would merge, overwrite, or delete memory files.

**Precondition:** The action must be explicitly triggered by a deliberate `/improve` run or a named consolidation command from the user. Auto-consolidation during idle sessions, session writes, or background tasks is prohibited.

**Rule:** Memory writes are **append-first, rewrite-rarely**.
- Session writes (session_handoff.md) → append new block; never clobber prior blocks
- New insights → new memory files; never silently rewrite existing files
- Merging overlapping files → only during explicit `/improve` runs
- Deleting memory files → only during explicit `/improve` runs after audit

**Enforcement:** Prose (behavioral). The idle_moonshot `memory_consolidation` task is audit-only — it identifies candidates but does not execute merges. `dreaming.py` and `memory_consolidate.py` are gated to explicit invocation only, never auto-scheduled.

**Recovery:** If a background task attempts a memory merge, abort and post the candidate list to #moonshot instead. Do not merge.

**Escalation:** None — this is a hard behavioral rule Shadow enforces unilaterally.

**Research basis:** arXiv 2026 — "Useful Memories Become Faulty When Continuously Updated by LLMs". Controlled ARC-AGI experiments showed episodic-only (no auto-consolidation) doubled accuracy vs. forced-consolidation agents. The consolidation rewrite step itself is lossy and non-deterministic; same trajectories yield qualitatively different memories under different update schedules.
