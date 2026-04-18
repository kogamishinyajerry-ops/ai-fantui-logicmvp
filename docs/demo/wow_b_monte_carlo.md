# Wow B — Monte Carlo 可靠性（10k trials < 5s + 同种子字节一致）

**演示主题**：工程语义的可靠性分析，不是演示特效。同一种子跑两次 byte-identical；10000 次试验在演示窗口内跑完；四种失效模式按硬件语义分布。

---

## 1. 开场台词（< 30s）

> "单次真值引擎告诉你「现在是什么」。
> Monte Carlo 告诉你「一万次操作里，哪个部件最先坏，平均多少次循环才故障」。
> 一次演示能跑完，同一个种子永远重现 —— 这是合规证据，不是演示特效。"

---

## 2. Keystroke 序列（3 步）

### Step 1 — 基础 1000 trials（契约形状 + 数值区间）
- **URL**：`POST /api/monte-carlo/run` on `http://127.0.0.1:8799`
- **点击目标**：`#chat-drawer` 右侧抽屉 → `#chat-analysis-btn` 打开分析面板 → Monte Carlo 子面板 → `n_trials` 输入框 + `seed` 输入框 → Run 按钮
- **输入内容**：`{"system_id": "thrust-reverser", "n_trials": 1000, "seed": 42}`

### Step 2 — 10000 trials（时延哇点）
- **URL**：同上
- **点击目标**：同面板 `n_trials` 输入框（覆盖原值）→ Run
- **输入内容**：`n_trials=10000`，`seed` 保持 42

### Step 3 — 确定性重放（审计哇点）
- **URL**：同上
- **点击目标**：同面板 Run 按钮（参数不动，直接再点一次）
- **输入内容**：完全相同 `{system_id: "thrust-reverser", n_trials: 10000, seed: 42}`

---

## 3. 预期 AI 输出（文字描述）

- **Step 1 AI 叙述**：1000 次试验完成；success_rate 在 [0,1] 区间；四种失效原因命中 —— RA 传感器失效、SW1 miss、SW2 miss、TRA 卡死；每种数值非负
- **Step 2 AI 叙述**：1 万次试验两百毫秒内跑完；`n_trials` 回显 10000；MTBF 数值更新；不是采样缩水
- **Step 3 AI 叙述**：同 seed 两次跑完 body 完全一致；工程审计可追溯；合规审查通过

---

## 4. UI 预期（面板渲染 / 图表刷新）

- **Step 1**：Analysis Tools 面板显示 `success_rate` 百分比 + `mtbf_cycles` 数值 + 4 条 failure_mode 条形图
- **Step 2**：同面板数字刷新；spinner 不出现超过 1 秒；failure_modes 条形图根据新样本微调
- **Step 3**：数字完全不变（byte-identical）；审计标记显示"确定性重放 ✓"

---

## 5. Timing Budget

| 动作 | 预算 | 锚点 |
|---|---|---|
| 1000 trials 单次 | < 1s（观察性） | 子秒级完成 |
| 10000 trials 单次 | < 5s wall clock | `test_wow_b_10k_trials_under_5s`（实测 ≈ 198ms） |
| 3 节拍完整演示 | < 15s（含讲解） | 现场节奏 |

---

## 6. 降级台词（AI 延迟 > 10s 或 参数输错）

> "如果用户不小心把 n_trials 敲成一百万，Monte Carlo 不会崩。引擎会 clamp 到 10000 上限，或返回结构化 400。
> 演示期间不会白屏，不会 500。类型错了，错误文案会告诉你是什么字段出了问题。
> AI 讲解卡壳？failure_modes 条形图已经画出来了 —— 你看 sw2_missed 是主要失效原因，MTBF 数值是硬计算出来的。"

---

## 7. 证据链

**Commit**：`4fc4db5 test(P20.0-A,C): e2e coverage for 3 wow scenarios + demo resilience`
**测试文件**：`tests/e2e/test_wow_b_monte_carlo.py`
**对应测试函数**：
- `test_wow_b_monte_carlo_returns_contract_shape` — 锁 9 个顶层 key
- `test_wow_b_10k_trials_under_5s` — Step 2 时延硬预算
- `test_wow_b_success_rate_in_unit_interval` — 数值区间
- `test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys` — 4 种失效模式命名
- `test_wow_b_is_deterministic_under_fixed_seed` — Step 3 确定性重放
- `test_wow_b_n_trials_zero_is_clamped_to_min` — 降级路径
- `test_wow_b_n_trials_overflow_is_clamped_to_max` — 降级路径

**降级路径额外锚**（`tests/e2e/test_frontend_degradation.py`）：
- `test_frontend_monte_carlo_bad_n_trials_returns_renderable_response[0/-1/1500000]`
- `test_frontend_monte_carlo_bad_type_returns_structured_400_not_html`

**Notion 战略页**：AI FANTUI LogicMVP 控制塔 → P19 Sprint → 3 哇瞬间 Deck
URL：https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec

**架构红线**：R1（真值优先）+ R4（降级可控）

---

**Execution-by**：opus47-max
