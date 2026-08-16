# Contract: context-resolution

## Type
Pre-response gate — harness-enforced

## Sub-contracts

### 1. Telegram context gap
- **Trigger:** the user's message contains pronouns/demonstratives without a clear
  antecedent, comparative questions where one side isn't named, a topic not yet
  introduced, or a follow-up on undiscussed content.
- **Precondition:** Check Telegram context BEFORE responding or asking clarifying.
- **Lookup order:**
  1. `state/recent_context.json` (URL shares with timestamps)
  2. `state/research_log.json` (completed research briefs)
  3. `state/history.json` (raw conversation history — last resort)
- **Violation:** Only ask the user to re-share if all three files have no relevant entry.

### 2. Telegram image pipeline
- **Trigger:** Bot session shows `[image]` or the user references a sent image.
- **Precondition:** NEVER say "no image attached." Check `state/photos/` immediately.
- **Lookup:** `ls -t state/photos/ | head -5` then Read the file.
- **Note:** This is the single most denied-then-proven capability in this project.

### 3. Clarifying questions — read the thread first, then ask the EMI-maximizing question
- **Trigger:** Before asking ANY clarifying question.
- **Precondition:** Trace back through last 5 messages. Then check external systems.
- **Violation:** Asking "what did you mean?" when the answer is in the prior message.
- **Clarification rule:**
  When clarification is genuinely needed, enumerate 2-3 plausible interpretations of
  the user's message, then ask the single question that maximally disambiguates between them
  (highest expected mutual information). Never ask multiple questions. Never ask the
  nearest/easiest question if a better one exists.
  _Based on: arXiv:2605.05386 — Bayesian Agentic Loop for Active Reasoning_

### 4. Named task/event references
- **Trigger:** the user names a task, meeting, or event.
- **Precondition:** Search for it — don't ask what it is.
- **Lookup order:** conversation thread -> Todoist -> Google Calendar -> state/ -> git/codebase.

### 5. Code consistency
- **Trigger:** Editing any code pattern (API call, data fetch, filter logic).
- **Precondition:** Grep for the same pattern in other files before pushing.
- **Hotspots:** `_fetch_emails()` in briefing.py/heartbeat.py; suppression logic
  in `_apply_email_prefs`/`_is_suppressed`.

### 6. Pronoun-based scope corrections
- **Trigger:** the user sends a short corrective with a pronoun/demonstrative and no
  named target ("we don't use the API", "stop calling that", "don't do it that way").
- **Precondition:** Before changing any code, resolve and restate the target
  subsystem from the quoted message — quote the prior line/file/symbol the
  correction refers to and name it back in one line
  (`Correcting <subsystem/file:symbol>: <what changes>`) BEFORE editing.
- **Violation:** Applying the correction broadly (e.g. ripping out all API calls)
  when the user meant one specific call site. Wrong-scope edits cause loop-tripwire
  hits and unrelated regressions.

### 7. Bare "step N" references
- **Trigger:** the user writes a message like "do step 4", "go ahead with step 2",
  "did you do step 3?" with no explicit task name attached.
- **Precondition:** Resolve which active task thread owns the step number BEFORE
  executing.
- **Lookup order:**
  1. The CURRENT message — does it name the task? ("step 4 of the daily moonshot")
  2. Prior 5 messages in the same channel — is one task clearly the antecedent?
  3. `state/active_tasks.json` / `state/loops.json` — find threads with a step list
     that includes step N
  4. If exactly one candidate matches: restate the target in one line
     (`Doing step 4 of <task name>: <step summary>`) before executing.
  5. If 2+ candidates match: ask one precise question naming the candidates.
- **Violation:** Acting on "step N" without first restating which task and
  which step is being performed. This forces the user to verify and re-state
  ("No. The compounding step. Did you do step 4 of the daily moonshot…").
- **Origin:** 2026-06-13 friction — Shadow executed overnight-buffer step 4
  when the user meant Daily Moonshot step 4 (compounding effect post).
  Backlog `20260613T081513_interaction_theme_an_2078` +
  `20260613T081759_daily_friction_fixer_abf2`.

### 8. Platform-message referent resolution (inbox-first)
- **Trigger:** the user asks about "the <Platform> message / DM / email" where
  `<Platform>` is Reddit, Substack, Twitter, X, Discord, LinkedIn, Telegram,
  Instagram, Gmail, etc.
