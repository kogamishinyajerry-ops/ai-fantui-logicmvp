2026-04-25T12:39:53.139524Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T12:39:53.139540Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc4a7-5dc0-7f73-8653-6896ab14ae7e
--------
user
You are reviewing governance bundle #2 R2 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 419286b on top of 1f25bb5).

R1 (commit 1f25bb5) returned CHANGES_REQUIRED with 3 findings:
- F1 BLOCKER: tier-B "1 persona" conflicts with §Output convention (5 verdicts assumed) + §Anti-bias safeguard (uniqueness check impossible) + E11-00-PLAN closure
- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B

Files to review (R2 commit 419286b):
- .planning/codex_personas/README.md
- .planning/constitution.md (only the bundle #2 § block, lines ~340-370)
- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md (only §6.x — context for §6.3 canonical reference)

R2 fixes claim:
1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.

Your task: Verify each R1 finding is genuinely resolved with no new spec-coherence drift, OR identify what's still inconsistent.

Output format (verbatim):
```
VERDICT: APPROVE | CHANGES_REQUIRED
F1: [resolved | partial | not resolved] — <reason ≤2 lines>
F2: [resolved | partial | not resolved] — <reason ≤2 lines>
F3: [resolved | partial | not resolved] — <reason ≤2 lines>
NEW_FINDINGS:
- <none | severity + ≤2 line summary>
```

Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.

Reply only with the structured output above. No preamble.
codex
Reviewing the R2 governance bundle as a correctness-only pass. I’m checking the cited files plus cross-doc references for `§6.2`, `§6.3`, rollback, Tier-A/Tier-B output rules, and the new trigger/rotation definitions before I issue the verdict.
exec
/bin/zsh -lc "rg -n \"ai-fantui-logicmvp|LogicMVP|governance bundle|persona|rollback|RETRO-V61-054|§6\\.3|§6\\.2\" /Users/Zhuanz/.codex/memories/MEMORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
277:- ElevenLabs, PVC, voice-cloning, Chinese TTS, 90 分钟中文探店博主语料结构表, VOICE-CORPUS-90MIN-PLAN.md, ELEVENLABS-VOICE-CORPUS-GUIDE.md, MATERIAL-DROPZONE.md, avatar-lab/inputs/persona/voice-pvc, 90-150 分钟, 20-30 分钟, 逛 / 光, pronunciation dictionaries, shop-explainer
287:- ElevenLabs voice-training materials in this project are organized under `avatar-lab/inputs/persona/voice-pvc/`; do not scatter PVC material inside transient job directories [Task 1]
304:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
310:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
320:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
542:- rollout_summaries/2026-04-15T09-02-39-gtWf-notion_v3_stabilization_s15a_s16a_s16b_opus_escalation.md (cwd=/Users/Zhuanz/AI-Notebooklm, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/15/rollout-2026-04-15T17-02-39-019d9060-d7f8-7841-b99d-96cd4b18ce5f.jsonl, updated_at=2026-04-15T10:23:11+00:00, thread_id=019d9060-d7f8-7841-b99d-96cd4b18ce5f, per-space scoping and rollback baseline with Opus escalation boundary)
546:- ReviewHold, Opus 4.6, ParameterRegistry, AntiHallucinationGateway, space_id, rollback, .gitignore, draft PR, core/storage/space_resolver.py, core/llm/client.py
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

codex
I’ve got the repo context and I’m staying in read-only review mode. Next I’m diffing `1f25bb5..419286b` and grepping the governance docs for Tier-A/Tier-B, rollback, `§6.2`/`§6.3`, the copy-count command, and rotation-state references to see whether the fixes actually converge.
exec
/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:5:> **Triggered by:** E11-02 PR #10 — first sub-phase to require 4 Codex rounds in this repo
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:7:> **Output artefacts:** constitution v2.3 §UI-COPY-PROBE; E11-00-PLAN §1.5 Surface Inventory template + 3 small differentials; `E11-02-SURFACE-INVENTORY.md` worked example
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:64:2. **强制 stage**：写完之后、commit 之前作者必须执行 claim-to-source sweep，三选一处置 [ANCHORED] / [REWRITE → planned for `<Phase-ID>`] / [DELETE]，结果登记到本期 §Surface Inventory。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:80:**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:89:| `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` 加 §1.5 Surface Inventory + Acceptance #5 + Scope 硬约束 + Counterargument C-UI | ✅ 本 PR |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:91:| 后续所有含 user-facing copy 的子 phase（E11-03..09 / E11-13..14 等）必填 §Surface Inventory | 进入 E11 phase 总验收清单（见 E11-00-PLAN.md §0 Acceptance #5） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:140:**Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:147:- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:157:- v2.3 §UI-COPY-PROBE triggers / §Surface Inventory mandate / §Anchor 格式细则
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:164:1. Roll back to default 5-persona for the next 3 sub-phases
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:180:- "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:188:- **Q1**：是否要把 §Surface Inventory 抽象成 `tools/inventory_check.py` 自动化校验脚本（grep 锚点行真实存在）？现状是手动 + Codex 抽查。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:192:- **Q3**：v2.3 §Surface Inventory 与现有 GSD `gsd-ui-checker` agent 是否重叠？
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:193:  - 倾向：**不重叠**。`gsd-ui-checker` 验 6 维度 design contract（layout / a11y / 等），是产品质量层；§Surface Inventory 验 honesty boundary（claim → src 锚点），是事实层。两者并列存在合理。
.planning/codex_personas/README.md:9:5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).
.planning/codex_personas/README.md:27:> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
.planning/codex_personas/README.md:33:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:40:git diff --stat $(git merge-base HEAD main)..HEAD -- \
.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:50:**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
.planning/codex_personas/README.md:59:# Tier-A（5 persona 并行，仅在条件满足时跑）：
.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/codex_personas/README.md:78:## Output convention
.planning/codex_personas/README.md:82:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:87:- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:93:No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
.planning/codex_personas/README.md:98:- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:102:## Anti-bias safeguard
.planning/codex_personas/README.md:104:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:109:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:111:2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
.planning/codex_personas/README.md:112:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:121:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/codex_personas/README.md:122:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:123:- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
.planning/codex_personas/README.md:125:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:250:   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
.planning/constitution.md:251:   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
.planning/constitution.md:316:- 评审者（Codex / 第二视角）有权要求作者贴出 §Surface Inventory；缺失或残缺直接 CHANGES_REQUIRED，不进入逐字 ripgrep round-trip。
.planning/constitution.md:317:- 评审者抽查 §Surface Inventory 中任意一行的锚点是否真实成立；命中 fabricated 锚点 → 视为伪造证据（同 v5.2 反假装条款）。
.planning/constitution.md:320:- 作者声称已做 sweep 但 §Surface Inventory 缺失 / 行数与 copy 不对应 / 锚点 line 不存在 → 当轮 review 视为未做自审，要求重做（不是逐条修）。
.planning/constitution.md:342:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/constitution.md:349:**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。
.planning/constitution.md:353:- v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
.planning/constitution.md:357:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:359:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:361:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/constitution.md:365:详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。

