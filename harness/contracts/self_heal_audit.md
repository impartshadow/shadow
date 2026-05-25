# Contract: self-heal-audit

**Type:** Behavioral (harness-enforced)
**Failure mode:** FM-003 (loop / symptom-only healing)

## Trigger

Any time repair.py or the watchdog autonomously applies a fix to a running system.

## Precondition

Before committing a repair, the repair agent MUST record:
1. **Symptom observed** — the exact error or log line that triggered the repair
2. **Prior occurrences** — how many times this same symptom appeared in `state/contract_violations.jsonl` or journalctl before this fix
3. **Root-cause hypothesis** — one sentence: why this symptom is occurring (not just what to patch)
4. **Fix applied** — what changed (file, line, diff summary)

This record goes into `state/repair_audit.jsonl` as a single JSON line.

## Enforcement

Harness: repair.py REPAIR_PROMPT includes the audit step. Code: `core/deficiency_tracker.py` `record_autonomous_heal()` writes the entry.

## Recovery

If the same symptom recurs within 7 days of a prior fix, escalate to the user rather than auto-healing again — this signals symptom-only healing.

## Escalation

Surface to the user when: same symptom healed 3+ times without a durable fix. Post summary to #shadow-log with prior heal dates.
