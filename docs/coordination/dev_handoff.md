# Dev Handoff

## Round 92：direct VDT control + flatter logic board + lower-priority result panels

### 当前结论

- Round 92 已完成。
- 当前全量回归：`129 tests OK`。
- 已完成三件事：
  - 左侧主控件改成更直观的 `VDT 模式 / VDT 反馈`
  - `L1 / L2 / L3 / L4` 改成附着在主流程节点旁边的逻辑注释
  - `结果摘要 / 推理结果` 下沉到底部次要区域，`当前结论` 留在逻辑主板附近
- 说明：现有代码里 `VDT90` 依旧通过 `deploy_position_percent >= 阈值` 推导；这只是 simplified plant 的实现选择，不是需求文档强制要求用户只能调 `Deploy feedback`

### 当前版本包含

- `反推拉杆`
- 条件面板：
  - `radio_altitude_ft`
  - `engine_running`
  - `aircraft_on_ground`
  - `reverser_inhibited`
  - `eec_enable`
  - `n1k`
  - `max_n1k_deploy_limit`
  - `feedback_mode`
  - `deploy_position_percent`（以 `VDT 反馈` 形式直观呈现）
- 逻辑主板：
  - 平级流程节点：`SW1 / TLS115 / TLS解锁 / SW2 / 540V / EEC / PLS / PDU / VDT90 / THR_LOCK`
  - 逻辑注释：`L1 / L2 / L3 / L4`
- 当前结论（贴近主板）
- 下沉的 `结果摘要 / 推理结果`
- 折叠的 `反馈 / 诊断（simplified plant）`
- 折叠的 `原始 JSON 调试`
- 次要入口 `诊断问答（冻结 / 后续开发）`

### 本轮实现结果

1. 直观 VDT 控件
   - 左侧保留 `feedback_mode`
   - 但用户主要看到的是 `VDT 模式` 和 `VDT 反馈`
   - `>=90%` 明确点亮 `VDT90`
2. 扁平逻辑主板
   - 流程节点保持平级 chip / box
   - `L1 / L2 / L3 / L4` 改成 `logic-note` 注释
   - 不再与 `TLS115 / 540V / EEC / PLS / PDU / THR_LOCK` 同类并列
3. 下沉结果区
   - `lever-result / 当前结论` 移到主板旁
   - `结果摘要 / 推理结果 / 原始 JSON 调试` 下移到底部次要区域
4. 冻结诊断问答
   - summary 改为 `诊断问答（冻结 / 后续开发）`
   - 保留折叠抽屉，不再抢主舞台

### 实现要求

- 优先继续复用现有 `POST /api/lever-snapshot`。
- 旧请求 `{tra_deg}` 必须保持兼容。
- 后端继续复用：
  - `HarnessConfig`
  - `LatchedThrottleSwitches`
  - `SimplifiedDeployPlant`
  - `DeployController.evaluate_with_explain(...)`
  - `DeployController.explain(...)`
- 文案上必须明确：
  - 这仍是 simplified plant feedback
  - 不是新的控制真值
  - 不是完整实时物理仿真

### 已确认保持不变

- `controller.py` confirmed control truth
- `SimulationRunner`
- `POST /api/demo`
- `POST /api/lever-snapshot` 旧请求 `{tra_deg}` 兼容
- `well_harness demo`
- `well_harness demo --format json`
- `well_harness run`

### 现场启动命令

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770 --open
```

## Round 90 开发任务（可选）：cockpit toggle feel and HUD hierarchy polish

### 当前状态

- Round 89 已完成，并通过指挥侧复核。
- 当前 UI 继续保持 **multi-parameter cockpit demo candidate**。
- 当前全量回归：`127 tests OK`。
- Round 89 只做了首屏密度微调，没有修改 endpoint、controller、runner 或交互语义。
- 在 `1440x1100` 左右常见演示窗口中，条件面板现在比之前更早进入首屏。
- 当前已经没有必须立刻处理的 UI 展示阻塞。

### 当前结论

- 如果现在停止开发，可以直接进入现场 demo / 彩排阶段。
- 如果还要继续打磨，最值得做的不是新功能，而是两个极小视觉 polish：
  - 左列 HUD 的字重和层次
  - 条件 toggle 的 cockpit 开关感

### 唯一任务（仅当继续打磨）

只做极小视觉 polish，不新增功能、不改语义。

允许的小改动：

- HUD 标签 / 值的字重、对比度、字号层次
- toggle 的轨道、手柄、active / inactive / focus 状态视觉
- 小范围 spacing / alignment 微调

不允许：

- 新参数
- endpoint 语义变化
- controller truth 修改
- `/api/lever-snapshot` 返回结构变化
- 新功能、新 schema / validator / runtime dependency / E2E / LLM

### 完成后回报

- 是否继续开发，还是直接冻结为 demo candidate
- 如果改了，改了哪些文件
- HUD hierarchy 具体改善了什么
- toggle feel 具体改善了什么
- 是否保持现有 demo / run / `/api/demo` / `/api/lever-snapshot` 行为不变
- 跑了哪些测试

## Round 89 开发任务（可选）：first-screen density polish

### 当前状态

- Round 88 已完成，并通过指挥侧复核。
- 当前 UI 继续保持 **multi-parameter cockpit demo candidate**。
- 当前全量回归：`126 tests OK`。
- Round 88 未修改任何仓库文件。
- 真实 Chrome 首屏已确认当前代码版本包含：
  - `反推拉杆`
  - `条件面板`
  - `逻辑主板`
  - `结果摘要 / 推理结果 / 当前结论`
- live `/api/lever-snapshot` 已覆盖：
  - `TRA=0 / -2 / -7 / -14`
  - `radio_altitude_ft = 6.0`
  - `engine_running = false`
  - `aircraft_on_ground = false`
  - `reverser_inhibited = true`
  - `eec_enable = false`
  - `n1k >= max_n1k_deploy_limit`
- 关键 truth 没有被 UI 误读，尤其 `eec_enable=false` 的 blocker 仍准确落在 `L2: eec_enable`。

### Round 88 的透明边界

- 本轮完成了真实 Chrome 首屏视觉 QA。
- 但没有完成“所有参数组合都在浏览器里手动切换一遍”的纯人工交互验证。
- 原因是开发会话无法物理使用用户鼠标 / 触控板，因此没有把 live endpoint smoke 伪装成 manual interaction QA。

### 当前判断

- 当前版本已经没有必须立刻处理的 UI 展示阻塞。
- 如果现在停止开发，当前版本可以直接作为 multi-parameter cockpit demo candidate 使用。
- 如果还要继续打磨，最值得做的不是新功能，而是首屏垂直密度轻量微调：
  - 在 `1440x1100` 这类常见演示窗口里，让条件面板再多露出一截。
  - 保持 cockpit 感，不退回大表单页。

### 唯一任务（仅当继续打磨）

只做 first-screen density polish，不新增功能。

允许的小改动：

- 首屏 vertical spacing / gap / padding
- HUD / 当前结论 / 条件面板的首屏占比
- toggle / range 的密度和对齐
- 折叠区位置和层级

不允许：

- controller truth 修改
- `/api/lever-snapshot` 语义变更
- 新参数 / 新 endpoint / 新功能
- 新 schema / validator / E2E / runtime dependency
- 将 simplified plant 说成完整实时物理模型

### 完成后回报

- 是否继续开发，还是直接冻结为 demo candidate
- 如果改了，改了哪些文件
- 首屏在 `1440x1100` 下改善了什么
- 是否保持现有 demo / run / `/api/demo` / `/api/lever-snapshot` 行为不变
- 跑了哪些测试

## Round 88 开发任务：browser hand-check for multi-parameter cockpit

### 当前状态

- Round 87 已完成，并通过指挥侧复核。
- 当前全量回归：`126 tests OK`。
- cockpit 已从“只拉 TRA”扩展为“TRA + 条件面板”的受控演示面。
- `/api/lever-snapshot` 旧请求 `{tra_deg}` 仍兼容，同时支持：
  - `radio_altitude_ft`
  - `engine_running`
  - `aircraft_on_ground`
  - `reverser_inhibited`
  - `eec_enable`
  - `n1k`
  - `max_n1k_deploy_limit`
- `SW1 / SW2` 仍由 `TRA + LatchedThrottleSwitches` 推导。
- `TLS / PLS / VDT / deploy position` 在折叠的 `反馈 / 诊断（simplified plant）` 区中展示。
- live 验证已确认：
  - `RA=6ft` -> `logic1` blocked on `radio_altitude_ft`
  - `engine_running=false` -> `logic2/logic3/logic4` blocked
  - `aircraft_on_ground=false` -> `logic2/logic3/logic4` blocked
  - `reverser_inhibited=true` -> `logic1/logic2/logic3` blocked
  - `eec_enable=false` -> `logic2` blocked，但 `logic3` 仍可 active；这是当前 confirmed controller truth
  - `n1k >= max_n1k_deploy_limit` -> `logic3` blocked on `n1k`

### 唯一任务

做一次真实浏览器 hand-check，重点确认“条件面板 + 拉杆 + 逻辑主板”一起工作时是否足够直观、足够像 cockpit，而不是普通表单。

启动：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --open
```

如果默认端口被占用：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8767
```

至少检查：

- 默认条件下 `TRA=0 / -2 / -7 / -14`。
- `RA = 6ft`：是否直观看到 `logic1` 被 `radio_altitude_ft` 卡住。
- `engine_running = false`：是否直观看到 `logic2/logic3/logic4` blocked。
- `aircraft_on_ground = false`：是否直观看到 `logic2/logic3/logic4` blocked。
- `reverser_inhibited = true`：是否直观看到 `logic1/logic2/logic3` blocked。
- `eec_enable = false`：是否清楚显示只卡住 `logic2`，不要误导成 `logic3` 也一定关闭。
- `n1k >= max_n1k_deploy_limit`：是否直观看到 `logic3` blocked on `n1k`。
- `反馈 / 诊断（simplified plant）` 是否仍明确是简化反馈，不是完整实时物理模型。
- `原始 JSON 调试` 和 evidence / risks 是否仍默认折叠。
- `诊断问答` 是否仍为次要入口。

如果真实浏览器 hand-check 没发现阻塞，不要修改代码。

如果发现阻塞，只允许极小 HTML / CSS / JS 修正，例如：

- 条件面板布局 / 密度
- toggle 的 cockpit 感和状态反馈
- blocker 文案清晰度
- `eec_enable=false` 这类容易误解的说明文案

如有代码变更，重新跑：

```bash
PYTHONPATH=src python3 -m unittest tests.test_demo
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

### 硬约束

- 不改 `controller.py` confirmed control truth。
- 不改 `SimulationRunner` 语义。
- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、旧形态 `POST /api/lever-snapshot` 或 `well_harness run`。
- 不新增 Node / Vite / Next、runtime dependency、LLM、schema / validator、browser E2E、截图工具或截图资产。
- 不新增第二套 payload、UI-side inference 或控制真值。
- 不把 simplified plant 说成完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 完成后回报

- 是否完成真实浏览器多参数 hand-check。
- 使用的浏览器、端口、视口。
- 检查了哪些参数组合。
- 是否需要代码修正；如果需要，改了哪些文件。
- 当前 UI 是否继续保持 multi-parameter cockpit demo candidate。
- `eec_enable=false` 的表现和说明是否准确。
- 现有 demo / run / `/api/demo` / `/api/lever-snapshot` 行为是否保持不变。
- 跑了哪些测试或 smoke。

## Round 87 开发任务：multi-parameter cockpit controls

### 当前判断

- 用户反馈正确：当前 cockpit demo 仍然主要只有 TRA 拉杆可调，不足以展示飞机电反推控制逻辑的完整条件链。
- 下一轮不是视觉美化，也不是问答增强，而是在现有反推拉杆 cockpit 上增加“状态条件面板”。
- 目标是用户除 TRA 外，还能调整 RA、发动机/地面状态、反推抑制、EEC enable、N1K / limit，并实时看到 HUD、逻辑主板、当前结论如何变化。

### 当前基线

- 当前全量回归：`124 tests OK`。
- UI 已是 interactive cockpit demo candidate。
- `POST /api/lever-snapshot` 已实现，并复用 `HarnessConfig`、`LatchedThrottleSwitches`、`SimplifiedDeployPlant`、`DeployController.evaluate_with_explain(...)` 与 `DeployController.explain(...)`。
- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。

### 唯一任务

扩展 cockpit UI 和 `/api/lever-snapshot`，增加除 TRA 外的关键输入条件调节能力。

### 必须支持的可调参数

- `radio_altitude_ft`
  - 影响 `logic1`：必须 `< 6ft`。
- `engine_running`
  - 影响 `logic2`、`logic3`、`logic4`。
- `aircraft_on_ground`
  - 影响 `logic2`、`logic3`、`logic4`。
- `reverser_inhibited`
  - 影响 `logic1`、`logic2`、`logic3`。
- `eec_enable`
  - 影响 `logic2`。
- `n1k`
  - 影响 `logic3`：`n1k < max_n1k_deploy_limit`。
- `max_n1k_deploy_limit`
  - 与 `n1k` 一起决定 `logic3` 是否放行。

SW1 / SW2 正常模式下继续由 TRA + `LatchedThrottleSwitches` 推导，不要作为普通用户直接开关。

TLS / PLS / VDT / deploy position 属于 simplified plant feedback / sensor side。如要显示或 override，必须放到高级折叠区，并明确是 feedback / diagnostic assumption，不是完整实时物理仿真。

### 后端要求

扩展现有 `POST /api/lever-snapshot` 请求，保持向后兼容。

旧请求仍必须工作：

```json
{"tra_deg": -7.0}
```

新请求建议：

```json
{
  "tra_deg": -7.0,
  "radio_altitude_ft": 5.0,
  "engine_running": true,
  "aircraft_on_ground": true,
  "reverser_inhibited": false,
  "eec_enable": true,
  "n1k": 35.0,
  "max_n1k_deploy_limit": 60.0
}
```

要求：

- 默认值保持 Round 84/85 行为。
- 数字输入做轻量 parse / clamp；非法输入返回清楚 400 或等价错误。
- 继续复用 `HarnessConfig`、`LatchedThrottleSwitches`、`SimplifiedDeployPlant`、`DeployController.evaluate_with_explain(...)`、`DeployController.explain(...)`。
- 不在 JS 里硬编码 controller 条件。

### UI 要求

新增一个紧凑“条件面板”，不要把 cockpit 退回表单页。

建议控件：

- RA：range 或 number，`0ft` 到 `20ft`，标注 `6ft` threshold。
- 发动机运行：toggle。
- 飞机在地面：toggle。
- 反推抑制：toggle。
- EEC enable：toggle。
- N1K：range 或 number。
- N1K deploy limit：number 或较小 range。

交互验收：

- RA 调到 `6ft` 或以上，`logic1` blocked on `radio_altitude_ft`。
- engine running 关闭，`logic2/logic3/logic4` 相关节点 blocked。
- aircraft on ground 关闭，`logic2/logic3/logic4` 相关节点 blocked。
- reverser inhibited 打开，`logic1/logic2/logic3` blocked。
- EEC enable 关闭，`logic2` blocked。
- `n1k >= max_n1k_deploy_limit`，`logic3` blocked。
- 恢复默认条件后，TRA 拉杆路径仍按 Round 84 预期工作。

### 硬约束

- 不改 `controller.py` confirmed control truth。
- 不改 `SimulationRunner` 语义。
- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、旧形态 `POST /api/lever-snapshot` 或 `well_harness run`。
- 不新增 Node / Vite / Next、runtime dependency、LLM、schema / validator、browser E2E、截图工具或截图资产。
- 不新增第二套 payload、UI-side inference 或控制真值。
- 不把 simplified plant 说成完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 测试要求

- `/api/lever-snapshot` 仅传 `tra_deg` 的旧请求仍兼容。
- 新增 endpoint tests 覆盖：
  - `radio_altitude_ft = 6.0` blocks `logic1` on `radio_altitude_ft`。
  - `engine_running = false` blocks affected logic。
  - `aircraft_on_ground = false` blocks affected logic。
  - `reverser_inhibited = true` blocks affected logic。
  - `eec_enable = false` blocks `logic2`。
  - `n1k >= max_n1k_deploy_limit` blocks `logic3`。
- 静态 HTML 包含条件面板控件。
- JS 监听条件面板输入，并仍调用 `/api/lever-snapshot`。
- UI 文案明确 feedback / plant 是 simplified first-cut demo，不是完整实时物理模型。
- 当前 `124 tests OK` 基线继续通过，并新增本轮测试。

### 完成后回报

- 改了哪些文件。
- 条件面板支持哪些参数。
- `/api/lever-snapshot` 如何保持旧请求兼容，并如何接收新参数。
- 各参数变化如何影响 logic1-4 / HUD / 逻辑主板。
- 是否仍复用 controller / switch / plant，而不是 JS 硬编码条件。
- 现有 demo / run / `/api/demo` 是否保持不变。
- 跑了哪些测试。

## Round 86 开发任务：manual exact TRA drag spot-check

### 当前状态

- Round 85 已完成，并通过指挥侧复核。
- 当前 UI 继续保持 interactive cockpit demo candidate。
- 当前全量回归：`124 tests OK`。
- Round 85 未修改任何仓库文件。
- 真实 Chrome 窗口已确认 cockpit 首屏：拉杆、HUD、逻辑主板、当前结论在第一屏，`诊断问答` 是次要入口。
- `原始 JSON 调试`、evidence / risks 仍默认折叠。
- `logic4 / THR_LOCK` 在 `-14°` 附近显示 blocked，并解释依赖 VDT90 / `deploy_90_percent_vdt` simplified plant feedback。
- 浏览器里已触发一次 range 控件微小变化：TRA 从 `-14.0°` 到 `-13.9°`。
- 由于本机 Chrome 多窗口 / profile 弹窗 / macOS GUI 注入坐标干扰，Round 85 没有完成四个精确 TRA 点的真实拖动验证。
- 四个 TRA 点已通过 live `/api/lever-snapshot` 验证。

### 唯一任务

做一次人工鼠标 / 触控板精确拖动 spot-check，确认四个 TRA 点在真实浏览器 UI 中可讲。

启动：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --open
```

如果默认端口被占用：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8767
```

请不要依赖 Apple Events / System Events / 自动坐标注入；直接人工拖动拉杆。

检查点：

- `TRA=0`：SW1/SW2 inactive；logic1/logic3/logic4 blocked；THR_LOCK inactive；当前结论提示进入 SW1 窗口。
- `TRA=-2`：SW1、L1、TLS115 active；SW2 inactive。
- `TRA=-7`：SW1/SW2、L2、540V active；logic3 blocked on `tra_deg`。
- `TRA=-14`：logic3、EEC、PLS、PDU active；VDT90 inactive；logic4 / THR_LOCK blocked on `deploy_90_percent_vdt`。
- `logic4 / THR_LOCK` 的 VDT90 / plant feedback 说明直观且不误导。
- evidence / risks 与 `原始 JSON 调试` 仍默认折叠。
- `诊断问答` 仍为次要入口。

如果通过，不要修改代码。

如果只发现轻微可读性问题，先记录，不要急着改；只有阻塞现场演示时才做极小 HTML / CSS / JS 修正。

如有代码变更，重新跑：

```bash
PYTHONPATH=src python3 -m unittest tests.test_demo
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

### 硬约束

- 不改 `controller.py` confirmed control truth。
- 不改 `SimulationRunner` 语义。
- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、`POST /api/lever-snapshot` 或 `well_harness run`。
- 不新增 Node / Vite / Next、runtime dependency、LLM、schema / validator、browser E2E、截图工具或截图资产。
- 不新增第二套 payload、UI-side inference 或控制真值。
- 不把 simplified plant 说成完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 完成后回报

- 是否完成人工四点拖动 spot-check。
- 使用的浏览器、端口、视口。
- `TRA=0/-2/-7/-14` 各自 UI 状态是否符合预期。
- 是否需要代码修正；如果需要，改了哪些文件。
- 当前 UI 是否继续保持 interactive cockpit demo candidate。
- `logic4 / THR_LOCK` 对 VDT90 / plant feedback 的解释是否直观且不误导。
- evidence / raw JSON 是否仍默认折叠。
- 现有 demo / run / `/api/demo` / `/api/lever-snapshot` 行为是否保持不变。
- 跑了哪些测试或 smoke。

## Round 85 开发任务：interactive lever cockpit browser drag QA

### 当前状态

- Round 84 interactive thrust reverser lever cockpit demo 已完成，并通过指挥侧复核。
- 当前全量回归：`124 tests OK`。
- UI 首屏已是 `反推拉杆` + HUD + `逻辑主板` + `当前结论`，不是问答文字页。
- `POST /api/lever-snapshot` 已实现 canonical pullback scrubber，并复用 `HarnessConfig`、`LatchedThrottleSwitches`、`SimplifiedDeployPlant`、`DeployController.evaluate_with_explain(...)` 与 `DeployController.explain(...)`。
- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
- 未修改 `controller.py` confirmed truth、`SimulationRunner`、`scenarios.py` 或 `docs/coordination/plan.md`。
- 还没做真实浏览器拖动拉杆 visual hand-check。

### 唯一任务

做一次真实浏览器拖动拉杆 hand-check，并只修现场展示阻塞。

启动：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --open
```

如果默认端口被占用：

```bash
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766
```

必须检查：

- 桌面宽屏首屏是否第一眼就是可操作反推拉杆 cockpit。
- 窄屏 / 移动宽度是否仍按拉杆 -> HUD -> 逻辑主板 -> 当前结论阅读。
- 拖动到 `TRA=0`、`-2`、`-7`、`-14` 时，HUD 和节点状态是否符合 Round 84 快照：
  - `TRA=0`：SW1/SW2 inactive；logic1/logic3/logic4 blocked；THR_LOCK inactive。
  - `TRA=-2`：SW1、L1、TLS115 active；SW2 inactive。
  - `TRA=-7`：SW1/SW2、L2、540V active；logic3 blocked on `tra_deg`。
  - `TRA=-14`：logic3、EEC、PLS、PDU active；VDT90 inactive；logic4 / THR_LOCK blocked on `deploy_90_percent_vdt`。
- `logic4 / THR_LOCK` 是否清楚说明依赖 VDT90 / simplified plant feedback，没有误导为完整实时物理仿真。
- evidence / risks 与 `原始 JSON 调试` 是否默认折叠。
- `诊断问答` 是否保持次要入口。

