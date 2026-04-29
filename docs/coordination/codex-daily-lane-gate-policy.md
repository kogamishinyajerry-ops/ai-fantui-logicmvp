# Codex Daily Lane Gate Policy

Date: 2026-04-29
Scope: JER-141 through JER-145 and later Codex Daily Lane PRs until the baseline
blockers are retired.

## Current Enforceable Gates

- Shared validation suite:
  `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`
- Default pytest lane:
  `PYTHONPATH=src python3 -m pytest tests/ -q --tb=no`
- Adversarial lane:
  `PYTHONPATH=src python3 src/well_harness/static/adversarial_test.py`

## Known Baseline Blockers

JER-148 established the current `origin/main` gate truth before M2 hardware
coupling work:

- Shared validation suite: pass, 24/24 commands.
- Default pytest: pass.
- Adversarial: pass, 8/8 cases.
- E2E: blocked by existing `/workbench` network-idle timeouts and the WOW-A
  causal-chain expectation mismatch.
- Mypy strict: blocked by existing package/stub and repo-wide typing errors.

Until the E2E and mypy blockers are fixed in their own scoped issues, Codex
Daily Lane PR descriptions must not claim `e2e 49/49` or `mypy --strict clean`.
They must distinguish pre-existing blockers from the PR's tested delta.

## Red-Line Handling

- `src/well_harness/controller.py` truth semantics stay out of Codex Daily Lane
  implementation slices unless Kogami routes an explicit higher-authority task.
- Frozen adapters and frozen hardware YAML files are read-only.
- Truth-level promotions and DAL-impacting change requests route to the Claude
  Code / Kogami lane.
- Any suspected R1-R5 contact requires explicit PR disclosure and CFDJerry
  review routing before merge.
