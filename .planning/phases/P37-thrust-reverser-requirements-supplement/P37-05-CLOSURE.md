---
phase: P37
plan: P37-05
title: Closure — thrust-reverser 反向需求增补完成，等 Kogami GATE-P37-CLOSURE
status: drafted · Pending GATE-P37-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P37-PLAN Approved (Kogami 2026-04-20, Q1=A markdown · Q2=A A.6 一并解决)
  - P37-01 → P37-03 executed in order, green
---

# P37 · thrust-reverser 反向需求增补（code-to-spec backfill）— Closure

## 执行摘要

按 Kogami 2026-04-20 "按优先级顺序，逐步深度修复" + thrust-reverser 特殊指令"以 controller.py 为准，更新补充需求文档，然后存档"，P37 按 Plan 顺序 P37-01 → P37-05 生成了反向权威 spec supplement（markdown 格式），把 P36β 遗留的 Appendix A 6 项 open assumption 全部 resolved 到 Kogami 内部自签的 supplement 各 § 段。

**核心转变：**
- P36β 留账 6 项"⚠️ pending sign-off"→ P37 全部变"✅ supplemented by Kogami 内部自签"
- thrust-reverser authority 定位从"docx Kogami 自裁（来源未明）"转为"Kogami 内部自签（明示非外部权威）"
- controller.py 继续为真值基准，supplement 是对稳定 code 的**诚实 snapshot**

**三轨回归零 delta**（default 762 / e2e 49 / adversarial 1 全部 identical vs P36β baseline），符合 P37 无测试改动无 code 改动的设计。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact | Commit |
|---|------|------|---------------|--------|
| P37-00 | Tier 1 Plan doc | ✅ Done | `.planning/phases/P37-thrust-reverser-requirements-supplement/P37-00-PLAN.md`（319 行 · 4 counter C1-C4 · Q1-Q2 已预签）| `ce5adfc` |
| P37-01 | W1 · Supplement markdown | ✅ Done | `docs/thrust_reverser/requirements_supplement.md`（297 行 · 8 § · 覆盖 A.1-A.6）| `0ba643c` |
| P37-02 | W2-W5 · 4 anchor 联动 | ✅ Done | matrix Appendix A 6 项 ⚠️→✅ + intake 4th SourceDocumentRef + YAML 头 supplement block + registry row 1 notes | `2bc1eeb` |
| P37-03 | W6 三轨回归 | ✅ Done | 本文档 §三轨证据 · 零 delta | (no commit) |
| P37-05 | W6 · Closure + ROADMAP + STATE + Notion DECISION | **Pending GATE-P37-CLOSURE (Kogami)** | 本文档 + ROADMAP + STATE + Notion DECISION 草案 | (本 commit) |

## 三轨回归证据

### 默认 pytest lane

```
PYTHONPATH=src python3 -m pytest tests/ --tb=no -q
→ 762 passed, 1 skipped, 49 deselected, 1 warning in 91.27s (0:01:31)
```

**Delta vs P36β baseline (762 passed)：** 0 · identical · 零 delta（P37 不加测试不改代码，identical 是预期结果）。

### Opt-in e2e lane

```
PYTHONPATH=src python3 -m pytest tests/ -m e2e --tb=no -q
→ 49 passed, 763 deselected, 1 warning in 2.72s
```

**Delta vs P36β baseline：** 0 · identical。

### Adversarial live lane（via e2e wrapper）

```
PYTHONPATH=src python3 -m pytest tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes -v -m e2e
→ 1 passed in 0.26s
```

**Delta vs P36β baseline：** 0 · identical（8/8 adversarial 内部通过）。

## 代码侧 invariants（自审确认）

P37 应改动的文件域：

**新增（2 files）**
- ✅ `docs/thrust_reverser/requirements_supplement.md`（P37-01, 297 行）
- ✅ `.planning/phases/P37-thrust-reverser-requirements-supplement/P37-00-PLAN.md`（P37-00, 319 行）
- ✅ `.planning/phases/P37-thrust-reverser-requirements-supplement/P37-05-CLOSURE.md`（P37-05, 本文档）

