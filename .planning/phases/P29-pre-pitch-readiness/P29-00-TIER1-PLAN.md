---
phase: P29
plan: P29-00-TIER1
title: Pre-Pitch Readiness Scorecard — 把 6 份 drill artefact 聚成 Kogami T-0 一眼 GREEN/YELLOW/RED
status: drafted · Executor self-signed under v4.0 Extended Autonomy Mode
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P25-P28 产出物齐备（runs/ 下每类 drill 至少一份 artefact）
  - P22 立项物料冻结基线未变
non-goals:
  - 重跑任何 drill（本 Phase 只聚合，不再做 expensive IO）
  - 修改任何 drill 脚本（dress_rehearsal / integrated_timing / backend_switch_drill / local_model_smoke / demo_rehearsal）
  - 修改 controller / LLM adapter / prompts / wow / 前端
  - 做 live-browser 校验 — 那是 preflight_checklist.md 的 manual 环节
---

# P29 · Pre-Pitch Readiness Scorecard

## Why this Phase

P25 / P27 / P28 分别加了 timing / switch / symbol 三层机器化守护，加上既有的
`dress_rehearsal` / `local_model_smoke` / `demo_rehearsal_dual_backend` / pytest /
adversarial — 现在 pitch 前 Kogami 要看状态得去 7 个地方捞 artefact，每个格式不一样。

P29 做一件具体的事：**写一份 `scripts/pitch_readiness.py`，从 `runs/` 下每类 drill
的最新 artefact 里抽 verdict + age，渲染成一张 markdown 表格，overall GREEN/YELLOW/RED 直接给结论**。
T-0 前 Kogami 一行命令看完 6 维度，红就去 re-run，绿就上台。

**只聚合不再跑的理由：** 各 drill 自己跑几十秒到几分钟。T-0 前 10 分钟 Kogami
没时间全跑一遍，只想知道"最近那次跑的结果新不新、pass 不 pass"。本 Phase 把
"读盘 + 解析 + 判新鲜 + 汇总" 这套动作固化到一个脚本里，不碰 drill 本身。

## Scope

### 被覆盖的 6 类 drill artefact

| 前缀（runs/） | 对应命令 | verdict 源 |
|-------------|---------|-----------|
| `dress_rehearsal_*` | `scripts/dress_rehearsal.py` | `rehearsal_report.md` 里的 `Verdict: **PASS/FAIL**` |
| `integrated_timing_minimax_*` | `scripts/integrated_timing_rehearsal.py --backend minimax` | `report.json` sections 各自 `verdict` 字段聚合 |
| `integrated_timing_ollama_*` | `scripts/integrated_timing_rehearsal.py --backend ollama` | 同上 |
| `backend_switch_drill_*` | `scripts/backend_switch_drill.py` | `report.json` 的 `minimax_to_ollama` / `ollama_to_minimax` aggregate verdict |
| `local_model_smoke_*` | `scripts/local_model_smoke.py` | `report.json` summary.verdict |
| `demo_rehearsal_dual_backend_*` | `scripts/demo_rehearsal.py` dual-backend mode | `report.json` overall verdict |

### 不在本 scorecard 的维度（显式声明）

- pytest 套件（666+ tests）→ 跑 `python3 -m pytest` 单独查
- adversarial 8/8 → 跑 `python3 src/well_harness/static/adversarial_test.py` 单独查
- 浏览器 UI / Canvas 渲染 → manual 眼检
- 网络条件 / 投影仪 / 电源 → `docs/demo/preflight_checklist.md` 的 16 项 T-0 清单

在 scorecard 底部 "Not covered" 段明示这 4 项，避免 Kogami 误以为 overall GREEN 就等于可以上台。

### Sub-phases

