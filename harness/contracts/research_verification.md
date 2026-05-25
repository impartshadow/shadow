# Contract: research-verification

**Type:** Harness behavioral rule  
**Failure mode:** FM-019 (incomplete response), FM-003 (stale/unverified claims)

## Trigger
When Shadow presents research findings from a single study, case, or example as evidence of a capability, trend, or conclusion.

## Precondition
Shadow must flag when:
- Evidence rests on a single data point (n=1, one pilot, one case study)
- Authors have a stated affiliation with the work they are evaluating
- Methodology is described as "still being built" or "experimental"

## Enforcement
Harness (prose rule). No code gate — applied during research synthesis.

## Required behavior
When any of the above conditions are true, the research output must include a **Credibility red flags** section listing:
- Sample size and what conclusions it does/doesn't support
- Any author conflicts of interest
- Whether methodology is stable or still evolving

Do NOT bury these caveats in footnotes. They belong at the same level as the main finding.

## Recovery
If a research summary is presented without these flags and a condition applies, rewrite the finding with the flag section before posting or archiving.

## Escalation
Escalate to the user only if the finding would affect a production decision (e.g., Shadow is about to act on a capability claim that rests on n=1 evidence).

## Example (motivated by)
CRUX iOS app pilot (2026): Claude shipped one iOS app with 2 errors. This is a strong directional signal for that specific, bounded task — not proof of general software-deployment capability. Narayanan/Kapoor are both CRUX members and commentators (potential bias).
