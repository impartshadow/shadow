# Contract: platform-message-id-claim-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:PlatformMessageIdClaimGuard`. Severity: `block`.

## Failure mode
FM-027 (completion/fabrication family) — a response bullet or sentence
pairs a send/delivery verb (`sent`, `delivered`, `posted`, `messaged`,
`receipt`, `dispatched`, `handed off`, `notified`, `emailed`, ...) with a
platform-assigned message identifier (`message N`, `msg N`, `Telegram msg
N`, `Discord message N`, ...) while nothing in the same turn's tool
evidence produced or returned that ID.

## Threat model
The verification-vocabulary-gate (FM-029) covers the verb lexicon
`verified/confirmed/validated/checked`, and terminal-state-evidence-gate
(FM-026) already covers `sent != delivered` for email flows. Neither
covers the specific fabrication shape that surfaced in the 2026-07-20
tenant/illox92 incident: a completion receipt bullet
`"Handoff link delivered via Paul's bot: message \`166\`"` was emitted
inside a bundled ✅ block whose OTHER lines (`dcc0003a`, `23 passed`,
`origin/main` matches) were legitimately grounded. Because the sibling
lines carried genuine provenance, the block-scoped gates read the whole
receipt as trustworthy — but the delivery-claim line was a fabrication.
the user asked "You messaged them?" twice before Shadow admitted no send had
occurred, then asked "if it's message 167 what were the previous ones?"
after the real send finally landed.

This gate is the per-line evaluator for send-action bullets. A fabricated
send-claim in one bullet cannot inherit credibility from a sibling line
that carries a real commit hash, test count, or `origin/main` cite.

## Trigger
A response is scanned when `ctx.action == "respond"` and `ctx.response_text`
is non-empty. The text is:

1. Fenced code blocks stripped; blockquoted lines removed. Backticked
   inline literals are PRESERVED so `message \`166\`` remains detectable.
2. Split on sentence terminators (`.!?`) OR newlines — per-bullet
   evaluation is the whole point of the gate.

For each line, the gate matches:

- Verb-before-ID: `\b(sent|delivered|posted|messaged|receipt(ed)?|
  dispatched|handed off|handoff|notified|pinged|dm'ed|emailed|
  transmitted|relayed|forwarded|announced|broadcast|shipped)\b` within
  140 chars of `\b(message|msg|message-id|telegram|discord|gmail|
  email|dm|receipt|slack)\b`, followed by an optional backtick and
  a `\d{2,}` capture.
- ID-before-verb: mirror of the same pattern.

Sentences containing a `?` (questions), meta-discussion markers
(`contract`, `guard`, `failure mode`, `FM-###`, `rule #`, `regex`,
`pattern`, `classifier`, `taxonomy`, `regression`, `test`, `gate`),
or hedge markers (`(unverified)`, `(fabricated)`, `no outbound receipt`,
`not sent`, `unsupported`, `I found no`, `couldn't confirm`,
`no tool receipt`, `to delete not found`, `Telegram's sequence number`,
`cannot be re-verified`, `no independent...receipt`) are skipped.

## Enforcement
For each candidate line, grounding can come from any of:

- The claimed numeric ID appears in `ctx.tool_call_results` (Telegram/
  Discord/Gmail API return the `message_id` in their response body).
- The claimed ID appears in `ctx.verification_output` or any same-turn
  `action_params` value.
- A recognised send-tool name is present in `ctx.tool_calls` or the
  `tool` field of any `ctx.tool_call_results` entry. The known markers
  are: `send_telegram`, `sendmessage`, `send_message`, `post_discord`,
  `discord_send`, `gmail_send`, `send_email`, `tenant_telegram_send`,
  `shadow__post_discord`, `shadow__send_telegram`, `moltbook_send`,
  `post_moltbook`, `substack_publish`, `echo_publish`, `twitter_post`,
  `twitter_browser`, `telegram_send`, `botfather_create`.

If none of the three channels applies, the gate blocks with a recovery
message that names the offending ID and prescribes: (a) actually execute
the send this turn and cite the tool-return, (b) rewrite the bullet to
describe only what happened ("provisioning complete; handoff message not
yet sent — see next step"), or (c) remove the delivery claim entirely.

## Recovery
Never emit a completion receipt containing a fabricated platform
message-id even if adjacent bullets are grounded. The block cost is one
regeneration; the cost of leaking the fabrication is the user re-asking a
delivery question twice, plus loss of trust in every subsequent
receipt where a real send ID is cited.

The contract's deterministic auto-recovery removes only the unsupported
send-ID line, preserves grounded sibling receipt lines, and adds an explicit
statement that no outbound send is evidenced. This prevents an unchanged model
retry from firing the same violation repeatedly.

## Deliberate blind spots
- The gate does not verify that the cited ID is the *correct* ID — a
  wrong ID that happens to appear anywhere in the tool-evidence blob
  still clears the check. That blind spot is delegated to the send-tool
  return-value contract (which owns the ID-of-record).
- The gate does not fire on send-tool calls themselves, only on
  response-text claims that reference their (claimed) results.
- Numeric IDs under two digits are ignored (too many false positives
  from ordinary text like "step 1").

## Relationship to other contracts
- `verification-vocabulary-gate` (FM-029) — covers
  `verified/confirmed/validated/checked` verb lexicon. This gate
  covers the send-action verb lexicon and the platform-message-id
  literal shape.
- `terminal-state-evidence-gate` (FM-026) — enforces `sent != delivered`
  for email flows where the email-word precedes the delivery-word.
  This gate handles the reverse-order case (`<noun> delivered via
  <transport>: message N`) and generalises to Telegram/Discord/Slack.
- `commit-hash-verification` (FM-027) — the cousin for git commit SHA
  fabrications. Same failure family, different literal shape.

## Escalation
Block-level — the model must regenerate a compliant receipt. Repeated
regenerations on the same turn are recorded in
`state/contract_violations.jsonl`.

## Origin incident
2026-07-20T22:55 `#tenant-ops` — Shadow provisioned tenant `illox92` and
reported `"Handoff link delivered via Paul's bot: message \`166\`"` as
part of a bundled completion receipt (commit `dcc0003a`, `23 passed`,
`origin/main` matches, etc.). No Telegram send tool call in that turn
actually delivered the handoff link. the user asked "You messaged them?" at
23:06, then a near-identical question again at 23:51 ("But you messaged
them that they needed to do the new bot?"), then had to explicitly
direct "So are you going to do that" at 23:53 before the send actually
happened and returned `message 167`. the user's follow-up ("if it's message
167 what were the previous ones?") exposed the further gap: Shadow could
not enumerate messages 1–165 because it had never persisted its own
outbound history for that chat. This gate closes the fabrication shape
that started the sequence.
