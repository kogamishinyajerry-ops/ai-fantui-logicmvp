2026-04-26T01:06:45.378543Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T01:06:45.378624Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc753-21e0-7141-abe2-a449ca3e4501
--------
user
You are Codex GPT-5.4 acting as **Persona P3 — Demo Presenter** (Tier-B single-persona pipeline, E11-15b sub-phase).

# Context — E11-15b Chinese-first iter 2 (h1/h2/buttons/caption)

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15b-chinese-h2-button-sweep-20260426`
**PR:** #25
**Worktree HEAD:** `7543d77` (single commit on top of main `0c2e0b6`)

## What E11-15b ships

Continuation of E11-15 (which flipped 5 eyebrow labels). 7 remaining English-only h1/h2/button/caption strings on /workbench bilingualized as `<中文> · <English>`, preserving English suffixes so existing dual-route test locks (e.g. `Control Logic Workbench</h1>`) keep passing without modification.

| File:Line | Before | After |
|---|---|---|
| `workbench.html:18` | `<h1>Control Logic Workbench</h1>` | `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` |
| `workbench.html:281` | `Load Active Ticket` (button) | `加载当前工单 · Load Active Ticket` |
| `workbench.html:282` | `Snapshot Current State` (button) | `快照当前状态 · Snapshot Current State` |
| `workbench.html:334` | `<h2>Review Queue</h2>` | `<h2>审核队列 · Review Queue</h2>` |
| `workbench.html:349` | `Approval Center` (button text) | `审批中心 · Approval Center` |
| `workbench.html:351` | `Approval actions are Kogami-only.` (caption) | `审批操作仅限 Kogami · Approval actions are Kogami-only.` |
| `workbench.html:380` | `<h2 id="approval-center-title">Kogami Proposal Triage</h2>` | `<h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>` |

## Files in scope

- `src/well_harness/static/workbench.html` — 7 strings flipped
- `tests/test_workbench_chinese_h2_button_sweep.py` — NEW (28 tests)
- `tests/test_workbench_chinese_eyebrow_sweep.py` — 1-line h1 lock update (line 119) to track new bilingual h1
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

## Your specific lens (P3 Demo Presenter)

Focus on:
- **Reading rhythm**: do the 7 bilingual strings flow naturally when a Chinese-speaking demo audience reads the page top-to-bottom? Any awkward 中文 · English pairing where the Chinese feels translated rather than native?
- **First-glance demo impression**: open `/workbench` cold — does the page now read Chinese-first across header, control buttons, annotation inbox, and approval center? Or is there still residual English-first surface that defeats the goal?
- **Translation quality**: especially `加载当前工单` for "Load Active Ticket" (vs. `加载活跃工单`/`载入当前工单`), `快照当前状态` for "Snapshot Current State", `审核队列` for "Review Queue", `Kogami 提案审批` for "Kogami Proposal Triage" — are these the most natural professional FCS-engineer renderings, or would a native Chinese FCS engineer phrase any of them differently?
- **Bilingual delimiter consistency**: every flip uses ` · ` (space-middot-space). Is this consistent with the rest of the codebase's bilingual pattern (e.g., column h2s `Probe & Trace · 探针与追踪`)? Note the column h2s use English-first; the new sweep uses Chinese-first. Is this asymmetry acceptable for demo flow, or does it look inconsistent at a glance?
- **API contract preservation**: confirm `demo_server.py:743` remediation message is unchanged AND no Chinese leaks into the backend file (test #28 covers this — verify the assertion is correct).
- **English suffix preservation**: confirm dual-route exact-substring locks (e.g., `Control Logic Workbench</h1>`) still pass via the preserved English suffix.

## Verification status

- 1063 / 1063 pytest pass (28 new in `test_workbench_chinese_h2_button_sweep.py`; full suite green)
- Truth-engine red line preserved: `git diff --name-only main..7543d77` shows only `.planning/...`, `static/workbench.html`, and 2 test files.
- Adjacent suite (chinese_eyebrow + dual_route + shell + role_affordance + column_rename + lever_snapshot_manual_override_guard) — 126/126 pass.

## Out of scope (deliberately deferred)

- **Approval lane h3s** (`Pending`/`Accept`/`Reject`) + lane buttons (`Accept Proposal`/`Reject Proposal`) — functional approval-flow strings; deferred to focused approval-flow polish sub-phase.
- **API remediation message** in `demo_server.py:743` — backend contract, locked.
- **Reverse direction**: column h2s currently use English-first (`Probe & Trace · 探针与追踪`); could be flipped to Chinese-first in a future sweep for delimiter symmetry.
- **`workbench.js` / `workbench.css`** — pure HTML sweep.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path (open `/workbench` headlessly and verify served HTML carries the new bilingual strings). Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..7543d77` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/` / `workbench.js` / `workbench.css` / `demo_server.py`.

Sign as: **P3 — Demo Presenter (Tier-B, E11-15b)**
codex
Reviewing the E11-15b slice as a demo-presenter code review. I’m first pulling the repo diff, the review-specific guidance, and the existing LogicMVP memory note so I can validate the live surface against the exact scope you defined.
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
/bin/zsh -lc 'rg -n "LogicMVP|E11|demo presentation|启动UI|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
934:- 启动UI, Address already in use, 8001, 8770, well_harness.demo_server, lsof -nP -iTCP, localhost, Well Harness 反推逻辑演示舱
940:- rollout_summaries/2026-04-08T15-04-09-7j1J-reconstruct_ai_coding_development_log_and_leadership_speech.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-04-09-019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf.jsonl, updated_at=2026-04-08T15:12:08+00:00, thread_id=019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf, detailed Chinese summary and 5-minute leadership speech)
950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
951:- rollout_summaries/2026-04-07T05-30-48-VWde-thrust_reverser_harness_audit_and_control_freeze.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T13-30-48-019d666c-0536-7403-80c3-1216c53a4944.jsonl, updated_at=2026-04-08T08:22:56+00:00, thread_id=019d666c-0536-7403-80c3-1216c53a4944, frozen controller truth and simplified-plant caveat)
962:- when the user said simply "启动UI" -> interpret that as a request to actually bring the service up and provide the working URL, not just describe a command [Task 3]
1240:- In this repo, the generator scripts under the external CFD workbench path were a more reliable evidence source than the rendered PDFs; when `pdftotext` is unavailable and `matplotlib` temp/cache paths are broken, parse scripts as text or AST instead of importing them [Task 1]

exec
/bin/zsh -lc "printf '%s
' \""'$PWD" && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
feat/e11-15b-chinese-h2-button-sweep-20260426
7543d7725993bdc83455e07382a669ac60776003
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt

codex
I have the branch and the review skill/context loaded. Next I’m checking the actual diff and the affected HTML/tests, then I’ll live-probe `/workbench` from a running server and compare that against the red-line contract.
  → Inspect branch diff and changed files for E11-15b scope compliance
  • Live-probe /workbench HTML and verify bilingual strings plus backend boundary
  • Summarize verdict and findings in P3 demo-presenter format
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,460p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    17	          <p class="eyebrow">控制逻辑工作台</p>
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
   275	            <h2>Probe &amp; Trace · 探针与追踪</h2>
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
   295	            <h2>Annotate &amp; Propose · 标注与提案</h2>
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
   315	            <h2>Hand off &amp; Track · 移交与跟踪</h2>
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
   381	        </header>
   382	        <div class="workbench-approval-grid">
   383	          <article class="workbench-approval-lane" data-approval-lane="pending">
   384	            <h3>Pending</h3>
   385	            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
   386	          </article>
   387	          <article class="workbench-approval-lane" data-approval-lane="accept">
   388	            <h3>Accept</h3>
   389	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
   390	          </article>
   391	          <article class="workbench-approval-lane" data-approval-lane="reject">
   392	            <h3>Reject</h3>
   393	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
   394	          </article>
   395	        </div>
   396	      </section>
   397	
   398	      <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
   399	    </main>
   400	
   401	    <script src="/annotation_overlay.js"></script>
   402	    <script src="/workbench.js"></script>
   403	  </body>
   404	</html>

exec
/bin/zsh -lc 'git diff --name-only main..7543d77' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
tests/test_workbench_chinese_eyebrow_sweep.py
tests/test_workbench_chinese_h2_button_sweep.py

exec
/bin/zsh -lc 'git diff --unified=3 main..7543d77 -- src/well_harness/static/workbench.html tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py .planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..81dec24
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md
@@ -0,0 +1,86 @@
+# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
+
+> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
+>
+> Continuation of E11-15: that sweep covered 5 eyebrow labels; this iter
+> covers the remaining English-only h1/h2/button/caption strings on
+> /workbench, bilingualizing them as `<中文> · <English>` so the page is
+> uniformly Chinese-first while preserving English suffixes for existing
+> test locks.
+
+## Surface diff inventory
+
+| # | Surface | Type | Anchor | Notes |
+|---|---|---|---|---|
+| 1 | h1 `Control Logic Workbench` → `控制逻辑工作台 · Control Logic Workbench` | [REWRITE] | `workbench.html:18` | Page-level title above the brand eyebrow E11-15 already flipped. |
+| 2 | btn `Load Active Ticket` → `加载当前工单 · Load Active Ticket` | [REWRITE] | `workbench.html:281` | First-column control panel skeleton button. |
+| 3 | btn `Snapshot Current State` → `快照当前状态 · Snapshot Current State` | [REWRITE] | `workbench.html:282` | Second skeleton button in same column. |
+| 4 | h2 `Review Queue` → `审核队列 · Review Queue` | [REWRITE] | `workbench.html:334` | Annotation-inbox aside heading. |
+| 5 | btn text `Approval Center` → `审批中心 · Approval Center` | [REWRITE] | `workbench.html:349` | Bottom-bar approval entry button. The Kogami-only display copy is intentionally bilingualized; the API remediation message in `demo_server.py:743` is **NOT** touched (backend contract). |
+| 6 | caption `Approval actions are Kogami-only.` → `审批操作仅限 Kogami · Approval actions are Kogami-only.` | [REWRITE] | `workbench.html:351` | Bottom-bar caption next to entry button. |
+| 7 | h2 `Kogami Proposal Triage` → `Kogami 提案审批 · Kogami Proposal Triage` | [REWRITE] | `workbench.html:380` | Approval Center panel heading. |
+
+## Out of scope (deliberately deferred or preserved)
+
+- **Approval lane h3s** (`Pending`/`Accept`/`Reject`) + lane buttons
+  (`Accept Proposal`/`Reject Proposal`) — functional approval-flow
+  strings; deferred to a focused approval-flow polish sub-phase.
+- **API remediation message** in `demo_server.py:743`
+  (`"Acquire sign-off via Approval Center, or switch to auto_scrubber."`)
+  — backend contract, locked by
+  `tests/test_lever_snapshot_manual_override_guard.py:151`.
+- **Column-trio eyebrows** + column h2s (already bilingual via E11-03).
+- **Eyebrow labels** (already flipped by E11-15).
+- **`workbench.js` / `workbench.css`** — pure HTML sweep.
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
+→ **Tier-B** (1-persona review). The first threshold (≥10) fails.
+
+> **Verdict: Tier-B**. Persona = **P3 (Demo Presenter)** — round-robin
+> successor of E11-15's P2 AND content-fit: this sub-phase is exactly
+> typography / reading-rhythm / first-glance demo impression, which is
+> P3's core lens.
+
+## Behavior contract (locked by tests)
+
+`tests/test_workbench_chinese_h2_button_sweep.py` (NEW, 28 tests):
+
+1. Each of the 7 new bilingual strings is positively asserted.
+2. 5 stale English-only patterns are asserted absent
+   (button text fragments asserted via `>X<` to avoid false positives
+   on the `Approval Center` substring inside `aria-controls` attributes).
+3. 7 English-suffix invariants asserted preserved (so dual-route exact
+   substring locks like `Control Logic Workbench</h1>` keep passing).
+4. 7 structural anchors (IDs, class hooks, data-role attributes) asserted
+   unchanged.
+5. Live `/workbench` route serves all 7 new bilingual strings.
+6. API remediation message in `demo_server.py` is asserted unchanged
+   AND no Chinese strings leak into the backend file.
+
+`tests/test_workbench_chinese_eyebrow_sweep.py` updated: line 119's
+exact-string h1 lock changed from `<h1>Control Logic Workbench</h1>` to
+`<h1>控制逻辑工作台 · Control Logic Workbench</h1>` to reflect the
+bilingualization.
+
+## Truth-engine red line
+
+Files touched:
+- `src/well_harness/static/workbench.html` — 7 strings flipped
+- `tests/test_workbench_chinese_h2_button_sweep.py` — NEW (28 tests)
+- `tests/test_workbench_chinese_eyebrow_sweep.py` — 1-line h1 lock update
+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md` — NEW
+- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended
+
+Files NOT touched: `controller.py`, `runner.py`, `models.py`,
+`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
+`demo_server.py`. Truth-engine boundary preserved. No new endpoints; no
+backend changes; the API remediation message is explicitly asserted
+unchanged.
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index 4e1b1b0..303459d 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -17,3 +17,4 @@ E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE] — all NEW section co
 E11-07: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE] — pure-NEW banner). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit for customer/repro-facing authority contract messaging).
 E11-08: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE]). Persona = P1 (Junior FCS Engineer — round-robin wraps P5 → P1 AND content-fit for small UI-only refactor with regression-risk JS attribute reading + URL-param parsing).
 E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
+E11-15b: Tier-B (7 copy_diff_lines, 7 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P3 (Demo Presenter — round-robin successor of P2 AND content-fit: typography/reading-rhythm/first-glance demo impression is P3's core lens). Bilingualizes h1 + 2 buttons + h2 + approval entry button + caption + h2 to `<中文> · <English>`, preserving English suffixes for dual-route test locks. API remediation message in demo_server.py:743 explicitly preserved (backend contract).
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 0f30743..90f44c3 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -15,7 +15,7 @@
       <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
         <div class="workbench-collab-brand">
           <p class="eyebrow">控制逻辑工作台</p>
-          <h1>Control Logic Workbench</h1>
+          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
         </div>
         <div
           id="workbench-identity"
@@ -278,8 +278,8 @@
             Waiting for probe &amp; trace panel boot.
           </div>
           <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
-            <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
-            <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
+            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
+            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
           </div>
         </article>
 
@@ -331,7 +331,7 @@
       <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
         <header>
           <p class="eyebrow">标注收件箱</p>
-          <h2>Review Queue</h2>
+          <h2>审核队列 · Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
           <li>No proposals submitted yet.</li>
@@ -346,9 +346,9 @@
           data-role="KOGAMI"
           aria-controls="approval-center-panel"
         >
-          Approval Center
+          审批中心 · Approval Center
         </button>
-        <span>Approval actions are Kogami-only.</span>
+        <span>审批操作仅限 Kogami · Approval actions are Kogami-only.</span>
       </footer>
 
       <section
@@ -377,7 +377,7 @@
       >
         <header>
           <p class="eyebrow">审批中心</p>
-          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
+          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
         </header>
         <div class="workbench-approval-grid">
           <article class="workbench-approval-lane" data-approval-lane="pending">
diff --git a/tests/test_workbench_chinese_eyebrow_sweep.py b/tests/test_workbench_chinese_eyebrow_sweep.py
index aa098a6..2abec09 100644
--- a/tests/test_workbench_chinese_eyebrow_sweep.py
+++ b/tests/test_workbench_chinese_eyebrow_sweep.py
@@ -115,8 +115,10 @@ def test_e11_03_column_eyebrows_preserved(preserved_eyebrow: str) -> None:
 @pytest.mark.parametrize(
     "anchor",
     [
-        # h1/h2 main titles untouched
-        "<h1>Control Logic Workbench</h1>",
+        # h1 main title is bilingualized by E11-15b (Chinese-first); the
+        # English suffix `Control Logic Workbench</h1>` is preserved as
+        # locked by test_workbench_dual_route.
+        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
         # IDs of containing sections untouched
         'id="workbench-state-of-world-bar"',
         'id="workbench-wow-starters"',
diff --git a/tests/test_workbench_chinese_h2_button_sweep.py b/tests/test_workbench_chinese_h2_button_sweep.py
new file mode 100644
index 0000000..ab4168a
--- /dev/null
+++ b/tests/test_workbench_chinese_h2_button_sweep.py
@@ -0,0 +1,186 @@
+"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
+
+Continues the E11-15 eyebrow sweep: 7 remaining English-only h1/h2/button/
+caption strings on /workbench are bilingualized as `<中文> · <English>`,
+preserving the English suffix so existing test locks (e.g. dual-route
+checks for `Control Logic Workbench</h1>`) continue to pass.
+
+In-scope strings (file:line in pre-sweep workbench.html):
+- :18  h1   Control Logic Workbench           → 控制逻辑工作台 · Control Logic Workbench
+- :281 btn  Load Active Ticket                → 加载当前工单 · Load Active Ticket
+- :282 btn  Snapshot Current State            → 快照当前状态 · Snapshot Current State
+- :334 h2   Review Queue                      → 审核队列 · Review Queue
+- :349 btn  Approval Center                   → 审批中心 · Approval Center
+- :351 cap  Approval actions are Kogami-only. → 审批操作仅限 Kogami · Approval actions are Kogami-only.
+- :380 h2   Kogami Proposal Triage            → Kogami 提案审批 · Kogami Proposal Triage
+
+Out of scope (deliberately preserved or deferred):
+- API remediation message in demo_server.py:743 — backend contract,
+  locked by tests/test_lever_snapshot_manual_override_guard.py:151.
+- Approval lane h3s "Pending"/"Accept"/"Reject" + lane buttons
+  ("Accept Proposal"/"Reject Proposal") — functional approval-flow
+  strings, deferred to a focused approval-flow polish sub-phase.
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
+# ─── 1. New bilingual strings POSITIVELY locked ──────────────────────
+
+
+@pytest.mark.parametrize(
+    "bilingual",
+    [
+        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
+        ">加载当前工单 · Load Active Ticket<",
+        ">快照当前状态 · Snapshot Current State<",
+        "<h2>审核队列 · Review Queue</h2>",
+        "审批中心 · Approval Center",
+        "审批操作仅限 Kogami · Approval actions are Kogami-only.",
+        "Kogami 提案审批 · Kogami Proposal Triage",
+    ],
+)
+def test_workbench_html_carries_bilingual_string(bilingual: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert bilingual in html, f"missing bilingual string: {bilingual}"
+
+
+# ─── 2. Stale English-only strings are gone ──────────────────────────
+
+
+@pytest.mark.parametrize(
+    "stale",
+    [
+        "<h1>Control Logic Workbench</h1>",
+        ">Load Active Ticket<",
+        ">Snapshot Current State<",
+        "<h2>Review Queue</h2>",
+        "<h2 id=\"approval-center-title\">Kogami Proposal Triage</h2>",
+    ],
+)
+def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale not in html, f"stale English-only string still present: {stale}"
+
+
+# ─── 3. English suffixes preserved for existing test locks ───────────
+#
+# E11-15b deliberately keeps the English token at the end of each
+# bilingual string, so existing exact-substring tests (e.g.
+# test_workbench_dual_route's `Control Logic Workbench</h1>` check)
+# keep passing without modification.
+
+
+@pytest.mark.parametrize(
+    "preserved_english_suffix",
+    [
+        "Control Logic Workbench</h1>",
+        "Load Active Ticket</button>",
+        "Snapshot Current State</button>",
+        "Review Queue</h2>",
+        "Approval Center\n",  # button text fragment, newline preserved
+        "Approval actions are Kogami-only.",
+        "Kogami Proposal Triage</h2>",
+    ],
+)
+def test_e11_15b_preserves_english_suffix(preserved_english_suffix: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert preserved_english_suffix in html, (
+        f"E11-15b broke English suffix invariant: {preserved_english_suffix}"
+    )
+
+
+# ─── 4. Structural anchors preserved ─────────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "anchor",
+    [
+        'id="approval-center-entry"',
+        'id="approval-center-panel"',
+        'id="approval-center-title"',
+        'id="annotation-inbox"',
+        'class="workbench-toolbar-button is-primary"',
+        'data-role="KOGAMI"',
+        'data-approval-role="KOGAMI"',
+    ],
+)
+def test_e11_15b_preserves_structural_anchors(anchor: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert anchor in html, f"E11-15b broke structural anchor: {anchor}"
+
+
+# ─── 5. Live-served route reflects the sweep ─────────────────────────
+
+
+def test_workbench_route_serves_bilingual_strings(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    assert "控制逻辑工作台 · Control Logic Workbench" in html
+    assert "审核队列 · Review Queue" in html
+    assert "审批中心 · Approval Center" in html
+    assert "审批操作仅限 Kogami" in html
+    assert "Kogami 提案审批" in html
+    assert "加载当前工单" in html
+    assert "快照当前状态" in html
+
+
+# ─── 6. Truth-engine red line — API remediation untouched ────────────
+#
+# The Approval Center remediation message in demo_server.py is a
+# backend API contract locked by test_lever_snapshot_manual_override_guard.
+# The HTML sweep MUST NOT bilingualize that string; the API stays English.
+
+
+def test_e11_15b_does_not_touch_api_remediation_message() -> None:
+    """The 409 remediation message is API contract, not display copy."""
+    repo_root = Path(__file__).resolve().parents[1]
+    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
+        encoding="utf-8"
+    )
+    # The original English-only remediation text MUST still be there.
+    assert (
+        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
+        in demo_server
+    )
+    # No Chinese leak into the API layer.
+    assert "审批中心" not in demo_server
+    assert "审批操作" not in demo_server

codex
The diff is cleanly scoped so far. I’m now checking the live route and the backend remediation boundary directly, because that’s where a presenter-style polish review can still miss a contract leak if I only read the static HTML.
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '720,760p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'python -m pytest -q tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_dual_route.py tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n \"Control Logic Workbench</h1>|Approval Center|workbench_dual_route|Kogami Proposal Triage|Load Active Ticket|Snapshot Current State\" tests src/well_harness -g '"'!tests/test_workbench_chinese_h2_button_sweep.py'"'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

 succeeded in 0ms:
src/well_harness/demo_server.py:743:                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
tests/test_workbench_dual_route.py:64:    assert "Control Logic Workbench</h1>" in body
tests/test_workbench_dual_route.py:90:    assert "Control Logic Workbench</h1>" not in body
tests/test_workbench_dual_route.py:103:    assert "Control Logic Workbench</h1>" in shell_html
tests/test_workbench_dual_route.py:107:    assert "Control Logic Workbench</h1>" not in bundle_html
src/well_harness/static/fan_console.html:421:    // with sign-off via the workbench Approval Center).
src/well_harness/static/workbench.js:3960:// When the workbench identity is NOT Kogami, replace the Approval Center
src/well_harness/static/workbench.html:18:          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
src/well_harness/static/workbench.html:281:            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
src/well_harness/static/workbench.html:282:            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
src/well_harness/static/workbench.html:349:          审批中心 · Approval Center
src/well_harness/static/workbench.html:380:          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
src/well_harness/static/workbench_start.html:112:        <li>建议演示前隐藏浏览器侧栏 + 关闭 Approval Center 抽屉</li>
src/well_harness/static/workbench_start.html:148:      <h2 class="ws-tile-title">Approval Center · 静态 shell 占位</h2>
src/well_harness/static/workbench_start.html:151:        落到 <code>/workbench</code> 底栏的 Approval Center 入口。 当前
src/well_harness/static/workbench_start.html:199:      详见 <a href="/workbench?intent=approval-review#approval-center-entry">Approval Center</a>
src/well_harness/static/demo.js:116:    // proof of authentication. Real sign-off via Approval Center post-E11-08.
tests/test_lever_snapshot_manual_override_guard.py:147:    """409 response includes a remediation message pointing to Approval Center."""
tests/test_lever_snapshot_manual_override_guard.py:151:    assert "Approval Center" in body.get("remediation", "")
tests/test_workbench_chinese_eyebrow_sweep.py:119:        # English suffix `Control Logic Workbench</h1>` is preserved as
tests/test_workbench_chinese_eyebrow_sweep.py:120:        # locked by test_workbench_dual_route.
tests/test_workbench_chinese_eyebrow_sweep.py:121:        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
tests/test_workbench_role_affordance.py:4:the Approval Center entry button + panel must be replaced with an
tests/test_workbench_role_affordance.py:8:Default state (Kogami identity): Approval Center visible, pending
tests/test_workbench_role_affordance.py:10:Non-Kogami state: Approval Center hidden, pending affordance visible.
tests/test_workbench_role_affordance.py:77:    """The affordance copy must explain WHY the Approval Center is gone

codex
The only execution issue so far is environmental: this checkout has `python3`, not `python`. I’m rerunning the targeted checks with the correct interpreter and then I’ll do a real `/workbench` fetch from a live local server instead of relying only on the unit test fixture.
exec
/bin/zsh -lc "rg -n \"if __name__ == '__main__'|def main\\(|argparse|serve_forever|ThreadingHTTPServer|HTTPServer\" src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
5:import argparse
14:from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
2856:def build_parser() -> argparse.ArgumentParser:
2857:    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
2886:def main(argv: list[str] | None = None) -> int:
2888:    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
2895:        server.serve_forever()

exec
/bin/zsh -lc 'python3 -m pytest -q tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_dual_route.py tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 11913ms:
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 11.67s

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2850,2905p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2850	            "THR_LOCK release must not be read as complete physical root-cause proof.",
  2851	        ],
  2852	    }
  2853	    return _apply_fault_injections_to_snapshot_payload(result, fault_injections)
  2854	
  2855	
  2856	def build_parser() -> argparse.ArgumentParser:
  2857	    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
  2858	    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
  2859	    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
  2860	    parser.add_argument(
  2861	        "--open",
  2862	        action="store_true",
  2863	        help=(
  2864	            "Open the local UI URL with Python's standard-library webbrowser.open; "
  2865	            "this is a launch convenience, not browser E2E automation."
  2866	        ),
  2867	    )
  2868	    return parser
  2869	
  2870	
  2871	def demo_url(host: str, port: int) -> str:
  2872	    return f"http://{host}:{port}/index.html"
  2873	
  2874	
  2875	def open_browser(url: str, opener=webbrowser.open) -> bool:
  2876	    try:
  2877	        opened = bool(opener(url))
  2878	    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
  2879	        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
  2880	        return False
  2881	    if not opened:
  2882	        print(f"Could not open browser automatically. Open {url} manually.")
  2883	    return opened
  2884	
  2885	
  2886	def main(argv: list[str] | None = None) -> int:
  2887	    args = build_parser().parse_args(argv)
  2888	    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
  2889	    host, port = server.server_address
  2890	    url = demo_url(host, port)
  2891	    print(f"Serving well-harness demo UI at {url}")
  2892	    if args.open:
  2893	        open_browser(url)
  2894	    try:
  2895	        server.serve_forever()
  2896	    except KeyboardInterrupt:
  2897	        print("\nStopping well-harness demo UI.")
  2898	    finally:
  2899	        server.server_close()
  2900	    return 0
  2901	
  2902	
  2903	if __name__ == "__main__":
  2904	    raise SystemExit(main())

exec
/bin/zsh -lc "nl -ba tests/test_workbench_dual_route.py | sed -n '55,110p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

codex
The targeted regression subset passed, including the English-suffix locks and the backend guard check. I’m doing one last live fetch from a real running `demo_server` instance so the verdict cites an actual served `/workbench` response, not just the fixture-backed tests.
exec
/bin/zsh -lc 'PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "curl -s http://127.0.0.1:8770/workbench | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'curl -s http://127.0.0.1:8770/workbench | rg -n "控制逻辑工作台 · Control Logic Workbench|加载当前工单 · Load Active Ticket|快照当前状态 · Snapshot Current State|审核队列 · Review Queue|审批中心 · Approval Center|审批操作仅限 Kogami · Approval actions are Kogami-only.|Kogami 提案审批 · Kogami Proposal Triage|<title>Control Logic Workbench</title>"' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Control Logic Workbench</title>
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/apple-touch-icon.svg">
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="/demo.css">
    <link rel="stylesheet" href="/workbench.css">
  </head>
  <body data-view="beginner">
    <main class="shell workbench-shell">
      <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
        <div class="workbench-collab-brand">
          <p class="eyebrow">控制逻辑工作台</p>
          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
        </div>
        <div
          id="workbench-identity"
          class="workbench-collab-chip"
          data-role="ENGINEER"
          data-identity-name="Kogami"
        >
          <span>Identity</span>
          <strong>Kogami / Engineer</strong>
        </div>
        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
          <span>Ticket</span>
          <strong>WB-E06-SHELL</strong>
        </div>
        <div
          id="workbench-feedback-mode"
          class="workbench-collab-chip workbench-feedback-mode-chip"
          data-feedback-mode="manual_feedback_override"
          data-mode-authority="advisory"
          aria-live="polite"
          title="Manual feedback override is advisory — truth engine readings remain authoritative."
        >
          <span>Feedback Mode</span>
          <strong>Manual (advisory)</strong>
          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
        </div>
        <label class="workbench-collab-system" for="workbench-system-select">
          <span>System</span>
          <select id="workbench-system-select">
            <option value="thrust-reverser">Thrust Reverser</option>
            <option value="landing-gear">Landing Gear</option>
            <option value="bleed-air-valve">Bleed Air Valve</option>
            <option value="c919-etras">C919 E-TRAS</option>
          </select>
        </label>
      </section>

      <section
        id="workbench-state-of-world-bar"
        class="workbench-state-of-world-bar"
        aria-label="State-of-the-world status bar (advisory)"
        data-status-kind="advisory"
      >
        <span class="workbench-sow-eyebrow">当前现状</span>
        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
              title="git rev-parse --short HEAD">
          <span class="workbench-sow-label">truth-engine SHA</span>
          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
        </span>
        <span class="workbench-sow-sep" aria-hidden="true">·</span>
        <span class="workbench-sow-field" data-sow-field="recent_e2e"
              title="docs/coordination/qa_report.md (most recent test run)">
          <span class="workbench-sow-label">recent e2e</span>
          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
        </span>
        <span class="workbench-sow-sep" aria-hidden="true">·</span>
        <span class="workbench-sow-field" data-sow-field="adversarial"
              title="docs/coordination/qa_report.md (shared validation)">
          <span class="workbench-sow-label">adversarial</span>
          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
        </span>
        <span class="workbench-sow-sep" aria-hidden="true">·</span>
        <span class="workbench-sow-field" data-sow-field="known_issues"
              title="docs/known-issues/ file count">
          <span class="workbench-sow-label">open issues</span>
          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
        </span>
        <span class="workbench-sow-flag" aria-hidden="false">
          advisory · not a live truth-engine reading
        </span>
      </section>

      <section
        id="workbench-wow-starters"
        class="workbench-wow-starters"
        aria-label="Canonical demo scenarios — one-click starter cards"
      >
        <header class="workbench-wow-starters-header">
          <p class="eyebrow">主流场景</p>
          <h2>起手卡 · One-click 走读</h2>
          <p class="workbench-wow-starters-sub">
            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
          </p>
        </header>
        <div class="workbench-wow-starters-grid">
          <article
            class="workbench-wow-card"
            data-wow-id="wow_a"
            aria-labelledby="workbench-wow-a-title"
          >
            <header>
              <span class="workbench-wow-tag">wow_a</span>
              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
            </header>
            <p class="workbench-wow-card-desc">
              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
            </p>
            <button
              type="button"

 succeeded in 0ms:
6:    <title>Control Logic Workbench</title>
18:          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
281:            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
282:            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
334:          <h2>审核队列 · Review Queue</h2>
349:          审批中心 · Approval Center
351:        <span>审批操作仅限 Kogami · Approval actions are Kogami-only.</span>
380:          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>

exec
/bin/zsh -lc "rg -n \"[\\p{Han}]\" src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
263:        # the banner's "v6.1 红线条款 →" link resolves to a real, in-repo
615:            # Pull the explicit "Forbidden（红线维持）" section. If the
618:            anchor = full_text.find("Forbidden（红线维持")
625:                    "Truth-engine 红线: controller / runner / models / "
633:                "Truth-engine 红线 source file (.planning/constitution.md) "
720:# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
1290:        "boundary_note": "这是 explain runtime / pitch 运维状态，不是新的控制真值。",
1404:    m = re.search(r"最近成功执行证据：`([^`]+)`", text)
1944:            "headline": f"TRA {tra_deg:.1f}°：拉杆还没进入 SW1 窗口，反推链路保持待命。",
1945:            "blocker": "当前卡在 SW1：继续拉入 -1.4° 到 -6.2° 窗口会触发第一段链路。",
1946:            "next_step": "下一步：把拉杆继续向反推方向拉到 SW1 window。",
1951:            "headline": f"TRA {tra_deg:.1f}°：SW1 已触发，但 L1 / TLS115 尚未放行。",
1952:            "blocker": f"当前卡在 L1：{failed or 'logic1 条件未完全满足'}。",
1953:            "next_step": "下一步：恢复 RA / inhibited / EEC feedback 等 L1 条件，或回到默认演示条件。",
1957:            "headline": f"TRA {tra_deg:.1f}°：SW1 / L1 / TLS115 已点亮，正在建立 TLS 解锁反馈。",
1958:            "blocker": "当前卡在 SW2：还没有进入 -5.0° 到 -9.8° 窗口。",
1959:            "next_step": "下一步：继续拉到 SW2 window，点亮 L2 / 540V。",
1963:        blocker_text = f"当前卡在 L2：{failed or 'logic2 条件未完全满足'}。"
1966:            blocker_text += "（L3 对这些信号独立检查，同步被阻塞。）"
1968:            "headline": f"TRA {tra_deg:.1f}°：SW2 已触发，但 L2 / 540V 尚未放行。",
1970:            "next_step": "下一步：恢复 engine / ground / inhibited / EEC enable 等 L2 条件。",
1975:            "headline": f"TRA {tra_deg:.1f}°：SW1、SW2 与 L2/540V 已点亮，L3 尚未放行。",
1976:            "blocker": f"当前卡在 L3：{failed or 'logic3 条件未完全满足'}。",
1977:            "next_step": "下一步：继续拉到 TRA <= -11.74°，并保持 N1K / TLS 等条件满足。",
1981:        next_step = "下一步：在受控轨迹中继续保持反推，等 deploy_90_percent_vdt / VDT90 反馈出现。"
1983:            next_step = "下一步：把 deploy feedback override 推到 >= 90%，演示 VDT90 -> L4 -> THR_LOCK。"
1985:            "headline": f"TRA {tra_deg:.1f}°：L3 已点亮，EEC / PLS / PDU 命令正在驱动受控演示轨迹。",
1986:            "blocker": f"THR_LOCK 仍未释放：L4 还在等待 {failed or 'VDT90 / plant feedback'}。",
1991:            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落，L1 属于首次解锁门，已完成使命。）"
1998:            "headline": f"TRA {tra_deg:.1f}°：manual feedback override 已把 VDT90 推到触发态，L4 / THR_LOCK 已点亮。",
1999:            "blocker": "当前无 L4 blocker；这是 simplified plant feedback override 的诊断演示结果。" + l1_post_deploy_note,
2000:            "next_step": "下一步：切回 auto scrubber，或降低 deploy feedback 观察 VDT90 / THR_LOCK 退回 blocked。",
2004:            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落。）"
2011:            "headline": f"TRA {tra_deg:.1f}°：L4 已满足，THR_LOCK release command 已触发。",
2012:            "blocker": "当前无 L4 blocker。" + l1_post_deploy_note,
2013:            "next_step": "下一步：查看证据或返回问答抽屉做诊断解释。",
2018:            f"{summary['blocker']} TRA 深拉区仍未开放：请求 {tra_lock['requested_tra_deg']:.1f}° "
2019:            f"已被限制在 {tra_lock['lock_deg']:.1f}°，当前只开放 {tra_lock['lock_deg']:.1f}° 到 0.0° 的自由拖动范围。"
2155:    blocker_text = " / ".join(unlock_blockers) if unlock_blockers else "L4 条件"
2161:            f"L4 已满足：TRA 现在可以在 {config.reverse_travel_min_deg:.1f}° 到 0.0° 区间自由拖动。"
2165:            f"L4 未满足：请求 {requested_tra_deg:.1f}° 已锁回 {lock_deg:.1f}°；"
2166:            f"当前只能在 {lock_deg:.1f}° 到 0.0° 范围内拖动。"
2170:            f"L4 未满足：当前自由拖动范围只开放 {lock_deg:.1f}° 到 0.0°；"
2171:            f"满足 {blocker_text} 后，{config.reverse_travel_min_deg:.1f}° 到 {lock_deg:.1f}° 深拉区间才开放。"
2325:            "label": "流程开始",
2326:            "detail": "RA 从 7.0 ft 起步；TRA=0°；VDT=0%。",
2331:            "detail": "TRA 从 0° 开始以 10°/s 推向 -14°。",
2336:            "detail": "碰到 L4 条件限位；VDT 开始以 50%/s 从 0% 变化。",
2341:            "detail": "VDT 达到 90%，L4 / THR_LOCK 首次满足。",
2345:            "label": "监测结束",
2346:            "detail": "VDT=100%，主动监测流程完成。",
2351:            "detail": "展示保持段：RA 继续匀速降到 0 ft 后保持。",
2357:        "title": "受控状态监控时间线",
2364:            "这条监控图按用户定义的 RA -> TRA -> VDT 受控时间线生成；"
2365:            "整段时间已压缩为原来的 1/10；VDT 按现有 demo 反馈语义绘制为 0%-100% 监测量，"
2366:            "控制逻辑仍由 DeployController 评估。"
2391:    # P43-02.5 (2026-04-21): C919 E-TRAS · certified · P34+P38 真实 PDF 接入 ·
2470:            # --- LGCU 双余度 MLG_WOW input (PDF 表2) ---
2477:            # --- TLS (Translating Lock Sleeve · 双余度) · stowed=locked → unlocked=False ---
2482:            # --- PLS (Primary Lock Sleeve · 双余度) · stowed=locked=True ---
2485:            # --- Pylon locks (left+right · each 双余度) · stowed=locked → unlocked=False ---
2734:        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
2763:        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
2765:        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"

exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_h2_button_sweep.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "git diff main..7543d77 -- src/well_harness/static/workbench.html | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 0f30743..90f44c3 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -15,7 +15,7 @@
       <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
         <div class="workbench-collab-brand">
           <p class="eyebrow">控制逻辑工作台</p>
-          <h1>Control Logic Workbench</h1>
+          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
         </div>
         <div
           id="workbench-identity"
@@ -278,8 +278,8 @@
             Waiting for probe &amp; trace panel boot.
           </div>
           <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
-            <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
-            <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
+            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
+            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
           </div>
         </article>
 
@@ -331,7 +331,7 @@
       <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
         <header>
           <p class="eyebrow">标注收件箱</p>
-          <h2>Review Queue</h2>
+          <h2>审核队列 · Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
           <li>No proposals submitted yet.</li>
@@ -346,9 +346,9 @@
           data-role="KOGAMI"
           aria-controls="approval-center-panel"
         >
-          Approval Center
+          审批中心 · Approval Center
         </button>
-        <span>Approval actions are Kogami-only.</span>
+        <span>审批操作仅限 Kogami · Approval actions are Kogami-only.</span>
       </footer>
 
       <section
@@ -377,7 +377,7 @@
       >
         <header>
           <p class="eyebrow">审批中心</p>
-          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
+          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
         </header>
         <div class="workbench-approval-grid">
           <article class="workbench-approval-lane" data-approval-lane="pending">

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '899,936p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   899	# Task Group: AI FANTUI LogicMVP demo presentation, launch behavior, and leadership-facing communication
   900	
   901	scope: Keep the well-harness demo honest and user-facing, launch the real local UI instead of describing it abstractly, and translate project progress into plain Chinese for non-software audiences.
   902	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
   903	
   904	## Task 1: Present direct VDT controls and flatten the logic board without changing backend truth
   905	
   906	### rollout_summary_files
   907	
   908	- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, iterative refinement from user corrections)
   909	- rollout_summaries/2026-04-07T06-20-24-tGb4-round_92_direct_vdt_control_flatter_logic_board.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-20-24-019d6699-6f65-7712-ba2d-13ed0f64e87e.jsonl, updated_at=2026-04-08T14:50:07+00:00, thread_id=019d6699-6f65-7712-ba2d-13ed0f64e87e, final Round 92 reflow with preserved endpoint contracts)
   910	
   911	### keywords
   912	
   913	- VDT 模式, VDT 反馈, deploy_position_percent, manual_feedback_override, logic-note, 结果摘要先下沉, 诊断问答 frozen, /api/lever-snapshot, THR_LOCK, deploy_90_percent_vdt
   914	
   915	## Task 2: Rewrite materials narrowly when the user says to exclude Notion/control-tower framing
   916	
   917	### rollout_summary_files
   918	
   919	- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
   920	
   921	### keywords
   922	
   923	- 排除Notion中枢管控的巧思设计，单论这个控制逻辑智能化, 现状及问题, 改进措施或设想, 工程师负担, 可交互、可解释、可推演
   924	
   925	## Task 3: Start the real local UI, handle port conflicts, and return the final reachable address
   926	
   927	### rollout_summary_files
   928	
   929	- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
   930	- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
   931	
   932	### keywords
   933	
   934	- 启动UI, Address already in use, 8001, 8770, well_harness.demo_server, lsof -nP -iTCP, localhost, Well Harness 反推逻辑演示舱
   935	
   936	## Task 4: Reconstruct a truthful leadership-facing project story without Git history

 succeeded in 84808ms:
