# Thrust-Reverser Traceability Matrix — docx ↔ controller.py ↔ YAML

**Phase:** P36β-04 · v5.2 solo-signed · 2026-04-20
**Authority:** Kogami (project owner), `GATE-P36β-PLAN: Approved` 2026-04-20 (Q1-Q5 delegated to Executor recommendation)

## 背景

P35α 登记表（`docs/provenance/adapter_truth_levels.md`）把 `thrust-reverser` 链路登为 `demonstrative + Upgrade pending`，等待 P36β 从 `Downloads/控制逻辑(1).docx` 建立追溯。

P36β 执行后本 matrix 建立：
- **上游 docx** `uploads/20260409-thrust-reverser-control-logic.docx`（SHA256 `6e457fe3...276133a5` · 230,930 bytes · 57 paragraphs · 2 tables · 1 media）—— 作为 requirement reference
- **代码真值** `src/well_harness/controller.py`（`DeployController` class · 4 logic groups）+ `src/well_harness/models.py`（`HarnessConfig` · 13 常数）—— 作为 truth source
- **硬件参数** `config/hardware/thrust_reverser_hardware_v1.yaml`（24 行 docx 头注释 + parameters 段）—— 作为 cross-verified table

本 matrix 为这三方的**字段级映射**。覆盖：
- 表 1 · 部件映射（docx 表 1 · 11 部件 → code/YAML 字段）
- 表 2 · 交联设备映射（docx 表 2 · 4 设备 → code/YAML 字段）
- 表 3 · 输入输出信号映射（docx §3-§4 · 13 信号 → `ResolvedInputs` / `ControllerOutputs`）
- 表 4 · 4 工作逻辑映射（docx §6 · 4 工作逻辑 → `DeployController` 4 logic 组）
- 表 5 · 阈值常数完整登记（13 常数 · docx 值 vs code 值 · 7 直接 trace / 2 Executor 假设 / 4 Kogami 待仲裁）
- Appendix A · Open Assumptions（6 项待 sign-off）

---

## 表 1 · 反推系统部件映射（docx 表 1 · 11 行 × 3 列）

| # | docx 部件名称（中文/英文）| 数量-单发 | code / YAML 字段 | 备注 |
|---|-----------------------|----------|-----------------|------|
| 1 | 电子反推作动控制器（ETRAC）| 1 | `controller.py::DeployController`（类）+ `tls_115vac_cmd` / `etrac_540vdc_cmd` / `pdu_motor_cmd` 输出 | 代码层的 ETRAC 指令出口是 `ControllerOutputs` 的 3 个字段 |
| 2 | 功率驱动单元（PDU）| 1 | `ControllerOutputs.pdu_motor_cmd` | 由 logic3 active 激活 |
| 3 | 柔性轴 | 4 | —（非信号部件）| docx 表 1 表述的是物理部件数，代码层不建 ComponentSpec（D1=A Lean 不走 workbench spec）|
| 4 | 机械作动筒 | 4 | —（非信号部件）| 同上 |
| 5 | 第三锁定系统（TLS）| 1 | `ControllerOutputs.tls_115vac_cmd` / `ResolvedInputs.tls_unlocked_ls` | logic1 激活 115VAC 解锁；logic3 需 TLS 已解锁 |
| 6 | 主锁定系统（PLS）| 4 | `ControllerOutputs.pls_power_cmd` | 由 logic3 active 激活 |
| 7 | 位移传感器（VDT）| 2 | `ResolvedInputs.deploy_90_percent_vdt`（布尔化：VDT > 90% = True）| Appendix A.2 · 90% 阈值 Kogami 待仲裁 |
| 8 | 接近传感器（LS）| 10 | `ResolvedInputs.tls_unlocked_ls` + PLS 相关（代码简化）| docx 10 个 LS，代码仅暴露 TLS 解锁 LS 一路 |
| 9 | 手动驱动单元（MDU）| 2 | —（非信号部件 · 人工操作）| 代码层不建模 |
| 10 | 线缆 | N/A | —（非信号部件）| 同上 |
| 11 | 设备安装支架 | N/A | —（非信号部件）| 同上 |

**结论：** 代码层只建模 docx 表 1 的 **4 类信号部件**（ETRAC/PDU 输出 + TLS/VDT/LS/PLS 输入反馈），物理部件（柔性轴/作动筒/MDU/线缆/支架）不进 code（符合"控制逻辑"的 scope）。

