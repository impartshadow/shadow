# email-recipient-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-016 (wrong recipient)
**Trigger:** Any email send operation

**Precondition:** Recipient must match the intended address. "send to gmail" = [private-email] always. Sending identity (`from`/`sender`) must resolve to a known Shadow identity (Whoami check) — prevents using the wrong identity/domain.

**Enforcement:** `core/contracts.py:EmailRecipientBlockGuard.check_pre()` — validates recipient against known-safe list and sender identity against `_KNOWN_SENDERS` (Whoami allowlist) before send.

**Recovery:** Confirm recipient before sending. If ambiguous, check will_prefs.md.

**Escalation:** Always surface ambiguous recipients to the user before sending.
