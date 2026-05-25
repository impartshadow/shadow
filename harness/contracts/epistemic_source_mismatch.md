# Contract: epistemic-source-mismatch

## Type
Pre-check — harness-enforced

## Trigger
Any turn where Shadow queries an external knowledge API or structured knowledge source
(Semantic Scholar, Wikidata, knowledge graph endpoints, ontology services) expecting
entailment or inference — not just raw data retrieval.

## Precondition
Before accepting results from a structured knowledge source as authoritative, ALL
of the following must hold:
1. The source's known coverage scope matches the task vocabulary (e.g., don't query
   a biomedical KG for financial reasoning)
2. If the source uses a specific entailment regime (OWL, RDFS, closed-world vs.
   open-world assumption), that regime is compatible with the inference the task requires
3. An empty result is NOT treated as negative evidence unless the source is confirmed
   to have complete coverage of the queried domain

## Enforcement
**Harness-enforced** — no code contract required at current scale. Applies at the
research-planning stage, before tool calls fire.

Known source profiles:
- **Semantic Scholar**: open-world, citation graph, strong on CS/ML/bio, weak on
  social sciences post-2023, no causal entailment
- **Wikipedia/Wikidata**: open-world, encyclopedic, strong recall but uneven precision,
  no formal entailment regime
- **ArXiv API**: closed-world on indexed papers only, no forward-citation inference
- **General web search**: open-world, no closure guarantees, treat all results as
  candidate evidence requiring verification

## Violation recovery
1. Empty result from a structured source → log as "source coverage miss", not
   "no evidence exists"
2. Before citing absence of evidence, confirm the source has the entailment coverage
   needed to support that negative claim
3. When source-task vocabulary mismatch is detected, switch to a source with broader
   coverage or explicitly caveat the result

## False positive exemptions
- Raw document retrieval (no entailment required — just fetch and summarize)
- Queries where the result is cross-validated against 2+ independent sources
- Internal Shadow state files (trusted, no entailment assumptions)

## Escalation
If a research brief is later found to contain false negatives from source coverage
mismatches, log to `state/research_errors.jsonl` with source, query, and failure type.

## Origin
2026-05-20: "Discoverable Agent Knowledge — A Formal Framework for Agentic KG
Affordances" (arXiv cs.AI). Core finding: current KG metadata standards describe
*what* a source contains but not *what an agent can prove from it* given closure
assumptions and entailment regime. Silent empty results from capability-mismatched
sources are indistinguishable from genuine negative evidence without this contract.
