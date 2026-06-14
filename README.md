# Shadow

**The sanitized public harness extracted from Shadow: contract enforcement, failure mode taxonomy, and skill templates for reliable AI agents.**

Shadow Kit is a Natural Language Agent Harness (NLAH) for building reliable AI assistants on top of Claude Code. It provides:

- **Contract enforcement** -- deterministic pre/post condition gates that catch failure modes before they reach the user
- **Failure mode taxonomy** -- a named catalog of ways AI agents fail, with automated recovery paths
- **Skill system** -- structured task flows with triage/execute/verify stages
- **Runtime policy** -- session lifecycle, tool routing, and behavioral defaults
- **Governance** -- runtime violation metrics, hot contract detection, and auto-recovery
- **Signed receipts** -- tamper-evident audit artifacts for governed agent actions

## Why this exists

AI agents fail in predictable ways: they deny capabilities they have, push code without verifying it, propose actions instead of executing them, and give manual instructions instead of solving problems programmatically. These aren't bugs -- they're systematic failure modes that repeat across sessions.

Shadow Kit turns these failure modes into code-enforced contracts. Instead of relying on the LLM to follow prompt instructions (which it will eventually violate), contracts run deterministic checks against every action and response. When a contract fires, it blocks the action and provides a recovery path.

This is not a framework. It's an enforcement layer that sits on top of Claude Code and makes your agent's behavioral guarantees deterministic.

## Read the thesis

[AI Agents Do Not Need Better Prompts. They Need Runtime Contracts.](docs/agent-failure-modes.md)

The short version: recurring agent failures are product requirements. Name them,
write contracts for them, and enforce the boundary before the failure reaches a
user or external system.

For a runnable demo, start with `examples/basic_assistant.py`. It shows a blocked
push, a blocked capability denial, a custom contract, governance metrics, and a
signed receipt.

## Quick start

### 1. Install

```bash
pip install shadow-kit
```

Or install from source:

```bash
git clone https://github.com/impartshadow/shadow.git
cd shadow
pip install -e .
```

### 2. Copy the template

```bash
cp shadow-kit/CLAUDE.md.template ./CLAUDE.md
```

Edit `CLAUDE.md` to configure your agent's identity, tool routing, and session behavior.

### 3. Set up your harness

Copy the `harness/` directory into your project root:

```bash
cp -r shadow-kit/harness/ ./harness/
```

Edit the files to match your agent's capabilities:

- `harness/_runtime.md` -- session startup, tool routing, default behaviors
- `harness/contracts/*.md` -- which contracts to enforce and how
- `harness/skills/*.md` -- task-specific flows your agent handles
- `harness/failure_modes/taxonomy.md` -- your agent's failure catalog

### 4. Use contracts in your code

```python
from shadow_kit.contracts import (
    ContractContext, check_all_pre, check_all_post,
    register_contract, get_governor,
)
from shadow_kit.receipts import issue_contract_receipt, verify_receipt

# Before an action (e.g., git push, sending email, archiving):
ctx = ContractContext(
    action="git_push",
    files_edited=["src/main.py"],
    response_text="Done.",
    verification_output="",  # Oops -- no verification
)
violations = check_all_pre(ctx)
for v in violations:
    print(f"[{v.severity}] {v.contract}: {v.message}")
    # => [block] verify-before-push: Push attempted without verification output.

# After generating a response:
ctx = ContractContext(
    action="respond",
    response_text="I can't access that page.",
    tool_calls=[],
    smoke_test_ran=False,
)
violations = check_all_post(ctx)
# => [block] pre-denial-gate: Denial without smoke test.

# Check governance metrics:
governor = get_governor()
metrics = governor.get_metrics()
print(f"Total violations: {metrics['total_violations']}")
print(f"Hot contracts: {governor.get_hot_contracts()}")

# Issue a signed audit receipt for a governed decision:
receipt = issue_contract_receipt(
    agent_id="research-agent-1",
    sequence=1,
    ctx=ctx,
    violations=violations,
    signing_key="dev-only-signing-key",
    policy_version="local-policy-v1",
)
assert verify_receipt(receipt, "dev-only-signing-key").valid
print(receipt["decision"], receipt["receipt_hash"])
```

### 5. Register custom contracts

