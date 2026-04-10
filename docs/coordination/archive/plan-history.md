# Coordination Plan History

这个归档文件保留了 active coordination plan 里旧 Round 的历史正文。当前真值请先看 ../plan.md 顶部的自动同步快照。


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
