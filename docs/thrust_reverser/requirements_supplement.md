# Thrust Reverser Requirements Supplement (反向需求增补)

**Phase:** P37 · v5.2 solo-signed · 2026-04-20
**Authority:** Kogami 内部自签（非甲方 / 非监管 / 非行业标准 —— 见 §7）
**Gate:** `GATE-P37-PLAN: Approved` Kogami 2026-04-20（Q1=A Markdown · Q2=A authority 一并解决）
**Status:** 本 supplement 是对 `uploads/20260409-thrust-reverser-control-logic.docx`（以下简称"原 docx"）的反向补完（code-to-spec backfill）。原 docx 保留为 2026-04-09 历史 snapshot 不变。

---

## §1 · 导言与范围

### 1.1 性质与反向生成过程

**本文档是反向真值化产物（ex-post facto spec）**：

Well Harness 项目的 thrust-reverser 控制逻辑已在 `src/well_harness/controller.py::DeployController` + `src/well_harness/models.py::HarnessConfig` 中实现完备并经 535 LOC 测试覆盖。原 docx（2026-04-09 · 57 段 · 2 表 · 1 图）覆盖了其中 4 个核心工作逻辑的条件列表和 4 个阈值常数，但未覆盖以下 5 处硬件参数 + 1 处 authority 声明。

P36β 建立 traceability matrix 时将这 6 处标记为 Appendix A Open Assumption 等 sign-off。Kogami 2026-04-20 明示："之前的 controller 以及完备了，可能你丢失了需求文档的全文" —— 从而将问题从"code 超前于 spec"重新定位为"spec 是 code 的不完整投影"。

本 supplement 的目的：**以 `controller.py` + `models.py` 的现有稳定实现为权威真值基准**，反向补完原 docx 缺的 6 项内容。

### 1.2 范围

本 supplement 覆盖：
- §2 · SW2 触发角度（补 Appendix A.1）
- §3 · Deploy 90% VDT 阈值（补 Appendix A.2）
- §4 · TLS/PLS 解锁延迟（补 Appendix A.3）
- §5 · 反推作动速率（补 Appendix A.4）
- §6 · 故障模式立场（补 Appendix A.5）
- §7 · Authority 定义（补 Appendix A.6）
- §8 · 与原 docx 和 code 的 3 方关系

本 supplement **不改** `controller.py` / `models.py` / YAML 任何 value ——它只是**给既有稳定实现加一层可读的 spec 皮肤**。

### 1.4 P41 Discovery 注（2026-04-20）

P41 起草时发现一个 P36β 时期未被识别到的事实：

**`src/well_harness/system_spec.py::current_reference_workbench_spec()` 早已提供完整 thrust-reverser workbench spec**（含 ComponentSpec / LogicNodeSpec / AcceptanceScenarioSpec · 被 6 处引用：`cli.py` / `controller_adapter.py::ReferenceDeployControllerAdapter.load_spec()` / `tests/test_system_spec.py` / 等）。

这意味着 P36β 决定的 "D1=A Lean (no workbench spec per D1=A)" 口径的**真实语义**是：
- **不是** "thrust-reverser 无 workbench spec"
- **而是** "`thrust_reverser_intake_packet.py` 层面选择不 populate business fields · 因为 intake packet 是后加的 bridge"

P41 scope C（Kogami 2026-04-20 "Go C"）：仅做**纯文档澄清** + **最简 intake regression test**。不改 `current_reference_workbench_spec()`、不改 `thrust_reverser_intake_packet.py` business fields、不 rename existing spec（破 6 处 callers 稳定性）。

### 1.3 适用与不适用场景

**适用：**
- Well Harness 项目内部控制逻辑验证
- GSD 证迹链 / Phase closeout audit
- 工程协作锚点（新人 onboarding / cross-team ref）
- controller.py 的行为说明书

**不适用：**
- 航空适航认证（需外部 TRCU / 适航局 authority）
- 对外客户交付（需甲方签准版）
- 法规合规声明（需监管签准）
- 非 Well Harness 语境复用

若未来需上述 scope，需独立 Phase 升级 authority（见 §7）。

---

## §2 · SW2 触发角度（补 Appendix A.1）

