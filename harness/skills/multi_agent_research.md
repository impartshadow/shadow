# Skill: Heterogeneous Multi-Agent Research (HMACE)

## Role sequence
Explorer -> [Quality Gate] -> Critic -> Curator

## Core insight
Heterogeneous multi-agent systems with specialized roles and collaborative evolution avoid premature convergence through diverse memory-guided exploration. This skill routes research tasks through three specialized agents instead of a single-pass LLM.

## Stage: Explorer
**Goal:** Generate candidate actions, heuristics, and hypotheses without judgment.
1. Receive research task or exploration prompt
2. Generate 3-5 diverse candidate approaches/solutions (favor novelty over consensus)
3. For each candidate, state assumptions and potential failure modes
4. Assign a `confidence` score (0.5–0.9) to each candidate based on approach clarity
5. Return candidates as structured list with confidence signals

## Quality Gate (between Explorer and Critic)
**Goal:** Halt iteration early when Explorer output is already high-quality; reserve Critic for ambiguous or low-confidence output.

- Compute `avg_confidence` across Explorer candidates
- If `avg_confidence >= 0.8` AND no candidate lists more than one critical failure mode: **skip Critic entirely** — pass candidates directly to Curator, logging `critic_skipped: true`
- If `avg_confidence < 0.8` OR any candidate flags a critical failure mode: **run full Critic pass**
- Log the gate decision in `state/heterogeneous_panel_log.jsonl` under `quality_gate_fired`

This implements the paper's finding that the strongest-model call (Critic) should be used for <25% of passes — only when Explorer output is genuinely uncertain.

## Stage: Critic
**Goal:** Evaluate candidates against system contracts and identify flaws.
1. Receive Explorer's candidates
2. For each candidate, check against `contracts.py` failure modes (FM-001 through FM-033)
3. Flag which candidates would violate contracts and why
4. Score each candidate on: feasibility, alignment with Standing Decisions, convergence risk (are all candidates the same?)
5. Return critique with severity levels
6. **Stance audit (Belief Engine pattern):** For each candidate where Critic changes the stance from Explorer (accept→reject or vice versa), emit a `STANCE_CHANGE` line with: `candidate_id`, `direction` (accept/reject), `reason_type` (evidence|contract_violation|prior_drift), and a one-sentence `extracted_argument`. This makes stance changes auditable — if `reason_type` is `prior_drift` on >50% of changes, flag convergence risk.

## Stage: Curator
**Goal:** Maintain session_handoff.md and merge diverse outcomes into memory.
1. Receive Critic's evaluation (or direct Explorer output if gate fired)
2. Pick the highest-scoring candidate that passes contract checks
3. If all candidates converge on the same action: flag as convergence risk (trigger heterogeneous-panel-guard)
4. Log outcome to memory/heterogeneous_panel_log.jsonl with: task_id, explorer_count, critic_verdict, selected_action, outcome, critic_skipped, stance_change_summary (count of evidence-driven vs prior-drift changes from Critic's STANCE_CHANGE lines)
5. Merge outcome into memory/session_handoff.md under "Done this session"

## Contracts referenced
- All contracts from `contracts.py` (Critic validates against them)
- `heterogeneous-panel-guard` — detect 3+ identical outcomes across sessions

## Orchestration (in claude_client.py)
```python
run_heterogeneous_panel(task: str, system: str = "") -> dict:
    # Explorer: generate candidates (Haiku call, cost-optimized)
    # Quality gate: skip Critic if avg_confidence >= 0.8 and no critical failure modes
    # Critic: evaluate candidates (Haiku call) — only when gate does not fire
    #   Critic must emit STANCE_CHANGE lines for any accept<->reject flip
    # Curator: merge outcome into memory (Sonnet call for synthesis)
    #   Curator logs stance_change_summary to heterogeneous_panel_log.jsonl
    # Net cost: ~1.3x single-pass when gate fires, ~2x when full Critic runs
```