^C
Stopping well-harness demo UI.

  ✓ Inspect branch diff and changed files for E11-15b scope compliance
  ✓ Live-probe /workbench HTML and verify bilingual strings plus backend boundary
  → Summarize verdict and findings in P3 demo-presenter format
codex
**APPROVE_WITH_NITS**

- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17): the new h1 at line 18 now repeats the exact Chinese phrase already used by the eyebrow at line 17: `控制逻辑工作台` then `控制逻辑工作台 · Control Logic Workbench`. Nothing is wrong functionally, but for a cold demo open it reads slightly duplicated rather than intentionally composed.
- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
- `INFO` [test_workbench_chinese_h2_button_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_h2_button_sweep.py:173): the backend-boundary assertion is correct for this slice. The remediation text at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:743) is unchanged, and the sweep-specific Chinese UI terms do not leak into it. The comment at lines 184-186 should just be read narrowly, since `demo_server.py` already contains unrelated Chinese elsewhere.

The 7 shipped strings themselves read naturally enough for a Chinese-speaking engineering demo. `加载当前工单`, `审核队列`, `审批中心`, and `Kogami 提案审批` all land well. `快照当前状态` is a little tool-label literal, but still acceptable and not awkward enough to block.

Live probe passed: I started `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770`, then fetched `/workbench`; the served HTML contained all 7 bilingual strings at lines 18, 281, 282, 334, 349, 351, and 380. Red-line scope also checks out: `git diff --name-only main..7543d77` only shows `.planning/...`, `src/well_harness/static/workbench.html`, and the 2 test files. No changes touched `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, `workbench.css`, or `demo_server.py`. Targeted verification: `python3 -m pytest -q tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_dual_route.py tests/test_lever_snapshot_manual_override_guard.py` -> `73 passed in 11.67s`.

**P3 — Demo Presenter (Tier-B, E11-15b)**


tokens used
79,758
**APPROVE_WITH_NITS**

- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17): the new h1 at line 18 now repeats the exact Chinese phrase already used by the eyebrow at line 17: `控制逻辑工作台` then `控制逻辑工作台 · Control Logic Workbench`. Nothing is wrong functionally, but for a cold demo open it reads slightly duplicated rather than intentionally composed.
- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
- `INFO` [test_workbench_chinese_h2_button_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_h2_button_sweep.py:173): the backend-boundary assertion is correct for this slice. The remediation text at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:743) is unchanged, and the sweep-specific Chinese UI terms do not leak into it. The comment at lines 184-186 should just be read narrowly, since `demo_server.py` already contains unrelated Chinese elsewhere.

The 7 shipped strings themselves read naturally enough for a Chinese-speaking engineering demo. `加载当前工单`, `审核队列`, `审批中心`, and `Kogami 提案审批` all land well. `快照当前状态` is a little tool-label literal, but still acceptable and not awkward enough to block.

Live probe passed: I started `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770`, then fetched `/workbench`; the served HTML contained all 7 bilingual strings at lines 18, 281, 282, 334, 349, 351, and 380. Red-line scope also checks out: `git diff --name-only main..7543d77` only shows `.planning/...`, `src/well_harness/static/workbench.html`, and the 2 test files. No changes touched `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, `workbench.css`, or `demo_server.py`. Targeted verification: `python3 -m pytest -q tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_dual_route.py tests/test_lever_snapshot_manual_override_guard.py` -> `73 passed in 11.67s`.

**P3 — Demo Presenter (Tier-B, E11-15b)**


