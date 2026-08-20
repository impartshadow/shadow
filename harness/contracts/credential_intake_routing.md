# Contract: credential-intake-routing

## Type
Post-response gate — deterministic enforcement via `core/contracts.py:CredentialIntakeRoutingGuard`

## Failure mode
FM-013 (clarification quality — routing delegated back to the user)

## Origin incident
2026-08-19 22:53 #shadow-hq. the user pasted a 94-char token with no instruction,
minutes after asking about OpenRouter access to open-source models. Shadow
enumerated candidates ("Replit, OpenRouter, or something else?") and asked
the user to pick. The token sat unwired and the user became the router for state his
own recent messages already resolved.

## Principle
A bare credential paste is an update to the standing operating intent, not an
isolated request. The next reversible action is predictable from recent
context: infer → validate read-only → store in Bitwarden → wire → report.

## Trigger (both required, same turn)
1. the user's message is dominated by a high-entropy secret-like token
   (≥28-char token-safe run with ≥3 character classes, or a known key prefix
   like `sk-`/`ghp_`/`AKIA`; non-token remainder ≤80 chars).
2. The response asks the user to identify the service/destination
   ("which service", "tell me the service name", "what's this for",
   "where should I put this").

## Exemption
The ask is allowed when the same response carries action evidence:
- Bitwarden store receipt (`bw create`, "stored in Bitwarden")
- read-only validation probe result (tested/validated against an endpoint,
  401/invalid-key outcome)
- explicit failed-inference disclosure ("checked recent context, no candidate")

## Enforcement
Severity: **block**.

## Violation recovery
1. Infer the target service from the last ~10 messages of channel context.
2. If a candidate exists, validate with a read-only probe (list-models /
   key-info endpoint) — never a mutating call.
3. Store in Bitwarden under the candidate service (marked unverified if no
   probe exists) and wire it in.
4. Report the inference, probe result, and rotation warning (pasted-in-chat
   copies are considered exposed).
5. Ask only after stating that context inference and validation both failed.