### 2.1 原 docx 覆盖状态

原 docx §9 提及 "油门台的开关信号 SW1 和 SW2 开关信号（0/1）"，明示 SW2 的存在但**未给触发角度**。相比之下 §45 明示 SW1 触发于 `[-1.4°, -6.2°]`。

### 2.2 Code 权威值

`src/well_harness/models.py::HarnessConfig` 第 22-43 行的 SW2 触发窗口常数：

| 常数 | 值 | 单位 |
|------|-----|------|
| `sw2_near_zero_deg` | `-5.0` | ° |
| `sw2_deep_reverse_deg` | `-9.8` | ° |

### 2.3 工程依据

SW2 触发窗口与 SW1 采取**相似结构但不同刻度**的 pattern：
- SW1 `[-1.4°, -6.2°]`：油门杆**早期反推意图识别**（DIU 控制 TLS 解锁继电器闭合）
- SW2 `[-5.0°, -9.8°]`：油门杆**深度反推意图确认**（参与 logic2 FADEC 反推许可）

两窗口**互相错开但重叠**的设计（SW2 near_zero -5.0 在 SW1 的 deep_reverse -6.2 附近），形成两级渐进式 latching：飞行员渐推油门杆进反推区 → 先过 SW1 near_zero 解锁 TLS → 再过 SW2 near_zero 开 logic2 → 最终过 SW1 / SW2 deep_reverse 满足 logic3 / logic4。

### 2.4 Supplement 签准

Kogami 2026-04-20 接纳 code 值 `SW2 [-5.0°, -9.8°]` 为**权威值**。

---

## §3 · Deploy 90% VDT 阈值（补 Appendix A.2）

### 3.1 原 docx 覆盖状态

原 docx §53 "反推完全展开信号" 提及概念但**未印具体百分比阈值**。

### 3.2 Code 权威值

`HarnessConfig.deploy_90_threshold_percent = 90.0`（单位 `%`）。

在 `controller.py:109-113` 中 `logic4_conditions` 的第 1 条：
```python
_condition(
    "deploy_90_percent_vdt",
    inputs.deploy_90_percent_vdt,
    "==",
    True,
    inputs.deploy_90_percent_vdt,
)
```
—— `inputs.deploy_90_percent_vdt` 是 ResolvedInputs 阶段已布尔化后的信号（VDT 原始位移 > 90% 视为 True）。

### 3.3 工程依据

"VDT > 90% 视为完全展开" 是**反推系统工程实践常识**：
- 90% 是反推系统厂家常用 "deploy complete" 阈值（VDT 位移达机械行程 90% 时作动筒已充分展开）
- 留 10% 余量给机械公差 / 液压响应 / 温度漂移
- 低于 90% 视为 "still deploying" · 100% 视为 "mechanical limit"

### 3.4 Supplement 签准

Kogami 2026-04-20 接纳 `deploy_90_threshold_percent = 90.0%` 为**权威值**。未来若甲方或监管有更严阈值（如 95%），需单独 Phase 升级。

---

## §4 · TLS/PLS 解锁延迟（补 Appendix A.3）

### 4.1 原 docx 覆盖状态

原 docx §3-§4 提及 TLS/PLS 作为传感器/供电信号，**未提任何解锁时序延迟**。

### 4.2 Code 权威值

`HarnessConfig` 解锁延迟常数：

| 常数 | 值 | 单位 | 含义 |
|------|-----|------|------|
| `tls_unlock_delay_s` | `0.3` | s | TLS 从 "115VAC 接通" 到 "ls 传感器报已解锁" 的典型延迟 |
| `pls_unlock_delay_s` | `0.2` | s | PLS 从 "供电接通" 到 "ls 传感器报已解锁" 的典型延迟 |

### 4.3 工程依据

电磁锁解锁时序 baseline：
- TLS 是单点机电锁（线圈通电 → 弹簧释放 → 锁芯后退）· 典型响应 200-400 ms
- PLS 是 4 点并列锁（4 PLS 同步）· 典型响应 150-250 ms
- 0.3s / 0.2s 是项目演示/仿真用的**代表性 baseline**，不是任何具体厂家产品的实测

