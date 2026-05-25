# Contract: Context Taint Propagation (FM-034b)

**Type:** Pre-check — block on taint detection
**Failure mode:** FM-034b (propagation-cascade contamination)
**Status:** Tier 2 queue — code implementation pending (see `core/contracts.py`)

## Problem

Shadow's existing contracts fire locally: `context-contamination` detects failed retry loops, `tool-chain-provenance` traces parameter sources within a single turn. Neither tracks what happens when a tool_call_result that *triggered a violation* in turn N is silently reused as a parameter in turn N+2. The violation fires; the tainted value persists in context; downstream calls consume it.

PropGuard (arXiv 2025) formalizes this as a spatio-temporal propagation problem: a single injected instruction contaminates multiple agents across multiple rounds before detection because each agent's local check passes — only the inter-turn graph reveals the cascade.

Shadow is not a multi-agent system in the MAS sense, but it faces the structural equivalent: sub-agent outputs fed back into the main context, tool_call_results accumulating across a long session, memory writes from one tool call becoming parameters for the next.

## Rule

Before any tool call whose parameters include values sourced from a `tool_call_result`, check whether that result's origin slot was flagged by a prior contract violation in the same session.

If the origin slot was flagged:
1. Do NOT proceed with the downstream tool call.
2. Log: `[taint-block] tool=<name> param=<key> tainted_by=<contract>/<slot_id>`
3. Re-retrieve the parameter from a clean source (re-read the file, re-run the query, ask the user).
4. Only proceed once the parameter is sourced from a violation-free origin.

## Taint tagging protocol

Each entry in `ContractContext.tool_call_results` carries a `tainted: bool` and `tainted_by: str` field after this contract is implemented. A result is tainted when:
- Its tool call triggered a `block`-severity violation, OR
- Its parameters were themselves sourced from a tainted result (transitive propagation)

Transitivity depth is capped at 3 to avoid false positives from long chains.

## Enforcement

`ContextTaintContract` in `core/contracts.py` — see Tier 2 queue.

Until code enforcement is wired: apply manually — before re-using a tool result that appeared in the same session as a contract violation, verify it was not the active result when the violation fired.

## Interaction with existing contracts

- Extends `context-contamination` (FM-034): that contract detects retry contamination within a turn; this tracks cross-turn propagation.
- Complements `tool-chain-provenance`: provenance checks that parameters are traceable; this checks that the traced source is clean.
- Complements `parallel-agent-consensus-guard`: consensus guard catches correlated agent outputs; this catches tainted parameters feeding parallel agents.

## Research basis

**PropGuard: Safeguarding LLM-MAS via Propagation-Aware Exploration and Remediation** (arXiv cs.LG 2025)

Builds a spatio-temporal graph of agent interactions, uses a trained inspector (GE-GRPO) to trace suspicious subgraphs, then remediates upstream and replays affected downstream interactions. The key empirical result: local per-step defenses consistently miss cascade contamination that only appears in the inter-turn graph.

**Credibility caveat:** The replay-remediation step assumes LLM output is approximately deterministic. It is not. Shadow's implementation avoids replay entirely — instead blocking the downstream call and requiring a clean re-retrieval. This is slower but avoids the drift problem the PropGuard critics identify.

## Escalation

Block-severity. If a taint block fires on an irreversible action (send, push, publish), surface to the user with: what was about to be sent, which upstream slot tainted it, and which contract originally flagged that slot.
