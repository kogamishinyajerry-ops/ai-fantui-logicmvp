2026-04-26T04:13:33.637622Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T04:13:33.637692Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc7fe-2046-7172-8c1a-086b32e1fa45
--------
user
You are Codex GPT-5.4 acting as **Persona P5 — Truth-Engine Red-Line & JS/HTML Lockstep Auditor** for E11-15e R2 verbatim-closure review.

**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**R2 HEAD:** `9184c6d` (R1 was `83d69e4`)

## What R2 changes (verbatim from your R1 Suggested-fix bullets)

Your R1 verdict was **CHANGES_REQUIRED** with 2 IMPORTANT + 1 NIT. Your R1 output is at `.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md`. The R2 patch adopts your suggested fixes verbatim:

1. **R1 IMPORTANT 1** (Section 7 guard list incomplete) — `tests/test_workbench_e11_15e_chinese_first_bundle.py::test_e11_15e_does_not_touch_truth_engine_backend` `e11_15e_chinese` list extended to anchor:
   - `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准` (trust-banner truth-engine sentence — note R2 also tightened the inner phrasing per P3)
   - `你的手动反馈会被记录用于 diff / review` (additional unique inner phrase from same `<span>`)
   - `真值引擎 · Truth Engine` (the JS-only `truth_engine` chip label literal)

