# handoff-integrity-check

**Type:** Pre-check (code-enforced in `core/contracts.py`)
**Failure mode:** FM-022 (self-consistency)
**Status:** Tier 2 — pending implementation

## Trigger

Any tool call result that is passed as context to a subsequent downstream tool call within the same pipeline (e.g., brief fetch → brief enrich → brief publish stages).

## Precondition

Tool call results feeding into downstream context must:
1. Conform to the expected schema for that pipeline stage (required fields present, no null sentinels where live values expected)
2. Not contain fields from a prior session's handoff that were not refreshed this session

## Enforcement

`HandoffIntegrityCheck` in `core/contracts.py` — pre-check that validates `ContractContext.tool_call_results` against registered stage schemas before the next tool call is allowed.

## Recovery

On violation: block downstream tool call, log to `state/trace.jsonl`, surface field name and expected vs. actual type to Shadow.

## Escalation

If the same field fails validation 3+ times in a session, post to #shadow-log with schema diff.

## Schema registration

Pipeline stages register schemas via `register_handoff_schema(stage_name, required_fields)`.
Initial schemas:
- `brief_fetch`: `{"id": str, "title": str, "status": str}`
- `brief_enrich`: `{"id": str, "title": str, "body": str, "status": str}`
- `brief_publish`: `{"id": str, "substack_url": str}`
