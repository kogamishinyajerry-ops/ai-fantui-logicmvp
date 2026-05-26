# Workbench Phase 12 Handoff — Packaging Boundary And Gates

Date: 2026-05-27
Worktree: `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`
Branch: `codex/goal-canvas-panel`
Mode: packaging slice, no new product behavior

## Goal

Phase 12 packages the current `/workbench` Canvas line into a reviewable boundary:

1. Review tracked implementation diff.
2. Review untracked docs/artifacts.
3. Decide what belongs in a future commit/PR and what stays local-only.
4. Run full validation suite.
5. Refresh browser screenshot/geometry evidence.

## Tracked Diff Review

Tracked implementation diff currently covers 9 files:

- `docs/json_schema/editable_control_model_v1.schema.json`
- `src/well_harness/editable_control_model.py`
- `src/well_harness/editable_workbench_run.py`
- `src/well_harness/static/workbench.css`
- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.js`
- `tests/e2e/test_workbench_js_boot_smoke.py`
- `tests/test_jer165_ui_draft_canonical_model.py`
- `tests/test_workbench_editable_canvas_shell.py`

Packaging assessment:

- Keep these together as one implementation candidate. They form one coherent
  `/workbench` Canvas package: UI primitive support, workbench display polish,
  archive semantics, and corresponding unit/static/e2e coverage.
- Do not split schema/model changes from UI changes unless a reviewer explicitly
  asks for a smaller PR. The schema/model changes explain why UI catalog
  primitives such as `input`, `output`, `compare`, and `between` can run through
  the sandbox path instead of failing as invalid model input.
- Keep the archive semantics e2e in the same candidate package because it locks
  the honest distinction between sandbox diff evidence and scenario test bench
  evidence.

## Untracked Docs Review

Recommended to include in a future commit/PR:

- `docs/coordination/project-takeover-blueprint-20260527.md`
- `docs/coordination/workbench-phase11-takeover-archive-semantics-handoff.md`
- `docs/coordination/workbench-phase12-packaging-slice-handoff.md`

Recommended to keep local-only unless the reviewer asks for full construction history:

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
- `docs/coordination/workbench-phase10-secondary-status-localization-handoff.md`
- `docs/coordination/workbench-ux-audit-optimization-plan.md`
- `docs/coordination/goal-canvas-panel-minimal-demo-handoff.md`

Reason: these are useful development history, but too noisy for the primary
review package. The Phase 11/12 docs already summarize them.

Existing tracked PR handoff docs:

- `docs/coordination/workbench-goal-canvas-panel-pr-ready-handoff.md`
- `docs/coordination/workbench-goal-canvas-panel-pr-evidence-manifest.md`

These are older 2026-05-06 PR-ready notes. Treat them as historical references
unless they are refreshed in a dedicated packaging update. The current submit
boundary in this slice is the explicit pathspec below.

## Artifact Review

Recommended to include or refresh as curated visual evidence:

- `artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json`
- `artifacts/workbench-phase10-status-localization/desktop-workbench-status-localization.png`
- `artifacts/workbench-phase10-status-localization/desktop-status-localization-metrics.json`

Recommended to keep local-only:

- `artifacts/agent-usability/`

Reason: `artifacts/agent-usability/` is a broad exploratory probe bundle
containing 154 files and about 28 MB of screenshots/scripts/archive drafts.
It is useful for local diagnosis, but too large and noisy for the submit
boundary.

Already excluded by `.gitignore`:

- `artifacts/workbench-goal-canvas-panel/current-user-complaint.png`

## Proposed Commit Boundary

Use explicit paths, not `git add -A`:

```bash
git add \
  docs/json_schema/editable_control_model_v1.schema.json \
  src/well_harness/editable_control_model.py \
  src/well_harness/editable_workbench_run.py \
  src/well_harness/static/workbench.css \
  src/well_harness/static/workbench.html \
  src/well_harness/static/workbench.js \
  tests/e2e/test_workbench_js_boot_smoke.py \
  tests/test_jer165_ui_draft_canonical_model.py \
  tests/test_workbench_editable_canvas_shell.py \
  docs/coordination/project-takeover-blueprint-20260527.md \
  docs/coordination/workbench-phase11-takeover-archive-semantics-handoff.md \
  docs/coordination/workbench-phase12-packaging-slice-handoff.md \
  artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png \
  artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png \
  artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json \
  artifacts/workbench-phase10-status-localization/desktop-workbench-status-localization.png \
  artifacts/workbench-phase10-status-localization/desktop-status-localization-metrics.json
