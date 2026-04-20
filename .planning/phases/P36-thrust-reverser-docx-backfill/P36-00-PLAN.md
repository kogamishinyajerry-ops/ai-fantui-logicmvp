---
phase: P36
plan: P36-00
title: β · thrust-reverser docx 真实化 — demonstrative → certified 升级（证迹补完第二轮 β 段）
status: drafted · Awaiting GATE-P36β-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P35-CLOSURE Approved (Kogami 2026-04-20) → origin/main at aabc548
  - Kogami 2026-04-20 "Go P36β" 指令 (follow-up to D · 证迹补完第二轮)
  - Kogami 2026-04-20 D1=A 精益 / D2=C 混合 / D3=Kogami 自裁 / D4=只登记 Appendix A (固化)
  - V1 自我修正: controller.py 4 个 logic 组 (logic1/2/3/4) 与 docx 4 工作逻辑条件数对齐
    (logic1 4 vs docx 3 · code 多 sw1 DIU 触发; logic2/3/4 各 5/6/4 完全 1:1)
  - D4-B docx outline 已扫 (57 段 + 2 表 + 1 图 + 4 工作逻辑 + 段 58 明示"故障不考虑")
  - docx 源文件: /Users/Zhuanz/Downloads/控制逻辑(1).docx (230,930 bytes)
non-goals:
  - 改 src/well_harness/controller.py 任何逻辑或条件数
  - 改 src/well_harness/models.py HarnessConfig 任何常数数值
  - 改 config/hardware/thrust_reverser_hardware_v1.yaml 任何数字（仅头部加 docx § 引用注释）
  - 改 tests/test_controller*.py 任何断言
  - 改 P35 registry 除 row 1 (thrust-reverser) 外任何行
  - 为 thrust_reverser 建 build_thrust_reverser_workbench_spec() 函数（D1=A 精益，仅建最小 intake packet）
  - 改 P34 / P35 任何文件（registry row 1 除外）
  - 建故障模式 spec 或 test（docx 段 58 明示"故障注入目前暂时不考虑，很复杂"，P36β 维持这个现状）
  - 添加 runtime warning / API 感知层 / 前端 badge（D4=只登记 Appendix A）
  - 改 demo_server / static / 既有 demo 流程
---

# P36-00 Plan · β · thrust-reverser docx 真实化 — demonstrative → certified 升级

## 0. TL;DR

按 Kogami 2026-04-20 "Go P36β" 指令 + D1-D4 四项固化，P36β 把 `Downloads/控制逻辑(1).docx` 作为 `controller.py` / `models.py` / `thrust_reverser_hardware_v1.yaml` 的**追溯性权威上游**入库、建 intake packet（精益版，3 SourceDocumentRef 完整、business fields 空）、补 hardware YAML docx § 引用注释、建 `docs/thrust_reverser/traceability_matrix.md`、升级 P35 registry row 1 从 `demonstrative + Upgrade pending` → `certified + In use`。

**不改 controller.py 一行代码、不改 models.py 一个常数、不改任何 test 断言**。纯证迹升级，预计 4h 内收口。

**规模估算：**
- W1 uploads/ 新增 docx (225KB)
- W2 新增 `thrust_reverser_intake_packet.py` ≈100 行（精益）
- W3 hardware YAML 头注释 +20 行
- W4 新增 `docs/thrust_reverser/traceability_matrix.md` ≈160-200 行
- W5 closure + ROADMAP + STATE + registry 升级（row 1 只改）+ Notion DECISION
- **总新增 ≈1000-1200 行 · 0 code behavior change · 0 test assertion change · 0 threshold number change**

---

## 1. 上下文

### 1.1 V1 已自修正（关键）

P36β outline 起草时（2026-04-20 14:xx）我报过一个 V1 "docx 工作逻辑 3 与 controller.py 实现不对齐"的顾虑。P36β Plan 起草前（2026-04-20 17:xx）精确对账 `src/well_harness/controller.py` 1-183 行发现：

