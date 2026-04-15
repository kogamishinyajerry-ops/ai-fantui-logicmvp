# Dev Handoff

<!-- AUTO-SYNCED DEV HANDOFF SNAPSHOT START -->
## 当前自动同步交接基线

- 活动 phase：`未识别活动 phase`
- 当前已验证 Plan：`P15-01`
- 最近成功执行证据：`GitHub GSD automation 24322974860`
- 当前证据模式：`shared-database live mode`
- 证据模式说明：共享 Notion 数据库可达；phase / run / QA / gate 取自实时数据库记录。
- 当前 QA 摘要：`PASS. 23/23 shared validation checks pass.`
- 当前运行摘要：`23/23 shared validation checks pass.`
- 当前 demo / freeze 基线已经稳定；当前主线已切到 P7 spec-driven workbench。
- 当前优先级是让 engineer-facing onboarding / playback / diagnosis / knowledge 工具形成连续工作流，而不是继续扩 demo 表面。

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

## 恢复工作时先看

1. [AI FANTUI LogicMVP 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)
2. [01 当前状态（自动同步）](https://www.notion.so/341c6894-2bed-810d-b7e6-e5d264bcfe61)
3. [09C 当前 Opus 4.6 审查简报](https://www.notion.so/342c6894-2bed-81d6-8137-ea138302f4dd)
4. [10 Freeze Demo Packet](https://www.notion.so/341c6894-2bed-8104-9ab1-f133d6da80f4)
5. [GitHub Actions / GSD Automation Loop](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)

## 当前交接结论

- Opus 状态：`当前无需 Opus 审查`
- 当前交接重点是保持 workbench bundle / playback / diagnosis / knowledge 链路可复用，不是回到零散单命令操作。
- 下方旧 Round 记录保留为历史上下文，不再当成当前执行指令。
<!-- AUTO-SYNCED DEV HANDOFF SNAPSHOT END -->

## 当前用途

- 这个文件现在只保留“当前自动同步交接基线 + 当前入口”。
- 当前恢复工作请优先依赖顶部自动同步快照、Notion 控制塔和 GitHub Actions。

## 历史归档

- 旧 Round 的交接正文已迁到 [archive/dev-handoff-history.md](./archive/dev-handoff-history.md)。
- 需要复盘过去每轮的实现细节、限制条件或现场命令时，再进入 archive 文件查看。