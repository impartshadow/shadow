# Contract: ownership-ask-execution-gate

**Type:** Code-enforced (Python `Contract` subclass in `core/contracts/conversation.py`)
**Failure mode:** FM-011 (explain-instead-of-act)
**Severity:** block

## Origin

2026-09-17 #shadow-hq. the user: *"I don't know why you're always trying to pitch
me... You should be able to handle this."* The correction landed in each of the
next three replies and the substitution repeated anyway:

1. "I've saved that correction" — no work.
2. An adjacent learning-loop bug fix, pushed, reported as "a concrete repair"
   while conceding it was not the ask.
3. A signature checker delivered to an external GitHub issue; when the user asked
   "does this fit what we were talking about", Shadow conceded it "reached for
   something concrete to report before establishing it was the right thing to
   pursue."

Each cycle was answered with language, not a gate. This is the gate.

## Trigger

Two branches share one trigger surface. System injections (`[System:` onward),
quoted Shadow text, and channel/reply tags are stripped before the user's text is
read, and a reply naming a hard blocker always passes.

**Branch A — explanation-only.** Fires when the user's turn is a rejection demand
(`you should be able to handle this`, `handle this yourself`, `pitch me`,
`stop pitching`, `you're still doing it`, `why do you keep ... half ...`), an
autonomy demand (`do it yourself`, `own this`), or an accountability ask
(`so what did you do`, `did you complete the task`) **and** the reply cites no
artifact (no resolving commit hash, existing run path, test output, URL or
platform id) **and** nothing was acted on this turn (no file edit, no non-read
tool call) **and** the reply speaks in intent / saved-correction language.

**Branch B — unjustified artifact.** Fires only on a *rejection* demand, when
the reply does cite artifact evidence but states no comparative choice
(`chose this over ...`, `instead of ... because ...`, `over the alternatives`).
Autonomy demands and accountability asks do not arm this branch: a first
artifact against "do it yourself" is ordinary progress.

**Branch C — principle saved, not applied (added 2026-10-24).** Fires when
the user states a standing rule (sentence-initial `always`/`never`/`prefer`,
`general principle`, `as a rule`, `from now on`) **and** the reply reports
writing the rule down (`saved as a standing principle`, `noted the correction`)
**and** either admits the application is unbuilt (`isn't built yet`, `still
open`, `note that as a to-do`) or speaks in intent language **and** nothing
beyond memory bookkeeping happened this turn. `record_decision`,
`apply_correction`, `remember` and `memory_write` do not count as acting on
this branch — the memory write is the failure shape, not the fix. A plain
state report with no saved-rule language ("No. Changing it now.") passes, so
the honest admission is never what gets blocked.

Origin: 2026-10-24 #finance. the user: *"Yeah. Always try to fix upstream"* right
after Shadow shipped a blocklist gate it had itself called whack-a-mole with
an upstream fix proposed. Reply: *"Saved as a standing principle … the
upstream fix isn't built yet. I'll note that as the next iteration."* the user
then had to ask *"did you change the prompt guidance yet?"* and finally *"Fix
it"* before the upstream change was made. Three routing turns for one
instruction. The same principle now also lives upstream as a line in
`conversation_rules()` (`core/identity.py`): apply a stated principle to the
work in view in the same turn; recording it is not the fix.

## Why this shape

Branch B deliberately does not key on the self-negating disclaimer Shadow kept
attaching ("that's a concrete repair, not proof that..."). Blocking honesty
would be satisfied by deleting the honest sentence, which is worse than the
original failure. It keys on the missing *justification* instead, which can
only be satisfied by doing the comparison.

## False-positive calibration

Replayed over all 4,757 user→assistant pairs in
`state/discord_transcript.jsonl`: 4 fires, all four the replies the user objected
to in the origin incident. Branch C replayed 2026-10-24 over 5,619 pairs:
2 fires, both the 02:26 and 02:30 #finance replies from its origin incident. An earlier draft armed on any `why do you keep ...`
and fired on 7 legitimate root-cause answers ("why do you keep pushing my daily
update after restart?"); that pattern was narrowed to the `half things` form.

## Recovery

- Branch A: take the next bounded action this turn and report the decision
  made, the action taken, and the result observed — or reply with only the one
  question that unblocks it, or name the hard blocker.
- Branch B: state what you chose, what you chose it over, and how it advances
  the question the user actually asked. If that cannot be stated, hold the artifact
  and answer the open question.

## Related

- `core/request_binding.py` — the completion-evidence half of the same
  mechanism: evidence may only close the request it traces to.
- `harness/contracts/persistent_correction.md`, `direct_ask_dismissal` —
  adjacent FM-011 surfaces.

## Tests

`tests/test_contracts.py::TestOwnershipAskExecutionGate` (10 cases, including
the three origin replies and the diagnostic-question carve-out).