| 组 | docx 条件数 | code 条件数 | 对账结论 |
|----|------------|------------|---------|
| logic1 | 3 (radio<6ft · not inhibited · not deployed) | 4 (+ sw1) | code 多 sw1 DIU 内部触发 · docx 段 45 描述但未纳入"工作逻辑 1"显式 list · **层次差异，不是冲突** |
| logic2 | 5 (engine · ground · not inhibited · sw2 · eec) | 5 | ✅ 完全 1:1 |
| logic3 | 6 (engine · ground · not inhibited · tls unlocked · n1k<max · tra≤-11.74°) | 6 | ✅ 完全 1:1 |
| logic4 | 4 (deployed · tra in (-32,0) · ground · engine) | 4 | ✅ 完全 1:1 |

**结论：** docx 与 code 没有真实冲突。P36β matrix 大多数行可直接 1:1 trace。

### 1.2 docx 覆盖 vs code 的 5 个未覆盖常数（D2=C 固化后的处置）

| 常数 | code 值 | docx 覆盖 | D2=C 处置 |
|------|---------|-----------|-----------|
| `SW1 near_zero_deg` | -1.4 | ✅ 段 45 | 直接 trace · 无 Open Question |
| `SW1 deep_reverse_deg` | -6.2 | ✅ 段 45 | 直接 trace · 无 Open Question |
| `SW2 near_zero_deg` | -5.0 | ❌（段 9 提 SW2 但未给角度）| **Executor 假设 · 镜像 SW1 pattern · 登 Appendix A** |
| `SW2 deep_reverse_deg` | -9.8 | ❌ 同上 | 同上 |
| `logic1_ra_ft_threshold` | 6.0 | ✅ 段 45 "小于 6ft" | 直接 trace |
| `logic3_tra_deg_threshold` | -11.74 | ✅ 段 51 | 直接 trace |
| `reverse_travel_min_deg` | -32.0 | ✅ 段 53 | 直接 trace |
| `reverse_travel_max_deg` | 0.0 | ✅ 段 53 | 直接 trace |
| `deploy_90_threshold_percent` | 90.0 | ❌（段 53 "反推完全展开"无百分比）| **Kogami 自裁（来源未明）· 登 Appendix A** |
| `tls_unlock_delay_s` | 0.3 | ❌（docx 无延迟表述）| **Kogami 自裁 · 登 Appendix A** |
| `pls_unlock_delay_s` | 0.2 | ❌ | 同上 |
| `deploy_rate_percent_per_s` | 30.0 | ❌（docx 无作动速率）| **Kogami 自裁 · 登 Appendix A** |

共 4 个 Kogami 待决数字（deploy_90 · tls_delay · pls_delay · deploy_rate）+ 2 个 Executor 假设镜像（SW2）。

### 1.3 P35 registry row 1 升级目标

P35α 在 registry 登：

```
| thrust-reverser | demonstrative | Upgrade pending | Downloads/控制逻辑(1).docx (拟 P36β 入库 uploads/) | Kogami 自裁 | — | P36β · 从 docx 抽需求、建 intake packet + traceability matrix |
```

P36β W5 收口改为：

```
| thrust-reverser | certified | In use | uploads/20260409-thrust-reverser-control-logic.docx | Kogami 自裁（docx 出处待 Kogami 明示签准方）| — | 已 certified · docs/thrust_reverser/traceability_matrix.md · truth lives in controller.py + yaml (no workbench spec per D1=A) |
```

**不改 row 1 以外任何行**（non-goal）。

---

## 2. Scope — 5 工作包

### W1 · docx 入库 + 校验（P36β-01）

- `mkdir -p uploads/`（当前不存在，同步建立 convention · P34 PDF 也可以未来入）
- `cp /Users/Zhuanz/Downloads/控制逻辑(1).docx uploads/20260409-thrust-reverser-control-logic.docx`
- 计算 `shasum -a 256` · 记录 SHA256 / size / paragraphs / tables / media 元数据到 commit message 和 intake packet 注释
- `git add uploads/20260409-thrust-reverser-control-logic.docx`
- 单 commit: `feat(P36β-01): thrust-reverser requirement docx landed in uploads/`

### W2 · Intake packet 精益版（P36β-02）

