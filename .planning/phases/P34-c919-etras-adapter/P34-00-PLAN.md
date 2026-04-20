---
phase: P34
plan: P34-00
title: C919 E-TRAS 控制逻辑 adapter 接入 — 严格对齐需求 PDF · 手工第 5 条真实链路
status: drafted · Awaiting GATE-P34-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: P33-00 (adapter-scaffolding, never signed)
preconditions:
  - GATE-P32-CLOSURE Approved (2026-04-20)
  - P31-GATE Approved (2026-04-20)
  - main HEAD at e6f9fe6
  - Kogami 2026-04-20 scope pivot: 放弃脚手架模板化，改为手工接入 C919 E-TRAS 真实 adapter
  - 需求文档 PDF 已到位: /sessions/.../uploads/20260417-C919反推控制逻辑需求文档.pdf (10 页, 1013KB)
non-goals:
  - 在 P34 内抽取 adapter 模板 / scaffolding CLI（后续 Phase 积累 ≥6 条真实链路之后再谈）
  - 替换或重构既有 thrust_reverser 逻辑（在 src/well_harness/controller.py）——P34 新增 c919_etras adapter 独立共存
  - Federation / Level 1 / 跨域链路（Kogami 2026-04-20 明示"后续积累足够再考虑"）
  - 修改 v5.2 红线 / 治理宪法（P34 纯能力层）
  - 把 PDF 之外的 C919 其他子系统（EFDS/PLS 内部/FADEC 整机）抽象进来
---

# P34-00 Plan · C919 E-TRAS 控制逻辑 adapter 接入

## 0. TL;DR

按 Kogami 2026-04-20 二次方向指令，P34 把需求 PDF 描述的 C919 E-TRAS（电反推作动系统）完整控制逻辑落成第 5 条真实 adapter 链路，**严格对齐 PDF 每一个信号、每一条逻辑门、每一个时间参数、每一个 Step**。接入方式严格套用既有 4 条 adapter 模板（bleed_air / landing_gear / efds / thrust_reverser_in_controller_py），不自造范式。停在 GATE-P34-PLAN 等签字。

**规模估算：**
- 3 个新文件（c919_etras_hardware_v1.yaml / c919_etras_adapter.py / c919_etras_intake_packet.py），约 800–1100 行
- 1 个新测试文件（test_c919_etras_adapter.py），约 400–600 行
- 1 个 traceability matrix markdown，约 150 行
- 1 个 __init__.py 注册条目（+6 行）
- 预计耗时 2.5–3.5 个 Executor 工作日（Plan/Gate 等待不计）

---

## 1. Scope — PDF 内容穷尽清单

### 1.1 表 1 部件清单（PDF p.1）
11 个部件需要在 adapter 的 `ComponentSpec` 层有对应存在或说明：机械作动筒×4 / PMDU×1 / TLS×1 / 吊挂锁×2 / TRCU×1 / 柔性连杆×4 / 线缆快卸面板×1 / 反推控制接触器×1 / 第三锁控制继电器×1 / 手动抑制断路器×1 / EICU×1（内含两独立模块）。

### 1.2 核心信号（20+，PDF p.2-10 汇总）

按来源分三层：

**A. 飞机系统输入（A/C）**
- `MLG_WOW`（主轮载信号，由 LGCU1/LGCU2 双冗余选择 —— PDF 表 2 5 行逻辑必须完整实现）
- `TR_Inhibited`（反推电气抑制）
- `LGCU1_MLG_WOW_Value` / `LGCU1_MLG_WOW_Valid`
- `LGCU2_MLG_WOW_Value` / `LGCU2_MLG_WOW_Valid`

**B. 油门台输入**
- `TRA`（油门杆解析角度，deg，范围含正推力→反推最大）
- `ATLTLA`（微动开关 1，-1.4°~-6.2° 区间触发）
- `APWTLA`（微动开关 2，-5°~-9.8° 区间触发）

