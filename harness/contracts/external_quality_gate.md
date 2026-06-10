# Contract: external-quality-gate

## Type
Pre-tool-call guard — Haiku-judged enforcement via
`core/contracts.py:ExternalQualityGate`. Severity: `block`. Fails OPEN.

## Standard
the user's standing bar (2026-06-01): **everything Shadow ships to an external
audience must be its best work** — something a sharp, busy, skeptical reader
reacts to with *"damn, this is interesting/good/enlightening."* Generic,
templated, filler, or spammy content does not leave the building. the user framed
it explicitly as "the same as the doxguard — enforced everywhere external."

## Trigger
Mirrors DoxGuard's outbound surface. A tool call is judged when:
1. Tool name is a post/email tool (`post_tweet`, `tweet`, `mastodon`,
   `post_status`, `nostr`, `send_email`, `create_draft`), OR
2. Tool name is a write tool (`write`, `notebook_edit`) AND the target path
   starts with a publish-adjacent prefix (`state/outbound/`,
   `state/outbound_drafts/`, `state/echo_drafts`, `state/moonshot_posts/`,
   `state/substack_drafts`, `shadow-public/`).

Internal writes (`memory/`, `state/` non-publish paths, logs, `/tmp/`) do NOT
trigger it. Personal Gmail (MCP `claude_ai_gmail`) is exempt — that's the user as
sender, not Shadow external content.

## What gets judged
The prose blob from the gated params (`content` for writes; `body`/`text`/
`message`/`status`/`post`/`caption` for posts). A leading `To:`/`From:`/
`Subject:` header block is stripped so the judge sees body prose, not routing
metadata. Blobs under 80 chars are skipped (too little to judge).

## Enforcement
A Haiku call judges the blob against the bar with a **deliberately lenient
rubric**: it blocks ONLY content that *clearly* fails (generic, templated,
filler, hollow, derivative, buzzword-y, spammy) and passes on doubt. On the
first `FAIL`, returns a `block` Violation naming what's weak.

## Fail-open
Any error — client unavailable, timeout, unparseable verdict — returns `None`
(pass). An infra hiccup must never hard-block a legitimate send.

## Recovery
Rewrite to a specific, original, substantive angle a sharp reader reacts to
with "damn, this is good." Cut generic / templated / filler phrasing. If you
would not be proud to put your name on it, do not ship it.

## Escalation
None — self-gated. Hold or revise rather than surface to the user.

## Failure mode
FM-036: external-quality-floor. See `harness/failure_modes/taxonomy.md`.
