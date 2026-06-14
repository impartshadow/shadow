"""
basic_assistant.py -- Example: setting up Shadow Kit contracts for a basic assistant.

This shows how to wire contract checking into your agent's action/response loop.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shadow_kit.contracts import (
    Contract,
    ContractContext,
    Violation,
    check_all_post,
    check_all_pre,
    get_governor,
    register_contract,
)
from shadow_kit.receipts import issue_contract_receipt, verify_receipt


# ---------------------------------------------------------------------------
# 1. Use built-in contracts out of the box
# ---------------------------------------------------------------------------

def example_verify_before_push():
    """The agent tries to push code without verification output."""
    ctx = ContractContext(
        action="git_push",
        files_edited=["src/main.py"],
        response_text="Fixed the bug. Done.",
        verification_output="",  # No verification!
    )

    violations = check_all_pre(ctx)
    for v in violations:
        print(f"[{v.severity.upper()}] {v.contract}: {v.message}")
        print(f"  Recovery: {v.recovery}")
        # => [BLOCK] verify-before-push: Push attempted without verification output.

    # Now with verification:
    ctx.verification_output = "12 passed, 0 failed"
    violations = check_all_pre(ctx)
    print(f"After verification: {len(violations)} violations")  # => 0


# ---------------------------------------------------------------------------
# 2. Catch capability denial
# ---------------------------------------------------------------------------

def example_denial_gate():
    """The agent says it can't access something without trying."""
    ctx = ContractContext(
        action="respond",
        response_text="I can't access the database from here. "
                      "I don't have permission to fetch those records.",
        tool_calls=[],
        smoke_test_ran=False,
    )

    violations = check_all_post(ctx)
    for v in violations:
        print(f"[{v.severity.upper()}] {v.contract}: {v.message}")
        # => [BLOCK] pre-denial-gate: Denial without smoke test.

    # The agent should have tried first:
    ctx.tool_calls = ["run_query"]  # Tool was actually called
    violations = check_all_post(ctx)
    print(f"After trying: {len(violations)} violations")  # => 0


# ---------------------------------------------------------------------------
# 3. Detect proposal-instead-of-action
# ---------------------------------------------------------------------------

def example_action_deferral():
    """The agent proposes what it would do instead of doing it."""
    ctx = ContractContext(
        action="respond",
        response_text=(
            "Here's the approach I'd take:\n"
            "Step 1: Read the config file\n"
            "Step 2: Update the database URL\n"
            "Would you like me to go ahead with this?"
        ),
        tool_calls=[],
    )

    violations = check_all_post(ctx)
    for v in violations:
        print(f"[{v.severity.upper()}] {v.contract}: {v.message}")
        # => [BLOCK] action-deferral-guard: Response proposes an action...


# ---------------------------------------------------------------------------
# 4. Register a custom contract
# ---------------------------------------------------------------------------

class ProfanityGuard(Contract):
    """Custom contract: block responses containing profanity."""
    name = "profanity-guard"
    failure_mode = "FM-CUSTOM-001"

    _BAD_WORDS = {"damn", "hell"}  # Keep it mild for the example

    def check_post(self, ctx: ContractContext) -> Violation | None:
        words = set(ctx.response_text.lower().split())
        found = words & self._BAD_WORDS
        if found:
            return Violation(
                contract=self.name,
                failure_mode=self.failure_mode,
                message=f"Response contains blocked words: {found}",
                severity="warn",
                recovery="Rephrase without profanity.",
            )
        return None


def example_custom_contract():
    """Register and use a custom contract."""
    register_contract(ProfanityGuard())

    ctx = ContractContext(
        action="respond",
        response_text="What the hell happened to the database?",
    )

    violations = check_all_post(ctx)
    for v in violations:
        print(f"[{v.severity.upper()}] {v.contract}: {v.message}")
        # => [WARN] profanity-guard: Response contains blocked words: {'hell'}


# ---------------------------------------------------------------------------
# 5. Monitor contract health
# ---------------------------------------------------------------------------

def example_governance():
    """Check governance metrics after running contracts."""
    governor = get_governor()
    metrics = governor.get_metrics()

    print(f"Total violations: {metrics['total_violations']}")
    print(f"Violations last hour: {metrics['violations_last_hour']}")
    print(f"Active contracts: {metrics['active_contracts']}")
    print(f"By contract: {metrics['violations_by_contract']}")

    hot = governor.get_hot_contracts(window_seconds=3600, threshold=2)
    if hot:
        print(f"Hot contracts (firing too often): {hot}")


# ---------------------------------------------------------------------------
# 6. Issue a signed audit receipt
# ---------------------------------------------------------------------------

def example_signed_receipt():
    """Turn a contract decision into a verifiable audit artifact."""
    signing_key = "local-dev-key"
    ctx = ContractContext(
        action="git_push",
        files_edited=["src/main.py"],
        response_text="Done.",
    )
    violations = check_all_pre(ctx)

    receipt = issue_contract_receipt(
        agent_id="demo-agent",
        sequence=1,
        ctx=ctx,
        violations=violations,
        signing_key=signing_key,
        policy_version="demo-policy-v1",
    )

    print(f"Decision: {receipt['decision']}")
    print(f"Receipt hash: {receipt['receipt_hash']}")
    print(f"Signature valid: {verify_receipt(receipt, signing_key).valid}")


# ---------------------------------------------------------------------------
# Run all examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Verify before push")
    print("=" * 60)
    example_verify_before_push()

    print()
    print("=" * 60)
    print("Example 2: Denial gate")
    print("=" * 60)
    example_denial_gate()

    print()
    print("=" * 60)
    print("Example 3: Action deferral")
    print("=" * 60)
    example_action_deferral()

    print()
    print("=" * 60)
    print("Example 4: Custom contract")
    print("=" * 60)
    example_custom_contract()

    print()
    print("=" * 60)
    print("Example 5: Governance metrics")
    print("=" * 60)
    example_governance()

    print()
    print("=" * 60)
    print("Example 6: Signed receipt")
    print("=" * 60)
    example_signed_receipt()
