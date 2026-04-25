2026-04-25T17:26:13.541594Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T17:26:13.541665Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc5ad-7926-7d31-a858-192744c7e8d5
--------
user
You are Codex GPT-5.4 acting as **Persona P4 — V&V Engineer** (Tier-A 5-persona pipeline, E11-03 sub-phase).

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

Focus on: test coverage maps to claims — every visible string locked, every stale string asserted absent, every stable anchor asserted present, JS boot copy in lockstep.

Read the files listed under "Files in scope" (full). Form an independent verdict from your persona's perspective.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items (E11-15 polish, separate sub-phases, backend) → NIT/INFO only.

Live-probe at least one path you're unsure about (e.g. boot demo_server, GET /workbench, verify rendered text). Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..2df105c` shows only the 4 in-scope path types listed above.

Sign as: **P4 — V&V Engineer (Tier-A, E11-03)**
codex
我会按 P4 验证视角做独立审查：先快速过记忆和仓库状态，再读取变更文件、跑 truth-engine red line 检查，并做一次实际 `/workbench` live probe 来核对渲染文本与 boot 文案是否一致。
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

exec
/bin/zsh -lc 'rg -n "LogicMVP|E11-03|workbench|column rename|feat/e11-03" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'pwd && git rev-parse --abbrev-ref HEAD && git rev-parse --short HEAD && git status --short && git merge-base main HEAD && git rev-parse --short main' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
feat/e11-03-column-rename-20260426
2df105c
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-prompt.txt
?? uv.lock
18fdb4622e02eccffa1fa13aa900696bc081f56e
18fdb46

codex
使用 `using-superpowers` 和 `gsd-code-review` 的最小流程来约束这次审查：我不会改代码，只做证据化核对，重点盯住字符串锁定、陈旧文案缺失、稳定锚点不变，以及 `main..HEAD` 的真实变更边界。
P4 review will verify scope, inspect each in-scope file, run targeted verification, and then produce a findings-first verdict.
  → Confirm branch/head and truth-engine red line against main
  • Read all in-scope files and diff to map claims to code/tests
  • Run targeted verification including live /workbench probe
  • Produce P4 verdict with severity-tagged findings and citations
exec
/bin/zsh -lc 'git diff --name-only main..HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
tests/test_workbench_column_rename.py

exec
/bin/zsh -lc "git diff --stat main..HEAD && printf '\\n---\\n' && git diff -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-03-SURFACE-INVENTORY.md                    |  53 +++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/static/workbench.html             |  18 +--
 src/well_harness/static/workbench.js               |  14 +-
 tests/test_workbench_column_rename.py              | 172 +++++++++++++++++++++
 5 files changed, 246 insertions(+), 12 deletions(-)

---

exec
/bin/zsh -lc "sed -n '1,180p' src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,260p' tests/test_workbench_column_rename.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '180,280p' src/well_harness/static/workbench.html" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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


@pytest.mark.parametrize(
    "boot_copy",
    [
        "Probe & Trace ready",
        "Annotate & Propose ready",
        "Hand off & Track ready",
    ],
)
def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert boot_copy in js, f"workbench.js boot status missing: {boot_copy}"


def test_workbench_js_boot_status_drops_stale_names() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Old boot copy must NOT appear, otherwise the visible chrome and the
    # status messages will disagree.
    assert "Control panel ready" not in js
    assert "Document panel ready" not in js
    assert "Circuit panel ready" not in js


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

 succeeded in 0ms:
          type="button"
          class="workbench-trust-banner-dismiss"
          aria-label="Hide trust banner for this session"
          data-trust-banner-dismiss
        >
          Hide for session
        </button>
      </aside>

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
        <button
          id="approval-center-entry"
          type="button"
          class="workbench-toolbar-button"

 succeeded in 0ms:
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
  residualRisk: "Watch for future sensor drift.",
  logicChange: "Add a pressure plausibility cross-check before enabling the deploy chain.",
  reliabilityGain: "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
  guardrailNote: "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
};

let bootstrapPayload = null;
let latestWorkbenchRequestId = 0;
let currentWorkbenchRunLabel = "手动生成";
let workbenchRecentArchives = [];
let workbenchRunHistory = [];
let selectedWorkbenchHistoryId = "";
let workbenchHistorySequence = 0;
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

