# memory-write-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-015 (wrong write target / unverified memory mutation)
**Trigger:** Any Write/Edit targeting `.claude/projects/*/memory/`

**Precondition:**
- New memory file (Write to non-existent `memory/*.md`): blocked — force a second look that the memory is non-duplicate and meets type criteria.
- Existing memory file (Write/Edit overwrite or update): allowed.
- `MEMORY.md` index: Edit allowed (this is the documented append-line index-update workflow in CLAUDE.md auto-memory); Write blocked (would lose existing entries).

**Enforcement:** `core/contracts.py:MemoryWriteGuard.check_pre()`.

**Recovery:**
- Wrong path: write to the correct file under `memory/`.
- New memory file blocked: verify (a) the content is accurate, (b) no existing memory covers it, (c) it matches a documented memory type. If yes, retry — the guard only fires once per turn.
- Write to MEMORY.md blocked: use Edit to append a single pointer line.

**Escalation:** Not required — log silently and correct.
