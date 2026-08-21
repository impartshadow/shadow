# Skill: Behavioral Robustness

## Purpose

Validate consequential or reusable Shadow workflows on both outcome correctness and behavioral robustness. Use this skill when a task can spend money, publish externally, modify production state, handle credentials, make decisions for another agent, or become a recurring autonomous workflow.

## Role sequence

Specify invariants -> Capture baseline trajectory -> Run perturbations -> Compare behavior -> Release or escalate

## Stage: Specify invariants

1. Define the required final state and the behavioral invariants that must hold throughout execution.
2. Include applicable authority, recipient, redaction, evidence, idempotency, recovery, and stop conditions.
3. Define a task-specific pass threshold before testing. Default: the baseline and every applicable high-risk perturbation must preserve all safety invariants; at least 80% of applicable non-safety variants must reach the correct outcome.

## Stage: Capture baseline trajectory

1. Exercise the workflow in a dry-run, sandbox, fixture, or read-only replay whenever live repetition could create side effects.
2. Record the ordered sequence of decisions and tool actions, including retries, authority checks, verification steps, and the terminal receipt.
3. Treat a correct final state with a missing safety or verification step as a behavioral failure.

## Stage: Run perturbations

Run only variants that are meaningful for the workflow:

1. Wording: paraphrase the request without changing its intent.
2. Ordering: reorder independent facts or instructions.
3. Irrelevant context: add plausible but non-operative details.
4. Tool failure: inject a timeout, malformed response, unavailable dependency, or retryable error.
5. Delayed feedback: withhold confirmation or make the receipt arrive late.
6. Multi-agent dynamics: change worker order, expose conflicting recommendations, or simulate one incomplete worker result.

Never repeat a consequential live side effect solely to test robustness. Use mocks, fixtures, dry-runs, or recorded traces.

## Stage: Compare behavior

For every variant, record:

- Outcome: pass or fail against the required final state.
- Invariants: which behavioral invariants held or failed.
- Strategy drift: material changes in tool choice, authority handling, retry behavior, verification, or stopping behavior.
- Recovery: whether injected failures produced a bounded and safe recovery path.

Ignore harmless implementation variation. Flag only differences that change safety, reliability, evidence quality, or compliance with the user's intent.

## Stage: Release or escalate

1. Release the workflow only if all safety invariants pass and the declared outcome threshold is met.
2. If variants reveal brittle heuristics, record the smallest reproducible failing perturbation in `state/deficiency_log.jsonl`.
3. For an active-contract or live-routing fix, prepare a Tier 2 proposal rather than editing enforcement paths without review.
4. Report the baseline result, perturbations run, pass rate, invariant failures, and release decision.

## Completion receipt

A complete behavioral evaluation states: workflow tested, environment used, baseline outcome, perturbation matrix, outcome pass rate, invariant pass rate, observed strategy drift, and release or escalation decision.