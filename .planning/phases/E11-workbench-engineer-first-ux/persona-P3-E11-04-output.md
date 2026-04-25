2026-04-25T18:01:23.638250Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T18:01:23.638326Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc5cd-b297-7083-9e89-8b1beb682895
--------
user
You are Codex GPT-5.4 acting as **Persona P3 — Demo Presenter** (Tier-B single-persona pipeline, E11-04 sub-phase).

# Context — E11-04 annotation vocabulary upgrade

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-04-annotation-vocab-20260426`
**PR:** #20
**Worktree HEAD:** `54e701b` (single commit on top of main `08a1e0e`)

## What E11-04 ships

Per E11-00-PLAN row E11-04: relabel the four annotation toolbar buttons + the toolbar header + the active-tool status from generic UI types to domain-anchored Chinese verbs that match the engineer's mental model. Underlying type IDs (`data-annotation-tool="point"/"area"/"link"/"text-range"`) stay stable.

| Old | New |
|---|---|
| Annotation (header) | 标注 |
| Point | 标记信号 (mark a signal) |
| Area | 圈选 logic gate (encircle a logic gate) |
| Link | 关联 spec (link to a spec) |
| Text Range | 引用 requirement 段 (cite a requirement section) |

Plus:
- Default `#workbench-annotation-active-tool` text: `Point tool active` → `标记信号 工具激活`
- `annotation_overlay.js:setActiveTool()` now maps tool ID via `TOOL_DOMAIN_LABEL` and renders `${label} 工具激活`

## Files in scope

- `src/well_harness/static/workbench.html` — toolbar block (lines ~189-198)
- `src/well_harness/static/annotation_overlay.js` — `setActiveTool()` (lines ~161-180)
- `tests/test_workbench_annotation_vocab.py` — NEW (20 tests, all 4 toolbar buttons + active-tool status + stable IDs + JS map)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended E11-04 entry

## Your specific lens (P3 Demo Presenter)

Focus on:
- Does the new domain vocabulary land for a live demo / engineer walkthrough?
- Are the Chinese labels readable and unambiguous from across the room?
- Do they convey the *purpose* of each tool, or could a presenter still mis-name them on stage?
- Does the active-tool status sentence ("X 工具激活") read naturally?
- Any internal jargon left in the toolbar surface?

## Verification status

- 976 / 976 pytest pass (20 new in `test_workbench_annotation_vocab.py`)
- Truth-engine red line preserved: only `static/workbench.html`, `static/annotation_overlay.js`, `tests/test_workbench_annotation_vocab.py`, and `.planning/` files touched

## Out of scope

- Annotation overlay rendering / marker rendering / inbox queue UI — separate sub-phases
- The `eyebrow` / column-3 skeleton chrome (P3 deferred NIT from E11-03) — future surface buildout
- Backend annotation persistence — explicit out-of-scope (truth-engine red line)

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path: e.g. boot demo_server, GET /workbench, verify rendered text. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..54e701b` shows only the in-scope path types.

Sign as: **P3 — Demo Presenter (Tier-B, E11-04)**
codex
Reviewing PR #20 as P3 Demo Presenter. I’m first checking prior repo guidance from memory, then I’ll inspect the exact diff, read the touched UI files/tests, and do a live `/workbench` probe to verify the vocabulary lands in the running surface.
exec
/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|E11|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
49:# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
52:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
58:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)
68:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, single copy-paste prompt delivered for Claude Code)
78:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, factual framing tightened after Claude critique)
109:# Task Group: AI FANTUI LogicMVP C919 E-TRAS reliability simulation candidates and adoption handoff
112:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s C919 E-TRAS workstation and candidate-handoff workflow, but branch names, commit SHAs, Notion pages, and demo URLs are checkout-specific.
118:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, candidate UI shipped on isolated branch after runtime fix)
128:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, Notion/GitHub handoff completed with pushed branch and final fix commit)
304:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
310:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
320:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
610:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, demo-first narrowing report without code changes)
620:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, Chinese Claude Code brief delivered in requested structure)
738:## Task 4: Keep the Phase 1 bounded-action-plan workflow truthful in both acceptance and local workbench UI
742:- rollout_summaries/2026-03-31T11-31-58-UgBd-phase1_copilot_workbench_upstream_integration_and_unsupporte.md (cwd=/Users/Zhuanz/Documents/20260330 Jerry AI CFD Project, rollout_path=/Users/Zhuanz/.codex/sessions/2026/03/31/rollout-2026-03-31T19-31-58-019d43aa-28aa-7711-8401-f53e905c11b3.jsonl, updated_at=2026-04-08T14:09:09+00:00, thread_id=019d43aa-28aa-7711-8401-f53e905c11b3, local workbench switched to upstream artifact and unsupported wording repaired)
747:- bounded_action_plan, Phase1BoundedActionPlan, supported, clarification_needed, unsupported, result_output_surface, phase1_bounded_action_plan_only, local_review_surface, workbench upstream integration, narrow Phase 1 bounded planning boundary
753:- rollout_summaries/2026-04-02T04-41-46-kVGb-phase1_ui_distance_and_interactive_postprocess_workbench.md (cwd=/Users/Zhuanz/Documents/20260330 Jerry AI CFD Project, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/02/rollout-2026-04-02T12-41-46-019d4c7f-5489-7a63-be71-48d72549d01b.jsonl, updated_at=2026-04-07T19:00:24+00:00, thread_id=019d4c7f-5489-7a63-be71-48d72549d01b, static review seed distinguished from the desired interactive workbench)
757:- UI demo, 整个真实工作流程的UI界面, 不能只是静态UI, 自然语言交互, interactive_postprocess_workbench_v1, local_review_surface, phase1_report_review_seed_page.py, 37 passed, workflow visualization
767:- when wiring the local workbench, the user asked to "把 UI workbench 切到真实 bounded action plan upstream artifact" and explicitly split `clarification_needed` from `unsupported` -> prefer upstream-backed truthful status rendering over demo-only hardcoding or softened empty-state wording [Task 4]
774:- The bounded-action-plan / workbench loop should stay truthful about `supported`, `clarification_needed`, and `unsupported`; the user reacts strongly to softened or blended status wording [Task 1]
778:- `local_review_surface/phase1_copilot_workbench.py` now consumes the real upstream `build_bounded_action_plan(...)` output, carries `action_plan_support_status` / `action_plan_note` / `action_plan_output_kind`, and should remain a local HTML-only, advisory-only surface [Task 4]
780:- The currently implemented UI surface is still a deterministic local HTML review seed; an NL-driven postprocess cockpit belongs to a separate governed proposal such as `interactive_postprocess_workbench_v1`, not to the already-accepted static Phase 1 path [Task 5]
787:- Symptom: a Phase 1 workbench shows generic empty-state wording even when the request is outside scope -> cause: unsupported and clarification-needed were collapsed into one message -> fix: branch explicitly on `ACTION_PLAN_UNSUPPORTED_STATUS` and preserve the stronger unsupported boundary copy [Task 4]
789:- Symptom: a future agent overstates how close the repo is to a "real UI" -> cause: the deterministic review seed was mistaken for an interactive workbench -> fix: say clearly that the static Phase 1 chain is real and tested, but NL-triggered postprocessing and workflow control need a new governed phase [Task 5]
791:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
793:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
794:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
800:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
804:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
810:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
811:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
817:## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts
821:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
822:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
838:- The workbench’s fingerprint board and onboarding action board both reused existing payload fields; future UI additions should prefer wiring into current payloads over new backend contracts [Task 3]
848:# Task Group: AI FANTUI LogicMVP demo presentation, launch behavior, and leadership-facing communication
851:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
857:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, iterative refinement from user corrections)
858:- rollout_summaries/2026-04-07T06-20-24-tGb4-round_92_direct_vdt_control_flatter_logic_board.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-20-24-019d6699-6f65-7712-ba2d-13ed0f64e87e.jsonl, updated_at=2026-04-08T14:50:07+00:00, thread_id=019d6699-6f65-7712-ba2d-13ed0f64e87e, final Round 92 reflow with preserved endpoint contracts)
868:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
878:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
879:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
889:- rollout_summaries/2026-04-08T15-04-09-7j1J-reconstruct_ai_coding_development_log_and_leadership_speech.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-04-09-019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf.jsonl, updated_at=2026-04-08T15:12:08+00:00, thread_id=019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf, detailed Chinese summary and 5-minute leadership speech)
899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
900:- rollout_summaries/2026-04-07T05-30-48-VWde-thrust_reverser_harness_audit_and_control_freeze.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T13-30-48-019d666c-0536-7403-80c3-1216c53a4944.jsonl, updated_at=2026-04-08T08:22:56+00:00, thread_id=019d666c-0536-7403-80c3-1216c53a4944, frozen controller truth and simplified-plant caveat)
1189:- In this repo, the generator scripts under the external CFD workbench path were a more reliable evidence source than the rendered PDFs; when `pdftotext` is unavailable and `matplotlib` temp/cache paths are broken, parse scripts as text or AST instead of importing them [Task 1]

exec
/bin/zsh -lc "git status --short && printf '\\n---\\n' && git rev-parse --abbrev-ref HEAD && printf '\\n---\\n' && git rev-parse HEAD && printf '\\n---\\n' && git merge-base main 54e701b && printf '\\n---\\n' && git diff --name-only main..54e701b" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-prompt.txt
?? uv.lock

---
feat/e11-04-annotation-vocab-20260426

---
54e701b5e5d435f395ea2b4776984ad47ba9a2ee

---
08a1e0e09132dc6abf30990ee66bb84ea794caa6

---
.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/annotation_overlay.js
src/well_harness/static/workbench.html
tests/test_workbench_annotation_vocab.py

codex
The diff is scoped correctly relative to `main..54e701b`; the only extra files in the worktree are two local persona artifacts and `uv.lock`, which are untracked and outside the reviewed commit. I’m reading the touched HTML/JS/tests now, then I’ll launch the demo surface and verify the rendered labels over HTTP.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '170,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   170	            an observed reading — for example, editing a snapshot input field before running a scenario.
   171	            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
   172	          </span>
   173	          <strong>That mode is advisory.</strong>
   174	          <span>
   175	            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   176	            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   177	          </span>
   178	        </div>
   179	        <button
   180	          type="button"
   181	          class="workbench-trust-banner-dismiss"
   182	          aria-label="Hide trust banner for this session"
   183	          data-trust-banner-dismiss
   184	        >
   185	          Hide for session
   186	        </button>
   187	      </aside>
   188	
   189	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   190	        <span class="workbench-annotation-toolbar-label">标注</span>
   191	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
   192	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
   193	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
   194	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
   195	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   196	          标记信号 工具激活
   197	        </span>
   198	      </section>
   199	
   200	      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
   201	        <article
   202	          id="workbench-control-panel"
   203	          class="workbench-collab-column workbench-annotation-surface"
   204	          data-column="control"
   205	          data-annotation-surface="control"
   206	          tabindex="0"
   207	        >
   208	          <header>
   209	            <p class="eyebrow">probe &amp; trace</p>
   210	            <h2>Probe &amp; Trace · 探针与追踪</h2>
   211	          </header>
   212	          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
   213	            Waiting for probe &amp; trace panel boot.
   214	          </div>
   215	          <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
   216	            <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
   217	            <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
   218	          </div>
   219	        </article>
   220	

exec
/bin/zsh -lc 'git diff --unified=80 main..54e701b -- src/well_harness/static/workbench.html src/well_harness/static/annotation_overlay.js tests/test_workbench_annotation_vocab.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/annotation_overlay.js b/src/well_harness/static/annotation_overlay.js
index b7eb309..96be6e1 100644
--- a/src/well_harness/static/annotation_overlay.js
+++ b/src/well_harness/static/annotation_overlay.js
@@ -81,116 +81,128 @@
       updated_at: observedAt,
       source: {
         ui: "workbench.annotation_overlay",
       },
     };
   }
 
   function loadDrafts() {
     try {
       const raw = window.localStorage.getItem(draftStorageKey);
       return raw ? JSON.parse(raw) : [];
     } catch (error) {
       return [];
     }
   }
 
   function persistDraft(draft) {
     const drafts = loadDrafts();
     drafts.push(draft);
     window.localStorage.setItem(draftStorageKey, JSON.stringify(drafts.slice(-50)));
   }
 
   function renderMarker(surfaceElement, draft) {
     const marker = document.createElement("span");
     marker.className = "workbench-annotation-marker";
     marker.dataset.tool = draft.tool;
     marker.title = `${draft.tool} annotation`;
     marker.style.left = `${Math.round((draft.anchor.x || 0) * 100)}%`;
     marker.style.top = `${Math.round((draft.anchor.y || 0) * 100)}%`;
     if (draft.tool === "area") {
       marker.style.width = `${Math.round((draft.anchor.width || 0.16) * 100)}%`;
       marker.style.height = `${Math.round((draft.anchor.height || 0.12) * 100)}%`;
     }
     surfaceElement.appendChild(marker);
   }
 
   function renderInboxDraft(draft) {
     const list = document.getElementById("annotation-inbox-list");
     if (!list) {
       return;
     }
     if (list.children.length === 1 && list.children[0].textContent === "No proposals submitted yet.") {
       list.textContent = "";
     }
     const item = document.createElement("li");
     item.className = "workbench-annotation-draft";
     item.textContent = `${draft.tool} on ${draft.surface}: ${draft.note}`;
     list.prepend(item);
   }
 
   function buildAnchorForTool(tool, surfaceElement, event) {
     const point = normalizePoint(event, surfaceElement);
     if (tool === "area") {
       return { ...point, width: 0.22, height: 0.16 };
     }
     if (tool === "link") {
       return { ...point, href: window.location.href, selector: `#${surfaceElement.id}` };
     }
     if (tool === "text-range") {
       return selectedTextAnchor(surfaceElement) || { ...point, selector: `#${surfaceElement.id}`, text_quote: "" };
     }
     return point;
   }
 
   function handleSurfaceClick(event) {
     const surfaceElement = event.currentTarget;
     const surface = surfaceElement.dataset.annotationSurface;
     if (!surfaces.includes(surface)) {
       return;
     }
     const draft = createAnnotationDraft({
       tool: activeTool,
       surface,
       anchor: buildAnchorForTool(activeTool, surfaceElement, event),
     });
     persistDraft(draft);
     renderMarker(surfaceElement, draft);
     renderInboxDraft(draft);
   }
 