---

## 表 2 · 与反推系统交联的设备映射（docx 表 2 · 4 条目）

| # | docx 部件名称 | code / YAML 字段 | 备注 |
|---|--------------|-----------------|------|
| 1 | 电源 RPDU（115VAC 供电源）| `ResolvedInputs.rpdu_115vac_available`（如存在）或隐含为始终 available | docx §3 提到 "电源RPDU的115 VAC供电" 是信号，代码层处理为上游前提 |
| 2 | DIU（数字接口单元）| 代码层不直接建模；SW1 触发通过 `ResolvedInputs.sw1` 映射 DIU 控制信号 | docx §3 "DIU的控制信号" 对应 code logic1 的 `sw1` 条件 |
| 3 | EICU（发动机接口控制单元）| `ResolvedInputs.reverser_inhibited`（is not EICU 540VDC cmd）· 注：`ControllerOutputs.etrac_540vdc_cmd` 是代码**反推侧**输出 | docx §3 "EICU的控制信号，用来控制540VDC接通" —— 对应 code logic2 激活后 etrac_540vdc_cmd 输出 |
| 4 | EEC（发动机电子控制）| `ResolvedInputs.eec_enable` / `reverser_not_deployed_eec` / `ControllerOutputs.eec_deploy_cmd` | docx §3 "EEC的展开和收起指令" + §5 "EEC使能信号" —— 代码层有 3 个相关字段 |

---

## 表 3 · 输入/输出/监测信号映射（docx §3-§5）

### 表 3A · 反推系统输入信号（docx §3 · 8 项 · 段 9-16）

| docx 段 | docx 描述 | code `ResolvedInputs` 字段 | 单位/类型 |
|--------|----------|---------------------------|----------|
| 9 | 油门台的开关信号 SW1 和 SW2（0/1）| `sw1` / `sw2` | bool |
| 10 | DIU 的控制信号（0/1）| （隐含于 `sw1` 触发逻辑） | bool |
| 11 | 油门台的角度信号 TRA（连续位移）| `tra_deg` | float, deg |
| 12 | EICU 的控制信号（控制 540VDC 接通）| 代码层处理为 `reverser_inhibited` 的非（!inhibited）| bool |
| 13 | EICU 的 28V 供电 | —（标记"不管"） | — |
| 14 | 电源 RPDU 的 115VAC 供电（电压信号）| （隐含前提）| — |
| 15 | EEC 的展开和收起指令（0/1）| `eec_enable` / `reverser_not_deployed_eec` | bool |
| 16 | 位移传感器的激励信号 | —（标记"不管"） | — |

### 表 3B · 反推系统输出信号（docx §4 · 5 项 · 段 19-23）

| docx 段 | docx 描述 | code `ResolvedInputs`/`ControllerOutputs` 字段 | 对应逻辑 |
|--------|----------|----------------------------------------------|---------|
| 19 | TLS 的传感器信号（0/1）| `ResolvedInputs.tls_unlocked_ls` | logic3 条件 |
| 20 | 作动器传感器信号（VDT 连续位移）| `ResolvedInputs.deploy_90_percent_vdt` | logic4 条件（阈值 90% · A.2）|
| 21 | PDU 电机信号 | `ControllerOutputs.pdu_motor_cmd`（由 logic3 激活）| — |
| 22 | TLS 的供电状态信号（0/1）| `ControllerOutputs.tls_115vac_cmd`（由 logic1 激活）| — |
| 23 | PLS 的传感器信号（0/1）| `ControllerOutputs.pls_power_cmd`（由 logic3 激活）| — |

### 表 3C · 需要监测的信号（docx §5 · 15 项 · 段 26-40）

docx §5 段 26-40 列 15 项监测信号，全部是前述 §3/§4 信号的重复或组合（如 "反推未被抑制信号" / "飞机处于地面状态信号"）。代码层对应 `ResolvedInputs` 中的 `reverser_inhibited` / `aircraft_on_ground` / `engine_running` / `reverser_not_deployed_eec` 等字段。**完整映射见表 4 的逻辑条件列。**

---

## 表 4 · 4 工作逻辑映射（docx §6 · 段 44-53 · 核心）

