---
phase: P38
plan: P38-05
title: Closure — c919-etras 证迹完整闭环完成，等 Kogami GATE-P38-CLOSURE
status: drafted · Pending GATE-P38-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P38-PLAN Approved (Kogami 2026-04-20, Q1=C 混合 authority · Q2=A YAML SHA 固化)
  - P38-01 → P38-03 executed in order, green
---

# P38 · c919-etras 证迹完整闭环 — Closure

## 执行摘要

按 Kogami 2026-04-20 三条并发指令触发：(a) 提供 PDF 实际路径 (b) "明示 TRCU 团队 sign-off" (c) "继续推进"，合并原 P38 (PDF 回填) + P39 (TRCU sign-off) 为一个 Phase。

按 Plan 顺序 P38-01 → P38-05 完成 c919-etras 证迹对称闭环：PDF 物理入库 uploads/ + YAML head SHA 固化 + Matrix Appendix A Q1/Q2/Q3 3 项全部 resolved + Registry row 5 authority + notes 更新 + Intake packet PDF notes 末尾 P38 记录。

**与 P37 thrust-reverser 对称完成：** 今日 2 条 certified 链路（thrust-reverser + c919-etras）证迹全部闭环。

**零代码改动 · 零阈值改动 · 零 YAML value 改动 · 零 test 改动。** 纯证迹层。三轨回归零 delta（default 762 / e2e 49 / adversarial 1 全部 identical）。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact | Commit |
|---|------|------|---------------|--------|
| P38-00 | Tier 1 Plan doc | ✅ Done | 295 行 · 4 counter · Q1/Q2 已预签 | `402db31` |
| P38-01 | W1 · PDF 入库 | ✅ Done | `uploads/20260417-C919反推控制逻辑需求文档.pdf` (989 KB · 10 pages · SHA 匹配 P34 记录) | `528aa0d` |
| P38-02 | W2-W5 · 4 anchor 联动 | ✅ Done | YAML head SHA 固化 + matrix Appendix A 3 项 resolved + registry row 5 更新 + intake notes 扩展 | `8c7fd70` |
| P38-03 | W6 三轨回归 | ✅ Done | 本文档 §三轨证据 · 零 delta | (no commit) |
| P38-05 | W6 · Closure + ROADMAP + STATE + Notion DECISION | **Pending GATE-P38-CLOSURE (Kogami)** | 本文档 + ROADMAP + STATE + Notion DECISION 草案 | (本 commit) |

## 三轨回归证据

### 默认 pytest lane

```
PYTHONPATH=src python3 -m pytest tests/ --tb=no -q
→ 762 passed, 1 skipped, 49 deselected, 1 warning in 98.93s
```

**Delta vs P37 baseline (762 passed)：** 0 · identical · 零 delta。

### Opt-in e2e lane

```
PYTHONPATH=src python3 -m pytest tests/ -m e2e --tb=no -q
→ 49 passed, 763 deselected, 1 warning in 2.60s
```

**Delta vs P37 baseline：** 0 · identical。

### Adversarial live lane（via e2e wrapper）

```
PYTHONPATH=src python3 -m pytest tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes -v -m e2e
→ 1 passed in 0.26s
```

**Delta vs P37 baseline：** 0 · identical（8/8 adversarial 内部通过）。

## 代码侧 invariants（自审确认）

**新增（2 files）：**
- ✅ `uploads/20260417-C919反推控制逻辑需求文档.pdf`（P38-01, binary, 989 KB）
- ✅ `.planning/phases/P38-c919-etras-provenance-closure/P38-00-PLAN.md` + `P38-05-CLOSURE.md`（P38-00 + 本文）

**修改（4 files, annotations only）：**
- ✅ `config/hardware/c919_etras_hardware_v1.yaml`（P38-02, head +9 行 SHA/Size/Authority/Phase/Kogami 字段扩展 · `parameters:` 段字节级不变）
- ✅ `docs/c919_etras/traceability_matrix.md`（P38-02, Appendix A header + 3 项 "Pending TRCU-team sign-off" 替换为 "✅ TRCU-team sign-off via Kogami 明示"）
- ✅ `docs/provenance/adapter_truth_levels.md`（P38-02, row 5 upstream_source + authority + notes 字段更新 · 其他 4 行字节级不变）
- ✅ `src/well_harness/adapters/c919_etras_intake_packet.py`（P38-02, PDF SourceDocumentRef notes 字段扩展 · 结构字节级不变）
- ✅ `.planning/ROADMAP.md` + `.planning/STATE.md`（P38-05）

