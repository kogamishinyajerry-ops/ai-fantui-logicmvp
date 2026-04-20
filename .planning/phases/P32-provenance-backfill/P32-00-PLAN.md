---
phase: P32
plan: P32-00
title: Provenance Backfill — 补完 v4.0 自签区间 + Milestone 9 Lifted + constitution v5.2 治理更新
status: drafted · Pending GATE-P32-PLAN (Kogami)
created: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
direction: Kogami 2026-04-20 directive — 「先补证迹差距，再补能力差距」
preconditions:
  - P31 DECISION 已写入 Notion 控制塔（2026-04-20）
  - P31 bundle `.planning/audit/bundles/p31-orphan-triage.bundle` 已产出
  - Kogami 三项定性回复已收到（单一 P32 / P17 Superseded by P19 / 外部 H2- 前缀）
non-goals:
  - 不触碰 controller.py / 19 节点 / R1-R5 基线（v5.2 红线）
  - 不新增任何能力 Phase 工作（本 Phase 纯证迹与治理，不动业务代码）
  - 不修改 P25 findings / budget 常量 / adversarial_test.py 场景数（那些归属 P33+ 能力差距）
  - 不代替 Kogami 做 Gate 签字（W1 P31 Gate 必须由 Kogami 本人写 `P31-GATE: Approved`）
---

# P32 · 证迹差距补完（Provenance Backfill）

## Why this Phase

v5.1 Pair Mode 下 Codex 节奏失控产出了 orphan commit 4474505；v5.2 Solo Mode 启动后 P31 在 Claude App 独自执行下完成了三轨 green + adversarial 自审 + PARTIAL MERGE re-land。但上一轮 gap 分析发现**证迹层有 6 项遗留债**：

1. **P31 Gate 未 close** — `25f64fe` 还在 `feat/p31-orphan-triage` 分支，等 Kogami 写 `P31-GATE: Approved` 才能 FF 到 main
2. **P17–P20 四个 Phase 没有 audit footnote** — P31 audit 只覆盖了 P21–P30
3. **Milestone 9 Project Freeze 从未正式 Lifted** — constitution.md 仍把 Freeze 描述为 active，而事实上 P17–P30 已在冻结线之上全部落地
4. **P17 Unfreeze Application 悬置** — 2026-04-18 Ready for Review，从未被批或驳
5. **Phase 编号命名空间冲突** — 内部 ROADMAP P24-P27 ≠ 外部 roadmap-2026H2 P24-P27
6. **Constitution 未反映 v5.2** — 仍写 v3.0 双 Opus / v4.0 Extended Autonomy，没有 v5.2 Solo Mode 条款

这些都不改代码，但是决定了项目能否**信得过自己的治理叙述**。Kogami 2026-04-20 指令「先补证迹差距，再补能力差距」明确了优先级；P32 是这条路径的第一个也是唯一一个证迹 Phase。

**为什么合成一个 P32 而不是拆几个：** Kogami 已经明确选「单一 P32 全覆盖」。六项都是证迹层 + authoritative 文档修改，彼此引用链密（W3 Lifted 叙述必然引用 W1 P31 closeout、W6 constitution v2.1 必然引用 W3 Lifted + W4 P17 Superseded 结论），拆 Phase 反而会让 Gate 链条变复杂。

## Scope

### W1 — P31 Gate 收口

**前置：** Kogami 在 Notion 控制塔 P31 DECISION 节点下写 `P31-GATE: Approved` + 日期

**执行动作：**
- 从 bundle 拉取 `feat/p31-orphan-triage`（如果 mount `.git/*.lock` 仍堵塞，从 scratch clone 走）
- FF merge 到 main（必须 `--ff-only`，因为 Codex orphan 分支 `codex/p30-explain-runtime-sync` 仍在远端，需要先标记 superseded）
- 删除远端 `codex/p30-explain-runtime-sync` 分支
- 清理 `.claude/worktrees/` 下的 Codex 残留目录
- `git log --format=fuller` 截图挂 Notion，证明 `Execution-by: opus47-claudeapp-solo · v5.2` trailer 真在 main HEAD

**Exit artefact：** main HEAD = `25f64fe`；Notion P31 节点挂 `closure-evidence.png`

