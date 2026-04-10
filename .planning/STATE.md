# State

Last activity: 2026-04-10 - P6 now treats the dashboard as the canonical live control-plane surface under partial Notion health, while repo-side handoff docs explicitly downgrade dead status/09C/freeze links instead of pretending those archived targets are still usable.

## Current Position

- Round 92 is complete, and the current approved P5 baseline is GitHub-backed `run_gsd_validation_suite.py` evidence with 175 tests, 10 demo smoke scenarios, and 8 shared validation checks.
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
- P5 is now closed as Approved after the Opus 4.6 phase-closeout review accepted the GitHub-backed P5 evidence chain through `P5-10`.
- P6 is now the active phase: reconcile control-tower truth, freeze/demo packet surfaces, and stale manual-browser-QA wording before opening the next deeper workbench arc.
- `P7-01` and `P7-02` are already landed on `main` as early foundation work for the future spec-driven workbench, but formal P7 execution is intentionally paused until P6 closes and the control plane catches up.
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
- `P5-11 压缩监控图并清理链路主板排版` is now implemented locally: the monitor timeline is compressed to 1/10 duration, rendered as a single selectable chart under the logic board, and the explanation rails are collapsed by default to keep the presenter surface readable.
- `P6-01 同步控制塔真值与 freeze packet 基线` now owns the active reconciliation pass: update stale status surfaces, publish a concise freeze/demo packet, and retire manual-browser-QA wording as an active approval rule.
- `P6-02 控制塔首页快照自动同步` is now implemented locally: the Notion dashboard page now gets a repo-managed live snapshot section at the top, so users no longer land first on the stale `P1 / 134 tests / Awaiting Opus` view.
- `P6-03 Freeze Demo Packet 自动快照同步` is now implemented locally: the freeze packet page gets the same kind of repo-managed top snapshot as the dashboard, so the stable evidence summary can keep following the live GitHub-backed baseline instead of drifting behind the latest verified plan, and successful CI runs no longer fail outright just because Notion writeback hits a temporary sharing 404.
- `P6-04 用可自动同步状态页旁路旧 archived status 页面` is now implemented locally: a new MCP-owned status page can be fully rewritten by repo-side sync, so dashboard / 09C / freeze packet links no longer have to point at the stale archived-ancestor status page.
- `P6-05 同步 repo 侧交接文档快照` is now implemented locally: `docs/coordination/plan.md`, `docs/coordination/dev_handoff.md`, `docs/coordination/qa_report.md`, and the repo freeze packet now expose managed current-baseline sections generated from the live control-plane snapshot while preserving older round notes below as history.
- `P6-06 将历史 repo 交接正文移出活跃文档` is now implemented locally: the active repo-side coordination docs and freeze packet keep only the managed current snapshot plus a short usage/archive stub, while the old Round-based long prose now lives in dedicated archive files so stale wording stops crowding live handoff surfaces.
- `P6-07 数据库写回失败时仍推进活动页快照` is now implemented locally: if a successful run cannot finish the shared database writeback, the sync loop now falls back to the active pages, promotes the current plan/run onto dashboard/status/09C/freeze surfaces, and keeps `prepare-opus-review` usable under the same partial-token 404 condition.
- `P6-08 清理活动页重复正文与臃肿运行摘要` is now implemented locally: repo-side handoff docs now show compact evidence summaries instead of raw validation JSON, the dashboard refresh path rewrites the current snapshot cleanly, and `prepare-opus-review` no longer aborts just because the status / 09C / freeze target pages drifted into archived block states under the local integration.
- `P6-09 让 repo 入口感知 archived Notion 活跃页` is now implemented locally: repo-side coordination/freeze docs stop advertising dead Notion subpage links when the local integration sees those pages as archived, and instead explicitly route users through the dashboard plus GitHub evidence plane.
- `P6-10 显式化 dashboard-only degraded mode` is now implemented locally: the Notion health validator and dashboard snapshot treat archived `status / 09C / freeze` pages plus the database surface as an explicit dashboard-only degraded mode instead of reporting a false full-health pass.
- `P6-11 让 repo docs 跟随更新鲜的 dashboard 快照` is now implemented locally: repo-side handoff/freeze docs prefer the fresher dashboard page snapshot when local database queries lag behind the live GitHub-backed dashboard state, so repo docs can keep up with the current P6 baseline.
- A new requirement set now exists for strict engineer-facing acceptance playback, fault injection and diagnosis, knowledge capture, and future-system generalization; this is large enough to require a new phase instead of being folded into demo freeze work.
- `P7-01` has an initial local foundation: `src/well_harness/system_spec.py` now defines a reusable control-system workbench spec and captures the current thrust-reverser chain as the first reference system, including acceptance-scenario, fault-mode, and clarification-question scaffolding.
- `P7-02` is already implemented on `main`: `src/well_harness/document_intake.py` defines a mixed-document intake packet, readiness assessment, and CLI export surface so future systems can arrive as PDF/markdown-heavy packets with explicit system-defined signal semantics.
- Those two P7 slices are treated as seeded groundwork, not as authority to bypass the newly approved P6 reconciliation pass.

