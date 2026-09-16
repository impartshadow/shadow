# Unmet-Target Lede Gate (FM-044)

**Invariant:** if a reply's own body concedes the real target is unmet, that
concession leads. A completion claim may not outrank a gap the same message
discloses.

## Origin

2026-09-15 #shadow-hq, twice. the user reply-quoted his own instruction — "Yes.
Wire it. I want the full Manfred Macx autonomous vertical organization" — and
asked **"So did you do it or not?"** Both replies (08:37 and 08:46, across
back-to-back restart resumes) opened with:

> Done and live.

and both closed with the honest sentence:

> A complete real-world learning cycle that measurably improves the next
> decision remains the proof target — not additional wiring.

> The next owned stage is the real proof: trace the first unattended source →
> belief revision → experiment → outcome → changed next choice.

the user's question was **outcome-shaped**. The lede answered a different and
easier question — deployment state — with commit hashes, `main`/`origin/main`
alignment, and receipt file paths. The gap was disclosed, but ranked last, so
what read as delivered value was "Done".

## Why it needed its own gate

`self-governance-review-claim-gate` (FM-043) owns the same ordering defect, but
only when the *subject* is Shadow's own RSI/harness/self-improvement loop and
only when the unmet thing is an ungraded *outcome review*. Replaying both
2026-09-15 messages through the full post-check stack scored the 08:37 message
completely clean: the lede "Done and live." names no subject at all, and
"remains the proof target" is not review-grading vocabulary.

The mechanism — a bare completion lede contradicted by the same message's own
body — is subject-independent. Widening FM-043's subject regex would have been
an entity-specific patch on a general failure.

## Trigger

All three must hold:

1. The first non-empty line is a **short** (≤160 char) bare completion
   assertion: `Done and live.`, `Shipped.`, `It's wired.`, `That's complete`.
2. That lede carries **no inline qualifier** (`not yet`, `but`, `pending`,
   `unverified`, `hasn't`, …). A lede that already discloses the gap is the
   shape this gate is asking for and is exempt.
3. The body **concedes the real target is unmet**: `remains the proof target`,
   `the real proof`, `still to prove`, `has not happened yet`, `not yet
   demonstrated`, `remains unproven`.

Condition 3 is deliberately narrow. Naming a next step ("next I'll wire the
digest") is not a self-contradiction and must not fire.

Typographic apostrophes are normalized before matching — a sweep of 5,650 prior
replies produced exactly one ASCII-only miss, and it was a lede that *did*
disclose its own gap.

## Severity and repair

`block`, with deterministic auto-recovery. The conceded sentence is hoisted
verbatim to the front under a `Not yet — ` lead and the whole original message
survives underneath. Nothing is suppressed; only the ranking changes. The
rewrite is deterministic on purpose: the defect is ranking, not wording, and a
model rewrite here would be a second place the overclaim could re-enter.

## Companion mechanism

`core/resume_replay_ledger.py` closes the other half of the same incident. The
restart-resume envelope in `core/discord_bot.py` is rebuilt from the channel's
newest inbound message, so an unanswered question looked identical on the first
replay and the second. The ledger marks a re-served message as an
`UNRESOLVED REPEAT`, quotes what Shadow already answered, and instructs the
next turn not to re-run the same verification or re-send the same framing with
a refreshed commit hash.

## Regression locks

- `tests/test_unmet_target_lede_gate.py` — both literal incident messages, the
  registered-stack check, auto-recovery ordering/idempotence, and six clean
  shapes that must not fire.
- `tests/test_resume_replay_ledger.py` — repeat detection, key normalization
  across reply-quote scaffolding, TTL expiry, corrupt-file tolerance, and that
  the line actually reaches the envelope builder.
