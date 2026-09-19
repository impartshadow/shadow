# timeout-disclosure-gate

**Type:** Post-check (code-enforced, block severity, deterministic)
**Failure mode:** FM-034 (factual-output-error — answering from pre-probe state)
**Trigger:** Every response (`ctx.action == "respond"`)
**Class:** `TimeoutDisclosureGate` in `core/contracts.py`

**Complement to `timeout-claim-entailment-gate`.** That gate catches claims
that *cite* timed-out evidence. This one catches the inverse failure: an
operation timed out during the turn, nothing superseded it, and the outgoing
response never says so. The reader then gets a confident answer assembled from
whatever state predated the probe, with no signal that the authoritative check
never returned.

**Precondition — ALL must hold:**

1. At least one entry in `ctx.tool_call_results` is a timeout. A timeout is
   recognised *only* from structured result fields:
   - `result_status == "timeout"`, or
   - `exit_code == 124`, or
   - `error_type` in `{TimeoutExpired, TimeoutError, ReadTimeout, CommandTimeout}`.
   Result prose is never keyword-scanned — a command whose *output* contains
   the word "timeout" is not a timed-out command.
2. That timed-out call was not superseded. A call is superseded when a *later*
   entry with the same `tool` and byte-identical canonicalized `params`
   succeeded (`result_status` in `{completed, ok, success}`, or absent
   `result_status` with `exit_code == 0`). The retry, not the abandonment, is
   what the response is entitled to describe.
3. The response text contains no disclosure token matching
   `\btimed[\s_-]?out\b|\btime[\s_-]?outs?\b` (case-insensitive).

**Recovery:** Retry the timed-out call with a longer budget or a narrower
scope. If it still does not return, state in the response that the operation
timed out and name which fact is therefore unverified — do not answer from
pre-probe state as if the check had succeeded.

**Auto-recover:** Rather than dropping the response, the gate appends an
explicit disclosure line naming the timed-out tools.

**False-positive shape deliberately excluded:** a long-running command that
completes successfully but whose stdout mentions timeouts (e.g. a test log, a
`grep` over this very doc) does not trip the gate, because only structured
result fields are consulted.

**Tests:** `tests/test_contracts.py` — 7 cases covering fire, no-fire on
disclosure, no-fire on successful retry with identical params, fire on retry
with *different* params, and prose-mention immunity.
