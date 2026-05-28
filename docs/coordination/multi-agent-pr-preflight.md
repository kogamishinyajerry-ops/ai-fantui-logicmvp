# Multi-Agent PR Preflight

Date: 2026-05-27
Status: M24 read-only validation and PR body gate

## Purpose

This package turns the M23 explicit pathspec boundary into a PR-ready preflight packet. It does not stage, commit, push, merge, self-approve, or write to external planning systems.

The packet answers three questions:

1. Which validation commands must be run before staging?
2. Which exact pathspec commands should be used after validation?
3. Which PR body text preserves the repo/GitHub/local artifact boundary and dirty-worktree boundary?

## Local Entry

```sh
make multi-agent-pr-preflight
```

Default output:

```text
/tmp/ai-fantui-multi-agent-pr-preflight/multi_agent_pr_preflight_v0_1.html
```

Verifier:

```sh
make verify-multi-agent-pr-preflight
```

The verifier opens the generated HTML in desktop and mobile browser viewports,
captures screenshots, and fails on missing required labels or horizontal page
overflow. Unit tests can keep the browser path disabled with
`--skip-browser`; the Makefile gate keeps the browser check enabled.

## Package Order

1. `multi-agent-cursor-baseline-v0-2`
2. `project-manager-status`
3. `candidate-review-runtime-export`
4. `ultrawork-monitor`
5. `m22-operator-cockpit`
6. `m23-packaging-consolidation`
7. `m24-pr-preflight`

The generated artifact contains 21 validation commands, 8 explicit stage commands, and the copy-ready PR body. The UltraWork package keeps a separate `git add -f -- ...` command for ignored `.claude/agents/*` files.

## Excluded Dirty Context

Do not stage these paths from this preflight package:

```text
.github/workflows/gsd-automation.yml
artifacts/**
src/well_harness/controller.py
src/well_harness/runner.py
src/well_harness/requirements_intake/**
src/well_harness/static/**
tests/test_demo.py
tests/test_requirements_intake_webui.py
tests/test_validation_suite.py
tools/run_gsd_validation_suite.py
.planning/**
```

## Control-Plane Boundary

Repo/GitHub/local artifacts are the active control surfaces for this preflight package. External planning systems are outside the blocking validation path.

## Verification

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_pr_preflight.py \
  scripts/run_multi_agent_pr_preflight.py \
  scripts/verify_multi_agent_pr_preflight.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_pr_preflight.py

make multi-agent-pr-preflight

make verify-multi-agent-pr-preflight
```

Browser gate: open the generated HTML and verify it shows `Multi-Agent PR Preflight`, `multi-agent-cursor-baseline-v0-2`, `ultrawork-monitor`, `m23-packaging-consolidation`, `repo-github-local-artifacts`, and `git add -f --` with desktop/mobile screenshots and no horizontal layout overflow.