如果没有发现现场阻塞，不要修改代码。

如果发现明确阻塞，只允许极小 HTML / CSS / JS 修正，并重新跑：

```bash
PYTHONPATH=src python3 -m unittest tests.test_demo
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

### 硬约束

- 不改 `controller.py` confirmed control truth。
- 不改 `SimulationRunner` 语义。
- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、`POST /api/lever-snapshot` 或 `well_harness run`。
- 不新增 Node / Vite / Next、runtime dependency、LLM、schema / validator、browser E2E、截图工具或截图资产。
- 不新增第二套 payload、UI-side inference 或控制真值。
- 不把 simplified plant 说成完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 完成后回报

- 是否完成真实浏览器拖动拉杆 hand-check。
- 使用的浏览器、端口、视口。
- 检查了哪些 TRA 点。
- 是否需要代码修正；如果需要，改了哪些文件。
- 当前 UI 是否继续保持 interactive cockpit demo candidate。
- `logic4 / THR_LOCK` 对 VDT90 / plant feedback 的解释是否直观且不误导。
- evidence / raw JSON 是否仍默认折叠。
- 现有 demo / run / `/api/demo` 行为是否保持不变。
- 跑了哪些测试。

## Round 84 完成记录：interactive thrust reverser lever cockpit demo

### 完成状态

- UI 首屏已从问答式文字页改为交互式反推拉杆 cockpit demo。
- 新增极薄后端 endpoint：`POST /api/lever-snapshot`。
- `/api/lever-snapshot` 使用 canonical pullback scrubber 生成演示快照，并明确标注这不是完整飞控实时物理仿真。
- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
- 未修改 `controller.py`、`SimulationRunner`、`scenarios.py`、`docs/coordination/plan.md`。
- 未新增 runtime dependency、Node / Vite / Next、LLM、E2E / Playwright / Selenium、schema / validator 或第二套 DemoAnswer payload。

### Cockpit UI

- 首屏主区域现在是：
  - `反推拉杆`：range 控件 `0°` 到 `-32°`，默认 `-14.0°`。
  - 阈值标尺：`SW1 -1.4° ~ -6.2°`、`SW2 -5.0° ~ -9.8°`、`L3 ≤ -11.74°`、`L4 travel (-32°, 0°)`。
  - HUD：TRA、SW1/SW2、无线电高度、发动机 / 地面、反推抑制、EEC enable、N1K / limit、TLS / PLS 解锁、deploy position / VDT90。
  - `逻辑主板`：节点按 `/api/lever-snapshot` 的 `active / blocked / inactive` 状态高亮。
  - `当前结论`：默认只显示 headline、blocker、next step；证据 / 风险折叠在 details 中。
  - `原始 JSON 调试`：继续折叠，作为 debug inspector。
- 原有四个中文问答 prompt 保留，但降级到 `诊断问答` 抽屉。

### `/api/lever-snapshot`

- Endpoint 位于 `src/well_harness/demo_server.py`。
- 输入：`{"tra_deg": <number>}`，会 clamp 到 `HarnessConfig.reverse_travel_min_deg` / `reverse_travel_max_deg`。
- 复用：
  - `HarnessConfig`
  - `LatchedThrottleSwitches`
  - `SimplifiedDeployPlant`
  - `DeployController.evaluate_with_explain(...)`
  - `DeployController.explain(...)` 生成的 failed conditions
- 不在 JS 中硬编码 controller 条件；JS 只渲染后端返回的 HUD、node states、summary 和 raw JSON。

### 关键 TRA 快照

- `TRA=0`：SW1/SW2 inactive；logic1/logic3/logic4 blocked；THR_LOCK inactive。
- `TRA=-2`：SW1、L1、TLS115 active；SW2 inactive。
- `TRA=-7`：SW1/SW2、L2、540V active；logic3 blocked，blocker 为 `tra_deg`。
- `TRA=-14`：logic3、EEC、PLS、PDU active；VDT90 inactive；logic4 / THR_LOCK blocked，blocker 为 `deploy_90_percent_vdt`。

### 测试

- 新增 `/api/lever-snapshot` HTTP smoke / contract test，覆盖 TRA `0 / -2 / -7 / -14`。
- 新增静态 UI 测试，覆盖 range 控件、lever input listener、`/api/lever-snapshot` 调用、raw JSON 默认折叠、`active / blocked / inactive` 状态类。
- `tests.test_demo` 当前为 64 tests OK。
- `tests.test_controller` 当前为 14 tests OK。

## Round 84 开发任务：interactive thrust reverser lever cockpit demo

### 当前判断修正

- 必须停止 “demo ready / 不做 UI 继续美化” 的方向。
- 当前中文 UI 虽然通过 `122 tests OK`，但仍是“问答式文字解释 UI”，不满足用户要的飞机电反推控制逻辑可视化操作 demo。
- 下一轮不是美化，而是核心交互重构：用户拖动反推拉杆，就能看到 TRA、SW1/SW2、logic1-4、TLS/PLS/VDT、THR_LOCK 的状态变化。

### 唯一任务

新增高质量交互式电反推拉杆 cockpit demo。

第一屏主视觉必须是可操作的简化反推拉杆 + 参数 HUD + 控制逻辑主板，而不是问答表单。

### 重点实现

- 新增 throttle / reverse lever 控件，范围建议 `0°` 到 `-32°`。
- 标注关键阈值 / 窗口：
  - SW1 window: `-1.4°` to `-6.2°`
  - SW2 window: `-5.0°` to `-9.8°`
  - logic3 TRA threshold: `<= -11.74°`
  - logic4 reverse travel: `(-32°, 0°)`
- 拉杆旁边实时显示参数 HUD：
  - TRA deg
  - SW1 / SW2
  - radio altitude
  - engine running
  - aircraft on ground
  - reverser inhibited
  - eec enable
  - n1k / max_n1k_deploy_limit
  - TLS unlocked
  - PLS unlocked
  - deploy position %
  - deploy_90_percent_vdt
- 控制逻辑主板必须跟随拉杆状态实时高亮：
  - SW1
  - logic1 / TLS115
  - TLS unlocked
  - SW2
  - logic2 / 540V
  - logic3 / EEC / PLS / PDU
  - VDT90
  - logic4 / THR_LOCK
- 节点状态至少区分 active / blocked / inactive。
- 主结果区默认只展示 1-2 句：当前会发生什么、当前被哪个条件卡住、下一步拉杆 / 状态变化会触发哪个节点。
- evidence / possible_causes / required_changes / risks 和 raw JSON 默认折叠。
- 现有问答 prompt 保留但降级为次要入口，例如右下角“诊断问答”抽屉。

### 技术方向

新增极薄后端 endpoint：

- `POST /api/lever-snapshot`

后端必须复用现有控制真值：

- `HarnessConfig`
- `LatchedThrottleSwitches`
- `DeployController.explain(...)`
- `DeployController.evaluate_with_explain(...)`

不要把 controller 条件硬编码到 JS。

如果 plant 状态需要时间维度，第一轮可以做 “canonical pullback scrubber”：

- slider 代表沿 nominal pullback 行程的受控演示状态。
- UI 文案明确：这是受控演示轨迹，不是完整飞控实时物理仿真。

如果只做 TRA 即时快照：

- 必须把 TLS / PLS / VDT 标注为 simplified / assumed / not yet timed。
- 不得假装完整物理模型。

### 硬约束

- 不改 `controller.py` confirmed control truth。
- 不改 `SimulationRunner` 语义。
- 不破坏现有 `well_harness demo`。
- 不破坏现有 `well_harness demo --format json`。
- 不破坏现有 `POST /api/demo`。
- 不破坏现有 `well_harness run`。
- 不新增 LLM。
- 不新增 Node / Vite / Next，除非明确说明为什么必须。
- 不新增运行时依赖。
- 不把 simplified plant 说成完整物理模型。
- 不继续扩 schema / validator 工具链。
- 不做 E2E / Playwright / Selenium。
- 不新增第二套 payload、UI-side inference 或控制真值。
- 不要修改 `docs/coordination/plan.md`。

### 测试要求

- `/api/lever-snapshot` 对 `TRA=0`、`-2`、`-7`、`-14` 的 smoke / contract 测试。
- 静态 HTML 包含 lever / range 控件。
- JS 包含 lever input listener，并调用 `/api/lever-snapshot`。
- UI 默认不展开 evidence / raw JSON。
- 链路节点有 active / blocked / inactive 状态类或等价状态映射。
- 当前 `122 tests OK` 基线继续通过，并新增本轮交互测试。

### 完成后回报

- 改了哪些文件。
- lever cockpit 第一屏如何组织。
- `/api/lever-snapshot` 如何复用 controller / switch model。
- 拉杆在 `TRA=0/-2/-7/-14` 时分别展示什么状态。
- logic4 / THR_LOCK 如何解释 VDT90 / plant feedback 依赖，是否避免误导。
- evidence / raw JSON 如何默认折叠。
- 现有问答能力如何降级为次要入口。
- 是否保持现有 demo / run / `/api/demo` 行为。
- 跑了哪些测试。

### 指挥提醒

不要再向用户证明现有 UI 可以讲 demo；用户要的是拖拉杆就能看懂电反推控制链路。

## Round 83 状态：plant boundary coverage accepted / demo ready

### 当前状态

- Round 82 plant simplification notes and boundary scenario coverage 已完成，并通过指挥侧复核。
- 当前全量回归：`122 tests OK`。
- 当前中文 UI 继续保持 demo candidate；没有必须处理的中文 demo 展示面阻塞。
- 本轮没有修改 `controller.py`、`SimulationRunner`、`run` CLI、demo text / JSON 输出语义、`POST /api/demo` payload 或 `DemoAnswer` shape。
- plant first-cut simplification 已明确标注：
  - deploy-position movement 在所有 PLS unlock indications 为 true 后才开始，这是 plant feedback / motion simplification，不是 controller `logic3` gate。
  - `reverser_not_deployed_eec = deploy_position_percent <= 0.0` 是 placeholder sensor / feedback simplification，不是已确认真实 EEC signal model。
- 新增边界测试覆盖 RA=6ft、TRA 未到 -11.74、N1K 不满足、90% 未到达、SW1/SW2 latch reset、PLS unlock 前 plant 位移不增长、位移大于 0 后 `reverser_not_deployed_eec` 为 false。

### 下一步

停止常规开发迭代。当前状态可用于中文 demo 和控制逻辑讨论。

如果后续还要补 plant 边界覆盖，只建议新增小型局部测试，例如：

- TLS 未解锁时 `logic3` 不满足。
- VDT 90% 前后相邻 trace-row 行为。

不要将 simplified plant 扩写成完整物理模型，也不要改 `controller.py` 真值逻辑。

## Round 82 完成记录：plant simplification notes and boundary scenario coverage

### 完成状态

- plant 简化假设已在 `README.md` 的 Modeling Notes 和 `src/well_harness/plant.py` 对应位置显式标注。
- 新增轻量边界测试，覆盖 controller 阈值边界、SW1/SW2 latch reset 语义，以及两个 first-cut plant feedback simplification。
- 未修改 `controller.py`、`SimulationRunner`、`scenarios.py`、`well_harness.cli run`、demo text / JSON 输出、`POST /api/demo` payload 或 `DemoAnswer` shape。
- 未新增 schema / validator / runtime dependency / Node / Vite / Next / LLM / browser E2E。
- 未修改 `docs/coordination/plan.md`。

### Plant 简化假设标注

- `README.md` / Modeling Notes：
  - 当前 first-cut plant 的 deploy-position movement 只有在所有 PLS unlock indications 为 true 后才开始；这是 plant feedback / motion simplification，不是 controller `logic3` 的新增门控。
  - 当前 first-cut plant 将 `reverser_not_deployed_eec` 简化为 `deploy_position_percent <= 0.0`；这是 placeholder sensor / feedback simplification，不是已确认真实 EEC signal model。
- `src/well_harness/plant.py`：
  - `PlantState.sensors(...)` 中 `reverser_not_deployed_eec` 附近有对应 first-cut feedback simplification 注释。
  - `SimplifiedDeployPlant.advance(...)` 中 `all(pls_unlocked_ls)` 位移门控附近有对应 plant simplification 注释，并明确不是 controller `logic3` gate。

### 新增测试覆盖

- `tests/test_controller.py`
  - `test_logic1_ra_threshold_is_strictly_below_six_feet`：`RA = 6ft` 时 `logic1` 与 `tls_115vac_cmd` 不应满足。
  - `test_logic3_blocks_commands_when_tra_has_not_reached_threshold`：TRA 未到 `-11.74°` 时 `logic3`、`eec_deploy_cmd`、`pls_power_cmd`、`pdu_motor_cmd` 不应触发。
  - `test_logic3_requires_n1k_below_deploy_limit`：`n1k == max_n1k_deploy_limit` 时 `logic3` 和其 command fan-out 不应触发。
  - `test_logic4_requires_deploy_90_percent_vdt`：未到 `deploy_90_percent_vdt` 时 `logic4` 和 throttle lock release 不应触发。
  - `test_sw1_sw2_latches_hold_until_reverse_selection_returns_near_zero`：保护 SW1/SW2 latch hold / reset 语义。
  - `test_deploy_motion_waits_for_all_pls_unlocks_in_first_cut_plant`：保护 PLS unlock 前 plant 位移不增长的 simplified plant behavior。
  - `test_reverser_not_deployed_eec_is_first_cut_position_simplification`：保护 `deploy_position_percent <= 0.0` 的 first-cut EEC feedback simplification。

### 当前验证

- `PYTHONPATH=src python3 -m py_compile src/well_harness/plant.py src/well_harness/controller.py src/well_harness/runner.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_controller`：14 tests OK。
- `PYTHONPATH=src python3 -m unittest tests.test_demo`：62 tests OK。
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`：122 tests OK。
- demo JSON smoke：`logic4 和 throttle lock 有什么关系` 通过。
- `run nominal-deploy --format json` smoke 通过，`logic4_any=True` 且 `throttle_electronic_lock_release_cmd` 触发。
- `run retract-reset --format json` smoke 通过，tail row 清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 下一步建议

- 当前 controller truth 不需要修改。
- 如继续扩 plant 边界覆盖，可考虑只新增小型局部测试，例如 TLS 未解锁时 `logic3` 不满足，或 VDT 90% 前后相邻 trace-row 行为；不要将 simplified plant 包装成完整物理模型。

## Round 82 开发任务：plant simplification notes and boundary scenario coverage

### 当前状态

- Round 81 中文 presenter rehearsal 已完成，并通过指挥侧复核。
- 当前中文 UI 可作为 demo candidate；没有必须处理的中文 demo 展示面阻塞。
- 当前全量回归：`115 tests OK`。
- 新一轮复核结论：核心 controller 真值逻辑没有发现硬性偏离。
- 当前要处理的是 simplified plant 假设和边界覆盖，不是 controller 逻辑错误。

### 唯一任务

在不修改 controller 真值逻辑、不改变现有 UI/API/demo/run CLI 行为的前提下，补齐 plant 简化假设说明，并新增轻量边界场景 / 测试覆盖。

### 必须保持

- 不改 `controller.py` 的 logic1-4 判定语义。
- 不改 `SimulationRunner` 语义。
- 不改变 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不改变 `POST /api/demo` payload 或 `DemoAnswer` shape。
- 不新增第二套 answer payload、UI-side inference 或控制真值。
- 不重写 plant 为完整物理模型。
- 不把 simplified plant 说成真实完整物理模型。
- 不做 UI 继续美化。
- 不继续做 schema / validator 工具链。
- 不新增运行时依赖、Node / Vite / Next、LLM 或 browser E2E。
- 不要修改 `docs/coordination/plan.md`。

### 建议实施

- 在 `README.md` 的 Modeling Notes 中显式说明两个 plant first-cut simplification：
  - plant 位移开始被简化门控在 `all(pls_unlocked_ls)` 之后。
  - `reverser_not_deployed_eec` 被简化为 `deploy_position_percent <= 0.0`。
- 如有帮助，在 `src/well_harness/plant.py` 对应位置加简短注释，说明这些是 simplified plant feedback assumptions，不是 controller confirmed truth。
- 新增轻量边界测试，优先使用 tests 内局部 scenario / frame helper；如新增 built-in scenario，保持数量少且命名清晰。
- 建议至少覆盖：
  - `RA = 6ft` 边界：`logic1` 不满足。
  - `TRA` 未到 `-11.74°`：`logic3` 不满足，`pls_power_cmd / pdu_motor_cmd` 不误触发。
  - `N1K` 限制不满足：`logic3` 不满足。
  - `deploy_90_percent_vdt` 未到达：`logic4` 不满足。
  - `SW1/SW2` latch reset / bounce 语义。
- 可选覆盖：
  - `TLS未解锁` 时 `logic3` 不满足。
  - PLS unlock 前 plant 位移不增长的简化假设。
  - 位移大于 0 后 `reverser_not_deployed_eec` 变为 false 的简化假设。

### 验收标准

1. plant 简化假设被显式标注，至少覆盖 PLS unlock 后才推动位移、`reverser_not_deployed_eec = deploy_position_percent <= 0.0` 两点。
2. 文档明确这些是 first-cut plant simplification，不是 controller confirmed truth。
3. `controller.py` 的 logic1-4 判定语义保持不变。
4. 新增轻量边界场景 / 测试覆盖 RA=6ft、TRA 未到 -11.74、N1K 不满足、90% 未到达、SW1/SW2 latch reset 或等价核心边界。
5. `run nominal-deploy` 与 `run retract-reset` 既有行为不回归。
6. `nominal-deploy` 仍到达 `logic4` 且 throttle lock release 仍触发。
7. `retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。
8. 当前 `115 tests OK` 基线继续通过，并新增本轮边界覆盖测试。
9. 中文 UI demo candidate 不回归。
10. 不新增 schema / validator / runtime dependency / E2E / LLM。

### 完成后回报

- 改了哪些文件。
- plant 简化假设标注在哪里、具体覆盖哪两点。
- 新增了哪些边界测试 / 场景。
- 是否改了 controller 真值逻辑。
- 默认 demo text / JSON 输出、`run` CLI、UI/API payload 是否保持不变。
- 跑了哪些测试。
- 下一步是否还需要更多 plant 边界场景。

## Round 82 状态：中文 demo freeze / live demo ready

### 当前状态

- Round 81 中文 presenter rehearsal 已完成，并通过指挥侧复核。
- 当前中文 UI 继续保持 demo candidate，可用于现场演示。
- 当前全量回归：`115 tests OK`。
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。
- 当前没有必须处理的中文 demo 展示面阻塞。

### 下一步

不要继续常规开发迭代。现场使用时直接启动并彩排：

- `PYTHONPATH=src python3 -m well_harness.demo_server --open`

如果默认端口被占用：

- `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`

只有在现场彩排发现明确阻塞演示的问题时，才允许做极小 HTML / CSS 微调。

### 演示路径

1. 打开首屏，讲一句：这是 `反推逻辑演示舱`。
2. 运行 / 展示 `logic4 和 throttle lock 有什么关系`。
3. 指向 `逻辑主板` 中 `L4 / THR_LOCK` 高亮。
4. 指向 `为什么高亮`，说明它只是答案关联，不是完整根因证明。
5. 指向 `推理结果`，扫 `证据 / 结果 / 可能原因 / 风险`。
6. 展示 `原始 JSON 调试` 是折叠的 debug inspector。
7. 运行 / 展示 `为什么 throttle lock 没释放`。
8. 简短说明边界：确定性演示层、内置场景、简化 plant、不是开放式 AI、不是完整物理模型。

### 不要做

- 不继续做 raw JSON copy affordance。
- 不继续扩 schema validation 工具链。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图工具或截图资产。
- 不接入真实 LLM / agent 系统。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario、second payload、UI-side inference 或新的 control truth。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

## Round 81 开发任务：中文 demo candidate / presenter rehearsal only

### 当前状态

- Round 80 中文 demo 真实浏览器视觉 QA 已完成，并通过指挥侧复核。
- 当前中文 UI 可作为 demo candidate。
- 当前全量回归：`115 tests OK`。
- 当前 UI 已完成：
  - `反推逻辑演示舱`
  - 提问区 / 运行演示 / 逻辑主板 / 为什么高亮 / 推理结果 / 结果摘要 / 原始 JSON 调试中文化
  - 游戏化 / 电路主板式逻辑主板
  - `L4 / THR_LOCK` 与 `L3 / EEC / PLS / PDU` 可区分
  - 主视觉内部英文提示已改成中文文案
  - `原始 JSON 调试` 折叠降权
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。
- 当前没有必须处理的中文 demo 展示面阻塞。

### 唯一任务

不要继续开发新功能。只做一次中文现场 presenter rehearsal / demo dry run。

如果彩排没有发现展示阻塞，不要修改代码。

如果彩排发现明确阻塞现场演示的问题，只允许做极小 HTML / CSS 微调。

### 彩排建议

- 启动：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 如果默认端口被占用，使用空闲端口：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 现场路径：
  1. 打开首屏，讲一句：这是 `反推逻辑演示舱`。
  2. 运行 / 展示 `logic4 和 throttle lock 有什么关系`。
  3. 指向 `逻辑主板` 中 `L4 / THR_LOCK` 高亮。
  4. 指向 `为什么高亮`，说明它只是答案关联，不是完整根因证明。
  5. 指向 `推理结果`，扫 `证据 / 结果 / 可能原因 / 风险`。
  6. 展示 `原始 JSON 调试` 是折叠的 debug inspector。
  7. 运行 / 展示 `为什么 throttle lock 没释放`。
  8. 简短说明边界：确定性演示层、内置场景、简化 plant、不是开放式 AI、不是完整物理模型。

### 允许修正

- 仅当彩排发现展示阻塞时，允许极小 HTML / CSS 修正：
  - 字距 / 行距
  - 字号
  - 逻辑主板节点 spacing
  - 高亮强度
  - 移动端换行
  - 原始 JSON 调试面板视觉权重
- 只有在 CSS 无法解决时，才允许极小 `demo.js` 调整。
- 如修改静态结构 / class，更新对应轻量静态测试。

### 非目标

- 不继续做 raw JSON copy affordance。
- 不继续扩 schema validation 工具链。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、真实 screenshot 文件或截图标注资产。
- 不接入真实 LLM / agent 系统。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario、second payload、UI-side inference 或新的 control truth。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 明确回报是否完成中文 presenter rehearsal。
2. 若没有代码修改，明确说明当前中文 UI 继续保持 demo candidate。
3. 若有代码修改，说明具体展示阻塞和极小修正范围。
4. `反推逻辑演示舱`、提问区、四个 prompt、逻辑主板、推理结果主干保持清楚。
5. `L4 / THR_LOCK` 与 `L3 / EEC / PLS / PDU` 高亮可区分。
6. `为什么 throttle lock 没释放` 能清楚展示 `可能原因 / 证据 / 风险`。
7. `原始 JSON 调试` 保留但不抢主视觉。
8. UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
9. 默认 demo text / JSON 输出和 `run` CLI 保持不变。
10. 当前 `115 tests OK` 基线继续通过。
11. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 是否完成中文 presenter rehearsal。
- 是否需要代码修改；如果需要，改了哪些文件。
- 当前中文 UI 是否继续保持 demo candidate。
- 逻辑主板观感是否仍足够直观。
- raw JSON 是否仍只是 `原始 JSON 调试`。
- UI/API 是否仍复用现有 demo reasoning layer。
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变。
- 跑了哪些测试。
- 是否还有必须处理的中文 demo 展示面阻塞。

## Round 80 完成记录：中文 demo 视觉 QA / 逻辑主板微调

### 结论

PASS，当前中文 UI 可作为 demo candidate。桌面真实 Chrome 窗口检查通过；窄屏使用真实 Chrome 窗口顶部检查，并用 Chrome 430px 渲染截图补充检查单列阅读路径。没有引入 E2E / Playwright / Selenium / 新依赖。

### 已完成

- 启动本地 UI：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 使用临时 Chrome profile 打开桌面窗口：
  - `http://127.0.0.1:8766/?round80=desktop-after-copy-fix`
  - 视口约 1440x1000。
