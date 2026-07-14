# Contract: loop-name-validation-guard

## Type
Post-response guard — deterministic enforcement via
`core/contracts.py:LoopNameValidationGuard`. Severity: `warn`.

## Failure mode
FM-022 — referencing a loop name or ID that does not exist in
`state/loops.json`. Examples: citing a retired loop as active,
inventing a loop ID, or carrying over a renamed loop's old name.

## Trigger
Post-check on response text. The regex
`\b(?:the|our|this|that|a|an|named|called)\s+([\w-]+(?:\s+[\w-]+)?)\s+loop\b`
extracts candidate loop references that follow a determiner
(e.g. "the arbor loop", "our echo loop", "this brief-production
loop"). Each candidate is checked against the lowercased set of
`id` and `name` fields from `state/loops.json`.

The determiner requirement (tightened 2026-06-17) drops natural-
prose mentions of "loop" that are not naming a specific Shadow
loop — phrases like "entries from each loop", "how the whole
loop", "with no Upwork loop" no longer fire because their
preceding word is not a determiner.

Code blocks (```fenced```) are stripped before scanning to avoid
firing on code that mentions loop identifiers.

A negation lookback (`_NEGATION_PREFIX_RE`) skips any match where
the 30 chars before the determiner contain "no / without / not /
retired / removed / deprecated" — Shadow is acknowledging the
loop's *absence*, not claiming it exists.

## Filtering
False-positive control is done with two frozensets:
1. `_STOPWORDS` — articles, pronouns, and generic loop descriptors
   ("the", "this", "main", "outer", "inner", "event", etc.).
2. `_COMMON_WORDS` — verbs/state descriptors that can't be loop names
   ("creates", "broken", "running", "stale") AND architectural pattern
   descriptors ("agentic", "tool", "gemini", "claude", "llm",
   "fallback", "retry", etc.). The latter group covers phrases like
   "the agentic tool loop" or "Claude fallback loop", which describe
   LLM-orchestration patterns, not Shadow's named loops.

A candidate fires only if it (a) is not pure stopwords, (b) contains
no common-word tokens, (c) looks slug-like, and (d) doesn't substring-
match any known ID or name.

## Recovery
Read `state/loops.json` and confirm the canonical ID/name. If the loop
was renamed, update the reference. If the loop is retired, label it
"retired" explicitly rather than implying it is active.

## Tests
`tests/test_contracts.py::TestLoopNameValidationGuard`. Regressions
covered: state descriptors ("broken loop"), known IDs ("arbor loop"),
architecture descriptors ("agentic tool loop", "Claude fallback loop"),
and true hallucinations ("frobnicator loop") which must still fire.

## History
- 2026-06-16: First gap-closer pass added state-descriptor filtering.
- 2026-06-17: Added architectural pattern descriptors after three
  false positives in 4h on "agentic Gemini loop" / "agentic tool loop"
  phrasing in Gemini-routing context.
- 2026-06-17b (gap-closer): Tightened `_LOOP_REF_RE` to require a
  determiner before the candidate, after 7 false positives in 4h
  on phrases like "entries from each loop", "how the whole loop",
  "with no Upwork loop". Added quantity adjectives ("whole",
  "entire", "single", etc.) to `_COMMON_WORDS` and added a
  `_NEGATION_PREFIX_RE` lookback for explicit absence statements.
- 2026-06-18 (gap-closer): Single-token filter on `id_words`. Loop
  IDs in `state/loops.json` are always single-token slugs (`arbor`,
  `awg-outreach`), so any candidate that still has multiple tokens
  after stop-word filtering is prose, not a name. Closes residual
  false-positive bucket: "QA stamps to loop", "entry to every loop",
  "the whole posting loop", "entries from each loop". 4 regression
  tests added.
- 2026-07-13 (gap-closer): Added "gates" (verb/plural of "gate", 2026-07-06
  addition) to `_COMMON_WORDS`, and added `_PARTICIPLE_COMPOUND_RE` to skip
  participle-descriptor compounds (`X-gated`, `X-driven`, `X-controlled`,
  `X-based`, `X-triggered`, `X-scoped`, `X-shaped`, `X-backed`, `X-powered`,
  `X-bound`, `X-paced`, `X-timed`, `X-keyed`). Both fired as FPs in the 4h
  window (2026-07-13 11:37 "that gates loop" + 11:38 "The receipt-gated loop").
  4 regression tests added.
