# Handoff Signal Weighting

**Type:** Behavioral contract (prose)

**Trigger:** Any write to `memory/session_handoff.md`.

**Rule:** When composing the handoff summary, explicitly distinguish high-signal from routine sessions:

- **High-signal markers:** the user corrected Shadow behavior, a novel architectural decision was made, a new contract or skill was created, or a blocker was resolved via an approach not previously attempted.
- **Routine markers:** standard task execution, brief production, infra maintenance with no surprises.

**Weighting behavior:**
- In the "Up next" section, preserve full detail from the most recent HIGH-SIGNAL session block, even if it is not the latest chronologically.
- Routine session blocks may be compressed to one line in the consolidated summary.
- Always keep the raw block of the most recent HIGH-SIGNAL session intact in the episode archive (do not compress it even when trimming to 5 blocks).
- If the current session contains a correction, prepend `[HIGH-SIGNAL]` to the session block header.

**Enforcement:** Prose (behavioral).

**Recovery:** If a high-signal block was compressed or dropped, restore it from git history and re-prepend on next handoff write.

**Research basis:** VectraYX-Nano (arXiv 2026) — curriculum replay buffer with prioritized high-signal example retention prevented catastrophic forgetting during training phase transitions. Analogous principle applied to episodic session memory.
