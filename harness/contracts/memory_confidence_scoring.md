# Contract: memory-confidence-scoring

**Type:** Harness (soft enforcement)
**Failure mode:** FM-034 (factual output error — wrong claim persisted as memory)

## Trigger

Any new memory file written to `memory/*.md` or any substantive update to an existing memory file.

## Rule

Every memory file MUST include a `confidence` field in its YAML frontmatter:

```yaml
---
name: example_memory
description: one-line description
type: feedback | user | project | reference
confidence: high | medium | low
---
```

### Confidence levels

| Level | Criteria | Action |
|---|---|---|
| **high** | the user stated it directly, or Shadow observed it firsthand via tool output | Write immediately |
| **medium** | Inferred from behavior, patterns, or indirect evidence | Write, but add `last_verified` marker if versioned fact |
| **low** | Single data point, ambiguous signal, or heavily inferred | Defer: surface to the user for confirmation OR wait for a second confirming signal before writing |

### Low-confidence exceptions

A low-confidence write is allowed when:
- It is a correction to an existing wrong memory (even uncertain corrections beat stale wrong ones)
- the user explicitly asks Shadow to remember something (the user's intent overrides confidence)

## Interaction with memory-freshness

`confidence` tags the initial write quality. `last_verified` tags ongoing decay. Both apply: a high-confidence write that is 90 days old without verification should be treated as unverified per `memory_freshness.md`.

## Enforcement

Harness (manual discipline). Shadow self-applies before every memory write.

## Recovery

If a memory file lacks a confidence field: add it on the next write to that file. Default to `medium` if uncertain.

## Escalation

Never surface to the user.