### 4.4 Supplement 签准

Kogami 2026-04-20 接纳 `tls_unlock_delay_s = 0.3` / `pls_unlock_delay_s = 0.2` 为**权威值**（simulation baseline · 非厂家实测）。

---

## §5 · 反推作动速率（补 Appendix A.4）

### 5.1 原 docx 覆盖状态

原 docx 无任何作动速率描述。

### 5.2 Code 权威值

`HarnessConfig.deploy_rate_percent_per_s = 30.0`（单位 `%/s`）。

在仿真侧用于 simplified plant 的作动筒位移速率模型（`0 → 100%` 耗时约 `3.3s`）。

### 5.3 工程依据

反推系统整体 deploy 时间工程 baseline：
- 大型民航反推系统典型全展开时间 2-4 秒
- 30 %/s → 3.3s 全程 · 落在区间中段
- 简化模型（线性速率），不建模液压升压曲线 / 温度影响

### 5.4 Supplement 签准

Kogami 2026-04-20 接纳 `deploy_rate_percent_per_s = 30.0` 为**权威值**（simplified-plant baseline）。

---

## §6 · 故障模式立场（补 Appendix A.5）

### 6.1 原 docx 覆盖状态

原 docx §58 明示："故障注入目前暂时不考虑，很复杂。"

### 6.2 P36β 立场

P36β 严格按原 docx §58 维持：
- 不建 `FaultModeSpec` 对象
- 不加故障注入测试
- intake packet `fault_modes = ()` 保留空

### 6.3 P37 立场

**维持 P36β 立场。** 本 supplement §6 不扩展故障模型。

### 6.4 未来扩展挂钩

若未来开故障模型 Phase（拟名 P-F · Fault Model Phase），建议：
1. 先明确 fault taxonomy（参考 `src/well_harness/fault_taxonomy.py`）
2. 从最常见的 3-4 种 fault mode 开始（电气中断 / 机械卡阻 / 传感器失效 / 液压失压）
3. 每个 FaultModeSpec 需要 `target_component_id` + `fault_kind` + `expected_diagnostic_sections`
4. 对接 Well Harness 的 knowledge capture pipeline · 让 fault 可作为 demo 的可演示场景

### 6.5 Supplement 签准

Kogami 2026-04-20 接纳 "P37 维持 P36β 不建故障模型" 为**当前权威立场**。

---

## §7 · Authority 定义（补 Appendix A.6）

### 7.1 Supplement 本身的 Authority

**Authority level:** Kogami 内部自签
**Signing party:** Kogami（2026-04-20, v5.2 Solo Mode 项目所有人）
**NOT:**
- 甲方 / 主机厂 / 航空制造商
- 民航监管机构 / 适航局
- 行业标准组织（RTCA / SAE / ARINC / ...）
- 外部 TRCU 厂家 / 供应商

### 7.2 原 docx（`uploads/20260409-thrust-reverser-control-logic.docx`）的 Authority

**Authority level:** Kogami 内部自签 / 历史 snapshot
**Metadata 已知部分：**
- 文件名：`控制逻辑(1).docx`（原名有 `(1)` 后缀，可能是 Downloads 自动重命名）
- SHA256：`6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5`
- 230,930 bytes · 57 段 · 2 表 · 1 EMF 图 · 无 Word Heading styles
**Metadata 未知部分：**
- 作者署名（docx properties 未录）
- 版本号 / 日期戳 / 修订记录
- 签准方标注

Kogami 2026-04-20 **接纳** 原 docx 为 "Kogami 内部来源控制逻辑需求文档" · **不冒充**任何外部 authority。

### 7.3 升级路径

若未来 Well Harness 需要 certification-grade authority：
1. **引入外部签准方**（主机厂航电工程团队 / 适航代表 / 第三方认证机构）
2. **重新审查** controller.py + supplement + 原 docx 的每一项
3. **签准文件** 替代本 supplement 作为 authority source
4. **registry** row 1 authority 字段升级（当前 "Kogami 内部自签" → 明确外部签准方）
5. **traceability matrix** Appendix A 每项改为"已外部 sign-off by X on YYYY-MM-DD"
6. 本 supplement 保留为历史过渡期文档 · 或标记 "Superseded by external certification"

