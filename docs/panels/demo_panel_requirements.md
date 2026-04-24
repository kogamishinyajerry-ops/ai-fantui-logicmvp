# 反推逻辑演示舱 · 需求文档

**文档编号**: FANTUI-PANEL-DEMO-REQ-V1.0  
**界面路径**: `/demo.html`  
**状态**: Baselined · v1.0-baseline (commit 433949d · 2026-04-22)  
**真值源**: `src/well_harness/demo_server.py::lever_snapshot_payload`  
**控制器**: `src/well_harness/controller.py::DeployController`

---

## 1. 概述

### 1.1 目的

反推逻辑演示舱是 FANTUI LogicMVP 的核心交互界面，提供以下能力：

- 实时评估反推控制逻辑（stateless 信号级评估，无状态机）
- 可视化 TRA → SW1/SW2 → L1/L2/L3/L4 → THR_LOCK 完整信号链路
- 支持故障注入，模拟 11 个节点 × 5 种故障类型的异常场景
- 实施 TRA=-14° 深拉区条件锁（L4 满足后解锁）

### 1.2 评估模型

本面板采用 **stateless 纯函数评估**：每次拖动拉杆或改变条件均实时向后端发送 POST 请求，后端重新计算并返回完整快照。无状态持久化，无历史回放（历史回放由仿真面板承担）。

### 1.3 界面结构

```
unified-nav (48px fixed top)
└── main.fan-workstation
    ├── fan-status-banner     系统状态 · IDLE / ACTIVE / BLOCKED / FAULT
    ├── fan-presets           场景预设快速按钮（5 个）
    └── fan-grid (two columns)
        ├── fan-col-left
        │   ├── [输入] 反推拉杆 (TRA) + TRA 锁状态行
        │   ├── [输入] 条件面板 (RA / N1K / VDT / 二元开关)
        │   └── [故障注入] 节点故障模拟
        └── fan-col-right
            ├── [HUD] 关键中间信号
            ├── [链路] 反推逻辑链路 SVG
            └── [输出] 反推命令卡片
```

---

## 2. 功能需求

### FR-01 · TRA 拉杆

| 属性 | 值 |
|------|-----|
| 类型 | `<input type="range">` |
| 范围 | -32° ～ 0° (step 0.5°) |
| 初始值 | 0° |
| 实时触发 | `input` 事件 → `buildRequest()` → `POST /api/lever-snapshot` |

**深拉区条件锁（TRA 守卫）：**

- L4 未满足时，滑块物理拦截于 -14°（JS `guardTraSlider()`）
- L4 已满足时，解除拦截，允许拖至 -32°
- 后端若返回 `effective_tra_deg ≠ requested_tra_deg`，JS 将滑块位置回拨到 `effective_tra_deg`

**TRA 区间分级（`fan-tra-zone`）：**

| 区间 | 标签 | data-zone |
|------|------|-----------|
| = 0° | FWD | fwd |
| -14° ～ -0.1° | REV | rev |
| -32° ～ -14.1° | DEEP REV | deep |

### FR-02 · TRA 锁状态行

**组件**：
- `#fan-tra-lock-badge` — 显示"深拉区关闭" / "深拉区开放"，由 `data-locked` 属性驱动 CSS 颜色（红/绿）
- `#fan-tra-lock-range` — 文字说明当前允许范围
- `#fan-tra-lock-msg` — 详细原因，来自后端 `tra_lock.message`

**驱动逻辑（`renderTraLock(data)`）：**

```
locked = data.tra_lock.locked
badge.dataset.locked = String(!locked)   // "true" 对应 data-locked="true" = 红色
```

### FR-03 · 条件面板

| 控件 | ID | 信号名 | 说明 |
|------|----|--------|------|
| 滑块 (0-100 ft) | `fan-ra` | `radio_altitude_ft` | L1 门限 < 6 ft |
| 滑块 (0-110%) | `fan-n1k` | `n1k` | L3 门限 < 84% |
| 滑块 (0-100%) | `fan-vdt` | `deploy_position_percent` | VDT90 触发 ≥ 90% |
| 复选框 | `fan-engine-running` | `engine_running` | L2 依赖 |
| 复选框 | `fan-aircraft-on-ground` | `aircraft_on_ground` | L1 依赖 |
| 复选框 | `fan-reverser-inhibited` | `reverser_inhibited` | L3 抑制，高优先级 |
| 复选框 | `fan-eec-enable` | `eec_enable` | L3 依赖 |

