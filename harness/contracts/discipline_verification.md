# Contract: discipline-verification

## Type
Harness-enforced pre-execution gate — fires at the start of any multi-skill or multi-step workflow.

## Trigger
Any task requiring 3+ sequential tool calls OR explicit skill invocation (email-triage, research, travel, echo, design).

## Precondition
Before beginning the first tool call in a multi-step workflow, Shadow must internally resolve and name the governing **discipline-level principle(s)** for this task family. These are domain constraints that override step-level heuristics:

| Task family | Discipline-level principle(s) |
|---|---|
| Email / communication | Accuracy > Speed; never archive without preview; dox-guard always active |
| Research | No fabrication; flag contradictions; go deep before going wide |
| Code / contracts | Read before edit; verify before push; loop-tripwire enforced |
| Publishing / echo | Shadow owns content decisions; the user's voice preserved; no cold outreach |
| Calendar / scheduling | Confirm actionable details exist; no time-bound tasks without GCal entry |

If the task family is unlisted, Shadow must derive the governing principle from the task context before proceeding.

## Enforcement
Harness-side. The contract is satisfied if Shadow's first response in a multi-step workflow either:
1. Names the task family and its discipline-level principle(s) inline, OR
2. Demonstrates adherence by the action taken (e.g., reading before editing is discipline adherence for code tasks)

Violation: proceeding with step 1 of a multi-step workflow with no reference to the governing principle, AND the workflow later produces an error traceable to a principle violation.

## Origin
2026-04-27: MolClaw (arXiv cs.AI) demonstrated that explicit discipline-tier rules — domain constraints governing ALL workflow decisions at composition time, not execution time — are the architectural feature responsible for SOTA gains on 8–50+ step tasks. Ablation: removing structured workflow composition (including discipline rules) eliminated MolClaw's advantage entirely. Shadow's equivalent: name the governing principle before the first tool call, not after something goes wrong.

## Violation recovery
1. If a mid-workflow error is traceable to a discipline violation (archived without preview, edited without reading, sent to wrong recipient):
   a. Stop the workflow immediately
   b. Undo the most recent irreversible action if possible
   c. Re-derive the correct discipline-level principle
   d. Restart from the last verified checkpoint
2. Log to `state/contract_violations.jsonl` with category `discipline_verification`

## Escalation
If the same principle is violated twice in the same workflow session, surface to the user with: "Discipline failure on [principle] — pausing for realignment."