**修改（4 files, annotations only）**
- ✅ `docs/thrust_reverser/traceability_matrix.md`（P37-02, Appendix A header + 6 items rewritten + table 5 status 标记）
- ✅ `src/well_harness/adapters/thrust_reverser_intake_packet.py`（P37-02, +20 行第 4 SourceDocumentRef · D1=A Lean 保留）
- ✅ `config/hardware/thrust_reverser_hardware_v1.yaml`（P37-02, docx § map 5 行改 + 新 supplement provenance block · `parameters:` 段字节级不变）
- ✅ `docs/provenance/adapter_truth_levels.md`（P37-02, row 1 notes + upstream_source + authority 字段更新 · 其他 4 行字节级不变）
- ✅ `.planning/ROADMAP.md` + `.planning/STATE.md`（P37-05）

**不应该出现 (verified 字节级不变)：**
- `src/well_harness/controller.py` —— DeployController class 完全不变
- `src/well_harness/models.py` —— HarnessConfig dataclass 完全不变
- `config/hardware/thrust_reverser_hardware_v1.yaml` 的 `parameters:` 段
- `tests/` 所有文件所有断言
- `uploads/20260409-thrust-reverser-control-logic.docx` —— 原 docx 冻结不动
- `src/well_harness/adapters/__init__.py` —— 不注册 supplement 模块（不存在，supplement 是 markdown 不是 py）
- 其他 4 adapter（bleed_air / efds / landing_gear / c919_etras）所有文件
- P34 / P35 / P36β 任何 commit 的文件（除 P35 registry row 1）

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — P37 commit 全走 `codex/p37-thrust-reverser-requirements-supplement` 独立分支；non-FF merge (Option M) 到 main 等 Kogami 签 `GATE-P37-CLOSURE: Approved` 后由 Executor 执行
- ✅ **R2 不自签 Gate** — P37-00 Plan 由 Kogami 签 `GATE-P37-PLAN: Approved`（Q1=A markdown · Q2=A A.6 一并解决）；本 closure 等 `GATE-P37-CLOSURE: Approved`
- ✅ **R3 Tier 1 adversarial** — P37-00 Plan §4 已写 4 条 counterargument（C1-C4）+ 就地缓解；本 closure 不额外自审（plan 已覆盖）
- ✅ **R4 不自选下一 Phase 方向** — P37 由 Kogami 2026-04-20 "按优先级顺序，逐步深度修复" + thrust-reverser 特殊处理指令明示发起；下一 Phase（P38 P34 PDF 回填 或 P39 c919 Appendix A sign-off 或 P40 CI SHA / 其他）由 Kogami 在 P37 closeout 后按 P0-P4 队列**再次明示**
- ✅ **R5 证迹先行** — 本 Phase 是证迹先行第三轮；反向生成过程透明记录（supplement §1 明示反向性质 / matrix Appendix A 保留 P37 来源标记 / registry row 1 明示 supplemented by P37）；不掩盖"supplement 非外部权威"事实（supplement §7 明示 + registry authority 明示）

## Q1-Q2 仲裁落地结果

| Open Question | Kogami 2026-04-20 决定 | 落地位置 |
|---|---|---|
| Q1 · supplement 文件格式 | **A** · Markdown | `docs/thrust_reverser/requirements_supplement.md`（297 行）|
| Q2 · A.6 docx authority 处置 | **A** · 本 Phase 一并解决 | Supplement §7 + Matrix Appendix A.6 + Registry row 1 authority 字段 |

## Tier 1 4 条反驳落地结果

