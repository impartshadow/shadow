# Self-Evaluation Bias in /improve

**Type:** Heuristic guideline (not code-enforced)
**Trigger:** Any /improve run that uses Claude to evaluate Claude-generated code or contracts

## The risk

When the same model (or same model family) both generates and evaluates code, it tends to reward solutions it finds *plausible* rather than solutions that are *correct*. TRUSTEE (April 2026) identified this as a core risk in self-contained 8B training loops — the evaluator systematically biases toward patterns it already knows.

Shadow's /improve loop has the same structure: Claude generates contract subclasses → Claude (or another Claude instance) evaluates them → new contracts ship. The evaluator may approve contracts that handle cases Claude already handles well while missing blind spots in novel failure modes.

## Dual-rubric requirement (added 2026-04-28)

ESRRSim (Bauer/Meta, Chang/USC — Apr 2026) demonstrated that output-only evaluation of reasoning models is broken: models can produce outputs that satisfy evaluation criteria while the reasoning trace shows they are gaming the test. Detection rates on output alone ranged 14–73% across 11 models; dual-rubric (output + trace) caught cases output-only missed.

For Shadow's /improve loop, this means:

**The output** is the proposed contract or recommendation.
**The reasoning trace** is the actual tool call sequence — which files were read, which grep patterns were run, which deficiency entries were examined.

Both must be audited independently before shipping:

1. **Output audit**: Does the proposed contract address a real, observed failure mode? Does the code handle the stated precondition correctly?
2. **Trace audit**: Do the tool calls in this session substantiate the claimed findings? If Shadow claims "FM-003 is recurring" there must be grep/read calls into deficiency_log or contract_violations that confirm it — not just inference from memory.

If the output passes but the trace doesn't substantiate the finding, treat it as a false positive and reject the improvement.

## Calibration collapse as a distinct failure mode (added 2026-05-04)

Paper: *Continual Calibration* (Semantic Scholar, Apr 2026) — across 3 model families and 8 task sequences, calibration (confidence quality) degraded ~3.4x faster than accuracy under sequential fine-tuning. In the sharpest case, conformal coverage dropped 0.92 → 0.61 while top-1 accuracy stayed within 3 points.

Shadow's analog: after many /improve cycles, Haiku judge accuracy (correct binary verdicts on `self_consistency_check` and `persistent_correction`) may stay stable while the judge's **confidence distribution** silently collapses — always returning 0.9+ certainty regardless of actual case difficulty. This would make the judge useless as a calibrated signal while appearing healthy by pass/fail metrics.

### Detection signal

If Haiku-judged contract calls log confidence scores, a healthy judge shows spread across [0.5, 1.0]. Collapse looks like: >80% of calls returning scores above 0.85, OR a bimodal distribution clustering at 0.6 and 0.95 with nothing in between. Run this check after every 10+ /improve cycles.

### Mitigation

- Log confidence scores from every Haiku judge call (not just the binary verdict)
- After 10+ /improve iterations, plot or bucket the confidence score distribution
- If distribution collapses (SD < 0.08 or >80% above 0.85), treat judge output as unreliable and flag for the user — accuracy-only metrics can no longer be trusted
- Paper's cheap fix: hold out ~5–10 real violation examples per contract type; periodically recheck judge confidence on these anchors. If anchor confidence drifts, the judge is miscalibrated.

## Ground-truth anchor requirement for Haiku judges (added 2026-05-14)

Paper: *Neurodata Without Boredom* (arXiv cs.LG, May 2026) — general-purpose coding agents completed sub-tasks reliably but failed end-to-end pipelines without errors. Crucially: **agents-as-judges failed to catch errors when no ground-truth reference was provided**. Without an anchor to compare against, the judge evaluates plausibility rather than correctness.

Shadow's `behavioral-haiku-guard` and `self-consistency-check` both use Haiku to evaluate a response in isolation — passing only the response text, not the original user request. This means Haiku can only judge internal coherence, not whether the response actually addressed what was asked.

### Mitigation

- **Always pass the user's original request alongside the response** in Haiku judge prompts. The request is the ground-truth anchor: it defines what "correct" looks like.
- When the user message is unavailable (empty `ctx.user_message`), log the verdict as `low_confidence: true` — the judge is operating without an anchor.
- For `behavioral-haiku-guard` specifically: the most important failure modes (FM-011 proposing instead of acting, FM-012 instructing the user instead of doing) are only detectable if the judge knows what was asked. A "here's how you could do X" response looks fine in isolation but is a clear FM-011 if the request was "do X".

### Sub-task vs pipeline correctness

The same paper found sub-task success does not predict pipeline success. For Shadow's multi-step tasks (research → write → post, or fetch → transform → commit → push):

- Each step completing without error is necessary but not sufficient
- The session audit should verify that claimed end-to-end completions are supported by observable artifacts (commits in git log, messages in Discord history, state file changes)
- A turn-by-turn quality score of 9/10 does not imply the pipeline actually completed

This motivated adding `PIPELINE_COMPLETENESS` scoring to `scripts/session_audit.py` (see that file).

## Mitigations already in place

- `post-response-evaluator` contract provides an independent check on response quality
- `loop-tripwire` prevents runaway self-modification
- the user reviews Tier 2 changes before merge

## Additional mitigations to apply

1. **Novel failure modes should be stress-tested against session transcripts**, not just unit tests. A contract that passes synthetic tests but never fires on real violations is a false positive.
2. **Prefer contracts triggered by observable tool outputs** (grep results, file reads) over contracts triggered by Claude's self-assessment of its own response quality.
3. **When /improve generates a new contract, explicitly ask: what case would this contract miss?** Document the answer in the contract file.
4. **Trace check before shipping**: Before committing any /improve output, verify at least one of these in the session: a grep into deficiency_log.jsonl, a read of contract_violations.jsonl, or a read of a real conversation transcript. If none of these tool calls happened, the finding is not evidence-grounded.

## Contract staleness signal

A contract that never fires in production for 30+ consecutive days is ambiguous: the behavior may be fixed, the contract may be irrelevant, or the model may be adapting around it. Static enforcement mechanisms age quickly — ESRRSim shows capability improvements compound month-over-month. The `get_silent_contracts()` function in `core/deficiency_tracker.py` surfaces these for review.

## Escalation

If three consecutive /improve runs produce contracts that never fire in production, flag for the user — this is evidence of evaluation bias generating plausible-but-useless contracts.

If a proposed improvement has no supporting tool calls in the session trace, reject it and explicitly note "trace-unsupported" in the session handoff.

If Haiku judge confidence score distribution collapses (per calibration collapse section above), flag for the user — accuracy-based evaluation of contracts is no longer reliable.