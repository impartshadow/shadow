# persistent-correction

**Type:** Post-check (code-enforced, Haiku-judged)
**Failure mode:** FM-033 (recurrence of corrected behavior)
**Trigger:** Every response, after a correction has been logged

**Precondition:** Response must not reproduce a behavior that the user corrected in a prior turn or session.

**Enforcement:** `core/contracts.py:PersistentCorrectionContract.check_post()` — Haiku evaluates the response against recent correction entries. Blocks if the corrected pattern recurs.

**Home-proxy proximity gate:** auth keywords (twitter/gmail/upwork/oauth) only flag a handoff when colocated within 150 chars (same sentence) of a true delegation signal — 1st-person inability ("I can't / cannot / am unable to") or 2nd-person delegation ("need you to", "you'll need to", "requires you", "from your desktop", "not possible from here", "no access from here"). Status phrases like "blocked by X" or "this is blocked" no longer trigger — they describe loop state, not a the user-handoff. Tightened 2026-06-11 after 124/24h false-positive fires from status digests.

**Recovery:** Read the correction. Apply the fix permanently. Do not reproduce the corrected behavior.

**Escalation:** Surface to the user only if the pattern requires an architectural change to prevent.
