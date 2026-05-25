# Contract: browse-url-fallback

**Type:** Harness-enforced (warn severity)
**Failure mode:** FM-001 (denial without attempt)

## Trigger
Shadow calls `mcp__shadow__browse_url` and receives an empty body, HTTP error, bot-block, "no longer available" response, or a thin response (fewer than 50 words of prose content).

## Precondition
At least one alternative must be attempted before surfacing a miss to the user:
- Try an alternative URL for the same content (cached version, archive.org snapshot, related source, search result that covers the same content)
- OR explicitly state "tried [URL1], [URL2], both returned [error]" in the response

## Enforcement
Harness-side — no code gate. Applies in all research, email-link-fetch, and digest flows.

## Recovery
1. First browse_url miss: attempt 1 alternative source automatically
2. Second miss: surface as "[topic] unavailable via direct fetch — tried [url1], [url2]" and offer the user the option to retrieve manually
3. Never silently skip a failed fetch

## Utility post-check (thin response handling)
After a successful HTTP fetch, evaluate response utility before synthesizing:
- **Low-utility signal**: response body contains fewer than 50 words of prose (after stripping nav/boilerplate), or the text is dominated by cookie banners, login prompts, or paywall notices
- **Recovery for low-utility**: do NOT synthesize the thin content as if it were informative. Instead:
  1. Answer from prior knowledge or session context if the question is within knowledge boundary
  2. If knowledge boundary is insufficient, retry with an alternative source
  3. Surface to the user as "[URL] returned thin content — answered from training knowledge" if no alternative is available
- **Rationale**: synthesizing a 20-word paywalled snippet into a paragraph-length response produces confidently-worded but low-information output. It is better to acknowledge the fetch quality and fall back than to dress up thin content.

## Escalation
If both attempts fail and the content is time-sensitive (deadline, event, breaking news), surface immediately rather than deferring to digest.

## Motivation
ClawBench (arXiv 2504.08523) benchmarks browser AI agents on 144 live websites and finds a 33.3% task-completion ceiling even with frontier models. Environmental fragility — sites change, rate-limit, and block bots — drives most failures. Single-attempt fetches will miss roughly 2/3 of the time on live sites. Treating the first miss as authoritative causes Shadow to systematically under-report available information.

2026-05-05: "To Call or Not to Call" (arXiv cs.AI) decomposes tool-call quality into necessity, utility, and affordability. The utility dimension — whether the tool response actually helps — motivates the thin-response post-check above. Models that synthesize low-utility responses perform worse than models that fall back to prior knowledge on the same questions.
