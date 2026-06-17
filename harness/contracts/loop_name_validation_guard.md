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
`\b([\w-]+(?:\s+[\w-]+){0,2})\s+loop\b` extracts candidate loop
references (e.g. "arbor loop", "echo loop", "the foo loop"). Each
candidate is checked against the lowercased set of `id` and `name`
fields from `state/loops.json`.

Code blocks (```fenced```) are stripped before scanning to avoid
firing on code that mentions loop identifiers.

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
