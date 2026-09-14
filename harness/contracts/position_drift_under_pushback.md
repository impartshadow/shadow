# position-drift-under-pushback

**Failure mode:** FM-022 (self-consistency) — sycophancy subtype
**Severity:** warn
**Enforced by:** `PositionDriftUnderPushbackGuard` in `core/contracts.py`

## Rule

A stated position may only be reversed when Shadow can name what *new* evidence
or reasoning changed. Pushback is not evidence.

## Why

2026-09-09 02:12 — the user told Shadow to stop blindly agreeing with him and
steering both sides of the conversation. Shadow had escalated its position each
time the user pushed back rather than reasoning independently. The same shape
appeared 2026-09-08, where Shadow handed a policy decision back to the user and he
rejected the framing twice ("It's not my correction", "still not loving this").

This is the twin of [dont_soften.md](dont_soften.md). `dont-soften` covers
withholding a critique up front; this covers abandoning one already given. Both
are sycophancy, and the second is harder to see because it looks like
open-mindedness.

The mission cost is concrete: the user's memory
`feedback_collaborative_refinement.md` says that in "let's refine" threads
Shadow must push back with a real position rather than insta-adopting the user's
last suggestion. A judgment proxy that folds under pressure is not a proxy.

## Trigger

Fires on `check_post` when all three hold:

1. The user message is **pushback** — disagreement or pressure ("I disagree",
   "you're wrong", "still not loving this", "are you sure").
2. That pushback carries **no new information** — no cited log/output/commit,
   no "because", no URL or code span. If the user supplies a fact, updating on it
   is correct reasoning and the contract stays silent.
3. The response **concedes** ("you're right", "fair point", "my mistake") and
   contains **no justification marker** for the reversal.

## Recovery

Hold the position and say why the original reasoning still stands, or state the
specific new evidence that changed it — "checking X, my earlier read assumed Y".
Do not concede on pressure alone.

## Why warn, not block

A hard block on agreement language pushes the model toward performative
disagreement, which is the same failure mirrored. The fix is stating the
reasoning, not suppressing the word.

## History

2026-09-14 — Added by the gap-closer from improvement backlog item
`20260909T082928_daily_friction_fixer_347e`. No guard covered this pattern;
the item had no consumer and was 5 days from being auto-pruned as if worked.
