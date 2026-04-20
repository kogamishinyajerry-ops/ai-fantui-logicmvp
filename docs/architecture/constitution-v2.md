# AI FANTUI Control Logic Workbench MVP — 项目宪法（v2.1, 2026-04-20 P32 W6 刷新）

> **版本变更记录：**
> - v2 (2026-04-15): Milestone 9 Project Freeze 时治理整改重建版
> - **v2.1 (2026-04-20, P32 W6 刷新):** 追加 v5.2 Solo Mode 纪律段 + Milestone 9 Lifted 追认段 + 联邦 Level 1/2 未验证状态明示；8 条绝对边界主体不变；已验证能力表补完 P17-P30 新增条目。详见 `.planning/constitution.md` 完整叙述。

## 项目定义

**名称**：AI FANTUI Control Logic Workbench MVP
**定位**：面向航空工程师的可泛化控制逻辑分析工具，支持多系统链路可视化、故障诊断、AI 辅助文档分析和自然语言驱动的推理解释。

## 是什么 / 不是什么

| 是 | 不是 |
|----|------|
| 航空控制逻辑的分析工具 | 飞行控制系统 |
| 多系统链路可视化和推理 | 实时传感器监控系统 |
| AI 辅助文档分析（spec → 结构化 prompt） | AI 生成控制逻辑 |
| 确定性的 truth engine（adapter → 逻辑判断） | 概率性 AI 推理替代品 |

## 代码真值与控制面职责表

| 层次 | 真值 | 控制面 |
|------|------|--------|
| 控制逻辑 truth | `controller.py` + adapter interface | GitHub repo |
| 运行时状态 | `controller.py` → adapter → truth evaluation | Browser canvas |
| 控制塔状态 | Notion databases | Notion |
| 证据链 | GitHub Actions runs | GitHub |

## 绝对边界（8 条）

1. **代码真值单一来源**：`controller.py` 是 thrust-reverser truth 的唯一权威；新系统 truth 必须通过 adapter interface 接入。
2. **无 AI 替代 truth**：AI 解释 truth，但永远不能修改 truth engine 的输出。
3. **Canvas 只听 truth engine**：AI 只能在 Canvas 旁加注释，不能控制节点状态。
4. **跨域关联需人工确认**：`cross_domain_links.json` 是唯一跨域关联注册表，AI 不能自动推断关联。
5. **无外部用户时不开发**：没有真实用户反馈前，不进行新功能扩展。
6. **GSD 自动化保护回归**：所有变更必须通过 23-command validation suite。
7. **Opus 4.6 是唯一主观裁判**：架构/UX 决策通过 Opus 4.6 审查 Gate。
8. **冻结期不做新功能**：Project Freeze 期间只做治理维护和 UI 质量改进。

## 已验证能力

- ✅ 多系统（4 个）控制逻辑链路可视化
- ✅ Truth engine 驱动的确定性状态判断
- ✅ 自然语言驱动的推理解释（MiniMax API + Ollama 本地双后端 · P21 PoC 2026-04-18）
- ✅ AI 辅助文档分析（spec → ambiguity → clarification → structured prompt）
- ✅ 文档 → diagnosis 端到端 pipeline
- ✅ Playwright headless smoke 测试覆盖 UI 关键路径
- ✅ 23-command GSD validation suite 全自动回归保护（P0-P16 基线）
- ✅ Fault injection UI + 后端 overrides 桥接（P17, 2026-04-15；P18 退场后实验室保留）
- ✅ Hardware partial unfreeze — YAML schema + Monte Carlo + 反诊断（P19, 2026-04-17）
- ✅ Three-track test discipline — pytest 默认 684/1skip + opt-in e2e 49 + adversarial 8/8（P31 re-land baseline 2026-04-20）
- ✅ Pre-pitch readiness scorecard（P29 + P30, 2026-04-18）

## 不能夸大的能力

- ❌ 实时传感器监控（系统是静态逻辑分析，非实时数据流）
- ❌ 生产级别安全硬化（demo/proof-of-concept 级别）
- ❌ 跨域联合推理（架构已设计但无真实跨域数据验证）
- ❌ 替代工程师判断（工具辅助，决策权在工程师）

## 联邦架构原则

每个 adapter 是独立 truth 域。跨域关联通过 `cross_domain_links.json` 显式注册，Level 0（共存）自动生效，Level 1/2 需人工确认 + 工程依据。

### 联邦 Level 1/2 验证状态（v2.1 补充）

截至 2026-04-20，Level 0 共存已在 4 个系统（thrust-reverser / landing-gear / hydraulic / electrical）上事实验证。**Level 1 跨域 adapter 关联 + Level 2 跨域联合推理尚无实跑证据**（只有文档定义）。这是 v2.1 显式记录的未验证能力，防止 AI 叙述或 demo 话术夸大联邦架构成熟度。

---

## v5.2 Solo Mode 执行层纪律（v2.1 新增）

以下纪律自 2026-04-20 起对所有 Phase 生效，替代 v3.0 双 Opus / v4.0 Extended Autonomy 的旧表述：

### 红线（五条）

1. **不可逆 main HEAD 改动须 Kogami 显式 Gate** — FF merge / force push / 分支删除必须等 `<PHASE>-GATE: Approved`
2. **不自签 Gate** — Executor 起草 PLAN/CLOSURE 但签字只能由 Kogami 写
3. **每个 PLAN 必须有 Tier 1 adversarial self-review** — ≥3 条反驳 + 就地反驳
4. **Executor 不自选下一 Phase 方向** — 用 `AskUserQuestion` 给 ≥2 选项，不单边推进
5. **证迹先行，能力后补** — 存在证迹债时必须先用证迹 Phase 关闭（本原则由 P32 2026-04-20 首次强制执行）

### Commit Trailer / Reviewer Sign

- 所有 Claude App Opus 4.7 v5.2 commit 必须带 `Execution-by: opus47-claudeapp-solo · v5.2` trailer
- Reviewer sign 使用 `Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD`
- Phase DECISION 节点首行 `## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)`

### 与 8 条绝对边界的关系

v5.2 红线 **不替代** 8 条绝对边界，两者是正交的：
- 绝对边界管"做什么不可碰"（code / truth engine / adapter discipline）
- v5.2 红线管"怎么做 governance"（Gate / trailer / 证迹纪律）

违反任一都会触发 Phase 拒收。

---

*v1 已废止。v2 为 2026-04-15 治理整改重建版；v2.1 为 2026-04-20 P32 W6 刷新，补 Milestone 9 Lifted 叙述 + v5.2 Solo Mode 纪律。*
