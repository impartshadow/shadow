# Failure Mode Taxonomy

Named failure modes with automated recovery paths. Each mode maps to a
contract that should have caught it and a code-level guard where possible.

---

## FM-001: capability-denial
**Pattern:** Shadow says "I can't access X" without trying.
**Root cause:** Default to caution over action. LLM tendency to hedge.
**Contract:** `pre_denial_gate`
**Code guard:** `core/contracts.py:PreDenialGate` — scans response for denial phrases.
**Recovery:** Block the denial. Run the smoke test. Show the output. Then decide.
**Frequency:** Highest — corrected 5+ times across sessions.

## FM-002: unverified-push
**Pattern:** "Done." without running verification command.
**Root cause:** Mental verification feels like real verification. It isn't.
**Contract:** `verify_before_push`
**Code guard:** `core/contracts.py:VerifyBeforePush` — blocks push without output.
**Recovery:** Run verification. Paste output. Then push.

## FM-003: edit-loop
**Pattern:** 3+ commits to the same file without fixing the root cause.
**Root cause:** Fixing symptoms instead of reading the full context.
**Contract:** `loop_prevention`
**Code guard:** `core/loop_guard.py` — graduated escalation (warn -> prompt -> block).
**Recovery:** Re-read entire file. Trace logic. One fix, verified.

## FM-004: wrong-tool-route
**Pattern:** Using WebFetch/WebSearch instead of MCP equivalents.
**Root cause:** Default tool selection overrides learned preference.
**Contract:** `wrong_tool_route` + `capability_misroute`
**Code guard:** `core/contracts.py:WrongToolRoute` — blocks wrong tool calls.
`core/contracts.py:CapabilityMisroute` — scans response text for mentions of
WebFetch/WebSearch, permission requests, or claims that web fetching is blocked.
**Recovery:** Use `mcp__shadow__browse_url` / `mcp__shadow__web_search`. Never
mention WebFetch/WebSearch in response text. Never claim web access needs
permission — Shadow always has it via MCP.
**Frequency:** Corrected 7+ times — the most repeated correction.

### FM-004 sub-patterns (all caught by CapabilityMisroute)
- Mentioning WebFetch/WebSearch by name in response text
- "I need WebFetch permission" / "Could you grant WebFetch access"
- "It's being blocked" (without MCP tool error output)
- "Can't fetch/pull/grab the article/page" (without trying mcp__shadow__browse_url)
- Asking the user to grant permission for a capability Shadow already has

## FM-005: context-miss
**Pattern:** Asking the user to repeat something he sent via Telegram.
**Root cause:** Claude Code and Telegram bot are separate processes.
**Contract:** `context_resolution`
**Code guard:** Harness-side only. Could add a pre-response hook that checks
`state/recent_context.json` — future upgrade.
**Recovery:** Check state files before asking. Lookup order: recent_context ->
research_log -> history.

## FM-006: misunderstood-intent
**Pattern:** Shadow answers a different question than the user asked.
**Root cause:** Over-indexing on what Shadow was already doing vs. what the user
actually said. Especially: "how would you do X" = brainstorm, not retry.
**Contract:** Harness-side — read the thread.
**Code guard:** None. This requires semantic understanding.
**Recovery:** Re-read the exact words. Answer THAT question. Don't redirect.
**Frequency:** Corrected 3+ times in recent sessions.

## FM-007: lost-context
**Pattern:** Shadow forgets something decided earlier in the session or in
a recent session (e.g. conflating a rate limit on one endpoint with a
general API block).
**Root cause:** Context window pressure, compaction, or just not persisting
the decision.
**Contract:** `loop_prevention` (conversation loop tripwire)
**Code guard:** `record_decision` / `check_decisions` tools exist but
aren't always called.
**Recovery:** Check decision log. Update session handoff after every push.

## FM-008: premature-proposal
**Pattern:** Proposing an approach instead of executing it.
**Root cause:** Risk aversion. Defaulting to "shall I?" instead of doing.
**Contract:** Runtime skill (default to action).
**Code guard:** None — semantic.
**Recovery:** Just do it. Report what you did, not what you plan to do.