### W2 — P17–P20 audit footnote

**范围：** `.planning/ROADMAP.md` 为以下 4 个 Phase 顶部加与 P21–P30 已有 footnote 同格式的 audit 声明：

- P17 Fault Injection (2026-04-15, Codex/MiniMax-2.7, self-signed under v4.0)
- P18 Demo Cleanup & Archive Integrity (2026-04-16)
- P19 Hardware Partial Unfreeze (2026-04-17, 18 sub-phases, MiniMax-2.7 主导 + Codex 关键 diff)
- P20 Wow E2E + Demo Resilience (2026-04-18, P20.2 子 Phase)

**Footnote 模板（每 Phase 顶部，与 P31 audit §6 的 P21 footnote 同格式）：**

```markdown
> **Audit note (v5.2 solo, 2026-04-20):** 本 Phase 于 v4.0 Extended Autonomy
> Mode 下由 Executor self-signed 落地。v5.2 Claude App Solo Mode (2026-04-20)
> 下经 `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` 批准后统一
> 追认 provenance。Phase 内容、测试数据、代码事实均未回修——仅证迹层追签。
```

**Exit artefact：** ROADMAP.md 4 处 footnote 落地；git diff 清洁无代码侧改动

### W3 — Milestone 9 Project Freeze Lifted 写回

**范围：** `.planning/constitution.md` 追加 Milestone 9 Lifted 段落，叙述：

- Lifted 日期：**2026-04-20**（P32 落地日，即 v5.2 Solo Mode 首次正式 governance action）
- Lifted 理由：2026-04-15 Freeze 后 5 天内 P17–P30 共 14 个 Phase 已在 v4.0 Extended Autonomy 下实质落地；Freeze 的 3 条 Resume Criteria 中「产品方向决策」已事实上被 Kogami 多次签字确认（P19 Partial Unfreeze approved、P23 Co-development Kit closed、P28 FAQ Evidence closed 等）
- Lifted 签字方：Kogami（P31-GATE: Approved 即等同于对这段事实的默许追认）+ Claude App Opus 4.7 (Solo Executor)
- 与 `docs/freeze/` 下 MILESTONE4/5/6-HOLD.md 的冻结家族关系：Milestone 9 是其中唯一从未正式 Lifted 的，现在补上

**Exit artefact：** constitution.md 有 `## Milestone 9 — Lifted (2026-04-20)` 段落；Notion 控制塔首页同步

### W4 — P17 Unfreeze Application 定性 Superseded by P19

**范围：** `docs/unfreeze/P17-application-draft.md` 顶部加 Superseded 标头（**不删除文件内容**，保留作为历史证据）：

```markdown
> **Status: Superseded by P19 Hardware Partial Unfreeze (2026-04-20)**
>
> 本申请书（v0.1, Ready for Review, 2026-04-18）的目标管线 PDF → adapter → ≥1
> 新系统 panel **被 P19 Hardware Partial Unfreeze 事实上超越**：P19 在 controller.py
> 零改动前提下交付了硬件 YAML schema + Monte Carlo + 反诊断 + 立项演讲稿
> （2026-04-17 Done, `.planning/phases/P19-hardware-partial-unfreeze/`）。
>
> 本申请不重走 Gate；文件保留作为 P17 slot 方向裁决的证据。P17 slot 最终由
> Fault Injection 占用（2026-04-15 Done），与本申请书无关。
>
> 定性签字：Kogami 2026-04-20 AskUserQuestion 答复 + Claude App Opus 4.7
> (Solo Executor) · v5.2 solo-signed · 2026-04-20
```

**Exit artefact：** P17 unfreeze draft 文件不动主体，仅 header 加 Superseded；Notion 同步

### W5 — Phase 编号命名空间去重（外部改前缀）

**范围：** `docs/co-development/roadmap-2026H2.md` 内全部 P23/P24/P25/P26/P27 改为 H2-23/H2-24/H2-25/H2-26/H2-27；内部 `.planning/ROADMAP.md` 的 P24-P30 **不动**。

