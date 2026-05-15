# Reverse Logic Demo UI Blueprint Development Brief

Date: 2026-05-14

This file is the handoff brief for implementing the final UI blueprint of the DeepSeek V4 Pro driven reverse-logic demo flow in AI-FANTUI LogicMVP.

## Read First

Worktree:

`/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui`

Blueprint pack:

`/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/artifacts/deepseek-live-full-chain-ui-blueprint/final-ui-blueprint-screenshots-20260514`

Start with:

1. `MANIFEST.md`
2. `selected-final-set/14-selected-overview-board.png`
3. `selected-final-set/27-global-nav-default-workbench.png`
4. `selected-final-set/28-command-palette-advanced-entry.png`
5. `selected-final-set/38-panel-state-strategy-final.png`
6. This brief

Use `selected-final-set/` as the implementation reference. Use `screenshots/` only as supporting context.

## Product Goal

Implement a compact, canvas-first engineering UI for the reverse-logic demo flow:

`/requirements-intake -> /logic-builder -> /fault-injection-prepare -> /fault-injection-sandbox`

The final UI must let a user:

1. import or select a requirement source,
2. confirm extracted control conditions,
3. inspect the generated logic graph,
4. adjust parameters,
5. run simulation,
6. inject faults,
7. review sandbox results,
8. trace evidence back to source text,
9. replay events,
10. generate/export a report.

The UI must preserve all capabilities, but it must not expose all controls by default.

## Core Design Philosophy

Default screen exposes only five entry points:

- `画布`
- `运行`
- `参数`
- `证据`
- `报告`

Everything else is reachable through:

- command palette,
- bottom drawer,
- right inspector,
- tabs,
- row expanders,
- contextual node/fault actions.

The main graph/canvas is the primary object. Sidebars, evidence, parameters, diagnostics, and reports are supporting surfaces.

## Non-Negotiable UI Requirements

- Reduced web viewport must work at a 1366x768-style height.
- The default workflow must not require vertical scrolling.
- Left rail and right inspector must be hideable and reopenable.
- Default state should collapse both side panels.
- The bottom parameter/simulation drawer may open, but it must not permanently shrink the canvas.
- Only one large auxiliary surface should be fixed at a time.
- When the bottom drawer is open, the right inspector should behave like a floating or collapsible layer.
- Text must not overlap controls.
- No nested cards.
- No marketing hero section.
- No decorative background blobs.
- No raw JSON as the primary user workflow.
- Chinese-first, domain-facing labels.

## Sandbox And Truth Boundary

The UI may display, simulate, compare, and package candidate logic. It must not imply certified control-truth changes.

Preserve these invariants wherever run/archive/review data appears:

- `truth_effect: "none"`
- `candidate_state: "sandbox_candidate"`
- `certification_claim: "none"`
- `controller_truth_modified: false`

Do not edit:

- `src/well_harness/controller.py`
- frozen adapters
- certified hardware YAML
- truth-level/DAL/PSSA data
- production certification claims

## Selected Screenshot Map

### 1. Blueprint Overview

Image:

`selected-final-set/14-selected-overview-board.png`

Purpose:

Defines the complete IA and flow sequence. Use it as the table of contents for the implementation.

### 2. Default Workbench

Image:

`selected-final-set/27-global-nav-default-workbench.png`

Target behavior:

- compact top bar,
- collapsed left icon rail,
- collapsed right vertical tabs,
- bottom run strip,
- central canvas workspace,
- sandbox/truth boundary chips.

### 3. Command Palette

Image:

`selected-final-set/28-command-palette-advanced-entry.png`

Target behavior:

The command palette is the only default advanced entry. It should expose:

- run simulation,
- open parameter drawer,
- open evidence,
- inject fault,
- open failure path,
- step replay,
- generate report,
- export review package,
- focus canvas,
- hide/show panels.

### 4. Blank Canvas / Template Entry

Image:

`selected-final-set/29-blank-canvas-template-entry.png`

Target behavior:

The user can start from:

