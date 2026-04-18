# 立项汇报演讲稿 — AI+工业逻辑验证工作台（Well Harness）

**总时长：** ≤ 20 分钟（不含 Q&A）
**主讲：** Kogami
**受众：** 甲方（航空系统工程 + IT 合规双背景）
**凡对外论断都标注证据文件路径 — 没有路径 = 不讲。**

---

## 时间表（硬分配）

| 段 | 名称                     | 时长 | 进度条 |
| -- | ------------------------ | ---- | ------ |
| 0  | Opening                  | 1:30 | 00:00 → 01:30 |
| 1  | wow_a 因果链（truth + AI 叙述） | 4:00 | 01:30 → 05:30 |
| 2  | wow_b 蒙特卡洛（数值独立）     | 3:00 | 05:30 → 08:30 |
| 3  | wow_c 反诊断（枚举独立）       | 2:30 | 08:30 → 11:00 |
| 4  | Fallback demo（断网切 Ollama） | 3:00 | 11:00 → 14:00 |
| 5  | R1–R5 宪法总结             | 2:30 | 14:00 → 16:30 |
| 6  | 闭场 + 请求立项决定          | 1:30 | 16:30 → 18:00 |
| —  | Buffer                   | 2:00 | 18:00 → 20:00 |

---

## 段 0 · Opening（1:30）

**目标：** 一句话说清"我们解决什么问题"。不讲技术，讲痛点。

**话术：**
> "在航空逆推力链这类安全关键控制逻辑的验证里，传统流程有两个痛点：
> 一是**AI 容易瞎说**——幻觉和自信的错答，对安全系统是灾难；
> 二是**黑箱**——你不知道 AI 为什么那么说，也没法审计。
>
> 我们做的不是'再造一个更聪明的 AI'。我们做的是——**把真值引擎放在 AI 前面**。
> 真值引擎先给出物理/逻辑层面的结论，AI 只负责把结论翻译成人话。
> 接下来 20 分钟，我会演示这个架构怎么工作，以及它为什么在甲方场景下可审计、
> 可降级、可国产化。"

**视觉提示：** 打开浏览器 `http://localhost:8799/`，显示 Canvas 19 节点初始态。

---

## 段 1 · wow_a 因果链（4:00）

**目标：** 让观众看见"一次操作 → 四个逻辑门依次激活 → 19 节点状态真实传播"。

**技术锚点：**
- 真值引擎代码：`src/well_harness/controller.py` · 19 节点 · 4 逻辑门（logic1–logic4）
- 彩排真跑：`runs/dress_rehearsal_20260418T063146Z/wow_a_timeline.json`（3 beats, 4ms 总耗时）

### 脚本

**1-a. 初始态（30s）**
> "这是一个 19 节点的反推力控制逻辑系统——4 个逻辑门（L1–L4）控制最终的
> THR_LOCK（推力锁死）输出。初始态所有节点灰色，没有激活。"

**操作：** 手动拉杆，`tra_deg: 0` → `tra_deg: -5`。

**1-b. BEAT_EARLY（1:00）**
> "拉到 -5 度，radio altitude < threshold，on_ground，L1 和 L2 亮绿——
> 这是着陆阶段的准备。注意：**L1 和 L2 同时亮，不是 AI 推断，是 controller.py
> 里 19 节点 + 4 门的确定性计算。** 观察右侧抽屉——AI 现在说'L1 是着陆判据'，
> 但它只是在转述左边的事实，真值来自门函数。"

**操作：** 继续拉到 -35 度 + 提 TLS。

**1-c. BEAT_DEEP（1:30）**
> "拉到深反推 -35 度，TLS 解锁，L2 和 L3 亮——深反推 commit。
> 继续等 VDT 达 90% → L4 亮 → THR_LOCK 激活。**整条因果链从人拉杆传到最终输出，
> 19 节点状态跟随四门逻辑，耗时 4ms。** 彩排已经把这个过程录下来了（`runs/
> dress_rehearsal_20260418T063146Z/wow_a_timeline.json`），每次跑结果字节级一致。"

