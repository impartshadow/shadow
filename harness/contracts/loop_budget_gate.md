# Contract: loop-budget-gate

## Type
Harness-enforced gate — fires when Shadow runs any goal-directed autonomous loop (karma watchdog, moonshot iteration, idle task, /improve round).

## Trigger
Any task that:
1. Sets an explicit goal or hypothesis AND
2. Iterates toward that goal with self-evaluation of completion

Typical examples: karma watchdog experiment, idle moonshot micro-tasks, /improve four-round generation loops, any `while not done` autonomous run.

## The problem this solves

Self-evaluation of goal completion is structurally biased: the same model that did the work grades it, inflating success rates. Codex CLI's `/goal` feature (May 2026) exposes this — their `budget_limit.md` stop condition exists precisely because self-assessed "done" is unreliable. The token budget is a safety net, not a feature.

Shadow has the same structure in its karma watchdog loop and /improve pipeline. Without an external stop condition, loops can:
- Exit early on hallucinated completion
- Run indefinitely on unsolvable goals
- Burn tokens on degenerate cycles

## Precondition

Before starting any autonomous goal loop, Shadow must establish:

1. **Budget**: a hard turn-count limit (default: 5 iterations; max: 10)
2. **External exit criterion**: at least one stop condition that is NOT self-assessment (e.g., "metric improved", "file exists", "test passes", "N turns elapsed")
3. **Budget tracking**: each iteration must log its turn number

Format to include at loop start:
```
Loop budget: N turns max
External stop: <measurable condition>
Turn 1 of N: ...
```

## Enforcement

Harness-side. Violation if Shadow runs ≥3 loop iterations without:
- Stating a turn count in each iteration, OR
- Having a non-self-eval exit criterion defined at loop start

## Budget defaults by loop type

| Loop type | Default budget | Hard max |
|---|---|---|
| /improve generation rounds | 4 | 6 |
| Karma watchdog iterations | 5 | 8 |
| Idle moonshot micro-tasks | 3 | 5 |
| Goal-directed research | 6 | 10 |

## Violation recovery

1. If a loop hit the turn budget without an external exit criterion firing:
   - Post turn-count and final state to #moonshot
   - Do NOT re-enter the loop this session
   - Log in session_handoff.md: "Loop X hit budget at turn N — goal unresolved, needs redesign"
2. If a loop exited on self-assessed completion with no external verify:
   - Flag the result as "self-eval only — unverified"
   - Propose a measurable exit criterion for the next run

## Origin
May 2026: Codex CLI 0.128.0 `/goal` feature analysis (Simon the userison). Key finding: prompt-injection goal loops require a budget_limit fallback because self-evaluation of completion is unreliable. The token-budget mechanism is an implicit concession that external stops are necessary. Applied to Shadow's existing autonomous loop patterns.

## Interaction with existing contracts
- Complements `loop-tripwire` (FM-003): tripwire blocks >3 commits to same file; budget-gate blocks >N iterations on same goal
- Complements `self-eval-bias`: that contract addresses /improve evaluation quality; this one addresses loop termination
- Complements `verify-before-push`: budget-gate fires during loop execution; verify-before-push fires at completion
