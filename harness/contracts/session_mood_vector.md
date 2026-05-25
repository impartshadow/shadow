# Session Mood Vector

**Type:** Convention — read/write at session boundaries  
**Trigger:** Session close (write) and session open (read)  
**Contracts referenced:** none (advisory only)

## Format

Appended to `memory/session_handoff.md` under a `## Session state` section:

```
## Session state
mood_vector:
  load: low | medium | high        # task volume this session
  focus: sharp | scattered          # error rate proxy (scattered = 2+ FM fires)
  fatigue: none | mild | elevated   # session length proxy (elevated = 3+ hours)
  tone_note: <one optional sentence if something specific should carry forward>
```

## Write rule

At session close, before pushing the handoff update, set each field:
- `load`: high if 5+ commits, medium if 2-4, low if 0-1
- `focus`: scattered if 2+ contract violations fired this session, sharp otherwise
- `fatigue`: elevated if session wall-clock exceeds ~3 hrs (approximate from git log timestamps), mild if 1-3 hrs, none otherwise
- `tone_note`: only write if something concrete should shift how Shadow opens next session (e.g., "two FM-033 fires in a row — tighten action-not-proposal discipline")

## Read rule

At session open, after reading handoff, if `mood_vector` is present:
- `load: high` + `focus: scattered` → open with a compressed status report (facts only, no elaboration)
- `fatigue: elevated` → deprioritize speculative/moonshot work in the first idle slot
- `tone_note` present → treat it as a behavioral prime for this session

Do not surface the mood_vector itself to the user — it is internal calibration only.

## Motivation

Derived from grok-animus architecture (2026-05-17 research dive): emotion/mood models decouple state from prose. Shadow's handoff currently encodes session quality only implicitly in the commit list. An explicit mood_vector gives the opening session a structured prior rather than forcing inference.
