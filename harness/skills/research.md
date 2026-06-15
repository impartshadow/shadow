# Skill: research

## Role sequence
Triage -> Execute -> Verify

## Stage: Triage
1. Identify the source (URL, topic, named content)
2. If named content (episode, article), web search for it — don't ask the user for URL
3. Route: `mcp__shadow__browse_url` for pages, `mcp__shadow__web_search` for lookups
4. **Site depth check**: if the target site has 3+ levels of nesting (arXiv, Wikipedia, docs, research databases), run structure map first (see Execute step 1b)
5. **Spec-type detection**: if the source is a specification (paper methods section, PR description, design doc, Slack thread with a task), flag it as a spec-input and run spec-gap analysis in Execute step 1c
6. **Mode classification** (set before Execute, influences any downstream Claude sub-calls):
   - `quick-lookup`: single-answer retrieval, no synthesis — use conciseness-forcing prompt prefix on any Claude call; no extended reasoning budget
   - `deep-dive`: synthesis, cross-source verification, spec analysis, adversarial disconfirmation — allow full reasoning budget; skip conciseness prefix
   - Default to `deep-dive` when the task involves 1d/1e/1f steps or the user used "dd" shorthand

## Stage: Execute
1. Fetch content via MCP tools (NEVER WebFetch or WebSearch)
   **1a. Long-document pre-filter (>4000 chars returned):** Before full analysis, identify and extract the sections relevant to the research query (abstract, methods, results, conclusion for papers; thread OP + direct replies for Discord; first + last paragraphs for articles). Pass the extracted sections to analysis, not the full document. Only fall back to full-document analysis if sectioning loses the signal.
   **1a-cite. Multi-hop citation requirement (all deep-dive tasks):** Each reasoning hop must cite at least one retrieved fact before the next hop is allowed. Structure as: [Hop N: Assertion] → [Retrieved fact: ...] → [Next assertion]. Free-form reasoning without cited intermediate facts is not permitted. Tag each hop's source with `[SOURCE: url/title]` so the chain is fully auditable.
   **1b. Structure-aware navigation (complex sites only):** Before sequential crawl, attempt to fetch `<root>/sitemap.xml` or read OpenGraph/breadcrumb metadata from the root page. Build a relevance-ranked URL list; prioritize URLs whose paths match the research query before falling back to sequential discovery. Skip branches already confirmed empty this session.
   **1c. Spec-gap analysis (spec-input only):** Before proceeding with the substantive work, enumerate what the spec does NOT specify. For each gap: (a) state the assumed default explicitly, (b) mark it `[ASSUMED]` in the output. This list must appear at the top of the response before any findings. Omit this step for non-spec sources (news articles, reference pages, etc.).
   **1d. Adversarial disconfirmation (deep-dive and research tasks):** Before synthesizing findings, explicitly run the adversarial test: (a) State the central claim in one sentence. (b) Generate the strongest plausible counter-evidence scenario — what data pattern, study result, or source would falsify this claim? (c) Search for that counter-evidence first. (d) If disconfirming evidence is found, it must appear in the output BEFORE supporting evidence, not after. If none is found after genuine search, record it as a `[TESTED: no disconfirm found]` note. Skip 1d only for quick factual lookups (single-answer retrieval with no synthesis step).
   **1e. Dual-path retrieval (deep-dive tasks only):** Before synthesizing, run two targeted retrieval passes and select the better-grounded one:
   - **Fact-anchor pass**: retrieve sources that directly support or cite verifiable claims (statistics, named studies, primary sources). Tag retrieved items `[FACT]`.
   - **Conclusion-anchor pass**: retrieve sources that argue for OR against the candidate conclusion. Tag retrieved items `[FOR]` or `[AGAINST]`.
   - **Judge selection**: compare the two passes — whichever yields more independently-sourced, non-circular evidence is the primary retrieval path for synthesis. If both are thin (fewer than 2 independent sources each), mark synthesis as `[LOW-RETRIEVAL]` and proceed with explicit uncertainty. Skip 1e for quick lookups and spec-gap tasks.
   **1f. Shared-scratchpad for parallel agent forks (multi-agent deep-dive only):** When this research task spawns two or more parallel Agent subagents: (a) Before launching agents, write a scratchpad file at `state/research_scratch.json` with `{"topic": <topic>, "started": <iso_ts>, "agents": {}}`. (b) Instruct each agent to append its key intermediate findings (not full output) under a keyed entry in `state/research_scratch.json` before returning. Also instruct each agent on its tool allowlist (see `agent_invocation_scope` contract). (c) After all agents return, **run a consolidator pass before synthesis**: read the full scratchpad; for each agent's entry, compress it to max 5 bullet points preserving claims, sources, and confidence signals; write the compressed version back to `state/research_scratch_consolidated.json`. This prevents context saturation at the synthesis (reporter) layer — do not pass raw agent outputs directly to synthesis. (d) From `state/research_scratch_consolidated.json`, detect redundant coverage (drop duplicate threads, marking them `[DEDUPLICATED]`) and conflicting findings (flag explicitly before synthesis). (e) Delete both `state/research_scratch.json` and `state/research_scratch_consolidated.json` after synthesis is complete. (f) **Graceful degradation**: if any agent returns an error or empty output, log `[AGENT-DROPOUT: <agent_key>]` in the scratchpad but continue — partial answers from remaining agents are preferable to aborting synthesis. Flag the gap explicitly in the final output. (g) **Role-fidelity check (adversarial agents only):** If any agent was given an explicit opposing directive ('argue against', 'steelman opposing', 'red-team', 'devil's advocate', 'critique'), before aggregating its output, verify that its conclusion diverges from the input claim. If the agent's conclusion agrees with or restates the input claim (polarity match), log it as `[ERO-DETECTED: role override]` in the scratchpad and either retry with a stronger stance anchor in the prompt or flag that position as `[UNVERIFIED-OPPOSITION]` in synthesis. Never silently incorporate a same-polarity response as genuine opposition. Skip 1f for single-agent research or quick lookups. (h) **Adjudicator stance (conflicting findings only):** When step (d) detects conflicting findings between agents, explicitly declare the adjudicator stance before synthesis — never leave it implicit. Use `epistemic-rigor` stance for deep-dive synthesis: surface all conflicts, require independent corroboration before resolving any disagreement, and tag any majority-only convergence `[MAJORITY-CONVERGENCE: not independently verified]`. Use `practical-bias` stance only for quick-lookup mode: accept majority consensus unless directly contradicted by a primary source. An undeclared stance silently defaults to majority-vote resolution, masking genuine disagreement in the output.
