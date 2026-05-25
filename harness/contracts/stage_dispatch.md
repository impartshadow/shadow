# Contract: stage-dispatch

## Type
Harness-enforced stage-ordering gate. Fires before any capability invocation that could advance the session to an irreversible stage.

## Motivation
SDOF (arXiv 2026) demonstrates that multi-agent systems with deterministic FSM pre/post-condition checks on every skill invocation achieve 100% precision blocking illegal operations — vs. asking the LLM to reason about ordering at runtime. The alignment tax comes from conflating intent routing with stage enforcement. Separate them: route with the model, enforce with code.

## Stage model

Shadow tasks follow a directed stage graph. Not all stages are required for every task, but no stage may be skipped *forward* more than one hop without an explicit override.

```
TRIAGE → RESEARCH → DRAFT → VERIFY → PUBLISH
                                  ↘ GIT → NOTIFY
```

| Stage | Code | Capabilities that belong here |
|---|---|---|
| Triage | S0 | Reading context, resolving intent, reading session_handoff.md, reading mind.md |
| Research | S1 | mcp__shadow__web_search, mcp__shadow__browse_url, reading external files, Telegram context pull |
| Draft | S2 | Composing post/email/brief text, generating code, editing files |
| Verify | S3 | Running tests (pytest), checking diffs, smoke tests, reading back what was written |
| Publish | S4 | mcp__shadow__post_to_discord, Substack publish, X post, email send via gmail_manage.py |
| Git | S5 | git commit, git push |
| Notify | S6 | Surfacing results to the user, posting to #shadow-hq |

## Valid transitions

- **Always valid**: staying in the same stage, moving forward one stage
- **Valid with explicit justification**: skipping forward two stages (e.g., S1→S3 when draft is trivial)
- **Invalid**: moving backward (e.g., S4→S2 — if publish revealed a draft problem, open a new task), skipping three or more stages

## Precondition

Before invoking a capability at stage Sn, the session must have completed at least stage S(n-2). Specifically:
- **Never PUBLISH (S4) before VERIFY (S3)** — the verify_before_push contract enforces this but stage_dispatch is the upstream model
- **Never GIT (S5) before VERIFY (S3)** — same enforcement
- **Never DRAFT (S2) before TRIAGE (S0)** — do not compose without resolving context first

## Enforcement

Harness-side + code target. The `step_state_tracking` contract handles within-stage drift. This contract governs cross-stage ordering.

Code enforcement target: `core/contracts.py` — `SkillStageContract` subclass. Each registered skill should declare `stage: str` and `check_pre()` should reject invocations that violate the ordering above by comparing `ctx.current_stage` to `self.stage`.

Until code enforcement is live, Shadow self-labels the current stage before each capability group invocation:
- **RESEARCH**: "[S1: research]" before web search or file reads
- **DRAFT**: "[S2: draft]" before composing
- **VERIFY**: "[S3: verify]" before running tests or reading back output
- **PUBLISH**: "[S4: publish]" before any outbound action

## Violation recovery

1. If a publish-stage tool was called before verify: abort, run verification, then re-attempt publish
2. If a draft was composed without triage (missing context): read the session_handoff and Telegram context now, then revise the draft
3. Log the stage-order violation to state/contract_violations.jsonl with contract=stage-dispatch

## Origin
2026-05-18: SDOF paper (arXiv cs.AI) — *Taming the Alignment Tax in Multi-Agent Orchestration with State-Constrained Dispatch*. Key finding: 22/22 illegal HR operations blocked with deterministic FSM checks; intent router (7B) outperforms GPT-4o zero-shot 80.9% vs 48.9% on constrained routing because the FSM removes ambiguity from the routing decision.

## Escalation
If a stage-order violation is detected after an irreversible action (publish, git push): surface immediately to the user with the stage sequence that was executed and the expected sequence.
