# 立项汇报 FAQ — 甲方典型问题 × 应答 × 证据

**格式约定：**
- 每条问答带 **证据文件** 字段——应答不引用代码/文档/真跑 artefact 的，不写进本文档。
- 每条标注 **R-原则** 锚点——让甲方快速找到合规抓手。
- **严格遵守 R3 可审计：凡答案里提到的数字/路径/测试，都必须真实可验证。**

---

## 基础架构类

### Q1. 你们的 AI 和传统专家系统有什么区别？

**A:** 我们**不是**用 AI 替代专家系统；是**把专家系统（truth engine）放在 AI 前面**。
`src/well_harness/controller.py` 的 19 节点 + 4 逻辑门是确定性的——同样输入永远同样输出。
AI 只在真值引擎产生结论后负责"翻译成人话"。换句话说：AI 答错了，控制结论也不错。

- R-锚点：**R1 真值优先 · R2 AI 仅解释**
- 证据：`src/well_harness/controller.py` · `tests/test_controller.py`（真值回归测试）

---

### Q2. 19 节点 + 4 逻辑门这个规模，能 scale 到真实产线系统吗？

**A:** 当前 19 节点是反推力逻辑链的**实际工程规模**（来自航空逆推控制子系统参考）。
架构本身不绑定节点数——`controller.py` 的门函数 + 节点状态机是数据驱动的，
扩展到 100/1000 节点不需要改架构。我们已经在 `P14/P15` 验证了"文档 → spec → 运行时"
端到端链，未来接其他控制域只需替换 YAML 硬件描述。

- R-锚点：**R1 真值优先**（节点表扩展不影响真值边界）
- 证据：`config/hardware/thrust_reverser_hardware_v1.yaml` · `.planning/ROADMAP.md` Phase P8/P10

---

### Q3. 为什么选 Python 做 runtime？工业场景不担心性能？

**A:** 演示用 Python 因为迭代速度快。性能数据在真跑报告里：**wow_a 因果链 4ms，
wow_b 10,000 次蒙特卡洛 48ms，wow_c 反诊断 72ms**——远快于甲方业务的决策周期。
如果未来要嵌入实时控制回路（非当前 scope），controller.py 的门逻辑可以直接
port 到 C/Rust；AI 叙述层保持在服务侧。

- 证据：`runs/dress_rehearsal_20260418T063146Z/rehearsal_report.md`

---

## 合规 / 安全类

### Q4. AI 会产生幻觉，怎么保证它不在安全关键场景说错话？

**A:** 两层护栏：
1. **结构层：** AI 不参与决策。Canvas 节点状态来自 truth engine，AI 输出**不写回** Canvas。
   拔掉 AI 服务，控制逻辑照跑。
2. **输入验证层：** `/api/chat/operate` 返回的 JSON 必须命中白名单 `action_type` 和
   `parameter_overrides` 字段清洗；不合规直接降级为默认响应。对抗测试 8/8 通过。

- R-锚点：**R2 · R5**
- 证据：`src/well_harness/llm_client.py` · `src/well_harness/static/adversarial_test.py`
  · `src/well_harness/demo_server.py`（operate handler 白名单逻辑）

---

### Q5. 数据出境怎么解决？MiniMax 是云 API，甲方数据可能落国外。

**A:** P21 已交付本地模型 fallback。一行命令切 Ollama + Qwen2.5-7B，
**所有 prompt 和 response 留在厂内**。候选模型都是国产开源（Qwen / GLM / DeepSeek），
pull 命令都在 `config/llm/local_model_candidates.yaml`。真跑证据：7B 下 chat 三端点
全绿，4.2–5.4s 延迟。

- R-锚点：**R4 降级可控**
- 证据：`docs/demo/local_model_poc.md` · `runs/local_model_smoke_20260418T072226Z/report.json`
  · `runs/demo_rehearsal_dual_backend_20260418T074215Z/report.json`

---

### Q6. 审计的时候你们能给什么？

**A:** 三层证据：
1. **代码层：** 所有 commit 都有 `Execution-by: opus47-max` trailer，git log 可回溯每次改动由谁做。
2. **测试层：** 主 pytest 658 通过 + 1 合法 skip / e2e 49 通过 / 对抗 8 通过。
3. **真跑层：** `runs/` 目录每次演示/彩排都产 artefact（JSON 报告 + timeline），
   `docs/freeze/` 保留带 SHA-256 的冻结基线。

同样种子的蒙特卡洛跑 5 次字节级一致——这就是可复现性的具体形态。

- R-锚点：**R3 可审计**
- 证据：`docs/freeze/2026-04-18-rehearsal-baseline.md`（SHA-256
  `df00dd9b230131a07effa3092eb12481cfb34118b252f1df5f352e2253453350`）

---

### Q7. 如果演示当天 MiniMax 429 / 超时 / 断网了怎么办？

**A:** `docs/demo/disaster_runbook.md` 7 个场景 × 4 字段（检测信号/立即话术/
恢复动作/最坏兜底）全部 <60s 可执行。场景 1 首选是直接切 Ollama 本地 fallback，
备选是换备份 MiniMax key。最坏情况跳过 AI 叙述直接展示 truth engine 原始 JSON——
"AI 只解释不决策"的 R2 原则恰好在此被证明。

- R-锚点：**R4 降级可控**
- 证据：`docs/demo/disaster_runbook.md` · `docs/demo/local_model_poc.md`

---

## 产品 / 供应商类

### Q8. 这个架构绑不绑定 MiniMax？换模型成本多大？

