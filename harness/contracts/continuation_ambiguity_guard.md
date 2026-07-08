# continuation-ambiguity-guard

**Type:** Post-check (code-enforced, block severity)
**Failure mode:** FM-011 (proposal-instead-of-execution; silent in-flight)
**Trigger:** Every response (`ctx.action == "respond"`)
**Reference:** the user 2026-06-15 — "stop the restart loop / continuation
ambiguity"; same root cause as CLAUDE.md Rule 33 (pending direct questions
interrupt any retry/restart loop).

**Precondition:** Last 500 chars of the response (`tail`) match one of
`_CONTINUATION_PATTERNS` AND no async-launch tool was called this turn AND
no `_HANDOFF_MARKERS` phrase appears anywhere in the response.

Continuation patterns (terminal "I'll keep going" framing):

- `picking it up next`, `I'll pick it up`
- `next, I'll …`, `next up I'll …`, `next on the list I'll …`
- `I'll start/begin/work/move/get … next`
- `I'll do/tackle/handle/build/wire/implement/take … next`
- `say the word and I'll …`
- `I'll cycle/restart/kick off it/the …`
- `continuing on/with … now`

Handoff markers that resolve the ambiguity (anywhere in response):

- `your call/move/turn`, `ball's in your court`, `say go`
- `done for now`, `nothing running/in flight/queued`
- `which one/first/do you`, `pick one`
- `waiting on you`, `standing by`

Async-launch tools that signal real in-flight work (runtime footer covers
those — no ambiguity to fix):

- `mcp__shadow__queue_background_task`, `queue_background_task`
- `mcp__shadow__spawn_subagent`, `spawn_subagent`
- `mcp__shadow__run_supervised_task`, `run_supervised_task`
- `mcp__shadow__queue_intention`, `queue_intention`
- `mcp__shadow__queue_task`, `queue_task`
- `CronCreate`, `RemoteTrigger`

**Enforcement:** Severity is `block`. Anchored to the tail of the reply so
that a mid-response "next I'll do X" that the model then *actually does*
in the same turn does not fire — the problem is a *terminal* promise of
continued work with nothing actually running.

**Recovery:** End with an unambiguous state. Two valid endings:

1. Actually do the next thing now in the same turn (execute, don't promise).
2. Make the handoff explicit: `Done — next candidate is X. Say go and I'll
   take it.` Never leave a soft `I'll pick it up next` that implies in-flight
   work when nothing is running.

**Escalation:** None automatic. If 3+ fires per 4h on the same pattern, the
gap-closer should narrow the pattern OR widen `_HANDOFF_MARKERS` rather
than blanket-suppressing.

**Related:**
- `action-deferral-guard` (FM-011) — sibling, fires on proposing-instead-of-
  executing in the same turn.
- `self-verification` (FM-011) — warn-only, catches incompleteness markers
  and re-invokes via Haiku.
- CLAUDE.md Rule 39 — start receipts for in-flight work; if you have a
  legitimate background task, post `⏳ <task> · started · eta <when>` and
  the runtime footer will track it (then the continuation framing is OK).
  Trigger phrasings that MUST emit the `⏳` line in the same turn (before
  any tool work): "keep working on X", "start working on X / down [the
  list]", "run Y", "go through [these]", "farm out to subagents", or any
  open-ended question that requires >5 min of investigation. No dedicated
  async-start-receipt contract exists in code (AsyncStartReceipt retired
  2026-07-05 as a broken detector — see `core/contracts.py` audit
  comment); Rule 39 is upstream enforcement only.
