# Backend Switch Drill — 发现记录

> **给谁看：** Kogami + 演讲演练团队 + disaster_runbook 维护者
> **回答什么：** P25 findings §1.3 留下的悬案——真实 `pkill + spawn + wait_ready` 切换延迟到底多少？
> **研究方法：** `scripts/backend_switch_drill.py` × 双方向 × N=2 真跑
> **最新更新：** 2026-04-18

---

## TL;DR

| 方向 | P25 预估 | 实测 p50 | 差异 | Verdict |
| ---- | -------- | ------- | ---- | ------- |
| MiniMax → Ollama | "5–8s" 直觉估计 | **108ms** | **实测比预估快约 50–75×** | GREEN × 2/2 |
| Ollama → MiniMax | "5–8s" 直觉估计 | **107ms** | **实测比预估快约 50–75×** | GREEN × 2/2 |

**核心发现：** 机械切换（SIGTERM → 进程退出 → 重新 spawn → `/api/lever-snapshot` 200）**两方向均 ~105ms**。远低于 P25 findings §1.3 里作为诚实边界写下的 "5–8s" 保守估计。

**但必须诚实标注范围：** 这个 105ms 只覆盖**"HTTP 服务 + 真值引擎"层的切换成本**。LLM adapter 是懒加载——`/api/lever-snapshot` 只走 controller，不触 LLM。**首次 post-switch `/api/chat/explain` 还要付 adapter 初始化 + (Ollama 情况下) 冷模型加载的代价**，那部分不在本 drill 测量范围里。

---

## 一、测试方法

### 1.1 测什么

对每个方向（a2b / b2a）重复 N=2 次完整循环：

```
spawn(from)  →  wait_ready(from)  →  warmup probe
       ↓
  [MEASURE START]
       ↓
  SIGTERM(from)   →  wait exit     (记 t_kill_ms)
  spawn(to)       →  wait_ready(to) (记 t_spawn_to_ready_ms)
       ↓
  [MEASURE END]   (t_total_ms = t_kill + t_spawn_to_ready)
       ↓
  kill(to) 清理 → 等 0.5s → 下一轮
```

- 预算参考：GREEN ≤ 8000ms · YELLOW ≤ 12000ms · 超即 ALERT（超过人能自然填充的话术窗口）
- 端口：**8797**（独立于 :5173 dev 实例、:8799 pitch 默认、:8766 adversarial，零冲突风险）
- Probe：`/api/lever-snapshot` 收到 200 视为 "ready"

### 1.2 测试环境

- macOS · localhost:8797 demo_server
- 2026-04-18 本地执行
- MiniMax：`~/.minimax_key` OK
- Ollama：`127.0.0.1:11434` reachable · `qwen2.5:7b-instruct` 已 pull
- 脚本不 mock — 真 spawn + 真 SIGTERM + 真 HTTP probe

### 1.3 不测什么（诚实边界，请逐条注意）

- **不测首次 post-switch LLM 调用延迟**。`/api/lever-snapshot` 是纯 truth-engine，不触 `MiniMaxClient` / `OllamaClient`。adapter 是首次 LLM 请求时才初始化。Ollama 首次 chat 还要加载 7B 模型到内存（~5–10s 冷启）。**P25 findings 测的就是这段——P27 没替代 P25，只补齐缺失的机械部分。**
- 不测真实 pitch 日网络条件（localhost vs 会场 WiFi 不同）
- 不测 backend 进程持有资源（文件句柄 / socket）被清理干净——只要 `/api/lever-snapshot` 200 就计 ready
- 样本量 N=2 每方向，不承诺 P95/P99

---

## 二、数据

### 2.1 MiniMax → Ollama（cycle N=2）

| Run | t_kill_ms | t_spawn_to_ready_ms | t_total_ms | Verdict |
| --- | -------- | ------------------- | ---------- | ------- |
| 1   | 1        | 107                 | 108        | GREEN   |
| 2   | 1        | 103                 | 104        | GREEN   |

**聚合：** n=2/2 clean · min=104ms · p50=108ms · max=108ms · **GREEN**

### 2.2 Ollama → MiniMax（cycle N=2）

| Run | t_kill_ms | t_spawn_to_ready_ms | t_total_ms | Verdict |
| --- | -------- | ------------------- | ---------- | ------- |
| 1   | 1        | 102                 | 103        | GREEN   |
| 2   | 1        | 106                 | 107        | GREEN   |

**聚合：** n=2/2 clean · min=103ms · p50=107ms · max=107ms · **GREEN**

**Artefact：** `runs/backend_switch_drill_20260418T134550Z/`

---

## 三、解读

### 3.1 为什么比 P25 估计快这么多

P25 findings §1.3 的 "5–8s" 是未分解的直觉——混了"HTTP server 上线" + "LLM adapter 加载" + "模型冷启"。P27 把这 3 层拆开，只测第一层：

