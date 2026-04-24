# 反推仿真面板 · 需求文档

**文档编号**: FANTUI-PANEL-SIM-REQ-V1.0  
**界面路径**: `/fan_sim_panel.html`  
**状态**: Baselined · v1.0-baseline (commit 433949d · 2026-04-22)  
**数据源**: `GET /api/monitor-timeline`  
**后端实现**: `src/well_harness/demo_server.py::monitor_timeline_payload`

---

## 1. 概述

### 1.1 目的

反推仿真面板以时间轴形式展示一次完整"受控着陆 → 展开反推"场景的信号演变过程，补充演示舱（demo.html）的 stateless 快照模式，提供以下能力：

- **5-lane 示波器**：将 15 个信号系列按物理层分组显示于时间轴
- **关键时刻标注**：自动标记 TRA=-14° 到达、VDT≥90%、L4 就绪、THR_LOCK 释放等事件
- **回放动画**：requestAnimationFrame 游标扫描时间轴，实时显示 t(s)
- **摘要芯片**：快速读取各里程碑时刻（秒数）

### 1.2 使用场景

| 场景 | 说明 |
|------|------|
| 逻辑时序验证 | 确认 L4 在 VDT≥90% 之后方才激活 |
| 培训演示 | 直观展示"接地 → 拉杆 → 展开 → 油门解锁"的时间流程 |
| 故障分析辅助 | 对照正常序列，定位异常时刻 |

### 1.3 界面结构

```
unified-nav (48px fixed top)
└── main.sim-workstation
    ├── sim-header            标题 + API 端点说明
    ├── [控制] 时间线控制      刷新 / 重放 / 停止 按钮 + 状态文字
    ├── [关键时刻] 事件注释    摘要芯片 + 事件卡片列表
    └── [时间轴] 5泳道示波器  SVG 1000×470 + 图例
```

---

## 2. 功能需求

### FR-S01 · 数据获取

- 页面加载时自动调用 `GET /api/monitor-timeline`
- 成功：调用 `render()`，状态栏显示采样点数和步长
- 失败：状态栏显示 `加载失败：<error message>`
- "刷新数据"按钮（`#sim-refresh-btn`）可重新拉取

### FR-S02 · 摘要芯片

从 `payload.timeline_summary` 提取 5 个里程碑时刻，渲染为芯片（`#sim-summary`）：

| 字段 | 芯片标签 | 含义 |
|------|----------|------|
| `tra_reaches_lock_at_s` | TRA=-14° 锁 | TRA 首次到达 -14° 的时刻 |
| `vdt_reaches_90_percent_at_s` | VDT≥90% | VDT 首次达到 90% 的时刻 |
| `l4_ready_at_s` | L4 ready | L4 逻辑门首次激活的时刻 |
| `thr_lock_release_at_s` | THR_LOCK | 油门锁释放信号首次激活的时刻 |
| `time_end_s`（payload 直接字段） | 时长 | 本次仿真总时长（s） |

非空值的芯片显示高亮绿色（`data-highlight` 属性）。

### FR-S03 · 事件卡片

从 `payload.events` 数组渲染事件卡片列表（`#sim-events`）。每张卡片：

```
[t=x.xxs]  <event.label>  <event.detail>
```

事件用黄色虚线注释到 SVG 时间轴上（见 FR-S05）。

### FR-S04 · 5-lane 示波器 SVG 架构

**画布尺寸**：1000 × 470 px（`viewBox="0 0 1000 470"`）

**内边距**：`PAD_LEFT=52, PAD_RIGHT=24, PAD_TOP=12, PAD_BOTTOM=26`

**泳道布局**：

| 索引 | 泳道名 | 包含信号 |
|------|--------|---------|
| 0 | INPUT | ra (RA, ft), tra (TRA, °) |
| 1 | LOGIC | sw1, logic1(L1), sw2, logic2(L2), logic3(L3), logic4(L4) |
| 2 | POWER | tls (TLS, V), etrac (ETRAC, V) |
| 3 | SENSOR | vdt (VDT, %) |
| 4 | CMD | eec, pls, pdu, thr_lock |

**泳道尺寸**：高度 `LANE_H=76px`，间隙 `LANE_GAP=4px`，总高 `(76+4)×5=400px`

**Y 轴归一化**：每条系列各自按 `display_min`/`display_max` 归一化到 `[0,1]`，再映射到泳道高度

```javascript
scaleY(norm, laneTop) = laneTop + LANE_H - norm * (LANE_H - 8)
```

**X 轴**：时间戳整秒处绘制垂直虚线刻度，下方显示秒数

### FR-S05 · 信号渲染规格

**折线**：`<polyline>` stroke-width 1.4，fill none，opacity 0.9

**信号颜色定义**（来自后端 `_monitor_series_definition()`）：

