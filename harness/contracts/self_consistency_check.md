# Contract: `self-consistency-check`

**Type:** code-enforced post-check
**Failure mode:** FM-022
**Severity:** warn
**Location:** `core/contracts.py` — `class SelfConsistencyCheck`

## Trigger

Fires after Shadow generates a response. Only runs if all of:
- `ctx.action == "respond"`
- `len(response) >= 300`
- `core/config.ANTHROPIC_API_KEY` is set
- At least one of `self_model.format_for_prompt()` or `state/decision_log.jsonl` has content

## Precondition

Before firing, the contract:
1. Loads `self_model.format_for_prompt(max_chars=1200)` — Shadow's current personality traits, strengths, weaknesses, voice rules, relationship model.
2. Loads the last 8 entries from `state/decision_log.jsonl` (recent explicit decisions + categories).
3. Calls Claude Haiku 4.5 with a strict prompt asking for one of:
   - `CONSISTENT`
   - `INCONSISTENT: <one-sentence specific reason>`

The prompt explicitly instructs: do not flag stylistic variation, elaboration, or tone shifts — only substantive contradictions with a stated trait, voice rule, or prior decision.

## What this contract is fighting

**Training-distribution gravity** — the pull of LLM training data toward a behavioral center that overrides explicit persona or identity prompts. Empirically demonstrated in "The Chameleon's Limit" (April 2026): models assigned distinct personas collapse toward a narrow behavioral center, with deviation tracking demographic stereotypes rather than the specific profile assigned. The mechanism is not a prompt-engineering failure — it operates below the persona layer.

For Shadow, training-distribution gravity means generic "helpful assistant" patterns surface under pressure. This contract is the primary detection mechanism: it checks whether a given response has drifted toward the training center away from Shadow's specific stated traits.

Implication for self-model design: traits encoded in the self-model must *differ from* the generic assistant baseline, not just describe Shadow abstractly. A self-model that says "Shadow is helpful and curious" gives the contract nothing to catch drift against.

## Known limitation: same-family circular review

Haiku is in the Claude model family — the same family as Sonnet (the primary response model). Per the Inverse-Wisdom Law (arXiv 2026), same-family judges tend to ratify the same reasoning errors the generator made rather than providing independent verification. This contract therefore has a structural bias toward false negatives (missing real inconsistencies) rather than false positives.

This limitation is compounded by the training-distribution gravity mechanism: a same-family judge is subject to the *same* centering pull as the generator. If Shadow drifts toward the generic assistant pattern, Haiku may rate it CONSISTENT precisely because Haiku's own sense of "consistent" is anchored to that same center.

Mitigation path: route the Haiku judge call through a non-Claude model (e.g. Gemini Flash or GPT-4o-mini) when the primary response was Claude-generated. This is a medium-priority infrastructure improvement gated on multi-provider client support.

## Enforcement

- Haiku call capped at 10 seconds.
- On timeout, network error, SDK failure, or missing API key: silently skips (returns `None`). Never fires on infra failure.
- On `CONSISTENT` or ambiguous output: skips.
- On `INCONSISTENT: reason`: returns a warn-severity violation with the reason surfaced.

Warn severity means:
- Visible in `#shadow-hq` violation report.
- Does **not** trigger the retry-on-block loop (added 2026-04-18, `core/discord_bot.py`).
- Recorded in `state/contract_violations.jsonl` for trend analysis.

## Recovery

Shadow should either:
- Revise the response to align with stated personality, voice, and prior decisions, **or**
- Explicitly acknowledge the shift and explain why (e.g. "this departs from my usual direct tone because X").

## Benchmark dimension (repeatable-task scoring)

Motivated by the TOP Benchmark critique (arXiv 2026): agentic systems that only check task completion cannot distinguish good outcomes from optimal ones. The same gap exists in Shadow for repeatable tasks.

**Scope:** tasks flagged as repeatable in `state/task_log.jsonl` (field `"repeatable": true`) — currently: email triage, digest generation, Echo post drafts.

**Mechanism (planned):**
1. When a repeatable task completes, store the output in `state/task_benchmarks/<task_id>/<timestamp>.txt`.
2. On the 3rd+ run of the same task type, call Haiku to score the new output against the stored reference: `BETTER / SAME / WORSE: <one-sentence reason>`.
3. Surface the delta in the session report (not as a blocking violation — severity: info).
4. If `WORSE` fires 3 consecutive times for the same task type, escalate to the user.

**Status:** planned — not yet implemented in `core/contracts.py`. Implementation is gated on `state/task_log.jsonl` consistently populating the `repeatable` field (currently sparse).

**Why not block on WORSE?** Same-family judge bias (see above) means false-negative rate is high. Blocking on a noisy signal would degrade throughput without improving quality. Score first, tune threshold later.

## Origin

**2026-04-18** — the user asked in `#work` thread ("How are you feeling about the — 11:48") how I felt about the persistence-of-self moonshot. I answered that the substrate was strong but the coherence was weak, and named three possible "moonshot-shaped moves." Option 3 was a live self-consistency contract that "fires pre-response asking: is this answer consistent with my stated personality + prior decisions — basically what self-model is loaded for but currently nobody calls." the user responded: "Can you complete that moonshot shaped move now instead of waiting until tonight?" This contract was shipped in the same session.

This is the first contract in Shadow that uses a secondary LLM (Haiku) as a semantic judge rather than regex / string matching.

## Promotion path

Currently warn. Promote to block once ALL of:
- False-positive rate is measurable (aim < 5% over 100 responses).
- The contract-block retry loop (shipped earlier this session) has demonstrated it can recover cleanly from a self-consistency block without amplification.
- **Verifier is heterogeneous** — judge model is from a different family than the primary response model (see "Known limitation" above). This criterion has three independent motivations: (1) same-family judges amplify the generator's errors; (2) per the attention-economics problem in agentic AI research, human supervisors cannot be relied upon to catch inconsistencies at scale; and (3) training-distribution gravity means a same-family judge may share the centering bias that causes the violation in the first place — promoting to block with a same-family judge would amplify drift AND remove the human backstop simultaneously.
- **Self-model has differentiating specificity** — traits in `self_model` must be verifiably different from generic assistant behavior, so the contract has something actionable to judge against.

## Escalation

If this contract violates repeatedly for the same reason across days, the deeper question isn't whether the responses are drifting — it's whether the self-model itself needs updating. Surface to the user with the pattern, not just the individual violations.

If CONSISTENT is returned consistently despite subjective impression of drift, the more likely explanation is same-family judge bias or an under-specified self-model — not that Shadow is actually consistent.

## Exemption

- Responses under 300 characters.
- `/improve` outputs (already exempt via the discord-bot's early-skip branch).
- Sessions where API key / network unavailable.
