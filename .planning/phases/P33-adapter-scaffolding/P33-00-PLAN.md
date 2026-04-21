---
phase: P33-SUPERSEDED
plan: P33-00 (SUPERSEDED BEFORE GATE)
title: 新链路接入脚手架模板化 — SUPERSEDED by P34 (C919 E-TRAS 真实 adapter)
status: SUPERSEDED · Kogami 2026-04-20（同日二次方向修正）scope pivot to P34
superseded_by: P34-00 (C919 E-TRAS adapter 接入)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed

# SUPERSEDE 说明

本 Plan（"新链路接入脚手架模板化"）在 GATE-P33-PLAN 签字前被 Kogami 同日二次 scope pivot 作废。

Kogami 2026-04-20 后续指令：
> "本终端在你刚才开发的过程中，加入了一个新的C919 E-TRAS 控制逻辑工作台，帮我把这个新控制逻辑加入项目，要严格按照一样的模板、规格，并确保没有bug（要满足需求文档pdf）"

该指令把原 Plan Tier 1 自审里 C2 对抗项（"应先手工写第 5 个 adapter 再抽模板吗？"）的默认答案（NO）直接翻掉——改为"先手工接入第 5 条真实链路（C919 E-TRAS），对照真实需求 PDF 跑通再谈脚手架"。

## 留存记录

- 原 Plan 16KB 设计（4 条 Tier 1 反驳 / 6 sub-phases / 3 open questions）不再有效，但在未来重开脚手架 Phase 时可复用为参考。
- 配套 TaskList 条目 #23~#28（P33-00 到 P33-05）全部 deleted。
- P33 作为 Phase 编号被跳过，下一 Phase 从 P34 开始（c919-etras-adapter），与 P32 证迹补完 / P33 SUPERSEDED / P34 实战接入 三段治理证迹一致。

## 下一 Phase

- Phase: P34
- Plan 位置: .planning/phases/P34-c919-etras-adapter/P34-00-PLAN.md
- 需求输入: /sessions/zealous-sweet-gauss/mnt/uploads/23089257-...-20260417-C919反推控制逻辑需求文档.pdf（10 页）
- Gate 阻塞: GATE-P34-PLAN 待 Kogami 签

---

**Status:** SUPERSEDED (never signed, never executed)
**Successor:** P34-00 (C919 E-TRAS adapter 接入)
  - 修改现有 4 个 adapter（thrust-reverser / landing_gear / bleed_air / efds）的 truth engine
  - 修改 controller.py / 19-node / truth evaluation
  - 修改 pitch_script.md / faq.md 等立项物料
---

# P33 · 新链路接入脚手架模板化

## Why this Phase

Kogami 2026-04-20 方向修正："暂时先不要关注链路之间的联系，后续积累足够的逻辑链路之后，再考虑链路之间的联系、融会贯通。" 二级 AskUserQuestion 选择："先做新链路接入脚手架模板化"。

**为什么脚手架优先于实际新增系统：** 当前 4 个 adapter 的代码规模已表现出共性（每个都是 `GenericControllerTruthAdapter` 子类 + `system_spec` 定义 + `intake_packet` 对偶），但共性是"看起来像但未被抽象出来"的状态。新系统接入每次都要 **手工抄一遍 400-600 行样板**，这既慢（工程成本 5-7d）又有 drift 风险（每个 adapter 各抄各的，schema 漂移）。

本 Phase 把共性抽到**可生成的模板**里：给一份系统描述 YAML（系统 ID / 节点表 / 信号表 / 阈值表），scaffolding CLI 产出完整的 `{name}_adapter.py` + `{name}_intake_packet.py` + `config/hardware/{name}_hardware_v1.yaml` + `tests/test_{name}_adapter.py` 骨架 + `__init__.py` 登记。目标是让**后续任何新系统接入降到 1-2d 完成 PoC**（剩下的是把业务逻辑填到骨架里，不是写样板）。

## Scope（严格 Non-goals 已在 frontmatter）

### Scope 核心（三件套 + 证明）

1. **Adapter 模板抽取 + CLI generator**（P33-01）
   - 读 thrust-reverser / landing_gear / bleed_air / efds 四个 adapter，识别共性骨架：`ControllerTruthMetadata` 声明 / `GenericTruthEvaluation` 构造 / snapshot 值提取器 / `ControlSystemWorkbenchSpec` 组装
   - 产出 `scripts/scaffold_adapter.py` CLI：输入 `--spec system_spec.yaml`，输出 4 个新文件（adapter.py / intake_packet.py / test_adapter.py / hardware.yaml）
   - 输入 spec YAML 的 schema：system_id / nodes (list of LogicNodeSpec mini-form) / signals (list of SteadySignalSpec mini-form) / thresholds / valid_outcomes / description
   - 输出文件以 Jinja2-like placeholder 填充（不用外部依赖；pure Python `str.format_map` 或手写 string template 足够）

