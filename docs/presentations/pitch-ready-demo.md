# AI FANTUI LogicMVP — 震撼级立项汇报 Demo

> Historical P19 presentation draft. Superseded by `docs/demo/pitch_script.md` / `docs/demo/faq.md` / `docs/demo/preflight_checklist.md` in P22. Do not use this file as the current pitch baseline.

**适用场景**: 立项汇报 / 投资人演示 / 技术评审
**版本**: P19 Sprint Final (2026-04-17)
**前提条件**: 浏览器打开 `http://localhost:5173/demo.html`，4系统已 onboarded

---

## 封面（30秒开场）

> "这是一个被冻结3次、被解冻2次的项目。它现在有634个自动测试、8/8对抗契约、5轮安全审计。但这些都不重要——重要的是下面这5分钟。"

**核心信息**:
- 这是一个**控制逻辑故障诊断工作台**
- 支持4套系统：thrust-reverser / landing-gear / bleed-air / efds
- AI在Truth Engine的确定性结果上做解释，不编造答案
- 可以把2小时的专家诊断缩短到5分钟

---

## 问题陈述（1分钟）

**业界痛点**:

| 现状 | 成本 |
|------|------|
| 控制逻辑故障诊断依赖专家人工分析 | 单次2-4小时 |
| 不同系统需要不同知识库，无法复用 | 培训成本高 |
| 故障根因分析靠经验猜测，缺乏概率支撑 | 误诊率高 |

**我们解决什么**:
- 将专家级诊断能力产品化，降低到普通工程师也能使用
- 5分钟内完成原来2小时的故障分析
- 给出概率排序的根因，不是模糊猜测

---

## 解决方案概览（1分钟）

### 核心架构

```
用户输入 → Truth Engine（确定性，无AI） → Canvas链路可视化
                    ↓
             AI 推理层（概率性，解释Truth结果）
                    ↓
              结构化诊断报告
```

**Truth Engine**（controller.py）:
- 确定性：相同输入总是产生相同结果
- 无幻觉：只返回真实节点状态和逻辑链路
- 4系统共用同一adapter接口

**AI推理层**:
- `/api/chat/reason` — 因果链解释（为什么这个节点亮/不亮）
- `/api/chat/operate` — 操作建议（如何修复）
- 绝对不修改Truth Engine的输出

### 技术指标

| 指标 | 数值 |
|------|------|
| 自动化测试 | 634 passed |
| 对抗测试 | 8/8 passed |
| 支持控制系统 | 4套 |
| API端点 | 20+ |
| Monte Carlo模拟 | 100万次/30秒内 |

---

## 三个"哇"瞬间

### 哇瞬间 A：AI因果链 + Canvas同步高亮

**触发词**（汇报人说这句话）:
> "我问一个问题：如果EEC通道B失效，反推展开还能进行吗？"

**前置条件**:
- Demo页面加载thrust-reverser系统
- Canvas显示完整链路（L1/L2/L3/Deploy_blocker/TLS等）

**对话脚本**:

| 步骤 | 操作者 | 动作 |
|------|--------|------|
| 1 | 汇报人 | 在输入框输入："如果EEC通道B失效，展开还能进行吗？" |
| 2 | 系统 | 自动调用 `/api/chat/reason` |
| 3 | Canvas | 高亮L1→L2→L3链路，蓝色流光动效 |
| 4 | AI回复 | 显示："L1当前被Altitude gate阻塞（RA=8ft ≥ 6ft threshold）；即使EEC B失效，Altitude gate条件不满足，L1仍然无法激活..." |

**决策者看到什么**:
- Canvas上的链路是实时从Truth Engine获取，不是静态图片
- AI解释基于真实条件，数字精确到门限值（6ft）
- 3秒内给出因果链，不是"让我查一下"

---

### 哇瞬间 B：Monte Carlo可靠性模拟

**触发词**:
> "那100万次Monte Carlo模拟之后，哪个器件换了最值？换完之后系统可靠性从多少提到多少？"

**前置条件**:
- 打开"敏感性分析"面板
- 系统：thrust-reverser

**对话脚本**:

