# third-party-state-claim-verification-guard

Blocks definitive positive claims that a named external system is connected,
authorized, linked, authenticated, or has access/permission enabled unless a
same-turn tool result contains both the named system and the claimed state.

A local proxy signal such as a successful click, responsive desktop, running
process, or service restart is not authoritative evidence for remote state.
When the external system cannot be read back, the response must say the action
was attempted and the outcome remains unverified.

Origin: on 2026-10-12 Shadow reported that dot access was enabled after driving
a headless GUI. The next turn admitted GUI control and dot access were
incomplete. The guard enforces the missing entailment boundary rather than a
dot-specific workflow.

Runtime enforcement: `contracts/third_party_state_claim_verification_guard.py`;
incident replay: `tests/test_third_party_state_claim_verification_guard.py`.
