2026-04-25T19:00:58.382134Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T19:00:58.382207Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc604-378f-7521-a72d-bc47abb677de
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B single-persona pipeline, E11-15 sub-phase).

# Context — E11-15 Chinese-first eyebrow sweep

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15-chinese-eyebrow-sweep-20260426`
**PR:** #24
**Worktree HEAD:** `440c9ba` (single commit on top of main `8c557f3`)

## What E11-15 ships

5 eyebrow labels above non-bilingual h1/h2s flipped from English-lowercase to pure Chinese so the page reads Chinese-first at a glance:

| File:Line | Before | After |
|---|---|---|
| `workbench.html:17` | `control logic workbench` | `控制逻辑工作台` |
| `workbench.html:62` | `state of world` | `当前现状` |
| `workbench.html:97` | `canonical scenarios` | `主流场景` |
| `workbench.html:333` | `annotation inbox` | `标注收件箱` |
| `workbench.html:379` | `approval center` | `审批中心` |

The 3 column-trio eyebrows (`probe & trace` / `annotate & propose` / `hand off & track`) are intentionally preserved — they live above bilingual h2 titles which already provide Chinese-first signal at the h2 line, and they are positively locked by `tests/test_workbench_column_rename.py`. E11-15 explicitly does NOT touch them.

## Files in scope

- `src/well_harness/static/workbench.html` — 5 eyebrow strings flipped (lines 17, 62, 97, 333, 379)
- `tests/test_workbench_chinese_eyebrow_sweep.py` — NEW (22 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

## Your specific lens (P2 Senior FCS Engineer)

Focus on:
- **Visible-copy consistency**: do the 5 new Chinese strings work harmoniously with their surrounding h1/h2/body copy? Is the page a coherent Chinese-first read, or does any eyebrow read awkwardly against its neighbors?
- **Structural-anchor preservation**: are the CSS class hooks (`eyebrow`, `workbench-sow-eyebrow`) untouched? Are the section IDs and h1/h2 strings unchanged?
- **Test completeness**: does the new test file lock both (a) presence of the 5 new strings AND (b) absence of the 5 old strings AND (c) preservation of the 3 out-of-scope column eyebrows?
- **Out-of-scope discipline**: is the sweep correctly bounded to ONLY the 5 in-scope eyebrows, or did it leak into the column trio / h2 strings / approval-flow buttons?
- **Truth-engine red line**: confirm zero changes to `controller.py`/`runner.py`/`models.py`/`adapters/`, and zero changes to `workbench.js` / `workbench.css`.
- **Translation quality**: is `当前现状` the right rendering of `state of world` in this state-of-world status-bar context (vs. `世界状态` or `当前状态`)? Same question for the other 4.

## Verification status

- 1035 / 1035 pytest pass (22 new in `test_workbench_chinese_eyebrow_sweep.py`; full suite green)
- Truth-engine red line preserved: `git diff --name-only main..440c9ba` shows only `.planning/...`, `src/well_harness/static/workbench.html`, `tests/test_workbench_chinese_eyebrow_sweep.py`

## Out of scope (deliberately deferred)

- h1 `Control Logic Workbench` and h2s `Review Queue`, `Kogami Proposal Triage` reformatting to bilingual — separate sub-phase
- The 3 column-trio eyebrows — locked by E11-03 + already bilingual at h2 line
- `Approval Center` button text + Kogami-only caption — functional approval-flow strings, separate sub-phase
- `workbench.js` / `workbench.css` — pure HTML sweep

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path (e.g., `/workbench` route serving the new Chinese eyebrows). Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..440c9ba` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/` / `workbench.js` / `workbench.css`.

Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-15)**
codex
Reviewing the E11-15 slice as a code review, with focus on copy coherence, scope containment, structural anchors, and the truth-engine red line. I’m pulling the repo state, relevant review workflow notes, and the exact HTML/tests diff before I probe the served `/workbench` path.
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

exec
/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|E11|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'git status --short --branch' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
## feat/e11-15-chinese-eyebrow-sweep-20260426
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt

codex
Using `gsd-code-review` for the review structure and a light memory pass only for this repo’s launch context. Next I’m checking the exact diff, the HTML neighborhood around the five changed eyebrows, and the new tests that are supposed to bound the sweep.
Reviewing a bounded UI-copy PR: verify scope, inspect changed HTML/tests/planning artifacts, confirm red-line diff boundaries, run targeted tests, and live-probe the served workbench route.
  → Inspect git diff and changed files for E11-15 scope and anchor preservation
  • Review new HTML copy in surrounding context and assess translation quality
  • Review tests for presence/absence/preservation coverage and run targeted pytest
  • Live-probe the served /workbench path and confirm rendered Chinese eyebrows
  • Summarize verdict with severity-tagged findings and citations
exec
/bin/zsh -lc 'git diff --name-only main..HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
tests/test_workbench_chinese_eyebrow_sweep.py

exec
/bin/zsh -lc 'git diff --stat main..HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-15-SURFACE-INVENTORY.md                    |  87 +++++++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/static/workbench.html             |  10 +-
 tests/test_workbench_chinese_eyebrow_sweep.py      | 160 +++++++++++++++++++++
 4 files changed, 253 insertions(+), 5 deletions(-)

exec
/bin/zsh -lc "sed -n '1,240p' tests/test_workbench_chinese_eyebrow_sweep.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,260p' tests/test_workbench_column_rename.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
"""E11-15 — Chinese-first eyebrow sweep.

The 5 eyebrow labels that did NOT carry a bilingual h2 below them are
flipped from English-lowercase to pure Chinese, so that the page
reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
annotate & propose, hand off & track) are explicitly out of scope —
they are positively locked by E11-03 tests and the bilingual h2 below
each already provides Chinese-first signal.

Default state preserves all existing IDs, classes, and h1/h2 strings.
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


# ─── 1. New Chinese eyebrows are POSITIVELY locked ───────────────────


@pytest.mark.parametrize(
    "eyebrow_html",
    [
        '<p class="eyebrow">控制逻辑工作台</p>',
        '<span class="workbench-sow-eyebrow">当前现状</span>',
        '<p class="eyebrow">主流场景</p>',
        '<p class="eyebrow">标注收件箱</p>',
        '<p class="eyebrow">审批中心</p>',
    ],
)
def test_workbench_html_carries_chinese_eyebrow(eyebrow_html: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"


# ─── 2. Old English-only eyebrows are gone ───────────────────────────


@pytest.mark.parametrize(
    "stale_eyebrow_html",
    [
        '<p class="eyebrow">control logic workbench</p>',
        '<span class="workbench-sow-eyebrow">state of world</span>',
        '<p class="eyebrow">canonical scenarios</p>',
        '<p class="eyebrow">annotation inbox</p>',
        '<p class="eyebrow">approval center</p>',
    ],
)
def test_workbench_html_does_not_carry_stale_english_eyebrow(stale_eyebrow_html: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale_eyebrow_html not in html, (
        f"stale English-only eyebrow still present: {stale_eyebrow_html}"
    )


# ─── 3. Out-of-scope eyebrows (E11-03 column trio) are PRESERVED ─────


@pytest.mark.parametrize(
    "preserved_eyebrow",
    [
        '<p class="eyebrow">probe &amp; trace</p>',
        '<p class="eyebrow">annotate &amp; propose</p>',
        '<p class="eyebrow">hand off &amp; track</p>',
    ],
)
def test_e11_03_column_eyebrows_preserved(preserved_eyebrow: str) -> None:
    """E11-15 explicitly does NOT touch the column-trio eyebrows.
    They live above bilingual h2s and are locked by test_workbench_column_rename."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_eyebrow in html, (
        f"E11-03 column eyebrow accidentally removed by E11-15 sweep: {preserved_eyebrow}"
    )


# ─── 4. Anchors and h1/h2 strings preserved ──────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        # h1/h2 main titles untouched
        "<h1>Control Logic Workbench</h1>",
        # IDs of containing sections untouched
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'id="annotation-inbox"',
        'id="approval-center-panel"',
        # Class hooks untouched (CSS still binds)
        'class="eyebrow"',
        'class="workbench-sow-eyebrow"',
    ],
)
def test_e11_15_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15 sweep accidentally broke structural anchor: {anchor}"


# ─── 5. Live-served route reflects the sweep ─────────────────────────


def test_workbench_route_serves_chinese_eyebrows(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert "控制逻辑工作台" in html
    assert "当前现状" in html
    assert "主流场景" in html
    assert "标注收件箱" in html
    assert "审批中心" in html


# ─── 6. Truth-engine red line ────────────────────────────────────────


def test_e11_15_only_touches_static_html() -> None:
    """The sweep is HTML-only — no JS, no CSS, no controller, no adapter.
    Verify by spot-checking that the 5 changed strings appear nowhere
    else in code-bearing files."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    # The new Chinese strings live only in HTML, not JS or CSS.
    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
        assert chinese not in js, f"unexpected Chinese eyebrow leaked into workbench.js: {chinese}"
        assert chinese not in css, f"unexpected Chinese eyebrow leaked into workbench.css: {chinese}"

 succeeded in 0ms:
"""E11-03 — three-column rename regression lock.

Locks the visible column titles, eyebrows, and boot status copy after
the E11-03 rename from technical nouns to engineer-task verbs:

  Scenario Control          → Probe & Trace · 探针与追踪
  Spec Review Surface       → Annotate & Propose · 标注与提案
  Logic Circuit Surface     → Hand off & Track · 移交与跟踪

Per E11-00-PLAN row E11-03: underlying IDs (data-column, panel ids,
data-annotation-surface) are intentionally stable so e2e selectors and
JS boot wiring don't break. Verify both invariants — new copy AND
preserved IDs — so a future "polish" pass can't silently regress
either side.
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


# ─── 1. New visible copy is present ──────────────────────────────────


@pytest.mark.parametrize(
    "title",
    [
        "Probe &amp; Trace · 探针与追踪",
        "Annotate &amp; Propose · 标注与提案",
        "Hand off &amp; Track · 移交与跟踪",
    ],
)
def test_workbench_html_carries_new_column_title(title: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert title in html, f"missing renamed column title: {title}"


@pytest.mark.parametrize(
    "eyebrow",
    ["probe &amp; trace", "annotate &amp; propose", "hand off &amp; track"],
)
def test_workbench_html_carries_new_eyebrow(eyebrow: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert eyebrow in html, f"missing renamed eyebrow: {eyebrow}"


# ─── 2. Old technical-noun copy removed ──────────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        "<h2>Scenario Control</h2>",
        "<h2>Spec Review Surface</h2>",
        "<h2>Logic Circuit Surface</h2>",
        ">control panel<",
        ">document<",
        ">circuit<",
        "Waiting for control panel boot.",
        "Waiting for document panel boot.",
        "Waiting for circuit panel boot.",
    ],
)
def test_workbench_html_does_not_carry_stale_column_title(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale technical-noun copy still present: {stale}"


# ─── 2b. New pre-hydration boot-status copy is POSITIVELY locked ──────
#
# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
# pre-hydration "Waiting for ... panel boot." strings. R1 only verified
# absence of the stale copy; R2 also asserts presence of the new copy
# so a drift to any other phrasing would fail the suite.


@pytest.mark.parametrize(
    "boot_status",
    [
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_workbench_html_carries_new_boot_status(boot_status: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert boot_status in html, f"missing renamed pre-hydration boot status: {boot_status}"


# ─── 3. Underlying IDs / data attributes preserved ──────────────────
#
# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
# panel ids, data-column tokens, data-annotation-surface tokens, and
# status div ids are anchors for e2e selectors and JS boot wiring, so
# they MUST stay stable through the rename.


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-control-panel"',
        'id="workbench-document-panel"',
        'id="workbench-circuit-panel"',
        'data-column="control"',
        'data-column="document"',
        'data-column="circuit"',
        'data-annotation-surface="control"',
        'data-annotation-surface="document"',
        'data-annotation-surface="circuit"',
        'id="workbench-control-status"',
        'id="workbench-document-status"',
        'id="workbench-circuit-status"',
    ],
)
def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"


# ─── 4. JS boot status copy matches new column names ────────────────


# P4 R1 NIT fix: lock the FULL hydrated boot-status sentence (not just
# the "X ready" prefix), so future drift in the staging note is also
# caught. P5 R1 IMPORTANT fix: the strings must NOT contain internal
# roadmap tokens like "E07+" or "E07".


@pytest.mark.parametrize(
    "boot_copy",
    [
        "Probe & Trace ready. Scenario actions are staged for the next bundle.",
        "Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
        "Hand off & Track ready. Overlay annotation is staged for the next bundle.",
    ],
)
def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert boot_copy in js, f"workbench.js boot status missing exact string: {boot_copy}"


def test_workbench_js_boot_status_drops_stale_names() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Old boot copy must NOT appear, otherwise the visible chrome and the
    # status messages will disagree.
    assert "Control panel ready" not in js
    assert "Document panel ready" not in js
    assert "Circuit panel ready" not in js


def test_workbench_js_boot_status_drops_internal_phase_tokens() -> None:
    """P5 R1 IMPORTANT fix: roadmap tokens like 'E07+'/'E07' must not
    leak into user-visible boot status strings."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Scope the check to the three boot functions to avoid false
    # positives in unrelated comments/blocks.
    for fn in (
        "bootWorkbenchControlPanel",
        "bootWorkbenchDocumentPanel",
        "bootWorkbenchCircuitPanel",
    ):
        anchor = js.find(f"function {fn}")
        assert anchor != -1, f"missing function {fn}"
        slice_ = js[anchor : anchor + 600]
        assert "E07" not in slice_, (
            f"internal phase token 'E07' leaked into {fn} boot status"
        )


# P1 R1 NIT fix: failure-path fallback must use the engineer-task verb,
# not the internal columnName token.


def test_workbench_js_failure_fallback_uses_task_verb_label() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # WORKBENCH_COLUMN_LABEL maps control/document/circuit → task verbs
    assert "WORKBENCH_COLUMN_LABEL" in js
    assert '"control": "Probe & Trace"' in js or 'control: "Probe & Trace"' in js
    assert '"document": "Annotate & Propose"' in js or 'document: "Annotate & Propose"' in js
    assert '"circuit": "Hand off & Track"' in js or 'circuit: "Hand off & Track"' in js
    # Failure copy must reference the label, not the raw columnName.
    assert "${label} panel failed independently" in js, (
        "failure fallback should use the engineer-task verb label, not the raw column token"
    )


# ─── 5. Live-served /workbench reflects the rename end-to-end ───────


def test_workbench_route_serves_renamed_columns(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # New copy
    assert "Probe &amp; Trace · 探针与追踪" in html
    assert "Annotate &amp; Propose · 标注与提案" in html
    assert "Hand off &amp; Track · 移交与跟踪" in html
    # Stable anchors still served
    assert 'id="workbench-control-panel"' in html
    assert 'data-column="circuit"' in html

exec
/bin/zsh -lc 'git diff --unified=20 main..HEAD -- src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 00d4ce7..0f30743 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -1,37 +1,37 @@
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
-          <p class="eyebrow">control logic workbench</p>
+          <p class="eyebrow">控制逻辑工作台</p>
           <h1>Control Logic Workbench</h1>
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
@@ -42,76 +42,76 @@
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
-        <span class="workbench-sow-eyebrow">state of world</span>
+        <span class="workbench-sow-eyebrow">当前现状</span>
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
-          <p class="eyebrow">canonical scenarios</p>
+          <p class="eyebrow">主流场景</p>
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
@@ -313,41 +313,41 @@
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
-          <p class="eyebrow">annotation inbox</p>
+          <p class="eyebrow">标注收件箱</p>
           <h2>Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
           <li>No proposals submitted yet.</li>
         </ul>
       </aside>
 
       <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
         <button
           id="approval-center-entry"
           type="button"
           class="workbench-toolbar-button"
           data-role="KOGAMI"
           aria-controls="approval-center-panel"
         >
           Approval Center
         </button>
         <span>Approval actions are Kogami-only.</span>
       </footer>
 
@@ -359,41 +359,41 @@
         data-pending-signoff="hidden"
       >
         <span class="workbench-pending-signoff-icon" aria-hidden="true">🛈</span>
         <div class="workbench-pending-signoff-body">
           <strong>Pending Kogami sign-off</strong>
           <span>
             你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属
             authority — 你的角色当前不会看到 disabled UI，而是这条 explicit
             "排队中" 提示。
           </span>
         </div>
       </section>
 
       <section
         id="approval-center-panel"
         class="workbench-approval-center"
         data-approval-role="KOGAMI"
         aria-labelledby="approval-center-title"
       >
         <header>
-          <p class="eyebrow">approval center</p>
+          <p class="eyebrow">审批中心</p>
           <h2 id="approval-center-title">Kogami Proposal Triage</h2>
         </header>
         <div class="workbench-approval-grid">
           <article class="workbench-approval-lane" data-approval-lane="pending">
             <h3>Pending</h3>
             <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
           </article>
           <article class="workbench-approval-lane" data-approval-lane="accept">
             <h3>Accept</h3>
             <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
           </article>
           <article class="workbench-approval-lane" data-approval-lane="reject">
             <h3>Reject</h3>
             <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
           </article>
         </div>
       </section>
 
       <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
     </main>

codex
The diff is still tightly bounded to four files, and the HTML patch only flips the five eyebrow nodes the prompt called out. I’m pulling exact line numbers now and then I’ll run the targeted pytest slice plus a direct HTTP probe against `/workbench` to verify the served page matches the static file.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '10,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    10	    <link rel="stylesheet" href="/demo.css">
    11	    <link rel="stylesheet" href="/workbench.css">
    12	  </head>
    13	  <body data-view="beginner">
    14	    <main class="shell workbench-shell">
    15	      <section id="workbench-topbar" class="workbench-collab-topbar" aria-label="Workbench identity and routing">
    16	        <div class="workbench-collab-brand">
    17	          <p class="eyebrow">控制逻辑工作台</p>
    18	          <h1>Control Logic Workbench</h1>
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

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '320,400p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   334	          <h2>Review Queue</h2>
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
   349	          Approval Center
   350	        </button>
   351	        <span>Approval actions are Kogami-only.</span>
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
   380	          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
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

exec
/bin/zsh -lc "nl -ba tests/test_workbench_column_rename.py | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_eyebrow_sweep.py | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   118	        # h1/h2 main titles untouched
   119	        "<h1>Control Logic Workbench</h1>",
   120	        # IDs of containing sections untouched
   121	        'id="workbench-state-of-world-bar"',
   122	        'id="workbench-wow-starters"',
   123	        'id="annotation-inbox"',
   124	        'id="approval-center-panel"',
   125	        # Class hooks untouched (CSS still binds)
   126	        'class="eyebrow"',
   127	        'class="workbench-sow-eyebrow"',
   128	    ],
   129	)
   130	def test_e11_15_preserves_structural_anchors(anchor: str) -> None:
   131	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   132	    assert anchor in html, f"E11-15 sweep accidentally broke structural anchor: {anchor}"
   133	
   134	
   135	# ─── 5. Live-served route reflects the sweep ─────────────────────────
   136	
   137	
   138	def test_workbench_route_serves_chinese_eyebrows(server) -> None:
   139	    status, html = _get(server, "/workbench")
   140	    assert status == 200
   141	    assert "控制逻辑工作台" in html
   142	    assert "当前现状" in html
   143	    assert "主流场景" in html
   144	    assert "标注收件箱" in html
   145	    assert "审批中心" in html
   146	
   147	
   148	# ─── 6. Truth-engine red line ────────────────────────────────────────
   149	
   150	
   151	def test_e11_15_only_touches_static_html() -> None:
   152	    """The sweep is HTML-only — no JS, no CSS, no controller, no adapter.
   153	    Verify by spot-checking that the 5 changed strings appear nowhere
   154	    else in code-bearing files."""
   155	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   156	    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
   157	    # The new Chinese strings live only in HTML, not JS or CSS.
   158	    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
   159	        assert chinese not in js, f"unexpected Chinese eyebrow leaked into workbench.js: {chinese}"
   160	        assert chinese not in css, f"unexpected Chinese eyebrow leaked into workbench.css: {chinese}"

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

codex
The file-level review is consistent with the prompt so far: the five target nodes changed, the trio columns stayed intact, and the class/id anchors are still there. I’m verifying it with the repo’s own tests now and then doing a real HTTP fetch from a local server, not just static-file inspection.
exec
/bin/zsh -lc 'python -m pytest tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_column_rename.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'rg -n "if __name__ ==|DemoRequestHandler|ThreadingHTTPServer|/workbench|serve_forever|demo_server" src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
14:from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
71:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
72:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
73:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
74:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
75:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
77:WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
203:class DemoRequestHandler(BaseHTTPRequestHandler):
231:            # /workbench top-of-page status bar. Read-only — never mutates
249:        if parsed.path in ("/workbench/start", "/workbench/start.html"):
253:        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
257:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
1426:    """E11-06: aggregate read-only fields for the /workbench status bar.
2888:    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
2895:        server.serve_forever()
2903:if __name__ == "__main__":

codex
The first test attempt exposed an environment fact, not a product issue: this shell has no `python` shim, so I’m switching to `python3`. I’m also confirming the repo’s demo server entrypoint so the live probe uses the actual `/workbench` route handler instead of a synthetic file server.
exec
/bin/zsh -lc "sed -n '2860,2915p' src/well_harness/demo_server.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    parser.add_argument(
        "--open",
        action="store_true",
        help=(
            "Open the local UI URL with Python's standard-library webbrowser.open; "
            "this is a launch convenience, not browser E2E automation."
        ),
    )
    return parser


def demo_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/index.html"


def open_browser(url: str, opener=webbrowser.open) -> bool:
    try:
        opened = bool(opener(url))
    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
        return False
    if not opened:
        print(f"Could not open browser automatically. Open {url} manually.")
    return opened


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
    host, port = server.server_address
    url = demo_url(host, port)
    print(f"Serving well-harness demo UI at {url}")
    if args.open:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping well-harness demo UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

exec
/bin/zsh -lc 'python3 -m pytest tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_column_rename.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 1320ms:
...........................................................              [100%]
59 passed in 1.07s

codex
The bounded regression slice passed locally: `59 passed` across the new E11-15 test file plus the existing E11-03 guardrail. I’m doing two last checks now: an explicit `main..440c9ba` red-line diff, and a real `/workbench` HTTP fetch through `DemoRequestHandler` so the verdict cites a served page, not just static HTML.
exec
/bin/zsh -lc 'git rev-parse --short HEAD && git diff --name-only main..440c9ba' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
440c9ba
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
tests/test_workbench_chinese_eyebrow_sweep.py

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '899,933p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import http.client
import threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    conn.request('GET', '/workbench')
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    print(f'status={resp.status}')
    print(f'port={server.server_port}')
    for token in ['控制逻辑工作台', '当前现状', '主流场景', '标注收件箱', '审批中心']:
        print(f'{token}={token in body}')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 578ms:
status=200
port=49211
控制逻辑工作台=True
当前现状=True
主流场景=True
标注收件箱=True
审批中心=True

codex
The live route probe is clean: `DemoRequestHandler` served `/workbench` with HTTP 200, and all five Chinese eyebrows were present in the response body. I’m doing one last pass over the inventory artifact to make sure the documentation of scope matches the code and tests, then I’ll issue the review verdict.
exec
/bin/zsh -lc "sed -n '1,240p' .planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15 Surface Inventory — Chinese-first eyebrow sweep

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Scope rationale

Workbench has 8 eyebrow labels, all originally English-lowercase. 3 of them
(probe & trace / annotate & propose / hand off & track) are positively
locked by `tests/test_workbench_column_rename.py` and live above bilingual
h2 titles (`Probe & Trace · 探针与追踪`, etc.) — so the column trio already
provides Chinese-first signal at the h2 line and is intentionally
out-of-scope for this sweep.

The remaining 5 eyebrows live above either an English h1 (`Control Logic
Workbench`) or an English h2 (`Review Queue`, `Kogami Proposal Triage`)
or no h2 at all (state-of-world bar, canonical scenarios), and read
English-first at a glance. E11-15 flips them to pure Chinese so the page
reads Chinese-first across every section header. The h1/h2 strings
themselves are NOT touched (separate sub-phase if reformatting them is
desired).

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Page eyebrow `control logic workbench` → `控制逻辑工作台` | [REWRITE] | `workbench.html:17` | Top-of-page brand eyebrow above `<h1>Control Logic Workbench</h1>`. |
| 2 | State-of-world eyebrow `state of world` → `当前现状` | [REWRITE] | `workbench.html:62` | First label inside `#workbench-state-of-world-bar`. |
| 3 | Starters eyebrow `canonical scenarios` → `主流场景` | [REWRITE] | `workbench.html:97` | Above `<h2>起手卡 · One-click 走读</h2>`. |
| 4 | Annotation inbox eyebrow `annotation inbox` → `标注收件箱` | [REWRITE] | `workbench.html:333` | Above `<h2>Review Queue</h2>`. |
| 5 | Approval center eyebrow `approval center` → `审批中心` | [REWRITE] | `workbench.html:379` | Above `<h2 id="approval-center-title">Kogami Proposal Triage</h2>`. |

