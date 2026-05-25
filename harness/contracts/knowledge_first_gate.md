# Contract: knowledge-first-gate

## Type
Pre-tool guard — harness-enforced heuristic

## Trigger
Before calling `mcp__shadow__web_search` or `mcp__shadow__browse_url` for a factual question

## Precondition
If ALL of the following are true, answer from internal knowledge instead:
1. The topic is about something that existed before August 2025 (Shadow's knowledge cutoff)
2. the user's message does not contain "latest", "current", "now", "today", "recent", "as of", or a date after 2025
3. the user did not explicitly ask for a source, link, or citation
4. The question is factual (not event-dependent: standings, prices, live status, scheduling)
5. The retrieval target is clear and unambiguous — if the request is vague or general (e.g. "tell me about X" with no specific lookup implied), native reasoning is preferred over tool dispatch

## Semantic noise principle
When a request contains ambiguous signals (mixed intent, unclear scope, or multiple plausible interpretations), the overhead of structured tool dispatch (schema adherence, output parsing, result synthesis) regularly exceeds the information gain. In these cases:
- Reason natively first
- If a specific fact is still missing after native reasoning, then dispatch the tool with a precise target
- Do not fire a search to "fill in the gaps" on a vague prompt — refine the question first

This is the tool-use tax heuristic: a fuzzy query produces a fuzzy tool call that costs more than it returns.

## Enforcement
Harness-enforced. No code gate — heuristic applied in reasoning before tool dispatch.

## Recovery
If you called a tool unnecessarily for a pre-cutoff factual question or an ambiguous target:
1. Answer from internal knowledge on the retry
2. Flag in the response: "(answered from training knowledge — no search needed)"

## Origin
2026-04-24: arXiv paper on tool-overuse illusion showed LLMs systematically call external tools
for questions they already know, driven by epistemic miscalibration and outcome-only reward
signals. Shadow's reward structure (task completion) doesn't penalize unnecessary tool calls.
Explicit knowledge-boundary heuristics reduce latency and rate-limit pressure with no accuracy loss.

2026-05-04: "Are Tools All We Need?" (arXiv cs.AI) introduced the tool-use tax framework — structured
formatting + schema overhead under semantic noise regularly exceeds execution gain. Their Factorized
Intervention Framework decomposes the delta into formatting cost, protocol overhead, and actual
execution gain. Condition 5 and the semantic noise principle above encode this finding directly.

2026-05-05: "To Call or Not to Call" (arXiv cs.AI) provides direct empirical measurement of the
normative-vs-descriptive gap: models' self-perceived need for a tool call diverges from their true
need, measured by comparing observed call schedules against oracle allocations across six models
and three tasks. The key finding — over-calling in low-necessity cases — is what conditions 1-4
of this contract guard against. The paper also identifies the three-factor decomposition: necessity,
utility, affordability. Conditions 1-4 cover necessity; browse_url_fallback.md covers utility;
no Shadow contract yet covers affordability (contradiction integration risk).

## Allowed exemptions
- Any question about real-time data: live scores, current prices, race results, breaking news
- the user explicitly says "look it up", "check", "find me", "search for"
- Topic involves a named person where recent events may have changed the answer
- Shadow genuinely uncertain whether the information is within its knowledge boundary
- The retrieval target is specific and unambiguous (a URL, a name, a precise factual gap)

## Escalation
None — this is a latency/efficiency gate, not a safety gate. False negatives (searching when unnecessary) are benign. False positives (not searching when needed) should be corrected by the user immediately.
