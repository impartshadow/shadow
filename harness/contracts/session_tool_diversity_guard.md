# session-tool-diversity-guard

**Type:** Post-condition (warn), session-scoped
**Failure mode:** FM-003 (loop / runaway behavior)
**Status:** Planned — Tier 2, pending code implementation in core/contracts.py

## What it enforces

Within a single session, the set of distinct tools invoked should grow gradually and purposefully. A sudden spike in tool diversity — many different tool classes called in rapid succession — is a behavioral signature of prompt-injection attacks that hijack the agent mid-session and redirect it toward unintended capability chains.

This contract tracks `session_tool_calls_history` (list of tool names across all turns this session) and warns when:
- Unique tool count in the last N turns exceeds a threshold relative to the session baseline
- A turn calls tools from 4+ distinct capability classes (browse, email, calendar, shell, git, etc.) with no coherent task context

## Trigger

Fires on `action == 'respond'` when session tool history is available.

## Precondition

`ContractContext.session_tool_calls_history` must be populated by the harness runtime (requires a new field on ContractContext).

## Enforcement

Code-enforced in `core/contracts.py` (planned). Severity: `warn` (not block — legitimate power-user sessions can touch many tools).

## Recovery

On violation: log the tool sequence to deficiency_log.jsonl with `failure_mode: FM-003-trajectory`. Do not block the response. Surface a note in the session summary so nightly can count trajectory anomalies.

## Escalation

If trajectory anomaly count exceeds 3 in a session, escalate to the user via Discord with the tool sequence.

## Architecture note (from research)

Motivated by: *A Low-Latency Fraud Detection Layer for Detecting Adversarial Interaction Patterns in LLM-Powered Agents* (arXiv cs.AI 2026). Their 42-feature taxonomy includes tool-invocation rate and session escalation patterns as leading indicators. Key caveat from the paper: behavioral detection assumes attacks are distinguishable from legitimate power-user behavior — keep severity at `warn` and tune threshold against real session baselines before hardening to `block`.
