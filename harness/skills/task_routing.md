# Skill: task-routing

## Role sequence
Classifier -> Dispatcher -> Tracker

## Purpose
At session entry, route the incoming request to a named skill path before executing anything. Prevents monolithic collapse (FM-011 proxy) where all requests fall through to unstructured handling.

Activate this skill when:
- Session starts with a new user message
- An incoming request has not yet been assigned to a skill path
- A mid-session pivot changes the task family

## Dispatch table

| Request category | Named skill | Signal words |
|---|---|---|
| Research / analysis / deep dive | `research.md` | "research", "find", "analyze", "what does X say", "dd" |
| Email / inbox / Gmail | `email_triage.md` | "email", "inbox", "draft", "send", "gmail" |
| Social / Echo / Moltbook posting | `echo.md` | "post", "echo", "moltbook", "tweet", "publish" |
| Multi-step workflow (5+ tool calls) | `workflow_composition.md` | chains, pipelines, 5+ steps |
| Multi-agent research panel | `multi_agent_research.md` | "panel", "heterogeneous", "multi-agent research" |
| Design / architecture | `design.md` | "design", "architecture", "schema", "model" |
| Travel / scheduling | `travel.md` | "travel", "flight", "hotel", "calendar", "schedule" |

## Research dive discriminator (check FIRST, before signal-word matching)

If the incoming message contains any of the following, it is a **research dive** and routes to `research.md` regardless of other signal words. Do NOT treat it as a code task, echo task, or general workflow.

- A URL pointing to an article, paper, blog post, or repo (`http://`, `https://`, `arxiv.org`, `github.com/`, `huggingface.co/`, `papers.`, `.pdf`)
- Words: "paper", "study", "research", "article", "read this", "look at this", "what do you think of", "dd", "deep dive" combined with a link or title

When a research dive is detected: confirm the routing with one line ("Reading as research dive — [title or domain]") then execute `research.md`. Do NOT execute any other flow first.

## Stage: Classifier
1. **Apply research dive discriminator first** — if matched, route to `research.md` immediately
2. Read the incoming request for other signal words
3. Match against dispatch table — pick the highest-confidence category
4. If no clear match: default to `workflow_composition.md` for multi-step tasks, `research.md` for information tasks
5. Log routing decision silently to `state/task_log.jsonl` under `routed_skill`

## Stage: Dispatcher
1. Load the named skill file mentally — apply its role sequence from this point forward
2. Do NOT re-read this routing skill mid-task unless a pivot occurs
3. If the task straddles two skills (e.g., research + email), use `workflow_composition.md` as the envelope and invoke the sub-skills as segments

## Stage: Tracker
1. After task completion, confirm the routed skill matched the work performed
2. If mismatch (routed to research.md but ended up doing social posting), log `routing_mismatch: true` in task_log entry
3. Routing mismatches are signals for dispatch table improvement — flag in next idle memory consolidation

## Monolith collapse detection
If session_audit.py reports >70% of recent sessions routed to the same skill path, treat as FM-011 (scope overrun / role collapse). Post to #shadow-log and check whether the dispatch table is correctly partitioned.

## Contracts referenced
- `action-deferral-guard` — routing must lead to execution, not proposal
- `behavioral-haiku-guard` — Haiku checks if routing led to denial without attempt
