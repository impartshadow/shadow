# Contract Design Principles

## Purpose
This file codifies the structural rules Shadow uses when authoring new contracts.
Violating these rules during contract authoring is itself a failure mode — poorly
designed contracts accumulate, become unmaintainable, and open prompt-injection
vectors via vague escape hatches.

---

## Rule 1: Exemptions must be deterministic

**Bad** (judgment-based, attackable):
- "unless absolutely relevant"
- "when appropriate"
- "if the context warrants it"
- "in cases where it makes sense"

**Good** (observable, machine-checkable):
- "unless step 5 is reached" (specific procedural gate)
- "unless the decision is already in flight" (observable state)
- "unless the user has explicitly said 'quick take'" (literal string match)
- "unless the response is inside a fenced code block" (structural marker)

**Why**: Vague exemption language is a prompt-injection vector. A user can argue
that their request falls under "unless relevant"; they cannot argue their request
is inside a fenced code block if it isn't. Every exemption clause should be
answerable with yes/no by reading context alone — no judgment, no inference.

---

## Rule 2: Contracts must have a falsifiable trigger

The **Trigger** section must name a specific observable signal:
- A pattern present in output text (regex-matchable)
- A tool call sequence
- A word or phrase the user said
- A file state (exists / doesn't exist)

NOT: "whenever Shadow is uncertain" or "in research contexts" without further
specification.

---

## Rule 3: Prefer one precise rule over many narrow carve-outs

If a contract has more than 5 exemptions, it is a signal the contract is
poorly scoped. Each exemption added is engineering debt — and exponentially
expands the edge-case surface. Refactor the trigger condition before adding
a 6th exemption.

This is the root cause behind prompt accumulation failure: systems that block
a behavior → add an exception → add an exception to the exception → collapse.

---

## Rule 4: Every new contract requires a test in tests/test_contracts.py

Code-enforced contracts without tests degrade silently. The test must cover:
- At least one true-positive (contract fires correctly)
- At least one true-negative (contract does not fire on valid output)
- At least one exemption path (exemption correctly suppresses firing)

---

## Origin
2026-04-29: Simon the userison exposed OpenAI Codex base_instructions showing
hyper-specific rules with judgment-based escape hatches. The core failure mode:
"unless absolutely relevant" is vague enough to be argued by any user prompt.
Shadow's contracts must never repeat this pattern.
