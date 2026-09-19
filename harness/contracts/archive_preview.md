# Contract: archive-preview

## Type
Pre-action gate — **not code-enforced** (prompt-level self-check)

## Trigger
Any call to `gmail_manage.py` archive function, or any response indicating
emails will be archived.

## Precondition
Before executing any archive action, a list of sender + subject for every
email in the queue MUST be shown to the user.

## Format
Flat bullet list: `- Sender Name: Subject line`

## Enforcement
**Not code-enforced.** No `ArchivePreview` class exists. The `preview_shown`
field on `ContractContext` was plumbed for this gate and is read by nothing.
**Status correction (2026-09-18):** this doc asserted code enforcement for a gate that does not exist in `core/contracts.py`. The rule is prompt-level only. Surfaced by `scripts/contract_law_registry.py`; promotion path is to implement the class, add it to `_ALL_CONTRACTS`, then restore the enforcement claim here.


## Exception
Automated preference-driven suppression (pre-configured by the user in
`data/preferences.json`) fires silently — no preview needed.

## Violation recovery
Show the preview list before proceeding. Never archive without it.
