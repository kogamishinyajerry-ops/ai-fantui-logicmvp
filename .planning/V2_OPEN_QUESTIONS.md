# C919 E-TRAS v2 需求矫正后的待确认疑点

> 背景：2026-04-24 基于《反推展开逻辑无歧义正式需求文档 v2.docx》对冻结版 V1.0 实现做 Gap Analysis 并矫正了 3 处偏差（C1/M1/M2，见 commit 本次改动）。以下疑点是 v2 原文未能消除的歧义或实现侧需要向需求方回确的事项。
>
> **用途**：需求评审会逐项走查；任何一项改变后必须同步代码和本文件。

---

## OPEN-Q-V2-01 · CMD3 Set 仅 APWTLA 的完整语义

**代码位置**: `src/well_harness/adapters/c919_etras_frozen_v1/cmd3_latch_controller.py::Cmd3LatchController.tick`
**相关 Fix**: M1

### 疑点
v2 §4.4 字面定义：`CMD3_Set = APWTLA`（单一条件）。

按字面实现后，空中场景下（WOW=0, engine_running=False, tr_inhibited=True）若 APWTLA 微动开关因线束短路/冰冻/误触报 1，CMD3 仍会置位。v1.0 冻结版靠 `engine_running AND selected_mlg_wow AND NOT tr_inhibited` 在 Set 门内吸收了这个风险。

### 处置（2026-04-24 Codex 审查后）

**Codex 复现结论（CRITICAL merge blocker）**：字面 M1（仅 APWTLA）在 fresh system + WOW=0 + engine=0 + APWTLA=1 下，three_phase_trcu_power_on 连续 10 个 tick 为 True，直到 1s 的 tr_stowed_and_locked dwell 完成才掉电。空中误上三相电是真实错误输出，非假设风险。

**当前策略（代码已恢复 v1.0 兜底）**：
- `Cmd3LatchController.tick` 的 Set 条件**保留** `(engine_running OR trcu_menu) AND selected_mlg_wow AND NOT tr_inhibited AND apwtla`
- 此为 v1.0 冻结版实现，属于 Codex 建议的"安全底线"
- v2 §4.4 字面偏离在代码 docstring 内明确标注，待需求方给出完整 `TR_Command3_Enable` 公式后再决定是否去掉 Set 内兜底

**回归测试（已补）**：
- `test_airborne_apwtla_fault_does_not_energize_three_phase` — 锁死 v1.0 兜底（CRITICAL 回归）
- `test_set_blocked_when_engine_off` — engine_off + apwtla=1 不置位
- `test_set_blocked_when_inhibited` — tr_inhibited + apwtla=1 不置位
- `test_set_blocked_when_airborne` — WOW=0 + apwtla=1 不置位

### 待需求方确认
1. v2 §4.4 "Set = APWTLA" 是否默认"前置门控由 `TR_Command3_Enable` 链路吸收"？
2. 若是，提供 v2 中 `TR_Command3_Enable` 的完整计算公式（见 OPEN-Q-V2-02）。
3. 若否（代码保留兜底是正确策略），本条 OPEN-Q 可关闭。

---

## OPEN-Q-V2-02 · TR_Command3_Enable 的完整计算公式

**代码位置**: `src/well_harness/adapters/c919_etras_frozen_v1/cmd3_latch_controller.py::derive_tr_command3_enable`
**相关 Fix**: M2

### 疑点
v2 §4.5 将 `TR_Command3_Enable` 声明为 "FADEC→EICU 信号"，但**未给出新的计算公式**。当前实现沿用 v1.0 冻结版的：

```
TR_Command3_Enable = NOT (TR_Stowed_And_Locked OR E_TRAS_OverTemp_Fault)
```

### 待确认
FADEC 侧是否还有其他禁止条件，例如：
1. 主电源 / APU 通道故障
2. FADEC 自检失败
3. 双 FADEC 通道表决不一致
4. TRCU 自检未完成

如果 OPEN-Q-V2-01 走"前置门控由 Enable 链路吸收"路线，那么 Enable 可能还需加入 `engine_running AND selected_mlg_wow AND NOT tr_inhibited`。

### 风险级别
**HIGH** — 这是三相电使能的主门控，任何漏条件都可能导致误触三相电。

### 回归场景建议
- 补需求方的公式后，对每个条件加独立断言测试。

---

## OPEN-Q-V2-03 · `test_inhibit_forces_sf_from_s4` 的测试原意

**代码位置**: `tests/test_c919_etras_frozen_v1_integration.py::TestSafetyPreemption::test_inhibit_forces_sf_from_s4`
**相关 Fix**: C1

### 疑点
该测试的 `locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked")` 没有 unlock PLS。Fix C1 之后，在这个锁配置下 `unlock_confirmed=False`，所以 `fadec_deploy_command` 永远不会真正发出；测试依然通过是因为 SF 由 `tr_inhibited=True` **独立**在 Step 11 抢占触发。

两种测试原意：
- **A**：只要 `tr_inhibited=True` 且系统处于 S4，就必须立刻进入 SF。当前测试符合 A，无需改动。
- **B**：模拟"Deploy 正在发生 → TR inhibit 突然触发 → SF 抢占"的完整链路。若是 B，需要补上 `pls_l="unlocked", pls_r="unlocked"` 让 Deploy 链路先真正通。

### 待确认
以测试命名 `test_inhibit_forces_sf_from_s4` 看，意图更接近 A（"从 S4 状态强制 SF"），但若后续做更严格的场景测试，应覆盖 B。

### 建议
保留当前测试作为 A 场景。新增 `test_inhibit_forces_sf_during_real_deploy`（场景 B），使用全部 5 锁 unlocked + TR_Position=30 + 随后注入 `tr_inhibited=True`。

---

## 其他已矫正但需评审留痕的事项

| 项 | v1.0 旧实现 | v2 矫正后 | 影响 |
|----|------------|----------|------|
| PLS 在 Unlock_Confirmed 中的角色 | 不参与 | 参与（与 TLS + 两吊挂锁同级） | Deploy 门控变严 |
| CMD3 Set 条件数 | 4 个（engine OR trcu_menu, WOW, not_inhibited, apwtla） | 1 个（apwtla） | 见 OPEN-Q-V2-01 |
| `derive_tr_command3_enable` 归属 | `Cmd3LatchController` 的静态方法 | 模块级函数 + Docstring 标注 FADEC 来源 | 语义清晰，待 OPEN-Q-V2-02 确认公式 |
| CMD2 ATLTLA 前置 | 已正确 | — | 无偏差 |
| Step4 ATLTLA 保持 | 已正确 | — | 无偏差 |
| Deploy 6 条件 | 已正确 | — | 无偏差（unlock_confirmed 内容变化见 C1） |

---

## 评审 checklist（需求方侧需回答）

- [ ] OPEN-Q-V2-01：CMD3 Set 是否字面仅 APWTLA？（回答 Y / N）
- [ ] OPEN-Q-V2-02：`TR_Command3_Enable` 除 stowed_and_locked 和 over_temp 外是否还有其他禁止条件？（列出清单）
- [ ] OPEN-Q-V2-03：`test_inhibit_forces_sf_from_s4` 原意 A 还是 B？（选一）
- [ ] v2 §4.3 PLS 主锁角色：除 Unlock_Confirmed 外是否还有其他系统状态需要 PLS 参与？（例如 S10 确认、SF 抢占复位）
