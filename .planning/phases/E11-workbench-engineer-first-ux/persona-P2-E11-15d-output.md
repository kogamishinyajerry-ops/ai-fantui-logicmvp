2026-04-26T03:04:02.024199Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T03:04:02.024442Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc7be-78ec-7141-b513-11d5871e043c
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B single-persona pipeline, E11-15d sub-phase).

# Context — E11-15d approval-flow polish

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15d-approval-flow-polish-20260426`
**PR:** #29
**Worktree HEAD:** `288d322` (single commit on top of main `b10fcba`)

## What E11-15d ships

Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).

| File:Line | Before | After |
|---|---|---|
| `workbench.html:384` | `<h3>Pending</h3>` | `<h3>待审 · Pending</h3>` |
| `workbench.html:385` | body `Submitted annotation proposals wait here before acceptance or rejection.` | bilingual `已提交的标注提案在被通过或驳回前在此排队 · ...` |
| `workbench.html:388` | `<h3>Accept</h3>` | `<h3>通过 · Accept</h3>` |
| `workbench.html:389` | btn `Accept Proposal` | `通过提案 · Accept Proposal` |
| `workbench.html:392` | `<h3>Reject</h3>` | `<h3>驳回 · Reject</h3>` |
| `workbench.html:393` | btn `Reject Proposal` | `驳回提案 · Reject Proposal` |

## Files in scope

- `src/well_harness/static/workbench.html` — 6 strings flipped (lines 384-393)
- `tests/test_workbench_approval_flow_polish.py` — NEW (25 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended via `tools/codex_persona_dispatch.py append-rotation`

## Your specific lens (P2 Senior FCS Engineer)

Focus on:
- **Visible-copy consistency**: do the 6 new bilingual approval-flow strings work harmoniously with the surrounding E11-15b approval-center surface (`Kogami 提案审批 · Kogami Proposal Triage` h2, `审批中心 · Approval Center` entry button, `审批操作仅限 Kogami · ...` caption)? Does the page now read uniformly as a Chinese-first FCS engineer's approval workflow?
- **Functional flow integrity**: the lane buttons (`通过提案`, `驳回提案`) carry `data-approval-action="accept"`/`"reject"` attributes. Confirm those structural anchors are preserved (they're the JS-binding points). Same for `data-approval-lane` on the lane articles.
- **Translation quality for FCS workflow domain**: are `待审`/`通过`/`驳回` the right approval-flow verbs for an aviation FCS engineer's workspace? Alternatives could be `待批`/`批准`/`拒绝` (more generic) or `待审议`/`通过审议`/`审议驳回` (more formal). The current choice biases toward concise + workshop-feel.
- **Test completeness**: the 25 tests cover (a) positive bilingual locks, (b) negative stale-English locks, (c) English suffix preservation, (d) structural anchor preservation, (e) live-served route, (f) backend isolation. Any contract claim untested?
- **Backend isolation correctness**: `test_e11_15d_does_not_touch_api_remediation_message` asserts `demo_server.py` remediation message is unchanged AND no Chinese strings leak in. Verify by independent grep that the assertion is correct (i.e., `demo_server.py` really doesn't contain `待审`/`通过提案`/`驳回提案`/`已提交的标注提案`).
- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).

## Verification status

- 1153 / 1153 default pytest pass (25 new in `test_workbench_approval_flow_polish.py`)
- Truth-engine red line preserved: `git diff --name-only main..288d322` shows only `static/workbench.html`, `tests/test_workbench_approval_flow_polish.py`, and `.planning/`
- E11-10 tooling validated: `python3 tools/codex_persona_dispatch.py next-persona` returned `P2` (used to derive your persona); `append-rotation E11-15d P2 B "..."` was used to append the rotation entry

## Out of scope (deliberately deferred or preserved)

- **API remediation message** in `demo_server.py:743` — backend contract.
- **Approval Center entry button + Kogami-only caption** + `approval-center-title` h2 — already bilingualized by E11-15b.
- **Topbar chips** (`Identity` / `Ticket` / `Feedback Mode` / `System`) — left as labels next to dynamic Chinese content.
- **System dropdown options** (`Thrust Reverser` / `Landing Gear` / `Bleed Air Valve` / `C919 E-TRAS`) — domain proper nouns; bilingualization can be a separate sub-phase if the user wants.
- **Column-trio eyebrows** — locked by E11-03; bilingual h2 already gives Chinese-first signal.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..288d322` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/` / `workbench.js` / `workbench.css` / `demo_server.py`.

Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-15d)**

codex
Reviewing the E11-15d slice as a code review only. I’m loading the review workflow guidance, checking prior LogicMVP context, and then I’ll verify the exact diff, the HTML strings, the new tests, and a live-served `/workbench` path.
exec
/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|approval|workbench|E11-15" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
215:- rollout_summaries/2026-04-21T13-13-28-Rmvx-docs_planning_cockpit_roadmap_and_phase1_local_project_radar.md (cwd=/Users/Zhuanz/AI Coding Assets, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/21/rollout-2026-04-21T21-13-28-019db02c-a12f-74d2-947b-0a1b052967a3.jsonl, updated_at=2026-04-21T15:14:12+00:00, thread_id=019db02c-a12f-74d2-947b-0a1b052967a3, docs/roadmap reset and team-agent approval)
355:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
361:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
365:- Notion MCP unavailable, unknown MCP server 'Notion', .planning/PROJECT.md, .planning/ROADMAP.md, .planning/STATE.md, Chrome approval denied, get_app_state denied
371:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
380:- when control-plane review would slow execution, the user said "决策权完全绕过Kogami和Notion里的Opus 4.7" -> if this workflow comes up again, own the local execution decisions instead of waiting on Notion-side approval unless a real gate appears [Task 1][Task 2]
394:- Symptom: trying to inspect Notion/Claude desktop first burns time -> cause: Notion MCP and Computer Use approvals can both be unavailable -> fix: pivot early to local planning docs and CLI/config inspection when `unknown MCP server 'Notion'` or browser-control denial appears [Task 1]
396:- Symptom: browser login page opens but Claude still cannot be used -> cause: `claude auth login --claudeai` was launched but approval blocked browser completion -> fix: ask the user to finish the browser auth step or use a session with explicit browser-control permission before declaring recovery complete [Task 2]
458:- ADR-006, Reviewer Agent Verdict=Accept 且 CI 全绿 → 你直接 merge, update-branch, sync_well_harness_approvals.py, Notion sync, PR stack, retarget to main, Clean Pass
490:- Under ADR-006, the reliable autonomous merge loop was: confirm acceptance + CI green -> merge -> update Notion task/session state -> reconcile session records with `sync_well_harness_approvals.py` [Task 1]
501:- Symptom: `ruff format --check` blocks a merge in the stack -> cause: formatting drift on a PR layer -> fix: reformat, recommit, rerun checks, and continue the merge loop rather than escalating for ordinary approval [Task 1]
661:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, demo-first narrowing report without code changes)
671:- rollout_summaries/2026-04-22T13-19-47-467x-demo_first_cfd_workbench_assessment_and_claude_handoff.md (cwd=/Users/Zhuanz/Desktop/cfd-harness-unified, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-19-47-019db558-c6dd-7930-b776-2493c7fc5dfb.jsonl, updated_at=2026-04-22T13:41:27+00:00, thread_id=019db558-c6dd-7930-b776-2493c7fc5dfb, Chinese Claude Code brief delivered in requested structure)
751:- Symptom: a future executor infers multi-solver activation from tooling breadcrumbs -> cause: skill inventory mentions SU2/CFX while runtime adapter is still single-engine -> fix: treat those as decision-tree inputs, not implementation approval [Task 2][Task 3]
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
1021:## Task 4: Accept corrected-inventory approval actions without collapsing into execution or freeze signoff
1025:- rollout_summaries/2026-04-07T13-59-35-aTNv-post_phase7_corrected_inventory_approval_and_freeze_signoff.md (cwd=/Users/Zhuanz/20260402 AI ControlLogicMaster, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-59-35-019d683d-d22a-7590-9bc5-612efced3d79.jsonl, updated_at=2026-04-08T13:29:34+00:00, thread_id=019d683d-d22a-7590-9bc5-612efced3d79, corrected-inventory approval action with explicit no-execution boundary)
1026:- rollout_summaries/2026-04-02T16-11-48-lkTw-aplh_post_phase7_manual_review_intake_action_review.md (cwd=/Users/Zhuanz/20260402 AI ControlLogicMaster, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/03/rollout-2026-04-03T00-11-48-019d4ef7-13d3-7311-a159-a08420027a5a.jsonl, updated_at=2026-04-08T12:29:35+00:00, thread_id=019d4ef7-13d3-7311-a159-a08420027a5a, manual intake accepted but explicitly not freeze approval)
1048:- when the user said "你是 independent approval authority… 你不是 corrected request packet 作者… 你不是 Phase 8 executor" -> preserve strict role separation between approval, review, execution, and freeze authority in this repo [Task 4]
1049:- when the user said "如果 approval granted，只能创建一个 executable approval YAML 和一个 approval action report" and "不得运行 populate-formal" -> approval sessions should only produce the allowed artifacts and must not spill into execution [Task 4]
1051:- when the user said acceptance "must not equal freeze approval" and "cannot directly enter final freeze signoff" -> always restate that `accepted_for_review` is not `freeze-complete`, even when readiness evidence looks strong [Task 3][Task 4]
1061:- `FormalPopulationExecutor.load_approval()`, `build_inventory()`, `validate_approval_matches_inventory()`, and `preflight_targets()` are the critical approval-path surfaces; the stale old approval failed correctly on `49 != 50` when the live corrected inventory was 50 files [Task 4]
1063:- In this governance family, `freeze_gate_status.yaml` and historical approval YAML are effectively immutable unless the task explicitly authorizes touching them; integrity is often tracked by the unchanged SHA-256 hash [Task 3][Task 4]
1072:- Symptom: a corrected inventory seems close enough to reuse an older approval -> cause: live file count/order changed and the old approval became stale -> fix: invalidate the old approval, prove the mismatch (`49 != 50` here), and issue a new executable approval YAML rather than patching history [Task 4]
1240:- In this repo, the generator scripts under the external CFD workbench path were a more reliable evidence source than the rendered PDFs; when `pdftotext` is unavailable and `matplotlib` temp/cache paths are broken, parse scripts as text or AST instead of importing them [Task 1]
1497:- postprocess_runner, nl_postprocess, visualization_engine, result_manifest, result_asset, patch-rejected, writing outside of the project; rejected by user approval settings, read-only, OpenFOAM
1537:- Symptom: a large implementation patch "lands" only in the agent narrative and not on disk -> cause: the environment rejected writes with `writing outside of the project; rejected by user approval settings` -> fix: confirm writeability early, and if patching is blocked, stop and report the exact failure instead of implying completion [Task 5]
1585:applies_to: cwd=/Users/Zhuanz plus machine-level account tooling under `~/.codex-accounts`, `~/.codex`, and `~/.npm-global/bin`; reuse_rule=safe for this machine’s local Codex account-management inspection, but do not reuse it as approval for quota-bypass or cross-account circumvention.

codex
Using `gsd-code-review` as the review frame and keeping it findings-first. Next I’m scoping the exact files in `288d322`, reading the approval-center HTML/tests, and checking the red-line diff to ensure nothing touched truth-engine or runtime surfaces.
exec
/bin/zsh -lc "nl -ba tests/test_workbench_approval_flow_polish.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '340,430p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   384	            <h3>待审 · Pending</h3>
   385	            <p>已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.</p>
   386	          </article>
   387	          <article class="workbench-approval-lane" data-approval-lane="accept">
   388	            <h3>通过 · Accept</h3>
   389	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
   390	          </article>
   391	          <article class="workbench-approval-lane" data-approval-lane="reject">
   392	            <h3>驳回 · Reject</h3>
   393	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>
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

 succeeded in 0ms:
     1	"""E11-15d — approval-flow polish: bilingualize 3 lane h3s + 2 lane buttons + 1 body copy.
     2	
     3	Closes the last English-only surface in the workbench demo (the
     4	Approval Center lane labels + buttons + pending-lane body copy).
     5	Functional approval-flow strings are now `<中文> · <English>`,
     6	preserving English suffixes for any downstream substring locks
     7	(none currently exist in tests).
     8	
     9	Out of scope:
    10	- API remediation message in demo_server.py:743 — backend contract
    11	  (locked by tests/test_lever_snapshot_manual_override_guard.py:151).
    12	- Approval Center entry button + Kogami-only caption (already
    13	  bilingualized by E11-15b PR #25).
    14	- approval-center-title h2 (already bilingualized by E11-15b PR #25).
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
    58	# ─── 1. New bilingual strings POSITIVELY locked ──────────────────────
    59	
    60	
    61	@pytest.mark.parametrize(
    62	    "bilingual",
    63	    [
    64	        "<h3>待审 · Pending</h3>",
    65	        "<h3>通过 · Accept</h3>",
    66	        "<h3>驳回 · Reject</h3>",
    67	        "通过提案 · Accept Proposal",
    68	        "驳回提案 · Reject Proposal",
    69	        "已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.",
    70	    ],
    71	)
    72	def test_workbench_html_carries_bilingual_approval_flow_string(bilingual: str) -> None:
    73	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    74	    assert bilingual in html, f"missing bilingual approval-flow string: {bilingual}"
    75	
    76	
    77	# ─── 2. Stale English-only strings are gone ──────────────────────────
    78	
    79	
    80	@pytest.mark.parametrize(
    81	    "stale",
    82	    [
    83	        "<h3>Pending</h3>",
    84	        "<h3>Accept</h3>",
    85	        "<h3>Reject</h3>",
    86	        ">Accept Proposal<",
    87	        ">Reject Proposal<",
    88	    ],
    89	)
    90	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    91	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    92	    assert stale not in html, f"stale English-only approval-flow string still present: {stale}"
    93	
    94	
    95	# ─── 3. English suffixes preserved for future substring locks ────────
    96	
    97	
    98	@pytest.mark.parametrize(
    99	    "preserved_english_suffix",
   100	    [
   101	        "Pending</h3>",
   102	        "Accept</h3>",
   103	        "Reject</h3>",
   104	        "Accept Proposal</button>",
   105	        "Reject Proposal</button>",
   106	        "before acceptance or rejection.",  # tail of the body copy
   107	    ],
   108	)
   109	def test_e11_15d_preserves_english_suffix(preserved_english_suffix: str) -> None:
   110	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   111	    assert preserved_english_suffix in html, (
   112	        f"E11-15d broke English suffix invariant: {preserved_english_suffix}"
   113	    )
   114	
   115	
   116	# ─── 4. Structural anchors preserved ─────────────────────────────────
   117	
   118	
   119	@pytest.mark.parametrize(
   120	    "anchor",
   121	    [
   122	        'data-approval-lane="pending"',
   123	        'data-approval-lane="accept"',
   124	        'data-approval-lane="reject"',
   125	        'data-approval-action="accept"',
   126	        'data-approval-action="reject"',
   127	        'class="workbench-approval-grid"',
   128	    ],
   129	)
   130	def test_e11_15d_preserves_structural_anchors(anchor: str) -> None:
   131	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   132	    assert anchor in html, f"E11-15d broke structural anchor: {anchor}"
   133	
   134	
   135	# ─── 5. Live-served route reflects the polish ────────────────────────
   136	
   137	
   138	def test_workbench_route_serves_bilingual_approval_flow(server) -> None:
   139	    status, html = _get(server, "/workbench")
   140	    assert status == 200
   141	    assert "待审 · Pending" in html
   142	    assert "通过 · Accept" in html
   143	    assert "驳回 · Reject" in html
   144	    assert "通过提案 · Accept Proposal" in html
   145	    assert "驳回提案 · Reject Proposal" in html
   146	    assert "已提交的标注提案在被通过或驳回前在此排队" in html
   147	
   148	
   149	# ─── 6. Truth-engine red line — API remediation untouched ────────────
   150	
   151	
   152	def test_e11_15d_does_not_touch_api_remediation_message() -> None:
   153	    """The 409 remediation message is API contract, not display copy."""
   154	    repo_root = Path(__file__).resolve().parents[1]
   155	    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
   156	        encoding="utf-8"
   157	    )
   158	    assert (
   159	        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   160	        in demo_server
   161	    )
   162	    # Approval-flow Chinese strings must NOT leak into backend
   163	    new_strings = [
   164	        "待审", "通过 · Accept", "驳回 · Reject",
   165	        "通过提案", "驳回提案", "已提交的标注提案",
   166	    ]
   167	    for new_string in new_strings:
   168	        assert new_string not in demo_server, (
   169	            f"E11-15d Chinese {new_string!r} unexpectedly leaked into demo_server.py"
   170	        )

exec
/bin/zsh -lc 'git diff --name-only main..288d322' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git diff --stat main..288d322' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git status --short --branch' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-15d-SURFACE-INVENTORY.md                   |   84 ++
 .../PERSONA-ROTATION-STATE.md                      |    1 +
 .../persona-P1-E11-10-R3-output.md                 | 1463 ++++++++++++++++++++
 .../persona-P1-E11-10-R3-prompt.txt                |   83 ++
 src/well_harness/static/workbench.html             |   12 +-
 tests/test_workbench_approval_flow_polish.py       |  170 +++
 6 files changed, 1807 insertions(+), 6 deletions(-)

 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-prompt.txt
src/well_harness/static/workbench.html
tests/test_workbench_approval_flow_polish.py

 succeeded in 0ms:
## feat/e11-15d-approval-flow-polish-20260426
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt

exec
/bin/zsh -lc 'git log --oneline --decorate -n 5' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
288d322 (HEAD -> feat/e11-15d-approval-flow-polish-20260426) phase(E11-15d): approval-flow polish — bilingualize lane h3s + buttons + body copy
b10fcba (origin/main, origin/HEAD, main) docs(E11-10): bump coordination evidence — PR #28 merged with P1 R3 APPROVE no findings
99d962f phase(E11-10): codex personas pipeline tooling (#28)
79a774a docs(E11-11): bump coordination evidence — PR #27 merged with P5 APPROVE_WITH_NITS
9f73f0f phase(E11-11): JS-boot e2e smoke + bundle-page bug fix surfaced by it (#27)

codex
The diff is scoped as claimed, except there are already untracked local review artifacts under `.planning/` from this session, which I’m ignoring. I’m now checking the whole `workbench.html` surface for remaining English-only heading/button content and independently verifying the backend-remediation string isolation with grep, not just the new test.
exec
/bin/zsh -lc 'rg -nE ">[A-Za-z][''^<]*</h[1-3]>|>[A-Za-z][''^<]*</button>" src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 2 in 0ms:
rg: error parsing flag -E: grep config error: unknown encoding: >[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>

exec
/bin/zsh -lc 'rg -n "待审|通过提案|驳回提案|已提交的标注提案|通过 · Accept|驳回 · Reject" src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '1,340p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'rg -n "Approval Center|Kogami Proposal Triage|审批中心|Pending Kogami sign-off|approval-center|data-approval-lane|data-approval-action" src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
 succeeded in 0ms:
343:          id="approval-center-entry"
347:          aria-controls="approval-center-panel"
349:          审批中心 · Approval Center
363:          <strong>Pending Kogami sign-off</strong>
373:        id="approval-center-panel"
374:        class="workbench-approval-center"
376:        aria-labelledby="approval-center-title"
379:          <p class="eyebrow">审批中心</p>
380:          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
383:          <article class="workbench-approval-lane" data-approval-lane="pending">
387:          <article class="workbench-approval-lane" data-approval-lane="accept">
389:            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
391:          <article class="workbench-approval-lane" data-approval-lane="reject">
393:            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>

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

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '730,755p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

codex
I’ve reached the closure-claim pass. There is already a possible gap outside the approval-center slice: `workbench.html` still appears to have at least one unrelated English-only button label, so I’m verifying that directly with the exact grep pattern and then live-probing `/workbench` through the server to separate “approval-flow done” from “entire page fully Chinese-first.”
exec
/bin/zsh -lc 'grep -nE ">[A-Za-z][''^<]*</h[1-3]>|>[A-Za-z][''^<]*</button>" src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
111:              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
143:              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
173:              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
380:          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>

exec
/bin/zsh -lc 'git diff --unified=20 main..288d322 -- src/well_harness/static/workbench.html tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 12a457a..cbc80a4 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -364,41 +364,41 @@
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
           <p class="eyebrow">审批中心</p>
           <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
         </header>
         <div class="workbench-approval-grid">
           <article class="workbench-approval-lane" data-approval-lane="pending">
-            <h3>Pending</h3>
-            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
+            <h3>待审 · Pending</h3>
+            <p>已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.</p>
           </article>
           <article class="workbench-approval-lane" data-approval-lane="accept">
-            <h3>Accept</h3>
-            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
+            <h3>通过 · Accept</h3>
+            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
           </article>
           <article class="workbench-approval-lane" data-approval-lane="reject">
-            <h3>Reject</h3>
-            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
+            <h3>驳回 · Reject</h3>
+            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>
           </article>
         </div>
       </section>
 
       <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
     </main>
 
     <script src="/annotation_overlay.js"></script>
     <script src="/workbench.js"></script>
   </body>
 </html>
diff --git a/tests/test_workbench_approval_flow_polish.py b/tests/test_workbench_approval_flow_polish.py
new file mode 100644
index 0000000..29be04b
--- /dev/null
+++ b/tests/test_workbench_approval_flow_polish.py
@@ -0,0 +1,170 @@
+"""E11-15d — approval-flow polish: bilingualize 3 lane h3s + 2 lane buttons + 1 body copy.
+
+Closes the last English-only surface in the workbench demo (the
+Approval Center lane labels + buttons + pending-lane body copy).
+Functional approval-flow strings are now `<中文> · <English>`,
+preserving English suffixes for any downstream substring locks
+(none currently exist in tests).
+
+Out of scope:
+- API remediation message in demo_server.py:743 — backend contract
+  (locked by tests/test_lever_snapshot_manual_override_guard.py:151).
+- Approval Center entry button + Kogami-only caption (already
+  bilingualized by E11-15b PR #25).
+- approval-center-title h2 (already bilingualized by E11-15b PR #25).
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
+        "<h3>待审 · Pending</h3>",
+        "<h3>通过 · Accept</h3>",
+        "<h3>驳回 · Reject</h3>",
+        "通过提案 · Accept Proposal",
+        "驳回提案 · Reject Proposal",
+        "已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.",
+    ],
+)
+def test_workbench_html_carries_bilingual_approval_flow_string(bilingual: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert bilingual in html, f"missing bilingual approval-flow string: {bilingual}"
+
+
+# ─── 2. Stale English-only strings are gone ──────────────────────────
+
+
+@pytest.mark.parametrize(
+    "stale",
+    [
+        "<h3>Pending</h3>",
+        "<h3>Accept</h3>",
+        "<h3>Reject</h3>",
+        ">Accept Proposal<",
+        ">Reject Proposal<",
+    ],
+)
+def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert stale not in html, f"stale English-only approval-flow string still present: {stale}"
+
+
+# ─── 3. English suffixes preserved for future substring locks ────────
+
+
+@pytest.mark.parametrize(
+    "preserved_english_suffix",
+    [
+        "Pending</h3>",
+        "Accept</h3>",
+        "Reject</h3>",
+        "Accept Proposal</button>",
+        "Reject Proposal</button>",
+        "before acceptance or rejection.",  # tail of the body copy
+    ],
+)
+def test_e11_15d_preserves_english_suffix(preserved_english_suffix: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert preserved_english_suffix in html, (
+        f"E11-15d broke English suffix invariant: {preserved_english_suffix}"
+    )
+
+
+# ─── 4. Structural anchors preserved ─────────────────────────────────
+
+
+@pytest.mark.parametrize(
+    "anchor",
+    [
+        'data-approval-lane="pending"',
+        'data-approval-lane="accept"',
+        'data-approval-lane="reject"',
+        'data-approval-action="accept"',
+        'data-approval-action="reject"',
+        'class="workbench-approval-grid"',
+    ],
+)
+def test_e11_15d_preserves_structural_anchors(anchor: str) -> None:
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    assert anchor in html, f"E11-15d broke structural anchor: {anchor}"
+
+
+# ─── 5. Live-served route reflects the polish ────────────────────────
+
+
+def test_workbench_route_serves_bilingual_approval_flow(server) -> None:
+    status, html = _get(server, "/workbench")
+    assert status == 200
+    assert "待审 · Pending" in html
+    assert "通过 · Accept" in html
+    assert "驳回 · Reject" in html
+    assert "通过提案 · Accept Proposal" in html
+    assert "驳回提案 · Reject Proposal" in html
+    assert "已提交的标注提案在被通过或驳回前在此排队" in html
+
+
+# ─── 6. Truth-engine red line — API remediation untouched ────────────
+
+
+def test_e11_15d_does_not_touch_api_remediation_message() -> None:
+    """The 409 remediation message is API contract, not display copy."""
+    repo_root = Path(__file__).resolve().parents[1]
+    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
+        encoding="utf-8"
+    )
+    assert (
+        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
+        in demo_server
+    )
+    # Approval-flow Chinese strings must NOT leak into backend
+    new_strings = [
+        "待审", "通过 · Accept", "驳回 · Reject",
+        "通过提案", "驳回提案", "已提交的标注提案",
+    ]
+    for new_string in new_strings:
+        assert new_string not in demo_server, (
+            f"E11-15d Chinese {new_string!r} unexpectedly leaked into demo_server.py"
+        )

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, threading, time
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
conn.request('GET', '/workbench')
resp = conn.getresponse()
body = resp.read().decode('utf-8')
print(f'STATUS {resp.status}')
for needle in [
    '审批中心 · Approval Center',
    'Kogami 提案审批 · Kogami Proposal Triage',
    '待审 · Pending',
    '通过 · Accept',
    '驳回 · Reject',
    '通过提案 · Accept Proposal',
    '驳回提案 · Reject Proposal',
]:
    print(f\"{needle}: {'YES' if needle in body else 'NO'}\")
server.shutdown()
server.server_close()
thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 590ms:
STATUS 200
审批中心 · Approval Center: YES
Kogami 提案审批 · Kogami Proposal Triage: YES
待审 · Pending: YES
通过 · Accept: YES
驳回 · Reject: YES
通过提案 · Accept Proposal: YES
驳回提案 · Reject Proposal: YES

 succeeded in 753ms:
.........................                                                [100%]
25 passed in 0.56s

codex
The stronger page-wide claim is looking overstated. I’m extracting all heading/button surfaces now, because the approval lane copy itself is correct, but the page still appears to carry older English-leading or English-only controls outside this six-string slice.
exec
/bin/zsh -lc 'rg -n "<h[1-3]|</h[1-3]|<button|</button>" src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
18:          <h1>控制逻辑工作台 · Control Logic Workbench</h1>
98:          <h2>起手卡 · One-click 走读</h2>
111:              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
119:            <button
126:            </button>
143:              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
149:            <button
156:            </button>
173:              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
179:            <button
186:            </button>
219:        <button
226:        </button>
231:        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">标记信号</button>
232:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">圈选 logic gate</button>
233:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">关联 spec</button>
234:        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">引用 requirement 段</button>
275:            <h2>探针与追踪 · Probe &amp; Trace</h2>
281:            <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
282:            <button type="button" class="workbench-toolbar-button">快照当前状态 · Snapshot Current State</button>
295:            <h2>标注与提案 · Annotate &amp; Propose</h2>
315:            <h2>移交与跟踪 · Hand off &amp; Track</h2>
334:          <h2>审核队列 · Review Queue</h2>
342:        <button
350:        </button>
380:          <h2 id="approval-center-title">Kogami 提案审批 · Kogami Proposal Triage</h2>
384:            <h3>待审 · Pending</h3>
388:            <h3>通过 · Accept</h3>
389:            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
392:            <h3>驳回 · Reject</h3>
393:            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '328,339p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '216,228p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '106,187p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

 succeeded in 0ms:
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

codex
The approval-center mechanics are intact. The remaining question is whether the new planning inventory and tests overclaim “last English-only surface” while the page still contains older English-only or English-leading copy elsewhere, so I’m checking the inventory doc against the actual HTML.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11-15d Surface Inventory — approval-flow polish
     2	
     3	> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
     4	>
     5	> Closes the last English-only surface in the workbench demo: the
     6	> Approval Center lane labels + buttons + pending-lane body copy.
     7	
     8	## Surface diff inventory
     9	
    10	| # | Surface | Type | Anchor | Notes |
    11	|---|---|---|---|---|
    12	| 1 | h3 `Pending` → `待审 · Pending` | [REWRITE] | `workbench.html:384` | Approval Center pending-lane heading. |
    13	| 2 | Pending body `Submitted annotation proposals wait here before acceptance or rejection.` → bilingual `已提交的标注提案在被通过或驳回前在此排队 · ...` | [REWRITE] | `workbench.html:385` | Pending-lane explanatory copy. |
    14	| 3 | h3 `Accept` → `通过 · Accept` | [REWRITE] | `workbench.html:388` | Accept-lane heading. |
    15	| 4 | btn `Accept Proposal` → `通过提案 · Accept Proposal` | [REWRITE] | `workbench.html:389` | Accept-lane action button. |
    16	| 5 | h3 `Reject` → `驳回 · Reject` | [REWRITE] | `workbench.html:392` | Reject-lane heading. |
    17	| 6 | btn `Reject Proposal` → `驳回提案 · Reject Proposal` | [REWRITE] | `workbench.html:393` | Reject-lane action button. |
    18	
    19	## Out of scope (deliberately preserved)
    20	
    21	- **API remediation message** in `demo_server.py:743` — backend
    22	  contract, locked by
    23	  `tests/test_lever_snapshot_manual_override_guard.py:151`.
    24	- **Approval Center entry button + Kogami-only caption** — already
    25	  bilingualized by E11-15b PR #25.
    26	- **`approval-center-title` h2** — already bilingualized by E11-15b
    27	  PR #25.
    28	- **`workbench.js` / `workbench.css`** — pure HTML sweep.
    29	- **`data-approval-action`/`data-approval-lane` attributes** — preserved
    30	  as structural anchors for any JS bindings or e2e selectors.
    31	
    32	## Tier-trigger evaluation
    33	
    34	Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
    35	
    36	> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
    37	
    38	- **copy_diff_lines** = 6 → < 10
    39	- **[REWRITE/DELETE] count** = 6 → ≥ 3
    40	
    41	→ **Tier-B** (1-persona review).
    42	
    43	> **Verdict: Tier-B**. Persona = **P2 (Senior FCS Engineer)** —
    44	> derived programmatically by
    45	> `python3 tools/codex_persona_dispatch.py next-persona` (returned `P2`
    46	> as the round-robin successor of E11-10's P1). First sub-phase to use
    47	> the E11-10 tooling for persona selection.
    48	
    49	## Behavior contract (locked by tests)
    50	
    51	`tests/test_workbench_approval_flow_polish.py` (NEW, 25 tests):
    52	
    53	1. 6 new bilingual strings positively asserted.
    54	2. 5 stale English-only patterns asserted absent.
    55	3. 6 English suffixes preserved (`Pending</h3>`, `Accept Proposal</button>`, etc.).
    56	4. 6 structural anchors (data-approval-lane / data-approval-action /
    57	   workbench-approval-grid class) asserted unchanged.
    58	5. Live-served `/workbench` route serves all 6 new bilingual strings.
    59	6. Backend isolation: `demo_server.py` remediation message unchanged
    60	   AND no Chinese leak into the backend file.
    61	
    62	## Truth-engine red line
    63	
    64	Files touched:
    65	- `src/well_harness/static/workbench.html` — 6 strings flipped
    66	- `tests/test_workbench_approval_flow_polish.py` — NEW (25 tests)
    67	- `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md` — NEW
    68	- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended (via tool)
    69	
    70	Files NOT touched: `controller.py`, `runner.py`, `models.py`,
    71	`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
    72	`demo_server.py`. Truth-engine boundary preserved.
    73	
    74	## Closure summary
    75	
    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
    77	- E11-15: 5 eyebrows
    78	- E11-15b: h1 + 2 buttons + h2 + entry button + caption + h2
    79	- E11-15c: 3 column h2s + page eyebrow dedup
    80	- **E11-15d: 3 lane h3s + 2 lane buttons + 1 body copy** (this sub-phase)
    81	
    82	The only remaining English-only string is the API remediation message
    83	in `demo_server.py:743`, which is backend contract and intentionally
    84	preserved.

