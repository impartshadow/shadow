# Detector Self-Check

**Type:** Contract
**Severity:** blocking (audit exit status)
**Added:** 2026-09-19

## Law

A detector's clean output is a hypothesis, not a receipt, until that detector has
been run against at least one input whose correct verdict is known and wrong.
No audit may report "0 findings" — or have that zero relayed as a status claim —
from a scan it has not just demonstrated can detect.

## Why

2026-09-18: `scripts/contract_law_registry.py` was built to catch docs that claim
enforcement they do not have. It shipped reporting **0 phantom**, and that number
was relayed as a finding. The scan was under-detecting three ways at once; eight
phantom laws were invisible. The whole test suite was green, because every test
asserted about the *live corpus* — and a detector that finds nothing looks
exactly like a corpus that contains nothing.

That is the same failure the registry exists to catch, recurring one layer up in
the verification tool itself: the tool's own output was treated as evidence about
the system rather than a claim requiring verification.

## Enforcement

Code-enforced by `core/detector_selfcheck.py`.

- A detector exposes `selfcheck()` returning `run_selfcheck(name, cases)`, where
  each `KnownBad` is an input whose wrong answer is known. Include known-*good*
  cases too: a detector that flags everything is as useless as one that flags
  nothing, and only a two-sided fixture set catches both.
- `audit()` carries the self-check result; the CLI and every caller must fail
  (not warn) when `validated` is false, before any count is printed or relayed.
  `scripts/contract_law_registry.py` and `scripts/nightly.py`
  (`_run_contract_law_registry`) do this.
- The declared set of detectors — modules defining `audit()` — is ratcheted in
  `harness/detector_selfcheck_baseline.json` by
  `tests/test_detector_selfcheck_registry.py`. Legacy detectors are
  grandfathered; the list may shrink, never grow, so a new detector ships with
  fixtures or fails the suite.
- Fixtures must bite: `tests/test_contract_law_registry.py` mutation-tests the
  registry by restoring each v1 scan bug and asserting the self-check fails.
