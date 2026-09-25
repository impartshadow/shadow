# repeated-dissatisfaction-verification-gate

**Type:** Code-enforced (Python `Contract` subclass in
`contracts/repeated_dissatisfaction_verification_gate.py`)
**Failure mode:** FM-002 (unverified claim) — ideation-loop axis
**Severity:** block

## Rule

The second unresolved "this still isn't right" signal on a thread is evidence
that the current abstraction level has been falsified. The next turn must
change **mode**, not content. Three exits:

1. **Verify externally** — run a search/fetch/read, or cite a concrete
   precedent, URL, path, commit, or named prior art.
2. **Say there is nothing to check against** — an explicit unverified hedge.
3. **Ask for the one specific fact** that would end the guessing.

A third bare reframing is blocked.

## Why

2026-09-20 #moonshot. the user signalled dissatisfaction five times over nine
hours — "We're not quite right" (13:04), "isn't this conversation enough of an
indicator?" (13:57), "How does this end up being different than a Facebook
group" (17:02), "I'm not in love with this yet" (19:09), "Nah. Regressing
again" (21:19). Each reply was prose-only and introduced a new metaphor:
community → repo → co-op → apprentice shop. The first external check
(OpenMined / ResearchHub as existing analogues) did not land until 01:04, and
only because the user happened to ask an unrelated operational question. Nothing
in the session would have broken the loop on its own — the pivot cost the user
five corrections and nine hours of attention.

The routing was correct throughout (`gpt-6-astra`, `channel_primary` — see
`state/model_fallback_events.jsonl`; the `claude_cli_failed` rows in that
window are `web_search`/`test` call sites, not conversational turns). This is
a mode-selection failure, not a model or routing failure.

2026-09-24 #moonshot recurrence: "This is over indexing on math proofs"
(02:35) and "Still not right" (02:41) were two signals six minutes apart, but
only the second matched `_DISSATISFACTION`, so the streak stopped at 1 and the
gate never engaged. `over-indexing` and `still indifferent` now count.

## Relationship to neighbouring gates

- [pushback_reverification_gate](../../contracts/pushback_reverification_gate.py)
  (FM-002) covers a **factual** challenge to a specific claim — it needs a
  checkable assertion to re-derive. This gate fires where there is no
  assertion at all: an open-ended thread where dissatisfaction is the only
  signal.
- [position_drift_under_pushback](position_drift_under_pushback.md) (FM-022)
  covers *conceding* under pushback. This covers *restating* under pushback.
- All three encode the same invariant: a correction from the user is evidence to
  act on, not a social cue to answer.

## Trigger

Fires on `check_post` when all hold:

1. The user message carries a **direction-dissatisfaction** signal
   (`_DISSATISFACTION`) or a **meta-level process challenge**
   (`_META_CHALLENGE` — "isn't this enough", "why do you keep", "stop
   asking"). Task-level corrections ("wrong Sumit", "that command failed")
   are deliberately out of scope; they have their own gates and a concrete
   thing to fix.
2. The per-thread unresolved streak reaches `_STREAK_THRESHOLD` (2).
3. The response takes none of the three exits and ran no verification tool.

## Streak accounting

State lives in `state/dissatisfaction_streaks.json`, keyed by channel, via
`core.state_io.update_json`. Conservative by construction:

- The streak **resets** whenever the turn changes mode (any of the three
  exits, or a verification tool call), or when the user themselves supplies
  new information (`_USER_NEW_INFO`: a URL, a "because", a named analogue like
  "it's kind of like an old school co-op"). A productive exchange never
  accumulates — only *unresolved* repetition reaches the threshold.
- A non-dissatisfaction turn leaves the streak **untouched** rather than
  clearing it, so interleaved chatter in the same channel cannot launder a
  live loop.
- Streaks older than 24h (`_STREAK_TTL_SECONDS`) are treated as cold: a signal
  the next day starts a fresh count.

## Recovery

Verify, hedge, or ask. Do not send another restatement of the same idea.

## Tests

`tests/test_repeated_dissatisfaction_gate.py`
