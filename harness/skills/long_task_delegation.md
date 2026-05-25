# Skill: Long Task Delegation

**Type:** Harness skill  
**Trigger:** Shadow is packaging a multi-step task for autonomous execution (nightly job, idle task, or loop)

## Role sequence

Spec → Validate → Delegate → Verify

## Stages

### Stage 1: Spec
1. Write explicit **success criteria** — not "research X" but "produce a 3-bullet summary of X written to state/Y.md"
2. Write **failure criteria** — what observable state means the task went wrong (file not written, exit nonzero, Discord post missing)
3. Identify **self-correction triggers** — what the agent should retry (max 3) vs. escalate to the user

### Stage 2: Validate
4. Confirm the task has access to all tools and state it needs before handing off
5. Estimate max wall-clock time. If > 10 minutes, flag as high-autonomy and name the expected output artifact explicitly

### Stage 3: Delegate
6. Write the task prompt to include: goal, numbered steps, success criteria, and an explicit instruction to write outcome to a state file or post to #moonshot
7. Set max_task_seconds if running inside idle_moonshot or nightly

### Stage 4: Verify
8. After execution, check the output artifact exists and matches success criteria
9. If verification fails, log to state/task_log.jsonl with outcome='failed' and root cause

## Contracts referenced
- `loop-tripwire` (FM-003): prevents runaway autonomous rewrites
- `action-deferral-guard` (FM-011): task must be executed, not just described

## Rules
- A task without explicit success criteria is not ready to delegate — write the criteria first
- Self-correction loops must have a maximum iteration count (default: 3)
- Tasks touching live systems (email, Discord, external APIs) require a dry-run verification step before the first autonomous run