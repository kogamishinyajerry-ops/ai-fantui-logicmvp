# Coordination Plan

<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT START -->
## 当前自动同步快照

- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`
- 当前已验证 Plan：`P7-05 捕获 fault resolution knowledge artifact`
- 最近成功执行证据：`P7-05 Knowledge artifact baseline`
- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`
- 当前 Opus 状态：`当前无需 Opus 审查`
- 当前结论：当前最高优先级是继续收口控制塔与 freeze/demo packet 的残余漂移，不是再加 demo 功能。
- 当前唯一人工动作：继续自动开发；当前无需手动触发 Opus 4.6。

## 当前关键边界

- `controller.py` 仍然是唯一控制真值。
- 不改 `SimulationRunner` 或现有 HTTP / CLI 契约。
- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。
- Opus 4.6 的主观审查仍然只使用 Notion + GitHub 证据面。

## 当前证据入口

- [Notion 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)
- [01 当前状态（自动同步）](https://www.notion.so/33fc6894-2bed-81b4-851c-e29c7eb8847d)
- [09C 当前 Opus 4.6 审查简报](https://www.notion.so/33fc6894-2bed-819c-a863-e6404937775a)
- [10 Freeze Demo Packet](https://www.notion.so/33fc6894-2bed-8133-a8d0-c0873aba72fc)
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