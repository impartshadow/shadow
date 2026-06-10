# loop-tripwire

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-003 (edit loop)
**Trigger:** `edit_file` action targeting a looped file, or `git_push` action while any tracked file has ≥ 2 session commits.

**Precondition:** Target file has been committed to git fewer than 2 times in the current session (warn) / fewer than 3 times (block).

**Enforcement:** `core/contracts.py:LoopTripwire.check_pre()` — counts commits to each file within the current session. On `edit_file`, the looped file must appear in `ctx.files_edited` for the contract to fire (narrowed 2026-05-28 to avoid 8 false positives where the contract fired on every unrelated edit once any file hit threshold).

**Recovery:** Stop editing the file. Diagnose root cause of the loop. Commit a fix, get it verified, then continue.

**Escalation:** Surface to the user only if the loop cannot be broken without a design change.
