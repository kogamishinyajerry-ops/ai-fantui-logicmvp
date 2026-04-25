2026-04-25T17:26:09.884885Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T17:26:09.884951Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc5ad-7155-7232-be24-db8ca034a7d2
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-A 5-persona pipeline, E11-03 sub-phase).

# Shared context for E11-03 review (all 5 personas)

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-03-column-rename-20260426`
**PR:** #19
**Worktree HEAD:** `2df105c` (single commit on top of main `18fdb46`)

## What E11-03 ships

Per E11-00-PLAN row E11-03: rename the three /workbench shell columns from technical nouns to engineer-task verbs while preserving every underlying ID so e2e selectors and JS boot wiring keep working.

Mapping (12 [REWRITE] lines in lockstep):
| Old | New |
|---|---|
| Scenario Control | Probe & Trace · 探针与追踪 |
| Spec Review Surface | Annotate & Propose · 标注与提案 |
| Logic Circuit Surface | Hand off & Track · 移交与跟踪 |

(Each title + eyebrow + default boot status + hydrated JS boot status — 4 strings × 3 columns = 12.)

Files in scope:
- `src/well_harness/static/workbench.html` — 3 [REWRITE] blocks at the column `<header>` + status div (lines ~208-253)
- `src/well_harness/static/workbench.js` — 3 [REWRITE] boot status strings in `bootWorkbenchControlPanel/DocumentPanel/CircuitPanel` (lines ~63-91)
- `tests/test_workbench_column_rename.py` — NEW (32 tests covering new copy, stale-copy absence, stable anchors, JS boot copy, live-served route)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended E11-03 = Tier-A

## Stable-ID invariants (must hold)

The plan explicitly says "保留底层 ID 不变以免 e2e 测试失效". E11-03 preserves:

- `id="workbench-control-panel"` / `data-column="control"` / `data-annotation-surface="control"` / `id="workbench-control-status"`
- `id="workbench-document-panel"` / `data-column="document"` / `data-annotation-surface="document"` / `id="workbench-document-status"`
- `id="workbench-circuit-panel"` / `data-column="circuit"` / `data-annotation-surface="circuit"` / `id="workbench-circuit-status"`

The new test file asserts all 12 anchors are still present.

## Truth-engine red line (must hold)

`git diff --name-only main..2df105c` should show only:
- `.planning/phases/E11-workbench-engineer-first-ux/*`
- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.js`
- `tests/test_workbench_column_rename.py`

NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`.

## Verification status

- 951 / 951 pytest pass (32 new tests in `test_workbench_column_rename.py`, 0 regression)
- All e2e tests still green (no e2e selector depends on the visible heading text)

## Out of scope

- Re-styling the columns (font, color, spacing) — E11-15 polish scope
- Other workbench surfaces (annotation toolbar, approval center, wow starter cards) — separate sub-phases
- Backend or controller code — explicit out-of-scope (truth-engine red line)

## Your specific lens

Focus on: boundary correctness — every stable ID/data-column anchor preserved, no e2e selector silently broken, no API contract drift.

Read the files listed under "Files in scope" (full). Form an independent verdict from your persona's perspective.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items (E11-15 polish, separate sub-phases, backend) → NIT/INFO only.

Live-probe at least one path you're unsure about (e.g. boot demo_server, GET /workbench, verify rendered text). Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..2df105c` shows only the 4 in-scope path types listed above.

Sign as: **P2 — Senior FCS Engineer (Tier-A, E11-03)**
codex
按你的 P2 审查口径，我先做两件事：快速回看与 `LogicMVP` 相关的记忆线索，随后直接核对 PR #19 的 in-scope 文件、`git diff` 边界，以及 `/workbench` 的真实渲染路径。
exec
/bin/zsh -lc 'rg -n "LogicMVP|workbench|E11|column rename|column-rename" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
我会按 `using-superpowers` 的技能约束执行这次审查；`gsd-code-review` 我不直接跑，因为它会产出 `REVIEW.md` 工件，而你这次要的是只读、就地给出独立 verdict。
Review-only pass for E11-03 under the P2 boundary-correctness lens.
  → Confirm branch/head scope and truth-engine red-line via git diff/path audit
  • Read the in-scope files fully and inspect anchor/copy changes with line citations
  • Live-probe /workbench render path and run targeted verification
  • Deliver persona verdict with severity-ordered findings
exec
/bin/zsh -lc 'git diff --stat main..HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-03-SURFACE-INVENTORY.md                    |  53 +++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/static/workbench.html             |  18 +--
 src/well_harness/static/workbench.js               |  14 +-
 tests/test_workbench_column_rename.py              | 172 +++++++++++++++++++++
 5 files changed, 246 insertions(+), 12 deletions(-)

exec
/bin/zsh -lc 'git branch --show-current && git rev-parse --short HEAD && git rev-parse --short main && git diff --name-only main..HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
feat/e11-03-column-rename-20260426
2df105c
18fdb46
.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
tests/test_workbench_column_rename.py

exec
/bin/zsh -lc 'wc -l src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     321 src/well_harness/static/workbench.html
    3973 src/well_harness/static/workbench.js
     172 tests/test_workbench_column_rename.py
      53 .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
      14 .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
    4533 total

codex
边界红线先成立了：`main..HEAD` 只有 5 个路径，且都在你给定的允许范围内，没有任何 truth-engine 文件漂移。现在转到逐文件审查，重点看三列的可见文案替换是否完全锁步、ID/data-* 锚点是否原封不动。
exec
/bin/zsh -lc "nl -ba tests/test_workbench_column_rename.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,321p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   105	# ─── 3. Underlying IDs / data attributes preserved ──────────────────
   106	#
   107	# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
   108	# panel ids, data-column tokens, data-annotation-surface tokens, and
   109	# status div ids are anchors for e2e selectors and JS boot wiring, so
   110	# they MUST stay stable through the rename.
   111	
   112	
   113	@pytest.mark.parametrize(
   114	    "anchor",
   115	    [
   116	        'id="workbench-control-panel"',
   117	        'id="workbench-document-panel"',
   118	        'id="workbench-circuit-panel"',
   119	        'data-column="control"',
   120	        'data-column="document"',
   121	        'data-column="circuit"',
   122	        'data-annotation-surface="control"',
   123	        'data-annotation-surface="document"',
   124	        'data-annotation-surface="circuit"',
   125	        'id="workbench-control-status"',
   126	        'id="workbench-document-status"',
   127	        'id="workbench-circuit-status"',
   128	    ],
   129	)
   130	def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
   131	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   132	    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"
   133	
   134	
   135	# ─── 4. JS boot status copy matches new column names ────────────────
   136	
   137	
   138	@pytest.mark.parametrize(
   139	    "boot_copy",
   140	    [
   141	        "Probe & Trace ready",
   142	        "Annotate & Propose ready",
   143	        "Hand off & Track ready",
   144	    ],
   145	)
   146	def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
   147	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   148	    assert boot_copy in js, f"workbench.js boot status missing: {boot_copy}"
   149	
   150	
   151	def test_workbench_js_boot_status_drops_stale_names() -> None:
   152	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   153	    # Old boot copy must NOT appear, otherwise the visible chrome and the
   154	    # status messages will disagree.
   155	    assert "Control panel ready" not in js
   156	    assert "Document panel ready" not in js
   157	    assert "Circuit panel ready" not in js
   158	
   159	
   160	# ─── 5. Live-served /workbench reflects the rename end-to-end ───────
   161	
   162	
   163	def test_workbench_route_serves_renamed_columns(server) -> None:
   164	    status, html = _get(server, "/workbench")
   165	    assert status == 200
   166	    # New copy
   167	    assert "Probe &amp; Trace · 探针与追踪" in html
   168	    assert "Annotate &amp; Propose · 标注与提案" in html
   169	    assert "Hand off &amp; Track · 移交与跟踪" in html
   170	    # Stable anchors still served
   171	    assert 'id="workbench-control-panel"' in html
   172	    assert 'data-column="circuit"' in html

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
    52	        id="workbench-wow-starters"
    53	        class="workbench-wow-starters"
    54	        aria-label="Canonical demo scenarios — one-click starter cards"
    55	      >
    56	        <header class="workbench-wow-starters-header">
    57	          <p class="eyebrow">canonical scenarios</p>
    58	          <h2>起手卡 · One-click 走读</h2>
    59	          <p class="workbench-wow-starters-sub">
    60	            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
    61	          </p>
    62	        </header>
    63	        <div class="workbench-wow-starters-grid">
    64	          <article
    65	            class="workbench-wow-card"
    66	            data-wow-id="wow_a"
    67	            aria-labelledby="workbench-wow-a-title"
    68	          >
    69	            <header>
    70	              <span class="workbench-wow-tag">wow_a</span>
    71	              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
    72	            </header>
    73	            <p class="workbench-wow-card-desc">
    74	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
    75	              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
    76	              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
    77	              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
    78	            </p>
    79	            <button
    80	              type="button"
    81	              class="workbench-wow-run-button"
    82	              data-wow-action="run"
    83	              data-wow-id="wow_a"
    84	            >
    85	              一键运行 wow_a
    86	            </button>
    87	            <div
    88	              class="workbench-wow-result"
    89	              data-wow-result-for="wow_a"
    90	              role="status"
    91	              aria-live="polite"
    92	            >
    93	              尚未运行。
    94	            </div>
    95	          </article>
    96	          <article
    97	            class="workbench-wow-card"
    98	            data-wow-id="wow_b"
    99	            aria-labelledby="workbench-wow-b-title"
   100	          >
   101	            <header>
   102	              <span class="workbench-wow-tag">wow_b</span>
   103	              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
   104	            </header>
   105	            <p class="workbench-wow-card-desc">
   106	              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
   107	              success_rate + failure_modes 分布。
   108	            </p>
   109	            <button
   110	              type="button"
   111	              class="workbench-wow-run-button"
   112	              data-wow-action="run"
   113	              data-wow-id="wow_b"
   114	            >
   115	              一键运行 wow_b
   116	            </button>
   117	            <div
   118	              class="workbench-wow-result"
   119	              data-wow-result-for="wow_b"
   120	              role="status"
   121	              aria-live="polite"
   122	            >
   123	              尚未运行。
   124	            </div>
   125	          </article>
   126	          <article
   127	            class="workbench-wow-card"
   128	            data-wow-id="wow_c"
   129	            aria-labelledby="workbench-wow-c-title"
   130	          >
   131	            <header>
   132	              <span class="workbench-wow-tag">wow_c</span>
   133	              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
   134	            </header>
   135	            <p class="workbench-wow-card-desc">
   136	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   137	              触发该 outcome 的参数组合（max_results=10）。
   138	            </p>
   139	            <button
   140	              type="button"
   141	              class="workbench-wow-run-button"
   142	              data-wow-action="run"
   143	              data-wow-id="wow_c"
   144	            >
   145	              一键运行 wow_c
   146	            </button>
   147	            <div
   148	              class="workbench-wow-result"
   149	              data-wow-result-for="wow_c"
   150	              role="status"
   151	              aria-live="polite"
   152	            >
   153	              尚未运行。
   154	            </div>
   155	          </article>
   156	        </div>
   157	      </section>
   158	
   159	      <aside
   160	        id="workbench-trust-banner"
   161	        class="workbench-trust-banner"
   162	        data-feedback-mode="manual_feedback_override"
   163	        role="note"
   164	        aria-label="Feedback mode trust affordance"
   165	      >
   166	        <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
   167	        <div class="workbench-trust-banner-body">
   168	          <span class="workbench-trust-banner-scope">
   169	            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
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
   190	        <span class="workbench-annotation-toolbar-label">Annotation</span>
   191	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">Point</button>
   192	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">Area</button>
   193	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">Link</button>
   194	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">Text Range</button>
   195	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   196	          Point tool active
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
   221	        <article
   222	          id="workbench-document-panel"
   223	          class="workbench-collab-column workbench-annotation-surface"
   224	          data-column="document"
   225	          data-annotation-surface="document"
   226	          tabindex="0"
   227	        >
   228	          <header>
   229	            <p class="eyebrow">annotate &amp; propose</p>
   230	            <h2>Annotate &amp; Propose · 标注与提案</h2>
   231	          </header>
   232	          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
   233	            Waiting for annotate &amp; propose panel boot.
   234	          </div>
   235	          <div class="workbench-collab-document">
   236	            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
   237	            <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
   238	          </div>
   239	        </article>
   240	
   241	        <article
   242	          id="workbench-circuit-panel"
   243	          class="workbench-collab-column workbench-annotation-surface"
   244	          data-column="circuit"
   245	          data-annotation-surface="circuit"
   246	          tabindex="0"
   247	        >
   248	          <header>
   249	            <p class="eyebrow">hand off &amp; track</p>
   250	            <h2>Hand off &amp; Track · 移交与跟踪</h2>
   251	          </header>
   252	          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
   253	            Waiting for hand off &amp; track panel boot.
   254	          </div>
   255	          <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
   256	            <span>SW1</span>
   257	            <span>Logic 1</span>
   258	            <span>Logic 2</span>
   259	            <span>Logic 3</span>
   260	            <span>Logic 4</span>
   261	            <span>THR LOCK</span>
   262	          </div>
   263	        </article>
   264	      </section>
   265	
   266	      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
   267	        <header>
   268	          <p class="eyebrow">annotation inbox</p>
   269	          <h2>Review Queue</h2>
   270	        </header>
   271	        <ul id="annotation-inbox-list">
   272	          <li>No proposals submitted yet.</li>
   273	        </ul>
   274	      </aside>
   275	
   276	      <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
   277	        <button
   278	          id="approval-center-entry"
   279	          type="button"
   280	          class="workbench-toolbar-button"
   281	          data-role="KOGAMI"
   282	          aria-controls="approval-center-panel"
   283	        >
   284	          Approval Center
   285	        </button>
   286	        <span>Approval actions are Kogami-only.</span>
   287	      </footer>
   288	
   289	      <section
   290	        id="approval-center-panel"
   291	        class="workbench-approval-center"
   292	        data-approval-role="KOGAMI"
   293	        aria-labelledby="approval-center-title"
   294	      >
   295	        <header>
   296	          <p class="eyebrow">approval center</p>
   297	          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
   298	        </header>
   299	        <div class="workbench-approval-grid">
   300	          <article class="workbench-approval-lane" data-approval-lane="pending">
   301	            <h3>Pending</h3>
   302	            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
   303	          </article>
   304	          <article class="workbench-approval-lane" data-approval-lane="accept">
   305	            <h3>Accept</h3>
   306	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
   307	          </article>
   308	          <article class="workbench-approval-lane" data-approval-lane="reject">
   309	            <h3>Reject</h3>
   310	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
   311	          </article>
   312	        </div>
   313	      </section>
   314	
   315	      <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
   316	    </main>
   317	
   318	    <script src="/annotation_overlay.js"></script>
   319	    <script src="/workbench.js"></script>
   320	  </body>
   321	</html>

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11-03 Surface Inventory — three-column rename
     2	
     3	> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
     4	
     5	## Surface diff inventory
     6	
     7	| # | Surface | Type | Anchor | Notes |
     8	|---|---|---|---|---|
     9	| 1 | Column 1 title: `Scenario Control` → `Probe & Trace · 探针与追踪` | [REWRITE] | `workbench.html` `#workbench-control-panel <h2>` | Engineer-task verb pair replaces technical noun. |
    10	| 2 | Column 1 eyebrow: `control panel` → `probe & trace` | [REWRITE] | `workbench.html` `#workbench-control-panel .eyebrow` | Lowercase match for visible chrome consistency. |
    11	| 3 | Column 1 boot status: `Waiting for control panel boot.` → `Waiting for probe & trace panel boot.` | [REWRITE] | `workbench.html` `#workbench-control-status` | Default copy before JS hydrates. |
    12	| 4 | Column 1 JS boot: `Control panel ready. Scenario actions are staged for E07+.` → `Probe & Trace ready. Scenario actions are staged for E07+.` | [REWRITE] | `workbench.js:bootWorkbenchControlPanel` | Status after hydration. |
    13	| 5 | Column 2 title: `Spec Review Surface` → `Annotate & Propose · 标注与提案` | [REWRITE] | `workbench.html` `#workbench-document-panel <h2>` | Maps to text-range annotation flow. |
    14	| 6 | Column 2 eyebrow: `document` → `annotate & propose` | [REWRITE] | `workbench.html` `#workbench-document-panel .eyebrow` | |
    15	| 7 | Column 2 boot status: `Waiting for document panel boot.` → `Waiting for annotate & propose panel boot.` | [REWRITE] | `workbench.html` `#workbench-document-status` | |
    16	| 8 | Column 2 JS boot: `Document panel ready. Text-range annotation arrives in E07.` → `Annotate & Propose ready. Text-range annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchDocumentPanel` | |
    17	| 9 | Column 3 title: `Logic Circuit Surface` → `Hand off & Track · 移交与跟踪` | [REWRITE] | `workbench.html` `#workbench-circuit-panel <h2>` | Maps to ticket handoff flow. |
    18	| 10 | Column 3 eyebrow: `circuit` → `hand off & track` | [REWRITE] | `workbench.html` `#workbench-circuit-panel .eyebrow` | |
    19	| 11 | Column 3 boot status: `Waiting for circuit panel boot.` → `Waiting for hand off & track panel boot.` | [REWRITE] | `workbench.html` `#workbench-circuit-status` | |
    20	| 12 | Column 3 JS boot: `Circuit panel ready. Overlay annotation arrives in E07.` → `Hand off & Track ready. Overlay annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchCircuitPanel` | |
    21	
    22	## Tier-trigger evaluation
    23	
    24	Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
    25	
    26	> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
    27	
    28	- **copy_diff_lines** = 12 → ≥ 10 ✓
    29	- **[REWRITE/DELETE] count** = 12 (all rows) → ≥ 3 ✓
    30	
    31	> **Verdict: Tier-A** (5-persona review).
    32	
    33	This is exactly the rename-pure case the Tier-A trigger was designed for: every visible string on three structural surfaces is being rewritten in lockstep. Tier-A is the conservative routing.
    34	
    35	## Stable-ID invariants (must hold)
    36	
    37	The plan explicitly says "保留底层 ID 不变以免 e2e 测试失效" — every one of these anchors stays untouched:
    38	
    39	- `id="workbench-control-panel"`, `id="workbench-document-panel"`, `id="workbench-circuit-panel"`
    40	- `data-column="control"`, `data-column="document"`, `data-column="circuit"`
    41	- `data-annotation-surface="control"`, `data-annotation-surface="document"`, `data-annotation-surface="circuit"`
    42	- `id="workbench-control-status"`, `id="workbench-document-status"`, `id="workbench-circuit-status"`
    43	
    44	`tests/test_workbench_column_rename.py` locks all 12 stable anchors alongside the new visible copy so a future "polish" pass can't silently regress either side.
    45	
    46	## Truth-engine red line
    47	
    48	Files touched:
    49	- `src/well_harness/static/workbench.html` (3 [REWRITE] blocks, 12 visible-copy lines)
    50	- `src/well_harness/static/workbench.js` (3 [REWRITE] boot status strings)
    51	- `tests/test_workbench_column_rename.py` (NEW)
    52	
    53	Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11 Tier-B Persona Rotation State
     2	
     3	> Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger` (governance bundle #2, 2026-04-25, PR #14).
     4	>
     5	> Source of truth for next Tier-B persona selection. Default = round-robin successor (P1 → P2 → P3 → P4 → P5 → P1) of last entry. Owner may write a non-default value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint: written value must NOT equal the immediately preceding Tier-B entry.
     6	>
     7	> New epic (E12, E13, ...) starts a fresh state file with sequence reset to P1.
     8	
     9	## Sequence
    10	
    11	E11-13: P1 (round-robin start; first Tier-B sub-phase under bundle #2)
    12	E11-14: P2 (round-robin successor; Senior FCS Engineer fits server-side / API contract review)
    13	E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html corrections + 12 ANCHORED card copy lines). All 5 personas dispatched. Rotation pointer unchanged (Tier-A does not consume a Tier-B slot).
    14	E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1,500p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1001,1500p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '501,1000p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    51	function bootWorkbenchColumnSafely(columnName, bootFn) {
    52	  try {
    53	    bootFn();
    54	  } catch (error) {
    55	    const status = workbenchElement(`workbench-${columnName}-status`);
    56	    if (status) {
    57	      status.textContent = `${columnName} panel failed independently: ${error.message || error}`;
    58	      status.dataset.tone = "warning";
    59	    }
    60	  }
    61	}
    62	
    63	// E11-03 (2026-04-26): the three columns were renamed from technical
    64	// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")
    65	// to engineer-task verbs ("Probe & Trace / Annotate & Propose / Hand off
    66	// & Track"). Underlying ids and data-column tokens stay stable so e2e
    67	// selectors don't break — only the visible status copy here changes.
    68	function bootWorkbenchControlPanel() {
    69	  const status = workbenchElement("workbench-control-status");
    70	  if (status) {
    71	    status.textContent =
    72	      "Probe & Trace ready. Scenario actions are staged for E07+.";
    73	    status.dataset.tone = "ready";
    74	  }
    75	}
    76	
    77	function bootWorkbenchDocumentPanel() {
    78	  const status = workbenchElement("workbench-document-status");
    79	  if (status) {
    80	    status.textContent =
    81	      "Annotate & Propose ready. Text-range annotation arrives in E07.";
    82	    status.dataset.tone = "ready";
    83	  }
    84	}
    85	
    86	function bootWorkbenchCircuitPanel() {
    87	  const status = workbenchElement("workbench-circuit-status");
    88	  if (status) {
    89	    status.textContent =
    90	      "Hand off & Track ready. Overlay annotation arrives in E07.";
    91	    status.dataset.tone = "ready";
    92	  }
    93	}
    94	
    95	function bootWorkbenchShell() {
    96	  bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
    97	  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
    98	  bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
    99	}
   100	
   101	// P43 authority contract — written only via assignFrozenSpec; never mutated directly
   102	let frozenSpec = null;
   103	
   104	// P43 workflow state machine (P43-03)
   105	let workflowState = "INIT";
   106	
   107	const _workflowTransitions = {
   108	  INIT:        { confirm_freeze: "FROZEN",      load_packet: "INIT" },
   109	  FROZEN:      { start_gen: "GENERATING",       confirm_freeze: "FROZEN",   reiterate: "INIT" },
   110	  GENERATING:  { gen_complete: "PANEL_READY",   gen_fail: "ERROR",          reiterate: "INIT" },
   111	  PANEL_READY: { final_approve: "APPROVING",    start_gen: "GENERATING",    reiterate: "INIT" },
   112	  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
   113	  APPROVED:    { archive: "ARCHIVING" },
   114	  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
   115	  ARCHIVED:    {},
   116	  ERROR:       { reiterate: "INIT" },
   117	};
   118	
   119	function dispatchWorkflowEvent(event) {
   120	  const next = (_workflowTransitions[workflowState] || {})[event];
   121	  if (next === undefined) {
   122	    return false;
   123	  }
   124	  workflowState = next;
   125	  updateWorkflowUI();
   126	  return true;
   127	}
   128	
   129	function updateWorkflowUI() {
   130	  const approveBtn  = workbenchElement("workbench-final-approve");
   131	  const startGenBtn = workbenchElement("workbench-start-gen");
   132	  const badge       = workbenchElement("workbench-workflow-state");
   133	
   134	  // "冻结审批 Spec" enabled when spec is not yet frozen or after generation
   135	  const approveEnabled = ["INIT", "PANEL_READY", "ANNOTATING", "WIRING"].includes(workflowState);
   136	  // "生成 (Frozen Spec)" enabled only when a frozen spec exists
   137	  const startGenEnabled = workflowState === "FROZEN";
   138	
   139	  if (approveBtn)  approveBtn.disabled  = !approveEnabled;
   140	  if (startGenBtn) startGenBtn.disabled = !startGenEnabled;
   141	  if (badge) {
   142	    badge.textContent    = workflowState;
   143	    badge.dataset.state  = workflowState.toLowerCase();
   144	  }
   145	}
   146	
   147	const workbenchPresets = {
   148	  ready_archived: {
   149	    label: "一键通过验收",
   150	    archiveBundle: true,
   151	    source: "reference",
   152	    sourceStatus: "当前样例：参考样例。系统会直接跑完整 happy path 并生成 archive。",
   153	    preparationMessage: "参考样例已就位，系统马上开始生成 ready bundle 并留档。",
   154	  },
   155	  blocked_follow_up: {
   156	    label: "一键看阻塞态",
   157	    archiveBundle: false,
   158	    source: "template",
   159	    sourceStatus: "当前样例：空白模板。系统会故意演示 clarification gate 如何把不完整 packet 拦下来。",
   160	    preparationMessage: "空白模板已就位，系统马上演示阻塞态。",
   161	  },
   162	  ready_preview: {
   163	    label: "一键快速预览",
   164	    archiveBundle: false,
   165	    source: "reference",
   166	    sourceStatus: "当前样例：参考样例。系统会直接跑 ready bundle，但不生成 archive。",
   167	    preparationMessage: "参考样例已就位，系统马上生成 ready bundle 供快速查看。",
   168	  },
   169	  archive_retry: {
   170	    label: "一键留档复跑",
   171	    archiveBundle: true,
   172	    source: "reference",
   173	    sourceStatus: "当前样例：参考样例。这个预设适合连续复跑，archive 会自动避开重名目录。",
   174	    preparationMessage: "参考样例已就位，系统马上做一次带 archive 的复跑。",
   175	  },
   176	};
   177	
   178	function workbenchElement(id) {
   179	  return document.getElementById(id);
   180	}
   181	
   182	function beginWorkbenchRequest() {
   183	  latestWorkbenchRequestId += 1;
   184	  return latestWorkbenchRequestId;
   185	}
   186	
   187	function isLatestWorkbenchRequest(requestId) {
   188	  return requestId === latestWorkbenchRequestId;
   189	}
   190	
   191	function setRequestStatus(message, tone = "neutral") {
   192	  const element = workbenchElement("workbench-request-status");
   193	  element.textContent = message;
   194	  element.dataset.tone = tone;
   195	}
   196	
   197	function setPacketSourceStatus(message) {
   198	  workbenchElement("workbench-packet-source-status").textContent = message;
   199	  persistWorkbenchPacketWorkspace();
   200	}
   201	
   202	function setResultMode(message) {
   203	  workbenchElement("workbench-result-mode").textContent = message;
   204	}
   205	
   206	function prettyJson(value) {
   207	  return JSON.stringify(value, null, 2);
   208	}
   209	
   210	function shortPath(path) {
   211	  if (!path) {
   212	    return "(none)";
   213	  }
   214	  const parts = String(path).split("/");
   215	  return parts[parts.length - 1] || String(path);
   216	}
   217	
   218	function cloneJson(value) {
   219	  return JSON.parse(JSON.stringify(value));
   220	}
   221	
   222	function normalizeRecentWorkbenchArchiveEntries(entries) {
   223	  if (!Array.isArray(entries)) {
   224	    return [];
   225	  }
   226	  return entries
   227	    .filter((entry) => entry && typeof entry === "object")
   228	    .map((entry) => ({
   229	      archive_dir: typeof entry.archive_dir === "string" ? entry.archive_dir : "",
   230	      manifest_path: typeof entry.manifest_path === "string" ? entry.manifest_path : "",
   231	      created_at_utc: typeof entry.created_at_utc === "string" ? entry.created_at_utc : "",
   232	      system_id: typeof entry.system_id === "string" ? entry.system_id : "unknown_system",
   233	      system_title: typeof entry.system_title === "string" ? entry.system_title : "",
   234	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
   235	      ready_for_spec_build: Boolean(entry.ready_for_spec_build),
   236	      selected_scenario_id: typeof entry.selected_scenario_id === "string" ? entry.selected_scenario_id : "",
   237	      selected_fault_mode_id: typeof entry.selected_fault_mode_id === "string" ? entry.selected_fault_mode_id : "",
   238	      has_workspace_handoff: Boolean(entry.has_workspace_handoff),
   239	      has_workspace_snapshot: Boolean(entry.has_workspace_snapshot),
   240	    }))
   241	    .filter((entry) => entry.manifest_path || entry.archive_dir);
   242	}
   243	
   244	function summarizeRecentWorkbenchArchive(entry) {
   245	  const state = entry.ready_for_spec_build ? "ready" : "blocked";
   246	  const scenario = entry.selected_scenario_id || "未选 scenario";
   247	  const faultMode = entry.selected_fault_mode_id || "未选 fault mode";
   248	  const workspace = entry.has_workspace_snapshot
   249	    ? "带工作区快照"
   250	    : (entry.has_workspace_handoff ? "仅带交接摘要" : "仅带 bundle");
   251	  return {
   252	    badge: state === "ready" ? "可恢复 / ready" : "可恢复 / blocked",
   253	    summary: `${scenario} / ${faultMode}`,
   254	    detail: `${workspace} / ${shortPath(entry.archive_dir || entry.manifest_path)}`,
   255	  };
   256	}
   257	
   258	function buildRecentWorkbenchArchiveEntryFromBundlePayload(payload) {
   259	  const archive = payload && payload.archive ? payload.archive : null;
   260	  const bundle = payload && payload.bundle ? payload.bundle : {};
   261	  if (!archive) {
   262	    return null;
   263	  }
   264	  return {
   265	    archive_dir: archive.archive_dir || "",
   266	    manifest_path: archive.manifest_json_path || "",
   267	    created_at_utc: archive.created_at_utc || "",
   268	    system_id: bundle.system_id || "unknown_system",
   269	    system_title: bundle.system_title || "",
   270	    bundle_kind: bundle.bundle_kind || "",
   271	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   272	    selected_scenario_id: bundle.selected_scenario_id || "",
   273	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   274	    has_workspace_handoff: Boolean(archive.workspace_handoff_json_path),
   275	    has_workspace_snapshot: Boolean(archive.workspace_snapshot_json_path),
   276	  };
   277	}
   278	
   279	function buildRecentWorkbenchArchiveEntryFromRestorePayload(payload) {
   280	  const bundle = payload && payload.bundle ? payload.bundle : {};
   281	  const manifest = payload && payload.manifest ? payload.manifest : {};
   282	  const files = manifest && typeof manifest.files === "object" ? manifest.files : {};
   283	  return {
   284	    archive_dir: payload.archive_dir || "",
   285	    manifest_path: payload.manifest_path || "",
   286	    created_at_utc: typeof manifest.created_at_utc === "string" ? manifest.created_at_utc : "",
   287	    system_id: bundle.system_id || "unknown_system",
   288	    system_title: bundle.system_title || "",
   289	    bundle_kind: bundle.bundle_kind || "",
   290	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   291	    selected_scenario_id: bundle.selected_scenario_id || "",
   292	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   293	    has_workspace_handoff: Boolean(files.workspace_handoff_json),
   294	    has_workspace_snapshot: Boolean(files.workspace_snapshot_json),
   295	  };
   296	}
   297	
   298	function upsertRecentWorkbenchArchiveEntry(entry) {
   299	  if (!entry || (!entry.manifest_path && !entry.archive_dir)) {
   300	    return;
   301	  }
   302	  const dedupeKey = entry.manifest_path || entry.archive_dir;
   303	  workbenchRecentArchives = [
   304	    entry,
   305	    ...workbenchRecentArchives.filter((item) => (item.manifest_path || item.archive_dir) !== dedupeKey),
   306	  ].slice(0, 6);
   307	  renderRecentWorkbenchArchives();
   308	}
   309	
   310	function renderRecentWorkbenchArchives() {
   311	  const container = workbenchElement("workbench-recent-archives-list");
   312	  const summaryElement = workbenchElement("workbench-recent-archives-summary");
   313	  if (!workbenchRecentArchives.length) {
   314	    summaryElement.textContent = "这里会列出最近成功生成的 archive；你可以直接点“恢复这个 Archive”，不用再自己查本地路径。";
   315	    container.replaceChildren((() => {
   316	      const card = document.createElement("article");
   317	      card.className = "workbench-history-card is-empty";
   318	      const title = document.createElement("strong");
   319	      title.textContent = "暂无最近 Archive";
   320	      const detail = document.createElement("p");
   321	      detail.textContent = "等你先生成一份 archive，或把已有 archive 放到默认目录后，这里就会出现可恢复列表。";
   322	      card.append(title, detail);
   323	      return card;
   324	    })());
   325	    return;
   326	  }
   327	
   328	  summaryElement.textContent = "这些 archive 都来自默认 archive root；点卡片就会自动把它恢复回当前 workbench。";
   329	  container.replaceChildren(...workbenchRecentArchives.map((entry) => {
   330	    const card = document.createElement("article");
   331	    card.className = "workbench-history-card";
   332	
   333	    const meta = document.createElement("div");
   334	    meta.className = "workbench-history-meta";
   335	
   336	    const systemChip = document.createElement("span");
   337	    systemChip.className = "workbench-history-chip";
   338	    systemChip.textContent = entry.system_id || "unknown_system";
   339	
   340	    const stateChip = document.createElement("span");
   341	    stateChip.className = "workbench-history-chip";
   342	    stateChip.dataset.state = entry.ready_for_spec_build ? "ready" : "blocked";
   343	    stateChip.textContent = entry.ready_for_spec_build ? "ready" : "blocked";
   344	
   345	    const workspaceChip = document.createElement("span");
   346	    workspaceChip.className = "workbench-history-chip";
   347	    workspaceChip.textContent = entry.has_workspace_snapshot
   348	      ? "workspace"
   349	      : (entry.has_workspace_handoff ? "handoff" : "bundle");
   350	
   351	    meta.append(systemChip, stateChip, workspaceChip);
   352	
   353	    const title = document.createElement("strong");
   354	    title.textContent = entry.system_title
   355	      ? `${entry.system_id} - ${entry.system_title}`
   356	      : entry.system_id;
   357	
   358	    const summary = summarizeRecentWorkbenchArchive(entry);
   359	    const summaryText = document.createElement("p");
   360	    summaryText.textContent = `${summary.badge} / ${summary.summary}`;
   361	
   362	    const detail = document.createElement("p");
   363	    detail.textContent = `${summary.detail} / ${entry.created_at_utc || "时间未知"}`;
   364	
   365	    const action = document.createElement("button");
   366	    action.type = "button";
   367	    action.className = "workbench-history-return-button workbench-recent-archive-action";
   368	    action.textContent = "恢复这个 Archive";
   369	    action.addEventListener("click", () => {
   370	      workbenchElement("workbench-archive-manifest-path").value = entry.archive_dir || entry.manifest_path;
   371	      void restoreWorkbenchArchiveFromManifest();
   372	    });
   373	
   374	    card.append(meta, title, summaryText, detail, action);
   375	    return card;
   376	  }));
   377	}
   378	
   379	async function refreshRecentWorkbenchArchives() {
   380	  setRequestStatus("正在刷新最近 archive 列表...", "neutral");
   381	  try {
   382	    const response = await fetch(workbenchRecentArchivesPath, {method: "GET"});
   383	    const payload = await response.json();
   384	    if (!response.ok) {
   385	      throw new Error(payload.error || "recent archives request failed");
   386	    }
   387	    workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
   388	    renderRecentWorkbenchArchives();
   389	    if (payload.default_archive_root) {
   390	      workbenchElement("default-archive-root").textContent = payload.default_archive_root;
   391	    }
   392	    setRequestStatus("最近 archive 列表已刷新。", "success");
   393	  } catch (error) {
   394	    setRequestStatus(`刷新最近 archive 列表失败：${String(error.message || error)}`, "error");
   395	  }
   396	}
   397	
   398	// ─── P43 authority helpers ────────────────────────────────────────────────────
   399	
   400	function deepFreeze(obj) {
   401	  if (obj === null || typeof obj !== "object") {
   402	    return obj;
   403	  }
   404	  Object.getOwnPropertyNames(obj).forEach((name) => {
   405	    deepFreeze(obj[name]);
   406	  });
   407	  return Object.freeze(obj);
   408	}
   409	
   410	function assignFrozenSpec(spec, origin) {  // origin: "freeze-event" | "archive-restore"
   411	  frozenSpec = deepFreeze(JSON.parse(JSON.stringify(spec)));
   412	}
   413	
   414	async function handleStartGen() {
   415	  if (frozenSpec === null) {
   416	    setRequestStatus("未找到已冻结规格 — 请先审批 Spec 再生成。", "error");
   417	    return;
   418	  }
   419	  // Write frozenSpec into the packet editor so runWorkbenchBundle() submits
   420	  // the frozen content, never a post-approval draft edit (R4 authority boundary)
   421	  const packetEl = workbenchElement("workbench-packet-json");
   422	  if (packetEl) {
   423	    packetEl.value = prettyJson(frozenSpec);
   424	    renderWorkbenchPacketDraftState();
   425	  }
   426	  if (!dispatchWorkflowEvent("start_gen")) {
   427	    setRequestStatus("当前工作流状态不允许启动生成。", "error");
   428	    return;
   429	  }
   430	  setCurrentWorkbenchRunLabel("Frozen Spec 生成");
   431	  const genOk = await runWorkbenchBundle();
   432	  dispatchWorkflowEvent(genOk ? "gen_complete" : "gen_fail");
   433	}
   434	
   435	function validateDraftAgainstFrozen(draft, frozen) {
   436	  if (frozen === null) {
   437	    return { valid: true, deviations: [] };
   438	  }
   439	  if (draft === null || typeof draft !== "object" || typeof frozen !== "object") {
   440	    return { valid: false, deviations: [{ field: "(root)", reason: "draft or frozen is not an object" }] };
   441	  }
   442	  const deviations = [];
   443	  for (const key of Object.keys(frozen)) {
   444	    if (JSON.stringify(frozen[key]) !== JSON.stringify(draft[key])) {
   445	      deviations.push({ field: key, frozen: frozen[key], draft: draft[key] });
   446	    }
   447	  }
   448	  return { valid: deviations.length === 0, deviations };
   449	}
   450	
   451	function handleFinalApprove() {
   452	  const packetEl = workbenchElement("workbench-packet-json");
   453	  const raw = packetEl ? packetEl.value : "";
   454	  let currentSpec;
   455	  try {
   456	    currentSpec = JSON.parse(raw || "{}");
   457	  } catch (error) {
   458	    setRequestStatus(`审批失败：Packet JSON 解析错误 — ${String(error.message || error)}`, "error");
   459	    return;
   460	  }
   461	
   462	  // Freeze the approved spec (R3 — only authorised write path)
   463	  assignFrozenSpec(currentSpec, "freeze-event");
   464	
   465	  // Delete draft immediately after freezing (R6)
   466	  clearDraftDesignState();
   467	
   468	  // Dispatch correct state machine event based on current state:
   469	  // PANEL_READY/ANNOTATING → final_approve → APPROVING → approve_ok → APPROVED
   470	  // INIT/FROZEN → confirm_freeze → FROZEN
   471	  if (workflowState === "PANEL_READY" || workflowState === "ANNOTATING") {
   472	    dispatchWorkflowEvent("final_approve");
   473	    dispatchWorkflowEvent("approve_ok");
   474	  } else {
   475	    dispatchWorkflowEvent("confirm_freeze");
   476	  }
   477	
   478	  setRequestStatus("Spec 已冻结。草稿已清除。可执行生成。", "success");
   479	}
   480	
   481	// ─────────────────────────────────────────────────────────────────────────────
   482	
   483	function workbenchBrowserStorage() {
   484	  try {
   485	    return window.localStorage;
   486	  } catch (error) {
   487	    return null;
   488	  }
   489	}
   490	
   491	function withWorkbenchPacketWorkspacePersistenceSuspended(callback) {
   492	  const previous = suspendWorkbenchPacketWorkspacePersistence;
   493	  suspendWorkbenchPacketWorkspacePersistence = true;
   494	  try {
   495	    return callback();
   496	  } finally {
   497	    suspendWorkbenchPacketWorkspacePersistence = previous;
   498	  }
   499	}
   500	

 succeeded in 0ms:
  1001	
  1002	function setActionsBadge(state, text) {
  1003	  const element = workbenchElement("workbench-actions-badge");
  1004	  element.dataset.state = state;
  1005	  element.textContent = text;
  1006	}
  1007	
  1008	function setSchemaRepairBadge(state, text) {
  1009	  const element = workbenchElement("workbench-schema-workspace-badge");
  1010	  element.dataset.state = state;
  1011	  element.textContent = text;
  1012	}
  1013	
  1014	function setClarificationWorkspaceBadge(state, text) {
  1015	  const element = workbenchElement("workbench-clarification-workspace-badge");
  1016	  element.dataset.state = state;
  1017	  element.textContent = text;
  1018	}
  1019	
  1020	function uniqueValues(values) {
  1021	  return [...new Set(
  1022	    values
  1023	      .map((value) => (typeof value === "string" ? value.trim() : ""))
  1024	      .filter(Boolean),
  1025	  )];
  1026	}
  1027	
  1028	function joinWithFallback(values, fallbackText = "-") {
  1029	  return values.length ? values.join(" / ") : fallbackText;
  1030	}
  1031	
  1032	function documentKindLabel(kind) {
  1033	  const labels = {
  1034	    markdown: "Markdown",
  1035	    notion: "Notion",
  1036	    pdf: "PDF",
  1037	    spreadsheet: "表格",
  1038	  };
  1039	  return labels[kind] || kind || "未知来源";
  1040	}
  1041	
  1042	function documentRoleLabel(role) {
  1043	  const labels = {
  1044	    acceptance_evidence: "验收证据",
  1045	    logic_spec: "逻辑规格",
  1046	    troubleshooting_note: "排故说明",
  1047	    timeline_note: "时间线说明",
  1048	  };
  1049	  return labels[role] || role || "未标注角色";
  1050	}
  1051	
  1052	function signalKindLabel(kind) {
  1053	  const labels = {
  1054	    command: "命令",
  1055	    commanded_state: "命令状态",
  1056	    derived: "派生量",
  1057	    sensor: "传感器",
  1058	    switch: "开关",
  1059	  };
  1060	  return labels[kind] || kind || "未知类型";
  1061	}
  1062	
  1063	function stateShapeLabel(stateShape) {
  1064	  const labels = {
  1065	    analog: "连续量",
  1066	    binary: "二值",
  1067	    discrete: "离散态",
  1068	  };
  1069	  return labels[stateShape] || stateShape || "未知形态";
  1070	}
  1071	
  1072	function createFingerprintChip(text, tone = "neutral") {
  1073	  const chip = document.createElement("span");
  1074	  chip.className = "workbench-fingerprint-chip";
  1075	  chip.dataset.tone = tone;
  1076	  chip.textContent = text;
  1077	  return chip;
  1078	}
  1079	
  1080	function createFingerprintEmptyCard(message) {
  1081	  const card = document.createElement("article");
  1082	  card.className = "workbench-fingerprint-item is-empty";
  1083	
  1084	  const detail = document.createElement("p");
  1085	  detail.className = "workbench-fingerprint-empty";
  1086	  detail.textContent = message;
  1087	
  1088	  card.append(detail);
  1089	  return card;
  1090	}
  1091	
  1092	function createActionItemCard({
  1093	  title,
  1094	  detail,
  1095	  chipText,
  1096	  chipTone = "neutral",
  1097	}) {
  1098	  const card = document.createElement("article");
  1099	  card.className = "workbench-actions-item";
  1100	
  1101	  const header = document.createElement("div");
  1102	  header.className = "workbench-actions-item-header";
  1103	
  1104	  const strong = document.createElement("strong");
  1105	  strong.className = "workbench-actions-item-title";
  1106	  strong.textContent = title;
  1107	
  1108	  const chip = createFingerprintChip(chipText, chipTone);
  1109	
  1110	  header.append(strong, chip);
  1111	
  1112	  const body = document.createElement("p");
  1113	  body.className = "workbench-actions-item-detail";
  1114	  body.textContent = detail;
  1115	
  1116	  card.append(header, body);
  1117	  return card;
  1118	}
  1119	
  1120	function createClarificationWorkspaceCard({
  1121	  id,
  1122	  prompt,
  1123	  rationale,
  1124	  requiredFor,
  1125	  answer = "",
  1126	  status = "needs_answer",
  1127	  editable = true,
  1128	}) {
  1129	  const card = document.createElement("article");
  1130	  card.className = "workbench-clarification-card";
  1131	
  1132	  const header = document.createElement("div");
  1133	  header.className = "workbench-clarification-card-header";
  1134	
  1135	  const titleGroup = document.createElement("div");
  1136	  const title = document.createElement("strong");
  1137	  title.textContent = id || "clarification";
  1138	  const promptText = document.createElement("p");
  1139	  promptText.textContent = prompt || "等待补齐说明。";
  1140	  titleGroup.append(title, promptText);
  1141	
  1142	  const chip = createFingerprintChip(status === "answered" ? "已回答" : "待回答", status === "answered" ? "ready" : "blocked");
  1143	  header.append(titleGroup, chip);
  1144	
  1145	  const meta = document.createElement("div");
  1146	  meta.className = "workbench-clarification-card-meta";
  1147	
  1148	  const rationaleText = document.createElement("span");
  1149	  rationaleText.textContent = `为什么要补：${rationale || "等待说明。"}`;
  1150	  const requiredForText = document.createElement("span");
  1151	  requiredForText.textContent = `补齐后用于：${requiredFor || "spec_build"}`;
  1152	  meta.append(rationaleText, requiredForText);
  1153	
  1154	  const textarea = document.createElement("textarea");
  1155	  textarea.className = "workbench-clarification-answer";
  1156	  textarea.dataset.questionId = id || "";
  1157	  textarea.placeholder = "在这里填写工程答案，写回 packet 后可直接重跑。";
  1158	  textarea.value = answer || "";
  1159	  textarea.disabled = !editable;
  1160	
  1161	  card.append(header, meta, textarea);
  1162	  return card;
  1163	}
  1164	
  1165	function createSchemaRepairCard({
  1166	  title,
  1167	  detail,
  1168	  targetPath,
  1169	  expectedEffect,
  1170	  autofixAvailable = false,
  1171	}) {
  1172	  const card = document.createElement("article");
  1173	  card.className = "workbench-schema-card";
  1174	
  1175	  const header = document.createElement("div");
  1176	  header.className = "workbench-schema-card-header";
  1177	
  1178	  const titleGroup = document.createElement("div");
  1179	  const strong = document.createElement("strong");
  1180	  strong.textContent = title;
  1181	  const body = document.createElement("p");
  1182	  body.textContent = detail;
  1183	  titleGroup.append(strong, body);
  1184	
  1185	  const chip = createFingerprintChip(autofixAvailable ? "可自动补齐" : "需手工修复", autofixAvailable ? "ready" : "blocked");
  1186	  header.append(titleGroup, chip);
  1187	
  1188	  const meta = document.createElement("div");
  1189	  meta.className = "workbench-schema-card-meta";
  1190	
  1191	  const pathText = document.createElement("span");
  1192	  pathText.textContent = `目标位置：${targetPath || "packet JSON"}`;
  1193	  const effectText = document.createElement("span");
  1194	  effectText.textContent = `修复结果：${expectedEffect || "修复后再重跑验证。"}`;
  1195	  meta.append(pathText, effectText);
  1196	
  1197	  card.append(header, meta);
  1198	  return card;
  1199	}
  1200	
  1201	function renderFingerprintDocumentList(documents, fallbackText) {
  1202	  const container = workbenchElement("workbench-fingerprint-doc-list");
  1203	  if (!documents.length) {
  1204	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1205	    return;
  1206	  }
  1207	
  1208	  container.replaceChildren(...documents.map((document) => {
  1209	    const card = document.createElement("article");
  1210	    card.className = "workbench-fingerprint-item";
  1211	
  1212	    const header = document.createElement("div");
  1213	    header.className = "workbench-fingerprint-item-header";
  1214	
  1215	    const title = document.createElement("strong");
  1216	    title.className = "workbench-fingerprint-item-title";
  1217	    title.textContent = document.title || document.id || "未命名文档";
  1218	
  1219	    const chips = document.createElement("div");
  1220	    chips.className = "workbench-fingerprint-chip-row";
  1221	    chips.append(
  1222	      createFingerprintChip(documentKindLabel(document.kind), "source"),
  1223	      createFingerprintChip(documentRoleLabel(document.role), "role"),
  1224	    );
  1225	
  1226	    header.append(title, chips);
  1227	
  1228	    const location = document.createElement("p");
  1229	    location.className = "workbench-fingerprint-item-detail";
  1230	    location.textContent = document.location || "未提供路径";
  1231	
  1232	    card.append(header, location);
  1233	    return card;
  1234	  }));
  1235	}
  1236	
  1237	function renderFingerprintSignalList(signals, fallbackText) {
  1238	  const container = workbenchElement("workbench-fingerprint-signal-list");
  1239	  if (!signals.length) {
  1240	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1241	    return;
  1242	  }
  1243	
  1244	  container.replaceChildren(...signals.map((signal) => {
  1245	    const card = document.createElement("article");
  1246	    card.className = "workbench-fingerprint-item";
  1247	
  1248	    const header = document.createElement("div");
  1249	    header.className = "workbench-fingerprint-item-header";
  1250	
  1251	    const title = document.createElement("strong");
  1252	    title.className = "workbench-fingerprint-item-title";
  1253	    title.textContent = signal.label || signal.id || "未命名信号";
  1254	
  1255	    const chips = document.createElement("div");
  1256	    chips.className = "workbench-fingerprint-chip-row";
  1257	    chips.append(
  1258	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
  1259	      createFingerprintChip(stateShapeLabel(signal.state_shape), "shape"),
  1260	      createFingerprintChip(signal.unit || "无单位", "unit"),
  1261	    );
  1262	
  1263	    header.append(title, chips);
  1264	
  1265	    const detail = document.createElement("p");
  1266	    detail.className = "workbench-fingerprint-item-detail";
  1267	    detail.textContent = signal.id ? `signal_id = ${signal.id}` : "未提供 signal_id";
  1268	
  1269	    card.append(header, detail);
  1270	    return card;
  1271	  }));
  1272	}
  1273	
  1274	function renderSystemFingerprint({
  1275	  badgeState = "idle",
  1276	  badgeText = "等待生成",
  1277	  summary = "这里会直接告诉你第二套系统到底长什么样，而不只是告诉你它能不能接。",
  1278	  systemId = "-",
  1279	  objective = "-",
  1280	  sourceMode = "-",
  1281	  sourceTruth = "-",
  1282	  documents = [],
  1283	  signals = [],
  1284	  documentFallback = "还没有来源文档。",
  1285	  signalFallback = "还没有关键信号定义。",
  1286	} = {}) {
  1287	  setFingerprintBadge(badgeState, badgeText);
  1288	  renderValue("workbench-fingerprint-summary", summary);
  1289	  renderValue("workbench-fingerprint-system-id", systemId);
  1290	  renderValue("workbench-fingerprint-objective", objective);
  1291	  renderValue("workbench-fingerprint-source-mode", sourceMode);
  1292	  renderValue("workbench-fingerprint-source-truth", sourceTruth);
  1293	  renderValue("workbench-fingerprint-doc-count", `${documents.length} 份文档`);
  1294	  renderValue("workbench-fingerprint-signal-count", `${signals.length} 个信号`);
  1295	  renderFingerprintDocumentList(documents, documentFallback);
  1296	  renderFingerprintSignalList(signals, signalFallback);
  1297	}
  1298	
  1299	function renderActionList(containerId, items, fallbackText) {
  1300	  const container = workbenchElement(containerId);
  1301	  if (!items.length) {
  1302	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1303	    return;
  1304	  }
  1305	  container.replaceChildren(...items);
  1306	}
  1307	
  1308	function renderOnboardingActions({
  1309	  badgeState = "idle",
  1310	  badgeText = "等待生成",
  1311	  summary = "这里会把接入动作拆成三列：先补澄清、再补结构、最后看解锁项。",
  1312	  followUps = [],
  1313	  blockers = [],
  1314	  unlocks = [],
  1315	  followUpFallback = "运行后这里会列出需要先回答的澄清项。",
  1316	  blockerFallback = "运行后这里会列出需要补的结构问题。",
  1317	  unlockFallback = "运行后这里会列出补齐后可解锁的能力。",
  1318	} = {}) {
  1319	  setActionsBadge(badgeState, badgeText);
  1320	  renderValue("workbench-actions-summary", summary);
  1321	  renderValue("workbench-actions-follow-up-count", `${followUps.length} 项`);
  1322	  renderValue("workbench-actions-schema-count", `${blockers.length} 项`);
  1323	  renderValue("workbench-actions-unlock-count", `${unlocks.length} 项`);
  1324	  renderActionList("workbench-actions-follow-up-list", followUps, followUpFallback);
  1325	  renderActionList("workbench-actions-schema-list", blockers, blockerFallback);
  1326	  renderActionList("workbench-actions-unlock-list", unlocks, unlockFallback);
  1327	}
  1328	
  1329	function setSchemaRepairActionState(disabled) {
  1330	  workbenchElement("workbench-apply-schema-repairs").disabled = disabled;
  1331	}
  1332	
  1333	function renderSchemaRepairWorkspace({
  1334	  badgeState = "idle",
  1335	  badgeText = "等待生成",
  1336	  summary = "这里会把 schema blocker 里的安全 autofix 项单独挑出来。",
  1337	  cards = [],
  1338	  fallbackTitle = "等待生成",
  1339	  fallbackText = "blocked bundle 出来后，这里会显示 repair suggestions。",
  1340	  note = "只有后端标记为 safe autofix 的修复才会开放一键应用。",
  1341	  actionsDisabled = true,
  1342	} = {}) {
  1343	  setSchemaRepairBadge(badgeState, badgeText);
  1344	  renderValue("workbench-schema-workspace-summary", summary);
  1345	  renderValue("workbench-schema-workspace-note", note);
  1346	  const container = workbenchElement("workbench-schema-workspace-list");
  1347	  if (!cards.length) {
  1348	    const emptyCard = document.createElement("article");
  1349	    emptyCard.className = "workbench-schema-card is-empty";
  1350	    const title = document.createElement("strong");
  1351	    title.textContent = fallbackTitle;
  1352	    const detail = document.createElement("p");
  1353	    detail.textContent = fallbackText;
  1354	    emptyCard.append(title, detail);
  1355	    container.replaceChildren(emptyCard);
  1356	  } else {
  1357	    container.replaceChildren(...cards);
  1358	  }
  1359	  setSchemaRepairActionState(actionsDisabled);
  1360	}
  1361	
  1362	function renderSchemaRepairWorkspaceFromPayload(payload) {
  1363	  const bundle = payload.bundle || {};
  1364	  const assessment = bundle.intake_assessment || {};
  1365	  const ready = Boolean(bundle.ready_for_spec_build);
  1366	  const repairSuggestions = Array.isArray(assessment.repair_suggestions) ? assessment.repair_suggestions : [];
  1367	  const safeSuggestions = repairSuggestions.filter((item) => item.autofix_available);
  1368	  const cards = repairSuggestions.map((item) => createSchemaRepairCard({
  1369	    title: item.title || item.id || "schema repair",
  1370	    detail: item.detail || item.blocking_reason || "等待修复说明。",
  1371	    targetPath: item.target_path || "packet JSON",
  1372	    expectedEffect: item.expected_effect,
  1373	    autofixAvailable: Boolean(item.autofix_available),
  1374	  }));
  1375	
  1376	  if (ready) {
  1377	    renderSchemaRepairWorkspace({
  1378	      badgeState: "ready",
  1379	      badgeText: "当前无需修复",
  1380	      summary: "这次 bundle 已经没有 schema blocker 需要修复；工作台保留为空，避免把当前 ready 状态误读成还有结构问题。",
  1381	      fallbackTitle: "当前无需 schema 修复",
  1382	      fallbackText: "schema blocker 已经清空，可以继续用当前 packet 跑 playback / diagnosis / knowledge。",
  1383	      note: "当前没有安全 schema 修复要应用。",
  1384	      actionsDisabled: true,
  1385	    });
  1386	    return;
  1387	  }
  1388	
  1389	  renderSchemaRepairWorkspace({
  1390	    badgeState: safeSuggestions.length ? "blocked" : "idle",
  1391	    badgeText: safeSuggestions.length ? "可安全修一点" : "暂时无安全修复",
  1392	    summary: safeSuggestions.length
  1393	      ? "这次 blocked bundle 里有后端确认安全的 schema autofix。你可以一键应用这些修复，然后马上重跑。"
  1394	      : "这次 blocked bundle 虽然还有 schema blocker，但当前没有被后端判定为 safe autofix 的修复项。",
  1395	    cards,
  1396	    fallbackTitle: "当前没有 repair suggestion",
  1397	    fallbackText: "当前没有额外 schema repair suggestion；如果仍阻塞，请直接检查 packet JSON。",
  1398	    note: safeSuggestions.length
  1399	      ? `当前共有 ${safeSuggestions.length} 条 safe autofix；工作台不会猜修复逻辑，只调用后端声明为安全的 patch。`
  1400	      : "剩余 schema blocker 需要手工修改 packet JSON 或工程语义后再重跑。",
  1401	    actionsDisabled: !safeSuggestions.length,
  1402	  });
  1403	}
  1404	
  1405	function setClarificationWorkspaceActionState(disabled) {
  1406	  workbenchElement("workbench-apply-clarifications").disabled = disabled;
  1407	  workbenchElement("workbench-apply-and-rerun").disabled = disabled;
  1408	}
  1409	
  1410	function renderClarificationWorkspace({
  1411	  badgeState = "idle",
  1412	  badgeText = "等待生成",
  1413	  summary = "这里会把需要补的 clarification 直接变成可填写表单，方便你写回当前 packet。",
  1414	  cards = [],
  1415	  fallbackTitle = "等待生成",
  1416	  fallbackText = "当 bundle 停在 clarification gate 时，这里会出现可直接填写的答案卡。",
  1417	  note = "先运行一次 blocked bundle，这里才会知道哪些问题还没回答。",
  1418	  actionsDisabled = true,
  1419	} = {}) {
  1420	  setClarificationWorkspaceBadge(badgeState, badgeText);
  1421	  renderValue("workbench-clarification-workspace-summary", summary);
  1422	  renderValue("workbench-clarification-workspace-note", note);
  1423	  const container = workbenchElement("workbench-clarification-workspace-list");
  1424	  if (!cards.length) {
  1425	    const emptyCard = document.createElement("article");
  1426	    emptyCard.className = "workbench-clarification-card is-empty";
  1427	    const title = document.createElement("strong");
  1428	    title.textContent = fallbackTitle;
  1429	    const detail = document.createElement("p");
  1430	    detail.textContent = fallbackText;
  1431	    emptyCard.append(title, detail);
  1432	    container.replaceChildren(emptyCard);
  1433	  } else {
  1434	    container.replaceChildren(...cards);
  1435	  }
  1436	  setClarificationWorkspaceActionState(actionsDisabled);
  1437	}
  1438	
  1439	function renderClarificationWorkspaceFromPayload(payload) {
  1440	  const bundle = payload.bundle || {};
  1441	  const clarification = bundle.clarification_brief || {};
  1442	  const ready = Boolean(bundle.ready_for_spec_build);
  1443	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  1444	  const unresolvedItems = followUpItems.filter((item) => item.status !== "answered");
  1445	  const cards = unresolvedItems.map((item) => createClarificationWorkspaceCard({
  1446	    id: item.id,
  1447	    prompt: item.prompt,
  1448	    rationale: item.rationale,
  1449	    requiredFor: item.required_for,
  1450	    answer: item.answer,
  1451	    status: item.status,
  1452	    editable: true,
  1453	  }));
  1454	
  1455	  if (ready) {
  1456	    renderClarificationWorkspace({
  1457	      badgeState: "ready",
  1458	      badgeText: "澄清已放行",
  1459	      summary: "这次 bundle 已经把 clarification gate 走通了；当前无需补答，如果要改问题答案，可以直接编辑 packet JSON 后重跑。",
  1460	      fallbackTitle: "当前无需回填",
  1461	      fallbackText: "clarification 问题已经补齐，当前链路可以继续往 playback / diagnosis / knowledge 走。",
  1462	      note: "当前 packet 已 ready；工作台按钮已关闭，避免把已通过状态误当成待补状态。",
  1463	      actionsDisabled: true,
  1464	    });
  1465	    return;
  1466	  }
  1467	
  1468	  renderClarificationWorkspace({
  1469	    badgeState: cards.length ? "blocked" : "idle",
  1470	    badgeText: cards.length ? "可直接回填" : "等待回填项",
  1471	    summary: cards.length
  1472	      ? "当前 bundle 停在 clarification gate；你可以直接在这里填写工程答案，写回 packet 后立即重跑。"
  1473	      : "这次虽然没 ready，但当前没有额外待回答的问题卡；如果仍阻塞，请优先看上方 schema blocker。",
  1474	    cards,
  1475	    fallbackTitle: "当前没有待答问题",
  1476	    fallbackText: "clarification 问题已经回答完毕，剩下的阻塞主要来自 schema / 结构问题。",
  1477	    note: cards.length
  1478	      ? `已加载 ${cards.length} 条待回答 clarification；“写回当前 Packet”不会新增前端规则，只会更新 packet JSON。`
  1479	      : "当前无待回答 clarification；请先修复 schema blocker 后再重跑。",
  1480	    actionsDisabled: !cards.length,
  1481	  });
  1482	}
  1483	
  1484	function currentClarificationWorkspaceAnswers() {
  1485	  return [...document.querySelectorAll(".workbench-clarification-answer")]
  1486	    .map((field) => ({
  1487	      questionId: field.dataset.questionId || "",
  1488	      answer: field.value.trim(),
  1489	    }))
  1490	    .filter((item) => item.questionId);
  1491	}
  1492	
  1493	function applyClarificationWorkspaceAnswersToPacket(packetPayload) {
  1494	  const nextPayload = cloneJson(packetPayload);
  1495	  const existingAnswers = Array.isArray(nextPayload.clarification_answers) ? nextPayload.clarification_answers : [];
  1496	  const answerMap = new Map(existingAnswers
  1497	    .filter((item) => item && typeof item.question_id === "string" && item.question_id.trim())
  1498	    .map((item) => [item.question_id.trim(), {
  1499	      question_id: item.question_id.trim(),
  1500	      answer: typeof item.answer === "string" ? item.answer : "",

 succeeded in 0ms:
   501	function readWorkbenchPersistedFieldValue(id) {
   502	  const field = workbenchElement(id);
   503	  if (!field) {
   504	    return null;
   505	  }
   506	  if (field.type === "checkbox") {
   507	    return Boolean(field.checked);
   508	  }
   509	  return field.value;
   510	}
   511	
   512	function applyWorkbenchPersistedFieldValue(id, value) {
   513	  const field = workbenchElement(id);
   514	  if (!field || value === undefined || value === null) {
   515	    return;
   516	  }
   517	  if (field.type === "checkbox") {
   518	    field.checked = Boolean(value);
   519	    return;
   520	  }
   521	  field.value = String(value);
   522	}
   523	
   524	function nextWorkbenchSequenceFromIds(entries, prefix) {
   525	  if (!Array.isArray(entries) || !entries.length) {
   526	    return 0;
   527	  }
   528	  return entries.reduce((maxValue, entry) => {
   529	    if (!entry || typeof entry.id !== "string" || !entry.id.startsWith(prefix)) {
   530	      return maxValue;
   531	    }
   532	    const sequence = Number(entry.id.slice(prefix.length));
   533	    if (!Number.isFinite(sequence)) {
   534	      return maxValue;
   535	    }
   536	    return Math.max(maxValue, sequence);
   537	  }, 0);
   538	}
   539	
   540	function activeWorkbenchPacketPayload() {
   541	  const parsed = parseWorkbenchPacketEditor();
   542	  if (parsed.payload) {
   543	    return parsed.payload;
   544	  }
   545	  const selectedEntry = selectedWorkbenchPacketRevisionEntry();
   546	  return selectedEntry ? selectedEntry.payload : null;
   547	}
   548	
   549	function activeWorkbenchHistoryEntry() {
   550	  if (!workbenchRunHistory.length) {
   551	    return null;
   552	  }
   553	  if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
   554	    return workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || latestWorkbenchHistoryEntry();
   555	  }
   556	  return latestWorkbenchHistoryEntry();
   557	}
   558	
   559	function buildWorkbenchHandoffSnapshot() {
   560	  const packetPayload = activeWorkbenchPacketPayload();
   561	  const packetEntry = selectedWorkbenchPacketRevisionEntry();
   562	  const packetSummary = packetPayload ? summarizePacketPayload(packetPayload) : null;
   563	  const resultEntry = activeWorkbenchHistoryEntry();
   564	  const resultSnapshot = detailedWorkbenchHistoryEntry(resultEntry);
   565	  const archive = resultEntry && resultEntry.payload ? resultEntry.payload.archive || null : null;
   566	  const note = String(readWorkbenchPersistedFieldValue("workbench-handoff-note") || "").trim();
   567	
   568	  let badgeState = "idle";
   569	  let badgeText = "等待载入";
   570	  let summary = "先载入 packet；系统才有可交接的当前状态。";
   571	
   572	  if (currentWorkbenchViewMode === "running") {
   573	    badgeState = "idle";
   574	    badgeText = "正在整理";
   575	    summary = note
   576	      ? "当前工作区正在生成新结果；你的交接备注会和最终状态一起留在导出快照里。"
   577	      : "当前工作区正在生成新结果；如果准备跨浏览器或交给别人，等结果出来后再补一段交接备注会更稳。";
   578	  } else if (resultEntry && resultEntry.archived) {
   579	    badgeState = "archived";
   580	    badgeText = "可交接";
   581	    summary = note
   582	      ? "当前工作区已经带交接备注，且结果已归档；导出快照后，接手人可以直接从这份状态继续。"
   583	      : "当前工作区已经具备可交接的 packet、结果和 archive 状态；如果要正式交接，建议再补一段备注。";
   584	  } else if (resultEntry && resultEntry.state === "ready") {
   585	    badgeState = "ready";
   586	    badgeText = "可交接";
   587	    summary = note
   588	      ? "当前工作区已经带交接备注；虽然这次没归档也可以继续交接，但备注里最好说明下一步要不要补 archive。"
   589	      : "当前工作区已经有 ready 结果；如果准备交给下一位，建议补一段备注说明是否还要 archive。";
   590	  } else if (resultEntry) {
   591	    badgeState = "blocked";
   592	    badgeText = resultEntry.state === "failure" ? "先修正" : "待补齐";
   593	    summary = note
   594	      ? "当前工作区已经带交接备注；接手人打开快照后会先看到现在卡在哪、为什么卡住。"
   595	      : "当前工作区已经明确告诉你卡在哪，但如果要跨浏览器或跨人交接，最好再补一段备注说明下一步。";
   596	  } else if (packetPayload) {
   597	    badgeState = "idle";
   598	    badgeText = "待运行";
   599	    summary = note
   600	      ? "当前只有 packet 和交接备注，还没有结果历史；接手人需要从这个输入基线继续跑 bundle。"
   601	      : "当前 packet 已就位，但还没有结果；如果你准备交接给下一位，建议先写备注说明为什么停在这里。";
   602	  }
   603	
   604	  return {
   605	    note,
   606	    badgeState,
   607	    badgeText,
   608	    summary,
   609	    system: packetPayload ? (packetPayload.system_id || "unknown_system") : "等待载入",
   610	    systemDetail: packetEntry
   611	      ? `${packetEntry.title} / ${packetEntry.timeLabel}`
   612	      : "当前输入区还没有已识别 packet 版本。",
   613	    packet: packetSummary
   614	      ? `${packetSummary.sourceDocuments} docs / ${packetSummary.logicNodes} logic / ${packetSummary.faultModes} faults`
   615	      : "等待载入",
   616	    packetDetail: packetSummary
   617	      ? `${packetSummary.components} components / ${packetSummary.scenarios} scenarios / ${packetSummary.clarificationAnswers} answers`
   618	      : "先载入 packet 后，这里会显示覆盖规模。",
   619	    result: currentWorkbenchViewMode === "running"
   620	      ? "正在生成"
   621	      : resultSnapshot
   622	        ? `${resultSnapshot.verdict} / ${resultSnapshot.scenario}`
   623	        : "等待第一次结果",
   624	    resultDetail: currentWorkbenchViewMode === "running"
   625	      ? "系统正在生成新结果；完成后这里会自动刷新。"
   626	      : resultSnapshot
   627	        ? resultSnapshot.blocker
   628	        : "还没有 bundle 结果。",
   629	    archive: archive ? "已留档" : (currentWorkbenchViewMode === "running" ? "处理中" : "未生成"),
   630	    archiveDetail: archive
   631	      ? shortPath(archive.archive_dir)
   632	      : resultSnapshot
   633	        ? resultSnapshot.archive
   634	        : "还没有 archive package。",
   635	    workspace: `${workbenchPacketRevisionHistory.length} 个 packet 版本 / ${workbenchRunHistory.length} 个结果`,
   636	    workspaceDetail:
   637	      currentWorkbenchViewMode === "history" && resultEntry
   638	        ? `当前在历史回看模式：${resultEntry.title} / ${resultEntry.timeLabel}`
   639	        : currentWorkbenchViewMode === "latest" && resultEntry
   640	          ? `当前主看板展示最新结果：${resultEntry.title} / ${resultEntry.timeLabel}`
   641	          : currentWorkbenchViewMode === "running"
   642	            ? "当前主看板正在生成新结果。"
   643	            : packetEntry
   644	              ? `当前 packet 基线：${packetEntry.title} / ${packetEntry.timeLabel}`
   645	              : "等待第一次 packet 载入。",
   646	  };
   647	}
   648	
   649	function renderWorkbenchHandoffBoard() {
   650	  const snapshot = buildWorkbenchHandoffSnapshot();
   651	  const badge = workbenchElement("workbench-handoff-badge");
   652	  badge.dataset.state = snapshot.badgeState;
   653	  badge.textContent = snapshot.badgeText;
   654	  renderValue("workbench-handoff-summary", snapshot.summary);
   655	  renderValue("workbench-handoff-system", snapshot.system);
   656	  renderValue("workbench-handoff-system-detail", snapshot.systemDetail);
   657	  renderValue("workbench-handoff-packet", snapshot.packet);
   658	  renderValue("workbench-handoff-packet-detail", snapshot.packetDetail);
   659	  renderValue("workbench-handoff-result", snapshot.result);
   660	  renderValue("workbench-handoff-result-detail", snapshot.resultDetail);
   661	  renderValue("workbench-handoff-archive", snapshot.archive);
   662	  renderValue("workbench-handoff-archive-detail", snapshot.archiveDetail);
   663	  renderValue("workbench-handoff-workspace", snapshot.workspace);
   664	  renderValue("workbench-handoff-workspace-detail", snapshot.workspaceDetail);
   665	}
   666	
   667	function workbenchHandoffBriefText() {
   668	  const snapshot = buildWorkbenchHandoffSnapshot();
   669	  const lines = [
   670	    "工作区交接摘要",
   671	    `- 状态：${snapshot.badgeText}`,
   672	    `- 系统：${snapshot.system}`,
   673	    `- 系统细节：${snapshot.systemDetail}`,
   674	    `- Packet 覆盖：${snapshot.packet}`,
   675	    `- Packet 细节：${snapshot.packetDetail}`,
   676	    `- 当前结果：${snapshot.result}`,
   677	    `- 结果细节：${snapshot.resultDetail}`,
   678	    `- Archive 状态：${snapshot.archive}`,
   679	    `- Archive 细节：${snapshot.archiveDetail}`,
   680	    `- 工作区规模：${snapshot.workspace}`,
   681	    `- 工作区细节：${snapshot.workspaceDetail}`,
   682	  ];
   683	  if (snapshot.note) {
   684	    lines.push(`- 交接备注：${snapshot.note}`);
   685	  }
   686	  return lines.join("\n");
   687	}
   688	
   689	async function copyWorkbenchHandoffBrief() {
   690	  const text = workbenchHandoffBriefText();
   691	  try {
   692	    if (navigator.clipboard && navigator.clipboard.writeText) {
   693	      await navigator.clipboard.writeText(text);
   694	    } else {
   695	      const textarea = document.createElement("textarea");
   696	      textarea.value = text;
   697	      textarea.setAttribute("readonly", "true");
   698	      textarea.style.position = "absolute";
   699	      textarea.style.left = "-9999px";
   700	      document.body.append(textarea);
   701	      textarea.select();
   702	      document.execCommand("copy");
   703	      textarea.remove();
   704	    }
   705	    setRequestStatus("当前工作区交接摘要已复制。", "success");
   706	  } catch (error) {
   707	    setRequestStatus(`复制交接摘要失败：${String(error.message || error)}`, "error");
   708	  }
   709	}
   710	
   711	function collectWorkbenchPacketWorkspaceState() {
   712	  return {
   713	    kind: "well-harness-workbench-browser-workspace",
   714	    version: 2,
   715	    exportedAt: new Date().toISOString(),
   716	    handoff: buildWorkbenchHandoffSnapshot(),
   717	    packetJsonText: workbenchElement("workbench-packet-json").value,
   718	    packetSourceStatus: workbenchElement("workbench-packet-source-status").textContent,
   719	    currentWorkbenchRunLabel,
   720	    selectedWorkbenchPacketRevisionId,
   721	    packetRevisionHistory: cloneJson(workbenchPacketRevisionHistory),
   722	    currentWorkbenchViewMode,
   723	    selectedWorkbenchHistoryId,
   724	    runHistory: cloneJson(workbenchRunHistory),
   725	    fields: Object.fromEntries(workbenchPersistedFieldIds.map((id) => [id, readWorkbenchPersistedFieldValue(id)])),
   726	  };
   727	}
   728	
   729	function persistWorkbenchPacketWorkspace() {
   730	  renderWorkbenchHandoffBoard();
   731	  if (suspendWorkbenchPacketWorkspacePersistence) {
   732	    return;
   733	  }
   734	  const storage = workbenchBrowserStorage();
   735	  if (!storage) {
   736	    return;
   737	  }
   738	  try {
   739	    storage.setItem(
   740	      workbenchPacketWorkspaceStorageKey,
   741	      JSON.stringify(collectWorkbenchPacketWorkspaceState()),
   742	    );
   743	  } catch (error) {
   744	    // Ignore persistence failures so the workbench stays usable in storage-limited environments.
   745	  }
   746	}
   747	
   748	function clearPersistedWorkbenchPacketWorkspace() {
   749	  const storage = workbenchBrowserStorage();
   750	  if (!storage) {
   751	    return;
   752	  }
   753	  try {
   754	    storage.removeItem(workbenchPacketWorkspaceStorageKey);
   755	  } catch (error) {
   756	    // Ignore storage cleanup failures.
   757	  }
   758	}
   759	
   760	function loadPersistedWorkbenchPacketWorkspace() {
   761	  const storage = workbenchBrowserStorage();
   762	  if (!storage) {
   763	    return null;
   764	  }
   765	  const raw = storage.getItem(workbenchPacketWorkspaceStorageKey);
   766	  if (!raw) {
   767	    return null;
   768	  }
   769	  try {
   770	    return JSON.parse(raw);
   771	  } catch (error) {
   772	    clearPersistedWorkbenchPacketWorkspace();
   773	    return null;
   774	  }
   775	}
   776	
   777	// ─── P43 draft_design_state persistence (UI-owned, never read by backend) ─────
   778	
   779	function saveDraftDesignState(draftObj) {
   780	  const storage = workbenchBrowserStorage();
   781	  if (!storage) {
   782	    return;
   783	  }
   784	  try {
   785	    storage.setItem(draftDesignStateKey, JSON.stringify(draftObj));
   786	  } catch (error) {
   787	    // Ignore persistence failures so the workbench stays usable.
   788	  }
   789	}
   790	
   791	function loadDraftDesignState() {
   792	  const storage = workbenchBrowserStorage();
   793	  if (!storage) {
   794	    return null;
   795	  }
   796	  const raw = storage.getItem(draftDesignStateKey);
   797	  if (!raw) {
   798	    return null;
   799	  }
   800	  try {
   801	    return JSON.parse(raw);
   802	  } catch (error) {
   803	    clearDraftDesignState();
   804	    return null;
   805	  }
   806	}
   807	
   808	function clearDraftDesignState() {
   809	  const storage = workbenchBrowserStorage();
   810	  if (!storage) {
   811	    return;
   812	  }
   813	  try {
   814	    storage.removeItem(draftDesignStateKey);
   815	  } catch (error) {
   816	    // Ignore cleanup failures.
   817	  }
   818	}
   819	
   820	// ─────────────────────────────────────────────────────────────────────────────
   821	
   822	function workspaceSnapshotDownloadName() {
   823	  const now = new Date();
   824	  const timestamp = [
   825	    now.getFullYear(),
   826	    String(now.getMonth() + 1).padStart(2, "0"),
   827	    String(now.getDate()).padStart(2, "0"),
   828	    "-",
   829	    String(now.getHours()).padStart(2, "0"),
   830	    String(now.getMinutes()).padStart(2, "0"),
   831	    String(now.getSeconds()).padStart(2, "0"),
   832	  ].join("");
   833	  return `well-harness-workbench-workspace-${timestamp}.json`;
   834	}
   835	
   836	function packetRevisionSignature(payload) {
   837	  return JSON.stringify(payload);
   838	}
   839	
   840	function nextWorkbenchHistoryId() {
   841	  workbenchHistorySequence += 1;
   842	  return `workbench-history-${workbenchHistorySequence}`;
   843	}
   844	
   845	function nextWorkbenchPacketRevisionId() {
   846	  workbenchPacketRevisionSequence += 1;
   847	  return `workbench-packet-revision-${workbenchPacketRevisionSequence}`;
   848	}
   849	
   850	function setActiveWorkbenchPreset(presetId) {
   851	  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
   852	    const selected = button.dataset.workbenchPreset === presetId;
   853	    button.classList.toggle("is-selected", selected);
   854	    button.setAttribute("aria-pressed", selected ? "true" : "false");
   855	  });
   856	}
   857	
   858	function setCurrentWorkbenchRunLabel(label) {
   859	  currentWorkbenchRunLabel = label || "手动生成";
   860	  persistWorkbenchPacketWorkspace();
   861	}
   862	
   863	function setPacketEditor(payload) {
   864	  workbenchElement("workbench-packet-json").value = prettyJson(payload);
   865	  persistWorkbenchPacketWorkspace();
   866	}
   867	
   868	function parseWorkbenchPacketEditor() {
   869	  const raw = workbenchElement("workbench-packet-json").value;
   870	  if (!raw.trim()) {
   871	    return {error: "当前 Packet JSON 为空。"};
   872	  }
   873	  try {
   874	    return {payload: JSON.parse(raw)};
   875	  } catch (error) {
   876	    return {error: String(error.message || error)};
   877	  }
   878	}
   879	
   880	function renderValue(elementId, value, fallbackText = "-") {
   881	  if (typeof value === "string") {
   882	    const text = value.trim();
   883	    workbenchElement(elementId).textContent = text || fallbackText;
   884	    return;
   885	  }
   886	  if (value === null || value === undefined) {
   887	    workbenchElement(elementId).textContent = fallbackText;
   888	    return;
   889	  }
   890	  workbenchElement(elementId).textContent = String(value);
   891	}
   892	
   893	function summarizePacketPayload(payload) {
   894	  return {
   895	    sourceDocuments: Array.isArray(payload.source_documents) ? payload.source_documents.length : 0,
   896	    components: Array.isArray(payload.components) ? payload.components.length : 0,
   897	    logicNodes: Array.isArray(payload.logic_nodes) ? payload.logic_nodes.length : 0,
   898	    scenarios: Array.isArray(payload.acceptance_scenarios) ? payload.acceptance_scenarios.length : 0,
   899	    faultModes: Array.isArray(payload.fault_modes) ? payload.fault_modes.length : 0,
   900	    clarificationAnswers: Array.isArray(payload.clarification_answers) ? payload.clarification_answers.length : 0,
   901	  };
   902	}
   903	
   904	function packetRevisionDetailText(payload) {
   905	  const summary = summarizePacketPayload(payload);
   906	  return `docs=${summary.sourceDocuments} / components=${summary.components} / logic=${summary.logicNodes} / scenarios=${summary.scenarios} / faults=${summary.faultModes} / answers=${summary.clarificationAnswers}`;
   907	}
   908	
   909	function latestWorkbenchPacketRevisionEntry() {
   910	  return workbenchPacketRevisionHistory.length ? workbenchPacketRevisionHistory[0] : null;
   911	}
   912	
   913	function selectedWorkbenchPacketRevisionEntry() {
   914	  return workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || latestWorkbenchPacketRevisionEntry();
   915	}
   916	
   917	function normalizeWorkbenchPacketRevisionHistory(entries) {
   918	  if (!Array.isArray(entries)) {
   919	    return [];
   920	  }
   921	  return entries
   922	    .filter((entry) => entry && typeof entry.id === "string" && entry.id && entry.payload)
   923	    .map((entry) => ({
   924	      id: entry.id,
   925	      timeLabel: entry.timeLabel || historyTimeLabel(),
   926	      title: entry.title || "Packet 更新",
   927	      payload: cloneJson(entry.payload),
   928	      summary: entry.summary || `${entry.payload.system_id || "unknown_system"} 已更新`,
   929	      detail: entry.detail || packetRevisionDetailText(entry.payload),
   930	      signature: packetRevisionSignature(entry.payload),
   931	    }))
   932	    .slice(0, maxWorkbenchPacketRevisionHistory);
   933	}
   934	
   935	function normalizeWorkbenchRunHistory(entries) {
   936	  if (!Array.isArray(entries)) {
   937	    return [];
   938	  }
   939	  return entries
   940	    .filter((entry) => entry && typeof entry.id === "string" && entry.id)
   941	    .map((entry) => ({
   942	      id: entry.id,
   943	      state: entry.state || "failure",
   944	      stateLabel: entry.stateLabel || (entry.state === "ready" ? "通过" : entry.state === "blocked" ? "阻塞" : "失败"),
   945	      archived: Boolean(entry.archived),
   946	      timeLabel: entry.timeLabel || historyTimeLabel(),
   947	      title: entry.title || "手动生成",
   948	      payload: entry.payload ? cloneJson(entry.payload) : null,
   949	      errorMessage: entry.errorMessage ? String(entry.errorMessage) : undefined,
   950	      summary: entry.summary || "请求未完成",
   951	      detail: entry.detail || "等待详情。",
   952	    }))
   953	    .slice(0, maxWorkbenchRunHistory);
   954	}
   955	
   956	function buildWorkbenchPacketRevisionEntry(payload, {
   957	  title,
   958	  summary,
   959	  detail,
   960	} = {}) {
   961	  return {
   962	    id: nextWorkbenchPacketRevisionId(),
   963	    timeLabel: historyTimeLabel(),
   964	    title: title || "Packet 更新",
   965	    payload: cloneJson(payload),
   966	    summary: summary || `${payload.system_id || "unknown_system"} 已更新`,
   967	    detail: detail || packetRevisionDetailText(payload),
   968	    signature: packetRevisionSignature(payload),
   969	  };
   970	}
   971	
   972	function splitLines(text) {
   973	  return text
   974	    .split("\n")
   975	    .map((item) => item.trim())
   976	    .filter(Boolean);
   977	}
   978	
   979	function setVisualBadge(state, text) {
   980	  const element = workbenchElement("workbench-visual-badge");
   981	  element.dataset.state = state;
   982	  element.textContent = text;
   983	}
   984	
   985	function setStageState(stageName, state, note) {
   986	  workbenchElement(`workbench-stage-${stageName}`).dataset.state = state;
   987	  workbenchElement(`workbench-stage-${stageName}-note`).textContent = note;
   988	}
   989	
   990	function setOnboardingBadge(state, text) {
   991	  const element = workbenchElement("workbench-onboarding-badge");
   992	  element.dataset.state = state;
   993	  element.textContent = text;
   994	}
   995	
   996	function setFingerprintBadge(state, text) {
   997	  const element = workbenchElement("workbench-fingerprint-badge");
   998	  element.dataset.state = state;
   999	  element.textContent = text;
  1000	}

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1501,2000p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1501	      status: item.status || "answered",
  1502	    }]));
  1503	  const workspaceAnswers = currentClarificationWorkspaceAnswers();
  1504	  const workspaceIds = workspaceAnswers.map((item) => item.questionId);
  1505	
  1506	  workspaceAnswers.forEach((item) => {
  1507	    if (!item.answer) {
  1508	      answerMap.delete(item.questionId);
  1509	      return;
  1510	    }
  1511	    answerMap.set(item.questionId, {
  1512	      question_id: item.questionId,
  1513	      answer: item.answer,
  1514	      status: "answered",
  1515	    });
  1516	  });
  1517	
  1518	  nextPayload.clarification_answers = [
  1519	    ...workspaceIds
  1520	      .map((questionId) => answerMap.get(questionId))
  1521	      .filter(Boolean),
  1522	    ...[...answerMap.entries()]
  1523	      .filter(([questionId]) => !workspaceIds.includes(questionId))
  1524	      .map(([, answer]) => answer),
  1525	  ];
  1526	  return {
  1527	    packetPayload: nextPayload,
  1528	    answeredCount: workspaceAnswers.filter((item) => item.answer).length,
  1529	  };
  1530	}
  1531	
  1532	async function runWorkbenchSchemaSafeRepair() {
  1533	  let packetPayload;
  1534	  try {
  1535	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  1536	  } catch (error) {
  1537	    setRequestStatus(`当前 Packet JSON 无法应用 schema 修复：${String(error.message || error)}`, "error");
  1538	    return;
  1539	  }
  1540	
  1541	  setRequestStatus("正在应用安全 schema 修复...", "neutral");
  1542	  try {
  1543	    const response = await fetch(workbenchRepairPath, {
  1544	      method: "POST",
  1545	      headers: {"Content-Type": "application/json"},
  1546	      body: JSON.stringify({
  1547	        packet_payload: packetPayload,
  1548	        apply_all_safe: true,
  1549	      }),
  1550	    });
  1551	    const payload = await response.json();
  1552	    if (!response.ok) {
  1553	      throw new Error(payload.message || payload.error || "workbench safe repair request failed");
  1554	    }
  1555	    maybeAutoSnapshotCurrentPacketDraft("应用安全 schema 修复");
  1556	    setPacketEditor(payload.packet_payload);
  1557	    setPacketSourceStatus(`当前 packet 已应用 ${payload.applied_suggestion_ids.length} 条安全 schema 修复，并准备重跑。`);
  1558	    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.packet_payload, {
  1559	      title: "Schema 安全修复",
  1560	      summary: `已应用 ${payload.applied_suggestion_ids.length} 条 safe autofix`,
  1561	      detail: payload.applied_suggestion_ids.join(" / "),
  1562	    }));
  1563	    renderSystemFingerprintFromPacketPayload(payload.packet_payload, {
  1564	      badgeState: "idle",
  1565	      badgeText: "画像已更新",
  1566	      summary: "安全 schema 修复已经写回当前 packet；系统现在会基于修复后的 packet 继续重跑 bundle。",
  1567	    });
  1568	    setCurrentWorkbenchRunLabel("Schema 安全修复并重跑");
  1569	    setActiveWorkbenchPreset("");
  1570	    await runWorkbenchBundle();
  1571	  } catch (error) {
  1572	    setRequestStatus(`安全 schema 修复失败：${String(error.message || error)}`, "error");
  1573	  }
  1574	}
  1575	
  1576	async function applyClarificationWorkspace({
  1577	  rerun = false,
  1578	} = {}) {
  1579	  let packetPayload;
  1580	  try {
  1581	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  1582	  } catch (error) {
  1583	    setRequestStatus(`当前 Packet JSON 无法写回 clarification：${String(error.message || error)}`, "error");
  1584	    return;
  1585	  }
  1586	
  1587	  const {packetPayload: nextPayload, answeredCount} = applyClarificationWorkspaceAnswersToPacket(packetPayload);
  1588	  maybeAutoSnapshotCurrentPacketDraft("写回 clarification");
  1589	  setPacketEditor(nextPayload);
  1590	  setPacketSourceStatus(
  1591	    answeredCount
  1592	      ? `当前 packet 已写回 ${answeredCount} 条 clarification answer。`
  1593	      : "当前 packet 已清空这批 clarification answer。"
  1594	  );
  1595	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(nextPayload, {
  1596	    title: "Clarification 写回",
  1597	    summary: answeredCount
  1598	      ? `已写回 ${answeredCount} 条 clarification answer`
  1599	      : "已清空当前 clarification answer",
  1600	  }));
  1601	  renderSystemFingerprintFromPacketPayload(nextPayload, {
  1602	    badgeState: "idle",
  1603	    badgeText: "画像已更新",
  1604	    summary: "clarification 答案已经写回当前 packet；如果系统画像或文档方向没问题，可以直接重跑看 gate 是否放行。",
  1605	  });
  1606	  renderValue(
  1607	    "workbench-clarification-workspace-note",
  1608	    answeredCount
  1609	      ? `已把 ${answeredCount} 条答案写回当前 packet。${rerun ? "系统现在会直接重跑。" : "如需验证是否放行，可以点右侧按钮或主运行按钮重跑。"}`
  1610	      : "已清空当前工作台里的回答并写回 packet；如需验证，请重新运行。",
  1611	  );
  1612	  setRequestStatus(
  1613	    answeredCount
  1614	      ? (rerun ? "clarification 已写回，正在重跑 bundle..." : "clarification 已写回当前 packet。")
  1615	      : "clarification 修改已写回当前 packet。",
  1616	    rerun ? "neutral" : "success",
  1617	  );
  1618	
  1619	  if (rerun) {
  1620	    setCurrentWorkbenchRunLabel("Clarification 回填并重跑");
  1621	    setActiveWorkbenchPreset("");
  1622	    await runWorkbenchBundle();
  1623	  }
  1624	}
  1625	
  1626	function renderSystemFingerprintFromPacketPayload(packetPayload, {
  1627	  badgeState = "idle",
  1628	  badgeText = "画像已载入",
  1629	  summary = "样例已经装载。你现在就能先看这套系统的文档来源和关键信号，不用等 bundle 跑完。",
  1630	} = {}) {
  1631	  const documents = Array.isArray(packetPayload.source_documents) ? packetPayload.source_documents : [];
  1632	  const signals = Array.isArray(packetPayload.components) ? packetPayload.components : [];
  1633	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
  1634	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
  1635	  if (documentKinds.length > 1) {
  1636	    sourceModeParts.push("混合来源");
  1637	  }
  1638	  if (documentKinds.includes("pdf")) {
  1639	    sourceModeParts.push("含 PDF");
  1640	  }
  1641	
  1642	  renderSystemFingerprint({
  1643	    badgeState,
  1644	    badgeText,
  1645	    summary,
  1646	    systemId: packetPayload.system_id || "-",
  1647	    objective: packetPayload.objective || "-",
  1648	    sourceMode: sourceModeParts.join(" / "),
  1649	    sourceTruth: packetPayload.source_of_truth || "等待工程真值说明",
  1650	    documents,
  1651	    signals,
  1652	    documentFallback: "当前 packet 还没有来源文档。",
  1653	    signalFallback: "当前 packet 还没有关键信号定义。",
  1654	  });
  1655	}
  1656	
  1657	function renderOnboardingReadiness({
  1658	  badgeState = "idle",
  1659	  badgeText = "等待生成",
  1660	  summary = "这里会直接告诉你：这份 packet 现在够不够支撑第二套控制逻辑进入 spec build。",
  1661	  docs = "-",
  1662	  docsDetail = "等待生成。",
  1663	  components = "-",
  1664	  componentsDetail = "等待生成。",
  1665	  logic = "-",
  1666	  logicDetail = "等待生成。",
  1667	  scenarios = "-",
  1668	  scenariosDetail = "等待生成。",
  1669	  faults = "-",
  1670	  faultsDetail = "等待生成。",
  1671	  clarifications = "-",
  1672	  clarificationsDetail = "等待生成。",
  1673	  unlocks = "-",
  1674	  gaps = "-",
  1675	} = {}) {
  1676	  setOnboardingBadge(badgeState, badgeText);
  1677	  renderValue("workbench-onboarding-summary", summary);
  1678	  renderValue("workbench-onboarding-docs", docs);
  1679	  renderValue("workbench-onboarding-docs-detail", docsDetail);
  1680	  renderValue("workbench-onboarding-components", components);
  1681	  renderValue("workbench-onboarding-components-detail", componentsDetail);
  1682	  renderValue("workbench-onboarding-logic", logic);
  1683	  renderValue("workbench-onboarding-logic-detail", logicDetail);
  1684	  renderValue("workbench-onboarding-scenarios", scenarios);
  1685	  renderValue("workbench-onboarding-scenarios-detail", scenariosDetail);
  1686	  renderValue("workbench-onboarding-faults", faults);
  1687	  renderValue("workbench-onboarding-faults-detail", faultsDetail);
  1688	  renderValue("workbench-onboarding-clarifications", clarifications);
  1689	  renderValue("workbench-onboarding-clarifications-detail", clarificationsDetail);
  1690	  renderValue("workbench-onboarding-unlocks", unlocks);
  1691	  renderValue("workbench-onboarding-gaps", gaps);
  1692	}
  1693	
  1694	function renderPreparationBoard(message) {
  1695	  setWorkbenchViewState("preparation");
  1696	  setVisualBadge("idle", "样例已就位");
  1697	  renderOnboardingReadiness({
  1698	    badgeState: "idle",
  1699	    badgeText: "样例待运行",
  1700	    summary: "样例已经装载，但还没有真正做 intake 检查；运行后这里才会告诉你第二套系统接入是否 ready。",
  1701	    gaps: "等待 intake",
  1702	  });
  1703	  renderValue("workbench-spotlight-verdict", "等待生成");
  1704	  renderValue("workbench-spotlight-verdict-detail", message);
  1705	  renderValue("workbench-spotlight-blocker", "尚未运行");
  1706	  renderValue("workbench-spotlight-blocker-detail", "点击“生成 Bundle”后，系统会告诉你卡在哪一步。");
  1707	  renderValue("workbench-spotlight-knowledge", "尚未形成");
  1708	  renderValue("workbench-spotlight-knowledge-detail", "还没有 diagnosis / knowledge 结果。");
  1709	  renderValue("workbench-spotlight-archive", "尚未归档");
  1710	  renderValue("workbench-spotlight-archive-detail", "如果勾选 archive，运行后这里会显示落档状态。");
  1711	  renderOnboardingActions({
  1712	    badgeState: "idle",
  1713	    badgeText: "等待动作生成",
  1714	    summary: "样例已经装载，但动作板还没真正跑 intake / clarification，所以先不猜下一步。",
  1715	  });
  1716	  renderSchemaRepairWorkspace({
  1717	    badgeState: "idle",
  1718	    badgeText: "等待修复项",
  1719	    summary: "样例虽然已经装载，但还没真正跑出 schema blocker，所以这里先不提前猜哪些结构问题能安全 autofix。",
  1720	    fallbackTitle: "等待第一次运行",
  1721	    fallbackText: "先跑一次 bundle；如果后端给出 repair suggestion，这里才会显示安全 schema 修复入口。",
  1722	    note: "当前只是样例准备阶段，还没有可应用的 schema repair。",
  1723	    actionsDisabled: true,
  1724	  });
  1725	  renderClarificationWorkspace({
  1726	    badgeState: "idle",
  1727	    badgeText: "等待回填项",
  1728	    summary: "样例虽然已经装载，但还没真正跑到 clarification gate，所以这里先不提前猜哪些问题要你回答。",
  1729	    fallbackTitle: "等待第一次运行",
  1730	    fallbackText: "先跑一次 bundle；如果它停在 clarification gate，这里就会出现可直接填写的答案卡。",
  1731	    note: "当前只是样例准备阶段，还没有需要写回的 clarification。",
  1732	    actionsDisabled: true,
  1733	  });
  1734	  renderValue(
  1735	    "workbench-visual-summary",
  1736	    "当前只是在准备样例。真正的验收结果会在你点击“生成 Bundle”之后出现在这里。",
  1737	  );
  1738	  setStageState("intake", "pending", "样例已装载，等待运行。");
  1739	  setStageState("clarification", "idle", "等待生成。");
  1740	  setStageState("playback", "idle", "等待生成。");
  1741	  setStageState("diagnosis", "idle", "等待生成。");
  1742	  setStageState("knowledge", "idle", "等待生成。");
  1743	  setStageState("archive", "idle", "等待生成。");
  1744	  renderWorkbenchHistoryViewBar();
  1745	  renderWorkbenchPacketHistoryViewBar();
  1746	}
  1747	
  1748	function pushWorkbenchRunHistory(entry) {
  1749	  setWorkbenchViewState("latest", entry.id);
  1750	  workbenchRunHistory = [entry, ...workbenchRunHistory].slice(0, maxWorkbenchRunHistory);
  1751	  renderWorkbenchRunHistory();
  1752	  persistWorkbenchPacketWorkspace();
  1753	}
  1754	
  1755	function renderWorkbenchPacketHistoryViewBar() {
  1756	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  1757	  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;
  1758	  const statusElement = workbenchElement("workbench-packet-history-status");
  1759	  const returnButton = workbenchElement("workbench-packet-history-return-latest");
  1760	
  1761	  if (!latestEntry) {
  1762	    statusElement.textContent = "当前 Packet：等待第一次载入";
  1763	    returnButton.disabled = true;
  1764	    renderWorkbenchPacketDraftState();
  1765	    renderWorkbenchPacketRevisionCompareBar();
  1766	    return;
  1767	  }
  1768	
  1769	  if (!selectedEntry || selectedEntry.id === latestEntry.id) {
  1770	    statusElement.textContent = `当前 Packet：最新版本 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
  1771	    returnButton.disabled = true;
  1772	    renderWorkbenchPacketDraftState();
  1773	    renderWorkbenchPacketRevisionCompareBar();
  1774	    return;
  1775	  }
  1776	
  1777	  statusElement.textContent = `当前 Packet：历史版本 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  1778	  returnButton.disabled = false;
  1779	  renderWorkbenchPacketDraftState();
  1780	  renderWorkbenchPacketRevisionCompareBar();
  1781	}
  1782	
  1783	function setPacketDraftActionState(disabled) {
  1784	  workbenchElement("workbench-save-packet-draft").disabled = disabled;
  1785	}
  1786	
  1787	function renderWorkbenchPacketDraftState() {
  1788	  const statusElement = workbenchElement("workbench-packet-draft-status");
  1789	  const noteElement = workbenchElement("workbench-packet-draft-note");
  1790	  const baselineEntry = selectedWorkbenchPacketRevisionEntry();
  1791	
  1792	  if (!baselineEntry) {
  1793	    const parsed = parseWorkbenchPacketEditor();
  1794	    if (parsed.error) {
  1795	      statusElement.textContent = "当前草稿：JSON 待修正";
  1796	      noteElement.textContent = `当前输入区已经恢复了草稿文本，但它还不是合法 JSON：${parsed.error}`;
  1797	      setPacketDraftActionState(true);
  1798	      return;
  1799	    }
  1800	    if (parsed.payload) {
  1801	      statusElement.textContent = "当前草稿：尚未建立版本基线";
  1802	      noteElement.textContent = "当前输入区已经有 packet，但还没进入已保存版本历史；你可以先把它保存成草稿，再继续切换样例或重跑。";
  1803	      setPacketDraftActionState(false);
  1804	      return;
  1805	    }
  1806	    statusElement.textContent = "当前草稿：等待第一次载入";
  1807	    noteElement.textContent = "先载入一个 packet；之后直接改 JSON 但还没运行时，也可以先把当前版本存成草稿。";
  1808	    setPacketDraftActionState(true);
  1809	    return;
  1810	  }
  1811	
  1812	  const parsed = parseWorkbenchPacketEditor();
  1813	  if (parsed.error) {
  1814	    statusElement.textContent = "当前草稿：JSON 暂不可保存";
  1815	    noteElement.textContent = `当前输入区还不是合法 JSON，所以版本历史暂时无法收纳它：${parsed.error}`;
  1816	    setPacketDraftActionState(true);
  1817	    return;
  1818	  }
  1819	
  1820	  if (baselineEntry.signature === packetRevisionSignature(parsed.payload)) {
  1821	    statusElement.textContent = `当前草稿：已与「${baselineEntry.title}」同步`;
  1822	    noteElement.textContent = "如果接下来切换样例、恢复旧版本或应用浏览器写回，系统会先检查是否存在新的有效草稿。";
  1823	    setPacketDraftActionState(true);
  1824	    return;
  1825	  }
  1826	
  1827	  statusElement.textContent = `当前草稿：有未保存改动（相对「${baselineEntry.title}」）`;
  1828	  noteElement.textContent = "你可以先手动保存这份 Packet 草稿；如果现在切换样例、恢复旧版本或应用浏览器写回，系统也会先自动保存这份有效草稿，刷新页面后也会继续恢复当前工作区。";
  1829	  setPacketDraftActionState(false);
  1830	}
  1831	
  1832	function restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  1833	  sourceStatusMessage = "已从浏览器恢复上次 packet 工作区。",
  1834	  sourceStatusMessageWithHistory = "已从浏览器恢复上次 packet 工作区和结果历史。",
  1835	  packetSourceFallback = "当前样例：已恢复工作区快照。",
  1836	  preparationMessage = "已恢复工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  1837	  fingerprintSummary = "已恢复工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  1838	  successMessage = "已恢复工作区快照。",
  1839	} = {}) {
  1840	  if (!workspace || typeof workspace !== "object") {
  1841	    return false;
  1842	  }
  1843	
  1844	  const normalizedHistory = normalizeWorkbenchPacketRevisionHistory(workspace.packetRevisionHistory);
  1845	  const normalizedRunHistory = normalizeWorkbenchRunHistory(workspace.runHistory);
  1846	  const fallbackPacketJsonText = normalizedHistory.length
  1847	    ? prettyJson(normalizedHistory[0].payload)
  1848	    : prettyJson(bootstrapPayload.reference_packet);
  1849	  const packetJsonText = typeof workspace.packetJsonText === "string" && workspace.packetJsonText.trim()
  1850	    ? workspace.packetJsonText
  1851	    : fallbackPacketJsonText;
  1852	
  1853	  withWorkbenchPacketWorkspacePersistenceSuspended(() => {
  1854	    workbenchPacketRevisionHistory = normalizedHistory;
  1855	    workbenchPacketRevisionSequence = nextWorkbenchSequenceFromIds(
  1856	      normalizedHistory,
  1857	      "workbench-packet-revision-",
  1858	    );
  1859	    workbenchRunHistory = normalizedRunHistory;
  1860	    workbenchHistorySequence = nextWorkbenchSequenceFromIds(
  1861	      normalizedRunHistory,
  1862	      "workbench-history-",
  1863	    );
  1864	    selectedWorkbenchPacketRevisionId = normalizedHistory.some((entry) => entry.id === workspace.selectedWorkbenchPacketRevisionId)
  1865	      ? workspace.selectedWorkbenchPacketRevisionId
  1866	      : (normalizedHistory[0] ? normalizedHistory[0].id : "");
  1867	    selectedWorkbenchHistoryId = normalizedRunHistory.some((entry) => entry.id === workspace.selectedWorkbenchHistoryId)
  1868	      ? workspace.selectedWorkbenchHistoryId
  1869	      : (normalizedRunHistory[0] ? normalizedRunHistory[0].id : "");
  1870	    currentWorkbenchViewMode = typeof workspace.currentWorkbenchViewMode === "string" && workspace.currentWorkbenchViewMode
  1871	      ? workspace.currentWorkbenchViewMode
  1872	      : (normalizedRunHistory.length ? "latest" : "preparation");
  1873	    currentWorkbenchRunLabel = typeof workspace.currentWorkbenchRunLabel === "string" && workspace.currentWorkbenchRunLabel.trim()
  1874	      ? workspace.currentWorkbenchRunLabel
  1875	      : "手动生成";
  1876	    workbenchElement("workbench-packet-json").value = packetJsonText;
  1877	    setPacketSourceStatus(
  1878	      typeof workspace.packetSourceStatus === "string" && workspace.packetSourceStatus.trim()
  1879	        ? workspace.packetSourceStatus
  1880	        : packetSourceFallback
  1881	    );
  1882	    const fields = workspace.fields && typeof workspace.fields === "object" ? workspace.fields : {};
  1883	    workbenchPersistedFieldIds.forEach((id) => {
  1884	      applyWorkbenchPersistedFieldValue(id, fields[id]);
  1885	    });
  1886	    renderWorkbenchPacketRevisionHistory();
  1887	  });
  1888	
  1889	  const parsed = parseWorkbenchPacketEditor();
  1890	  if (parsed.payload) {
  1891	    renderSystemFingerprintFromPacketPayload(parsed.payload, {
  1892	      badgeState: "idle",
  1893	      badgeText: "画像已恢复",
  1894	      summary: fingerprintSummary,
  1895	    });
  1896	  } else {
  1897	    renderSystemFingerprint({
  1898	      badgeState: "blocked",
  1899	      badgeText: "画像待修正",
  1900	      summary: `${successMessage} 但当前 JSON 还没恢复成合法 packet：${parsed.error}`,
  1901	      documentFallback: "先修正 JSON，再显示来源文档。",
  1902	      signalFallback: "先修正 JSON，再显示关键信号。",
  1903	    });
  1904	  }
  1905	  if (!normalizedRunHistory.length) {
  1906	    renderPreparationBoard(preparationMessage);
  1907	  } else if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
  1908	    restoreWorkbenchHistoryEntry(selectedWorkbenchHistoryId);
  1909	  } else {
  1910	    restoreLatestWorkbenchHistory();
  1911	  }
  1912	  setActiveWorkbenchPreset("");
  1913	  persistWorkbenchPacketWorkspace();
  1914	  setRequestStatus(
  1915	    normalizedRunHistory.length
  1916	      ? sourceStatusMessageWithHistory
  1917	      : sourceStatusMessage,
  1918	    "success",
  1919	  );
  1920	  return true;
  1921	}
  1922	
  1923	function restoreWorkbenchPacketWorkspaceFromBrowser() {
  1924	  const workspace = loadPersistedWorkbenchPacketWorkspace();
  1925	  if (!workspace) {
  1926	    return false;
  1927	  }
  1928	  return restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  1929	    sourceStatusMessage: "已从浏览器恢复上次 packet 工作区。",
  1930	    sourceStatusMessageWithHistory: "已从浏览器恢复上次 packet 工作区和结果历史。",
  1931	    packetSourceFallback: "当前样例：已从浏览器恢复上次 packet 工作区。",
  1932	    preparationMessage: "已从浏览器恢复上次 packet 工作区；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  1933	    fingerprintSummary: "已从浏览器恢复上次 packet 工作区。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  1934	    successMessage: "已从浏览器恢复上次 packet 工作区。",
  1935	  });
  1936	}
  1937	
  1938	function summarizeWorkbenchPacketRevisionEntry(entry) {
  1939	  if (!entry) {
  1940	    return null;
  1941	  }
  1942	  const summary = summarizePacketPayload(entry.payload);
  1943	  return {
  1944	    systemId: entry.payload.system_id || "unknown_system",
  1945	    docs: `${summary.sourceDocuments} 份`,
  1946	    logic: `${summary.logicNodes} logic / ${summary.components} components`,
  1947	    scenarios: `${summary.scenarios} scenarios / ${summary.faultModes} faults`,
  1948	    answers: `${summary.clarificationAnswers} answers`,
  1949	  };
  1950	}
  1951	
  1952	function renderWorkbenchPacketRevisionCompareBar() {
  1953	  const compareBar = workbenchElement("workbench-packet-history-compare-bar");
  1954	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  1955	  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;
  1956	
  1957	  if (!latestEntry || !selectedEntry || selectedEntry.id === latestEntry.id) {
  1958	    compareBar.hidden = true;
  1959	    return;
  1960	  }
  1961	
  1962	  const replay = summarizeWorkbenchPacketRevisionEntry(selectedEntry);
  1963	  const latest = summarizeWorkbenchPacketRevisionEntry(latestEntry);
  1964	
  1965	  workbenchElement("workbench-packet-history-compare-summary").textContent =
  1966	    `你正在回看「${selectedEntry.title}」，下面这些卡会直接告诉你它和最新 packet 在输入骨架上差在哪里。`;
  1967	  renderValue("workbench-packet-history-compare-system", `回看：${replay.systemId}`);
  1968	  renderValue("workbench-packet-history-compare-system-detail", `最新：${latest.systemId}`);
  1969	  renderValue("workbench-packet-history-compare-docs", `回看：${replay.docs}`);
  1970	  renderValue("workbench-packet-history-compare-docs-detail", `最新：${latest.docs}`);
  1971	  renderValue("workbench-packet-history-compare-logic", `回看：${replay.logic}`);
  1972	  renderValue("workbench-packet-history-compare-logic-detail", `最新：${latest.logic}`);
  1973	  renderValue("workbench-packet-history-compare-scenarios", `回看：${replay.scenarios}`);
  1974	  renderValue("workbench-packet-history-compare-scenarios-detail", `最新：${latest.scenarios}`);
  1975	  renderValue("workbench-packet-history-compare-answers", `回看：${replay.answers}`);
  1976	  renderValue("workbench-packet-history-compare-answers-detail", `最新：${latest.answers}`);
  1977	  compareBar.hidden = false;
  1978	}
  1979	
  1980	function renderWorkbenchPacketRevisionHistory() {
  1981	  const container = workbenchElement("workbench-packet-history-cards");
  1982	  if (!workbenchPacketRevisionHistory.length) {
  1983	    container.replaceChildren((() => {
  1984	      const card = document.createElement("article");
  1985	      card.className = "workbench-history-card is-empty";
  1986	      const title = document.createElement("strong");
  1987	      title.textContent = "暂无版本";
  1988	      const detail = document.createElement("p");
  1989	      detail.textContent = "先载入 reference/template、本地 JSON，或在页面里写回一次 packet。";
  1990	      card.append(title, detail);
  1991	      return card;
  1992	    })());
  1993	    renderWorkbenchPacketHistoryViewBar();
  1994	    return;
  1995	  }
  1996	
  1997	  container.replaceChildren(...workbenchPacketRevisionHistory.map((entry) => {
  1998	    const card = document.createElement("button");
  1999	    const selected = entry.id === selectedWorkbenchPacketRevisionId;
  2000	    const summary = summarizePacketPayload(entry.payload);

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '2501,3000p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '2001,2500p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2501	      card.append(title, detail);
  2502	      return card;
  2503	    })());
  2504	    renderWorkbenchHistoryViewBar();
  2505	    return;
  2506	  }
  2507	
  2508	  container.replaceChildren(...workbenchRunHistory.map((entry) => {
  2509	    const card = document.createElement("button");
  2510	    const selected = entry.id === selectedWorkbenchHistoryId;
  2511	    card.type = "button";
  2512	    card.className = "workbench-history-card";
  2513	    card.dataset.selected = selected ? "true" : "false";
  2514	    card.setAttribute("aria-pressed", selected ? "true" : "false");
  2515	    card.addEventListener("click", () => {
  2516	      restoreWorkbenchHistoryEntry(entry.id);
  2517	    });
  2518	
  2519	    const meta = document.createElement("div");
  2520	    meta.className = "workbench-history-meta";
  2521	
  2522	    const stateChip = document.createElement("span");
  2523	    stateChip.className = "workbench-history-chip";
  2524	    stateChip.dataset.state = entry.state;
  2525	    stateChip.textContent = entry.stateLabel;
  2526	
  2527	    const archiveChip = document.createElement("span");
  2528	    archiveChip.className = "workbench-history-chip";
  2529	    archiveChip.dataset.state = entry.archived ? "archived" : entry.state;
  2530	    archiveChip.textContent = entry.archived ? "已留档" : "未留档";
  2531	
  2532	    const timeChip = document.createElement("span");
  2533	    timeChip.className = "workbench-history-chip";
  2534	    timeChip.textContent = entry.timeLabel;
  2535	
  2536	    meta.append(stateChip, archiveChip, timeChip);
  2537	
  2538	    const title = document.createElement("strong");
  2539	    title.textContent = entry.title;
  2540	
  2541	    const summary = document.createElement("p");
  2542	    summary.textContent = entry.summary;
  2543	
  2544	    const detail = document.createElement("p");
  2545	    detail.textContent = entry.detail;
  2546	
  2547	    const action = document.createElement("span");
  2548	    action.className = "workbench-history-action";
  2549	    action.textContent = selected ? "当前主看板正在显示这次结果" : "点此回看这次结果";
  2550	
  2551	    card.append(meta, title, summary, detail, action);
  2552	    return card;
  2553	  }));
  2554	  renderWorkbenchHistoryViewBar();
  2555	}
  2556	
  2557	function historyTimeLabel() {
  2558	  return new Date().toLocaleTimeString("zh-CN", {
  2559	    hour: "2-digit",
  2560	    minute: "2-digit",
  2561	    second: "2-digit",
  2562	    hour12: false,
  2563	  });
  2564	}
  2565	
  2566	function buildWorkbenchHistoryEntryFromPayload(payload) {
  2567	  const bundle = payload.bundle || {};
  2568	  const clarification = bundle.clarification_brief || {};
  2569	  const archive = payload.archive || null;
  2570	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  2571	    ? bundle.intake_assessment.blocking_reasons
  2572	    : [];
  2573	  const ready = Boolean(bundle.ready_for_spec_build);
  2574	  return {
  2575	    id: nextWorkbenchHistoryId(),
  2576	    state: ready ? "ready" : "blocked",
  2577	    stateLabel: ready ? "通过" : "阻塞",
  2578	    archived: Boolean(archive),
  2579	    timeLabel: historyTimeLabel(),
  2580	    title: currentWorkbenchRunLabel,
  2581	    payload: cloneJson(payload),
  2582	    summary: ready
  2583	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
  2584	      : `停在 ${clarification.gate_status || "clarification"}，等待补齐信息`,
  2585	    detail: ready
  2586	      ? (archive ? `archive：${shortPath(archive.archive_dir)}` : "本次未生成 archive。")
  2587	      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 尚未 ready。"),
  2588	  };
  2589	}
  2590	
  2591	function buildWorkbenchHistoryEntryFromFailure(message) {
  2592	  return {
  2593	    id: nextWorkbenchHistoryId(),
  2594	    state: "failure",
  2595	    stateLabel: "失败",
  2596	    archived: false,
  2597	    timeLabel: historyTimeLabel(),
  2598	    title: currentWorkbenchRunLabel,
  2599	    errorMessage: String(message),
  2600	    summary: "请求未完成",
  2601	    detail: message,
  2602	  };
  2603	}
  2604	
  2605	function workbenchHistoryTone(state) {
  2606	  if (state === "ready") {
  2607	    return "success";
  2608	  }
  2609	  if (state === "blocked") {
  2610	    return "warning";
  2611	  }
  2612	  return "error";
  2613	}
  2614	
  2615	function renderFailureResponse(message, {
  2616	  pushHistory = true,
  2617	  sourceMode = "当前来源：workbench bundle 请求失败。",
  2618	  requestStatusMessage = `生成失败：${String(message)}`,
  2619	  requestStatusTone = "error",
  2620	} = {}) {
  2621	  const normalizedMessage = String(message);
  2622	  setResultMode(sourceMode);
  2623	  workbenchElement("bundle-json-output").textContent = prettyJson({
  2624	    error: "workbench_bundle_failed",
  2625	    message: normalizedMessage,
  2626	  });
  2627	  renderExplainRuntime({});
  2628	  renderFailureBoard(normalizedMessage);
  2629	  if (pushHistory) {
  2630	    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromFailure(normalizedMessage));
  2631	  }
  2632	  setRequestStatus(requestStatusMessage, requestStatusTone);
  2633	}
  2634	
  2635	function restoreWorkbenchHistoryEntry(entryId) {
  2636	  const entry = workbenchRunHistory.find((item) => item.id === entryId);
  2637	  if (!entry) {
  2638	    return;
  2639	  }
  2640	  setWorkbenchViewState("history", entry.id);
  2641	  renderWorkbenchRunHistory();
  2642	  setActiveWorkbenchPreset("");
  2643	  if (entry.payload) {
  2644	    renderBundleResponse(entry.payload, {
  2645	      pushHistory: false,
  2646	      sourceMode: "当前来源：最近验收结果回看。",
  2647	      requestStatusMessage: `已回看：${entry.title}`,
  2648	      requestStatusTone: workbenchHistoryTone(entry.state),
  2649	    });
  2650	    return;
  2651	  }
  2652	  renderFailureResponse(entry.errorMessage || entry.detail, {
  2653	    pushHistory: false,
  2654	    sourceMode: "当前来源：最近验收结果回看。",
  2655	    requestStatusMessage: `已回看：${entry.title}`,
  2656	    requestStatusTone: workbenchHistoryTone(entry.state),
  2657	  });
  2658	}
  2659	
  2660	function restoreLatestWorkbenchHistory() {
  2661	  const latestEntry = latestWorkbenchHistoryEntry();
  2662	  if (!latestEntry) {
  2663	    return;
  2664	  }
  2665	  setWorkbenchViewState("latest", latestEntry.id);
  2666	  renderWorkbenchRunHistory();
  2667	  setActiveWorkbenchPreset("");
  2668	  if (latestEntry.payload) {
  2669	    renderBundleResponse(latestEntry.payload, {
  2670	      pushHistory: false,
  2671	      sourceMode: "当前来源：最新结果回看。",
  2672	      requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
  2673	      requestStatusTone: workbenchHistoryTone(latestEntry.state),
  2674	    });
  2675	    return;
  2676	  }
  2677	  renderFailureResponse(latestEntry.errorMessage || latestEntry.detail, {
  2678	    pushHistory: false,
  2679	    sourceMode: "当前来源：最新结果回看。",
  2680	    requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
  2681	    requestStatusTone: workbenchHistoryTone(latestEntry.state),
  2682	  });
  2683	}
  2684	
  2685	function renderRunningBoard(message) {
  2686	  setWorkbenchViewState("running");
  2687	  setVisualBadge("idle", "正在生成");
  2688	  renderOnboardingReadiness({
  2689	    badgeState: "idle",
  2690	    badgeText: "正在评估",
  2691	    summary: "系统正在检查这份 packet 能不能作为第二套控制逻辑的可靠起点。",
  2692	    gaps: "评估中",
  2693	  });
  2694	  renderValue("workbench-spotlight-verdict", "正在处理中");
  2695	  renderValue("workbench-spotlight-verdict-detail", message);
  2696	  renderValue("workbench-spotlight-blocker", "正在判定");
  2697	  renderValue("workbench-spotlight-blocker-detail", "系统正在检查当前 packet 是通过还是阻塞。");
  2698	  renderValue("workbench-spotlight-knowledge", "处理中");
  2699	  renderValue("workbench-spotlight-knowledge-detail", "如果 bundle ready，knowledge 结果会在本轮生成。");
  2700	  renderValue("workbench-spotlight-archive", "处理中");
  2701	  renderValue("workbench-spotlight-archive-detail", "如果本轮勾选 archive，系统会在生成后汇报落档结果。");
  2702	  renderOnboardingActions({
  2703	    badgeState: "idle",
  2704	    badgeText: "动作解析中",
  2705	    summary: "系统正在按真实 clarification / schema 结果生成动作板，不会在前端自己猜步骤。",
  2706	  });
  2707	  renderSchemaRepairWorkspace({
  2708	    badgeState: "idle",
  2709	    badgeText: "修复解析中",
  2710	    summary: "系统正在检查这次 blocked bundle 里有没有被后端判定为 safe autofix 的 schema 修复项。",
  2711	    fallbackTitle: "正在解析",
  2712	    fallbackText: "请稍等，系统正在决定这次 run 有没有可直接应用的安全 schema 修复。",
  2713	    note: "工作台只会接受后端明确给出的 repair suggestion。",
  2714	    actionsDisabled: true,
  2715	  });
  2716	  renderClarificationWorkspace({
  2717	    badgeState: "idle",
  2718	    badgeText: "回填解析中",
  2719	    summary: "系统正在读取真实 clarification gate 结果；只有后端确认的待答问题才会被放进这个回填工作台。",
  2720	    fallbackTitle: "正在解析",
  2721	    fallbackText: "请稍等，系统正在决定这次 run 有没有需要直接回填的 clarification。",
  2722	    note: "当前不会在前端凭空生成问题，只复用 bundle 真实返回的 follow_up_items。",
  2723	    actionsDisabled: true,
  2724	  });
  2725	  renderValue("workbench-visual-summary", "系统正在跑当前 bundle。以最后一次点击为准，旧响应不会覆盖新结果。");
  2726	  setStageState("intake", "pending", "正在读取当前 packet。");
  2727	  setStageState("clarification", "pending", "正在检查 clarification gate。");
  2728	  setStageState("playback", "idle", "等待前序结果。");
  2729	  setStageState("diagnosis", "idle", "等待前序结果。");
  2730	  setStageState("knowledge", "idle", "等待前序结果。");
  2731	  setStageState("archive", "idle", "等待前序结果。");
  2732	  renderWorkbenchHistoryViewBar();
  2733	}
  2734	
  2735	function renderFailureBoard(message) {
  2736	  setVisualBadge("blocked", "请求失败");
  2737	  renderOnboardingReadiness({
  2738	    badgeState: "blocked",
  2739	    badgeText: "请求失败",
  2740	    summary: "这次不是 packet 本身通过或阻塞，而是请求失败了，所以还不能判断第二套系统接入准备度。",
  2741	    gaps: "先修正请求",
  2742	  });
  2743	  renderValue("workbench-spotlight-verdict", "需要修正输入");
  2744	  renderValue("workbench-spotlight-verdict-detail", message);
  2745	  renderValue("workbench-spotlight-blocker", "请求未完成");
  2746	  renderValue("workbench-spotlight-blocker-detail", "先修正输入或请求错误，再重新运行。");
  2747	  renderValue("workbench-spotlight-knowledge", "未生成");
  2748	  renderValue("workbench-spotlight-knowledge-detail", "因为请求失败，所以没有下游结果。");
  2749	  renderValue("workbench-spotlight-archive", "未生成");
  2750	  renderValue("workbench-spotlight-archive-detail", "本次没有产生 archive package。");
  2751	  renderOnboardingActions({
  2752	    badgeState: "blocked",
  2753	    badgeText: "动作未生成",
  2754	    summary: `这次不是 clarification 阻塞，而是请求本身失败了，所以动作板也还不能可靠生成：${message}`,
  2755	    followUpFallback: "先修正请求，再显示澄清动作。",
  2756	    blockerFallback: "先修正请求，再显示结构 blocker。",
  2757	    unlockFallback: "先修正请求，再显示解锁项。",
  2758	  });
  2759	  renderSchemaRepairWorkspace({
  2760	    badgeState: "blocked",
  2761	    badgeText: "暂不可修复",
  2762	    summary: "这次请求没有成功，所以还不能可靠判断哪些 schema blocker 适合安全 autofix。",
  2763	    fallbackTitle: "先修正请求",
  2764	    fallbackText: "等请求恢复成功后，这里才会出现真实 schema repair suggestion。",
  2765	    note: "当前错误优先级高于 schema repair；先把请求恢复正常。",
  2766	    actionsDisabled: true,
  2767	  });
  2768	  renderClarificationWorkspace({
  2769	    badgeState: "blocked",
  2770	    badgeText: "暂不可回填",
  2771	    summary: "这次请求没有成功，所以工作台现在也不能可靠判断应该让你回答哪些 clarification。",
  2772	    fallbackTitle: "先修正请求",
  2773	    fallbackText: "等请求恢复成功后，这里才会出现真实的 clarification 回填项。",
  2774	    note: "当前错误优先级高于 clarification 回填；先把 JSON 或请求本身修好。",
  2775	    actionsDisabled: true,
  2776	  });
  2777	  renderValue("workbench-visual-summary", "这次不是 bundle 阻塞，而是请求本身没有成功。先修正输入，再重新点击“生成 Bundle”。");
  2778	  setStageState("intake", "blocked", "输入或请求存在问题。");
  2779	  setStageState("clarification", "idle", "等待请求恢复。");
  2780	  setStageState("playback", "idle", "等待请求恢复。");
  2781	  setStageState("diagnosis", "idle", "等待请求恢复。");
  2782	  setStageState("knowledge", "idle", "等待请求恢复。");
  2783	  setStageState("archive", "idle", "等待请求恢复。");
  2784	}
  2785	
  2786	function applyReferencePacketSelection({
  2787	  archiveBundle,
  2788	  sourceStatus,
  2789	  preparationMessage,
  2790	}) {
  2791	  if (!bootstrapPayload) {
  2792	    return false;
  2793	  }
  2794	  maybeAutoSnapshotCurrentPacketDraft("载入参考样例");
  2795	  setPacketEditor(bootstrapPayload.reference_packet);
  2796	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.reference_packet, {
  2797	    title: "载入参考样例",
  2798	    summary: "reference packet 已重新载入。",
  2799	  }));
  2800	  fillReferenceResolutionDefaults();
  2801	  workbenchElement("workbench-scenario-id").value = "";
  2802	  workbenchElement("workbench-fault-mode-id").value = "";
  2803	  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  2804	  setPacketSourceStatus(sourceStatus);
  2805	  renderPreparationBoard(preparationMessage);
  2806	  renderSystemFingerprintFromPacketPayload(bootstrapPayload.reference_packet, {
  2807	    badgeState: "idle",
  2808	    badgeText: "画像已载入",
  2809	    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  2810	  });
  2811	  return true;
  2812	}
  2813	
  2814	function applyTemplatePacketSelection({
  2815	  archiveBundle,
  2816	  sourceStatus,
  2817	  preparationMessage,
  2818	}) {
  2819	  if (!bootstrapPayload) {
  2820	    return false;
  2821	  }
  2822	  maybeAutoSnapshotCurrentPacketDraft("载入空白模板");
  2823	  setPacketEditor(bootstrapPayload.template_packet);
  2824	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.template_packet, {
  2825	    title: "载入空白模板",
  2826	    summary: "template packet 已载入，适合演示 blocked onboarding。",
  2827	  }));
  2828	  clearResolutionDefaults();
  2829	  workbenchElement("workbench-scenario-id").value = "";
  2830	  workbenchElement("workbench-fault-mode-id").value = "";
  2831	  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  2832	  setPacketSourceStatus(sourceStatus);
  2833	  renderPreparationBoard(preparationMessage);
  2834	  renderSystemFingerprintFromPacketPayload(bootstrapPayload.template_packet, {
  2835	    badgeState: "blocked",
  2836	    badgeText: "画像待补齐",
  2837	    summary: "空白模板已经装载。虽然它还没 ready，但你已经可以先确认它的文档方向、控制目标和关键信号占位是不是对的。",
  2838	  });
  2839	  return true;
  2840	}
  2841	
  2842	function runWorkbenchPreset(presetId) {
  2843	  const preset = workbenchPresets[presetId];
  2844	  if (!preset) {
  2845	    return;
  2846	  }
  2847	  if (!bootstrapPayload) {
  2848	    setRequestStatus("bootstrap 尚未加载完成，请稍后再点预设。", "warning");
  2849	    return;
  2850	  }
  2851	  const applied = preset.source === "template"
  2852	    ? applyTemplatePacketSelection(preset)
  2853	    : applyReferencePacketSelection(preset);
  2854	  if (!applied) {
  2855	    setRequestStatus("当前样例还没准备好，请稍后再试。", "warning");
  2856	    return;
  2857	  }
  2858	  setActiveWorkbenchPreset(presetId);
  2859	  setRequestStatus(`${preset.label}：正在自动生成结果...`, "neutral");
  2860	  void runWorkbenchBundle();
  2861	}
  2862	
  2863	function fillReferenceResolutionDefaults() {
  2864	  workbenchElement("workbench-root-cause").value = defaultReferenceResolution.rootCause;
  2865	  workbenchElement("workbench-repair-action").value = defaultReferenceResolution.repairAction;
  2866	  workbenchElement("workbench-validation-after-fix").value = defaultReferenceResolution.validationAfterFix;
  2867	  workbenchElement("workbench-residual-risk").value = defaultReferenceResolution.residualRisk;
  2868	  workbenchElement("workbench-logic-change").value = defaultReferenceResolution.logicChange;
  2869	  workbenchElement("workbench-reliability-gain").value = defaultReferenceResolution.reliabilityGain;
  2870	  workbenchElement("workbench-guardrail-note").value = defaultReferenceResolution.guardrailNote;
  2871	  workbenchElement("workbench-evidence-links").value = "";
  2872	  workbenchElement("workbench-observed-symptoms").value = "";
  2873	}
  2874	
  2875	function clearResolutionDefaults() {
  2876	  [
  2877	    "workbench-root-cause",
  2878	    "workbench-repair-action",
  2879	    "workbench-validation-after-fix",
  2880	    "workbench-residual-risk",
  2881	    "workbench-logic-change",
  2882	    "workbench-reliability-gain",
  2883	    "workbench-guardrail-note",
  2884	    "workbench-evidence-links",
  2885	    "workbench-observed-symptoms",
  2886	  ].forEach((id) => {
  2887	    workbenchElement(id).value = "";
  2888	  });
  2889	}
  2890	
  2891	function renderBulletList(containerId, items, fallbackText) {
  2892	  const container = workbenchElement(containerId);
  2893	  const effectiveItems = Array.isArray(items) && items.length ? items : [fallbackText];
  2894	  container.replaceChildren(
  2895	    ...effectiveItems.map((item) => {
  2896	      const li = document.createElement("li");
  2897	      li.textContent = String(item);
  2898	      return li;
  2899	    }),
  2900	  );
  2901	}
  2902	
  2903	function readExplainRuntimePayload(payload) {
  2904	  const runtime = payload
  2905	    && typeof payload === "object"
  2906	    && payload.explain_runtime
  2907	    && typeof payload.explain_runtime === "object"
  2908	    && !Array.isArray(payload.explain_runtime)
  2909	    ? payload.explain_runtime
  2910	    : null;
  2911	  if (!runtime) {
  2912	    return {
  2913	      reported: false,
  2914	      status: "",
  2915	      statusSource: "",
  2916	      backend: "",
  2917	      model: "",
  2918	      source: "",
  2919	      cachedAt: "",
  2920	      observedAt: "",
  2921	      cacheHits: null,
  2922	      expectedCount: null,
  2923	      backendMatch: null,
  2924	      requestedBackend: "",
  2925	      requestedModel: "",
  2926	      detail: "",
  2927	      boundaryNote: "",
  2928	    };
  2929	  }
  2930	  const toTrimmedString = (value) => (typeof value === "string" ? value.trim() : "");
  2931	  const toNonNegativeInt = (value) => {
  2932	    const parsed = Number(value);
  2933	    return Number.isFinite(parsed) && parsed >= 0 ? Math.floor(parsed) : null;
  2934	  };
  2935	  return {
  2936	    reported: true,
  2937	    status: toTrimmedString(runtime.status),
  2938	    statusSource: toTrimmedString(runtime.status_source),
  2939	    backend: toTrimmedString(runtime.llm_backend),
  2940	    model: toTrimmedString(runtime.llm_model),
  2941	    source: toTrimmedString(runtime.response_source || runtime.last_response_source),
  2942	    cachedAt: toTrimmedString(runtime.cached_at),
  2943	    observedAt: toTrimmedString(runtime.observed_at_utc),
  2944	    cacheHits: toNonNegativeInt(runtime.verified_cache_hits ?? runtime.cache_hits),
  2945	    expectedCount: toNonNegativeInt(runtime.expected_count),
  2946	    backendMatch: runtime.backend_match === true ? true : (runtime.backend_match === false ? false : null),
  2947	    requestedBackend: toTrimmedString(runtime.requested_backend),
  2948	    requestedModel: toTrimmedString(runtime.requested_model),
  2949	    detail: toTrimmedString(runtime.detail),
  2950	    boundaryNote: toTrimmedString(runtime.boundary_note),
  2951	  };
  2952	}
  2953	
  2954	function explainRuntimeSourceLabel(source) {
  2955	  if (source === "cached_llm") return "缓存命中";
  2956	  if (source === "live_llm") return "实时 LLM";
  2957	  if (source === "error") return "运行错误";
  2958	  return "未观察";
  2959	}
  2960	
  2961	function explainRuntimeBadgeState(runtime) {
  2962	  if (runtime.status === "shelved") return "shelved";
  2963	  if (!runtime.reported) return "idle";
  2964	  if (runtime.backendMatch === false || runtime.status === "warning") return "blocked";
  2965	  if (runtime.source === "cached_llm") return "ready";
  2966	  if (runtime.source === "error") return "blocked";
  2967	  if (runtime.source === "live_llm") return "live";
  2968	  return "idle";
  2969	}
  2970	
  2971	function explainRuntimeBadgeText(runtime) {
  2972	  if (runtime.status === "shelved") return "已搁置";
  2973	  if (!runtime.reported) return "未报告";
  2974	  if (runtime.backendMatch === false) return "后端不一致";
  2975	  if (runtime.status === "ready" && runtime.source === "cached_llm") return "缓存已验证";
  2976	  if (runtime.source === "live_llm") return "实时 explain";
  2977	  if (runtime.status === "warning") return "需要关注";
  2978	  return "待命";
  2979	}
  2980	
  2981	function renderExplainRuntime(payload) {
  2982	  const badge = workbenchElement("workbench-explain-runtime-badge");
  2983	  const summary = workbenchElement("workbench-explain-runtime-summary");
  2984	  const backendStrong = workbenchElement("workbench-explain-runtime-backend");
  2985	  const backendDetail = workbenchElement("workbench-explain-runtime-backend-detail");
  2986	  const sourceStrong = workbenchElement("workbench-explain-runtime-source");
  2987	  const sourceDetail = workbenchElement("workbench-explain-runtime-source-detail");
  2988	  const cacheStrong = workbenchElement("workbench-explain-runtime-cache");
  2989	  const cacheDetail = workbenchElement("workbench-explain-runtime-cache-detail");
  2990	  const boundaryStrong = workbenchElement("workbench-explain-runtime-boundary");
  2991	  if (!badge || !summary || !backendStrong || !sourceStrong || !cacheStrong || !boundaryStrong) {
  2992	    return;
  2993	  }
  2994	
  2995	  const runtime = readExplainRuntimePayload(payload);
  2996	  badge.dataset.state = explainRuntimeBadgeState(runtime);
  2997	  badge.textContent = explainRuntimeBadgeText(runtime);
  2998	
  2999	  // Phase A (2026-04-22): LLM features shelved. Short-circuit to a clean
  3000	  // "shelved" rendering so the cache/backend/source panels don't misreport

 succeeded in 0ms:
  2001	    card.type = "button";
  2002	    card.className = "workbench-history-card";
  2003	    card.dataset.selected = selected ? "true" : "false";
  2004	    card.setAttribute("aria-pressed", selected ? "true" : "false");
  2005	    card.addEventListener("click", () => {
  2006	      restoreWorkbenchPacketRevisionEntry(entry.id);
  2007	    });
  2008	
  2009	    const meta = document.createElement("div");
  2010	    meta.className = "workbench-history-meta";
  2011	
  2012	    const systemChip = document.createElement("span");
  2013	    systemChip.className = "workbench-history-chip";
  2014	    systemChip.textContent = entry.payload.system_id || "unknown_system";
  2015	
  2016	    const coverageChip = document.createElement("span");
  2017	    coverageChip.className = "workbench-history-chip";
  2018	    coverageChip.textContent = `${summary.logicNodes}L / ${summary.scenarios}S / ${summary.faultModes}F`;
  2019	
  2020	    const timeChip = document.createElement("span");
  2021	    timeChip.className = "workbench-history-chip";
  2022	    timeChip.textContent = entry.timeLabel;
  2023	
  2024	    meta.append(systemChip, coverageChip, timeChip);
  2025	
  2026	    const title = document.createElement("strong");
  2027	    title.textContent = entry.title;
  2028	
  2029	    const summaryText = document.createElement("p");
  2030	    summaryText.textContent = entry.summary;
  2031	
  2032	    const detail = document.createElement("p");
  2033	    detail.textContent = entry.detail;
  2034	
  2035	    const action = document.createElement("span");
  2036	    action.className = "workbench-history-action";
  2037	    action.textContent = selected ? "当前输入区正在使用这个 Packet 版本" : "点此恢复这个 Packet 版本";
  2038	
  2039	    card.append(meta, title, summaryText, detail, action);
  2040	    return card;
  2041	  }));
  2042	  renderWorkbenchPacketHistoryViewBar();
  2043	}
  2044	
  2045	function pushWorkbenchPacketRevision(entry) {
  2046	  selectedWorkbenchPacketRevisionId = entry.id;
  2047	  workbenchPacketRevisionHistory = [entry, ...workbenchPacketRevisionHistory].slice(0, maxWorkbenchPacketRevisionHistory);
  2048	  renderWorkbenchPacketRevisionHistory();
  2049	  persistWorkbenchPacketWorkspace();
  2050	}
  2051	
  2052	function captureCurrentWorkbenchPacketDraft({
  2053	  title,
  2054	  summary,
  2055	  detail = null,
  2056	} = {}) {
  2057	  const parsed = parseWorkbenchPacketEditor();
  2058	  if (parsed.error) {
  2059	    renderWorkbenchPacketDraftState();
  2060	    return {
  2061	      error: parsed.error,
  2062	      changed: false,
  2063	      entry: null,
  2064	      payload: null,
  2065	    };
  2066	  }
  2067	
  2068	  const baselineEntry = selectedWorkbenchPacketRevisionEntry();
  2069	  const signature = packetRevisionSignature(parsed.payload);
  2070	  if (baselineEntry && baselineEntry.signature === signature) {
  2071	    renderWorkbenchPacketDraftState();
  2072	    return {
  2073	      error: null,
  2074	      changed: false,
  2075	      entry: baselineEntry,
  2076	      payload: parsed.payload,
  2077	    };
  2078	  }
  2079	
  2080	  const entry = buildWorkbenchPacketRevisionEntry(parsed.payload, {
  2081	    title: title || "手动保存 Packet 草稿",
  2082	    summary: summary || "当前 packet 草稿已保存到版本历史。",
  2083	    detail,
  2084	  });
  2085	  pushWorkbenchPacketRevision(entry);
  2086	  return {
  2087	    error: null,
  2088	    changed: true,
  2089	    entry,
  2090	    payload: parsed.payload,
  2091	  };
  2092	}
  2093	
  2094	function maybeAutoSnapshotCurrentPacketDraft(reason) {
  2095	  return captureCurrentWorkbenchPacketDraft({
  2096	    title: `自动保存草稿 / ${reason}`,
  2097	    summary: `在${reason}前自动收纳当前 packet 草稿。`,
  2098	  });
  2099	}
  2100	
  2101	function saveCurrentWorkbenchPacketDraft() {
  2102	  const result = captureCurrentWorkbenchPacketDraft({
  2103	    title: "手动保存 Packet 草稿",
  2104	    summary: "当前 packet 草稿已手动保存到版本历史。",
  2105	  });
  2106	  if (result.error) {
  2107	    setRequestStatus(`当前 Packet 草稿无法保存：${result.error}`, "error");
  2108	    return;
  2109	  }
  2110	  if (!result.changed) {
  2111	    setRequestStatus("当前 Packet 已和已保存版本同步，无需重复保存草稿。", "warning");
  2112	    return;
  2113	  }
  2114	  setRequestStatus("当前 Packet 草稿已保存到版本历史。", "success");
  2115	}
  2116	
  2117	function downloadWorkbenchWorkspaceSnapshot() {
  2118	  const snapshot = collectWorkbenchPacketWorkspaceState();
  2119	  try {
  2120	    const blob = new Blob([prettyJson(snapshot)], {type: "application/json"});
  2121	    const objectUrl = URL.createObjectURL(blob);
  2122	    const anchor = document.createElement("a");
  2123	    anchor.href = objectUrl;
  2124	    anchor.download = workspaceSnapshotDownloadName();
  2125	    anchor.click();
  2126	    URL.revokeObjectURL(objectUrl);
  2127	    setRequestStatus("当前工作区快照已导出。", "success");
  2128	  } catch (error) {
  2129	    setRequestStatus(`导出工作区快照失败：${String(error.message || error)}`, "error");
  2130	  }
  2131	}
  2132	
  2133	async function importWorkbenchWorkspaceSnapshot(file) {
  2134	  if (!file) {
  2135	    return;
  2136	  }
  2137	  try {
  2138	    const rawText = await file.text();
  2139	    const workspace = JSON.parse(rawText);
  2140	    if (!workspace || typeof workspace !== "object") {
  2141	      throw new Error("快照不是有效对象。");
  2142	    }
  2143	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
  2144	      throw new Error(`不支持的快照类型：${workspace.kind}`);
  2145	    }
  2146	    if (!restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  2147	      sourceStatusMessage: "已导入工作区快照。",
  2148	      sourceStatusMessageWithHistory: "已导入工作区快照和结果历史。",
  2149	      packetSourceFallback: `当前样例：已导入工作区快照 / ${file.name}。`,
  2150	      preparationMessage: "已导入工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  2151	      fingerprintSummary: "已导入工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  2152	      successMessage: "已导入工作区快照。",
  2153	    })) {
  2154	      throw new Error("快照内容不完整，无法恢复工作区。");
  2155	    }
  2156	  } catch (error) {
  2157	    setRequestStatus(`导入工作区快照失败：${String(error.message || error)}`, "error");
  2158	  }
  2159	}
  2160	
  2161	function archivePayloadFromRestoreResponse(payload) {
  2162	  const resolvedFiles = payload && typeof payload.resolved_files === "object" ? payload.resolved_files : {};
  2163	  return {
  2164	    archive_dir: payload.archive_dir || "",
  2165	    manifest_json_path: payload.manifest_path || "",
  2166	    bundle_json_path: resolvedFiles.bundle_json || null,
  2167	    summary_markdown_path: resolvedFiles.summary_markdown || null,
  2168	    intake_assessment_json_path: resolvedFiles.intake_assessment_json || null,
  2169	    clarification_brief_json_path: resolvedFiles.clarification_brief_json || null,
  2170	    playback_report_json_path: resolvedFiles.playback_report_json || null,
  2171	    fault_diagnosis_report_json_path: resolvedFiles.fault_diagnosis_report_json || null,
  2172	    knowledge_artifact_json_path: resolvedFiles.knowledge_artifact_json || null,
  2173	    workspace_handoff_json_path: resolvedFiles.workspace_handoff_json || null,
  2174	    workspace_snapshot_json_path: resolvedFiles.workspace_snapshot_json || null,
  2175	  };
  2176	}
  2177	
  2178	async function restoreWorkbenchArchiveFromManifest() {
  2179	  const requestId = beginWorkbenchRequest();
  2180	  const manifestPath = workbenchElement("workbench-archive-manifest-path").value.trim();
  2181	  if (!manifestPath) {
  2182	    setRequestStatus("请先填写 archive_manifest.json 或 archive 目录路径。", "warning");
  2183	    return;
  2184	  }
  2185	
  2186	  setActiveWorkbenchPreset("");
  2187	  setRequestStatus("正在从 archive 恢复工作区...", "neutral");
  2188	  try {
  2189	    const response = await fetch(workbenchArchiveRestorePath, {
  2190	      method: "POST",
  2191	      headers: {"Content-Type": "application/json"},
  2192	      body: JSON.stringify({manifest_path: manifestPath}),
  2193	    });
  2194	    const payload = await response.json();
  2195	    if (!isLatestWorkbenchRequest(requestId)) {
  2196	      return;
  2197	    }
  2198	    if (!response.ok) {
  2199	      throw new Error(payload.message || payload.error || "workbench archive restore request failed");
  2200	    }
  2201	
  2202	    workbenchElement("workbench-archive-manifest-path").value = payload.archive_dir || payload.manifest_path || manifestPath;
  2203	    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromRestorePayload(payload));
  2204	    const sourceMode = `当前来源：Archive 恢复 / ${shortPath(payload.manifest_path)}。`;
  2205	    if (payload.workspace_snapshot && restoreWorkbenchPacketWorkspaceSnapshot(payload.workspace_snapshot, {
  2206	      sourceStatusMessage: `已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
  2207	      sourceStatusMessageWithHistory: `已从 archive 恢复工作区和结果历史 / ${shortPath(payload.manifest_path)}。`,
  2208	      packetSourceFallback: `当前样例：已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
  2209	      preparationMessage: "已从 archive 恢复工作区；如需确认当前输入，可以先看 packet 历史、结果历史和交接摘要。",
  2210	      fingerprintSummary: "已从 archive 恢复工作区。你可以继续编辑、重跑 bundle，或直接沿用归档里的历史结果继续交接。",
  2211	      successMessage: "已从 archive 恢复工作区。",
  2212	    })) {
  2213	      try {
  2214	        const restoredPacketSpec = JSON.parse(payload.workspace_snapshot.packetJsonText || "{}");
  2215	        assignFrozenSpec(restoredPacketSpec, "archive-restore");
  2216	      } catch (_) {
  2217	        // Non-critical: frozen spec not updated if snapshot packet is unparseable
  2218	      }
  2219	      setResultMode(sourceMode);
  2220	      return;
  2221	    }
  2222	
  2223	    renderBundleResponse(
  2224	      {
  2225	        bundle: payload.bundle,
  2226	        archive: archivePayloadFromRestoreResponse(payload),
  2227	      },
  2228	      {
  2229	        sourceMode,
  2230	        requestStatusMessage: payload.workspace_snapshot
  2231	          ? "已从 archive 恢复 bundle，但工作区快照不完整；当前只恢复了结果摘要。"
  2232	          : "已从 archive 恢复 bundle 结果。",
  2233	        requestStatusTone: payload.workspace_snapshot ? "warning" : "success",
  2234	      },
  2235	    );
  2236	  } catch (error) {
  2237	    if (!isLatestWorkbenchRequest(requestId)) {
  2238	      return;
  2239	    }
  2240	    setRequestStatus(`从 archive 恢复工作区失败：${String(error.message || error)}`, "error");
  2241	  }
  2242	}
  2243	
  2244	function maybeCaptureCurrentPacketRevision({
  2245	  title,
  2246	  summary,
  2247	  detail = null,
  2248	} = {}) {
  2249	  let payload;
  2250	  try {
  2251	    payload = JSON.parse(workbenchElement("workbench-packet-json").value);
  2252	  } catch (error) {
  2253	    return null;
  2254	  }
  2255	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  2256	  const signature = packetRevisionSignature(payload);
  2257	  if (latestEntry && latestEntry.signature === signature) {
  2258	    return latestEntry;
  2259	  }
  2260	  const entry = buildWorkbenchPacketRevisionEntry(payload, {
  2261	    title,
  2262	    summary,
  2263	    detail,
  2264	  });
  2265	  pushWorkbenchPacketRevision(entry);
  2266	  return entry;
  2267	}
  2268	
  2269	function restoreWorkbenchPacketRevisionEntry(entryId) {
  2270	  const entry = workbenchPacketRevisionHistory.find((item) => item.id === entryId);
  2271	  if (!entry) {
  2272	    return;
  2273	  }
  2274	  maybeAutoSnapshotCurrentPacketDraft(`恢复 ${entry.title}`);
  2275	  selectedWorkbenchPacketRevisionId = entry.id;
  2276	  renderWorkbenchPacketRevisionHistory();
  2277	  setActiveWorkbenchPreset("");
  2278	  setPacketEditor(entry.payload);
  2279	  setPacketSourceStatus(`当前 packet：已恢复 ${entry.title} / ${entry.timeLabel}。建议重新运行 bundle 验证这个版本。`);
  2280	  renderPreparationBoard(`已恢复 packet 版本「${entry.title}」。重新运行后，主看板会按这个版本显示最新结果。`);
  2281	  renderSystemFingerprintFromPacketPayload(entry.payload, {
  2282	    badgeState: "idle",
  2283	    badgeText: "画像已恢复",
  2284	    summary: "你正在回看一个历史 packet 版本；如果这个版本更合适，可以直接在此基础上继续修和重跑。",
  2285	  });
  2286	  renderWorkbenchPacketRevisionHistory();
  2287	  setRequestStatus(`已恢复 packet 版本：${entry.title}`, "success");
  2288	}
  2289	
  2290	function restoreLatestWorkbenchPacketRevision() {
  2291	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  2292	  if (!latestEntry) {
  2293	    return;
  2294	  }
  2295	  restoreWorkbenchPacketRevisionEntry(latestEntry.id);
  2296	}
  2297	
  2298	function setWorkbenchViewState(mode, historyId = "") {
  2299	  currentWorkbenchViewMode = mode;
  2300	  selectedWorkbenchHistoryId = historyId;
  2301	  persistWorkbenchPacketWorkspace();
  2302	}
  2303	
  2304	function latestWorkbenchHistoryEntry() {
  2305	  return workbenchRunHistory.length ? workbenchRunHistory[0] : null;
  2306	}
  2307	
  2308	function summarizeWorkbenchHistoryEntry(entry) {
  2309	  const bundle = entry && entry.payload ? entry.payload.bundle || {} : {};
  2310	  return {
  2311	    verdict: entry ? entry.stateLabel : "-",
  2312	    scenario: bundle.selected_scenario_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
  2313	    faultMode: bundle.selected_fault_mode_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
  2314	    archive: entry && entry.archived ? "已留档" : "未留档",
  2315	  };
  2316	}
  2317	
  2318	function detailedWorkbenchHistoryEntry(entry) {
  2319	  if (!entry) {
  2320	    return null;
  2321	  }
  2322	  if (!entry.payload) {
  2323	    return {
  2324	      title: `${entry.title} / ${entry.timeLabel}`,
  2325	      verdict: "失败",
  2326	      blocker: entry.detail || "请求未完成",
  2327	      scenario: "请求失败",
  2328	      faultMode: "请求失败",
  2329	      knowledge: "未生成",
  2330	      archive: "未留档",
  2331	    };
  2332	  }
  2333	
  2334	  const bundle = entry.payload.bundle || {};
  2335	  const clarification = bundle.clarification_brief || {};
  2336	  const knowledge = bundle.knowledge_artifact || {};
  2337	  const archive = entry.payload.archive || null;
  2338	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  2339	    ? bundle.intake_assessment.blocking_reasons
  2340	    : [];
  2341	  const ready = Boolean(bundle.ready_for_spec_build);
  2342	
  2343	  return {
  2344	    title: `${entry.title} / ${entry.timeLabel}`,
  2345	    verdict: ready ? "通过" : "阻塞",
  2346	    blocker: ready
  2347	      ? "当前无阻塞"
  2348	      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 仍未 ready。"),
  2349	    scenario: bundle.selected_scenario_id || "(none)",
  2350	    faultMode: bundle.selected_fault_mode_id || "(none)",
  2351	    knowledge: ready ? (knowledge.status || "已生成") : "尚未形成",
  2352	    archive: archive ? `已留档 / ${shortPath(archive.archive_dir)}` : "未留档",
  2353	  };
  2354	}
  2355	
  2356	function workbenchHistoryDetailFields(snapshot, compareSnapshot) {
  2357	  const compare = compareSnapshot || {};
  2358	  return [
  2359	    {label: "结论", value: snapshot.verdict, diff: snapshot.verdict === compare.verdict ? "same" : "changed"},
  2360	    {label: "当前卡点", value: snapshot.blocker, diff: snapshot.blocker === compare.blocker ? "same" : "changed"},
  2361	    {label: "Scenario", value: snapshot.scenario, diff: snapshot.scenario === compare.scenario ? "same" : "changed"},
  2362	    {label: "Fault Mode", value: snapshot.faultMode, diff: snapshot.faultMode === compare.faultMode ? "same" : "changed"},
  2363	    {label: "知识沉淀", value: snapshot.knowledge, diff: snapshot.knowledge === compare.knowledge ? "same" : "changed"},
  2364	    {label: "归档状态", value: snapshot.archive, diff: snapshot.archive === compare.archive ? "same" : "changed"},
  2365	  ];
  2366	}
  2367	
  2368	function renderWorkbenchHistoryDetailCard({
  2369	  titleElementId,
  2370	  bodyElementId,
  2371	  snapshot,
  2372	  compareSnapshot,
  2373	}) {
  2374	  workbenchElement(titleElementId).textContent = snapshot.title;
  2375	  const body = workbenchElement(bodyElementId);
  2376	  body.replaceChildren(...workbenchHistoryDetailFields(snapshot, compareSnapshot).map((field) => {
  2377	    const row = document.createElement("div");
  2378	    row.className = "workbench-history-detail-row";
  2379	
  2380	    const label = document.createElement("span");
  2381	    label.className = "workbench-history-detail-label";
  2382	    label.textContent = field.label;
  2383	
  2384	    const value = document.createElement("strong");
  2385	    value.className = "workbench-history-detail-value";
  2386	    value.dataset.diff = field.diff;
  2387	    value.textContent = field.value;
  2388	
  2389	    row.append(label, value);
  2390	    return row;
  2391	  }));
  2392	}
  2393	
  2394	function renderWorkbenchHistoryCompareBar() {
  2395	  const compareBar = workbenchElement("workbench-history-compare-bar");
  2396	  const latestEntry = latestWorkbenchHistoryEntry();
  2397	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2398	
  2399	  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry) {
  2400	    compareBar.hidden = true;
  2401	    return;
  2402	  }
  2403	
  2404	  const replay = summarizeWorkbenchHistoryEntry(selectedEntry);
  2405	  const latest = summarizeWorkbenchHistoryEntry(latestEntry);
  2406	
  2407	  workbenchElement("workbench-history-compare-summary").textContent =
  2408	    `你正在回看「${selectedEntry.title}」，下面这 4 项会直接告诉你它和最新结果差在哪里。`;
  2409	  renderValue("workbench-history-compare-verdict", `回看：${replay.verdict}`);
  2410	  renderValue("workbench-history-compare-verdict-detail", `最新：${latest.verdict}`);
  2411	  renderValue("workbench-history-compare-scenario", `回看：${replay.scenario}`);
  2412	  renderValue("workbench-history-compare-scenario-detail", `最新：${latest.scenario}`);
  2413	  renderValue("workbench-history-compare-fault", `回看：${replay.faultMode}`);
  2414	  renderValue("workbench-history-compare-fault-detail", `最新：${latest.faultMode}`);
  2415	  renderValue("workbench-history-compare-archive", `回看：${replay.archive}`);
  2416	  renderValue("workbench-history-compare-archive-detail", `最新：${latest.archive}`);
  2417	  compareBar.hidden = false;
  2418	}
  2419	
  2420	function renderWorkbenchHistoryDetailBoard() {
  2421	  const detailBoard = workbenchElement("workbench-history-detail-board");
  2422	  const latestEntry = latestWorkbenchHistoryEntry();
  2423	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2424	
  2425	  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry || latestEntry.id === selectedEntry.id) {
  2426	    detailBoard.hidden = true;
  2427	    return;
  2428	  }
  2429	
  2430	  const replaySnapshot = detailedWorkbenchHistoryEntry(selectedEntry);
  2431	  const latestSnapshot = detailedWorkbenchHistoryEntry(latestEntry);
  2432	  renderWorkbenchHistoryDetailCard({
  2433	    titleElementId: "workbench-history-detail-replay-title",
  2434	    bodyElementId: "workbench-history-detail-replay",
  2435	    snapshot: replaySnapshot,
  2436	    compareSnapshot: latestSnapshot,
  2437	  });
  2438	  renderWorkbenchHistoryDetailCard({
  2439	    titleElementId: "workbench-history-detail-latest-title",
  2440	    bodyElementId: "workbench-history-detail-latest",
  2441	    snapshot: latestSnapshot,
  2442	    compareSnapshot: replaySnapshot,
  2443	  });
  2444	  detailBoard.hidden = false;
  2445	}
  2446	
  2447	function renderWorkbenchHistoryViewBar() {
  2448	  const latestEntry = latestWorkbenchHistoryEntry();
  2449	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2450	  const statusElement = workbenchElement("workbench-history-view-status");
  2451	  const returnButton = workbenchElement("workbench-history-return-latest");
  2452	
  2453	  if (currentWorkbenchViewMode === "running") {
  2454	    statusElement.textContent = "当前查看：正在生成新结果";
  2455	    returnButton.disabled = true;
  2456	    renderWorkbenchHistoryCompareBar();
  2457	    renderWorkbenchHistoryDetailBoard();
  2458	    return;
  2459	  }
  2460	
  2461	  if (currentWorkbenchViewMode === "preparation") {
  2462	    statusElement.textContent = "当前查看：样例准备中";
  2463	    returnButton.disabled = true;
  2464	    renderWorkbenchHistoryCompareBar();
  2465	    renderWorkbenchHistoryDetailBoard();
  2466	    return;
  2467	  }
  2468	
  2469	  if (!latestEntry) {
  2470	    statusElement.textContent = "当前查看：等待第一次结果";
  2471	    returnButton.disabled = true;
  2472	    renderWorkbenchHistoryCompareBar();
  2473	    renderWorkbenchHistoryDetailBoard();
  2474	    return;
  2475	  }
  2476	
  2477	  if (currentWorkbenchViewMode !== "history" || !selectedEntry || selectedEntry.id === latestEntry.id) {
  2478	    statusElement.textContent = `当前查看：最新结果 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
  2479	    returnButton.disabled = true;
  2480	    renderWorkbenchHistoryCompareBar();
  2481	    renderWorkbenchHistoryDetailBoard();
  2482	    return;
  2483	  }
  2484	
  2485	  statusElement.textContent = `当前查看：历史回看 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  2486	  returnButton.disabled = false;
  2487	  renderWorkbenchHistoryCompareBar();
  2488	  renderWorkbenchHistoryDetailBoard();
  2489	}
  2490	
  2491	function renderWorkbenchRunHistory() {
  2492	  const container = workbenchElement("workbench-history-cards");
  2493	  if (!workbenchRunHistory.length) {
  2494	    container.replaceChildren((() => {
  2495	      const card = document.createElement("article");
  2496	      card.className = "workbench-history-card is-empty";
  2497	      const title = document.createElement("strong");
  2498	      title.textContent = "暂无结果";
  2499	      const detail = document.createElement("p");
  2500	      detail.textContent = "先点一个一键预设或手动生成一次 bundle。";

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3501,3973p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3001,3500p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3501	    if (!isLatestWorkbenchRequest(requestId)) {
  3502	      return false;
  3503	    }
  3504	    renderFailureResponse(String(error.message || error), {
  3505	      sourceMode: "当前来源：输入解析失败。",
  3506	      requestStatusMessage: String(error.message || error),
  3507	    });
  3508	    return false;
  3509	  }
  3510	  maybeCaptureCurrentPacketRevision({
  3511	    title: `${currentWorkbenchRunLabel} / 运行前 Packet`,
  3512	    summary: "在本次 bundle 请求前捕获当前 packet 版本。",
  3513	  });
  3514	  renderSystemFingerprintFromPacketPayload(requestPayload.packet_payload, {
  3515	    badgeState: "idle",
  3516	    badgeText: "画像解析中",
  3517	    summary: "系统正在生成 bundle，但这套系统的文档来源、控制目标和关键信号已经先展开给你看了。",
  3518	  });
  3519	  renderRunningBoard(`${currentWorkbenchRunLabel}：正在生成 bundle，请直接看上方可视化验收板。`);
  3520	  setRequestStatus("正在生成 workbench bundle...", "neutral");
  3521	  try {
  3522	    const response = await fetch(workbenchBundlePath, {
  3523	      method: "POST",
  3524	      headers: {"Content-Type": "application/json"},
  3525	      body: JSON.stringify(requestPayload),
  3526	    });
  3527	    const payload = await response.json();
  3528	    if (!isLatestWorkbenchRequest(requestId)) {
  3529	      return false;
  3530	    }
  3531	    if (!response.ok) {
  3532	      throw new Error(payload.message || payload.error || "workbench bundle request failed");
  3533	    }
  3534	    renderBundleResponse(payload);
  3535	    return true;
  3536	  } catch (error) {
  3537	    if (!isLatestWorkbenchRequest(requestId)) {
  3538	      return false;
  3539	    }
  3540	    renderFailureResponse(String(error.message || error));
  3541	    return false;
  3542	  }
  3543	}
  3544	
  3545	function installPacketSourceHandlers() {
  3546	  workbenchElement("load-reference-packet").addEventListener("click", () => {
  3547	    if (!applyReferencePacketSelection({
  3548	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3549	      sourceStatus: "当前样例：参考样例。适合直接点 '生成 Bundle' 做可视化 happy path 验收。",
  3550	      preparationMessage: "参考样例已经装载完毕，点击 '生成 Bundle' 即可进入可视化验收。",
  3551	    })) {
  3552	      return;
  3553	    }
  3554	    setCurrentWorkbenchRunLabel("手动生成");
  3555	    setActiveWorkbenchPreset("");
  3556	    setRequestStatus("已载入 reference packet。", "success");
  3557	  });
  3558	
  3559	  workbenchElement("load-template-packet").addEventListener("click", () => {
  3560	    if (!applyTemplatePacketSelection({
  3561	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3562	      sourceStatus: "当前样例：空白模板。适合验证 clarification gate 是否会主动拦住不完整 packet。",
  3563	      preparationMessage: "空白模板已经装载完毕，运行后通常会在 clarification gate 停下。",
  3564	    })) {
  3565	      return;
  3566	    }
  3567	    setCurrentWorkbenchRunLabel("手动生成");
  3568	    setActiveWorkbenchPreset("");
  3569	    setRequestStatus("已载入空白模板。", "warning");
  3570	  });
  3571	
  3572	  workbenchElement("workbench-file-input").addEventListener("change", async (event) => {
  3573	    const input = event.currentTarget;
  3574	    const [file] = input.files || [];
  3575	    if (!file) {
  3576	      return;
  3577	    }
  3578	
  3579	    const text = await file.text();
  3580	    maybeAutoSnapshotCurrentPacketDraft("导入本地 JSON / " + file.name);
  3581	    workbenchElement("workbench-packet-json").value = text;
  3582	    setPacketSourceStatus("当前样例：本地文件 " + file.name + "。如果不是在调试，可以直接点 '生成 Bundle' 看可视化结果。");
  3583	    renderPreparationBoard("本地 JSON 已装载，运行后会把当前 packet 的通过/阻塞结果显示在上方看板。");
  3584	
  3585	    try {
  3586	      const packetPayload = JSON.parse(text);
  3587	      pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(packetPayload, {
  3588	        title: "导入本地 JSON / " + file.name,
  3589	        summary: "本地 packet 已导入输入区。",
  3590	      }));
  3591	      renderSystemFingerprintFromPacketPayload(packetPayload, {
  3592	        badgeState: "idle",
  3593	        badgeText: "画像已载入",
  3594	        summary: "本地 JSON 已装载。你现在就能先看这套系统的大致画像，再决定要不要继续生成 bundle。",
  3595	      });
  3596	    } catch (error) {
  3597	      renderSystemFingerprint({
  3598	        badgeState: "blocked",
  3599	        badgeText: "画像未识别",
  3600	        summary: "本地 JSON 还没解析成功，所以系统画像暂时无法展开：" + String(error.message || error),
  3601	        documentFallback: "先修正 JSON，再显示来源文档。",
  3602	        signalFallback: "先修正 JSON，再显示关键信号。",
  3603	      });
  3604	    }
  3605	
  3606	    setCurrentWorkbenchRunLabel("手动生成 / " + file.name);
  3607	    setActiveWorkbenchPreset("");
  3608	    setRequestStatus("已载入本地文件：" + file.name, "success");
  3609	    input.value = "";
  3610	  });
  3611	}
  3612	
  3613	function installWorkspaceSnapshotHandlers() {
  3614	  workbenchElement("export-workbench-workspace").addEventListener("click", () => {
  3615	    downloadWorkbenchWorkspaceSnapshot();
  3616	  });
  3617	
  3618	  workbenchElement("restore-workbench-archive").addEventListener("click", () => {
  3619	    void restoreWorkbenchArchiveFromManifest();
  3620	  });
  3621	
  3622	  workbenchElement("refresh-workbench-recent-archives").addEventListener("click", () => {
  3623	    void refreshRecentWorkbenchArchives();
  3624	  });
  3625	
  3626	  workbenchElement("copy-workbench-handoff-brief").addEventListener("click", () => {
  3627	    void copyWorkbenchHandoffBrief();
  3628	  });
  3629	
  3630	  workbenchElement("workbench-workspace-file-input").addEventListener("change", async (event) => {
  3631	    const input = event.currentTarget;
  3632	    const [file] = input.files || [];
  3633	    if (!file) {
  3634	      return;
  3635	    }
  3636	
  3637	    await importWorkbenchWorkspaceSnapshot(file);
  3638	    input.value = "";
  3639	  });
  3640	}
  3641	
  3642	function installExecutionHandlers() {
  3643	  workbenchElement("run-workbench-bundle").addEventListener("click", () => {
  3644	    setCurrentWorkbenchRunLabel("手动生成");
  3645	    setActiveWorkbenchPreset("");
  3646	    void runWorkbenchBundle();
  3647	  });
  3648	
  3649	  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
  3650	    button.addEventListener("click", () => {
  3651	      setCurrentWorkbenchRunLabel(button.textContent.trim());
  3652	      runWorkbenchPreset(button.dataset.workbenchPreset || "");
  3653	    });
  3654	  });
  3655	}
  3656	
  3657	function installP43Handlers() {
  3658	  const approveBtn = workbenchElement("workbench-final-approve");
  3659	  if (approveBtn) {
  3660	    approveBtn.addEventListener("click", () => { handleFinalApprove(); });
  3661	  }
  3662	  const startGenBtn = workbenchElement("workbench-start-gen");
  3663	  if (startGenBtn) {
  3664	    startGenBtn.addEventListener("click", () => { void handleStartGen(); });
  3665	  }
  3666	}
  3667	
  3668	function installPersistenceHandlers() {
  3669	  workbenchElement("workbench-packet-json").addEventListener("input", () => {
  3670	    renderWorkbenchPacketDraftState();
  3671	    persistWorkbenchPacketWorkspace();
  3672	    saveDraftDesignState({
  3673	      packetJsonText: workbenchElement("workbench-packet-json").value,
  3674	      savedAt: new Date().toISOString(),
  3675	    });
  3676	  });
  3677	
  3678	  workbenchPersistedFieldIds.forEach((id) => {
  3679	    const field = workbenchElement(id);
  3680	    const eventName = field && field.type === "checkbox" ? "change" : "input";
  3681	    field.addEventListener(eventName, () => {
  3682	      persistWorkbenchPacketWorkspace();
  3683	    });
  3684	  });
  3685	}
  3686	
  3687	function installRecoveryAndRepairHandlers() {
  3688	  workbenchElement("workbench-history-return-latest").addEventListener("click", () => {
  3689	    restoreLatestWorkbenchHistory();
  3690	  });
  3691	
  3692	  workbenchElement("workbench-packet-history-return-latest").addEventListener("click", () => {
  3693	    restoreLatestWorkbenchPacketRevision();
  3694	  });
  3695	
  3696	  workbenchElement("workbench-save-packet-draft").addEventListener("click", () => {
  3697	    saveCurrentWorkbenchPacketDraft();
  3698	  });
  3699	
  3700	  workbenchElement("workbench-apply-schema-repairs").addEventListener("click", () => {
  3701	    void runWorkbenchSchemaSafeRepair();
  3702	  });
  3703	
  3704	  workbenchElement("workbench-apply-clarifications").addEventListener("click", () => {
  3705	    void applyClarificationWorkspace({ rerun: false });
  3706	  });
  3707	
  3708	  workbenchElement("workbench-apply-and-rerun").addEventListener("click", () => {
  3709	    void applyClarificationWorkspace({ rerun: true });
  3710	  });
  3711	}
  3712	
  3713	function installToolbarHandlers() {
  3714	  installPacketSourceHandlers();
  3715	  installWorkspaceSnapshotHandlers();
  3716	  installExecutionHandlers();
  3717	  installPersistenceHandlers();
  3718	  installRecoveryAndRepairHandlers();
  3719	  installP43Handlers();
  3720	}
  3721	
  3722	function installViewModeHandlers() {
  3723	  function setViewMode(mode) {
  3724	    document.body.dataset.view = mode;
  3725	    workbenchElement("view-btn-beginner").classList.toggle("is-active", mode === "beginner");
  3726	    workbenchElement("view-btn-expert").classList.toggle("is-active", mode === "expert");
  3727	    workbenchElement("view-mode-hint").textContent = mode === "beginner"
  3728	      ? "— 专家工具默认折叠，适合先看结论"
  3729	      : "— 显示所有工具：JSON 编辑器 / schema repair / clarification";
  3730	  }
  3731	
  3732	  const beginnerBtn = workbenchElement("view-btn-beginner");
  3733	  const expertBtn = workbenchElement("view-btn-expert");
  3734	  if (!beginnerBtn || !expertBtn) {
  3735	    return;
  3736	  }
  3737	
  3738	  beginnerBtn.addEventListener("click", () => {
  3739	    setViewMode("beginner");
  3740	  });
  3741	  expertBtn.addEventListener("click", () => {
  3742	    setViewMode("expert");
  3743	  });
  3744	
  3745	  setViewMode("beginner");
  3746	}
  3747	
  3748	// E11-13 (2026-04-25): manual_feedback_override trust-affordance.
  3749	// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
  3750	// it onto #workbench-trust-banner so the banner shows only when mode =
  3751	// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
  3752	// (e.g., when the snapshot endpoint reports a different mode in future
  3753	// E11-14+). Banner dismissal is session-local (sessionStorage); chip + actual
  3754	// mode value remain visible across dismissals.
  3755	function syncTrustBannerForMode(mode) {
  3756	  const banner = document.getElementById("workbench-trust-banner");
  3757	  if (banner) {
  3758	    banner.setAttribute("data-feedback-mode", mode);
  3759	  }
  3760	}
  3761	
  3762	function setFeedbackMode(mode) {
  3763	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  3764	  if (!allowed.has(mode)) {
  3765	    return false;
  3766	  }
  3767	  const chip = document.getElementById("workbench-feedback-mode");
  3768	  if (chip) {
  3769	    chip.setAttribute("data-feedback-mode", mode);
  3770	    const label = chip.querySelector("strong");
  3771	    if (label) {
  3772	      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
  3773	    }
  3774	  }
  3775	  syncTrustBannerForMode(mode);
  3776	  return true;
  3777	}
  3778	
  3779	function installFeedbackModeAffordance() {
  3780	  const chip = document.getElementById("workbench-feedback-mode");
  3781	  const banner = document.getElementById("workbench-trust-banner");
  3782	  if (!chip || !banner) {
  3783	    return;
  3784	  }
  3785	  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
  3786	  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
  3787	    banner.setAttribute("data-trust-banner-dismissed", "true");
  3788	  }
  3789	  const dismiss = banner.querySelector("[data-trust-banner-dismiss]");
  3790	  if (dismiss) {
  3791	    dismiss.addEventListener("click", () => {
  3792	      banner.setAttribute("data-trust-banner-dismissed", "true");
  3793	      if (window.sessionStorage) {
  3794	        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
  3795	      }
  3796	    });
  3797	  }
  3798	}
  3799	
  3800	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
  3801	// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
  3802	// the monte-carlo / reverse-diagnose API contracts from the matching e2e
  3803	// suites. One click → POST (with bounded timeout) → single-line summary in
  3804	// the card's result area.
  3805	//
  3806	// The exact card payloads are FROZEN — tests/test_workbench_wow_starters.py
  3807	// asserts byte-equality against this object; do not silently re-tune
  3808	// n_trials, max_results, n1k, or BEAT_DEEP_PAYLOAD shape without updating
  3809	// the regression lock and the surface-inventory drift acceptance.
  3810	const WOW_REQUEST_TIMEOUT_MS = 10000;
  3811	
  3812	const WOW_SCENARIOS = {
  3813	  wow_a: {
  3814	    endpoint: "/api/lever-snapshot",
  3815	    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
  3816	    payload: {
  3817	      tra_deg: -35,
  3818	      radio_altitude_ft: 2,
  3819	      engine_running: true,
  3820	      aircraft_on_ground: true,
  3821	      reverser_inhibited: false,
  3822	      eec_enable: true,
  3823	      n1k: 0.92,
  3824	      feedback_mode: "auto_scrubber",
  3825	      deploy_position_percent: 95,
  3826	    },
  3827	    // P1+P2+P5 R2 fix: read actual logic-gate states from the response
  3828	    // instead of overstating "L1–L4 latched". Under auto_scrubber pullback
  3829	    // the e2e contract says BEAT_DEEP latches at minimum {logic2, logic3,
  3830	    // logic4} with logic1 dropping out (reverser_not_deployed_eec flips
  3831	    // false mid-deploy). Print the live active set verbatim so the card
  3832	    // never overstates the truth.
  3833	    summarize: (body) => {
  3834	      const logic = body && typeof body.logic === "object" ? body.logic : {};
  3835	      const order = ["logic1", "logic2", "logic3", "logic4"];
  3836	      const active = order.filter((k) => logic[k] && logic[k].active === true);
  3837	      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
  3838	      const activeStr = active.length === 0 ? "none" : active.join("+");
  3839	      return `nodes=${nodes.length} · active=[${activeStr}] · mode=auto_scrubber`;
  3840	    },
  3841	  },
  3842	  wow_b: {
  3843	    endpoint: "/api/monte-carlo/run",
  3844	    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
  3845	    summarize: (body) => {
  3846	      if (!body) return "(empty body)";
  3847	      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
  3848	      const failures = body.n_failures;
  3849	      const trials = body.n_trials;
  3850	      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
  3851	    },
  3852	  },
  3853	  wow_c: {
  3854	    endpoint: "/api/diagnosis/run",
  3855	    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
  3856	    summarize: (body) => {
  3857	      if (!body) return "(empty body)";
  3858	      const total = body.total_combos_found;
  3859	      const returned = Array.isArray(body.results) ? body.results.length : 0;
  3860	      const grid = body.grid_resolution;
  3861	      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
  3862	    },
  3863	  },
  3864	};
  3865	
  3866	async function runWowScenario(wowId) {
  3867	  const scenario = WOW_SCENARIOS[wowId];
  3868	  const button = document.querySelector(
  3869	    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  3870	  );
  3871	  const result = document.querySelector(
  3872	    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  3873	  );
  3874	  if (!scenario || !result) {
  3875	    return;
  3876	  }
  3877	  if (button) {
  3878	    button.disabled = true;
  3879	  }
  3880	  result.removeAttribute("data-wow-state");
  3881	  result.textContent = `POST ${scenario.endpoint} ...`;
  3882	  // P1 R2 BLOCKER fix: bounded timeout via AbortController so a stalled
  3883	  // endpoint cannot freeze the card mid-demo.
  3884	  const controller =
  3885	    typeof AbortController !== "undefined" ? new AbortController() : null;
  3886	  const timeoutHandle = controller
  3887	    ? setTimeout(() => controller.abort(), WOW_REQUEST_TIMEOUT_MS)
  3888	    : null;
  3889	  try {
  3890	    const t0 = performance.now();
  3891	    const response = await fetch(scenario.endpoint, {
  3892	      method: "POST",
  3893	      headers: { "Content-Type": "application/json" },
  3894	      body: JSON.stringify(scenario.payload),
  3895	      signal: controller ? controller.signal : undefined,
  3896	    });
  3897	    const ms = Math.round(performance.now() - t0);
  3898	    let body = null;
  3899	    try {
  3900	      body = await response.json();
  3901	    } catch (_err) {
  3902	      body = null;
  3903	    }
  3904	    if (!response.ok) {
  3905	      result.setAttribute("data-wow-state", "error");
  3906	      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
  3907	      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
  3908	      return;
  3909	    }
  3910	    result.setAttribute("data-wow-state", "ok");
  3911	    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  3912	  } catch (err) {
  3913	    result.setAttribute("data-wow-state", "error");
  3914	    if (err && err.name === "AbortError") {
  3915	      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
  3916	    } else {
  3917	      result.textContent = `network error: ${err && err.message ? err.message : err}`;
  3918	    }
  3919	  } finally {
  3920	    if (timeoutHandle !== null) {
  3921	      clearTimeout(timeoutHandle);
  3922	    }
  3923	    if (button) {
  3924	      button.disabled = false;
  3925	    }
  3926	  }
  3927	}
  3928	
  3929	function installWowStarters() {
  3930	  const buttons = document.querySelectorAll(
  3931	    '.workbench-wow-run-button[data-wow-action="run"]',
  3932	  );
  3933	  buttons.forEach((btn) => {
  3934	    btn.addEventListener("click", () => {
  3935	      const wowId = btn.getAttribute("data-wow-id");
  3936	      if (wowId && WOW_SCENARIOS[wowId]) {
  3937	        void runWowScenario(wowId);
  3938	      }
  3939	    });
  3940	  });
  3941	}
  3942	
  3943	window.addEventListener("DOMContentLoaded", () => {
  3944	  bootWorkbenchShell();
  3945	  installViewModeHandlers();
  3946	  installFeedbackModeAffordance();
  3947	  installWowStarters();
  3948	
  3949	  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  3950	  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  3951	  // NOT contain bundle elements like #workbench-packet-json,
  3952	  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  3953	  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  3954	  // bundle DOM exists and would throw "Cannot read properties of null" on the
  3955	  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  3956	  // skip bundle boot entirely. This script is shared between both pages.
  3957	  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  3958	  if (!onBundlePage) {
  3959	    return;
  3960	  }
  3961	
  3962	  installToolbarHandlers();
  3963	  updateWorkflowUI();
  3964	  if (checkUrlIntakeParam()) {
  3965	    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
  3966	    if (bundleBtn) {
  3967	      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
  3968	      bundleBtn.click();
  3969	    }
  3970	    return;
  3971	  }
  3972	  void loadBootstrapPayload();
  3973	});

 succeeded in 0ms:
  3001	  // zero-counters as observed prewarm telemetry.
  3002	  if (runtime.status === "shelved") {
  3003	    summary.textContent = runtime.detail || "LLM explain 功能已搁置。";
  3004	    backendStrong.textContent = "已搁置";
  3005	    backendDetail.textContent = "LLM 后端已从活跃代码库搁置，见 archive/shelved/llm-features/SHELVED.md。";
  3006	    sourceStrong.textContent = "已搁置";
  3007	    sourceDetail.textContent = "explain 路由已移除，不会产生新的观察记录。";
  3008	    cacheStrong.textContent = "已搁置";
  3009	    cacheDetail.textContent = "LLM 缓存链路已停用；无 cached_at / 命中统计。";
  3010	    boundaryStrong.textContent = runtime.boundaryNote || "LLM 已搁置 — 非控制真值";
  3011	    return;
  3012	  }
  3013	
  3014	  if (!runtime.reported) {
  3015	    summary.textContent = "当前 workbench 响应还没带 explain runtime 观察值，所以这里只保留占位。";
  3016	  } else if (runtime.observedAt) {
  3017	    summary.textContent = `${runtime.detail || "已收到 explain runtime 观察值。"} 最近观测时间：${runtime.observedAt}。`;
  3018	  } else {
  3019	    summary.textContent = runtime.detail || "已收到 explain runtime 观察值。";
  3020	  }
  3021	
  3022	  if (runtime.backend || runtime.model) {
  3023	    const backendText = runtime.backend || "(未知 backend)";
  3024	    const modelText = runtime.model || "(未知 model)";
  3025	    backendStrong.textContent = `${backendText} · ${modelText}`;
  3026	    if (runtime.backendMatch === false) {
  3027	      const requestedBackendText = runtime.requestedBackend || "(未声明 backend)";
  3028	      const requestedModelText = runtime.requestedModel || "(auto)";
  3029	      backendDetail.textContent = `最近 pitch_prewarm 请求的是 ${requestedBackendText} · ${requestedModelText}，但当前观察到的运行后端不是这套，需要先纠正 demo_server。`;
  3030	    } else if (runtime.observedAt) {
  3031	      backendDetail.textContent = `这是最近一次 explain runtime 观测到的后端组合。观测时间：${runtime.observedAt}。`;
  3032	    } else {
  3033	      backendDetail.textContent = "这是当前 demo_server 暴露出来的 explain 后端组合；它只是操作者运行观察值，不改变任何控制真值。";
  3034	    }
  3035	  } else {
  3036	    backendStrong.textContent = "未报告";
  3037	    backendDetail.textContent = "后端暂未在 bootstrap / bundle 响应中提供 explain_runtime.llm_backend / llm_model，前端保留占位。";
  3038	  }
  3039	
  3040	  sourceStrong.textContent = explainRuntimeSourceLabel(runtime.source);
  3041	  if (runtime.backendMatch === false) {
  3042	    sourceDetail.textContent = "虽然最近预热流程有结果，但它对应的 backend / model 和当前期望不一致，所以这里会明确提醒，不把它误当成安全可用的缓存状态。";
  3043	  } else if (runtime.source === "cached_llm") {
  3044	    sourceDetail.textContent = "最近一次 explain 命中了预热缓存，说明 prewarm 生效；重启 demo_server 后需重新预热。";
  3045	  } else if (runtime.source === "live_llm") {
  3046	    sourceDetail.textContent = "最近一次 explain 走了实时 LLM（缓存未命中或未启用），请关注首次响应时延。";
  3047	  } else if (runtime.source === "error") {
  3048	    sourceDetail.textContent = "最近一次 explain 报错，详情请看 dev 抽屉 raw payload 或 server 日志。";
  3049	  } else {
  3050	    sourceDetail.textContent = "本轮还没观察到 explain 调用；一旦用户在 chat / demo 舱发起一次 explain，这里就会亮起。";
  3051	  }
  3052	
  3053	  if (runtime.cachedAt) {
  3054	    const hitsPart = runtime.cacheHits !== null ? ` · 验证命中 ${runtime.cacheHits}` : "";
  3055	    const expectedPart = runtime.expectedCount !== null ? `/${runtime.expectedCount}` : "";
  3056	    cacheStrong.textContent = runtime.cachedAt;
  3057	    cacheDetail.textContent = `cached_at 上报为 ${runtime.cachedAt}${hitsPart}${expectedPart}。explain 缓存只在 demo_server 进程内有效，重启或换 backend 都会清空，需要重新预热。`;
  3058	  } else if (runtime.cacheHits !== null || runtime.expectedCount !== null) {
  3059	    const parts = [];
  3060	    if (runtime.cacheHits !== null && runtime.expectedCount !== null) {
  3061	      parts.push(`验证命中 ${runtime.cacheHits}/${runtime.expectedCount}`);
  3062	    } else if (runtime.cacheHits !== null) {
  3063	      parts.push(`验证命中 ${runtime.cacheHits}`);
  3064	    } else if (runtime.expectedCount !== null) {
  3065	      parts.push(`预期 ${runtime.expectedCount}`);
  3066	    }
  3067	    cacheStrong.textContent = parts.join(" / ") || "待命";
  3068	    cacheDetail.textContent = "尚未看到 cached_at 时间戳，但最近 pitch_prewarm 已经回传了命中统计；仍可用来判断缓存是否在服务。";
  3069	  } else {
  3070	    cacheStrong.textContent = "待命";
  3071	    cacheDetail.textContent = "尚未看到 cached_at。若刚刚跑过 prewarm，请核对 demo_server 输出；否则这里会保持“待命”直到首次 explain 观察上报。";
  3072	  }
  3073	
  3074	  boundaryStrong.textContent = runtime.boundaryNote || "runtime status only";
  3075	}
  3076	
  3077	function renderArchiveSummary(archive) {
  3078	  const statusElement = workbenchElement("archive-status");
  3079	  if (!archive) {
  3080	    statusElement.textContent = "本次未生成 archive package。";
  3081	    renderBulletList("archive-files", [], "勾选“同时生成 archive package”后，成功运行会显示文件列表。");
  3082	    return;
  3083	  }
  3084	  statusElement.textContent = `已生成 archive package：${archive.archive_dir}`;
  3085	  const filePaths = [
  3086	    archive.manifest_json_path,
  3087	    archive.bundle_json_path,
  3088	    archive.summary_markdown_path,
  3089	    archive.intake_assessment_json_path,
  3090	    archive.clarification_brief_json_path,
  3091	    archive.playback_report_json_path,
  3092	    archive.fault_diagnosis_report_json_path,
  3093	    archive.knowledge_artifact_json_path,
  3094	    archive.workspace_handoff_json_path,
  3095	    archive.workspace_snapshot_json_path,
  3096	  ].filter(Boolean);
  3097	  renderBulletList("archive-files", filePaths, "Archive package 已生成。");
  3098	}
  3099	
  3100	function renderOnboardingReadinessFromPayload(payload) {
  3101	  const bundle = payload.bundle || {};
  3102	  const assessment = bundle.intake_assessment || {};
  3103	  const clarification = bundle.clarification_brief || {};
  3104	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  3105	  const sourceCount = Number(assessment.source_document_count || 0);
  3106	  const componentCount = Number(assessment.component_count || 0);
  3107	  const logicCount = Number(assessment.logic_node_count || 0);
  3108	  const scenarioCount = Number(assessment.acceptance_scenario_count || 0);
  3109	  const faultCount = Number(assessment.fault_mode_count || 0);
  3110	  const openQuestionCount = Number(clarification.open_question_count || 0);
  3111	  const blockingReasonCount = Number(clarification.blocking_reason_count || 0);
  3112	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  3113	  const answeredClarifications = followUpItems.filter((item) => item.status === "answered").length;
  3114	  const ready = Boolean(bundle.ready_for_spec_build);
  3115	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
  3116	  const unlocks = Array.isArray(clarification.unlocks_after_completion) && clarification.unlocks_after_completion.length
  3117	    ? clarification.unlocks_after_completion.join(" / ")
  3118	    : (ready ? "spec_build / scenario_playback / fault_diagnosis / knowledge_capture" : "spec_build");
  3119	
  3120	  renderOnboardingReadiness({
  3121	    badgeState: ready ? "ready" : "blocked",
  3122	    badgeText: ready ? "可接第二套系统" : "还不能安全接入",
  3123	    summary: ready
  3124	      ? "这份 packet 已经具备进入第二套控制逻辑 spec build 的基本条件，可以继续往 playback、diagnosis、knowledge 走。"
  3125	      : "这份 packet 还不够完整。系统已经把“缺什么”拆出来了，先补齐再接第二套控制逻辑更稳。",
  3126	    docs: `${sourceCount} 份`,
  3127	    docsDetail: sourceCount
  3128	      ? `${sourceMode}${assessment.mixed_source_packet ? " / 混合来源" : ""}${assessment.includes_pdf_sources ? " / 含 PDF" : ""}`
  3129	      : "还没有来源文档。",
  3130	    components: `${componentCount} 项`,
  3131	    componentsDetail: componentCount ? "已有组件/信号定义。" : "还没有组件定义。",
  3132	    logic: `${logicCount} 个`,
  3133	    logicDetail: logicCount ? "已有逻辑节点结构。" : "还没有逻辑节点。",
  3134	    scenarios: `${scenarioCount} 个`,
  3135	    scenariosDetail: scenarioCount ? "已有可回放验收场景。" : "还没有验收场景。",
  3136	    faults: `${faultCount} 个`,
  3137	    faultsDetail: faultCount ? "已有故障模式可注入。" : "还没有故障模式。",
  3138	    clarifications: `${answeredClarifications}/${followUpItems.length || openQuestionCount || 0}`,
  3139	    clarificationsDetail: openQuestionCount
  3140	      ? `还有 ${openQuestionCount} 个澄清问题没回答。`
  3141	      : "澄清问题已补齐。",
  3142	    unlocks,
  3143	    gaps: `${blockingReasonCount} 个结构问题 / ${openQuestionCount} 个澄清问题`,
  3144	  });
  3145	}
  3146	
  3147	function renderSystemFingerprintFromPayload(payload) {
  3148	  const bundle = payload.bundle || {};
  3149	  const assessment = bundle.intake_assessment || {};
  3150	  const clarification = bundle.clarification_brief || {};
  3151	  const generatedSpec = assessment.generated_workbench_spec || {};
  3152	  const ready = Boolean(bundle.ready_for_spec_build);
  3153	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  3154	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
  3155	
  3156	  if (assessment.mixed_source_packet) {
  3157	    sourceModeParts.push("混合来源");
  3158	  }
  3159	  if (assessment.includes_pdf_sources) {
  3160	    sourceModeParts.push("含 PDF");
  3161	  }
  3162	
  3163	  renderSystemFingerprint({
  3164	    badgeState: ready ? "ready" : "blocked",
  3165	    badgeText: ready ? "画像已识别" : "画像待补齐",
  3166	    summary: ready
  3167	      ? "这套系统已经不只是“能接入”，而是连文档覆盖、控制目标、工程真值和关键信号都已经清楚摊开了。"
  3168	      : "虽然这份 packet 还没 ready，但它的系统画像已经先展开了；你可以先确认方向对不对，再补缺口。",
  3169	    systemId: bundle.system_id || assessment.system_id || workbenchElement("workbench-fingerprint-system-id").textContent,
  3170	    objective: assessment.objective || workbenchElement("workbench-fingerprint-objective").textContent,
  3171	    sourceMode: sourceModeParts.join(" / "),
  3172	    sourceTruth: generatedSpec.source_of_truth || workbenchElement("workbench-fingerprint-source-truth").textContent,
  3173	    documents: Array.isArray(clarification.source_documents) ? clarification.source_documents : [],
  3174	    signals: Array.isArray(assessment.custom_signal_semantics) ? assessment.custom_signal_semantics : [],
  3175	    documentFallback: "当前 bundle 还没有识别出来源文档。",
  3176	    signalFallback: "当前 bundle 还没有识别出关键信号。",
  3177	  });
  3178	}
  3179	
  3180	function renderOnboardingActionsFromPayload(payload) {
  3181	  const bundle = payload.bundle || {};
  3182	  const assessment = bundle.intake_assessment || {};
  3183	  const clarification = bundle.clarification_brief || {};
  3184	  const ready = Boolean(bundle.ready_for_spec_build);
  3185	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  3186	  const blockingReasons = Array.isArray(assessment.blocking_reasons) ? assessment.blocking_reasons : [];
  3187	  const unlocks = Array.isArray(clarification.unlocks_after_completion) ? clarification.unlocks_after_completion : [];
  3188	
  3189	  const pendingFollowUps = followUpItems
  3190	    .filter((item) => item.status !== "answered")
  3191	    .map((item) => createActionItemCard({
  3192	      title: item.id || "clarification",
  3193	      detail: item.prompt || "等待补齐说明。",
  3194	      chipText: "待回答",
  3195	      chipTone: "blocked",
  3196	    }));
  3197	
  3198	  const schemaBlockers = blockingReasons.map((reason, index) => createActionItemCard({
  3199	    title: `schema blocker ${index + 1}`,
  3200	    detail: reason,
  3201	    chipText: "待补结构",
  3202	    chipTone: "blocked",
  3203	  }));
  3204	
  3205	  const unlockItems = unlocks.map((item) => createActionItemCard({
  3206	    title: item,
  3207	    detail: ready
  3208	      ? "这项能力已经放行，可以继续往下走。"
  3209	      : "把左边两列补齐后，这项能力就会被解锁。",
  3210	    chipText: ready ? "已解锁" : "待解锁",
  3211	    chipTone: ready ? "ready" : "signal",
  3212	  }));
  3213	
  3214	  renderOnboardingActions({
  3215	    badgeState: ready ? "ready" : "blocked",
  3216	    badgeText: ready ? "接入路径已放行" : "接入路径待补齐",
  3217	    summary: ready
  3218	      ? "这套系统当前已经没有澄清或结构阻塞，动作板上只保留已放行的下一步能力。"
  3219	      : "这套系统还没 ready，但动作板已经把先补什么、再补什么、补完解锁什么拆开了。",
  3220	    followUps: pendingFollowUps,
  3221	    blockers: schemaBlockers,
  3222	    unlocks: unlockItems,
  3223	    followUpFallback: ready ? "澄清项都已回答。" : "当前没有待回答澄清项。",
  3224	    blockerFallback: ready ? "结构问题已补齐。" : "当前没有额外结构 blocker。",
  3225	    unlockFallback: "当前没有可展示的解锁项。",
  3226	  });
  3227	}
  3228	
  3229	function renderVisualAcceptanceBoard(payload) {
  3230	  const bundle = payload.bundle || {};
  3231	  const clarification = bundle.clarification_brief || {};
  3232	  const diagnosis = bundle.fault_diagnosis_report || {};
  3233	  const knowledge = bundle.knowledge_artifact || {};
  3234	  const archive = payload.archive || null;
  3235	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  3236	    ? bundle.intake_assessment.blocking_reasons
  3237	    : [];
  3238	  const ready = Boolean(bundle.ready_for_spec_build);
  3239	
  3240	  if (ready) {
  3241	    setVisualBadge(archive ? "archived" : "ready", archive ? "通过并已归档" : "可以验收");
  3242	    renderValue("workbench-spotlight-verdict", "链路已跑通");
  3243	    renderValue(
  3244	      "workbench-spotlight-verdict-detail",
  3245	      archive
  3246	        ? "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge，并已留下 archive。"
  3247	        : "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge。"
  3248	    );
  3249	    renderValue("workbench-spotlight-blocker", "当前无阻塞");
  3250	    renderValue(
  3251	      "workbench-spotlight-blocker-detail",
  3252	      bundle.selected_fault_mode_id
  3253	        ? `当前 fault mode：${bundle.selected_fault_mode_id}，可以直接看右侧卡片做验收。`
  3254	        : "当前没有 blocking reason。"
  3255	    );
  3256	    renderValue("workbench-spotlight-knowledge", knowledge.status || "已生成");
  3257	    renderValue(
  3258	      "workbench-spotlight-knowledge-detail",
  3259	      knowledge.diagnosis_summary || diagnosis.suspected_root_cause || "知识沉淀已生成。"
  3260	    );
  3261	    renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
  3262	    renderValue(
  3263	      "workbench-spotlight-archive-detail",
  3264	      archive
  3265	        ? `目录：${shortPath(archive.archive_dir)}`
  3266	        : "本次没有生成 archive package。"
  3267	    );
  3268	    renderValue(
  3269	      "workbench-visual-summary",
  3270	      "这次 bundle 已经走完整条 engineer workflow。你现在主要看步骤状态带和聚焦卡片，不必先看 Raw JSON。"
  3271	    );
  3272	    setStageState("intake", "complete", "packet 已通过 intake 检查。");
  3273	    setStageState("clarification", "complete", clarification.gate_status || "clarification 已放行。");
  3274	    setStageState("playback", "complete", "已生成可复盘的 playback。");
  3275	    setStageState("diagnosis", "complete", diagnosis.suspected_root_cause || "已生成 diagnosis。");
  3276	    setStageState("knowledge", "complete", knowledge.status ? `knowledge=${knowledge.status}` : "已生成 knowledge artifact。");
  3277	    setStageState("archive", archive ? "complete" : "pending", archive ? "archive package 已落档。" : "本次未归档，但可随时重跑。");
  3278	    return;
  3279	  }
  3280	
  3281	  setVisualBadge(archive ? "archived" : "blocked", archive ? "阻塞但已归档" : "当前阻塞");
  3282	  renderValue("workbench-spotlight-verdict", "需要补信息");
  3283	  renderValue(
  3284	    "workbench-spotlight-verdict-detail",
  3285	    "当前 packet 还没走到 playback / diagnosis / knowledge，先补齐 clarification gate 需要的信息。"
  3286	  );
  3287	  renderValue("workbench-spotlight-blocker", "Clarification Gate");
  3288	  renderValue(
  3289	    "workbench-spotlight-blocker-detail",
  3290	    blockingReasons.length ? blockingReasons[0] : clarification.gating_statement || "当前 packet 仍未 ready。"
  3291	  );
  3292	  renderValue("workbench-spotlight-knowledge", "尚未形成");
  3293	  renderValue("workbench-spotlight-knowledge-detail", "因为 clarification 还没过，所以 diagnosis / knowledge 还不会生成。");
  3294	  renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
  3295	  renderValue(
  3296	    "workbench-spotlight-archive-detail",
  3297	    archive
  3298	      ? `已把当前阻塞态留档到 ${shortPath(archive.archive_dir)}`
  3299	      : "如果你想保留这次阻塞态，可以勾选 archive 后重跑。"
  3300	  );
  3301	  renderValue(
  3302	    "workbench-visual-summary",
  3303	    "这次不是失败，而是系统在 clarification gate 主动停下来了。你只要看卡在哪一步，不需要读后面的专业输出。"
  3304	  );
  3305	  setStageState("intake", "complete", "packet 已被读取并检查。");
  3306	  setStageState("clarification", "blocked", clarification.gate_status || "clarification 仍未放行。");
  3307	  setStageState("playback", "idle", "clarification 未过，暂不继续。");
  3308	  setStageState("diagnosis", "idle", "clarification 未过，暂不继续。");
  3309	  setStageState("knowledge", "idle", "clarification 未过，暂不继续。");
  3310	  setStageState("archive", archive ? "complete" : "pending", archive ? "阻塞态也已成功归档。" : "当前未归档。");
  3311	}
  3312	
  3313	function renderBundleResponse(payload, {
  3314	  pushHistory = true,
  3315	  sourceMode = "当前来源：`POST /api/workbench/bundle`。",
  3316	  requestStatusMessage = null,
  3317	  requestStatusTone = null,
  3318	} = {}) {
  3319	  const bundle = payload.bundle || {};
  3320	  const clarification = bundle.clarification_brief || {};
  3321	  const playback = bundle.playback_report || {};
  3322	  const diagnosis = bundle.fault_diagnosis_report || {};
  3323	  const knowledge = bundle.knowledge_artifact || {};
  3324	  const resolution = knowledge.resolution_record || {};
  3325	  const optimization = knowledge.optimization_record || {};
  3326	  const ready = Boolean(bundle.ready_for_spec_build);
  3327	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
  3328	  workbenchElement("bundle-ready-state").textContent = ready ? "Ready" : "Blocked";
  3329	  workbenchElement("bundle-ready-state").dataset.state = ready ? "ready" : "blocked";
  3330	  workbenchElement("bundle-scenario-id").textContent = bundle.selected_scenario_id || "(none)";
  3331	  workbenchElement("bundle-fault-mode-id").textContent = bundle.selected_fault_mode_id || "(none)";
  3332	  workbenchElement("clarification-gate-status").textContent = clarification.gate_status || "-";
  3333	  workbenchElement("clarification-gating-statement").textContent = clarification.gating_statement || "-";
  3334	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  3335	    ? bundle.intake_assessment.blocking_reasons
  3336	    : [];
  3337	  workbenchElement("bundle-blocking-reasons").textContent = blockingReasons.length
  3338	    ? blockingReasons.join(" | ")
  3339	    : "none";
  3340	
  3341	  renderOnboardingReadinessFromPayload(payload);
  3342	  renderSystemFingerprintFromPayload(payload);
  3343	  renderOnboardingActionsFromPayload(payload);
  3344	  renderSchemaRepairWorkspaceFromPayload(payload);
  3345	  renderClarificationWorkspaceFromPayload(payload);
  3346	  renderVisualAcceptanceBoard(payload);
  3347	  renderBulletList("bundle-next-actions", bundle.next_actions, "当前没有 next actions。");
  3348	  renderValue("playback-scenario-label", playback.scenario_label, ready ? "未提供 playback label。" : "Blocked bundle 不包含 playback。");
  3349	  renderValue("playback-completion", playback.completion_reached, ready ? "false" : "Blocked bundle 不包含 playback。");
  3350	  renderValue("playback-sampled-signals", Array.isArray(playback.signal_series) ? playback.signal_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  3351	  renderValue("playback-sampled-logic", Array.isArray(playback.logic_series) ? playback.logic_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  3352	  renderValue("diagnosis-fault-mode", diagnosis.fault_mode_id || bundle.selected_fault_mode_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3353	  renderValue("diagnosis-target-component", diagnosis.target_component_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3354	  renderValue("diagnosis-root-cause", diagnosis.suspected_root_cause, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3355	  renderValue(
  3356	    "diagnosis-blocked-logic",
  3357	    Array.isArray(diagnosis.blocked_logic_node_ids) && diagnosis.blocked_logic_node_ids.length
  3358	      ? diagnosis.blocked_logic_node_ids.join(" | ")
  3359	      : null,
  3360	    ready ? "none" : "Blocked bundle 不包含 diagnosis。",
  3361	  );
  3362	  renderValue("knowledge-status", knowledge.status, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3363	  renderValue("knowledge-diagnosis-summary", knowledge.diagnosis_summary, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3364	  renderValue("knowledge-confirmed-root-cause", resolution.confirmed_root_cause, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3365	  renderValue("knowledge-repair-action", resolution.repair_action, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3366	  renderValue("knowledge-validation-after-fix", resolution.validation_after_fix, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3367	  renderValue("knowledge-residual-risk", resolution.residual_risk, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3368	  renderValue("optimization-logic-change", optimization.suggested_logic_change, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  3369	  renderValue("optimization-reliability-gain", optimization.reliability_gain_hypothesis, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  3370	  renderValue(
  3371	    "optimization-guardrail-note",
  3372	    optimization.redundancy_reduction_or_guardrail_note,
  3373	    ready ? "(none)" : "Blocked bundle 不包含 optimization record。",
  3374	  );
  3375	  if (pushHistory) {
  3376	    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromPayload(payload));
  3377	  }
  3378	  if (payload.archive) {
  3379	    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromBundlePayload(payload));
  3380	  }
  3381	  renderArchiveSummary(payload.archive);
  3382	  renderExplainRuntime(payload);
  3383	  workbenchElement("bundle-json-output").textContent = prettyJson(payload);
  3384	  setResultMode(sourceMode);
  3385	  setRequestStatus(
  3386	    requestStatusMessage || (
  3387	      ready
  3388	        ? "Bundle 已生成，可直接拿右侧结果做验收。"
  3389	        : "Clarification follow-up bundle 已生成；当前 packet 仍被 schema / clarification gate 阻塞。"
  3390	    ),
  3391	    requestStatusTone || (ready ? "success" : "warning"),
  3392	  );
  3393	}
  3394	
  3395	function collectWorkbenchRequestPayload() {
  3396	  let packetPayload;
  3397	  try {
  3398	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  3399	  } catch (error) {
  3400	    throw new Error(`packet JSON 解析失败：${String(error.message || error)}`);
  3401	  }
  3402	  return {
  3403	    packet_payload: packetPayload,
  3404	    scenario_id: workbenchElement("workbench-scenario-id").value.trim() || undefined,
  3405	    fault_mode_id: workbenchElement("workbench-fault-mode-id").value.trim() || undefined,
  3406	    sample_period_s: Number(workbenchElement("workbench-sample-period").value || "0.5"),
  3407	    archive_bundle: workbenchElement("workbench-archive-toggle").checked,
  3408	    workspace_handoff: buildWorkbenchHandoffSnapshot(),
  3409	    workspace_snapshot: collectWorkbenchPacketWorkspaceState(),
  3410	    observed_symptoms: workbenchElement("workbench-observed-symptoms").value.trim() || undefined,
  3411	    evidence_links: splitLines(workbenchElement("workbench-evidence-links").value),
  3412	    confirmed_root_cause: workbenchElement("workbench-root-cause").value.trim() || undefined,
  3413	    repair_action: workbenchElement("workbench-repair-action").value.trim() || undefined,
  3414	    validation_after_fix: workbenchElement("workbench-validation-after-fix").value.trim() || undefined,
  3415	    residual_risk: workbenchElement("workbench-residual-risk").value.trim() || undefined,
  3416	    suggested_logic_change: workbenchElement("workbench-logic-change").value.trim() || undefined,
  3417	    reliability_gain_hypothesis: workbenchElement("workbench-reliability-gain").value.trim() || undefined,
  3418	    guardrail_note: workbenchElement("workbench-guardrail-note").value.trim() || undefined,
  3419	  };
  3420	}
  3421	
  3422	function checkUrlIntakeParam() {
  3423	  try {
  3424	    const params = new URLSearchParams(window.location.search);
  3425	    const intakeRaw = params.get("intake");
  3426	    let intakePacket;
  3427	    let textarea;
  3428	    if (!intakeRaw) {
  3429	      return false;
  3430	    }
  3431	    try {
  3432	      intakePacket = JSON.parse(intakeRaw);
  3433	    } catch (parseError) {
  3434	      intakePacket = JSON.parse(decodeURIComponent(intakeRaw));
  3435	    }
  3436	    if (!intakePacket || typeof intakePacket !== "object") {
  3437	      return false;
  3438	    }
  3439	    setPacketEditor(intakePacket);
  3440	    textarea = workbenchElement("workbench-packet-json");
  3441	    if (textarea) {
  3442	      textarea.scrollTop = textarea.scrollHeight;
  3443	    }
  3444	    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(intakePacket, {
  3445	      title: "Pipeline 结果预载入",
  3446	      summary: "通过 URL intake 参数载入的 packet。",
  3447	    }));
  3448	    renderPreparationBoard("Pipeline 结果已经装载，系统会自动生成 bundle 并显示诊断结果。");
  3449	    renderSystemFingerprintFromPacketPayload(intakePacket, {
  3450	      badgeState: "idle",
  3451	      badgeText: "画像已载入",
  3452	      summary: "Pipeline 结果已经带入当前 workbench，系统会直接继续生成 bundle。",
  3453	    });
  3454	    setPacketSourceStatus("当前样例：来自 AI Document Analyzer 的 Pipeline 结果。页面会自动生成 Bundle。");
  3455	    setCurrentWorkbenchRunLabel("Pipeline 结果导入");
  3456	    setActiveWorkbenchPreset("");
  3457	    return true;
  3458	  } catch (error) {
  3459	    return false;
  3460	  }
  3461	}
  3462	
  3463	async function loadBootstrapPayload() {
  3464	  setRequestStatus("正在加载 bootstrap 样例...", "neutral");
  3465	  const response = await fetch(workbenchBootstrapPath, {method: "GET"});
  3466	  const payload = await response.json();
  3467	  if (!response.ok) {
  3468	    throw new Error(payload.error || "bootstrap request failed");
  3469	  }
  3470	  bootstrapPayload = payload;
  3471	  renderExplainRuntime(payload);
  3472	  workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
  3473	  renderRecentWorkbenchArchives();
  3474	  workbenchElement("default-archive-root").textContent = payload.default_archive_root || "(unknown)";
  3475	  if (restoreWorkbenchPacketWorkspaceFromBrowser()) {
  3476	    return;
  3477	  }
  3478	  setPacketEditor(payload.reference_packet);
  3479	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.reference_packet, {
  3480	    title: "默认参考样例",
  3481	    summary: "启动时自动载入的 reference packet。",
  3482	  }));
  3483	  fillReferenceResolutionDefaults();
  3484	  setPacketSourceStatus("当前样例：参考样例。适合直接点“生成 Bundle”做可视化 happy path 验收。");
  3485	  renderPreparationBoard("参考样例已经装载完毕，点击“生成 Bundle”即可进入可视化验收。");
  3486	  renderSystemFingerprintFromPacketPayload(payload.reference_packet, {
  3487	    badgeState: "idle",
  3488	    badgeText: "画像已载入",
  3489	    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  3490	  });
  3491	  setActiveWorkbenchPreset("");
  3492	  setRequestStatus("已载入 reference packet，直接点“生成 Bundle”即可跑 happy path。", "success");
  3493	}
  3494	
  3495	async function runWorkbenchBundle() {
  3496	  const requestId = beginWorkbenchRequest();
  3497	  let requestPayload;
  3498	  try {
  3499	    requestPayload = collectWorkbenchRequestPayload();
  3500	  } catch (error) {

codex
文件本体已经读完。我接着做两类交叉验证：一是搜全仓看有没有 selector 仍绑在旧可见文案上，二是直接起 `demo_server` 探 `/workbench` 和相关静态资源，避免只凭源码推断。
exec
/bin/zsh -lc "rg -n \"Scenario Control|Spec Review Surface|Logic Circuit Surface|Probe & Trace|Annotate & Propose|Hand off & Track|workbench-control-panel|workbench-document-panel|workbench-circuit-panel|workbench-control-status|workbench-document-status|workbench-circuit-status|data-column=\\\"control\\\"|data-column=\\\"document\\\"|data-column=\\\"circuit\\\"\" src tests" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_column_rename.py:6:  Scenario Control          → Probe & Trace · 探针与追踪
tests/test_workbench_column_rename.py:7:  Spec Review Surface       → Annotate & Propose · 标注与提案
tests/test_workbench_column_rename.py:8:  Logic Circuit Surface     → Hand off & Track · 移交与跟踪
tests/test_workbench_column_rename.py:89:        "<h2>Scenario Control</h2>",
tests/test_workbench_column_rename.py:90:        "<h2>Spec Review Surface</h2>",
tests/test_workbench_column_rename.py:91:        "<h2>Logic Circuit Surface</h2>",
tests/test_workbench_column_rename.py:116:        'id="workbench-control-panel"',
tests/test_workbench_column_rename.py:117:        'id="workbench-document-panel"',
tests/test_workbench_column_rename.py:118:        'id="workbench-circuit-panel"',
tests/test_workbench_column_rename.py:119:        'data-column="control"',
tests/test_workbench_column_rename.py:120:        'data-column="document"',
tests/test_workbench_column_rename.py:121:        'data-column="circuit"',
tests/test_workbench_column_rename.py:125:        'id="workbench-control-status"',
tests/test_workbench_column_rename.py:126:        'id="workbench-document-status"',
tests/test_workbench_column_rename.py:127:        'id="workbench-circuit-status"',
tests/test_workbench_column_rename.py:141:        "Probe & Trace ready",
tests/test_workbench_column_rename.py:142:        "Annotate & Propose ready",
tests/test_workbench_column_rename.py:143:        "Hand off & Track ready",
tests/test_workbench_column_rename.py:171:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_column_rename.py:172:    assert 'data-column="circuit"' in html
tests/test_workbench_approval_center.py:70:        anchor={"selector": "#workbench-document-panel", "start_offset": 0, "end_offset": 12, "text_quote": "Reference"},
tests/test_workbench_dual_route.py:68:    assert 'id="workbench-control-panel"' in body
src/well_harness/static/workbench.js:64:// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")
src/well_harness/static/workbench.js:65:// to engineer-task verbs ("Probe & Trace / Annotate & Propose / Hand off
src/well_harness/static/workbench.js:69:  const status = workbenchElement("workbench-control-status");
src/well_harness/static/workbench.js:72:      "Probe & Trace ready. Scenario actions are staged for E07+.";
src/well_harness/static/workbench.js:78:  const status = workbenchElement("workbench-document-status");
src/well_harness/static/workbench.js:81:      "Annotate & Propose ready. Text-range annotation arrives in E07.";
src/well_harness/static/workbench.js:87:  const status = workbenchElement("workbench-circuit-status");
src/well_harness/static/workbench.js:90:      "Hand off & Track ready. Overlay annotation arrives in E07.";
tests/test_workbench_shell.py:60:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_shell.py:66:    assert "workbench-control-panel" in ids
tests/test_workbench_shell.py:67:    assert "workbench-document-panel" in ids
tests/test_workbench_shell.py:68:    assert "workbench-circuit-panel" in ids
src/well_harness/static/workbench.html:202:          id="workbench-control-panel"
src/well_harness/static/workbench.html:204:          data-column="control"
src/well_harness/static/workbench.html:212:          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
src/well_harness/static/workbench.html:222:          id="workbench-document-panel"
src/well_harness/static/workbench.html:224:          data-column="document"
src/well_harness/static/workbench.html:232:          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
src/well_harness/static/workbench.html:242:          id="workbench-circuit-panel"
src/well_harness/static/workbench.html:244:          data-column="circuit"
src/well_harness/static/workbench.html:252:          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
tests/test_workbench_annotation_static.py:19:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_annotation_static.py:21:    assert 'id="workbench-document-panel"' in html
tests/test_workbench_annotation_static.py:23:    assert 'id="workbench-circuit-panel"' in html
tests/test_workbench_prompt_ticket_auth.py:19:        anchor={"selector": "#workbench-document-panel", "href": "https://example.test/spec"},

exec
/bin/zsh -lc 'rg -n "Scenario Control|Spec Review Surface|Logic Circuit Surface|control panel ready|document panel ready|circuit panel ready|Waiting for control panel boot|Waiting for document panel boot|Waiting for circuit panel boot" tests/e2e tests src' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_column_rename.py:6:  Scenario Control          → Probe & Trace · 探针与追踪
tests/test_workbench_column_rename.py:7:  Spec Review Surface       → Annotate & Propose · 标注与提案
tests/test_workbench_column_rename.py:8:  Logic Circuit Surface     → Hand off & Track · 移交与跟踪
tests/test_workbench_column_rename.py:89:        "<h2>Scenario Control</h2>",
tests/test_workbench_column_rename.py:90:        "<h2>Spec Review Surface</h2>",
tests/test_workbench_column_rename.py:91:        "<h2>Logic Circuit Surface</h2>",
tests/test_workbench_column_rename.py:95:        "Waiting for control panel boot.",
tests/test_workbench_column_rename.py:96:        "Waiting for document panel boot.",
tests/test_workbench_column_rename.py:97:        "Waiting for circuit panel boot.",
src/well_harness/static/workbench.js:64:// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")

exec
/bin/zsh -lc 'git diff --unified=20 main..HEAD -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..ced38be
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
@@ -0,0 +1,53 @@
+# E11-03 Surface Inventory — three-column rename
+
+> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
+
+## Surface diff inventory
+
+| # | Surface | Type | Anchor | Notes |
+|---|---|---|---|---|
+| 1 | Column 1 title: `Scenario Control` → `Probe & Trace · 探针与追踪` | [REWRITE] | `workbench.html` `#workbench-control-panel <h2>` | Engineer-task verb pair replaces technical noun. |
+| 2 | Column 1 eyebrow: `control panel` → `probe & trace` | [REWRITE] | `workbench.html` `#workbench-control-panel .eyebrow` | Lowercase match for visible chrome consistency. |
+| 3 | Column 1 boot status: `Waiting for control panel boot.` → `Waiting for probe & trace panel boot.` | [REWRITE] | `workbench.html` `#workbench-control-status` | Default copy before JS hydrates. |
+| 4 | Column 1 JS boot: `Control panel ready. Scenario actions are staged for E07+.` → `Probe & Trace ready. Scenario actions are staged for E07+.` | [REWRITE] | `workbench.js:bootWorkbenchControlPanel` | Status after hydration. |
+| 5 | Column 2 title: `Spec Review Surface` → `Annotate & Propose · 标注与提案` | [REWRITE] | `workbench.html` `#workbench-document-panel <h2>` | Maps to text-range annotation flow. |
+| 6 | Column 2 eyebrow: `document` → `annotate & propose` | [REWRITE] | `workbench.html` `#workbench-document-panel .eyebrow` | |
+| 7 | Column 2 boot status: `Waiting for document panel boot.` → `Waiting for annotate & propose panel boot.` | [REWRITE] | `workbench.html` `#workbench-document-status` | |
+| 8 | Column 2 JS boot: `Document panel ready. Text-range annotation arrives in E07.` → `Annotate & Propose ready. Text-range annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchDocumentPanel` | |
+| 9 | Column 3 title: `Logic Circuit Surface` → `Hand off & Track · 移交与跟踪` | [REWRITE] | `workbench.html` `#workbench-circuit-panel <h2>` | Maps to ticket handoff flow. |
+| 10 | Column 3 eyebrow: `circuit` → `hand off & track` | [REWRITE] | `workbench.html` `#workbench-circuit-panel .eyebrow` | |
+| 11 | Column 3 boot status: `Waiting for circuit panel boot.` → `Waiting for hand off & track panel boot.` | [REWRITE] | `workbench.html` `#workbench-circuit-status` | |
+| 12 | Column 3 JS boot: `Circuit panel ready. Overlay annotation arrives in E07.` → `Hand off & Track ready. Overlay annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchCircuitPanel` | |
+
+## Tier-trigger evaluation
+
+Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
+
+> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
+
+- **copy_diff_lines** = 12 → ≥ 10 ✓
+- **[REWRITE/DELETE] count** = 12 (all rows) → ≥ 3 ✓
+
+> **Verdict: Tier-A** (5-persona review).
+
+This is exactly the rename-pure case the Tier-A trigger was designed for: every visible string on three structural surfaces is being rewritten in lockstep. Tier-A is the conservative routing.
+
+## Stable-ID invariants (must hold)
+
+The plan explicitly says "保留底层 ID 不变以免 e2e 测试失效" — every one of these anchors stays untouched:
+
+- `id="workbench-control-panel"`, `id="workbench-document-panel"`, `id="workbench-circuit-panel"`
+- `data-column="control"`, `data-column="document"`, `data-column="circuit"`
+- `data-annotation-surface="control"`, `data-annotation-surface="document"`, `data-annotation-surface="circuit"`
+- `id="workbench-control-status"`, `id="workbench-document-status"`, `id="workbench-circuit-status"`
+
+`tests/test_workbench_column_rename.py` locks all 12 stable anchors alongside the new visible copy so a future "polish" pass can't silently regress either side.
+
+## Truth-engine red line
+
+Files touched:
+- `src/well_harness/static/workbench.html` (3 [REWRITE] blocks, 12 visible-copy lines)
+- `src/well_harness/static/workbench.js` (3 [REWRITE] boot status strings)
+- `tests/test_workbench_column_rename.py` (NEW)
+
+Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index e6ecec3..d8fb548 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -1,13 +1,14 @@
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
+E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 39a3194..a706072 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -189,85 +189,85 @@
       <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
         <span class="workbench-annotation-toolbar-label">Annotation</span>
         <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">Point</button>
         <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">Area</button>
         <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">Link</button>
         <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">Text Range</button>
         <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
           Point tool active
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
-            <p class="eyebrow">control panel</p>
-            <h2>Scenario Control</h2>
+            <p class="eyebrow">probe &amp; trace</p>
+            <h2>Probe &amp; Trace · 探针与追踪</h2>
           </header>
           <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for control panel boot.
+            Waiting for probe &amp; trace panel boot.
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
-            <p class="eyebrow">document</p>
-            <h2>Spec Review Surface</h2>
+            <p class="eyebrow">annotate &amp; propose</p>
+            <h2>Annotate &amp; Propose · 标注与提案</h2>
           </header>
           <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for document panel boot.
+            Waiting for annotate &amp; propose panel boot.
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
-            <p class="eyebrow">circuit</p>
-            <h2>Logic Circuit Surface</h2>
+            <p class="eyebrow">hand off &amp; track</p>
+            <h2>Hand off &amp; Track · 移交与跟踪</h2>
           </header>
           <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for circuit panel boot.
+            Waiting for hand off &amp; track panel boot.
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
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index dc66e55..3dd764a 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -43,60 +43,68 @@ let workbenchHistorySequence = 0;
 let currentWorkbenchViewMode = "empty";
 let workbenchPacketRevisionHistory = [];
 let selectedWorkbenchPacketRevisionId = "";
 let workbenchPacketRevisionSequence = 0;
 let suspendWorkbenchPacketWorkspacePersistence = false;
 const maxWorkbenchRunHistory = 6;
 const maxWorkbenchPacketRevisionHistory = 8;
 
 function bootWorkbenchColumnSafely(columnName, bootFn) {
   try {
     bootFn();
   } catch (error) {
     const status = workbenchElement(`workbench-${columnName}-status`);
     if (status) {
       status.textContent = `${columnName} panel failed independently: ${error.message || error}`;
       status.dataset.tone = "warning";
     }
   }
 }
 
+// E11-03 (2026-04-26): the three columns were renamed from technical
+// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")
+// to engineer-task verbs ("Probe & Trace / Annotate & Propose / Hand off
+// & Track"). Underlying ids and data-column tokens stay stable so e2e
+// selectors don't break — only the visible status copy here changes.
 function bootWorkbenchControlPanel() {
   const status = workbenchElement("workbench-control-status");
   if (status) {
-    status.textContent = "Control panel ready. Scenario actions are staged for E07+.";
+    status.textContent =
+      "Probe & Trace ready. Scenario actions are staged for E07+.";
     status.dataset.tone = "ready";
   }
 }
 
 function bootWorkbenchDocumentPanel() {
   const status = workbenchElement("workbench-document-status");
   if (status) {
-    status.textContent = "Document panel ready. Text-range annotation arrives in E07.";
+    status.textContent =
+      "Annotate & Propose ready. Text-range annotation arrives in E07.";
     status.dataset.tone = "ready";
   }
 }
 
 function bootWorkbenchCircuitPanel() {
   const status = workbenchElement("workbench-circuit-status");
   if (status) {
-    status.textContent = "Circuit panel ready. Overlay annotation arrives in E07.";
+    status.textContent =
+      "Hand off & Track ready. Overlay annotation arrives in E07.";
     status.dataset.tone = "ready";
   }
 }
 
 function bootWorkbenchShell() {
   bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
   bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
   bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
 }
 
 // P43 authority contract — written only via assignFrozenSpec; never mutated directly
 let frozenSpec = null;
 
 // P43 workflow state machine (P43-03)
 let workflowState = "INIT";
 
 const _workflowTransitions = {
   INIT:        { confirm_freeze: "FROZEN",      load_packet: "INIT" },
   FROZEN:      { start_gen: "GENERATING",       confirm_freeze: "FROZEN",   reiterate: "INIT" },
   GENERATING:  { gen_complete: "PANEL_READY",   gen_fail: "ERROR",          reiterate: "INIT" },
diff --git a/tests/test_workbench_column_rename.py b/tests/test_workbench_column_rename.py
new file mode 100644
index 0000000..cb1a441
--- /dev/null
+++ b/tests/test_workbench_column_rename.py
@@ -0,0 +1,172 @@
+"""E11-03 — three-column rename regression lock.
+
+Locks the visible column titles, eyebrows, and boot status copy after
+the E11-03 rename from technical nouns to engineer-task verbs:
+
+  Scenario Control          → Probe & Trace · 探针与追踪
+  Spec Review Surface       → Annotate & Propose · 标注与提案
+  Logic Circuit Surface     → Hand off & Track · 移交与跟踪
+
+Per E11-00-PLAN row E11-03: underlying IDs (data-column, panel ids,
+data-annotation-surface) are intentionally stable so e2e selectors and
+JS boot wiring don't break. Verify both invariants — new copy AND
+preserved IDs — so a future "polish" pass can't silently regress
+either side.
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
+# ─── 1. New visible copy is present ──────────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "title",
+    [
+        "Probe &amp; Trace · 探针与追踪",
+        "Annotate &amp; Propose · 标注与提案",
+        "Hand off &amp; Track · 移交与跟踪",
+    ],
+)
+def test_workbench_html_carries_new_column_title(title: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert title in html, f"missing renamed column title: {title}"
+
+
+@pytest.mark.parametrize(
+    "eyebrow",
+    ["probe &amp; trace", "annotate &amp; propose", "hand off &amp; track"],
+)
+def test_workbench_html_carries_new_eyebrow(eyebrow: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert eyebrow in html, f"missing renamed eyebrow: {eyebrow}"
+
+
+# ─── 2. Old technical-noun copy removed ──────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "stale",
+    [
+        "<h2>Scenario Control</h2>",
+        "<h2>Spec Review Surface</h2>",
+        "<h2>Logic Circuit Surface</h2>",
+        ">control panel<",
+        ">document<",
+        ">circuit<",
+        "Waiting for control panel boot.",
+        "Waiting for document panel boot.",
+        "Waiting for circuit panel boot.",
+    ],
+)
+def test_workbench_html_does_not_carry_stale_column_title(stale: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale not in html, f"stale technical-noun copy still present: {stale}"
+
+
+# ─── 3. Underlying IDs / data attributes preserved ──────────────────
+#
+# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
+# panel ids, data-column tokens, data-annotation-surface tokens, and
+# status div ids are anchors for e2e selectors and JS boot wiring, so
+# they MUST stay stable through the rename.
+
+
+@pytest.mark.parametrize(
+    "anchor",
+    [
+        'id="workbench-control-panel"',
+        'id="workbench-document-panel"',
+        'id="workbench-circuit-panel"',
+        'data-column="control"',
+        'data-column="document"',
+        'data-column="circuit"',
+        'data-annotation-surface="control"',
+        'data-annotation-surface="document"',
+        'data-annotation-surface="circuit"',
+        'id="workbench-control-status"',
+        'id="workbench-document-status"',
+        'id="workbench-circuit-status"',
+    ],
+)
+def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"
+
+
+# ─── 4. JS boot status copy matches new column names ────────────────
+
+
+@pytest.mark.parametrize(
+    "boot_copy",
+    [
+        "Probe & Trace ready",
+        "Annotate & Propose ready",
+        "Hand off & Track ready",
+    ],
+)
+def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    assert boot_copy in js, f"workbench.js boot status missing: {boot_copy}"
+
+
+def test_workbench_js_boot_status_drops_stale_names() -> None:
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    # Old boot copy must NOT appear, otherwise the visible chrome and the
+    # status messages will disagree.
+    assert "Control panel ready" not in js
+    assert "Document panel ready" not in js
+    assert "Circuit panel ready" not in js
+
+
+# ─── 5. Live-served /workbench reflects the rename end-to-end ───────
+
+
+def test_workbench_route_serves_renamed_columns(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    # New copy
+    assert "Probe &amp; Trace · 探针与追踪" in html
+    assert "Annotate &amp; Propose · 标注与提案" in html
+    assert "Hand off &amp; Track · 移交与跟踪" in html
+    # Stable anchors still served
+    assert 'id="workbench-control-panel"' in html
+    assert 'data-column="circuit"' in html

exec
/bin/zsh -lc "nl -ba tests/test_workbench_dual_route.py | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-09 — dual-route fix locks /workbench shell vs /workbench/bundle split.
     2	
     3	Before E11-09 (PR #13), `/workbench` served a single 1078-line file with
     4	TWO `<h1>` headings: "Control Logic Workbench" (Epic-06..10 shell) +
     5	"Workbench Bundle 验收台" (legacy bundle). The product-identity split
     6	was 3 of 5 personas' BLOCKER #1 in E11-01 baseline review.
     7	
     8	After E11-09:
     9	- `/workbench` serves shell only (1 h1: "Control Logic Workbench")
    10	- `/workbench/bundle` serves the legacy bundle page (1 h1: "Workbench
    11	  Bundle 验收台")
    12	
    13	This test file locks the contract so any regression is caught at CI time
    14	rather than user time.
    15	"""
    16	
    17	from __future__ import annotations
    18	
    19	import http.client
    20	import re
    21	import threading
    22	from http.server import ThreadingHTTPServer
    23	from pathlib import Path
    24	
    25	import pytest
    26	
    27	from well_harness.demo_server import DemoRequestHandler
    28	
    29	
    30	REPO_ROOT = Path(__file__).resolve().parents[1]
    31	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    32	
    33	
    34	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    35	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    36	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    37	    thread.start()
    38	    return server, thread
    39	
    40	
    41	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    42	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    43	    connection.request("GET", path)
    44	    response = connection.getresponse()
    45	    body = response.read().decode("utf-8")
    46	    return response.status, body
    47	
    48	
    49	@pytest.mark.parametrize("path", ["/workbench", "/workbench.html", "/expert/workbench.html"])
    50	def test_workbench_route_serves_shell_only(path: str) -> None:
    51	    """`/workbench` (and aliases) serve the Epic-06..10 shell with exactly 1 h1."""
    52	    server, thread = _start_demo_server()
    53	    try:
    54	        status, body = _get(server, path)
    55	    finally:
    56	        server.shutdown()
    57	        server.server_close()
    58	        thread.join(timeout=2)
    59	
    60	    assert status == 200
    61	    assert "<title>Control Logic Workbench</title>" in body
    62	    h1_count = len(re.findall(r"<h1[ >]", body))
    63	    assert h1_count == 1, f"{path} must have exactly 1 h1, found {h1_count}"
    64	    assert "Control Logic Workbench</h1>" in body
    65	    # Bundle h1 must NOT leak onto the shell page
    66	    assert "Workbench Bundle 验收台</h1>" not in body
    67	    # Shell-essential ids still present (regression guard)
    68	    assert 'id="workbench-control-panel"' in body
    69	    assert 'id="approval-center-entry"' in body
    70	
    71	
    72	@pytest.mark.parametrize("path", ["/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"])
    73	def test_workbench_bundle_route_serves_bundle_only(path: str) -> None:
    74	    """`/workbench/bundle` (and aliases) serve the legacy 验收台 with exactly 1 h1."""
    75	    server, thread = _start_demo_server()
    76	    try:
    77	        status, body = _get(server, path)
    78	    finally:
    79	        server.shutdown()
    80	        server.server_close()
    81	        thread.join(timeout=2)
    82	
    83	    assert status == 200
    84	    assert "<title>Well Harness Workbench Bundle 验收台</title>" in body
    85	    h1_count = len(re.findall(r"<h1[ >]", body))
    86	    assert h1_count == 1, f"{path} must have exactly 1 h1, found {h1_count}"
    87	    assert 'id="workbench-page-title"' in body
    88	    assert "Workbench Bundle 验收台</h1>" in body
    89	    # Shell h1 must NOT leak onto the bundle page
    90	    assert "Control Logic Workbench</h1>" not in body
    91	    # Bundle-essential UI present (regression guard)
    92	    assert 'data-workbench-preset="ready_archived"' in body
    93	    assert "一键预设验收卡" in body
    94	
    95	
    96	def test_shell_and_bundle_files_share_no_h1() -> None:
    97	    """Static-file invariant: each file has exactly 1 h1 and they don't overlap."""
    98	    shell_html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    99	    bundle_html = (STATIC_DIR / "workbench_bundle.html").read_text(encoding="utf-8")
   100	
   101	    assert len(re.findall(r"<h1[ >]", shell_html)) == 1, "shell file must have exactly 1 h1"
   102	    assert len(re.findall(r"<h1[ >]", bundle_html)) == 1, "bundle file must have exactly 1 h1"
   103	    assert "Control Logic Workbench</h1>" in shell_html
   104	    assert "Workbench Bundle 验收台</h1>" in bundle_html
   105	    # Cross-file leakage guard
   106	    assert "Workbench Bundle 验收台</h1>" not in shell_html
   107	    assert "Control Logic Workbench</h1>" not in bundle_html
   108	
   109	
   110	def test_workbench_js_has_bundle_sentinel_guard() -> None:
   111	    """E11-09 R1 BLOCKER fix: workbench.js is shared between /workbench (shell)
   112	    and /workbench/bundle (bundle) but its DOMContentLoaded handler used to
   113	    unconditionally bind bundle-only elements (e.g. #workbench-packet-json,
   114	    #load-reference-packet, #run-workbench-bundle), throwing
   115	    `Cannot read properties of null (reading 'addEventListener')` on the
   116	    shell page.
   117	
   118	    The fix is a sentinel guard that detects whether bundle DOM is present
   119	    by probing for `#workbench-packet-json` (the bundle's textarea input),
   120	    early-returning on the shell page before installToolbarHandlers /

exec
/bin/zsh -lc "nl -ba tests/test_workbench_annotation_static.py | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	from pathlib import Path
     2	
     3	
     4	PROJECT_ROOT = Path(__file__).resolve().parents[1]
     5	
     6	
     7	def test_workbench_loads_annotation_overlay_and_four_tools():
     8	    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
     9	
    10	    assert '<script src="/annotation_overlay.js"' in html
    11	    assert 'id="workbench-annotation-toolbar"' in html
    12	    for tool in ["point", "area", "link", "text-range"]:
    13	        assert f'data-annotation-tool="{tool}"' in html
    14	
    15	
    16	def test_workbench_exposes_three_annotation_surfaces():
    17	    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
    18	
    19	    assert 'id="workbench-control-panel"' in html
    20	    assert 'data-annotation-surface="control"' in html
    21	    assert 'id="workbench-document-panel"' in html
    22	    assert 'data-annotation-surface="document"' in html
    23	    assert 'id="workbench-circuit-panel"' in html
    24	    assert 'data-annotation-surface="circuit"' in html
    25	
    26	
    27	def test_annotation_overlay_js_exports_bootstrap_and_draft_contracts():
    28	    script = (PROJECT_ROOT / "src/well_harness/static/annotation_overlay.js").read_text(encoding="utf-8")
    29	
    30	    assert "WorkbenchAnnotationOverlay" in script
    31	    assert "createAnnotationDraft" in script
    32	    assert "installAnnotationOverlay" in script
    33	    for tool in ["point", "area", "link", "text-range"]:
    34	        assert tool in script

exec
/bin/zsh -lc "nl -ba tests/test_workbench_shell.py | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	from __future__ import annotations
     2	
     3	import http.client
     4	import threading
     5	from html.parser import HTMLParser
     6	from pathlib import Path
     7	
     8	from http.server import ThreadingHTTPServer
     9	
    10	from well_harness.demo_server import DemoRequestHandler
    11	
    12	
    13	REPO_ROOT = Path(__file__).resolve().parents[1]
    14	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    15	
    16	
    17	class IdCollector(HTMLParser):
    18	    def __init__(self) -> None:
    19	        super().__init__()
    20	        self.ids: set[str] = set()
    21	        self.data_attrs: dict[str, dict[str, str]] = {}
    22	
    23	    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
    24	        attr_map = {key: value or "" for key, value in attrs}
    25	        element_id = attr_map.get("id")
    26	        if element_id:
    27	            self.ids.add(element_id)
    28	            self.data_attrs[element_id] = {
    29	                key: value for key, value in attr_map.items() if key.startswith("data-")
    30	            }
    31	
    32	
    33	def parse_workbench_ids() -> IdCollector:
    34	    parser = IdCollector()
    35	    parser.feed((STATIC_DIR / "workbench.html").read_text(encoding="utf-8"))
    36	    return parser
    37	
    38	
    39	def start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    40	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    41	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    42	    thread.start()
    43	    return server, thread
    44	
    45	
    46	def test_workbench_route_serves_shell() -> None:
    47	    server, thread = start_demo_server()
    48	    try:
    49	        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    50	        connection.request("GET", "/workbench")
    51	        response = connection.getresponse()
    52	        html = response.read().decode("utf-8")
    53	    finally:
    54	        server.shutdown()
    55	        server.server_close()
    56	        thread.join(timeout=2)
    57	
    58	    assert response.status == 200
    59	    assert "Control Logic Workbench" in html
    60	    assert 'id="workbench-control-panel"' in html
    61	
    62	
    63	def test_workbench_shell_has_three_independent_columns() -> None:
    64	    ids = parse_workbench_ids().ids
    65	
    66	    assert "workbench-control-panel" in ids
    67	    assert "workbench-document-panel" in ids
    68	    assert "workbench-circuit-panel" in ids
    69	
    70	
    71	def test_workbench_shell_has_identity_ticket_and_system_topbar() -> None:
    72	    ids = parse_workbench_ids().ids
    73	
    74	    assert "workbench-topbar" in ids
    75	    assert "workbench-identity" in ids
    76	    assert "workbench-ticket" in ids
    77	    assert "workbench-system-select" in ids
    78	
    79	
    80	def test_workbench_shell_has_annotation_inbox_skeleton() -> None:
    81	    ids = parse_workbench_ids().ids
    82	
    83	    assert "annotation-inbox" in ids
    84	    assert "annotation-inbox-list" in ids
    85	
    86	
    87	def test_workbench_shell_has_kogami_approval_entry() -> None:
    88	    parser = parse_workbench_ids()
    89	
    90	    assert "approval-center-entry" in parser.ids
    91	    assert parser.data_attrs["approval-center-entry"].get("data-role") == "KOGAMI"
    92	
    93	
    94	def test_workbench_javascript_exposes_failure_isolation_hooks() -> None:
    95	    script = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    96	
    97	    assert "bootWorkbenchControlPanel" in script
    98	    assert "bootWorkbenchDocumentPanel" in script
    99	    assert "bootWorkbenchCircuitPanel" in script
   100	    assert "bootWorkbenchColumnSafely" in script

exec
/bin/zsh -lc "nl -ba tests/test_workbench_approval_center.py | sed -n '1,140p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	import json
     2	from pathlib import Path
     3	
     4	import pytest
     5	
     6	from well_harness.workbench.approval import ApprovalCenter, WorkbenchPermissionError
     7	from well_harness.workbench.proposals import build_annotation_proposal
     8	
     9	
    10	PROJECT_ROOT = Path(__file__).resolve().parents[1]
    11	
    12	
    13	def _proposal() -> dict:
    14	    return build_annotation_proposal(
    15	        proposal_id="prop_approval_001",
    16	        tool="point",
    17	        surface="control",
    18	        anchor={"x": 0.2, "y": 0.4},
    19	        note="Approve review of the control state handoff.",
    20	        author="engineer-a",
    21	        ticket_id="WB-E08-APPROVAL",
    22	        system_id="thrust-reverser",
    23	        created_at="2026-04-25T09:00:00Z",
    24	    )
    25	
    26	
    27	def _read_events(path: Path) -> list[dict]:
    28	    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    29	
    30	
    31	def test_approval_center_submits_proposal_and_appends_audit_event(tmp_path):
    32	    audit_path = tmp_path / "audit/events.jsonl"
    33	    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)
    34	
    35	    result = center.submit(_proposal(), actor="engineer-a")
    36	
    37	    assert result["status"] == "pending"
    38	    assert result["proposal_id"] == "prop_approval_001"
    39	    assert center.pending()[0]["id"] == "prop_approval_001"
    40	    events = _read_events(audit_path)
    41	    assert events[-1]["type"] == "proposal.submitted"
    42	    assert events[-1]["proposal_id"] == "prop_approval_001"
    43	    assert events[-1]["event_hash"]
    44	
    45	
    46	def test_approval_center_rejects_non_kogami_triage(tmp_path):
    47	    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=tmp_path / "audit/events.jsonl")
    48	    center.submit(_proposal(), actor="engineer-a")
    49	
    50	    with pytest.raises(WorkbenchPermissionError, match="Kogami"):
    51	        center.accept("prop_approval_001", actor="engineer-a")
    52	
    53	
    54	def test_approval_center_accepts_and_rejects_with_hash_chain(tmp_path):
    55	    audit_path = tmp_path / "audit/events.jsonl"
    56	    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)
    57	    center.submit(_proposal(), actor="engineer-a")
    58	
    59	    accepted = center.accept("prop_approval_001", actor="Kogami", reason="Scope is correct.")
    60	    events = _read_events(audit_path)
    61	
    62	    assert accepted["status"] == "accepted"
    63	    assert events[-1]["type"] == "proposal.accepted"
    64	    assert events[-1]["previous_hash"] == events[-2]["event_hash"]
    65	
    66	    second = build_annotation_proposal(
    67	        proposal_id="prop_approval_002",
    68	        tool="text-range",
    69	        surface="document",
    70	        anchor={"selector": "#workbench-document-panel", "start_offset": 0, "end_offset": 12, "text_quote": "Reference"},
    71	        note="Reject this duplicate document note.",
    72	        author="engineer-a",
    73	        ticket_id="WB-E08-APPROVAL",
    74	        system_id="thrust-reverser",
    75	        created_at="2026-04-25T09:01:00Z",
    76	    )
    77	    center.submit(second, actor="engineer-a")
    78	    rejected = center.reject("prop_approval_002", actor="Kogami", reason="Duplicate.")
    79	
    80	    assert rejected["status"] == "rejected"
    81	    assert _read_events(audit_path)[-1]["type"] == "proposal.rejected"
    82	
    83	
    84	def test_workbench_static_approval_center_exposes_triage_lanes():
    85	    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
    86	
    87	    assert 'id="approval-center-panel"' in html
    88	    assert 'data-approval-role="KOGAMI"' in html
    89	    for lane in ["pending", "accept", "reject"]:
    90	        assert f'data-approval-lane="{lane}"' in html

exec
/bin/zsh -lc "rg -n \"workbench-control-panel|workbench-document-panel|workbench-circuit-panel|data-column=\\\"control\\\"|data-column=\\\"document\\\"|data-column=\\\"circuit\\\"|/workbench\" tests/e2e tests" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_archive_integrity.py:201:            "$schema": "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
tests/test_workbench_column_rename.py:116:        'id="workbench-control-panel"',
tests/test_workbench_column_rename.py:117:        'id="workbench-document-panel"',
tests/test_workbench_column_rename.py:118:        'id="workbench-circuit-panel"',
tests/test_workbench_column_rename.py:119:        'data-column="control"',
tests/test_workbench_column_rename.py:120:        'data-column="document"',
tests/test_workbench_column_rename.py:121:        'data-column="circuit"',
tests/test_workbench_column_rename.py:160:# ─── 5. Live-served /workbench reflects the rename end-to-end ───────
tests/test_workbench_column_rename.py:164:    status, html = _get(server, "/workbench")
tests/test_workbench_column_rename.py:171:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_column_rename.py:172:    assert 'data-column="circuit"' in html
tests/test_workbench_start.py:1:"""E11-02 — onboarding landing /workbench/start.
tests/test_workbench_start.py:5:* `/workbench/start` returns a 200 HTML response with a 5-persona +
tests/test_workbench_start.py:9:* Each tile deep-links into `/workbench` with an `intent=` query
tests/test_workbench_start.py:12:* Arbitrary `?intent=` payloads must NOT be reflected by `/workbench`.
tests/test_workbench_start.py:89:@pytest.mark.parametrize("path", ["/workbench/start", "/workbench/start.html"])
tests/test_workbench_start.py:112:        connection.request("GET", "/workbench_start.css")
tests/test_workbench_start.py:164:        assert href.startswith("/workbench?intent="), (
tests/test_workbench_start.py:165:            f"{tile_id}: href {href!r} must deep-link into /workbench with intent= query"
tests/test_workbench_start.py:193:    """R1-F4 verbatim: `/workbench` must not reflect arbitrary intent= payloads."""
tests/test_workbench_start.py:197:        connection.request("GET", "/workbench?intent=%3Csvg%20onload%3Dalert(1)%3E")
tests/test_pr_close_loop.py:14:        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
tests/test_pr_close_loop.py:15:        "Generated Prompt": "## anchor\nproposal\n\n## scope\nsrc/well_harness/workbench/**",
tests/test_pr_close_loop.py:37:    assert extract_changed_files(_diff_for("src/well_harness/workbench/pr_review.py")) == [
tests/test_pr_close_loop.py:38:        "src/well_harness/workbench/pr_review.py"
tests/test_pr_close_loop.py:43:    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/workbench/pr_review.py"))
tests/test_pr_close_loop.py:46:    assert report["changed_files"] == ["src/well_harness/workbench/pr_review.py"]
tests/test_pr_close_loop.py:59:    report = review_pr_diff(ticket, _diff_for("src/well_harness/workbench/pr_review.py"))
tests/test_workbench_approval_center.py:70:        anchor={"selector": "#workbench-document-panel", "start_offset": 0, "end_offset": 12, "text_quote": "Reference"},
tests/test_workbench_approval_center.py:85:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
tests/test_workbench_dual_route.py:1:"""E11-09 — dual-route fix locks /workbench shell vs /workbench/bundle split.
tests/test_workbench_dual_route.py:3:Before E11-09 (PR #13), `/workbench` served a single 1078-line file with
tests/test_workbench_dual_route.py:9:- `/workbench` serves shell only (1 h1: "Control Logic Workbench")
tests/test_workbench_dual_route.py:10:- `/workbench/bundle` serves the legacy bundle page (1 h1: "Workbench
tests/test_workbench_dual_route.py:49:@pytest.mark.parametrize("path", ["/workbench", "/workbench.html", "/expert/workbench.html"])
tests/test_workbench_dual_route.py:51:    """`/workbench` (and aliases) serve the Epic-06..10 shell with exactly 1 h1."""
tests/test_workbench_dual_route.py:68:    assert 'id="workbench-control-panel"' in body
tests/test_workbench_dual_route.py:72:@pytest.mark.parametrize("path", ["/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"])
tests/test_workbench_dual_route.py:74:    """`/workbench/bundle` (and aliases) serve the legacy 验收台 with exactly 1 h1."""
tests/test_workbench_dual_route.py:111:    """E11-09 R1 BLOCKER fix: workbench.js is shared between /workbench (shell)
tests/test_workbench_dual_route.py:112:    and /workbench/bundle (bundle) but its DOMContentLoaded handler used to
tests/test_workbench_dual_route.py:156:    #    must appear BEFORE the guard so they still run on /workbench.
tests/test_workbench_dual_route.py:160:        "bootWorkbenchShell must run on /workbench (before bundle guard)"
tests/test_workbench_dual_route.py:163:        "installViewModeHandlers must run on /workbench (before bundle guard)"
tests/test_p43_authority_contract.py:6:removed in 2026-04-25 (PROMOTE per `docs/workbench/xpassed-audit-20260425.md`)
tests/test_workbench_archive_manifest_schema.py:39:        self.assertIn("docs/json_schema/workbench_archive_manifest_v1.schema.json", result.stdout)
tests/test_workbench_archive_manifest_schema.py:61:        self.assertEqual("docs/json_schema/workbench_archive_manifest_v1.schema.json", payload["schema_path"])
tests/test_workbench_archive_manifest_schema.py:80:        self.assertEqual("docs/json_schema/workbench_archive_manifest_v1.schema.json", payload["schema_path"])
tests/test_workbench_wow_starters.py:3:Locks the contract for the top-of-/workbench wow starter cards so future
tests/test_workbench_wow_starters.py:8:  1. /workbench static HTML carries the three starter cards (one per
tests/test_workbench_wow_starters.py:260:    # Positive claim (must appear): cards are live on /workbench.
tests/test_workbench_wow_starters.py:293:    """Live-served /workbench page includes the wow starters section."""
tests/test_workbench_wow_starters.py:294:    status, html = _get(server, "/workbench")
tests/test_demo.py:935:        # from /workbench to /workbench/bundle. /workbench is now the
tests/test_demo.py:941:            connection.request("GET", "/workbench/bundle")
tests/test_demo.py:980:        # workbench_bundle.html (served at /workbench/bundle).
tests/test_demo.py:1182:        # which moved from /workbench to /workbench/bundle.
tests/test_demo.py:1221:            connection.request("GET", "/api/workbench/bootstrap")
tests/test_demo.py:1232:        self.assertIn("artifacts/workbench-bundles", payload["default_archive_root"])
tests/test_demo.py:1316:                    connection.request("GET", "/api/workbench/recent-archives")
tests/test_demo.py:1370:                        "/api/workbench/bundle",
tests/test_demo.py:1468:                    "/api/workbench/archive-restore",
tests/test_demo.py:1490:        self.assertIn("artifacts/workbench-bundles", payload["default_archive_root"])
tests/test_demo.py:1504:                "/api/workbench/repair",
tests/test_workbench_trust_affordance.py:120:    """Live-served /workbench HTML contains chip + banner + copy strings."""
tests/test_workbench_trust_affordance.py:123:        status, body = _get(server, "/workbench")
tests/test_workbench_trust_affordance.py:141:    """`/workbench/bundle` (legacy 验收台) must NOT contain the shell-only chip/banner."""
tests/test_workbench_trust_affordance.py:144:        status, body = _get(server, "/workbench/bundle")
tests/test_workbench_prompt_ticket_auth.py:19:        anchor={"selector": "#workbench-document-panel", "href": "https://example.test/spec"},
tests/test_workbench_prompt_ticket_auth.py:32:        scope_files=["src/well_harness/workbench/**", "docs/workbench/**"],
tests/test_workbench_prompt_ticket_auth.py:41:    assert "src/well_harness/workbench/**" in prompt
tests/test_workbench_prompt_ticket_auth.py:48:        scope_files=["src/well_harness/workbench/**"],
tests/test_workbench_prompt_ticket_auth.py:67:        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
tests/test_workbench_prompt_ticket_auth.py:73:        changed_files=["src/well_harness/workbench/prompting.py", "docs/workbench/HANDOVER.md"],
tests/test_workbench_prompt_ticket_auth.py:78:        validate_push_attempt(ticket, engineer="other-agent", changed_files=["src/well_harness/workbench/prompting.py"])
tests/test_workbench_shell.py:50:        connection.request("GET", "/workbench")
tests/test_workbench_shell.py:60:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_shell.py:66:    assert "workbench-control-panel" in ids
tests/test_workbench_shell.py:67:    assert "workbench-document-panel" in ids
tests/test_workbench_shell.py:68:    assert "workbench-circuit-panel" in ids
tests/test_workbench_bundle_schema.py:39:        self.assertIn("docs/json_schema/workbench_bundle_v1.schema.json", result.stdout)
tests/test_workbench_bundle_schema.py:61:        self.assertEqual("docs/json_schema/workbench_bundle_v1.schema.json", payload["schema_path"])
tests/test_workbench_bundle_schema.py:80:        self.assertEqual("docs/json_schema/workbench_bundle_v1.schema.json", payload["schema_path"])
tests/test_workbench_bundle.py:215:                "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
tests/test_workbench_bundle.py:233:            self.assertIn("https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json", saved_summary)
tests/test_workbench_bundle.py:327:            "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
tests/test_workbench_bundle.py:393:            "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
tests/test_workbench_bundle.py:433:        self.assertIn("schema: https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json", text)
tests/test_workbench_annotation_static.py:8:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
tests/test_workbench_annotation_static.py:17:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
tests/test_workbench_annotation_static.py:19:    assert 'id="workbench-control-panel"' in html
tests/test_workbench_annotation_static.py:21:    assert 'id="workbench-document-panel"' in html
tests/test_workbench_annotation_static.py:23:    assert 'id="workbench-circuit-panel"' in html

exec
/bin/zsh -lc "python - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
try:
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench')
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    print(f'STATUS /workbench: {resp.status}')
    for needle in [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'id=\"workbench-control-panel\"',
        'data-column=\"document\"',
        'id=\"workbench-circuit-status\"',
    ]:
        print(f'{needle}: {needle in body}')
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench.js')
    resp = conn.getresponse()
    js = resp.read().decode('utf-8')
    print(f'STATUS /workbench.js: {resp.status}')
    for needle in [
        'Probe & Trace ready. Scenario actions are staged for E07+.',
        'Annotate & Propose ready. Text-range annotation arrives in E07.',
        'Hand off & Track ready. Overlay annotation arrives in E07.',
    ]:
        print(f'{needle}: {needle in js}')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_column_rename.py tests/test_workbench_shell.py tests/test_workbench_dual_route.py tests/test_workbench_annotation_static.py tests/test_workbench_approval_center.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 4409ms:
.....................................................                    [100%]
53 passed in 4.15s

codex
实时探针第一次被环境绊住了：这台机器没有 `python`，只有 `python3`。我用同样的探针改跑 `python3`，并顺手把正在跑的定向 pytest 结果收回来。
exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
try:
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench')
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    print(f'STATUS /workbench: {resp.status}')
    for needle in [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'id=\"workbench-control-panel\"',
        'data-column=\"document\"',
        'id=\"workbench-circuit-status\"',
    ]:
        print(f'{needle}: {needle in body}')
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench.js')
    resp = conn.getresponse()
    js = resp.read().decode('utf-8')
    print(f'STATUS /workbench.js: {resp.status}')
    for needle in [
        'Probe & Trace ready. Scenario actions are staged for E07+.',
        'Annotate & Propose ready. Text-range annotation arrives in E07.',
        'Hand off & Track ready. Overlay annotation arrives in E07.',
    ]:
        print(f'{needle}: {needle in js}')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 612ms:
STATUS /workbench: 200
Probe &amp; Trace · 探针与追踪: False
Annotate &amp; Propose · 标注与提案: False
Hand off &amp; Track · 移交与跟踪: False
id="workbench-control-panel": False
data-column="document": False
id="workbench-circuit-status": False
STATUS /workbench.js: 200
Probe & Trace ready. Scenario actions are staged for E07+.: False
Annotate & Propose ready. Text-range annotation arrives in E07.: False
Hand off & Track ready. Overlay annotation arrives in E07.: False

codex
出现了一个实打实的边界异常：源码和定向测试都指向“已改名”，但我直接起 `DemoRequestHandler` 探 `/workbench` 与 `/workbench.js`，返回体里这些新字符串一个都不在。这个不是文案 nit，而是“live route 是否真的在吃这份文件”的契约问题，我转成一次最小化路径调试。
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/systematic-debugging/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

5. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Use the `superpowers:test-driven-development` skill for writing proper failing tests

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with your human partner before attempting more fixes**

   This is NOT a failed hypothesis - this is a wrong architecture.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"

exec
/bin/zsh -lc "rg -n \"workbench.html|workbench.js|/workbench|/workbench.js|static\" src/well_harness/demo_server.py src/well_harness -g '"'!src/well_harness/static/*'"'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/demo_server.py:48:STATIC_DIR = Path(__file__).with_name("static")
src/well_harness/demo_server.py:70:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
src/well_harness/demo_server.py:71:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
src/well_harness/demo_server.py:72:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
src/well_harness/demo_server.py:73:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
src/well_harness/demo_server.py:74:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
src/well_harness/demo_server.py:201:    """Serve the static demo shell and a thin JSON API around DemoAnswer."""
src/well_harness/demo_server.py:211:            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
src/well_harness/demo_server.py:231:            self._serve_static("index.html")
src/well_harness/demo_server.py:235:            self._serve_static("demo.html")
src/well_harness/demo_server.py:238:        if parsed.path in ("/workbench/start", "/workbench/start.html"):
src/well_harness/demo_server.py:239:            self._serve_static("workbench_start.html")
src/well_harness/demo_server.py:242:        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
src/well_harness/demo_server.py:243:            self._serve_static("workbench_bundle.html")
src/well_harness/demo_server.py:246:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
src/well_harness/demo_server.py:247:            self._serve_static("workbench.html")
src/well_harness/demo_server.py:252:            self._serve_static(relative_path)
src/well_harness/demo_server.py:566:    def _serve_static(self, relative_path: str):
src/well_harness/demo_server.py:567:        static_root = STATIC_DIR.resolve()
src/well_harness/demo_server.py:568:        target_path = (static_root / relative_path).resolve()
src/well_harness/demo_server.py:569:        # Path must live inside static_root (traversal guard) and exist as a file.
src/well_harness/demo_server.py:570:        # Phase UI-F (2026-04-22): allow nested static paths like
src/well_harness/demo_server.py:573:            target_path.relative_to(static_root)
src/well_harness/demo_server.py:48:STATIC_DIR = Path(__file__).with_name("static")
src/well_harness/demo_server.py:70:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
src/well_harness/demo_server.py:71:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
src/well_harness/demo_server.py:72:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
src/well_harness/demo_server.py:73:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
src/well_harness/demo_server.py:74:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
src/well_harness/demo_server.py:201:    """Serve the static demo shell and a thin JSON API around DemoAnswer."""
src/well_harness/demo_server.py:211:            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
src/well_harness/demo_server.py:231:            self._serve_static("index.html")
src/well_harness/demo_server.py:235:            self._serve_static("demo.html")
src/well_harness/demo_server.py:238:        if parsed.path in ("/workbench/start", "/workbench/start.html"):
src/well_harness/demo_server.py:239:            self._serve_static("workbench_start.html")
src/well_harness/demo_server.py:242:        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
src/well_harness/demo_server.py:243:            self._serve_static("workbench_bundle.html")
src/well_harness/demo_server.py:246:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
src/well_harness/demo_server.py:247:            self._serve_static("workbench.html")
src/well_harness/demo_server.py:252:            self._serve_static(relative_path)
src/well_harness/demo_server.py:566:    def _serve_static(self, relative_path: str):
src/well_harness/demo_server.py:567:        static_root = STATIC_DIR.resolve()
src/well_harness/demo_server.py:568:        target_path = (static_root / relative_path).resolve()
src/well_harness/demo_server.py:569:        # Path must live inside static_root (traversal guard) and exist as a file.
src/well_harness/demo_server.py:570:        # Phase UI-F (2026-04-22): allow nested static paths like
src/well_harness/demo_server.py:573:            target_path.relative_to(static_root)
src/well_harness/workbench/prompting.py:13:    "src/well_harness/workbench/**",
src/well_harness/workbench/prompting.py:14:    "src/well_harness/static/workbench.*",
src/well_harness/workbench/prompting.py:15:    "src/well_harness/static/annotation_overlay.js",
src/well_harness/workbench/prompting.py:17:    "docs/workbench/**",
src/well_harness/timeline_engine/schema.py:111:    # Flat static fault_schedule (backward compat shim for pre-existing
src/well_harness/timeline_engine/schema.py:112:    # static fault_injections). Equivalent to inject_fault events with
src/well_harness/switches.py:32:    @staticmethod
src/well_harness/workbench_bundle.py:28:WORKBENCH_BUNDLE_SCHEMA_ID = "https://well-harness.local/json_schema/workbench_bundle_v1.schema.json"
src/well_harness/workbench_bundle.py:31:ARCHIVE_MANIFEST_SCHEMA_ID = "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json"
src/well_harness/timeline_engine/validator.py:96:def _parse_static_schedule_entry(
src/well_harness/timeline_engine/validator.py:161:        _parse_static_schedule_entry(entry, float(duration_s), i)
src/well_harness/timeline_engine/player.py:232:    @staticmethod
src/well_harness/timeline_engine/player.py:289:    @staticmethod
src/well_harness/adapters/c919_etras_frozen_v1/lock_status_aggregator.py:13:    @staticmethod
src/well_harness/adapters/c919_etras_frozen_v1/safety_interlock_manager.py:16:    @staticmethod
src/well_harness/adapters/c919_etras_frozen_v1/safety_interlock_manager.py:20:    @staticmethod
src/well_harness/adapters/c919_etras_frozen_v1/safety_interlock_manager.py:28:    @staticmethod
src/well_harness/tools/generate_adapter.py:145:    L("    @staticmethod")
src/well_harness/tools/generate_adapter.py:155:    L("    @staticmethod")
src/well_harness/tools/generate_adapter.py:165:    L("    @staticmethod")
src/well_harness/tools/generate_adapter.py:490:        lines.append("    @staticmethod")
src/well_harness/tools/generate_adapter.py:498:        lines.append("    @staticmethod")
src/well_harness/tools/generate_adapter.py:512:        lines.append("    @staticmethod")
src/well_harness/tools/generate_adapter.py:532:    """Build the _build_logic_rules static helper (returns the rules structure)."""

exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
try:
    for path in ['/workbench', '/workbench.js']:
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
        conn.request('GET', path)
        resp = conn.getresponse()
        body = resp.read().decode('utf-8', errors='replace')
        print(f'===== {path} {resp.status} =====')
        print(body[:1200])
        print('LEN', len(body))
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 601ms:
===== /workbench 200 =====
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
LEN 11888
===== /workbench.js 200 =====
const workbenchBootstrapPath = "/api/workbench/bootstrap";
const workbenchBundlePath = "/api/workbench/bundle";
const workbenchRepairPath = "/api/workbench/repair";
const workbenchArchiveRestorePath = "/api/workbench/archive-restore";
const workbenchRecentArchivesPath = "/api/workbench/recent-archives";
const workbenchPacketWorkspaceStorageKey = "well-harness-workbench-packet-workspace-v1";
const draftDesignStateKey = "draft_design_state";
const workbenchPersistedFieldIds = [
  "workbench-scenario-id",
  "workbench-fault-mode-id",
  "workbench-sample-period",
  "workbench-archive-toggle",
  "workbench-archive-manifest-path",
  "workbench-handoff-note",
  "workbench-observed-symptoms",
  "workbench-evidence-links",
  "workbench-root-cause",
  "workbench-repair-action",
  "workbench-validation-after-fix",
  "workbench-residual-risk",
  "workbench-logic-change",
  "workbench-reliability-gain",
  "workbench-guardrail-note",
];

const defaultReferenceResolution = {
  rootCause: "Pressure sensor bias was confirmed during troubleshooting.",
  repairAction: "Recalibrated the sensor path.",
  validationAfterFix: "Acceptance replay completed after the repair.",
  residualRisk: "Watch for fut
LEN 139679

codex
根因方向已经浮出来了：`DemoRequestHandler` 很可能不是从当前 worktree 的 `src/` 导入，而是命中了机器上另一个 `well_harness` 包。下一步我只验证两件事：当前 `python3` 的实际模块来源，以及 pytest 为什么还能通过。
exec
/bin/zsh -lc 'rg -n "pythonpath|pytest.ini_options|tool.pytest|addopts" pyproject.toml pytest.ini setup.cfg tox.ini' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: pytest.ini: No such file or directory (os error 2)
rg: setup.cfg: No such file or directory (os error 2)
rg: tox.ini: No such file or directory (os error 2)
pyproject.toml:32:[tool.pytest.ini_options]
pyproject.toml:34:addopts = "-m 'not e2e'"
pyproject.toml:40:pythonpath = ["src", "."]

exec
/bin/zsh -lc "nl -ba pyproject.toml | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "python3 - <<'PY'
import sys
import well_harness
import well_harness.demo_server as ds
print('well_harness.__file__ =', well_harness.__file__)
print('demo_server.__file__ =', ds.__file__)
print('sys.path[:8] =')
for item in sys.path[:8]:
    print(item)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
well_harness.__file__ = /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/__init__.py
demo_server.__file__ = /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py
sys.path[:8] =

/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python39.zip
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload
/Users/Zhuanz/Library/Python/3.9/lib/python/site-packages
/Users/Zhuanz/Desktop/cfd-harness-unified/src
/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages

codex
根因确认了：我第一次 live probe 误命中了机器上另一个 checkout 的 `well_harness`，不是这个 PR 的 worktree。这里的 `pytest` 能过，是因为 [pyproject.toml](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/pyproject.toml:32) 给 pytest 注入了 `pythonpath = ["src", "."]`。我现在用同样的导入前缀把 live probe 重新跑一遍。
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '230,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
/bin/zsh -lc "PYTHONPATH=src:. python3 - <<'PY'
import sys
import well_harness
import well_harness.demo_server as ds
print('well_harness.__file__ =', well_harness.__file__)
print('demo_server.__file__ =', ds.__file__)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
well_harness.__file__ = /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/__init__.py
demo_server.__file__ = /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py

exec
/bin/zsh -lc "PYTHONPATH=src:. python3 - <<'PY'
import http.client, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
try:
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench')
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    print(f'STATUS /workbench: {resp.status}')
    for needle in [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'id=\"workbench-control-panel\"',
        'data-column=\"document\"',
        'id=\"workbench-circuit-status\"',
    ]:
        print(f'{needle}: {needle in body}')
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    conn.request('GET', '/workbench.js')
    resp = conn.getresponse()
    js = resp.read().decode('utf-8')
    print(f'STATUS /workbench.js: {resp.status}')
    for needle in [
        'Probe & Trace ready. Scenario actions are staged for E07+.',
        'Annotate & Propose ready. Text-range annotation arrives in E07.',
        'Hand off & Track ready. Overlay annotation arrives in E07.',
    ]:
        print(f'{needle}: {needle in js}')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 568ms:
STATUS /workbench: 200
Probe &amp; Trace · 探针与追踪: True
Annotate &amp; Propose · 标注与提案: True
Hand off &amp; Track · 移交与跟踪: True
id="workbench-control-panel": True
data-column="document": True
id="workbench-circuit-status": True
STATUS /workbench.js: 200
Probe & Trace ready. Scenario actions are staged for E07+.: True
Annotate & Propose ready. Text-range annotation arrives in E07.: True
Hand off & Track ready. Overlay annotation arrives in E07.: True

exec
/bin/zsh -lc "nl -ba tests/test_workbench_dual_route.py | sed -n '110,175p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   110	def test_workbench_js_has_bundle_sentinel_guard() -> None:
   111	    """E11-09 R1 BLOCKER fix: workbench.js is shared between /workbench (shell)
   112	    and /workbench/bundle (bundle) but its DOMContentLoaded handler used to
   113	    unconditionally bind bundle-only elements (e.g. #workbench-packet-json,
   114	    #load-reference-packet, #run-workbench-bundle), throwing
   115	    `Cannot read properties of null (reading 'addEventListener')` on the
   116	    shell page.
   117	
   118	    The fix is a sentinel guard that detects whether bundle DOM is present
   119	    by probing for `#workbench-packet-json` (the bundle's textarea input),
   120	    early-returning on the shell page before installToolbarHandlers /
   121	    updateWorkflowUI / loadBootstrapPayload run.
   122	
   123	    This test is a structural-static check — it does NOT execute JS. A real
   124	    JS-boot smoke test (jsdom or headless browser) is deferred to E11-11
   125	    e2e coverage sub-phase per v2.3 §C-Opus governance-weight calibration.
   126	    """
   127	    js_text = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   128	
   129	    # 1. Sentinel probe must be present
   130	    assert 'getElementById("workbench-packet-json")' in js_text, (
   131	        "missing E11-09 sentinel probe — bundle/shell discriminator removed?"
   132	    )
   133	
   134	    # 2. Early-return must be present
   135	    assert "if (!onBundlePage)" in js_text, (
   136	        "missing E11-09 onBundlePage early-return guard"
   137	    )
   138	
   139	    # 3. Guard must precede the bundle installers in DOMContentLoaded handler
   140	    sentinel_pos = js_text.index('getElementById("workbench-packet-json")')
   141	    install_toolbar_call_pos = js_text.index("installToolbarHandlers();", sentinel_pos)
   142	    update_workflow_call_pos = js_text.index("updateWorkflowUI();", sentinel_pos)
   143	    load_bootstrap_call_pos = js_text.index("loadBootstrapPayload()", sentinel_pos)
   144	
   145	    assert sentinel_pos < install_toolbar_call_pos, (
   146	        "E11-09 guard must precede installToolbarHandlers"
   147	    )
   148	    assert sentinel_pos < update_workflow_call_pos, (
   149	        "E11-09 guard must precede updateWorkflowUI"
   150	    )
   151	    assert sentinel_pos < load_bootstrap_call_pos, (
   152	        "E11-09 guard must precede loadBootstrapPayload"
   153	    )
   154	
   155	    # 4. Shell-essential boot calls (bootWorkbenchShell, installViewModeHandlers)
   156	    #    must appear BEFORE the guard so they still run on /workbench.
   157	    shell_boot_pos = js_text.index("bootWorkbenchShell();")
   158	    view_mode_pos = js_text.index("installViewModeHandlers();")
   159	    assert shell_boot_pos < sentinel_pos, (
   160	        "bootWorkbenchShell must run on /workbench (before bundle guard)"
   161	    )
   162	    assert view_mode_pos < sentinel_pos, (
   163	        "installViewModeHandlers must run on /workbench (before bundle guard)"
   164	    )

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3940,3973p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3940	  });
  3941	}
  3942	
  3943	window.addEventListener("DOMContentLoaded", () => {
  3944	  bootWorkbenchShell();
  3945	  installViewModeHandlers();
  3946	  installFeedbackModeAffordance();
  3947	  installWowStarters();
  3948	
  3949	  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  3950	  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  3951	  // NOT contain bundle elements like #workbench-packet-json,
  3952	  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  3953	  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  3954	  // bundle DOM exists and would throw "Cannot read properties of null" on the
  3955	  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  3956	  // skip bundle boot entirely. This script is shared between both pages.
  3957	  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  3958	  if (!onBundlePage) {
  3959	    return;
  3960	  }
  3961	
  3962	  installToolbarHandlers();
  3963	  updateWorkflowUI();
  3964	  if (checkUrlIntakeParam()) {
  3965	    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
  3966	    if (bundleBtn) {
  3967	      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
  3968	      bundleBtn.click();
  3969	    }
  3970	    return;
  3971	  }
  3972	  void loadBootstrapPayload();
  3973	});

  ✓ Confirm branch/head scope and truth-engine red-line via git diff/path audit
  ✓ Read the in-scope files fully and inspect anchor/copy changes with line citations
  ✓ Live-probe /workbench render path and run targeted verification
  → Deliver persona verdict with severity-ordered findings
codex
最后整理 verdict 前，我把记忆引用行号补齐一下；正文仍然只基于这次仓内检查和 live probe。
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '791,817p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,879p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

 succeeded in 0ms:
   791	# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
   792	
   793	scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
   794	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
   795	
   796	## Task 1: Build an isolated Notion hub and harden repo-side sync/timeouts
   797	
   798	### rollout_summary_files
   799	
   800	- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
   801	
   802	### keywords
   803	
   804	- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
   805	
   806	## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查
   807	
   808	### rollout_summary_files
   809	
   810	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   811	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
   812	
   813	### keywords
   814	
   815	- 根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查, 当前无需 Opus 审查, Gate status: Approved, tools/gsd_notion_sync.py run, NOTION_WRITEBACK_TIMEOUT_S, P7-19, P7-20, P8-05, P8-06
   816	
   817	## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts

  ✓ Confirm branch/head scope and truth-engine red-line via git diff/path audit
  ✓ Read the in-scope files fully and inspect anchor/copy changes with line citations
  ✓ Live-probe /workbench render path and run targeted verification
  ✓ Deliver persona verdict with severity-ordered findings
codex
**APPROVE**

No findings.

Boundary checks all hold:
- Truth-engine red line is clean: `git diff --name-only main..HEAD` contains only the two `.planning` files, [workbench.html:202](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:202), [workbench.js:63](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:63), and [test_workbench_column_rename.py:1](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:1). No `controller.py` / `runner.py` / `models.py` / `adapters/` drift.
- The shell rename is copy-only while stable anchors remain intact at [workbench.html:202](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:202), [workbench.html:222](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:222), and [workbench.html:242](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:242).
- Hydrated boot copy changed in place, with the same status IDs and no selector contract drift, at [workbench.js:68](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:68), [workbench.js:77](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:77), and [workbench.js:86](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:86).
- Shell boot still executes on `/workbench` before the bundle sentinel early-return, so the renamed shell status path remains live: [workbench.js:3943](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3943), [test_workbench_dual_route.py:110](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_dual_route.py:110).
- Existing selector-bearing tests are anchor-based, not heading-text-based, so this rename does not silently sever their contracts: [test_workbench_shell.py:63](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_shell.py:63), [test_workbench_annotation_static.py:16](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_static.py:16), [test_workbench_approval_center.py:66](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_center.py:66), plus the new lock file at [test_workbench_column_rename.py:113](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:113).

Verification:
- Live probe: with `PYTHONPATH=src:.`, `DemoRequestHandler` served `GET /workbench` and `GET /workbench.js` as `200`, and both responses contained the renamed copy plus preserved anchors.
- Targeted regression run passed: `pytest -q tests/test_workbench_column_rename.py tests/test_workbench_shell.py tests/test_workbench_dual_route.py tests/test_workbench_annotation_static.py tests/test_workbench_approval_center.py` → `53 passed in 4.15s`.

Residual risk:
- JS boot on `/workbench` is still validated structurally plus asset probe, not via headless browser execution; the repo already records that deferred gap at [test_workbench_dual_route.py:123](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_dual_route.py:123).

**P2 — Senior FCS Engineer (Tier-A, E11-03)**

tokens used
217,647
**APPROVE**

No findings.

Boundary checks all hold:
- Truth-engine red line is clean: `git diff --name-only main..HEAD` contains only the two `.planning` files, [workbench.html:202](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:202), [workbench.js:63](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:63), and [test_workbench_column_rename.py:1](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:1). No `controller.py` / `runner.py` / `models.py` / `adapters/` drift.
- The shell rename is copy-only while stable anchors remain intact at [workbench.html:202](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:202), [workbench.html:222](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:222), and [workbench.html:242](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:242).
- Hydrated boot copy changed in place, with the same status IDs and no selector contract drift, at [workbench.js:68](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:68), [workbench.js:77](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:77), and [workbench.js:86](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:86).
- Shell boot still executes on `/workbench` before the bundle sentinel early-return, so the renamed shell status path remains live: [workbench.js:3943](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3943), [test_workbench_dual_route.py:110](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_dual_route.py:110).
- Existing selector-bearing tests are anchor-based, not heading-text-based, so this rename does not silently sever their contracts: [test_workbench_shell.py:63](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_shell.py:63), [test_workbench_annotation_static.py:16](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_annotation_static.py:16), [test_workbench_approval_center.py:66](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_approval_center.py:66), plus the new lock file at [test_workbench_column_rename.py:113](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:113).

Verification:
- Live probe: with `PYTHONPATH=src:.`, `DemoRequestHandler` served `GET /workbench` and `GET /workbench.js` as `200`, and both responses contained the renamed copy plus preserved anchors.
- Targeted regression run passed: `pytest -q tests/test_workbench_column_rename.py tests/test_workbench_shell.py tests/test_workbench_dual_route.py tests/test_workbench_annotation_static.py tests/test_workbench_approval_center.py` → `53 passed in 4.15s`.

Residual risk:
- JS boot on `/workbench` is still validated structurally plus asset probe, not via headless browser execution; the repo already records that deferred gap at [test_workbench_dual_route.py:123](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_dual_route.py:123).

**P2 — Senior FCS Engineer (Tier-A, E11-03)**

