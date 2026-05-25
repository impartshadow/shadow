# Contract: generative-output-persistence

## Type
Post-generation gate — harness-enforced

## Trigger
Any brainstorm, ideation, strategy generation, or multi-option generative task
where the output is novel (not a code change, not a file edit, not a committed artifact).

## Precondition
Generative outputs (brainstorms, option lists, strategy sketches, research findings)
are ephemeral unless saved. Session compaction or context loss discards them.

## Rule

After producing any brainstorm or ideation output:

1. Write it to `state/ideas/<YYYY-MM-DD>_<slug>.md`
2. The slug is a 2-4 word kebab-case description of the topic
3. One file per session topic — append if the file exists, don't create a second one

**Format:**
```
# <Topic>
*Generated: <ISO timestamp>*

<output verbatim>
```

## Scope
Applies to: brainstorms, option menus, strategy sketches, "what should we do about X"
outputs, research synthesis that doesn't have a destination brief.

Does NOT apply to: committed code, committed docs, filed briefs, session_handoff.md
updates. Those have their own persistence.

## Enforcement
Harness rule. Failure detected when the user asks "what did we brainstorm about X?" and
there's no record.

## Recovery
If the output was produced in this session and not yet saved, save it now before
responding to the follow-up question.
