# Wow A — 因果链高亮（19 节点真值引擎 + 4 logic gate）

**演示主题**：同一套 19 节点、同一台真值引擎，只改 1 个 lever，4 个 logic gate 按因果顺序亮灯。AI 只负责讲故事，故事错了不影响灯。

---

## 1. 开场台词（< 30s）

> "这不是演示动画。屏幕上这 19 个节点背后是一台真值引擎 —— 不是概率模型，不是 AI 猜测。
> 我给它三个节拍：早、深、空。每次只改一个 lever，看 4 个 logic gate 按因果顺序亮灯。
> AI 在旁边讲故事。它讲错了，灯照样是对的 —— 这是我们刻意做的隔离。"

---

## 2. Keystroke 序列（3 步）

### Step 1 — 节拍"早"（浅拉 + 着陆姿态）
- **URL**：`POST /api/lever-snapshot` on `http://127.0.0.1:8799`
- **点击目标**：canvas 顶部 `#canvas-global-controls` 区域 → `tra_deg` 拉杆
- **输入内容**：`tra_deg=-5`，其余维持 landing 默认（`radio_altitude_ft=2, engine_running=true, aircraft_on_ground=true, reverser_inhibited=false, eec_enable=true, n1k=0.8, feedback_mode=auto_scrubber, deploy_position_percent=90`）

### Step 2 — 节拍"深"（深拉 + 高 N1K）
- **URL**：同上 `POST /api/lever-snapshot`
- **点击目标**：同 `tra_deg` 拉杆 + `n1k` slider + `deploy_position_percent` input
- **输入内容**：`tra_deg=-35, n1k=0.92, deploy_position_percent=95`

### Step 3 — 节拍"空"（抬飞机 / 负面控制）
- **URL**：同上
- **点击目标**：`aircraft_on_ground` toggle + `radio_altitude_ft` input
- **输入内容**：在 Step 1 基础上改 `radio_altitude_ft=500, aircraft_on_ground=false`

---

## 3. 预期 AI 输出（文字描述）

- **Step 1 AI 叙述**：着陆姿态 + TLS unlock 确认 → 前两档亮；TRA 只到 -5° 未达深拉阈值，canonical pullback 短，plant 只 deploy ~6%，logic3/4 按住不动
- **Step 2 AI 叙述**：深拉过线 → auto_scrubber 在 ~4.4s 内驱动 plant VDT 到 100%，反馈节点 `deploy_90_percent_vdt` 翻位 → 真值引擎一次 POST 内端到端跑完 logic2 → logic3 → logic4 → thr_lock 因果链；logic1 在 deploy 完成后因 `reverser_not_deployed_eec` 翻位而熄灭，这是真值引擎的实时状态机投影，不是 AI 填充
- **Step 3 AI 叙述**：飞机抬升到空中 → 链路第一道门断裂，不看 TRA 多深，先看姿态；safety-first 的 interlock 严守因果

---

## 4. UI 预期（节点高亮 / 连线流光 / Canvas 状态）

- **Step 1**：logic1 + logic2 节点点亮（活性色）；logic3/logic4 保持待命灰；连线从 input 节点流向 logic1/2
- **Step 2**：logic2 + logic3 + logic4 同步点亮，thr_lock 解锁；logic1 在 reverser 完全 deploy 后因 `reverser_not_deployed_eec` 翻位而熄灭；连线流光从 input → logic2 → logic3 → 反馈节点 `vdt90` → logic4 → thr_lock，呈现端到端因果链（包含反馈回路本身的视觉走线）
- **Step 3**：4 个 logic 节点全灰；连线从 `radio_altitude_ft` 节点出发后**立即熄灭**（在 logic1 前断开），其他 lever 保持不变

---

## 5. Timing Budget

| 动作 | 预算 | 锚点 |
|---|---|---|
| 单次 `/api/lever-snapshot` warm | < 500ms | `test_wow_a_response_under_500ms_warm` |
| 连续 3 节拍 HTTP 往返 | < 2s | 真值引擎确定性 |
| Canvas 重绘 | < 100ms 每节拍 | 浏览器端，无后端依赖 |
| 讲解 + 演示总时长 | < 15s（不含 AI 叙述） | 现场节奏控制 |

---

## 6. 降级台词（AI 延迟 > 10s 或拒答）

> "AI 讲故事卡了一下 —— 没关系，看灯。真值引擎是决定者，AI 只是解释者。
> logic2 → logic3 → logic4 按我说的顺序亮起来了，因果顺序写在链路里，不在 LLM 里。
> 演示期间 AI 挂了，安全不挂。这正是我们的架构红线 —— R2 原则。"

---

## 7. 证据链

**Commit**：`4fc4db5 test(P20.0-A,C): e2e coverage for 3 wow scenarios + demo resilience`
**测试文件**：`tests/e2e/test_wow_a_causal_chain.py`
**对应测试函数**：
- `test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields` — 锁 19 节点 + {id, state} 契约
- `test_wow_a_lever_snapshot_exposes_four_logic_gates` — 锁 4 logic gate 命名
- `test_wow_a_beat_early_activates_logic1_and_logic2_only` — Step 1
- `test_wow_a_beat_deep_activates_logic2_and_logic3` — Step 2（在 auto_scrubber 模式下锁 logic2 + logic3 + logic4 同时 active；测试名为历史命名保留稳定，断言契约见函数 docstring）
- `test_wow_a_beat_blocked_deactivates_entire_chain` — Step 3
- `test_wow_a_truth_engine_is_deterministic` — 同输入 byte-identical
- `test_wow_a_response_under_500ms_warm` — Timing 预算锚
- `test_wow_a_lever_snapshot_evidence_field_present` — LLM 叙述所需字段存在

**Notion 战略页**：AI FANTUI LogicMVP 控制塔 → P19 Sprint → 3 哇瞬间 Deck
URL：https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec

**架构红线**：R1（真值优先）+ R2（AI 仅解释）+ R5（adversarial 8/8 守门）

---

**Execution-by**：opus47-max
