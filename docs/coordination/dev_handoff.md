# Dev Handoff

<!-- AUTO-SYNCED DEV HANDOFF SNAPSHOT START -->
## 当前自动同步交接基线

- 活动 phase：`P43 Control Logic Workbench end-to-end milestone — P43-03 DONE · P43-04 pending`
- 当前已验证 Plan：`P43-02-00 P43-02 Batch — Orchestrator + Document Pipeline + Freeze Gate`
- 最近成功执行证据：`local validation suite PASS · main@5b85f2b · 726 passed 12 xpassed (default lane) · 24/24 checks · GitHub Actions 全绿`
- 当前证据模式：`repo-doc snapshot（2026-04-22 治理收口）`
- 证据模式说明：ROADMAP.md P43 Status 行已修正（Active 前缀），解析器现正确识别 P43。CI validation 全绿。下次 CI notion-sync 成功后将由自动同步覆盖。
- 当前 QA 摘要：`PASS. 726 passed, 12 xpassed, 27 deselected (e2e opt-in) · validation suite 24/24 · main@5b85f2b · GitHub Actions all green`
- 当前运行摘要：`治理收口 pass：CI workflow 修复 + ROADMAP Active 修正 + SoT 对齐 + README 定位刷新 + GitHub Actions 三 job 全绿。`
- 当前主线：P43-02 Batch 执行中，P43-03 已完成，P43-04 pending。下一步：执行 P43-04 后提交 GATE-P43-02-BATCH-CLOSURE。
- 当前优先级：P43-04 执行 → GATE-P43-02-BATCH-CLOSURE 提交。

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
2. [01 当前状态（自动同步）](https://www.notion.so/346c6894-2bed-81cf-afd0-d060768d56d7)
3. [09C 当前 Opus 4.6 审查简报](https://www.notion.so/346c6894-2bed-81cb-9a11-fb66c1d2e723)
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