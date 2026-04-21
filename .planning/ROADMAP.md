# Roadmap

## Current Milestone

**Project Freeze — All P0-P16 Complete + Federation Model Defined (2026-04-15)**。Milestone 9 — Project Freeze (2026-04-15)。Opus 4.6 Final Adjudication: Project reached MVP达标线，建议冻结。P16 AI Canvas Sync 已完成（真值引擎先行+AI标注后到）。联邦架构战略已裁定并文档化（整合≠合并，三级门槛）。GSD automation 保持运行保护回归。

## Phase P0: Control Tower And GSD Control Plane

Status: Done

Goal: Create the independent Notion control tower and align it with the local GSD model.

Exit Criteria:

- Notion root page exists as `AI FANTUI LogicMVP 控制塔`.
- Roadmap, task, session, decision, QA, asset, risk, plan, execution run, review gate, and UAT gap objects exist.
- The control tower treats GitHub / repo as code truth and Notion as control plane.

## Phase P1: Automate Execution And Evidence Writeback

Status: Done

Goal: Connect the local/GitHub GSD execution loop to Notion so plan runs, QA outcomes, and UAT gaps write back automatically, while keeping GitHub and Notion as the only evidence surfaces used by Opus 4.6.

Exit Criteria:

- A local script can run validation commands and write Execution Run + QA + UAT Gap state to Notion.
- A GitHub Actions workflow reuses the same script.
- The GitHub repo and workflow runs are usable as review evidence from Notion.
- Missing Notion or GitHub credentials degrade safely without leaking secrets.
- Failures become UAT gaps; subjective review is routed through the Opus 4.6 review gate without citing local terminal files.
- P1 was approved in the Review Gate and the two historical same-plan failure gaps were resolved as superseded.

## Phase P2: Harden Opus 4.6 Review Packets

Status: Done

Goal: Standardize the Opus 4.6 review packet so subjective approval happens from Notion pages and the GitHub repo alone.

Exit Criteria:

- A state-driven current Opus 4.6 review brief exists in Notion and can be refreshed from live control-plane state.
- Review Gate instructions explicitly forbid local terminal file references.
- The boundary between automated validation and Opus 4.6 subjective review is explicit.
- The current brief successfully drove an Opus adjudication that approved P1 and resolved legacy gaps.

## Phase P3: Reduce Control-Plane Drift

Status: Done

Goal: Keep the automated loop stable as validation entrypoints, Notion evidence, and Opus review packets evolve.

Exit Criteria:

- Local runs, GitHub Actions, and Notion writeback all reuse a single validation entrypoint.
- Same-plan legacy automation gaps auto-resolve after later successful runs.
- The current Opus 4.6 review brief generator stays aligned with the live Notion control-tower structure and GitHub evidence URLs.
- Superseded legacy review artifacts retire automatically once the default gate is approved and 09C says no review is required.
- The GitHub Actions workflow stays aligned with GitHub-hosted runner runtime deprecations without reintroducing manual review dependence.

## Phase P4: Elevate Cockpit Demo To Presenter-Ready

Status: Done

Goal: Turn the current cockpit demo candidate into a presenter-ready local demo that stays deterministic, explainable, and honest about the simplified plant boundary.

Exit Criteria:

- The first-screen cockpit flow, presenter talk track, and structured answer panel stay aligned around the same live-demo route.
- Presenter-critical prompts and lever interactions are regression-protected without introducing browser-only approval steps or a second control-truth layer.
- Demo copy and UI make the distinction between controller truth and simplified plant feedback explicit wherever a live audience could misread it.
- `POST /api/demo`, `POST /api/lever-snapshot`, `well_harness demo`, and `well_harness demo_server` remain stable unless a later plan explicitly changes their contracts.

## Phase P5: Demo Polish And Edge-Case Hardening

Status: Done

Goal: Harden the presenter demo against edge-case interactions and replace residual browser-only confidence checks with GitHub-verifiable smoke coverage.

Exit Criteria:

- Rapid lever edits, fast condition toggles, and extreme-value inputs are regression-protected by automated tests.
- A demo-path smoke suite runs in GitHub Actions without requiring browser-only approval steps.
- Residual "manual browser QA" expectations are either automated, narrowed into explicit scripts, or retired as no longer needed.
- The controller-truth versus simplified-plant boundary remains explicit, and no second control-truth layer is introduced while polishing the demo.

## Phase P6: Reconcile Control Tower And Freeze Demo Packet

Status: Done

Goal: Turn the now-stable P5 demo evidence into a consistent freeze-ready control-tower story, so Notion status pages, repo docs, and final presenter handoff materials all match the latest GitHub-backed truth without adding new product surface.

Exit Criteria:

- `01 当前状态` and related control-tower summaries no longer point at stale `129 tests OK` / manual-browser-QA-only guidance once P5 is approved.
- A concise freeze/demo packet exists that summarizes the latest stable GitHub evidence, current smoke coverage, presenter boundary conditions, and the remaining human signoff step.
- Historical browser hand-check notes are either archived or explicitly reframed as presenter aids rather than active approval requirements.
- No new demo features, controller-truth changes, or API-contract changes are introduced while preparing the freeze packet and documentation closure.
- The control plane can explicitly acknowledge dashboard-only degraded mode when archived Notion subpages block direct writes, without pretending those subpages are still healthy.

## Phase P7: Build A Spec-Driven Control Analysis Workbench

Status: Done

Goal: Add a reusable control-system specification layer that can drive strict scenario playback, fault injection, diagnosis, and knowledge capture without being locked to the current thrust-reverser chain alone.

Exit Criteria:

- A canonical control-system spec can describe components, logic nodes, monitored signals, acceptance scenarios, fault injection targets, and required clarification questions for new systems.
- The current thrust-reverser logic is represented as the first reference system through that spec layer without replacing `controller.py` as code truth.
- The system has a documented path from engineer-supplied process docs to monitor-vs-time traces, even if document adapters are phased in incrementally.
- A fault-analysis workflow is defined that produces reproducible reasoning artifacts, records confirmed fixes, and emits post-repair optimization suggestions.
- The onboarding path for a new control system explicitly blocks on unanswered ambiguity, instead of silently guessing at missing details.

## Phase P8: Runtime Generalization Proof

Status: Done

Goal: Prove the generalized contract layer can host a second real control-system truth adapter without changing `controller.py` or bypassing the adapter boundary.

Exit Criteria:

- P7 is explicitly treated as the completed contract/schema layer, and the runtime proof work starts from that validated baseline.
- At least one non-thrust-reverser control-system adapter publishes valid metadata and a valid control-system spec through the adapter boundary alone.
- A minimal second system can produce deterministic truth evaluations from adapter inputs without introducing a hidden hardcoded rule path outside the adapter interface.
- The constitution/state surfaces explicitly allow new system truth only through adapters and forbid bypassing adapters with new hardcoded truth paths.
- Runtime validation proves the second-system adapter can be exercised safely while the reference thrust-reverser truth remains untouched.

## Phase P9: Automation Hardening & Evidence Pipeline Maturity

Status: Done

Goal: Close the remaining manual intervention gaps in the GSD automation loop so that a plan lands on main and the Notion control plane updates automatically — with no human-initiated Notion or GitHub operations required in the happy path.

Exit Criteria:

- GSD automation loop completes a full cycle (plan → validate → Notion update → CI) without manual intervention.
- Roadmap DB Phase lifecycle (register new phase, close completed phase) is automated into the GSD loop.
- CI/CD pipeline includes three distinct stages: regression → validation → Notion sync.
- Failed Notion sync stage does not fail the overall pipeline (writeback is non-blocking).
- Roadmap DB shows P6=Done, P7=Done, P8=Done, P9=Done (no manual edits needed).
- All resolvable manual touchpoints are eliminated; irreducible human-only steps are explicitly documented with degraded-mode handling.

## Phase P10: Second-System Runtime Pipeline End-to-End

Status: Done

Goal: Prove the generalized contract layer can host a second real control-system truth adapter through the complete intake → playback → diagnosis → knowledge pipeline, with both systems producing deterministic truth evaluations and a side-by-side comparison report.

Exit Criteria:

- Landing-gear adapter → intake → playback trace → diagnosis → knowledge artifact full chain runs end-to-end, each stage output passes its v1 schema validation.
- Side-by-side comparison report shows both thrust-reverser and landing-gear runtime outputs.
- All 23 shared validation commands continue to pass (no regression).
- `/glm-execute` compliance: every plan involving >50 LOC has a `[MODEL-CALL]` audit record.
- Roadmap DB shows P9=Done, P10=Done.

## Phase P11: Product Readiness & Third-Party Onboarding Guide

Status: Done

## Milestone 4 Hold — Superseded by P12

Status: Deprecated

Milestone 4 Hold 已取消（P12 启动）。保留作为历史记录。

## Phase P12: Third-System Onboarding Validation

Status: Done

## Phase P13: Route B — Browser Workbench Multi-System Integration

Status: Done

Opus 4.6 Adjudication: Approved (2026-04-13)
Goal: 将 Demo UI 从单一 thrust-reverser 系统扩展为支持在浏览器中切换查看三个控制系统（thrust-reverser / landing-gear / bleed-air valve）的逻辑链路、状态和推理结果。

Exit Criteria:

- Demo UI 顶部或侧边提供系统切换器，可切换三个已 onboard 的控制系统。
- 切换系统后，逻辑面板（chain-panel）显示对应系统的条件逻辑节点和状态。
- 切换系统后，问答推理结果区域显示对应系统的 answer payload。
- 三个系统的 adapter 均通过已有的 v1 schema 验证链路（已在 P8/P10/P12 验证）。
- Demo server 启动时默认加载 thrust-reverser，其他系统按需加载。
- 所有 23 shared validation commands 继续通过（无回归）。
- Roadmap DB shows P13=Done.

**Plans:** 1 plan(s)

Plans:
- [x] P13-01-PLAN.md // Add system-switcher + /api/system-snapshot + data-driven chain-panel + truth-evaluation answer per system (committed: 211ab2e, 07e015d, 2f818a6, cfc4aec, a28d4dc, 182d5e4)

## Phase P14: AI Document Analyzer — Import logic circuit docs → AI ambiguity detection → Deep confirmation loop → Claude Code prompt generation

Status: Done (2026-04-13)

Goal: Build a browser UI where engineers can import control-system logic circuit documents (PDF/markdown/text), triggering an AI-powered analysis pipeline that detects ambiguous spec descriptions, runs a deep interactive confirmation dialogue loop to resolve ambiguities, and ultimately generates a structured Claude Code prompt document ready for new module development. Complements the existing `document_intake.py` pipeline by adding AI-driven ambiguity detection and clarification loops.

Exit Criteria:

- Engineer uploads a control-system spec document via browser UI (drag-drop or file picker)
- AI analyzes the document and surfaces specific ambiguous/unclear spec sections with confidence scores
- Interactive confirmation loop lets engineer clarify each ambiguity one at a time
- Loop terminates when AI determines information is sufficient and logically closed (no more blockers)
- A structured prompt document is generated containing: system overview, logic node specifications, condition rules, edge cases, and implementation guidance
- Prompt document can be previewed and exported/downloaded as markdown
- All existing 92 tests continue to pass (no regression)
- All 23 shared validation commands continue to pass
- Roadmap DB shows P14=Done

## Milestone 6 Hold — Lifted 2026-04-13

Status: Lifted

Goal: P0→P13 全栈闭环完成。后端 pipeline + 8 个 v1 schema + 3-stage CI/CD + product onboarding + browser workbench multi-system UI = 可泛化工作台 MVP 达标。Milestone 6 Hold 于 2026-04-13 解除，P14 启动。

Exit Criteria (superseded by P14 development):

- P13 = Done，0 open UAT gap。
- 所有 92 tests 继续通过（回归保护）。
- 23 shared validation commands 继续通过。
- Roadmap DB shows P13=Done.

## Milestone 7 — Complete (2026-04-13)

Status: Closed

Goal: Complete P14 — AI Document Analyzer。Build a browser UI where engineers import logic circuit spec documents (PDF/markdown/text), triggering an AI analysis pipeline that detects spec ambiguities, runs deep confirmation loops to resolve them, and generates a structured Claude Code prompt document for new module development.

