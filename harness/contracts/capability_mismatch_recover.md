# Contract: capability-mismatch-recover

## Type
Harness-enforced recovery gate — triggered during task decomposition

## Trigger
Any point in task execution where Shadow identifies a needed tool, skill, or access path that is not currently available in the harness.

## Precondition
Before declaring a sub-task "blocked by missing capability", ALL of the following must be completed:
1. Checked `memory/reference_capability_inventory.md` for any listed alternative path
2. Attempted at least one MCP tool that might cover the gap (mcp__shadow__run_shell, mcp__shadow__browse_url, etc.)
3. Searched harness/skills/ for any existing skill that partially covers the need

## Recovery path (in order)

1. **Check inventory** — read `memory/reference_capability_inventory.md`. If an alternative path exists, use it without surfacing the gap to the user.
2. **Try MCP shell escape** — most capability gaps can be bridged via `mcp__shadow__run_shell`. Attempt a shell-based workaround before any other escalation.
3. **Log the gap** — append to `state/capability_gaps.jsonl`:
   ```json
   {"ts": "<ISO>", "task": "<what was needed>", "gap": "<what was missing>", "workaround": "<what was tried>"}
   ```
4. **Decompose differently** — if the capability is genuinely absent, re-decompose the parent task to route around it. Do not surface a dead-end; find the adjacent path.
5. **Surface only if all paths fail** — if steps 1–4 are exhausted, report: "All paths failed — here's what I tried: [output]" and append the gap to the log.

## What NOT to do
- Do not say "I don't have access to X" without completing all precondition steps
- Do not ask the user to provide credentials or access unless step 5 is reached
- Do not silently skip the sub-task — re-decompose or log

## Enforcement
Harness-side only. Violation pattern: outgoing response containing "I don't have" / "I can't" / "not available" without a preceding tool call or investigation output in the same turn.

## Escalation
If the same gap appears in `state/capability_gaps.jsonl` 3+ times across sessions, flag it in the next session startup status report as a structural harness gap for the user to review.
