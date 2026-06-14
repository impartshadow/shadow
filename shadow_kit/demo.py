"""Runnable Shadow Kit proof for installed packages.

Run with:

    python -m shadow_kit.demo
"""

from __future__ import annotations

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


class NoHandoffContract(Contract):
    """Small custom contract used to prove local extension works."""

    name = "no-handoff"
    failure_mode = "FM-DEMO-001"

    def check_post(self, ctx: ContractContext) -> Violation | None:
        if "ask the user to run" not in ctx.response_text.lower():
            return None
        return Violation(
            contract=self.name,
            failure_mode=self.failure_mode,
            message="Response hands off execution instead of using an available tool.",
            severity="block",
            recovery="Execute the action through the tool layer and report the result.",
        )


def _print_violations(label: str, violations: list[Violation]) -> None:
    print(f"\n{label}")
    if not violations:
        print("  allowed")
        return
    for violation in violations:
        print(f"  [{violation.severity.upper()}] {violation.contract}: {violation.message}")
        print(f"    recovery: {violation.recovery}")


def main() -> int:
    push_ctx = ContractContext(
        action="git_push",
        files_edited=["src/main.py"],
        response_text="Done.",
        verification_output="",
    )
    push_violations = check_all_pre(push_ctx)
    _print_violations("1. Unverified push", push_violations)

    push_ctx.verification_output = "tests: 12 passed"
    _print_violations("2. Verified push retry", check_all_pre(push_ctx))

    denial_ctx = ContractContext(
        action="respond",
        response_text="I can't access that repository.",
        tool_calls=[],
        smoke_test_ran=False,
    )
    _print_violations("3. Capability denial before trying", check_all_post(denial_ctx))

    deferral_ctx = ContractContext(
        action="respond",
        response_text=(
            "Here's the approach I'd take:\n"
            "Would you like me to update the file?\n"
            "I can wire the config after that."
        ),
        tool_calls=[],
    )
    _print_violations("4. Action deferral", check_all_post(deferral_ctx))

    register_contract(NoHandoffContract())
    handoff_ctx = ContractContext(
        action="respond",
        response_text="Ask the user to run the migration.",
    )
    _print_violations("5. Custom contract", check_all_post(handoff_ctx))

    receipt = issue_contract_receipt(
        agent_id="demo-agent",
        sequence=1,
        ctx=push_ctx,
        violations=push_violations,
        signing_key="local-demo-key",
        policy_version="shadow-kit-demo-v1",
    )
    verified = verify_receipt(receipt, "local-demo-key")
    print("\n6. Signed receipt")
    print(f"  decision: {receipt['decision']}")
    print(f"  receipt_hash: {receipt['receipt_hash']}")
    print(f"  signature_valid: {verified.valid}")

    metrics = get_governor().get_metrics()
    print("\n7. Governance metrics")
    print(f"  total_violations: {metrics['total_violations']}")
    print(f"  active_contracts: {metrics['active_contracts']}")
    print(f"  violations_by_contract: {metrics['violations_by_contract']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
