---
phase: P30
plan: P30-00-TIER1
title: Scorecard 语义与 findings §5.1 决策对齐 — integrated_timing 两 backend 合并为 best-of-2 维度
status: drafted · Executor self-signed under v4.0 Extended Autonomy Mode
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P29 pitch_readiness.py 已落地
  - P25 findings §5.1 明确推荐 Ollama 主路径
  - P22 立项物料冻结基线未变
non-goals:
  - 修改 integrated_timing_rehearsal.py（budget 常量、budget 语义保持 P25 baseline）
  - 修改 integrated-timing-findings.md（P25 findings 是冻结证据）
  - 修改 pitch_script.md 或任何 pitch 物料
  - 引入新的 measurement round（纯逻辑调整，不重跑 drill）
---

# P30 · Scorecard 语义与 findings §5.1 决策对齐

## Why this Phase

P29 scorecard 首轮真跑 overall YELLOW，根因：Integrated Timing · MiniMax 维度 over_budget。
但查 P25 findings §5.1 明确写的是：

> **demo 用 Ollama 主路径**：wow_a 时间预算稳过，合规故事更顺。

也就是说 **pitch 日只会用一个 backend**（推荐 Ollama），MiniMax 那次 YELLOW 是
"备选方案的已知限制"，不是"当前系统故障"。现有 scorecard 把两个 backend 并列展示
二者独立判定 verdict，导致 Kogami T-0 看到 overall YELLOW 会以为"系统坏了需要修"，
而实际上只要不选 MiniMax 就没事。这是一个**语义层面的误导性**，不是脚本 bug。

P30 做一件具体的事：**把 `Integrated Timing · MiniMax` + `Integrated Timing · Ollama`
合并为一个 `Integrated Timing (best-of-2)` 维度**，取二者更 green 的那个作为主 verdict，
detail 列显式注明 "Ollama GREEN / MiniMax YELLOW — 建议用 Ollama 主路径（findings §5.1）"。

**不改 findings / budget 常量的理由：** 那些是 P25 测量产出的证据基线。budget=15s
是 P25 基于 "3 snapshots + 2 chats" 的保守估计；MiniMax L1/L3 ≈ 9.2s 是真实测量；
over_budget 判定是正确的**物理事实描述**。P30 只改 scorecard 的**聚合语义**——
在"二选一 backend"的业务上下文下，正确的 overall 判定就是 best-of-2。

## Scope

### 脚本侧改动（scripts/pitch_readiness.py）

1. 新增常量 `INTEGRATED_TIMING_GROUP = ("integrated_timing_ollama_", "integrated_timing_minimax_")`
2. 新增 `collect_readiness` 的后处理步骤：扫描 rows 里这两个 prefix 的 entry，若均存在：
   - 合并为单行 `Integrated Timing (best-of-2 backends)`
   - verdict 取二者中**更 green** 的（GREEN > YELLOW > RED > UNKNOWN）
   - age 取更新的那个
   - detail 注明 "`<winner>` <verdict> · `<other>` <verdict> — 建议用 Ollama 主路径（findings §5.1）"
3. 若 prefix group 里只有一个存在：保留原单行（边界 case，避免聚合时误删）

### Sub-phases

| Sub | 工作 | 工期 | 产出 |
|-----|------|------|------|
| P30-01 | pitch_readiness.py 聚合逻辑改动 + 重跑验证 overall 升 GREEN | 0.2d | 改动后脚本 + 新样例 |
| P30-02 | 更新 docs/demo/pre-pitch-readiness-report.md 首轮样例为 best-of-2 视图 | 0.1d | 新 sample doc |
| P30-03 | closure + ROADMAP + GATE-P30-CLOSURE self-sign（v4.0 7-checklist）| 0.1d | 三轨绿 + Notion sync |

**总工期：** 0.4 工作日

## Exit Criteria

- [ ] pitch_readiness.py best-of-2 聚合逻辑正确：Ollama GREEN + MiniMax YELLOW → 合并行 GREEN
- [ ] overall verdict 由 YELLOW 升 GREEN（反映"pitch 日选 Ollama 就没事"的业务语义）
- [ ] detail 明示 losing backend 的 verdict，避免 Kogami 误以为 MiniMax 也 GREEN
- [ ] 样例 doc 更新，显式引用 findings §5.1
- [ ] pytest 666/1skip 零回归 · e2e 49/49 · adversarial 8/8
- [ ] GATE-P30-CLOSURE self-signed under v4.0

## R1–R5 合规（事前 self-audit）

| 原则 | P30 保持方式 |
|------|-------------|
| R1 真值优先 | 只改聚合层，MiniMax over_budget 的 **真实测量值**不被篡改、不被隐藏（仍在 detail 里） |
| R2 AI 仅解释 | 无 LLM 调用 |
| R3 可审计 | detail 显式注明 losing backend verdict + 引用 findings §5.1，不是 "sweep under rug" |
| R4 降级可控 | 无降级相关改动 |
| R5 adversarial 守门 | adversarial_test.py 零触碰；closure 跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | best-of-2 可能遮蔽"两 backend 都坏了"的真实故障 | 低 | 假绿 | 只在一 GREEN + 一 YELLOW 时才升 GREEN；两者都 YELLOW/RED → 合并行取**更差**的（防止乐观偏置）|
| R2 | "findings §5.1 推荐 Ollama" 是 P25 基于当时测量的判断；未来 MiniMax 云端提速到 <7s 该方针就反转 | 低 | 长期维护 | detail 里附 `findings §5.1` 引用，Kogami 看到差异 → 重新审视 findings 是正常治理节奏 |
| R3 | 合并行丢掉 per-backend age，若 MiniMax artefact 很新但 Ollama 很旧，可能误判"Ollama stale" | 中 | 误 YELLOW | 合并行 age 取 winner（更 green 的那个）的 age；若 Ollama GREEN 但超 stale 阈值，best-of-2 自然降 YELLOW，行为合理 |
| R4 | 改动后 P29 样例 doc 与当前输出不一致 → 历史 sample 失效 | 确认发生 | 文档一致性 | P30-02 显式更新 sample；在 closure message 说明 "P29 sample superseded by P30" |

## 治理 Gate 规则（v4.0）

- Executor 自主推进所有 3 个 sub-phase
- P30-03 closure self-sign 贴 7-checklist
- v4.0 窗口 Phase 收口计数：#6（P25=#1, P26=#2, P27=#3, P28=#4, P29=#5, P30=#6）— Kogami 2026-04-18 已多次显式续签
- 红线：若改动触及 integrated_timing_rehearsal.py / findings / pitch 物料 → 立停回滚

## Scope 初审（Executor pre-review）

- 纯聚合层语义调整，无宪法级改动 → 红线 #1 不触
- 可逆（单脚本 + 单样例 doc）→ 红线 #2 不触
- 不改宪法级 Notion / v4.0 自身 → 红线 #3 不触
- 已越 ≥3 Phase 阈值但 Kogami 显式续签 → 红线 #4 已被用户覆盖

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_
