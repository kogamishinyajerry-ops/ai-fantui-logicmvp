# 反推控制逻辑详解

**文档编号**: FANTUI-LOGIC-GUIDE-V1.0  
**状态**: Baselined · v1.0-baseline (commit 433949d · 2026-04-22)  
**权威实现**: `src/well_harness/controller.py::DeployController`  
**评估入口**: `src/well_harness/demo_server.py::lever_snapshot_payload`

---

## 1. 控制逻辑概览

### 1.1 设计原则

反推控制逻辑采用 **stateless 纯函数评估**：给定一组输入信号，唯一确定性地输出控制命令。不存在隐含状态或历史依赖（时序回放由仿真面板另行承担）。

### 1.2 信号流方向

```
TRA 拉杆位置
    │
    ▼
[SW1 / SW2]  ← TRA 角度阈值触发
    │
    ▼
[L1 门]  ← SW1 AND aircraft_on_ground AND RA<6ft
    │
    ▼
TLS 115VAC 供电 → TLS 解锁 (TLS_Unlocked_LS)
    │
    ├── [L2 门]  ← SW2 AND engine_running AND TLS_Unlocked
    │       │
    │       ▼
    │   ETRAC 540VDC 供电
    │       │
    │       ▼
    │   [L3 门]  ← ETRAC AND N1K<84% AND eec_enable AND NOT reverser_inhibited
    │       │
    │       ├──→ EEC DEPLOY CMD
    │       ├──→ PLS POWER CMD
    │       └──→ PDU MOTOR CMD
    │                │
    │                ▼
    │           VDT 位置反馈（VDT90 ≥ 90%）
    │                │
    └──── [L4 门]  ← L3 AND VDT90
              │
              ▼
         THR_LOCK RELEASE  ←── 油门杆反向区解锁
              │
              ▼
         TRA 深拉区开放（-32°~-14°）
```

### 1.3 四条命令输出总结

| 命令 | 触发条件 | 作用 |
|------|---------|------|
| `tls_115vac_cmd` | L1 = True | 115VAC 供电给 TLS，解除位移锁 |
| `etrac_540vdc_cmd` | L2 = True | 540VDC 供电给 ETRAC/PDU |
| `eec_deploy_cmd` / `pls_power_cmd` / `pdu_motor_cmd` | L3 = True | 联合驱动反推翻转斗展开 |
| `throttle_electronic_lock_release_cmd` | L4 = True | 释放油门电子锁，允许进入深反推区 |

---

## 2. 输入信号字典

| 信号名 | 类型 | 范围 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `tra_deg` | float | -32.0 ~ 0.0 ° | 0.0 | 推力反向杆角度（0°=收起，-32°=全反推） |
| `radio_altitude_ft` | float | 0 ~ ∞ ft | 5.0 | 无线电高度表读数 |
| `engine_running` | bool | — | true | 发动机运行标志 |
| `aircraft_on_ground` | bool | — | true | 飞机在地面（WOW 信号派生） |
| `reverser_inhibited` | bool | — | false | 反推抑制（最高优先级，true 时阻断 L3） |
| `eec_enable` | bool | — | true | EEC 使能 |
| `n1k` | float | 0 ~ 110 % | 35.0 | 风扇转速 N1% |
| `deploy_position_percent` | float | 0 ~ 100 % | 0.0 | 反推翻转斗展开位置反馈（仅 manual 模式有效） |
| `feedback_mode` | str | — | auto_scrubber | VDT 反馈模式（见 §3.4） |
| `fault_injections` | list[dict] | — | [] | 故障注入列表（见 §5） |

---

## 3. 四个逻辑门详解

### 3.1 L1 — 地面展开许可门

**判断：是否允许开始展开序列**

```
L1 = SW1 AND aircraft_on_ground AND (radio_altitude_ft < 6.0)
```

