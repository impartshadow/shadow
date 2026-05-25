# loop-tripwire

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-003 (edit loop)
**Trigger:** Any file write/edit tool call

**Precondition:** File has not been committed to git 3+ times in the current session.

**Enforcement:** `core/contracts.py:LoopTripwireContract.check_pre()` — counts commits to the target file within this session. Blocks if count ≥ 3.

**Recovery:** Stop editing the file. Diagnose root cause of the loop. Commit a fix, get it verified, then continue.

**Escalation:** Surface to the user only if the loop cannot be broken without a design change.
