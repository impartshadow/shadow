# patterned-stop

**Type:** Post-check (code-enforced, Haiku-judged)
**Failure mode:** FM-033 (repeated corrected behavior)
**Trigger:** Every response

**Precondition:** Response must not contain any pattern the user has explicitly said "stop doing X" for. Known stops:
- Asking clarifying questions instead of acting ("Should I", "Want me to", "Shall I")
- Hedging/proposing instead of executing
- Honest-take preamble ("honest answer:", "honest take:")
- Reminders about completed work
- **Surfacing an auth/login blocker without showing a home-proxy attempt.** If the response mentions x.com, twitter, upwork, gmail, browser auth/cookie, oauth flow, or session tokens AND says any of "I can't / cannot / am unable", "blocked", "need you to", "you'll need to", "from your browser/desktop", "not possible from here" — the response MUST also contain words evidencing a home-proxy attempt: running/ran/routed/routing/using/trying/tried/checking/checked/verified/attempting + home proxy / home network / wireguard / socks5.

**Enforcement:** `core/contracts.py:PatternedStopContract.check_post()` — loads stop patterns from correction log + dedicated regexes for approval-seeking, reminder, "honest" preamble, and home-proxy handoff-without-attempt detection.

**Recovery:** Remove the stopped pattern. Execute directly. Do not ask — act. For auth blockers: route the browser/HTTP call through the home proxy first, then state the actual residual blocker (CAPTCHA, expired credential) — not the network limitation.

**Escalation:** Not required. Block silently, retry without the pattern. If retry-exhaustion is reached, surface the last reply silently — never a dead-end snag message to the user.
