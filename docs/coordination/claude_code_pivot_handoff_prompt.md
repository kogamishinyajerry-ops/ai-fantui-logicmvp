# 给 Claude Code 的执行指令包

你现在接手的不是一个需要从零重构的项目，而是一个已经具备真实工程能力、但治理面和表达面严重漂移的仓库。

你的任务不是立刻改代码，而是先基于当前 repo / GitHub / Notion 的真实状态，输出一份“治理收口优先”的分阶段执行方案。只有在方案被批准后，你才能进入实施。

## 你必须先读的文件

请先阅读以下文件，再输出你的第一响应：

- `docs/coordination/claude_code_pivot_analysis_report.md`
- `README.md`
- `.github/workflows/gsd-automation.yml`
- `pyproject.toml`
- `.planning/STATE.md`
- `.planning/notion_control_plane.json`
- `tools/gsd_notion_sync.py`
- `docs/coordination/plan.md`
- `docs/coordination/dev_handoff.md`

## 你的首要判断基线

你必须坚持以下 source-of-truth 顺序：

1. `repo` 是代码真相
2. `GitHub` 是对外工程面
3. `Notion` 是控制中枢

当三者冲突时，先修 sync / workflow / 表达层，不要反向修改 repo 真相去迎合错误的 Notion 或 GitHub 页面。

## 你已经知道的关键事实

请不要从零开始重新判断，也不要忽略以下已确认事实：

- 当前本地 `HEAD` 是 `main@433949d`
- 本地 `python3 tools/run_gsd_validation_suite.py --format json` 为全绿
- GitHub 最新 `GSD Automation Loop` 中 `regression` 通过、`validation` 失败、`notion-sync` 跳过
- 这个 `validation` 红灯的核心原因是 workflow 只安装了 `jsonschema pytest`，没有覆盖 `pyproject.toml` 中 `.[dev]` 依赖里的 `numpy` / `pyyaml` / `pytest-subtests`
- `.planning/notion_control_plane.json` 对应的页面和数据库都可访问，控制面没有坏
- 但 Notion dashboard / status / 09C / 10 仍停留在旧 HEAD、旧分支、旧测试基线和旧阶段叙事
- `README.md` 仍把项目讲成 `lightweight simulation harness`，已经落后于当前真实项目形态

## 你的第一响应必须做什么

你的第一响应只能输出：

- 总判断
- 分阶段执行方案
- 每阶段验收标准
- 关键风险与边界
- 需要人工处理的 GitHub 设置清单

你的第一响应不能做这些事：

- 不能直接 patch
- 不能直接重写 README
- 不能直接改 workflow
- 不能直接改 Notion sync
- 不能跳过阶段划分直接进入实现

## 你必须采用的优先级

请严格按以下优先级组织你的执行方案：

1. `CI / workflow truth`
2. `repo / GitHub / Notion source-of-truth 对齐`
3. `README / GitHub 页面定位刷新`
4. `Notion sync 逻辑与活跃页面刷新`
5. `项目价值叙事与目标架构重写`

## 你必须覆盖的阶段

你的方案至少必须包含以下五个阶段：

1. CI 和 validation 闭环恢复
2. repo / GitHub / Notion source-of-truth 对齐
3. GitHub 页面与 README 定位刷新
4. Notion sync 逻辑与活跃页面刷新
5. 项目价值叙事与目标架构重写

## 你的实施边界

在第一阶段和方案设计中，必须遵守以下边界：

- 不改真值层接口
- 不重写 `controller` / adapter truth
- 不允许把 UI 或 LLM 层变成第二套隐藏规则引擎
- `certified` / `demonstrative` 的表述必须保持诚实
- 不能把内部 authority-backed 口径写成外部适航或外部认证
- Notion 与 GitHub 页面必须跟随 repo 已验证事实，不能反向定义 repo 真相
- 当前优先目标是治理收口，不是功能扩展

## 你需要优先检查的关键面

- `.github/workflows/gsd-automation.yml`
- `README.md`
- `tools/gsd_notion_sync.py`
- `.planning/notion_control_plane.json`
- `docs/coordination/plan.md`
- `docs/coordination/dev_handoff.md`

## 你的方案必须显式包含的验收条件

- 本地 `python3 tools/run_gsd_validation_suite.py --format json` 保持全绿
- GitHub 最新 `GSD Automation Loop` 的 `validation` 变绿，且失败原因被解释清楚
- Notion dashboard / `01 当前状态` / `09C 当前 Opus 4.6 审查简报` / `10 Freeze Demo Packet` 使用统一的当前 HEAD、阶段和分支策略口径
- GitHub 仓库页面与 `README.md` 顶部定位不再把项目表述成单纯 simulation harness
- 对无法通过 repo patch 自动修复的 GitHub 仓库设置，单独输出人工设置清单

## 你对项目的重定位方向

在治理收口完成后，你应把项目重新定位为：

> 民航控制逻辑需求到验证证据的工程工作台

不要再把它讲成：

- 单纯仿真 harness
- 单纯 demo cockpit
- 单纯聊天 UI

## 你的输出格式

请严格使用以下结构输出你的第一响应：

1. 总判断
2. 分阶段执行方案
3. 每阶段验收标准
4. 风险与实施边界
5. 人工 GitHub 设置清单

## 额外要求

- 不要从零开始推翻现有判断
- 不要忽略现有 repo 证据
- 不要把 Notion 当前页面文案直接当成真相
- 如果你发现新的冲突，请明确写出“冲突点 -> 你采用的真值来源 -> 原因”
- 你的第一响应结束时，不要附带 patch，不要附带伪代码实现，不要附带大段 changelog

你现在只需要输出“执行方案”，不要执行改动。
