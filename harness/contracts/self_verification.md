# self-verification

**Type:** Post-check (code-enforced, warn-only)
**Failure mode:** FM-011 (proposal-instead-of-execution)
**Trigger:** Every response (`ctx.action == "respond"`)
**Reference:** TheraAgent iterative self-verification loop, arXiv:2605.05963

**Precondition:** Response text matches one of `_INCOMPLETENESS_PATTERNS`
(`core/contracts.py:SelfVerificationContract`). Patterns target hedging,
deferred actions, and unresolved placeholders — the surface signatures of
"propose instead of execute" responses:

- `\btodo\b`, `\bplaceholder\b`, `\bfill in\b`, `\breplace with\b`
- `\b(?:you|user)\s+(?:will\s+)?need to\b`
- `\b(?:next|then|after that)\s+(?:you|the user)\s+(?:should|will)\b`
- `\b(?:assuming|if|depending on)\b.*,\s*(?:you|the user)\b`
- `\bonce (?:you|the user|this)\b`
- `\b(?:pending|awaiting)\b`, `\bunfinished\b`, `\bincomplete\b`, `\bskipped\b`
- `\bnot (?:yet|included)\b`

**Enforcement:** Severity is `warn`, not `block` — the contract does not stop
the response. `auto_recover()` runs a Haiku judge ("did this EXECUTE or
PROPOSE?") and, on a `PROPOSED` verdict, re-invokes the prompt with an
execution directive. Two caps keep the recovery loop bounded:

- `_MAX_RETRIES = 2` per-prompt (hashed from first 200 chars of response)
- `_GLOBAL_RETRY_CAP = 5` per `_RETRY_TTL_SECONDS = 600s` window

Both counters self-prune on every `auto_recover` call via `_prune_global()`.
Hitting either cap routes to `_escalate_to_human()` which writes
`state/self_verification_escalations.jsonl` instead of looping.

**Recovery:**
- If the response was genuinely executing (verdict `EXECUTED`): no action;
  warn-only fire was a false positive on an incompleteness keyword in
  legitimate narration. Don't suppress — telemetry is the value.
- If the response was proposing (verdict `PROPOSED`): the auto-recovered
  text replaces the original. The model should still internalize the
  execution-over-proposal mandate from `harness/_runtime.md`.

**Escalation:** Cap-hit escalations land in
`state/self_verification_escalations.jsonl`. Surface to the user only if the
escalation rate spikes (>5/24h) — otherwise it's normal cap-saturation
under chatty sessions.

**Tuning notes:**
- Pattern `\bonce (?:you|the user|this)\b` produces the most false positives
  (legitimate "once this completes, X" phrasing). Narrow only if the
  Haiku-verdict EXECUTED rate on this pattern exceeds ~80% over a 24h window.
- Violation records currently carry only `contract`, `failure_mode`,
  `message`, `severity`. Adding `matched_pattern` would aid debugging
  without breaking consumers — drop-in optional field.

**Related:**
- `action-deferral-guard` (FM-011) — same failure mode, blocking severity,
  fires on explicit "I'll do X next" framing
- `completion-artifact` (FM-027) — opposite end; fires when execution is
  claimed but artifact is missing
