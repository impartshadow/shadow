# Contract: activity-assertion-grounding

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:ActivityAssertionGroundingGuard`. Severity: `warn`.

## Failure mode
FM-014 (activity sub-case) — assert-from-git-history. A response answers a
live-activity, shipping, or resource-consumption question definitively, but the
only ground-truth tools that ran this turn were git-history reads (`git log`,
`git status`, `git rev-parse`). Git tools answer "what was committed", not
"what is currently running or consuming quota".

## Threat model
The 2026-07-13 evening incident is the canonical case. the user directed Shadow to
stop autonomous shipping at 7pm CT for dinner. Shadow gated the *scheduled
autonomous-worker* execution path, unit-tested it, and called it "durable" —
without enumerating the other concurrent Claude execution paths (background
CLI, previously-launched sessions). Post-cutoff, two commits landed at 7:21pm
and 8:20pm; Shadow itself surfaced this at 01:32 but treated it as a local
enforcement gap rather than a trigger for re-audit. At 02:45 the user asked
"Anything else ship?" and Shadow answered:

> "No. The tenant-status dedup fix (`0fa3110b`) was the last shipment, pushed
> at 8:33 PM CT. There is unfinished local work on execution snapshots, but it
> has not been committed or shipped."

`git log` was consulted; no `pgrep`, `ps`, session-ledger tail, or quota
check ran. The response even acknowledged unfinished local work but did not
investigate its source — evidence of an active process, dismissed as inert.
the user then supplied ground truth ("Something was shipping. We capped out our
5-hour window") and Shadow finally discovered an active Claude run had been
editing files at 9:12pm and consumed quota until the 5-hour cap hit at 9:32pm.

Both `StateAssertionGroundingGuard` and `stale-state-assertion-guard` passed
the response: a read had happened. The gap is that the read didn't match the
*shape of the question*. This guard closes that gap for the specific class of
"live-activity / shipping / resource consumption" questions.

## Trigger
A response is scanned when **all** of:
1. `ctx.action == "respond"`.
2. The user message contains activity/shipping/consumption grammar:
   - `anything (else) ship(ped|ping)?`, `anything (else) running/going/active/happening/new/left`
   - `still|currently running/working/shipping/going/active/executing`
   - `what/which is/was/are/were/has/have running/shipping/shipped/consumed/using/consuming`
   - `how much quota/usage/claude/capacity/headroom/window/cap`
   - `consumed/capped/hitting/hit (out) the/our/a quota/window/limit/cap/5-hour/weekly`
   - `is/are (anything|something|it|they|shadow|the worker|the scheduler|claude|codex) (still) running/working/shipping/going/active/executing/consuming`
   - `did/has/have (anything|something|we|it|they|shadow) (else) ship(ped)?/run/ran/consume(d)?`
3. The response (after `_strip_non_action_text`) contains at least one
   definitive-assertion pattern:
   - Leading `Yes.` / `No.` / `Nothing.` / `Nope.` / `None.` / `Confirmed.`
   - `nothing/no (other|additional|new) (else) ship(ped|ping)?/ran/running/active/happening/consumed`
   - `the (last|latest|only|final) ship(ment|ping)?/run/commit/autonomous was/is/remained`
4. The response contains no hedge (`not sure`, `unsure`, `i think`,
   `might be`, `may be`, `likely`, `probably`, `can't tell`, `don't know`,
   `unverifiable`, `let me check`, `need to check`, `checking now`, ...).

## Enforcement
If all four triggers match, the contract requires at least one process/session/
quota-state read this turn. Any of the following satisfies:

- MCP tool: `list_async_tasks`, `list_background_tasks`, `get_loop_state`
  (and `mcp__shadow__*` mirrors).
- Bash / `run_shell` command whose text matches the process shell regex:
  `pgrep`, `pkill`, `ps -* / ps a/e/f/u/x`, `jobs`, `kill`, `systemctl`,
  `journalctl`, `crontab -l`, `top`, `htop`, `lsof`, `/proc/`, `ccusage`,
  `claude … status/usage/quota`, or a `tail`/`cat` of `action_log`,
  `bot_restart`, `last_bot_start`, `running_sessions`, `active_sessions`,
  `claude_usage`, `quota_state`, or `scheduler_state`.

The check inspects both `ctx.tool_calls` + `ctx.tool_params` and, as a
secondary source, `ctx.tool_call_results` (some execution paths populate one
and not the other). Git tools are deliberately excluded — that is the whole
point of the guard.

If no process/session/quota read is found, the response carries a warn-level
violation. If the response text itself acknowledges uncommitted/unfinished/
pending work (via the `_UNCOMMITTED_ACK_RE` pattern), the violation message
appends an additional line calling out that Shadow saw the signal and
dismissed it as inert.

## Deliberate blind spot
Cannot catch *read-the-wrong-process-source* — a `pgrep` returning stale PIDs
or a `tail` of the wrong log. Warn, not block, for the same reason as the
sibling: legitimate answers may come from prior conversation ("I already know
Claude is running — did anything ship from it?") and blocking would false-
positive on those.

## Recovery
In the same turn, run one or more of:

- `pgrep -f '(claude|codex|python.*worker)'` — check for active autonomous
  sessions.
- `tail -20 state/action_log.jsonl` — check most recent action ledger entries.
- `tail -5 state/bot_restart_log.jsonl` — check whether the bot has restarted.
- `ccusage` or `claude … status` — check quota-window state.

Prefix the answer with the observed process/quota state:
"pgrep shows N active claude sessions; last log line at HH:MM; so <answer>."

If the answer truly comes from in-context user content (the user just told Shadow
what's running), prefix with the source so the user can audit.

## Relationship to other contracts
- `state-assertion-grounding` (parent): passes when ANY read tool runs. Git
  tools satisfy it. This guard is the tighter sub-case for activity questions
  where the tool signature must include a process/quota check.
- `stale-state-assertion-guard`: fires on definitive process-state *claims*
  ("X isn't running", "Y was already deleted"). This guard fires on definitive
  answers to activity *questions* even when the response doesn't use those
  specific claim phrases.
- `self-stoppage-claim-guard`: fires on sentence-initial 1st-person past-tense
  stoppage claims ("Stopped the refactor"). Different surface form; same
  family of "asserting state without checking process".

## Escalation
Warn-only — no auto-block, no the user surface. If this guard fires ≥3 times in a
4h window on distinct activity questions, promote a Quick Reference rule
targeting the specific surface form that keeps regenerating.

## Origin
2026-07-13 autonomous-shutdown incident. See CLAUDE.md Quick Reference rule
extension to rule 55 (activity sub-case) and this reflect-repair commit for
full context.