| 条件 | 正常值 | 门限 | 含义 |
|------|--------|------|------|
| SW1 | TRA ≤ 0°（越过 0°） | SW1_MIN_DEG(-1.4°) ～ SW1_MAX_DEG(-6.2°) | 拉杆进入反推区间 |
| aircraft_on_ground | true | — | 主轮接地信号 |
| radio_altitude_ft | < 6 ft | 6.0 ft | 无线电高度低于 6 ft |

**L1 激活效果**：触发 `tls_115vac_cmd`，向 TLS（位移锁）供 115VAC，开始解锁序列。

**L1 失效典型场景**：
- 空中意外拉杆（RA ≥ 6 ft 时 L1 = False）
- SW1 stuck_off（拉杆信号丢失）
- aircraft_on_ground = false（飞机离地）

---

### 3.2 L2 — 动力回路使能门

**判断：是否允许向 ETRAC/PDU 供电**

```
L2 = SW2 AND engine_running AND TLS_Unlocked_LS
```

| 条件 | 含义 |
|------|------|
| SW2 | TRA 进入深反推区（≤ -13°，SW2_NEAR_ZERO_DEG） |
| engine_running | 发动机运行中 |
| TLS_Unlocked_LS | L1 激活后 TLS 完成机械解锁（位移锁传感器） |

> **注意**：TLS_Unlocked_LS 是 L1 → 物理解锁 → 传感器反馈的结果，有机械延迟。仿真中简化为 L1 激活即置 True。

**L2 激活效果**：触发 `etrac_540vdc_cmd`，向 ETRAC（电气反推作动控制器）供 540VDC。

**L2 失效典型场景**：
- SW2 stuck_off（拉杆未够深）
- TLS 断路（sensor_zero 故障导致 TLS_Unlocked = false）
- engine_running = false

---

### 3.3 L3 — 展开驱动门

**判断：是否允许驱动反推翻转斗展开**

```
L3 = ETRAC_540V AND (N1K < N1K_DEPLOY_LIMIT) AND eec_enable AND NOT reverser_inhibited
```

| 条件 | 门限 | 含义 |
|------|------|------|
| ETRAC_540V | L2 输出 | ETRAC 已供电 |
| N1K < 84% | 84%（可配置） | 防止转速过高时展开 |
| eec_enable | true | EEC 使能 |
| NOT reverser_inhibited | false | 无反推抑制（最高优先级） |

**L3 激活效果**：
- `eec_deploy_cmd` = True → EEC 发出展开指令
- `pls_power_cmd` = True → 主锁供电
- `pdu_motor_cmd` = True → PDU 电机驱动翻转斗运动

**VDT 反馈**：PDU 驱动翻转斗后，位置传感器 VDT 读数开始上升。当 VDT ≥ 90% 时，`vdt90` 信号置 True，成为 L4 的前置条件。

**`reverser_inhibited` 的特殊地位**：
- 优先级最高，任何时候 `reverser_inhibited = True` 均阻断 L3
- SVG 链路图中，该信号线标记为 `data-fault="true"`（激活时线路变红）

---

### 3.4 L4 — 油门解锁门

**判断：是否允许释放油门电子锁，进入深反推区**

```
L4 = L3 AND VDT90
```

| 条件 | 含义 |
|------|------|
| L3 | 展开驱动门已激活（反推正在展开） |
| VDT90 | 展开位置已达 90%（翻转斗基本到位） |

**L4 激活效果**：
- `throttle_electronic_lock_release_cmd` = True
- TRA 深拉区（-32°~-14°）解锁，飞行员可继续向深反推方向拉杆

**L4 与 TRA 深拉区锁的关系**：

```
L4 = False  →  TRA 拉杆物理拦截在 -14°
              （JS guardTraSlider 阻止 slider 低于 -14°）
              （后端 effective_tra_deg 回拨到 -14°）

L4 = True   →  TRA 拉杆可自由拖至 -32°
              （深拉区开放）
```

---

## 4. TRA=-14° 深拉区条件锁

### 4.1 设计意图

油门反向杆深拉区（-32°~-14°）需要反推装置已基本到位（VDT≥90%）才能进入，防止飞行员在反推尚未完全展开时就请求最大反推推力，避免机械损坏。

