# subtask-threshold-guard

**Type:** Post-session audit rule  
**Failure mode:** FM-022  
**Enforcement:** harness (session_audit.py _post_to_log)

## Trigger
After each session audit, any individual FM score < 6 while the overall grade is B or above.

## Precondition
Overall grade is A or B (composite looks fine) but at least one FM scores ≤ 5/10.

## Enforcement
Session audit posts an additional `⚠️ SUBTASK BELOW THRESHOLD` alert to `#shadow-log` listing the specific FM, its score, and description. Does not downgrade the overall grade — reports alongside it.

## Why it matters
A composite B grade can hide a single FM firing at 4/10. The AssetOpsBench retrospective showed that execution-level scores inversely correlated with composite rankings (r=−0.13) — meaning good overall scores actively obscured specific failure modes. Per-FM threshold alerting is the mitigation.

## Recovery
1. Check `state/trace.jsonl` for that FM's recent firings.
2. If FM appears ≥ 3 times in the last session, add to improvement backlog with priority `high`.
3. Do not wait for a D/F grade to trigger investigation.

## Escalation
If the same FM scores < 6 in three consecutive audits while overall grade stays B+, surface to the user as a structural blind spot in the grading rubric.
