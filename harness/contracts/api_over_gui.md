# API-first tool routing

## Type
**Code-enforced pre-check** — `ApiFirstRoutingGuard` in `core/contracts.py` (FM-004, warn-only).
Fires when `browse_url` or `browser_open` targets a domain that has a canonical API client.
See `harness/contracts/binding_time_principle.md` for the complementary design principle (not code-enforced).

## Motivation
Reflex's computer-use research (cited Innermost Loop 2026-05-06) measured a **45x cost premium** for pixel/screenshot-based agents versus API-native agents on equivalent tasks. The cost to act autonomously is dropping, but only for agents that use structured interfaces.

## Principle
When selecting a tool or automation approach, always prefer structured API routes over GUI or screenshot-based navigation:

1. **If a structured API exists** — use it. Never fall back to browser automation, screenshot parsing, or simulated mouse/keyboard when an API call achieves the same result.
2. **If evaluating two equivalent tools** — the one with a structured API response wins over the one requiring HTML scraping or visual parsing.
3. **If building a new integration** — check for an official API before reaching for any browser automation library.
4. **If asked to "automate X" where X is a UI** — first ask: is there an API for X? Check `reference_capability_inventory.md` and attempt an API call before any screenshot path.

## Cost signal
45x is a decision boundary, not a nudge. If an API path exists and Shadow chooses a GUI path instead, that is a routing error regardless of whether it succeeds.

## Enforcement
- `core/contracts.py → ApiFirstRoutingGuard` (pre-check, warn, committed `b6ac60a`)
- `tests/test_contracts.py → TestApiFirstRoutingGuard` (8 tests)

## Contracts referenced
- `capability_misroute.md` — primary routing gate
- `tool_routing_priors.md` — data-informed calibration principle
- `pre_denial_gate.md` — must attempt API before denying capability

## Escalation
If a task requires GUI automation because no API exists, document that gap explicitly: "No API found for X — using GUI path as fallback." This creates a signal for future API integrations.
