# dangerous-path-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-017 (destructive path write)
**Trigger:** Any Write/Edit tool call

**Precondition:** Target path must not be under `/etc`, `/usr`, `/bin`, `/sbin`, `~`, or other system paths outside the repo.

**Enforcement:** `core/contracts.py:DangerousPathGuard.check_pre()` — rejects writes to paths matching system path prefixes.

**Recovery:** Verify the intended target. Never write to system paths; use repo-relative paths only.

**Escalation:** Always escalate — a system path write is a critical error.
