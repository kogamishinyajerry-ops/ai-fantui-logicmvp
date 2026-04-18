---
phase: P27
plan: P27-00-TIER1
title: Backend Switch Drill — 真实 pkill + spawn + wait_ready 切换延迟的可证伪化
status: drafted · Executor self-review under v4.0 Extended Autonomy Mode
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P21 local_model_poc (Ollama 7B + MiniMax 双后端 adapter 已到位)
  - P25 integrated-timing-findings (findings § 1.3 明确点名：段 4 预算未含真实切换开销 5–8s)
  - ~/.minimax_key 存在；`127.0.0.1:11434` Ollama 可达；`qwen2.5:7b-instruct` 已 pull
non-goals:
  - 修改 controller / 19-node / 4 logic gates / LLM adapter / prompts / wow 脚本
  - 修改 demo_server 源码（只 spawn + kill，不改一行）
  - 改写 P22 pitch_script.md 或 disaster_runbook.md
  - 自动判断 "够不够用" 做 pitch；只报测，决策权交 Kogami
---

# P27 · Backend Switch Drill

## Why this Phase

P25 findings § 1.3 的诚实边界里白纸黑字写着：

> "不模拟段 4 切换 backend 的真实切换步骤（脚本是 per-backend spawn，所以 fallback 段里实际跑的是本轮同后端的又一次 chat）— 这把段 4 budget 测出的结果偏乐观（**没含 kill + respawn + wait_ready 的 5–8s**）。"

disaster_runbook.md 场景 1 推荐的第一动作是 "切到本地 Ollama fallback"——命令链 `export LLM_BACKEND=ollama && pkill -f well_harness.demo_server && python3 -m well_harness.demo_server &`。**这条链的实测延迟从未被测。** 5–8s 是直觉估计，不是数据。

Pitch 当天若 MiniMax 挂，演讲者要在场子里等这段链完成。**3s 是人能自然衔接的填充窗口，10s+ 就是冷场。** 把切换延迟从"直觉"升格为"数据"，正是 v4.0 授权下 Executor 能安全推进的单点发现。

P27 做一件具体的事：**写 `scripts/backend_switch_drill.py`，spawn demo_server on dedicated port 8797，测 MiniMax→Ollama 和 Ollama→MiniMax 两个方向 × N=2 次的 kill-to-ready 延迟，写 findings 文档。** 不改 disaster_runbook 的 5–8s 措辞——findings 交 Kogami 决定是否联动改写。

## Scope

### 测试内容

| 方向 | 起始 | 目标 | 测量 |
| ---- | ---- | ---- | ---- |
| A | `LLM_BACKEND=minimax` running | `LLM_BACKEND=ollama` + `OLLAMA_MODEL=qwen2.5:7b-instruct` | `t_kill`（SIGTERM→exit）+ `t_spawn_to_ready`（spawn→`/api/lever-snapshot` 200）+ `t_total`（=两者和） |
| B | `LLM_BACKEND=ollama` running | `LLM_BACKEND=minimax` | 同上 |

- 每方向 N=2 真跑
- 端口：8797（独立于 :5173 dev 实例和 :8799 pitch 默认端口，避免冲突）
- Warmup：起 server 后先调一次 `/api/lever-snapshot` 确保 adapter 已加载，再计时切换
- atexit 清理：若中途失败保留进程，exit hook SIGKILL 残余

### 产出

| 文件 | 内容 |
| ---- | ---- |
| `scripts/backend_switch_drill.py` | drill 主脚本；exit 0 = N runs 全绿，1 = 任一 run degraded，2 = prereq 缺失 |
| `runs/backend_switch_drill_<ts>/report.json` | 4 次运行原始数据 + 聚合 p50/min/max |
| `runs/backend_switch_drill_<ts>/summary.md` | 每方向一行 verdict |
| `docs/demo/backend-switch-drill-findings.md` | P25 预估 5–8s vs 实测对比；对 disaster_runbook 场景 1 话术的影响评估（报而不改）|

