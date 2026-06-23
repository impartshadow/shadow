# Contract: live-state-claim-guard

**Type:** Code-enforced (warn-only)
**Failure mode:** FM-026 (live-state assertion without live fetch)
**Location:** `core/contracts.py` → `class LiveStateClaimGuard`

## Trigger
A response asserts current/live external state — prices, market data, news, weather, scores, election counts, third-party model releases — without running a live data tool (`mcp__shadow__web_search`, `mcp__shadow__browse_url`) in the same turn. Model priors decay; a "current price of X" claim from training memory is not live data.

## Precondition
For a violation to fire, ALL of:
1. The response contains a **live-state phrase** matching `_LIVE_STATE_RE`: `currently trading|at|priced`, `today's price/news`, `as of <today/now/<month>>`, `right now`, `latest price/news`, `live price/data`, `at $N rising/falling`, etc.
2. The response contains an **external subject** matching `_EXTERNAL_SUBJECT_RE`: prices, market, stocks, crypto, weather, headlines, sports scores, elections, ChatGPT/Gemini versions, etc.
3. **Proximity:** the external subject must sit within **200 chars** of the live-state phrase (`_PROXIMITY_WINDOW`). Same-paragraph rule — "right now" 800 chars away from an unrelated "score" doesn't count.
4. No live-data tool was called in this turn (`_LIVE_TOOLS = {mcp__shadow__web_search, mcp__shadow__browse_url, ...}`).

Internal-state markers (`state/`, `loops.json`, `MRR`, `subscriber`, `digest`, etc.) are detected separately to avoid firing on internal status reports — those read from local files, not the open web.

## Enforcement
Code-enforced post-check (severity: `warn`). The contract does not block; it logs to `state/contract_violations.jsonl` so post-session audit can spot regressions.

## Recovery
On a warn:
1. If the claim is about external state, re-run the response after a live tool call (`mcp__shadow__web_search "<topic> latest"` or `mcp__shadow__browse_url`).
2. If the claim is about internal state (digest, brief queue, MRR, loops), the warn is a false positive — verify the response doesn't mention an external subject within 200 chars and tighten the trigger if it does.

## Recurring false-positive pattern
Pre-200-char tightening (gap-closer 2026-06-23), this guard fired 7x/24h on long-form Discord/moonshot posts where "right now" and "score" were 600–1200 chars apart and unrelated:
- "Right now we're publishing the hook" + "governance score" 800 chars later (living-index thread)
- "right now the showcase fires off a score regression" + 5 unrelated "score" mentions

The proximity gate eliminates the FP class. If the guard reappears at >3/24h, audit the latest violations for response excerpts and either narrow `_EXTERNAL_SUBJECT_RE` or further tighten `_PROXIMITY_WINDOW`.

## Escalation
None. Warn-only — the post-session audit (`scripts/session_audit.py`) and the gap-closer are the feedback loop.

## Related contracts
- `crypto-price-claim-guard` — predecessor, scoped only to BTC/ETH price claims.
- `partial-evidence-flag` — covers revenue $ claims (separate `_REVENUE_CLAIM_RE` branch with block-severity).
- `factual-claim-verification` — flags uncited statistics/project-state claims; complements live-state by catching past-tense uncited facts.