2. **Hardware YAML 模板 + 测试骨架模板**（P33-02）
   - `config/hardware/_template_hardware_v1.yaml`（以 `landing_gear_hardware_v1.yaml` 结构为蓝本，参数占位符化）
   - `tests/_template_test_adapter.py`（schema validation + truth invariants + adversarial placeholder）
   - CLI 在 P33-01 同时调用这两个模板

3. **Smoke-test 玩具 adapter — 证明脚手架真能跑通**（P33-03）
   - 用 scaffolding CLI 生成一个玩具系统：`cabin_temp`（2-3 个节点：`thermostat_setpoint_c` / `cabin_temp_sensor_c` / `heater_cmd`；logic：if sensor < setpoint - 2 then heater ON else OFF）
   - 不是真实航空系统，不上前端面板，不上 adversarial live lane，只验证生成的代码能 import / 能通过 `test_{cabin_temp}_adapter.py` 基础 schema 测试
   - 目的：**证明 P33-01/02 的模板真能产出可跑代码**，而不是"理论上好用但实际生成的代码要人工改 50 行才能跑"

4. **使用文档**（P33-04 一部分）
   - `docs/engineering/adding-a-new-adapter.md`：1-page workflow "从 spec YAML 到可 demo 的新系统 adapter 在 1-2d 内完成"
   - 包含 pitch_script 语境下的"如果甲方要加一个新系统怎么办"FAQ answer（但**不改 faq.md 本身**，只给甲方审查时可引的一张图）

### Sub-phase 分解（P33-00 至 P33-05）

| Sub | 交付物 | 触碰面 | 工期 | Gate |
|-----|--------|--------|------|------|
| P33-00 | 本 Plan doc | `.planning/phases/P33-adapter-scaffolding/` | 0.5d | **GATE-P33-PLAN (Kogami)** — 本文 |
| P33-01 | scaffolding CLI + adapter template | `scripts/scaffold_adapter.py`（新）+ `templates/adapter/*.tmpl`（新）+ `tests/test_scaffold_adapter.py`（新） | 1.5d | Executor 子阶段自验 |
| P33-02 | hardware YAML + test 模板 | `config/hardware/_template_hardware_v1.yaml`（新）+ `tests/_template_test_adapter.py`（新） | 0.5d | Executor 子阶段自验 |
| P33-03 | Smoke-test 玩具 adapter `cabin_temp` | `src/well_harness/adapters/cabin_temp_adapter.py`（生成）+ `tests/test_cabin_temp_adapter.py`（生成） | 0.5d | Executor 子阶段自验（生成代码必须通过基础 schema 测试） |
| P33-04 | 三轨回归 + 使用文档 | `docs/engineering/adding-a-new-adapter.md`（新）+ 三轨测试 fresh 真跑 | 0.5d | Executor 子阶段自验（三轨零回归门） |
| P33-05 | Closure + Notion DECISION + ROADMAP | `.planning/phases/P33-adapter-scaffolding/P33-05-CLOSURE.md`（新）+ `.planning/ROADMAP.md` + Notion 控制塔 | 0.5d | **GATE-P33-CLOSURE (Kogami)** |

**总工期预估：** 3-4 工作日（"先下基础"定价；比原作废的 Deep Federation 5-7d 轻）。

## Exit Criteria（可证伪）

1. `scripts/scaffold_adapter.py --spec <yaml>` 可从命令行调用，给任意合法 spec YAML 产出 4 个新文件且语法合法（`python -c "import x"` 通过）。
2. 模板覆盖：adapter 主体 / intake packet / hardware YAML / test skeleton 四文件类别全部有模板且能生成。
3. Smoke-test toy adapter `cabin_temp` 从 scaffolding 生成后：a) pytest `tests/test_cabin_temp_adapter.py` 通过（schema validation 层）；b) 在 `src/well_harness/adapters/__init__.py` 登记并 importable；c) 在 `list_controller_adapters()` 或等价 API 调用中可见。
4. `docs/engineering/adding-a-new-adapter.md` 存在，含 "1-2d workflow"，内部 CI 不做死链校验（纯文档）。
5. **三轨回归** 相对 P32 基线（pytest 684/1skip / e2e 49 / adversarial 8/8）：default lane 可增 scaffolding + cabin_temp 相关测试（预计 +5~10 测试）但零回归；e2e lane 零增零回归（纯后端脚手架不动前端）；adversarial lane 零增零回归（不动真值引擎不动 prompt）。
6. P33 commit author/trailer 符合 v5.2：`Claude App Opus 4.7 <opus47-claudeapp-solo@local>` + trailer `Execution-by: opus47-claudeapp-solo · v5.2`。
7. Notion 控制塔 `## P33 DECISION · v5.2 solo-signed (YYYY-MM-DD) · 新链路接入脚手架模板化` 段含完整 Sub-phase 证据 + Tier 1 adversarial 摘录 + 三轨 fresh 数据 + 工具使用示例（1 行命令 + 输出路径列表）。

