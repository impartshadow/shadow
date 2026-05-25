---
name: bilevel-preplan
type: design-pattern
target: scripts/improve.py
---

# Bilevel Symbolic Pre-Plan (Round 0)

**Motivation:** BISON (McIlraith lab, 2025) shows that a fast symbolic planning layer
before neural execution reduces wasted exploration and improves generalization on
long-horizon tasks. Applied to /improve: Round 0 runs a cheap structured query that
produces a typed plan before the heavier neural rounds fire.

**Type:** Design pattern (not a Contract subclass — no check_pre/check_post)

**Trigger:** Fires at the start of every L2 attempt, before `_round1_explore`.

**What it produces:**
- `fm_cross_refs` — failure modes semantically adjacent to the target pattern
- `gate_type` — pre/post/session classification for the likely guard
- `candidate_mechanism` — one-sentence enforcement hypothesis to seed R1
- `key_signal` — the detection signal R1 should look for in response/action text

**Precondition:** Pattern dict and existing contracts string are available.

**Enforcement:** `_round0_symbolic_preplan()` in `scripts/improve.py`. Uses
`SUMMARY_MODEL` (haiku-class) — fast and cheap. Failure returns empty dict;
R1 proceeds without the seed rather than blocking.

**Recovery:** If JSON parse fails, log warning and skip — R1 degrades gracefully
to its prior open-ended exploration behavior.

**Escalation:** None — this is a non-blocking enhancement layer.

**Design notes:**
- Keep the preplan call under 300 tokens output; it is a *seed*, not a specification.
- R1 should treat the preplan as a starting hypothesis, not a constraint.
- If the preplan's `gate_type` conflicts with what R1 finds, R1 wins — the
  symbolic layer informs but does not override neural exploration.