Exit Criteria:

- P14 = Done (2026-04-13)
- All 326 tests continue to pass
- All 23 shared validation commands continue to pass
- Roadmap DB shows P14=Done

## Milestone 8 — Complete (2026-04-14)

Status: Closed

Goal: Complete P15 — Pipeline Integration。Connect P14 AI Document Analyzer output to P7/P8 spec-driven intake pipeline for end-to-end "document to diagnosis" workflow.

Exit Criteria:

- P15 = Done (2026-04-14)
- P14 output converts to valid control_system_spec_v1 intake packet
- Intake packet enters P7/P8 pipeline without manual editing
- Browser UI provides "Analyze → Clarify → Generate → Run Pipeline → View Diagnosis" one-click flow
- All 345 existing tests continue to pass
- All 23 shared validation commands continue to pass
- Roadmap DB shows P15=Done

## Milestone 5 Hold — Lifted 2026-04-13

Status: Lifted

Goal: P0→P12 完整闭环。三个控制系统（thrust-reverser / landing-gear / bleed-air valve）共享同一 pipeline 并全部通过 v1 schema validation。已达到"可泛化工作台 MVP"达标线。Route B 开发启动，Hold 解除。

Exit Criteria:

- `docs/freeze/MILESTONE5-HOLD.md` exists and documents the final hold declaration.
- All phase code frozen — no new feature development.
- 23 shared validation commands continue to pass (regression protection only).
- 3-system pipeline proof documented: `docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md`.
- Roadmap DB shows P12=Done, Milestone 5 Hold=Active.

Goal: Validate the P11 onboarding tools (guide + templates + dry-run script) by actually onboarding a third control system through the full pipeline — proving the tools work for non-project-owners.

Exit Criteria:

- A third control system (not thrust-reverser, not landing-gear) successfully passes through the full intake → playback → diagnosis → knowledge pipeline using `templates/new_system/` and `docs/onboarding/`.
- Each stage output passes its v1 schema validation.
- `tools/onboard_new_system_dry_run.py` exits 0 for the third system.
- Onboarding process documented as a case study in `docs/onboarding/`.
- All 23 shared validation commands continue to pass (no regression).
- Roadmap DB shows P11=Done, P12=Active.


Goal: Transform the proven two-system pipeline into a product that external engineers can successfully use to onboard a new control system — without requiring project insider knowledge.

Exit Criteria:

- A standalone onboarding guide in `docs/onboarding/` describes how to create a new system spec file → adapter → intake packet → run the full pipeline.
- A minimal template in `templates/new_system/` provides empty spec / adapter / intake packet skeletons.
- A dry-run script allows users to verify their new system spec can pass through the pipeline.
- Onboarding guide is reviewable by non-project-owners (or GLM-5.1 via `/glm-execute`) for understandability.
- All 23 shared validation commands continue to pass (no regression).
- Roadmap DB shows P10=Done, P11=Active.


### Phase 1: P14: AI Document Analyzer - Import logic circuit docs → AI ambiguity detection → Deep confirmation loop → Claude Code prompt generation

**Goal:** Build a browser UI where engineers can import control-system logic circuit documents, trigger an AI-powered analysis pipeline that detects ambiguous spec descriptions, runs deep confirmation loops, and generates Claude Code prompt documents.
**Requirements**: P14-01
**Depends on:** Phase 0
**Plans:** 1 plan(s)

Plans:
- [x] P14-01-PLAN.md // AI Document Analyzer full pipeline (7 tasks: ai module + routes + UI + nav links + tests + regression) ✓

## Phase P15: Pipeline Integration — P14 AI Document Analyzer output connects to P7/P8 spec-driven intake pipeline, enabling end-to-end document-to-diagnosis workflow

Status: Done (2026-04-14)

Goal: Connect the P14 AI Document Analyzer's generated prompt document output to the P7/P8 control-system spec intake pipeline, creating a seamless "document to diagnosis" workflow where engineers upload a spec document and receive a complete diagnosis report without manually editing JSON.

Exit Criteria:

- P14 analyze-document output (clarified ambiguities + structured spec) automatically converts to a valid control_system_spec_v1 intake packet
- The converted intake packet can enter the P7/P8 pipeline (intake → playback → diagnosis → knowledge) without manual editing
- Browser UI provides "Analyze → Clarify → Generate → Run Pipeline → View Diagnosis" one-click flow
- The AI-generated spec conversion passes v1 schema validation
- All 345 existing tests continue to pass (no regression)
- All 23 shared validation commands continue to pass

**Plans:** 1 plan(s)

Plans:
- [x] P15-01-SUMMARY.md // Pipeline Integration full pipeline (4 tasks: ai_doc_analyzer converter + routes + UI + tests + regression) ✓

## Project Freeze — Opus 4.6 Final Adjudication (2026-04-14)

**Status: Active — No active development phases**

**Opus 4.6 裁决：** P0→P15 全部完成。项目已达到"可泛化动力控制电路系统工作台 MVP"达标线。建议进入 Project Freeze。

**冻结内容：**
- 代码基线冻结，不继续自动开发
- GSD automation 保持运行（23-command validation suite 在每次 push 时保护回归）

**解冻条件（人工决策）：**
- 外部工程师实际使用后提供反馈
- 产品方向决策需要新功能
- 新的领域需求（超出控制电路分析的范围）

**继承的改进项（冻结期间可选择性处理）：**
| 优先级 | 改进项 | 状态 |
|--------|--------|------|
| P1（投产前） | 服务端文件上传大小限制 | ✅ 已完成：50MB→10MB (19fea92) |
| P2 | Content-type 白名单 | ✅ 已完成：仅允许application/json/text/plain (19fea92) |
| P2 | Pre-existing notion sync failure 修复或归档 | ✅ 已归档：degraded modes已在P6/P9硬化，无未处理失败 |
| P3 | 确认循环跳过选项 | ✅ 已完成：Skip→跳过，UI汉化 (19fea92) |
| P4（回归保护） | system_switcher_smoke URL修复 | ✅ 已完成：DEMO_URL 从 `/` 改为 `/demo.html`，匹配 Phase 3 路由真相（`/`→chat.html, `/demo.html`→专家演示舱），430 tests 无回归 (c97d95d) |
| P5 | P17 Fault Injection | ✅ 已完成：前端故障注入 UI + 后端 overrides 桥接 + 9 pytest 覆盖，439 tests 无回归 (f3f4250, 09e0c77) |

## Phase P16: AI Canvas Sync（Opus 4.6 架构裁决 — 方向A+）

Status: Done (2026-04-15)

Opus 4.6 裁决：方向A+（真值引擎先行 + AI标注后到）。拒绝方向B（AI控制Canvas，违反项目宪法）。

架构原则：**Truth engine是决定者，AI是解释者，Canvas只听truth engine的，AI只在Canvas旁加注释。**

**目标**：让AI对话和SVG Canvas实现双向同步——Canvas状态基于truth engine，AI解释基于truth结果，AI讨论的节点在Canvas上有蓝色视觉标记。

**Exit Criteria**：
- `/api/chat/explain` 返回 `highlighted_nodes` + `suggestion_nodes` + `confidence`
- 所有4个系统都可通过 `/api/system-snapshot` 获取节点状态快照
- Canvas上节点有两层视觉状态：truth层（active/blocked/inactive）+ AI讨论层（.ai-discussed）
- MiniMax context中包含truth engine的node_states（消除AI和Canvas的脱节）
- 430 tests继续通过（无回归）；P17完成 → 439 tests（+9 fault injection pytest）

**Plans:** 1 plan(s) — Codex GPT-5.4 执行

## Phase P17: Fault Injection — Interactive Fault Mode Simulation

> **Audit note (v5.2 solo, 2026-04-20):** 本 Phase 于 v4.0 Extended Autonomy Mode 下由 Executor (Codex + MiniMax-2.7) self-signed 落地（2026-04-15，439 tests 零回归）。v5.2 Claude App Solo Mode (2026-04-20) 下经 `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` 批准后统一追认 provenance。Phase 内容、测试数据、代码事实均未回修——仅证迹层追签。

Status: Done (2026-04-15)

Goal: 在 chat.html 工作台中加入可交互的故障注入 UI，让工程师可以模拟"开关卡住"、"传感器失效"、"逻辑卡死"、"命令阻塞"四种故障，观察故障下的逻辑链路变化。

架构：**Truth engine 是决定者，AI 是解释者，fault injection 是 truth engine 的已知输入覆盖。** 故障不修改 controller.py，只通过 JS `activeFaults[]` Map 注入到 `/api/lever-snapshot` 请求，demo_server 在 `_simulate_lever_state` 中短路对应节点值。

**Sub-phases:**
- P17-01 Frontend: chat.js + chat.css + chat.html — fault bar、preset buttons、node ⚡ buttons、`.is-faulted` CSS、`activeFaults` Map、`injectFault`/`removeFault`/`sendWithFaults`、`applyFaultVisual`
- P17-02 Backend: demo_server.py — `parse_lever_snapshot_request` 验证 `fault_injections`；`_simulate_lever_state` 通过 `_apply_switch/sensor/output_fault_injections` 应用短路；返回 `active_fault_node_ids` 供 Canvas 视觉标注
- P17-03 Tests: 9 个 pytest API 测试覆盖 fault injection — stuck_off/stuck_on/RA sensor_zero/invalid node/invalid type/non-list/multiple faults/baseline

**Exit Criteria:**
- chat.html 有 ⚡ 按钮触发故障注入栏，3 个 preset（SW2 卡关/TLS 失效/全链路断裂）
- `/api/lever-snapshot` 接受 `fault_injections` 并返回 `active_fault_node_ids`
- `_simulate_lever_state` 应用 sw1/sw2/RA/TLS/逻辑节点故障短路
- 439 tests 继续通过（无回归）

**Plans:** P17-01 + P17-02 Codex GPT-5.4 执行，P17-03 MiniMax-2.7 实现

## Phase P18: Demo Cleanup & Archive Integrity

> **Audit note (v5.2 solo, 2026-04-20):** 本 Phase 于 v4.0 Extended Autonomy Mode 下由 Executor self-signed 落地（2026-04-16，含 P18.5 fault UI 退场 + P18.6 SHA256 归档校验）。v5.2 Claude App Solo Mode (2026-04-20) 下经 `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` 批准后统一追认 provenance。Phase 内容、测试数据、代码事实均未回修——仅证迹层追签。

Status: Done (2026-04-16)

Goal: 清理 P17 残留 UI 噪声，为立项演示冻结可校验的工作台归档。

