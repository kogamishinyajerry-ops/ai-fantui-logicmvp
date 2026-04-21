# C919 电反推力装置 (E-TRAS) 控制逻辑面板需求文档

**文档编号**: C919-ETRAS-PANEL-REQ-V0.9  
**状态**: Baselined — Pre-Freeze Reference  
**版本**: V0.9  
**日期**: 2026-04-20  
**维护者**: C919 E-TRAS Logic Team  

> **说明**: 本文档为正式冻结版 V1.0 之前的入库基线记录，完整、忠实地描述已实现控制逻辑面板的需求与设计。后续若需升级至冻结版 V1.0 逻辑（增加状态机、PLS、双通道 WOW 等），请以冻结版 V1.0 文档为准并发起变更单。

---

## 1. 文档定位

### 1.1 目的
本文档为 C919 E-TRAS 控制逻辑面板（Web 工作台）提供完整、可审计的需求基线，涵盖：
- 系统功能边界与输入输出信号定义
- 六个核心控制逻辑节点的完整布尔条件
- API 接口合同
- 验收标准与已知工程推断项

### 1.2 来源
- **原始参考**: `20260417-C919反推控制逻辑需求文档.pdf`（用户提供）
- **实现基线**: `c919_etras/models.py` + `c919_etras/controller.py`
- **工作台规格**: `c919_etras/system_spec.py`

### 1.3 范围
**覆盖**: 控制逻辑评估、六个逻辑节点、API 接口、Web 工作台功能  
**不覆盖**: 总线协议、具体针脚定义、完整 BIT/故障树、维护菜单全部细节  

### 1.4 版本差异说明（V0.9 → V1.0 冻结版）

| 项目 | V0.9（本文档） | V1.0 冻结版 |
|------|--------------|------------|
| WOW 通道 | 单路 `MLG_WOW`（已解析输入） | 双路 LGCU1/2 有效性+一致性投票 |
| PLS 处理 | 不纳入收起确认 | 纳入两把 PLS（Primary Lock System） |
| CMD3 Reset | 外部 `TR_Command3_Enable` 信号 | 内部派生（`NOT(Stowed&Locked OR OverTemp)`） |
| Stow CMD1 | 工程推断（未有原始图纸依据） | 冻结正式版 |
| 状态机 | 无（纯函数评估器） | 12 态（S0~S10 + SF） |
| 执行模型 | 无状态纯函数 | 有状态 tick() 循环 |

---

## 2. 系统对象与边界

### 2.1 单发侧核心对象

| 对象 | 数量 | 说明 |
|------|------|------|
| 机械作动筒 | 4 | PMDU 驱动 |
| PMDU | 1 | 电机驱动单元 |
| TLS | 1 | 位移锁（平移锁止系统）|
| 吊挂锁（Pylon Lock） | 2 | 左/右各一把 |
| TRCU | 1 | 反推控制单元 |
| EICU | 1 | 电接口控制单元（本控制器所在节点）|

> **注**: V0.9 不涉及 PLS（Primary Lock System）。V1.0 冻结版新增 PLS_L/PLS_R 作为独立对象。

### 2.2 电源对象

| 电源 | 对应命令 | 说明 |
|------|---------|------|
| 115VAC 单相解锁供电 | CMD2 → `SinglePhaseUnlockPower_On` | 驱动 TLS + 两把吊挂锁 |
| 115VAC 三相作动供电 | CMD3 → `ThreePhaseTRCUPower_On` | 驱动 TRCU |

### 2.3 安全边界
- **仅地面允许展开**（TR_WOW == 1 或 MLG_WOW == 1 作为地面判断）
- **任何禁止/保护条件优先级高于展开命令**
- **TR_Inhibited 为最高优先级抑制信号**

---

## 3. 信号字典

### 3.1 原始输入信号

