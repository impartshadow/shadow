# agent-native-shipping-gate

**Type:** Post-check (code-enforced, block severity, deterministic)
**Failure mode:** FM-026 (claim-without-evidence — framing/artifact mismatch)
**Trigger:** Every response (`ctx.action == "respond"`) ≥ 120 chars
**Reference:** the user 2026-06-23 02:16 #moonshot incident:
"You went on a whole thing about how we should do things only an agent could
do and then shipped something that doesn't require any AI or reasoning."
Memory: `feedback_agent_native_quality_bar.md`.

**Precondition:** ALL of the following must hold:

1. Response contains an "agent-native" framing token (one of):
   `agent-native`, `agent native`, `only an agent can/could/should`,
   `only a continuously-running agent`, `requires LLM/model reasoning`,
   `LLM/model reasoning at runtime`, `dynamic model/LLM/agent judgment`,
   `agent-only part`, `the part that needed an agent`,
   `what an agent can do that a human`,
   `requires being a continuously-running agent`.
2. Response cites at least one Python file under sanctioned roots
   (`scripts/`, `core/`, `echo/`, `tools/`, `agents/`, `harness/`).
3. At least one cited path resolves on disk.
4. ALL resolved cited paths lack a runtime model-call indicator
   (`claude_client`, `gemini_utility`, `gemini_ask`, `codex_ask`,
   `anthropic.Anthropic/Client/AsyncAnthropic`, `from anthropic`,
   `import anthropic`, `from openai`, `openai.ChatCompletion/...`,
   `.messages.create`, `.completions.create`,
   `claude-(opus|sonnet|haiku|fable)`, `claude_(sonnet|opus|haiku)`).

If *any* cited resolved file contains a model call, the gate stays silent —
the agent-native framing is anchored to a real reasoning artifact and the
deterministic files are supporting glue.

**Enforcement:** Block. Three valid recovery paths:

1. Commit the actual model-using module (`claude_client.ask`,
   `gemini_utility`, `codex_ask`, `anthropic.messages.create`) so the
   artifact matches the framing.
2. Drop the agent-native framing from the receipt.
3. Cite a different already-committed file that carries the runtime
   reasoning layer.

**False-positive control:** The four-way `AND` means strategy discussion
that mentions "agent-native" without a file citation never fires; mixed
responses where any cited file has an LLM call never fire; responses citing
unresolvable paths never fire.

**Related:**
- `feedback_agent_native_quality_bar.md` — the memory rule this gate
  enforces; post-hoc memory had low leverage because the failure happens at
  artifact-production time.
- `external-quality-gate` (FM-036) — separate Haiku-judged best-work check
  on outbound content.
- `partial-evidence-flag` (FM-026) — sibling failure mode, fires on
  definitive claims with thin evidence.
