---
phase: P37
plan: P37-00
title: thrust-reverser 反向需求增补（code-to-spec backfill）— Appendix A 6 项 resolved via supplement
status: drafted · Awaiting GATE-P37-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P36β-CLOSURE Approved (Kogami 2026-04-20) → origin/main at 96bacaf
  - Kogami 2026-04-20 directive: "以 controller.py 为准，更新补充需求文档，然后存档" (thrust-reverser 特殊处理)
  - Kogami 2026-04-20 执行节奏: "按优先级顺序，逐步深度修复" (P0 首个)
  - GATE-P37-PLAN Approved (Kogami 2026-04-20, Q1=A Markdown · Q2=A A.6 一并解决)
  - 已有 infra: uploads/ convention (P36β-01 建立) · intake packet精益模式 (D1=A) · traceability matrix Appendix A 6 项登记
non-goals:
  - 改 src/well_harness/controller.py 一行（真值基准不变）
  - 改 src/well_harness/models.py 任何常数
  - 改 config/hardware/thrust_reverser_hardware_v1.yaml 任何 value（仅头注释扩展）
  - 改原 uploads/20260409-thrust-reverser-control-logic.docx（保留为历史 snapshot）
  - 改 P34 / P35 / P36β 任何已签文件（除本 Phase 显式范围内的联动更新）
  - 改其他 4 adapter（bleed_air / efds / landing_gear / c919-etras 都不动）
  - 新增测试（P35-03 banner test 无需扩展 · thrust-reverser 不在 frozen 列表）
  - 破 D1=A 精益模式（intake packet 仅加第 4 个 SourceDocumentRef · 业务 fields 保持空）
  - 自签外部 authority（supplement authority = Kogami 内部自签 · 非甲方 / 非监管 / 非行业标准）
---

# P37-00 Plan · thrust-reverser 反向需求增补（code-to-spec backfill）

## 0. TL;DR

按 Kogami 2026-04-20 "按优先级顺序，逐步深度修复" + thrust-reverser 特殊指令："以 controller.py 为准，更新补充需求文档，然后存档"，P37 生成一份增补需求文档（markdown 格式），反向覆盖当前原 docx `20260409-thrust-reverser-control-logic.docx` 缺的 5 处常数 + 明确 A.6 authority 地位，把 P36β 留的 Appendix A 6 项 open assumption 全部 resolve 为"Kogami 内部自签"。

**核心转变：**
- 原 docx = 历史 snapshot（57 段 · 覆盖 60% · 仍保留作审计锚）
- 新 supplement = 反向权威补完（Kogami 自签 · 覆盖 100% · 成为并列 authority）
- controller.py + models.py = 不变的真值基准（本 Phase non-goal 首条）

**规模估算：**
- W1 · `docs/thrust_reverser/requirements_supplement.md` ~180 行（8 段 · 覆盖 A.1-A.6 + 背景 + 与原 docx 关系）
- W2 · `docs/thrust_reverser/traceability_matrix.md` Appendix A 修改 ~30 行（6 项 status: pending → supplemented）
- W3 · `src/well_harness/adapters/thrust_reverser_intake_packet.py` +20 行（第 4 个 SourceDocumentRef）
- W4 · `config/hardware/thrust_reverser_hardware_v1.yaml` 头 +15 行（supplement provenance block）
- W5 · `docs/provenance/adapter_truth_levels.md` row 1 notes 1 行修改
- W6 · closure + ROADMAP + STATE + Notion DECISION
- **总 ~600 行 · 0 code behavior change · 0 threshold change · 0 YAML value change · 0 test assertion change**

---

## 1. 上下文

### 1.1 为什么需要 supplement（P36β 留账 + Kogami 披露）

P36β 收口时 Appendix A 登记了 6 项 open assumption：
- A.1 SW2 ±5.0/-9.8° · Executor 假设镜像 SW1
- A.2 Deploy 90% VDT · 行业默认
- A.3 TLS/PLS unlock delays 0.3/0.2s
- A.4 Deploy rate 30%/s
- A.5 Fault modes docx §58 "不考虑"
- A.6 docx authority（author/version/sign-off 未知）

