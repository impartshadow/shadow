# Contract: parallel-agent-consensus-guard

## Type
Post-check — observational, warn-only.

## Trigger
Any session where two or more parallel Agent calls return results that are substantively identical (same conclusion, same sources, same framing) on a task that was open-ended or uncertain.

## The problem this solves

The naive model of multi-agent verification is: if two independent agents agree, the answer is more likely correct. This is only true if the agents were genuinely independent. If they shared context, a corrupted source, or a common retrieval artifact, they will agree *because they were both wrong in the same way* — not because they independently converged on truth.

HAM³ (CVPR 2026) demonstrates that coordinated attacks on multi-modal multi-agent systems produce correlated errors in >50% of successful cases. The system appears maximally confident while being systematically wrong. The threat model for parallel Shadow agents is not "one agent fails" — it is **"all agents agree on the wrong answer."**

This is distinct from `context-contamination` (FM-034), which covers repeated tool calls with errors in the retry path. This contract covers correlated *success* across agents that were never individually flagged as failing.

## Precondition

This contract fires when:
1. Two or more Agent calls were issued in the same turn or within the same research task.
2. Their returned conclusions are substantively identical (same factual claim, same source citation, same recommended action).
3. The task was open-ended enough that independent agents should plausibly have returned different framings or emphasis.

## Rule

**High agreement from parallel agents on uncertain tasks is a warning, not a confidence signal.**

When this fires:
1. Do not present the consensus as verified or high-confidence.
2. Inspect whether the agents received overlapping context — shared tool call results, same URL, same document chunk.
3. If overlap is confirmed, treat the result as a single data point, not corroborated evidence.
4. If the task is high-stakes (publishing, financial, code deployment), spawn a third agent with a *deliberately different retrieval path* before proceeding.
5. Log the overlap in the session handoff under "Evidence gaps."

## What independent context looks like

Agents are genuinely independent when:
- They received different seed documents or search queries.
- They were not given each other's intermediate outputs.
- Their prompts do not reference the same named source.

Agents are *not* independent when:
- One agent's output was fed into another's prompt.
- Both agents searched the same query string.
- Both agents fetched the same URL.

## Enforcement

Tier 2 code contract: `ParallelAgentConsensusGuard` in `core/contracts.py` (to be added — see Tier 2 queue).
Until code enforcement is wired: this is a harness-enforced behavioral rule Shadow must apply manually when consolidating multi-agent research.

## Interaction with existing contracts

- Extends `agent-invocation-scope`: that contract requires tool allowlists to prevent scope overlap; this contract catches the case where scope was isolated but *content* converged anyway.
- Complements `research-verification`: verification requires checking sources, not just agent count.
- Complements `partial-evidence-flag`: when consensus is suspect, the result should be flagged as partial evidence.

## Research basis

**HAM³ — Hierarchical Attacks for Multi-Modal Multi-Agent Reasoning** (CVPR 2026)

Tested across ReAct, Plan-and-Solve, and Reflexion paradigms. >50% of successful attacks produced correlated errors across multiple agents. Reasoning-layer attacks (which inject adversarial content into the reasoning trace rather than the input image) outperformed perception and communication layer attacks. Key implication: the attack surface is the *shared reasoning substrate*, not just the perceptual inputs.

External validity caveat: the 78.3% ASR was measured on GQA (visual QA), not agentic tasks with real-world consequences. The attack framework requires grey/white-box access not available in Shadow's deployment context. The defense (independent context isolation + disagreement detection) is warranted regardless, because the correlated failure mode can arise from non-adversarial causes (shared caches, duplicate retrieval) as well.