**不应该出现 (verified 字节级不变)：**
- `src/well_harness/adapters/c919_etras_adapter.py` —— 1444 LOC adapter 主体完全不变
- `config/hardware/c919_etras_hardware_v1.yaml` 的 `parameters:` 段
- `tests/test_c919_etras_adapter.py` —— 712 LOC / 63 tests 全部不变
- Thrust-reverser 任何文件（P37 已独立闭环）
- bleed_air / efds / landing_gear 任何文件
- P34 / P35 / P36β / P37 任何已签 commit 的核心 artefact
- 其他 JSON schema / ControllerTruthMetadata / demo_server / static

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — P38 commit 全走 `codex/p38-c919-etras-provenance-closure` 独立分支；non-FF merge (Option M) 等 Kogami 签 `GATE-P38-CLOSURE: Approved` 后由 Executor 执行
- ✅ **R2 不自签 Gate** — P38-00 Plan 由 Kogami 签 `GATE-P38-PLAN: Approved`（Q1=C 混合 · Q2=A SHA 固化）；本 closure 等 `GATE-P38-CLOSURE: Approved`
- ✅ **R3 Tier 1 adversarial** — P38-00 Plan §4 已写 4 条 counterargument（C1-C4）+ 就地缓解
- ✅ **R4 不自选下一 Phase 方向** — P38 由 Kogami 2026-04-20 三条并发指令明示发起（PDF + TRCU sign-off + 继续推进）；下一 Phase（P40 CI SHA · P41 workbench spec · 其他）由 Kogami 在 P38 closeout 后明示
- ✅ **R5 证迹先行** — 本 Phase 是证迹先行第四轮（c919 对称 P37）；Kogami 代 TRCU 明示 sign-off 透明标注（"代表 TRCU 团队 authority"）· 不冒充 TRCU 团队文件化签准；未来升级路径留明（TRCU 团队书面签准）

## Q1/Q2 仲裁落地结果

| Open Question | Kogami 2026-04-20 决定 | 落地位置 |
|---|---|---|
| Q1 · c919 authority 字段处理 | **C** · 混合（authority 字段维持 "甲方 (TRCU 团队)" · notes 透明记载 Kogami 代 TRCU 明示）| Registry row 5 authority 字段 + notes · Matrix Appendix A · YAML head |
| Q2 · YAML head 加 SHA256 固化字段 | **A** · 是（第 4 位置 SHA 副本）| YAML head SHA256 字段 + Size 字段 |

## Tier 1 4 条反驳落地结果

| 反驳（来自 P38-00 Plan §4）| 缓解 |
|---|---|
| C1 · Kogami 代 TRCU 明示 sign-off · 审计边界模糊 | Matrix Appendix A 3 项 resolution 明示 "signed via Kogami 2026-04-20 directive '明示 TRCU 团队 sign-off'（代表 TRCU 团队 authority 接纳）" · Registry row 5 authority 字段透明标注 · 升级路径留明 |
| C2 · c919 "甲方" vs thrust-reverser "Kogami 内部自签" · authority 等级不一致 | Q1=C 混合保留 "甲方" 标签的形式 · notes 诚实记载 Kogami 代 · registry notes 字段整合两种信息 · 审计读 matrix Appendix A 即明了实际 sign-off 机制 |
| C3 · CI 无 SHA enforcement | 4 位置 SHA 副本（intake notes / YAML head / matrix / registry notes）· P40 独立 Phase 解决 CI enforcement |
| C4 · YAML head "5 pages" typo | 事实 —— YAML head 原本已正确标 "10 pages"，plan §4 对 C4 的顾虑是误读；P38-02 无需改动，保留原值 |

## PDF 入库事实卡

| 字段 | 值 |
|------|----|
| 文件路径 | `uploads/20260417-C919反推控制逻辑需求文档.pdf` |
| 源路径 | `/Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf`（Kogami 2026-04-20 提供）|
| SHA256 | `dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5` |
| Size | 1,013,541 bytes (989 KB) |
| Pages | 10 |
| 匹配 P34 记录 | ✅ 完全匹配（SHA · size · pages 全一致，cowork P34 时期记录准确）|
| SHA 副本位置数 | 5（P34 intake notes · YAML head 新加 · matrix `dbe3f76b…` · registry row 5 notes · closure 本 doc）|

## Appendix A 3 项 resolution

| # | 原假设 | P38 sign-off |
|---|--------|-------------|
| A.Q1 | `MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT = 84.0`（mid-band of PDF §1.1.3 ⑤ 79-89%）| ✅ Kogami 代 TRCU 团队明示接纳（未来若 TRCU 团队正式书面签准 ambient-→-limit interpolation table，升级 sign-off 来源）|
| A.Q2 | MLG_WOW disagree / both-invalid → conservative FALSE（`_select_mlg_wow` adapter:195）| ✅ Kogami 代 TRCU 团队明示接纳 conservative-FALSE 立场为权威值 |
| A.Q3 | `MAX_N1K_STOW_LIMIT_PERCENT = 30.0`（PDF §Step7 未印具体数字，保守占位）| ✅ Kogami 代 TRCU 团队明示接纳 30.0 为权威值 |

## Notion DECISION 草案（等 GATE-P38-CLOSURE 后贴入控制塔）

**目标页：** 控制塔 `33cc68942bed8136b5c9f9ba5b4b44ec`（P34 / P35 / P36β / P37 DECISION 同页）

**块内容：**

