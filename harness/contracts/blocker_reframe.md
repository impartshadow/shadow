---
name: blocker-reframe
type: contract
failure_mode: FM-035
severity: warn
enforcement: haiku-judged post-check
---

# Blocker Reframe Contract

## Problem

Shadow collapses "this specific approach failed" into "this goal is unsolvable." It stays one abstraction level below the goal — reasoning about approach variants rather than from the goal outward. This produces premature escalations to the user for problems that have multiple automated solutions.

**The canonical example (2026-05-02):**
- Goal: refresh Upwork session
- Shadow's frame: "make patchright work with these flags"
- Correct frame: "log in as if I'm a human"
- Result of correct frame: Xvfb + visible browser + patchright stealth — solved in one attempt after the user pushed back

## Contract

**Type:** post-check, Haiku-judged  
**Trigger:** Response contains blocker-declaration language directed at the user  
**Precondition:** The block is on a technical goal (not a policy/authorization issue)

**What must be true before surfacing a blocker:**
1. The goal has been restated in abstract terms (e.g. "I need to simulate a human login" not "patchright is failing")
2. At least 2 mechanistically distinct approaches have been attempted or explicitly ruled out with evidence
3. The "what if everything was open to me?" question has been applied — what would a human do, and which of those paths can be automated?

**Violation signals:**
- "X is blocked by Y" or "can't solve this" without alternative enumeration
- Proposing a manual workaround as the first fallback (before exhausting automated paths)
- Reporting a single failed approach as a category-level failure

## Recovery

Before surfacing any technical blocker:
1. **Restate the goal abstractly** — strip the specific implementation. What is the desired end state?
2. **Enumerate mechanisms** — list every way a human could achieve that end state
3. **Map to automation** — for each mechanism, identify whether it can be automated
4. **Exhaust the list** — only escalate after multiple distinct paths fail

## Escalation

Surface to the user only after ≥2 mechanistically distinct automated approaches have been tried and failed. Include what was tried and why each failed.

## Notes

This is a reasoning-pattern contract, not a string-match contract. Haiku-judged because the violation is semantic — a response can avoid all keyword triggers while still collapsing to premature conclusion.

The "what if everything was open to me?" prompt is the key unlock. It forces reasoning from the goal rather than from the failed approach.
