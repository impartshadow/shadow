# Mutable State Grounding Guard

**Type:** Deterministic pre-response block (`MutableStateGroundingGuard`, FM-022)

**Trigger:** A `respond` action whose structured claim extractor emits a mutable current-state observation, inference, self-action result, concurrence, or temporal claim.

**Precondition:** The upstream extractor has run and supplied a completed extraction plus a versioned predicate ontology. If the producer is wholly absent (no claims, evidence, or derivations), the guard is not applicable; partial structured output fails closed.

**Enforcement:** Each governed claim must have resolved referents, an ontology-resolved predicate, and successful same-turn evidence matching the predicate and every referent. Evidence must include required fields and must not be stale after a mutation, superseded, or conflicting. Quantified and temporal claims require evidence for their added scope; current inferences require a registered reproducible derivation. Bounded historical reports, quotations, and genuine conditionals are excluded.

**Recovery:** Obtain live authoritative evidence for each referent and required field, or rewrite the statement as a specifically attributed historical report or bounded uncertainty. Do not repeat or endorse an unsupported proposition.

**Escalation:** Block the response. Repeated missing-extractor violations indicate an upstream integration failure; a completely unwired extractor must remain not-applicable rather than blocking every response.
