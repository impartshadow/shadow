# Contract: spec-integration-validator

## Type
Post-action check — Haiku-judged, warn-only.

## Trigger
Any `/improve` Level 2 run that successfully injects a new contract into `core/contracts.py`.

## The problem this solves

Contracts are injected one at a time, but the harness spec is a system — contracts share failure modes, post-check chains, and ContractContext fields. A new contract can pass its own behavioral gate (Round 5) while still:

1. **Shadow-duplicating** an existing contract that covers 80% of the same FM.
2. **Contradicting** a prior post-check (e.g., two contracts both fire on FM-011 but prescribe opposite recovery actions).
3. **Missing a required ContractContext field** that exists in the spec but wasn't in the generated code's imports.

AIRA-Design demonstrated that an agent-as-verifier step after each architecture write catches integration violations before they compound. The same principle applies here: inject, then immediately verify against the full spec.

## Precondition

This contract fires after:
1. A new Contract subclass has been written to `core/contracts.py`.
2. `pytest tests/test_contracts.py` has passed.
3. The new class name is known.

## Rule

After injection and test pass, run a Haiku integration check:

```
Prompt to Haiku:
  HARNESS SPEC (top 16 active contracts from CLAUDE.md + taxonomy):
  [list of contract names, failure modes, check_type, severity]

  NEW CONTRACT:
  [class name, failure_mode, check_type, severity, abbreviated check logic]

  Questions:
  A. Does any existing contract already cover ≥70% of this failure mode? [YES/NO + which one]
  B. Does this contract's recovery action contradict any existing contract's recovery action on the same FM? [YES/NO + details]
  C. Does the contract reference any ContractContext field not present in the dataclass? [YES/NO + field name]

  Reply: JSON {"a": bool, "a_detail": str, "b": bool, "b_detail": str, "c": bool, "c_detail": str}
```

If any answer is YES:
- Log the specific finding to `state/contract_violations.jsonl` with `contract: "spec-integration-validator"`.
- Append a warning to `#shadow-log` Discord channel: `⚠️ spec-integration-validator: [finding]`.
- Do NOT revert the injected contract — annotation only.

If all answers are NO: pass silently.

## Enforcement

Harness-enforced: add a `_spec_integration_check(class_name, generated)` call in `scripts/improve.py` immediately after `_inject_contract` returns success. Haiku call via `core.claude_client.ask`.

## Recovery

On a YES finding, the generated contract is annotated but not reverted. The `/improve` next run will see the violation in `contract_violations.jsonl` and use it as a signal to generate a replacement or merge the duplicate.

## Escalation

Surface to the user only if 3+ injections in the same session all fire this validator — that indicates a systemic spec drift requiring human review.

## Research basis

**AIRA-Design** — 20 agents writing novel attention implementations with an agent-as-verifier step after each write. The verifier step was responsible for catching ~40% of integration violations before they propagated into the evaluation harness. Applied here: Shadow's own contract injection is structurally analogous — each `/improve` run writes a "novel architecture" (a new Contract subclass) into a system that must remain internally consistent.
