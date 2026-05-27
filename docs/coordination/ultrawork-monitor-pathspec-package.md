# UltraWork Monitor Pathspec Package

## Purpose

This package adds a read-only local UltraWork Monitor entry for the multi-agent lane without changing controller truth, runtime truth, Notion control-plane configuration, or existing browser routes.

Local entry:

```sh
make ultrawork-monitor-dashboard
```

The target writes JSON and HTML to `/tmp/ai-fantui-ultrawork-monitor-dashboard` by default and prints the HTML path to open locally.

## UltraWork Slice Pathspec

Stage this slice only with explicit pathspecs:

```sh
git add -- \
  Makefile \
  docs/coordination/ultrawork-monitor-pathspec-package.md \
  docs/json_schema/ultrawork_monitor_dashboard_v0_1.schema.json \
  scripts/run_ultrawork_monitor_dashboard.py \
  scripts/verify_ultrawork_monitor_dashboard.py \
  src/well_harness/ultrawork_monitor_dashboard.py \
  tests/test_ultrawork_monitor_dashboard.py

git add -f -- \
  .claude/agents/ultrawork-orchestrator.md \
  .claude/agents/ultrawork-logic-ir-agent.md \
  .claude/agents/ultrawork-evidence-reviewer.md
```

## Required Baseline Dependency Boundary

The UltraWork entry renders the existing multi-agent queue cursor. Before committing this slice, confirm the following direct baseline cursor package is already committed in the target branch or staged in a prior multi-agent package:

```sh
git add -- \
  docs/json_schema/multi_agent_queue_cursor_state_v0_1.schema.json \
  docs/json_schema/multi_agent_queue_run_ledger_v0_1.schema.json \
  scripts/run_multi_agent_queue_cursor_state.py \
  scripts/verify_multi_agent_queue_cursor_state.py \
  scripts/run_multi_agent_queue_run_ledger.py \
  scripts/verify_multi_agent_queue_run_ledger.py \
  tests/fixtures/multi_agent_queue_cursor_state_ready_to_resume_v0_1.json \
  tests/fixtures/multi_agent_queue_cursor_state_v0_1.json \
  tests/fixtures/multi_agent_queue_run_ledger_v0_1.json \
  tests/test_multi_agent_queue_cursor_state.py \
  tests/test_multi_agent_queue_run_ledger.py
```

The cursor package also depends on the earlier approved candidate queue v0.8 and agent contract packages. If those files are still untracked in the target branch, package those earlier multi-agent baselines first, then commit the UltraWork Monitor slice.

`Makefile` is a shared entrypoint file for the multi-agent lane in this worktree. If the target branch does not already include the earlier multi-agent Makefile expansion, land that baseline first or split the Makefile patch before staging this UltraWork-only slice.

## Excluded Paths

Do not stage these paths for the UltraWork Monitor PR:

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

The Notion 404 remains an external control-plane blocker. This package must not edit Notion configuration, Notion sync scripts, or controller truth.

## Verification

Run these commands after pathspec staging:

```sh
python3 -m py_compile \
  src/well_harness/ultrawork_monitor_dashboard.py \
  scripts/run_ultrawork_monitor_dashboard.py \
  scripts/verify_ultrawork_monitor_dashboard.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_ultrawork_monitor_dashboard.py

make ultrawork-monitor-dashboard

make verify-ultrawork-monitor-dashboard
```

Browser gate: open `/tmp/ai-fantui-ultrawork-monitor-dashboard/ultrawork_monitor_dashboard_v0_1.html` and verify the page shows `UltraWork Monitor`, `RUN-QUEUE-010`, `LogicIRRepairAgent`, and `notion-control-plane-404`.
