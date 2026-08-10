# Contract: flow-checkpoint

## Type

Post-check instrumentation feeding deterministic, bounded recovery routing.

## Reference

**Paper:** Reinforced Collaboration in Multi-Agent Flow Networks (arXiv:2605.12943)

**Core insight:** Multi-agent flow networks with reinforcement learning can dynamically reroute task subtrees away from low-confidence agents, reducing error propagation across the pipeline.

## Trigger

Every response generation (`action == "respond"`).

## Precondition

Response text is non-empty and the action is a direct user-facing response (not internal tool call).

## Enforcement

Code-enforced in `core/contracts.py:FlowCheckpointContract.check_post()`.

### Confidence Scoring

Scores response on 0-1 scale by counting linguistic signals:

- **Hedging markers** (lower confidence): "might", "may", "could", "possibly", "seems", "I think", "perhaps", etc.
- **Confidence markers** (higher confidence): "confirmed", "verified", "executed", "deployed", "error", "failed", etc.
- **Deferral markers** (lower confidence): "you will need to", "I cannot", "requires manual", etc.

Normalized by response length to avoid false signals in long responses.

## Observability

Low-confidence outputs (< 0.6) are emitted to `state/flow_routing_queue.jsonl` with:

```json
{
  "ts": <unix_timestamp>,
  "confidence": <0.0-1.0>,
  "response_length": <char_count>,
  "action": "respond",
  "tools_used": [...],
  "needs_rerouting": true,
  "summary": <first_200_chars>
}
```

High-confidence outputs (> 0.9) are also logged for observability.

## Integration Points

### Deterministic Consumer

`core/flow_rerouter.py` consumes `state/flow_routing_queue.jsonl` to:

1. Flag patterns (e.g., "low confidence on Git operations" → escalate to Git specialist role)
2. Route recognized execution failures to one named fallback executor
3. Escalate authentication failures instead of retrying them
4. Record the original route, recovery decision, and timestamp in an append-only ledger

### Fallback Escalation

When `needs_rerouting == true`:

- Dispatch to higher-context variant of system prompt
- Add role-specific instructions ("You are X. Re-solve with explicit steps.")
- Log outcome for RL feedback

## Recovery

Recovery is bounded to one fallback. Unknown failures escalate rather than chaining autonomously.

## Severity

Observe-only (no violations returned). Routing decisions are made downstream based on emitted signals.

## Testing

See `tests/test_contracts.py:test_flow_checkpoint_*` for:

- Hedging pattern detection
- Confidence score calibration
- Routing signal emission

## Notes

This contract is the minimal implementation of arXiv:2605.12943. Full reinforced routing requires:

1. Fallback prompt templates indexed by failure mode (not included)
2. Multi-role dispatch logic (not included)
3. RL reward signal for rerouting decisions (not included)
4. Nightly pipeline consumer that reads `flow_routing_queue.jsonl` (not included)

The contract provides the observation layer. `core/flow_rerouter.py` owns deterministic
classification, while `core/task_dag.py` applies a single named fallback and persists
the outcome. Reinforcement learning remains intentionally deferred until the ledger
contains enough clean outcome-labelled routing data.