### 表 4.1 · 工作逻辑 1（docx §47 · 3 条件 → code `controller.py:26-49` · 4 条件）

| docx 条件 | docx 描述 | code 条件 | 阈值 | 单测 |
|----------|----------|----------|------|------|
| 1 | 飞机无线电高度低于 6 英尺信号 | `radio_altitude_ft < logic1_ra_ft_threshold` | `6.0` ft | `DeployControllerTests::test_logic1_requires_all_confirmed_conditions` / `test_logic1_ra_threshold_is_strictly_below_six_feet` |
| 2 | 反推未被抑制信号 | `not reverser_inhibited` | - | 同上 |
| 3 | 反推力装置未展开信号 | `reverser_not_deployed_eec == True` | - | 同上 |
| — | （docx 段 45 提 SW1 但放在工作过程，非 §47 工作逻辑 1 list） | `sw1 == True` | - | `SwitchModelTests::test_sw1_sw2_latches_hold_until_reverse_selection_returns_near_zero` |

**层次差异说明：** docx §47 描述"工作逻辑 1"的 3 条件为**语义逻辑**（DIU 判定是否可发指令）；docx §45 在"工作过程"描述 DIU 实际动作依赖 SW1 触发（油门杆角度在 SW1 区间）。代码 `logic1_conditions` 是"DIU 实际发出 TLS 解锁 115VAC 指令"的 full gate，因此合并两者为 4 条件。**不是 docx/code 的冲突**，是表达层次差异。

### 表 4.2 · 工作逻辑 2（docx §49 · 5 条件 → code `controller.py:50-68` · 5 条件 · 1:1）

| docx 条件 | code 条件 | 阈值 | 单测 |
|----------|----------|------|------|
| 1 发动机处于运行状态信号 | `engine_running == True` | - | `DeployControllerTests`（通过综合 test）|
| 2 飞机处于地面状态信号 | `aircraft_on_ground == True` | - | 同上 |
| 3 反推处于非抑制状态信号 | `not reverser_inhibited` | - | 同上 |
| 4 油门台微动开关 2 闭合信号 | `sw2 == True` | - | 同上 |
| 5 EEC 使能信号 | `eec_enable == True` | - | 同上 |

### 表 4.3 · 工作逻辑 3（docx §51 · 6 条件 → code `controller.py:69-106` · 6 条件 · 1:1）

| docx 条件 | code 条件 | 阈值 | 单测 |
|----------|----------|------|------|
| 1 发动机处于运行状态信号 | `engine_running == True` | - | `test_logic3_uses_tls_unlock_and_tra_threshold` |
| 2 飞机处于地面状态信号 | `aircraft_on_ground == True` | - | 同上 |
| 3 反推处于非抑制状态信号 | `not reverser_inhibited` | - | 同上 |
| 4 TLS 已解锁信号 | `tls_unlocked_ls == True` | - | 同上 |
| 5 发动机 N1k < 最大 N1k 展开限制信号 | `n1k < inputs.max_n1k_deploy_limit` | `max_n1k_deploy_limit`（per-snapshot, docx 无具体值）| `test_logic3_requires_n1k_below_deploy_limit` |
| 6 油门杆解析角度 ≤ -11.74° 信号 | `tra_deg <= logic3_tra_deg_threshold` | `-11.74` deg | `test_logic3_blocks_commands_when_tra_has_not_reached_threshold` / `test_logic3_explain_includes_threshold_details` |

### 表 4.4 · 工作逻辑 4（docx §53 · 4 条件 → code `controller.py:107-130` · 4 条件 · 1:1）

| docx 条件 | code 条件 | 阈值 | 单测 |
|----------|----------|------|------|
| 1 反推完全展开信号 | `deploy_90_percent_vdt == True` | VDT > `90.0%`（Appendix A.2）| `test_logic4_requires_deploy_90_percent_vdt` |
| 2 油门杆位于反推行程 (-32° < TRA < 0°) 信号 | `reverse_travel_min_deg < tra_deg < reverse_travel_max_deg` | `(-32.0, 0.0)` deg | 同上 |
| 3 飞机处于地面状态信号 | `aircraft_on_ground == True` | - | 同上 |
| 4 发动机处于运行状态信号 | `engine_running == True` | - | 同上 |

---

## 表 5 · 阈值常数完整登记（13 常数 · docx 值 vs code 值）

