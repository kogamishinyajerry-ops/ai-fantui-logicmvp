---
phase: P32
plan: P32-05
title: Closure — 证迹补完完成，等 Kogami GATE-P32-CLOSURE
status: drafted · Pending GATE-P32-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
---

# P32 · 证迹差距补完 — Closure

## 执行摘要

Kogami 2026-04-20 指令「先补证迹差距，再补能力差距」 + `GATE-P32-PLAN: Approved` 后，P32 按 plan 顺序 P32-01 → P32-05 完成 W2–W6 六项证迹工作（W1 P31 Gate 收口留作 P32-07，等 Kogami 单独写 `P31-GATE: Approved`）。

**三轨回归零回归**，与 P31 re-land 基线字节级一致。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact |
|---|------|------|---------------|
| W1 | P31 Gate 收口（FF merge + Codex 分支清理） | **Pending Kogami `P31-GATE: Approved`** | 待 — 将在 Gate 后由 Executor 执行 |
| W2 | P17–P20 audit footnote（`.planning/ROADMAP.md`） | ✅ Done | ROADMAP line 368/391/408/432 新增 4 处 footnote；line 452 P21 footnote 原有保留 |
| W3 | Milestone 9 Project Freeze Lifted 追认（`.planning/constitution.md`） | ✅ Done | constitution.md 新增 `## Milestone 9 — Project Freeze → Lifted` 段 + Governance Mode Timeline 段 |
| W4 | P17 Unfreeze Application 定性 Superseded by P19 | ✅ Done | `docs/unfreeze/P17-application-draft.md` 顶部加 Status 标头；文件主体未改 |
| W5 | 外部 roadmap-2026H2 改前缀 H2-23 ~ H2-27 | ✅ Done | roadmap-2026H2.md 全文换前缀 + sla-draft.md 3 处 + 内部 ROADMAP P23-04 交叉引用 + P23 plan doc 交叉引用 |
| W6 | Constitution v2.1（两份 constitution 升版） | ✅ Done | `.planning/constitution.md` Phase Registry 补 P12-P32 + v5.2 Solo Mode 红线段；`docs/architecture/constitution-v2.md` 升 v2.1 + Level 1/2 未验证明示 + v5.2 纪律段 |

## 三轨回归证据

所有三轨在 P32 W2-W6 所有文档改动完成后跑，与 P31 re-land `25f64fe` 基线对比：

### 默认 pytest lane

```
PYTHONPATH=src MINIMAX_KEY_FILE=~/.minimax_key python3 -m pytest --tb=no -q
→ 684 passed, 1 skipped, 49 deselected, 104 subtests passed in 51.97s
```

**Delta vs P31 baseline:** 0 · identical

### Opt-in e2e lane

```
PYTHONPATH=src MINIMAX_KEY_FILE=~/.minimax_key python3 -m pytest -m e2e --tb=no -q
→ 49 passed, 685 deselected in 1.52s
```

**Delta vs P31 baseline:** 0 · identical

### Adversarial live lane

```
WELL_HARNESS_PORT=8799 PYTHONPATH=src MINIMAX_KEY_FILE=~/.minimax_key python3 src/well_harness/static/adversarial_test.py
→ ALL TESTS PASSED (8/8)
```

**Delta vs P31 baseline:** 0 · identical

**解读：** P32 只动治理/证迹文档，code/tests/scripts 零改动。三轨等于基线是预期结果；若有 delta 反而说明意外污染。本基线再次确证 P32 的非侵入性。

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — W1 P31 Gate 收口被显式放到 P32-07 最后，等 Kogami 签；W2-W6 全部在 scratch clone branch `feat/p32-provenance-backfill` 上，未触碰 workspace mount 的 main
- ✅ **R2 不自签 Gate** — P32 DECISION 引用 `GATE-P32-PLAN: Approved` 为 Kogami 签字；Closure 本文档等 `GATE-P32-CLOSURE: Approved`
- ✅ **R3 Tier 1 adversarial** — plan doc §「Counterargument Pre-check」已写 5 条反驳 + 就地反驳；本 closure 不额外自审（plan 已覆盖）
- ✅ **R4 不自选下一 Phase 方向** — P32 执行范围是 Kogami 2026-04-20 指令明示，未自选；下一 Phase 方向留给 Kogami 在 P32 closeout 后给新指令
- ✅ **R5 证迹先行** — P32 本身就是执行「证迹先行」原则的第一个 Phase；为未来能力 Phase 清理前置条件

## 代码侧 invariants（自审确认）

P32 branch 的 `git diff feat/p31-orphan-triage..feat/p32-provenance-backfill --stat` 应显示的文件域：

- ✅ `.planning/ROADMAP.md`（W2 footnotes + W5 P23-04 交叉引用）
- ✅ `.planning/constitution.md`（W3 + W6 主体）
- ✅ `.planning/phases/P23-co-development-kit/P23-00-TIER1-PLAN.md`（W5 交叉引用）
- ✅ `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`（新增）
- ✅ `.planning/phases/P32-provenance-backfill/P32-05-CLOSURE.md`（新增，本文件）
- ✅ `docs/architecture/constitution-v2.md`（W6 升版）
- ✅ `docs/co-development/roadmap-2026H2.md`（W5 主文件改前缀）
- ✅ `docs/co-development/sla-draft.md`（W5 3 处交叉引用）
- ✅ `docs/unfreeze/P17-application-draft.md`（W4 Superseded 标头）

**不应该出现：** `src/**` / `tests/**` / `scripts/**` / `tools/**` / `config/**` 任何文件。如出现即违反 P32 non-goal。

## 待 Kogami 的两个 Gate 签字

### 1) `GATE-P32-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P32 commit 可以合入上游。

### 2) `P31-GATE: Approved`（W1 前置）

触发动作：Executor 执行 W1 —
- `git fetch <bundle> feat/p32-provenance-backfill:feat/p32-provenance-backfill`（带 P31 父提交 + P32 增量）
- `git checkout main && git merge --ff-only feat/p32-provenance-backfill`（main HEAD 前进到 P32 commit）
- `git push origin --delete codex/p30-explain-runtime-sync`（远端 Codex 残留分支清理）
- `rm -rf .claude/worktrees/`（workspace mount 的 Codex worktree 残留清理）
- `git log --format=fuller` 截图，证据挂 Notion 的 P31 节点

**两个 Gate 顺序可以任意 —— 先签哪个都不阻塞另一个**，但 W1 真正执行需要两个都 Approved。

## Notion 治理同步计划

GATE-P32-CLOSURE 签字后，Executor 会：
1. 控制塔页面（`33cc68942bed8136b5c9f9ba5b4b44ec`）追加 `## P32 DECISION · v5.2 solo-signed (2026-04-20) · 证迹补完`
2. 挂链：plan doc · closure doc · P31 bundle · P32 extended bundle · 三轨回归 log
3. Phase Registry 数据库（Notion）补 P32 行

task #15 (P32 Notion sync) 留在 Kogami Gate 后执行。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P32-CLOSURE: Approved` (Kogami) · `P31-GATE: Approved` (Kogami, W1 前置)
