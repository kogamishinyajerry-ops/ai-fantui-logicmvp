---
phase: P35
plan: P35-05
title: Closure — Adapter Truth-Level Registry + Freeze Banner 落地完成，等 Kogami GATE-P35-CLOSURE
status: drafted · Pending GATE-P35-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P35-PLAN Approved (Kogami 2026-04-20, Q1=C / Q2=A / Q3=B / Q4=A / Q5=A)
  - P35-01 → P35-04 executed in order, green
---

# P35 · Adapter Truth-Level Registry + Demonstrative Adapters Freeze Banner — Closure

## 执行摘要

按 Kogami 2026-04-20 方向指令 **D · 证迹补完第二轮** + `GATE-P35-PLAN: Approved`（Q1-Q5 五项仲裁），P35α 按 Plan 顺序 P35-01 → P35-05 将 Q2=B 扫描识别出的 3 个 demonstrative adapter（bleed_air / efds / landing_gear）的"无需求来源"事实显式登记并加防回归测试。

**零代码行为改动，零阈值/YAML 数字改动，零既有测试断言改动。** 纯文档层证迹固化，新增 1 registry + 7 banner + 1 regression test。

**三轨回归零既有回归**，+15 新增 tests（P35-03）全绿，default 762 vs P34 baseline 747（+15 符合预期，无污染），e2e/adversarial identical。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact |
|---|------|------|---------------|
| P35-00 | Tier 1 Plan doc（5 counterargument + 5 Open Questions） | ✅ Done | `.planning/phases/P35-adapter-truth-level-registry/P35-00-PLAN.md`（315 行）· commit `c886e14` |
| P35-01 | W1 · Truth-level registry | ✅ Done | `docs/provenance/adapter_truth_levels.md`（101 行 · 5 rows · schema C）· commit `5a7e7b1` |
| P35-02 | W2 · FROZEN banner × 7 files | ✅ Done | 3 adapter + 2 intake + 2 yaml · commit `6cc0d31` · +76 行注释/docstring |
| P35-03 | W3 · Banner regression guard | ✅ Done | `tests/test_adapter_freeze_banner.py`（88 行 · 15 parametrized cases）· commit `e0f8a8a` |
| P35-04 | 三轨回归 | ✅ Done | 本文档 §三轨证据 |
| P35-05 | Closure + ROADMAP + STATE + Notion DECISION | **Pending GATE-P35-CLOSURE (Kogami)** | 本文档 + 下方 Notion DECISION 草案 |

## 三轨回归证据

### 默认 pytest lane

```
PYTHONPATH=src python3 -m pytest tests/ --tb=no -q
→ 762 passed, 1 skipped, 49 deselected, 1 warning in 119.24s (0:01:59)
```

**Delta vs P34 baseline (747 passed)：** +15 新增 P35-03 parametrized cases · 零既有测试失败。

### Opt-in e2e lane

```
PYTHONPATH=src python3 -m pytest tests/ -m e2e --tb=no -q
→ 49 passed, 763 deselected, 1 warning in 2.71s
```

**Delta vs P34 baseline：** 0 · identical。

### Adversarial live lane（via e2e wrapper）

```
PYTHONPATH=src python3 -m pytest tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes -v -m e2e
→ 1 passed in 0.25s
```

`tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes` 包裹 `WELL_HARNESS_PORT=8799 src/well_harness/static/adversarial_test.py`，内部 8/8 断言通过。

**Delta vs P34 baseline：** 0 · identical。

## 代码侧 invariants（自审确认）

P35α 应改动的文件域（`git diff main..codex/p35-adapter-truth-level-registry --stat`）：

**新增（3 files）**
- ✅ `docs/provenance/adapter_truth_levels.md`（P35-01）
- ✅ `tests/test_adapter_freeze_banner.py`（P35-03）
- ✅ `.planning/phases/P35-adapter-truth-level-registry/P35-00-PLAN.md`（P35-00）+ 本文件 `P35-05-CLOSURE.md`（P35-05）

**修改（7 files, +76 行 banner only）**
- ✅ `src/well_harness/adapters/bleed_air_adapter.py`（+11 行 docstring append）
- ✅ `src/well_harness/adapters/bleed_air_intake_packet.py`（+6 行 docstring append）
- ✅ `src/well_harness/adapters/efds_adapter.py`（+17 行 new docstring）
- ✅ `src/well_harness/adapters/landing_gear_adapter.py`（+17 行 new docstring）
- ✅ `src/well_harness/adapters/landing_gear_intake_packet.py`（+11 行 new docstring）
- ✅ `config/hardware/bleed_air_hardware_v1.yaml`（+7 行 head comment）
- ✅ `config/hardware/landing_gear_hardware_v1.yaml`（+7 行 head comment）

**应改动但本 Phase 不触 (P35-05)：** `.planning/ROADMAP.md` + `.planning/STATE.md` + 本 closure doc（同 commit `docs(P35-05):` 落地）。