### Sub-phases

| Sub | 工作 | 工期 | 产出 |
| --- | --- | --- | ---- |
| P27-01 | `scripts/backend_switch_drill.py` | 0.3d | 脚本 + 单元跑通 |
| P27-02 | 双方向 N=2 真跑（两个 backend 都可用时）| 0.2d | 4 份 artefact JSON |
| P27-03 | `findings.md` + ROADMAP + closure + GATE self-sign (v4.0) | 0.2d | 三轨绿 + Notion sync |

**总工期：** 0.7 工作日

## Exit Criteria

- [ ] `scripts/backend_switch_drill.py` 落盘且能独立运行（`python3 scripts/backend_switch_drill.py --help` 正常）
- [ ] 双方向 × N=2 真跑落盘到 `runs/backend_switch_drill_<ts>/`
- [ ] findings.md 写出实测 vs P25 预估 5–8s 差异，给 Kogami 决策建议但不改 disaster_runbook
- [ ] pytest 662/1skip 零回归 · e2e 49/49 · adversarial 8/8 零回归
- [ ] GATE-P27-CLOSURE self-signed under v4.0

## R1–R5 合规（事前 self-audit）

| 原则 | P27 保持方式 |
| ---- | ----------- |
| R1 真值优先 | 不动 controller.py / 19-node / 4 logic gates；脚本只 spawn/kill，不改源码 |
| R2 AI 仅解释 | 不触 LLM adapter；只选 LLM_BACKEND 环境变量 |
| R3 可审计 | 真跑落盘 `runs/backend_switch_drill_<ts>/report.json`，原始毫秒数据完整 |
| R4 降级可控 | degraded 响应（minimax_api_key_missing / ollama_unreachable）显式 bucket 为 DEGRADED verdict，不假装成 PASS |
| R5 adversarial 守门 | adversarial_test.py 零触碰；closure 跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | drill 进程因 Ollama/MiniMax 响应慢超时，残留僵尸 server 占端口 8797 | 中 | 重跑失败 | atexit hook + 启动时 `_port_free` 预检 + SIGKILL fallback |
| R2 | 测量时混入系统噪声（外部进程抢 CPU 导致 spawn 慢）| 中 | N=2 离散度大 | 报告 min/p50/max 三档，不只 mean；findings 标样本量 |
| R3 | Ollama 模型冷启第一次 spawn 特别慢（模型加载进内存）| 高 | MiniMax→Ollama 首次会很慢 | warmup 一次 chat/explain；区分 "首切" vs "暖切" 两列 |
| R4 | 测试 exit code 1 被 CI 误当 failure 但其实是 degraded | 低 | CI 误报 | 脚本不进 pytest default lane；只作 rehearsal script（类似 dress_rehearsal） |

## 治理 Gate 规则（v4.0）

- Executor 自主推进所有 3 个 sub-phase
- P27-03 closure self-sign 贴 7-checklist
- v4.0 窗口 Phase 收口计数：#3（P25=#1, P26=#2, P27=#3）
- **触达深度验收建议阈值（≥3 未经 Kogami 过目）**；P27 收口后主动贴深度验收推荐到控制塔，让 Kogami 回帐时知晓
- 红线：若 drill 意外触及 controller / LLM adapter → 立停回滚

## Scope 初审（Executor pre-review）

基于 v4.0 授权自主初审：
- 纯脚本层工作 + spawn/kill 外部进程 → 不改任何运行时代码，红线 #1 不触
- 非不可逆（drill 可重跑；残留 artefact 无害）→ 红线 #2 不触
- 不改宪法级 Notion / v4.0 自身 → 红线 #3 不触
- 可能触发深度验收建议（第 3 Phase）→ 红线 #4 "自判触发器" 需主动披露，不自决是否绕过

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_
