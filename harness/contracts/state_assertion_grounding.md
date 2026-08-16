# Contract: state-assertion-grounding

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:StateAssertionGroundingGuard`. Severity: `warn`.

## Failure mode
FM-014 (process layer) — assert-from-memory. A response answers a factual /
state question definitively, but no ground-truth-reading tool ran this turn,
so the answer is sourced from memory or stale conversation context rather
than the live system state. The same owner handles bare concurrence with a
factual framing (for example, opening with “you're right”) without a live read.

## Threat model
The "Zelle is the rent" / "no rent confirmation" / "X is dark" corrections
all share the same root cause: the user asks a verification-shaped question
("is X ...?" "did Y ...?" "how many ...?"), Shadow answers `Yes/No/Confirmed`,
and the only thing Shadow read was its own short-term context. The answer
sounds authoritative but is unanchored.

Probe-based contracts (e.g. `claim-verification`, `completion-artifact`) only
fire when a claim names a resolvable referent — a SHA, a file path, a
collection. The misses that recur do not name anything probe-able, so no
ground-truth check exists for them. The only remaining lever for that class
of failure is *process*: require that SOME ground-truth-reading tool ran
this turn before a definitive state assertion can ship.

## Trigger
A response is scanned when **all** of:
1. `ctx.action == "respond"`.
2. The original user message contains state/factual-question grammar
   (`is`, `are`, `did`, `does`, `has`, `have`, `where`, `when`,
   `how many`, `which`, `right?`, `correct?`, `isn't`, `aren't`, ...).
3. The response (after `_strip_non_action_text`) contains at least one
   definitive-assertion pattern:
   - "confirmed" / "verified"
   - "no/nothing/zero <noun> in/on/found/exists/present"
   - "the/most recent/last/latest <noun> is/was/are/were"
   - "isn't / aren't / wasn't / weren't / is not / are not"
   - Leading "Yes." / "No." / "Correct." / "Confirmed." / "Wrong."
4. The response contains no hedge (`not sure`, `unsure`, `I think`,
   `might be`, `may be`, `likely`, `probably`, `can't tell`,
   `don't know`, `unverifiable`, `I'd have to check`).
5. The candidate claim does not name a probe-resolvable referent — if a
   probe target (SHA, path, collection) is present, the probe contracts
   already cover it and this guard defers.

## Enforcement
If all five conditions are met, the contract checks `ctx.tool_calls` for at
least one tool from a permissive read-tools allowlist that includes
`Read`, `Grep`, `Glob`, `Bash`, `run_shell`, `read_file`, `browse_url`,
`web_search`, `memory_search`, `discord_history`, `recall_episode`,
`session_search`, `cross_surface_recall`, `trace_query`,
`list_async_tasks`, `list_directory`, plus the `mcp__shadow__*` mirrors.

If no read tool ran this turn, the response carries a warn-level violation:
"Definitive state assertion answering the user's factual question, but no
ground-truth-reading tool ran this turn — this answer is from memory/stale
context, not a live read."

## Deliberate blind spot
The contract cannot catch *read-the-wrong-source* — a turn that reads Gmail
when it should read Discord, or reads a stale cache when the live source
diverges. It catches assert-from-memory only. (The stale-cache half of this
blind spot is now covered for state files by `dead-source-citation-guard`,
added 2026-07-07 after the echo_post_log incident; see
`dead_source_citation.md`.) The check is `warn`, not
`block`, because a definitive state claim with no backing read is *suspect*,
not *proven wrong*; blocking would false-positive on answers the user legitimately
provided in the conversation context one or two turns earlier.

## Recovery
Run a read against the actual source (file, log, API, dashboard) in the same
turn and cite the output. If the answer truly does come from in-context user
content, prefix the assertion with the source so the user can audit
("Per your 14:02 message, ..." / "Your last screenshot showed ...").

## Relationship to other contracts
- `claim-verification` / `completion-artifact` / `commit-hash-verification`
  cover the *probe-resolvable* claim space (SHAs, paths, collections).
  This guard covers everything those miss.
- `partial-evidence-flag` (FM-026) fires on definitive *research* claims
  without a citation; state-assertion-grounding is the *factual/system-state*
  analogue for the same root cause.
- `stale-state-assertion-guard` extends this for live-process / runtime claims
  ("X isn't running", "Y was already deleted"); see CLAUDE.md Quick Reference
  rule #37(a).
- `activity-assertion-grounding` (sibling, added 2026-07-14 after the
  autonomous-shutdown incident) covers a distinct sub-case: definitive answers
  to *live-activity* questions ("anything else ship?", "did we consume quota?",
  "is anything still running?") where the only tool that ran was a git-history
  tool. Git tools answer "what committed", not "what's running or consuming
  quota"; this guard passes with any read, so an activity question with a
  git-log-only response satisfies it but not the sibling. Warn severity.
  Origin: 2026-07-13 evening — Shadow answered "No, X was the last shipment"
  to "Anything else ship?" from `git log` alone while a Claude run was in fact
  actively editing execution-snapshot files and consuming the 5-hour quota
  window past the declared 7pm cutoff. The response even acknowledged
  "unfinished local work on execution snapshots" but did not investigate its
  source. See `core/contracts.py:ActivityAssertionGroundingGuard`.

## Escalation
Warn-only — no auto-block, no the user surface. Repeated fires across sessions
mean the upstream prompt is still emitting unanchored assertions; promote the
specific failure pattern to a Quick Reference rule in CLAUDE.md if it stays
hot for >3 consecutive days.

## Recent activity
2026-07-10 gap-closer window: **6 fires in 4h** (00:58, 00:59, 01:28, 02:36,
02:37, 02:55) — the promote-trigger from the previous window fired again.
Generalized Quick Reference rule 55 promoted this pass to close the
generation-time salience gap on the broader `Yes/No/Confirmed`-shaped
answer class.

2026-06-27 gap-closer window: **6 fires in 4h, 7 fires in 24h** — the top
violator in the 4h window. The assertion-by-the user inverse was previously owned
by the separate `concurrence-grounding` guard and is now handled here. Quick Reference rule 50 already
covers the retrospective- and forward-count classes ("what shipped" + status
counts), so the rule itself is documented; the remaining gap is generation-time
salience on the broader `Yes/No/Confirmed`-shaped answer class. Sister
That concurrence surface was first added 2026-06-27.

Prior data point: 3 fires in 24h on 2026-06-20 (00:23, 14:08, 14:43). The
trendline is climbing, not flat; if the next gap-closer window also reports
≥6/4h, promote a generalized Quick Reference rule beyond the rule-50 cases.
