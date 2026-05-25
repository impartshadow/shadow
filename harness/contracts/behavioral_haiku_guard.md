# Contract: behavioral-haiku-guard

## Type
Post-check — Haiku-judged, warn-only.

## Trigger
Every `respond` action where `response_text` is >= 120 characters.

## Failure modes evaluated
- FM-001: Claiming inability without showing an attempt first
- FM-011: Proposing or describing instead of executing
- FM-012: Instructing the user to do something manually the agent could handle
- FM-013: Responding beyond the scope of what was asked
- FM-019: Unnecessary hedging, clarification requests, or trailing off

## Enforcement
`BehavioralHaikuGuard` in `core/contracts.py` — single Haiku call with a strict rule-based prompt. Fires if confidence >= 0.82.

## Current architecture (single-judge)

One Haiku call per response, using a rule-enumeration prompt ("does this response match FM-NNN patterns?").

This is a **homogeneous ensemble of one** — the known failure mode from ensemble monitoring research. A single judge has:
- No mechanism to catch violations it systematically misses
- No false-positive suppression from a disagreeing second opinion
- No signal distinguishing "confident correct" from "confidently wrong"

## Target architecture (dual-judge — Tier 2 upgrade)

Run **two** Haiku calls in parallel with uncorrelated prompts:

1. **Judge A — rule-based (current)**: enumerates FM patterns explicitly, asks for pattern match.
2. **Judge B — intent-based (new)**: does not enumerate FMs. Instead asks: "What was the user asking for? Did this response accomplish it, or did it defer/propose/hedge? Return the dominant failure if any."

Fire violation if **either** judge returns confidence >= threshold. This implements the ensemble diversity principle without requiring a stronger model:
- Judge A catches explicit pattern matches ("would you like me to")
- Judge B catches structural intent failures that don't surface pattern tokens
- Their failure modes are uncorrelated — Judge B catches what Judge A systematically misses

The cheapest version does NOT require both judges to agree (AND logic). Requiring consensus raises the false-negative rate. OR logic (fire if either hits) is the correct operationalization of "diverse monitors outperform homogeneous ones."

## Why OR not AND

The 2.4x detection gain in the ensemble paper comes from coverage complementarity — each monitor catches a different subset of failures. AND logic would eliminate the gain by requiring overlap where there is none. OR logic with independent prompts is the correct implementation.

## False-positive mitigation

To prevent OR logic from increasing false positives:
- Keep Judge B's confidence threshold at 0.82 (same as Judge A)
- Judge B prompt must include the same exception list (auth walls, hardware 2FA, etc.)
- Both judges read the same response text

## Recovery
Same as current: surface the highest-confidence violation, warn-severity, inject recovery instruction.

## Research basis
**Ensemble Monitoring for AI Control: Diverse Signals Outweigh More Compute** (arXiv cs.AI, 2026)

12 GPT-4.1-Mini monitors across prompting and fine-tuning strategies. Best 3-monitor ensemble achieves 2.4x detection gain vs. three identical monitors. Key finding: gain comes from diversity of failure modes, not scale or compute. Fine-tuned monitors appear in every top-performing ensemble.

External validity caveat: tested on coding tasks (adversarial test-passing). The paper does not validate "diversity beats scale" for open-ended agentic monitoring — in non-code domains, monitors may converge on the same surface features regardless of prompting strategy. The dual-judge upgrade is warranted but expected gains may be smaller in Shadow's open-domain context.
