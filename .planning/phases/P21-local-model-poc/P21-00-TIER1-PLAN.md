---
phase: P21
plan: P21-00
type: tier1-overview
wave: 0
depends_on: [P20.2]
files_created: []  # Tier 1 Plan has no direct file deliverables — each sub-phase does
files_modified: []
autonomous: false
freeze_constraints:
  - "R1 真值优先 / R2 AI 仅解释 / R3 可审计 / R4 降级可控 / R5 adversarial 守门 全部维持"
  - "truth engine (controller.py / 19-node / 4 logic gates) 零触碰"
  - "主 pytest 639/1skip 基线必须守住；opt-in -m e2e 49 全绿"
  - "adversarial 8/8 不退化"
  - "MiniMax cloud backend 保持可用（作为降级兜底），不是被替换而是被并列"
exit_criteria_at_phase_level:
  - "3 wow moments 可用完全离线的国产开源 LLM 跑通，生成合理叙述"
  - "切换指令单行可控：LLM_BACKEND={minimax|ollama} 环境变量即可切换"
  - "立项汇报物 docs/demo/local_model_poc.md 含架构图 + 切换演示脚本 + 性能数据"
  - "disaster_runbook.md 新增场景：MiniMax 不可用→自动切 Ollama（<60s 恢复）"
---

# P21 Tier 1 Plan — 国产模型本地 PoC（立项汇报王牌）

## 0 · Why（动机）

项目当前三条 LLM 路径（`/api/chat/explain` · `/api/chat/operate` · `/api/chat/reason`）全部硬编码 MiniMax cloud API (`https://api.minimax.chat/v1/text/chatcompletion_v2`)。
立项汇报场景下 Kogami 需回答两个硬问题：

1. **"断网能不能演？"** — 当前答案：能（R2 降级路径），但只剩真值引擎输出，叙述层空白。
2. **"数据出不出境？国产化合规怎么讲？"** — 当前答案：MiniMax 本身国产，但仍是 SaaS；审查者会问"不走外网怎么跑"。

P21 的目标是把两个答案同时升级为："能，而且断网也有叙述——因为 LLM 可切本地国产开源模型（Qwen/GLM/DeepSeek）跑在演示机上"。
这不是替换 MiniMax，而是**在 MiniMax 旁边并列一条本地后端**，切换成本等于一个环境变量。

## 1 · Non-Goals（明确不做什么）

- **生产级 benchmark 矩阵**：PoC 不追求量化精度、吞吐、多模型横评。
- **GPU 机柜方案**：PoC 只需证明"能在一台 Mac M-series 或一台带 4090 的 Linux 上跑起来"。
- **模型微调**：PoC 用官方 instruct 版权重，不 fine-tune。
- **质量平权证明**：不构建"本地模型 vs MiniMax"的盲测对比集——R2（AI 仅解释）已把 LLM 降到非关键路径，本 PoC 不承担质量保证责任。
- **替换 MiniMax**：MiniMax 继续是 default backend，本地模型是**并列可选**。

## 2 · Scope（范围）

### 2.1 代码改动面（src/ 业务改动仅一处：抽 adapter 边界）

```
src/well_harness/demo_server.py
  • _get_minimax_api_key() 保持原样（向后兼容）
  • 3 × LLM 调用块 (_handle_chat_explain / _handle_chat_operate / _handle_chat_reason)
    内部约 500 行 HTTP + JSON parsing 样板，抽到新模块

src/well_harness/llm_client.py  [NEW]
  • LLMClient Protocol: chat(messages, *, temperature, max_tokens, timeout) -> str
  • MiniMaxClient(LLMClient)  — 当前 inline 代码平移
  • OllamaClient(LLMClient)   — 新增，走 http://localhost:11434/api/chat
  • get_llm_client() factory — 读 LLM_BACKEND env, 默认 'minimax'

tests/test_llm_client.py  [NEW]
  • MiniMaxClient mock 网络层 happy/error path
  • OllamaClient mock 网络层 happy/error path
  • get_llm_client() factory 路由逻辑
```