exec
/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md | tail -n 40' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    18	E11-08: Tier-B (4 copy_diff_lines, 0 [REWRITE/DELETE]). Persona = P1 (Junior FCS Engineer — round-robin wraps P5 → P1 AND content-fit for small UI-only refactor with regression-risk JS attribute reading + URL-param parsing).
    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
    20	E11-15b: Tier-B (7 copy_diff_lines, 7 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P3 (Demo Presenter — round-robin successor of P2 AND content-fit: typography/reading-rhythm/first-glance demo impression is P3's core lens). Bilingualizes h1 + 2 buttons + h2 + approval entry button + caption + h2 to `<中文> · <English>`, preserving English suffixes for dual-route test locks. API remediation message in demo_server.py:743 explicitly preserved (backend contract).
    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
    22	E11-11: Tier-B (0 copy_diff_lines — pure infra + bug fix). Persona = P5 (Apps Engineer — round-robin successor of P4 AND content-fit: P5 reviews end-user-facing reproducibility, browser boot health, and shipped-flow integrity, exactly what the new e2e + bundle-page bug fix needs). Closes deferred JS verification debt from E11-08/13/15c via Playwright smoke suite (8 tests, opt-in `pytest -m e2e`). The first run of the new bundle-page boot test surfaced a latent variable-shadowing bug at workbench.js:1224 (renderFingerprintDocumentList), which is fixed in lockstep along with a sibling shadow at line 1649. Static-source guard test added so the regression is caught even when e2e is deselected.
    23	E11-10: Tier-B (0 copy_diff_lines — pure tooling). Persona = P1 (Junior FCS Engineer — round-robin successor of P5 AND content-fit: small focused tooling with regression-risk concerns (regex parsing, round-robin arithmetic, file-system side-effects) is exactly P1's lens). Adds tools/codex_persona_dispatch.py with 4 subcommands (dispatch / collect / next-persona / append-rotation) and 34 tests covering verdict parser, finding counter, tokens parser, round-robin arithmetic, rotation-state parse + roundtrip, and end-to-end collect.
    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)

codex
I’ve confirmed the HTML anchors themselves are unchanged. I’m doing one more pass through `workbench.js` to confirm those attributes are in fact the real binding points, so the approval buttons remain mechanically safe and this stays a pure copy-only slice.
exec
/bin/zsh -lc 'rg -n "data-approval-action|data-approval-lane|approval-center|approval-action|approval-lane" src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
3971:  const entry = document.getElementById("approval-center-entry");
3972:  const panel = document.getElementById("approval-center-panel");

exec
/bin/zsh -lc "rg -n \"Hide for session|Pending Kogami sign-off|No proposals submitted yet|Waiting for .* panel boot|What \\\"manual feedback\\\" means here|Truth Engine — Read Only\" src/well_harness/static/workbench.html" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
209:            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
225:          Hide for session
248:          Truth Engine — Read Only
278:            Waiting for probe &amp; trace panel boot.
298:            Waiting for annotate &amp; propose panel boot.
318:            Waiting for hand off &amp; track panel boot.
337:          <li>No proposals submitted yet.</li>
363:          <strong>Pending Kogami sign-off</strong>

codex
The `id`-based approval-center boot path is present in `workbench.js`. I didn’t find a same-file selector use for `data-approval-action` / `data-approval-lane`, so I’m checking repo-wide before I describe those as live JS binding points rather than preserved structural hooks.
exec
/bin/zsh -lc 'rg -n "data-approval-action|approval-action|data-approval-lane|approval-lane" .' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3960,4045p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
./src/well_harness/static/workbench.css:642:.workbench-approval-lane {
./src/well_harness/static/workbench.css:650:.workbench-approval-lane p {
./src/well_harness/static/workbench_start.html:154:        没有 approval-action handler</strong>，按钮点了不会落账（对 Kogami 也不会）。
./src/well_harness/static/workbench_start.html:159:        <li>data-approval-role="KOGAMI" + data-approval-action 锚点已就位</li>
./src/well_harness/static/workbench.html:383:          <article class="workbench-approval-lane" data-approval-lane="pending">
./src/well_harness/static/workbench.html:387:          <article class="workbench-approval-lane" data-approval-lane="accept">
./src/well_harness/static/workbench.html:389:            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">通过提案 · Accept Proposal</button>
./src/well_harness/static/workbench.html:391:          <article class="workbench-approval-lane" data-approval-lane="reject">
./src/well_harness/static/workbench.html:393:            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">驳回提案 · Reject Proposal</button>
./tests/test_workbench_approval_center.py:90:        assert f'data-approval-lane="{lane}"' in html
./tests/test_workbench_approval_flow_polish.py:122:        'data-approval-lane="pending"',
./tests/test_workbench_approval_flow_polish.py:123:        'data-approval-lane="accept"',
./tests/test_workbench_approval_flow_polish.py:124:        'data-approval-lane="reject"',
./tests/test_workbench_approval_flow_polish.py:125:        'data-approval-action="accept"',
./tests/test_workbench_approval_flow_polish.py:126:        'data-approval-action="reject"',

 succeeded in 0ms:
  3960	// When the workbench identity is NOT Kogami, replace the Approval Center
  3961	// entry button + panel with an explicit "Pending Kogami sign-off"
  3962	// affordance instead of leaving disabled UI in place. setWorkbenchIdentity
  3963	// is exported on window for tests + URL-param-driven demo flow.
  3964	function applyRoleAffordance() {
  3965	  const chip = document.getElementById("workbench-identity");
  3966	  if (!chip) {
  3967	    return;
  3968	  }
  3969	  const identity = chip.getAttribute("data-identity-name") || "";
  3970	  const isKogami = identity.trim() === "Kogami";
  3971	  const entry = document.getElementById("approval-center-entry");
  3972	  const panel = document.getElementById("approval-center-panel");
  3973	  const affordance = document.getElementById(
  3974	    "workbench-pending-signoff-affordance",
  3975	  );
  3976	  if (entry) {
  3977	    entry.hidden = !isKogami;
  3978	    entry.setAttribute("aria-disabled", isKogami ? "false" : "true");
  3979	  }
  3980	  if (panel) {
  3981	    panel.hidden = !isKogami;
  3982	  }
  3983	  if (affordance) {
  3984	    affordance.setAttribute(
  3985	      "data-pending-signoff",
  3986	      isKogami ? "hidden" : "visible",
  3987	    );
  3988	  }
  3989	}
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

codex
The anchors are preserved, but repo-wide evidence says they are preserved selectors more than active runtime bindings today. I’m checking the existing approval-center contract test and the starter-page note so I can phrase that distinction precisely.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench_start.html | sed -n '148,164p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_approval_center.py | sed -n '1,180p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   148	      <h2 class="ws-tile-title">Approval Center · 静态 shell 占位</h2>
   149	      <p class="ws-tile-subtitle">label 上写 Kogami-only · 角色判定逻辑未实现</p>
   150	      <p class="ws-tile-desc">
   151	        落到 <code>/workbench</code> 底栏的 Approval Center 入口。 当前
   152	        是静态 HTML：3 道 lane（Pending / Accept / Reject）+ 两个按钮 + 一句
   153	        "Approval actions are Kogami-only" 的告示文案。 <strong>workbench.js
   154	        没有 approval-action handler</strong>，按钮点了不会落账（对 Kogami 也不会）。
   155	        hash-chain 查阅 / SHA 分组 / JSONL 导出 / 状态过滤 / 角色判定都是 E11-08 范围，
   156	        本期只是给后续 phase 留好 selector 锚点。
   157	      </p>
   158	      <ul class="ws-tile-bullets">
   159	        <li>data-approval-role="KOGAMI" + data-approval-action 锚点已就位</li>
   160	        <li>Pending lane 当前只是占位文案，没有真实 proposal 列表</li>
   161	        <li>角色判定 / 实际签批落账逻辑完全在 E11-08 后</li>
   162	      </ul>
   163	      <span class="ws-tile-arrow">→</span>
   164	    </a>

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

codex
I’ve got enough to separate the copy slice from the stronger marketing claim. I’m running the existing approval-center contract test alongside the new polish tests once, so the final verdict can distinguish “this diff is mechanically safe” from “the page-wide Chinese-first closure claim is still not true.”
exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
html = Path('src/well_harness/static/workbench.html').read_text(encoding='utf-8')
for needle in [
    'Hide for session',
    'Pending Kogami sign-off',
    'Truth Engine — Read Only',
    'No proposals submitted yet.',
    'Causal Chain · 因果链走读',
    'Monte Carlo · 1000-trial 可靠性',
    'Reverse Diagnose · 反向诊断',
]:
    print(f\"{needle}: {'YES' if needle in html else 'NO'}\")
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
Hide for session: YES
Pending Kogami sign-off: YES
Truth Engine — Read Only: YES
No proposals submitted yet.: YES
Causal Chain · 因果链走读: YES
Monte Carlo · 1000-trial 可靠性: YES
Reverse Diagnose · 反向诊断: YES

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_approval_center.py tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 889ms:
.............................                                            [100%]
29 passed in 0.57s

codex
I have the review outcome. Before I write it up, I’m grabbing the exact MEMORY.md line numbers I used for this repo context so the final response can include the required memory citation block cleanly and only once.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '899,930p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
**CHANGES_REQUIRED**

- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.

- INFO `src/well_harness/static/workbench.html:383-393`: the approval-flow copy itself reads correctly for an FCS engineer workspace. `待审 / 通过 / 驳回` is the right concise triage vocabulary; I would keep it over `待批 / 批准 / 拒绝`.
- INFO `src/well_harness/static/workbench.html:383-393`, `tests/test_workbench_approval_center.py:84-90`, `src/well_harness/demo_server.py:741-744`: structural integrity is preserved. `data-approval-lane` and `data-approval-action` remain intact, the backend remediation string stays English, and `rg` found no `待审 / 通过提案 / 驳回提案 / 已提交的标注提案` leakage into `demo_server.py`.
- INFO `src/well_harness/static/workbench.js:3971-3982`, `src/well_harness/static/workbench_start.html:153-160`: these `data-approval-*` markers are preserved structural hooks, but I do not see evidence in the current repo that they are active JS binding points today; `workbench.js` toggles the entry/panel by `id`, and the starter page still says there is no `approval-action` handler yet. Not a regression, just wording precision.

Approval-center polish passed the mechanical checks: `pytest -q tests/test_workbench_approval_center.py tests/test_workbench_approval_flow_polish.py` returned `29 passed`, and a live local probe of `GET /workbench` returned `200` with all expected E11-15d approval strings present. Truth-engine red line is preserved: `git diff --name-only main..288d322` touches only `.planning/*`, `src/well_harness/static/workbench.html`, and `tests/test_workbench_approval_flow_polish.py`; no changes to `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, `workbench.css`, or `demo_server.py`.

**P2 — Senior FCS Engineer (Tier-B, E11-15d)**

tokens used
206,854
**CHANGES_REQUIRED**

- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.

- INFO `src/well_harness/static/workbench.html:383-393`: the approval-flow copy itself reads correctly for an FCS engineer workspace. `待审 / 通过 / 驳回` is the right concise triage vocabulary; I would keep it over `待批 / 批准 / 拒绝`.
- INFO `src/well_harness/static/workbench.html:383-393`, `tests/test_workbench_approval_center.py:84-90`, `src/well_harness/demo_server.py:741-744`: structural integrity is preserved. `data-approval-lane` and `data-approval-action` remain intact, the backend remediation string stays English, and `rg` found no `待审 / 通过提案 / 驳回提案 / 已提交的标注提案` leakage into `demo_server.py`.
- INFO `src/well_harness/static/workbench.js:3971-3982`, `src/well_harness/static/workbench_start.html:153-160`: these `data-approval-*` markers are preserved structural hooks, but I do not see evidence in the current repo that they are active JS binding points today; `workbench.js` toggles the entry/panel by `id`, and the starter page still says there is no `approval-action` handler yet. Not a regression, just wording precision.

Approval-center polish passed the mechanical checks: `pytest -q tests/test_workbench_approval_center.py tests/test_workbench_approval_flow_polish.py` returned `29 passed`, and a live local probe of `GET /workbench` returned `200` with all expected E11-15d approval strings present. Truth-engine red line is preserved: `git diff --name-only main..288d322` touches only `.planning/*`, `src/well_harness/static/workbench.html`, and `tests/test_workbench_approval_flow_polish.py`; no changes to `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `workbench.js`, `workbench.css`, or `demo_server.py`.

**P2 — Senior FCS Engineer (Tier-B, E11-15d)**

