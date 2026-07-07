# Contract: dead-source-citation-guard

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:DeadSourceCitationGuard`. Severity: `block`.

## Failure mode
FM-014 (read-a-stale-cache) — a response cites a `state/*.json(l)` file as
evidence for a current-state finding, but that file's writer is dead: the
file has not been written in >= 21 days, and the response never discloses
its age. The read happened, so every assert-from-memory guard passes; the
evidence itself is what's rotten.

## Origin
2026-07-07 Echo incident. Shadow read `state/echo_post_log.json` — 31
entries, all 2026-04-02→04-11, writer (`echo/crosspost.py`) retired three
months earlier — and presented it to the user as Echo's *current* platform
performance ("Every single Echo post is landing on Nostr only"). the user had to
catch it; Shadow retracted; six other consumers had been silently reading the
same dead file for three months. This is the exact blind spot named in
`state_assertion_grounding.md` ("The contract cannot catch
*read-the-wrong-source* ... or reads a stale cache").

## Trigger
All of:
1. Response cites one or more `state/<...>.json` / `.jsonl` paths (raw text
   scan — citations live inside backtick spans that
   `_strip_non_action_text` removes).
2. A cited file exists and its mtime is >= 21 days old.
3. The response contains no staleness disclosure anywhere (`stale`,
   `retired`, `abandoned`, `last updated/entry`, `as of 20XX`,
   `N days/weeks/months old`, `snapshot`, `historical`, ...).

## Pass conditions
- All cited state files fresh (< 21 days), or
- the response discloses the file's age/retirement so the user can weigh the
  evidence himself.

Nonexistent cited paths are skipped — fabricated receipts belong to
`completion-artifact` / `claim-verification`.

## Recovery
Check the file's mtime / newest entry timestamp. Either locate the live
sibling source (the writer may have moved, as echo_post_log →
echo_tweet_log) or state the age explicitly next to the citation
("last written 2026-04-11 — treating as historical only").

## Calibration
Replay of 1,404 recent Shadow outbound Discord messages (2026-07-07):
11 fires (0.8%), overestimated because mtime was measured at replay time,
not send time; the surviving fires were genuine dead-source citations
(`claude_usage_log.json` cited 30+ days after its writer stopped).

## Relationship to other contracts
- `state-assertion-grounding` / `stale-state-assertion-guard`: require that
  *a* read happened. This guard requires the read source be *alive*.
- `corpus-citation-guard`: same-turn read of internal corpora; does not check
  corpus freshness.
- `canonical-source-guard`: per-fact authoritative-source registry; this
  guard is registry-free and covers the long tail of state files.
