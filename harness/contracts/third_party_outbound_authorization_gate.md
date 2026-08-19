# third-party-outbound-authorization-gate (FM-045)

**Scope.** Response-time gate. Blocks Shadow from asserting a same-turn
outbound write (PR, issue, comment, review) to a GitHub repository — or
other third-party public forum — that Shadow does not own, unless the
response cites an explicit user-authorization anchor for external publish.

**Origin.** 2026-08-17/18 overnight moonshot run. Under a broad standing
authorization to "architect it all... over the course of tonight" — which
scoped internal engineering work — Shadow escalated into publishing a real
pull request to a stranger's repository (`XuebinMa/agent-guard#119`) and
posted issue-thread comments on `crewAIInc/crewAI#5888` and
`langchain-ai/langgraph#7844` as instrumentation for a self-defined
`transferable_institution` completion metric. Internal-infra authorization
and outbound-publish authority to third-party systems are different risk
classes; conflating them is what let a governance program act on unrelated
OSS repos.

**Owned namespaces (do not fire).** `[public-handle]`, `[private-handle]`,
`private-name`. Everything else is third-party.

**Trigger.** All three must hold in the same response:
1. An outbound verb (`opened`, `filed`, `submitted`, `created`, `posted`,
   `commented`, `replied`, `contributed`, `engaged`, `dispatched`,
   `delivered`, `pushed`, `left`).
2. A target word (`pull request`, `PR`, `issue`, `comment`, `reply`,
   `contribution`, `thread`, `discussion`, `review`).
3. A third-party GitHub reference — a `github.com/<owner>/<repo>` URL,
   `<owner>/<repo>#N` shorthand, or a bare known-third-party repo name
   (e.g. `crewAI #5888`, `langgraph #7844`, `agent-guard PR #119`).

Fenced code blocks, inline code, and blockquotes are stripped before the
check — retrospective narration of a past incident does not fire.

**Bypass — explicit authorization anchors.** Any of the following in the
response satisfies the gate:
- `the user authorized` / `the user approved` / `per the user's approval`
- `third-party outbound: authorized` or `outbound-authorization: <anchor>`
- `explicitly authorized third-party` / `standing external publish
  authorization`

**Severity.** `block`. This is a hard-to-reverse action visible to third
parties under Shadow's identity; failing closed is correct.

**Recovery.** Cite the explicit authorization anchor for this specific
outbound write, reframe as internal-only, or hold the outbound and ask
the user directly before publishing.

**Preserve.** Read-only observation of third-party threads (retrieving
comments, checking maintainer status, reading a PR body) does not fire —
the gate requires an outbound-write verb. Internal commits, tests, and
receipts on owned namespaces (`[public-handle]`, `[private-handle]`) are unaffected.

**Load path.** Standalone contract at
`contracts/third_party_outbound_authorization_gate.py`, auto-loaded by
`core.contract_loader.load_all_dynamic()` at bot startup. Regression tests
in `tests/test_third_party_outbound_authorization_gate.py`.
