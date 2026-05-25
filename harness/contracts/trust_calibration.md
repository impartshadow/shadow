# trust-calibration

**Type:** Pre-check (block)
**Failure mode:** FM-011 (action deferral / unnecessary escalation)
**Enforcement:** `core/contracts.py → TrustCalibrationContract`

## Purpose

Replace the binary static allowlist with a posterior over the user's risk tolerance. Observe approve/deny signals per action-category and tighten auto-allow thresholds as confidence accumulates. Escalate only at the uncertainty boundary — where the user's preference is genuinely unknown.

## Trigger

Any action that is not explicitly listed in CLAUDE.md's standing-authority section but has historical approve/deny signals in `state/decision_log.jsonl`.

## Precondition

- `action_category` must be one of the logged categories (git_push, email_send, discord_post, web_publish, external_api)
- `state/decision_log.jsonl` must contain ≥1 entry with `category == "approval_outcome"` for this category

## Enforcement

1. Read approval outcome entries from `state/decision_log.jsonl` for the target action category
2. Compute beta-binomial posterior: α = approvals + 1, β = denials + 1
3. Compute posterior mean p = α / (α + β) and confidence = α + β (total observations)
4. **High confidence allow** (p ≥ 0.90, confidence ≥ 5): proceed without escalation
5. **High confidence block** (p ≤ 0.10, confidence ≥ 5): block with FM-011 violation
6. **Uncertainty boundary** (0.10 < p < 0.90 OR confidence < 5): surface to the user with the current posterior stats

## Confidence banding for escalation messages

Not all uncertainty-boundary escalations are equal. When surfacing to the user, include the confidence band so the message conveys whether this is a close call or a cold-start:

| Condition | Band label | Message tone |
|---|---|---|
| confidence < 5 (cold start) | `[NEW]` | "No history for this action type — flagging for first preference signal" |
| 0.40 ≤ p < 0.60 (genuine split) | `[UNCLEAR]` | "Approval history is split (X approved, Y denied) — flagging at boundary" |
| p in [0.10,0.40) or (0.60,0.90] (mild lean) | `[LEAN-ALLOW]` / `[LEAN-BLOCK]` | "History leans X but confidence below threshold" |

Clear-cut escalations (confidence ≥ 5 but p in 0.10–0.90) are informationally expensive — the user is resolving genuine ambiguity. Near-certain cases that still trip the threshold (p = 0.89, confidence = 4) are calibration noise — the message should say so.

## Recovery

On uncertainty boundary hit: surface the action, record the outcome (approve/deny) via `decision_log.record_approval_outcome()`, update the posterior for next time.

## Escalation

Surface to the user only when posterior confidence is below threshold — not for every undocumented action. The goal is to converge the uncertainty region over time, not to ask forever.

## Dissent caveat

Preference-learning from approval signals can drift: Shadow learns to frame actions to shift approval probability. The posterior tracks the user's observed preferences, not ground-truth safety. Standing-authority CLAUDE.md rules remain hard constraints and override any learned posterior.

A second caveat from the alignment literature (Hadfield-Menell reward modeling line): a probabilistic posterior doesn't explain *why* an action was escalated. the user needs legible reasons to build trust in the escalation system — always include the human-readable reason alongside the posterior stats, not just the numbers.
