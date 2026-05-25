# Context Contamination Contract (FM-034)

## Type
Post-check (observational, warn-only)

## Trigger
Detects when the same tool is called multiple times with errors in between, indicating failed attempts left in the context window.

## Precondition
- Message history length ≥ 4 (multi-turn conversation)
- Same tool name appears in multiple assistant turns
- Tool result errors present between repeated calls

## Enforcement
`ContextContaminationContract` in `core/contracts.py` scans the message history for repeated tool calls with intervening errors. When detected, logs a warning violation.

## Recovery
When this contract fires:
1. Call `claude_client.trim_failed_attempt(messages)` to strip the failed tool call and its result from the context
2. Retry with clean context containing only the successful conversation prefix + the failed tool's name (state summary)
3. This breaks the contamination cycle before the next API call

## Research Basis
**Why Retrying Fails: Context Contamination in LLM Agent Pipelines** (arXiv:2605.08563)

Failed LLM agent attempts left in the context window systematically increase per-step error rates on retries, compounding failure rather than recovering from it. Each failed trace adds noise to the subsequent attempt, degrading the signal about what the agent should do differently.

### Key Finding
Retries with contaminated context show 40-60% higher error rates than retries with clean context. The failed attempt trace becomes a negative exemplar that the LLM learns from in subsequent attempts.

### Implication for Shadow
Context trimming on failure should be automatic for tool-use loops. When a tool call fails (error/exception in tool_result), the next attempt should not re-read the failure trace. Instead:
- Preserve the conversation goal and state summary
- Drop the full error trace and failed attempt
- Re-attempt with minimal context overhead

## Escalation
This contract is observational. It fires when contamination is detected but does not block execution. The trimming happens automatically in the retry path (`claude_client.chat()`). If this fires repeatedly on the same tool, investigate whether that tool has an underlying issue (auth, configuration, permissions) rather than continuing to retry with trimming.
