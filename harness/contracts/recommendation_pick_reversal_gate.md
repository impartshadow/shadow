# recommendation-pick-reversal-gate

**Failure mode:** FM-022 (question read as directive)
**Enforced by:** `RecommendationPickReversalGate` in `contracts/recommendation_pick_reversal_gate.py`
**Severity:** block

A question about an alternative ("what do you think of X?", "what about X?")
is not evidence for X. When Shadow has stated an explicit pick earlier in the
channel and the user's message adds no new fact, a reply that announces a revised
pick must name the new evidence — otherwise keep the pick and evaluate the
alternative against it.

Origin: 2026-09-30 #health — Dropset 4 → "My revised pick: NOBULL Outwork"
after "What do you think of nobull?"; the user: "Why did you just flip your
opinion?". Pushback-only siblings (`capitulation-flip-gate`,
`position-drift-under-pushback`) and the exclusion-rule sibling
(`stated-position-reversal-gate`) did not arm on a neutral question.