// E11-03 (2026-04-26): the three columns were renamed from technical
// nouns ("Scenario Control / Spec Review Surface / Logic Circuit Surface")
// to engineer-task verbs ("Probe & Trace / Annotate & Propose / Hand off
// & Track"). Underlying ids and data-column tokens stay stable so e2e
// selectors don't break — only the visible status copy here changes.
function bootWorkbenchControlPanel() {
  const status = workbenchElement("workbench-control-status");
  if (status) {
    status.textContent =
      "Probe & Trace ready. Scenario actions are staged for E07+.";
    status.dataset.tone = "ready";
  }
}

function bootWorkbenchDocumentPanel() {
  const status = workbenchElement("workbench-document-status");
  if (status) {
    status.textContent =
      "Annotate & Propose ready. Text-range annotation arrives in E07.";
    status.dataset.tone = "ready";
  }
}

function bootWorkbenchCircuitPanel() {
  const status = workbenchElement("workbench-circuit-status");
  if (status) {
    status.textContent =
      "Hand off & Track ready. Overlay annotation arrives in E07.";
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
  PANEL_READY: { final_approve: "APPROVING",    start_gen: "GENERATING",    reiterate: "INIT" },
  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
  APPROVED:    { archive: "ARCHIVING" },
  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
  ARCHIVED:    {},
  ERROR:       { reiterate: "INIT" },
};

function dispatchWorkflowEvent(event) {
  const next = (_workflowTransitions[workflowState] || {})[event];
  if (next === undefined) {
    return false;
  }
  workflowState = next;
  updateWorkflowUI();
  return true;
}

function updateWorkflowUI() {
  const approveBtn  = workbenchElement("workbench-final-approve");
  const startGenBtn = workbenchElement("workbench-start-gen");
  const badge       = workbenchElement("workbench-workflow-state");

  // "冻结审批 Spec" enabled when spec is not yet frozen or after generation
  const approveEnabled = ["INIT", "PANEL_READY", "ANNOTATING", "WIRING"].includes(workflowState);
  // "生成 (Frozen Spec)" enabled only when a frozen spec exists
  const startGenEnabled = workflowState === "FROZEN";

  if (approveBtn)  approveBtn.disabled  = !approveEnabled;
  if (startGenBtn) startGenBtn.disabled = !startGenEnabled;
  if (badge) {
    badge.textContent    = workflowState;
    badge.dataset.state  = workflowState.toLowerCase();
  }
}

const workbenchPresets = {
  ready_archived: {
    label: "一键通过验收",
    archiveBundle: true,
    source: "reference",
    sourceStatus: "当前样例：参考样例。系统会直接跑完整 happy path 并生成 archive。",
    preparationMessage: "参考样例已就位，系统马上开始生成 ready bundle 并留档。",
  },
  blocked_follow_up: {
    label: "一键看阻塞态",
    archiveBundle: false,
    source: "template",
    sourceStatus: "当前样例：空白模板。系统会故意演示 clarification gate 如何把不完整 packet 拦下来。",
    preparationMessage: "空白模板已就位，系统马上演示阻塞态。",
  },
  ready_preview: {
    label: "一键快速预览",
    archiveBundle: false,
    source: "reference",
    sourceStatus: "当前样例：参考样例。系统会直接跑 ready bundle，但不生成 archive。",
    preparationMessage: "参考样例已就位，系统马上生成 ready bundle 供快速查看。",
  },
  archive_retry: {
    label: "一键留档复跑",
    archiveBundle: true,
    source: "reference",
    sourceStatus: "当前样例：参考样例。这个预设适合连续复跑，archive 会自动避开重名目录。",
    preparationMessage: "参考样例已就位，系统马上做一次带 archive 的复跑。",
  },
};

function workbenchElement(id) {
  return document.getElementById(id);
}

exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md && printf '\\n---\\n' && sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-03 Surface Inventory — three-column rename

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Column 1 title: `Scenario Control` → `Probe & Trace · 探针与追踪` | [REWRITE] | `workbench.html` `#workbench-control-panel <h2>` | Engineer-task verb pair replaces technical noun. |
| 2 | Column 1 eyebrow: `control panel` → `probe & trace` | [REWRITE] | `workbench.html` `#workbench-control-panel .eyebrow` | Lowercase match for visible chrome consistency. |
| 3 | Column 1 boot status: `Waiting for control panel boot.` → `Waiting for probe & trace panel boot.` | [REWRITE] | `workbench.html` `#workbench-control-status` | Default copy before JS hydrates. |
| 4 | Column 1 JS boot: `Control panel ready. Scenario actions are staged for E07+.` → `Probe & Trace ready. Scenario actions are staged for E07+.` | [REWRITE] | `workbench.js:bootWorkbenchControlPanel` | Status after hydration. |
| 5 | Column 2 title: `Spec Review Surface` → `Annotate & Propose · 标注与提案` | [REWRITE] | `workbench.html` `#workbench-document-panel <h2>` | Maps to text-range annotation flow. |
| 6 | Column 2 eyebrow: `document` → `annotate & propose` | [REWRITE] | `workbench.html` `#workbench-document-panel .eyebrow` | |
| 7 | Column 2 boot status: `Waiting for document panel boot.` → `Waiting for annotate & propose panel boot.` | [REWRITE] | `workbench.html` `#workbench-document-status` | |
| 8 | Column 2 JS boot: `Document panel ready. Text-range annotation arrives in E07.` → `Annotate & Propose ready. Text-range annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchDocumentPanel` | |
| 9 | Column 3 title: `Logic Circuit Surface` → `Hand off & Track · 移交与跟踪` | [REWRITE] | `workbench.html` `#workbench-circuit-panel <h2>` | Maps to ticket handoff flow. |
| 10 | Column 3 eyebrow: `circuit` → `hand off & track` | [REWRITE] | `workbench.html` `#workbench-circuit-panel .eyebrow` | |
| 11 | Column 3 boot status: `Waiting for circuit panel boot.` → `Waiting for hand off & track panel boot.` | [REWRITE] | `workbench.html` `#workbench-circuit-status` | |
| 12 | Column 3 JS boot: `Circuit panel ready. Overlay annotation arrives in E07.` → `Hand off & Track ready. Overlay annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchCircuitPanel` | |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 12 → ≥ 10 ✓
- **[REWRITE/DELETE] count** = 12 (all rows) → ≥ 3 ✓

> **Verdict: Tier-A** (5-persona review).

This is exactly the rename-pure case the Tier-A trigger was designed for: every visible string on three structural surfaces is being rewritten in lockstep. Tier-A is the conservative routing.

## Stable-ID invariants (must hold)

The plan explicitly says "保留底层 ID 不变以免 e2e 测试失效" — every one of these anchors stays untouched:

- `id="workbench-control-panel"`, `id="workbench-document-panel"`, `id="workbench-circuit-panel"`
- `data-column="control"`, `data-column="document"`, `data-column="circuit"`
- `data-annotation-surface="control"`, `data-annotation-surface="document"`, `data-annotation-surface="circuit"`
- `id="workbench-control-status"`, `id="workbench-document-status"`, `id="workbench-circuit-status"`

`tests/test_workbench_column_rename.py` locks all 12 stable anchors alongside the new visible copy so a future "polish" pass can't silently regress either side.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` (3 [REWRITE] blocks, 12 visible-copy lines)
- `src/well_harness/static/workbench.js` (3 [REWRITE] boot status strings)
- `tests/test_workbench_column_rename.py` (NEW)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.

---
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

codex
代码层面的 rename 已经能看到是纯表层变更，下一步我在验证“测试是否真的覆盖到 claim”这件事：会补读带行号的源码/测试，并跑一次目标测试加 `/workbench` 真机探针。
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '200,255p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba tests/test_workbench_column_rename.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '55,95p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'git diff main..HEAD -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js tests/test_workbench_column_rename.py .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
@@ -11,3 +11,4 @@
 E11-13: P1 (round-robin start; first Tier-B sub-phase under bundle #2)
 E11-14: P2 (round-robin successor; Senior FCS Engineer fits server-side / API contract review)
 E11-05: Tier-A (≥10 copy_diff_lines AND ≥3 [REWRITE]: 3 workbench_start.html corrections + 12 ANCHORED card copy lines). All 5 personas dispatched. Rotation pointer unchanged (Tier-A does not consume a Tier-B slot).
+E11-03: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 39a3194..a706072 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -206,11 +206,11 @@
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
@@ -226,11 +226,11 @@
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
@@ -246,11 +246,11 @@
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
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index dc66e55..3dd764a 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -60,10 +60,16 @@ function bootWorkbenchColumnSafely(columnName, bootFn) {
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
@@ -71,7 +77,8 @@ function bootWorkbenchControlPanel() {
 function bootWorkbenchDocumentPanel() {
   const status = workbenchElement("workbench-document-status");
   if (status) {
-    status.textContent = "Document panel ready. Text-range annotation arrives in E07.";
+    status.textContent =
+      "Annotate & Propose ready. Text-range annotation arrives in E07.";
     status.dataset.tone = "ready";
   }
 }
@@ -79,7 +86,8 @@ function bootWorkbenchDocumentPanel() {
 function bootWorkbenchCircuitPanel() {
   const status = workbenchElement("workbench-circuit-status");
   if (status) {
-    status.textContent = "Circuit panel ready. Overlay annotation arrives in E07.";
+    status.textContent =
+      "Hand off & Track ready. Overlay annotation arrives in E07.";
     status.dataset.tone = "ready";
   }
 }
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
/bin/zsh -lc 'pytest -q tests/test_workbench_column_rename.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 736ms:
................................                                         [100%]
32 passed in 0.56s

codex
验证结果已经够形成结论了：实现本身是干净的 rename，red line 也成立；真正的问题落在 V&V 面，测试文件没有把 12 条可见 copy 全部正向锁死。现在我补一个 live probe 证据，再整理成 findings-first verdict。
exec
/bin/zsh -lc "python - <<'PY'
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
    checks = [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'Waiting for probe &amp; trace panel boot.',
        'Waiting for annotate &amp; propose panel boot.',
        'Waiting for hand off &amp; track panel boot.',
    ]
    print('status=', resp.status)
    for item in checks:
        print(('FOUND' if item in body else 'MISSING'), item)
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,880p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
本机没有 `python` 别名，我改用 `python3` 直接做 live probe；这也顺手验证了 review 结论不是靠静态阅读硬猜。
exec
/bin/zsh -lc "python3 - <<'PY'
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
    checks = [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'Waiting for probe &amp; trace panel boot.',
        'Waiting for annotate &amp; propose panel boot.',
        'Waiting for hand off &amp; track panel boot.',
    ]
    print('status=', resp.status)
    for item in checks:
        print(('FOUND' if item in body else 'MISSING'), item)
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 615ms:
status= 200
MISSING Probe &amp; Trace · 探针与追踪
MISSING Annotate &amp; Propose · 标注与提案
MISSING Hand off &amp; Track · 移交与跟踪
MISSING Waiting for probe &amp; trace panel boot.
MISSING Waiting for annotate &amp; propose panel boot.
MISSING Waiting for hand off &amp; track panel boot.

codex
第一次 live probe 返回了 200 但没命中预期文案，这更像环境导入路径问题而不是代码问题。我先核对 `well_harness` 到底是从当前 `src/` 还是别的已安装包导入，再用正确路径重跑探针。
exec
/bin/zsh -lc 'rg -n "pythonpath|tool.pytest|pytest.ini_options|addopts" pyproject.toml pytest.ini setup.cfg tox.ini' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: pytest.ini: No such file or directory (os error 2)
rg: setup.cfg: No such file or directory (os error 2)
rg: tox.ini: No such file or directory (os error 2)
pyproject.toml:32:[tool.pytest.ini_options]
pyproject.toml:34:addopts = "-m 'not e2e'"
pyproject.toml:40:pythonpath = ["src", "."]

exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import well_harness
import well_harness.demo_server
print('pkg=', well_harness.__file__)
print('demo_server=', well_harness.demo_server.__file__)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
pkg= /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/__init__.py
demo_server= /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py

exec
/bin/zsh -lc "python3 - <<'PY'
import well_harness
import well_harness.demo_server
print('pkg=', well_harness.__file__)
print('demo_server=', well_harness.demo_server.__file__)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
pkg= /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/__init__.py
demo_server= /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py

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
    print('status=', resp.status)
    for needle in [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'Waiting for probe &amp; trace panel boot.',
        'Waiting for annotate &amp; propose panel boot.',
        'Waiting for hand off &amp; track panel boot.',
    ]:
        print(('FOUND' if needle in body else 'MISSING'), needle)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
  File "<stdin>", line 24
    
    ^
SyntaxError: unexpected EOF while parsing

codex
导入路径已经校正到当前 checkout；刚才只是临时探针脚本少了收尾块。我重跑一次带完整关闭逻辑的版本，拿可引用的 live evidence。
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
    print('status=', resp.status)
    for needle in [
        'Probe &amp; Trace · 探针与追踪',
        'Annotate &amp; Propose · 标注与提案',
        'Hand off &amp; Track · 移交与跟踪',
        'Waiting for probe &amp; trace panel boot.',
        'Waiting for annotate &amp; propose panel boot.',
        'Waiting for hand off &amp; track panel boot.',
    ]:
        print(('FOUND' if needle in body else 'MISSING'), needle)
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 574ms:
status= 200
FOUND Probe &amp; Trace · 探针与追踪
FOUND Annotate &amp; Propose · 标注与提案
FOUND Hand off &amp; Track · 移交与跟踪
FOUND Waiting for probe &amp; trace panel boot.
FOUND Waiting for annotate &amp; propose panel boot.
FOUND Waiting for hand off &amp; track panel boot.

exec
/bin/zsh -lc "nl -ba pyproject.toml | sed -n '28,42p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

codex
**CHANGES_REQUIRED**

- IMPORTANT — The suite does not positively lock the three renamed pre-hydration HTML boot-status strings. Those rewritten lines are present in [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:212):212-214, 232-234, 252-253 and are explicitly part of the 12-line surface inventory in [E11-03-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md:9):9-20. But [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:86):86-102 only checks that the old waiting-copy is absent, and [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:163):163-172 does not assert the new waiting-copy either. A drift to any different phrase would still pass, so coverage does not meet the stated “12 visible-copy lines in lockstep” claim.

- NIT — The JS boot-copy tests only lock the `"... ready"` prefixes, not the full rewritten sentences. The actual strings are in [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:71):71-72, 80-81, 89-90, while [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:138):138-157 only checks the renamed prefixes plus stale-prefix absence. If the intended contract is exact copy lock, these should be full-string assertions.

Truth-engine red line is clean: `git diff --name-only main..HEAD` returned only the five expected tracked files in scope. I also ran `pytest -q tests/test_workbench_column_rename.py` and got `32 passed`, then did a live probe with `PYTHONPATH=src` per [pyproject.toml](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/pyproject.toml:32):32-40; `DemoRequestHandler` served `/workbench` with `200` and all three renamed titles plus all three renamed waiting-status strings present. So the implementation looks correct; the gap is the verification net, not the shipped copy.

**P4 — V&V Engineer (Tier-A, E11-03)**

tokens used
127,616
**CHANGES_REQUIRED**

- IMPORTANT — The suite does not positively lock the three renamed pre-hydration HTML boot-status strings. Those rewritten lines are present in [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:212):212-214, 232-234, 252-253 and are explicitly part of the 12-line surface inventory in [E11-03-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-03-SURFACE-INVENTORY.md:9):9-20. But [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:86):86-102 only checks that the old waiting-copy is absent, and [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:163):163-172 does not assert the new waiting-copy either. A drift to any different phrase would still pass, so coverage does not meet the stated “12 visible-copy lines in lockstep” claim.

- NIT — The JS boot-copy tests only lock the `"... ready"` prefixes, not the full rewritten sentences. The actual strings are in [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:71):71-72, 80-81, 89-90, while [tests/test_workbench_column_rename.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_column_rename.py:138):138-157 only checks the renamed prefixes plus stale-prefix absence. If the intended contract is exact copy lock, these should be full-string assertions.

Truth-engine red line is clean: `git diff --name-only main..HEAD` returned only the five expected tracked files in scope. I also ran `pytest -q tests/test_workbench_column_rename.py` and got `32 passed`, then did a live probe with `PYTHONPATH=src` per [pyproject.toml](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/pyproject.toml:32):32-40; `DemoRequestHandler` served `/workbench` with `200` and all three renamed titles plus all three renamed waiting-status strings present. So the implementation looks correct; the gap is the verification net, not the shipped copy.

**P4 — V&V Engineer (Tier-A, E11-03)**

