2026-04-25T18:30:15.294513Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T18:30:15.294590Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc5e8-1bd8-7011-a77d-b960226efb5c
--------
user
You are Codex GPT-5.4 acting as **Persona P5 — Apps Engineer** (Tier-B single-persona pipeline, E11-07 sub-phase).

# Context — E11-07 Authority Contract banner

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-07-authority-banner-20260426`
**PR:** #22
**Worktree HEAD:** `c7131e9` (single commit on top of main `2e5bddc`)

## What E11-07 ships

Per E11-00-PLAN row E11-07: always-visible banner above the 3-column collab grid that announces the truth-engine read-only contract.

Banner copy:
- Icon: `🔒`
- Headline: `Truth Engine — Read Only`
- Rule: `Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值`
- Link: `v6.1 红线条款 →` → `/v6.1-redline`

New route: `GET /v6.1-redline` (and `/v6.1-redline.txt`) — serves plain-text excerpt of the v6.1 forbidden-paths section sourced live from `.planning/constitution.md`. Falls back to a small static excerpt if the constitution is unreachable.

## Files in scope

- `src/well_harness/static/workbench.html` — NEW `<aside id="workbench-authority-banner">` between the annotation toolbar and the 3-column grid (line ~235)
- `src/well_harness/static/workbench.css` — NEW `.workbench-authority-banner*` selectors
- `src/well_harness/demo_server.py` — NEW route + helper `_serve_v61_redline_excerpt()` (read-only)
- `tests/test_workbench_authority_banner.py` — NEW (12 tests covering banner presence, canonical copy, link target, route behavior, placement)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

## Your specific lens (P5 Apps Engineer)

Focus on:
- **Customer/new-engineer read**: would someone arriving on /workbench for the first time understand the contract from the banner alone? Is the wording unambiguous?
- **Link target reality**: clicking `v6.1 红线条款 →` must produce a real, truthful page. Verify the route serves something coherent.
- **Honesty**: the banner makes a strong "Read Only" claim. Verify nothing in this PR (or elsewhere on /workbench) contradicts it. Are the wow_a/b/c starter cards still POSTing? Is that a contradiction?
- **Drift risk**: the route reads `.planning/constitution.md` live. If the constitution clause heading drifts, does the fallback still produce a truthful excerpt?

## Verification status

- 1003 / 1003 pytest pass (12 new in `test_workbench_authority_banner.py`)
- `GET /v6.1-redline` returns 200 text/plain with the v6.1 forbidden-paths section
- Truth-engine red line preserved: only `static/`, `demo_server.py` route + helper, `tests/`, `.planning/` touched

## Out of scope

- Visual restyle (banner color/shadow/animation) — E11-15 polish scope
- Per-column micro-banners on each individual column — separate sub-phase
- Authentication on /v6.1-redline — read-only public excerpt by design

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..c7131e9` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/`.

Sign as: **P5 — Apps Engineer (Tier-B, E11-07)**
codex
Reviewing PR #22 in code-review mode. I’ll verify the touched surface, confirm the truth-engine red line against `main..c7131e9`, inspect the banner/route implementation, and run a live probe on `/v6.1-redline` before issuing a verdict.
exec
/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|E11-07|authority banner|v6.1-redline|authority contract" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-prompt.txt
?? uv.lock

exec
/bin/zsh -lc 'git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git rev-parse main' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
feat/e11-07-authority-banner-20260426
c7131e991fbd715c42684322798e8eac126a61e5
2e5bddc551e5f2986eb3563a675fca7c2033df0d

codex
Using `gsd-code-review` as the review workflow here. I’ve confirmed the branch/HEAD pair and there are unrelated untracked files in the worktree, so I’ll ignore those and keep the review scoped to the PR diff.
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
/bin/zsh -lc 'git diff --name-only main..c7131e9' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/demo_server.py
src/well_harness/static/workbench.css
src/well_harness/static/workbench.html
tests/test_workbench_authority_banner.py

exec
/bin/zsh -lc 'git diff --stat main..c7131e9' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-07-SURFACE-INVENTORY.md                    |  43 ++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/demo_server.py                    |  45 +++++++
 src/well_harness/static/workbench.css              |  55 ++++++++
 src/well_harness/static/workbench.html             |  25 ++++
 tests/test_workbench_authority_banner.py           | 146 +++++++++++++++++++++
 6 files changed, 315 insertions(+)

codex
The diff is narrow and the truth-engine files are untouched, which matches the red line. I’m reading the modified files plus the existing `/workbench` interaction paths now to check whether the new banner’s “Read Only” claim is contradicted anywhere nearby.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '210,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   221	        </button>
   222	      </aside>
   223	
   224	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   225	        <span class="workbench-annotation-toolbar-label">标注</span>
   226	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
   227	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
   228	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
   229	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
   230	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   231	          标记信号 工具激活
   232	        </span>
   233	      </section>
   234	
   235	      <aside
   236	        id="workbench-authority-banner"
   237	        class="workbench-authority-banner"
   238	        role="note"
   239	        aria-label="Truth-engine authority contract"
   240	      >
   241	        <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
   242	        <span class="workbench-authority-banner-headline">
   243	          Truth Engine — Read Only
   244	        </span>
   245	        <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
   246	        <span class="workbench-authority-banner-rule">
   247	          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
   248	        </span>
   249	        <a
   250	          class="workbench-authority-banner-link"
   251	          href="/v6.1-redline"
   252	          target="_blank"
   253	          rel="noopener"
   254	          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
   255	        >
   256	          v6.1 红线条款 →
   257	        </a>
   258	      </aside>
   259	
   260	      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
   261	        <article
   262	          id="workbench-control-panel"
   263	          class="workbench-collab-column workbench-annotation-surface"
   264	          data-column="control"
   265	          data-annotation-surface="control"
   266	          tabindex="0"
   267	        >
   268	          <header>
   269	            <p class="eyebrow">probe &amp; trace</p>
   270	            <h2>Probe &amp; Trace · 探针与追踪</h2>
   271	          </header>
   272	          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
   273	            Waiting for probe &amp; trace panel boot.
   274	          </div>
   275	          <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
   276	            <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
   277	            <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
   278	          </div>
   279	        </article>
   280	
   281	        <article
   282	          id="workbench-document-panel"
   283	          class="workbench-collab-column workbench-annotation-surface"
   284	          data-column="document"
   285	          data-annotation-surface="document"
   286	          tabindex="0"
   287	        >
   288	          <header>
   289	            <p class="eyebrow">annotate &amp; propose</p>
   290	            <h2>Annotate &amp; Propose · 标注与提案</h2>
   291	          </header>
   292	          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
   293	            Waiting for annotate &amp; propose panel boot.
   294	          </div>
   295	          <div class="workbench-collab-document">
   296	            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
   297	            <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
   298	          </div>
   299	        </article>
   300	
   301	        <article
   302	          id="workbench-circuit-panel"
   303	          class="workbench-collab-column workbench-annotation-surface"
   304	          data-column="circuit"
   305	          data-annotation-surface="circuit"
   306	          tabindex="0"
   307	        >
   308	          <header>
   309	            <p class="eyebrow">hand off &amp; track</p>
   310	            <h2>Hand off &amp; Track · 移交与跟踪</h2>
   311	          </header>
   312	          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
   313	            Waiting for hand off &amp; track panel boot.
   314	          </div>
   315	          <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
   316	            <span>SW1</span>
   317	            <span>Logic 1</span>
   318	            <span>Logic 2</span>
   319	            <span>Logic 3</span>
   320	            <span>Logic 4</span>

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.css | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "nl -ba tests/test_workbench_authority_banner.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-07 — Authority Contract banner regression lock.
     2	
     3	Locks the always-visible banner that announces the truth-engine
     4	read-only contract on /workbench, plus the /v6.1-redline route that
     5	serves the constitution clause the banner links to.
     6	
     7	Per E11-00-PLAN row E11-07: pure-UI banner, no truth-engine code
     8	changes. The contract is twofold —
     9	  1. The banner is on the /workbench shell with the canonical copy.
    10	  2. The link target resolves to a real text excerpt sourced from
    11	     .planning/constitution.md (so the banner is not a dead link).
    12	"""
    13	
    14	from __future__ import annotations
    15	
    16	import http.client
    17	import threading
    18	from http.server import ThreadingHTTPServer
    19	from pathlib import Path
    20	
    21	import pytest
    22	
    23	from well_harness.demo_server import DemoRequestHandler
    24	
    25	
    26	REPO_ROOT = Path(__file__).resolve().parents[1]
    27	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    28	
    29	
    30	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    31	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    32	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    33	    thread.start()
    34	    return server, thread
    35	
    36	
    37	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str, str]:
    38	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    39	    connection.request("GET", path)
    40	    response = connection.getresponse()
    41	    body = response.read().decode("utf-8")
    42	    content_type = response.getheader("Content-Type", "")
    43	    return response.status, body, content_type
    44	
    45	
    46	@pytest.fixture
    47	def server():
    48	    s, t = _start_demo_server()
    49	    try:
    50	        yield s
    51	    finally:
    52	        s.shutdown()
    53	        s.server_close()
    54	        t.join(timeout=2)
    55	
    56	
    57	# ─── 1. Banner is present on /workbench ──────────────────────────────
    58	
    59	
    60	def test_workbench_html_has_authority_banner() -> None:
    61	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    62	    assert 'id="workbench-authority-banner"' in html
    63	    assert 'role="note"' in html
    64	    # Always-visible: no data-dismissed attribute, no conditional class
    65	    # toggling. The banner stays on screen for the entire session.
    66	    assert "data-trust-banner-dismiss" not in (
    67	        html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
    68	    )
    69	
    70	
    71	@pytest.mark.parametrize(
    72	    "phrase",
    73	    [
    74	        "🔒",
    75	        "Truth Engine — Read Only",
    76	        "Propose 不修改",
    77	        "工程师只能提交 ticket / proposal",
    78	        "v6.1 红线条款",
    79	    ],
    80	)
    81	def test_workbench_html_banner_carries_canonical_copy(phrase: str) -> None:
    82	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    83	    assert phrase in html, f"missing canonical banner copy: {phrase}"
    84	
    85	
    86	def test_workbench_html_banner_links_to_v61_redline_route() -> None:
    87	    """The banner link must point at the in-repo route, not at an
    88	    external GitHub URL or a stale /.planning/ path that the static
    89	    handler would 404 on."""
    90	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    91	    banner_block = html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
    92	    assert 'href="/v6.1-redline"' in banner_block
    93	
    94	
    95	# ─── 2. /v6.1-redline route works ────────────────────────────────────
    96	
    97	
    98	def test_v61_redline_route_returns_200_text(server) -> None:
    99	    status, body, content_type = _get(server, "/v6.1-redline")
   100	    assert status == 200
   101	    assert "text/plain" in content_type
   102	    assert "v6.1" in body or "truth-engine" in body or "红线" in body
   103	
   104	
   105	def test_v61_redline_excerpt_carries_truth_engine_paths(server) -> None:
   106	    """Whatever excerpt the route returns, it must name the four paths
   107	    that are off-limits — controller/runner/models/adapters."""
   108	    _, body, _ = _get(server, "/v6.1-redline")
   109	    # At least one of the canonical truth-engine path names must appear,
   110	    # whether in the constitution excerpt or in the static fallback.
   111	    assert any(name in body for name in ("controller", "runner", "models", "adapters")), (
   112	        f"excerpt missing truth-engine path names; got {body[:200]!r}"
   113	    )
   114	
   115	
   116	def test_v61_redline_route_alias_with_extension(server) -> None:
   117	    """Both /v6.1-redline and /v6.1-redline.txt should resolve."""
   118	    status, body, _ = _get(server, "/v6.1-redline.txt")
   119	    assert status == 200
   120	    assert body  # non-empty
   121	
   122	
   123	# ─── 3. Live-served /workbench renders banner end-to-end ────────────
   124	
   125	
   126	def test_workbench_route_serves_authority_banner(server) -> None:
   127	    status, html, _ = _get(server, "/workbench")
   128	    assert status == 200
   129	    assert 'id="workbench-authority-banner"' in html
   130	    assert 'href="/v6.1-redline"' in html
   131	    assert "Truth Engine — Read Only" in html
   132	
   133	
   134	# ─── 4. Banner placement: above the 3-column collab grid ────────────
   135	
   136	
   137	def test_workbench_banner_appears_before_collab_grid() -> None:
   138	    """The banner must sit ABOVE the 3-column grid so it frames the
   139	    controller / circuit columns, not below them."""
   140	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   141	    banner_pos = html.find('id="workbench-authority-banner"')
   142	    grid_pos = html.find('class="workbench-collab-grid"')
   143	    assert banner_pos != -1 and grid_pos != -1
   144	    assert banner_pos < grid_pos, (
   145	        "authority banner must precede the 3-column collab grid"
   146	    )

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '260,420p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   260	
   261	        # E11-07 (2026-04-26): Authority Contract banner link target.
   262	        # Serves the v6.1 truth-engine red-line clause as plain text so
   263	        # the banner's "v6.1 红线条款 →" link resolves to a real, in-repo
   264	        # excerpt rather than a 404. Read-only; no truth-engine mutation.
   265	        if parsed.path in ("/v6.1-redline", "/v6.1-redline.txt"):
   266	            self._serve_v61_redline_excerpt()
   267	            return
   268	
   269	        relative_path = unquote(parsed.path.lstrip("/"))
   270	        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
   271	            self._serve_static(relative_path)
   272	            return
   273	
   274	        # P19.8: Hardware schema discovery
   275	        if parsed.path == HARDWARE_SCHEMA_PATH:
   276	            system_id = parse_qs(parsed.query).get("system_id", ["thrust-reverser"])[0]
   277	            self._handle_hardware_schema(system_id=system_id)
   278	            return
   279	
   280	        if parsed.path == FANTUI_LOG_PATH:
   281	            # records() is internally locked; the copy it returns is
   282	            # self-contained so JSON serialization can run unlocked.
   283	            recs = _FANTUI_SYSTEM.records()
   284	            self._send_json(200, recs)
   285	            return
   286	
   287	        if parsed.path == FANTUI_STATE_PATH:
   288	            # Atomic snapshot — one lock acquisition covers all fields
   289	            # so callers don't observe torn state.
   290	            self._send_json(200, _FANTUI_SYSTEM.snapshot())
   291	            return
   292	
   293	        self._send_json(404, {"error": "not_found"})
   294	
   295	    def do_POST(self):
   296	        parsed = urlparse(self.path)
   297	        if parsed.path not in {
   298	            "/api/demo",
   299	            "/api/lever-snapshot",
   300	            "/api/timeline-simulate",
   301	            SYSTEM_SNAPSHOT_POST_PATH,
   302	            WORKBENCH_BUNDLE_PATH,
   303	            WORKBENCH_REPAIR_PATH,
   304	            WORKBENCH_ARCHIVE_RESTORE_PATH,
   305	            DIAGNOSIS_RUN_PATH,
   306	            MONTE_CARLO_RUN_PATH,
   307	            HARDWARE_SCHEMA_PATH,
   308	            SENSITIVITY_SWEEP_PATH,
   309	            FANTUI_TICK_PATH,
   310	            FANTUI_RESET_PATH,
   311	            FANTUI_SET_VDT_PATH,
   312	        }:
   313	            self._send_json(404, {"error": "not_found"})
   314	            return
   315	
   316	        try:
   317	            content_length = int(self.headers.get("Content-Length", "0") or "0")
   318	        except ValueError:
   319	            self._send_json(400, {"error": "invalid_content_length"})
   320	            return
   321	
   322	        # Guard: reject oversized payloads before reading
   323	        if content_length and content_length > _MAX_DOCUMENT_BYTES:
   324	            self._send_json(413, {"error": "payload_too_large", "message": f"Request body exceeds maximum of {_MAX_DOCUMENT_BYTES} bytes."})
   325	            return
   326	
   327	        # Guard: enforce Content-Type whitelist (defense-in-depth; browser enforces this too)
   328	        content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
   329	        allowed_types = {"application/json"}
   330	        if content_type and content_type not in allowed_types:
   331	            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json."})
   332	            return
   333	
   334	        try:
   335	            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
   336	            request_payload = json.loads(body)
   337	        except (UnicodeDecodeError, json.JSONDecodeError):
   338	            self._send_json(400, {"error": "invalid_json"})
   339	            return
   340	        if not isinstance(request_payload, dict):
   341	            self._send_json(400, {"error": "invalid_json_object"})
   342	            return
   343	
   344	        if parsed.path == "/api/lever-snapshot":
   345	            lever_inputs, error_payload = parse_lever_snapshot_request(request_payload)
   346	            if error_payload is not None:
   347	                # E11-14: parser may attach `_status` (e.g., 409 for manual_override_unsigned);
   348	                # default to 400 for legacy parse errors.
   349	                status_code = error_payload.pop("_status", 400)
   350	                self._send_json(status_code, error_payload)
   351	                return
   352	
   353	            fault_injections = lever_inputs.pop("_fault_injections", None)
   354	            self._send_json(
   355	                200,
   356	                lever_snapshot_payload(
   357	                    **lever_inputs,
   358	                    fault_injections=fault_injections,
   359	                ),
   360	            )
   361	            return
   362	        if parsed.path == "/api/timeline-simulate":
   363	            result = _handle_timeline_simulate(request_payload)
   364	            status = result.pop("_status", 200)
   365	            self._send_json(status, result)
   366	            return
   367	        if parsed.path == FANTUI_TICK_PATH:
   368	            status, result = _handle_fantui_tick(request_payload)
   369	            self._send_json(status, result)
   370	            return
   371	        if parsed.path == FANTUI_RESET_PATH:
   372	            _FANTUI_SYSTEM.reset()
   373	            self._send_json(200, {"ok": True, "t_s": 0.0})
   374	            return
   375	        if parsed.path == FANTUI_SET_VDT_PATH:
   376	            # E11-14 R2 (P2 BLOCKER #2, 2026-04-25): set_vdt is a test probe
   377	            # that bypasses the /api/lever-snapshot sign-off contract. The
   378	            # endpoint stays available for the fan-console debug UI but now
   379	            # requires an explicit `test_probe_acknowledgment` field so a
   380	            # caller cannot accidentally use it to inject manual feedback
   381	            # while believing they're going through the authority chain.
   382	            # The 409 message explains the alternative (use /api/lever-snapshot
   383	            # with sign-off when authority semantics matter).
   384	            ack = request_payload.get("test_probe_acknowledgment")
   385	            if ack is not True:
   386	                self._send_json(
   387	                    409,
   388	                    {
   389	                        "error": "test_probe_unacknowledged",
   390	                        "message": (
   391	                            "/api/fantui/set_vdt is a test probe that bypasses the "
   392	                            "manual_feedback_override authority chain. To use it from "
   393	                            "tests/dev tooling, pass test_probe_acknowledgment=true. "
   394	                            "For authoritative manual feedback, use /api/lever-snapshot "
   395	                            "with feedback_mode=manual_feedback_override + sign-off."
   396	                        ),
   397	                        # E11-14 R3 (P2 R2 IMPORTANT #4 fix, 2026-04-25): every 409
   398	                        # path must disclose the deferred replay/freshness gap so
   399	                        # callers don't mistake structural validation for latched
   400	                        # authorization. set_vdt's bypass nature is itself a live
   401	                        # residual risk surface.
   402	                        "residual_risk": (
   403	                            "Test-probe bypass remains structural; "
   404	                            "test_probe_acknowledgment=true is not authentication. "
   405	                            "Replay/nonce/freshness validation and one-shot latching are "
   406	                            "scoped to E11-16 (approval endpoint hardening)."
   407	                        ),
   408	                    },
   409	                )
   410	                return
   411	            try:
   412	                pct = float(request_payload.get("deploy_position_percent", 0))
   413	            except (TypeError, ValueError):
   414	                self._send_json(400, {"error": "deploy_position_percent must be a number"})
   415	                return
   416	            try:
   417	                _FANTUI_SYSTEM.set_plant_position(pct)
   418	            except ValueError as exc:
   419	                self._send_json(400, {"error": str(exc)})
   420	                return

exec
/bin/zsh -lc "rg -n \"v6\\.1-redline|_serve_v61_redline_excerpt|constitution|forbidden-paths|wow_a|wow_b|wow_c|fetch\\(|POST|proposal|ticket|read only|Read Only|truth_engine|feedback-mode|ticket / proposal\" src/well_harness/demo_server.py src/well_harness/static/workbench.html src/well_harness/static/workbench.css src/well_harness/static/workbench.js tests/test_workbench_authority_banner.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_authority_banner.py:4:read-only contract on /workbench, plus the /v6.1-redline route that
tests/test_workbench_authority_banner.py:5:serves the constitution clause the banner links to.
tests/test_workbench_authority_banner.py:11:     .planning/constitution.md (so the banner is not a dead link).
tests/test_workbench_authority_banner.py:75:        "Truth Engine — Read Only",
tests/test_workbench_authority_banner.py:77:        "工程师只能提交 ticket / proposal",
tests/test_workbench_authority_banner.py:92:    assert 'href="/v6.1-redline"' in banner_block
tests/test_workbench_authority_banner.py:95:# ─── 2. /v6.1-redline route works ────────────────────────────────────
tests/test_workbench_authority_banner.py:99:    status, body, content_type = _get(server, "/v6.1-redline")
tests/test_workbench_authority_banner.py:105:def test_v61_redline_excerpt_carries_truth_engine_paths(server) -> None:
tests/test_workbench_authority_banner.py:108:    _, body, _ = _get(server, "/v6.1-redline")
tests/test_workbench_authority_banner.py:110:    # whether in the constitution excerpt or in the static fallback.
tests/test_workbench_authority_banner.py:117:    """Both /v6.1-redline and /v6.1-redline.txt should resolve."""
tests/test_workbench_authority_banner.py:118:    status, body, _ = _get(server, "/v6.1-redline.txt")
tests/test_workbench_authority_banner.py:130:    assert 'href="/v6.1-redline"' in html
tests/test_workbench_authority_banner.py:131:    assert "Truth Engine — Read Only" in html
src/well_harness/static/workbench.css:66:/* E11-13: feedback-mode chip with advisory affordance.
src/well_harness/static/workbench.css:70:.workbench-feedback-mode-chip {
src/well_harness/static/workbench.css:78:.workbench-feedback-mode-chip strong {
src/well_harness/static/workbench.css:82:.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] {
src/well_harness/static/workbench.css:87:.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] strong {
src/well_harness/static/workbench.css:91:.workbench-feedback-mode-dot {
src/well_harness/static/workbench.css:102:.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"] .workbench-feedback-mode-dot {
src/well_harness/static/workbench.css:172:/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
src/well_harness/static/workbench.css:307:   data-feedback-mode = manual_feedback_override AND not session-dismissed.
src/well_harness/static/workbench.css:322:.workbench-trust-banner[data-feedback-mode="truth_engine"],
src/well_harness/static/workbench.js:398:    const response = await fetch(workbenchRecentArchivesPath, {method: "GET"});
src/well_harness/static/workbench.js:1559:    const response = await fetch(workbenchRepairPath, {
src/well_harness/static/workbench.js:1560:      method: "POST",
src/well_harness/static/workbench.js:2205:    const response = await fetch(workbenchArchiveRestorePath, {
src/well_harness/static/workbench.js:2206:      method: "POST",
src/well_harness/static/workbench.js:3331:  sourceMode = "当前来源：`POST /api/workbench/bundle`。",
src/well_harness/static/workbench.js:3481:  const response = await fetch(workbenchBootstrapPath, {method: "GET"});
src/well_harness/static/workbench.js:3538:    const response = await fetch(workbenchBundlePath, {
src/well_harness/static/workbench.js:3539:      method: "POST",
src/well_harness/static/workbench.js:3765:// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
src/well_harness/static/workbench.js:3774:    banner.setAttribute("data-feedback-mode", mode);
src/well_harness/static/workbench.js:3779:  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
src/well_harness/static/workbench.js:3783:  const chip = document.getElementById("workbench-feedback-mode");
src/well_harness/static/workbench.js:3785:    chip.setAttribute("data-feedback-mode", mode);
src/well_harness/static/workbench.js:3788:      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
src/well_harness/static/workbench.js:3796:  const chip = document.getElementById("workbench-feedback-mode");
src/well_harness/static/workbench.js:3801:  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
src/well_harness/static/workbench.js:3816:// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
src/well_harness/static/workbench.js:3817:// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
src/well_harness/static/workbench.js:3819:// suites. One click → POST (with bounded timeout) → single-line summary in
src/well_harness/static/workbench.js:3829:  wow_a: {
src/well_harness/static/workbench.js:3831:    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
src/well_harness/static/workbench.js:3858:  wow_b: {
src/well_harness/static/workbench.js:3869:  wow_c: {
src/well_harness/static/workbench.js:3897:  result.textContent = `POST ${scenario.endpoint} ...`;
src/well_harness/static/workbench.js:3907:    const response = await fetch(scenario.endpoint, {
src/well_harness/static/workbench.js:3908:      method: "POST",
src/well_harness/static/workbench.js:3972:    const response = await fetch(WORKBENCH_STATE_OF_WORLD_PATH, {
src/well_harness/static/workbench.js:3989:    writeField("truth_engine_sha", payload.truth_engine_sha);
src/well_harness/demo_server.py:68:SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
src/well_harness/demo_server.py:196:# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
src/well_harness/demo_server.py:265:        if parsed.path in ("/v6.1-redline", "/v6.1-redline.txt"):
src/well_harness/demo_server.py:266:            self._serve_v61_redline_excerpt()
src/well_harness/demo_server.py:295:    def do_POST(self):
src/well_harness/demo_server.py:301:            SYSTEM_SNAPSHOT_POST_PATH,
src/well_harness/demo_server.py:423:        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
src/well_harness/demo_server.py:603:    def _serve_v61_redline_excerpt(self):
src/well_harness/demo_server.py:605:        as plain text. Sourced from .planning/constitution.md so the demo
src/well_harness/demo_server.py:606:        ships the same words the constitution does, with no drift risk."""
src/well_harness/demo_server.py:608:        constitution = repo_root / ".planning" / "constitution.md"
src/well_harness/demo_server.py:610:            full_text = constitution.read_text(encoding="utf-8")
src/well_harness/demo_server.py:627:                    "may propose changes via ticket / proposal — they may "
src/well_harness/demo_server.py:629:                    ".planning/constitution.md §v6.1 Solo Autonomy Delegation."
src/well_harness/demo_server.py:633:                "Truth-engine 红线 source file (.planning/constitution.md) "
src/well_harness/demo_server.py:718:# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
src/well_harness/demo_server.py:732:    ticket_id = request_payload.get("ticket_id")
src/well_harness/demo_server.py:742:                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
src/well_harness/demo_server.py:760:    if not isinstance(ticket_id, str) or not ticket_id.strip():
src/well_harness/demo_server.py:761:        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
src/well_harness/demo_server.py:770:    signoff_ticket = signoff.get("ticket_id")
src/well_harness/demo_server.py:781:    if not isinstance(signoff_ticket, str) or not signoff_ticket.strip():
src/well_harness/demo_server.py:783:            "manual_override_signoff.ticket_id",
src/well_harness/demo_server.py:784:            "manual_override_signoff.ticket_id must be a non-empty string.",
src/well_harness/demo_server.py:786:    if signoff_ticket.strip() != ticket_id.strip():
src/well_harness/demo_server.py:788:            "manual_override_signoff.ticket_id",
src/well_harness/demo_server.py:789:            "manual_override_signoff.ticket_id must match the request's ticket_id.",
src/well_harness/demo_server.py:1359:def _truth_engine_short_sha() -> str:
src/well_harness/demo_server.py:1435:        "truth_engine_sha": _truth_engine_short_sha(),
src/well_harness/demo_server.py:1436:        "truth_engine_sha_source": "git rev-parse --short HEAD",
src/well_harness/static/workbench.html:24:        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
src/well_harness/static/workbench.html:29:          id="workbench-feedback-mode"
src/well_harness/static/workbench.html:30:          class="workbench-collab-chip workbench-feedback-mode-chip"
src/well_harness/static/workbench.html:31:          data-feedback-mode="manual_feedback_override"
src/well_harness/static/workbench.html:38:          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
src/well_harness/static/workbench.html:58:        <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
src/well_harness/static/workbench.html:61:          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
src/well_harness/static/workbench.html:95:            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
src/well_harness/static/workbench.html:101:            data-wow-id="wow_a"
src/well_harness/static/workbench.html:105:              <span class="workbench-wow-tag">wow_a</span>
src/well_harness/static/workbench.html:109:              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
src/well_harness/static/workbench.html:112:              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
src/well_harness/static/workbench.html:118:              data-wow-id="wow_a"
src/well_harness/static/workbench.html:120:              一键运行 wow_a
src/well_harness/static/workbench.html:124:              data-wow-result-for="wow_a"
src/well_harness/static/workbench.html:133:            data-wow-id="wow_b"
src/well_harness/static/workbench.html:137:              <span class="workbench-wow-tag">wow_b</span>
src/well_harness/static/workbench.html:141:              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
src/well_harness/static/workbench.html:148:              data-wow-id="wow_b"
src/well_harness/static/workbench.html:150:              一键运行 wow_b
src/well_harness/static/workbench.html:154:              data-wow-result-for="wow_b"
src/well_harness/static/workbench.html:163:            data-wow-id="wow_c"
src/well_harness/static/workbench.html:167:              <span class="workbench-wow-tag">wow_c</span>
src/well_harness/static/workbench.html:171:              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
src/well_harness/static/workbench.html:178:              data-wow-id="wow_c"
src/well_harness/static/workbench.html:180:              一键运行 wow_c
src/well_harness/static/workbench.html:184:              data-wow-result-for="wow_c"
src/well_harness/static/workbench.html:197:        data-feedback-mode="manual_feedback_override"
src/well_harness/static/workbench.html:243:          Truth Engine — Read Only
src/well_harness/static/workbench.html:247:          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
src/well_harness/static/workbench.html:251:          href="/v6.1-redline"
src/well_harness/static/workbench.html:254:          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
src/well_harness/static/workbench.html:332:          <li>No proposals submitted yet.</li>
src/well_harness/static/workbench.html:362:            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1650,1765p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1650	            "field": field_name,
  1651	            "message": f"{field_name} must be numeric.",
  1652	        }
  1653	    if not math.isfinite(value):
  1654	        return default, {
  1655	            "error": "invalid_numeric_value",
  1656	            "field": field_name,
  1657	            "message": f"{field_name} must be a finite number.",
  1658	        }
  1659	    if value <= 0:
  1660	        return default, {
  1661	            "error": "invalid_workbench_request",
  1662	            "field": field_name,
  1663	            "message": f"{field_name} must be greater than zero.",
  1664	        }
  1665	    return value, None
  1666	
  1667	
  1668	def _optional_request_object(payload: dict, field_name: str) -> tuple[dict | None, dict | None]:
  1669	    raw_value = payload.get(field_name)
  1670	    if raw_value is None:
  1671	        return None, None
  1672	    if not isinstance(raw_value, dict):
  1673	        return None, {
  1674	            "error": "invalid_workbench_request",
  1675	            "field": field_name,
  1676	            "message": f"{field_name} must be a JSON object when provided.",
  1677	        }
  1678	    return raw_value, None
  1679	
  1680	
  1681	def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
  1682	    packet_payload = request_payload.get("packet_payload")
  1683	    if not isinstance(packet_payload, dict):
  1684	        return None, {
  1685	            "error": "invalid_workbench_request",
  1686	            "field": "packet_payload",
  1687	            "message": "packet_payload must be a JSON object.",
  1688	        }
  1689	    try:
  1690	        packet = intake_packet_from_dict(packet_payload)
  1691	    except ValueError as exc:
  1692	        return None, {
  1693	            "error": "invalid_workbench_packet",
  1694	            "field": "packet_payload",
  1695	            "message": str(exc),
  1696	        }
  1697	
  1698	    scenario_id, error_payload = _optional_request_str(request_payload, "scenario_id")
  1699	    if error_payload is not None:
  1700	        return None, error_payload
  1701	    fault_mode_id, error_payload = _optional_request_str(request_payload, "fault_mode_id")
  1702	    if error_payload is not None:
  1703	        return None, error_payload
  1704	    observed_symptoms, error_payload = _optional_request_str(request_payload, "observed_symptoms")
  1705	    if error_payload is not None:
  1706	        return None, error_payload
  1707	    evidence_links, error_payload = _optional_request_string_list(request_payload, "evidence_links")
  1708	    if error_payload is not None:
  1709	        return None, error_payload
  1710	    confirmed_root_cause, error_payload = _optional_request_str(request_payload, "confirmed_root_cause")
  1711	    if error_payload is not None:
  1712	        return None, error_payload
  1713	    repair_action, error_payload = _optional_request_str(request_payload, "repair_action")
  1714	    if error_payload is not None:
  1715	        return None, error_payload
  1716	    validation_after_fix, error_payload = _optional_request_str(request_payload, "validation_after_fix")
  1717	    if error_payload is not None:
  1718	        return None, error_payload
  1719	    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
  1720	    if error_payload is not None:
  1721	        return None, error_payload
  1722	    suggested_logic_change, error_payload = _optional_request_str(request_payload, "suggested_logic_change")
  1723	    if error_payload is not None:
  1724	        return None, error_payload
  1725	    reliability_gain_hypothesis, error_payload = _optional_request_str(
  1726	        request_payload,
  1727	        "reliability_gain_hypothesis",
  1728	    )
  1729	    if error_payload is not None:
  1730	        return None, error_payload
  1731	    guardrail_note, error_payload = _optional_request_str(request_payload, "guardrail_note")
  1732	    if error_payload is not None:
  1733	        return None, error_payload
  1734	    sample_period_s, error_payload = _optional_request_float(
  1735	        request_payload,
  1736	        "sample_period_s",
  1737	        default=0.5,
  1738	    )
  1739	    if error_payload is not None:
  1740	        return None, error_payload
  1741	    workspace_handoff, error_payload = _optional_request_object(request_payload, "workspace_handoff")
  1742	    if error_payload is not None:
  1743	        return None, error_payload
  1744	    workspace_snapshot, error_payload = _optional_request_object(request_payload, "workspace_snapshot")
  1745	    if error_payload is not None:
  1746	        return None, error_payload
  1747	    if workspace_handoff is None and workspace_snapshot is not None:
  1748	        derived_handoff = workspace_snapshot.get("handoff")
  1749	        if isinstance(derived_handoff, dict):
  1750	            workspace_handoff = derived_handoff
  1751	
  1752	    archive_bundle_raw = request_payload.get("archive_bundle", False)
  1753	    archive_bundle = isinstance(archive_bundle_raw, bool) and archive_bundle_raw is True
  1754	    try:
  1755	        bundle = build_workbench_bundle(
  1756	            packet,
  1757	            scenario_id=scenario_id,
  1758	            fault_mode_id=fault_mode_id,
  1759	            observed_symptoms=observed_symptoms,
  1760	            evidence_links=evidence_links or (),
  1761	            confirmed_root_cause=confirmed_root_cause,
  1762	            repair_action=repair_action,
  1763	            validation_after_fix=validation_after_fix,
  1764	            residual_risk=residual_risk,
  1765	            suggested_logic_change=suggested_logic_change,

exec
/bin/zsh -lc "rg -n \"wow_a|wow_b|wow_c|workbench-wow|workbench starter|starter card|api/diagnosis/run|api/monte-carlo/run|api/sensitivity-sweep|api/workbench|ticket|proposal\" src/well_harness/static src/well_harness/demo_server.py tests | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/demo_server.py:71:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
src/well_harness/demo_server.py:72:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
src/well_harness/demo_server.py:73:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
src/well_harness/demo_server.py:74:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
src/well_harness/demo_server.py:75:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
src/well_harness/demo_server.py:77:WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
src/well_harness/demo_server.py:94:DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
src/well_harness/demo_server.py:96:MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
src/well_harness/demo_server.py:99:SENSITIVITY_SWEEP_PATH = "/api/sensitivity-sweep"
src/well_harness/demo_server.py:627:                    "may propose changes via ticket / proposal — they may "
src/well_harness/demo_server.py:718:# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
src/well_harness/demo_server.py:732:    ticket_id = request_payload.get("ticket_id")
src/well_harness/demo_server.py:742:                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
src/well_harness/demo_server.py:760:    if not isinstance(ticket_id, str) or not ticket_id.strip():
src/well_harness/demo_server.py:761:        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
src/well_harness/demo_server.py:770:    signoff_ticket = signoff.get("ticket_id")
src/well_harness/demo_server.py:781:    if not isinstance(signoff_ticket, str) or not signoff_ticket.strip():
src/well_harness/demo_server.py:783:            "manual_override_signoff.ticket_id",
src/well_harness/demo_server.py:784:            "manual_override_signoff.ticket_id must be a non-empty string.",
src/well_harness/demo_server.py:786:    if signoff_ticket.strip() != ticket_id.strip():
src/well_harness/demo_server.py:788:            "manual_override_signoff.ticket_id",
src/well_harness/demo_server.py:789:            "manual_override_signoff.ticket_id must match the request's ticket_id.",
src/well_harness/static/workbench.css:172:/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
src/well_harness/static/workbench.css:176:.workbench-wow-starters {
src/well_harness/static/workbench.css:184:.workbench-wow-starters-header {
src/well_harness/static/workbench.css:188:.workbench-wow-starters-header h2 {
src/well_harness/static/workbench.css:194:.workbench-wow-starters-sub {
src/well_harness/static/workbench.css:200:.workbench-wow-starters-grid {
src/well_harness/static/workbench.css:207:  .workbench-wow-starters-grid {
src/well_harness/static/workbench.css:212:.workbench-wow-card {
src/well_harness/static/workbench.css:222:.workbench-wow-card header {
src/well_harness/static/workbench.css:228:.workbench-wow-card h3 {
src/well_harness/static/workbench.css:234:.workbench-wow-tag {
src/well_harness/static/workbench.css:245:.workbench-wow-card-desc {
src/well_harness/static/workbench.css:252:.workbench-wow-card-desc code {
src/well_harness/static/workbench.css:260:.workbench-wow-run-button {
src/well_harness/static/workbench.css:272:.workbench-wow-run-button:hover:not([disabled]) {
src/well_harness/static/workbench.css:276:.workbench-wow-run-button[disabled] {
src/well_harness/static/workbench.css:281:.workbench-wow-result {
src/well_harness/static/workbench.css:296:.workbench-wow-result[data-wow-state="ok"] {
src/well_harness/static/workbench.css:301:.workbench-wow-result[data-wow-state="error"] {
tests/test_workbench_start.py:8:  future E2E coverage and ticket templates can target it.
tests/test_workbench_start.py:174:    """R1-F1: dead hash fragments (#wow_a / #probe / #repro / #audit) had to go.
tests/test_workbench_start.py:219:    assert "wow_a fixture" in body
src/well_harness/static/adversarial_test.py:15:# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
src/well_harness/static/adversarial_test.py:27:    "ticket_id": "WB-ADVERSARIAL",
src/well_harness/static/adversarial_test.py:31:        "ticket_id": "WB-ADVERSARIAL",
tests/test_workbench_approval_center.py:7:from well_harness.workbench.proposals import build_annotation_proposal
tests/test_workbench_approval_center.py:13:def _proposal() -> dict:
tests/test_workbench_approval_center.py:14:    return build_annotation_proposal(
tests/test_workbench_approval_center.py:15:        proposal_id="prop_approval_001",
tests/test_workbench_approval_center.py:21:        ticket_id="WB-E08-APPROVAL",
tests/test_workbench_approval_center.py:31:def test_approval_center_submits_proposal_and_appends_audit_event(tmp_path):
tests/test_workbench_approval_center.py:33:    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)
tests/test_workbench_approval_center.py:35:    result = center.submit(_proposal(), actor="engineer-a")
tests/test_workbench_approval_center.py:38:    assert result["proposal_id"] == "prop_approval_001"
tests/test_workbench_approval_center.py:41:    assert events[-1]["type"] == "proposal.submitted"
tests/test_workbench_approval_center.py:42:    assert events[-1]["proposal_id"] == "prop_approval_001"
tests/test_workbench_approval_center.py:47:    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=tmp_path / "audit/events.jsonl")
tests/test_workbench_approval_center.py:48:    center.submit(_proposal(), actor="engineer-a")
tests/test_workbench_approval_center.py:56:    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)
tests/test_workbench_approval_center.py:57:    center.submit(_proposal(), actor="engineer-a")
tests/test_workbench_approval_center.py:63:    assert events[-1]["type"] == "proposal.accepted"
tests/test_workbench_approval_center.py:66:    second = build_annotation_proposal(
tests/test_workbench_approval_center.py:67:        proposal_id="prop_approval_002",
tests/test_workbench_approval_center.py:73:        ticket_id="WB-E08-APPROVAL",
tests/test_workbench_approval_center.py:81:    assert _read_events(audit_path)[-1]["type"] == "proposal.rejected"
src/well_harness/static/workbench.js:1:const workbenchBootstrapPath = "/api/workbench/bootstrap";
src/well_harness/static/workbench.js:2:const workbenchBundlePath = "/api/workbench/bundle";
src/well_harness/static/workbench.js:3:const workbenchRepairPath = "/api/workbench/repair";
src/well_harness/static/workbench.js:4:const workbenchArchiveRestorePath = "/api/workbench/archive-restore";
src/well_harness/static/workbench.js:5:const workbenchRecentArchivesPath = "/api/workbench/recent-archives";
src/well_harness/static/workbench.js:3331:  sourceMode = "当前来源：`POST /api/workbench/bundle`。",
src/well_harness/static/workbench.js:3816:// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
src/well_harness/static/workbench.js:3817:// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
src/well_harness/static/workbench.js:3829:  wow_a: {
src/well_harness/static/workbench.js:3831:    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
src/well_harness/static/workbench.js:3858:  wow_b: {
src/well_harness/static/workbench.js:3859:    endpoint: "/api/monte-carlo/run",
src/well_harness/static/workbench.js:3869:  wow_c: {
src/well_harness/static/workbench.js:3870:    endpoint: "/api/diagnosis/run",
src/well_harness/static/workbench.js:3885:    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
src/well_harness/static/workbench.js:3888:    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
src/well_harness/static/workbench.js:3947:    '.workbench-wow-run-button[data-wow-action="run"]',
src/well_harness/static/workbench.js:3960:// Reads /api/workbench/state-of-world and writes the four advisory
src/well_harness/static/workbench.js:3964:const WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";
tests/test_workbench_authority_banner.py:77:        "工程师只能提交 ticket / proposal",
src/well_harness/static/workbench_bundle.html:410:            <p id="workbench-result-mode" class="workbench-section-note">当前来源：等待 `POST /api/workbench/bundle`。</p>
tests/test_demo.py:1221:            connection.request("GET", "/api/workbench/bootstrap")
tests/test_demo.py:1316:                    connection.request("GET", "/api/workbench/recent-archives")
tests/test_demo.py:1370:                        "/api/workbench/bundle",
tests/test_demo.py:1468:                    "/api/workbench/archive-restore",
tests/test_demo.py:1504:                "/api/workbench/repair",
tests/test_demo.py:1711:            "dry-run / proposal, required_changes / risks",
tests/test_demo.py:1795:            "dry-run proposal, required_changes / risks",
tests/test_demo.py:1850:            "dry-run proposal",
src/well_harness/static/workbench.html:24:        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
src/well_harness/static/workbench.html:87:        id="workbench-wow-starters"
src/well_harness/static/workbench.html:88:        class="workbench-wow-starters"
src/well_harness/static/workbench.html:89:        aria-label="Canonical demo scenarios — one-click starter cards"
src/well_harness/static/workbench.html:91:        <header class="workbench-wow-starters-header">
src/well_harness/static/workbench.html:94:          <p class="workbench-wow-starters-sub">
src/well_harness/static/workbench.html:95:            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
src/well_harness/static/workbench.html:98:        <div class="workbench-wow-starters-grid">
src/well_harness/static/workbench.html:100:            class="workbench-wow-card"
src/well_harness/static/workbench.html:101:            data-wow-id="wow_a"
src/well_harness/static/workbench.html:102:            aria-labelledby="workbench-wow-a-title"
src/well_harness/static/workbench.html:105:              <span class="workbench-wow-tag">wow_a</span>
src/well_harness/static/workbench.html:106:              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
src/well_harness/static/workbench.html:108:            <p class="workbench-wow-card-desc">
src/well_harness/static/workbench.html:112:              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
src/well_harness/static/workbench.html:116:              class="workbench-wow-run-button"
src/well_harness/static/workbench.html:118:              data-wow-id="wow_a"
src/well_harness/static/workbench.html:120:              一键运行 wow_a
src/well_harness/static/workbench.html:123:              class="workbench-wow-result"
src/well_harness/static/workbench.html:124:              data-wow-result-for="wow_a"
src/well_harness/static/workbench.html:132:            class="workbench-wow-card"
src/well_harness/static/workbench.html:133:            data-wow-id="wow_b"
src/well_harness/static/workbench.html:134:            aria-labelledby="workbench-wow-b-title"
src/well_harness/static/workbench.html:137:              <span class="workbench-wow-tag">wow_b</span>
src/well_harness/static/workbench.html:138:              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
src/well_harness/static/workbench.html:140:            <p class="workbench-wow-card-desc">
src/well_harness/static/workbench.html:141:              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
src/well_harness/static/workbench.html:146:              class="workbench-wow-run-button"
src/well_harness/static/workbench.html:148:              data-wow-id="wow_b"
src/well_harness/static/workbench.html:150:              一键运行 wow_b
src/well_harness/static/workbench.html:153:              class="workbench-wow-result"
src/well_harness/static/workbench.html:154:              data-wow-result-for="wow_b"
src/well_harness/static/workbench.html:162:            class="workbench-wow-card"
src/well_harness/static/workbench.html:163:            data-wow-id="wow_c"
src/well_harness/static/workbench.html:164:            aria-labelledby="workbench-wow-c-title"
src/well_harness/static/workbench.html:167:              <span class="workbench-wow-tag">wow_c</span>
src/well_harness/static/workbench.html:168:              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
src/well_harness/static/workbench.html:170:            <p class="workbench-wow-card-desc">
src/well_harness/static/workbench.html:171:              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
src/well_harness/static/workbench.html:176:              class="workbench-wow-run-button"
src/well_harness/static/workbench.html:178:              data-wow-id="wow_c"
src/well_harness/static/workbench.html:180:              一键运行 wow_c
src/well_harness/static/workbench.html:183:              class="workbench-wow-result"
src/well_harness/static/workbench.html:184:              data-wow-result-for="wow_c"
src/well_harness/static/workbench.html:247:          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
src/well_harness/static/workbench.html:332:          <li>No proposals submitted yet.</li>
src/well_harness/static/workbench.html:362:            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
tests/e2e/test_wow_b_monte_carlo.py:3:Locks the observable contract of /api/monte-carlo/run against a live
tests/e2e/test_wow_b_monte_carlo.py:26:    return api_post(base_url, "/api/monte-carlo/run",
tests/e2e/test_wow_b_monte_carlo.py:31:def test_wow_b_monte_carlo_returns_contract_shape(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:40:def test_wow_b_10k_trials_under_5s(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:51:def test_wow_b_success_rate_in_unit_interval(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:63:def test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:77:def test_wow_b_is_deterministic_under_fixed_seed(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:86:def test_wow_b_n_trials_zero_is_clamped_to_min(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:97:def test_wow_b_n_trials_overflow_is_clamped_to_max(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:65:def test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:79:def test_wow_a_lever_snapshot_exposes_four_logic_gates(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:93:def test_wow_a_beat_early_activates_logic1_and_logic2_only(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:105:def test_wow_a_beat_deep_activates_logic2_and_logic3(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:136:def test_wow_a_beat_blocked_deactivates_entire_chain(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:148:def test_wow_a_truth_engine_is_deterministic(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:160:def test_wow_a_response_under_500ms_warm(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:171:def test_wow_a_lever_snapshot_evidence_field_present(demo_server, api_post):
src/well_harness/static/demo.js:108:    // E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
src/well_harness/static/demo.js:114:    // actor↔signed_by binding + ticket cross-binding; replay/nonce/freshness
src/well_harness/static/demo.js:127:      ticket_id:                "WB-DEMO",
src/well_harness/static/demo.js:131:        ticket_id: "WB-DEMO",
tests/e2e/fixtures/schema_snapshot.json:16:    "path": "/api/monte-carlo/run",
tests/e2e/fixtures/schema_snapshot.json:25:    "path": "/api/diagnosis/run",
tests/test_p19_api_endpoints.py:3:- POST /api/diagnosis/run
tests/test_p19_api_endpoints.py:4:- POST /api/monte-carlo/run
tests/test_p19_api_endpoints.py:92:# ─── POST /api/diagnosis/run ─────────────────────────────────────────────────
tests/test_p19_api_endpoints.py:100:            "POST", "/api/diagnosis/run", body={"outcome": "logic1_active"}
tests/test_p19_api_endpoints.py:112:            "/api/diagnosis/run",
tests/test_p19_api_endpoints.py:121:            "/api/diagnosis/run",
tests/test_p19_api_endpoints.py:130:            "POST", "/api/diagnosis/run", body={"outcome": "pls_unlocked"}
tests/test_p19_api_endpoints.py:138:            "POST", "/api/diagnosis/run", body={}
tests/test_p19_api_endpoints.py:144:# ─── POST /api/monte-carlo/run ───────────────────────────────────────────────
tests/test_p19_api_endpoints.py:153:            "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:165:            "POST", "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:169:            "POST", "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:177:            "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:186:            "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:195:            "/api/monte-carlo/run",
tests/test_p19_api_endpoints.py:236:# ─── POST /api/sensitivity-sweep ─────────────────────────────────────────────
tests/test_p19_api_endpoints.py:243:        status, data = server.request("POST", "/api/sensitivity-sweep", body={})
tests/test_p19_api_endpoints.py:256:            "/api/sensitivity-sweep",
tests/test_c919_etras_workstation.py:105:        self.assertNotIn('"/api/monte-carlo/run"', js)
tests/test_pr_close_loop.py:4:from well_harness.collab.merge_close import build_merge_close_plan, close_ticket_with_verdict
tests/test_pr_close_loop.py:8:def _ticket() -> dict:
tests/test_pr_close_loop.py:15:        "Generated Prompt": "## anchor\nproposal\n\n## scope\nsrc/well_harness/workbench/**",
tests/test_pr_close_loop.py:43:    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/workbench/pr_review.py"))
tests/test_pr_close_loop.py:51:    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/controller.py"))
tests/test_pr_close_loop.py:57:def test_merge_close_stub_appends_pr_and_ticket_events(tmp_path):
tests/test_pr_close_loop.py:58:    ticket = _ticket()
tests/test_pr_close_loop.py:59:    report = review_pr_diff(ticket, _diff_for("src/well_harness/workbench/pr_review.py"))
tests/test_pr_close_loop.py:60:    plan = build_merge_close_plan(ticket, report, actor="Kogami")
tests/test_pr_close_loop.py:61:    close_result = close_ticket_with_verdict(ticket, report, audit_path=tmp_path / "audit/events.jsonl", actor="Kogami")
tests/test_pr_close_loop.py:65:    assert plan["actions"] == ["record_pr_acceptance", "record_ticket_close"]
tests/test_pr_close_loop.py:67:    assert [event["type"] for event in events] == ["pr.accepted", "ticket.closed"]
tests/e2e/test_wow_c_reverse_diagnose.py:3:Locks /api/diagnosis/run contract: valid outcome returns a list of parameter
tests/e2e/test_wow_c_reverse_diagnose.py:27:def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:28:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:42:def test_wow_c_each_result_carries_required_parameter_keys(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:43:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:56:def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:58:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:71:def test_wow_c_all_valid_outcomes_return_200(demo_server, api_post, outcome):
tests/e2e/test_wow_c_reverse_diagnose.py:73:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:83:def test_wow_c_invalid_outcome_returns_structured_400(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:84:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:97:def test_wow_c_missing_outcome_returns_400(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:98:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:106:def test_wow_c_max_results_bound_is_respected(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:107:    status, body = api_post(demo_server, "/api/diagnosis/run", {
src/well_harness/static/c919_etras_panel/index.html:849:  document.getElementById('dv_trwowAcc').textContent='▲'+(d.tr_wow_acc_s||0).toFixed(2)+'s';
src/well_harness/static/annotation_overlay.js:24:    const ticket = document.getElementById("workbench-ticket");
src/well_harness/static/annotation_overlay.js:25:    return ticket ? ticket.dataset.ticket || "WB-LOCAL" : "WB-LOCAL";
src/well_harness/static/annotation_overlay.js:77:      ticket_id: input.ticket_id || currentTicketId(),
src/well_harness/static/annotation_overlay.js:122:    if (list.children.length === 1 && list.children[0].textContent === "No proposals submitted yet.") {
tests/conftest.py:16:# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
tests/conftest.py:23:# ⚠ CANNED TEST FIXTURE — NOT REAL AUTHENTICATION. signed_by/ticket_id are
tests/conftest.py:28:    "ticket_id": "WB-TEST",
tests/conftest.py:32:        "ticket_id": "WB-TEST",
tests/test_lever_snapshot_manual_override_guard.py:3:Locks the contract: /api/lever-snapshot requires actor + ticket_id +
tests/test_lever_snapshot_manual_override_guard.py:38:    "ticket_id": "WB-TEST-1",
tests/test_lever_snapshot_manual_override_guard.py:42:        "ticket_id": "WB-TEST-1",
tests/test_lever_snapshot_manual_override_guard.py:79:    """auto_scrubber path: no actor/ticket required, returns 200."""
tests/test_lever_snapshot_manual_override_guard.py:103:def test_manual_override_missing_ticket_id_returns_409(server) -> None:
tests/test_lever_snapshot_manual_override_guard.py:106:    payload["ticket_id"] = ""
tests/test_lever_snapshot_manual_override_guard.py:110:    assert body.get("field") == "ticket_id"
tests/test_lever_snapshot_manual_override_guard.py:116:    payload["ticket_id"] = "WB-TEST-1"
tests/test_lever_snapshot_manual_override_guard.py:133:def test_manual_override_signoff_ticket_mismatch_returns_409(server) -> None:
tests/test_lever_snapshot_manual_override_guard.py:134:    """signoff.ticket_id MUST equal request ticket_id; mismatch is rejected."""
tests/test_lever_snapshot_manual_override_guard.py:139:        "ticket_id": "WB-DIFFERENT",
tests/test_lever_snapshot_manual_override_guard.py:143:    assert body.get("field") == "manual_override_signoff.ticket_id"
tests/test_lever_snapshot_manual_override_guard.py:162:    (matching ticket_id) and impersonates Kogami. Live-verified by P2 in R1.
tests/test_lever_snapshot_manual_override_guard.py:210:    payload["ticket_id"] = "WB-TEST-1"
tests/test_p19_api_multisystem.py:3:- POST /api/diagnosis/run with system_id parameter
tests/test_p19_api_multisystem.py:4:- POST /api/monte-carlo/run with system_id parameter
tests/test_p19_api_multisystem.py:92:    """system_id parameter for POST /api/diagnosis/run.
tests/test_p19_api_multisystem.py:100:            "POST", "/api/diagnosis/run",
tests/test_p19_api_multisystem.py:108:            "POST", "/api/diagnosis/run",

codex
I’ve confirmed the new route is wired where expected. Next I’m checking the surrounding `/workbench` behaviors: the starter-card POSTs, feedback-mode signals, and any proposal flow that might make the “Read Only” claim misleading to a first-time engineer.
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '596,646p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   621	                section = full_text[anchor:end] if end != -1 else full_text[anchor:]
   622	                excerpt_lines.append(section.rstrip())
   623	            else:
   624	                excerpt_lines.append(
   625	                    "Truth-engine 红线: controller / runner / models / "
   626	                    "adapters/ are read-only by design. Workbench surfaces "
   627	                    "may propose changes via ticket / proposal — they may "
   628	                    "never mutate truth-engine values directly. See "
   629	                    ".planning/constitution.md §v6.1 Solo Autonomy Delegation."
   630	                )
   631	        else:
   632	            excerpt_lines.append(
   633	                "Truth-engine 红线 source file (.planning/constitution.md) "
   634	                "is not available in this checkout. The contract remains: "
   635	                "controller / runner / models / adapters/ are read-only."
   636	            )
   637	        body = "\n".join(excerpt_lines).encode("utf-8")
   638	        self._send_bytes(200, body, "text/plain; charset=utf-8")
   639	
   640	    def _send_json(self, status_code: int, payload: dict):
   641	        # Compact JSON: no indentation (machine-to-machine API, not human-readable)
   642	        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
   643	        self._send_bytes(status_code, response, "application/json; charset=utf-8")
   644	
   645	    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
   646	        self.send_response(status_code)

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3760,3955p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,210p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/annotation_overlay.js | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

 succeeded in 0ms:
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
  3788	      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
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
  3846	    // logic4} with logic1 dropping out (reverser_not_deployed_eec flips
  3847	    // false mid-deploy). Print the live active set verbatim so the card
  3848	    // never overstates the truth.
  3849	    summarize: (body) => {
  3850	      const logic = body && typeof body.logic === "object" ? body.logic : {};
  3851	      const order = ["logic1", "logic2", "logic3", "logic4"];
  3852	      const active = order.filter((k) => logic[k] && logic[k].active === true);
  3853	      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
  3854	      const activeStr = active.length === 0 ? "none" : active.join("+");
  3855	      return `nodes=${nodes.length} · active=[${activeStr}] · mode=auto_scrubber`;
  3856	    },
  3857	  },
  3858	  wow_b: {
  3859	    endpoint: "/api/monte-carlo/run",
  3860	    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
  3861	    summarize: (body) => {
  3862	      if (!body) return "(empty body)";
  3863	      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
  3864	      const failures = body.n_failures;
  3865	      const trials = body.n_trials;
  3866	      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
  3867	    },
  3868	  },
  3869	  wow_c: {
  3870	    endpoint: "/api/diagnosis/run",
  3871	    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
  3872	    summarize: (body) => {
  3873	      if (!body) return "(empty body)";
  3874	      const total = body.total_combos_found;
  3875	      const returned = Array.isArray(body.results) ? body.results.length : 0;
  3876	      const grid = body.grid_resolution;
  3877	      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
  3878	    },
  3879	  },
  3880	};
  3881	
  3882	async function runWowScenario(wowId) {
  3883	  const scenario = WOW_SCENARIOS[wowId];
  3884	  const button = document.querySelector(
  3885	    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  3886	  );
  3887	  const result = document.querySelector(
  3888	    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  3889	  );
  3890	  if (!scenario || !result) {
  3891	    return;
  3892	  }
  3893	  if (button) {
  3894	    button.disabled = true;
  3895	  }
  3896	  result.removeAttribute("data-wow-state");
  3897	  result.textContent = `POST ${scenario.endpoint} ...`;
  3898	  // P1 R2 BLOCKER fix: bounded timeout via AbortController so a stalled
  3899	  // endpoint cannot freeze the card mid-demo.
  3900	  const controller =
  3901	    typeof AbortController !== "undefined" ? new AbortController() : null;
  3902	  const timeoutHandle = controller
  3903	    ? setTimeout(() => controller.abort(), WOW_REQUEST_TIMEOUT_MS)
  3904	    : null;
  3905	  try {
  3906	    const t0 = performance.now();
  3907	    const response = await fetch(scenario.endpoint, {
  3908	      method: "POST",
  3909	      headers: { "Content-Type": "application/json" },
  3910	      body: JSON.stringify(scenario.payload),
  3911	      signal: controller ? controller.signal : undefined,
  3912	    });
  3913	    const ms = Math.round(performance.now() - t0);
  3914	    let body = null;
  3915	    try {
  3916	      body = await response.json();
  3917	    } catch (_err) {
  3918	      body = null;
  3919	    }
  3920	    if (!response.ok) {
  3921	      result.setAttribute("data-wow-state", "error");
  3922	      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
  3923	      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
  3924	      return;
  3925	    }
  3926	    result.setAttribute("data-wow-state", "ok");
  3927	    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  3928	  } catch (err) {
  3929	    result.setAttribute("data-wow-state", "error");
  3930	    if (err && err.name === "AbortError") {
  3931	      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
  3932	    } else {
  3933	      result.textContent = `network error: ${err && err.message ? err.message : err}`;
  3934	    }
  3935	  } finally {
  3936	    if (timeoutHandle !== null) {
  3937	      clearTimeout(timeoutHandle);
  3938	    }
  3939	    if (button) {
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

exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n \"Forbidden（红线维持|v6\\.1|Solo Autonomy Delegation|controller|runner|models|adapters\" .planning/constitution.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
5:> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
7:> **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
9:> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
62:- `src/well_harness/controller.py` is the confirmed control truth.
63:- `src/well_harness/runner.py` is the simulation coordination layer.
66:- Bypassing adapters with new hardcoded truth paths is forbidden.
151:- **v6.1 Solo Autonomy Delegation (2026-04-25, active):** Kogami 在 PR #5 Gate 后口头授权 Claude Code 全权（Notion + PR merge + Codex 自决 + 新 phase 启停），仅 truth-engine 红线维持。详见 v6.1 Solo Autonomy 节、DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT、Notion Page 11 §v6.1。
152:- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
154:- **v2.4 Recursive Coherence Drift Mitigation (2026-04-25, active, ratified by Opus 4.7):** doc-only rule-bundle PR R3 Opus consultation trigger + R5 drift-acceptance declaration + R6 hard cap + forbidden-superlative list + standard substitute template. Source: RETRO-V61-055 §3 + Opus 4.7 strategic review same day. Confirmed instances: PR #11 (5R), PR #14 (6R, merged with drift acceptance). v6.1 Hard Stop ≥4 仍适用于 source-code 与非 rule-bundle PR。详见 v2.3 §Recursive Coherence Drift Mitigation、RETRO-V61-055。
160:1. **No controller.py / 19-node / R1–R5 / irreversible main-HEAD mutation without Kogami Gate sign.** FF merges, branch deletes, force-pushes, and any action that rewrites main's history must wait for an explicit `<PHASE>-GATE: Approved` comment from Kogami.
197:## v6.1 Claude Code Solo Autonomy Delegation (2026-04-25, active)
205:Recorded as `DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT` (Notion 04 决策日志 DB) and reflected in Notion Page 11 §v6.1 Solo Autonomy Delegation. v5.2 五红线和 v6.0 联合开发 Codex 触发清单作为基线继承；v6.1 仅在其上叠加授权层。
210:- `gh pr merge`：合并任何 OPEN PR 到 main，前提 (1) 未触红线 (2) 三轨证据齐全 (3) Codex 已审查（如触发 v6.0 / v6.1 trigger 清单）
216:### Forbidden（红线维持，触碰即停车）
218:- `src/well_harness/controller.py` 任何编辑（pure truth engine）
219:- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义
220:- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）
224:- 自创规则版本号（v6.1 之后下次叠加层应是 v6.2，不得跳号）
226:### Codex 触发清单（继承 v6.0 + V61-001 新增 + v6.1 EMPIRICAL-CLAIM-PROBE）
232:**v6.1 新增 EMPIRICAL-CLAIM-PROBE 规则（2026-04-25）：** PR prose（test docstring / 文件级 comment / demo doc / PR description）写下任何关于服务端 runtime 行为的具体数字（plant deploy %、sim time、tick count、logic-X activation timing 等）之前，Claude Code 必须 boot 相关代码路径在本地实测一次，或显式标 `TODO(probe-before-merge)`，或引用数字定义所在的 commit:line。仅基于 mental-model 算术得出的数字禁止落地到 regression-locked 测试或客户向 demo doc。来源：PR #5 round 1 Codex 命中 BEAT_EARLY ~6% deploy 实际 0% （详 `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`）。
368:- v6.1 Codex 触发清单（多文件 UI / API 契约 / OpenFOAM solver / CFD 几何 / Phase E2E 失败 / Docker+OpenFOAM / GSD 产出物等）
385:**Scope:** doc-only rule-bundle PRs only. Source-code rule-bundle PRs follow standard R4 Opus trigger and v6.1 Hard Stop ≥4. (Source code has pytest/executability auto-grounding spec drift; coherence drift is a doc-only phenomenon.)
401:**R-budget two-tier cap (replaces v6.1 Hard Stop ≥4 for doc-only rule-bundle PRs):**
426:- 意外触红线（grep 命中 `controller.py` 在 `git diff` 中）→ `git checkout` 撤销 + 立即停车汇报
428:### Commit Trailer (v6.1)
431:Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
436:- Kogami chat 中显式 "撤销 v6.1 / 收回授权 / 暂停自驱"

 succeeded in 0ms:
     1	# AI FANTUI LogicMVP Constitution
     2	
     3	> **Constitution version:** v2.4 (2026-04-25, +Recursive Coherence Drift Mitigation for doc-only rule-bundle PRs, ratified by Opus 4.7 strategic review)
     4	>
     5	> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
     6	>
     7	> **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
     8	>
     9	> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
    10	>
    11	> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
    12	>
    13	> **v2.4 增量 (2026-04-25, ratified by Opus 4.7):** 追加 §Recursive Coherence Drift Mitigation — applies only to doc-only rule-bundle PRs (objective trigger: modifies ≥1 constitution rule body AND adds/rewrites ≥2 cross-doc pointers, OR labeled `governance-bundle`). Triggers Opus consultation at R3 (普通 PR 仍 R4); R5 mandatory drift-acceptance declaration; R6 hard cap (binary: rollback or merge-with-explicit-drift). Forbidden superlatives in commit/PR bodies. 1 canonical source at `<path>`; downstream references may drift in wording but must not contradict canonical. Source: RETRO-V61-055 §3 (PR #15) + Opus 4.7 strategic review same day. v2.2 / v2.3 / governance bundle #2 / Verbatim Exception / RETRO 序号 / Self-Pass-Rate 全部不动。
    14	
    15	## Milestone Hold (historical, 2026-04-13)
    16	
    17	**Declared:** 2026-04-13
    18	**Scope:** Milestone 4 (Phases P4–P11)
    19	**Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**
    20	
    21	All P0 through P11 phases are complete. The project is at a natural pause point.
    22	
    23	### What This Hold Means
    24	
    25	- No active development phases.
    26	- Base code frozen; only regression fixes and documentation corrections permitted.
    27	- Notion control tower and GitHub repo remain accessible as read-only reference.
    28	- Opus 4.6 review gate is not active.
    29	
    30	### Reason
    31	
    32	All P0→P11 capabilities have been delivered:
    33	- Deterministic control-logic analysis workbench (thrust-reverser reference system)
    34	- Runtime generalization proof via adapter layer (landing-gear second system)
    35	- Fully automated GSD loop with Notion writeback and GitHub Actions CI
    36	- Third-party onboarding guide and template scaffolding
    37	- 23-command regression suite, 0 open gaps
    38	
    39	The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.
    40	
    41	### Resume Criteria
    42	
    43	Milestone Hold lifts when one or more of the following conditions are met:
    44	
    45	1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
    46	2. External user feedback identifies a confirmed gap that cannot be resolved within the existing frozen baseline.
    47	3. A project sponsor or lead author formally requests a new development phase via Notion control tower or GitHub.
    48	
    49	No development activity resumes without a documented decision in the Notion control plane.
    50	
    51	---
    52	
    53	## Project Identity
    54	
    55	**Name:** AI FANTUI LogicMVP
    56	**Type:** Deterministic control-logic analysis workbench
    57	**First Reference System:** Thrust reverser deploy cockpit
    58	**Generalization Proof:** Landing-gear adapter runtime (second system)
    59	
    60	## Core Truths
    61	
    62	- `src/well_harness/controller.py` is the confirmed control truth.
    63	- `src/well_harness/runner.py` is the simulation coordination layer.
    64	- The simplified plant is a first-cut feedback model, not a complete physical model.
    65	- New system truth is allowed only through explicit adapter interfaces.
    66	- Bypassing adapters with new hardcoded truth paths is forbidden.
    67	
    68	## Control Plane
    69	
    70	- GitHub / repo is the code truth plane.
    71	- Notion is the control plane and audit cockpit.
    72	- GSD owns plan → execute → verify routing.
    73	- Opus 4.6 is the only intended manual review gate for subjective judgment.
    74	
    75	## Phase Registry
    76	
    77	| Phase | Title | Status |
    78	|-------|-------|--------|
    79	| P0 | Control Tower And GSD Control Plane | Done |
    80	| P1 | Automate Execution And Evidence Writeback | Done |
    81	| P2 | Harden Opus 4.6 Review Packets | Done |
    82	| P3 | Reduce Control-Plane Drift | Done |
    83	| P4 | Elevate Cockpit Demo To Presenter-Ready | Done |
    84	| P5 | Demo Polish And Edge-Case Hardening | Done |
    85	| P6 | Reconcile Control Tower And Freeze Demo Packet | Done |
    86	| P7 | Build A Spec-Driven Control Analysis Workbench | Done |
    87	| P8 | Runtime Generalization Proof | Done |
    88	| P9 | Automation Hardening & Evidence Pipeline Maturity | Done |
    89	| P10 | Second-System Runtime Pipeline End-to-End | Done |
    90	| P11 | Product Readiness & Third-Party Onboarding Guide | Done |
    91	| P12 | Third-System Onboarding Validation | Done |
    92	| P13 | Route B — Browser Workbench Multi-System Integration | Done |
    93	| P14 | AI Document Analyzer | Done (2026-04-13) |
    94	| P15 | Pipeline Integration — P14 output → P7/P8 intake | Done (2026-04-14) |
    95	| P16 | AI Canvas Sync（Opus 4.6 架构裁决） | Done (2026-04-15) |
    96	| P17 | Fault Injection — Interactive Fault Mode | Done (2026-04-15, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
    97	| P18 | Demo Cleanup & Archive Integrity | Done (2026-04-16, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
    98	| P19 | Hardware Partial Unfreeze — Monte Carlo + Reverse Diagnosis + Pitch Deck | Done (2026-04-17, self-signed v4.0; provenance re-signed 2026-04-20 P32; supersedes `docs/unfreeze/P17-application-draft.md`) |
    99	| P20 | Wow E2E Coverage + Demo Resilience + Dress Rehearsal | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
   100	| P21 | Local Model PoC — 国产模型本地降级 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   101	| P22 | Demo Rehearsal 物料冻结 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   102	| P23 | Co-development Kit — 立项通过后首批对接物料 | Done (2026-04-18, GATE-P23-CLOSURE Approved; 对外路线图编号 H2-23 ~ H2-27) |
   103	| P24 | 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals | Done (2026-04-18, GATE-P24-CLOSURE Approved) |
   104	| P25 | 立项汇报段落级时序彩排 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   105	| P26 | 立项物料引用有效性自动验证 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   106	| P27 | Backend Switch Drill — pkill+spawn+wait_ready | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   107	| P28 | FAQ Evidence Cross-Check | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   108	| P29 | Pre-Pitch Readiness Scorecard | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   109	| P30 | Scorecard 语义与 findings §5.1 决策对齐 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
   110	| P31 | Explain-runtime visibility + prewarm guardrails (orphan-triage re-land) | Done (2026-04-20, v5.2 solo-signed; awaiting `P31-GATE: Approved` for FF merge to main) |
   111	| P32 | Provenance Backfill — v4.0 追认 + Milestone 9 Lifted + constitution v2.1 | In progress (2026-04-20, v5.2 solo-signed; `GATE-P32-PLAN: Approved` 2026-04-20, awaiting `GATE-P32-CLOSURE: Approved`) |
   112	
   113	---
   114	
   115	## Milestone 9 — Project Freeze → Lifted
   116	
   117	**Declared:** 2026-04-15 by Opus 4.6 Final Adjudication
   118	**Lifted:** 2026-04-20 (retroactive provenance追认 under v5.2 Claude App Solo Mode, P32 W3)
   119	**Scope:** Post-P16 freeze line covering all P17–P30 activity
   120	
   121	### What Milestone 9 Meant
   122	
   123	Opus 4.6 declared Project Freeze after P16 AI Canvas Sync (2026-04-15) with the assessment "项目已达到可泛化动力控制电路系统工作台 MVP 达标线". Freeze conditions required that continued development await one of three Resume Criteria: 外部用户反馈 / 产品方向决策 / 赞助方请求. `docs/freeze/FREEZE-RULING-2026-04-15.md` is the primary rulemaking document; `MILESTONE4/5/6-HOLD.md` are the earlier freeze-family records.
   124	
   125	### Why It Was Lifted (retroactively 追认)
   126	
   127	Between 2026-04-15 and 2026-04-18, under the v4.0 Extended Autonomy Mode then-in-force, **14 Phases (P17 → P30) landed above the freeze line**, each individually self-signed by the Executor (Codex / MiniMax-2.7 / Claude Code Opus 4.7) and accepted by Kogami through point-Gate decisions (`GATE-P23-CLOSURE: Approved`, `GATE-P24-CLOSURE: Approved`, etc.). These Gate approvals collectively satisfied Resume Criterion #1 「产品方向决策」 — Kogami's on-the-record directives to continue with 立项 demo hardening, co-development kit, then pitch script rehearsal constitute the required 产品方向 evidence.
   128	
   129	**However**, the 14-Phase window **never carried an explicit Milestone 9 Lifted statement in this constitution**. That gap is what P32 W3 closes: not by retroactively re-consenting to work that already happened, but by正式 acknowledging that the freeze line was in fact crossed and the Resume Criterion path was met.
   130	
   131	### Signatures
   132	
   133	- **Kogami (Project Sponsor):** implicit Lifted consent via the 14 per-Phase Gate approvals (2026-04-15 → 2026-04-18); **explicit 追认 via `GATE-P32-PLAN: Approved` (2026-04-20)**
   134	- **Claude App Opus 4.7 (Solo Executor, v5.2):** solo-signed 2026-04-20 via `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`
   135	
   136	### What This Does NOT Mean
   137	
   138	- Milestone 9 Lifted does **not** authorize new能力 Phases prospectively. Any new Phase (P33+) must still go through its own PLAN / CLOSURE Gate sequence under v5.2 Solo Mode.
   139	- It does **not** imply `docs/freeze/FREEZE-RULING-2026-04-15.md` is void. That ruling stands as the 2026-04-15 factual assessment; Lifted simply记录 that the Resume Criteria were thereafter met.
   140	- It does **not** alter any P17–P30 Phase content, tests, or code. P32 is证迹 (provenance) only.
   141	
   142	---
   143	
   144	## Governance Mode Timeline
   145	
   146	- **v3.0 双 Opus (2026-04-xx → 2026-04-17):** Claude Code Opus 4.7 as Executor; Notion AI Opus 4.7 as independent Gate reviewer. Retired when v4.0 Extended Autonomy allowed Executor self-signing.
   147	- **v4.0 Extended Autonomy (2026-04-17 → 2026-04-19):** Executor allowed to self-sign Gate within a ≥3-Phase深度验收 window when Kogami 显式 renewed the mandate. Used for P17 → P30 close-out.
   148	- **v5.1 Pair Mode (2026-04-19 → 2026-04-20):** Short-lived dual-Executor pair (Claude App + Codex). Abandoned after orphan commit `4474505` (Codex, unsigned) triggered the P31 orphan-triage response.
   149	- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
   150	- **v6.0 Multi-Agent × Codex Joint Dev (2026-04-22 → 2026-04-25):** Claude Code 主执行 + Codex 强制盲点审查回到清单（多文件前端 / API 契约变更 / e2e 期望变更 / UI 变更 / 用户 UX 批评后首次实现 / OpenFOAM 误差等触发硬性调用）。Verbatim exception 5 条件允许跳过 round-2。详见 Notion Page 11 v6.0 节。
   151	- **v6.1 Solo Autonomy Delegation (2026-04-25, active):** Kogami 在 PR #5 Gate 后口头授权 Claude Code 全权（Notion + PR merge + Codex 自决 + 新 phase 启停），仅 truth-engine 红线维持。详见 v6.1 Solo Autonomy 节、DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT、Notion Page 11 §v6.1。
   152	- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
   153	- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
   154	- **v2.4 Recursive Coherence Drift Mitigation (2026-04-25, active, ratified by Opus 4.7):** doc-only rule-bundle PR R3 Opus consultation trigger + R5 drift-acceptance declaration + R6 hard cap + forbidden-superlative list + standard substitute template. Source: RETRO-V61-055 §3 + Opus 4.7 strategic review same day. Confirmed instances: PR #11 (5R), PR #14 (6R, merged with drift acceptance). v6.1 Hard Stop ≥4 仍适用于 source-code 与非 rule-bundle PR。详见 v2.3 §Recursive Coherence Drift Mitigation、RETRO-V61-055。
   155	
   156	## v5.2 Claude App Solo Mode (active)
   157	
   158	### Red Lines (five absolutes)
   159	
   160	1. **No controller.py / 19-node / R1–R5 / irreversible main-HEAD mutation without Kogami Gate sign.** FF merges, branch deletes, force-pushes, and any action that rewrites main's history must wait for an explicit `<PHASE>-GATE: Approved` comment from Kogami.
   161	2. **No self-signed Gate.** Executor drafts `PLAN.md` and `CLOSURE.md` but never signs `GATE-<PHASE>-PLAN: Approved` or `GATE-<PHASE>-CLOSURE: Approved`. Those two signatures are Kogami-only.
   162	3. **Tier 1 adversarial self-review is mandatory on every PLAN.** Plans must contain a Counterargument section with ≥3 reasoned self-objections and explicit rebuttals before request-for-Gate.
   163	4. **Executor does not self-select next Phase direction.** When a Phase closes, Executor awaits Kogami's next directive. If Executor has a recommendation, it must be offered as an `AskUserQuestion` with ≥2 options, not acted on unilaterally.
   164	5. **证迹 (provenance) precedes 能力 (capability).** New capability work is gated on no outstanding provenance debt. If gap analysis identifies provenance debt, that debt is closed in a dedicated证迹 Phase before any能力 Phase starts (this is precisely what P32 enforces for the v4.0 window).
   165	
   166	### DECISION Format
   167	
   168	Every Phase closure writes a DECISION section to the Notion control tower (`33cc68942bed8136b5c9f9ba5b4b44ec`) with heading:
   169	
   170	```markdown
   171	## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)
   172	```
   173	
   174	Body covers: direction source · scope · Kogami Gate references · Exit artefact links · Red-line compliance checklist.
   175	
   176	### Commit Trailer
   177	
   178	Every commit by Claude App Opus 4.7 under v5.2 must include the trailer:
   179	
   180	```
   181	Execution-by: opus47-claudeapp-solo · v5.2
   182	```
   183	
   184	Reviewer sign line (in Notion / closure docs / audit records):
   185	
   186	```
   187	Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD
   188	```
   189	
   190	### Sandbox Discipline
   191	
   192	- Workspace mount `.git/*.lock` residues are known blockers. v5.2 convention: scratch clone at `/sessions/<id>/p31-work/repo` + git bundle transfer when locks persist. Bundles live under `.planning/audit/bundles/` with adjacent README import instructions.
   193	- Workspace mount file edits only permitted on paths that do NOT coincide with files changed by a pending bundle, to avoid FF merge conflicts.
   194	
   195	---
   196	
   197	## v6.1 Claude Code Solo Autonomy Delegation (2026-04-25, active)
   198	
   199	### Origin
   200	
   201	Kogami 2026-04-25 verbatim grant, after PR #5 GATE-WOW-A-NARRATION-FIX: Approved:
   202	
   203	> 全权授权你进行开发，根据你的建议继续执行，只有truth-engine不许动，其他权限都交给你，你可以按照分工，调用codex配合你。记得在Notion页面里更新我这次的授权，以及Claude code的权限说明
   204	
   205	Recorded as `DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT` (Notion 04 决策日志 DB) and reflected in Notion Page 11 §v6.1 Solo Autonomy Delegation. v5.2 五红线和 v6.0 联合开发 Codex 触发清单作为基线继承；v6.1 仅在其上叠加授权层。
   206	
   207	### Allowed (without per-step Kogami sign-off)
   208	
   209	- Git: push / rebase / force-push 仅在 Claude 自己创建的 dev 分支；main 与 reviewer 已 ack 的 PR head 仍走 PR 流程
   210	- `gh pr merge`：合并任何 OPEN PR 到 main，前提 (1) 未触红线 (2) 三轨证据齐全 (3) Codex 已审查（如触发 v6.0 / v6.1 trigger 清单）
   211	- Notion 写入：04 决策日志、03 会话记录、Page 11 模型分工、Roadmap、其他子页
   212	- Codex 调用自决：`/codex-gpt54` 何时调由 Claude 判断；硬触发清单与 v6.0 一致
   213	- 自启 Phase：写 PLAN.md / 执行 / 写 CLOSURE.md / 自签 GATE-Pxx-CLOSURE: Approved；Tier 1 adversarial self-review (≥3 反对意见 + rebuttal) 仍硬性必跑
   214	- 测试 / 调试 / `demo_server` 启停 / git bisect
   215	
   216	### Forbidden（红线维持，触碰即停车）
   217	
   218	- `src/well_harness/controller.py` 任何编辑（pure truth engine）
   219	- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义
   220	- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）

exec
/bin/zsh -lc "python - <<'PY'
from http.server import ThreadingHTTPServer
from threading import Thread
from http.client import HTTPConnection
from well_harness.demo_server import DemoRequestHandler
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
conn = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
for path in ('/v6.1-redline','/workbench'):
    conn.request('GET', path)
    resp = conn.getresponse()
    body = resp.read().decode('utf-8', errors='replace')
    print('PATH', path)
    print('STATUS', resp.status)
    print('CONTENT_TYPE', resp.getheader('Content-Type'))
    print('BODY_SNIP', body[:400].replace('\\n','\\\\n'))
conn.close()
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_authority_banner.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 2251ms:
............                                                             [100%]
12 passed in 2.07s

codex
The targeted banner tests are essentially green; I’m polling for completion and rerunning the live probe with `python3` because this checkout doesn’t have `python` on PATH.
exec
/bin/zsh -lc "python3 - <<'PY'
from http.server import ThreadingHTTPServer
from threading import Thread
from http.client import HTTPConnection
from well_harness.demo_server import DemoRequestHandler
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
for path in ('/v6.1-redline','/workbench'):
    conn = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('GET', path)
    resp = conn.getresponse()
    body = resp.read().decode('utf-8', errors='replace')
    print('PATH', path)
    print('STATUS', resp.status)
    print('CONTENT_TYPE', resp.getheader('Content-Type'))
    print('BODY_SNIP', body[:400].replace('\\n','\\\\n'))
    conn.close()
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 622ms:
PATH /v6.1-redline
STATUS 404
CONTENT_TYPE application/json; charset=utf-8
BODY_SNIP {"error": "not_found"}
PATH /workbench
STATUS 200
CONTENT_TYPE text/html; charset=utf-8
BODY_SNIP <!doctype html>\n<html lang="zh-CN">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>协作工作台 · FANTUI LogicMVP</title>\n  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n  <link rel="stylesheet" href="/unified-nav.css">\n  <link rel="stylesheet" href="/workbench_shell.css">\n</head>\n<body class="unified-nav-enabled" data-nav-curr

codex
The first manual probe exposed an environment trap, not a product failure: plain `python3` imported a different `well_harness` than this checkout, so `/v6.1-redline` 404’d against the wrong code. I’m re-probing with the repo-local `src` on `PYTHONPATH` so the route check actually targets commit `c7131e9`.
exec
/bin/zsh -lc 'rg -n "pythonpath|src-layout|well_harness" pyproject.toml setup.cfg setup.py pytest.ini tox.ini .' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: setup.cfg: No such file or directory (os error 2)
rg: setup.py: No such file or directory (os error 2)
rg: pytest.ini: No such file or directory (os error 2)
rg: tox.ini: No such file or directory (os error 2)
pyproject.toml:38:# - src: well_harness package imports
pyproject.toml:40:pythonpath = ["src", "."]
./src/well_harness/knowledge_capture.py:7:from well_harness.controller_adapter import GenericControllerTruthAdapter
./src/well_harness/knowledge_capture.py:8:from well_harness.document_intake import ControlSystemIntakePacket
./src/well_harness/knowledge_capture.py:9:from well_harness.fault_diagnosis import (
./src/well_harness/second_system_smoke.py:7:from well_harness.adapters import LANDING_GEAR_CONTROLLER_METADATA, build_landing_gear_controller_adapter
./src/well_harness/second_system_smoke.py:8:from well_harness.controller_adapter import GenericControllerTruthAdapter
./src/well_harness/second_system_smoke.py:9:from well_harness.document_intake import load_intake_packet
./src/well_harness/second_system_smoke.py:10:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_truth_adapter
./src/well_harness/second_system_smoke.py:11:from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter
./src/well_harness/second_system_smoke.py:12:from well_harness.scenario_playback import ScenarioPlaybackReport, build_playback_report_from_truth_adapter
./src/well_harness/second_system_smoke.py:13:from well_harness.system_spec import AcceptanceScenarioSpec, ComponentSpec, workbench_spec_from_dict
./src/well_harness/second_system_smoke.py:14:from well_harness.workbench_bundle import build_workbench_bundle
./src/well_harness/__main__.py:1:from well_harness.cli import main
./src/well_harness/two_system_runtime_comparison.py:6:from well_harness.adapters import build_landing_gear_controller_adapter
./src/well_harness/two_system_runtime_comparison.py:7:from well_harness.controller_adapter import GenericControllerTruthAdapter, build_reference_controller_adapter
./src/well_harness/two_system_runtime_comparison.py:8:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_truth_adapter
./src/well_harness/two_system_runtime_comparison.py:9:from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter
./src/well_harness/two_system_runtime_comparison.py:10:from well_harness.scenario_playback import build_playback_report_from_truth_adapter
./src/well_harness/two_system_runtime_comparison.py:11:from well_harness.system_spec import workbench_spec_from_dict
./src/well_harness/demo.py:7:from well_harness.controller_adapter import build_reference_controller_adapter
./src/well_harness/demo.py:8:from well_harness.models import FieldChange, HarnessConfig, LogicTransitionDiagnosis, SimulationResult
./src/well_harness/demo.py:9:from well_harness.runner import SimulationRunner
./src/well_harness/demo.py:10:from well_harness.scenarios import nominal_deploy_scenario
./src/well_harness/system_spec.py:6:from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
./src/well_harness/system_spec.py:7:from well_harness.models import HarnessConfig
./src/well_harness/demo_server.py:18:from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
./src/well_harness/demo_server.py:19:from well_harness.controller_adapter import build_reference_controller_adapter
./src/well_harness/demo_server.py:20:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./src/well_harness/demo_server.py:21:from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
./src/well_harness/demo_server.py:22:from well_harness.adapters.efds_adapter import build_efds_controller_adapter
./src/well_harness/demo_server.py:23:from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
./src/well_harness/demo_server.py:24:from well_harness.document_intake import (
./src/well_harness/demo_server.py:32:from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
./src/well_harness/demo_server.py:33:from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
./src/well_harness/demo_server.py:34:from well_harness.plant import PlantState, SimplifiedDeployPlant
./src/well_harness/demo_server.py:35:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./src/well_harness/demo_server.py:36:from well_harness.timeline_engine import (
./src/well_harness/demo_server.py:41:from well_harness.timeline_engine.executors.fantui import FantuiExecutor
./src/well_harness/demo_server.py:42:from well_harness.workbench_bundle import (
./src/well_harness/demo_server.py:462:            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
./src/well_harness/demo_server.py:490:            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
./src/well_harness/demo_server.py:544:        import well_harness as _wh
./src/well_harness/demo_server.py:561:                from well_harness.hardware_schema import (
./src/well_harness/switches.py:5:from well_harness.models import HarnessConfig, SwitchWindow
./src/well_harness/fault_diagnosis.py:6:from well_harness.controller_adapter import GenericControllerTruthAdapter
./src/well_harness/fault_diagnosis.py:7:from well_harness.document_intake import ControlSystemIntakePacket, intake_packet_to_workbench_spec
./src/well_harness/fault_diagnosis.py:8:from well_harness.fault_taxonomy import validate_fault_kind
./src/well_harness/fault_diagnosis.py:9:from well_harness.scenario_playback import (
./src/well_harness/fault_diagnosis.py:15:from well_harness.system_spec import ComponentSpec, ControlSystemWorkbenchSpec, FaultModeSpec, workbench_spec_from_dict
./src/well_harness/fantui_tick.py:21:from well_harness.controller import DeployController
./src/well_harness/fantui_tick.py:22:from well_harness.models import (
./src/well_harness/fantui_tick.py:28:from well_harness.plant import PlantState, SimplifiedDeployPlant
./src/well_harness/fantui_tick.py:29:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./src/well_harness/static/c919_etras_workstation.html:49:      <span class="etras-scope-note">控制器真值源：<code>src/well_harness/adapters/c919_etras_adapter.py</code></span>
./src/well_harness/static/c919_etras_workstation.html:623:      <code>src/well_harness/adapters/c919_etras_adapter.py</code> ·
./src/well_harness/static/demo.html:601:    <code>src/well_harness/demo_server.py::lever_snapshot_payload</code> →
./src/well_harness/static/demo.html:602:    <code>src/well_harness/controller.py::DeployController</code> ·
./src/well_harness/plant.py:6:from well_harness.models import ControllerOutputs, HarnessConfig, PlantDebugState, PlantSensors
./templates/new_system/README.md:13:| Template | `src/well_harness/adapters/your_system_adapter.py` | Python adapter implementing `GenericControllerTruthAdapter` |
./templates/new_system/README.md:14:| Template | `src/well_harness/adapters/your_system_intake_packet.py` | Builder function that produces a `ControlSystemIntakePacket` |
./templates/new_system/README.md:16:| **Reference** | `src/well_harness/adapters/landing_gear_adapter.py` | Complete working implementation — study this to understand the full pattern |
./templates/new_system/README.md:24:The actual files to create are in `src/well_harness/adapters/`:
./templates/new_system/README.md:51:- Imports `SourceDocumentRef` from `well_harness.document_intake`
./templates/new_system/README.md:84:- See `src/well_harness/fault_taxonomy.py` for the full enum
./templates/new_system/README.md:92:**`GenericControllerTruthAdapter` protocol** — defined in `src/well_harness/controller_adapter.py`:
./templates/new_system/README.md:111:LANDING_GEAR_SOURCE_OF_TRUTH = "src/well_harness/adapters/landing_gear_adapter.py"
./templates/new_system/README.md:136:from well_harness.adapters.landing_gear_adapter import build_landing_gear_workbench_spec
./templates/new_system/README.md:137:from well_harness.document_intake import (
./templates/new_system/README.md:142:from well_harness.system_spec import workbench_spec_from_dict
./templates/new_system/README.md:153:            location="src/well_harness/adapters/landing_gear_adapter.py",
./tests/test_validation_suite.py:61:    def test_build_child_env_prepends_repo_src_to_pythonpath(self):
./config/llm/local_model_candidates.yaml:58:#   - Backend switch:  LLM_BACKEND=ollama python -m well_harness.demo_server
./config/llm/local_model_candidates.yaml:65:#   pkill -f demo_server && python -m well_harness.demo_server &
./tools/validate_validation_schema_runner_report_schema.py:37:    existing_pythonpath = env.get("PYTHONPATH")
./tools/validate_validation_schema_runner_report_schema.py:40:        if not existing_pythonpath
./tools/validate_validation_schema_runner_report_schema.py:41:        else f"{src_path}{os.pathsep}{existing_pythonpath}"
./templates/new_system/SKELETON.py:13:  1. Copy this file to src/well_harness/adapters/your_system_skeleton.py
./templates/new_system/SKELETON.py:15:  3. Run: python3 tools/onboard_new_system_dry_run.py --spec-file src/well_harness/adapters/your_system_skeleton.py
./templates/new_system/SKELETON.py:21:from well_harness.controller_adapter import (
./templates/new_system/SKELETON.py:31:SKELETON_SOURCE_OF_TRUTH = "src/well_harness/adapters/your_system_skeleton.py"
./templates/new_system/SKELETON.py:72:    from well_harness.system_spec import (
./templates/new_system/SKELETON.py:224:    from well_harness.document_intake import (
./src/well_harness/scenario_playback.py:8:from well_harness.controller_adapter import GenericControllerTruthAdapter
./src/well_harness/scenario_playback.py:9:from well_harness.document_intake import ControlSystemIntakePacket, intake_packet_to_workbench_spec
./src/well_harness/scenario_playback.py:10:from well_harness.system_spec import (
./tools/validate_playback_trace_schema.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_playback_trace_schema.py:36:        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
./tools/validate_playback_trace_schema.py:69:        exit_code = well_harness_main(
./tests/test_archive_integrity.py:17:from well_harness.workbench_bundle import (
./tests/test_archive_integrity.py:25:from well_harness.document_intake import load_intake_packet
./templates/new_system/new_system_adapter.py:4:Follow this pattern to wire your physical system into the well_harness pipeline.
./templates/new_system/new_system_adapter.py:8:  1. Copy this file to src/well_harness/adapters/your_system_adapter.py
./templates/new_system/new_system_adapter.py:11:  4. Run tools/onboard_new_system_dry_run.py --spec-file src/well_harness/adapters/your_system_adapter.py
./templates/new_system/new_system_adapter.py:17:from well_harness.controller_adapter import (
./templates/new_system/new_system_adapter.py:28:NEW_SYSTEM_SOURCE_OF_TRUTH = "src/well_harness/adapters/your_system_adapter.py"
./templates/new_system/new_system_adapter.py:96:        by well_harness.system_spec.workbench_spec_to_dict().
./templates/new_system/new_system_adapter.py:98:    from well_harness.system_spec import (
./templates/new_system/new_system_adapter.py:220:    the well_harness pipeline. It must expose:
./tools/demo_path_smoke.py:18:from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
./tools/demo_path_smoke.py:19:from well_harness.demo_server import (
./tools/demo_path_smoke.py:24:from well_harness.models import HarnessConfig
./src/well_harness/static/fantui_circuit.html:403:  FANTUI LogicMVP · Frozen V1.0 · Signal scope: <code style="color:#cdd6e0;background:#111820;padding:0 3px">src/well_harness/controller.py::DeployController</code><br>
./config/hardware/thrust_reverser_hardware_v1.yaml:5:# Source:     HarnessConfig defaults (src/well_harness/models.py)
./tools/validate_validation_report_schema.py:37:    existing_pythonpath = env.get("PYTHONPATH")
./tools/validate_validation_report_schema.py:40:        if not existing_pythonpath
./tools/validate_validation_report_schema.py:41:        else f"{src_path}{os.pathsep}{existing_pythonpath}"
./templates/new_system/new_system_intake_packet.py:8:    from well_harness.adapters.your_system_intake_packet import build_new_system_intake_packet
./templates/new_system/new_system_intake_packet.py:15:from well_harness.document_intake import (
./templates/new_system/new_system_intake_packet.py:25:# from well_harness.adapters.your_system_adapter import (
./templates/new_system/new_system_intake_packet.py:64:    # (workbench_spec_from_dict is imported from well_harness.system_spec)
./tools/validate_landing_gear_adapter.py:14:from well_harness.adapters.landing_gear_adapter import (
./tests/test_workbench_column_rename.py:26:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_column_rename.py:30:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tools/validate_second_system_smoke_schema.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_second_system_smoke_schema.py:53:        exit_code = well_harness_main(["second-system-smoke", *(extra_args or []), "--format", "json"])
./src/well_harness/static/index.html:448:      <strong style="color:var(--home-text)">真值源</strong>：<code>src/well_harness/adapters/*.py</code> ·
./src/well_harness/static/index.html:449:      <strong style="color:var(--home-text)">启动服务</strong>：<code>python3 -m well_harness.demo_server --host 127.0.0.1 --port 8002</code> ·
./tools/validate_demo_answer_schema.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_demo_answer_schema.py:54:        exit_code = well_harness_main(["demo", "--format", "json", prompt])
./tools/validate_controller_truth_adapter_metadata_schema.py:14:from well_harness.controller_adapter import build_reference_controller_adapter
./tools/validate_controller_truth_adapter_metadata_schema.py:15:from well_harness.system_spec import current_reference_workbench_spec
./tests/test_controller.py:3:from well_harness.controller_adapter import ControllerTruthMetadata
./tests/test_controller.py:4:from well_harness.controller import DeployController
./tests/test_controller.py:5:from well_harness.models import (
./tests/test_controller.py:13:from well_harness.plant import PlantState, SimplifiedDeployPlant
./tests/test_controller.py:14:from well_harness.runner import SimulationRunner
./tests/test_controller.py:15:from well_harness.scenarios import nominal_deploy_scenario, retract_reset_scenario
./tests/test_controller.py:16:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./tools/validate_control_system_spec_schema.py:17:from well_harness.cli import main as well_harness_main
./tools/validate_control_system_spec_schema.py:18:from well_harness.document_intake import assess_intake_packet, load_intake_packet
./tools/validate_control_system_spec_schema.py:44:        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
./tools/validate_control_system_spec_schema.py:77:        exit_code = well_harness_main(["spec", "--format", "json"])
./tools/validate_workbench_bundle_schema.py:15:from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
./tools/validate_workbench_bundle_schema.py:16:from well_harness.workbench_bundle import build_workbench_bundle
./tools/validate_workbench_bundle_schema.py:42:        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
./tools/validate_two_system_runtime_comparison.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_two_system_runtime_comparison.py:53:        exit_code = well_harness_main(["two-system-runtime-comparison", "--format", "json"])
./tests/test_workbench_start.py:31:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_start.py:35:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tools/validate_debug_json_schema.py:10:from well_harness.cli import main as cli_main
./tools/validate_debug_json_schema.py:14:SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "well_harness_debug_v1.schema.json"
./tools/validate_landing_gear_playback.py:14:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tools/validate_landing_gear_playback.py:15:from well_harness.scenario_playback import build_playback_report_from_truth_adapter
./scripts/backend_switch_drill.py:128:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
./tools/run_gsd_validation_suite.py:56:            (python, "-m", "well_harness.cli", "second-system-smoke", "--format", "json"),
./tools/run_gsd_validation_suite.py:136:    existing_pythonpath = env.get("PYTHONPATH")
./tools/run_gsd_validation_suite.py:137:    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
./archive/shelved/multi-system-ui/SHELVED.md:5:The **pre-unification** form of `src/well_harness/static/demo.html` (+ `demo.js`
./archive/shelved/multi-system-ui/SHELVED.md:39:| legacy-demo.html | src/well_harness/static/demo.html | 136 KB |
./archive/shelved/multi-system-ui/SHELVED.md:40:| legacy-demo.js | src/well_harness/static/demo.js | 82 KB |
./archive/shelved/multi-system-ui/SHELVED.md:41:| legacy-demo.css | src/well_harness/static/demo.css | 69 KB |
./archive/shelved/multi-system-ui/SHELVED.md:61:- Adapter (live): `src/well_harness/adapters/landing_gear_adapter.py`
./archive/shelved/multi-system-ui/SHELVED.md:70:- Adapter (live): `src/well_harness/adapters/efds_adapter.py`
./archive/shelved/multi-system-ui/SHELVED.md:89:   current `src/well_harness/static/demo.html` ETRAS-style grid as an
./archive/shelved/multi-system-ui/SHELVED.md:93:3. **Full multi-system back**: `cp archive/shelved/multi-system-ui/static/legacy-demo.* src/well_harness/static/` then reconcile with any subsequent
./archive/shelved/multi-system-ui/SHELVED.md:104:- `src/well_harness/adapters/landing_gear_adapter.py` — still live
./archive/shelved/multi-system-ui/SHELVED.md:105:- `src/well_harness/adapters/bleed_air_adapter.py` — still live
./archive/shelved/multi-system-ui/SHELVED.md:106:- `src/well_harness/adapters/efds_adapter.py` — still live
./archive/shelved/multi-system-ui/SHELVED.md:107:- `src/well_harness/demo_server.py` — POST `/api/system-snapshot` still
./tools/validate_fault_taxonomy_schema.py:14:from well_harness.fault_taxonomy import SUPPORTED_FAULT_KINDS, fault_taxonomy_to_dict
./tools/check_authority_contract.py:20:_WORKBENCH_JS = _REPO / "src" / "well_harness" / "static" / "workbench.js"
./tools/check_authority_contract.py:21:_WORKBENCH_PY = _REPO / "src" / "well_harness" / "workbench_bundle.py"
./tools/check_authority_contract.py:22:_DEMO_SERVER   = _REPO / "src" / "well_harness" / "demo_server.py"
./tools/check_authority_contract.py:23:_GENERATOR_PY  = _REPO / "src" / "well_harness" / "tools" / "generate_adapter.py"
./tools/check_authority_contract.py:64:    Scans demo_server.py AND all *.py under src/well_harness/ (excl. static assets).
./tools/check_authority_contract.py:75:    # All other Python files under src/well_harness/ (wide backend scan)
./tools/check_authority_contract.py:76:    well_harness = _REPO / "src" / "well_harness"
./tools/check_authority_contract.py:77:    if well_harness.exists():
./tools/check_authority_contract.py:78:        for py_file in sorted(well_harness.rglob("*.py")):
./tools/check_authority_contract.py:103:        "detail": backend_hits or ["src/well_harness/**/*.py: 0 occurrences of draft_design_state — compliant"],
./src/well_harness/controller.py:5:from well_harness.models import (
./tools/validate_workbench_archive_manifest_schema.py:16:from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
./tools/validate_workbench_archive_manifest_schema.py:17:from well_harness.workbench_bundle import (
./archive/shelved/llm-features/src/ai_doc_analyzer.py:13:from well_harness.document_intake import (
./archive/shelved/llm-features/src/ai_doc_analyzer.py:17:from well_harness.system_spec import (
./archive/shelved/llm-features/src/ai_doc_analyzer.py:25:from well_harness.workbench_bundle import build_workbench_bundle as _build_workbench_bundle
./tools/validate_landing_gear_diagnosis.py:14:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tools/validate_landing_gear_diagnosis.py:15:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_truth_adapter
./scripts/c919_etras_panel_server.py:13:# Add src/ to path for well_harness imports
./scripts/c919_etras_panel_server.py:17:from well_harness.adapters.c919_etras_frozen_v1 import (
./scripts/c919_etras_panel_server.py:25:from well_harness.adapters.c919_etras_frozen_v1.cmd3_latch_controller import (
./scripts/c919_etras_panel_server.py:29:from well_harness.timeline_engine import TimelinePlayer, parse_timeline
./scripts/c919_etras_panel_server.py:30:from well_harness.timeline_engine.validator import ValidationError as TimelineValidationError
./scripts/c919_etras_panel_server.py:31:from well_harness.timeline_engine.executors.c919_etras import C919ETRASExecutor
./scripts/c919_etras_panel_server.py:34:STATIC = _REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel"
./scripts/c919_etras_panel_server.py:37:SHARED_STATIC_ROOT = _REPO_ROOT / "src" / "well_harness" / "static"
./tools/validate_validation_schema_checker_report_schema.py:36:    existing_pythonpath = env.get("PYTHONPATH")
./tools/validate_validation_schema_checker_report_schema.py:39:        if not existing_pythonpath
./tools/validate_validation_schema_checker_report_schema.py:40:        else f"{src_path}{os.pathsep}{existing_pythonpath}"
./src/well_harness/reverse_diagnosis.py:16:from well_harness.hardware_schema import (
./archive/shelved/llm-features/SHELVED.md:12:### Static frontend (6 files) — from `src/well_harness/static/`
./archive/shelved/llm-features/SHELVED.md:22:### Python modules (2 files) — from `src/well_harness/`
./archive/shelved/llm-features/SHELVED.md:43:## Routes removed from `src/well_harness/demo_server.py`
./archive/shelved/llm-features/SHELVED.md:75:1. `git mv archive/shelved/llm-features/static/* src/well_harness/static/`
./archive/shelved/llm-features/SHELVED.md:76:2. `git mv archive/shelved/llm-features/src/{llm_client.py,ai_doc_analyzer.py} src/well_harness/`
./archive/shelved/llm-features/SHELVED.md:78:4. Restore `demo_server.py` imports, route constants, POST allowlist entries, dispatch blocks, and handler bodies (reference pre-Phase-A git history: `git log --oneline -- src/well_harness/demo_server.py`)
./tools/demo_ui_handcheck.py:11:START_COMMAND = "PYTHONPATH=src python3 -m well_harness.demo_server"
./tools/demo_ui_handcheck.py:12:OPEN_COMMAND = "PYTHONPATH=src python3 -m well_harness.demo_server --open"
./src/well_harness/document_intake.py:8:from well_harness.fault_taxonomy import validate_fault_kind
./src/well_harness/document_intake.py:9:from well_harness.system_spec import (
./tools/validate_landing_gear_knowledge.py:14:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tools/validate_landing_gear_knowledge.py:15:from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter
./tools/validate_landing_gear_full_pipeline.py:32:from well_harness.adapters.landing_gear_intake_packet import build_landing_gear_intake_packet
./tools/validate_landing_gear_full_pipeline.py:33:from well_harness.document_intake import intake_packet_to_workbench_spec
./tools/validate_landing_gear_full_pipeline.py:34:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
./tools/validate_landing_gear_full_pipeline.py:35:from well_harness.knowledge_capture import build_knowledge_artifact
./tools/validate_landing_gear_full_pipeline.py:36:from well_harness.scenario_playback import build_playback_report_from_intake_packet
./tools/validate_landing_gear_full_pipeline.py:37:from well_harness.system_spec import workbench_spec_to_dict
./tools/validate_fault_diagnosis_schema.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_fault_diagnosis_schema.py:37:        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
./tools/validate_fault_diagnosis_schema.py:71:        exit_code = well_harness_main(
./tools/gsd_notion_sync.py:1192:    existing_pythonpath = env.get("PYTHONPATH")
./tools/gsd_notion_sync.py:1193:    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
./tests/test_fantui_circuit_wires.py:19:CIRCUIT_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "fantui_circuit.html"
./tools/validate_knowledge_artifact_schema.py:16:from well_harness.cli import main as well_harness_main
./tools/validate_knowledge_artifact_schema.py:41:        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
./tools/validate_knowledge_artifact_schema.py:75:        exit_code = well_harness_main(
./src/well_harness/workbench/pr_review.py:11:from well_harness.collab.restricted_auth import RestrictedAuthError, validate_push_attempt
./tests/test_workbench_approval_center.py:6:from well_harness.workbench.approval import ApprovalCenter, WorkbenchPermissionError
./tests/test_workbench_approval_center.py:7:from well_harness.workbench.proposals import build_annotation_proposal
./tests/test_workbench_approval_center.py:85:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
./scripts/dress_rehearsal.py:4:Boots well_harness.demo_server on :8799 as a subprocess, replays the HTTP
./scripts/dress_rehearsal.py:137:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
./src/well_harness/monte_carlo_engine.py:18:from well_harness.hardware_schema import (
./tools/onboard_new_system_dry_run.py:33:from well_harness.document_intake import (
./tools/onboard_new_system_dry_run.py:39:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
./tools/onboard_new_system_dry_run.py:40:from well_harness.knowledge_capture import build_knowledge_artifact
./tools/onboard_new_system_dry_run.py:41:from well_harness.scenario_playback import build_playback_report_from_intake_packet
./tools/onboard_new_system_dry_run.py:42:from well_harness.system_spec import workbench_spec_from_dict, workbench_spec_to_dict
./src/well_harness/workbench/prompting.py:13:    "src/well_harness/workbench/**",
./src/well_harness/workbench/prompting.py:14:    "src/well_harness/static/workbench.*",
./src/well_harness/workbench/prompting.py:15:    "src/well_harness/static/annotation_overlay.js",
./tools/validate_generator_adapter.py:15:from well_harness.controller_adapter import build_reference_controller_adapter
./tools/validate_generator_adapter.py:16:from well_harness.tools.generate_adapter import spec_to_adapter_source
./tools/validate_generator_adapter.py:19:SPEC_PATH = PROJECT_ROOT / "src" / "well_harness" / "tools" / "specs" / "reference_thrust_reverser.spec.json"
./tests/test_pr_close_loop.py:4:from well_harness.collab.merge_close import build_merge_close_plan, close_ticket_with_verdict
./tests/test_pr_close_loop.py:5:from well_harness.workbench.pr_review import extract_changed_files, review_pr_diff
./tests/test_pr_close_loop.py:14:        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
./tests/test_pr_close_loop.py:15:        "Generated Prompt": "## anchor\nproposal\n\n## scope\nsrc/well_harness/workbench/**",
./tests/test_pr_close_loop.py:37:    assert extract_changed_files(_diff_for("src/well_harness/workbench/pr_review.py")) == [
./tests/test_pr_close_loop.py:38:        "src/well_harness/workbench/pr_review.py"
./tests/test_pr_close_loop.py:43:    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/workbench/pr_review.py"))
./tests/test_pr_close_loop.py:46:    assert report["changed_files"] == ["src/well_harness/workbench/pr_review.py"]
./tests/test_pr_close_loop.py:51:    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/controller.py"))
./tests/test_pr_close_loop.py:59:    report = review_pr_diff(ticket, _diff_for("src/well_harness/workbench/pr_review.py"))
./archive/shelved/llm-features/tests/test_pitch_prewarm.py:16:from well_harness import demo_server
./archive/shelved/llm-features/tests/test_pitch_prewarm.py:17:from well_harness.demo_server import DemoRequestHandler
./tests/test_lever_snapshot_manual_override_guard.py:22:from well_harness.demo_server import DemoRequestHandler
./archive/shelved/llm-features/tests/test_llm_client.py:21:from well_harness import llm_client as lc
./tests/test_workbench_dual_route.py:27:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_dual_route.py:31:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./scripts/pitch_readiness.py:13:    python3 src/well_harness/static/adversarial_test.py      # ~3s
./scripts/pitch_readiness.py:388:        "- adversarial 8/8 (run `python3 src/well_harness/static/adversarial_test.py`)",
./tests/test_timeline_engine.py:16:from well_harness.timeline_engine import (
./tests/test_timeline_engine.py:26:from well_harness.timeline_engine.fault_schedule import compile_fault_schedule
./src/well_harness/cli.py:8:from well_harness.demo import answer_demo_prompt, demo_answer_to_payload, render_demo_answer
./src/well_harness/cli.py:9:from well_harness.document_intake import (
./src/well_harness/cli.py:17:from well_harness.fault_diagnosis import (
./src/well_harness/cli.py:21:from well_harness.knowledge_capture import build_knowledge_artifact, render_knowledge_artifact_text
./src/well_harness/cli.py:22:from well_harness.runner import SimulationRunner
./src/well_harness/cli.py:23:from well_harness.scenarios import BUILT_IN_SCENARIOS
./src/well_harness/cli.py:24:from well_harness.scenario_playback import build_playback_report_from_intake_packet, render_playback_report_text
./src/well_harness/cli.py:25:from well_harness.second_system_smoke import (
./src/well_harness/cli.py:29:from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict
./src/well_harness/cli.py:30:from well_harness.two_system_runtime_comparison import (
./src/well_harness/cli.py:34:from well_harness.workbench_bundle import (
./src/well_harness/cli.py:44:JSON_SCHEMA_NAME = "well_harness.debug"
./src/well_harness/cli.py:48:    parser = argparse.ArgumentParser(prog="well_harness")
./tests/test_thrust_reverser_intake_packet.py:26:from well_harness.adapters.thrust_reverser_intake_packet import (
./tests/test_thrust_reverser_intake_packet.py:31:from well_harness.document_intake import ControlSystemIntakePacket
./tests/test_thrust_reverser_intake_packet.py:36:    assert THRUST_REVERSER_SOURCE_OF_TRUTH == "src/well_harness/controller.py"
./tests/test_monte_carlo_engine.py:20:from well_harness.monte_carlo_engine import MonteCarloEngine, ReliabilityResult
./archive/shelved/llm-features/tests/test_chat_operate_input_validation.py:15:from well_harness.demo_server import _handle_chat_operate, _handle_chat_reason
./tests/test_workbench_authority_banner.py:23:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_authority_banner.py:27:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./archive/shelved/llm-features/tests/test_p43_02_5_c919_panel_schema_alignment.py:19:from well_harness.adapters.c919_etras_adapter import build_c919_etras_workbench_spec
./archive/shelved/llm-features/tests/test_p43_02_5_c919_panel_schema_alignment.py:24:    / "src" / "well_harness" / "static" / "chat.html"
./src/well_harness/controller_adapter.py:6:from well_harness.controller import DeployController
./src/well_harness/controller_adapter.py:7:from well_harness.models import ControllerExplain, ControllerOutputs, HarnessConfig, ResolvedInputs
./src/well_harness/controller_adapter.py:105:    source_of_truth="src/well_harness/controller.py",
./src/well_harness/controller_adapter.py:128:        from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict
./tests/test_c919_etras_frozen_v1_unit.py:6:from well_harness.adapters.c919_etras_frozen_v1 import (
./tests/test_second_system_smoke.py:7:from well_harness.cli import main
./tests/test_second_system_smoke.py:8:from well_harness.second_system_smoke import (
./archive/shelved/llm-features/tests/test_p14_ai_doc_analyzer.py:14:from well_harness.demo_server import DemoRequestHandler
./src/well_harness/workbench_bundle.py:11:from well_harness.document_intake import (
./src/well_harness/workbench_bundle.py:16:from well_harness.fault_diagnosis import (
./src/well_harness/workbench_bundle.py:20:from well_harness.knowledge_capture import KnowledgeArtifact, build_knowledge_artifact
./src/well_harness/workbench_bundle.py:21:from well_harness.scenario_playback import (
./src/well_harness/workbench_bundle.py:32:ARCHIVE_MANIFEST_SELF_CHECK_COMMAND = "python3 -m well_harness.cli archive-manifest ."
./tests/test_p43_authority_contract.py:27:_WJS  = _REPO / "src" / "well_harness" / "static" / "workbench.js"
./tests/test_p43_authority_contract.py:28:_WPY  = _REPO / "src" / "well_harness" / "workbench_bundle.py"
./tests/test_p43_authority_contract.py:29:_DSV  = _REPO / "src" / "well_harness" / "demo_server.py"
./tests/test_fault_taxonomy.py:5:from well_harness.fault_taxonomy import (
./tests/test_pitch_citations.py:155:        "See `src/well_harness/controller.py` (line 42) and "
./tests/test_pitch_citations.py:159:    assert "src/well_harness/controller.py" in cites
./src/well_harness/collab/merge_close.py:6:from well_harness.workbench.audit import AuditEventLog
./archive/shelved/llm-features/tests/test_chat_operate.py:25:from well_harness.demo_server import DemoRequestHandler, lever_snapshot_payload
./archive/shelved/llm-features/tests/test_chat_operate.py:218:        from well_harness import llm_client as lc
./tests/test_workbench_state_of_world_bar.py:22:from well_harness.demo_server import (
./tests/test_workbench_state_of_world_bar.py:29:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./archive/shelved/llm-features/tests/test_chat_reason_input_validation.py:16:from well_harness.demo_server import _handle_chat_reason
./tests/conftest.py:13:from well_harness.adapters.c919_etras_frozen_v1 import LockInputs, RawInputs
./tests/test_fault_diagnosis.py:7:from well_harness.cli import main
./tests/test_fault_diagnosis.py:8:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tests/test_fault_diagnosis.py:9:from well_harness.document_intake import load_intake_packet
./tests/test_fault_diagnosis.py:10:from well_harness.fault_diagnosis import (
./tests/test_fault_diagnosis.py:17:from well_harness.scenario_playback import PLAYBACK_TRACE_KIND
./tests/test_timeline_sim_page.py:11:from well_harness.demo_server import DemoRequestHandler
./tests/test_timeline_sim_page.py:15:STATIC_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"
./archive/shelved/llm-features/tests/e2e/test_demo_resilience.py:135:        REPO_ROOT / "src" / "well_harness" / "static" / "adversarial_test.py"
./archive/shelved/llm-features/tests/test_canvas_interaction_artifacts.py:18:SRC_DIR = Path(__file__).parent.parent / "src" / "well_harness" / "static"
./tests/test_fantui_tick_runtime.py:19:from well_harness.demo_server import DemoRequestHandler
./tests/test_fantui_tick_runtime.py:20:from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
./tests/test_fantui_tick_runtime.py:21:from well_harness.models import PilotInputs
./tests/test_fantui_tick_runtime.py:25:STATIC_ROOT = REPO_ROOT / "src" / "well_harness" / "static"
./tests/test_fantui_tick_runtime.py:245:        from well_harness import demo_server
./archive/shelved/llm-features/tests/test_p43_doc_analyzer_blocker_fix.py:25:from well_harness.ai_doc_analyzer import run_pipeline_from_intake
./archive/shelved/llm-features/tests/test_p43_doc_analyzer_blocker_fix.py:32:SOURCE_FILE = Path(__file__).parent.parent / "src" / "well_harness" / "ai_doc_analyzer.py"
./archive/shelved/llm-features/tests/test_p43_doc_analyzer_blocker_fix.py:33:FRONTEND_FILE = Path(__file__).parent.parent / "src" / "well_harness" / "static" / "ai-doc-analyzer.js"
./tests/test_content_type_whitelist.py:14:from well_harness.demo_server import DemoRequestHandler
./archive/shelved/llm-features/tests/test_demo_llm_tests_snippet.py:10:- well_harness.llm_client (now in archive/shelved/llm-features/src/)
./archive/shelved/llm-features/tests/test_demo_llm_tests_snippet.py:59:        from well_harness import llm_client as lc
./archive/shelved/llm-features/tests/test_p43_readAsText_browser_behavior.py:8:`src/well_harness/static/ai-doc-analyzer.js:224` silently produces garbage
./archive/shelved/llm-features/tests/test_p43_readAsText_browser_behavior.py:90:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
./tests/test_nan_inf_clamp.py:7:from well_harness.demo_server import _optional_request_float
./tests/test_nan_inf_clamp.py:8:from well_harness.scenario_playback import _sample_times
./tests/test_demo.py:15:from well_harness import demo_server
./tests/test_demo.py:16:from well_harness.cli import main
./tests/test_demo.py:17:from well_harness.demo import NODE_CATALOG, answer_demo_prompt
./tests/test_demo.py:18:from well_harness.demo_server import DemoRequestHandler
./tests/test_demo.py:19:from well_harness.models import HarnessConfig
./tests/test_demo.py:20:from well_harness.workbench_bundle import archive_workbench_bundle, build_workbench_bundle
./tests/test_demo.py:35:DEMO_UI_STATIC_DIR = PROJECT_ROOT / "src" / "well_harness" / "static"
./tests/test_demo.py:62:    existing_pythonpath = env.get("PYTHONPATH")
./tests/test_demo.py:65:        if not existing_pythonpath
./tests/test_demo.py:66:        else f"{src_path}{os.pathsep}{existing_pythonpath}"
./tests/test_demo.py:93:        self.assertEqual(asset["name"], "well_harness.demo_answer.asset")
./tests/test_demo.py:121:        self.assertEqual(asset["name"], "well_harness.demo_json_output.asset")
./tests/test_demo.py:1547:            [sys.executable, "-m", "well_harness.demo_server", "--help"],
./tests/test_demo.py:1686:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
./tests/test_demo.py:1687:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
./tests/test_demo.py:1771:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
./tests/test_demo.py:1772:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
./tests/test_demo.py:1867:            "PYTHONPATH=src python3 -m well_harness.demo_server",
./tests/test_demo.py:1868:            "PYTHONPATH=src python3 -m well_harness.demo_server --open",
./tests/test_workbench_annotation_static.py:8:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
./tests/test_workbench_annotation_static.py:17:    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")
./tests/test_workbench_annotation_static.py:28:    script = (PROJECT_ROOT / "src/well_harness/static/annotation_overlay.js").read_text(encoding="utf-8")
./tests/test_p19_api_multisystem.py:37:        from well_harness.demo_server import DemoRequestHandler
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:13:from well_harness.ai_doc_analyzer import (
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:50:        from well_harness.ai_doc_analyzer import Question
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:177:    from well_harness.document_intake import intake_packet_from_dict
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:191:    from well_harness.document_intake import intake_packet_from_dict
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:207:    from well_harness.document_intake import intake_packet_from_dict
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:242:        from well_harness.ai_doc_analyzer import Question as P14Question
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:284:    from well_harness.demo_server import _handle_p15_convert
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:298:    from well_harness.demo_server import _handle_p15_convert
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:308:    from well_harness.demo_server import _handle_p15_convert
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:321:    from well_harness import demo_server
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:376:    from well_harness.demo_server import _handle_p15_run_pipeline
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:390:    from well_harness.demo_server import _handle_p15_convert, _handle_p15_run_pipeline
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:411:    from well_harness.demo_server import P15_CONVERT_PATH, P15_RUN_PIPELINE_PATH
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:420:    from well_harness.demo_server import DemoRequestHandler
./archive/shelved/llm-features/tests/test_p15_pipeline_integration.py:444:    from well_harness.ai_doc_analyzer import _MOCK_INTAKE_PACKET
./archive/shelved/llm-features/tests/test_pitch_symbols.py:43:        "src/well_harness/controller.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:51:        "src/well_harness/demo_server.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:58:        "src/well_harness/demo_server.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:65:        "src/well_harness/demo_server.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:73:        "src/well_harness/llm_client.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:80:        "src/well_harness/llm_client.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:87:        "src/well_harness/llm_client.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:94:        "src/well_harness/llm_client.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:101:        "src/well_harness/llm_client.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:109:        "src/well_harness/demo_server.py",
./archive/shelved/llm-features/tests/test_pitch_symbols.py:116:        "src/well_harness/demo_server.py",
./tests/test_c919_circuit_wires.py:17:CIRCUIT_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel" / "circuit.html"
./pyproject.toml:38:# - src: well_harness package imports
./pyproject.toml:40:pythonpath = ["src", "."]
./tests/test_c919_chart_integration.py:19:C919_INDEX = REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel" / "index.html"
./tests/test_c919_chart_integration.py:21:TIMESERIES_JS = REPO_ROOT / "src" / "well_harness" / "static" / "timeseries_chart.js"
./tests/test_generator_parity.py:13:_spec_path = os.path.join(os.path.dirname(__file__), "..", "src", "well_harness", "tools", "specs", "reference_thrust_reverser.spec.json")
./tests/test_generator_parity.py:17:from well_harness.tools.generate_adapter import spec_to_adapter_source
./tests/test_generator_parity.py:30:from well_harness.controller_adapter import (
./tests/e2e/test_wow_b_monte_carlo.py:19:# From src/well_harness/monte_carlo_engine.py failure-mode enum
./tests/test_workbench_annotation_vocab.py:29:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_annotation_vocab.py:33:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tests/test_onboard_new_system_dry_run.py:34:    "source_of_truth": "src/well_harness/adapters/landing_gear_adapter.py",
./tests/test_workbench_wow_starters.py:31:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_wow_starters.py:35:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tests/test_c919_etras_frozen_v1_integration.py:6:from well_harness.adapters.c919_etras_frozen_v1 import C919ReverseThrustSystem, FrozenConfig, SystemState
./tests/test_knowledge_capture.py:7:from well_harness.cli import main
./tests/test_knowledge_capture.py:8:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tests/test_knowledge_capture.py:9:from well_harness.document_intake import load_intake_packet
./tests/test_knowledge_capture.py:10:from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
./tests/test_knowledge_capture.py:11:from well_harness.knowledge_capture import (
./tests/test_proposal_schema_store.py:6:from well_harness.workbench.proposals import (
./tests/test_timeline_c919_etras.py:15:from well_harness.timeline_engine import (
./tests/test_timeline_c919_etras.py:21:from well_harness.timeline_engine.executors.c919_etras import C919ETRASExecutor
./tests/test_timeline_c919_etras.py:25:TIMELINE_FIXTURES_DIR = REPO_ROOT / "src" / "well_harness" / "timelines"
./tests/test_adapter_freeze_banner.py:31:    "src/well_harness/adapters/bleed_air_adapter.py",
./tests/test_adapter_freeze_banner.py:32:    "src/well_harness/adapters/efds_adapter.py",
./tests/test_adapter_freeze_banner.py:33:    "src/well_harness/adapters/landing_gear_adapter.py",
./tests/test_adapter_freeze_banner.py:37:    "src/well_harness/adapters/bleed_air_intake_packet.py",
./tests/test_adapter_freeze_banner.py:38:    "src/well_harness/adapters/landing_gear_intake_packet.py",
./tests/test_c919_etras_workstation.py:4:with the adapter truth source (src/well_harness/adapters/c919_etras_adapter.py):
./tests/test_c919_etras_workstation.py:22:from well_harness.adapters.c919_etras_adapter import build_c919_etras_workbench_spec
./tests/test_c919_etras_workstation.py:23:from well_harness.demo_server import DemoRequestHandler
./tests/test_c919_etras_workstation.py:27:STATIC_DIR = PROJECT_ROOT / "src" / "well_harness" / "static"
./tests/test_two_system_runtime_comparison.py:7:from well_harness.cli import main
./tests/test_two_system_runtime_comparison.py:8:from well_harness.two_system_runtime_comparison import (
./tests/test_system_spec.py:5:from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
./tests/test_system_spec.py:6:from well_harness.models import HarnessConfig
./tests/test_system_spec.py:7:from well_harness.system_spec import (
./tests/test_p19_api_endpoints.py:38:        from well_harness.demo_server import DemoRequestHandler
./tests/test_landing_gear_adapter.py:5:from well_harness.adapters.landing_gear_adapter import (
./tests/test_landing_gear_adapter.py:11:from well_harness.controller_adapter import (
./tests/test_landing_gear_adapter.py:14:from well_harness.system_spec import CONTROL_SYSTEM_SPEC_SCHEMA_ID
./tests/test_landing_gear_adapter.py:40:        self.assertEqual("src/well_harness/adapters/landing_gear_adapter.py", payload["source_of_truth"])
./tests/test_landing_gear_adapter.py:47:        self.assertEqual("src/well_harness/adapters/landing_gear_adapter.py", payload["source_of_truth"])
./tests/test_c919_etras_adapter.py:27:from well_harness.adapters.c919_etras_adapter import (
./tests/test_c919_etras_adapter.py:42:from well_harness.adapters.c919_etras_intake_packet import (
./tests/test_c919_etras_adapter.py:45:from well_harness.controller_adapter import (
./tests/test_c919_etras_adapter.py:48:from well_harness.system_spec import CONTROL_SYSTEM_SPEC_SCHEMA_ID
./tests/test_c919_etras_adapter.py:137:            "src/well_harness/adapters/c919_etras_adapter.py",
./tests/test_timeline_fantui.py:13:from well_harness.demo_server import DemoRequestHandler
./tests/test_timeline_fantui.py:14:from well_harness.timeline_engine import (
./tests/test_timeline_fantui.py:20:from well_harness.timeline_engine.executors.fantui import FantuiExecutor
./tests/test_timeline_fantui.py:23:TIMELINE_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "src" / "well_harness" / "timelines"
./tests/test_archive_restore_sandbox.py:16:from well_harness.demo_server import build_workbench_archive_restore_response, default_workbench_archive_root
./tests/test_archive_restore_sandbox.py:17:from well_harness.document_intake import load_intake_packet
./tests/test_archive_restore_sandbox.py:18:from well_harness.workbench_bundle import (
./tests/test_archive_restore_sandbox.py:90:            "command": "python3 -m well_harness.cli archive-manifest .",
./tests/test_archive_restore_sandbox.py:323:        from well_harness.workbench_bundle import SandboxEscapeError
./tests/test_scenario_playback.py:10:from well_harness.cli import main
./tests/test_scenario_playback.py:11:from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
./tests/test_scenario_playback.py:12:from well_harness.document_intake import load_intake_packet
./tests/test_scenario_playback.py:13:from well_harness.scenario_playback import (
./tests/test_scenario_playback.py:103:        from well_harness.controller_adapter import build_reference_controller_adapter
./tests/test_scenario_playback.py:191:                "well_harness.cli",
./tests/test_workbench_bundle.py:12:from well_harness.cli import main
./tests/test_workbench_bundle.py:13:from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
./tests/test_workbench_bundle.py:14:from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
./tests/test_workbench_bundle.py:15:from well_harness.knowledge_capture import KNOWLEDGE_ARTIFACT_KIND
./tests/test_workbench_bundle.py:16:from well_harness.scenario_playback import PLAYBACK_TRACE_KIND
./tests/test_workbench_bundle.py:17:from well_harness.workbench_bundle import (
./tests/test_workbench_bundle.py:223:                "python3 -m well_harness.cli archive-manifest .",
./tests/test_workbench_bundle.py:234:            self.assertIn("python3 -m well_harness.cli archive-manifest .", saved_summary)
./tests/test_workbench_bundle.py:333:            "python3 -m well_harness.cli archive-manifest .",
./tests/test_workbench_bundle.py:399:        self.assertEqual("python3 -m well_harness.cli archive-manifest .", payload["self_check"]["command"])
./tests/test_workbench_bundle.py:435:        self.assertIn("self_check: python3 -m well_harness.cli archive-manifest .", text)
./tests/test_workbench_bundle.py:447:        existing_pythonpath = env.get("PYTHONPATH")
./tests/test_workbench_bundle.py:448:        env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
./tests/test_workbench_bundle.py:457:                [sys.executable, "-m", "well_harness.cli", "archive-manifest", "."],
./tests/test_workbench_bundle.py:467:        self.assertIn("self_check: python3 -m well_harness.cli archive-manifest .", result.stdout)
./tests/test_workbench_bundle.py:714:            with mock.patch("well_harness.workbench_bundle._archive_timestamp", return_value="20260411T080000Z"):
./tests/test_reverse_diagnosis.py:16:from well_harness.reverse_diagnosis import (
./tests/e2e/conftest.py:3:Boots well_harness.demo_server as a subprocess on port 8799, waits until
./tests/e2e/conftest.py:63:    # user-site resolution of the editable-installed well_harness package.
./tests/e2e/conftest.py:70:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
./tests/test_controller_truth_metadata_schema_extension.py:30:from well_harness.controller_adapter import (  # noqa: E402
./tests/test_controller_truth_metadata_schema_extension.py:37:from well_harness.tools.generate_adapter import spec_to_adapter_source  # noqa: E402
./tests/test_controller_truth_metadata_schema_extension.py:200:        spec_path = _REPO_ROOT / "src/well_harness/tools/specs/reference_thrust_reverser.spec.json"
./tests/test_controller_truth_metadata_schema_extension.py:221:            "from well_harness.controller_adapter import (\n    ControllerTruthMetadata,\n    GenericTruthEvaluation,\n)",
./tests/test_controller_adapter.py:6:from well_harness.controller import DeployController
./tests/test_controller_adapter.py:7:from well_harness.controller_adapter import (
./tests/test_controller_adapter.py:14:from well_harness.models import HarnessConfig, ResolvedInputs
./tests/test_controller_adapter.py:56:        self.assertEqual(adapter.metadata.source_of_truth, "src/well_harness/controller.py")
./tests/test_controller_adapter.py:68:        self.assertEqual("src/well_harness/controller.py", payload["source_of_truth"])
./tests/test_controller_adapter.py:112:        self.assertEqual("src/well_harness/controller.py", payload["source_of_truth"])
./tests/test_workbench_trust_affordance.py:23:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_trust_affordance.py:27:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tests/test_cli.py:10:from well_harness.cli import main
./tests/test_cli.py:11:from well_harness.models import DIAGNOSIS_CONTEXT_FIELDS
./tests/test_cli.py:12:from well_harness.runner import SimulationRunner
./tests/test_cli.py:13:from well_harness.scenarios import nominal_deploy_scenario, retract_reset_scenario
./tests/test_cli.py:17:JSON_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "well_harness_debug_v1.schema.json"
./tests/test_cli.py:161:    existing_pythonpath = env.get("PYTHONPATH")
./tests/test_cli.py:164:        if not existing_pythonpath
./tests/test_cli.py:165:        else f"{src_path}{os.pathsep}{existing_pythonpath}"
./tests/test_cli.py:364:                "name": "well_harness.debug",
./tests/test_cli.py:479:        self.assertEqual(schema_contract["schema_name"], "well_harness.debug")
./tests/test_cli.py:688:        self.assertNotIn("well_harness: error:", result.stdout)
./tests/test_cli.py:701:        self.assertNotIn("well_harness: error:", result.stdout)
./tests/test_cli.py:714:        self.assertNotIn("well_harness: error:", result.stdout)
./tests/test_cli.py:727:        self.assertNotIn("well_harness: error:", result.stdout)
./tests/test_cli.py:757:        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
./tests/test_cli.py:773:        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
./tests/test_cli.py:785:        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
./tests/test_cli.py:795:        self.assertNotIn("well_harness: error:", result.stdout)
./tests/test_cli.py:854:        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_report")
./tests/test_cli.py:1092:        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_schema_runner_report")
./tests/test_cli.py:1152:        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_schema_checker_report")
./tests/test_hardware_schema.py:21:from well_harness.hardware_schema import (
./src/well_harness/tools/generate_adapter.py:9:    python -m well_harness.tools.generate_adapter path/to/spec.json -o output_adapter.py
./src/well_harness/tools/generate_adapter.py:65:It was generated by: well_harness.tools.generate_adapter
./src/well_harness/tools/generate_adapter.py:87:    L("from well_harness.controller_adapter import (")
./src/well_harness/tools/generate_adapter.py:580:It was generated by: well_harness.tools.generate_adapter
./src/well_harness/tools/generate_adapter.py:588:_THIRD_PARTY_IMPORT_BLOCK = '''from well_harness.controller_adapter import (
./tests/test_lever_snapshot_boundaries.py:16:from well_harness.demo_server import lever_snapshot_payload
./tests/test_lever_snapshot_boundaries.py:17:from well_harness.models import HarnessConfig
./tests/test_lever_snapshot_boundaries.py:18:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./tests/test_metadata_registry_consistency.py:21:    well_harness namespace must equal the set of metadata_const values
./tests/test_metadata_registry_consistency.py:45:from well_harness.controller_adapter import ControllerTruthMetadata  # noqa: E402
./tests/test_metadata_registry_consistency.py:56:    "well_harness.controller_adapter",
./tests/test_metadata_registry_consistency.py:57:    "well_harness.adapters.bleed_air_adapter",
./tests/test_metadata_registry_consistency.py:58:    "well_harness.adapters.efds_adapter",
./tests/test_metadata_registry_consistency.py:59:    "well_harness.adapters.landing_gear_adapter",
./tests/test_metadata_registry_consistency.py:60:    "well_harness.adapters.c919_etras_adapter",
./tests/fixtures/_validation_mismatch_schema.json:3:  "title": "well_harness.validation mismatch schema",
./tests/test_workbench_shell.py:10:from well_harness.demo_server import DemoRequestHandler
./tests/test_workbench_shell.py:14:STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
./tests/test_workbench_prompt_ticket_auth.py:6:from well_harness.collab.restricted_auth import RestrictedAuthError, validate_push_attempt
./tests/test_workbench_prompt_ticket_auth.py:7:from well_harness.workbench.prompting import publish_ticket, render_claude_code_prompt
./tests/test_workbench_prompt_ticket_auth.py:8:from well_harness.workbench.proposals import build_annotation_proposal
./tests/test_workbench_prompt_ticket_auth.py:32:        scope_files=["src/well_harness/workbench/**", "docs/workbench/**"],
./tests/test_workbench_prompt_ticket_auth.py:41:    assert "src/well_harness/workbench/**" in prompt
./tests/test_workbench_prompt_ticket_auth.py:48:        scope_files=["src/well_harness/workbench/**"],
./tests/test_workbench_prompt_ticket_auth.py:67:        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
./tests/test_workbench_prompt_ticket_auth.py:73:        changed_files=["src/well_harness/workbench/prompting.py", "docs/workbench/HANDOVER.md"],
./tests/test_workbench_prompt_ticket_auth.py:78:        validate_push_attempt(ticket, engineer="other-agent", changed_files=["src/well_harness/workbench/prompting.py"])
./tests/test_workbench_prompt_ticket_auth.py:81:        validate_push_attempt(ticket, engineer="claude-code", changed_files=["src/well_harness/controller.py"])
./tests/test_document_intake.py:7:from well_harness.cli import main
./tests/test_document_intake.py:8:from well_harness.document_intake import (
./tests/test_document_intake.py:233:        self.assertEqual(payload["source_of_truth"], "src/well_harness/controller.py")
./README.md:19:- a deterministic demo layer (`well_harness demo`) for controlled live reasoning — not a full AI system
./README.md:26:- `src/well_harness/models.py`
./README.md:28:- `src/well_harness/controller.py`
./README.md:30:- `src/well_harness/switches.py`
./README.md:32:- `src/well_harness/plant.py`
./README.md:34:- `src/well_harness/scenarios.py`
./README.md:36:- `src/well_harness/runner.py`
./README.md:38:- `src/well_harness/cli.py`
./README.md:40:- `src/well_harness/demo.py`
./README.md:42:- `src/well_harness/demo_server.py`
./README.md:50:PYTHONPATH=src python3 -m well_harness run nominal-deploy
./README.md:56:PYTHONPATH=src python3 -m well_harness run retract-reset
./README.md:62:PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --full
./README.md:68:PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --full
./README.md:74:PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json
./README.md:80:PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json
./README.md:88:    "name": "well_harness.debug",
./README.md:99:PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8
./README.md:107:PYTHONPATH=src python3 -m well_harness demo "触发 SW1 会发生什么"
./README.md:108:PYTHONPATH=src python3 -m well_harness demo "触发 logic3 会发生什么"
./README.md:109:PYTHONPATH=src python3 -m well_harness demo "触发 VDT90 会发生什么"
./README.md:110:PYTHONPATH=src python3 -m well_harness demo "触发 THR_LOCK 会发生什么"
./README.md:111:PYTHONPATH=src python3 -m well_harness demo "为什么 SW1 还没触发"
./README.md:112:PYTHONPATH=src python3 -m well_harness demo "为什么 SW2 还没触发"
./README.md:113:PYTHONPATH=src python3 -m well_harness demo "为什么 TLS115 还没触发"
./README.md:114:PYTHONPATH=src python3 -m well_harness demo "为什么 logic1 还没满足"
./README.md:115:PYTHONPATH=src python3 -m well_harness demo "为什么 logic2 还没满足"
./README.md:116:PYTHONPATH=src python3 -m well_harness demo "为什么 logic3 还没满足"
./README.md:117:PYTHONPATH=src python3 -m well_harness demo "为什么 logic4 还没满足"
./README.md:118:PYTHONPATH=src python3 -m well_harness demo "logic4 和 throttle lock 有什么关系"
./README.md:119:PYTHONPATH=src python3 -m well_harness demo --format json "logic4 和 throttle lock 有什么关系"
./README.md:120:PYTHONPATH=src python3 -m well_harness demo "为什么 TLS unlocked 还没触发"
./README.md:121:PYTHONPATH=src python3 -m well_harness demo "为什么 540V 还没触发"
./README.md:122:PYTHONPATH=src python3 -m well_harness demo "为什么 VDT90 还没触发"
./README.md:123:PYTHONPATH=src python3 -m well_harness demo "为什么 THR_LOCK 还没释放"
./README.md:124:PYTHONPATH=src python3 -m well_harness demo "为什么 throttle lock 没释放"
./README.md:125:PYTHONPATH=src python3 -m well_harness demo "如果把 logic3 的 TRA 阈值从 -11.74 改成 -8，会发生什么"
./README.md:131:Use `well_harness demo --format json "..."` when automation needs the same `DemoAnswer` fields as arrays; default `demo "..."` output remains the human-readable text format.
./README.md:136:For a non-unittest entrypoint to the same demo answer schema check, run `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`; it reuses `tests/fixtures/demo_json_output_asset_v1.json` and real `well_harness demo --format json` payloads, and prints a clear `SKIP` with a successful exit if `jsonschema` is unavailable.
./README.md:142:PYTHONPATH=src python3 -m well_harness.demo_server
./README.md:145:Open the printed local URL to use the first-screen demo UI. The UI posts prompts to `POST /api/demo`, reuses the same deterministic `DemoAnswer` payload as `well_harness demo --format json`, highlights the fixed control chain, and keeps a raw JSON debug panel visible. It is a local UI shell for the controlled demo layer, not a full natural-language AI product or complete physical simulation.
./README.md:146:If you want the server to ask the standard-library browser launcher to open the URL after startup, run `PYTHONPATH=src python3 -m well_harness.demo_server --open`; this is only a launch convenience, not browser E2E automation.
./README.md:312:- A formal JSON Schema reference lives at `docs/json_schema/well_harness_debug_v1.schema.json`. It documents the shared `well_harness.debug` v1 envelope, the top-level `timeline`, `events`, `explain`, and `diagnose` payload shapes, and key nested trace / explain / diagnosis objects for external integration.
./README.md:324:- Optional offline JSON Schema validation is available through both `tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_contract_payloads_when_installed` and `tools/validate_debug_json_schema.py`. Both entrypoints validate the same `timeline`, `events`, `explain`, and `diagnose` fixture commands against `docs/json_schema/well_harness_debug_v1.schema.json`. The optional `jsonschema` package is only needed when you explicitly run these validation entrypoints.
./README.md:325:- When changing `schema.schema_version`, update `docs/json_schema/well_harness_debug_v1.schema.json`, all affected `tests/fixtures/*_contract_v1.json` files, and the contract helper in `tests/test_cli.py` in the same change so schema drift is caught by CI.
./src/well_harness/timeline_engine/executors/c919_etras.py:18:from well_harness.adapters.c919_etras_frozen_v1 import (
./src/well_harness/timeline_engine/executors/c919_etras.py:25:from well_harness.timeline_engine.executors.base import ExecutorTickResult
./src/well_harness/scenarios.py:3:from well_harness.models import PilotFrame, Scenario
./AGENTS.md:10:- `src/well_harness/controller.py` is the only confirmed control truth for the reference thrust-reverser system.
./AGENTS.md:11:- `src/well_harness/runner.py` / `SimulationRunner` remains the runtime driver for simulation-style execution.
./AGENTS.md:22:- Controller truth: `src/well_harness/controller.py`
./AGENTS.md:23:- Runtime driver: `src/well_harness/runner.py`
./AGENTS.md:24:- Adapters: `src/well_harness/controller_adapter.py` and `src/well_harness/adapters/`
./AGENTS.md:25:- Models: `src/well_harness/models.py`
./AGENTS.md:26:- Playback/diagnosis/knowledge: `src/well_harness/scenario_playback.py`, `src/well_harness/fault_diagnosis.py`, `src/well_harness/knowledge_capture.py`
./AGENTS.md:27:- Browser/UI surfaces: `src/well_harness/demo_server.py`, `src/well_harness/static/`
./src/well_harness/timeline_engine/executors/__init__.py:3:from well_harness.timeline_engine.executors.base import Executor, ExecutorTickResult
./src/well_harness/tools/specs/reference_thrust_reverser.spec.json:641:  "source_of_truth": "src/well_harness/controller.py",
./src/well_harness/hardware_schema.py:2:Hardware schema loader for well_harness.
./src/well_harness/hardware_schema.py:134:    well_harness package is at <repo-root>/src/well_harness/, so we need
./src/well_harness/hardware_schema.py:138:        import well_harness
./src/well_harness/hardware_schema.py:140:        pkg_root = Path(well_harness.__file__).parent
./src/well_harness/hardware_schema.py:141:        # <repo-root>/src/well_harness/ -> <repo-root>/src/ -> <repo-root>/
./src/well_harness/timeline_engine/executors/fantui.py:20:from well_harness.controller_adapter import build_reference_controller_adapter
./src/well_harness/timeline_engine/executors/fantui.py:21:from well_harness.models import ControllerOutputs, HarnessConfig, ResolvedInputs
./src/well_harness/timeline_engine/executors/fantui.py:22:from well_harness.plant import PlantState, SimplifiedDeployPlant
./src/well_harness/timeline_engine/executors/fantui.py:23:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./src/well_harness/timeline_engine/executors/fantui.py:24:from well_harness.timeline_engine.executors.base import ExecutorTickResult
./archive/shelved/llm-features/scripts/integrated_timing_rehearsal.py:185:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
./docs/c919_etras/traceability_matrix.md:3:Audit-grade mapping from the 甲方 requirement PDF (`uploads/20260417-C919反推控制逻辑需求文档.pdf`, 10 pages) to the executable truth adapter (`src/well_harness/adapters/c919_etras_adapter.py`) and the validation suite (`tests/test_c919_etras_adapter.py`).
./docs/c919_etras/traceability_matrix.md:8:2. **Adapter anchor** — file + line number in `src/well_harness/adapters/c919_etras_adapter.py` (LOC references are rechecked in each P34-05 closure).
./docs/c919_etras/traceability_matrix.md:101:`_select_mlg_wow(lgcu1_value, lgcu1_valid, lgcu2_value, lgcu2_valid)` lives at `src/well_harness/adapters/c919_etras_adapter.py:195` and implements PDF 表2 with a safety-conservative tie-break policy (disagree → FALSE; both invalid → FALSE).
./docs/c919_etras/traceability_matrix.md:143:All three items are tracked in the intake packet's `source_documents` field via `c919-etras-requirement-pdf-001` notes (see `src/well_harness/adapters/c919_etras_intake_packet.py:58`) so the downstream knowledge-capture / diagnosis pipeline surfaces them as explicit assumptions rather than silent defaults.
./docs/c919_etras/traceability_matrix.md:153:| Adversarial 8/8 | `WELL_HARNESS_PORT=8799 python src/well_harness/static/adversarial_test.py` (via `archive/shelved/llm-features/tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes`) | 8/8 ALL TESTS PASSED | Wraps the adversarial script under live `demo_server` on :8799 |
./docs/panels/sim_panel_requirements.md:7:**后端实现**: `src/well_harness/demo_server.py::monitor_timeline_payload`
./src/well_harness/runner.py:3:from well_harness.controller_adapter import ControllerTruthAdapter, build_reference_controller_adapter
./src/well_harness/runner.py:4:from well_harness.models import (
./src/well_harness/runner.py:12:from well_harness.plant import PlantState, SimplifiedDeployPlant
./src/well_harness/runner.py:13:from well_harness.switches import LatchedThrottleSwitches, SwitchState
./src/well_harness/timeline_engine/player.py:23:from well_harness.timeline_engine.executors.base import Executor
./src/well_harness/timeline_engine/player.py:24:from well_harness.timeline_engine.fault_schedule import (
./src/well_harness/timeline_engine/player.py:28:from well_harness.timeline_engine.schema import (
./archive/shelved/llm-features/scripts/pitch_prewarm.py:145:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
./docs/panels/demo_panel_requirements.md:6:**真值源**: `src/well_harness/demo_server.py::lever_snapshot_payload`  
./docs/panels/demo_panel_requirements.md:7:**控制器**: `src/well_harness/controller.py::DeployController`
./src/well_harness/timeline_engine/validator.py:7:from well_harness.timeline_engine.schema import (
./docs/thrust_reverser/requirements_supplement.md:16:Well Harness 项目的 thrust-reverser 控制逻辑已在 `src/well_harness/controller.py::DeployController` + `src/well_harness/models.py::HarnessConfig` 中实现完备并经 535 LOC 测试覆盖。原 docx（2026-04-09 · 57 段 · 2 表 · 1 图）覆盖了其中 4 个核心工作逻辑的条件列表和 4 个阈值常数，但未覆盖以下 5 处硬件参数 + 1 处 authority 声明。
./docs/thrust_reverser/requirements_supplement.md:39:**`src/well_harness/system_spec.py::current_reference_workbench_spec()` 早已提供完整 thrust-reverser workbench spec**（含 ComponentSpec / LogicNodeSpec / AcceptanceScenarioSpec · 被 6 处引用：`cli.py` / `controller_adapter.py::ReferenceDeployControllerAdapter.load_spec()` / `tests/test_system_spec.py` / 等）。
./docs/thrust_reverser/requirements_supplement.md:73:`src/well_harness/models.py::HarnessConfig` 第 22-43 行的 SW2 触发窗口常数：
./docs/thrust_reverser/requirements_supplement.md:202:1. 先明确 fault taxonomy（参考 `src/well_harness/fault_taxonomy.py`）
./docs/thrust_reverser/requirements_supplement.md:261:| **真值基准** | `src/well_harness/controller.py` + `models.py` | 代码真值 · 唯一 ground truth | 改动需新 Phase + 三轨回归 |
./docs/thrust_reverser/requirements_supplement.md:264:| **Workbench spec (P41 discovered)** | `src/well_harness/system_spec.py::current_reference_workbench_spec()`（约 280 行）| 派生于 controller.py + HarnessConfig · ComponentSpec/LogicNodeSpec/AcceptanceScenarioSpec | 跟 code 同步 · 6 处 callers 依赖稳定 |
./docs/thrust_reverser/requirements_supplement.md:285:4. `src/well_harness/adapters/thrust_reverser_intake_packet.py`（4 SourceDocumentRef · 证迹挂链）
./docs/thrust_reverser/requirements_supplement.md:287:6. `src/well_harness/controller.py` + `models.py`（最终真值 · 代码即 law）
./docs/thrust_reverser/requirements_supplement.md:310:**Sync with code:** 本 supplement 任何数值变更必须与 `src/well_harness/models.py::HarnessConfig` 同 commit 原子更新
./archive/shelved/llm-features/scripts/local_model_smoke.py:101:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(SERVER_PORT)],
./docs/onboarding/README.md:103:**Reference:** See `src/well_harness/adapters/landing_gear_adapter.py` for a complete worked example (function `build_landing_gear_workbench_spec()`).
./docs/onboarding/README.md:141:**Reference implementation:** `src/well_harness/adapters/landing_gear_adapter.py` — `LandingGearControllerAdapter` class.
./docs/onboarding/README.md:153:Create a file `src/well_harness/adapters/<your_system>_intake_packet.py` that builds a `ControlSystemIntakePacket`.
./docs/onboarding/README.md:155:**Reference:** `src/well_harness/adapters/landing_gear_intake_packet.py`
./docs/onboarding/README.md:158:from well_harness.document_intake import (
./docs/onboarding/README.md:163:from well_harness.system_spec import workbench_spec_from_dict
./docs/onboarding/README.md:174:            location="src/well_harness/adapters/your_adapter.py",
./docs/onboarding/README.md:225:from well_harness.adapters.your_system_intake_packet import build_your_system_intake_packet
./docs/onboarding/README.md:226:from well_harness.document_intake import intake_packet_to_workbench_spec
./docs/onboarding/README.md:227:from well_harness.scenario_playback import build_playback_report_from_intake_packet
./docs/onboarding/README.md:228:from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
./docs/onboarding/README.md:229:from well_harness.knowledge_capture import build_knowledge_artifact
./docs/onboarding/README.md:230:from well_harness.system_spec import workbench_spec_to_dict
./docs/onboarding/README.md:312:- `onboarding_questions` must be an array; use `default_workbench_clarification_questions()` from `well_harness.system_spec` to populate it
./docs/onboarding/README.md:334:**Fix:** Provide non-empty `clarification_answers` for all required onboarding questions, or use the `assess_intake_packet()` function from `well_harness.document_intake` to identify which questions are unanswered.
./docs/onboarding/README.md:341:src/well_harness/
./tests/fixtures/p43_spike/real_pdf_happy_path/README.md:14:- `intake_minimal_ready.json` — minimal compliant intake packet referencing real C919 ETRAS pdf via metadata; uses stable clarification question_ids (`source_documents`, `component_state_domains`, `timeline_rules`, `fault_taxonomy`) per `default_workbench_clarification_questions()` at `src/well_harness/system_spec.py:244`.
./src/well_harness/timeline_engine/fault_schedule.py:17:from well_harness.timeline_engine.schema import FaultScheduleEntry, Timeline
./docs/json_schema/validation_report_v1.schema.json:4:  "title": "well_harness validation report v1",
./docs/json_schema/validation_report_v1.schema.json:8:    "schema_name": "well_harness.validation_report",
./archive/shelved/llm-features/scripts/demo_rehearsal_dual_backend.py:93:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:28:| Adapter file | `src/well_harness/adapters/bleed_air_adapter.py` |
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:29:| Intake packet | `src/well_harness/adapters/bleed_air_intake_packet.py` |
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:43:6. `src/well_harness/adapters/landing_gear_adapter.py` (lines 1-80, full file) — the reference implementation
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:44:7. `src/well_harness/models.py` — confirmed `ControlSystemIntakePacket` lives in `document_intake.py`
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:63:  --spec-file src/well_harness/adapters/bleed_air_adapter.py \
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:174:- `src/well_harness/adapters/bleed_air_adapter.py` — 380 lines
./docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md:175:- `src/well_harness/adapters/bleed_air_intake_packet.py` — 53 lines
./src/well_harness/timeline_engine/__init__.py:16:from well_harness.timeline_engine.schema import (
./src/well_harness/timeline_engine/__init__.py:25:from well_harness.timeline_engine.fault_schedule import ActiveFaultSet, compile_active_faults
./src/well_harness/timeline_engine/__init__.py:26:from well_harness.timeline_engine.validator import ValidationError, parse_timeline
./src/well_harness/timeline_engine/__init__.py:27:from well_harness.timeline_engine.player import TimelinePlayer
./src/well_harness/timeline_engine/__init__.py:28:from well_harness.timeline_engine.executors.base import Executor, ExecutorTickResult
./docs/co-development/security-review-template.md:23:| 1 | 是否改动 `src/well_harness/controller.py`？ | R1 | 未改 / 有独立 Opus 4.6 架构审查记录 | PR 直接修改门函数但无审查 |
./docs/co-development/security-review-template.md:38:当前对抗测试（`src/well_harness/static/adversarial_test.py`）覆盖 8 个场景：
./src/well_harness/adapters/landing_gear_intake_packet.py:14:from well_harness.adapters.landing_gear_adapter import build_landing_gear_workbench_spec
./src/well_harness/adapters/landing_gear_intake_packet.py:15:from well_harness.document_intake import (
./src/well_harness/adapters/landing_gear_intake_packet.py:20:from well_harness.system_spec import workbench_spec_from_dict
./src/well_harness/adapters/landing_gear_intake_packet.py:43:            location="src/well_harness/adapters/landing_gear_adapter.py",
./tests/fixtures/demo_json_output_asset_v1.json:2:  "name": "well_harness.demo_json_output.asset",
./tests/fixtures/demo_json_output_asset_v1.json:4:  "description": "Lightweight regression contract for well_harness demo --format json output. This is not a JSON Schema.",
./docs/thrust_reverser/traceability_matrix.md:12:- **代码真值** `src/well_harness/controller.py`（`DeployController` class · 4 logic groups）+ `src/well_harness/models.py`（`HarnessConfig` · 13 常数）—— 作为 truth source
./docs/thrust_reverser/traceability_matrix.md:225:- 本 matrix 一旦更新 row（阈值值改动 / 新增常数 / docx 升级 v2），必须同 commit 原子更新 `config/hardware/thrust_reverser_hardware_v1.yaml` 头 + `src/well_harness/adapters/thrust_reverser_intake_packet.py` notes + `docs/provenance/adapter_truth_levels.md` row 1
./src/well_harness/adapters/c919_etras_adapter.py:72:from well_harness.controller_adapter import (
./src/well_harness/adapters/c919_etras_adapter.py:76:from well_harness.system_spec import (
./src/well_harness/adapters/c919_etras_adapter.py:94:C919_ETRAS_SOURCE_OF_TRUTH = "src/well_harness/adapters/c919_etras_adapter.py"
./src/well_harness/tools/generate_svg.py:9:    python -m well_harness.tools.generate_svg path/to/spec.json -o output.svg.html
./tests/fixtures/explain_contract_v1.json:2:  "contract_name": "well_harness.explain.v1",
./tests/fixtures/explain_contract_v1.json:16:    "name": "well_harness.debug",
./docs/json_schema/knowledge_artifact_v1.schema.json:4:  "title": "well_harness.knowledge_artifact v1 JSON payload",
./src/well_harness/adapters/bleed_air_adapter.py:23:from well_harness.controller_adapter import (
./src/well_harness/adapters/bleed_air_adapter.py:28:from well_harness.system_spec import (
./src/well_harness/adapters/bleed_air_adapter.py:46:BLEED_AIR_SOURCE_OF_TRUTH = "src/well_harness/adapters/bleed_air_adapter.py"
./tests/fixtures/validation_schema_runner_report_asset_v1.json:2:  "asset_name": "well_harness.validation_schema_runner_report.v1",
./docs/co-development/api-contract.md:175:完整列表见 `src/well_harness/demo_server.py` 文件头部的 `*_PATH` 常量。
./docs/unfreeze/P17-application-draft.md:249:  - `src/well_harness/static/adversarial_test.py`（R5 adversarial 8/8 守门）
./tests/fixtures/_validation_fail_invalid_logic_contract.json:2:  "contract_name": "well_harness.validation.fail_invalid_logic_choice",
./tests/fixtures/_validation_fail_invalid_logic_contract.json:16:    "name": "well_harness.debug",
./src/well_harness/adapters/bleed_air_intake_packet.py:8:    from well_harness.adapters.bleed_air_intake_packet import build_bleed_air_intake_packet
./src/well_harness/adapters/bleed_air_intake_packet.py:19:from well_harness.adapters.bleed_air_adapter import (
./src/well_harness/adapters/bleed_air_intake_packet.py:23:from well_harness.document_intake import (
./src/well_harness/adapters/bleed_air_intake_packet.py:28:from well_harness.system_spec import workbench_spec_from_dict
./src/well_harness/adapters/bleed_air_intake_packet.py:50:            location="src/well_harness/adapters/bleed_air_adapter.py",
./docs/co-development/sla-draft.md:89:adapter 切换成本：加一个 `*Client` 类 + 在 `_BACKENDS` dict 注册，预估 <50 行代码（见 `src/well_harness/llm_client.py`）。
./docs/coordination/archive/plan-history.md:33:PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770 --open
./docs/coordination/archive/plan-history.md:52:- `/api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 保持不变。
./docs/coordination/archive/plan-history.md:61:- 不改 `SimulationRunner`、`well_harness demo`、`POST /api/demo`、`well_harness run`。
./tests/fixtures/_validation_fail_unclassified_contract.json:2:  "contract_name": "well_harness.validation.fail_unclassified",
./tests/fixtures/_validation_fail_unclassified_contract.json:12:    "name": "well_harness.debug",
./src/well_harness/adapters/landing_gear_adapter.py:22:from well_harness.controller_adapter import ControllerTruthMetadata, GenericTruthEvaluation
./src/well_harness/adapters/landing_gear_adapter.py:23:from well_harness.system_spec import (
./src/well_harness/adapters/landing_gear_adapter.py:39:LANDING_GEAR_SOURCE_OF_TRUTH = "src/well_harness/adapters/landing_gear_adapter.py"
./tests/fixtures/diagnose_contract_v1.json:2:  "contract_name": "well_harness.diagnose.v1",
./tests/fixtures/diagnose_contract_v1.json:14:    "name": "well_harness.debug",
./docs/P43-workflow-automaton.yaml:287:      owner: "src/well_harness/static/workbench.js"
./docs/P43-workflow-automaton.yaml:292:      owner: "src/well_harness/workbench_bundle.py"
./src/well_harness/adapters/c919_etras_intake_packet.py:9:    from well_harness.adapters.c919_etras_intake_packet import (
./src/well_harness/adapters/c919_etras_intake_packet.py:16:from well_harness.adapters.c919_etras_adapter import (
./src/well_harness/adapters/c919_etras_intake_packet.py:20:from well_harness.document_intake import (
./src/well_harness/adapters/c919_etras_intake_packet.py:24:from well_harness.system_spec import workbench_spec_from_dict
./src/well_harness/adapters/c919_etras_intake_packet.py:48:            location="src/well_harness/adapters/c919_etras_adapter.py",
./tests/fixtures/_validation_fail_invalid_scenario_contract.json:2:  "contract_name": "well_harness.validation.fail_invalid_scenario_choice",
./tests/fixtures/_validation_fail_invalid_scenario_contract.json:10:    "name": "well_harness.debug",
./docs/coordination/archive/dev-handoff-history.md:78:- `well_harness demo`
./docs/coordination/archive/dev-handoff-history.md:79:- `well_harness demo --format json`
./docs/coordination/archive/dev-handoff-history.md:80:- `well_harness run`
./docs/coordination/archive/dev-handoff-history.md:85:PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8770 --open
./docs/coordination/archive/dev-handoff-history.md:229:PYTHONPATH=src python3 -m well_harness.demo_server --open
./docs/coordination/archive/dev-handoff-history.md:235:PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8767
./docs/coordination/archive/dev-handoff-history.md:271:- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、旧形态 `POST /api/lever-snapshot` 或 `well_harness run`。
./docs/coordination/archive/dev-handoff-history.md:301:- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
./docs/coordination/archive/dev-handoff-history.md:388:- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、旧形态 `POST /api/lever-snapshot` 或 `well_harness run`。
./docs/coordination/archive/dev-handoff-history.md:441:PYTHONPATH=src python3 -m well_harness.demo_server --open
./docs/coordination/archive/dev-handoff-history.md:447:PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8767
./docs/coordination/archive/dev-handoff-history.md:477:- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、`POST /api/lever-snapshot` 或 `well_harness run`。
./docs/coordination/archive/dev-handoff-history.md:503:- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
./docs/coordination/archive/dev-handoff-history.md:514:PYTHONPATH=src python3 -m well_harness.demo_server --open
./docs/coordination/archive/dev-handoff-history.md:520:PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766
./docs/coordination/archive/dev-handoff-history.md:549:- 不破坏 `well_harness demo`、`well_harness demo --format json`、`POST /api/demo`、`POST /api/lever-snapshot` 或 `well_harness run`。
./docs/coordination/archive/dev-handoff-history.md:574:- 现有 `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
./docs/coordination/archive/dev-handoff-history.md:591:- Endpoint 位于 `src/well_harness/demo_server.py`。
./docs/coordination/archive/dev-handoff-history.md:693:- 不破坏现有 `well_harness demo`。
./docs/coordination/archive/dev-handoff-history.md:694:- 不破坏现有 `well_harness demo --format json`。
./docs/coordination/archive/dev-handoff-history.md:696:- 不破坏现有 `well_harness run`。
./docs/coordination/archive/dev-handoff-history.md:759:- plant 简化假设已在 `README.md` 的 Modeling Notes 和 `src/well_harness/plant.py` 对应位置显式标注。
./docs/coordination/archive/dev-handoff-history.md:761:- 未修改 `controller.py`、`SimulationRunner`、`scenarios.py`、`well_harness.cli run`、demo text / JSON 输出、`POST /api/demo` payload 或 `DemoAnswer` shape。
./docs/coordination/archive/dev-handoff-history.md:770:- `src/well_harness/plant.py`：
./docs/coordination/archive/dev-handoff-history.md:787:- `PYTHONPATH=src python3 -m py_compile src/well_harness/plant.py src/well_harness/controller.py src/well_harness/runner.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:818:- 不改变 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:819:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:834:- 如有帮助，在 `src/well_harness/plant.py` 对应位置加简短注释，说明这些是 simplified plant feedback assumptions，不是 controller confirmed truth。
./docs/coordination/archive/dev-handoff-history.md:885:- `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:889:- `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:915:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:916:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:949:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:951:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:985:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:986:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1025:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:1049:- 未修改 `controller.py`、`SimulationRunner`、`well_harness.cli run`。
./docs/coordination/archive/dev-handoff-history.md:1050:- 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1057:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1060:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1061:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1062:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1104:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1106:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:1147:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1148:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1207:- 未修改 `controller.py`、`SimulationRunner`、`well_harness.cli run`。
./docs/coordination/archive/dev-handoff-history.md:1208:- 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1219:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1222:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1223:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1224:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1241:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:1242:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1264:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1266:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:1289:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1290:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1333:  - `src/well_harness/demo_server.py`
./docs/coordination/archive/dev-handoff-history.md:1334:  - `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:1335:  - `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:1336:  - `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:1339:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:1379:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1382:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1383:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1384:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:1403:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:1404:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1426:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/dev-handoff-history.md:1470:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1471:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1519:  - 默认 `PYTHONPATH=src python3 -m well_harness.demo_server --open` 因本机 `127.0.0.1:8000` 已有 Python 进程占用而失败。
./docs/coordination/archive/dev-handoff-history.md:1520:  - 改用 `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766 --open` 继续检查，不改变默认 server 行为。
./docs/coordination/archive/dev-handoff-history.md:1521:- `src/well_harness/static/demo.html`：
./docs/coordination/archive/dev-handoff-history.md:1525:- `src/well_harness/static/demo.css`：
./docs/coordination/archive/dev-handoff-history.md:1549:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1563:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8765`
./docs/coordination/archive/dev-handoff-history.md:1574:  - `src/well_harness/static/demo.css` 压缩 showcase 内 chain panel 的节点尺寸、header 间距和 highlight explanation 间距，让 `logic4 / THR_LOCK` 末端节点在桌面首屏更稳定可见。
./docs/coordination/archive/dev-handoff-history.md:1593:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1596:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1597:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1598:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:1599:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:1600:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:1610:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:1626:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:1627:  - 可选启动便利：`PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1639:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，做一次真实浏览器视觉 hand-check，并只修正阻碍 Demo UI 展示的首屏可读性问题。
./docs/coordination/archive/dev-handoff-history.md:1644:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1680:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1681:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1721:- 在 `src/well_harness/static/demo.html` 新增 `showcase-mission`、`showcase-surface`、`showcase-intro`、`showcase-grid`，把 prompt、fixed control chain、structured answer 主干组合成第一屏 demo-ready surface。
./docs/coordination/archive/dev-handoff-history.md:1727:- `src/well_harness/static/demo.css` 新增 showcase layout：
./docs/coordination/archive/dev-handoff-history.md:1742:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1743:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:1745:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1746:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1747:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:1748:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:1749:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:1761:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:1776:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:1777:  - 可选启动便利：`PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/dev-handoff-history.md:1785:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，对本地 UI 做一次 demo-ready showcase surface pass。
./docs/coordination/archive/dev-handoff-history.md:1789:让浏览器打开 `PYTHONPATH=src python3 -m well_harness.demo_server --open` 后，第一屏就是一个可展示的 Demo UI：
./docs/coordination/archive/dev-handoff-history.md:1799:- 优先改 `src/well_harness/static/demo.html` 与 `src/well_harness/static/demo.css`。
./docs/coordination/archive/dev-handoff-history.md:1843:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1844:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:1884:- 在 `src/well_harness/demo_server.py` 新增可选 `--open` 参数。
./docs/coordination/archive/dev-handoff-history.md:1905:  - `well_harness.demo_server --help` 中 `--open` 文案。
./docs/coordination/archive/dev-handoff-history.md:1912:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:1913:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:1917:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1918:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:1919:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:1920:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:1921:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:1932:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:1947:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:1953:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为 `well_harness.demo_server` 增加一个可选的浏览器打开 affordance。
./docs/coordination/archive/dev-handoff-history.md:1957:- 在 `src/well_harness/demo_server.py` 增加可选参数：
./docs/coordination/archive/dev-handoff-history.md:1973:  - 如想自动打开浏览器，可用 `PYTHONPATH=src python3 -m well_harness.demo_server --open`。
./docs/coordination/archive/dev-handoff-history.md:1994:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:1995:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2001:1. `PYTHONPATH=src python3 -m well_harness.demo_server` 默认行为保持不变。
./docs/coordination/archive/dev-handoff-history.md:2002:2. `PYTHONPATH=src python3 -m well_harness.demo_server --open` 会使用标准库尝试打开本地 UI URL。
./docs/coordination/archive/dev-handoff-history.md:2036:- 在 `src/well_harness/static/demo.css` 中对 compact `answer-guide` 增加窄屏 spacing polish：
./docs/coordination/archive/dev-handoff-history.md:2064:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:2066:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2067:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2068:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:2069:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:2070:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2081:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2096:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2102:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，优化本地 UI 中 compact `answer-guide` 在移动端 / 窄屏下的 spacing、可读性和触控扫读体验。
./docs/coordination/archive/dev-handoff-history.md:2138:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2139:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2181:- 在 `src/well_harness/static/demo.html` 的 `Structured output` 区域新增 `answer-guide` wrapper，把 `Audience answer-field legend` 与 `Answer sections` summary 组合成同一个 compact answer guide。
./docs/coordination/archive/dev-handoff-history.md:2182:- 在 `src/well_harness/static/demo.css` 新增 `answer-guide`、`answer-guide-intro`、`answer-guide-grid` 布局样式：
./docs/coordination/archive/dev-handoff-history.md:2201:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:2204:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2205:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2206:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:2207:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:2208:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2219:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2234:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2240:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，优化本地 UI 中 `Audience answer-field legend` 与 `Answer sections` summary 的视觉关系，形成轻量 compact answer guide layout。
./docs/coordination/archive/dev-handoff-history.md:2275:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2276:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2316:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:2334:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:2359:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:2362:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2363:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2364:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2365:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2366:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2375:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2392:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2402:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 audience-facing answer-field legend。
./docs/coordination/archive/dev-handoff-history.md:2440:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2441:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2482:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:2492:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:2519:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:2522:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2523:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2524:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2525:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:2526:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2535:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2552:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2568:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一个 screenshot-free presenter route strip，帮助演示者按页面区域顺序走查。
./docs/coordination/archive/dev-handoff-history.md:2602:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2603:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2646:  - 覆盖启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:2668:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:2674:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2675:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2676:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:2677:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:2678:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2688:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2705:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2720:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 presenter readiness run card。
./docs/coordination/archive/dev-handoff-history.md:2728:  - 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2756:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2757:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2799:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:2808:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:2829:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:2835:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2836:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2837:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:2838:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:2839:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2849:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:2866:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:2875:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加轻量 presenter callout labels，让页面与 `docs/demo_presenter_talk_track.md` 的讲解点更容易对应。
./docs/coordination/archive/dev-handoff-history.md:2907:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:2908:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:2979:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:2980:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2981:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:2982:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:2983:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:2984:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:2994:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3009:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:3018:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一页式 presenter talk track。
./docs/coordination/archive/dev-handoff-history.md:3056:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:3057:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:3128:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:3129:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3130:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3131:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:3132:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:3133:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3143:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3158:  - `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:3167:在不改变 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo 增加一个轻量 concise presenter walkthrough。
./docs/coordination/archive/dev-handoff-history.md:3198:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:3199:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:3283:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:3284:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3285:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3286:- `python3 -m json.tool /tmp/well_harness_round66_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3287:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:3288:- `python3 -m json.tool /tmp/well_harness_round66_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3289:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:3290:- `python3 -m json.tool /tmp/well_harness_round66_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3291:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3301:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3322:  - 输出本地 UI 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:3365:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3366:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3367:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/dev-handoff-history.md:3368:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/dev-handoff-history.md:3369:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:3370:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3371:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/dev-handoff-history.md:3381:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3399:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3403:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3406:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3431:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3433:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round64_demo_bridge.txt`
./docs/coordination/archive/dev-handoff-history.md:3434:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round64_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3435:- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round64_demo_logic3.json`
./docs/coordination/archive/dev-handoff-history.md:3436:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round64_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3437:- `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round64_demo_server_help.txt`
./docs/coordination/archive/dev-handoff-history.md:3438:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round64_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3439:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round64_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3440:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round64_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3441:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round64_retract_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3451:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3469:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3480:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3496:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3498:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round63_demo_bridge.txt`
./docs/coordination/archive/dev-handoff-history.md:3499:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round63_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3500:- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round63_demo_logic3.json`
./docs/coordination/archive/dev-handoff-history.md:3501:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round63_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3502:- `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round63_demo_server_help.txt`
./docs/coordination/archive/dev-handoff-history.md:3503:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round63_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3504:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round63_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3505:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round63_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3506:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round63_retract_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3516:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3534:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3539:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3543:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3560:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3563:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3564:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round62_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3565:- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round62_demo_logic3.json`
./docs/coordination/archive/dev-handoff-history.md:3566:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round62_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3567:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round62_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3568:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round62_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3569:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round62_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3570:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round62_retract_events.txt`
./docs/coordination/archive/dev-handoff-history.md:3571:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:3581:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3599:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3604:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3607:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3627:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3630:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3631:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round61_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3632:- `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round61_demo_logic3.json`
./docs/coordination/archive/dev-handoff-history.md:3633:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round61_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3634:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round61_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3635:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round61_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3636:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:3637:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3638:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:3648:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3664:- 本地 UI shell 已存在，启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:3671:在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加一个轻量 answer-to-chain highlight explanation。
./docs/coordination/archive/dev-handoff-history.md:3697:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:3698:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:3736:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3746:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3750:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3764:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3767:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3768:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round60_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3769:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round60_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3770:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round60_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3771:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round60_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3772:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:3773:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3774:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:3784:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3801:  - `src/well_harness/demo_server.py`
./docs/coordination/archive/dev-handoff-history.md:3802:  - `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3803:  - `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3804:  - `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3805:- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:3812:在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加 sample prompt 分组、键盘提交 affordance 和更清楚的受控 demo 帮助文案。
./docs/coordination/archive/dev-handoff-history.md:3857:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:3858:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:3905:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3911:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3920:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3934:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:3937:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:3938:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round59_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:3939:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round59_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:3940:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round59_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:3941:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round59_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:3942:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:3943:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:3946:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:3954:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:3971:  - `src/well_harness/demo_server.py`
./docs/coordination/archive/dev-handoff-history.md:3972:  - `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:3973:  - `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:3974:  - `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:3975:- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:3982:在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加 selected prompt 状态、移动端链路展示优化和 raw JSON 折叠能力。
./docs/coordination/archive/dev-handoff-history.md:4007:- 折叠功能不要改变 `well_harness demo --format json` payload。
./docs/coordination/archive/dev-handoff-history.md:4022:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:4023:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:4070:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:4078:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:4083:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:4103:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:4106:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:4107:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round58_demo_bridge.json`
./docs/coordination/archive/dev-handoff-history.md:4108:- `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round58_demo_diagnose.json`
./docs/coordination/archive/dev-handoff-history.md:4109:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round58_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:4110:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round58_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:4111:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:4112:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:4115:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:4123:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:4140:  - `src/well_harness/demo_server.py`
./docs/coordination/archive/dev-handoff-history.md:4141:  - `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:4142:  - `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:4143:  - `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:4144:- 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:4146:- 默认 `well_harness demo` text / JSON 输出、`run` CLI 和既有 harness JSON 输出保持不变。
./docs/coordination/archive/dev-handoff-history.md:4150:在不改变现有 deploy 控制逻辑语义、仿真行为、现有 `run` CLI 行为、现有 harness JSON 输出形状、现有 `well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下，为本地 UI demo shell 增加最小交互状态 polish 和更细的控制链路高亮。
./docs/coordination/archive/dev-handoff-history.md:4193:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:4194:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:4239:- 新增 `src/well_harness/demo_server.py`。
./docs/coordination/archive/dev-handoff-history.md:4241:  - 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/dev-handoff-history.md:4247:  - `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:4248:  - `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:4249:  - `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:4270:  - 补充 `PYTHONPATH=src python3 -m well_harness.demo_server` 本地 UI 启动方式和边界说明。
./docs/coordination/archive/dev-handoff-history.md:4274:- `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/dev-handoff-history.md:4277:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:4278:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:4279:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round57_nominal.json`
./docs/coordination/archive/dev-handoff-history.md:4280:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round57_diagnose_logic4.json`
./docs/coordination/archive/dev-handoff-history.md:4281:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/dev-handoff-history.md:4282:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 4.9`
./docs/coordination/archive/dev-handoff-history.md:4283:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:4285:- `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/dev-handoff-history.md:4292:- 默认 `well_harness demo "..."` 文本输出保持不变。
./docs/coordination/archive/dev-handoff-history.md:4293:- `well_harness demo --format json "..."` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:4309:- `well_harness demo "..."` 与 `well_harness demo --format json "..."` 已可用。
./docs/coordination/archive/dev-handoff-history.md:4316:新增一个最小本地 UI，用来展示现有 `well_harness demo --format json` reasoning layer。
./docs/coordination/archive/dev-handoff-history.md:4318:要求在不改变现有 deploy 控制逻辑语义、仿真行为、`run` CLI 行为、harness JSON 输出形状、`well_harness demo` text / JSON 输出语义，且不新增运行时依赖的前提下完成。
./docs/coordination/archive/dev-handoff-history.md:4324:- `src/well_harness/demo_server.py`
./docs/coordination/archive/dev-handoff-history.md:4325:- `src/well_harness/static/demo.html`
./docs/coordination/archive/dev-handoff-history.md:4326:- `src/well_harness/static/demo.css`
./docs/coordination/archive/dev-handoff-history.md:4327:- `src/well_harness/static/demo.js`
./docs/coordination/archive/dev-handoff-history.md:4331:- `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/coordination/archive/dev-handoff-history.md:4332:- 如实现成本很低，可同时新增 `well_harness ui`，但不能影响 `run` / `demo` 子命令。
./docs/coordination/archive/dev-handoff-history.md:4338:- API 直接复用 `answer_demo_prompt(...)` 与 `demo_answer_to_payload(...)`，或等价地走现有 `well_harness demo --format json` 逻辑。
./docs/coordination/archive/dev-handoff-history.md:4376:- 不改 `well_harness.cli run` 默认行为。
./docs/coordination/archive/dev-handoff-history.md:4377:- 不改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/dev-handoff-history.md:4452:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:4453:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:4454:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:4455:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:4456:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/dev-handoff-history.md:4471:- `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/dev-handoff-history.md:4493:  - 通过真实 `well_harness demo --format json` 路径校验三条 payload：
./docs/coordination/archive/dev-handoff-history.md:4517:- `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/dev-handoff-history.md:4518:- `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/dev-handoff-history.md:4519:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json > /tmp/well_harness_round55_nominal_verify.json`
./docs/coordination/archive/dev-handoff-history.md:4520:- `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json > /tmp/well_harness_round55_logic4_diagnose_verify.json`
./docs/coordination/archive/dev-handoff-history.md:4521:- `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 > /tmp/well_harness_round55_retract_events.txt`
./docs/coordination/archive/dev-handoff-history.md:4551:- 未修改 `controller.py`、`SimulationRunner`、`well_harness demo`、`POST /api/demo` 或 `well_harness run`。
./tests/fixtures/validation_schema_checker_report_asset_v1.json:2:  "asset_name": "well_harness.validation_schema_checker_report.v1",
./tests/fixtures/timeline_contract_v1.json:2:  "contract_name": "well_harness.timeline.v1",
./tests/fixtures/timeline_contract_v1.json:10:    "name": "well_harness.debug",
./docs/P43-contract-proof-report.md:30:**What we fixed** (Step B · Kogami Option X expansion · 4 LOC surgical · 1 Codex review round): three critical Counter-F contract bugs in `src/well_harness/ai_doc_analyzer.py` that had silently broken the pipeline in production:
./docs/P43-contract-proof-report.md:74:- **P43-03 (document ingestion · pypdf + python-docx)**: fix Bug D (stable question_id contract in `_inject_clarification_answers` at `src/well_harness/ai_doc_analyzer.py:799`) together with the server-side extraction path decided in P43-00 Q12=B+a. Update ai-doc-analyzer's upload surface to submit the original binary to a new server endpoint, and remove the `readAsText` call entirely at `src/well_harness/static/ai-doc-analyzer.js:224`.
./docs/coordination/archive/qa-report-history.md:29:  - `well_harness demo --format json 'logic4 和 throttle lock 有什么关系'` 保持 `logic4_thr_lock_bridge / logic4->thr_lock / logic4`。
./docs/coordination/archive/qa-report-history.md:53:  - `well_harness demo --format json 'logic4 和 throttle lock 有什么关系'` 仍返回 `logic4_thr_lock_bridge / logic4->thr_lock / logic4`。
./docs/coordination/archive/qa-report-history.md:88:    - `src/well_harness/static/demo.html`
./docs/coordination/archive/qa-report-history.md:89:    - `src/well_harness/static/demo.css`
./docs/coordination/archive/qa-report-history.md:170:  - `controller.py`、`SimulationRunner`、`well_harness demo`、`POST /api/demo`、`well_harness run` 保持不变。
./docs/coordination/archive/qa-report-history.md:173:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:177:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:178:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:202:  - 独立 server 使用 `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8767 --open`。
./docs/coordination/archive/qa-report-history.md:248:  - 现有 `well_harness demo`、`well_harness demo --format json`、`well_harness run`、`POST /api/demo` 和 `POST /api/lever-snapshot` 行为保持不变。
./docs/coordination/archive/qa-report-history.md:263:  - `POST /api/demo`、`well_harness demo`、`well_harness demo --format json`、`well_harness run` 行为保持不变。
./docs/coordination/archive/qa-report-history.md:267:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:272:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:273:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:274:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:313:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:315:  - 未改变 `well_harness run` CLI 行为。
./docs/coordination/archive/qa-report-history.md:318:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:329:  - `src/well_harness/plant.py` 已在对应实现附近添加简短注释，且没有把它们写成完整物理真值。
./docs/coordination/archive/qa-report-history.md:333:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py src/well_harness/plant.py src/well_harness/controller.py src/well_harness/runner.py`
./docs/coordination/archive/qa-report-history.md:336:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:337:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:338:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:339:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:361:  - `src/well_harness/plant.py` 在 `reverser_not_deployed_eec` 与 `all(pls_unlocked_ls)` 位移门控附近增加了简短注释，均明确是 first-cut plant simplification。
./docs/coordination/archive/qa-report-history.md:370:  - 未修改 `controller.py`、`SimulationRunner`、`scenarios.py`、`well_harness.cli run`。
./docs/coordination/archive/qa-report-history.md:371:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:376:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/plant.py src/well_harness/controller.py src/well_harness/runner.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:391:  - `src/well_harness/controller.py`：`logic1` 保留 `RA < 6ft / SW1 / 非抑制 / 未展开`。
./docs/coordination/archive/qa-report-history.md:392:  - `src/well_harness/controller.py`：`logic2` 使用 `发动机运行 / 在地面 / 非抑制 / SW2 / EEC使能`。
./docs/coordination/archive/qa-report-history.md:393:  - `src/well_harness/controller.py`：`logic3` 没有把 `PLS解锁` 当控制门控条件，且同时输出 `eec_deploy_cmd / pls_power_cmd / pdu_motor_cmd`。
./docs/coordination/archive/qa-report-history.md:394:  - `src/well_harness/controller.py`：`logic4` 使用 `deploy_90_percent_vdt`、`-32° < TRA < 0°`、在地面、发动机运行。
./docs/coordination/archive/qa-report-history.md:395:  - `src/well_harness/switches.py`：`SW1/SW2` 使用区间触发和继续后拉保持语义。
./docs/coordination/archive/qa-report-history.md:396:  - `src/well_harness/plant.py`：位移增长被 simplified plant 门控在 `all(pls_unlocked_ls)` 之后。
./docs/coordination/archive/qa-report-history.md:397:  - `src/well_harness/plant.py`：`reverser_not_deployed_eec` 当前简化为 `deploy_position_percent <= 0.0`。
./docs/coordination/archive/qa-report-history.md:398:  - `src/well_harness/scenarios.py`：当前 built-in scenarios 仍主要是 `nominal-deploy` 与 `retract-reset`。
./docs/coordination/archive/qa-report-history.md:417:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:419:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:420:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:421:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:442:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:444:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:445:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:446:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:455:  - 未修改 controller / runner / scenario / `well_harness.cli run`。
./docs/coordination/archive/qa-report-history.md:456:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:472:  - 启动：`PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/qa-report-history.md:492:  - 未修改 controller / runner / scenario / `well_harness.cli run`。
./docs/coordination/archive/qa-report-history.md:493:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:497:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:500:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:501:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:502:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:511:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:513:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:514:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:515:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:526:  - 未修改 controller / runner / scenario / `well_harness.cli run`。
./docs/coordination/archive/qa-report-history.md:527:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:555:  - 未修改 controller / runner / scenario / `well_harness.cli run`。
./docs/coordination/archive/qa-report-history.md:556:  - 未改变 `well_harness demo` text / JSON 输出语义。
./docs/coordination/archive/qa-report-history.md:572:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:574:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:575:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:576:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:596:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766`
./docs/coordination/archive/qa-report-history.md:616:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:619:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:620:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:621:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:631:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:634:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:635:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:636:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:637:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:638:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:651:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:661:  - `git diff -- src/well_harness/static/demo.html src/well_harness/static/demo.css src/well_harness/static/demo.js tests/test_demo.py README.md docs/coordination/dev_handoff.md docs/coordination/qa_report.md`
./docs/coordination/archive/qa-report-history.md:662:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open`
./docs/coordination/archive/qa-report-history.md:663:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8766 --open`
./docs/coordination/archive/qa-report-history.md:688:  - `PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8765`
./docs/coordination/archive/qa-report-history.md:690:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:693:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:694:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:695:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:696:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:697:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:713:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:720:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server --open` 或手动打开本地 URL。
./docs/coordination/archive/qa-report-history.md:732:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:733:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:735:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:736:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:737:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:738:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:739:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:755:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:761:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server --open`，打开首屏应看到 showcase surface：prompt、fixed chain、structured answer 主干与折叠 raw JSON inspector。
./docs/coordination/archive/qa-report-history.md:775:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:776:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:780:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:781:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:782:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:783:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:784:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:788:  - `src/well_harness/demo_server.py` 新增可选 `--open` 参数。
./docs/coordination/archive/qa-report-history.md:789:  - 默认 `PYTHONPATH=src python3 -m well_harness.demo_server` 行为保持不变。
./docs/coordination/archive/qa-report-history.md:790:  - `PYTHONPATH=src python3 -m well_harness.demo_server --open` 会使用 Python 标准库 `webbrowser.open(...)` 尝试打开本地 UI URL。
./docs/coordination/archive/qa-report-history.md:806:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:812:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server --help`，应看到 `--open`。
./docs/coordination/archive/qa-report-history.md:813:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server --open`，server 会尝试用标准库打开本地 URL；如果失败会提示手动打开并继续 serve。
./docs/coordination/archive/qa-report-history.md:826:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:828:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:829:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:830:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:831:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:832:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:861:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:881:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:884:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:885:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:886:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:887:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:888:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:911:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:931:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:934:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:935:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:936:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:937:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:938:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:960:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:980:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:983:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:984:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:985:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:986:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:987:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1006:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1024:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1030:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1031:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1032:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1033:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1034:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1054:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1071:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1077:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1078:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1079:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1080:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1081:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1101:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1124:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1125:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1126:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1127:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1128:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1129:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1148:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1172:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1173:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1174:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1175:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1176:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1177:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1197:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1221:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1222:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1223:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1224:  - `python3 -m json.tool /tmp/well_harness_round66_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1225:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1226:  - `python3 -m json.tool /tmp/well_harness_round66_nominal.json`
./docs/coordination/archive/qa-report-history.md:1227:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1228:  - `python3 -m json.tool /tmp/well_harness_round66_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1229:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1247:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1255:  - 另开终端运行 `PYTHONPATH=src python3 -m well_harness.demo_server` 并按 helper 清单手测 UI。
./docs/coordination/archive/qa-report-history.md:1271:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1272:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1273:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:1274:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1275:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1276:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1277:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py tools/demo_ui_handcheck.py`
./docs/coordination/archive/qa-report-history.md:1283:  - helper 输出本地 UI 启动命令：`PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1298:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1305:  - 按输出提示另开终端运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1320:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1322:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round64_demo_bridge.txt`
./docs/coordination/archive/qa-report-history.md:1323:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round64_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1324:  - `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round64_demo_logic3.json`
./docs/coordination/archive/qa-report-history.md:1325:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round64_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1326:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round64_demo_server_help.txt`
./docs/coordination/archive/qa-report-history.md:1327:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round64_nominal.json`
./docs/coordination/archive/qa-report-history.md:1328:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round64_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1329:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round64_events.txt`
./docs/coordination/archive/qa-report-history.md:1330:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round64_retract_events.txt`
./docs/coordination/archive/qa-report-history.md:1353:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1359:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1376:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1378:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系' >/tmp/well_harness_round63_demo_bridge.txt`
./docs/coordination/archive/qa-report-history.md:1379:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round63_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1380:  - `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round63_demo_logic3.json`
./docs/coordination/archive/qa-report-history.md:1381:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round63_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1382:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help >/tmp/well_harness_round63_demo_server_help.txt`
./docs/coordination/archive/qa-report-history.md:1383:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round63_nominal.json`
./docs/coordination/archive/qa-report-history.md:1384:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round63_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1385:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round63_events.txt`
./docs/coordination/archive/qa-report-history.md:1386:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round63_retract_events.txt`
./docs/coordination/archive/qa-report-history.md:1405:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1411:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1425:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1428:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1429:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round62_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1430:  - `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round62_demo_logic3.json`
./docs/coordination/archive/qa-report-history.md:1431:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round62_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1432:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round62_nominal.json`
./docs/coordination/archive/qa-report-history.md:1433:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round62_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1434:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5 >/tmp/well_harness_round62_events.txt`
./docs/coordination/archive/qa-report-history.md:1435:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8 >/tmp/well_harness_round62_retract_events.txt`
./docs/coordination/archive/qa-report-history.md:1436:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1459:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1465:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1478:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1481:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1482:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round61_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1483:  - `PYTHONPATH=src python3 -m well_harness demo --format json '触发 logic3 会发生什么' | python3 -m json.tool >/tmp/well_harness_round61_demo_logic3.json`
./docs/coordination/archive/qa-report-history.md:1484:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round61_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1485:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round61_nominal.json`
./docs/coordination/archive/qa-report-history.md:1486:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round61_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1487:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1488:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1489:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1510:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1516:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1529:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1532:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1533:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round60_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1534:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round60_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1535:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round60_nominal.json`
./docs/coordination/archive/qa-report-history.md:1536:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round60_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1537:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1538:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1539:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1558:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1564:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1577:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1580:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1581:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round59_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1582:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round59_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1583:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round59_nominal.json`
./docs/coordination/archive/qa-report-history.md:1584:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round59_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1585:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1586:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1589:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1608:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1614:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1628:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1631:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1632:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool >/tmp/well_harness_round58_demo_bridge.json`
./docs/coordination/archive/qa-report-history.md:1633:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool >/tmp/well_harness_round58_demo_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1634:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round58_nominal.json`
./docs/coordination/archive/qa-report-history.md:1635:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round58_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1636:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1637:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1640:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1662:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1668:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1681:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1684:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1685:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1686:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round57_nominal.json`
./docs/coordination/archive/qa-report-history.md:1687:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round57_diagnose_logic4.json`
./docs/coordination/archive/qa-report-history.md:1688:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:1689:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 4.9`
./docs/coordination/archive/qa-report-history.md:1690:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1692:  - `PYTHONPATH=src python3 -m well_harness.demo_server --help`
./docs/coordination/archive/qa-report-history.md:1695:  - 新增 `src/well_harness/demo_server.py`，使用 Python 标准库本地 HTTP server。
./docs/coordination/archive/qa-report-history.md:1696:  - 启动命令为 `PYTHONPATH=src python3 -m well_harness.demo_server`。
./docs/coordination/archive/qa-report-history.md:1699:    - `src/well_harness/static/demo.html`
./docs/coordination/archive/qa-report-history.md:1700:    - `src/well_harness/static/demo.css`
./docs/coordination/archive/qa-report-history.md:1701:    - `src/well_harness/static/demo.js`
./docs/coordination/archive/qa-report-history.md:1709:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1715:  - 运行 `PYTHONPATH=src python3 -m well_harness.demo_server`，打开打印的本地 URL。
./docs/coordination/archive/qa-report-history.md:1729:  - `sed -n '1,260p' src/well_harness/demo.py`
./docs/coordination/archive/qa-report-history.md:1730:  - `sed -n '1,260p' src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1737:  - 当前已有 `well_harness demo "..."` 与 `well_harness demo --format json "..."`。
./docs/coordination/archive/qa-report-history.md:1761:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1762:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1763:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1764:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1765:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1778:  - `well_harness demo --format json` 输出语义保持不变。
./docs/coordination/archive/qa-report-history.md:1800:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1801:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1802:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1803:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1804:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:1809:  - 入口读取 `tests/fixtures/demo_json_output_asset_v1.json`，复用真实 `well_harness demo --format json` payload，而不是手写第二套 JSON payload。
./docs/coordination/archive/qa-report-history.md:1841:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1842:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1843:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1844:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round54_nominal.json`
./docs/coordination/archive/qa-report-history.md:1849:  - 当前环境安装了 `jsonschema`，该测试实际用 `Draft202012Validator.check_schema(...)` 校验 `docs/json_schema/demo_answer_v1.schema.json`，并验证 `tests/fixtures/demo_json_output_asset_v1.json` 中三条 prompt 的真实 `well_harness demo --format json` payload。
./docs/coordination/archive/qa-report-history.md:1873:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1874:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1875:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1876:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json > /tmp/well_harness_round53_nominal.json`
./docs/coordination/archive/qa-report-history.md:1877:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json > /tmp/well_harness_round53_logic4_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1881:  - 新增 `docs/json_schema/demo_answer_v1.schema.json`，作为 `well_harness demo --format json` 输出的正式 JSON Schema 文档。
./docs/coordination/archive/qa-report-history.md:1915:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1916:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:1917:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1918:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:1919:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json > /tmp/well_harness_round52_nominal.json`
./docs/coordination/archive/qa-report-history.md:1937:  - 默认 `well_harness demo "..."` 人类可读输出保持不变。
./docs/coordination/archive/qa-report-history.md:1953:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:1955:  - `PYTHONPATH=src python3 -m well_harness demo --format json 'logic4 和 throttle lock 有什么关系' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1956:  - `PYTHONPATH=src python3 -m well_harness demo --format json '为什么 logic4 还没满足' | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:1957:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1958:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool >/tmp/well_harness_round51_nominal.json`
./docs/coordination/archive/qa-report-history.md:1959:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool >/tmp/well_harness_round51_logic4_diagnose.json`
./docs/coordination/archive/qa-report-history.md:1963:  - `well_harness demo` 已支持 `--format json`。
./docs/coordination/archive/qa-report-history.md:1964:  - 默认 `well_harness demo "..."` 人类可读输出保持不变，仍包含 `intent:`、`evidence:` 等文本结构。
./docs/coordination/archive/qa-report-history.md:1995:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:1996:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 logic4 还没满足'`
./docs/coordination/archive/qa-report-history.md:1997:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2028:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2030:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 throttle lock 有什么关系'`
./docs/coordination/archive/qa-report-history.md:2031:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 logic4 还没满足，throttle lock 也没释放'`
./docs/coordination/archive/qa-report-history.md:2032:  - `PYTHONPATH=src python3 -m well_harness demo 'logic4 和 THR_LOCK 的关系'`
./docs/coordination/archive/qa-report-history.md:2033:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 logic4 还没满足'`
./docs/coordination/archive/qa-report-history.md:2034:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2067:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 4.9`
./docs/coordination/archive/qa-report-history.md:2068:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 logic4 还没满足'`
./docs/coordination/archive/qa-report-history.md:2069:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2100:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2102:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 SW1 还没触发'`
./docs/coordination/archive/qa-report-history.md:2103:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 SW2 还没触发'`
./docs/coordination/archive/qa-report-history.md:2104:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 TLS115 还没触发'`
./docs/coordination/archive/qa-report-history.md:2105:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 TLS unlocked 还没触发'`
./docs/coordination/archive/qa-report-history.md:2106:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 540V 还没触发'`
./docs/coordination/archive/qa-report-history.md:2107:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 VDT90 还没触发'`
./docs/coordination/archive/qa-report-history.md:2108:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 THR_LOCK 还没释放'`
./docs/coordination/archive/qa-report-history.md:2109:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2110:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2111:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic1 --time 0.4`
./docs/coordination/archive/qa-report-history.md:2112:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic2 --time 1.1`
./docs/coordination/archive/qa-report-history.md:2113:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:2137:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2139:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 TLS unlocked 还没触发'`
./docs/coordination/archive/qa-report-history.md:2140:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 540V 还没触发'`
./docs/coordination/archive/qa-report-history.md:2141:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 VDT90 还没触发'`
./docs/coordination/archive/qa-report-history.md:2142:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 THR_LOCK 还没释放'`
./docs/coordination/archive/qa-report-history.md:2143:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2144:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2145:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic2 --time 1.1`
./docs/coordination/archive/qa-report-history.md:2146:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2147:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:2171:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2173:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 VDT90 还没触发'`
./docs/coordination/archive/qa-report-history.md:2174:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 THR_LOCK 还没释放'`
./docs/coordination/archive/qa-report-history.md:2175:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2176:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2177:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 4.9`
./docs/coordination/archive/qa-report-history.md:2178:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2179:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:2203:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2205:  - `PYTHONPATH=src python3 -m well_harness demo '触发 SW1 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2206:  - `PYTHONPATH=src python3 -m well_harness demo '触发 SW2 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2207:  - `PYTHONPATH=src python3 -m well_harness demo '触发 TLS115 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2208:  - `PYTHONPATH=src python3 -m well_harness demo '触发 540V 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2209:  - `PYTHONPATH=src python3 -m well_harness demo '触发 EEC deploy 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2210:  - `PYTHONPATH=src python3 -m well_harness demo '触发 PLS power 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2211:  - `PYTHONPATH=src python3 -m well_harness demo '触发 TLS unlocked 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2212:  - `PYTHONPATH=src python3 -m well_harness demo '触发 THR_LOCK 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2213:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2214:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2215:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2216:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:2244:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo.py src/well_harness/cli.py`
./docs/coordination/archive/qa-report-history.md:2246:  - `PYTHONPATH=src python3 -m well_harness demo '触发 TLS unlocked 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2247:  - `PYTHONPATH=src python3 -m well_harness demo '触发 PDU motor 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2248:  - `PYTHONPATH=src python3 -m well_harness demo '触发 VDT90 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2249:  - `PYTHONPATH=src python3 -m well_harness demo '触发 THR_LOCK 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2250:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2251:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2277:  - `PYTHONPATH=src python3 -m well_harness demo '触发 TLS unlocked 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2278:  - `PYTHONPATH=src python3 -m well_harness demo '触发 PDU motor 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2279:  - `PYTHONPATH=src python3 -m well_harness demo '触发 VDT90 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2280:  - `PYTHONPATH=src python3 -m well_harness demo '触发 THR_LOCK 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2281:  - `PYTHONPATH=src python3 -m well_harness demo '触发 540V 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2282:  - `PYTHONPATH=src python3 -m well_harness demo '触发 EEC deploy 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2283:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2309:  - `PYTHONPATH=src python3 -m well_harness demo '触发 SW1 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2310:  - `PYTHONPATH=src python3 -m well_harness demo '触发 TLS unlocked 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2311:  - `PYTHONPATH=src python3 -m well_harness demo '触发 VDT90 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2312:  - `PYTHONPATH=src python3 -m well_harness demo '触发 THR_LOCK 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2313:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2314:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json | python3 -m json.tool`
./docs/coordination/archive/qa-report-history.md:2315:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --tail 8`
./docs/coordination/archive/qa-report-history.md:2339:  - `PYTHONPATH=src python3 -m well_harness demo '触发 logic3 会发生什么'`
./docs/coordination/archive/qa-report-history.md:2340:  - `PYTHONPATH=src python3 -m well_harness demo '为什么 throttle lock 没释放'`
./docs/coordination/archive/qa-report-history.md:2341:  - `PYTHONPATH=src python3 -m well_harness demo '如果把 logic3 的 TRA 阈值从 -11.74 改成 -8，会发生什么'`
./docs/coordination/archive/qa-report-history.md:2342:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --tail 3`
./docs/coordination/archive/qa-report-history.md:2343:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --tail 5`
./docs/coordination/archive/qa-report-history.md:2344:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8`
./docs/coordination/archive/qa-report-history.md:2345:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:2349:  - 新增 `well_harness demo` 入口可运行。
./docs/coordination/archive/qa-report-history.md:2789:  - `FAIL CLI` 路径的输出已经收敛为单行脚本摘要，不再泄露 argparse `usage:` / `well_harness: error:` 噪音。
./docs/coordination/archive/qa-report-history.md:2891:  - `python3 -m json.tool docs/json_schema/well_harness_debug_v1.schema.json >/tmp/well_harness_debug_v1.schema.pretty.json`
./docs/coordination/archive/qa-report-history.md:2907:  - `python3 -m json.tool docs/json_schema/well_harness_debug_v1.schema.json >/tmp/well_harness_debug_v1.schema.pretty.json`
./docs/coordination/archive/qa-report-history.md:2924:  - `python3 -m json.tool docs/json_schema/well_harness_debug_v1.schema.json >/tmp/well_harness_debug_v1.schema.pretty.json`
./docs/coordination/archive/qa-report-history.md:2940:  - `python3 -m json.tool docs/json_schema/well_harness_debug_v1.schema.json >/tmp/well_harness_debug_v1.schema.pretty.json`
./docs/coordination/archive/qa-report-history.md:2973:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json | python3 -c '...'`
./docs/coordination/archive/qa-report-history.md:2988:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json | python3 -c '...'`
./docs/coordination/archive/qa-report-history.md:2989:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --format json | python3 -c '...'`
./docs/coordination/archive/qa-report-history.md:2990:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8 --format json | python3 -c '...'`
./docs/coordination/archive/qa-report-history.md:2991:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json | python3 -c '...'`
./docs/coordination/archive/qa-report-history.md:3005:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --full`
./docs/coordination/archive/qa-report-history.md:3006:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic4 --format json`
./docs/coordination/archive/qa-report-history.md:3007:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view diagnose --full`
./docs/coordination/archive/qa-report-history.md:3022:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --full`
./docs/coordination/archive/qa-report-history.md:3023:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json`
./docs/coordination/archive/qa-report-history.md:3024:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view diagnose --full`
./docs/coordination/archive/qa-report-history.md:3039:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8`
./docs/coordination/archive/qa-report-history.md:3040:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic4 --time 5.0 --format json`
./docs/coordination/archive/qa-report-history.md:3041:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --full`
./docs/coordination/archive/qa-report-history.md:3042:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --full`
./docs/coordination/archive/qa-report-history.md:3057:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --full`
./docs/coordination/archive/qa-report-history.md:3058:  - `PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json`
./docs/coordination/archive/qa-report-history.md:3059:  - `PYTHONPATH=src python3 -m well_harness run retract-reset --view events --full`
./docs/coordination/archive/qa-report-history.md:3074:  - `PYTHONPATH=src python3 -m py_compile src/well_harness/demo_server.py src/well_harness/demo.py src/well_harness/cli.py`
./tests/fixtures/validation_report_asset_v1.json:2:  "contract_name": "well_harness.validation_report.v1",
./tests/fixtures/validation_report_asset_v1.json:8:  "schema_path": "docs/json_schema/well_harness_debug_v1.schema.json",
./tests/fixtures/validation_report_asset_v1.json:66:        "contract_name": "well_harness.validation.fail_cli",
./tests/fixtures/validation_report_asset_v1.json:107:        "contract_name": "well_harness.timeline.v1",
./src/well_harness/adapters/thrust_reverser_intake_packet.py:4:Bridges the thrust-reverser truth path (lives in src/well_harness/controller.py
./src/well_harness/adapters/thrust_reverser_intake_packet.py:26:    from well_harness.adapters.thrust_reverser_intake_packet import (
./src/well_harness/adapters/thrust_reverser_intake_packet.py:34:from well_harness.document_intake import (
./src/well_harness/adapters/thrust_reverser_intake_packet.py:38:from well_harness.system_spec import KnowledgeCaptureSpec
./src/well_harness/adapters/thrust_reverser_intake_packet.py:42:THRUST_REVERSER_SOURCE_OF_TRUTH = "src/well_harness/controller.py"
./src/well_harness/adapters/thrust_reverser_intake_packet.py:65:            location="src/well_harness/controller.py",
./src/well_harness/adapters/thrust_reverser_intake_packet.py:139:            "src/well_harness/controller.py::DeployController; this packet is the "
./docs/json_schema/validation_schema_checker_report_v1.schema.json:4:  "title": "well_harness validation schema checker report v1",
./docs/json_schema/validation_schema_checker_report_v1.schema.json:8:    "schema_name": "well_harness.validation_schema_checker_report",
./docs/json_schema/fault_diagnosis_v1.schema.json:4:  "title": "well_harness.fault_diagnosis v1 JSON payload",
./tests/fixtures/events_contract_v1.json:2:  "contract_name": "well_harness.events.v1",
./tests/fixtures/events_contract_v1.json:12:    "name": "well_harness.debug",
./docs/control_logic_guide.md:5:**权威实现**: `src/well_harness/controller.py::DeployController`  
./docs/control_logic_guide.md:6:**评估入口**: `src/well_harness/demo_server.py::lever_snapshot_payload`
./docs/control_logic_guide.md:374:| 四个逻辑门评估 | `src/well_harness/controller.py` | `DeployController.evaluate()` |
./docs/control_logic_guide.md:375:| 快照生成入口 | `src/well_harness/demo_server.py` | `lever_snapshot_payload()` L2090 |
./docs/control_logic_guide.md:376:| TRA 锁载荷构建 | `src/well_harness/demo_server.py` | `_build_tra_lock_payload()` L1601 |
./docs/control_logic_guide.md:377:| 故障注入覆写 | `src/well_harness/demo_server.py` | `_apply_fault_injections_to_snapshot_payload()` L663 |
./docs/control_logic_guide.md:378:| 信号字典 | `src/well_harness/models.py` | `HarnessConfig` |
./docs/control_logic_guide.md:379:| 仿真时间线生成 | `src/well_harness/demo_server.py` | `monitor_timeline_payload()` L1769 |
./docs/control_logic_guide.md:380:| 时间线信号定义 | `src/well_harness/demo_server.py` | `_monitor_series_definition()` L1662 |
./docs/control_logic_guide.md:381:| 前端链路渲染 | `src/well_harness/static/demo.js` | `renderChain()` |
./docs/control_logic_guide.md:382:| 前端 TRA 锁渲染 | `src/well_harness/static/demo.js` | `renderTraLock()` |
./docs/control_logic_guide.md:383:| 前端故障注入构建 | `src/well_harness/static/demo.js` | `buildFaultInjections()` |
./tests/fixtures/_validation_fail_cli_contract.json:2:  "contract_name": "well_harness.validation.fail_cli",
./tests/fixtures/_validation_fail_cli_contract.json:12:    "name": "well_harness.debug",
./docs/notion/ai_fantui_logicmvp_notion_hub.md:309:  - `src/well_harness/controller.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:311:  - `src/well_harness/runner.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:312:  - `src/well_harness/plant.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:313:  - `src/well_harness/switches.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:315:  - `src/well_harness/demo.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:316:  - `src/well_harness/demo_server.py`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:317:  - `src/well_harness/static/*`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:436:- `well_harness run`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:437:- `well_harness demo`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:603:- `docs/json_schema/well_harness_debug_v1.schema.json`
./docs/notion/ai_fantui_logicmvp_notion_hub.md:616:- 代码仓：`well_harness`
./docs/json_schema/validation_schema_runner_report_v1.schema.json:4:  "title": "well_harness validation schema runner report v1",
./docs/json_schema/validation_schema_runner_report_v1.schema.json:8:    "schema_name": "well_harness.validation_schema_runner_report",
./docs/json_schema/control_system_spec_v1.schema.json:4:  "title": "well_harness.control_system_spec v1 JSON payload",
./src/well_harness/adapters/efds_adapter.py:20:from well_harness.controller_adapter import (
./src/well_harness/adapters/efds_adapter.py:23:from well_harness.system_spec import (
./src/well_harness/adapters/efds_adapter.py:35:EFDS_SOURCE_OF_TRUTH = "src/well_harness/adapters/efds_adapter.py"
./src/well_harness/adapters/efds_adapter.py:362:        from well_harness.controller_adapter import GenericTruthEvaluation
./docs/json_schema/workbench_bundle_v1.schema.json:4:  "title": "well_harness.workbench_bundle v1 JSON payload",
./docs/demo_presenter_talk_track.md:40:   `PYTHONPATH=src python3 -m well_harness.demo_server`
./docs/demo_presenter_talk_track.md:41:2. Open the local URL printed by the server, usually `http://127.0.0.1:8000/`. If you want a launch convenience, use `PYTHONPATH=src python3 -m well_harness.demo_server --open`; it only calls the standard-library browser launcher and is not browser E2E automation.
./docs/json_schema/demo_answer_v1.schema.json:4:  "title": "well_harness demo answer v1",
./docs/json_schema/demo_answer_v1.schema.json:5:  "description": "Machine-readable structure reference for well_harness demo --format json output. This documents the DemoAnswer payload shape and is not a plant or controller truth model.",
./docs/json_schema/demo_answer_v1.schema.json:59:    "schema_name": "well_harness.demo_answer",
./docs/json_schema/hardware_schema_v1.schema.json:4:  "title": "well_harness.thrust_reverser_hardware v1",
./docs/demo/pre-pitch-readiness-report.md:27:- adversarial 8/8 (run `python3 src/well_harness/static/adversarial_test.py`)
./docs/json_schema/two_system_runtime_comparison_v1.schema.json:4:  "title": "well_harness.two_system_runtime_comparison v1 JSON payload",
./docs/workbench/xpassed-audit-20260425.md:13:All 12 xpassed cases originate from a single file: `tests/test_p43_authority_contract.py`. Each was marked `@pytest.mark.xfail(strict=False)` while the corresponding P43 sub-phase (P43-03 through P43-08) was pending. Static-grep verification on `src/well_harness/static/workbench.js` (HEAD = 2ded020) confirms all five gating constructs are now present:
./docs/json_schema/second_system_smoke_v1.schema.json:4:  "title": "well_harness.second_system_smoke v1 JSON payload",
./tests/fixtures/demo_answer_asset_v1.json:2:  "name": "well_harness.demo_answer.asset",
./src/well_harness/adapters/__init__.py:1:from well_harness.adapters.landing_gear_adapter import (
./src/well_harness/adapters/__init__.py:6:from well_harness.adapters.efds_adapter import (
./src/well_harness/adapters/__init__.py:11:from well_harness.adapters.c919_etras_adapter import (
./docs/json_schema/well_harness_debug_v1.schema.json:3:  "$id": "https://well-harness.local/json_schema/well_harness_debug_v1.schema.json",
./docs/json_schema/well_harness_debug_v1.schema.json:4:  "title": "well_harness.debug v1 JSON payload",
./docs/json_schema/well_harness_debug_v1.schema.json:8:    "schema_name": "well_harness.debug",
./docs/json_schema/well_harness_debug_v1.schema.json:43:          "const": "well_harness.debug"
./docs/demo/local_model_poc.md:17:            well_harness.llm_client.get_llm_client()
./docs/demo/local_model_poc.md:49:pkill -f well_harness.demo_server
./docs/demo/local_model_poc.md:50:python3 -m well_harness.demo_server &
./docs/demo/local_model_poc.md:54:pkill -f well_harness.demo_server
./docs/demo/local_model_poc.md:55:python3 -m well_harness.demo_server &
./docs/freeze/archive/2026-04-10-freeze-demo-packet-history.md:33:- `src/well_harness/controller.py` 仍然是唯一控制真值。
./docs/json_schema/playback_trace_v1.schema.json:4:  "title": "well_harness.playback_trace v1 JSON payload",
./docs/workbench/HANDOVER.md:115:- E08 endpoint semantics are implemented in `src/well_harness/workbench/` but not mounted into `demo_server.py`, because the allowed file domain only permitted the E06 `/workbench` route addition in that file.
./docs/workbench/HANDOVER.md:140:**Why this is a gap:** The annotation overlay (`src/well_harness/static/annotation_overlay.js`) keeps draft markers and Annotation Inbox state in browser memory. Existing tests assert structural correctness over short-lived requests; nothing exercises a multi-hour idle session where the same Workbench tab keeps overlays mounted, drafts accumulate, and DOM listeners remain bound.
./docs/workbench/HANDOVER.md:157:**Why this is a gap:** `src/well_harness/collab/restricted_auth.py` enforces the `Authorized Engineer` + `Scope Files` invariants per call, but two tabs of `/workbench` open against the same demo_server can each generate ticket prompts concurrently. Existing tests are single-actor, single-tab. A real reviewer scenario (two reviewer tabs + one engineer tab) is not exercised.
./docs/json_schema/workbench_archive_manifest_v1.schema.json:4:  "title": "well_harness.workbench_archive_manifest v1 JSON payload",
./docs/json_schema/workbench_archive_manifest_v1.schema.json:179:          "const": "python3 -m well_harness.cli archive-manifest ."
./docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:4:  "title": "well_harness.controller_truth_adapter_metadata v1 JSON payload",
./docs/json_schema/controller_truth_adapter_metadata_v1.schema.json:5:  "description": "Published metadata contract for controller truth adapters. This documents adapter identity and source-of-truth boundaries without introducing a second control truth. P42 (2026-04-20) extended additively in v1 with two optional governance fields (truth_level, status). Per the serializer in well_harness.controller_adapter, governance fields that are None at the dataclass layer are dropped from the payload. Therefore: field missing in a payload means pre-P42/unclassified and MUST NOT be treated by downstream consumers as 'already governed'. See each field's own description for the resulting semantic.",
./docs/json_schema/fault_taxonomy_v1.schema.json:4:  "title": "well_harness fault taxonomy v1",
./docs/demo/pitch_script.md:48:- 真值引擎代码：`src/well_harness/controller.py` · 19 节点 · 4 逻辑门（logic1–logic4）
./docs/demo/pitch_script.md:153:pkill -f well_harness.demo_server
./docs/demo/pitch_script.md:154:python3 -m well_harness.demo_server &
./docs/demo/pitch_script.md:183:| **R1 真值优先** | 19 节点状态始终来自 controller.py，AI 从不改写 | `src/well_harness/controller.py` |
./docs/demo/pitch_script.md:187:| **R5 对抗守门** | 对抗测试 8/8 通过（注入/越权/绕过） | `src/well_harness/static/adversarial_test.py` |
./docs/workbench/inherited-logic4-blocker-investigation.md:121: src/well_harness/demo_server.py | 18 ++++++++++++++++--
./docs/workbench/inherited-logic4-blocker-investigation.md:137:**Code change (load-bearing snippet, `src/well_harness/demo_server.py::_canonical_pullback_sequence`):**
./docs/freeze/2026-04-09-freeze-snapshot.md:44:- `src/well_harness/controller.py` 仍然是唯一控制真值。
./docs/freeze/2026-04-09-freeze-snapshot.md:45:- `src/well_harness/runner.py` 仍然是仿真编排层。
./docs/freeze/2026-04-09-freeze-snapshot.md:47:- `POST /api/demo`、`POST /api/lever-snapshot`、`GET /api/monitor-timeline`、`well_harness demo`、`well_harness run` 视为当前冻结版的有效演示接口。
./docs/demo/backend-switch-drill-findings.md:111:pkill -f well_harness.demo_server && python3 -m well_harness.demo_server &
./docs/demo/backend-switch-drill-findings.md:127:- SIGTERM→exit **t_kill_ms=1ms** 看起来可疑，但合理：`well_harness.demo_server` 没注册长清理 hook，SIGTERM 到进程死亡主要受 Bottle 的 asyncore loop 退出速度决定。用 `os.killpg` 对进程组发信号，两步内能干净退出
./docs/demo/faq.md:18:`src/well_harness/controller.py` 的 19 节点 + 4 逻辑门是确定性的——同样输入永远同样输出。
./docs/demo/faq.md:22:- 证据：`src/well_harness/controller.py` · `tests/test_controller.py`（真值回归测试）
./docs/demo/faq.md:60:- 证据：`archive/shelved/llm-features/src/llm_client.py` · `src/well_harness/static/adversarial_test.py`
./docs/demo/faq.md:61:  · `src/well_harness/demo_server.py`（operate handler 白名单逻辑）
./docs/demo/faq.md:153:3. **对抗测试：** `src/well_harness/static/adversarial_test.py` 8 个场景覆盖
./docs/demo/faq.md:156:- 证据：`src/well_harness/static/adversarial_test.py`（当前 8/8 通过）
./docs/demo/faq.md:182:- 证据：`src/well_harness/demo_server.py` explain/operate/reason 三个 handler 的 system prompt
./docs/demo/faq.md:194:- 证据：`src/well_harness/demo_server.py` chat handlers 如何 inject snapshot 到 system prompt
./docs/provenance/sha_registry.yaml:35:      - src/well_harness/adapters/thrust_reverser_intake_packet.py
./docs/provenance/sha_registry.yaml:46:      - src/well_harness/adapters/c919_etras_intake_packet.py
./docs/P43-api-contract-lock.yaml:4:# src/well_harness/demo_server.py at commit 5d2d3ec (after Step B fix).
./docs/P43-api-contract-lock.yaml:364:        anchor: src/well_harness/ai_doc_analyzer.py:799
./docs/demo/disaster_runbook.md:26:   pkill -f well_harness.demo_server && python3 -m well_harness.demo_server &
./docs/demo/disaster_runbook.md:95:pkill -9 -f well_harness.demo_server || true
./docs/demo/disaster_runbook.md:96:nohup python3 -m well_harness.demo_server > /tmp/demo_server.log 2>&1 &
./runs/xpassed_audit_20260425T045925Z.txt:4:tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/bleed_air_adapter.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:5:tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/efds_adapter.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:6:tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/landing_gear_adapter.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:7:tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/bleed_air_intake_packet.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:8:tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/landing_gear_intake_packet.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:11:tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/bleed_air_adapter.py] PASSED [  0%]
./runs/xpassed_audit_20260425T045925Z.txt:12:tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/efds_adapter.py] PASSED [  1%]
./runs/xpassed_audit_20260425T045925Z.txt:13:tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/landing_gear_adapter.py] PASSED [  1%]
./runs/xpassed_audit_20260425T045925Z.txt:14:tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/bleed_air_intake_packet.py] PASSED [  1%]
./runs/xpassed_audit_20260425T045925Z.txt:15:tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/landing_gear_intake_packet.py] PASSED [  1%]
./runs/xpassed_audit_20260425T045925Z.txt:813:tests/test_validation_suite.py::ValidationSuiteTests::test_build_child_env_prepends_repo_src_to_pythonpath PASSED [ 93%]
./docs/demo/preflight_checklist.md:45:| 13 | 对抗绿 | 启 demo_server :8766 → `python3 src/well_harness/static/adversarial_test.py 2>&1 | tail -3` | `ALL TESTS PASSED` | 不能演对抗段 |
./docs/demo/preflight_checklist.md:63:| 17 | demo_server 可访问 + Canvas 渲染 | 启 `python3 -m well_harness.demo_server --port 8799 &` → 浏览器开 `http://127.0.0.1:8799/` → 硬刷 Cmd-Shift-R | 19 节点可见 + 聊天抽屉可展开 |
./docs/demo/preflight_checklist.md:113:│       python3 -m well_harness.demo_server &      │
./docs/provenance/adapter_truth_levels.yaml:38:    metadata_module: well_harness.controller_adapter
./docs/provenance/adapter_truth_levels.yaml:45:    metadata_module: well_harness.adapters.bleed_air_adapter
./docs/provenance/adapter_truth_levels.yaml:52:    metadata_module: well_harness.adapters.efds_adapter
./docs/provenance/adapter_truth_levels.yaml:59:    metadata_module: well_harness.adapters.landing_gear_adapter
./docs/provenance/adapter_truth_levels.yaml:66:    metadata_module: well_harness.adapters.c919_etras_adapter
./runs/post_merge_followup_20260425/three_track_evidence.md:36:$ WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py
./docs/demo/pitch-citations-audit.md:18:| Q1-controller-class | faq.md Q1 | `class DeployController` | src/well_harness/controller.py | ✅ |
./docs/demo/pitch-citations-audit.md:19:| Q4-chat-explain-handler | faq.md Q4/Q13 | `def _handle_chat_explain` | src/well_harness/demo_server.py | ✅ |
./docs/demo/pitch-citations-audit.md:20:| Q4-chat-operate-handler | faq.md Q4/Q13 | `def _handle_chat_operate` | src/well_harness/demo_server.py | ✅ |
./docs/demo/pitch-citations-audit.md:21:| Q13-chat-reason-handler | faq.md Q13 | `def _handle_chat_reason` | src/well_harness/demo_server.py | ✅ |
./docs/demo/pitch-citations-audit.md:22:| Q8-LLMClient-protocol | faq.md Q8/Q15 | `class LLMClient(...Protocol)` | src/well_harness/llm_client.py | ✅ |
./docs/demo/pitch-citations-audit.md:23:| Q8-MiniMaxClient | faq.md Q8 | `class MiniMaxClient` | src/well_harness/llm_client.py | ✅ |
./docs/demo/pitch-citations-audit.md:24:| Q8-OllamaClient | faq.md Q8 | `class OllamaClient` | src/well_harness/llm_client.py | ✅ |
./docs/demo/pitch-citations-audit.md:25:| Q8-BACKENDS-dict | faq.md Q8/Q15 | `_BACKENDS: ` | src/well_harness/llm_client.py | ✅ |
./docs/demo/pitch-citations-audit.md:26:| Q15-get-llm-client-factory | faq.md Q15 | `def get_llm_client` | src/well_harness/llm_client.py | ✅ |
./docs/demo/pitch-citations-audit.md:27:| Q11-VALID-ACTION-TYPES | faq.md Q11 | `VALID_ACTION_TYPES = {` | src/well_harness/demo_server.py | ✅ |
./docs/demo/pitch-citations-audit.md:28:| Q11-VALID-RESPONSE-TYPES | faq.md Q11 | `VALID_RESPONSE_TYPES = {` | src/well_harness/demo_server.py | ✅ |
./runs/workbench_e2e_20260425T040608Z/ticket.json:4:  "Generated Prompt": "# Claude Code Workbench Ticket\n\n## anchor\n\n- Proposal: prop_demo_e2e_001\n- Ticket: WB-E10-DEMO\n- System: thrust-reverser\n- Authorized Engineer: claude-code\n- Surface: document\n- Tool: text-range\n- Note: Demo ticket for PR review and close loop evidence.\n- Anchor JSON: {\"end_offset\": 28, \"selector\": \"#workbench-document-panel\", \"start_offset\": 0, \"text_quote\": \"Reference packet\"}\n\n## scope\n\n- src/well_harness/workbench/**\n- docs/workbench/**\n\n## acceptance\n\n- Implement only the scoped Workbench change requested by the annotation proposal.\n- Preserve proposal ID `prop_demo_e2e_001` and ticket ID `WB-E10-DEMO` in handoff notes.\n- Add or update focused tests for the changed behavior.\n- Run the repo's fast-lane validation before handing back.\n\n## non-goals\n\n- Do not edit controller truth, adapter truth, logic gates, pitch materials, or Parking Lot items.\n- Do not write to Notion directly.\n- Do not expand scope files without Kogami approval.\n- Do not present a local stub as a merged or deployed change.\n",
./runs/workbench_e2e_20260425T040608Z/ticket.json:26:    "src/well_harness/workbench/**",

exec
/bin/zsh -lc "python3 - <<'PY'
import well_harness, inspect
import well_harness.demo_server as ds
print('well_harness', well_harness.__file__)
print('demo_server', ds.__file__)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
from http.server import ThreadingHTTPServer
from threading import Thread
from http.client import HTTPConnection
from well_harness.demo_server import DemoRequestHandler
import well_harness.demo_server as ds
print('demo_server', ds.__file__)
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
for path in ('/v6.1-redline','/v6.1-redline.txt','/workbench'):
    conn = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('GET', path)
    resp = conn.getresponse()
    body = resp.read().decode('utf-8', errors='replace')
    print('PATH', path)
    print('STATUS', resp.status)
    print('CONTENT_TYPE', resp.getheader('Content-Type'))
    print('BODY_SNIP', body[:300].replace('\\n','\\\\n'))
    conn.close()
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 115ms:
well_harness /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/__init__.py
demo_server /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py

 succeeded in 582ms:
demo_server /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py
PATH /v6.1-redline
STATUS 200
CONTENT_TYPE text/plain; charset=utf-8
BODY_SNIP # v6.1 truth-engine red-line clause\n\n\nForbidden（红线维持，触碰即停车）\n\n- `src/well_harness/controller.py` 任何编辑（pure truth engine）\n- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义\n- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）\n- `runs/dress_rehearsal_*/wo
PATH /v6.1-redline.txt
STATUS 200
CONTENT_TYPE text/plain; charset=utf-8
BODY_SNIP # v6.1 truth-engine red-line clause\n\n\nForbidden（红线维持，触碰即停车）\n\n- `src/well_harness/controller.py` 任何编辑（pure truth engine）\n- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义\n- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）\n- `runs/dress_rehearsal_*/wo
PATH /workbench
STATUS 200
CONTENT_TYPE text/html; charset=utf-8
BODY_SNIP <!doctype html>\n<html lang="zh-CN">\n  <head>\n    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <title>Control Logic Workbench</title>\n    <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n    <link rel="apple-touch-icon" href="/apple-tou

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.css | sed -n '300,380p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '216,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   216	### Forbidden（红线维持，触碰即停车）
   217	
   218	- `src/well_harness/controller.py` 任何编辑（pure truth engine）
   219	- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义
   220	- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）
   221	- `runs/dress_rehearsal_*/wow_*_timeline.json` fixture 数据
   222	- Force-push 到 main / 已 merge 分支；squash 重写 main 历史；`--no-verify` / `--no-gpg-sign`
   223	- 假装跑了测试（数字必须来自真实 stdout 粘贴）
   224	- 自创规则版本号（v6.1 之后下次叠加层应是 v6.2，不得跳号）
   225	
   226	### Codex 触发清单（继承 v6.0 + V61-001 新增 + v6.1 EMPIRICAL-CLAIM-PROBE）
   227	
   228	继承 v6.0 硬性触发：多文件前端、API 契约、e2e 期望变更、UI 交互模式、用户 UX 批评首次实现、OpenFOAM solver 报错、Phase E2E ≥3 case 连续失败、Docker+OpenFOAM 联合调试、`foam_agent_adapter.py` >5 LOC、`_generate_*.py` CFD 几何新增、GSD 产出物。
   229	
   230	继承 RETRO-V61-001 新增：安全敏感 operator endpoint、byte-reproducibility 敏感路径、跨 ≥3 文件 API schema rename。
   231	
   232	**v6.1 新增 EMPIRICAL-CLAIM-PROBE 规则（2026-04-25）：** PR prose（test docstring / 文件级 comment / demo doc / PR description）写下任何关于服务端 runtime 行为的具体数字（plant deploy %、sim time、tick count、logic-X activation timing 等）之前，Claude Code 必须 boot 相关代码路径在本地实测一次，或显式标 `TODO(probe-before-merge)`，或引用数字定义所在的 commit:line。仅基于 mental-model 算术得出的数字禁止落地到 regression-locked 测试或客户向 demo doc。来源：PR #5 round 1 Codex 命中 BEAT_EARLY ~6% deploy 实际 0% （详 `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`）。
   233	
   234	## v2.3 · UI-COPY-PROBE
   235	
   236	### 触发条件
   237	任何写入 repo 的 user-facing 自然语言文本，包括但不限于：
   238	- 入口页 / landing 页的 tile title / tile description / hero copy
   239	- button label / link text / empty state / tooltip / modal body
   240	- toast / banner / inline notice
   241	- onboarding 步骤说明 / 错误提示文案
   242	
   243	豁免：
   244	- 纯 a11y 标签（aria-label）若与可见 label 1:1 同步
   245	- 自动从 schema / enum / config 渲染的字符串（值由代码生成，文案即数据）
   246	
   247	### 强制 stage（写完之后、commit 之前必走）
   248	对本期新增/修改的每一条 user-facing copy，作者必须执行 **claim-to-source sweep**：
   249	
   250	1. **拆 claim**：把 copy 拆成可验证的具体声明单元（surface 名、行为、字段、角色、限制、数据来源、文件格式、SHA 类型……）。叙述性形容词（"流畅"、"清晰"）不计 claim。
   251	2. **grep 回 src/**：每一条 claim 必须在 src/ tests/ schemas/ config/ 至少一个文件中找到 line-number 锚点；锚点要支持该 claim 当前已 ship，不是计划态。
   252	3. **三选一处置**：
   253	   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
   254	   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
   255	   - **[DELETE]** 找不到锚点且无规划 → 删除该 claim。
   256	
   257	#### Anchor 格式细则
   258	
   259	每一条 anchor 必须是 **可执行的 ripgrep / sed 命令的目标**。按 claim 极性，正合法形式只有两种之一：
   260	

 succeeded in 0ms:
   300	
   301	.workbench-wow-result[data-wow-state="error"] {
   302	  border: 1px solid rgba(247, 144, 144, 0.5);
   303	  color: #ffd6d6;
   304	}
   305	
   306	/* E11-13: trust-affordance banner. Visible only when
   307	   data-feedback-mode = manual_feedback_override AND not session-dismissed.
   308	   Explains the advisory boundary so the user does not infer authority
   309	   from manual override. */
   310	.workbench-trust-banner {
   311	  display: flex;
   312	  align-items: flex-start;
   313	  gap: 0.85rem;
   314	  margin-bottom: 1rem;
   315	  padding: 0.85rem 1rem;
   316	  border: 1px solid rgba(247, 188, 92, 0.5);
   317	  border-radius: 10px;
   318	  background: rgba(247, 188, 92, 0.1);
   319	  color: #f7e2ba;
   320	}
   321	
   322	.workbench-trust-banner[data-feedback-mode="truth_engine"],
   323	.workbench-trust-banner[data-trust-banner-dismissed="true"] {
   324	  display: none;
   325	}
   326	
   327	.workbench-trust-banner-icon {
   328	  flex: 0 0 auto;
   329	  font-size: 1.2rem;
   330	  color: #f7d398;
   331	  line-height: 1;
   332	}
   333	
   334	.workbench-trust-banner-body {
   335	  flex: 1 1 auto;
   336	  display: flex;
   337	  flex-direction: column;
   338	  gap: 0.25rem;
   339	  font-size: 0.9rem;
   340	  line-height: 1.45;
   341	}
   342	
   343	.workbench-trust-banner-body strong {
   344	  color: #fbeacb;
   345	}
   346	
   347	.workbench-trust-banner-scope {
   348	  color: rgba(247, 226, 186, 0.86);
   349	  font-size: 0.85rem;
   350	}
   351	
   352	.workbench-trust-banner-scope em {
   353	  color: #fbeacb;
   354	  font-style: normal;
   355	  font-weight: 600;
   356	}
   357	
   358	.workbench-trust-banner-dismiss {
   359	  flex: 0 0 auto;
   360	  align-self: center;
   361	  padding: 0.35rem 0.7rem;
   362	  border: 1px solid rgba(247, 188, 92, 0.4);
   363	  border-radius: 6px;
   364	  background: transparent;
   365	  color: #fbeacb;
   366	  cursor: pointer;
   367	  font-size: 0.8rem;
   368	}
   369	
   370	.workbench-trust-banner-dismiss:hover {
   371	  background: rgba(247, 188, 92, 0.16);
   372	}
   373	
   374	/* E11-07 (2026-04-26): Authority Contract banner.
   375	   Permanent, always-visible 1-line banner above the 3-column grid that
   376	   announces the truth-engine read-only contract and links to the v6.1
   377	   red-line clause. Distinct visual language from the manual_feedback
   378	   trust banner (which is conditional/dismissible) — this banner is
   379	   neither dismissible nor conditional. */
   380	.workbench-authority-banner {

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '320,390p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   320	            <span>Logic 4</span>
   321	            <span>THR LOCK</span>
   322	          </div>
   323	        </article>
   324	      </section>
   325	
   326	      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
   327	        <header>
   328	          <p class="eyebrow">annotation inbox</p>
   329	          <h2>Review Queue</h2>
   330	        </header>
   331	        <ul id="annotation-inbox-list">
   332	          <li>No proposals submitted yet.</li>
   333	        </ul>
   334	      </aside>
   335	
   336	      <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
   337	        <button
   338	          id="approval-center-entry"
   339	          type="button"
   340	          class="workbench-toolbar-button"
   341	          data-role="KOGAMI"
   342	          aria-controls="approval-center-panel"
   343	        >
   344	          Approval Center
   345	        </button>
   346	        <span>Approval actions are Kogami-only.</span>
   347	      </footer>
   348	
   349	      <section
   350	        id="approval-center-panel"
   351	        class="workbench-approval-center"
   352	        data-approval-role="KOGAMI"
   353	        aria-labelledby="approval-center-title"
   354	      >
   355	        <header>
   356	          <p class="eyebrow">approval center</p>
   357	          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
   358	        </header>
   359	        <div class="workbench-approval-grid">
   360	          <article class="workbench-approval-lane" data-approval-lane="pending">
   361	            <h3>Pending</h3>
   362	            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
   363	          </article>
   364	          <article class="workbench-approval-lane" data-approval-lane="accept">
   365	            <h3>Accept</h3>
   366	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
   367	          </article>
   368	          <article class="workbench-approval-lane" data-approval-lane="reject">
   369	            <h3>Reject</h3>
   370	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
   371	          </article>
   372	        </div>
   373	      </section>
   374	
   375	      <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
   376	    </main>
   377	
   378	    <script src="/annotation_overlay.js"></script>
   379	    <script src="/workbench.js"></script>
   380	  </body>
   381	</html>

exec
/bin/zsh -lc 'rg -n "workbench-authority-banner|annotation_overlay|workbench.js|workbench_trust_banner|proposal|acceptance or rejection|No proposals submitted yet" src/well_harness/static/workbench.html src/well_harness/static/*.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:236:        id="workbench-authority-banner"
src/well_harness/static/workbench.html:237:        class="workbench-authority-banner"
src/well_harness/static/workbench.html:241:        <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
src/well_harness/static/workbench.html:242:        <span class="workbench-authority-banner-headline">
src/well_harness/static/workbench.html:245:        <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
src/well_harness/static/workbench.html:246:        <span class="workbench-authority-banner-rule">
src/well_harness/static/workbench.html:247:          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
src/well_harness/static/workbench.html:250:          class="workbench-authority-banner-link"
src/well_harness/static/workbench.html:332:          <li>No proposals submitted yet.</li>
src/well_harness/static/workbench.html:362:            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
src/well_harness/static/workbench.html:378:    <script src="/annotation_overlay.js"></script>
src/well_harness/static/workbench.html:379:    <script src="/workbench.js"></script>
src/well_harness/static/annotation_overlay.js:83:        ui: "workbench.annotation_overlay",
src/well_harness/static/annotation_overlay.js:122:    if (list.children.length === 1 && list.children[0].textContent === "No proposals submitted yet.") {

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.css | sed -n '380,455p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   380	.workbench-authority-banner {
   381	  display: flex;
   382	  flex-wrap: wrap;
   383	  align-items: baseline;
   384	  gap: 0.6rem;
   385	  margin-bottom: 0.85rem;
   386	  padding: 0.55rem 0.95rem;
   387	  border: 1px solid rgba(120, 220, 170, 0.32);
   388	  border-radius: 8px;
   389	  background: rgba(20, 40, 30, 0.6);
   390	  color: #c8e8d4;
   391	  font-size: 0.88rem;
   392	  line-height: 1.4;
   393	}
   394	
   395	.workbench-authority-banner-icon {
   396	  font-size: 1rem;
   397	}
   398	
   399	.workbench-authority-banner-headline {
   400	  font-weight: 600;
   401	  color: #d8f5e2;
   402	  letter-spacing: 0.02em;
   403	}
   404	
   405	.workbench-authority-banner-sep {
   406	  color: rgba(206, 223, 236, 0.42);
   407	}
   408	
   409	.workbench-authority-banner-rule {
   410	  color: rgba(200, 232, 212, 0.86);
   411	}
   412	
   413	.workbench-authority-banner-link {
   414	  margin-left: auto;
   415	  padding: 0.18rem 0.55rem;
   416	  border-radius: 4px;
   417	  background: rgba(120, 220, 170, 0.12);
   418	  color: #b6ecc8;
   419	  font-size: 0.78rem;
   420	  text-decoration: none;
   421	  white-space: nowrap;
   422	}
   423	
   424	.workbench-authority-banner-link:hover {
   425	  background: rgba(120, 220, 170, 0.22);
   426	  color: #d8f5e2;
   427	}
   428	
   429	.workbench-annotation-toolbar {
   430	  display: flex;
   431	  align-items: center;
   432	  gap: 0.65rem;
   433	  margin-bottom: 1rem;
   434	  padding: 0.75rem 1rem;
   435	}
   436	
   437	.workbench-annotation-toolbar-label {
   438	  color: rgba(206, 223, 236, 0.72);
   439	  font-size: 0.75rem;
   440	  letter-spacing: 0.06em;
   441	  text-transform: uppercase;
   442	}
   443	
   444	.workbench-annotation-tool {
   445	  border: 1px solid rgba(143, 214, 233, 0.22);
   446	  border-radius: 8px;
   447	  background: rgba(16, 31, 46, 0.88);
   448	  color: #edf8ff;
   449	  cursor: pointer;
   450	  padding: 0.55rem 0.72rem;
   451	}
   452	
   453	.workbench-annotation-tool.is-active,
   454	.workbench-annotation-tool[aria-pressed="true"] {
   455	  border-color: rgba(122, 224, 210, 0.58);

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    15	E11-04: Tier-B (7 copy_diff_lines, fails ≥10 threshold; though 7 [REWRITE] meets ≥3). Persona = P3 (Demo Presenter — content-fit for domain vocabulary the engineer reads on screen; also the round-robin successor of P2). Plan row 275 said "NO Codex (mechanical relabel)" but the constitution Tier-B rule is the stricter SSOT.
    16	E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE] — all NEW section content fails ≥3 threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit for new endpoint contract validation).
    17	E11-07: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE] — pure-NEW banner). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit for customer/repro-facing authority contract messaging).

 succeeded in 0ms:
     1	# E11-07 Surface Inventory — Authority Contract banner
     2	
     3	> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
     4	
     5	## Surface diff inventory
     6	
     7	| # | Surface | Type | Anchor | Notes |
     8	|---|---|---|---|---|
     9	| 1 | Banner icon `🔒` | [ANCHORED] | `#workbench-authority-banner` (NEW) | Always-visible truth-engine seal. |
    10	| 2 | Banner headline `Truth Engine — Read Only` | [ANCHORED] | same section | Names the contract directly. |
    11	| 3 | Banner rule `Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值` | [ANCHORED] | same section | The actual rule — propose only, never mutate. |
    12	| 4 | Banner link label `v6.1 红线条款 →` | [ANCHORED] | `<a href="/v6.1-redline">` | Anchored to the new route. |
    13	
    14	## Tier-trigger evaluation
    15	
    16	Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
    17	
    18	> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
    19	
    20	- **copy_diff_lines** = 4 → < 10
    21	- **[REWRITE/DELETE] count** = 0 → < 3
    22	
    23	Both thresholds NOT met. → **Tier-B** (1-persona review).
    24	
    25	E11-00-PLAN row E11-07 explicitly says "不（仅 UI banner，不动 code）". Tier-B with one persona review is the conservative middle ground.
    26	
    27	> **Verdict: Tier-B**. Persona = **P5 (Apps Engineer)** — round-robin successor of E11-06's P4 AND content-fit: the banner is the customer/repro-facing authority contract; P5 should validate the messaging is unambiguous from the customer/new-engineer perspective and that the link target is real.
    28	
    29	## New endpoint contract
    30	
    31	`GET /v6.1-redline` (and `/v6.1-redline.txt`) returns 200 plain-text excerpt of the v6.1 truth-engine red-line clause. Sourced live from `.planning/constitution.md` so the rendered text never drifts from the constitution's words. Falls back to a small static excerpt if the constitution is unreachable, so the banner never produces a 404.
    32	
    33	The excerpt MUST name at least one of the four off-limits paths (controller / runner / models / adapters) — locked by `test_v61_redline_excerpt_carries_truth_engine_paths`.
    34	
    35	## Truth-engine red line
    36	
    37	Files touched:
    38	- `src/well_harness/static/workbench.html` — NEW `<aside id="workbench-authority-banner">` between annotation toolbar and 3-column grid
    39	- `src/well_harness/static/workbench.css` — NEW `.workbench-authority-banner*` selectors
    40	- `src/well_harness/demo_server.py` — NEW route `/v6.1-redline` + `_serve_v61_redline_excerpt()` helper. **Read-only**: never mutates state, only reads `.planning/constitution.md`.
    41	- `tests/test_workbench_authority_banner.py` — NEW (12 tests)
    42	
    43	Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new banner *names* the truth-engine red line — this is the meta-statement, not a violation.

exec
/bin/zsh -lc 'git diff main..c7131e9 -- src/well_harness/demo_server.py src/well_harness/static/workbench.html src/well_harness/static/workbench.css tests/test_workbench_authority_banner.py .planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
new file mode 100644
index 0000000..c8dad78
--- /dev/null
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md
@@ -0,0 +1,43 @@
+# E11-07 Surface Inventory — Authority Contract banner
+
+> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
+
+## Surface diff inventory
+
+| # | Surface | Type | Anchor | Notes |
+|---|---|---|---|---|
+| 1 | Banner icon `🔒` | [ANCHORED] | `#workbench-authority-banner` (NEW) | Always-visible truth-engine seal. |
+| 2 | Banner headline `Truth Engine — Read Only` | [ANCHORED] | same section | Names the contract directly. |
+| 3 | Banner rule `Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值` | [ANCHORED] | same section | The actual rule — propose only, never mutate. |
+| 4 | Banner link label `v6.1 红线条款 →` | [ANCHORED] | `<a href="/v6.1-redline">` | Anchored to the new route. |
+
+## Tier-trigger evaluation
+
+Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
+
+> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
+
+- **copy_diff_lines** = 4 → < 10
+- **[REWRITE/DELETE] count** = 0 → < 3
+
+Both thresholds NOT met. → **Tier-B** (1-persona review).
+
+E11-00-PLAN row E11-07 explicitly says "不（仅 UI banner，不动 code）". Tier-B with one persona review is the conservative middle ground.
+
+> **Verdict: Tier-B**. Persona = **P5 (Apps Engineer)** — round-robin successor of E11-06's P4 AND content-fit: the banner is the customer/repro-facing authority contract; P5 should validate the messaging is unambiguous from the customer/new-engineer perspective and that the link target is real.
+
+## New endpoint contract
+
+`GET /v6.1-redline` (and `/v6.1-redline.txt`) returns 200 plain-text excerpt of the v6.1 truth-engine red-line clause. Sourced live from `.planning/constitution.md` so the rendered text never drifts from the constitution's words. Falls back to a small static excerpt if the constitution is unreachable, so the banner never produces a 404.
+
+The excerpt MUST name at least one of the four off-limits paths (controller / runner / models / adapters) — locked by `test_v61_redline_excerpt_carries_truth_engine_paths`.
+
+## Truth-engine red line
+
+Files touched:
+- `src/well_harness/static/workbench.html` — NEW `<aside id="workbench-authority-banner">` between annotation toolbar and 3-column grid
+- `src/well_harness/static/workbench.css` — NEW `.workbench-authority-banner*` selectors
+- `src/well_harness/demo_server.py` — NEW route `/v6.1-redline` + `_serve_v61_redline_excerpt()` helper. **Read-only**: never mutates state, only reads `.planning/constitution.md`.
+- `tests/test_workbench_authority_banner.py` — NEW (12 tests)
+
+Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new banner *names* the truth-engine red line — this is the meta-statement, not a violation.
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index b4335e9..24eacc4 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -14,3 +14,4 @@ E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html
 E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
 E11-04: Tier-B (7 copy_diff_lines, fails ≥10 threshold; though 7 [REWRITE] meets ≥3). Persona = P3 (Demo Presenter — content-fit for domain vocabulary the engineer reads on screen; also the round-robin successor of P2). Plan row 275 said "NO Codex (mechanical relabel)" but the constitution Tier-B rule is the stricter SSOT.
 E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE] — all NEW section content fails ≥3 threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit for new endpoint contract validation).
+E11-07: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE] — pure-NEW banner). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit for customer/repro-facing authority contract messaging).
diff --git a/src/well_harness/demo_server.py b/src/well_harness/demo_server.py
index 00fc2d6..a9cf9f4 100644
--- a/src/well_harness/demo_server.py
+++ b/src/well_harness/demo_server.py
@@ -258,6 +258,14 @@ class DemoRequestHandler(BaseHTTPRequestHandler):
             self._serve_static("workbench.html")
             return
 
+        # E11-07 (2026-04-26): Authority Contract banner link target.
+        # Serves the v6.1 truth-engine red-line clause as plain text so
+        # the banner's "v6.1 红线条款 →" link resolves to a real, in-repo
+        # excerpt rather than a 404. Read-only; no truth-engine mutation.
+        if parsed.path in ("/v6.1-redline", "/v6.1-redline.txt"):
+            self._serve_v61_redline_excerpt()
+            return
+
         relative_path = unquote(parsed.path.lstrip("/"))
         if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
             self._serve_static(relative_path)
@@ -592,6 +600,43 @@ class DemoRequestHandler(BaseHTTPRequestHandler):
         content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
         self._send_bytes(200, target_path.read_bytes(), content_type)
 
+    def _serve_v61_redline_excerpt(self):
+        """E11-07 (2026-04-26): serve the v6.1 truth-engine red-line clause
+        as plain text. Sourced from .planning/constitution.md so the demo
+        ships the same words the constitution does, with no drift risk."""
+        repo_root = Path(__file__).resolve().parents[2]
+        constitution = repo_root / ".planning" / "constitution.md"
+        try:
+            full_text = constitution.read_text(encoding="utf-8")
+        except (FileNotFoundError, OSError):
+            full_text = ""
+        excerpt_lines = ["# v6.1 truth-engine red-line clause\n", ""]
+        if full_text:
+            # Pull the explicit "Forbidden（红线维持）" section. If the
+            # exact heading drifts, fall back to a small static excerpt
+            # so the link still resolves to *something* truthful.
+            anchor = full_text.find("Forbidden（红线维持")
+            if anchor != -1:
+                end = full_text.find("\n## ", anchor)
+                section = full_text[anchor:end] if end != -1 else full_text[anchor:]
+                excerpt_lines.append(section.rstrip())
+            else:
+                excerpt_lines.append(
+                    "Truth-engine 红线: controller / runner / models / "
+                    "adapters/ are read-only by design. Workbench surfaces "
+                    "may propose changes via ticket / proposal — they may "
+                    "never mutate truth-engine values directly. See "
+                    ".planning/constitution.md §v6.1 Solo Autonomy Delegation."
+                )
+        else:
+            excerpt_lines.append(
+                "Truth-engine 红线 source file (.planning/constitution.md) "
+                "is not available in this checkout. The contract remains: "
+                "controller / runner / models / adapters/ are read-only."
+            )
+        body = "\n".join(excerpt_lines).encode("utf-8")
+        self._send_bytes(200, body, "text/plain; charset=utf-8")
+
     def _send_json(self, status_code: int, payload: dict):
         # Compact JSON: no indentation (machine-to-machine API, not human-readable)
         response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
diff --git a/src/well_harness/static/workbench.css b/src/well_harness/static/workbench.css
index b3a3484..16cbf01 100644
--- a/src/well_harness/static/workbench.css
+++ b/src/well_harness/static/workbench.css
@@ -371,6 +371,61 @@
   background: rgba(247, 188, 92, 0.16);
 }
 
+/* E11-07 (2026-04-26): Authority Contract banner.
+   Permanent, always-visible 1-line banner above the 3-column grid that
+   announces the truth-engine read-only contract and links to the v6.1
+   red-line clause. Distinct visual language from the manual_feedback
+   trust banner (which is conditional/dismissible) — this banner is
+   neither dismissible nor conditional. */
+.workbench-authority-banner {
+  display: flex;
+  flex-wrap: wrap;
+  align-items: baseline;
+  gap: 0.6rem;
+  margin-bottom: 0.85rem;
+  padding: 0.55rem 0.95rem;
+  border: 1px solid rgba(120, 220, 170, 0.32);
+  border-radius: 8px;
+  background: rgba(20, 40, 30, 0.6);
+  color: #c8e8d4;
+  font-size: 0.88rem;
+  line-height: 1.4;
+}
+
+.workbench-authority-banner-icon {
+  font-size: 1rem;
+}
+
+.workbench-authority-banner-headline {
+  font-weight: 600;
+  color: #d8f5e2;
+  letter-spacing: 0.02em;
+}
+
+.workbench-authority-banner-sep {
+  color: rgba(206, 223, 236, 0.42);
+}
+
+.workbench-authority-banner-rule {
+  color: rgba(200, 232, 212, 0.86);
+}
+
+.workbench-authority-banner-link {
+  margin-left: auto;
+  padding: 0.18rem 0.55rem;
+  border-radius: 4px;
+  background: rgba(120, 220, 170, 0.12);
+  color: #b6ecc8;
+  font-size: 0.78rem;
+  text-decoration: none;
+  white-space: nowrap;
+}
+
+.workbench-authority-banner-link:hover {
+  background: rgba(120, 220, 170, 0.22);
+  color: #d8f5e2;
+}
+
 .workbench-annotation-toolbar {
   display: flex;
   align-items: center;
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index f1fff5a..4cae143 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -232,6 +232,31 @@
         </span>
       </section>
 
+      <aside
+        id="workbench-authority-banner"
+        class="workbench-authority-banner"
+        role="note"
+        aria-label="Truth-engine authority contract"
+      >
+        <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
+        <span class="workbench-authority-banner-headline">
+          Truth Engine — Read Only
+        </span>
+        <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
+        <span class="workbench-authority-banner-rule">
+          Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值
+        </span>
+        <a
+          class="workbench-authority-banner-link"
+          href="/v6.1-redline"
+          target="_blank"
+          rel="noopener"
+          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
+        >
+          v6.1 红线条款 →
+        </a>
+      </aside>
+
       <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
         <article
           id="workbench-control-panel"
diff --git a/tests/test_workbench_authority_banner.py b/tests/test_workbench_authority_banner.py
new file mode 100644
index 0000000..7e621ba
--- /dev/null
+++ b/tests/test_workbench_authority_banner.py
@@ -0,0 +1,146 @@
+"""E11-07 — Authority Contract banner regression lock.
+
+Locks the always-visible banner that announces the truth-engine
+read-only contract on /workbench, plus the /v6.1-redline route that
+serves the constitution clause the banner links to.
+
+Per E11-00-PLAN row E11-07: pure-UI banner, no truth-engine code
+changes. The contract is twofold —
+  1. The banner is on the /workbench shell with the canonical copy.
+  2. The link target resolves to a real text excerpt sourced from
+     .planning/constitution.md (so the banner is not a dead link).
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
+def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str, str]:
+    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
+    connection.request("GET", path)
+    response = connection.getresponse()
+    body = response.read().decode("utf-8")
+    content_type = response.getheader("Content-Type", "")
+    return response.status, body, content_type
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
+# ─── 1. Banner is present on /workbench ──────────────────────────────
+
+
+def test_workbench_html_has_authority_banner() -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert 'id="workbench-authority-banner"' in html
+    assert 'role="note"' in html
+    # Always-visible: no data-dismissed attribute, no conditional class
+    # toggling. The banner stays on screen for the entire session.
+    assert "data-trust-banner-dismiss" not in (
+        html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
+    )
+
+
+@pytest.mark.parametrize(
+    "phrase",
+    [
+        "🔒",
+        "Truth Engine — Read Only",
+        "Propose 不修改",
+        "工程师只能提交 ticket / proposal",
+        "v6.1 红线条款",
+    ],
+)
+def test_workbench_html_banner_carries_canonical_copy(phrase: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert phrase in html, f"missing canonical banner copy: {phrase}"
+
+
+def test_workbench_html_banner_links_to_v61_redline_route() -> None:
+    """The banner link must point at the in-repo route, not at an
+    external GitHub URL or a stale /.planning/ path that the static
+    handler would 404 on."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    banner_block = html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
+    assert 'href="/v6.1-redline"' in banner_block
+
+
+# ─── 2. /v6.1-redline route works ────────────────────────────────────
+
+
+def test_v61_redline_route_returns_200_text(server) -> None:
+    status, body, content_type = _get(server, "/v6.1-redline")
+    assert status == 200
+    assert "text/plain" in content_type
+    assert "v6.1" in body or "truth-engine" in body or "红线" in body
+
+
+def test_v61_redline_excerpt_carries_truth_engine_paths(server) -> None:
+    """Whatever excerpt the route returns, it must name the four paths
+    that are off-limits — controller/runner/models/adapters."""
+    _, body, _ = _get(server, "/v6.1-redline")
+    # At least one of the canonical truth-engine path names must appear,
+    # whether in the constitution excerpt or in the static fallback.
+    assert any(name in body for name in ("controller", "runner", "models", "adapters")), (
+        f"excerpt missing truth-engine path names; got {body[:200]!r}"
+    )
+
+
+def test_v61_redline_route_alias_with_extension(server) -> None:
+    """Both /v6.1-redline and /v6.1-redline.txt should resolve."""
+    status, body, _ = _get(server, "/v6.1-redline.txt")
+    assert status == 200
+    assert body  # non-empty
+
+
+# ─── 3. Live-served /workbench renders banner end-to-end ────────────
+
+
+def test_workbench_route_serves_authority_banner(server) -> None:
+    status, html, _ = _get(server, "/workbench")
+    assert status == 200
+    assert 'id="workbench-authority-banner"' in html
+    assert 'href="/v6.1-redline"' in html
+    assert "Truth Engine — Read Only" in html
+
+
+# ─── 4. Banner placement: above the 3-column collab grid ────────────
+
+
+def test_workbench_banner_appears_before_collab_grid() -> None:
+    """The banner must sit ABOVE the 3-column grid so it frames the
+    controller / circuit columns, not below them."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    banner_pos = html.find('id="workbench-authority-banner"')
+    grid_pos = html.find('class="workbench-collab-grid"')
+    assert banner_pos != -1 and grid_pos != -1
+    assert banner_pos < grid_pos, (
+        "authority banner must precede the 3-column collab grid"
+    )

exec
/bin/zsh -lc 'rg -n "def lever_snapshot_payload|def diagnosis_run_payload|def monte_carlo|def _handle_diagnosis|def _handle_monte|def parse_lever_snapshot_request|manual_feedback_override|auto_scrubber" src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
162:    "auto_scrubber",
163:    "manual_feedback_override",
392:                            "manual_feedback_override authority chain. To use it from "
395:                            "with feedback_mode=manual_feedback_override + sign-off."
699:    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
711:            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
716:# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
717:# When feedback_mode = manual_feedback_override, the request must include
725:    Only enforced when feedback_mode == "manual_feedback_override". For
726:    auto_scrubber, this returns None unconditionally (no extra fields needed).
728:    if feedback_mode != "manual_feedback_override":
742:                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
743:                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
759:        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
761:        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
766:            "manual_feedback_override requires a manual_override_signoff object.",
1182:def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
1256:    # auto_scrubber; returns 409 payload with `_status` hint when signoff
1257:    # missing/invalid for manual_feedback_override.
1573:                feedback_mode="manual_feedback_override",
1604:            "feedback_mode": "manual_feedback_override",
1873:    deploy rate. Without this, auto_scrubber shows L4 permanently blocked on
1982:        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
1989:    elif feedback_mode == "manual_feedback_override":
2098:    if feedback_mode == "manual_feedback_override":
2634:def lever_snapshot_payload(
2643:    feedback_mode: str = "auto_scrubber",
2764:        if feedback_mode == "auto_scrubber"
2771:            if feedback_mode == "auto_scrubber"
2772:            else "manual_feedback_override"
2810:            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '680,860p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   680	
   681	def _parse_bool_input(request_payload: dict, field_name: str, default: bool) -> tuple[bool | None, dict | None]:
   682	    raw_value = request_payload.get(field_name, default)
   683	    if isinstance(raw_value, bool):
   684	        return raw_value, None
   685	    if isinstance(raw_value, str):
   686	        normalized = raw_value.strip().lower()
   687	        if normalized in {"true", "1", "yes", "on"}:
   688	            return True, None
   689	        if normalized in {"false", "0", "no", "off"}:
   690	            return False, None
   691	    return None, {
   692	        "error": "invalid_lever_snapshot_input",
   693	        "field": field_name,
   694	        "message": f"{field_name} must be boolean.",
   695	    }
   696	
   697	
   698	def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
   699	    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
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
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '920,1120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   920	
   921	
   922	def _apply_fault_injections_to_snapshot_payload(
   923	    result: dict,
   924	    fault_injections: list[dict] | None,
   925	) -> dict:
   926	    fault_map = _fault_injection_map(fault_injections)
   927	    if not fault_map:
   928	        return result
   929	
   930	    nodes_by_id = {
   931	        node["id"]: node
   932	        for node in result.get("nodes", [])
   933	        if isinstance(node, dict) and "id" in node
   934	    }
   935	    input_payload = result.get("input")
   936	    hud_payload = result.get("hud")
   937	    outputs_payload = result.get("outputs")
   938	    logic_payload = result.get("logic")
   939	
   940	    for node_id, fault_type in fault_map.items():
   941	        reason = _fault_reason(fault_type)
   942	
   943	        if node_id == "sw1":
   944	            active = fault_type == "stuck_on"
   945	            if isinstance(hud_payload, dict):
   946	                hud_payload["sw1"] = active
   947	            _set_faulted_node_state(
   948	                nodes_by_id.get("sw1"),
   949	                state="active" if active else "inactive",
   950	            )
   951	            continue
   952	
   953	        if node_id == "sw2":
   954	            active = fault_type == "stuck_on"
   955	            if isinstance(hud_payload, dict):
   956	                hud_payload["sw2"] = active
   957	            _set_faulted_node_state(
   958	                nodes_by_id.get("sw2"),
   959	                state="active" if active else "inactive",
   960	            )
   961	            continue
   962	
   963	        if node_id == "radio_altitude_ft" and fault_type == "sensor_zero":
   964	            if isinstance(input_payload, dict):
   965	                input_payload["radio_altitude_ft"] = 0.0
   966	            if isinstance(hud_payload, dict):
   967	                hud_payload["radio_altitude_ft"] = 0.0
   968	            _set_faulted_node_state(nodes_by_id.get("radio_altitude_ft"), state="inactive")
   969	            continue
   970	
   971	        if node_id == "n1k" and fault_type == "sensor_zero":
   972	            if isinstance(input_payload, dict):
   973	                input_payload["n1k"] = 0.0
   974	            if isinstance(hud_payload, dict):
   975	                hud_payload["n1k"] = 0.0
   976	            _set_faulted_node_state(nodes_by_id.get("n1k"), state="inactive")
   977	            continue
   978	
   979	        if node_id == "tls115" and fault_type == "sensor_zero":
   980	            if isinstance(outputs_payload, dict):
   981	                outputs_payload["tls_115vac_cmd"] = False
   982	            _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
   983	            continue
   984	
   985	        if node_id in {"logic1", "logic2", "logic3", "logic4"} and fault_type == "logic_stuck_false":
   986	            logic_entry = logic_payload.get(node_id) if isinstance(logic_payload, dict) else None
   987	            if isinstance(logic_entry, dict):
   988	                logic_entry["active"] = False
   989	                failed_conditions = list(logic_entry.get("failed_conditions") or [])
   990	                _append_unique(failed_conditions, reason)
   991	                logic_entry["failed_conditions"] = failed_conditions
   992	
   993	            if isinstance(outputs_payload, dict):
   994	                outputs_payload[f"{node_id}_active"] = False
   995	
   996	            _set_faulted_node_state(nodes_by_id.get(node_id), state="blocked", reason=reason)
   997	
   998	            if node_id == "logic1":
   999	                if isinstance(outputs_payload, dict):
  1000	                    outputs_payload["tls_115vac_cmd"] = False
  1001	                _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
  1002	            elif node_id == "logic2":
  1003	                if isinstance(outputs_payload, dict):
  1004	                    outputs_payload["etrac_540vdc_cmd"] = False
  1005	                _set_faulted_node_state(nodes_by_id.get("etrac_540v"), state="inactive")
  1006	            elif node_id == "logic3":
  1007	                if isinstance(outputs_payload, dict):
  1008	                    outputs_payload["eec_deploy_cmd"] = False
  1009	                    outputs_payload["pls_power_cmd"] = False
  1010	                    outputs_payload["pdu_motor_cmd"] = False
  1011	                _set_faulted_node_state(nodes_by_id.get("eec_deploy"), state="inactive")
  1012	                _set_faulted_node_state(nodes_by_id.get("pls_power"), state="inactive")
  1013	                _set_faulted_node_state(nodes_by_id.get("pdu_motor"), state="inactive")
  1014	            elif node_id == "logic4":
  1015	                if isinstance(outputs_payload, dict):
  1016	                    outputs_payload["throttle_electronic_lock_release_cmd"] = False
  1017	                _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
  1018	            continue
  1019	
  1020	        if node_id == "thr_lock" and fault_type == "cmd_blocked":
  1021	            if isinstance(outputs_payload, dict):
  1022	                outputs_payload["throttle_electronic_lock_release_cmd"] = False
  1023	            _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
  1024	            continue
  1025	
  1026	        if node_id == "vdt90" and fault_type == "cmd_blocked":
  1027	            if isinstance(hud_payload, dict):
  1028	                hud_payload["deploy_90_percent_vdt"] = False
  1029	            _set_faulted_node_state(nodes_by_id.get("vdt90"), state="blocked", reason=reason)
  1030	
  1031	    result["active_fault_node_ids"] = list(fault_map.keys())
  1032	    result["fault_injections"] = fault_injections or []
  1033	    return result
  1034	
  1035	
  1036	_TIMELINE_MAX_DURATION_S = 600.0
  1037	_TIMELINE_MIN_STEP_S = 0.01
  1038	# Belt-and-braces cap so a user cannot request 600s / 0.01s = 60,000 ticks
  1039	# just because each individual bound is within range (Codex PR-2 MINOR #1).
  1040	_TIMELINE_MAX_TICKS = 20_000
  1041	_TIMELINE_MAX_EVENTS = 500
  1042	
  1043	
  1044	def _handle_fantui_tick(request_payload: dict) -> tuple[int, dict]:
  1045	    """Advance the FANTUI stateful tick system one step and return a snapshot.
  1046	
  1047	    Paired with ``/api/fantui/reset`` and ``/api/fantui/log``. The response
  1048	    mirrors what /api/log emits so the same ``timeseries_chart.js`` module can
  1049	    render either panel's buffer.
  1050	    """
  1051	    try:
  1052	        pilot = parse_pilot_inputs(request_payload)
  1053	    except ValueError as exc:
  1054	        return 400, {"error": "invalid_input", "message": str(exc)}
  1055	    try:
  1056	        dt_s = float(request_payload.get("dt_s", 0.1))
  1057	    except (TypeError, ValueError):
  1058	        return 400, {"error": "invalid_dt_s"}
  1059	    # Guard: tick step must be positive, finite, and small enough to avoid
  1060	    # jumping over switch windows. 1.0s is a conservative ceiling.
  1061	    # ``math.isfinite`` rejects NaN / ±Inf before they can poison ``_t_s``
  1062	    # (Codex review, 2026-04-24, CRITICAL).
  1063	    if not math.isfinite(dt_s) or dt_s <= 0 or dt_s > 1.0:
  1064	        return 400, {"error": "dt_s_out_of_range", "message": "0 < dt_s <= 1.0"}
  1065	
  1066	    rec, count = _FANTUI_SYSTEM.tick_with_count(pilot, dt_s)
  1067	    snapshot = rec.as_dict()
  1068	    snapshot["sample_count"] = count
  1069	    return 200, snapshot
  1070	
  1071	
  1072	def _handle_timeline_simulate(request_payload: dict) -> dict:
  1073	    """Run a Timeline against the FANTUI executor and return the trace as JSON.
  1074	
  1075	    Returns `_status` key for the HTTP code to use (200 / 400).
  1076	    """
  1077	    try:
  1078	        timeline = parse_timeline(request_payload)
  1079	    except TimelineValidationError as exc:
  1080	        return {"_status": 400, "error": "invalid_timeline", "field": exc.field, "message": exc.message}
  1081	
  1082	    if timeline.system != "fantui":
  1083	        return {
  1084	            "_status": 400,
  1085	            "error": "unsupported_system",
  1086	            "message": f"this endpoint only runs FANTUI timelines; got system={timeline.system!r}",
  1087	        }
  1088	    if timeline.duration_s > _TIMELINE_MAX_DURATION_S:
  1089	        return {
  1090	            "_status": 400,
  1091	            "error": "timeline_too_long",
  1092	            "message": f"duration_s must be <= {_TIMELINE_MAX_DURATION_S}s",
  1093	        }
  1094	    if timeline.step_s < _TIMELINE_MIN_STEP_S:
  1095	        return {
  1096	            "_status": 400,
  1097	            "error": "timeline_step_too_small",
  1098	            "message": f"step_s must be >= {_TIMELINE_MIN_STEP_S}s",
  1099	        }
  1100	    tick_count = int(timeline.duration_s / timeline.step_s) + 1
  1101	    if tick_count > _TIMELINE_MAX_TICKS:
  1102	        return {
  1103	            "_status": 400,
  1104	            "error": "timeline_too_many_ticks",
  1105	            "message": f"duration_s/step_s would produce {tick_count} ticks; max {_TIMELINE_MAX_TICKS}",
  1106	        }
  1107	    if len(timeline.events) > _TIMELINE_MAX_EVENTS:
  1108	        return {
  1109	            "_status": 400,
  1110	            "error": "timeline_too_many_events",
  1111	            "message": f"events list has {len(timeline.events)} entries; max {_TIMELINE_MAX_EVENTS}",
  1112	        }
  1113	
  1114	    try:
  1115	        executor = FantuiExecutor()
  1116	        trace = TimelinePlayer(timeline, executor).run()
  1117	    except (ValueError, TypeError) as exc:
  1118	        # Runtime errors (unknown fault id, bad set_input value, …) get
  1119	        # surfaced as a 400 rather than a 500 so the UI can show the
  1120	        # validation message inline (Codex PR-2 MAJOR #3).

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1120,1300p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1120	        # validation message inline (Codex PR-2 MAJOR #3).
  1121	        return {
  1122	            "_status": 400,
  1123	            "error": "invalid_timeline",
  1124	            "message": str(exc),
  1125	        }
  1126	    return _timeline_trace_to_json(trace)
  1127	
  1128	
  1129	def _timeline_trace_to_json(trace) -> dict:
  1130	    return {
  1131	        "timeline": {
  1132	            "system": trace.timeline.system,
  1133	            "step_s": trace.timeline.step_s,
  1134	            "duration_s": trace.timeline.duration_s,
  1135	            "title": trace.timeline.title,
  1136	            "description": trace.timeline.description,
  1137	        },
  1138	        "frames": [
  1139	            {
  1140	                "tick": f.tick,
  1141	                "t_s": f.t_s,
  1142	                "phase": f.phase,
  1143	                "inputs": f.inputs,
  1144	                "outputs": f.outputs,
  1145	                "logic_states": f.logic_states,
  1146	                "active_faults": f.active_faults,
  1147	                "events_fired": f.events_fired,
  1148	            }
  1149	            for f in trace.frames
  1150	        ],
  1151	        "transitions": [
  1152	            {
  1153	                "tick": f.tick,
  1154	                "t_s": f.t_s,
  1155	                "phase": f.phase,
  1156	                "logic_states": f.logic_states,
  1157	                "active_faults": f.active_faults,
  1158	            }
  1159	            for f in trace.transitions
  1160	        ],
  1161	        "assertions": [
  1162	            {
  1163	                "at_s": a.at_s,
  1164	                "target": a.target,
  1165	                "expected": a.expected,
  1166	                "observed": a.observed,
  1167	                "passed": a.passed,
  1168	                "note": a.note,
  1169	            }
  1170	            for a in trace.assertions
  1171	        ],
  1172	        "outcome": {
  1173	            "deployed_successfully": trace.outcome.deployed_successfully,
  1174	            "thr_lock_released": trace.outcome.thr_lock_released,
  1175	            "logic_first_active_t_s": trace.outcome.logic_first_active_t_s,
  1176	            "logic_first_blocked_t_s": trace.outcome.logic_first_blocked_t_s,
  1177	            "failure_cascade": trace.outcome.failure_cascade,
  1178	        },
  1179	    }
  1180	
  1181	
  1182	def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
  1183	    lever_inputs = {}
  1184	    for field_name, options in LEVER_NUMERIC_INPUTS.items():
  1185	        value, error_payload = _parse_float_input(request_payload, field_name, options)
  1186	        if error_payload is not None:
  1187	            return None, error_payload
  1188	        lever_inputs[field_name] = value
  1189	
  1190	    config = HarnessConfig()
  1191	    lever_inputs["tra_deg"] = _clamp_tra(lever_inputs["tra_deg"], config)
  1192	
  1193	    for field_name, default in LEVER_BOOLEAN_INPUTS.items():
  1194	        value, error_payload = _parse_bool_input(request_payload, field_name, default)
  1195	        if error_payload is not None:
  1196	            return None, error_payload
  1197	        lever_inputs[field_name] = value
  1198	
  1199	    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
  1200	    if error_payload is not None:
  1201	        return None, error_payload
  1202	    lever_inputs["feedback_mode"] = feedback_mode
  1203	
  1204	    # E11-14 R1 had the guard here; moved to the END of structural parsing
  1205	    # in R2 (P2 IMPORTANT #3, 2026-04-25): a malformed
  1206	    # deploy_position_percent="oops" + missing signoff used to return 409
  1207	    # manual_override_unsigned, masking the real 400. Authority guard now
  1208	    # runs on otherwise-well-formed manual-override requests only.
  1209	
  1210	    deploy_position_percent, error_payload = _parse_float_input(
  1211	        request_payload,
  1212	        "deploy_position_percent",
  1213	        {"default": 0.0, "min": 0.0, "max": 100.0},
  1214	    )
  1215	    if error_payload is not None:
  1216	        return None, error_payload
  1217	    lever_inputs["deploy_position_percent"] = deploy_position_percent
  1218	
  1219	    fault_injections = request_payload.get("fault_injections")
  1220	    if fault_injections is not None:
  1221	        if not isinstance(fault_injections, list):
  1222	            return None, {
  1223	                "error": "invalid_fault_injections",
  1224	                "message": "fault_injections must be a list",
  1225	            }
  1226	        normalized_faults = []
  1227	        for fault in fault_injections:
  1228	            if not isinstance(fault, dict):
  1229	                return None, {
  1230	                    "error": "invalid_fault_injections",
  1231	                    "message": "each fault_injection must be an object",
  1232	                }
  1233	            node_id = str(fault.get("node_id", "")).strip()
  1234	            fault_type = str(fault.get("fault_type", "")).strip()
  1235	            if node_id not in LEVER_SNAPSHOT_FAULT_NODES:
  1236	                return None, {
  1237	                    "error": "invalid_fault_injection_node",
  1238	                    "message": f"Unknown node_id: {node_id}",
  1239	                }
  1240	            if fault_type not in LEVER_SNAPSHOT_FAULT_TYPES:
  1241	                return None, {
  1242	                    "error": "invalid_fault_type",
  1243	                    "message": f"Unknown fault_type: {fault_type}",
  1244	                }
  1245	            normalized_faults.append(
  1246	                {
  1247	                    "node_id": _normalize_fault_injection_node_id(node_id),
  1248	                    "fault_type": fault_type,
  1249	                }
  1250	            )
  1251	        if normalized_faults:
  1252	            lever_inputs["_fault_injections"] = normalized_faults
  1253	
  1254	    # E11-14 R2 (P2 IMPORTANT #3): authority guard runs AFTER structural
  1255	    # parsing so 400 (malformed) precedes 409 (unsigned). No-op for
  1256	    # auto_scrubber; returns 409 payload with `_status` hint when signoff
  1257	    # missing/invalid for manual_feedback_override.
  1258	    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
  1259	    if signoff_error is not None:
  1260	        return None, signoff_error
  1261	
  1262	    return lever_inputs, None
  1263	
  1264	
  1265	def default_workbench_archive_root() -> Path:
  1266	    return (Path.cwd() / "artifacts" / "workbench-bundles").resolve()
  1267	
  1268	
  1269	def reference_workbench_packet_payload() -> dict:
  1270	    return json.loads(REFERENCE_PACKET_PATH.read_text(encoding="utf-8"))
  1271	
  1272	
  1273	def build_explain_runtime_payload() -> dict[str, Any]:
  1274	    # LLM features shelved in Phase A (2026-04-22). Return a stable idle payload
  1275	    # so workbench clients can still render the runtime panel without runtime error.
  1276	    return {
  1277	        "status": "shelved",
  1278	        "status_source": "runtime_config",
  1279	        "llm_backend": "",
  1280	        "llm_model": "",
  1281	        "response_source": "unknown",
  1282	        "cached_at": "",
  1283	        "observed_at_utc": "",
  1284	        "verified_cache_hits": 0,
  1285	        "expected_count": 0,
  1286	        "backend_match": None,
  1287	        "requested_backend": "",
  1288	        "requested_model": "",
  1289	        "detail": "LLM features shelved — see archive/shelved/llm-features/SHELVED.md.",
  1290	        "boundary_note": "这是 explain runtime / pitch 运维状态，不是新的控制真值。",
  1291	    }
  1292	
  1293	
  1294	def recent_workbench_archive_summaries(*, limit: int = 6) -> list[dict]:
  1295	    archive_root = default_workbench_archive_root()
  1296	    if not archive_root.is_dir():
  1297	        return []
  1298	
  1299	    summaries: list[dict] = []
  1300	    for archive_dir in archive_root.iterdir():

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '440,520p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   440	            if error_payload is not None:
   441	                self._send_json(400, error_payload)
   442	                return
   443	            self._send_json(200, response_payload)
   444	            return
   445	        if parsed.path == WORKBENCH_REPAIR_PATH:
   446	            response_payload, error_payload = build_workbench_safe_repair_response(request_payload)
   447	            if error_payload is not None:
   448	                self._send_json(400, error_payload)
   449	                return
   450	            self._send_json(200, response_payload)
   451	            return
   452	        if parsed.path == WORKBENCH_ARCHIVE_RESTORE_PATH:
   453	            response_payload, error_payload = build_workbench_archive_restore_response(request_payload)
   454	            if error_payload is not None:
   455	                self._send_json(400, error_payload)
   456	                return
   457	            self._send_json(200, response_payload)
   458	            return
   459	
   460	        # P19.6: Reverse diagnosis run (uses already-parsed request_payload)
   461	        if parsed.path == DIAGNOSIS_RUN_PATH:
   462	            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
   463	            outcome = str(request_payload.get("outcome", "")).strip()
   464	            if outcome not in VALID_OUTCOMES:
   465	                self._send_json(400, {
   466	                    "error": f"Invalid outcome: {outcome!r}. "
   467	                             f"Valid: {sorted(VALID_OUTCOMES)}"
   468	                })
   469	                return
   470	            max_results = min(int(request_payload.get("max_results", 1000)), 1000)
   471	            max_results = max(max_results, 0)
   472	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   473	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   474	                self._send_json(400, {
   475	                    "error": f"system_id {system_id!r} is not supported for diagnosis. "
   476	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   477	                })
   478	                return
   479	            yaml_path = self._hardware_yaml_path(system_id)
   480	            try:
   481	                engine = ReverseDiagnosisEngine(yaml_path)
   482	                report = engine.diagnose_and_report(outcome, max_results=max_results)
   483	                self._send_json(200, report)
   484	            except Exception as exc:
   485	                self._send_json(500, {"error": str(exc)})
   486	            return
   487	
   488	        # P19.7: Monte Carlo reliability simulation
   489	        if parsed.path == MONTE_CARLO_RUN_PATH:
   490	            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
   491	            n_trials_raw = request_payload.get("n_trials", 100)
   492	            try:
   493	                n_trials = int(n_trials_raw)
   494	            except (TypeError, ValueError):
   495	                self._send_json(400, {"error": "n_trials must be an integer"})
   496	                return
   497	            n_trials = max(1, min(n_trials, 10000))
   498	
   499	            seed = None
   500	            if "seed" in request_payload:
   501	                try:
   502	                    seed = int(request_payload["seed"])
   503	                except (TypeError, ValueError):
   504	                    self._send_json(400, {"error": "seed must be an integer"})
   505	                    return
   506	
   507	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   508	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   509	                self._send_json(400, {
   510	                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
   511	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   512	                })
   513	                return
   514	            yaml_path = self._hardware_yaml_path(system_id)
   515	            try:
   516	                engine = MonteCarloEngine(yaml_path)
   517	                result = engine.run(n_trials, seed=seed)
   518	                self._send_json(200, _reliability_result_to_dict(result))
   519	            except Exception as exc:
   520	                self._send_json(500, {"error": str(exc)})

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2634,2825p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2634	def lever_snapshot_payload(
  2635	    tra_deg: float,
  2636	    radio_altitude_ft: float = 5.0,
  2637	    engine_running: bool = True,
  2638	    aircraft_on_ground: bool = True,
  2639	    reverser_inhibited: bool = False,
  2640	    eec_enable: bool = True,
  2641	    n1k: float = 35.0,
  2642	    max_n1k_deploy_limit: float = 60.0,
  2643	    feedback_mode: str = "auto_scrubber",
  2644	    deploy_position_percent: float = 0.0,
  2645	    fault_injections: list[dict] | None = None,
  2646	) -> dict:
  2647	    config = HarnessConfig()
  2648	    requested_tra = _clamp_tra(tra_deg, config)
  2649	    lock_deg = _clamp_tra(TRA_L4_LOCK_DEG, config)
  2650	    requested_snapshot = _simulate_lever_state(
  2651	        requested_tra,
  2652	        config=config,
  2653	        radio_altitude_ft=radio_altitude_ft,
  2654	        engine_running=engine_running,
  2655	        aircraft_on_ground=aircraft_on_ground,
  2656	        reverser_inhibited=reverser_inhibited,
  2657	        eec_enable=eec_enable,
  2658	        n1k=n1k,
  2659	        max_n1k_deploy_limit=max_n1k_deploy_limit,
  2660	        feedback_mode=feedback_mode,
  2661	        deploy_position_percent=deploy_position_percent,
  2662	        fault_injections=fault_injections,
  2663	    )
  2664	    lock_probe = _simulate_lever_state(
  2665	        lock_deg,
  2666	        config=config,
  2667	        radio_altitude_ft=radio_altitude_ft,
  2668	        engine_running=engine_running,
  2669	        aircraft_on_ground=aircraft_on_ground,
  2670	        reverser_inhibited=reverser_inhibited,
  2671	        eec_enable=eec_enable,
  2672	        n1k=n1k,
  2673	        max_n1k_deploy_limit=max_n1k_deploy_limit,
  2674	        feedback_mode=feedback_mode,
  2675	        deploy_position_percent=deploy_position_percent,
  2676	        fault_injections=fault_injections,
  2677	    )
  2678	    boundary_unlock_ready = lock_probe["outputs"].logic4_active
  2679	    effective_tra = (
  2680	        requested_tra
  2681	        if boundary_unlock_ready or requested_tra >= lock_deg
  2682	        else lock_deg
  2683	    )
  2684	    snapshot = (
  2685	        requested_snapshot
  2686	        if effective_tra == requested_tra
  2687	        else lock_probe
  2688	    )
  2689	
  2690	    time_s = snapshot["time_s"]
  2691	    plant_debug_state = snapshot["plant_state"]
  2692	    sensors = snapshot["sensors"]
  2693	    pilot_inputs = snapshot["pilot_inputs"]
  2694	    inputs = snapshot["inputs"]
  2695	    outputs = snapshot["outputs"]
  2696	    explain = snapshot["explain"]
  2697	    deep_range_open = boundary_unlock_ready
  2698	    tra_lock = _build_tra_lock_payload(
  2699	        config=config,
  2700	        requested_tra_deg=requested_tra,
  2701	        effective_tra_deg=effective_tra,
  2702	        lock_deg=lock_deg,
  2703	        boundary_unlock_ready=boundary_unlock_ready,
  2704	        deep_range_open=deep_range_open,
  2705	        unlock_blockers=[condition.name for condition in lock_probe["explain"].logic4.failed_conditions],
  2706	    )
  2707	    logic1_completed = sensors.tls_unlocked_ls
  2708	    logic4_blockers = [condition.name for condition in explain.logic4.failed_conditions]
  2709	    logic3_blockers = [condition.name for condition in explain.logic3.failed_conditions]
  2710	
  2711	    nodes = [
  2712	        # ── Input sensor / signal nodes ──────────────────────────────────────
  2713	        # These are the ground-level signals; their "active" state is
  2714	        # computed to match the condition thresholds used by the logic gates.
  2715	        _node("radio_altitude_ft", "RA", "active" if inputs.radio_altitude_ft < 6.0 else "inactive",
  2716	              "Input sensors: altitude < 6 ft threshold"),
  2717	        _node("reverser_inhibited", "REV_INH",
  2718	              "inactive" if not inputs.reverser_inhibited else "active",
  2719	              "Input signals: true = inhibit active (blocked)"),
  2720	        _node("engine_running", "ENG",
  2721	              "active" if inputs.engine_running else "inactive",
  2722	              "Input signals"),
  2723	        _node("aircraft_on_ground", "GND",
  2724	              "active" if inputs.aircraft_on_ground else "inactive",
  2725	              "Input signals"),
  2726	        _node("eec_enable", "EEC_EN",
  2727	              "active" if inputs.eec_enable else "inactive",
  2728	              "Input signals"),
  2729	        _node("sw1", "SW1", "active" if inputs.sw1 else "inactive", "LatchedThrottleSwitches"),
  2730	        _node("sw2", "SW2", "active" if inputs.sw2 else "inactive", "LatchedThrottleSwitches"),
  2731	        # ── Intermediate / output nodes ────────────────────────────────────────
  2732	        _node("logic1", "L1", _logic_node_state(outputs.logic1_active), "DeployController.explain(logic1)", [condition.name for condition in explain.logic1.failed_conditions]),
  2733	        _node("tls115", "TLS115", "active" if outputs.tls_115vac_cmd or sensors.tls_unlocked_ls else "inactive", "DeployController outputs"),
  2734	        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
  2735	        _node("logic2", "L2", _logic_node_state(outputs.logic2_active), "DeployController.explain(logic2)", [condition.name for condition in explain.logic2.failed_conditions]),
  2736	        _node("etrac_540v", "540V", "active" if outputs.etrac_540vdc_cmd else "inactive", "DeployController outputs"),
  2737	        _node("logic3", "L3", _logic_node_state(outputs.logic3_active), "DeployController.explain(logic3)", logic3_blockers),
  2738	        _node("eec_deploy", "EEC", "active" if outputs.eec_deploy_cmd else "inactive", "DeployController outputs"),
  2739	        _node("pls_power", "PLS", "active" if outputs.pls_power_cmd else "inactive", "DeployController outputs"),
  2740	        _node("pdu_motor", "PDU", "active" if outputs.pdu_motor_cmd else "inactive", "DeployController outputs"),
  2741	        _node("vdt90", "VDT90", "active" if sensors.deploy_90_percent_vdt and outputs.logic3_active else "inactive", "SimplifiedDeployPlant sensors + L3 causal gate"),
  2742	        _node("logic4", "L4", _logic_node_state(outputs.logic4_active), "DeployController.explain(logic4)", logic4_blockers),
  2743	        _node(
  2744	            "thr_lock",
  2745	            "THR_LOCK",
  2746	            "active"
  2747	            if outputs.throttle_electronic_lock_release_cmd
  2748	            else (
  2749	                "blocked"
  2750	                if explain.logic4.failed_conditions
  2751	                else "inactive"
  2752	            ),
  2753	            # Use explain.logic4.failed_conditions to determine "blocked" vs "inactive".
  2754	            # This correctly handles the causal chain: when L4 is blocked (has unmet
  2755	            # conditions like tra_deg), THR_LOCK is "blocked" (waiting on L4).
  2756	            # When L4 has no failed conditions but is simply not active, THR_LOCK is "inactive".
  2757	            "DeployController outputs",
  2758	            logic4_blockers if not outputs.throttle_electronic_lock_release_cmd else [],
  2759	        ),
  2760	    ]
  2761	    summary = _lever_summary(effective_tra, inputs, sensors, outputs, explain, feedback_mode, tra_lock)
  2762	    model_note = (
  2763	        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
  2764	        if feedback_mode == "auto_scrubber"
  2765	        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"
  2766	    )
  2767	
  2768	    result = {
  2769	        "mode": (
  2770	            "canonical_pullback_scrubber"
  2771	            if feedback_mode == "auto_scrubber"
  2772	            else "manual_feedback_override"
  2773	        ),
  2774	        "model_note": model_note,
  2775	        "tra_lock": tra_lock,
  2776	        "input": {
  2777	            "requested_tra_deg": requested_tra,
  2778	            "tra_deg": effective_tra,
  2779	            "radio_altitude_ft": inputs.radio_altitude_ft,
  2780	            "engine_running": inputs.engine_running,
  2781	            "aircraft_on_ground": inputs.aircraft_on_ground,
  2782	            "reverser_inhibited": inputs.reverser_inhibited,
  2783	            "eec_enable": inputs.eec_enable,
  2784	            "n1k": inputs.n1k,
  2785	            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
  2786	            "feedback_mode": feedback_mode,
  2787	            "deploy_position_percent": deploy_position_percent,
  2788	        },
  2789	        "time_s": time_s,
  2790	        "hud": {
  2791	            "requested_tra_deg": requested_tra,
  2792	            "tra_deg": effective_tra,
  2793	            "sw1": inputs.sw1,
  2794	            "sw2": inputs.sw2,
  2795	            "radio_altitude_ft": inputs.radio_altitude_ft,
  2796	            "engine_running": inputs.engine_running,
  2797	            "aircraft_on_ground": inputs.aircraft_on_ground,
  2798	            "reverser_inhibited": inputs.reverser_inhibited,
  2799	            "eec_enable": inputs.eec_enable,
  2800	            "n1k": inputs.n1k,
  2801	            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
  2802	            "tls_unlocked_ls": sensors.tls_unlocked_ls,
  2803	            "pls_unlocked_ls": sensors.pls_unlocked_ls,
  2804	            "all_pls_unlocked_ls": sensors.all_pls_unlocked,
  2805	            "deploy_position_percent": sensors.deploy_position_percent,
  2806	            # In manual override mode: gate VDT90 display on L3 being active.
  2807	            # The user can force deploy_position_percent>=90 manually, but that
  2808	            # doesn't mean the causal chain is satisfied — VDT90 requires L3
  2809	            # (EEC deploy command) to be active first.
  2810	            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
  2811	            "feedback_mode": feedback_mode,
  2812	        },
  2813	        "outputs": {
  2814	            "logic1_active": outputs.logic1_active,
  2815	            "logic2_active": outputs.logic2_active,
  2816	            "logic3_active": outputs.logic3_active,
  2817	            "logic4_active": outputs.logic4_active,
  2818	            "tls_115vac_cmd": outputs.tls_115vac_cmd,
  2819	            "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
  2820	            "eec_deploy_cmd": outputs.eec_deploy_cmd,
  2821	            "pls_power_cmd": outputs.pls_power_cmd,
  2822	            "pdu_motor_cmd": outputs.pdu_motor_cmd,
  2823	            "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
  2824	        },
  2825	        "logic": {

codex
I have enough to issue the review. I’m doing one last memory citation lookup so the close-out can include the required continuity reference cleanly, then I’ll return the verdict with findings first.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,872p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '899,930p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
**APPROVE_WITH_NITS**

- `NIT` [demo_server.py:618](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:618) [E11-07-SURFACE-INVENTORY.md:31](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md:31): the “live constitution text / no drift risk” claim is slightly stronger than the implementation. The handler only stays live while the exact `Forbidden（红线维持` heading matches; if that heading drifts, it silently falls back to hand-written summary text. The fallback is still truthful, so this is not blocking, but it is not quite the same guarantee the docs describe.
- `NIT` [test_workbench_authority_banner.py:105](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_authority_banner.py:105): the test docstring says the route must name “the four paths,” but the assertion only requires any one of them. That under-locks the contract and would not catch a future regression that trims the red-line copy too far.

Repo-local live probe passed: `PYTHONPATH=src python3 ...` returned `200 text/plain` for `/v6.1-redline` and `/v6.1-redline.txt`, and `200 text/html` for `/workbench`. The banner copy itself is clear and unambiguous on first read [workbench.html:235](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:235), and I do not see an honesty contradiction on `/workbench`: the visible wow cards still POST, but they POST into snapshot/analysis endpoints rather than truth mutation [workbench.html:86](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:86) [workbench.js:3828](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3828) [demo_server.py:344](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:344) [demo_server.py:460](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:460) [demo_server.py:2634](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:2634). The proposal path also stays on the “propose, don’t mutate” side: annotation drafts are local proposal artifacts [annotation_overlay.js:68](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:68) [annotation_overlay.js:97](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:97), and approval remains explicitly Kogami-only [workbench.html:336](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:336) [workbench.html:350](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:350).

Truth-engine red line confirmed: `git diff --name-only main..c7131e9` only shows `.planning/...`, [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1), [workbench.css](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.css:1), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:1), and [test_workbench_authority_banner.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_authority_banner.py:1); no changes to `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`.

**P5 — Apps Engineer (Tier-B, E11-07)**

tokens used
125,719
**APPROVE_WITH_NITS**

- `NIT` [demo_server.py:618](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:618) [E11-07-SURFACE-INVENTORY.md:31](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-07-SURFACE-INVENTORY.md:31): the “live constitution text / no drift risk” claim is slightly stronger than the implementation. The handler only stays live while the exact `Forbidden（红线维持` heading matches; if that heading drifts, it silently falls back to hand-written summary text. The fallback is still truthful, so this is not blocking, but it is not quite the same guarantee the docs describe.
- `NIT` [test_workbench_authority_banner.py:105](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_authority_banner.py:105): the test docstring says the route must name “the four paths,” but the assertion only requires any one of them. That under-locks the contract and would not catch a future regression that trims the red-line copy too far.

Repo-local live probe passed: `PYTHONPATH=src python3 ...` returned `200 text/plain` for `/v6.1-redline` and `/v6.1-redline.txt`, and `200 text/html` for `/workbench`. The banner copy itself is clear and unambiguous on first read [workbench.html:235](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:235), and I do not see an honesty contradiction on `/workbench`: the visible wow cards still POST, but they POST into snapshot/analysis endpoints rather than truth mutation [workbench.html:86](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:86) [workbench.js:3828](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3828) [demo_server.py:344](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:344) [demo_server.py:460](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:460) [demo_server.py:2634](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:2634). The proposal path also stays on the “propose, don’t mutate” side: annotation drafts are local proposal artifacts [annotation_overlay.js:68](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:68) [annotation_overlay.js:97](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/annotation_overlay.js:97), and approval remains explicitly Kogami-only [workbench.html:336](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:336) [workbench.html:350](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:350).

Truth-engine red line confirmed: `git diff --name-only main..c7131e9` only shows `.planning/...`, [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1), [workbench.css](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.css:1), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:1), and [test_workbench_authority_banner.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_authority_banner.py:1); no changes to `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`.

**P5 — Apps Engineer (Tier-B, E11-07)**

