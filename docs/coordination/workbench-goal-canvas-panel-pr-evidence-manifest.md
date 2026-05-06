# Workbench Goal Canvas Panel PR Evidence Manifest

Date: 2026-05-06
Worktree: `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`
Branch: `codex/goal-canvas-panel`

## Purpose

This manifest defines the artifact boundary for the current `/workbench` Canvas panel PR. It keeps the PR evidence small and reviewable while preserving local validation byproducts outside the source diff.

## Add To PR

Primary visual and geometry evidence:

- `artifacts/workbench-chinese-connected-final.png`
- `artifacts/workbench-chinese-connected-after-fix.png`
- `artifacts/workbench-ux-audit/desktop-default-workbench.png`
- `artifacts/workbench-ux-audit/narrow-default-workbench.png`
- `artifacts/workbench-ux-audit/default-visible-metrics.json`
- `artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json`

Primary coordination docs:

- `docs/coordination/workbench-goal-canvas-panel-pr-ready-handoff.md`
- `docs/coordination/workbench-goal-canvas-panel-pr-evidence-manifest.md`

Optional secondary context, add only when the PR body explicitly references the demo handoff:

- `docs/coordination/goal-canvas-panel-minimal-demo-handoff.md`

## Keep Out Of PR By Default

Phase process docs are useful local history, but they are too noisy for the main PR unless a reviewer asks for the implementation timeline:

- `docs/coordination/workbench-phase1-canvas-first-goal.md`
- `docs/coordination/workbench-phase1-canvas-first-handoff.md`
- `docs/coordination/workbench-phase2-inspector-modes-goal.md`
- `docs/coordination/workbench-phase2-inspector-modes-handoff.md`
- `docs/coordination/workbench-phase3-reference-circuit-first-screen-goal.md`
- `docs/coordination/workbench-phase3-reference-circuit-first-screen-handoff.md`
- `docs/coordination/workbench-phase4-onboarding-guide-goal.md`
- `docs/coordination/workbench-phase4-onboarding-guide-handoff.md`
- `docs/coordination/workbench-phase5-reference-visual-and-outsider-tutorial-goal.md`
- `docs/coordination/workbench-phase5-reference-visual-and-outsider-tutorial-handoff.md`
- `docs/coordination/workbench-phase6-guide-collapse-and-canvas-visibility-handoff.md`
- `docs/coordination/workbench-phase7-canvas-dominant-panzoom-handoff.md`
- `docs/coordination/workbench-phase8-reference-readability-handoff.md`
- `docs/coordination/workbench-phase9-chinese-connected-wire-handoff.md`
- `docs/coordination/workbench-ux-audit-optimization-plan.md`

Generated validation bundles and runtime logs:

- `artifacts/workbench-bundles/`
- `artifacts/workbench-goal-canvas-panel/demo-server-8799.log`

Process-only screenshots now ignored by exact path:

- `artifacts/workbench-current-complaint-inspect.png`
- `artifacts/workbench-goal-canvas-panel/current-user-complaint.png`

## Recommended Add Command

Use explicit paths rather than `git add -A`:

```bash
git add \
  .gitignore \
  src/well_harness/static/workbench.html \
  src/well_harness/static/workbench.css \
  src/well_harness/static/workbench.js \
  tests/e2e/test_workbench_js_boot_smoke.py \
  tests/test_jer178_operation_catalog_palette.py \
  tests/test_jer181_duplicate_keyboard_editing.py \
  tests/test_validate_notion_control_plane.py \
  tests/test_workbench_editable_canvas_shell.py \
  tests/test_workbench_p44_01_circuit_hero.py \
  tools/validate_notion_control_plane.py \
  docs/coordination/workbench-goal-canvas-panel-pr-ready-handoff.md \
  docs/coordination/workbench-goal-canvas-panel-pr-evidence-manifest.md \
  artifacts/workbench-chinese-connected-final.png \
  artifacts/workbench-chinese-connected-after-fix.png \
  artifacts/workbench-ux-audit/desktop-default-workbench.png \
  artifacts/workbench-ux-audit/narrow-default-workbench.png \
  artifacts/workbench-ux-audit/default-visible-metrics.json \
  artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png \
  artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png \
  artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json
```

## Verification Evidence

Latest validation recorded for this PR-ready state:

- `python3 -m pytest tests/test_validate_notion_control_plane.py tests/test_validation_suite.py -q` -> `21 passed`
- `python3 tools/validate_notion_control_plane.py --format json` -> `status: pass`, `degraded_page_keys=["opus_brief"]`
- `python3 tools/run_gsd_validation_suite.py --format json` -> `status: pass`, `command_count: 25`, `completed_commands: 25`, `failed_check: null`
- `git diff --check` -> pass
