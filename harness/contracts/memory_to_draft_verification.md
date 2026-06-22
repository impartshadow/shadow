# memory-to-draft verification gate

**Type:** Pre-check (block before Write/post).
**Failure mode:** FM-026.
**Contract class:** `MemoryDraftVerificationGate` in `core/contracts.py`.

## Trigger

A `Write` to a publish-adjacent path (`drafts/`, `state/outbound_drafts/`,
`state/echo_drafts/`, `state/moonshot_posts/`, `state/substack_drafts/`,
`state/outbound/`, `shadow-public/`) OR a direct outbound post tool
(`post_tweet`, `send_email`, `create_draft`, `mastodon`, `post_status`,
`nostr`).

## Precondition

The content blob must NOT contain an unqualified self-credibility metric of
the form:

| Pattern | Example match |
|---|---|
| top-N ranking | "verifiable top-5 Claude Code user" |
| billions-of-tokens | "20 billion tokens over twelve weeks" |
| one-of-the-highest | "one of the highest-volume Claude Code users" |
| anthropic-verified | "Anthropic-verified high-volume user" |
| leaderboard claim | "atop the Claude Code leaderboard" |
| verifiable self-claim | "verifiable top operator" |

A "qualifier" within ~200 chars of the claim defuses it:

- Paren tags: `(unverified)`, `(internal)`, `(from memory)`,
  `(from training data)`, `(self-reported)`, `(approximate)`, `(directional)`,
  `(estimate)`.
- Bare phrases: `internal leaderboard`, `self-reported`, `not Anthropic-verified`.

## Enforcement

Code (`MemoryDraftVerificationGate.check_pre`). Severity **block**.

## Recovery

Pick one before the write lands:

1. Soften to a qualitative claim the reader can take at face value —
   "a very high-volume operator", "operating at the scale of tens of
   billions of tokens".
2. Add the inline qualifier in parens — `(internal leaderboard — not
   Anthropic-verified)`.
3. Cite the source by name in the same paragraph — `per Anthropic's
   <dashboard>` or `per the Epic internal Claude Code rollout`.

The word **"verifiable"** appearing in a memory file is NOT a verification.
The agent putting it on the page in the memory description is the same
agent generating the draft — the adjective doesn't survive the loop.

## Escalation

None. The fix is one of the three recoveries above. If a real
Anthropic-verified ranking exists and a buyer can audit it, cite the source
— the gate then accepts the claim.

## Origin

2026-06-22 — Shadow drafted `drafts/governance_failure_modes.md` for the
governance-play credibility piece. The lead paragraph embedded "verifiable
top-5 Claude Code user, ~20B tokens / 12 weeks" lifted directly from
`memory/user_epic_ai_role.md`. The piece was pitched as publish-ready.
the user had to ask "What are you basing the one of the most highest volume?"
before the source was disclosed. The number was an internal Epic
leaderboard, not an Anthropic-verified ranking.

Extends CLAUDE.md Rule 42 (external URLs + consumer-product claims need a
fetch or `(unverified)` flag) to the memory→draft path: a self-descriptor
embedded into outbound content is the same generation-without-verification
failure as a fabricated commit hash (Rule 29) or a premature "done" on a
multi-step flow (Rule 30).
