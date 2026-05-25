# Contract: repair-loop

## Type
Harness-enforced validation gate — fires after any structured extraction task that produces a list, hierarchy, or schema from an unstructured source.

## Trigger
Any task that:
1. Takes unstructured input (research paper, email thread, document) AND
2. Produces structured output (gap list, action items, JSON schema, ranked criteria)

Typical examples: research deep-dives, email digest extraction, contract generation from conversation.

## Precondition (Observe-Diagnose-Repair)
Before marking the extraction **done**, Shadow must complete one validation pass:

**Observe:** Does the output structure match the source? Spot-check ≥1 item by tracing it back to the source text.

**Diagnose:** Identify any items in the output with no traceable source anchor (hallucinated structure), or source items that were silently dropped.

**Repair:** If divergence is found:
- Remove or flag fabricated items
- Add missing items from source
- Note the repair inline: "(corrected: X was missing from initial pass)"

If no divergence found after spot-check, state "ODR: clean" before marking done.

## Enforcement
Harness-side. No code enforcement yet (see future upgrade path below).

The contract is satisfied if Shadow's response to a structured extraction task:
- Includes a spot-check trace of at least one output item to its source
- OR explicitly states "ODR: clean" after self-review
- OR notes a repair made

## Origin
2026-04-26: arXiv paper *RegReAct: Self-Correcting Multi-Agent Pipelines for Structured Regulatory Information Extraction* demonstrated that single-pass LLMs hallucinate structure and lose hierarchies in complex documents. Their 7-stage ODR pipeline outperformed GPT-4o single-pass on all structural and semantic metrics. The key insight — *enforce structure before completeness* — applies to any Shadow task that extracts a list or schema from prose.

## Violation recovery
1. If a structured extraction was shipped without an ODR pass:
   a. Re-read the source (paper, thread, doc)
   b. Spot-check 2-3 output items against it
   c. Post corrections as a follow-up: "ODR catch: X was fabricated / Y was missing"
2. If repair reveals >25% of items are unsupported: discard and re-extract from scratch

## Future upgrade path
If Shadow gains structured task logging, implement a `RepairLoopContract` in `core/contracts.py` that:
- Detects structured-extraction task type from prompt keywords ("extract", "list", "schema", "gaps")
- Requires a `odr_validated: true` flag in task completion metadata
- On missing flag: auto-injects a repair-pass prompt before allowing done signal

## Escalation
If the same source yields >3 hallucinated items in a single extraction: surface to the user — the source may be malformed or the extraction prompt needs redesign.

## Interaction with existing contracts
- Complements `step-state-tracking`: ODR is a *post-step* validation; step-state-tracking is a *mid-step* self-label
- Complements `verify-before-push`: ODR is source-level validation; verify-before-push is output-level confirmation
