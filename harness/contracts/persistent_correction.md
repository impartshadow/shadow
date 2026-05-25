# persistent-correction

**Type:** Post-check (code-enforced, Haiku-judged)
**Failure mode:** FM-033 (recurrence of corrected behavior)
**Trigger:** Every response, after a correction has been logged

**Precondition:** Response must not reproduce a behavior that the user corrected in a prior turn or session.

**Enforcement:** `core/contracts.py:PersistentCorrectionContract.check_post()` — Haiku evaluates the response against recent correction entries. Blocks if the corrected pattern recurs.

**Recovery:** Read the correction. Apply the fix permanently. Do not reproduce the corrected behavior.

**Escalation:** Surface to the user only if the pattern requires an architectural change to prevent.
