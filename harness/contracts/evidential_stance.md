# Evidential Stance Contract

**Type:** Behavioral (post-check, research synthesis paths)
**Trigger:** Any research deep-dive or multi-round synthesis producing claims
**Failure mode:** FM-022 (self-consistency) / FM-001 (hallucination)

## Precondition

Before treating a research claim as established:
- The claim must be traceable to ≥1 specific piece of evidence from the source
- Stance scalars above 0.7 (strong agreement/disagreement) require ≥2 independent evidence items
- If evidence is absent or single-sourced, the claim must carry `[unverified]`

## Enforcement

Behavioral (prose contract). Shadow enforces this during synthesis by:
1. Extracting `(claim, supporting_evidence[], stance_scalar)` for each material claim
2. Logging to `state/evidential_log.jsonl` with source attribution
3. Flagging any stance_scalar > 0.7 backed by < 2 evidence items

The `_run_single_dive` function in `scripts/ai_digest.py` is the primary enforcement point — it appends evidential state to `state/evidential_log.jsonl` after each dive.

## Recovery

On weak evidence for a high-confidence stance:
- Downgrade claim language ("may suggest" not "shows")
- Add `[unverified]` to the specific statistic or fact
- Do not suppress the claim — tag it

## Escalation

None — this is a quality signal, not a blocking contract. Surface patterns quarterly during `/improve` sessions if `state/evidential_log.jsonl` shows systematic unanchored stances.

## Rationale

Motivated by Belief Engine (arXiv 2026): BE demonstrates that auditable stance dynamics require an explicit evidential state — scalar beliefs without evidence attribution are uninterpretable and unreliable. Shadow's research pipeline produces actionable takeaways for the user; unanchored stances in those outputs carry risk proportional to their confidence.