**C. TR 装置传感器**
- `TR_Position`（作动筒 VDT 位置，0~100%）
- `VDT_Sensor_Valid`
- 3 把锁状态（每把 2 个 LS 传感器，共 6 个）：`TLS_LS_A/B` / `Left_Pylon_LS_A/B` / `Right_Pylon_LS_A/B` / `PLS_LS` ×2
- `E_TRAS_Over_Temp_Fault`
- `TRCU_Power_Status`

**D. FADEC / EICU 输出**
- `EICU_CMD2`（AEICU2）
- `EICU_CMD3`（AEICU3）
- `TR_Command3_Enable`
- `FADEC_Deploy_Command`（CMD1，展开）
- `FADEC_Stow_Command`（CMD1，收起）
- `TR_WOW`（FADEC 用的带时间过滤轮载信号）

**E. 模式/工况**
- `Engine_Running`（发动机慢车及以上）
- `FADEC_Maintenance_Mode`
- `TR_Maintenance_Command_from_AC`
- `TRCU_in_Menu_Mode`
- `N1k`（% 发动机转速，相对量）
- `Max_N1k_Deploy_Limit`（79%~89%，随环境温压）
- `Max_N1k_Stow_Limit`

### 1.3 4 条逻辑节点（LogicNodeSpec）

对应 PDF §1.1.1 / §1.1.2 / §1.1.3 + TR_Command3_Enable 子图（图 4）：

**L1 · EICU_CMD2**（图 2）
```
EICU_CMD2 = MLG_WOW_valid_true
          AND NOT TR_Inhibited
          AND Comm2_timer < 30s
          AND NOT (TR_Position >= 80% for 0.5s confirmation)
```
持续时间过滤：Confirmation time 0.5s（TR_Position_Deployed）、Comm2_timer 状态机（上电初始化 0s / ATLTLA 0→1 重置为 0s / ATLTLA 持续 1 则持续计时）

**L2 · EICU_CMD3**（图 3，RS 触发器结构）
```
S = (Engine_Running OR TRCU_in_Menu_Mode)
    AND MLG_WOW_valid_true
    AND NOT TR_Inhibited
    AND TR_Deploy_Commanded (即 APWTLA=1)
R* = NOT TR_Command3_Enable
EICU_CMD3 = S-R* latch 当前状态
```

**L3 · TR_Command3_Enable**（图 4，嵌套子图）
```
TR_Command3_Enable = NOT (
    (TR_Stowed_And_Locked_持续_1s AND TRA >= -1.4° AND 115VAC_at_TRCU_input)
    OR TR_Emergency_Stop_signal (E_TRAS_Over_Temp_Fault)
)
```
持续时间过滤：TR_Stowed & Locked 需要 1s 确认

**L4 · FADEC_Deploy_Command（CMD1）**（图 5）
```
CMD1 = ((Engine_Running) OR (FADEC_Maintenance_Mode AND TR_Maintenance_Command_from_AC))
     AND NOT TR_Inhibited
     AND (TLS_Both_Pylon_Locks_Unlocked_VALID
          OR (ATLTLA=1 AND ≥1/2 TLS_LS_unlocked_VALID
              AND ≥1/2 Right_Pylon_LS_unlocked_VALID
              AND ≥1/2 Left_Pylon_LS_unlocked_VALID, 持续 400ms))
     AND TR_WOW = 1
     AND N1k <= Max_N1k_Deploy_Limit
     AND TRA < -11.74°
```
持续时间过滤：400ms 锁确认 / TR_WOW（2.25s TRUE → TRUE，120ms FALSE → FALSE）

（Stow 侧 CMD1 与 Deploy 对称，PDF 未单独画图，按文字 Step 7~10 推导：`N1k ≤ Max_N1k_Stow_Limit` 后 FADEC_Stow_Command=1；PDF 未给收起门其他条件，**留为 Open Question Q3**。）

### 1.4 Step 1~10 时间线（PDF p.2-4）

完整的着陆→展开→最大反推→收起→断电十步。将以 `AcceptanceScenarioSpec` 形式落地为：
- `scenario_nominal_deploy_stow`（Step 1~10 全链路回放 ~30s 时间轴）

