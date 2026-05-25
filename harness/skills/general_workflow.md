# Skill: general_workflow

## Role sequence
Triage -> Execute -> Verify

## Stage: Triage
1. Read `memory/session_handoff.md` to orient on current state and open tasks.
2. If a message ends with `...` mid-sentence or mid-list, flag it explicitly before proceeding: "This message appears truncated — conclusions may be incomplete."
3. Check git log for loops: `git log --oneline -10` on any file touched 3+ times this session.
4. If the user corrects a mutating task after visible confusion or frustration, stop actions based on the prior model before continuing.
5. For similarly named repos, public/private exports, remotes, approval prompts, or external artifacts, restate the corrected entity split before the next mutation: target, owner/location, exposure boundary, and excluded lookalikes.

## Stage: Execute
1. For feedback/correction from the user: write memory immediately (Read MEMORY.md → Write new file → Edit MEMORY.md index).
2. For code tasks: Read the target file before any Edit. Never edit blind.
3. For file discovery: use Glob for known patterns; use Grep for symbol/keyword searches; spawn Explore agent only if scope spans >3 files or requires multiple rounds.
4. Chain dependent edits sequentially; independent reads/writes run in parallel.
5. After a corrected entity split, mark prior dependent tool actions suspect and verify live targets before repo creates, remote edits, pushes, publishes, or credential writes.

## Stage: Verify
1. After any Edit, confirm the change is semantically correct — do not re-read to verify (Edit errors on failure).
2. After memory writes, confirm MEMORY.md index entry matches the file written.
3. If work was interrupted by a correction mid-task, resume the original task explicitly after saving the correction.

## Key patterns
- `mcp__shadow__run_shell` for shell commands; never raw Bash for grep/find when Grep/Glob suffice.
- Feedback corrections go to memory files in `/home/agentshadow/.claude/projects/-home-agentshadow-shadow/memory/` — never inline.
- Truncated messages (`...`) must be flagged before drawing conclusions from them.
- Default to action: save the feedback AND continue the interrupted task in the same turn.

## Contracts referenced
- `loop-tripwire` — blocks 3+ edits to same file this session
- `persistent-correction` — recurrence of corrected behavior
- `memory-write-guard` — memory writes outside allowed paths
