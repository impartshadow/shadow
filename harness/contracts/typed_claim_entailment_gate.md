# Contract: typed-claim-entailment-gate

## Type

Pre-response deterministic gate implemented by
`core/contracts.py:TypedClaimEntailmentGate`. Severity: `block`.

## Trigger boundary

The gate runs only when the caller explicitly supplies `claim_manifest` or
`assertion_spans`. Those fields prove that the typed-claim extraction pipeline
ran. Plain response contexts from the legacy Discord guard are not applicable:
they contain neither typed evidence nor a way to produce a compliant manifest.

When the pipeline is active, every detected externally checkable assertion must
map to exactly one complete typed claim. Non-factual modalities such as
questions, proposals, uncertainty, logic, and stable general knowledge may be
declared exempt.

## Enforcement

Each non-exempt claim must have a canonical subject, resolved referent bindings,
trusted immutable evidence, a completed operation phase, valid freshness, and a
direct or allowlisted deterministic derivation that entails the full claim
tuple. Missing or malformed manifests block as `FM-014.MANIFEST`; referent,
evidence, lifecycle, staleness, completeness, and entailment failures retain
their corresponding FM-014 subcodes.

## Recovery

Run the typed extraction pipeline before invoking this gate. Then atomize the
response, bind each claim to the correct entity and evidence records, and emit
only claims fully entailed by admissible evidence. If the pipeline did not run,
do not synthesize a manifest inside the gate; treat it as not applicable and let
the other deterministic evidence guards evaluate the plain response.