+  // E11-04 (2026-04-26): map underlying annotation type IDs to the
+  // domain-anchored labels rendered on the toolbar. The IDs stay stable
+  // (e2e selectors depend on data-annotation-tool="point" etc.); only the
+  // visible status copy changes.
+  const TOOL_DOMAIN_LABEL = {
+    "point": "标记信号",
+    "area": "圈选 logic gate",
+    "link": "关联 spec",
+    "text-range": "引用 requirement 段",
+  };
+
   function setActiveTool(tool) {
     if (!tools.includes(tool)) {
       return;
     }
     activeTool = tool;
     document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
       const pressed = button.dataset.annotationTool === activeTool;
       button.classList.toggle("is-active", pressed);
       button.setAttribute("aria-pressed", String(pressed));
     });
     const status = document.getElementById("workbench-annotation-active-tool");
     if (status) {
-      status.textContent = `${tool} tool active`;
+      const label = TOOL_DOMAIN_LABEL[tool] || tool;
+      status.textContent = `${label} 工具激活`;
     }
   }
 
   function installAnnotationOverlay() {
     document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
       button.addEventListener("click", () => setActiveTool(button.dataset.annotationTool));
     });
     document.querySelectorAll("[data-annotation-surface]").forEach((surfaceElement) => {
       surfaceElement.addEventListener("click", handleSurfaceClick);
     });
     setActiveTool(activeTool);
   }
 
   window.WorkbenchAnnotationOverlay = {
     tools,
     surfaces,
     createAnnotationDraft,
     installAnnotationOverlay,
     setActiveTool,
   };
 
   window.addEventListener("DOMContentLoaded", installAnnotationOverlay);
 })();
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index a706072..2782e52 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -110,167 +110,167 @@
               type="button"
               class="workbench-wow-run-button"
               data-wow-action="run"
               data-wow-id="wow_b"
             >
               一键运行 wow_b
             </button>
             <div
               class="workbench-wow-result"
               data-wow-result-for="wow_b"
               role="status"
               aria-live="polite"
             >
               尚未运行。
             </div>
           </article>
           <article
             class="workbench-wow-card"
             data-wow-id="wow_c"
             aria-labelledby="workbench-wow-c-title"
           >
             <header>
               <span class="workbench-wow-tag">wow_c</span>
               <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
               触发该 outcome 的参数组合（max_results=10）。
             </p>
             <button
               type="button"
               class="workbench-wow-run-button"
               data-wow-action="run"
               data-wow-id="wow_c"
             >
               一键运行 wow_c
             </button>
             <div
               class="workbench-wow-result"
               data-wow-result-for="wow_c"
               role="status"
               aria-live="polite"
             >
               尚未运行。
             </div>
           </article>
         </div>
       </section>
 
       <aside
         id="workbench-trust-banner"
         class="workbench-trust-banner"
         data-feedback-mode="manual_feedback_override"
         role="note"
         aria-label="Feedback mode trust affordance"
       >
         <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
         <div class="workbench-trust-banner-body">
           <span class="workbench-trust-banner-scope">
             <em>What "manual feedback" means here:</em> any value you type into the workbench to override
             an observed reading — for example, editing a snapshot input field before running a scenario.
             Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
           </span>
           <strong>That mode is advisory.</strong>
           <span>
             Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
             Your manual feedback is recorded for diff/review but does not change source-of-truth values.
           </span>
         </div>
         <button
           type="button"
           class="workbench-trust-banner-dismiss"
           aria-label="Hide trust banner for this session"
           data-trust-banner-dismiss
         >
           Hide for session
         </button>
       </aside>
 
       <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
