# Contract: gmail-sender-identity-guard

## Type
Pre-action gate — deterministic enforcement via
`core/contracts.py:GmailSenderIdentityGuard`. Severity: `block`.

## Failure mode
FM-023 (identity/PII leakage) — an outbound Gmail send is constructed with
the operator's personal address bound to the sender slot.

## Threat model
The personal address is the user's own inbox. Per standing authority it is valid
as a *recipient* (Quick Reference rule 9, "send to gmail") and as an argument
to inbox reads (`gmail_summary.py <personal> …`), but it is never a valid
**sender** — business sends originate from the business account.

The literal token and the business sender address are defined once, in
`core/contracts.py:GmailSenderIdentityGuard` (`_PERSONAL_TOKEN`) and the
standing-authority section of `CLAUDE.md`. This document deliberately does
not restate the address, so the identifier does not spread across the repo.

The pre-existing `raw-gmail-send-guard` keyed on *transport* (smtplib, the
Gmail HTTP endpoint) and so missed identity violations that used an approved
transport with the wrong `from`. This guard keys on sender identity in a
send slot, which is invariant across transports.

## Trigger
Four detection primitives, any one of which blocks:

1. **Sender kwarg** — `from_addr=`, `sender=`, `from_=`, or `userId=` bound
   to a literal containing the personal token (AST scan).
2. **Header assignment** — a `From` / `from` / `Sender` / `Reply-To` header
   assignment or dict-literal entry whose value contains the personal token.
3. **Shell argv** — `--from <personal>`, including the
   `gmail_manage.py send … --from <personal>` form.
4. **Tool arguments** — a tool call whose serialized args contain a send verb
   (`send`, `draft`, `MIMEText`, `messages/send`) co-occurring with a sender
   slot bound to the personal token.

Runs as a runtime `check_pre` and as a static AST scan on `git_commit` /
`git_push`, so the pattern is caught both when executed and when committed.

## Not flagged
The recipient forms (`--to <personal>`, `to=<personal>`), inbox reads
(`gmail_summary.py <personal>`), `list sent`, prose/markdown/comment
mentions, anything under the excluded path prefixes (`tests/fixtures/**`),
and any file or line carrying `# noqa: GmailSenderIdentityGuard`.

The recipient case is the common legitimate one; separating the sender slot
from the recipient slot at the AST level is what keeps the false-positive
rate at zero on rule-9 sends to the user.

## Precondition
Every outbound Gmail send names the business account as sender.

## Recovery
Replace the sender with the business account. If the intent was to email
the user, the fix is to move the personal address from the sender slot to the
recipient slot (`to=`), not to suppress the guard. Test fixtures belong
under `tests/fixtures/` with the `# noqa: GmailSenderIdentityGuard` marker.

## Related
Extends `dox-guard` (FM-023), which blocks the personal token co-occurring
with send/draft verbs in shell text. This guard adds structural (AST)
coverage of the sender slot that a text-level match cannot distinguish from
a recipient.

## Escalation
None. The correct sender is unambiguous — this is a mechanical fix, never a
the user-facing blocker.
