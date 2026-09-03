# Skill: thin_context_brief

## Trigger

Use when the user provides a sparse description of a person or organization and
asks Shadow to identify, investigate, contextualize, or brief it. Examples:
"the [family-member] from legal we just met", "that AI leader who left Epic", or
"figure out who this founder is." A full legal name is not required.

## Workflow

1. Bind pronouns and vague references against the quoted message, current
   channel, recent cross-channel history, and canonical memory.
2. Form multiple candidates. Search authorized internal context, first-party
   profiles and employer pages, official public records, then reputable news
   and professional sources.
3. Cross-check role, organization, geography, timeline, education, public work,
   and known professional relationships. Use independent sources; repeated
   copies of one claim count once.
4. Resolve only when one candidate is materially better supported. Otherwise
   return ranked candidates and the smallest fact that would discriminate them.
5. Produce a compact brief containing identity, confidence, why the match fits,
   decision-relevant background, recent public activity, sources, and material
   uncertainty.

## Boundaries

- Public professional research is allowed; uncertainty is not a reason to stop.
- Do not retrieve or expose private home addresses, personal phone/email,
  dates of birth, financial identifiers, credentials, or non-public household
  details.
- Do not turn professional associations or shared addresses into claims of
  employment, ownership, or personal relationships.
- Use the address/parcel public-record workflow when property ownership is the
  actual task.
