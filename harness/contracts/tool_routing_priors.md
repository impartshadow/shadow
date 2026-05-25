# Design principle: tool routing priors

## Type
Harness-side design principle — no code enforcement. Informs future contract and routing decisions.

## Motivation
The `wrong-tool-route` and `capability-misroute` contracts are static binary rules. They encode a prior ("use mcp__shadow__browse_url, not WebFetch") but do not update based on observed failure rates. A Bayes-consistent orchestrator would weight tool candidates by historical success, not just whether a rule fires.

## Principle
When adding or revising a tool-routing rule, check `state/contract_violations.jsonl` first:

1. If tool X has appeared in 3+ recent violations, that is a low-reliability signal — tighten its routing rule.
2. If a contract has had zero violations in 60+ days, it may encode an overcorrection — the prior has been absorbed and the hard rule may be relaxing the wrong direction.
3. Prefer threshold-based contracts ("N violations in W days") over fixed-pattern bans where the failure behavior is measurable.

## Implementation path
`DeficiencyTracker.tool_failure_rates(days=30)` returns per-tool violation counts. Use this output in `/improve` audits to calibrate routing rules against data rather than intuition.

## Contracts referenced
- `capability_misroute.md` — primary target for future upgrade
- `pre_denial_gate.md` — secondary target
- `wrong_tool_route` (in `core/contracts.py`) — static regex; candidate for data-informed threshold

## Escalation
When tool_failure_rates() shows a tool appearing in 5+ violations in 7 days and no contract covers it, flag to the user as a gap in routing coverage.
