# Verified Failure Store

**Type:** Supplementary memory contract (enforced in `core/deficiency_tracker.py` + `core/contracts.py`)

**Trigger:** After any Contract violation that is followed by a successful tool call or explicit recovery confirmation within the same session.

**Precondition:** A `Violation` was emitted AND the subsequent tool call (`ctx.tool_calls`) succeeded without a second violation of the same contract.

**Enforcement:** `Contract.register_verified(violation, recovery_tool)` — writes a confirmed signature to `state/verified_failure_signatures.jsonl` only when recovery is confirmed.

**Why verified-only matters:** Shadow's `contract_violations.jsonl` logs every violation, including false positives, partial recoveries, and unresolved loops. When `/improve` or idle tasks mine this log for patterns, noise from unconfirmed entries produces low-quality signals. Verified signatures are a filtered subset: the violation fired, the recovery succeeded, and the pattern is reusable.

**Signature schema:**
```json
{
  "ts": "ISO-8601",
  "contract": "verify-before-push",
  "failure_mode": "FM-002",
  "trigger_context": "action=git_push, files_edited=[core/contracts.py]",
  "recovery_tool": "pytest",
  "recovery_confirmed": true
}
```

**Recovery:** None needed — this is a passive logger, not a blocking check.

**Escalation:** When 3+ identical signatures accumulate, surface to `/improve` as a persistent pattern candidate for a new pre-check.

**Implementation target:** `core/contracts.py:Contract.register_verified()` (Tier 2) + `core/deficiency_tracker.py:record_verified_recovery()` (Tier 1.5)
