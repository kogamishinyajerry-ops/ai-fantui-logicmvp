# Coordination Plan

<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT START -->
## 当前自动同步快照

- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`
- 当前已验证 Plan：`P6-04 用可自动同步状态页旁路旧 archived status 页面`
- 最近成功执行证据：`GitHub GSD automation 24239357493`
- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`
- 当前 Opus 状态：`当前无需 Opus 审查`
- 当前 QA 摘要：`Stable demo baseline remains 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
- 当前结论：当前最高优先级是继续收口控制塔与 freeze/demo packet 的残余漂移，不是再加 demo 功能。
- 当前唯一人工动作：继续自动开发；当前无需手动触发 Opus 4.6。

## 当前关键边界

- `controller.py` 仍然是唯一控制真值。
- 不改 `SimulationRunner` 或现有 HTTP / CLI 契约。
- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。
- Opus 4.6 的主观审查仍然只使用 Notion + GitHub 证据面。

## 当前证据入口

- [Notion 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)
- [01 当前状态（自动同步）](https://www.notion.so/33ec6894-2bed-8169-bb65-feb161fdae6d)
- [09C 当前 Opus 4.6 审查简报](https://www.notion.so/33cc6894-2bed-819a-811c-f19885ee595a)
- [10 Freeze Demo Packet](https://www.notion.so/33ec68942bed8151a0a8ff9a36aa8816)
- [GitHub Repo](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
- [GitHub Actions](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)

## 历史记录说明

- 下方旧轮次记录保留作为历史快照，不再代表当前真值。
<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT END -->

## 当前阶段

Round 92 已完成：direct VDT control + flatter logic board + lower-priority result panels

## 当前判断

- Round 92 已通过指挥侧复核。
- 当前全量回归：`129 tests OK`。
- 左侧控件已从内部实现词修正为更直观的 `VDT 模式 / VDT 反馈` 呈现。
- `VDT90 -> L4 -> THR_LOCK` 现在可在 UI 中完整演示。
- 逻辑主板已改成：
  - 平级流程节点：`SW1 / TLS115 / TLS解锁 / SW2 / 540V / EEC / PLS / PDU / VDT90 / THR_LOCK`
  - 逻辑注释：`L1 / L2 / L3 / L4`
- `当前结论` 保留在逻辑主板附近。
- `结果摘要 / 推理结果 / 原始 JSON 调试` 已下沉到底部次要区域。
- `诊断问答` 继续冻结为次要入口。

## 当前结论

- 当前版本已经更贴近用户要的 cockpit demo 结构。
- 下一步不建议再加功能；只建议做真实浏览器手拖 / 手切换 QA。

## 现场使用建议

启动当前 UI：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770 --open
```

现场演示建议路径：

1. 默认 TRA 位置先讲主板结构。
2. 拖 TRA 讲 `SW1 -> L1 -> SW2 -> L2 -> L3 -> VDT90 -> L4 / THR_LOCK`。
3. 再切条件面板演示：
   - `RA = 6ft`
   - `engine_running = false`
   - `aircraft_on_ground = false`
   - `reverser_inhibited = true`
   - `eec_enable = false`
   - `n1k >= max_n1k_deploy_limit`
4. 最后再打开 `反馈 / 诊断（simplified plant）` 或 `原始 JSON 调试` 解释边界。

## 当前关键事实

- `/api/lever-snapshot` 旧请求 `{tra_deg}` 仍兼容。
- `/api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 保持不变。
- `controller.py` confirmed control truth 未改。
- `SimulationRunner` 未改。
- 未新增第二套 payload、UI-side inference 或控制真值。
- 未把 simplified plant 说成完整实时物理模型。

## 后续原则

- 不改 `controller.py` confirmed truth。
- 不改 `SimulationRunner`、`well_harness demo`、`POST /api/demo`、`well_harness run`。
- 不新增 schema / validator / E2E / runtime dependency / LLM / Node / Vite / Next。
- 本轮优先级是 UI 语义和主视图布局，不是新增功能花样。