```python
from shadow_kit.contracts import Contract, ContractContext, Violation, register_contract

class NoSQLInjection(Contract):
    name = "no-sql-injection"
    failure_mode = "FM-CUSTOM-001"

    def check_pre(self, ctx: ContractContext) -> Violation | None:
        for param in ctx.tool_params:
            query = param.get("query", "")
            if "DROP TABLE" in query.upper():
                return Violation(
                    contract=self.name,
                    failure_mode=self.failure_mode,
                    message="SQL injection detected in query parameter.",
                    severity="block",
                    recovery="Use parameterized queries.",
                )
        return None

register_contract(NoSQLInjection())
```

## Architecture

```
your-project/
  CLAUDE.md                    # Agent config (generated from template)
  harness/
    _runtime.md                # Session lifecycle, tool routing, defaults
    contracts/
      verify_before_push.md    # Human-readable contract specs
      pre_denial_gate.md
      ...
    skills/
      research.md              # Task-specific flows
      email_triage.md
      ...
    failure_modes/
      taxonomy.md              # Named failure catalog
  core/
    contracts.py               # Code-enforced contract classes
```

### How it works

1. **CLAUDE.md** is the loader. It tells the LLM where to find behavioral rules, which contracts are active, and what the quick-reference rules are.

2. **Harness files** (`harness/`) are human-readable Markdown specs. Each contract file defines: type, trigger, precondition, enforcement mechanism, recovery path, and escalation rules. Skills define task flows with triage/execute/verify stages.

3. **Code enforcement** (`core/contracts.py`) makes harness rules deterministic. Each Contract subclass implements `check_pre()` and/or `check_post()` against a `ContractContext`. Violations are either `warn` (flag but allow) or `block` (prevent the action).

4. **The taxonomy** (`harness/failure_modes/taxonomy.md`) names every failure mode. When a new pattern is observed, it gets a name (FM-XXX), a contract, and a code guard. Naming failures makes them tractable.

5. **Governance** (`ContractGovernor`) tracks violation counts, contract error rates, and auto-recovery success rates. Use `get_governor().get_metrics()` to monitor contract system health.

6. **Receipts** (`shadow_kit.receipts`) turn each governed decision into a signed JSON artifact. The open-source kit uses caller-provided HMAC keys; a gateway deployment can hold signing keys outside the agent container, attach policy versions and metering, and export the receipt chain for audits.

### Contract lifecycle

```
Action/Response -> check_pre()/check_post() -> Violation? -> Block/Warn -> Recovery
                                                          -> auto_recover() -> Corrected response
```

Contracts support auto-recovery: instead of just blocking, a contract can rewrite the response to fix the violation. Override `auto_recover()` in your Contract subclass.

### Signed Audit Receipts

Receipts are the bridge from local contract checks to a governed agent control
plane. A receipt records the governed agent id, sequence number, previous
receipt hash, action, decision, policy version, context hash, contract
violations, metering fields, HMAC-SHA256 signature, and signed-envelope hash.

```python
from shadow_kit.contracts import ContractContext, check_all_pre
from shadow_kit.receipts import issue_contract_receipt, verify_receipt

ctx = ContractContext(
    action="git_push",
    files_edited=["src/main.py"],
    response_text="Done.",
)
violations = check_all_pre(ctx)

receipt = issue_contract_receipt(
    agent_id="demo-agent",
    sequence=42,
    ctx=ctx,
    violations=violations,
    signing_key="local-dev-key",
    policy_version="runtime-contracts-v1",
    previous_hash="",
)

verified = verify_receipt(receipt, "local-dev-key")
assert verified.valid
```

In an open-core setup, the agent can emit local receipts. In the commercial
gateway architecture, the gateway owns the signing key and the agent only sees
the decision. That makes policy enforcement, per-governed-agent metering, and
audit export independent of the agent's prompt.

## Included contracts

| Contract | Failure mode | What it catches |
|---|---|---|
| `verify-before-push` | FM-002 | Code push without running verification |
| `pre-denial-gate` | FM-001 | "I can't access X" without trying first |
| `loop-tripwire` | FM-003 | 3+ edits to the same file in a session |
| `read-before-edit` | FM-003 | Editing a file without reading it first |
| `action-deferral-guard` | FM-011 | Proposing instead of executing; manual instructions instead of API calls |
| `topic-overrun-guard` | FM-013 | Continuing a topic after the user signals closure |
| `completion-integrity` | FM-014 | Claiming "done" while listing unfinished items |
| `git-push-target-guard` | FM-015 | Force-push to protected branches |
| `dangerous-path-guard` | FM-017 | Writes to sensitive file paths (.env, credentials, /etc/) |

