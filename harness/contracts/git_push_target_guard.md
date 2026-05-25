# git-push-target-guard

**Type:** Pre-check (code-enforced)
**Failure mode:** FM-015 (wrong push target)
**Trigger:** Any git push operation

**Precondition:** Push target branch must match the current feature branch or main. Remote must be the expected origin.

**Enforcement:** `core/contracts.py:GitPushTargetGuard.check_pre()` — validates remote and branch before allowing push.

**Recovery:** Confirm target branch. Never force-push to main without explicit user instruction.

**Escalation:** Surface to the user if the intended target is ambiguous.
