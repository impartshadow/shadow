# Skill — Design Iteration

## When this activates
Any visual asset request: server icons, logos, banners, images, signatures, illustrations.
Feedback on a prior visual ("wrong diagonal", "too dark", "make it X") = design iteration.

## Design preference memory
Before generating ANY visual, read `state/design_preferences.json`. Apply stored prefs automatically — never ask about something already stored.

After the user confirms a design ("perfect", "love it", thumbs up, or just stops iterating):
- Write the preference delta to `state/design_preferences.json`
- Log what changed and why in the notes field

## Stage 1 — Load preferences
```python
import json
from pathlib import Path
prefs = json.loads(Path("state/design_preferences.json").read_text()) if Path("state/design_preferences.json").exists() else {}
```
Apply: color scheme, orientation, style, font, mood. If pref conflicts with explicit request, explicit request wins — then update the stored pref.

## Stage 2 — Generate variations (MANDATORY for new requests)
On any NEW design request (not an iteration fix), generate **10–15 variants** and upload the strongest one. Do NOT ask which to generate — pick and ship the best, mention 2-3 alt directions briefly.

On **iteration feedback** ("wrong diagonal", "too dark"): apply the fix + store the pref, upload immediately. One shot, no menu.

## Stage 3 — Store result
```python
# After confirmation or after iteration converges (the user stops giving feedback):
prefs["last_asset"] = {"name": asset_name, "file": saved_path}
prefs["<key>"] = <value>  # e.g. prefs["orientation"] = "bottom-left-to-upper-right"
Path("state/design_preferences.json").write_text(json.dumps(prefs, indent=2))
```

## Standing preferences (as of 2026-04-19)
These are loaded from `state/design_preferences.json`. Current state after Discord icon session:
- **orientation**: bottom-left to upper-right (diagonal rising)
- **color_scheme**: black and white
- **style**: noise-solidifying, wet ink, script/cursive font (Dancing Script)
- **mood**: emergent, not-quite-finished, signal-from-static
- **font_path**: `/tmp/dancing.ttf` (Dancing Script — re-download if missing)

## Contracts referenced
- `default-to-action`: generate, don't propose
- `completion-signal-enforcer`: say Done. after upload confirmed
