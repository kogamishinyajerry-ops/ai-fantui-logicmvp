# AI FANTUI LogicMVP Notion 管理中枢方案

## 目标

把 Notion 变成这个项目的长期上下文中枢，让新的 AI 会话不再依赖你手工复制一大段提示词。

这套方案遵循两个原则：

1. **完全独立于现有 `AI-Harness 控制塔 v1 / v2`**
2. **参考 AI-Harness 的开发控制塔思路，但不复用它们的数据库或关系**

也就是说，`AI FANTUI LogicMVP` 应该是一个新的、独立的 Notion 项目空间，只借鉴架构，不共享执行面。

---

## 一句话架构

把 Notion 分成四层：

1. **稳定上下文层**
   - 项目是什么
   - 什么是真实控制真值
   - 什么绝对不能改
2. **当前状态层**
   - 现在做到哪一轮
   - 当前结论是什么
   - 下一步该做什么
3. **执行记录层**
   - 任务
   - 会话
   - 决策
   - QA / 验证
4. **AI 启动层**
   - 新会话只读哪些页面
   - 本轮目标是什么
   - 继续做哪一个任务

这样你每次开新会话时，只需要一句短指令：

> 读取 `AI FANTUI LogicMVP 控制塔` 里的 `00 项目宪法`、`01 当前状态`、`进行中任务` 和 `最新会话记录`，然后继续。

---

## 隔离原则

为了不干扰你已有的 `AI-Harness 控制塔 v1 / v2`，建议严格遵守下面的边界：

- 不复用它们现有的任务数据库
- 不把 `AI FANTUI LogicMVP` 任务关联到它们的里程碑或会话记录
- 不建立跨项目 relation / rollup
- 最多只在一个总目录页里放链接入口
- 标签体系也独立，例如：
  - `Project = AI FANTUI LogicMVP`
  - 不与 `AI-Harness v1 / v2` 共用状态字段或 round 编号

如果你已经有一个顶层目录页，例如 `AI 开发中枢`，那这个新项目只需要作为**新的入口链接**挂进去，而不是接入已有项目的数据库内部。

---

## 推荐页面树

建议在 Notion 新建一个顶层页面：

`AI FANTUI LogicMVP 控制塔`

其下采用下面的结构：

### 0. Dashboard

`AI FANTUI LogicMVP 控制塔`

这个首页只做导航和当前判断，不承载大段历史内容。

首页建议固定四块：

- `当前状态`
- `当前结论`
- `继续入口`
- `关键边界`

首页只展示：

- 当前 round / phase
- 当前是否建议继续开发或冻结
- 当前回归状态
- 当前进行中的任务视图
- 最新会话记录
- 最新决策

### 1. 稳定上下文

- `00 项目宪法`
- `00A 代码真值与边界`
- `00B 代码库地图`

用途：

- 给 AI 会话提供稳定、不常变化的长期上下文
- 替代你每次复制的“当前审查请求”

### 2. 当前状态

- `01 当前状态`
- `01A 当前轮次 / Roadmap`
- `01B 当前风险与阻塞`

用途：

- 让 AI 在新会话里快速知道“现在在哪里”

### 3. 执行数据库

- `02 任务数据库`
- `03 会话记录数据库`
- `04 决策日志数据库`
- `05 QA / 验证数据库`
- `06 证据与资产数据库`
- `07 待定问题 / 风险数据库`

### 4. AI 启动面板

- `08 AI 启动卡`
- `08A 新会话模板`
- `08B 交接模板`

这部分是“避免复制提示词”的关键。

---

## 推荐数据库设计

数据库数量不要太多，但要把“稳定内容”和“执行内容”分开。

### `02 任务数据库`

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Title | Title | 任务名，动词开头 |
| Status | Select | Inbox / Ready / Doing / Blocked / Review / Done |
| Priority | Select | P0 / P1 / P2 / P3 |
| Area | Multi-select | Controller / Plant / Demo UI / CLI / Tests / Docs / Validation |
| Round | Relation | 关联当前轮次 |
| Session | Relation | 关联执行它的会话 |
| Decision | Relation | 关联相关决策 |
| QA Run | Relation | 关联验证记录 |
| Repo Paths | Text | 影响文件路径 |
| Acceptance | Text | 验收标准 |
| Next Step | Text | 当前下一步 |
| Owner | Select | AI / Me |
| Updated | Last edited time | 自动 |