**不应该出现：** 任何 adapter 行为逻辑 / 阈值 / test assertion 改动；`controller.py` / `models.py` / `ControllerTruthMetadata` / JSON schema / `demo_server` / static / 既有测试文件改动；c919_etras / thrust_reverser 关联 file 改动。如出现即违反 P35α non-goal。

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — 本 closure 不触发 main advance；P35 commit 全走 `codex/p35-adapter-truth-level-registry` 独立分支；non-FF merge（Option M 同 P34）到 main 等 Kogami 签 `GATE-P35-CLOSURE: Approved` 后由 Executor 执行
- ✅ **R2 不自签 Gate** — P35-00 Plan 由 Kogami 签 `GATE-P35-PLAN: Approved`（含 Q1=C / Q2=A / Q3=B / Q4=A / Q5=A 五项仲裁）；本 closure 等 `GATE-P35-CLOSURE: Approved`；相关历史 Gate（P31-GATE / GATE-P32-CLOSURE / GATE-P34-CLOSURE）均由 Kogami 2026-04-20 人工显式签字
- ✅ **R3 Tier 1 adversarial** — P35-00 Plan §4「Tier 1 对抗性自审」已交 5 条 counterargument（C1-C5）+ 就地缓解：C1（banner 遗忘）↔ W3 regression guard；C2（runtime API 无感知）↔ 承认+分 Phase；C3（冻结语义模糊）↔ 明示定义；C4（P35/P36 顺序）↔ registry row 升级设计；C5（banner 文字风险）↔ Q5=A 逐字签。
- ✅ **R4 不自选下一 Phase 方向** — P35α 由 Kogami 2026-04-20 明示指令 "D · 证迹补完第二轮" 发起；下一 Phase 方向（P36β thrust_reverser docx 真实化）留给 Kogami 在 P35 closeout 后 **再次明示**（Plan §11 已注）
- ✅ **R5 证迹先行** — 本 Phase 本身就是「证迹先行」的第二轮；3 adapter "无上游源" 是 Kogami 2026-04-20 chat 明示口径，banner + registry 把这一事实锚为可审计；3 demonstrative adapter 的现有 behavior/tests/YAML 数字均 **未触动**，等后续 Phase 有上游规格时再真实化

## Q1-Q5 仲裁落地结果

| Open Question | Kogami 仲裁 | 落地位置 |
|---|---|---|
| Q1 · truth_level enum 命名 | **C** · `demonstrative / certified / placeholder` + 独立 `status` 字段（本质状态分离）| `docs/provenance/adapter_truth_levels.md` §Truth Level Schema |
| Q2 · banner 存放位置 | **A** · adapter module docstring + YAML head comment | P35-02 commit (7 files) |
| Q3 · efds 是否补 stub intake/yaml | **B** · 不补（冻结即不新增）| P35-02 commit 不包含 efds_intake_packet.py / efds_hardware_v1.yaml |
| Q4 · thrust_reverser 登记 level | **A** · `demonstrative` + `status: Upgrade pending`（P36β 升级）| `docs/provenance/adapter_truth_levels.md` row 1 |
| Q5 · banner 文字内容 | **A** · 接受 Plan §6 草案字节级 | P35-02 commit (3 版 banner 分别落在 adapter/intake/yaml) |

## Tier 1 5 条反驳落地结果

| 反驳 (来自 P35-00 Plan §Counterargument Pre-check) | 缓解 |
|---|---|
| C1 · banner 是纯注释，1 年后会被遗忘或删掉 | `tests/test_adapter_freeze_banner.py` 15 parametrized cases · CI default lane 每跑必查 · 删 banner → 立即红 |
| C2 · docs 层 banner 不入 runtime API / 前端，demo 场景仍可能误读 | 承认 gap 真实；超出 P35α scope（non-goal 明列）；runtime 层升级留给未来独立 Phase；registry 文件是升级锚点 |
| C3 · "冻结搁置"语义模糊 —— 3 adapter 还能被 api/demo 调用吗 | `docs/provenance/adapter_truth_levels.md` §下游使用者须知 明示"冻结 = 不新增真实化证迹"；现有 smoke/API 保持运行（否则违反 P34 non-goal + Kogami 明说"不影响继续开发"）|
| C4 · P35α / P36β 顺序 | Registry row 1（thrust-reverser）设计为 `demonstrative + Upgrade pending`；P36β 收口时 in-place 改 1 行升级。本 Phase 不前置 P36β 任何动作 |
| C5 · banner 文字对外声明影响大 | Q5=A 逐字签；三版 banner 文字（adapter docstring / intake docstring / yaml head）分别定稿 in Plan §6 |

## Notion DECISION 草案（等 GATE-P35-CLOSURE 后贴入控制塔）

**目标页**：控制塔 `33cc68942bed8136b5c9f9ba5b4b44ec`（P34 DECISION 同页）

**块内容：**

