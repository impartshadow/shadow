# Contract: monitor-exoneration-evidence

**Type:** Code-enforced post-check (warn severity)
**Failure mode:** FM-014 (self-referential-monitor sub-case of completion integrity)
**Location:** `core/contracts.py` → `class MonitorExonerationEvidenceGuard`

## Trigger

A response declares a monitor's own alert/finding a false positive (misleading,
misclassified, retired, healthy, working as intended, inflated, stale) AND the
same turn changes that monitor's judgment/reporting layer, AND no same-turn
independent check of the *monitored condition* is present.

## Precondition

All of:

1. **Exoneration verdict** — `_EXONERATION_RE` ("false positive", "misleading",
   "misclassified", "not actually broken", "working as intended", "is healthy /
   retired / stale", "inflating old failure durations").
2. **Monitoring subject** — `_MONITOR_SUBJECT_RE` (monitor, alert, audit, cron,
   nightly, briefing, probe, finding, flag, classification, reporting).
3. **Monitor-layer change this turn** — an edited file matching
   `_MONITOR_FILE_RE` (`*_monitor.py`, `cron_health*`, `briefing.py`,
   `nightly.py`, `*_audit.py`, `*_receipts.py`, `alert*.py`) OR reporting-fix
   vocabulary (`_REPORTING_FIX_RE`: "fixed the reporting", "corrected those
   classifications", "reclassified", "stopped inflating/alerting", "routed the
   alerts to …", "suppressed/excluded … findings").
4. **No independent condition evidence** — neither in-text
   (`_INDEPENDENT_EVIDENCE_RE`: "re-ran the audit", "checked each finding",
   "confirmed against live state", "verified independently", "underlying
   findings resolved", "fixed it at source") nor a same-turn tool call matching
   `_CONDITION_PROBE_RE` (`audit_loop_runtime`, `loop_runtime_receipts`,
   `check_consecutive_failures`, `curl`, `requests.get`, `gh api`, `--probe`).

## Carve-outs (don't fire)

- Explicit hedge (`_HEDGE_RE`) — "not verified", "haven't confirmed", "findings
  remain open", "requires fresh evidence". The verdict is already tentative.
- No monitor-layer change — exoneration prose alone is a different class.
- No exoneration verdict — an ordinary monitor bug fix is grounded by its tests.
- `ctx.action != "respond"`.

## Enforcement

Warn. Some monitored conditions genuinely cannot be exercised in-turn (the next
scheduled run is their only producer); the correct posture there is the hedge,
not a blocked response. Warn writes to `state/contract_violations.jsonl` so
`scripts/session_audit.py` and the gap-closer can loop on the class.

## Recovery

Run the monitored condition itself in the same turn — re-run the audit
(`core.loop_runtime_receipts.audit_loop_runtime()`), the live credential probe,
or the phase's current wiring — and report each flagged finding's live status.
Prove retirement or health from live source/receipts. If it can't be exercised
this turn, say so and keep the findings open instead of reclassifying them.

## Related contracts

- `classifier-fix-repro-guard` (FM-027) — same shape for *externally*-triggered
  classifiers/rate limits. This guard covers Shadow's internal monitors, which
  that guard's external-trigger vocabulary excludes.
- `completion-artifact` / `post-commit-audit` (FM-027) — accept unit-test-green,
  which is exactly the off-target evidence in this class.
- `state-assertion-grounding` (FM-014) — a turn that reads the *monitor's*
  sources is grounded by its measure while the monitored condition stays unread.

## Origin

2026-09-12 `#shadow-hq`. The briefing reported several cron jobs "broken for
30–56 days straight". the user asked what they were, then "Can you figure it out".
Shadow reclassified all three findings as reporting artifacts, shipped
`5c46b06d` (retired-phase suppression, observed-span instead of elapsed age,
alerts rerouted to `#shadow-log`) and reported "Found the causes and fixed the
reporting. 27 tests passed." The 27 tests proved the reporting change worked.
The loop audit's three findings were never checked against live state and
reproduced verbatim on 2026-09-13 (`echo`, `brief-production`, `tenant-ops`
sharing one bulk stamp).

The upstream mechanism this guard changes: when the alerting system exonerates
itself, the exoneration now needs evidence from outside the alerting system.