- 桌面视觉 QA 结果：
  - 第一屏能清楚看出 `反推逻辑演示舱`。
  - 提问区、四个核心 prompt、逻辑主板、结果摘要、推理结果主干可见。
  - 默认 prompt `logic4 和 throttle lock 有什么关系` 自动渲染，`L4 / THR_LOCK` 高亮醒目但不刺眼。
  - `L3 / EEC / PLS / PDU` 能看出是同组子节点。
  - `原始 JSON 调试` 仍折叠在 debug inspector 中，不抢主视觉。
- 使用 430px 窄屏检查：
  - 窄屏顶部真实 Chrome 窗口能看到中文 hero / 提问区 / 四个 prompt 起点。
  - Chrome 430px 补充渲染截图显示页面按提问区 -> 逻辑主板 -> 推理结果单列阅读，未发现横向撑宽阻塞。
- 本轮发现并修正一个中文现场可读性问题：
  - 主视觉里仍有 `DemoAnswer matched_node / target_logic` 等偏内部英文文案。
  - 已改为“答案里的命中节点 / 目标逻辑”“答案关联：意图 / 命中节点 / 目标逻辑”等中文文案。
  - 未改变 DOM id、payload 字段、API shape 或控制真值。
- 第二个 prompt `为什么 throttle lock 没释放`：
  - 浏览器内自动点击未完成，因为本机 Chrome 禁用了 Apple Events JavaScript，`System Events` 点击也会卡住 / 被拒绝。
  - 已通过同一 server 的真实 `POST /api/demo` 路径验证 `diagnose_problem` payload，包含 `evidence / possible_causes / risks`。

### 未改内容

- 未修改 `docs/coordination/plan.md`。
- 未修改 `controller.py`、`SimulationRunner`、`well_harness.cli run`。
- 未改变 `well_harness demo` text / JSON 输出语义。
- 未改变 `POST /api/demo` payload 或 `DemoAnswer` shape。
- 未新增 second payload、schema、validator、runtime dependency、Node / Vite / Next、LLM、E2E / Playwright / Selenium。
- 未把 simplified plant 说成真实完整物理模型。

### 验证

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- 行为断言：
  - `nominal_logic4_any True`
  - `nominal_thr_release_any True`
  - `retract_clear True`
- 结果：
  - `tests.test_demo`: 62 tests OK。
  - 全量回归：115 tests OK。

### 下一步建议

没有必须处理的中文 demo 展示面阻塞。若继续 UI，只建议现场彩排时微调字距 / 高亮强度 / 主板节点 spacing，不要回到 schema / validator / raw JSON 小功能路线。

## Round 80 开发任务：中文 demo 界面真实浏览器视觉 QA / 游戏化逻辑主板微调

### 当前状态

- Round 79 中文 demo 展示面优化已完成，并通过指挥侧复核。
- 当前全量回归：`115 tests OK`。
- 当前 UI 已从英文-heavy cockpit 改成更适合中文现场演示的 `反推逻辑演示舱`。
- 当前已完成：
  - 提问区 / 运行演示 / 逻辑主板 / 为什么高亮 / 推理结果 / 结果摘要 / 原始 JSON 调试中文化。
  - 四个核心 prompt 保持不变。
  - 逻辑主板改成游戏化 / 电路主板风格：深色网格、发光芯片节点、LED 点、能量箭头、active glow。
  - `L4 / THR_LOCK` 与 `L3 / EEC / PLS / PDU` 继续可区分。
  - 结构化答案区使用中文字段名：意图、命中节点、目标逻辑、证据、结果、可能原因、需要变化、风险。
  - `原始 JSON 调试` 继续折叠降权。
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。
- 当前剩余风险：本轮尚未做真实浏览器中文现场视觉 QA。

### 唯一任务

做一次真实浏览器中文现场视觉 QA，重点看首屏中文信息密度和“逻辑主板”的观感。

如果视觉已经适合现场 demo，优先不要改代码，只更新交接 / QA 记录。

如果发现明确影响现场演示的问题，只允许做极小 HTML / CSS 微调，不要新增新功能。

### 建议执行

- 启动本地 UI：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 如果默认端口被占用，使用空闲端口：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 在真实浏览器中检查：
  - 桌面宽屏。
  - 窄屏 / 移动宽度。
- 至少检查两个 prompt：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 throttle lock 没释放`
- 检查重点：
  - 第一屏是否一眼能看懂“这是反推逻辑演示舱”。
  - 中文文案是否太多，是否还有明显英文-heavy 的标题 / 区块。
  - 四个示例 prompt 是否容易选择。
  - 逻辑主板是否足够像游戏化链路 / 电路板，而不是普通表格。
  - `L4 / THR_LOCK` 高亮是否醒目但不刺眼。
  - `L3 / EEC / PLS / PDU` 是否能看出是同组子节点。
  - `推理结果` 区是否能快速扫到 `证据 / 结果 / 可能原因 / 风险`。
  - `原始 JSON 调试` 是否折叠且不抢主视觉。
  - 窄屏下是否仍按提问区 -> 逻辑主板 -> 推理结果阅读。

### 允许修正

- 只允许极小 HTML / CSS 修正：
  - spacing
  - 字号
  - 高亮强度
  - 逻辑主板节点间距
  - 移动端换行
  - raw JSON 调试面板视觉权重
- 只有在视觉阻塞无法用 CSS 解决时，才允许极小 `demo.js` 调整。
- 如修改静态结构 / class，更新对应轻量静态测试。

### 非目标

- 不继续做 raw JSON copy affordance。
- 不继续扩 schema validation 工具链。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、真实 screenshot 文件或截图标注资产。
- 不接入真实 LLM / agent 系统。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario、second payload、UI-side inference 或新的 control truth。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 明确回报是否完成真实浏览器中文现场视觉 QA。
2. 若完成，说明使用的浏览器、端口、视口。
3. 若无法完成，明确说明原因，不得把静态测试说成真实浏览器验证。
4. 中文首屏能清楚展示 `反推逻辑演示舱`、提问区、四个 prompt、逻辑主板、推理结果主干。
5. 逻辑主板观感足够直观，`L4 / THR_LOCK` 与 `L3 / EEC / PLS / PDU` 高亮可区分。
6. `为什么 throttle lock 没释放` 能清楚展示 `可能原因 / 证据 / 风险`。
7. `原始 JSON 调试` 保留但不抢主视觉。
8. 如无需修正，明确回报当前中文 UI 可作为 demo candidate。
9. 如有修正，新增或更新轻量静态测试覆盖对应 HTML / CSS class 或中文文案。
10. 当前 `115 tests OK` 基线继续通过。
11. 现有 CLI 行为保持不变。
12. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 是否完成真实浏览器中文现场视觉 QA。
- 使用的浏览器、端口、视口。
- 是否需要代码修正；如果需要，改了哪些文件。
- 当前中文 UI 是否可作为 demo candidate。
- 逻辑主板观感是否足够直观。
- raw JSON 是否仍只是 `原始 JSON 调试`。
- UI/API 是否仍复用现有 demo reasoning layer。
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变。
- 跑了哪些测试。
- 是否还有必须处理的中文 demo 展示面阻塞。

## Round 79 改向完成记录：中文 demo 展示面优化

### 结论

PASS。根据用户反馈，本轮暂停 freeze rehearsal，将本地 UI 从英文-heavy cockpit 改成更适合中文现场演示的 `反推逻辑演示舱`。

### 已完成

- UI 主要文案中文化：
  - hero / mission / boundary
  - 提问区 / 运行演示 / 逻辑主板 / 为什么高亮 / 推理结果 / 结果摘要 / 原始 JSON 调试
  - 四个核心 prompt 分组：链路关系、未释放诊断、触发影响、改阈值预演
- 大幅压缩页面说明文案，避免展示面像内部文档清单。
- 将 fixed control chain 视觉强化为游戏化 / 主板式 `逻辑主板`：
  - 节点像发光芯片 / 技能节点。
  - 箭头使用更明显的能量链路样式。
  - `L4 / THR_LOCK`、`L3 / EEC / PLS / PDU` 保持可区分。
  - 原始英文 token 保留在 `title` / `data-node` 中，避免语义失真。
- 结构化答案区改成中文结果卡片：
  - 意图、命中节点、目标逻辑、证据、结果、可能原因、需要变化、风险。
  - 底层 `DemoAnswer` 字段、DOM id、payload shape 未改变。
- raw JSON 继续折叠为 `原始 JSON 调试`，保留但不作为主视觉。
- 更新静态 UI 测试以覆盖中文主标题、提问区、逻辑主板、推理结果、raw JSON 折叠、四个核心 prompt 和现有 API 复用路径。

### 未改内容

- 未修改 `docs/coordination/plan.md`。
- 未修改 `controller.py`、`SimulationRunner`、`well_harness.cli run`。
- 未改变 `well_harness demo` text / JSON 输出语义。
- 未改变 `POST /api/demo` payload 或 `DemoAnswer` shape。
- 未新增 second payload、schema、validator、runtime dependency、Node / Vite / Next、LLM、E2E / Playwright / Selenium。
- 未把 simplified plant 说成真实完整物理模型。

### 下一步建议

下一轮如继续 UI，只建议用浏览器做一次中文现场 demo 视觉手检，重点看中文信息密度和逻辑主板观感；不要回到 schema / validator / raw JSON 小功能惯性。

### 验证

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- 行为断言：
  - `nominal_logic4_any True`
  - `nominal_thr_release_any True`
  - `retract_clear True`
- 结果：
  - `tests.test_demo`: 62 tests OK。
  - 全量回归：115 tests OK。

## Round 79 开发任务：UI demo freeze candidate / presenter rehearsal only

### 当前状态

- Round 78 已完成，并将当前 UI 判定为 freeze candidate。
- 当前全量回归：`115 tests OK`。
- 当前项目目录不是 Git 仓库；不要依赖 `git diff` 做变更判断。
- 本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 当前 UI 已经具备可展示 demo surface：
  - `Deploy-chain reasoning cockpit`
  - prompt 输入与四个核心示例 prompt
  - fixed control chain
  - highlight explanation
  - structured answer 主干
  - raw JSON debug inspector 折叠降权
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一任务

不要继续开发新功能。只做一次人工 presenter rehearsal / demo dry run。

如果彩排没有发现展示阻塞，不要修改代码。

如果彩排发现明确阻塞现场演示的问题，只允许做极小 HTML / CSS 修正，并保留当前 API / payload / CLI / 控制逻辑语义。

### 彩排建议

- 启动：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 如果默认端口被占用，换空闲端口，例如：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 按以下顺序走一遍：
  1. 打开首屏，确认 `Deploy-chain reasoning cockpit`。
  2. 运行 / 展示 `logic4 和 throttle lock 有什么关系`。
  3. 指向 fixed control chain 中 `logic4 / THR_LOCK` 高亮。
  4. 指向 highlight explanation。
  5. 指向 structured answer。
  6. 展示 raw JSON 只是折叠 debug inspector。
  7. 运行 / 展示 `为什么 throttle lock 没释放`。
  8. 指向 `possible_causes / evidence / risks`。
  9. 简短说明边界：deterministic controlled demo layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。

### 非目标

- 不继续做 raw JSON copy affordance。
- 不继续扩 schema validation 工具链。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、真实 screenshot 文件或截图标注资产。
- 不接入真实 LLM / agent 系统。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario、second payload、UI-side inference 或新的 control truth。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 明确回报是否完成 presenter rehearsal。
2. 若没有代码修改，明确说明 UI 继续保持 freeze candidate。
3. 若有代码修改，说明具体展示阻塞和极小修正范围。
4. raw JSON debug inspector 保留但不抢主视觉。
5. UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
6. 默认 demo text / JSON 输出和 `run` CLI 保持不变。
7. 当前 `115 tests OK` 基线继续通过。
8. `nominal-deploy` 仍能到达 `logic4`。
9. `retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 是否完成 presenter rehearsal。
- 是否需要代码修改；如果需要，改了哪些文件。
- UI 是否继续保持 freeze candidate。
- raw JSON 是否仍只是 debug inspector。
- UI/API 是否仍复用现有 demo reasoning layer。
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变。
- 跑了哪些测试。
- 是否还有必须处理的 UI 展示面阻塞。

## Round 78 完成记录：UI demo clean-window visual QA and freeze candidate

### 结论

PASS，当前 UI 可作为 freeze candidate。没有发现需要继续修改 HTML / CSS / JS 的第一屏展示阻塞。

本轮是人工视觉 QA / freeze 判断，不是浏览器 E2E automation。临时截图只保存在 `/tmp/well-harness-r78-shots/` 用于本轮检查，没有新增截图资产、浏览器自动化框架或仓库文件。

### 已完成

- 复核当前工作区不是 Git 仓库，未依赖 `git diff` 做判断。
- 阅读核心文件：
  - `README.md`
  - `docs/coordination/plan.md`（只读，未修改）
  - `docs/coordination/dev_handoff.md`
  - `docs/coordination/qa_report.md`
  - `src/well_harness/demo_server.py`
  - `src/well_harness/static/demo.html`
  - `src/well_harness/static/demo.css`
  - `src/well_harness/static/demo.js`
  - `tests/test_demo.py`
- 启动本地 UI：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 使用 Safari 新窗口打开：
  - `http://127.0.0.1:8766/?round78=safari-clean-desktop`
  - 视口约为桌面宽屏窗口。
- 桌面宽屏视觉检查结果：
  - 第一屏明确是 `Deploy-chain reasoning cockpit` demo surface，不像内部调试页。
  - prompt 输入区、四个核心示例 prompt、fixed control chain、highlight explanation、structured answer 主干清楚可见。
  - `logic4 和 throttle lock 有什么关系` 默认 answer 可见，`logic4 / THR_LOCK` 高亮与 highlight explanation / structured answer 的关系清楚。
  - raw JSON 保持为折叠 `Raw JSON debug inspector`，没有抢主视觉。
- 使用临时 Chrome profile 打开窄屏窗口：
  - `open -na 'Google Chrome' --args --user-data-dir=/tmp/well-harness-r78-openna-profile --no-first-run --no-default-browser-check --disable-default-apps --new-window --window-size=430,1200 'http://127.0.0.1:8766/?round78=openna-narrow'`
  - 视口约为 430px 宽。
- 窄屏视觉检查结果：
  - 页面仍按 hero / route strip / prompt panel 的顺序阅读。
  - prompt 区与四个示例 prompt 在窄屏下可扫读，后续 chain / answer 按单列布局继续向下阅读。
  - 未发现横向撑宽导致无法阅读的阻塞。
- 使用 headless Chrome 临时 profile 补充桌面 / 窄屏截图检查：
  - 1440x1000 桌面：prompt / chain / structured answer 三栏展示清楚。
  - 430x1200 窄屏：保持 prompt -> chain -> answer 的单列阅读路径。
- 运行 `POST /api/demo` 真实 API smoke 验证第二个核心 prompt：
  - `为什么 throttle lock 没释放`
  - 返回 `intent=diagnose_problem`，并包含 `possible_causes` / `evidence` / `risks`。
- 未做代码修正。
- 未修改 `README.md`、`docs/coordination/plan.md`、UI 静态文件、`demo_server.py`、`demo.py`、`cli.py`、controller / runner / scenario。
- 未新增 runtime dependency、schema、validator、raw JSON copy affordance、second answer payload、UI-side inference 或新的 control truth。

### 浏览器限制说明

- Safari / Chrome 的 Apple Events JavaScript 均未启用，因此无法通过 AppleScript 在浏览器页内自动点击第二个 prompt。
- macOS `System Events` click 被拒绝，因此未将第二个 prompt 声称为“浏览器点击交互完成”。
- 第二个 prompt 已通过真实 `POST /api/demo` 路径验证；UI 的相同 `DemoAnswer` 渲染路径仍由默认 bridge prompt 的浏览器视觉检查和静态测试覆盖。

### Freeze candidate 判断

- 当前 UI 可作为 freeze candidate。
- 剩余风险是没有浏览器 E2E 自动化证明，但这符合本轮非目标。
- 若下一轮继续做 UI，只建议非常小的现场手测文案 / spacing polish；不要回到 schema / validator / raw JSON micro-affordance 路线。

### 验证

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
- 行为断言：
  - `nominal_logic4_any True`
  - `nominal_throttle_lock_release_any True`
  - `retract_clear True`
- 结果：
  - `tests.test_demo`: 62 tests OK。
  - 全量回归：115 tests OK。
  - demo JSON smoke 通过。
  - `run nominal-deploy --format json` smoke 通过。

## Round 78 开发任务：UI demo clean-window visual QA and freeze candidate

### 当前状态

- Round 77 已完成并通过当前工作区复核。
- 当前全量回归：`115 tests OK`。
- 当前项目目录不是 Git 仓库；不要依赖 `git diff` 做变更判断。
- 本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 当前 UI 已经是 demo-ready showcase surface：
  - `Deploy-chain reasoning cockpit`
  - prompt 输入与四个核心示例 prompt
  - fixed control chain
  - highlight explanation
  - structured answer 主干
  - raw JSON debug inspector 折叠降权
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

做一次干净浏览器窗口的视觉 QA，并把当前 UI 作为 freeze candidate 收口。

如果干净窗口下已经可展示，优先不要改代码；只更新交接 / QA 记录。

如果仍有第一屏展示阻塞，只允许做极小 HTML / CSS 修正，不要再加新功能。

### 建议执行

- 使用空闲端口启动 UI，例如：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
- 用干净浏览器窗口打开本地 URL：
  - 优先新窗口 / 隐身窗口 / 临时 profile。
  - 如果本机浏览器状态污染严重，明确说明原因，不要声称完成干净窗口验收。
- 至少检查两个 prompt：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 throttle lock 没释放`
- 至少检查两个视口：
  - 桌面宽屏。
  - 窄屏 / 移动宽度，手动 resize 即可。
- 检查重点：
  - 第一屏是否像可展示 Demo UI，而不是内部调试页。
  - prompt 输入与四个示例 prompt 是否清楚可见。
  - fixed control chain 是否容易扫读。
  - `logic4 / THR_LOCK` 与 `logic3 / EEC / PLS / PDU` 高亮是否能区分。
  - highlight explanation 与 structured answer 的关系是否清楚。
  - `possible_causes / evidence / risks` 是否容易扫读。
  - raw JSON debug inspector 是否保留但不抢主视觉。
  - 窄屏下是否仍按 prompt -> chain -> answer 顺序阅读。

### 允许修正

- 只允许极小 HTML / CSS 修正：
  - spacing
  - font size / line-height
  - panel hierarchy
  - chain readability
  - button / card visual weight
  - narrow-screen wrapping
  - raw JSON debug inspector visual weight
- 只有在视觉阻塞无法用 CSS 解决时，才允许极小 `demo.js` 调整。
- 如修改静态结构 / class，更新对应轻量静态测试。

### 非目标

- 不继续做 raw JSON copy affordance。
- 不继续扩 schema validation 工具链。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、真实 screenshot 文件或截图标注资产。
- 不接入真实 LLM / agent 系统。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario、second payload、UI-side inference 或新的 control truth。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 明确回报是否完成干净浏览器窗口 visual QA。
2. 若完成，说明使用的浏览器 / 打开方式 / 端口 / 检查过的视口。
3. 若无法完成，明确说明原因，不得把静态测试说成真实浏览器验证。
4. `logic4 和 throttle lock 有什么关系` 在桌面宽屏下可展示 prompt、chain highlight、highlight explanation、structured answer 主干。
5. `为什么 throttle lock 没释放` 能清楚展示 `possible_causes / evidence / risks`。
6. 窄屏下仍能按 prompt -> chain -> answer 顺序阅读。
7. raw JSON debug inspector 保留但不抢主视觉。
8. 如无需修正，明确回报当前 UI 可作为 freeze candidate。
9. 如有修正，新增或更新轻量静态测试覆盖对应 HTML / CSS class 或文案。
10. 当前 `115 tests OK` 基线继续通过。
11. 现有 CLI 行为保持不变。
12. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 是否完成干净浏览器窗口 visual QA。
- 使用的浏览器 / 端口 / 视口。
- 是否需要代码修正；如果需要，改了哪些文件。
- 当前 UI 是否可作为 freeze candidate。
- raw JSON 是否仍只是 debug inspector。
- UI/API 是否仍复用现有 demo reasoning layer。
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变。
- 跑了哪些测试。
- 下一轮是否还有必须处理的 UI 展示面阻塞。

## Round 77 接手继续完成：UI demo showcase finishing pass

### 结论

PASS。接手 Gemini 3.1 Pro 已完成的深色 engineering dashboard / cockpit 风格后，继续做小范围 showcase finishing，没有回到 schema / validator / raw JSON micro-affordance 路线。

### 已完成

- 先执行用户指定的 `git diff -- ...`，但当前目录不是 Git 仓库，命令返回 `Not a git repository`；因此本轮以当前工作区文件为准，未做任何 git 回滚或覆盖。
- 阅读并保留现有 UI 核心结构：
  - `showcase-surface`
  - grouped example prompts
  - fixed control chain
  - highlight explanation
  - structured answer / compact answer guide
  -折叠 raw JSON debug inspector
- 使用本地 server 检查 UI：
  - 默认 `PYTHONPATH=src python3 -m well_harness.demo_server --open` 因本机 `127.0.0.1:8000` 已有 Python 进程占用而失败。
  - 改用 `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766 --open` 继续检查，不改变默认 server 行为。
- `src/well_harness/static/demo.html`：
  - 将 hero eyebrow 从 `well-harness local UI demo shell` 收敛为 `well-harness deterministic demo cockpit`。
  - 将 hero title 收敛为 `Deploy-chain reasoning cockpit`。
  - 将 mission 文案压短为 prompt -> highlighted control chain -> structured answer 的 first-screen demo surface。
- `src/well_harness/static/demo.css`：
  - 保留 Gemini 的深色 technical cockpit 风格。
  - 修复 `.showcase-grid` 原先只在注释里存在 `grid-template-areas` 的问题，改成真实三栏 grid：prompt / chain / answer。
  - 加入 `overflow-x: hidden`，降低路线条 / 宽面板造成页面横向漂移的风险。
  - 强化 chain panel：增加 cockpit 背景、边框、节点间距、active highlight 的柔和 green glow，让 control chain 成为主视觉之一。
  - 强化 structured answer：output card 边框更清楚，section card 使用渐变背景与左侧 accent border，便于扫读 evidence / outcome / possible_causes / risks。
  - raw JSON 保留为折叠 debug inspector，并通过透明度与 dashed border 降低视觉权重。
  - 移除 CSS 内部 `Test string hacks` 注释，改成真实 `.raw-card .debug-inspector` 规则。
  - 保留移动端单列 prompt -> chain -> answer 结构。
- `tests/test_demo.py`：
  - 更新 showcase static asset 测试，覆盖真实 cockpit grid、chain panel、output card、raw JSON 降权、移动端单列，不再依赖旧浅色布局 token。
- 未修改 `docs/coordination/plan.md`。
- 未新增 runtime dependency、schema、validator、Node / Vite / Next、second payload、UI-side inference 或新的 control truth。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_route_strip tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_mobile_answer_guide_spacing`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`

### 当前注意事项

- 本轮没有改 `demo_server.py`、`demo.py`、`cli.py`、controller / runner / scenario。
- UI/API 仍通过 `POST /api/demo` 复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 还需要在最终收尾前按用户要求跑：
  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
  - `PYTHONPATH=src python3 -m unittest tests.test_demo`
  - `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
  - demo JSON / run JSON smoke。

