# Contract: harness-scaffold-egress-guard

## Type
Post-check (sanitizes before external send)

## Trigger
Any response payload destined for an external sink (Discord, email, Substack, Moltbook, X)

## Failure mode
FM-015 — internal scaffolding leaking to user-facing surfaces

## What it prevents
Harness-internal scaffolding tokens appearing in external responses:
- Bracketed tags: `[Channel: ...]`, `[Executing: ...]`, `[System: ...]`, `[Tool: ...]`, `[Resume context: ...]`, `[Bot just restarted: ...]`, `[Completed before restart: ...]`
- Bare scaffold phrases at line start (de-bracketed variants)

the user sees results, not harness execution scaffolding.

## Enforcement
Code-enforced in `core/contracts.py::HarnessScaffoldEgressGuard`. Two-layer detection:
1. Bracketed harness tags anywhere on a line
2. Bare scaffold phrases at line start

Recovery behavior:
- If sanitization leaves non-empty content: rewrite payload in place, log violation, allow send
- If sanitization leaves empty/whitespace-only content: block send entirely

## Companion contract
`HarnessScaffoldingLeakGuard` catches internal repair metadata (`**Corrected Response:**`, `Repair Summary:`) in Discord channels specifically.

## CLAUDE.md rule
Rule 15: "Never surface `[Executing: ...]` or `[Channel: ...]` preambles or raw command blocks in user-facing channels — the user sees results, not the harness's execution scaffolding."
