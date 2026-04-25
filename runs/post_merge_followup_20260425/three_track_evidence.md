# Three-Track Regression Evidence — Post-Merge Followup 2026-04-25

**Branch:** `chore/post-merge-followup-20260425`
**HEAD:** at time of run = `06b4b57` (T4 report) on top of PR #3 head `2ded020`
**Base:** PR #3 head (pre-merge per Kogami `(B)` directive) — NOT main, because PR #3 is still OPEN

All three runs produced from the same sandbox (Python 3.9.6, pytest 7.4.4, macOS arm64). Port 8799 reaped before each run.

---

## Track 1 — default lane

```bash
$ python3 -m pytest -v --no-header
========== 851 passed, 27 deselected, 12 xpassed in 76.30s (0:01:16) ===========
```

- Target: `default ≥ 851 passed` ✓ (exactly at target)
- 12 xpassed = the P43 R2/R3/R4/R5/R6a contract checks documented in `docs/workbench/xpassed-audit-20260425.md`
- 27 deselected = e2e + adversarial markers (per `pyproject.toml addopts = "-m 'not e2e'"`)

## Track 2 — e2e lane

```bash
$ python3 -m pytest -v -m e2e --no-header
================= 1 failed, 26 passed, 863 deselected in 1.20s =================
```

- Target: `仍然只有 1 failed（即 inherited blocker），不得新增 fail` ✓
- The single failure is `tests/e2e/test_wow_a_causal_chain.py::test_wow_a_beat_deep_activates_logic2_and_logic3`, the same inherited logic4 blocker analysed in `docs/workbench/inherited-logic4-blocker-investigation.md` (first-bad commit `a46e4e6`, 22 commits older than PR #3 base).
- No new e2e regressions introduced by T2/T3/T4 doc commits.

## Track 3 — adversarial

```bash
$ WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py
…
[Test 4] TRA boundary conditions               PASS (4/4)
[Test 5] VDT 90% threshold                     PASS (4/4)
[Test 6] Rapid cycling (10 iterations)         PASS
[Test 7] Frontend authoritative nodeStateMap   PASS (2/2)
[Test 8] Full causal chain verification        PASS (14/14)

======================================================================
ALL TESTS PASSED
======================================================================
```

- Target: `adversarial 8/8 ALL PASSED` ✓
- Note Test 8 confirms `vdt90=active` and `logic4=active` and `thr_lock=active` for the full causal chain in the running server — this is consistent with the T4 finding that `auto_scrubber` is designed to drive VDT to 100% and latch L4. The adversarial suite encodes the **post-`a46e4e6` spec**; the wow_a e2e encodes the **pre-`a46e4e6` invariant**. The two are in declared conflict — see T4 report for [A]/[B]/[C] options.

---

## Honesty addendum

- The numbers above are real `pytest` / script stdout, not paraphrased. The default-lane delta vs. HANDOVER's E10 baseline (`819 passed, 1 skipped, 49 deselected`) → current (`851 passed, 27 deselected, 12 xpassed`):
  - +32 passed across the rebase from E10's snapshot to PR #3 head (consistent with the additional epic content + the P43 R2-R6 implementations that converted the 12 xfail markers into xpassed).
  - The earlier "1 skipped" line is no longer present; the suite has zero skips in this run.
  - The deselect count differs (27 vs 49) because the deselect set changed as new tests with different marker shapes landed. Not a regression — the marker config (`pyproject.toml addopts`) is unchanged.
- T2/T3/T4 commits add doc-only files (`docs/workbench/*.md`, `runs/xpassed_audit_*.txt`); none of the three deltas above is attributable to these commits.