| 信号名 | 类型 | 单位 | 冻结定义 |
|--------|------|------|---------|
| `mlg_wow` | bool | — | 主轮载荷（已解析单路，含 LGCU 冗余投票结果）|
| `tr_wow` | bool | — | FADEC 侧 TR_WOW（含 2.25s/120ms 确认延时，由外部 plant 维护）|
| `tra_deg` | float | ° | 油门杆/反推力杆解析角度（正推~0°，最大反推~-32°）|
| `atltla` | bool | — | 微动开关 1 信号（TRA 经过 SW1 窗口 [-1.4°, -6.2°] 时 = 1）|
| `apwtla` | bool | — | 微动开关 2 信号（TRA 经过 SW2 窗口 [-5.0°, -9.8°] 时 = 1）|
| `engine_running` | bool | — | 发动机达到慢车及以上 |
| `trcu_menu_mode` | bool | — | TRCU 维护菜单模式（允许 CMD3 备用路径）|
| `tr_inhibited` | bool | — | 反推电气抑制（0=允许，1=抑制）|
| `fadec_maintenance_mode` | bool | — | FADEC 维护模式 |
| `tr_maintenance_cmd` | bool | — | 飞机发出反推维护指令 |
| `comm2_timer_s` | float | s | CMD2 内部计时器（由外部 harness 维护）|
| `cmd3_latched` | bool | — | CMD3 SR 锁存器当前输出（由外部 harness 维护）|
| `tr_position_pct` | float | % | 反推位置（0%=完全收起，100%=完全展开）|
| `tr_deployed_confirmed` | bool | — | TR_Position ≥ 80% 持续 0.5s 后置 True |
| `n1k_pct` | float | % | 发动机转速 N1k |
| `max_n1k_deploy_limit_pct` | float | % | 允许展开的 N1k 上限（随 P0 变化）|
| `max_n1k_stow_limit_pct` | float | % | 允许收起的 N1k 上限 |
| `etras_over_temp_fault` | bool | — | E-TRAS 过温故障位 |
| `tr_command3_enable` | bool | — | FADEC 发往 EICU 的 CMD3 使能（FALSE = 复位 SR 锁存）|
| `tls_any_unlocked_valid` | bool | — | TLS 至少 1 传感器有效且解锁 |
| `right_pylon_any_unlocked_valid` | bool | — | 右吊挂锁至少 1 传感器有效且解锁 |
| `left_pylon_any_unlocked_valid` | bool | — | 左吊挂锁至少 1 传感器有效且解锁 |
| `all_locks_unlocked_direct` | bool | — | 全传感器 VALID 路径：TLS + 两吊挂锁全部有效且解锁 |

### 3.2 派生信号

| 信号名 | 计算方 | 说明 |
|--------|--------|------|
| `cmd3_output` | 控制器内 SR 锁存 | CMD3 三相电输出真实状态 |
| `locks_unlocked_or_confirmed` | 控制器内组合 | Deploy CMD1 条件③的锁解锁确认 |
| `maintenance_cycle` | 控制器内组合 | `fadec_maintenance_mode AND tr_maintenance_cmd` |

### 3.3 输出信号

| 信号名 | 冻结命名 | 说明 |
|--------|---------|------|
| `cmd2_active` | `SinglePhaseUnlockPower_On` | TLS + 两吊挂锁 115VAC 单相解锁供电 |
| `cmd3_output` | `ThreePhaseTRCUPower_On` | TRCU 115VAC 三相作动供电 |
| `deploy_cmd1_active` | `FADEC_Deploy_Command` | FADEC 展开命令（→ PMDU） |
| `stow_cmd1_active` | `FADEC_Stow_Command` | FADEC 收起命令（→ PMDU）[工程推断] |
| `thr_idle_lock_release` | — | 油门慢车电子锁释放（TR 展开 ≥ 80%） |
| `tls_pylon_115vac_on` | — | 等价于 `cmd2_active` |
| `trcu_3phase_on` | — | 等价于 `cmd3_output` |
| `pmdu_deploy_cmd` | — | 等价于 `deploy_cmd1_active` |
| `pmdu_stow_cmd` | — | 等价于 `stow_cmd1_active` |

---

## 4. 控制器参数配置

### 4.1 微动开关区间（TRA）

| 开关 | 信号 | 近零边界 | 深反推边界 | 说明 |
|------|------|---------|-----------|------|
| SW1 | `ATLTLA` | -1.4° | -6.2° | 单相解锁请求 |
| SW2 | `APWTLA` | -5.0° | -9.8° | 三相作动请求 |

### 4.2 关键阈值

