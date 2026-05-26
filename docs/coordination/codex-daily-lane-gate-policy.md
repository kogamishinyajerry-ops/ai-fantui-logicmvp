# Codex Daily Lane Gate Policy

Date: 2026-04-29
Scope: JER-141 through JER-145 and later Codex Daily Lane PRs until the baseline
blockers are retired.

## Current Validation Tiers

Daily Lane validation is tiered. Do not treat every test or proof artifact as a
hard stop.

### Tier 0 Hard Holds

Only these failures must stop daily workbench development immediately:

- controller truth or adapter semantics changed without an explicit
  higher-authority task;
- frozen adapters, certified hardware YAML, or C919 reference packets changed;
- public schema/import/export/archive contracts broken at a repo boundary;
- simulation determinism broken for the same circuit plus the same input trace.

### Tier 1 Daily Warnings

Run focused evidence for the touched surface and disclose failures, but do not
turn these into controller-truth holds unless they reveal a Tier 0 issue:

- Shared validation suite:
  `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`
- Default pytest lane:
  `PYTHONPATH=src python3 -m pytest tests/ -q --tb=no`
- Adversarial lane:
  `PYTHONPATH=src python3 src/well_harness/static/adversarial_test.py`

For narrow workbench/Canvas slices, a targeted pytest/e2e subset plus
`git diff --check` is acceptable daily evidence when the PR explicitly states
that full suite, full e2e, and strict mypy are milestone-only or not claimed.

### Tier 2 Milestone Gates

Full opt-in e2e, full shared validation, strict mypy clean, release manifests,
and Opus/Kogami architecture or UX review are release/maturity gates. They block
release or certification claims, not ordinary sandbox UI iteration, unless a
Tier 0 hard hold is observed.

## JER-228 Validation Suite Isolation

The shared validation suite must fail diagnostically instead of hanging
indefinitely. `tools/run_gsd_validation_suite.py` now applies a default
per-command timeout and exposes isolation controls:

```bash
PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --list-checks
PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --only unit_tests --timeout-seconds 300 --format json
PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --skip unit_tests --continue-on-failure --format json
```

If `unit_tests` times out, the report status is `fail`, `failure_kind` is
`timeout`, `failed_check` names the hung command, and the captured stdout/stderr
tail is retained for follow-up triage. A timeout is not a pass and must not be
hidden in PR proof text. It blocks the current PR only when it is on the touched
surface or exposes a Tier 0 hard hold; otherwise record it as a milestone
blocker/follow-up.

## Clean Worktree Strategy

Workbench v5 and later deep-water slices must start from a fresh worktree based
on current `origin/main`:

```bash
git fetch origin main
git worktree add -b codex/JER-XXX-short-slug \
  "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP-jerXXX-short-slug" origin/main
```

Do not continue feature work from the historical divergent local `main` or from
an older issue worktree. Before implementation and before PR, record:

- `git status --short --branch`;
- `git rev-parse HEAD` and `git rev-parse origin/main`;
- `git diff --name-only origin/main...HEAD` for red-line review.

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
They must distinguish pre-existing blockers from the PR's tested delta. These
are milestone/release blockers, not daily hard holds, unless they identify a
controller-truth, certified-asset, schema-boundary, or simulation-determinism
regression.

## Official Mypy Gate

JER-171 defines the Codex-lane mypy command as:

`PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json`

Install dependencies with `python3 -m pip install -e '.[typecheck]'`.

The wrapper runs:

`python3 -m mypy --strict --explicit-package-bases src tests tools`

Current status on 2026-04-30: blocked, not clean. The observed wrapper report
shows 4692 errors in 322 files across 379 checked source files.
Until that blocker is retired, PRs may attach the wrapper's JSON output as
evidence, but they must not use it as a passing merge gate.

## Red-Line Handling

- `src/well_harness/controller.py` truth semantics stay out of Codex Daily Lane
  implementation slices unless Kogami routes an explicit higher-authority task.
- Frozen adapters and frozen hardware YAML files are read-only.
- Truth-level promotions and DAL-impacting change requests route to the Claude
  Code / Kogami lane.
- Any suspected R1-R5 contact requires explicit PR disclosure and CFDJerry
  review routing before merge.
