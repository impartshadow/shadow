# completion-artifact

**Type:** Post-check (code-enforced)
**Failure mode:** FM-027 (fabricated completion)
**Trigger:** Every response

**Precondition:** Three independent checks gate completion language at generation time:

1. **Check A — cited paths must exist.** If the response says it ran/verified a file
   (`pytest X`, `python X`, `ran X`, `verified with X`), every cited path is stat-checked
   against disk in the same turn. Nonexistent → block.

2. **Check B — push/commit completion must cite a SHA.** Past-tense first-person
   commit/push framing ("Applied and pushed", "committed.", "pushed.", "fix landed")
   with no hex token anywhere → block. Forces a citation that `commit-hash-verification`
   then validates.

3. **Check C — closure language cannot leave a dirty worktree.** If the response
   contains a *closure signal* (done, all set, shipped, deployed, task complete,
   wrapped up, landed; or "committed and pushed", "pushed to main", "fix landed")
   AND the worktree has uncommitted code work (excluding routine `memory/`, `state/`
   mutations), block with the dirty path list.

**Important — Check C narrowing (2026-06-06):** Closure signals only. Generic edit
verbs ("added", "updated", "modified", "created", "wired", "patched") used in
mid-coding narration ("I added a guard to handle the empty case") do NOT trigger
this gate — they fired 19 false positives in 24h before the narrowing.

**Enforcement:** `core/contracts.py:CompletionArtifactContract.check_post()` —
`_DONE_WITH_WORK` regex (closure-signal only), `_PUSH_DONE` (past-tense commit
framing), `_RUN_PATH` (cited test/file paths). Dirty-worktree state injected by
`core/contract_guard.py:_dirty_worktree()` which already excludes
`memory/` and `state/` prefixes.

**Recovery:**
- Check A: Stat every cited path before claiming you ran it. Either create the
  file and run it for real, or remove the claim.
- Check B: Run `git rev-parse HEAD` after pushing, cite the actual hash.
- Check C: Commit the dirty paths before claiming closure. Or rephrase: "the
  guard is drafted but remains uncommitted" passes.

**Escalation:** None. Block silently and let the model retry. Real completion
claims always have an artifact; this contract just makes that structurally
inescapable.
