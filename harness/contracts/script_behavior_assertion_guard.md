# script-behavior-assertion-guard

**Type:** Post-check (code-enforced, warn)
**Failure mode:** FM-022 (state assertion without grounding)
**Trigger:** Response text references a high-churn internal script name and asserts what it does/doesn't do.

**Precondition:** If the response asserts a behavior claim about an internal Shadow script (e.g., "/reflect only diagnoses", "nightly.py doesn't restart the bot", "session_audit doesn't write to memory"), a `Read` or `Grep` of that script must have run in the same turn.

**Enforcement:** `core/contracts.py:ScriptBehaviorAssertionGuard.check_post()` — matches a curated list of high-churn scripts (`reflect.py`, `nightly.py`, `session_audit.py`, `heartbeat.py`, `moonshot_daily.py`, `daily_friction_fixer.py`, `anticipation*.py`, `credential_guardian.py`, `loop_dispatcher.py`, `twitter_engage.py`, `moltbook_engage.py`, `substack_publish.py`) plus assertion phrases (`only diagnoses`, `doesn't write`, `has no code-edit loop`, `diagnose-only`, etc.). Passes if a live read tool touched the named script this turn.

**Severity:** warn — not block. Some assertions are correctly grounded in a Read that the regex can't trivially confirm; the trace log lets `session_audit.py` catch persistent recurrence.

**Recovery:** `Read scripts/<name>.py` (or `Grep` for the relevant function) in the same turn, then re-answer with the read-back in context.

**Escalation:** None at warn severity. If the same script triggers >3 times in 24h, surface to `#shadow-log` via the daily failure-mode digest.

**Origin:** Backlog `20260619T082541_daily_friction_fixer_f968` — Shadow told the user `/reflect` was diagnose-only with "no tool-execution or code-edit loop" (10:20), then retracted 6 minutes later because the repair executor was already live in the script. CLAUDE.md rule #41.