建议视图：

- `Now`
- `Ready Next`
- `Blocked`
- `Recently Done`

### `03 会话记录数据库`

这个数据库是“会话记忆”，专门用于代替你复制上下文。

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Session | Title | 例如 `2026-04-08 Round 92 review` |
| Status | Select | Open / Closed / Handed Off |
| Goal | Text | 本次目标 |
| Summary | Text | 本次完成了什么 |
| Decisions | Relation | 关联决策 |
| Tasks | Relation | 关联任务 |
| QA Runs | Relation | 关联验证 |
| Artifacts | Relation | 关联证据 |
| Next Session Brief | Text | 给下一次 AI 会话的最短启动说明 |
| Started At | Date | 开始时间 |
| Updated | Last edited time | 自动 |

每一条会话记录正文建议固定模板：

1. Objective
2. Context Loaded
3. Work Done
4. Decisions Made
5. Validation
6. Risks / Open Questions
7. Next Session Brief

### `04 决策日志数据库`

这个数据库负责沉淀“为什么这么做”，避免下一次会话重新争论旧问题。

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Decision | Title | 决策标题 |
| Status | Select | Proposed / Accepted / Superseded / Rejected |
| Scope | Select | Product / Architecture / UI / Validation / Workflow |
| Date | Date | 决策时间 |
| Why | Text | 决策原因 |
| Tradeoff | Text | 取舍 |
| Affects | Text | 影响范围 |
| Related Round | Relation | 关联轮次 |
| Related Tasks | Relation | 关联任务 |
| Related Evidence | Relation | 关联证据 |

### `05 QA / 验证数据库`

这个项目非常依赖验证证据，所以 QA 建议单独成库。

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Run | Title | 例如 `Round 92 full regression` |
| Result | Select | PASS / FAIL / PARTIAL / SKIP |
| Scope | Multi-select | Unit / CLI / Demo / Manual / Schema / Regression |
| Commands | Text | 执行命令 |
| Summary | Text | 关键结果 |
| Blocking Issues | Text | 阻塞点 |
| Related Round | Relation | 关联轮次 |
| Related Tasks | Relation | 关联任务 |
| Evidence | Relation | 关联资产 |
| Date | Date | 验证时间 |

### `06 证据与资产数据库`

这个库用于统一管理“事实来源”，让 AI 能回到原始依据。

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Asset | Title | 资产名 |
| Type | Select | README / Plan / Handoff / QA Report / Test Fixture / Schema / Screenshot / Command Output |
| Source | URL or Text | Notion 页面、仓库路径或外部链接 |
| Repo Path | Text | 仓库内路径 |
| Summary | Text | 这份资产证明什么 |
| Currentness | Select | Active / Historical / Archived |
| Related Round | Relation | 关联轮次 |
| Related Decisions | Relation | 关联决策 |

### `07 待定问题 / 风险数据库`

建议字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Issue | Title | 问题名 |
| Severity | Select | High / Medium / Low |
| Type | Select | Risk / Open Question / Enhancement / Follow-up |
| Status | Select | Open / Monitoring / Resolved / Deferred |
| Why It Matters | Text | 为什么重要 |
| Next Action | Text | 下一步 |
| Related Round | Relation | 关联轮次 |
| Related Task | Relation | 关联任务 |

---

## 推荐的“稳定页面”内容

### `00 项目宪法`

这一页是每个新 AI 会话最先读取的页面，内容要尽量稳定。

建议结构：

1. 项目目标
2. 用户要解决的核心问题
3. 当前系统边界
4. 仓库结构摘要
5. 绝对不能破坏的行为
6. AI 工作方式

针对当前仓库，建议初始化为：

#### 项目目标

- 用一个轻量、可验证的 harness 来模拟 thrust reverser deploy logic
- 重点是逻辑链路、调试可解释性和 cockpit demo 演示
- 当前不是完整物理仿真，也不是通用自然语言 AI 系统