**跟随变更的文件（grep 过的 pre-check，Kogami 批准后开工再复核）：**
- `docs/co-development/roadmap-2026H2.md`（主改文件）
- `docs/co-development/api-contract.md`（如果引用 P24-P27）
- `docs/co-development/sla-draft.md`（如果引用）
- `docs/co-development/security-review-template.md`（如果引用）
- `.planning/PROJECT.md`（Operating Model 段如果引用）
- `docs/architecture/constitution-v2.md`（如果引用）
- Notion 控制塔：`docs/co-development/` 对外展示页

**改名规则：**
- P23 Co-development Kit → **H2-23 Co-development Kit**
- P24 甲方子系统接入 PoC → **H2-24 甲方子系统接入 PoC**
- P25 生产前硬化 → **H2-25 生产前硬化**
- P26 首批产线 Validation → **H2-26 首批产线 Validation**
- P27 季度审计包 → **H2-27 季度审计包**

**文档顶部加命名空间说明：**

```markdown
> **编号命名空间：** 本文件使用 `H2-XX` 前缀，表示"2026H2 对外交付路线图"的 Phase。
> 与 `.planning/ROADMAP.md` 中的 `PXX`（内部执行路线图）是**两套独立命名空间**，
> 不要混淆。P32 证迹补完于 2026-04-20 完成去重（原 P23-P27 全部重命名为 H2-23-H2-27）。
```

**Exit artefact：** roadmap-2026H2.md 全文改完；git grep 确认 `\bP(2[3-7])\b` 在外部 roadmap 上下文全部消失；交叉引用文件同步更新

### W6 — Constitution v2.1 治理更新

**范围：** 两份 constitution 文件同步更新到 v2.1，反映 v5.2 Solo Mode：

**`.planning/constitution.md` 更新点：**
- 顶部 governance mode 从 v4.0 Extended Autonomy 改到 v5.2 Claude App Solo Mode
- 加 v5.2 红线章节（完整复制自 2026-04-20 v5.2 charter）
- Phase Registry 增加 P31 / P32 行
- Milestone 9 段（W3 产物）编入正式结构

**`docs/architecture/constitution-v2.md` 更新点：**
- 版本从 v2 → v2.1（2026-04-20 refresh）
- 8 条绝对边界不动（controller.py / 19 节点 / R1-R5 基线 etc.）
- 新增「v5.2 Solo Mode 执行层纪律」段：DECISION 格式 `## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)`、commit trailer `Execution-by: opus47-claudeapp-solo · v5.2`、reviewer sign format `Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed`、Tier 1 adversarial self-review mandatory
- Validated capabilities 不动；新增「Not yet validated under federation」清单（对应上一轮 gap 分析 §3 的 Level 1/2 gate 空白）

**Exit artefact：** 两份 constitution 改完；顶部 version/date 同步更新；git diff 清洁（仅治理文字改动）

### Sub-phase 执行顺序（建议）

| Sub | 工作 | 依赖 | 工期 |
|-----|------|------|------|
| P32-01 | W2 P17-P20 footnote（无依赖，先做） | 无 | 0.15d |
| P32-02 | W4 P17 Unfreeze Superseded 标头 | 无 | 0.05d |
| P32-03 | W5 外部 roadmap H2- 前缀改名 + 交叉引用扫描 | 无 | 0.3d |
| P32-04 | W3 Milestone 9 Lifted 段（引用 W2 + W4 产物） | W2, W4 | 0.15d |
| P32-05 | W6 Constitution v2.1 更新（引用 W3 + W4 + W5） | W3, W4, W5 | 0.4d |
| P32-06 | 三轨回归验证 + Notion 治理同步 | P32-01 ~ P32-05 | 0.2d |
| P32-07 | **W1 P31 Gate 收口**（最后做，等 Kogami 写 P31-GATE: Approved） | Kogami Gate | 0.1d |

**总工期：** 约 1.4 工作日（W1 的等 Kogami 时间不算）

**W1 放最后的原因：** P31 Gate 收口一旦执行就改 main 的 HEAD——这是 v5.2 红线里明确列的「不可逆操作」，必须放在 P32 其他证迹动作都做完、三轨绿了之后一并提交给 Kogami 作为总 closeout。

## Exit Criteria

