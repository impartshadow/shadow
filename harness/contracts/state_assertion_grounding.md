# Contract: state-assertion-grounding

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:StateAssertionGroundingGuard`. Severity: `warn`.

## Failure mode
FM-014 (process layer) — assert-from-memory. A response answers a factual /
state question definitively, but no ground-truth-reading tool ran this turn,
so the answer is sourced from memory or stale conversation context rather
than the live system state.

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
diverges. It catches assert-from-memory only. The check is `warn`, not
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

## Escalation
Warn-only — no auto-block, no the user surface. Repeated fires across sessions
mean the upstream prompt is still emitting unanchored assertions; promote the
specific failure pattern to a Quick Reference rule in CLAUDE.md if it stays
hot for >3 consecutive days.

## Recent activity
3 fires in 24h on 2026-06-20 (00:23, 14:08, 14:43). Each fire was a
definitive `Yes/No/Confirmed`-shaped answer to a verification-shaped question
where no read tool ran. Pattern is recurring at warn-level cadence; not yet
hot enough to warrant a Quick Reference promotion.
