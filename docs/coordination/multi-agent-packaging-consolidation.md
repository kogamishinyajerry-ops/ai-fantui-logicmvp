# Multi-Agent Packaging Consolidation

Date: 2026-05-27
Status: M23 read-only PR boundary gate

## Purpose

This package converts the accumulated multi-agent construction lane into an auditable PR packaging sequence. It does not stage, commit, push, merge, self-approve, or write to Notion.

The package answers one question:

Which explicit pathspec groups must be staged, and in which dependency order, so the multi-agent lane can become a reviewable PR without absorbing unrelated dirty worktree state?

## Local Entry

```sh
make multi-agent-packaging-consolidation
```

Default output:

```text
/tmp/ai-fantui-multi-agent-packaging-consolidation/multi_agent_packaging_consolidation_v0_1.html
```

Verifier:

```sh
make verify-multi-agent-packaging-consolidation
```

## Package Order

1. `multi-agent-cursor-baseline`
2. `project-manager-status`
3. `ultrawork-monitor`
4. `m22-operator-cockpit`
5. `m23-packaging-consolidation`

The generated artifact includes exact `git add -- ...` commands for each package. The UltraWork package also includes a separate `git add -f -- ...` command for ignored `.claude/agents/*` files.

## Excluded Dirty Context

Do not stage these paths from this consolidation package:

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

`notion-control-plane-404` remains an external control-plane blocker. This package must not change Notion configuration or rewrite the blocker as a local code failure.

## Verification

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_packaging_consolidation.py \
  scripts/run_multi_agent_packaging_consolidation.py \
  scripts/verify_multi_agent_packaging_consolidation.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_packaging_consolidation.py

make multi-agent-packaging-consolidation

make verify-multi-agent-packaging-consolidation
```

Browser gate: open the generated HTML and verify it shows `Multi-Agent Packaging Consolidation`, `multi-agent-cursor-baseline`, `ultrawork-monitor`, `m22-operator-cockpit`, and `notion-control-plane-404` without desktop or mobile layout overflow.