**Sub-phases:**
- P18.5 — 移除 fault injection UI（上游决策：故障注入退回实验室，不在立项演示暴露）、修正 Canvas 点击精度 (#1)
- P18.6 — 为工作台归档新增 SHA256 完整性校验（为审计方提供一键复核基线）

**Exit Criteria:**
- chat.html 不再出现 ⚡ fault bar / preset / 节点 fault 按钮；Canvas 点击命中率回到像素级
- 工作台 tar + SHA256 校验文件成对产出；校验脚本可独立重放
- 主 pytest 零回归

## Phase P19: Hardware Partial Unfreeze — Monte Carlo + Reverse Diagnosis + Pitch Deck

> **Audit note (v5.2 solo, 2026-04-20):** 本 Phase 于 v4.0 Extended Autonomy Mode 下由 Executor (MiniMax-2.7 主导 + Codex 关键 diff) self-signed 落地（2026-04-17，18 个 sub-phases P19.1→P19.18，634+ tests 零 controller.py 回归）。**本 Phase 同时事实上超越了 `docs/unfreeze/P17-application-draft.md`（Ready for Review 2026-04-18）所申请的"硬件部分解冻"方向** — 该申请于 P32 定性为 Superseded by P19。v5.2 Claude App Solo Mode (2026-04-20) 下经 `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` 批准后统一追认 provenance。Phase 内容、测试数据、代码事实均未回修——仅证迹层追签。

Status: Done (2026-04-17)

Goal: 把硬件描述层从"只冻结"部分解冻为"可驱动 Wow 场景"——保留 controller.py 真值边界不动，新增 YAML 参数层 + 两条独立数值通道 + 立项演示物料。

架构约束：controller.py 零改动；新增层都放在 truth engine 外围，通过确定性枚举/模拟产出数据，AI 仅负责叙述。

**Sub-phases (18 plans, P19.1 → P19.18):**
- P19.1 — hardware YAML schema + loader（thrust-reverser 参数集）
- P19.2 — Monte Carlo reliability simulation engine（wow_b 数值通道，纯计算）
- P19.3 — reverse diagnosis engine（wow_c 枚举参数组合达成目标结论）
- P19.4 → P19.17 — 支撑 API、前端按钮、端到端测试、回归硬化、演示打磨（中间 plans 合并提交；详细 plan 文档见 `.planning/phases/P19-hardware-partial-unfreeze/P19-XX-PLAN.md`）
- P19.18 — 立项演讲稿 + 三哇场景脚本（`docs/presentations/pitch-ready-demo.md` + `demo-talking-points.md`）

**Exit Criteria:**
- 三哇 API 齐备：`/api/lever-snapshot`（因果链）/`/api/monte-carlo/run`（蒙特卡洛）/`/api/diagnosis/run`（反诊断）
- 634+ pytest 全绿（无 controller.py 回归）
- 立项演讲稿和提示卡在仓库内可直接复制到 Notion

**Plans:** 18 plans — MiniMax-2.7 主导，关键前端 diff 走 Codex GPT-5.4

## Phase P20: Wow E2E Coverage + Demo Resilience + Dress Rehearsal

> **Audit note (v5.2 solo, 2026-04-20):** 本 Phase 于 v4.0 Extended Autonomy Mode 下由 Executor self-signed 落地（2026-04-18，含 P20.2 子 Phase；默认 CI 639 pass 不变 + opt-in e2e 38→49 pass + adversarial 8/8 PASS 不变）。v5.2 Claude App Solo Mode (2026-04-20) 下经 `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md` 批准后统一追认 provenance。Phase 内容、测试数据、代码事实均未回修——仅证迹层追签。

Status: Done (2026-04-18, 含 P20.2 子 Phase)

Goal: 把三哇从"能跑"升级为"抗操作失误 + 可自动彩排"。

**Sub-phases:**
- P20.0-A/B/C/D — e2e 套件覆盖三哇 Canvas/抽屉 DOM 断言、按键级演示脚本、P17 unfreeze 申请草稿
- P20.1-E — demo resilience（降级徽标、错误降级叙述、对抗测试硬化）
- P20.2 — dress rehearsal 自动化（`scripts/dress_rehearsal.py`）+ 7 场景灾难手册（`docs/demo/disaster_runbook.md`）+ 彩排基线冻结 + 离线 tarball

**Exit Criteria:**
- e2e lane 49/49 全绿；主 pytest 零回归
- Dress rehearsal 脚本一键产出 wow_a/b/c timeline + 报告
- `docs/freeze/2026-04-18-rehearsal-baseline.md` 含 SHA256 基线；`docs/demo/disaster_runbook.md` 7 场景 × 4 字段

**Plans:** P20.0-A…D + P20.1-E + P20.2 — MiniMax-2.7 执行，e2e 断言与灾难手册 Codex 审查

## Phase P21: Local Model PoC — 国产模型本地降级

> **Audit note (v5.2 solo, 2026-04-20):** closure flags for P21–P30 below were written forward from the v4.0 Extended Autonomy window on 2026-04-18/19 by orphan commit `4474505` (Codex, unsigned). They are factually consistent with Notion control-tower state at that time. Provenance re-signed on 2026-04-20 under v5.2 Claude App Solo Mode via `.planning/audit/P31-orphan-4474505-audit.md`. They are NOT net-new Gate approvals issued by the re-land commit.

Status: Done (2026-04-18)

Goal: 把 AI 叙述层从"绑定 MiniMax 云 API"解耦为"云/本地双后端可切换"，为甲方合规（数据不出境）和灾难降级（断网）提供工程级答案。

架构约束：只动 adapter 边界，不动 controller.py / API 契约 / 前端 UI；错误码做等价前缀映射让降级徽标零改动。

**Sub-phases:**
- P21-01 — 抽取 `LLMClient` Protocol + MiniMax/Ollama 适配器 + `get_llm_client()` 工厂；19 个单元测试锁定契约
- P21-02 — `config/llm/local_model_candidates.yaml`（Qwen2.5-7B/14B、GLM4-9B、DeepSeek-V2-Lite）+ pull_cmd + 硬件预算注释
- P21-03 — `scripts/local_model_smoke.py` + 首次真跑（Qwen2.5-7B 3/3 PASS / 4.2–5.4s，报告在 `runs/local_model_smoke_20260418T072226Z/`）
- P21-04 — `docs/demo/local_model_poc.md`（架构图 + 切换命令 + R1–R5 自审）+ PATCH `disaster_runbook.md` 场景 1 指向本地 fallback

**Exit Criteria:**
- 主 pytest 658 pass / 1 合法 skip；e2e 49/49；对抗 8/8（全无回归）
- `LLM_BACKEND=ollama OLLAMA_MODEL=qwen2.5:7b-instruct` 一行切换成立，`/api/chat/{explain,operate,reason}` 三端点在本地模型下真跑通过
- 灾难手册场景 1 首选 fallback 已改为本地模型

**Plans:** P21-00 Tier 1 + P21-01…04 — 已收口并写回 `GATE-P21-CLOSURE Approved`

## Phase P22: Demo Rehearsal 物料冻结

Status: Done (2026-04-18)

Goal: 把立项汇报日所有需要的"非代码制品"一次性冻结——双后端真跑证据、≤20min 话术稿、15 题 FAQ、16 项预检 checklist。

Non-goals（严格禁止）：新 wow / 改 truth engine / 调 AI prompt / 做 PPT 美化。

**Sub-phases:**
- P22-01 — `scripts/demo_rehearsal_dual_backend.py` + 双后端真跑（MiniMax + Ollama 7B）14/14 PASS，报告在 `runs/demo_rehearsal_dual_backend_20260418T074215Z/`
- P22-02 — `docs/demo/pitch_script.md`（≤20min hard-time 表 × 7 段 × 证据路径绑定 × 诚实性护栏）
- P22-03 — `docs/demo/faq.md`（15 题 × 证据文件 × R-原则锚点 × 关键词跳转表）
- P22-04 — `docs/demo/preflight_checklist.md`（T-60 → T-0 16 项 + 应急一页纸 + 一键预检脚本）

**Exit Criteria:**
- 三轨验证绿：主 pytest 658/1skip、e2e 49/49、对抗 8/8
- 双后端真跑 artefact 落盘；所有汇报物料彼此交叉引用（话术 ↔ FAQ ↔ 预检 ↔ 灾难手册）
- 立项当天可按 pitch_script 时间表直接开讲

**Plans:** P22-00 Tier 1 + P22-01…04 — 已收口并写回 `GATE-P22-CLOSURE Approved`

## Phase P23: Co-development Kit — 立项通过后首批对接物料

Status: Done (2026-04-18)

Goal: 把立项通过那一刻甲方需要的四份"对接文档"提前冻结在仓库里。纯文档 Phase，controller.py / LLM adapter / API 契约零改动。

Non-goals：新 wow / 承诺具体上线日期 / 修改真值引擎。

**Sub-phases:**
- P23-01 — `docs/co-development/api-contract.md`（三哇 + chat 六端点 schema + 版本策略 + 错误码前缀规则）
- P23-02 — `docs/co-development/security-review-template.md`（甲方 PR 审查 10 项 × R 锚点 × PASS/FAIL 信号）
- P23-03 — `docs/co-development/sla-draft.md`（Demo / Staging / Production 三级 profile × 可用性/响应/数据/AI 供应链）
- P23-04 — `docs/co-development/roadmap-2026H2.md`（H2-23 → H2-27 对外路线图，含 H2-24 PoC / H2-25 硬化 / H2-26 首批 validation / H2-27 季度审计；外部命名空间见该文件顶部说明，2026-04-20 P32 W5 去重）

**Exit Criteria:**
- 四份文档全部落 `docs/co-development/`，每份带"给谁看 / 回答什么 / 何时变动"头部
- 主 pytest 658/1skip 零回归（纯文档应自动成立）
- `GATE-P23-CLOSURE` 已 Approved，并已完成 Notion sync 回写

**Plans:** P23-00 Tier 1 + P23-01…04 — Executor 独立执行；Gate 已独立复核并收口

## Phase P24: 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals

Status: Done (2026-04-18) · `GATE-P24-CLOSURE` Approved

Goal: 把三个前端 surface（demo.html / chat.html / workbench.html）的视觉层统一到工业级水准，在不改变任何行为的前提下抽出共享 design tokens、补齐 hover/focus/empty states。

Non-goals：修改 controller.py / 19-node 真值引擎 / LLM adapter / AI prompts / 新 wow 场景 / 重构 state management / 引入新框架。

**Sub-phases:**
- P24-01 — `design-tokens.css`（79 行共享色板/字体/运动/阴影 tokens）+ demo.css / chat.css / workbench.css / ai-doc-analyzer.css 通过 `@import` 接入；surface-local override 保留各 surface 非 canonical 差异（零视觉回归）
- P24-02 — chat drawer polish：消息卡片 border-radius 统一到 10px，transition 改用 motion tokens，新增 `:empty::before` 空态 "等待提问…" chip
- P24-03 — workbench chrome polish：toolbar/run/file-picker 按钮补齐 hover/active/focus-visible/[disabled] 状态；form inputs 补焦点环；workbench.html 无 SVG canvas（SVG 节点在 demo.html，归 P24-04 管）
- P24-04 — demo visuals polish：`.presenter-callout` 可读性升级（背景 0.10→0.14 / 边框 0.30→0.42 / 字距 + nowrap），`.presenter-run-card` 加 `--shadow-md` 深度分离。保守 scope 确保 P22 话术 keyword 零偏离

**Exit Criteria:**
- 主 pytest 658/1skip 零回归（四次 sub-phase 全部命中）
- Opt-in e2e 49/49 + adversarial 8/8 零回归（四次 sub-phase 全部命中）
- P22 话术 keyword（"提问区"/"逻辑主板"/"为什么高亮"/"推理结果"/"原始 JSON 调试"/"反推逻辑演示舱"）经 test_demo.py 自动检查保持
- `GATE-P24-CLOSURE` 已 Approved，并已完成 Notion 02B Execution Run + 控制塔 DECISION 回写

**Plans:** P24-00 Tier 1 + P24-01…04 — Executor 独立执行（v3.0 rule 31）；Gate 已独立复核并收口

**注：** P24 期间确认 v3.0 已完全移除 Codex，原 Plan 草稿中"每 sub-phase Codex 审查"条款已在首次 Notion 验证后修正。未来 Phase 撰写必须先 GET Notion 11 模型分工页验证规则版本，不依赖 Executor 记忆。

## Phase P25: 立项汇报段落级时序彩排 — pitch_script.md 硬时间表的可证伪化

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode

Goal: 把 P22 冻结的 pitch_script.md 7 段硬时间表升格为可机器验证的契约——给每段分配保守 backend 时间预算（人讲时间不占），自动跑对应 API（lever-snapshot/monte-carlo/diagnosis/chat），双后端各 N=2 真跑，聚合 budget vs 实测 vs 裕度。

Non-goals：修改 controller.py / 19-node / LLM adapter / prompts / wow 脚本 / pitch_script.md 本身 / 前端 UI。

**Sub-phases:**
- P25-01 — `scripts/integrated_timing_rehearsal.py`（段落→API map + 双后端 spawn + degraded 响应检测 + 报告生成）
- P25-02 — 双后端 N=2 真跑，artefact 入库 `runs/integrated_timing_minimax_20260418T132007Z/` + `runs/integrated_timing_ollama_20260418T132057Z/`
- P25-03 — `docs/demo/integrated-timing-findings.md` — 逐段 budget/实测/裕度 + 关键发现
- P25-04 — closure + GATE-P25-CLOSURE self-signed (v4.0 七点自审)

**关键发现：** MiniMax cloud 2/2 runs **超 wow_a 段 15s budget（实测 18.4s / 29.0s）**；Ollama 7B local 2/2 runs **达标（实测 8.9s / 10.1s，裕度 5+s）**。这攻击了 pitch_script.md 段 4 "本地是 fallback" 的隐含措辞——数据表明**本地其实更快**。给 Kogami 三个选项（改后端主次 / 维持现状靠临场 buffer / 预生成缓存）；P25 不自行改 P22 冻结基线。

**Exit Criteria:**
- 主 pytest 658/1skip 零回归 · e2e 49/49 · adversarial 8/8
- 双后端真跑 artefact 入库 + findings 落盘
- GATE-P25-CLOSURE self-signed under v4.0 + 控制塔 DECISION + Notion 02B

**Plans:** P25-00 Tier 1 + P25-01…04 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #1 新 Phase 收口）

## Phase P26: 立项物料引用有效性自动验证 — pitch_script / faq / preflight / runbook 的证据路径可证伪化

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode

**Goal:** 让 9 份立项物料（pitch_script / faq / preflight_checklist / disaster_runbook / local_model_poc / wow_a/b/c 场景卡 / integrated-timing-findings）里每一条代码路径 / artefact / 配置文件引用都进 pytest default lane 机器验证，避免 refactor 静默打断 evidence 链。

**Sub-phases delivered:**
- P26-01 — `tests/test_pitch_citations.py`（PITCH_DOCS × 9 文件 × CITATION_RE 正则提取 + placeholder skip 双层护栏 + ≥50 citation 回归下限）
- P26-02 — 首轮真跑 GREEN：100% citation 在 repo 内可解析，无 audit doc 需要
- P26-03 — closure + GATE-P26-CLOSURE self-signed (v4.0 七点自审)

**关键数据：** 4 个测试进 default lane（pytest 658 → 662）；citation 提取器一次通过真跑验证；零 broken 引用。

**Exit Criteria:**
- 主 pytest 662/1skip 零回归 · e2e 49/49 · adversarial 8/8
- citation verifier 进 default lane（非 opt-in）
- GATE-P26-CLOSURE self-signed under v4.0 + 控制塔 DECISION + Notion 02B

**Plans:** P26-00 Tier 1 + P26-01…03 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #2 新 Phase 收口）

## Phase P27: Backend Switch Drill — 真实 pkill+spawn+wait_ready 切换延迟的可证伪化

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode · **触达 v4.0 ≥3 Phase 深度验收建议阈值**

**Goal:** 闭合 P25 findings §1.3 留下的悬案——真实机械切换延迟从未被测，"5–8s" 是直觉估计不是数据。P27 测实、写 findings、不改 disaster_runbook。

**Sub-phases delivered:**
- P27-01 — `scripts/backend_switch_drill.py`（独立端口 8797 + spawn/kill 计时 + atexit 僵尸清理 + prereq 预检 + 预算分档 GREEN/YELLOW/ALERT）
- P27-02 — 双方向 × N=2 真跑 artefact 入库 `runs/backend_switch_drill_20260418T134550Z/`
- P27-03 — `docs/demo/backend-switch-drill-findings.md` + closure + GATE self-sign (v4.0 七点自审)

**关键数据：** MiniMax→Ollama p50=**108ms**；Ollama→MiniMax p50=**107ms**。P25 "5–8s" 直觉估计偏保守约 50–75 倍。**但有诚实边界：** 本 drill 只测 HTTP+truth-engine 层机械切换，不覆盖首次 post-switch LLM 调用（adapter 初始化 + Ollama 冷模型加载 5–10s）。P25 段 4 预算 20s 早已覆盖了真冷启代价。

**Exit Criteria:**
- 主 pytest 662/1skip 零回归 · e2e 49/49 · adversarial 8/8
- 双方向 N=2 真跑 artefact + findings 落盘
- GATE-P27-CLOSURE self-signed under v4.0 + **主动贴深度验收建议到控制塔**（≥3 Phase 阈值触达）

**Plans:** P27-00 Tier 1 + P27-01…03 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #3 新 Phase 收口——达深度验收建议阈值，Executor 收口后主动暂停等 Kogami 过目）

## Phase P28: FAQ Evidence Cross-Check — 结构化符号证据交叉验证

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode (Kogami 已显式续签越过 ≥3 阈值)

**Goal:** 把 P26 的 "路径存在" 守护升级为 "符号存在" 守护。FAQ 里形如 "_BACKENDS dict / VALID_ACTION_TYPES whitelist / LLMClient Protocol" 的结构性 claim，refactor 重命名会让 pitch 当天甲方问答链瞬间崩。P28 hand-curate 12 个 load-bearing claim 进 pytest default lane。

**Sub-phases delivered:**
- P28-01 — `tests/test_pitch_symbols.py`（12 claim 映射表 + 4 测试：meta-check + symbol resolve + anthropic-absent + registry hygiene）
- P28-02 — 首轮真跑 12/12 PASS；意外发现 3 处文档 cite 不存在的 `requirements.txt` → `docs/demo/pitch-citations-audit.md` 归档
- P28-03 — closure + ROADMAP + GATE-P28-CLOSURE self-sign (v4.0 七点自审)

**关键产出：** 12 个符号级 claim 当前与代码一致；发现 3 处 citation drift (faq.md L126, onboarding/README.md L53, co-development/security-review-template.md L30) 都把 `pyproject.toml` 误 cite 成 `requirements.txt`。pitch 日风险评级低（Q9 实质 claim 正确），但建议 Kogami 批示一行字符串替换 hotfix。

**Exit Criteria:**
- 主 pytest 666/1skip 零回归（662→666，P28 新增 4 测试）· e2e 49/49 · adversarial 8/8
- 符号验证器进 default lane
- audit doc 落盘但不自改 pitch 物料（non-goal 守）
- GATE-P28-CLOSURE self-signed under v4.0

**Plans:** P28-00 Tier 1 + P28-01…03 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #4 新 Phase 收口）

## Phase P29: Pre-Pitch Readiness Scorecard — 6 维度 drill artefact 聚合成 T-0 一眼 GREEN/YELLOW/RED

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode

**Goal:** P25/P27/P28 加了三层机器化守护，加上既有的 dress_rehearsal / local_model_smoke / demo_rehearsal，pitch 前 Kogami 要看状态得去 7 个地方捞 artefact。P29 写一个聚合脚本，读 `runs/` 下每类最新 artefact，渲染成一张 markdown 表格，退出码 0/1/2 映射 GREEN/YELLOW/RED。**只聚合不重跑**——各 drill 自己跑几十秒到几分钟，T-0 前 Kogami 没时间全跑。

**Sub-phases:**
- P29-01 — `scripts/pitch_readiness.py`（6 drill reader + age 校验 + markdown 渲染 + 退出码 0/1/2）
- P29-02 — `docs/demo/pre-pitch-readiness-report.md` 首轮样例归档（Kogami 下次跑可以 diff 比对）
- P29-03 — closure + ROADMAP + GATE-P29-CLOSURE self-sign (v4.0 七点自审)

**关键产出：** 首轮真跑 overall YELLOW（MiniMax wow_a 因果链段超 budget，P25 findings §1.1 已记录的真实状态，非 regression）；其余 5 维度 GREEN。样例归档供 Kogami 日后 diff 用；scorecard 底部明示 pytest / adversarial / UI / network 四项**不在本 scorecard 覆盖范围**，避免误判。

**Exit Criteria:**
- 主 pytest 666/1skip 零回归 · e2e 49/49 · adversarial 8/8 · 聚合脚本无副作用（纯读 runs/）
- 脚本默认 `--stale-hours 24` 超期 GREEN 降 YELLOW
- RED 只用于 "no artefact at all"（有 artefact 但 fail 归 YELLOW 提醒 investigate，不是 RED）
- GATE-P29-CLOSURE self-signed under v4.0

**Plans:** P29-00 Tier 1 + P29-01…03 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #5 新 Phase 收口 — 深度验收建议阈值已持续续签）

## Phase P30: Scorecard 语义与 findings §5.1 决策对齐 — integrated_timing 两 backend 合并为 best-of-2

Status: Done (2026-04-18) · self-signed under v4.0 Extended Autonomy Mode

**Goal:** P29 scorecard 首轮 overall YELLOW 的根因是 MiniMax wow_a 超 budget（findings §1.1/§5.1 已充分记录的物理现实），但 findings §5.1 明确推荐"pitch 日用 Ollama 主路径"。scorecard 把两个 backend 并列独立判定导致 Kogami T-0 看到 YELLOW 会误以为"系统坏了"，而实际上只要选 Ollama 就 GREEN。P30 改 scorecard 聚合语义：把 ollama + minimax 两行合并为一行 `Integrated Timing (best-of-2 backends)`，取更 green 的作 verdict，detail 显式注明 losing backend 的 verdict + 引用 findings §5.1。

**Sub-phases:**
- P30-01 — `scripts/pitch_readiness.py` 加 `_merge_best_of_integrated_timing` 聚合逻辑（GREEN > YELLOW > RED > UNKNOWN 偏序；winner 取 age，detail 保留 losing backend 真相）
- P30-02 — 重跑 scorecard 验证 overall YELLOW→GREEN；更新 `docs/demo/pre-pitch-readiness-report.md` 首轮样例为 best-of-2 视图
- P30-03 — closure + ROADMAP + GATE-P30-CLOSURE self-sign (v4.0 七点自审)

**关键产出：** scorecard 从 6 行减至 5 行；overall YELLOW→GREEN（反映 pitch 日 Ollama 主路径的实际业务方针）；MiniMax YELLOW 真相**不被抹去**——在 detail 列显式保留 + findings §5.1 引用。Non-goals 全守：`integrated_timing_rehearsal.py` budget 常量零触碰 / findings doc 零触碰 / pitch 物料零触碰。

**Exit Criteria:**
- best-of-2 聚合正确：Ollama GREEN + MiniMax YELLOW → 合并行 GREEN，且 MiniMax YELLOW 可追溯
- overall verdict YELLOW → GREEN（但两者都坏时取**更差**的，避免乐观偏置）
- 样例 doc 更新 · pytest 666/1skip 零回归 · e2e 49/49 · adversarial 8/8
- GATE-P30-CLOSURE self-signed under v4.0

**Plans:** P30-00 Tier 1 + P30-01…03 — Executor self-sign 全程（v4.0 Extended Autonomy Mode，窗口内 #6 新 Phase 收口）

## 联邦架构战略（Opus 4.6 裁决 2026-04-15）

**结论**：联邦模式是正确的方向，整合≠合并。

**三层联邦架构**：
- Layer 1：独立 Adapter 联邦（完全隔离，确定性）
- Layer 2：跨域关联登记表 `cross_domain_links.json`（人工确认，确定性）
- Layer 3：AI 解释层（概率性，跨域叙事，不改变 Canvas）

**整合三级门槛**：
- Level 0：共存（自动）
- Level 1：信号关联 + 人类工程师确认 + 工程依据
- Level 2：联合推理 + Opus 4.6 架构审查

**禁止**：AI 自动推断跨域关联 / 因"看起来相关"合并 adapter / adapter 间硬编码依赖

**当前代码无需改动**。已创建：
- `docs/architecture/federation-model.md`（联邦架构宪法级文档）
- `data/cross_domain_links.json`（空跨域关联登记表，含完整 schema）
- `docs/json_schema/control_system_spec_v1.schema.json` 新增 `external_dependencies` 字段（含 `externalDependencySpec`）

**解冻条件**（不变）：外部用户反馈 / 产品方向决策 / 新领域需求

## Phase P34: C919 E-TRAS adapter 接入 — 第 5 个真值适配器

Status: DECISION drafted · GATE-P34-CLOSURE Pending (Kogami)

**Goal:** 按 Kogami 2026-04-20 二次方向指令 + `GATE-P34-PLAN: Approved`（Q1-A/Q2-A/Q3-A），将 20260417 C919 反推控制逻辑需求 PDF（10 页 / 1013 KB / SHA256 `dbe3f76b…31da5`）逐页落成第 5 条真实 adapter 链路。严格对齐每一个信号 / 逻辑门 / 时间参数 / Step，未引入任何 adapter 模板脚手架抽象（保留到 ≥6 条真实链路后再谈）。P33 adapter-scaffolding 与 P33 federation-level1 均被本 Phase supersede。

**交付物：**
- Hardware YAML：`config/hardware/c919_etras_hardware_v1.yaml`（325 行，5 段：sensor / logic_thresholds / physical_limits / timing / valid_outcomes）
- Adapter：`src/well_harness/adapters/c919_etras_adapter.py`（1444 行，17 组件 / 5 逻辑节点 / 4 acceptance / 5 fault mode）
- Intake packet：`src/well_harness/adapters/c919_etras_intake_packet.py`（100 行）+ `__init__.py` 注册 +6
- Tests：`tests/test_c919_etras_adapter.py`（712 行，63 tests，13 测试类）
- Traceability：`docs/c919_etras/traceability_matrix.md`（153 行，5 表 + Appendix A）
- Plan：`.planning/phases/P34-c919-etras-adapter/P34-00-PLAN.md`
- Closure：`.planning/phases/P34-c919-etras-adapter/P34-05-CLOSURE.md`

**三轨回归（vs P32 head dd915e1）：**
- default pytest 747 passed / 1 skipped / 49 deselected（+63 新增，零既有回归）
- opt-in e2e 49 passed（identical）
- adversarial 8/8（identical）

**Q1/Q2/Q3 Kogami 仲裁：**
- Q1-A · Max N1k Deploy Limit = 84.0%（mid-band of PDF §1.1.3 ⑤ 79-89%），支持 per-snapshot override
- Q2-A · MLG_WOW 冗余 disagree / both-invalid → conservative FALSE（两种边界都视为 in-flight）
- Q3-A · Max N1k Stow Limit = 30.0%（PDF §Step7 未印，保守占位）

三处仲裁均在 traceability matrix Appendix A 登记 TRCU sign-off TODO。

**Exit Criteria:**
- DECISION drafted（本 ROADMAP 行 + Notion 控制塔页 `33cc68942bed8136b5c9f9ba5b4b44ec` append block）✅
- Commit 分支 `codex/p34-c919-etras` @ `19282ba` pushed to origin · 不 FF 到 main 直至 Gate 批
- GATE-P34-CLOSURE 由 Kogami 显式签字（v5.2 R2 红线：Executor 不自签）
- 签字后：FF merge 到 origin/main · Notion DECISION "Pending" → "Approved (Kogami YYYY-MM-DD)"

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 closure §v5.2 checklist）。

**Plans:** P34-00 Tier 1（5 条 counterargument + Q1-A/Q2-A/Q3-A 已裁）+ P34-01…04 顺序执行全绿 + P34-05 closure drafted 等签。

## Phase P35: Adapter Truth-Level Registry + Demonstrative Adapters Freeze Banner (证迹补完第二轮 α 段)

Status: Executed & Green · Awaiting `GATE-P35-CLOSURE: Approved` (Kogami)

**Goal:** 按 Kogami 2026-04-20 方向 D · 证迹补完第二轮 + 披露「bleed_air / efds / landing_gear 3 adapter 是我之前尝试随便生成的逻辑面板，没有需求文档，当作没来源冻结搁置即可」，P35α 做纯文档层证迹固化：truth-level 登记表 + 3 adapter 的 7 文件 FROZEN banner + 防回归测试。零代码行为改动，零阈值改动，零既有测试断言改动。

**Sub-phases & commits (branch `codex/p35-adapter-truth-level-registry`, base `main c88e4f0`):**
- P35-00 (`c886e14`): Tier 1 plan (315 行 · 5 counterargument C1-C5 · Q1-Q5 Open Questions)
- P35-01 (`5a7e7b1`): `docs/provenance/adapter_truth_levels.md` 新增（5 行 · schema C 本质+状态分离）
- P35-02 (`6cc0d31`): 7 文件 FROZEN banner 落地（3 adapter + 2 intake + 2 yaml）
- P35-03 (`e0f8a8a`): `tests/test_adapter_freeze_banner.py` 15 parametrized cases

**Q1-Q5 Kogami 2026-04-20 仲裁：**
- Q1 = C · truth_level enum (`demonstrative/certified/placeholder`) + 独立 `status` 字段（本质状态分离）
- Q2 = A · banner 在 module docstring + YAML head comment
- Q3 = B · efds 不补 stub intake/yaml（冻结即不新增）
- Q4 = A · thrust_reverser 登记为 `demonstrative + Upgrade pending`（P36β 升级）
- Q5 = A · 接受 banner 文字逐字稿

**三轨回归（vs P34 head c88e4f0）：**
- default pytest: **762 passed** / 1 skipped / 49 deselected（P34 baseline 747 + P35-03 新增 15 = 762 · 零既有回归）
- opt-in e2e: **49 passed**（identical to P34 baseline）
- adversarial wrapper: **1 passed**（8/8 inside identical）

**Exit Criteria (all met):**
- `docs/provenance/adapter_truth_levels.md` 含 5 行 + schema 说明 ✅
- 7 文件 banner 落地，文字与 Q5=A 草案字节级一致 ✅
- `tests/test_adapter_freeze_banner.py` 15 passed ✅
- 三轨全绿，零既有回归 ✅
- ROADMAP / STATE 更新（本段）✅
- Closure doc 起草（`.planning/phases/P35-adapter-truth-level-registry/P35-05-CLOSURE.md`）✅

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 P35-05-CLOSURE.md §v5.2 checklist）。

**Plans:** P35-00 Tier 1（5 counterargument · Q1-Q5 Kogami 仲裁）+ P35-01…03 顺序 commit 全绿 + P35-04 三轨 zero regression + P35-05 closure drafted 等签。

**Next phase:** P36β (thrust_reverser docx 真实化) — 等 Kogami 在 P35 closeout 后明示推进。

## Phase P36β: thrust-reverser docx 真实化 — demonstrative → certified 升级（证迹补完第二轮 β 段）

Status: Executed & Green · Awaiting `GATE-P36β-CLOSURE: Approved` (Kogami)

**Goal:** 按 Kogami 2026-04-20 "Go P36β" 指令 + D1=A 精益 / D2=C 混合 / D3=Kogami 自裁 / D4=只登记 + Q1-Q5 全部由 Executor 推荐决定 + `GATE-P36β-PLAN: Approved`，把 `Downloads/控制逻辑(1).docx` 入库为 `uploads/20260409-thrust-reverser-control-logic.docx` 建立 thrust_reverser 的追溯链路，升级 P35 registry row 1 从 `demonstrative + Upgrade pending` → `certified + In use`。零代码行为改动，零阈值/YAML value 改动，零既有测试断言改动。

**Sub-phases & commits (branch `codex/p36-thrust-reverser-docx-backfill`, base `main aabc548`):**
- P36β-00 (`a078b6c`): Tier 1 plan (383 行 · 5 counterargument · Q1-Q5 Open Questions)
- P36β-01 (`b43ac2e`): docx 入库 `uploads/20260409-thrust-reverser-control-logic.docx` (SHA256 `6e457fe3…276133a5` · 230,930 bytes · 57 段 · 2 表 · 1 EMF 图)
- P36β-02 (`bcdf91b`): `src/well_harness/adapters/thrust_reverser_intake_packet.py` 120 行精益版（3 SourceDocumentRef · no workbench spec per D1=A）
- P36β-03 (`0be39c6`): `config/hardware/thrust_reverser_hardware_v1.yaml` 头 24 行 docx § 引用块（parameters 字节级不变）
- P36β-04 (`8198e1c`): `docs/thrust_reverser/traceability_matrix.md` 241 行（5 表 + Appendix A 6 open assumptions）
- P36β-05 closure drafted (registry row 1 in-place 升级 + 本段 + STATE + closure doc + Notion DECISION Pending)

**Q1-Q5 Executor 推荐 · Kogami 2026-04-20 全部批：**
- Q1=A · SW2 ±5.0/-9.8° Executor 假设镜像 SW1 → Appendix A.1
- Q2=B · Deploy 90% VDT 行业默认 → Appendix A.2（Kogami 后补实际来源）
- Q3=A · TLS/PLS 解锁延迟 0.3/0.2s Kogami 待仲裁 → Appendix A.3
- Q4=A · Deploy rate 30%/s Kogami 待仲裁 → Appendix A.4
- Q5=A · docx authority = Kogami 自裁（具体签准方 Appendix A.6 待 sign-off）

**三轨回归（vs P35 head aabc548）：**
- default pytest: **762 passed** / 1 skipped / 49 deselected in 95.66s （identical，零 delta —— 符合 P36β 无测试改动的设计）
- opt-in e2e: **49 passed** / 763 deselected in 2.89s (identical)
- adversarial wrapper: **1 passed** in 0.27s (8/8 inside identical)

**关键不变量（自审确认）：**
- `src/well_harness/controller.py` 字节级不变
- `src/well_harness/models.py` 字节级不变
- `config/hardware/thrust_reverser_hardware_v1.yaml` 的 `parameters:` 段字节级不变（仅头注释 +24 行）
- 既有测试断言字节级不变

**Exit Criteria (all met):**
- `uploads/20260409-thrust-reverser-control-logic.docx` 入库 · SHA256 记录 ≥ 5 位置（commit msg / intake notes / YAML head / matrix / registry notes）✅
- `src/well_harness/adapters/thrust_reverser_intake_packet.py` 120 行精益版 ✅
- `config/hardware/thrust_reverser_hardware_v1.yaml` 头 +24 行 docx § 引用 ✅
- `docs/thrust_reverser/traceability_matrix.md` 241 行（5 表 + Appendix A 6 项）✅
- `docs/provenance/adapter_truth_levels.md` row 1 升级 `demonstrative`→`certified` ✅
- 三轨全绿零 delta ✅
- ROADMAP / STATE 更新（本段）✅
- Closure doc 起草 · 等 `GATE-P36β-CLOSURE: Approved`

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 P36β-05-CLOSURE.md §v5.2 checklist）。

**Registry row 1 升级：** 

```
(P35α 版 2026-04-20) thrust-reverser | demonstrative | Upgrade pending | Downloads/控制逻辑(1).docx（拟入库）| ...
(P36β 升级 2026-04-20) thrust-reverser | certified | In use | uploads/20260409-thrust-reverser-control-logic.docx | Kogami 自裁（Appendix A.6 待 sign-off）| ...
```

**Plans:** P36β-00 Tier 1（5 counterargument · Q1-Q5 仲裁）+ P36β-01…04 顺序 commit + P36β 三轨零 delta + P36β-05 closure drafted 等签。

**Next phase:** 留给 Kogami 明示（候选：P37 thrust-reverser workbench spec · 或 P38 CI-level provenance hash enforcement · 或其他方向）— R4 不自选。

## Phase P37: thrust-reverser 反向需求增补（code-to-spec backfill · 证迹补完第二轮 γ 段）

Status: Executed & Green · Awaiting `GATE-P37-CLOSURE: Approved` (Kogami)

**Goal:** 按 Kogami 2026-04-20 "按优先级顺序，逐步深度修复" + thrust-reverser 特殊指令 "以 controller.py 为准，更新补充需求文档，然后存档"，P37 生成反向权威 spec supplement（markdown），把 P36β 遗留的 Appendix A 6 项 open assumption 全部 resolved 到 Kogami 内部自签的 supplement 各 § 段。controller.py + models.py 继续为真值基准；原 docx 保留作 2026-04-09 历史 snapshot。

**Sub-phases & commits (branch `codex/p37-thrust-reverser-requirements-supplement`, base `main 96bacaf`):**
- P37-00 (`ce5adfc`): Tier 1 plan (319 行 · 4 counterargument · Q1-Q2 已预签)
- P37-01 (`0ba643c`): `docs/thrust_reverser/requirements_supplement.md` 297 行（8 段 · 覆盖 A.1-A.6）
- P37-02 (`2bc1eeb`): 4 anchor 联动更新（matrix Appendix A 6 项 ⚠️→✅ + intake 加第 4 SourceDocumentRef + YAML 头 supplement block + registry row 1 notes 升级）
- P37-05 closure drafted (本段 + STATE + closure doc + Notion DECISION Pending)

**Q1-Q2 Kogami 2026-04-20 仲裁（GATE-P37-PLAN: Approved）：**
- Q1 = A · supplement 格式 Markdown
- Q2 = A · A.6 docx authority 一并解决（supplement §7 明示 Kogami 内部自签 · 非外部权威）

**三轨回归（vs P36β head 96bacaf）：**
- default pytest: **762 passed** / 1 skipped / 49 deselected in 91.27s（identical · 零 delta）
- opt-in e2e: **49 passed** / 763 deselected in 2.72s (identical)
- adversarial wrapper: **1 passed** in 0.26s (8/8 inside identical)

**Appendix A 6 项全部 resolved：**
- A.1 SW2 ±5.0°/-9.8° → supplement §2 · mirroring SW1 pattern
- A.2 Deploy 90% VDT → supplement §3 · 行业默认
- A.3 TLS/PLS 延迟 0.3/0.2s → supplement §4 · simulation baseline
- A.4 Deploy rate 30%/s → supplement §5 · simplified-plant baseline
- A.5 故障模式 → supplement §6 · 维持 docx §58 "不考虑" + 未来挂钩
- A.6 docx authority → supplement §7 · Kogami 内部自签 · 非外部权威 · 升级路径明示

**Authority 定位明示（supplement §7）：**
- Supplement authority = Kogami 内部自签（非甲方 / 非监管 / 非行业标准）
- Well Harness scope = 项目内部控制逻辑验证平台（非取证交付）
- 若未来需外部 certification-grade authority 需新 Phase 升级 · §7.3 列升级路径

**Registry row 1 升级（P36β → P37）：**
- upstream_source: 加 supplement 路径
- authority: "Kogami 自裁（docx 签准方待明）" → "Kogami 内部自签（明示非外部权威）"
- notes: "6 Appendix A open assumptions pending" → "Appendix A 6 项全部 resolved via P37 supplement"

**关键不变量（字节级确认）：**
- `src/well_harness/controller.py` 字节级不变（DeployController class）
- `src/well_harness/models.py` 字节级不变（HarnessConfig dataclass）
- `config/hardware/thrust_reverser_hardware_v1.yaml` `parameters:` 段字节级不变（仅头注释扩展）
- 既有测试断言字节级不变
- 原 docx `uploads/20260409-...` 冻结不动
- 其他 4 adapter（bleed/efds/lg/c919）所有文件不变

**Exit Criteria (all met):**
- `docs/thrust_reverser/requirements_supplement.md` 297 行 · 8 段 · A.1-A.6 全覆盖 ✅
- `docs/thrust_reverser/traceability_matrix.md` Appendix A 6 项 ⚠️→✅ + 表 5 引用更新 ✅
- `src/well_harness/adapters/thrust_reverser_intake_packet.py` 4 SourceDocumentRef · D1=A 精益保留 ✅
- `config/hardware/thrust_reverser_hardware_v1.yaml` 头部 supplement block + `parameters:` 字节级不变 ✅
- `docs/provenance/adapter_truth_levels.md` row 1 升级 · 其他 4 行不变 ✅
- 三轨全绿零 delta ✅
- ROADMAP + STATE 更新（本段）✅
- Closure doc 起草 · 等 `GATE-P37-CLOSURE: Approved`

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 P37-05-CLOSURE.md §v5.2 checklist）。

**Plans:** P37-00 Tier 1（4 counterargument · Q1-Q2 仲裁）+ P37-01 supplement + P37-02 4 anchor 联动 + P37-03 三轨零 delta + P37-05 closure drafted 等签。

**Next phase (按 P0-P4 优先级队列)：** 留给 Kogami 明示 —— 候选 P38 P34 PDF 回填 · P39 c919 Appendix A 3 项 sign-off · P40 CI SHA enforcement · 或其他 · R4 不自选。

## Phase P38: c919-etras 证迹完整闭环（PDF 入库 + TRCU sign-off 落地）

Status: Executed & Green · Awaiting `GATE-P38-CLOSURE: Approved` (Kogami)

**Goal:** 按 Kogami 2026-04-20 三条并发指令 (PDF 路径 + "明示 TRCU 团队 sign-off" + "继续推进")，合并原 P38 (PDF 回填) + P39 (c919 Appendix A 3 项 sign-off) 为一个 Phase，按 P37 对称模式完成 c919-etras 证迹闭环。**零代码 · 零阈值 · 零 YAML value · 零 test 改动。**

**Sub-phases & commits (branch `codex/p38-c919-etras-provenance-closure`, base `main db03294`):**
- P38-00 (`402db31`): Tier 1 plan (295 行 · 4 counter · Q1/Q2)
- P38-01 (`528aa0d`): `uploads/20260417-C919反推控制逻辑需求文档.pdf` 入库（989 KB · SHA `dbe3f76b…276133a5` · 匹配 P34 记录）
- P38-02 (`8c7fd70`): 4 anchor 联动（YAML head SHA 固化 · matrix Appendix A 3 项 resolved · registry row 5 更新 · intake notes 扩展）
- P38-05 closure drafted（本段 + STATE + closure doc + Notion DECISION Pending）

**Q1/Q2 Kogami 2026-04-20 仲裁（GATE-P38-PLAN: Approved）：**
- Q1 = C · authority 字段维持 "甲方 (TRCU 团队)" · notes 透明记载 Kogami 代 TRCU 明示
- Q2 = A · YAML head 加 SHA256 固化字段（第 4 位置 SHA 副本）

**三轨回归（vs P37 head db03294）：**
- default pytest: **762 passed** / 1 skipped / 49 deselected in 98.93s（identical · 零 delta）
- opt-in e2e: **49 passed** / 763 deselected in 2.60s (identical)
- adversarial wrapper: **1 passed** in 0.26s (8/8 inside identical)

**c919 Appendix A 3 项全部 resolved：**
- A.Q1 Max N1k Deploy Limit 84.0% → Kogami 代 TRCU 明示接纳
- A.Q2 MLG_WOW conservative-FALSE → Kogami 代 TRCU 明示接纳
- A.Q3 Max N1k Stow Limit 30.0% → Kogami 代 TRCU 明示接纳

**PDF 入库事实：**
- Path: `uploads/20260417-C919反推控制逻辑需求文档.pdf`
- SHA256 `dbe3f76b…276133a5` · 完全匹配 P34 cowork 记录
- 5 位置 SHA 副本（intake notes / YAML head 新加 / matrix / registry notes / closure 引用）

**与 P37 thrust-reverser 对称：** 两条 certified 链路今日证迹全部整齐闭环（thrust-reverser 6 项 supplement resolved · c919-etras 3 项 TRCU sign-off resolved）。

**关键不变量（字节级确认）：**
- `src/well_harness/adapters/c919_etras_adapter.py` (1444 LOC) 字节级不变
- `config/hardware/c919_etras_hardware_v1.yaml` `parameters:` 段字节级不变（仅头部 +9 行 SHA/Size/Authority/Phase 字段扩展）
- `tests/test_c919_etras_adapter.py` (712 LOC · 63 tests) 字节级不变
- thrust-reverser / bleed_air / efds / landing_gear 任何文件不变

**Exit Criteria (all met):**
- PDF 入库 uploads/ · SHA 匹配 ✅
- YAML head SHA 固化 ✅
- Matrix Appendix A 3 项 resolved ✅
- Registry row 5 notes + authority 字段更新（其他 4 行字节级不变）✅
- Intake PDF SourceDocumentRef notes 扩展 ✅
- 三轨零 delta ✅
- ROADMAP + STATE 更新 ✅
- Closure doc 起草 · 等 `GATE-P38-CLOSURE: Approved`

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 P38-05-CLOSURE.md §v5.2 checklist）。

**Plans:** P38-00 Tier 1 + P38-01..04 顺序执行全绿 + P38-05 closure drafted 等签。

**Next phase:** 按 P0-P4 优先级 · Kogami 明示 —— 候选 P40 CI SHA enforcement · P41 workbench spec · P42 runtime truth_level API · 其他 · R4 不自选。

## Phase P40: CI-level SHA enforcement — 自动校验 uploads/ provenance hash

Status: Executed & Green · Awaiting `GATE-P40-CLOSURE: Approved` (Kogami)

**Goal:** 按 Kogami 2026-04-20 "继续推进" + 选 P40 作下一方向 + "Q1-Q3 由你推荐决定" 授权 + `GATE-P40-PLAN: Approved`，建立自动 SHA 校验基础设施，闭合 P34/P36β/P37/P38 counterargument 反复提到的 "SHA 副本靠人工维护 · CI 无校验 · tamper 未必发现" 风险（C2/C3 类）。

**Sub-phases & commits (branch `codex/p40-ci-sha-enforcement`, base `main 74a459a`):**
- P40-00 (`9a589bb`): Tier 1 plan (379 行 · 4 counter C1-C4 · Q1-Q3 Executor 预签)
- P40-01 (`ee72271`): `docs/provenance/sha_registry.yaml` SoT · 2 files 初始条目 (46 行)
- P40-02 (`12f7b94`): `scripts/verify_provenance_hashes.py` (195 行 · stream-hash · --strict 模式 · exit 1 on drift)
- P40-03 (`bf60eb8`): `tests/test_provenance_sha_integrity.py` (96 行 · 3 tests · default lane)
- P40-05 closure drafted (本段 + STATE + closure doc + Notion DECISION Pending)

**Q1-Q3 Executor 预签 · Kogami 2026-04-20 授权：**
- Q1 = A · pytest default lane 集成（最简 · 与既有 762 test 体系一致）
- Q2 = A · YAML registry 格式（与 hardware config 格式一致）
- Q3 = A · 硬失败 exit 1（SHA mismatch 是 hard signal）

**三轨回归（vs P38 head 74a459a）：**
- default pytest: **765 passed** / 1 skipped / 49 deselected in 89.05s（P38 baseline 762 + 3 new P40-03 = 765 · 设计预期）
- opt-in e2e: **49 passed** (identical)
- adversarial wrapper: **1 passed** (8/8 inside identical)

**Registry 初始 2 条目：**
- `uploads/20260409-thrust-reverser-control-logic.docx` · SHA `6e457fe3…276133a5` · 230,930 bytes · P36β · Kogami 内部自签
- `uploads/20260417-C919反推控制逻辑需求文档.pdf` · SHA `dbe3f76b…276133a5` · 1,013,541 bytes · P38 · 甲方 (TRCU) 代明示

**Update protocol** (registry 头注释)：新增/替换/删除 uploads/* 必须同 Phase commit 更新 registry，不能静默覆写。

**关键不变量（字节级确认）：**
- 5 个真值链路 adapter / controller.py / models.py 字节级不变
- 既有 762 tests 断言字节级不变（+3 tests 是 P40 新增，不改旧 tests）
- `uploads/*` 任何文件内容不变
- 散布 SHA 文字 (matrix / supplement / registry notes / intake notes / YAML head) 不变（本 Phase 仅校验，不改源头）

**Exit Criteria (all met):**
- `docs/provenance/sha_registry.yaml` 46 行 · version 1 · 2 files ✅
- `scripts/verify_provenance_hashes.py` 195 行 · default + --strict 模式本地 exit 0 ✅
- `tests/test_provenance_sha_integrity.py` 96 行 · 3 tests 本地通过 ✅
- 三轨: default 765 (+3) / e2e 49 identical / adversarial 1 identical ✅
- ROADMAP + STATE 更新（本段）✅
- Closure doc 起草 · 等 `GATE-P40-CLOSURE: Approved`

**证迹合规：** v5.2 R1 R2 R3 R4 R5 全部 self-verified 合规（详见 P40-05-CLOSURE.md §v5.2 checklist）。

**Plans:** P40-00 Tier 1（4 counter · Q1-Q3 Executor 预签 Kogami 授权）+ P40-01..03 顺序 commit + P40-04 三轨 +3 设计预期 + P40-05 closure drafted 等签。

**Next phase:** 按 P1-P4 优先级 · Kogami 明示 —— 候选 P41 thrust-reverser workbench spec · P42 runtime truth_level API · P43 freeze/upgrade template · 或其他 · R4 不自选。**P0 队列全部 resolved**。

## 2026-04-20 全天 Phase 链总结

| Phase | 性质 | Gate | main commit |
|-------|------|------|-------------|
| P31 | re-land explain-runtime visibility + prewarm | ✅ | `25f64fe` |
| P32 | provenance backfill (v4.0 audit + Milestone 9 Lifted) | ✅ | `e6f9fe6` |
| P34 | C919 E-TRAS adapter (第 5 条真值链路) | ✅ | `c88e4f0` (merge) |
| P35α | Adapter truth-level registry + 3 demonstrative freeze banner | ✅ | `aabc548` (merge) |
| P36β | thrust-reverser docx 真实化 (demonstrative → certified 升级) | ✅ | `96bacaf` (merge) |
| P37 | thrust-reverser 反向需求增补 (code-to-spec backfill) | ✅ | `db03294` (merge) |
| P38 | c919-etras 证迹完整闭环 (PDF 入库 + TRCU sign-off) | ✅ | `74a459a` (merge) |
| P40 | CI-level SHA enforcement | Pending closure | - |

**证迹补完第二轮全套**（α/β/γ/δ/ε）完成 · 5 真值链路全部有 truth-level 登记 · 2 certified 链路 Appendix A 全部 resolved · CI 层自动防 tamper。

## Phase P41: thrust-reverser intake packet clarification (scope C · D1=A Lean discovery)

Status: Executed & Green · Awaiting `GATE-P41-CLOSURE: Approved`

**Goal:** P41 起草时发现 `src/well_harness/system_spec.py:273::current_reference_workbench_spec()` 早已提供完整 thrust-reverser workbench spec（6 处 callers）。D1=A Lean 真实语义 = `thrust_reverser_intake_packet.py` intake layer 选择空 tuple，非 "无 spec"。Kogami 2026-04-20 "Go C" 选最简路径：仅 docs 澄清 + 最简 regression test。

**Sub-phases & commits (branch `codex/p41-thrust-reverser-intake-clarification`, base `main 8989268`):**
- P41-00 (`4c957fe`): Plan (136 行 · scope pivot discovery 时间线 · 3 counter)
- P41-01 (`cbbddcc`): supplement §1.4 Discovery 注 + §8 升级 3 方→4 方关系 + registry row 1 notes 精准化
- P41-02 (`4d94b4d`): `tests/test_thrust_reverser_intake_packet.py` 2 tests 防 D1=A Lean 回归
- P41-05 closure drafted

**三轨（vs P40 head 8989268）：**
- default pytest: **767 passed** (+2 P41-02 · P40 baseline 765) · e2e 49 identical · adversarial 1 identical

**代码侧 invariants（字节级）：** controller.py / models.py / current_reference_workbench_spec / thrust_reverser_intake_packet.py business fields / 其他 4 adapter / 既有 765 tests 断言 · 全部不变。

**P41 教训：** P36β 起草时未穷举 `ControlSystemWorkbenchSpec` 工厂函数 · 导致 "no workbench spec" 口径 5 Phase 连锁 drift。未来 Phase 起草前应加 **"spec factory grep"** 前置步骤。

**Next phase:** P42 · truth_level 进 ControllerTruthMetadata schema + runtime API（Kogami "连续 3 Phase" 指令第 2 位）

## Phase P43: Control Logic Workbench end-to-end milestone

Status: **Plan v7 GATE-P43-PLAN Approved** (Kogami 2026-04-20) · **P43-01 Contract Proof Spike CLOSED** · **GATE-P43-01-CLOSURE Approved** (Kogami 2026-04-21) · **P43-02 Batch plan v3.1 submitted · awaiting GATE-P43-02-BATCH-PLAN-QUALITY** (Kogami plan-quality 前置门 · 2026-04-21 · Codex r4 `可过-Gate` @ `987d723` · 8-entry §3d delta bundled)

### P43-02 Batch Sub-phase: Orchestrator + Document Pipeline + Freeze Gate (plan v3.1 submitted · awaiting plan-quality gate)

**Branch**: `codex/p43-02-orchestrator-extend` (not merged · execution unblocked by Gate approval)
**Plan artifact**: `.planning/phases/P43-control-logic-workbench/P43-02-00-PLAN.md` v3.1 @ HEAD `987d723`
**Gate ID (this submission)**: `GATE-P43-02-BATCH-PLAN-QUALITY` (plan-quality 前置门 · pre-execution)
**Execution gate (future · post-implementation)**: `GATE-P43-02-BATCH-CLOSURE`
**Codex Q7=A arc**: r1 强 → r2 强 → r3 弱 → r4 弱 → **r4 final `可过-Gate`** (5 plan revisions: v1→v2→v3→v3.1→v3.1 final-scrub)
**Submission package**: see plan §10 (Codex arc · 8-entry §3d delta · Q-lock compliance · Kogami options A/B/C)

**8-entry §3d whitelist delta bundled** (Q1=A · formal package · per plan §10.2):
1. `tests/test_p43_document_pipeline.py` (Test Whitelist)
2. `tests/test_p43_clarification_stable_ids.py` (Test Whitelist · Bug D semantic category binding · 6 regression cases)
3. `tests/test_p43_freeze_gate.py` (Test Whitelist)
4. `tests/test_p43_dual_sha_manifest.py` (Test Whitelist · Q12=B+a null-tolerant 4-组合)
5. `tests/fixtures/p43_document_pipeline/` (PDF/DOCX/TXT/MD corpus)
6. `tests/fixtures/p43_pre_archive/` (backward-compat)
7. `pyproject.toml` → `[project.optional-dependencies] document = ["pypdf>=4.0", "python-docx>=1.0"]` (Source Code Whitelist new row · repo-root packaging metadata)
8. `docs/<system>/traceability_matrix.md` per-system freeze-time SKELETON emission (Doc Deliverables Whitelist new row · aligned with P43-00 §2c:190 P34-P42 precedent)

**Awaiting Kogami decision**: A (approve all 8 + Gate · **Executor recommendation**) / B (approve Gate + partial subset · triggers v3.2 re-plan for rejected entries) / C (reject Gate · Batch-2 hard-frozen · R4 arbitration).

**Scope digest**: 3 sub-phases combined (P43-02 + P43-03 + P43-04) · ~2100-2700 LOC · 3-4 days wall-time · 13 Codex adapter-boundary review rounds planned for execution · 16 authority tests (14 R1-R6 + 2 observability) + ~30 other ≈ ~46 new default-lane tests · 8 endpoints total (P43-01's 7 + `/api/document/extract` · `/api/workbench/freeze` dropped as CLI-only).

**Commit arc (v1→v3.1 final-scrub)**:
- `03e4acf` v1 draft · Codex r1 需修正·信号强 (6 required + 2 polish)
- `1781641` v2 surgical rewrite · closes r1 · Codex r2 需修正·信号强 (3 required + 1 polish)
- `ee0d018` v3 surgical addendum · closes r2 (whitelist anchor / pyproject explicit / semantic category) · Codex r3 需修正·信号弱
- `ac30621` v3.1 janitorial · closes r3 (§2b heading / pyproject pre-emptive / Bug D 6 cases / §6 v2→v3 wording)
- `4aed5fd` v3.1 metadata scrub (r4 pass 1 · 7 version-drift sites closed)
- `987d723` v3.1 §6/§7 lifecycle scrub (r4 pass 2 · 5 lifecycle lines closed)
- `(this commit)` v3.1 §10 Kogami submission section + STATE.md + ROADMAP.md · **Codex r4 final `可过-Gate`** verdict stamped on `987d723`

---

### P43-01 Sub-phase: Contract Proof Spike (CLOSED)

**Gate approval**: GATE-P43-01-CLOSURE Approved by Kogami on 2026-04-21 on the basis of Codex Step G r4 `可过-Gate` verdict (commit `9a51183`). Plan §3 Step G item 4 authorizes P43-02 kickoff.

**Deliverable snapshot**:
- `src/well_harness/ai_doc_analyzer.py:840,843,866,867` — Bugs A/B1/B2 surgical fix (~5 LOC READ-side · Kogami Option X expansion at Step B)
- `tests/test_p43_doc_analyzer_blocker_fix.py` — 4 default-lane regression tests
- `tests/test_p43_readAsText_browser_behavior.py` — 1 opt-in e2e Playwright test
- `tests/fixtures/p43_spike/{real_pdf_happy_path, synthetic_blocker}/*` — 5 fixtures + 2 expected-response dumps + README
- `docs/P43-contract-proof-report.md` — plan-whitelisted gate summary
- `docs/P43-api-contract-lock.yaml` — 7 endpoints · 36 endpoint error branches + 6 global guards
- `.planning/phases/P43-control-logic-workbench/reports/p43-01-contract-proof/CONTRACT-PROOF-REPORT.md` — supporting detailed artifact

**Execution arc** (9 commits):
`48e4796` (Step A partial + Kogami escalation · 2 new Counter-F bugs B1/B2 beyond plan) → `5d2d3ec` (Step B Kogami Option X · Bugs A/B1/B2 fix + 4 regression tests) → `8d76cf5` (Codex Step B `可过-Gate` trailer) → `7fd243d` (Steps D/E/F · Playwright + API contract-lock + R6/R7/R8 inventory) → `4d40aee` (Step G finalize · executive summary + exit-criteria mechanical verification) → `6729768` (scrub r1 · 3 fixes) → `e86a8cc` (scrub r2 · 7 drift items) → `9a51183` (scrub r3 · 1 trigger-text fix) → `e579a16` (Step G closure · r4 trailer + Kogami submission).

**Counter F closure** (4 bugs · unified root cause — no internal contract lock between producer and consumer within `run_pipeline_from_intake()`'s own data path):
| Bug | Anchor | Fix |
|-----|--------|-----|
| A | `ai_doc_analyzer.py:840` · blocker guard READ/EMIT key mismatch | Step B surgical fix |
| B1 | `ai_doc_analyzer.py:866` · `bundle.playback_report.scenarios` (no attr) | Step B surgical fix |
| B2 | `ai_doc_analyzer.py:867` · `bundle.fault_diagnosis_report.fault_modes` (no attr) | Step B surgical fix |
| D | `ai_doc_analyzer.py:799` · `clarify-{i}` vs stable question_id | **Deferred to P43-03** per Q12=B+a |

**Three-lane regression** (re-run 2026-04-21): default 800 passed · e2e 50 passed · zero regression vs P42 baseline `a6521ca`.

**Codex Step G review arc** (4 rounds): r1 `需修正·信号弱` (3 fixes) → r2 `需修正·信号强` (7 drift items surfaced via deeper probing) → r3 `需修正·信号弱` (1 residual trigger text) → **r4 `可过-Gate`** on `9a51183` with endorsement: *"GATE-P43-01-CLOSURE: Commit 9a51183 closes the Step G contract-lock gap; /api/workbench/repair now truthfully documents apply_all_safe as a truthiness guard, the YAML remains valid and internally consistent, and no new drift was introduced."*

**Non-blocking residual polish** (logged for future slice · Codex r4 explicit): `src/well_harness/demo_server.py:2666` error message says "apply_all_safe must be true" but runtime guard is truthiness-based. Fix candidate for P43-02 or standalone cleanup.

### P43-01 plan phase (historical · plan v5 frozen)

- Branch `codex/p43-01-contract-proof-spike` merged to `main` (`45322e5`)
- 5 plan revisions v1→v5 · 5 Codex adversarial rounds (pre-execution)
- Codex plan-phase arc: r1 需阻止 (9-point audit · 4 fixes) → r2 需修正·信号强 (5 fixes) → r3 需修正·信号弱 ("不是大修") → r4 需修正·信号弱 ("一轮极小 scrub") → r5 not-可过-Gate ("治理叙事结构在炸 · 建议 Option B/C")
- Kogami R4 Option B (2026-04-21): freeze v5 · 3 governance-label residuals (GL-1/2/3) accepted as §7a Appendix A · Gate Approved
- Q lock: Q1=A+B+D · Q2=A · Q3=B · Q4=A · Q5=B
- Scope: 5 must-land (S1-S5) + 3 report-only (R6-R8) — all closed per execution arc above
- Governance lesson: Codex r5 root-cause "多源 label drift · single source of truth 缺失" · filed for future GSD plan template improvement

**Next**: P43-02 (workflow / orchestrator / panel) kickoff — consume `docs/P43-api-contract-lock.yaml` as authoritative endpoint contract.

**Goal:** Build a complete Control Logic Workbench enabling: 需求文档导入 → 解析+询问+确认闭环 → frozen spec → 控制逻辑面板渐进生成+连线 → 面板调试+标注修改 → 迭代优化 → 用户 Final Approval → archive. End-to-end user journey 10 steps.

**Path ① governance arc (extends P42 precedent · 6 Codex rounds):**

| Round | v | Codex verdict | Action |
|-------|---|---------------|--------|
| r1 | v1 (`81adf39`) | 需阻止（6 counters A-F · incl. 真 bug `blockers`/`blocking_reasons`）| Kogami 路径① → v2 |
| r2 | v2 (`aa8e03a`) | 需修正·信号强（4 cuts: state.yaml phantom · P43-01 hard-freeze · draft_design_state authority · §3d touched-forbidden）| path ① → v3 |
| r3 | v3 (`14131c4`) | 需修正·信号强（cuts #1/#2 closed） | path ① → v4 |
| r4 | v4 (`cf85723`) | 需修正·信号强（3 surgical · "不建议 R4 撤回") | path ① → v5 |
| r5 | v5 (`292a555`) | 需修正·信号强（3 precise · "值得 v6 最后一次") | **Kogami R4 Option A** → v6 |
| r6 | v6 (`6e46784`) | 需修正·信号强（3 residuals · "不建议 v7") | **Kogami R4 Option B + strengthen directive** → v7 |
| — | v7 (`a14dae8`) | **Kogami GATE-P43-PLAN Approved** | Q answers locked per Executor recs |

**Kogami R4 arbitrations (×3):**
- r5→v6: Option A (surgical 3-fix · Kogami-approved one more path ① cycle)
- r6→v7: Option B + strengthen-before-Gate directive (KL-1/2/3 promoted from accepted residuals into §3e mechanical)
- v7: Gate Approved · Q lock · next P43-01 spike

**Plan v7 structure:**
- §1 user journey 10 steps (Final Approved → demonstrative/Upgrade pending · 非 certified)
- §3a P43-01 Contract Proof Spike must land first (asserted happy path + failure path + contract lock · non-negotiable freeze if fails)
- §3c workflow automaton contract (17 state / 10+ event / transition table / error taxonomy / idempotency · non-goal state.yaml)
- §3d Source Code Whitelist 12 files with L1/L2/L3 ladder + Doc Deliverables Whitelist 6 files + Test Whitelist 7 files + Tooling+CI Whitelist 4 files + Blacklist
- §3e draft_design_state authority contract R1-R6 mechanical verification (CI/test patterns in default lane + opt-in e2e)
- §5 C1-C15 self-audit (C7-C15 verified-by codex-gpt54-xhigh)
- §7 sequencing: 4 gates (Q1=D batching)
- §8 18-item Exit Criteria
- §8a Codex r6 KL-1/2/3 closure governance record

**KL-1/2/3 mechanical closure (Kogami strengthen directive · v7):**

| KL | Attack point | v7 §3e mechanical guard |
|----|-------------|-----------------------|
| KL-1 · R1 helper scan | `demo_server.py` `build_*_response()` helpers not in handler body scan | `test_r1_helper_payload_builders_no_draft` + `test_r1_handler_call_closure` · AST call-graph closure within demo_server.py |
| KL-2 · R3 property mutation | `frozenSpec.foo = ...` / alias-mutate bypass | `assignFrozenSpec` MUST call `deepFreeze(newSpec)` recursive `Object.freeze()` · `test_r3_deepfreeze_enforced` static + `test_r3_runtime_mutation_blocked` opt-in |
| KL-3 · R5 validator behavior | Default lane only checks function exists + failure codes literal | Each fixture case MUST specify `required_substrings_in_validator_source` · Python assertIn static proof of 4 conflict logic paths + P43-09 Exit **MANDATORY** one-time Node parity run |

**Q answers locked (Kogami 2026-04-20):**
- Q1 = D (4 gates: P43-01 + 3 batches)
- Q2 = A (workbench.js vanilla JS)
- Q4 = A (user alias + comment approval)
- Q7 = A (P43 milestone-wide Codex per touchpoint)
- Q8 = B (spike lean + primitive API contract table + contract lock)
- Q10 = B (workflow automaton .md + machine-readable yaml)
- Q12 = B + a (server-side pypdf+python-docx, no OCR, dual-SHA manifest)
- Deleted fake Qs (retained as governance record): Q3/Q5/Q6/Q9/Q11/Q13

**Sub-phase batching (Q1=D · 4 gates total):**
1. P43-01 Contract Proof Spike (independent gate · ~1 day · must land before P43-02+)
2. P43-02..P43-04 基础线 (合 1 gate · workflow + orchestrator + doc pipeline + Freeze)
3. P43-05..P43-07 preview 层 (合 1 gate · panel gen + wiring + debug · §3e authority contract 落地)
4. P43-08..P43-10 收尾 (合 1 gate · iteration + Final Approval demonstrative + archive)

**Commit trail (branch `codex/p43-control-logic-workbench` merged to main `99211bd`):**
- `81adf39` feat(P43-00): plan v1 · Codex r1 需阻止
- `aa8e03a` docs(P43-00): plan v2 path ① · Codex r2 需修正
- `14131c4` docs(P43-00): plan v3 · Codex r3 需修正
- `cf85723` docs(P43-00): plan v4 · Codex r4 需修正
- `292a555` docs(P43-00): plan v5 · Codex r5 需修正 · Kogami Option A
- `6e46784` docs(P43-00): plan v6 · Codex r6 需修正 · Kogami Option B
- `506c870` docs(P43-00): plan v6 frozen + §8a Appendix A (initial Option B accept-residual)
- `a14dae8` docs(P43-00): plan v7 · Kogami strengthen directive · KL-1/2/3 closed · GATE-P43-PLAN Approved
- `99211bd` Merge to main (non-FF · SHAs preserved)

**Next phase:** P43-01 Contract Proof Spike · Executor draft `P43-01-00-PLAN.md` (8 scope items · must include real pdf end-to-end + blocker bug fix + primitive contract lock) · submit independent GATE-P43-01-PLAN. If spike asserted_pass fails → P43-02+ auto-frozen (non-goal #16 hard rule).

---

## Phase P42: truth_level + status into ControllerTruthMetadata schema + machine SoT + generator fix (path ①)

Status: CLOSED (merged to main `a6521ca` 2026-04-20)

**Goal:** Mirror the P35α 2-dimensional registry (truth_level + status) into the runtime `ControllerTruthMetadata` dataclass + JSON schema, close the three-way drift (runtime / docs markdown / tests) via a machine-readable yaml SoT, and fix the `generate_adapter.py` shadow-class hole that would let future auto-generated adapters bypass governance entirely.

**Adversarial history (P42 唯一 v1→v2 迭代的 Phase):**
- `GATE-P42-PLAN (v1)` Approved 2026-04-20 (Q1=A / Q2=C / Q3=B) — 落地前 Executor 按 adapter-boundary 硬性规则调 Codex GPT-5.4 xhigh adversarial review。
- Codex 返 **需修正 · 信号强** · 3 条 structural counter 命中真伤：
  · A · `**asdict(metadata)` 在 payload · v1 extend 抹 provenance 语义边界
  · B · `demonstrative/In use` 默认 + `generate_adapter.py:74-79` shadow class 使新 adapter 静默滑过
  · C · runtime hardcode + markdown + test hardcode 三源无机器闭合 · CI 可假绿
- Executor 核验 Codex 2 条事实断言均真实 · 停工 + 3 路径升级 Kogami。
- Kogami 选 **路径①**（修 plan 后重走 GATE-P42-PLAN）。
- `GATE-P42-PLAN (v2)` Approved 2026-04-20 (Q1-Q5 per Executor 建议 A/D/B/A/A · Q2 推翻为 None sentinel)。

**Sub-phases & commits (branch `codex/p42-truth-level-schema`, base `main a05bb6d`):**
- P42-00 v1 (`42acdef`): Plan v1 (230 行 · 4 counter · Q1-Q3)
- P42-00 v2 (`eaa409a`): Plan v2 (post-Codex · 431 行 · 7 counter · Q1-Q5 · verified-by codex-gpt54-xhigh)
- P42-01 (`0a13bc2`): W1 dataclass truth_level/status=None sentinel + to_dict 剥 None + JSON schema extend
- P42-02 (`bc33c95`): W2 5 metadata instantiations 显式填值
- P42-03 (`c174734`): W3 generate_adapter.py 删 shadow class + 模板默认 demonstrative/Upgrade pending
- P42-04 (`30cf3be`): W4 `docs/provenance/adapter_truth_levels.yaml` machine SoT + markdown "Machine-readable SoT" 注脚（表格 5 行零改）
- P42-05 (`3ad64e6`): W5 tests (17 schema+serializer+generator + 12 bidir = 29 new tests)
- P42-06 closure drafted

**三轨（vs P41 head a05bb6d）：**
- default pytest: **796 passed** / 1 skipped / 49 deselected in 90.60s (+29 vs P41 767 baseline · 17 schema+serializer+generator + 12 bidir)
- opt-in e2e: **49 passed** / 797 deselected in 2.99s (identical)
- adversarial wrapper: **1 passed** (8/8 inside identical)

**代码侧 invariants（字节级）：** controller.py / models.py / system_spec.py / 5 adapter evaluate/explain/evaluate_snapshot/load_spec / 所有 YAML parameter 文件 / JSON schema `$id` 与 version const / registry markdown 5 行 table · 全部不变。

**Codex counter 消化策略：** Counters C5/C6/C7 在 plan v2 `verified-by: codex-gpt54-xhigh`，**Executor 用自己语言重写 · 不直接复制 Codex 文字**（遵 v5.2 §0 Codex 调度规则）。v2 缓解落点：
- A → `to_dict` 剥 None · pre-P42 payload 字节等价 · schema description 规定语义
- B → Q2 改 D (None sentinel) · 删 shadow · 模板强制 Upgrade pending
- C → yaml SoT + dynamic importlib discover + bidir test（runtime ↔ yaml ↔ markdown table）

**Registry 2 维状态（P42 落后 · 与 P35α 不变 · 现 machine-enforced）：**

| system_id | truth_level | status | 与 runtime 绑定 |
|-----------|-------------|--------|-----------------|
| `thrust-reverser` | certified | In use | `controller_adapter.REFERENCE_DEPLOY_CONTROLLER_METADATA` |
| `bleed-air-valve` | demonstrative | Frozen | `adapters.bleed_air_adapter.BLEED_AIR_CONTROLLER_METADATA` |
| `emergency_flare_deployment_system` | demonstrative | Frozen | `adapters.efds_adapter.EFDS_CONTROLLER_METADATA` |
| `minimal_landing_gear_extension` | demonstrative | Frozen | `adapters.landing_gear_adapter.LANDING_GEAR_CONTROLLER_METADATA` |
| `c919-etras` | certified | In use | `adapters.c919_etras_adapter.C919_ETRAS_CONTROLLER_METADATA` |

P42 把三层一致性从 "人工保" 转为 "CI 保"：yaml SoT 被改动但 markdown 忘同步 → 测试红；新 adapter 生成但没登记 yaml → 测试红；registry 某行 level/status 改但 runtime metadata 忘改 → 测试红。

**Next phase:** 按 R4 等 Kogami 明示 —— 候选 P43 adapter freeze/upgrade 模板化（Kogami 2026-04-20 已预定）· P44 runtime API surface · P45 全量 yaml-ify registry · 或其他。**Codex 对抗性 review 已在治理流程中，未来 adapter boundary 变更 Phase 必先调 Codex。**
