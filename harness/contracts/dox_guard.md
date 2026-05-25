# Contract: dox-guard

## Type
Pre-tool-call guard — deterministic enforcement via
`core/contracts.py:DoxGuard`. Severity: `block`.

## Threat model
The the user<->Shadow Discord channel is a **private two-way conversation**.
Shadow referring to the user by name, email, or handle inside that channel
is normal dialogue, NOT a dox.

The actual threat is Shadow emitting identifiers **OUT OF** that
conversation — to third parties or public surfaces:
- Cold emails from Shadow's mailbox to strangers
- Tweets / Mastodon / Nostr posts
- Webhook / platform-registration POSTs (e.g. Moltbook)
- File writes to publish-adjacent paths (`state/outbound_drafts/`,
  `shadow-public/`, etc.)

This contract guards ONLY the outbound surface. It does NOT run on
`respond` action — Discord output is not scrubbed.

## Trigger
A tool call is scanned when:
1. Tool name contains an outbound substring (`gmail`, `send_email`,
   `create_draft`, `post_tweet`, `tweet`, `mastodon`, `nostr`,
   `webhook`, `post_url`, `http_post`), OR
2. Tool name contains a write substring (`write`, `notebook_edit`)
   AND the target path starts with a publish-adjacent prefix
   (`state/outbound_drafts/`, `state/echo_drafts`,
   `state/moonshot_posts/`, `shadow-public/`).

Internal writes — `memory/`, `state/journal/`, logs, `/tmp/`, anywhere
else on the user's own machine — do NOT trigger the guard.

## What gets scanned
Inside each gated tool_params, the following fields are combined and
checked:
- Prose: `body`, `content`, `text`, `message`, `subject`, `status`,
  `post`, `caption`
- Paths: `file_path`, `path`
- URLs: `url`, `endpoint`

Matching:
- Deny-list substring match (normalizes hyphens/underscores to spaces
  so `private-name` also matches `the user`)
- Generic email regex (minus explicit whitelist)
- Phone regex (with/without parens, country code, separators)

## Deny-list
`DoxGuard._DENY_LIST` in `core/contracts.py`. Currently:
- `[private-email]`, `[public-contact-email]`
- Bare handles `[private-handle]`, `[public-handle]`
- `the user` as multi-word phrase (last-name alone is common — not
  matched to avoid false positives)

Expand by editing the list and adding a regression case to
`tests/test_contracts.py::TestDoxGuard`.

## Violation message discipline
The violation message counts matched identifiers but never echoes the
matched substring — log lines and violation reports must not themselves
leak the identifier they blocked.

## No auto-recovery
Blocked responses must be **regenerated from scratch** without the
identifier. In-place redaction in outbound content ("I'm
[redacted-name]'s agent") reads badly; rewriting is cleaner.

## Origin
- 2026-04-18 first incident: Shadow printed `[public-contact-email]`
  in `#shadow-hq` Discord. Initially shipped a `check_post` to block
  Discord output.
- 2026-04-18 the user corrected the framing: "I don't care if they hit
  discord. That's not the problem. You were going to send my info out
  of our two-way conversation into the world." Contract inverted:
  `check_post` removed; `check_pre` on outbound tools is the whole
  point.
- Root cause of the Moltbook/outbound_scout leak: `scripts/outbound_scout.py`
  hardcoded the principal's name into the Haiku prompt. Fixed in the
  same session.