- 新建 `src/well_harness/adapters/thrust_reverser_intake_packet.py` ≈100 行（参考 `c919_etras_intake_packet.py` pattern，精益变种）
- 实现 `build_thrust_reverser_intake_packet() -> ControlSystemIntakePacket`
  - `system_id = "thrust-reverser"`
  - `title = "Thrust Reverser Deploy Controller"`
  - `objective = ...`
  - `source_of_truth = "src/well_harness/controller.py"`
  - `source_documents = (<3 refs 下列>)`
  - `components = ()`（精益：无 ComponentSpec · D1=A）
  - `logic_nodes = ()`（精益：无 LogicNodeSpec · truth 在 controller.py DeployController class · Q1-Q4 在 matrix 里 trace）
  - `acceptance_scenarios = ()`（精益）
  - `fault_modes = ()`（docx 段 58 "不考虑"）
  - `knowledge_capture` = minimal 默认
  - `clarification_answers = ()`
  - `tags = (...)`
- 3 个 SourceDocumentRef：
  1. `kind="python-controller"` · `location="src/well_harness/controller.py"` · `role="truth_source"` · notes 引用 DeployController + logic1/2/3/4
  2. `kind="docx"` · `location="uploads/20260409-thrust-reverser-control-logic.docx"` · `role="requirement_reference"` · notes 含 SHA256 + "57 段 / 2 表 / 4 工作逻辑" + 引用 P36-04 matrix
  3. `kind="yaml"` · `location="config/hardware/thrust_reverser_hardware_v1.yaml"` · `role="hardware_spec"` · notes "13 常数 cross-verified with docx · 4 常数 Kogami 待仲裁登 Appendix A · 2 常数 Executor 假设镜像"
- `src/well_harness/adapters/__init__.py` 加 3 行注册（import build_thrust_reverser_intake_packet · 加公共 symbol）
- **不**建 `build_thrust_reverser_workbench_spec()` · **不**用标准 `intake_packet_to_workbench_spec` 转换（D1=A 精益：truth 继续在 controller.py 原生，不进 workbench spec pipeline）
- 单 commit: `feat(P36β-02): thrust-reverser intake packet (lean · 3 SourceDocumentRef · no workbench spec per D1=A)`

### W3 · Hardware YAML 头部 docx § 引用（P36β-03）

修 `config/hardware/thrust_reverser_hardware_v1.yaml` 头注释段（当前头部已有 "Source: HarnessConfig defaults (src/well_harness/models.py)" 和 "Value sources (models.py lines 22-43)" 段）—— 在这些段**之后**加新段：

```
# docx provenance (2026-04-09 upload):
# ==================================================================================
# Source:     uploads/20260409-thrust-reverser-control-logic.docx
# SHA256:     <calculated at W1>
# Size:       230930 bytes · Paragraphs: 57 · Tables: 2 · Media: 1 (EMF)
# Upstream:   Kogami 自裁（docx 出处/签准方待 Kogami 明示）
#
# Threshold → docx § map:
#   logic1_ra_ft_threshold = 6.0           → docx 段 45 "飞机离地小于 6ft"
#   SW1 near_zero_deg = -1.4               → docx 段 45 "油门台角度 [-1.4°, -6.2°]"
#   SW1 deep_reverse_deg = -6.2            → 同上
#   SW2 near_zero_deg = -5.0               → docx 无 · Executor 假设 · 镜像 SW1 pattern · Appendix A
#   SW2 deep_reverse_deg = -9.8            → 同上 · Appendix A
#   logic3_tra_deg_threshold = -11.74      → docx 段 51 "油门杆解析角度 ≤ -11.74°"
#   reverse_travel_min_deg = -32.0         → docx 段 53 "反推行程 -32° < TRA < 0°"
#   reverse_travel_max_deg = 0.0           → 同上
#   deploy_90_threshold_percent = 90.0     → docx 无 · Kogami 待仲裁 · Appendix A
#   tls_unlock_delay_s = 0.3               → docx 无 · Kogami 待仲裁 · Appendix A
#   pls_unlock_delay_s = 0.2               → docx 无 · Kogami 待仲裁 · Appendix A
#   deploy_rate_percent_per_s = 30.0       → docx 无 · Kogami 待仲裁 · Appendix A
# See docs/thrust_reverser/traceability_matrix.md for full Appendix A and sign-off TODOs.
```

