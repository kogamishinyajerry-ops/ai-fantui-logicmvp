---
phase: P35
plan: P35-00
title: Adapter Truth-Level Registry + Demonstrative Adapters Freeze Banner — 证迹补完第二轮 α 段
status: drafted · Awaiting GATE-P35-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P34-CLOSURE Approved (Kogami 2026-04-20) → origin/main at c88e4f0
  - P31-GATE Approved (Kogami 2026-04-20)
  - GATE-P32-CLOSURE Approved (Kogami 2026-04-20)
  - Kogami 2026-04-20 方向指令: D · 证迹补完第二轮
  - D1=B 拆分 P35α (W1+W2) / P36β (W3+W4+W5)
  - D2=C docx 入库（留给 P36β 执行时落地）
  - D3=A 串联（P31/P32/P34 先签 → 已全部完成到 origin/main）
  - D4=B docx outline 先审（outline 已发 Kogami 2026-04-20）
  - D5=5 counterargument（§4 交付 5 条）
  - Kogami 2026-04-20 口径: bleed_air/efds/landing_gear 3 adapter "是随便生成的逻辑面板，没有需求文档，当作没来源，冻结搁置，不影响继续开发"
non-goals:
  - 改 3 demonstrative adapter 任何行为 / 阈值 / 测试断言 / hardware YAML 数字
  - 新增 3 demonstrative adapter 的 intake packet / hardware YAML（冻结就冻结，不新增）
  - 改 P34 c919_etras adapter / thrust_reverser (controller.py) / models.py
  - 改 ControllerTruthMetadata schema 或 JSON schema（留给独立未来 Phase）
  - 真实化 thrust_reverser（属 P36β）
  - 替 Kogami 升级任何 adapter 的 truth_level（registry 内容由 Kogami 签准后落地）
  - runtime API surface 暴露 truth_level（留给独立未来 Phase）
---

# P35-00 Plan · Adapter Truth-Level Registry + Demonstrative Adapters Freeze Banner

## 0. TL;DR

Kogami 2026-04-20 明示：bleed_air / efds / landing_gear 三个既有 adapter"是我之前尝试随便生成的逻辑面板，我自己也没有明确的需求文档——当作没有需求来源，把它们先冻结搁置即可，不影响继续开发"。

P35α 按 D1=B 拆分做证迹补完第二轮的 α 段：**纯文档层** truth-level 登记 + 3 adapter 的 docstring/YAML 头部冻结 banner。**零代码行为改动，零测试断言改动，零 hardware YAML 数字改动**。半天收口。

**规模估算：**
- W1: 1 新 markdown (`docs/provenance/adapter_truth_levels.md`) · ~80 行
- W2: 7 个既有文件加 banner（3 adapter + 2 intake + 2 yaml）· 各 ≤15 行注释/docstring 增补
- W3: 1 新测试（assert banner 存在）· ~50 行
- W4: ROADMAP + STATE + closure + Notion DECISION · ~90 行
- 预计 3-5 小时（半个 Executor 工作日）

---

## 1. 上下文（Q2=B 扫描事实 + Kogami 口径）

Q2=B 扫描（2026-04-20）产出 5-adapter gap 表，核心事实：

| # | 真值系统 | 上游规格来源 | 证迹完整度 | adapter 自述词 |
|---|---------|------------|-----------|----------------|
| 1 | thrust_reverser (controller.py) | `Downloads/控制逻辑(1).docx`（Kogami 2026-04-20 披露）| YAML cites code; 无 docx 锚；P36β 真实化 | "reflects only the confirmed logic" |
| 2 | bleed_air | **none** (Kogami 2026-04-20) | 自指 SourceDocumentRef；YAML 只有 phase tag；0 dedicated tests | "Simplified environmental control system adapter" |
| 3 | efds | **none** | 0 intake / 0 yaml / 0 matrix / 0 dedicated tests | "Emergency Flare Deployment System ..." |
| 4 | landing_gear | **none** | 自指 SourceDocumentRef；YAML 只有 phase tag；611 LOC tests 但自证 | "Minimal ... to prove adapter-only runtime generalization" |
| 5 | c919_etras (P34) | `uploads/20260417-C919反推控制逻辑需求文档.pdf` + 甲方 C919 TRCU 团队 | ✅ P34 完成，153 行 matrix + 3 SourceDocumentRef + Q1-A/Q2-A/Q3-A 仲裁 | 完整锚 PDF |

