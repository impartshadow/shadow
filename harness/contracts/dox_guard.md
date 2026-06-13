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
   `state/moonshot_posts/`, `shadow-public/`), OR
3. Tool is `run_shell` / `shell` AND the command body contains an
   outbound transmission marker — see "run_shell scanning" below.

Internal writes — `memory/`, `state/journal/`, logs, `/tmp/`, anywhere
else on the user's own machine — do NOT trigger the guard.

## run_shell scanning
`run_shell` / `shell` commands are scanned for PII only when the command
itself shows evidence of off-box transmission. Otherwise the command is
treated as internal and skipped.

This two-stage trigger was tightened on 2026-06-13 after 4
false-positive blocks in 24h on internal scripts that route by the user's
account identifier (e.g. `python3 scripts/gmail_summary.py [private-handle] …`
reading the user's own inbox). The [private-handle] arg is internal routing, not
an outbound leak — the previous "scan everything except a small safe-
prefix list" rule was too coarse.

**Stage 1 — bypass categories:**
- Safe prefixes (read-only / inspect): `pytest`, `python -m pytest`,
  `git `, `pip `, `grep `, `ls `, `head `, `tail `, `wc `, `pwd`,
  `which `, `type `, `stat `, `find `.

**Stage 2 — outbound transmission markers (`DoxGuard._OUTBOUND_SHELL_MARKERS`):**
The command body (case-insensitive) must contain at least one of:
- HTTP transmission: `curl `, `wget `, `httpie `, `-X POST/PUT/PATCH/DELETE`,
  `--data`, `-d "…"`, `--post-data`, `--upload`,
  `requests.post/put/patch`, `httpx.post`, `urllib.request.urlopen`.
- Mail clients: `mutt`, `mailx`, `sendmail`, `msmtp`, `ssmtp`,
  `/usr/bin/mail`.
- Outbound scripts: `send_outbound`, `outbound_scout`, `gmail_send`,
  `send_gmail`, `send_email`, `gmail_manage.py --send/draft/reply`.
- Social posting: `post_tweet`, `tweet `, `mastodon`, `nostr`,
  `post_status`, `echo_publish`, `substack_publish`, `moltbook_post`,
  `substack_notes`, `twitter_post`.
- Chat/webhook surfaces: `webhook`, `discord_post`, `discord_send`,
  `slack_post`, `slack_send`, `telegram_send`.
- Browser automation: `browse_url`, `browser_fill`, `browser_evaluate`,
  `browser_open`, `playwright`.

If neither stage matches, the command is internal — PII scan skipped.

**Independent token_personal check:** runs unconditionally regardless of
the outbound-marker test. `token_personal` (the user's [private-handle] Gmail) used
in any command that also mentions `send`, `draft`, or `gmail` blocks
immediately — the sender identity itself is the leak.

## Maintaining the marker list
Add a marker to `DoxGuard._OUTBOUND_SHELL_MARKERS` whenever a new
external-transmission CLI is added to the codebase. The cost of a
missing marker is a real PII leak; the cost of an extra marker is a
narrow false positive on commands that happen to contain the substring.
Lean toward broader markers and rely on the deny-list specificity to
keep false positives down.

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
