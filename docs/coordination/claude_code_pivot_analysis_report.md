# AI FANTUI LogicMVP 审查与 Claude Code 转向报告

更新日期：2026-04-22

## 1. 交付目标

这份报告用于把当前项目的真实状态、GitHub 对外工程面、Notion 控制中枢状态，以及三者之间的漂移点，一次性讲清楚，并作为后续 Claude Code 执行“项目转向与治理收口”的事实基线。

本报告的判断基线固定为：

- `repo` 是代码真相
- `GitHub` 是对外工程面
- `Notion` 是控制中枢

结论上，三者必须先对齐，再谈产品叙事、架构升级和项目转向。

## 2. 执行前总判断

当前项目的首要问题不是核心能力不足，而是治理面与表达面的漂移已经开始遮蔽真实能力。

从代码真实能力来看，项目已经明显超出 README 中“lightweight simulation harness”的定位，更接近：

> 民航控制逻辑需求到验证证据的工程工作台

但从 GitHub 页面、CI 行为、Notion 当前活跃页面、以及 repo 内部分文档来看，这个项目正在同时讲多个版本的故事，且彼此不一致。

当前优先级必须固定为：

1. `CI / workflow truth`
2. `repo / GitHub / Notion source-of-truth 对齐`
3. `README / GitHub 定位刷新`
4. `Notion sync 逻辑与活跃页面刷新`
5. `项目价值叙事与目标架构重写`

不能先重写故事，再放任 GitHub、Notion、CI 继续讲错故事。

## 3. 证据基线

### 3.1 Repo 当前事实

- 当前本地 `HEAD` 为 `433949d`，位于 `main`。
- 本地 `python3 tools/run_gsd_validation_suite.py --format json` 为全绿。
- 本地 `python3 tools/validate_notion_control_plane.py --format json` 也为全绿。
- `README.md` 顶部仍将项目表述为 `lightweight simulation harness`，且继续强调“first cut focuses on deploy-only behavior”，已经明显落后于当前真实产品形态。
- `README.md` 还写着 “Project Status: Active on claude/c919-etras-frozen-v1-migration branch”，与当前 `main@433949d` 的真实状态不一致。
- `.planning/STATE.md` 仍混有多套历史阶段、历史分支、历史测试基线口径，不能继续被当作当前对外说明的直接事实源。

### 3.2 GitHub 当前事实

- 仓库为私有库。
- 默认分支为 `main`。
- `main` 当前 HEAD 为 `433949d`。
- 仓库 `description` 为空。
- 仓库 `homepage` 为空。
- 仓库 `topics` 为空。
- 当前没有 open issues / PR。
- 最新 `GSD Automation Loop` 的结果表现为：
  - `regression` 通过
  - `validation` 失败
  - `notion-sync` 跳过
- 失败原因不是核心逻辑回归，而是 workflow 的依赖安装策略漂移：
  - `.github/workflows/gsd-automation.yml` 中 `validation` 只安装了 `jsonschema pytest`
  - `pyproject.toml` 的 `.[dev]` 依赖还包含 `numpy`、`pyyaml`、`pytest-subtests`
  - 因此 CI 在测试收集阶段就会因为缺依赖而报错
- 这意味着当前 GitHub 红灯主要是环境与 workflow truth 漂移，不是代码主线已经失真。

### 3.3 Notion 当前事实

- `.planning/notion_control_plane.json` 配置完整，且页面和数据库都可访问。
- 本地控制面验证脚本返回 `status: pass`，说明控制面“活着”，不是权限损坏，也不是对象丢失。
- 但控制面内容存在明显漂移：
  - dashboard 最近编辑时间是 2026-04-22，但内容仍写旧的 `main HEAD 61b12b3`
  - dashboard 仍写旧工作分支 `codex/p43-02-orchestrator-extend`
  - dashboard 仍写旧测试基线 `pytest 796 passed`
  - `01 当前状态` 也停在旧 HEAD / 旧分支口径
  - `09C 当前 Opus 4.6 审查简报` 仍停留在 P42 语境
  - `10 Freeze Demo Packet` 仍停留在 P30 语境
- 结论必须写清楚：

> Notion 不是坏了，而是当前 sync 逻辑已经不能稳定表达 repo / GitHub 的真实状态。

## 4. 漂移矩阵

| 面 | 当前真实状态 | 当前对外/控制面表达 | 结论 |
| --- | --- | --- | --- |
| Repo | `main@433949d`，本地验证绿 | README 仍讲 deploy-only harness，且写旧分支 | 叙事与状态双重漂移 |
| GitHub Actions | regression 绿，validation 红 | 红灯容易被误读为主线功能回归 | 实际是 workflow 依赖策略漂移 |
| Notion dashboard/status | 页面与数据库可访问 | 内容仍停留在旧 HEAD、旧分支、旧测试基线 | 控制面“活着但失真” |
| README / Repo Docs | 项目已是工程工作台雏形 | 仍以轻量仿真 harness 自我介绍 | 产品定位严重滞后 |

## 5. 分级问题清单

### P0

