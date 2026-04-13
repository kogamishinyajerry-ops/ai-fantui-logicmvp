# 模型分工规则

> 版本：v1.3（修订于 2026-04-13）
> 状态：冻结

## 核心原则

MiniMax-M2.7 是**唯一开发指令交互窗口**，但不是所有工作的执行者。
- 复杂实现任务 → 必须通过 `/codex-gpt54` 调度 Codex 参与
- 复杂架构/深度规划 → 通过 Notion @Opus 4.6
- 快速调研/信息检索 → 通过 `/gemini-ccr` 调用 Gemini 2.5 Flash
- MiniMax-M2.7 保留作为调度中枢 + 简单直接改动

**硬性规则（违反 = P0 失误）：**
> 任何涉及多文件改动、逻辑设计决策、或前端 UI 变动的任务，必须经过 Codex review 或 Codex 联合开发。
> MiniMax-M2.7 不得在未经 Codex 审查的情况下"一站式"完成复杂开发任务。

## 模型职责表

| 模型 | 职责范围 | 调用方式 |
|------|----------|----------|
| **MiniMax-M2.7**（我） | 唯一开发指令交互窗口，调度中枢，简单直接改动 | 直接执行 |
| **Codex GPT-5.4** | 代码审查 60% + 并行开发协助 40% | `/codex-gpt54` 或 `/codex:review` 等 plugin 命令 |
| **Opus 4.6** | 复杂架构/深度规划 | Notion @Opus 4.6 |
| **Gemini 2.5 Flash** | 快速调研/信息检索 | `/gemini-ccr` |

## Codex 调用时机（强制）

### 必须调用 Codex 的场景

1. **任何多文件前端改动**（>1 个 HTML/JS/CSS 文件）
2. **任何涉及 API 契约变更的改动**
3. **任何涉及 adapter boundary 的改动**
4. **任何涉及 schema/v1 contract 的改动**
5. **任何用户明确提出 UX 批评后的首次实现**
6. **任何 gsd-quick / gsd-execute-phase 的产出物**

### Codex 调用方式

```bash
# 代码审查（推荐优先）
/codex:review <文件路径或变更描述>

# 联合开发（复杂任务并行执行）
/codex:exec "<具体实现任务描述>"

# 通过 skill 调用
/codex-gpt54
```

### Codex 不可通过 Agent tool 拉起
Codex 只接受 sonnet/opus/haiku 模型。必须通过 slash command `/codex-gpt54` 或 `/codex:review` 等 plugin 命令。

## MiniMax-M2.7 可独立完成的场景

1. **单一文件微小改动**（< 20 行，不涉及逻辑设计）
2. **纯文档更新**（不涉及代码逻辑）
3. **测试验证**（已有代码的回归测试）
4. **服务启动**（无代码改动的验证）
5. **Notion 控制平面同步**（无代码审查需求）

## 违反处理

当用户指出违反分工规则时：
1. 立即识别失误
2. 回滚或补做 Codex review
3. 更新本文档
4. 在 Notion 控制平面记录教训

## 变更历史

- v1.3 (2026-04-13): 明确 Codex 调用时机，增加硬性规则，补充违反处理
- v1.2 (2026-04-13): Opus 4.6 裁决更新，Gemini 2.5 Flash 比例调整
- v1.1: 初始分工定义