**VDT 反馈模式（`fan-feedback-mode`）：**
- `auto_scrubber`：后端自动将 VDT 随 PDU 命令推进
- `manual_feedback_override`：前端手动置 VDT%

### FR-04 · 场景预设

| 按钮标签 | data-preset | 效果 |
|----------|-------------|------|
| 默认前向 | `nominal-fwd` | TRA=0, RA=5, N1K=35, VDT=0, 地面, 引擎开 |
| 着陆展开全链路 | `landing-deploy` | TRA=-9, RA=2, N1K=35, VDT=80 |
| 最大反推 | `max-reverse` | TRA=-32, RA=0, N1K=60, VDT=100 |
| 收起回杆 | `stow-return` | TRA=0, RA=0, N1K=35, VDT=0 |
| 抑制位阻塞 | `inhibit-block` | TRA=-9, reverser_inhibited=true |

### FR-05 · 故障注入面板

面板标题显示当前激活故障数量（`#fan-fault-count`），"清除所有故障"按钮（`#fan-fault-clear`）重置所有复选框。

#### 可注入节点（11 个）

| 组 | 节点 ID | 显示名 | 支持故障类型 |
|----|---------|--------|------------|
| 开关 | `sw1` | SW1 | stuck_off, stuck_on |
| 开关 | `sw2` | SW2 | stuck_off, stuck_on |
| 传感器 | `radio_altitude_ft` | RA | sensor_zero → 强制 0 ft |
| 传感器 | `n1k` | N1K | sensor_zero → 强制 0% |
| 传感器 | `tls115` | TLS115 | sensor_zero → 断路 |
| 逻辑门 | `logic1` | L1 | logic_stuck_false |
| 逻辑门 | `logic2` | L2 | logic_stuck_false |
| 逻辑门 | `logic3` | L3 | logic_stuck_false |
| 逻辑门 | `logic4` | L4 | logic_stuck_false |
| 执行机构 | `vdt90` | VDT90 | cmd_blocked |
| 执行机构 | `thr_lock` | THR_LOCK | cmd_blocked |

#### 故障类型语义

| 类型 | 含义 | 效果 |
|------|------|------|
| `stuck_off` | 开关固断在断开位置 | 强制节点 inactive（无论 TRA 位置） |
| `stuck_on` | 开关固断在接通位置 | 强制节点 active |
| `sensor_zero` | 传感器输出归零 | 信号值置 0，可能导致下游门条件失效 |
| `logic_stuck_false` | 逻辑门输出固断假 | 门强制为 false，下游全部断开 |
| `cmd_blocked` | 执行机构封锁 | 命令强制无效 |

#### API 请求格式

```json
POST /api/lever-snapshot
{
  "tra_deg": -9.0,
  "radio_altitude_ft": 2.0,
  "engine_running": true,
  "aircraft_on_ground": true,
  "reverser_inhibited": false,
  "eec_enable": true,
  "n1k": 35.0,
  "feedback_mode": "auto_scrubber",
  "deploy_position_percent": 0.0,
  "fault_injections": [
    { "node_id": "sw1", "fault_type": "stuck_off" },
    { "node_id": "logic3", "fault_type": "logic_stuck_false" }
  ]
}
```

`fault_injections` 缺省为 `[]`（无故障）。

### FR-06 · HUD 关键信号

| HUD 项 | 元素 ID | 数据来源 |
|--------|---------|---------|
| SW1 (TRA 段) | `fan-hud-sw1` | `response.hud.sw1` |
| SW2 (深反推) | `fan-hud-sw2` | `response.hud.sw2` |
| TLS 解锁 | `fan-hud-tls` | `response.hud.tls_unlocked` |
| VDT90 反馈 | `fan-hud-vdt90` | `response.hud.vdt90` |
| L1/L2/L3/L4 | `fan-hud-logic` | `response.hud.logic1…4` |
| THR_LOCK 释放 | `fan-hud-thr-lock` | `response.hud.thr_lock` |

