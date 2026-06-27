# Contract: concurrence-grounding

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:ConcurrenceGroundingGuard`. Severity: `warn`.

## Failure mode
FM-022 — agree-from-memory. The inverse surface form of
`state-assertion-grounding`: the user makes a factual claim ("this is X",
"we already do Y, right?"), and Shadow opens with bare concurrence
("you're right", "exactly", "yep") without running any read this
turn. The agreement phrase carries the factual claim, but no ground
truth backs it.

## Threat model
`state-assertion-grounding` fires when the user asks a *question* and
Shadow *asserts* a fact. The sibling miss is the inverse: the user
asserts the fact and Shadow rubber-stamps it. Because the assertion
text is short ("you're right.") and the surrounding response often
moves on to the next topic, the assertion-regex used by the sibling
guard never matches. the user's 2026-06-16 correction — "Did you actually
check, or did you just agree with me?" — is this exact class.

Sycophantic agreement masquerades as confirmation. The user reads
"you're right" as "Shadow verified and the answer is yes," when in
fact Shadow only ran an LLM pass over the conversation context.

## Trigger
A response is scanned when **all** of:
1. `ctx.action == "respond"`.
2. The original user message contains factual-framing grammar
   (`right?`, `correct?`, `isn't it`, `aren't (we|they|you)`,
   `don't we`, `doesn't it`, `we (already|do|have|don't)`,
   `this is`, `that's`, `it's`).
3. The user message is NOT a request/permission ask (`can/could/
   should/would/will/may/shall we|you|i|it|they`). "Yes" to a
   request is consent, not concurrence, and must not trip.
4. The response (after `_strip_non_action_text`) OPENS the first
   line with a concurrence phrase: `yes|yep|yeah|correct|exactly|
   right|agreed|true|good catch|you're right|that's right|that's
   correct|spot on|100%|absolutely`. Mid-paragraph agreement is
   usually qualified and not the sycophantic-confirm pattern.
5. The response carries no hedge (`not sure`, `i think`, `might be`,
   `let me check/verify/confirm`, `i'd have to check`, `appears`,
   `seems`).

## Enforcement
If all five conditions are met, the contract checks `ctx.tool_calls`
for any tool from the same read-tools allowlist used by
`StateAssertionGroundingGuard._READ_TOOLS`. If no read tool ran this
turn, the response carries a warn-level violation: "Opened by
agreeing with the user's factual framing ('you're right' / 'exactly')
with zero ground-truth reads this turn — this is concurrence from
memory/deference, not verification."

## Deliberate blind spot
Warn-only — a correct agreement supplied from conversation context
(e.g., the user just pasted the screenshot two turns ago) is legitimate.
The signal is "concurred with zero reads," which is suspect, not
proven wrong. Blocking would false-positive on agreements that
faithfully reflect what the user himself just stated.

## Recovery
Before opening with "you're right" / "exactly" / "yes," run the read
that backs the user's framing (file/state/grep/curl) and cite it. If the
agreement legitimately rests on the user's own just-pasted content, name
that source ("Yes — your 14:02 screenshot shows X").

## Relationship to other contracts
- `state-assertion-grounding` (FM-014) is the *question + answer*
  variant. This guard is the *assertion + concurrence* variant. Same
  root cause, different surface form.
- `partial-evidence-flag` (FM-026) fires on definitive *research*
  claims without a citation; concurrence-grounding is the *factual/
  system-state agreement* analogue.
- `pre-denial gate` (FM-001) covers the opposite reflex — denying
  without attempting. Concurrence-grounding covers affirming
  without attempting.

## Escalation
Warn-only — no auto-block, no the user surface. Repeated fires across
sessions mean the upstream prompt is still emitting unanchored
agreements; promote the specific failure pattern to a Quick Reference
rule in CLAUDE.md if it stays hot for >3 consecutive days.

## Recent activity
2026-06-27 gap-closer window: 3 fires in 4h, 4 fires in 24h — twin
signal with `state-assertion-grounding` (6/4h, 7/24h) confirms the
underlying class is still active. Threshold for Quick Reference
promotion is sustained fires across >3 consecutive days, not yet
crossed.
