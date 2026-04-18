---
phase: P25
plan: P25-00-TIER1
title: 立项汇报段落级时序彩排 — pitch_script.md 硬时间预算的端到端可验证化
status: drafted · Executor self-reviewed under v4.0 Extended Autonomy Mode
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P22 话术 + 预检 + FAQ + 灾难手册四文档已冻结
  - P21 双后端 (MiniMax + Ollama) 已真跑通过
  - P24 视觉硬化已落地，三轨基线 658/1skip · 49/49 · 8/8
non-goals:
  - 修改 controller.py / 19-node / 4 logic gates / LLM adapter / prompts / wow 脚本
  - 修改 pitch_script.md 时间表本身（这是 P22 已冻结的话术基线，只验证不改写）
  - 改前端 UI 或演示流程
  - 新增真跑场景（只组合已有 API）
---

# P25 · 立项汇报段落级时序彩排

## Why this Phase

P22 冻结了 20 分钟硬时间表（`docs/demo/pitch_script.md`）和 14 项双后端真跑（`runs/demo_rehearsal_dual_backend_20260418T074215Z/`），但**两件事从未被机器组合过：**

1. **pitch_script 的段落时间预算** — 7 段 × 硬时长（如 wow_a 4min / fallback 3min）— 只是文档里的一张表，没有任何测试核对"每段真实 backend 响应叠加起来是否真的容得下"。
2. **Ollama 7B 在段 4 的切换** — smoke 测试显示 4.2–5.4s 单次响应，但 **段 4 只有 3 分钟**，里面要包含切后端命令 + 浏览器硬刷 + 问 1 句话 + 合规讲解。Backend 部分究竟吃掉多少秒？

P25 做一件具体的事：把 pitch_script 的段落时间表**升格为可验证契约**——给每段分配"backend 时间预算"（人讲的时间除外），自动跑对应 API，聚合实测 vs 预算，产出裕度报告。

**严格不动：** controller / truth engine / LLM adapter / prompts / pitch_script.md 本身 / 任何 wow 逻辑。

## Scope

### 段落→API 映射（来自 pitch_script.md）

| 段 | 名称 | 段时长 | Backend 需求 | 预算 (API 叠加，保守) |
| -- | --- | ------ | ----------- | ------------------ |
| 0 | Opening | 1:30 | 无 API（静态页面）| 0s |
| 1 | wow_a 因果链 | 4:00 | `/api/lever-snapshot` × 3 beats + `/api/chat/explain` × 2 | ≤ 15s（含 2 次 chat） |
| 2 | wow_b 蒙特卡洛 | 3:00 | `/api/monte-carlo/run` 1k + 10k | ≤ 3s（纯计算） |
| 3 | wow_c 反诊断 | 2:30 | `/api/diagnosis/run` × 1 | ≤ 1s（纯枚举） |
| 4 | Fallback | 3:00 | 切 Ollama + `/api/chat/explain` × 1 | ≤ 20s（含切后端启动 + 1 次 7B 响应） |
| 5 | R1–R5 总结 | 2:30 | 无 API | 0s |
| 6 | 闭场 | 1:30 | 无 API | 0s |

**预算设计哲学：**
- 段时长一大半留给"人讲"，backend 部分只占段的 10–20%，不允许 API 吃掉话术空间
- fallback 段的 20s 是因为 7B 本身 4–5s × 有时 2–3 次交互 + 启动等待
- 超预算 = P25 findings 里报出，不回滚、不改话术（人讲有 buffer 消化），但要报给 Kogami

### Sub-phases

| Sub | 工作 | 工作日 | 关键产出 |
| --- | --- | ----- | -------- |
| P25-01 | `scripts/integrated_timing_rehearsal.py` — 段落→API map + 预算核对 + 双后端聚合 | 0.5d | script + 单测 |
| P25-02 | 首轮双后端真跑 | 0.3d | `runs/integrated_timing_<backend>_<ts>/report.json` × 2 |
| P25-03 | findings 归档 `docs/demo/integrated-timing-findings.md` | 0.2d | 逐段 budget/实测/裕度 + 风险提示 |
| P25-04 | closure + GATE self-sign (v4.0) | 0.2d | 三轨绿 + 控制塔 DECISION + ROADMAP + Notion sync |

**总工期：** 1.2 工作日

## Exit Criteria

- [ ] `scripts/integrated_timing_rehearsal.py` 可独立跑（MOCK + 真跑两套路径）
- [ ] 双后端 (MiniMax + Ollama qwen2.5:7b) 各一轮真跑 artefact 入库
- [ ] `docs/demo/integrated-timing-findings.md` 逐段 budget/实测/裕度 + 若有超预算段，含风险提示
- [ ] 主 pytest 658/1skip 零回归 · e2e 49/49 零回归 · adversarial 8/8 零回归
- [ ] GATE-P25-CLOSURE self-signed under v4.0 (7-checklist) + 控制塔 DECISION

## R1–R5 合规（事前 self-audit）

| 原则 | P25 保持方式 |
| ---- | ------------ |
| R1 真值优先 | 纯验证层脚本，零触碰 controller.py / 19-node |
| R2 AI 仅解释 | 不改 LLM adapter，只调用现有 API 并测时延 |
| R3 可审计 | 每段 budget/实测字段落盘；commit trailer `Execution-by: opus47-max` |
| R4 降级可控 | 若某 backend 不可达，脚本 graceful 报 SKIPPED 不崩；fallback 路径视觉/语义不动 |
| R5 adversarial 守门 | adversarial_test.py 零触碰；本轮 closure 仍跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | Ollama 7B 在段 4 超过 20s 预算（假设不成立） | 中 | 话术在段 4 被 API 等待"卡住" | 脚本如实报告；findings 里给 Kogami 两条路（加大 buffer / 降模型规模） |
| R2 | MiniMax 当日延迟高于基线 | 低 | 段 1 超预算 | 网络环境敏感；报告实测 + 时间戳，多次跑取 P95 |
| R3 | 脚本误把 degraded fallback (key_missing) 当正常响应 | 中 | 假绿 | 响应体 `error_code` 字段显式检查；degraded 走独立 bucket |
| R4 | 脚本耗时过长导致 pytest CI 变慢 | 低 | CI 刺激 | P25 脚本不进 CI default lane，仅手动 + 本 Phase 一次真跑 |

## 治理 Gate 规则（v4.0 Extended Autonomy Mode）

- Executor 可自主推进全部 4 个 sub-phase
- P25-04 closure self-sign 贴 7-checklist（格式延用 P24 closure 形式）
- 红线：若脚本触到 controller / LLM adapter / prompts → 立停 + 回滚 + 向 Kogami 报告
- v4.0 Phase 收口计数：若本次批量收口不计入、P25 算窗口内 #1 Phase 收口

## Scope 初审（Executor pre-review，非 Kogami 批准）

Executor 基于 v4.0 授权自主初审：
- 纯验证层工作，无宪法级改动 → v4.0 红线 #1 不触
- 非不可逆破坏 → v4.0 红线 #2 不触
- 不修改 v4.0 规则或宪法级 Notion 页面 → 红线 #3 不触
- 无需深度验收触发（测试轨迹平稳、无技术路线偏移）→ 红线 #4 不触

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_
