# memory-pressure-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-017 (RAM exhaustion / OOM during subagent spawn)
**Trigger:** Pre-check on any action whose prompt/response text contains a spawn signal — `Agent(`, `spawn_subagent`, `subagent_type`, `run_supervised_task`, `queue_background_task`.

**Precondition:**
- Block (`severity=error`) when `/proc/meminfo` MemAvailable < 350 MB and a spawn is being proposed.
- Warn (`severity=warn`) when MemAvailable < 500 MB and a spawn is being proposed.
- Skip silently when no spawn signal is present, even if RAM is low — general low-memory state is not by itself a violation.

**Enforcement:** `core/contracts.py:MemoryPressureGuard.check_pre()`.

Reads `/proc/meminfo` directly (no shell-out). Includes a 60 s same-severity
debounce so a single memory dip cannot generate multiple identical warnings
in rapid succession — repeat fires within the debounce window are dropped.

**Recovery:**
- Block: run `ps aux --sort=-%mem | head -15`; kill stale `chrome-devtools-mcp` or completed subagent processes; retry once RAM is recovered.
- Warn: defer the spawn or stage the work serially.

**Escalation:** Not required — log silently. Repeat blocks within a single
session suggest a leak; surface only if `state/contract_violations.jsonl`
shows >5 blocks in 24 h.

**History:**
- 2026-06-04 — Fixed noise pattern: warn-level check was firing on every prompt
  under low RAM regardless of whether a spawn was actually being proposed
  (`ctx.prompt`/`ctx.response` were also nonexistent fields, silently masked by
  `or ""`). Now: only fires when a spawn signal is present, uses the real
  `user_message` / `response_text` fields, and debounces 60 s per severity.