| 反驳（来自 P37-00 Plan §4）| 缓解 |
|---|---|
| C1 · ex-post facto 真值化 · 审计断点 | Supplement §1 开头明示反向性质 · Matrix Appendix A 每项保留 "P37 来源" · Registry notes "supplemented by P37" · Phase naming 使用 "reverse-backfill" · 原 docx 保留作历史 snapshot |
| C2 · Kogami 内部自签 不够硬 | Supplement §7 明示适用/不适用场景 · Registry authority 字段明示 "非外部权威" · §7.3 列升级路径给未来 certification · Well Harness 当前 scope 匹配此 authority |
| C3 · markdown 不如 docx 正式 | Kogami Q1=A 明选 · markdown git-native 版本控制友好 · 原 docx 保留 · pandoc 可转 |
| C4 · supplement 背书 code bug | 535 LOC tests 覆盖 + 今日三轨稳定 · supplement 是对稳定 code 的诚实 snapshot · 若 code 有 bug 修 code + 同步修 supplement · 风险 = code 本身风险 |

## Registry row 1 升级对比

**P36β 版（2026-04-20 earlier）：**
```
thrust-reverser | certified | In use | uploads/20260409-thrust-reverser-control-logic.docx
  | Kogami 自裁（docx 具体签准方待 Appendix A.6 明示）| —
  | 已 certified · ... · 6 Appendix A open assumptions pending sign-off
```

**P37 升级（2026-04-20 later）：**
```
thrust-reverser | certified | In use
  | uploads/20260409-thrust-reverser-control-logic.docx (原 docx 历史 snapshot)
    + docs/thrust_reverser/requirements_supplement.md (P37 反向补完)
  | Kogami 内部自签（明示非外部权威 · 见 supplement §7）| —
  | ... · Appendix A 6 项全部 resolved via P37 supplement
  | 若需外部 certification-grade authority 需新 Phase 升级 · supplement §7.3 列升级路径
```

## Notion DECISION 草案（等 GATE-P37-CLOSURE 后贴入控制塔）

**目标页：** 控制塔 `33cc68942bed8136b5c9f9ba5b4b44ec`（P34 / P35 / P36β DECISION 同页）

**块内容：**

