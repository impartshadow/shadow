# Contract: contract-regression-gate

**Type:** Pre-ship gate — harness-enforced, tested in `tests/test_contracts.py`
**Failure mode:** FM-003 (loop/regression — silent behavioral drift on historical inputs)

## Trigger

Any `/improve` run that generates or modifies a Contract subclass in `core/contracts.py`.

## Precondition

A frozen replay fixture must exist at `tests/fixtures/contract_regression_inputs.json`. Each entry is a `(context_dict, contract_name, expected_fires: bool)` triple representing a historical canonical case.

## Rule

Before committing any contract change:
1. Run `pytest tests/test_contracts.py -k regression -q`
2. All frozen fixture cases must pass — i.e., every `(context, contract, expected_fires)` triple produces the expected outcome
3. If any regression case fails, block the commit and report which historical input now produces wrong behavior

## Replay fixture format

```json
[
  {
    "contract": "verify-before-push",
    "context": {"action": "git_push", "verification_output": ""},
    "expected_fires": true,
    "label": "push with empty verification should block"
  },
  {
    "contract": "verify-before-push",
    "context": {"action": "git_push", "verification_output": "12 passed"},
    "expected_fires": false,
    "label": "push with passing tests should not block"
  }
]
```

## Growing the fixture

Whenever a false-positive or false-negative contract violation is discovered in production:
1. Add the offending context as a new fixture entry
2. Mark `expected_fires` correctly
3. Commit fixture update alongside the contract fix

This creates an ever-growing exemplar buffer that prevents the same regression from recurring.

## Enforcement

`scripts/improve.py` calls `_run_regression_replay()` after Round 4 (generate) and before `git commit`. `/improve` blocks and reports if any fixture entry regresses.

## Recovery

On regression failure:
1. Do NOT commit the new contract code
2. Report which fixture entry failed and what changed
3. Revise the contract logic to satisfy both the new behavior AND the frozen historical cases

## Escalation

If a historical fixture case needs to be intentionally changed (deliberate behavior change, not accident), the user must explicitly approve the fixture update before the commit proceeds.
