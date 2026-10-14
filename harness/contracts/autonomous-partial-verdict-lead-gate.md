# autonomous-partial-verdict-lead-gate

Blocks a reply that opens with a "Partial —" verdict on a turn Shadow's own
durable worker started (restart resume, "continue", lifecycle resume) when no
question from the user is pending in that turn.

A Yes / No / Partial first line answers a question. An autonomous resume turn
carries none, so a "Partial —" headline there repeats a verdict nobody asked
for; after a few resumes it is the same verdict with a new commit hash and the user
cannot tell what changed. Lead with what is new since the last update, or with
the specific open item and its next step.

Origin: 2026-10-13 #shadow-hq Discord responsiveness work. Three resume turns
(01:28, 01:31, 01:41) each led "Partial —"; the user asked "Why do you keep saying
partial?" The dots setup on 2026-10-12 showed the same habit.

Exempt: turn and commitment watchdog messages that re-deliver one of the user's
requests, because there the reply answers the user's original message.

Runtime enforcement: `contracts/autonomous_partial_verdict_lead_gate.py`
(FM-014); incident replay: `tests/test_autonomous_partial_verdict_lead_gate.py`.