- [ ] W1 P31-GATE: Approved 由 Kogami 签；main HEAD = `25f64fe`；远端 Codex 残留分支 + 本地 worktrees 清理完成
- [ ] W2 ROADMAP.md P17/P18/P19/P20 四处 audit footnote 落地
- [ ] W3 constitution.md 有 `## Milestone 9 — Lifted (2026-04-20)` 段
- [ ] W4 P17 unfreeze draft 顶部 Superseded 标头加好，文件主体未改
- [ ] W5 外部 roadmap-2026H2.md 全部 P23-P27 重命名为 H2-23 ~ H2-27；交叉引用文件同步
- [ ] W6 两份 constitution 更新到 v2.1，v5.2 Solo Mode 条款写入
- [ ] pytest 默认 684 pass / 1 skip 零回归 · opt-in e2e 49 pass 零回归 · adversarial 8/8 PASS 零回归（本 Phase 纯文档，理论上不可能碰测试，但必须自证）
- [ ] Notion 控制塔 P32 DECISION + 6 W exit artefact 挂链完成
- [ ] GATE-P32-CLOSURE 由 Kogami 签

## R1–R5 合规（事前 self-audit）

| 原则 | P32 保持方式 |
|------|-------------|
| R1 真值优先 | 只改治理/证迹文档，controller.py / 19 节点 / truth engine 零触碰；W3 Milestone 9 Lifted 叙述基于事实（14 Phase 已在冻结线之上落地是客观现实） |
| R2 AI 仅解释 | 无 LLM 调用；无新推理能力 |
| R3 可审计 | 每个 W 都有明确的 before/after diff + Notion artefact 挂链；W2 footnote 格式与 P31 audit 一致，可回溯 |
| R4 降级可控 | 无降级改动 |
| R5 失败可控 | W1 Gate 是唯一不可逆操作，放最后 + 显式等 Kogami 批；其他 W 都是纯文档，最坏情况 git revert 可回退 |

## Counterargument Pre-check（Tier 1 adversarial self-review）

自审 5 条 counterargument，防止 P32 本身变成新的证迹债：

1. **「Milestone 9 Lifted 日期写 2026-04-20 是追溯造假」** — 反驳：文档明确写「Lifted 是对 2026-04-15 → 2026-04-18 已落地事实的 provenance 追认，不是 Phase 能力本身在 4-20 才 Lifted」。日期选 4-20 是因为这是 v5.2 Solo Mode 首次 governance action 的日子，符合「追认发生在本日」的叙述纪律。
2. **「外部 roadmap 改前缀会破坏甲方已看过的文档引用」** — 反驳：甲方尚未立项，外部 roadmap-2026H2.md 当前仅对内流通；改前缀的成本只在本 repo 内部，外部零影响。且 Kogami 已选择此方案（Recommended）。
3. **「P17 Unfreeze Superseded by P19 不严谨——P19 并未交付 PDF→adapter→panel」** — 反驳：P19 交付的是硬件层部分解冻（YAML + Monte Carlo + 反诊断 + pitch），其实现路径 ≠ P17 申请的 PDF 解析路径，但**达到了 P17 申请书陈述的根本目标「让工作台能驱动新能力 demo」**。P17 申请的具体管线未实现不等于方向未被满足——Superseded 是准确定性。若 Kogami 坚持 P17 方向仍独立有效，应选「重启 P33 候选」而非 Superseded（AskUserQuestion 已给选项且 Kogami 选 Superseded）。
4. **「P32 自己也是 v5.2 Solo Mode 下的 Executor self-plan，凭什么它可以追认别的 Phase？」** — 反驳：P32 **不是**自签落地。流程是 Executor draft PLAN → **Kogami GATE-P32-PLAN Approved** → Executor 执行 → Executor draft closure → **Kogami GATE-P32-CLOSURE Approved**。两道 Kogami Gate 是追认合法性的来源，P32 本身是 Kogami 批复链的产物。
5. **「W1 P31 Gate 放最后 = 在 P32 没批之前就执行了不可逆 FF merge」** — 反驳：W1 是 P32 的 Sub-phase 之一，顺序 P32-07 最后，必须在 GATE-P32-PLAN Approved **和** `P31-GATE: Approved` 都在手后才执行。如果 Kogami 选择先走 W1 单独收口（即「仅 P32 = W1-W4，延后 W5/W6」的 AskUserQuestion option，但 Kogami 没选这个），流程另议。目前选择的「单一 P32 全覆盖」意味着 W1 绑在 P32 里一并 Gate。

