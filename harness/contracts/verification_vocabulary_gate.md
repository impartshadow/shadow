# Contract: verification-vocabulary-gate

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:VerificationVocabularyGate`. Severity: `block`.

## Failure mode
FM-029 (evidence layer) — assertive verification vocabulary without
provenance. The response uses `verified`, `confirmed`, `validated`, or
`checked <object>` as a statement of fact, but nothing in the same turn
backs the claim: no inline citation, no file path, no commit hash, no
tool call, no hedge.

## Threat model
The umbrella "same-turn read" family (Quick Reference rules 3, 29, 30,
41, 42, 50, 55, 58) handles factual claims, retrospective narration, and
completion claims — but the fastest path to a hollow assertion is a bare
verification verb: "verified the config", "confirmed the send landed",
"validated the flow". These verbs *feel* like receipts; they aren't.
The state-assertion-grounding sibling covers the `Yes/No/Confirmed`
opener grammar. This gate covers verbs anywhere in a response — mid-
sentence narration is the pattern the sibling misses.

## Trigger
A response is scanned when `ctx.action == "respond"` and `ctx.response_text`
is non-empty. Within each sentence (fenced code blocks stripped; other
regions preserved to keep provenance visible):

1. `_LEXICON` matches `verified`, `confirmed`, or `validated`.
2. `_CHECKED_OBJ` matches `checked <object>` where the object is a bare
   noun (not `checked in`, `checked out`, `checked with`, etc.).
3. `_NEGATION_BEFORE` excludes candidates preceded by `not`, `never`,
   `un-`, `isn't`, `wasn't`, `to be`, etc.
4. `_WHITELIST_PHRASES` masks known non-assertive uses (`twitter
   verified`, `verified badge`, `verified checkmark`, `verified by
   visa`, `unconfirmed`, `to be confirmed`).

Sentences containing a `?` are skipped (questions, not assertions).

## Enforcement
For each candidate sentence, provenance can come from any of:

- `_PROVENANCE_INLINE` in the sentence or the immediately preceding one
  (bracketed `[source:...]`, a repo-relative path under `state/`, `core/`,
  `scripts/`, `echo/`, `harness/`, `memory/`, `drafts/`, `tests/`, `docs/`,
  a 7–40 char hex hash, an `http(s)://` URL, or the word `pytest`).
- `_HEDGE_INLINE` in the sentence (`(unverified)`, `(from memory)`,
  `appears`, `probably`, `I think`, `per memory —`).
- `_same_turn_tool_provenance` — any tool from `_PROVENANCE_TOOLS`
  (`Read`, `Grep`, `Bash`, `Glob`, `browse_url`, `web_search`, and
  their `mcp__shadow__*` mirrors) ran this turn.

If none of the three provenance channels applies to the sentence, the
gate blocks the response with a recovery message naming the offending
token and instructing the model to either (a) add an inline citation to
the source consulted, (b) soften to a hedge, or (c) remove the claim.

## Backtick-preserved second pass
The initial `_strip_quoted_and_code` pass removes backtick-quoted
inline text so vocabulary matches don't false-positive on quoted code.
That strip also removes inline provenance signals (backtick-quoted
paths and hashes) from the sentence stream. The gate compensates with
a parallel provenance-visible pass (`_strip_fenced_only`) that removes
only triple-fenced code blocks. When the sentence-index alignment
between the two streams holds (verified by length comparison), a second
provenance check runs against the backtick-preserved sentence and can
clear the candidate. If alignment drifted (rare), the second check is
skipped rather than falling back to a whole-response provenance sweep —
that would exempt any provenance marker anywhere in the response and
defeat the gate. Added 2026-07-19 to fix an FP cluster where a response
citing `state/foo.json` in backticks was blocked because backticks were
stripped before the provenance search.

## Recovery
The offending sentence gets one of:

1. An inline citation to the source consulted this turn — the same
   provenance tokens the gate recognizes (`state/path.json`, a full
   commit hash, an URL, or a bracketed `[source: ...]` cite).
2. A hedge that acknowledges the claim is unverified —
   `(unverified)`, `(from memory)`, `appears`, `probably`, `I think`,
   `per memory —`.
3. Removal of the claim entirely if no source was consulted and the
   assertion isn't load-bearing.

Never keep the assertive verb without evidence.

## Deliberate blind spot
The gate does not fire on questions, negations, or the whitelisted
compound phrases. It does not attempt to validate that the cited
provenance is *correct* — a wrong-file cite still clears the gate.
That blind spot is the state-assertion-grounding sibling's territory
(and, for capability/wiring claims, capability-scope-assertion-guard's).

## Relationship to other contracts
- `state-assertion-grounding` — sibling that catches definitive
  `Yes/No/Confirmed` openers to factual questions when no ground-truth
  read ran. This gate covers the verb lexicon anywhere in a response,
  not just openers.
- `claim-evidence-binding-guard` — parent FM-029 gate; owns the broader
  claim-without-evidence family. This gate is the vocabulary-specific
  cover.
- `partial-evidence-flag` (FM-026) — fires on definitive research claims
  without a citation. Complementary — that gate cares about claim shape,
  this one about verb shape.
- `definitive-state-assertion-gate` (FM-025) — blocks pre-send when a
  named referent lacks a same-turn read. This gate is post-check and
  triggers on the verb lexicon regardless of referent shape.

## Escalation
Block-level — the model must regenerate a compliant response. Repeated
regenerations on the same turn are recorded in
`state/contract_violations.jsonl`; a persistent block across sessions
means the upstream prompt is still emitting bare verification verbs
and the specific pattern should be lifted into a Quick Reference bullet.

## Recent activity
2026-07-20 gap-closer window: **4 fires in 4h (block)**, **18 fires in
24h**, **30 fires in 72h**. All 4 recent fires cited `verified` or
`confirmed` as the offending token. The umbrella provenance rules
(CLAUDE.md rules 3, 29, 30, 41, 42, 50, 55, 58) cover the semantic
requirement, but none of them names the verb-token lexicon that this
gate uses to enforce. Missing harness doc filled this pass so the gate's
design is discoverable and the FP-repair history (2026-07-19 backtick-
preserved second pass) has a home.

2026-07-21 gap-closer window: **8 fires in 4h (block)**, **15 fires in
24h**. Fires: 00:44 (`Verified`), 00:53 (`verified`), 02:42
(`verified`), 03:20 (`confirmed`), 03:24 (`confirmed`), 03:27
(`Verified`), 03:41 (`verified`), 03:42 (`checked`). Cleared the
≥6/4h "promote to Quick Reference" trip criterion documented in
`harness/contracts/state_assertion_grounding.md`. Rule 59 added to
CLAUDE.md this pass — the mid-sentence verb-lexicon rule was not
visible at generation time (rule 55 focused on opener grammar only),
so the pattern regenerated. Rule 59 names the verb tokens and
provenance channels explicitly.
