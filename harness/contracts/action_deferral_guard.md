# action-deferral-guard

**Type:** Post-check (code-enforced)
**Failure mode:** FM-011 (proposal instead of execution)
**Trigger:** Every response

**Precondition:** Response must not propose or describe an action that Shadow has authority to execute. No "Would you like me to…", "Should I…", "Do you want me to…", "Shall I…".

**Enforcement:** `core/contracts.py:ActionDeferralGuard.check_post()` — pattern-matches proposal phrases. Blocks response and requires retry without deferral.

**Recovery:** Execute directly. Remove the proposal phrase and perform the action.

**Escalation:** Not required. Block silently, execute on retry.
