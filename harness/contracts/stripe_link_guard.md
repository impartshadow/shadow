# Contract: stripe-link-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:StripeLinkGuard`. Severity: `block`.

## Failure mode
FM-033 — recurrence of an explicitly corrected behavior. the user has corrected
"don't link Stripe" 6+ times. The behavior keeps regenerating; this contract
converts a Haiku post-hoc catch (`persistent-correction`) into a deterministic
regex block.

## Threat model
The Substack paywall at `echofromshadow.substack.com` is the trailhead for
paid conversion. Substack's native paid-subscription flow handles checkout
via the connected Stripe account, so a Stripe link in a user-facing surface
is redundant at best and an unwanted source-of-truth divergence at worst.

CLAUDE.md rule #38 (2026-06-18) documents the standing prohibition. Six
violations of "Stop linking Stripe" landed across 24h (2026-06-17 → 2026-06-18)
with no deterministic gate — `persistent-correction` was only catching them
post-hoc. This contract closes the loop.

## Trigger
A response is scanned when its text length is ≥ 8 chars and contains any of:
- `https?://*.stripe.com`
- `buy.stripe.com`
- `checkout.stripe.com`
- `dashboard.stripe.com`

## Enforcement
Each match is checked against three exemption conditions; the violation fires
only if none apply:

1. **Inside a fenced code block** (odd `` ``` `` count before the match).
   Technical context, e.g. `PAYMENT_LINK = "..."` placeholders in scripts —
   not a user-facing link.
2. **Inside a straight-quoted span** (odd `"` count before the match).
   the user pasted a Stripe URL; Shadow is mirroring it back.
3. **Markdown blockquote line** (`>` at start of the match's line). Same
   mirror semantics as case 2.

Otherwise the contract emits a `block`-severity violation with a recovery
hint pointing to `echofromshadow.substack.com`.

## Recovery
Replace the Stripe URL with the Substack URL. The Substack paywall handles
checkout via the connected Stripe account; the user-facing link should
never be Stripe directly. The only legitimate exception is mirroring back a
Stripe URL that the user pasted himself (case 2 above), which the regex skips.

## Relationship to other contracts
- `persistent-correction` (Haiku) was the prior catch — its hit rate on
  "Stop linking Stripe" prompted this guard. Haiku still runs but now serves
  as a fallback for paraphrased or obfuscated Stripe references that the
  regex can't see.
- `partial-evidence-flag` enforces a *different* Stripe coupling: revenue $
  claims must cite a Stripe READ or `state/revenue.json`. That contract is
  about epistemic grounding; this one is about user-facing links. They share
  a substring but distinct semantics.
- CLAUDE.md rule #38 is the upstream behavioral rule; this contract is the
  downstream gate.

## Escalation
Block is sufficient. The recovery is mechanical (swap the URL). Do not
surface to the user — the rule and the recovery are both documented in
CLAUDE.md. Recurring violations within a single session indicate prompt
contamination from a Stripe-link-bearing memory or template; track via
`state/trajectory_log.jsonl` and treat as a prompt-source bug, not a
behavioral regression.

## Recent activity
6 violations across 24h on 2026-06-17 → 2026-06-18 caught post-hoc by
`persistent-correction` ("Stop linking Stripe") and `patterned-stop` before
the deterministic gate landed. After this contract is registered, every
match in conformant response text becomes a hard block at emit time.
