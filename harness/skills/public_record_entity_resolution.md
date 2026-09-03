# Skill: public_record_entity_resolution

## Trigger

Use when the user supplies an address or parcel and asks who owns, controls, formed,
registered, or is connected to the property or owning entity.

## Guardrails

- The user-supplied address or parcel is the lawful seed. Do not expand into
  private-account, credential, people-search, or contact-data sources.
- Public ambiguity is not a privacy boundary. Continue through public records
  while labeling the strength of every connection.
- Never equate a registered agent, principal-office address, organizer, lawyer,
  or shared address with beneficial ownership unless a deed or filing says so.
- Do not reveal personal phone numbers, personal email addresses, dates of birth,
  financial identifiers, or non-public household information.

## Workflow

1. Create the deterministic plan:
   `python3 scripts/public_record_entity_resolution.py --jurisdiction "<county, state>" --address "<address>"`
   (Use `--parcel` instead when supplied.)
2. Follow the chain serially: county parcel → owner entity → state registry →
   registered agent/principal office → recorder deeds and official filings.
3. At each stage use official structured sources first. Record the exact result
   URL, record date, and observed fact; a search-results snippet alone is not a
   documented ownership claim.
4. If an endpoint blocks or returns an unusable shell, treat it as routing
   failure—not absence. Try, in order:
   - direct official result/document URL;
   - alternate official assessor, GIS, recorder, or state index;
   - cached search result that identifies the official record;
   - `mcp__shadow__browser_open`/browser-capable access;
   - home-proxy browser route when access remains blocked.
5. Classify each supported connection exactly as one of:
   - `documented_ownership`
   - `registered_agent_identity_bridge`
   - `shared_address_evidence`
   - `inferred_relationship`
6. Feed evidence and retrieval attempts to the resolver with
   `--evidence-json`. Report its strongest-supported connection and disclose
   whether beneficial ownership remains unavailable.
7. Stop only at documented ownership, exhausted public routes, or a named
   genuinely-private-data boundary. Nonconclusive evidence is not a stop reason.

## Output

- Strongest supported connection first.
- Evidence ladder separating record facts from inference.
- Investigation path, including blocked routes and fallbacks attempted.
- Remaining gap and exact stopping reason.
- Direct links to the official records used.
