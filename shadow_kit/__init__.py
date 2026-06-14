"""Shadow Kit core -- contract enforcement for AI agent harnesses."""

from shadow_kit.contracts import (
    Contract,
    ContractContext,
    ContractGovernor,
    Violation,
    attempt_auto_recovery,
    check_all_post,
    check_all_pre,
    get_contract,
    get_governor,
    list_contracts,
    register_contract,
)
from shadow_kit.receipts import (
    ReceiptVerification,
    canonical_hash,
    issue_contract_receipt,
    issue_receipt,
    receipt_hash,
    verify_receipt,
)

__all__ = [
    "Contract",
    "ContractContext",
    "ContractGovernor",
    "ReceiptVerification",
    "Violation",
    "attempt_auto_recovery",
    "canonical_hash",
    "check_all_post",
    "check_all_pre",
    "get_contract",
    "get_governor",
    "issue_contract_receipt",
    "issue_receipt",
    "list_contracts",
    "receipt_hash",
    "register_contract",
    "verify_receipt",
]
