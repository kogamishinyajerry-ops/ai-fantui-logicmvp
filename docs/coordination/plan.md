# Coordination Plan

<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT START -->
## 当前自动同步快照

- 当前阶段：`P43 Control Logic Workbench end-to-end milestone`
- 当前已验证 Plan：`P43-02-00 P43-02 Batch — Orchestrator + Document Pipeline + Freeze Gate`
- 最近成功执行证据：`constitution v2.4 + RETRO-V61-055 merged via PR #15 (2026-04-25)`
- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`
- 当前 Opus 状态：`当前无需 Opus 审查`
- 当前证据模式：`repo-doc fallback mode`
- 证据模式说明：共享 Notion 数据库与活跃控制面页面当前不可达；当前快照由 repo freeze packet 与 handoff docs 恢复。
- 当前 QA 摘要：`PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
- 当前结论：当前最高优先级是把 spec-driven workbench 收成统一 engineer-facing workflow，而不是继续做 P6 控制面清理或新增 demo 表面。
- 当前唯一人工动作：继续自动开发；当前无需手动触发 Opus 4.6。

## 当前开发架构与执行规则

- GitHub / repo 是实现真值；Notion 是控制面；`controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。
- `runner.py` / `SimulationRunner` 继续承担运行时编排职责；不要把 orchestration 重新塞回 controller truth、UI 或持久化层。
- 新系统 truth 只能通过显式 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。
- FlyByWire / A320 资料只作为知识参考和设计启发，不直接复制成项目代码真值。
- 一个切片只有在代码修改、目标验证命令、`gsd_notion_sync.py run` 写回，以及 `prepare-opus-review` 复核全部完成后，才算真正完成。
- 共享数据库或独立子页不可达时，可以暂时依赖 repo-side synced snapshot 继续恢复上下文，但在 live writeback 回补前，不把控制面视为“已同步到最新”。
- 任何 Notion 写回降级、部分失败或超时都应被当成 control-plane gap / blocker 处理，不能静默跳过后继续宣称已完成同步。
- Opus 4.6 只在显式 gate / blocker / subjective review need 时介入；没有 review need 时默认动作就是继续自动开发。
- P7 workbench 继续把 intake / playback / diagnosis / knowledge / follow-up 收成 engineer-facing workflow，不引入第二套隐藏规则引擎。

## 当前关键边界

- `controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。
- `runner.py` / `SimulationRunner` 继续承担运行时编排，不把 orchestration 回塞进 controller truth / UI / persistence。
- 新系统 truth 只能通过 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。
- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。
- FlyByWire / A320 资料只作为参考知识库，不作为代码复制源。
- Opus 4.6 的主观审查仍然只使用 Notion + GitHub 证据面。

## 当前证据入口

- [Notion 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)
- [01 当前状态（自动同步）](https://www.notion.so/346c6894-2bed-81cf-afd0-d060768d56d7)
- [09C 当前 Opus 4.6 审查简报](https://www.notion.so/34dc6894-2bed-81fb-bf60-ea687dff25e7)
- [10 Freeze Demo Packet](https://www.notion.so/34ac6894-2bed-8159-aec4-e99f7b3d2f51)
- [GitHub Repo](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
- [GitHub Actions](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)

## 历史记录说明

- 下方旧轮次记录保留作为历史快照，不再代表当前真值。
<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT END -->

## 当前用途

- 这个文件现在只保留“当前自动同步快照 + 当前入口说明”。
- 当前项目真值以顶部自动同步快照、Notion 控制塔和 GitHub Actions 为准。

## 历史归档

- 旧 Round 的 plan 正文已迁到 [archive/plan-history.md](./archive/plan-history.md)。
- 如果需要复盘 Round 92 之前的阶段性判断、现场演示建议和旧约束，请去 archive 文件查看。