## Counterargument Pre-check（v5.2 R3 · Tier 1 adversarial self-review · ≥3 反驳）

### C1 · 生成的代码可能"看起来能跑但实际有隐蔽 bug"——模板掩盖而非抽象

**反论：** 把 4 个 adapter 的共性抽到模板里，假设了共性是"对"的。但 4 个 adapter 本身可能各有局部 smells：比如 bleed_air_adapter 用了 `hysteresis` 但 landing_gear 没用，efds 的 fault_modes 结构和 thrust-reverser 不完全一致。模板如果强行统一会丢掉真实差异；如果保留所有分支的 opt-in 开关，模板本身会变得和"抄一遍"一样复杂。结果可能是：**生成了大量"语法正确但语义 half-baked"的代码**，反而让后续新系统接入者多花时间去 debug 生成物，而不是省时间。

**就地反驳：** 部分接受——Plan 有三层防护：
1. **模板刻意做"最小共性"而不是"并集"**：只抽所有 4 个 adapter 都共享的结构（metadata / truth evaluation / snapshot extractors / spec 组装 skeleton），**不**抽任何一个独有的 feature。独有的 feature（e.g. bleed_air 的 hysteresis）留给接入者手动加。
2. **Smoke-test toy adapter cabin_temp 必须跑通** — 这是 P33-03 的硬 exit criteria。如果模板产出的代码 cabin_temp 都跑不起来，说明模板本身错了，不发布。
3. **使用文档 explicitly 写"生成后一般还要手工补 15-40 行业务逻辑"**—— 不承诺"零手工"。诚实定价：脚手架省的是样板（~300-400 行每 adapter），不省业务逻辑（~50-100 行）。

### C2 · P33 是否应该先走一遍"手工新增第 5 个 adapter"，再抽模板？

**反论：** Kogami 选的是"先做脚手架 → 后续再多接系统"。但工程实践里，"抽象 of N 个样本" 通常在 N=3+1 时才稳定（前 4 个是样本，第 5 个是验证）。如果 P33 只从 4 样本抽，没有第 5 个验证目标，模板可能被设计成"适合过去 4 个但下一个进来就不合"。

**就地反驳：** 驳回——这正是 P33-03 smoke-test toy adapter 的作用：cabin_temp 是**模板的首个"新接入"验证**，相当于在脚手架发布前先走一遍完整产出→跑通流程。cabin_temp 故意设计得和 thrust-reverser/landing_gear/bleed_air/efds 都不一样（只有 2-3 个节点 / 逻辑极简 / 无 fault modes / 无复杂 spec），**如果 cabin_temp 能从 scaffolding 跑通，说明模板 covers 的共性范围合理**。如果 cabin_temp 跑不通，Plan 授权 Executor stop for Kogami（触发 v5.2 R4）并给出降级路径（只发布 adapter + intake 模板，yaml 和 test 模板留 P34）。

### C3 · scaffolding 会不会成为"永远没人用"的 infrastructure over-engineering？

**反论：** 脚手架是给**未来新系统接入**用的，但"未来新系统"本身还没被 Kogami 批准开。如果 P34 / P35 一直不碰新 adapter，P33 产出的 scaffolding 就是纯 overhead（代码库里多了一个没人用的工具，维护成本 > 收益）。

**就地反驳：** 部分接受——P33 的真实价值依赖 Kogami 后续确实批 "新增 adapter" 的 Phase。如果未来 6 个月没批，P33 的回报率是负的。但：
1. **Kogami 的方向指令明示"积累逻辑链路"**——这意味着新增 adapter 是可预期的后续方向之一。
2. **P33 本身成本低**（3-4d）——即使未来不批新 adapter，沉没成本可接受。
3. **使用文档 `adding-a-new-adapter.md`** 对立项汇报有直接价值：即使 scaffolding 本身没人调用，文档本身回答了甲方问题"加一套你们没见过的新系统要多久"——从"抄 500 行 5d" 变成 "填 spec YAML + 补业务逻辑 1-2d"。pitch 叙事价值 > 工具使用价值。

