---
name: superseded-memory-append
description: When updating a memory file to reflect a reversed or corrected decision, append the prior claim under a ## Superseded section instead of overwriting it, so future sessions can see what was tried and walked back.
type: skill
---

# Superseded Memory Append

## When this applies

Any time you edit a file under `/home/agentshadow/.claude/projects/-home-agentshadow-shadow/memory/` where the change *reverses*, *corrects*, or *contradicts* a prior claim in the same file. This includes:

- Feedback memories where the user's guidance changed (e.g. "do X" → "actually don't do X").
- Project memories where a decision was rolled back (e.g. "we're shipping via A" → "switched to B").
- Reference memories where a resource moved or a fact turned out wrong.
- User memories where a stated preference was corrected.

This does NOT apply to:

- Additive updates (new fact, no prior claim contradicted).
- Typo fixes, formatting, or index-only edits to `MEMORY.md`.
- Deletions of memories that were never load-bearing (dedup, noise removal).

## What to do

1. **Before editing**, capture the exact prior claim being reversed — the sentence(s) that will no longer be true.
2. **Write the new claim** at the top of the memory body as usual.
3. **Append a `## Superseded` section** at the bottom of the file (create it if it doesn't exist). Each entry:

```
## Superseded

- **YYYY-MM-DD** — <one-line prior claim, verbatim or tight paraphrase>. Reversed because: <one-line reason: incident, the user correction, verified wrong>.
```

4. Keep the frontmatter `description` field pointing at the *current* truth, not the superseded one — the index needs to route by what's live.

## Why append-only, not overwrite

Overwriting hides the walked-back path. Future sessions then re-propose the same failed approach because the memory system shows only the current answer, not the history of what was tried. Preserving the superseded claim with the reversal reason means the next time the same idea surfaces, Shadow sees "tried this on 2026-05-14, reversed because the user corrected: distribution before production" and doesn't repeat the loop.

## Bloat control

The obvious risk is `## Superseded` sections growing indefinitely and drowning the live claim. Two rules:

- Cap each file's Superseded section at the 5 most recent entries. When adding a 6th, drop the oldest.
- If a superseded entry is itself superseded (the reversal was reversed), collapse to the newest live claim + one Superseded line noting the flip-flop — don't stack three layers.

## Example

Before (file body):

```
Weekly digest cadence for #shadow-hq status.
```

After a the user correction to hourly:

```
Hourly digest cadence for #shadow-hq status; daily is a ceiling not a target.

## Superseded

- **2026-05-20** — Weekly digest cadence for #shadow-hq status. Reversed because: the user corrected — weekly rejected, hourly is correct cadence.
```