## Round 77 开发完成记录：UI demo real browser visual hand-check and first-screen fixes

### 结论

PASS，带一个明确边界：真实浏览器桌面首屏 hand-check 已完成；窄屏真实窗口自动调整受本机 Chrome 窗口状态限制，未作为完整浏览器窄屏验证结论，只做了 CSS/media-rule 修复与静态回归保护。

### 已完成

- 启动本地 UI server：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8765`
- 使用已有 Google Chrome profile 打开本地 UI：
  - `http://127.0.0.1:8765/?round77=existing-profile`
  - `http://127.0.0.1:8765/?round77=existing-profile-after-chain-compact`
  - `http://127.0.0.1:8765/?round77=existing-profile-after-prompt-compact`
- 在真实 Chrome 桌面窗口中检查 `logic4 和 throttle lock 有什么关系`：
  - 首屏现在明显是 demo-ready showcase surface，而不是内部调试页。
  - prompt 输入区、四个核心示例、fixed control chain、structured answer 主干同屏可见。
  - `logic4 / THR_LOCK` 高亮、highlight explanation、structured answer 的关系比 Round 76 更清楚。
  - raw JSON 仍保留为折叠 debug inspector，没有抢主视觉。
- 修复首屏展示阻塞：
  - `src/well_harness/static/demo.css` 压缩 showcase 内 chain panel 的节点尺寸、header 间距和 highlight explanation 间距，让 `logic4 / THR_LOCK` 末端节点在桌面首屏更稳定可见。
  - 压缩 showcase 内 prompt 示例卡、示例按钮、textarea 和 prompt hint，让 prompt 输入与四个示例更稳定同屏可见。
  - 修复窄屏示例区域：长 prompt button 允许断行，`max-width: 780px` 下 grouped examples 回到单列并取消 grid item 撑宽，减少移动端横向溢出风险。
  - 未改 `demo.html` / `demo.js`，未改 API / reasoning layer。
- 更新 `tests/test_demo.py` 的 showcase surface 静态测试，覆盖：
  - 三列 showcase grid。
  - showcase grouped examples。
  - prompt button 断行。
  - showcase textarea compact rule。
  - compact chain / highlight explanation rules。
  - 窄屏 grouped examples 单列与 `width: auto` 修复。
- 尝试窄屏真实浏览器检查：
  - Chrome headless `430x1200` 能写出截图文件，但本机该路径多次出现 timeout / garbled capture，不作为可靠视觉结论。
  - AppleScript 调整 Chrome 窗口宽度时选中本机另一个 arXiv Chrome 窗口，无法可靠定位 demo 窗口，因此不声称完成真实窄屏浏览器验证。
- 未修改 `docs/coordination/plan.md`。
- 未新增 runtime dependency、schema、validator、raw JSON copy affordance、second payload、UI-side inference 或新的 control truth。

### 验证

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_mobile_answer_guide_spacing tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_compact_answer_guide_layout tests.test_demo.DemoIntentLayerTests.test_demo_server_main_open_affordance_uses_helper_and_continues_serving`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 验证结果

- 定向 showcase / UI 回归测试：4 tests OK。
- `tests.test_demo`: 62 tests OK。
- 全量回归：115 tests OK。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- 行为断言通过：`nominal-deploy` 仍到达 `logic4` 且 `throttle_lock_release_cmd` 仍触发，`retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。

### 剩余风险

- 本轮真实浏览器 hand-check 覆盖了桌面 Chrome 首屏；窄屏仍主要由 CSS/media-rule 静态测试保护，不是浏览器 E2E 自动化证明。
- 展示面修复是 HTML/CSS 首屏 polish，不是新的 reasoning、schema、payload 或控制真值。

## Round 77 开发任务：UI demo real browser visual hand-check and first-screen fixes

### 当前状态

- Round 76 已通过指挥侧复核。
- 当前全量回归：`115 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
  - 可选启动便利：`PYTHONPATH=src python3 -m well_harness.demo_server --open`
- Round 76 已经把页面从内部调试页推进成 demo-ready `showcase-surface`：
  - prompt / 示例 prompt
  - fixed control chain
  - highlight explanation
  - structured answer 主干
  - raw JSON debug inspector 降级为折叠调试视图
- 当前剩余风险不是缺功能，而是真实浏览器首屏观感还没有被人工确认。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，做一次真实浏览器视觉 hand-check，并只修正阻碍 Demo UI 展示的首屏可读性问题。

### 建议执行

- 启动本地 UI：
  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 在真实浏览器里人工检查首屏：
  - 是否一眼能看出这是 well-harness deterministic reasoning demo。
  - prompt 输入和四个示例 prompt 是否清楚可见。
  - fixed control chain 是否容易扫读。
  - `logic4 和 throttle lock 有什么关系` 默认回答是否能展示 chain highlight / highlight explanation / structured answer。
  - raw JSON inspector 是否保留但不抢主视觉。
  - 窄屏 / 移动宽度下是否还能按 prompt -> chain -> answer 顺序读。
- 如发现问题，优先做小范围 HTML / CSS 修复：
  - 首屏 spacing
  - panel 层级
  - 字体大小 / 行距
  - chain 可读性
  - debug inspector 视觉权重
- 只在必要时做极小 `demo.js` 调整，不要新增复杂状态。
- 如果浏览器环境无法打开，也要运行 server 并记录无法执行真实浏览器手测的原因；此时只做静态检查，不要假装完成浏览器手测。

### 非目标

- 不继续做 raw JSON copy affordance。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增浏览器驱动或自动点击 / 自动断言。
- 不新增新的 answer payload 或 UI-side inference。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 开发会话明确回报是否完成真实浏览器 visual hand-check。
2. 若完成 hand-check，回报浏览器打开方式和检查过的视口 / 场景。
3. 若无法完成 hand-check，明确说明原因，不得把静态测试说成真实浏览器验证。
4. 首屏仍明显是可展示 demo surface。
5. prompt 输入、示例 prompt、fixed control chain、structured answer 主干仍清楚可见。
6. `logic4 和 throttle lock 有什么关系` 仍能展示 chain highlight / highlight explanation / structured answer。
7. raw JSON debug inspector 保留但不抢主视觉。
8. 窄屏布局仍能按 prompt -> chain -> answer 顺序扫读。
9. 如有修复，新增或更新轻量静态测试覆盖对应 HTML / CSS class 或文案。
10. 当前 `115 tests OK` 基线继续通过。
11. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
12. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 是否完成真实浏览器 visual hand-check
- 用什么方式打开 UI，检查了哪些视口 / 场景
- 如有修复，改了哪些文件
- 首屏展示面是否清楚呈现 prompt / chain / structured answer 主干
- raw JSON inspector 是否保留但不抢主视觉
- 如何确保没有新增第二套 payload、新 schema、UI-side inference 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 76 开发完成记录：UI demo showcase surface pass

### 结论

PASS。

### 已完成

- 在 `src/well_harness/static/demo.html` 新增 `showcase-mission`、`showcase-surface`、`showcase-intro`、`showcase-grid`，把 prompt、fixed control chain、structured answer 主干组合成第一屏 demo-ready surface。
- 保留四个核心示例 prompt：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 throttle lock 没释放`
  - `触发 logic3 会发生什么`
  - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
- `src/well_harness/static/demo.css` 新增 showcase layout：
  - hero 更像 demo title / boundary surface。
  - route strip 更轻量，避免像文档清单抢占主视觉。
  - 桌面端 `showcase-grid` 使用 prompt 左侧、chain / answer 右侧的展示布局。
  - 窄屏下 `showcase-grid` 回到 prompt -> chain -> answer 单列。
- raw JSON 保留为同一份 `DemoAnswer` payload 的 debug view，但从默认展开 panel 降级为折叠 `debug-inspector`。
- 保持 `Answer sections` summary、`Audience answer-field legend`、highlight explanation、selected prompt、Cmd/Ctrl+Enter、loading / empty / API error、mobile answer guide spacing 等既有 UI 行为。
- 未改 `demo_server.py`、`demo.py`、`cli.py`、controller / runner / scenario。
- 未新增 runtime dependency、schema、validator、second payload、UI-side inference 或新的 control truth。
- README 只补一句本地 UI showcase surface 说明。
- 新增 `tests/test_demo.py` 静态测试覆盖 showcase surface HTML / CSS / README 文案，并更新 raw JSON details 断言为 inspector 形态。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_mobile_answer_guide_spacing tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_compact_answer_guide_layout`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 验证结果

- `tests.test_demo`: 62 tests OK。
- 全量回归：115 tests OK。
- `nominal-deploy` 仍到达 `logic4`，且 `throttle_lock_release_cmd` 仍触发。
- `retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。
- `demo_server --open` help 文案仍存在。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。

### 剩余风险 / 下一轮建议

- showcase surface 是静态 HTML / CSS 展示面优化，不是浏览器 E2E 证明。
- 若继续增强，建议做少量真实浏览器视觉手测或非常轻量的首屏可读性 polish；不要回到 validator / schema / raw JSON micro-affordance 惯性。

## Round 76 开发任务：UI demo showcase surface pass

### 当前状态

- Round 75 已通过指挥侧复核。
- 当前全量回归：`114 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
  - 可选启动便利：`PYTHONPATH=src python3 -m well_harness.demo_server --open`
- 当前 UI 已经有完整功能，但过去多轮偏向细节 polish / hand-check / 文档辅助。
- 当前必须停止继续做 validator / schema / raw JSON copy / 微型 affordance 惯性，转向一个能直接给人看的 demo 展示面。
- 当前 UI 已包含 presenter callout labels、screenshot-free presenter route strip、`Presenter Readiness Run Card`、answer-to-chain highlight explanation、compact `answer-guide`、`Audience answer-field legend`、`Answer sections` summary、移动端 / 窄屏 answer guide spacing polish 和可折叠 raw JSON debug。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，对本地 UI 做一次 demo-ready showcase surface pass。

### 目标

让浏览器打开 `PYTHONPATH=src python3 -m well_harness.demo_server --open` 后，第一屏就是一个可展示的 Demo UI：

- 视觉上清楚地告诉观众这是 well-harness 的 deterministic reasoning demo。
- 第一屏能看到 prompt 输入 / 示例 prompt / control chain / 结构化答案区域的主干，不像内部调试页。
- control chain、highlight explanation、structured answer、raw JSON debug 的关系更清楚。
- raw JSON 仍保留，但不抢主视觉；它应该像 debug / inspector，而不是页面的主角。
- 现有 route strip / callout labels / answer guide 可以保留，但要融入展示面，不要显得像堆叠的辅助文档。

### 建议实现

- 优先改 `src/well_harness/static/demo.html` 与 `src/well_harness/static/demo.css`。
- 必要时只做极小 `demo.js` 调整，不要新增复杂状态机。
- 强化首屏视觉层级：
  - hero 区更像 demo title / scenario boundary，而不是普通文档标题。
  - prompt panel 和 chain panel 在桌面端形成更清楚的 showcase layout。
  - structured answer / answer guide / raw JSON 在视觉上分出主次。
- 可考虑增加一个轻量 “Demo flow” 或 “What to show first” 小区域，但不要再扩成长 hand-check 文档。
- 继续保留四个核心示例 prompt：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 throttle lock 没释放`
  - `触发 logic3 会发生什么`
  - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
- 保持现有功能不回归：
  - loading / empty / API error
  - selected prompt
  - Cmd/Ctrl+Enter
  - chain highlight
  - highlight explanation
  - `Answer sections` summary
  - `Audience answer-field legend`
  - raw JSON details
  - mobile answer guide spacing
  - `demo_server --open`
- README 只补最短展示运行方式和“这是 demo showcase surface”的说明，不要继续堆 validator / schema 文档。

### 非目标

- 不继续做 raw JSON copy affordance；除非 showcase surface 已完成且只需极小顺手整理。
- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增浏览器驱动或自动点击 / 自动断言。
- 不新增新的 answer payload 或 UI-side inference。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 本地 UI 第一屏明显像一个可展示 demo surface，而不是内部调试页或文档清单。
2. 第一屏保留可操作 prompt 输入和示例 prompt。
3. 第一屏或紧随其后能清楚看到 fixed control chain。
4. 运行 `logic4 和 throttle lock 有什么关系` 后，chain highlight、highlight explanation、structured answer 三者关系更容易看懂。
5. 运行 `为什么 throttle lock 没释放` 后，`possible_causes` / `evidence` / `risks` 仍清楚可见。
6. raw JSON debug 保留但视觉上降级为 inspector / debug view，不抢主展示面。
7. 页面仍明确边界：deterministic controlled demo layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。
8. `demo_server --open` 不回归。
9. Round 75、Round 74、Round 73 的关键 UI 行为不回归。
10. 新增或更新轻量静态测试覆盖 showcase surface 的关键 HTML / CSS 文案与布局 class。
11. 当前 `114 tests OK` 基线继续通过，并新增本轮 showcase surface 测试。
12. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
13. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- demo-ready showcase surface 如何呈现
- 第一屏如何展示 prompt / chain / structured answer 主干
- raw JSON 如何保留但不抢主视觉
- 如何确保没有新增第二套 payload、新 schema、UI-side inference 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 75 开发完成记录：UI demo optional browser launch affordance

### 结论

PASS。

### 已完成

- 在 `src/well_harness/demo_server.py` 新增可选 `--open` 参数。
- 默认不带 `--open` 时，仍按既有路径：
  - 绑定 host / port。
  - 打印 `Serving well-harness demo UI at ...`。
  - 进入 `serve_forever()`。
- 带 `--open` 时：
  - 仍打印本地 UI URL。
  - 使用 Python 标准库 `webbrowser.open(...)` 尝试打开 URL。
  - 仍进入 `serve_forever()`。
- 新增轻量 helper：
  - `demo_url(host, port)`
  - `open_browser(url, opener=webbrowser.open)`
- `open_browser(...)` 在 opener 返回 false 或抛异常时打印清楚提示：
  - `Could not open browser automatically... Open <url> manually.`
  - 返回 `False`，但不阻止 server 继续启动。
- `--open` 文案明确它只是 launch convenience，不是 browser E2E automation。
- `POST /api/demo` 仍直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`，未改 UI/API payload。
- 更新 `README.md`、`docs/demo_presenter_talk_track.md`、`tools/demo_ui_handcheck.py`，说明默认仍可手动打开 URL，`--open` 只是标准库浏览器启动便利。
- 新增 `tests/test_demo.py` 测试覆盖：
  - `demo_url(...)` helper。
  - `open_browser(...)` 成功 / false / exception 分支。
  - `well_harness.demo_server --help` 中 `--open` 文案。
  - `demo_server.main([... "--open"])` 使用 fake server，不启动长期 server，并确认 `serve_forever()` / `server_close()` 仍被调用。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_open_browser_helper_reports_failures tests.test_demo.DemoIntentLayerTests.test_demo_server_help_documents_optional_open_affordance tests.test_demo.DemoIntentLayerTests.test_demo_server_main_open_affordance_uses_helper_and_continues_serving tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_manual_checklist tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_presenter_walkthrough tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_includes_readiness_run_card`
- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 验证结果

- `tests.test_demo`: 61 tests OK。
- 全量回归：114 tests OK。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。

### 剩余风险 / 下一轮建议

- `--open` 是标准库浏览器启动便利，不是浏览器 E2E、截图工具、自动 readiness detector 或新的控制真值。
- 若继续增强 UI，建议只做轻量现场可用性 polish 或手测说明，不要回到 schema / validator 工具链。

## Round 75 开发任务：UI demo optional browser launch affordance

### 当前状态

- Round 74 已通过指挥侧复核。
- 当前全量回归：`111 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前 UI 已包含 presenter callout labels、screenshot-free presenter route strip、`Presenter Readiness Run Card`、answer-to-chain highlight explanation、compact `answer-guide`、`Audience answer-field legend`、`Answer sections` summary、移动端 / 窄屏 answer guide spacing polish 和可折叠 raw JSON debug。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为 `well_harness.demo_server` 增加一个可选的浏览器打开 affordance。

### 建议实现

- 在 `src/well_harness/demo_server.py` 增加可选参数：
  - `--open`
- 默认不带 `--open` 时，现有行为保持不变：
  - 绑定 host / port
  - 打印 `Serving well-harness demo UI at ...`
  - 进入 `serve_forever()`
- 带 `--open` 时：
  - 使用 Python 标准库 `webbrowser.open(url)` 打开本地 UI URL。
  - 仍然打印本地 URL。
  - 仍然进入 `serve_forever()`。
  - 如果浏览器打开失败，打印清楚提示但继续 serve。
- 建议抽出很小的 helper，便于测试：
  - `demo_url(host, port)` 或等价函数
  - `open_browser(url)` 或等价薄包装
- 更新 `tools/demo_ui_handcheck.py` / `docs/demo_presenter_talk_track.md` / README 时，只补一句：
  - 默认命令仍是手动打开 URL。
  - 如想自动打开浏览器，可用 `PYTHONPATH=src python3 -m well_harness.demo_server --open`。
- 不要把 `--open` 写成浏览器 E2E automation；它只是标准库打开 URL 的启动便利。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增浏览器驱动或自动点击 / 自动断言。
- 不新增新的 answer payload 或 UI-side inference。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. `PYTHONPATH=src python3 -m well_harness.demo_server` 默认行为保持不变。
2. `PYTHONPATH=src python3 -m well_harness.demo_server --open` 会使用标准库尝试打开本地 UI URL。
3. `--open` 失败时有清楚提示，并且不阻止 server 继续启动。
4. `--help` 能看到 `--open` 说明。
5. `--open` 不使用 Playwright / Selenium / Node / 新依赖，不驱动页面交互，也不是 E2E automation。
6. `POST /api/demo` 仍直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
7. Round 74 mobile answer guide spacing 不回归。
8. Round 73 compact answer guide 不回归。
9. Round 72 audience answer-field legend 不回归。
10. Round 71 screenshot-free presenter route strip 不回归。
11. 新增或更新轻量测试覆盖 `demo_server --open` parser / helper / help 文案，避免启动长期 server。
12. 当前 `111 tests OK` 基线继续通过，并新增本轮 launch affordance 测试。
13. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
14. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- `demo_server --open` 如何运行
- 默认 `demo_server` 行为是否保持不变
- `--open` 失败时如何提示并继续启动
- 如何明确它不是 E2E automation、截图工具、自动 readiness detector 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 74 开发完成记录：UI demo mobile answer guide spacing polish

### 结论

PASS。

### 已完成

- 在 `src/well_harness/static/demo.css` 中对 compact `answer-guide` 增加窄屏 spacing polish：
  - `@media (max-width: 780px)` 下收紧 `answer-guide` padding / gap / margin。
  - `answer-guide-intro` 改为更清楚的纵向排布，并提高说明文字行距。
  - `answer-guide-grid` 继续保持单列布局，并调整 legend / summary 之间的 gap。
  - `answer-field-legend` 与 `answer-section-summary` 在窄屏下使用更紧凑 padding / radius。
  - `summary-chip` 在窄屏下增加触控高度、左右 padding、行距，并允许长文案换行。
  - `button.summary-chip` 在窄屏下左对齐，便于扫读。
  - `@media (max-width: 520px)` 下让 summary chips 单列铺满宽度。
- 保持原有 HTML 结构和稳定 id 不变：
  - `answer-guide`
  - `answer-guide-grid`
  - `answer-field-legend`
  - `answer-section-summary`
  - `answer-section-summary-items`
  - `answer-section-keyboard-hint`
- 未新增 JS 状态，未改 `demo.js`，未改 UI/API payload。
- 保持 `Answer sections` chip click/focus 与方向键导航不变。
- 空 section 与 UI/API error unavailable 状态不变。
- 更新 `docs/demo_presenter_talk_track.md`，说明移动端 / 窄屏也按 compact answer guide 纵向走查。
- 更新 `tools/demo_ui_handcheck.py --walkthrough`，提醒窄屏下 top-to-bottom 读 compact answer guide。
- 更新 `README.md`，补充窄屏下 compact answer guide 使用 touch-friendly spacing 且不改变 `DemoAnswer` payload。
- 新增 `tests/test_demo.py` 静态回归测试，覆盖 mobile / narrow-screen answer guide spacing 的 HTML / CSS / README / talk track / walkthrough 引用。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_mobile_answer_guide_spacing tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_compact_answer_guide_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_audience_answer_field_legend tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 验证结果

- `tests.test_demo`: 58 tests OK。
- 全量回归：111 tests OK。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。

### 剩余风险 / 下一轮建议

- mobile answer guide spacing 是静态 CSS polish，不是浏览器 E2E 证明。
- 若继续增强 UI，建议做轻量现场可读性 polish 或手测说明，不要回到 schema / validator 工具链。

## Round 74 开发任务：UI demo mobile answer guide spacing polish

### 当前状态

- Round 73 已通过指挥侧复核。
- 当前全量回归：`110 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前 UI 已包含 presenter callout labels、screenshot-free presenter route strip、`Presenter Readiness Run Card`、answer-to-chain highlight explanation、compact `answer-guide`、`Audience answer-field legend`、`Answer sections` summary 和可折叠 raw JSON debug。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，优化本地 UI 中 compact `answer-guide` 在移动端 / 窄屏下的 spacing、可读性和触控扫读体验。