**不改**任何 YAML value（`parameters:` 段下全部不动）。仅头部加注释。

单 commit: `docs(P36β-03): thrust-reverser hardware YAML anchored to docx sections`

### W4 · Traceability matrix（P36β-04）

新建 `docs/thrust_reverser/traceability_matrix.md`（参照 P34 `docs/c919_etras/traceability_matrix.md` 格式，5 表 + Appendix A）：

- **表 1 · 部件映射**（docx 表 1 · 反推系统 11 部件 + docx 表 2 · 5 交联设备 → `HarnessConfig` / code 字段映射）
- **表 2 · 输入信号映射**（docx 段 9-16 · 8 项 → code `ResolvedInputs` fields）
- **表 3 · 输出信号映射**（docx 段 19-23 · 5 项 + 段 26-40 · 15 监测信号 → `ControllerOutputs` fields）
- **表 4 · 4 工作逻辑映射**
  - 工作逻辑 1 (docx 段 47) → `controller.py:26-49` (logic1_conditions, 4 条件 含 sw1 DIU)
  - 工作逻辑 2 (docx 段 49) → `controller.py:50-68` (logic2_conditions, 5 条件)
  - 工作逻辑 3 (docx 段 51) → `controller.py:69-106` (logic3_conditions, 6 条件)
  - 工作逻辑 4 (docx 段 53) → `controller.py:107-130` (logic4_conditions, 4 条件)
  - 每行含：docx 条件 · code 条件 · 单测 (tests/test_controller.py 函数名)
- **表 5 · 阈值常数完整登记**（13 常数 · 表头 `code 常数 / code 值 / docx § / docx 值 / 差距 / 处置`）
  - ✅ 7 常数 1:1 (radio 6ft / SW1 ×2 / TRA -11.74° / travel -32°/0°)
  - ⏳ 4 常数 Kogami 仲裁（deploy_90 / tls_delay / pls_delay / deploy_rate）→ Appendix A
  - ⏳ 2 常数 Executor 假设（SW2 ×2）→ Appendix A
- **Appendix A · Open Assumptions Registry (待 Kogami sign-off)**
  - A.1 SW2 触发角度 -5.0°/-9.8° · Executor 假设镜像 SW1 pattern · 建议 Kogami 确认或给实际值
  - A.2 Deploy 90% VDT 阈值 · Kogami 待仲裁（行业常识？甲方规定？）
  - A.3 TLS/PLS 解锁延迟 0.3s/0.2s · Kogami 待仲裁
  - A.4 Deploy rate 30%/s · Kogami 待仲裁
  - A.5 故障模式 docx 段 58 明示"不考虑，很复杂" · P36β 维持 · 未来 Phase 补时重开
  - A.6 docx 本身的 authority（作者/版本/签准方）· Kogami 明示

单 commit: `docs(P36β-04): thrust-reverser traceability matrix (5 tables + Appendix A, 6 open assumptions)`

### W5 · 收口（P36β-05）

- 三轨回归（期望：default 762 identical · e2e 49 identical · adversarial 1 identical —— P36β 不加测试，零 delta）
- `docs/provenance/adapter_truth_levels.md` row 1 升级（demonstrative → certified · Upgrade pending → In use · upstream_source 改入库路径 · notes 加 "truth lives in controller.py + yaml; no workbench spec (D1=A lean)"）
- `.planning/ROADMAP.md` 追加 Phase P36β 段
- `.planning/STATE.md` 更新 Current Position 到 P36β
- 新建 `.planning/phases/P36-thrust-reverser-docx-backfill/P36-05-CLOSURE.md`
- Notion DECISION append（Pending 状态，等 `GATE-P36β-CLOSURE: Approved` 后 flip）
- 单 commit: `docs(P36β-05): closure — awaiting GATE-P36β-CLOSURE`

---

## 3. Non-goals — 严格禁止

已在 frontmatter `non-goals` 全列。强调：
- **不**改 `controller.py` 一行代码
- **不**改 `models.py` 任何 HarnessConfig 常数
- **不**改 YAML 的任何 `parameters:` 段 value（仅加头注释）
- **不**改任何既有测试
- **不**建 workbench spec（D1=A）
- **不**建故障模式（docx 明示不考虑）
- **不**加 runtime warning（D4）
- **不**改 P35 registry 其他 4 行（仅 row 1）
- **不**改 P34 / demo_server / static / 前端

