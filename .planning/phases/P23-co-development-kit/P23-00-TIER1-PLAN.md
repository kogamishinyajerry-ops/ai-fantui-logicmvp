---
phase: P23
plan: P23-00-TIER1
title: 立项通过后 Co-development Kit — 接口/安全/SLA/路线图冻结
status: planned
created: 2026-04-18
owner: Executor=Gate (Claude Code Opus 4.7, v3.2 治理折叠)
preconditions: 立项汇报通过（由 Kogami 确认）
non-goals:
  - 修改 controller.py 真值引擎
  - 修改 LLM adapter / AI prompts
  - 新增 wow 场景
  - 承诺具体上线日期（只给路线图区间）
---

# P23 · Co-development Kit — 立项通过后首批交付物

## Why this Phase

立项汇报 (P22) 已全绿落地，物料冻结。**一旦立项通过，需要在 48 小时内把工作台从"项目"切换到"甲方 co-development 基线"**。本 Phase 的目标是**提前把那一刻所需的四份"对接文档"冻结在仓库里**，而不是等甲方工程师到场再现写。

不涉及代码改动 — 全部是 contract / policy / roadmap 文档。

## Scope（严格 Non-goals 已在 frontmatter）

提前冻结四份 co-development 文档：
1. **接口契约清单**（API freeze + 版本策略）
2. **安全评审模板**（甲方用它审每次 PR）
3. **SLA 草案**（可用性、响应时间、数据留存、模型供应链）
4. **长期路线图**（P23–P27 区间展望，给甲方一个"未来 2–3 个季度会发生什么"的视图）

## Sub-phases（4 sub + closure）

| Sub | 交付物 | 说明 |
| --- | ------ | ---- |
| P23-01 | `docs/co-development/api-contract.md` | 冻结当前三哇 API（lever-snapshot / monte-carlo/run / diagnosis/run）+ chat 三端点的请求/响应 schema；加版本策略（v1 不破坏，新 field 只追加） |
| P23-02 | `docs/co-development/security-review-template.md` | 甲方安全工程团队评审每次 PR 时用的 10 项 checklist（R1–R5 锚点 + adversarial 8 项对应 + 数据边界 + supply chain） |
| P23-03 | `docs/co-development/sla-draft.md` | 可用性分级（演示 / 预生产 / 生产）、响应窗口、数据留存政策、AI 模型供应链（MiniMax / Ollama / 甲方自备）3 个 profile |
| P23-04 | `docs/co-development/roadmap-2026H2.md` | P23–P27 路线图：P23 kit / P24 甲方子系统接入 PoC / P25 生产前硬化 / P26 首批产线 validation / P27 审计包 |
| P23-05 | closure Gate + Notion sync | 自签 GATE-P23-CLOSURE（v3.2 Executor=Gate，7/7 合规 checklist） |

## Exit Criteria

- 四份文档全部落 `docs/co-development/`，每份带清晰的"**这份文档给谁看 / 回答什么问题 / 什么情况下会变动**"头部
- 主 pytest / e2e / adversarial 零回归（这是纯文档 Phase，回归应该天然成立）
- ROADMAP.md 有 P23 条目（本 Phase 完成时追加）
- Notion 02B Execution Run + 04A GATE-P23-CLOSURE self-signed + 控制塔 DECISION 块

## 合规 checklist（在 closure Gate 自审）

1. R1 真值优先 — controller.py 零触碰 ✅ （纯文档）
2. R2 AI 仅解释 — 不修改 prompt / LLM adapter ✅
3. R3 可审计 — 所有承诺可映射到 git commit / 真跑 artefact / R 原则
4. R4 降级可控 — SLA 三级 profile 留足降级空间
5. R5 对抗守门 — 安全评审模板复用 adversarial 8 项
6. 三轨零回归（文档 Phase 应自动成立）
7. Non-goals 严守（frontmatter 条款逐条对照）

## Estimated cost

1–1.5 工作日。全部 Opus 4.7 Executor=Gate 独立完成；无需 Codex 审查（纯文档 + 无前端 diff）。

## Scope Gate（self-signed v3.2）

本 Plan 已在创建时完成 7/7 合规自审。Non-goals 显式，Exit Criteria 可证伪。Executor=Gate 授权执行 P23-01 → P23-05。