### 建议实现

- 优先做 CSS-only polish，必要时只做极小 HTML 文案 / class 调整。
- 保持 `answer-guide`、`answer-guide-grid`、`answer-field-legend`、`answer-section-summary`、`answer-section-summary-items`、`answer-section-keyboard-hint` 等现有结构和 id 不变。
- 在窄屏 media rule 中优化：
  - `answer-guide` padding / gap / margin
  - `answer-guide-intro` 换行与行距
  - `answer-guide-grid` 单列布局 spacing
  - `answer-field-legend` 与 `answer-section-summary` 的视觉间距
  - `summary-chip` / `summary-chips` 触控间距与可读性
- 保持 `Answer sections` chip click/focus 与方向键导航行为不变。
- 空 section / UI/API error unavailable 状态不应回归。
- legend 仍应说明它只是 reading aid，不是新 schema、新 payload 或新控制真值。
- 如更新 `docs/demo_presenter_talk_track.md` 或 `tools/demo_ui_handcheck.py --walkthrough`，只补一句移动端也按 compact answer guide 走查即可，不要改变默认清单语义。
- README 只补一句简短说明，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增新的 answer payload 或 UI-side inference。
- 不新增复杂 answer navigator。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. compact `answer-guide` 在移动端 / 窄屏下 spacing 更清楚，字段 legend 与 section summary 不挤压。
2. `answer-guide-grid` 在窄屏下保持单列或等价响应式布局。
3. `answer-guide-intro`、legend、summary chips 在窄屏下保持可读与可触控。
4. `answer-field-legend`、`answer-section-summary`、`answer-section-summary-items`、`answer-section-keyboard-hint` 等现有 id 保持不变。
5. `Answer sections` chip click/focus 与方向键导航不回归。
6. 空 section 与 UI/API error unavailable 状态不回归。
7. legend 仍明确它不是新 schema、新 payload 或新的控制真值。
8. Round 73 compact answer guide 不回归。
9. Round 72 audience answer-field legend 不回归。
10. Round 71 screenshot-free presenter route strip 不回归。
11. Round 70 readiness run card 不回归。
12. Round 69 presenter callout labels 不回归。
13. 新增或更新轻量静态测试覆盖 mobile / narrow-screen answer guide spacing 的 HTML / CSS / 文档引用。
14. 当前 `110 tests OK` 基线继续通过，并新增本轮 mobile spacing 测试。
15. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
16. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- mobile / narrow-screen answer guide spacing 如何优化
- 如何确认 legend 与 Answer sections summary 的语义没有变化
- 如何确保没有新增 DemoAnswer 字段、新 schema、新 payload 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 73 开发完成记录：UI demo compact answer guide layout

### 结论

PASS。

### 已完成

- 在 `src/well_harness/static/demo.html` 的 `Structured output` 区域新增 `answer-guide` wrapper，把 `Audience answer-field legend` 与 `Answer sections` summary 组合成同一个 compact answer guide。
- 在 `src/well_harness/static/demo.css` 新增 `answer-guide`、`answer-guide-intro`、`answer-guide-grid` 布局样式：
  - 桌面端使用两列 grid，让字段 legend 与 section count summary 更紧凑地并排呈现。
  - 移动端回到单列，保持可读性。
- 保留原有稳定 id：
  - `answer-field-legend`
  - `answer-section-summary`
  - `answer-section-summary-items`
  - `answer-section-keyboard-hint`
- 未新增 `DemoAnswer` 字段，未新增 schema，未新增 payload，也未新增 UI-side inference 或控制真值。
- 保持 `Answer sections` chip click/focus、方向键导航、empty section 与 UI/API error unavailable 状态不变。
- 更新 `docs/demo_presenter_talk_track.md`，说明 legend 与 `Answer sections` summary 是同一个 compact answer guide，且描述同一份 `DemoAnswer` payload。
- 更新 `tools/demo_ui_handcheck.py --walkthrough`，提醒演示者用 compact answer guide 同时说明字段 legend 与 section counts。
- 更新 `README.md` 的 UI demo 说明。
- 新增 `tests/test_demo.py` 静态回归测试，覆盖 compact answer guide 的 HTML / CSS / talk track / README / walkthrough 引用。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_compact_answer_guide_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_audience_answer_field_legend tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_route_strip`
- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 验证结果

- `tests.test_demo`: 57 tests OK。
- 全量回归：110 tests OK。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。

### 剩余风险 / 下一轮建议

- compact answer guide 是静态视觉布局 polish，不是浏览器 E2E 证明。
- 若继续增强 UI，建议只做小范围可读性 polish，例如更紧凑的移动端 spacing 或现场视觉提示，不要回到 schema / validator 工具链。

## Round 73 开发任务：UI demo compact answer guide layout

### 当前状态

- Round 72 已通过指挥侧复核。
- 当前全量回归：`109 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前 UI 已包含 presenter callout labels、screenshot-free presenter route strip、`Presenter Readiness Run Card`、answer-to-chain highlight explanation、`Answer sections` summary、`Audience answer-field legend` 和可折叠 raw JSON debug。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，优化本地 UI 中 `Audience answer-field legend` 与 `Answer sections` summary 的视觉关系，形成轻量 compact answer guide layout。

### 建议实现

- 将 `Audience answer-field legend` 和 `Answer sections` summary 组合成一个更清楚的 answer guide 区域。
- 可以新增轻量 wrapper，例如 `answer-guide`，包含：
  - `Audience answer-field legend`
  - `Answer sections`
- 也可以在现有结构上用 CSS 让两者在桌面端并排或上下更紧凑，在移动端保持单列。
- 继续使用原生 `<details>`；不要新增复杂 JS 状态。
- 保持 `Answer sections` chip click/focus 与方向键导航行为不变。
- 空 section / error unavailable 状态不应回归。
- legend 仍应说明它只是 reading aid，不是新 schema、新 payload 或新控制真值。
- 如更新 `docs/demo_presenter_talk_track.md`，只补一句：legend 与 section summary 是同一个 answer guide 区域。
- 如更新 `tools/demo_ui_handcheck.py --walkthrough`，只补一句提醒，不要改变默认清单语义。
- README 只补一句简短说明，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增新的 answer payload 或 UI-side inference。
- 不新增复杂 answer navigator。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 中存在更清楚的 compact answer guide layout，能把 `Audience answer-field legend` 与 `Answer sections` summary 关联起来。
2. legend 和 summary 的现有语义保持不变，不新增 `DemoAnswer` 字段。
3. 桌面端或宽屏下两者视觉关系更紧凑；移动端保持可读单列或等价响应式布局。
4. `Answer sections` chip click/focus 与方向键导航不回归。
5. 空 section 与 UI/API error unavailable 状态不回归。
6. legend 仍明确它不是新 schema、新 payload 或新的控制真值。
7. Round 72 audience answer-field legend 不回归。
8. Round 71 screenshot-free presenter route strip 不回归。
9. Round 70 readiness run card 不回归。
10. Round 69 presenter callout labels 不回归。
11. 新增或更新轻量静态测试覆盖 compact answer guide 的 HTML / CSS / 文档引用。
12. 当前 `109 tests OK` 基线继续通过，并新增本轮 layout 测试。
13. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
14. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- compact answer guide layout 如何呈现
- legend 与 Answer sections summary 如何视觉关联
- 如何确保没有新增 DemoAnswer 字段、新 schema、新 payload 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 72 开发完成记录：UI demo audience answer-field legend

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在 `Structured output` 区域新增原生 `<details id="answer-field-legend" class="answer-field-legend">`。
  - legend 覆盖字段：
    - `intent`
    - `matched_node`
    - `target_logic`
    - `evidence`
    - `outcome`
    - `possible_causes`
    - `required_changes`
    - `risks`
    - `raw JSON`
  - 明确 `intent` 是 controlled demo intent，不是 open-ended LLM intent recognition。
  - 明确 `possible_causes` / `risks` 不是 complete root-cause proof。
  - 明确 `required_changes` 是 dry-run / proposal guidance，不直接修改 `controller.py`。
  - 明确 raw JSON 是同一份 `DemoAnswer` payload 的 machine-readable debug view，不是第二套 answer。
  - 明确 legend 只是 reading aid，不改变 UI/API payload，不创建 schema，也不增加新的 control-truth source。

- `src/well_harness/static/demo.css`
  - 新增 `.answer-field-legend`、`.answer-field-legend summary`、`.answer-field-legend dl/dt/dd/p` 样式。
  - 在窄屏 media rule 中让 legend 字段解释从双列变为单列，保持移动端可读。

- `docs/demo_presenter_talk_track.md`
  - 开场中新增指引：当观众询问字段含义时，打开 `Audience answer-field legend`。
  - 保持它是 reading aid，不是新 schema / payload / control truth 的边界。

- `tools/demo_ui_handcheck.py`
  - `--walkthrough` 增加一句：
    - `If field names need explaining, open the Audience answer-field legend in Structured answer.`
  - 默认 hand-check 清单语义保持不变。

- `tests/test_demo.py`
  - 新增 `test_demo_static_assets_include_audience_answer_field_legend`。
  - 覆盖 legend HTML / CSS / talk track / walkthrough 引用。
  - Round 71 route strip、Round 70 readiness run card、Round 69 presenter callout labels、Round 64 summary chip keyboard navigation 回归测试继续通过。

- `README.md`
  - 补充 audience answer-field legend 的一句说明。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_audience_answer_field_legend tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_route_strip tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_includes_readiness_run_card tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation`
- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 结果

- `tests.test_demo`: 56 tests OK。
- 全量测试结果：109 tests OK。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 行为断言通过：`nominal-deploy` 仍到达 `logic4`，`retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。

### 剩余风险

- legend 是观众阅读辅助，不是正式 JSON Schema、fixture contract 或新的 answer payload。
- legend 没有维护第二套 control truth；后续不要把它扩成 UI-side inference 或 schema 工具链。

## Round 72 开发任务：UI demo audience answer-field legend

### 当前状态

- Round 71 已通过指挥侧复核。
- 当前全量回归：`108 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工演示辅助材料：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
  - `docs/demo_presenter_talk_track.md`
- 当前 UI 已包含 presenter callout labels、screenshot-free presenter route strip、`Presenter Readiness Run Card`、structured output、`Answer sections` summary、highlight explanation 和 raw JSON debug。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 audience-facing answer-field legend。

### 建议实现

- 在 UI 的 Answer header、Structured output 或 compact help 附近新增一个轻量 legend / details。
- legend 建议解释这些字段：
  - `intent`: 受控 demo intent，不是开放式 LLM 意图识别。
  - `matched_node`: answer 关联的 catalog node / alias。
  - `target_logic`: answer 关联的 logic gate。
  - `evidence`: 现有 harness evidence 摘要。
  - `outcome`: demo answer 的结果摘要。
  - `possible_causes`: 受控提示，不是完整根因证明。
  - `required_changes`: dry-run / proposal 下的建议项，不会直接修改 `controller.py`。
  - `risks`: 简化模型和变更风险提示。
  - raw JSON: 同一份 `DemoAnswer` payload 的机器可读 debug 视图，不是第二套答案。
- legend 应短小，偏现场观众可读，不要变成长篇文档。
- 可以用原生 `<details>` / `<summary>`，或一个静态 `<aside>`。
- 如修改 `docs/demo_presenter_talk_track.md`，只补一句让演示者在观众问“字段是什么意思”时指向该 legend。
- 如修改 `tools/demo_ui_handcheck.py --walkthrough`，只补一句提醒，不要改变默认清单语义。
- README 只补一句简短说明，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不新增新的 answer payload 或 UI-side inference。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 中存在轻量 audience answer-field legend。
2. legend 至少覆盖 `intent`、`matched_node`、`target_logic`、`evidence`、`outcome`、`possible_causes`、`required_changes`、`risks`、raw JSON。
3. legend 明确 `intent` 是受控 demo intent，不是开放式 LLM 意图识别。
4. legend 明确 `possible_causes` / `risks` 不是完整根因证明。
5. legend 明确 `required_changes` 是 dry-run / proposal 语境，不直接修改 `controller.py`。
6. legend 明确 raw JSON 是同一份 `DemoAnswer` payload 的 debug 视图，不是第二套答案。
7. legend 不改变 UI/API payload、不维护第二套 answer payload 或控制真值。
8. Round 71 screenshot-free presenter route strip 不回归。
9. Round 70 readiness run card 不回归。
10. Round 69 presenter callout labels 不回归。
11. Round 64 summary chip keyboard navigation 不回归。
12. 新增或更新轻量静态测试覆盖 legend 的 HTML / CSS / 文档引用。
13. 当前 `108 tests OK` 基线继续通过，并新增本轮 legend 测试。
14. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
15. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- answer-field legend 如何呈现
- legend 覆盖哪些字段，以及如何解释 demo 边界
- 如何明确它不是新 schema、新 payload 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 71 开发完成记录：UI demo screenshot-free presenter route strip

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在 hero 后新增 `presenter-route-strip`。
  - route strip 覆盖演示顺序：
    - `1 [Input] choose prompt`
    - `2 [Chain] inspect highlight`
    - `3 [Highlight] explain association`
    - `4 [Structured answer] scan sections`
    - `5 [Raw JSON] verify payload`
  - 明确它是 manual walkthrough guide，不是 browser E2E automation，不是 screenshot annotation tool，也不是 control-truth source。

- `src/well_harness/static/demo.css`
  - 新增 `.presenter-route-strip`、`.route-strip-title`、`.route-step`、`.route-strip-note` 样式。
  - 在窄屏 media rule 中让 route strip 可横向滚动并使用 `scroll-snap-type: x proximity`，保持移动端可读。

- `docs/demo_presenter_talk_track.md`
  - 在开场和 `Presenter Readiness Run Card` 中说明 route strip 对应演示路径。
  - 明确 route strip 是 screenshot-free visual guide，用来替代截图标注式提示。
  - 保持 manual / non-E2E / not control truth 边界。

- `tools/demo_ui_handcheck.py`
  - `--walkthrough` 增加一句：
    - `Use the screenshot-free route strip: Input -> Chain -> Highlight -> Structured answer -> Raw JSON.`
  - 默认 hand-check 清单、Round 66 observations、Round 67 walkthrough、Round 68 talk track、Round 70 readiness run card 保持不回归。

- `tests/test_demo.py`
  - 新增 `test_demo_static_assets_include_presenter_route_strip`。
  - 覆盖 route strip 的 HTML / CSS / talk track / walkthrough 引用。
  - Round 70 readiness run card、Round 69 presenter callout labels、Round 64 summary chip keyboard navigation 回归测试继续通过。

- `README.md`
  - 补充 UI 中 screenshot-free presenter route strip 的一句说明。

### 验证

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_route_strip tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_includes_readiness_run_card tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_callout_labels tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 结果

- `tests.test_demo`: 55 tests OK。
- 全量测试结果：108 tests OK。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 行为断言通过：`nominal-deploy` 仍到达 `logic4`，`retract-reset` 仍清掉 `sw1`、`sw2`、`logic1`、`logic2`、`logic3`、`logic4`。

### 剩余风险

- route strip 是人工演示视觉提示，不是浏览器 E2E 自动化证明。
- route strip 没有维护第二套 answer payload 或 control truth；后续不要把它扩成截图标注系统或 presenter mode 状态机。

## Round 71 开发任务：UI demo screenshot-free presenter route strip

### 当前状态

- Round 70 已通过指挥侧复核。
- 当前全量回归：`107 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工演示辅助材料：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
  - `docs/demo_presenter_talk_track.md`
- 当前 talk track 已包含 `Presenter Readiness Run Card`。
- UI 已具备 presenter callout labels：
  - `[Input]`
  - `[Chain]`
  - `[Highlight]`
  - `[Structured answer]`
  - `[Raw JSON]`
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一个 screenshot-free presenter route strip，帮助演示者按页面区域顺序走查。

### 建议实现

- 在静态 UI 中新增一个轻量 presenter route strip / visual guide，建议放在 hero、compact help 或 callout labels 附近。
- route strip 应使用现有 callout 词，形成短路径，例如：
  - `1 [Input] choose prompt`
  - `2 [Chain] inspect highlight`
  - `3 [Highlight] explain association`
  - `4 [Structured answer] scan sections`
  - `5 [Raw JSON] verify payload`
- route strip 是现场视觉提示，不要生成截图，不要依赖图片，不要自动驱动浏览器。
- route strip 不要改变 API payload，也不要维护第二套 answer payload 或控制真值。
- 如空间允许，可在移动端让 route strip 横向可滚动或自然换行；保持轻量 CSS 即可。
- 更新 `docs/demo_presenter_talk_track.md`，说明 route strip 是 screenshot-free visual guide，用于替代截图标注式提示。
- 如有必要，更新 `tools/demo_ui_handcheck.py --walkthrough` 一句话，提示演示者按 route strip 走：Input -> Chain -> Highlight -> Structured answer -> Raw JSON。
- README 只补一句简短说明，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不新增真实 screenshot 文件或截图标注资产。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 中存在 screenshot-free presenter route strip / visual guide。
2. route strip 至少覆盖 `[Input]`、`[Chain]`、`[Highlight]`、`[Structured answer]`、`[Raw JSON]` 五个区域。
3. route strip 明确用于人工演示走查，不是 browser E2E automation，也不是截图标注工具。
4. route strip 不改变 UI/API payload、不维护第二套 answer payload 或控制真值。
5. route strip 不影响 selected prompt、loading / empty / API error、chain highlight、answer sections summary、raw JSON 折叠等既有行为。
6. `docs/demo_presenter_talk_track.md` 更新说明 route strip 如何对应演示路径。
7. 如修改 `tools/demo_ui_handcheck.py --walkthrough`，默认 hand-check 清单、Round 66 observations、Round 67 walkthrough、Round 68 talk track、Round 70 readiness run card 不回归。
8. 新增或更新轻量静态测试覆盖 route strip 的 HTML / CSS / JS 或文档引用。
9. Round 70 readiness run card 不回归。
10. Round 69 presenter callout labels 不回归。
11. Round 64 summary chip keyboard navigation 不回归。
12. 当前 `107 tests OK` 基线继续通过，并新增本轮 route strip 测试。
13. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
14. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- presenter route strip 如何呈现
- route strip 覆盖哪些 UI 区域，以及如何对应 talk track / run card
- 如何明确它不是 E2E automation、截图标注工具或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 70 开发完成记录：UI demo presenter readiness run card

### 结论

PASS。

### 已完成

- `docs/demo_presenter_talk_track.md`
  - 新增 `Presenter Readiness Run Card`。
  - 明确 run card 是 manual pre-demo check，不是 browser E2E automation，不是 automatic readiness detector，也不是新的 answer payload 或 control truth。
  - 覆盖启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
  - 覆盖本地 URL：`http://127.0.0.1:8000/`。
  - 覆盖 bridge prompt：`logic4 和 throttle lock 有什么关系`。
  - 覆盖页面 callout labels：`[Input]`、`[Chain]`、`[Highlight]`、`[Structured answer]`、`[Raw JSON]`。
  - 覆盖 control chain 高亮、highlight explanation、structured answer、`Answer sections` summary、raw JSON debug。
  - 明确 loading / empty prompt / API error / network error 是 UI 状态，不是 control-logic conclusion。
  - 明确 demo 边界：deterministic controlled demo layer、built-in `nominal-deploy` / `retract-reset` scenarios、simplified first-cut plant、not a full LLM、not a complete physical model。

- `tools/demo_ui_handcheck.py`
  - `--walkthrough` 结尾新增 readiness run card 引用。
  - 默认 hand-check 清单、Round 66 observations、Round 67 walkthrough、Round 68 talk track 引用、Round 69 callout label 引用保持不回归。

- `tests/test_demo.py`
  - 新增 `test_demo_presenter_talk_track_includes_readiness_run_card`。
  - 更新 walkthrough 测试，确认 `--walkthrough` 输出 readiness run card 引用。
  - Round 69 presenter callout labels、Round 68 talk track、Round 64 summary chip keyboard navigation 静态测试继续通过。

- `README.md`
  - 补充 talk track 内含 readiness run card 的一句说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_includes_readiness_run_card tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_covers_core_flow tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_presenter_walkthrough`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_callout_labels tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 54 tests OK。
- 全量回归：107 tests OK。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- readiness run card 是人工演示前检查，不是浏览器 E2E 自动化证明，也不是自动 readiness detector。
- 若继续增强 UI demo，优先补轻量截图标注或更短现场视觉提示，不要回到 schema / validator 工具链。

## Round 70 开发任务：UI demo presenter readiness run card

### 当前状态

- Round 69 已通过指挥侧复核。
- 当前全量回归：`106 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工演示辅助材料：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
  - `docs/demo_presenter_talk_track.md`
- UI 已具备 presenter callout labels：
  - `[Input]`
  - `[Chain]`
  - `[Highlight]`
  - `[Structured answer]`
  - `[Raw JSON]`
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 presenter readiness run card。

### 建议实现

