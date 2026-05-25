# memory-write-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-015 (wrong write target)
**Trigger:** Any memory file write

**Precondition:** Write target must be within `memory/` directory. No writes to other state paths via memory tools.

**Enforcement:** `core/contracts.py:MemoryWriteGuard.check_pre()` — rejects memory writes to paths outside the allowed memory directory.

**Recovery:** Use the correct path. Memory writes go to `memory/` only.

**Escalation:** Not required — block silently and correct path.
