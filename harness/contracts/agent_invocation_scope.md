# Contract: agent-invocation-scope

## Type
Harness-enforced pre-condition — fires on any Agent tool invocation.

## Trigger
Any call to the `Agent` tool, whether spawned during an autonomous session or an interactive one.

## The problem this solves

Inter-agent calls without explicit scope are structurally identical to the loop problem that `loop-budget-gate` addresses: the spawning agent cannot verify whether the subagent understood the scope boundary, and the subagent cannot know when to stop or what is out of scope.

The A2A protocol (Google, 2025) handles this with a structured message envelope: every agent↔agent call carries a declared task scope, an expected output format, and a budget or stop criterion. Shadow's `Agent` tool calls currently lack this envelope — descriptions are optional and prompts routinely omit stop criteria.

Motivated by: *Tool Use as Action: Towards Agentic Control in Mobile Core Networks* (May 2026), which demonstrates MCP+A2A as the emergent pattern for structured agent orchestration. Extended by: *Towards Multi-Agent Autonomous Reasoning in Hydrodynamics* (Zhao et al., May 2026), which demonstrates that **per-specialist tool allowlists** are the primary reliability driver in Layer Execution Graph (LEG) architectures — factual precision held above 90% across 1–5 parallel tracks precisely because each specialist could not reach tools outside its domain.

Extended by: *HAM³ — Hierarchical Attacks for Multi-Modal Multi-Agent Reasoning* (CVPR 2026), which shows that shared mutable context across parallel agents is the primary attack surface for correlated errors — agents that share a context reference can all fail identically even when their tool allowlists are properly isolated.

## Precondition

Before invoking the Agent tool, Shadow must:

1. **Scope**: Supply a `description` parameter that states what the subagent should accomplish, in one concrete sentence.
2. **Budget / stop criterion**: When the subagent task is open-ended (research, exploration, multi-step execution), the `prompt` must include either:
   - A turn budget: `"Report back in under N tool calls."`
   - A completion predicate: `"Stop once you have found X."`
3. **Tool allowlist (parallel specialist agents)**: When two or more agents are spawned in parallel — i.e., as specialist forks in a multi-agent research or execution task — each agent's `prompt` must include an explicit statement of which tools it is permitted to use. Format: `"You may use: <tool_a>, <tool_b>. Do not call any other tools."`  This prevents one specialist's tool calls from contaminating the output scope of another and prevents context saturation at the consolidator/reporter layer.
4. **Context isolation (parallel specialist agents)**: When two or more agents are spawned in parallel, each agent must receive an independently constructed context — not a reference to a shared document, shared tool result, or shared intermediate output from another agent. Passing the same URL, the same retrieved document chunk, or the same prior agent's output to multiple parallel agents collapses their independence. If agents must reason about the same source, fetch it separately per agent or serialize the task. The failure mode from shared context is not "one agent fails" — it is **all agents agree on the wrong answer** because they were all poisoned by the same input.
5. **No re-delegation**: The subagent must not be instructed to spawn further agents unless explicitly authorized by the user.

Minimal compliant invocation (single agent):
```
Agent(
  description="Find all callers of foo() in core/ — report file+line only",
  prompt="Search core/ for calls to foo(). List file:line. Stop after first 20 results."
)
```

Minimal compliant invocation (parallel specialist agents):
```
Agent(
  description="Specialist: retrieve hydrodynamics data from arXiv only",
  prompt="You may use: mcp__shadow__browse_url, mcp__shadow__web_search. Do not call any other tools. Fetch the abstract and methods section of <url>. Report findings in under 300 words. Stop after 3 tool calls."
)
```

Note: parallel agents must receive *different* seed URLs or search queries. Do not pass the same URL to two parallel agents — their outputs will not be independent.

## Enforcement

Tier 2 code contract: `AgentInvocationScopeContract` in `core/contracts.py`.
Checks `tool_params` for Agent calls — blocks if `description` is absent; warns if the prompt has no budget/stop signal and the description implies open-ended work. Warns (not blocks) when two or more Agent calls appear in the same turn and none of their prompts include a tool-restriction phrase.

## Recovery

If fired:
1. Add or strengthen the `description` parameter.
2. Append a stop criterion to the `prompt` before re-invoking.
3. For parallel specialist forks, add explicit tool allowlists to each agent prompt.
4. For parallel specialist forks, verify each agent received a distinct seed context — different URLs, different query strings, no shared intermediate outputs.
5. Log the scope in session_handoff.md if the subagent task is non-trivial.

## Escalation

Block (not warn) when `description` is entirely absent. Warn when description exists but prompt is open-ended with no stopping signal. Warn when 2+ parallel agents are spawned without tool allowlists in any of their prompts.

## Interaction with existing contracts

- Extends `loop-budget-gate` (FM-003): that contract covers iterative loops; this covers one-shot Agent spawns.
- Complements `decision-authority` (FM-024): scope declaration makes the authorization trail explicit.
- Complements `fabricated-gap-guard` (FM-021): a scoped Agent prompt is less likely to hallucinate a gap that doesn't exist.
- Complements `research_epistemology`: tool allowlists per specialist reduce the risk of one agent's retrieval contaminating another's findings.
- Complements `parallel-agent-consensus-guard`: context isolation prevents shared-input correlated errors; consensus guard catches correlated errors that slip through anyway.

## Origin
May 2026: *Tool Use as Action* prototype paper (MCP+A2A for 6G network orchestration). Key finding extracted for Shadow: A2A's structured message envelope — scope + stop criterion per inter-agent call — is the missing analog to `loop-budget-gate` for spawned subagents.

Extended May 2026: *Towards Multi-Agent Autonomous Reasoning in Hydrodynamics* (Zhao et al.). Key finding: tool allowlists per specialist agent are the mechanism that keeps parallel forks reliable under concurrency. Accuracy held >90% across 5 parallel tracks; the authors attribute this to role-fidelity enforced by tool isolation, not just prompt instructions.

Extended May 2026: *HAM³ — Hierarchical Attacks for Multi-Modal Multi-Agent Reasoning* (CVPR 2026). Key finding: shared context across parallel agents is the attack surface for correlated errors — all agents fail identically when fed the same poisoned input, regardless of tool isolation. Independent context construction per agent is the required defense.
