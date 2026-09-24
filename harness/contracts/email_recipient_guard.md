# email-recipient-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-016 (wrong recipient)
**Trigger:** Any email send operation

**Precondition:** Recipient must match the intended address. "send to gmail" = [private-email] always. Sending identity (`from`/`sender`) must resolve to a known Shadow identity (Whoami check) — prevents using the wrong identity/domain.

**Enforcement:** `core/contracts.py:EmailRecipientBlockGuard.check_pre()` — validates recipient against known-safe list and sender identity against `_KNOWN_SENDERS` (Whoami allowlist) before send.

**Recovery:** Confirm recipient before sending. If ambiguous, check will_prefs.md.

**Escalation:** Always surface ambiguous recipients to the user before sending.

## Shared business inboxes

Judge first contact by message purpose and the recipient's published remit,
not solely by `info@`, `hello@`, or `support@`. A legitimate service or
eligibility inquiry, a published application, or requested contact may belong
at a shared inbox. Unsolicited pitches to helpdesks remain inappropriate.

For these appropriate contacts, supply `EmailSendPreflight.new_thread` with
`contact_purpose` (`service_inquiry`, `eligibility_inquiry`,
`published_application`, or `requested_contact`), `recipient_context` citing
the source and explaining the fit, and `authority_basis` citing existing
authority for that recipient and action. Inspect the actual message and source
before recording this judgment. These fields document judgment; they do not
grant authority or prove the cited facts. Do not relabel a pitch as an inquiry.
No-reply addresses are not contact channels. Preserve all other sending checks.

Reserve `operator_approved_new_thread` for actual explicit operator approval.
A guard error is not by itself a reason to ask the user: resolve context and
authority first. If approval is necessary, explain the value, exact proposed
action, and authority boundary in a self-contained request. Do not bulk resend
historically blocked or retired outreach after a rule change.