### C4 · scaffolding 生成代码的维护责任归谁？模板更新后存量 adapter 是否要反向同步？

**反论：** 模板升级（e.g. 加一个新的通用 helper）后，4 个存量 adapter 不会自动得到这个 helper。时间久了，"模板产出的第 5/6/7 个 adapter"和"存量 4 个"会 drift：新生的按模板 N 规范，老的按"当年手写的风格"，久之成为两套混用。

**就地反驳：** 接受——Plan 明示此为 known limitation：
1. **scaffolding 不做反向同步**。模板升级只影响未来生成；存量 adapter 保持手写态。
2. **使用文档 explicit 说明**："if 你要把模板升级应用到存量 adapter，是独立的 refactoring 工作，非 scaffolding 责任"。
3. **留 open question Q2**（本 Plan 下方）：Kogami 是否希望 P33 包含"把存量 4 个 adapter 也按模板重写一遍"？默认答案 NO（非 P33 scope）。

## 合规 checklist（Plan 阶段 · Closure 时再次复审）

- ✅ **R1 不可逆 main HEAD** — P33 commits 落 feat/p33-adapter-scaffolding 分支；FF merge 等 GATE-P33-CLOSURE
- ✅ **R2 不自签 Gate** — GATE-P33-PLAN 本文 + GATE-P33-CLOSURE P33-05 都等 Kogami
- ✅ **R3 Tier 1 adversarial self-review** — 本 Plan §Counterargument Pre-check 有 4 条反驳 + 就地反驳（超 ≥3 条要求）
- ✅ **R4 不自选下一 Phase 方向** — P33 (v2) scope 是 Kogami 2026-04-20 两轮 AskUserQuestion 明示选中（作废 Federation → 选"积累链路" → 选"先做脚手架"）
- ✅ **R5 证迹先行** — P33 本身是能力层（非证迹层），但**使用文档 `adding-a-new-adapter.md` 作为工程证迹**在 P33-04 与代码同期落盘
- ✅ **8 条绝对边界** — 逐条对照：controller.py 真值 (#1) / AI 不替代 truth (#2) / Canvas 只听 truth (#3) / cross_domain 注册表 (#4) / 冻结期不开新功能 (#8 已 lifted 但治理 footprint 低) 均不动；GSD 自动化回归保护 (#6) 通过三轨 zero-regress 维持
- ✅ **Three-track 零回归** — exit criteria #5 明示，P33-04 fresh 真跑门

## 开口问题（供 Kogami 在 Plan Gate 时一并裁决）

- **Q1 · smoke-test toy adapter 的选择：** 默认 `cabin_temp`（客舱温度简易恒温器，2-3 节点，非真实飞控系统）。你是否偏好：A. `cabin_temp`（默认，刻意非飞控避免 pitch 上被问到细节）/ B. 某个真实但简化的飞控系统（如 APU start simplified, 但会多 0.5-1d 因为要对齐真实信号命名）/ C. Executor 自裁。
- **Q2 · 存量 4 adapter 是否随模板重写：** 默认 NO（非 P33 scope，保持 refactoring 独立）。你是否希望：A. NO（默认，保持范围最小）/ B. YES（把存量 4 个也按模板重写，工期 +2-3d，回归风险略升）/ C. 部分 YES（比如只重写最简单的 efds 做对照实验）。
- **Q3 · CLI 调用形式：** 默认 `python scripts/scaffold_adapter.py --spec spec.yaml --outdir src/well_harness/adapters/`。你是否偏好：A. CLI（默认，与 GSD automation 兼容）/ B. 交互式 prompts（cookiecutter 风格，对新人更友好）/ C. 两者都做（CLI 主，interactive 包装，工期 +0.5d）。

## Estimated cost

- 工期：3-4 工作日
- Solo Executor 独立执行；GATE-P33-PLAN + GATE-P33-CLOSURE 等 Kogami 签
- 风险点：C1（模板掩盖差异）+ C2（smoke-test 未通过）构成主要不确定性；两者都有 stop-for-Kogami 兜底

## Scope 初审（Executor pre-review，非 Gate 批准）

本 Plan 自审：Non-goals 显式 + Exit Criteria 可证伪（7 条）+ Tier 1 对抗自审 4 条 + R1-R5 合规 6/6 + 8 条绝对边界对照 + 三轨零回归门 + 3 个 Plan 阶段开口问题。按 v5.2 Solo Mode 规则，**P33-00 本身即 stop point**，等 GATE-P33-PLAN: Approved 后启动 P33-01 模板抽取。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P33-PLAN: Approved`（Kogami）