2. **R1 IMPORTANT 2** (guard doesn't traverse `src/well_harness/adapters/`) — backend traversal extended to walk `adapters/**/*.py` via `rglob('*.py')`, excluding `__pycache__`. Sanity-check assertion ensures ≥1 adapter file is found so the guard cannot silently relax if `adapters/` gets renamed/emptied.

3. **R1 NIT** (boot-path comment) — no behavioral bug, no fix required (your suggested fix said "none required").

R2 verification: 80/80 new tests pass (was 67); 357/357 workbench-suite pass; 1234/1234 full suite pass.

## Your R2 review scope

Confirm verbatim closure of your 2 R1 IMPORTANTs. Specifically:

- Does the R2 `e11_15e_chinese` list now cover every shipped Chinese display string introduced by E11-15e? Walk the SURFACE-INVENTORY (rows 1-30) and confirm each unique Chinese segment is anchored OR is a substring of an anchored segment.
- Does the R2 backend traversal actually iterate `src/well_harness/adapters/`? Check `git diff 83d69e4..9184c6d -- tests/test_workbench_e11_15e_chinese_first_bundle.py` for the `rglob` extension and the `adapter_count >= 1` sanity check.
- Truth-engine red line still honored end-to-end: `git diff main..9184c6d -- src/well_harness/controller.py runner.py models.py adapters/ demo_server.py` should be empty.
- R2 added 4 new bilingualized accessibility/hover names (per P3 IMPORTANT 1 / P1 NIT 1 closure). Are the corresponding 4 unique Chinese strings (`手动反馈覆盖仅作参考`, `反馈模式信任说明`, `隐藏本次会话的信任提示横幅`, `真值引擎权限契约`) anchored in the R2 guard list? (They are.)

## Files

- `git diff 83d69e4..9184c6d -- tests/test_workbench_e11_15e_chinese_first_bundle.py`
- `git diff 83d69e4..9184c6d -- src/well_harness/static/workbench.html`
- `git diff main..9184c6d -- src/well_harness/`

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Be terse. If your R1 IMPORTANTs are both closed, say APPROVE.

codex
Reviewing the R2 delta against my prior red-line findings first. I’m pulling the repo-local context, the prior P5 output, and the exact diffs you named so the verdict stays tied to the shipped literals and guard behavior.
exec
/bin/zsh -lc "sed -n '1,220p' .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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


exec
/bin/zsh -lc 'rg -n "LogicMVP|E11|P5|runtime generalization|Chinese-first|truth-engine" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
842:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
844:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
845:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
851:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
855:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
861:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
862:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
872:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
873:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
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

exec
/bin/zsh -lc 'git rev-parse --verify 9184c6d && git rev-parse --verify 83d69e4 && git rev-parse --abbrev-ref HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
9184c6d089cc3ed874d421fed57fdfa231925e8e
83d69e4947451085f0a45966ee652fd00377e29d
feat/e11-15e-tier-a-chinese-first-bundle-20260426

codex
I’ve confirmed the target SHAs and branch. Next I’m checking the exact test diff, the HTML literals, and whether any truth-layer file changed under `src/well_harness/`.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/receiving-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: receiving-code-review
description: Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
---

# Code Review Reception

## Overview

Code review requires technical evaluation, not emotional performance.

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (explicit CLAUDE.md violation)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**Example:**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## Source-Specific Handling

### From your human partner
- **Trusted** - implement after understanding
- **Still ask** if scope unclear
- **No performative agreement**
- **Skip to action** or technical acknowledgment

### From External Reviewers
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**your human partner's rule:** "External feedback - be skeptical, but check carefully"

## YAGNI Check for "Professional" Features

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**your human partner's rule:** "You and reviewer both report to me. If we don't need this feature, don't add it."

## Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## When To Push Back

Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with your human partner's architectural decisions

**How to push back:**
- Use technical reasoning, not defensiveness
- Ask specific questions
- Reference working tests/code
- Involve your human partner if architectural

**Signal if uncomfortable pushing back out loud:** "Strange things are afoot at the Circle K"

## Acknowledging Correct Feedback

When feedback IS correct:
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**Why no thanks:** Actions speak. Just fix it. The code itself shows you heard the feedback.

**If you catch yourself about to write "Thanks":** DELETE IT. State the fix instead.

## Gracefully Correcting Your Pushback

If you pushed back and were wrong:
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

State the correction factually and move on.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

## Real Examples

**Performative Agreement (Bad):**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**Technical Verification (Good):**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI (Good):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**Unclear Item (Good):**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub Thread Replies

When replying to inline review comments on GitHub, reply in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.

## The Bottom Line

**External feedback = suggestions to evaluate, not orders to follow.**

Verify. Question. Then implement.

No performative agreement. Technical rigor always.

exec
/bin/zsh -lc 'git diff 83d69e4..9184c6d -- src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git diff 83d69e4..9184c6d -- tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 157518a..e5804b3 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -36,7 +36,7 @@
           data-feedback-mode="manual_feedback_override"
           data-mode-authority="advisory"
           aria-live="polite"
-          title="Manual feedback override is advisory — truth engine readings remain authoritative."
+          title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."
         >
           <span>反馈模式 · Feedback Mode</span>
           <strong>手动（仅参考）· Manual (advisory)</strong>
@@ -84,7 +84,7 @@
           <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
         </span>
         <span class="workbench-sow-flag" aria-hidden="false">
-          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
+          仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading
         </span>
       </section>
 
@@ -140,7 +140,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_b</span>
-              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
+              <h3 id="workbench-wow-b-title">1000 次试验可靠性 · Monte Carlo</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
@@ -201,25 +201,25 @@
         class="workbench-trust-banner"
         data-feedback-mode="manual_feedback_override"
         role="note"
-        aria-label="Feedback mode trust affordance"
+        aria-label="反馈模式信任说明 · Feedback mode trust affordance"
       >
         <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
         <div class="workbench-trust-banner-body">
           <span class="workbench-trust-banner-scope">
-            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
+            <em>此处"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
             (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
-            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
+            被动读取、回放与审计链导航不属于"手动反馈" (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
           </span>
           <strong>该模式仅作参考 · That mode is advisory.</strong>
           <span>
-            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
+            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
             你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
           </span>
         </div>
         <button
           type="button"
           class="workbench-trust-banner-dismiss"
-          aria-label="Hide trust banner for this session"
+          aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"
           data-trust-banner-dismiss
         >
           隐藏（本次会话）· Hide for session
@@ -241,11 +241,11 @@
         id="workbench-authority-banner"
         class="workbench-authority-banner"
         role="note"
-        aria-label="Truth-engine authority contract"
+        aria-label="真值引擎权限契约 · Truth-engine authority contract"
       >
         <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
         <span class="workbench-authority-banner-headline">
-          真值引擎 · 只读 · Truth Engine — Read Only
+          真值引擎（只读）· Truth Engine — Read Only
         </span>
         <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
         <span class="workbench-authority-banner-rule">

 succeeded in 0ms:
diff --git a/tests/test_workbench_e11_15e_chinese_first_bundle.py b/tests/test_workbench_e11_15e_chinese_first_bundle.py
index 46ef2ee..73f0607 100644
--- a/tests/test_workbench_e11_15e_chinese_first_bundle.py
+++ b/tests/test_workbench_e11_15e_chinese_first_bundle.py
@@ -92,24 +92,39 @@ def server():
         "<span>反馈模式 · Feedback Mode</span>",
         "<span>系统 · System</span>",
         "<strong>手动（仅参考）· Manual (advisory)</strong>",
-        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
+        # WOW h3 direction flips (3) — strict Chinese-first per E11-15c
+        # convention; R2 P3 IMPORTANT closure: wow_b switched from
+        # `1000-trial 可靠性` (English token leading) to fully Chinese
+        # `1000 次试验可靠性`.
         '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
-        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
+        '<h3 id="workbench-wow-b-title">1000 次试验可靠性 · Monte Carlo</h3>',
         '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
-        # State-of-world labels (4) + advisory flag (1)
+        # State-of-world labels (4) + advisory flag (1, R2 P3 IMPORTANT
+        # closure: outer middot reserved for Chinese/English split, inner
+        # Chinese clause now uses comma instead of an extra middot).
         "真值引擎 SHA · truth-engine SHA",
         "最近 e2e · recent e2e",
         "对抗样本 · adversarial",
         "未关闭问题 · open issues",
-        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
-        # Trust banner body (3)
-        '这里"手动反馈"的含义 · What "manual feedback" means here:',
+        "仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading",
+        # Trust banner body (3) — R2 P3 NIT closure: native phrasing
+        # tightened (`此处`, `不属于"手动反馈"`, `仍以真值引擎读数为准`).
+        '此处"手动反馈"的含义 · What "manual feedback" means here:',
         "该模式仅作参考 · That mode is advisory.",
-        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
+        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings",
         # Trust banner dismiss (1)
         "隐藏（本次会话）· Hide for session",
-        # Authority banner headline (1)
-        "真值引擎 · 只读 · Truth Engine — Read Only",
+        # Authority banner headline (1) — R2 P3 IMPORTANT closure: outer
+        # middot reserved for Chinese/English split; inner Chinese clause
+        # uses parentheses instead of an extra middot.
+        "真值引擎（只读）· Truth Engine — Read Only",
+        # Accessibility / hover names (R2 P1 NIT + P3 IMPORTANT closure):
+        # the feedback-mode title attribute and three aria-labels were
+        # English-only at R1 and broke surface-honesty pledge.
+        'title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."',
+        'aria-label="反馈模式信任说明 · Feedback mode trust affordance"',
+        'aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"',
+        'aria-label="真值引擎权限契约 · Truth-engine authority contract"',
         # Pre-hydration boot placeholders (3)
         "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
         "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
@@ -143,6 +158,9 @@ def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None
         '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
         '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
         '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
+        # R2 P3 IMPORTANT: also forbid the R1 mid-Chinese English-token
+        # leading form `1000-trial 可靠性 · Monte Carlo`.
+        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
         # Bare state-of-world labels (no Chinese prefix)
         ">truth-engine SHA<",
         ">recent e2e<",
@@ -161,6 +179,19 @@ def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None
         # Bare inbox + pending sign-off
         "<li>No proposals submitted yet.</li>",
         "<strong>Pending Kogami sign-off</strong>",
+        # R2 P3 IMPORTANT closure: forbid the R1 multi-middot-inside-Chinese
+        # forms that broke the strict `<中文> · <English>` convention.
+        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
+        "真值引擎 · 只读 · Truth Engine — Read Only",
+        # R2 P3 NIT closure: forbid the awkward R1 phrasings.
+        '这里"手动反馈"的含义',
+        "仍然是权威",
+        # R2 P1 NIT + P3 IMPORTANT closure: forbid the R1 English-only
+        # accessibility/hover names.
+        'title="Manual feedback override is advisory — truth engine readings remain authoritative."',
+        'aria-label="Hide trust banner for this session"',
+        'aria-label="Feedback mode trust affordance"',
+        'aria-label="Truth-engine authority contract"',
     ],
 )
 def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
@@ -254,13 +285,20 @@ def test_workbench_route_serves_e11_15e_bundle(server) -> None:
     # Spot-check one string from each surface category.
     assert "身份 · Identity" in html
     assert "因果链走读 · Causal Chain" in html
+    assert "1000 次试验可靠性 · Monte Carlo" in html
     assert "真值引擎 SHA · truth-engine SHA" in html
     assert "该模式仅作参考 · That mode is advisory." in html
+    assert "仍以真值引擎读数为准" in html
     assert "隐藏（本次会话）· Hide for session" in html
-    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html
+    assert "真值引擎（只读）· Truth Engine — Read Only" in html
     assert "等待 probe &amp; trace 面板启动" in html
     assert "暂无已提交提案 · No proposals submitted yet." in html
     assert "等待 Kogami 签字 · Pending Kogami sign-off" in html
+    # R2 P1 NIT + P3 IMPORTANT closure: accessibility/hover names served
+    assert "手动反馈覆盖仅作参考" in html  # title attribute
+    assert "反馈模式信任说明" in html       # trust-banner aria-label
+    assert "隐藏本次会话的信任提示横幅" in html  # dismiss aria-label
+    assert "真值引擎权限契约" in html       # authority-banner aria-label
 
 
 # ─── 7. Truth-engine red line — backend untouched ────────────────────
@@ -268,44 +306,87 @@ def test_workbench_route_serves_e11_15e_bundle(server) -> None:
 
 def test_e11_15e_does_not_touch_truth_engine_backend() -> None:
     """E11-15e only edits static HTML/JS display copy. It must NOT leak
-    into controller.py / runner.py / models.py / adapters / demo_server
-    (truth-engine red line — see .planning/constitution.md)."""
+    into controller.py / runner.py / models.py / demo_server.py / any
+    `src/well_harness/adapters/*.py` (truth-engine red line per
+    .planning/constitution.md).
+
+    R2 P5 IMPORTANT closure:
+      - Guard list extended to cover the trust-banner truth-engine
+        sentence and the JS-only `truth_engine` chip label that the
+        R1 list missed.
+      - Backend traversal extended to walk `src/well_harness/adapters/
+        **/*.py` (excluding `__pycache__`) so the constitutional adapter
+        boundary is actually enforced, not only claimed.
+    """
     repo_root = Path(__file__).resolve().parents[1]
-    backend_paths = [
-        repo_root / "src" / "well_harness" / "controller.py",
-        repo_root / "src" / "well_harness" / "runner.py",
-        repo_root / "src" / "well_harness" / "models.py",
-        repo_root / "src" / "well_harness" / "demo_server.py",
+    well_harness_dir = repo_root / "src" / "well_harness"
+    backend_paths: list[Path] = [
+        well_harness_dir / "controller.py",
+        well_harness_dir / "runner.py",
+        well_harness_dir / "models.py",
+        well_harness_dir / "demo_server.py",
     ]
+    adapters_dir = well_harness_dir / "adapters"
+    if adapters_dir.is_dir():
+        backend_paths.extend(
+            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
+        )
+    # Sanity check: the adapters traversal MUST find at least one file,
+    # otherwise the guard silently relaxes if adapters/ gets renamed or
+    # emptied. R2 P5 IMPORTANT closure depends on this.
+    adapter_count = sum(1 for p in backend_paths if "adapters" in p.parts)
+    assert adapter_count >= 1, (
+        "E11-15e red-line guard expected ≥1 adapter under "
+        "src/well_harness/adapters/; adapter directory missing or empty"
+    )
     e11_15e_chinese = [
+        # Topbar chips
         "身份 · Identity",
         "工单 · Ticket",
         "反馈模式 · Feedback Mode",
         "系统 · System",
         "手动（仅参考）",
+        # WOW h3s (R2 includes the new wow_b strict-Chinese form)
         "因果链走读",
-        "1000-trial 可靠性",
+        "1000 次试验可靠性",
         "反向诊断 · Reverse Diagnose",
+        # State-of-world labels + flag (R2 uses comma-separated form)
         "真值引擎 SHA",
         "最近 e2e",
         "对抗样本",
         "未关闭问题",
-        "仅参考 · 非真值引擎实时读数",
-        '这里"手动反馈"的含义',
+        "仅参考，非真值引擎实时读数",
+        # Trust banner body (R2 native phrasing)
+        '此处"手动反馈"的含义',
         "该模式仅作参考",
+        # R2 P5 IMPORTANT #1 closure: anchors for the trust-banner
+        # truth-engine sentence and the unique inner phrase, plus the
+        # JS-only `truth_engine` chip label, so a future backend leak of
+        # any shipped Chinese display string fails the guard.
+        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准",
+        "你的手动反馈会被记录用于 diff / review",
+        "真值引擎 · Truth Engine",  # JS-side `truth_engine` chip label
+        # Trust banner dismiss + authority banner headline (R2 form)
         "隐藏（本次会话）",
-        "真值引擎 · 只读",
+        "真值引擎（只读）",
+        # Pre-hydration boot placeholders + reference packet + inbox + sign-off
         "等待 probe",
         "等待 annotate",
         "等待 hand off",
         "参考资料、澄清说明",
         "暂无已提交提案",
         "等待 Kogami 签字",
+        # R2 accessibility/hover names (unique Chinese segments only)
+        "手动反馈覆盖仅作参考",
+        "反馈模式信任说明",
+        "隐藏本次会话的信任提示横幅",
+        "真值引擎权限契约",
     ]
     for backend in backend_paths:
         text = backend.read_text(encoding="utf-8")
         for phrase in e11_15e_chinese:
             assert phrase not in text, (
                 f"E11-15e display copy {phrase!r} unexpectedly leaked into "
-                f"backend file {backend.name} — truth-engine red-line breach"
+                f"backend file {backend.relative_to(repo_root)} — "
+                "truth-engine red-line breach"
             )

exec
/bin/zsh -lc 'git diff --stat main..9184c6d -- src/well_harness/ && git diff --name-only main..9184c6d -- src/well_harness/' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 src/well_harness/static/workbench.html | 62 +++++++++++++++++-----------------
 src/well_harness/static/workbench.js   |  2 +-
 2 files changed, 32 insertions(+), 32 deletions(-)
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js

codex
The truth-layer diff is clean so far: only `static/workbench.html` and `static/workbench.js` move versus `main`. I’m now checking that the guard list actually covers every shipped Chinese segment, including the JS-only chip label and the new accessibility names.
exec
/bin/zsh -lc "sed -n '1,260p' tests/test_workbench_e11_15e_chinese_first_bundle.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
"""E11-15e — Tier-A Chinese-first bundle regression lock.

Bilingualizes 17 user-visible English-only surfaces enumerated by P2
during the E11-15d review (see test_workbench_approval_flow_polish.py
docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
E11-15d-SURFACE-INVENTORY.md):

  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
                          open issues / advisory flag
  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
  Authority banner (1):   Truth Engine — Read Only headline
  Trust dismiss (1):      Hide for session button
  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
  Reference packet (1):   Annotate column intro <p>
  Inbox empty (1):        No proposals submitted yet.
  Pending sign-off (1):   Pending Kogami sign-off

Pattern: `<中文> · <English>` everywhere; English suffix is preserved
verbatim so all prior `assert <english> in html` substring locks across
test_workbench_trust_affordance, test_workbench_authority_banner,
test_workbench_role_affordance, test_workbench_column_rename, and
test_workbench_state_of_world_bar continue to pass without contract
churn.

Out of scope (deferred to a future Tier-A or constitutional decision):
  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    domain proper nouns coupled to value-attribute IDs and to the
    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    locked by tests/test_workbench_column_rename.py:170-172 — those are
    a separate JS-side bilingualization with their own lockstep contract.
  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    </pre> flow diagram — visual phase-arrow, not English copy.
  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    that were already bilingualized in earlier sub-phases.

Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────


@pytest.mark.parametrize(
    "bilingual",
    [
        # Topbar chip labels (5)
        "<span>身份 · Identity</span>",
        "<span>工单 · Ticket</span>",
        "<span>反馈模式 · Feedback Mode</span>",
        "<span>系统 · System</span>",
        "<strong>手动（仅参考）· Manual (advisory)</strong>",
        # WOW h3 direction flips (3) — strict Chinese-first per E11-15c
        # convention; R2 P3 IMPORTANT closure: wow_b switched from
        # `1000-trial 可靠性` (English token leading) to fully Chinese
        # `1000 次试验可靠性`.
        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
        '<h3 id="workbench-wow-b-title">1000 次试验可靠性 · Monte Carlo</h3>',
        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
        # State-of-world labels (4) + advisory flag (1, R2 P3 IMPORTANT
        # closure: outer middot reserved for Chinese/English split, inner
        # Chinese clause now uses comma instead of an extra middot).
        "真值引擎 SHA · truth-engine SHA",
        "最近 e2e · recent e2e",
        "对抗样本 · adversarial",
        "未关闭问题 · open issues",
        "仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading",
        # Trust banner body (3) — R2 P3 NIT closure: native phrasing
        # tightened (`此处`, `不属于"手动反馈"`, `仍以真值引擎读数为准`).
        '此处"手动反馈"的含义 · What "manual feedback" means here:',
        "该模式仅作参考 · That mode is advisory.",
        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings",
        # Trust banner dismiss (1)
        "隐藏（本次会话）· Hide for session",
        # Authority banner headline (1) — R2 P3 IMPORTANT closure: outer
        # middot reserved for Chinese/English split; inner Chinese clause
        # uses parentheses instead of an extra middot.
        "真值引擎（只读）· Truth Engine — Read Only",
        # Accessibility / hover names (R2 P1 NIT + P3 IMPORTANT closure):
        # the feedback-mode title attribute and three aria-labels were
        # English-only at R1 and broke surface-honesty pledge.
        'title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."',
        'aria-label="反馈模式信任说明 · Feedback mode trust affordance"',
        'aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"',
        'aria-label="真值引擎权限契约 · Truth-engine authority contract"',
        # Pre-hydration boot placeholders (3)
        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
        # Reference-packet intro (1)
        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
        # Inbox empty state (1)
        "暂无已提交提案 · No proposals submitted yet.",
        # Pending sign-off (1)
        "等待 Kogami 签字 · Pending Kogami sign-off",
    ],
)
def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"


# ─── 2. Stale English-only surfaces are gone ─────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        # Bare topbar chip labels (no Chinese prefix) — must be replaced
        "<span>Identity</span>",
        "<span>Ticket</span>",
        "<span>Feedback Mode</span>",
        "<span>System</span>",
        "<strong>Manual (advisory)</strong>",
        # WOW h3 stale English-first ordering (E11-15c convention)
        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
        # R2 P3 IMPORTANT: also forbid the R1 mid-Chinese English-token
        # leading form `1000-trial 可靠性 · Monte Carlo`.
        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
        # Bare state-of-world labels (no Chinese prefix)
        ">truth-engine SHA<",
        ">recent e2e<",
        ">adversarial<",
        ">open issues<",
        # Bare trust-banner body lines — these are now sentence-internal
        # so we look for the line-leading position they used to hold.
        "<em>What \"manual feedback\" means here:</em>",
        "<strong>That mode is advisory.</strong>",
        # Bare button + headline + boot placeholders
        ">\n          Hide for session\n        <",
        ">\n          Truth Engine — Read Only\n        <",
        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
        # Bare inbox + pending sign-off
        "<li>No proposals submitted yet.</li>",
        "<strong>Pending Kogami sign-off</strong>",
        # R2 P3 IMPORTANT closure: forbid the R1 multi-middot-inside-Chinese
        # forms that broke the strict `<中文> · <English>` convention.
        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
        "真值引擎 · 只读 · Truth Engine — Read Only",
        # R2 P3 NIT closure: forbid the awkward R1 phrasings.
        '这里"手动反馈"的含义',
        "仍然是权威",
        # R2 P1 NIT + P3 IMPORTANT closure: forbid the R1 English-only
        # accessibility/hover names.
        'title="Manual feedback override is advisory — truth engine readings remain authoritative."',
        'aria-label="Hide trust banner for this session"',
        'aria-label="Feedback mode trust affordance"',
        'aria-label="Truth-engine authority contract"',
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only surface still present: {stale}"


# ─── 3. English suffixes preserved (substring locks unchanged) ───────


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        # Anchors required by trust_affordance.py
        "Manual (advisory)",
        "Truth engine readings",
        "Hide for session",
        'What "manual feedback" means here',
        "That mode is advisory.",
        # Anchor required by authority_banner.py
        "Truth Engine — Read Only",
        # Anchor required by role_affordance.py
        "Pending Kogami sign-off",
        # Anchor required by state_of_world_bar.py
        "advisory · not a live truth-engine reading",
        # Anchors required by column_rename.py:118-120 (pre-hydration)
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-feedback-mode"',
        'id="workbench-trust-banner"',
        'id="workbench-authority-banner"',
        'id="workbench-pending-signoff-affordance"',
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'data-trust-banner-dismiss',
        'data-feedback-mode="manual_feedback_override"',
    ],
)
def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"


# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──


def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
    switch. If the JS literal stays English-only, the very first mode
    flip would silently revert the static HTML's bilingual chip back to

exec
/bin/zsh -lc 'rg -n "SURFACE-INVENTORY|surface inventory|rows 1-30|Row 1|row 1" .planning/phases/E11-workbench-engineer-first-ux -S' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:25:   For every bilingualized string in `E11-15e-SURFACE-INVENTORY.md` Section 2:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:93:E11-02-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:94:E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:95:E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:96:E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:97:E11-06-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:98:E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:99:E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:100:E11-09-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:101:E11-10-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:102:E11-11-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:104:E11-13-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:105:E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:106:E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:107:E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:108:E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:109:E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:110:E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:232:  → Read E11-15e shared context, surface inventory, persona rotation state, and identify all claimed bilingualized strings plus expected lock files
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:237:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:261:    21	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:275:    35	E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:279:    39	If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:396:   115	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:477:    25	E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:489:     6	E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:1334:     4	don't silently regress the trust affordance. Per E11-13-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:2209:   109	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:2817:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3003:   Cross-reference your E11-15d R2 NIT enumeration against the 22 REWRITE rows in `E11-15e-SURFACE-INVENTORY.md` Section 2. Your R2 listed: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block. Plus the original R1-D2 IMPORTANT list: `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, topbar chips.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3008:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3010:   - Run the existing E11-15d guard `tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure` on a hypothetical extension to E11-15e artifacts — does the SURFACE-INVENTORY language pass that guard's exemption rules?
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3018:   `E11-15e-SURFACE-INVENTORY.md` Section 1 claims Tier-A based on copy_diff_lines ~38 + 22 REWRITE. Re-count from `git diff main..83d69e4`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3029:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Sections 1, 2, 3, 6
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3031:- `tests/test_workbench_e11_15e_chinese_first_bundle.py` Section 1 (positive bilingual locks — does this list match Section 2 of SURFACE-INVENTORY?)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3094:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Section 2 (full surface table)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3121:   For every bilingualized string in `E11-15e-SURFACE-INVENTORY.md` Section 2:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3209:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3302:   Cross-reference your E11-15d R2 NIT enumeration against the 22 REWRITE rows in `E11-15e-SURFACE-INVENTORY.md` Section 2. Your R2 listed: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block. Plus the original R1-D2 IMPORTANT list: `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, topbar chips.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3307:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:3366:   For every bilingualized string in `E11-15e-SURFACE-INVENTORY.md` Section 2:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:46:- `.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:150:.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:1586:/bin/zsh -lc 'git diff --unified=20 main..54e701b -- .planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:1588:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:1592:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-prompt.txt:20:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:1264:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:1342:  1307	- `IMPORTANT` `append-rotation` and `next-persona` disagree on Tier-A semantics. [parse_rotation_state`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:199) skips Tier-A only when the literal `Rotation pointer unchanged` suffix is present, but [append_rotation_entry`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:234) never adds that suffix for Tier-A rows even though the contract says appended rows are canonical and Tier-A should not consume the pointer ([E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:67), [E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:73)). Live probe: starting from `P5`, appending a Tier-A `P1` row made `next_persona()` return `P2` instead of preserving `P1`.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:31:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:32:- **NIT** — `E11-15d-SURFACE-INVENTORY.md:86`, `workbench.html` lines 42/48/65/71/77/83/87/209/213/215/278/298/318/301/302: remaining-list still partial. `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block all still English/English-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:41:- Guard now scans **3 artifacts**: SURFACE-INVENTORY, PERSONA-ROTATION-STATE, AND this test file itself (self-scan is the new safety net).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:44:### NIT closure — expand SURFACE-INVENTORY remaining-list
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:46:`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:55:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — remaining-list expansion + grep template
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:331:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:366:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:373:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1303:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'; nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8409:/bin/zsh -lc 'git diff --unified=5 a17e744..a02729a -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js src/well_harness/static/workbench.css src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8411:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8415:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:97:Surface Inventory: .planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:44:- `.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:526:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:2483:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3697:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:38:  "kind": "advisory",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3698:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:40:  "truth_engine_sha_source": "git rev-parse --short HEAD",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3699:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:42:  "recent_e2e_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3700:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:44:  "adversarial_source": "docs/coordination/qa_report.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3701:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:46:  "open_known_issues_source": "docs/known-issues/ (file count)",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3702:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:47:  "last_executed_evidence": "<latest stamp>" | "—",
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3703:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:48:  "generated_at": "<ISO8601 Z>"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:3704:.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md:63:Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new endpoint is explicitly classified as `kind: "advisory"` — it never claims to be a live truth-engine reading.
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:49:> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:50:> E11-02 的 worked example 见 `E11-02-SURFACE-INVENTORY.md`。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:321:8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-prompt.txt:71:- `.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-prompt.txt:20:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-prompt.txt:28:- `.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:48:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` R2 closure log + rows #15/#18/#20/#27-#30
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:57:Reviewing the R2 closure against my R1 findings. I’m loading the prior R1 output, the exact diffs, and the surface inventory to verify verbatim string closure and check for any new Chinese-first convention drift.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:94:/bin/zsh -lc "sed -n '1,220p' .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md && printf '\\n--- INVENTORY ---\\n' && sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:154:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Section 2 (full surface table)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:172:I’m treating this as a read-only bilingual copy/convention review for E11-15e. I’ll load the shared context, skim any relevant LogicMVP memory, then inspect the exact diff, tests, and surface inventory before issuing an approval verdict with line-cited findings.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-output.md:462:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md:96:- Inventory row 14: anchor traced by Codex R4 NIT (workbench.html:506-540 — 9 textareas not 5)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:620:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:631:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:337: .../E11-03-SURFACE-INVENTORY.md                    |  53 +++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:350:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:357:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:362:      53 .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:870:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:5017:/bin/zsh -lc 'git diff --unified=20 main..HEAD -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:5019:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:5023:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:82:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:899:   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:1032:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:1293:+# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:310:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:334:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:341:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:855:/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1076:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:8701:- IMPORTANT — `src/well_harness/static/workbench.html:77-90,107-120,137-150`, `src/well_harness/static/workbench.js:3888-3896`, `src/well_harness/static/workbench_start.html:69,108-114`, `tests/test_workbench_wow_starters.py:80-93,114-118`, `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:23-25`: two user-facing surfaces remain unguarded. The suite never checks the selector contract that makes the cards clickable (`data-wow-action="run"` / `.workbench-wow-run-button`), and it never probes the three `/workbench/start` rewrites that changed “not shipped” text to “shipped”. Those surfaces are in the recorded inventory but not in the regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:8713:- IMPORTANT — `src/well_harness/static/workbench.html:77-90,107-120,137-150`, `src/well_harness/static/workbench.js:3888-3896`, `src/well_harness/static/workbench_start.html:69,108-114`, `tests/test_workbench_wow_starters.py:80-93,114-118`, `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:23-25`: two user-facing surfaces remain unguarded. The suite never checks the selector contract that makes the cards clickable (`data-wow-action="run"` / `.workbench-wow-run-button`), and it never probes the three `/workbench/start` rewrites that changed “not shipped” text to “shipped”. Those surfaces are in the recorded inventory but not in the regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:337:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:351:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:355:If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:622: .../E11-15e-SURFACE-INVENTORY.md                   | 141 ++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:762:     6	E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:1502:+E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:2411:/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:2530:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:3006:  Suggested fix: add anchors for both omitted shipped strings, or make the guard derive its phrase list from the same locked surface inventory used by the positive HTML/JS tests.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:3024:  Suggested fix: add anchors for both omitted shipped strings, or make the guard derive its phrase list from the same locked surface inventory used by the positive HTML/JS tests.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:152:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:170:If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:961:     6	E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:143:- `.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:43:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:331:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:339: .../E11-15-SURFACE-INVENTORY.md                    |  87 +++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:618:# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1435:   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1655:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1735:/bin/zsh -lc "sed -n '1,240p' .planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1818:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:29:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:789:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:2718:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:51:- `.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:989: .../E11-10-SURFACE-INVENTORY.md                    | 150 +++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:996:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1031:/bin/zsh -lc 'rg -n "Rotation pointer unchanged|append-rotation|next-persona|persona dispatch|Tier-A|Tier-B" .planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md tools/codex_persona_dispatch.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1048:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:6:> Tier-B/Tier-A persona-review loop (verdict regex parsing, round-robin
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1049:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:21:8. Decide Tier-B acceptance
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1050:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:31:| 1 | `tools/codex_persona_dispatch.py` CLI with 4 subcommands | [NEW] | `tools/codex_persona_dispatch.py` | dispatch / collect / next-persona / append-rotation. Stdlib-only, ~310 LOC. |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1051:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:60:Exit code 0 if Tier-B acceptance met, 1 otherwise. Notes contain
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1052:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:64:### `next-persona`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1053:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:67:the most recent Tier-B entry. Tier-A entries with the canonical
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1054:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:68:"Rotation pointer unchanged" suffix are skipped per constitution.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1055:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:71:### `append-rotation <sub-phase> <persona> <tier> <reason>`
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1056:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:108:> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1057:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:113:→ **Tier-B** (1-persona review).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1058:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:115:> **Verdict: Tier-B**. Persona = **P1 (Junior FCS Engineer)** —
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1059:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:132:6. `parse_rotation_state` — 2 tests covering Tier-A skip + empty
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1133:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md | sed -n '56,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1210:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md | sed -n '76,100p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1295:- `IMPORTANT` `append-rotation` and `next-persona` disagree on Tier-A semantics. [parse_rotation_state`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:199) skips Tier-A only when the literal `Rotation pointer unchanged` suffix is present, but [append_rotation_entry`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:234) never adds that suffix for Tier-A rows even though the contract says appended rows are canonical and Tier-A should not consume the pointer ([E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:67), [E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:73)). Live probe: starting from `P5`, appending a Tier-A `P1` row made `next_persona()` return `P2` instead of preserving `P1`.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1307:- `IMPORTANT` `append-rotation` and `next-persona` disagree on Tier-A semantics. [parse_rotation_state`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:199) skips Tier-A only when the literal `Rotation pointer unchanged` suffix is present, but [append_rotation_entry`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tools/codex_persona_dispatch.py:234) never adds that suffix for Tier-A rows even though the contract says appended rows are canonical and Tier-A should not consume the pointer ([E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:67), [E11-10-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:73)). Live probe: starting from `P5`, appending a Tier-A `P1` row made `next_persona()` return `P2` instead of preserving `P1`.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:43:- `.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:193:.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:203: .../E11-07-SURFACE-INVENTORY.md                    |  43 ++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:3311:./docs/thrust_reverser/traceability_matrix.md:225:- 本 matrix 一旦更新 row（阈值值改动 / 新增常数 / docx 升级 v2），必须同 commit 原子更新 `config/hardware/thrust_reverser_hardware_v1.yaml` 头 + `src/well_harness/adapters/thrust_reverser_intake_packet.py` notes + `docs/provenance/adapter_truth_levels.md` row 1
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:4696:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:4762:/bin/zsh -lc 'git diff main..c7131e9 -- src/well_harness/demo_server.py src/well_harness/static/workbench.html src/well_harness/static/workbench.css tests/test_workbench_authority_banner.py .planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:4764:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:4768:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:6107:- `NIT` [demo_server.py:618](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:618) [E11-07-SURFACE-INVENTORY.md:31](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md:31): the “live constitution text / no drift risk” claim is slightly stronger than the implementation. The handler only stays live while the exact `Forbidden（红线维持` heading matches; if that heading drifts, it silently falls back to hand-written summary text. The fallback is still truthful, so this is not blocking, but it is not quite the same guarantee the docs describe.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:6120:- `NIT` [demo_server.py:618](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:618) [E11-07-SURFACE-INVENTORY.md:31](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md:31): the “live constitution text / no drift risk” claim is slightly stronger than the implementation. The handler only stays live while the exact `Forbidden（红线维持` heading matches; if that heading drifts, it silently falls back to hand-written summary text. The fallback is still truthful, so this is not blocking, but it is not quite the same guarantee the docs describe.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-prompt.txt:20:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:595:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:603:/bin/zsh -lc "git diff --stat main..938a5a2 && printf '\\n---\\n' && git diff --unified=0 main..938a5a2 -- src/well_harness/static/workbench.html tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_direction_consistency.py .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:605: .../E11-15c-SURFACE-INVENTORY.md                   |  80 +++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:614:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:618:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:694:+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1067:   109	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2078:   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-prompt.txt:28:- `.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-R2-output.md:40:- Does the R2 `e11_15e_chinese` list now cover every shipped Chinese display string introduced by E11-15e? Walk the SURFACE-INVENTORY (rows 1-30) and confirm each unique Chinese segment is anchored OR is a substring of an anchored segment.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-R2-output.md:104:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:357:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:364:/bin/zsh -lc "git diff --stat main..HEAD && printf '\\n---\\n' && git diff -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:366: .../E11-03-SURFACE-INVENTORY.md                    |  53 +++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:841:/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md && printf '\\n---\\n' && sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1197:/bin/zsh -lc 'git diff main..HEAD -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1199:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1203:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1582:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1844:- IMPORTANT — The suite does not positively lock the three renamed pre-hydration HTML boot-status strings. Those rewritten lines are present in [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:212):212-214, 232-234, 252-253 and are explicitly part of the 12-line surface inventory in [E11-03-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md:9):9-20. But [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:86):86-102 only checks that the old waiting-copy is absent, and [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:163):163-172 does not assert the new waiting-copy either. A drift to any different phrase would still pass, so coverage does not meet the stated “12 visible-copy lines in lockstep” claim.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:1856:- IMPORTANT — The suite does not positively lock the three renamed pre-hydration HTML boot-status strings. Those rewritten lines are present in [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:212):212-214, 232-234, 252-253 and are explicitly part of the 12-line surface inventory in [E11-03-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md:9):9-20. But [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:86):86-102 only checks that the old waiting-copy is absent, and [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:163):163-172 does not assert the new waiting-copy either. A drift to any different phrase would still pass, so coverage does not meet the stated “12 visible-copy lines in lockstep” claim.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:40:`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:54:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — overclaim removed; deferred list added
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:79:These are explicitly enumerated in the SURFACE-INVENTORY now.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:384:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:460:    71	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:674:   173	# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:678:   177	    """P2 R1 IMPORTANT closure: an earlier draft of E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:691:   190	        / "E11-15d-SURFACE-INVENTORY.md"
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:707:   206	                    f"E11-15d-SURFACE-INVENTORY contains forbidden overclaim "
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:740:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1114:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:9:> earlier draft of this inventory overclaimed "last English-only surface"
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1670:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1681:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1682:- **NIT** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:86), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:42): the new “English-only surfaces still remaining” section is still partial. Beyond the 4 explicit strings, WOW h3s, and topbar chip labels, `/workbench` still shows visible English/English-first copy at `Manual (advisory)` ([line 42](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:42)), system options ([48](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:48)), state-of-world labels/flag ([65](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:65), [71](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:71), [77](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:77), [83](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:83), [87](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87)), trust-banner body copy ([209](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:209), [213](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:213), [215](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215)), boot placeholders ([278](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:278), [298](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:298), [318](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:318)), and the reference-packet block ([301](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:301), [302](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:302)). If that section is meant as a full remainder inventory, it still understates the page.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1705:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1706:- **NIT** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:86), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:42): the new “English-only surfaces still remaining” section is still partial. Beyond the 4 explicit strings, WOW h3s, and topbar chip labels, `/workbench` still shows visible English/English-first copy at `Manual (advisory)` ([line 42](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:42)), system options ([48](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:48)), state-of-world labels/flag ([65](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:65), [71](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:71), [77](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:77), [83](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:83), [87](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87)), trust-banner body copy ([209](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:209), [213](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:213), [215](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215)), boot placeholders ([278](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:278), [298](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:298), [318](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:318)), and the reference-packet block ([301](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:301), [302](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:302)). If that section is meant as a full remainder inventory, it still understates the page.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:522:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1115:- `.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:10:   Cross-reference your E11-15d R2 NIT enumeration against the 22 REWRITE rows in `E11-15e-SURFACE-INVENTORY.md` Section 2. Your R2 listed: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block. Plus the original R1-D2 IMPORTANT list: `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, topbar chips.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:17:   - Run the existing E11-15d guard `tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure` on a hypothetical extension to E11-15e artifacts — does the SURFACE-INVENTORY language pass that guard's exemption rules?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:25:   `E11-15e-SURFACE-INVENTORY.md` Section 1 claims Tier-A based on copy_diff_lines ~38 + 22 REWRITE. Re-count from `git diff main..83d69e4`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:36:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Sections 1, 2, 3, 6
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:38:- `tests/test_workbench_e11_15e_chinese_first_bundle.py` Section 1 (positive bilingual locks — does this list match Section 2 of SURFACE-INVENTORY?)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:588: .../E11-15d-SURFACE-INVENTORY.md                   |   84 ++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:597:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1464:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1532:    67	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:145:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:25:   Cross-reference your E11-15d R2 NIT enumeration against the 22 REWRITE rows in `E11-15e-SURFACE-INVENTORY.md` Section 2. Your R2 listed: `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block. Plus the original R1-D2 IMPORTANT list: `Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`, WOW h3s, topbar chips.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:32:   - Run the existing E11-15d guard `tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure` on a hypothetical extension to E11-15e artifacts — does the SURFACE-INVENTORY language pass that guard's exemption rules?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:40:   `E11-15e-SURFACE-INVENTORY.md` Section 1 claims Tier-A based on copy_diff_lines ~38 + 22 REWRITE. Re-count from `git diff main..83d69e4`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:51:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Sections 1, 2, 3, 6
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:53:- `tests/test_workbench_e11_15e_chinese_first_bundle.py` Section 1 (positive bilingual locks — does this list match Section 2 of SURFACE-INVENTORY?)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:97:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:115:If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:120:/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:374:# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:379:    SURFACE-INVENTORY, the PERSONA-ROTATION-STATE entry, and this test
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:395:        / "E11-15d-SURFACE-INVENTORY.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:438:E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:695:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first|all English surfaces|all English-only|uniformly|the last|Chinese-first" -S .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-output.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-prompt.txt src/well_harness/static/workbench.html src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:699:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:700:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:701:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:702:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:703:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:704:.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:705:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:713:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:715:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:719:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:721:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:723:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:727:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:731:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:740:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:744:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:755:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1350:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:6:> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:756:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:757:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1352:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:78:## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:758:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1353:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:80:E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:766:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1371:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:767:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:768:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1378:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:769:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:770:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1381:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:7:> (Chinese-first DOM render). The new e2e infra immediately surfaced a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:771:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1384:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:86:- Real-DOM control-panel + approval entry buttons render Chinese-first text.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:797:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:815:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1499:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:1:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:816:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1500:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:11:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:817:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1501:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:18:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:818:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1502:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:36:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:822:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1511:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:1:# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:823:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:824:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1527:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:13:| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:825:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1528:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:27:  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:826:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1531:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:59:1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:837:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:839:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:843:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1556:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:845:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1563:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:847:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:861:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:866:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:878:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:881:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:883:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:884:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:893:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1639:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:897:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:902:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1652:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:904:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:944:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:952:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:957:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:964:/bin/zsh -lc "git diff --stat main..83d69e4 && echo '---DIFF---' && git diff --unified=0 --word-diff=plain main..83d69e4 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_approval_flow_polish.py .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:966: .../E11-15e-SURFACE-INVENTORY.md                   | 141 ++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:975:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:979:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1095:{+| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1127:{+E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1200:{+E11-15d-SURFACE-INVENTORY.md):+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1927:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:275:    35	E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1932:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:396:   115	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1947:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:49:> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1948:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1951:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1955:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1957:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1963:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1967:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1970:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1681:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1971:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1972:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1705:- **IMPORTANT** — [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:1): R2 does not fully close the R1 doc-honesty issue. The module header still says this slice “Closes the last English-only surface,” while the new guard at [tests/test_workbench_approval_flow_polish.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_flow_polish.py:176) only scans `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. The same overclaim therefore still ships in-branch, and the guard is too narrow to catch it there or to catch equivalent rephrasings elsewhere.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1973:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1976:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:351:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1981:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:31:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1983:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1985:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1993:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1994:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2005:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2007:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2009:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2026:.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2027:.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md:32:> **Persona selection: P5 (Apps Engineer)** — domain-anchoring is exactly the customer/repro lens this relabel is meant to serve; P5 round-robin slot also follows P2 (the last Tier-B was E11-14 = P2; round-robin successor is P3, but E11-13 was P1 and E11-14 was P2 — actually next is P3). However content-fit weight: P3 (Demo Presenter) is a better content match for "domain-anchored vocabulary the engineer/customer reads on screen". Plan defers to round-robin: **P3 Demo Presenter**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2028:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:5:**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2029:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2030:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:86:**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2031:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2032:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2033:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:139:fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2034:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:16:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2036:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2039:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2044:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2048:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2049:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2050:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2051:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2052:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2057:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2058:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2060:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2063:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2065:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2070:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2073:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2075:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2076:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2080:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2082:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2084:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2085:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2087:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2090:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2093:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2098:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2103:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:695:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first|all English surfaces|all English-only|uniformly|the last|Chinese-first" -S .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-output.md .planning/phases/E11-workbench-engineer-first-ux/persona-P*-E11-15e-prompt.txt src/well_harness/static/workbench.html src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2104:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:700:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72:E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2105:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:701:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:87:"all" or "the last". The deferred list above is **non-exhaustive** — if a
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2106:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:702:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2107:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:704:.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2109:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:715:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2111:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:719:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:166:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2113:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:721:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2115:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:723:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:111:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2118:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:731:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2120:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:740:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2123:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:744:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2126:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:756:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2127:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:767:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2128:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:769:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2129:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:797:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2130:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:823:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2135:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:837:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2136:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:839:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2138:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:847:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2141:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:861:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2143:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:866:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2148:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:878:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2151:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:881:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2153:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:883:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2154:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:884:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2158:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:897:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2160:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:904:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2162:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:944:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2163:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:952:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2165:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:957:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2171:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1095:{+| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |+}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2192:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2198:.planning/phases/governance-bundle-2/codex-r5-output.md:649:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2199:.planning/phases/governance-bundle-2/codex-r5-output.md:716:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2207:.planning/phases/governance-bundle-2/codex-r6-output.md:524:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2208:.planning/phases/governance-bundle-2/codex-r6-output.md:591:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2212:.planning/phases/governance-bundle-2/codex-r6-output.md:889:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2216:.planning/phases/governance-bundle-2/codex-r6-output.md:952:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2228:.planning/phases/governance-bundle-2/codex-r4-output.md:532: > **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2240:.planning/phases/governance-bundle-2/codex-r3-output.md:169:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2261:.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1790:    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2262:.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1857:   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2307:/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '1,260p' && printf '\\n---\\n' && nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2314:     6	E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2685:   115	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:2761:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3000:{"baseRefName":"main","body":"## Summary\n\nE11-15e Tier-A bundle that bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review.\n\n- **Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim\n- **Lockstep contract:** zero churn on existing substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar)\n- **JS lockstep:** workbench.js:3788 dynamic chip text bilingualized so first mode switch doesn't revert to English\n- **Truth-engine red line:** controller.py / runner.py / models.py / adapters / demo_server.py untouched; new test scans backend for the 23 Chinese display strings\n\n## Surface scope\n\n22 REWRITE rows: topbar chips (5) + WOW h3 direction flips (3) + state-of-world labels (5) + trust banner body (3) + dismiss button + authority banner headline + pre-hydration boot placeholders (3) + reference packet intro + inbox empty state + pending sign-off.\n\n**Surface honesty:** This sub-phase closes 22 surfaces. It does **NOT** close \"the last\" or \"all\". Deferred surfaces (system options, post-hydration JS boot status, phase-arrow flow diagram, column eyebrow tags) are explicitly listed in SURFACE-INVENTORY.md Section 3 (non-exhaustive).\n\n## Tier classification\n\nTier-A per constitution: copy_diff_lines ~38, REWRITE rows = 22 (>=10 lines AND >=3 REWRITE).\n\nPersona dispatch: **P3** (round-robin successor of E11-15d's P2) leads, with P1/P2/P4/P5 per Tier-A 5-persona requirement.\n\n## Verification\n\n- New test file `tests/test_workbench_e11_15e_chinese_first_bundle.py`: **67 cases pass**\n- Full suite: **1221 passed, 0 regressions**\n\n## Test plan\n\n- [x] tests/test_workbench_e11_15e_chinese_first_bundle.py — 67/67 pass\n- [x] tests/test_workbench_*.py — 188/188 pass\n- [x] tests/ — 1221/1221 pass\n- [ ] Tier-A 5-persona codex dispatch; if codex degraded, Executor 即 Gate (v3.2) per project memory rule (documented in SURFACE-INVENTORY Section 6)\n\nGenerated with Claude Code","headRefName":"feat/e11-15e-tier-a-chinese-first-bundle-20260426","number":30,"title":"phase(E11-15e): Tier-A Chinese-first bundle — 22 REWRITE rows"}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3038:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3082:    31	- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3083:    32	- **NIT** — `E11-15d-SURFACE-INVENTORY.md:86`, `workbench.html` lines 42/48/65/71/77/83/87/209/213/215/278/298/318/301/302: remaining-list still partial. `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block all still English/English-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3092:    41	- Guard now scans **3 artifacts**: SURFACE-INVENTORY, PERSONA-ROTATION-STATE, AND this test file itself (self-scan is the new safety net).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3095:    44	### NIT closure — expand SURFACE-INVENTORY remaining-list
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3097:    46	`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3106:    55	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — remaining-list expansion + grep template
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3111:    60	- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3179:    30	> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3189:    40	`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3197:    48	`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3203:    54	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — overclaim removed; deferred list added
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3228:    79	These are explicitly enumerated in the SURFACE-INVENTORY now.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3284:    11	corrected. See E11-15d-SURFACE-INVENTORY.md for the (non-exhaustive)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3455:   182	# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3460:   187	    SURFACE-INVENTORY, the PERSONA-ROTATION-STATE entry, and this test
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3476:   203	        / "E11-15d-SURFACE-INVENTORY.md",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3527:    'E11-15e-SURFACE-INVENTORY.md': repo / '.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md',
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3553:E11-15e-SURFACE-INVENTORY.md PASS []
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3590:text = Path('.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md').read_text(encoding='utf-8').splitlines()
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3680:45 | `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3777:text = Path('.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md').read_text(encoding='utf-8').splitlines()
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3857:- `IMPORTANT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:321), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:6), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:76): Section 3 is still incomplete. The live `/workbench` HTML still exposes English-only circuit-skeleton labels `SW1`, `Logic 1`, `Logic 2`, `Logic 3`, `Logic 4`, `THR LOCK` at lines 321-326, and the browser-tab title remains `Control Logic Workbench` at line 6. None of these appear in Section 2’s rewrite table or Section 3’s deferred table.  
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3860:- `IMPORTANT` [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:19), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:64), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:6), [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:3): the Tier/count evidence is not reproducible as written. By constitution, `copy_diff_lines` is insertions+deletions; `git diff --stat main..83d69e4 -- workbench.html workbench.js` yields `28 + 28 = 56`, not `~38`. Section 2 contains 26 numbered rewrite rows, the positive HTML lock list contains 24 entries, and the new test docstring still says `17`. Tier-A still fires because `56 >= 10` and REWRITE is well above `3`, but the published `22` / `~38` math is internally inconsistent.  
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3861:  Suggested fix: normalize one canonical counting scheme across PR body, shared context, SURFACE-INVENTORY, and the new test docstring, and spell out dedup arithmetic that actually lands on the published number.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3865:Overclaim drift is clean. Extending the E11-15d heuristic to PR #30 body, [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35), and [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:1) produced no fresh `last English-only surface` / `uniformly Chinese-first` claims. `pytest -q tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure tests/test_workbench_e11_15e_chinese_first_bundle.py` passed with `68 passed`.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3874:- `IMPORTANT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:321), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:6), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:76): Section 3 is still incomplete. The live `/workbench` HTML still exposes English-only circuit-skeleton labels `SW1`, `Logic 1`, `Logic 2`, `Logic 3`, `Logic 4`, `THR LOCK` at lines 321-326, and the browser-tab title remains `Control Logic Workbench` at line 6. None of these appear in Section 2’s rewrite table or Section 3’s deferred table.  
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3877:- `IMPORTANT` [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:19), [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:64), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:6), [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:3): the Tier/count evidence is not reproducible as written. By constitution, `copy_diff_lines` is insertions+deletions; `git diff --stat main..83d69e4 -- workbench.html workbench.js` yields `28 + 28 = 56`, not `~38`. Section 2 contains 26 numbered rewrite rows, the positive HTML lock list contains 24 entries, and the new test docstring still says `17`. Tier-A still fires because `56 >= 10` and REWRITE is well above `3`, but the published `22` / `~38` math is internally inconsistent.  
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3878:  Suggested fix: normalize one canonical counting scheme across PR body, shared context, SURFACE-INVENTORY, and the new test docstring, and spell out dedup arithmetic that actually lands on the published number.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:3882:Overclaim drift is clean. Extending the E11-15d heuristic to PR #30 body, [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:72), [_E11-15e-prompt-shared-context.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35), and [test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:1) produced no fresh `last English-only surface` / `uniformly Chinese-first` claims. `pytest -q tests/test_workbench_approval_flow_polish.py::test_e11_15d_artifacts_do_not_overclaim_closure tests/test_workbench_e11_15e_chinese_first_bundle.py` passed with `68 passed`.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-prompt.txt:36:- `.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-r2-output.md:308:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-r2-output.md:632:+# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-r2-output.md:1210:   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:44:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:622:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:629:/bin/zsh -lc 'git diff --unified=3 main..7543d77 -- src/well_harness/static/workbench.html tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py .planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:631:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:635:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:715:+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:71:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-R2-prompt.txt:25:- Does the R2 `e11_15e_chinese` list now cover every shipped Chinese display string introduced by E11-15e? Walk the SURFACE-INVENTORY (rows 1-30) and confirm each unique Chinese segment is anchored OR is a substring of an anchored segment.
.planning/phases/E11-workbench-engineer-first-ux/persona-E11-05-shared-context.txt:18:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:16:- **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1`: R2 doesn't fully close the R1 doc-honesty issue. The module header still says this slice "Closes the last English-only surface," while the new guard at `:176` only scanned `E11-15d-SURFACE-INVENTORY.md` for two literal phrases. Same overclaim still shipped in-branch; guard too narrow.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:17:- **NIT** — `E11-15d-SURFACE-INVENTORY.md:86`, `workbench.html` lines 42/48/65/71/77/83/87/209/213/215/278/298/318/301/302: remaining-list still partial. `Manual (advisory)`, system options, state-of-world labels, trust-banner body, boot placeholders, reference-packet block all still English/English-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:26:- Guard now scans **3 artifacts**: SURFACE-INVENTORY, PERSONA-ROTATION-STATE, AND this test file itself (self-scan is the new safety net).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:29:### NIT closure — expand SURFACE-INVENTORY remaining-list
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:31:`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:40:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — remaining-list expansion + grep template
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-R2-prompt.txt:33:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` R2 closure log + rows #15/#18/#20/#27-#30
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:44:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Section 2 (full surface table)
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:75:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:98:- `.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:896:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:334:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1143:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:8701:- IMPORTANT — `src/well_harness/static/workbench.html:77-90,107-120,137-150`, `src/well_harness/static/workbench.js:3888-3896`, `src/well_harness/static/workbench_start.html:69,108-114`, `tests/test_workbench_wow_starters.py:80-93,114-118`, `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:23-25`: two user-facing surfaces remain unguarded. The suite never checks the selector contract that makes the cards clickable (`data-wow-action="run"` / `.workbench-wow-run-button`), and it never probes the three `/workbench/start` rewrites that changed “not shipped” text to “shipped”. Those surfaces are in the recorded inventory but not in the regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:1146:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:8713:- IMPORTANT — `src/well_harness/static/workbench.html:77-90,107-120,137-150`, `src/well_harness/static/workbench.js:3888-3896`, `src/well_harness/static/workbench_start.html:69,108-114`, `tests/test_workbench_wow_starters.py:80-93,114-118`, `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:23-25`: two user-facing surfaces remain unguarded. The suite never checks the selector contract that makes the cards clickable (`data-wow-action="run"` / `.workbench-wow-run-button`), and it never probes the three `/workbench/start` rewrites that changed “not shipped” text to “shipped”. Those surfaces are in the recorded inventory but not in the regression lock.
.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:79:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:161:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:174:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:181:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:961:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p' && printf '\\n---\\n' && nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:59:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Section 2 (full surface table)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:77:I’m treating this as a read-only bilingual copy/convention review for E11-15e. I’ll load the shared context, skim any relevant LogicMVP memory, then inspect the exact diff, tests, and surface inventory before issuing an approval verdict with line-cited findings.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:340:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:354:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:358:If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:361:/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:513:E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1350:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:6:> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1351:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1352:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:78:## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1353:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:80:E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1354:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:83:- E11-15c: 3 column h2s + page eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1355:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:103:  因果链走读` etc. are English-first; same direction-flip pattern as
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1356:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:104:  E11-15c column h2s could apply.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1371:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1372:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:44:| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1373:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45:| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1374:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:46:| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1375:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:83:| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1376:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:113:| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1377:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1378:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1379:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1380:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:6:> affordance JS toggle), E11-13 (bundle/shell sentinel), and E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1381:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:7:> (Chinese-first DOM render). The new e2e infra immediately surfaced a
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1382:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:66:> successor of E11-15c's P4 AND content-fit: P5 reviews end-user-facing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1383:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:84:E11-15c closure (2 tests):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1384:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:86:- Real-DOM control-panel + approval entry buttons render Chinese-first text.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1392:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:108:E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1442:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:11:Across E11-08, E11-15, E11-15b, E11-15c, and E11-11, the per-sub-phase
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1443:.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:134:   E11-15c PERSONA-ROTATION-STATE.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1467:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1499:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:1:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1500:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:11:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1501:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:18:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1502:.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:36:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1511:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:1:# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1512:.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1526:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:1:# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1527:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:13:| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1528:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:27:  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1529:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:33:- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1530:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:57:`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1531:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:59:1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1532:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:74:- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1533:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:75:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1546:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1548:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1556:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1563:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1577:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1593:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1598:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1615:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1618:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1620:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1621:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1628:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1639:.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1647:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1652:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1659:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1669:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1677:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:595:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1679:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:603:/bin/zsh -lc "git diff --stat main..938a5a2 && printf '\\n---\\n' && git diff --unified=0 main..938a5a2 -- src/well_harness/static/workbench.html tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_direction_consistency.py .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1680:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:605: .../E11-15c-SURFACE-INVENTORY.md                   |  80 +++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1682:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:614:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1683:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:618:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1691:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:694:+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1808:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1819:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1824:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1840:E11-02-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1841:E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1842:E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1843:E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1844:E11-06-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1845:E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1846:E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1847:E11-09-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1848:E11-10-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1849:E11-11-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1851:E11-13-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1852:E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1853:E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1854:E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1855:E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1856:E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1857:E11-15e-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:1973:     6	E11-15d-SURFACE-INVENTORY.md):
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2232:/bin/zsh -lc "sed -n '1,220p' .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2308:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2528:/bin/zsh -lc "rg -n \"Kogami / Engineer|data-identity-name|Identity</span>|feedback-mode|title=\\\"\" src/well_harness/static/workbench.html .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2530:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:37:| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2531:.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:84:| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2584:.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25:| 3 | Topbar chip tooltip | "Manual feedback override is advisory — truth engine readings remain authoritative." | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode title attribute) | [ANCHORED] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2604:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md | sed -n '18,32p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2623:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '30,95p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2716:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:39>), [E11-13-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:88>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:86>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2720:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:143>), [test_workbench_chinese_direction_consistency.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:11>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:97>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2724:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:248>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:104>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:31>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2744:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:39>), [E11-13-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:88>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:86>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2748:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:143>), [test_workbench_chinese_direction_consistency.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:11>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:97>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:2752:- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:248>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:104>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:31>)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:318:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:343: .../E11-14-SURFACE-INVENTORY.md                    |   62 +
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-prompt.txt:20:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:549:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:656:9207:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:1:# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:86:- `.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:350:.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:367: .../E11-11-SURFACE-INVENTORY.md                    | 106 +++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-prompt.txt:20:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:43:- `.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:139:.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:485:/bin/zsh -lc 'git diff --stat main..4a53b94 && git diff --unified=80 main..4a53b94 -- src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js tests/test_workbench_role_affordance.py .planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:487: .../E11-08-SURFACE-INVENTORY.md                    |  52 +++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:494:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:498:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:2873:.planning/phases/E11-workbench-engineer-first-ux/E11-08-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:298:/bin/zsh -lc "sed -n '1,220p' .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:846:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:855:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:860:      53 .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:5616:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:5734:Truth-engine red line is clean: `git diff --name-only main..2df105c` shows only `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md`, `src/well_harness/static/workbench.html`, `src/well_harness/static/workbench.js`, and `tests/test_workbench_column_rename.py`. No truth-engine files were touched.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:5747:Truth-engine red line is clean: `git diff --name-only main..2df105c` shows only `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md`, `src/well_harness/static/workbench.html`, `src/well_harness/static/workbench.js`, and `tests/test_workbench_column_rename.py`. No truth-engine files were touched.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:25:`E11-15d-SURFACE-INVENTORY.md`:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:39:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — overclaim removed; deferred list added
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:64:These are explicitly enumerated in the SURFACE-INVENTORY now.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-prompt.txt:31:- `.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-prompt.txt:10:   For every bilingualized string in `E11-15e-SURFACE-INVENTORY.md` Section 2:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-prompt.txt:29:- `.planning/phases/E11-workbench-engineer-first-ux/E11-06-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-output.md:471:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-output.md:865:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-output.md:1075:366:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-output.md:2182:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-output.md:173:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-output.md:214:+# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-output.md:791:   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:239: .../E11-14-SURFACE-INVENTORY.md                    | 62 ++++++++++++++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:242: create mode 100644 .planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:924: .../E11-14-SURFACE-INVENTORY.md                    |  62 +++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:936:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1779:.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md:43:| 17 | workbench_start.html:144 | "Approval Center · 静态 shell 占位" | surface-location | src/well_harness/static/workbench.html:139-163 (静态 lanes) | [ANCHORED] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1780:.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md:97:- Inventory rows 17–21: anchor traced by Codex R3 finding `R3-F3` (Approval Center static shell)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1781:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md:23:| 1 | 409 error remediation message | "manual_feedback_override requires actor + ticket_id + manual_override_signoff. Acquire sign-off via Approval Center, or switch to auto_scrubber." | `src/well_harness/demo_server.py:_validate_manual_override_signoff()` reject() helper | [ANCHORED] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1782:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md:31:The 409 response asserts: "manual_feedback_override requires actor + ticket_id + manual_override_signoff. Acquire sign-off via Approval Center, or switch to auto_scrubber."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1783:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md:34:- Rule enforced in `_validate_manual_override_signoff()` — exactly the 3 required fields named (actor / ticket_id / manual_override_signoff)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:1784:.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md:35:- Approval Center referenced exists in workbench shell DOM (`#approval-center-entry` per workbench.html, locked by E11-09 dual-route test)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:511:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:867:.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:876:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:881:      53 .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:886:/bin/zsh -lc 'git diff --unified=3 main..2df105c -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:888:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:892:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:28:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:21:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:35:E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.
.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md:39:If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:633:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:646:/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:546:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:557: .../E11-05-SURFACE-INVENTORY.md                    |  51 ++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:569:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:576:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:581:/bin/zsh -lc 'git diff --unified=80 a17e744..a02729a -- src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:583:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:587:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2627:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9207:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:1:# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9208:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:5:> Records every user-facing string introduced by E11-05 and classifies each per the [ANCHORED/REWRITE/DELETE] taxonomy so the Tier-A vs Tier-B routing decision is auditable.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9209:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:23:| 13 | `workbench_start.html` line ~69: "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" → "wow_a/b/c 起手卡片已上线（E11-05），见 /workbench 顶部「起手卡」" | [REWRITE] | `workbench_start.html:69` | Now that E11-05 ships, the placeholder is updated to a positive claim. |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9210:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:24:| 14 | `workbench_start.html` line ~108: "wow_a/b/c 目前只在 tests/e2e/test_wow_a_causal_chain.py 里有，没有 UI 走读 surface" → "wow_a/b/c 起手卡 已在 /workbench 顶部上线（E11-05）…" | [REWRITE] | `workbench_start.html:107-108` | Removes the negative claim that no UI走读 surface exists. |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9211:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:25:| 15 | `workbench_start.html` line ~113: "无-chrome demo mode + UI wow_a 走读 进入 E11-05/08 范围" → "无-chrome demo mode 进入 E11-08 范围（wow_a 走读 已 E11-05 完成）" | [REWRITE] | `workbench_start.html:113` | Removes the implicit claim that wow_a走读 is still pending; demarcates remaining E11-08 scope. |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9212:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:38:Both thresholds are met: the 3 [REWRITE] lines on `workbench_start.html` are doc-truth corrections (placeholder copy that previously claimed E11-05 wasn't shipped). Per the rule's spirit — protect against stale copy reaching production — Tier-A is the conservative routing here.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9213:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:40:> **Action: dispatch all 5 personas (P1–P5) for E11-05.**
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9214:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:47:- `src/well_harness/static/workbench.js` (NEW WOW_SCENARIOS const + runWowScenario + installWowStarters + 1 hook line in DOMContentLoaded)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9215:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:48:- `src/well_harness/static/workbench_start.html` (3 [REWRITE] lines documenting that E11-05 has shipped)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9222:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9225:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:331:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9238:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:366:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9239:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:373:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9259:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1303:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'; nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9276:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8409:/bin/zsh -lc 'git diff --unified=5 a17e744..a02729a -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js src/well_harness/static/workbench.css src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9277:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8411:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9278:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8415:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9331:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9347:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:161:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9348:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:174:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9349:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:181:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9364:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:961:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p' && printf '\\n---\\n' && nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9408:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9424:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:546:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9425:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:557: .../E11-05-SURFACE-INVENTORY.md                    |  51 ++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9426:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:569:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9427:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:576:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9428:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:581:/bin/zsh -lc 'git diff --unified=80 a17e744..a02729a -- src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9429:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:583:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9430:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:587:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9482:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2627:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9499:.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md:33:| 7  | workbench_start.html:69 | "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" | feature-name (negative) | E11-00-PLAN.md §3 row E11-05 | [REWRITE → planned for E11-05] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9500:.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md:39:| 13 | workbench_start.html:108 | "无-chrome demo mode + UI wow_a 走读 进入 E11-05/08 范围" | feature-name (negative) | E11-00-PLAN.md §3 rows E11-05,E11-08 | [REWRITE → planned for E11-05/08] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9507:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9512:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:310:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9524:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:334:/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9525:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:341:      51 .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9536:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:855:/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/e2e/test_wow_a_causal_chain.py tests/e2e/test_wow_b_monte_carlo.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9541:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1076:/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9564:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:35:- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9569:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:633:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:9570:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:646:/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp

exec
/bin/zsh -lc 'rg -n "truth_engine|Truth Engine|反馈模式信任说明|真值引擎权限契约|手动反馈覆盖仅作参考|隐藏本次会话的信任提示横幅" src/well_harness/static/workbench.js src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:39:          title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."
src/well_harness/static/workbench.html:63:        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
src/well_harness/static/workbench.html:66:          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
src/well_harness/static/workbench.html:204:        aria-label="反馈模式信任说明 · Feedback mode trust affordance"
src/well_harness/static/workbench.html:222:          aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"
src/well_harness/static/workbench.html:244:        aria-label="真值引擎权限契约 · Truth-engine authority contract"
src/well_harness/static/workbench.html:248:          真值引擎（只读）· Truth Engine — Read Only
src/well_harness/static/workbench.js:3779:  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
src/well_harness/static/workbench.js:3788:      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
src/well_harness/static/workbench.js:4043:    writeField("truth_engine_sha", payload.truth_engine_sha);

exec
/bin/zsh -lc 'git diff main..9184c6d -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
codex
I’ve confirmed the exact `rglob("*.py")` extension and the `adapter_count >= 1` sanity check in the test diff. I’m doing one last pass against `E11-15e-SURFACE-INVENTORY.md` so the approval is tied to the declared row set, not just the commit message.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
     2	
     3	**Date:** 2026-04-26 (R1 dispatched 2026-04-26, R2 patched same day)
     4	**Status:** R2 in_review (Tier-A, 26 REWRITE rows after R2 expansion → 5-persona re-dispatch)
     5	**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
     6	**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
     7	that P2 enumerated during the E11-15d Tier-B review (see
     8	`tests/test_workbench_approval_flow_polish.py:189-194`).
     9	
    10	## R2 closure log (2026-04-26)
    11	
    12	R1 dispatch: P1 APPROVE_WITH_NITS (3 NITs), P2 incomplete codex output, P3
    13	CHANGES_REQUIRED (3 IMPORTANT + 1 NIT), P4 incomplete codex output, P5
    14	CHANGES_REQUIRED (2 IMPORTANT + 1 NIT). R2 incorporates **all** actionable
    15	findings from P1/P3/P5 in a single patch:
    16	
    17	| Finding | Source | R2 fix |
    18	|---------|--------|--------|
    19	| `title="Manual feedback override is advisory…"` English-only | P3 IMPORTANT 1 + P1 NIT 1 | Bilingualized + locked + inventory row #27 added |
    20	| `1000-trial 可靠性 · Monte Carlo` not strict Chinese-first | P3 IMPORTANT 2 | Changed to `1000 次试验可靠性 · Monte Carlo`; row #9 updated |
    21	| Multi-middot inside Chinese half (rows #15, #20) | P3 IMPORTANT 3 | Outer middot reserved for CN/EN split; inner clauses use comma / parentheses |
    22	| Trust banner Chinese awkward calque | P3 NIT + P1 NIT 2 | `这里…` → `此处…`; `仍然是权威` → `仍以真值引擎读数为准`; `不算 manual feedback` → `不属于"手动反馈"` |
    23	| `aria-label`s on dismiss button + trust banner + authority banner English-only | P1 NIT 1 + P3 IMPORTANT 1 | All 3 aria-labels bilingualized; rows #28-#30 added |
    24	| Section 7 guard list missing trust-banner truth-engine sentence + JS truth_engine label | P5 IMPORTANT 1 | Guard list extended to cover both shipped strings |
    25	| Guard doesn't traverse `src/well_harness/adapters/` | P5 IMPORTANT 2 | Guard now walks `adapters/**/*.py` via `rglob`, with sanity-check that ≥1 adapter file is found |
    26	
    27	R2 verification: 80/80 new tests pass (was 67 in R1; +13 new locks); 357/357
    28	workbench-suite tests pass; **1234/1234** full suite pass (was 1221 in R1).
    29	
    30	## R2 deferred (still legitimate per Section 3 surface-honesty pledge)
    31	
    32	- P1 NIT 3: post-hydration JS boot status strings (`Probe & Trace ready. ...` × 3) remain English-only — explicitly deferred per Section 3.
    33	- P3 NIT (full sentence-split of trust-banner English clause): would require restructuring the existing semantic block (`<em>` + `<strong>` + `<span>` triplet). Deferred to a UX/copy decision; the R2 native-phrasing tightening already addresses the worst part of the density complaint.
    34	- P5 NIT (boot-path comment about `installFeedbackModeAffordance` not auto-calling `setFeedbackMode`): no behavioral bug, no fix required.
    35	
    36	---
    37	
    38	## 1. Tier classification
    39	
    40	Per the constitution, Tier = **Tier-A** iff
    41	`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.
    42	
    43	| Metric | Count |
    44	|--------|------:|
    45	| copy_diff_lines (workbench.html + workbench.js)        | ~38 |
    46	| REWRITE rows (display strings rewritten in place)      | **22** |
    47	| DELETE rows (English-only string removed without bilingual replacement) | 0 |
    48	| ADD rows (new strings introduced for the first time)   | 0 |
    49	
    50	**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus
    51	P1, P2, P4, P5 per Tier-A 5-persona requirement.
    52	
    53	---
    54	
    55	## 2. Surface table (REWRITE = 22)
    56	
    57	Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
    58	verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
    59	passing without contract churn.
    60	
    61	| # | Surface | File:Line | Old (English-only) | New (bilingual) |
    62	|---|---------|-----------|---------------------|-----------------|
    63	| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
    64	| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
    65	| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
    66	| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
    67	| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
    68	| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
    69	| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
    70	| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
    71	| 9 | WOW h3 (wow_b) — direction flip + R2 strict Chinese-first | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000 次试验可靠性 · Monte Carlo` |
    72	| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
    73	| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
    74	| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
    75	| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
    76	| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
    77	| 15 | State-of-world advisory flag (R2: comma instead of inner middot) | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading` |
    78	| 16 | Trust banner scope `<em>` (R2: `此处` + `不属于"手动反馈"`) | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>此处"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
    79	| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
    80	| 18 | Trust banner truth-engine `<span>` (R2: `仍以真值引擎读数为准`) | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings ...` |
    81	| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
    82	| 20 | Authority banner headline (R2: parentheses instead of inner middot) | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎（只读）· Truth Engine — Read Only` |
    83	| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
    84	| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
    85	| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
    86	| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
    87	| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
    88	| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
    89	| 27 | Feedback-mode chip `title` attribute (R2 P3 IMPORTANT 1 + P1 NIT 1 closure) | workbench.html:39 | `title="Manual feedback override is advisory — truth engine readings remain authoritative."` | `title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."` |
    90	| 28 | Trust banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:204 | `aria-label="Feedback mode trust affordance"` | `aria-label="反馈模式信任说明 · Feedback mode trust affordance"` |
    91	| 29 | Trust dismiss button `aria-label` (R2 P1 NIT 1 closure) | workbench.html:222 | `aria-label="Hide trust banner for this session"` | `aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"` |
    92	| 30 | Authority banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:244 | `aria-label="Truth-engine authority contract"` | `aria-label="真值引擎权限契约 · Truth-engine authority contract"` |
    93	
    94	(R2 expanded count: 26 REWRITE rows after dedup of #5/#6 with their HTML siblings,
    95	plus 4 R2 accessibility/hover names = **30 row IDs / ~26 distinct surfaces**.
    96	Tier-A trigger remains satisfied; copy_diff_lines now ≈ 50.)
    97	
    98	---
    99	
   100	## 3. Out of scope (explicitly deferred — surface-honesty closure)
   101	
   102	E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
   103	following surfaces remain English-only and are **deferred to future sub-phases
   104	or constitutional decisions**, not silently included:
   105	
   106	| Deferred surface | Why deferred | File:Line |
   107	|------------------|--------------|-----------|
   108	| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
   109	| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
   110	| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
   111	| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
   112	| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
   113	| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
   114	| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
   115	
   116	**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
   117	"all" or "the last". The deferred list above is **non-exhaustive** — if a
   118	reviewer finds another English-only user-visible surface not listed here that is
   119	neither REWRITE in this slice nor in the deferred table, that finding is
   120	**legitimate** and a CHANGES_REQUIRED is appropriate.
   121	
   122	---
   123	
   124	## 4. Truth-engine red line
   125	
   126	Display-copy edits only. `controller.py` / `runner.py` / `models.py` /
   127	`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep
   128	guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::
   129	test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any
   130	of the 23 Chinese display strings introduced here.
   131	
   132	---
   133	
   134	## 5. Lockstep test impact
   135	
   136	| Existing test file | Impact | Reason |
   137	|--------------------|--------|--------|
   138	| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
   139	| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
   140	| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
   141	| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
   142	| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
   143	| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
   144	| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
   145	| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
   146	| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |
   147	
   148	Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).
   149	
   150	---
   151	
   152	## 6. Persona dispatch plan
   153	
   154	Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e
   155	**lead** is **P3**.
   156	
   157	| Persona | Lens |
   158	|---------|------|
   159	| P1 | Engineer-task-flow regression |
   160	| P2 | Surface-inventory honesty + closure-claim guards |
   161	| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
   162	| P4 | Lockstep test contract preservation (no churn on existing locks) |
   163	| P5 | Truth-engine red-line + JS-HTML lockstep |
   164	
   165	**Codex degradation contingency:** if all 5 codex accounts are
   166	secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply
   167	**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:
   168	Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the
   169	fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
   170	entry. Self-signing requires the standard 1221-test green + repo-honesty self-
   171	review (this inventory + Section 3 surface-honesty pledge satisfy that bar).

exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '180,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   180	        "<li>No proposals submitted yet.</li>",
   181	        "<strong>Pending Kogami sign-off</strong>",
   182	        # R2 P3 IMPORTANT closure: forbid the R1 multi-middot-inside-Chinese
   183	        # forms that broke the strict `<中文> · <English>` convention.
   184	        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
   185	        "真值引擎 · 只读 · Truth Engine — Read Only",
   186	        # R2 P3 NIT closure: forbid the awkward R1 phrasings.
   187	        '这里"手动反馈"的含义',
   188	        "仍然是权威",
   189	        # R2 P1 NIT + P3 IMPORTANT closure: forbid the R1 English-only
   190	        # accessibility/hover names.
   191	        'title="Manual feedback override is advisory — truth engine readings remain authoritative."',
   192	        'aria-label="Hide trust banner for this session"',
   193	        'aria-label="Feedback mode trust affordance"',
   194	        'aria-label="Truth-engine authority contract"',
   195	    ],
   196	)
   197	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   198	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   199	    assert stale not in html, f"stale English-only surface still present: {stale}"
   200	
   201	
   202	# ─── 3. English suffixes preserved (substring locks unchanged) ───────
   203	
   204	
   205	@pytest.mark.parametrize(
   206	    "preserved_english_suffix",
   207	    [
   208	        # Anchors required by trust_affordance.py
   209	        "Manual (advisory)",
   210	        "Truth engine readings",
   211	        "Hide for session",
   212	        'What "manual feedback" means here',
   213	        "That mode is advisory.",
   214	        # Anchor required by authority_banner.py
   215	        "Truth Engine — Read Only",
   216	        # Anchor required by role_affordance.py
   217	        "Pending Kogami sign-off",
   218	        # Anchor required by state_of_world_bar.py
   219	        "advisory · not a live truth-engine reading",
   220	        # Anchors required by column_rename.py:118-120 (pre-hydration)
   221	        "Waiting for probe &amp; trace panel boot.",
   222	        "Waiting for annotate &amp; propose panel boot.",
   223	        "Waiting for hand off &amp; track panel boot.",
   224	    ],
   225	)
   226	def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
   227	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   228	    assert preserved_english_suffix in html, (
   229	        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
   230	    )
   231	
   232	
   233	# ─── 4. Structural anchors preserved ─────────────────────────────────
   234	
   235	
   236	@pytest.mark.parametrize(
   237	    "anchor",
   238	    [
   239	        'id="workbench-feedback-mode"',
   240	        'id="workbench-trust-banner"',
   241	        'id="workbench-authority-banner"',
   242	        'id="workbench-pending-signoff-affordance"',
   243	        'id="workbench-state-of-world-bar"',
   244	        'id="workbench-wow-starters"',
   245	        'data-trust-banner-dismiss',
   246	        'data-feedback-mode="manual_feedback_override"',
   247	    ],
   248	)
   249	def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
   250	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   251	    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"
   252	
   253	
   254	# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
   255	
   256	
   257	def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
   258	    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
   259	    switch. If the JS literal stays English-only, the very first mode
   260	    flip would silently revert the static HTML's bilingual chip back to

exec
/bin/zsh -lc 'rg --files src/well_harness/adapters' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/adapters/landing_gear_intake_packet.py
src/well_harness/adapters/c919_etras_frozen_v1/telemetry_logger.py
src/well_harness/adapters/c919_etras_frozen_v1/tr_wow_filter.py
src/well_harness/adapters/c919_etras_frozen_v1/tick.py
src/well_harness/adapters/c919_etras_frozen_v1/lock_status_aggregator.py
src/well_harness/adapters/c919_etras_frozen_v1/cmd3_latch_controller.py
src/well_harness/adapters/c919_etras_frozen_v1/state_machine.py
src/well_harness/adapters/c919_etras_frozen_v1/__init__.py
src/well_harness/adapters/c919_etras_frozen_v1/safety_interlock_manager.py
src/well_harness/adapters/c919_etras_frozen_v1/fadec_stow_logic.py
src/well_harness/adapters/c919_etras_frozen_v1/wow_selector.py
src/well_harness/adapters/c919_etras_frozen_v1/fadec_deploy_logic.py
src/well_harness/adapters/c919_etras_frozen_v1/cmd2_controller.py
src/well_harness/adapters/c919_etras_frozen_v1/signals.py
src/well_harness/adapters/thrust_reverser_intake_packet.py
src/well_harness/adapters/efds_adapter.py
src/well_harness/adapters/__init__.py
src/well_harness/adapters/c919_etras_adapter.py
src/well_harness/adapters/bleed_air_adapter.py
src/well_harness/adapters/bleed_air_intake_packet.py
src/well_harness/adapters/landing_gear_adapter.py
src/well_harness/adapters/c919_etras_intake_packet.py

codex
The adapter sanity check is real: this checkout has 20+ `adapters/**/*.py` files, so the guard is not vacuous. I’m reading the row table directly now to make sure nothing in the declared 30-row surface set escaped the guard via a unique Chinese fragment.
exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '300,380p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3772,3794p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '61,112p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

 succeeded in 0ms:
   300	    assert "隐藏本次会话的信任提示横幅" in html  # dismiss aria-label
   301	    assert "真值引擎权限契约" in html       # authority-banner aria-label
   302	
   303	
   304	# ─── 7. Truth-engine red line — backend untouched ────────────────────
   305	
   306	
   307	def test_e11_15e_does_not_touch_truth_engine_backend() -> None:
   308	    """E11-15e only edits static HTML/JS display copy. It must NOT leak
   309	    into controller.py / runner.py / models.py / demo_server.py / any
   310	    `src/well_harness/adapters/*.py` (truth-engine red line per
   311	    .planning/constitution.md).
   312	
   313	    R2 P5 IMPORTANT closure:
   314	      - Guard list extended to cover the trust-banner truth-engine
   315	        sentence and the JS-only `truth_engine` chip label that the
   316	        R1 list missed.
   317	      - Backend traversal extended to walk `src/well_harness/adapters/
   318	        **/*.py` (excluding `__pycache__`) so the constitutional adapter
   319	        boundary is actually enforced, not only claimed.
   320	    """
   321	    repo_root = Path(__file__).resolve().parents[1]
   322	    well_harness_dir = repo_root / "src" / "well_harness"
   323	    backend_paths: list[Path] = [
   324	        well_harness_dir / "controller.py",
   325	        well_harness_dir / "runner.py",
   326	        well_harness_dir / "models.py",
   327	        well_harness_dir / "demo_server.py",
   328	    ]
   329	    adapters_dir = well_harness_dir / "adapters"
   330	    if adapters_dir.is_dir():
   331	        backend_paths.extend(
   332	            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
   333	        )
   334	    # Sanity check: the adapters traversal MUST find at least one file,
   335	    # otherwise the guard silently relaxes if adapters/ gets renamed or
   336	    # emptied. R2 P5 IMPORTANT closure depends on this.
   337	    adapter_count = sum(1 for p in backend_paths if "adapters" in p.parts)
   338	    assert adapter_count >= 1, (
   339	        "E11-15e red-line guard expected ≥1 adapter under "
   340	        "src/well_harness/adapters/; adapter directory missing or empty"
   341	    )
   342	    e11_15e_chinese = [
   343	        # Topbar chips
   344	        "身份 · Identity",
   345	        "工单 · Ticket",
   346	        "反馈模式 · Feedback Mode",
   347	        "系统 · System",
   348	        "手动（仅参考）",
   349	        # WOW h3s (R2 includes the new wow_b strict-Chinese form)
   350	        "因果链走读",
   351	        "1000 次试验可靠性",
   352	        "反向诊断 · Reverse Diagnose",
   353	        # State-of-world labels + flag (R2 uses comma-separated form)
   354	        "真值引擎 SHA",
   355	        "最近 e2e",
   356	        "对抗样本",
   357	        "未关闭问题",
   358	        "仅参考，非真值引擎实时读数",
   359	        # Trust banner body (R2 native phrasing)
   360	        '此处"手动反馈"的含义',
   361	        "该模式仅作参考",
   362	        # R2 P5 IMPORTANT #1 closure: anchors for the trust-banner
   363	        # truth-engine sentence and the unique inner phrase, plus the
   364	        # JS-only `truth_engine` chip label, so a future backend leak of
   365	        # any shipped Chinese display string fails the guard.
   366	        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准",
   367	        "你的手动反馈会被记录用于 diff / review",
   368	        "真值引擎 · Truth Engine",  # JS-side `truth_engine` chip label
   369	        # Trust banner dismiss + authority banner headline (R2 form)
   370	        "隐藏（本次会话）",
   371	        "真值引擎（只读）",
   372	        # Pre-hydration boot placeholders + reference packet + inbox + sign-off
   373	        "等待 probe",
   374	        "等待 annotate",
   375	        "等待 hand off",
   376	        "参考资料、澄清说明",
   377	        "暂无已提交提案",
   378	        "等待 Kogami 签字",
   379	        # R2 accessibility/hover names (unique Chinese segments only)
   380	        "手动反馈覆盖仅作参考",

 succeeded in 0ms:
    61	| # | Surface | File:Line | Old (English-only) | New (bilingual) |
    62	|---|---------|-----------|---------------------|-----------------|
    63	| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
    64	| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
    65	| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
    66	| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
    67	| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
    68	| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
    69	| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
    70	| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
    71	| 9 | WOW h3 (wow_b) — direction flip + R2 strict Chinese-first | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000 次试验可靠性 · Monte Carlo` |
    72	| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
    73	| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
    74	| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
    75	| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
    76	| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
    77	| 15 | State-of-world advisory flag (R2: comma instead of inner middot) | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading` |
    78	| 16 | Trust banner scope `<em>` (R2: `此处` + `不属于"手动反馈"`) | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>此处"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
    79	| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
    80	| 18 | Trust banner truth-engine `<span>` (R2: `仍以真值引擎读数为准`) | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings ...` |
    81	| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
    82	| 20 | Authority banner headline (R2: parentheses instead of inner middot) | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎（只读）· Truth Engine — Read Only` |
    83	| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
    84	| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
    85	| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
    86	| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
    87	| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
    88	| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
    89	| 27 | Feedback-mode chip `title` attribute (R2 P3 IMPORTANT 1 + P1 NIT 1 closure) | workbench.html:39 | `title="Manual feedback override is advisory — truth engine readings remain authoritative."` | `title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."` |
    90	| 28 | Trust banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:204 | `aria-label="Feedback mode trust affordance"` | `aria-label="反馈模式信任说明 · Feedback mode trust affordance"` |
    91	| 29 | Trust dismiss button `aria-label` (R2 P1 NIT 1 closure) | workbench.html:222 | `aria-label="Hide trust banner for this session"` | `aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"` |
    92	| 30 | Authority banner `aria-label` (R2 P1 NIT 1 closure) | workbench.html:244 | `aria-label="Truth-engine authority contract"` | `aria-label="真值引擎权限契约 · Truth-engine authority contract"` |
    93	
    94	(R2 expanded count: 26 REWRITE rows after dedup of #5/#6 with their HTML siblings,
    95	plus 4 R2 accessibility/hover names = **30 row IDs / ~26 distinct surfaces**.
    96	Tier-A trigger remains satisfied; copy_diff_lines now ≈ 50.)
    97	
    98	---
    99	
   100	## 3. Out of scope (explicitly deferred — surface-honesty closure)
   101	
   102	E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
   103	following surfaces remain English-only and are **deferred to future sub-phases
   104	or constitutional decisions**, not silently included:
   105	
   106	| Deferred surface | Why deferred | File:Line |
   107	|------------------|--------------|-----------|
   108	| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
   109	| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
   110	| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
   111	| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
   112	| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |

exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '380,408p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   380	        "手动反馈覆盖仅作参考",
   381	        "反馈模式信任说明",
   382	        "隐藏本次会话的信任提示横幅",
   383	        "真值引擎权限契约",
   384	    ]
   385	    for backend in backend_paths:
   386	        text = backend.read_text(encoding="utf-8")
   387	        for phrase in e11_15e_chinese:
   388	            assert phrase not in text, (
   389	                f"E11-15e display copy {phrase!r} unexpectedly leaked into "
   390	                f"backend file {backend.relative_to(repo_root)} — "
   391	                "truth-engine red-line breach"
   392	            )

exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '84,170p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
    95	        # WOW h3 direction flips (3) — strict Chinese-first per E11-15c
    96	        # convention; R2 P3 IMPORTANT closure: wow_b switched from
    97	        # `1000-trial 可靠性` (English token leading) to fully Chinese
    98	        # `1000 次试验可靠性`.
    99	        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
   100	        '<h3 id="workbench-wow-b-title">1000 次试验可靠性 · Monte Carlo</h3>',
   101	        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
   102	        # State-of-world labels (4) + advisory flag (1, R2 P3 IMPORTANT
   103	        # closure: outer middot reserved for Chinese/English split, inner
   104	        # Chinese clause now uses comma instead of an extra middot).
   105	        "真值引擎 SHA · truth-engine SHA",
   106	        "最近 e2e · recent e2e",
   107	        "对抗样本 · adversarial",
   108	        "未关闭问题 · open issues",
   109	        "仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading",
   110	        # Trust banner body (3) — R2 P3 NIT closure: native phrasing
   111	        # tightened (`此处`, `不属于"手动反馈"`, `仍以真值引擎读数为准`).
   112	        '此处"手动反馈"的含义 · What "manual feedback" means here:',
   113	        "该模式仅作参考 · That mode is advisory.",
   114	        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings",
   115	        # Trust banner dismiss (1)
   116	        "隐藏（本次会话）· Hide for session",
   117	        # Authority banner headline (1) — R2 P3 IMPORTANT closure: outer
   118	        # middot reserved for Chinese/English split; inner Chinese clause
   119	        # uses parentheses instead of an extra middot.
   120	        "真值引擎（只读）· Truth Engine — Read Only",
   121	        # Accessibility / hover names (R2 P1 NIT + P3 IMPORTANT closure):
   122	        # the feedback-mode title attribute and three aria-labels were
   123	        # English-only at R1 and broke surface-honesty pledge.
   124	        'title="手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative."',
   125	        'aria-label="反馈模式信任说明 · Feedback mode trust affordance"',
   126	        'aria-label="隐藏本次会话的信任提示横幅 · Hide trust banner for this session"',
   127	        'aria-label="真值引擎权限契约 · Truth-engine authority contract"',
   128	        # Pre-hydration boot placeholders (3)
   129	        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
   130	        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
   131	        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
   132	        # Reference-packet intro (1)
   133	        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
   134	        # Inbox empty state (1)
   135	        "暂无已提交提案 · No proposals submitted yet.",
   136	        # Pending sign-off (1)
   137	        "等待 Kogami 签字 · Pending Kogami sign-off",
   138	    ],
   139	)
   140	def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
   141	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   142	    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"
   143	
   144	
   145	# ─── 2. Stale English-only surfaces are gone ─────────────────────────
   146	
   147	
   148	@pytest.mark.parametrize(
   149	    "stale",
   150	    [
   151	        # Bare topbar chip labels (no Chinese prefix) — must be replaced
   152	        "<span>Identity</span>",
   153	        "<span>Ticket</span>",
   154	        "<span>Feedback Mode</span>",
   155	        "<span>System</span>",
   156	        "<strong>Manual (advisory)</strong>",
   157	        # WOW h3 stale English-first ordering (E11-15c convention)
   158	        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
   159	        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
   160	        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
   161	        # R2 P3 IMPORTANT: also forbid the R1 mid-Chinese English-token
   162	        # leading form `1000-trial 可靠性 · Monte Carlo`.
   163	        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
   164	        # Bare state-of-world labels (no Chinese prefix)
   165	        ">truth-engine SHA<",
   166	        ">recent e2e<",
   167	        ">adversarial<",
   168	        ">open issues<",
   169	        # Bare trust-banner body lines — these are now sentence-internal
   170	        # so we look for the line-leading position they used to hold.

codex
I have the row table and the guard list side by side now. I’m running the targeted E11-15e test file once so the approval is based on both diff inspection and the actual guard execution in this checkout.
exec
/bin/zsh -lc 'pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 749ms:
........................................................................ [ 90%]
........                                                                 [100%]
80 passed in 0.58s

codex
I’ve finished the closure check. No new red-line issue showed up in the R2 slice; I’m just grabbing the exact memory lines I consulted so the final note can cite them cleanly.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '96,106p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    96	- Symptom: `tmp_pack_*` cleanup does not stick or space keeps growing -> cause: a live GUI-spawned `git add` keeps repopulating the accidental home repo -> fix: stop the writer and atomically rename `.git` out of the way before cleanup [Task 1][Task 2]
    97	- Symptom: a long one-shot backup/cleanup script flakes out mid-run -> cause: too much work is bundled around a moving `.git` target -> fix: split the work into smaller commands after the `.git` rename [Task 2]
    98	- Symptom: cache removal partially fails with `Directory not empty` -> cause: nested cache subtrees were still present after the first broad delete -> fix: rerun targeted `rm -rf` on the remaining subdirectories and re-measure afterwards [Task 2]
    99	
   100	# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
   101	
   102	scope: Audit repo/GitHub/Notion drift, tighten source-of-truth framing, and hand off a governance-first Chinese execution package to Claude Code without silently turning analysis into code edits.
   103	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
   104	
   105	## Task 1: Audit repo, GitHub Actions, and Notion/control-plane drift before proposing project repositioning
   106	

codex
APPROVE

No findings. R1 IMPORTANT #1 is closed: Section 7 in [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:307) now includes the previously missing trust-banner truth sentence, the `diff / review` inner phrase, the JS-only `真值引擎 · Truth Engine` label, and the four new R2 accessibility Chinese strings. Against the declared 30-row surface set in [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:61), each row is covered by an exact anchor or an anchored substring.

R1 IMPORTANT #2 is closed: the backend guard now walks `src/well_harness/adapters/**/*.py` via `rglob("*.py")` and hard-fails if no adapter file is found in [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:329). `git diff main..9184c6d -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py` is empty, the JS lockstep label is still aligned at [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3788), and I reran `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py`: `80 passed in 0.58s`.


tokens used
70,998
APPROVE

No findings. R1 IMPORTANT #1 is closed: Section 7 in [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:307) now includes the previously missing trust-banner truth sentence, the `diff / review` inner phrase, the JS-only `真值引擎 · Truth Engine` label, and the four new R2 accessibility Chinese strings. Against the declared 30-row surface set in [E11-15e-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:61), each row is covered by an exact anchor or an anchored substring.

R1 IMPORTANT #2 is closed: the backend guard now walks `src/well_harness/adapters/**/*.py` via `rglob("*.py")` and hard-fails if no adapter file is found in [tests/test_workbench_e11_15e_chinese_first_bundle.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:329). `git diff main..9184c6d -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/ src/well_harness/demo_server.py` is empty, the JS lockstep label is still aligned at [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3788), and I reran `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py`: `80 passed in 0.58s`.