P35α 的任务是**把"2/3/4 号没有需求来源"这一事实显式登记**，并在 adapter/YAML 头部加 banner，确保下游复用（演示 / 对外文档 / 客户材料 / 学习材料）不会把它们误引用为可信证迹。

---

## 2. Scope — 两个工作包 + 测试 + 收口

### W1 · 新增 `docs/provenance/adapter_truth_levels.md`

**文件布局：** 标题 + 背景 + schema 描述 + 1 张 5 行表 + upgrade path 说明 + 治理注脚。

**表 schema：**

| 列 | 含义 |
|---|---|
| `system_id` | adapter 的 metadata `system_id`（与代码常量严格一致）|
| `truth_level` | enum: `certified` / `demonstrative` / `placeholder` |
| `status` | enum: `In use` / `Frozen` / `Upgrade pending` / `Upgrade in progress` |
| `upstream_source` | 具体路径或 `none` |
| `authority` | 签准方（甲方团队名 / Kogami / 无）|
| `frozen_as_of` | YYYY-MM-DD 或 `—` |
| `upgrade_path` | 一句话说明如何从当前 level 升 certified |
| `notes` | 引用对应 Phase 号（P34 等）|

**5 行初始数据（由 Kogami 签准）：**

| system_id | truth_level | status | upstream_source | authority | frozen_as_of | upgrade_path |
|-----------|-------------|--------|-----------------|-----------|-------------|--------------|
| `thrust-reverser` | `demonstrative` | `Upgrade pending` | `Downloads/控制逻辑(1).docx`（拟 P36β 入库 `uploads/`） | Kogami 自裁（docx 出处待 Kogami 明示）| — | P36β · 从 docx 抽需求、建 intake packet + traceability matrix |
| `bleed-air-valve` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 未来 Kogami 提供上游规格后开新 Phase |
| `emergency_flare_deployment_system` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 同上 |
| `minimal_landing_gear_extension` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 同上 |
| `c919-etras` | `certified` | `In use` | `uploads/20260417-C919反推控制逻辑需求文档.pdf` | 甲方 (C919 TRCU 团队) | — | 已 certified |

### W2 · 3 adapter freeze banner 落地

每个冻结 adapter 的关联文件加 banner。7 文件清单：

| 文件 | 注入位置 |
|------|---------|
| `src/well_harness/adapters/bleed_air_adapter.py` | module-level docstring 追加段 |
| `src/well_harness/adapters/bleed_air_intake_packet.py` | module-level docstring 追加段 |
| `config/hardware/bleed_air_hardware_v1.yaml` | head comment 追加段 |
| `src/well_harness/adapters/efds_adapter.py` | module-level docstring（当前无 docstring，新增）|
| `src/well_harness/adapters/landing_gear_adapter.py` | module-level docstring（当前无，新增）|
| `src/well_harness/adapters/landing_gear_intake_packet.py` | module-level docstring 追加段 |
| `config/hardware/landing_gear_hardware_v1.yaml` | head comment 追加段 |

banner 文字见 §6 草案（待 Kogami 逐字批）。

### W3 · 新增 `tests/test_adapter_freeze_banner.py`

- 断言 3 个 adapter module docstring 含关键字 `FROZEN` + `no authoritative upstream spec`
- 断言 2 个 intake packet docstring 含同样关键字
- 断言 2 个 yaml 头部含同样关键字
- 共 7 个断言，单个 test class，~50 行
- 作用：防回归 —— 如果未来有人删 banner，CI 立刻红

### W4 · 收口物料

- `.planning/ROADMAP.md` 追加 P35 段
- `.planning/STATE.md` 更新（若存在 "current phase" 字段）
- `.planning/phases/P35-adapter-truth-level-registry/P35-05-CLOSURE.md` 新建
- Notion 控制塔 page `33cc68942bed8136b5c9f9ba5b4b44ec` append P35 DECISION block（Pending 状态，等 `GATE-P35-CLOSURE: Approved` 后由 Executor flip）

