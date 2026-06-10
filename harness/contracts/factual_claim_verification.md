# Contract: factual-claim-verification

**Type:** Code-enforced (Python `Contract` subclass in `core/contracts.py`)
**Failure mode:** FM-029 (generation-verification gap)
**Severity:** warn (does not block)

## Trigger

Fires post-response when both are true:

1. The response contains either an uncited statistic (number + unit like `%`, `users`, `days`, `months`) OR a project-name assertion involving an active project (`arbor`, `anvil`, `awg`, `moltbook`, `echo`, `upwork`, `substack`, `stripe`).
2. No evidence-producing tool was called in this turn (the canonical set lives in `_EVIDENCE_TOOLS` on the contract — currently `Read`, `Bash`, `Grep`, `Glob`, and the `mcp__shadow__*` retrieval tools).

If the response opens with an evidence-source tool call (or contains hedging words like `appears`, `seems`, `based on`), the contract is silent.

## Precondition

Any time Shadow makes a factual assertion about state outside this turn's tool output — past Shadow behavior, project status, counts, timing — the assertion must either be hedged or backed by an evidence call in the same turn.

## Enforcement

`FactualClaimVerificationContract.check_post` in `core/contracts.py`.

Two checks:
- **Statistic check** — finds quantity-with-unit patterns. Fires if the sentence containing the stat has no hedging word AND no evidence tool was called this turn.
- **Project-claim check** — finds project-name mentions. Skips bare lists/identifier soup and file paths (e.g., `echo/twitter.py`). Requires an actual assertion verb (`is`, `has`, `emits`, `posts`, `runs`, `broke`, `live`, `dead`, etc.) in the same sentence before firing.

## Recovery

When this fires, the response either:
- Adds a hedge: `"Echo appears to be dark based on the last posted_at stamp."`
- Adds an evidence call: open the relevant state file or run the check, then re-state with citation: `"Echo is dark — state/echo_posts.jsonl shows last entry 2026-05-19."`

The contract is warn-only because some claims (recent in-context observations from the same turn's earlier tool calls) are legitimate. The agent must judge whether the warn is signal or noise.

## Escalation

No automatic escalation. Repeated fires in a single session indicate the agent is making assertions from memory instead of from live state — surface in the next session handoff or session-audit report.

## Why narrowing happened (2026-05-30)

The contract was previously firing on:
- Identifier lists: `"(arbor, echo, substack, digests)"` → flagged as project claim
- File paths: `"echo/twitter.py"` → flagged as project claim
- Bare project names with no assertion: `"echo...."` → flagged

The `_EVIDENCE_TOOLS` set also contained only legacy names (`read_file`, `run_shell`), so the cited-source exemption never fired — `Read` and `Bash` calls were not counted as evidence. Both were repaired in the same commit.

## Tests

`tests/test_contracts.py::TestFactualClaimVerificationContract`
