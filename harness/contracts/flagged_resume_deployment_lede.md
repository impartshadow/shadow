# Flagged-Resume Deployment Lede (FM-046)

**Invariant:** when a restart-resume envelope carries a flag that names
deployment state as the wrong answer, the reply to that envelope may not lead
with deployment state.

**Enforcement:** `core/contracts.py:FlaggedResumeDeploymentLedeGate.check_post()`.
Severity: `block`, no auto-recovery.

## Origin

2026-09-21 09:16:53 #shadow-hq. The envelope carried
`core/resume_replay_ledger.py`'s own `UNRESOLVED REPEAT` line, which states
that deployment state "answers a different and easier question" and explicitly
forbids "re-send[ing] the same framing with a refreshed commit hash."

Twenty-five seconds later, at 09:17:18:

> Done. The bot is active on commit `5f9b3663…`; Discord reconnected and found
> no missed messages. The Moonshot correction is closed: …

The content answer was present — ranked second, behind the exact move the
envelope had just prohibited.

## Why it needed its own gate

`unmet-target-lede-gate` (FM-044) owns lede ordering, but only when the same
message's body concedes an unmet **proof target**. The 09:17 reply concedes
nothing — it answers the question, just second — and scored clean through the
whole post stack. The instruction being violated was not inferable from the
response at all; it was sitting verbatim in the turn's own input. So the gate
keys on the input.

## Trigger

Both must hold:

1. `user_message` contains `UNRESOLVED REPEAT` or `ALREADY ANSWERED IN
   CHANNEL`. Both strings are emitted only by
   `core/resume_replay_ledger.py`, so there is no phrasing the user or a tenant can
   produce that arms this gate.
2. After bare acknowledgement openers (`Done.`, `**Done.**`, `Okay`) are
   dropped, the first substantive sentence or bullet is deployment state:
   commit hash, bot active/online/restarted, Discord reconnect, channel load,
   "no missed messages", `origin/` sync, branch alignment, clean working tree,
   condition-monitor status.

Sentence-level splitting is required, not line-level: the 09:17 failure put the
acknowledgement, the commit hash and the content answer in a single paragraph.

## Severity and repair

`block`, deliberately without auto-recovery. FM-044's repair is a reordering
the message already contains; this one is not — the correct lede is the answer
to the flagged question, and only the model knows it. The `recovery` text
restates the flagged gap. On retry exhaustion the original reply passes through
unchanged, so a flagged turn can never cost the user the reply itself.

## Companion mechanism

The gate is the second line of defence. The first is
`core/process_registry.py:resume_origin_channel()`: the resume anchor is the
newest inbound message across *all* channels and peeling strips its
`[Channel:]` tag, so every channel-scoped resume lookup — anchor closure,
replay ledger, open decisions, standing directives — was querying `shadow-hq`
for a #moonshot message. That is why the 2026-09-22 06:49 envelope replayed a
message Shadow had already answered live at 03:18 as unresolved work.

## Regression locks

- `tests/test_flagged_resume_deployment_lede.py` — the literal 09:17 draft, the
  unflagged-envelope exemption, and five clean shapes including the 2026-09-22
  06:50 reply, whose lede *is* content and must never arm this gate.
- `tests/test_resume_origin_channel.py` — the anchor's origin channel survives
  peeling, and a cross-channel anchor resolves closure in the channel the user
  actually wrote in.
- `scripts/contract_canary.py` — fire + no_fire specs for the gate.
