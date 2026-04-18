# API 契约清单 — Well Harness v1

> **给谁看：** 甲方接入方工程师 + 安全评审工程师
> **回答什么：** 工作台当前对外暴露了哪些 API，请求/响应长什么样，版本怎么升
> **什么情况下变动：** 新增 field 只追加，不破坏 v1；破坏性变更另起 `/api/v2/*` 路径
> **最新校对日期：** 2026-04-18（main @ `2c7e7b2` 之后的 P22 冻结态）

---

## 0. 版本策略

- **当前版本：** v1（路径以 `/api/*` 起头，未带版本号即表示 v1）
- **向后兼容规则：**
  - 响应 JSON 可以**新增** field，消费方必须忽略未知 field
  - 不删除 field、不改字段名、不改类型
  - 请求 JSON 允许**新增 optional field**，不允许新增 required field
- **破坏性变更：** 必须起 `/api/v2/*` 新路径并发公告；`/api/v1/*` 至少共存 1 个季度
- **错误码：** 格式 `<backend>_<kind>`（例：`minimax_timeout` / `ollama_unreachable`）；前端降级徽标依赖前缀匹配，不依赖完整字符串

---

## 1. 三哇 API（数值通道，LLM-independent）

### 1.1 `POST /api/lever-snapshot` — wow_a 因果链

**用途：** 输入操纵量 + 传感器值，返回 19 节点的真值状态。

**Request schema:**
```json
{
  "tra_deg": -35,                       // number, throttle resolver angle, [-35, +35]
  "radio_altitude_ft": 2,               // number, 弧度英尺
  "engine_running": true,               // bool
  "aircraft_on_ground": true,           // bool
  "reverser_inhibited": false,          // bool
  "eec_enable": true,                   // bool
  "n1k": 0.92,                          // number, N1% 归一化 [0,1]
  "feedback_mode": "auto_scrubber",     // enum: "auto_scrubber" | "linear" | "frozen"
  "deploy_position_percent": 95,        // number [0,100]
  "fault_injections": []                // DEPRECATED since P18.5 — 接受但忽略
}
```

**Response schema:**
```json
{
  "nodes": [ /* 固定 19 个节点，顺序稳定 */
    {"id": "tra", "state": "active", "value": -35, "label": "TRA"}
    /* ... */
  ],
  "logic_gates": { "L1": true, "L2": true, "L3": true, "L4": false },
  "thr_lock": false,
  "truth_trace": { /* per-node derivation chain, for audit */ }
}
```

**合规锚点：** R1 真值优先（节点状态来自 `controller.py` 而非 AI）、R3 可审计（`truth_trace` 可回放）

---

### 1.2 `POST /api/monte-carlo/run` — wow_b 数值可靠性

**用途：** 参数不确定性下跑 N 次 controller，返回成功率分布。**完全不经过 LLM**。

**Request schema:**
```json
{
  "n_trials": 10000,    // int, 建议 [100, 50000]
  "seed": 42            // int, 提供则确定性 replay
}
```

**Response schema:**
```json
{
  "n_trials": 10000,
  "success_rate": 0.947,
  "elapsed_ms": 48,
  "seed": 42,
  "histogram": { /* 分桶直方图 */ }
}
```

**确定性保证：** 相同 `{n_trials, seed}` 保证字节级一致输出（见 `runs/dress_rehearsal_*/wow_b_timeline.json`）。

**合规锚点：** R3 可审计（seed replay）、R1（不触碰 truth engine）

---

### 1.3 `POST /api/diagnosis/run` — wow_c 反诊断

**用途：** 输入目标结论，枚举所有能达成它的参数组合路径。**枚举，不推理。**

**Request schema:**
```json
{
  "outcome": "thr_lock_active",         // enum: "thr_lock_active" | "logic1_active" | "logic3_active" | "deploy_confirmed" | "tls_unlocked"
  "max_results": 10,                    // int, default 10
  "system_id": "thrust-reverser"        // string
}
```

**Response schema:**
```json
{
  "outcome": "thr_lock_active",
  "diagnoses": [
    {
      "path_id": "d-001",
      "parameter_assignment": {"tra_deg": -35, "n1k": 0.92 /*...*/},
      "logic_gates_activated": ["L1","L2","L3","L4"],
      "confidence": "deterministic"       // 枚举所得，非推断
    }
    /* ... */
  ],
  "elapsed_ms": 72
}
```

**合规锚点：** R3（每条路径绑定节点 ID）、R5（不允许 AI 生成路径）

---

## 2. Chat API（AI 叙述通道，LLM-dependent）

三端点行为一致，差异在 system prompt。

### 2.1 `POST /api/chat/explain` · `/operate` · `/reason`

**Request schema:**
```json
{
  "question": "L3 为什么 active",
  "system_id": "thrust-reverser"
}
```

**Response schema（explain）:**
```json
{
  "answer": "自然语言叙述",
  "highlighted_nodes": ["logic3","tra","n1k"],
  "suggestion_nodes": [],
  "confidence": 0.82,                   // AI 自报，仅供 UI 展示
  "backend": "minimax"                  // "minimax" | "ollama"
}
```

**Response schema（operate）:** 同上加 `action` 字段，必须命中白名单 `VALID_ACTION_TYPES`；不合规则降级。

**Response schema（reason）:** 同 explain 加 `reasoning_chain[]`。

**失败时降级结构：**
```json
{"error": "minimax_timeout", "fallback_message": "AI 暂时不可用", "backend": "minimax"}
```

**合规锚点：** R2 AI 仅解释（UI 不得根据 action 直接改写 Canvas）、R4 降级可控（error 码前缀映射）、R5（prompt injection 白名单已在 handler 清洗）

---

## 3. 配套 API（非 wow 核心，供管理界面使用）

| 路径 | 方法 | 用途 |
|------|------|------|
| `/api/system-snapshot` | GET / POST | 全系统节点状态快照（用于 Canvas 初始化） |
| `/api/hardware/schema` | GET | 硬件 YAML schema 导出（P19.1） |
| `/api/monitor-timeline` | GET | 事件 timeline（用于彩排回放） |
| `/api/workbench/bootstrap` | POST | 工作台归档启动 |
| `/api/workbench/bundle` | POST | 工作台打包 + SHA256 校验（P18.6） |

完整列表见 `src/well_harness/demo_server.py` 文件头部的 `*_PATH` 常量。

---

## 4. 甲方接入方的版本承诺

| 项目 | 承诺 |
| ---- | ---- |
| `/api/v1/*` 生命周期 | 产品化后至少 2 个季度不破坏 |
| 新 field 前缀 | `x_*` 前缀表示实验性，不承诺稳定 |
| 错误码扩展 | 新 backend 加入时保持 `<backend>_<kind>` 格式 |
| Schema 导出 | 本文档每次 breaking release 同步更新，并在 `docs/freeze/` 落 SHA256 |

---

## 5. 真跑参考（证据）

- MiniMax + Ollama 双后端端到端通过：`runs/demo_rehearsal_dual_backend_20260418T074215Z/report.json`（14/14 PASS）
- 本地 7B smoke：`runs/local_model_smoke_20260418T072226Z/report.json`（3/3 PASS）
- 回归测试：`tests/test_llm_client.py`（19 tests 锁定 adapter 契约）
