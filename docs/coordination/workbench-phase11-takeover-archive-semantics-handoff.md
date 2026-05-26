# Workbench Phase 11 Handoff — Takeover And Archive Semantics

Date: 2026-05-27
Worktree: `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`
Branch: `codex/goal-canvas-panel`
Mode: takeover closeout, no controller-truth change

## 做了什么

- 接手并收口当前 `/workbench` Canvas 主线，建立本地可恢复入口：
  `docs/coordination/project-takeover-blueprint-20260527.md`。
- 将 Phase 1-10 的工作状态压缩成一个可继续开发的 Phase 11 边界：
  Canvas-first、inspector modes、参考图首屏、新手指引、reference visual、
  guide collapse、canvas-dominant pan/zoom、reference readability、中文节点/连线、
  二级状态中文化。
- 明确当前主线判断：`goal-canvas-panel` 是当前 `/workbench` 静态工作台候选线；
  `requirements-intake-webui` / M21 线保留为历史证据和交付包装上下文，不应直接覆盖
  `/workbench` Canvas 主线。
- 保留并说明 archive semantics repair：
  - `run_sandbox` 代表 sandbox diff evidence，可从 `diff_summary` 判定 pass/fail。
  - `run_scenario_tests` 代表 scenario test bench evidence，应独立引用
    `sandbox_test_run_report`。
  - 当用户只运行 sandbox diff 而未运行 scenario test bench 时，archive 可以诚实记录
    `run_sandbox: pass` 与 `run_scenario_tests: not_run`，而不是把两者混成一个通过项。
- 保留 Phase 10 的合同边界：可见文本中文化，但 `data-*`、JSON、archive、schema enum
  继续使用原始英文合同值。

## 没做什么

- 未修改 `src/well_harness/controller.py`、adapter、certified YAML、public schema、
  CLI contract、HTTP endpoint contract 或持久化 archive 格式。
- 未新增依赖、前端框架、数据库、云同步、协作/权限系统或认证声明。
- 未清理、回滚或重排当前工作树里的既有 Phase 1-10 dirty/untracked 产物。
- 未声明 production-ready、cloud-ready、certification-ready、full e2e green 或 full mypy clean。
- 未启动新的视觉 redesign；Phase 11 只做接手收口和证据语义硬化。

## 当前 changed-file 集

当前 tracked implementation diff 覆盖：

- `docs/json_schema/editable_control_model_v1.schema.json`
- `src/well_harness/editable_control_model.py`
- `src/well_harness/editable_workbench_run.py`
- `src/well_harness/static/workbench.css`
- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.js`
- `tests/e2e/test_workbench_js_boot_smoke.py`
- `tests/test_jer165_ui_draft_canonical_model.py`
- `tests/test_workbench_editable_canvas_shell.py`

当前 untracked handoff/docs/artifacts 包括本文件、Phase 1-10 handoff/goal 文档、
`project-takeover-blueprint-20260527.md`、`artifacts/agent-usability/`、
`artifacts/workbench-phase10-status-localization/` 等。后续 PR 前必须决定这些产物是提交、
拆分、归档还是清理。

## Archive Semantics Contract

Phase 11 认可的最小合同如下：

- Archive 中的 `diff_summary` 是 sandbox diff run 的证据源。
- Archive 中的 `sandbox_test_run_report` 是 scenario test bench 的证据源。
- Archive 中的 `sandbox_runner_trace_kernel` 可以由真实 test bench 运行产生；如果未运行，
  必须生成结构化 `not_run` kernel，而不是缺失关键 section。
- `review_archive_regression_bundle_v3.regression_steps` 必须区分：
  - `step_id: "run_sandbox"` with `evidence_key: "diff_summary"`
  - `step_id: "run_scenario_tests"` with `evidence_key: "sandbox_test_run_report"`
- `red_line_metadata.controller_truth_modified` 必须保持 `false`。
- `truth_effect` 必须保持 `none`；Phase 11 不允许 truth promotion。

## Verification Commands

Fresh Phase 11 verification commands:

```bash
node --check src/well_harness/static/workbench.js
PYTHONPATH=src:. python3 -m pytest -q tests/test_workbench_editable_canvas_shell.py -k "phase10_secondary_status or cockpit_editor"
PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "archive_after_sandbox_run_has_structured_not_run_test_sections or candidate_debugger_view_tracks_failing_assertion_and_archive or preflight_analyzer_classifies_failed_candidate_and_archives"
git diff --check
```

## Verification Results

- `node --check src/well_harness/static/workbench.js` -> pass.
- `PYTHONPATH=src:. python3 -m pytest -q tests/test_workbench_editable_canvas_shell.py -k "phase10_secondary_status or cockpit_editor"` -> `3 passed, 57 deselected`.
- `PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "archive_after_sandbox_run_has_structured_not_run_test_sections or candidate_debugger_view_tracks_failing_assertion_and_archive or preflight_analyzer_classifies_failed_candidate_and_archives"` -> `3 passed, 60 deselected`.
- `git diff --check` -> pass.

## Risks / Unresolved Issues

- 当前分支不是 clean branch；它包含多阶段累计差异。不要在未审阅 changed-file 集前直接声明
  PR-ready。
- 旧 workspace routing 文档和当前 `/workbench` 蓝图存在时间差。后续继续时应先读
  `project-takeover-blueprint-20260527.md`，再核对 live worktree state。
- 完整 validation suite 本阶段尚未作为收口 gate 跑完；若要声明 branch closure，需要重跑
  `tools/run_gsd_validation_suite.py --format json` 并记录 Notion 控制面状态。
- 参考图仍需要产品判断：它到底是 source-backed full C919 E-TRAS graph，还是
  thrust-reverser/reference fragment。没有 source-backed graph 时，UI 文案必须保持诚实。

## Next Recommended Step

下一步不要立刻开新 UI 大改。先做 Phase 12 packaging slice：

1. 审阅 tracked diff 和 untracked docs/artifacts。
2. 决定哪些 Phase 1-11 handoff 文档进入提交，哪些只作为本地证据归档。
3. 如需 PR，先跑完整 validation suite 和一个浏览器截图/geometry gate。
4. 再选择后续功能方向：reference graph source-backed completeness、icon rail/inspector polish、
   或 archive/package PR-readiness。
