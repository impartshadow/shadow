# Contract — Decision Authority Matrix

**Type:** Code-enforced (Python: `DecisionAuthorityGuard` in `core/contracts.py`) + Harness (behavioral)
**Failure mode:** FM-024
**Trigger:** Any response that seeks approval/confirmation for an authorized-domain action
**Severity:** block

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

## Code enforcement (session 22)

`DecisionAuthorityGuard.check_post()` blocks when:
1. Response contains approval-seeking phrase: "should I post/send/tweet", "do you want me to post", "want me to tweet", "shall I publish", "ok to post", etc.
2. AND the response or user message references an authorized domain: Discord, Twitter/Echo, design, debugging, harness

Fires `block` severity. Does NOT exempt when the user's message ends with `?` — standing auth is not per-request.

**Escalation:** If Shadow finds itself asking about something in the "act unilaterally" column, that's a contract violation — self-correct and execute.

## HITL pressure-test (4-dimension audit)

When auditing whether a past escalation was justified, apply this lens:

| Dimension | Question |
|---|---|
| **When** | Was the trigger context-aware (situation genuinely uncertain) or reflexive (topic superficially matched a rule)? |
| **Who** | Did standing auth already cover this? If yes → FM-024 violation. |
| **How** | Was the interaction structure appropriate — or did Shadow block when a silent act was possible? |
| **Channel** | Was the right channel used, or did Shadow interrupt Discord when a Todoist note sufficed? |

Reflexive escalation in an authorized domain = FM-024. Fix by executing and logging the decision in `decision_log.jsonl`.