---

## 3. Non-goals — 严格禁止

已在 frontmatter `non-goals` 列出。强调：
- **不** 改 3 demonstrative adapter 任何行为 / 阈值 / 测试 / YAML 数字
- **不** 新增 3 demonstrative adapter 的 intake packet / hardware YAML（efds 没有 intake 也不补）
- **不** 改 P34 / thrust_reverser / controller.py / models.py
- **不** 改 `ControllerTruthMetadata` 或 JSON schema
- **不** 暴露 truth_level 到 runtime API / demo_server

---

## 4. Tier 1 对抗性自审（≥3 条，交付 5 条）

### C1 · "banner 是纯注释，1 年后会被遗忘或意外删掉，等于没写"

**承认有效性。** 缓解：W3 断言测试。CI 每次默认 lane 都检查 banner 关键字存在。删 banner → 测试立刻红。+ W1 registry 文件在 docs/provenance 下，成为独立可引用的证迹源，不依赖 docstring 存活。

### C2 · "banner + registry 是纯 docs 兜底，demo_server / api / 前端没感知，用户在 demo 场景仍可能误读"

**承认 gap 真实。** 但超出 P35α scope（non-goal 已明列）。本 Phase 只做 docs 层冻结；runtime 层升级（例如 adapter registry API 返回 truth_level、前端加 level badge、demo 页加 disclaimer banner）留给未来独立 Phase（拟名 P37 · Truth-Level Runtime Surface，等 Kogami 决定是否发）。P35α 的 docs 层 banner + registry 是**必要但非充分**防护，作为未来 runtime 防护的锚点。

### C3 · "'冻结搁置'语义模糊 —— 3 adapter 还能被 api / demo 调用吗？还是必须 404？"

**明示定义：** "冻结" = 不新增真实化证迹 + 不新增测试断言 + 不改行为数字。现有 smoke 测试和 API 暴露**保持运行**（demo 依赖它们，违反 P34 non-goal 亦违反 Kogami 明说"不影响继续开发"）。banner 只在 docstring / yaml 头部**叙述性**告诉 human reader"别把这当真证迹用"。

### C4 · "P36β 真实化 thrust_reverser 的时间顺序 —— 若 P36β 先执行 P35α 后执行怎么办？"

**处理：** W1 registry 的 thrust_reverser 行默认写 `truth_level: demonstrative` + `status: Upgrade pending`。P36β 收口时 Executor 改这一行到 `truth_level: certified` + `status: In use`（属 P36β 内的收口动作之一）。若 Kogami 要颠倒顺序（先 P36β 后 P35α），P35α 起草时 thrust_reverser 行就直接写 `certified`。

### C5 · "W2 banner 文字需要 Kogami 逐字审吗？"

**是，必须。** Banner 是对外声明，影响所有 downstream 复用者（包括未来新员工 onboarding、外部学习材料、潜在客户演示）。GATE-P35-PLAN 时 Kogami 必须明示 banner 文案可接受或指定修订。本 plan §6 附完整草案供审。

---

## 5. Open Questions — 必须 Kogami 仲裁

### Q1 · truth_level enum 命名
- **A** · `demonstrative` / `certified` / `placeholder`（强调本质）
- **B** · `frozen` / `active` / `placeholder`（强调当前状态）
- **C** · `demonstrative` / `certified` / `placeholder` + 独立 `status` 字段（`In use` / `Frozen` / `Upgrade pending`）表达状态——两维度分离
- **Executor 建议：C**（本质与状态分离；例如"demonstrative-active"也可表达；W1 schema 已按 C 设计）

### Q2 · banner 存放位置
- **A** · 每个 adapter module docstring + YAML head comment（W2 当前草案）
- **B** · 每个 adapter 同目录加独立 `FROZEN.md` 文件
- **C** · A + B 双保险
- **Executor 建议：A**（docstring 随代码走，`help()` / IDE tooltip 即时显示；独立 .md 容易被忽视；W1 registry 已经是独立文件，banner 是它的触手）

