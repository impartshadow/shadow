# Contract: lossless-session-pointer

**Type:** Harness-side (process enforcement, not code-gated)

**Trigger:** Any write or rewrite of `memory/session_handoff.md`

**Precondition:** The previous session handoff state must be recoverable after the write.

**Rule:**

When updating `session_handoff.md`, the current git commit SHA (HEAD at time of write) must be preserved in `state/session_pointer_chain.json` before overwriting. This creates a queryable pointer chain: any prior session state is recoverable via:

```
git show <sha>:memory/session_handoff.md
```

The `recover_from_sha(sha)` function in `scripts/loop_dispatcher.py` implements this recovery path.

**Enforcement:** Harness-side. The `loop_dispatcher.py` script calls `record_session_pointer()` at the start of each run, which writes HEAD SHA before any state mutations.

**Why this matters (LCM motivation):**
Flat rolling checkpoints accumulate drift — when a session handoff is overwritten, prior reasoning context is permanently lost. The LCM paper (arXiv, Feb 2026) demonstrates that agents using deterministic pointer chains to prior state outperform those relying on lossy model-written memory, because reconstruction succeeds even after context compression. Shadow's session handoff is the highest-value target for this pattern.

**Recovery:** If `session_pointer_chain.json` is missing or empty, run `git log --oneline -20` to find candidate SHAs and manually verify via `git show <sha>:memory/session_handoff.md`.

**Escalation:** If the pointer chain file exceeds 100 entries, it is auto-truncated to the last 100 by `record_session_pointer()`. No escalation needed.

**Contracts referenced:** loop-tripwire (FM-003), loop-budget-gate (FM-003)
