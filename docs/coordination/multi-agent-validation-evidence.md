# Multi-Agent Validation Evidence

Date: 2026-05-27
Status: M25 read-only validation evidence gate

## Purpose

This package captures the M24 preflight validation plan as auditable command evidence before pathspec staging. It does not stage, commit, push, merge, self-approve, or write to Notion.

The packet answers three questions:

1. Did the 19 validation commands actually run?
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
3. `ultrawork-monitor`
4. `m22-operator-cockpit`
5. `m23-packaging-consolidation`
6. `m24-pr-preflight`
7. `m25-validation-evidence`

The generated artifact contains 19 validation commands, 19 command results, 8 explicit stage commands, and a PR evidence note. The UltraWork package keeps a separate `git add -f -- ...` command for ignored `.claude/agents/*` files.

## Excluded Dirty Context

Do not stage these paths from this evidence package:

```text
.github/workflows/gsd-automation.yml
artifacts/**
src/well_harness/controller.py
src/well_harness/runner.py
src/well_harness/demo_server.py
src/well_harness/requirements_intake/**
src/well_harness/static/**
tests/test_demo.py
tests/test_requirements_intake_webui.py
tests/test_validation_suite.py
tools/run_gsd_validation_suite.py
.planning/**
```

## Notion Blocker

`notion-control-plane-404` remains an external control-plane blocker. This evidence package must not change Notion configuration or rewrite the blocker as a local code failure.

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

Browser gate: open the generated HTML and verify it shows `Multi-Agent Validation Evidence`, `multi-agent-cursor-baseline-v0-2-01`, `m24-pr-preflight-03`, `m25-validation-evidence`, `notion-control-plane-404`, and `19 validation commands passed` without desktop or mobile layout overflow.
