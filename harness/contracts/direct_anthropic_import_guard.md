# direct-anthropic-import-guard

**Type:** Pre-check (code-enforced, blocking)
**Failure mode:** FM-004 (wrong tool/client route)
**Trigger:** Write/Edit that adds a direct `anthropic` SDK import outside the canonical wrapper

**Precondition:** Anthropic SDK calls must route through `core/claude_client.py`.

**Enforcement:** `core/contracts.py:DirectAnthropicImportGuard.check_pre()` blocks direct `import anthropic` / `from anthropic import ...` in new non-test code.

**Recovery:** Use `core.claude_client` wrapper helpers instead of creating a local SDK client.

**Escalation:** Only allow a new direct import if the user explicitly approves a second canonical wrapper.