- blank canvas,
- DOCX L1-L4 official template,
- recent sandbox restore.

Do not default to a heavy form or long onboarding page.

### 5. Generated Logic Canvas

Image:

`selected-final-set/30-docx-template-generated-canvas.png`

Target behavior:

Generated logic should show short labels, readable wires, source badges, stage chips, and a run-ready bottom strip.

### 6. Running Signal Propagation

Image:

`selected-final-set/31-running-signal-propagation.png`

Target behavior:

Simulation state should be visible through:

- highlighted active wires,
- current frame,
- timeline ticks,
- compact output verdict,
- current signal values.

Avoid opening large logs by default.

### 7. Parameter Drawer

Image:

`selected-final-set/32-parameter-drawer-final.png`

Target behavior:

Use a bottom drawer for:

- RA height,
- SW1/SW2,
- VDT ground speed,
- TRA threshold,
- sample rate,
- simulation step,
- scenario preset,
- dry-run / real-value mode,
- apply/reset/pin/collapse.

### 8. Fault Injection

Image:

`selected-final-set/33-fault-injection-final.png`

Target behavior:

Fault injection should use a compact matrix and path highlight:

- ID,
- injection position,
- fault type,
- trigger condition,
- expected impact,
- covered path,
- risk,
- status.

Advanced parameters belong in row expanders, not default columns.

### 9. Failure Diagnosis

Image:

`selected-final-set/34-failure-diagnosis-path.png`

Target behavior:

When sandbox fails, automatically open a right diagnostic inspector with:

- failure summary,
- affected path,
- first abnormal node,
- input snapshot,
- suggested fix,
- evidence links.

The canvas should highlight the failing path.

### 10. Evidence Trace

Image:

`selected-final-set/35-evidence-trace-final.png`

Target behavior:

Every important node/condition should trace to:

- source excerpt,
- anchor ID,
- requirement level,
- confidence,
- reviewer note,
- related run frames,
- related faults.

### 11. Sandbox Review

Image:

`selected-final-set/36-sandbox-review-final.png`

Target behavior:

Review rows should be compact and evidence-linked:

- condition completeness,
- threshold consistency,
- uncertainty handling,
- fault coverage,
- replay reproducibility,
- report traceability,
- controller truth unchanged.

### 12. Replay And Report

Image:

`selected-final-set/37-replay-report-final.png`

Target behavior:

Report preview and replay timeline should be cross-linked. Report sections must link back to canvas nodes and timeline events.

### 13. Panel State Strategy

Image:

`selected-final-set/38-panel-state-strategy-final.png`

Target behavior:

Implement these layout rules:

- default collapsed,
- at most one fixed auxiliary panel at a time,
- bottom drawer turns right inspector into floating/collapsible layer,
- no vertical scrolling at small height,
- steps become compact tabs/chips,
- advanced capabilities enter through command palette.

### 14. Concept Video Storyboard

Image:

`selected-final-set/39-concept-video-storyboard.png`

Purpose:

Use this as a future video prompt/storyboard. Do not block UI implementation on video generation.

## Implementation Phases

### Phase 0 - Freeze The Blueprint Contract

Deliver:

- implementation spec or updated coordination doc,
- screenshot map linked to the selected final set,
- acceptance checklist for layout and interactions.

### Phase 1 - Global Shell And Space Strategy

Deliver:

- compact top bar,
- collapsed left rail,
- collapsible right inspector,
- bottom run strip,
- route-consistent layout tokens,
- 1366x768 no-scroll geometry evidence.

### Phase 2 - Command Palette And Five Default Entries

Deliver:

- command palette,
- default entries: canvas, run, parameters, evidence, report,
- keyboard-accessible search/actions,
- no default exposure of advanced controls.

### Phase 3 - Parameter, Simulation, Fault, Review, Evidence, Report

Deliver:

- bottom parameter/simulation drawer,
- running timeline and event ticks,
- fault matrix with affected path highlight,
- sandbox review rows,
- right evidence/diagnosis inspector,
- replay/report cross-linking.

### Phase 4 - Verification And Artifact Evidence