关键时间常数（PDF 明示）：
- 展开 2~3s（环境相关）
- 慢车→最大 ~5s
- 转速下降 ~7.5s
- 收起 ~3s
- 最大→完全收起 ~11s
- FADEC 确认收起 1s

### 1.5 故障模式（FaultModeSpec）

PDF 明示或隐含的故障路径 → 最小集：
- `fault_e_tras_over_temp`：E-TRAS Over Temp Fault 触发 → TR_Command3_Enable=0 → CMD3 断电
- `fault_tr_inhibited`：电气抑制 → 全链路阻断（CMD2/CMD3/CMD1 均不能发出）
- `fault_n1k_too_high`：N1k 超过 Max_N1k_Deploy_Limit → CMD1 不发出，反推不展开
- `fault_lgcu_disagreement`：LGCU1 vs LGCU2 WOW 不一致 → MLG_WOW=0 → CMD2/CMD3 阻断（PDF 表 2 第 2 行）
- `fault_lock_sensor_partial_loss`：TLS/吊挂锁传感器部分失效 → 400ms 确认路径被迫走"≥1/2 有效"分支（PDF §1.1.3 ③）

---

## 2. 架构/接入方案 —— 套用既有模板，不自造

### 2.1 文件清单

```
src/well_harness/adapters/
  c919_etras_adapter.py          <- 主 adapter（依照 bleed_air_adapter.py 模板）
  c919_etras_intake_packet.py    <- 工作台 intake（依照 bleed_air_intake_packet.py 模板）

config/hardware/
  c919_etras_hardware_v1.yaml    <- 硬件/阈值/时间参数（依照 thrust_reverser_hardware_v1.yaml 模板）

tests/
  test_c919_etras_adapter.py     <- 单测（依照 tests/adapters/test_bleed_air_adapter.py 模板）

docs/c919_etras/
  traceability_matrix.md         <- PDF 每节/每图/每表 → 代码行 + 单测名映射（甲方审查友好）

src/well_harness/adapters/__init__.py  <- 追加 6 行注册
```

### 2.2 Metadata 常量

```python
C919_ETRAS_SYSTEM_ID = "c919-etras"
C919_ETRAS_SOURCE_OF_TRUTH = "src/well_harness/adapters/c919_etras_adapter.py"
C919_ETRAS_DESCRIPTION = (
    "C919 aircraft Electric Thrust Reverser Actuation System (E-TRAS). "
    "Implements the 4-step control logic chain specified in the 20260417 C919 "
    "reverse-control-logic requirements document: EICU CMD2, EICU CMD3, "
    "TR_Command3_Enable, and FADEC Deploy Command (CMD1), plus the canonical "
    "Step 1-10 land-deploy-stow scenario."
)

C919_ETRAS_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="c919-etras-controller-adapter",
    system_id=C919_ETRAS_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=C919_ETRAS_SOURCE_OF_TRUTH,
    description=C919_ETRAS_DESCRIPTION,
)
```

### 2.3 snapshot 提取器

复用 bleed_air_adapter.py 的三个 helper（`_require_snapshot_value` / `_snapshot_bool` / `_snapshot_float`），新增：
- `_snapshot_optional_bool`（用于 `*_Valid` 位，允许 None 表示传感器缺失）
- `_snapshot_duration_state`（用于持续时间过滤器内部状态，调用方传入历史快照序列）

### 2.4 关键实现细节

**持续时间过滤器**：Confirmation 0.5s / 400ms / 1s / 2.25s / 120ms 的 debounce 用显式的 `{name}_hold_time_s` 快照字段实现（调用方在每个 tick 维护该字段），或 adapter 内部维护 prev-state + timestamp deltas。**Plan 默认方案：前者（显式状态字段进 snapshot）**，因为这个项目的 adapter 是纯函数 evaluate_snapshot，无状态，符合既有范式。**如 Kogami 要求状态机风格，提至 Q4 开口问题。**