#### 当前核心资产

- `controller.py` 是 confirmed control truth
- `runner.py` 是 simulation loop
- `demo.py` / `demo_server.py` 是 demo-facing reasoning / presentation layer
- `tests/` 和 `docs/json_schema/` 是可回归验证资产

#### 绝对边界

- 不把 simplified plant 说成完整实时物理模型
- 不随意改 `controller.py` 中已确认控制真值
- 不改现有 CLI / demo / API 契约，除非明确决定
- 优先保留可验证性、可解释性和回归稳定性

### `00A 代码真值与边界`

建议把“哪些文件是真值、哪些只是呈现层”写死在这里：

- 真值层：
  - `src/well_harness/controller.py`
- 仿真层：
  - `src/well_harness/runner.py`
  - `src/well_harness/plant.py`
  - `src/well_harness/switches.py`
- 演示层：
  - `src/well_harness/demo.py`
  - `src/well_harness/demo_server.py`
  - `src/well_harness/static/*`
- 证据层：
  - `tests/*`
  - `docs/json_schema/*`
  - `docs/coordination/*`

### `00B 代码库地图`

这一页是 AI 的检索入口，内容尽量短，不要复制整份 README。

只保留：

- 模块列表
- 每个模块一句话职责
- 常用命令
- 常见验证入口

---

## 推荐的“当前状态页面”内容

### `01 当前状态`

这页应该是强时效页面，每轮更新。

建议固定区块：

1. 当前轮次
2. 当前结论
3. 当前回归状态
4. 建议下一步
5. 不建议做什么
6. 最近更新

基于当前仓库，建议初始化为：

#### 当前轮次

- `Round 92 已完成`

#### 当前结论

- 当前版本已经接近 cockpit demo candidate
- 当前不建议盲目继续加功能
- 下一步优先是现场手动 QA / 演示验证，而不是功能扩展

#### 当前回归

- `129 tests OK`

#### 当前关键边界

- 不改 `controller.py` confirmed truth
- 不改 `SimulationRunner`
- 不新增另一套控制真值
- 不把 simplified plant 表述成完整实时物理模型

#### 当前主路径

- `SW1 -> L1 -> TLS115 -> TLS unlocked -> SW2 -> L2 -> 540V -> L3 -> EEC/PLS/PDU -> VDT90 -> L4 -> THR_LOCK`

### `01A 当前轮次 / Roadmap`

这里建议用数据库而不是长文档。

字段建议：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Round | Title | 例如 `Round 92` |
| Status | Select | Planned / Active / Done / Frozen |
| Goal | Text | 本轮目标 |
| Exit Criteria | Text | 完成条件 |
| Summary | Text | 结果摘要 |
| Related Tasks | Relation | 关联任务 |
| Related QA | Relation | 关联验证 |

### `01B 当前风险与阻塞`

只保留当前有效风险，不要把历史全部堆进去。

建议初始化：

- `当 Review Gate 进入 Awaiting Opus 4.6 时，审查输入必须只使用 Notion 页面与 GitHub 仓库证据`
- `部分演示表达依赖 simplified plant feedback，需要持续防止误读`
- `如果后续继续做 UI polish，需要避免重新挤压逻辑主板主视图`

---

## “避免复制提示词”的关键设计

核心不是把大 prompt 存进 Notion，而是把**AI 每次真正需要读取的上下文拆成固定入口**。

### 入口 1：`08 AI 启动卡`

这页只保留四部分：

1. 读取顺序
2. 当前目标
3. 当前禁止事项
4. 直接继续哪个任务

建议写成下面这种格式：

#### Read Order

1. `00 项目宪法`
2. `00A 代码真值与边界`
3. `01 当前状态`
4. `02 任务数据库 -> 视图：Now`
5. `03 会话记录数据库 -> 最新一条`

#### Session Objective

- 优先延续当前 round 的主目标

#### Must Not Break

- `controller.py` confirmed truth
- `well_harness run`
- `well_harness demo`
- `POST /api/demo`
- `POST /api/lever-snapshot`

#### Next Action

