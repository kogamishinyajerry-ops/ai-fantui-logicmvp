2026-04-25T18:14:44.543741Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T18:14:44.543801Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
Reading additional input from stdin...
OpenAI Codex v0.118.0 (research preview)
--------
workdir: /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
model: gpt-5.4
provider: openai
approval: never
sandbox: danger-full-access
reasoning effort: xhigh
reasoning summaries: none
session id: 019dc5d9-e440-7812-86f4-7d221f9ae353
--------
user
You are Codex GPT-5.4 acting as **Persona P4 — V&V Engineer** (Tier-B single-persona pipeline, E11-06 sub-phase).

# Context — E11-06 state-of-the-world status bar

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-06-status-bar-20260426`
**PR:** #21
**Worktree HEAD:** `166d8d5` (single commit on top of main `7f17c0b`)

## What E11-06 ships

Per E11-00-PLAN row E11-06: top-of-/workbench 1-line advisory status bar showing:
- **truth-engine SHA** (git rev-parse --short HEAD)
- **recent e2e** (parsed from `docs/coordination/qa_report.md`)
- **adversarial** (same source, "X/X shared validation pass")
- **open issues** (file count in `docs/known-issues/`, currently 0 — directory absent)

New endpoint: `GET /api/workbench/state-of-world` returning advisory payload with `kind: "advisory"` flag, `_source` sibling for every value, and `generated_at` ISO timestamp. POST to the endpoint must return 404/405 (read-only contract).

The visible bar carries an explicit advisory flag: `advisory · not a live truth-engine reading`.

## Files in scope

- `src/well_harness/demo_server.py` — new constant `WORKBENCH_STATE_OF_WORLD_PATH`, helpers `_truth_engine_short_sha()` / `_read_recent_evidence_lines()` / `_open_known_issues_count()`, payload `workbench_state_of_world_payload()`, GET handler. Also added `from datetime import datetime` import.
- `src/well_harness/static/workbench.html` — new `<section id="workbench-state-of-world-bar">` between topbar and wow starters
- `src/well_harness/static/workbench.css` — new `.workbench-state-of-world-bar*` selectors
- `src/well_harness/static/workbench.js` — new `hydrateStateOfWorldBar()` + DOMContentLoaded hook
- `tests/test_workbench_state_of_world_bar.py` — NEW (15 tests covering payload contract, kind=advisory, ints, ISO timestamp, live endpoint, HTML slots, JS wiring, POST→404/405)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended E11-06 entry

## Your specific lens (P4 V&V Engineer)

Focus on:
- **Endpoint contract correctness**: GET returns 200 with documented shape; POST returns 404/405; idempotent; no truth-engine mutation
- **Test coverage maps to claims**: every payload field locked, every HTML slot locked, JS wiring locked, advisory flag asserted
- **Read-only invariant**: no path through the new code mutates state
- **Source provenance**: each value's `_source` field actually matches the runtime source (qa_report.md, git, known-issues dir)
- **Failure modes**: git missing → "unknown"; qa_report missing → empty strings → bar renders "—"; known-issues dir missing → 0
- **Live evidence**: bar values match what's currently in qa_report.md

## Verification status

- 991 / 991 pytest pass (15 new in `test_workbench_state_of_world_bar.py`)
- Direct payload smoke: `workbench_state_of_world_payload()` returns `kind=advisory`, `truth_engine_sha=<git short SHA>`, `recent_e2e_label="175 tests OK"`, `adversarial_label="8/8 shared validation pass"`, `open_known_issues_count=0`
- Truth-engine red line preserved: only `static/`, `tests/`, `.planning/`, and demo_server.py touched

## Out of scope

- Updating `docs/coordination/qa_report.md` to reflect 991 tests (currently still says 175 — separate doc-sync sub-phase)
- Live re-running tests on every request — the bar is explicitly advisory
- Authenticated access to the endpoint (no auth in this MVP layer)
- Real-time websocket updates — endpoint is poll-on-load only

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path: e.g. boot demo_server, GET /api/workbench/state-of-world, verify response shape; or POST and confirm 404/405. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..166d8d5` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/`.

Sign as: **P4 — V&V Engineer (Tier-B, E11-06)**
2026-04-25T18:14:51.816909Z ERROR codex_api::endpoint::responses_websocket: failed to connect to websocket: IO error: tls handshake eof, url: wss://chatgpt.com/backend-api/codex/responses
codex
按 P4 V&V 视角做一次读代码+实机探针验收，先确认这次改动的实际文件范围、相关实现和测试覆盖，再起一个本地 probe 验证 `GET/POST /api/workbench/state-of-world` 的真实行为。
exec
/bin/zsh -lc 'rg -n "LogicMVP|state-of-world|E11-06|status bar|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
100:# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
103:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
109:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)
119:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, single copy-paste prompt delivered for Claude Code)
129:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, factual framing tightened after Claude critique)
160:# Task Group: AI FANTUI LogicMVP C919 E-TRAS reliability simulation candidates and adoption handoff
163:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s C919 E-TRAS workstation and candidate-handoff workflow, but branch names, commit SHAs, Notion pages, and demo URLs are checkout-specific.
169:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, candidate UI shipped on isolated branch after runtime fix)
179:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, Notion/GitHub handoff completed with pushed branch and final fix commit)
355:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
361:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
371:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
661:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, demo-first narrowing report without code changes)
671:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, Chinese Claude Code brief delivered in requested structure)
789:## Task 4: Keep the Phase 1 bounded-action-plan workflow truthful in both acceptance and local workbench UI
793:- rollout_summaries/2026-03-31T11-31-58-UgBd-phase1_copilot_workbench_upstream_integration_and_unsupporte.md (cwd=/Users/Zhuanz/Documents/20260330 Jerry AI CFD Project, rollout_path=/Users/Zhuanz/.codex/sessions/2026/03/31/rollout-2026-03-31T19-31-58-019d43aa-28aa-7711-8401-f53e905c11b3.jsonl, updated_at=2026-04-08T14:09:09+00:00, thread_id=019d43aa-28aa-7711-8401-f53e905c11b3, local workbench switched to upstream artifact and unsupported wording repaired)
798:- bounded_action_plan, Phase1BoundedActionPlan, supported, clarification_needed, unsupported, result_output_surface, phase1_bounded_action_plan_only, local_review_surface, workbench upstream integration, narrow Phase 1 bounded planning boundary
804:- rollout_summaries/2026-04-02T04-41-46-kVGb-phase1_ui_distance_and_interactive_postprocess_workbench.md (cwd=/Users/Zhuanz/Documents/20260330 Jerry AI CFD Project, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/02/rollout-2026-04-02T12-41-46-019d4c7f-5489-7a63-be71-48d72549d01b.jsonl, updated_at=2026-04-07T19:00:24+00:00, thread_id=019d4c7f-5489-7a63-be71-48d72549d01b, static review seed distinguished from the desired interactive workbench)
808:- UI demo, 整个真实工作流程的UI界面, 不能只是静态UI, 自然语言交互, interactive_postprocess_workbench_v1, local_review_surface, phase1_report_review_seed_page.py, 37 passed, workflow visualization
818:- when wiring the local workbench, the user asked to "把 UI workbench 切到真实 bounded action plan upstream artifact" and explicitly split `clarification_needed` from `unsupported` -> prefer upstream-backed truthful status rendering over demo-only hardcoding or softened empty-state wording [Task 4]
825:- The bounded-action-plan / workbench loop should stay truthful about `supported`, `clarification_needed`, and `unsupported`; the user reacts strongly to softened or blended status wording [Task 1]
829:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
831:- The currently implemented UI surface is still a deterministic local HTML review seed; an NL-driven postprocess cockpit belongs to a separate governed proposal such as `interactive_postprocess_workbench_v1`, not to the already-accepted static Phase 1 path [Task 5]
838:- Symptom: a Phase 1 workbench shows generic empty-state wording even when the request is outside scope -> cause: unsupported and clarification-needed were collapsed into one message -> fix: branch explicitly on `ACTION_PLAN_UNSUPPORTED_STATUS` and preserve the stronger unsupported boundary copy [Task 4]
840:- Symptom: a future agent overstates how close the repo is to a "real UI" -> cause: the deterministic review seed was mistaken for an interactive workbench -> fix: say clearly that the static Phase 1 chain is real and tested, but NL-triggered postprocessing and workflow control need a new governed phase [Task 5]
842:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
844:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
845:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
851:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
855:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
861:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
862:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
868:## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts
872:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
873:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
889:- The workbench’s fingerprint board and onboarding action board both reused existing payload fields; future UI additions should prefer wiring into current payloads over new backend contracts [Task 3]
899:# Task Group: AI FANTUI LogicMVP demo presentation, launch behavior, and leadership-facing communication
902:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
908:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, iterative refinement from user corrections)
909:- rollout_summaries/2026-04-07T06-20-24-tGb4-round_92_direct_vdt_control_flatter_logic_board.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-20-24-019d6699-6f65-7712-ba2d-13ed0f64e87e.jsonl, updated_at=2026-04-08T14:50:07+00:00, thread_id=019d6699-6f65-7712-ba2d-13ed0f64e87e, final Round 92 reflow with preserved endpoint contracts)
919:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
929:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
930:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
940:- rollout_summaries/2026-04-08T15-04-09-7j1J-reconstruct_ai_coding_development_log_and_leadership_speech.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-04-09-019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf.jsonl, updated_at=2026-04-08T15:12:08+00:00, thread_id=019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf, detailed Chinese summary and 5-minute leadership speech)
950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
951:- rollout_summaries/2026-04-07T05-30-48-VWde-thrust_reverser_harness_audit_and_control_freeze.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T13-30-48-019d666c-0536-7403-80c3-1216c53a4944.jsonl, updated_at=2026-04-08T08:22:56+00:00, thread_id=019d666c-0536-7403-80c3-1216c53a4944, frozen controller truth and simplified-plant caveat)
1240:- In this repo, the generator scripts under the external CFD workbench path were a more reliable evidence source than the rendered PDFs; when `pdftotext` is unavailable and `matplotlib` temp/cache paths are broken, parse scripts as text or AST instead of importing them [Task 1]

codex
我会按 review 合同来做：先核对 diff 和被改文件，再对 `qa_report.md` 与接口返回做对照，最后补一个 live probe 和只读红线检查。
exec
/bin/zsh -lc "sed -n '842,878p' /Users/Zhuanz/.codex/memories/MEMORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development

scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.

## Task 1: Build an isolated Notion hub and harden repo-side sync/timeouts

### rollout_summary_files

- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)

### keywords

- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass

## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查

### rollout_summary_files

- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)

### keywords

- 根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查, 当前无需 Opus 审查, Gate status: Approved, tools/gsd_notion_sync.py run, NOTION_WRITEBACK_TIMEOUT_S, P7-19, P7-20, P8-05, P8-06

## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts

### rollout_summary_files

- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)

### keywords

- 第二套系统画像, 第二套系统接入动作板, clarification_brief, blocking_reasons, unlocks_after_completion, second-system-smoke, two_system_runtime_comparison, scenario_playback, 23/23 pass


exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.agents/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: gsd-code-review
description: "Review source files changed during a phase for bugs, security issues, and code quality problems"
argument-hint: "<phase-number> [--depth=quick|standard|deep] [--files file1,file2,...]"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
  - Task
---

<objective>
Review source files changed during a phase for bugs, security vulnerabilities, and code quality problems.

Spawns the gsd-code-reviewer agent to analyze code at the specified depth level. Produces REVIEW.md artifact in the phase directory with severity-classified findings.

Arguments:
- Phase number (required) — which phase's changes to review (e.g., "2" or "02")
- `--depth=quick|standard|deep` (optional) — review depth level, overrides workflow.code_review_depth config
  - quick: Pattern-matching only (~2 min)
  - standard: Per-file analysis with language-specific checks (~5-15 min, default)
  - deep: Cross-file analysis including import graphs and call chains (~15-30 min)
- `--files file1,file2,...` (optional) — explicit comma-separated file list, skips SUMMARY/git scoping (highest precedence for scoping)

Output: {padded_phase}-REVIEW.md in phase directory + inline summary of findings
</objective>

<execution_context>
@$HOME/.Codex/get-shit-done/workflows/code-review.md
</execution_context>

<context>
Phase: $ARGUMENTS (first positional argument is phase number)

Optional flags parsed from $ARGUMENTS:
- `--depth=VALUE` — Depth override (quick|standard|deep). If provided, overrides workflow.code_review_depth config.
- `--files=file1,file2,...` — Explicit file list override. Has highest precedence for file scoping per D-08. When provided, workflow skips SUMMARY.md extraction and git diff fallback entirely.

Context files (AGENTS.md, SUMMARY.md, phase state) are resolved inside the workflow via `gsd-tools init phase-op` and delegated to agent via `<files_to_read>` blocks.
</context>

<process>
This command is a thin dispatch layer. It parses arguments and delegates to the workflow.

Execute the code-review workflow from @$HOME/.Codex/get-shit-done/workflows/code-review.md end-to-end.

The workflow (not this command) enforces these gates:
- Phase validation (before config gate)
- Config gate check (workflow.code_review)
- File scoping (--files override > SUMMARY.md > git diff fallback)
- Empty scope check (skip if no files)
- Agent spawning (gsd-code-reviewer)
- Result presentation (inline summary + next steps)
</process>

 succeeded in 0ms:
---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Instruction Priority

Superpowers skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md, GEMINI.md, or AGENTS.md says "don't use TDD" and a skill says "always use TDD," follow the user's instructions. The user is in control.

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.

**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool.

**In Gemini CLI:** Skills activate via the `activate_skill` tool. Gemini loads skill metadata at session start and activates the full content on demand.

**In other environments:** Check your platform's documentation for how skills are loaded.

## Platform Adaptation

Skills use Claude Code tool names. Non-CC platforms: see `references/copilot-tools.md` (Copilot CLI), `references/codex-tools.md` (Codex) for tool equivalents. Gemini CLI users get the tool mapping loaded automatically via GEMINI.md.

# Using Skills

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

```dot
digraph skill_flow {
    "User message received" [shape=doublecircle];
    "About to EnterPlanMode?" [shape=doublecircle];
    "Already brainstormed?" [shape=diamond];
    "Invoke brainstorming skill" [shape=box];
    "Might any skill apply?" [shape=diamond];
    "Invoke Skill tool" [shape=box];
    "Announce: 'Using [skill] to [purpose]'" [shape=box];
    "Has checklist?" [shape=diamond];
    "Create TodoWrite todo per item" [shape=box];
    "Follow skill exactly" [shape=box];
    "Respond (including clarifications)" [shape=doublecircle];

    "About to EnterPlanMode?" -> "Already brainstormed?";
    "Already brainstormed?" -> "Invoke brainstorming skill" [label="no"];
    "Already brainstormed?" -> "Might any skill apply?" [label="yes"];
    "Invoke brainstorming skill" -> "Might any skill apply?";

    "User message received" -> "Might any skill apply?";
    "Might any skill apply?" -> "Invoke Skill tool" [label="yes, even 1%"];
    "Might any skill apply?" -> "Respond (including clarifications)" [label="definitely not"];
    "Invoke Skill tool" -> "Announce: 'Using [skill] to [purpose]'";
    "Announce: 'Using [skill] to [purpose]'" -> "Has checklist?";
    "Has checklist?" -> "Create TodoWrite todo per item" [label="yes"];
    "Has checklist?" -> "Follow skill exactly" [label="no"];
    "Create TodoWrite todo per item" -> "Follow skill exactly";
}
```

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Skill Priority

When multiple skills could apply, use this order:

1. **Process skills first** (brainstorming, debugging) - these determine HOW to approach the task
2. **Implementation skills second** (frontend-design, mcp-builder) - these guide execution

"Let's build X" → brainstorming first, then implementation skills.
"Fix this bug" → debugging first, then domain-specific skills.

## Skill Types

**Rigid** (TDD, debugging): Follow exactly. Don't adapt away discipline.

**Flexible** (patterns): Adapt principles to context.

The skill itself tells you which.

## User Instructions

Instructions say WHAT, not HOW. "Add X" or "Fix Y" doesn't mean skip workflows.

codex
用 `gsd-code-review` 的 findings-first 合同来做这次验收，同时按 `verification-before-completion` 的要求只基于已跑过的证据和 live probe 下结论。
P4 V&V review for E11-06 needs code inspection, source/evidence verification, and at least one live endpoint probe before a verdict.
  → Inspect branch diff and confirm truth-engine red-line files are untouched
  • Review backend/frontend/tests for endpoint contract, advisory semantics, source provenance, and read-only behavior
  • Run live probe(s) against demo_server and verify response shape plus POST behavior
  • Issue P4 verdict with cited findings and residual risks only
exec
/bin/zsh -lc 'git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt
?? uv.lock

exec
/bin/zsh -lc 'git branch --show-current && git rev-parse --short HEAD && git rev-parse --short main' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
feat/e11-06-status-bar-20260426
166d8d5
7f17c0b

exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/verification-before-completion/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

exec
/bin/zsh -lc 'git diff --name-only main..166d8d5' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/demo_server.py
src/well_harness/static/workbench.css
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
tests/test_workbench_state_of_world_bar.py

codex
diff 范围已经确认，只触及 `demo_server.py`、静态资源、测试和 `.planning`，truth-engine 核心文件没有进入这次改动面。下一步我在逐项核对实现与测试是否真的把用户故事和失败兜底都锁住。
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""Small local UI server for the deterministic demo reasoning layer."""
     2	
     3	from __future__ import annotations
     4	
     5	import argparse
     6	from dataclasses import replace
     7	from datetime import datetime
     8	from functools import lru_cache
     9	import json
    10	import math
    11	import re
    12	from typing import Any
    13	import webbrowser
    14	from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    15	from pathlib import Path
    16	from urllib.parse import parse_qs, unquote, urlparse
    17	
    18	from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
    19	from well_harness.controller_adapter import build_reference_controller_adapter
    20	from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
    21	from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
    22	from well_harness.adapters.efds_adapter import build_efds_controller_adapter
    23	from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
    24	from well_harness.document_intake import (
    25	    apply_safe_schema_repairs,
    26	    assess_intake_packet,
    27	    build_clarification_brief,
    28	    intake_packet_from_dict,
    29	    intake_packet_to_dict,
    30	    intake_template_payload,
    31	)
    32	from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
    33	from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
    34	from well_harness.plant import PlantState, SimplifiedDeployPlant
    35	from well_harness.switches import LatchedThrottleSwitches, SwitchState
    36	from well_harness.timeline_engine import (
    37	    TimelinePlayer,
    38	    ValidationError as TimelineValidationError,
    39	    parse_timeline,
    40	)
    41	from well_harness.timeline_engine.executors.fantui import FantuiExecutor
    42	from well_harness.workbench_bundle import (
    43	    SandboxEscapeError,
    44	    archive_workbench_bundle,
    45	    build_workbench_bundle,
    46	    load_workbench_archive_manifest,
    47	    load_workbench_archive_restore_payload,
    48	)
    49	STATIC_DIR = Path(__file__).with_name("static")
    50	REFERENCE_PACKET_DIR = Path(__file__).with_name("reference_packets")
    51	REFERENCE_PACKET_PATH = REFERENCE_PACKET_DIR / "custom_reverse_control_v1.json"
    52	REPO_ROOT = Path(__file__).resolve().parents[2]
    53	RUNS_DIR = REPO_ROOT / "runs"
    54	DEFAULT_HOST = "127.0.0.1"
    55	DEFAULT_PORT = 8000
    56	# Server-side DoS guard: 10 MB, aligned with browser client limit.
    57	_MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
    58	CONTENT_TYPES = {
    59	    ".html": "text/html; charset=utf-8",
    60	    ".css": "text/css; charset=utf-8",
    61	    ".js": "application/javascript; charset=utf-8",
    62	    ".json": "application/json; charset=utf-8",
    63	    ".svg": "image/svg+xml; charset=utf-8",
    64	    ".ico": "image/x-icon",
    65	    ".png": "image/png",
    66	}
    67	SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
    68	SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
    69	TRA_L4_LOCK_DEG = -14.0
    70	MONITOR_TIMELINE_PATH = "/api/monitor-timeline"
    71	WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
    72	WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
    73	WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
    74	WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
    75	WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
    76	# E11-06 (2026-04-26): state-of-the-world status bar endpoint.
    77	WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
    78	MONITOR_RA_START_FT = 7.0
    79	MONITOR_RA_RATE_FT_PER_S = 1.0
    80	MONITOR_TRA_START_S = 1.0
    81	MONITOR_TRA_RATE_DEG_PER_S = 10.0
    82	MONITOR_TRA_LOCK_DEG = -14.0
    83	MONITOR_VDT_START_S = 2.4
    84	MONITOR_VDT_RATE_PERCENT_PER_S = 50.0
    85	MONITOR_ACTIVE_END_S = 4.4
    86	MONITOR_TIMELINE_END_S = 7.0
    87	MONITOR_TIMELINE_COMPRESSION_RATIO = 10.0
    88	MONITOR_ENGINE_RUNNING = True
    89	MONITOR_AIRCRAFT_ON_GROUND = True
    90	MONITOR_REVERSER_INHIBITED = False
    91	MONITOR_EEC_ENABLE = True
    92	
    93	# Reverse diagnosis API (P19.6)
    94	DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
    95	# Monte Carlo reliability API (P19.7)
    96	MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
    97	# Hardware schema discovery (P19.8)
    98	HARDWARE_SCHEMA_PATH = "/api/hardware/schema"
    99	SENSITIVITY_SWEEP_PATH = "/api/sensitivity-sweep"
   100	# FANTUI stateful tick endpoints — live counterpart to C919 /api/tick.
   101	# The existing /api/lever-snapshot stays stateless; this triad is separate
   102	# so the two surfaces don't fight each other or share global state.
   103	FANTUI_TICK_PATH = "/api/fantui/tick"
   104	FANTUI_RESET_PATH = "/api/fantui/reset"
   105	FANTUI_LOG_PATH = "/api/fantui/log"
   106	FANTUI_STATE_PATH = "/api/fantui/state"
   107	FANTUI_SET_VDT_PATH = "/api/fantui/set_vdt"
   108	
   109	STATIC_ROUTE_ALIASES = {
   110	    "/favicon.ico": "favicon.svg",
   111	    "/apple-touch-icon.png": "apple-touch-icon.svg",
   112	}
   113	
   114	SENSITIVITY_SWEEP_DEFAULT_RA_VALUES = (2.0, 5.0, 10.0, 20.0, 40.0)
   115	SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES = (-28.0, -20.0, -15.0, -11.0, -6.0)
   116	SENSITIVITY_SWEEP_DEFAULT_OUTCOMES = (
   117	    "logic1_active",
   118	    "logic3_active",
   119	    "thr_lock_active",
   120	    "deploy_confirmed",
   121	)
   122	SENSITIVITY_SWEEP_ALLOWED_OUTCOMES = frozenset(
   123	    {
   124	        "logic1_active",
   125	        "logic2_active",
   126	        "logic3_active",
   127	        "thr_lock_active",
   128	        "deploy_confirmed",
   129	        "tls_unlocked",
   130	        "pls_unlocked",
   131	    }
   132	)
   133	
   134	_SYSTEM_YAML_MAP = {
   135	    "thrust-reverser": "thrust_reverser_hardware_v1.yaml",
   136	    "landing-gear": "landing_gear_hardware_v1.yaml",
   137	    "bleed-air": "bleed_air_hardware_v1.yaml",
   138	    "c919-etras": "c919_etras_hardware_v1.yaml",
   139	}
   140	
   141	# Systems whose YAML format is loadable by load_thrust_reverser_hardware.
   142	# Landing-gear and bleed-air YAMLs use a different schema and cannot be loaded
   143	# by the thrust-reverser-specific engine; they are served via the generic loader
   144	# in _handle_hardware_schema only.
   145	_SUPPORTED_FOR_ANALYSIS = frozenset({"thrust-reverser"})
   146	
   147	MONITOR_N1K = 35.0
   148	MONITOR_MAX_N1K_DEPLOY_LIMIT = 60.0
   149	LEVER_NUMERIC_INPUTS = {
   150	    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
   151	    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
   152	    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
   153	    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
   154	}
   155	LEVER_BOOLEAN_INPUTS = {
   156	    "engine_running": True,
   157	    "aircraft_on_ground": True,
   158	    "reverser_inhibited": False,
   159	    "eec_enable": True,
   160	}
   161	LEVER_FEEDBACK_MODES = {
   162	    "auto_scrubber",
   163	    "manual_feedback_override",
   164	}
   165	LEVER_SNAPSHOT_FAULT_NODE_ALIASES = {
   166	    "sw1_input": "sw1",
   167	    "sw2_input": "sw2",
   168	}
   169	LEVER_SNAPSHOT_FAULT_NODES = {
   170	    "sw1",
   171	    "sw2",
   172	    "radio_altitude_ft",
   173	    "n1k",
   174	    "tls115",
   175	    "logic1",
   176	    "logic2",
   177	    "logic3",
   178	    "logic4",
   179	    "thr_lock",
   180	    "vdt90",
   181	    "sw1_input",
   182	    "sw2_input",
   183	}
   184	LEVER_SNAPSHOT_FAULT_TYPES = {
   185	    "stuck_off",
   186	    "stuck_on",
   187	    "sensor_zero",
   188	    "logic_stuck_false",
   189	    "cmd_blocked",
   190	}
   191	FAULT_INJECTION_REASON = "fault_injection"
   192	
   193	# ── FANTUI stateful tick singleton ─────────────────────────────────────────
   194	# Module-level state. ``FantuiTickSystem`` is itself thread-safe — see its
   195	# internal ``_lock`` — so no outer lock is needed here. Restarting the server
   196	# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
   197	# ``_FANTUI_LOCK`` is kept as an alias to the system's internal lock for
   198	# backward-compatibility with any test that reached in directly.
   199	_FANTUI_SYSTEM = FantuiTickSystem()
   200	_FANTUI_LOCK = _FANTUI_SYSTEM._lock
   201	
   202	
   203	class DemoRequestHandler(BaseHTTPRequestHandler):
   204	    """Serve the static demo shell and a thin JSON API around DemoAnswer."""
   205	
   206	    server_version = "WellHarnessDemo/1.0"
   207	
   208	    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
   209	        return
   210	
   211	    def do_GET(self):
   212	        parsed = urlparse(self.path)
   213	        if parsed.path in STATIC_ROUTE_ALIASES:
   214	            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
   215	            return
   216	        if parsed.path == MONITOR_TIMELINE_PATH:
   217	            self._send_json(200, monitor_timeline_payload())
   218	            return
   219	        if parsed.path == WORKBENCH_BOOTSTRAP_PATH:
   220	            self._send_json(200, workbench_bootstrap_payload())
   221	            return
   222	        if parsed.path == SYSTEM_SNAPSHOT_PATH:
   223	            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
   224	            self._send_json(200, system_snapshot_payload(system_id))
   225	            return
   226	        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
   227	            self._send_json(200, workbench_recent_archives_payload())
   228	            return
   229	        if parsed.path == WORKBENCH_STATE_OF_WORLD_PATH:
   230	            # E11-06 (2026-04-26): aggregated state-of-the-world for the
   231	            # /workbench top-of-page status bar. Read-only — never mutates
   232	            # truth-engine state. Fields are *advisory*: they reflect the
   233	            # last-recorded evidence (git SHA + qa_report.md + freeze
   234	            # packet), not a live test run.
   235	            self._send_json(200, workbench_state_of_world_payload())
   236	            return
   237	
   238	        # Default entry: unified landing page with 2x3 card grid
   239	        # (Phase A: chat.html shelved; Phase UI-C: root now serves index.html
   240	        # instead of demo.html so user can reach all 6 surfaces.)
   241	        if parsed.path in ("", "/"):
   242	            self._serve_static("index.html")
   243	            return
   244	
   245	        if parsed.path in ("/demo.html", "/expert/demo.html"):
   246	            self._serve_static("demo.html")
   247	            return
   248	
   249	        if parsed.path in ("/workbench/start", "/workbench/start.html"):
   250	            self._serve_static("workbench_start.html")
   251	            return
   252	
   253	        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
   254	            self._serve_static("workbench_bundle.html")
   255	            return
   256	
   257	        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
   258	            self._serve_static("workbench.html")
   259	            return
   260	

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.css | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	@import url("/design-tokens.css");
     2	
     3	.workbench-shell {
     4	  padding-bottom: 4rem;
     5	}
     6	
     7	.workbench-collab-topbar,
     8	.workbench-collab-bottom-bar,
     9	.workbench-collab-grid,
    10	.workbench-annotation-toolbar,
    11	.workbench-approval-center,
    12	.workbench-annotation-inbox {
    13	  border: 1px solid rgba(143, 214, 233, 0.16);
    14	  background: rgba(8, 18, 29, 0.86);
    15	  box-shadow: var(--shadow-sm);
    16	}
    17	
    18	.workbench-collab-topbar {
    19	  position: sticky;
    20	  top: 0;
    21	  z-index: 10;
    22	  display: grid;
    23	  grid-template-columns: minmax(14rem, 1fr) auto auto auto minmax(12rem, 16rem);
    24	  gap: 0.9rem;
    25	  align-items: center;
    26	  margin-bottom: 1rem;
    27	  padding: 0.9rem 1rem;
    28	  backdrop-filter: blur(16px);
    29	}
    30	
    31	.workbench-collab-brand h1,
    32	.workbench-collab-column h2,
    33	.workbench-annotation-inbox h2 {
    34	  margin: 0;
    35	}
    36	
    37	.workbench-collab-chip,
    38	.workbench-collab-system {
    39	  display: flex;
    40	  flex-direction: column;
    41	  gap: 0.25rem;
    42	  min-width: 0;
    43	}
    44	
    45	.workbench-collab-chip span,
    46	.workbench-collab-system span {
    47	  color: rgba(206, 223, 236, 0.7);
    48	  font-size: 0.75rem;
    49	  letter-spacing: 0.06em;
    50	  text-transform: uppercase;
    51	}
    52	
    53	.workbench-collab-chip strong {
    54	  color: #eff8ff;
    55	  font-size: 0.95rem;
    56	}
    57	
    58	.workbench-collab-system select {
    59	  border: 1px solid rgba(143, 214, 233, 0.22);
    60	  border-radius: 8px;
    61	  background: rgba(8, 17, 28, 0.92);
    62	  color: #edf8ff;
    63	  padding: 0.65rem 0.8rem;
    64	}
    65	
    66	/* E11-13: feedback-mode chip with advisory affordance.
    67	   Distinct visual weight from neutral chips so the user reads it as
    68	   a mode indicator, not just metadata. Amber tint signals advisory
    69	   (not breach). */
    70	.workbench-feedback-mode-chip {
    71	  position: relative;
    72	  padding: 0.35rem 0.7rem;
    73	  border: 1px solid rgba(247, 188, 92, 0.45);
    74	  border-radius: 8px;
    75	  background: rgba(247, 188, 92, 0.08);
    76	}
    77	
    78	.workbench-feedback-mode-chip strong {
    79	  color: #f7d398;
    80	}
    81	
    82	.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] {
    83	  border-color: rgba(120, 220, 170, 0.45);
    84	  background: rgba(120, 220, 170, 0.08);
    85	}
    86	
    87	.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] strong {
    88	  color: #b6e8d2;
    89	}
    90	
    91	.workbench-feedback-mode-dot {
    92	  position: absolute;
    93	  top: 0.45rem;
    94	  right: 0.55rem;
    95	  width: 0.55rem;
    96	  height: 0.55rem;
    97	  border-radius: 50%;
    98	  background: rgba(247, 188, 92, 0.85);
    99	  box-shadow: 0 0 6px rgba(247, 188, 92, 0.55);
   100	}
   101	
   102	.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] .workbench-feedback-mode-dot {
   103	  background: rgba(120, 220, 170, 0.85);
   104	  box-shadow: 0 0 6px rgba(120, 220, 170, 0.5);
   105	}
   106	
   107	/* E11-06 (2026-04-26): state-of-the-world status bar.
   108	   1-line top-of-/workbench bar showing truth-engine SHA · recent e2e ·
   109	   adversarial · open known-issues. Read-only, advisory. The trailing
   110	   "advisory" flag is the contract that this is NOT a live truth-engine
   111	   reading. */
   112	.workbench-state-of-world-bar {
   113	  display: flex;
   114	  flex-wrap: wrap;
   115	  align-items: center;
   116	  gap: 0.55rem;
   117	  margin-bottom: 0.85rem;
   118	  padding: 0.55rem 0.9rem;
   119	  border: 1px solid rgba(206, 223, 236, 0.18);
   120	  border-radius: 8px;
   121	  background: rgba(8, 18, 34, 0.65);
   122	  font-size: 0.85rem;
   123	  line-height: 1.4;
   124	  color: rgba(206, 223, 236, 0.86);
   125	}
   126	
   127	.workbench-sow-eyebrow {
   128	  margin-right: 0.4rem;
   129	  padding: 0.1rem 0.45rem;
   130	  border-radius: 4px;
   131	  background: rgba(206, 223, 236, 0.1);
   132	  color: rgba(206, 223, 236, 0.7);
   133	  font-size: 0.7rem;
   134	  letter-spacing: 0.08em;
   135	  text-transform: uppercase;
   136	}
   137	
   138	.workbench-sow-field {
   139	  display: inline-flex;
   140	  align-items: baseline;
   141	  gap: 0.35rem;
   142	}
   143	
   144	.workbench-sow-label {
   145	  color: rgba(206, 223, 236, 0.62);
   146	  font-size: 0.75rem;
   147	  letter-spacing: 0.04em;
   148	  text-transform: lowercase;
   149	}
   150	
   151	.workbench-sow-value {
   152	  font-family: "SFMono-Regular", "Menlo", monospace;
   153	  color: #d8ecff;
   154	  font-size: 0.88rem;
   155	}
   156	
   157	.workbench-sow-sep {
   158	  color: rgba(206, 223, 236, 0.32);
   159	  font-weight: 600;
   160	}
   161	
   162	.workbench-sow-flag {
   163	  margin-left: auto;
   164	  padding: 0.1rem 0.5rem;
   165	  border-radius: 4px;
   166	  background: rgba(247, 188, 92, 0.14);
   167	  color: #f7d398;
   168	  font-size: 0.72rem;
   169	  letter-spacing: 0.04em;
   170	}
   171	
   172	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
   173	   Top-of-/workbench placement so the demo presenter has a one-click
   174	   走读 entrypoint to BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose
   175	   without typing payloads by hand. */
   176	.workbench-wow-starters {
   177	  margin-bottom: 1rem;
   178	  padding: 1rem 1.1rem;
   179	  border: 1px solid rgba(120, 200, 255, 0.28);
   180	  border-radius: 12px;
   181	  background: rgba(12, 28, 48, 0.55);
   182	}
   183	
   184	.workbench-wow-starters-header {
   185	  margin-bottom: 0.85rem;
   186	}
   187	
   188	.workbench-wow-starters-header h2 {
   189	  margin: 0.2rem 0 0.35rem;
   190	  font-size: 1.15rem;
   191	  color: #d8ecff;
   192	}
   193	
   194	.workbench-wow-starters-sub {
   195	  margin: 0;
   196	  color: rgba(206, 223, 236, 0.78);
   197	  font-size: 0.85rem;
   198	}
   199	
   200	.workbench-wow-starters-grid {
   201	  display: grid;
   202	  grid-template-columns: repeat(3, minmax(0, 1fr));
   203	  gap: 0.85rem;
   204	}
   205	
   206	@media (max-width: 960px) {
   207	  .workbench-wow-starters-grid {
   208	    grid-template-columns: 1fr;
   209	  }
   210	}
   211	
   212	.workbench-wow-card {
   213	  display: flex;
   214	  flex-direction: column;
   215	  gap: 0.55rem;
   216	  padding: 0.85rem 0.95rem;
   217	  border: 1px solid rgba(120, 200, 255, 0.22);
   218	  border-radius: 10px;
   219	  background: rgba(8, 18, 34, 0.65);
   220	}
   221	
   222	.workbench-wow-card header {
   223	  display: flex;
   224	  align-items: baseline;
   225	  gap: 0.55rem;
   226	}
   227	
   228	.workbench-wow-card h3 {
   229	  margin: 0;
   230	  font-size: 1rem;
   231	  color: #e6f1ff;
   232	}
   233	
   234	.workbench-wow-tag {
   235	  padding: 0.1rem 0.45rem;
   236	  border-radius: 4px;
   237	  background: rgba(120, 200, 255, 0.18);
   238	  color: #9ed3ff;
   239	  font-family: "SFMono-Regular", "Menlo", monospace;
   240	  font-size: 0.72rem;
   241	  letter-spacing: 0.04em;
   242	  text-transform: lowercase;
   243	}
   244	
   245	.workbench-wow-card-desc {
   246	  margin: 0;
   247	  color: rgba(206, 223, 236, 0.84);
   248	  font-size: 0.85rem;
   249	  line-height: 1.45;
   250	}
   251	
   252	.workbench-wow-card-desc code {
   253	  padding: 0.05rem 0.3rem;
   254	  border-radius: 3px;
   255	  background: rgba(120, 200, 255, 0.12);
   256	  color: #b8e0ff;
   257	  font-size: 0.8rem;
   258	}
   259	
   260	.workbench-wow-run-button {

 succeeded in 0ms:
     1	<!doctype html>
     2	<html lang="zh-CN">
     3	  <head>
     4	    <meta charset="utf-8">
     5	    <meta name="viewport" content="width=device-width, initial-scale=1">
     6	    <title>Control Logic Workbench</title>
     7	    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
     8	    <link rel="apple-touch-icon" href="/apple-touch-icon.svg">
     9	    <link rel="manifest" href="/manifest.json">
    10	    <link rel="stylesheet" href="/demo.css">
    11	    <link rel="stylesheet" href="/workbench.css">
    12	  </head>
    13	  <body data-view="beginner">
    14	    <main class="shell workbench-shell">
    15	      <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
    16	        <div class="workbench-collab-brand">
    17	          <p class="eyebrow">control logic workbench</p>
    18	          <h1>Control Logic Workbench</h1>
    19	        </div>
    20	        <div id="workbench-identity" class="workbench-collab-chip" data-role="ENGINEER">
    21	          <span>Identity</span>
    22	          <strong>Kogami / Engineer</strong>
    23	        </div>
    24	        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
    25	          <span>Ticket</span>
    26	          <strong>WB-E06-SHELL</strong>
    27	        </div>
    28	        <div
    29	          id="workbench-feedback-mode"
    30	          class="workbench-collab-chip workbench-feedback-mode-chip"
    31	          data-feedback-mode="manual_feedback_override"
    32	          data-mode-authority="advisory"
    33	          aria-live="polite"
    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
    35	        >
    36	          <span>Feedback Mode</span>
    37	          <strong>Manual (advisory)</strong>
    38	          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
    39	        </div>
    40	        <label class="workbench-collab-system" for="workbench-system-select">
    41	          <span>System</span>
    42	          <select id="workbench-system-select">
    43	            <option value="thrust-reverser">Thrust Reverser</option>
    44	            <option value="landing-gear">Landing Gear</option>
    45	            <option value="bleed-air-valve">Bleed Air Valve</option>
    46	            <option value="c919-etras">C919 E-TRAS</option>
    47	          </select>
    48	        </label>
    49	      </section>
    50	
    51	      <section
    52	        id="workbench-state-of-world-bar"
    53	        class="workbench-state-of-world-bar"
    54	        aria-label="State-of-the-world status bar (advisory)"
    55	        data-status-kind="advisory"
    56	      >
    57	        <span class="workbench-sow-eyebrow">state of world</span>
    58	        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
    59	              title="git rev-parse --short HEAD">
    60	          <span class="workbench-sow-label">truth-engine SHA</span>
    61	          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
    62	        </span>
    63	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    64	        <span class="workbench-sow-field" data-sow-field="recent_e2e"
    65	              title="docs/coordination/qa_report.md (most recent test run)">
    66	          <span class="workbench-sow-label">recent e2e</span>
    67	          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
    68	        </span>
    69	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    70	        <span class="workbench-sow-field" data-sow-field="adversarial"
    71	              title="docs/coordination/qa_report.md (shared validation)">
    72	          <span class="workbench-sow-label">adversarial</span>
    73	          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
    74	        </span>
    75	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    76	        <span class="workbench-sow-field" data-sow-field="known_issues"
    77	              title="docs/known-issues/ file count">
    78	          <span class="workbench-sow-label">open issues</span>
    79	          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
    80	        </span>
    81	        <span class="workbench-sow-flag" aria-hidden="false">
    82	          advisory · not a live truth-engine reading
    83	        </span>
    84	      </section>
    85	
    86	      <section
    87	        id="workbench-wow-starters"
    88	        class="workbench-wow-starters"
    89	        aria-label="Canonical demo scenarios — one-click starter cards"
    90	      >
    91	        <header class="workbench-wow-starters-header">
    92	          <p class="eyebrow">canonical scenarios</p>
    93	          <h2>起手卡 · One-click 走读</h2>
    94	          <p class="workbench-wow-starters-sub">
    95	            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
    96	          </p>
    97	        </header>
    98	        <div class="workbench-wow-starters-grid">
    99	          <article
   100	            class="workbench-wow-card"
   101	            data-wow-id="wow_a"
   102	            aria-labelledby="workbench-wow-a-title"
   103	          >
   104	            <header>
   105	              <span class="workbench-wow-tag">wow_a</span>
   106	              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
   107	            </header>
   108	            <p class="workbench-wow-card-desc">
   109	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
   110	              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
   111	              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
   112	              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
   113	            </p>
   114	            <button
   115	              type="button"
   116	              class="workbench-wow-run-button"
   117	              data-wow-action="run"
   118	              data-wow-id="wow_a"
   119	            >
   120	              一键运行 wow_a
   121	            </button>
   122	            <div
   123	              class="workbench-wow-result"
   124	              data-wow-result-for="wow_a"
   125	              role="status"
   126	              aria-live="polite"
   127	            >
   128	              尚未运行。
   129	            </div>
   130	          </article>
   131	          <article
   132	            class="workbench-wow-card"
   133	            data-wow-id="wow_b"
   134	            aria-labelledby="workbench-wow-b-title"
   135	          >
   136	            <header>
   137	              <span class="workbench-wow-tag">wow_b</span>
   138	              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
   139	            </header>
   140	            <p class="workbench-wow-card-desc">
   141	              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
   142	              success_rate + failure_modes 分布。
   143	            </p>
   144	            <button
   145	              type="button"
   146	              class="workbench-wow-run-button"
   147	              data-wow-action="run"
   148	              data-wow-id="wow_b"
   149	            >
   150	              一键运行 wow_b
   151	            </button>
   152	            <div
   153	              class="workbench-wow-result"
   154	              data-wow-result-for="wow_b"
   155	              role="status"
   156	              aria-live="polite"
   157	            >
   158	              尚未运行。
   159	            </div>
   160	          </article>
   161	          <article
   162	            class="workbench-wow-card"
   163	            data-wow-id="wow_c"
   164	            aria-labelledby="workbench-wow-c-title"
   165	          >
   166	            <header>
   167	              <span class="workbench-wow-tag">wow_c</span>
   168	              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
   169	            </header>
   170	            <p class="workbench-wow-card-desc">
   171	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   172	              触发该 outcome 的参数组合（max_results=10）。
   173	            </p>
   174	            <button
   175	              type="button"
   176	              class="workbench-wow-run-button"
   177	              data-wow-action="run"
   178	              data-wow-id="wow_c"
   179	            >
   180	              一键运行 wow_c
   181	            </button>
   182	            <div
   183	              class="workbench-wow-result"
   184	              data-wow-result-for="wow_c"
   185	              role="status"
   186	              aria-live="polite"
   187	            >
   188	              尚未运行。
   189	            </div>
   190	          </article>
   191	        </div>
   192	      </section>
   193	
   194	      <aside
   195	        id="workbench-trust-banner"
   196	        class="workbench-trust-banner"
   197	        data-feedback-mode="manual_feedback_override"
   198	        role="note"
   199	        aria-label="Feedback mode trust affordance"
   200	      >
   201	        <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
   202	        <div class="workbench-trust-banner-body">
   203	          <span class="workbench-trust-banner-scope">
   204	            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
   205	            an observed reading — for example, editing a snapshot input field before running a scenario.
   206	            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
   207	          </span>
   208	          <strong>That mode is advisory.</strong>
   209	          <span>
   210	            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   211	            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   212	          </span>
   213	        </div>
   214	        <button
   215	          type="button"
   216	          class="workbench-trust-banner-dismiss"
   217	          aria-label="Hide trust banner for this session"
   218	          data-trust-banner-dismiss
   219	        >
   220	          Hide for session

 succeeded in 0ms:
     1	const workbenchBootstrapPath = "/api/workbench/bootstrap";
     2	const workbenchBundlePath = "/api/workbench/bundle";
     3	const workbenchRepairPath = "/api/workbench/repair";
     4	const workbenchArchiveRestorePath = "/api/workbench/archive-restore";
     5	const workbenchRecentArchivesPath = "/api/workbench/recent-archives";
     6	const workbenchPacketWorkspaceStorageKey = "well-harness-workbench-packet-workspace-v1";
     7	const draftDesignStateKey = "draft_design_state";
     8	const workbenchPersistedFieldIds = [
     9	  "workbench-scenario-id",
    10	  "workbench-fault-mode-id",
    11	  "workbench-sample-period",
    12	  "workbench-archive-toggle",
    13	  "workbench-archive-manifest-path",
    14	  "workbench-handoff-note",
    15	  "workbench-observed-symptoms",
    16	  "workbench-evidence-links",
    17	  "workbench-root-cause",
    18	  "workbench-repair-action",
    19	  "workbench-validation-after-fix",
    20	  "workbench-residual-risk",
    21	  "workbench-logic-change",
    22	  "workbench-reliability-gain",
    23	  "workbench-guardrail-note",
    24	];
    25	
    26	const defaultReferenceResolution = {
    27	  rootCause: "Pressure sensor bias was confirmed during troubleshooting.",
    28	  repairAction: "Recalibrated the sensor path.",
    29	  validationAfterFix: "Acceptance replay completed after the repair.",
    30	  residualRisk: "Watch for future sensor drift.",
    31	  logicChange: "Add a pressure plausibility cross-check before enabling the deploy chain.",
    32	  reliabilityGain: "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
    33	  guardrailNote: "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
    34	};
    35	
    36	let bootstrapPayload = null;
    37	let latestWorkbenchRequestId = 0;
    38	let currentWorkbenchRunLabel = "手动生成";
    39	let workbenchRecentArchives = [];
    40	let workbenchRunHistory = [];
    41	let selectedWorkbenchHistoryId = "";
    42	let workbenchHistorySequence = 0;
    43	let currentWorkbenchViewMode = "empty";
    44	let workbenchPacketRevisionHistory = [];
    45	let selectedWorkbenchPacketRevisionId = "";
    46	let workbenchPacketRevisionSequence = 0;
    47	let suspendWorkbenchPacketWorkspacePersistence = false;
    48	const maxWorkbenchRunHistory = 6;
    49	const maxWorkbenchPacketRevisionHistory = 8;
    50	
    51	// E11-03 R2 (P1 NIT fix, 2026-04-26): translate the internal column
    52	// token (control/document/circuit) into the user-facing engineer-task
    53	// verb so the failure-path copy never reverts to technical-noun
    54	// phrasing. Mapping mirrors the rename in workbench.html.
    55	const WORKBENCH_COLUMN_LABEL = {
    56	  control: "Probe & Trace",
    57	  document: "Annotate & Propose",
    58	  circuit: "Hand off & Track",
    59	};
    60	
    61	function bootWorkbenchColumnSafely(columnName, bootFn) {
    62	  try {
    63	    bootFn();
    64	  } catch (error) {
    65	    const status = workbenchElement(`workbench-${columnName}-status`);
    66	    if (status) {
    67	      const label = WORKBENCH_COLUMN_LABEL[columnName] || columnName;
    68	      status.textContent = `${label} panel failed independently: ${error.message || error}`;
    69	      status.dataset.tone = "warning";
    70	    }
    71	  }
    72	}
    73	
    74	// E11-03 (2026-04-26): the three columns were renamed from technical
    75	// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")
    76	// to engineer-task verbs ("Probe & Trace / Annotate & Propose / Hand off
    77	// & Track"). Underlying ids and data-column tokens stay stable so e2e
    78	// selectors don't break — only the visible status copy here changes.
    79	//
    80	// E11-03 R2 (P5 IMPORTANT fix, 2026-04-26): drop internal phase tokens
    81	// ("E07+", "E07") from the user-visible hydrated copy. Customers/new
    82	// engineers should not need to know roadmap codes; the staging note is
    83	// rephrased in plain language.
    84	function bootWorkbenchControlPanel() {
    85	  const status = workbenchElement("workbench-control-status");
    86	  if (status) {
    87	    status.textContent =
    88	      "Probe & Trace ready. Scenario actions are staged for the next bundle.";
    89	    status.dataset.tone = "ready";
    90	  }
    91	}
    92	
    93	function bootWorkbenchDocumentPanel() {
    94	  const status = workbenchElement("workbench-document-status");
    95	  if (status) {
    96	    status.textContent =
    97	      "Annotate & Propose ready. Text-range annotation is staged for the next bundle.";
    98	    status.dataset.tone = "ready";
    99	  }
   100	}
   101	
   102	function bootWorkbenchCircuitPanel() {
   103	  const status = workbenchElement("workbench-circuit-status");
   104	  if (status) {
   105	    status.textContent =
   106	      "Hand off & Track ready. Overlay annotation is staged for the next bundle.";
   107	    status.dataset.tone = "ready";
   108	  }
   109	}
   110	
   111	function bootWorkbenchShell() {
   112	  bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
   113	  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
   114	  bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
   115	}
   116	
   117	// P43 authority contract — written only via assignFrozenSpec; never mutated directly
   118	let frozenSpec = null;
   119	
   120	// P43 workflow state machine (P43-03)
   121	let workflowState = "INIT";
   122	
   123	const _workflowTransitions = {
   124	  INIT:        { confirm_freeze: "FROZEN",      load_packet: "INIT" },
   125	  FROZEN:      { start_gen: "GENERATING",       confirm_freeze: "FROZEN",   reiterate: "INIT" },
   126	  GENERATING:  { gen_complete: "PANEL_READY",   gen_fail: "ERROR",          reiterate: "INIT" },
   127	  PANEL_READY: { final_approve: "APPROVING",    start_gen: "GENERATING",    reiterate: "INIT" },
   128	  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
   129	  APPROVED:    { archive: "ARCHIVING" },
   130	  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
   131	  ARCHIVED:    {},
   132	  ERROR:       { reiterate: "INIT" },
   133	};
   134	
   135	function dispatchWorkflowEvent(event) {
   136	  const next = (_workflowTransitions[workflowState] || {})[event];
   137	  if (next === undefined) {
   138	    return false;
   139	  }
   140	  workflowState = next;
   141	  updateWorkflowUI();
   142	  return true;
   143	}
   144	
   145	function updateWorkflowUI() {
   146	  const approveBtn  = workbenchElement("workbench-final-approve");
   147	  const startGenBtn = workbenchElement("workbench-start-gen");
   148	  const badge       = workbenchElement("workbench-workflow-state");
   149	
   150	  // "冻结审批 Spec" enabled when spec is not yet frozen or after generation
   151	  const approveEnabled = ["INIT", "PANEL_READY", "ANNOTATING", "WIRING"].includes(workflowState);
   152	  // "生成 (Frozen Spec)" enabled only when a frozen spec exists
   153	  const startGenEnabled = workflowState === "FROZEN";
   154	
   155	  if (approveBtn)  approveBtn.disabled  = !approveEnabled;
   156	  if (startGenBtn) startGenBtn.disabled = !startGenEnabled;
   157	  if (badge) {
   158	    badge.textContent    = workflowState;
   159	    badge.dataset.state  = workflowState.toLowerCase();
   160	  }
   161	}
   162	
   163	const workbenchPresets = {
   164	  ready_archived: {
   165	    label: "一键通过验收",
   166	    archiveBundle: true,
   167	    source: "reference",
   168	    sourceStatus: "当前样例：参考样例。系统会直接跑完整 happy path 并生成 archive。",
   169	    preparationMessage: "参考样例已就位，系统马上开始生成 ready bundle 并留档。",
   170	  },
   171	  blocked_follow_up: {
   172	    label: "一键看阻塞态",
   173	    archiveBundle: false,
   174	    source: "template",
   175	    sourceStatus: "当前样例：空白模板。系统会故意演示 clarification gate 如何把不完整 packet 拦下来。",
   176	    preparationMessage: "空白模板已就位，系统马上演示阻塞态。",
   177	  },
   178	  ready_preview: {
   179	    label: "一键快速预览",
   180	    archiveBundle: false,
   181	    source: "reference",
   182	    sourceStatus: "当前样例：参考样例。系统会直接跑 ready bundle，但不生成 archive。",
   183	    preparationMessage: "参考样例已就位，系统马上生成 ready bundle 供快速查看。",
   184	  },
   185	  archive_retry: {
   186	    label: "一键留档复跑",
   187	    archiveBundle: true,
   188	    source: "reference",
   189	    sourceStatus: "当前样例：参考样例。这个预设适合连续复跑，archive 会自动避开重名目录。",
   190	    preparationMessage: "参考样例已就位，系统马上做一次带 archive 的复跑。",
   191	  },
   192	};
   193	
   194	function workbenchElement(id) {
   195	  return document.getElementById(id);
   196	}
   197	
   198	function beginWorkbenchRequest() {
   199	  latestWorkbenchRequestId += 1;
   200	  return latestWorkbenchRequestId;
   201	}
   202	
   203	function isLatestWorkbenchRequest(requestId) {
   204	  return requestId === latestWorkbenchRequestId;
   205	}
   206	
   207	function setRequestStatus(message, tone = "neutral") {
   208	  const element = workbenchElement("workbench-request-status");
   209	  element.textContent = message;
   210	  element.dataset.tone = tone;
   211	}
   212	
   213	function setPacketSourceStatus(message) {
   214	  workbenchElement("workbench-packet-source-status").textContent = message;
   215	  persistWorkbenchPacketWorkspace();
   216	}
   217	
   218	function setResultMode(message) {
   219	  workbenchElement("workbench-result-mode").textContent = message;
   220	}
   221	
   222	function prettyJson(value) {
   223	  return JSON.stringify(value, null, 2);
   224	}
   225	
   226	function shortPath(path) {
   227	  if (!path) {
   228	    return "(none)";
   229	  }
   230	  const parts = String(path).split("/");
   231	  return parts[parts.length - 1] || String(path);
   232	}
   233	
   234	function cloneJson(value) {
   235	  return JSON.parse(JSON.stringify(value));
   236	}
   237	
   238	function normalizeRecentWorkbenchArchiveEntries(entries) {
   239	  if (!Array.isArray(entries)) {
   240	    return [];
   241	  }
   242	  return entries
   243	    .filter((entry) => entry && typeof entry === "object")
   244	    .map((entry) => ({
   245	      archive_dir: typeof entry.archive_dir === "string" ? entry.archive_dir : "",
   246	      manifest_path: typeof entry.manifest_path === "string" ? entry.manifest_path : "",
   247	      created_at_utc: typeof entry.created_at_utc === "string" ? entry.created_at_utc : "",
   248	      system_id: typeof entry.system_id === "string" ? entry.system_id : "unknown_system",
   249	      system_title: typeof entry.system_title === "string" ? entry.system_title : "",
   250	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
   251	      ready_for_spec_build: Boolean(entry.ready_for_spec_build),
   252	      selected_scenario_id: typeof entry.selected_scenario_id === "string" ? entry.selected_scenario_id : "",
   253	      selected_fault_mode_id: typeof entry.selected_fault_mode_id === "string" ? entry.selected_fault_mode_id : "",
   254	      has_workspace_handoff: Boolean(entry.has_workspace_handoff),
   255	      has_workspace_snapshot: Boolean(entry.has_workspace_snapshot),
   256	    }))
   257	    .filter((entry) => entry.manifest_path || entry.archive_dir);
   258	}
   259	
   260	function summarizeRecentWorkbenchArchive(entry) {
   261	  const state = entry.ready_for_spec_build ? "ready" : "blocked";
   262	  const scenario = entry.selected_scenario_id || "未选 scenario";
   263	  const faultMode = entry.selected_fault_mode_id || "未选 fault mode";
   264	  const workspace = entry.has_workspace_snapshot
   265	    ? "带工作区快照"
   266	    : (entry.has_workspace_handoff ? "仅带交接摘要" : "仅带 bundle");
   267	  return {
   268	    badge: state === "ready" ? "可恢复 / ready" : "可恢复 / blocked",
   269	    summary: `${scenario} / ${faultMode}`,
   270	    detail: `${workspace} / ${shortPath(entry.archive_dir || entry.manifest_path)}`,
   271	  };
   272	}
   273	
   274	function buildRecentWorkbenchArchiveEntryFromBundlePayload(payload) {
   275	  const archive = payload && payload.archive ? payload.archive : null;
   276	  const bundle = payload && payload.bundle ? payload.bundle : {};
   277	  if (!archive) {
   278	    return null;
   279	  }
   280	  return {
   281	    archive_dir: archive.archive_dir || "",
   282	    manifest_path: archive.manifest_json_path || "",
   283	    created_at_utc: archive.created_at_utc || "",
   284	    system_id: bundle.system_id || "unknown_system",
   285	    system_title: bundle.system_title || "",
   286	    bundle_kind: bundle.bundle_kind || "",
   287	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   288	    selected_scenario_id: bundle.selected_scenario_id || "",
   289	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   290	    has_workspace_handoff: Boolean(archive.workspace_handoff_json_path),
   291	    has_workspace_snapshot: Boolean(archive.workspace_snapshot_json_path),
   292	  };
   293	}
   294	
   295	function buildRecentWorkbenchArchiveEntryFromRestorePayload(payload) {
   296	  const bundle = payload && payload.bundle ? payload.bundle : {};
   297	  const manifest = payload && payload.manifest ? payload.manifest : {};
   298	  const files = manifest && typeof manifest.files === "object" ? manifest.files : {};
   299	  return {
   300	    archive_dir: payload.archive_dir || "",
   301	    manifest_path: payload.manifest_path || "",
   302	    created_at_utc: typeof manifest.created_at_utc === "string" ? manifest.created_at_utc : "",
   303	    system_id: bundle.system_id || "unknown_system",
   304	    system_title: bundle.system_title || "",
   305	    bundle_kind: bundle.bundle_kind || "",
   306	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   307	    selected_scenario_id: bundle.selected_scenario_id || "",
   308	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   309	    has_workspace_handoff: Boolean(files.workspace_handoff_json),
   310	    has_workspace_snapshot: Boolean(files.workspace_snapshot_json),
   311	  };
   312	}
   313	
   314	function upsertRecentWorkbenchArchiveEntry(entry) {
   315	  if (!entry || (!entry.manifest_path && !entry.archive_dir)) {
   316	    return;
   317	  }
   318	  const dedupeKey = entry.manifest_path || entry.archive_dir;
   319	  workbenchRecentArchives = [
   320	    entry,

exec
/bin/zsh -lc "nl -ba tests/test_workbench_state_of_world_bar.py | sed -n '1,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-06 — state-of-the-world status bar regression lock.
     2	
     3	Locks the contract for the top-of-/workbench advisory status bar that
     4	shows truth-engine SHA · recent e2e · adversarial · open known-issues.
     5	
     6	Per E11-00-PLAN row E11-06: read-only aggregation of evidence; the
     7	fields are *advisory* and never claim to be a live truth-engine
     8	reading. Verify both invariants — endpoint shape AND HTML/JS wiring —
     9	so future polish passes don't silently regress either side.
    10	"""
    11	
    12	from __future__ import annotations
    13	
    14	import http.client
    15	import json
    16	import threading
    17	from http.server import ThreadingHTTPServer
    18	from pathlib import Path
    19	
    20	import pytest
    21	
    22	from well_harness.demo_server import (
    23	    DemoRequestHandler,
    24	    workbench_state_of_world_payload,
    25	)
    26	
    27	
    28	REPO_ROOT = Path(__file__).resolve().parents[1]
    29	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    30	
    31	
    32	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    33	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    34	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    35	    thread.start()
    36	    return server, thread
    37	
    38	
    39	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    40	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    41	    connection.request("GET", path)
    42	    response = connection.getresponse()
    43	    return response.status, response.read().decode("utf-8")
    44	
    45	
    46	def _get_json(server: ThreadingHTTPServer, path: str) -> tuple[int, dict]:
    47	    status, body = _get(server, path)
    48	    return status, json.loads(body) if body else {}
    49	
    50	
    51	@pytest.fixture
    52	def server():
    53	    s, t = _start_demo_server()
    54	    try:
    55	        yield s
    56	    finally:
    57	        s.shutdown()
    58	        s.server_close()
    59	        t.join(timeout=2)
    60	
    61	
    62	# ─── 1. Payload contract (direct) ────────────────────────────────────
    63	
    64	
    65	def test_state_of_world_payload_has_required_fields() -> None:
    66	    payload = workbench_state_of_world_payload()
    67	    for field in (
    68	        "kind",
    69	        "truth_engine_sha",
    70	        "truth_engine_sha_source",
    71	        "recent_e2e_label",
    72	        "recent_e2e_source",
    73	        "adversarial_label",
    74	        "adversarial_source",
    75	        "open_known_issues_count",
    76	        "open_known_issues_source",
    77	        "last_executed_evidence",
    78	        "generated_at",
    79	    ):
    80	        assert field in payload, f"missing field: {field}"
    81	
    82	
    83	def test_state_of_world_kind_is_advisory() -> None:
    84	    """The bar is read-only and must NEVER claim to be a live truth-engine
    85	    reading. The 'advisory' kind is the contract."""
    86	    payload = workbench_state_of_world_payload()
    87	    assert payload["kind"] == "advisory"
    88	
    89	
    90	def test_state_of_world_open_issues_is_int() -> None:
    91	    payload = workbench_state_of_world_payload()
    92	    assert isinstance(payload["open_known_issues_count"], int)
    93	    assert payload["open_known_issues_count"] >= 0
    94	
    95	
    96	def test_state_of_world_truth_engine_sha_is_short() -> None:
    97	    """git rev-parse --short HEAD returns 7-12 chars for typical repos.
    98	    If git is missing, the function falls back to "unknown" — also OK."""
    99	    payload = workbench_state_of_world_payload()
   100	    sha = payload["truth_engine_sha"]
   101	    assert isinstance(sha, str) and sha
   102	    assert sha == "unknown" or 4 <= len(sha) <= 40
   103	
   104	
   105	def test_state_of_world_generated_at_is_iso() -> None:
   106	    payload = workbench_state_of_world_payload()
   107	    ts = payload["generated_at"]
   108	    assert isinstance(ts, str) and ts.endswith("Z")
   109	    assert "T" in ts
   110	
   111	
   112	# ─── 2. Live-served endpoint contract ────────────────────────────────
   113	
   114	
   115	def test_state_of_world_endpoint_returns_200(server) -> None:
   116	    status, body = _get_json(server, "/api/workbench/state-of-world")
   117	    assert status == 200
   118	    assert body.get("kind") == "advisory"
   119	
   120	
   121	# ─── 3. /workbench HTML carries the bar ──────────────────────────────
   122	
   123	
   124	def test_workbench_html_has_state_of_world_bar() -> None:
   125	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   126	    assert 'id="workbench-state-of-world-bar"' in html
   127	    assert 'data-status-kind="advisory"' in html
   128	
   129	
   130	@pytest.mark.parametrize(
   131	    "field",
   132	    [
   133	        "truth_engine_sha",
   134	        "recent_e2e_label",
   135	        "adversarial_label",
   136	        "open_known_issues_count",
   137	    ],
   138	)
   139	def test_workbench_html_bar_has_field_slot(field: str) -> None:
   140	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   141	    assert f'data-sow-value="{field}"' in html, f"missing bar slot: {field}"
   142	
   143	
   144	def test_workbench_html_bar_has_advisory_flag() -> None:
   145	    """The bar must visibly disclose its advisory nature so a presenter
   146	    or customer reading the line never mistakes it for a live truth-engine
   147	    reading."""
   148	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   149	    assert "advisory · not a live truth-engine reading" in html
   150	
   151	
   152	# ─── 4. JS hydration is wired to DOMContentLoaded ───────────────────
   153	
   154	
   155	def test_workbench_js_hydrate_state_of_world_bar_wired() -> None:
   156	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   157	    assert "function hydrateStateOfWorldBar" in js
   158	    assert "/api/workbench/state-of-world" in js
   159	    # Hooked into DOMContentLoaded alongside the existing init calls.
   160	    assert "hydrateStateOfWorldBar()" in js
   161	
   162	
   163	# ─── 5. Live-served /workbench includes the bar HTML ────────────────
   164	
   165	
   166	def test_workbench_route_serves_state_of_world_bar(server) -> None:
   167	    status, html = _get(server, "/workbench")
   168	    assert status == 200
   169	    assert 'id="workbench-state-of-world-bar"' in html
   170	    assert 'data-sow-value="truth_engine_sha"' in html
   171	    assert 'data-sow-value="recent_e2e_label"' in html
   172	    assert 'data-sow-value="adversarial_label"' in html
   173	    assert 'data-sow-value="open_known_issues_count"' in html
   174	
   175	
   176	# ─── 6. Truth-engine red line check ─────────────────────────────────
   177	
   178	
   179	def test_state_of_world_endpoint_is_read_only(server) -> None:
   180	    """A POST to /api/workbench/state-of-world must NOT be silently
   181	    accepted — the endpoint is GET-only by design. Either 404 or 405
   182	    is acceptable; what's NOT acceptable is a 200 that mutates state."""
   183	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
   184	    connection.request(
   185	        "POST",
   186	        "/api/workbench/state-of-world",
   187	        body=b"{}",
   188	        headers={"Content-Type": "application/json"},
   189	    )
   190	    response = connection.getresponse()
   191	    response.read()
   192	    assert response.status in (404, 405), (
   193	        f"state-of-world POST returned {response.status}; must be 404/405"
   194	    )

exec
/bin/zsh -lc 'rg -n "state[-_]of[-_]world|hydrateStateOfWorldBar|WORKBENCH_STATE_OF_WORLD_PATH|workbench_state_of_world_payload|_truth_engine_short_sha|_read_recent_evidence_lines|_open_known_issues_count" src/well_harness/demo_server.py src/well_harness/static/workbench.js tests/test_workbench_state_of_world_bar.py docs/coordination/qa_report.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_state_of_world_bar.py:24:    workbench_state_of_world_payload,
tests/test_workbench_state_of_world_bar.py:65:def test_state_of_world_payload_has_required_fields() -> None:
tests/test_workbench_state_of_world_bar.py:66:    payload = workbench_state_of_world_payload()
tests/test_workbench_state_of_world_bar.py:83:def test_state_of_world_kind_is_advisory() -> None:
tests/test_workbench_state_of_world_bar.py:86:    payload = workbench_state_of_world_payload()
tests/test_workbench_state_of_world_bar.py:90:def test_state_of_world_open_issues_is_int() -> None:
tests/test_workbench_state_of_world_bar.py:91:    payload = workbench_state_of_world_payload()
tests/test_workbench_state_of_world_bar.py:96:def test_state_of_world_truth_engine_sha_is_short() -> None:
tests/test_workbench_state_of_world_bar.py:99:    payload = workbench_state_of_world_payload()
tests/test_workbench_state_of_world_bar.py:105:def test_state_of_world_generated_at_is_iso() -> None:
tests/test_workbench_state_of_world_bar.py:106:    payload = workbench_state_of_world_payload()
tests/test_workbench_state_of_world_bar.py:115:def test_state_of_world_endpoint_returns_200(server) -> None:
tests/test_workbench_state_of_world_bar.py:116:    status, body = _get_json(server, "/api/workbench/state-of-world")
tests/test_workbench_state_of_world_bar.py:124:def test_workbench_html_has_state_of_world_bar() -> None:
tests/test_workbench_state_of_world_bar.py:126:    assert 'id="workbench-state-of-world-bar"' in html
tests/test_workbench_state_of_world_bar.py:155:def test_workbench_js_hydrate_state_of_world_bar_wired() -> None:
tests/test_workbench_state_of_world_bar.py:157:    assert "function hydrateStateOfWorldBar" in js
tests/test_workbench_state_of_world_bar.py:158:    assert "/api/workbench/state-of-world" in js
tests/test_workbench_state_of_world_bar.py:160:    assert "hydrateStateOfWorldBar()" in js
tests/test_workbench_state_of_world_bar.py:166:def test_workbench_route_serves_state_of_world_bar(server) -> None:
tests/test_workbench_state_of_world_bar.py:169:    assert 'id="workbench-state-of-world-bar"' in html
tests/test_workbench_state_of_world_bar.py:179:def test_state_of_world_endpoint_is_read_only(server) -> None:
tests/test_workbench_state_of_world_bar.py:180:    """A POST to /api/workbench/state-of-world must NOT be silently
tests/test_workbench_state_of_world_bar.py:186:        "/api/workbench/state-of-world",
tests/test_workbench_state_of_world_bar.py:193:        f"state-of-world POST returned {response.status}; must be 404/405"
src/well_harness/demo_server.py:77:WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
src/well_harness/demo_server.py:229:        if parsed.path == WORKBENCH_STATE_OF_WORLD_PATH:
src/well_harness/demo_server.py:235:            self._send_json(200, workbench_state_of_world_payload())
src/well_harness/demo_server.py:1314:def _truth_engine_short_sha() -> str:
src/well_harness/demo_server.py:1334:def _read_recent_evidence_lines() -> dict:
src/well_harness/demo_server.py:1365:def _open_known_issues_count() -> int:
src/well_harness/demo_server.py:1380:def workbench_state_of_world_payload() -> dict:
src/well_harness/demo_server.py:1387:    evidence = _read_recent_evidence_lines()
src/well_harness/demo_server.py:1390:        "truth_engine_sha": _truth_engine_short_sha(),
src/well_harness/demo_server.py:1396:        "open_known_issues_count": _open_known_issues_count(),
src/well_harness/static/workbench.js:3960:// Reads /api/workbench/state-of-world and writes the four advisory
src/well_harness/static/workbench.js:3964:const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";
src/well_harness/static/workbench.js:3966:async function hydrateStateOfWorldBar() {
src/well_harness/static/workbench.js:3967:  const bar = document.getElementById("workbench-state-of-world-bar");
src/well_harness/static/workbench.js:3972:    const response = await fetch(WORKBENCH_STATE_OF_WORLD_PATH, {
src/well_harness/static/workbench.js:4004:  void hydrateStateOfWorldBar();

exec
/bin/zsh -lc "nl -ba docs/coordination/qa_report.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# QA Report
     2	
     3	<!-- AUTO-SYNCED QA REPORT SNAPSHOT START -->
     4	## 当前自动同步 QA 基线
     5	
     6	- 结论：PASS；当前稳定基线由 GitHub-backed validation evidence 支撑。
     7	- 当前阶段：`P43 Control Logic Workbench end-to-end milestone`
     8	- 当前已验证 Plan：`P43-02-00 P43-02 Batch — Orchestrator + Document Pipeline + Freeze Gate`
     9	- 最近成功执行证据：`E11-04 PR #20 merged (annotation vocabulary upgrade, Tier-B P3 APPROVE_WITH_NITS) — 2026-04-26`
    10	- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`
    11	- 当前 Opus 状态：`当前无需 Opus 审查`
    12	- Open Gap 数量：`0`
    13	- 当前证据模式：`repo-doc fallback mode`
    14	- 证据模式说明：共享 Notion 数据库与活跃控制面页面当前不可达；当前快照由 repo freeze packet 与 handoff docs 恢复。
    15	- 当前 QA 摘要：`PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
    16	- 当前运行摘要：`Focused control-plane maintenance run passed. Carried forward the stronger shared validation baseline: 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
    17	
    18	## 当前执行规则
    19	
    20	- GitHub / repo 是实现真值；Notion 是控制面；`controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。
    21	- `runner.py` / `SimulationRunner` 继续承担运行时编排职责；不要把 orchestration 重新塞回 controller truth、UI 或持久化层。
    22	- 新系统 truth 只能通过显式 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。
    23	- FlyByWire / A320 资料只作为知识参考和设计启发，不直接复制成项目代码真值。
    24	- 一个切片只有在代码修改、目标验证命令、`gsd_notion_sync.py run` 写回，以及 `prepare-opus-review` 复核全部完成后，才算真正完成。
    25	
    26	- `manual browser QA` 不再是当前审批规则；相关历史记录只保留为 presenter guidance / 历史上下文。
    27	
    28	## 当前证据入口
    29	
    30	- [GitHub Repo](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
    31	- [GitHub Actions](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)
    32	- [Notion 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)
    33	
    34	## 历史 QA 记录说明
    35	
    36	- 下方按 Round 保存的 QA 记录保留不删，但它们不是当前冻结基线。
    37	<!-- AUTO-SYNCED QA REPORT SNAPSHOT END -->
    38	
    39	## 当前用途
    40	
    41	- 这个文件现在只保留“当前自动同步 QA 基线 + 当前证据入口”。
    42	- 当前 QA 真值以顶部自动同步快照、GitHub Actions 和 Notion 控制塔为准。
    43	
    44	## 历史归档
    45	
    46	- 旧 Round 的 QA 正文已迁到 [archive/qa-report-history.md](./archive/qa-report-history.md)。
    47	- 需要复盘以前每轮的细节验证过程、浏览器边界或旧 blocker 时，再进入 archive 文件查看。
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1290,1425p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1290	    )
  1291	    return summaries[:limit]
  1292	
  1293	
  1294	def workbench_bootstrap_payload() -> dict:
  1295	    return {
  1296	        "template_packet": intake_template_payload(),
  1297	        "reference_packet": reference_workbench_packet_payload(),
  1298	        "default_archive_root": str(default_workbench_archive_root()),
  1299	        "recent_archives": recent_workbench_archive_summaries(),
  1300	        "explain_runtime": build_explain_runtime_payload(),
  1301	    }
  1302	
  1303	
  1304	def workbench_recent_archives_payload() -> dict:
  1305	    return {
  1306	        "default_archive_root": str(default_workbench_archive_root()),
  1307	        "recent_archives": recent_workbench_archive_summaries(),
  1308	    }
  1309	
  1310	
  1311	# ─── E11-06: state-of-the-world helpers ──────────────────────────────
  1312	
  1313	
  1314	def _truth_engine_short_sha() -> str:
  1315	    """Return the short HEAD SHA of the working repo, or 'unknown' if
  1316	    git is unavailable. The bar copy must never crash the page."""
  1317	    import subprocess
  1318	    try:
  1319	        repo_root = Path(__file__).resolve().parents[2]
  1320	        result = subprocess.run(
  1321	            ["git", "rev-parse", "--short", "HEAD"],
  1322	            cwd=str(repo_root),
  1323	            capture_output=True,
  1324	            text=True,
  1325	            timeout=2,
  1326	        )
  1327	        if result.returncode == 0:
  1328	            return result.stdout.strip() or "unknown"
  1329	    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
  1330	        pass
  1331	    return "unknown"
  1332	
  1333	
  1334	def _read_recent_evidence_lines() -> dict:
  1335	    """Parse the most-recent evidence stamp out of the coordination
  1336	    qa_report. Returns three optional fields. Falls back to empty
  1337	    strings if the file is missing or malformed; the bar then renders
  1338	    "—" instead of crashing."""
  1339	    repo_root = Path(__file__).resolve().parents[2]
  1340	    qa_report = repo_root / "docs" / "coordination" / "qa_report.md"
  1341	    out = {
  1342	        "recent_e2e_label": "",
  1343	        "adversarial_label": "",
  1344	        "last_executed_evidence": "",
  1345	    }
  1346	    try:
  1347	        text = qa_report.read_text(encoding="utf-8")
  1348	    except (FileNotFoundError, OSError):
  1349	        return out
  1350	    # Match e.g. "175 tests OK"
  1351	    m = re.search(r"(\d+)\s*tests?\s*OK", text)
  1352	    if m:
  1353	        out["recent_e2e_label"] = f"{m.group(1)} tests OK"
  1354	    # Match e.g. "8/8 shared validation checks pass"
  1355	    m = re.search(r"(\d+/\d+)\s*shared validation", text)
  1356	    if m:
  1357	        out["adversarial_label"] = f"{m.group(1)} shared validation pass"
  1358	    # Match the most recent execution evidence backtick block
  1359	    m = re.search(r"最近成功执行证据：`([^`]+)`", text)
  1360	    if m:
  1361	        out["last_executed_evidence"] = m.group(1)
  1362	    return out
  1363	
  1364	
  1365	def _open_known_issues_count() -> int:
  1366	    """Count files in docs/known-issues/ (or /known_issues/). Returns 0
  1367	    if the directory does not exist."""
  1368	    repo_root = Path(__file__).resolve().parents[2]
  1369	    for candidate in ("known-issues", "known_issues"):
  1370	        directory = repo_root / "docs" / candidate
  1371	        if directory.is_dir():
  1372	            return sum(
  1373	                1
  1374	                for entry in directory.iterdir()
  1375	                if entry.is_file() and entry.suffix in {".md", ".txt"}
  1376	            )
  1377	    return 0
  1378	
  1379	
  1380	def workbench_state_of_world_payload() -> dict:
  1381	    """E11-06: aggregate read-only fields for the /workbench status bar.
  1382	
  1383	    Honest about its advisory nature: every field has a `source` label
  1384	    so the user can trace where a given value came from, and the
  1385	    `kind: "advisory"` flag is the contract that this is NOT a live
  1386	    truth-engine reading."""
  1387	    evidence = _read_recent_evidence_lines()
  1388	    return {
  1389	        "kind": "advisory",
  1390	        "truth_engine_sha": _truth_engine_short_sha(),
  1391	        "truth_engine_sha_source": "git rev-parse --short HEAD",
  1392	        "recent_e2e_label": evidence["recent_e2e_label"] or "—",
  1393	        "recent_e2e_source": "docs/coordination/qa_report.md",
  1394	        "adversarial_label": evidence["adversarial_label"] or "—",
  1395	        "adversarial_source": "docs/coordination/qa_report.md",
  1396	        "open_known_issues_count": _open_known_issues_count(),
  1397	        "open_known_issues_source": "docs/known-issues/ (file count)",
  1398	        "last_executed_evidence": evidence["last_executed_evidence"] or "—",
  1399	        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
  1400	    }
  1401	
  1402	
  1403	def _optional_request_float_list(
  1404	    payload: dict,
  1405	    field_name: str,
  1406	    *,
  1407	    default: tuple[float, ...],
  1408	) -> tuple[tuple[float, ...], dict | None]:
  1409	    raw_value = payload.get(field_name)
  1410	    if raw_value is None:
  1411	        return default, None
  1412	    if not isinstance(raw_value, list) or not raw_value:
  1413	        return default, {
  1414	            "error": "invalid_sensitivity_sweep_request",
  1415	            "field": field_name,
  1416	            "message": f"{field_name} must be a non-empty list of finite numbers.",
  1417	        }
  1418	
  1419	    normalized: list[float] = []
  1420	    for item in raw_value:
  1421	        if isinstance(item, bool):
  1422	            return default, {
  1423	                "error": "invalid_sensitivity_sweep_request",
  1424	                "field": field_name,
  1425	                "message": f"{field_name} must be numeric.",

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3940,4025p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3940	      button.disabled = false;
  3941	    }
  3942	  }
  3943	}
  3944	
  3945	function installWowStarters() {
  3946	  const buttons = document.querySelectorAll(
  3947	    '.workbench-wow-run-button[data-wow-action="run"]',
  3948	  );
  3949	  buttons.forEach((btn) => {
  3950	    btn.addEventListener("click", () => {
  3951	      const wowId = btn.getAttribute("data-wow-id");
  3952	      if (wowId && WOW_SCENARIOS[wowId]) {
  3953	        void runWowScenario(wowId);
  3954	      }
  3955	    });
  3956	  });
  3957	}
  3958	
  3959	// E11-06 (2026-04-26): hydrate the state-of-the-world status bar.
  3960	// Reads /api/workbench/state-of-world and writes the four advisory
  3961	// fields into the bar. Falls back to "—" so the page never shows a
  3962	// half-broken bar. Failures are silent (the bar starts with "…"
  3963	// placeholders so there is no flash of the wrong content).
  3964	const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";
  3965	
  3966	async function hydrateStateOfWorldBar() {
  3967	  const bar = document.getElementById("workbench-state-of-world-bar");
  3968	  if (!bar) {
  3969	    return;
  3970	  }
  3971	  try {
  3972	    const response = await fetch(WORKBENCH_STATE_OF_WORLD_PATH, {
  3973	      method: "GET",
  3974	      headers: { Accept: "application/json" },
  3975	    });
  3976	    if (!response.ok) {
  3977	      return;
  3978	    }
  3979	    const payload = await response.json();
  3980	    const writeField = (key, value) => {
  3981	      const slot = bar.querySelector(`[data-sow-value="${key}"]`);
  3982	      if (slot) {
  3983	        slot.textContent =
  3984	          value === null || value === undefined || value === ""
  3985	            ? "—"
  3986	            : String(value);
  3987	      }
  3988	    };
  3989	    writeField("truth_engine_sha", payload.truth_engine_sha);
  3990	    writeField("recent_e2e_label", payload.recent_e2e_label);
  3991	    writeField("adversarial_label", payload.adversarial_label);
  3992	    writeField("open_known_issues_count", payload.open_known_issues_count);
  3993	  } catch (_err) {
  3994	    // Silent — the bar already shows "…" placeholders, which renders as
  3995	    // a benign "still loading" state instead of a broken half-page.
  3996	  }
  3997	}
  3998	
  3999	window.addEventListener("DOMContentLoaded", () => {
  4000	  bootWorkbenchShell();
  4001	  installViewModeHandlers();
  4002	  installFeedbackModeAffordance();
  4003	  installWowStarters();
  4004	  void hydrateStateOfWorldBar();
  4005	
  4006	  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  4007	  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  4008	  // NOT contain bundle elements like #workbench-packet-json,
  4009	  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  4010	  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  4011	  // bundle DOM exists and would throw "Cannot read properties of null" on the
  4012	  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  4013	  // skip bundle boot entirely. This script is shared between both pages.
  4014	  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  4015	  if (!onBundlePage) {
  4016	    return;
  4017	  }
  4018	
  4019	  installToolbarHandlers();
  4020	  updateWorkflowUI();
  4021	  if (checkUrlIntakeParam()) {
  4022	    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
  4023	    if (bundleBtn) {
  4024	      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
  4025	      bundleBtn.click();

exec
/bin/zsh -lc "rg -n \"do_POST|POST|WORKBENCH_STATE_OF_WORLD_PATH|send_error\\(|405|404\" src/well_harness/demo_server.py | sed -n '1,200p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
68:SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
77:WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
196:# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
229:        if parsed.path == WORKBENCH_STATE_OF_WORLD_PATH:
285:        self._send_json(404, {"error": "not_found"})
287:    def do_POST(self):
293:            SYSTEM_SNAPSHOT_POST_PATH,
305:            self._send_json(404, {"error": "not_found"})
415:        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
426:                self._send_json(404, result)
586:            self._send_json(404, {"error": "not_found"})
589:            self._send_json(404, {"error": "not_found"})

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '260,330p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   260	
   261	        relative_path = unquote(parsed.path.lstrip("/"))
   262	        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
   263	            self._serve_static(relative_path)
   264	            return
   265	
   266	        # P19.8: Hardware schema discovery
   267	        if parsed.path == HARDWARE_SCHEMA_PATH:
   268	            system_id = parse_qs(parsed.query).get("system_id", ["thrust-reverser"])[0]
   269	            self._handle_hardware_schema(system_id=system_id)
   270	            return
   271	
   272	        if parsed.path == FANTUI_LOG_PATH:
   273	            # records() is internally locked; the copy it returns is
   274	            # self-contained so JSON serialization can run unlocked.
   275	            recs = _FANTUI_SYSTEM.records()
   276	            self._send_json(200, recs)
   277	            return
   278	
   279	        if parsed.path == FANTUI_STATE_PATH:
   280	            # Atomic snapshot — one lock acquisition covers all fields
   281	            # so callers don't observe torn state.
   282	            self._send_json(200, _FANTUI_SYSTEM.snapshot())
   283	            return
   284	
   285	        self._send_json(404, {"error": "not_found"})
   286	
   287	    def do_POST(self):
   288	        parsed = urlparse(self.path)
   289	        if parsed.path not in {
   290	            "/api/demo",
   291	            "/api/lever-snapshot",
   292	            "/api/timeline-simulate",
   293	            SYSTEM_SNAPSHOT_POST_PATH,
   294	            WORKBENCH_BUNDLE_PATH,
   295	            WORKBENCH_REPAIR_PATH,
   296	            WORKBENCH_ARCHIVE_RESTORE_PATH,
   297	            DIAGNOSIS_RUN_PATH,
   298	            MONTE_CARLO_RUN_PATH,
   299	            HARDWARE_SCHEMA_PATH,
   300	            SENSITIVITY_SWEEP_PATH,
   301	            FANTUI_TICK_PATH,
   302	            FANTUI_RESET_PATH,
   303	            FANTUI_SET_VDT_PATH,
   304	        }:
   305	            self._send_json(404, {"error": "not_found"})
   306	            return
   307	
   308	        try:
   309	            content_length = int(self.headers.get("Content-Length", "0") or "0")
   310	        except ValueError:
   311	            self._send_json(400, {"error": "invalid_content_length"})
   312	            return
   313	
   314	        # Guard: reject oversized payloads before reading
   315	        if content_length and content_length > _MAX_DOCUMENT_BYTES:
   316	            self._send_json(413, {"error": "payload_too_large", "message": f"Request body exceeds maximum of {_MAX_DOCUMENT_BYTES} bytes."})
   317	            return
   318	
   319	        # Guard: enforce Content-Type whitelist (defense-in-depth; browser enforces this too)
   320	        content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
   321	        allowed_types = {"application/json"}
   322	        if content_type and content_type not in allowed_types:
   323	            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json."})
   324	            return
   325	
   326	        try:
   327	            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
   328	            request_payload = json.loads(body)
   329	        except (UnicodeDecodeError, json.JSONDecodeError):
   330	            self._send_json(400, {"error": "invalid_json"})

codex
实现主体已经读完。现在在核对两件事：一是 `_source` 字段是不是始终诚实，二是测试是否真正把这些诚实性和失败兜底锁住，而不是只测“字段存在”。
exec
/bin/zsh -lc "find docs -maxdepth 2 \\( -type d -name 'known-issues' -o -type d -name 'known_issues' \\) -print" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
exec
/bin/zsh -lc "python - <<'PY'
from well_harness.demo_server import workbench_state_of_world_payload
import json
print(json.dumps(workbench_state_of_world_payload(), ensure_ascii=False, indent=2))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_state_of_world_bar.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 1885ms:
...............                                                          [100%]
15 passed in 1.67s

codex
本地目标测试已经起跑，`python` 不在 PATH，但这不影响结论，我会用 `python3` 做 payload smoke 和 HTTP probe。
exec
/bin/zsh -lc "python3 - <<'PY'
from well_harness.demo_server import workbench_state_of_world_payload
import json
print(json.dumps(workbench_state_of_world_payload(), ensure_ascii=False, indent=2))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
text = Path('docs/coordination/qa_report.md').read_text(encoding='utf-8')
import re
print('recent_e2e:', re.search(r'(\\d+)\\s*tests?\\s*OK', text).group(0))
print('adversarial_match:', re.search(r'(\\d+/\\d+)\\s*shared validation', text).group(0))
print('last_evidence:', re.search(r'最近成功执行证据："'`([''^`]+)`'"', text).group(1))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
recent_e2e: 175 tests OK
adversarial_match: 8/8 shared validation
last_evidence: E11-04 PR #20 merged (annotation vocabulary upgrade, Tier-B P3 APPROVE_WITH_NITS) — 2026-04-26

 exited 1 in 203ms:
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name 'workbench_state_of_world_payload' from 'well_harness.demo_server' (/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py)

codex
我碰到一个需要核清的验证风险：裸 `python3` 导入到的是另一份 `ai-fantui-logicmvp` 工作副本，不是当前 review 的这棵树。这不一定影响 live HTTP probe，但它会直接影响“这些测试到底测的是哪份代码”的可信度，我正在确认。
exec
/bin/zsh -lc 'pwd && realpath . && realpath src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py

exec
/bin/zsh -lc 'ls -la' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
total 512
-rw-r--r--@  1 Zhuanz  staff       0 Apr 18 23:57 , v.get(type), v.get(v.get(type), {}))
" 2>&1 | grep -v "Warning\|urllib3\|LIBRE_SSL\|https_proxy\|http_proxy\|Credit\|limit\|resets\|plus\|active\|kogamishiny\|ksnbdajdjddkdd\|mahbubaamyrss\|paauhtgaiah\|picassoer\|ramaiamandhab\|sajihsmipoal\|Switch"
drwxr-xr-x@ 34 Zhuanz  staff    1088 Apr 26 01:13 .
drwxr-xr-x@  6 Zhuanz  staff     192 Apr 19 00:08 ..
drwxr-xr-x@  5 Zhuanz  staff     160 Apr 25 14:12 .claude
-rw-r--r--@  1 Zhuanz  staff    2428 Apr 18 23:57 .codex_analysis_prompt.txt
-rw-r--r--@  1 Zhuanz  staff    1969 Apr 18 23:57 .codex_fix_prompt.txt
-rw-r--r--@  1 Zhuanz  staff    1928 Apr 18 23:57 .codex_p0_fix_review.txt
-rw-r--r--@  1 Zhuanz  staff    1637 Apr 18 23:57 .codex_p1_review.txt
drwxr-xr-x@ 16 Zhuanz  staff     512 Apr 26 02:15 .git
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 18 23:57 .github
-rw-r--r--@  1 Zhuanz  staff     334 Apr 25 14:12 .gitignore
drwxr-xr-x@ 16 Zhuanz  staff     512 Apr 25 22:02 .planning
drwxr-xr-x@  6 Zhuanz  staff     192 Apr 25 13:00 .pytest_cache
drwxr-xr-x@  8 Zhuanz  staff     256 Apr 26 01:13 .venv
-rw-r--r--@  1 Zhuanz  staff    3424 Apr 18 23:57 AGENTS.md
-rw-r--r--@  1 Zhuanz  staff   34221 Apr 25 14:12 README.md
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 25 14:12 archive
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 25 12:59 artifacts
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 25 14:12 audit
drwxr-xr-x@  4 Zhuanz  staff     128 Apr 18 23:57 config
drwxr-xr-x@  4 Zhuanz  staff     128 Apr 25 14:12 data
drwxr-xr-x@ 25 Zhuanz  staff     800 Apr 25 14:12 docs
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 25 14:12 outputs
-rw-r--r--@  1 Zhuanz  staff    1430 Apr 25 14:12 pyproject.toml
drwxr-xr-x@ 17 Zhuanz  staff     544 Apr 25 14:12 runs
drwxr-xr-x@  3 Zhuanz  staff      96 Apr 25 14:12 schemas
drwxr-xr-x@  8 Zhuanz  staff     256 Apr 26 01:47 scripts
drwxr-xr-x@  4 Zhuanz  staff     128 Apr 25 23:56 src
drwxr-xr-x@  4 Zhuanz  staff     128 Apr 25 14:12 templates
drwxr-xr-x@ 84 Zhuanz  staff    2688 Apr 26 02:09 tests
drwxr-xr-x@  5 Zhuanz  staff     160 Apr 25 14:12 tickets
drwxr-xr-x@ 32 Zhuanz  staff    1024 Apr 26 01:46 tools
drwxr-xr-x@  4 Zhuanz  staff     128 Apr 25 14:12 uploads
-rw-r--r--@  1 Zhuanz  staff  196425 Apr 26 01:13 uv.lock

exec
/bin/zsh -lc "rg -n \"pythonpath|PYTHONPATH|tool.pytest|pytest.ini|testpaths|src\" pyproject.toml pytest.ini setup.cfg tox.ini conftest.py -g '"'!**/.venv/**'"'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: pytest.ini: No such file or directory (os error 2)
rg: setup.cfg: No such file or directory (os error 2)
rg: tox.ini: No such file or directory (os error 2)
rg: conftest.py: No such file or directory (os error 2)
pyproject.toml:27:"" = "src"
pyproject.toml:30:where = ["src"]
pyproject.toml:32:[tool.pytest.ini_options]
pyproject.toml:36:testpaths = ["tests"]
pyproject.toml:37:# Make bare `pytest` work without requiring PYTHONPATH=src:. on the caller:
pyproject.toml:38:# - src: well_harness package imports
pyproject.toml:40:pythonpath = ["src", "."]

exec
/bin/zsh -lc "python3 - <<'PY'
import sys
import well_harness
import well_harness.demo_server as ds
print('well_harness:', well_harness.__file__)
print('demo_server:', ds.__file__)
print('sys.path[0:8]=', sys.path[:8])
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 115ms:
well_harness: /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/__init__.py
demo_server: /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py
sys.path[0:8]= ['', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python39.zip', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload', '/Users/Zhuanz/Library/Python/3.9/lib/python/site-packages', '/Users/Zhuanz/Desktop/cfd-harness-unified/src', '/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages']

exec
/bin/zsh -lc "nl -ba pyproject.toml | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	[build-system]
     2	requires = ["setuptools>=68"]
     3	build-backend = "setuptools.build_meta"
     4	
     5	[project]
     6	name = "well-harness"
     7	version = "0.1.0"
     8	description = "Engineering workbench for aviation control logic: requirements to runtime verification evidence"
     9	readme = "README.md"
    10	requires-python = ">=3.9"
    11	# Runtime stays stdlib-only — demo_server.py imports no third-party packages.
    12	# Third-party deps land in [project.optional-dependencies] groups below so
    13	# they can be installed explicitly for test/tooling lanes.
    14	
    15	[project.optional-dependencies]
    16	# Install with: pip install -e '.[dev]'
    17	# Covers the pytest default lane + the schema-validation scripts under tools/.
    18	dev = [
    19	    "pytest>=8.0",
    20	    "pytest-subtests>=0.11",
    21	    "jsonschema>=4.17",
    22	    "numpy>=1.24",
    23	    "pyyaml>=6.0",
    24	]
    25	
    26	[tool.setuptools.package-dir]
    27	"" = "src"
    28	
    29	[tool.setuptools.packages.find]
    30	where = ["src"]
    31	
    32	[tool.pytest.ini_options]
    33	# Default CI lane excludes e2e; opt-in with: pytest -m e2e (or pytest -m "e2e or not e2e")
    34	addopts = "-m 'not e2e'"
    35	# Constrain discovery to tests/ so shelved archive trees are never collected.
    36	testpaths = ["tests"]
    37	# Make bare `pytest` work without requiring PYTHONPATH=src:. on the caller:
    38	# - src: well_harness package imports
    39	# - . (repo root): tools.* and tests.* imports from a few cross-file suites
    40	pythonpath = ["src", "."]
    41	markers = [
    42	    "e2e: opt-in end-to-end tests that boot demo_server on :8799 (run with -m e2e)",
    43	]

codex
我已经把一个潜在假阳性源头定位出来了：这台机器裸 `python3` 会串到另一份同名 repo，所以后续 live probe 我会强制 `PYTHONPATH=src:.` 绑定当前 worktree，避免把别处的 `demo_server.py` 当成本次 PR 的证据。
exec
/bin/zsh -lc "PYTHONPATH=src:. python3 - <<'PY'
from well_harness import demo_server as ds
import json
print('demo_server_file=', ds.__file__)
payload = ds.workbench_state_of_world_payload()
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "PYTHONPATH=src:. python3 - <<'PY'
from well_harness.demo_server import DemoRequestHandler
from http.server import ThreadingHTTPServer
import threading, http.client, json
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('GET', '/api/workbench/state-of-world')
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    payload = json.loads(body)
    print('GET_STATUS', resp.status)
    print('GET_KIND', payload.get('kind'))
    print('GET_SHA', payload.get('truth_engine_sha'))
    print('GET_RECENT_E2E', payload.get('recent_e2e_label'))
    print('GET_ADVERSARIAL', payload.get('adversarial_label'))
    print('GET_OPEN_ISSUES', payload.get('open_known_issues_count'))
    print('GET_EVIDENCE', payload.get('last_executed_evidence'))
    conn.close()

    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('POST', '/api/workbench/state-of-world', body=b'{}', headers={'Content-Type': 'application/json'})
    resp = conn.getresponse()
    print('POST_STATUS', resp.status)
    print('POST_BODY', resp.read().decode('utf-8'))
    conn.close()

    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('GET', '/api/workbench/state-of-world')
    resp = conn.getresponse()
    body2 = resp.read().decode('utf-8')
    payload2 = json.loads(body2)
    print('GET2_STATUS', resp.status)
    print('GET2_RECENT_E2E', payload2.get('recent_e2e_label'))
    print('GET2_ADVERSARIAL', payload2.get('adversarial_label'))
    print('GET2_OPEN_ISSUES', payload2.get('open_known_issues_count'))
    print('GET2_SHA', payload2.get('truth_engine_sha'))
    print('STABLE_NON_TIMESTAMP', {
        'kind': payload.get('kind') == payload2.get('kind'),
        'sha': payload.get('truth_engine_sha') == payload2.get('truth_engine_sha'),
        'recent_e2e': payload.get('recent_e2e_label') == payload2.get('recent_e2e_label'),
        'adversarial': payload.get('adversarial_label') == payload2.get('adversarial_label'),
        'open_issues': payload.get('open_known_issues_count') == payload2.get('open_known_issues_count'),
        'evidence': payload.get('last_executed_evidence') == payload2.get('last_executed_evidence'),
    })
    conn.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 103ms:
 succeeded in 611ms:
GET_STATUS 200
GET_KIND advisory
GET_SHA 166d8d5
GET_RECENT_E2E 175 tests OK
GET_ADVERSARIAL 8/8 shared validation pass
GET_OPEN_ISSUES 0
GET_EVIDENCE E11-04 PR #20 merged (annotation vocabulary upgrade, Tier-B P3 APPROVE_WITH_NITS) — 2026-04-26
POST_STATUS 404
POST_BODY {"error": "not_found"}
GET2_STATUS 200
GET2_RECENT_E2E 175 tests OK
GET2_ADVERSARIAL 8/8 shared validation pass
GET2_OPEN_ISSUES 0
GET2_SHA 166d8d5
STABLE_NON_TIMESTAMP {'kind': True, 'sha': True, 'recent_e2e': True, 'adversarial': True, 'open_issues': True, 'evidence': True}

codex
我在对照实现和口头合同时发现了一个边界点：payload 里多带了 `last_executed_evidence`，但它不像另外四个 advisory 值那样有对应 `_source` sibling。我先看一下 phase inventory 是否把它列为正式合同字段，避免把“额外调试信息”误判成接口违约。
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11-06 Surface Inventory — state-of-the-world status bar
     2	
     3	> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
     4	
     5	## Surface diff inventory
     6	
     7	| # | Surface | Type | Anchor | Notes |
     8	|---|---|---|---|---|
     9	| 1 | Section eyebrow `state of world` | [ANCHORED] | `workbench.html` `#workbench-state-of-world-bar` (NEW) | Section identifier. |
    10	| 2 | Field label `truth-engine SHA` | [ANCHORED] | `data-sow-field="truth_engine_sha"` | Sourced from `git rev-parse --short HEAD`. |
    11	| 3 | Field label `recent e2e` | [ANCHORED] | `data-sow-field="recent_e2e"` | Sourced from `docs/coordination/qa_report.md`. |
    12	| 4 | Field label `adversarial` | [ANCHORED] | `data-sow-field="adversarial"` | Sourced from `docs/coordination/qa_report.md`. |
    13	| 5 | Field label `open issues` | [ANCHORED] | `data-sow-field="known_issues"` | Sourced from `docs/known-issues/` file count. |
    14	| 6-9 | 4 placeholder values `…` | [ANCHORED] | `data-sow-value="…"` slots | Replaced by JS hydration. |
    15	| 10 | Advisory flag `advisory · not a live truth-engine reading` | [ANCHORED] | trailing `.workbench-sow-flag` | Honesty contract — bar is NEVER a live truth-engine reading. |
    16	
    17	## Tier-trigger evaluation
    18	
    19	Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
    20	
    21	> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
    22	
    23	- **copy_diff_lines** = 10 → ≥ 10 ✓
    24	- **[REWRITE/DELETE] count** = 0 → < 3
    25	
    26	Threshold not met (zero rewrites — this is a NEW section). → **Tier-B** (1-persona review).
    27	
    28	E11-00-PLAN row E11-06 row 277 explicitly says "YES Codex (新 API 调用 / 状态聚合)". Tier-B with full 1-persona review honors that.
    29	
    30	> **Verdict: Tier-B**. Persona = **P4 (V&V Engineer)** — round-robin successor of E11-04's P3, AND content-fit: this introduces a new endpoint (`/api/workbench/state-of-world`) with read-only contract that V&V should validate (status codes, payload shape, idempotency, no truth-engine mutation).
    31	
    32	## Endpoint contract (locked by tests)
    33	
    34	`GET /api/workbench/state-of-world` returns 200 with:
    35	
    36	```json
    37	{
    38	  "kind": "advisory",
    39	  "truth_engine_sha": "<git short sha>" | "unknown",
    40	  "truth_engine_sha_source": "git rev-parse --short HEAD",
    41	  "recent_e2e_label": "<X tests OK>" | "—",
    42	  "recent_e2e_source": "docs/coordination/qa_report.md",
    43	  "adversarial_label": "<X/X shared validation pass>" | "—",
    44	  "adversarial_source": "docs/coordination/qa_report.md",
    45	  "open_known_issues_count": <int >= 0>,
    46	  "open_known_issues_source": "docs/known-issues/ (file count)",
    47	  "last_executed_evidence": "<latest stamp>" | "—",
    48	  "generated_at": "<ISO8601 Z>"
    49	}
    50	```
    51	
    52	`POST /api/workbench/state-of-world` must return 404 or 405 (no mutation possible).
    53	
    54	## Truth-engine red line
    55	
    56	Files touched:
    57	- `src/well_harness/demo_server.py` — adds `WORKBENCH_STATE_OF_WORLD_PATH` constant, `_truth_engine_short_sha()`, `_read_recent_evidence_lines()`, `_open_known_issues_count()`, `workbench_state_of_world_payload()`, GET handler. **Read-only**: never mutates state, only aggregates.
    58	- `src/well_harness/static/workbench.html` — NEW status-bar section before wow starters
    59	- `src/well_harness/static/workbench.css` — NEW `.workbench-state-of-world-bar*` selectors
    60	- `src/well_harness/static/workbench.js` — NEW `hydrateStateOfWorldBar()` + DOMContentLoaded hook
    61	- `tests/test_workbench_state_of_world_bar.py` — NEW (15 tests)
    62	
    63	Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new endpoint is explicitly classified as `kind: "advisory"` — it never claims to be a live truth-engine reading.

exec
/bin/zsh -lc 'rg -n "last_executed_evidence|truth_engine_sha_source|recent_e2e_source|adversarial_source|open_known_issues_source|_source sibling|generated_at|kind" -S .planning/phases/E11-workbench-engineer-first-ux docs src tests' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/knowledge_capture.py:16:KNOWLEDGE_ARTIFACT_KIND = "well-harness-knowledge-artifact"
src/well_harness/knowledge_capture.py:29:    generated_at_utc: str
src/well_harness/knowledge_capture.py:56:        "generated_at_utc": artifact.generated_at_utc,
src/well_harness/knowledge_capture.py:65:        "kind": KNOWLEDGE_ARTIFACT_KIND,
src/well_harness/knowledge_capture.py:166:        generated_at_utc=_now_utc_iso(),
src/well_harness/knowledge_capture.py:230:        generated_at_utc=_now_utc_iso(),
src/well_harness/knowledge_capture.py:245:        f"generated_at_utc: {artifact.generated_at_utc}",
tests/test_archive_integrity.py:202:            "kind": "well-harness-workbench-archive-manifest",
tests/test_archive_integrity.py:207:                "bundle_kind": "full_workbench_bundle",
src/well_harness/second_system_smoke.py:17:SECOND_SYSTEM_SMOKE_KIND = "well-harness-second-system-smoke"
src/well_harness/second_system_smoke.py:22:ADAPTER_RUNTIME_PROOF_KIND = "adapter_runtime_proof"
src/well_harness/second_system_smoke.py:34:    kind: str
src/well_harness/second_system_smoke.py:42:    bundle_kind: str
src/well_harness/second_system_smoke.py:70:        "kind": SECOND_SYSTEM_SMOKE_KIND,
src/well_harness/second_system_smoke.py:232:        kind=SECOND_SYSTEM_SMOKE_KIND,
src/well_harness/second_system_smoke.py:240:        bundle_kind=ADAPTER_RUNTIME_PROOF_KIND,
src/well_harness/second_system_smoke.py:309:        f"proof_mode={INTAKE_PACKET_PROOF_MODE}, bundle={bundle.bundle_kind}, scenario={bundle.selected_scenario_id or 'none'}, "
src/well_harness/second_system_smoke.py:313:        kind=SECOND_SYSTEM_SMOKE_KIND,
src/well_harness/second_system_smoke.py:321:        bundle_kind=bundle.bundle_kind,
src/well_harness/second_system_smoke.py:365:        f"kind: {report.kind}",
src/well_harness/second_system_smoke.py:372:        f"bundle_kind: {report.bundle_kind}",
tests/test_controller.py:78:        truth_kind="test-double",
docs/c919_etras/traceability_matrix.md:89:| PDF / safety concern | FaultModeSpec `id` | `fault_kind` (JSON-schema enum) | Adapter LOC | Test |
src/well_harness/two_system_runtime_comparison.py:14:TWO_SYSTEM_RUNTIME_COMPARISON_KIND = "well-harness-two-system-runtime-comparison"
src/well_harness/two_system_runtime_comparison.py:54:    kind: str
src/well_harness/two_system_runtime_comparison.py:80:        "kind": TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
src/well_harness/two_system_runtime_comparison.py:161:        kind=TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
src/well_harness/two_system_runtime_comparison.py:175:        f"kind: {report.kind}",
docs/onboarding/README.md:76:  "kind": "well-harness-control-system-spec",
docs/onboarding/README.md:98:- `kind` — one of: `sensor`, `command`, `pilot_input`
docs/onboarding/README.md:172:            kind="python-adapter",             # or "pdf", "markdown", "notion"
docs/onboarding/README.md:313:- All required fields at the top level must be present (`$schema`, `kind`, `version`, `system_id`, etc.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:106:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:108:- Which component kinds are valid (`sensor`, `command`, `pilot_input` — listed in onboarding README but easy to miss)
docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:109:- Which `fault_kind` values are valid (from `fault_taxonomy.py`, not mentioned in onboarding README)
docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:141:- All `downstream_component_ids` reference components of `kind="command"`
docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:145:The valid `fault_kind` values should be listed directly in the onboarding README, not require a separate file read.
src/well_harness/system_spec.py:10:CONTROL_SYSTEM_SPEC_KIND = "well-harness-control-system-spec"
src/well_harness/system_spec.py:19:    kind: str
src/well_harness/system_spec.py:83:    fault_kind: str
src/well_harness/system_spec.py:135:        "kind": CONTROL_SYSTEM_SPEC_KIND,
src/well_harness/system_spec.py:151:                kind=item["kind"],
src/well_harness/system_spec.py:218:                fault_kind=item["fault_kind"],
src/well_harness/system_spec.py:279:            kind="sensor",
src/well_harness/system_spec.py:289:            kind="pilot_input",
src/well_harness/system_spec.py:299:            kind="switch",
src/well_harness/system_spec.py:309:            kind="switch",
src/well_harness/system_spec.py:319:            kind="state",
src/well_harness/system_spec.py:329:            kind="state",
src/well_harness/system_spec.py:339:            kind="state",
src/well_harness/system_spec.py:349:            kind="state",
src/well_harness/system_spec.py:359:            kind="sensor",
src/well_harness/system_spec.py:369:            kind="parameter",
src/well_harness/system_spec.py:379:            kind="power",
src/well_harness/system_spec.py:389:            kind="power",
src/well_harness/system_spec.py:399:            kind="command",
src/well_harness/system_spec.py:409:            kind="command",
src/well_harness/system_spec.py:419:            kind="command",
src/well_harness/system_spec.py:429:            kind="feedback",
src/well_harness/system_spec.py:439:            kind="command",
src/well_harness/system_spec.py:546:            fault_kind="stuck_low",
src/well_harness/system_spec.py:555:            fault_kind="latched_no_unlock",
src/well_harness/system_spec.py:564:            fault_kind="command_path_failure",
tests/test_fault_diagnosis.py:11:    FAULT_DIAGNOSIS_KIND,
tests/test_fault_diagnosis.py:17:from well_harness.scenario_playback import PLAYBACK_TRACE_KIND
tests/test_fault_diagnosis.py:75:        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["kind"])
tests/test_fault_diagnosis.py:80:        self.assertEqual(PLAYBACK_TRACE_KIND, payload["baseline_report"]["kind"])
tests/test_fault_diagnosis.py:81:        self.assertEqual(PLAYBACK_TRACE_KIND, payload["fault_report"]["kind"])
tests/test_fault_diagnosis.py:95:        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["kind"])
tests/test_fault_diagnosis.py:123:        self.assertEqual(FAULT_DIAGNOSIS_KIND, schema["properties"]["kind"]["const"])
tests/test_fault_diagnosis.py:126:        self.assertEqual("well-harness-playback-trace", schema["$defs"]["playbackTrace"]["properties"]["kind"]["const"])
src/well_harness/fault_taxonomy.py:6:FAULT_TAXONOMY_KIND = "well-harness-fault-taxonomy"
src/well_harness/fault_taxonomy.py:13:    fault_kind: str
src/well_harness/fault_taxonomy.py:22:        fault_kind="bias_low",
src/well_harness/fault_taxonomy.py:29:        fault_kind="bias_high",
src/well_harness/fault_taxonomy.py:36:        fault_kind="stuck_low",
src/well_harness/fault_taxonomy.py:43:        fault_kind="stuck_high",
src/well_harness/fault_taxonomy.py:50:        fault_kind="open_circuit",
src/well_harness/fault_taxonomy.py:57:        fault_kind="short_to_power",
src/well_harness/fault_taxonomy.py:64:        fault_kind="latched_no_unlock",
src/well_harness/fault_taxonomy.py:71:        fault_kind="command_path_failure",
src/well_harness/fault_taxonomy.py:80:SUPPORTED_FAULT_KINDS = tuple(entry.fault_kind for entry in FAULT_TAXONOMY)
src/well_harness/fault_taxonomy.py:83:def validate_fault_kind(fault_kind: str) -> str:
src/well_harness/fault_taxonomy.py:84:    normalized = fault_kind.strip()
src/well_harness/fault_taxonomy.py:85:    if normalized in SUPPORTED_FAULT_KINDS:
src/well_harness/fault_taxonomy.py:87:    supported = ", ".join(SUPPORTED_FAULT_KINDS)
src/well_harness/fault_taxonomy.py:88:    raise ValueError(f"fault_kind must be one of: {supported}. Received: {fault_kind!r}")
src/well_harness/fault_taxonomy.py:94:        "kind": FAULT_TAXONOMY_KIND,
src/well_harness/fault_taxonomy.py:96:        "fault_kinds": [asdict(entry) for entry in FAULT_TAXONOMY],
tests/test_workbench_archive_manifest_schema.py:40:        self.assertIn("bundle_kind=full_workbench_bundle", result.stdout)
tests/test_workbench_archive_manifest_schema.py:41:        self.assertIn("bundle_kind=clarification_follow_up", result.stdout)
tests/test_workbench_archive_manifest_schema.py:64:        self.assertIn("clarification_follow_up", {item["bundle_kind"] for item in payload["results"]})
tests/test_workbench_archive_manifest_schema.py:65:        self.assertIn("full_workbench_bundle", {item["bundle_kind"] for item in payload["results"]})
docs/P43-workflow-automaton.yaml:7:generated_at_utc: "2026-04-21T18:00:00Z"
docs/P43-workflow-automaton.yaml:15:    kind: initial
docs/P43-workflow-automaton.yaml:18:    kind: normal
docs/P43-workflow-automaton.yaml:21:    kind: normal
docs/P43-workflow-automaton.yaml:24:    kind: normal
docs/P43-workflow-automaton.yaml:27:    kind: normal
docs/P43-workflow-automaton.yaml:30:    kind: normal
docs/P43-workflow-automaton.yaml:33:    kind: normal
docs/P43-workflow-automaton.yaml:36:    kind: normal
docs/P43-workflow-automaton.yaml:39:    kind: normal
docs/P43-workflow-automaton.yaml:42:    kind: normal
docs/P43-workflow-automaton.yaml:45:    kind: normal
docs/P43-workflow-automaton.yaml:48:    kind: transient
docs/P43-workflow-automaton.yaml:52:    kind: transient
docs/P43-workflow-automaton.yaml:58:    kind: terminal_normal
docs/P43-workflow-automaton.yaml:61:    kind: transient
docs/P43-workflow-automaton.yaml:65:    kind: terminal_normal
docs/P43-workflow-automaton.yaml:68:    kind: terminal_fault
src/well_harness/demo_server.py:1275:                "bundle_kind": bundle.get("bundle_kind"),
src/well_harness/demo_server.py:1344:        "last_executed_evidence": "",
src/well_harness/demo_server.py:1361:        out["last_executed_evidence"] = m.group(1)
src/well_harness/demo_server.py:1385:    `kind: "advisory"` flag is the contract that this is NOT a live
src/well_harness/demo_server.py:1389:        "kind": "advisory",
src/well_harness/demo_server.py:1391:        "truth_engine_sha_source": "git rev-parse --short HEAD",
src/well_harness/demo_server.py:1393:        "recent_e2e_source": "docs/coordination/qa_report.md",
src/well_harness/demo_server.py:1395:        "adversarial_source": "docs/coordination/qa_report.md",
src/well_harness/demo_server.py:1397:        "open_known_issues_source": "docs/known-issues/ (file count)",
src/well_harness/demo_server.py:1398:        "last_executed_evidence": evidence["last_executed_evidence"] or "—",
src/well_harness/demo_server.py:1399:        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
tests/test_p19_api_endpoints.py:217:        for key in ("kind", "version", "system_id", "sensor",
tests/test_demo.py:1350:                                "kind": "well-harness-workbench-browser-workspace",
tests/test_demo.py:1382:                self.assertEqual("full_workbench_bundle", payload["bundle"]["bundle_kind"])
tests/test_demo.py:1411:                self.assertEqual("well-harness-workbench-archive-manifest", manifest_payload["kind"])
tests/test_demo.py:1440:            "kind": "well-harness-workbench-browser-workspace",
tests/test_demo.py:1482:        self.assertEqual("well-harness-workbench-archive-manifest", payload["manifest"]["kind"])
tests/test_demo.py:1483:        self.assertEqual("full_workbench_bundle", payload["bundle"]["bundle_kind"])
tests/test_timeline_engine.py:102:                        {"t_s": 0.5, "kind": "ramp_input", "target": "tra_deg", "value": -14}
tests/test_timeline_engine.py:114:                    {"t_s": 2.0, "kind": "set_input", "target": "tra_deg", "value": -14},
tests/test_timeline_engine.py:115:                    {"t_s": 0.5, "kind": "set_input", "target": "tra_deg", "value": -2},
tests/test_timeline_engine.py:130:                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:131:                TimelineEvent(t_s=3.0, kind="clear_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:150:                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw2:stuck_on", duration_s=0.5),
tests/test_timeline_engine.py:163:                TimelineEvent(t_s=2.0, kind="inject_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:176:                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:177:                TimelineEvent(t_s=3.0, kind="clear_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:199:                TimelineEvent(t_s=0.1, kind="set_input", target="tra_deg", value=-7.0),
tests/test_timeline_engine.py:216:                TimelineEvent(t_s=0.2, kind="inject_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:217:                TimelineEvent(t_s=0.4, kind="clear_fault", target="sw1:stuck_off"),
tests/test_timeline_engine.py:245:                    t_s=0.1, kind="ramp_input", target="tra_deg", value=-10.0, duration_s=1.0
tests/test_timeline_engine.py:275:                    t_s=0.6, kind="assert_condition", target="logic4", value="active",
tests/test_timeline_engine.py:279:                    t_s=0.2, kind="assert_condition", target="logic4_active", value=True,
tests/test_timeline_engine.py:306:                TimelineEvent(t_s=0.5, kind="inject_fault", target="sw1:stuck_off"),
src/well_harness/static/workbench_start.css:120:.ws-tile[data-persona="P1"]     .ws-tile-kind { color: var(--ws-active); }
src/well_harness/static/workbench_start.css:121:.ws-tile[data-persona="P2"]     .ws-tile-kind { color: var(--ws-accent); }
src/well_harness/static/workbench_start.css:122:.ws-tile[data-persona="P5"]     .ws-tile-kind { color: var(--ws-violet); }
src/well_harness/static/workbench_start.css:123:.ws-tile[data-persona="KOGAMI"] .ws-tile-kind { color: var(--ws-warn); }
src/well_harness/static/workbench_start.css:124:.ws-tile[data-persona="P4"]     .ws-tile-kind { color: var(--ws-rose); }
src/well_harness/static/workbench_start.css:126:.ws-tile-kind {
tests/test_scenario_playback.py:14:    PLAYBACK_TRACE_KIND,
tests/test_scenario_playback.py:77:        self.assertEqual(PLAYBACK_TRACE_KIND, payload["kind"])
tests/test_scenario_playback.py:125:        self.assertEqual(PLAYBACK_TRACE_KIND, payload["kind"])
tests/test_scenario_playback.py:137:        self.assertEqual(PLAYBACK_TRACE_KIND, schema["properties"]["kind"]["const"])
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:294:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:647:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:670:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:691:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:715:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:738:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:762:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3531:   705	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3850:  1024	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3857:  1031	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4096:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4132:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4151:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4398:  1044	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4406:  1052	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4568:  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4604:  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4983:  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4984:  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4985:  1627	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:4988:  1630	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:5501:  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:5502:  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:5941:  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6464:  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6475:  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6813:  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6814:  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6987:  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
tests/test_workbench_state_of_world_bar.py:68:        "kind",
tests/test_workbench_state_of_world_bar.py:70:        "truth_engine_sha_source",
tests/test_workbench_state_of_world_bar.py:72:        "recent_e2e_source",
tests/test_workbench_state_of_world_bar.py:74:        "adversarial_source",
tests/test_workbench_state_of_world_bar.py:76:        "open_known_issues_source",
tests/test_workbench_state_of_world_bar.py:77:        "last_executed_evidence",
tests/test_workbench_state_of_world_bar.py:78:        "generated_at",
tests/test_workbench_state_of_world_bar.py:83:def test_state_of_world_kind_is_advisory() -> None:
tests/test_workbench_state_of_world_bar.py:85:    reading. The 'advisory' kind is the contract."""
tests/test_workbench_state_of_world_bar.py:87:    assert payload["kind"] == "advisory"
tests/test_workbench_state_of_world_bar.py:105:def test_state_of_world_generated_at_is_iso() -> None:
tests/test_workbench_state_of_world_bar.py:107:    ts = payload["generated_at"]
tests/test_workbench_state_of_world_bar.py:118:    assert body.get("kind") == "advisory"
tests/test_workbench_state_of_world_bar.py:127:    assert 'data-status-kind="advisory"' in html
tests/test_validate_notion_control_plane.py:52:                {"id": "legacy-gate-id", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "Superseded by the current default gate."},
tests/test_validate_notion_control_plane.py:53:                {"id": "legacy-plan-id", "kind": "plan", "title": "P1-02 消除手动浏览器 QA 依赖", "reason": "Superseded by the current review contract."},
tests/test_document_intake.py:29:        self.assertEqual({document.kind for document in packet.source_documents}, {"pdf", "markdown"})
tests/test_document_intake.py:48:        self.assertEqual("well-harness-control-system-spec", report["generated_workbench_spec"]["kind"])
tests/test_document_intake.py:66:                "kind": "sensor",
tests/test_document_intake.py:116:                "fault_kind": "stuck_low",
tests/test_document_intake.py:152:        self.assertEqual(template_payload["source_documents"][0]["kind"], "pdf")
tests/test_document_intake.py:202:    def test_intake_packet_rejects_unknown_fault_kind(self):
tests/test_document_intake.py:208:                "fault_kind": "mystery_fault",
tests/test_document_intake.py:216:        with self.assertRaisesRegex(ValueError, "fault_kind must be one of"):
tests/test_document_intake.py:230:        self.assertEqual(payload["kind"], "well-harness-control-system-spec")
tests/test_workbench_bundle.py:14:from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
tests/test_workbench_bundle.py:15:from well_harness.knowledge_capture import KNOWLEDGE_ARTIFACT_KIND
tests/test_workbench_bundle.py:16:from well_harness.scenario_playback import PLAYBACK_TRACE_KIND
tests/test_workbench_bundle.py:18:    WORKBENCH_BUNDLE_KIND,
tests/test_workbench_bundle.py:71:        self.assertEqual("clarification_follow_up", bundle.bundle_kind)
tests/test_workbench_bundle.py:91:        self.assertEqual("full_workbench_bundle", bundle.bundle_kind)
tests/test_workbench_bundle.py:114:        self.assertEqual(WORKBENCH_BUNDLE_KIND, payload["kind"])
tests/test_workbench_bundle.py:116:        self.assertEqual("full_workbench_bundle", payload["bundle_kind"])
tests/test_workbench_bundle.py:117:        self.assertEqual(PLAYBACK_TRACE_KIND, payload["playback_report"]["kind"])
tests/test_workbench_bundle.py:118:        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["fault_diagnosis_report"]["kind"])
tests/test_workbench_bundle.py:119:        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["knowledge_artifact"]["kind"])
tests/test_workbench_bundle.py:128:        self.assertEqual(WORKBENCH_BUNDLE_KIND, payload["kind"])
tests/test_workbench_bundle.py:130:        self.assertEqual("clarification_follow_up", payload["bundle_kind"])
tests/test_workbench_bundle.py:141:        self.assertEqual(WORKBENCH_BUNDLE_KIND, schema["properties"]["kind"]["const"])
tests/test_workbench_bundle.py:144:        self.assertEqual(PLAYBACK_TRACE_KIND, schema["$defs"]["playbackTraceEnvelope"]["properties"]["kind"]["const"])
tests/test_workbench_bundle.py:173:        self.assertIn("bundle_kind: clarification_follow_up", blocked_text)
tests/test_workbench_bundle.py:178:        self.assertIn("bundle_kind: full_workbench_bundle", ready_text)
tests/test_workbench_bundle.py:211:            self.assertEqual("full_workbench_bundle", saved_bundle["bundle_kind"])
tests/test_workbench_bundle.py:213:            self.assertEqual("well-harness-workbench-archive-manifest", saved_manifest["kind"])
tests/test_workbench_bundle.py:221:            self.assertEqual("full_workbench_bundle", saved_manifest["bundle"]["bundle_kind"])
tests/test_workbench_bundle.py:260:                        "kind": "wrong-kind",
tests/test_workbench_bundle.py:265:                            "bundle_kind": "full_workbench_bundle",
tests/test_workbench_bundle.py:330:        self.assertEqual("well-harness-workbench-archive-manifest", schema["properties"]["kind"]["const"])
tests/test_workbench_bundle.py:396:        self.assertEqual("well-harness-workbench-archive-manifest", payload["kind"])
tests/test_workbench_bundle.py:539:            "kind": "well-harness-workbench-browser-workspace",
tests/test_workbench_bundle.py:599:            "kind": "well-harness-workbench-browser-workspace",
tests/test_workbench_bundle.py:652:            "kind": "well-harness-workbench-browser-workspace",
tests/test_workbench_bundle.py:678:        self.assertEqual("well-harness-workbench-archive-manifest", restore_payload["manifest"]["kind"])
tests/test_workbench_bundle.py:679:        self.assertEqual("full_workbench_bundle", restore_payload["bundle"]["bundle_kind"])
tests/test_workbench_bundle.py:701:        self.assertEqual("full_workbench_bundle", bundle_payload["bundle_kind"])
tests/test_workbench_bundle.py:742:        self.assertEqual("full_workbench_bundle", payload["bundle_kind"])
tests/test_workbench_bundle.py:756:        self.assertEqual("clarification_follow_up", payload["bundle_kind"])
tests/test_workbench_bundle.py:777:            self.assertEqual("clarification_follow_up", payload["bundle_kind"])
src/well_harness/static/workbench.js:250:      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
src/well_harness/static/workbench.js:286:    bundle_kind: bundle.bundle_kind || "",
src/well_harness/static/workbench.js:305:    bundle_kind: bundle.bundle_kind || "",
src/well_harness/static/workbench.js:729:    kind: "well-harness-workbench-browser-workspace",
src/well_harness/static/workbench.js:1048:function documentKindLabel(kind) {
src/well_harness/static/workbench.js:1055:  return labels[kind] || kind || "未知来源";
src/well_harness/static/workbench.js:1068:function signalKindLabel(kind) {
src/well_harness/static/workbench.js:1076:  return labels[kind] || kind || "未知类型";
src/well_harness/static/workbench.js:1238:      createFingerprintChip(documentKindLabel(document.kind), "source"),
src/well_harness/static/workbench.js:1274:      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
src/well_harness/static/workbench.js:1649:  const documentKinds = uniqueValues(documents.map((document) => document.kind));
src/well_harness/static/workbench.js:1650:  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
src/well_harness/static/workbench.js:1651:  if (documentKinds.length > 1) {
src/well_harness/static/workbench.js:1654:  if (documentKinds.includes("pdf")) {
src/well_harness/static/workbench.js:2159:    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
src/well_harness/static/workbench.js:2160:      throw new Error(`不支持的快照类型：${workspace.kind}`);
src/well_harness/static/workbench.js:2599:      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
src/well_harness/static/workbench.js:3120:  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
src/well_harness/static/workbench.js:3131:  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
src/well_harness/static/workbench.js:3169:  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
src/well_harness/static/workbench.js:3170:  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
src/well_harness/static/workbench.js:3343:  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
tests/test_cli.py:786:        self.assertEqual(payload["failure_kind"], "cli_exit")
tests/test_cli.py:791:        self.assertEqual(failure["failure_kind"], "cli_exit")
tests/test_cli.py:839:                    self.assertEqual(payload["failure_kind"], scenario["expected_failure_kind"])
tests/test_cli.py:903:            set(schema_contract["failure_kinds"]),
tests/test_cli.py:904:            set(schema_defs["failureKind"]["enum"]),
tests/test_cli.py:914:            if item["expected_failure_kind"] == "schema_unavailable"
tests/test_cli.py:918:            if item["expected_failure_kind"] == "schema_validation"
tests/test_cli.py:928:        self.assertIn("failure_kind", schema_defs["failReport"]["allOf"][1]["required"])
tests/test_cli.py:930:            {item["expected_failure_kind"] for item in fail_scenarios}.issubset(
tests/test_cli.py:931:                schema_contract["failure_kinds"]
tests/test_cli.py:1078:        self.assertEqual(payload["failure_kind"], fail_contract["expected_failure_kind"])
tests/test_cli.py:1115:        self.assertIn("failure_kind", report_base["properties"])
tests/test_cli.py:1135:            set(schema_contract["failure_kinds"]),
tests/test_cli.py:1136:            set(schema_defs["failureKind"]["enum"]),
tests/test_cli.py:1141:        self.assertIn(asset["fail"]["expected_failure_kind"], schema_contract["failure_kinds"])
tests/test_cli.py:1175:        self.assertIn("failure_kind", report_base["properties"])
tests/test_cli.py:1200:            set(schema_contract["failure_kinds"]),
tests/test_cli.py:1201:            set(schema_defs["failureKind"]["enum"]),
tests/test_cli.py:1207:        self.assertIn(asset["fail"]["expected_failure_kind"], schema_contract["failure_kinds"])
tests/test_cli.py:1425:        self.assertEqual(payload["failure_kind"], fail_contract["expected_failure_kind"])
tests/test_timeline_fantui.py:111:                TimelineEvent(t_s=0.0, kind="ramp_input", target="tra_deg", value=-26.0, duration_s=4.0),
tests/test_timeline_fantui.py:141:                TimelineEvent(t_s=0.0, kind="ramp_input", target="tra_deg", value=-26.0, duration_s=4.0),
tests/test_timeline_fantui.py:144:                TimelineEvent(t_s=5.0, kind="inject_fault", target="logic3:logic_stuck_false"),
tests/test_timeline_fantui.py:192:                TimelineEvent(t_s=0.5, kind="inject_fault", target="sw1:stuckoff"),
tests/test_timeline_fantui.py:217:                TimelineEvent(t_s=5.0, kind="inject_fault", target="sw1:stuck_off"),
tests/test_timeline_fantui.py:218:                TimelineEvent(t_s=7.0, kind="clear_fault", target="sw1:stuck_off"),
tests/test_timeline_fantui.py:220:                TimelineEvent(t_s=7.5, kind="ramp_input", target="tra_deg", value=-14.0, duration_s=1.0),
tests/test_timeline_fantui.py:270:                {"t_s": 0.5, "kind": "inject_fault", "target": "sw1:stuckoff"},
tests/test_system_spec.py:8:    CONTROL_SYSTEM_SPEC_KIND,
tests/test_system_spec.py:73:        self.assertEqual(payload["kind"], CONTROL_SYSTEM_SPEC_KIND)
tests/test_system_spec.py:96:        self.assertEqual(CONTROL_SYSTEM_SPEC_KIND, schema["properties"]["kind"]["const"])
tests/test_c919_etras_adapter.py:146:        self.assertEqual("python-generic-truth-adapter", payload["truth_kind"])
tests/test_c919_etras_adapter.py:678:        thrust_reverser `kind: "thrust-reverser-hardware"` layout (parameters
tests/test_c919_etras_adapter.py:680:        `kind: "hardware_schema"` flat layout adopted by bleed_air /
tests/test_c919_etras_adapter.py:682:        scope. We verify the YAML is well-formed and that its own `kind`
tests/test_c919_etras_adapter.py:684:        to the matching legacy kind.
tests/test_c919_etras_adapter.py:692:        self.assertEqual("hardware_schema", hardware_payload["kind"])
src/well_harness/fault_diagnosis.py:8:from well_harness.fault_taxonomy import validate_fault_kind
src/well_harness/fault_diagnosis.py:17:FAULT_DIAGNOSIS_KIND = "well-harness-fault-diagnosis"
src/well_harness/fault_diagnosis.py:26:    kind: str
src/well_harness/fault_diagnosis.py:40:    fault_kind: str
src/well_harness/fault_diagnosis.py:65:        "fault_kind": report.fault_kind,
src/well_harness/fault_diagnosis.py:83:        "kind": FAULT_DIAGNOSIS_KIND,
src/well_harness/fault_diagnosis.py:146:    fault_kind = validate_fault_kind(fault_mode.fault_kind)
src/well_harness/fault_diagnosis.py:152:    if fault_kind == "bias_low":
src/well_harness/fault_diagnosis.py:163:    if fault_kind == "bias_high":
src/well_harness/fault_diagnosis.py:174:    if fault_kind in {"stuck_low", "open_circuit", "command_path_failure"}:
src/well_harness/fault_diagnosis.py:177:            f"{fault_mode.target_component_id} is forced to its inactive value for {fault_kind}.",
src/well_harness/fault_diagnosis.py:179:    if fault_kind in {"stuck_high", "short_to_power"}:
src/well_harness/fault_diagnosis.py:182:            f"{fault_mode.target_component_id} is forced to its active value for {fault_kind}.",
src/well_harness/fault_diagnosis.py:184:    if fault_kind == "latched_no_unlock":
src/well_harness/fault_diagnosis.py:199:        f"fault kind {fault_kind!r} is not yet supported; clarify the injection semantics before replaying diagnostics."
src/well_harness/fault_diagnosis.py:218:            kind="missing",
src/well_harness/fault_diagnosis.py:230:        kind=baseline.kind,
src/well_harness/fault_diagnosis.py:290:        f"{fault_mode.target_component_id} under {fault_mode.fault_kind} keeps "
src/well_harness/fault_diagnosis.py:295:        f"Injected fault mode {fault_mode.id} targets {fault_mode.target_component_id} with {fault_mode.fault_kind}.",
src/well_harness/fault_diagnosis.py:309:        fault_kind=fault_mode.fault_kind,
src/well_harness/fault_diagnosis.py:361:        f"fault_mode: {report.fault_mode_id} ({report.fault_kind}) target={report.target_component_id}",
src/well_harness/static/c919_etras_workstation.css:450:.probability-node-kind {
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:21:    { "t_s": 0.0, "kind": "mark_phase", "target": "descent" },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:22:    { "t_s": 0.0, "kind": "set_input", "target": "lgcu1_mlg_wow", "value": true },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:23:    { "t_s": 0.0, "kind": "set_input", "target": "lgcu2_mlg_wow", "value": true },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:24:    { "t_s": 0.5, "kind": "ramp_input", "target": "tra_deg", "value": -12.5, "duration_s": 3.5 },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:25:    { "t_s": 1.0, "kind": "inject_fault", "target": "tr_inhibited:stuck_on", "note": "A/C bus inhibits TR before SW1 window closes" },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:26:    { "t_s": 2.3, "kind": "assert_condition", "target": "ln_eicu_cmd2", "value": "blocked", "note": "TRA inside SW1 window with MLG_WOW=1 → CMD2 SHOULD fire but tr_inhibited blocks it" },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:27:    { "t_s": 9.0, "kind": "assert_condition", "target": "fadec_deploy_command", "value": false, "note": "deploy must never fire under persistent inhibit" },
src/well_harness/timelines/c919_tr_inhibited_blocks_deploy.json:28:    { "t_s": 9.0, "kind": "assert_condition", "target": "ln_fadec_deploy_command", "value": "idle", "note": "deploy never reaches triggerable state because enable upstream is dead" }
src/well_harness/timelines/nominal_landing.json:18:    { "t_s": 0.0,  "kind": "mark_phase", "target": "descent",         "note": "approach" },
src/well_harness/timelines/nominal_landing.json:19:    { "t_s": 0.0,  "kind": "ramp_input", "target": "radio_altitude_ft", "value": 5.0, "duration_s": 5.0, "note": "descend 500→5 ft in 5s" },
src/well_harness/timelines/nominal_landing.json:20:    { "t_s": 5.0,  "kind": "mark_phase", "target": "landing",         "note": "main gear touchdown" },
src/well_harness/timelines/nominal_landing.json:21:    { "t_s": 5.0,  "kind": "set_input",  "target": "aircraft_on_ground", "value": true },
src/well_harness/timelines/nominal_landing.json:22:    { "t_s": 5.0,  "kind": "set_input",  "target": "radio_altitude_ft", "value": 2.0 },
src/well_harness/timelines/nominal_landing.json:23:    { "t_s": 6.0,  "kind": "mark_phase", "target": "throttle_push",   "note": "pilot pulls reverse lever" },
src/well_harness/timelines/nominal_landing.json:24:    { "t_s": 6.0,  "kind": "ramp_input", "target": "tra_deg",          "value": -26.0, "duration_s": 4.0, "note": "0°→-26° pullback (SW1→SW2→L3 threshold)" },
src/well_harness/timelines/nominal_landing.json:25:    { "t_s": 10.0, "kind": "mark_phase", "target": "deploy" },
src/well_harness/timelines/nominal_landing.json:26:    { "t_s": 12.0, "kind": "assert_condition", "target": "logic3",     "value": "active", "note": "L3 should be active 2s after deploy-range reach" },
src/well_harness/timelines/nominal_landing.json:27:    { "t_s": 16.0, "kind": "assert_condition", "target": "logic4_active", "value": true, "note": "L4 should fire once plant VDT reaches 90%" },
src/well_harness/timelines/nominal_landing.json:28:    { "t_s": 17.0, "kind": "mark_phase", "target": "end",             "note": "throttle_lock released, simulation end" }
src/well_harness/tools/generate_adapter.py:100:    L('    truth_kind="spec-derived-generic-truth",')
src/well_harness/tools/generate_adapter.py:225:        "truth_kind": "spec-derived-generic-truth",
src/well_harness/tools/generate_adapter.py:597:    truth_kind: str
src/well_harness/tools/generate_adapter.py:604:            "kind": "well-harness-controller-truth-adapter-metadata",
src/well_harness/static/workbench_bundle.html:623:              <span class="workbench-summary-label">Bundle Kind</span>
src/well_harness/static/workbench_bundle.html:624:              <strong id="bundle-kind">-</strong>
src/well_harness/timelines/c919_nominal_deploy.json:21:    { "t_s": 0.0, "kind": "mark_phase", "target": "descent" },
src/well_harness/timelines/c919_nominal_deploy.json:22:    { "t_s": 0.0, "kind": "set_input", "target": "lgcu1_mlg_wow", "value": true, "note": "touchdown — LGCU1 WOW" },
src/well_harness/timelines/c919_nominal_deploy.json:23:    { "t_s": 0.0, "kind": "set_input", "target": "lgcu2_mlg_wow", "value": true, "note": "touchdown — LGCU2 WOW" },
src/well_harness/timelines/c919_nominal_deploy.json:24:    { "t_s": 0.5, "kind": "mark_phase", "target": "throttle_push", "note": "pilot pulls TRA back into reverse" },
src/well_harness/timelines/c919_nominal_deploy.json:25:    { "t_s": 0.5, "kind": "ramp_input", "target": "tra_deg", "value": -12.5, "duration_s": 3.5, "note": "+5°→-12.5° sweep through SW1 and SW2 windows" },
src/well_harness/timelines/c919_nominal_deploy.json:26:    { "t_s": 4.0, "kind": "mark_phase", "target": "deploy" },
src/well_harness/timelines/c919_nominal_deploy.json:27:    { "t_s": 6.0, "kind": "assert_condition", "target": "ln_eicu_cmd3", "value": "active", "note": "CMD3 latch must be live while deploy command is asserted" },
src/well_harness/timelines/c919_nominal_deploy.json:28:    { "t_s": 10.0, "kind": "assert_condition", "target": "fadec_deploy_command", "value": true, "note": "FADEC Deploy Command asserts after unlock-confirmed + TR_WOW + TRA<-11.74°" },
src/well_harness/timelines/c919_nominal_deploy.json:29:    { "t_s": 13.0, "kind": "mark_phase", "target": "deployed_idle", "note": "state machine holds in S5_DEPLOYED_IDLE_REVERSE" }
tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json:11:      "kind": "switch",
tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json:21:      "kind": "sensor",
tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json:31:      "kind": "command",
tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json:85:      "fault_kind": "bias_low",
src/well_harness/scenario_playback.py:21:PLAYBACK_TRACE_KIND = "well-harness-playback-trace"
src/well_harness/scenario_playback.py:36:    kind: str
src/well_harness/scenario_playback.py:45:    kind: str
src/well_harness/scenario_playback.py:82:        "kind": PLAYBACK_TRACE_KIND,
src/well_harness/scenario_playback.py:375:                        kind="signal_change",
src/well_harness/scenario_playback.py:387:                        kind="logic_change",
src/well_harness/scenario_playback.py:399:                kind="transition_start",
src/well_harness/scenario_playback.py:407:                kind="transition_end",
src/well_harness/scenario_playback.py:417:            kind=components[component_id].kind,
src/well_harness/scenario_playback.py:428:            kind="logic_node",
src/well_harness/scenario_playback.py:454:        events=tuple(sorted(events, key=lambda item: (item.time_s, item.kind, item.label))),
src/well_harness/scenario_playback.py:510:        lines.extend(f"  - t={event.time_s:g}s {event.kind}: {event.details}" for event in report.events[:12])
src/well_harness/timelines/sw1_stuck_at_touchdown.json:18:    { "t_s": 0.0,  "kind": "mark_phase", "target": "descent" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:19:    { "t_s": 0.0,  "kind": "ramp_input", "target": "radio_altitude_ft", "value": 5.0, "duration_s": 5.0 },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:20:    { "t_s": 5.0,  "kind": "mark_phase", "target": "landing" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:21:    { "t_s": 5.0,  "kind": "set_input",  "target": "aircraft_on_ground", "value": true },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:22:    { "t_s": 5.0,  "kind": "set_input",  "target": "radio_altitude_ft", "value": 2.0 },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:23:    { "t_s": 5.0,  "kind": "inject_fault", "target": "sw1:stuck_off", "note": "micro-switch jams at touchdown" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:24:    { "t_s": 6.0,  "kind": "mark_phase", "target": "throttle_push" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:25:    { "t_s": 6.0,  "kind": "ramp_input", "target": "tra_deg",          "value": -26.0, "duration_s": 4.0 },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:26:    { "t_s": 10.0, "kind": "mark_phase", "target": "deploy_attempt" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:27:    { "t_s": 17.0, "kind": "assert_condition", "target": "logic1", "value": "blocked", "note": "L1 must stay blocked because sw1 never latches" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:28:    { "t_s": 17.0, "kind": "assert_condition", "target": "logic4_active", "value": false, "note": "L4 must remain false — chain broken at L1" },
src/well_harness/timelines/sw1_stuck_at_touchdown.json:29:    { "t_s": 17.0, "kind": "assert_condition", "target": "throttle_electronic_lock_release_cmd", "value": false, "note": "THR_LOCK must NOT release — safety preserved" }
tests/test_timeline_c919_etras.py:101:                TimelineEvent(t_s=0.0, kind="set_input", target="lgcu1_mlg_wow", value=True),
tests/test_timeline_c919_etras.py:102:                TimelineEvent(t_s=0.0, kind="set_input", target="lgcu2_mlg_wow", value=True),
tests/test_timeline_c919_etras.py:103:                TimelineEvent(t_s=0.5, kind="ramp_input", target="tra_deg", value=-12.5, duration_s=3.5),
tests/test_timeline_c919_etras.py:104:                TimelineEvent(t_s=4.0, kind="inject_fault", target="etras_over_temp_fault:stuck_on"),
tests/test_timeline_c919_etras.py:141:                TimelineEvent(t_s=0.5, kind="ramp_input", target="tra_deg", value=-12.5, duration_s=3.5),
tests/test_timeline_c919_etras.py:142:                TimelineEvent(t_s=8.0, kind="ramp_input", target="tra_deg", value=-28.0, duration_s=1.0),
tests/test_timeline_c919_etras.py:143:                TimelineEvent(t_s=12.0, kind="ramp_input", target="tra_deg", value=0.0, duration_s=1.0),
tests/test_timeline_c919_etras.py:205:                TimelineEvent(t_s=0.5, kind="inject_fault", target="tr_inhibited:wiggle"),
tests/test_timeline_c919_etras.py:267:                {"t_s": 0.5, "kind": "inject_fault", "target": "tr_inhibited:wiggle"},
src/well_harness/static/timeline-sim.html:198:      { t_s: 0.0,  kind: "mark_phase", target: "descent" },
src/well_harness/static/timeline-sim.html:199:      { t_s: 0.0,  kind: "ramp_input", target: "radio_altitude_ft", value: 5.0, duration_s: 5.0 },
src/well_harness/static/timeline-sim.html:200:      { t_s: 5.0,  kind: "mark_phase", target: "landing" },
src/well_harness/static/timeline-sim.html:201:      { t_s: 5.0,  kind: "set_input",  target: "aircraft_on_ground", value: true },
src/well_harness/static/timeline-sim.html:202:      { t_s: 5.0,  kind: "set_input",  target: "radio_altitude_ft",  value: 2.0 },
src/well_harness/static/timeline-sim.html:203:      { t_s: 6.0,  kind: "mark_phase", target: "throttle_push" },
src/well_harness/static/timeline-sim.html:204:      { t_s: 6.0,  kind: "ramp_input", target: "tra_deg", value: -26.0, duration_s: 4.0 },
src/well_harness/static/timeline-sim.html:205:      { t_s: 10.0, kind: "mark_phase", target: "deploy" },
src/well_harness/static/timeline-sim.html:206:      { t_s: 12.0, kind: "assert_condition", target: "logic3", value: "active" },
src/well_harness/static/timeline-sim.html:207:      { t_s: 16.0, kind: "assert_condition", target: "logic4_active", value: true }
src/well_harness/static/timeline-sim.html:222:      { t_s: 0.0,  kind: "ramp_input", target: "radio_altitude_ft", value: 5.0, duration_s: 5.0 },
src/well_harness/static/timeline-sim.html:223:      { t_s: 5.0,  kind: "set_input",  target: "aircraft_on_ground", value: true },
src/well_harness/static/timeline-sim.html:224:      { t_s: 5.0,  kind: "set_input",  target: "radio_altitude_ft", value: 2.0 },
src/well_harness/static/timeline-sim.html:225:      { t_s: 5.0,  kind: "inject_fault", target: "sw1:stuck_off" },
src/well_harness/static/timeline-sim.html:226:      { t_s: 6.0,  kind: "ramp_input", target: "tra_deg", value: -26.0, duration_s: 4.0 },
src/well_harness/static/timeline-sim.html:227:      { t_s: 17.0, kind: "assert_condition", target: "logic1", value: "blocked" },
src/well_harness/static/timeline-sim.html:228:      { t_s: 17.0, kind: "assert_condition", target: "logic4_active", value: false }
src/well_harness/static/timeline-sim.html:245:      { t_s: 0.0, kind: "set_input", target: "lgcu1_mlg_wow", value: true },
src/well_harness/static/timeline-sim.html:246:      { t_s: 0.0, kind: "set_input", target: "lgcu2_mlg_wow", value: true },
src/well_harness/static/timeline-sim.html:247:      { t_s: 0.5, kind: "ramp_input", target: "tra_deg", value: -12.5, duration_s: 3.5 },
src/well_harness/static/timeline-sim.html:248:      { t_s: 6.0, kind: "assert_condition", target: "ln_eicu_cmd3", value: "active" },
src/well_harness/static/timeline-sim.html:249:      { t_s: 10.0, kind: "assert_condition", target: "fadec_deploy_command", value: true }
src/well_harness/static/timeline-sim.html:266:      { t_s: 0.0, kind: "set_input", target: "lgcu1_mlg_wow", value: true },
src/well_harness/static/timeline-sim.html:267:      { t_s: 0.0, kind: "set_input", target: "lgcu2_mlg_wow", value: true },
src/well_harness/static/timeline-sim.html:268:      { t_s: 0.5, kind: "ramp_input", target: "tra_deg", value: -12.5, duration_s: 3.5 },
src/well_harness/static/timeline-sim.html:269:      { t_s: 1.0, kind: "inject_fault", target: "tr_inhibited:stuck_on" },
src/well_harness/static/timeline-sim.html:270:      { t_s: 2.3, kind: "assert_condition", target: "ln_eicu_cmd2", value: "blocked" },
src/well_harness/static/timeline-sim.html:271:      { t_s: 9.0, kind: "assert_condition", target: "fadec_deploy_command", value: false }
src/well_harness/static/timeline-sim.html:289:function setStatus(msg, kind = "") {
src/well_harness/static/timeline-sim.html:291:  statusEl.className = "status " + kind;
src/well_harness/static/timeline-sim.html:357:  const pushCell = (k, v, kindClass = "") =>
src/well_harness/static/timeline-sim.html:358:    cells.push(`<div class="outcome-cell"><div class="k">${escape(k)}</div><div class="v ${kindClass}">${escape(String(v))}</div></div>`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:119:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1184:   234	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1220:   270	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1239:   289	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1484:  1032	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1491:  1039	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1504:  1052	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1512:  1060	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1674:  1222	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:1710:  1258	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:2167:   713	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:2591:  1633	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:2592:  1634	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:2593:  1635	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:2596:  1638	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:3047:  2583	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:3609:  2143	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:3610:  2144	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:4551:  3104	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:4562:  3115	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:4600:  3153	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:4601:  3154	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:4774:  3327	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:119:      "kind": "sensor",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:133:      "kind": "pilot_input",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:147:      "kind": "switch",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:161:      "kind": "switch",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:175:      "kind": "state",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:189:      "kind": "state",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:203:      "kind": "state",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:217:      "kind": "state",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:231:      "kind": "sensor",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:245:      "kind": "parameter",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:259:      "kind": "power",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:273:      "kind": "power",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:287:      "kind": "command",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:301:      "kind": "command",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:315:      "kind": "command",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:329:      "kind": "feedback",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:343:      "kind": "command",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:358:      "fault_kind": "stuck_low",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:377:      "fault_kind": "latched_no_unlock",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:397:      "fault_kind": "command_path_failure",
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:409:  "kind": "well-harness-control-system-spec",
tests/test_knowledge_capture.py:10:from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
tests/test_knowledge_capture.py:12:    KNOWLEDGE_ARTIFACT_KIND,
tests/test_knowledge_capture.py:82:        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["kind"])
tests/test_knowledge_capture.py:87:        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["diagnosis_report"]["kind"])
tests/test_knowledge_capture.py:106:        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["kind"])
tests/test_knowledge_capture.py:109:        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["diagnosis_report"]["kind"])
tests/test_knowledge_capture.py:137:        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, schema["properties"]["kind"]["const"])
tests/test_knowledge_capture.py:140:        self.assertEqual("well-harness-fault-diagnosis", schema["$defs"]["faultDiagnosis"]["properties"]["kind"]["const"])
src/well_harness/document_intake.py:8:from well_harness.fault_taxonomy import validate_fault_kind
src/well_harness/document_intake.py:28:    kind: str
src/well_harness/document_intake.py:87:        kind=_require_str(payload, "kind"),
src/well_harness/document_intake.py:157:        fault_kind=validate_fault_kind(_require_str(payload, "fault_kind")),
src/well_harness/document_intake.py:176:        kind=_require_str(payload, "kind"),
src/well_harness/document_intake.py:201:                "kind": "pdf",
src/well_harness/document_intake.py:209:                "kind": "markdown",
src/well_harness/document_intake.py:220:                "kind": "sensor",
src/well_harness/document_intake.py:412:        "fault_kind": "stuck_low",
src/well_harness/document_intake.py:914:    source_document_kinds = sorted({document.kind for document in packet.source_documents})
src/well_harness/document_intake.py:922:        "source_document_kinds": source_document_kinds,
src/well_harness/document_intake.py:923:        "includes_pdf_sources": "pdf" in source_document_kinds,
src/well_harness/document_intake.py:924:        "mixed_source_packet": len(source_document_kinds) > 1,
src/well_harness/document_intake.py:935:                "kind": component.kind,
src/well_harness/document_intake.py:1020:                "kind": document.kind,
src/well_harness/document_intake.py:1047:            f"(kinds={', '.join(report['source_document_kinds']) or '-'})"
src/well_harness/document_intake.py:1062:            f"  - {item['id']} [{item['state_shape']}] unit={item['unit']} kind={item['kind']}"
src/well_harness/document_intake.py:1100:            f"  - {item['id']} [{item['kind']}] role={item['role']} title={item['title']} location={item['location']}"
src/well_harness/controller_adapter.py:10:CONTROLLER_TRUTH_ADAPTER_METADATA_KIND = "well-harness-controller-truth-adapter-metadata"
src/well_harness/controller_adapter.py:21:    truth_kind: str
src/well_harness/controller_adapter.py:41:        "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
src/well_harness/controller_adapter.py:104:    truth_kind="python-controller-adapter",
tests/test_two_system_runtime_comparison.py:9:    TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
tests/test_two_system_runtime_comparison.py:28:        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, report.kind)
tests/test_two_system_runtime_comparison.py:41:        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, payload["kind"])
tests/test_two_system_runtime_comparison.py:53:        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, schema["properties"]["kind"]["const"])
src/well_harness/static/workbench.html:55:        data-status-kind="advisory"
src/well_harness/tools/generate_svg.py:51:    # node_infos[id] = {id, label, kind, state_shape, level, col, row}
src/well_harness/tools/generate_svg.py:121:    # Sort nodes within each level by a stable key (kind priority + label)
src/well_harness/tools/generate_svg.py:122:    KIND_PRIORITY = {
src/well_harness/tools/generate_svg.py:135:        kind = ""
src/well_harness/tools/generate_svg.py:137:            kind = components[node_id].get("kind", "command")
src/well_harness/tools/generate_svg.py:139:            kind = "logic"
src/well_harness/tools/generate_svg.py:140:        return (KIND_PRIORITY.get(kind, 9), node_id)
src/well_harness/tools/generate_svg.py:234:    # Build connection list: (from_id, to_id, kind)
src/well_harness/tools/generate_svg.py:244:    for from_id, to_id, kind in connections:
src/well_harness/tools/generate_svg.py:250:        kind_class = "conn-input" if kind == "input" else "conn-logic"
src/well_harness/tools/generate_svg.py:252:        cls = f"conn-line {kind_class}"
src/well_harness/tools/generate_svg.py:268:    def node_tag(kind: str) -> str:
src/well_harness/tools/generate_svg.py:281:        return tag_map.get(kind, kind[:3].upper())
src/well_harness/tools/generate_svg.py:283:    def node_cls(kind: str) -> str:
src/well_harness/tools/generate_svg.py:295:        return cls_map.get(kind, "chain-node-svg")
src/well_harness/tools/generate_svg.py:297:    def node_kind_type_tag(kind: str) -> str:
src/well_harness/tools/generate_svg.py:298:        if kind in ("sensor", "pilot_input", "switch", "state", "parameter"):
src/well_harness/tools/generate_svg.py:300:        if kind == "logic":
src/well_harness/tools/generate_svg.py:302:        if kind in ("power", "feedback"):
src/well_harness/tools/generate_svg.py:304:        if kind == "command":
src/well_harness/tools/generate_svg.py:318:        kind = comp.get("kind", "sensor")
src/well_harness/tools/generate_svg.py:319:        cls = node_cls(kind)
src/well_harness/tools/generate_svg.py:320:        type_tag = node_tag(kind)
src/well_harness/tools/generate_svg.py:321:        node_type = node_kind_type_tag(kind)
src/well_harness/tools/generate_svg.py:373:            kind2 = comp.get("kind", "command")
src/well_harness/tools/generate_svg.py:374:            cls2 = node_cls(kind2)
src/well_harness/tools/generate_svg.py:375:            type_tag2 = node_tag(kind2)
src/well_harness/tools/generate_svg.py:376:            node_type2 = node_kind_type_tag(kind2)
tests/test_archive_restore_sandbox.py:60:        "kind": "well-harness-workbench-archive-manifest",
tests/test_archive_restore_sandbox.py:65:            "bundle_kind": "full_workbench_bundle",
src/well_harness/cli.py:559:            "kind": manifest.get("kind"),
src/well_harness/cli.py:564:                "bundle_kind": bundle.get("bundle_kind"),
src/well_harness/cli.py:586:    if payload.get("kind") is not None:
src/well_harness/cli.py:587:        lines.append(f"kind: {payload['kind']}")
src/well_harness/cli.py:596:        lines.append(f"bundle: {bundle.get('system_id')} / {bundle.get('bundle_kind')}")
tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json:9:      "kind": "pdf",
tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json:20:      "kind": "switch",
tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json:33:      "kind": "sensor",
tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json:46:      "kind": "command",
tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json:122:      "fault_kind": "bias_low",
src/well_harness/hardware_schema.py:94:    kind: str
src/well_harness/hardware_schema.py:214:        kind=raw["kind"],
src/well_harness/workbench_bundle.py:26:WORKBENCH_BUNDLE_KIND = "well-harness-workbench-bundle"
src/well_harness/workbench_bundle.py:29:ARCHIVE_MANIFEST_KIND = "well-harness-workbench-archive-manifest"
src/well_harness/workbench_bundle.py:65:    bundle_kind: str
src/well_harness/workbench_bundle.py:127:        "kind": WORKBENCH_BUNDLE_KIND,
src/well_harness/workbench_bundle.py:131:        "bundle_kind": bundle.bundle_kind,
src/well_harness/workbench_bundle.py:238:    if manifest.get("kind") != ARCHIVE_MANIFEST_KIND:
src/well_harness/workbench_bundle.py:239:        issues.append(f"kind must be {ARCHIVE_MANIFEST_KIND!r}.")
src/well_harness/workbench_bundle.py:272:        for field_name in ("bundle_kind", "system_id", "system_title"):
src/well_harness/workbench_bundle.py:561:            bundle_kind="clarification_follow_up",
src/well_harness/workbench_bundle.py:617:        bundle_kind="full_workbench_bundle",
src/well_harness/workbench_bundle.py:632:        f"bundle_kind: {bundle.bundle_kind}",
src/well_harness/workbench_bundle.py:696:        f"- Bundle Kind: `{bundle.bundle_kind}`",
src/well_harness/workbench_bundle.py:814:        "kind": ARCHIVE_MANIFEST_KIND,
src/well_harness/workbench_bundle.py:819:            "bundle_kind": bundle.bundle_kind,
src/well_harness/workbench_bundle.py:857:            _slugify(bundle.selected_scenario_id or bundle.bundle_kind),
src/well_harness/reference_packets/custom_reverse_control_v1.json:9:      "kind": "pdf",
src/well_harness/reference_packets/custom_reverse_control_v1.json:17:      "kind": "markdown",
src/well_harness/reference_packets/custom_reverse_control_v1.json:28:      "kind": "switch",
src/well_harness/reference_packets/custom_reverse_control_v1.json:41:      "kind": "sensor",
src/well_harness/reference_packets/custom_reverse_control_v1.json:54:      "kind": "command",
src/well_harness/reference_packets/custom_reverse_control_v1.json:130:      "fault_kind": "bias_low",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:9:        "kind": "switch",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:16:        "kind": "sensor",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:23:        "kind": "command",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:75:          "kind": "switch",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:89:          "kind": "sensor",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:103:          "kind": "command",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:118:          "fault_kind": "bias_low",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:131:      "kind": "well-harness-control-system-spec",
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:223:    "source_document_kinds": [
tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json:231:    "bundle_kind": "full_workbench_bundle",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:118:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:626:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:649:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:670:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:694:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:717:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:741:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:3550:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:3586:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:3605:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:3735:   705	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4056:  1024	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4063:  1031	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4076:  1044	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4084:  1052	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4254:  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4290:  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4667:  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4668:  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4669:  1627	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:4672:  1630	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:5185:  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:5186:  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:5933:  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6158:  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6169:  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6207:  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6208:  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6385:  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
src/well_harness/static/index.html:83:  .home-card-kind {
src/well_harness/static/index.html:91:  .home-card[data-scope="workstation"] .home-card-kind { color: var(--home-active); }
src/well_harness/static/index.html:92:  .home-card[data-scope="circuit"]     .home-card-kind { color: var(--home-accent); }
src/well_harness/static/index.html:93:  .home-card[data-scope="simulation"]  .home-card-kind { color: var(--home-warn); }
src/well_harness/static/index.html:94:  .home-card[data-scope="docs"]        .home-card-kind { color: #b07af5; }
src/well_harness/static/index.html:339:      <span class="home-card-kind">工作台</span>
src/well_harness/static/index.html:347:      <span class="home-card-kind">工作台</span>
src/well_harness/static/index.html:356:      <span class="home-card-kind">仿真 · 外部服务</span>
src/well_harness/static/index.html:365:      <span class="home-card-kind">电路图</span>
src/well_harness/static/index.html:373:      <span class="home-card-kind">电路图</span>
src/well_harness/static/index.html:382:      <span class="home-card-kind">仿真</span>
src/well_harness/static/index.html:391:      <span class="home-card-kind">文档</span>
src/well_harness/static/index.html:399:      <span class="home-card-kind">文档</span>
src/well_harness/static/workbench_start.html:56:      <span class="ws-tile-kind">学习与演示</span>
src/well_harness/static/workbench_start.html:79:      <span class="ws-tile-kind">工程师调试</span>
src/well_harness/static/workbench_start.html:100:      <span class="ws-tile-kind">立项 / 汇报演示</span>
src/well_harness/static/workbench_start.html:124:      <span class="ws-tile-kind">客户问题复现</span>
src/well_harness/static/workbench_start.html:147:      <span class="ws-tile-kind">提案审核（Kogami）</span>
src/well_harness/static/workbench_start.html:171:      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
src/well_harness/static/c919_etras_workstation.js:101:    { id: "mlg_wow", kind: "INPUT", label: "mlg_wow · WOW 仲裁", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:102:    { id: "tr_wow", kind: "INPUT", label: "tr_wow · 2.25s SET", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:103:    { id: "atltla", kind: "INPUT", label: "atltla · SW1", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:104:    { id: "tra_deg", kind: "INPUT", label: "tra_deg · 油门角度", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:105:    { id: "tr_inhibited", kind: "INPUT", label: "tr_inhibited · 抑制位", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:106:    { id: "ln_eicu_cmd2", kind: "LOGIC", label: "EICU_CMD2 · 单相解锁", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:107:    { id: "eicu_cmd2", kind: "OUTPUT", label: "eicu_cmd2 · 1-φ unlock", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:108:    { id: "apwtla", kind: "INPUT", label: "apwtla · SW2", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:109:    { id: "ln_eicu_cmd3", kind: "LOGIC", label: "EICU_CMD3 · 三相 TRCU", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:110:    { id: "eicu_cmd3", kind: "OUTPUT", label: "eicu_cmd3 · 3-φ TRCU", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:111:    { id: "lock_state", kind: "INPUT", label: "lock_state · 锁聚合", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:112:    { id: "ln_tr_command3_enable", kind: "LOGIC", label: "TR_Command3_Enable", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:113:    { id: "tr_command3_enable", kind: "OUTPUT", label: "tr_command3_enable", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:114:    { id: "e_tras_over_temp_fault", kind: "INPUT", label: "e_tras_over_temp_fault · 过温抑制", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:115:    { id: "engine_running", kind: "INPUT", label: "engine_running · 发动机运行", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:116:    { id: "n1k_percent", kind: "INPUT", label: "n1k_percent · 转速", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:117:    { id: "tr_position_percent", kind: "INPUT", label: "tr_position_percent · VDT", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:118:    { id: "ln_fadec_deploy_command", kind: "LOGIC", label: "FADEC_Deploy · 展开命令", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:119:    { id: "fadec_deploy_command", kind: "OUTPUT", label: "fadec_deploy_command", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:120:    { id: "ln_fadec_stow_command", kind: "LOGIC", label: "FADEC_Stow · 收起命令", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:121:    { id: "fadec_stow_command", kind: "OUTPUT", label: "fadec_stow_command", normalProbability: 0.9990 },
src/well_harness/static/c919_etras_workstation.js:579:            <span class="probability-node-kind">${escapeHtml(node.kind)}</span>${escapeHtml(node.label)}
docs/P43-api-contract-lock.yaml:28:generated_at_utc: 2026-04-21
docs/P43-api-contract-lock.yaml:315:          source_document_kinds: 'array[string]'
docs/P43-api-contract-lock.yaml:331:          bundle_kind: "well-harness-workbench-bundle"
docs/provenance/adapter_truth_levels.md:100:   - 更新对应 adapter 的 intake packet（加 PDF / docx 的 `SourceDocumentRef` · `kind=pdf/docx` · `role=requirement_reference`）
tests/fixtures/validation_schema_runner_report_asset_v1.json:53:    "expected_failure_kind": "status_mismatch",
docs/thrust_reverser/requirements_supplement.md:204:3. 每个 FaultModeSpec 需要 `target_component_id` + `fault_kind` + `expected_diagnostic_sections`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3127:src/well_harness/timeline_engine/player.py:113:                events_fired_ids.append(f"{event.kind}@{event.t_s:.3f}:{event.target}")
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3137:src/well_harness/timeline_engine/player.py:248:        if kind == "set_input":
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3262:    14	# Seven event kinds — Codex architecture consultation recommendation.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3263:    15	EVENT_KINDS = (
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3304:    56	    kind: str
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3312:    64	        if self.kind not in EVENT_KINDS:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3313:    65	            raise ValueError(f"unknown event kind: {self.kind!r}; expected one of {EVENT_KINDS}")
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3316:    68	        if self.kind == "ramp_input" and (self.duration_s is None or self.duration_s <= 0):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3318:    70	        if self.kind == "inject_fault" and self.duration_s is not None and self.duration_s <= 0:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3320:    72	        if self.kind == "start_deploy_sequence" and self.duration_s is not None and self.duration_s <= 0:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3336:   247	        kind = event.kind
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3337:   248	        if kind == "set_input":
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3342:   253	        if kind == "ramp_input":
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:3358:   269	        if kind == "start_deploy_sequence":
src/well_harness/timeline_engine/schema.py:14:# Seven event kinds — Codex architecture consultation recommendation.
src/well_harness/timeline_engine/schema.py:15:EVENT_KINDS = (
src/well_harness/timeline_engine/schema.py:56:    kind: str
src/well_harness/timeline_engine/schema.py:64:        if self.kind not in EVENT_KINDS:
src/well_harness/timeline_engine/schema.py:65:            raise ValueError(f"unknown event kind: {self.kind!r}; expected one of {EVENT_KINDS}")
src/well_harness/timeline_engine/schema.py:68:        if self.kind == "ramp_input" and (self.duration_s is None or self.duration_s <= 0):
src/well_harness/timeline_engine/schema.py:70:        if self.kind == "inject_fault" and self.duration_s is not None and self.duration_s <= 0:
src/well_harness/timeline_engine/schema.py:72:        if self.kind == "start_deploy_sequence" and self.duration_s is not None and self.duration_s <= 0:
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:152:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
tests/fixtures/validation_schema_checker_report_asset_v1.json:49:    "expected_failure_kind": "status_mismatch",
tests/test_fault_taxonomy_schema.py:39:        self.assertIn("control-system fault_kind enum", result.stdout)
tests/test_fault_taxonomy_schema.py:64:            {"fault_taxonomy_payload", "control_system_spec_fault_kind_enum"},
tests/test_onboard_new_system_dry_run.py:29:    "kind": "well-harness-control-system-spec",
tests/test_onboard_new_system_dry_run.py:39:            "kind": "pilot_input",
tests/test_onboard_new_system_dry_run.py:50:            "kind": "sensor",
tests/test_onboard_new_system_dry_run.py:61:            "kind": "sensor",
tests/test_onboard_new_system_dry_run.py:72:            "kind": "command",
tests/test_onboard_new_system_dry_run.py:83:            "kind": "command",
tests/test_onboard_new_system_dry_run.py:94:            "kind": "sensor",
tests/test_onboard_new_system_dry_run.py:105:            "kind": "sensor",
tests/test_onboard_new_system_dry_run.py:236:            "fault_kind": "latched_no_unlock",
tests/test_onboard_new_system_dry_run.py:250:            "fault_kind": "bias_low",
tests/test_onboard_new_system_dry_run.py:313:    # missing kind, version, title, objective, source_of_truth,
tests/test_hardware_schema.py:8:- Wrong kind rejected by schema validation
tests/test_hardware_schema.py:32:    "kind": "thrust-reverser-hardware",
tests/test_hardware_schema.py:114:    def test_returns_correct_kind_and_version(self, tmp_path: Path) -> None:
tests/test_hardware_schema.py:117:        assert hw.kind == "thrust-reverser-hardware"
tests/test_hardware_schema.py:171:        assert hw.kind == "thrust-reverser-hardware"
tests/test_hardware_schema.py:199:class TestWrongKindRejected:
tests/test_hardware_schema.py:200:    """test_wrong_kind_rejected — wrong kind string is rejected by schema validation."""
tests/test_hardware_schema.py:202:    def test_rejects_wrong_kind(self, tmp_path: Path) -> None:
tests/test_hardware_schema.py:204:        bad["kind"] = "wrong-kind"
tests/test_hardware_schema.py:208:        assert "kind" in str(exc_info.value).lower() or "const" in str(exc_info.value).lower()
tests/test_hardware_schema.py:253:        assert hw.kind == "thrust-reverser-hardware"
docs/json_schema/validation_report_v1.schema.json:31:    "failure_kinds": [
docs/json_schema/validation_report_v1.schema.json:74:        "failure_kind": {
docs/json_schema/validation_report_v1.schema.json:75:          "$ref": "#/$defs/failureKind"
docs/json_schema/validation_report_v1.schema.json:111:        "failure_kind": {
docs/json_schema/validation_report_v1.schema.json:169:    "failureKind": {
docs/json_schema/validation_report_v1.schema.json:227:            "failure_kind"
docs/json_schema/validation_report_v1.schema.json:233:            "failure_kind": {
docs/json_schema/validation_report_v1.schema.json:234:              "$ref": "#/$defs/failureKind"
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1248:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1271:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1292:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1316:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1339:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:1363:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
docs/json_schema/knowledge_artifact_v1.schema.json:10:    "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:18:    "generated_at_utc",
docs/json_schema/knowledge_artifact_v1.schema.json:29:    "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:53:    "generated_at_utc": {
docs/json_schema/knowledge_artifact_v1.schema.json:171:        "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:184:        "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:224:        "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:236:        "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:259:        "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:268:        "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:284:        "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:304:        "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:368:        "kind",
docs/json_schema/knowledge_artifact_v1.schema.json:375:        "fault_kind",
docs/json_schema/knowledge_artifact_v1.schema.json:395:        "kind": {
docs/json_schema/knowledge_artifact_v1.schema.json:416:        "fault_kind": {
tests/test_thrust_reverser_intake_packet.py:46:    kinds = {sd.kind for sd in packet.source_documents}
tests/test_thrust_reverser_intake_packet.py:47:    assert kinds == {"python-controller", "docx", "yaml", "markdown"}, (
tests/test_thrust_reverser_intake_packet.py:48:        f"Expected 4 kinds (python-controller / docx / yaml / markdown), got {kinds}"
docs/json_schema/validation_schema_checker_report_v1.schema.json:37:    "failure_kinds": [
docs/json_schema/validation_schema_checker_report_v1.schema.json:57:    "failureKind": {
docs/json_schema/validation_schema_checker_report_v1.schema.json:118:        "failure_kind": {
docs/json_schema/validation_schema_checker_report_v1.schema.json:119:          "$ref": "#/$defs/failureKind"
docs/json_schema/validation_schema_checker_report_v1.schema.json:264:            "failure_kind"
docs/json_schema/validation_schema_checker_report_v1.schema.json:270:            "failure_kind": {
docs/json_schema/validation_schema_checker_report_v1.schema.json:271:              "$ref": "#/$defs/failureKind"
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:1789:   234	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:1825:   270	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:1844:   289	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2093:  1032	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2100:  1039	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2113:  1052	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2121:  1060	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2283:  1222	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2319:  1258	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:2776:   713	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:3154:  2583	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:3716:  2143	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:3717:  2144	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:4208:  1633	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:4209:  1634	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:4210:  1635	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:4213:  1638	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:5160:  3104	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:5171:  3115	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:5209:  3153	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:5210:  3154	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:5383:  3327	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
tests/test_fault_taxonomy.py:6:    FAULT_TAXONOMY_KIND,
tests/test_fault_taxonomy.py:9:    SUPPORTED_FAULT_KINDS,
tests/test_fault_taxonomy.py:11:    validate_fault_kind,
tests/test_fault_taxonomy.py:24:    def test_fault_taxonomy_lists_supported_fault_kinds(self):
tests/test_fault_taxonomy.py:25:        self.assertIn("bias_low", SUPPORTED_FAULT_KINDS)
tests/test_fault_taxonomy.py:26:        self.assertIn("command_path_failure", SUPPORTED_FAULT_KINDS)
tests/test_fault_taxonomy.py:27:        self.assertEqual("stuck_low", validate_fault_kind("stuck_low"))
tests/test_fault_taxonomy.py:34:        self.assertEqual(FAULT_TAXONOMY_KIND, schema["properties"]["kind"]["const"])
tests/test_fault_taxonomy.py:54:    def test_unknown_fault_kind_raises_helpful_error(self):
tests/test_fault_taxonomy.py:55:        with self.assertRaisesRegex(ValueError, "fault_kind must be one of"):
tests/test_fault_taxonomy.py:56:            validate_fault_kind("mystery_fault")
docs/json_schema/control_system_spec_v1.schema.json:10:    "kind",
docs/json_schema/control_system_spec_v1.schema.json:28:    "kind": {
docs/json_schema/control_system_spec_v1.schema.json:124:    "faultKindValue": {
docs/json_schema/control_system_spec_v1.schema.json:143:        "kind",
docs/json_schema/control_system_spec_v1.schema.json:158:        "kind": {
docs/json_schema/control_system_spec_v1.schema.json:372:        "fault_kind",
docs/json_schema/control_system_spec_v1.schema.json:385:        "fault_kind": {
docs/json_schema/control_system_spec_v1.schema.json:386:          "$ref": "#/$defs/faultKindValue"
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1434:    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1755:function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1762:  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1775:function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1783:  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1945:      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:1981:      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2459:      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2495:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2514:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2860:  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2861:  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2862:  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:2865:  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:3376:    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:3377:      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:3818:      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:4343:  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:4354:  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:4392:  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:4393:  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:4566:  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
src/well_harness/timeline_engine/player.py:111:                if event.kind == "mark_phase":
src/well_harness/timeline_engine/player.py:113:                events_fired_ids.append(f"{event.kind}@{event.t_s:.3f}:{event.target}")
src/well_harness/timeline_engine/player.py:193:                    event.kind == "assert_condition"
src/well_harness/timeline_engine/player.py:247:        kind = event.kind
src/well_harness/timeline_engine/player.py:248:        if kind == "set_input":
src/well_harness/timeline_engine/player.py:253:        if kind == "ramp_input":
src/well_harness/timeline_engine/player.py:269:        if kind == "start_deploy_sequence":
docs/json_schema/second_system_smoke_v1.schema.json:10:    "kind",
docs/json_schema/second_system_smoke_v1.schema.json:19:    "bundle_kind",
docs/json_schema/second_system_smoke_v1.schema.json:35:    "kind": {
docs/json_schema/second_system_smoke_v1.schema.json:66:    "bundle_kind": {
src/well_harness/timeline_engine/fault_schedule.py:43:        if event.kind == "inject_fault":
src/well_harness/timeline_engine/fault_schedule.py:59:        elif event.kind == "clear_fault":
docs/json_schema/playback_trace_v1.schema.json:10:    "kind",
docs/json_schema/playback_trace_v1.schema.json:30:    "kind": {
docs/json_schema/playback_trace_v1.schema.json:119:        "kind",
docs/json_schema/playback_trace_v1.schema.json:131:        "kind": {
docs/json_schema/playback_trace_v1.schema.json:154:        "kind",
docs/json_schema/playback_trace_v1.schema.json:163:        "kind": {
tests/fixtures/system_intake_packet_v1.json:9:      "kind": "pdf",
tests/fixtures/system_intake_packet_v1.json:17:      "kind": "markdown",
tests/fixtures/system_intake_packet_v1.json:28:      "kind": "switch",
tests/fixtures/system_intake_packet_v1.json:38:      "kind": "sensor",
tests/fixtures/system_intake_packet_v1.json:48:      "kind": "command",
tests/fixtures/system_intake_packet_v1.json:115:      "fault_kind": "bias_low",
docs/json_schema/fault_taxonomy_v1.schema.json:5:  "description": "Published reusable taxonomy for supported control-system fault kinds.",
docs/json_schema/fault_taxonomy_v1.schema.json:10:    "kind",
docs/json_schema/fault_taxonomy_v1.schema.json:12:    "fault_kinds"
docs/json_schema/fault_taxonomy_v1.schema.json:18:    "kind": {
docs/json_schema/fault_taxonomy_v1.schema.json:24:    "fault_kinds": {
docs/json_schema/fault_taxonomy_v1.schema.json:28:        "$ref": "#/$defs/faultKindEntry"
docs/json_schema/fault_taxonomy_v1.schema.json:37:    "faultKindEntry": {
docs/json_schema/fault_taxonomy_v1.schema.json:41:        "fault_kind",
docs/json_schema/fault_taxonomy_v1.schema.json:48:        "fault_kind": {
src/well_harness/timeline_engine/validator.py:8:    EVENT_KINDS,
src/well_harness/timeline_engine/validator.py:61:    kind = raw.get("kind")
src/well_harness/timeline_engine/validator.py:62:    if kind not in EVENT_KINDS:
src/well_harness/timeline_engine/validator.py:63:        raise ValidationError(f"{field}.kind", f"must be one of {EVENT_KINDS}")
src/well_harness/timeline_engine/validator.py:73:    if kind == "ramp_input" and (duration_s is None or duration_s <= 0):
src/well_harness/timeline_engine/validator.py:87:        kind=kind,
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:918:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:941:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:962:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:986:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1009:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1033:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:3753:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:3789:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:3808:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4234:   705	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4559:  1024	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4566:  1031	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4579:  1044	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4587:  1052	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4749:  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:4785:  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5162:  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5163:  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5164:  1627	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5167:  1630	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5641:  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5652:  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5690:  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5691:  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:5864:  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:6122:  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:6684:  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:6685:  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
tests/test_controller_adapter.py:8:    CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
tests/test_controller_adapter.py:55:        self.assertEqual(adapter.metadata.truth_kind, "python-controller-adapter")
tests/test_controller_adapter.py:64:        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_KIND, payload["kind"])
tests/test_controller_adapter.py:75:        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_KIND, schema["properties"]["kind"]["const"])
docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:10:    "kind",
docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:14:    "truth_kind",
docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:22:    "kind": {
docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:34:    "truth_kind": {
tests/test_controller_truth_metadata_schema_extension.py:31:    CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
tests/test_controller_truth_metadata_schema_extension.py:94:        truth_kind="test-kind",
tests/test_controller_truth_metadata_schema_extension.py:101:        "kind",
tests/test_controller_truth_metadata_schema_extension.py:105:        "truth_kind",
tests/test_controller_truth_metadata_schema_extension.py:120:        self.assertEqual(payload["kind"], CONTROLLER_TRUTH_ADAPTER_METADATA_KIND)
tests/test_controller_truth_metadata_schema_extension.py:164:            "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
tests/test_controller_truth_metadata_schema_extension.py:168:            "truth_kind": "k",
tests/fixtures/validation_report_asset_v1.json:62:      "expected_failure_kind": "cli_exit",
tests/fixtures/validation_report_asset_v1.json:71:        "failure_kind": "cli_exit",
tests/fixtures/validation_report_asset_v1.json:87:      "expected_failure_kind": "schema_unavailable",
tests/fixtures/validation_report_asset_v1.json:103:      "expected_failure_kind": "schema_validation",
tests/fixtures/validation_report_asset_v1.json:112:        "failure_kind": "schema_validation",
docs/json_schema/workbench_archive_manifest_v1.schema.json:9:    "kind",
docs/json_schema/workbench_archive_manifest_v1.schema.json:21:    "kind": {
docs/json_schema/workbench_archive_manifest_v1.schema.json:71:        "bundle_kind",
docs/json_schema/workbench_archive_manifest_v1.schema.json:80:        "bundle_kind": {
src/well_harness/adapters/landing_gear_intake_packet.py:41:            kind="python-adapter",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:882:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:905:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:926:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:950:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:973:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:997:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:3295:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:3331:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:3350:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:3774:   705	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4093:  1024	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4100:  1031	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4113:  1044	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4121:  1052	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4283:  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4319:  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4694:  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4695:  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4696:  1627	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:4699:  1630	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:5204:  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:5205:  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:5644:  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6165:  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6176:  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6214:  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6215:  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6388:  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
docs/json_schema/fault_diagnosis_v1.schema.json:10:    "kind",
docs/json_schema/fault_diagnosis_v1.schema.json:17:    "fault_kind",
docs/json_schema/fault_diagnosis_v1.schema.json:37:    "kind": {
docs/json_schema/fault_diagnosis_v1.schema.json:58:    "fault_kind": {
docs/json_schema/fault_diagnosis_v1.schema.json:130:        "kind",
docs/json_schema/fault_diagnosis_v1.schema.json:143:        "kind": {
docs/json_schema/fault_diagnosis_v1.schema.json:183:        "kind",
docs/json_schema/fault_diagnosis_v1.schema.json:195:        "kind": {
docs/json_schema/fault_diagnosis_v1.schema.json:218:        "kind",
docs/json_schema/fault_diagnosis_v1.schema.json:227:        "kind": {
docs/json_schema/fault_diagnosis_v1.schema.json:243:        "kind",
docs/json_schema/fault_diagnosis_v1.schema.json:263:        "kind": {
tests/test_second_system_smoke.py:9:    SECOND_SYSTEM_SMOKE_KIND,
tests/test_second_system_smoke.py:28:        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, report.kind)
tests/test_second_system_smoke.py:35:        self.assertEqual("adapter_runtime_proof", report.bundle_kind)
tests/test_second_system_smoke.py:52:        self.assertEqual("full_workbench_bundle", report.bundle_kind)
tests/test_second_system_smoke.py:60:        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, payload["kind"])
tests/test_second_system_smoke.py:66:        self.assertEqual("adapter_runtime_proof", payload["bundle_kind"])
tests/test_second_system_smoke.py:76:        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, schema["properties"]["kind"]["const"])
tests/test_second_system_smoke.py:104:        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, payload["kind"])
docs/json_schema/workbench_bundle_v1.schema.json:10:    "kind",
docs/json_schema/workbench_bundle_v1.schema.json:14:    "bundle_kind",
docs/json_schema/workbench_bundle_v1.schema.json:29:    "kind": {
docs/json_schema/workbench_bundle_v1.schema.json:41:    "bundle_kind": {
docs/json_schema/workbench_bundle_v1.schema.json:122:        "kind",
docs/json_schema/workbench_bundle_v1.schema.json:129:        "kind": {
docs/json_schema/workbench_bundle_v1.schema.json:141:        "kind",
docs/json_schema/workbench_bundle_v1.schema.json:148:        "kind": {
docs/json_schema/workbench_bundle_v1.schema.json:160:        "kind",
docs/json_schema/workbench_bundle_v1.schema.json:167:        "kind": {
src/well_harness/adapters/bleed_air_adapter.py:63:    truth_kind="python-generic-truth-adapter",
src/well_harness/adapters/bleed_air_adapter.py:117:                kind="sensor",
src/well_harness/adapters/bleed_air_adapter.py:128:                kind="command",
src/well_harness/adapters/bleed_air_adapter.py:139:                kind="sensor",
src/well_harness/adapters/bleed_air_adapter.py:150:                kind="sensor",
src/well_harness/adapters/bleed_air_adapter.py:161:                kind="sensor",
src/well_harness/adapters/bleed_air_adapter.py:426:                fault_kind="stuck_high",
src/well_harness/adapters/bleed_air_adapter.py:448:                fault_kind="stuck_low",
src/well_harness/adapters/bleed_air_adapter.py:470:                fault_kind="bias_high",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:104:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1649:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1672:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1693:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1717:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1740:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1764:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
src/well_harness/adapters/landing_gear_adapter.py:46:    truth_kind="python-generic-truth-adapter",
src/well_harness/adapters/landing_gear_adapter.py:95:                kind="pilot_input",
src/well_harness/adapters/landing_gear_adapter.py:105:                kind="sensor",
src/well_harness/adapters/landing_gear_adapter.py:115:                kind="sensor",
src/well_harness/adapters/landing_gear_adapter.py:125:                kind="command",
src/well_harness/adapters/landing_gear_adapter.py:135:                kind="command",
src/well_harness/adapters/landing_gear_adapter.py:145:                kind="sensor",
src/well_harness/adapters/landing_gear_adapter.py:155:                kind="sensor",
src/well_harness/adapters/landing_gear_adapter.py:285:                fault_kind="latched_no_unlock",
src/well_harness/adapters/landing_gear_adapter.py:294:                fault_kind="bias_low",
src/well_harness/adapters/bleed_air_intake_packet.py:48:            kind="python-adapter",
docs/json_schema/two_system_runtime_comparison_v1.schema.json:10:    "kind",
docs/json_schema/two_system_runtime_comparison_v1.schema.json:25:    "kind": {
src/well_harness/adapters/c919_etras_intake_packet.py:46:            kind="python-adapter",
src/well_harness/adapters/c919_etras_intake_packet.py:60:            kind="pdf",
src/well_harness/adapters/c919_etras_intake_packet.py:80:            kind="yaml",
src/well_harness/adapters/efds_adapter.py:40:    truth_kind="python-generic-truth-adapter",
src/well_harness/adapters/efds_adapter.py:90:                kind="sensor",
src/well_harness/adapters/efds_adapter.py:100:                kind="sensor",
src/well_harness/adapters/efds_adapter.py:110:                kind="sensor",
src/well_harness/adapters/efds_adapter.py:120:                kind="sensor",
src/well_harness/adapters/efds_adapter.py:130:                kind="sensor",
src/well_harness/adapters/efds_adapter.py:141:                kind="logic_gate",
src/well_harness/adapters/efds_adapter.py:151:                kind="logic_gate",
src/well_harness/adapters/efds_adapter.py:161:                kind="logic_gate",
src/well_harness/adapters/efds_adapter.py:172:                kind="pilot_input",
src/well_harness/adapters/efds_adapter.py:182:                kind="pilot_input",
src/well_harness/adapters/efds_adapter.py:192:                kind="pilot_input",
src/well_harness/adapters/efds_adapter.py:203:                kind="actuator",
src/well_harness/adapters/efds_adapter.py:213:                kind="actuator",
src/well_harness/adapters/efds_adapter.py:301:                fault_kind="open_circuit",
src/well_harness/adapters/efds_adapter.py:310:                fault_kind="bias_high",
src/well_harness/adapters/efds_adapter.py:319:                fault_kind="latched_no_unlock",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:252:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:722:      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1567:src/well_harness/static/workbench.js:226:      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1572:src/well_harness/static/workbench.js:262:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1579:src/well_harness/static/workbench.js:281:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1632:src/well_harness/static/workbench.js:2575:      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1676:src/well_harness/static/workbench.js:3319:  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1735:226:      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1740:262:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1747:281:    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1799:2575:      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1843:3319:  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
docs/json_schema/validation_schema_runner_report_v1.schema.json:31:    "failure_kinds": [
docs/json_schema/validation_schema_runner_report_v1.schema.json:80:        "failure_kind": {
docs/json_schema/validation_schema_runner_report_v1.schema.json:81:          "$ref": "#/$defs/failureKind"
docs/json_schema/validation_schema_runner_report_v1.schema.json:180:    "failureKind": {
docs/json_schema/validation_schema_runner_report_v1.schema.json:240:            "failure_kind"
docs/json_schema/validation_schema_runner_report_v1.schema.json:246:            "failure_kind": {
docs/json_schema/validation_schema_runner_report_v1.schema.json:247:              "$ref": "#/$defs/failureKind"
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:1276:  1253	                "bundle_kind": bundle.get("bundle_kind"),
src/well_harness/adapters/thrust_reverser_intake_packet.py:63:            kind="python-controller",
src/well_harness/adapters/thrust_reverser_intake_packet.py:77:            kind="docx",
src/well_harness/adapters/thrust_reverser_intake_packet.py:95:            kind="yaml",
src/well_harness/adapters/thrust_reverser_intake_packet.py:109:            kind="markdown",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:33:New endpoint: `GET /api/workbench/state-of-world` returning advisory payload with `kind: "advisory"` flag, `_source` sibling for every value, and `generated_at` ISO timestamp. POST to the endpoint must return 404/405 (read-only contract).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:43:- `tests/test_workbench_state_of_world_bar.py` — NEW (15 tests covering payload contract, kind=advisory, ints, ISO timestamp, live endpoint, HTML slots, JS wiring, POST→404/405)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:60:- Direct payload smoke: `workbench_state_of_world_payload()` returns `kind=advisory`, `truth_engine_sha=<git short SHA>`, `recent_e2e_label="175 tests OK"`, `adversarial_label="8/8 shared validation pass"`, `open_known_issues_count=0`
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:108:829:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1123:    55	        data-status-kind="advisory"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1540:   250	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1576:   286	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1595:   305	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1682:    68	        "kind",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1684:    70	        "truth_engine_sha_source",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1686:    72	        "recent_e2e_source",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1688:    74	        "adversarial_source",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1690:    76	        "open_known_issues_source",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1691:    77	        "last_executed_evidence",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1692:    78	        "generated_at",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1697:    83	def test_state_of_world_kind_is_advisory() -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1699:    85	    reading. The 'advisory' kind is the contract."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1701:    87	    assert payload["kind"] == "advisory"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1719:   105	def test_state_of_world_generated_at_is_iso() -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1721:   107	    ts = payload["generated_at"]
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1732:   118	    assert body.get("kind") == "advisory"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1741:   127	    assert 'data-status-kind="advisory"' in html
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1816:tests/test_workbench_state_of_world_bar.py:83:def test_state_of_world_kind_is_advisory() -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1822:tests/test_workbench_state_of_world_bar.py:105:def test_state_of_world_generated_at_is_iso() -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1962:  1344	        "last_executed_evidence": "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1979:  1361	        out["last_executed_evidence"] = m.group(1)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2003:  1385	    `kind: "advisory"` flag is the contract that this is NOT a live
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2007:  1389	        "kind": "advisory",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2009:  1391	        "truth_engine_sha_source": "git rev-parse --short HEAD",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2011:  1393	        "recent_e2e_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2013:  1395	        "adversarial_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2015:  1397	        "open_known_issues_source": "docs/known-issues/ (file count)",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2016:  1398	        "last_executed_evidence": evidence["last_executed_evidence"] or "—",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2017:  1399	        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2423:    print('GET_KIND', payload.get('kind'))
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2428:    print('GET_EVIDENCE', payload.get('last_executed_evidence'))
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2449:        'kind': payload.get('kind') == payload2.get('kind'),
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2454:        'evidence': payload.get('last_executed_evidence') == payload2.get('last_executed_evidence'),
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2465:GET_KIND advisory
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2478:STABLE_NON_TIMESTAMP {'kind': True, 'sha': True, 'recent_e2e': True, 'adversarial': True, 'open_issues': True, 'evidence': True}
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2481:我在对照实现和口头合同时发现了一个边界点：payload 里多带了 `last_executed_evidence`，但它不像另外四个 advisory 值那样有对应 `_source` sibling。我先看一下 phase inventory 是否把它列为正式合同字段，避免把“额外调试信息”误判成接口违约。
docs/json_schema/hardware_schema_v1.schema.json:9:    "kind",
docs/json_schema/hardware_schema_v1.schema.json:15:    "kind": {
src/well_harness/adapters/c919_etras_adapter.py:151:    truth_kind="python-generic-truth-adapter",
src/well_harness/adapters/c919_etras_adapter.py:282:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:295:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:306:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:319:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:332:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:343:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:356:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:373:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:383:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:396:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:409:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:419:                kind="sensor",
src/well_harness/adapters/c919_etras_adapter.py:430:                kind="command",
src/well_harness/adapters/c919_etras_adapter.py:442:                kind="command",
src/well_harness/adapters/c919_etras_adapter.py:455:                kind="command",
src/well_harness/adapters/c919_etras_adapter.py:468:                kind="command",
src/well_harness/adapters/c919_etras_adapter.py:482:                kind="command",
src/well_harness/adapters/c919_etras_adapter.py:1054:                fault_kind="stuck_high",
src/well_harness/adapters/c919_etras_adapter.py:1078:                fault_kind="open_circuit",
src/well_harness/adapters/c919_etras_adapter.py:1100:                fault_kind="stuck_high",
src/well_harness/adapters/c919_etras_adapter.py:1124:                fault_kind="command_path_failure",
src/well_harness/adapters/c919_etras_adapter.py:1147:                fault_kind="bias_low",
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:119:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:1394:src/well_harness/workbench_bundle.py:26:WORKBENCH_BUNDLE_KIND = "well-harness-workbench-bundle"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:1396:src/well_harness/workbench_bundle.py:29:ARCHIVE_MANIFEST_KIND = "well-harness-workbench-archive-manifest"
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:1423:src/well_harness/workbench_bundle.py:617:        bundle_kind="full_workbench_bundle",
docs/co-development/api-contract.md:21:- **错误码：** 格式 `<backend>_<kind>`（例：`minimax_timeout` / `ollama_unreachable`）；前端降级徽标依赖前缀匹配，不依赖完整字符串
docs/co-development/api-contract.md:185:| 错误码扩展 | 新 backend 加入时保持 `<backend>_<kind>` 格式 |
docs/demo/local_model_poc.md:123:  `_BACKENDS` dict；保持错误码前缀匹配 `<backend>_<kind>` 以复用前端 UI 契约。
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1482:       <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1506:       <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1527:       <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1553:       <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1576:       <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1600:       <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2195:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2218:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2239:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2263:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2286:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2310:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:4881:   705	    kind: "well-harness-workbench-browser-workspace",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5404:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5440:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5459:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5708:  1024	function documentKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5715:  1031	  return labels[kind] || kind || "未知来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5728:  1044	function signalKindLabel(kind) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5736:  1052	  return labels[kind] || kind || "未知类型";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5898:  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:5934:  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:6311:  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:6312:  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:6313:  1627	  if (documentKinds.length > 1) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:6316:  1630	  if (documentKinds.includes("pdf")) {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:6767:  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:7329:  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:7330:  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8230:  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8241:  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8279:  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8280:  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:8453:  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt:18:New endpoint: `GET /api/workbench/state-of-world` returning advisory payload with `kind: "advisory"` flag, `_source` sibling for every value, and `generated_at` ISO timestamp. POST to the endpoint must return 404/405 (read-only contract).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt:28:- `tests/test_workbench_state_of_world_bar.py` — NEW (15 tests covering payload contract, kind=advisory, ints, ISO timestamp, live endpoint, HTML slots, JS wiring, POST→404/405)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt:45:- Direct payload smoke: `workbench_state_of_world_payload()` returns `kind=advisory`, `truth_engine_sha=<git short SHA>`, `recent_e2e_label="175 tests OK"`, `adversarial_label="8/8 shared validation pass"`, `open_known_issues_count=0`
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:300:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
tests/test_workbench_bundle_schema.py:40:        self.assertIn("bundle_kind=full_workbench_bundle", result.stdout)
tests/test_workbench_bundle_schema.py:41:        self.assertIn("bundle_kind=clarification_follow_up", result.stdout)
tests/test_workbench_bundle_schema.py:64:        self.assertIn("clarification_follow_up", {item["bundle_kind"] for item in payload["results"]})
tests/test_workbench_bundle_schema.py:65:        self.assertIn("full_workbench_bundle", {item["bundle_kind"] for item in payload["results"]})
docs/demo/faq.md:201:在 `_BACKENDS` dict 里加一行——**预估 <50 行代码**。错误码用 `<backend>_<kind>`
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:38:  "kind": "advisory",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:40:  "truth_engine_sha_source": "git rev-parse --short HEAD",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:42:  "recent_e2e_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:44:  "adversarial_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:46:  "open_known_issues_source": "docs/known-issues/ (file count)",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:47:  "last_executed_evidence": "<latest stamp>" | "—",
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:48:  "generated_at": "<ISO8601 Z>"
.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:63:Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new endpoint is explicitly classified as `kind: "advisory"` — it never claims to be a live truth-engine reading.
tests/test_gsd_notion_sync.py:717:        self.assertEqual("P1 phase readiness + 旧失败 Gap 裁决", brief.intervention_kind)
tests/test_gsd_notion_sync.py:749:        self.assertEqual("失败阻塞分流审查", brief.intervention_kind)
tests/test_gsd_notion_sync.py:780:        self.assertEqual("当前无需 Opus 审查", brief.intervention_kind)
tests/test_gsd_notion_sync.py:810:        self.assertEqual("Phase 收口与下一步优先级审查", brief.intervention_kind)
tests/test_gsd_notion_sync.py:2281:                    return_value={"intervention_kind": "当前无需 Opus 审查", "review_target": "P6 / P6-06"},
tests/test_gsd_notion_sync.py:2351:                patch("tools.gsd_notion_sync.write_notion_outcome", return_value={"opus_review_brief": {"intervention_kind": "当前无需 Opus 审查"}}),
tests/test_gsd_notion_sync.py:2696:        self.assertEqual("当前无需 Opus 审查", payload["intervention_kind"])
tests/test_gsd_notion_sync.py:3155:                    {"id": "gate-legacy", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "superseded"},
tests/test_gsd_notion_sync.py:3156:                    {"id": "plan-legacy", "kind": "plan", "title": "P1-02 消除手动浏览器 QA 依赖", "reason": "superseded"},
tests/test_gsd_notion_sync.py:3157:                    {"id": "already-archived", "kind": "plan", "title": "Archived already", "reason": "superseded"},
tests/test_gsd_notion_sync.py:3208:                    {"id": "gate-legacy", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "superseded"},
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:104:778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:236:- 7 event kinds: set_input, ramp_input, inject_fault, clear_fault, mark_phase, assert_condition, start_deploy_sequence
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1080:    56	      <span class="ws-tile-kind">学习与演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1103:    79	      <span class="ws-tile-kind">工程师调试</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1124:   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1148:   124	      <span class="ws-tile-kind">客户问题复现</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1171:   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1195:   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1760:   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1796:   262	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1815:   281	    bundle_kind: bundle.bundle_kind || "",
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:778:   250	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",

Completed diff inspection, code/test review, and repo-scoped live probe with GET/POST verification.
  ✓ Inspect branch diff and confirm truth-engine red-line files are untouched
  ✓ Review backend/frontend/tests for endpoint contract, advisory semantics, source provenance, and read-only behavior
  ✓ Run live probe(s) against demo_server and verify response shape plus POST behavior
  → Issue P4 verdict with cited findings and residual risks only
codex
**APPROVE_WITH_NITS**

- `NIT` [tests/test_workbench_state_of_world_bar.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_state_of_world_bar.py:65) (65-80, 83-119): the suite locks field presence, `kind=advisory`, basic type/ISO shape, HTML slots, JS hook text, and POST rejection, but it does not lock the `_source` values, `last_executed_evidence`, or the documented fallback branches in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1314) (git missing, missing `qa_report.md`, missing `docs/known-issues/`). That leaves the provenance and graceful-degradation claims partially unguarded.
- `NIT` [src/well_harness/demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1365) (1365-1377, 1396-1397): `_open_known_issues_count()` can read either `docs/known-issues/` or `docs/known_issues/`, but `open_known_issues_source` always reports `docs/known-issues/ (file count)`. If the underscore fallback is ever the real source, the provenance label becomes inaccurate.

Live probe on the current worktree was clean. I booted `DemoRequestHandler` from the reviewed checkout with `PYTHONPATH=src:.`; `GET /api/workbench/state-of-world` returned `200` with `kind=advisory`, `truth_engine_sha=166d8d5`, `recent_e2e_label=175 tests OK`, `adversarial_label=8/8 shared validation pass`, `open_known_issues_count=0`, and the evidence stamp matching [docs/coordination/qa_report.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/docs/coordination/qa_report.md:9) (9-16). `POST /api/workbench/state-of-world` returned `404`, and a second GET matched all non-timestamp fields, which supports the read-only/idempotent contract.

Red-line check also passed: `git diff --name-only main..166d8d5` only shows `.planning`, `src/well_harness/demo_server.py`, `src/well_harness/static/*`, and `tests/test_workbench_state_of_world_bar.py`; no changes under `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`. I re-ran `pytest -q tests/test_workbench_state_of_world_bar.py` and got `15 passed`; I did not re-run the full `991`-test suite in this review pass.

**P4 — V&V Engineer (Tier-B, E11-06)**

tokens used
89,107
**APPROVE_WITH_NITS**

- `NIT` [tests/test_workbench_state_of_world_bar.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_state_of_world_bar.py:65) (65-80, 83-119): the suite locks field presence, `kind=advisory`, basic type/ISO shape, HTML slots, JS hook text, and POST rejection, but it does not lock the `_source` values, `last_executed_evidence`, or the documented fallback branches in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1314) (git missing, missing `qa_report.md`, missing `docs/known-issues/`). That leaves the provenance and graceful-degradation claims partially unguarded.
- `NIT` [src/well_harness/demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1365) (1365-1377, 1396-1397): `_open_known_issues_count()` can read either `docs/known-issues/` or `docs/known_issues/`, but `open_known_issues_source` always reports `docs/known-issues/ (file count)`. If the underscore fallback is ever the real source, the provenance label becomes inaccurate.

Live probe on the current worktree was clean. I booted `DemoRequestHandler` from the reviewed checkout with `PYTHONPATH=src:.`; `GET /api/workbench/state-of-world` returned `200` with `kind=advisory`, `truth_engine_sha=166d8d5`, `recent_e2e_label=175 tests OK`, `adversarial_label=8/8 shared validation pass`, `open_known_issues_count=0`, and the evidence stamp matching [docs/coordination/qa_report.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/docs/coordination/qa_report.md:9) (9-16). `POST /api/workbench/state-of-world` returned `404`, and a second GET matched all non-timestamp fields, which supports the read-only/idempotent contract.

Red-line check also passed: `git diff --name-only main..166d8d5` only shows `.planning`, `src/well_harness/demo_server.py`, `src/well_harness/static/*`, and `tests/test_workbench_state_of_world_bar.py`; no changes under `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`. I re-ran `pytest -q tests/test_workbench_state_of_world_bar.py` and got `15 passed`; I did not re-run the full `991`-test suite in this review pass.

**P4 — V&V Engineer (Tier-B, E11-06)**