**RS 触发器（EICU_CMD3）**：实现为 `prev_cmd3 + (S, R*)` 的组合函数：`cmd3 = (prev_cmd3 OR S) AND NOT R*`。snapshot 必须带 `prev_eicu_cmd3` 字段。

**MLG_WOW 选择表（表 2）**：原样落地为一个私有函数 `_select_mlg_wow(v1_value, v1_valid, v2_value, v2_valid) -> bool`，返回值严格按 PDF 5 行表，单测覆盖全部 5 行。

### 2.5 与 thrust_reverser（现有）共存策略

现有 `src/well_harness/controller.py` 的 thrust-reverser 逻辑（logic1/2/3/4）是"简化泛型反推逻辑"，不是 C919 具体型号。P34 新增的 `c919_etras` adapter 是**更详细、更 PDF-准确的真实机型落地**。两者共存：
- 现有 `thrust-reverser` 继续服务于通用演示 / 对抗测试 / 既有 e2e
- 新增 `c919-etras` 专门服务于 C919 E-TRAS PDF 需求验收
- `traceability_matrix.md` 会明示两者的差异（哪些信号是 C919 特有 / 哪些泛型反推已覆盖）
- **不改动 thrust-reverser 任何一行代码**（保持既有基线）

---

## 3. Tier 1 对抗性自审（≥3 条反驳，交付 5 条）

### C1 · "PDF 只有 10 页，细节一定漏了，adapter 会是'看起来符合但实际不准确'"

**反驳：**
- Plan §1.2 已把 PDF 中所有命名信号（20+）逐条列出，**无一遗漏**；
- Plan §1.3 把 4 张逻辑图（图 2/3/4/5）以及表 2 的 5 行冗余选择表逐条转译为伪代码；
- Plan §1.4 把 Step 1~10 的全部时间常数（2~3s / 5s / 7.5s / 3s / 11s / 1s / 30s / 0.5s / 400ms / 2.25s / 120ms）列出；
- 但确有 3 个 PDF 灰区（Stow 侧 CMD1 完整逻辑、Comm2_timer 在 EICU 重启后是否保留、Max_N1k_Stow_Limit 具体数值）—— 这 3 个全部提升为 **Open Questions Q1/Q2/Q3**，Plan 不默认，等 Kogami 或 C919 TRCU 团队确认；
- Exit criterion 强制每条逻辑节点对应 ≥1 个单测 case 指向 PDF 具体段落，traceability matrix 三向闭环。

### C2 · "既有 thrust_reverser 已经覆盖反推逻辑，再加 c919_etras 是重复工作"

**反驳：**
- 既有 `controller.py` 的 thrust-reverser 是**简化泛型逻辑**，没有：MLG_WOW 双 LGCU 冗余选择、EICU RS 触发器、TR_Command3_Enable 嵌套图、N1k 动态 deploy limit、FADEC 维护模式、LGCU WOW 2.25s/120ms 非对称时间常数、400ms 锁确认、E-TRAS Over Temp 紧急断电等 PDF 明示要求；
- 新增 c919_etras **不是重复**，是把现有"反推概念玩具"升级到"可交付给 C919 TRCU 团队做需求 sign-off 的真实机型"；
- 保留 thrust_reverser 是为了既有 686-test 基线不崩（R1 不动 main HEAD 已签章），并让泛型 demo / onboarding 路径仍可走；
- Plan 明示"不改 thrust_reverser 一行"，零回归风险。

### C3 · "Over-engineering —— 直接把 PDF 逻辑硬编码进 Python 就行，搞 20+ ComponentSpec + 4 LogicNode + 10-step scenario 太重"