exec
/bin/zsh -lc 'git diff --unified=80 1f25bb5..419286b -- .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/codex_personas/README.md b/.planning/codex_personas/README.md
index 5a5e184..5f195b6 100644
--- a/.planning/codex_personas/README.md
+++ b/.planning/codex_personas/README.md
@@ -1,91 +1,125 @@
 # Codex Persona Review Pipeline
 
 > Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
 > Date: 2026-04-25
 > Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6
 
 ## Purpose
 
 5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).
 
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
-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
 
-**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。
+**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
+
+```bash
+# 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
+git diff --stat $(git merge-base HEAD main)..HEAD -- \
+  'src/well_harness/static/*.html' \
+  'src/well_harness/static/*.js' \
+  'src/well_harness/static/*.css'
+```
+
+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
+
+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
+
+**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
 
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
 
 # Tier-B（1 persona 默认 — P1 Junior FCS）：
 cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
   "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
   > .planning/phases/<phase-id>/persona-P1-output.md 2>&1
 
 # Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
 cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
   "$(cat .planning/codex_personas/P3-demo-presenter.md)" \
   > .planning/phases/<phase-id>/persona-P3-output.md 2>&1
 ```
 
 ## Output convention
 
-Each persona writes verdict to its own file. Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:
+Each persona writes verdict to its own file. Closure semantics depend on which tier ran:
+
+### Tier-A（5-persona 并行）
+
+Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:
 
 - 5 verdicts side-by-side
 - Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
 - Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
 - 0 BLOCKER is a phase-CLOSURE precondition
 
+### Tier-B（1-persona 默认）
+
+No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
+
+- 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
+- Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
+- 0 BLOCKER from that single persona is the phase-CLOSURE precondition
+- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
+
+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
+
 ## Anti-bias safeguard
 
-If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
+**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
 1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
 2. Triggers re-run with sharpened persona contexts
 3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework
 
+**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
+2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
+3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
+
 ## Cost / latency baseline (recorded for retro)
 
 **Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
 - PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
 - E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
 
 **Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
 - Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
 - Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
 - **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
 
-If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce post-merge defects in user-facing copy, re-evaluate whether tier-trigger conditions are too lax (RETRO-V61-054 §6.2 candidate trigger).
+If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
diff --git a/.planning/constitution.md b/.planning/constitution.md
index ae4ad62..ecc7188 100644
--- a/.planning/constitution.md
+++ b/.planning/constitution.md
@@ -279,109 +279,115 @@ reviewer 复跑命令：(a) 对 scope= 部分跑 grep，hits 数必须与 anchor
 ##### 通用约束（所有 anchor）
 
 - section-only 引用（如 `constitution.md §v5.2 红线` / `PROJECT.md §Vision`）**不算 anchor**——必须落到行号或 `scope=<file>` 形式。
 - 多锚点用 ` + ` 拼接（参见正面 claim 多源支持的情形）。
 
 ##### 写作模板
 
 正面 claim：
 
 ```
 src/well_harness/static/workbench.js:140-164 (preset 数组定义 4 项 + 各自 archiveBundle 标记)
 ```
 
 负面 claim（带 peer）：
 
 ```
 scope=src/well_harness/static/workbench.html (grep "demo-mode\|demo-stage" 0 hits); peer=src/well_harness/static/workbench.html:283-299 (view-mode-toggle-bar 存在，仅 beginner / expert 两键)
 ```
 
 负面 claim（仅 scope）：
 
 ```
 scope=src/well_harness/static/workbench.js (grep "approval-action\|data-approval-action" 0 hits)
 ```
 
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
 | 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
 
 **例外（仍跑全 5）：**
 - 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
 - Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
 
 **判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。
 
 **保留不变：**
 - v2.2 EMPIRICAL-CLAIM-PROBE 的全部触发条件
 - v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
 - v6.1 Codex 触发清单（多文件 UI / API 契约 / OpenFOAM solver / CFD 几何 / Phase E2E 失败 / Docker+OpenFOAM / GSD 产出物等）
 - §RETRO 序号、Self-Pass-Rate 强制、Hard Stop Points、Verbatim Exception
 
 **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
 
-**回滚条件：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE 失效条件被触发） → 自动回滚到 5-persona 默认 + 入 RETRO-V61-054 §6.2 候选触发位置。
+**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
+
+1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
+2. 开新 RETRO-V61-* 文件记录失败摊销，链接到 RETRO-V61-054
+3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
+
+详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
 
 **详细文档：** `.planning/codex_personas/README.md` §Invocation 表，更新于本 bundle。RETRO-V61-054 §6 amortization 实证记录。
 
 ### Verbatim Exception（继承 v6.0，五条件 AND）
 
 允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
 
 ### Self-Pass-Rate 强制
 
 任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
 
 ### Hard Stop Points
 
 - 需要修红线 → 停 + 索取 Kogami explicit "truth-engine 修复 logic-X" 字面授权
 - Codex returns BLOCKER 不能 verbatim 修 → 停 + 升级到 Kogami
 - 三轨任一连续 ≥3 次新增失败且非 inherited → 停 + 写 forensics + 升级
 - 意外触红线（grep 命中 `controller.py` 在 `git diff` 中）→ `git checkout` 撤销 + 立即停车汇报
 
 ### Commit Trailer (v6.1)
 
 ```
 Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
 ```
 
 ### 撤销条件
 
 - Kogami chat 中显式 "撤销 v6.1 / 收回授权 / 暂停自驱"
 - Claude Code 自评发现已超出能力边界（含红线无法绕开） → 自请暂停 + 升级

exec
/bin/zsh -lc 'git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/governance-bundle-2/

codex
The first pass already shows one likely coherence problem: `README.md` was updated, but `constitution.md` still appears to keep the old Tier-B selector text in the rule table. I’m opening the exact sections with line numbers and checking whether the rollback canon and the new rotation-state mechanism are actually enforceable in-tree.
exec
/bin/zsh -lc "nl -ba .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md | sed -n '140,176p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '334,372p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '1,170p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   140	**Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
   141	
   142	### 6.2 governance bundle #2 — persona pipeline tier-trigger
   143	
   144	Per Opus §1 verbatim spec, this RETRO §6.1 unlocks the rule change:
   145	
   146	**5-persona pipeline → tier-trigger:**
   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows
   148	- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
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
   171	- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
   172	- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
   173	- Estimated savings on persona pipeline: **~70–80%** Codex tokens
   174	- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
   175	
   176	### 6.5 Meta-observation

 succeeded in 0ms:
   334	**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
   335	
   336	**实证：** E11-09 dual-h1 fix PR #13 落地于 2026-04-25，Codex 2 轮 APPROVE（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。leading indicator fired。
   337	
   338	**新规则（替换"每个 user-facing UI 子 phase 默认跑全 5"）：**
   339	
   340	| 条件 | persona 数 | 选哪个 |
   341	|---|---|---|
   342	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
   343	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
   344	
   345	**例外（仍跑全 5）：**
   346	- 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
   347	- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
   348	
   349	**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。
   350	
   351	**保留不变：**
   352	- v2.2 EMPIRICAL-CLAIM-PROBE 的全部触发条件
   353	- v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
   354	- v6.1 Codex 触发清单（多文件 UI / API 契约 / OpenFOAM solver / CFD 几何 / Phase E2E 失败 / Docker+OpenFOAM / GSD 产出物等）
   355	- §RETRO 序号、Self-Pass-Rate 强制、Hard Stop Points、Verbatim Exception
   356	
   357	**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
   358	
   359	**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
   360	
   361	1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
   362	2. 开新 RETRO-V61-* 文件记录失败摊销，链接到 RETRO-V61-054
   363	3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
   364	
   365	详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
   366	
   367	**详细文档：** `.planning/codex_personas/README.md` §Invocation 表，更新于本 bundle。RETRO-V61-054 §6 amortization 实证记录。
   368	
   369	### Verbatim Exception（继承 v6.0，五条件 AND）
   370	
   371	允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
   372	

 succeeded in 0ms:
     1	# Codex Persona Review Pipeline
     2	
     3	> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
     4	> Date: 2026-04-25
     5	> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6
     6	
     7	## Purpose
     8	
     9	5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).
    10	
    11	## Persona inventory
    12	
    13	| ID | Persona | File |
    14	|---|---|---|
    15	| P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
    16	| P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
    17	| P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
    18	| P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
    19	| P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |
    20	
    21	## Invocation
    22	
    23	### Tier-trigger（governance bundle #2 落地，2026-04-25 起生效）
    24	
    25	> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
    26	>
    27	> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
    28	
    29	按下表决定调多少 persona：
    30	
    31	| 子 phase 特征 | persona 数 | 选哪个 |
    32	|---|---|---|
    33	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
    34	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
    35	
    36	**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
    37	
    38	```bash
    39	# 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
    40	git diff --stat $(git merge-base HEAD main)..HEAD -- \
    41	  'src/well_harness/static/*.html' \
    42	  'src/well_harness/static/*.js' \
    43	  'src/well_harness/static/*.css'
    44	```
    45	
    46	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
    47	
    48	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
    49	
    50	**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
    51	
    52	**例外（仍跑全 5）：**
    53	- 该子 phase 触发了 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
    54	- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
    55	
    56	### 命令模板
    57	
    58	```bash
    59	# Tier-A（5 persona 并行，仅在条件满足时跑）：
    60	for p in P1 P2 P3 P4 P5; do
    61	  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    62	    "$(cat .planning/codex_personas/${p}-*.md)" \
    63	    > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
    64	done
    65	wait
    66	
    67	# Tier-B（1 persona 默认 — P1 Junior FCS）：
    68	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    69	  "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
    70	  > .planning/phases/<phase-id>/persona-P1-output.md 2>&1
    71	
    72	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
    73	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    74	  "$(cat .planning/codex_personas/P3-demo-presenter.md)" \
    75	  > .planning/phases/<phase-id>/persona-P3-output.md 2>&1
    76	```
    77	
    78	## Output convention
    79	
    80	Each persona writes verdict to its own file. Closure semantics depend on which tier ran:
    81	
    82	### Tier-A（5-persona 并行）
    83	
    84	Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:
    85	
    86	- 5 verdicts side-by-side
    87	- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
    88	- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
    89	- 0 BLOCKER is a phase-CLOSURE precondition
    90	
    91	### Tier-B（1-persona 默认）
    92	
    93	No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
    94	
    95	- 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
    96	- Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
    97	- 0 BLOCKER from that single persona is the phase-CLOSURE precondition
    98	- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
    99	
   100	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
   101	
   102	## Anti-bias safeguard
   103	
   104	**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
   105	1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
   106	2. Triggers re-run with sharpened persona contexts
   107	3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework
   108	
   109	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
   110	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
   111	2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
   112	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
   113	
   114	## Cost / latency baseline (recorded for retro)
   115	
   116	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
   117	- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
   118	- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
   119	
   120	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
   121	- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
   122	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
   123	- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
   124	
   125	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.

exec
/bin/zsh -lc "rg -n \"§6\\.2|§6\\.3|rollback|Tier-B|PERSONA-ROTATION-STATE|copy_diff_lines|git diff --stat\" .planning" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/audit/bundles/README.md:34:git diff --stat dd915e1 feat/p31-orphan-triage
.planning/audit/bundles/p32-provenance-backfill-README.md:55:git diff --stat dd915e1 feat/p32-provenance-backfill
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/constitution.md:357:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:359:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:361:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/constitution.md:365:详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:40:git diff --stat $(git merge-base HEAD main)..HEAD -- \
.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:109:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:112:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:122:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:125:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/P43-control-logic-workbench/P43-00-PLAN.md:248:- **Side-effect ordering（v3 新补）**：`final_approve` event 触发 side-effect 序：① localStorage state → APPROVING · ② server-side adapter emit + registry row append（原子）· ③ `archive_workbench_bundle` manifest append · ④ localStorage state → APPROVED。任何一步失败 · 回退到 ① 前状态 · 上报 error taxonomy `partial_approve_rollback`
.planning/phases/governance-bundle-2/codex-r2-output.md:20:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-output.md:21:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
.planning/phases/governance-bundle-2/codex-r2-output.md:26:- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md (only §6.x — context for §6.3 canonical reference)
.planning/phases/governance-bundle-2/codex-r2-output.md:29:1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
.planning/phases/governance-bundle-2/codex-r2-output.md:30:2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:49:Reviewing the R2 governance bundle as a correctness-only pass. I’m checking the cited files plus cross-doc references for `§6.2`, `§6.3`, rollback, Tier-A/Tier-B output rules, and the new trigger/rotation definitions before I issue the verdict.
.planning/phases/governance-bundle-2/codex-r2-output.md:51:/bin/zsh -lc "rg -n \"ai-fantui-logicmvp|LogicMVP|governance bundle|persona|rollback|RETRO-V61-054|§6\\.3|§6\\.2\" /Users/Zhuanz/.codex/memories/MEMORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:67:542:- rollout_summaries/2026-04-15T09-02-39-gtWf-notion_v3_stabilization_s15a_s16a_s16b_opus_escalation.md (cwd=/Users/Zhuanz/AI-Notebooklm, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/15/rollout-2026-04-15T17-02-39-019d9060-d7f8-7841-b99d-96cd4b18ce5f.jsonl, updated_at=2026-04-15T10:23:11+00:00, thread_id=019d9060-d7f8-7841-b99d-96cd4b18ce5f, per-space scoping and rollback baseline with Opus escalation boundary)
.planning/phases/governance-bundle-2/codex-r2-output.md:68:546:- ReviewHold, Opus 4.6, ParameterRegistry, AntiHallucinationGateway, space_id, rollback, .gitignore, draft PR, core/storage/space_resolver.py, core/llm/client.py
.planning/phases/governance-bundle-2/codex-r2-output.md:212:I’ve got the repo context and I’m staying in read-only review mode. Next I’m diffing `1f25bb5..419286b` and grepping the governance docs for Tier-A/Tier-B, rollback, `§6.2`/`§6.3`, the copy-count command, and rotation-state references to see whether the fixes actually converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:225:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r2-output.md:227:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r2-output.md:230:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r2-output.md:232:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r2-output.md:240:.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:241:.planning/codex_personas/README.md:40:git diff --stat $(git merge-base HEAD main)..HEAD -- \
.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:246:.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:247:.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:251:.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:257:.planning/codex_personas/README.md:109:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:260:.planning/codex_personas/README.md:112:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:262:.planning/codex_personas/README.md:122:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:264:.planning/codex_personas/README.md:125:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:265:.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r2-output.md:272:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:275:.planning/constitution.md:357:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:276:.planning/constitution.md:359:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:277:.planning/constitution.md:361:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:278:.planning/constitution.md:365:详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
.planning/phases/governance-bundle-2/codex-r2-output.md:322:+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:329:+git diff --stat $(git merge-base HEAD main)..HEAD -- \
.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:356: # Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:361: # Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:381:+### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:400:+**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:403:+3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:413: - Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:416:-If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce post-merge defects in user-facing copy, re-evaluate whether tier-trigger conditions are too lax (RETRO-V61-054 §6.2 candidate trigger).
.planning/phases/governance-bundle-2/codex-r2-output.md:417:+If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:487: | 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:501: **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:503:-**回滚条件：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE 失效条件被触发） → 自动回滚到 5-persona 默认 + 入 RETRO-V61-054 §6.2 候选触发位置。
.planning/phases/governance-bundle-2/codex-r2-output.md:504:+**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:506:+1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:510:+详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
.planning/phases/governance-bundle-2/codex-r2-output.md:546:The first pass already shows one likely coherence problem: `README.md` was updated, but `constitution.md` still appears to keep the old Tier-B selector text in the rule table. I’m opening the exact sections with line numbers and checking whether the rollback canon and the new rotation-state mechanism are actually enforceable in-tree.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:5:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:6:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:11:- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md (only §6.x — context for §6.3 canonical reference)
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:14:1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:15:2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.

codex
I need one more cross-check on the upstream plan because F1 was partly about E11 closure semantics, not just README wording. I’m opening the E11 plan section that defines the persona pipeline to see whether R2 actually aligned the canonical execution contract or only patched the derivative docs.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '160,210p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'rg -n "persona|Aggregator|unique|uniqueness|5 verdict|5 persona|Tier-A|Tier-B|closure|phase-CLOSURE|E11-04-PERSONA-REVIEW-RESULTS" .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
17:2. 5 个 Codex personas 各自跑一次 review，BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2 个/persona。
86:每个 persona 在 §6 会有 distinct Codex prompt。
94:| **E11-01** | Persona journey maps + gap audit per surface — 输出 `JOURNEYS.md` 把 5 personas × 当前 11 维度展开成 55 个 cell，标记每个 cell BLOCKED / FRICTION / OK | 无 | 不 |
103:| **E11-10** | Codex persona-review pipeline — 5 个 reusable prompts 落 `.planning/codex_personas/`，并跑首轮 review on E11-02..09 阶段产出 | E11-02..09 一一就绪后逐个跑 | 不 |
105:| **E11-12** | CLOSURE — `E11-12-CLOSURE.md` + persona review summary + 三轨证据 + 自签 GATE-E11-CLOSURE: Approved (v6.1) | E11-01..19（除 E11-12 自身外的 18 项 closed） | 不 |
143:- **C（先做 E11-12 closure 收 phase 再换新 phase）**：拒绝。18 子 phase 没做先 closure 是伪闭环。
147:不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
160:| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
165:- 否则降为 1-persona（任选 P1/P2/P3/P4/P5 之一，默认 P1 + 当期 owner 视情况轮换）
177:- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
178:- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
180:**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
182:**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
190:**目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。
209:**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。
211:### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) 加 anti-bias safeguard：每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding，否则 review 不算 valid（pipeline 强制项）。结论：bias 风险存在但已通过 distinct context + cross-persona uniqueness 要求 mitigated。
221:**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
233:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
243:| Codex 5 personas pipeline 跑一轮 ≈ 5 × 10min ≈ 1h CPU 时间 | Low | 后台跑（已有先例），分 batch；persona 失败 retry 1 次后转 manual review |
251:详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
256:4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings + ≥1 finding NOT covered by other personas
260:- Claude Code 汇总 5 份 verdict 进 `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md`
281:| E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
294:## 8. Verification protocol (E11 closure 前必跑)
302:| Codex personas | 5/5 verdict in {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER count = 0 across all | `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md` |
314:3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
320:9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
326:1. 5 personas 的 specific company / 项目 context 要不要 fictionalize？（默认: 是，避免暗示真实客户）
342:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 5-persona Codex review 结果。

 succeeded in 0ms:
   160	| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
   161	| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
   162	
   163	**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
   164	- 触发条件 = (a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE]
   165	- 否则降为 1-persona（任选 P1/P2/P3/P4/P5 之一，默认 P1 + 当期 owner 视情况轮换）
   166	- v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**
   167	
   168	**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
   169	
   170	### 3.6.1 Leading Indicator OUTCOME — fired ≤2 rounds (2026-04-25)
   171	
   172	E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。R1 的 BLOCKER 不是 honesty 类（不是 fabricated surface claim），是**真实 runtime bug**（workbench.js 共享 shell + bundle 但 binding bundle-only 元素无 null guard），属于 reactive review 正常工作。
   173	
   174	**Action 触发**：governance bundle #2 已通过 PR #14 落地（2026-04-25）：
   175	
   176	- `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
   177	- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
   178	- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
   179	
   180	**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
   181	
   182	**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
   183	
   184	**详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.
   185	
   186	---
   187	
   188	## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
   189	
   190	**目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。
   191	
   192	**条件解锁**：满足全部 3 条后可并发启动一个**不动 src/** 的 E12 spec phase（如 fault diagnosis 的 PRD + intake packet schema）：
   193	1. E11-09 ≤ 2 轮 Codex APPROVE（证 v2.3 摊销）
   194	2. E11-06 完成（E11-15..19 进入纯前端期）
   195	3. 该 E12 候选明确不动 `src/well_harness/{controller,runner,models,plant}.py` / `adapters/` / `tests/e2e/test_wow_a*`
   196	
   197	**理由**：并发 src/ phase 会拉高 truth-engine 触碰风险且让"v2.3 摊销 vs bloat"归因失败（两个 phase 同时跑 Codex 会污染 leading indicator 数据）。
   198	
   199	---
   200	
   201	## 4. Tier-1 Adversarial Self-Review（v5.2 红线 #3 强制）
   202	
   203	> 三个最强自我反对意见 + 显式 rebuttal。
   204	
   205	### Counterargument #1: "为什么不让真工程师上手反馈再改？"
   206	
   207	**反对论点**: pre-emptive UX 工作可能优化错的方向。等到第一个 customer-facing 工程师 onboard 时再迭代，更省成本，避免 design-by-imagination。
   208	
   209	**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。
   210	

exec
/bin/zsh -lc "find .planning/phases -name 'PERSONA-ROTATION-STATE.md' -print" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
codex
I found a second likely drift source outside the three edited files: the E11 plan still contains hard 5-persona/5-verdict closure language. I’m reading the exact verification and closure lines now, because if those remain canonical, the README split alone does not actually resolve F1.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '248,318p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   248	
   249	## 6. Codex Persona Review Pipeline
   250	
   251	详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
   252	
   253	1. **Persona 背景** — role / experience / mental model
   254	2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
   255	3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
   256	4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings + ≥1 finding NOT covered by other personas
   257	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
   258	
   259	每轮 review 跑完后：
   260	- Claude Code 汇总 5 份 verdict 进 `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md`
   261	- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
   262	- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一
   263	
   264	---
   265	
   266	## 7. Sequencing & estimated effort
   267	
   268	| Sub-phase | Type | LOC est | Time est | Codex required? |
   269	|---|---|---|---|---|
   270	| E11-01 | doc | ~300 | 30min | NO |
   271	| E11-02 | code (HTML/JS) | ~200 | 1h | YES (UI 交互模式变更) |
   272	| E11-03 | refactor (HTML/CSS) | ~150 | 45min | YES (UI 交互模式变更) |
   273	| E11-04 | doc + code | ~100 | 30min | NO (mechanical relabel) |
   274	| E11-05 | code (JS) | ~150 | 1h | YES (UI 交互模式变更) |
   275	| E11-06 | code (HTML/JS) | ~120 | 45min | YES (新 API 调用 / 状态聚合) |
   276	| E11-07 | code (HTML/CSS) | ~80 | 30min | NO (添加 banner，无逻辑) |
   277	| E11-08 | code (JS) | ~60 | 30min | NO (单 conditional 文案) |
   278	| E11-09 | refactor (routing) | ~200 | 1h | YES (路由变更 → 用户导航 mode) |
   279	| E11-10 | doc | ~600 (5 prompts) | 1.5h | self-review only |
   280	| E11-11 | test | ~150 | 1h | YES (新 e2e 期望) |
   281	| E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
   282	| E11-13 | code (HTML/CSS) | ~100 | 45min | YES (UI 交互模式变更 + manual mode trust 可视化) |
   283	| E11-14 | code (Python endpoint guard) | ~80 | 1h | YES (server-side guard, adapter boundary 内) |
   284	| E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
   285	| E11-16 | code (Python) | ~120 | 1h | YES (approval endpoint 三元绑定) |
   286	| E11-17 | code (HTML/CSS/JS) | ~180 | 1h | YES (presenter mode toggle = UI 交互模式变更) |
   287	| E11-18 | code (HTML/JS) | ~150 | 1h | YES (logic-gate trace tuple + schema 升级) |
   288	| E11-19 | code (HTML/JS + schema) | ~250 | 1.5h | YES (UI 交互模式变更 + ticket schema enrichment) |
   289	
   290	**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
   291	
   292	---
   293	
   294	## 8. Verification protocol (E11 closure 前必跑)
   295	
   296	| 维度 | 标准 | 锚点 |
   297	|---|---|---|
   298	| Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
   299	| E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
   300	| Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
   301	| Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
   302	| Codex personas | 5/5 verdict in {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER count = 0 across all | `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md` |
   303	| Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
   304	| EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |
   305	
   306	---
   307	
   308	## 9. CLOSURE 退出条件
   309	
   310	E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：
   311	
   312	1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
   313	2. ✅ §8 verification protocol 全部通过
   314	3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
   315	4. ✅ truth-engine 红线 0 触碰
   316	5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
   317	6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
   318	7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria

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
    17	2. 5 个 Codex personas 各自跑一次 review，BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2 个/persona。
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

exec
/bin/zsh -lc 'rg -n "copy_diff_lines|PERSONA-ROTATION-STATE|round-robin|discarded and the full 5-persona|re-executes|Tier-B.*upgrade|upgrade.*Tier-A" .planning' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:679:    46	读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:681:    48	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:733:   100	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:743:   110	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:761:/bin/zsh -lc "rg -n \"§6\\.2|§6\\.3|rollback|Tier-B|PERSONA-ROTATION-STATE|copy_diff_lines|git diff --stat\" .planning" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:778:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:779:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:783:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:785:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:795:.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:796:.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:802:.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:809:.planning/phases/governance-bundle-2/codex-r2-output.md:242:.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:810:.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:814:.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:816:.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:828:.planning/phases/governance-bundle-2/codex-r2-output.md:335:+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/phases/governance-bundle-2/codex-r2-output.md:829:.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:833:.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:835:.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:852:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:853:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:950:/bin/zsh -lc "find .planning/phases -name 'PERSONA-ROTATION-STATE.md' -print" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/codex_personas/README.md:46:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.

codex
I’ve finished the substantive review and I’m checking one last bookkeeping item for the final response: if I cite memory, I need the exact line range and rollout id. Then I’ll return the structured verdict only.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '810,812p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '791,804p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   810	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   811	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
   812	

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

codex
```text
VERDICT: CHANGES_REQUIRED
F1: partial — README now splits Tier-A/Tier-B output correctly, but E11-00-PLAN still hardcodes 5-persona closure/uniqueness/aggregator semantics at lines 17, 256, 260, 302.
F2: partial — README, constitution, and RETRO §6.3 now align, but E11-00-PLAN:182 still reduces rollback to “5-persona default + retro successor” and omits the 3-sub-phase + Opus steps.
F3: not resolved — deterministic counting/round-robin exists only in README; constitution.md:343 and RETRO §6.2 still preserve the old default-P1/owner-rotation wording, so the canonical rule is still ambiguous.
NEW_FINDINGS:
- IMPORTANT: .planning/codex_personas/README.md:9 still says the pipeline "ensures inter-persona finding uniqueness", which is false for Tier-B where uniqueness is explicitly N/A.
- NIT: `PERSONA-ROTATION-STATE.md` is referenced but not created; acceptable if seeded on first Tier-B sub-phase, so not the blocker here.
```

tokens used
125,757
```text
VERDICT: CHANGES_REQUIRED
F1: partial — README now splits Tier-A/Tier-B output correctly, but E11-00-PLAN still hardcodes 5-persona closure/uniqueness/aggregator semantics at lines 17, 256, 260, 302.
F2: partial — README, constitution, and RETRO §6.3 now align, but E11-00-PLAN:182 still reduces rollback to “5-persona default + retro successor” and omits the 3-sub-phase + Opus steps.
F3: not resolved — deterministic counting/round-robin exists only in README; constitution.md:343 and RETRO §6.2 still preserve the old default-P1/owner-rotation wording, so the canonical rule is still ambiguous.
NEW_FINDINGS:
- IMPORTANT: .planning/codex_personas/README.md:9 still says the pipeline "ensures inter-persona finding uniqueness", which is false for Tier-B where uniqueness is explicitly N/A.
- NIT: `PERSONA-ROTATION-STATE.md` is referenced but not created; acceptable if seeded on first Tier-B sub-phase, so not the blocker here.
```

