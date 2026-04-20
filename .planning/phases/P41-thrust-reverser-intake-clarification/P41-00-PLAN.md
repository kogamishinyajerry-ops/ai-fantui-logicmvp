---
phase: P41
plan: P41-00
title: thrust-reverser intake packet clarification — D1=A Lean 真实语义澄清（scope C）
status: drafted · GATE-P41-PLAN 隐式 Approved (Kogami 2026-04-20 "Go C")
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: P41 原始 "workbench spec builder" scope（基于错误前提 · 见 §1）
preconditions:
  - GATE-P40-CLOSURE Approved (Kogami 2026-04-20) → origin/main at 8989268
  - Kogami 2026-04-20 "Go C" directive（从 A/B/C 菜单明确选 scope C：跳过 workbench spec 新增 · 仅做 docs 澄清）
  - 发现事实：`src/well_harness/system_spec.py:273` `current_reference_workbench_spec()` 早已存在完整 workbench spec（被 controller_adapter.py / cli.py / tests 共 6 处引用）
non-goals:
  - 改 controller.py / models.py / HarnessConfig
  - 改 current_reference_workbench_spec() 本身（已存在、已被引用）
  - 改 adapter pattern 文件结构（不新建 thrust_reverser_adapter.py）
  - rename current_reference_workbench_spec → build_thrust_reverser_workbench_spec（破 6 处 callers）
  - 改 thrust_reverser_intake_packet.py 的 business fields 结构（保留空 tuple 的 D1=A 选择 · P41 只是澄清语义）
  - 改既有 5 adapter / 其他 3 frozen / c919-etras
---

# P41-00 Plan · thrust-reverser intake packet clarification（scope C）

## 0. TL;DR

原 P41 假设 "thrust-reverser 无 workbench spec · 补 D1=A 精益债" 在 scope 起草时扫现有代码被证伪：
- **事实：** `src/well_harness/system_spec.py::current_reference_workbench_spec()` 早已提供完整 workbench spec
- **D1=A Lean 真实语义：** 不是"无 spec"，而是"`thrust_reverser_intake_packet.py` 层面 business fields 保留空 tuple，不走 workbench_spec_from_dict bridge pattern"
- **真实原因：** P36β 起草时 Executor 没 discover 到 `current_reference_workbench_spec()`（命名不带 thrust_reverser 前缀 · 且 adapter 已在 controller_adapter.py 封装）

Kogami 2026-04-20 "Go C" 选最简路径：**跳过 intake 填充 · 仅做 docs 澄清 + 加一个最简 intake regression test**。

**规模：** 约 30 分钟 · 3-4 commits · +2 tests · 0 代码行为变动。

## 1. 发现时间线

| 时间 | 事件 |
|------|------|
| P36β 起草（2026-04-20 早）| Executor 决定 D1=A Lean · 理由"thrust-reverser 无 workbench spec builder，建一个是 scope 风险" |
| P36β-02 落地 | `thrust_reverser_intake_packet.py` business fields = ()，tags 含 `"lean-intake"` |
| P37 起草 | 沿用 D1=A Lean · 未重审前提 |
| P38 起草 | 沿用 D1=A Lean · 未重审前提 |
| P40 收口 | registry / supplement / closure 反复引用 "no workbench spec per D1=A" |
| **P41 起草** | **发现 `current_reference_workbench_spec()` 早已存在** · D1=A 前提错误 |

**教训：** P36β 起草前未穷举现有 `*.py` 里 `ControlSystemWorkbenchSpec` 工厂函数 · 导致 5 Phase 连锁 narrative drift。

## 2. Scope — 3 工作包（scope C · 精简）

### W1 · supplement §8 + §1 澄清（约 10 min）

修 `docs/thrust_reverser/requirements_supplement.md`：
- §1 导言 添加 P41 discovery 注 · 明示 "D1=A Lean 指 intake packet 层 · workbench spec via system_spec.current_reference_workbench_spec 早已存在"
- §8 "与原 docx 和 code 3 方关系" 改为 "4 方关系" · 新增 `current_reference_workbench_spec()` 作为第 4 方 authority source

### W2 · registry row 1 notes 精准化（约 5 min）

修 `docs/provenance/adapter_truth_levels.md` row 1 notes 字段：
- 从 "truth lives in controller.py + yaml (no workbench spec per D1=A)"
- 改为 "truth lives in controller.py + yaml · workbench spec via `system_spec.current_reference_workbench_spec()` (system_spec.py:273) · thrust_reverser_intake_packet.py 保留 Lean (business fields empty) per D1=A intake-layer choice"

