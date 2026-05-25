# Error Attribution Contract

**Type:** Diagnostic principle (harness-enforced)

**Failure mode:** FM-035 (mis-attributed fix)

## Problem

Shadow's `/improve` pipeline detects failure patterns and routes them directly to L2 code generation. This skips the attribution step: *where is the bug* — in the prompt/harness, in a contract gap, in model behavior, or in missing context? A contract written for a model-behavior failure does nothing. A harness doc update applied to a contract gap also does nothing. Wrong attribution → wasted cycle.

## Attribution taxonomy

| Label | Root cause | Correct fix |
|---|---|---|
| `prompt_gap` | Harness rule exists but is ambiguous, incomplete, or not loaded in system prompt | Update CLAUDE.md, harness/*.md, or memory/*.md |
| `contract_gap` | No code-enforced gate exists for this class of failure | L2 code generation (default path) |
| `model_behavior` | Behavior is a model-level tendency (RLHF artifact, distribution drift) — no textual signal to intercept | Backlog; escalate if high-frequency |
| `context_miss` | The relevant state (decision log, prior correction, email) wasn't loaded into context | Fix state loading / context retrieval |

## Trigger

Fires during L1 pattern detection in `/improve`. Each detected pattern must carry an `attribution` field using the taxonomy above before L2 routing is decided.

## Enforcement

Harness-side: the `_detect_patterns` prompt in `scripts/improve.py` is required to request and use the `attribution` field. The routing logic should branch:
- `contract_gap` → L2 code generation (existing path)
- `prompt_gap` → append to `state/improvement_backlog.jsonl` with target=`harness` and priority=`medium`
- `model_behavior` → append to backlog with priority=`low`, no code gen
- `context_miss` → append to backlog with target=`state_loading` and priority=`medium`

## Pre-condition

Pattern has been identified with at least 2 occurrences or 1 high-severity occurrence.

## Post-condition

Each pattern has an `attribution` label. Code generation is only triggered for `contract_gap` patterns.

## Recovery

If attribution is missing or ambiguous, default to `contract_gap` (conservative — better to generate a redundant contract than to skip a fixable gap).

## Escalation

If `model_behavior` patterns accumulate >5 entries in 30 days, surface to the user — this signals a distribution shift that warrants model-level intervention.

## Research basis

IBM Research (Shbita, Gentile et al.): *A Systematic Approach for Large Language Models Debugging* — proposes treating LLMs as observable systems with issue detection → diagnosis → **attribution** → refinement loop. The attribution step (prompt vs. model vs. data) is the explicit gap between ad-hoc debugging and systematic improvement.