**1-d. AI 叙述开关（1:00）**
> "我故意拔掉 AI——关掉聊天抽屉——Canvas 上的节点状态**完全不变**。
> 这是我们的 **R2 原则：AI 只解释，不决策**。即使 AI 服务挂了，
> 或者 AI 说错了，控制逻辑的结论也不会被污染。"

---

## 段 2 · wow_b 蒙特卡洛（3:00）

**目标：** 让观众看见"数值通道和 AI 解耦"。

**技术锚点：**
- 蒙特卡洛 API：`/api/monte-carlo/run` · 纯数值 · 字节级确定性 replay
- 彩排真跑：`runs/dress_rehearsal_20260418T063146Z/wow_b_timeline.json`（1k 191ms，10k 48ms，replay 40ms deterministic）

### 脚本

**操作：** 点击"蒙特卡洛"按钮，跑 10,000 trials。

**话术（1:30）：**
> "10,000 次参数扫动，48 毫秒跑完——**这条通道完全不经过任何 LLM**。
> 它回答的是：'在参数不确定性下，THR_LOCK 成功率的置信区间是多少？'
> 答案是分布，不是一句话。分布来自 controller.py 的逐次真值计算，
> 不来自 AI 猜测。"

**操作：** 展示 1k baseline + 10k 对照。

**话术（1:30）：**
> "同样的种子，跑 5 遍结果**字节级一致**——这是可审计性（R3）。
> 甲方将来真要独立复核这个结果，我们能提供原始参数表 + 种子 + 输出哈希，
> 他们自己一命令复现，不依赖我们。"

---

## 段 3 · wow_c 反诊断（2:30）

**目标：** 让观众看见"AI 擅长的生成任务，我们用枚举把它变成可审计"。

**技术锚点：**
- 反诊断 API：`/api/diagnosis/run` · `outcome=thr_lock_active` · 枚举所有可能诱因
- 彩排真跑：`runs/dress_rehearsal_20260418T063146Z/wow_c_timeline.json`（7 diagnoses, 72ms）

### 脚本

**操作：** 点击"反诊断 THR_LOCK"按钮。

**话术（1:30）：**
> "反诊断在问：'要让 THR_LOCK 激活，一共有几条可能的触发路径？'
> 这种题目如果交给 AI，它会给你一段流畅的文字说'大概是 TRA 和 TLS...'——
> 但没法验证。**我们的答案是 7 条枚举路径，72 毫秒产出，每条都能回到 controller.py
> 的节点 ID。** AI 只是在最后一步把 7 条翻译成人话。"

**话术（1:00）：**
> "把 AI 的生成任务变成枚举任务——这就是我们把 AI 放在真值引擎**下游**
> 的设计逻辑。AI 不负责想答案，负责叙述答案。"

---

## 段 4 · Fallback Demo（断网切 Ollama）（3:00）

**目标：** 回答甲方必问的"云 API 挂了怎么办" + "数据不出境"。

**技术锚点：**
- 切换命令：`LLM_BACKEND=ollama` + `OLLAMA_MODEL=qwen2.5:7b-instruct`
- P21 adapter：`src/well_harness/llm_client.py`（Protocol + MiniMax + Ollama + factory）
- 候选清单：`config/llm/local_model_candidates.yaml`
- 真跑证据：`runs/local_model_smoke_20260418T072226Z/report.json`（7B 3/3 PASS, 4.2–5.4s）
- 双后端真跑：`runs/demo_rehearsal_dual_backend_20260418T074215Z/report.json`（14/14 PASS）
- 详细文档：`docs/demo/local_model_poc.md`

### 脚本

**4-a. 开场（30s）**
> "我现在要做的事情听起来有点危险——**拔掉 MiniMax 云 API，换成本地 Qwen2.5-7B。**
> 一行命令，不重启浏览器，对话抽屉继续工作。"

**操作：** 终端执行：
```bash
export LLM_BACKEND=ollama
export OLLAMA_MODEL=qwen2.5:7b-instruct
pkill -f well_harness.demo_server
python3 -m well_harness.demo_server &
```

