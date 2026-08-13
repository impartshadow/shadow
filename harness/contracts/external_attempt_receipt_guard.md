# external-attempt-receipt-guard

**Type:** Code-enforced post-check (`core/contracts.py:ExternalAttemptReceiptGuard`)
**Failure mode:** FM-029.b — fabricated external fetch-attempt receipt
**Severity:** block

**Trigger:** Response text contains a first-person, present-turn attempt claim
(`I tried / retried / fetched / accessed / hit …`) naming an external object
(link, url, proxy, browser, page, site, endpoint, captcha, http) while the turn
contains no live-fetch tool call (browser_*, browse_url, run_shell, web_search,
bash/curl) and no captured verification output.

**Precondition:** Any external-attempt claim must have a same-turn tool receipt.

**Carve-outs (pass):**
- Negated non-attempts: "I haven't tried the link yet"
- Past-time recall: "Earlier today I tried … nothing has changed"
- Reported/retracted prior claims: "The Aug 8 receipt said I accessed … that claim was false"
- No external object: "I tried a simpler regex first"
- `verification_output` present on the context

**Recovery:** Run the actual fetch this turn and cite its output, or rewrite the
claim as a plan ("I will try…") / hedge it as unattempted.

**Escalation:** None — regenerate with a real receipt.

**Origin:** 2026-08-08 Dotloop class — a response fabricated "retried through
the home SOCKS proxy, 403 Press & Hold" with zero tool calls behind it.
Spec tests: `tests/test_external_attempt_receipt_guard.py`.
