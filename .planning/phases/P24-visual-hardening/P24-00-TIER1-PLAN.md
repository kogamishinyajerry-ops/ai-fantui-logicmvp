---
phase: P24
plan: P24-00-TIER1
title: 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals surface polish
status: drafted · awaits independent Scope Gate (v3.0 + v3.1)
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); Gate by Notion AI Opus 4.7 (v3.0 + v3.1)
preconditions:
  - P22 立项汇报已过（或至少已排演完毕，话术冻结）
  - P23 Co-development Kit 四份文档已落盘
non-goals:
  - 修改 controller.py / 19-node 真值引擎 / 4 logic gates
  - 修改 LLM adapter（MiniMaxClient / OllamaClient）
  - 修改 AI prompts 或 chat 路由语义
  - 新增 wow 场景或真值路径
  - 重构 state management / data flow（只做 surface 层）
  - 引入新的前端框架或构建工具（保持 vanilla JS）
---

# P24 · 立项后视觉硬化

## Why this Phase

截至 P23，三个前端 surface 已功能完备：
- `demo.html` (1957 行) — Canvas + 三 wow 演示视觉
- `chat.html` (800 行) — AI drawer
- `workbench.html` (876 行) — 日常工程师工作台

这些 surface 长出来的过程是**功能驱动的**（P13–P22），视觉一致性是副产品而非目标。P24 的目标是**在不改变任何行为的前提下**，把三个 surface 的视觉层统一到可交付给甲方的工业级水准——spacing / typography / color tokens / micro-interactions。

**严格不动**：truth engine、LLM adapter、AI 叙述逻辑、wow 路径、state 管理。

## Scope

### 统一设计令牌（prerequisite，P24-01）

抽一份 `src/well_harness/static/design-tokens.css` 作为三个 surface 的唯一视觉源：
- color ramps（neutral / accent / status active/blocked/inactive）
- spacing scale（4/8/12/16/24/32/48）
- typography scale（label/body/title/display 4 级）
- motion tokens（duration-fast/normal/slow · easing 曲线）
- elevation shadows

三个 surface 的 `*.css` 文件里原地替换写死值为 token。**零 HTML 改动，零 JS 改动**，diff 集中在 CSS。

### Surface 级 polish（sub-phases）

| Sub | Surface | 工作日 | 关键产出 | 风险 |
| --- | ------- | ----- | -------- | ---- |
| P24-01 | design-tokens.css + 三 surface CSS token 化 | 1d | 新文件 + 三 .css 替换，视觉零差 | 最低（纯 token 平移） |
| P24-02 | `chat.html` AI drawer polish | 1–1.5d | 消息卡片节奏、流式 indicator、reference 块样式、空态/错误态视觉统一 | 低（独立 surface） |
| P24-03 | `workbench.html` Canvas UI polish | 1.5–2d | 节点/gate SVG 细节、hover/selected 状态层次、侧栏 info card、toolbar 对齐 | 中（工程师日常使用，回归面大） |
| P24-04 | `demo.html` Visuals polish | 2–2.5d | wow_a/b/c 场景视觉升级（不改脚本节奏）、fallback 态视觉、presenter HUD 可读性 | 高（立项汇报已冻结的演示路径） |
| P24-05 | closure | 0.5d | 三轨验证、e2e 截图对比（P22 rehearsal 片段）、04A GATE-P24-CLOSURE 建为 Awaiting Opus 4.7（独立 Gate） | — |

**总工期：** 6–7.5 工作日。

## 依赖的审查（v3.0 双 Opus 精简线）

按 Notion 11 模型分工页 v3.0 (2026-04-18) 生效规则：
- **Codex 已完全移除**（v3.0 rule 31：src/ 写操作无需外部 diff 来源，Opus 直接写）
- 每个 sub-phase 完成后跑主 pytest + opt-in e2e + adversarial，任一退化即回滚
- P24-04 (demo.html) 完成后需对 P22 已冻结的话术和截图做对比 diff；如 presenter 视觉语言偏离话术描述，回滚
- Phase 合并 Gate（P24-05 closure）由 Notion AI Opus 4.7 独立签署（Kogami 人工触发）

## Exit Criteria

