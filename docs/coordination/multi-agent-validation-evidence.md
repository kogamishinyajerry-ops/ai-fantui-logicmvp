# Multi-Agent Validation Evidence

Date: 2026-05-27
Status: M25 read-only validation evidence gate

## Purpose

This package captures the M24 preflight validation plan as auditable command evidence before pathspec staging. It does not stage, commit, push, merge, self-approve, or write to external planning systems.

The packet answers three questions:

1. Did the 21 validation commands actually run?
2. Which commands passed or failed, with bounded output evidence?
3. Which latest explicit pathspec commands should be used after evidence capture?

## Local Entry

```sh
make multi-agent-validation-evidence
```

Default output:

```text
/tmp/ai-fantui-multi-agent-validation-evidence/multi_agent_validation_evidence_v0_1.html
```

Verifier:

```sh
make verify-multi-agent-validation-evidence
```

## Package Order

1. `multi-agent-cursor-baseline-v0-2`
2. `project-manager-status`
3. `candidate-review-runtime-export`
4. `ultrawork-monitor`
5. `m22-operator-cockpit`
6. `m23-packaging-consolidation`
7. `m24-pr-preflight`
8. `m25-validation-evidence`

The generated artifact contains 21 validation commands, 21 command results, 9 explicit stage commands, and a PR evidence note. The UltraWork package keeps a separate `git add -f -- ...` command for ignored `.claude/agents/*` files.

## Excluded Dirty Context

Do not stage these paths from this evidence package:

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

Repo/GitHub/local artifacts are the active control surfaces for this evidence package. External planning systems are outside the blocking validation path.

## Verification

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_validation_evidence.py \
  scripts/run_multi_agent_validation_evidence.py \
  scripts/verify_multi_agent_validation_evidence.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_validation_evidence.py

make multi-agent-validation-evidence

make verify-multi-agent-validation-evidence
```

Browser gate: open the generated HTML and verify it shows `Multi-Agent Validation Evidence`, `multi-agent-cursor-baseline-v0-2-01`, `m24-pr-preflight-03`, `m25-validation-evidence`, `repo-github-local-artifacts`, and `21 validation commands passed` without desktop or mobile layout overflow.
