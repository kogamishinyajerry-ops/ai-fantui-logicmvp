# UltraWork Monitor Pathspec Package

## Purpose

This package adds a read-only local UltraWork Monitor entry for the multi-agent lane without changing controller truth, runtime truth, planning-control configuration, or existing browser routes.

The monitor now exposes a five-agent active team under
`agent_team.mode = five_agent_context_cap`. Legacy queue role labels such as
`EvidenceRepairAgent`, `RequirementRepairAgent`, and `SimulationTestAgent` are
rendered as task categories, not additional live agents.

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
  src/well_harness/multi_agent_team.py \
  src/well_harness/ultrawork_monitor_dashboard.py \
  tests/test_ultrawork_monitor_dashboard.py

git add -f -- \
  .claude/agents/ultrawork-orchestrator.md \
  .claude/agents/ultrawork-logic-ir-agent.md \
  .claude/agents/ultrawork-evidence-reviewer.md
```

## Required Baseline Dependency Boundary

The UltraWork entry renders the current v0.2 multi-agent queue cursor. Before committing this slice, confirm the following direct baseline cursor package is already committed in the target branch or staged in a prior multi-agent package:

```sh
git add -- \
  Makefile \
  docs/coordination/multi-agent-continuation-checkpoint.md \
  docs/json_schema/multi_agent_queue_cursor_state_v0_2.schema.json \
  docs/json_schema/multi_agent_queue_run_ledger_v0_2.schema.json \
  scripts/run_multi_agent_queue_cursor_state_v0_2.py \
  scripts/verify_multi_agent_queue_cursor_state_v0_2.py \
  scripts/run_multi_agent_queue_run_ledger_v0_2.py \
  scripts/verify_multi_agent_queue_run_ledger_v0_2.py \
  src/well_harness/agent_task_contract.py \
  tests/test_agent_task_contract.py \
  tests/test_multi_agent_queue_cursor_state_v0_2.py \
  tests/test_multi_agent_queue_run_ledger_v0_2.py
```

The cursor package also depends on the earlier approved candidate queue v0.9 and agent contract packages. If those files are still untracked in the target branch, package those earlier multi-agent baselines first, then commit the UltraWork Monitor slice.

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

Repo, GitHub, and local artifacts are the active control surfaces for this monitor package. External planning systems are outside the blocking validation path.

## Verification

Run these commands after pathspec staging:

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_team.py \
  src/well_harness/ultrawork_monitor_dashboard.py \
  scripts/run_ultrawork_monitor_dashboard.py \
  scripts/verify_ultrawork_monitor_dashboard.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_ultrawork_monitor_dashboard.py

make ultrawork-monitor-dashboard

make verify-ultrawork-monitor-dashboard
```

Browser gate: `make verify-ultrawork-monitor-dashboard` opens `/tmp/ai-fantui-ultrawork-monitor-dashboard/ultrawork_monitor_dashboard_v0_1.html`, captures desktop/mobile screenshots under `screenshots/`, and verifies the page shows `UltraWork Monitor`, `five_agent_context_cap`, `RUN-QUEUE-011`, `LogicIRRepairAgent`, `PackagingPRReadinessAgent`, and `No active blockers` without page-level horizontal overflow.