```markdown
## P37 DECISION · v5.2 solo-signed (2026-04-20) · thrust-reverser 反向需求增补（code-to-spec backfill）

**Phase**: P37 — 证迹补完第二轮 γ 段（反向权威生成）
**Status**: Executed & Green; Awaiting GATE-P37-CLOSURE (Kogami)
**Gates**: `GATE-P37-PLAN: Approved` (Kogami 2026-04-20, Q1=A markdown · Q2=A A.6 一并解决) · `GATE-P37-CLOSURE: Pending`

### Directive context

Kogami 2026-04-20: "按优先级顺序，逐步深度修复" + thrust-reverser 特殊指令 "以 controller.py 为准，更新补充需求文档，然后存档"。

### 核心产出

- `docs/thrust_reverser/requirements_supplement.md` (297 行, 8 §, markdown, **Kogami 内部自签 authority**)
- Matrix Appendix A 6 项全部 resolved (⚠️ → ✅)
- Intake packet 从 3 SourceDocumentRef 扩到 4 (加 supplement markdown ref, D1=A Lean 保留)
- YAML 头增补 provenance block + 5 行 docx § map 更新 (parameters 字节级不变)
- Registry row 1 notes + upstream_source + authority 字段升级

### Artefacts (git-tracked, branch `codex/p37-thrust-reverser-requirements-supplement` base main 96bacaf)

- Plan: `.planning/phases/P37-thrust-reverser-requirements-supplement/P37-00-PLAN.md` (319 行 · commit `ce5adfc`)
- Supplement: `docs/thrust_reverser/requirements_supplement.md` (297 行 · commit `0ba643c`)
- 联动更新: matrix + intake + yaml + registry (commit `2bc1eeb`)
- Closure: 本文档 (commit 待 P37-05)

### Regression evidence (三轨)

- default pytest: **762 passed** / 1 skipped / 49 deselected in 91.27s (identical to P36β baseline, zero delta)
- opt-in e2e: **49 passed** / 763 deselected in 2.72s (identical)
- adversarial wrapper: **1 passed** in 0.26s (8/8 inside identical)

### Code invariants (verified byte-level)

- controller.py / models.py: 字节级不变
- YAML parameters 段: 字节级不变
- 既有测试断言: 字节级不变
- 原 docx 20260409: 冻结不动

### Appendix A 6 项全部 resolved

| # | 项 | Status |
|---|---|---|
| A.1 | SW2 触发角度 ±5.0°/-9.8° | ✅ P37 supplement §2 · mirroring SW1 pattern |
| A.2 | Deploy 90% VDT | ✅ P37 supplement §3 · 行业默认 |
| A.3 | TLS/PLS 解锁延迟 0.3/0.2s | ✅ P37 supplement §4 · simulation baseline |
| A.4 | Deploy rate 30%/s | ✅ P37 supplement §5 · simplified-plant baseline |
| A.5 | 故障模式 | ✅ P37 supplement §6 · 维持 docx §58 "不考虑" 立场 + 未来挂钩 |
| A.6 | docx authority | ✅ P37 supplement §7 · Kogami 内部自签 · 非外部权威 · 升级路径明示 |

### Authority 定位明示

- Supplement authority = **Kogami 内部自签**（非甲方 / 非监管 / 非行业标准）
- Well Harness 当前 scope = 项目内部控制逻辑验证平台（非取证交付）
- Authority 级别**匹配**项目 scope
- 若未来需外部 certification，supplement §7.3 列升级路径（引入 TRCU / 适航局等外部签准方）

### Tier 1 counterargument coverage

All 4 counterarguments (C1-C4) mitigated; see closure §Tier 1 4 条反驳落地结果。

### Next phase (R4 不自选)

按 P0-P4 优先级队列，候选:
- P38 · P34 PDF 回填 uploads/ (需 Kogami 提供 PDF)
- P39 · c919-etras Appendix A 3 项 sign-off (需 Kogami 明示来源或 delegate)
- P40 · CI SHA enforcement (基础设施 Phase)
- 其他（由 Kogami 明示）

Execution-by: opus47-claudeapp-solo · v5.2
```

## 待 Kogami 的一个 Gate 签字

### `GATE-P37-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P37 branch 可以合入 origin/main。

**Executor 在 Gate 签字后执行**（一次性脚本，同 P34/P35/P36β Option M 模式）：

1. `git checkout main` · `git fetch origin` · `git merge --no-ff codex/p37-thrust-reverser-requirements-supplement -m "..."` · `git push origin main`（SHA 保留：`ce5adfc` / `0ba643c` / `2bc1eeb` / 本 commit）
2. Notion 控制塔页 `33cc68942bed8136b5c9f9ba5b4b44ec` append 上方 "Notion DECISION 草案"（Pending）然后 flip Pending → Approved (Kogami YYYY-MM-DD)
3. 删本地 merged 分支 `codex/p37-thrust-reverser-requirements-supplement`
4. 按 P0-P4 优先级队列请示下一 Phase 方向（R4 不自选）

## 风险与已知 gap (after P37)

| 事项 | 状态 | 处置 |
|------|------|------|
| c919-etras Appendix A 3 项 TRCU sign-off TODO | 未动 (P37 不涉 c919) | P39（下一 P0 Phase 候选）|
| P34 PDF 未入库 uploads/ | 未动 (P37 不涉 P34) | P38（等 Kogami 提供 PDF）|
| CI SHA enforcement | 未动 | P40（基础设施 Phase）|
| thrust-reverser 无 workbench spec (D1=A 精益) | 未动 (P37 不破 D1=A) | P1 队列候选（未来） |
| 运行时 API 不感知 truth_level | 未动 | P1 队列候选 |

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P37-CLOSURE: Approved` (Kogami)