### 4.2 锁的三层实现

**层 1：前端物理守卫（`guardTraSlider()`）**
```javascript
if (traLockActive && parseFloat(inputs.tra.value) < TRA_LOCK_DEG) {
    inputs.tra.value = String(TRA_LOCK_DEG);  // TRA_LOCK_DEG = -14
}
```
每次 `input` 事件后立即执行，用户无法拖过 -14°。

**层 2：后端 effective_tra_deg 回拨**
```python
effective_tra = requested_tra if boundary_unlock_ready or requested_tra >= lock_deg else lock_deg
```
后端以 `effective_tra_deg` 计算快照；如请求超出允许范围，评估在 -14° 进行，并在响应中明示 `clamped=true`。

**层 3：前端同步回拨**
```javascript
if (Math.abs(parseFloat(inputs.tra.value) - effectiveTra) > 0.1) {
    inputs.tra.value = String(effectiveTra);
}
```
收到响应后，如后端回拨了 TRA，前端滑块强制同步。

### 4.3 锁状态响应字段

| 字段 | 含义 |
|------|------|
| `locked` | true = 深拉区关闭 |
| `clamped` | true = 本次请求被回拨 |
| `lock_deg` | 锁定边界角度（-14°） |
| `effective_tra_deg` | 实际生效的 TRA 角度 |
| `allowed_reverse_min_deg` | 当前允许的最小 TRA（locked=true 时为 -14°，false 时为 -32°） |
| `boundary_unlock_ready` | 在 -14° 处探针：L4 是否已满足 |
| `unlock_logic` | `"logic4"`（固定） |
| `unlock_blockers` | L4 未满足时的失败条件名称列表 |
| `message` | 人类可读的状态说明 |

---

## 5. 故障注入系统

### 5.1 故障注入流程

```
POST /api/lever-snapshot
  └── fault_injections: [{node_id, fault_type}, ...]
        │
        ▼
demo_server.py::lever_snapshot_payload()
  └── 先正常计算快照
        │
        ▼
_apply_fault_injections_to_snapshot_payload()
  └── 逐一覆写对应节点状态
        │
        ▼
返回注入后的快照（含 fault_summary）
```

### 5.2 各故障类型的覆写逻辑

**stuck_off / stuck_on（开关类，sw1/sw2）**
```python
active = (fault_type == "stuck_on")
hud_payload[node_id] = active
node.state = "active" if active else "inactive"
```

**sensor_zero（传感器类，RA/N1K/TLS115）**
- `radio_altitude_ft` → 置 0，节点变 inactive（RA 始终 < 6，反而使 L1 更容易满足）
- `n1k` → 置 0，节点变 inactive（N1K < 84% 更易满足，L3 条件放宽）
- `tls115` → `tls_115vac_cmd=False`，节点变 inactive（L2 的 TLS_Unlocked 前提失效）

> **注意**：RA sensor_zero 将高度置 0，由于 L1 门限是"< 6 ft"，RA=0 反而满足条件——这是有意的，体现传感器失效后控制系统的不确定行为。

**logic_stuck_false（逻辑门类，L1~L4）**
```python
logic_entry["active"] = False
outputs[f"{node_id}_active"] = False
node.state = "blocked"
```
下游所有依赖该门的节点状态连带变为无效（级联阻断）。

**cmd_blocked（执行机构类，VDT90/THR_LOCK）**
```python
outputs[f"{node_id}"] = False
node.state = "blocked"
```

### 5.3 多故障并发规则

- 同一节点设置多个故障类型：后写入的覆盖先写入的（`fault_map` 为 dict）
- 不同节点可同时故障，效果独立叠加
- 级联效果：逻辑门故障会导致其直接驱动的下游命令节点一并置为 blocked

---

## 6. VDT 反馈模式

### 6.1 auto_scrubber（默认）

后端 `SimplifiedDeployPlant` 根据 L3 命令状态自动推进 VDT 值：
- L3 激活 → VDT 逐步上升
- L3 未激活 → VDT 保持当前值（不回落）