- GitHub workflow 依赖安装错误，导致 `validation` 红灯不能代表真实主线健康度。
- repo / GitHub / Notion 对于 `HEAD`、分支、测试基线的口径不一致。
- 现有 coordination 文档顶部自动同步快照仍停留在旧阶段，进一步放大漂移。

### P1

- `README.md` 与 GitHub 页面定位过时，继续把项目讲成单纯 simulation harness。
- Notion 的 `status / opus_brief / freeze_packet` 不再反映当前阶段。
- repo 内存在多套历史阶段口径，缺少单一、可验证、对外可复述的当前主线叙事。

### P2

- GitHub 仓库页面缺少 `description`、`homepage`、`topics`。
- GitHub 侧几乎没有治理入口，仓库页面无法帮助外部快速理解项目定位。
- 即使代码能力在增长，工程面对外表达仍然近乎空白。

## 6. 产品转向结论

Claude Code 后续在重写叙事与架构时，应把项目正式定位为：

> 民航控制逻辑需求到验证证据的工程工作台

不要再把它讲成：

- 单纯演示舱
- 单纯 lightweight simulation harness
- 单纯聊天式 cockpit UI

这个项目当前最有价值的主线，不是“AI 能解释控制逻辑”，而是已经形成了接近完整的工程闭环：

`需求/资料 -> 规格澄清 -> adapter truth -> playback -> diagnosis -> knowledge -> bundle/archive -> traceability`

也就是说，它更像一个工程工作台，而不是一个漂亮但脆弱的 demo。

## 7. Claude Code 的第一响应要求

Claude Code 在收到本报告后，第一步只能输出“分阶段执行方案”，不能直接开始 patch。

这个执行方案至少必须覆盖以下五个阶段：

1. CI 和 validation 闭环恢复
2. repo / GitHub / Notion source-of-truth 对齐
3. GitHub 页面与 README 定位刷新
4. Notion sync 逻辑与活跃页面刷新
5. 项目价值叙事与目标架构重写

Claude 的第一份输出必须是方案，不是改动。

## 8. Claude Code 的实施边界

第一阶段必须遵守以下边界：

- 不改真值层接口，不重写 `controller` / adapter truth
- 不允许把 UI 或 LLM 层变成第二套隐藏规则引擎
- `certified` / `demonstrative` 的表述必须保持诚实，不能把内部 authority-backed 口径写成外部认证
- Notion 和 GitHub 页面更新必须以 repo 已验证事实为准，不能反向覆盖 repo 真相
- 治理收口优先于功能扩展

## 9. 建议 Claude 首批触达的关键面

在执行方案落地阶段，建议 Claude 优先处理以下面：

- `.github/workflows/gsd-automation.yml`
- `README.md`
- `tools/gsd_notion_sync.py`
- `.planning/notion_control_plane.json`
- `docs/coordination/plan.md`
- `docs/coordination/dev_handoff.md`

只有在这些面收口后，才进入更大范围的架构与文档调整。

## 10. 验收条件

Claude 的方案中必须显式包含以下验收条件：

- 本地 `python3 tools/run_gsd_validation_suite.py --format json` 仍然全绿
- GitHub 最新 `GSD Automation Loop` 的 `validation` 变绿，且失败原因被解释清楚
- Notion dashboard / `01 当前状态` / `09C 当前 Opus 4.6 审查简报` / `10 Freeze Demo Packet` 对同一当前阶段、HEAD、分支策略使用统一口径
- GitHub 仓库页面与 `README.md` 顶部定位不再把项目表述成单纯 simulation harness
- 如果有 GitHub 仓库设置项无法通过 repo patch 自动修复，Claude 必须把它们列成“人工 GitHub 设置清单”

## 11. 建议的人工 GitHub 设置清单

以下项目可能无法完全通过 repo 内 patch 自动修复；如果 Claude 无法自动处理，应单独列成需要人工执行的 GitHub 设置清单：

- 仓库 `description`
- 仓库 `homepage`
- 仓库 `topics`
- `main` 分支保护策略
- 是否启用 `delete branch on merge`
- 是否启用 `allow auto-merge`
- 是否启用 `allow update branch`

这些不是当前 P0 阻塞项，但它们决定 GitHub 是否能成为合格的对外工程面。

## 12. 建议 Claude 的输出格式

建议 Claude 第一响应采用以下结构：

1. 总判断
2. 分阶段执行方案
3. 每阶段验收标准
4. 关键风险与边界
5. 人工 GitHub 设置清单

## 13. 关键证据入口

- Repo:
  - `README.md`
  - `.github/workflows/gsd-automation.yml`
  - `pyproject.toml`
  - `.planning/STATE.md`
  - `.planning/notion_control_plane.json`
  - `tools/run_gsd_validation_suite.py`
  - `tools/validate_notion_control_plane.py`
- Coordination:
  - `docs/coordination/plan.md`
  - `docs/coordination/dev_handoff.md`
- External:
  - GitHub Actions: <https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions>
  - GitHub Repo: <https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp>
  - Notion 控制塔: <https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec>

## 14. 一句话收口

当前项目需要的不是“再做一个更炫的页面”，而是先把 repo、GitHub、Notion 重新对齐到同一个真实工程故事上；只有这样，这个项目才能系统性地讲清自己在民航飞机控制逻辑设计流程里的价值。
