# Skill: Tiered Context Budgeting

## Role sequence
triage → compress → execute

## When to invoke
When a task requires feeding a document or conversation history longer than ~8K tokens to Claude.

## Stages

### 1. Triage
- Estimate total token count of the input (rough heuristic: 1 token ≈ 4 chars).
- If total fits in context budget with room for response, skip to execute.
- Otherwise proceed to compress.

### 2. Compress
Split the input into recency tiers:

| Tier | Content age / position | Treatment |
|---|---|---|
| Hot | Last 20% of tokens (most recent) | Pass verbatim — full fidelity |
| Warm | Middle 40% | One-sentence-per-paragraph summary |
| Cold | Oldest 40% | Extract only named entities, decisions, and numbers |

Apply tier treatment in order, from cold to hot, until total fits budget.

### 3. Execute
- Feed tiered content to Claude with a brief framing note: "[older context summarized for brevity]"
- If the task produces wrong answers attributable to missing cold-tier detail, escalate: re-run with warm tier passed verbatim.

## Contracts referenced
- No active contract; this is a soft skill invoked by the researcher and document-processing flows.

## Notes
- Mirrors SP-KV's key insight: recent tokens have higher predicted utility; allocate cache accordingly.
- Do not apply to short documents — overhead exceeds benefit below ~8K tokens.