**不改的文件（写死，任何 sub-phase 都不能碰）：**
- `controller.py`（真值引擎）
- 所有 `test_*_truth_engine*.py`
- `tests/e2e/test_wow_{a,b,c}_*.py` 的断言（参数化 fixture 可改）
- `src/well_harness/static/adversarial_test.py`

### 2.2 Phase 内资源

```
config/llm/local_model_candidates.yaml  [NEW]
  • 候选模型矩阵：qwen2.5-7b-instruct / glm-4-9b-chat / deepseek-v2.5-lite
  • 每项：ollama pull 命令 / 预估 RAM / 适合的 prompt template

docs/demo/local_model_poc.md  [NEW]
  • 架构图（adapter 模式）· 切换演示 · 性能数据 · 断网演示剧本

docs/demo/disaster_runbook.md  [PATCH]
  • 场景 1 (MiniMax 降级) 新增"自动切 Ollama"恢复动作

scripts/local_model_smoke.py  [NEW]
  • 启动 demo_server + LLM_BACKEND=ollama
  • 三 wow 路径 HTTP 重放，断言 evidence/explanation 非空
```

## 3 · Sub-Phase 分解

| Sub | Name | 工作日 | 关键产出 | 停不停 |
|-----|------|-------|---------|-------|
| P21-01 | LLM adapter 边界抽取 | 1–2d | `llm_client.py` + `test_llm_client.py` + demo_server 3 点位 refactor · MiniMax 路径零回归 | **自动** |
| P21-02 | Ollama 后端 + 候选模型矩阵 | 2–3d | `OllamaClient` 实现 + `config/llm/local_model_candidates.yaml` + 首选 qwen2.5:7b 验证 | **自动** |
| P21-03 | e2e 参数化 + 本地烟雾脚本 | 1–2d | `tests/e2e/conftest.py` 加 `llm_backend` fixture · `scripts/local_model_smoke.py` 真跑 | **自动** |
| P21-04 | 立项汇报物 + disaster 更新 | 1–2d | `docs/demo/local_model_poc.md` · disaster_runbook.md PATCH · 架构图 (ASCII/Mermaid) | **自动** |
| P21-05 | Phase 收口 Gate + main merge | 0.5d | Executor 初审 + Notion 04A 条目建为 Awaiting + 治理同步 · branch 清理 · 待 Kogami 触发 Notion AI Opus 4.7 独立 Gate | **自动至 Gate 待审** |

**总工期估计：** 5.5–10.5 工作日（≈ 1.5–2 周）

## 4 · 架构契约（adapter 抽取后）

```
┌─────────────────────────────────────────────────────────┐
│  demo_server.py routes                                  │
│    /api/chat/explain  /api/chat/operate  /api/chat/reason│
│             │                                           │
│             ▼                                           │
│  get_llm_client()  ← reads os.environ['LLM_BACKEND']    │
│             │                                           │
│       ┌─────┴──────┐                                    │
│       ▼            ▼                                    │
│  MiniMaxClient  OllamaClient    (VLLMClient 留扩展位)   │
│  api.minimax    localhost:11434                         │
│                                                         │
│  共享 Protocol: chat(messages) -> str                   │
│  共享错误语义: LLMClientError 子类                      │
└─────────────────────────────────────────────────────────┘
```

关键不变量：
- demo_server.py 的 routes handler 对 client 类型透明——只看 str 返回或 raise LLMClientError
- 现有降级路径（`minimax_api_key_missing` → front-end `chat-degraded-notice`）通过 **client 层映射**得到保持：OllamaClient 连不上 localhost:11434 时触发等价 `ollama_unreachable` 错误，前端降级 UI 相同

## 5 · 风险矩阵（每项含检测手段）

