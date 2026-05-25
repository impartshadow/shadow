# Contract: agent-routing-rationale

## Type
Harness-enforced pre-condition — fires on any Agent tool invocation that specifies a non-default `subagent_type`.

## Trigger
Any Agent call where `subagent_type` is explicitly set (Explore, Plan, code-reviewer, or any future specialist).

## The problem this solves

DecisionBench (arXiv cs.AI, May 2026) benchmarked 23,375 task instances across 11 models and found that orchestrator routing fidelity — the rate of selecting the correct specialist for a task — is 7.5–29.5%, even when output quality is statistically indistinguishable (|β| ≤ 0.010, p ≥ 0.21) across routing choices. Quality metrics are blind to routing failures: a wrong specialist can produce acceptable output that still fails at the system level.

The study also found that **delivery channel** — whether peer-model profiles are passed preloaded in the context vs. retrieved on-demand — dominates routing accuracy more than profile content quality. This implies Shadow must commit to routing decisions explicitly at invocation time.

Without explicit routing rationale, Shadow cannot audit whether it is delegating systematically to the wrong specialist. The bug is invisible in output quality.

## Precondition

When invoking Agent with a non-default `subagent_type`, the `description` field MUST include:

1. A routing rationale clause explaining why this specialist type rather than the default general-purpose agent.

The rationale does NOT need to be a separate line — it can be embedded naturally:

**Compliant:**
```
description="Locate all callers of foo() — Explore agent for read-only pattern search, no synthesis needed"
```

**Non-compliant:**
```
description="Find callers of foo()"  # routing rationale absent
```

Valid rationale patterns:
- "Explore agent because this is read-only file/symbol search with no cross-file analysis"
- "Plan agent because this requires multi-file architecture decisions before code changes"
- "general-purpose agent because this mixes research and execution in a single task"

## Preloaded context requirement

When passing context to a sub-agent, embed it in the `prompt` at call time — do NOT instruct the sub-agent to "first read X to understand the context" when you can embed the relevant excerpt directly.

DecisionBench shows that on-demand context retrieval inside the sub-agent degrades routing fidelity vs. preloaded context, regardless of profile quality.

- **Preferred:** include the relevant file excerpt, prior decision, or background fact inline in the prompt
- **Avoid:** "Read harness/_runtime.md first to understand the context"
- **Exception:** if the context is too large to embed (> ~2000 tokens of relevant material), note this in the description as a known routing degradation: `"[context too large to preload — sub-agent will retrieve on-demand]"`

## Enforcement

Harness-behavioral (Tier 1). Tier 2 queue: `AgentRoutingRationaleContract` in `core/contracts.py`.

## Recovery

If fired:
1. Add a routing rationale clause to the `description`.
2. Move relevant background context inline into the `prompt` rather than leaving it for the sub-agent to fetch.

## Interaction with existing contracts

- Extends `agent-invocation-scope`: that contract requires scope + stop criterion + tool allowlists; this adds routing rationale to the pre-flight checklist.
- Complements `parallel-agent-consensus-guard`: knowing why each specialist was chosen makes it easier to detect when specialists were given overlapping sources.
- Complements `behavioral-haiku-guard`: undocumented routing choices are a form of implicit deferral.

## Research basis

**DecisionBench: A Benchmark for Emergent Delegation in Long-Horizon Agentic Workflows** (arXiv cs.AI, May 2026)

- Routing fidelity-at-1: 7.5%–29.5% across awareness conditions at near-equal quality
- Quality metrics statistically flat (|β| ≤ 0.010, p ≥ 0.21) — routing failures are quality-invisible
- Delivery channel dominates description content for routing accuracy
- Counterfactual ceiling: perfect delegation would score 15–31 pp higher than measured

Caveat: benchmark uses a fixed delegation interface (`call_model`) and does not test emergent delegation where the orchestrator learns when to delegate. Shadow's use case is closer to the fixed-interface case, so the finding is applicable.