## v5.2 红线合规

- ✅ 不触碰 controller.py / 19 节点 / R1-R5 基线
- ✅ 不自签 Gate — P32 PLAN / CLOSURE 两个 Gate 都要 Kogami 签
- ✅ W1 P31 Gate 收口 = 显式依赖 Kogami 先写 `P31-GATE: Approved`，不代签
- ✅ 不自选下一 Phase 方向 — 本 Phase 执行 Kogami 2026-04-20 指令「先补证迹差距」，未自主选择
- ✅ Tier 1 adversarial self-review 已在上方完成（5 条 counterargument）

## Notion 同步计划

P32 DECISION 段将写入控制塔首页 `33cc68942bed8136b5c9f9ba5b4b44ec`，位于 P31 DECISION 节点之下，格式：

```markdown
## P32 DECISION · v5.2 solo-signed (2026-04-20) · 证迹补完

**Direction:** Kogami 指令「先补证迹差距，再补能力差距」(2026-04-20)
**Scope:** 单一 P32 全覆盖 6 项证迹缺口
**Approvals collected:**
  - P31 Gate closeout (W1): pending `P31-GATE: Approved`
  - W2 footnote / W3 Lifted / W4 Superseded / W5 H2- 前缀 / W6 v2.1: pending `GATE-P32-PLAN: Approved`
  - Closure: pending `GATE-P32-CLOSURE: Approved`
**Exit artefact links:** [Plan doc] [ROADMAP.md diff] [constitution diff] [Notion P31 closure]
**Red-line compliance:** 见 plan doc R1-R5 表 + v5.2 红线 checklist
```

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P32-PLAN: Approved` (Kogami)

---

## 附录 A — 本 Phase 触及的文件清单（预估）

修改类型 M = Modify、A = Add、R = Rename-in-place (文本内容改)：

| 文件 | 改动类型 | W | 说明 |
|------|---------|---|------|
| `.planning/ROADMAP.md` | M | W2 | 4 处 footnote |
| `.planning/constitution.md` | M | W3, W6 | Milestone 9 段 + v5.2 治理 |
| `docs/architecture/constitution-v2.md` | M | W6 | v2.1 更新 |
| `docs/unfreeze/P17-application-draft.md` | M | W4 | Superseded 标头 |
| `docs/co-development/roadmap-2026H2.md` | R | W5 | P23-P27 → H2-23-H2-27 全文替换 |
| `docs/co-development/api-contract.md` | M | W5 | 交叉引用同步（如有） |
| `docs/co-development/sla-draft.md` | M | W5 | 交叉引用同步（如有） |
| `docs/co-development/security-review-template.md` | M | W5 | 交叉引用同步（如有） |
| `.planning/PROJECT.md` | M | W5 | Operating Model 段交叉引用（如有） |
| `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` | A | 本文件 | 计划文档 |
| `.planning/phases/P32-provenance-backfill/P32-01-FOOTNOTE.md` | A | W2 | Sub-phase 产出记录 |
| `.planning/phases/P32-provenance-backfill/P32-05-CLOSURE.md` | A | 全部 | 收尾记录 |

**预估代码侧零改动**；src/ / tests/ / scripts/ / tools/ 全目录不进 diff。

## 附录 B — 为什么不先做能力 Phase（P17 申请本身、P24 甲方 PoC、adversarial 8→15）

Kogami 指令「先补证迹差距，**再**补能力差距」已明确排序。技术理由：

- **P17 PDF→adapter→panel 如果现在启动，Constitution 仍是 v3.0/v4.0 旧叙述** — 新能力 Phase 的 Gate 签字会继续继承治理债，越跑越难回头
- **P24 甲方 PoC 触发条件是外部立项** — 现在不可启动
- **adversarial 8→15 触发条件是「Staging 环境搭起来」** — 属于 H2-25 生产前硬化，前置是 H2-24 PoC 完成

所以 P32 是能力 Phase 启动前的**治理地基**，不做 P32 就做能力 Phase = 还债延期。