Kogami 2026-04-20 明示："之前的 controller 以及完备了，可能你丢失了需求文档的全文"。这个披露重新定位了 gap 的性质：
- **不是 docx 缺失 5 处常数** —— 而是 **docx 本身可能是 code 的不完整 projection**
- **不是 controller.py 超出 docx 范围** —— 而是 **docx 截了一个子集，code 是完整的**
- **解法不是等 authority sign-off** —— 而是 **以 code 为权威反向生成完整 spec**

### 1.2 Supplement 的性质定位（明示声明，防混淆）

- **权威级别：** Kogami 内部自签
- **不冒充：** 不是甲方 PDF / 不是监管文件 / 不是行业标准
- **适用场景：** 项目内部控制逻辑验证 · 工程协作锚点 · GSD 证迹链
- **不适用场景：** 航空适航认证 / 对外客户交付 / 法规合规声明 · 若用于此类场合需另开 Phase 升级 authority
- **与原 docx 关系：** 并列 authority · 原 docx 保留为"历史 snapshot"不变

### 1.3 "反向真值化" 的透明度保证

P37 不掩盖"supplement 是 P37 反向生成的"这一事实：
- supplement §1 开头**明示反向性质**
- traceability matrix Appendix A 保留每项"P37 supplement 来源"记录
- registry row 1 notes 明确"supplemented by P37"
- 审计时任何人读到 supplement + matrix + registry 都能立刻知道真值生成路径

---

## 2. Scope — 6 工作包

### W1 · 新增 `docs/thrust_reverser/requirements_supplement.md`（~180 行）

8 段结构：

| § | 标题 | 内容 |
|---|------|------|
| §1 | 导言与范围 | supplement 性质明示（Kogami 内部自签 · 反向补完）· 与原 docx 关系 · 适用/不适用场景 |
| §2 | SW2 触发角度（补 A.1）| `SW2 near_zero_deg = -5.0°` · `SW2 deep_reverse_deg = -9.8°`；镜像 SW1 pattern 的工程依据 |
| §3 | Deploy 90% VDT 阈值（补 A.2）| `deploy_90_threshold_percent = 90.0%`；行业默认 "VDT > 90% 视为完全展开"的工程出处 |
| §4 | TLS/PLS 解锁延迟（补 A.3）| `tls_unlock_delay_s = 0.3` / `pls_unlock_delay_s = 0.2`；机电时序 baseline |
| §5 | 反推作动速率（补 A.4）| `deploy_rate_percent_per_s = 30.0`；actuator 速率 baseline |
| §6 | 故障模式（补 A.5）| 明示 "P37 维持 P36β 的 docx §58 '不考虑'立场"；未来扩展挂钩说明 |
| §7 | Authority 定义（补 A.6）| 明示 Kogami 内部自签 · 非外部 authority · 升级路径 |
| §8 | 与原 docx 和 code 关系 | 三方 authority 关系：code 为真值基准 / 原 docx 为历史 snapshot / supplement 为反向补完 |

### W2 · 更新 `docs/thrust_reverser/traceability_matrix.md`

- Appendix A 6 项从 "⚠️ pending sign-off" → "✅ supplemented by P37 · Kogami 自签"
- 每项加指向 supplement § 号
- 表 5 阈值常数列：⚠️ 改 ✅ 并加 "→ supplement §X" 引用
- 不改原有结构和表头

### W3 · 更新 `src/well_harness/adapters/thrust_reverser_intake_packet.py`

