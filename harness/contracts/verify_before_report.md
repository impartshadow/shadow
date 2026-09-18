# verify-before-report

**Type:** Runtime contract (`check_post`, severity `warn`)
**Failure mode:** FM-034 (factual output error — a status claim emitted from a proxy signal)
**Implementation:** `core/contracts.py:VerifyBeforeReportGuard`, claim extraction in `core/status_claims.py`

**Precondition:** Any status claim Shadow volunteers — a count (`139 briefs queued`), a balance (`$47 confirmed`), or a verdict (`the channel is dark`, `the credential expired`) — must be carried by something this turn actually read.

**Enforcement:** On every `respond`, `core.status_claims.extract_status_claims()` pulls the definitive status claims out of the response (fenced code, inline code and quoted lines are excluded; a hedged response yields no claims). Each claim's value is then looked for in the turn's haystack: every `tool_call_results` result body, every tool param, `verification_output`, and the user's own message. Quantity and money claims match on normalised digits (`1,240` ≡ `1240`); verdict claims match on the verdict word. Anything left unmatched is a violation.

**Why it is not gated on a question.** `state-assertion-grounding` fires only when the user asks a factual question and the answer had zero reads. The FM-034 instances that recur are *unprompted*: a status line in a digest or a progress report where nobody asked and the number came from context. This guard is also value-level, not read-level — a turn that ran ten tools and still reported a remembered number is exactly the failure, and the read-level guard passes it.

**Relationship to the static sieve.** `scripts/proxy_signal_audit.py` closes the same failure class one layer down: no *function* in `scripts/`/`core/` may build a verdict or a quantity out of file mtime, a single log line, or a cached snapshot. That audit only sees code Shadow wrote to disk. This contract covers the larger surface — what Shadow says.

**Recovery:** Re-read the state being reported in the same turn and report what the read returned. If the number genuinely comes from an earlier read, mark the provenance inline ("as of this morning's digest") rather than asserting it as current.

**Severity rationale:** `warn`, not `block`. A value missing from the turn's output is suspect, not proven wrong — it may come from a read two turns ago, which is still the provenance the discipline asks to make explicit.

**Escalation:** None. False positives are absorbed by hedging the claim (which is the desired behaviour) or by narrowing `_QUANTITY_NOUNS` / `_VERDICT_WORDS` in `core/status_claims.py`.
