2026-04-26T03:58:23.067661Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T03:58:23.067738Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc7f0-3b5c-7640-bb8a-c42ecdf6d471
--------
user
You are Codex GPT-5.4 acting as **Persona P5 — Truth-Engine Red-Line & JS/HTML Lockstep Auditor** (Tier-A persona pipeline, E11-15e sub-phase, R1).

Read `.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md` for sub-phase scope, files, and verification baseline.

## Your specific lens (P5 — Truth-Engine Red-Line & JS/HTML Lockstep Auditor)

The truth-engine red line (per `.planning/constitution.md`) forbids display-copy work from touching `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, and `demo_server.py`. E11-15e claims compliance and adds a guard test. Your job is to verify the red line is honored and the new lockstep contracts won't drift.

1. **Truth-engine red-line compliance**
   - `git diff main..83d69e4 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py` — should be empty.
   - The new test `test_e11_15e_does_not_touch_truth_engine_backend` at `tests/test_workbench_e11_15e_chinese_first_bundle.py` Section 7 scans these 4 backend files for the 23 Chinese display strings. Verify:
     - All 23 Chinese display strings introduced in this PR are in the guard's `e11_15e_chinese` list (no missing).
     - The 4 backend file paths are correct and exhaustive (any other backend file with truth-engine status?).
     - Note: `demo_server.py` is one file but `adapters/` is a directory — the guard reads `controller.py`, `runner.py`, `models.py`, `demo_server.py` only. Should it also iterate `src/well_harness/adapters/*.py`?

2. **JS/HTML lockstep correctness**
   The static HTML chip text `<strong>手动（仅参考）· Manual (advisory)</strong>` (workbench.html:42) and the JS dynamic write at workbench.js:3788 (`label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";`) must remain consistent. Audit:
   - On first mode switch, JS replaces the static HTML's `<strong>` text. Both branches now produce bilingual output. ✅
   - Are there OTHER JS write paths to `workbench-feedback-mode strong` that bypass this function? grep workbench.js for `feedback-mode`, `feedbackMode`, `data-feedback-mode` write operations.
   - Does workbench.js have any `innerHTML` / `textContent` assignment to `workbench-trust-banner-headline` / `workbench-authority-banner-headline` / state-of-world labels / boot status that could bypass the bilingual contract?

3. **Truth-engine red-line guard scope**
   - The guard scans for **Chinese display strings** in backend. Good defense.
   - Should the guard ALSO assert that workbench.html / workbench.js DON'T import or reference truth-engine values (e.g., that the bilingualization isn't accidentally pulling truth from `controller.py`)? Probably out of scope — copy is static — but worth a sanity check.

4. **Static-HTML snapshot vs JS-dynamic state**
   - When the demo loads, the static HTML serves `<strong>手动（仅参考）· Manual (advisory)</strong>`. JS hydration fires `installFeedbackModeAffordance` which calls `setFeedbackMode("manual_feedback_override")`, which re-writes the chip text. Verify the JS literal exactly matches the static HTML (no whitespace drift, no Chinese-character variant).
   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?

5. **Constitutional adapter-interface rule**
   - Per `.planning/constitution.md`: "新系统 truth 只能通过显式 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path." E11-15e adds zero new truth paths. Confirm.

## Files to inspect

- `git diff main..83d69e4` (full diff)
- `src/well_harness/controller.py`, `runner.py`, `models.py`, `demo_server.py`, `adapters/` (verify untouched)
- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.js` (especially `installFeedbackModeAffordance`, `setFeedbackMode`, `bootWorkbench*Panel`)
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` Sections 5, 7
- `.planning/constitution.md` (truth-engine red-line definitions)

## Out of scope for your lens (other personas cover these)

- P1: engineer-task-flow regression
- P2: surface-inventory honesty + closure-claim guards
- P3: bilingual copy quality + convention adherence
- P4: lockstep test contract preservation

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Then list findings with severity tags (`BLOCKER` / `IMPORTANT` / `NIT`), each with `file:line` reference and `Suggested fix:` bullet.

If the truth-engine red line is breached, flag as `BLOCKER` minimum.

codex
Reviewing the E11-15e slice as a read-only audit with the P5 lens. I’m loading the shared sub-phase context, constitution red line, and the exact diff/tests first, then I’ll verify whether the backend truth-engine boundary stayed untouched and whether the JS/HTML lockstep can drift.
exec
/bin/zsh -lc 'rg -n "LogicMVP|E11-15e|workbench|truth-engine|red-line" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.agents/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
Using `gsd-code-review` as the review workflow and the repo’s constitutional rules as the governing contract. I’ve confirmed the task is a read-only audit, so I’m scoping the exact touched surfaces, the guard test, and every JS write path that could bypass the bilingual lockstep.
  → Load sub-phase context and constitutional red-line definitions
  • Inspect diff vs main and verify backend truth-engine files remain untouched
  • Audit JS/HTML lockstep and guard-test scope for drift or blind spots
  • Summarize findings with verdict and file/line references
exec
/bin/zsh -lc "sed -n '1,240p' .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,260p' .planning/constitution.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15e — shared context for Tier-A persona prompts

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**PR:** #30
**HEAD:** `83d69e4`
**Tier:** A (copy_diff_lines ~38, REWRITE rows = 22; per constitution Tier-A iff ≥10 lines AND ≥3 REWRITE)
**Round-robin lead:** P3 (successor of E11-15d's P2)

## What E11-15e ships

Bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review (`tests/test_workbench_approval_flow_polish.py:189-194`).

**Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim so prior substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar) keep passing without contract churn.

## Files in scope

- `src/well_harness/static/workbench.html` — 21 REWRITE strings
- `src/well_harness/static/workbench.js` — 1 lockstep edit at line 3788 (feedback-mode chip dynamic text, both `truth_engine` and `manual_feedback_override` branches bilingualized)
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` — 67 new test cases (positive bilingual locks + stale-English negative guards + English-suffix preservation + structural anchors + JS lockstep + live-served route + truth-engine red-line guard)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan

## Files explicitly NOT in scope (truth-engine red line)

`controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`. The new lockstep guard `test_e11_15e_does_not_touch_truth_engine_backend` scans these 4 backend files for any of the 23 Chinese display strings introduced in this sub-phase.

## Verification baseline

- 67/67 new tests pass
- 188/188 prior workbench tests pass (lockstep contracts preserved)
- 1221/1221 full suite passes (0 regressions, 35 deselected per default markers)

## Surface honesty pledge

E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.

## Codex degradation contingency

If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).

 succeeded in 0ms:
# AI FANTUI LogicMVP Constitution

> **Constitution version:** v2.4 (2026-04-25, +Recursive Coherence Drift Mitigation for doc-only rule-bundle PRs, ratified by Opus 4.7 strategic review)
>
> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
>
> **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
>
> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
>
> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
>
> **v2.4 增量 (2026-04-25, ratified by Opus 4.7):** 追加 §Recursive Coherence Drift Mitigation — applies only to doc-only rule-bundle PRs (objective trigger: modifies ≥1 constitution rule body AND adds/rewrites ≥2 cross-doc pointers, OR labeled `governance-bundle`). Triggers Opus consultation at R3 (普通 PR 仍 R4); R5 mandatory drift-acceptance declaration; R6 hard cap (binary: rollback or merge-with-explicit-drift). Forbidden superlatives in commit/PR bodies. 1 canonical source at `<path>`; downstream references may drift in wording but must not contradict canonical. Source: RETRO-V61-055 §3 (PR #15) + Opus 4.7 strategic review same day. v2.2 / v2.3 / governance bundle #2 / Verbatim Exception / RETRO 序号 / Self-Pass-Rate 全部不动。

## Milestone Hold (historical, 2026-04-13)

**Declared:** 2026-04-13
**Scope:** Milestone 4 (Phases P4–P11)
**Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**

All P0 through P11 phases are complete. The project is at a natural pause point.

### What This Hold Means

- No active development phases.
- Base code frozen; only regression fixes and documentation corrections permitted.
- Notion control tower and GitHub repo remain accessible as read-only reference.
- Opus 4.6 review gate is not active.

### Reason

All P0→P11 capabilities have been delivered:
- Deterministic control-logic analysis workbench (thrust-reverser reference system)
- Runtime generalization proof via adapter layer (landing-gear second system)
- Fully automated GSD loop with Notion writeback and GitHub Actions CI
- Third-party onboarding guide and template scaffolding
- 23-command regression suite, 0 open gaps

The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.

### Resume Criteria

Milestone Hold lifts when one or more of the following conditions are met:

1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
2. External user feedback identifies a confirmed gap that cannot be resolved within the existing frozen baseline.
3. A project sponsor or lead author formally requests a new development phase via Notion control tower or GitHub.

No development activity resumes without a documented decision in the Notion control plane.

---

## Project Identity

**Name:** AI FANTUI LogicMVP
**Type:** Deterministic control-logic analysis workbench
**First Reference System:** Thrust reverser deploy cockpit
**Generalization Proof:** Landing-gear adapter runtime (second system)

## Core Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` is the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- New system truth is allowed only through explicit adapter interfaces.
- Bypassing adapters with new hardcoded truth paths is forbidden.

## Control Plane

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan → execute → verify routing.
- Opus 4.6 is the only intended manual review gate for subjective judgment.

## Phase Registry

| Phase | Title | Status |
|-------|-------|--------|
| P0 | Control Tower And GSD Control Plane | Done |
| P1 | Automate Execution And Evidence Writeback | Done |
| P2 | Harden Opus 4.6 Review Packets | Done |
| P3 | Reduce Control-Plane Drift | Done |
| P4 | Elevate Cockpit Demo To Presenter-Ready | Done |
| P5 | Demo Polish And Edge-Case Hardening | Done |
| P6 | Reconcile Control Tower And Freeze Demo Packet | Done |
| P7 | Build A Spec-Driven Control Analysis Workbench | Done |
| P8 | Runtime Generalization Proof | Done |
| P9 | Automation Hardening & Evidence Pipeline Maturity | Done |
| P10 | Second-System Runtime Pipeline End-to-End | Done |
| P11 | Product Readiness & Third-Party Onboarding Guide | Done |
| P12 | Third-System Onboarding Validation | Done |
| P13 | Route B — Browser Workbench Multi-System Integration | Done |
| P14 | AI Document Analyzer | Done (2026-04-13) |
| P15 | Pipeline Integration — P14 output → P7/P8 intake | Done (2026-04-14) |
| P16 | AI Canvas Sync（Opus 4.6 架构裁决） | Done (2026-04-15) |
| P17 | Fault Injection — Interactive Fault Mode | Done (2026-04-15, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P18 | Demo Cleanup & Archive Integrity | Done (2026-04-16, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P19 | Hardware Partial Unfreeze — Monte Carlo + Reverse Diagnosis + Pitch Deck | Done (2026-04-17, self-signed v4.0; provenance re-signed 2026-04-20 P32; supersedes `docs/unfreeze/P17-application-draft.md`) |
| P20 | Wow E2E Coverage + Demo Resilience + Dress Rehearsal | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P21 | Local Model PoC — 国产模型本地降级 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P22 | Demo Rehearsal 物料冻结 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P23 | Co-development Kit — 立项通过后首批对接物料 | Done (2026-04-18, GATE-P23-CLOSURE Approved; 对外路线图编号 H2-23 ~ H2-27) |
| P24 | 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals | Done (2026-04-18, GATE-P24-CLOSURE Approved) |
| P25 | 立项汇报段落级时序彩排 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P26 | 立项物料引用有效性自动验证 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P27 | Backend Switch Drill — pkill+spawn+wait_ready | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P28 | FAQ Evidence Cross-Check | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P29 | Pre-Pitch Readiness Scorecard | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P30 | Scorecard 语义与 findings §5.1 决策对齐 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P31 | Explain-runtime visibility + prewarm guardrails (orphan-triage re-land) | Done (2026-04-20, v5.2 solo-signed; awaiting `P31-GATE: Approved` for FF merge to main) |
| P32 | Provenance Backfill — v4.0 追认 + Milestone 9 Lifted + constitution v2.1 | In progress (2026-04-20, v5.2 solo-signed; `GATE-P32-PLAN: Approved` 2026-04-20, awaiting `GATE-P32-CLOSURE: Approved`) |

---

## Milestone 9 — Project Freeze → Lifted

**Declared:** 2026-04-15 by Opus 4.6 Final Adjudication
**Lifted:** 2026-04-20 (retroactive provenance追认 under v5.2 Claude App Solo Mode, P32 W3)
**Scope:** Post-P16 freeze line covering all P17–P30 activity

### What Milestone 9 Meant

Opus 4.6 declared Project Freeze after P16 AI Canvas Sync (2026-04-15) with the assessment "项目已达到可泛化动力控制电路系统工作台 MVP 达标线". Freeze conditions required that continued development await one of three Resume Criteria: 外部用户反馈 / 产品方向决策 / 赞助方请求. `docs/freeze/FREEZE-RULING-2026-04-15.md` is the primary rulemaking document; `MILESTONE4/5/6-HOLD.md` are the earlier freeze-family records.

### Why It Was Lifted (retroactively 追认)

Between 2026-04-15 and 2026-04-18, under the v4.0 Extended Autonomy Mode then-in-force, **14 Phases (P17 → P30) landed above the freeze line**, each individually self-signed by the Executor (Codex / MiniMax-2.7 / Claude Code Opus 4.7) and accepted by Kogami through point-Gate decisions (`GATE-P23-CLOSURE: Approved`, `GATE-P24-CLOSURE: Approved`, etc.). These Gate approvals collectively satisfied Resume Criterion #1 「产品方向决策」 — Kogami's on-the-record directives to continue with 立项 demo hardening, co-development kit, then pitch script rehearsal constitute the required 产品方向 evidence.

**However**, the 14-Phase window **never carried an explicit Milestone 9 Lifted statement in this constitution**. That gap is what P32 W3 closes: not by retroactively re-consenting to work that already happened, but by正式 acknowledging that the freeze line was in fact crossed and the Resume Criterion path was met.

### Signatures

- **Kogami (Project Sponsor):** implicit Lifted consent via the 14 per-Phase Gate approvals (2026-04-15 → 2026-04-18); **explicit 追认 via `GATE-P32-PLAN: Approved` (2026-04-20)**
- **Claude App Opus 4.7 (Solo Executor, v5.2):** solo-signed 2026-04-20 via `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`

### What This Does NOT Mean

- Milestone 9 Lifted does **not** authorize new能力 Phases prospectively. Any new Phase (P33+) must still go through its own PLAN / CLOSURE Gate sequence under v5.2 Solo Mode.
- It does **not** imply `docs/freeze/FREEZE-RULING-2026-04-15.md` is void. That ruling stands as the 2026-04-15 factual assessment; Lifted simply记录 that the Resume Criteria were thereafter met.
- It does **not** alter any P17–P30 Phase content, tests, or code. P32 is证迹 (provenance) only.

---

## Governance Mode Timeline

- **v3.0 双 Opus (2026-04-xx → 2026-04-17):** Claude Code Opus 4.7 as Executor; Notion AI Opus 4.7 as independent Gate reviewer. Retired when v4.0 Extended Autonomy allowed Executor self-signing.
- **v4.0 Extended Autonomy (2026-04-17 → 2026-04-19):** Executor allowed to self-sign Gate within a ≥3-Phase深度验收 window when Kogami 显式 renewed the mandate. Used for P17 → P30 close-out.
- **v5.1 Pair Mode (2026-04-19 → 2026-04-20):** Short-lived dual-Executor pair (Claude App + Codex). Abandoned after orphan commit `4474505` (Codex, unsigned) triggered the P31 orphan-triage response.
- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
- **v6.0 Multi-Agent × Codex Joint Dev (2026-04-22 → 2026-04-25):** Claude Code 主执行 + Codex 强制盲点审查回到清单（多文件前端 / API 契约变更 / e2e 期望变更 / UI 变更 / 用户 UX 批评后首次实现 / OpenFOAM 误差等触发硬性调用）。Verbatim exception 5 条件允许跳过 round-2。详见 Notion Page 11 v6.0 节。
- **v6.1 Solo Autonomy Delegation (2026-04-25, active):** Kogami 在 PR #5 Gate 后口头授权 Claude Code 全权（Notion + PR merge + Codex 自决 + 新 phase 启停），仅 truth-engine 红线维持。详见 v6.1 Solo Autonomy 节、DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT、Notion Page 11 §v6.1。
- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
- **v2.4 Recursive Coherence Drift Mitigation (2026-04-25, active, ratified by Opus 4.7):** doc-only rule-bundle PR R3 Opus consultation trigger + R5 drift-acceptance declaration + R6 hard cap + forbidden-superlative list + standard substitute template. Source: RETRO-V61-055 §3 + Opus 4.7 strategic review same day. Confirmed instances: PR #11 (5R), PR #14 (6R, merged with drift acceptance). v6.1 Hard Stop ≥4 仍适用于 source-code 与非 rule-bundle PR。详见 v2.3 §Recursive Coherence Drift Mitigation、RETRO-V61-055。

## v5.2 Claude App Solo Mode (active)

### Red Lines (five absolutes)

1. **No controller.py / 19-node / R1–R5 / irreversible main-HEAD mutation without Kogami Gate sign.** FF merges, branch deletes, force-pushes, and any action that rewrites main's history must wait for an explicit `<PHASE>-GATE: Approved` comment from Kogami.
2. **No self-signed Gate.** Executor drafts `PLAN.md` and `CLOSURE.md` but never signs `GATE-<PHASE>-PLAN: Approved` or `GATE-<PHASE>-CLOSURE: Approved`. Those two signatures are Kogami-only.
3. **Tier 1 adversarial self-review is mandatory on every PLAN.** Plans must contain a Counterargument section with ≥3 reasoned self-objections and explicit rebuttals before request-for-Gate.
4. **Executor does not self-select next Phase direction.** When a Phase closes, Executor awaits Kogami's next directive. If Executor has a recommendation, it must be offered as an `AskUserQuestion` with ≥2 options, not acted on unilaterally.
5. **证迹 (provenance) precedes 能力 (capability).** New capability work is gated on no outstanding provenance debt. If gap analysis identifies provenance debt, that debt is closed in a dedicated证迹 Phase before any能力 Phase starts (this is precisely what P32 enforces for the v4.0 window).

### DECISION Format

Every Phase closure writes a DECISION section to the Notion control tower (`33cc68942bed8136b5c9f9ba5b4b44ec`) with heading:

```markdown
## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)
```

Body covers: direction source · scope · Kogami Gate references · Exit artefact links · Red-line compliance checklist.

### Commit Trailer

Every commit by Claude App Opus 4.7 under v5.2 must include the trailer:

```
Execution-by: opus47-claudeapp-solo · v5.2
```

Reviewer sign line (in Notion / closure docs / audit records):

```
Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD
```

### Sandbox Discipline

- Workspace mount `.git/*.lock` residues are known blockers. v5.2 convention: scratch clone at `/sessions/<id>/p31-work/repo` + git bundle transfer when locks persist. Bundles live under `.planning/audit/bundles/` with adjacent README import instructions.
- Workspace mount file edits only permitted on paths that do NOT coincide with files changed by a pending bundle, to avoid FF merge conflicts.

---

## v6.1 Claude Code Solo Autonomy Delegation (2026-04-25, active)

### Origin

Kogami 2026-04-25 verbatim grant, after PR #5 GATE-WOW-A-NARRATION-FIX: Approved:

> 全权授权你进行开发，根据你的建议继续执行，只有truth-engine不许动，其他权限都交给你，你可以按照分工，调用codex配合你。记得在Notion页面里更新我这次的授权，以及Claude code的权限说明

Recorded as `DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT` (Notion 04 决策日志 DB) and reflected in Notion Page 11 §v6.1 Solo Autonomy Delegation. v5.2 五红线和 v6.0 联合开发 Codex 触发清单作为基线继承；v6.1 仅在其上叠加授权层。

### Allowed (without per-step Kogami sign-off)

- Git: push / rebase / force-push 仅在 Claude 自己创建的 dev 分支；main 与 reviewer 已 ack 的 PR head 仍走 PR 流程
- `gh pr merge`：合并任何 OPEN PR 到 main，前提 (1) 未触红线 (2) 三轨证据齐全 (3) Codex 已审查（如触发 v6.0 / v6.1 trigger 清单）
- Notion 写入：04 决策日志、03 会话记录、Page 11 模型分工、Roadmap、其他子页
- Codex 调用自决：`/codex-gpt54` 何时调由 Claude 判断；硬触发清单与 v6.0 一致
- 自启 Phase：写 PLAN.md / 执行 / 写 CLOSURE.md / 自签 GATE-Pxx-CLOSURE: Approved；Tier 1 adversarial self-review (≥3 反对意见 + rebuttal) 仍硬性必跑
- 测试 / 调试 / `demo_server` 启停 / git bisect

### Forbidden（红线维持，触碰即停车）

- `src/well_harness/controller.py` 任何编辑（pure truth engine）
- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义
- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）
- `runs/dress_rehearsal_*/wow_*_timeline.json` fixture 数据
- Force-push 到 main / 已 merge 分支；squash 重写 main 历史；`--no-verify` / `--no-gpg-sign`
- 假装跑了测试（数字必须来自真实 stdout 粘贴）
- 自创规则版本号（v6.1 之后下次叠加层应是 v6.2，不得跳号）

### Codex 触发清单（继承 v6.0 + V61-001 新增 + v6.1 EMPIRICAL-CLAIM-PROBE）

继承 v6.0 硬性触发：多文件前端、API 契约、e2e 期望变更、UI 交互模式、用户 UX 批评首次实现、OpenFOAM solver 报错、Phase E2E ≥3 case 连续失败、Docker+OpenFOAM 联合调试、`foam_agent_adapter.py` >5 LOC、`_generate_*.py` CFD 几何新增、GSD 产出物。

继承 RETRO-V61-001 新增：安全敏感 operator endpoint、byte-reproducibility 敏感路径、跨 ≥3 文件 API schema rename。

**v6.1 新增 EMPIRICAL-CLAIM-PROBE 规则（2026-04-25）：** PR prose（test docstring / 文件级 comment / demo doc / PR description）写下任何关于服务端 runtime 行为的具体数字（plant deploy %、sim time、tick count、logic-X activation timing 等）之前，Claude Code 必须 boot 相关代码路径在本地实测一次，或显式标 `TODO(probe-before-merge)`，或引用数字定义所在的 commit:line。仅基于 mental-model 算术得出的数字禁止落地到 regression-locked 测试或客户向 demo doc。来源：PR #5 round 1 Codex 命中 BEAT_EARLY ~6% deploy 实际 0% （详 `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`）。

## v2.3 · UI-COPY-PROBE

### 触发条件
任何写入 repo 的 user-facing 自然语言文本，包括但不限于：
- 入口页 / landing 页的 tile title / tile description / hero copy
- button label / link text / empty state / tooltip / modal body
- toast / banner / inline notice
- onboarding 步骤说明 / 错误提示文案

豁免：
- 纯 a11y 标签（aria-label）若与可见 label 1:1 同步
- 自动从 schema / enum / config 渲染的字符串（值由代码生成，文案即数据）

### 强制 stage（写完之后、commit 之前必走）
对本期新增/修改的每一条 user-facing copy，作者必须执行 **claim-to-source sweep**：

1. **拆 claim**：把 copy 拆成可验证的具体声明单元（surface 名、行为、字段、角色、限制、数据来源、文件格式、SHA 类型……）。叙述性形容词（"流畅"、"清晰"）不计 claim。
2. **grep 回 src/**：每一条 claim 必须在 src/ tests/ schemas/ config/ 至少一个文件中找到 line-number 锚点；锚点要支持该 claim 当前已 ship，不是计划态。
3. **三选一处置**：
   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
   - **[DELETE]** 找不到锚点且无规划 → 删除该 claim。

#### Anchor 格式细则

每一条 anchor 必须是 **可执行的 ripgrep / sed 命令的目标**。按 claim 极性，正合法形式只有两种之一：


exec
/bin/zsh -lc "git diff --stat main..83d69e4 && printf '\\n---BACKEND-DIFF---\\n' && git diff --name-only main..83d69e4 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-15e-SURFACE-INVENTORY.md                   | 141 ++++++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 .../persona-P2-E11-15d-R3-output.md                |  96 +++++++
 .../persona-P2-E11-15d-R3-prompt.txt               |  69 +++++
 src/well_harness/static/workbench.html             |  54 ++--
 src/well_harness/static/workbench.js               |   2 +-
 .../test_workbench_e11_15e_chinese_first_bundle.py | 311 +++++++++++++++++++++
 7 files changed, 646 insertions(+), 28 deletions(-)

---BACKEND-DIFF---

exec
/bin/zsh -lc 'git rev-parse --short HEAD && git rev-parse --verify 83d69e4 && git rev-parse --verify main' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
83d69e4
83d69e4947451085f0a45966ee652fd00377e29d
a4f17bcd944f0e56def7701422e5b8f27e2da9e0

codex
The backend diff check is clean so far: `main..83d69e4` only touches static workbench surfaces, the new tests, and planning artifacts. Next I’m enumerating the actual 23 bilingual strings from the diff and comparing them against the Section 7 guard list and every JS write path that can mutate those DOM nodes after hydration.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3740,3845p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '1,420p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3740	    document.body.dataset.view = mode;
  3741	    workbenchElement("view-btn-beginner").classList.toggle("is-active", mode === "beginner");
  3742	    workbenchElement("view-btn-expert").classList.toggle("is-active", mode === "expert");
  3743	    workbenchElement("view-mode-hint").textContent = mode === "beginner"
  3744	      ? "— 专家工具默认折叠，适合先看结论"
  3745	      : "— 显示所有工具：JSON 编辑器 / schema repair / clarification";
  3746	  }
  3747	
  3748	  const beginnerBtn = workbenchElement("view-btn-beginner");
  3749	  const expertBtn = workbenchElement("view-btn-expert");
  3750	  if (!beginnerBtn || !expertBtn) {
  3751	    return;
  3752	  }
  3753	
  3754	  beginnerBtn.addEventListener("click", () => {
  3755	    setViewMode("beginner");
  3756	  });
  3757	  expertBtn.addEventListener("click", () => {
  3758	    setViewMode("expert");
  3759	  });
  3760	
  3761	  setViewMode("beginner");
  3762	}
  3763	
  3764	// E11-13 (2026-04-25): manual_feedback_override trust-affordance.
  3765	// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
  3766	// it onto #workbench-trust-banner so the banner shows only when mode =
  3767	// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
  3768	// (e.g., when the snapshot endpoint reports a different mode in future
  3769	// E11-14+). Banner dismissal is session-local (sessionStorage); chip + actual
  3770	// mode value remain visible across dismissals.
  3771	function syncTrustBannerForMode(mode) {
  3772	  const banner = document.getElementById("workbench-trust-banner");
  3773	  if (banner) {
  3774	    banner.setAttribute("data-feedback-mode", mode);
  3775	  }
  3776	}
  3777	
  3778	function setFeedbackMode(mode) {
  3779	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  3780	  if (!allowed.has(mode)) {
  3781	    return false;
  3782	  }
  3783	  const chip = document.getElementById("workbench-feedback-mode");
  3784	  if (chip) {
  3785	    chip.setAttribute("data-feedback-mode", mode);
  3786	    const label = chip.querySelector("strong");
  3787	    if (label) {
  3788	      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
  3789	    }
  3790	  }
  3791	  syncTrustBannerForMode(mode);
  3792	  return true;
  3793	}
  3794	
  3795	function installFeedbackModeAffordance() {
  3796	  const chip = document.getElementById("workbench-feedback-mode");
  3797	  const banner = document.getElementById("workbench-trust-banner");
  3798	  if (!chip || !banner) {
  3799	    return;
  3800	  }
  3801	  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
  3802	  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
  3803	    banner.setAttribute("data-trust-banner-dismissed", "true");
  3804	  }
  3805	  const dismiss = banner.querySelector("[data-trust-banner-dismiss]");
  3806	  if (dismiss) {
  3807	    dismiss.addEventListener("click", () => {
  3808	      banner.setAttribute("data-trust-banner-dismissed", "true");
  3809	      if (window.sessionStorage) {
  3810	        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
  3811	      }
  3812	    });
  3813	  }
  3814	}
  3815	
  3816	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
  3817	// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
  3818	// the monte-carlo / reverse-diagnose API contracts from the matching e2e
  3819	// suites. One click → POST (with bounded timeout) → single-line summary in
  3820	// the card's result area.
  3821	//
  3822	// The exact card payloads are FROZEN — tests/test_workbench_wow_starters.py
  3823	// asserts byte-equality against this object; do not silently re-tune
  3824	// n_trials, max_results, n1k, or BEAT_DEEP_PAYLOAD shape without updating
  3825	// the regression lock and the surface-inventory drift acceptance.
  3826	const WOW_REQUEST_TIMEOUT_MS = 10000;
  3827	
  3828	const WOW_SCENARIOS = {
  3829	  wow_a: {
  3830	    endpoint: "/api/lever-snapshot",
  3831	    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
  3832	    payload: {
  3833	      tra_deg: -35,
  3834	      radio_altitude_ft: 2,
  3835	      engine_running: true,
  3836	      aircraft_on_ground: true,
  3837	      reverser_inhibited: false,
  3838	      eec_enable: true,
  3839	      n1k: 0.92,
  3840	      feedback_mode: "auto_scrubber",
  3841	      deploy_position_percent: 95,
  3842	    },
  3843	    // P1+P2+P5 R2 fix: read actual logic-gate states from the response
  3844	    // instead of overstating "L1–L4 latched". Under auto_scrubber pullback
  3845	    // the e2e contract says BEAT_DEEP latches at minimum {logic2, logic3,

 succeeded in 0ms:
     1	"""E11-15e — Tier-A Chinese-first bundle regression lock.
     2	
     3	Bilingualizes 17 user-visible English-only surfaces enumerated by P2
     4	during the E11-15d review (see test_workbench_approval_flow_polish.py
     5	docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
     6	E11-15d-SURFACE-INVENTORY.md):
     7	
     8	  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
     9	  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
    10	  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
    11	                          open issues / advisory flag
    12	  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
    13	  Authority banner (1):   Truth Engine — Read Only headline
    14	  Trust dismiss (1):      Hide for session button
    15	  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
    16	  Reference packet (1):   Annotate column intro <p>
    17	  Inbox empty (1):        No proposals submitted yet.
    18	  Pending sign-off (1):   Pending Kogami sign-off
    19	
    20	Pattern: `<中文> · <English>` everywhere; English suffix is preserved
    21	verbatim so all prior `assert <english> in html` substring locks across
    22	test_workbench_trust_affordance, test_workbench_authority_banner,
    23	test_workbench_role_affordance, test_workbench_column_rename, and
    24	test_workbench_state_of_world_bar continue to pass without contract
    25	churn.
    26	
    27	Out of scope (deferred to a future Tier-A or constitutional decision):
    28	  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    29	    domain proper nouns coupled to value-attribute IDs and to the
    30	    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
    31	  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    32	    locked by tests/test_workbench_column_rename.py:170-172 — those are
    33	    a separate JS-side bilingualization with their own lockstep contract.
    34	  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    35	    </pre> flow diagram — visual phase-arrow, not English copy.
    36	  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    37	    that were already bilingualized in earlier sub-phases.
    38	
    39	Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
    40	"""
    41	
    42	from __future__ import annotations
    43	
    44	import http.client
    45	import threading
    46	from http.server import ThreadingHTTPServer
    47	from pathlib import Path
    48	
    49	import pytest
    50	
    51	from well_harness.demo_server import DemoRequestHandler
    52	
    53	
    54	REPO_ROOT = Path(__file__).resolve().parents[1]
    55	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    56	
    57	
    58	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    59	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    60	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    61	    thread.start()
    62	    return server, thread
    63	
    64	
    65	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    66	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    67	    connection.request("GET", path)
    68	    response = connection.getresponse()
    69	    return response.status, response.read().decode("utf-8")
    70	
    71	
    72	@pytest.fixture
    73	def server():
    74	    s, t = _start_demo_server()
    75	    try:
    76	        yield s
    77	    finally:
    78	        s.shutdown()
    79	        s.server_close()
    80	        t.join(timeout=2)
    81	
    82	
    83	# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────
    84	
    85	
    86	@pytest.mark.parametrize(
    87	    "bilingual",
    88	    [
    89	        # Topbar chip labels (5)
    90	        "<span>身份 · Identity</span>",
    91	        "<span>工单 · Ticket</span>",
    92	        "<span>反馈模式 · Feedback Mode</span>",
    93	        "<span>系统 · System</span>",
    94	        "<strong>手动（仅参考）· Manual (advisory)</strong>",
    95	        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
    96	        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
    97	        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
    98	        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
    99	        # State-of-world labels (4) + advisory flag (1)
   100	        "真值引擎 SHA · truth-engine SHA",
   101	        "最近 e2e · recent e2e",
   102	        "对抗样本 · adversarial",
   103	        "未关闭问题 · open issues",
   104	        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
   105	        # Trust banner body (3)
   106	        '这里"手动反馈"的含义 · What "manual feedback" means here:',
   107	        "该模式仅作参考 · That mode is advisory.",
   108	        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
   109	        # Trust banner dismiss (1)
   110	        "隐藏（本次会话）· Hide for session",
   111	        # Authority banner headline (1)
   112	        "真值引擎 · 只读 · Truth Engine — Read Only",
   113	        # Pre-hydration boot placeholders (3)
   114	        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
   115	        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
   116	        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
   117	        # Reference-packet intro (1)
   118	        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
   119	        # Inbox empty state (1)
   120	        "暂无已提交提案 · No proposals submitted yet.",
   121	        # Pending sign-off (1)
   122	        "等待 Kogami 签字 · Pending Kogami sign-off",
   123	    ],
   124	)
   125	def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
   126	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   127	    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"
   128	
   129	
   130	# ─── 2. Stale English-only surfaces are gone ─────────────────────────
   131	
   132	
   133	@pytest.mark.parametrize(
   134	    "stale",
   135	    [
   136	        # Bare topbar chip labels (no Chinese prefix) — must be replaced
   137	        "<span>Identity</span>",
   138	        "<span>Ticket</span>",
   139	        "<span>Feedback Mode</span>",
   140	        "<span>System</span>",
   141	        "<strong>Manual (advisory)</strong>",
   142	        # WOW h3 stale English-first ordering (E11-15c convention)
   143	        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
   144	        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
   145	        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
   146	        # Bare state-of-world labels (no Chinese prefix)
   147	        ">truth-engine SHA<",
   148	        ">recent e2e<",
   149	        ">adversarial<",
   150	        ">open issues<",
   151	        # Bare trust-banner body lines — these are now sentence-internal
   152	        # so we look for the line-leading position they used to hold.
   153	        "<em>What \"manual feedback\" means here:</em>",
   154	        "<strong>That mode is advisory.</strong>",
   155	        # Bare button + headline + boot placeholders
   156	        ">\n          Hide for session\n        <",
   157	        ">\n          Truth Engine — Read Only\n        <",
   158	        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
   159	        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
   160	        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
   161	        # Bare inbox + pending sign-off
   162	        "<li>No proposals submitted yet.</li>",
   163	        "<strong>Pending Kogami sign-off</strong>",
   164	    ],
   165	)
   166	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   167	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   168	    assert stale not in html, f"stale English-only surface still present: {stale}"
   169	
   170	
   171	# ─── 3. English suffixes preserved (substring locks unchanged) ───────
   172	
   173	
   174	@pytest.mark.parametrize(
   175	    "preserved_english_suffix",
   176	    [
   177	        # Anchors required by trust_affordance.py
   178	        "Manual (advisory)",
   179	        "Truth engine readings",
   180	        "Hide for session",
   181	        'What "manual feedback" means here',
   182	        "That mode is advisory.",
   183	        # Anchor required by authority_banner.py
   184	        "Truth Engine — Read Only",
   185	        # Anchor required by role_affordance.py
   186	        "Pending Kogami sign-off",
   187	        # Anchor required by state_of_world_bar.py
   188	        "advisory · not a live truth-engine reading",
   189	        # Anchors required by column_rename.py:118-120 (pre-hydration)
   190	        "Waiting for probe &amp; trace panel boot.",
   191	        "Waiting for annotate &amp; propose panel boot.",
   192	        "Waiting for hand off &amp; track panel boot.",
   193	    ],
   194	)
   195	def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
   196	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   197	    assert preserved_english_suffix in html, (
   198	        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
   199	    )
   200	
   201	
   202	# ─── 4. Structural anchors preserved ─────────────────────────────────
   203	
   204	
   205	@pytest.mark.parametrize(
   206	    "anchor",
   207	    [
   208	        'id="workbench-feedback-mode"',
   209	        'id="workbench-trust-banner"',
   210	        'id="workbench-authority-banner"',
   211	        'id="workbench-pending-signoff-affordance"',
   212	        'id="workbench-state-of-world-bar"',
   213	        'id="workbench-wow-starters"',
   214	        'data-trust-banner-dismiss',
   215	        'data-feedback-mode="manual_feedback_override"',
   216	    ],
   217	)
   218	def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
   219	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   220	    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"
   221	
   222	
   223	# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
   224	
   225	
   226	def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
   227	    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
   228	    switch. If the JS literal stays English-only, the very first mode
   229	    flip would silently revert the static HTML's bilingual chip back to
   230	    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
   231	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   232	    assert '"真值引擎 · Truth Engine"' in js, (
   233	        "JS feedback-mode `truth_engine` branch must use bilingual label"
   234	    )
   235	    assert '"手动（仅参考）· Manual (advisory)"' in js, (
   236	        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
   237	    )
   238	    # Stale English-only literals must not coexist (would imply duplicate
   239	    # write-paths or stale residue).
   240	    assert '"Truth Engine"' not in js, (
   241	        'stale English-only `"Truth Engine"` literal still in workbench.js'
   242	    )
   243	    assert '"Manual (advisory)"' not in js, (
   244	        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
   245	    )
   246	
   247	
   248	# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────
   249	
   250	
   251	def test_workbench_route_serves_e11_15e_bundle(server) -> None:
   252	    status, html = _get(server, "/workbench")
   253	    assert status == 200
   254	    # Spot-check one string from each surface category.
   255	    assert "身份 · Identity" in html
   256	    assert "因果链走读 · Causal Chain" in html
   257	    assert "真值引擎 SHA · truth-engine SHA" in html
   258	    assert "该模式仅作参考 · That mode is advisory." in html
   259	    assert "隐藏（本次会话）· Hide for session" in html
   260	    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html
   261	    assert "等待 probe &amp; trace 面板启动" in html
   262	    assert "暂无已提交提案 · No proposals submitted yet." in html
   263	    assert "等待 Kogami 签字 · Pending Kogami sign-off" in html
   264	
   265	
   266	# ─── 7. Truth-engine red line — backend untouched ────────────────────
   267	
   268	
   269	def test_e11_15e_does_not_touch_truth_engine_backend() -> None:
   270	    """E11-15e only edits static HTML/JS display copy. It must NOT leak
   271	    into controller.py / runner.py / models.py / adapters / demo_server
   272	    (truth-engine red line — see .planning/constitution.md)."""
   273	    repo_root = Path(__file__).resolve().parents[1]
   274	    backend_paths = [
   275	        repo_root / "src" / "well_harness" / "controller.py",
   276	        repo_root / "src" / "well_harness" / "runner.py",
   277	        repo_root / "src" / "well_harness" / "models.py",
   278	        repo_root / "src" / "well_harness" / "demo_server.py",
   279	    ]
   280	    e11_15e_chinese = [
   281	        "身份 · Identity",
   282	        "工单 · Ticket",
   283	        "反馈模式 · Feedback Mode",
   284	        "系统 · System",
   285	        "手动（仅参考）",
   286	        "因果链走读",
   287	        "1000-trial 可靠性",
   288	        "反向诊断 · Reverse Diagnose",
   289	        "真值引擎 SHA",
   290	        "最近 e2e",
   291	        "对抗样本",
   292	        "未关闭问题",
   293	        "仅参考 · 非真值引擎实时读数",
   294	        '这里"手动反馈"的含义',
   295	        "该模式仅作参考",
   296	        "隐藏（本次会话）",
   297	        "真值引擎 · 只读",
   298	        "等待 probe",
   299	        "等待 annotate",
   300	        "等待 hand off",
   301	        "参考资料、澄清说明",
   302	        "暂无已提交提案",
   303	        "等待 Kogami 签字",
   304	    ]
   305	    for backend in backend_paths:
   306	        text = backend.read_text(encoding="utf-8")
   307	        for phrase in e11_15e_chinese:
   308	            assert phrase not in text, (
   309	                f"E11-15e display copy {phrase!r} unexpectedly leaked into "
   310	                f"backend file {backend.name} — truth-engine red-line breach"
   311	            )

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
    17	          <p class="eyebrow">工程师工作区</p>
    18	          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
    19	        </div>
    20	        <div
    21	          id="workbench-identity"
    22	          class="workbench-collab-chip"
    23	          data-role="ENGINEER"
    24	          data-identity-name="Kogami"
    25	        >
    26	          <span>身份 · Identity</span>
    27	          <strong>Kogami / Engineer</strong>
    28	        </div>
    29	        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
    30	          <span>工单 · Ticket</span>
    31	          <strong>WB-E06-SHELL</strong>
    32	        </div>
    33	        <div
    34	          id="workbench-feedback-mode"
    35	          class="workbench-collab-chip workbench-feedback-mode-chip"
    36	          data-feedback-mode="manual_feedback_override"
    37	          data-mode-authority="advisory"
    38	          aria-live="polite"
    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
    40	        >
    41	          <span>反馈模式 · Feedback Mode</span>
    42	          <strong>手动（仅参考）· Manual (advisory)</strong>
    43	          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
    44	        </div>
    45	        <label class="workbench-collab-system" for="workbench-system-select">
    46	          <span>系统 · System</span>
    47	          <select id="workbench-system-select">
    48	            <option value="thrust-reverser">Thrust Reverser</option>
    49	            <option value="landing-gear">Landing Gear</option>
    50	            <option value="bleed-air-valve">Bleed Air Valve</option>
    51	            <option value="c919-etras">C919 E-TRAS</option>
    52	          </select>
    53	        </label>
    54	      </section>
    55	
    56	      <section
    57	        id="workbench-state-of-world-bar"
    58	        class="workbench-state-of-world-bar"
    59	        aria-label="State-of-the-world status bar (advisory)"
    60	        data-status-kind="advisory"
    61	      >
    62	        <span class="workbench-sow-eyebrow">当前现状</span>
    63	        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
    64	              title="git rev-parse --short HEAD">
    65	          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
    66	          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
    67	        </span>
    68	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    69	        <span class="workbench-sow-field" data-sow-field="recent_e2e"
    70	              title="docs/coordination/qa_report.md (most recent test run)">
    71	          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
    72	          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
    73	        </span>
    74	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    75	        <span class="workbench-sow-field" data-sow-field="adversarial"
    76	              title="docs/coordination/qa_report.md (shared validation)">
    77	          <span class="workbench-sow-label">对抗样本 · adversarial</span>
    78	          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
    79	        </span>
    80	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    81	        <span class="workbench-sow-field" data-sow-field="known_issues"
    82	              title="docs/known-issues/ file count">
    83	          <span class="workbench-sow-label">未关闭问题 · open issues</span>
    84	          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
    85	        </span>
    86	        <span class="workbench-sow-flag" aria-hidden="false">
    87	          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
    88	        </span>
    89	      </section>
    90	
    91	      <section
    92	        id="workbench-wow-starters"
    93	        class="workbench-wow-starters"
    94	        aria-label="Canonical demo scenarios — one-click starter cards"
    95	      >
    96	        <header class="workbench-wow-starters-header">
    97	          <p class="eyebrow">主流场景</p>
    98	          <h2>起手卡 · One-click 走读</h2>
    99	          <p class="workbench-wow-starters-sub">
   100	            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
   101	          </p>
   102	        </header>
   103	        <div class="workbench-wow-starters-grid">
   104	          <article
   105	            class="workbench-wow-card"
   106	            data-wow-id="wow_a"
   107	            aria-labelledby="workbench-wow-a-title"
   108	          >
   109	            <header>
   110	              <span class="workbench-wow-tag">wow_a</span>
   111	              <h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>
   112	            </header>
   113	            <p class="workbench-wow-card-desc">
   114	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
   115	              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
   116	              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
   117	              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
   118	            </p>
   119	            <button
   120	              type="button"
   121	              class="workbench-wow-run-button"
   122	              data-wow-action="run"
   123	              data-wow-id="wow_a"
   124	            >
   125	              一键运行 wow_a
   126	            </button>
   127	            <div
   128	              class="workbench-wow-result"
   129	              data-wow-result-for="wow_a"
   130	              role="status"
   131	              aria-live="polite"
   132	            >
   133	              尚未运行。
   134	            </div>
   135	          </article>
   136	          <article
   137	            class="workbench-wow-card"
   138	            data-wow-id="wow_b"
   139	            aria-labelledby="workbench-wow-b-title"
   140	          >
   141	            <header>
   142	              <span class="workbench-wow-tag">wow_b</span>
   143	              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
   144	            </header>
   145	            <p class="workbench-wow-card-desc">
   146	              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
   147	              success_rate + failure_modes 分布。
   148	            </p>
   149	            <button
   150	              type="button"
   151	              class="workbench-wow-run-button"
   152	              data-wow-action="run"
   153	              data-wow-id="wow_b"
   154	            >
   155	              一键运行 wow_b
   156	            </button>
   157	            <div
   158	              class="workbench-wow-result"
   159	              data-wow-result-for="wow_b"
   160	              role="status"
   161	              aria-live="polite"
   162	            >
   163	              尚未运行。
   164	            </div>
   165	          </article>
   166	          <article
   167	            class="workbench-wow-card"
   168	            data-wow-id="wow_c"
   169	            aria-labelledby="workbench-wow-c-title"
   170	          >
   171	            <header>
   172	              <span class="workbench-wow-tag">wow_c</span>
   173	              <h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>
   174	            </header>
   175	            <p class="workbench-wow-card-desc">
   176	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   177	              触发该 outcome 的参数组合（max_results=10）。
   178	            </p>
   179	            <button
   180	              type="button"
   181	              class="workbench-wow-run-button"
   182	              data-wow-action="run"
   183	              data-wow-id="wow_c"
   184	            >
   185	              一键运行 wow_c
   186	            </button>
   187	            <div
   188	              class="workbench-wow-result"
   189	              data-wow-result-for="wow_c"
   190	              role="status"
   191	              aria-live="polite"
   192	            >
   193	              尚未运行。
   194	            </div>
   195	          </article>
   196	        </div>
   197	      </section>
   198	
   199	      <aside
   200	        id="workbench-trust-banner"
   201	        class="workbench-trust-banner"
   202	        data-feedback-mode="manual_feedback_override"
   203	        role="note"
   204	        aria-label="Feedback mode trust affordance"
   205	      >
   206	        <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
   207	        <div class="workbench-trust-banner-body">
   208	          <span class="workbench-trust-banner-scope">
   209	            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
   210	            (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
   211	            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
   212	          </span>
   213	          <strong>该模式仅作参考 · That mode is advisory.</strong>
   214	          <span>
   215	            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   216	            你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   217	          </span>
   218	        </div>
   219	        <button
   220	          type="button"

exec
/bin/zsh -lc 'git diff main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index cbc80a4..157518a 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -23,11 +23,11 @@
           data-role="ENGINEER"
           data-identity-name="Kogami"
         >
-          <span>Identity</span>
+          <span>身份 · Identity</span>
           <strong>Kogami / Engineer</strong>
         </div>
         <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
-          <span>Ticket</span>
+          <span>工单 · Ticket</span>
           <strong>WB-E06-SHELL</strong>
         </div>
         <div
@@ -38,12 +38,12 @@
           aria-live="polite"
           title="Manual feedback override is advisory — truth engine readings remain authoritative."
         >
-          <span>Feedback Mode</span>
-          <strong>Manual (advisory)</strong>
+          <span>反馈模式 · Feedback Mode</span>
+          <strong>手动（仅参考）· Manual (advisory)</strong>
           <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
         </div>
         <label class="workbench-collab-system" for="workbench-system-select">
-          <span>System</span>
+          <span>系统 · System</span>
           <select id="workbench-system-select">
             <option value="thrust-reverser">Thrust Reverser</option>
             <option value="landing-gear">Landing Gear</option>
@@ -62,29 +62,29 @@
         <span class="workbench-sow-eyebrow">当前现状</span>
         <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
               title="git rev-parse --short HEAD">
-          <span class="workbench-sow-label">truth-engine SHA</span>
+          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
           <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="recent_e2e"
               title="docs/coordination/qa_report.md (most recent test run)">
-          <span class="workbench-sow-label">recent e2e</span>
+          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
           <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="adversarial"
               title="docs/coordination/qa_report.md (shared validation)">
-          <span class="workbench-sow-label">adversarial</span>
+          <span class="workbench-sow-label">对抗样本 · adversarial</span>
           <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="known_issues"
               title="docs/known-issues/ file count">
-          <span class="workbench-sow-label">open issues</span>
+          <span class="workbench-sow-label">未关闭问题 · open issues</span>
           <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
         </span>
         <span class="workbench-sow-flag" aria-hidden="false">
-          advisory · not a live truth-engine reading
+          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
         </span>
       </section>
 
@@ -108,7 +108,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_a</span>
-              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
+              <h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
@@ -140,7 +140,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_b</span>
-              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
+              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
@@ -170,7 +170,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_c</span>
-              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
+              <h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
@@ -206,14 +206,14 @@
         <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
         <div class="workbench-trust-banner-body">
           <span class="workbench-trust-banner-scope">
-            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
-            an observed reading — for example, editing a snapshot input field before running a scenario.
-            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
+            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
+            (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
+            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
           </span>
-          <strong>That mode is advisory.</strong>
+          <strong>该模式仅作参考 · That mode is advisory.</strong>
           <span>
-            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
-            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
+            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
+            你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
           </span>
         </div>
         <button
@@ -222,7 +222,7 @@
           aria-label="Hide trust banner for this session"
           data-trust-banner-dismiss
         >
-          Hide for session
+          隐藏（本次会话）· Hide for session
         </button>
       </aside>
 
@@ -245,7 +245,7 @@
       >
         <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
         <span class="workbench-authority-banner-headline">
-          Truth Engine — Read Only
+          真值引擎 · 只读 · Truth Engine — Read Only
         </span>
         <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
         <span class="workbench-authority-banner-rule">
@@ -275,7 +275,7 @@
             <h2>探针与追踪 · Probe &amp; Trace</h2>
           </header>
           <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for probe &amp; trace panel boot.
+            等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
           </div>
           <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
             <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
@@ -295,10 +295,10 @@
             <h2>标注与提案 · Annotate &amp; Propose</h2>
           </header>
           <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for annotate &amp; propose panel boot.
+            等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
           </div>
           <div class="workbench-collab-document">
-            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
+            <p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.</p>
             <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
           </div>
         </article>
@@ -315,7 +315,7 @@
             <h2>移交与跟踪 · Hand off &amp; Track</h2>
           </header>
           <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for hand off &amp; track panel boot.
+            等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
           </div>
           <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
             <span>SW1</span>
@@ -334,7 +334,7 @@
           <h2>审核队列 · Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
-          <li>No proposals submitted yet.</li>
+          <li>暂无已提交提案 · No proposals submitted yet.</li>
         </ul>
       </aside>
 
@@ -360,7 +360,7 @@
       >
         <span class="workbench-pending-signoff-icon" aria-hidden="true">🛈</span>
         <div class="workbench-pending-signoff-body">
-          <strong>Pending Kogami sign-off</strong>
+          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
           <span>
             你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属
             authority — 你的角色当前不会看到 disabled UI，而是这条 explicit
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index 375e6c9..33a247a 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -3785,7 +3785,7 @@ function setFeedbackMode(mode) {
     chip.setAttribute("data-feedback-mode", mode);
     const label = chip.querySelector("strong");
     if (label) {
-      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
+      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
     }
   }
   syncTrustBannerForMode(mode);
diff --git a/tests/test_workbench_e11_15e_chinese_first_bundle.py b/tests/test_workbench_e11_15e_chinese_first_bundle.py
new file mode 100644
index 0000000..46ef2ee
--- /dev/null
+++ b/tests/test_workbench_e11_15e_chinese_first_bundle.py
@@ -0,0 +1,311 @@
+"""E11-15e — Tier-A Chinese-first bundle regression lock.
+
+Bilingualizes 17 user-visible English-only surfaces enumerated by P2
+during the E11-15d review (see test_workbench_approval_flow_polish.py
+docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
+E11-15d-SURFACE-INVENTORY.md):
+
+  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
+  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
+  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
+                          open issues / advisory flag
+  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
+  Authority banner (1):   Truth Engine — Read Only headline
+  Trust dismiss (1):      Hide for session button
+  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
+  Reference packet (1):   Annotate column intro <p>
+  Inbox empty (1):        No proposals submitted yet.
+  Pending sign-off (1):   Pending Kogami sign-off
+
+Pattern: `<中文> · <English>` everywhere; English suffix is preserved
+verbatim so all prior `assert <english> in html` substring locks across
+test_workbench_trust_affordance, test_workbench_authority_banner,
+test_workbench_role_affordance, test_workbench_column_rename, and
+test_workbench_state_of_world_bar continue to pass without contract
+churn.
+
+Out of scope (deferred to a future Tier-A or constitutional decision):
+  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
+    domain proper nouns coupled to value-attribute IDs and to the
+    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
+  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
+    locked by tests/test_workbench_column_rename.py:170-172 — those are
+    a separate JS-side bilingualization with their own lockstep contract.
+  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
+    </pre> flow diagram — visual phase-arrow, not English copy.
+  - Workbench-bundle / approval-center / annotation-toolbar surfaces
+    that were already bilingualized in earlier sub-phases.
+
+Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
+"""
+
+from __future__ import annotations
+
+import http.client
+import threading
+from http.server import ThreadingHTTPServer
+from pathlib import Path
+
+import pytest
+
+from well_harness.demo_server import DemoRequestHandler
+
+
+REPO_ROOT = Path(__file__).resolve().parents[1]
+STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
+
+
+def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
+    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
+    thread = threading.Thread(target=server.serve_forever, daemon=True)
+    thread.start()
+    return server, thread
+
+
+def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
+    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
+    connection.request("GET", path)
+    response = connection.getresponse()
+    return response.status, response.read().decode("utf-8")
+
+
+@pytest.fixture
+def server():
+    s, t = _start_demo_server()
+    try:
+        yield s
+    finally:
+        s.shutdown()
+        s.server_close()
+        t.join(timeout=2)
+
+
+# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────
+
+
+@pytest.mark.parametrize(
+    "bilingual",
+    [
+        # Topbar chip labels (5)
+        "<span>身份 · Identity</span>",
+        "<span>工单 · Ticket</span>",
+        "<span>反馈模式 · Feedback Mode</span>",
+        "<span>系统 · System</span>",
+        "<strong>手动（仅参考）· Manual (advisory)</strong>",
+        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
+        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
+        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
+        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
+        # State-of-world labels (4) + advisory flag (1)
+        "真值引擎 SHA · truth-engine SHA",
+        "最近 e2e · recent e2e",
+        "对抗样本 · adversarial",
+        "未关闭问题 · open issues",
+        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
+        # Trust banner body (3)
+        '这里"手动反馈"的含义 · What "manual feedback" means here:',
+        "该模式仅作参考 · That mode is advisory.",
+        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
+        # Trust banner dismiss (1)
+        "隐藏（本次会话）· Hide for session",
+        # Authority banner headline (1)
+        "真值引擎 · 只读 · Truth Engine — Read Only",
+        # Pre-hydration boot placeholders (3)
+        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
+        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
+        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
+        # Reference-packet intro (1)
+        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
+        # Inbox empty state (1)
+        "暂无已提交提案 · No proposals submitted yet.",
+        # Pending sign-off (1)
+        "等待 Kogami 签字 · Pending Kogami sign-off",
+    ],
+)
+def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"
+
+
+# ─── 2. Stale English-only surfaces are gone ─────────────────────────
+
+
+@pytest.mark.parametrize(
+    "stale",
+    [
+        # Bare topbar chip labels (no Chinese prefix) — must be replaced
+        "<span>Identity</span>",
+        "<span>Ticket</span>",
+        "<span>Feedback Mode</span>",
+        "<span>System</span>",
+        "<strong>Manual (advisory)</strong>",
+        # WOW h3 stale English-first ordering (E11-15c convention)
+        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
+        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
+        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
+        # Bare state-of-world labels (no Chinese prefix)
+        ">truth-engine SHA<",
+        ">recent e2e<",
+        ">adversarial<",
+        ">open issues<",
+        # Bare trust-banner body lines — these are now sentence-internal
+        # so we look for the line-leading position they used to hold.
+        "<em>What \"manual feedback\" means here:</em>",
+        "<strong>That mode is advisory.</strong>",
+        # Bare button + headline + boot placeholders
+        ">\n          Hide for session\n        <",
+        ">\n          Truth Engine — Read Only\n        <",
+        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
+        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
+        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
+        # Bare inbox + pending sign-off
+        "<li>No proposals submitted yet.</li>",
+        "<strong>Pending Kogami sign-off</strong>",
+    ],
+)
+def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale not in html, f"stale English-only surface still present: {stale}"
+
+
+# ─── 3. English suffixes preserved (substring locks unchanged) ───────
+
+
+@pytest.mark.parametrize(
+    "preserved_english_suffix",
+    [
+        # Anchors required by trust_affordance.py
+        "Manual (advisory)",
+        "Truth engine readings",
+        "Hide for session",
+        'What "manual feedback" means here',
+        "That mode is advisory.",
+        # Anchor required by authority_banner.py
+        "Truth Engine — Read Only",
+        # Anchor required by role_affordance.py
+        "Pending Kogami sign-off",
+        # Anchor required by state_of_world_bar.py
+        "advisory · not a live truth-engine reading",
+        # Anchors required by column_rename.py:118-120 (pre-hydration)
+        "Waiting for probe &amp; trace panel boot.",
+        "Waiting for annotate &amp; propose panel boot.",
+        "Waiting for hand off &amp; track panel boot.",
+    ],
+)
+def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert preserved_english_suffix in html, (
+        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
+    )
+
+
+# ─── 4. Structural anchors preserved ─────────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "anchor",
+    [
+        'id="workbench-feedback-mode"',
+        'id="workbench-trust-banner"',
+        'id="workbench-authority-banner"',
+        'id="workbench-pending-signoff-affordance"',
+        'id="workbench-state-of-world-bar"',
+        'id="workbench-wow-starters"',
+        'data-trust-banner-dismiss',
+        'data-feedback-mode="manual_feedback_override"',
+    ],
+)
+def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"
+
+
+# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
+
+
+def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
+    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
+    switch. If the JS literal stays English-only, the very first mode
+    flip would silently revert the static HTML's bilingual chip back to
+    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    assert '"真值引擎 · Truth Engine"' in js, (
+        "JS feedback-mode `truth_engine` branch must use bilingual label"
+    )
+    assert '"手动（仅参考）· Manual (advisory)"' in js, (
+        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
+    )
+    # Stale English-only literals must not coexist (would imply duplicate
+    # write-paths or stale residue).
+    assert '"Truth Engine"' not in js, (
+        'stale English-only `"Truth Engine"` literal still in workbench.js'
+    )
+    assert '"Manual (advisory)"' not in js, (
+        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
+    )
+
+
+# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────
+
+
+def test_workbench_route_serves_e11_15e_bundle(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    # Spot-check one string from each surface category.
+    assert "身份 · Identity" in html
+    assert "因果链走读 · Causal Chain" in html
+    assert "真值引擎 SHA · truth-engine SHA" in html
+    assert "该模式仅作参考 · That mode is advisory." in html
+    assert "隐藏（本次会话）· Hide for session" in html
+    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html
+    assert "等待 probe &amp; trace 面板启动" in html
+    assert "暂无已提交提案 · No proposals submitted yet." in html
+    assert "等待 Kogami 签字 · Pending Kogami sign-off" in html
+
+
+# ─── 7. Truth-engine red line — backend untouched ────────────────────
+
+
+def test_e11_15e_does_not_touch_truth_engine_backend() -> None:
+    """E11-15e only edits static HTML/JS display copy. It must NOT leak
+    into controller.py / runner.py / models.py / adapters / demo_server
+    (truth-engine red line — see .planning/constitution.md)."""
+    repo_root = Path(__file__).resolve().parents[1]
+    backend_paths = [
+        repo_root / "src" / "well_harness" / "controller.py",
+        repo_root / "src" / "well_harness" / "runner.py",
+        repo_root / "src" / "well_harness" / "models.py",
+        repo_root / "src" / "well_harness" / "demo_server.py",
+    ]
+    e11_15e_chinese = [
+        "身份 · Identity",
+        "工单 · Ticket",
+        "反馈模式 · Feedback Mode",
+        "系统 · System",
+        "手动（仅参考）",
+        "因果链走读",
+        "1000-trial 可靠性",
+        "反向诊断 · Reverse Diagnose",
+        "真值引擎 SHA",
+        "最近 e2e",
+        "对抗样本",
+        "未关闭问题",
+        "仅参考 · 非真值引擎实时读数",
+        '这里"手动反馈"的含义',
+        "该模式仅作参考",
+        "隐藏（本次会话）",
+        "真值引擎 · 只读",
+        "等待 probe",
+        "等待 annotate",
+        "等待 hand off",
+        "参考资料、澄清说明",
+        "暂无已提交提案",
+        "等待 Kogami 签字",
+    ]
+    for backend in backend_paths:
+        text = backend.read_text(encoding="utf-8")
+        for phrase in e11_15e_chinese:
+            assert phrase not in text, (
+                f"E11-15e display copy {phrase!r} unexpectedly leaked into "
+                f"backend file {backend.name} — truth-engine red-line breach"
+            )

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '220,390p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'rg -n "feedback-mode|feedbackMode|data-feedback-mode|workbench-feedback-mode|workbench-trust-banner-headline|workbench-authority-banner-headline|state-of-world|boot status|control-status|document-status|circuit-status|textContent|innerHTML" src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   220	          type="button"
   221	          class="workbench-trust-banner-dismiss"
   222	          aria-label="Hide trust banner for this session"
   223	          data-trust-banner-dismiss
   224	        >
   225	          隐藏（本次会话）· Hide for session
   226	        </button>
   227	      </aside>
   228	
   229	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   230	        <span class="workbench-annotation-toolbar-label">标注</span>
   231	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
   232	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
   233	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
   234	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
   235	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   236	          标记信号 工具激活
   237	        </span>
   238	      </section>
   239	
   240	      <aside
   241	        id="workbench-authority-banner"
   242	        class="workbench-authority-banner"
   243	        role="note"
   244	        aria-label="Truth-engine authority contract"
   245	      >
   246	        <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
   247	        <span class="workbench-authority-banner-headline">
   248	          真值引擎 · 只读 · Truth Engine — Read Only
   249	        </span>
   250	        <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
   251	        <span class="workbench-authority-banner-rule">
   252	          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
   253	        </span>
   254	        <a
   255	          class="workbench-authority-banner-link"
   256	          href="/v6.1-redline"
   257	          target="_blank"
   258	          rel="noopener"
   259	          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
   260	        >
   261	          v6.1 红线条款 →
   262	        </a>
   263	      </aside>
   264	
   265	      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
   266	        <article
   267	          id="workbench-control-panel"
   268	          class="workbench-collab-column workbench-annotation-surface"
   269	          data-column="control"
   270	          data-annotation-surface="control"
   271	          tabindex="0"
   272	        >
   273	          <header>
   274	            <p class="eyebrow">probe &amp; trace</p>
   275	            <h2>探针与追踪 · Probe &amp; Trace</h2>
   276	          </header>
   277	          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
   278	            等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
   279	          </div>
   280	          <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
   281	            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
   282	            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
   283	          </div>
   284	        </article>
   285	
   286	        <article
   287	          id="workbench-document-panel"
   288	          class="workbench-collab-column workbench-annotation-surface"
   289	          data-column="document"
   290	          data-annotation-surface="document"
   291	          tabindex="0"
   292	        >
   293	          <header>
   294	            <p class="eyebrow">annotate &amp; propose</p>
   295	            <h2>标注与提案 · Annotate &amp; Propose</h2>
   296	          </header>
   297	          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
   298	            等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
   299	          </div>
   300	          <div class="workbench-collab-document">
   301	            <p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.</p>
   302	            <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
   303	          </div>
   304	        </article>
   305	
   306	        <article
   307	          id="workbench-circuit-panel"
   308	          class="workbench-collab-column workbench-annotation-surface"
   309	          data-column="circuit"
   310	          data-annotation-surface="circuit"
   311	          tabindex="0"
   312	        >
   313	          <header>
   314	            <p class="eyebrow">hand off &amp; track</p>
   315	            <h2>移交与跟踪 · Hand off &amp; Track</h2>
   316	          </header>
   317	          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
   318	            等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
   319	          </div>
   320	          <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
   321	            <span>SW1</span>
   322	            <span>Logic 1</span>
   323	            <span>Logic 2</span>
   324	            <span>Logic 3</span>
   325	            <span>Logic 4</span>
   326	            <span>THR LOCK</span>
   327	          </div>
   328	        </article>
   329	      </section>
   330	
   331	      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
   332	        <header>
   333	          <p class="eyebrow">标注收件箱</p>
   334	          <h2>审核队列 · Review Queue</h2>
   335	        </header>
   336	        <ul id="annotation-inbox-list">
   337	          <li>暂无已提交提案 · No proposals submitted yet.</li>
   338	        </ul>
   339	      </aside>
   340	
   341	      <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
   342	        <button
   343	          id="approval-center-entry"
   344	          type="button"
   345	          class="workbench-toolbar-button"
   346	          data-role="KOGAMI"
   347	          aria-controls="approval-center-panel"
   348	        >
   349	          审批中心 · Approval Center
   350	        </button>
   351	        <span>审批操作仅限 Kogami · Approval actions are Kogami-only.</span>
   352	      </footer>
   353	
   354	      <section
   355	        id="workbench-pending-signoff-affordance"
   356	        class="workbench-pending-signoff"
   357	        role="status"
   358	        aria-live="polite"
   359	        data-pending-signoff="hidden"
   360	      >
   361	        <span class="workbench-pending-signoff-icon" aria-hidden="true">🛈</span>
   362	        <div class="workbench-pending-signoff-body">
   363	          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
   364	          <span>
   365	            你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属
   366	            authority — 你的角色当前不会看到 disabled UI，而是这条 explicit
   367	            "排队中" 提示。
   368	          </span>
   369	        </div>
   370	      </section>
   371	
   372	      <section
   373	        id="approval-center-panel"
   374	        class="workbench-approval-center"
   375	        data-approval-role="KOGAMI"
   376	        aria-labelledby="approval-center-title"
   377	      >
   378	        <header>
   379	          <p class="eyebrow">审批中心</p>
   380	          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
   381	        </header>
   382	        <div class="workbench-approval-grid">
   383	          <article class="workbench-approval-lane" data-approval-lane="pending">
   384	            <h3>待审 · Pending</h3>
   385	            <p>已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.</p>
   386	          </article>
   387	          <article class="workbench-approval-lane" data-approval-lane="accept">
   388	            <h3>通过 · Accept</h3>
   389	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
   390	          </article>

 succeeded in 0ms:
68:      status.textContent = `${label} panel failed independently: ${error.message || error}`;
85:  const status = workbenchElement("workbench-control-status");
87:    status.textContent =
94:  const status = workbenchElement("workbench-document-status");
96:    status.textContent =
103:  const status = workbenchElement("workbench-circuit-status");
105:    status.textContent =
158:    badge.textContent    = workflowState;
209:  element.textContent = message;
214:  workbenchElement("workbench-packet-source-status").textContent = message;
219:  workbenchElement("workbench-result-mode").textContent = message;
330:    summaryElement.textContent = "这里会列出最近成功生成的 archive；你可以直接点“恢复这个 Archive”，不用再自己查本地路径。";
335:      title.textContent = "暂无最近 Archive";
337:      detail.textContent = "等你先生成一份 archive，或把已有 archive 放到默认目录后，这里就会出现可恢复列表。";
344:  summaryElement.textContent = "这些 archive 都来自默认 archive root；点卡片就会自动把它恢复回当前 workbench。";
354:    systemChip.textContent = entry.system_id || "unknown_system";
359:    stateChip.textContent = entry.ready_for_spec_build ? "ready" : "blocked";
363:    workspaceChip.textContent = entry.has_workspace_snapshot
370:    title.textContent = entry.system_title
376:    summaryText.textContent = `${summary.badge} / ${summary.summary}`;
379:    detail.textContent = `${summary.detail} / ${entry.created_at_utc || "时间未知"}`;
384:    action.textContent = "恢复这个 Archive";
406:      workbenchElement("default-archive-root").textContent = payload.default_archive_root;
669:  badge.textContent = snapshot.badgeText;
734:    packetSourceStatus: workbenchElement("workbench-packet-source-status").textContent,
899:    workbenchElement(elementId).textContent = text || fallbackText;
903:    workbenchElement(elementId).textContent = fallbackText;
906:  workbenchElement(elementId).textContent = String(value);
998:  element.textContent = text;
1003:  workbenchElement(`workbench-stage-${stageName}-note`).textContent = note;
1009:  element.textContent = text;
1015:  element.textContent = text;
1021:  element.textContent = text;
1027:  element.textContent = text;
1033:  element.textContent = text;
1092:  chip.textContent = text;
1102:  detail.textContent = message;
1122:  strong.textContent = title;
1130:  body.textContent = detail;
1153:  title.textContent = id || "clarification";
1155:  promptText.textContent = prompt || "等待补齐说明。";
1165:  rationaleText.textContent = `为什么要补：${rationale || "等待说明。"}`;
1167:  requiredForText.textContent = `补齐后用于：${requiredFor || "spec_build"}`;
1196:  strong.textContent = title;
1198:  body.textContent = detail;
1208:  pathText.textContent = `目标位置：${targetPath || "packet JSON"}`;
1210:  effectText.textContent = `修复结果：${expectedEffect || "修复后再重跑验证。"}`;
1233:    title.textContent = doc.title || doc.id || "未命名文档";
1246:    location.textContent = doc.location || "未提供路径";
1269:    title.textContent = signal.label || signal.id || "未命名信号";
1283:    detail.textContent = signal.id ? `signal_id = ${signal.id}` : "未提供 signal_id";
1367:    title.textContent = fallbackTitle;
1369:    detail.textContent = fallbackText;
1444:    title.textContent = fallbackTitle;
1446:    detail.textContent = fallbackText;
1778:    statusElement.textContent = "当前 Packet：等待第一次载入";
1786:    statusElement.textContent = `当前 Packet：最新版本 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
1793:  statusElement.textContent = `当前 Packet：历史版本 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
1811:      statusElement.textContent = "当前草稿：JSON 待修正";
1812:      noteElement.textContent = `当前输入区已经恢复了草稿文本，但它还不是合法 JSON：${parsed.error}`;
1817:      statusElement.textContent = "当前草稿：尚未建立版本基线";
1818:      noteElement.textContent = "当前输入区已经有 packet，但还没进入已保存版本历史；你可以先把它保存成草稿，再继续切换样例或重跑。";
1822:    statusElement.textContent = "当前草稿：等待第一次载入";
1823:    noteElement.textContent = "先载入一个 packet；之后直接改 JSON 但还没运行时，也可以先把当前版本存成草稿。";
1830:    statusElement.textContent = "当前草稿：JSON 暂不可保存";
1831:    noteElement.textContent = `当前输入区还不是合法 JSON，所以版本历史暂时无法收纳它：${parsed.error}`;
1837:    statusElement.textContent = `当前草稿：已与「${baselineEntry.title}」同步`;
1838:    noteElement.textContent = "如果接下来切换样例、恢复旧版本或应用浏览器写回，系统会先检查是否存在新的有效草稿。";
1843:  statusElement.textContent = `当前草稿：有未保存改动（相对「${baselineEntry.title}」）`;
1844:  noteElement.textContent = "你可以先手动保存这份 Packet 草稿；如果现在切换样例、恢复旧版本或应用浏览器写回，系统也会先自动保存这份有效草稿，刷新页面后也会继续恢复当前工作区。";
1981:  workbenchElement("workbench-packet-history-compare-summary").textContent =
2003:      title.textContent = "暂无版本";
2005:      detail.textContent = "先载入 reference/template、本地 JSON，或在页面里写回一次 packet。";
2030:    systemChip.textContent = entry.payload.system_id || "unknown_system";
2034:    coverageChip.textContent = `${summary.logicNodes}L / ${summary.scenarios}S / ${summary.faultModes}F`;
2038:    timeChip.textContent = entry.timeLabel;
2043:    title.textContent = entry.title;
2046:    summaryText.textContent = entry.summary;
2049:    detail.textContent = entry.detail;
2053:    action.textContent = selected ? "当前输入区正在使用这个 Packet 版本" : "点此恢复这个 Packet 版本";
2390:  workbenchElement(titleElementId).textContent = snapshot.title;
2398:    label.textContent = field.label;
2403:    value.textContent = field.value;
2423:  workbenchElement("workbench-history-compare-summary").textContent =
2470:    statusElement.textContent = "当前查看：正在生成新结果";
2478:    statusElement.textContent = "当前查看：样例准备中";
2486:    statusElement.textContent = "当前查看：等待第一次结果";
2494:    statusElement.textContent = `当前查看：最新结果 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
2501:  statusElement.textContent = `当前查看：历史回看 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
2514:      title.textContent = "暂无结果";
2516:      detail.textContent = "先点一个一键预设或手动生成一次 bundle。";
2541:    stateChip.textContent = entry.stateLabel;
2546:    archiveChip.textContent = entry.archived ? "已留档" : "未留档";
2550:    timeChip.textContent = entry.timeLabel;
2555:    title.textContent = entry.title;
2558:    summary.textContent = entry.summary;
2561:    detail.textContent = entry.detail;
2565:    action.textContent = selected ? "当前主看板正在显示这次结果" : "点此回看这次结果";
2639:  workbenchElement("bundle-json-output").textContent = prettyJson({
2913:      li.textContent = String(item);
3013:  badge.textContent = explainRuntimeBadgeText(runtime);
3019:    summary.textContent = runtime.detail || "LLM explain 功能已搁置。";
3020:    backendStrong.textContent = "已搁置";
3021:    backendDetail.textContent = "LLM 后端已从活跃代码库搁置，见 archive/shelved/llm-features/SHELVED.md。";
3022:    sourceStrong.textContent = "已搁置";
3023:    sourceDetail.textContent = "explain 路由已移除，不会产生新的观察记录。";
3024:    cacheStrong.textContent = "已搁置";
3025:    cacheDetail.textContent = "LLM 缓存链路已停用；无 cached_at / 命中统计。";
3026:    boundaryStrong.textContent = runtime.boundaryNote || "LLM 已搁置 — 非控制真值";
3031:    summary.textContent = "当前 workbench 响应还没带 explain runtime 观察值，所以这里只保留占位。";
3033:    summary.textContent = `${runtime.detail || "已收到 explain runtime 观察值。"} 最近观测时间：${runtime.observedAt}。`;
3035:    summary.textContent = runtime.detail || "已收到 explain runtime 观察值。";
3041:    backendStrong.textContent = `${backendText} · ${modelText}`;
3045:      backendDetail.textContent = `最近 pitch_prewarm 请求的是 ${requestedBackendText} · ${requestedModelText}，但当前观察到的运行后端不是这套，需要先纠正 demo_server。`;
3047:      backendDetail.textContent = `这是最近一次 explain runtime 观测到的后端组合。观测时间：${runtime.observedAt}。`;
3049:      backendDetail.textContent = "这是当前 demo_server 暴露出来的 explain 后端组合；它只是操作者运行观察值，不改变任何控制真值。";
3052:    backendStrong.textContent = "未报告";
3053:    backendDetail.textContent = "后端暂未在 bootstrap / bundle 响应中提供 explain_runtime.llm_backend / llm_model，前端保留占位。";
3056:  sourceStrong.textContent = explainRuntimeSourceLabel(runtime.source);
3058:    sourceDetail.textContent = "虽然最近预热流程有结果，但它对应的 backend / model 和当前期望不一致，所以这里会明确提醒，不把它误当成安全可用的缓存状态。";
3060:    sourceDetail.textContent = "最近一次 explain 命中了预热缓存，说明 prewarm 生效；重启 demo_server 后需重新预热。";
3062:    sourceDetail.textContent = "最近一次 explain 走了实时 LLM（缓存未命中或未启用），请关注首次响应时延。";
3064:    sourceDetail.textContent = "最近一次 explain 报错，详情请看 dev 抽屉 raw payload 或 server 日志。";
3066:    sourceDetail.textContent = "本轮还没观察到 explain 调用；一旦用户在 chat / demo 舱发起一次 explain，这里就会亮起。";
3072:    cacheStrong.textContent = runtime.cachedAt;
3073:    cacheDetail.textContent = `cached_at 上报为 ${runtime.cachedAt}${hitsPart}${expectedPart}。explain 缓存只在 demo_server 进程内有效，重启或换 backend 都会清空，需要重新预热。`;
3083:    cacheStrong.textContent = parts.join(" / ") || "待命";
3084:    cacheDetail.textContent = "尚未看到 cached_at 时间戳，但最近 pitch_prewarm 已经回传了命中统计；仍可用来判断缓存是否在服务。";
3086:    cacheStrong.textContent = "待命";
3087:    cacheDetail.textContent = "尚未看到 cached_at。若刚刚跑过 prewarm，请核对 demo_server 输出；否则这里会保持“待命”直到首次 explain 观察上报。";
3090:  boundaryStrong.textContent = runtime.boundaryNote || "runtime status only";
3096:    statusElement.textContent = "本次未生成 archive package。";
3100:  statusElement.textContent = `已生成 archive package：${archive.archive_dir}`;
3185:    systemId: bundle.system_id || assessment.system_id || workbenchElement("workbench-fingerprint-system-id").textContent,
3186:    objective: assessment.objective || workbenchElement("workbench-fingerprint-objective").textContent,
3188:    sourceTruth: generatedSpec.source_of_truth || workbenchElement("workbench-fingerprint-source-truth").textContent,
3343:  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
3344:  workbenchElement("bundle-ready-state").textContent = ready ? "Ready" : "Blocked";
3346:  workbenchElement("bundle-scenario-id").textContent = bundle.selected_scenario_id || "(none)";
3347:  workbenchElement("bundle-fault-mode-id").textContent = bundle.selected_fault_mode_id || "(none)";
3348:  workbenchElement("clarification-gate-status").textContent = clarification.gate_status || "-";
3349:  workbenchElement("clarification-gating-statement").textContent = clarification.gating_statement || "-";
3353:  workbenchElement("bundle-blocking-reasons").textContent = blockingReasons.length
3399:  workbenchElement("bundle-json-output").textContent = prettyJson(payload);
3490:  workbenchElement("default-archive-root").textContent = payload.default_archive_root || "(unknown)";
3667:      setCurrentWorkbenchRunLabel(button.textContent.trim());
3743:    workbenchElement("view-mode-hint").textContent = mode === "beginner"
3765:// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
3774:    banner.setAttribute("data-feedback-mode", mode);
3783:  const chip = document.getElementById("workbench-feedback-mode");
3785:    chip.setAttribute("data-feedback-mode", mode);
3788:      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
3796:  const chip = document.getElementById("workbench-feedback-mode");
3801:  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
3897:  result.textContent = `POST ${scenario.endpoint} ...`;
3923:      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
3927:    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
3931:      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
3933:      result.textContent = `network error: ${err && err.message ? err.message : err}`;
4000:    const suffix = label.textContent.includes("/")
4001:      ? label.textContent.split("/").slice(1).join("/").trimStart()
4003:    label.textContent = suffix ? `${name.trim()} / ${suffix}` : name.trim();
4014:// Reads /api/workbench/state-of-world and writes the four advisory
4018:const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";
4021:  const bar = document.getElementById("workbench-state-of-world-bar");
4037:        slot.textContent =

exec
/bin/zsh -lc 'find src/well_harness/adapters -maxdepth 2 -type f | sort' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/adapters/__init__.py
src/well_harness/adapters/__pycache__/__init__.cpython-311.pyc
src/well_harness/adapters/__pycache__/__init__.cpython-312.pyc
src/well_harness/adapters/__pycache__/bleed_air_adapter.cpython-311.pyc
src/well_harness/adapters/__pycache__/bleed_air_adapter.cpython-312.pyc
src/well_harness/adapters/__pycache__/c919_etras_adapter.cpython-311.pyc
src/well_harness/adapters/__pycache__/c919_etras_adapter.cpython-312.pyc
src/well_harness/adapters/__pycache__/c919_etras_intake_packet.cpython-311.pyc
src/well_harness/adapters/__pycache__/c919_etras_intake_packet.cpython-312.pyc
src/well_harness/adapters/__pycache__/efds_adapter.cpython-311.pyc
src/well_harness/adapters/__pycache__/efds_adapter.cpython-312.pyc
src/well_harness/adapters/__pycache__/landing_gear_adapter.cpython-311.pyc
src/well_harness/adapters/__pycache__/landing_gear_adapter.cpython-312.pyc
src/well_harness/adapters/__pycache__/landing_gear_intake_packet.cpython-312.pyc
src/well_harness/adapters/__pycache__/thrust_reverser_intake_packet.cpython-311.pyc
src/well_harness/adapters/__pycache__/thrust_reverser_intake_packet.cpython-312.pyc
src/well_harness/adapters/bleed_air_adapter.py
src/well_harness/adapters/bleed_air_intake_packet.py
src/well_harness/adapters/c919_etras_adapter.py
src/well_harness/adapters/c919_etras_frozen_v1/__init__.py
src/well_harness/adapters/c919_etras_frozen_v1/cmd2_controller.py
src/well_harness/adapters/c919_etras_frozen_v1/cmd3_latch_controller.py
src/well_harness/adapters/c919_etras_frozen_v1/fadec_deploy_logic.py
src/well_harness/adapters/c919_etras_frozen_v1/fadec_stow_logic.py
src/well_harness/adapters/c919_etras_frozen_v1/lock_status_aggregator.py
src/well_harness/adapters/c919_etras_frozen_v1/safety_interlock_manager.py
src/well_harness/adapters/c919_etras_frozen_v1/signals.py
src/well_harness/adapters/c919_etras_frozen_v1/state_machine.py
src/well_harness/adapters/c919_etras_frozen_v1/telemetry_logger.py
src/well_harness/adapters/c919_etras_frozen_v1/tick.py
src/well_harness/adapters/c919_etras_frozen_v1/tr_wow_filter.py
src/well_harness/adapters/c919_etras_frozen_v1/wow_selector.py
src/well_harness/adapters/c919_etras_intake_packet.py
src/well_harness/adapters/efds_adapter.py
src/well_harness/adapters/landing_gear_adapter.py
src/well_harness/adapters/landing_gear_intake_packet.py
src/well_harness/adapters/thrust_reverser_intake_packet.py

exec
/bin/zsh -lc "git diff --name-only main..83d69e4 -- src/well_harness && printf '\\n---ALL WELL_HARNESS CHANGES---\\n' && git diff --stat main..83d69e4 -- src/well_harness" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js

---ALL WELL_HARNESS CHANGES---
 src/well_harness/static/workbench.html | 54 +++++++++++++++++-----------------
 src/well_harness/static/workbench.js   |  2 +-
 2 files changed, 28 insertions(+), 28 deletions(-)

codex
The only `src/well_harness/**` changes are `static/workbench.html` and `static/workbench.js`, which matches the claimed red line. I’m now tracing the runtime write paths for the feedback chip, boot placeholders, and state-of-world labels to see whether hydration can bypass the new bilingual contract after initial load.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '50,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3990,4065p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n \"bootWorkbench|installFeedbackModeAffordance\\(|setFeedbackMode\\(|workbench-authority-banner-headline|workbench-trust-banner-headline\" src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3990	
  3991	function setWorkbenchIdentity(name) {
  3992	  const chip = document.getElementById("workbench-identity");
  3993	  if (!chip || typeof name !== "string" || !name.trim()) {
  3994	    return false;
  3995	  }
  3996	  chip.setAttribute("data-identity-name", name.trim());
  3997	  const label = chip.querySelector("strong");
  3998	  if (label) {
  3999	    // Preserve the trailing role suffix (e.g., "/ Engineer") if present.
  4000	    const suffix = label.textContent.includes("/")
  4001	      ? label.textContent.split("/").slice(1).join("/").trimStart()
  4002	      : "";
  4003	    label.textContent = suffix ? `${name.trim()} / ${suffix}` : name.trim();
  4004	  }
  4005	  applyRoleAffordance();
  4006	  return true;
  4007	}
  4008	
  4009	if (typeof window !== "undefined") {
  4010	  window.setWorkbenchIdentity = setWorkbenchIdentity;
  4011	}
  4012	
  4013	// E11-06 (2026-04-26): hydrate the state-of-the-world status bar.
  4014	// Reads /api/workbench/state-of-world and writes the four advisory
  4015	// fields into the bar. Falls back to "—" so the page never shows a
  4016	// half-broken bar. Failures are silent (the bar starts with "…"
  4017	// placeholders so there is no flash of the wrong content).
  4018	const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";
  4019	
  4020	async function hydrateStateOfWorldBar() {
  4021	  const bar = document.getElementById("workbench-state-of-world-bar");
  4022	  if (!bar) {
  4023	    return;
  4024	  }
  4025	  try {
  4026	    const response = await fetch(WORKBENCH_STATE_OF_WORLD_PATH, {
  4027	      method: "GET",
  4028	      headers: { Accept: "application/json" },
  4029	    });
  4030	    if (!response.ok) {
  4031	      return;
  4032	    }
  4033	    const payload = await response.json();
  4034	    const writeField = (key, value) => {
  4035	      const slot = bar.querySelector(`[data-sow-value="${key}"]`);
  4036	      if (slot) {
  4037	        slot.textContent =
  4038	          value === null || value === undefined || value === ""
  4039	            ? "—"
  4040	            : String(value);
  4041	      }
  4042	    };
  4043	    writeField("truth_engine_sha", payload.truth_engine_sha);
  4044	    writeField("recent_e2e_label", payload.recent_e2e_label);
  4045	    writeField("adversarial_label", payload.adversarial_label);
  4046	    writeField("open_known_issues_count", payload.open_known_issues_count);
  4047	  } catch (_err) {
  4048	    // Silent — the bar already shows "…" placeholders, which renders as
  4049	    // a benign "still loading" state instead of a broken half-page.
  4050	  }
  4051	}
  4052	
  4053	window.addEventListener("DOMContentLoaded", () => {
  4054	  bootWorkbenchShell();
  4055	  installViewModeHandlers();
  4056	  installFeedbackModeAffordance();
  4057	  installWowStarters();
  4058	  void hydrateStateOfWorldBar();
  4059	  // E11-08: apply role affordance after DOM is ready. Honors
  4060	  // ?identity=<name> URL param so demos / tests can flip identity
  4061	  // without rebuilding the page.
  4062	  try {
  4063	    const params = new URLSearchParams(window.location.search);
  4064	    const requested = params.get("identity");
  4065	    if (requested && requested.trim()) {

 succeeded in 0ms:
61:function bootWorkbenchColumnSafely(columnName, bootFn) {
84:function bootWorkbenchControlPanel() {
93:function bootWorkbenchDocumentPanel() {
102:function bootWorkbenchCircuitPanel() {
111:function bootWorkbenchShell() {
112:  bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
113:  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
114:  bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
3767:// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
3778:function setFeedbackMode(mode) {
3795:function installFeedbackModeAffordance() {
4054:  bootWorkbenchShell();
4056:  installFeedbackModeAffordance();

exec
/bin/zsh -lc "rg -n \"workbench-authority-banner-headline|workbench-trust-banner-headline|workbench-trust-banner|workbench-authority-banner|setFeedbackMode\\(|installFeedbackModeAffordance\\(|workbench-control-status|workbench-document-status|workbench-circuit-status|data-sow-value|workbench-sow-label|state-of-world-bar\" src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
85:  const status = workbenchElement("workbench-control-status");
94:  const status = workbenchElement("workbench-document-status");
103:  const status = workbenchElement("workbench-circuit-status");
3766:// it onto #workbench-trust-banner so the banner shows only when mode =
3767:// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
3772:  const banner = document.getElementById("workbench-trust-banner");
3778:function setFeedbackMode(mode) {
3795:function installFeedbackModeAffordance() {
3797:  const banner = document.getElementById("workbench-trust-banner");
3802:  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
3810:        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
4021:  const bar = document.getElementById("workbench-state-of-world-bar");
4035:      const slot = bar.querySelector(`[data-sow-value="${key}"]`);
4056:  installFeedbackModeAffordance();

codex
I’ve isolated one likely blind spot already: the red-line test only scans four concrete backend files and does not traverse `src/well_harness/adapters/`, even though the constitution explicitly names that directory as part of the red line. I’m validating whether that’s the only gap or whether the guard also missed any newly introduced Chinese anchor from the trust banner body.
exec
/bin/zsh -lc "python - <<'PY'
from pathlib import Path
import re
html = Path('src/well_harness/static/workbench.html').read_text(encoding='utf-8')
# crude extract of lines containing Chinese plus English separator dot for changed surfaces only
for i,line in enumerate(html.splitlines(),1):
    if '·' in line and re.search(r'[\\u4e00-\\u9fff]', line):
        print(f'{i}: {line.strip()}')
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

 succeeded in 0ms:
# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY

**Date:** 2026-04-26
**Status:** in_review (Tier-A, ≥15 REWRITE rows → 5-persona dispatch)
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
that P2 enumerated during the E11-15d Tier-B review (see
`tests/test_workbench_approval_flow_polish.py:189-194`).

---

## 1. Tier classification

Per the constitution, Tier = **Tier-A** iff
`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.

| Metric | Count |
|--------|------:|
| copy_diff_lines (workbench.html + workbench.js)        | ~38 |
| REWRITE rows (display strings rewritten in place)      | **22** |
| DELETE rows (English-only string removed without bilingual replacement) | 0 |
| ADD rows (new strings introduced for the first time)   | 0 |

**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus
P1, P2, P4, P5 per Tier-A 5-persona requirement.

---

## 2. Surface table (REWRITE = 22)

Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
passing without contract churn.

| # | Surface | File:Line | Old (English-only) | New (bilingual) |
|---|---------|-----------|---------------------|-----------------|
| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |

(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs
for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`
counts in the metric table above.)

---

## 3. Out of scope (explicitly deferred — surface-honesty closure)

E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
following surfaces remain English-only and are **deferred to future sub-phases
or constitutional decisions**, not silently included:

| Deferred surface | Why deferred | File:Line |
|------------------|--------------|-----------|
| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |

**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
"all" or "the last". The deferred list above is **non-exhaustive** — if a
reviewer finds another English-only user-visible surface not listed here that is
neither REWRITE in this slice nor in the deferred table, that finding is
**legitimate** and a CHANGES_REQUIRED is appropriate.

---

## 4. Truth-engine red line

Display-copy edits only. `controller.py` / `runner.py` / `models.py` /
`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep
guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::
test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any
of the 23 Chinese display strings introduced here.

---

## 5. Lockstep test impact

| Existing test file | Impact | Reason |
|--------------------|--------|--------|
| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |

Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).

---

## 6. Persona dispatch plan

Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e
**lead** is **P3**.

| Persona | Lens |
|---------|------|
| P1 | Engineer-task-flow regression |
| P2 | Surface-inventory honesty + closure-claim guards |
| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
| P4 | Lockstep test contract preservation (no churn on existing locks) |
| P5 | Truth-engine red-line + JS-HTML lockstep |

**Codex degradation contingency:** if all 5 codex accounts are
secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply
**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:
Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the
fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
entry. Self-signing requires the standard 1221-test green + repo-honesty self-
review (this inventory + Section 3 surface-honesty pledge satisfy that bar).

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 742ms:
...................................................................      [100%]
67 passed in 0.57s

codex
One detail in the requested scenario doesn’t match the code path: `installFeedbackModeAffordance()` does not currently call `setFeedbackMode("manual_feedback_override")`; it only mirrors the existing `data-feedback-mode` onto the trust banner. I’m checking whether `setFeedbackMode` is invoked anywhere else, because that determines whether the static `<strong>` gets rewritten during normal boot or only on future runtime updates.
exec
/bin/zsh -lc 'rg -n "setFeedbackMode" src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
3767:// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
3778:function setFeedbackMode(mode) {

exec
/bin/zsh -lc "rg -n \"window\\..*setFeedbackMode|setFeedbackMode =|installFeedbackModeAffordance\\(\" src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
3795:function installFeedbackModeAffordance() {
4056:  installFeedbackModeAffordance();

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import ast, re
src = Path('tests/test_workbench_e11_15e_chinese_first_bundle.py').read_text(encoding='utf-8')
# rough parse of bilingual list and guard list via ast on list literals
# Find the first parametrized bilingual list and guard list.
mod = ast.parse(src)
class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.bilingual=None
        self.guard=None
    def visit_FunctionDef(self,node):
        if node.name=='test_workbench_html_carries_bilingual_e11_15e_string':
            # decorator args list
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(getattr(dec.func,'attr',None),'',None) is None:
                    pass
        self.generic_visit(node)
vis=Visitor()
# easier regex between markers
m1 = re.search(r'\"bilingual\",\\n\\s*\\[(.*?)\\n\\s*\\],\\n\\)', src, re.S)
m2 = re.search(r'e11_15e_chinese = \\[(.*?)\\n\\s*\\]', src, re.S)
for label, m in [('bilingual',m1),('guard',m2)]:
    print(label, bool(m))
    block='['+m.group(1)+']'
    vals=ast.literal_eval(block)
    print(label, len(vals))
    if label=='bilingual':
        bilingual=vals
    else:
        guard=vals
print('Missing guard anchors for bilingual entries:')
for b in bilingual:
    if not any(g in b for g in guard):
        print('MISS:', b)
print('Guard entries unused against bilingual set:')
for g in guard:
    if not any(g in b for b in bilingual):
        print('UNUSED:', g)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
bilingual True
bilingual 24
guard True
guard 23
Missing guard anchors for bilingual entries:
MISS: 真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings
Guard entries unused against bilingual set:

codex
I’m checking one last boundary question before I write the verdict: whether `controller_adapter.py` should be treated as part of the same protected adapter boundary, or whether the constitutional red line is intentionally limited to `src/well_harness/adapters/` plus the four named backend files. That affects whether the current guard is merely incomplete or materially under-scoped.
exec
/bin/zsh -lc "nl -ba src/well_harness/controller_adapter.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	from __future__ import annotations
     2	
     3	from dataclasses import asdict, dataclass
     4	from typing import Any, Mapping, Protocol
     5	
     6	from well_harness.controller import DeployController
     7	from well_harness.models import ControllerExplain, ControllerOutputs, HarnessConfig, ResolvedInputs
     8	
     9	
    10	CONTROLLER_TRUTH_ADAPTER_METADATA_KIND = "well-harness-controller-truth-adapter-metadata"
    11	CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION = 1
    12	CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID = (
    13	    "https://well-harness.local/json_schema/controller_truth_adapter_metadata_v1.schema.json"
    14	)
    15	
    16	
    17	@dataclass(frozen=True)
    18	class ControllerTruthMetadata:
    19	    adapter_id: str
    20	    system_id: str
    21	    truth_kind: str
    22	    source_of_truth: str
    23	    description: str
    24	    # P42 (2026-04-20) governance fields · None sentinel = pre-P42/unclassified.
    25	    # Production adapters MUST set both explicitly (enforced by
    26	    # tests/test_metadata_registry_consistency.py). Dataclass defaults exist
    27	    # only for forward-compat loader paths and test fixtures.
    28	    truth_level: str | None = None
    29	    status: str | None = None
    30	
    31	    def to_dict(self) -> dict:
    32	        return controller_truth_metadata_to_dict(self)
    33	
    34	
    35	_GOVERNANCE_FIELDS = ("truth_level", "status")
    36	
    37	
    38	def controller_truth_metadata_to_dict(metadata: ControllerTruthMetadata) -> dict:
    39	    payload = {
    40	        "$schema": CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
    41	        "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
    42	        "version": CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
    43	        **asdict(metadata),
    44	    }
    45	    # P42: drop None-valued governance fields so v1 payload shape is byte-
    46	    # identical to pre-P42 when governance unset. 字段缺失 = pre-P42/unclassified;
    47	    # downstream consumers MUST NOT treat missing field as "already governed".
    48	    for field in _GOVERNANCE_FIELDS:
    49	        if payload.get(field) is None:
    50	            payload.pop(field, None)
    51	    return payload
    52	
    53	
    54	@dataclass(frozen=True)
    55	class GenericTruthEvaluation:
    56	    system_id: str
    57	    active_logic_node_ids: tuple[str, ...]
    58	    asserted_component_values: dict[str, Any]
    59	    completion_reached: bool
    60	    blocked_reasons: tuple[str, ...]
    61	    summary: str
    62	
    63	    def to_dict(self) -> dict[str, Any]:
    64	        return generic_truth_evaluation_to_dict(self)
    65	
    66	
    67	def generic_truth_evaluation_to_dict(evaluation: GenericTruthEvaluation) -> dict[str, Any]:
    68	    return {
    69	        "system_id": evaluation.system_id,
    70	        "active_logic_node_ids": list(evaluation.active_logic_node_ids),
    71	        "asserted_component_values": dict(evaluation.asserted_component_values),
    72	        "completion_reached": evaluation.completion_reached,
    73	        "blocked_reasons": list(evaluation.blocked_reasons),
    74	        "summary": evaluation.summary,
    75	    }
    76	
    77	
    78	class ControllerTruthAdapter(Protocol):
    79	    metadata: ControllerTruthMetadata
    80	
    81	    def explain(self, inputs: ResolvedInputs) -> ControllerExplain:
    82	        ...
    83	
    84	    def evaluate(self, inputs: ResolvedInputs) -> ControllerOutputs:
    85	        ...
    86	
    87	    def evaluate_with_explain(self, inputs: ResolvedInputs) -> tuple[ControllerOutputs, ControllerExplain]:
    88	        ...
    89	
    90	
    91	class GenericControllerTruthAdapter(Protocol):
    92	    metadata: ControllerTruthMetadata
    93	
    94	    def load_spec(self) -> dict[str, Any]:
    95	        ...
    96	
    97	    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
    98	        ...
    99	
   100	
   101	REFERENCE_DEPLOY_CONTROLLER_METADATA = ControllerTruthMetadata(
   102	    adapter_id="reference-deploy-controller",
   103	    system_id="reference_thrust_reverser_deploy",
   104	    truth_kind="python-controller-adapter",
   105	    source_of_truth="src/well_harness/controller.py",
   106	    description="Wraps DeployController as the current reference system truth adapter.",
   107	    truth_level="certified",  # P42: aligned with docs/provenance/adapter_truth_levels.yaml row "thrust-reverser"
   108	    status="In use",
   109	)
   110	
   111	
   112	class ReferenceDeployControllerAdapter:
   113	    def __init__(self, config: HarnessConfig | None = None) -> None:
   114	        self.config = config or HarnessConfig()
   115	        self.metadata = REFERENCE_DEPLOY_CONTROLLER_METADATA
   116	        self._controller = DeployController(self.config)
   117	
   118	    def explain(self, inputs: ResolvedInputs) -> ControllerExplain:
   119	        return self._controller.explain(inputs)
   120	
   121	    def evaluate(self, inputs: ResolvedInputs) -> ControllerOutputs:
   122	        return self._controller.evaluate(inputs)
   123	
   124	    def evaluate_with_explain(self, inputs: ResolvedInputs) -> tuple[ControllerOutputs, ControllerExplain]:
   125	        return self._controller.evaluate_with_explain(inputs)
   126	
   127	    def load_spec(self) -> dict[str, Any]:
   128	        from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict
   129	
   130	        return workbench_spec_to_dict(current_reference_workbench_spec(self.config))
   131	
   132	    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
   133	        inputs = resolved_inputs_from_snapshot(snapshot)
   134	        outputs, explain = self.evaluate_with_explain(inputs)
   135	        logic_rows = (explain.logic1, explain.logic2, explain.logic3, explain.logic4)
   136	        active_logic_node_ids = tuple(logic.logic_name for logic in logic_rows if logic.active)
   137	        blocked_reasons = tuple(
   138	            f"{logic.logic_name}:{condition.name}"
   139	            for logic in logic_rows
   140	            if not logic.active
   141	            for condition in logic.failed_conditions
   142	        )
   143	        return GenericTruthEvaluation(
   144	            system_id=self.metadata.system_id,
   145	            active_logic_node_ids=active_logic_node_ids,
   146	            asserted_component_values={
   147	                # Input conditions (raw signals from snapshot)
   148	                "sw1": inputs.sw1,
   149	                "sw2": inputs.sw2,
   150	                "radio_altitude_ft": inputs.radio_altitude_ft,
   151	                "engine_running": inputs.engine_running,
   152	                "aircraft_on_ground": inputs.aircraft_on_ground,
   153	                "eec_enable": inputs.eec_enable,
   154	                "n1k": inputs.n1k,
   155	                "tra_deg": inputs.tra_deg,
   156	                "reverser_inhibited": inputs.reverser_inhibited,
   157	                # Plant feedback (drives VDT90 / L4 condition)
   158	                "deploy_90_percent_vdt": inputs.deploy_90_percent_vdt,
   159	                # Output commands
   160	                "tls_115vac_cmd": outputs.tls_115vac_cmd,
   161	                "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
   162	                "eec_deploy_cmd": outputs.eec_deploy_cmd,
   163	                "pls_power_cmd": outputs.pls_power_cmd,
   164	                "pdu_motor_cmd": outputs.pdu_motor_cmd,
   165	                "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
   166	            },
   167	            completion_reached=outputs.throttle_electronic_lock_release_cmd,
   168	            blocked_reasons=blocked_reasons,
   169	            summary=(
   170	                f"Reference deploy truth evaluated with {len(active_logic_node_ids)} active logic nodes; "
   171	                f"completion={'yes' if outputs.throttle_electronic_lock_release_cmd else 'no'}."
   172	            ),
   173	        )
   174	
   175	
   176	def build_reference_controller_adapter(config: HarnessConfig | None = None) -> ReferenceDeployControllerAdapter:
   177	    return ReferenceDeployControllerAdapter(config)
   178	
   179	
   180	def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
   181	    if key not in snapshot:
   182	        raise KeyError(f"missing snapshot value: {key}")
   183	    return snapshot[key]
   184	
   185	
   186	def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
   187	    value = _require_snapshot_value(snapshot, key)
   188	    if isinstance(value, bool):
   189	        return value
   190	    if isinstance(value, (int, float)) and value in (0, 1):
   191	        return bool(value)
   192	    raise TypeError(f"snapshot value {key!r} must be a bool-compatible value")
   193	
   194	
   195	def _snapshot_float(snapshot: Mapping[str, Any], key: str) -> float:
   196	    value = _require_snapshot_value(snapshot, key)
   197	    if isinstance(value, bool):
   198	        raise TypeError(f"snapshot value {key!r} must be numeric")
   199	    if isinstance(value, (int, float)):
   200	        return float(value)
   201	    raise TypeError(f"snapshot value {key!r} must be numeric")
   202	
   203	
   204	def resolved_inputs_from_snapshot(snapshot: Mapping[str, Any]) -> ResolvedInputs:
   205	    return ResolvedInputs(
   206	        radio_altitude_ft=_snapshot_float(snapshot, "radio_altitude_ft"),
   207	        tra_deg=_snapshot_float(snapshot, "tra_deg"),
   208	        sw1=_snapshot_bool(snapshot, "sw1"),
   209	        sw2=_snapshot_bool(snapshot, "sw2"),
   210	        engine_running=_snapshot_bool(snapshot, "engine_running"),
   211	        aircraft_on_ground=_snapshot_bool(snapshot, "aircraft_on_ground"),
   212	        reverser_inhibited=_snapshot_bool(snapshot, "reverser_inhibited"),
   213	        eec_enable=_snapshot_bool(snapshot, "eec_enable"),
   214	        n1k=_snapshot_float(snapshot, "n1k"),
   215	        max_n1k_deploy_limit=_snapshot_float(snapshot, "max_n1k_deploy_limit"),
   216	        tls_unlocked_ls=_snapshot_bool(snapshot, "tls_unlocked_ls"),
   217	        all_pls_unlocked_ls=_snapshot_bool(snapshot, "all_pls_unlocked_ls"),
   218	        reverser_not_deployed_eec=_snapshot_bool(snapshot, "reverser_not_deployed_eec"),
   219	        reverser_fully_deployed_eec=_snapshot_bool(snapshot, "reverser_fully_deployed_eec"),
   220	        deploy_90_percent_vdt=_snapshot_bool(snapshot, "deploy_90_percent_vdt"),
   221	    )

exec
/bin/zsh -lc "rg -n \"controller_adapter|adapters/|truth-engine red line|red line\" .planning/constitution.md AGENTS.md src/well_harness -g '"'!src/well_harness/static/*'"'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/constitution.md:220:- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）
AGENTS.md:24:- Adapters: `src/well_harness/controller_adapter.py` and `src/well_harness/adapters/`
src/well_harness/knowledge_capture.py:7:from well_harness.controller_adapter import GenericControllerTruthAdapter
src/well_harness/second_system_smoke.py:7:from well_harness.adapters import LANDING_GEAR_CONTROLLER_METADATA, build_landing_gear_controller_adapter
src/well_harness/second_system_smoke.py:8:from well_harness.controller_adapter import GenericControllerTruthAdapter
src/well_harness/second_system_smoke.py:150:        return build_landing_gear_controller_adapter()
src/well_harness/two_system_runtime_comparison.py:6:from well_harness.adapters import build_landing_gear_controller_adapter
src/well_harness/two_system_runtime_comparison.py:7:from well_harness.controller_adapter import GenericControllerTruthAdapter, build_reference_controller_adapter
src/well_harness/two_system_runtime_comparison.py:134:        build_reference_controller_adapter(),
src/well_harness/two_system_runtime_comparison.py:140:        build_landing_gear_controller_adapter(),
src/well_harness/demo.py:7:from well_harness.controller_adapter import build_reference_controller_adapter
src/well_harness/demo.py:1551:    controller_adapter = build_reference_controller_adapter(proposed_config)
src/well_harness/demo.py:1553:        if controller_adapter.explain(row.resolved_inputs).logic3.active:
src/well_harness/system_spec.py:6:from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
src/well_harness/demo_server.py:19:from well_harness.controller_adapter import build_reference_controller_adapter
src/well_harness/demo_server.py:20:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
src/well_harness/demo_server.py:21:from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
src/well_harness/demo_server.py:22:from well_harness.adapters.efds_adapter import build_efds_controller_adapter
src/well_harness/demo_server.py:23:from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
src/well_harness/demo_server.py:626:                    "adapters/ are read-only by design. Workbench surfaces "
src/well_harness/demo_server.py:635:                "controller / runner / models / adapters/ are read-only."
src/well_harness/demo_server.py:720:# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
src/well_harness/demo_server.py:721:# stays put: no controller / runner / models / adapters/*.py changes.
src/well_harness/demo_server.py:2039:    controller_adapter = build_reference_controller_adapter(config)
src/well_harness/demo_server.py:2083:        outputs, explain = controller_adapter.evaluate_with_explain(resolved_inputs)
src/well_harness/demo_server.py:2130:        controller_adapter = build_reference_controller_adapter(config)
src/well_harness/demo_server.py:2131:        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
src/well_harness/demo_server.py:2234:    controller_adapter = build_reference_controller_adapter(config)
src/well_harness/demo_server.py:2268:        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
src/well_harness/demo_server.py:2387:    "thrust-reverser": build_reference_controller_adapter,
src/well_harness/demo_server.py:2388:    "landing-gear": build_landing_gear_controller_adapter,
src/well_harness/demo_server.py:2389:    "bleed-air": build_bleed_air_controller_adapter,
src/well_harness/demo_server.py:2390:    "efds": build_efds_controller_adapter,
src/well_harness/demo_server.py:2393:    "c919-etras": build_c919_etras_controller_adapter,
src/well_harness/adapters/landing_gear_intake_packet.py:43:            location="src/well_harness/adapters/landing_gear_adapter.py",
src/well_harness/controller_adapter.py:176:def build_reference_controller_adapter(config: HarnessConfig | None = None) -> ReferenceDeployControllerAdapter:
src/well_harness/fault_diagnosis.py:6:from well_harness.controller_adapter import GenericControllerTruthAdapter
src/well_harness/adapters/bleed_air_adapter.py:23:from well_harness.controller_adapter import (
src/well_harness/adapters/bleed_air_adapter.py:46:BLEED_AIR_SOURCE_OF_TRUTH = "src/well_harness/adapters/bleed_air_adapter.py"
src/well_harness/adapters/bleed_air_adapter.py:613:def build_bleed_air_controller_adapter() -> BleedAirValveControllerAdapter:
src/well_harness/runner.py:3:from well_harness.controller_adapter import ControllerTruthAdapter, build_reference_controller_adapter
src/well_harness/runner.py:20:        controller_adapter: ControllerTruthAdapter | None = None,
src/well_harness/runner.py:23:        self.controller_adapter = controller_adapter or build_reference_controller_adapter(self.config)
src/well_harness/runner.py:66:                outputs, explain = self.controller_adapter.evaluate_with_explain(inputs)
src/well_harness/scenario_playback.py:8:from well_harness.controller_adapter import GenericControllerTruthAdapter
src/well_harness/adapters/c919_etras_intake_packet.py:48:            location="src/well_harness/adapters/c919_etras_adapter.py",
src/well_harness/adapters/bleed_air_intake_packet.py:50:            location="src/well_harness/adapters/bleed_air_adapter.py",
src/well_harness/adapters/landing_gear_adapter.py:22:from well_harness.controller_adapter import ControllerTruthMetadata, GenericTruthEvaluation
src/well_harness/adapters/landing_gear_adapter.py:39:LANDING_GEAR_SOURCE_OF_TRUTH = "src/well_harness/adapters/landing_gear_adapter.py"
src/well_harness/adapters/landing_gear_adapter.py:380:def build_landing_gear_controller_adapter() -> LandingGearControllerAdapter:
src/well_harness/adapters/efds_adapter.py:20:from well_harness.controller_adapter import (
src/well_harness/adapters/efds_adapter.py:35:EFDS_SOURCE_OF_TRUTH = "src/well_harness/adapters/efds_adapter.py"
src/well_harness/adapters/efds_adapter.py:362:        from well_harness.controller_adapter import GenericTruthEvaluation
src/well_harness/adapters/efds_adapter.py:516:def build_efds_controller_adapter() -> EFDSControllerAdapter:
src/well_harness/adapters/__init__.py:4:    build_landing_gear_controller_adapter,
src/well_harness/adapters/__init__.py:9:    build_efds_controller_adapter,
src/well_harness/adapters/__init__.py:14:    build_c919_etras_controller_adapter,
src/well_harness/adapters/__init__.py:20:    "build_landing_gear_controller_adapter",
src/well_harness/adapters/__init__.py:23:    "build_efds_controller_adapter",
src/well_harness/adapters/__init__.py:26:    "build_c919_etras_controller_adapter",
src/well_harness/adapters/c919_etras_adapter.py:72:from well_harness.controller_adapter import (
src/well_harness/adapters/c919_etras_adapter.py:94:C919_ETRAS_SOURCE_OF_TRUTH = "src/well_harness/adapters/c919_etras_adapter.py"
src/well_harness/adapters/c919_etras_adapter.py:1444:def build_c919_etras_controller_adapter() -> C919ETRASControllerAdapter:
src/well_harness/adapters/thrust_reverser_intake_packet.py:6:adapters/*_adapter.py pattern) to the intake pipeline so the docx requirement
src/well_harness/timeline_engine/executors/fantui.py:20:from well_harness.controller_adapter import build_reference_controller_adapter
src/well_harness/timeline_engine/executors/fantui.py:70:        self._controller = build_reference_controller_adapter(self._config)
src/well_harness/tools/generate_adapter.py:38:    class_name: str = _to_pythonIdentifier(system_id) + "_controller_adapter"
src/well_harness/tools/generate_adapter.py:87:    L("from well_harness.controller_adapter import (")
src/well_harness/tools/generate_adapter.py:588:_THIRD_PARTY_IMPORT_BLOCK = '''from well_harness.controller_adapter import (

exec
/bin/zsh -lc "pytest -q tests/test_workbench_column_rename.py -k 'boot or ready'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 198ms:
...........                                                              [100%]
11 passed, 26 deselected in 0.04s

exec
/bin/zsh -lc 'rg -n "innerHTML" src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc 'git diff --exit-code main..83d69e4 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
exec
/bin/zsh -lc 'rg -n "真值引擎 · Truth Engine|真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威" src/well_harness' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.js:3788:      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
src/well_harness/static/workbench.html:215:            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,889p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   842	# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
   843	
   844	scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
   845	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
   846	
   847	## Task 1: Build an isolated Notion hub and harden repo-side sync/timeouts
   848	
   849	### rollout_summary_files
   850	
   851	- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
   852	
   853	### keywords
   854	
   855	- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
   856	
   857	## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查
   858	
   859	### rollout_summary_files
   860	
   861	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   862	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
   863	
   864	### keywords
   865	
   866	- 根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查, 当前无需 Opus 审查, Gate status: Approved, tools/gsd_notion_sync.py run, NOTION_WRITEBACK_TIMEOUT_S, P7-19, P7-20, P8-05, P8-06
   867	
   868	## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts
   869	
   870	### rollout_summary_files
   871	
   872	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
   873	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
   874	
   875	### keywords
   876	
   877	- 第二套系统画像, 第二套系统接入动作板, clarification_brief, blocking_reasons, unlocks_after_completion, second-system-smoke, two_system_runtime_comparison, scenario_playback, 23/23 pass
   878	
   879	## User preferences
   880	
   881	- the user’s repeated instruction was: "根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查" -> default to uninterrupted autonomous execution when the gate is approved, and only interrupt for manual Opus review [Task 2][Task 3]
   882	- when the user asked to use Notion as the development center and avoid copying prompts, they were asking for a durable control plane, not an ad hoc note dump [Task 1]
   883	- once the control tower says `Approved` / `当前无需 Opus 审查`, do not stop for routine permission between small slices [Task 2]
   884	
   885	## Reusable knowledge
   886	
   887	- `tools/gsd_notion_sync.py run` can partially succeed even when live writeback times out; repo-doc sync may still complete, and a retry with higher `NOTION_WRITEBACK_TIMEOUT_S` can finish the Notion update [Task 1][Task 2]
   888	- The stronger QA baseline in this repo is not necessarily the most recent narrow maintenance run; the P6 recovery established that homepage/freeze text may need to prefer archived stronger evidence such as `175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass` [Task 1]
   889	- The workbench’s fingerprint board and onboarding action board both reused existing payload fields; future UI additions should prefer wiring into current payloads over new backend contracts [Task 3]

  ✓ Load sub-phase context and constitutional red-line definitions
  ✓ Inspect diff vs main and verify backend truth-engine files remain untouched
  ✓ Audit JS/HTML lockstep and guard-test scope for drift or blind spots
  → Summarize findings with verdict and file/line references
codex
CHANGES_REQUIRED

- IMPORTANT — [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:280), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3788): the Section 7 `e11_15e_chinese` guard list is incomplete. It misses at least the trust-banner truth-engine sentence `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 ...` and the JS-only `truth_engine` chip label `真值引擎 · Truth Engine`, so a future backend leak of either shipped string would still pass the red-line guard.
  Suggested fix: add anchors for both omitted shipped strings, or make the guard derive its phrase list from the same locked surface inventory used by the positive HTML/JS tests.

- IMPORTANT — [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:274), [.planning/constitution.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/constitution.md:220): the guard only scans four named files and does not traverse `src/well_harness/adapters/`, even though the constitution explicitly puts `src/well_harness/adapters/` behind the truth-engine red line. The slice itself does not touch adapters, but the test does not actually enforce the claimed boundary.
  Suggested fix: extend the guard to iterate `src/well_harness/adapters/**/*.py` (excluding `__pycache__`) in addition to the four named backend files.

- NIT — [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3795), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:4056): `installFeedbackModeAffordance()` does not call `setFeedbackMode("manual_feedback_override")`; the static HTML chip remains as-authored until some later runtime path calls `setFeedbackMode()`. The HTML and JS literals are in exact lockstep, so this is not a behavioral bug, but the boot-path description should be stated precisely.
  Suggested fix: none required in code unless you want comments/tests to describe the boot path more accurately.

The actual red line is otherwise honored: `git diff --exit-code main..83d69e4 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py` returned clean, and I found no other JS write path to `#workbench-feedback-mode strong` beyond `setFeedbackMode()`, nor any JS writes to the trust/authority headlines. The post-hydration boot-status strings are still English-only, but that is explicitly deferred in E11-15e Section 3 and remains consistent with the existing lockstep tests.

