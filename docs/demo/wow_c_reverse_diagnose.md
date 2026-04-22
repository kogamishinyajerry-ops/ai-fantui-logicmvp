# Wow C — 反向诊断（选择 outcome，回溯可行参数组合）

**演示主题**：工程师不问"这组 lever 会怎样"，反过来问"想要 `deploy_confirmed` 需要哪些参数组合"。真值引擎做网格搜索，返回可行域。这不是搜索展示，是设计工具。

---

## 1. 开场台词（< 30s）

> "Wow A 是「给 lever 算结果」，Wow B 是「重复跑统计」。
> Wow C 反过来 —— 工程师指一个目标状态，比如 `deploy_confirmed`，引擎倒推出能到达这个状态的所有 lever 组合。
> 6 个可枚举 outcome，每个都能反向走。这不是 search UI，是可复用的设计工具。"

---

## 2. Keystroke 序列（3 步）

### Step 1 — 正向反向诊断（deploy_confirmed）
- **URL**：`POST /api/diagnosis/run` on `http://127.0.0.1:8799`
- **点击目标**：`#chat-drawer` → `#chat-analysis-btn` → Reverse Diagnosis 子面板 → outcome 下拉框 → `max_results` 输入框 → Run
- **输入内容**：`{"system_id": "thrust-reverser", "outcome": "deploy_confirmed", "max_results": 10}`

### Step 2 — 遍历 6 个合法 outcome（覆盖面验证）
- **URL**：同上，重复 6 次
- **点击目标**：outcome 下拉框依次切换
- **输入内容**：outcome 依次 = `logic3_active / logic1_active / thr_lock_active / deploy_confirmed / tls_unlocked / pls_unlocked`；`max_results=1`

### Step 3 — 非法 outcome 的降级反馈（自恢复哇点）
- **URL**：同上
- **点击目标**：outcome 框手动输入（绕过下拉校验）
- **输入内容**：`{"system_id": "thrust-reverser", "outcome": "banana_outcome"}`

---

## 3. 预期 AI 输出（文字描述）

- **Step 1 AI 叙述**：找到 N 组参数组合都能到达 `deploy_confirmed`；每组精确到 RA 英尺数、TRA 度数、两开关闭合状态、两把锁 unlock 状态；`grid_resolution` 和 `timestamp` 可见
- **Step 2 AI 叙述**：6 个 outcome 全部可反向到达 + 200 OK；如果明天产品部门加一种新 outcome，在 truth engine 定义后立刻变成可反查目标
- **Step 3 AI 叙述**：输错 outcome 不崩；错误文案把 6 个合法选项**全部列出**，现场工程师可以直接复制粘贴自恢复

---

## 4. UI 预期（表格 / 错误提示）

- **Step 1**：Reverse Diagnosis 面板显示结果表格；每行 6 列（`radio_altitude_ft / tra_deg / sw1_closed / sw2_closed / tls_unlocked / pls_unlocked`）；`grid_resolution` + `timestamp` 在面板顶部可见
- **Step 2**：6 次切换，每次表格刷新；outcome 标签回显请求值；`grid_resolution` 每次更新
- **Step 3**：结果区变红色错误提示框；文案写出 6 个合法 outcome（操作员可直接点击填回）；不白屏不 5xx

---

## 5. Timing Budget

| 动作 | 预算 | 锚点 |
|---|---|---|
| 单次 `/api/diagnosis/run` | < 1s（观察性） | Step 1 和 Step 2 每次 |
| 6 个 outcome 遍历 | ≤ 6s | `test_wow_c_all_valid_outcomes_return_200` 参数化 |
| 错误路径 | 即时 400 | `test_wow_c_invalid_outcome_returns_structured_400` |
| 3 节拍完整演示 | < 15s（含讲解） | 现场节奏 |

---

## 6. 降级台词（AI 延迟 > 10s 或 结果为 0）

> "如果 Reverse Diagnose 返回 `total_combos_found == 0`，引擎**诚实地**告诉你：当前参数空间里没有任何组合能到达这个 outcome。
> 这不是 bug，是工程事实 —— 可能意味着你定义的 outcome 需要放宽，或者硬件根本不可达。
> 引擎不会为了演示假装找到。AI 讲错了没关系，表格数据是引擎直接算的，不经过 LLM。"

---

## 7. 证据链

**Commit**：`4fc4db5 test(P20.0-A,C): e2e coverage for 3 wow scenarios + demo resilience`
**测试文件**：`tests/e2e/test_wow_c_reverse_diagnose.py`
**对应测试函数**：
- `test_wow_c_deploy_confirmed_returns_nonempty_results` — Step 1 哇点
- `test_wow_c_each_result_carries_required_parameter_keys` — 6 字段契约
- `test_wow_c_response_has_reproducibility_metadata` — grid_resolution + timestamp 审计
- `test_wow_c_all_valid_outcomes_return_200[logic1_active]` — Step 2
- `test_wow_c_all_valid_outcomes_return_200[logic3_active]`
- `test_wow_c_all_valid_outcomes_return_200[thr_lock_active]`
- `test_wow_c_all_valid_outcomes_return_200[deploy_confirmed]`
- `test_wow_c_all_valid_outcomes_return_200[tls_unlocked]`
- `test_wow_c_all_valid_outcomes_return_200[pls_unlocked]`
- `test_wow_c_invalid_outcome_returns_structured_400` — Step 3
- `test_wow_c_missing_outcome_returns_400`
- `test_wow_c_max_results_bound_is_respected`

**降级额外锚**（`archive/shelved/llm-features/tests/e2e/test_demo_resilience.py`）：
- `test_resilience_diagnosis_unknown_system_returns_400`

**Notion 战略页**：AI FANTUI LogicMVP 控制塔 → P19 Sprint → 3 哇瞬间 Deck
URL：https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec

**架构红线**：R1（真值优先）+ R2（AI 仅解释）+ R4（降级可控）

---

**Execution-by**：opus47-max
