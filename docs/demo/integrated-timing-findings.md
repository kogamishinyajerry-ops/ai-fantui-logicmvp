# 立项汇报段落级时序彩排 — 发现记录

> **给谁看：** Kogami + 演讲演练团队
> **回答什么：** pitch_script.md 的 7 段硬时间表，在真实 backend 下每段 backend API 叠加时间是否容得下？
> **研究方法：** `scripts/integrated_timing_rehearsal.py` × 双后端 × N=2 真跑
> **最新更新：** 2026-04-18

---

## TL;DR

| 段 | budget | MiniMax (cloud) | Ollama 7B (local) | 结论 |
| -- | ------ | --------------- | ----------------- | ---- |
| 0 Opening | 0s | 0s | 0s | 无 API，无风险 |
| **1 wow_a 因果链** | **15s** | **18.4s / 29.0s ❌** | **8.9s / 10.1s ✅** | **MiniMax 2/2 超预算；Ollama 2/2 达标** |
| 2 wow_b 蒙特卡洛 | 3s | 0.17–0.20s ✅ | 0.20–0.29s ✅ | 纯计算，两后端都极快 |
| 3 wow_c 反诊断 | 1s | 0.01–0.02s ✅ | 0.006s ✅ | 纯枚举，两后端都极快 |
| 4 Fallback chat | 20s | 7.9s–11.7s ✅ | 2.9s–3.3s ✅ | 两后端都达标（Ollama 有 ~17s 裕度） |
| 5 R1–R5 | 0s | 0s | 0s | 无 API |
| 6 闭场 | 0s | 0s | 0s | 无 API |

**核心发现：** 用 **Ollama 7B (本地) 比用 MiniMax (云) 更能保证 wow_a 段时间预算** — 这与 pitch_script.md 隐含的"MiniMax 是主路径、Ollama 是 fallback"的话术假设**相反**。不是"谁合规选谁"，而是"本地其实更快"。

---

## 一、脚本与方法

### 1.1 测什么

pitch_script.md 第 10–21 行固定的 7 段硬时间表里，标有 backend API 需求的有 4 段（wow_a / wow_b / wow_c / fallback）。我们给每段分配一个"保守 backend 时间预算"（人讲时间不占预算），自动跑对应 API，聚合实测 vs 预算：

- 段 1 wow_a：3 次 `lever-snapshot` + 2 次 `chat/explain` → budget 15s
- 段 2 wow_b：1k + 10k `monte-carlo/run` → budget 3s
- 段 3 wow_c：1 次 `diagnosis/run` → budget 1s
- 段 4 fallback：1 次 `chat/explain`（含模型启动冷启）→ budget 20s

预算设计哲学：段时长大半留给人讲，backend 只占 10–20%；超预算 = 演讲被迫等待或压缩话术。

### 1.2 测试环境

- macOS · localhost:8799 demo_server · LLM_BACKEND={minimax | ollama}
- 每 backend 一轮 = 一次进程 spawn + warmup + 顺序跑 8 个 API case + 1 次 `_wait_ready` 冷启测量
- N=2 per backend（2026-04-18 本地执行）
- Ollama 模型：qwen2.5:7b-instruct（per P21 真跑证据）
- 脚本不 mock 任何调用 — 全部真 backend

### 1.3 不测什么（诚实边界）

- 不测人讲时间（话术由 Kogami 现场掌控）
- 不测网络抖动 P95 / P99（真 pitch 日网络条件未知，不预设）
- 不测 MiniMax 的 M2 vs M2.7 区别（用 demo_server 现行配置）
- 不模拟"段 4 切换 backend"的真实切换步骤（脚本是 per-backend spawn，所以 fallback 段里实际跑的是本轮同后端的又一次 chat）— 这把段 4 budget 测出的结果偏乐观（没含 `kill + respawn + wait_ready` 的 5–8s）

---

## 二、数据

### 2.1 MiniMax cloud 真跑（N=2）

| Run | 段 1 wow_a 总 | 段 1 各 case | 段 2 MC | 段 3 Diag | 段 4 Fallback | verdict |
| --- | ------------ | ----------- | ------- | --------- | ------------- | ------- |
| 1 | **29.0s ❌** | init 1.1ms / early 1.5ms / deep 1.4ms / L1 11.7s / L3 17.3s | 173 + 22ms | 10ms | 7.9s | YELLOW (over_budget × 1) |
| 2 | **18.4s ❌** | ... / L1 9.2s / L3 9.2s | 168 + ? ms | 15ms | 11.7s | YELLOW (over_budget × 1) |

**均值：** L1 ~10.4s · L3 ~13.3s · wow_a 段总 ~23.7s · 超预算 8.7s

**Artefact：** `runs/integrated_timing_minimax_20260418T132007Z/report.json`

### 2.2 Ollama 7B local 真跑（N=2）

