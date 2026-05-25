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
- **BALAR extension (code-enforced via `BALARClarificationGuard`):**
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
