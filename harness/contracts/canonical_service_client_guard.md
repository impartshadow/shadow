# canonical-service-client-guard

**Type:** Pre-check (code-enforced, blocking)
**Failure mode:** FM-004 (duplicate service client)
**Trigger:** Write/Edit that adds a new Moltbook HTTP client or Twitter/X posting client outside the canonical modules

**Precondition:** External service integrations must reuse canonical client modules so auth, safety gates, and validation do not drift between paths.

**Enforcement:** `core/contracts.py:CanonicalServiceClientGuard.check_pre()` blocks duplicate Moltbook HTTP request logic and third Twitter/X client implementations.

**Recovery:** Use `core.moltbook_client` for Moltbook auth/base HTTP, `echo.twitter` / `echo.twitter_browser` for X posting, and `echo.twitter_common` for shared X validation.

**Escalation:** Add a new canonical client only when the existing module cannot represent the service boundary cleanly.