**4-b. Reload + 问一句（1:30）**
> "浏览器硬刷。[问'L3 为什么 active']—— 5 秒内，本地 Qwen2.5-7B 给出回答。
> Canvas 状态完全不变，因为真值引擎本来就没用 LLM。
> **今天演示的这条切换链已经真跑过——chat 的三个端点 explain/operate/reason
> 在 7B 上都通，平均 4–5 秒。**"

**4-c. 合规讲解（1:00）**
> "这对甲方意味着三件事：
> 1. **断网不影响演示**（R4 降级可控）
> 2. **敏感数据可以完全留在厂内**（不出境合规）
> 3. **AI 层不绑定单一供应商**——MiniMax / Qwen / GLM / DeepSeek 都是配置文件一行改动
>    （`config/llm/local_model_candidates.yaml`）。"

---

## 段 5 · R1–R5 宪法总结（2:30）

**目标：** 把前面的演示操作上升到原则层面，作为甲方的审查抓手。

### 脚本

**话术：**
> "这个系统由 5 条宪法原则支撑——每条都不是口号，都有代码/测试/真跑证据映射：

| 原则 | 在今天演示里怎么体现 | 证据文件 |
| ---- | -------------------- | -------- |
| **R1 真值优先** | 19 节点状态始终来自 controller.py，AI 从不改写 | `src/well_harness/controller.py` |
| **R2 AI 仅解释** | 关掉 AI 抽屉，节点逻辑不变 | `tests/test_controller.py`（真值回归） |
| **R3 可审计** | 蒙特卡洛字节级 replay，彩排 SHA-256 冻结 | `docs/freeze/2026-04-18-rehearsal-baseline.md` |
| **R4 降级可控** | 一行切 Ollama，demo 不中断 | `runs/demo_rehearsal_dual_backend_20260418T074215Z/report.json` |
| **R5 对抗守门** | 对抗测试 8/8 通过（注入/越权/绕过） | `src/well_harness/static/adversarial_test.py` |

> **每条原则都有 pytest 测试 + 真跑证据。**主 pytest 658 个测试通过，1 个
> 合法跳过；e2e 49 个全绿；对抗 8 个全绿。这就是 AI+工业逻辑在甲方场景下的
> 交付标准。"

---

## 段 6 · 闭场 + 请求立项决定（1:30）

**话术：**
> "今天演示的不是一个原型——是**一个可冻结、可审计、可降级、可国产化的
> 工程交付**。从 P15 到 P22，全部代码 + 文档 + 真跑证据都在仓库里，每个 commit
> 都有 trailer `Execution-by: opus47-max`。
>
> 我们请求的是：**把这个工作台从'项目'升级为'产品'**——
> 授权下一阶段与甲方安全工程团队 co-development，目标是 2026Q3 交付
> 首批产线生产级验证。
>
> 谢谢。"

**视觉提示：** 打开 `.planning/ROADMAP.md` 最后一页，停在"P20.2 Closed / P21 Closed"。

---

## 演讲者 Checkpoint 备忘

- **Demo 前 60 分钟：** 按 `docs/demo/preflight_checklist.md` 逐项过
- **如果 wow_b 10k 跑慢：** 降到 1k，引 `wow_b_timeline.json` 里的 48ms replay
- **如果 MiniMax 挂了：** 直接切 Ollama（脚本 4-a 那段就是真场景）
- **如果 Ollama 也挂了：** 跳过段 4，`docs/demo/disaster_runbook.md` 场景 1 有完整 fallback 链
- **甲方打断问问题：** 见 `docs/demo/faq.md` — 10+ 典型问答全部带证据路径

---

## 诚实性护栏

- 凡本稿里写"真跑"——必有 `runs/` 下 artefact。
- 凡本稿里写"代码行"——必有 `src/` 下文件 + 函数名。
- 凡本稿里写"测试通过"——必有 `pytest` 输出截图或 CI 记录。
- **如果演讲时发现某段证据文件不存在或过期，立刻跳过那段，不即兴编造。**