Verification run: `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py` passed `67/67`; `pytest -q tests/test_workbench_column_rename.py -k 'boot or ready'` passed `11/11`.


tokens used
114,007
CHANGES_REQUIRED

- IMPORTANT — [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:280), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3788): the Section 7 `e11_15e_chinese` guard list is incomplete. It misses at least the trust-banner truth-engine sentence `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 ...` and the JS-only `truth_engine` chip label `真值引擎 · Truth Engine`, so a future backend leak of either shipped string would still pass the red-line guard.
  Suggested fix: add anchors for both omitted shipped strings, or make the guard derive its phrase list from the same locked surface inventory used by the positive HTML/JS tests.

- IMPORTANT — [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:274), [.planning/constitution.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/constitution.md:220): the guard only scans four named files and does not traverse `src/well_harness/adapters/`, even though the constitution explicitly puts `src/well_harness/adapters/` behind the truth-engine red line. The slice itself does not touch adapters, but the test does not actually enforce the claimed boundary.
  Suggested fix: extend the guard to iterate `src/well_harness/adapters/**/*.py` (excluding `__pycache__`) in addition to the four named backend files.

- NIT — [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3795), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:4056): `installFeedbackModeAffordance()` does not call `setFeedbackMode("manual_feedback_override")`; the static HTML chip remains as-authored until some later runtime path calls `setFeedbackMode()`. The HTML and JS literals are in exact lockstep, so this is not a behavioral bug, but the boot-path description should be stated precisely.
  Suggested fix: none required in code unless you want comments/tests to describe the boot path more accurately.

The actual red line is otherwise honored: `git diff --exit-code main..83d69e4 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py` returned clean, and I found no other JS write path to `#workbench-feedback-mode strong` beyond `setFeedbackMode()`, nor any JS writes to the trust/authority headlines. The post-hydration boot-status strings are still English-only, but that is explicitly deferred in E11-15e Section 3 and remains consistent with the existing lockstep tests.

Verification run: `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py` passed `67/67`; `pytest -q tests/test_workbench_column_rename.py -k 'boot or ready'` passed `11/11`.


