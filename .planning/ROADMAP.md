# Roadmap

## Current Milestone

Keep AI FANTUI LogicMVP stable as a GSD-managed, Notion-synced control loop while expanding it from a deterministic cockpit demo into a spec-driven control-analysis workbench with strict acceptance, fault injection, and reusable onboarding patterns.

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

Status: Active

Goal: 将 Demo UI 从单一 thrust-reverser 系统扩展为支持在浏览器中切换查看三个控制系统（thrust-reverser / landing-gear / bleed-air valve）的逻辑链路、状态和推理结果。

Exit Criteria:

- Demo UI 顶部或侧边提供系统切换器，可切换三个已 onboard 的控制系统。
- 切换系统后，逻辑面板（chain-panel）显示对应系统的条件逻辑节点和状态。
- 切换系统后，问答推理结果区域显示对应系统的 answer payload。
- 三个系统的 adapter 均通过已有的 v1 schema 验证链路（已在 P8/P10/P12 验证）。
- Demo server 启动时默认加载 thrust-reverser，其他系统按需加载。
- 所有 23 shared validation commands 继续通过（无回归）。
- Roadmap DB shows P13=Active.

**Plans:** 1 plan(s)

Plans:
- [x] P13-01-PLAN.md // Add system-switcher + /api/system-snapshot + data-driven chain-panel + truth-evaluation answer per system (committed: 211ab2e, 07e015d, 2f818a6, cfc4aec, a28d4dc)

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

