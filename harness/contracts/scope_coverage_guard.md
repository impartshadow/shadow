# scope-coverage-guard (FM-013)

Pre+post contract that resolves referents, extracts scope slots from the user
turn, and blocks responses that drop slots. Forces a bounded retry naming the
uncovered slots.

Sub-modes:
- **FM-013a** — referent-drop: user turn contains a strong resolver token
  ("clean this up", "handle these", "address them", "the above") but no thread
  source (Discord reply, Telegram reply, inline quote, prior numbered list) binds
  the referent. Response must open with a disambiguation restatement.
- **FM-013b** — slot-drop: multi-slot ask; response covers some slots but drops
  others. First fire is `block` (forces retry); repeat fire on the retry is
  `warn` (escalates to pattern-analysis).

## Type
Code-enforced (`ScopeCoverageGuard` in `core/contracts.py`).

## Trigger
`_should_fire` returns True when any of:
- ≥ 2 structural asks (numbered items, multiple verbs joined with and/then/also,
  ≥ 2 question marks)
- `action_params.referenced_message` or `reply_to_message` is present
- The turn contains a `> quoted` block
- Short message (< 60 chars) with any resolver token ("this", "that", "it",
  "them", "those", "the above", etc.)

## Precondition
FM-013a fires only on **strong** resolver tokens ("the above", "all of it",
"clean this up", "handle these", "address them", "handle this/that/them",
"close these/them"). Weak/casual resolvers ("this", "that", "it", "them" alone
in a short turn) do NOT fire — they were 14 false-positive warns in 4 h on
2026-07-17 before the split.

FM-013b fires when `_extract_slots` returns ≥ 2 slots AND the response fails
`_slot_covered` (lemma-overlap ≥ threshold) for at least one slot.

## Enforcement
- `check_pre`: emits FM-013a `warn` when strong resolver token is unresolved.
  Also populates `ctx.action_params["scope_slots"]` for post-check to consume.
- `check_post`: first drop emits FM-013b `block` with recovery instructions
  naming covered / dropped slot IDs and text; a second drop after
  `scope_retry_attempted=True` emits FM-013b `warn`.

## Recovery
- **FM-013a**: open with `Re: your ask — I read this as X. Confirm or correct.`
  before executing.
- **FM-013b (block)**: re-emit the response addressing every slot; explicitly
  defer any blocked slot with `slot [N] blocked: <reason>`.
- **FM-013b (warn on retry)**: log to `state/contract_violations.jsonl` for
  pattern review.

## Escalation
Repeat FM-013b `warn` fires across sessions surface via `session_audit.py` —
Haiku grades whether the retry hint is being ignored.