### FR-07 · 逻辑链路 SVG

**SVG viewBox**: `0 0 900 400`，四列布局：

| 列 | x 中心 | 内容 |
|----|--------|------|
| INPUTS | 90 | sw1, aircraft_on_ground, RA, sw2, engine_running, N1K, eec_enable, reverser_inhibited |
| LOGIC GATES | 340 | L1, L2, L3（AND门 D形符号） |
| INTERMEDIATE | 580 | TLS115, TLS_Unlocked, VDT90, ETRAC, EEC_deploy, PLS, PDU |
| OUTPUT | 810 | L4（AND门），THR_LOCK |

**线路状态着色**（由 JS `renderChain()` 实时更新）：

| `data-state` | 颜色 | 含义 |
|-------------|------|------|
| `active` | `#00e5a0`（绿） | 上下游节点均激活 |
| `fault` | `#e05555`（红） | 源节点激活且为故障信号 |
| `idle` | `#46597a`（灰） | 未激活 |

`data-fault="true"` 标记的线（当前为 reverser_inhibited → L3）在源节点激活时变红。

**Junction 节点**（分叉点圆点）：跟随源节点颜色同步。

### FR-08 · 输出命令卡片

| 卡片 | ID | 信号 | 说明 |
|------|----|------|------|
| TLS 115VAC | `fan-out-tls115` | `tls_115vac_cmd` | L1 触发 → TLS 解锁供电 |
| ETRAC 540VDC | `fan-out-etrac` | `etrac_540vdc_cmd` | L2 触发 → PDU 动力 |
| EEC DEPLOY | `fan-out-eec` | `eec_deploy_cmd` | L3 触发 → 展开命令 |
| THR_LOCK RELEASE | `fan-out-thr` | `throttle_electronic_lock_release_cmd` | L4 触发 → 油门反向区解锁 |

卡片 `data-state` 枚举：`idle` / `active` / `blocked` / `fault`。

---

## 3. API 契约

### 3.1 POST /api/lever-snapshot

**请求体**（JSON）：见 FR-05 示例。

**响应体**（简化）：

```json
{
  "status": "ok",
  "tra_deg": -9.0,
  "tra_lock": {
    "locked": true,
    "clamped": false,
    "lock_deg": -14.0,
    "effective_tra_deg": -9.0,
    "allowed_reverse_min_deg": -14.0,
    "visual_reverse_min_deg": -32.0,
    "boundary_unlock_ready": false,
    "unlock_logic": "logic4",
    "message": "L4 未满足：当前自由拖动范围只开放 -14.0° 到 0.0°；..."
  },
  "hud": {
    "sw1": true, "sw2": false, "tls_unlocked": false,
    "vdt90": false, "logic1": true, "logic2": false,
    "logic3": false, "logic4": false, "thr_lock": false
  },
  "nodes": [
    { "id": "sw1", "label": "SW1", "state": "active", "note": "..." },
    ...
  ],
  "outputs": {
    "tls_115vac_cmd": true,
    "etrac_540vdc_cmd": false,
    "eec_deploy_cmd": false,
    "throttle_electronic_lock_release_cmd": false
  },
  "fault_summary": {
    "active_fault_count": 0,
    "faulted_nodes": []
  }
}
```

### 3.2 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功，返回快照 |
| 400 | 请求体格式错误 |
| 500 | 服务端评估异常 |

---

## 4. 非功能需求

| 需求 | 指标 |
|------|------|
| 响应延迟 | 本地 < 50ms（stateless，无 I/O） |
| 并发 | 单连接（单用户 demo 场景） |
| 浏览器兼容 | 现代浏览器 ES2020+（SVG 2.0，no polyfill） |
| 可访问性 | ARIA label 覆盖主要交互元素 |

---

## 5. 已知约束

- `auto_scrubber` 模式下 VDT 值由后端根据 PDU 命令状态推进，前端 VDT 滑块仅在 `manual_feedback_override` 模式下有效
- 故障注入效果为 stateless 覆写，不持久化到 session；每次请求独立注入
- 本面板不支持多发（左/右）切换；逻辑对称，单发评估

---

*文档与代码同步版本：v1.0-baseline · 2026-04-22*
