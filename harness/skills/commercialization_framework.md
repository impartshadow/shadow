# Skill: Commercialization Decision Framework

## Overview

the user repeatedly asks variants of "how do we turn Shadow / shadow-kit / agent-gateway into a real business?" and "what belongs free vs paid?". Each ask re-litigates the same canonical answers. The fix is a single living venture memo that every commercialization question is answered against — not a 4-turn discussion every time.

Backlog origin: `20260614T075704_interaction_theme_an_3a32` (commercialization re-litigation, 2026-06-14).
Related memory: `project_harness_venture.md` (current venture thesis).

## When to use

Trigger this skill on the first turn that does any of:

- the user asks "should this be free or paid?" / "what's the paid tier?" / "where does the wedge sit?"
- Shadow is about to propose a pricing/packaging/positioning change to the user
- A research output (research_produce, idle_moonshot) reaches a conclusion that affects monetization

## Canonical-answers structure

A single `state/venture_memo.json` (or `harness/skills/venture_memo.md` if narrative-heavy) with these named slots — each must have a current answer AND an `updated_at` timestamp:

| Slot | What it answers | Current default |
|------|------------------|------------------|
| `repo_split` | shadow (private) vs shadow-kit (open-core) vs agent-gateway (productized harness) | shadow=closed proprietary; shadow-kit=BSL/open-core; agent-gateway=enterprise SaaS |
| `paid_tier` | What the paid subscription buys | $7/mo Substack: operator's view + raw decision logs |
| `icp` | Ideal customer profile in 1 sentence | "AI/eng leaders running autonomous agents at scale who need governance visibility, not yet another agent framework" |
| `wedge` | The first thing that gets us a paying customer | Substack subscribers → harness-as-product upsell to agent operators |
| `proof_demo` | The one-link demo that converts skeptics | Shadow's live revenue scoreboard + audit log + autonomous gap-closer trace |
| `pricing` | Tier prices and what gates them | Free Substack; $7/mo paid Substack; enterprise harness pricing per governed agent (TBD) |
| `next_revenue_action` | The single most leveraged action this week | Drive paid Substack conversion via Substack hero + about page rewrite (already shipping) |

Each slot's update should cite the source: a the user message ("the user said X on 2026-06-14"), a real signal (subscriber milestone, churn event), or a memory file. Do NOT update slots from speculation.

## Flow lifecycle

1. **Read first** — before answering any commercialization question, read the memo. If the answer is in the memo and `updated_at` is < 14 days, give that answer plus a 1-line "memo says X, updated Y" attribution.
2. **Update on signal** — when the user changes positioning, when a paying subscriber arrives, when a pricing question is decided, update the relevant slot in the same turn.
3. **Refuse stale defaults** — if a slot has `updated_at > 14 days`, do NOT cite the default; ask the user explicitly OR flag the staleness in the response.
4. **One-line memo-update receipt** — post to `#shadow-log` on any slot change: `✅ venture-memo · <slot> · <new value summary>`.

## Hard stops

1. **No new commercialization speculation in user-facing responses** — if a slot is empty and the user hasn't decided, say "memo is empty on this; I'll flag for your call" — do not invent a default for that turn.
2. **No drift on `repo_split`** — splitting shadow vs shadow-kit was a deliberate the user-call; never reverse it without the user explicitly saying so.

## Why this exists

the user asked "what belongs free vs paid?" or equivalent 5+ times in the last 30 days. Every answer was derived from scratch. A persistent venture memo collapses these into one read-and-cite, not a re-derive-each-time loop.

## Reference

- Memory: `project_harness_venture.md` (current venture thesis: open-core + BSL, price-per-governed-agent)
- Memory: `feedback_venture_positioning_epic_firewall.md` (positioning: operator at large software firm, no employer name)
- Memory: `stripe_context.md` (pricing catalog: $7/mo subscription is the only one)
- Memory: `feedback_substack_default_hosting.md` (Substack stays as trailhead)