适合演示场景：飞行员只需拉杆，系统自动模拟展开过程。

### 6.2 manual_feedback_override

前端手动控制 VDT 滑块（`deploy_position_percent`），后端直接使用该值。

适合测试场景：精确设置 VDT 值以触发或绕过 VDT90 阈值。

---

## 7. 节点状态枚举

| state | 含义 | SVG 颜色 |
|-------|------|---------|
| `active` | 信号有效 / 命令激活 | `#00e5a0` 绿 |
| `inactive` | 信号无效 / 命令未激活 | `#46597a` 灰 |
| `blocked` | 被故障注入或上游阻断 | `#e05555` 红 |

---

## 8. 典型场景走查

### 8.1 正常着陆展开全链路

```
t=0s    飞机接地：aircraft_on_ground=true, RA=5ft
t=1s    拉杆越过 0°：TRA=-2°, SW1 激活
        → L1 = SW1(✓) AND GND(✓) AND RA<6(✓) = True
        → tls_115vac_cmd = ON → TLS 开始解锁
t=2s    TLS 解锁完成，拉杆到 -13°：TRA=-13°, SW2 激活
        → L2 = SW2(✓) AND eng(✓) AND TLS_Unlocked(✓) = True
        → etrac_540vdc_cmd = ON
t=2.5s  L3 条件满足（N1K=35%<84%, EEC_EN=true, !inhibit）
        → L3 = True
        → eec_deploy + pls_power + pdu_motor = ON
        → 翻转斗开始展开，VDT 上升
t=5s    VDT 达 90%：VDT90 = True
        → L4 = L3(✓) AND VDT90(✓) = True
        → throttle_electronic_lock_release_cmd = ON
        → TRA 深拉区开放，可继续拉至 -32°
```

### 8.2 空中意外拉杆（RA ≥ 6ft）

```
TRA=-9°, RA=15ft
→ SW1 = True（拉杆已越过 0°）
→ aircraft_on_ground = True
→ RA < 6ft = False（15 ft 不满足）
→ L1 = False → 整条链路断开
→ tls_115vac_cmd = OFF
→ L2/L3/L4 均 False
→ THR_LOCK 不释放
→ 飞行员即使拉至 -32° 也无任何反推命令
```

### 8.3 反推抑制激活

```
TRA=-20°, L3 条件其余均满足, reverser_inhibited = True
→ L3 = ETRAC(✓) AND N1K(✓) AND EEC(✓) AND NOT inhibit(✗) = False
→ L3 = False → eec/pls/pdu = OFF
→ VDT 不上升 → VDT90 = False → L4 = False
→ THR_LOCK 不释放
```

---

## 9. 代码位置索引

| 功能 | 文件 | 关键符号 |
|------|------|---------|
| 四个逻辑门评估 | `src/well_harness/controller.py` | `DeployController.evaluate()` |
| 快照生成入口 | `src/well_harness/demo_server.py` | `lever_snapshot_payload()` L2090 |
| TRA 锁载荷构建 | `src/well_harness/demo_server.py` | `_build_tra_lock_payload()` L1601 |
| 故障注入覆写 | `src/well_harness/demo_server.py` | `_apply_fault_injections_to_snapshot_payload()` L663 |
| 信号字典 | `src/well_harness/models.py` | `HarnessConfig` |
| 仿真时间线生成 | `src/well_harness/demo_server.py` | `monitor_timeline_payload()` L1769 |
| 时间线信号定义 | `src/well_harness/demo_server.py` | `_monitor_series_definition()` L1662 |
| 前端链路渲染 | `src/well_harness/static/demo.js` | `renderChain()` |
| 前端 TRA 锁渲染 | `src/well_harness/static/demo.js` | `renderTraLock()` |
| 前端故障注入构建 | `src/well_harness/static/demo.js` | `buildFaultInjections()` |

---

*文档与代码同步版本：v1.0-baseline · 2026-04-22*