### Q3 · efds 无 intake/yaml 是否顺便补 stub？
- **A** · 顺便补 stub intake packet + stub yaml（头部直接 banner，主体空），提升资产对称性
- **B** · 不补，维持现状
- **Executor 建议：B**（Kogami 口径"冻结搁置不影响继续开发"→"不新增"精神。efds 没有 intake/yaml 这件事本身就是 demonstrative 的标志，反而是证迹）

### Q4 · thrust_reverser 在 registry 的初始 truth_level（P35α 起草时，P36β 未执行）
- **A** · `demonstrative` + `status: Upgrade pending`（诚实现实；P36β 收口时升级）
- **B** · 先不列 thrust_reverser，P36β 起草时再加行
- **Executor 建议：A**（5-adapter 全列，审计清晰；P36β 只需 in-place 改 1 行，便于 diff review）

### Q5 · banner 文字内容（逐字审 §6 草案）
- **A** · 接受 §6 草案
- **B** · 要求修订（请 Kogami 给出具体修订词）

---

## 6. banner 文字草案（供 Kogami 逐字审）

### Python adapter module docstring 追加版（bleed_air / efds / landing_gear adapter 文件）

```
FROZEN (2026-04-20) — demonstrative adapter, no authoritative upstream spec.

Status: frozen per Kogami 2026-04-20 directive. This adapter was built for
capability demonstration (runtime adapter generalization proof), NOT from an
authoritative requirement document. Its thresholds, logic nodes, timing
constants, and test assertions are illustrative and MUST NOT be cited as
truth in certification, testing, external documentation, or customer-facing
material.

See docs/provenance/adapter_truth_levels.md for the registry and upgrade path.
```

### Intake packet docstring 追加版（bleed_air / landing_gear intake 文件）

```
FROZEN (2026-04-20) — demonstrative intake packet, no authoritative upstream spec.

This packet's SourceDocumentRef points to the adapter file itself (self-reference)
because no authoritative upstream document exists. Do not cite this packet as
audit truth. See docs/provenance/adapter_truth_levels.md.
```

### Hardware YAML head comment 追加版（bleed_air / landing_gear yaml 文件）

```
# FROZEN (2026-04-20) — demonstrative hardware parameters, no authoritative upstream spec
# =========================================================================
# Status: frozen per Kogami 2026-04-20 directive. These parameters were built
# for capability demonstration, NOT from an authoritative requirement source.
# MUST NOT be cited as truth in certification, testing, external docs, or
# customer-facing material. See docs/provenance/adapter_truth_levels.md.
# =========================================================================
```

---

## 7. Sub-phase 分解

### P35-01 · W1 registry doc（约 30 分钟）
- 新建 `docs/provenance/` 目录
- 写 `adapter_truth_levels.md`（标题 + 背景 + schema + 5 行表 + upgrade path + 治理注脚）
- 单 commit：`docs(P35-01): adapter truth-level registry (5 rows)`

### P35-02 · W2 banner 落地（约 1 小时）
- 按 §2 W2 文件清单 7 文件逐一加 banner
- 单 commit：`docs(P35-02): freeze banner on 3 demonstrative adapters (7 files)`

### P35-03 · W3 banner 断言测试（约 30 分钟）
- 新建 `tests/test_adapter_freeze_banner.py`
- 本地跑 `pytest tests/test_adapter_freeze_banner.py -v`
- 单 commit：`test(P35-03): adapter freeze banner regression guard`

### P35-04 · 三轨回归（约 20 分钟）
- default: `PYTHONPATH=src python -m pytest tests/ --tb=no -q` · 期望 750+ passed（747 + ≥3 new）
- e2e: `PYTHONPATH=src python -m pytest tests/ -m e2e --tb=no -q` · 期望 49 identical
- adversarial: `WELL_HARNESS_PORT=8799 python src/well_harness/static/adversarial_test.py` · 期望 8/8
- 结果贴 Closure doc，不单独 commit

### P35-05 · Closure + ROADMAP + STATE + Notion DECISION（约 1 小时）
- 新建 `.planning/phases/P35-adapter-truth-level-registry/P35-05-CLOSURE.md`
- 更新 `.planning/ROADMAP.md` + `.planning/STATE.md`
- Append Notion DECISION block（Pending 状态）
- 单 commit：`docs(P35-05): closure — awaiting GATE-P35-CLOSURE`
- 然后 push 分支 → 等 Kogami 签 `GATE-P35-CLOSURE: Approved` → non-FF merge main（Option M 同 P34）→ Notion flip → 回报

