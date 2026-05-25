# Contract: outcome-equivalence-guard

## Type
Post-check — observe-only. No blocking, pure instrumentation.

## Trigger
Every `respond` action.

## Failure mode
FM-028: Trajectory mismatch despite correct outcome.

## Core insight (TIER, arXiv:2605.16790)
Trajectory-Invariant Execution Rewards evaluate final state equivalence rather than trajectory matching. Valid alternative action paths to the same goal state should be rewarded equally.

Standard approaches to evaluating agent behavior penalize non-canonical paths even when they reach the correct end-state. This suppresses discovery of alternative strategies. TIER rewards outcome equivalence: if the goal is accomplished, the path is valid.

## Enforcement
`OutcomeEquivalenceGuard` in `core/contracts.py` — post-check observer that evaluates outcome achievement (heuristic + outcome signal emission).

Emits to `state/outcome_equivalence_scores.jsonl` for session audit analysis:
- `outcome_achieved`: boolean, whether response shows completion/results
- `trajectory_match`: boolean, whether path followed expected sequence
- `outcome_equivalence_score`: 0-1 score, high if outcome achieved regardless of trajectory
- `tools_used`: list of tool names called this turn

## Evaluation criteria

**Outcome achieved:** response shows:
1. Completion signals (committed, executed, deployed, completed, done, fixed) + tool execution, OR
2. Result output (JSON, error message, success text), OR
3. Standalone completion signal

**Trajectory match:** no backtracking patterns (retry, attempt, try again, revert, undo).

**Equivalence score:**
- 0.8 if outcome achieved
- 0.85 if outcome achieved via non-standard (non-trajectory-matching) path
- 0.2 if outcome not achieved

## Recovery
Observe-only — no recovery actions. Data informs:
1. Session audit's outcome-vs-trajectory report
2. Multi-session learning patterns (detecting alternative valid paths)
3. Skill router feedback (non-canonical paths that succeed can become new canonical paths)

## Post-session analysis
`session_audit.py` reads `outcome_equivalence_scores.jsonl` to compute:
- Fraction of outcomes achieved via non-standard paths
- Detection of alternative valid solution strategies
- Trajectory-skill calibration (did non-standard paths consistently succeed or fail?)

## Why this matters

Current evaluation penalizes alternative-but-valid paths. This suppresses learning from diverse strategies. TIER enables:
1. **Alternative strategy discovery**: if outcome is correct, the path is viable
2. **Robustness to path constraints**: system learns multiple routes to same goal
3. **Skill router calibration**: non-canonical paths that consistently succeed can inform skill routing rules

Example: executing a task via script + verification instead of step-by-step commands should be rewarded equally if the outcome is the same. TIER ensures this equivalence is captured.