| 参数 | 值 | 来源 |
|------|-----|------|
| `tra_idle_reverse_deg` | -11.74° | 文档图5 Deploy 条件⑥ |
| `comm2_timer_limit_s` | 30 s | 文档 1.1.1 节 |
| `tr_deployed_threshold_pct` | 80% | 文档 Step 4 |
| `tr_wow_set_delay_s` | 2.25 s | 文档 1.1.3 节条件④ |
| `tr_wow_reset_delay_s` | 120 ms | 文档 1.1.3 节条件④ |
| `cmd2_deployed_confirm_s` | 0.5 s | TR ≥ 80% 持续确认（CMD2 断电触发） |
| `stow_lock_confirm_s` | 1.0 s | 收起上锁确认延时 |
| `default_n1k_deploy_limit_pct` | 84% | 文档 79%~89% 取中值 |
| `default_n1k_stow_limit_pct` | 72% | **工程推断**（比 Deploy Limit 低约 12%）|

---

## 5. 核心逻辑节点定义

### 5.1 CMD2：单相解锁供电（图 2）

**输出**: `SinglePhaseUnlockPower_On = cmd2_active`  
**逻辑**: 全部 AND

| 条件编号 | 信号 | 判断 | 阈值 |
|---------|------|------|------|
| ① | `mlg_wow` | == | TRUE |
| ② | `tr_inhibited` | == | FALSE |
| ③ | `comm2_timer_s` | < | 30s |
| ④ | `tr_deployed_confirmed` | == | FALSE |

> **注**: 条件①使用的 `mlg_wow` 为已解算的单路信号（非冻结版的 `Selected_MLG_WOW`）。

---

### 5.2 CMD3 Set：SR 锁存器置位端（图 3）

**逻辑**: 全部 AND

| 条件编号 | 信号 | 判断 | 阈值 |
|---------|------|------|------|
| ① | `engine_running OR trcu_menu_mode` | == | TRUE |
| ② | `mlg_wow` | == | TRUE |
| ③ | `tr_inhibited` | == | FALSE |
| ④ | `apwtla` | == | TRUE |

---

### 5.3 CMD3 Reset：SR 锁存器复位端（图 4）

**逻辑**: 单条件

| 条件编号 | 信号 | 判断 | 阈值 |
|---------|------|------|------|
| ① | `tr_command3_enable` | == | FALSE |

> **注**: 两条断电路径（路径A：TR 收起上锁 + TRA > -1.4°；路径B：过温）由外部 plant 综合后以 `tr_command3_enable` 信号形式输入控制器。控制器不重复实现内部综合逻辑。

---

### 5.4 CMD3 输出：三相作动供电

**SR 锁存器行为**（Reset 优先）:

```
IF cmd3_reset_cond == TRUE:   cmd3_output = FALSE   （Reset 优先）
ELIF cmd3_set_cond == TRUE:   cmd3_output = TRUE    （Set 置位）
ELSE:                          cmd3_output = cmd3_latched  （Hold 保持）

ThreePhaseTRCUPower_On = cmd3_output
```

> **冻结约定（V0.9 兼容）**: 回杆（APWTLA=0）后不得立即切断三相电。保持行为由 `tr_command3_enable == TRUE` 维持，直到外部 plant 触发 Reset。

---

### 5.5 Deploy CMD1：展开命令（图 5）

**输出**: `FADEC_Deploy_Command = deploy_cmd1_active`  
**逻辑**: 全部 AND

| 条件编号 | 信号/表达式 | 判断 | 阈值 | 来源 |
|---------|------------|------|------|------|
| ① | `engine_running OR maintenance_cycle` | == | TRUE | 发动机激活或维护周期 |
| ② | `tr_inhibited` | == | FALSE | 无抑制 |
| ③ | `locks_unlocked_or_confirmed` | == | TRUE | TLS + 两吊挂锁解锁（见 5.5a）|
| ④ | `tr_wow` | == | TRUE | 带 2.25s 确认的地面信号 |
| ⑤ | `n1k_pct` | ≤ | `max_n1k_deploy_limit_pct` | N1k 在限值内 |
| ⑥ | `tra_deg` | < | -11.74° | 反推杆过反推慢车位 |

**5.5a 锁解锁确认（条件③内部）**:

```python
locks_unlocked_or_confirmed = (
    all_locks_unlocked_direct      # 路径 A：全传感器 VALID（TLS + 两吊挂锁）
    OR (
        atltla                     # 路径 B（持续 400ms，外部 plant 确认后反映在各信号中）
        AND tls_any_unlocked_valid
        AND right_pylon_any_unlocked_valid
        AND left_pylon_any_unlocked_valid
    )
)
```

---

### 5.6 Stow CMD1：收起命令 ⚠️ 工程推断