---

## 4. Tier 1 对抗性自审（≥3 条，交付 5 条）

### C1 · "W2 精益模式下 thrust_reverser 升级到 'certified' 语义不严谨 —— 没有 workbench spec，algorithms 没经过标准 pipeline 验证"

**承认部分有效。** 缓解：
1. registry row 1 notes 字段**显式**写 `truth lives in controller.py + yaml; no workbench spec (D1=A lean)` —— 下游查 registry 时立即知道这条 `certified` 不走 workbench pipeline
2. thrust_reverser 已有 `tests/test_controller.py` 315 LOC 覆盖，+ `test_controller_adapter.py` 127 LOC + `test_controller_truth_adapter_metadata_schema.py` 93 LOC · 合计 535 LOC 测试 · pytest 绿就代表 controller.py 行为稳定
3. W4 matrix 表 4 把 4 组 logic 条件逐条 trace 到 docx 工作逻辑 → 建立 docx 与 code 的可审计映射
4. P37（若未来 Kogami 发 directive）可独立补 workbench spec，不破坏 P36β 的 certified level

### C2 · "docx 被未来改动/替换后，intake packet SHA 校验不对 —— 但项目没有 CI SHA 校验，等于没保护"

**承认 gap 真实。** 缓解：
1. W1 固化 SHA256 到 commit message + intake packet notes + YAML 头 + matrix Appendix A 四个独立位置，任一处发现 docx SHA 不匹配都能察觉
2. CI 自动校验 docx SHA 超出 P36β scope（独立小 Phase · 拟 P38 · CI-level provenance hash enforcement · 如果 Kogami 未来发 directive）
3. 当前 4 位 SHA 副本 + repo 的 uploads/ 入库本身 = 防护够 layering

### C3 · "Q1-Q4 Executor 假设 / Kogami 待仲裁项被审计方视为证迹漏洞"

**承认 gap 真实。** 缓解：
1. Appendix A 显式**用英文+中文双语**登记每个 Open Assumption · 不是"看起来正常"而是"明示未决"
2. `status: certified + In use` 的 registry 含义：**已建立追溯链路**，不等于"所有数字都被 authority 签准"——registry notes 字段加"6 open assumptions in Appendix A pending authority sign-off"
3. 未来 authority sign-off 走一个轻量 Phase 更新 Appendix A + registry notes，不需要重开 certification

### C4 · "code 有 docx 没覆盖的常数 = code 实际领先 docx —— docx 不是真正的上游权威"

**承认事实。** 缓解：
1. Matrix 表 5 如实记录 "code has authority beyond docx in 6 places"
2. Appendix A.6 请 Kogami 明示 docx 的 authority 级别（是完整权威？还是"前期需求文档，工程实现有补充"？）
3. registry row 1 `authority: Kogami 自裁` 字段本身就是对这一事实的承认 —— 不假装甲方签准整份 code，而是承认最终签准权在 Kogami 手里
4. 真实项目里这种情况很常见（code 演化快于 spec），matrix 透明化此 gap 比粉饰强

### C5 · "thrust_reverser YAML 头有 'Do NOT modify controller.py even if these values differ from simulator needs' —— P36β 是不是违反这个 freeze rule？"

**不违反。** 缓解：
1. P36β **没改** controller.py 一行（non-goal 首条）
2. P36β **没改** YAML 任何 `parameters:` value（non-goal 第 3 条）
3. 只加 YAML 头注释，注释本身不影响 controller.py / simulator 行为
4. Freeze rule 明说 "Do NOT modify controller.py" —— 纯 docs 增补不在此列
5. W5 closure doc 明列 "controller.py / models.py / YAML parameters 字节级不变" invariant · git diff 可验证

---

## 5. Open Questions — 必须 Kogami 仲裁（GATE-P36β-PLAN 签时）

