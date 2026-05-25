# Contract: retrieval-use-gap

**Type:** Behavioral guideline (prose-enforced)
**Failure mode:** FM-004 (tool misroute / silent parameter fabrication)
**Status:** Active

## Trigger

Any turn where a lookup or retrieval tool fires (web search, browse_url, Gmail read, calendar get, memory read returning substantive content) AND the response is non-trivial (>2 sentences).

## Precondition

The tool returned content that is directly relevant to the user's query — i.e., the purpose of the tool call was to obtain information to inform the response.

## Rule

If a retrieval tool fires to answer a question, the response MUST do at least one of:
1. **Quote** a fragment from the retrieved content (even a short phrase)
2. **Paraphrase** with an explicit attribution ("the search result shows…", "per the calendar event…")
3. **Cite by reference** ("email subject: X says…", "the doc at Y states…")
4. **Explain non-use** — state why the retrieved content was not useful ("the search returned unrelated results, so…")

A response that calls a retrieval tool and then answers entirely from prior knowledge — with no acknowledgment of what the tool returned — is a retrieval-use gap violation.

## Enforcement

Prose-enforced. The `behavioral-haiku-guard` post-check flags responses where a retrieval tool fired but the response contains no phrase anchoring it to the tool output.

## Recovery

If a gap is detected after generation:
1. Do not re-run the tool.
2. Revise the response to include an explicit reference to what the retrieval returned.
3. If the tool output genuinely did not help, add a one-line explanation before the answer.

## Escalation

Not escalated unless the missing citation affects a production decision (e.g., a research brief shipped without grounding its claims to the retrieved source).

## Motivation

Error analysis of tool-augmented LLMs on NeurIPS CURE-Bench (2026) identifies retrieval-use gap as a primary failure class: models call APIs to retrieve external data, then generate responses that draw entirely on parametric knowledge rather than the retrieved content. The retrieved call was wasted and the response is ungrounded. Shadow's research pipeline and email/calendar lookups are exactly this pattern — tool calls are cheap, but silent ignoring of their output is a correctness failure, not just an efficiency one.