**A:** 不绑定。`src/well_harness/llm_client.py` 是 Protocol + 工厂模式，
当前支持 MiniMax 和 Ollama 两个 backend；新加一个 backend（例如 vLLM 或甲方自己部署的模型）
只需实现一个 `chat()` 方法 + 在 `_BACKENDS` dict 注册。**前端 UI 契约不变**——
错误码前缀做了等价表，前端"降级徽标"逻辑零改动。

- R-锚点：**R4**
- 证据：`src/well_harness/llm_client.py` · `tests/test_llm_client.py`（19 tests 覆盖适配器契约）

---

### Q9. 你们依赖 Opus 4.7 / Claude 这类外部 AI 工具——交付到甲方后怎么维护？

**A:** 区分两件事：
1. **运行时依赖**（演示/产线跑）：只依赖 MiniMax 或 Ollama（国产开源模型），**没有 Claude**。
2. **开发期依赖**（我们这边写代码）：用 Opus 4.7 加速。但所有 commit、测试、文档都是
   人类可读的产物，甲方接手后用任何工具维护都不受影响。

交付物里**没有**任何"必须由 Claude 才能跑"的代码或脚本。

- 证据：`requirements.txt`（无 anthropic 依赖）· `src/well_harness/llm_client.py`（adapter 只含 MiniMax + Ollama）

---

### Q10. 从 P22 到产品化还要多久？

**A:** 本次立项汇报目标是**把工作台从项目升级为产品**。当前已经冻结的能力：
truth engine / wow_a/b/c / MiniMax+Ollama 双后端 / 灾难手册 / 可审计彩排基线 /
对抗测试通过。如果获批立项，下一步是 co-development：与甲方安全工程团队对齐
**一个真实子系统** 的文档→spec→运行时链，目标 2026Q3 首批产线 validation。

- 证据：`.planning/ROADMAP.md`（历史 P1–P17 已交付节点）

---

## 对抗 / 边界类（R5 锚点）

### Q11. 如果用户恶意输入想让 AI 解读错，你们怎么防？

**A:** 三层：
1. **prompt injection 白名单：** operate / reason handler 校验返回的 JSON schema
   (`VALID_ACTION_TYPES` / `VALID_RESPONSE_TYPES`)，不合法直接降级。
2. **parameter_overrides 清洗：** 参数白名单 + 类型校验，AI 返回 `system_override: rm -rf /`
   这类 payload 会被直接丢弃。
3. **对抗测试：** `src/well_harness/static/adversarial_test.py` 8 个场景覆盖
   幂等/边界/快速循环/前端权威/全链路验证，每次 CI 都跑。

- 证据：`src/well_harness/static/adversarial_test.py`（当前 8/8 通过）

---

### Q12. AI 说谎怎么办？模型有时候非常自信地给错误答案。

**A:** 这正是"AI 仅解释"的意义。如果 AI 在 wow_a 的叙述里说错（比如说 L3 激活
但 Canvas 上 L3 实际是灰色），**观众立刻能看见矛盾**——因为 Canvas 显示的是
truth engine 的事实，不是 AI 的说法。错配是**显性的**，不是**隐性的**。

我们演示时会故意演示"关闭 AI 抽屉，Canvas 节点状态不变"来强化这个点。

- 证据：`docs/demo/pitch_script.md` 段 1-d「AI 叙述开关」

---

### Q13. 那 AI 在这个系统里到底有什么用？感觉像装饰。

**A:** AI 做两件事**人类做不动**的工作：
1. **实时把 19 节点状态翻译成自然语言**——工程师可以用"解释 L3 为什么亮"这类
   自然问句，而不是盯着状态机读 JSON。
2. **反诊断用户意图的叙述化**——wow_c 枚举出 7 条触发路径后，AI 把 7 条技术路径
   翻译成"如果你想激活 THR_LOCK，最推荐这一条，因为……"。

AI 做**叙述层优化**，不做**决策层生成**。这是设计约束，不是缺陷。

- 证据：`src/well_harness/demo_server.py` explain/operate/reason 三个 handler 的 system prompt

---

## 工程细节类

### Q14. 控制逻辑改了，怎么保证 AI 叙述同步？

**A:** AI 叙述在运行时从 `/api/lever-snapshot` 拿最新节点状态作为 context——
controller.py 改了，下一次请求 AI 就看到新状态。AI **不缓存** 控制逻辑的知识。
这意味着：改 controller.py 不需要改 prompt，也不需要 re-train。

- 证据：`src/well_harness/demo_server.py` chat handlers 如何 inject snapshot 到 system prompt

---

### Q15. 如果甲方想接入自己的 AI（已经部署好的大模型），要改多少代码？

**A:** 实现一个新的 `*Client` 类，继承 `LLMClient` Protocol 的 `chat()` 方法，
在 `_BACKENDS` dict 里加一行——**预估 <50 行代码**。错误码用 `<backend>_<kind>`
前缀命名以复用前端降级 UI。`tests/test_llm_client.py` 里的 MiniMax/Ollama 测试
就是模板。

- 证据：`src/well_harness/llm_client.py`（当前 ~220 行，含 2 个 backend）

---

## 演讲者速查卡

| 问题关键词 | 跳转 Q |
| ---------- | ------ |
| 幻觉 / AI 说错 | Q4 · Q12 · Q13 |
| 数据出境 / 云 | Q5 |
| 审计 / 证据 | Q6 |
| 断网 / 挂了 / 429 | Q7 |
| 供应商绑定 / 换模型 | Q8 · Q15 |
| 维护 / Claude 依赖 | Q9 |
| 产品化 / 时间表 | Q10 |
| 对抗 / 攻击 / 注入 | Q11 |
| 节点规模 / scale | Q2 |
| 性能 / 延迟 | Q3 · Q5 |
