# State

Last activity: 2026-04-09 - P6-01 archived a temporary freeze snapshot and a plain-language project history review on top of the current P5-10 monitored-demo baseline.

## Current Position

- Round 92 is complete, and the current validated baseline is local `run_gsd_validation_suite.py` with 167 tests plus 8 shared validation checks.
- Notion control tower is live at https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec.
- GitHub repo is live at https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp.
- P1 is closed as Approved in the Review Gate after GitHub-backed Opus adjudication.
- The two historical `Automation failure: P1-01 ...` gaps are now resolved as superseded by later successful runs.
- 09C now functions as a state-driven current Opus review brief, not a fixed prompt template.
- Local runs, GitHub Actions, and Notion writeback now share a single validation entrypoint via `tools/run_gsd_validation_suite.py`.
- 09C now explicitly distinguishes between “需要 Opus 审查” and “当前无需 Opus 审查”, and a normal refresh no longer overwrites an already approved gate decision.
- Review snapshots now prefer GitHub Action run / QA evidence over local Codex runs, so current Opus briefs stay anchored to the GitHub evidence plane.
- The shared validation suite now emits stable `python3 ...` command labels instead of machine-local Python executable paths.
- The GitHub workflow now runs Node24-compatible action versions and opts into `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`, matching GitHub's current deprecation path for JavaScript actions.
- The shared validation suite now also checks live Notion control-plane accessibility, validating the configured key pages and databases before a drift reaches Opus review time.
- Successful non-gated writebacks now refresh 09C automatically, so the current Opus brief keeps following the latest validated plan without a separate maintenance step.
- The old `P1 自动化目标审查 Gate` and `P1-02 消除手动浏览器 QA 依赖` records are now treated as configured legacy review artifacts and auto-archived once the approved default gate confirms no review is currently required.
- GitHub run `24168293031` proved the same retirement logic works from CI, and 09C now points at `P3-07 自动退场旧审查对象` with `当前无需 Opus 审查`.
- P4 is now closed as Approved after all six presenter-ready plans (`P4-01` through `P4-06`) verified successfully and GitHub run `24170575224` passed.
- The next roadmap phase is `P5 Demo Polish And Edge-Case Hardening`, focused on edge-case coverage and GitHub-verifiable smoke confidence instead of new product-surface expansion.
- `P5-01 GitHub 可验证 demo smoke suite` is now implemented locally: `tools/demo_path_smoke.py` covers bridge prompt, extreme clamp, mode-switch reset, and expected invalid-input behavior through the HTTP demo surface.
- The shared validation suite now includes 8 checks, with `demo_path_smoke` added as the new GitHub-verifiable presenter-demo confidence layer.
- `P5-02 最新交互胜出 demo 请求仲裁` is now implemented locally: the browser shell ignores stale prompt or lever responses once a newer interaction has started, so rapid edits no longer let an older response repaint the shared result surface.
- `P5-03 可见演示预设 smoke sweep` is now implemented locally: the smoke suite verifies `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready` through the same `POST /api/lever-snapshot` evidence plane used by the live demo.
- `P5-04 快速条件 toggle smoke sweep` is now implemented locally: the smoke suite verifies the visible blocker toggles for `engine_running`, `aircraft_on_ground`, `reverser_inhibited`, and `eec_enable` through the same HTTP evidence plane.
- `P5-05 L4 锁位与紧凑演示舱布局` is now implemented locally: deep reverse requests are capped at `-14°` until the `L4` gate is ready, the UI shows that lock state explicitly, and the demo smoke suite now covers the new lock gate.
- `P5-06 完成锁位语义与同屏观察布局` is now implemented locally: VDT controls sit at the top of the cockpit, the desktop logic board stays visible while the left column scrolls, and the interim lock-state presentation work is in place.
- `P5-07 明确条件深拉区语义并放松桌面舱面密度` is now implemented locally: the slider always shows `-32°..0°`, browser-side free dragging stays inside `-14°..0°` until the `L4` boundary unlock is ready, and the desktop lever/preset/condition areas now breathe more clearly without crowding the right-side logic board.
- `P5-08 修复 VDT live-control wiring 与条件深拉解锁回归` is now implemented locally: the moved VDT mode/percentage controls are again part of live snapshot scheduling, so dragging VDT updates the visible readout and can reopen the deep TRA drag band when the backend `L4` boundary unlock becomes ready.
- `P5-09 纠正 TRA 启动位与拖动方向语义` is now implemented locally: the cockpit no longer boots on a near-threshold preset, the TRA rail now explains that deeper reverse lives to the left, and the default interaction demonstrates the free `-14° .. 0°` band before any `L4` unlock.
- `P5-10 增加 RA-TRA-VDT 受控状态监控时间线` is now implemented locally: the demo exposes a dedicated full-width monitoring panel driven by a backend `GET /api/monitor-timeline` trace, with event markers and multi-row status curves for the user-defined RA / TRA / VDT process.
- `P6-01 同步控制塔真值与 freeze packet 基线` is now implemented locally as repo-backed archive material: the project now has a temporary freeze snapshot and a five-minute development-history review document for handoff and recap.
- `P6 Reconcile Control Tower And Freeze Demo Packet` is now drafted locally as the next planned phase, pending the current P5 Opus adjudication.

## Active Objective

Keep the development loop operational while shifting the active roadmap from P4 closeout into P5 planning:

- Write Execution Run records to Notion.
- Write QA records to Notion.
- Create UAT Gap records on failure.
- Route subjective human review through Opus 4.6 Review Gate only.
- Ensure Opus 4.6 review briefs cite Notion pages and the GitHub repo only.
- Preserve the approved P4 presenter baseline while P5 edge-case hardening is decomposed.
- Keep the first-screen cockpit flow, presenter run card, lever presets, chain state legend, current conclusion rails, result-source note, stale-state guardrails, talk track, and structured answer area aligned around the same live-demo route.
- Convert residual confidence checks into GitHub-verifiable smoke coverage before resuming deeper automatic demo changes.
- Maintain the boundary between controller truth and simplified plant feedback in demo copy and UI affordances.
- Keep the TRA conditional deep-range drag semantics and same-screen cockpit layout aligned with the same `POST /api/lever-snapshot` truth surface.
- Add a deterministic state-vs-time monitor for the cockpit chain without reintroducing a second control-truth layer or crowding the presenter surface.
- Keep a readable freeze/archive packet in the repo so the current baseline can be resumed or explained quickly after a pause.

## Blockers/Concerns

- `NOTION_API_KEY` is visible locally.
- GitHub credentials live in `~/.zshrc`, so non-interactive shells may need explicit sourcing or env injection.
- Opus 4.6 review packets must never rely on local terminal file paths.
- Historical browser hand-check notes in archived coordination docs are not part of the active review contract.
- `P5-09` is verified locally, and the control-plane default plan now points to it so the next GitHub/Notion writeback can move the current Opus review target onto the corrected startup semantics instead of the threshold-pinned `P5-08` snapshot alone.
- The Notion `01 当前状态` page is still stale (`129 tests OK` and manual-browser-QA wording), so the next planned phase should prioritize truth reconciliation and freeze-packet closure rather than new demo features.

## Accumulated Context

### Roadmap Evolution

- Phase P4 added: Elevate Cockpit Demo To Presenter-Ready
- Phase P5 added: Demo Polish And Edge-Case Hardening
- Phase P6 added: Reconcile Control Tower And Freeze Demo Packet

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
