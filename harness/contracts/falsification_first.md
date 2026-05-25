# Contract: falsification-first

## Type
Process gate — harness-enforced (doc-level); code enforcement tracked as Tier 2 backlog item.

## Trigger
Any response involving synthesis of research findings where step 1d (adversarial disconfirmation) was applicable — i.e., the task required forming a position or central claim across multiple sources, not just a factual lookup.

## Precondition
Before synthesizing or presenting conclusions, ALL of the following must hold:
1. The central claim was stated in one sentence prior to synthesis
2. A counter-evidence search was executed (not merely acknowledged)
3. Either disconfirming evidence is surfaced BEFORE supporting evidence, OR a `[TESTED: no disconfirm found]` note is present
4. The output does not lead with accumulating positives and append caveats at the end

## Enforcement
**Harness-enforced** (doc-level). Code-enforcement (`FalsificationFirstGate` in `core/contracts.py`) is in Tier 2 backlog — pending the user review.

For now: Shadow self-checks at Verify stage using the falsification audit step in `harness/skills/research.md`.

## Origin
2026-04-27: arXiv workshop paper "Sound Agentic Science Requires Adversarial Experiments" (cs.AI). Identified that LLM agents in research workflows optimize for narrative coherence and publishable positives without falsification. The fix is structural: flip the default objective from "accumulate support" to "generate disconfirmation first."

## Violation recovery
1. Stop before finalizing synthesis
2. State the central claim in one sentence
3. Run adversarial search: "what evidence would falsify [central claim]?"
4. If disconfirmation found: move it to the top of findings
5. If not found: add `[TESTED: no disconfirm found after [N] searches]` note
6. Then resume synthesis with disconfirmation context locked in

## False positive exemptions
- Single-answer factual lookups ("what year did X happen", "what is the API signature for Y")
- Responses explicitly marked as "quick take" by the user
- Tasks where the user has already provided the central claim and is asking for supporting detail only

## Escalation
If Shadow completes 3+ deep research tasks in a session without any `[TESTED: no disconfirm found]` notes or disconfirmation sections, treat as a falsification-skip pattern — Shadow is optimizing for narrative coherence. Flag in session handoff as a calibration note.