- 加第 4 个 `SourceDocumentRef`：
  ```python
  SourceDocumentRef(
      id="thrust-reverser-supplement-001",
      kind="markdown",
      title="Thrust Reverser Requirements Supplement (P37 · reverse-backfill)",
      location="docs/thrust_reverser/requirements_supplement.md",
      role="requirement_supplement",
      notes=(
          "Reverse-engineered spec supplement covering 5 constants + 1 authority clause "
          "that original docx did not cover. Kogami 内部自签 authority. Companion to "
          "uploads/20260409-thrust-reverser-control-logic.docx (historical snapshot)."
      ),
  )
  ```
- 保持业务 fields 仍为空（D1=A 精益不破）
- docstring 头部 note 加 "P37 extension: 4 SourceDocumentRef (controller + docx + yaml + supplement)"

### W4 · 更新 `config/hardware/thrust_reverser_hardware_v1.yaml` 头

- 在 docx provenance block 之后加 supplement provenance block：
  ```
  # supplement provenance (P37 · 2026-04-20 · Kogami 内部自签):
  # =======================================================================
  # Source:     docs/thrust_reverser/requirements_supplement.md (markdown)
  # Authority:  Kogami 内部自签 (P37 · code-to-spec backfill)
  # Purpose:    Reverse-engineered spec for 5 constants + 1 authority clause
  #             not covered by original docx 20260409 (historical snapshot).
  # Coverage:   SW2 angles (§2) / Deploy 90% VDT (§3) / TLS/PLS delays (§4) /
  #             Deploy rate (§5) / Fault modes (§6) / Authority (§7)
  ```
- 表 5 阈值 → docx § map 里 "docx NO" 改成 "supplement §X"
- 不改 `parameters:` 段任何 value

### W5 · 更新 `docs/provenance/adapter_truth_levels.md` row 1 notes

从：
```
... · 6 Appendix A open assumptions pending sign-off
```
改为：
```
... · 5 Appendix A constants supplemented by P37 (Kogami 内部自签) · A.5 (fault modes) 维持 docx §58 立场 · A.6 (authority) resolved: Kogami 内部 authority
```

（其余 4 行字节级不变）

### W6 · 收口

- 三轨回归（**期望零 delta** 同 P36β）
- `.planning/ROADMAP.md` 追加 P37 段
- `.planning/STATE.md` 更新 Current Position
- `.planning/phases/P37-thrust-reverser-requirements-supplement/P37-05-CLOSURE.md` 新建
- Notion DECISION append（Pending 状态）
- push branch · 等 `GATE-P37-CLOSURE: Approved`

---

## 3. Non-goals — 严格禁止

已在 frontmatter 全列。强调：
- **不**改 `controller.py` / `models.py` / YAML value / test
- **不**改原 docx
- **不**破 D1=A 精益模式（业务 fields 仍空）
- **不**自签外部 authority（supplement authority 仅限 Kogami 内部）
- **不**改其他 4 adapter 任何行（bleed/efds/lg/c919 不动）
- **不**新增测试（P35-03 banner test 无需扩展）
- **不**修改 P34 / P35 / P36β 已签文件（除 row 1 notes）

---

## 4. Tier 1 对抗性自审（4 条 · C1-C4）

### C1 · "反向生成需求文档 = ex-post facto 真值化 · 审计追溯链存在断点"

**承认有效。** 缓解：
1. supplement §1 **开头明示**反向性质 · 任何读者立即知道这是 code-to-spec backfill 不是 upstream authority
2. traceability matrix Appendix A 每项保留"P37 supplement 来源"标记 · 不隐藏事实
3. registry row 1 notes **明确**标注 "supplemented by P37" · 状态透明化
4. Phase naming **"reverse-backfill"** 直接命名 · commit message / closure doc / Notion DECISION 都沿用此词 · 审计友好
5. 原 docx **保留**作历史 snapshot（non-goal 明列）· 任何人想看"P37 前状态"可读原 docx

### C2 · "Kogami 内部自签 authority 在外部认证场合不够硬"

