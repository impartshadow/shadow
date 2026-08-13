# Contract: spawn-lifecycle-claim-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:SpawnLifecycleClaimGuard`. Severity: `warn`.

## Failure mode
FM-014 (spawn/fleet sub-case). A response asserts lifecycle state about the
spawn fleet, the scheduler, or a specific episode ("capital was terminated",
"the fleet is rolling", "I'll continue autonomously", "continuous fleet
operation") without a same-turn read of the authoritative spawn state
(`state/spawn_registry.json`, `state/spawn_evidence.jsonl`) or a
scheduler/process check (`crontab -l`, `pgrep -f spawn_runner`).

## Origin
2026-08-06/07 accelerando thread. At 22:21 the user asked "What's next on the
accelerando list?" and Shadow answered that "the first episode produced no
external pull, so its capital was correctly terminated." The registry
actually held `verdict=continue` with $1 of $3 spent. Shadow self-corrected
70 seconds later after a live read, but the same shape recurred at 01:06
("I'll continue autonomously" — no recurring scheduler existed) and produced
the user's "This is why I have trust issues." Shadow logged a prose correction
into the decision log — "built does not mean running; any live-state claim
requires same-turn evidence" — but nothing forced the next lifecycle claim
to cite the registry or the scheduler.

`ActivityAssertionGroundingGuard` (sibling) fires only when the user *asks* an
activity question. The 22:21 and 01:06 turns were volunteered lifecycle
narrations in response to strategy questions — no activity trigger phrase in
the user's message. This guard closes that gap.

## Trigger
A response is scanned when `ctx.action == "respond"` and any of:
1. **First-person autonomy claim** matches `_FIRST_PERSON_AUTONOMY_RE`:
   "I'll/I will/I'm continue autonomously", "continuous fleet operation",
   "the fleet is rolling/running/live/recurrent/autonomous", "capital was
   (correctly) terminated/killed/reaped".
2. **Subject + lifecycle verb pair** within 120 chars: a fleet subject
   (`spawn/fleet/episode/scheduler/recurring trigger/the cron/the tick/
   spawn_registry/spawn_runner/spawn_fleet`) sitting inside a 120-char
   window of a lifecycle verb
   (`terminated/killed/reaped/retired/running/rolling/continuing/continues/
   continuous/scheduled/recurring/autonomous(ly)/live/active/idle/dormant`).
3. **Count-with-status claim** (`_COUNT_STATUS_RE`): a numeric count
   paired with "active/running/live/rolling/operating" (e.g. "46 running
   probes", "45 active spawns"). Added 2026-08-09 after the accelerando
   thread — a bare count is itself a lifecycle assertion even when the
   surface noun sits outside the subject vocabulary, because the count is
   what makes it a claim about live execution.
4. **Capability/gap claim** (`_CAPABILITY_GAP_RE`): "the missing
   layer/piece/mechanism is X", "it/Shadow/the fleet/accelerando cannot
   routinely/currently X", "no controlled/automated branching/selection/
   variants", "does not support parallel variants". Requires either a
   fleet subject in the response or a registry-backed capability concept
   ("controlled branching", "bounded variants", "shared evaluator",
   "promote the winner", "discovery loop", "accelerando") in the response
   or the user message. Added 2026-08-12 after the Discovery Loop replay
   where Shadow said accelerando's "missing layer is controlled branching"
   — a claim the registry (which already exercises exactly that shape)
   would have refuted. What the fleet is *capable of* is a live-state
   assertion, not architectural inference.

## Entity-table disambiguation (2026-08-09)
Even when the initial trigger is satisfied by a registry read, a count of
the shape "N running/active <noun>" WITHOUT one of the
`_ENTITY_DISAMBIGUATION_RE` phrases (`runnable records`, `eligible state`,
`registry records`, `no persistent worker`, `no active worker/runner
process`, `0 workers`, `scheduler-driven`, `not N continuously operating`,
`means eligible`, `work starts on schedule`) warns. Origin: 2026-08-08
18:25 — "46 running probes" passed the single-read check but conflated
registry-eligible records with live worker processes. Shadow itself
self-corrected 90 minutes later that "'46 running' means eligible state
records — not 46 continuously operating agents." The disambiguation is
what makes the number honest; without it the count reads as live
execution.

Suppressed by `_HEDGE_RE`: "not continuously", "not yet", "no recurring
scheduler", "overstated", "the scheduler does not exist", "i think", "might
be", "may be", "likely", "probably", "unverified", "from memory", "let me
check", "need to check", "checking now".

## Precondition satisfied by
Any of the following in the same turn:
- `files_read` contains a path matching `spawn_registry|spawn_evidence|
  spawn_runner|spawn_fleet`.
- Tool call (`Read`, `Grep`, `Glob`) with `file_path`/`path`/`pattern`
  matching the same regex as `_STATE_READ_RE`.
- `Bash`/`run_shell` command matching `_STATE_READ_RE`:
  `state/spawn_registry.json`, `state/spawn_evidence.jsonl`,
  `spawn_registry.py`, `spawn_runner.py`, `spawn_fleet.py`, `crontab -l`,
  `pgrep`, `ps -*`, `tail ... spawn/action_log/scheduler`.

## Enforcement
Warn-only. The guard logs to `state/contract_violations.jsonl`; post-session
audit surfaces recurrence. Blocking would false-positive on design/spec
conversations where the fleet is discussed abstractly (the entire 10:24–11:26
strategy thread in the same session used "spawn" and "running" repeatedly
without asserting live state).

## Recovery
Same turn:
1. `Read state/spawn_registry.json` (or `python3 -c "from core.spawn_registry
   import ..." `).
2. `crontab -l | grep spawn` — confirm scheduler presence.
3. `pgrep -f spawn_runner` — confirm active episodes.
4. Report exact partial state — active spawns, verdict, capital used,
   scheduler cadence, PIDs — instead of a summary verb.

The 01:21 self-correction is the canonical passing shape:
> "Not continuously — my prior answer overstated it. Episode 1 finished:
> 2 contacts, 0 replies. Episode 2 is running now: PID 268976. Capital:
> $2 of $3 authorized. Gap: no recurring scheduler exists."

## Related contracts
- `activity-assertion-grounding` — fires when the user asks a live-activity
  question; this guard fires when Shadow volunteers the claim.
- `state-assertion-grounding` — parent; passes when any read tool runs
  (git tools included). This guard's read set is narrower (spawn/scheduler
  reads only, not git).
- `live-state-claim-guard` — external-state claims (prices, news, weather).
  Same failure shape, different subject class.
