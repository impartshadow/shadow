# Contract: classifier-fix-repro-guard

**Type:** Code-enforced post-check (warn severity)
**Failure mode:** FM-027 (trigger-repro sub-case of fabricated verification claim)
**Location:** `core/contracts.py` → `class ClassifierFixReproGuard`

## Trigger

Response text asserts that a fix targeting an **externally-triggered classifier /
refusal / rate-limit / policy block** is "live", "fixed", "won't fire", "no
more refusals", or equivalent, AND no same-turn reproduction of the trigger
condition is present in either the response text or the tool calls.

## Precondition

For a violation to fire, ALL of:

1. **Completion signal** matching `_COMPLETION_RE` — anchored to fix/refusal/
   classifier vocabulary. Examples: "fix is live", "live for tonight", "won't
   fire", "no more refusals", "stops the refusal", "the classifier is fixed",
   "policy refusal is resolved".
2. **External-trigger target** matching `_EXTERNAL_TRIGGER_RE` — e.g. "AUP",
   "usage policy", "anti-distillation", "reverse engineering", "duplicating
   model outputs", "policy classifier", "refusal", "blocked by", "rate limit",
   "429", "content filter", "safety filter", "trigger phrase".
3. **No repro evidence** — neither
   (a) an in-text signal matching `_REPRO_TEXT_RE` ("reproduced the trigger",
       "live-fire probe passed", "replayed the blocked draft through the current
       gate", "trigger-condition probe passed", "probe mode ran clean", "now
       passes / still blocked"), NOR
   (b) a same-turn Bash/`run_shell` tool call invoking a repro/replay/probe
       entrypoint matching `_REPRO_SCRIPT_RE` (`scripts/replay_blocked_drafts.py`,
       `scripts/counterfactual_replay.py`, `_run_autonomous_session(probe_only=True)`,
       `pytest ...probe|replay|live-fire|aup`).

## Carve-outs (don't fire)

- Response contains an explicit hedge — "not verified live yet", "watch gate",
  "unverified", "can't reproduce locally", "waiting for the next run", "repro
  deferred/pending". The writer is already labelling the claim tentative.
- Response is meta-discussion of this contract itself (docstring/design/test
  authoring).
- No completion signal is present — the response is describing a fix in
  progress, not declaring it done.
- No external-trigger vocabulary is present — the fix is not classifier-gated,
  so unit-test-green is legitimate evidence and `CompletionArtifactContract`
  handles it.

## Enforcement

Warn severity. The guard does not block; it appends to
`state/contract_violations.jsonl` and emits a trace event so
`scripts/session_audit.py` and the gap-closer can loop on the class.

Blocking would false-positive on legitimate fixes where the classifier is
server-side, the replay wrapper doesn't exist yet, or the affected quota is
exhausted — cases where a same-turn live-fire attempt genuinely isn't
possible. The correct posture there is an explicit hedge (which the carve-out
recognises), not a blocked response.

## Recovery

1. In the same turn, run the repro the fix is trying to prove. Preferred paths:

    | Fix target | Repro command |
    |---|---|
    | Pre-send contract gate (`persistent-correction`, `behavioral-haiku-guard`, `partial-evidence-flag`) | `python3 scripts/replay_blocked_drafts.py --since 24h` |
    | Nightly AUP / policy classifier | `python3 -c 'from scripts.nightly import _run_autonomous_session; print(_run_autonomous_session(probe_only=True))'` |
    | Rate-limit / 429 handling | live curl of the affected endpoint through the fixed retry path |
    | Bespoke classifier fix | write a `scripts/_tmp_<name>_probe.py` that feeds the failing input through the fixed code path and prints the verdict |

2. Paste the pass/fail verdict inline before using "live"/"fixed"/"shipped".

3. If the repro genuinely isn't possible in this turn, say so explicitly
   ("watch gate through <date> — no local repro path exists yet") — the hedge
   carve-out will pass the response.

## Related contracts

- `completion-artifact` (FM-027) — verifies cited paths exist and cited pushes
  cite resolving SHAs. Handles pure-logic completion claims. This guard is the
  behavior-gated sibling.
- `post-commit-audit` (FM-027) — commits in a response must include a
  verification step. Unit tests satisfy it for logic fixes but not for
  classifier fixes; this guard closes that gap.
- `fabricated-verification-claim` (FM-027) — blocks "verified via <tool>"
  surface forms without a same-turn matching tool call. Different surface
  form; same failure family.
- `state-assertion-grounding` (FM-014) — warns on definitive state answers
  with no ground-truth read. Fires only on the user's question flow, not on
  unsolicited completion narration.
- `verify-before-push` (harness/contracts/verify_before_push.md) — general
  push-verification rule. This guard adds the specific classifier/refusal
  clause referenced in the CLAUDE.md Quick Reference verification family
  (rules 3, 29, 30, 41, 42, 50, 55).

## Origin

2026-07-16T11:25 `#moonshot`. Shadow shipped `ef1cb476` — sanitizer, reframing,
and retry fallback for AUP-classifier refusals in `scripts/nightly.py` — with
"63 nightly-related tests pass" and reported **"Fix is live for tonight."**
the user asked at 11:43 to "try a run now while we're monitoring." At 12:01
("Did this run?") and 12:05 ("Ha") the exact same AUP refusal fired twice on
trivial live messages. The real root cause (`7ab836c5`, 12:11) was accumulated
poisoned session context in the running Moonshot Claude session — not prompt
phrasing. Unit-test-green was cited 35 min before the very failure the fix
claimed to have stopped.

The upstream mechanism this guard changes: a completion claim about a
classifier fix now must carry same-turn evidence that the *classifier itself*
accepted a trigger case, not merely that the fix's *code* passed a self-scored
test suite.