**反驳：**
- 这是 Kogami 原话"**严格按照一样的模板、规格**"的直接含义 —— 4 条既有 adapter 全部是这个结构（ComponentSpec / LogicNodeSpec / AcceptanceScenarioSpec / FaultModeSpec 四元组），**不用这个结构等于违反指令**；
- 工作台生态（intake_packet / playback / fault_diagnosis / knowledge_capture）都依赖这四元组契约，hardcode 版本跑不通任何既有 pipeline；
- 甲方"需求→实现→测试"三向可追溯性（traceability_matrix.md）就是这个结构的衍生价值，直接 hardcode 会让甲方 sign-off 路径断链。

### C4 · "手工实现 RS 触发器 + 持续时间过滤一定有 off-by-one 错误"

**反驳：**
- 承认此风险高。P34-03 测试 Plan §5 **强制**为：
  - RS 触发器：latch 保持 / set-then-reset / reset-then-set / set 和 reset 同时（PDF 图 3 标了 R*，说明 Reset 有优先级）→ ≥4 条 case
  - 持续时间过滤：每个 debounce 时间常数 ≥3 条 case（刚到、刚过、未到）× 5 个时间常数 = 15+ case
  - RS + 持续时间复合场景：TR_Stowed & Locked 1s 确认期内收到 Emergency Stop → 应立即触发 ≥1 条
- 以及 Step 1~10 完整回放一次即可覆盖所有 debounce 边界的主路径；
- 双保险：写完代码后 pytest 全绿 + 对着 PDF §1.1.1~1.1.3 对每条 logic 逐条"指"到代码行号（traceability matrix 二遍审查）。

### C5 · "PDF 没有给出 snapshot 的具体字段名约定，adapter 命名冲突怎么办"

**反驳：**
- PDF 中的信号中文名 + 英文缩写已经明确：Plan §1.2 按 PDF 原文照搬英文缩写（MLG_WOW, TRA, ATLTLA, APWTLA, EICU_CMD2/3, TR_Command3_Enable, N1k, TR_WOW, etc.），在 snapshot 字段名上**严格使用 PDF 原词 + 小写下划线**（如 `mlg_wow`, `tra`, `atltla`, `apwtla`, `eicu_cmd2`, `tr_command3_enable`, `n1k`, `tr_wow`）；
- 既有 4 条 adapter 的 snapshot 字段命名规则一致（`valve_position` / `inlet_pressure` / `gear_position` 都是小写下划线），新 adapter 完全对齐；
- 因为 c919_etras 是独立 `system_id`，即使与 landing_gear 的 `mlg_wow` / `squat_switch` 语义重叠，namespacing 不会冲突（不同 adapter 的 snapshot 各自独立）。

---

## 4. Open Questions（GATE-P34-PLAN 签字时必须逐条仲裁）

### Q1 · Stow 侧 FADEC_Stow_Command（CMD1 收起）完整逻辑？

PDF 只在 Step 7~8 文字叙述提到 `N1k ≤ Max_N1k_Stow_Limit → FADEC_Stow_Command=1`，**没有画图 / 没有给 TR_Inhibited / 维护模式 / WOW 等辅助条件**。

- 选项 A（Executor 默认提案）：对称于 Deploy Command，但把"N1k ≤ Max_N1k_Deploy_Limit"换成"N1k ≤ Max_N1k_Stow_Limit"、把 "TRA < -11.74"换成"TRA=0 或接近 0 deg"、其他条件保留（Engine_Running / NOT TR_Inhibited / TR_WOW=1）；
- 选项 B：只用 PDF 字面条件（仅 N1k），更保守；
- 选项 C：推迟 Stow 侧实现，P34 只做 Deploy 侧 + 明示"Stow 侧在后续 Phase 从 TRCU 团队拿到补充规范再实现"。

**Executor 推荐：A（对称提案，但在 traceability matrix 里明示"PDF §Step 7~8 未明确，采用对称假设"）。**

### Q2 · Comm2_timer 在 EICU 断电/重启后是否保留？

PDF §1.1.1 ③"当 EICU 上电时，EICU CMD2 计时初始化为 0s"—— 这意味着 EICU 每次重启 timer 归零。但 PDF 没说：EICU 上电后首次着陆 ATLTLA 还没变 0→1 时，timer 的状态是 0s（未启动）还是"保持 0s 并冻结"？

