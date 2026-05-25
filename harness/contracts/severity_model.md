# Contract Severity Model

**Type:** Harness documentation
**Trigger:** Authoring or auditing a contract
**Contracts referenced:** All contracts in `harness/contracts/`

---

## Why severity matters

Not all violations have the same impact. Logging a capability misroute and a trailing summary the same way means the improve loop has no signal for prioritization. Severity lets `deficiency_tracker.priority_rank()` surface high-impact failures first.

## Severity tiers

| Tier | Label | Meaning | Example |
|------|-------|---------|--------|
| 4 | `critical` | Blocks execution or causes data loss | Pushing unverified code, DOX leak via outbound tool |
| 3 | `high` | Behavioral regression that the user has corrected 3+ times | WebFetch/WebSearch instead of MCP, editing without reading |
| 2 | `medium` | Degrades quality but recoverable | Post-response question restatement, fabricated gap claim |
| 1 | `low` | Style/polish issues with no correctness impact | Minor trailing sentence, unnecessary clarification |

## Assigning severity

When writing a new contract, set `severity` to one of: `low`, `medium`, `high`, `critical`.

Use the `violation_count` threshold as a secondary signal:
- 0–2 corrections → `medium`
- 3–5 corrections → `high`
- 6+ corrections OR involves outbound data → `critical`

## How severity is consumed

- `DeficiencyTracker.priority_rank()` weights by `severity × recency_decay × frequency`
- `/improve` reads `priority_rank()` to choose which contracts to strengthen first
- `Violation.severity` in `core/contracts.py` maps to these labels (not just `warn`/`block`)