| # | code 常数（`HarnessConfig` / `models.py`）| code 值 | docx § | docx 值 | 差距 | 处置 |
|---|-------------------------------------------|---------|--------|---------|------|------|
| 1 | `logic1_ra_ft_threshold` | `6.0` ft | §45 "飞机离地小于 6 ft" | 6 ft | ✅ 完全匹配 | 直接 trace |
| 2 | SW1 `near_zero_deg` | `-1.4°` | §45 "油门台角度 [-1.4°, -6.2°]" | -1.4° | ✅ 完全匹配 | 直接 trace |
| 3 | SW1 `deep_reverse_deg` | `-6.2°` | §45（同句）| -6.2° | ✅ 完全匹配 | 直接 trace |
| 4 | SW2 `near_zero_deg` | `-5.0°` | —（§9 提 SW2 但未给角度）| — | ✅ supplement §2 | **P37 supplement §2 · Kogami 内部自签 · Appendix A.1 resolved** |
| 5 | SW2 `deep_reverse_deg` | `-9.8°` | — | — | ✅ supplement §2 | 同上 |
| 6 | `logic3_tra_deg_threshold` | `-11.74°` | §51 "油门杆解析角度 ≤ -11.74°" | -11.74° | ✅ 完全匹配 | 直接 trace |
| 7 | `reverse_travel_min_deg` | `-32.0°` | §53 "反推行程 -32° < TRA < 0°" | -32° | ✅ 完全匹配 | 直接 trace |
| 8 | `reverse_travel_max_deg` | `0.0°` | §53（同句）| 0° | ✅ 完全匹配 | 直接 trace |
| 9 | `deploy_90_threshold_percent` | `90.0%` | §53 "反推完全展开" 提及但无百分比 | — | ✅ supplement §3 | **P37 supplement §3 · 行业默认 · Appendix A.2 resolved** |
| 10 | `tls_unlock_delay_s` | `0.3 s` | —（docx 提 TLS 解锁但无延迟）| — | ✅ supplement §4 | **P37 supplement §4 · simulation baseline · Appendix A.3 resolved** |
| 11 | `pls_unlock_delay_s` | `0.2 s` | — | — | ✅ supplement §4 | 同上 |
| 12 | `deploy_rate_percent_per_s` | `30.0 %/s` | —（docx 无作动速率）| — | ✅ supplement §5 | **P37 supplement §5 · simplified-plant baseline · Appendix A.4 resolved** |
| 13 | `max_n1k_deploy_limit` | per-snapshot runtime input | §51 "发动机 N1k 小于最大 N1k 展开限制" | 未印具体值 | ✅ docx 结构匹配（per-snapshot 符合"最大 N1k 展开限制"的开放语义）| 直接 trace（无硬编码常数需比对）|

**统计（P36β）：** 13 常数中 7 项 1:1 trace（+1 项 per-snapshot 结构匹配），2 项 Executor 假设，4 项 Kogami 待仲裁。

**统计（P37 更新）：** 13 常数中 7 项 1:1 docx trace（+1 项 per-snapshot 结构匹配），6 项已 resolved 到 `docs/thrust_reverser/requirements_supplement.md` §2-§5（反向补完 · Kogami 内部自签）。⚠️ 标记全部变 ✅。

---

## Appendix A · Open Assumptions Registry（6 项 · P37 supplemented 2026-04-20）

**状态更新（P37 · 2026-04-20）：** Kogami 2026-04-20 directive "以 controller.py 为准，更新补充需求文档" 已执行。6 项 Open Assumption 全部 resolved 到 `docs/thrust_reverser/requirements_supplement.md` 对应 § 段。Supplement authority = Kogami 内部自签（非外部权威 · 见 supplement §7）。

### A.1 · SW2 触发角度（镜像 SW1 pattern）— ✅ P37 SUPPLEMENTED

- **常数：** `SW2 near_zero_deg = -5.0°` · `SW2 deep_reverse_deg = -9.8°`
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §2 提供反向权威 · Kogami 内部自签接纳
- **Supplement 工程依据摘要：** SW2 [-5.0°, -9.8°] 与 SW1 [-1.4°, -6.2°] 形成两级渐进式 latching（早期解锁 → 深度反推确认）
- **External upgrade path：** 若未来 TRCU 团队 / 甲方 / 监管实测值与 code 不符，需新 Phase 升级；P37 立场作过渡期 authority