- 选项 A（Executor 默认提案）：上电后 timer=0 且冻结，只有 ATLTLA 0→1 跳变触发首次"重置为 0 并开始计时"；timer 冻结状态下 EICU_CMD2 的 `Comm2_timer < 30s` 条件恒真（因为 0s < 30s），但 ATLTLA=0 所以不会触发实际 CMD2；
- 选项 B：上电即 timer 开始计时，30s 后 CMD2 被永久禁用，这显然荒唐但是 PDF 字面可读；
- 选项 C：问 Kogami / C919 TRCU 团队拿补充条款。

**Executor 推荐：A（和工程直觉一致，且不会被 B 陷阱卡住首次着陆）。**

### Q3 · Max_N1k_Stow_Limit 的具体数值？

PDF §Step 7 只说"N1k ≤ Max_N1k_Stow_Limit"，没给数值。Deploy 侧 PDF §1.1.3 ⑤说 `Max_N1k_Deploy_Limit ≈ 79%~89%` 随环境变化。

- 选项 A（Executor 默认提案）：把 `Max_N1k_Stow_Limit` 设为一个配置值（hardware YAML 中 `max_n1k_stow_limit_percent: 30.0` —— 工程常识反推值），留 comment "PDF 未明确，取工程常识 30% 作为 placeholder"，traceability matrix 明示这是 assumption；
- 选项 B：设为 `max_n1k_stow_limit_percent: null` 强制调用方传入，不设默认；
- 选项 C：不做 Stow 侧（同 Q1 C）。

**Executor 推荐：A（30% placeholder + 明示假设）。**

---

## 5. Sub-phase 分解

### P34-01 · Hardware YAML（2–4 小时）
写 `config/hardware/c919_etras_hardware_v1.yaml`：
- `sensor`：MLG_WOW / TRA / TR_Position / N1k / 各锁位 LS / 两 LGCU valid bit（总 20+ 字段）
- `logic_thresholds`：tra_deploy_threshold_deg = -11.74 / tra_stow_angle_deg = 0 / sw1 window [-1.4, -6.2] / sw2 window [-5, -9.8] / tr_deployed_percent = 80 / max_n1k_deploy_pct_min = 79 / max_n1k_deploy_pct_max = 89 / max_n1k_stow_pct = 30（Q3-A）
- `physical_limits`：deploy_time_s = [2, 3] / stow_time_s = 3 / idle_to_max_s = 5 / n1k_ramp_down_s = 7.5 / max_to_fully_stowed_s = 11
- `timing`：confirmation_0_5_s / comm2_timer_limit_s = 30 / lock_confirm_400ms_s = 0.4 / tr_wow_true_persist_s = 2.25 / tr_wow_false_persist_s = 0.12 / tr_stowed_locked_confirm_s = 1.0 / fadec_stow_confirmation_s = 1.0
- `valid_outcomes`：[eicu_cmd2 / eicu_cmd3 / tr_command3_enable / fadec_deploy_cmd1 / fadec_stow_cmd1 / tr_deployed / tr_stowed_locked]

### P34-02 · Adapter 实现（8–12 小时）
写 `src/well_harness/adapters/c919_etras_adapter.py`：
- Metadata 常量 + SYSTEM_ID
- 5 个 snapshot helper（复用 + 新增 2 个）
- `_select_mlg_wow` 私有函数（PDF 表 2 完整 5 行）
- `build_c919_etras_workbench_spec` 函数：构造 ControlSystemWorkbenchSpec
  - components: 20+ ComponentSpec（对照 §1.2 清单）
  - logic_nodes: 4 个 LogicNodeSpec（L1~L4）
  - acceptance_scenarios: 1 个完整 Step 1~10 回放（~30s 轴）+ 可选 2 个单点 scenario
  - fault_modes: 5 个 FaultModeSpec（对照 §1.5）
  - tags: ("c919", "e-tras", "thrust-reverser", "aviation", "fifth-adapter")
