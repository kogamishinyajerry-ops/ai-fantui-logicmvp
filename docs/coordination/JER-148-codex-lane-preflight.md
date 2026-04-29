# JER-148 Codex Daily Lane Preflight

Date: 2026-04-29

## Issue

- Linear: JER-148
- Title: `[project] [L5] [none] [DAL-TBD] Codex lane repo sync and baseline preflight`
- Project: `AI FANTUI LogicMVP - Codex Daily Lane`
- Adapter: project-level
- Truth-level impact: none
- Red lines touched: none

## Worktree

Clean Codex worktree:

- Path: `/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP-codex-daily`
- Branch: `codex/JER-148-preflight`
- Base: `origin/main` at `8ea159e471cd50006430221e4c0e5650a4ad2ff7`
- Status before implementation: `## codex/JER-148-preflight...origin/main`

Original checkout was not modified by this run:

- Path: `/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP`
- Status: `main...origin/main [ahead 23, behind 159]`
- Existing local changes: deleted `.planning/phases/E06-workbench-shell/E06-00-PLAN.md`, deleted `tests/test_workbench_shell.py`, modified `audit/events.jsonl`, untracked `.annotations/`, `.tickets/`, `outputs/history/`

## Baseline Results

| Gate | Command | Result | Notes |
| --- | --- | --- | --- |
| Validation suite | `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json` | PASS | 24/24 checks passed, including `notion_control_plane`. |
| Default pytest | `PYTHONPATH=src python3 -m pytest tests/ -q --tb=no` | PASS | 3153 passed, 39 skipped, 35 deselected in 267.00s. |
| Adversarial | `WELL_HARNESS_PORT=8798 PYTHONPATH=src python3 src/well_harness/static/adversarial_test.py` | PASS | 8/8 adversarial sections passed; temporary server on port 8798 was stopped after the run. |
| E2E | `PYTHONPATH=src python3 -m pytest tests/ -m e2e -q` | FAIL | 27 passed, 8 failed, 3192 deselected. Failures: 7 Playwright `/workbench` `networkidle` timeouts, 1 WOW-A expectation mismatch where early beat activated `logic1` only instead of `logic1` + `logic2`. |
| Mypy strict | `PYTHONPATH=src python3 -m mypy --strict src tests tools` | FAIL | Missing `types-PyYAML` / `types-jsonschema` stubs and duplicate `tools.codex_persona_dispatch` module naming blocked the raw command. |
| Mypy strict with explicit package bases | `PYTHONPATH=src:. python3 -m mypy --strict --explicit-package-bases src tests tools` | FAIL | 4575 existing errors across 298 files; current repo has no checked-in mypy configuration for this full-scope command. |

## Gate Interpretation

- The clean worktree and default validation path are healthy enough to start Codex Daily Lane development from `origin/main`.
- The historical `762+ / 49 / 8/8 / mypy clean` gate is not a direct match for current `origin/main` on 2026-04-29:
  - default pytest has grown to 3153 passing tests with 39 skips and 35 e2e tests deselected;
  - opt-in e2e currently collects 35 tests, not 49, and fails 8 tests;
  - raw mypy strict is not currently a configured green gate in this checkout.
- R1-R5 red-line files were not edited. No frozen adapter, C919 reference packet, or controller truth semantics were touched.

## Next Actions

1. Treat JER-148 as the baseline evidence issue for the Codex lane.
2. Before merging M2 implementation PRs, decide whether to:
   - fix or rebaseline the e2e `/workbench` and WOW-A failures, or
   - keep them as known pre-existing gate blockers while allowing non-UI M2 work with explicit waiver notes.
3. Define the official mypy gate command and dependencies before claiming `mypy --strict clean` on future PRs.
4. Start M2 execution with JER-141 once the PR for this docs-only preflight is reviewed.
