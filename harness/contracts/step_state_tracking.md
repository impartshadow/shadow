# Contract: step-state-tracking

## Type
Harness-enforced self-assessment gate — fires at natural task milestones during multi-step work.

## Trigger
Any response that is one turn in a multi-step sequence (identified by: chained tool calls, loop structures, or tasks that span 3+ reasoning steps). Fires before committing an irreversible action in that sequence.

## Precondition
Before executing an irreversible action mid-task (push, send, archive, delete, publish), Shadow must briefly self-label its current reasoning state:
- **on_track**: plan still matches observations; no anomalies
- **drifting**: plan assumptions have been partially invalidated but proceeding
- **stuck**: blocked on a sub-step; have tried ≥1 alternative

If labeled **drifting** or **stuck**, one of the following must follow:
1. An explicit corrective step (retry with different approach)
2. A mid-task escalation to the user (terse: "Drifting on X — doing Y instead")

## Enforcement
Harness-side. No code enforcement yet (see future upgrade path below).

The contract is satisfied if Shadow's response to a multi-step milestone:
- Names the current state label (on_track / drifting / stuck)
- OR implicitly demonstrates on-track progress (tool output verified, next step logically follows)

## Origin
2026-04-24: arXiv paper *From Actions to Understanding: Conformal Interpretability of Temporal Concepts in LLM Agents* demonstrated linear separability of success/failure latent directions in agent activation space. For API-only agents like Shadow, the analogous mechanism is structured self-assessment at step boundaries — conceptually equivalent to the paper's temporal concept probing, implemented via prompting rather than activation steering.

2026-05-04: AgentFloor (arXiv cs.AI) benchmarked 16 open-weight models (0.27B–32B) + GPT-5 across a 6-tier capability ladder. Key finding: sustained constraint-tracking over many steps (tier 4) is the **only tier where neither frontier nor small models reach strong reliability**. This is not a gap that will close by upgrading the model — it requires structural enforcement. This contract is the mechanism.

## Violation recovery
1. If an irreversible action was taken while drifting with no escalation:
   a. Audit what diverged from the original plan
   b. Surface the delta to the user with: "Mid-task drift — here's what changed and why"
2. If stuck and never surfaced: post the block immediately with one alternative tried

## Future upgrade path
If Shadow gains access to structured task logging with per-step outcomes, implement a `StepStateEvaluator` contract in `core/contracts.py` that:
- Maintains a per-session step trace
- Computes confidence bounds (conformal-style) over recent step labels
- Auto-escalates when ≥2 consecutive steps are labeled drifting/stuck

## Escalation
If drift is detected at 3+ consecutive steps, treat as a planning failure — stop, read the original task spec again, and re-plan from the last verified checkpoint.