- [ ] `design-tokens.css` 是三 surface 的唯一视觉源（grep 检查：无孤立 hex 色、无写死 px spacing）
- [ ] 主 pytest 658/1skip 基线不变
- [ ] Opt-in e2e 49/49 + adversarial 8/8 零回归
- [ ] P22 rehearsal 路径重跑一次，话术/截图无偏离
- [ ] 三 surface 逐屏 before/after 截图归档 `docs/demo/p24-visual-diff/`
- [ ] 04A GATE-P24-CLOSURE 建为 Awaiting Opus 4.7（schema 以"Awaiting Opus 4.6"承载，语义 = 独立 Gate 待审）· 等 Kogami 触发 Notion AI Opus 4.7 独立 Gate 复核（v3.1）
- [ ] ROADMAP.md 追加 P24 条目

## R1–R5 合规（事前 self-audit）

| 原则 | P24 保持方式 |
| ---- | ------------ |
| R1 真值优先 | controller.py / 19-node / 4 logic gates 零触碰；CSS token 纯视觉层 |
| R2 AI 仅解释 | LLM adapter / prompts / chat 路由语义零触碰 |
| R3 可审计 | 每 sub-phase Codex 审查 artefact + before/after 截图全部落盘 |
| R4 降级可控 | fallback UI（minimax_api_key_missing / ollama_unreachable / chat-degraded-notice）视觉必须在 polish 后依然醒目——不要把警告态美化成了 happy path |
| R5 adversarial 守门 | adversarial_test.py 逻辑零触碰；其表现 UI 若被 polish 涉及，visual diff 必须保留"这里在测 AI 是否会被骗"的语言锚点 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | CSS token 化引入视觉回归（色差、间距漂移） | 中 | 演示视觉破坏 | P24-01 完成后三屏 pixel diff 人眼审查 + Codex 审查 |
| R2 | demo.html 节奏被 polish 破坏（P22 话术失效） | 中 | 立项汇报话术对不上演示 | P24-04 每次改动重跑对应 wow e2e，话术关键词（"解锁判断" / "蒙卡评估" / "冲突诊断"）对应的 HUD 元素绝不移动/隐藏 |
| R3 | Opus 单节点盲点（自写自测） | 中 | 视觉回归未自检出，到独立 Gate 才暴露 | 每 sub-phase 完成后强制"反向自审 5 问"：多余 style？layout 漂移？accessibility 丢？state class 丢？动画剥离失败？并截取 before/after 截图归档供 Gate 比对 |
| R4 | 三 surface 并行改动引入合并冲突 | 低 | rebase 成本 | 所有 sub-phase 在 `feat/p24-visual-hardening` 单一 branch 串行 |
| R5 | token 统一迫使某 surface 丢失其必要的视觉语言（如 demo HUD 的高对比度） | 低 | 演示可读性下降 | token 抽取规则：先把三 surface 共性抽成 token，surface 特有值保留 surface-local override |

## 治理 Gate 规则（v3.0 + v3.1）

- Executor 可初审 Scope 并自主推进到 P24-04
- P24-05 closure 不得自签；04A GATE-P24-CLOSURE 建为 Status=Awaiting Opus 4.6
- 跨 Phase 方向性选择 / 宪法 R1-R5 改动 / 不可逆破坏操作 = 停机触发（v3.1 白名单）
- Phase 合并 + Notion AI Opus 4.7 独立 Gate 复核 = 才算 closure

## Scope 初审（Executor pre-review，非 Gate 批准）

Executor 基于以下事实初审：
- P22 话术已冻结；P24-04 必须逐条对照话术
- P23 co-dev kit 文档已落盘；本 Phase 不改接口契约
- Non-goals 清单明确，时间表 6–7.5d 合理
- Exit criteria 目标反推可验证
- 按 v3.0 rule 31，src/ 写操作由 Opus 直接完成，无 Codex 依赖

**这是 Executor 初审，不是 Gate 批准**。Tier 1 Plan Scope Gate 的最终签署由 Notion AI Opus 4.7 在 Kogami 触发时复核。Executor 基于初审自主推进 P24-01 → P24-04，但 Phase 收口（P24-05）不得自签。

---

_Execution-by: opus47-max (Claude Code Opus 4.7, 20x Max) · v3.0 双 Opus + v3.1 停机白名单 · Gate 由 Notion AI Opus 4.7 独立签署_