These are the generic contracts that apply to any agent. Shadow's production harness includes additional domain-specific contracts (email archiving, tool routing, memory validation) that you can use as templates.

## Included failure modes

| Code | Name | Pattern |
|---|---|---|
| FM-001 | capability-denial | Agent says "I can't" without attempting the action |
| FM-002 | unverified-push | Agent claims "done" without running verification |
| FM-003 | edit-loop | 3+ commits to the same file without fixing root cause |
| FM-006 | misunderstood-intent | Agent answers a different question than was asked |
| FM-007 | lost-context | Agent forgets a decision from earlier in the session |
| FM-008 | premature-proposal | Agent proposes instead of executing |
| FM-010 | sycophantic-validation | Agent praises the user's idea instead of evaluating it |
| FM-011 | explain-instead-of-act | Agent describes what it would do rather than doing it |
| FM-012 | manual-instruction | Agent gives "click here" instructions instead of solving via API |
| FM-013 | topic-overrun | Agent continues a topic after user signals closure |
| FM-014 | completion-integrity | Agent claims "shipped" while acknowledging gaps |

## Customization

### Adding a contract

1. Create a `Contract` subclass in `core/contracts.py`
2. Implement `check_pre()` and/or `check_post()`
3. Call `register_contract(instance)`
4. Document in `harness/contracts/<name>.md`
5. Add to `harness/failure_modes/taxonomy.md`
6. Write tests

### Adding a skill

Create a Markdown file in `harness/skills/` following this structure:

```markdown
# Skill: your-skill-name

## Role sequence
Triage -> Execute -> Verify

## Stage: Triage
1. How to identify this task
2. What to check before starting

## Stage: Execute
1. Step-by-step execution
2. Tools to use

## Stage: Verify
1. How to confirm success
2. What to check for errors

## Contracts referenced
- List which contracts apply
```

### Adding a failure mode

Add an entry to `harness/failure_modes/taxonomy.md`:

```markdown
## FM-XXX: your-failure-name
**Pattern:** What the agent does wrong
**Root cause:** Why the agent does this
**Contract:** Which contract should catch it
**Code guard:** Which Contract subclass enforces it
**Recovery:** What to do when it fires
```

## Self-improvement

Shadow Kit supports a self-improvement loop: audit conversations for failure patterns, then generate new Contract subclasses to catch them. The pattern:

1. **Audit** -- review recent conversations for repeated corrections
2. **Name** -- give the failure pattern a code (FM-XXX) and add it to the taxonomy
3. **Guard** -- write a Contract subclass with regex-based detection
4. **Test** -- verify the contract catches the failure without false positives
5. **Ship** -- register the contract and update the harness docs

Code enforcement is the default. Prose rules are a last resort -- they work until the LLM ignores them.

## Testing

```bash
python3 -m pytest tests/ -v
```


## Built with this in production

Shadow — the agent that built this harness — has been running as an autonomous business unit since early 2026. It manages:

- A research Substack ([Echo From Shadow](https://echofromshadow.substack.com)) — queued, scheduled, and published autonomously
- An algorithmic trading loop (Arbor) — daily options sessions with live P&L
- A content distribution pipeline — brief production, Echo posts, social
- Self-improvement — audits its own failure patterns and generates new contracts

The harness is not hypothetical. It is what keeps a live production agent coherent across sessions, tools, and failure modes.

## Apply this to your business

If you are building or running an AI agent and hitting reliability problems — agents that deny capabilities they have, push unverified code, get stuck in loops, or need constant babysitting — this is the pattern that fixes it.

Shadow works with a small number of teams to implement the NLAH pattern on their specific agent stack.

**Follow along:** [Echo From Shadow](https://echofromshadow.substack.com) — the newsletter where Shadow documents what it's building, what breaks, and what works.

**Consulting inquiries:** impartshadow@gmail.com

## License

MIT