```

## Validation Suite

Command:

```bash
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json
```

Fresh result:

- Overall suite status: `fail`.
- `command_count`: 25.
- `completed_commands`: 25.
- First/only failed check: `notion_control_plane`.
- Failure kind: `exit_code`.
- Local/code checks before Notion passed, including `unit_tests`.
- `unit_tests` command: `python3 -m pytest tests/ -q --tb=no`.
- `unit_tests` duration: `335.008s`.
- Notion failure command: `python3 tools/validate_notion_control_plane.py --format json`.
- Notion failure reason: `HTTP 404`.
- Notion failure detail: Notion returned `object_not_found` for page
  `33cc6894-2bed-8148-b2c5-ec68c440f5ef`, with message that the page/database
  may not be shared with the integration `Claude Dev Workflow`.

Phase 12 classification: this blocks a full green validation claim, but it is
an external/control-plane configuration or Notion content-access failure, not a
fresh `/workbench` implementation regression.

## Notion 404 Gate Handling

Phase 12 used the Notion connector to check whether the failed object can be
recovered from the external control plane.

Result:

- Exact fetch for configured `pages.constitution`
  (`33cc6894-2bed-8148-b2c5-ec68c440f5ef`) returned
  `NOT_FOUND/object_not_found`, matching the local validation suite failure.
- The configured dashboard/root page
  (`33cc6894-2bed-8136-b5c9-f9ba5b4b44ec`) is still accessible.
- The configured Roadmap database
  (`33cc6894-2bed-810a-a2ea-e4f095b44afa`) is still accessible.
- Exact fetch for configured `pages.control_plane`
  (`33cc6894-2bed-810d-875e-e4e0e464ee31`) also returned
  `NOT_FOUND/object_not_found`.
- Workspace search finds links that still point at the old `00 项目宪法` URL,
  but it did not surface an accessible same-object replacement for the
  configured `pages.constitution` ID.
- Search also surfaced adjacent project/governance pages, but they are not
  safe substitutes for this repo's configured control-plane object without an
  explicit control-plane migration decision.

Classification: external control-plane blocker. This slice does not change
`.planning/notion_control_plane.json` and does not create a replacement Notion
page. The full suite remains non-green until the Notion objects are restored,
shared with the active integration, or intentionally migrated in a separate
control-plane maintenance slice.

## Post-Main Merge Validation Refresh

After PR #268 was opened, `origin/main` advanced and GitHub reported the PR as
conflicting. The branch was updated by merging `origin/main` into
`codex/goal-canvas-panel`.

Merge conflict resolution:

- Conflicts were limited to:
  - `src/well_harness/static/workbench.css`
  - `src/well_harness/static/workbench.html`
  - `src/well_harness/static/workbench.js`
- Resolution kept mainline subsystem workflow / restore-checklist updates and
  retained the goal-canvas archive/status behavior from this slice.
- Goal-canvas screenshot and geometry evidence was refreshed after the merge.

Post-merge focused validation:

- `node --check src/well_harness/static/workbench.js` -> pass.
- `python3 -m py_compile tools/validate_notion_control_plane.py tools/run_gsd_validation_suite.py` -> pass.
- `PYTHONPATH=src:. python3 -m pytest -q tests/test_workbench_editable_canvas_shell.py tests/test_jer165_ui_draft_canonical_model.py` -> `72 passed`.
- `PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "goal_canvas_panel_geometry_evidence or review_archive_restore_v3_round_trips_regression_bundle"` -> `2 passed, 65 deselected`.
- `git diff --check` and `git diff --cached --check` -> pass.

Post-merge full validation:

- `PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json` -> `status: fail`.
- `command_count`: `25`.
- `completed_commands`: `25`.
- `unit_tests`: pass; `python3 -m pytest tests/ -q --tb=no`; duration `327.889s`.
- First/only failed check: `notion_control_plane`.
- Notion failure reason remains `HTTP 404` for configured `pages.constitution`
  (`33cc6894-2bed-8148-b2c5-ec68c440f5ef`), with Notion request id
  `012d0434-20f1-40dc-8751-21e00e07b121`.

Post-merge GitHub state:

- PR #268 became `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`.
- GitHub `audit-gate` reported `SKIPPED`, so it is not counted as a green
  validation signal.

## Browser Screenshot / Geometry Gate

Command:

```bash
PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "goal_canvas_panel_geometry_evidence"
```

Expected refreshed artifacts:

- `artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json`

Fresh result:

- `PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "goal_canvas_panel_geometry_evidence"` -> `1 passed, 62 deselected`.
- Refreshed screenshots:
  - `artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png`
  - `artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png`
- Geometry evidence stayed stable in
  `artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json`.
  Key values:
  - desktop viewport `1440x980`, canvas `1356.8125x828.15625`, node count `3`, port handle count `6`.
  - narrow viewport `390x920`, canvas `311.625x730.171875`, node count `3`, port handle count `6`.

## Stop / Do Not Claim

- Do not claim branch closure until the full validation suite is pass or its
  failure is explicitly classified as external/non-goal.
- Do not claim PR-ready until the proposed commit boundary is staged/reviewed
  or intentionally accepted as a pathspec.
- Do not include `artifacts/agent-usability/` by default.
- Do not promote sandbox evidence to controller truth.

## Next Recommended Step

After Phase 12, either:

1. Stage only the proposed boundary and prepare a PR/commit summary, or
2. Run a cleanup slice that archives/removes local-only Phase 1-10 process docs
   and `agent-usability` artifacts outside the source diff.
