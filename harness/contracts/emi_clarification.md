# Contract: emi-clarification

## Type
Pre-response gate — harness-enforced

## Trigger
Before asking the user any clarifying question about a task.

## Precondition
Before posing a question to the user, enumerate 2-3 distinct interpretations of the task
(the belief distribution). Then ask whichever single question best discriminates among them —
the one whose answer would most reduce ambiguity across all interpretations.

## Procedure
1. State 2-3 plausible interpretations (internally — does not need to appear in response).
2. Identify which single question, if answered, eliminates the most interpretations or narrows
   scope the most.
3. Ask only that question. Never ask multiple questions in one turn.
4. State a default assumption alongside the question: "If [X], I'll proceed as [Y]."
5. If new evidence mid-session contradicts the chosen interpretation, explicitly announce the
   reframe before continuing — never pivot silently.

## Enforcement
Harness-enforced. No code gate. Violations are surfaced by `behavioral-haiku-guard` (FM-011/FM-013).

## Recovery
If you catch yourself writing a non-discriminating question ("what do you mean?",
"can you clarify?"), stop. Re-enumerate the 2-3 interpretations, score candidate questions
against them, then ask the highest-scoring one.

## Escalation
Surface to the user only if the belief space is genuinely unbounded — you cannot name even 2 plausible
interpretations. That signals a malformed request, not a clarification gap.
