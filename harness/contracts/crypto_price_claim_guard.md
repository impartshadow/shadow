# Contract: crypto-price-claim-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:CryptoPriceClaimGuard`. Severity: `block`.

## Failure mode
FM-026 — stale/fabricated live-state assertion. A response states a crypto
price figure (`$97K`, `$63,500 BTC`, etc.) without invoking a live price
fetch (`mcp__shadow__web_search` or `mcp__shadow__browse_url`) in the same
turn.

## Origin
2026-06-08 #finance incident: Gemini produced "$97K–$102K" BTC figures from
model priors during a fallback path while the actual price was ~$63K. the user
caught the gap when his Coinbase screenshot diverged from Shadow's stated
number. The model has no offline access to live prices and must always
ground crypto figures in a same-turn fetch.

## Trigger
A response is flagged when BOTH:
1. The text matches `_PRICE_CLAIM_RE` — a dollar figure (`$97,000`, `$102K`)
   or a token-paired figure (`63K BTC`, `2,400 ETH`).
2. The text contains crypto context (`bitcoin`, `BTC`, `ethereum`, `ETH`,
   `crypto`, `coinbase`, `binance`, `satoshi`, etc.).

The contract carves out historical/discussion contexts via `_HISTORICAL_RE`
(`in 2021`, `back when`, `all-time high`, `peaked at`, `last year`) — those
are not live-state claims and need no fetch.

## Enforcement
After the live-state claim is detected, the contract inspects the same
turn's tool calls. If none match `_LIVE_PRICE_TOOLS`
(`mcp__shadow__web_search`, `mcp__shadow__browse_url`, or their aliases),
the response is blocked.

## Recovery
Run `mcp__shadow__web_search` or `mcp__shadow__browse_url` to fetch the live
price, then re-emit the response with the fetched figure and a `[source]`
citation. If the figure is genuinely historical, phrase the claim with an
explicit historical anchor (`in 2021`, `as of <date>`) so the carve-out
matches.

## Related contracts
- `live-state-claim-guard` — generalizes this rule to any live-state assertion
  (current events, system status, "as of today", etc.). Same enforcement
  shape, different trigger set.
- `partial-evidence-flag` — fires alongside on revenue-style claims; together
  they form the "definitive figure without provenance" gate.

## the user-facing rule (CLAUDE.md alignment)
This contract operationalizes rule 21 ("the user provides a screenshot/visual
and Shadow's CLI data disagrees, state the conflict first") at the
generation step rather than the correction step — by blocking the
unsupported figure before it ships, the screenshot/CLI conflict never
materializes.

## Recent activity
5 violations in last 24h (2026-06-14) — four during a single Coinbase CDP
build sequence between 01:00 and 01:48 UTC. Contract caught every instance;
no recovery skips logged.
