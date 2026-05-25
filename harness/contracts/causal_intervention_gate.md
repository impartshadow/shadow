# Contract: causal-intervention-gate

**Type:** Behavioral pre-check (harness)
**Trigger:** Any irreversible action — email send, git push, Substack publish, Discord DM, webhook
**Precondition:** Shadow has articulated a causal commitment before executing
**Enforcement:** Harness prompt + CausalInterventionGate contract in `core/contracts.py` (Tier 2)
**Recovery:** If commitment cannot be made → downgrade to EXPERIMENT (dry-run first)
**Escalation:** If EXPERIMENT output is ambiguous → ABSTAIN and surface to the user

## Motivation

CIVeX (2025) demonstrates that schema validation and policy filters do not certify that a proposed action has an identifiable causal effect on the target state. A valid tool call can still execute against the wrong target or under confounded state — producing zero effect or unintended side-effects. This is distinct from the existing verify-before-push contract (which checks *output quality*); this contract checks *causal identifiability*.

## Verdicts

| Verdict | Condition | Shadow behavior |
|---|---|---|
| EXECUTE | Causal path is clear: action A → state change B, fully identified | Proceed |
| REJECT | No identifiable causal effect (no-op, wrong target, action already applied) | Block; surface reason |
| EXPERIMENT | Causal path is plausible but unverified (new recipient, new branch, new publish path) | Dry-run first, observe output |
| ABSTAIN | State is confounded — effect cannot be identified even with a dry-run | Surface to the user |

## Causal commitment format

Before any EXECUTE verdict on an irreversible action, Shadow must be able to complete:

> "This [action] will change [STATE] from [BEFORE] to [AFTER] because [REASON]."

**Examples:**

- `"This git push will update origin/main from adf7604 to 3b9f200 because the 2/day Substack cap fix passed pytest and the smoke test."`
- `"This email will deliver the weekly digest to [private-email] (not previously received) because the Gmail API shows no matching subject in the last 7 days."`
- `"This Substack publish will add brief #106 to echofromshadow.substack.com (currently at 2 posts today — cap will be reached, publish blocked → downgrade to EXPERIMENT)."`

If Shadow cannot complete this sentence with specifics, the verdict is EXPERIMENT, not EXECUTE.

## Scope

Applies to: email sends, git pushes to remote, Substack publishes, Discord DMs to external users, outbound webhooks.

Does NOT apply to: read operations, local file edits, memory writes, internal Discord channel posts.

## Integration with existing contracts

- **email-recipient-guard** (FM-016): causal commitment adds the state-change assertion on top of recipient validation.
- **git-push-target-guard** (FM-015): causal commitment adds the branch-state assertion on top of target validation.
- **verify-before-push** (FM-002): causal commitment is the *pre-execution* analogue; verify-before-push is the *post-execution* confirmation.
- **platform-action-precheck** (FM-012): causal commitment fires within the pre-flight check sequence.
