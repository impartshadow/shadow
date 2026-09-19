# Contract: verify-before-push

## Type
Pre-push gate — **not code-enforced** (prompt-level self-check)

## Trigger
Any response containing "Done." or "Pushed." or any `git push` command.

## Precondition
Response MUST contain a code block with verification command output matching
the fix type. Mental verification is not verification.

## Enforcement
**Not code-enforced.** No `VerifyBeforePush` class exists in `core/contracts.py`.
It exists only in `shadow-kit/shadow_kit/contracts.py` (the extracted product).
A no-op `class VerifyBeforePush: pass` stub was committed to `core/contracts.py`
to satisfy `tests/test_contract_guard.py`, and was removed 2026-09-18.

Adjacent registered gates cover parts of this rule — `claim-verification`,
`execution-evidence-guard`, `commit-hash-verification` — but no gate implements
the pre-push verification-output precondition stated below.
**Status correction (2026-09-18):** this doc asserted code enforcement for a gate that does not exist in `core/contracts.py`. The rule is prompt-level only. Surfaced by `scripts/contract_law_registry.py`; promotion path is to implement the class, add it to `_ALL_CONTRACTS`, then restore the enforcement claim here.


## Verification commands by fix type

| Fix type | Verification command |
|---|---|
| Gmail query / filter logic | `python3 -c "from scripts.gmail_summary import _get_auto_archive_senders; print(_get_auto_archive_senders())"` |
| Auto-archive pattern logic | `python3 -c "from scripts.gmail_summary import _get_auto_archive_senders, _load_pattern_context; print(_get_auto_archive_senders()); print(_load_pattern_context())"` |
| Archive action (before executing) | `python3 scripts/gmail_manage.py --dry-run archive <msg_ids>` |
| Email preference / suppression | `python3 -c "from scripts.briefing import _apply_email_prefs; import json; prefs=json.load(open('data/preferences.json')); print('loaded', len(prefs.get('email',{}).get('senders',{})), 'sender prefs')"` |
| Briefing / task filter logic | `python3 -c "from scripts.briefing import _fetch_tasks; import pprint; pprint.pprint(_fetch_tasks())"` |
| Any new logic | `.venv/bin/python -m pytest tests/ -q` — must show 0 failures |
| Bot scripts / handlers | `python3 <script> --dry-run` or run in test mode |
| Commit says run/execute/ship a `.py` script | Spawn the process and paste its PID or exit code in the same response (enforced by `script-run-verification` in `core/contracts.py`) |

## Violation recovery
Remove "Done." claim, run the appropriate verification command, re-evaluate.
If verification fails, fix before pushing — never push unverified logic fixes.

## Escalation
If verification genuinely can't run (e.g. requires live Telegram), say so
explicitly: "Pushed — can't verify locally; watch the next run."