### A.2 · Deploy 90% VDT 阈值来源 — ✅ P37 SUPPLEMENTED

- **常数：** `deploy_90_threshold_percent = 90.0%`
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §3 明示 "90.0% 行业默认 VDT>90% 视为完全展开" · Kogami 内部自签
- **External upgrade path：** 若甲方/监管有更严阈值（如 95%），需新 Phase 升级 code + supplement

### A.3 · TLS/PLS 解锁延迟（0.3s / 0.2s）— ✅ P37 SUPPLEMENTED

- **常数：** `tls_unlock_delay_s = 0.3` · `pls_unlock_delay_s = 0.2`
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §4 明示 "simulation baseline · 非厂家实测" · Kogami 内部自签
- **External upgrade path：** 接入实机电时序测试报告后 · 新 Phase 升级 · simulation baseline superseded

### A.4 · Deploy Rate（30%/s）— ✅ P37 SUPPLEMENTED

- **常数：** `deploy_rate_percent_per_s = 30.0`
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §5 明示 "simplified-plant baseline" · Kogami 内部自签
- **External upgrade path：** 同 A.3

### A.5 · 故障模式（不建模）— ✅ P37 MAINTAINED

- **docx §58 原文：** "故障注入目前暂时不考虑，很复杂。"
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §6 维持 docx 立场 + 附 "未来扩展挂钩" 说明（fault model Phase 开展建议见 supplement §6.4）
- **External upgrade path：** supplement §6.4 列 fault model Phase 开展建议

### A.6 · docx 本身的 authority — ✅ P37 RESOLVED

- **docx 元数据（P36β 已登记，P37 维持）：**
  - 文件名：`控制逻辑(1).docx`
  - SHA256: `6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5`
  - 无作者 / 版本 / 签准方标注
- **Resolution (P37 · 2026-04-20):** `docs/thrust_reverser/requirements_supplement.md` §7 明示：
  - 原 docx authority = Kogami 内部来源 / 历史 snapshot
  - Supplement authority = Kogami 内部自签 · 非外部权威
  - **不冒充** 甲方 / 监管 / 行业标准
- **External upgrade path：** supplement §7.3 列 certification 升级路径（引入 TRCU 团队 / 适航局等外部签准方）

---

## 升级后状态登记（P36β 执行结果）

P35α 的 registry row 1（2026-04-20 P35α 写入）：

```
| thrust-reverser | demonstrative | Upgrade pending | Downloads/控制逻辑(1).docx（拟 P36β 入库 uploads/）| Kogami 自裁（docx 出处待 Kogami 明示）| — | P36β · 从 docx 抽需求、建 intake packet + traceability matrix |
```

P36β W5 收口更新为：

```
| thrust-reverser | certified | In use | uploads/20260409-thrust-reverser-control-logic.docx | Kogami 自裁（docx 具体签准方待 Appendix A.6 明示）| — | 已 certified · docs/thrust_reverser/traceability_matrix.md · truth lives in controller.py + yaml (no workbench spec per D1=A) · 6 Appendix A open assumptions pending sign-off |
```

**"certified" 语义明示：** 本链路已建立 docx → code → yaml 完整追溯，但并非"所有数字已被 authority 正式签准"。6 处 Open Assumption 在 Appendix A 公开登记，等未来 authority 补 sign-off。这是"诚实 certified"——有追溯有登记，但不掩盖 gap。

---

## 治理注脚

- 本 matrix 一旦更新 row（阈值值改动 / 新增常数 / docx 升级 v2），必须同 commit 原子更新 `config/hardware/thrust_reverser_hardware_v1.yaml` 头 + `src/well_harness/adapters/thrust_reverser_intake_packet.py` notes + `docs/provenance/adapter_truth_levels.md` row 1
- Appendix A 任一项 sign-off 完成，本 matrix 删除对应 ⚠️ 标记 + 升级 Open Assumptions 为 Signed Assumptions
- 本 matrix 的每次修改必须经过 Kogami 签 Gate（非 trivial rename / typo fix 除外）
- 未来 P37（若 Kogami 发）可补 `build_thrust_reverser_workbench_spec()` —— 届时 intake packet 的 business fields 由 spec 填充，本 matrix 表 4 可迁移到 LogicNodeSpec 对象里