**输出**: `FADEC_Stow_Command = stow_cmd1_active`  
**状态**: **工程推断补全**（原始文档未提供完整 Stow 逻辑图）  
**推断依据**: 文档 Step 7 唯一明确条件 + 安全原则推断  

| 条件编号 | 信号 | 判断 | 阈值 | 推断依据 |
|---------|------|------|------|---------|
| ① | `engine_running OR maintenance_cycle` | == | TRUE | FADEC 必须激活 |
| ② | `tr_wow` | == | TRUE | 必须在地面 |
| ③ | `n1k_pct` | ≤ | `max_n1k_stow_limit_pct` | 文档明确给出 |
| ④ | `tra_deg` | ≥ | -11.74° | 反推杆已离开慢车位 |
| ⑤ | `tr_position_pct` | > | 0% | TR 处于展开状态 |

> **变更请求**: 待原始图纸/接口文件确认后，以文档为准修订此逻辑节点，并移除"工程推断"标注。

---

### 5.7 油门慢车锁释放（Step 4）

**输出**: `thr_idle_lock_release`  
**逻辑**:

| 条件 | 信号 | 判断 | 阈值 |
|------|------|------|------|
| ① | `tr_deployed_confirmed` | == | TRUE |

> TR_Position ≥ 80% 持续 0.5s 后 FADEC 解锁反推慢车电子锁。

---

## 6. 执行模型

### 6.1 设计原则
控制器为**无状态纯函数**（`C919EtrasController`），无副作用。所有时序状态由外部 harness 维护后作为普通字段传入。

### 6.2 逻辑评估顺序（单步内）

```
1. 计算 normal_or_maintenance（中间量）
2. 计算 maintenance_cycle（中间量）
3. 评估 CMD2 节点
4. 评估 CMD3 Set 端
5. 评估 CMD3 Reset 端
6. 评估 CMD3 SR 锁存输出
7. 计算 locks_unlocked_or_confirmed（中间量）
8. 评估 Deploy CMD1
9. 评估 Stow CMD1
10. 评估 油门慢车锁释放
11. 生成 C919ControllerOutputs
```

### 6.3 时序状态（由外部 harness 维护）

| 状态量 | 重置条件 | 累积条件 |
|--------|---------|---------|
| `comm2_timer_s` | ATLTLA 0→1 上升沿 | ATLTLA == 1 时按 dt 累加 |
| `cmd3_latched` | `tr_command3_enable == FALSE` | Set 条件满足时置 True |
| `tr_deployed_confirmed` | TR_Position < 80% 持续 | TR_Position ≥ 80% 持续 0.5s 后置 True |
| `tr_wow` | 外部 WOW == 0 持续 120ms | 外部 WOW == 1 持续 2.25s 后置 True |

---

## 7. API 接口合同

### 7.1 端点列表

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | Web 工作台 HTML 入口 |
| GET | `/api/spec` | 系统规格 JSON（组件、逻辑节点、验收场景）|
| GET | `/api/config` | 控制器配置参数 JSON |
| POST | `/api/evaluate` | 输入快照 → 逻辑节点评估结果 |

### 7.2 POST /api/evaluate

**请求 Content-Type**: `application/json`

**请求体**（快照字段，全部可选，缺省为安全侧默认值）:

```json
{
  "mlg_wow": false,
  "tr_wow": false,
  "tra_deg": 0.0,
  "atltla": false,
  "apwtla": false,
  "engine_running": false,
  "trcu_menu_mode": false,
  "tr_inhibited": false,
  "fadec_maintenance_mode": false,
  "tr_maintenance_cmd": false,
  "comm2_timer_s": 0.0,
  "cmd3_latched": false,
  "tls_any_unlocked_valid": false,
  "right_pylon_any_unlocked_valid": false,
  "left_pylon_any_unlocked_valid": false,
  "all_locks_unlocked_direct": false,
  "tr_position_pct": 0.0,
  "tr_deployed_confirmed": false,
  "n1k_pct": 0.0,
  "max_n1k_deploy_limit_pct": 84.0,
  "max_n1k_stow_limit_pct": 72.0,
  "etras_over_temp_fault": false,
  "tr_command3_enable": true
}
```

**响应体**:

```json
{
  "nodes": [
    {
      "id": "cmd2",
      "active": false,
      "conditions": [
        {
          "name": "mlg_wow",
          "current_value": false,
          "comparison": "==",
          "threshold_value": true,
          "passed": false
        }
      ],
      "failed_count": 1
    }
  ],
  "outputs": {
    "cmd2_active": false,
    "cmd3_set_cond": false,
    "cmd3_reset_cond": false,
    "cmd3_output": false,
    "deploy_cmd1_active": false,
    "stow_cmd1_active": false,
    "thr_idle_lock_release": false,
    "tls_pylon_115vac_on": false,
    "trcu_3phase_on": false,
    "pmdu_deploy_cmd": false,
    "pmdu_stow_cmd": false
  }
}
```

---

## 8. Web 工作台功能需求

### 8.1 核心功能

| 功能 | 说明 |
|------|------|
| 实时双向绑定 | 修改任意输入立即重新评估，所有输出随之更新 |
| 快捷预设 | 5 大场景（空闲/展开中/已展开/收起中/中止）+ 10 步时序快捷卡 |
| 逻辑节点详情 | 每节点显示：激活状态、所有条件当前值、未通过条件高亮 |
| 工程推断标注 | Stow CMD1 节点显示"工程推断"标记 |
| 评估计数 | 显示当前会话已评估次数 |

### 8.2 界面布局（三列）

| 列 | 内容 |
|----|------|
| 左列（300px）| 输入信号面板：地面/WOW、油门杆、发动机、锁传感器、位置/N1k、故障位 |
| 中列（自适应）| 六节点逻辑评估网格（2×3），每格显示激活/阻断状态与条件详情 |
| 右列（260px）| 电气输出指示（CMD2/3、Deploy/Stow、三路派生电气）|

### 8.3 底部序列时间线

10 个步骤卡对应反推展开→收起完整序列，点击快速加载预设状态。

---

## 9. 验收标准

### 9.1 逻辑正确性
| 场景 | 期望结果 |
|------|---------|
| 默认空闲（所有输入为安全侧默认值）| 所有命令 FALSE |
| MLG_WOW=1, ATLTLA=1, TR_Inhibited=0, CMD2_Timer=0, TR_Deployed=False | CMD2=TRUE |
| CMD2=TRUE 时 TR_Position≥80% | CMD2=FALSE（30s 计时器未触发但 TR_Deployed 条件触发）|
| CMD3 Set 条件全满 + tr_command3_enable=FALSE | CMD3 Output = FALSE（Reset 优先）|
| Deploy 所有 6 个条件满足 | FADEC_Deploy_Command=TRUE |
| TR_Inhibited=1（任何状态）| CMD2=FALSE，Deploy=FALSE |
| TR_Deployed_Confirmed=TRUE | thr_idle_lock_release=TRUE |

### 9.2 API 合规性
- POST /api/evaluate 响应时间 < 50ms
- 错误输入返回 HTTP 400 及错误描述
- 所有输出字段在响应中完整存在

### 9.3 UI 功能
- 快捷预设加载后界面立即刷新
- 条件评估结果颜色编码（绿色=通过，红色=失败，黄色=推断）

---

## 10. 工程推断项清单

| 编号 | 内容 | 推断依据 | 变更请求优先级 |
|------|------|---------|--------------|
| INF-01 | Stow CMD1 完整布尔条件（§5.6）| 文档 Step7 描述 + 安全工程原则 | P1 |
| INF-02 | `max_n1k_stow_limit_pct = 72%` | 比 Deploy Limit 低约 12% | P1 |
| INF-03 | `tr_command3_enable` 由外部 plant 综合（路径 A + 路径 B）| CMD3 Reset 端原始图未给两路完整 OR 逻辑 | P2 |
| INF-04 | `cmd2_deployed_confirm_s = 0.5s` | 文档 Step4 描述 TR≥80% 断电，0.5s 为工程估算 | P2 |
| INF-05 | `lock_unlock_confirm_s = 400ms`（路径 B 的时间窗）| 工程估算 | P2 |

---

## 11. 接入说明

### 11.1 独立模式

```bash
cd /Users/Zhuanz/20260420-C919-ETRAS-LogicSpec
python3 panel_server.py
# → http://localhost:9000
```

### 11.2 集成模式

```python
from c919_etras import C919EtrasAdapter, build_c919_adapter

adapter = build_c919_adapter()
adapter.load_spec()
result = adapter.evaluate_snapshot(your_snapshot)
```

---

## 附录 A：已知差异/待确认项（与 V1.0 冻结版对比）

见本文档第 1.4 节"版本差异说明"。完整差异分析见冻结版 V1.0 文档第 2 节"冻结裁决与统一解释"。