**承认。** 缓解：
1. supplement §7 **明示**适用/不适用场景 · 不适用场景明确列：航空适航认证 / 对外客户交付 / 法规合规
2. registry row 1 authority 字段 **明确**标 "Kogami 内部自签" · 不冒充甲方 / 监管 / 行业
3. 未来若需外部认证 · 独立 Phase 升级 · supplement §7 留升级路径
4. Well Harness 当前定位是**项目内部控制逻辑验证平台** · 非取证交付系统 · 此 authority 级别匹配项目 scope

### C3 · "markdown 格式不够正式 / 不如 docx"

**部分有效但权衡后选 markdown。** 缓解：
1. Kogami Q1=A 明选 markdown · 执行 directive
2. markdown 是 git-native · 版本控制 · diff 友好 · CI 扫描友好
3. 未来若需 docx export · 手工 pandoc 转换 <10 分钟 · 不 lock-in
4. 原 docx 保留 · 双格式并存

### C4 · "supplement 背书了 code 值 · 如果 code 本身有 bug, supplement 把 bug 也背书"

**承认。** 缓解：
1. `controller.py` + `HarnessConfig` 常数已经过 535 LOC test 覆盖（test_controller.py 315 + test_controller_adapter.py 127 + test_controller_truth_adapter_metadata_schema.py 93）
2. 今日全天三轨回归稳定（default 762 / e2e 49 / adversarial 8-of-8）
3. P25-P30 pitch readiness drill 每日跑 · code 行为稳定
4. supplement 是对**既有稳定 code 的诚实 snapshot**，不是新主张 · 风险级别 = code 本身的风险级别
5. 若未来发现 code bug · 修 code · 同步更新 supplement · 这是正常维护流程

---

## 5. Open Questions 已 resolved

| Q | Kogami 2026-04-20 决定 |
|---|------------------------|
| Q1 · supplement 文件格式 | **A** · Markdown |
| Q2 · A.6 docx authority 处置 | **A** · 本 Phase 一并解决 · supplement §7 明示 Kogami 内部自签 |

**无新 Open Questions** · plan 执行阶段若出现未预见分支立即 STOP 报告 Kogami。

---

## 6. Sub-phase 分解

### P37-00 · Plan (本文档 · ~320 行 · 已签)

### P37-01 · supplement markdown 新增（~30 min）
- 新建 `docs/thrust_reverser/requirements_supplement.md` ~180 行
- 8 段内容（§1 导言 / §2-§6 常数补完 / §7 authority / §8 关系）
- 单 commit: `feat(P37-01): thrust-reverser requirements supplement (reverse-backfill, Kogami 内部自签)`

### P37-02 · 4 anchors 联动更新（~45 min）
- W2 matrix Appendix A 标记变 + 表 5 引用
- W3 intake packet 加第 4 SourceDocumentRef
- W4 YAML 头 supplement provenance block
- W5 registry row 1 notes 1 行修改
- 本地跑 `PYTHONPATH=src python -c "from well_harness.adapters.thrust_reverser_intake_packet import build_thrust_reverser_intake_packet; p=build_thrust_reverser_intake_packet(); print(len(p.source_documents))"` 验证 4 refs
- 本地跑 `python -c "import yaml; yaml.safe_load(open('config/hardware/thrust_reverser_hardware_v1.yaml'))"` 验证 YAML parse 清洁
- 单 commit: `docs(P37-02): anchor matrix/intake/yaml/registry to supplement (4 files)`

### P37-03 · 三轨回归（~20 min）
- default / e2e / adversarial · 期望零 delta
- 不单独 commit · 结果贴 closure

### P37-05 · 收口（~40 min）
- closure doc
- ROADMAP + STATE
- Notion DECISION append (Pending)
- 单 commit: `docs(P37-05): closure — awaiting GATE-P37-CLOSURE`
- push branch

**总 4 commits · ~2-2.5h 工时。**

---

## 7. Exit Criteria

