# Contract: portfolio-source-write-guard

## Type
Pre-action gate — deterministic enforcement via
`core/contracts.py:PortfolioSourceWriteGuard`. Severity: `block`.

## Failure mode
FM-004 (parallel implementation) — a write reaches the portfolio authority
source without going through the canonical module that keeps its projection
in sync.

## Threat model
`state/business_theme_portfolio.json` is the authority;
`state/business_theme_allocations.json` is a generated projection carrying a
`source_hash` of the authority. Every consumer calls `validate_projection`,
which fails closed when the hashes diverge.

A raw `update_json` / `json.dump` write to the authority therefore does not
produce a wrong number — it produces a hard outage. The 2026-07-28 Daily
Moonshot died this way: the source was mutated at 06:10, the allocator was
not rerun, and the 07:00 launcher raised
`portfolio projection is stale; run scripts/business_theme_allocator.py`.

`core/portfolio_store.py:update_portfolio_source` binds the mutation and the
refresh into one step. This guard is what stops new call sites from
reintroducing the unbound write.

## Trigger
Scanned on `Write`, `write_file`, `Edit`, `mcp__shadow__write_file`. A
violation requires all four conditions in the written content:

1. The path is not in `_ALLOWED_PATHS` (`core/portfolio_store.py`, `tests/`,
   `test_`) — the store owns the write, and tests must be able to construct
   the failure.
2. The content does not already call `update_portfolio_source`.
3. `_SOURCE_RE` matches `business_theme_portfolio.json`.
4. `_RAW_WRITE_RE` matches a raw write call: `update_json(`, `save_json(`,
   `write_text(`, or `json.dump(`.

Requiring the source filename *and* a raw write call in the same content is
what keeps doc mentions, comments, and read-only references from firing.

## Precondition
Any code path that mutates the portfolio authority also regenerates the
allocations projection before the turn ends.

## Enforcement
`check_pre` — blocks before the write lands, so the stale projection is never
written in the first place.

## Recovery
Replace the direct write with:

```python
from core.portfolio_store import update_portfolio_source
update_portfolio_source(PORTFOLIO_SOURCE, mutate, default={"bets": []})
```

The store calls `refresh_projection()` on the canonical source, so the
projection's `source_hash` matches before any consumer reads it.

## Defense in depth
This guard is the write-side gate. The read side self-heals independently:
`load_portfolio_projection` regenerates and re-validates on hash mismatch
when both paths are canonical (`core/portfolio_store.py:88`). A projection
written by an unguarded path outside this repo therefore degrades to a
refresh rather than an outage. Both layers exist because the read-side heal
cannot fix a source write that never triggered a regen in a non-canonical
path.

## Escalation
None. This is a mechanical routing fix with a named replacement API — it is
never a the user-facing blocker.
