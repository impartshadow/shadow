# Skill: Overnight Work Queue

## Overview

When the user signs off ("I'm going to bed", "let's pick up tomorrow", "keep working on this"), Shadow has a wide-open mandate to keep moving but a narrow real prior on what the desired output is. The default failure mode is one of:

- Shadow picks a generic task (post to Echo, run a digest) that doesn't move the strategic thread the user was on.
- Shadow attempts the full strategic thread, fumbles a sub-step, and the user wakes up to an inflight mess.
- Shadow produces a sprawling research dump that doesn't connect to morning action.

The fix is a structured decomposition of the user's last strategic thread into an ordered, time-budgeted overnight queue, with a morning brief that summarizes what landed and what's next.

Backlog origin: `20260614T075704_interaction_theme_an_2627` (overnight ambiguity, 2026-06-14).
Adjacent infrastructure: `scripts/idle_moonshot.py` (idle micro-tasks), `scripts/daily_commander_brief.py` (6am brief).

## When to use

Trigger this skill on the first turn after the user signals end-of-session for the night. Detection signals:

- "going to bed" / "going to sleep" / "headed to bed" / "calling it a night" / "see you in the morning"
- "keep [working|moving|going] on this" right after a strategic thread
- "work on X overnight" / "have X ready by morning"

NOT a trigger: the user pivoting mid-session ("let's switch to Y"), the user stepping away for a meeting, the user pausing on a single task.

## State shape

A single `state/overnight_queue.jsonl` (append-only) with one entry per planning round:

```json
{
  "round_id": "2026-06-15T03:00",
  "created_at": "ISO-8601",
  "trigger_message": "I'm going to bed, keep working on shadow-kit positioning",
  "strategic_thread": "shadow-kit positioning — open-core wedge vs closed proprietary, what to put in the README hero",
  "tasks": [
    {
      "task_id": "shadow-kit-pos-1",
      "kind": "research",                  // research | code | docs | tests | commit | brief
      "instruction": "Survey 5 comparable open-core agent-governance frameworks; capture wedge wording for each",
      "time_budget_min": 30,
      "depends_on": [],
      "outputs_to": "state/research/shadow_kit_pos_competitors.md",
      "status": "pending"                   // pending | in_progress | done | failed | skipped
    },
    {
      "task_id": "shadow-kit-pos-2",
      "kind": "docs",
      "instruction": "Rewrite shadow-kit README hero to lead with the 1-sentence wedge",
      "time_budget_min": 20,
      "depends_on": ["shadow-kit-pos-1"],
      "outputs_to": "shadow-kit/README.md",
      "status": "pending"
    }
  ],
  "morning_brief_target": "06:00 CT",
  "total_budget_min": 240
}
```

## Flow lifecycle

1. **Decompose** — extract the strategic thread from the trigger message + last 5 turns. Use Opus (via `ask(model=_DEEP_REASONING_MODEL)`) to decompose into 3–8 ordered tasks with explicit `outputs_to` paths. Each task must produce a real artifact (a file, a commit, a publication).
2. **Validate budget** — sum `time_budget_min`. If total > 240 min (4 hours), drop the lowest-leverage tasks. the user should wake to a focused result, not 8 hours of churn.
3. **Execute serially** — process tasks in `depends_on` order. On `kind=code`/`commit`, follow CLAUDE.md rules #29 (rev-parse HEAD), #30 (no premature "done"), and rule #3 (verification citation).
4. **On failure** — set `status=failed` with a short reason; do not block downstream tasks unless they explicitly depend on the failed one.
5. **Morning brief** — at the configured target time (default 6am CT, ties into `daily_commander_brief.py`), emit a summary with what landed, what failed, and what's queued for the user's review.

## Hard stops

1. **No commits without tests** — code tasks must include or update tests before commit; if tests fail, status=failed and HALT downstream.
2. **No external broadcasts** — no email, no Substack publish, no Echo posts unless the trigger message explicitly authorized one.
3. **No deletes** — destructive operations (file rm, branch delete, account close) are off-limits overnight without an explicit the user-authorization in the trigger message.
4. **Budget guardrail** — if the cumulative actual time hits 1.5x the planned budget, HALT remaining tasks and write the partial-progress brief.

## Why this exists

The 2026-06-14 overnight session produced sprawling output without a clear strategic anchor; the user woke to a digest he had to parse before knowing what mattered. The fix is structured decomposition + a morning brief that leads with what landed.

## Reference

- Script: `scripts/daily_commander_brief.py` (6am brief — overnight queue feeds into this)
- Script: `scripts/idle_moonshot.py` (idle micro-tasks — distinct from overnight queue; runs from cron, not end-of-session)
- Memory: `feedback_distribution_over_production.md` (rule #17 — overnight tasks favor distribution when briefs are queued)
- CLAUDE.md rule #26 (multi-step task flows execute end-to-end in one pass)