- `docs/thrust_reverser/requirements_supplement.md` 新建 · 8 段 · A.1-A.6 全覆盖
- `docs/thrust_reverser/traceability_matrix.md` Appendix A 6 项 ⚠️→✅ · 表 5 阈值引用更新
- `src/well_harness/adapters/thrust_reverser_intake_packet.py` 4 SourceDocumentRef · D1=A 精益保留
- `config/hardware/thrust_reverser_hardware_v1.yaml` 头部 supplement block + `parameters:` 字节级不变
- `docs/provenance/adapter_truth_levels.md` row 1 notes 改 · 其他 4 行不变
- 三轨回归 default 762 / e2e 49 / adversarial 1 identical · 零 delta
- ROADMAP + STATE 更新 · closure drafted
- Notion DECISION append (Pending)
- Branch `codex/p37-thrust-reverser-requirements-supplement` 4 commits pushed

---

## 8. 风险与回滚

| 风险 | 概率 | 影响 | 缓解/回滚 |
|------|------|------|----------|
| supplement 文字未来被 Kogami 要求改 | 中 | 小 | markdown 单文件修订成本极低 |
| matrix Appendix A 联动有漏 | 低 | 小 | 6 项逐条确认 · 表 5 逐行 cross-check |
| intake packet 加 4th SourceDocumentRef 破 D1=A 精益 | 低 | 中 | 业务 fields 仍 = () · 仅 metadata 扩展 · non-goal 严守 |
| YAML head 新 block 误影响 parse | 低 | 中 | commit 前跑 yaml.safe_load 验证 · 已列入 P37-02 checklist |
| registry row 1 notes 修改触发 P35-03 banner test | 极低 | 小 | banner test 不检 thrust-reverser · 不影响 |
| 三轨出现 delta | 极低 | 中 | P37 不加测试不改代码不改 YAML value · delta 说明意外污染 · 回退 commit 排查 |

**回滚策略：** `GATE-P37-CLOSURE` 不批时，`git revert` 回到 `96bacaf` main HEAD。P37 branch 保留作审计存证。

---

## 9. v5.2 红线合规预声明（plan 级）

- **R1 不可逆 main HEAD** — P37 commit 走 `codex/p37-thrust-reverser-requirements-supplement` 独立分支；non-FF merge (Option M) 等 `GATE-P37-CLOSURE: Approved` 后由 Executor 执行
- **R2 不自签 Gate** — P37-00 Plan 由 Kogami 2026-04-20 签 `GATE-P37-PLAN: Approved`（Q1=A / Q2=A）；P37-05 等 `GATE-P37-CLOSURE: Approved`
- **R3 Tier 1 adversarial** — §4 已写 4 条反驳（C1-C4）+ 就地缓解
- **R4 不自选下一 Phase 方向** — P37 由 Kogami 2026-04-20 "thrust-reverser 特殊处理" 明示指令发起；下一 Phase 方向（P38 P34 PDF 回填 / P39 c919 Appendix A sign-off / P40 CI SHA / 其他）由 Kogami 在 P37 closeout 后**按优先级顺序**明示下一步
- **R5 证迹先行** — 本 Phase 是证迹先行第三轮；用 code-to-spec 反向生成 · 透明记录反向过程 · 明示 authority 级别；不冒充外部权威

---

## 10. 停点

**本 plan 已由 Kogami 2026-04-20 签 `GATE-P37-PLAN: Approved`（Q1=A / Q2=A）**

Executor 立即开始执行 P37-01..05：

1. ✅ 已切 `codex/p37-thrust-reverser-requirements-supplement`（本 commit 所在分支）
2. P37-01 写 supplement markdown
3. P37-02 4 anchors 联动更新
4. P37-03 三轨回归
5. P37-05 closure + ROADMAP + STATE + Notion DECISION (Pending)
6. push branch · 等 `GATE-P37-CLOSURE: Approved`

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Gate Approved:** `GATE-P37-PLAN: Approved` (Kogami 2026-04-20, Q1=A / Q2=A)
**Awaiting next:** `GATE-P37-CLOSURE: Approved` after P37-01..05 executed green
