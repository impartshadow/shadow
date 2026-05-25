# state-io-consolidation-guard

**Type:** Pre-check (code-enforced, blocking)
**Failure mode:** FM-004 (state/client route drift)
**Trigger:** Write/Edit that adds ad hoc JSON or JSONL writes targeting `state/`

**Precondition:** Persistent state reads/writes should use `core.state_io` helpers so atomic writes, JSONL locking, and parse-failure behavior stay centralized.

**Enforcement:** `core/contracts.py:StateIoConsolidationGuard.check_pre()` blocks direct `json.dump`, `write_text(json.dumps(...))`, and append-style `json.dumps` writes when the edited content targets `state/`.

**Recovery:** Replace direct file writes with `load_json`, `save_json`, `load_jsonl`, `append_jsonl`, or `save_jsonl` from `core.state_io`.

**Escalation:** Tests may write fixtures directly. Runtime code should not bypass `core.state_io` without an explicit durability reason.
