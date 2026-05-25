# Session Handoff Append Policy

**Type:** Behavioral contract (prose)

**Trigger:** Every session_handoff.md update (end-of-session or mid-session push).

**Rule:** `memory/session_handoff.md` is an **append log**, not a single overwritten summary.

- Write the new session block at the **top** of the file (prepend, newest-first)
- Keep the last 5 raw session blocks intact below the current consolidated summary
- Never delete or rewrite prior session blocks during a normal session write
- The consolidated "Standing decisions" and "Up next" sections may be updated freely
- Raw session blocks (Done last session, commits) are immutable once written

**Format:**
```
# Session Handoff
**Last updated:** <date>

## Done last session
<new block>

---
<!-- raw episode archive — do not overwrite -->
## [Previous session YYYY-MM-DD]
<prior block>

## [Previous session YYYY-MM-DD]
<prior block>
... (up to 5 prior blocks)
```

**Enforcement:** Prose (behavioral).

**Recovery:** If a session write would overwrite prior blocks, append instead and post a note to #shadow-log.

**Research basis:** arXiv 2026 — "Useful Memories Become Faulty When Continuously Updated by LLMs". Raw episode preservation outperformed consolidated rewrites; the append-only approach preserves authoritative ground truth that consolidation degrades.