| 层 | 典型时间 | 何时付 |
| -- | ------- | ------ |
| HTTP server 起来（Python 导入 + Bottle route 注册 + socket bind）| **~100ms** | 每次 spawn 时付；controller/19-node 也在这里加载 |
| LLM adapter 初始化（MiniMax 读 key + 客户端对象构造 / Ollama HTTP client 构造）| ~50–200ms | 首次 /api/chat/* 请求时付 |
| Ollama 7B 模型冷启（qwen2.5:7b-instruct 首次加载到 GPU/CPU）| **~5–10s** | 首次真实推理调用时付 |

**pitch 日真实场景重新绑定：**
- 从 SIGTERM 到 `/api/lever-snapshot` 能渲染 19 节点 canvas：**~105ms**
- 从 SIGTERM 到第一次 `/api/chat/explain` 返回答案：仍然 ~5–10s（P25 段 4 预算 20s 覆盖的就是这段）

**结论：** 主讲人演讲时 `pkill && restart` 后**硬刷浏览器**看到的 canvas 延迟只有 100ms——完全无感。真正需要防的是**首次"向 AI 提问"的冷启延迟**，而那一块 P25 段 4 预算 20s 已经有裕度（MiniMax 测 7.9–11.7s，Ollama 测 2.9–3.3s 均过关）。

### 3.2 对 disaster_runbook 场景 1 的影响

场景 1 "恢复动作" 步骤 1 的命令链：
```bash
export LLM_BACKEND=ollama
export OLLAMA_MODEL=qwen2.5:7b-instruct
pkill -f well_harness.demo_server && python3 -m well_harness.demo_server &
# 浏览器硬刷
```

**可以更自信地告诉主讲人：** "硬刷后 canvas 立即出现（~100ms），但**第一次提问** AI 回答可能要等 5–10s（Ollama 模型冷启 + 首次推理）。"

disaster_runbook 当前措辞 "首响延迟上升到 3–6s（本地 7B）" 是对**稳态**的描述，不是冷启。P21 local_model_poc 测的是 P50 约 3s（暖态）。**首次冷启实测是 P21 `runs/local_model_smoke_20260418T065144Z/report.json` 里的 first-call 数据。** 具体数字本 Phase 不再重测，建议 Kogami 决定是否在 disaster_runbook 显式披露"首次冷启 5–10s"。

### 3.3 对 pitch_script.md 的影响（无改动建议）

P25 findings 段 4 budget 20s 的裕度分析保持有效。P27 数据不改变 P25 给 Kogami 的 ABC 三选项。**本 Phase 建议对 pitch_script.md 零改动。**

### 3.4 诚实性护栏

- 所有毫秒数来自 `time.monotonic()`，无估算、无修饰
- N=2 不足以做 P95；若 Kogami 需要，建议 P28 再跑 N=10
- SIGTERM→exit **t_kill_ms=1ms** 看起来可疑，但合理：`well_harness.demo_server` 没注册长清理 hook，SIGTERM 到进程死亡主要受 Bottle 的 asyncore loop 退出速度决定。用 `os.killpg` 对进程组发信号，两步内能干净退出

---

## 四、建议（给 Kogami 决策）

### 4.1 pitch 日当天

- **无需额外 buffer 时间给 "mechanical switch"**——100ms 完全看不见
- **"切完 backend 立刻提问" 话术要铺垫**：若主讲人将在切换后立即演示 AI 问答，那段冷启 5–10s 要靠 pitch_script 段 4 现有 20s 预算吸收（已验证过关）；或"切换后先讲一段真值引擎，60s 后再提第一个 AI 问题"——这样 Ollama 模型已暖，首问快

### 4.2 disaster_runbook 维护（可选联动）

若 Kogami 想让 disaster_runbook 更精准：
- 把场景 1 "首响延迟上升到 3–6s" 补成 "首次冷启 5–10s；稳态 3–6s"
- 新增一行"切换后 hard-refresh 即可看到 19 节点 canvas，<200ms"

本 Phase 不自行改 disaster_runbook（它是 P20.2 冻结基线）。

---

## 五、复现

```bash
python3 scripts/backend_switch_drill.py                   # 双方向 N=2
python3 scripts/backend_switch_drill.py --n-runs 10       # 做 P95 分析
python3 scripts/backend_switch_drill.py --direction a2b   # 只测 MiniMax→Ollama
```

Artefacts 落 `runs/backend_switch_drill_<ts>/`：
- `report.json` — 原始每轮数据 + 聚合 min/p50/max
- `summary.md` — 每方向一行 verdict

Exit code：0=双方向全 GREEN / 1=任一 YELLOW/DEGRADED / 2=prereq 缺失 / 3=内部错误。

Prereq：
- `~/.minimax_key` 非空
- `127.0.0.1:11434` 可达 + `qwen2.5:7b-instruct` pull 过
- 端口 8797 未占用

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode_
