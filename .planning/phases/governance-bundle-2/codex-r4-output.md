2026-04-25T13:04:18.399967Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T13:04:18.400034Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc4bd-b694-7b71-818e-b69eb3046bc5
--------
user
You are reviewing governance bundle #2 R4 (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit fa4605b on top of 58426cf).

History:
- R1 (1f25bb5): CHANGES_REQUIRED — F1 BLOCKER tier-aware closure conflict, F2 IMPORTANT rollback divergence, F3 IMPORTANT trigger non-determinism
- R2 (419286b → e259a42): R1 + R2 fixes (4-doc cross-coherence)
- R3 (process crashed) → R3-fix (58426cf): README §命令模板 + §Cost residual drift fixed
- R3-retry (58426cf): CHANGES_REQUIRED — F1 IMPORTANT Tier-B selection rule/template divergence, F2 IMPORTANT E11-00-PLAN §3.6 temporally stale
- R4-fix (fa4605b, this PR): both R3-retry findings addressed

R4-fix changes (4 files, 12+/13- lines):
1. F1 fix — Tier-B selection SSOT: README:40 (rule table), README:116 (anti-bias #1), constitution.md:343 (canonical rule), RETRO §6.2:148 — all 4 spots reframed so `PERSONA-ROTATION-STATE.md` is the ONLY source of truth. Default = round-robin successor of last entry. Owner does not "override the round-robin"; owner "writes a non-default value to the state file". Hard constraint (no consecutive same persona) is rule-enforced, not owner-discretionary.
2. F2 fix — E11-00-PLAN §3.6 historicized: Action column relabeled "历史决策表 (landed as PR #14)", removed "5-persona pipeline tier-trigger 候选规则" subsection, replaced with "触发条件 (landed)" pointing to constitution as canonical. "未在 §3.6 立法 → 当时未在 §3.6 立法" past-tense. §3.6 + §3.6.1 + §3.7 now form a single linear decision-arc.

Files reviewed (R4 commit fa4605b):
- .planning/codex_personas/README.md (lines 40, 116)
- .planning/constitution.md (line 343)
- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md (line 148, §6.2)
- .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md (lines 155-168)

Your task: Issue formal R4 verdict. Verify:

1. Tier-B selection rule wording is now identical pattern across all 4 docs (state-file SSOT + default = round-robin successor + owner writes non-default + hard constraint = no consecutive repeat). No surviving "default starting P1 + owner override" mental model.
2. E11-00-PLAN §3.6 + §3.6.1 form a single coherent decision-arc — no surviving "candidate / pending" framing alongside "已落地 PR #14" claim.
3. constitution.md + README + RETRO + E11-00-PLAN all reference each other correctly (no orphan section pointers).
4. The RUNNABLE example (README §命令模板:73-81) and the RULE TEXT now describe the same Tier-B selection process.

Output format (verbatim):
```
VERDICT: APPROVE | CHANGES_REQUIRED
R3-retry-F1 (Tier-B SSOT): [resolved | drift] — <≤2 lines>
R3-retry-F2 (§3.6 historicized): [resolved | drift] — <≤2 lines>
Cross-doc convergence (rule + template + closure + rollback + counting cmd): [resolved | drift] — <≤2 lines>
NEW_R4_FINDINGS:
- <none | severity + ≤2 line summary>
```

Be ruthless. If the rule text and the runnable template still describe different processes (e.g., one says "owner override", other says "state file SSOT"), flag drift. If §3.6 + §3.6.1 still have any residual "candidate" wording, flag drift. If a new contradiction was introduced by the historicization, flag NEW_R4.

Reply only with structured output. No preamble.
codex
Reviewing R4 against the stated R3-retry findings. I’m checking the exact four files plus the commit diff so the verdict is based on the landed text, not the summary.
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

exec
/bin/zsh -lc 'rg -n "LogicMVP|governance bundle|persona|tier" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
238:- rollout_summaries/2026-04-20T18-07-19-PTSo-codex_gpt54_fast_mode_xhigh_claude_code.md (cwd=/Users/Zhuanz/Documents/Codex/2026-04-21-codex, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/21/rollout-2026-04-21T02-07-19-019dac13-4e3e-76c1-a49b-5f78e234ce70.jsonl, updated_at=2026-04-21T01:39:09+00:00, thread_id=019dac13-4e3e-76c1-a49b-5f78e234ce70, CLI catalog checked; separate fast tier not exposed)
242:- codex-cli, gpt-5.4, xhigh, fast mode, priority processing, service_tier, codex debug models, additional_speed_tiers, ~/.codex/config.toml, codex exec, codex review, cx-auto
247:- when asking about Codex speed modes, the user clarified "我是说1.5倍速度，2倍积分消耗的模式，仍然保持gpt-5.4-xhigh" -> separate provider, model, reasoning effort, and speed tier explicitly instead of answering with a blurred model-only explanation [Task 2]
254:- The installed Codex CLI already pins `model = "gpt-5.4"` and `model_reasoning_effort = "xhigh"` in `~/.codex/config.toml`, so the unresolved question was only the extra fast/priority tier [Task 2]
255:- `codex debug models` is the decisive check for CLI-exposed capabilities; in this environment `gpt-5.4` listed `supported_reasoning_levels = [low, medium, high, xhigh]` and `additional_speed_tiers = []` [Task 2]
256:- If the user truly needs the 1.5x / 2x priority mode while keeping `gpt-5.4` + `xhigh`, the durable path is a custom OpenAI API wrapper that sends `service_tier = "priority"` instead of relying on `codex exec` to expose it [Task 2]
261:- Symptom: the answer over-promises a config-only "fast mode" fix for Codex CLI -> cause: model name, reasoning effort, and service tier were conflated -> fix: inspect `codex debug models` and only promise knobs that the installed CLI actually exposes [Task 2]
277:- ElevenLabs, PVC, voice-cloning, Chinese TTS, 90 分钟中文探店博主语料结构表, VOICE-CORPUS-90MIN-PLAN.md, ELEVENLABS-VOICE-CORPUS-GUIDE.md, MATERIAL-DROPZONE.md, avatar-lab/inputs/persona/voice-pvc, 90-150 分钟, 20-30 分钟, 逛 / 光, pronunciation dictionaries, shop-explainer
287:- ElevenLabs voice-training materials in this project are organized under `avatar-lab/inputs/persona/voice-pvc/`; do not scatter PVC material inside transient job directories [Task 1]
304:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
310:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
320:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
791:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
793:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
794:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
800:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
804:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
810:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
811:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
821:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
822:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
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
1627:- Official Claude cloud-local handoff is not a one-click sync of local Claude Code sessions/memory/`.claude` config; the practical route is GitHub repo + Claude Project / GitHub integration / Claude Code on the web, with project rules separated from personal machine config [Task 3]
1739:- Claude leak, Mythos, Capybara, 10T parameters, evidence table, credibility tiers, official facts vs rumor, Anthropic risk report, OpenAI, Gemini, capability-route comparison
1743:- when the user asked for "深度研究Claude今天泄漏的新模型，10T参数规模" and then "按可信度做成证据表" -> do deep source-backed research with explicit credibility tiers, not a quick rumor summary [Task 1]
1749:- The user responds well to credibility labels like `高可信 / 中可信 / 低可信` and to dimensions such as context, agent/tool use, multimodality, safety/gating, and tiering [Task 1]

codex
Using `using-superpowers` for process discipline and treating this as a read-only review. I’m now diffing `58426cf..fa4605b` and reading the four touched sections side by side to test the exact wording against your four acceptance checks.
exec
/bin/zsh -lc 'git show --stat --oneline fa4605b' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
fa4605b docs(governance): bundle #2 R4 fixes — Tier-B selection SSOT + E11-00-PLAN §3.6 historicized
 .planning/codex_personas/README.md                      |  4 ++--
 .planning/constitution.md                               |  2 +-
 .../E11-workbench-engineer-first-ux/E11-00-PLAN.md      | 17 ++++++++---------
 .../retrospectives/RETRO-V61-054-ui-copy-probe-birth.md |  2 +-
 4 files changed, 12 insertions(+), 13 deletions(-)

exec
/bin/zsh -lc 'git diff --unified=40 58426cf..fa4605b -- .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/codex_personas/README.md b/.planning/codex_personas/README.md
index a1d95cf..e04d4bb 100644
--- a/.planning/codex_personas/README.md
+++ b/.planning/codex_personas/README.md
@@ -1,131 +1,131 @@
 # Codex Persona Review Pipeline
 
 > Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
 > Date: 2026-04-25
 > Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6
 
 ## Purpose
 
 5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape.
 
 **Anti-bias model (governance bundle #2, 2026-04-25):**
 - **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
 - **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
 
 See §Tier-trigger below for which tier fires when.
 
 ## Persona inventory
 
 | ID | Persona | File |
 |---|---|---|
 | P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
 | P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
 | P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
 | P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
 | P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |
 
 ## Invocation
 
 ### Tier-trigger（governance bundle #2 落地，2026-04-25 起生效）
 
 > **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
 >
 > v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
 
 按下表决定调多少 persona：
 
 | 子 phase 特征 | persona 数 | 选哪个 |
 |---|---|---|
 | user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | **`PERSONA-ROTATION-STATE.md` 是唯一 source of truth。** 默认值 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同 |
 
 **"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
 
 ```bash
 # 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
 git diff --stat $(git merge-base HEAD main)..HEAD -- \
   'src/well_harness/static/*.html' \
   'src/well_harness/static/*.js' \
   'src/well_harness/static/*.css'
 ```
 
 读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
 
 **轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
 
 **判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
 
 **例外（仍跑全 5）：**
 - 该子 phase 触发了 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
 - Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
 
 ### 命令模板
 
 ```bash
 # Tier-A（5 persona 并行，仅在条件满足时跑）：
 for p in P1 P2 P3 P4 P5; do
   cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
     "$(cat .planning/codex_personas/${p}-*.md)" \
     > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
 done
 wait
 
 # Tier-B（1 persona，跨-sub-phase 轮换 P1 → P2 → P3 → P4 → P5 → P1，起点 P1）：
 # 启动新 epic 第一个 Tier-B sub-phase 跑 P1；后续按 PERSONA-ROTATION-STATE.md 末行下一个值轮换。
 # 例：当期 epic 已记录 sub-phase X1: P1, X2: P2 → 当前 sub-phase 应跑 P3。
 PERSONA=P3  # 由 .planning/phases/<epic>/PERSONA-ROTATION-STATE.md 决定，不得与上一行 Tier-B sub-phase 重复
 cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
   "$(cat .planning/codex_personas/${PERSONA}-*.md)" \
   > .planning/phases/<phase-id>/persona-${PERSONA}-output.md 2>&1
 # commit 后追加一行到 PERSONA-ROTATION-STATE.md：
 # echo "<phase-id>: ${PERSONA} (<reason — content fit / round-robin>)" >> .planning/phases/<epic>/PERSONA-ROTATION-STATE.md
 ```
 
 ## Output convention
 
 Each persona writes verdict to its own file. Closure semantics depend on which tier ran:
 
 ### Tier-A（5-persona 并行）
 
 Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:
 
 - 5 verdicts side-by-side
 - Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
 - Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
 - 0 BLOCKER is a phase-CLOSURE precondition
 
 ### Tier-B（1-persona 默认）
 
 No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
 
 - 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
 - Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
 - 0 BLOCKER from that single persona is the phase-CLOSURE precondition
 - Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
 
 If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
 
 ## Anti-bias safeguard
 
 **Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
 1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
 2. Triggers re-run with sharpened persona contexts
 3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework
 
 **Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
-1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
+1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
 2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
 3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
 
 ## Cost / latency baseline (recorded for retro)
 
 **Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
 - PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
 - E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
 
 **Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
 - Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
 - Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
 - **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
 
 If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).
diff --git a/.planning/constitution.md b/.planning/constitution.md
index 783a994..5a1e0ae 100644
--- a/.planning/constitution.md
+++ b/.planning/constitution.md
@@ -303,81 +303,81 @@ scope=src/well_harness/static/workbench.js (grep "approval-action\|data-approval
 
 ##### 禁止格式（v2.3 失效条件之一）
 
 - `(absence claim — verified by absence of <X> in <file>)` —— 自然语言而非可执行 grep 命令
 - `<file>:<line-range> (peer description)` 不带 `scope=` 前缀但描述 peer feature —— 容易被误读为"grep 范围"
 - section-only 引用（如 `constitution.md §v5.2`）作为唯一 anchor——参见上面通用约束
 
 ### 与 v2.2 EMPIRICAL-CLAIM-PROBE 的关系
 - v2.2 治**数值/计算/百分比/SHA 等可量化断言**，对照源是计算复跑 / pytest / runs/。
 - v2.3 治**界面/行为/字段/角色等可定位断言**，对照源是 src/ ripgrep 锚点。
 - 两条并列触发，不互相覆盖；同一条 copy 同时含数值与 surface 时，必须双轨都过。
 
 ### 审查侧的展开
 - 评审者（Codex / 第二视角）有权要求作者贴出 §Surface Inventory；缺失或残缺直接 CHANGES_REQUIRED，不进入逐字 ripgrep round-trip。
 - 评审者抽查 §Surface Inventory 中任意一行的锚点是否真实成立；命中 fabricated 锚点 → 视为伪造证据（同 v5.2 反假装条款）。
 
 ### 失效条件
 - 作者声称已做 sweep 但 §Surface Inventory 缺失 / 行数与 copy 不对应 / 锚点 line 不存在 → 当轮 review 视为未做自审，要求重做（不是逐条修）。
 - 连续两期被外部 reviewer 抓出 ≥1 条 fabricated surface → 触发该 Phase Owner 的 self-pass-rate 校准复盘。
 
 ### Trailer
 任何含 user-facing copy 改动的 commit，message 末尾追加：
 `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`
 
 ### 来源
 - E11-02 PR #10 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（fabricated knowledge field 名、虚构 archive 行为、虚构 role gate、SHA256 vs commit-SHA 混淆、不存在的 wow_a UI 走读 surface）
 - Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
 - 详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md`
 
 ### Codex Persona Pipeline Tier-Trigger（governance bundle #2, 2026-04-25 起生效）
 
 **前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
 
 **实证：** E11-09 dual-h1 fix PR #13 落地于 2026-04-25，Codex 2 轮 APPROVE（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。leading indicator fired。
 
 **新规则（替换"每个 user-facing UI 子 phase 默认跑全 5"）：**
 
 | 条件 | persona 数 | 选哪个 |
 |---|---|---|
 | user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
 
 **"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
 
 ```bash
 git diff --stat $(git merge-base HEAD main)..HEAD -- \
   'src/well_harness/static/*.html' \
   'src/well_harness/static/*.js' \
   'src/well_harness/static/*.css'
 ```
 
 读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
 
 **例外（仍跑全 5）：**
 - 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
 - Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
 
 **判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
 
 **保留不变：**
 - v2.2 EMPIRICAL-CLAIM-PROBE 的全部触发条件
 - v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
 - v6.1 Codex 触发清单（多文件 UI / API 契约 / OpenFOAM solver / CFD 几何 / Phase E2E 失败 / Docker+OpenFOAM / GSD 产出物等）
 - §RETRO 序号、Self-Pass-Rate 强制、Hard Stop Points、Verbatim Exception
 
 **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
 
 **回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
 
 1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
 2. 开新 RETRO-V61-* 文件记录失败摊销，链接到 RETRO-V61-054
 3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
 
 详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
 
 **详细文档：** `.planning/codex_personas/README.md` §Invocation 表，更新于本 bundle。RETRO-V61-054 §6 amortization 实证记录。
 
 ### Verbatim Exception（继承 v6.0，五条件 AND）
 
 允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
 
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
index 2dad3c0..2d5788a 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
@@ -115,94 +115,93 @@
 
 > **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
 
 ---
 
 ## 3.5 执行排序（Opus 4.7 strategic input · 2026-04-25）
 
 > 数据源：Notion @Opus 4.7 异步会话，2026-04-25。审查范围 = E11-02 + v2.3 governance bundle 落地后的 strategic review。
 > 完整 Opus 输出存档在 PR #11 description / Notion 04 决策日志 DB。
 
 ### 排序（next 6 sub-phases）
 
 ```
 E11-09 → E11-13/14 → E11-05 → E11-03 → E11-04 → E11-06
 ```
 
 **逐项理由**（Opus 4.7 verbatim）：
 
 1. **E11-09 dual-h1 修复** — 30 秒 quick win，先清债（双 h1 是身份分裂遗债），同时作为 §3.6 leading indicator 量度 governance 摊销。
 2. **E11-13 + E11-14 manual_feedback_override 修复** — 提前到第 2 而非第 3。**关键 reframe**: 不是 authority-chain breach（873 + adversarial 8/8 已证 truth-engine 没被越权），是 **UI affordance 让用户*看起来*越权**——比 demo BLOCKER 更污染信任。修复在 UI / 服务端 endpoint guard 两层，不进 controller。
 3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
 4. **E11-03 三列重命名** — P1 / P2 工程师任务命名升级。
 5. **E11-04 annotation 词汇升级** — P1 / P2 / P5 domain anchoring。
 6. **E11-06 status bar** — 基础设施收尾。
 
 ### Opus 4.7 拒绝的备选
 
 - **B（直接全做 P2-1 truth-boundary fix 链 + 其他都推后）**：拒绝。错在把"看起来越权"上升为 R1-R5 红线 fix——是过度反应。
 - **C（先做 E11-12 closure 收 phase 再换新 phase）**：拒绝。18 子 phase 没做先 closure 是伪闭环。
 
 ### E11-15..19 的位置
 
 不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
 
 ---
 
 ## 3.6 Leading Indicator · E11-09 ≤ 2 Codex 轮 = governance 摊销证据
 
 > Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。
 
-**E11-09 是 governance machinery 是否过载的实证 gate**：
+**E11-09 是 governance machinery 是否过载的实证 gate**（已 fired 2026-04-25 — §3.6.1 OUTCOME 见下）：
 
-| E11-09 Codex 轮数 | 解读 | Action |
+| E11-09 Codex 轮数 | 解读 | Action（历史决策表） |
 |---|---|---|
-| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
-| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
+| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（landed as `governance bundle #2`, PR #14, 2026-04-25） |
+| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（hypothetical：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
 | ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
 
-**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
-- 触发条件 = (a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE]
-- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
-- v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**
+**触发条件（landed）**：(a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] → Tier-A (5 personas 并行)。否则 → Tier-B (1 persona, `PERSONA-ROTATION-STATE.md` 选 persona)。完整规则在 `constitution.md` §Codex Persona Pipeline Tier-Trigger（governance bundle #2 落地版本）；本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧。
 
-**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
+**保留不变**：v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**。
+
+**当时未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性 *曾 取决于* E11-09 结果——E11-09 跑完前不写进 constitution。E11-09 ≤2 轮 APPROVE fired 后，governance bundle #2 才作为 PR #14 落 constitution（详见 §3.6.1）。
 
 ### 3.6.1 Leading Indicator OUTCOME — fired ≤2 rounds (2026-04-25)
 
 E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。R1 的 BLOCKER 不是 honesty 类（不是 fabricated surface claim），是**真实 runtime bug**（workbench.js 共享 shell + bundle 但 binding bundle-only 元素无 null guard），属于 reactive review 正常工作。
 
 **Action 触发**：governance bundle #2 已通过 PR #14 落地（2026-04-25）：
 
 - `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
 - `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
 - 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
 
 **Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
 
 **回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
 
 **详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
 
 ---
 
 ## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
 
 **目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。
 
 **条件解锁**：满足全部 3 条后可并发启动一个**不动 src/** 的 E12 spec phase（如 fault diagnosis 的 PRD + intake packet schema）：
 1. E11-09 ≤ 2 轮 Codex APPROVE（证 v2.3 摊销）
 2. E11-06 完成（E11-15..19 进入纯前端期）
 3. 该 E12 候选明确不动 `src/well_harness/{controller,runner,models,plant}.py` / `adapters/` / `tests/e2e/test_wow_a*`
 
 **理由**：并发 src/ phase 会拉高 truth-engine 触碰风险且让"v2.3 摊销 vs bloat"归因失败（两个 phase 同时跑 Codex 会污染 leading indicator 数据）。
 
 ---
 
 ## 4. Tier-1 Adversarial Self-Review（v5.2 红线 #3 强制）
 
 > 三个最强自我反对意见 + 显式 rebuttal。
 
 ### Counterargument #1: "为什么不让真工程师上手反馈再改？"
 
 **反对论点**: pre-emptive UX 工作可能优化错的方向。等到第一个 customer-facing 工程师 onboard 时再迭代，更省成本，避免 design-by-imagination。
 
diff --git a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
index cd17ce7..97aef9f 100644
--- a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
+++ b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
@@ -108,81 +108,81 @@ The legislation PR (this PR — `feat/E11-02b-v23-ui-copy-probe-20260425`) took
 
 **Meta-lessons** (filed for future v2.X legislation):
 
 1. **Recursive honesty boundary** — the worked example demonstrating the rule must itself pass the rule. Codex R2 caught a fabricated peer feature (3 buttons claimed; only 2 exist) inside the very inventory used to demonstrate v2.3. Reflex when authoring legislation: **after each rule edit, grep-validate every example sentence against current src.** Self-application is mandatory.
 
 2. **Spec coherence drift across iterations** — R3 / R4 each added new wording while leaving older wording in place. By R4, three different sentences gave three subtly different cardinality rules. Reflex when revising spec: **collapse to single-source-of-truth form (subsections with explicit "仅此一字段为必填" wording) rather than appending new prose alongside the old.** Three statements of the same rule = three places to disagree.
 
 3. **5-round legislation cost** — averaging 130k tokens per round, the v2.3 PR consumed ~650k Codex tokens. This is acceptable as a one-time legislative cost (the rule covers all future user-facing UI phases), but signals the marginal cost of rule-while-applying. Future legislation should consider drafting on a *separate* worked example so the rule is canonical before being applied retroactively.
 
 The meta-loop itself is evidence that v2.3 works: Codex correctly used v2.3's own anchor-format rule to identify the worked-example-violates-rule problem, and used it again to identify spec-coherence drift. The rule is self-consistent because Codex's review process — running the rule on the document defining it — would have terminated faster (or not at all) if the rule had been internally inconsistent.
 
 ---
 
 ## 6. Amortization confirmation — E11-09 leading indicator fired (2026-04-25)
 
 Opus 4.7 §1 strategic review (2026-04-25) set E11-09 dual-h1 fix as the **leading indicator** for whether v2.3 UI-COPY-PROBE has been amortized. Decision rule:
 
 | E11-09 Codex 轮数 | 解读 | Action |
 |---|---|---|
 | ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
 | 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档 |
 | ≥ 4 轮 | governance 失效 | Opus 4.7 再介入诊断 |
 
 ### 6.1 Outcome — E11-09 PR #13
 
 **Total rounds: 2 (R1 BLOCKER → R2 APPROVE).**
 
 | Round | Verdict | Type of finding | Was it honesty-related? |
 |---|---|---|---|
 | R1 | BLOCKER | F1: real JS error — `workbench.js` shared between routes, unconditionally bound 14+ bundle-only DOM elements that don't exist on shell route. F2 IMPORTANT: test coverage didn't catch JS boot path. | **No.** F1 is a runtime bug (TypeError on null .addEventListener), found by Codex's empirical Node-level reasoning. Not a fabricated-surface-claim issue. F2 is missing-test-coverage of the bug. Both are *real engineering defects*, caught by reactive review working as intended. |
 | R2 | APPROVE | none | (CLEAN) |
 
 **Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
 
 ### 6.2 governance bundle #2 — persona pipeline tier-trigger
 
 Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
 
 **5-persona pipeline → tier-trigger:**
 - Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
-- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
+- Tier-B (1 persona): all other cases. `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source-of-truth for persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of last entry; new epic = P1. Owner may write a non-default value (content fit, e.g., demo-arc → P3); hard constraint: written value must not equal the immediately preceding Tier-B entry. Sequence resets per epic.
 
 Landed in:
 - `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)
 - `.planning/codex_personas/README.md` §Invocation table (this PR)
 - Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
 
 **Things NOT changed:**
 - v2.2 EMPIRICAL-CLAIM-PROBE triggers
 - v2.3 §UI-COPY-PROBE triggers / §Surface Inventory mandate / §Anchor 格式细则
 - v6.1 Codex trigger list
 - RETRO numbering / Self-Pass-Rate strict / Hard Stop Points / Verbatim Exception 5 conditions
 
 ### 6.3 Rollback condition (codified)
 
 If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
 1. Roll back to default 5-persona for the next 3 sub-phases
 2. Open a successor RETRO-V61-* documenting the failed amortization
 3. Re-engage Opus 4.7 strategic review
 
 ### 6.4 Cost estimate
 
 - Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
 - Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
 - Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
 - Estimated savings on persona pipeline: **~70–80%** Codex tokens
 - E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
 
 ### 6.5 Meta-observation
 
 The Leading Indicator pattern (set a binary outcome that determines next governance action *before* the first observation) is itself a methodology artifact worth retaining. It avoids both extremes:
 - "Codify rules pre-emptively" (v2.3 PR's 5-round trap — the rule had to be defined while applied to itself)
 - "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)
 
 Future v2.X legislation should consider committing leading indicators alongside the rule, not after.
 
 ---
 
 ## 7. Open questions
 
 - **Q1**：是否要把 §Surface Inventory 抽象成 `tools/inventory_check.py` 自动化校验脚本（grep 锚点行真实存在）？现状是手动 + Codex 抽查。

exec
/bin/zsh -lc 'git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/governance-bundle-2/

codex
The landed diff removed the old “owner override / default P1” phrasing from the rule tables. I’m checking the live line-numbered text now for any residual stale wording in the same files and for whether the runnable Tier-B snippet still implies a different operator model.
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '332,370p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '32,130p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '150,178p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md | sed -n '140,170p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   332	### Codex Persona Pipeline Tier-Trigger（governance bundle #2, 2026-04-25 起生效）
   333	
   334	**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
   335	
   336	**实证：** E11-09 dual-h1 fix PR #13 落地于 2026-04-25，Codex 2 轮 APPROVE（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。leading indicator fired。
   337	
   338	**新规则（替换"每个 user-facing UI 子 phase 默认跑全 5"）：**
   339	
   340	| 条件 | persona 数 | 选哪个 |
   341	|---|---|---|
   342	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
   343	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
   344	
   345	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
   346	
   347	```bash
   348	git diff --stat $(git merge-base HEAD main)..HEAD -- \
   349	  'src/well_harness/static/*.html' \
   350	  'src/well_harness/static/*.js' \
   351	  'src/well_harness/static/*.css'
   352	```
   353	
   354	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
   355	
   356	**例外（仍跑全 5）：**
   357	- 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
   358	- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
   359	
   360	**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
   361	
   362	**保留不变：**
   363	- v2.2 EMPIRICAL-CLAIM-PROBE 的全部触发条件
   364	- v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
   365	- v6.1 Codex 触发清单（多文件 UI / API 契约 / OpenFOAM solver / CFD 几何 / Phase E2E 失败 / Docker+OpenFOAM / GSD 产出物等）
   366	- §RETRO 序号、Self-Pass-Rate 强制、Hard Stop Points、Verbatim Exception
   367	
   368	**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
   369	
   370	**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：

 succeeded in 0ms:
   150	
   151	## 3.6 Leading Indicator · E11-09 ≤ 2 Codex 轮 = governance 摊销证据
   152	
   153	> Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。
   154	
   155	**E11-09 是 governance machinery 是否过载的实证 gate**（已 fired 2026-04-25 — §3.6.1 OUTCOME 见下）：
   156	
   157	| E11-09 Codex 轮数 | 解读 | Action（历史决策表） |
   158	|---|---|---|
   159	| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（landed as `governance bundle #2`, PR #14, 2026-04-25） |
   160	| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（hypothetical：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
   161	| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
   162	
   163	**触发条件（landed）**：(a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] → Tier-A (5 personas 并行)。否则 → Tier-B (1 persona, `PERSONA-ROTATION-STATE.md` 选 persona)。完整规则在 `constitution.md` §Codex Persona Pipeline Tier-Trigger（governance bundle #2 落地版本）；本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧。
   164	
   165	**保留不变**：v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**。
   166	
   167	**当时未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性 *曾 取决于* E11-09 结果——E11-09 跑完前不写进 constitution。E11-09 ≤2 轮 APPROVE fired 后，governance bundle #2 才作为 PR #14 落 constitution（详见 §3.6.1）。
   168	
   169	### 3.6.1 Leading Indicator OUTCOME — fired ≤2 rounds (2026-04-25)
   170	
   171	E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。R1 的 BLOCKER 不是 honesty 类（不是 fabricated surface claim），是**真实 runtime bug**（workbench.js 共享 shell + bundle 但 binding bundle-only 元素无 null guard），属于 reactive review 正常工作。
   172	
   173	**Action 触发**：governance bundle #2 已通过 PR #14 落地（2026-04-25）：
   174	
   175	- `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
   176	- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
   177	- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
   178	

 succeeded in 0ms:
   140	**Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
   141	
   142	### 6.2 governance bundle #2 — persona pipeline tier-trigger
   143	
   144	Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
   145	
   146	**5-persona pipeline → tier-trigger:**
   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
   148	- Tier-B (1 persona): all other cases. `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source-of-truth for persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of last entry; new epic = P1. Owner may write a non-default value (content fit, e.g., demo-arc → P3); hard constraint: written value must not equal the immediately preceding Tier-B entry. Sequence resets per epic.
   149	
   150	Landed in:
   151	- `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)
   152	- `.planning/codex_personas/README.md` §Invocation table (this PR)
   153	- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
   154	
   155	**Things NOT changed:**
   156	- v2.2 EMPIRICAL-CLAIM-PROBE triggers
   157	- v2.3 §UI-COPY-PROBE triggers / §Surface Inventory mandate / §Anchor 格式细则
   158	- v6.1 Codex trigger list
   159	- RETRO numbering / Self-Pass-Rate strict / Hard Stop Points / Verbatim Exception 5 conditions
   160	
   161	### 6.3 Rollback condition (codified)
   162	
   163	If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
   164	1. Roll back to default 5-persona for the next 3 sub-phases
   165	2. Open a successor RETRO-V61-* documenting the failed amortization
   166	3. Re-engage Opus 4.7 strategic review
   167	
   168	### 6.4 Cost estimate
   169	
   170	- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase

 succeeded in 0ms:
    32	>
    33	> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
    34	
    35	按下表决定调多少 persona：
    36	
    37	| 子 phase 特征 | persona 数 | 选哪个 |
    38	|---|---|---|
    39	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
    40	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | **`PERSONA-ROTATION-STATE.md` 是唯一 source of truth。** 默认值 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同 |
    41	
    42	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
    43	
    44	```bash
    45	# 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
    46	git diff --stat $(git merge-base HEAD main)..HEAD -- \
    47	  'src/well_harness/static/*.html' \
    48	  'src/well_harness/static/*.js' \
    49	  'src/well_harness/static/*.css'
    50	```
    51	
    52	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
    53	
    54	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
    55	
    56	**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
    57	
    58	**例外（仍跑全 5）：**
    59	- 该子 phase 触发了 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
    60	- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
    61	
    62	### 命令模板
    63	
    64	```bash
    65	# Tier-A（5 persona 并行，仅在条件满足时跑）：
    66	for p in P1 P2 P3 P4 P5; do
    67	  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    68	    "$(cat .planning/codex_personas/${p}-*.md)" \
    69	    > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
    70	done
    71	wait
    72	
    73	# Tier-B（1 persona，跨-sub-phase 轮换 P1 → P2 → P3 → P4 → P5 → P1，起点 P1）：
    74	# 启动新 epic 第一个 Tier-B sub-phase 跑 P1；后续按 PERSONA-ROTATION-STATE.md 末行下一个值轮换。
    75	# 例：当期 epic 已记录 sub-phase X1: P1, X2: P2 → 当前 sub-phase 应跑 P3。
    76	PERSONA=P3  # 由 .planning/phases/<epic>/PERSONA-ROTATION-STATE.md 决定，不得与上一行 Tier-B sub-phase 重复
    77	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    78	  "$(cat .planning/codex_personas/${PERSONA}-*.md)" \
    79	  > .planning/phases/<phase-id>/persona-${PERSONA}-output.md 2>&1
    80	# commit 后追加一行到 PERSONA-ROTATION-STATE.md：
    81	# echo "<phase-id>: ${PERSONA} (<reason — content fit / round-robin>)" >> .planning/phases/<epic>/PERSONA-ROTATION-STATE.md
    82	```
    83	
    84	## Output convention
    85	
    86	Each persona writes verdict to its own file. Closure semantics depend on which tier ran:
    87	
    88	### Tier-A（5-persona 并行）
    89	
    90	Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:
    91	
    92	- 5 verdicts side-by-side
    93	- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
    94	- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
    95	- 0 BLOCKER is a phase-CLOSURE precondition
    96	
    97	### Tier-B（1-persona 默认）
    98	
    99	No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
   100	
   101	- 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
   102	- Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
   103	- 0 BLOCKER from that single persona is the phase-CLOSURE precondition
   104	- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
   105	
   106	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
   107	
   108	## Anti-bias safeguard
   109	
   110	**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
   111	1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
   112	2. Triggers re-run with sharpened persona contexts
   113	3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework
   114	
   115	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
   116	1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
   117	2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
   118	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
   119	
   120	## Cost / latency baseline (recorded for retro)
   121	
   122	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
   123	- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
   124	- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
   125	
   126	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
   127	- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
   128	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
   129	- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
   130	

codex
I’ve narrowed the remaining risk to two things: hidden stale wording outside the edited lines, and whether the Tier-B shell snippet still encodes a narrower process than the normative rule. I’m grepping the four docs for residual `candidate / 待立法 / override / 起点 P1 / round-robin` language and for every cross-reference that should still resolve after the historicization.
exec
/bin/zsh -lc "rg -n \"candidate|候选|待.*立法|override|覆盖|默认起点 P1|起点 P1|round-robin|PERSONA-ROTATION-STATE|§6\\.3|§6\\.|§3\\.6|README|constitution|RETRO-V61-054|Tier-Trigger|tier-trigger\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:1:# RETRO-V61-054 — UI-COPY-PROBE birth (E11-02 4-round arc + Opus 4.7 root-cause)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:7:> **Output artefacts:** constitution v2.3 §UI-COPY-PROBE; E11-00-PLAN §1.5 Surface Inventory template + 3 small differentials; `E11-02-SURFACE-INVENTORY.md` worked example
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:59:## 3. v2.3 立法输出（已 land 在 constitution.md）
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:61:完整规则正文移到 `.planning/constitution.md` §v2.3 · UI-COPY-PROBE。本 retro 只记三件事：
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:88:| `.planning/constitution.md` 加 §v2.3 UI-COPY-PROBE | ✅ 本 PR |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:92:| Codex review trigger 清单更新（v2.3 触发条件并列 v2.2，不互斥） | ✅ constitution.md 反映 |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:142:### 6.2 governance bundle #2 — persona pipeline tier-trigger
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:144:Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:**
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona): all other cases. `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source-of-truth for persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of last entry; new epic = P1. Owner may write a non-default value (content fit, e.g., demo-arc → P3); hard constraint: written value must not equal the immediately preceding Tier-B entry. Sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:151:- `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:152:- `.planning/codex_personas/README.md` §Invocation table (this PR)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:153:- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:202:- Constitution amendment: `.planning/constitution.md` §v2.3 (HEAD this PR)
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:96:| **E11-03** | 三列重命名 + 重排 — "Scenario Control / Spec / Circuit" → 工程师任务命名（候选：「Probe & Trace」「Annotate & Propose」「Hand off & Track」），保留底层 ID 不变以免 e2e 测试失效 | E11-01 | 不 |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:106:| **E11-13** | manual_feedback_override **trust-affordance 修复（UI/可视化层）** — 加警示 banner + 模式标识 chip + 失谐告警，让用户*看起来不再越权*。**不是** authority-chain breach 修复（873 + adversarial 8/8 已证 truth-engine 实际未被越权），而是 UI affordance 让用户对真值失去信任的"可视污染"修复。Opus 4.7 (2026-04-25) reframe；详见 §3.5。 | E11-01（P2-1 Reading B locked） | 不 |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:107:| **E11-14** | manual_feedback_override **服务端 role guard** — `/api/lever-snapshot` 对 manual_feedback_override 增 actor + ticket-binding 检查，未签 sign-off 时端点返回 409 而不是 200（仍不动 controller）。配合 E11-13 形成"UI 看不到 + 服务端拒绝"两道防线。 | E11-13 | 不（adapter boundary 内的 endpoint 守护，不进 controller / models / adapters/*.py 真值出口） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:133:1. **E11-09 dual-h1 修复** — 30 秒 quick win，先清债（双 h1 是身份分裂遗债），同时作为 §3.6 leading indicator 量度 governance 摊销。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:134:2. **E11-13 + E11-14 manual_feedback_override 修复** — 提前到第 2 而非第 3。**关键 reframe**: 不是 authority-chain breach（873 + adversarial 8/8 已证 truth-engine 没被越权），是 **UI affordance 让用户*看起来*越权**——比 demo BLOCKER 更污染信任。修复在 UI / 服务端 endpoint guard 两层，不进 controller。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:155:**E11-09 是 governance machinery 是否过载的实证 gate**（已 fired 2026-04-25 — §3.6.1 OUTCOME 见下）：
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（landed as `governance bundle #2`, PR #14, 2026-04-25） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**触发条件（landed）**：(a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] → Tier-A (5 personas 并行)。否则 → Tier-B (1 persona, `PERSONA-ROTATION-STATE.md` 选 persona)。完整规则在 `constitution.md` §Codex Persona Pipeline Tier-Trigger（governance bundle #2 落地版本）；本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:167:**当时未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性 *曾 取决于* E11-09 结果——E11-09 跑完前不写进 constitution。E11-09 ≤2 轮 APPROVE fired 后，governance bundle #2 才作为 PR #14 落 constitution（详见 §3.6.1）。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:175:- `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:176:- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:177:- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:181:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:183:**详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:189:**目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:194:3. 该 E12 候选明确不动 `src/well_harness/{controller,runner,models,plant}.py` / `adapters/` / `tests/e2e/test_wow_a*`
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:214:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:226:**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:232:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:304:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:316:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:322:9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:330:3. 三列 verb 命名候选 "Probe & Trace / Annotate & Propose / Hand off & Track" 还是更激进的 "What-If / Mark / Hand off"？（默认: 前者，与现有 button 文案对齐）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:344:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/constitution.md:3:> **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append + governance bundle #2 persona tier-trigger amortization)
.planning/constitution.md:9:> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:109:| P32 | Provenance Backfill — v4.0 追认 + Milestone 9 Lifted + constitution v2.1 | In progress (2026-04-20, v5.2 solo-signed; `GATE-P32-PLAN: Approved` 2026-04-20, awaiting `GATE-P32-CLOSURE: Approved`) |
.planning/constitution.md:127:**However**, the 14-Phase window **never carried an explicit Milestone 9 Lifted statement in this constitution**. That gap is what P32 W3 closes: not by retroactively re-consenting to work that already happened, but by正式 acknowledging that the freeze line was in fact crossed and the Resume Criterion path was met.
.planning/constitution.md:150:- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
.planning/constitution.md:151:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/constitution.md:189:- Workspace mount `.git/*.lock` residues are known blockers. v5.2 convention: scratch clone at `/sessions/<id>/p31-work/repo` + git bundle transfer when locks persist. Bundles live under `.planning/audit/bundles/` with adjacent README import instructions.
.planning/constitution.md:281:- section-only 引用（如 `constitution.md §v5.2 红线` / `PROJECT.md §Vision`）**不算 anchor**——必须落到行号或 `scope=<file>` 形式。
.planning/constitution.md:308:- section-only 引用（如 `constitution.md §v5.2`）作为唯一 anchor——参见上面通用约束
.planning/constitution.md:313:- 两条并列触发，不互相覆盖；同一条 copy 同时含数值与 surface 时，必须双轨都过。
.planning/constitution.md:330:- 详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md`
.planning/constitution.md:332:### Codex Persona Pipeline Tier-Trigger（governance bundle #2, 2026-04-25 起生效）
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:373:2. 开新 RETRO-V61-* 文件记录失败摊销，链接到 RETRO-V61-054
.planning/constitution.md:374:3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/constitution.md:376:详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
.planning/constitution.md:378:**详细文档：** `.planning/codex_personas/README.md` §Invocation 表，更新于本 bundle。RETRO-V61-054 §6 amortization 实证记录。
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:31:> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | **`PERSONA-ROTATION-STATE.md` 是唯一 source of truth。** 默认值 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同 |
.planning/codex_personas/README.md:54:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:73:# Tier-B（1 persona，跨-sub-phase 轮换 P1 → P2 → P3 → P4 → P5 → P1，起点 P1）：
.planning/codex_personas/README.md:74:# 启动新 epic 第一个 Tier-B sub-phase 跑 P1；后续按 PERSONA-ROTATION-STATE.md 末行下一个值轮换。
.planning/codex_personas/README.md:76:PERSONA=P3  # 由 .planning/phases/<epic>/PERSONA-ROTATION-STATE.md 决定，不得与上一行 Tier-B sub-phase 重复
.planning/codex_personas/README.md:80:# commit 后追加一行到 PERSONA-ROTATION-STATE.md：
.planning/codex_personas/README.md:81:# echo "<phase-id>: ${PERSONA} (<reason — content fit / round-robin>)" >> .planning/phases/<epic>/PERSONA-ROTATION-STATE.md
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:122:**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/codex_personas/README.md:126:**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

exec
/bin/zsh -lc "git grep -n \"default 5-persona\\|owner override\\|Owner 可按 sub-phase 内容覆盖\\|candidate .*governance bundle #2\\|待 E11-09 实证后立法\\|5-persona pipeline tier-trigger 候选规则\\|未在 §3.6 立法的原因\" 58426cf -- .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
58426cf:.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
58426cf:.planning/codex_personas/README.md:122:**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
58426cf:.planning/codex_personas/README.md:129:- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
58426cf:.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).
58426cf:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
58426cf:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
58426cf:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
58426cf:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:168:**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
58426cf:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:164:1. Roll back to default 5-persona for the next 3 sub-phases
58426cf:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
58426cf:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:180:- "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)

exec
/bin/zsh -lc "git grep -n \"Governance Mode Timeline entry \\\"governance bundle #2 persona tier-trigger\\\"|governance bundle #2 persona tier-trigger|Governance Mode Timeline\" -- .planning" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
codex
There’s a nontrivial edge now: the edited hotspots are cleaner, but the same E11 plan still contains shorter Tier-B summaries elsewhere. I’m checking whether those summaries are harmless shorthand or whether they preserve the old “pure round-robin” model and therefore break the “only state file SSOT” requirement.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '208,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '1,30p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# E11 — Workbench Engineer-First UX Overhaul (PLAN)
     2	
     3	> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
     4	> **Date:** 2026-04-25
     5	> **Governance:** v6.1 (DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT)
     6	> **Trigger:** Kogami 2026-04-25 verbatim — "你现在的项目工作台，如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难，没有清晰的指引，面板操作困难，设计不够简约……深度思考解决方案。"
     7	> **Truth-engine red lines:** unchanged — `controller.py` / 19-node / 4 logic gates / `adapters/` 全程不动。
     8	
     9	---
    10	
    11	## 0. Goal Statement
    12	
    13	把 `/workbench` 从 Epic-06..10 留下的"功能完整但无引导的脚手架"重做为**真飞机控制逻辑工程师在 30 分钟内能产出第一份有用工作的工具**，且整个改造**完全不触碰真值层**（所有红线维持）。
    14	
    15	成功标准（goal-backward verifier）：
    16	1. 一个第一次接触 Workbench 的飞机控制工程师，**不读代码、不看 HANDOVER**，凭页面 affordance 能在 30 分钟内独立完成：(a) 选一个 wow-scenario 跑通，(b) 在某个 logic gate 边上贴一条 domain-anchored annotation，(c) 把这条 annotation 转成 Claude Code prompt 输出给同事。
    17	2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
    18	3. main 三轨绿（default ≥ 863 / e2e 27 passed / adversarial 8/8）。
    19	4. truth-engine 红线 0 触碰。
    20	5. **(v2.3) 每个子 phase 的 user-facing copy 在 §Surface Inventory 全数登记**，锚点 line 真实存在；评审者抽查 1-3 行命中率 100%。
    21	
    22	---
    23	
    24	## 1. Current State — 反向 audit (probed 2026-04-25, main HEAD eea8065)
    25	
    26	| 维度 | 现状 | 工程师视角问题 |
    27	|---|---|---|
    28	| 页面入口 `/workbench` | 1078 行 HTML / 1717 行 CSS / 3754 行 JS / 22 个 data-attributed widgets | 信息密度过高，无层级 |
    29	| 页面身份 | 同一页 2 个 `<h1>`：上半 "Control Logic Workbench" (Epic-06 shell) + 下半 "Workbench Bundle 验收台" (旧 bundle 页) | 分裂的产品身份，工程师无法分辨"我在哪" |
    30	| 三列抽象 | "Scenario Control" / "Spec Review Surface" / "Logic Circuit Surface" | UI surface 命名，不是工程师任务命名 |

 succeeded in 0ms:
   208	**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。
   209	
   210	### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
   211	
   212	**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
   213	
   214	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
   215	
   216	### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"
   217	
   218	**反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。
   219	
   220	**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '300,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '252,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   252	1. **Persona 背景** — role / experience / mental model
   253	2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
   254	3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
   255	4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
   256	   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
   257	   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
   258	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
   259	
   260	每轮 review 跑完后（tier-aware）：

 succeeded in 0ms:
   300	| Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
   301	| E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
   302	| Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
   303	| Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
   304	| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
   305	| Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
   306	| EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |
   307	
   308	---
   309	
   310	## 9. CLOSURE 退出条件
   311	
   312	E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：
   313	
   314	1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
   315	2. ✅ §8 verification protocol 全部通过
   316	3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
   317	4. ✅ truth-engine 红线 0 触碰
   318	5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
   319	6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
   320	7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria

codex
I found two classes of leftovers in `E11-00-PLAN`: some are valid shorthand because they defer to `§3.6 + constitution`, others could still be read as the old “just rotate P1→P5” model. I’m checking the named section pointers now, because a clean rule rewrite still fails if the docs point at sections that don’t actually exist.
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '220,340p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   220	- 假装跑了测试（数字必须来自真实 stdout 粘贴）
   221	- 自创规则版本号（v6.1 之后下次叠加层应是 v6.2，不得跳号）
   222	
   223	### Codex 触发清单（继承 v6.0 + V61-001 新增 + v6.1 EMPIRICAL-CLAIM-PROBE）
   224	
   225	继承 v6.0 硬性触发：多文件前端、API 契约、e2e 期望变更、UI 交互模式、用户 UX 批评首次实现、OpenFOAM solver 报错、Phase E2E ≥3 case 连续失败、Docker+OpenFOAM 联合调试、`foam_agent_adapter.py` >5 LOC、`_generate_*.py` CFD 几何新增、GSD 产出物。
   226	
   227	继承 RETRO-V61-001 新增：安全敏感 operator endpoint、byte-reproducibility 敏感路径、跨 ≥3 文件 API schema rename。
   228	
   229	**v6.1 新增 EMPIRICAL-CLAIM-PROBE 规则（2026-04-25）：** PR prose（test docstring / 文件级 comment / demo doc / PR description）写下任何关于服务端 runtime 行为的具体数字（plant deploy %、sim time、tick count、logic-X activation timing 等）之前，Claude Code 必须 boot 相关代码路径在本地实测一次，或显式标 `TODO(probe-before-merge)`，或引用数字定义所在的 commit:line。仅基于 mental-model 算术得出的数字禁止落地到 regression-locked 测试或客户向 demo doc。来源：PR #5 round 1 Codex 命中 BEAT_EARLY ~6% deploy 实际 0% （详 `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`）。
   230	
   231	## v2.3 · UI-COPY-PROBE
   232	
   233	### 触发条件
   234	任何写入 repo 的 user-facing 自然语言文本，包括但不限于：
   235	- 入口页 / landing 页的 tile title / tile description / hero copy
   236	- button label / link text / empty state / tooltip / modal body
   237	- toast / banner / inline notice
   238	- onboarding 步骤说明 / 错误提示文案
   239	
   240	豁免：
   241	- 纯 a11y 标签（aria-label）若与可见 label 1:1 同步
   242	- 自动从 schema / enum / config 渲染的字符串（值由代码生成，文案即数据）
   243	
   244	### 强制 stage（写完之后、commit 之前必走）
   245	对本期新增/修改的每一条 user-facing copy，作者必须执行 **claim-to-source sweep**：
   246	
   247	1. **拆 claim**：把 copy 拆成可验证的具体声明单元（surface 名、行为、字段、角色、限制、数据来源、文件格式、SHA 类型……）。叙述性形容词（"流畅"、"清晰"）不计 claim。
   248	2. **grep 回 src/**：每一条 claim 必须在 src/ tests/ schemas/ config/ 至少一个文件中找到 line-number 锚点；锚点要支持该 claim 当前已 ship，不是计划态。
   249	3. **三选一处置**：
   250	   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
   251	   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
   252	   - **[DELETE]** 找不到锚点且无规划 → 删除该 claim。
   253	
   254	#### Anchor 格式细则
   255	
   256	每一条 anchor 必须是 **可执行的 ripgrep / sed 命令的目标**。按 claim 极性，正合法形式只有两种之一：
   257	
   258	##### 正面 claim 的 anchor（`<file>:<line>` 形式）
   259	
   260	适用于"X feature 已 ship" / "Y 字段是 N 个" / "Z 类型是 SHA256" 等可在源代码中**找到声明行**的断言。
   261	
   262	- 唯一合法形式：`<file>:<line>` 或 `<file>:<line-range>`
   263	- reviewer 复跑命令：`sed -n <line>p <file>`（应输出 claim 所声明的 token / label / value）
   264	
   265	##### 负面 claim 的 anchor（`scope=<file>[:line-range]` + 可选 `peer=<file>:<line-range>`）
   266	
   267	适用于"本期还没有 demo mode" / "JS 没有 approval handler" 等**通过 grep 验证缺位**的断言。
   268	
   269	- **scope= 字段**（必填，且**仅此一字段为必填**）：
   270	  - 形式 1：`scope=<file>` —— grep 跑全 file，命令 `grep <selector> <file>` 应返回 0 hits
   271	  - 形式 2：`scope=<file>:<line-range>` —— 缩小 grep 范围到该 line-range，命令 `sed -n <line-range>p <file> | grep <selector>` 应返回 0 hits
   272	  - 形式 1 是默认；只有当 claim 明确针对某一区域（"在 toolbar 区没有 X"）时才用形式 2
   273	- **peer= 字段**（可选，强烈推荐）：
   274	  - 形式：`peer=<file>:<line-range>` —— 指向**真实存在**的相似 feature，用作对照锚
   275	  - 不写 peer 不算违规；写了以后 reviewer 会 sed 复跑该 line-range 验证 peer 真实存在
   276	
   277	reviewer 复跑命令：(a) 对 scope= 部分跑 grep，hits 数必须与 anchor 描述一致；(b) 若有 peer=，对其跑 sed，行内容必须支持 anchor 描述。任一不一致 → MISMATCH，进入 v2.3 失效条件。
   278	
   279	##### 通用约束（所有 anchor）
   280	
   281	- section-only 引用（如 `constitution.md §v5.2 红线` / `PROJECT.md §Vision`）**不算 anchor**——必须落到行号或 `scope=<file>` 形式。
   282	- 多锚点用 ` + ` 拼接（参见正面 claim 多源支持的情形）。
   283	
   284	##### 写作模板
   285	
   286	正面 claim：
   287	
   288	```
   289	src/well_harness/static/workbench.js:140-164 (preset 数组定义 4 项 + 各自 archiveBundle 标记)
   290	```
   291	
   292	负面 claim（带 peer）：
   293	
   294	```
   295	scope=src/well_harness/static/workbench.html (grep "demo-mode\|demo-stage" 0 hits); peer=src/well_harness/static/workbench.html:283-299 (view-mode-toggle-bar 存在，仅 beginner / expert 两键)
   296	```
   297	
   298	负面 claim（仅 scope）：
   299	
   300	```
   301	scope=src/well_harness/static/workbench.js (grep "approval-action\|data-approval-action" 0 hits)
   302	```
   303	
   304	##### 禁止格式（v2.3 失效条件之一）
   305	
   306	- `(absence claim — verified by absence of <X> in <file>)` —— 自然语言而非可执行 grep 命令
   307	- `<file>:<line-range> (peer description)` 不带 `scope=` 前缀但描述 peer feature —— 容易被误读为"grep 范围"
   308	- section-only 引用（如 `constitution.md §v5.2`）作为唯一 anchor——参见上面通用约束
   309	
   310	### 与 v2.2 EMPIRICAL-CLAIM-PROBE 的关系
   311	- v2.2 治**数值/计算/百分比/SHA 等可量化断言**，对照源是计算复跑 / pytest / runs/。
   312	- v2.3 治**界面/行为/字段/角色等可定位断言**，对照源是 src/ ripgrep 锚点。
   313	- 两条并列触发，不互相覆盖；同一条 copy 同时含数值与 surface 时，必须双轨都过。
   314	
   315	### 审查侧的展开
   316	- 评审者（Codex / 第二视角）有权要求作者贴出 §Surface Inventory；缺失或残缺直接 CHANGES_REQUIRED，不进入逐字 ripgrep round-trip。
   317	- 评审者抽查 §Surface Inventory 中任意一行的锚点是否真实成立；命中 fabricated 锚点 → 视为伪造证据（同 v5.2 反假装条款）。
   318	
   319	### 失效条件
   320	- 作者声称已做 sweep 但 §Surface Inventory 缺失 / 行数与 copy 不对应 / 锚点 line 不存在 → 当轮 review 视为未做自审，要求重做（不是逐条修）。
   321	- 连续两期被外部 reviewer 抓出 ≥1 条 fabricated surface → 触发该 Phase Owner 的 self-pass-rate 校准复盘。
   322	
   323	### Trailer
   324	任何含 user-facing copy 改动的 commit，message 末尾追加：
   325	`UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`
   326	
   327	### 来源
   328	- E11-02 PR #10 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（fabricated knowledge field 名、虚构 archive 行为、虚构 role gate、SHA256 vs commit-SHA 混淆、不存在的 wow_a UI 走读 surface）
   329	- Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
   330	- 详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md`
   331	
   332	### Codex Persona Pipeline Tier-Trigger（governance bundle #2, 2026-04-25 起生效）
   333	
   334	**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
   335	
   336	**实证：** E11-09 dual-h1 fix PR #13 落地于 2026-04-25，Codex 2 轮 APPROVE（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。leading indicator fired。
   337	
   338	**新规则（替换"每个 user-facing UI 子 phase 默认跑全 5"）：**
   339	
   340	| 条件 | persona 数 | 选哪个 |

exec
/bin/zsh -lc 'rg -n "''^#+ .*v2'"\\.3|"'^#+ .*Codex Persona Pipeline Tier-Trigger|''^#+ .*Governance Mode Timeline|持久化条款|§v2'"\\.3\" .planning/constitution.md .planning/codex_personas/README.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/constitution.md:142:## Governance Mode Timeline
.planning/constitution.md:231:## v2.3 · UI-COPY-PROBE
.planning/constitution.md:304:##### 禁止格式（v2.3 失效条件之一）
.planning/constitution.md:332:### Codex Persona Pipeline Tier-Trigger（governance bundle #2, 2026-04-25 起生效）
.planning/codex_personas/README.md:31:> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:59:## 3. v2.3 立法输出（已 land 在 constitution.md）
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:61:完整规则正文移到 `.planning/constitution.md` §v2.3 · UI-COPY-PROBE。本 retro 只记三件事：
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:88:| `.planning/constitution.md` 加 §v2.3 UI-COPY-PROBE | ✅ 本 PR |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:97:## 5b. Meta-loop: v2.3 PR itself ran 5 Codex rounds (2026-04-25)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:151:- `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:202:- Constitution amendment: `.planning/constitution.md` §v2.3 (HEAD this PR)
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:44:## 1.5 Surface Inventory（v2.3 UI-COPY-PROBE 强制）

codex
I’ve confirmed the cross-links. Before issuing the verdict, I’m doing one last verification pass to make sure I don’t overstate resolution where the remaining text is only “close enough” but not actually identical.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/verification-before-completion/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
files = {
'README40': Path('.planning/codex_personas/README.md').read_text(),
'CONST343': Path('.planning/constitution.md').read_text(),
'RETRO148': Path('.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md').read_text(),
'E11_163': Path('.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md').read_text(),
}
for k,v in files.items():
    print('---',k,'---')
    for needle in ['唯一 source of truth','canonical source-of-truth','默认值 =','默认 =','Owner 可写入非默认值','Owner may write a non-default value','不得与上一行 Tier-B persona 相同','must not equal the immediately preceding Tier-B entry','PERSONA-ROTATION-STATE.md']:
        if needle in v:
            print(needle)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
--- README40 ---
唯一 source of truth
默认值 =
Owner 可写入非默认值
PERSONA-ROTATION-STATE.md
--- CONST343 ---
唯一 source of truth
默认 =
Owner 可写入非默认值
PERSONA-ROTATION-STATE.md
--- RETRO148 ---
canonical source-of-truth
Owner may write a non-default value
must not equal the immediately preceding Tier-B entry
PERSONA-ROTATION-STATE.md
--- E11_163 ---
PERSONA-ROTATION-STATE.md

codex
One more stale-text check turned up a likely blocker: `§3.6` itself is historicized, but I found another sentence later in the same plan that still talks as if the leading indicator is pending. I’m reading that paragraph in place before I lock the verdict.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '228,236p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   228	### Counterargument C-Opus: "我是否在 governance 投资曲线已经 over-process 的情况下还在加新规则？"
   229	
   230	**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
   231	
   232	**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
   233	
   234	---
   235	
   236	## 5. Risk register

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '320,324p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   320	7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria
   321	8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
   322	9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
   323	
   324	---

codex
The verdict is negative unless the remaining stale text is genuinely just shorthand. I’m pulling the exact memory lines I used so the final response can stay compliant without adding extra explanation.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '791,794p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '49,58p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   791	# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
   792	
   793	scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
   794	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.

 succeeded in 0ms:
    49	# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
    50	
    51	scope: Audit repo/GitHub/Notion drift, tighten source-of-truth framing, and hand off a governance-first Chinese execution package to Claude Code without silently turning analysis into code edits.
    52	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
    53	
    54	## Task 1: Audit repo, GitHub Actions, and Notion/control-plane drift before proposing project repositioning
    55	
    56	### rollout_summary_files
    57	
    58	- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)

codex
VERDICT: CHANGES_REQUIRED
R3-retry-F1 (Tier-B SSOT): drift — README/constitution/RETRO now align on state-file SSOT, but E11-00-PLAN:163 only says “Tier-B ... `PERSONA-ROTATION-STATE.md` 选 persona,” and README §命令模板:73-81 still scripts only the default round-robin path; the 4-doc pattern is not actually identical.
R3-retry-F2 (§3.6 historicized): drift — §3.6 + §3.6.1 themselves are historicized, but E11-00-PLAN:232 still says the current phase uses the leading indicator to decide whether to start governance bundle #2, so landed and pending framings still coexist in the same PLAN.
Cross-doc convergence (rule + template + closure + rollback + counting cmd): drift — constitution↔README↔RETRO↔E11 pointers resolve, and rollback/counting text is aligned, but E11-00-PLAN:17/214/316 still collapse Tier-B to bare “P1→P5 rotation,” so rule/template/closure wording has not fully converged.
NEW_R4_FINDINGS:
- IMPORTANT — E11-00-PLAN:17/214/316 still preserve a shorthand Tier-B operator model that omits `PERSONA-ROTATION-STATE.md` as the explicit SSOT plus the non-default/no-repeat constraints.


tokens used
56,416
VERDICT: CHANGES_REQUIRED
R3-retry-F1 (Tier-B SSOT): drift — README/constitution/RETRO now align on state-file SSOT, but E11-00-PLAN:163 only says “Tier-B ... `PERSONA-ROTATION-STATE.md` 选 persona,” and README §命令模板:73-81 still scripts only the default round-robin path; the 4-doc pattern is not actually identical.
R3-retry-F2 (§3.6 historicized): drift — §3.6 + §3.6.1 themselves are historicized, but E11-00-PLAN:232 still says the current phase uses the leading indicator to decide whether to start governance bundle #2, so landed and pending framings still coexist in the same PLAN.
Cross-doc convergence (rule + template + closure + rollback + counting cmd): drift — constitution↔README↔RETRO↔E11 pointers resolve, and rollback/counting text is aligned, but E11-00-PLAN:17/214/316 still collapse Tier-B to bare “P1→P5 rotation,” so rule/template/closure wording has not fully converged.
NEW_R4_FINDINGS:
- IMPORTANT — E11-00-PLAN:17/214/316 still preserve a shorthand Tier-B operator model that omits `PERSONA-ROTATION-STATE.md` as the explicit SSOT plus the non-default/no-repeat constraints.


