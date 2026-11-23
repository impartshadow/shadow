# mid-session-restart-guard

**Type:** Pre-check on tool parameters
**Failure mode:** FM-033
**Enforcement:** `core/contracts/code_ops.py:MidSessionRestartGuard`

Blocks a shadow-bot restart command while tracked code files under `core/`,
`harness/`, `scripts/`, `tests/` or `tools/` have uncommitted changes. It reads
`git status --porcelain` at check time. Untracked files and `state/` or `docs/`
changes do not count.

**Limits:** It runs only where pre-checks are dispatched: write tools in
`core/gemini_agent.py` and `core/routing_emergency.py`. Shell commands in Claude and
Codex CLI sessions and the `restart_bot` tool (`core/process_registry.py`) are not
checked, so those restart paths have no uncommitted-code check. It also does not
check for an unpushed commit; the mandate's NO_MID_SESSION_RESTART rule still
requires the push.

**Recovery:** Commit and push the in-flight changes, then restart.
