# AI Agents Do Not Need Better Prompts. They Need Runtime Contracts.

Most agent failures are treated like personality problems.

The model was lazy. The instruction was unclear. The context window was too full.
The prompt needed another bullet.

That framing is weak. Production agents fail in repeatable, nameable ways. A
repeatable failure should not be fixed with more pleading. It should become a
runtime contract.

Shadow Kit is built around that premise.

## The failure pattern

After enough real sessions, agent failures stop looking random. They cluster.

Common examples:

- **Capability denial:** the agent says it cannot access or do something before
  trying the available tool path.
- **Action deferral:** the agent proposes work instead of executing work it is
  already authorized to perform.
- **Manual fallback:** the agent gives the human UI instructions instead of using
  an API, browser session, credential store, or script.
- **Unverified completion:** the agent claims a code change is shipped without
  running tests or reading back the changed state.
- **Tool misrouting:** the agent uses the wrong tool family even though the
  system has a sanctioned path.
- **Context overrun:** the agent keeps working the old thread after the user has
  moved on.
- **Dox or recipient mistakes:** the agent sends to, posts to, or names an
  entity outside its authority envelope.

Those are not edge cases. They are the normal failure modes of an autonomous
agent under pressure.

## The wrong fix

The default fix is to add another instruction:

> Do not say you cannot do something before trying.

Then the agent violates it again.

So the instruction becomes louder:

> CRITICAL: NEVER say you cannot do something before trying.

Then it violates it again in a slightly different surface form.

This is the prompt treadmill. It feels like governance because the rules are
visible. It is not governance because nothing deterministic happens when a rule
is violated.

## The better unit: a contract

A contract is a named failure mode plus an executable check.

It has:

- a trigger
- a precondition or postcondition
- a severity
- a recovery path
- tests

Example:

```python
ctx = ContractContext(
    action="respond",
    response_text="I can't access that page.",
    tool_calls=[],
    smoke_test_ran=False,
)

violations = check_all_post(ctx)
```

That should not produce a better apology. It should block the response and force
the agent down the recovery path: attempt the tool call first, then report what
happened.

## What Shadow Kit contains

This repository is the sanitized public harness extracted from Shadow, a live
autonomous agent.

It includes:

- contract classes for common agent failure modes
- a failure-mode taxonomy
- human-readable contract specs
- skill templates
- governance metrics for hot contracts and violation counts
- tests for the enforcement layer

The public repo currently contains more than 100 contract specs because the
system is grown from live failures, not designed from a clean-room theory of
what agents might do wrong.

## The architecture

Shadow Kit gives you the open-core enforcement layer:

```text
agent action/response
        |
        v
pre/post contract checks
        |
        +-- pass  -> execute/respond
        |
        +-- block -> recover, retry, or escalate
```

For many local agents, that is enough. The harness catches the recurring
behavioral failures before they reach the user.

For teams running agents with real side effects, the stronger architecture puts
the governor outside the agent:

```text
untrusted agent container -> governance gateway -> external world
                              |
                              v
                    signed receipt log + usage meter
```

The distinction matters. A prompt can ask an agent not to call an endpoint. An
external gateway can make the call impossible, sign the decision, and produce an
audit trail.

## The commercial wedge

The open-core kit is for builders who want to understand and adopt the pattern.

The paid product is the governed gateway layer:

- boundary enforcement between agent and external systems
- deterministic mediation for egress and user-visible output
- signed, hash-chained receipts
- per-governed-agent metering
- invoice and audit export
- managed deployment for teams that do not want to build the control plane

The value metric is simple: **governed agents**. If an agent can affect external
systems, it should be governed, metered, and auditable.

## Why this is different

Most agent tooling optimizes for capability:

- more tools
- longer context
- better planning
- more autonomy

Shadow Kit optimizes for failure containment.

That is the missing layer. Autonomy without a governor is just a larger blast
radius. The useful product is not "an agent that can do anything." The useful
product is an agent that can do real work inside enforced boundaries.

## Start here

Install the kit:

```bash
git clone https://github.com/impartshadow/shadow.git
cd shadow
pip install -e .
python3 -m pytest -q
```

Try the contract layer in your own agent:

```python
from shadow_kit.contracts import ContractContext, check_all_pre, check_all_post
```

Then turn every repeated failure into a contract. If the failure happened twice,
it is not a surprise anymore. It is a missing guard.

For commercial gateway access or implementation work: `impartshadow@gmail.com`
