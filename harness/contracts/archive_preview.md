# Contract: archive-preview

## Type
Pre-action gate — deterministic enforcement via `core/contracts.py`

## Trigger
Any call to `gmail_manage.py` archive function, or any response indicating
emails will be archived.

## Precondition
Before executing any archive action, a list of sender + subject for every
email in the queue MUST be shown to the user.

## Format
Flat bullet list: `- Sender Name: Subject line`

## Enforcement
**Code-enforced** in `core/contracts.py:ArchivePreview` — blocks archive
execution if no preview was shown in the current interaction.

## Exception
Automated preference-driven suppression (pre-configured by the user in
`data/preferences.json`) fires silently — no preview needed.

## Violation recovery
Show the preview list before proceeding. Never archive without it.
