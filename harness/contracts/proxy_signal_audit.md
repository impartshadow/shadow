# proxy-signal-audit

**Type:** Static analyzer + CI regression test (test-enforced)
**Failure mode:** FM-034 (factual errors: false "expired" / "stalled" / "blocked" alerts emitted from a proxy signal)
**Trigger:** `python3 scripts/proxy_signal_audit.py` (also run by `tests/test_proxy_signal_audit.py` as a regression gate)

**Precondition:** No function in `scripts/*` or `core/*` may emit a status verdict (`expired`, `stale`, `stalled`, `blocked`, `dead`, `missing`, `broken`, `down`, `failing`, `unhealthy`, ...) from a code path gated by file mtime without also calling a real validator (HTTP/subprocess/explicit verify).

**Enforcement:** AST scan in `scripts/proxy_signal_audit.py`. A finding requires:

1. The function reads file mtime (`os.path.getmtime` or `Path.stat().st_mtime`).
2. The mtime (or any variable derived from it through assignment chains) appears in the test of an enclosing `if` block.
3. That `if` block contains a return/yield whose value carries a verdict-word string.
4. The function does not call any real validator (`requests`, `httpx`, `urllib`, `subprocess`, `validator(...)`, `.verify(...)`, `live_check`, etc.).

The current findings count is pinned by the `BASELINE_FINDINGS` constant in `tests/test_proxy_signal_audit.py` (baseline 0 at introduction; `state/` is gitignored so the baseline rides with the test, not a JSON file). The `TestBaseline::test_audit_at_or_below_baseline` case fails the test suite if any new function regresses past the baseline.

**Recovery:** When the test surfaces a new finding, treat mtime as a *diagnostic log line*, not a verdict. Two patterns are canonical:

- Demote the mtime-only path to an advisory state (`stale_unverified`) that is deliberately not alertable — `scripts/credential_guardian.py` (8e1c988).
- Drop the mtime fallback entirely and let real auth failures surface at point-of-use as 401/403 — `scripts/echo_publish.py` (4013e29), `scripts/twitter_heartbeat.py` (this commit).

**Escalation:** None — the guard is structural. False positives are absorbed by adding a real-validator hint (network/subprocess call) or by allowlisting a path in `scripts/proxy_signal_audit.py:_ALLOWED` with a one-line written reason.

**Why this is a sieve, not a one-shot fix:** the failure class regenerates because every helper script with a freshness concern is tempted to read mtime first. This audit is run as a regression test on every push, so new instances of the pattern fail CI on the way in. The class is closed at the architectural level, not by chasing each instance after the user sees the false alarm.