2. **Serial depth over parallel breadth**: Prefer iterative deepening — one thread at a time, follow each source to its conclusion before spawning a new query. Do NOT fan out into many parallel searches to cover more surface area; go deeper on fewer threads instead. Exception: when spawning parallel Agent subagents per step 1f, the shared scratchpad makes breadth safe — use it only in that context.
3. Follow sources and verify claims — not just a summary
4. Structure output: headline conclusion, key points, evidence, actionable takeaways (no summary-prefix preamble)
5. Show investigation path: inline narration OR "Path taken:" header

### AEI skepticism gates (run before accepting any tool output as ground truth)
- **Illusion check**: if 3+ search results share near-identical phrasing on a contested claim, flag as potential coordinated poisoning — do not accept as consensus
- **Maze check**: if the same factual question has been retrieved 2+ times and results contradict each other, STOP retrieval, flag contradiction explicitly, do not continue chasing resolution through more queries
- **Temporal anomaly**: if all sources on a topic cluster around a single date or single domain, treat as low-diversity signal — state this limitation
- **Circular reference**: if source A cites source B which cites source A, note the loop and do not treat it as independent corroboration
- **Specificity trap**: a claim that is highly specific (named location, named military unit, specific hardware, internal tool name, precise casualty/count figures) but absent from mainstream press should be flagged as "reportorial, not independently verified" — specificity is not a proxy for credibility; it can be a marker of unverifiable insider reporting or fabrication
- **Reasoning chain causality (CIR proxy)**: when a paper or tool output presents a model's reasoning chain as evidence of understanding or capability: (a) check whether CIR or SR metrics were measured — if only accuracy is reported, mark the reasoning quality claim `[UNVALIDATED: accuracy ≠ causal reasoning]`; (b) do NOT treat a correct conclusion as validation of the chain that preceded it; (c) for AI benchmark comparisons, note if the evaluation measures reasoning process vs. output-only accuracy
- **Benchmark saturation trap**: when a source cites an AI benchmark score (SWE-bench, HumanEval, MMLU, LiveCodeBench, etc.) as evidence of real-world capability or deployment readiness: (a) tag the claim `[BENCHMARK: score ≠ deployment reliability]`; (b) check whether top performers used test-time compute scaling or dataset-specific tricks — if so, note `[BENCHMARK-GAMED: test-time compute]`; (c) do NOT treat a high benchmark number as evidence the system handles ambiguous, real-world tasks at that rate. Benchmark saturation has historically preceded capability plateaus on real codebases by 12–18 months.