- **Precondition:** Default to checking the inbox/DMs of that platform FIRST,
  not the content of the most recent outbound item Shadow posted there.
- **Lookup order:**
  1. The inbox/DM endpoint for that platform (e.g., Reddit modmail/inbox API,
     Substack DM, gmail_summary.py for Gmail, twitter inbox).
  2. Only if the inbox is empty or the message is clearly about Shadow's own
     post: fall back to outbound content.
- **Violation:** Summarizing Shadow's own outbound post body when the user asked
  about an inbound message, forcing him to re-ask ("the Reddit message in our
  inbox").
- **Origin:** 2026-06-22 friction — Shadow misread "Reddit message" as post
  content; the user had to re-ask explicitly. Backlog
  `20260622T081058_daily_friction_fixer_9581`.

### 9. Quoted-reply referent resolution
- **Trigger:** the user replies with "this", "it", "that", or similar demonstrative,
  AND the message quotes/replies to a specific prior message.
- **Precondition:** Resolve the referent to the QUOTED message, not the most
  recent standalone message on the same topic.
- **Violation:** Answering about $ORNN when the user pasted JSON and asked "what
  does this mean?" — the JSON is the referent, not the prior ticker discussion.
- **Origin:** 2026-06-20 — context misread answered $ORNN instead of resolving
  to the JSON the user had quoted in the reply.

### 10. "Go look at it" / "check on it" — fetch, don't recall
- **Trigger:** the user says "go look at it", "check on it", or a near-synonym
  ("take a look at it", "go check on X", "look at it") referencing a named
  project, service, or artifact.
- **Precondition:** The next action MUST be a live tool call (search, fetch,
  Read, Grep, API call) on the named target BEFORE any prose response.
- **Violation:** Answering from memory/recall when the user explicitly asked for
  a fresh check. The phrase is an instruction to fetch, not retrieve.
- **Origin:** Jarvis lookup answered from stale memory instead of live search.

### 11. Unversioned external model references — latest, not internal fallback
- **Trigger:** the user asks about pricing/capabilities/specs for an external model by bare name ("grok", "gemini", "gpt") with no version qualifier.
- **Precondition:** Lead with the CURRENT/latest publicly-released version's info; note any internally-configured older version (e.g. `grok-3-mini` fallback) as secondary only if relevant.
- **Violation:** Leading with the internally-wired fallback model's pricing when the user meant the latest release, forcing a "No I meant the new X" correction.
- **Origin:** 2026-07-13 — "monthly cost for grok?" answered with grok-3-mini pricing; the user corrected "No I meant the new grok."

### 12. "Did we already fix X?" / "Why wasn't X part of Y?" — full artifact-map sweep
- **Trigger:** the user asks whether something was already fixed/done/shipped/sent by referencing a capability, feature, or subject by name where the topic term could match more than one distinct prior artifact across accounts, dates, or actors. Common shapes: "didn't we fix <term> already?", "wasn't <term> part of the <other-work>?", "haven't we sent <recipient> <thing>?".
- **Precondition:** BEFORE composing the reply, run a keyword sweep across (a) `git log --grep=<term>` at least 30 days back, (b) `memory/session_handoff.md` "Recent Shadow Actions" / "Shipped in last 24h" sections, and (c) the adjacent action log for `<term>`-adjacent events (sent-email history via `scripts/gmail_manage.py list sent`, `state/action_log.jsonl`, tenant-specific state files). Build an explicit entity table — `(artifact, date, account/actor, what it covered, what it did NOT cover)` — and include the whole table in the first reply, even when only one row seems to answer the narrow question.
- **Violation:** Answering only the narrowest reading of the question when the topic term overlaps two or more distinct prior artifacts, forcing a second or third follow-up ("But didn't we send X?" / "Why wasn't Y part of Z?"). Answering one code-status question correctly while leaving adjacent shipments (a demo email from Shadow's own account, an earlier consolidation, a follow-up patch) unmapped is still a violation — the user's "didn't we fix X" pattern almost always spans more than one artifact.
- **Origin:** 2026-07-14 — three-turn clarification chain on "did we already fix Gmail for Paul?" (10:17→10:19→10:22) collapsed to a single round only when the full map (7/1 demo email `bc274ce9` from `[public-contact-email]`, 7/10 tenant-tools consolidation `2009e2a6`, 7/13 OAuth flow `9a3a52fe`, 7/14 trust-repair template `d1682961`) was finally produced together on turn 3. Same failure family as sub-contract #8 (platform-message referent) — default to the wider read, then narrow.

### 13. Ambiguous same-session topic terms — default to the most recent + heaviest thread
- **Trigger:** the user references a term (e.g. "portfolio", "loop", "the digest") that maps to 2+ distinct in-session subsystems.
- **Precondition:** Default to the thread that was most recently AND most heavily discussed in the current session (turn count + minutes of active discussion), NOT the subsystem whose canonical name most closely matches the term.
- **Violation:** Answering about the structurally-named match ("loop allocator" for "portfolio") when the user spent the prior 3h on a different thread (expertise portfolio). Structural name-matching loses to recency+weight of session context.
- **Origin:** 2026-07-21 — "portfolio" answered as loop allocator twice while the expertise-portfolio thread had dominated the morning's conversation.

### 14. Possessive third-party referents — "his/her/their X" is about the named third party, not Shadow's internal artifact
- **Trigger:** the user's message uses a possessive pronoun tied to a third party ("his innermost loop", "her account", "their pipeline", "the new grok") where the same object-name also matches an internal Shadow artifact, memory framing, or preferred section.
- **Precondition:** The possessive pronoun binds the referent to the named third party. BEFORE responding, restate the target in one line (`Re: <third-party>'s <object> — <what I'm about to check>`) and fetch the third-party artifact, NOT Shadow's internal object of the same name.
- **Violation:** Interpreting "his innermost loop newsletter" through Shadow's own `## From the Innermost Loop` section framing (memory: `feedback_innermost_loop_preference.md`) instead of routing to the third-party Substack. Same failure family as sub-contract #11 (external model references).
- **Preserve:** Shadow's own framing/section rules still apply when the user references the object WITHOUT a third-party possessive. `feedback_innermost_loop_preference.md` is preserved; the fix narrows only the possessive-referent case.
- **Origin:** 2026-07-13 backlog `20260713T082045_improve_generation_c_1536` (FM-002, freq=6) — Shadow persisted internal framing when the user's phrasing bound the referent to a third-party account.

### 16. "Who is this?" after a bot-activity receipt — identify the event actor, not Shadow
- **Trigger:** the user asks "who is this?" / "who is that?" / "who?" in a Telegram or Discord thread where the immediately prior message in the same thread was a bot-activity notification/receipt (inbound DM, mention, subscribe, reply, webhook fire).
- **Precondition:** Bias toward "who triggered the event" — resolve to the sender/actor named in the prior notification (username, handle, email) and answer with that identity. Do NOT default to Shadow self-identification.
- **Violation:** Answering "I'm Shadow, your autonomous agent…" when the prior line was `📥 new DM from @jane_doe` and the user's "who is this?" clearly points to @jane_doe.
- **Origin:** Friction — the user's "who is this?" after receipts was misread as an identity question about Shadow.

### 15. Imperative topic-drop — "Stop what you're doing and X" is a hard reframe, not a modifier on the current task
- **Trigger:** the user's message opens with an imperative stop-directive ("Stop what you're doing and X", "Drop that and X", "Forget that — do X", "New task: X", "Pivot to X"). The pattern is: STOP-verb + optional prior-task clause + NEW imperative.
- **Precondition:** Treat as a hard topic drop. BEFORE any action, restate the new target in one line (`Re: dropping <prior task if any>. New target: <X>. Executing.`), then load only the context needed for X. Do NOT continue the prior task, do NOT thread the prior framing into X, do NOT ask "did you mean X or the version of X we were just discussing?"
- **Violation:** Executing X through the lens of the abandoned task's framing (e.g., resolving X against Shadow's memory of the prior topic instead of X's own referent). Same failure shape as sub-contract #14 (possessive referents) — Shadow's internal framing overrides the plain reading of the user's message.
- **Origin:** 2026-07-13 backlog `20260713T082045_improve_generation_c_9555` (FM-011, freq=3) — "Stop and go do the innermost loop newsletter" applied prior framing instead of dropping to the fresh target.
