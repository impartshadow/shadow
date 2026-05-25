# Skill: workflow-composition

## Role sequence
Triage -> Execute -> Verify

## Purpose
Governs how Shadow composes multi-step workflows that chain multiple skills or 5+ sequential tool calls. Directly implements the three-tier hierarchy insight: tool-level (atomic ops) → workflow-level (validated pipelines) → discipline-level (governing principles).

Use this skill when:
- A task requires 5+ sequential tool calls
- Two or more named skills are being combined (e.g., research + email-triage)
- The task has branching logic (different actions depending on intermediate results)

## Stage: Triage
1. Name the task family and resolve discipline-level principle(s) — contract: `discipline-verification`
2. Decompose into workflow segments: each segment is 3–7 tool calls with a verifiable intermediate output
3. Identify irreversible actions (send, archive, push, publish) — these are segment boundaries
4. If the task has ≥2 irreversible actions, confirm the full plan with the user before executing
5. **Provenance map (required for chains of 3+ tool calls):** Before executing, list each planned tool call and where each non-trivial parameter comes from. Format:
   ```
   tool_chain_plan:
     1. <tool_name>(<param>=<source: user | prior_tool_N | state/file>)
     2. <tool_name>(<param>=<source>)
     ...
   ```
   Any parameter whose source is `unknown` is an orphaned argument — resolve it (via retrieval or user clarification) before proceeding. Never fabricate a value. See contract: `tool_chain_provenance`.

## Stage: Execute
1. Execute segment 1 to its verifiable intermediate output
2. **Embedded quality checkpoint** (required before proceeding to next segment):
   - State: `on_track | drifting | stuck` — contract: `step-state-tracking`
   - Verify: does the intermediate output match what the next segment expects as input?
   - **Provenance check**: confirm each parameter for the next tool call can be traced to user input, this segment's output, or loaded state. If a param has no traceable source, stop and retrieve it before continuing.
   - If `drifting`: name what diverged, apply one corrective step, then continue
   - If `stuck`: surface to the user immediately with one alternative tried
3. Proceed to segment 2 only after checkpoint passes
4. Repeat for each segment

### Quality checkpoint format (terse, inline)
```
[checkpoint] on_track — <intermediate output verified>. Proceeding to segment N.
```
or
```
[checkpoint] drifting — <what diverged>. Corrective: <action taken>.
```
or
```
[checkpoint] provenance-gap — <param> for <next_tool> has no source. Resolving via <retrieval_action>.
```

## Stage: Verify
1. Confirm all segment outputs are coherent end-to-end
2. Confirm no discipline-level principle was violated across the full workflow
3. Confirm no tool call in the chain used an orphaned argument (no provenance-gap checkpoints that were papered over)
4. Log completion to `state/task_log.jsonl` with `workflow_segments: N`

## Contracts referenced
- `discipline-verification` — name governing principles before first tool call
- `step-state-tracking` — label state at each segment boundary
- `tool_chain_provenance` — parameter source must be traceable to user, prior tool output, or loaded state
- `verify-before-push` — applies to any push within a workflow
- `loop-tripwire` — if the same segment fails 3 times, stop and escalate

## Anti-patterns (directly from MolClaw ablation + ToolWeave)
- **Ad-hoc tool chains**: running tools in sequence without segment structure — loses coherence by step 5+
- **Deferred quality checks**: running all tools first, verifying at the end — errors compound silently
- **Ignoring discipline tier**: executing workflow steps without having named the governing principle — produces locally correct but globally wrong outputs
- **Orphaned arguments**: passing a value to a tool that was not provided by the user or returned by a prior tool — silent fabrication; caught by `tool_chain_provenance` contract

## Skill audit: reflection gate
MolClaw (2026): performance gains concentrate at workflow-level skills with embedded reflection, not at tool tier. Any skill file in `harness/skills/` that lacks an explicit quality-check or reflection step is a first-class improvement candidate. Skills without it: treat as missing a segment boundary.

Current skill coverage:
- `workflow_composition.md` — reflection built in ✅
- `research.md` — verify step present ✅
- `email_triage.md` — verify step present ✅
- `prospective_retry.md` — check step present ✅
- `echo.md` — reflection step added 2026-04-27 ✅
- `design.md` — verify partial (3 checks) ⚠️
- `travel.md` — verify partial ⚠️