- 从 `Now` 视图中取优先级最高、状态为 `Ready` 的任务

### 入口 2：`08A 新会话模板`

每次新建一条会话记录时，都用同一个模板。

模板正文建议：

```md
## Objective

## Context Loaded
- 00 项目宪法
- 00A 代码真值与边界
- 01 当前状态
- 当前进行中任务
- 最新会话记录

## Constraints

## Work Log

## Decisions

## Validation

## Handoff

## Next Session Brief
读取 00 项目宪法、01 当前状态、当前进行中任务、最新会话记录，然后继续当前任务。
```

### 入口 3：`03 会话记录 -> Next Session Brief`

这是你真正替代“复制提示词”的地方。

每次会话结束，只更新一句短说明，例如：

- `继续 P1 的 Opus 审查闭环，不做功能扩展；先看当前状态、Review Gate、最新 QA、09C 当前审查简报。`
- `继续 demo UI polish，只允许视觉微调，不允许改 controller truth 或 API 契约。`

补充规则：

- 历史 `browser hand-check` / `hand-check` 文档可以保留在仓库里作为归档材料，但不再属于当前审查入口。
- 当前正式审查入口应该始终落在 Notion 的 `09A Opus 4.6 手动审查协议` 与 `09C 当前 Opus 4.6 审查简报`。

以后你开新会话时，给 AI 的口令就可以缩成一句：

> 读取 `AI FANTUI LogicMVP 控制塔` 的启动卡，并按最新会话记录继续。

---

## AI-Harness 风格映射

你提到希望参考已有 `AI-Harness` 的开发架构。虽然这次会话无法直接读取你 Notion 里的 v1 / v2 页面，但从你当前仓库结构看，最适合沿用的是下面这套映射：

### 1. `PROJECT.md` 等价物

Notion 中对应：

- `00 项目宪法`

### 2. `ROADMAP.md` 等价物

Notion 中对应：

- `01A 当前轮次 / Roadmap`

### 3. `STATE.md` 等价物

Notion 中对应：

- `01 当前状态`

### 4. `ISSUES.md` 等价物

Notion 中对应：

- `07 待定问题 / 风险数据库`

### 5. `dev handoff` 等价物

Notion 中对应：

- `03 会话记录数据库`

### 6. `qa_report` 等价物

Notion 中对应：

- `05 QA / 验证数据库`

这样你的 Notion 就会成为一个“可检索的 GSD 控制塔”，而不是单纯任务板。

---

## 当前仓库到 Notion 的初始化映射

建议第一批先迁以下内容，不要一次把所有历史全搬进去。

### 从仓库迁入 `00 项目宪法`

来源：

- `README.md`

迁入内容：

- 项目目标
- 架构概览
- 常用命令
- 建模边界
- JSON / demo / validation 的定位

### 从仓库迁入 `01 当前状态`

来源：

- `docs/coordination/plan.md`

迁入内容：

- 当前轮次：Round 92
- 当前判断
- 当前结论
- 后续原则

### 从仓库迁入 `03 会话记录数据库`

来源：

- `docs/coordination/dev_handoff.md`

迁入方式：

- 不需要把全文拆成 90 多轮
- 只需要新建一条“当前最新交接记录”
- 摘要保留最新 round 的结果和边界

### 从仓库迁入 `05 QA / 验证数据库`

来源：

- `docs/coordination/qa_report.md`

迁入方式：

- 只先创建 1 到 3 条关键验证记录：
  - `Round 92 full regression`
  - `Round 92 command / demo consistency`
  - `Current known boundaries`

### 从仓库迁入 `06 证据与资产数据库`

建议先放这些关键资产：

- `README.md`
- `docs/coordination/plan.md`
- `docs/coordination/dev_handoff.md`
- `docs/coordination/qa_report.md`
- `docs/json_schema/well_harness_debug_v1.schema.json`
- `tests/test_demo.py`
- `tests/test_cli.py`

---

## 推荐的初始化内容

如果你现在就开始建这个 Notion 项目，建议先写入下面这些初始卡片。

### 首页摘要