## FM-009: archive-without-preview
**Pattern:** Archiving emails without showing the user the list first.
**Root cause:** Treating auto-archive and interactive triage identically.
**Contract:** `archive_preview`
**Code guard:** `core/contracts.py:ArchivePreview` — blocks archive without preview.
**Recovery:** Show sender+subject list. Then proceed.

## FM-010: sycophantic-validation
**Pattern:** Praising the user's approach instead of evaluating it honestly.
**Root cause:** RLHF optimization for user satisfaction over truth.
**Contract:** None — this is a meta-pattern.
**Code guard:** None possible. Requires ongoing vigilance.
**Recovery:** Treat Claude praise as noise. Evaluate against outcomes.
Push back with one clear objection when the user is going down a bad path.

## FM-011: explain-instead-of-act
**Pattern:** Shadow proposes/architects instead of executing the action.
**Root cause:** Risk aversion. LLM tendency to describe what it would do rather than doing it.
**Contract:** `explain-instead-of-act`
**Code guard:** `core/contracts.py:ExplainInsteadOfAct` — detects 2+ proposal markers without execution evidence.
**Recovery:** Execute the action directly. Report what you did, not what you plan to do.
**Frequency:** 8+ deficiency entries in March-April 2026.

## FM-012: manual-instruction-guard
**Pattern:** Shadow gives the user manual UI instructions (click here, go to settings) instead of solving programmatically.
**Root cause:** Defaulting to explaining the manual path rather than attempting API/tool-based solutions.
**Contract:** `manual-instruction-guard`
**Code guard:** `core/contracts.py:ManualInstructionGuard` — detects 2+ manual navigation patterns without programmatic evidence.
**Recovery:** Attempt the action via API/browse_url first. Only give manual instructions if programmatic path fails.
**Frequency:** 5+ deficiency entries in April 2026 (Discord setup was the main offender).

## FM-013: topic-overrun
**Pattern:** Shadow continues a topic after the user signals closure (done/fine/good/set).
**Root cause:** Trying to be thorough when the user wants to move on.
**Contract:** `topic-overrun-guard`
**Code guard:** `core/contracts.py:TopicOverrunGuard` — detects closure acknowledgement followed by continuation.
**Recovery:** Drop the thread. If something is genuinely urgent, save it for later.
**Frequency:** 4+ deficiency entries in March-April 2026.

## FM-014: completion-integrity
**Pattern:** Shadow claims "done", "shipped", or "wired" while the same response acknowledges unresolved gaps (not done, still missing, not yet wired).
**Root cause:** Shadow commits code, leads with "shipped and wired", then lists gaps — making the user think the request was fully delivered when it wasn't.
**Contract:** `completion-integrity`
**Code guard:** `core/contracts.py:CompletionIntegrity` — detects strong completion claims co-occurring with 2+ gap acknowledgments. Exempt for audit/review responses.
**Recovery:** Remove the completion claim. Lead with what's actually done, list what's remaining. Don't signal done until it's done.
**Frequency:** 3+ incidents in April 2026 (memory system, briefing integration, L2 improvements).

### FM-004 — Wrong tool route / Web capability denial

**Contract:** `web-tool-guard` (replaces `wrong-tool-route` + `capability-misroute`)

**Trigger:** Any interaction involving web tool calls or response text mentioning web tools/access.

**Pre-check:** Blocks `WebFetch` / `WebSearch` tool calls — must use `mcp__shadow__browse_url` / `mcp__shadow__web_search`.

**Post-check (a):** Blocks any mention of `WebFetch` / `WebSearch` in response text.

**Post-check (b):** Blocks claims that web access is unavailable unless an MCP tool was actually attempted (`ctx.tool_calls` contains MCP tool, `smoke_test_ran` is True, or response contains MCP error evidence).

**Severity:** Block (all checks).

**Recovery:** Replace banned tool with MCP equivalent; remove banned tool names from text; attempt MCP tool before claiming inability.

### FM-015: unvalidated-memory-write