| # | 风险 | 概率 | 影响 | 检测手段 | 缓解 |
|---|-----|-----|-----|---------|-----|
| R1 | Ollama 响应结构与 MiniMax 不一致，导致 explanation 字段解析失败 | 中 | 前端降级 UI 显示乱码 | `tests/test_llm_client.py` 两路 fixture 断言 `chat()` 返回 str | 在 OllamaClient 内部完成 shape 归一化，向上只暴露 str |
| R2 | 本地 7B 模型生成速度 > 30s，超出 MiniMax 降级 timeout | 中 | 演示现场卡顿 | `scripts/local_model_smoke.py` 打印每路 elapsed_ms，warn if >5s | `max_tokens` 压到 300（MiniMax 默认 600）；prompt 加"极简回答"指令；7B 不够则降 4B (qwen2.5:3b) |
| R3 | `ollama pull` 需要 GB 级下载，会场无网络时不可用 | 低 | 演示机没模型文件 | PoC 交付时 bundle 一份 qwen2.5:7b 的 `~/.ollama/models/` 目录到冻结包 | 冻结基线 tarball 新增 `local_model_weights/` 子目录（如确需） |
| R4 | LLM_BACKEND 切换导致主 pytest 回归（639→<639） | 低 | main CI 红 | 每 sub-phase 末尾必须跑 `pytest -m "not e2e" -q` 并贴 tail -3 | MiniMaxClient 路径保持 default；测试用 `monkeypatch.setenv` 显式切换 |
| R5 | 国产模型生成内容触发敏感词过滤，输出 "" 或拒绝 | 低 | 现场生成空白 | 三 wow prompt 预先离线 smoke 三次，记在 `docs/demo/local_model_poc.md` 中 | 备用 prompt 预置（换措辞）；前端已有 empty response 降级 UI |
| R6 | Sub-phase 并行被主 branch 其它改动截胡 | 低 | rebase 冲突 | 每 sub-phase 开 commit 前 `git fetch && git rebase origin/main` | 所有 sub-phase 在 `feat/p21-local-model-poc` 单一 branch 串行 |
| R7 | PoC 被误读为"MiniMax 弃用"，引发下游期望混乱 | 中 | 立项汇报 message 跑偏 | `docs/demo/local_model_poc.md` 首句明确"MiniMax 继续是 default；本 PoC 是并列选项" | 同上，并在 Notion DECISION 记录里固化 |

## 6 · Exit Criteria（Phase 级，不到位就不收口）

- [ ] 主 pytest: 639 passed, 1 skipped（基线不变）
- [ ] Opt-in e2e: 49 passed（现有）+ 新增 ≥3 条（wow_{a,b,c} 参数化跨 backend），总 ≥52
- [ ] Adversarial: 8/8
- [ ] `LLM_BACKEND=ollama ollama serve & python3 scripts/local_model_smoke.py` 真跑 3/3 wow 路径绿，每路 elapsed_ms 落盘
- [ ] `docs/demo/local_model_poc.md` 含：为什么国产化、adapter 架构图、切换命令单、3 wow 路径演示脚本、性能数据
- [ ] `docs/demo/disaster_runbook.md` 场景 1 追加"自动切 Ollama"恢复动作
- [ ] Executor 初审完成 + Notion 04A GATE-P21-CLOSURE 建为 Awaiting + 治理同步（02B/04A/05/06/控制塔/决策日志）+ 等 Kogami 触发 Notion AI Opus 4.7 独立 Gate

## 7 · 固定结尾

**请 Kogami 确认 P21 Tier 1 Plan 范围与分解，确认后启动 P21-01 adapter 抽取（完全自动驾驶到 P21-05 收口）。**

---

_Execution-by: opus47-max (Claude Code Opus 4.7, 20x Max) · v3.0 双 Opus + v3.1 停机白名单 · Gate 由 Notion AI Opus 4.7 独立签署_
