# Skill: Stateful Debug (Episodic Memory for Corrections)

## Overview

**Solvita insight:** Agents accumulate and reuse problem-solving experience across tasks rather than starting fresh each session.

This skill implements episodic memory for correction patterns: before acting on ambiguous tasks, retrieve top-3 similar past corrections from the correction_log in memory/session_handoff.md and apply them as soft priors.

## Role Sequence

1. **Triage**: User message describes an ambiguous or recurring problem domain
2. **Retrieve**: Load correction_log; extract top-3 entries matching current FM-type
3. **Apply Priors**: Boost confidence in catching repeated mistakes
4. **Execute**: Proceed with action, informed by episodic history

## Correction Log Format

| FM-code | Trigger Context | Resolution | Session |
|---------|-----------------|-----------|---------|
| FM-033 | Problem description | What fixed it | session-N |

**Example entries:**
- FM-033 | Ask approval before posting Discord | Stop asking, wire directly | session-45
- FM-011 | Propose instead of executing | Read contracts for action-first rule | session-46

## Retrieval Pattern

1. Extract correction_log table from memory/session_handoff.md
2. Filter by matching FM-code (e.g., FM-033 for persistent-correction triggers)
3. Return top-3 most recent rows
4. Apply as soft priors in PersistentCorrectionGuard.check_post():
   - If recent correction's FM-code matches, boost Haiku score by +0.15
   - Cap at 1.0; allows borderline cases (0.60–0.72) to cross threshold

## Integration Points

- **PersistentCorrectionGuard._load_correction_log()** — loads from markdown table
- **check_post() scoring** — applies soft prior boost
- **Memory system** — correction_log lives in session_handoff.md (persistent across sessions)

## Adding New Corrections

When a correction fires:

1. Extract FM-code and trigger context from correction message
2. Record resolution in CLAUDE.md, contracts, or recovery message
3. Append row to correction_log table in memory/session_handoff.md
4. Next session: soft priors automatically boost detection for similar triggers

Example: User corrects "stop asking for approval" → add row:
```
| FM-033 | Ask approval before posting Discord | Stop asking, wire directly | session-45 |
```

Next time persistent-correction sees approval-seeking language, score +0.15 boost fires.

## Why This Works

- **Episodic, not generic**: corrections tied to specific session context, not static rules
- **Reusable priors**: soft boost prevents edge cases from slipping through
- **Lightweight**: no new infrastructure, reads from existing handoff memory
- **Actionable**: resolutions are specific to what actually worked, not abstract principle
