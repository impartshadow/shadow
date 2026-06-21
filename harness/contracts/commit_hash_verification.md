# Contract: commit-hash-verification

## Type
Post-response gate — deterministic enforcement via
`core/contracts.py:CommitHashVerificationContract`. Severity: `block`.

## Failure mode
FM-027 — fabricated completion claim. A response cites a commit SHA in
commit/push language but the SHA does not resolve via `git cat-file`.

## Threat model
Shadow's worst completion failures historically were not bad commits — they
were *invented* commits. The 2026-05-29 `experience_reindex` incident shipped
"Applied and pushed. Verified atomicity with pytest tests/test_experience_migration.py"
with a hash (`3821fc0`) and test path that both did not exist. the user trusts
"pushed" claims as scaffolding for the next step; trusting a fabrication
contaminates downstream work.

This contract makes citing a fake SHA structurally impossible by validating
every commit-language-adjacent hex token against the local git object store
before the response can ship.

## Trigger
A response is scanned when:
1. The response text length is ≥ 10 chars, AND
2. It contains commit/push language (`commit`, `committed`, `pushed`, `push`,
   `shipped`, `landed`, `sha`, `HEAD`).

When triggered, every 7-40 char lowercase-hex token that appears in one of
these contexts is treated as a candidate commit SHA:
- Backtick-wrapped: `` `<hex>` ``
- Adjacent to commit language: `commit <hex>`, `HEAD at <hex>`, `pushed <hex>`,
  `<hex> landed`, `<hex> is live`, etc.

Pure-decimal tokens (e.g. 9-digit Substack post IDs) are excluded — real short
hashes effectively always carry a hex letter, and the decimal carve-out
removes the highest-rate false-positive class without weakening the
fabricated-hash catch.

## Enforcement
Each candidate SHA is resolved via `git cat-file -t <sha>`. The check passes
only if `returncode == 0` AND `stdout.strip() == "commit"`. Anything else —
nonexistent object, non-commit object (tree/blob), git not available —
unresolves the SHA.

A SHA is checked against the Shadow repo first, then against the sibling
repos Shadow legitimately operates in (`/home/agentshadow/agent-gateway`,
`/home/agentshadow/agent-contracts`). A hash that resolves in any of them
is real, not fabricated — this prevents false fires when Shadow reports
push receipts for the open-source spinoff repos (4-hit burst on
2026-06-20 against real `agent-contracts` HEAD hashes was the trigger).

If git itself raises (subprocess failure, timeout), the check returns `None`
rather than blocking. Infrastructure failure must not gate generation.

## Recovery
Run the commit for real and cite the actual hash from `git rev-parse HEAD`,
or remove the commit citation entirely. Never paraphrase a remembered SHA —
always re-derive from the working tree.

## Relationship to other contracts
- `completion-artifact` Check B catches push/commit completion language with
  NO hex token at all. Together they make a fabricated "Done" structurally
  un-emittable: either you cite a SHA (then this contract validates it
  exists) or you cite no SHA (then completion-artifact blocks the bare
  completion claim).
- `claim-verification` audits the *diff* of a real commit. It is blind to a
  fully fabricated hash — closing that gap is the sole purpose of this
  contract.

## Escalation
Block is sufficient — the recovery is to run the actual git command. Do not
escalate to the user. Recurring violations within a single session indicate
context contamination from an earlier fake hash; clear the contaminated
buffer (re-read git log) before retrying the response.

## Recent activity
8 violations in 4h on 2026-06-14 — fake hashes `28404c9` (Coinbase CDP, 3 hits
00:55–00:59), `207796e` (Coinbase CDP, 1 hit 01:48), `7e040ed` (Shadow Kit, 3
hits 03:45–03:56), `b8ea668` + `a8dec41…` (Shadow Kit, same 03:53–03:56 burst).
Second burst 2026-06-14 12:24–13:48 (6 more hits): fake hashes `9d74091`,
`d2e107a`, `f059e72` cited as push receipts during research/distribution
sessions. All within-session hallucinations on push-receipt language; contract
caught every instance. Pattern is regenerating across sessions, so the upstream
rule was promoted to CLAUDE.md #29 (2026-06-14): commit hashes must be the
literal `git rev-parse HEAD` output, never a remembered short hash.
