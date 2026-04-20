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