| Sub | 工作 | 工期 | 产出 |
|-----|------|------|------|
| P29-01 | `scripts/pitch_readiness.py` — 6 drill reader + age 校验 + markdown 渲染 + 退出码 | 0.3d | 脚本 + 首轮输出 |
| P29-02 | `docs/demo/pre-pitch-readiness-report.md` — 首轮真跑样例归档（Kogami 能直接 diff 下次跑对比） | 0.1d | sample scorecard |
| P29-03 | closure + ROADMAP + GATE-P29-CLOSURE self-sign（v4.0 7-checklist）| 0.2d | 三轨绿 + Notion sync |

**总工期：** 0.6 工作日

## Exit Criteria

- [ ] `scripts/pitch_readiness.py` 真跑产出合法 markdown（当前 overall YELLOW，因 P25 MiniMax wow_a 段超 budget — 已是已知真实状态，非脚本 bug）
- [ ] 脚本退出码 0/1/2 正确映射 GREEN/YELLOW/RED
- [ ] `docs/demo/pre-pitch-readiness-report.md` 归档首轮输出
- [ ] `--stale-hours` 参数可用（默认 24h；artefact 超期 GREEN 降 YELLOW）
- [ ] pytest 666+ 不降、e2e 49/49 零回归、adversarial 8/8 零回归
- [ ] GATE-P29-CLOSURE self-signed under v4.0

## R1–R5 合规（事前 self-audit）

| 原则 | P29 保持方式 |
|------|-------------|
| R1 真值优先 | 只读 `runs/` 下已落盘 artefact，不调 LLM 不触发新物理仿真 |
| R2 AI 仅解释 | 聚合脚本纯 Python stdlib，无 LLM 调用 |
| R3 可审计 | 强化 R3 — scorecard 本身是审计产物，每条都带 "latest artefact 文件名 + 新旧度小时数" |
| R4 降级可控 | 不涉及降级链路 |
| R5 adversarial 守门 | adversarial_test.py 零触碰；closure 跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | drill 脚本未来换了 verdict 字段名（`within_budget` → `pass`）读取失败 → scorecard 显示 UNKNOWN | 中 | scorecard 假黄 | reader 对未知 verdict 显式在 detail 列打印 `unknown verdict: <name>=<value>` 前 3 个，立即可定位 |
| R2 | `runs/` 被清空或 artefact 过期 → 全部 RED 误导 "系统坏了" | 中 | 假警报 | age 阈值做 YELLOW warning 而非 RED；RED 只用于 "no artefact at all"；Kogami 看到 RED 就知道要 re-run drill |
| R3 | 多种 drill 的 verdict 语义不一致（"within_budget"/"ok"/"PASS"/"GREEN"）| 高（确认如此）| reader 逻辑脆 | 每类 drill 独立 reader，各自知道自己家的词表；只在入口层归一化为 GREEN/YELLOW/RED |
| R4 | Kogami 误把 overall GREEN 当成"一切妥当"不看 `Not covered` 段 | 中 | pitch 日漏项 | scorecard 底部加粗 `Not covered by this scorecard` 段，显式列 pytest / adversarial / UI / network 四项 |

## 治理 Gate 规则（v4.0）

- Executor 自主推进所有 3 个 sub-phase
- P29-03 closure self-sign 贴 7-checklist
- v4.0 窗口 Phase 收口计数：#5（P25=#1, P26=#2, P27=#3, P28=#4, P29=#5）— Kogami 2026-04-18 已主动续签越过 ≥3 阈值，并在本轮 compaction 后再次显式续权
- 红线：若脚本意外 spawn 新进程 / 动任何 drill 脚本源 → 立停回滚

## Scope 初审（Executor pre-review）

- 纯聚合脚本 + 样例文档，无宪法级改动 → 红线 #1 不触
- 只读聚合，可逆 → 红线 #2 不触
- 不改宪法级 Notion / v4.0 自身 → 红线 #3 不触
- 已越 ≥3 Phase 阈值但 Kogami 显式续签 → 红线 #4 已被用户覆盖

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_