**Pattern:** Writing to `~/.claude/projects/.*/memory/` without verifying content accuracy, checking for duplicates, or confirming the memory meets type criteria.

**Root cause:** Memory path is outside project root but wasn't blocked by a dedicated contract, so it fell through to the warn tier — which doesn't prevent the write.

**Contract:** `memory-write-guard`

**Code guard:** `core/contracts.py:MemoryWriteGuard`

**Recovery:** Check MEMORY.md for duplicates. Verify content accuracy. Confirm memory type criteria. Then write.

### FM-011: explain-instead-of-act

**Pattern:** Shadow proposes/architects/gives-manual-instructions instead of executing.

**Sub-patterns:**
- (a) deferred-action — "would you like me to", "I can set up", "here's the approach"
- (b) manual-instruction — "go to settings", "click on X", "navigate to"

**Root cause:** Risk aversion. LLM tendency to describe rather than do.

**Contract:** `action-deferral-guard`

**Code guard:** `core/contracts.py:ActionDeferralGuard` — classifies tool calls as execution vs. reconnaissance; fires when 2+ proposal/instruction markers appear without execution evidence.

**Recovery:** Execute directly. Report what you did, not what you plan to do.

**Severity:** Block.

### FM-004 — Wrong Tool Route / Capability Misroute

**Code guard:** `WebToolGuardV2` (replaces `WebToolGuard`, `WrongToolRoute`, `CapabilityMisroute`)

**What it catches:**
- Pre-check: Tool calls to `WebFetch` or `WebSearch` (banned tools)
- Post-check (a): Response text mentioning `WebFetch`/`WebSearch` tool names
- Post-check (b): Response claiming web access is blocked/denied without attempting MCP tools

**Enforcement:** Escalating retry counter per session:
- 1st violation: standard correction naming the correct MCP tool
- 2nd violation: REPEAT VIOLATION with emphatic correction
- 3rd+ violation: FM-004 LOOP DETECTED — escalates to the user

**Correct tools:** `mcp__shadow__browse_url` (fetch), `mcp__shadow__web_search` (search)

**Exemptions:** MCP tool in `tool_calls`, smoke test ran, MCP error evidence in response, code blocks/meta-discussion text

**Severity:** `block` (all checks). Corrected 7+ times — soft signals don't work.

**Recovery:** See escalating table. Post-check (b) recovery directs to call MCP first. At count >= 3, appends escalation flag.

### FM-017 — Writes to paths outside project scope

**Contract:** `PathScopeGuard` (block), `DangerousPathGuard` (block on sensitive patterns)
**Trigger:** `Write`, `Edit`, or `write_file` to a path outside the allowlist.
**Detection:** `os.path.realpath` normalization, then allowlist check: project root (any file) and memory dir (.md only).
**Severity:** block — hard gate, write does not proceed.
**Recovery:** Move file into project directory or add path to `PathScopeGuard._ALLOWLIST`.
**History:** Originally warn-severity in `DangerousPathGuard`; escalated to block after repeated violations slipped through.

### FM-004 — Wrong tool routed

**Contract:** `web-tool-rewriter` (pre-check rewrite), `web-tool-guard` (pre+post block), `web-tool-guard-v2` (pre+post block with escalation)

**Recovery:** `WebToolRewriter` silently rewrites `WebFetch` → `mcp__shadow__browse_url` and `WebSearch` → `mcp__shadow__web_search` in-place before execution. Downstream guards serve as fallback if rewrite is bypassed.

### FM-011 — Action deferral: proposes or instructs instead of executing

**Contracts:** `ActionDeferralGuard` (multi-marker, threshold ≥ 2), `SingleDeferralGuard` (single hard Class A marker in short response)