### W3 · 新增最简 intake 防回归测试（约 15 min）

新建 `tests/test_thrust_reverser_intake_packet.py`（~40 行 · 2 tests）：
- `test_thrust_reverser_intake_packet_imports_clean` · import + 4 SourceDocumentRef count check
- `test_thrust_reverser_intake_packet_matches_d1a_lean` · business fields (components / logic_nodes / acceptance_scenarios / fault_modes) 都是空 tuple · tags 含 "lean-intake"

（若未来有人意外破 Lean，test 立刻红）

## 3. Non-goals — 严格禁止

已在 frontmatter 明列。强调：
- **不**改 controller.py / models.py / current_reference_workbench_spec
- **不**改 thrust_reverser_intake_packet.py 的 business fields 结构
- **不**改其他 adapter 任何文件
- **不**碰 P34-P40 已签 commit

## 4. Tier 1 对抗性自审（≥3 条，交付 3 条）

### C1 · "D1=A 被证伪了 · P36β/P37/P38 的 closure / registry 已经定型 · 现在改是 ex-post facto 修正"

**承认是事后修正。** 缓解：
1. P41 不改 P36β/P37/P38 任何已落 commit
2. 仅在 registry notes / supplement 层面补澄清注脚 · 不推翻已 signed Gates
3. §1 时间线透明记录发现过程 · 审计可追

### C2 · "为什么不做 scope A（intake packet 填充 business fields）· 那样更一致"

**承认一致性损失。** 缓解：
1. A 会破 thrust_reverser_intake_packet.py 的 Lean 语义（business fields 原本是空 · 填充等于改 D1=A→D1=B）
2. 没有实际下游消费者 · intake packet 目前没被任何 test 或运行时消费（`grep thrust_reverser_intake_packet tests/` = 0 matches）
3. Kogami "Go C" 明确选 scope C · 执行 directive
4. 未来若需 D1=B, 独立 Phase（P44+ 候选）

### C3 · "加 regression test 有没有过度"

**低风险 trade-off。** 缓解：
1. 2 tests 极简 · 纯 import + assert · 无网络/并发/fixture
2. 防回归价值：未来 if intake Lean 被误破 → 测试立刻捕获
3. 也校验 P41 的 4 SourceDocumentRef（P37 added supplement）数量正确 · 防 SourceDocumentRef 漂移

## 5. Sub-phase 分解

- P41-00 · Plan（本文 · ~130 行）
- P41-01 · W1+W2 · supplement §1/§8 + registry row 1 notes 联动（约 15 min · 单 commit）
- P41-02 · W3 · 新 test 文件（约 15 min · 单 commit）
- P41-03 · 三轨（期望 **default 767 passed** = 765 + 2 new · e2e 49 identical · adversarial 1 identical）
- P41-05 · closure + ROADMAP + STATE + Notion DECISION · push

## 6. Exit Criteria

- `docs/thrust_reverser/requirements_supplement.md` §1 + §8 澄清 discover
- `docs/provenance/adapter_truth_levels.md` row 1 notes 精准化
- `tests/test_thrust_reverser_intake_packet.py` 新建 · 2 tests 本地通过
- 三轨：default 767 / e2e 49 / adversarial 1
- ROADMAP + STATE 更新
- Closure drafted · 等 `GATE-P41-CLOSURE: Approved`

## 7. v5.2 红线合规

- R1 非 merge 主分支 · 等 GATE-P41-CLOSURE
- R2 GATE-P41-PLAN 由 Kogami "Go C" 隐式批准（如误读等 Kogami 打断）；GATE-P41-CLOSURE 仍需显式字符串
- R3 3 条 counterargument 就地缓解
- R4 Kogami 明示 P41 方向（选 scope C from 明确菜单）· 下一 Phase 由 Kogami 明示
- R5 P41 本身是 adversarial-driven scope 自纠正 · 透明记录发现过程

## 8. 停点

**本 plan 不 stop** · Kogami "Go C" directive + scope 极小 · Executor 连续执行 P41-01..05。

若 Kogami 要 stop，立刻打断。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Gate:** GATE-P41-PLAN 隐式 Approved（Kogami "Go C" 2026-04-20）· 等 `GATE-P41-CLOSURE: Approved`