## Stage: Verify
1. Cross-check search results before presenting — no conflicting or stale data
2. If claims conflict, note the discrepancy explicitly
3. Flag uncertainty rather than guessing
4. If Illusion, Maze, or Specificity Trap signal fired during Execute, include a "Source quality note" in the output
5. **Assumption audit (spec-input only):** If spec-gap analysis ran in Execute 1c, re-check each `[ASSUMED]` item against any additional context discovered during research. Correct or confirm each assumption before final output.
6. **Falsification audit**: If step 1d ran, verify: (a) counter-evidence search was actually executed (not skipped), (b) any `[TESTED: no disconfirm found]` note is present if search returned empty, (c) disconfirming evidence found is NOT buried after supporting evidence. If any of these fail, revise before marking Done.
7. **Dual-path audit**: If step 1e ran, verify: (a) both passes were executed (not just one), (b) judge selection was explicitly stated, (c) any `[LOW-RETRIEVAL]` tag is present if both passes were thin. If skipped on a deep-dive task, re-run before marking Done.
8. **Scratchpad audit**: If step 1f ran, verify: (a) both `state/research_scratch.json` and `state/research_scratch_consolidated.json` were deleted after synthesis, (b) any conflicts flagged in the consolidated scratchpad appear explicitly in the output, (c) redundant threads dropped during synthesis are noted as `[DEDUPLICATED]`, (d) any `[ERO-DETECTED]` entry either resulted in a retry or appears as `[UNVERIFIED-OPPOSITION]` in synthesis — never silently folded into findings as genuine opposition, (e) any `[AGENT-DROPOUT]` entries are disclosed in the final output with the gap they leave, (f) adjudicator stance was declared before resolving any conflicting findings (if 1f step (h) applied).

## Contracts referenced
- `context_resolution` — check if the user already sent this via Telegram
- `research_epistemology` — citation and contradiction disclosure requirements
- `agent_invocation_scope` — tool allowlists required when spawning parallel specialist agents
- Tool routing: ALWAYS mcp__shadow__browse_url, NEVER WebFetch

## Output format
- Newsletter/article: full research-command-style analysis (follow sources, verify)
- Quick lookup: direct answer, cited
- Comparison: structured table
- Spec analysis: `[ASSUMED]` list first, then findings
- Deep dive with 1d: disconfirming evidence section appears before synthesis
- **Deep dive synthesis scaffold** (when 1e ran): structure the synthesis section as:
  1. **Claim** — the central claim in one sentence
  2. **Evidence** — findings from the selected retrieval path, tagged `[FACT]`/`[FOR]`/`[AGAINST]`
  3. **Gaps** — what retrieval could not confirm; mark each `[UNVERIFIED]`
  4. **Verdict** — bottom-line assessment with explicit confidence level (`[HIGH]`/`[MEDIUM]`/`[LOW]`)
  This replaces free-form synthesis paragraphs for deep-dive tasks and suppresses hedge-and-abstain non-answers.
