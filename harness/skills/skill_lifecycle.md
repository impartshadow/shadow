# Skill: skill_lifecycle

## Role sequence
Triage -> Execute -> Verify

## Purpose
Governs how Shadow skills are discovered, promoted to first-class files, and retired.
Maps to COSPLAY's co-evolution loop: execution trace → pattern extraction → skill bank update.
Also implements the Skillhub Insight→Skill→Actor loop: session handoff history (Insight feed)
→ extracted mechanics (Skill Agent) → loaded at session start (Actor).

## Stage: Triage
1. Trigger: idle task fires OR `/improve` runs OR the user asks to codify a pattern
2. Source types:
   - `state/task_log.jsonl` — outcome-labeled execution records
   - `state/decision_log.jsonl` — reasoning traces
   - `state/contract_violations.jsonl` — failure-path patterns
   - `memory/session_handoff.md` (via `git log -- memory/session_handoff.md`) — qualitative session-level wins not captured in structured logs; treat recurring phrases in 'what worked' / 'carry forward' sections as promotable candidates
3. Check `harness/skills/` for an existing skill before creating a new file

## Stage: Execute — skill discovery
1. Mine source log for (trigger, action_sequence, outcome) tuples
2. Cluster by shared action_sequence prefix (2-gram minimum)
3. Compute rough precision: `successes / (successes + failures)` for each cluster
4. Promote if: precision ≥ 0.80 AND cluster size ≥ 5 occurrences in rolling 30 days (task_log source)
   OR tactic appears in 3+ of last 8 session handoff snapshots (session_handoff source)
5. **Critic step — redundancy check**: before creating a new file, read the 2-3 most semantically similar existing skills. If >50% of the proposed steps already appear in an existing skill, extend that file instead of creating a new one.
6. Draft `harness/skills/discovered_<name>.md` using standard skill template
7. Tag with `discovered_from: task_log | decision_log | session_handoff` and `confidence: 0.0–1.0`
8. **Reconstruction gate (deduction pass)**: after drafting, run `_run_skill_reconstruction_check()` — given only the drafted skill text, verify it can reproduce the original trigger pattern. If the check returns False (reconstruction score < 0.5), discard the draft and log reason to `state/decision_log.jsonl` with `category: skill_lifecycle_rejected`. This prevents abstracting skills that are too specific to their source trajectory to generalize.

## Stage: Execute — skill pruning
1. Monthly: scan all `discovered_*.md` files
2. Re-run precision computation against latest 30-day window
3. If precision drops below 0.60 OR cluster size falls below 3: archive to `harness/skills/retired/`
4. Never delete a skill written by the user — only auto-discovered ones are eligible for pruning

## Stage: Verify
1. After promotion: confirm skill file is syntactically valid (has Role sequence, at least one Stage)
2. After pruning: post summary to #moonshot — name, precision at retirement, replacement if any
3. Log promotion/retirement decision to `state/decision_log.jsonl` with category `skill_lifecycle`

## Contracts referenced
- `loop-tripwire` — don't re-edit the same skill file 3+ times in one session
- `fabricated-gap-guard` — don't claim a skill gap without checking harness/skills/ first

## Output format
- New skill: `harness/skills/discovered_<name>.md` + #moonshot post
- Pruned skill: moved to `harness/skills/retired/` + #moonshot post
- No candidate: post 'No promotable skill found (30d window)' to #moonshot
- Rejected candidate: log to `state/decision_log.jsonl` (no #moonshot post needed)