## Out of scope (preserved)

- **Column-trio eyebrows** (`probe & trace`, `annotate & propose`,
  `hand off & track`) — locked by E11-03 tests; bilingual h2 below
  already gives Chinese-first signal.
- **All h1/h2 strings** — reformatting from English-only to bilingual
  (e.g. `Review Queue` → `审核队列 · Review Queue`) is a separate
  sub-phase and would push this sweep to Tier-A.
- **`Approval Center` button text + Kogami-only caption** — functional
  approval-flow strings; deferred to a focused E11-XX sub-phase.
- **`workbench.js`, `workbench.css`** — pure HTML sweep; no
  selector/string drift.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 5 → < 10
- **[REWRITE/DELETE] count** = 5 → ≥ 3

→ **Tier-B** (1-persona review). The first threshold (≥10) fails, so
even with all 5 lines being [REWRITE], the sub-phase stays Tier-B.

> **Verdict: Tier-B**. Persona = **P2 (Senior FCS Engineer)** — round-robin
> successor of E11-08's P1. P3 (Demo Presenter) would also fit content-wise
> (typography/reading-rhythm), but P3 has been used twice recently
> (E11-04, E11-05) so round-robin default applies. Senior FCS reviews
> visible-copy consistency + structural-anchor preservation, which is
> exactly the lens this sweep needs.