**SingleDeferralGuard detail:**
Catches the most common FM-011 form — a short response (< 500 chars) with exactly one "offer to act" phrase (would you like me to, I can create, etc.) and zero execution tool calls. Architectural/soft patterns (here's the approach, steps:) remain at threshold 2 via `ActionDeferralGuard`.

**Exemptions:** discussion mode, hypothetical questions, blocker markers, past-tense execution, long responses, pure user questions without imperative verbs, read-only tool context with factual findings.

### FM-016 — Unauthorized email recipient

**Severity:** block  
**Contract:** `EmailRecipientBlockGuard` (`email-recipient-guard`)  
**Trigger:** `gmail_create_draft` (or any gmail send/draft/create tool) called with a `to` address not in the static allowlist or session allowlist.  
**Detection:** `email.utils.getaddresses()` extracts bare addresses from display-name and multi-recipient formats; each address is checked against `_KNOWN_RECIPIENTS` (static) and `_session_allowlist` (session-scoped).  
**Recovery:** Agent surfaces the blocked recipient to the user, calls `EmailRecipientBlockGuard.allow(addr)` if the user explicitly named the recipient, then retries the tool call.  
**Prevention:** Always check whether the recipient was explicitly named by the user before sending.

### FM-019: response-quality

**Description:** Response fails semantic quality checks — restates question without answering, asks for unnecessary clarification, or trails off without a completion signal.

**Contract:** `PostResponseEvaluator` (`post-response-evaluator`)

**Severity:** warn

**Sub-patterns:**
- (a) Restates the question ("if I understand correctly", "you're asking about") without leading with an answer
- (b) Asks for clarification when tools could resolve the ambiguity (searched nothing, asked the user to specify)
- (c) Long response trails off into a question without confirming task completion

**Recovery:** Lead with the answer or action. Signal completion explicitly. Use tools to resolve ambiguity before asking.

### FM-018: dropped-question-part

**Description:** Shadow understood and answered part of a multi-part message but silently dropped one or more other parts.

**Contract:** `MultiPartCoverageGuard` (`multi-part-coverage`)

**Severity:** warn

**Trigger:** User message contains 2+ distinct question/request parts (detected via question marks, numbered lists, conjunction splitters, or semicolons) and the response has <15% keyword coverage on one or more parts.

**Recovery:** Re-read the user's full message. Identify each distinct question or request. Address every part in your response.

**False positive mitigation:** Exemptions for short messages (<20 chars), terse responses (<50 chars), code dump inputs, discussion mode, single compound imperatives, and explicit deferrals.

### FM-015: Parameter-level misroute

**Contracts:** `GitPushTargetGuard`, `InputSanitizationGuard`

**Description:** Action targets the wrong destination due to malformed or unexpected parameters. Includes shell metacharacter artifacts (e.g. `2>/dev/null` parsed as a remote name) and pushes to non-allowed remotes.

**Detection:**
- `InputSanitizationGuard` (layer 0): Rejects structurally invalid remote names containing shell metacharacters. Rejects remotes not in allowlist at block severity.
- `GitPushTargetGuard` (layer 1): Validates branch protection and force-push rules.

**Recovery:** Reconstruct the git push command without shell redirects. Use `origin` unless the user explicitly confirms an alternative remote.

### FM-020 — Meta-work displacement

**Description:** Nightly autonomous session spent >50% of effort on harness/contract/meta changes with zero user-facing or capability-expanding artifacts.

**Contract:** `meta-work-auditor` (post-session audit, not pre/post response)

**Code guard:** `scripts/meta_work_auditor.py` — classifies changed files as meta vs. real work, flags sessions where meta_ratio > 0.5 and real_files == 0.

**Trigger:** Runs after every nightly autonomous session (Phase 1.6 in `nightly.py`).

**Severity:** warn — posts to #moonshot, injects guidance into next session's prompt.

**Recovery:** Next session's backlog prioritization should favor capability work over infrastructure. The displacement flag is logged to `state/meta_work_audit_log.jsonl` for trend tracking.

**History:** Identified after multiple nightly sessions drifted into self-improvement infrastructure (contracts, analytics, benchmarks) while moonshot projects stalled.

### FM-015 — Parameter-level misroute

**Layer-0 guard:** `ToolParamSanitizer` — structural input validation. Catches shell metacharacter artifacts in git args, truncated/malformed memory paths, and generic Bash arg injection before downstream contracts parse them.

**Layer-1 guard:** `InputSanitizationGuard` — remote allowlist + metacharacter validation (defense-in-depth, redundant with layer-0).

**Layer-2 guards:** `GitPushTargetGuard` (branch protection, force-push), `MemoryWriteGuard` (semantic memory validation on structurally valid writes).

**Detection:** Three checks — (A) git positional args validated against `^[a-zA-Z0-9_./:@-]+$` after redirect stripping, (B) memory filenames must be `[a-z0-9_]+.md` with valid frontmatter, (C) non-flag Bash tokens scanned for embedded shell operators outside quotes.

**Severity:** A=block, B=block, C=warn.

**Recovery:** Strip shell redirects and reconstruct git commands; fix memory filenames to lowercase_snake_case.md with required frontmatter; verify intentionality of embedded operators.

### FM-019: Response trails off without completion signal

**Contract:** `CompletionSignalEnforcer` (block), `PostResponseEvaluator` Checks 1-2 (warn)
**Trigger:** Response >= 150 chars ends with a question in the last 2 non-empty lines, no completion signal (`Done.`, `pushed`, `committed`, etc.) found anywhere in the response, and the question is not an opinion/preference query or an already-guarded deferral.
**Severity:** block (enforcer), warn (evaluator checks 1-2)
**Recovery:** Add a completion signal before follow-up questions. If the task is done, say "Done." then ask. If the task is NOT done, finish it — don't ask whether to finish it.
**Exemptions:** Short responses (< 150 chars), completion signal present, opinion questions (`thoughts?`, `make sense?`), `want me to` (handled by ActionDeferralGuard), numbered/bulleted option lists with choice questions.

### FM-001+FM-004 Compound: Web Denial with Unrelated Tool Calls

**Contract:** `WebDenialCompoundGuard` (`web-denial-compound-guard`)
**Severity:** block
**Primary FM:** FM-001 (denial without smoke test)
**Secondary FM:** FM-004 (wrong tool route)

**Description:** Response contains a web-access denial phrase, but the only tools called were non-web tools. PreDenialGate exempts this because tools were called. WebToolGuard may miss it because `_TOOL_DISCUSSION_RE` stripping removes the denial evidence. This compound guard catches the gap.

**Detection:** All three conditions must be true:
1. Response contains a `_WEB_DENIAL_PATTERNS` match (after stripping code blocks/meta-discussion)
2. `ctx.tool_calls` is non-empty
3. No MCP web tool (`mcp__shadow__browse_url`, `mcp__shadow__web_search`) is in `ctx.tool_calls`

**Exemptions:** Smoke test ran, MCP web tool called, MCP error evidence in response, denial in code blocks/meta-discussion.

**Recovery:** Call `mcp__shadow__browse_url` or `mcp__shadow__web_search` before claiming web access is unavailable. Only report failure if the MCP tool itself returns an error.

### FM-019(c): Completion signal missing — auto-rewrite

**Contract:** `CompletionSignalRewriter` (replaces `CompletionSignalEnforcer`)
**Severity:** block (auto-recovered via `auto_recover()`)
**Trigger:** `ctx.action == "respond"`, response >= 150 chars, last 2 lines contain trailing `?`, no completion signal in full text.
**Recovery:** Auto-rewrite: follow-up questions get `Done.` prepended; incomplete-task questions get stripped with continuation directive. Falls back to block if classification fails.

### FM-001+FM-004+FM-011 Compound (Web Denial Compound)

**What:** Response denies web access while calling unrelated tools and proposing
manual workarounds instead of executing.

**Guards:**
- `WebDenialCompoundGuard` — post-check, detection. Catches compound violation after generation.
- `WebDenialCompoundPreGuard` — pre-check, prevention. Injects mandatory web-access directive before generation to prevent the denial belief from forming.

**Why two guards:** The post-check guard detects correctly but its prose recovery
re-enters the same LLM distribution, producing identical compound violations in a
loop. The pre-check injector changes the distribution *before* generation — the
directive enters as a system-level constraint with higher authority than the model's
capability beliefs.

**Recovery:** Pre-guard auto-injects directive; post-guard blocks with explicit
correction. Defense in depth.

**Root cause:** PreDenialGate tool_calls exemption + WebToolGuard text stripping +
ActionDeferralGuard reconnaissance-tool exemption create a three-way gap.

## FM-021: fabricated-gap
**Pattern:** Shadow asserts that its own infrastructure is missing, needed, or should be built — without running Grep/Read/Glob/Bash to confirm the gap. Claims like "Shadow needs X", "there's no test for Y", "we should build Z" made from general agent-architecture intuition rather than ground truth.
**Root cause:** Pattern-matching against mental models of what a generic agent *ought* to have, without checking what Shadow actually has. Shadow has substantial existing infra (nightly self-audit, Bilevel pattern, /improve, memory decay, regression tests, contract enforcement) that keeps getting re-discovered as if new.
**Contract:** `fabricated-gap-guard`
**Code guard:** `core/contracts.py:FabricatedGapGuard` — detects gap claims + Shadow-infra vocabulary + absence of investigation tools this turn.
**Recovery:** Grep/read the repo before proposing. If gap exists, cite evidence. If not, retract the proposal.
**Frequency:** 4 of 5 proposed gaps in a single thread on 2026-04-18 turned out to be fabricated.

## FM-022: self-inconsistency
**Pattern:** Shadow produces a response that contradicts its own stated personality, voice rules, strengths/weaknesses, or recent explicit decisions — despite all that state being loaded into every system prompt.
**Root cause:** Self-model and decision log are injected as context but there's no enforcement pass that asks "does this response cohere with that context?" The persistence-of-self moonshot produced a detailed substrate without a coherence gate.
**Contract:** `self-consistency-check`
**Code guard:** `core/contracts.py:SelfConsistencyCheck` — post-response Haiku pass against self-model + last 8 decisions.
**Recovery:** Revise to align with stated identity, or explicitly acknowledge the deliberate shift.
**Frequency:** New — no baseline yet. Shipped 2026-04-18 as the "moonshot-shaped move" the user asked for live.

## FM-023: dox-leak
**Pattern:** Shadow transmits the user's personal identifiers (emails, handles, phone numbers, real name) OUT of the private the user<->Shadow conversation to third parties or public surfaces — cold emails to strangers, tweets, Mastodon posts, webhook / platform-registration POSTs (e.g. Moltbook), or file writes to publish-adjacent paths (`state/outbound_drafts/`, `shadow-public/`). Discord is a private 2-way channel and is NOT a dox surface.
**Root cause:** Identifiers sit in memory/user_will.md (loaded into every context) and in operational code (outbound_scout prompts hardcoded the principal's name + employer). Without an outbound-side gate, any content generator that's seen the context can echo those identifiers into external content.
**Contract:** `dox-guard`
**Code guard:** `core/contracts.py:DoxGuard` — pre-tool-call scan on outbound tool names (gmail/tweet/mastodon/webhook) and on write-tool calls whose target path is publish-adjacent. Severity: `block`. No auto-recover — blocked content must be regenerated cleanly.
**Scheduler path:** Scripts invoked directly by the scheduler (outbound_scout, echo_publish) bypass the contract pipeline. Those paths call `DoxGuard.scrub()` at the content boundary as a last-resort safety net.
**Recovery:** Rewrite outbound content without the identifier — role-based references only, principal stays unnamed.
**Origin:** 2026-04-18 live incident — Shadow's outbound_scout was about to cold-email strangers from [contact-redacted] with "I'm an AI agent built by [full name] in [city]" baked into the Haiku prompt. the user: "You were going to send my info out of our two-way conversation into the world." First-pass shipped a response-text guard; the user corrected the framing — response_text is inbounds-equivalent, check_pre on outbound tools is the whole point.

### FM-012 — Manual instruction guard (supplementary)

| Field | Value |
|---|---|
| **Contract** | `platform-action-precheck` |
| **Supplements** | `ManualInstructionGuard`, `ActionDeferralGuard` |
| **Pre-check** | Warn-severity steering signal when user message references a platform Shadow has tool access to |
| **Post-check** | Block-severity gate on 1+ Class B manual-instruction pattern without execution tool evidence; scoped per-sentence exemptions |
| **Gaps addressed** | Global exempt-pattern bypass in ManualInstructionGuard (lines 826-828); `total < 2` threshold in ActionDeferralGuard |
| **Recovery** | Pre: name the tool path. Post: rewrite with programmatic execution first |

### FM-019: Trailing off without completion
**Pattern:** A completed response closes with an open-ended offer or hedge phrase ("let me know if", "feel free to", "happy to adjust") instead of a definitive completion signal.
**Example:** `"The deployment is done. Let me know if you need any changes."`
**Contract:** `TrailingHedgeGuard` (check_post, block-severity)
**Detection:** Strips code blocks/blockquotes, splits into sentences, checks last 3 sentences against hedge phrase list. Exempt if genuine blocker signal present or brainstorm-mode phrasing detected.
**Recovery:** Strip the hedge sentence. End with `"Done."` if work is complete. If genuinely blocked, state the explicit blocker (`"Cannot proceed without X"`).

### FM-026 — Decision Verification

**Description:** High-stakes outbound action (push, PR, email, tweet) executed without a structured `[DECISION]` artifact documenting the action, basis, and rationale.

**Detection:** `DecisionVerificationContract` (warn, post-check); `DecisionArtifactGate` (block, pre-check — validates artifact presence, action field match, and basis length ≥ 20 chars).

**Recovery:** Emit `[DECISION] action=<action> basis=<≥20-char rationale>` in the response before the action fires. Explicit user authorization (`ok push`, `ship it`, `lgtm`) in the preceding user message exempts the check. Empty `response_text` (autonomous scripts) is also exempt.

**Escalation:** Surface to the user after 3 consecutive OUTCOME failures on the same action type (logged to `state/decision_outcomes.jsonl`).

## FM-025: stale-url-citation
**Pattern:** Shadow provides a URL that browse_url already confirmed is unavailable ("no longer available", "product not found", 404).
**Root cause:** URL extracted from the browse call input without validating the response content.
**Contract:** `StaleUrlGuard` (warn, post-check) — cross-references browse_url results against cited URLs.
**Recovery:** Do not cite URLs from failed browse results. Search for the current URL or acknowledge unavailability.

## FM-027: tool-auth-fallback-skipped
**Pattern:** Shadow surfaces an auth-failure message ("token expired", "needs re-auth") to the user without first attempting the shadow MCP fallback path.
**Root cause:** First tool fails → error surfaced immediately instead of routing to `mcp__shadow__run_shell` + `core.*`.
**Contract:** `ToolAuthFallbackGuard` (block, post-check) — fires when auth-failure language appears without shell fallback in tool_calls.
**Recovery:** Route to `mcp__shadow__run_shell` with the appropriate `core.*` module. Only escalate to the user if the fallback also fails.
**Note:** Specialized variant of FM-001. FM-001 catches "I can't access X" claims; FM-027 catches auth-failure surfacing specifically.

### FM-011 — Action Deferral

**Description:** Agent proposes or offers to act instead of executing. Manifests as "would you like me to", "I can X if you want", "shall I", "let me know if you'd like", or similar phrases with no tool execution this turn.

**Contracts:**
- `ActionDeferralGuard` (warn) — detects 2+ deferral/instruction markers
- `SingleDeferralGuard` (block) — catches single hard Class-A deferral phrases
- `ActionDeferralBlockGuard` (block) — compound check: any offer phrase + zero tool calls; tighter phrase set, explicit exemptions for brainstorm/question/how-would-you contexts. Supersedes warn-level contracts for blocking enforcement.
- `ExplainInsteadOfAct` (warn) — legacy; retained for logging signal
- `ManualInstructionGuard` (warn) — legacy; retained for logging signal

**Recovery:** Execute now — call the required tool(s) and return output. Do not offer, ask for confirmation, or list options.

**Escalation:** If the required tool is genuinely unavailable (capability gap), say so explicitly with evidence rather than offering.

| FM-015 | `MemoryIndexGuard` | Write/Edit to MEMORY.md containing body prose, frontmatter, or non-pointer lines | Block — structural corruption is not recoverable | Write content to a new `.md` memory file; add a single `- [file.md](file.md) — hook` pointer to MEMORY.md |

## FM-034: factual-output-error
**Pattern:** Shadow states something factually wrong — incorrect dates, wrong numbers, wrong names, incorrect claim about what a tool returned, or wrong state of the world.
**Rate:** 0.21/day (14d avg as of 2026-04-28). Ranked #4 FM by frequency.
**Root cause:** Over-confident assertion from memory without verification; stale data used as current; tool output misread.
**Code guard:** None. Requires fact-checking behavior at generation time — not contractable with post-hoc pattern matching.
**Harness guidance:** When making specific factual claims (numbers, dates, names, API outputs), hedge or verify. "verify-before-claiming" meta-principle applies.
**Recovery:** If the user says "that's wrong" — acknowledge without hedging, check the actual source, provide corrected value.
**Note:** Not the same as FM-001 (capability denial) or FM-006 (intent misread). FM-034 is specifically wrong *output content* when Shadow *tried* to answer correctly.

## FM-024: cross-modal-injection

**Pattern:** Malicious instructions injected into tool results (WebFetch, MCP, API responses) are passed downstream to other agents or into the reasoning pipeline without sanitization, potentially causing cascading reasoning failures across the multi-agent system.

**Root cause:** Tool results are treated as trusted data when they're actually user-controllable or attacker-injectable via web content, API responses, or intermediate agent outputs. Multi-modal pipelines amplify risk: injection in one modality propagates to all downstream consumers.

**Contract:** `ToolResultInjectionGuard` (warn, post-check) + `sanitize_tool_output()` (pre-check sanitizer)

**Code guard:** 
- `core/contracts.py:ToolResultInjectionGuard` — detects OWASP LLM02 patterns in tool results (role overrides, instruction prefixes, system-prompt injections)
- `core/claude_client.py:sanitize_tool_output()` — strips injection signatures before passing results to reasoning context

**Recovery:** (1) Post-check identifies suspicious patterns and warns. (2) Pre-check sanitization strips known patterns before downstream use. (3) If sanitization fails, escalate to the user.

**Severity:** warn (post-check), block (if critical patterns remain after sanitization).

**Source:** "Hierarchical Attacks for Multi-Modal Multi-Agent Reasoning" (arXiv:2605.13213) — demonstrates cascade failures when intermediate agents receive injected instructions.

**Frequency:** New — shipped 2026-05-15 as foundational guard for multi-agent safety.

## FM-035: premature-blocker
**Pattern:** Shadow tries one approach, fails, and declares the goal unsolvable — without reframing the goal abstractly or enumerating alternative mechanisms. Example: "headless Chromium is blocked by Google" → stops, rather than "I need to simulate a human login" → tries Xvfb + visible browser + stealth mode.
**Root cause:** Collapse of "this specific approach failed" into "this class of problem is unsolvable." Shadow stays one level of abstraction below the goal and reasons about approach variants instead of from the goal outward.
**Contract:** `PrematureBlockerContract` (warn, post-check, Haiku-judged)
**Code guard:** `core/contracts.py:PrematureBlockerContract` — Haiku judge: detects blocker-declaration language + absence of alternative-mechanism enumeration or goal reframe.
**Recovery:** Before surfacing any technical blocker as final: (1) restate the goal in abstract terms, (2) enumerate ≥2 mechanistically distinct approaches, (3) only escalate if all are exhausted.
**Escalation:** Surface to the user only after all enumerated paths fail.
**Origin:** 2026-05-02 — Upwork reauth blocked by Google bot detection. Shadow declared it unsolvable. the user pushed back: "I can't believe you can't solve this." Xvfb + patchright stealth solved it in one attempt. Root cause: Shadow framed it as "fix the Chromium flags" not "simulate a human login."
**Frequency:** New — no baseline. Suspected high given FM-001 frequency pattern.