- `C919ETRASControllerAdapter` 类：`metadata` / `load_spec` / `evaluate_snapshot`
- `build_c919_etras_controller_adapter` factory
- 配套 `c919_etras_intake_packet.py`（依照 bleed_air_intake_packet.py 骨架）
- 更新 `src/well_harness/adapters/__init__.py` 追加 3 行 import + 3 行 __all__

### P34-03 · 测试（6–10 小时）
写 `tests/test_c919_etras_adapter.py`：
- (a) 4 个 LogicNode 真值表，每个 ≥6 case：
  - L1 EICU_CMD2：MLG_WOW off / TR_Inhibited on / Comm2_timer=30 / TR_Deployed / 全条件满足 / 冗余失效
  - L2 EICU_CMD3：Set only / Reset only / Set+Reset（R* 优先级）/ latch hold / Engine not running / TRCU menu mode 补路
  - L3 TR_Command3_Enable：nominal false（未收起）/ nominal true（收起上锁 1s 确认）/ Emergency Stop 立即 false / TRA 条件 / 115VAC 条件
  - L4 CMD1：全路径满足 / N1k 超限 / TR_WOW=0 / TRA 不够 / 400ms 锁确认未到 / 锁 VALID 路径 vs ≥1/2 路径
- (b) MLG_WOW 选择表 5 行完整覆盖（独立 5 case）
- (c) Step 1~10 整条时间线 end-to-end 回放（1 个 scenario，单测中分 10 个断言检查 CMD2/CMD3/CMD1/TR_Deployed/TR_Stowed_Locked 在各关键时间点的值）
- (d) 5 个故障注入 smoke（对应 §1.5）
- (e) snapshot validation：缺失字段 raise KeyError / 类型错误 raise TypeError

### P34-04 · 三轨回归 + Traceability Matrix（3–5 小时）
- 跑 pytest 全量（预期：684 + 新增 ~40 ≈ 720+ 通过，1 skip, 49 deselected 不变）
- 跑 opt-in e2e（49 保持，无新增除非 Kogami 要求）
- 跑对抗测试套（8/8 保持绿）
- 写 `docs/c919_etras/traceability_matrix.md`：
  - 表 1：PDF 信号 → adapter snapshot 字段 → ComponentSpec id（20+ 行）
  - 表 2：PDF 4 逻辑图 → LogicNodeSpec id → 代码行号 → 单测函数名（4 行）
  - 表 3：Step 1~10 → scenario transitions → 单测断言（10 行）
  - 表 4：故障模式 → FaultModeSpec id → 单测（5 行）
  - 表 5：PDF 表 2（MLG_WOW 5 行）→ _select_mlg_wow 分支 → 单测 case（5 行）
  - 附录 A：3 个 PDF 灰区 + Q1/Q2/Q3 Executor 假设 + 等 TRCU 团队 sign-off 的待办列表

### P34-05 · Closure（2–3 小时）
- 单文件 commit（trailer: `Execution-by: opus47-claudeapp-solo · v5.2`）
- Notion 治理页追加 `## P34 DECISION · v5.2 solo-signed (2026-04-20)`：PDF 输入证迹（文件 hash + 10 页）+ 4 逻辑节点代码行 + 单测数据 + traceability matrix 链接 + Tier 1 5 条反驳落地结果 + Q1/Q2/Q3 Kogami 批复
- 停在 `GATE-P34-CLOSURE`，等 Kogami 签字
- 更新 ROADMAP / 下一步方向建议（继续累积第 6 条真实链路 vs 回到脚手架模板化 vs 开始谈 Federation）

---

## 6. 退出准则（Exit Criteria）

P34 完成且 Kogami 可签 `GATE-P34-CLOSURE: Approved` 需全部满足：