```markdown
## P35 DECISION · v5.2 solo-signed (2026-04-20) · Adapter Truth-Level Registry + Freeze Banner

**Phase**: P35α — 证迹补完第二轮 α 段
**Status**: Executed & Green; Awaiting GATE-P35-CLOSURE (Kogami)
**Gates**: `GATE-P35-PLAN: Approved` (Kogami 2026-04-20, Q1=C/Q2=A/Q3=B/Q4=A/Q5=A) · `GATE-P35-CLOSURE: Pending`

### Directive context

Kogami 2026-04-20: 方向指令 D · 证迹补完第二轮；披露 bleed_air/efds/landing_gear "是之前随便生成的逻辑面板，没有需求文档，当作没来源冻结搁置，不影响继续开发"。

### Artefacts (git-tracked, branch `codex/p35-adapter-truth-level-registry` base main c88e4f0)

- Plan: `.planning/phases/P35-adapter-truth-level-registry/P35-00-PLAN.md` (315 行 · commit `c886e14`)
- Closure: `.planning/phases/P35-adapter-truth-level-registry/P35-05-CLOSURE.md` (本文档 · commit 待 P35-05)
- Registry: `docs/provenance/adapter_truth_levels.md` (101 行 · 5 rows · schema C · commit `5a7e7b1`)
- Banner files (7): bleed_air_adapter.py / bleed_air_intake_packet.py / efds_adapter.py / landing_gear_adapter.py / landing_gear_intake_packet.py / bleed_air_hardware_v1.yaml / landing_gear_hardware_v1.yaml (commit `6cc0d31` · +76 行)
- Test: `tests/test_adapter_freeze_banner.py` (88 行 · 15 parametrized cases · commit `e0f8a8a`)

### Regression evidence (三轨)

- default pytest: **762 passed** / 1 skipped / 49 deselected in 119.24s (P34 baseline 747 + 15 P35-03 · 零既有回归)
- opt-in e2e: **49 passed** / 763 deselected in 2.71s (identical to P34 baseline)
- adversarial wrapper: **1 passed** in 0.25s (8/8 inside identical)

### Registry 5 rows

| system_id | truth_level | status |
|---|---|---|
| thrust-reverser | demonstrative | Upgrade pending (P36β) |
| bleed-air-valve | demonstrative | Frozen (2026-04-20) |
| emergency_flare_deployment_system | demonstrative | Frozen (2026-04-20) |
| minimal_landing_gear_extension | demonstrative | Frozen (2026-04-20) |
| c919-etras | certified | In use |

### Q1-Q5 resolution

- Q1-C · truth_level (demonstrative/certified/placeholder) + 独立 status
- Q2-A · banner 在 docstring + YAML head comment
- Q3-B · efds 不补 stub
- Q4-A · thrust_reverser 登 demonstrative + Upgrade pending
- Q5-A · banner 文字逐字稿接受

### Tier 1 counterargument coverage

All 5 counterarguments from P35-00 Plan §4 mitigated; see closure §Tier 1 5 条反驳落地结果。

### Next phase

P36β (thrust_reverser docx 真实化) — 等 Kogami 在 P35 closeout 后 **再次明示** 推进（R4：不自选）。

Execution-by: opus47-claudeapp-solo · v5.2
```

## 待 Kogami 的一个 Gate 签字

### `GATE-P35-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P35 branch 可以合入 origin/main。

**Executor 在 Gate 签字后执行**（一次性脚本，同 P34 Option M 模式）：

1. `git checkout main` · `git fetch origin` · `git merge --no-ff codex/p35-adapter-truth-level-registry -m "..."` · `git push origin main`（SHA 保留：`c886e14` / `5a7e7b1` / `6cc0d31` / `e0f8a8a` / 待写的 P35-05 closure commit）
2. Notion 控制塔页 `33cc68942bed8136b5c9f9ba5b4b44ec` append 上方 "Notion DECISION 草案"（并 flip "Pending" → "Approved (Kogami YYYY-MM-DD)"）
3. 向 Kogami 请示 P36β 方向是否推进

## 风险与已知 gap

| 事项 | 状态 | 处置 |
|------|------|------|
| Runtime API 不感知 truth_level（demo_server / 前端 / registry API 返回）| 已知 gap（C2）| 留给未来独立 Phase（Plan §4 C2 已记）；当前 docs 层 banner 是必要但非充分防护 |
| P34 PDF 实际不在 repo `uploads/`（P34 intake aspirational 路径）| 已知 gap | 建议 P36β 或单独 Phase 一并入库；P34 证迹闭环尚缺这一步 |
| `uploads/` 目录当前不存在 | 已知 gap | 同上；P36β 执行时创建 |
| thrust_reverser docx 进入 repo | 未做 | P36β 执行时入库（D2=C）|
| Level 升级流程未走实战 | 未做 | P36β 完整演示 demonstrative → certified 升级路径 |

## Kogami-local 残留（参考 · 本 Phase 已顺手清）

P35α 起草前已执行 §4 cleanup（Kogami 2026-04-20 "optional 全部按建议"授权）：
- ✅ `git push origin --delete codex/p30-explain-runtime-sync`
- ✅ `git branch -d codex/p34-c919-etras`（本地已 merged）
- ✅ `rm -rf .claude/worktrees/{blissful-brown-b2606d, charming-babbage-19cfa2, sad-mendel-e5676f}`
- ✅ `git stash drop stash@{0}`（P31/P32 carryover，内容已全部 on main · 无数据损失）

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P35-CLOSURE: Approved` (Kogami)
