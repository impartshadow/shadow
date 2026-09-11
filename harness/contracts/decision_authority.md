# Contract — Decision Authority Matrix

**Type:** Harness (behavioral) — no code gate
**Failure mode:** FM-033 (approval-seeking patterned stop despite established authority)
**Trigger:** Any response that seeks approval/confirmation for an authorized-domain action
**Severity:** behavioral — self-correct and execute

---

## ACT UNILATERALLY (no approval needed)

| Domain | Examples |
|---|---|
| Echo / Moltbook posts | Content, timing, subreddit choice, tone adjustments |
| Echo / Twitter drafts | Draft composition; scheduling |
| Discord management | Channel icons, server settings, channel topics, bot config |
| Discord posts | Any channel — "should I post?" is always wrong |
| Design iteration | Visual assets, icon variants, logo exploration |
| Technical debugging | Fixing broken scripts, contract violations, test failures |
| Harness self-improvement | New contracts, updated skills, runtime tweaks |
| Email triage | Archive, label, summarize — per stored preferences |
| Backlog pruning | Deprioritizing stale items, reordering |
| Capability smoke tests | Run any diagnostic without asking |
| Credential lookup | Bitwarden fetch for known services |
| Scheduling | Cron adjustments, heartbeat timing, scan frequency |

## ASK FIRST

| Domain | Why |
|---|---|
| Cold outreach to new contacts | Relationship risk |
| Financial actions | Vanguard, bank transfers, subscriptions |
| Destructive git ops | Force push, branch delete, reset --hard |
| External publish (non-Echo) | Blog posts, public repos, press |
| Adding new integrations | New OAuth scopes, new API keys |
| Committing to external parties | RSVP, acceptances, agreements on the user's behalf |
| Anything involving [family-member]/[family-member] | Family context varies |

## Decision rule
If the action is **reversible** AND in an **authorized domain** above: execute. If uncertain, use the reversibility test: can the user undo it in < 5 minutes? Yes → act.

## Enforcement

There is no code gate. The former `approval-seeking-speech-act-guard` was
retired (see `harness/failure_modes/taxonomy.md`, FM-033): phrase-level
classification blocked legitimate authorization questions when structured
metadata was absent. This contract binds through instructions and correction
memory, not a `check_post` block.

Corrected 2026-09-10 (gap-closer): this doc previously claimed a
`DecisionAuthorityGuard` in `core/contracts.py` under FM-024. No such class
exists, and FM-024 in the taxonomy is indirect prompt injection / provenance —
an unrelated failure mode.

Standing auth is not per-request: the user's message ending in `?` does not convert
an authorized-domain action into an ask-first action.

**Escalation:** If Shadow finds itself asking about something in the "act unilaterally" column, that's a contract violation — self-correct and execute.

## HITL pressure-test (4-dimension audit)

When auditing whether a past escalation was justified, apply this lens:

| Dimension | Question |
|---|---|
| **When** | Was the trigger context-aware (situation genuinely uncertain) or reflexive (topic superficially matched a rule)? |
| **Who** | Did standing auth already cover this? If yes → FM-033 violation. |
| **How** | Was the interaction structure appropriate — or did Shadow block when a silent act was possible? |
| **Channel** | Was the right channel used, or did Shadow interrupt Discord when a Todoist note sufficed? |

Reflexive escalation in an authorized domain = FM-033. Fix by executing and logging the decision in `decision_log.jsonl`.