## Active Objective

Close the P5 -> P6 control-plane gap without adding product surface, while keeping the already-seeded P7 groundwork intact:

- Write Execution Run records to Notion.
- Write QA records to Notion.
- Create UAT Gap records on failure.
- Route subjective human review through Opus 4.6 Review Gate only.
- Ensure Opus 4.6 review briefs cite Notion pages and the GitHub repo only.
- Update the active status surface, roadmap pages, and the freeze/demo packet so they reflect the approved P5 evidence baseline instead of stale `129 tests OK` / manual-browser-QA guidance.
- Keep the first-screen cockpit flow, presenter run card, lever presets, chain state legend, current conclusion rails, result-source note, stale-state guardrails, talk track, and structured answer area aligned around the same live-demo route.
- Maintain the boundary between controller truth and simplified plant feedback in demo copy and UI affordances.
- Keep a readable freeze/archive packet in the repo and Notion so the current baseline can be resumed, reviewed, or handed off quickly after a pause.
- Keep active repo-side handoff docs intentionally slim, with older round prose moved into explicit archive files instead of lingering inline below the current snapshot.
- Keep the active Notion surfaces self-healing even when the local integration cannot reach every shared database; successful P6 control-plane runs should still advance dashboard/status/09C/freeze to the newest GitHub-backed plan.
- Preserve the seeded P7 foundation work, but do not deepen the spec-driven workbench arc until P6 closes and the control plane is back in sync.

## Blockers/Concerns

- `NOTION_API_KEY` is visible locally.
- GitHub credentials live in `~/.zshrc`, so non-interactive shells may need explicit sourcing or env injection.
- Opus 4.6 review packets must never rely on local terminal file paths.
- Historical browser hand-check notes in archived coordination docs are not part of the active review contract.
- The local `NOTION_API_KEY` integration can write directly to some key pages, but it still lacks access to parts of the shared control-plane database surface; repo-side full-database refresh paths should keep treating that token scope as a deployment dependency, not a guaranteed capability.
- `P5-09` is verified locally, and the control-plane default plan now points to it so the next GitHub/Notion writeback can move the current Opus review target onto the corrected startup semantics instead of the threshold-pinned `P5-08` snapshot alone.
- `01 当前状态` has been brought onto the P6 baseline, but the wider control tower still contains some historical summary blocks; P6 should keep trimming residual stale wording before reopening deeper P7 execution.
- The dashboard and freeze packet can now be refreshed from repo-side sync, but `01 当前状态` is still blocked on page-block access for the local integration; treat that as an explicit control-plane dependency until the integration is shared more broadly or a MCP-backed fallback owns that page.
- The original `01 当前状态` page still exists and remains blocked by archived-ancestor constraints, but the active control-plane `status` pointer now targets a new auto-synced replacement page, so user-visible links no longer need to land on the stale page.
- Repo-side coordination doc sync now falls back to active Notion pages when the local token cannot query the shared plan/run databases, so repo handoff docs can still refresh even under partial integration scope.

## Accumulated Context

### Roadmap Evolution

- Phase P4 added: Elevate Cockpit Demo To Presenter-Ready
- Phase P5 added: Demo Polish And Edge-Case Hardening
- Phase P6 added: Reconcile Control Tower And Freeze Demo Packet
- Phase P7 added: Build A Spec-Driven Control Analysis Workbench

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
