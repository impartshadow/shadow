# Retrieval Strategy: Grep-First Principle

**Type:** Standing principle (validated by empirical research)  
**Research source:** "Is Grep All You Need? How Agent Harnesses Reshape Agentic Search" (2605.15184)  
**Implemented by:** Memory retrieval layer (`core/memory_search.py`), contract enforcement (`core/contracts.py`)

---

## The Finding

Empirical study across agentic workflows: simple grep-based (BM25) and keyword retrieval often match or exceed complex semantic search (embedding-based RAG) on realistic agent queries. Gains from semantic search are **not guaranteed**; they require **measurement**.

### Core Principle

**Default to grep/BM25. Add semantic search only when precision gap is demonstrated.**

This is not "embeddings are bad"—it's "don't add complexity without evidence."

---

## Shadow's Implementation

### Current State

Shadow uses **hybrid retrieval** (RRF fusion of BM25 + semantic):

```python
# core/memory_search.py
def hybrid_search(query: str, n_results: int = 5, filter_type: str = "") -> dict:
    """Merge BM25 + semantic retrieval via Reciprocal Rank Fusion."""
    # BM25 retrieval (keyword)
    bm25_results = _bm25_search(query, fetch_n)
    # Semantic retrieval (embedding)
    sem_results = _query_collection(query, fetch_n)
    # Fuse via RRF, rerank by salience (recency + reinforcement)
    return merge_and_rank(bm25_results, sem_results)
```

This is **justified** because:
1. A benchmark harness (`scripts/benchmark_retrieval.py`) validates the hybrid approach on 15 test queries covering keyword-matching, semantic, and mixed intent queries.
2. Results show hybrid > pure semantic on mixed queries (where Shadow operates).
3. The baseline is established; future degradation will be detected.

---

## Behavioral Guards Use Deterministic Matching

**FM-011** (ActionDeferralGuard) and **FM-033** (PatternerStop) do NOT use LLM-scored similarity:

- **FM-011**: Pure regex patterns (18 patterns matching "would you like", "shall I", "here's my approach", etc.)
- **FM-033**: Bounded Haiku evaluation against explicit behavioral stops — not free-form semantic judgment

This validates the paper's insight: constraints (explicit directive set) beat similarity scoring for behavioral boundaries.

---

## When to Measure

### Add semantic search if:
- Benchmark shows >10% precision gap favoring semantic over BM25 on your query set
- The use case requires fuzzy intent matching (e.g., "how to handle user corrections" vs "feedback")
- Cross-file dependency detection needs learned representations

### Stick with BM25 if:
- Benchmark shows hybrid ≈ BM25 (within 5%)
- Query tokens are exact or near-exact (e.g., "Discord migration", "OpenClaw architecture")
- Latency is a constraint (BM25 is ~10x faster than embedding lookup)

---

## References

- Benchmark tool: `scripts/benchmark_retrieval.py`
- Memory search: `core/memory_search.py` (BM25 at line 382+, semantic at line ~150)
- Hybrid fusion: RRF at line ~160
- Test queries: `scripts/benchmark_retrieval.py:TEST_QUERIES` (15 real queries)

---

## Action Items

1. **Quarterly benchmark re-runs**: Re-run `python3 scripts/benchmark_retrieval.py --json` to catch precision drift.
2. **New query type addition**: When Shadow hits a new query pattern (e.g., domain-specific), add to TEST_QUERIES and re-benchmark.
3. **Salience decay tuning**: If hybrid ranking feels stale, adjust `_HALF_LIFE_DAYS` (line 37) and re-benchmark.

---

## Behavioral Rules (Contract-Enforced)

### When to Use Grep / Exact Retrieval

**Trigger:** User query contains:
- Explicit file path patterns (`"src/"`, `"scripts/"`, `".py"`, `".md"`)
- Symbol lookups (`"find function X"`, `"where is class Y"`, `"grep for pattern Z"`)
- Exact string matching (`"search for literal 'auth_token'"`)
- Project/repo structure queries (`"what files exist in"`, `"list modules"`)

**Action:** Use Glob or Grep exclusively. Do NOT fall back to semantic search.

**Why:** Exact match has zero ambiguity. Semantic search adds latency, cost, and false positives on queries where BM25 is deterministic.

### When to Use Semantic Search

**Trigger:** User query is:
- Open-ended intent (`"how should we handle user corrections"`, `"what's our approach to auth"`)
- Cross-concept reasoning (`"relate authentication to the onboarding flow"`)
- Fuzzy topic matching (`"find anything about handling failures"`)
- No file path or exact symbol named

**Action:** Use web search or semantic retrieval tools.

**Why:** Fuzzy intent requires learned representations. BM25 will miss cross-domain connections.

### Fallback Strategy

1. **Query classification:** User intent is exact-match or open-ended?
2. **Try grep-first:** If exact-match type, run Glob/Grep and return result
3. **Semantic fallback:** If grep returns zero results AND query is amenable (not file-path), retry with semantic search
4. **Block uncertain routing:** Do NOT propose "I could use X or Y" — choose based on this rule, execute

This prevents FM-011 hedging ("here are two approaches") by making the tool choice deterministic.

## Related Contracts

- **FM-002** (VerifyBeforePush): Deterministic pattern matching for verification signals
- **FM-011** (ActionDeferralGuard): Regex-based behavioral boundary
- **FM-011** (RetrievalStrategyContract): Route tool calls by query type (grep → semantic fallback)
- **FM-033** (PatternerStop): Bounded evaluation against explicit stops

All validate the "explicit > similarity-scored" principle.