---

## 8. Exit Criteria

- `docs/provenance/adapter_truth_levels.md` 存在，含 5 行表 + schema 描述
- 7 文件 banner 落，文字与 §6（或 Kogami 修订后版本）一致
- `tests/test_adapter_freeze_banner.py` 通过
- default pytest ≥750 passed / 1 skipped / 49 deselected · 无既有回归
- e2e 49 identical · adversarial 8/8
- ROADMAP / STATE 更新
- Closure doc 起草 · 等 `GATE-P35-CLOSURE: Approved`
- Notion DECISION 块 append（Pending 状态）
- Plan + W1-W5 共 5 个 commits in `codex/p35-adapter-truth-level-registry` branch, pushed

---

## 9. 风险与回滚

| 风险 | 概率 | 影响 | 缓解/回滚 |
|------|------|------|----------|
| banner 文字被 Kogami 要求大改 | 中 | 小 | §6 草案单独签；只改 banner 文字一处 |
| W3 测试写法与其他 test suite 冲突 | 低 | 小 | 独立 file · module docstring 断言是纯字符串匹配 |
| `docs/provenance/` 目录无 existing convention | 低 | 小 | 单文件，不污染其他 docs subdir |
| Q2=B 扫描漏了某个 demonstrative adapter | 低 | 中 | 5 adapter 已穷举：bleed_air / efds / landing_gear / c919_etras / thrust_reverser (controller.py) —— 4 demonstrative（含 thrust_reverser pending）+ 1 certified（c919_etras），无遗漏 |
| 将来 runtime API 要暴露 truth_level，docs 层格式不便迁移 | 低 | 小 | W1 schema 已设计为结构化表格（可 parse 成 YAML），将来 runtime 层可把 docs 表迁移到 `config/truth_levels.yaml` |

**回滚：** `GATE-P35-CLOSURE` 不批时，`git revert` 回到 `c88e4f0` main HEAD 即可。P35 branch 保留作审计存证。

---

## 10. v5.2 红线合规预声明（plan 级）

- **R1 不可逆 main HEAD** — P35 commit 全走 `codex/p35-adapter-truth-level-registry` 独立分支；main merge 等 `GATE-P35-CLOSURE: Approved`，走 Option M non-FF merge（同 P34）保 SHA
- **R2 不自签 Gate** — P35-00 等 Kogami `GATE-P35-PLAN: Approved`（含 Q1-Q5 仲裁）；P35-05 等 `GATE-P35-CLOSURE: Approved`
- **R3 Tier 1 adversarial** — §4 已写 5 条反驳（C1-C5）+ 就地缓解
- **R4 不自选下一 Phase 方向** — P35 由 Kogami 2026-04-20 "D · 证迹补完第二轮" 明示指令发起；下一 Phase（P36β thrust_reverser 真实化）方向由 Kogami 在 P35 closeout 后 **再次明示**（避免 P35α 进展导致方向 drift）
- **R5 证迹先行** — 本 Phase 本身就是"证迹先行"的第二轮；3 adapter 无 upstream source 是 Kogami 2026-04-20 chat 显式口径，banner 锚定该事实；W1 registry 是显式事实登记

---

## 11. 停点

**本 plan 不执行任何动作。等 Kogami 签 `GATE-P35-PLAN: Approved` + Q1-Q5 逐条仲裁。**

收到签字后 Executor：

1. 从 `main` (c88e4f0) 派生 `codex/p35-adapter-truth-level-registry`
2. 按 P35-01..05 顺序执行，每 sub-phase 1 commit
3. 三轨全绿 → 起草 P35-05-CLOSURE.md · push 分支 · 等 `GATE-P35-CLOSURE: Approved`
4. 收签 → non-FF merge main（Option M，保 SHA）→ push origin main → Notion flip → 回报 Kogami
5. 等 Kogami 明示 P36β 方向推进 / 调整 / 暂停

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P35-PLAN: Approved` (Kogami) + Q1/Q2/Q3/Q4/Q5 仲裁
