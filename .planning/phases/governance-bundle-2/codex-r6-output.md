2026-04-25T13:23:25.632281Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T13:23:25.632311Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc4cf-35c7-7e30-b009-f196a3390d59
--------
user
You are reviewing governance bundle #2 R6 (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit ee602b0 on top of d0a3c86).

History (6 rounds — recursive coherence drift):
- R1 → R5: each round closed structural findings but introduced new drift in references/paraphrases
- R5 verdict (commit d0a3c86): CHANGES_REQUIRED — 3 IMPORTANT all about "claimed convergence is itself drifted" (3 verbatim spots not identical / E11-00-PLAN pointers expand rule / bash override branch lacks literal assignment)
- R6 strategy switch (commit ee602b0): collapse to 1 canonical (constitution.md:343) + N pure pointers. Zero rule body anywhere except constitution. Recognized this is the same v2.3 PR meta-loop captured in RETRO-V61-054 §6.5.

R6 changes (3 files, 19+/41-):
1. README §Tier-trigger (lines 29-33): collapsed from 30+ lines (rule table + counting cmd + exception bullet + 判断时机) to 4-line pure-pointer paragraph. ZERO rule body remains.
2. RETRO §6.2 line 147: collapsed Tier-A + Tier-B bullets to 1 sentence: "rule itself is canonical at constitution.md §Codex Persona Pipeline Tier-Trigger; this bullet records decision, not rule body. Do not paraphrase here."
3. E11-00-PLAN lines 17, 163, 214, 316: each replaced with pure pointer "see constitution.md §Codex Persona Pipeline Tier-Trigger (canonical). 本 plan 不重述规则." ZERO rule restatement remains.
4. README §命令模板 bash Step 3a/3b: 5 explicit `# PERSONA=P{1,2,3,4,5}` lines as literal toggle (was: comment block referencing nonexistent code). User toggles 2 comment markers to switch path; both paths share hard-constraint sentinel.

Files reviewed (R6 commit ee602b0):
- .planning/codex_personas/README.md (especially lines 29-33, 46-82)
- .planning/constitution.md (UNCHANGED this round; only canonical rule body)
- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md (line 147)
- .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md (lines 17, 163, 214, 316)

