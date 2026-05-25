# Bilevel Planner Contract (FM-011)

**Type:** Post-check enforcement  
**Failure Mode:** FM-011 (Action deferral — proposes instead of executes)  
**Status:** Active (2026-05-20+)

## Trigger

When `state/current_plan.json` exists with a `tasks` array containing at least one task with `"committed": true`, this contract fires on response generation.

## Precondition

1. Committed tasks exist in `state/current_plan.json`
2. Response text contains proposal-seeking language ("should I", "would you like", "shall I", etc.)

## Enforcement

Block the response and return Violation (severity="block"):

```
"Committed task(s) exist (task_name_1, ...) but response proposes instead of executing. 
Approved plans are binding — execute them directly without re-seeking approval."
```

Suggest recovery:
```
Read state/current_plan.json for committed tasks. Execute them directly. 
No re-proposing or re-seeking approval.
```

## Recovery

1. Read `state/current_plan.json` to see the committed task list
2. Execute the committed tasks directly without asking for re-approval
3. Do not propose alternatives or request clarification unless tasks are blocked by a technical error

## Rationale (Research Insight)

From **"Learning Bilevel Policies over Symbolic World Models for Long-Horizon Planning"** (arXiv:2605.15975):

The paper shows that separating high-level symbolic planning (what to do) from low-level continuous execution (how to do it) prevents compounding errors and enables reliable long-horizon task completion.

In Shadow's context:
- **High-level (symbolic):** User approves a plan → tasks become "committed"
- **Low-level (execution):** Shadow executes committed tasks directly
- **Violation:** Re-proposing or re-seeking approval on a committed task breaks the bilevel abstraction and wastes turns

When a plan is approved and committed, the contract enforces that Shadow treats it as binding rather than re-negotiating or seeking approval again.

## Escalation

If a committed task cannot be executed due to a technical blocker (e.g., auth failure, permission denied), the contract does not fire — the error is legitimate. Surface the blocker in the response instead.

## Related Contracts

- `action-deferral-guard`: Catches proposal language in general (no committed plan context)
- `planner-recovery`: Detects subgoal stalls and triggers replanning
- `cognifold`: Proactive pattern warning from cognitive structures

## Testing

See `tests/test_contracts.py` → `test_bilevel_planner_*`
