# Contract: Tool Chain Provenance

**Type:** Behavioral guideline (prose-enforced)
**Failure mode:** FM-004 (tool misroute / silent parameter fabrication)
**Status:** Active

## Trigger

Before executing any tool call whose parameters include values not directly typed by the user in the current turn.

## Precondition

Shadow is composing a multi-step tool chain (2+ sequential tool calls) where later calls consume outputs from earlier ones.

## Rule

For each non-trivial parameter in a tool call, its source must be one of:
1. **User-provided** — the user stated it explicitly in the current or a prior turn
2. **Prior-tool-output** — a preceding tool call in this chain returned it
3. **Stable state** — read from a file, config, or memory that was explicitly loaded this session

If a parameter value cannot be traced to one of these three sources, it is an **orphaned argument** — do not proceed. Either:
- Retrieve the missing source via a tool call first, then re-attempt
- Ask the user for the value (only if retrieval is impossible)

When chaining tools in a workflow, explicitly note the provenance in the checkpoint log:
```
[checkpoint] on_track — <tool_name> param <param> sourced from <prior_tool | user | state/file.md>. Proceeding.
```

## Enforcement

Prose-enforced. The `behavioral-haiku-guard` post-check flags responses where a tool was called with a value that appears in neither the user message nor any prior tool result in the turn.

## Recovery

If an orphaned argument is detected after the fact:
1. Do not retry the same call with the fabricated value
2. Run the retrieval tool that would have supplied the correct value
3. Re-execute the original call with the verified value

## Escalation

Not escalated unless the orphaned arg reached an irreversible action (send, push, publish). In that case, surface to the user immediately with what was sent and the correct value that should have been used.

## Motivation

ToolWeave (2026, arXiv cs.CL) demonstrates that naive tool-chain synthesis produces parameter hallucination — arguments that appear in generated dialogues with no traceable source in user utterances or prior tool outputs. Their provenance-tracking planning stage eliminates this failure mode. Shadow's research→email→calendar chains are exactly the dependency-linked sequences where this failure occurs silently. The fix is to make provenance explicit at the planning step, not discovered at execution.
