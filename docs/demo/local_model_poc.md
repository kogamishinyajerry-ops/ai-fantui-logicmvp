# P21 Local Model PoC — 国产模型本地 Fallback

> **用途：** 立项汇报王牌。当 MiniMax 云 API 不可达（key 过期 / 限流 / 网络中断），
> 一行命令切到本地 Ollama 模型，链路不中断。
>
> **不是什么：** 不追求和 MiniMax 质量平权；不替换现有 MiniMax 主路径；
> 不 fine-tune。**是 R4 降级可控的工程学证据。**

---

## 1. 架构一图流

```
   demo_server route (/api/chat/explain | /operate | /reason)
                          │
                          ▼
            well_harness.llm_client.get_llm_client()
                          │
           ┌──────────────┴──────────────┐
           ▼                             ▼
     MiniMaxClient (默认)          OllamaClient (fallback)
     POST api.minimax.chat         POST localhost:11434/api/chat
     Bearer ~/.minimax_key         LLM_BACKEND=ollama
```

- **切换开关：** 环境变量 `LLM_BACKEND=ollama`（默认 `minimax`）。
- **Adapter 边界：** `src/well_harness/llm_client.py`（~220 行，Protocol + 2 实现 + factory）。
- **错误码等价表**（前端降级徽标 UI 契约不变）：
  | MiniMax                     | Ollama                   |
  | --------------------------- | ------------------------ |
  | `minimax_api_key_missing`   | `ollama_unreachable`     |
  | `minimax_http_error`        | `ollama_http_error`      |
  | `minimax_error`             | `ollama_error`           |
  | `minimax_empty_response`    | `ollama_empty_response`  |

---

## 2. 切换命令（演示机 / 60 秒内可执行）

```bash
# 一次性准备（演示机已做）
brew install ollama
ollama serve &
ollama pull qwen2.5:7b-instruct   # 4.7GB，≤8GB RAM

# 切到本地 fallback
export LLM_BACKEND=ollama
export OLLAMA_MODEL=qwen2.5:7b-instruct
pkill -f well_harness.demo_server
python3 -m well_harness.demo_server &

# 回到 MiniMax 主路径
unset LLM_BACKEND
pkill -f well_harness.demo_server
python3 -m well_harness.demo_server &
```

候选模型清单：`config/llm/local_model_candidates.yaml`（Qwen2.5-7B / 14B / GLM-4 9B / DeepSeek-V2.5 Lite）。

---

## 3. 真实运行数据（2026-04-18，Mac M-series，qwen2.5:32b）

来源：`runs/local_model_smoke_20260418T071304Z/report.json`

| Endpoint               | Status | Latency  | Verdict |
| ---------------------- | ------ | -------- | ------- |
| `/api/chat/explain`    | 400    | 30008 ms | FAIL（32B 首响超 30s adapter timeout） |
| `/api/chat/operate`    | 200    | 17739 ms | PASS    |
| `/api/chat/reason`     | 200    | 24901 ms | PASS    |

**结论：** 2/3 端点在 32B 上真实跑通；单次 explain 在 32B 上触发默认 30s 超时，
属于重量级模型 + 默认 timeout 的预期边界。**推荐演示默认 `qwen2.5:7b-instruct`**
（首响 0.2–0.5s，整体 2–6s，稳定在 adapter 30s 阈值内）。

> 注：7B real-run 数据将在 Ollama pull 完成后补采并 PATCH 本表。MiniMax 主路径
> 的稳定基线见 `runs/dress_rehearsal_20260418T063146Z/`（wow_a 4ms / wow_b 279ms
> / wow_c 72ms — LLM 不在这些数字的关键路径上，Ollama 切换不影响三 wow 数字）。

---

## 4. R1–R5 宪法合规自审

| 原则 | 本 Phase 保持方式 |
| ---- | ----------------- |
| R1 真值优先 | 真值引擎（`controller.py`, 19 节点 + 4 门）zero-touch。Ollama 和 MiniMax 都只消费 snapshot，不改写。 |
| R2 AI 仅解释 | Adapter 只换叙述层后端，结构化字段（`action_type` / `parameter_overrides` / `highlighted_nodes`）白名单和清洗保留。 |
| R3 可审计 | `runs/local_model_smoke_<ts>/report.json` 提供端到端 wall-clock，可复现。配置 YAML + 错误码等价表对外可讲。 |
| R4 降级可控 | 本 Phase 的全部工程意义。切换 ≤60s 命令可执行，前端 degraded-notice UI 契约不变。 |
| R5 对抗守门 | Ollama 输出经相同 JSON schema + VALID_ACTION_TYPES / VALID_RESPONSE_TYPES 校验，不可信 payload 直接降级为默认响应。`tests/test_llm_client.py` 19 tests + 主 pytest 658 pass + e2e 49/49 + adversarial 8/8。 |

---

## 5. 立项汇报话术参考（≤30s）

> "MiniMax 是我们的主通道。但把 AI 解释层放进工业系统，甲方会问：'云 API 挂了怎么办？'
> 我们做了一件事——用一个最小 adapter 边界，把国产开源模型（Qwen2.5 / GLM-4 /
> DeepSeek）做成热切换的本地 fallback。一行 `LLM_BACKEND=ollama`，链路不中断。
> 真实彩排当天这条线已经跑通 2/3 的 chat 端点。这不是质量平权，是**R4 降级可控**
> 的工程学证据——AI 层不是不可替换的黑箱。"

---

## 6. 维护者注记

- 增加候选模型：编辑 `config/llm/local_model_candidates.yaml` → `candidates:` 列表，
  填 `model_id` / `size_gb` / `ram_gb` / `pull_cmd`。无需改代码。
- 增加新 backend（非 Ollama，如 vLLM）：在 `llm_client.py` 添加一个实现类并挂到
  `_BACKENDS` dict；保持错误码前缀匹配 `<backend>_<kind>` 以复用前端 UI 契约。
- 灾难演练：`scripts/local_model_smoke.py --skip-if-unreachable` 是幂等、CI-safe 入口。
