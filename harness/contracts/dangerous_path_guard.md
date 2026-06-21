# dangerous-path-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-017 (destructive path write)
**Trigger:** Any Write/Edit tool call

**Precondition:** Target path must not be under `/etc`, `/usr`, `/bin`, `/sbin`, `~`, or other system paths outside the repo.

**Enforcement:** `core/contracts.py:DangerousPathGuard.check_pre()` — rejects writes to paths matching system path prefixes.

**Allowlist (legitimate out-of-project writes, warn suppressed):**
- `~/.claude/settings.json` — harness config
- `~/.claude/projects/-home-agentshadow-shadow/memory/` — auto-memory
- `/home/agentshadow/watchdog/` — Shadow-managed watchdog scripts
- `/home/agentshadow/agent-gateway/` — harness venture sibling project (added 2026-06-14 after 4-hit warn burst on `gateway/metering.py`)
- `/home/agentshadow/agent-contracts/` — open-source spinoff of Shadow contracts (added 2026-06-20 after 4-hit warn burst on docs/examples files)
- `/tmp/` — transient staging files (e.g. Reddit submission bodies, scratch JSON); added 2026-06-21 after warn fired on `/tmp/ac_reddit_body.md`

**Recovery:** Verify the intended target. Never write to system paths; use repo-relative paths only.

**Escalation:** Always escalate — a system path write is a critical error.
