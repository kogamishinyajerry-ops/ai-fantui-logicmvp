# Workbench Goal Canvas Panel PR-ready Handoff

Date: 2026-05-06
Worktree: `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`
Branch: `codex/goal-canvas-panel`
Base: `origin/main` / `db2cfe6`

## Current Slice

This slice consolidates the current `/workbench` Canvas panel work into a UI/test/evidence change set.

- Phase 1-9 improved the default `/workbench` first screen into a C919 E-TRAS / thrust-reverser reference control circuit view with Chinese node labels, visible directional wires, compact Simulink-like blocks, canvas-dominant pan/zoom, guide controls, and a collapsed inspector that does not cover the right-side L4 / THR_LOCK chain.
- Phase 10 adds a small UI-display-only cleanup for secondary status summaries: proof/debug/handoff summaries now render status enums through `displayStatusLabel()` so values such as `not_run`, `selection_only`, `evidence_gap`, `run_required`, and `not_archive_ready` appear as Chinese labels in user-facing summary text.
- Phase 11 hardens the repo-local Notion control-plane validation against transient TLS/EOF transport failures. The validator retries explicit transport errors, preserves HTTP/API/config/object-health failures as hard failures, and reports retry exhaustion as `notion_transport_unavailable`.
- Raw JSON/export values are intentionally unchanged. Sandbox invariants remain `truth_effect: "none"`, `candidate_state: "sandbox_candidate"`, and `certification_claim: "none"`.

## Scope Boundaries

Changed tracked files:

- `.gitignore`
- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.css`
- `src/well_harness/static/workbench.js`
- `tests/e2e/test_workbench_js_boot_smoke.py`
- `tests/test_workbench_editable_canvas_shell.py`
- `tests/test_jer178_operation_catalog_palette.py`
- `tests/test_jer181_duplicate_keyboard_editing.py`
- `tests/test_workbench_p44_01_circuit_hero.py`
- `tools/validate_notion_control_plane.py`
- `tests/test_validate_notion_control_plane.py`
- `docs/coordination/workbench-goal-canvas-panel-pr-ready-handoff.md`
- `docs/coordination/workbench-goal-canvas-panel-pr-evidence-manifest.md`

Not touched:

- `src/well_harness/controller.py`
- `src/well_harness/runner.py`
- `src/well_harness/controller_adapter.py`
- `src/well_harness/adapters/`
- Certified YAML, public schemas, CLI contracts, archive/export formats, persistent data formats.

## Artifact Decision

Canonical artifact boundary:

- `docs/coordination/workbench-goal-canvas-panel-pr-evidence-manifest.md`

Recommended to keep as PR evidence:

- `artifacts/workbench-chinese-connected-final.png`
- `artifacts/workbench-chinese-connected-after-fix.png`
- `artifacts/workbench-ux-audit/desktop-default-workbench.png`
- `artifacts/workbench-ux-audit/narrow-default-workbench.png`
- `artifacts/workbench-ux-audit/default-visible-metrics.json`
- `artifacts/workbench-goal-canvas-panel/desktop-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/narrow-goal-canvas-panel.png`
- `artifacts/workbench-goal-canvas-panel/goal-canvas-panel-geometry.json`

Recommended to leave untracked or archive outside the PR:

- `artifacts/workbench-bundles/` validation byproducts.
- `artifacts/workbench-goal-canvas-panel/demo-server-8799.log`.
- Intermediate complaint/inspection screenshots unless the PR body explicitly references them.

## Verification

Fresh PR-ready checks:

- `python3 -m pytest tests/test_workbench_editable_canvas_shell.py::test_phase10_secondary_status_summaries_use_chinese_display_labels -q` -> `1 passed`.
- `node --check src/well_harness/static/workbench.js` -> exit 0.
- `python3 -m pytest tests/test_workbench_editable_canvas_shell.py tests/test_workbench_p44_01_circuit_hero.py tests/test_jer178_operation_catalog_palette.py tests/test_jer181_duplicate_keyboard_editing.py -q` -> `116 passed`.
- `python3 -m pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py::test_workbench_reference_first_screen_is_chinese_connected_and_uncovered tests/e2e/test_workbench_js_boot_smoke.py::test_workbench_reference_graph_is_connected_named_and_guide_discoverable tests/e2e/test_workbench_js_boot_smoke.py::test_workbench_canvas_dominates_viewport_and_direct_pan_zoom_tracks_mouse -q` -> `3 passed`.
- `python3 -m pytest tests/test_validate_notion_control_plane.py tests/test_validation_suite.py -q` -> `21 passed`.
- `python3 -m py_compile tools/validate_notion_control_plane.py` -> exit 0.
- `python3 tools/validate_notion_control_plane.py --format json` -> `status: pass`, checked 7 pages, 10 databases, and 2 legacy artifacts; `degraded_page_keys=["opus_brief"]`.
- `python3 tools/run_gsd_validation_suite.py --format json` -> `status: pass`, `command_count: 25`, `completed_commands: 25`, `failed_check: null`; Notion check returned pass with `degraded_page_keys=["opus_brief"]`.

Earlier full-suite evidence before Phase 10:

- `python3 -m pytest -q` -> `3428 passed, 39 skipped, 103 deselected`.
- `python3 tools/run_gsd_validation_suite.py --format json` -> `status: pass`, `command_count: 25`, `completed_commands: 25`, `failed_check: null`; Notion returned pass with `degraded_page_keys=["opus_brief"]`.

## Open Risk

There is no current local verification blocker.

The Notion control plane is reachable with the terminal `NOTION_API_KEY`, but `opus_brief` is still archived/in trash and the validator reports `degraded_page_keys=["opus_brief"]`. Treat this as a control-plane content/IA follow-up, not as evidence of a `/workbench` code regression.

Transient TLS/EOF failures are now retried by `tools/validate_notion_control_plane.py`; if all attempts fail, the script still exits non-zero with `reason="notion_transport_unavailable"`.

## Next Slice

Do not expand into controller truth, certified adapters, YAML, schemas, or new frontend frameworks.

Recommended next development slice:

- Continue UI-display-only Chinese label mapping for lower-priority panels, especially archive/handoff generated text and debug timeline helper summaries.
- Keep raw export JSON fields unchanged.
- Add one focused static or e2e regression per visible display surface.
- Decide whether `opus_brief` should be restored, replaced, or intentionally excluded from active-page degradation.
