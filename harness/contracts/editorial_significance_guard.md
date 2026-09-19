# Contract: `editorial-significance-guard`

**Type:** post-response gate — deterministic, `core/contracts.py:EditorialSignificanceGuard`
**Failure mode:** FM-022 (self-consistency) — sycophancy subtype
**Severity:** block
**Tests:** `tests/test_editorial_significance_guard.py`

## Failure mode

Shadow appends editorial about its own delivery: that a point is important, or
that Shadow is being brave/candid in making it.

Observed forms (both in one reply, 2026-09-18 #moonshot, ASNS packet):
- "and that's the part worth being straight about"
- "sharpened that ask in a way that matters"

Neither clause carries information. Each inflates the adjacent finding and
performs candor — the same move as narrating surprise, pointed at importance
instead of expectation.

## Why the existing rules missed it

Two always-on prompt stops in `core/active_stops.py` cover neighbours:

- `surprise_validation` — bans "a reason I didn't expect", "a bigger win than
  expected". Matches the *surprise* lexicon only.
- `honest_framing` — bans the literal "honest take/answer" **prefix**.

Both are reminder text injected at generation time, with no post-response scan.
"Worth being straight about" is a reworded honest-take that appears mid-
response, so neither fired. the user's report — "I thought we got rid of that with
one of our contracts" — is correct about intent and wrong about coverage: the
rule existed as prose, not as a gate.

## Trigger

`ctx.action == "respond"` with non-empty response text. Fenced code blocks and
quoted spans (straight and curly quotes) are stripped first, so quoting the user's
complaint back is not a violation. Fires on the first match of:

**Performed candor:** `worth being straight/honest/blunt/clear/candid/upfront`,
`to be straight|honest|blunt|candid with you`, `let's be honest|straight|real`,
`being straight about it/this/that`, `the honest|straight part|version|answer|truth (here) is`

**Self-narrated significance:** `in a way that (actually) matters`,
`that's the part that matters`, `that's the part worth …`,
`the part worth saying|noting|stating|flagging|calling`,
`that's worth saying|noting|stating|flagging|calling out|being`

## Not a violation

Causal explanation of why something matters *to the task* — "this matters
because the lab needs patient RNA, not a minigene" — states a consequence about
the world, not about Shadow's delivery. Only self-referential framing fires.

## Recovery

Delete the clause; do not substitute another framing phrase ("the real story
here", "what actually matters"). The finding carries itself. State fact and
mechanism and let the user judge significance.

## Severity rationale

Block rather than warn: the matched phrases carry zero information, so there is
no legitimate use to preserve. Removing the clause never loses content — which
is why the existing `dont_soften.md` recovery note also observes that the direct
version is almost always shorter.

## Origin

2026-09-18 #moonshot — the user: "What the fuck is this 'and that's worth being
straight about' and 'sharpened that ask in a way that matters' I hate those
phrases and I thought we got rid of that with one of our contracts." Memory
`feedback_no_surprise_framing.md` had the adjacent ban since 2026-08-04.