Deliver:

- focused tests,
- Playwright or browser screenshot evidence,
- geometry evidence proving no default vertical scrolling,
- final implementation summary.

## Suggested Verification Commands

Run from:

`/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui`

Commands:

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_requirements_intake_webui.py
PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_deepseek_ui_workbench_flow.py
git diff --check
```

If e2e cannot run, report the exact missing browser/runtime prerequisite. Do not claim visual completion from static checks alone.

## New Codex Session Prompt

Copy the prompt below into a new Codex session:

```text
接手 AI-FANTUI LogicMVP 的 DeepSeek V4 Pro 反推逻辑演示舱 UI 蓝图落地工作。

工作目录：
/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui

先阅读这些文件和目录：
1. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/WORKTREE_INDEX.md
2. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/AGENTS.md
3. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/artifacts/deepseek-live-full-chain-ui-blueprint/final-ui-blueprint-screenshots-20260514/MANIFEST.md
4. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/artifacts/deepseek-live-full-chain-ui-blueprint/final-ui-blueprint-screenshots-20260514/BLUEPRINT_UI_DEVELOPMENT_BRIEF.md
5. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/artifacts/deepseek-live-full-chain-ui-blueprint/final-ui-blueprint-screenshots-20260514/selected-final-set/
6. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/tests/test_requirements_intake_webui.py
7. /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/tests/e2e/test_deepseek_ui_workbench_flow.py

开发目标：
把 selected-final-set/ 里的最终 UI 蓝图落地到现有 DeepSeek 反推逻辑 WebUI 链路：
/requirements-intake -> /logic-builder -> /fault-injection-prepare -> /fault-injection-sandbox

最终效果：
1. 默认界面 canvas-first，适配 1366x768 风格的 WebUI 可视高度，不需要上下滚动。
2. 默认只暴露五个必要入口：画布、运行、参数、证据、报告。
3. 左侧 rail、右侧 inspector 都能收起/展开。
4. 高级能力通过命令面板、底部抽屉、右侧检查器、tabs、row expanders 按需进入。
5. 保留并可操作参数调节、仿真运行、故障注入、沙盒审查、证据追溯、回放报告。
6. 参数和仿真控制放到底部抽屉，不长期挤压主画布。
7. 故障、失败诊断、证据、报告都要能反向定位到 canvas 节点、时间轴事件、来源锚点。
8. 不把 raw JSON 作为主工作流。

硬约束：
1. 不改 src/well_harness/controller.py。
2. 不改冻结 adapters、认证硬件 YAML、truth-level/DAL/PSSA 数据或生产认证声明。
3. 保留 sandbox-only 语义：
   - truth_effect: "none"
   - candidate_state: "sandbox_candidate"
   - certification_claim: "none"
   - controller_truth_modified: false
4. 不引入 React/Vite/新前端框架、数据库、云同步、多人协作、权限、评论、shared cursor 或新编排系统。
5. 不 weaken/skip/xfail 测试。
6. 中文优先，领域语言优先，不把内部字段当作默认主标签。

建议先做的最小可验收 slice：
Phase 1: 只落地全局 shell 和空间策略：
- compact top bar
- collapsed left rail
- collapsible right inspector
- bottom run strip
- command palette entry
- 1366x768 默认无纵向滚动
- selected-final-set/27、28、38 对应的布局状态

然后再进入 Phase 2/3：
- 参数/仿真底部抽屉
- 故障矩阵和影响路径高亮
- 失败诊断右侧 inspector
- 证据追溯
- 回放报告

验收命令：
PYTHONPATH=src:. python3 -m pytest -q tests/test_requirements_intake_webui.py
PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_deepseek_ui_workbench_flow.py
git diff --check

请先执行 preflight：
pwd
git status --short --branch
python3 --version
读取上述 brief 和 selected-final-set，汇报你准备实现的 Phase、目标文件、验收方式。
如果 worktree 里已有 dirty changes，先分类哪些是现有基线、哪些会被本轮修改，不要回滚用户或其他会话的改动。
```