```markdown
## P38 DECISION · v5.2 solo-signed (2026-04-20) · c919-etras 证迹完整闭环（PDF 入库 + TRCU sign-off 落地）

**Phase**: P38 — 证迹补完第二轮 δ 段（c919 对称 P37 闭环）
**Status**: Executed & Green; Awaiting GATE-P38-CLOSURE (Kogami)
**Gates**: `GATE-P38-PLAN: Approved` (Kogami 2026-04-20, Q1=C 混合 authority · Q2=A SHA 固化) · `GATE-P38-CLOSURE: Pending`

### Directive context

Kogami 2026-04-20 三条并发指令:
  (a) 提供 PDF 实际路径 /Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf
  (b) "明示 TRCU 团队 sign-off" (解锁 c919 Appendix A 3 项)
  (c) "继续推进"

### PDF 入库事实

- File: `uploads/20260417-C919反推控制逻辑需求文档.pdf`
- SHA256: `dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5`
- Size: 1,013,541 bytes (989 KB) · Pages: 10
- SHA 副本 5 位置（P34 intake / YAML head 新加 / matrix / registry / closure）
- 完全匹配 P34 cowork 记录 (无需修正任何已有引用)

### Artefacts (git-tracked, branch `codex/p38-c919-etras-provenance-closure` base main db03294)

- Plan: `.planning/phases/P38-c919-etras-provenance-closure/P38-00-PLAN.md` (295 行 · commit `402db31`)
- PDF: `uploads/20260417-C919反推控制逻辑需求文档.pdf` (commit `528aa0d`)
- 联动: YAML head + matrix Appendix A + registry row 5 + intake notes (commit `8c7fd70`)
- Closure: 本文档 (commit 待 P38-05)

### Regression evidence (三轨)

- default pytest: **762 passed** / 1 skipped / 49 deselected in 98.93s (identical · zero delta vs P37)
- opt-in e2e: **49 passed** / 763 deselected in 2.60s (identical)
- adversarial wrapper: **1 passed** in 0.26s (8/8 inside identical)

### Code invariants (verified byte-level)

- c919_etras_adapter.py (1444 LOC): 字节级不变
- YAML parameters 段: 字节级不变
- tests/test_c919_etras_adapter.py (712 LOC · 63 tests): 字节级不变
- thrust-reverser (P37) / 其他 3 adapter: 字节级不变

### Appendix A 3 项全部 resolved

| # | 项 | Status |
|---|---|---|
| A.Q1 | Max N1k Deploy Limit 84.0% (PDF 79-89% mid-band) | ✅ Kogami 代 TRCU 明示接纳 |
| A.Q2 | MLG_WOW conservative-FALSE | ✅ Kogami 代 TRCU 明示接纳 |
| A.Q3 | Max N1k Stow Limit 30.0% (PDF §Step7 silent) | ✅ Kogami 代 TRCU 明示接纳 |

### Authority 定位明示（Q1=C 混合）

- Registry row 5 authority 字段: 维持 "甲方 (C919 TRCU 团队)" + 加 "Q1/Q2/Q3 sign-off 由 Kogami 2026-04-20 代 TRCU 明示接纳 (P38)"
- 审计路径透明: matrix Appendix A + registry notes 明示 Kogami 代 mechanism
- 若未来需 TRCU 团队书面签准，独立 Phase 升级 sign-off 来源

### Tier 1 counterargument coverage

All 4 counterarguments (C1-C4) mitigated; see closure §Tier 1 4 条反驳落地结果。

### Today's certified chains — symmetric closure

- **thrust-reverser**: P37 · supplement §2-§7 resolved 6 Appendix A items · Kogami 内部自签
- **c919-etras**: P38 · matrix Appendix A Q1/Q2/Q3 resolved · Kogami 代 TRCU 明示接纳
- 两条 certified 链路今日对称闭环 · 5 条真值链路证迹全部整齐

### Next phase (R4 不自选)

按 P0-P4 优先级队列，候选:
- P40 · CI-level SHA enforcement (基础设施 Phase · 不需 Kogami 外部材料, 可独立完成)
- P41 · thrust-reverser workbench spec builder (补 D1=A 精益债)
- P42 · truth_level 进 ControllerTruthMetadata schema + runtime API
- 其他（由 Kogami 明示）

Execution-by: opus47-claudeapp-solo · v5.2
```

## 待 Kogami 的一个 Gate 签字

### `GATE-P38-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P38 branch 可以合入 origin/main。

**Executor 在 Gate 签字后执行**（同 P37 Option M 模式）：

1. `git checkout main` · `git merge --no-ff codex/p38-c919-etras-provenance-closure -m "..."` · `git push origin main`（SHA 保留）
2. Notion 控制塔页 append P38 DECISION（Pending）然后 flip Approved
3. 删本地 merged 分支
4. 按 P0-P4 队列请示下一方向

## 风险与已知 gap（after P38）

| 事项 | 状态 | 处置 |
|------|------|------|
| CI 无 SHA enforcement | Known gap | P40（可独立 Phase · 不依赖 Kogami 外部材料）|
| thrust-reverser 无 workbench spec (D1=A) | Known | P41 候选 |
| runtime API 不感知 truth_level | Known | P42 候选 |
| TRCU 团队未来若书面签准 | Known | supplement §7.3 类升级路径留 |

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P38-CLOSURE: Approved` (Kogami)