1. **PDF 对齐**：traceability matrix 五张表 100% 覆盖，每行都能回指到 PDF 具体段落 + 代码文件行号 + 单测名
2. **4 逻辑节点正确性**：单测 ≥30 case 全部通过，包含持续时间边界、RS 触发器边界、MLG_WOW 冗余 5 行、400ms 锁确认两条路径
3. **Step 1~10 回放**：scenario 完整通过，10 个关键时间点断言全部对上 PDF 文字描述
4. **故障注入**：5 个 FaultMode 每个 ≥1 case 通过
5. **三轨零回归**：pytest/e2e/adversarial 相对 P32 基线仅有新增 case，无既有测试失败
6. **v5.2 红线合规**：R1 不动 main HEAD 不签、R2 Gate 只给 Kogami 签、R3 ≥3 反驳已交（本 Plan 5 条）、R4 P34 由 Kogami 2026-04-20 明示发起、R5 provenance-first（Plan 每条设计都可追溯到 PDF 某段）
7. **Notion DECISION 写入**：含 PDF hash + 4 逻辑行号 + 单测数据 + Tier 1 + Q1/Q2/Q3 批复
8. **Open Questions Q1/Q2/Q3 批复**：Kogami 明示选 A/B/C 或给补充条款

---

## 7. 风险与回滚

**风险 R1**：发现 PDF 存在的灰区比 Q1/Q2/Q3 更多（如图像细节看不清、某个信号时序暗含条件），导致 Executor 在 P34-02 期间出现第 4、第 5 个 Open Question。
- 缓解：P34-02 期间任何新 Open Question 立即暂停实现、写进 traceability matrix 附录 A、在 Notion DECISION 里明示，**不 Executor 自裁**。

**风险 R2**：单测中 RS 触发器 / 持续时间过滤的边界条件验证覆盖不足，通过 CI 但上真机出 bug。
- 缓解：Exit 准则 #2 要求 ≥30 case、C4 反驳指定的具体覆盖点强制落实。

**风险 R3**：新增 20+ ComponentSpec 在既有工作台 pipeline（playback / fault_diagnosis / knowledge_capture）中触发未知 schema 校验失败。
- 缓解：P34-04 三轨回归如果挂掉某个 validation 测试，**先排查 schema 兼容性**，必要时在 P34 内补 schema 适配 PR，而不是强行跳过。

**回滚预案**：P34-02 实现代码为新增文件，不改动既有 4 个 adapter 或 controller.py。一旦 Kogami 在 P34-04/05 发现严重问题，通过删除新增 6 个文件即可完全回滚。`git checkout` 既有文件到 P32 HEAD (e6f9fe6) 零痕迹。

---

## 8. v5.2 红线合规声明

| 红线 | 本 Plan 合规情况 |
|---|---|
| R1 · 不自把 main HEAD | 是。本 Plan 不触发 main advance；新 commit 走独立分支 codex/p34-c919-etras |
| R2 · Gate 只给 Kogami 签 | 是。GATE-P34-PLAN / GATE-P34-CLOSURE 两道 Gate，Executor 不签 |
| R3 · Tier 1 ≥3 反驳 | 超额。交付 5 条反驳（C1~C5） |
| R4 · 不自选 Phase | 合规。P34 由 Kogami 2026-04-20 明示指令发起（"加入 C919 E-TRAS 控制逻辑"） |
| R5 · provenance-first | 是。Plan 每条设计都指向 PDF 页/节/图，Open Questions 明示 PDF 灰区不由 Executor 自裁 |

---

## 9. 停点

按 v5.2 Solo Mode 规则，**P34-00 本身即 stop point**。

Executor 在本文落盘后等 Kogami 两件事：
- (1) `GATE-P34-PLAN: Approved` 签字
- (2) Q1 / Q2 / Q3 三个开口问题的仲裁答复（选 A/B/C 或给补充条款）

收到两项后方启动 P34-01（Hardware YAML），**不擅自预跑任何一行代码**。

---

**Owner:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Reviewer (awaiting):** Kogami · GATE-P34-PLAN
**Supersedes:** P33-00 (adapter-scaffolding, never signed before this pivot)
**Next:** P34-01 (blocked on GATE-P34-PLAN + Q1/Q2/Q3 answers)
