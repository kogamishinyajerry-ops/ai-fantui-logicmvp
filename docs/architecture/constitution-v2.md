# AI FANTUI Control Logic Workbench MVP — 项目宪法（v2, 2026-04-15 重建）

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
- ✅ 自然语言驱动的推理解释（MiniMax API）
- ✅ AI 辅助文档分析（spec → ambiguity → clarification → structured prompt）
- ✅ 文档 → diagnosis 端到端 pipeline
- ✅ Playwright headless smoke 测试覆盖 UI 关键路径
- ✅ 23-command GSD validation suite 全自动回归保护

## 不能夸大的能力

- ❌ 实时传感器监控（系统是静态逻辑分析，非实时数据流）
- ❌ 生产级别安全硬化（demo/proof-of-concept 级别）
- ❌ 跨域联合推理（架构已设计但无真实跨域数据验证）
- ❌ 替代工程师判断（工具辅助，决策权在工程师）

## 联邦架构原则

每个 adapter 是独立 truth 域。跨域关联通过 `cross_domain_links.json` 显式注册，Level 0（共存）自动生效，Level 1/2 需人工确认 + 工程依据。

---

*v1 已废止。本版为 2026-04-15 治理整改重建版本。*
