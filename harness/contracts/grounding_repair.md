# Grounding Repair Contract

**Type:** Post-check (warn-only)  
**Failure Mode:** FM-011 (Proposing instead of executing)  
**Source:** arXiv:2605.01750 (Talk is Cheap, Communication is Hard)

## Trigger

Fires when:
1. User message is an **imperative** (command verb + object, no conditional)
2. Response contains **hedging phrases** ("would you like", "I could do X or Y", "should I", etc.)
3. Haiku scores the re-negotiation as ≥0.7 confidence

## Precondition

- `ctx.action == "respond"`
- User message starts with action verb (implement, create, fix, run, etc.) and ends with period
- User message does NOT contain "should I", "can I", "would you like", or trailing `?`
- Response text ≥80 chars and contains at least one hedging pattern

## Enforcement

**GroundingRepairContract.check_post():**

1. Parse user message for imperative structure (`_is_imperative`)
2. Scan response for hedging patterns (regex quick-filter)
3. If both true, invoke Haiku to score 0-1: "Did the agent re-open a decided scope?"
4. If score ≥0.7, return Violation (warn-severity, no block)
5. Log event to `state/grounding_failures.jsonl` for FM-011 trend tracking

## Recovery

**Heuristic:** When the user's prior message contains an imperative verb with no conditional, Shadow must act — not re-ground.

Examples of violations:
- **User:** "Implement the grounding repair contract."  
  **Shadow:** "I could implement this, or would you prefer I also update the audit script?"  
  ❌ Re-negotiating after a decided scope.

- **User:** "Run the tests and commit."  
  **Shadow:** "Here's what I'd do: run tests, then ask if you want me to commit, or..."  
  ❌ Re-opening a decided sequence.

Examples of correct execution:
- **User:** "Implement the grounding repair contract."  
  **Shadow:** *(executes without hedging)* "I've added GroundingRepairContract to core/contracts.py and created harness/contracts/grounding_repair.md. Running tests... ✓ Committed: abc1234."

- **User:** "Should I implement this, or would you prefer something else?"  
  **Shadow:** *(this is conditional; contract skips)* "I'd recommend implementing it because..."

## Escalation

None. Warn-severity violations do not block or escalate to the user.

## Integration

- **session_audit.py:** Grounding-failure events are read from `state/grounding_failures.jsonl` and counted in FM-011 trend tracking. High frequency (>3 per session) may trigger FM-011 backlog items.
- **Contracts co-firing:** Works alongside ActionDeferralGuard (FM-011, more general regex-based) and ExecutionIntentGate (FM-011, intent classification). Grounding-repair targets a *specific* sub-case: imperative + hedging.

## Rationale

**Dynamic grounding failures** (the paper's key finding) differ from static communication errors:
- Not caused by unclear language mapping
- Caused by iterative negotiation breakdown *after* agreement is reached
- Require active repair protocols (detection + reversion to prior agreed state)

This contract detects the breakdown and flags it for observation. Future evolution: auto-recovery by removing hedging phrases and re-committing to the user's decision.