- 优先在 `docs/demo_presenter_talk_track.md` 增加一小段 `Presenter readiness run card`。
- 如不显得拥挤，也可以在 UI 的 compact help 或 callout 附近新增一个轻量 `<details>` readiness checklist；但不要做复杂 presenter mode 或状态机。
- run card 只做人工检查提示，不要自动探测 readiness。
- 建议覆盖：
  - 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`
  - 打开本地 URL。
  - 先运行 bridge prompt：`logic4 和 throttle lock 有什么关系`。
  - 确认页面 callout labels 对齐 talk track：`[Input]`、`[Chain]`、`[Highlight]`、`[Structured answer]`、`[Raw JSON]`。
  - 确认 control chain 高亮和 highlight explanation 可见。
  - 确认 structured answer 与 `Answer sections` summary 可读。
  - 需要机器可读视图时，展开 raw JSON debug。
  - 若出现 loading / empty / API error / network error，说明它是 UI 状态，不是控制逻辑结论。
  - 开场边界提示：deterministic controlled demo layer、内置 `nominal-deploy` / `retract-reset`、simplified first-cut plant、非完整 LLM、非完整物理模型。
- 如修改 `tools/demo_ui_handcheck.py --walkthrough`，只补一行引用 readiness run card；默认完整 hand-check 清单与 Round 66/67/68/69 内容不应回归。
- README 只补一句简短说明或路径，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 prompt history / prompt library 管理系统。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不新增自动 readiness detection。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 存在轻量 presenter readiness run card。
2. run card 明确是人工演示前检查，不是 browser E2E automation，也不是自动 readiness detector。
3. run card 覆盖 UI 启动命令和本地 URL 检查。
4. run card 覆盖 bridge prompt：`logic4 和 throttle lock 有什么关系`。
5. run card 覆盖页面 callout labels：`[Input]`、`[Chain]`、`[Highlight]`、`[Structured answer]`、`[Raw JSON]`。
6. run card 覆盖 control chain 高亮、highlight explanation、structured answer、`Answer sections` summary、raw JSON debug。
7. run card 明确 loading / empty / API error / network error 是 UI 状态，不是控制逻辑结论。
8. run card 明确 demo 边界：deterministic controlled layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。
9. 如修改 `tools/demo_ui_handcheck.py --walkthrough`，默认 hand-check 清单、Round 66 observations、Round 67 walkthrough、Round 68 talk track 引用、Round 69 callout label 引用不回归。
10. 新增或更新轻量测试覆盖 readiness run card 的启动命令、bridge prompt、callout labels、UI 状态边界和 demo 边界文案。
11. Round 69 presenter callout labels 不回归。
12. Round 68 talk track 测试不回归。
13. Round 64 summary chip keyboard navigation 不回归。
14. 当前 `106 tests OK` 基线继续通过，并新增本轮 run card 测试。
15. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
16. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- presenter readiness run card 放在哪里、如何查看
- run card 覆盖哪些启动步骤、prompt、UI 区域和边界提示
- 如何明确它不是 E2E automation、自动 readiness detector 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 69 开发完成记录：UI demo presenter callout labels

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在关键 UI 区域新增轻量 presenter callout labels：
    - `[Input]` prompt 输入区
    - `[Chain]` fixed control chain
    - `[Highlight]` answer-to-chain highlight explanation
    - `[Structured answer]` structured output
    - `[Raw JSON]` raw JSON debug
  - labels 只在 section header / summary 附近显示，不改变 API 请求或 demo payload。

- `src/well_harness/static/demo.css`
  - 新增 `.presenter-callout` 轻量 badge 样式。
  - 保持 selected prompt、loading / empty / API error、chain highlight、answer sections summary、raw JSON 折叠等既有结构不变。

- `docs/demo_presenter_talk_track.md`
  - 补充页面 callout labels 与 talk track 的对应关系。
  - 继续说明它是人工演示话术，不是 browser E2E automation，也不是新的 answer payload 或 control truth。

- `tools/demo_ui_handcheck.py`
  - `--walkthrough` 的 setup 步骤新增跟随页面 callout labels 的一句提示。
  - 默认 hand-check 清单和 Round 66 guided observations 保持不回归。

- `tests/test_demo.py`
  - 新增 `test_demo_static_assets_include_presenter_callout_labels`。
  - 更新 walkthrough / talk track / raw JSON 折叠相关静态断言，覆盖 `[Input]`、`[Chain]`、`[Highlight]`、`[Structured answer]`、`[Raw JSON]`。

- `README.md`
  - 补充 UI section headers 的 presenter callout labels 与 talk track 对齐说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_callout_labels tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_covers_core_flow tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_presenter_walkthrough`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_presenter_callout_labels`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 53 tests OK。
- 全量回归：106 tests OK。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- presenter callout labels 是人工演示定位辅助，不是浏览器 E2E 自动化证明，也不是新的控制真值。
- 若继续增强 UI demo，优先补轻量截图标注或现场视觉提示，不要回到 schema / validator 工具链。

## Round 69 开发任务：UI demo presenter callout labels

### 当前状态

- Round 68 已通过指挥侧复核。
- 当前全量回归：`105 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工演示辅助材料：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
  - `docs/demo_presenter_talk_track.md`
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 presenter callout labels，让页面与 `docs/demo_presenter_talk_track.md` 的讲解点更容易对应。

### 建议实现

- 在静态 UI 中为关键区域增加小型 callout label / badge，例如：
  - `[Input]` prompt 输入区
  - `[Chain]` fixed control chain
  - `[Highlight]` answer-to-chain highlight explanation
  - `[Structured answer]` structured output
  - `[Raw JSON]` raw JSON debug
- label 应轻量、清晰、不会遮挡 UI；不需要复杂开关。
- 如果担心默认界面太吵，可以做成 subtle helper text 或只在 section header 附近显示。
- label 应与 Round 68 talk track 的 callout 词一致，帮助演示者按台词指向页面区域。
- 更新 `docs/demo_presenter_talk_track.md`，说明这些 callout labels 对应现场讲解点。
- 如有必要，更新 `tools/demo_ui_handcheck.py --walkthrough` 的一句话，提醒演示者跟随页面 callout labels；默认 hand-check 清单与 expected observations 不应回归。
- README 只补一句简短说明，不要新增长篇文档。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不新增复杂 prompt history / prompt library 管理系统。
- 不新增复杂 presenter mode 或 UI 状态机。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 中存在轻量 presenter callout labels。
2. callout labels 至少覆盖 Input、Chain、Highlight explanation、Structured answer、Raw JSON 五个区域。
3. labels 与 `docs/demo_presenter_talk_track.md` 的 callout 词保持一致或明确对应。
4. labels 不改变 UI/API payload、不维护第二套 answer payload 或控制真值。
5. labels 不影响 selected prompt、loading / empty / API error、chain highlight、answer sections summary、raw JSON 折叠等既有行为。
6. `docs/demo_presenter_talk_track.md` 更新说明页面 callout labels 如何对应演示台词。
7. 如果修改 `tools/demo_ui_handcheck.py --walkthrough`，默认 hand-check 清单、Round 66 observations、Round 67 walkthrough 不回归。
8. 新增或更新轻量静态测试覆盖 callout labels 的 HTML / CSS / JS 或文档引用。
9. Round 68 talk track 测试不回归。
10. Round 64 summary chip keyboard navigation 不回归。
11. 当前 `105 tests OK` 基线继续通过，并新增本轮 callout label 测试。
12. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
13. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- presenter callout labels 如何呈现
- labels 覆盖哪些 UI 区域，以及如何对应 talk track
- 如何明确它不是 E2E automation 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 68 开发完成记录：UI demo one-page presenter talk track

### 结论

PASS。

### 已完成

- `docs/demo_presenter_talk_track.md`
  - 新增一页式 presenter talk track。
  - 覆盖四类核心 prompt：
    - `logic4 和 throttle lock 有什么关系`
    - `为什么 throttle lock 没释放`
    - `触发 logic3 会发生什么`
    - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - 每个 prompt 都包含 `[Say]` 演示台词和 `[Point]` UI 指向区域。
  - 明确提到 `control chain`、`highlight explanation`、`structured answer`、`raw JSON`。
  - 明确 proposal 是 dry-run，不直接修改 `controller.py`。
  - 明确 demo 边界：deterministic controlled demo layer、built-in `nominal-deploy` / `retract-reset`、simplified first-cut plant、not an open-ended LLM、not a complete physical model。
  - 明确 loading / empty prompt / API error / network error 是 UI 状态，不是 control-logic conclusion。

- `tools/demo_ui_handcheck.py`
  - `--walkthrough` 结尾新增 `docs/demo_presenter_talk_track.md` 引用。
  - 默认完整 hand-check 清单和 Round 67 walkthrough 保持不回归。

- `tests/test_demo.py`
  - 新增 `test_demo_presenter_talk_track_covers_core_flow`，读取 talk track 文档并校验核心 prompt、UI 区域、边界文案和 controller safety 文案。
  - 更新 walkthrough 测试，确认 helper 输出引用 talk track 路径。

- `README.md`
  - 补充一页式 talk track 路径。

### 验证命令

- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_presenter_talk_track_covers_core_flow tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_presenter_walkthrough tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_manual_checklist`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 52 tests OK。
- 全量回归：105 tests OK。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- talk track 是人工演示话术，不是浏览器 E2E 自动化证明。
- 当前仍无真实截图标注；若继续增强，优先补轻量截图标注或更短现场台词，不要回到 schema / validator 工具链。

### 原始任务上下文

- Round 67 已通过指挥侧复核。
- 当前全量回归：`104 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工手测 helper：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- helper 默认清单、guided expected observations、concise presenter walkthrough 均保持人工辅助定位，不启动 server、不驱动浏览器。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一页式 presenter talk track。

### 建议实现

- 推荐新增文档：
  - `docs/demo_presenter_talk_track.md`
- 内容应控制在一页左右，面向现场讲解，不是详细 hand-check 清单。
- `tools/demo_ui_handcheck.py --walkthrough` 可以在结尾引用该文档路径；如果改 helper，默认完整清单和现有 walkthrough 不应回归。
- README 可补一行指向该一页式 talk track。
- talk track 建议包含：
  - 30 秒开场：这是 deterministic controlled demo layer，不是开放式 LLM / 完整物理模型。
  - 演示路径：
    1. `logic4 和 throttle lock 有什么关系`
    2. `为什么 throttle lock 没释放`
    3. `触发 logic3 会发生什么`
    4. `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - 每个 prompt 的一句讲解台词和一个 UI 指向区域：
    - control chain
    - highlight explanation
    - structured answer
    - raw JSON
  - 收尾句：结果基于内置 `nominal-deploy` / `retract-reset` 和 simplified first-cut plant；proposal 不直接改 `controller.py`。
  - 如果 UI 出现 empty / error / loading 状态，提示这是 UI 状态而不是控制逻辑结论。
- 可以使用轻量文字 callout，例如 `[Say]`、`[Point]`、`[Boundary]`；不要要求真实截图。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具、图像依赖或 AI 图片生成。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 存在一页式 presenter talk track，建议路径为 `docs/demo_presenter_talk_track.md`。
2. talk track 覆盖 bridge、diagnose、trigger、proposal 四类核心 prompt。
3. talk track 对每个 prompt 都包含一句演示台词和一个 UI 指向区域。
4. talk track 明确提到 control chain、highlight explanation、structured answer、raw JSON。
5. talk track 明确 proposal 是 dry-run，不直接修改 `controller.py`。
6. talk track 明确 demo 边界：deterministic controlled layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。
7. talk track 明确 empty / error / loading 是 UI 状态，不是控制逻辑结论。
8. 如修改 `tools/demo_ui_handcheck.py --walkthrough`，默认 hand-check 清单和 Round 67 walkthrough 不回归。
9. 新增或更新轻量测试覆盖 talk track 的核心 prompt、UI 区域、边界文案和 controller safety 文案。
10. Round 67 presenter walkthrough 不回归。
11. Round 66 helper observations 不回归。
12. Round 64 summary chip keyboard navigation 不回归。
13. 当前 `104 tests OK` 基线继续通过，并新增本轮 talk-track 测试。
14. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
15. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- one-page presenter talk track 放在哪里
- talk track 覆盖哪些 prompt / 台词 / UI 指向区域
- 如何明确它不是 E2E automation 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 67 开发完成记录：UI demo concise presenter walkthrough

### 结论

PASS。

### 已完成

- `tools/demo_ui_handcheck.py`
  - 新增 `--walkthrough`。
  - 默认 `tools/demo_ui_handcheck.py` 仍输出 Round 66 的完整 hand-check 清单和逐 prompt expected observations。
  - `--walkthrough` 输出 concise presenter walkthrough，面向现场 1-2 分钟演示，而不是替代完整手测清单。
  - walkthrough 覆盖四类核心 prompt：
    - `logic4 和 throttle lock 有什么关系`
    - `为什么 throttle lock 没释放`
    - `触发 logic3 会发生什么`
    - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - walkthrough 使用 `[Input]`、`[Chain]`、`[Structured answer]`、`[Raw JSON]`、`[Safety]`、`[Boundary]` callout，指导演示者指向对应 UI 区域。
  - walkthrough 明确它是 manual presenter walkthrough，不是 browser E2E automation，也不是新的 answer payload 或 control truth。
  - walkthrough 明确边界：deterministic controlled demo layer、built-in `nominal-deploy` / `retract-reset` scenarios、simplified first-cut plant、not a full LLM、not a complete physical model。

- `tests/test_demo.py`
  - 新增 `test_demo_ui_handcheck_script_outputs_presenter_walkthrough`。
  - 更新 `--help` smoke，覆盖 `--walkthrough` 参数。
  - 继续保护 Round 66 helper observations 和 Round 64 summary chip keyboard navigation 静态测试。

- `README.md`
  - 补充 `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough` 用法。

### 验证命令

- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --help`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_presenter_walkthrough tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_manual_checklist tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_help_documents_manual_scope`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 51 tests OK。
- 全量回归：104 tests OK。
- UI/API 仍复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- walkthrough 是人工演示脚本，不是浏览器 E2E 自动化证明。
- 继续没有引入截图生成、浏览器驱动或新的控制真值；后续如增强，优先补演示截图标注或更清晰的现场话术。

### 原始任务上下文

- Round 66 已通过指挥侧复核。
- 当前全量回归：`103 tests OK`。
- 当前已有本地 UI shell：
  - `PYTHONPATH=src python3 -m well_harness.demo_server`
- 当前已有人工手测 helper：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
  - 默认只打印清单，不启动 server，不驱动浏览器。
  - 已覆盖四类核心 prompt 的 guided expected observations。
- 默认 demo text / JSON 输出、`run` CLI、既有 harness JSON 输出、控制逻辑和仿真行为保持不变。

### 唯一开发任务

在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一个轻量 concise presenter walkthrough。

### 建议实现

- 优先扩展 `tools/demo_ui_handcheck.py`，例如新增：
  - `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`
- `--walkthrough` 输出应是面向演示者的短流程，不是替代现有完整 hand-check 清单。
- 默认 `tools/demo_ui_handcheck.py` 输出仍应保持 Round 66 的完整清单和 expected observations。
- walkthrough 建议包含 4-6 个短步骤：
  - 启动 server 并打开 URL。
  - 运行 `logic4 和 throttle lock 有什么关系`，指向 `logic4 / THR_LOCK` 高亮、highlight explanation、raw JSON。
  - 运行 `为什么 throttle lock 没释放`，指向 `possible_causes / evidence / risks`。
  - 运行 `触发 logic3 会发生什么`，指向 `logic3` 与 `EEC / PLS / PDU` 子节点高亮。
  - 运行 `把 logic3 的 TRA 阈值改成 -8 会发生什么`，指向 dry-run proposal、`required_changes / risks`，并强调不修改 controller。
  - 以边界提示收尾：deterministic controlled demo layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。
- 可加入文字 callout 标签，例如 `[Input]`、`[Chain]`、`[Structured answer]`、`[Raw JSON]`，帮助现场讲解；不要生成或依赖真实截图。
- 如选择新增 `docs/demo_walkthrough.md`，也需要由 helper 输出或引用，并用轻量测试保护关键内容。

### 非目标

- 不引入 Playwright / Selenium / 浏览器 E2E 框架。
- 不新增截图生成工具或图像依赖。
- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不重跑或重写 plant。
- 不改 `SimulationRunner` / `controller.py`。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不要修改 `docs/coordination/plan.md`。

### 验收标准

1. 存在轻量 concise presenter walkthrough，优先通过 `tools/demo_ui_handcheck.py --walkthrough` 运行。
2. 默认 `tools/demo_ui_handcheck.py` 的完整 hand-check 清单和 Round 66 expected observations 不回归。
3. walkthrough 覆盖 bridge、diagnose、trigger、proposal 四类核心 prompt。
4. walkthrough 指导演示者说明 `logic4 / THR_LOCK` 高亮、highlight explanation 与 raw JSON。
5. walkthrough 指导演示者说明 `possible_causes / evidence / risks`。
6. walkthrough 指导演示者说明 `logic3` 与 `EEC / PLS / PDU` command 子节点高亮。
7. walkthrough 指导演示者说明 dry-run proposal、`required_changes / risks`，并明确不修改 controller。
8. walkthrough 明确它是人工演示走查，不是 browser E2E automation，也不是新的控制真值。
9. walkthrough 明确 UI demo 边界：deterministic controlled layer、内置 scenario、simplified first-cut plant、非完整 LLM、非完整物理模型。
10. 新增或更新轻量测试覆盖 walkthrough 命令 / 输出中的核心 prompt、UI callout、边界文案。
11. Round 66 helper observations 不回归。
12. Round 64 summary chip keyboard navigation 不回归。
13. 当前 `103 tests OK` 基线继续通过，并新增本轮 walkthrough 测试。
14. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
15. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- concise presenter walkthrough 如何运行
- walkthrough 覆盖哪些 prompt / callout / 观察点
- 如何明确它不是 E2E automation 或新的控制真值
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 run CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 66 开发完成记录：UI demo guided hand-check expected observations

### 结论

PASS。

### 已完成

- `tools/demo_ui_handcheck.py`
  - 继续作为轻量人工 browser hand-check helper。
  - 为每个核心 prompt 增加 `expected observations`。
  - `bridge` prompt `logic4 和 throttle lock 有什么关系` 覆盖：
    - `intent: logic4_thr_lock_bridge`
    - `logic4 / THR_LOCK bridge association`
    - `evidence / outcome` relationship 检查
    - raw JSON 中 `matched_node=logic4->thr_lock`
  - `diagnose` prompt `为什么 throttle lock 没释放` 覆盖：
    - `intent: diagnose_problem`
    - `THR_LOCK / throttle_lock_release_cmd` association
    - `possible_causes / evidence / risks`
    - raw JSON debug 可见性
  - `trigger` prompt `触发 logic3 会发生什么` 覆盖：
    - `intent: trigger_node`
    - `logic3` 与 `EEC / PLS / PDU` command 子节点高亮
    - `evidence / outcome` trigger window 检查
    - raw JSON 中 `matched_node=logic3` 与 `target_logic=logic3`
  - `proposal` prompt `把 logic3 的 TRA 阈值改成 -8 会发生什么` 覆盖：
    - `intent: propose_logic_change`
    - `logic3` threshold proposal association
    - dry-run / proposal、`required_changes / risks`
    - 明确 `does not directly modify controller.py`
  - notes 中新增说明：expected observations 是 manual review hints，不是新的 answer payload 或 control truth。
  - helper 仍明确是 manual browser hand-check helper，不是 browser E2E automation。
  - helper 默认仍只打印清单，不启动 server、不驱动浏览器；`--open` 仍只用标准库打开 URL。

- `tests/test_demo.py`
  - 更新 `test_demo_ui_handcheck_script_outputs_manual_checklist`。
  - 断言 guided observations 的 intent、关键节点、raw JSON、section 和 safety 文案。
  - 继续覆盖 Round 65 的启动命令、URL、核心 prompt、UI checkpoint 和边界提示。

- `README.md`
  - 补充 hand-check helper 会打印 core prompts with guided expected observations。

### 验证命令

- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --help`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_manual_checklist tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_help_documents_manual_scope`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `python3 -m json.tool /tmp/well_harness_round66_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `python3 -m json.tool /tmp/well_harness_round66_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `python3 -m json.tool /tmp/well_harness_round66_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 50 tests OK。
- 全量回归：103 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- guided observations 仍是人工验收提示，不是浏览器 E2E 自动化证明，也不是新的 answer payload / control truth。
- 当前 UI 仍无浏览器 E2E；如果继续增强，优先补截图标注或更清楚的演示走查文档，不要回到 schema / validator 工具链。

## Round 65 开发完成记录：UI demo lightweight browser hand-check helper

### 结论

PASS。

### 已完成

- `tools/demo_ui_handcheck.py`
  - 新增轻量 browser hand-check helper。
  - 默认只打印人工手测清单，不启动长期 server，不驱动浏览器。
  - 输出本地 UI 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
  - 输出默认 URL 形态：`http://127.0.0.1:8000/`。
  - 覆盖四类核心 prompt：
    - `logic4 和 throttle lock 有什么关系`
    - `为什么 throttle lock 没释放`
    - `触发 logic3 会发生什么`
    - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - 覆盖 UI 手测检查项：
    - selected prompt state
    - loading / ready state
    - control chain highlight
    - highlight explanation
    - `Answer sections` summary
    - summary chip click / focus
    - summary chip arrow-key navigation
    - raw JSON debug collapse / expand
    - empty prompt error
  - 覆盖 demo 边界提示：
    - deterministic controlled demo layer
    - built-in `nominal-deploy` / `retract-reset` scenarios
    - simplified first-cut plant
    - not a full natural-language AI system
    - not a complete physical model
  - 可选 `--open` 只用 Python 标准库 `webbrowser.open(...)` 打开 URL；仍不启动 server，也不自动化浏览器。

- `tests/test_demo.py`
  - 新增 `DEMO_UI_HANDCHECK_SCRIPT_PATH`。
  - 新增 `test_demo_ui_handcheck_script_outputs_manual_checklist`。
  - 新增 `test_demo_ui_handcheck_script_help_documents_manual_scope`。
  - 测试覆盖 helper 输出中的启动命令、URL、核心 prompt、UI 检查项、边界文案、`not browser E2E automation` 和 `--open` help。

- `README.md`
  - 补充 `PYTHONPATH=src python3 tools/demo_ui_handcheck.py` 用法。
  - 明确 helper 是人工 hand-check guidance，不是 browser E2E automation，默认不启动 server、不驱动浏览器。