**Q1 · SW2 触发角度（Executor 假设镜像 SW1）**
- **A** · 接受 `SW2 near_zero=-5.0°, deep_reverse=-9.8°` 为 Executor 假设，登 Appendix A.1，注 "docx 无 · 镜像 SW1 pattern · 待 TRCU / 甲方 sign-off"
- **B** · Kogami 给实际值
- **Executor 建议：A**

**Q2 · Deploy 90% VDT 阈值来源**
- **A** · Kogami 自裁 / 未明确 · 登 Appendix A.2 待未来 sign-off
- **B** · 行业常识（"VDT > 90% 视为完全展开"）· 登 Appendix A.2 但标 "行业默认"
- **C** · 你给甲方出处 / 规定引用
- **Executor 建议：B**（明确行业默认 + 待 Kogami 补实际来源）

**Q3 · TLS/PLS 解锁延迟 0.3s / 0.2s 来源**
- **A** · Kogami 自裁 · 登 Appendix A.3 · 注 "docx 无 · 待 sign-off"
- **B** · 你给实际来源
- **Executor 建议：A**

**Q4 · Deploy rate 30%/s 来源**
- **A** · Kogami 自裁 · 登 Appendix A.4
- **B** · 你给实际来源
- **Executor 建议：A**

**Q5 · docx 本身的 authority（影响 intake packet SourceDocumentRef.role + registry row 1 authority 字段）**
- **A** · `Kogami 自裁`（P36β 起草时已按此默认）· docx 出处、作者、版本、签准方都是你的判断
- **B** · 具体组织（TRCU / 飞机制造商 / 适航局 / 其他）—— 请写出
- **Executor 建议：A**（符合 D3 已定）

---

## 6. Sub-phase 分解

### P36β-01 · W1 docx 入库（约 20 min）
- mkdir uploads/ · cp · shasum · git add · commit
- 验证：`ls -la uploads/` 看到 docx · `shasum -a 256 uploads/*.docx` 得到 hash · commit message 记录
- 风险：macOS `cp` 可能保留 xattr · 用 `-X` 或 `ditto` 剥 xattr（如遇 git warning）

### P36β-02 · W2 intake packet 精益版（约 45 min）
- 写 `src/well_harness/adapters/thrust_reverser_intake_packet.py`（参照 c919 pattern）
- 写 `src/well_harness/adapters/__init__.py` 注册（+3 行）
- 本地跑 `PYTHONPATH=src python -c "from well_harness.adapters.thrust_reverser_intake_packet import build_thrust_reverser_intake_packet; p = build_thrust_reverser_intake_packet(); print(p.system_id, len(p.source_documents))"` 验证
- 跑 `pytest tests/test_adapter_freeze_banner.py` 确认 P35-03 不误报（thrust_reverser 不在 frozen 列表 · 应无变化）
- 风险：__init__.py 新增可能触发 ImportError 循环 · 精心 import order

### P36β-03 · W3 YAML 头注释（约 20 min）
- Edit `config/hardware/thrust_reverser_hardware_v1.yaml` 头注释段
- 验证：`head -50 config/hardware/thrust_reverser_hardware_v1.yaml` 视觉检查 · `python -c "import yaml; yaml.safe_load(open('config/hardware/thrust_reverser_hardware_v1.yaml'))"` 确认 parse 正常
- 风险：YAML 注释格式若破坏 parse 则破窗

### P36β-04 · W4 traceability matrix（约 1.5-2h）
- 写 `docs/thrust_reverser/traceability_matrix.md`
- 5 表 + Appendix A 6 项
- 风险：条目漏、行号偏差 → 每行对照 controller.py / docx / yaml 精确 grep 确认

### P36β-05 · W5 收口（约 1h）
- 三轨回归（期望零 delta）
- registry row 1 升级 1 行 in-place edit
- ROADMAP / STATE 更新
- Closure doc
- Notion DECISION append（Pending）
- push branch
- 风险：registry row 1 edit 碰巧触发 P35-03 banner test（thrust_reverser 不在 frozen 列表，不应触发 · 提前检查）

---

## 7. Exit Criteria

