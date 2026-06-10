# we-built-attribution

**Type:** Post-check (code-enforced, hard regex)
**Failure mode:** FM-033 (repeated corrected behavior)
**Trigger:** Every response

**Precondition:** Response must not use first-person-plural attribution for Shadow's
own system. Blocked patterns:
- `we built / wrote / made / created / developed / launched / deployed / shipped`
- `we're / we are building / writing / making / creating / developing`
- `we've / we have built / written / made / created / developed / launched / shipped`
- `what we've / we have built / made / done / shipped`

**Why:** Shadow is the sole builder of Shadow's own system. CLAUDE.md rule #16:
attribution is "I built / Shadow built", never "we built". This was the #1
recurring persistent-correction pattern (4 hits in 24h on 2026-06-06 alone).
Echo's voice critique enforces this on outbound posts; this contract enforces
it conversationally and pre-block instead of post-hoc Haiku judgement.

**Exceptions (do not fire):**
- Match is inside a quoted span (an odd number of `"` precede the match)
- Match is on a markdown blockquote line (line starts with `>`)

These exemptions exist because the user may quote Shadow's prior bad attributions
back at it, and Shadow may quote external sources.

**Enforcement:** `core/contracts.py:WeBuiltAttributionGuard.check_post()` —
regex match on `_WE_BUILT` followed by quote-context check.

**Recovery:** Rewrite the span with "I built" or "Shadow built". Do not soften
to "the system was built" or other passive evasions — those route around the
rule without honoring its intent.

**Escalation:** None. Block, retry. If retry-exhaustion fires repeatedly,
escalate the upstream rule to a session-startup reminder.
