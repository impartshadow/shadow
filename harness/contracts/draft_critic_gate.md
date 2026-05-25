# draft-critic-gate

**Type:** Post-condition (harness-enforced, Haiku-judged)
**Failure mode:** FM-034 (factual output error)
**Trigger:** Any substantive outbound draft — email body, research summary, or plan — longer than 150 words.

## Precondition
A draft has been generated for delivery to the user or a third party.

## Enforcement
Harness-side: before delivering the draft, run a Haiku self-critique pass with the prompt:

> "Review this draft for: (1) factual claims that contradict what you know about the subject, (2) internal inconsistencies, (3) misattributed sources or unverified numbers. List issues found, or reply PASS if none."

If Haiku returns anything other than PASS, surface the critique inline before delivery and ask Shadow to resolve.

## Recovery
On FAIL: revise the flagged claims, re-run the critic pass, deliver only after PASS.

## Escalation
If three consecutive drafts fail the critic pass, escalate to the user with both the draft and the critique output.

## Notes
- This is the clinical-safety-review analog from VST: AI generates, critic checks, human reviews only if critic flags.
- Automation bias risk: critic pass must be substantive (not rubber-stamp). The Haiku prompt is deliberately adversarial.
- Does NOT apply to short factual replies (< 150 words) or status messages.