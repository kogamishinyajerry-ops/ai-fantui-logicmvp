2026-04-26T01:20:33.510178Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T01:20:33.510235Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc75f-bce7-7c82-9d93-827a69d0dcb0
--------
user
You are Codex GPT-5.4 acting as **Persona P4 — V&V Engineer** (Tier-B single-persona pipeline, E11-15c sub-phase).

# Context — E11-15c closure of P3 NITs

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15c-column-h2-flip-eyebrow-dedup-20260426`
**PR:** #26
**Worktree HEAD:** `938a5a2` (single commit on top of main `62e58fb`)

## What E11-15c ships

Direct closure of the 2 NITs raised by P3 Demo Presenter on E11-15b (`persona-P3-E11-15b-output.md:165-167`).

| File:Line | Before | After | Closes |
|---|---|---|---|
| `workbench.html:17` | eyebrow `控制逻辑工作台` | `工程师工作区` | NIT #1 (h1 + eyebrow duplication) |
| `workbench.html:275` | h2 `Probe & Trace · 探针与追踪` | `探针与追踪 · Probe & Trace` | NIT #2 (direction asymmetry) |
| `workbench.html:295` | h2 `Annotate & Propose · 标注与提案` | `标注与提案 · Annotate & Propose` | NIT #2 |
| `workbench.html:315` | h2 `Hand off & Track · 移交与跟踪` | `移交与跟踪 · Hand off & Track` | NIT #2 |

## Files in scope

- `src/well_harness/static/workbench.html` — 4 strings flipped
- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated (param values + live-route check) for new Chinese-first column h2 strings
- `tests/test_workbench_chinese_eyebrow_sweep.py` — page-eyebrow lock updated from `控制逻辑工作台` to `工程师工作区`; truth-engine token list + live-route check updated to add `工程师工作区` while keeping `控制逻辑工作台` (still served via h1 substring)
- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

## Your specific lens (P4 V&V Engineer)

This is the highest-stakes lens for THIS sub-phase, because we are touching test contracts that prior sub-phases (E11-03, E11-15) locked. The V&V question is: **did we preserve every invariant the prior contracts intended, or did the contract migration accidentally weaken something?**

Focus on:
- **Contract migration completeness**: For every test we updated in lockstep with HTML, verify the new assertion is at least as strong as the old one. (E.g., E11-03 locked the EXACT bilingual h2 string; we changed direction — is the new assertion still locking the exact full string?)
- **Eyebrow-vs-h1 invariant strength**: `test_eyebrow_and_h1_are_not_chinese_duplicates` is a NEW programmatic invariant that closes NIT #1. Does it actually catch any future regression where someone re-introduces duplication, or could it be silently bypassed (e.g., by adding whitespace, by changing the markup structure such that the parser fails open)?
- **English suffix preservation**: 4 substring locks (e.g., `Probe & Trace</h2>`) are claimed preserved. Verify by independent grep.
- **Live-route ↔ static-source agreement**: the live `/workbench` route should serve exactly what the static file contains. Spot-check one path live.
- **Truth-engine isolation**: the new `工程师工作区` and `探针与追踪 · Probe` strings must not leak into demo_server.py / controller.py / runner.py / models.py / workbench.js / workbench.css. The new test #15 covers this; verify the test's negative assertions are correct (i.e., grep the actual files yourself).
- **Cross-contract compatibility**: did E11-15b's contracts (h1 bilingual, button bilingualization, API isolation) survive intact? Spot-check `tests/test_workbench_chinese_h2_button_sweep.py` and `tests/test_workbench_role_affordance.py` still pass.
- **Translation/semantic coherence of `工程师工作区`**: is this the right meta-category for the page, or does it implicitly contradict the data-role of the chip below (`Kogami / Engineer`)? Could it be misread as "this page is only for the Engineer role" when in fact Kogami also uses it?

## Verification status

- 1078 / 1078 pytest pass (15 new in `test_workbench_chinese_direction_consistency.py`; full suite green)
- Adjacent suite (column_rename + chinese_eyebrow_sweep + chinese_h2_button_sweep + dual_route + shell + role_affordance) — 126/126 pass.

## Out of scope (deliberately deferred)

- **Approval lane h3s + lane buttons** (`Pending`/`Accept`/`Reject`/`Accept Proposal`/`Reject Proposal`) — functional approval-flow strings.
- **API remediation message** in `demo_server.py:743` — backend contract.
- **`workbench.js` / `workbench.css`** — pure HTML+test sweep.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..938a5a2` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/` / `workbench.js` / `workbench.css` / `demo_server.py`.

Sign as: **P4 — V&V Engineer (Tier-B, E11-15c)**
codex
Reviewing PR #26 as P4 V&V Engineer. I’m starting with the prior repo-specific guidance and the exact diff/test surface so I can check whether the contract migration preserved strength instead of only following the green test result.
exec
/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|E11-15|workbench|eyebrow|direction consistency" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc 'git status --short && git branch --show-current && git rev-parse --short HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt
feat/e11-15c-column-h2-flip-eyebrow-dedup-20260426
938a5a2

codex
I’ve confirmed the requested branch/HEAD and pulled the repo-specific LogicMVP memory. Next I’m checking the exact diff, the affected tests, and one live `/workbench` probe to see whether the migration preserved contract strength rather than just keeping the suite green.
P4 review plan focused on invariant preservation and contract strength.
  → Inspect branch diff and changed files against stated red-line scope
  • Read affected HTML and tests to evaluate contract migration strength
  • Run targeted verification including grep and at least one live /workbench probe
  • Draft verdict with severity-ordered findings and residual nits
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,380p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    26	          <span>Identity</span>
    27	          <strong>Kogami / Engineer</strong>
    28	        </div>
    29	        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
    30	          <span>Ticket</span>
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
    41	          <span>Feedback Mode</span>
    42	          <strong>Manual (advisory)</strong>
    43	          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
    44	        </div>
    45	        <label class="workbench-collab-system" for="workbench-system-select">
    46	          <span>System</span>
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
    65	          <span class="workbench-sow-label">truth-engine SHA</span>
    66	          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
    67	        </span>
    68	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    69	        <span class="workbench-sow-field" data-sow-field="recent_e2e"
    70	              title="docs/coordination/qa_report.md (most recent test run)">
    71	          <span class="workbench-sow-label">recent e2e</span>
    72	          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
    73	        </span>
    74	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    75	        <span class="workbench-sow-field" data-sow-field="adversarial"
    76	              title="docs/coordination/qa_report.md (shared validation)">
    77	          <span class="workbench-sow-label">adversarial</span>
    78	          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
    79	        </span>
    80	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    81	        <span class="workbench-sow-field" data-sow-field="known_issues"
    82	              title="docs/known-issues/ file count">
    83	          <span class="workbench-sow-label">open issues</span>
    84	          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
    85	        </span>
    86	        <span class="workbench-sow-flag" aria-hidden="false">
    87	          advisory · not a live truth-engine reading
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
   111	              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
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
   143	              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
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
   173	              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
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
   209	            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
   210	            an observed reading — for example, editing a snapshot input field before running a scenario.
   211	            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
   212	          </span>
   213	          <strong>That mode is advisory.</strong>
   214	          <span>
   215	            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   216	            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   217	          </span>
   218	        </div>
   219	        <button
   220	          type="button"
   221	          class="workbench-trust-banner-dismiss"
   222	          aria-label="Hide trust banner for this session"
   223	          data-trust-banner-dismiss
   224	        >
   225	          Hide for session
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
   248	          Truth Engine — Read Only
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
   278	            Waiting for probe &amp; trace panel boot.
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
   298	            Waiting for annotate &amp; propose panel boot.
   299	          </div>
   300	          <div class="workbench-collab-document">
   301	            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
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
   318	            Waiting for hand off &amp; track panel boot.
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
   337	          <li>No proposals submitted yet.</li>
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
   363	          <strong>Pending Kogami sign-off</strong>
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

exec
/bin/zsh -lc 'git diff --name-only main..938a5a2' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
tests/test_workbench_chinese_direction_consistency.py
tests/test_workbench_chinese_eyebrow_sweep.py
tests/test_workbench_column_rename.py

exec
/bin/zsh -lc "git diff --stat main..938a5a2 && printf '\\n---\\n' && git diff --unified=0 main..938a5a2 -- src/well_harness/static/workbench.html tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_direction_consistency.py .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-15c-SURFACE-INVENTORY.md                   |  80 +++++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/static/workbench.html             |   8 +-
 ...test_workbench_chinese_direction_consistency.py | 184 +++++++++++++++++++++
 tests/test_workbench_chinese_eyebrow_sweep.py      |  12 +-
 tests/test_workbench_column_rename.py              |  16 +-
 6 files changed, 288 insertions(+), 13 deletions(-)

---
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..ec83650
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
@@ -0,0 +1,80 @@
+# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup
+
+> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
+>
+> Direct closure of the 2 NITs raised by P3 Demo Presenter on E11-15b
+> (`persona-P3-E11-15b-output.md:165-167`).
+
+## NIT closure summary
+
+| P3 NIT | Fix |
+|---|---|
+| #1: page eyebrow `控制逻辑工作台` immediately followed by h1 `控制逻辑工作台 · Control Logic Workbench` reads redundantly | Eyebrow flipped to `工程师工作区` so eyebrow + h1 read as category + title (two distinct semantic levels) |
+| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
+
+## Surface diff inventory
+
+| # | Surface | Type | Anchor | Notes |
+|---|---|---|---|---|
+| 1 | Page eyebrow `控制逻辑工作台` → `工程师工作区` | [REWRITE] | `workbench.html:17` | Closes P3 NIT #1; eyebrow now reads as engineer-workspace sub-category, h1 stays as page title. |
+| 2 | Column h2 `Probe & Trace · 探针与追踪` → `探针与追踪 · Probe & Trace` | [REWRITE] | `workbench.html:275` | Closes P3 NIT #2; English suffix preserved for substring locks. |
+| 3 | Column h2 `Annotate & Propose · 标注与提案` → `标注与提案 · Annotate & Propose` | [REWRITE] | `workbench.html:295` | Same. |
+| 4 | Column h2 `Hand off & Track · 移交与跟踪` → `移交与跟踪 · Hand off & Track` | [REWRITE] | `workbench.html:315` | Same. |
+
+## Test contract updates (existing files touched in lockstep)
+
+- `tests/test_workbench_column_rename.py`: 2 assertion blocks updated
+  to expect Chinese-first column h2s (param values + live-route check).
+- `tests/test_workbench_chinese_eyebrow_sweep.py`: page eyebrow lock
+  updated from `控制逻辑工作台` to `工程师工作区`; truth-engine
+  spot-check token list and live-route check updated to add
+  `工程师工作区` while keeping `控制逻辑工作台` as a substring (still
+  served via h1).
+- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
+  positive locks for new strings, negative locks for stale, English suffix
+  preservation, eyebrow-vs-h1 non-duplication invariant, live-served route,
+  truth-engine isolation.
+
+## Tier-trigger evaluation
+
+Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
+
+> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
+
+- **copy_diff_lines** = 4 → < 10
+- **[REWRITE/DELETE] count** = 4 → ≥ 3
+
+→ **Tier-B** (1-persona review). The first threshold (≥10) fails.
+
+> **Verdict: Tier-B**. Persona = **P4 (V&V Engineer)** — round-robin
+> successor of E11-15b's P3 AND content-fit: this sub-phase rewrites
+> existing test contracts in lockstep with HTML changes, so the V&V
+> lens (verifying invariants are preserved across the contract migration)
+> is exactly right.
+
+## Behavior contract (locked by tests)
+
+`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
+
+1. 3 column h2s positively asserted Chinese-first.
+2. 3 stale English-first column h2 strings asserted absent.
+3. Page eyebrow positively asserted as `工程师工作区`; old `控制逻辑工作台` eyebrow asserted absent.
+4. h1 still carries `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` (E11-15b contract preserved).
+5. Programmatic invariant: extracted eyebrow inner text != extracted h1 Chinese half — locks the dedup property.
+6. 4 English suffixes preserved (`Probe & Trace</h2>`, etc.).
+7. Live-served `/workbench` route serves all new strings.
+8. Truth-engine isolation: new Chinese strings absent from `demo_server.py`/`controller.py`/`runner.py`/`models.py`/`workbench.js`/`workbench.css`.
+
+## Truth-engine red line
+
+Files touched:
+- `src/well_harness/static/workbench.html` — 4 strings flipped
+- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated
+- `tests/test_workbench_chinese_eyebrow_sweep.py` — eyebrow + truth-engine token list + live-route assertions updated
+- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
+- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended
+
+Files NOT touched: `controller.py`, `runner.py`, `models.py`,
+`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
+`demo_server.py`. Truth-engine boundary preserved.
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index 303459d..242fd4a 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -20,0 +21 @@ E11-15b: Tier-B (7 copy_diff_lines, 7 [REWRITE] — fails ≥10 copy_diff thresh
+E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 90f44c3..12a457a 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -17 +17 @@
-          <p class="eyebrow">控制逻辑工作台</p>
+          <p class="eyebrow">工程师工作区</p>
@@ -275 +275 @@
-            <h2>Probe &amp; Trace · 探针与追踪</h2>
+            <h2>探针与追踪 · Probe &amp; Trace</h2>
@@ -295 +295 @@
-            <h2>Annotate &amp; Propose · 标注与提案</h2>
+            <h2>标注与提案 · Annotate &amp; Propose</h2>
@@ -315 +315 @@
-            <h2>Hand off &amp; Track · 移交与跟踪</h2>
+            <h2>移交与跟踪 · Hand off &amp; Track</h2>
diff --git a/tests/test_workbench_chinese_direction_consistency.py b/tests/test_workbench_chinese_direction_consistency.py
new file mode 100644
index 0000000..83725fe
--- /dev/null
+++ b/tests/test_workbench_chinese_direction_consistency.py
@@ -0,0 +1,184 @@
+"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
+
+Two NIT closures from E11-15b (P3 Demo Presenter):
+
+NIT #1 — h1 + eyebrow duplication
+    `<p class="eyebrow">控制逻辑工作台</p>` immediately followed by
+    `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` reads redundantly.
+    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
+    eyebrow + h1 read as category + title.
+
+NIT #2 — direction asymmetry
+    Column-trio h2s were English-first (`Probe & Trace · 探针与追踪`)
+    while the rest of the page is Chinese-first. E11-15c flips them
+    to `<中文> · <English>` for full-page direction consistency.
+
+Net change is 4 [REWRITE] lines in workbench.html. Existing test files
+test_workbench_column_rename and test_workbench_chinese_eyebrow_sweep
+were updated in lockstep with the new strings.
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
+# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
+
+
+@pytest.mark.parametrize(
+    "chinese_first_h2",
+    [
+        "<h2>探针与追踪 · Probe &amp; Trace</h2>",
+        "<h2>标注与提案 · Annotate &amp; Propose</h2>",
+        "<h2>移交与跟踪 · Hand off &amp; Track</h2>",
+    ],
+)
+def test_column_h2_is_chinese_first(chinese_first_h2: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
+
+
+@pytest.mark.parametrize(
+    "stale_english_first_h2",
+    [
+        "<h2>Probe &amp; Trace · 探针与追踪</h2>",
+        "<h2>Annotate &amp; Propose · 标注与提案</h2>",
+        "<h2>Hand off &amp; Track · 移交与跟踪</h2>",
+    ],
+)
+def test_stale_english_first_column_h2_removed(stale_english_first_h2: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale_english_first_h2 not in html, (
+        f"stale English-first column h2 still present: {stale_english_first_h2}"
+    )
+
+
+# ─── 2. NIT #1: page eyebrow + h1 are no longer duplicates ───────────
+
+
+def test_page_eyebrow_is_engineer_workspace_not_h1_duplicate() -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert '<p class="eyebrow">工程师工作区</p>' in html
+    assert '<p class="eyebrow">控制逻辑工作台</p>' not in html
+
+
+def test_h1_still_carries_full_bilingual_title() -> None:
+    """E11-15b's h1 bilingualization must survive E11-15c — only the
+    sibling eyebrow changes; the h1 stays as the page-title source of
+    truth."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert "<h1>控制逻辑工作台 · Control Logic Workbench</h1>" in html
+
+
+def test_eyebrow_and_h1_are_not_chinese_duplicates() -> None:
+    """Closure of P3's NIT #1: extracting the eyebrow's Chinese and the
+    h1's Chinese, they must not match."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    eyebrow_inner = (
+        html.split('<div class="workbench-collab-brand">')[1]
+        .split('<p class="eyebrow">')[1]
+        .split("</p>")[0]
+    )
+    h1_inner = html.split("<h1>")[1].split("</h1>")[0]
+    h1_chinese = h1_inner.split(" · ")[0]
+    assert eyebrow_inner != h1_chinese, (
+        f"eyebrow ({eyebrow_inner!r}) duplicates h1 Chinese ({h1_chinese!r}) — "
+        "P3 NIT #1 not closed"
+    )
+
+
+# ─── 3. English suffixes preserved (no regression on substring locks) ─
+
+
+@pytest.mark.parametrize(
+    "preserved_english_suffix",
+    [
+        "Probe &amp; Trace</h2>",
+        "Annotate &amp; Propose</h2>",
+        "Hand off &amp; Track</h2>",
+        "Control Logic Workbench</h1>",
+    ],
+)
+def test_e11_15c_preserves_english_suffix(preserved_english_suffix: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert preserved_english_suffix in html, (
+        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
+    )
+
+
+# ─── 4. Live-served route reflects E11-15c ───────────────────────────
+
+
+def test_workbench_route_reflects_direction_flip(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    assert "探针与追踪 · Probe" in html
+    assert "标注与提案 · Annotate" in html
+    assert "移交与跟踪 · Hand off" in html
+    assert "工程师工作区" in html
+
+
+# ─── 5. Truth-engine red line ────────────────────────────────────────
+
+
+def test_e11_15c_only_touches_static_html_and_tests() -> None:
+    """The fix is HTML + test-only. Demo server, controller, runner,
+    models, adapters, JS, and CSS must NOT carry the new strings."""
+    repo_root = Path(__file__).resolve().parents[1]
+    backend_files = [
+        repo_root / "src" / "well_harness" / "demo_server.py",
+        repo_root / "src" / "well_harness" / "controller.py",
+        repo_root / "src" / "well_harness" / "runner.py",
+        repo_root / "src" / "well_harness" / "models.py",
+    ]
+    for f in backend_files:
+        if not f.exists():
+            continue
+        content = f.read_text(encoding="utf-8")
+        for new_string in ["工程师工作区", "探针与追踪 · Probe"]:
+            assert new_string not in content, (
+                f"E11-15c string {new_string!r} unexpectedly leaked into {f.name}"
+            )
+
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
+    for new_string in ["工程师工作区"]:
+        assert new_string not in js
+        assert new_string not in css
diff --git a/tests/test_workbench_chinese_eyebrow_sweep.py b/tests/test_workbench_chinese_eyebrow_sweep.py
index 2abec09..190a5ed 100644
--- a/tests/test_workbench_chinese_eyebrow_sweep.py
+++ b/tests/test_workbench_chinese_eyebrow_sweep.py
@@ -60 +60,4 @@ def server():
-        '<p class="eyebrow">控制逻辑工作台</p>',
+        # E11-15c: page eyebrow changed from `控制逻辑工作台` (which
+        # duplicated the h1) to `工程师工作区` so eyebrow + h1 read as
+        # category + title rather than two copies of the same phrase.
+        '<p class="eyebrow">工程师工作区</p>',
@@ -142,0 +146,5 @@ def test_workbench_route_serves_chinese_eyebrows(server) -> None:
+    # E11-15c: page eyebrow flipped to `工程师工作区`; the literal
+    # `控制逻辑工作台` is still served via the h1 (`控制逻辑工作台 ·
+    # Control Logic Workbench`), so we still assert it as a substring
+    # of the served page.
+    assert "工程师工作区" in html
@@ -160 +168 @@ def test_e11_15_only_touches_static_html() -> None:
-    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
+    for chinese in ["工程师工作区", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
diff --git a/tests/test_workbench_column_rename.py b/tests/test_workbench_column_rename.py
index c0b0b15..a049107 100644
--- a/tests/test_workbench_column_rename.py
+++ b/tests/test_workbench_column_rename.py
@@ -64,3 +64,5 @@ def server():
-        "Probe &amp; Trace · 探针与追踪",
-        "Annotate &amp; Propose · 标注与提案",
-        "Hand off &amp; Track · 移交与跟踪",
+        # E11-15c flipped to Chinese-first to match the rest of the page;
+        # English suffix preserved so substring locks still pass.
+        "探针与追踪 · Probe &amp; Trace",
+        "标注与提案 · Annotate &amp; Propose",
+        "移交与跟踪 · Hand off &amp; Track",
@@ -229,4 +231,4 @@ def test_workbench_route_serves_renamed_columns(server) -> None:
-    # New copy
-    assert "Probe &amp; Trace · 探针与追踪" in html
-    assert "Annotate &amp; Propose · 标注与提案" in html
-    assert "Hand off &amp; Track · 移交与跟踪" in html
+    # E11-15c flipped these from English-first to Chinese-first.
+    assert "探针与追踪 · Probe &amp; Trace" in html
+    assert "标注与提案 · Annotate &amp; Propose" in html
+    assert "移交与跟踪 · Hand off &amp; Track" in html

codex
The diff is as narrow as claimed: only HTML, tests, and planning artifacts changed, with no truth-engine file edits in `main..938a5a2`. I’m now reading the changed tests plus the adjacent E11-15b contracts to see whether any assertion got weaker during the string migration.
exec
/bin/zsh -lc "nl -ba tests/test_workbench_column_rename.py | sed -n '1,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-03 — three-column rename regression lock.
     2	
     3	Locks the visible column titles, eyebrows, and boot status copy after
     4	the E11-03 rename from technical nouns to engineer-task verbs:
     5	
     6	  Scenario Control          → Probe & Trace · 探针与追踪
     7	  Spec Review Surface       → Annotate & Propose · 标注与提案
     8	  Logic Circuit Surface     → Hand off & Track · 移交与跟踪
     9	
    10	Per E11-00-PLAN row E11-03: underlying IDs (data-column, panel ids,
    11	data-annotation-surface) are intentionally stable so e2e selectors and
    12	JS boot wiring don't break. Verify both invariants — new copy AND
    13	preserved IDs — so a future "polish" pass can't silently regress
    14	either side.
    15	"""
    16	
    17	from __future__ import annotations
    18	
    19	import http.client
    20	import threading
    21	from http.server import ThreadingHTTPServer
    22	from pathlib import Path
    23	
    24	import pytest
    25	
    26	from well_harness.demo_server import DemoRequestHandler
    27	
    28	
    29	REPO_ROOT = Path(__file__).resolve().parents[1]
    30	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    31	
    32	
    33	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    34	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    35	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    36	    thread.start()
    37	    return server, thread
    38	
    39	
    40	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    41	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    42	    connection.request("GET", path)
    43	    response = connection.getresponse()
    44	    return response.status, response.read().decode("utf-8")
    45	
    46	
    47	@pytest.fixture
    48	def server():
    49	    s, t = _start_demo_server()
    50	    try:
    51	        yield s
    52	    finally:
    53	        s.shutdown()
    54	        s.server_close()
    55	        t.join(timeout=2)
    56	
    57	
    58	# ─── 1. New visible copy is present ──────────────────────────────────
    59	
    60	
    61	@pytest.mark.parametrize(
    62	    "title",
    63	    [
    64	        # E11-15c flipped to Chinese-first to match the rest of the page;
    65	        # English suffix preserved so substring locks still pass.
    66	        "探针与追踪 · Probe &amp; Trace",
    67	        "标注与提案 · Annotate &amp; Propose",
    68	        "移交与跟踪 · Hand off &amp; Track",
    69	    ],
    70	)
    71	def test_workbench_html_carries_new_column_title(title: str) -> None:
    72	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    73	    assert title in html, f"missing renamed column title: {title}"
    74	
    75	
    76	@pytest.mark.parametrize(
    77	    "eyebrow",
    78	    ["probe &amp; trace", "annotate &amp; propose", "hand off &amp; track"],
    79	)
    80	def test_workbench_html_carries_new_eyebrow(eyebrow: str) -> None:
    81	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    82	    assert eyebrow in html, f"missing renamed eyebrow: {eyebrow}"
    83	
    84	
    85	# ─── 2. Old technical-noun copy removed ──────────────────────────────
    86	
    87	
    88	@pytest.mark.parametrize(
    89	    "stale",
    90	    [
    91	        "<h2>Scenario Control</h2>",
    92	        "<h2>Spec Review Surface</h2>",
    93	        "<h2>Logic Circuit Surface</h2>",
    94	        ">control panel<",
    95	        ">document<",
    96	        ">circuit<",
    97	        "Waiting for control panel boot.",
    98	        "Waiting for document panel boot.",
    99	        "Waiting for circuit panel boot.",
   100	    ],
   101	)
   102	def test_workbench_html_does_not_carry_stale_column_title(stale: str) -> None:
   103	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   104	    assert stale not in html, f"stale technical-noun copy still present: {stale}"
   105	
   106	
   107	# ─── 2b. New pre-hydration boot-status copy is POSITIVELY locked ──────
   108	#
   109	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
   110	# pre-hydration "Waiting for ... panel boot." strings. R1 only verified
   111	# absence of the stale copy; R2 also asserts presence of the new copy
   112	# so a drift to any other phrasing would fail the suite.
   113	
   114	
   115	@pytest.mark.parametrize(
   116	    "boot_status",
   117	    [
   118	        "Waiting for probe &amp; trace panel boot.",
   119	        "Waiting for annotate &amp; propose panel boot.",
   120	        "Waiting for hand off &amp; track panel boot.",
   121	    ],
   122	)
   123	def test_workbench_html_carries_new_boot_status(boot_status: str) -> None:
   124	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   125	    assert boot_status in html, f"missing renamed pre-hydration boot status: {boot_status}"
   126	
   127	
   128	# ─── 3. Underlying IDs / data attributes preserved ──────────────────
   129	#
   130	# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
   131	# panel ids, data-column tokens, data-annotation-surface tokens, and
   132	# status div ids are anchors for e2e selectors and JS boot wiring, so
   133	# they MUST stay stable through the rename.
   134	
   135	
   136	@pytest.mark.parametrize(
   137	    "anchor",
   138	    [
   139	        'id="workbench-control-panel"',
   140	        'id="workbench-document-panel"',
   141	        'id="workbench-circuit-panel"',
   142	        'data-column="control"',
   143	        'data-column="document"',
   144	        'data-column="circuit"',
   145	        'data-annotation-surface="control"',
   146	        'data-annotation-surface="document"',
   147	        'data-annotation-surface="circuit"',
   148	        'id="workbench-control-status"',
   149	        'id="workbench-document-status"',
   150	        'id="workbench-circuit-status"',
   151	    ],
   152	)
   153	def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
   154	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   155	    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"
   156	
   157	
   158	# ─── 4. JS boot status copy matches new column names ────────────────
   159	
   160	
   161	# P4 R1 NIT fix: lock the FULL hydrated boot-status sentence (not just
   162	# the "X ready" prefix), so future drift in the staging note is also
   163	# caught. P5 R1 IMPORTANT fix: the strings must NOT contain internal
   164	# roadmap tokens like "E07+" or "E07".
   165	
   166	
   167	@pytest.mark.parametrize(
   168	    "boot_copy",
   169	    [
   170	        "Probe & Trace ready. Scenario actions are staged for the next bundle.",
   171	        "Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
   172	        "Hand off & Track ready. Overlay annotation is staged for the next bundle.",
   173	    ],
   174	)
   175	def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
   176	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   177	    assert boot_copy in js, f"workbench.js boot status missing exact string: {boot_copy}"
   178	
   179	
   180	def test_workbench_js_boot_status_drops_stale_names() -> None:
   181	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   182	    # Old boot copy must NOT appear, otherwise the visible chrome and the
   183	    # status messages will disagree.
   184	    assert "Control panel ready" not in js
   185	    assert "Document panel ready" not in js
   186	    assert "Circuit panel ready" not in js
   187	
   188	
   189	def test_workbench_js_boot_status_drops_internal_phase_tokens() -> None:
   190	    """P5 R1 IMPORTANT fix: roadmap tokens like 'E07+'/'E07' must not
   191	    leak into user-visible boot status strings."""
   192	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   193	    # Scope the check to the three boot functions to avoid false
   194	    # positives in unrelated comments/blocks.
   195	    for fn in (
   196	        "bootWorkbenchControlPanel",
   197	        "bootWorkbenchDocumentPanel",
   198	        "bootWorkbenchCircuitPanel",
   199	    ):
   200	        anchor = js.find(f"function {fn}")
   201	        assert anchor != -1, f"missing function {fn}"
   202	        slice_ = js[anchor : anchor + 600]
   203	        assert "E07" not in slice_, (
   204	            f"internal phase token 'E07' leaked into {fn} boot status"
   205	        )
   206	
   207	
   208	# P1 R1 NIT fix: failure-path fallback must use the engineer-task verb,
   209	# not the internal columnName token.
   210	
   211	
   212	def test_workbench_js_failure_fallback_uses_task_verb_label() -> None:
   213	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   214	    # WORKBENCH_COLUMN_LABEL maps control/document/circuit → task verbs
   215	    assert "WORKBENCH_COLUMN_LABEL" in js
   216	    assert '"control": "Probe & Trace"' in js or 'control: "Probe & Trace"' in js
   217	    assert '"document": "Annotate & Propose"' in js or 'document: "Annotate & Propose"' in js
   218	    assert '"circuit": "Hand off & Track"' in js or 'circuit: "Hand off & Track"' in js
   219	    # Failure copy must reference the label, not the raw columnName.
   220	    assert "${label} panel failed independently" in js, (
   221	        "failure fallback should use the engineer-task verb label, not the raw column token"
   222	    )
   223	
   224	
   225	# ─── 5. Live-served /workbench reflects the rename end-to-end ───────
   226	
   227	
   228	def test_workbench_route_serves_renamed_columns(server) -> None:
   229	    status, html = _get(server, "/workbench")
   230	    assert status == 200
   231	    # E11-15c flipped these from English-first to Chinese-first.
   232	    assert "探针与追踪 · Probe &amp; Trace" in html
   233	    assert "标注与提案 · Annotate &amp; Propose" in html
   234	    assert "移交与跟踪 · Hand off &amp; Track" in html
   235	    # Stable anchors still served
   236	    assert 'id="workbench-control-panel"' in html
   237	    assert 'data-column="circuit"' in html

exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_eyebrow_sweep.py | sed -n '1,280p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_role_affordance.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15 — Chinese-first eyebrow sweep.
     2	
     3	The 5 eyebrow labels that did NOT carry a bilingual h2 below them are
     4	flipped from English-lowercase to pure Chinese, so that the page
     5	reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
     6	annotate & propose, hand off & track) are explicitly out of scope —
     7	they are positively locked by E11-03 tests and the bilingual h2 below
     8	each already provides Chinese-first signal.
     9	
    10	Default state preserves all existing IDs, classes, and h1/h2 strings.
    11	"""
    12	
    13	from __future__ import annotations
    14	
    15	import http.client
    16	import threading
    17	from http.server import ThreadingHTTPServer
    18	from pathlib import Path
    19	
    20	import pytest
    21	
    22	from well_harness.demo_server import DemoRequestHandler
    23	
    24	
    25	REPO_ROOT = Path(__file__).resolve().parents[1]
    26	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    27	
    28	
    29	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    30	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    31	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    32	    thread.start()
    33	    return server, thread
    34	
    35	
    36	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    37	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    38	    connection.request("GET", path)
    39	    response = connection.getresponse()
    40	    return response.status, response.read().decode("utf-8")
    41	
    42	
    43	@pytest.fixture
    44	def server():
    45	    s, t = _start_demo_server()
    46	    try:
    47	        yield s
    48	    finally:
    49	        s.shutdown()
    50	        s.server_close()
    51	        t.join(timeout=2)
    52	
    53	
    54	# ─── 1. New Chinese eyebrows are POSITIVELY locked ───────────────────
    55	
    56	
    57	@pytest.mark.parametrize(
    58	    "eyebrow_html",
    59	    [
    60	        # E11-15c: page eyebrow changed from `控制逻辑工作台` (which
    61	        # duplicated the h1) to `工程师工作区` so eyebrow + h1 read as
    62	        # category + title rather than two copies of the same phrase.
    63	        '<p class="eyebrow">工程师工作区</p>',
    64	        '<span class="workbench-sow-eyebrow">当前现状</span>',
    65	        '<p class="eyebrow">主流场景</p>',
    66	        '<p class="eyebrow">标注收件箱</p>',
    67	        '<p class="eyebrow">审批中心</p>',
    68	    ],
    69	)
    70	def test_workbench_html_carries_chinese_eyebrow(eyebrow_html: str) -> None:
    71	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    72	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
    73	
    74	
    75	# ─── 2. Old English-only eyebrows are gone ───────────────────────────
    76	
    77	
    78	@pytest.mark.parametrize(
    79	    "stale_eyebrow_html",
    80	    [
    81	        '<p class="eyebrow">control logic workbench</p>',
    82	        '<span class="workbench-sow-eyebrow">state of world</span>',
    83	        '<p class="eyebrow">canonical scenarios</p>',
    84	        '<p class="eyebrow">annotation inbox</p>',
    85	        '<p class="eyebrow">approval center</p>',
    86	    ],
    87	)
    88	def test_workbench_html_does_not_carry_stale_english_eyebrow(stale_eyebrow_html: str) -> None:
    89	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    90	    assert stale_eyebrow_html not in html, (
    91	        f"stale English-only eyebrow still present: {stale_eyebrow_html}"
    92	    )
    93	
    94	
    95	# ─── 3. Out-of-scope eyebrows (E11-03 column trio) are PRESERVED ─────
    96	
    97	
    98	@pytest.mark.parametrize(
    99	    "preserved_eyebrow",
   100	    [
   101	        '<p class="eyebrow">probe &amp; trace</p>',
   102	        '<p class="eyebrow">annotate &amp; propose</p>',
   103	        '<p class="eyebrow">hand off &amp; track</p>',
   104	    ],
   105	)
   106	def test_e11_03_column_eyebrows_preserved(preserved_eyebrow: str) -> None:
   107	    """E11-15 explicitly does NOT touch the column-trio eyebrows.
   108	    They live above bilingual h2s and are locked by test_workbench_column_rename."""
   109	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   110	    assert preserved_eyebrow in html, (
   111	        f"E11-03 column eyebrow accidentally removed by E11-15 sweep: {preserved_eyebrow}"
   112	    )
   113	
   114	
   115	# ─── 4. Anchors and h1/h2 strings preserved ──────────────────────────
   116	
   117	
   118	@pytest.mark.parametrize(
   119	    "anchor",
   120	    [
   121	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
   122	        # English suffix `Control Logic Workbench</h1>` is preserved as
   123	        # locked by test_workbench_dual_route.
   124	        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
   125	        # IDs of containing sections untouched
   126	        'id="workbench-state-of-world-bar"',
   127	        'id="workbench-wow-starters"',
   128	        'id="annotation-inbox"',
   129	        'id="approval-center-panel"',
   130	        # Class hooks untouched (CSS still binds)
   131	        'class="eyebrow"',
   132	        'class="workbench-sow-eyebrow"',
   133	    ],
   134	)
   135	def test_e11_15_preserves_structural_anchors(anchor: str) -> None:
   136	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   137	    assert anchor in html, f"E11-15 sweep accidentally broke structural anchor: {anchor}"
   138	
   139	
   140	# ─── 5. Live-served route reflects the sweep ─────────────────────────
   141	
   142	
   143	def test_workbench_route_serves_chinese_eyebrows(server) -> None:
   144	    status, html = _get(server, "/workbench")
   145	    assert status == 200
   146	    # E11-15c: page eyebrow flipped to `工程师工作区`; the literal
   147	    # `控制逻辑工作台` is still served via the h1 (`控制逻辑工作台 ·
   148	    # Control Logic Workbench`), so we still assert it as a substring
   149	    # of the served page.
   150	    assert "工程师工作区" in html
   151	    assert "控制逻辑工作台" in html
   152	    assert "当前现状" in html
   153	    assert "主流场景" in html
   154	    assert "标注收件箱" in html
   155	    assert "审批中心" in html
   156	
   157	
   158	# ─── 6. Truth-engine red line ────────────────────────────────────────
   159	
   160	
   161	def test_e11_15_only_touches_static_html() -> None:
   162	    """The sweep is HTML-only — no JS, no CSS, no controller, no adapter.
   163	    Verify by spot-checking that the 5 changed strings appear nowhere
   164	    else in code-bearing files."""
   165	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   166	    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
   167	    # The new Chinese strings live only in HTML, not JS or CSS.
   168	    for chinese in ["工程师工作区", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
   169	        assert chinese not in js, f"unexpected Chinese eyebrow leaked into workbench.js: {chinese}"
   170	        assert chinese not in css, f"unexpected Chinese eyebrow leaked into workbench.css: {chinese}"

 succeeded in 0ms:
     1	"""E11-08 — role affordance for non-Kogami identities.
     2	
     3	Per E11-00-PLAN row E11-08: when the workbench identity is NOT Kogami,
     4	the Approval Center entry button + panel must be replaced with an
     5	explicit "Pending Kogami sign-off" affordance rather than leaving
     6	disabled UI in place.
     7	
     8	Default state (Kogami identity): Approval Center visible, pending
     9	affordance hidden.
    10	Non-Kogami state: Approval Center hidden, pending affordance visible.
    11	
    12	The test locks both the static HTML invariants (data-identity-name
    13	attribute, hidden affordance section, applyRoleAffordance JS function)
    14	and the live-served route. The toggle behavior itself is exercised
    15	via static-source inspection rather than a headless browser; the
    16	JS function is small enough to be auditable by inspection.
    17	"""
    18	
    19	from __future__ import annotations
    20	
    21	import http.client
    22	import re
    23	import threading
    24	from http.server import ThreadingHTTPServer
    25	from pathlib import Path
    26	
    27	import pytest
    28	
    29	from well_harness.demo_server import DemoRequestHandler
    30	
    31	
    32	REPO_ROOT = Path(__file__).resolve().parents[1]
    33	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    34	
    35	
    36	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    37	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    38	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    39	    thread.start()
    40	    return server, thread
    41	
    42	
    43	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    44	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    45	    connection.request("GET", path)
    46	    response = connection.getresponse()
    47	    return response.status, response.read().decode("utf-8")
    48	
    49	
    50	@pytest.fixture
    51	def server():
    52	    s, t = _start_demo_server()
    53	    try:
    54	        yield s
    55	    finally:
    56	        s.shutdown()
    57	        s.server_close()
    58	        t.join(timeout=2)
    59	
    60	
    61	# ─── 1. Static HTML carries the new attributes + section ────────────
    62	
    63	
    64	def test_workbench_identity_chip_carries_data_identity_name() -> None:
    65	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    66	    assert 'data-identity-name="Kogami"' in html
    67	
    68	
    69	def test_workbench_html_has_pending_signoff_affordance_section() -> None:
    70	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    71	    assert 'id="workbench-pending-signoff-affordance"' in html
    72	    assert 'data-pending-signoff="hidden"' in html  # default hidden state
    73	    assert "Pending Kogami sign-off" in html
    74	
    75	
    76	def test_pending_signoff_affordance_explains_replacement_of_disabled_ui() -> None:
    77	    """The affordance copy must explain WHY the Approval Center is gone
    78	    for this user — otherwise users still see it as broken UI."""
    79	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    80	    affordance_block = (
    81	        html.split('id="workbench-pending-signoff-affordance"')[1].split(
    82	            "</section>"
    83	        )[0]
    84	    )
    85	    assert "Kogami" in affordance_block
    86	    assert "排队" in affordance_block or "提案" in affordance_block
    87	
    88	
    89	# ─── 2. CSS visibility contract ──────────────────────────────────────
    90	
    91	
    92	def test_pending_signoff_css_default_hidden_visible_toggle() -> None:
    93	    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    94	    # Default selector hides the affordance.
    95	    assert (
    96	        ".workbench-pending-signoff {" in css
    97	        and "display: none" in css.split(".workbench-pending-signoff {")[1].split("}")[0]
    98	    )
    99	    # Visible attribute selector reveals it.
   100	    assert (
   101	        '.workbench-pending-signoff[data-pending-signoff="visible"]' in css
   102	    )
   103	
   104	
   105	# ─── 3. JS contract ──────────────────────────────────────────────────
   106	
   107	
   108	def test_workbench_js_has_apply_role_affordance() -> None:
   109	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   110	    assert "function applyRoleAffordance" in js
   111	    assert "function setWorkbenchIdentity" in js
   112	    # window-export so tests / demo flow can call from outside the module
   113	    assert "window.setWorkbenchIdentity = setWorkbenchIdentity" in js
   114	
   115	
   116	def test_workbench_js_affordance_toggles_on_kogami_check() -> None:
   117	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   118	    # The toggle hinges on the literal "Kogami" string.
   119	    affordance_block = js.split("function applyRoleAffordance")[1].split(
   120	        "}\n\n"
   121	    )[0]
   122	    assert '"Kogami"' in affordance_block
   123	    # Both targets get toggled in lockstep.
   124	    assert "approval-center-entry" in affordance_block
   125	    assert "approval-center-panel" in affordance_block
   126	    assert "workbench-pending-signoff-affordance" in affordance_block
   127	
   128	
   129	def test_workbench_js_honors_url_identity_param() -> None:
   130	    """A `?identity=<name>` URL param flips the identity at boot."""
   131	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   132	    assert "URLSearchParams" in js
   133	    assert 'params.get("identity")' in js
   134	    assert "setWorkbenchIdentity(requested)" in js
   135	
   136	
   137	# ─── 4. Live-served route ───────────────────────────────────────────
   138	
   139	
   140	def test_workbench_route_serves_role_affordance_section(server) -> None:
   141	    status, html = _get(server, "/workbench")
   142	    assert status == 200
   143	    assert 'id="workbench-pending-signoff-affordance"' in html
   144	    assert 'data-identity-name="Kogami"' in html
   145	
   146	
   147	# ─── 5. Default state preserves Kogami workflow ─────────────────────
   148	
   149	
   150	def test_default_html_keeps_approval_center_visible_for_kogami() -> None:
   151	    """Without ?identity= override, page boots as Kogami; #approval-center-entry
   152	    must NOT carry hidden=true in source HTML (JS hides it post-boot only
   153	    when identity != Kogami)."""
   154	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   155	    entry_block = html.split('id="approval-center-entry"')[1].split(">")[0]
   156	    assert "hidden" not in entry_block.lower()
   157	
   158	
   159	# ─── 6. Truth-engine red line (no data mutation paths added) ────────
   160	
   161	
   162	def test_e11_08_only_touches_ui_layer() -> None:
   163	    """The fix must be UI-only — no new endpoint, no controller change.
   164	    Verify by grepping for the new identifiers across the codebase: they
   165	    must appear only in static/, tests/, .planning/."""
   166	    # workbench.html identifies the chip
   167	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   168	    assert 'data-identity-name="Kogami"' in html
   169	    # Stable: the identity attribute is not consumed by any backend
   170	    # endpoint — the JS in workbench.js is the only reader.
   171	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   172	    assert "data-identity-name" in js

exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_h2_button_sweep.py | sed -n '1,280p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
     2	
     3	Continues the E11-15 eyebrow sweep: 7 remaining English-only h1/h2/button/
     4	caption strings on /workbench are bilingualized as `<中文> · <English>`,
     5	preserving the English suffix so existing test locks (e.g. dual-route
     6	checks for `Control Logic Workbench</h1>`) continue to pass.
     7	
     8	In-scope strings (file:line in pre-sweep workbench.html):
     9	- :18  h1   Control Logic Workbench           → 控制逻辑工作台 · Control Logic Workbench
    10	- :281 btn  Load Active Ticket                → 加载当前工单 · Load Active Ticket
    11	- :282 btn  Snapshot Current State            → 快照当前状态 · Snapshot Current State
    12	- :334 h2   Review Queue                      → 审核队列 · Review Queue
    13	- :349 btn  Approval Center                   → 审批中心 · Approval Center
    14	- :351 cap  Approval actions are Kogami-only. → 审批操作仅限 Kogami · Approval actions are Kogami-only.
    15	- :380 h2   Kogami Proposal Triage            → Kogami 提案审批 · Kogami Proposal Triage
    16	
    17	Out of scope (deliberately preserved or deferred):
    18	- API remediation message in demo_server.py:743 — backend contract,
    19	  locked by tests/test_lever_snapshot_manual_override_guard.py:151.
    20	- Approval lane h3s "Pending"/"Accept"/"Reject" + lane buttons
    21	  ("Accept Proposal"/"Reject Proposal") — functional approval-flow
    22	  strings, deferred to a focused approval-flow polish sub-phase.
    23	"""
    24	
    25	from __future__ import annotations
    26	
    27	import http.client
    28	import threading
    29	from http.server import ThreadingHTTPServer
    30	from pathlib import Path
    31	
    32	import pytest
    33	
    34	from well_harness.demo_server import DemoRequestHandler
    35	
    36	
    37	REPO_ROOT = Path(__file__).resolve().parents[1]
    38	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    39	
    40	
    41	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    42	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    43	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    44	    thread.start()
    45	    return server, thread
    46	
    47	
    48	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    49	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    50	    connection.request("GET", path)
    51	    response = connection.getresponse()
    52	    return response.status, response.read().decode("utf-8")
    53	
    54	
    55	@pytest.fixture
    56	def server():
    57	    s, t = _start_demo_server()
    58	    try:
    59	        yield s
    60	    finally:
    61	        s.shutdown()
    62	        s.server_close()
    63	        t.join(timeout=2)
    64	
    65	
    66	# ─── 1. New bilingual strings POSITIVELY locked ──────────────────────
    67	
    68	
    69	@pytest.mark.parametrize(
    70	    "bilingual",
    71	    [
    72	        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
    73	        ">加载当前工单 · Load Active Ticket<",
    74	        ">快照当前状态 · Snapshot Current State<",
    75	        "<h2>审核队列 · Review Queue</h2>",
    76	        "审批中心 · Approval Center",
    77	        "审批操作仅限 Kogami · Approval actions are Kogami-only.",
    78	        "Kogami 提案审批 · Kogami Proposal Triage",
    79	    ],
    80	)
    81	def test_workbench_html_carries_bilingual_string(bilingual: str) -> None:
    82	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    83	    assert bilingual in html, f"missing bilingual string: {bilingual}"
    84	
    85	
    86	# ─── 2. Stale English-only strings are gone ──────────────────────────
    87	
    88	
    89	@pytest.mark.parametrize(
    90	    "stale",
    91	    [
    92	        "<h1>Control Logic Workbench</h1>",
    93	        ">Load Active Ticket<",
    94	        ">Snapshot Current State<",
    95	        "<h2>Review Queue</h2>",
    96	        "<h2 id=\"approval-center-title\">Kogami Proposal Triage</h2>",
    97	    ],
    98	)
    99	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   100	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   101	    assert stale not in html, f"stale English-only string still present: {stale}"
   102	
   103	
   104	# ─── 3. English suffixes preserved for existing test locks ───────────
   105	#
   106	# E11-15b deliberately keeps the English token at the end of each
   107	# bilingual string, so existing exact-substring tests (e.g.
   108	# test_workbench_dual_route's `Control Logic Workbench</h1>` check)
   109	# keep passing without modification.
   110	
   111	
   112	@pytest.mark.parametrize(
   113	    "preserved_english_suffix",
   114	    [
   115	        "Control Logic Workbench</h1>",
   116	        "Load Active Ticket</button>",
   117	        "Snapshot Current State</button>",
   118	        "Review Queue</h2>",
   119	        "Approval Center\n",  # button text fragment, newline preserved
   120	        "Approval actions are Kogami-only.",
   121	        "Kogami Proposal Triage</h2>",
   122	    ],
   123	)
   124	def test_e11_15b_preserves_english_suffix(preserved_english_suffix: str) -> None:
   125	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   126	    assert preserved_english_suffix in html, (
   127	        f"E11-15b broke English suffix invariant: {preserved_english_suffix}"
   128	    )
   129	
   130	
   131	# ─── 4. Structural anchors preserved ─────────────────────────────────
   132	
   133	
   134	@pytest.mark.parametrize(
   135	    "anchor",
   136	    [
   137	        'id="approval-center-entry"',
   138	        'id="approval-center-panel"',
   139	        'id="approval-center-title"',
   140	        'id="annotation-inbox"',
   141	        'class="workbench-toolbar-button is-primary"',
   142	        'data-role="KOGAMI"',
   143	        'data-approval-role="KOGAMI"',
   144	    ],
   145	)
   146	def test_e11_15b_preserves_structural_anchors(anchor: str) -> None:
   147	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   148	    assert anchor in html, f"E11-15b broke structural anchor: {anchor}"
   149	
   150	
   151	# ─── 5. Live-served route reflects the sweep ─────────────────────────
   152	
   153	
   154	def test_workbench_route_serves_bilingual_strings(server) -> None:
   155	    status, html = _get(server, "/workbench")
   156	    assert status == 200
   157	    assert "控制逻辑工作台 · Control Logic Workbench" in html
   158	    assert "审核队列 · Review Queue" in html
   159	    assert "审批中心 · Approval Center" in html
   160	    assert "审批操作仅限 Kogami" in html
   161	    assert "Kogami 提案审批" in html
   162	    assert "加载当前工单" in html
   163	    assert "快照当前状态" in html
   164	
   165	
   166	# ─── 6. Truth-engine red line — API remediation untouched ────────────
   167	#
   168	# The Approval Center remediation message in demo_server.py is a
   169	# backend API contract locked by test_lever_snapshot_manual_override_guard.
   170	# The HTML sweep MUST NOT bilingualize that string; the API stays English.
   171	
   172	
   173	def test_e11_15b_does_not_touch_api_remediation_message() -> None:
   174	    """The 409 remediation message is API contract, not display copy."""
   175	    repo_root = Path(__file__).resolve().parents[1]
   176	    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
   177	        encoding="utf-8"
   178	    )
   179	    # The original English-only remediation text MUST still be there.
   180	    assert (
   181	        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   182	        in demo_server
   183	    )
   184	    # No Chinese leak into the API layer.
   185	    assert "审批中心" not in demo_server
   186	    assert "审批操作" not in demo_server

codex
The migrated tests remain mostly exact-string locks, not vague substring checks. I’m now validating the remaining claims mechanically: grepping the suffix invariants, probing the served `/workbench`, and checking whether the new negative-isolation test really matches what’s in `demo_server.py`, `controller.py`, `runner.py`, `models.py`, `workbench.js`, and `workbench.css`.
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
/bin/zsh -lc 'rg -n "工程师工作区|探针与追踪 · Probe|Probe &amp; Trace</h2>|Annotate &amp; Propose</h2>|Hand off &amp; Track</h2>|Control Logic Workbench</h1>" src/well_harness/static/workbench.html src/well_harness/demo_server.py src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/static/workbench.js src/well_harness/static/workbench.css' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:17:          <p class="eyebrow">工程师工作区</p>
src/well_harness/static/workbench.html:18:          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
src/well_harness/static/workbench.html:275:            <h2>探针与追踪 · Probe &amp; Trace</h2>
src/well_harness/static/workbench.html:295:            <h2>标注与提案 · Annotate &amp; Propose</h2>
src/well_harness/static/workbench.html:315:            <h2>移交与跟踪 · Hand off &amp; Track</h2>

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 2840ms:
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 2.66s

codex
The isolation grep is clean so far: the new strings only appear in `workbench.html` among the red-line files I checked. I also have the targeted verification suite running; once that completes I’ll combine it with a direct `/workbench` probe and call out any remaining contract gaps.
codex
I found one concrete gap in the new isolation test and I’m confirming whether it’s just documentation drift or an actual contract hole. I’m also checking the pre-change test shape from `main` so I can say precisely whether any assertion became weaker or whether the new file compensates for it.
exec
/bin/zsh -lc "git show main:tests/test_workbench_column_rename.py | nl -ba | sed -n '55,255p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    55	        t.join(timeout=2)
    56	
    57	
    58	# ─── 1. New visible copy is present ──────────────────────────────────
    59	
    60	
    61	@pytest.mark.parametrize(
    62	    "title",
    63	    [
    64	        "Probe &amp; Trace · 探针与追踪",
    65	        "Annotate &amp; Propose · 标注与提案",
    66	        "Hand off &amp; Track · 移交与跟踪",
    67	    ],
    68	)
    69	def test_workbench_html_carries_new_column_title(title: str) -> None:
    70	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    71	    assert title in html, f"missing renamed column title: {title}"
    72	
    73	
    74	@pytest.mark.parametrize(
    75	    "eyebrow",
    76	    ["probe &amp; trace", "annotate &amp; propose", "hand off &amp; track"],
    77	)
    78	def test_workbench_html_carries_new_eyebrow(eyebrow: str) -> None:
    79	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    80	    assert eyebrow in html, f"missing renamed eyebrow: {eyebrow}"
    81	
    82	
    83	# ─── 2. Old technical-noun copy removed ──────────────────────────────
    84	
    85	
    86	@pytest.mark.parametrize(
    87	    "stale",
    88	    [
    89	        "<h2>Scenario Control</h2>",
    90	        "<h2>Spec Review Surface</h2>",
    91	        "<h2>Logic Circuit Surface</h2>",
    92	        ">control panel<",
    93	        ">document<",
    94	        ">circuit<",
    95	        "Waiting for control panel boot.",
    96	        "Waiting for document panel boot.",
    97	        "Waiting for circuit panel boot.",
    98	    ],
    99	)
   100	def test_workbench_html_does_not_carry_stale_column_title(stale: str) -> None:
   101	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   102	    assert stale not in html, f"stale technical-noun copy still present: {stale}"
   103	
   104	
   105	# ─── 2b. New pre-hydration boot-status copy is POSITIVELY locked ──────
   106	#
   107	# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
   108	# pre-hydration "Waiting for ... panel boot." strings. R1 only verified
   109	# absence of the stale copy; R2 also asserts presence of the new copy
   110	# so a drift to any other phrasing would fail the suite.
   111	
   112	
   113	@pytest.mark.parametrize(
   114	    "boot_status",
   115	    [
   116	        "Waiting for probe &amp; trace panel boot.",
   117	        "Waiting for annotate &amp; propose panel boot.",
   118	        "Waiting for hand off &amp; track panel boot.",
   119	    ],
   120	)
   121	def test_workbench_html_carries_new_boot_status(boot_status: str) -> None:
   122	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   123	    assert boot_status in html, f"missing renamed pre-hydration boot status: {boot_status}"
   124	
   125	
   126	# ─── 3. Underlying IDs / data attributes preserved ──────────────────
   127	#
   128	# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
   129	# panel ids, data-column tokens, data-annotation-surface tokens, and
   130	# status div ids are anchors for e2e selectors and JS boot wiring, so
   131	# they MUST stay stable through the rename.
   132	
   133	
   134	@pytest.mark.parametrize(
   135	    "anchor",
   136	    [
   137	        'id="workbench-control-panel"',
   138	        'id="workbench-document-panel"',
   139	        'id="workbench-circuit-panel"',
   140	        'data-column="control"',
   141	        'data-column="document"',
   142	        'data-column="circuit"',
   143	        'data-annotation-surface="control"',
   144	        'data-annotation-surface="document"',
   145	        'data-annotation-surface="circuit"',
   146	        'id="workbench-control-status"',
   147	        'id="workbench-document-status"',
   148	        'id="workbench-circuit-status"',
   149	    ],
   150	)
   151	def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
   152	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   153	    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"
   154	
   155	
   156	# ─── 4. JS boot status copy matches new column names ────────────────
   157	
   158	
   159	# P4 R1 NIT fix: lock the FULL hydrated boot-status sentence (not just
   160	# the "X ready" prefix), so future drift in the staging note is also
   161	# caught. P5 R1 IMPORTANT fix: the strings must NOT contain internal
   162	# roadmap tokens like "E07+" or "E07".
   163	
   164	
   165	@pytest.mark.parametrize(
   166	    "boot_copy",
   167	    [
   168	        "Probe & Trace ready. Scenario actions are staged for the next bundle.",
   169	        "Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
   170	        "Hand off & Track ready. Overlay annotation is staged for the next bundle.",
   171	    ],
   172	)
   173	def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
   174	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   175	    assert boot_copy in js, f"workbench.js boot status missing exact string: {boot_copy}"
   176	
   177	
   178	def test_workbench_js_boot_status_drops_stale_names() -> None:
   179	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   180	    # Old boot copy must NOT appear, otherwise the visible chrome and the
   181	    # status messages will disagree.
   182	    assert "Control panel ready" not in js
   183	    assert "Document panel ready" not in js
   184	    assert "Circuit panel ready" not in js
   185	
   186	
   187	def test_workbench_js_boot_status_drops_internal_phase_tokens() -> None:
   188	    """P5 R1 IMPORTANT fix: roadmap tokens like 'E07+'/'E07' must not
   189	    leak into user-visible boot status strings."""
   190	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   191	    # Scope the check to the three boot functions to avoid false
   192	    # positives in unrelated comments/blocks.
   193	    for fn in (
   194	        "bootWorkbenchControlPanel",
   195	        "bootWorkbenchDocumentPanel",
   196	        "bootWorkbenchCircuitPanel",
   197	    ):
   198	        anchor = js.find(f"function {fn}")
   199	        assert anchor != -1, f"missing function {fn}"
   200	        slice_ = js[anchor : anchor + 600]
   201	        assert "E07" not in slice_, (
   202	            f"internal phase token 'E07' leaked into {fn} boot status"
   203	        )
   204	
   205	
   206	# P1 R1 NIT fix: failure-path fallback must use the engineer-task verb,
   207	# not the internal columnName token.
   208	
   209	
   210	def test_workbench_js_failure_fallback_uses_task_verb_label() -> None:
   211	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   212	    # WORKBENCH_COLUMN_LABEL maps control/document/circuit → task verbs
   213	    assert "WORKBENCH_COLUMN_LABEL" in js
   214	    assert '"control": "Probe & Trace"' in js or 'control: "Probe & Trace"' in js
   215	    assert '"document": "Annotate & Propose"' in js or 'document: "Annotate & Propose"' in js
   216	    assert '"circuit": "Hand off & Track"' in js or 'circuit: "Hand off & Track"' in js
   217	    # Failure copy must reference the label, not the raw columnName.
   218	    assert "${label} panel failed independently" in js, (
   219	        "failure fallback should use the engineer-task verb label, not the raw column token"
   220	    )
   221	
   222	
   223	# ─── 5. Live-served /workbench reflects the rename end-to-end ───────
   224	
   225	
   226	def test_workbench_route_serves_renamed_columns(server) -> None:
   227	    status, html = _get(server, "/workbench")
   228	    assert status == 200
   229	    # New copy
   230	    assert "Probe &amp; Trace · 探针与追踪" in html
   231	    assert "Annotate &amp; Propose · 标注与提案" in html
   232	    assert "Hand off &amp; Track · 移交与跟踪" in html
   233	    # Stable anchors still served
   234	    assert 'id="workbench-control-panel"' in html
   235	    assert 'data-column="circuit"' in html

exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_direction_consistency.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "python - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer((\"127.0.0.1\", 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection(\"127.0.0.1\", server.server_port, timeout=5)
    conn.request(\"GET\", \"/workbench\")
    resp = conn.getresponse()
    body = resp.read().decode(\"utf-8\")
    static = Path(\"src/well_harness/static/workbench.html\").read_text(encoding=\"utf-8\")
    print(f\"status={resp.status}\")
    print(f\"exact_match={body == static}\")
    for token in [\"工程师工作区\", \"<h2>探针与追踪 · Probe &amp; Trace</h2>\", \"<h1>控制逻辑工作台 · Control Logic Workbench</h1>\"]:
        print(f\"token_present[{token}]={token in body}\")
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
     2	
     3	Two NIT closures from E11-15b (P3 Demo Presenter):
     4	
     5	NIT #1 — h1 + eyebrow duplication
     6	    `<p class="eyebrow">控制逻辑工作台</p>` immediately followed by
     7	    `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` reads redundantly.
     8	    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
     9	    eyebrow + h1 read as category + title.
    10	
    11	NIT #2 — direction asymmetry
    12	    Column-trio h2s were English-first (`Probe & Trace · 探针与追踪`)
    13	    while the rest of the page is Chinese-first. E11-15c flips them
    14	    to `<中文> · <English>` for full-page direction consistency.
    15	
    16	Net change is 4 [REWRITE] lines in workbench.html. Existing test files
    17	test_workbench_column_rename and test_workbench_chinese_eyebrow_sweep
    18	were updated in lockstep with the new strings.
    19	"""
    20	
    21	from __future__ import annotations
    22	
    23	import http.client
    24	import threading
    25	from http.server import ThreadingHTTPServer
    26	from pathlib import Path
    27	
    28	import pytest
    29	
    30	from well_harness.demo_server import DemoRequestHandler
    31	
    32	
    33	REPO_ROOT = Path(__file__).resolve().parents[1]
    34	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    35	
    36	
    37	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    38	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    39	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    40	    thread.start()
    41	    return server, thread
    42	
    43	
    44	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    45	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    46	    connection.request("GET", path)
    47	    response = connection.getresponse()
    48	    return response.status, response.read().decode("utf-8")
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
    62	# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
    63	
    64	
    65	@pytest.mark.parametrize(
    66	    "chinese_first_h2",
    67	    [
    68	        "<h2>探针与追踪 · Probe &amp; Trace</h2>",
    69	        "<h2>标注与提案 · Annotate &amp; Propose</h2>",
    70	        "<h2>移交与跟踪 · Hand off &amp; Track</h2>",
    71	    ],
    72	)
    73	def test_column_h2_is_chinese_first(chinese_first_h2: str) -> None:
    74	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    75	    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
    76	
    77	
    78	@pytest.mark.parametrize(
    79	    "stale_english_first_h2",
    80	    [
    81	        "<h2>Probe &amp; Trace · 探针与追踪</h2>",
    82	        "<h2>Annotate &amp; Propose · 标注与提案</h2>",
    83	        "<h2>Hand off &amp; Track · 移交与跟踪</h2>",
    84	    ],
    85	)
    86	def test_stale_english_first_column_h2_removed(stale_english_first_h2: str) -> None:
    87	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    88	    assert stale_english_first_h2 not in html, (
    89	        f"stale English-first column h2 still present: {stale_english_first_h2}"
    90	    )
    91	
    92	
    93	# ─── 2. NIT #1: page eyebrow + h1 are no longer duplicates ───────────
    94	
    95	
    96	def test_page_eyebrow_is_engineer_workspace_not_h1_duplicate() -> None:
    97	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    98	    assert '<p class="eyebrow">工程师工作区</p>' in html
    99	    assert '<p class="eyebrow">控制逻辑工作台</p>' not in html
   100	
   101	
   102	def test_h1_still_carries_full_bilingual_title() -> None:
   103	    """E11-15b's h1 bilingualization must survive E11-15c — only the
   104	    sibling eyebrow changes; the h1 stays as the page-title source of
   105	    truth."""
   106	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   107	    assert "<h1>控制逻辑工作台 · Control Logic Workbench</h1>" in html
   108	
   109	
   110	def test_eyebrow_and_h1_are_not_chinese_duplicates() -> None:
   111	    """Closure of P3's NIT #1: extracting the eyebrow's Chinese and the
   112	    h1's Chinese, they must not match."""
   113	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   114	    eyebrow_inner = (
   115	        html.split('<div class="workbench-collab-brand">')[1]
   116	        .split('<p class="eyebrow">')[1]
   117	        .split("</p>")[0]
   118	    )
   119	    h1_inner = html.split("<h1>")[1].split("</h1>")[0]
   120	    h1_chinese = h1_inner.split(" · ")[0]
   121	    assert eyebrow_inner != h1_chinese, (
   122	        f"eyebrow ({eyebrow_inner!r}) duplicates h1 Chinese ({h1_chinese!r}) — "
   123	        "P3 NIT #1 not closed"
   124	    )
   125	
   126	
   127	# ─── 3. English suffixes preserved (no regression on substring locks) ─
   128	
   129	
   130	@pytest.mark.parametrize(
   131	    "preserved_english_suffix",
   132	    [
   133	        "Probe &amp; Trace</h2>",
   134	        "Annotate &amp; Propose</h2>",
   135	        "Hand off &amp; Track</h2>",
   136	        "Control Logic Workbench</h1>",
   137	    ],
   138	)
   139	def test_e11_15c_preserves_english_suffix(preserved_english_suffix: str) -> None:
   140	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   141	    assert preserved_english_suffix in html, (
   142	        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
   143	    )
   144	
   145	
   146	# ─── 4. Live-served route reflects E11-15c ───────────────────────────
   147	
   148	
   149	def test_workbench_route_reflects_direction_flip(server) -> None:
   150	    status, html = _get(server, "/workbench")
   151	    assert status == 200
   152	    assert "探针与追踪 · Probe" in html
   153	    assert "标注与提案 · Annotate" in html
   154	    assert "移交与跟踪 · Hand off" in html
   155	    assert "工程师工作区" in html
   156	
   157	
   158	# ─── 5. Truth-engine red line ────────────────────────────────────────
   159	
   160	
   161	def test_e11_15c_only_touches_static_html_and_tests() -> None:
   162	    """The fix is HTML + test-only. Demo server, controller, runner,
   163	    models, adapters, JS, and CSS must NOT carry the new strings."""
   164	    repo_root = Path(__file__).resolve().parents[1]
   165	    backend_files = [
   166	        repo_root / "src" / "well_harness" / "demo_server.py",
   167	        repo_root / "src" / "well_harness" / "controller.py",
   168	        repo_root / "src" / "well_harness" / "runner.py",
   169	        repo_root / "src" / "well_harness" / "models.py",
   170	    ]
   171	    for f in backend_files:
   172	        if not f.exists():
   173	            continue
   174	        content = f.read_text(encoding="utf-8")
   175	        for new_string in ["工程师工作区", "探针与追踪 · Probe"]:
   176	            assert new_string not in content, (
   177	                f"E11-15c string {new_string!r} unexpectedly leaked into {f.name}"
   178	            )
   179	
   180	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   181	    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
   182	    for new_string in ["工程师工作区"]:
   183	        assert new_string not in js
   184	        assert new_string not in css

 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "git show main:tests/test_workbench_chinese_eyebrow_sweep.py | nl -ba | sed -n '50,210p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    50	        s.server_close()
    51	        t.join(timeout=2)
    52	
    53	
    54	# ─── 1. New Chinese eyebrows are POSITIVELY locked ───────────────────
    55	
    56	
    57	@pytest.mark.parametrize(
    58	    "eyebrow_html",
    59	    [
    60	        '<p class="eyebrow">控制逻辑工作台</p>',
    61	        '<span class="workbench-sow-eyebrow">当前现状</span>',
    62	        '<p class="eyebrow">主流场景</p>',
    63	        '<p class="eyebrow">标注收件箱</p>',
    64	        '<p class="eyebrow">审批中心</p>',
    65	    ],
    66	)
    67	def test_workbench_html_carries_chinese_eyebrow(eyebrow_html: str) -> None:
    68	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    69	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
    70	
    71	
    72	# ─── 2. Old English-only eyebrows are gone ───────────────────────────
    73	
    74	
    75	@pytest.mark.parametrize(
    76	    "stale_eyebrow_html",
    77	    [
    78	        '<p class="eyebrow">control logic workbench</p>',
    79	        '<span class="workbench-sow-eyebrow">state of world</span>',
    80	        '<p class="eyebrow">canonical scenarios</p>',
    81	        '<p class="eyebrow">annotation inbox</p>',
    82	        '<p class="eyebrow">approval center</p>',
    83	    ],
    84	)
    85	def test_workbench_html_does_not_carry_stale_english_eyebrow(stale_eyebrow_html: str) -> None:
    86	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    87	    assert stale_eyebrow_html not in html, (
    88	        f"stale English-only eyebrow still present: {stale_eyebrow_html}"
    89	    )
    90	
    91	
    92	# ─── 3. Out-of-scope eyebrows (E11-03 column trio) are PRESERVED ─────
    93	
    94	
    95	@pytest.mark.parametrize(
    96	    "preserved_eyebrow",
    97	    [
    98	        '<p class="eyebrow">probe &amp; trace</p>',
    99	        '<p class="eyebrow">annotate &amp; propose</p>',
   100	        '<p class="eyebrow">hand off &amp; track</p>',
   101	    ],
   102	)
   103	def test_e11_03_column_eyebrows_preserved(preserved_eyebrow: str) -> None:
   104	    """E11-15 explicitly does NOT touch the column-trio eyebrows.
   105	    They live above bilingual h2s and are locked by test_workbench_column_rename."""
   106	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   107	    assert preserved_eyebrow in html, (
   108	        f"E11-03 column eyebrow accidentally removed by E11-15 sweep: {preserved_eyebrow}"
   109	    )
   110	
   111	
   112	# ─── 4. Anchors and h1/h2 strings preserved ──────────────────────────
   113	
   114	
   115	@pytest.mark.parametrize(
   116	    "anchor",
   117	    [
   118	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
   119	        # English suffix `Control Logic Workbench</h1>` is preserved as
   120	        # locked by test_workbench_dual_route.
   121	        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
   122	        # IDs of containing sections untouched
   123	        'id="workbench-state-of-world-bar"',
   124	        'id="workbench-wow-starters"',
   125	        'id="annotation-inbox"',
   126	        'id="approval-center-panel"',
   127	        # Class hooks untouched (CSS still binds)
   128	        'class="eyebrow"',
   129	        'class="workbench-sow-eyebrow"',
   130	    ],
   131	)
   132	def test_e11_15_preserves_structural_anchors(anchor: str) -> None:
   133	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   134	    assert anchor in html, f"E11-15 sweep accidentally broke structural anchor: {anchor}"
   135	
   136	
   137	# ─── 5. Live-served route reflects the sweep ─────────────────────────
   138	
   139	
   140	def test_workbench_route_serves_chinese_eyebrows(server) -> None:
   141	    status, html = _get(server, "/workbench")
   142	    assert status == 200
   143	    assert "控制逻辑工作台" in html
   144	    assert "当前现状" in html
   145	    assert "主流场景" in html
   146	    assert "标注收件箱" in html
   147	    assert "审批中心" in html
   148	
   149	
   150	# ─── 6. Truth-engine red line ────────────────────────────────────────
   151	
   152	
   153	def test_e11_15_only_touches_static_html() -> None:
   154	    """The sweep is HTML-only — no JS, no CSS, no controller, no adapter.
   155	    Verify by spot-checking that the 5 changed strings appear nowhere
   156	    else in code-bearing files."""
   157	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   158	    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
   159	    # The new Chinese strings live only in HTML, not JS or CSS.
   160	    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
   161	        assert chinese not in js, f"unexpected Chinese eyebrow leaked into workbench.js: {chinese}"
   162	        assert chinese not in css, f"unexpected Chinese eyebrow leaked into workbench.css: {chinese}"

codex
The exact live-probe script failed only because this checkout has `python3`, not `python`. I’m rerunning it with the correct interpreter and will use that result, not the earlier failed shell invocation, as the route-equality evidence.
exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer((\"127.0.0.1\", 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection(\"127.0.0.1\", server.server_port, timeout=5)
    conn.request(\"GET\", \"/workbench\")
    resp = conn.getresponse()
    body = resp.read().decode(\"utf-8\")
    static = Path(\"src/well_harness/static/workbench.html\").read_text(encoding=\"utf-8\")
    print(f\"status={resp.status}\")
    print(f\"exact_match={body == static}\")
    for token in [\"工程师工作区\", \"<h2>探针与追踪 · Probe &amp; Trace</h2>\", \"<h1>控制逻辑工作台 · Control Logic Workbench</h1>\"]:
        print(f\"token_present[{token}]={token in body}\")
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 621ms:
status=200
exact_match=False
token_present[工程师工作区]=False
token_present[<h2>探针与追踪 · Probe &amp; Trace</h2>]=False
token_present[<h1>控制逻辑工作台 · Control Logic Workbench</h1>]=False

codex
The live probe surfaced a real discrepancy: `/workbench` returns 200, but the body is not byte-identical to `src/well_harness/static/workbench.html`, and the raw static tokens I checked are missing from the served HTML. I’m inspecting the actual served payload now to determine whether the server is rewriting the file on the way out or whether the route is serving a different surface than the tests assume.
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '700,860p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   700	    if not isinstance(raw_value, str):
   701	        return None, {
   702	            "error": "invalid_lever_snapshot_input",
   703	            "field": "feedback_mode",
   704	            "message": "feedback_mode must be a string.",
   705	        }
   706	    normalized = raw_value.strip()
   707	    if normalized not in LEVER_FEEDBACK_MODES:
   708	        return None, {
   709	            "error": "invalid_lever_snapshot_input",
   710	            "field": "feedback_mode",
   711	            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
   712	        }
   713	    return normalized, None
   714	
   715	
   716	# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
   717	# When feedback_mode = manual_feedback_override, the request must include
   718	# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
   719	# the endpoint returns 409 Conflict (paired with E11-13 UI affordance, this
   720	# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
   721	# stays put: no controller / runner / models / adapters/*.py changes.
   722	def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str) -> dict | None:
   723	    """Return error_payload (with `_status` 409) if signoff is missing/invalid; else None.
   724	
   725	    Only enforced when feedback_mode == "manual_feedback_override". For
   726	    auto_scrubber, this returns None unconditionally (no extra fields needed).
   727	    """
   728	    if feedback_mode != "manual_feedback_override":
   729	        return None
   730	
   731	    actor = request_payload.get("actor")
   732	    ticket_id = request_payload.get("ticket_id")
   733	    signoff = request_payload.get("manual_override_signoff")
   734	
   735	    def reject(field: str, message: str) -> dict:
   736	        return {
   737	            "_status": 409,
   738	            "error": "manual_override_unsigned",
   739	            "field": field,
   740	            "message": message,
   741	            "remediation": (
   742	                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
   743	                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   744	            ),
   745	            # E11-14 R2 (P2 IMPORTANT #4, 2026-04-25): residual risk disclosure.
   746	            # The current sign-off check is structural only — same triplet can
   747	            # authorize multiple override payloads (replay) and signed_at is
   748	            # not freshness-checked. One-shot latch / nonce / freshness is the
   749	            # E11-16 approval-endpoint hardening scope. Until E11-16 lands,
   750	            # this guard is "shape correct" not "latched authorization".
   751	            "residual_risk": (
   752	                "Sign-off is structural only. Replay across payloads is not blocked; "
   753	                "signed_at is not freshness-validated. One-shot latch + nonce + "
   754	                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
   755	            ),
   756	        }
   757	
   758	    if not isinstance(actor, str) or not actor.strip():
   759	        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
   760	    if not isinstance(ticket_id, str) or not ticket_id.strip():
   761	        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
   762	
   763	    if not isinstance(signoff, dict):
   764	        return reject(
   765	            "manual_override_signoff",
   766	            "manual_feedback_override requires a manual_override_signoff object.",
   767	        )
   768	    signed_by = signoff.get("signed_by")
   769	    signed_at = signoff.get("signed_at")
   770	    signoff_ticket = signoff.get("ticket_id")
   771	    if not isinstance(signed_by, str) or not signed_by.strip():
   772	        return reject(
   773	            "manual_override_signoff.signed_by",
   774	            "manual_override_signoff.signed_by must be a non-empty string.",
   775	        )
   776	    if not isinstance(signed_at, str) or not signed_at.strip():
   777	        return reject(
   778	            "manual_override_signoff.signed_at",
   779	            "manual_override_signoff.signed_at must be a non-empty timestamp string.",
   780	        )
   781	    if not isinstance(signoff_ticket, str) or not signoff_ticket.strip():
   782	        return reject(
   783	            "manual_override_signoff.ticket_id",
   784	            "manual_override_signoff.ticket_id must be a non-empty string.",
   785	        )
   786	    if signoff_ticket.strip() != ticket_id.strip():
   787	        return reject(
   788	            "manual_override_signoff.ticket_id",
   789	            "manual_override_signoff.ticket_id must match the request's ticket_id.",
   790	        )
   791	
   792	    # E11-14 R2 fix (P2 BLOCKER #1, 2026-04-25): actor must equal
   793	    # manual_override_signoff.signed_by. Without this binding, an attacker
   794	    # can submit `actor="Mallory"` with `signed_by="Kogami"` and the server
   795	    # would accept it (P2 verified via live probe). Bind requester identity
   796	    # to the signoff's signer.
   797	    if signed_by.strip() != actor.strip():
   798	        return reject(
   799	            "actor",
   800	            "actor must match manual_override_signoff.signed_by (impersonation guard).",
   801	        )
   802	
   803	    return None
   804	
   805	
   806	def _normalize_fault_injection_node_id(node_id: str) -> str:
   807	    normalized = str(node_id or "").strip()
   808	    return LEVER_SNAPSHOT_FAULT_NODE_ALIASES.get(normalized, normalized)
   809	
   810	
   811	def _fault_injection_map(fault_injections: list[dict] | None) -> dict[str, str]:
   812	    fault_map: dict[str, str] = {}
   813	    for fault in fault_injections or []:
   814	        node_id = _normalize_fault_injection_node_id(fault.get("node_id", ""))
   815	        fault_type = str(fault.get("fault_type", "")).strip()
   816	        if node_id and fault_type:
   817	            fault_map[node_id] = fault_type
   818	    return fault_map
   819	
   820	
   821	def _append_unique(values: list[str], value: str) -> None:
   822	    if value not in values:
   823	        values.append(value)
   824	
   825	
   826	def _apply_switch_fault_injections(
   827	    switch_state: SwitchState,
   828	    fault_map: dict[str, str],
   829	) -> SwitchState:
   830	    sw1 = switch_state.sw1
   831	    if fault_map.get("sw1") == "stuck_off":
   832	        sw1 = False
   833	    elif fault_map.get("sw1") == "stuck_on":
   834	        sw1 = True
   835	
   836	    sw2 = switch_state.sw2
   837	    if fault_map.get("sw2") == "stuck_off":
   838	        sw2 = False
   839	    elif fault_map.get("sw2") == "stuck_on":
   840	        sw2 = True
   841	
   842	    if sw1 == switch_state.sw1 and sw2 == switch_state.sw2:
   843	        return switch_state
   844	
   845	    return SwitchState(
   846	        previous_tra_deg=switch_state.previous_tra_deg,
   847	        sw1=sw1,
   848	        sw2=sw2,
   849	    )
   850	
   851	
   852	def _apply_sensor_fault_injections(sensors, fault_map: dict[str, str]):
   853	    sensor_updates = {}
   854	
   855	    if fault_map.get("tls115") == "sensor_zero":
   856	        sensor_updates["tls_unlocked_ls"] = False
   857	
   858	    if fault_map.get("vdt90") == "cmd_blocked":
   859	        sensor_updates["deploy_90_percent_vdt"] = False
   860	

exec
/bin/zsh -lc "rg -n \"def _serve_static|workbench.html|replace\\(|decode\\(|read_text\\(|read_bytes\\(\" src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
257:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
258:            self._serve_static("workbench.html")
335:            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
585:    def _serve_static(self, relative_path: str):
601:        self._send_bytes(200, target_path.read_bytes(), content_type)
610:            full_text = constitution.read_text(encoding="utf-8")
864:    return replace(sensors, **sensor_updates)
897:    return replace(outputs, **output_updates)
1270:    return json.loads(REFERENCE_PACKET_PATH.read_text(encoding="utf-8"))
1392:        text = qa_report.read_text(encoding="utf-8")
1444:        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",

exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer((\"127.0.0.1\", 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection(\"127.0.0.1\", server.server_port, timeout=5)
    conn.request(\"GET\", \"/workbench\")
    resp = conn.getresponse()
    body = resp.read().decode(\"utf-8\")
    print(f\"status={resp.status}\")
    print(body[:1200])
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 602ms:
status=200
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>协作工作台 · FANTUI LogicMVP</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/unified-nav.css">
  <link rel="stylesheet" href="/workbench_shell.css">
</head>
<body class="unified-nav-enabled" data-nav-current="workbench">

<!-- ── Unified Nav ─────────────────────────────────────────────────── -->
<header class="unified-nav" role="navigation" aria-label="FANTUI LogicMVP 主导航">
  <a href="/index.html" class="unified-nav-brand">FANTUI LogicMVP</a>
  <div class="unified-nav-groups">
    <div class="unified-nav-group">
      <span class="unified-nav-group-label">工作台</span>
      <a href="/demo.html" class="unified-nav-link" data-nav-key="demo">反推逻辑</a>
      <a href="/c919_etras_workstation.html" class="unified-nav-link" data-nav-key="etras">C919 E-TRAS</a>
    </div>
    <div class="unified-nav-group">
      <span class="unified-nav-group-label">协作</span>
      <a href="/workbench" class="unified-nav-link" data-nav-key="workbench" data-current="true">Workbench Shell</a>
    </div>
    <div clas

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '580,620p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   580	        except FileNotFoundError as exc:
   581	            self._send_json(400, {"error": str(exc)})
   582	        except Exception as exc:
   583	            self._send_json(500, {"error": str(exc)})
   584	
   585	    def _serve_static(self, relative_path: str):
   586	        static_root = STATIC_DIR.resolve()
   587	        target_path = (static_root / relative_path).resolve()
   588	        # Path must live inside static_root (traversal guard) and exist as a file.
   589	        # Phase UI-F (2026-04-22): allow nested static paths like
   590	        # /c919_etras_panel/circuit.html so the unified-nav can link to them.
   591	        try:
   592	            target_path.relative_to(static_root)
   593	        except ValueError:
   594	            self._send_json(404, {"error": "not_found"})
   595	            return
   596	        if not target_path.is_file():
   597	            self._send_json(404, {"error": "not_found"})
   598	            return
   599	
   600	        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
   601	        self._send_bytes(200, target_path.read_bytes(), content_type)
   602	
   603	    def _serve_v61_redline_excerpt(self):
   604	        """E11-07 (2026-04-26): serve the v6.1 truth-engine red-line clause
   605	        as plain text. Sourced from .planning/constitution.md so the demo
   606	        ships the same words the constitution does, with no drift risk."""
   607	        repo_root = Path(__file__).resolve().parents[2]
   608	        constitution = repo_root / ".planning" / "constitution.md"
   609	        try:
   610	            full_text = constitution.read_text(encoding="utf-8")
   611	        except (FileNotFoundError, OSError):
   612	            full_text = ""
   613	        excerpt_lines = ["# v6.1 truth-engine red-line clause\n", ""]
   614	        if full_text:
   615	            # Pull the explicit "Forbidden（红线维持）" section. If the
   616	            # exact heading drifts, fall back to a small static excerpt
   617	            # so the link still resolves to *something* truthful.
   618	            anchor = full_text.find("Forbidden（红线维持")
   619	            if anchor != -1:
   620	                end = full_text.find("\n## ", anchor)

codex
The mismatch turned out to be interpreter-path related, not a repo regression: direct `python3` imported a non-local `well_harness` package. I’m rerunning the probe with `PYTHONPATH=src` so the live check hits this checkout’s `demo_server.py` and `static/` tree.
exec
/bin/zsh -lc 'rg -n "pythonpath|tool.pytest|pytest.ini|addopts|testpaths" pyproject.toml pytest.ini setup.cfg tox.ini' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: pytest.ini: No such file or directory (os error 2)
rg: setup.cfg: No such file or directory (os error 2)
rg: tox.ini: No such file or directory (os error 2)
pyproject.toml:32:[tool.pytest.ini_options]
pyproject.toml:34:addopts = "-m 'not e2e'"
pyproject.toml:36:testpaths = ["tests"]
pyproject.toml:40:pythonpath = ["src", "."]

exec
/bin/zsh -lc "python3 - <<'PY'
import well_harness, inspect
print(well_harness.__file__)
from well_harness import demo_server
print(demo_server.__file__)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer((\"127.0.0.1\", 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection(\"127.0.0.1\", server.server_port, timeout=5)
    conn.request(\"GET\", \"/workbench\")
    resp = conn.getresponse()
    body = resp.read().decode(\"utf-8\")
    static = Path(\"src/well_harness/static/workbench.html\").read_text(encoding=\"utf-8\")
    print(f\"status={resp.status}\")
    print(f\"exact_match={body == static}\")
    for token in [\"工程师工作区\", \"<h2>探针与追踪 · Probe &amp; Trace</h2>\", \"<h1>控制逻辑工作台 · Control Logic Workbench</h1>\"]:
        print(f\"token_present[{token}]={token in body}\")
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 102ms:
 succeeded in 569ms:
status=200
exact_match=True
token_present[工程师工作区]=True
token_present[<h2>探针与追踪 · Probe &amp; Trace</h2>]=True
token_present[<h1>控制逻辑工作台 · Control Logic Workbench</h1>]=True

codex
I’ve confirmed the valid live probe with `PYTHONPATH=src`: `/workbench` is a 200 and is byte-identical to `src/well_harness/static/workbench.html`. I’m doing one last isolation sweep across `adapters/` and the JS/CSS pair because the new test’s docstring over-claims slightly, and I want the final verdict to separate “code is clean” from “test contract is complete.”
exec
/bin/zsh -lc 'rg -n "工程师工作区|探针与追踪 · Probe|标注与提案 · Annotate|移交与跟踪 · Hand off" src/well_harness/adapters src/well_harness/static/workbench.js src/well_harness/static/workbench.css src/well_harness/demo_server.py src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc 'git diff --name-only main..938a5a2 -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters src/well_harness/demo_server.py src/well_harness/static/workbench.js src/well_harness/static/workbench.css' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
codex
I have enough to draft the main verdict, but I’m adding the two adjacent workbench tests the user called out around the broader 126-test slice so I can speak to cross-contract compatibility from direct evidence, not from the prompt summary.
exec
/bin/zsh -lc 'pytest -q tests/test_workbench_dual_route.py tests/test_workbench_shell.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 3727ms:
..............                                                           [100%]
14 passed in 3.57s

  ✓ Inspect branch diff and changed files against stated red-line scope
  ✓ Read affected HTML and tests to evaluate contract migration strength
  ✓ Run targeted verification including grep and at least one live /workbench probe
  → Draft verdict with severity-ordered findings and residual nits
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,856p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
**Verdict**

`APPROVE_WITH_NITS`

**Findings**

- `IMPORTANT` [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:161) / [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:182): the new truth-engine isolation test over-claims its coverage. The docstring says adapters, JS, and CSS are covered, but the implementation only scans `demo_server.py`/`controller.py`/`runner.py`/`models.py`, and the JS/CSS loop only asserts absence of `工程师工作区`. A future leak of `探针与追踪 · Probe` into `workbench.js` or `workbench.css` would not fail this test, and `src/well_harness/adapters/` is not checked at all. I independently grepped those paths and found no current leak, so this is a guard-strength gap, not a current product defect.

- `INFO` [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17) / [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:23) / [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:27): `工程师工作区` is coherent with the current rendered identity state because the chip already encodes `data-role="ENGINEER"` and `Kogami / Engineer`. I do not see a present contradiction, but the eyebrow is more role-specific than the old copy, so if this surface later becomes explicitly shared-first rather than engineer-first, this string will age sooner.

**Evidence**

- Contract migration strength is preserved. [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:68) adds exact full-tag locks for all three flipped h2s, and [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:107) preserves the exact bilingual h1. The eyebrow dedup invariant at [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:110) fails closed on markup drift; it is not silently bypassed by missing anchors.
- English suffix preservation is intact. Independent grep found `Control Logic Workbench</h1>`, `Probe &amp; Trace</h2>`, `Annotate &amp; Propose</h2>`, and `Hand off &amp; Track</h2>` only in [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:18).
- Live probe passed. `PYTHONPATH=src python3` serving `DemoRequestHandler` and `GET /workbench` returned `status=200`, `exact_match=True` against `src/well_harness/static/workbench.html`, with `工程师工作区`, `<h2>探针与追踪 · Probe &amp; Trace</h2>`, and `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` present.
- Truth-engine red line is preserved. `git diff --name-only main..938a5a2` only showed the 6 claimed files; there were no changes under `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`, `workbench.js`, or `workbench.css`.
- Cross-contract compatibility spot-check passed. `pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py tests/test_workbench_dual_route.py tests/test_workbench_shell.py` completed `126 passed`. I did not rerun the full `1078`-test suite.

P4 — V&V Engineer (Tier-B, E11-15c)

tokens used
180,088
**Verdict**

`APPROVE_WITH_NITS`

**Findings**

- `IMPORTANT` [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:161) / [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:182): the new truth-engine isolation test over-claims its coverage. The docstring says adapters, JS, and CSS are covered, but the implementation only scans `demo_server.py`/`controller.py`/`runner.py`/`models.py`, and the JS/CSS loop only asserts absence of `工程师工作区`. A future leak of `探针与追踪 · Probe` into `workbench.js` or `workbench.css` would not fail this test, and `src/well_harness/adapters/` is not checked at all. I independently grepped those paths and found no current leak, so this is a guard-strength gap, not a current product defect.

- `INFO` [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17) / [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:23) / [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:27): `工程师工作区` is coherent with the current rendered identity state because the chip already encodes `data-role="ENGINEER"` and `Kogami / Engineer`. I do not see a present contradiction, but the eyebrow is more role-specific than the old copy, so if this surface later becomes explicitly shared-first rather than engineer-first, this string will age sooner.

**Evidence**

- Contract migration strength is preserved. [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:68) adds exact full-tag locks for all three flipped h2s, and [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:107) preserves the exact bilingual h1. The eyebrow dedup invariant at [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:110) fails closed on markup drift; it is not silently bypassed by missing anchors.
- English suffix preservation is intact. Independent grep found `Control Logic Workbench</h1>`, `Probe &amp; Trace</h2>`, `Annotate &amp; Propose</h2>`, and `Hand off &amp; Track</h2>` only in [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:18).
- Live probe passed. `PYTHONPATH=src python3` serving `DemoRequestHandler` and `GET /workbench` returned `status=200`, `exact_match=True` against `src/well_harness/static/workbench.html`, with `工程师工作区`, `<h2>探针与追踪 · Probe &amp; Trace</h2>`, and `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` present.
- Truth-engine red line is preserved. `git diff --name-only main..938a5a2` only showed the 6 claimed files; there were no changes under `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`, `workbench.js`, or `workbench.css`.
- Cross-contract compatibility spot-check passed. `pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py tests/test_workbench_dual_route.py tests/test_workbench_shell.py` completed `126 passed`. I did not rerun the full `1078`-test suite.

P4 — V&V Engineer (Tier-B, E11-15c)

