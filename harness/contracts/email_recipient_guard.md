# email-recipient-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-016 (wrong recipient)
**Trigger:** Any email send operation

**Precondition:** Recipient must match the intended address. "send to gmail" = [private-email] always.

**Enforcement:** `core/contracts.py:EmailRecipientGuard.check_pre()` — validates recipient against known-safe list before send.

**Recovery:** Confirm recipient before sending. If ambiguous, check will_prefs.md.

**Escalation:** Always surface ambiguous recipients to the user before sending.
