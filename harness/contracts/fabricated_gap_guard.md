# Contract: fabricated-gap-guard

## Type
Post-response guard — deterministic enforcement via `core/contracts.py`

## Trigger
Any response that claims Shadow infrastructure is missing, needed, or
should be built — when paired with Shadow-internal vocabulary — and no
investigation tool (Grep / Glob / Read / Bash / mcp__shadow__read_file /
mcp__shadow__list_directory / session_search / memory_search) was called
in the same turn.

## Precondition
When claiming a gap exists in Shadow's own codebase (contracts, scripts,
harness, skills, nightly, self-audit, etc.), ONE of the following must
be true in the same turn:
1. A Grep ran against the relevant file / directory
2. A Glob or Bash `ls`/`find` enumerated what's there
3. A Read fetched the file being discussed
4. An MCP Shadow tool surfaced the relevant state

## Enforcement
**Code-enforced** in `core/contracts.py:FabricatedGapGuard` — scans outgoing
responses for gap-claim patterns co-occurring with Shadow-infra vocabulary,
and fires when no investigation tool was called this turn.

## Origin
2026-04-18 conversation with the user: after the bold-self-improvement
directive, Shadow listed five "problems" in its own infra. Verification
showed four were fabricated (MEMORY.md wasn't near its limit, two
contracts already had tests, the "forcing function" I proposed already
runs nightly at 02:30 CT). Pattern: pattern-matching from general
agent-architecture intuition onto Shadow specifically, without grounding.

## Violation recovery
Grep or read the actual repo to confirm the gap. If it already exists,
retract the proposal. If the gap is real, cite the evidence (file paths
checked, what was absent). Never propose self-improvement work based on
vibes alone — Shadow has substantial existing infrastructure (nightly
self-audit, Bilevel pattern, `/improve`, memory decay, regression tests,
contract enforcement) that general intuition will keep re-discovering.

## Exemption
If the gap claim appears inside a fenced code block (specification text,
example, quoted prior message), the shared `_strip_light` utility removes
it before pattern-matching. This allows meta-discussion about contracts
without firing the guard.

## Escalation
If this contract fires more than twice in a single session, treat as a
calibration incident — Shadow is drifting into ungrounded proposals.
Slow down, read the relevant code, and revert the unverified claims.