### 7.4 Supplement 签准

Kogami 2026-04-20 接纳上述 authority 定义 + 升级路径。

---

## §8 · 与原 docx / code / workbench spec 的 4 方关系 (P41 updated 2026-04-20)

### 8.1 四方角色

| 角色 | 文件 | Authority 级别 | 变更门槛 |
|------|------|---------------|---------|
| **真值基准** | `src/well_harness/controller.py` + `models.py` | 代码真值 · 唯一 ground truth | 改动需新 Phase + 三轨回归 |
| **历史 snapshot** | `uploads/20260409-thrust-reverser-control-logic.docx` | Kogami 内部来源 · 截面式 | 冻结 · 不改动 |
| **反向补完** | `docs/thrust_reverser/requirements_supplement.md`（本文档）| Kogami 内部自签 · 对 code 的 snapshot 式 spec 皮肤 | 跟 code 同步修订（code 改了此文档也改）|
| **Workbench spec (P41 discovered)** | `src/well_harness/system_spec.py::current_reference_workbench_spec()`（约 280 行）| 派生于 controller.py + HarnessConfig · ComponentSpec/LogicNodeSpec/AcceptanceScenarioSpec | 跟 code 同步 · 6 处 callers 依赖稳定 |

### 8.2 冲突消解规则

如任何三者之间出现冲突：
1. **Code wins** · `controller.py` + `HarnessConfig` 是真值
2. 原 docx 若描述与 code 不一致 → 以 code 为准 · 原 docx 保留原貌不改
3. 本 supplement 若描述与 code 不一致 → 修本 supplement（bug in supplement, not in code）

### 8.3 维护策略

- Code 改动 → 必须同步更新 supplement + traceability matrix + YAML 头
- 原 docx 冻结 → 除非发现错别字 / 结构破损 · 否则不动
- Supplement 修订 → 小修 markdown diff commit；大修走 Phase

### 8.4 审计路径

任何人审计 thrust-reverser 真值路径时应按如下顺序读：
1. `docs/provenance/adapter_truth_levels.md` row 1（definitive registry · 当前 level 和 status）
2. `docs/thrust_reverser/traceability_matrix.md`（5 表 + Appendix A · 完整追溯）
3. 本 supplement（spec 层可读说明）
4. `src/well_harness/adapters/thrust_reverser_intake_packet.py`（4 SourceDocumentRef · 证迹挂链）
5. `config/hardware/thrust_reverser_hardware_v1.yaml`（硬件常数 · YAML 头 docx / supplement 引用）
6. `src/well_harness/controller.py` + `models.py`（最终真值 · 代码即 law）

---

## 附：术语

- **SW1 / SW2**：油门台（Throttle Quadrant）微动开关，分别对应反推意图的 early-detection 和 deep-confirm 两级
- **TLS** (Third-tier Locking System)：第三锁定系统 · 反推解锁时序的第三环节
- **PLS** (Primary Locking System)：主锁定系统 · 4 点并列
- **VDT** (Variable Displacement Transducer)：位移传感器 · 连续值 · 触发"反推完全展开"信号依赖其阈值化
- **TRA** (Throttle Resolver Angle)：油门杆解析角度 · 连续值 · 反推方向 TRA < 0°
- **N1k**：发动机低压转子相对转速 · 反推展开许可条件之一
- **DIU**：数字接口单元 · 油门台信号处理
- **EICU**：发动机接口控制单元 · 540VDC 控制
- **EEC**：发动机电子控制 · 展开/收起指令源
- **ETRAC**：电子反推作动控制器 · 代码层由 `DeployController` 代表
- **PDU**：功率驱动单元 · 反推运动执行端
- **RPDU**：分配电源单元 · 115VAC 供电源

---

**Signed:** Kogami 2026-04-20（v5.2 Solo Mode project owner · 内部自签 authority）
**Maintained by:** Claude App Opus 4.7 (Solo Executor) under `GATE-P37-PLAN: Approved`
**Sync with code:** 本 supplement 任何数值变更必须与 `src/well_harness/models.py::HarnessConfig` 同 commit 原子更新