-        <span class="workbench-annotation-toolbar-label">Annotation</span>
-        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">Point</button>
-        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">Area</button>
-        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">Link</button>
-        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">Text Range</button>
+        <span class="workbench-annotation-toolbar-label">标注</span>
+        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
+        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
+        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
+        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
         <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
-          Point tool active
+          标记信号 工具激活
         </span>
       </section>
 
       <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
         <article
           id="workbench-control-panel"
           class="workbench-collab-column workbench-annotation-surface"
           data-column="control"
           data-annotation-surface="control"
           tabindex="0"
         >
           <header>
             <p class="eyebrow">probe &amp; trace</p>
             <h2>Probe &amp; Trace · 探针与追踪</h2>
           </header>
           <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
             Waiting for probe &amp; trace panel boot.
           </div>
           <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
             <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
             <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
           </div>
         </article>
 
         <article
           id="workbench-document-panel"
           class="workbench-collab-column workbench-annotation-surface"
           data-column="document"
           data-annotation-surface="document"
           tabindex="0"
         >
           <header>
             <p class="eyebrow">annotate &amp; propose</p>
             <h2>Annotate &amp; Propose · 标注与提案</h2>
           </header>
           <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
             Waiting for annotate &amp; propose panel boot.
           </div>
           <div class="workbench-collab-document">
             <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
             <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
           </div>
         </article>
 
         <article
           id="workbench-circuit-panel"
           class="workbench-collab-column workbench-annotation-surface"
           data-column="circuit"
           data-annotation-surface="circuit"
           tabindex="0"
         >
           <header>
             <p class="eyebrow">hand off &amp; track</p>
             <h2>Hand off &amp; Track · 移交与跟踪</h2>
           </header>
           <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
             Waiting for hand off &amp; track panel boot.
           </div>
           <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
             <span>SW1</span>
             <span>Logic 1</span>
             <span>Logic 2</span>
             <span>Logic 3</span>
             <span>Logic 4</span>
             <span>THR LOCK</span>
           </div>
         </article>
       </section>
 
       <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
         <header>
           <p class="eyebrow">annotation inbox</p>
           <h2>Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
           <li>No proposals submitted yet.</li>
         </ul>
       </aside>
 
       <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
