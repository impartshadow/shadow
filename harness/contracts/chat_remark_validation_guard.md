# Contract: `chat-remark-validation-guard`

**Type:** post-response gate, deterministic, `core/contracts.py:ChatRemarkValidationGuard`
**Failure mode:** FM-022 (self-consistency), sycophancy subtype
**Severity:** block
**Tests:** `tests/test_chat_remark_validation_guard.py`

## Failure mode

the user makes a remark that asks for nothing, and Shadow answers it as a request:
it restates his message and approves his choice.

2026-10-08 #osrs. the user: "Yeah I'm just chilling until the raid drops. I was
just surprised at virtus". Shadow: "Yeah—the Virtus spike caught you off guard,
not a reason to buy it. ... Waiting for the raid to show what actually matters
makes sense." the user: "There are emdashes and just weird validation comments."

## Why the existing rules missed it

The correction was saved through `apply_correction` as prompt text only, and
`core/model_tools.py` cut it at a flat 200 characters, mid-word. The saved rule
also named tokens (em dashes, validation) rather than the trigger: a message
with no question and no ask. Nothing checked the reply after drafting.

## Rule

Arms only when the user's own text (source-channel context, system tails, quoted
blocks, and channel tags stripped) is 280 characters or fewer, has no `?`, no
question-word sentence opener, no "tell/show/help me" or "please/can you" ask,
and no operational command from `core/interaction_mode.py`.

Once armed, it blocks:

- approval tails: "makes sense.", "fair enough", "good/right call", "that's
  reasonable.", "totally understandable", "Agreed"/"Exactly" sentence openers,
  "sensible adjustment"
- em dashes in replies of 400 characters or fewer (the chat register)

Quoted text and inline code are exempt.

## Calibration

Replay of `state/discord_transcript.jsonl` (2026-10-08): 1,406 remark turns
armed. 38 replies carried approval tails, all reflexive agreement. Em dashes
appeared in 880 replies overall, mostly long status reports, so that arm is
limited to short replies (258 hits).
