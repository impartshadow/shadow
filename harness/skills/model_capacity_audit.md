---
name: model-capacity-audit
description: Audit whether Shadow is using Codex and Claude subscription capacity responsibly, report available quota and resets, and allocate useful work. Use for recurring questions about unused usage, model capacity, or plan value.
---

# Skill: Model capacity audit

## When to invoke

Are we using all of our Codex and Claude usage responsibly? Do we have a lot
of usage we could use? How much model capacity is left, and what useful work
should use it? Are we wasting our subscriptions or leaving valuable capacity
unused? Run this audit for these recurring questions.

Read the full `harness/skills/model_capacity_audit.md` before executing; a
retrieved excerpt is only the entrypoint. Report actual provider quota windows,
assess useful outcomes, and execute the supported improvement.

## Role sequence
Re-anchor → Read meters → Assess outcomes → Execute → Report

## Stage: Re-anchor

Work in `/home/agentshadow/shadow`. Call `check_decisions` for usage, quota,
model routing and subscription corrections; read `state/mandate.md` and
`state/will_prefs.md`. If MCP tools are unavailable, the same canonical wrappers
are callable from `core.mcp_server`. Keep this audit inline in interactive work.

## Stage: Read meters

- Codex: inspect `scripts/codex_usage.py` and
  `core.model_codex.codex_read_rate_from_rollouts()`. Read the newest raw
  `token_count.rate_limits` event in `~/.codex/sessions/` to retain its limit ID,
  scope, plan, individual limit and every window. Select by event timestamp,
  not file modification order. Validate `window_minutes`: 300 means five hours,
  10080 means seven days. Either slot may contain the weekly window. A lone
  short window is not a weekly reading. Missing windows are unknown, not zero.
- Claude: call `core.claude_quota.fetch_usage()` and inspect the raw payload
  alongside `utilization(payload)`. Report `five_hour`, `seven_day`, and each
  model-specific `limits` entry separately, including its reset if supplied.
  An exhausted Fable allowance does not prove other Claude models are exhausted.
- `state/claude_quota.json` is the existing sampler's last observation; Codex
  also persists a rate-status cache through `core/model_codex.py`. These are
  valid historical sources, with their timestamps and calibration status.
  If refresh fails, try the existing home-proxy path where relevant, then label
  the last observation's source, age and limitation. A 429 from the telemetry
  endpoint alone does not prove inference quota exhaustion. Do not repeatedly
  poll it or start a model session merely to obtain a quota reading.
- Compute remaining percentage only as 100 minus an observed meter. Display
  observation and reset times using `ZoneInfo('America/Chicago')`. Do not infer
  missing reset times or future availability. A past reset invalidates a
  current-headroom claim from that snapshot.

Never substitute local token totals, cache hits, API-equivalent prices, old
allocator defaults, or a model-specific meter for account subscription usage.
The percentages do not establish how many tasks remain or marginal dollar cost.

## Stage: Assess outcomes

Read `core/model_routing_policy.py`, current cooldown state, recent
`state/token_usage.jsonl` and `state/autonomous_executor_log.jsonl`, and the
runtime fingerprint/process when judging activation. Use
`scripts.usage_by_script.load_records()` for bounded attribution; token logs
cover recorded calls, not necessarily every provider call. Compare periods and
model/task mix without treating call counts as quota percentages.

Inspect `state/commitments.json`, `core.work_ledger.build_snapshot()`, recent
research intake and its experiment receipts. Distinguish delivered outcomes,
successful implementations, waiting for external feedback, repeated closure
checks, failed retries and internal activity. Inspect a suspected waste owner's
current source and live receipts before declaring it faulty or changing it.

Answer both questions independently: is useful capacity available, and is it
being converted into responsibilities the user can stop managing? Spare quota alone
does not prove waste, an absence of valuable work, or a reason to downgrade.
Compare the strongest useful next action with preserving capacity for interactive
work and recovery. Label unproven tactics; do not invent work to hit a burn target.

## Stage: Execute

Execute the strongest authorized, reversible improvement supported by the audit.
Use existing execution owners and canonical model routing. Keep evidence-backed
unfinished actions in their existing lifecycle. Preserve pauses and external
waiting conditions; spare quota is not permission to restart a paused fleet,
launch interactive subagents, create new recurring alerts or make new outreach.
Do not copy the old frontier allocator's static commercial work orders or assumed
model hierarchy. Plan or routing changes require current evidence and the
existing authority envelope; do not change subscriptions from utilization alone.

## Stage: Report

Lead with available headroom and a candid responsibility assessment. Include:

- Provider/window/scope, percent used and remaining, reset in Central Time.
- Source observation times and any stale, absent or failed-refresh limitation.
- Useful outcomes versus concrete waste evidence; attribution limits.
- The improvement executed, its observed result, and any owned next action.

Put findings in the reply, not only in a file. For changes, finish affected-path
checks, live entrypoint execution, commit/push and required activation. Avoid
claiming optimal use or reliable future behavior from a skill installation alone.
