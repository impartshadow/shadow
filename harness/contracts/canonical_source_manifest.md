# Contract: canonical-source-manifest (FM-014)

## Type
Production-site gate — code-enforced in `core/canonical_sources.py`

## What it is
The state manifest: each fact-class declares, in one place, its single
authoritative source, the read-signatures that prove that source was consulted,
the known-wrong sources that have been mistaken for it, and the ONE module
allowed to produce it. A fact value cannot leave its producer without proving it
read the authoritative source.

This is the production-site mirror of `CanonicalSourceGuard`, which checks the
*response text*. The manifest catches the wrong-source read where the value is
*produced*, before it ever flows downstream as asserted truth.

## The two layers

1. **Reader side (annotation):** `match(question)` → which fact-class a question
   is about; `source_for(key)` → its `FactSource`. Monitors and guards read from
   here so there is exactly one definition of "where the truth lives."
2. **Producer side (enforcement):** `cite(key, value, source)` constructs a
   `FactValue` that validates `source` against the registry at construction — a
   `FactValue` cannot exist for a wrong/uncited source. `@must_cite_source(key)`
   wraps a producer so it must return that `FactValue`, and (when `owner` is set)
   so only the declared owner module may produce the fact.

## Registered facts (manifest)

| Fact | Owner (writer) | Authoritative source | Known-wrong |
|---|---|---|---|
| `revenue.mrr` | `scripts/stripe_check.py` | Stripe live `Subscription.list` (× $29) | substack subscriber count, projections, "should be" |
| `rent.paid` | — | Gmail, landlord autopay confirmation (Real Property Mgmt) | Zelle/Mary Stanford, Ally reminder, calendar entry |
| `twitter.posted` | — | `core.liveness age_hours('twitter.posted')` | derived `posted_at` log |

## How to add a fact to the manifest
1. `register(FactSource(key=..., aliases=..., authoritative=..., verify_signals=..., wrong_signals=..., owner=...))` in `core/canonical_sources.py`. Encode a real past miss in `wrong_signals` so the wrong source is never re-guessed.
2. Wrap the producer with `@must_cite_source("<key>")` and return `cite("<key>", value, source="<what you actually read>")`.
3. Set `owner` to the producer's module path so no other module can emit the fact.
4. Add a test in `tests/test_contracts.py` (accept authoritative, reject wrong source, reject non-owner).

## Enforcement
- `cite()` raises `WrongSourceError` on a known-wrong source or one carrying no verify_signal; `CanonicalSourceError` on an unregistered fact.
- `@must_cite_source` raises `UncitedFactError` if the producer returns a bare value, `CanonicalSourceError` if a non-owner module produces the fact.

## Recovery
On a raise: the producer read the wrong source. Re-read the authoritative source
named in `FactSource.authoritative` and re-`cite()` from it. Do not unwrap the
decorator to make the value pass — that re-opens the wrong-source class.

## Origin
The "Zelle is the rent" and 282h-tweet misses: a read DID happen, but of the
wrong source, asserted as truth. No recency stamp or assert-from-memory guard
catches that — only knowing which source is authoritative does. Built out from
`CanonicalSourceGuard` (response-text) into a production-site gate so wrong-source
reads raise where produced, not downstream. Audit thread across
#moonshot/#echo/#shadow-hq, 2026-05-30.