- 项目：`AI FANTUI LogicMVP`
- 代码仓：`well_harness`
- 当前阶段：`Round 92 已完成`
- 当前状态：`可作为 cockpit demo candidate，优先做现场 QA，不建议盲目扩功能`
- 当前回归：`129 tests OK`

### 第一条决策

`当前项目以“逻辑可解释 + demo 可演示 + 回归可验证”为核心，不追求完整物理仿真。`

### 第一条风险

`simplified plant feedback 容易在演示中被误读为完整实时物理模型，需要持续控制文案和 UI 表达。`

### 第一条会话记录

`2026-04-08 初始化 Notion 控制塔`

建议摘要：

- 建立独立 Notion 项目，不复用 AI-Harness v1 / v2 数据库
- 固化项目宪法、当前状态、任务、会话、决策、QA、证据六类对象
- 以后新会话从启动卡进入，而不是复制长 prompt

---

## 实际搭建顺序

建议按这个顺序建，半小时内就能形成可用版本：

1. 新建顶层页 `AI FANTUI LogicMVP 控制塔`
2. 建 `00 项目宪法`
3. 建 `01 当前状态`
4. 建 `02 任务数据库`
5. 建 `03 会话记录数据库`
6. 建 `04 决策日志数据库`
7. 建 `05 QA / 验证数据库`
8. 建 `08 AI 启动卡`
9. 把首页做成 dashboard，只放 linked views

如果你想先做最小可用版，只做下面五个也够：

1. `00 项目宪法`
2. `01 当前状态`
3. `02 任务数据库`
4. `03 会话记录数据库`
5. `08 AI 启动卡`

---

## 首页 dashboard 推荐布局

建议首页从上到下只放这些内容：

### 区块 1：现在发生什么

- 当前结论
- 当前回归
- 当前轮次

### 区块 2：继续做什么

- `02 任务数据库 -> Now`
- `03 会话记录数据库 -> 最新一条`

### 区块 3：为什么这样做

- `04 决策日志数据库 -> 最近 3 条`

### 区块 4：事实依据

- `05 QA / 验证数据库 -> 最近 PASS / FAIL`
- `06 证据与资产数据库 -> 核心资产`

### 区块 5：注意边界

- confirmed truth 在 `controller.py`
- simplified plant 不是完整物理模型
- 不轻易改 CLI / demo / API 契约

---

## 日常操作方法

### 开新 AI 会话前

只做两件事：

1. 更新 `01 当前状态`
2. 在最新一条 `03 会话记录` 里写好 `Next Session Brief`

### AI 开始工作时

让 AI 读取：

- `08 AI 启动卡`
- `00 项目宪法`
- `01 当前状态`
- `Now` 任务视图
- 最新会话记录

### AI 完成工作后

至少更新三处：

1. `03 会话记录`
2. `04 决策日志`（如果有新决策）
3. `05 QA / 验证`（如果跑了验证）

这样下一次会话就能直接续上，不需要你再手工拼 prompt。

---

## 不建议的做法

- 把所有历史会话堆在一个长页面里
- 让任务数据库兼任决策日志
- 把稳定上下文和本轮动态状态写在同一页
- 复用 AI-Harness v1 / v2 的内部数据库
- 在首页写过多细节，导致 AI 每次都要读很长内容

---

## 当前会话的限制说明

本次会话里，Notion 插件没有暴露可用的数据接口，所以我**无法直接读取你 Notion 中已有的 `AI-Harness 控制塔 v1 / v2` 页面，也无法直接替你在 Notion 创建新页面**。

因此这份方案是：

- 基于你的需求进行隔离式设计
- 参考当前仓库的真实结构进行初始化
- 按照“AI-Harness / GSD 控制塔”思路映射成 Notion 结构

一旦 Notion 连接恢复，可直接按这份结构落库。

---

## 最短执行建议

如果你想最快开始，今天只做这三步：

1. 新建 `AI FANTUI LogicMVP 控制塔`
2. 建四个核心对象：`项目宪法 / 当前状态 / 任务 / 会话`
3. 新建一页 `AI 启动卡`，以后所有新会话都从它开始

这样你就已经摆脱“每次复制长 prompt”的工作方式了。
