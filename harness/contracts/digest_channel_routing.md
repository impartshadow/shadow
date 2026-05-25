# Contract: digest-channel-routing

## Type
Design rule — harness-enforced

## Trigger
When writing or modifying any script, hand, or tool that produces digest, summary,
research brief, deep-dive, or signal-aggregation content.

## Rule

| Content type | Default channel |
|---|---|
| Digest, summary, research brief, deep-dive, signal aggregation | `#research` |
| Infra noise: bug fixes, cron output, health alerts | `#shadow-log` |
| the user-facing status, decisions, blockers | `#shadow-hq` |

**Default for digest/summary content is always `#research`.** Do not route to
`#shadow-hq` unless the content is a business decision or actionable blocker
requiring the user's response.

## Precondition
Before wiring up any new digest/summary output, confirm the channel is `#research`.
If you find yourself routing to `#shadow-hq`, ask: "does the user need to act on this,
or is this for ambient awareness?" If ambient → `#research`.

## Enforcement
Harness rule. No code gate — prevent by design.

## Failure mode
FM-012 (platform action misconfiguration). Corrected twice (2026-05-11). The pattern:
new digest hands get wired to `#shadow-hq` by default because it's the most visible
channel. Resist this.

## Escalation
If content genuinely spans both channels (e.g., a brief that IS the checkpoint signal),
post the brief to `#research` and post a one-line pointer to `#shadow-hq`.
