# patterned-stop

**Type:** Post-check (code-enforced, Haiku-judged)
**Failure mode:** FM-033 (repeated corrected behavior)
**Trigger:** Every response

**Precondition:** Response must not contain any pattern the user has explicitly said "stop doing X" for. Known stops: asking clarifying questions instead of acting, hedging, proposing instead of executing.

**Enforcement:** `core/contracts.py:PatternedStopContract.check_post()` — loads stop patterns from correction log, checks response for matches.

**Recovery:** Remove the stopped pattern. Execute directly. Do not ask — act.

**Escalation:** Not required. Block silently, retry without the pattern.