## Behavior contract (locked by tests)

`tests/test_workbench_chinese_eyebrow_sweep.py` (NEW, 22 tests):

1. Each of the 5 new Chinese eyebrow strings is positively asserted.
2. Each of the 5 stale English eyebrow strings is asserted absent.
3. The 3 E11-03 column eyebrows are asserted preserved.
4. h1, section IDs, and CSS class hooks (`eyebrow`, `workbench-sow-eyebrow`)
   are asserted unchanged.
5. Live-served `/workbench` route returns the new Chinese eyebrows.
6. The 5 new Chinese strings do NOT leak into `workbench.js` or
   `workbench.css` (HTML-only sweep).

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 5 eyebrow strings flipped
- `tests/test_workbench_chinese_eyebrow_sweep.py` — NEW (22 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`. Truth-engine
boundary preserved. No new endpoints; no backend changes.

exec
/bin/zsh -lc 'git diff --unified=10 main..HEAD -- .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
index e73c364..4e1b1b0 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
@@ -9,10 +9,11 @@
 ## Sequence
 
 E11-13: P1 (round-robin start; first Tier-B sub-phase under bundle #2)
 E11-14: P2 (round-robin successor; Senior FCS Engineer fits server-side / API contract review)
 E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html corrections + 12 ANCHORED card copy lines). All 5 personas dispatched. Rotation pointer unchanged (Tier-A does not consume a Tier-B slot).
 E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
 E11-04: Tier-B (7 copy_diff_lines, fails ≥10 threshold; though 7 [REWRITE] meets ≥3). Persona = P3 (Demo Presenter — content-fit for domain vocabulary the engineer reads on screen; also the round-robin successor of P2). Plan row 275 said "NO Codex (mechanical relabel)" but the constitution Tier-B rule is the stricter SSOT.
 E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE] — all NEW section content fails ≥3 threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit for new endpoint contract validation).
 E11-07: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE] — pure-NEW banner). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit for customer/repro-facing authority contract messaging).
 E11-08: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE]). Persona = P1 (Junior FCS Engineer — round-robin wraps P5 → P1 AND content-fit for small UI-only refactor with regression-risk JS attribute reading + URL-param parsing).
+E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).

codex
One subtle area remained after the main verification: whether the new regression file really locks all of the “unchanged h1/h2” contract it claims. I’m searching the suite for those three untouched h2 strings before I finalize the verdict, because that decides whether this is a clean approve or an approve-with-nit about test precision.
exec
/bin/zsh -lc 'rg -n "起手卡 · One-click 走读|Review Queue|Kogami Proposal Triage|Control Logic Workbench" tests src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:6:    <title>Control Logic Workbench</title>
src/well_harness/static/workbench.html:18:          <h1>Control Logic Workbench</h1>
src/well_harness/static/workbench.html:98:          <h2>起手卡 · One-click 走读</h2>
src/well_harness/static/workbench.html:334:          <h2>Review Queue</h2>
src/well_harness/static/workbench.html:380:          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
tests/test_workbench_start.py:206:    assert "Control Logic Workbench" in body
tests/test_workbench_dual_route.py:4:TWO `<h1>` headings: "Control Logic Workbench" (Epic-06..10 shell) +
tests/test_workbench_dual_route.py:9:- `/workbench` serves shell only (1 h1: "Control Logic Workbench")
tests/test_workbench_dual_route.py:61:    assert "<title>Control Logic Workbench</title>" in body
tests/test_workbench_dual_route.py:64:    assert "Control Logic Workbench</h1>" in body
tests/test_workbench_dual_route.py:90:    assert "Control Logic Workbench</h1>" not in body
tests/test_workbench_dual_route.py:103:    assert "Control Logic Workbench</h1>" in shell_html
tests/test_workbench_dual_route.py:107:    assert "Control Logic Workbench</h1>" not in bundle_html
tests/test_workbench_shell.py:59:    assert "Control Logic Workbench" in html
tests/test_workbench_chinese_eyebrow_sweep.py:119:        "<h1>Control Logic Workbench</h1>",

exec
/bin/zsh -lc 'rg -n "当前现状|主流场景|标注收件箱|审批中心|控制逻辑工作台" src/well_harness/static/workbench.js src/well_harness/static/workbench.css src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters tests' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_chinese_eyebrow_sweep.py:60:        '<p class="eyebrow">控制逻辑工作台</p>',
tests/test_workbench_chinese_eyebrow_sweep.py:61:        '<span class="workbench-sow-eyebrow">当前现状</span>',
tests/test_workbench_chinese_eyebrow_sweep.py:62:        '<p class="eyebrow">主流场景</p>',
tests/test_workbench_chinese_eyebrow_sweep.py:63:        '<p class="eyebrow">标注收件箱</p>',
tests/test_workbench_chinese_eyebrow_sweep.py:64:        '<p class="eyebrow">审批中心</p>',
tests/test_workbench_chinese_eyebrow_sweep.py:141:    assert "控制逻辑工作台" in html
tests/test_workbench_chinese_eyebrow_sweep.py:142:    assert "当前现状" in html
tests/test_workbench_chinese_eyebrow_sweep.py:143:    assert "主流场景" in html
tests/test_workbench_chinese_eyebrow_sweep.py:144:    assert "标注收件箱" in html
tests/test_workbench_chinese_eyebrow_sweep.py:145:    assert "审批中心" in html
tests/test_workbench_chinese_eyebrow_sweep.py:158:    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:

exec
/bin/zsh -lc 'rg -n "probe &amp; trace|annotate &amp; propose|hand off &amp; track|Review Queue|Kogami Proposal Triage|起手卡 · One-click 走读" src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
98:          <h2>起手卡 · One-click 走读</h2>
274:            <p class="eyebrow">probe &amp; trace</p>
278:            Waiting for probe &amp; trace panel boot.
294:            <p class="eyebrow">annotate &amp; propose</p>
298:            Waiting for annotate &amp; propose panel boot.
314:            <p class="eyebrow">hand off &amp; track</p>
318:            Waiting for hand off &amp; track panel boot.
334:          <h2>Review Queue</h2>
380:          <h2 id="approval-center-title">Kogami Proposal Triage</h2>

Completed diff review, copy/context inspection, targeted regression run, explicit main..440c9ba red-line diff, and a live /workbench route probe through DemoRequestHandler.
  ✓ Inspect git diff and changed files for E11-15 scope and anchor preservation
  ✓ Review new HTML copy in surrounding context and assess translation quality
  ✓ Review tests for presence/absence/preservation coverage and run targeted pytest
  ✓ Live-probe the served /workbench path and confirm rendered Chinese eyebrows
  → Summarize verdict with severity-tagged findings and citations
codex
**APPROVE_WITH_NITS**

- `NIT` — [test_workbench_chinese_eyebrow_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_eyebrow_sweep.py:115): section 4 says the sweep preserves h1/h2 strings, but the assertions only lock the h1 plus ids/classes. The unchanged h2s at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:98), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:334), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:380) are not explicitly locked. The “truth-engine red line” block at [test_workbench_chinese_eyebrow_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_eyebrow_sweep.py:151) also only proves no JS/CSS string leak, not the broader “no controller/adapter changes” claim in its docstring.

The shipped HTML slice itself is clean. The five in-scope eyebrows changed exactly where intended at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:62), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:97), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:333), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:379). The out-of-scope trio remained intact at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:274), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:294), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:314), consistent with [test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:74). `eyebrow` / `workbench-sow-eyebrow` hooks and section ids are untouched.

Translation quality is acceptable. `控制逻辑工作台`, `标注收件箱`, and `审批中心` read naturally against their neighboring copy. `当前现状` is the right rendering for this advisory status-bar context; `世界状态` is too literal, and `当前状态` is more easily confused with a concrete system state. `主流场景` works, though `典型场景` would be a slightly tighter rendering of “canonical scenarios” if you revisit copy later.

Verification was solid: `python3 -m pytest tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_column_rename.py -q` passed with `59 passed in 1.07s`. Live probe through `DemoRequestHandler` returned `GET /workbench -> 200` on `127.0.0.1:49211`, and the served HTML contained all five new Chinese eyebrows. `git diff --name-only main..440c9ba` only lists the two planning files, `workbench.html`, and the new eyebrow test file, so the truth-engine red line is preserved: no changes to `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, or `workbench.css`.

**P2 — Senior FCS Engineer (Tier-B, E11-15)**


tokens used
57,559
**APPROVE_WITH_NITS**

- `NIT` — [test_workbench_chinese_eyebrow_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_eyebrow_sweep.py:115): section 4 says the sweep preserves h1/h2 strings, but the assertions only lock the h1 plus ids/classes. The unchanged h2s at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:98), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:334), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:380) are not explicitly locked. The “truth-engine red line” block at [test_workbench_chinese_eyebrow_sweep.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_eyebrow_sweep.py:151) also only proves no JS/CSS string leak, not the broader “no controller/adapter changes” claim in its docstring.

The shipped HTML slice itself is clean. The five in-scope eyebrows changed exactly where intended at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:17), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:62), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:97), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:333), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:379). The out-of-scope trio remained intact at [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:274), [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:294), and [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:314), consistent with [test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:74). `eyebrow` / `workbench-sow-eyebrow` hooks and section ids are untouched.

Translation quality is acceptable. `控制逻辑工作台`, `标注收件箱`, and `审批中心` read naturally against their neighboring copy. `当前现状` is the right rendering for this advisory status-bar context; `世界状态` is too literal, and `当前状态` is more easily confused with a concrete system state. `主流场景` works, though `典型场景` would be a slightly tighter rendering of “canonical scenarios” if you revisit copy later.

Verification was solid: `python3 -m pytest tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_column_rename.py -q` passed with `59 passed in 1.07s`. Live probe through `DemoRequestHandler` returned `GET /workbench -> 200` on `127.0.0.1:49211`, and the served HTML contained all five new Chinese eyebrows. `git diff --name-only main..440c9ba` only lists the two planning files, `workbench.html`, and the new eyebrow test file, so the truth-engine red line is preserved: no changes to `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, or `workbench.css`.

**P2 — Senior FCS Engineer (Tier-B, E11-15)**