Untouched-by-design (README operational sections, NOT rule restatement):
- README §Output convention (Tier-A aggregator vs Tier-B single verdict — README's owned procedural content, not in constitution)
- README §Anti-bias safeguard (per-tier anti-bias mechanism — README's owned content, not in constitution)
- README §Cost / latency baseline (cost record — README's owned content)

Your task: Issue formal R6 verdict. Verify:

1. Rule body (Tier-A trigger condition, Tier-B persona-selection SSOT, counting command, rollback condition) appears in EXACTLY ONE place — constitution.md §Codex Persona Pipeline Tier-Trigger. Anywhere else that has even a fragment of the rule = drift.
2. Every E11-00-PLAN reference to the rule is now a pure pointer with zero rule restatement (no "default round-robin", no "P1→P5", no "STATE.md SSOT" expansion in PLAN).
3. README §Tier-trigger header section lines 29-33 contains ZERO rule body (only pointer + history reference).
4. RETRO §6.2 line 147 contains ZERO rule body (only pointer + decision-arc reference).
5. README §命令模板 Step 3a/3b: BOTH paths are literally executable (Step 3a is active code; Step 3b has 5 commented `# PERSONA=Px` lines that user can uncomment); hard-constraint sentinel applies to both.
6. README §Output convention / §Anti-bias safeguard / §Cost ARE allowed to keep their current content because they describe README's owned operational mechanisms (aggregator vs single verdict / per-tier anti-bias / token cost record) — these are NOT rule body, they are procedural documentation. ONLY mark as drift if these sections have leaked rule body (e.g., a copy of the trigger condition or the SSOT statement).

Output format (verbatim):
```
VERDICT: APPROVE | CHANGES_REQUIRED
Rule body in 1 place only (constitution): [resolved | drift] — <≤2 lines>
E11-00-PLAN pure pointers (zero restatement): [resolved | drift] — <≤2 lines>
README §Tier-trigger pure pointer: [resolved | drift] — <≤2 lines>
RETRO §6.2 pure pointer: [resolved | drift] — <≤2 lines>
Bash template both paths literal: [resolved | drift] — <≤2 lines>
README owned operational sections free of rule body: [resolved | drift] — <≤2 lines>
NEW_R6_FINDINGS:
- <none | severity + ≤2 line summary>
```

Be ruthless. The PR has now run for 6 rounds. If you find ANY surviving rule restatement (even a fragment) outside constitution, mark drift. If a pointer says "see X" but isn't pure (it adds rule details after the see), mark drift. The R6 strategy is binary: rule body lives in constitution, references are pointers — ANY rule fragment outside constitution proves the strategy didn't take.

Reply only with structured output. No preamble.
codex
Reviewing PR #14 at `ee602b0` against the requested binary R6 criterion: I’m checking the touched planning docs for any surviving rule fragment outside `constitution.md`, then I’ll verify the bash template is literally runnable in both paths.
exec
/bin/zsh -lc "sed -n '1,260p' /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
sed: /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md: No such file or directory

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
/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|governance bundle|persona tier trigger|RETRO-V61-054|E11-00-PLAN|constitution.md" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc 'pwd && git rev-parse --is-inside-work-tree && git rev-parse HEAD && git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
true
ee602b0af47968d2237e3bd873523fe34b6e4a07
?? .planning/phases/governance-bundle-2/

codex
I’ve confirmed the workspace is at `ee602b0`. Next I’m reading the review workflow guidance, then I’ll run a narrow text audit over the four target files plus a repo-wide fragment search for any leaked tier-trigger rule outside `constitution.md`.
exec
/bin/zsh -lc "sed -n '1,260p' /Users/Zhuanz/.agents/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "nl -ba .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md | sed -n '130,165p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '1,140p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '1,360p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   130	
   131	### 6.1 Outcome — E11-09 PR #13
   132	
   133	**Total rounds: 2 (R1 BLOCKER → R2 APPROVE).**
   134	
   135	| Round | Verdict | Type of finding | Was it honesty-related? |
   136	|---|---|---|---|
   137	| R1 | BLOCKER | F1: real JS error — `workbench.js` shared between routes, unconditionally bound 14+ bundle-only DOM elements that don't exist on shell route. F2 IMPORTANT: test coverage didn't catch JS boot path. | **No.** F1 is a runtime bug (TypeError on null .addEventListener), found by Codex's empirical Node-level reasoning. Not a fabricated-surface-claim issue. F2 is missing-test-coverage of the bug. Both are *real engineering defects*, caught by reactive review working as intended. |
   138	| R2 | APPROVE | none | (CLEAN) |
   139	
   140	**Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
   141	
   142	### 6.2 governance bundle #2 — persona pipeline tier-trigger
   143	
   144	Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
   145	
   146	**5-persona pipeline → tier-trigger:** the rule itself is canonical at `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger. This bullet records the decision (governance bundle #2 landing on 2026-04-25 PR #14), not the rule body — read constitution for the actual Tier-A trigger condition, the Tier-B persona-selection SSOT, the counting command, the rollback semantics, and the verbatim text. Do not paraphrase here.
   147	
   148	Landed in:
   149	- `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)
   150	- `.planning/codex_personas/README.md` §Invocation table (this PR)
   151	- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
   152	
   153	**Things NOT changed:**
   154	- v2.2 EMPIRICAL-CLAIM-PROBE triggers
   155	- v2.3 §UI-COPY-PROBE triggers / §Surface Inventory mandate / §Anchor 格式细则
   156	- v6.1 Codex trigger list
   157	- RETRO numbering / Self-Pass-Rate strict / Hard Stop Points / Verbatim Exception 5 conditions
   158	
   159	### 6.3 Rollback condition (codified)
   160	
   161	If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
   162	1. Roll back to default 5-persona for the next 3 sub-phases
   163	2. Open a successor RETRO-V61-* documenting the failed amortization
   164	3. Re-engage Opus 4.7 strategic review
   165	

 succeeded in 0ms:
     1	# Codex Persona Review Pipeline
     2	
     3	> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
     4	> Date: 2026-04-25
     5	> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6
     6	
     7	## Purpose
     8	
     9	5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape.
    10	
    11	**Anti-bias model (governance bundle #2, 2026-04-25):**
    12	- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
    13	- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
    14	
    15	See §Tier-trigger below for which tier fires when.
    16	
    17	## Persona inventory
    18	
    19	| ID | Persona | File |
    20	|---|---|---|
    21	| P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
    22	| P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
    23	| P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
    24	| P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
    25	| P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |
    26	
    27	## Invocation
    28	
    29	### Tier-trigger
    30	
    31	> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
    32	>
    33	> History: governance bundle #2 (2026-04-25 PR #14) softened the prior 5-persona default. Decision arc: `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
    34	
    35	### 命令模板
    36	
    37	```bash
    38	# Tier-A（5 persona 并行，仅在条件满足时跑）：
    39	for p in P1 P2 P3 P4 P5; do
    40	  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    41	    "$(cat .planning/codex_personas/${p}-*.md)" \
    42	    > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
    43	done
    44	wait
    45	
    46	# Tier-B（1 persona）：PERSONA-ROTATION-STATE.md 是唯一 source of truth。
    47	#
    48	# Step 1 — Read state file last entry (or "" if file empty / new epic):
    49	STATE_FILE=.planning/phases/<epic>/PERSONA-ROTATION-STATE.md
    50	LAST=$(tail -1 "$STATE_FILE" 2>/dev/null | grep -oE 'P[1-5]' || echo "")
    51	#
    52	# Step 2 — Compute default = round-robin successor of last (P1 if empty):
    53	case "$LAST" in
    54	  P1) DEFAULT=P2 ;; P2) DEFAULT=P3 ;; P3) DEFAULT=P4 ;;
    55	  P4) DEFAULT=P5 ;; P5) DEFAULT=P1 ;; *)  DEFAULT=P1 ;;
    56	esac
    57	#
    58	# Step 3 — Choose path (uncomment exactly ONE of 3a or 3b):
    59	#
    60	# Step 3a (DEFAULT path): take the round-robin successor as-is.
    61	PERSONA=$DEFAULT
    62	#
    63	# Step 3b (OVERRIDE path): owner writes a non-default P-value motivated by
    64	# sub-phase content (e.g., demo-arc-heavy → P3; 适航 trace heavy → P4).
    65	# To use, comment out Step 3a above and uncomment exactly one literal line below:
    66	# PERSONA=P1   # demo-not-applicable
    67	# PERSONA=P2   # senior FCS deep code review
    68	# PERSONA=P3   # demo-arc-heavy sub-phase
    69	# PERSONA=P4   # 适航 trace / V&V heavy sub-phase
    70	# PERSONA=P5   # customer-facing / triage scenario
    71	#
    72	# Hard constraint enforced by rule layer (must hold for both paths):
    73	[ "$PERSONA" = "$LAST" ] && { echo "ERROR: PERSONA=$PERSONA equals LAST=$LAST — violates no-consecutive-repeat"; exit 1; }
    74	#
    75	# Step 4 — Run the chosen persona:
    76	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    77	  "$(cat .planning/codex_personas/${PERSONA}-*.md)" \
    78	  > .planning/phases/<phase-id>/persona-${PERSONA}-output.md 2>&1
    79	#
    80	# Step 5 — Append the new entry to the state file (canonical write):
    81	echo "<phase-id>: ${PERSONA} (<reason — round-robin | content-fit-override>)" >> "$STATE_FILE"
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
   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

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
    17	2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
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
    31	| Annotation 词汇 | "Point / Area / Link / Text Range" | 通用 UI primitive，无领域含义；工程师不会自然说"在 logic3 上 point" |
    32	| 入口 button 标签 | "Load Active Ticket" / "Snapshot Current State" / "通过并留档" / "阻塞演示" / "快速通过" / "留档复跑" | 动作明显但无 `WHEN` 提示，混杂中英 |
    33	| 角色提示 | `data-role="ENGINEER"` 在身份 chip 上 | 没有 affordance 反映 ENGINEER 实际能/不能做什么 |
    34	| Approval Center | "Kogami Proposal Triage" 三个 lane (Pending/Accept/Reject) | 非 Kogami 角色看到 disabled UI 无解释 |
    35	| 主流程进度 | `<aside id="annotation-inbox">` Review Queue 是个空 skeleton | 工程师不知道 annotation → proposal → ticket → PR 整条链路是怎么走的 |
    36	| 红线告知 | 无任何 UI surface 告诉工程师"controller.py / 19-node 是只读的，你只能 propose 不能 commit" | 工程师可能误以为 button click 会改 truth；没有契约可视化 |
    37	| Domain anchoring | wow_a/wow_b/wow_c 三个 demo scenarios 在 `docs/demo/` 但 UI 上没有"从已知场景开始"按钮 | 工程师必须自己造 lever 输入；高门槛 |
    38	| State-of-the-world | 没有顶部 status bar 显示当前真值引擎版本、最近一次 e2e 结果、known issues | 工程师必须读 HANDOVER 才能判断 baseline 健康度 |
    39	
    40	> **方法论备注**：以上数字均来自 `wc -l src/well_harness/static/workbench.html` 等真实 grep（满足 v6.1 EMPIRICAL-CLAIM-PROBE rule）；UI surface 的"22 widgets"来自 `grep -c "data-annotation-tool\|data-approval-action\|workbench-collab-"` 实测。
    41	
    42	---
    43	
    44	## 1.5 Surface Inventory（v2.3 UI-COPY-PROBE 强制）
    45	
    46	> 凡本期引入或修改 user-facing copy（tile / label / empty state / tooltip / modal / banner / onboarding），
    47	> 在此逐条登记，触发 v2.3 UI-COPY-PROBE。叙述形容词不登记，可定位声明必登记。
    48	>
    49	> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
    50	> E11-02 的 worked example 见 `E11-02-SURFACE-INVENTORY.md`。
    51	
    52	### Format（每行一个 claim）
    53	
    54	| # | Copy 出处 (file:line) | Claim 摘录 (≤40 字) | 类别 | Anchor / Plan-ID | 状态 |
    55	|---|---|---|---|---|---|
    56	| 1 | static/<file>:L<n> | "<claim>" | feature-name / field-name / behavior / role-gate / data-source / format-spec / limit / surface-location | src/<file>:L<n> 或 E11-XX | [ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE] |
    57	
    58	### 字段约束
    59	- **Copy 出处**：必填，file:line 必须落到本期 PR diff 内的具体行
    60	- **Claim 摘录**：必填，剥离修饰只留可验证骨架
    61	- **类别**（枚举）：feature-name / field-name / behavior / role-gate / data-source / format-spec / limit / surface-location
    62	- **Anchor / Plan-ID**：[ANCHORED] 必填 src 锚点 file:line；[REWRITE] 必填 Plan-ID（如 E11-04 / E12-01）；[DELETE] 留 "—"
    63	- **状态**（枚举）：[ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE]
    64	
    65	### 总计
    66	- ANCHORED: <N1>
    67	- REWRITE-as-planned: <N2>  ← 写入 commit trailer
    68	- DELETE: <N3>
    69	
    70	### 审查锚（给 Codex / 评审者）
    71	- 评审者从本表抽查任意 1-3 行的 src 锚点真实性
    72	- 表为空或与本期 copy diff 行数明显不匹配 → CHANGES_REQUIRED，不进入逐条 ripgrep
    73	
    74	---
    75	
    76	## 2. Personas（5 个，将作为 Codex review pipeline 输入）
    77	
    78	| ID | Persona | 背景 | 目标 | 上手 ≤ 30 分钟需要做到 |
    79	|---|---|---|---|---|
    80	| P1 | **Junior FCS Engineer (3-month hire)** | 航空控制专业本科 + 入职 3 月，会 Python，未读过本仓库代码 | 学习 reverser 控制链路，跑通一次 wow 场景 | 找到 Workbench 入口、选 wow_a、看到 logic1→4 因果链亮灯、贴一条 annotation |
    81	| P2 | **Senior FCS Engineer (10y reverser exp)** | 老航空控制工程师，带过 C919 反推方案，熟悉 R1-R5 invariants | 验证 logic3/4 阈值在边界 case 是否 spec-compliant | 改 lever 输入做 what-if、找到对应 invariant 的 spec 来源、贴 spec-cited annotation |
    82	| P3 | **Demo Presenter (立项汇报现场)** | 项目经理 + 销售工程师双角色，10 分钟讲完 3 wow 场景 | 现场零摩擦走完 wow_a → wow_b → wow_c | 一键启动 demo、清晰故事弧、AI 叙述 fallback 时也能讲 |
    83	| P4 | **QA / V&V Engineer** | 适航认证背景，关注 traceability + audit chain | 验证某条 logic3 行为对应的 requirement 文档 | 找到 requirement → controller 代码 → e2e 测试 的三段引用链 |
    84	| P5 | **Customer Apps Engineer** | 一线工程师与客户对接 | 接到客户报告"L4 在 X 条件下行为异常"，转成 issue | 把客户描述映射到 Workbench probe 操作、产出 ticket payload 给 dev team |
    85	
    86	每个 persona 在 §6 会有 distinct Codex prompt。
    87	
    88	---
    89	
    90	## 3. Sub-phase breakdown（按依赖顺序）
    91	
    92	| Sub-phase | 内容 | 依赖 | Truth-engine 触碰? |
    93	|---|---|---|---|
    94	| **E11-01** | Persona journey maps + gap audit per surface — 输出 `JOURNEYS.md` 把 5 personas × 当前 11 维度展开成 55 个 cell，标记每个 cell BLOCKED / FRICTION / OK | 无 | 不 |
    95	| **E11-02** | Onboarding 流：新增 `/workbench/start` 路由（或 modal）— 5 秒识别角色 → 推荐 3 个起手任务 → 一键进入对应工作流 | E11-01 | 不 |
    96	| **E11-03** | 三列重命名 + 重排 — "Scenario Control / Spec / Circuit" → 工程师任务命名（候选：「Probe & Trace」「Annotate & Propose」「Hand off & Track」），保留底层 ID 不变以免 e2e 测试失效 | E11-01 | 不 |
    97	| **E11-04** | Domain-anchored annotation 词汇升级 — UI 仍用 point/area/link/text-range 作为底层类型，但 button label + 工具说明转为「标记信号」「圈选 logic gate」「关联 spec」「引用 requirement 段」 | E11-03 | 不 |
    98	| **E11-05** | Canonical scenarios 起手卡 — wow_a/b/c 在顶部以 starter card 出现，一键 POST `/api/lever-snapshot` 预填 BEAT_DEEP_PAYLOAD 等 | E11-01 | 不 |
    99	| **E11-06** | State-of-the-world status bar — 顶部 1 行：truth-engine commit SHA · 最近 e2e 结果 · adversarial 8/8 状态 · open known-issues 数 | 无 | 不 |
   100	| **E11-07** | Authority contract banner — 在 controller / circuit 周围加一条 "🔒 Truth Engine — Read Only · Propose 不修改" 永久 banner，链接 v6.1 红线条款 | E11-03 | 不（仅 UI banner，不动 code） |
   101	| **E11-08** | 角色 affordance — 非 Kogami 角色看到 Approval Center 时显示 "Pending Kogami sign-off" 而不是 disabled UI | 无 | 不 |
   102	| **E11-09** | 双 h1 修复 — 把旧 "Workbench Bundle 验收台" 整页迁到 `/workbench/bundle` 子路径，主 `/workbench` 只保留 Epic-06..10 shell | 无 | 不（仅前端路由，不动 demo_server 真值出口） |
   103	| **E11-10** | Codex persona-review pipeline — 5 个 reusable prompts 落 `.planning/codex_personas/`，并跑首轮 review on E11-02..09 阶段产出 | E11-02..09 一一就绪后逐个跑 | 不 |
   104	| **E11-11** | E2E coverage — 增 `tests/e2e/test_e11_workbench_onboarding.py` 锁住 onboarding flow 的关键 selector 不被改坏 | E11-02 | 不 |
   105	| **E11-12** | CLOSURE — `E11-12-CLOSURE.md` + persona review summary + 三轨证据 + 自签 GATE-E11-CLOSURE: Approved (v6.1) | E11-01..19（除 E11-12 自身外的 18 项 closed） | 不 |
   106	| **E11-13** | manual_feedback_override **trust-affordance 修复（UI/可视化层）** — 加警示 banner + 模式标识 chip + 失谐告警，让用户*看起来不再越权*。**不是** authority-chain breach 修复（873 + adversarial 8/8 已证 truth-engine 实际未被越权），而是 UI affordance 让用户对真值失去信任的"可视污染"修复。Opus 4.7 (2026-04-25) reframe；详见 §3.5。 | E11-01（P2-1 Reading B locked） | 不 |
   107	| **E11-14** | manual_feedback_override **服务端 role guard** — `/api/lever-snapshot` 对 manual_feedback_override 增 actor + ticket-binding 检查，未签 sign-off 时端点返回 409 而不是 200（仍不动 controller）。配合 E11-13 形成"UI 看不到 + 服务端拒绝"两道防线。 | E11-13 | 不（adapter boundary 内的 endpoint 守护，不进 controller / models / adapters/*.py 真值出口） |
   108	| **E11-15** | UI 字符串中文优先化 sweep — 全部 user-facing label / button 默认中文，英文降为 muted sublabel；保持底层 selector ID 不变 | E11-03 | 不 |
   109	| **E11-16** | 服务端 approval endpoint 加固 — `/api/workbench/*` approval 类 endpoint 增 actor + ticket + artifact-hash 三元绑定，与 audit chain hash 链接（不动 controller） | E11-08 | 不 |
   110	| **E11-17** | Presenter mode toggle — 一键隐藏 annotation / approval / dev chrome；narration fallback ribbon 在 AI 服务慢/down 时显示静态文案 | E11-02 | 不 |
   111	| **E11-18** | 逐 logic-gate trace tuple 显示 — Logic Circuit Surface 上 L1–L4 各自挂 (requirement_id, test_id, artifact_hash) 三元；annotation schema 升级要求三元 | E11-04 | 不 |
   112	| **E11-19** | Apps-engineer 客户视图 — customer 复现面板 + repro recipe 字段 + ticket schema enrichment + 重复 case 模糊搜索 | E11-04 | 不 |
   113	
   114	> 红线维持: E11-01..19 全部仅触碰 `src/well_harness/static/workbench.{html,css,js}`、`src/well_harness/static/annotation_overlay.js`、`src/well_harness/demo_server.py`（仅 endpoint guard，不动 controller dispatch）、新增的 e2e 测试、新增的 `.planning/` 文档。**不进入** `controller.py` / `runner.py` / `models.py` (truth-bearing) / `adapters/` / wow_a fixture。
   115	
   116	> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
   117	
   118	---
   119	
   120	## 3.5 执行排序（Opus 4.7 strategic input · 2026-04-25）
   121	
   122	> 数据源：Notion @Opus 4.7 异步会话，2026-04-25。审查范围 = E11-02 + v2.3 governance bundle 落地后的 strategic review。
   123	> 完整 Opus 输出存档在 PR #11 description / Notion 04 决策日志 DB。
   124	
   125	### 排序（next 6 sub-phases）
   126	
   127	```
   128	E11-09 → E11-13/14 → E11-05 → E11-03 → E11-04 → E11-06
   129	```
   130	
   131	**逐项理由**（Opus 4.7 verbatim）：
   132	
   133	1. **E11-09 dual-h1 修复** — 30 秒 quick win，先清债（双 h1 是身份分裂遗债），同时作为 §3.6 leading indicator 量度 governance 摊销。
   134	2. **E11-13 + E11-14 manual_feedback_override 修复** — 提前到第 2 而非第 3。**关键 reframe**: 不是 authority-chain breach（873 + adversarial 8/8 已证 truth-engine 没被越权），是 **UI affordance 让用户*看起来*越权**——比 demo BLOCKER 更污染信任。修复在 UI / 服务端 endpoint guard 两层，不进 controller。
   135	3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
   136	4. **E11-03 三列重命名** — P1 / P2 工程师任务命名升级。
   137	5. **E11-04 annotation 词汇升级** — P1 / P2 / P5 domain anchoring。
   138	6. **E11-06 status bar** — 基础设施收尾。
   139	
   140	### Opus 4.7 拒绝的备选
   141	
   142	- **B（直接全做 P2-1 truth-boundary fix 链 + 其他都推后）**：拒绝。错在把"看起来越权"上升为 R1-R5 红线 fix——是过度反应。
   143	- **C（先做 E11-12 closure 收 phase 再换新 phase）**：拒绝。18 子 phase 没做先 closure 是伪闭环。
   144	
   145	### E11-15..19 的位置
   146	
   147	不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
   148	
   149	---
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
   163	**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
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
   179	**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
   180	
   181	**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
   182	
   183	**详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
   184	
   185	---
   186	
   187	## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
   188	
   189	**目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。
   190	
   191	**条件解锁**：满足全部 3 条后可并发启动一个**不动 src/** 的 E12 spec phase（如 fault diagnosis 的 PRD + intake packet schema）：
   192	1. E11-09 ≤ 2 轮 Codex APPROVE（证 v2.3 摊销）
   193	2. E11-06 完成（E11-15..19 进入纯前端期）
   194	3. 该 E12 候选明确不动 `src/well_harness/{controller,runner,models,plant}.py` / `adapters/` / `tests/e2e/test_wow_a*`
   195	
   196	**理由**：并发 src/ phase 会拉高 truth-engine 触碰风险且让"v2.3 摊销 vs bloat"归因失败（两个 phase 同时跑 Codex 会污染 leading indicator 数据）。
   197	
   198	---
   199	
   200	## 4. Tier-1 Adversarial Self-Review（v5.2 红线 #3 强制）
   201	
   202	> 三个最强自我反对意见 + 显式 rebuttal。
   203	
   204	### Counterargument #1: "为什么不让真工程师上手反馈再改？"
   205	
   206	**反对论点**: pre-emptive UX 工作可能优化错的方向。等到第一个 customer-facing 工程师 onboard 时再迭代，更省成本，避免 design-by-imagination。
   207	
   208	**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。
   209	
   210	### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
   211	
   212	**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
   213	
   214	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware；canonical 定义见 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger 和 `.planning/codex_personas/README.md` §Anti-bias safeguard。本 PLAN 不重述。结论：bias 风险存在但已通过 distinct context + canonical tier-aware anti-bias 机制 mitigated。
   215	
   216	### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"
   217	
   218	**反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。
   219	
   220	**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
   221	
   222	### Counterargument C-UI: "本期 copy 里我是否写了一个 src/ 还没 ship 的 surface？"
   223	
   224	**反对论点**（v2.3 立法后强制必答）: landing / tile / banner / tooltip 的 copy 是否描述了某个 feature / field / role-gate / behavior，而该 surface 在当前 commit 的 src/ 里其实不存在或只存在于计划态？
   225	
   226	**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
   227	
   228	### Counterargument C-Opus: "我是否在 governance 投资曲线已经 over-process 的情况下还在加新规则？"
   229	
   230	**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
   231	
   232	**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**当时未立即立法 tier-trigger 的原因**：Opus 警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。§3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 已 fired (2026-04-25)，governance bundle #2 已通过 PR #14 落 constitution（详 §3.6.1）。Phase Owner 在每个新子 phase 启动前仍必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
   233	
   234	---
   235	
   236	## 5. Risk register
   237	
   238	| Risk | Severity | Mitigation |
   239	|---|---|---|
   240	| 改 workbench.html 大量 selector 导致 e2e + adversarial 测试失败 | High | 每 sub-phase 末跑三轨；保留底层 `id` 和 `data-*` selector 不动，只改 visible label / class / 排版 |
   241	| 新 onboarding flow 与已有 ticket 流程冲突 | Med | E11-02 的 `/workbench/start` 单纯是入口，导向已有按钮；不替换底层 prompt/ticket 逻辑 |
   242	| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
   243	| 工程师在 Authority Contract banner 之外仍误以为可改 truth | Med | E11-07 banner + E11-04 annotation 词汇双重锁；同时不提供任何会让工程师以为"在 UI 改 truth-engine"的 affordance |
   244	| 角色 affordance E11-08 暴露 Kogami-only 操作的 implementation detail | Low | 仅展示 "Awaiting Kogami sign-off" 文案，不暴露内部 actor 列表 |
   245	
   246	---
   247	
   248	## 6. Codex Persona Review Pipeline
   249	
   250	详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
   251	
   252	1. **Persona 背景** — role / experience / mental model
   253	2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
   254	3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
   255	4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
   256	   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
   257	   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
   258	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
   259	
   260	每轮 review 跑完后（tier-aware）：
   261	- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
   262	- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
   263	- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
   264	- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
   265	
   266	---
   267	
   268	## 7. Sequencing & estimated effort
   269	
   270	| Sub-phase | Type | LOC est | Time est | Codex required? |
   271	|---|---|---|---|---|
   272	| E11-01 | doc | ~300 | 30min | NO |
   273	| E11-02 | code (HTML/JS) | ~200 | 1h | YES (UI 交互模式变更) |
   274	| E11-03 | refactor (HTML/CSS) | ~150 | 45min | YES (UI 交互模式变更) |
   275	| E11-04 | doc + code | ~100 | 30min | NO (mechanical relabel) |
   276	| E11-05 | code (JS) | ~150 | 1h | YES (UI 交互模式变更) |
   277	| E11-06 | code (HTML/JS) | ~120 | 45min | YES (新 API 调用 / 状态聚合) |
   278	| E11-07 | code (HTML/CSS) | ~80 | 30min | NO (添加 banner，无逻辑) |
   279	| E11-08 | code (JS) | ~60 | 30min | NO (单 conditional 文案) |
   280	| E11-09 | refactor (routing) | ~200 | 1h | YES (路由变更 → 用户导航 mode) |
   281	| E11-10 | doc | ~600 (5 prompts) | 1.5h | self-review only |
   282	| E11-11 | test | ~150 | 1h | YES (新 e2e 期望) |
   283	| E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
   284	| E11-13 | code (HTML/CSS) | ~100 | 45min | YES (UI 交互模式变更 + manual mode trust 可视化) |
   285	| E11-14 | code (Python endpoint guard) | ~80 | 1h | YES (server-side guard, adapter boundary 内) |
   286	| E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
   287	| E11-16 | code (Python) | ~120 | 1h | YES (approval endpoint 三元绑定) |
   288	| E11-17 | code (HTML/CSS/JS) | ~180 | 1h | YES (presenter mode toggle = UI 交互模式变更) |
   289	| E11-18 | code (HTML/JS) | ~150 | 1h | YES (logic-gate trace tuple + schema 升级) |
   290	| E11-19 | code (HTML/JS + schema) | ~250 | 1.5h | YES (UI 交互模式变更 + ticket schema enrichment) |
   291	
   292	**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
   293	
   294	---
   295	
   296	## 8. Verification protocol (E11 closure 前必跑)
   297	
   298	| 维度 | 标准 | 锚点 |
   299	|---|---|---|
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
   316	3. ✅ Codex persona review 给出 0 BLOCKER（tier 决定 + persona 选取规则 canonical = `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger）
   317	4. ✅ truth-engine 红线 0 触碰
   318	5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
   319	6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
   320	7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria
   321	8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
   322	9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
   323	
   324	---
   325	
   326	## 10. Open Questions（pending Kogami input · 不阻塞启动）
   327	
   328	1. 5 personas 的 specific company / 项目 context 要不要 fictionalize？（默认: 是，避免暗示真实客户）
   329	2. Onboarding flow 是 modal 还是单独路由？（默认: 单独路由 `/workbench/start`，可深链可分享）
   330	3. 三列 verb 命名候选 "Probe & Trace / Annotate & Propose / Hand off & Track" 还是更激进的 "What-If / Mark / Hand off"？（默认: 前者，与现有 button 文案对齐）
   331	4. 双 h1 修复时把旧 bundle 验收台搬到 `/workbench/bundle` 还是直接 deprecate？（默认: 搬到子路径，保留访问路径以免破坏旧 demo 习惯）
   332	5. Authority Contract banner 是 sticky 还是 dismissable？（默认: sticky 在 truth-engine surfaces 周围，dismissable 在其他位置以免审美干扰）
   333	
   334	> 本 phase 启动不依赖以上 Q 解决；Q 在 E11-01 journey map 阶段会迭代回到 plan 里 confirm。
   335	
   336	---
   337	
   338	## 11. Trailer
   339	
   340	```
   341	Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
   342	```
   343	
   344	> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '330,360p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

codex
The narrow reads are enough to show one problem already: the R6 collapse happened in the target header/pointer spots, but the README and PLAN still appear to carry tier-trigger fragments elsewhere. I’m doing one repo-wide grep pass now to separate actual rule-body leakage from allowed operational prose.
exec
/bin/zsh -lc 'rg -n "copy diff|REWRITE/DELETE|PERSONA-ROTATION-STATE|round-robin|P1→P2→P3→P4→P5→P1|Tier-Trigger|Tier-trigger|Tier-B|Tier-A|source of truth|唯一 source of truth|rollback" .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'rg -n "copy diff|REWRITE/DELETE|PERSONA-ROTATION-STATE|round-robin|P1→P2→P3→P4→P5→P1|Tier-Trigger|Tier-trigger|Tier-B|Tier-A|source of truth|唯一 source of truth|rollback" .planning/codex_personas/README.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
12:- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
15:See §Tier-trigger below for which tier fires when.
29:### Tier-trigger
31:> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
38:# Tier-A（5 persona 并行，仅在条件满足时跑）：
46:# Tier-B（1 persona）：PERSONA-ROTATION-STATE.md 是唯一 source of truth。
49:STATE_FILE=.planning/phases/<epic>/PERSONA-ROTATION-STATE.md
52:# Step 2 — Compute default = round-robin successor of last (P1 if empty):
60:# Step 3a (DEFAULT path): take the round-robin successor as-is.
81:echo "<phase-id>: ${PERSONA} (<reason — round-robin | content-fit-override>)" >> "$STATE_FILE"
88:### Tier-A（5-persona 并行）
97:### Tier-B（1-persona 默认）
104:- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

 succeeded in 0ms:
17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
72:- 表为空或与本期 copy diff 行数明显不匹配 → CHANGES_REQUIRED，不进入逐条 ripgrep
116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
163:**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
175:- `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
179:**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
181:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
214:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware；canonical 定义见 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger 和 `.planning/codex_personas/README.md` §Anti-bias safeguard。本 PLAN 不重述。结论：bias 风险存在但已通过 distinct context + canonical tier-aware anti-bias 机制 mitigated。
242:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
256:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
257:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
261:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
262:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
264:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
304:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
316:3. ✅ Codex persona review 给出 0 BLOCKER（tier 决定 + persona 选取规则 canonical = `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger）
344:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc 'rg -n "copy diff|REWRITE/DELETE|PERSONA-ROTATION-STATE|round-robin|P1→P2→P3→P4→P5→P1|next-persona|Tier-B persona|rollback|default 5-persona|Tier-A|Tier-B|source of truth|唯一 source of truth|5-persona|全 P1|全跑|新 epic 第一行|不得与上一行" .planning/codex_personas/README.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/constitution.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:** the rule itself is canonical at `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger. This bullet records the decision (governance bundle #2 landing on 2026-04-25 PR #14), not the rule body — read constitution for the actual Tier-A trigger condition, the Tier-B persona-selection SSOT, the counting command, the rollback semantics, and the verbatim text. Do not paraphrase here.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:161:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:162:1. Roll back to default 5-persona for the next 3 sub-phases
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:168:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:169:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:178:- "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:151:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/constitution.md:334:**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/constitution.md:342:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
.planning/constitution.md:345:**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
.planning/constitution.md:354:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/codex_personas/README.md:12:- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:31:> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
.planning/codex_personas/README.md:33:> History: governance bundle #2 (2026-04-25 PR #14) softened the prior 5-persona default. Decision arc: `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
.planning/codex_personas/README.md:38:# Tier-A（5 persona 并行，仅在条件满足时跑）：
.planning/codex_personas/README.md:46:# Tier-B（1 persona）：PERSONA-ROTATION-STATE.md 是唯一 source of truth。
.planning/codex_personas/README.md:49:STATE_FILE=.planning/phases/<epic>/PERSONA-ROTATION-STATE.md
.planning/codex_personas/README.md:52:# Step 2 — Compute default = round-robin successor of last (P1 if empty):
.planning/codex_personas/README.md:60:# Step 3a (DEFAULT path): take the round-robin successor as-is.
.planning/codex_personas/README.md:81:echo "<phase-id>: ${PERSONA} (<reason — round-robin | content-fit-override>)" >> "$STATE_FILE"
.planning/codex_personas/README.md:88:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:97:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:122:**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/codex_personas/README.md:124:- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
.planning/codex_personas/README.md:127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/codex_personas/README.md:128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:129:- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:72:- 表为空或与本期 copy diff 行数明显不匹配 → CHANGES_REQUIRED，不进入逐条 ripgrep
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（landed as `governance bundle #2`, PR #14, 2026-04-25） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:160:| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（hypothetical：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:176:- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:179:**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:181:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:230:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:232:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**当时未立即立法 tier-trigger 的原因**：Opus 警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。§3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 已 fired (2026-04-25)，governance bundle #2 已通过 PR #14 落 constitution（详 §3.6.1）。Phase Owner 在每个新子 phase 启动前仍必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:242:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:256:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:261:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:262:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:264:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:304:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:322:9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:344:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc 'git diff --stat d0a3c86..ee602b0 -- .planning/codex_personas/README.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md && git diff --unified=3 d0a3c86..ee602b0 -- .planning/codex_personas/README.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .planning/codex_personas/README.md                 | 48 +++++++---------------
 .../E11-workbench-engineer-first-ux/E11-00-PLAN.md |  8 ++--
 .../RETRO-V61-054-ui-copy-probe-birth.md           |  4 +-
 3 files changed, 19 insertions(+), 41 deletions(-)
diff --git a/.planning/codex_personas/README.md b/.planning/codex_personas/README.md
index b90cd8a..948258c 100644
--- a/.planning/codex_personas/README.md
+++ b/.planning/codex_personas/README.md
@@ -26,38 +26,11 @@ See §Tier-trigger below for which tier fires when.
 
 ## Invocation
 
-### Tier-trigger（governance bundle #2 落地，2026-04-25 起生效）
+### Tier-trigger
 
-> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
+> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
 >
-> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
-
-按下表决定调多少 persona：
-
-| 子 phase 特征 | persona 数 | 选哪个 |
-|---|---|---|
-| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | **`PERSONA-ROTATION-STATE.md` 是唯一 source of truth。** 默认值 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同 |
-
-**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
-
-```bash
-# 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
-git diff --stat $(git merge-base HEAD main)..HEAD -- \
-  'src/well_harness/static/*.html' \
-  'src/well_harness/static/*.js' \
-  'src/well_harness/static/*.css'
-```
-
-读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
-
-**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
-
-**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
-
-**例外（仍跑全 5）：**
-- 该子 phase 触发了 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
-- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
+> History: governance bundle #2 (2026-04-25 PR #14) softened the prior 5-persona default. Decision arc: `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
 
 ### 命令模板
 
@@ -82,14 +55,21 @@ case "$LAST" in
   P4) DEFAULT=P5 ;; P5) DEFAULT=P1 ;; *)  DEFAULT=P1 ;;
 esac
 #
-# Step 3a — Default path: take the round-robin successor as-is.
+# Step 3 — Choose path (uncomment exactly ONE of 3a or 3b):
+#
+# Step 3a (DEFAULT path): take the round-robin successor as-is.
 PERSONA=$DEFAULT
 #
-# Step 3b — Override path: owner writes a non-default P-value motivated by
+# Step 3b (OVERRIDE path): owner writes a non-default P-value motivated by
 # sub-phase content (e.g., demo-arc-heavy → P3; 适航 trace heavy → P4).
-# Hard constraint enforced by rule layer: PERSONA must NOT equal $LAST.
-# (Uncomment + edit ONE of the two lines above to choose a path.)
+# To use, comment out Step 3a above and uncomment exactly one literal line below:
+# PERSONA=P1   # demo-not-applicable
+# PERSONA=P2   # senior FCS deep code review
+# PERSONA=P3   # demo-arc-heavy sub-phase
+# PERSONA=P4   # 适航 trace / V&V heavy sub-phase
+# PERSONA=P5   # customer-facing / triage scenario
 #
+# Hard constraint enforced by rule layer (must hold for both paths):
 [ "$PERSONA" = "$LAST" ] && { echo "ERROR: PERSONA=$PERSONA equals LAST=$LAST — violates no-consecutive-repeat"; exit 1; }
 #
 # Step 4 — Run the chosen persona:
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
index 9441f3d..21a15ae 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
@@ -14,7 +14,7 @@
 
 成功标准（goal-backward verifier）：
 1. 一个第一次接触 Workbench 的飞机控制工程师，**不读代码、不看 HANDOVER**，凭页面 affordance 能在 30 分钟内独立完成：(a) 选一个 wow-scenario 跑通，(b) 在某个 logic gate 边上贴一条 domain-anchored annotation，(c) 把这条 annotation 转成 Claude Code prompt 输出给同事。
-2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量与选取规则按 `constitution.md` §Codex Persona Pipeline Tier-Trigger（governance bundle #2，2026-04-25 PR #14 落地版本）跑：Tier-A = 5/5 全 persona 并行；Tier-B = 1/1，按 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` SSOT 选取（默认值 = 末行 round-robin 后继；owner 可写非默认；不得与上一行 Tier-B 同 persona）。E11-13..19 默认按 tier-trigger。
+2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
 3. main 三轨绿（default ≥ 863 / e2e 27 passed / adversarial 8/8）。
 4. truth-engine 红线 0 触碰。
 5. **(v2.3) 每个子 phase 的 user-facing copy 在 §Surface Inventory 全数登记**，锚点 line 真实存在；评审者抽查 1-3 行命中率 100%。
@@ -160,7 +160,7 @@ E11-09 → E11-13/14 → E11-05 → E11-03 → E11-04 → E11-06
 | 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（hypothetical：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
 | ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
 
-**触发条件（landed, 完整规则在 `constitution.md` §Codex Persona Pipeline Tier-Trigger — governance bundle #2 落地版本）**：(a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] → Tier-A (5 personas 并行)。否则 → Tier-B (1 persona，按 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` SSOT 选取：默认 = 末行 round-robin 后继；owner 可写非默认；不得与上一行 Tier-B 重复)。本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；任何 shorthand 引用此规则的他处必指向 constitution canonical 节。
+**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
 
 **保留不变**：v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**。
 
@@ -211,7 +211,7 @@ E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓
 
 **反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
 
-**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（完整规则见 `constitution.md` §Codex Persona Pipeline Tier-Trigger / `codex_personas/README.md` §Anti-bias safeguard）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由 (i) `PERSONA-ROTATION-STATE.md` SSOT 强制跨-sub-phase 不同 persona + (ii) §Surface Inventory grep 锚点 + (iii) RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
+**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware；canonical 定义见 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger 和 `.planning/codex_personas/README.md` §Anti-bias safeguard。本 PLAN 不重述。结论：bias 风险存在但已通过 distinct context + canonical tier-aware anti-bias 机制 mitigated。
 
 ### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"
 
@@ -313,7 +313,7 @@ E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.
 
 1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
 2. ✅ §8 verification protocol 全部通过
-3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 `constitution.md` §Codex Persona Pipeline Tier-Trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；Tier-B persona 由 `PERSONA-ROTATION-STATE.md` SSOT 选取）
+3. ✅ Codex persona review 给出 0 BLOCKER（tier 决定 + persona 选取规则 canonical = `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger）
 4. ✅ truth-engine 红线 0 触碰
 5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
 6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
diff --git a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
index 97aef9f..cad5893 100644
--- a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
+++ b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
@@ -143,9 +143,7 @@ Opus 4.7 §1 strategic review (2026-04-25) set E11-09 dual-h1 fix as the **leadi
 
 Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
 
-**5-persona pipeline → tier-trigger:**
-- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
-- Tier-B (1 persona): all other cases. `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source-of-truth for persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of last entry; new epic = P1. Owner may write a non-default value (content fit, e.g., demo-arc → P3); hard constraint: written value must not equal the immediately preceding Tier-B entry. Sequence resets per epic.
+**5-persona pipeline → tier-trigger:** the rule itself is canonical at `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger. This bullet records the decision (governance bundle #2 landing on 2026-04-25 PR #14), not the rule body — read constitution for the actual Tier-A trigger condition, the Tier-B persona-selection SSOT, the counting command, the rollback semantics, and the verbatim text. Do not paraphrase here.
 
 Landed in:
 - `.planning/constitution.md` §v2.3 § Codex Persona Pipeline Tier-Trigger (this PR)

codex
One more check: the repo-wide grep surfaced likely leakage inside `constitution.md` itself at non-canonical lines, not just in README/PLAN. I’m opening those spots before I issue the verdict, because your criterion is “exactly one place” and that includes summaries inside the same file.
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '1,25p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# AI FANTUI LogicMVP Constitution
     2	
     3	> **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append + governance bundle #2 persona tier-trigger amortization)
     4	>
     5	> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
     6	>
     7	> **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
     8	>
     9	> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
    10	>
    11	> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
    12	
    13	## Milestone Hold (historical, 2026-04-13)
    14	
    15	**Declared:** 2026-04-13
    16	**Scope:** Milestone 4 (Phases P4–P11)
    17	**Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**
    18	
    19	All P0 through P11 phases are complete. The project is at a natural pause point.
    20	
    21	### What This Hold Means
    22	
    23	- No active development phases.
    24	- Base code frozen; only regression fixes and documentation corrections permitted.
    25	- Notion control tower and GitHub repo remain accessible as read-only reference.

exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '145,155p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '150,185p;250,266p;296,318p;340,344p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '84,132p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   145	- **v4.0 Extended Autonomy (2026-04-17 → 2026-04-19):** Executor allowed to self-sign Gate within a ≥3-Phase深度验收 window when Kogami 显式 renewed the mandate. Used for P17 → P30 close-out.
   146	- **v5.1 Pair Mode (2026-04-19 → 2026-04-20):** Short-lived dual-Executor pair (Claude App + Codex). Abandoned after orphan commit `4474505` (Codex, unsigned) triggered the P31 orphan-triage response.
   147	- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
   148	- **v6.0 Multi-Agent × Codex Joint Dev (2026-04-22 → 2026-04-25):** Claude Code 主执行 + Codex 强制盲点审查回到清单（多文件前端 / API 契约变更 / e2e 期望变更 / UI 变更 / 用户 UX 批评后首次实现 / OpenFOAM 误差等触发硬性调用）。Verbatim exception 5 条件允许跳过 round-2。详见 Notion Page 11 v6.0 节。
   149	- **v6.1 Solo Autonomy Delegation (2026-04-25, active):** Kogami 在 PR #5 Gate 后口头授权 Claude Code 全权（Notion + PR merge + Codex 自决 + 新 phase 启停），仅 truth-engine 红线维持。详见 v6.1 Solo Autonomy 节、DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT、Notion Page 11 §v6.1。
   150	- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
   151	- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
   152	
   153	## v5.2 Claude App Solo Mode (active)
   154	
   155	### Red Lines (five absolutes)

 succeeded in 0ms:
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
   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

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
   163	**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
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
   179	**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
   180	
   181	**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
   182	
   183	**详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
   184	
   185	---
   250	详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
   251	
   252	1. **Persona 背景** — role / experience / mental model
   253	2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
   254	3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
   255	4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
   256	   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
   257	   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
   258	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
   259	
   260	每轮 review 跑完后（tier-aware）：
   261	- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
   262	- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
   263	- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
   264	- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
   265	
   266	---
   296	## 8. Verification protocol (E11 closure 前必跑)
   297	
   298	| 维度 | 标准 | 锚点 |
   299	|---|---|---|
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
   316	3. ✅ Codex persona review 给出 0 BLOCKER（tier 决定 + persona 选取规则 canonical = `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger）
   317	4. ✅ truth-engine 红线 0 触碰
   318	5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
   340	```
   341	Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
   342	```
   343	
   344	> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

codex
I have enough to fail the bundle already, but I’m doing one last repo-wide grep to make sure I’m not missing any extra leak outside the four review files. That lets me distinguish “targeted spots fixed” from “strategy actually achieved.”
exec
/bin/zsh -lc 'git ls-files .planning | rg "constitution|README|RETRO-V61-054|E11-00-PLAN|PERSONA-ROTATION-STATE|governance-bundle-2"' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/audit/bundles/README.md
.planning/audit/bundles/p32-provenance-backfill-README.md
.planning/codex_personas/README.md
.planning/constitution.md
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md

exec
/bin/zsh -lc 'rg -n "copy diff ≥ ?10|copy diff >= ?10|REWRITE/DELETE|PERSONA-ROTATION-STATE|round-robin|P1→P2→P3→P4→P5→P1|Tier-B persona|Tier-Trigger|Tier-trigger|rollback to default 5-persona|force default 5-persona|next 3 sub-phases|唯一 source of truth|source of truth for next-persona|no-consecutive-repeat" .' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
codex
The repo-wide broad regex was too brittle, so I’m doing one simpler pass on the concrete trigger tokens. After that I’ll close with the formal verdict only.
exec
/bin/zsh -lc 'rg -n "Tier-B|Tier-A|rollback" .planning/codex_personas/README.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/constitution.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:** the rule itself is canonical at `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger. This bullet records the decision (governance bundle #2 landing on 2026-04-25 PR #14), not the rule body — read constitution for the actual Tier-A trigger condition, the Tier-B persona-selection SSOT, the counting command, the rollback semantics, and the verbatim text. Do not paraphrase here.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:161:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:169:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:181:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:242:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:256:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:261:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:262:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:264:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:304:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:344:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:342:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | **`.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` 是 Tier-B 选 persona 的唯一 source of truth。** 默认 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同。每次 Tier-B sub-phase commit 后必须追加一行 `<sub-phase-id>: P? (<reason>)`；新 epic 重置序列起点 = P1 |
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/codex_personas/README.md:12:- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:31:> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
.planning/codex_personas/README.md:38:# Tier-A（5 persona 并行，仅在条件满足时跑）：
.planning/codex_personas/README.md:46:# Tier-B（1 persona）：PERSONA-ROTATION-STATE.md 是唯一 source of truth。
.planning/codex_personas/README.md:88:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:97:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/codex_personas/README.md:128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

exec
/bin/zsh -lc 'rg -n "PERSONA-ROTATION-STATE|round-robin|copy diff|REWRITE/DELETE|next 3 sub-phases|no-consecutive-repeat" .' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
codex
The verdict is fixed. I’m only pulling exact `MEMORY.md` line numbers now so the final reply can satisfy the session’s memory-citation requirement without adding extra prose.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '49,58p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
Rule body in 1 place only (constitution): drift — Non-canonical rule fragments still exist at `constitution.md:11,151`, `RETRO-V61-054-ui-copy-probe-birth.md:161-164`, `README.md:12-13,46-81,104-118,127-131`, and `E11-00-PLAN.md:181,257,304,344`.
E11-00-PLAN pure pointers (zero restatement): drift — The four edited pointer spots are clean, but PLAN still restates rollback and tier semantics at `181`, `257`, `304`, and `344`.
README §Tier-trigger pure pointer: resolved — `README.md:29-33` is now a clean pointer/history block with no trigger, SSOT, counting, or rollback detail.
RETRO §6.2 pure pointer: resolved — `RETRO-V61-054-ui-copy-probe-birth.md:144-146` is a pure decision pointer; the surviving rollback restatement sits in §6.3, not §6.2.
Bash template both paths literal: resolved — `README.md:60-73` gives active Step 3a code, five literal `# PERSONA=Px` Step 3b toggles, and one hard-constraint sentinel covering both paths.
README owned operational sections free of rule body: drift — `Output convention` leaks trigger detail at `104-106`; `Anti-bias safeguard` leaks SSOT/rotation/rollback at `115-118`; `Cost` leaks trigger+rollback at `127-131`.
NEW_R6_FINDINGS:
- IMPORTANT — `constitution.md:11,151` still summarize the tier-trigger outside `§Codex Persona Pipeline Tier-Trigger`, so the rule is not single-homed even inside constitution.
- IMPORTANT — `README.md:46-81` command-template comments still encode SSOT/round-robin/state-write semantics outside constitution; executability is fixed, single-source is not.
- IMPORTANT — `E11-00-PLAN.md:181,257,304,344` still carries rollback and tier-behavior restatements, so PLAN is not pure-pointer-only.
- IMPORTANT — `RETRO-V61-054-ui-copy-probe-birth.md:161-164` keeps rollback semantics outside constitution, which independently breaks the R6 “exactly one place” strategy.

tokens used
75,911
VERDICT: CHANGES_REQUIRED
Rule body in 1 place only (constitution): drift — Non-canonical rule fragments still exist at `constitution.md:11,151`, `RETRO-V61-054-ui-copy-probe-birth.md:161-164`, `README.md:12-13,46-81,104-118,127-131`, and `E11-00-PLAN.md:181,257,304,344`.
E11-00-PLAN pure pointers (zero restatement): drift — The four edited pointer spots are clean, but PLAN still restates rollback and tier semantics at `181`, `257`, `304`, and `344`.
README §Tier-trigger pure pointer: resolved — `README.md:29-33` is now a clean pointer/history block with no trigger, SSOT, counting, or rollback detail.
RETRO §6.2 pure pointer: resolved — `RETRO-V61-054-ui-copy-probe-birth.md:144-146` is a pure decision pointer; the surviving rollback restatement sits in §6.3, not §6.2.
Bash template both paths literal: resolved — `README.md:60-73` gives active Step 3a code, five literal `# PERSONA=Px` Step 3b toggles, and one hard-constraint sentinel covering both paths.
README owned operational sections free of rule body: drift — `Output convention` leaks trigger detail at `104-106`; `Anti-bias safeguard` leaks SSOT/rotation/rollback at `115-118`; `Cost` leaks trigger+rollback at `127-131`.
NEW_R6_FINDINGS:
- IMPORTANT — `constitution.md:11,151` still summarize the tier-trigger outside `§Codex Persona Pipeline Tier-Trigger`, so the rule is not single-homed even inside constitution.
- IMPORTANT — `README.md:46-81` command-template comments still encode SSOT/round-robin/state-write semantics outside constitution; executability is fixed, single-source is not.
- IMPORTANT — `E11-00-PLAN.md:181,257,304,344` still carries rollback and tier-behavior restatements, so PLAN is not pure-pointer-only.
- IMPORTANT — `RETRO-V61-054-ui-copy-probe-birth.md:161-164` keeps rollback semantics outside constitution, which independently breaks the R6 “exactly one place” strategy.

