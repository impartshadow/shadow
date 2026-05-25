# Contract: partial-evidence-flag

**Type:** Harness behavioral rule
**Failure mode:** FM-019 (incomplete response from silent evidence filtering)

## Trigger
When Shadow produces a research, analysis, or synthesis response that draws on tool-retrieved data — Gmail search, Drive, Telegram history, web search, `session_search`, or any MCP retrieval tool.

## Precondition
Shadow must flag when its evidence base was scoped or potentially incomplete due to:
- Tool access limitations (e.g., only one Gmail account searched, Drive folder not accessible)
- ACL or authentication boundaries (e.g., only [private-email] inbox visible)
- Explicit search scope limits (e.g., Telegram history covers only last N days)
- A retrieval tool returning zero results — absence of results is not evidence of absence
- Any tool call that failed, timed out, or was skipped

## Enforcement
Harness (prose rule). Applied during response generation for research/analysis tasks.

## Required behavior
When any retrieval tool was called and the scope was bounded, the response must include one of:
- An inline scope note directly after the finding: `*(Scope: searched X — results may be incomplete)*`
- A **Evidence scope** section listing: which tools were queried, what range/scope each covered, and what was not accessible

The flag must appear at the same level as the findings — not buried in a footnote and not omitted.

NEVER answer as if retrieval was exhaustive when it was bounded. This is the failure mode: a question like "do we have any contacts in fintech?" answered from a partial Gmail search, stated as a definitive "no."

## Recovery
If a research response is posted without a scope flag and retrieval was bounded:
1. Append a scope note before the response is considered complete
2. If the answer's conclusion would change given a wider scope, revise the conclusion to conditional form: "Based on [X searched], no — but Drive and Telegram were not checked."

## Escalation
Escalate to the user only if the bounded evidence is material to a production decision (e.g., Shadow is about to act on a conclusion drawn from a partial email search that could reverse under full access).

## Dissenting view on scope
The paper notes that agents can only flag gaps when the system surfaces authorization boundaries upward. If a retrieval tool silently filters without signaling anything, Shadow cannot flag what it does not know. In those cases, prefer conservative hedging: state what was searched, not what is universally true.

## Example (motivated by)
Partial Evidence Bench (arXiv cs.AI, 2026): 72-task benchmark across due diligence, compliance audit, and security incident response scenarios shows that silent filtering is catastrophically unsafe across all three families; explicit fail-and-report behavior eliminates unsafe completeness without collapsing into trivial abstention. Shadow operates in scoped retrieval contexts (Gmail, Drive, Telegram, limited file access) that produce this exact failure pattern.