### 验证命令

- `python3 -m py_compile tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --help`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_outputs_manual_checklist tests.test_demo.DemoIntentLayerTests.test_demo_ui_handcheck_script_help_documents_manual_scope`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 50 tests OK。
- 全量回归：103 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- helper 是人工验收辅助，不是浏览器级 E2E 自动化证明。
- 当前 UI 仍无浏览器 E2E；如果继续增强，优先做更清晰的浏览器手测流程或截图标注，不要回到 schema / validator 工具链。

## Round 64 开发完成记录：UI demo answer section keyboard navigation

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在 `Answer sections` summary 中新增 `answer-section-keyboard-hint`。
  - 文案为 `Use arrow keys to move between section chips.`。

- `src/well_harness/static/demo.css`
  - 新增 `.summary-hint` 样式。

- `src/well_harness/static/demo.js`
  - 新增 `focusSummaryChip(currentChip, key)`：
    - `ArrowRight` / `ArrowDown` 聚焦下一个 chip。
    - `ArrowLeft` / `ArrowUp` 聚焦上一个 chip。
    - `Home` 聚焦第一个 chip。
    - `End` 聚焦最后一个 chip。
  - 新增 `handleSummaryChipKeydown(event)`：
    - 只处理 summary chip 上的方向键 / `Home` / `End`。
    - 不处理 `Enter` / `Space`，继续依靠原生 button click 行为触发已有 section focus。
  - 动态生成的 `button.summary-chip` 新增：
    - `aria-describedby="answer-section-keyboard-hint"`
    - `keydown` listener 指向 `handleSummaryChipKeydown`
  - API / UI error 仍用非 button 的 unavailable chip，不保留上一条 answer 的可导航 chip。

- `tests/test_demo.py`
  - 新增 `test_demo_static_assets_include_answer_section_keyboard_navigation`。
  - 覆盖方向键 / `Home` / `End` 代码路径、summary keyboard hint、`aria-describedby`、error unavailable 行为和不复制 `Enter` / `Space` click 逻辑。

- `README.md`
  - 补充 `Answer sections` summary 支持 arrow-key chip navigation 的说明。

### 验证命令

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_keyboard_navigation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round64_demo_bridge.txt`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round64_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round64_demo_logic3.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round64_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round64_demo_server_help.txt`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round64_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round64_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round64_events.txt`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round64_retract_events.txt`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 48 tests OK。
- 全量回归：101 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；summary keyboard navigation 通过静态测试保护。
- 下一轮如果继续增强 UI，最值得做的是轻量 browser hand-check script 或 section focus 的手测说明，而不是回到 schema / validator 工具链。

## Round 63 开发完成记录：UI demo answer section jump and focus polish

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.js`
  - 新增 `answerSectionId(sectionName)`，统一生成 `answer-section-*` section id。
  - 新增 `focusAnswerSection(sectionName)`，点击 summary chip 后聚焦并滚动到对应 structured output section。
  - `renderList(...)` 现在给每个 structured output section 设置：
    - `id="answer-section-<sectionName>"`
    - `tabindex="-1"`
  - `renderAnswerSectionSummary(...)` 现在生成原生 `button.summary-chip`。
  - 每个 summary chip 设置 `type="button"` 与 `aria-controls="answer-section-<sectionName>"`。
  - 空 section 的 chip 仍保留跳转能力，文案继续显示 `0 items — empty for this answer`。
  - API / UI error 时仍调用 `renderAnswerSectionSummaryUnavailable()`，不会保留上一条 answer 的可跳转 chip。

- `src/well_harness/static/demo.css`
  - 新增 `button.summary-chip` cursor 样式。
  - 新增 `.summary-chip:focus-visible` 与 `.answer-section:focus-visible` focus ring。
  - 新增 `.answer-section { scroll-margin-top: 24px; }`，让 scroll/focus 位置更易读。

- `tests/test_demo.py`
  - 新增 `test_demo_static_assets_include_answer_section_jump_focus`。
  - 继续增强 Round 62 summary 静态测试，覆盖 `aria-controls`、section id / tabindex、focus / scroll 行为和 error unavailable 状态。

- `README.md`
  - 补充 `Answer sections` summary chip 可以 focus 到匹配 answer section 的说明。

### 验证命令

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_jump_focus`
- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round63_demo_bridge.txt`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round63_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round63_demo_logic3.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round63_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round63_demo_server_help.txt`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round63_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round63_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round63_events.txt`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round63_retract_events.txt`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 47 tests OK。
- 全量回归：100 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；summary jump / focus 行为通过静态测试保护。
- 下一轮如果继续增强 UI，最值得做的是小范围 section keyboard polish 或 browser hand-check script，而不是回到 schema / validator 工具链。

## Round 62 开发完成记录：UI demo structured answer scan polish

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在 `Structured output` 区域上方新增 `Answer sections` summary。
  - 新增 `answer-section-summary` 与 `answer-section-summary-items` 节点。
  - 初始状态显示 `Waiting for answer.`。

- `src/well_harness/static/demo.css`
  - 新增 `.answer-section-summary`、`.summary-chips`、`.summary-chip` 样式。
  - 新增 `.summary-chip.is-empty` 与 `.summary-chip.is-error` 状态。

- `src/well_harness/static/demo.js`
  - 新增 `renderAnswerSectionSummary(payload)`：
    - 基于现有 `DemoAnswer` payload 的 `evidence`、`outcome`、`possible_causes`、`required_changes`、`risks` 数组生成 item count。
    - 空数组显示 `0 items — empty for this answer`。
  - 新增 `renderAnswerSectionSummaryUnavailable()`：
    - API / UI error 时显示 `Section summary unavailable for UI/API errors.`。
    - 避免保留上一条 answer 的旧计数。
  - `renderList(...)` 的空 section 文案改为 `empty for this answer`，仍不改变 demo JSON payload。

- `tests/test_demo.py`
  - 新增静态 UI 测试，覆盖 answer section summary 的 HTML / CSS / JS 结构、empty 文案和 error/unavailable 文案。

- `README.md`
  - 补充 `Answer sections` summary 的简短说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_answer_section_summary tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round62_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round62_demo_logic3.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round62_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round62_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round62_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round62_events.txt`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round62_retract_events.txt`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 46 tests OK。
- 全量回归：99 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；answer section summary 通过静态测试保护。
- summary 是扫读辅助，只计数现有 `DemoAnswer` arrays；后续如果继续增强 UI，最值得做的是小范围 section jump / focus polish，而不是回到 schema / validator 工具链。

## Round 61 开发完成记录：UI demo answer-to-chain highlight explanation

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 在控制链路图下新增 `<aside id="highlight-explanation">`。
  - 新增 `highlight-payload-fields`、`highlight-node-list`、`highlight-explanation-list` 三个输出节点。
  - 初始说明明确高亮来自 `matched_node` / `target_logic`，且只是 answer association，不是完整因果证明。

- `src/well_harness/static/demo.css`
  - 新增 `.highlight-explanation` 及其 heading / paragraph / list 样式。

- `src/well_harness/static/demo.js`
  - 新增 `nodeLabels`，只用于把已有高亮 node id 转成人类可读标签。
  - 新增 `highlightedNodesForPayload(payload)`，让视觉高亮和解释文案共用同一份 existing UI alias mapping。
  - 新增 `renderHighlightExplanation(payload)`：
    - 显示 `intent`、`matched_node`、`target_logic`。
    - 显示高亮节点列表。
    - 对 `logic4->thr_lock` 输出 logic4 / THR_LOCK bridge highlight 说明。
    - 对 `logic3` 输出 logic3 / EEC / PLS / PDU command 子节点说明。
    - 对 throttle-lock release 相关 answer 输出 release command association 说明。
    - 明确这不是完整因果证明或真实物理根因证明。
  - 新增 `clearHighlightExplanation()`，API / UI error 时清空高亮解释。

- `tests/test_demo.py`
  - 新增静态 UI 测试，覆盖 highlight explanation HTML / CSS / JS 结构和关键说明片段。

- `README.md`
  - 补充 UI highlight explanation 的简短说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_highlight_explanation tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_polish_and_highlight_refinements`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round61_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round61_demo_logic3.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round61_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round61_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round61_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 45 tests OK。
- 全量回归：98 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；当前通过静态 / API smoke 锁住结构。
- highlight explanation 是 answer association 说明，不是因果证明；下一轮如果继续增强 UI，最值得做的是小范围视觉 / keyboard / help polish 或轻量浏览器手测脚本，而不是回到 schema / validator 工具链。

## Round 61 指挥计划：UI demo answer-to-chain highlight explanation

### 当前状态

- Round 60 已完成并通过指挥侧复核。
- 当前全量回归：`97 tests OK`。
- 本地 UI shell 已存在，启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
- UI 已具备 loading / empty prompt / API error、selected prompt、示例 prompt 分组、`Cmd+Enter` / `Ctrl+Enter` 提交、compact help copy、固定控制链路、command 子节点高亮、移动端 step rail、结构化输出和可折叠 raw JSON debug。
- UI/API 仍直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI 和既有 harness JSON 输出保持不变。

### 唯一开发任务

在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加一个轻量 answer-to-chain highlight explanation。

### 建议实现

- 在控制链路图附近新增一个小型说明区，例如 `Why these nodes are highlighted` / `Highlight explanation`。
- 每次 API 返回后，基于现有 `DemoAnswer` JSON payload 的 `matched_node` / `target_logic` / `intent` 生成说明。
- 说明当前关联的 payload 字段、高亮了哪些节点或子节点，以及高亮只代表 answer association，不是完整因果证明或真实物理根因证明。
- 继续复用现有前端高亮 alias mapping；不要维护第二套控制真值，不要在 UI 层重新推理 controller 逻辑。
- `logic4 和 throttle lock 有什么关系` 应说明 `logic4` 与 `THR_LOCK` bridge highlight。
- `触发 logic3 会发生什么` 应说明 `logic3` 与 `EEC` / `PLS` / `PDU` command 子节点关联 highlight。
- `为什么 throttle lock 没释放` 仍应能看到 cause / evidence / risks、raw JSON 和相关链路高亮。

### 非目标

- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不引入浏览器 E2E 框架。
- 不新增 scenario。
- 不新增复杂 prompt history / prompt library 管理系统。
- 不重跑或重写 plant。
- 不改 `SimulationRunner`。
- 不改 `controller.py` 的 deploy 判定逻辑。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 中存在 answer-to-chain highlight explanation 区域。
2. explanation 基于现有 `DemoAnswer` payload 字段生成，至少引用 `matched_node` 或 `target_logic`。
3. explanation 能说明高亮节点列表，并明确高亮只是 answer association，不是完整因果证明。
4. `logic4 和 throttle lock 有什么关系` 能说明 `logic4` 与 `THR_LOCK` 的 bridge highlight。
5. `触发 logic3 会发生什么` 能说明 `logic3` 与 `EEC` / `PLS` / `PDU` 的关联 highlight。
6. `为什么 throttle lock 没释放` 仍能看到 cause / evidence / risks、raw JSON 和相关链路高亮。
7. Round 60 的 prompt 分组、keyboard affordance、help copy 不回归。
8. Round 59 的 selected prompt、mobile rail、raw JSON 折叠不回归。
9. 新增轻量 UI tests 覆盖 highlight explanation 的 HTML / JS 结构和关键说明片段。
10. 当前 `97 tests OK` 基线继续通过，并新增本轮 UI explanation tests。
11. 现有 CLI 行为保持不变：`run nominal-deploy`、`--view timeline/events/explain/diagnose`、`--format json`、`demo "..."`、`demo --format json "..."`。
12. `nominal-deploy` 仍能到达 `logic4`，`retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- highlight explanation 如何呈现
- explanation 如何从 `matched_node` / `target_logic` 映射到高亮节点
- 如何确保高亮解释不是第二套控制真值或因果证明
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 60 开发完成记录：UI demo prompt guidance and keyboard affordance

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 示例 prompt 改为轻量分组：
    - `Chain relationship` -> `logic4 和 throttle lock 有什么关系`
    - `Diagnosis` -> `为什么 throttle lock 没释放`
    - `Trigger` -> `触发 logic3 会发生什么`
    - `Proposal` -> `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - 示例按钮新增 `data-category` / `data-intent`，仅用于 UI 展示和测试，不改变 API payload。
  - textarea 新增 `prompt-keyboard-hint`，提示 `Press Cmd/Ctrl+Enter to run; plain Enter adds a newline.`。
  - 新增短小 `<details id="demo-help">` help copy，说明当前是 deterministic controlled demo layer，不是开放式 LLM，也不是完整物理模型。

- `src/well_harness/static/demo.css`
  - 新增 `.grouped-examples`、`.example-group`、`.prompt-hint`、`.demo-help` 样式。
  - 保留 Round 59 的 selected prompt、mobile step rail、raw JSON `<details>` 样式。

- `src/well_harness/static/demo.js`
  - 新增 textarea `keydown` handler。
  - `Cmd+Enter` / `Ctrl+Enter` 调用现有 `form.requestSubmit()`。
  - 普通 Enter 没有被拦截，textarea 仍可换行。
  - selected prompt 状态继续通过 `syncSelectedPrompt(prompt)` 维护。

- `tests/test_demo.py`
  - 新增静态 UI usability 测试，覆盖 prompt 分组、`data-category` / `data-intent`、Cmd/Ctrl+Enter 提示与 keydown handler、help `<details>` copy。

- `README.md`
  - 补充 UI 示例 prompt 分组、Cmd/Ctrl+Enter 和 compact help note 的简短说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_polish_and_highlight_refinements`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round60_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round60_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round60_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round60_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

### 当前结果

- `tests.test_demo`: 44 tests OK。
- 全量回归：97 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；当前通过静态 / API smoke 锁住结构。
- 下一步若继续增强 UI，最值得做的是更清楚的 answer-to-chain 高亮解释或小型 keyboard affordance 文案 polish；不要回到 schema / validator 工具链惯性。

## Round 60 指挥计划：UI demo prompt guidance and keyboard affordance

### 当前状态

- Round 59 已完成并通过复核。
- 当前全量回归：`96 tests OK`。
- 本地 UI shell 已存在：
  - `src/well_harness/demo_server.py`
  - `src/well_harness/static/demo.html`
  - `src/well_harness/static/demo.css`
  - `src/well_harness/static/demo.js`
- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
- UI 已具备 loading / empty prompt / API error、selected prompt、固定控制链路、command 子节点高亮、移动端 step rail、结构化输出和可折叠 raw JSON debug。
- UI/API 仍直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI 和既有 harness JSON 输出保持不变。

### 唯一开发任务

在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加 sample prompt 分组、键盘提交 affordance 和更清楚的受控 demo 帮助文案。

### 建议实现

#### Sample Prompt 分组

- 将现有示例 prompt 按 demo intent 或演示用途做轻量分组，例如：
  - Chain relationship: `logic4 和 throttle lock 有什么关系`
  - Diagnosis: `为什么 throttle lock 没释放`
  - Trigger: `触发 logic3 会发生什么`
  - Proposal: `把 logic3 的 TRA 阈值改成 -8 会发生什么`
- 分组可以是简单 heading / label，不需要复杂组件。
- 现有 selected prompt 状态必须继续工作。
- 如新增 `data-intent` / `data-category`，仅用于 UI 展示和测试，不要改变 demo API payload。

#### Keyboard Affordance

- 给 textarea 增加清晰提示，例如 `Press Cmd/Ctrl+Enter to run` 或中文等价提示。
- 支持 `Cmd+Enter` / `Ctrl+Enter` 提交当前 prompt。
- 不要劫持普通 Enter；textarea 仍应可换行。
- 键盘提交应复用现有 form submit 路径，不要复制请求逻辑。

#### Help Copy

- 增加一个极小帮助区，说明：
  - 当前支持受控短句，不是开放式 LLM。
  - 示例 prompt 覆盖 trigger / diagnose / bridge / proposal。
  - 回答基于内置 `nominal-deploy` / `retract-reset` 和 simplified first-cut plant。
- 可以用原生 `<details>` / `<summary>`，默认折叠或展开均可。
- 不要把帮助文案写成长篇文档；页面仍应第一屏可用。

### 非目标

- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不引入浏览器 E2E 框架。
- 不新增 scenario。
- 不新增复杂 prompt history / prompt library 管理系统。
- 不重跑或重写 plant。
- 不改 `SimulationRunner`。
- 不改 `controller.py` 的 deploy 判定逻辑。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 验收标准

1. 示例 prompt 以轻量分组形式展示，覆盖 bridge / diagnose / trigger / proposal 四类演示用途。
2. 现有 selected prompt 状态继续工作，不因分组结构回归。
3. textarea 或 prompt 区显示清楚键盘提交提示。
4. `Cmd+Enter` / `Ctrl+Enter` 通过现有 form submit 路径运行当前 prompt。
5. 普通 Enter 仍可在 textarea 中换行，不被误当作提交。
6. 页面包含极小帮助文案，明确这是 deterministic controlled demo layer，不是开放式自然语言 AI，也不是完整物理模型。
7. raw JSON 折叠、移动端 step rail、链路高亮不回归。
8. 新增轻量 UI tests：
   - 静态 HTML / JS 覆盖 prompt 分组或 category 标记
   - 静态 HTML / JS 覆盖 Cmd/Ctrl+Enter 提示和键盘处理
   - 静态 HTML 覆盖 help copy / details 结构
   - 现有 selected / raw JSON / mobile rail 静态测试继续通过
9. 当前 `96 tests OK` 基线继续通过，并新增本轮 UI usability tests。
10. 现有 CLI 行为保持不变：
    - `run nominal-deploy`
    - `--view timeline/events/explain/diagnose`
    - `--format json`
    - `demo "..."`
    - `demo --format json "..."`
11. `nominal-deploy` 仍能到达 `logic4`。
12. `retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- sample prompt 如何分组
- 键盘提交 affordance 如何实现，普通 Enter 是否仍可换行
- help copy 如何说明 demo 边界
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 59 开发完成记录：UI demo flow polish - selected prompt, mobile chain, raw JSON collapse

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 示例 prompt 按钮新增 `is-selected` 初始状态与 `aria-pressed`。
  - 新增 `selected-example` 状态行，显示当前 selected example 或 custom prompt。
  - 固定控制链路容器新增 `mobile-step-rail` class。
  - raw JSON debug 改为原生 `<details id="raw-json-details" open>` / `<summary>` 折叠结构。

- `src/well_harness/static/demo.css`
  - 新增 `.examples button.is-selected` / `[aria-pressed="true"]` selected 样式。
  - 新增 `.raw-card details` / `.raw-card summary` 样式。
  - 在窄屏 media rule 中把 `.chain-map.mobile-step-rail` 调整为横向可滚动 step rail：
    - `flex-wrap: nowrap`
    - `overflow-x: auto`
    - `scroll-snap-type: x proximity`
  - 子节点 group 在移动端保持独立宽度，避免 `logic1/TLS115`、`logic2/540V`、`logic3/EEC/PLS/PDU`、`logic4/THR_LOCK` 挤在一起。

- `src/well_harness/static/demo.js`
  - 新增 `syncSelectedPrompt(prompt)`。
  - 示例按钮点击后同步 `is-selected` 与 `aria-pressed="true"`。
  - 用户手动编辑 textarea 后会重新匹配 prompt；不匹配任何示例时清为 `Selected example: custom prompt`。
  - raw JSON 内容仍由 `renderPayload(...)` / `renderErrorPayload(...)` 更新同一个 `#raw-json` 节点，没有改变 API payload。

- `tests/test_demo.py`
  - 新增静态 flow polish 测试，覆盖 selected prompt、`aria-pressed`、移动端 rail class / media rule、raw JSON 折叠结构。

- `README.md`
  - 补充 selected prompt、窄屏链路 rail、raw JSON expandable panel 的简短说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_polish_and_highlight_refinements tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_flow_polish_controls tests.test_demo.DemoIntentLayerTests.test_demo_server_api_returns_demo_json_payload tests.test_demo.DemoIntentLayerTests.test_demo_server_api_missing_prompt_returns_readable_error_json`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round59_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round59_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round59_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round59_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`

### 当前结果

- `tests.test_demo`: 43 tests OK。
- 全量回归：96 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍没有浏览器级 E2E；当前通过静态 / API smoke 锁住结构。
- 下一步最值得处理的是小范围 demo usability，例如帮助文案 / sample prompt grouping / keyboard affordance；不要回到 schema / validator 工具链惯性。

## Round 59 指挥计划：UI demo flow polish - selected prompt, mobile chain, raw JSON collapse

### 当前状态

- Round 58 已完成并通过复核。
- 当前全量回归：`95 tests OK`。
- 本地 UI shell 已存在：
  - `src/well_harness/demo_server.py`
  - `src/well_harness/static/demo.html`
  - `src/well_harness/static/demo.css`
  - `src/well_harness/static/demo.js`
- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
- UI 已具备 loading、empty prompt、API / network error、固定控制链路、细化 command 子节点高亮、结构化输出和 raw JSON debug。
- UI/API 仍直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text / JSON 输出、`run` CLI 和既有 harness JSON 输出保持不变。

### 唯一开发任务

在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加 selected prompt 状态、移动端链路展示优化和 raw JSON 折叠能力。

### 建议实现

#### Selected Prompt 状态

- 示例 prompt 按钮点击后显示 selected / active 状态。
- 建议使用轻量 class，例如 `is-selected`，并同步 `aria-pressed="true"`。
- 用户手动编辑 textarea 后，如果内容不再匹配任何示例 prompt，应清除 selected 状态。
- 如实现成本低，可以显示一行 “Selected example: ...” 或等价提示；不要做复杂 prompt history。

#### 移动端链路展示

- 继续使用固定控制链路，不引入复杂图引擎。
- 在窄屏下让链路更可读：
  - 可以改成横向可滚动 step rail。
  - 或改成清晰的 stacked step cards。
  - 关键是 `logic1/TLS115`、`logic2/540V`、`logic3/EEC/PLS/PDU`、`logic4/THR_LOCK` 子节点在移动端不要挤成一团。
- 现有高亮语义保持不变：高亮只代表 answer association，不是完整因果证明。

#### Raw JSON 折叠

- raw JSON debug 面板应保持可访问，但允许折叠 / 展开。
- 优先用原生 `<details>` / `<summary>`，或一个极小按钮实现。
- raw JSON 内容仍应随每次 API 返回更新。
- 折叠功能不要改变 `well_harness demo --format json` payload。

### 非目标

- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不引入浏览器 E2E 框架。
- 不新增 scenario。
- 不重跑或重写 plant。
- 不改 `SimulationRunner`。
- 不改 `controller.py` 的 deploy 判定逻辑。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 验收标准

1. 示例 prompt 按钮点击后有明显 selected / active 状态。
2. selected 状态具备基础可访问性标记，例如 `aria-pressed` 或等价语义。
3. 用户手动改写 prompt 后，selected 状态能清除或更新，不误导当前输入来源。
4. 移动端控制链路展示更可读，至少通过静态 CSS / HTML 测试覆盖关键 class 或结构。
5. `logic4` / `THR_LOCK` 与 `logic3` command 子节点高亮不回归。
6. raw JSON debug 面板可折叠 / 展开，且内容仍随 API payload 更新。
7. `logic4 和 throttle lock 有什么关系` 仍能看到结构化解释、相关链路高亮和 raw JSON debug。
8. `为什么 throttle lock 没释放` 仍能看到 cause / evidence / risks。
9. 新增轻量 UI tests：
   - 静态 HTML / JS 覆盖 selected prompt 状态
   - 静态 CSS 覆盖移动端链路展示 class 或 media rule
   - 静态 HTML / JS 覆盖 raw JSON 折叠结构或 toggle 逻辑
10. 当前 `95 tests OK` 基线继续通过，并新增本轮 UI flow polish tests。
11. 现有 CLI 行为保持不变：
    - `run nominal-deploy`
    - `--view timeline/events/explain/diagnose`
    - `--format json`
    - `demo "..."`
    - `demo --format json "..."`
12. `nominal-deploy` 仍能到达 `logic4`。
13. `retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- selected prompt 状态如何呈现
- 移动端链路展示如何优化
- raw JSON debug 如何折叠 / 展开
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 58 开发完成记录：UI demo interaction polish and chain highlight refinement

### 结论

PASS。

### 已完成

- `src/well_harness/static/demo.html`
  - 新增 `ui-status` 状态行。
  - 将链路中的复合节点拆成可独立高亮的轻量子节点：
    - `logic1` / `tls115`
    - `logic2` / `etrac_540v`
    - `logic3` / `eec_deploy` / `pls_power` / `pdu_motor`
    - `logic4` / `thr_lock`

- `src/well_harness/static/demo.css`
  - 增加 loading / error / disabled button 样式。
  - 增加 `.chain-group` / command subnode 样式。
  - 增加 `.answer-section.is-error` 错误面板样式。

- `src/well_harness/static/demo.js`
  - loading 时显示 `Thinking deterministically...`。
  - loading 期间禁用提交按钮和所有示例 prompt 按钮，避免重复请求。
  - 空 prompt 在 UI 层直接显示 `请输入一个受控 demo prompt。`，并在 raw JSON debug 中展示 `missing_prompt`。
  - API error / network error 进入专门错误渲染路径，结构化区域展示可读错误，raw JSON debug 继续保留。
  - 细化高亮 alias map：
    - `logic4->thr_lock` 同时高亮 `logic4` 与 `thr_lock`。
    - `thr_lock` 只高亮 `thr_lock`，从而和 `logic4` 区分。
    - `logic3` 高亮 `logic3` 及 `eec_deploy` / `pls_power` / `pdu_motor`。
    - `tls115`、`etrac_540v`、`eec_deploy`、`pls_power`、`pdu_motor`、`thr_lock` 都有独立节点映射。

- `tests/test_demo.py`
  - 新增 missing prompt API smoke。
  - 新增静态 UI polish / 高亮映射测试。

- `README.md`
  - 补充 UI 的 loading / empty / API-error 状态与子节点高亮说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_api_returns_demo_json_payload tests.test_demo.DemoIntentLayerTests.test_demo_server_api_missing_prompt_returns_readable_error_json tests.test_demo.DemoIntentLayerTests.test_demo_server_serves_static_shell tests.test_demo.DemoIntentLayerTests.test_demo_static_html_contains_key_ui_elements tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_polish_and_highlight_refinements`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round58_demo_bridge.json`
- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round58_demo_diagnose.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round58_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round58_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 - <<'PY' ... PY`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`

### 当前结果

- `tests.test_demo`: 42 tests OK。
- 全量回归：95 tests OK。
- UI/API 仍复用现有 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 仍是本地静态 shell，没有浏览器级端到端测试。
- 下一轮最值得处理的是小范围视觉 / demo flow polish，例如更明显的 selected prompt 状态、移动端链路展示或 raw JSON 折叠；不要回到 schema / validator 工具链惯性。

## Round 58 指挥计划：UI demo interaction polish and chain highlight refinement

### 当前状态

- Round 57 已完成并通过复核。
- 当前全量回归：`93 tests OK`。
- 本地 UI shell 已存在：
  - `src/well_harness/demo_server.py`
  - `src/well_harness/static/demo.html`
  - `src/well_harness/static/demo.css`
  - `src/well_harness/static/demo.js`
- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
- UI 通过 `POST /api/demo` 直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`。
- 默认 `well_harness demo` text / JSON 输出、`run` CLI 和既有 harness JSON 输出保持不变。

### 唯一开发任务

在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加最小交互状态 polish 和更细的控制链路高亮。

### 建议实现

#### 交互状态

- 增加或完善 loading 状态。
- 提交 prompt 后显示明确 “running / loading / thinking deterministically” 状态。
- loading 期间禁用提交按钮和示例按钮，避免重复请求。
- 增加 empty prompt 状态：
  - 空 prompt 不应只依赖 API 400。
  - UI 应给出清晰提示，例如 “请输入一个受控 demo prompt”。
  - raw JSON debug 可以展示 `{ "error": "missing_prompt" }` 或等价错误 payload。
- 增加 API / network error 状态：
  - 结构化区域应显示清楚错误。
  - raw JSON debug 面板继续保留。

#### 链路高亮

- 继续使用固定控制链路，不引入复杂图引擎。
- 当前 `logic4->thr_lock` 能高亮 `logic4`，但 `THR_LOCK` 只是同一个 stack 内文字；可以在 HTML 中为 stack 内关键子节点增加轻量 `data-node` 标记，或用等价方式让高亮更清楚。
- 建议至少细化：
  - `tls115`
  - `etrac_540v`
  - `eec_deploy`
  - `pls_power`
  - `pdu_motor`
  - `thr_lock`
- `matched_node` / `target_logic` 映射仍应在前端保持小型 alias map，不要引入新依赖。
- 高亮只代表 demo answer 关联节点，不要把它说成完整因果证明。

### 非目标

- 不继续扩 schema validation 工具链。
- 不新增正式 JSON Schema、fixture contract 或 validator report。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖。
- 不新增运行时依赖。
- 不新增 scenario。
- 不重跑或重写 plant。
- 不改 `SimulationRunner`。
- 不改 `controller.py` 的 deploy 判定逻辑。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 验收标准

1. UI 显示明确 loading 状态，且 loading 期间防止重复提交。
2. 空 prompt 在 UI 中显示清楚错误提示，不产生不透明失败。
3. API 错误或网络错误在 UI 中有可读提示，并保留 raw JSON debug。
4. 控制链路高亮能更清楚地区分 `logic4` 与 `THR_LOCK`，以及至少若干 command 子节点。
5. `logic4 和 throttle lock 有什么关系` 仍能看到结构化解释、raw JSON 和相关链路高亮。
6. `为什么 throttle lock 没释放` 仍能看到 cause / evidence / risks、raw JSON 和相关链路高亮。
7. `触发 logic3 会发生什么` 仍能高亮 logic3 相关节点。
8. 新增轻量 UI tests：
   - empty prompt / missing prompt API 或 UI shell 测试
   - 静态 HTML / JS 包含 loading / error 状态关键元素或文案
   - 静态 HTML / JS 覆盖新增高亮子节点或 alias mapping
9. 当前 `93 tests OK` 基线继续通过，并新增本轮 UI polish tests。
10. 现有 CLI 行为保持不变：
    - `run nominal-deploy`
    - `--view timeline/events/explain/diagnose`
    - `--format json`
    - `demo "..."`
    - `demo --format json "..."`
11. `nominal-deploy` 仍能到达 `logic4`。
12. `retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- loading / empty / error 状态如何呈现
- 链路高亮如何区分 `logic4` / `THR_LOCK` 和 command 子节点
- UI/API 是否仍复用现有 demo reasoning layer
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 57 开发完成记录：UI demo shell

### 结论

PASS。

### 已完成

- 新增 `src/well_harness/demo_server.py`。
  - 使用 Python 标准库 `ThreadingHTTPServer`。
  - 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
  - 提供 `POST /api/demo`。
  - API 直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`，不维护第二套 demo answer payload 或控制真值。
  - `GET /` / `GET /demo.html` / `GET /demo.css` / `GET /demo.js` 提供静态 UI shell。

- 新增静态 UI：
  - `src/well_harness/static/demo.html`
  - `src/well_harness/static/demo.css`
  - `src/well_harness/static/demo.js`

- UI 行为：
  - 第一屏就是可操作 demo。
  - 包含输入框和示例 prompt：
    - `logic4 和 throttle lock 有什么关系`
    - `为什么 throttle lock 没释放`
    - `触发 logic3 会发生什么`
    - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
  - 展示固定控制链路：
    `SW1 -> logic1/TLS115 -> TLS unlocked -> SW2 -> logic2/540V -> logic3/EEC+PLS+PDU -> VDT90 -> logic4/THR_LOCK`
  - 根据 `matched_node` / `target_logic` 做简单高亮。
  - 展示结构化 `DemoAnswer` 字段和 raw JSON debug 面板。
  - 明确说明 UI 是 deterministic controlled demo layer，本轮不接真实 LLM，也不是完整物理模型。

- `tests/test_demo.py`
  - 新增 server/API smoke。
  - 新增静态 shell smoke。
  - 新增静态 HTML 关键文案 / 元素测试。

- `README.md`
  - 补充 `PYTHONPATH=src python3 -m well_harness.demo_server` 本地 UI 启动方式和边界说明。

### 验证命令

- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_api_returns_demo_json_payload tests.test_demo.DemoIntentLayerTests.test_demo_server_serves_static_shell tests.test_demo.DemoIntentLayerTests.test_demo_static_html_contains_key_ui_elements`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round57_nominal.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round57_diagnose_logic4.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 4.9`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
- 行为断言脚本：`nominal-deploy` 仍到达 `logic4`；`retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前结果

- `tests.test_demo`: 40 tests OK。
- 全量回归：93 tests OK。
- 默认 `well_harness demo "..."` 文本输出保持不变。
- `well_harness demo --format json "..."` 输出语义保持不变。
- `run` CLI 与既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- UI 目前是本地 demo shell，不是前端工程化产品。
- 目前只有静态 HTML / API smoke；如果后续要演示更复杂交互，下一步最值得补的是小范围的 UI 状态 polish，例如 loading / error / empty prompt 的展示细节，而不是继续扩 schema/validator 工具链。

## Round 57 指挥计划：UI demo shell

### 当前状态

- Round 56 已完成并通过指挥侧复核。
- 当前全量回归：`90 tests OK`。
- `well_harness demo "..."` 与 `well_harness demo --format json "..."` 已可用。
- Demo reasoning layer 是 deterministic controlled intent layer，不是开放式 LLM 系统。
- 当前还没有可展示 UI：未发现 `package.json` / Vite / Next / tsx / jsx，也没有静态 HTML / CSS / JS UI 入口。
- 继续扩 validator / schema / fixture 工具链对可展示 demo 帮助有限；Round 57 必须转向用户可见 UI。

### 唯一开发任务

新增一个最小本地 UI，用来展示现有 `well_harness demo --format json` reasoning layer。

要求在不改变现有 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下完成。

### 推荐技术方案

优先使用 Python 标准库本地 HTTP server + 静态页面：

- `src/well_harness/demo_server.py`
- `src/well_harness/static/demo.html`
- `src/well_harness/static/demo.css`
- `src/well_harness/static/demo.js`

推荐启动方式：

- `PYTHONPATH=src python3 -m well_harness.demo_server`
- 如实现成本很低，可同时新增 `well_harness ui`，但不能影响 `run` / `demo` 子命令。

服务端建议：

- 使用 Python 标准库 `http.server` 或等价标准库。
- 提供极薄 API，例如 `POST /api/demo`。
- API 直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`，或等价地走现有 `well_harness demo --format json` 逻辑。
- 不手写第二套 answer payload，不维护第二套控制真值。

页面建议：

- 第一屏就是可操作 demo，不做 landing page。
- 有输入框。
- 有示例 prompt 按钮：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 throttle lock 没释放`
  - `触发 logic3 会发生什么`
  - `把 logic3 的 TRA 阈值改成 -8 会发生什么`
- 展示结构化结果字段：
  - `intent`
  - `matched_node`
  - `target_logic`
  - `evidence`
  - `outcome`
  - `possible_causes`
  - `required_changes`
  - `risks`
- 展示固定控制链路图：
  `SW1 -> logic1/TLS115 -> TLS unlocked -> SW2 -> logic2/540V -> logic3/EEC+PLS+PDU -> VDT90 -> logic4/THR_LOCK`
- 根据 `matched_node` / `target_logic` 做简单高亮即可。
- 保留 raw JSON debug 面板。
- 明确显示边界提示：当前是 deterministic controlled demo layer，基于内置 scenario 和 simplified first-cut plant，不是完整自然语言 AI 系统，也不是完整物理模型。

### 非目标

- 不继续扩 schema validation 工具链，除非 UI demo 已完成且只需极小测试保护。
- 不接入真实 LLM / agent 系统。
- 不做大而全 UI 或前端工程化平台。
- 不新增 Node / Vite / Next 依赖，除非开发会话明确说明收益大于成本。
- 不新增运行时依赖。
- 不新增 scenario。
- 不重跑或重写 plant。
- 不改 `SimulationRunner`。
- 不改 `controller.py` 的 deploy 判定逻辑。
- 不改 `well_harness.cli run` 默认行为。
- 不改变 `well_harness demo` text / JSON 输出语义。
- 不把 simplified plant 说成真实完整物理模型。
- 不修改 `docs/coordination/plan.md`。

### 验收标准

1. 可以用一个命令启动本地 UI。
2. 浏览器打开后第一屏就是 demo 操作界面。
3. 输入 `logic4 和 throttle lock 有什么关系` 可以看到结构化解释。
4. 输入 `为什么 throttle lock 没释放` 可以看到 cause / evidence / risks。
5. 页面显示固定控制链路图，并根据 `matched_node` / `target_logic` 高亮相关节点。
6. 页面显示 raw JSON debug。
7. 页面明确说明这是 UI demo shell，不是完整开放式自然语言产品，也不是完整物理仿真。
8. 新增轻量 UI smoke tests：
   - server / API smoke test
   - demo endpoint 返回合法 JSON
   - 静态 HTML 包含关键 UI 文案或元素
9. 当前 `90 tests OK` 继续通过，并新增本轮 UI smoke tests。
10. 现有 CLI 行为保持不变：
    - `run nominal-deploy`
    - `--view timeline/events/explain/diagnose`
    - `--format json`
    - `demo "..."`
    - `demo --format json "..."`
11. `nominal-deploy` 仍能到达 `logic4`。
12. `retract-reset` 仍能清掉 `sw1`、`sw2` 及相关逻辑。

### 完成后请回报

- 改了哪些文件
- UI 启动命令是什么
- UI/API 如何复用现有 demo reasoning layer
- 页面如何展示控制链路与高亮
- raw JSON debug 面板如何显示
- 默认 demo text / JSON 输出和 `run` CLI 是否保持不变
- 跑了哪些测试
- 下一轮最值得处理的 UI demo 盲点是什么

## Round 56 指挥侧验收记录

### 结论

PASS。

### 已确认完成

- `tools/validate_demo_answer_schema.py`
  - 新增 `--format json`。
  - 默认不带参数时继续输出 Round 55 的人类可读文本：
    `OK ...` / `PASS ...` / `SKIP ...`。
  - JSON 输出复用同一轮真实 validator 结果，不维护第二套 payload。
  - JSON 顶层包含 `status`、`schema_path`、`asset_path`、`results`。
  - `results[]` 包含 `prompt`、`intent`、`validation_status`，并在验证路径下包含 `error_count` / `errors`。
  - 缺少 `jsonschema` 或设置 `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1` 时，JSON 输出稳定为 `status=skip`、`results=[]`、`reason=<optional dependency message>`。

- `tests/test_demo.py`
  - 新增 demo answer schema validator JSON pass 输出 smoke test。
  - 新增 demo answer schema validator JSON forced-skip 输出 smoke test。
  - 保留 Round 55 文本入口 smoke tests。
  - 保留 Round 54 optional unittest validator。

- `README.md`
  - 补充 `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json`。
  - 说明文本模式面向人类，JSON 模式面向自动化消费。

### 本轮验证命令

- `python3 -m py_compile tools/validate_demo_answer_schema.py`
- `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`
- `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json`
- `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1 PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_forced_skip tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_json_pass_output tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_json_forced_skip_output tests.test_demo.DemoIntentLayerTests.test_optional_jsonschema_validates_demo_json_payloads_when_installed`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json | python3 -m json.tool`
- `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1 PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- 行为断言脚本：`nominal-deploy` 仍到达 `logic4`，`retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`

### 当前结果

- `tools/validate_demo_answer_schema.py --format json` 默认路径在当前环境中实际校验三条 demo JSON payload 并通过。
- JSON pass 输出列出三条 prompt：
  - `logic4 和 throttle lock 有什么关系`
  - `为什么 logic4 还没满足`
  - `为什么 throttle lock 没释放`
- JSON forced-skip 输出返回 0，`status=skip`，`results=[]`。
- `tests.test_demo`: 37 tests OK。
- 全量回归：90 tests OK。
- 默认 demo text 输出保持不变。
- `well_harness demo --format json` 输出语义保持不变。
- `run` CLI 和既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- `tools/validate_demo_answer_schema.py --format json` 目前还没有自己的轻量 fixture contract。
- 如果外部集成方长期消费这个 validator report，可下一轮单独补 fixture；不要扩成完整 schema 工具链或通用 report 平台。

## Round 55 指挥侧验收记录

### 结论

PASS。

### 已确认完成

- `tools/validate_demo_answer_schema.py`
  - 新增极薄非 unittest optional validator 入口。
  - 读取 `docs/json_schema/demo_answer_v1.schema.json`。
  - 读取 `tests/fixtures/demo_json_output_asset_v1.json`。
  - 通过真实 `well_harness demo --format json` 路径校验三条 payload：
    - `logic4 和 throttle lock 有什么关系`
    - `为什么 logic4 还没满足`
    - `为什么 throttle lock 没释放`
  - 安装 `jsonschema` 时使用 `Draft202012Validator.check_schema(...)` 与 validator 校验真实 payload。
  - 缺少 `jsonschema` 或设置 `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1` 时打印明确 `SKIP` 并以 0 退出。

- `tests/test_demo.py`
  - 新增脚本级默认入口 smoke test。
  - 新增强制 `SKIP` 分支 smoke test。
  - Round 54 的 optional unittest validator 继续保留并通过。

- `README.md`
  - 补充非 unittest 入口命令：
    `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`
  - 说明 `jsonschema` 是可选依赖；普通 demo / run 命令不依赖它。

### 指挥侧复核命令

- `python3 -m py_compile tools/validate_demo_answer_schema.py`
- `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`
- `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1 PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`
- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_answer_schema_standalone_script_forced_skip tests.test_demo.DemoIntentLayerTests.test_optional_jsonschema_validates_demo_json_payloads_when_installed`
- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json > /tmp/well_harness_round55_nominal_verify.json`
- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json > /tmp/well_harness_round55_logic4_diagnose_verify.json`
- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 > /tmp/well_harness_round55_retract_events.txt`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- 行为断言脚本：`nominal-deploy` 仍到达 `logic4`，`retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`

### 当前结果

- 独立入口默认路径在当前环境中实际校验三条 demo JSON payload 并通过。
- 独立入口强制 `SKIP` 路径返回 0，stdout 包含明确 optional dependency 提示。
- `tests.test_demo`: 35 tests OK。
- 全量回归：88 tests OK。
- 默认 demo text 输出保持不变。
- demo JSON 输出语义保持不变。
- `run` CLI 和既有 harness JSON 输出保持不变。
- `nominal-deploy` 仍到达 `logic4`。
- `retract-reset` 仍清掉 `sw1 / sw2 / logic1 / logic2 / logic3 / logic4`。

### 当前剩余盲点

- `tools/validate_demo_answer_schema.py` 目前是人类可读极薄入口，没有自己的 `--format json` 输出。
- 如果外部集成方还需要机器消费这个 validator 自身的执行结果，可下一轮单独补小型 JSON 输出；不要扩成完整 schema 工具链或开放式 demo 平台。

## Round 87 完成记录：multi-parameter cockpit controls

- 扩展了 `POST /api/lever-snapshot`，旧请求 `{ "tra_deg": ... }` 继续兼容；新请求可附带 `radio_altitude_ft`、`engine_running`、`aircraft_on_ground`、`reverser_inhibited`、`eec_enable`、`n1k`、`max_n1k_deploy_limit`。
- 后端继续复用 `HarnessConfig`、`LatchedThrottleSwitches`、`SimplifiedDeployPlant`、`DeployController.evaluate_with_explain(...)` 与 `DeployController.explain(...)`；没有在 JS 中硬编码 controller 真值。
- cockpit 新增紧凑“条件面板”，支持 RA、发动机运行、飞机在地面、反推抑制、EEC enable、N1K、N1K limit；`SW1 / SW2` 仍由 TRA + latch model 推导。
- `TLS / PLS / VDT / deploy position` 已移到折叠的 feedback / diagnostic 区，并明确标注为 simplified first-cut plant feedback，不是完整实时物理模型。
- `当前结论` 摘要增强了上游 blocker 呈现：L1 / L2 / L3 / L4 会按真实 explain failed conditions 给出当前卡点。
- 新增 endpoint tests 覆盖：`radio_altitude_ft = 6.0`、`engine_running = false`、`aircraft_on_ground = false`、`reverser_inhibited = true`、`eec_enable = false`、`n1k >= max_n1k_deploy_limit`。
- 新增静态测试覆盖条件面板 HTML / CSS / JS wiring，以及 feedback / diagnostic 折叠区。
- 未修改 `controller.py`、`SimulationRunner`、`well_harness demo`、`POST /api/demo` 或 `well_harness run`。
