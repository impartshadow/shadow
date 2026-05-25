# Contract: memory-freshness

**Type:** Harness (soft enforcement — code enforcement tracked as future work)
**Failure mode:** FM-022 (self-consistency via stale facts)

## Trigger
When writing or updating a memory file that contains a versioned fact: file paths, API endpoints, credential locations, project status, contact details, or specific dates.

## Precondition
Memory file contains at least one claim that could become false over time (as opposed to stable preferences, personality rules, or behavioral guidance).

## Rule
Versioned facts MUST include an inline `last_verified` marker:

```
token path: ~/.config/shadow/token.json — last_verified: 2026-04-25
RSN: Imparthuman — last_verified: 2026-04-20
```

Evidence-free facts (preferences, behavioral rules, communication style) do NOT require markers — they don't decay on a calendar.

## Confidence decay rule
- `last_verified` < 30 days: treat as current
- `last_verified` 30–90 days: treat as likely current; verify before acting on high-stakes decisions
- `last_verified` > 90 days OR no marker: treat as unverified; run a fresh lookup before citing or acting

## Enforcement
The `stale_memory_freshness` idle task (idle_moonshot.py) enforces this passively by surfacing stale candidates weekly. During active sessions: if citing a versioned fact from a file with no `last_verified` marker, assume file mtime as the verification date and apply the decay rule.

## Recovery
On stale-fact detection: verify immediately, update the memory file with corrected value + fresh `last_verified`, never act on the stale version.

## Escalation
Silent self-correction only. Never surface to the user unless the correction changes a decision already in flight.
