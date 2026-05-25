# Contract: verify-before-push

## Type
Pre-push gate — deterministic enforcement via `core/contracts.py`

## Trigger
Any response containing "Done." or "Pushed." or any `git push` command.

## Precondition
Response MUST contain a code block with verification command output matching
the fix type. Mental verification is not verification.

## Enforcement
**Code-enforced** in `core/contracts.py:VerifyBeforePush` — blocks push if no
verification output detected in the response context.

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

## Violation recovery
Remove "Done." claim, run the appropriate verification command, re-evaluate.
If verification fails, fix before pushing — never push unverified logic fixes.

## Escalation
If verification genuinely can't run (e.g. requires live Telegram), say so
explicitly: "Pushed — can't verify locally; watch the next run."