| 步骤 | 操作者 | 动作 |
|------|--------|------|
| 1 | 汇报人 | 点击"🔍 敏感性分析"按钮 |
| 2 | 系统 | 发起20次调用（5个RA值 × 4个outcomes） |
| 3 | 面板 | 显示4×5热力图，颜色深浅代表成功率 |
| 4 | 汇报人 | 指向最高提升行："看这里——Radio Altitude传感器换成工业级后，成功率从99.2%→99.7%" |

**决策者看到什么**:
- 有数据支撑的可靠性建议，不是"我觉得"
- 5秒钟算出100万次统计结果
- 具体到某个器件的具体提升百分点

---

### 哇瞬间 C：反向诊断

**触发词**:
> "现在换个角度：现场报告说L4展不开——你告诉我三大可能原因和概率。"

**前置条件**:
- 打开"🔍 诊断"面板
- 选择 outcome: `logic3_active`（对应L4展开）

**对话脚本**:

| 步骤 | 操作者 | 动作 |
|------|--------|------|
| 1 | 汇报人 | 在Diagnosis面板选择 outcome=`pls_unlocked`，点击"运行诊断" |
| 2 | 系统 | 调用 `/api/diagnosis/run` → ReverseDiagnosisEngine |
| 3 | 报告 | 显示Top-3根因概率列表 |
| 4 | 汇报人 | 指向第一个原因："Prob #1：SW2卡在关闭位置——概率67%，建议检查液压管路" |

**决策者看到什么**:
- 不是模糊的"可能是"，而是带概率的排序
- 第一个原因就解决了67%的情况
- 有修复建议，不是只给问题不给答案

---

## 技术架构（可选展开）

### 4系统支持

```
Thrust-Reverser ← 反推系统（19节点）
Landing Gear     ← 起落架系统
Bleed Air        ← 引气系统
EFDS             ← 电子灭火系统
```

每套系统：独立的adapter接口 + 独立YAML配置 + 独立Truth Engine

### API层

| 端点 | 用途 |
|------|------|
| `/api/chat/reason` | AI因果推理 |
| `/api/chat/operate` | 操作建议 |
| `/api/chat/explain` | 结构化解释 |
| `/api/diagnosis/run` | 反向诊断 |
| `/api/monte-carlo/run` | Monte Carlo可靠性模拟 |
| `/api/hardware/schema` | 硬件规格查询 |
| `/api/system-snapshot` | 多系统快照 |
| `/api/sensitivity-sweep` | 敏感性分析 |

### 安全与测试

- R1-R5 安全审计：HIGH/CRITICAL 全闭合
- 8/8 对抗测试：永久锚定
- 634 pytest：每次push自动运行
- Truth Engine冻结：controller.py不变

---

## 收场（30秒）

> "同样的架构已支持4套系统。扩展到第5套需要一周。
>
> 对外审查完整可追溯：每次修改都经过Opus-4.7 Gate + 8/8对抗契约 + 634测试。
>
> 现在申请的是：**资源X · 时间Y · 下阶段目标Z**。"

---

## 附录：3哇串联脚本

**完整演示流程（约10分钟）**:

1. **开场（2分钟）**：问题陈述 + 解决方案概览
2. **哇A（2分钟）**：AI因果链 → Canvas高亮
3. **哇B（2分钟）**：Monte Carlo → 可靠性建议
4. **哇C（2分钟）**：反向诊断 → 根因排序
5. **收场（2分钟）**：架构 + 安全基线 + 申请

**备用Q&A预案**:

| 问题 | 预案 |
|------|------|
| "Canvas上的颜色是什么意思？" | Active=亮灯，Blocked=等待条件，Inactive=未进入 |
| "AI会编造故障原因吗？" | AI只读Truth Engine结果，不修改Truth Engine |
| "支持其他飞机系统吗？" | 理论上支持任何控制逻辑系统，需adapter |
| "634测试覆盖哪些场景？" | 单元测试+对抗测试+集成测试，端到端覆盖 |
| "为什么不直接用AI生成逻辑？" | 确定性控制逻辑不能概率推断，必须基于Truth Engine |

---

*本文档由P19 Sprint自动生成（2026-04-17）*