| Run | 段 1 wow_a 总 | 段 1 各 case | 段 2 MC | 段 3 Diag | 段 4 Fallback | verdict |
| --- | ------------ | ----------- | ------- | --------- | ------------- | ------- |
| 1 | **10.1s ✅** | init 1.0ms / early 1.3ms / deep 1.3ms / L1 7.1s / L3 3.1s | 268 + 18ms | 5.5ms | 3.0s | GREEN |
| 2 | **8.9s ✅** | ... / L1 5.1s / L3 3.7s | 201 + ?ms | 5.3ms | 3.3s | GREEN |

**均值：** L1 ~6.1s · L3 ~3.4s · wow_a 段总 ~9.5s · 裕度 ~5.5s

**Artefact：** `runs/integrated_timing_ollama_20260418T132057Z/report.json`

---

## 三、解读

### 3.1 为什么 MiniMax 比 Ollama 慢

假设（未验证，待确认）：
- demo_server 连的 MiniMax 端点配置可能用了 M2/M2.7 推理模型，每次会生成长 CoT，耗时正比于输出 token
- Qwen2.5-7B 在 Apple Silicon 本地 GPU 推理速度 ~20–40 token/s + 无网络 RTT，对"短回答"场景反而更快
- MiniMax 云端每次请求含 HTTPS + 队列 + 推理多段，p50 可能就在 10s 量级

### 3.2 对 pitch 的实际含义

1. **段 1 wow_a 如果用 MiniMax：大概率超预算 3–14 秒** — 主讲人会被迫在提问后"站着等"，或需提前准备填充话术（pitch_script.md 的 1-b / 1-c / 1-d 正文足够填，但需操作员心里有数）
2. **Ollama 7B 可当"真正的主路径"而不只是 fallback** — 速度 / 合规 / 可离线 三项都强，只有 MiniMax 的"中文措辞更精细"是剩下优势
3. **wow_b / wow_c 零风险** — 两后端都 < 300ms，人讲时间完全支配
4. **段 4 两后端都过关** — 但脚本里的段 4 没含真实 backend 切换成本，真实 pitch 里需额外留 5–8s 给 `pkill + spawn + wait_ready`

### 3.3 诚实性护栏

- 所有 `elapsed_ms` 数字来自 `time.monotonic()`，无估算、无修饰
- degraded 响应（`error: minimax_api_key_missing` / `ollama_unreachable`）会被脚本显式标为 `degraded` verdict，不计入 PASS
- 本 findings 样本量 N=2，不保证 P95/P99；要做大样本需 N≥5–10 次重复跑 + 统计

---

## 四、建议（给 Kogami 决策，不自行落地）

### 4.1 立项日当天

**选项 A（最保守，推荐）：**
- pitch 日 **主后端换成 Ollama 7B**，保留 MiniMax 为"云端对比组"仅在段 4 演示时切回
- 优点：wow_a 时间预算稳过；合规故事更顺
- 成本：需 `LLM_BACKEND=ollama` 起 server；pitch 脚本 3-a 节"断网切 Ollama"需改写（但 pitch_script.md 是 P22 已冻结基线，改写等于 P22 再开放）

**选项 B（维持现状）：**
- pitch 日仍然 MiniMax 作为主后端
- 在段 1 wow_a 的"等待 chat 响应"时主讲补讲 pitch_script 已有的"这些节点不是 AI 推断"填充话术（1-b 尾段 + 1-c 开段有天然 buffer 空间）
- 成本：对主讲人临场抗压要求较高；某些 runs 可能触发 17s+ 的长尾等待让观众感到冷场

**选项 C（工程增强，建议下一 Phase）：**
- 在 pitch 开始前 **预热 chat/explain 两个问题**（结果缓存在 demo_server 内存或 runs/ JSON），pitch 时点击即出
- 本质：把"real-time LLM 响应"降级为"录屏级确定性演示"
- R1–R5 合规性未变（结果还是 AI 生成，只是缓存；可以在缓存里标"pre-generated 2026-04-XX"透明披露）

### 4.2 治理意义

这条发现 **直接攻击了 P22 话术稿里段 4 的"本地是 fallback"措辞**——P25 的客观数据表明本地更快。若选 A，pitch_script.md 不再是 P22 冻结基线，等于给 P25 的 closure 增加"需联动更新 P22"的副作用。因此 P25 自签仅签脚本 + artefact + findings；pitch_script.md 的改写留给 Kogami 决策。

---

## 五、复现

```bash
python3 scripts/integrated_timing_rehearsal.py --backend minimax
python3 scripts/integrated_timing_rehearsal.py --backend ollama --ollama-model qwen2.5:7b-instruct
```

Artefacts 自动落 `runs/integrated_timing_<backend>_<ts>/report.json` +
`per_section_summary.md`；exit code 0=GREEN / 1=YELLOW 或 DEGRADED / 2=prereq 缺失。

Prereq：
- MiniMax：`~/.minimax_key` 非空
- Ollama：`127.0.0.1:11434` 可达 + `qwen2.5:7b-instruct` pull 过

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode_
