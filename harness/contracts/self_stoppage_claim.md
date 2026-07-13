# Contract: self-stoppage-claim-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:SelfStoppageClaimGuard`. Severity: **block**.

## Failure mode
FM-022 — self-referential 1st-person past-tense stoppage claim asserted from
memory instead of a same-turn ground-truth read.

## Threat model
`StaleStateAssertionGuard` covers 3rd-person passive stoppage predicates:
"X was already stopped", "Y is dead", "Z has been dark". It does NOT catch the
sentence-initial 1st-person past-tense action form — "Stopped the client
refactor", "Paused the extraction loop", "Halted the increment run", "Aborted
the pipeline". That surface form landed a false claim into #shadow-hq on
2026-07-12T21:43: the user sent bare "Go" to continue an active refactor loop,
Shadow replied "Stopped the client refactor. Latest Innermost Loop: ..." and
pivoted to a Substack digest summary. Increment 4 (Codex adapter, commit
`199fd12f`) had already shipped; the "Stopped" claim was fabricated. the user only
surfaced the contradiction ~4h later by quoting the increment-3 receipt and
asking "Did you do this?"

The upstream mechanism is the same generation-without-verification family
named by rule 55: a definitive-tense claim presented without a same-turn read.
This guard closes the specific gap where the claim is Shadow narrating its
own stoppage of an in-flight multi-step task.

## Trigger
A response is scanned when the stripped response text (see
`_strip_non_action_text`) contains:

1. A sentence-initial or post-sentence-boundary token matching
   `(i\s+)?(stopped|paused|halted|aborted|cancelled|shut down|killed|
   suspended|terminated|ended)`.
2. Followed by `the|our|my|this`.
3. Followed (optionally through ≤3 modifier words) by a task-subject noun:
   `client|refactor|extraction|migration|pipeline|increment|iteration|cycle|
   watcher|monitor|scan|experiment|import|generation|distribution|publish|
   scout|engagement|farming|training|deployment|research|analysis|audit|
   sweep|session|run|job|task|thread|workflow|series|flow|loop|sequence|
   rollout|backfill|batch|worker|consumer|producer|orchestration`.

## Enforcement
Blocks unless one of the following ran this turn:

- `Bash` or `mcp__shadow__run_shell` — covers `git log/status/rev-parse`,
  `pgrep`/`ps`/`kill`, `systemctl`, `crontab`, `jobs`.
- `mcp__shadow__get_loop_state` — direct loop/increment ledger read.
- `Read` / `Grep` / `Glob` / `mcp__shadow__read_file` /
  `mcp__shadow__list_directory` where the path targets `state/` or `memory/`
  (task ledger / handoff).

`browse_url` and generic reads of unrelated paths are deliberately excluded:
fetching a Substack URL does not verify whether Shadow's local task loop
actually stopped.

## Carve-outs
Hedge markers render the claim conditional and pass:
`would have stopped`, `if ... stopped`, `had stopped`, `almost stopped`,
`nearly stopped`, `about to stop`, `was wrong`, `overstated`, `retract`,
`correction`, `previously said`, `my prior response`, `earlier I said`.

## Recovery
Before claiming you stopped/paused/halted a multi-step task, run one of:
- `git log --oneline -5` (no new commits since the task started ⇒ genuinely
  stopped)
- `pgrep -f <task_name>` (empty ⇒ no process running)
- Read the relevant `state/` ledger for the loop/increment sequence.

Cite the output. If nothing actually stopped, don't claim it did — continue
the task or state the real blocker.

## Relationship to other contracts
- `stale-state-assertion-guard` covers 3rd-person passive stoppage predicates
  ("X is dead", "Y has been stopped"). This guard is the 1st-person
  action-form sibling.
- `state-assertion-grounding` fires when the user asks a factual question and no
  read backs the answer. This guard fires regardless of user turn shape —
  bare continuation directives ("Go" / "Keep going") never trigger
  state-assertion-grounding, so a distinct gate is required.
- `unbuilt-guarantee-guard` and `commit-hash-verification` cover architecture
  and completion claims; this guard covers stoppage claims specifically.

## Escalation
Block-severity — the response is rejected pre-send. The trace log lets
session_audit surface any recurrence pattern that would justify tightening
the pass set further (e.g. dropping generic `Bash` if unrelated shell calls
prove to be the false-positive path).