| 信号 ID | 标签 | 颜色 | 单位 | 泳道 |
|---------|------|------|------|------|
| ra | RA | `#ff6f91` 粉红 | ft | INPUT |
| tra | TRA | `#ffaa33` 橙 | deg | INPUT |
| sw1 | SW1 | `#28f4ff` 青 | state | LOGIC |
| logic1 | L1 | `#34d4ff` 浅青 | state | LOGIC |
| sw2 | SW2 | `#28f4ff` 青 | state | LOGIC |
| logic2 | L2 | `#34d4ff` 浅青 | state | LOGIC |
| logic3 | L3 | `#34d4ff` 浅青 | state | LOGIC |
| logic4 | L4 | `#34d4ff` 浅青 | state | LOGIC |
| tls | TLS | `#7dff9a` 浅绿 | V | POWER |
| etrac | ETRAC | `#86ffbf` 绿 | V | POWER |
| vdt | VDT | `#b69dff` 紫 | % | SENSOR |
| eec | EEC | `#ffd65c` 黄 | state | CMD |
| pls | PLS | `#ffd65c` 黄 | state | CMD |
| pdu | PDU | `#ffd65c` 黄 | state | CMD |
| thr_lock | THR_LOCK | `#ff8c7a` 橙红 | state | CMD |

**事件注释线**：黄色 `#f5c518`，stroke-dasharray `3,3`，opacity 0.55，从顶到 X 轴底。

**系列标签**：绘制于折线末端（最后一个采样点左上方），8px 字体。

### FR-S06 · 回放动画

- "▶ 重放"按钮触发 `startReplay()`
- 游标为绿色竖线（`#00e5a0`），从 `PAD_LEFT` 到 `W-PAD_RIGHT` 扫描
- 动画时长 = `(tEnd - tStart)` 秒（1s 仿真时间 = 1s 实际动画时间）
- `requestAnimationFrame` 驱动，`#sim-replay-progress` 显示 `t = x.xxs`
- "■ 停止"取消动画，隐藏游标
- 图表重渲染（刷新数据）后自动重建游标引用

### FR-S07 · 图例

图例（`#sim-legend`）渲染全部 15 个信号的色块 + 标签 + 单位，鼠标悬停高亮。

---

## 3. API 契约

### 3.1 GET /api/monitor-timeline

**响应体**：

```json
{
  "step_s": 0.05,
  "time_start_s": 0.0,
  "time_end_s": 7.0,
  "series": [
    {
      "id": "ra",
      "label": "RA",
      "unit": "ft",
      "display_min": 0.0,
      "display_max": 7.0,
      "color": "#ff6f91",
      "category": "input",
      "samples": [[0.0, 5.5], [0.05, 5.45], ...]
    },
    ...
  ],
  "events": [
    { "time_s": 1.0, "label": "SW1", "detail": "TRA 越过 0°" },
    { "time_s": 2.8, "label": "L1",  "detail": "逻辑门 L1 激活" },
    ...
  ],
  "timeline_summary": {
    "tra_reaches_lock_at_s": 3.2,
    "vdt_reaches_90_percent_at_s": 5.1,
    "l4_ready_at_s": 5.1,
    "thr_lock_release_at_s": 5.1
  }
}
```

**`series[i].samples`**：`[[time_s, value], ...]` 按时间升序排列

**状态码**：

| 状态码 | 含义 |
|--------|------|
| 200 | 成功，返回时间线数据 |
| 500 | 服务端生成失败 |

---

## 4. 仿真场景规格（后端标准场景）

`monitor_timeline_payload()` 生成的"受控着陆"标准场景：

| 参数 | 值 |
|------|-----|
| 初始 RA | 5.5 ft |
| RA 下降速率 | 1.1 ft/s |
| TRA 开始拉杆时刻 | 1.0 s |
| TRA 拉杆速率 | 4.5 °/s |
| TRA 最深位置 | -32° |
| VDT 开始上升时刻 | 3.0 s |
| VDT 上升速率 | 30 %/s |
| 仿真总时长 | 7.0 s |
| 采样步长 | 0.05 s（140 个采样点） |

---

## 5. 非功能需求

| 需求 | 指标 |
|------|------|
| 初次加载渲染 | < 200ms（140 采样点 × 15 系列） |
| 回放帧率 | requestAnimationFrame（≥ 60 fps） |
| SVG 兼容性 | 纯 SVGElement API，无第三方图表库 |
| 浏览器兼容 | 现代浏览器 ES2020+，async/await |

---

## 6. 与演示舱的关系

| 维度 | 演示舱 (demo.html) | 仿真面板 (fan_sim_panel.html) |
|------|--------------------|-----------------------------|
| 评估模式 | Stateless 实时快照 | 预生成时间序列 |
| 用户交互 | 高（拖滑块、勾故障） | 低（刷新、回放） |
| 时间维度 | 单时刻截面 | 完整时间轴 |
| 故障注入 | 支持 | 不支持（标准场景） |
| 适合场景 | 逻辑条件探索 | 时序验证、培训演示 |

---

*文档与代码同步版本：v1.0-baseline · 2026-04-22*
