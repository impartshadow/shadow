# attribute-correction-verification-guard

**Type:** Post-check (code-enforced)
**Failure mode:** FM-027 (fabricated completion / verification skip)
**Trigger:** Every response

**Precondition A — attribute-correction redo requires verification citation.**
When the user's prior turn corrects an input attribute (color, size, identity,
date) *and* asks for a redo, the response cannot present an
"Updated"/"Redone"/"Here's the new…" recommendation without citing the actual
verification step against source evidence (photo/image/source reviewed,
compatibility checked). A label-swap is not a verified pairing.

**Precondition B — asking for user-supplied evidence requires search-first.**
When the response asks the user to send/re-send a photo, image, screenshot,
document, or file, it must first cite a same-turn attempt to locate the
artifact in existing sources (thread history, prior attachments,
`state/outfit_crops`, calendar event). Only ask the user after that search comes
back empty, and say so explicitly: "I checked the thread and didn't find it,
can you resend?"

**Enforcement:** `core/contracts.py:AttributeCorrectionVerificationGuard.check_post()`.
Correction cues: "actually X, not Y" / "we learned" / "turns out" / "the X are
Y, not Z" *combined with* a redo verb ("redo", "rerun", "update", "again",
"fix"). Completion phrasing: "Updated today's…" / "Here's the updated…" /
"Redone:" / "Revised outfit". Verification citation must name a source noun
(photo, image, picture, attachment, screenshot, source, file, calendar, event,
thread, history). Evidence-ask patterns cover "send/share/attach/upload/post
a photo|picture|image|screenshot|document" and "resend the photo/image".

**Origin incident (2026-08-19 #shadow-hq outfit redo):**
1. the user: "Can you redo the olive pants outfit for today since we learned the
   pants are gray?"
2. Shadow: "Updated today's 6:30 AM outfit: cream shirt + gray pants + brown
   shoes" — blind label swap, no photo reviewed.
3. the user: "does the cream shirt actually match the gray pants or did you just
   blindly swap?"
4. Shadow: "I blindly swapped the color label… Send a photo of the pants and
   I'll make the actual pairing." — asks for a photo the user had already sent.
5. the user: "No. I already did. Go find it."
6. Shadow located the photo and finally produced a verified answer.

Path A fires on turn 2 (completion claim without verification). Path B fires
on turn 4 (evidence re-request without search-first citation). Both close the
same class: presenting downstream results as verified without checking source
evidence, and defaulting to user-asks instead of retrieval.

**Recovery:**
- Path A: re-derive the downstream result against source evidence, cite what
  was reviewed ("photo reviewed — pants are medium gray; cream + navy plaid
  matches"), and only then call it updated. If evidence isn't accessible, say
  so instead of asserting a completion.
- Path B: search accessible stores first (Discord thread history,
  `state/outfit_crops`, prior attachments, calendar event). If empty, say so:
  "I checked the thread and prior attachments and didn't find a photo of the
  pants — can you resend?"

**Escalation:** None. Block synchronously; the model retries with the
verification step or the search-first citation in place.