diff --git a/tests/test_workbench_annotation_vocab.py b/tests/test_workbench_annotation_vocab.py
new file mode 100644
index 0000000..995a47d
--- /dev/null
+++ b/tests/test_workbench_annotation_vocab.py
@@ -0,0 +1,158 @@
+"""E11-04 — annotation vocabulary upgrade regression lock.
+
+Locks the domain-anchored annotation toolbar copy after the E11-04
+relabel from generic UI types to engineer-domain verbs:
+
+  Annotation toolbar label:  Annotation        → 标注
+  Point                      → 标记信号
+  Area                       → 圈选 logic gate
+  Link                       → 关联 spec
+  Text Range                 → 引用 requirement 段
+
+Per E11-00-PLAN row E11-04: underlying type IDs (data-annotation-tool=
+"point"/"area"/"link"/"text-range") stay stable so e2e selectors and the
+annotation_overlay.js click handlers don't break. Verify both invariants —
+new visible labels AND preserved IDs — so a future "polish" pass can't
+silently regress either side.
+"""
+
+from __future__ import annotations
+
+import http.client
+import re
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
+# ─── 1. Domain-anchored visible labels are present ──────────────────
+
+
+@pytest.mark.parametrize(
+    "label",
+    [
+        ">标注<",  # toolbar header
+        ">标记信号<",  # point button
+        ">圈选 logic gate<",  # area button
+        ">关联 spec<",  # link button
+        ">引用 requirement 段<",  # text-range button
+    ],
+)
+def test_workbench_html_carries_domain_label(label: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert label in html, f"missing domain-anchored label: {label}"
+
+
+def test_workbench_html_default_active_tool_uses_domain_label() -> None:
+    """Pre-hydration default in #workbench-annotation-active-tool must use
+    the domain label rather than the generic "Point tool active"."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert "标记信号 工具激活" in html
+
+
+# ─── 2. Generic UI-type labels removed ───────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "stale",
+    [
+        ">Annotation<",
+        ">Point<",
+        ">Area<",
+        ">Link<",
+        ">Text Range<",
+        "Point tool active",
+    ],
+)
+def test_workbench_html_drops_stale_generic_label(stale: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale not in html, f"stale generic label still present: {stale}"
+
+
+# ─── 3. Underlying data-annotation-tool tokens preserved ────────────
+#
+# Per E11-00-PLAN row E11-04: relabel touches *visible copy only*. The
+# data-annotation-tool tokens are anchors for annotation_overlay.js
+# click handlers and any e2e selectors, so they MUST stay stable.
+
+
+@pytest.mark.parametrize(
+    "anchor",
+    [
+        'data-annotation-tool="point"',
+        'data-annotation-tool="area"',
+        'data-annotation-tool="link"',
+        'data-annotation-tool="text-range"',
+        'id="workbench-annotation-toolbar"',
+        'id="workbench-annotation-active-tool"',
+    ],
+)
+def test_workbench_html_preserves_stable_tool_anchor(anchor: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert anchor in html, f"E11-04 broke stable annotation anchor: {anchor}"
+
+
+# ─── 4. annotation_overlay.js status template uses domain labels ────
+
+
+def test_annotation_overlay_uses_tool_domain_label_map() -> None:
+    js = (STATIC_DIR / "annotation_overlay.js").read_text(encoding="utf-8")
+    assert "TOOL_DOMAIN_LABEL" in js
+    # Each tool ID must map to its domain label.
+    assert '"point": "标记信号"' in js
+    assert '"area": "圈选 logic gate"' in js
+    assert '"link": "关联 spec"' in js
+    assert '"text-range": "引用 requirement 段"' in js
+    # The status template must use the label, not the raw tool ID.
+    assert "${label} 工具激活" in js
+    # The old generic template must not remain in the file.
+    assert "${tool} tool active" not in js
+
+
+# ─── 5. Live-served /workbench reflects the relabel end-to-end ──────
+
+
+def test_workbench_route_serves_relabel(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    # New domain labels
+    assert ">标记信号<" in html
+    assert ">圈选 logic gate<" in html
+    assert ">关联 spec<" in html
+    assert ">引用 requirement 段<" in html
+    # Stable anchors still served
+    assert 'data-annotation-tool="point"' in html
+    assert 'data-annotation-tool="text-range"' in html

exec
/bin/zsh -lc "nl -ba tests/test_workbench_annotation_vocab.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/annotation_overlay.js | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	(function () {
     2	  const tools = ["point", "area", "link", "text-range"];
     3	  const surfaces = ["control", "document", "circuit"];
     4	  const draftStorageKey = "well-harness-workbench-annotation-drafts-v1";
     5	  let activeTool = "point";
     6	  let draftSequence = 0;
     7	
     8	  function clampUnit(value) {
     9	    if (!Number.isFinite(value)) {
    10	      return 0;
    11	    }
    12	    return Math.max(0, Math.min(1, value));
    13	  }
    14	
    15	  function normalizePoint(event, element) {
    16	    const bounds = element.getBoundingClientRect();
    17	    return {
    18	      x: clampUnit((event.clientX - bounds.left) / bounds.width),
    19	      y: clampUnit((event.clientY - bounds.top) / bounds.height),
    20	    };
    21	  }
    22	
    23	  function currentTicketId() {
    24	    const ticket = document.getElementById("workbench-ticket");
    25	    return ticket ? ticket.dataset.ticket || "WB-LOCAL" : "WB-LOCAL";
    26	  }
    27	
    28	  function currentSystemId() {
    29	    const selector = document.getElementById("workbench-system-select");
    30	    return selector ? selector.value : "thrust-reverser";
    31	  }
    32	
    33	  function currentAuthor() {
    34	    const identity = document.getElementById("workbench-identity");
    35	    if (!identity) {
    36	      return "local-engineer";
    37	    }
    38	    const label = identity.querySelector("strong");
    39	    return label ? label.textContent.trim() : "local-engineer";
    40	  }
    41	
    42	  function timestamp() {
    43	    return new Date().toISOString();
    44	  }
    45	
    46	  function draftId() {
    47	    draftSequence += 1;
    48	    return `prop_local_${Date.now()}_${draftSequence}`;
    49	  }
    50	
    51	  function selectedTextAnchor(surfaceElement) {
    52	    const selection = window.getSelection ? window.getSelection() : null;
    53	    if (!selection || selection.rangeCount === 0 || !selection.toString().trim()) {
    54	      return null;
    55	    }
    56	    const range = selection.getRangeAt(0);
    57	    if (!surfaceElement.contains(range.commonAncestorContainer)) {
    58	      return null;
    59	    }
    60	    return {
    61	      selector: `#${surfaceElement.id}`,
    62	      start_offset: 0,
    63	      end_offset: selection.toString().length,
    64	      text_quote: selection.toString().trim(),
    65	    };
    66	  }
    67	
    68	  function createAnnotationDraft(input) {
    69	    const observedAt = timestamp();
    70	    return {
    71	      id: input.id || draftId(),
    72	      tool: input.tool,
    73	      surface: input.surface,
    74	      anchor: input.anchor,
    75	      note: input.note || `${input.tool} annotation on ${input.surface}`,
    76	      author: input.author || currentAuthor(),
    77	      ticket_id: input.ticket_id || currentTicketId(),
    78	      system_id: input.system_id || currentSystemId(),
    79	      status: "pending",
    80	      created_at: observedAt,
    81	      updated_at: observedAt,
    82	      source: {
    83	        ui: "workbench.annotation_overlay",
    84	      },
    85	    };
    86	  }
    87	
    88	  function loadDrafts() {
    89	    try {
    90	      const raw = window.localStorage.getItem(draftStorageKey);
    91	      return raw ? JSON.parse(raw) : [];
    92	    } catch (error) {
    93	      return [];
    94	    }
    95	  }
    96	
    97	  function persistDraft(draft) {
    98	    const drafts = loadDrafts();
    99	    drafts.push(draft);
   100	    window.localStorage.setItem(draftStorageKey, JSON.stringify(drafts.slice(-50)));
   101	  }
   102	
   103	  function renderMarker(surfaceElement, draft) {
   104	    const marker = document.createElement("span");
   105	    marker.className = "workbench-annotation-marker";
   106	    marker.dataset.tool = draft.tool;
   107	    marker.title = `${draft.tool} annotation`;
   108	    marker.style.left = `${Math.round((draft.anchor.x || 0) * 100)}%`;
   109	    marker.style.top = `${Math.round((draft.anchor.y || 0) * 100)}%`;
   110	    if (draft.tool === "area") {
   111	      marker.style.width = `${Math.round((draft.anchor.width || 0.16) * 100)}%`;
   112	      marker.style.height = `${Math.round((draft.anchor.height || 0.12) * 100)}%`;
   113	    }
   114	    surfaceElement.appendChild(marker);
   115	  }
   116	
   117	  function renderInboxDraft(draft) {
   118	    const list = document.getElementById("annotation-inbox-list");
   119	    if (!list) {
   120	      return;
   121	    }
   122	    if (list.children.length === 1 && list.children[0].textContent === "No proposals submitted yet.") {
   123	      list.textContent = "";
   124	    }
   125	    const item = document.createElement("li");
   126	    item.className = "workbench-annotation-draft";
   127	    item.textContent = `${draft.tool} on ${draft.surface}: ${draft.note}`;
   128	    list.prepend(item);
   129	  }
   130	
   131	  function buildAnchorForTool(tool, surfaceElement, event) {
   132	    const point = normalizePoint(event, surfaceElement);
   133	    if (tool === "area") {
   134	      return { ...point, width: 0.22, height: 0.16 };
   135	    }
   136	    if (tool === "link") {
   137	      return { ...point, href: window.location.href, selector: `#${surfaceElement.id}` };
   138	    }
   139	    if (tool === "text-range") {
   140	      return selectedTextAnchor(surfaceElement) || { ...point, selector: `#${surfaceElement.id}`, text_quote: "" };
   141	    }
   142	    return point;
   143	  }
   144	
   145	  function handleSurfaceClick(event) {
   146	    const surfaceElement = event.currentTarget;
   147	    const surface = surfaceElement.dataset.annotationSurface;
   148	    if (!surfaces.includes(surface)) {
   149	      return;
   150	    }
   151	    const draft = createAnnotationDraft({
   152	      tool: activeTool,
   153	      surface,
   154	      anchor: buildAnchorForTool(activeTool, surfaceElement, event),
   155	    });
   156	    persistDraft(draft);
   157	    renderMarker(surfaceElement, draft);
   158	    renderInboxDraft(draft);
   159	  }
   160	
   161	  // E11-04 (2026-04-26): map underlying annotation type IDs to the
   162	  // domain-anchored labels rendered on the toolbar. The IDs stay stable
   163	  // (e2e selectors depend on data-annotation-tool="point" etc.); only the
   164	  // visible status copy changes.
   165	  const TOOL_DOMAIN_LABEL = {
   166	    "point": "标记信号",
   167	    "area": "圈选 logic gate",
   168	    "link": "关联 spec",
   169	    "text-range": "引用 requirement 段",
   170	  };
   171	
   172	  function setActiveTool(tool) {
   173	    if (!tools.includes(tool)) {
   174	      return;
   175	    }
   176	    activeTool = tool;
   177	    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
   178	      const pressed = button.dataset.annotationTool === activeTool;
   179	      button.classList.toggle("is-active", pressed);
   180	      button.setAttribute("aria-pressed", String(pressed));
   181	    });
   182	    const status = document.getElementById("workbench-annotation-active-tool");
   183	    if (status) {
   184	      const label = TOOL_DOMAIN_LABEL[tool] || tool;
   185	      status.textContent = `${label} 工具激活`;
   186	    }
   187	  }
   188	
   189	  function installAnnotationOverlay() {
   190	    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
   191	      button.addEventListener("click", () => setActiveTool(button.dataset.annotationTool));
   192	    });
   193	    document.querySelectorAll("[data-annotation-surface]").forEach((surfaceElement) => {
   194	      surfaceElement.addEventListener("click", handleSurfaceClick);
   195	    });
   196	    setActiveTool(activeTool);
   197	  }
   198	
   199	  window.WorkbenchAnnotationOverlay = {
   200	    tools,
   201	    surfaces,
   202	    createAnnotationDraft,
   203	    installAnnotationOverlay,
   204	    setActiveTool,
   205	  };
   206	
   207	  window.addEventListener("DOMContentLoaded", installAnnotationOverlay);
   208	})();

 succeeded in 0ms:
     1	"""E11-04 — annotation vocabulary upgrade regression lock.
     2	
     3	Locks the domain-anchored annotation toolbar copy after the E11-04
     4	relabel from generic UI types to engineer-domain verbs:
     5	
     6	  Annotation toolbar label:  Annotation        → 标注
     7	  Point                      → 标记信号
     8	  Area                       → 圈选 logic gate
     9	  Link                       → 关联 spec
    10	  Text Range                 → 引用 requirement 段
    11	
    12	Per E11-00-PLAN row E11-04: underlying type IDs (data-annotation-tool=
    13	"point"/"area"/"link"/"text-range") stay stable so e2e selectors and the
    14	annotation_overlay.js click handlers don't break. Verify both invariants —
    15	new visible labels AND preserved IDs — so a future "polish" pass can't
    16	silently regress either side.
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
    61	# ─── 1. Domain-anchored visible labels are present ──────────────────
    62	
    63	
    64	@pytest.mark.parametrize(
    65	    "label",
    66	    [
    67	        ">标注<",  # toolbar header
    68	        ">标记信号<",  # point button
    69	        ">圈选 logic gate<",  # area button
    70	        ">关联 spec<",  # link button
    71	        ">引用 requirement 段<",  # text-range button
    72	    ],
    73	)
    74	def test_workbench_html_carries_domain_label(label: str) -> None:
    75	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    76	    assert label in html, f"missing domain-anchored label: {label}"
    77	
    78	
    79	def test_workbench_html_default_active_tool_uses_domain_label() -> None:
    80	    """Pre-hydration default in #workbench-annotation-active-tool must use
    81	    the domain label rather than the generic "Point tool active"."""
    82	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    83	    assert "标记信号 工具激活" in html
    84	
    85	
    86	# ─── 2. Generic UI-type labels removed ───────────────────────────────
    87	
    88	
    89	@pytest.mark.parametrize(
    90	    "stale",
    91	    [
    92	        ">Annotation<",
    93	        ">Point<",
    94	        ">Area<",
    95	        ">Link<",
    96	        ">Text Range<",
    97	        "Point tool active",
    98	    ],
    99	)
   100	def test_workbench_html_drops_stale_generic_label(stale: str) -> None:
   101	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   102	    assert stale not in html, f"stale generic label still present: {stale}"
   103	
   104	
   105	# ─── 3. Underlying data-annotation-tool tokens preserved ────────────
   106	#
   107	# Per E11-00-PLAN row E11-04: relabel touches *visible copy only*. The
   108	# data-annotation-tool tokens are anchors for annotation_overlay.js
   109	# click handlers and any e2e selectors, so they MUST stay stable.
   110	
   111	
   112	@pytest.mark.parametrize(
   113	    "anchor",
   114	    [
   115	        'data-annotation-tool="point"',
   116	        'data-annotation-tool="area"',
   117	        'data-annotation-tool="link"',
   118	        'data-annotation-tool="text-range"',
   119	        'id="workbench-annotation-toolbar"',
   120	        'id="workbench-annotation-active-tool"',
   121	    ],
   122	)
   123	def test_workbench_html_preserves_stable_tool_anchor(anchor: str) -> None:
   124	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   125	    assert anchor in html, f"E11-04 broke stable annotation anchor: {anchor}"
   126	
   127	
   128	# ─── 4. annotation_overlay.js status template uses domain labels ────
   129	
   130	
   131	def test_annotation_overlay_uses_tool_domain_label_map() -> None:
   132	    js = (STATIC_DIR / "annotation_overlay.js").read_text(encoding="utf-8")
   133	    assert "TOOL_DOMAIN_LABEL" in js
   134	    # Each tool ID must map to its domain label.
   135	    assert '"point": "标记信号"' in js
   136	    assert '"area": "圈选 logic gate"' in js
   137	    assert '"link": "关联 spec"' in js
   138	    assert '"text-range": "引用 requirement 段"' in js
   139	    # The status template must use the label, not the raw tool ID.
   140	    assert "${label} 工具激活" in js
   141	    # The old generic template must not remain in the file.
   142	    assert "${tool} tool active" not in js
   143	
   144	
   145	# ─── 5. Live-served /workbench reflects the relabel end-to-end ──────
   146	
   147	
   148	def test_workbench_route_serves_relabel(server) -> None:
   149	    status, html = _get(server, "/workbench")
   150	    assert status == 200
   151	    # New domain labels
   152	    assert ">标记信号<" in html
   153	    assert ">圈选 logic gate<" in html
   154	    assert ">关联 spec<" in html
   155	    assert ">引用 requirement 段<" in html
   156	    # Stable anchors still served
   157	    assert 'data-annotation-tool="point"' in html
   158	    assert 'data-annotation-tool="text-range"' in html

codex
The UI copy change is small and isolated. I’m checking the actual served `/workbench` HTML next, because for this persona the key question is whether the vocabulary reads naturally in the live surface, not just in the static file or test fixture.
exec
/bin/zsh -lc "rg -n \"workbench|serve_forever|if __name__ == '__main__'|argparse|port\" src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
3:from __future__ import annotations
5:import argparse
6:from dataclasses import replace
7:from functools import lru_cache
8:import json
9:import math
10:import re
11:from typing import Any
12:import webbrowser
13:from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
14:from pathlib import Path
15:from urllib.parse import parse_qs, unquote, urlparse
17:from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
18:from well_harness.controller_adapter import build_reference_controller_adapter
19:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
20:from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
21:from well_harness.adapters.efds_adapter import build_efds_controller_adapter
22:from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
23:from well_harness.document_intake import (
31:from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
32:from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
33:from well_harness.plant import PlantState, SimplifiedDeployPlant
34:from well_harness.switches import LatchedThrottleSwitches, SwitchState
35:from well_harness.timeline_engine import (
40:from well_harness.timeline_engine.executors.fantui import FantuiExecutor
41:from well_harness.workbench_bundle import (
43:    archive_workbench_bundle,
44:    build_workbench_bundle,
45:    load_workbench_archive_manifest,
46:    load_workbench_archive_restore_payload,
70:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
71:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
72:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
73:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
74:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
217:            self._send_json(200, workbench_bootstrap_payload())
224:            self._send_json(200, workbench_recent_archives_payload())
238:        if parsed.path in ("/workbench/start", "/workbench/start.html"):
239:            self._serve_static("workbench_start.html")
242:        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
243:            self._serve_static("workbench_bundle.html")
246:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
247:            self._serve_static("workbench.html")
312:            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json."})
420:            response_payload, error_payload = build_workbench_bundle_response(request_payload)
427:            response_payload, error_payload = build_workbench_safe_repair_response(request_payload)
434:            response_payload, error_payload = build_workbench_archive_restore_response(request_payload)
443:            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
456:                    "error": f"system_id {system_id!r} is not supported for diagnosis. "
457:                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
463:                report = engine.diagnose_and_report(outcome, max_results=max_results)
464:                self._send_json(200, report)
471:            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
491:                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
492:                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
524:        import pathlib as _pathlib
525:        import well_harness as _wh
542:                from well_harness.hardware_schema import (
552:                import yaml
1029:            "error": "unsupported_system",
1209:def default_workbench_archive_root() -> Path:
1210:    return (Path.cwd() / "artifacts" / "workbench-bundles").resolve()
1213:def reference_workbench_packet_payload() -> dict:
1219:    # so workbench clients can still render the runtime panel without runtime error.
1238:def recent_workbench_archive_summaries(*, limit: int = 6) -> list[dict]:
1239:    archive_root = default_workbench_archive_root()
1251:            manifest = load_workbench_archive_manifest(manifest_path)
1283:def workbench_bootstrap_payload() -> dict:
1286:        "reference_packet": reference_workbench_packet_payload(),
1287:        "default_archive_root": str(default_workbench_archive_root()),
1288:        "recent_archives": recent_workbench_archive_summaries(),
1293:def workbench_recent_archives_payload() -> dict:
1295:        "default_archive_root": str(default_workbench_archive_root()),
1296:        "recent_archives": recent_workbench_archive_summaries(),
1366:    raise ValueError(f"Unsupported outcome: {outcome}")
1373:            "error": "unsupported_system",
1374:            "message": "sensitivity sweep currently supports only 'thrust-reverser'.",
1407:                f"Unsupported outcomes: {invalid_outcomes}. "
1468:            "error": "invalid_workbench_request",
1482:            "error": "invalid_workbench_request",
1493:            "error": "invalid_workbench_request",
1501:            "error": "invalid_workbench_request",
1513:            "error": "invalid_workbench_request",
1526:            "error": "invalid_workbench_request",
1533:def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
1537:            "error": "invalid_workbench_request",
1545:            "error": "invalid_workbench_packet",
1607:        bundle = build_workbench_bundle(
1624:            "error": "invalid_workbench_selection",
1630:        archive = archive_workbench_bundle(
1632:            default_workbench_archive_root(),
1640:        "default_archive_root": str(default_workbench_archive_root()),
1645:def build_workbench_safe_repair_response(request_payload: dict) -> tuple[dict | None, dict | None]:
1649:            "error": "invalid_workbench_request",
1655:            "error": "invalid_workbench_request",
1663:            "error": "invalid_workbench_packet",
1683:def build_workbench_archive_restore_response(request_payload: dict) -> tuple[dict | None, dict | None]:
1689:            "error": "invalid_workbench_request",
1700:        restore_payload = load_workbench_archive_restore_payload(manifest_path)
1703:            "error": "workbench_archive_not_found",
1711:            "error": "invalid_workbench_archive",
1716:    restore_payload["default_archive_root"] = str(default_workbench_archive_root())
2236:# Multi-system snapshot support (P13)
2323:            "lgcu1_mlg_wow_value": True,            # LGCU1 reports on-ground
2325:            "lgcu2_mlg_wow_value": True,            # LGCU2 reports on-ground
2708:def build_parser() -> argparse.ArgumentParser:
2709:    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
2711:    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
2723:def demo_url(host: str, port: int) -> str:
2724:    return f"http://{host}:{port}/index.html"
2740:    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
2741:    host, port = server.server_address
2742:    url = demo_url(host, port)
2747:        server.serve_forever()

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""Small local UI server for the deterministic demo reasoning layer."""
     2	
     3	from __future__ import annotations
     4	
     5	import argparse
     6	from dataclasses import replace
     7	from functools import lru_cache
     8	import json
     9	import math
    10	import re
    11	from typing import Any
    12	import webbrowser
    13	from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    14	from pathlib import Path
    15	from urllib.parse import parse_qs, unquote, urlparse
    16	
    17	from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
    18	from well_harness.controller_adapter import build_reference_controller_adapter
    19	from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
    20	from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
    21	from well_harness.adapters.efds_adapter import build_efds_controller_adapter
    22	from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
    23	from well_harness.document_intake import (
    24	    apply_safe_schema_repairs,
    25	    assess_intake_packet,
    26	    build_clarification_brief,
    27	    intake_packet_from_dict,
    28	    intake_packet_to_dict,
    29	    intake_template_payload,
    30	)
    31	from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
    32	from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
    33	from well_harness.plant import PlantState, SimplifiedDeployPlant
    34	from well_harness.switches import LatchedThrottleSwitches, SwitchState
    35	from well_harness.timeline_engine import (
    36	    TimelinePlayer,
    37	    ValidationError as TimelineValidationError,
    38	    parse_timeline,
    39	)
    40	from well_harness.timeline_engine.executors.fantui import FantuiExecutor
    41	from well_harness.workbench_bundle import (
    42	    SandboxEscapeError,
    43	    archive_workbench_bundle,
    44	    build_workbench_bundle,
    45	    load_workbench_archive_manifest,
    46	    load_workbench_archive_restore_payload,
    47	)
    48	STATIC_DIR = Path(__file__).with_name("static")
    49	REFERENCE_PACKET_DIR = Path(__file__).with_name("reference_packets")
    50	REFERENCE_PACKET_PATH = REFERENCE_PACKET_DIR / "custom_reverse_control_v1.json"
    51	REPO_ROOT = Path(__file__).resolve().parents[2]
    52	RUNS_DIR = REPO_ROOT / "runs"
    53	DEFAULT_HOST = "127.0.0.1"
    54	DEFAULT_PORT = 8000
    55	# Server-side DoS guard: 10 MB, aligned with browser client limit.
    56	_MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
    57	CONTENT_TYPES = {
    58	    ".html": "text/html; charset=utf-8",
    59	    ".css": "text/css; charset=utf-8",
    60	    ".js": "application/javascript; charset=utf-8",
    61	    ".json": "application/json; charset=utf-8",
    62	    ".svg": "image/svg+xml; charset=utf-8",
    63	    ".ico": "image/x-icon",
    64	    ".png": "image/png",
    65	}
    66	SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
    67	SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
    68	TRA_L4_LOCK_DEG = -14.0
    69	MONITOR_TIMELINE_PATH = "/api/monitor-timeline"
    70	WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
    71	WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
    72	WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
    73	WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
    74	WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
    75	MONITOR_RA_START_FT = 7.0
    76	MONITOR_RA_RATE_FT_PER_S = 1.0
    77	MONITOR_TRA_START_S = 1.0
    78	MONITOR_TRA_RATE_DEG_PER_S = 10.0
    79	MONITOR_TRA_LOCK_DEG = -14.0
    80	MONITOR_VDT_START_S = 2.4
    81	MONITOR_VDT_RATE_PERCENT_PER_S = 50.0
    82	MONITOR_ACTIVE_END_S = 4.4
    83	MONITOR_TIMELINE_END_S = 7.0
    84	MONITOR_TIMELINE_COMPRESSION_RATIO = 10.0
    85	MONITOR_ENGINE_RUNNING = True
    86	MONITOR_AIRCRAFT_ON_GROUND = True
    87	MONITOR_REVERSER_INHIBITED = False
    88	MONITOR_EEC_ENABLE = True
    89	
    90	# Reverse diagnosis API (P19.6)
    91	DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
    92	# Monte Carlo reliability API (P19.7)
    93	MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
    94	# Hardware schema discovery (P19.8)
    95	HARDWARE_SCHEMA_PATH = "/api/hardware/schema"
    96	SENSITIVITY_SWEEP_PATH = "/api/sensitivity-sweep"
    97	# FANTUI stateful tick endpoints — live counterpart to C919 /api/tick.
    98	# The existing /api/lever-snapshot stays stateless; this triad is separate
    99	# so the two surfaces don't fight each other or share global state.
   100	FANTUI_TICK_PATH = "/api/fantui/tick"
   101	FANTUI_RESET_PATH = "/api/fantui/reset"
   102	FANTUI_LOG_PATH = "/api/fantui/log"
   103	FANTUI_STATE_PATH = "/api/fantui/state"
   104	FANTUI_SET_VDT_PATH = "/api/fantui/set_vdt"
   105	
   106	STATIC_ROUTE_ALIASES = {
   107	    "/favicon.ico": "favicon.svg",
   108	    "/apple-touch-icon.png": "apple-touch-icon.svg",
   109	}
   110	
   111	SENSITIVITY_SWEEP_DEFAULT_RA_VALUES = (2.0, 5.0, 10.0, 20.0, 40.0)
   112	SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES = (-28.0, -20.0, -15.0, -11.0, -6.0)
   113	SENSITIVITY_SWEEP_DEFAULT_OUTCOMES = (
   114	    "logic1_active",
   115	    "logic3_active",
   116	    "thr_lock_active",
   117	    "deploy_confirmed",
   118	)
   119	SENSITIVITY_SWEEP_ALLOWED_OUTCOMES = frozenset(
   120	    {
   121	        "logic1_active",
   122	        "logic2_active",
   123	        "logic3_active",
   124	        "thr_lock_active",
   125	        "deploy_confirmed",
   126	        "tls_unlocked",
   127	        "pls_unlocked",
   128	    }
   129	)
   130	
   131	_SYSTEM_YAML_MAP = {
   132	    "thrust-reverser": "thrust_reverser_hardware_v1.yaml",
   133	    "landing-gear": "landing_gear_hardware_v1.yaml",
   134	    "bleed-air": "bleed_air_hardware_v1.yaml",
   135	    "c919-etras": "c919_etras_hardware_v1.yaml",
   136	}
   137	
   138	# Systems whose YAML format is loadable by load_thrust_reverser_hardware.
   139	# Landing-gear and bleed-air YAMLs use a different schema and cannot be loaded
   140	# by the thrust-reverser-specific engine; they are served via the generic loader
   141	# in _handle_hardware_schema only.
   142	_SUPPORTED_FOR_ANALYSIS = frozenset({"thrust-reverser"})
   143	
   144	MONITOR_N1K = 35.0
   145	MONITOR_MAX_N1K_DEPLOY_LIMIT = 60.0
   146	LEVER_NUMERIC_INPUTS = {
   147	    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
   148	    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
   149	    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
   150	    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
   151	}
   152	LEVER_BOOLEAN_INPUTS = {
   153	    "engine_running": True,
   154	    "aircraft_on_ground": True,
   155	    "reverser_inhibited": False,
   156	    "eec_enable": True,
   157	}
   158	LEVER_FEEDBACK_MODES = {
   159	    "auto_scrubber",
   160	    "manual_feedback_override",
   161	}
   162	LEVER_SNAPSHOT_FAULT_NODE_ALIASES = {
   163	    "sw1_input": "sw1",
   164	    "sw2_input": "sw2",
   165	}
   166	LEVER_SNAPSHOT_FAULT_NODES = {
   167	    "sw1",
   168	    "sw2",
   169	    "radio_altitude_ft",
   170	    "n1k",
   171	    "tls115",
   172	    "logic1",
   173	    "logic2",
   174	    "logic3",
   175	    "logic4",
   176	    "thr_lock",
   177	    "vdt90",
   178	    "sw1_input",
   179	    "sw2_input",
   180	}
   181	LEVER_SNAPSHOT_FAULT_TYPES = {
   182	    "stuck_off",
   183	    "stuck_on",
   184	    "sensor_zero",
   185	    "logic_stuck_false",
   186	    "cmd_blocked",
   187	}
   188	FAULT_INJECTION_REASON = "fault_injection"
   189	
   190	# ── FANTUI stateful tick singleton ─────────────────────────────────────────
   191	# Module-level state. ``FantuiTickSystem`` is itself thread-safe — see its
   192	# internal ``_lock`` — so no outer lock is needed here. Restarting the server
   193	# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
   194	# ``_FANTUI_LOCK`` is kept as an alias to the system's internal lock for
   195	# backward-compatibility with any test that reached in directly.
   196	_FANTUI_SYSTEM = FantuiTickSystem()
   197	_FANTUI_LOCK = _FANTUI_SYSTEM._lock
   198	
   199	
   200	class DemoRequestHandler(BaseHTTPRequestHandler):
   201	    """Serve the static demo shell and a thin JSON API around DemoAnswer."""
   202	
   203	    server_version = "WellHarnessDemo/1.0"
   204	
   205	    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
   206	        return
   207	
   208	    def do_GET(self):
   209	        parsed = urlparse(self.path)
   210	        if parsed.path in STATIC_ROUTE_ALIASES:
   211	            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
   212	            return
   213	        if parsed.path == MONITOR_TIMELINE_PATH:
   214	            self._send_json(200, monitor_timeline_payload())
   215	            return
   216	        if parsed.path == WORKBENCH_BOOTSTRAP_PATH:
   217	            self._send_json(200, workbench_bootstrap_payload())
   218	            return
   219	        if parsed.path == SYSTEM_SNAPSHOT_PATH:
   220	            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
   221	            self._send_json(200, system_snapshot_payload(system_id))
   222	            return
   223	        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
   224	            self._send_json(200, workbench_recent_archives_payload())
   225	            return
   226	
   227	        # Default entry: unified landing page with 2x3 card grid
   228	        # (Phase A: chat.html shelved; Phase UI-C: root now serves index.html
   229	        # instead of demo.html so user can reach all 6 surfaces.)
   230	        if parsed.path in ("", "/"):
   231	            self._serve_static("index.html")
   232	            return
   233	
   234	        if parsed.path in ("/demo.html", "/expert/demo.html"):
   235	            self._serve_static("demo.html")
   236	            return
   237	
   238	        if parsed.path in ("/workbench/start", "/workbench/start.html"):
   239	            self._serve_static("workbench_start.html")
   240	            return
   241	
   242	        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
   243	            self._serve_static("workbench_bundle.html")
   244	            return
   245	
   246	        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
   247	            self._serve_static("workbench.html")
   248	            return
   249	
   250	        relative_path = unquote(parsed.path.lstrip("/"))
   251	        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
   252	            self._serve_static(relative_path)
   253	            return
   254	
   255	        # P19.8: Hardware schema discovery
   256	        if parsed.path == HARDWARE_SCHEMA_PATH:
   257	            system_id = parse_qs(parsed.query).get("system_id", ["thrust-reverser"])[0]
   258	            self._handle_hardware_schema(system_id=system_id)
   259	            return
   260	

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2700,2765p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2700	            "PLS / VDT feedback comes from simplified first-cut plant timing.",
  2701	            "Manual feedback override is only a diagnostic demo control, not new control truth.",
  2702	            "THR_LOCK release must not be read as complete physical root-cause proof.",
  2703	        ],
  2704	    }
  2705	    return _apply_fault_injections_to_snapshot_payload(result, fault_injections)
  2706	
  2707	
  2708	def build_parser() -> argparse.ArgumentParser:
  2709	    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
  2710	    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
  2711	    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
  2712	    parser.add_argument(
  2713	        "--open",
  2714	        action="store_true",
  2715	        help=(
  2716	            "Open the local UI URL with Python's standard-library webbrowser.open; "
  2717	            "this is a launch convenience, not browser E2E automation."
  2718	        ),
  2719	    )
  2720	    return parser
  2721	
  2722	
  2723	def demo_url(host: str, port: int) -> str:
  2724	    return f"http://{host}:{port}/index.html"
  2725	
  2726	
  2727	def open_browser(url: str, opener=webbrowser.open) -> bool:
  2728	    try:
  2729	        opened = bool(opener(url))
  2730	    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
  2731	        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
  2732	        return False
  2733	    if not opened:
  2734	        print(f"Could not open browser automatically. Open {url} manually.")
  2735	    return opened
  2736	
  2737	
  2738	def main(argv: list[str] | None = None) -> int:
  2739	    args = build_parser().parse_args(argv)
  2740	    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
  2741	    host, port = server.server_address
  2742	    url = demo_url(host, port)
  2743	    print(f"Serving well-harness demo UI at {url}")
  2744	    if args.open:
  2745	        open_browser(url)
  2746	    try:
  2747	        server.serve_forever()
  2748	    except KeyboardInterrupt:
  2749	        print("\nStopping well-harness demo UI.")
  2750	    finally:
  2751	        server.server_close()
  2752	    return 0
  2753	
  2754	
  2755	if __name__ == "__main__":
  2756	    raise SystemExit(main())

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_annotation_vocab.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 709ms:
....................                                                     [100%]
20 passed in 0.55s

codex
The targeted regression test passes locally. I’m doing the requested runtime probe by starting the demo server and fetching `/workbench`, so the verdict is based on the real served page instead of file-only inspection.
exec
/bin/zsh -lc 'PYTHONPATH=src python -m well_harness.demo_server --host 127.0.0.1 --port 8770' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

codex
`python` isn’t on PATH in this worktree shell, so I’m re-running the same probe with `python3`. No code issue yet; this is just an environment detail for the live check.
exec
/bin/zsh -lc 'PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "curl -s http://127.0.0.1:8770/workbench | sed -n '185,205p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'curl -s http://127.0.0.1:8770/workbench | rg -n "标注|标记信号|圈选 logic gate|关联 spec|引用 requirement 段|工具激活|Annotation|Point tool active"' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
          Hide for session
        </button>
      </aside>

      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
        <span class="workbench-annotation-toolbar-label">标注</span>
        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
          标记信号 工具激活
        </span>
      </section>

      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
        <article
          id="workbench-control-panel"
          class="workbench-collab-column workbench-annotation-surface"
          data-column="control"
          data-annotation-surface="control"

 succeeded in 0ms:
189:      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
190:        <span class="workbench-annotation-toolbar-label">标注</span>
191:        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
192:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
193:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
194:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
196:          标记信号 工具激活
230:            <h2>Annotate &amp; Propose · 标注与提案</h2>
266:      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">

exec
/bin/zsh -lc 'curl -I -s http://127.0.0.1:8770/workbench' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
HTTP/1.0 501 Unsupported method ('HEAD')
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 18:02:50 GMT
Connection: close
Content-Type: text/html;charset=utf-8
Content-Length: 497


codex
The server is up and the served HTML contains the new labels exactly where expected. I’m doing one last pass on runtime details and wording quality now, especially whether the mixed Chinese-English nouns and the active-status sentence would sound clean during a spoken walkthrough.
exec
/bin/zsh -lc "curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8770/workbench" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
200

exec
/bin/zsh -lc 'git diff --unified=20 main..54e701b -- .planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..62cd57a
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-04-SURFACE-INVENTORY.md
@@ -0,0 +1,56 @@
+# E11-04 Surface Inventory — annotation vocabulary upgrade
+
+> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
+
+## Surface diff inventory
+
+| # | Surface | Type | Anchor | Notes |
+|---|---|---|---|---|
+| 1 | Toolbar label: `Annotation` → `标注` | [REWRITE] | `workbench.html` `.workbench-annotation-toolbar-label` | Generic English noun → domain-anchored Chinese verb. |
+| 2 | Button: `Point` → `标记信号` | [REWRITE] | `data-annotation-tool="point"` button | Mark a signal. |
+| 3 | Button: `Area` → `圈选 logic gate` | [REWRITE] | `data-annotation-tool="area"` button | Encircle a logic gate. |
+| 4 | Button: `Link` → `关联 spec` | [REWRITE] | `data-annotation-tool="link"` button | Link to a spec. |
+| 5 | Button: `Text Range` → `引用 requirement 段` | [REWRITE] | `data-annotation-tool="text-range"` button | Cite a requirement section. |
+| 6 | Default active-tool copy: `Point tool active` → `标记信号 工具激活` | [REWRITE] | `#workbench-annotation-active-tool` | Pre-hydration default. |
+| 7 | JS active-tool template: `${tool} tool active` → `${label} 工具激活` | [REWRITE] | `annotation_overlay.js:setActiveTool` | Maps tool ID via TOOL_DOMAIN_LABEL. |
+
+## Tier-trigger evaluation
+
+Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
+
+> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
+
+- **copy_diff_lines** = 7 → < 10
+- **[REWRITE/DELETE] count** = 7 → ≥ 3
+
+Both thresholds NOT met (copy_diff_lines fails). → **Tier-B** (1-persona review).
+
+E11-00-PLAN row E11-04 row 275 explicitly classifies this as "NO Codex (mechanical relabel)". The strict tier-trigger rule on the books is Tier-B; running a single-persona review is the conservative middle ground that honors both constraints.
+
+> **Verdict: Tier-B**. Per `PERSONA-ROTATION-STATE.md` round-robin successor, the next slot is determined after Tier-A E11-03 ran (rotation pointer unchanged).
+>
+> **Persona selection: P5 (Apps Engineer)** — domain-anchoring is exactly the customer/repro lens this relabel is meant to serve; P5 round-robin slot also follows P2 (the last Tier-B was E11-14 = P2; round-robin successor is P3, but E11-13 was P1 and E11-14 was P2 — actually next is P3). However content-fit weight: P3 (Demo Presenter) is a better content match for "domain-anchored vocabulary the engineer/customer reads on screen". Plan defers to round-robin: **P3 Demo Presenter**.
+
+(Note: the constitution allows owner-override of round-robin when content motivates it. Either P3 or P5 is defensible; round-robin is the safer default.)
+
+## Stable-ID invariants (must hold)
+
+The plan explicitly says "UI 仍用 point/area/link/text-range 作为底层类型". Every one of these stays untouched:
+
+- `data-annotation-tool="point"`
+- `data-annotation-tool="area"`
+- `data-annotation-tool="link"`
+- `data-annotation-tool="text-range"`
+- `id="workbench-annotation-toolbar"`
+- `id="workbench-annotation-active-tool"`
+
+`tests/test_workbench_annotation_vocab.py` locks all 6 stable anchors alongside the new visible copy.
+
+## Truth-engine red line
+
+Files touched:
+- `src/well_harness/static/workbench.html` (1 [REWRITE] block, 6 visible-copy lines)
+- `src/well_harness/static/annotation_overlay.js` (1 [REWRITE] for the status template + new TOOL_DOMAIN_LABEL map)
+- `tests/test_workbench_annotation_vocab.py` (NEW, 20 tests)
+
+Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index d8fb548..6d16b70 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -1,14 +1,15 @@
 # E11 Tier-B Persona Rotation State
 
 > Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger` (governance bundle #2, 2026-04-25, PR #14).
 >
 > Source of truth for next Tier-B persona selection. Default = round-robin successor (P1 → P2 → P3 → P4 → P5 → P1) of last entry. Owner may write a non-default value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint: written value must NOT equal the immediately preceding Tier-B entry.
 >
 > New epic (E12, E13, ...) starts a fresh state file with sequence reset to P1.
 
 ## Sequence
 
 E11-13: P1 (round-robin start; first Tier-B sub-phase under bundle #2)
 E11-14: P2 (round-robin successor; Senior FCS Engineer fits server-side / API contract review)
 E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html corrections + 12 ANCHORED card copy lines). All 5 personas dispatched. Rotation pointer unchanged (Tier-A does not consume a Tier-B slot).
 E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
+E11-04: Tier-B (7 copy_diff_lines, fails ≥10 threshold; though 7 [REWRITE] meets ≥3). Persona = P3 (Demo Presenter — content-fit for domain vocabulary the engineer reads on screen; also the round-robin successor of P2). Plan row 275 said "NO Codex (mechanical relabel)" but the constitution Tier-B rule is the stricter SSOT.

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '188,198p'; printf '\\n---\\n'; nl -ba src/well_harness/static/annotation_overlay.js | sed -n '172,186p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   188	
   189	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   190	        <span class="workbench-annotation-toolbar-label">标注</span>
   191	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
   192	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
   193	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
   194	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
   195	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   196	          标记信号 工具激活
   197	        </span>
   198	      </section>

---
   172	  function setActiveTool(tool) {
   173	    if (!tools.includes(tool)) {
   174	      return;
   175	    }
   176	    activeTool = tool;
   177	    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
   178	      const pressed = button.dataset.annotationTool === activeTool;
   179	      button.classList.toggle("is-active", pressed);
   180	      button.setAttribute("aria-pressed", String(pressed));
   181	    });
   182	    const status = document.getElementById("workbench-annotation-active-tool");
   183	    if (status) {
   184	      const label = TOOL_DOMAIN_LABEL[tool] || tool;
   185	      status.textContent = `${label} 工具激活`;
   186	    }

codex
The live GET returned `200` and served the same toolbar strings as the diff. I’ve got enough evidence for a verdict, and I’m shutting the local demo server back down before I write the review.
 succeeded in 38745ms:
^C
Stopping well-harness demo UI.

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,880p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   848	# Task Group: AI FANTUI LogicMVP demo presentation, launch behavior, and leadership-facing communication
   849	
   850	scope: Keep the well-harness demo honest and user-facing, launch the real local UI instead of describing it abstractly, and translate project progress into plain Chinese for non-software audiences.
   851	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
   852	
   853	## Task 1: Present direct VDT controls and flatten the logic board without changing backend truth
   854	
   855	### rollout_summary_files
   856	
   857	- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, iterative refinement from user corrections)
   858	- rollout_summaries/2026-04-07T06-20-24-tGb4-round_92_direct_vdt_control_flatter_logic_board.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-20-24-019d6699-6f65-7712-ba2d-13ed0f64e87e.jsonl, updated_at=2026-04-08T14:50:07+00:00, thread_id=019d6699-6f65-7712-ba2d-13ed0f64e87e, final Round 92 reflow with preserved endpoint contracts)
   859	
   860	### keywords
   861	
   862	- VDT 模式, VDT 反馈, deploy_position_percent, manual_feedback_override, logic-note, 结果摘要先下沉, 诊断问答 frozen, /api/lever-snapshot, THR_LOCK, deploy_90_percent_vdt
   863	
   864	## Task 2: Rewrite materials narrowly when the user says to exclude Notion/control-tower framing
   865	
   866	### rollout_summary_files
   867	
   868	- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
   869	
   870	### keywords
   871	
   872	- 排除Notion中枢管控的巧思设计，单论这个控制逻辑智能化, 现状及问题, 改进措施或设想, 工程师负担, 可交互、可解释、可推演
   873	
   874	## Task 3: Start the real local UI, handle port conflicts, and return the final reachable address
   875	
   876	### rollout_summary_files
   877	
   878	- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
   879	- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
   880	

codex
**APPROVE_WITH_NITS**

- `NIT` [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:185): `${label} 工具激活` is understandable, but it reads stage-stiff rather than natural. For mixed labels like “引用 requirement 段”, the full status becomes awkward to say aloud in a walkthrough.
- `NIT` [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:192): the purpose verbs land, but three visible labels still keep mixed-language nouns: `logic gate`, `spec`, `requirement`. An engineer audience will follow them, but a presenter is still likely to paraphrase instead of reading the UI verbatim.
- `INFO` [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:107) and [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:127): outside the toolbar, placed annotations still surface raw internal copy like `point annotation` / `point on control: ...`. That is out of scope for E11-04, but if the live demo includes actually dropping annotations, the vocabulary upgrade is not end-to-end yet.

Live probe: I started `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770`, then `GET http://127.0.0.1:8770/workbench` returned `200` and served the expected toolbar block at [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:189): `标注`, `标记信号`, `圈选 logic gate`, `关联 spec`, `引用 requirement 段`, `标记信号 工具激活`. Targeted regression verification also passed at [tests/test_workbench_annotation_vocab.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_vocab.py:148): `20 passed in 0.55s`.

Truth-engine red line check: `git diff --name-only main..54e701b` shows only `.planning/` entries plus [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:189), [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:161), and [tests/test_workbench_annotation_vocab.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_vocab.py:1). The worktree does contain unrelated untracked local files, but they are not part of `main..54e701b`.

**P3 — Demo Presenter (Tier-B, E11-04)**

tokens used
95,341
**APPROVE_WITH_NITS**

- `NIT` [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:185): `${label} 工具激活` is understandable, but it reads stage-stiff rather than natural. For mixed labels like “引用 requirement 段”, the full status becomes awkward to say aloud in a walkthrough.
- `NIT` [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:192): the purpose verbs land, but three visible labels still keep mixed-language nouns: `logic gate`, `spec`, `requirement`. An engineer audience will follow them, but a presenter is still likely to paraphrase instead of reading the UI verbatim.
- `INFO` [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:107) and [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:127): outside the toolbar, placed annotations still surface raw internal copy like `point annotation` / `point on control: ...`. That is out of scope for E11-04, but if the live demo includes actually dropping annotations, the vocabulary upgrade is not end-to-end yet.

Live probe: I started `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770`, then `GET http://127.0.0.1:8770/workbench` returned `200` and served the expected toolbar block at [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:189): `标注`, `标记信号`, `圈选 logic gate`, `关联 spec`, `引用 requirement 段`, `标记信号 工具激活`. Targeted regression verification also passed at [tests/test_workbench_annotation_vocab.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_vocab.py:148): `20 passed in 0.55s`.

Truth-engine red line check: `git diff --name-only main..54e701b` shows only `.planning/` entries plus [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:189), [src/well_harness/static/annotation_overlay.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:161), and [tests/test_workbench_annotation_vocab.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_vocab.py:1). The worktree does contain unrelated untracked local files, but they are not part of `main..54e701b`.

**P3 — Demo Presenter (Tier-B, E11-04)**

