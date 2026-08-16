# interpretation-menu-guard

**Type:** Post-check (code-enforced, deterministic regex)
**Failure mode:** FM-013 (clarification-quality — asking the wrong question)
**Enforcement:** `core/contracts.py:InterpretationMenuGuard.check_post()`

## Trigger

Response contains BOTH:

1. An **opener** that frames the response as enumerating readings of the user's
   own message. Examples: "I see your message in three ways", "Your message
   could imply two different goals", "This could mean either… or…", "I read
   this in two ways".
2. A **terminal question** handing the pick back to the user. Examples: "Which of
   these best describes…?", "Which is the priority?", "Which do you mean?",
   "Which reading is closer?".

Either signal alone does not fire. Both together = an interpretation menu.

## Why it exists

the user explicitly rejected this pattern on 2026-07-08 during MTP refinement:
"Don't just blindly take what I said. I want to refine with you. Not dictate."
The next two Shadow turns each responded with an enumerated menu of what
the user might have meant, followed by "Which of these best describes your
goal?" and "Which is the priority?" — deferring the entire refinement back
to the user across two full turns. The stall left the substantive MTP question
open when an unrelated side-incident hit; the direct question was not
answered for ~3 hours until the user re-asked verbatim.

This is the same structural failure as the banned action-option-menu
pattern (CLAUDE.md rule 10 — "never present the user a menu to choose from for
an authorized call") applied to *interpretation* instead of action.

## Recovery

Pick the highest-probability interpretation and answer or execute against it
under standing authority. If you need to name the reading, do it in one line
before the answer (e.g. "Reading this as X:"). Never end a refinement turn
with "which of these" / "which is the priority" / "which best describes".

## Non-violations

Real blocking ambiguity in an execution-adjacent request (e.g. "restart the
bot" when two bots are running) remains a legitimate reason to ask one precise
question. This contract only fires when the response is a menu of readings of
the user's own message and hands the pick back to him.

## Tests

`tests/test_interpretation_menu_guard.py` — covers both transcript instances
(2026-07-08 13:06:30 and 13:08:48), plus negative cases (clarification about
external ambiguity, single-position answer, direct answers).

## History

- 2026-07-08: created after `/reflect` diagnosed the MTP refinement stall.
- 2026-08-16: removed the zero-signal BALAR model judge; this deterministic
  guard remains the canonical owner for interpretation-menu deferrals.
