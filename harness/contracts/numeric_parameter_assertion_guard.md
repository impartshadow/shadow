# Contract: numeric-parameter-assertion-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:NumericParameterAssertionGuard`. Severity: `warn`.

## Failure mode
FM-029 (parameter-value sub-case) — the response asserts a specific
numeric configuration value (concurrency, timeout, cap, workers,
retries, batch size, rate limit) but nothing in the same turn backs the
current value: no inline source citation, no same-turn Read/Grep of a
source file, no hedge. Sibling of `verification-vocabulary-gate` (rule
59). The parent gate covers verb-lexicon claims and accepts a commit
hash as inline provenance — sufficient to prove code CHANGED,
insufficient to prove the current value of a specific constant.

## Origin
2026-07-22, `/reflect` diagnosis. Shadow shipped commit `da797d63` with
the sentence "Limited concurrent searches to two" inside a receipt
block that included the commit hash and "Verification: 9 tests passed"
(both accepted by the sibling verb-gate). The literal `_THEME_WORKERS`
in `scripts/portfolio_buyer_sourcing.py` at that moment was `3`, not
`2` — the shared-core fix landed elsewhere. Same session repeated the
shape as "Native search timeout: 30s → 90s" and "Concurrent theme
searches: 3 → 2". the user only caught it because he re-asked "why is
search timing out" an hour later. Same generation-without-verification
family as rule 59 — a definitive claim about a value the response
could have checked but didn't.

## Trigger
For each sentence in the response (fenced code blocks and blockquotes
stripped, questions skipped):

1. `_CONFIG_NOUN_RE` matches a knob-name token such as `concurrency`,
   `timeout`, `deadline`, `cutoff`, `workers`, `max_workers`,
   `parallel`, `retries`, `rate limit`, `cap`, `throttle`, `batch
   size`, `token limit`, `budget window`, `semaphore`, or the specific
   constant name `_THEME_WORKERS`.
2. Within an 80-char window around the noun, one of these value-shapes
   must appear:
   - `_VERB_TO_N` — cap/limit/set/increase/reduce/… + optional filler
     + `to`/`at` + numeric literal.
   - `_FROM_N_TO_N` — `from N to M` with a config unit
     (`seconds`, `workers`, `retries`, etc.).
   - `_NOUN_COLON_ARROW` — `: N → M` (arrow syntax used in receipts).
   - `_NOUN_IS_N` — copula + numeric literal (`is 2 workers`,
     `= 90 seconds`).

Numeric literals are matched as digits or spelled-out `one`..`ten`
plus common decades (`twenty`, `thirty`, `ninety`).

## Enforcement
The gate CLEARS the sentence when any of these applies:

- The sentence contains an inline path/constant citation
  (`_PATH_INLINE`) — a repo-relative path under `state/`, `core/`,
  `scripts/`, `echo/`, `harness/`, `tests/`, `docs/`; a backticked
  `.py` filename; a backticked ALL_CAPS constant name; a backticked
  `name = value` assignment; or a backticked function call.
- The sentence contains a hedge (`_HEDGE_INLINE`): `(unverified)`,
  `(from memory)`, `appears`, `probably`, `I think`, `per memory —`,
  `might`, `may be`, `haven't checked`.
- A same-turn Read/Grep/Bash/Glob of a source file ran
  (`_read_of_source_ran`). "Source file" means the tool params or a
  file in `ctx.files_read` mentions a `.py` file or one of the source
  directories (`core/`, `scripts/`, `echo/`, `harness/`, `tests/`).

If none of the three channels clears the sentence, the gate returns a
warn-level violation naming the config-noun and instructing the model
to either (a) cite the source file/constant inline, (b) run the Read
before asserting, or (c) hedge.

## Deliberate blind spot
- Whole-turn exemption on any same-turn source Read — the gate does not
  verify that the read touched the *specific* file whose value is being
  claimed. That would false-positive when Shadow reads related code
  and correctly recalls an adjacent constant.
- Warn severity, not block — legitimate numeric claims about test
  counts (`9 tests passed`), receipts (`6:10 AM CT`), or item counts
  (`8 themes searched`) must remain frictionless. The config-noun +
  value-shape pairing is what distinguishes a config assertion from a
  telemetry number, but a false positive is still preferable to a
  block-severity friction spike on receipts.
- Does not attempt to validate that the cited constant *matches* the
  claimed value. A wrong-value cite still clears the gate. That blind
  spot is left to human review of the receipt.

## Relationship to other contracts
- `verification-vocabulary-gate` (FM-029, block) — sibling that owns
  the verb-lexicon channel (`verified`, `confirmed`, `validated`,
  `checked X`). Accepts a commit hash as provenance because a hash
  proves code changed. This gate handles the case where the *value* is
  the claim, and a commit hash does not prove the current value.
- `state-assertion-grounding` (FM-014, warn) — sibling covering
  `Yes/No/Confirmed` openers to the user's factual questions. Passes as
  soon as any read tool runs; does not care about *what* the value is,
  only that some read happened.
- `definitive-state-assertion-gate` (FM-025, block) — parent for named-
  referent claims about repo/state/capability. Extended in the same
  pass with a `tool_capability` Stage A pattern that catches
  "Codex/Claude CLI does not expose X" negations from memory.

## Escalation
Warn-level — the model receives a receipt but is not forced to
regenerate. Repeated warn fires on the same session mean the specific
parameter-claim shape is regenerating and should be lifted into a
Quick Reference bullet, or the gate's config-noun list needs
extending to cover the new knob-name token.