- `uploads/20260409-thrust-reverser-control-logic.docx` 入库 · SHA256 记录 ≥4 位置
- `src/well_harness/adapters/thrust_reverser_intake_packet.py` 新建 · 3 SourceDocumentRef 完整 · 空 business fields (精益)
- `config/hardware/thrust_reverser_hardware_v1.yaml` 头注释 +docx § 引用 · parameters 字节级不变
- `docs/thrust_reverser/traceability_matrix.md` 新建 · 5 表 + Appendix A 6 项
- `docs/provenance/adapter_truth_levels.md` row 1 升级 demonstrative→certified · 其余 4 行字节级不变
- Three-lane: default 762 / e2e 49 / adversarial 1 identical to P35 baseline · 零 delta
- Closure doc 起草 · 等 `GATE-P36β-CLOSURE: Approved`
- Notion DECISION append（Pending）
- Branch `codex/p36-thrust-reverser-docx-backfill` 6 commits pushed (P36β-00 plan + 01..05 = 6 commits)

---

## 8. 风险与回滚

| 风险 | 概率 | 影响 | 缓解/回滚 |
|------|------|------|----------|
| docx 打开失败（加密/受损）| 低 | 阻塞 | W1 前先 zipfile.ZipFile 再试一次 · 失败则 STOP 报 Kogami |
| controller.py 实际条件数与 §1.1 对账不符 | 极低 | 阻塞 matrix W4 | 逐行 grep 确认 · 已在 P36β outline 阶段精确对账，概率极低 |
| Appendix A 6 项有漏 | 低 | 中 | matrix 写完回扫 models.py 逐个 HarnessConfig 字段核对 |
| registry row 1 升级触发 P35-03 banner test | 极低 | 小 | test 只检 3 demonstrative 系统 + c919 matrix; thrust_reverser 不在监控列表 |
| P36β-05 三轨有 delta | 低 | 中 | P36β 不加测试不改代码，delta 说明意外污染 · 回退 commit 排查 |
| docx 路径含中文括号 `(1)` 在 git add 时编码问题 | 低 | 小 | W1 rename 到 ASCII 路径 `20260409-thrust-reverser-control-logic.docx` 已规避 |

**回滚策略：** 如果 `GATE-P36β-CLOSURE` 不批，`git revert` 回到 `aabc548` main HEAD 即可。P36β branch 保留作审计存证。

---

## 9. v5.2 红线合规预声明（plan 级）

- **R1 不可逆 main HEAD** — P36β commit 全走 `codex/p36-thrust-reverser-docx-backfill` 独立分支；non-FF merge (Option M) 到 main 等 `GATE-P36β-CLOSURE: Approved` 后由 Executor 执行，保 SHA
- **R2 不自签 Gate** — P36β-00 等 Kogami `GATE-P36β-PLAN: Approved`（含 Q1-Q5 仲裁）；P36β-05 等 `GATE-P36β-CLOSURE: Approved`
- **R3 Tier 1 adversarial** — §4 已写 5 条反驳（C1-C5）+ 就地缓解
- **R4 不自选下一 Phase 方向** — P36β 由 Kogami 2026-04-20 "Go" 明示发起；下一 Phase 方向（P37 workbench spec / 其他）由 Kogami 在 P36β closeout 后再次明示
- **R5 证迹先行** — 本 Phase 本身是证迹先行第二轮的 β 段；docx 入库 + matrix + Appendix A 6 项明示未决是"诚实证迹"不是"装齐"

---

## 10. 停点

**本 plan 不执行任何动作。等 `GATE-P36β-PLAN: Approved` + Q1-Q5 逐条仲裁。**

收到签字后 Executor：

1. 从 `main` (aabc548) 派生 `codex/p36-thrust-reverser-docx-backfill`
2. 按 P36β-01..05 顺序执行，每 sub-phase 1 commit（含 P36β-00 plan 共 6 commits）
3. 三轨跑完 · 零 delta 预期 → 起草 P36β-05-CLOSURE.md · push 分支
4. 等 `GATE-P36β-CLOSURE: Approved`
5. non-FF merge main（Option M · SHA 保留）→ push origin main → Notion flip → 删本地 merged 分支 → 回报 Kogami
6. 等 Kogami 明示下一方向（P37 workbench spec? P38 CI SHA 校验? 或其他）

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P36β-PLAN: Approved` (Kogami) + Q1/Q2/Q3/Q4/Q5 仲裁
