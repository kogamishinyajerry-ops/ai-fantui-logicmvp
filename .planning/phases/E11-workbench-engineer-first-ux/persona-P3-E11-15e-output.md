2026-04-26T03:58:02.519541Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T03:58:02.519629Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc7ef-eb18-73b2-8020-0a3e8b2fdaa0
--------
user
You are Codex GPT-5.4 acting as **Persona P3 — Bilingual Copy & Convention Editor** (Tier-A persona pipeline, E11-15e sub-phase, R1, **lead persona** by round-robin succession from E11-15d's P2).

Read `.planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md` for sub-phase scope, files, and verification baseline.

## Your specific lens (P3 — Bilingual Copy & Convention Editor, lead)

You are the editor responsible for the `<中文> · <English>` bilingualization convention quality. Your scope:

1. **Convention adherence — Chinese-first ordering**
   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?

2. **Bilingual copy quality — Chinese phrasing**
   - Do the Chinese translations read naturally to a Mandarin-native flight-controls engineer?
   - Specific calls to scrutinize:
     - `身份 · Identity` — is `身份` natural for an "Identity" chip in an FCS context, or would `角色` (role) be more idiomatic here? (Note: there's already a separate ENGINEER role concept in the data-role attribute.)
     - `工单 · Ticket` — is `工单` the right register for a ticketing system? `任务` / `工作令` / `工单` differ in formality.
     - `反馈模式 · Feedback Mode` — natural?
     - `手动（仅参考）· Manual (advisory)` — does the parenthetical placement read well in Chinese? Would `仅参考的手动模式 · Manual (advisory)` or `手动反馈 · 仅作参考 · Manual (advisory)` be more readable?
     - `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` — three middle dots in one string. Acceptable, or should the inner Chinese clause use a different punctuation (e.g., comma)?
     - `真值引擎 · 只读 · Truth Engine — Read Only` — three-segment middle-dot chain. Same question.
     - `这里"手动反馈"的含义 · What "manual feedback" means here:` — `这里` placement at the start. Native order would be `"手动反馈"在此的含义` or `"手动反馈"的含义在此`. Is `这里...的含义` actually correct?
     - `该模式仅作参考` — register match with `That mode is advisory.`?
     - `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威` — `仍然是权威` vs `仍是权威` vs `保持权威`?

3. **Long-form trust banner Chinese clauses**
   - The trust banner body has three sentences. Chinese is added before each English clause. Read the rendered Chinese-only content as a coherent paragraph — does it flow? Are the Chinese sentence boundaries clear when the English is stripped out?
   - Is the technical vocabulary (`logic gate L1–L4`, `controller 派发`, `审计链`, `manual feedback`, `truth engine`) appropriately mixed (transliterated vs translated)?

4. **WOW h3 direction-flip correctness**
   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
   - Do the WOW card descriptions (under each h3) need any adjustment to match the new title direction?

5. **Anything else within bilingual copy / convention scope**
   - Does any of the 22 REWRITE strings violate the `<中文> · <English>` pattern in a subtle way?
   - Are any English-only surfaces left on the same DOM blocks where bilingual neighbors now exist (visual/copy inconsistency)? Example: if `身份 · Identity` is the chip label, what about the chip value `Kogami / Engineer` — is leaving that English-only inconsistent?

## Files to inspect

- `git diff main..83d69e4 src/well_harness/static/workbench.html`
- `git diff main..83d69e4 src/well_harness/static/workbench.js`
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` (especially the parametrized positive-lock list to verify no copy slipped past you)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` Section 2 (full surface table)

## Out of scope for your lens (other personas cover these)

- P1: engineer-task-flow regression
- P2: surface-inventory honesty + closure-claim guards
- P4: lockstep test contract preservation
- P5: truth-engine red-line + JS-HTML lockstep

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Then list findings with severity tags (`BLOCKER` / `IMPORTANT` / `NIT`), each with `file:line` reference and `Suggested fix:` bullet.

Be specific. If a Chinese phrase reads awkwardly, propose the exact replacement. If a convention is violated, cite which prior sub-phase established it.

codex
I’m treating this as a read-only bilingual copy/convention review for E11-15e. I’ll load the shared context, skim any relevant LogicMVP memory, then inspect the exact diff, tests, and surface inventory before issuing an approval verdict with line-cited findings.
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
/bin/zsh -lc 'rg -n "E11-15e|LogicMVP|bilingual|Chinese-first|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
sed: /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md: No such file or directory

codex
I’m using `using-superpowers` to force the skill check and `gsd-code-review` as the review workflow. Next I’m reading the E11-15e shared context plus the exact HTML/JS/test/inventory deltas the prompt named.
exec
/bin/zsh -lc "sed -n '1,240p' /Users/Zhuanz/.agents/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/_E11-15e-prompt-shared-context.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15e — shared context for Tier-A persona prompts

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**PR:** #30
**HEAD:** `83d69e4`
**Tier:** A (copy_diff_lines ~38, REWRITE rows = 22; per constitution Tier-A iff ≥10 lines AND ≥3 REWRITE)
**Round-robin lead:** P3 (successor of E11-15d's P2)

## What E11-15e ships

Bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review (`tests/test_workbench_approval_flow_polish.py:189-194`).

**Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim so prior substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar) keep passing without contract churn.

## Files in scope

- `src/well_harness/static/workbench.html` — 21 REWRITE strings
- `src/well_harness/static/workbench.js` — 1 lockstep edit at line 3788 (feedback-mode chip dynamic text, both `truth_engine` and `manual_feedback_override` branches bilingualized)
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` — 67 new test cases (positive bilingual locks + stale-English negative guards + English-suffix preservation + structural anchors + JS lockstep + live-served route + truth-engine red-line guard)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan

## Files explicitly NOT in scope (truth-engine red line)

`controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`. The new lockstep guard `test_e11_15e_does_not_touch_truth_engine_backend` scans these 4 backend files for any of the 23 Chinese display strings introduced in this sub-phase.

## Verification baseline

- 67/67 new tests pass
- 188/188 prior workbench tests pass (lockstep contracts preserved)
- 1221/1221 full suite passes (0 regressions, 35 deselected per default markers)

## Surface honesty pledge

E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.

## Codex degradation contingency

If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).

exec
/bin/zsh -lc "sed -n '1,260p' .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY

**Date:** 2026-04-26
**Status:** in_review (Tier-A, ≥15 REWRITE rows → 5-persona dispatch)
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**Scope:** Bilingualize the user-visible English-only surfaces on `/workbench`
that P2 enumerated during the E11-15d Tier-B review (see
`tests/test_workbench_approval_flow_polish.py:189-194`).

---

## 1. Tier classification

Per the constitution, Tier = **Tier-A** iff
`copy_diff_lines ≥ 10 AND (REWRITE + DELETE) count ≥ 3`.

| Metric | Count |
|--------|------:|
| copy_diff_lines (workbench.html + workbench.js)        | ~38 |
| REWRITE rows (display strings rewritten in place)      | **22** |
| DELETE rows (English-only string removed without bilingual replacement) | 0 |
| ADD rows (new strings introduced for the first time)   | 0 |

**Verdict: Tier-A.** Dispatch round-robin successor of E11-15d's P2 → **P3**, plus
P1, P2, P4, P5 per Tier-A 5-persona requirement.

---

## 2. Surface table (REWRITE = 22)

Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
passing without contract churn.

| # | Surface | File:Line | Old (English-only) | New (bilingual) |
|---|---------|-----------|---------------------|-----------------|
| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |

(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs
for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`
counts in the metric table above.)

---

## 3. Out of scope (explicitly deferred — surface-honesty closure)

E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
following surfaces remain English-only and are **deferred to future sub-phases
or constitutional decisions**, not silently included:

| Deferred surface | Why deferred | File:Line |
|------------------|--------------|-----------|
| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |

**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
"all" or "the last". The deferred list above is **non-exhaustive** — if a
reviewer finds another English-only user-visible surface not listed here that is
neither REWRITE in this slice nor in the deferred table, that finding is
**legitimate** and a CHANGES_REQUIRED is appropriate.

---

## 4. Truth-engine red line

Display-copy edits only. `controller.py` / `runner.py` / `models.py` /
`src/well_harness/adapters/` / `demo_server.py` are **untouched**. Lockstep
guard at `tests/test_workbench_e11_15e_chinese_first_bundle.py::
test_e11_15e_does_not_touch_truth_engine_backend` scans backend files for any
of the 23 Chinese display strings introduced here.

---

## 5. Lockstep test impact

| Existing test file | Impact | Reason |
|--------------------|--------|--------|
| `test_workbench_trust_affordance.py` | ✅ no change | All 5 substring locks (`Manual (advisory)`, `Truth engine readings`, `Hide for session`, `What "manual feedback" means here`, `That mode is advisory.`) are preserved as English suffixes. |
| `test_workbench_authority_banner.py` | ✅ no change | `Truth Engine — Read Only` preserved as suffix. |
| `test_workbench_role_affordance.py` | ✅ no change | `Pending Kogami sign-off` preserved as suffix. |
| `test_workbench_column_rename.py` | ✅ no change | Pre-hydration `Waiting for ... panel boot.` substrings preserved as suffixes; post-hydration JS strings unchanged (out of scope). |
| `test_workbench_state_of_world_bar.py` | ✅ no change | `advisory · not a live truth-engine reading` preserved as suffix. |
| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
| `test_workbench_chinese_h2_button_sweep.py` | ✅ no change | h2/button sweep targets are already-bilingual surfaces. |
| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
| `test_workbench_e11_15e_chinese_first_bundle.py` (new) | ✅ added | 67 tests — positive bilingual locks, stale-English negative guards, English-suffix preservation locks, structural anchors, JS lockstep, live-served route, truth-engine red-line guard. |

Full suite verification: **1221 passed, 0 regressions** (pre-PR baseline 1154).

---

## 6. Persona dispatch plan

Tier-A → 5-persona round-robin. E11-15d closed with P2 → successor for E11-15e
**lead** is **P3**.

| Persona | Lens |
|---------|------|
| P1 | Engineer-task-flow regression |
| P2 | Surface-inventory honesty + closure-claim guards |
| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
| P4 | Lockstep test contract preservation (no churn on existing locks) |
| P5 | Truth-engine red-line + JS-HTML lockstep |

**Codex degradation contingency:** if all 5 codex accounts are
secondary-window-throttled or token-refresh-failed (as in E11-15d R3), apply
**Executor 即 Gate (v3.2 治理折叠)** per the project memory rule:
Claude Code Opus 4.7 self-signs the Tier-A gate, transparently documenting the
fallback in PR body + `dev_handoff.md` + this inventory's persona-rotation
entry. Self-signing requires the standard 1221-test green + repo-honesty self-
review (this inventory + Section 3 surface-honesty pledge satisfy that bar).

exec
/bin/zsh -lc "sed -n '1,260p' tests/test_workbench_e11_15e_chinese_first_bundle.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
"""E11-15e — Tier-A Chinese-first bundle regression lock.

Bilingualizes 17 user-visible English-only surfaces enumerated by P2
during the E11-15d review (see test_workbench_approval_flow_polish.py
docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
E11-15d-SURFACE-INVENTORY.md):

  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
                          open issues / advisory flag
  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
  Authority banner (1):   Truth Engine — Read Only headline
  Trust dismiss (1):      Hide for session button
  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
  Reference packet (1):   Annotate column intro <p>
  Inbox empty (1):        No proposals submitted yet.
  Pending sign-off (1):   Pending Kogami sign-off

Pattern: `<中文> · <English>` everywhere; English suffix is preserved
verbatim so all prior `assert <english> in html` substring locks across
test_workbench_trust_affordance, test_workbench_authority_banner,
test_workbench_role_affordance, test_workbench_column_rename, and
test_workbench_state_of_world_bar continue to pass without contract
churn.

Out of scope (deferred to a future Tier-A or constitutional decision):
  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    domain proper nouns coupled to value-attribute IDs and to the
    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    locked by tests/test_workbench_column_rename.py:170-172 — those are
    a separate JS-side bilingualization with their own lockstep contract.
  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    </pre> flow diagram — visual phase-arrow, not English copy.
  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    that were already bilingualized in earlier sub-phases.

Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
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


# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────


@pytest.mark.parametrize(
    "bilingual",
    [
        # Topbar chip labels (5)
        "<span>身份 · Identity</span>",
        "<span>工单 · Ticket</span>",
        "<span>反馈模式 · Feedback Mode</span>",
        "<span>系统 · System</span>",
        "<strong>手动（仅参考）· Manual (advisory)</strong>",
        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
        # State-of-world labels (4) + advisory flag (1)
        "真值引擎 SHA · truth-engine SHA",
        "最近 e2e · recent e2e",
        "对抗样本 · adversarial",
        "未关闭问题 · open issues",
        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
        # Trust banner body (3)
        '这里"手动反馈"的含义 · What "manual feedback" means here:',
        "该模式仅作参考 · That mode is advisory.",
        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
        # Trust banner dismiss (1)
        "隐藏（本次会话）· Hide for session",
        # Authority banner headline (1)
        "真值引擎 · 只读 · Truth Engine — Read Only",
        # Pre-hydration boot placeholders (3)
        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
        # Reference-packet intro (1)
        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
        # Inbox empty state (1)
        "暂无已提交提案 · No proposals submitted yet.",
        # Pending sign-off (1)
        "等待 Kogami 签字 · Pending Kogami sign-off",
    ],
)
def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"


# ─── 2. Stale English-only surfaces are gone ─────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        # Bare topbar chip labels (no Chinese prefix) — must be replaced
        "<span>Identity</span>",
        "<span>Ticket</span>",
        "<span>Feedback Mode</span>",
        "<span>System</span>",
        "<strong>Manual (advisory)</strong>",
        # WOW h3 stale English-first ordering (E11-15c convention)
        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
        # Bare state-of-world labels (no Chinese prefix)
        ">truth-engine SHA<",
        ">recent e2e<",
        ">adversarial<",
        ">open issues<",
        # Bare trust-banner body lines — these are now sentence-internal
        # so we look for the line-leading position they used to hold.
        "<em>What \"manual feedback\" means here:</em>",
        "<strong>That mode is advisory.</strong>",
        # Bare button + headline + boot placeholders
        ">\n          Hide for session\n        <",
        ">\n          Truth Engine — Read Only\n        <",
        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
        # Bare inbox + pending sign-off
        "<li>No proposals submitted yet.</li>",
        "<strong>Pending Kogami sign-off</strong>",
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only surface still present: {stale}"


# ─── 3. English suffixes preserved (substring locks unchanged) ───────


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        # Anchors required by trust_affordance.py
        "Manual (advisory)",
        "Truth engine readings",
        "Hide for session",
        'What "manual feedback" means here',
        "That mode is advisory.",
        # Anchor required by authority_banner.py
        "Truth Engine — Read Only",
        # Anchor required by role_affordance.py
        "Pending Kogami sign-off",
        # Anchor required by state_of_world_bar.py
        "advisory · not a live truth-engine reading",
        # Anchors required by column_rename.py:118-120 (pre-hydration)
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-feedback-mode"',
        'id="workbench-trust-banner"',
        'id="workbench-authority-banner"',
        'id="workbench-pending-signoff-affordance"',
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'data-trust-banner-dismiss',
        'data-feedback-mode="manual_feedback_override"',
    ],
)
def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"


# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──


def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
    switch. If the JS literal stays English-only, the very first mode
    flip would silently revert the static HTML's bilingual chip back to
    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert '"真值引擎 · Truth Engine"' in js, (
        "JS feedback-mode `truth_engine` branch must use bilingual label"
    )
    assert '"手动（仅参考）· Manual (advisory)"' in js, (
        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
    )
    # Stale English-only literals must not coexist (would imply duplicate
    # write-paths or stale residue).
    assert '"Truth Engine"' not in js, (
        'stale English-only `"Truth Engine"` literal still in workbench.js'
    )
    assert '"Manual (advisory)"' not in js, (
        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
    )


# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────


def test_workbench_route_serves_e11_15e_bundle(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # Spot-check one string from each surface category.
    assert "身份 · Identity" in html
    assert "因果链走读 · Causal Chain" in html
    assert "真值引擎 SHA · truth-engine SHA" in html
    assert "该模式仅作参考 · That mode is advisory." in html
    assert "隐藏（本次会话）· Hide for session" in html
    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html

exec
/bin/zsh -lc 'git diff main..83d69e4 -- src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index cbc80a4..157518a 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -23,11 +23,11 @@
           data-role="ENGINEER"
           data-identity-name="Kogami"
         >
-          <span>Identity</span>
+          <span>身份 · Identity</span>
           <strong>Kogami / Engineer</strong>
         </div>
         <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
-          <span>Ticket</span>
+          <span>工单 · Ticket</span>
           <strong>WB-E06-SHELL</strong>
         </div>
         <div
@@ -38,12 +38,12 @@
           aria-live="polite"
           title="Manual feedback override is advisory — truth engine readings remain authoritative."
         >
-          <span>Feedback Mode</span>
-          <strong>Manual (advisory)</strong>
+          <span>反馈模式 · Feedback Mode</span>
+          <strong>手动（仅参考）· Manual (advisory)</strong>
           <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
         </div>
         <label class="workbench-collab-system" for="workbench-system-select">
-          <span>System</span>
+          <span>系统 · System</span>
           <select id="workbench-system-select">
             <option value="thrust-reverser">Thrust Reverser</option>
             <option value="landing-gear">Landing Gear</option>
@@ -62,29 +62,29 @@
         <span class="workbench-sow-eyebrow">当前现状</span>
         <span class="workbench-sow-field" data-sow-field="truth_engine_sha"
               title="git rev-parse --short HEAD">
-          <span class="workbench-sow-label">truth-engine SHA</span>
+          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
           <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="recent_e2e"
               title="docs/coordination/qa_report.md (most recent test run)">
-          <span class="workbench-sow-label">recent e2e</span>
+          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
           <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="adversarial"
               title="docs/coordination/qa_report.md (shared validation)">
-          <span class="workbench-sow-label">adversarial</span>
+          <span class="workbench-sow-label">对抗样本 · adversarial</span>
           <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
         </span>
         <span class="workbench-sow-sep" aria-hidden="true">·</span>
         <span class="workbench-sow-field" data-sow-field="known_issues"
               title="docs/known-issues/ file count">
-          <span class="workbench-sow-label">open issues</span>
+          <span class="workbench-sow-label">未关闭问题 · open issues</span>
           <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
         </span>
         <span class="workbench-sow-flag" aria-hidden="false">
-          advisory · not a live truth-engine reading
+          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
         </span>
       </section>
 
@@ -108,7 +108,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_a</span>
-              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
+              <h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
@@ -140,7 +140,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_b</span>
-              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
+              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
@@ -170,7 +170,7 @@
           >
             <header>
               <span class="workbench-wow-tag">wow_c</span>
-              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
+              <h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
@@ -206,14 +206,14 @@
         <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
         <div class="workbench-trust-banner-body">
           <span class="workbench-trust-banner-scope">
-            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
-            an observed reading — for example, editing a snapshot input field before running a scenario.
-            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
+            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
+            (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
+            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
           </span>
-          <strong>That mode is advisory.</strong>
+          <strong>该模式仅作参考 · That mode is advisory.</strong>
           <span>
-            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
-            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
+            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
+            你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
           </span>
         </div>
         <button
@@ -222,7 +222,7 @@
           aria-label="Hide trust banner for this session"
           data-trust-banner-dismiss
         >
-          Hide for session
+          隐藏（本次会话）· Hide for session
         </button>
       </aside>
 
@@ -245,7 +245,7 @@
       >
         <span class="workbench-authority-banner-icon" aria-hidden="true">🔒</span>
         <span class="workbench-authority-banner-headline">
-          Truth Engine — Read Only
+          真值引擎 · 只读 · Truth Engine — Read Only
         </span>
         <span class="workbench-authority-banner-sep" aria-hidden="true">·</span>
         <span class="workbench-authority-banner-rule">
@@ -275,7 +275,7 @@
             <h2>探针与追踪 · Probe &amp; Trace</h2>
           </header>
           <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for probe &amp; trace panel boot.
+            等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
           </div>
           <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
             <button type="button" class="workbench-toolbar-button is-primary">加载当前工单 · Load Active Ticket</button>
@@ -295,10 +295,10 @@
             <h2>标注与提案 · Annotate &amp; Propose</h2>
           </header>
           <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for annotate &amp; propose panel boot.
+            等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
           </div>
           <div class="workbench-collab-document">
-            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
+            <p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.</p>
             <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
           </div>
         </article>
@@ -315,7 +315,7 @@
             <h2>移交与跟踪 · Hand off &amp; Track</h2>
           </header>
           <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
-            Waiting for hand off &amp; track panel boot.
+            等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
           </div>
           <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
             <span>SW1</span>
@@ -334,7 +334,7 @@
           <h2>审核队列 · Review Queue</h2>
         </header>
         <ul id="annotation-inbox-list">
-          <li>No proposals submitted yet.</li>
+          <li>暂无已提交提案 · No proposals submitted yet.</li>
         </ul>
       </aside>
 
@@ -360,7 +360,7 @@
       >
         <span class="workbench-pending-signoff-icon" aria-hidden="true">🛈</span>
         <div class="workbench-pending-signoff-body">
-          <strong>Pending Kogami sign-off</strong>
+          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
           <span>
             你的提案已加入排队，等待 Kogami 处理。Approval 操作是 Kogami 专属
             authority — 你的角色当前不会看到 disabled UI，而是这条 explicit

exec
/bin/zsh -lc 'git diff main..83d69e4 -- src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index 375e6c9..33a247a 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -3785,7 +3785,7 @@ function setFeedbackMode(mode) {
     chip.setAttribute("data-feedback-mode", mode);
     const label = chip.querySelector("strong");
     if (label) {
-      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
+      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
     }
   }
   syncTrustBannerForMode(mode);

codex
I have the E11-15e diff and tests loaded. I’m now checking the earlier E11-15c convention source and pulling exact line numbers from the current HTML/JS so the review can distinguish a real convention break from a wording nit.
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '20,380p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    20	        <div
    21	          id="workbench-identity"
    22	          class="workbench-collab-chip"
    23	          data-role="ENGINEER"
    24	          data-identity-name="Kogami"
    25	        >
    26	          <span>身份 · Identity</span>
    27	          <strong>Kogami / Engineer</strong>
    28	        </div>
    29	        <div id="workbench-ticket" class="workbench-collab-chip" data-ticket="WB-E06-SHELL">
    30	          <span>工单 · Ticket</span>
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
    41	          <span>反馈模式 · Feedback Mode</span>
    42	          <strong>手动（仅参考）· Manual (advisory)</strong>
    43	          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
    44	        </div>
    45	        <label class="workbench-collab-system" for="workbench-system-select">
    46	          <span>系统 · System</span>
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
    65	          <span class="workbench-sow-label">真值引擎 SHA · truth-engine SHA</span>
    66	          <span class="workbench-sow-value" data-sow-value="truth_engine_sha">…</span>
    67	        </span>
    68	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    69	        <span class="workbench-sow-field" data-sow-field="recent_e2e"
    70	              title="docs/coordination/qa_report.md (most recent test run)">
    71	          <span class="workbench-sow-label">最近 e2e · recent e2e</span>
    72	          <span class="workbench-sow-value" data-sow-value="recent_e2e_label">…</span>
    73	        </span>
    74	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    75	        <span class="workbench-sow-field" data-sow-field="adversarial"
    76	              title="docs/coordination/qa_report.md (shared validation)">
    77	          <span class="workbench-sow-label">对抗样本 · adversarial</span>
    78	          <span class="workbench-sow-value" data-sow-value="adversarial_label">…</span>
    79	        </span>
    80	        <span class="workbench-sow-sep" aria-hidden="true">·</span>
    81	        <span class="workbench-sow-field" data-sow-field="known_issues"
    82	              title="docs/known-issues/ file count">
    83	          <span class="workbench-sow-label">未关闭问题 · open issues</span>
    84	          <span class="workbench-sow-value" data-sow-value="open_known_issues_count">…</span>
    85	        </span>
    86	        <span class="workbench-sow-flag" aria-hidden="false">
    87	          仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading
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
   111	              <h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>
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
   143	              <h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>
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
   173	              <h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>
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
   209	            <em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入用来覆盖某个观测读数的任何值——例如在运行一个场景前编辑快照输入字段
   210	            (any value you type into the workbench to override an observed reading — for example, editing a snapshot input field before running a scenario).
   211	            被动读取、回放与审计链导航不算 manual feedback (Passive reads, replays, and audit-chain navigation do NOT count as manual feedback).
   212	          </span>
   213	          <strong>该模式仅作参考 · That mode is advisory.</strong>
   214	          <span>
   215	            真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   216	            你的手动反馈会被记录用于 diff / review，但不改写真值 · Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   217	          </span>
   218	        </div>
   219	        <button
   220	          type="button"
   221	          class="workbench-trust-banner-dismiss"
   222	          aria-label="Hide trust banner for this session"
   223	          data-trust-banner-dismiss
   224	        >
   225	          隐藏（本次会话）· Hide for session
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
   248	          真值引擎 · 只读 · Truth Engine — Read Only
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
   278	            等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.
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
   298	            等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.
   299	          </div>
   300	          <div class="workbench-collab-document">
   301	            <p>参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes, and future text-range annotations will land here.</p>
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
   318	            等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.
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
   337	          <li>暂无已提交提案 · No proposals submitted yet.</li>
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
   363	          <strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>
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

exec
/bin/zsh -lc 'rg -n "E11-15c|Chinese-first|direction" .planning/phases/E11-workbench-engineer-first-ux tests src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_workbench_column_rename.py:64:        # E11-15c flipped to Chinese-first to match the rest of the page;
tests/test_workbench_column_rename.py:231:    # E11-15c flipped these from English-first to Chinese-first.
tests/test_workbench_approval_flow_polish.py:8:This is one slice in a multi-sub-phase Chinese-first thread; it does
tests/test_workbench_approval_flow_polish.py:9:NOT finish the workbench Chinese-first work. P2 R2 IMPORTANT closure:
tests/test_workbench_approval_flow_polish.py:189:    `uniformly Chinese-first`. P2 verified `/workbench` still has many
tests/test_workbench_approval_flow_polish.py:214:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:6:> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:78:## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:80:E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:83:- E11-15c: 3 column h2s + page eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:103:  因果链走读` etc. are English-first; same direction-flip pattern as
.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:104:  E11-15c column h2s could apply.
tests/test_workbench_e11_15e_chinese_first_bundle.py:1:"""E11-15e — Tier-A Chinese-first bundle regression lock.
tests/test_workbench_e11_15e_chinese_first_bundle.py:9:  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
tests/test_workbench_e11_15e_chinese_first_bundle.py:95:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
tests/test_workbench_e11_15e_chinese_first_bundle.py:142:        # WOW h3 stale English-first ordering (E11-15c convention)
tests/test_metadata_registry_consistency.py:1:"""P42-05 · Bidirectional registry ↔ runtime ↔ markdown consistency guard.
tests/test_metadata_registry_consistency.py:53:# yaml and acts as a reverse-direction check (any module added here but not
tests/test_metadata_registry_consistency.py:135:class YamlRuntimeBidirectionalTests(unittest.TestCase):
tests/test_workbench_chinese_eyebrow_sweep.py:1:"""E11-15 — Chinese-first eyebrow sweep.
tests/test_workbench_chinese_eyebrow_sweep.py:5:reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
tests/test_workbench_chinese_eyebrow_sweep.py:8:each already provides Chinese-first signal.
tests/test_workbench_chinese_eyebrow_sweep.py:60:        # E11-15c: page eyebrow changed from `控制逻辑工作台` (which
tests/test_workbench_chinese_eyebrow_sweep.py:72:    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
tests/test_workbench_chinese_eyebrow_sweep.py:121:        # h1 main title is bilingualized by E11-15b (Chinese-first); the
tests/test_workbench_chinese_eyebrow_sweep.py:146:    # E11-15c: page eyebrow flipped to `工程师工作区`; the literal
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:1:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:44:| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45:| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:46:| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:83:| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:113:| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:115:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:131:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-prompt.txt:45:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:6:> affordance JS toggle), E11-13 (bundle/shell sentinel), and E11-15c
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:7:> (Chinese-first DOM render). The new e2e infra immediately surfaced a
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:66:> successor of E11-15c's P4 AND content-fit: P5 reviews end-user-facing
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:84:E11-15c closure (2 tests):
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md:86:- Real-DOM control-panel + approval entry buttons render Chinese-first text.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:127:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:623:   flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:691:+  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:1780:   405	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:276:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:800:  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:898:  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:108:E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:166:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:170:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:753:  flex-direction: column;
tests/test_workbench_chinese_direction_consistency.py:1:"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
tests/test_workbench_chinese_direction_consistency.py:8:    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
tests/test_workbench_chinese_direction_consistency.py:11:NIT #2 — direction asymmetry
tests/test_workbench_chinese_direction_consistency.py:13:    while the rest of the page is Chinese-first. E11-15c flips them
tests/test_workbench_chinese_direction_consistency.py:14:    to `<中文> · <English>` for full-page direction consistency.
tests/test_workbench_chinese_direction_consistency.py:62:# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
tests/test_workbench_chinese_direction_consistency.py:75:    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
tests/test_workbench_chinese_direction_consistency.py:103:    """E11-15b's h1 bilingualization must survive E11-15c — only the
tests/test_workbench_chinese_direction_consistency.py:142:        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
tests/test_workbench_chinese_direction_consistency.py:146:# ─── 4. Live-served route reflects E11-15c ───────────────────────────
tests/test_workbench_chinese_direction_consistency.py:149:def test_workbench_route_reflects_direction_flip(server) -> None:
tests/test_workbench_chinese_direction_consistency.py:166:    P4 IMPORTANT closure (E11-15c review): every backend / JS / CSS /
tests/test_workbench_chinese_direction_consistency.py:198:                f"E11-15c string {new_string!r} unexpectedly leaked into "
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:44:E11-15c closure (2 tests): real-DOM headers + buttons all render Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:338:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:376:060f698 (origin/main, origin/HEAD, main) docs(E11-15c): bump coordination evidence — PR #26 merged with P4 APPROVE_WITH_NITS
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:377:393bccf phase(E11-15c): closure of P3 NITs — column h2 dir flip + h1/eyebrow dedup (#26)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:379:92af49a phase(E11-15b): Chinese-first iter 2 — h1/h2/buttons/caption bilingualized (#25)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:492:+- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:638:+# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:644:+    Chinese-first across every header surface."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:663:+    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:665:+    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2178:tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_every_runtime_instance_has_a_yaml_entry
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2179:tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_every_yaml_entry_has_a_runtime_instance
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2180:tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_yaml_modules_match_known_runtime_modules
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2428:tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u63a2\u9488\u4e0e\u8ffd\u8e2a \xb7 Probe &amp; Trace</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2429:tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u6807\u6ce8\u4e0e\u63d0\u6848 \xb7 Annotate &amp; Propose</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2430:tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u79fb\u4ea4\u4e0e\u8ddf\u8e2a \xb7 Hand off &amp; Track</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2431:tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Probe &amp; Trace \xb7 \u63a2\u9488\u4e0e\u8ffd\u8e2a</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2432:tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Annotate &amp; Propose \xb7 \u6807\u6ce8\u4e0e\u63d0\u6848</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2433:tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Hand off &amp; Track \xb7 \u79fb\u4ea4\u4e0e\u8ddf\u8e2a</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2434:tests/test_workbench_chinese_direction_consistency.py::test_page_eyebrow_is_engineer_workspace_not_h1_duplicate
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2435:tests/test_workbench_chinese_direction_consistency.py::test_h1_still_carries_full_bilingual_title
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2436:tests/test_workbench_chinese_direction_consistency.py::test_eyebrow_and_h1_are_not_chinese_duplicates
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2437:tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Probe &amp; Trace</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2438:tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Annotate &amp; Propose</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2439:tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Hand off &amp; Track</h2>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2440:tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Control Logic Workbench</h1>]
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2441:tests/test_workbench_chinese_direction_consistency.py::test_workbench_route_reflects_direction_flip
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:2442:tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_only_touches_static_html_and_tests
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3503:     7	- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3649:   153	# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3655:   159	    Chinese-first across every header surface."""
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3674:   178	    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md:3676:   180	    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:11:Across E11-08, E11-15, E11-15b, E11-15c, and E11-11, the per-sub-phase
.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md:134:   E11-15c PERSONA-ROTATION-STATE.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:3:# Context — E11-15 Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:12:5 eyebrow labels above non-bilingual h1/h2s flipped from English-lowercase to pure Chinese so the page reads Chinese-first at a glance:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:22:The 3 column-trio eyebrows (`probe & trace` / `annotate & propose` / `hand off & track`) are intentionally preserved — they live above bilingual h2 titles which already provide Chinese-first signal at the h2 line, and they are positively locked by `tests/test_workbench_column_rename.py`. E11-15 explicitly does NOT touch them.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-prompt.txt:34:- **Visible-copy consistency**: do the 5 new Chinese strings work harmoniously with their surrounding h1/h2/body copy? Is the page a coherent Chinese-first read, or does any eyebrow read awkwardly against its neighbors?
tests/test_workbench_chinese_h2_button_sweep.py:1:"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
tests/e2e/test_workbench_js_boot_smoke.py:7:- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
tests/e2e/test_workbench_js_boot_smoke.py:160:# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
tests/e2e/test_workbench_js_boot_smoke.py:166:    Chinese-first across every header surface."""
tests/e2e/test_workbench_js_boot_smoke.py:185:    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
tests/e2e/test_workbench_js_boot_smoke.py:187:    # column h2s: Chinese-first per E11-15c
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:121:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1591:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1700:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1821:   270	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1960:   409	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:2244:   689	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:2931:  1870	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:2944:  1883	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:2949:  1888	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:2962:  1901	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:21:4. **WOW h3 direction-flip impact on click-flow**
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:22:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-prompt.txt:25:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R3-output.md:60:- **Did R3 actually close R2 IMPORTANT?** Re-grep `last English-only surface` and `uniformly Chinese-first` across SURFACE-INVENTORY + PERSONA-ROTATION-STATE + tests/test_workbench_approval_flow_polish.py:
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r2-output.md:333:   285	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r2-output.md:444:   138	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:18:# Context — E11-15 Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:27:5 eyebrow labels above non-bilingual h1/h2s flipped from English-lowercase to pure Chinese so the page reads Chinese-first at a glance:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:37:The 3 column-trio eyebrows (`probe & trace` / `annotate & propose` / `hand off & track`) are intentionally preserved — they live above bilingual h2 titles which already provide Chinese-first signal at the h2 line, and they are positively locked by `tests/test_workbench_column_rename.py`. E11-15 explicitly does NOT touch them.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:49:- **Visible-copy consistency**: do the 5 new Chinese strings work harmoniously with their surrounding h1/h2/body copy? Is the page a coherent Chinese-first read, or does any eyebrow read awkwardly against its neighbors?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:309:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:350:"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:354:reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:357:each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:418:    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1167:     1	"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1171:     5	reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1174:     8	each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1235:    69	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1737:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1747:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1754:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1772:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:1843:+E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:121:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1130:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1239:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1360:   270	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1499:   409	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1779:   689	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:2960:  1870	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:2973:  1883	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:2978:  1888	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:2991:  1901	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-04-output.md:129:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:1:# E11-15 Surface Inventory — Chinese-first eyebrow sweep
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:11:provides Chinese-first signal at the h2 line and is intentionally
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:18:reads Chinese-first across every section header. The h1/h2 strings
.planning/phases/E11-workbench-engineer-first-ux/E11-15-SURFACE-INVENTORY.md:36:  already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:131:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:387:   308	    p_dispatch.add_argument("sub_phase", help="e.g. E11-15c")
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1024:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1026:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1087:376:060f698 (origin/main, origin/HEAD, main) docs(E11-15c): bump coordination evidence — PR #26 merged with P4 APPROVE_WITH_NITS
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-output.md:1088:377:393bccf phase(E11-15c): closure of P3 NITs — column h2 dir flip + h1/eyebrow dedup (#26)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-prompt.txt:29:E11-15c closure (2 tests): real-DOM headers + buttons all render Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r3-output.md:91:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:1:# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/E11-15b-SURFACE-INVENTORY.md:8:> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:516:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:676:   flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:785:+  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:906:   flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2740:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2849:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2970:   270	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:3109:   409	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:3397:   689	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:4080:  1870	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:4093:  1883	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:4098:  1888	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:4111:  1901	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:1:# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:13:| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:27:  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:33:- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:57:`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:59:1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:74:- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md:75:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:27:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:48:- **Visible-copy consistency**: do the 6 new bilingual approval-flow strings work harmoniously with the surrounding E11-15b approval-center surface (`Kogami 提案审批 · Kogami Proposal Triage` h2, `审批中心 · Approval Center` entry button, `审批操作仅限 Kogami · ...` caption)? Does the page now read uniformly as a Chinese-first FCS engineer's approval workflow?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:53:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:67:- **Column-trio eyebrows** — locked by E11-03; bilingual h2 already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:320:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1021:I’ve reached the closure-claim pass. There is already a possible gap outside the approval-center slice: `workbench.html` still appears to have at least one unrelated English-only button label, so I’m verifying that directly with the exact grep pattern and then live-probing `/workbench` through the server to separate “approval-flow done” from “entire page fully Chinese-first.”
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1541:    76	With E11-15d, the entire `/workbench` UI is uniformly Chinese-first:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1544:    79	- E11-15c: 3 column h2s + page eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1572:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1574:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1577:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1 (derived programmatically by next-persona tool). Closes the last English-only surface in the workbench demo (3 approval lane h3s + 2 lane buttons + 1 pending-lane body copy). 6 [REWRITE], <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency works for this final approval-flow surface. With this sub-phase, /workbench is uniformly Chinese-first — only backend API remediation message in demo_server.py:743 stays English (backend contract).)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1828:I’ve got enough to separate the copy slice from the stronger marketing claim. I’m running the existing approval-center contract test alongside the new polish tests once, so the final verdict can distinguish “this diff is mechanically safe” from “the page-wide Chinese-first closure claim is still not true.”
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1900:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1901:- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1915:- IMPORTANT `src/well_harness/static/workbench.html:225`, `src/well_harness/static/workbench.html:248`, `src/well_harness/static/workbench.html:337`, `src/well_harness/static/workbench.html:363`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:5-6`, `.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:76-84`, `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so “last English-only surface” and “uniformly Chinese-first” are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:1916:- IMPORTANT `tests/test_workbench_approval_flow_polish.py:1-15`, `tests/test_workbench_approval_flow_polish.py:61-169`, `src/well_harness/static/workbench.html:111`, `src/well_harness/static/workbench.html:143`, `src/well_harness/static/workbench.html:173`, `src/well_harness/static/workbench.html:219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:509:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R3-output.md:1215:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2965:tokens used
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:142:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md:121:**E11 path**: E11-03 (column rename to verb-based Chinese-first labels) + E11-04 (annotation vocabulary domain-anchoring) + new E11-15 (sweep all UI strings to Chinese-first with English in muted sublabels).
.planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md:179:| **E11-15** (new) | queued | full UI string sweep — Chinese-first with English muted sublabels |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:308:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:43:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:121:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-output.md:23:   Suggested mitigation (presentation-friendly): Chinese-first labels on the primary surface; keep English only in muted sublabels.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:142:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:285:   899	- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:1574:- NIT — [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:250), [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:255), [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:90): `Hand off & Track · 移交与跟踪` is directionally right, but this lane still visually reads as a logic-circuit/overlay surface (`SW1`, `Logic 1-4`, `THR LOCK`, “Overlay annotation arrives in E07”). In a real demo it still works, but the presenter will need one bridging sentence so the title does not promise a fuller handoff-tracking surface than the current skeleton shows.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:1589:- NIT — [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:250), [src/well_harness/static/workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:255), [src/well_harness/static/workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:90): `Hand off & Track · 移交与跟踪` is directionally right, but this lane still visually reads as a logic-circuit/overlay surface (`SW1`, `Logic 1-4`, `THR LOCK`, “Overlay annotation arrives in E07”). In a real demo it still works, but the presenter will need one bridging sentence so the title does not promise a fuller handoff-tracking surface than the current skeleton shows.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-prompt.txt:28:   - Same audit for the boot status placeholders: static HTML serves `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` then JS replaces it with the existing `Probe & Trace ready. Scenario actions are staged for the next bundle.` (still English-only — out-of-scope per SURFACE-INVENTORY Section 3). Is that English-only post-hydration string a contradiction with the Chinese-first commitment, or correctly deferred?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:317:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1543:   689	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1936:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:2045:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:2166:   270	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:2305:   409	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3254:  1870	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3267:  1883	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3272:  1888	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:3285:  1901	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8531:+  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:9693:   899	- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:5:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:15:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-prompt.txt:16:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:18:# Context — E11-15b Chinese-first iter 2 (h1/h2/buttons/caption)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:51:- **First-glance demo impression**: open `/workbench` cold — does the page now read Chinese-first across header, control buttons, annotation inbox, and approval center? Or is there still residual English-first surface that defeats the goal?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:53:- **Bilingual delimiter consistency**: every flip uses ` · ` (space-middot-space). Is this consistent with the rest of the codebase's bilingual pattern (e.g., column h2s `Probe & Trace · 探针与追踪`)? Note the column h2s use English-first; the new sweep uses Chinese-first. Is this asymmetry acceptable for demo flow, or does it look inconsistent at a glance?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:67:- **Reverse direction**: column h2s currently use English-first (`Probe & Trace · 探针与追踪`); could be flipped to Chinese-first in a future sweep for delimiter symmetry.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:191:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:637:+# E11-15b Surface Inventory — Chinese-first h2/button/caption sweep (iter 2)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:644:+> uniformly Chinese-first while preserving English suffixes for existing
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:730: E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:796:+        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:809:+"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1428:     1	"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1726:- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1741:- `NIT` [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:275): the new sweep is Chinese-first in the hero/review/approval surfaces, but the three main column h2s at lines 275, 295, and 315 are still English-first while the new headings at lines 334 and 380 are Chinese-first. That direction flip is now the most visible remaining polish gap, even though it is correctly treated as deferred scope.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-output.md:93:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:30:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:32:> **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1-15, 61-169`, `workbench.html:111, 143, 173, 219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:41:- Header banner now states this is "NOT the final Chinese-first sweep" and explicitly references the P2 R1 IMPORTANT.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:42:- Replaced "Closure summary" section with "Workbench Chinese-first thread progress (NOT closure)" + new explicit "English-only surfaces still remaining" section listing the 4 strings you found (with their existing test-lock locations) + WOW starter h3s + topbar chip labels. Deferred to future E11-15e Tier-A bundle.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:44:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:48:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:61:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:63:- **Is the guard test sufficient?** It only catches reintroduction of those 2 specific phrases. Other overclaim phrasings (e.g., "the entire workbench Chinese-first work is done", "no English remains") would slip past. Acceptable trade-off for narrow IMPORTANT closure, OR should the guard be broader?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:262:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:395:     6	> body copy (6 strings). Note: this is NOT the final Chinese-first
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:399:    10	> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:467:    78	## Workbench Chinese-first thread progress (NOT closure)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:469:    80	E11-15d is one slice in a multi-sub-phase Chinese-first thread:
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:472:    83	- E11-15c: 3 column h2s + page eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:489:   100	  因果链走读` etc. are English-first; same direction-flip pattern as
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:490:   101	  E11-15c column h2s could apply.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:498:   109	/ inbox-placeholder / affordance-strong / WOW-h3-direction strings as
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:679:   178	    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:696:   195	        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:730:    19	E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:732:    21	E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:735:    24	E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1108:/bin/zsh -lc 'rg -n "last English-only surface|uniformly Chinese-first" .planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md tests/test_workbench_approval_flow_polish.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1111:tests/test_workbench_approval_flow_polish.py:178:    claimed `last English-only surface` and `uniformly Chinese-first`,
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1113:tests/test_workbench_approval_flow_polish.py:195:        "uniformly Chinese-first",
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1115:.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:10:> and "uniformly Chinese-first" — corrected.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1507:print('uniformly Chinese-first' in text)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1685:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1709:- **INFO** — [E11-15d-SURFACE-INVENTORY.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15d-SURFACE-INVENTORY.md:3), [PERSONA-ROTATION-STATE.md](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24): the specific forbidden phrases are cleaned out of the planning docs as requested. `last English-only surface` and `uniformly Chinese-first` only remain inside the leading corrective blockquote of the surface inventory; they do not appear in the live body of either planning doc.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:1:You are Codex GPT-5.4 acting as **Persona P4 — V&V Engineer** (Tier-B single-persona pipeline, E11-15c sub-phase).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:3:# Context — E11-15c closure of P3 NITs
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:10:## What E11-15c ships
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:17:| `workbench.html:275` | h2 `Probe & Trace · 探针与追踪` | `探针与追踪 · Probe & Trace` | NIT #2 (direction asymmetry) |
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:24:- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated (param values + live-route check) for new Chinese-first column h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:26:- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:27:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:35:- **Contract migration completeness**: For every test we updated in lockstep with HTML, verify the new assertion is at least as strong as the old one. (E.g., E11-03 locked the EXACT bilingual h2 string; we changed direction — is the new assertion still locking the exact full string?)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:45:- 1078 / 1078 pytest pass (15 new in `test_workbench_chinese_direction_consistency.py`; full suite green)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt:64:Sign as: **P4 — V&V Engineer (Tier-B, E11-15c)**
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:12:Closes the LAST English-only surface in the workbench demo. With this sub-phase, `/workbench` is uniformly Chinese-first; only the backend API remediation message in `demo_server.py:743` stays English (backend contract, locked by `tests/test_lever_snapshot_manual_override_guard.py:151`).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:33:- **Visible-copy consistency**: do the 6 new bilingual approval-flow strings work harmoniously with the surrounding E11-15b approval-center surface (`Kogami 提案审批 · Kogami Proposal Triage` h2, `审批中心 · Approval Center` entry button, `审批操作仅限 Kogami · ...` caption)? Does the page now read uniformly as a Chinese-first FCS engineer's approval workflow?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:38:- **Closure claim verification**: I claim `/workbench` is now uniformly Chinese-first. Verify by `grep -nE ">[A-Za-z][^<]*</h[1-3]>|>[A-Za-z][^<]*</button>"` on `workbench.html` to confirm no remaining English-only h1/h2/h3/button content. Acceptable exceptions: identifier strings in topbar chips (`Identity`, `Ticket`, `System`, `Feedback Mode`), system option labels (`Thrust Reverser`, etc.) which are domain proper-nouns, and the `eyebrow` decorative labels in the column trio (locked by E11-03 tests).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-prompt.txt:52:- **Column-trio eyebrows** — locked by E11-03; bilingual h2 already gives Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:19:E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:21:E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:24:E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md:25:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-output.md:323:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:36:4. **WOW h3 direction-flip impact on click-flow**
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:37:   - The WOW starter cards' h3 changed from English-first to Chinese-first ordering. Does this affect screen-reader announcement order for the `aria-labelledby` linkage (workbench-wow-a-title etc.)? The h3 is the labelled-by target — the rest of the card description still starts with the API endpoint string.
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:40:   - The new `等待 Kogami 签字 · Pending Kogami sign-off` is followed by an existing Chinese-first body span: `你的提案已加入排队，等待 Kogami 处理...`. Does the doubled "等待 Kogami" reading (header + body) feel redundant, or is it OK reinforcement?
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:323:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:93:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:20:You ran the E11-15d Tier-B review across 3 rounds (R1, R2, R3) and were the persona who flagged the doc-honesty `last English-only surface` / `uniformly Chinese-first` overclaim. Your enumeration of remaining English-only surfaces in E11-15d's R2 review is what E11-15e set out to close.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:30:   E11-15e's PR body and SURFACE-INVENTORY both repeatedly say it "closes 22 surfaces" and explicitly disclaim "the last" / "all" / "uniformly Chinese-first". Re-grep the new artifacts (PR body, SURFACE-INVENTORY, new test file `test_workbench_e11_15e_chinese_first_bundle.py`):
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:31:   - Any forbidden overclaim phrases (`last English-only surface` / `uniformly Chinese-first` / `all English surfaces` / equivalents) that drifted in?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:140:E11-15: Tier-B (5 copy_diff_lines, 5 [REWRITE] — fails ≥10 copy_diff threshold; though all 5 are [REWRITE]). Persona = P2 (Senior FCS Engineer — round-robin successor of P1; content-fit for visible-copy consistency + structural-anchor preservation review). The 3 E11-03 column-trio eyebrows are explicitly out-of-scope (positively locked by test_workbench_column_rename + bilingual h2 already provides Chinese-first signal).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:142:E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:145:E11-15d: Tier-B (Persona = P2 — Senior FCS Engineer — round-robin successor of E11-10's P1, derived programmatically by next-persona tool. Bilingualizes the Approval Center lane labels: 3 h3s + 2 lane buttons + 1 pending-lane body copy = 6 [REWRITE]; <10 copy_diff → Tier-B. Persona-content fit: P2's lens on visible-copy consistency for the approval-flow surface. P2 R1 IMPORTANT closure: removed earlier overclaim that this sub-phase finished the workbench Chinese-first thread. Surfaces still English-only after E11-15d: `Hide for session` (trust banner dismiss), `Truth Engine — Read Only` (authority headline), `No proposals submitted yet.` (inbox placeholder), `Pending Kogami sign-off` (affordance strong text), and WOW starter card h3s — deferred to follow-up E11-15e.)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:146:E11-15e: Tier-A (Persona = P3 — Tier-A Chinese-first bundle: 22 REWRITE rows across topbar chips + WOW h3 direction flips + state-of-world labels + trust-banner body + authority banner + boot placeholders + reference-packet block + inbox empty state + pending sign-off; English suffixes preserved; new lockstep test (67 cases); zero regressions on 1221-test full suite; closes 22 of P2's enumerated English-only surfaces (out-of-scope deferred surfaces explicitly listed in SURFACE-INVENTORY Section 3)). All 5 personas dispatched. Rotation pointer unchanged.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:149:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:192:| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:193:| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:194:| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:231:| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:261:| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:263:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:279:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:292:/bin/zsh -lc 'pwd && git rev-parse --short HEAD && git status --short && rg -n "E11-15e|E11-15d|LogicMVP|persona|surface-inventory|uniformly Chinese-first|last English-only surface" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:338:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:16:You are Codex GPT-5.4 acting as **Persona P4 — V&V Engineer** (Tier-B single-persona pipeline, E11-15c sub-phase).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:18:# Context — E11-15c closure of P3 NITs
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:25:## What E11-15c ships
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:32:| `workbench.html:275` | h2 `Probe & Trace · 探针与追踪` | `探针与追踪 · Probe & Trace` | NIT #2 (direction asymmetry) |
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:39:- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated (param values + live-route check) for new Chinese-first column h2 strings
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:41:- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:42:- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:50:- **Contract migration completeness**: For every test we updated in lockstep with HTML, verify the new assertion is at least as strong as the old one. (E.g., E11-03 locked the EXACT bilingual h2 string; we changed direction — is the new assertion still locking the exact full string?)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:60:- 1078 / 1078 pytest pass (15 new in `test_workbench_chinese_direction_consistency.py`; full suite green)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:79:Sign as: **P4 — V&V Engineer (Tier-B, E11-15c)**
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:83:/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|E11-15|workbench|eyebrow|direction consistency" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:129:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:196:?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:197:?? .planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:595:.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:598:tests/test_workbench_chinese_direction_consistency.py
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:603:/bin/zsh -lc "git diff --stat main..938a5a2 && printf '\\n---\\n' && git diff --unified=0 main..938a5a2 -- src/well_harness/static/workbench.html tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_direction_consistency.py .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:605: .../E11-15c-SURFACE-INVENTORY.md                   |  80 +++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:608: ...test_workbench_chinese_direction_consistency.py | 184 +++++++++++++++++++++
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:614:diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:618:+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:620:+# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:632:+| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:646:+  to expect Chinese-first column h2s (param values + live-route check).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:652:+- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:676:+`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:678:+1. 3 column h2s positively asserted Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:693:+- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:694:+- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:705:+E11-15c: Tier-B (4 copy_diff_lines, 4 [REWRITE] — fails ≥10 copy_diff threshold). Persona = P4 (V&V Engineer — round-robin successor of P3 AND content-fit: this sub-phase rewrites existing test contracts in lockstep with HTML changes, so V&V invariant-preservation lens is exactly right). Direct closure of P3's 2 NITs from E11-15b: (a) page eyebrow `控制逻辑工作台` → `工程师工作区` to break duplication with h1; (b) 3 column h2s flipped from English-first to Chinese-first for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:722:diff --git a/tests/test_workbench_chinese_direction_consistency.py b/tests/test_workbench_chinese_direction_consistency.py
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:726:+++ b/tests/test_workbench_chinese_direction_consistency.py
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:728:+"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:735:+    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:738:+NIT #2 — direction asymmetry
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:740:+    while the rest of the page is Chinese-first. E11-15c flips them
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:741:+    to `<中文> · <English>` for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:789:+# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:802:+    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:830:+    """E11-15b's h1 bilingualization must survive E11-15c — only the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:869:+        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:873:+# ─── 4. Live-served route reflects E11-15c ───────────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:876:+def test_workbench_route_reflects_direction_flip(server) -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:904:+                f"E11-15c string {new_string!r} unexpectedly leaked into {f.name}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:918:+        # E11-15c: page eyebrow changed from `控制逻辑工作台` (which
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:923:+    # E11-15c: page eyebrow flipped to `工程师工作区`; the literal
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:939:+        # E11-15c flipped to Chinese-first to match the rest of the page;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:949:+    # E11-15c flipped these from English-first to Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1022:    64	        # E11-15c flipped to Chinese-first to match the rest of the page;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1189:   231	    # E11-15c flipped these from English-first to Chinese-first.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1202:     1	"""E11-15 — Chinese-first eyebrow sweep.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1206:     5	reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1209:     8	each already provides Chinese-first signal.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1261:    60	        # E11-15c: page eyebrow changed from `控制逻辑工作台` (which
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1273:    72	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1322:   121	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1347:   146	    # E11-15c: page eyebrow flipped to `工程师工作区`; the literal
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:1550:     1	"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2013:/bin/zsh -lc 'pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2209:/bin/zsh -lc "nl -ba tests/test_workbench_chinese_direction_consistency.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2236:     1	"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2243:     8	    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2246:    11	NIT #2 — direction asymmetry
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2248:    13	    while the rest of the page is Chinese-first. E11-15c flips them
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2249:    14	    to `<中文> · <English>` for full-page direction consistency.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2297:    62	# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2310:    75	    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2338:   103	    """E11-15b's h1 bilingualization must survive E11-15c — only the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2377:   142	        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2381:   146	# ─── 4. Live-served route reflects E11-15c ───────────────────────────
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2384:   149	def test_workbench_route_reflects_direction_flip(server) -> None:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2412:   177	                f"E11-15c string {new_string!r} unexpectedly leaked into {f.name}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2446:    69	    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2495:   118	        # h1 main title is bilingualized by E11-15b (Chinese-first); the
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2951:- `IMPORTANT` [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:161) / [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:182): the new truth-engine isolation test over-claims its coverage. The docstring says adapters, JS, and CSS are covered, but the implementation only scans `demo_server.py`/`controller.py`/`runner.py`/`models.py`, and the JS/CSS loop only asserts absence of `工程师工作区`. A future leak of `探针与追踪 · Probe` into `workbench.js` or `workbench.css` would not fail this test, and `src/well_harness/adapters/` is not checked at all. I independently grepped those paths and found no current leak, so this is a guard-strength gap, not a current product defect.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2957:- Contract migration strength is preserved. [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:68) adds exact full-tag locks for all three flipped h2s, and [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:107) preserves the exact bilingual h1. The eyebrow dedup invariant at [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:110) fails closed on markup drift; it is not silently bypassed by missing anchors.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2961:- Cross-contract compatibility spot-check passed. `pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py tests/test_workbench_dual_route.py tests/test_workbench_shell.py` completed `126 passed`. I did not rerun the full `1078`-test suite.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2963:P4 — V&V Engineer (Tier-B, E11-15c)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2973:- `IMPORTANT` [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:161) / [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:182): the new truth-engine isolation test over-claims its coverage. The docstring says adapters, JS, and CSS are covered, but the implementation only scans `demo_server.py`/`controller.py`/`runner.py`/`models.py`, and the JS/CSS loop only asserts absence of `工程师工作区`. A future leak of `探针与追踪 · Probe` into `workbench.js` or `workbench.css` would not fail this test, and `src/well_harness/adapters/` is not checked at all. I independently grepped those paths and found no current leak, so this is a guard-strength gap, not a current product defect.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2979:- Contract migration strength is preserved. [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:68) adds exact full-tag locks for all three flipped h2s, and [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:107) preserves the exact bilingual h1. The eyebrow dedup invariant at [tests/test_workbench_chinese_direction_consistency.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:110) fails closed on markup drift; it is not silently bypassed by missing anchors.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2983:- Cross-contract compatibility spot-check passed. `pytest -q tests/test_workbench_chinese_direction_consistency.py tests/test_workbench_column_rename.py tests/test_workbench_chinese_eyebrow_sweep.py tests/test_workbench_chinese_h2_button_sweep.py tests/test_workbench_role_affordance.py tests/test_workbench_dual_route.py tests/test_workbench_shell.py` completed `126 passed`. I did not rerun the full `1078`-test suite.
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:2985:P4 — V&V Engineer (Tier-B, E11-15c)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:141:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:1074:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:1183:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:1304:   270	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:1449:   409	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:2035:   689	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:2928:  1870	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:2941:  1883	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:2946:  1888	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:2959:  1901	    flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:9:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:10:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:11:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:12:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:31:4. **WOW h3 direction-flip correctness**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:32:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-prompt.txt:33:   - Do the WOW card descriptions (under each h3) need any adjustment to match the new title direction?
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:342:819:- when accepted, the user wanted one concrete next step rather than options -> end this repo’s review/acceptance slices with a single next named direction [Task 1][Task 4]
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:364:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1195:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-10-R2-output.md:1631:   405	    p_dispatch.add_argument("sub_phase", help="e.g. E11-15c")
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:111:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:372:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:546:   214	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:2392:    39	The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:2398:    45	1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:2502:   149	- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:2516:   163	4. **Executor does not self-select next Phase direction.** When a Phase closes, Executor awaits Kogami's next directive. If Executor has a recommendation, it must be offered as an `AskUserQuestion` with ≥2 options, not acted on unilaterally.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:2527:   174	Body covers: direction source · scope · Kogami Gate references · Exit artefact links · Red-line compliance checklist.
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:4484:   337	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md:205:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:131:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:846:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1020:   214	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:127:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:875:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:2493:    40	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:2602:   149	  flex-direction: column;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:233:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3175:    35	body{background:var(--bg0);color:var(--text0);font-family:var(--ui);font-size:12px;display:flex;flex-direction:column;padding-top:var(--nav-h)}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3209:    69	.panel{background:var(--bg1);overflow-y:auto;display:flex;flex-direction:column}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3211:    71	.sec{border-bottom:1px solid var(--b0);padding:10px 12px;display:flex;flex-direction:column;gap:7px}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3239:    99	  display:flex;flex-direction:column;gap:4px;transition:all .2s;
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3249:   109	.cmd-grid{display:flex;flex-direction:column;gap:4px;padding:6px 12px 12px}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3261:   121	.gauge{display:flex;flex-direction:column;align-items:center;gap:4px}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3265:   125	.log-wrap{flex:1;overflow:hidden;display:flex;flex-direction:column;padding:0 12px 10px}
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md:3293:   153	.tsc-drawer-inner{padding:8px 12px 10px;display:flex;flex-direction:column;gap:6px}
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-03-r2-output.md:93:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:24:1. **Convention adherence — Chinese-first ordering**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:25:   - E11-15c established Chinese-first column h2 ordering. Are E11-15e's WOW h3 direction flips (`因果链走读 · Causal Chain` / `1000-trial 可靠性 · Monte Carlo` / `反向诊断 · Reverse Diagnose`) consistent with E11-15c?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:26:   - Are all 22 REWRITE strings Chinese-first (Chinese before middle dot)?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:27:   - Is `1000-trial 可靠性 · Monte Carlo` actually "Chinese-first" given the leading "1000-trial" English token? Should it be re-ordered as `可靠性 1000-trial · Monte Carlo` or `1000 次试验可靠性 · Monte Carlo` for stricter convention adherence?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:46:4. **WOW h3 direction-flip correctness**
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:47:   - E11-15c flipped column h2s from English-first to Chinese-first. E11-15e flips WOW h3s the same way. But the WOW h3s previously had a different convention — original was English-first. Verify the flip is consistent with the **page-wide direction convention**, not breaking some special case.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:48:   - Do the WOW card descriptions (under each h3) need any adjustment to match the new title direction?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:200:/bin/zsh -lc 'rg -n "E11-15e|LogicMVP|bilingual|Chinese-first|workbench" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:246:950:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:363:# E11-15e — Tier-A Chinese-first bundle SURFACE INVENTORY
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:406:| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:407:| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:408:| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:445:| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:475:| `test_workbench_chinese_direction_consistency.py` | ✅ no change | E11-15c column h2 invariant unaffected (no h2 changes). |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:477:| `test_workbench_approval_flow_polish.py` | ✅ no change | E11-15d guard (Section 7) checks for forbidden overclaim phrases; this surface inventory honors that contract by explicitly **not** claiming "last" or "uniformly Chinese-first". |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:493:| P3 (lead) | Bilingual copy quality + Chinese-first ordering convention adherence |
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:508:"""E11-15e — Tier-A Chinese-first bundle regression lock.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:516:  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:602:        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:649:        # WOW h3 stale English-first ordering (E11-15c convention)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:975:I have the E11-15e diff and tests loaded. I’m now checking the earlier E11-15c convention source and pulling exact line numbers from the current HTML/JS so the review can distinguish a real convention break from a wording nit.
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:3:# Context — E11-15b Chinese-first iter 2 (h1/h2/buttons/caption)
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:36:- **First-glance demo impression**: open `/workbench` cold — does the page now read Chinese-first across header, control buttons, annotation inbox, and approval center? Or is there still residual English-first surface that defeats the goal?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:38:- **Bilingual delimiter consistency**: every flip uses ` · ` (space-middot-space). Is this consistent with the rest of the codebase's bilingual pattern (e.g., column h2s `Probe & Trace · 探针与追踪`)? Note the column h2s use English-first; the new sweep uses Chinese-first. Is this asymmetry acceptable for demo flow, or does it look inconsistent at a glance?
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-prompt.txt:52:- **Reverse direction**: column h2s currently use English-first (`Probe & Trace · 探针与追踪`); could be flipped to Chinese-first in a future sweep for delimiter symmetry.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:15:> **IMPORTANT** — `workbench.html:225, 248, 337, 363`, `E11-15d-SURFACE-INVENTORY.md:5-6, 76-84`, `PERSONA-ROTATION-STATE.md:24`: the six approval-lane rewrites are correct, but the branch-level closure claim is not. `/workbench` still has visible English-only copy outside this slice (`Hide for session`, `Truth Engine — Read Only`, `No proposals submitted yet.`, `Pending Kogami sign-off`), so "last English-only surface" and "uniformly Chinese-first" are overstated as written.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:17:> **IMPORTANT** — `tests/test_workbench_approval_flow_polish.py:1-15, 61-169`, `workbench.html:111, 143, 173, 219-226`: test coverage matches the six-string approval-center polish, not the stronger page-wide closure claim. It does not catch the existing English-first WOW h3s or the multiline English-only dismiss button, so the current docs/test narrative can report full closure while the page still is not Chinese-first end-to-end.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:26:- Header banner now states this is "NOT the final Chinese-first sweep" and explicitly references the P2 R1 IMPORTANT.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:27:- Replaced "Closure summary" section with "Workbench Chinese-first thread progress (NOT closure)" + new explicit "English-only surfaces still remaining" section listing the 4 strings you found (with their existing test-lock locations) + WOW starter h3s + topbar chip labels. Deferred to future E11-15e Tier-A bundle.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:29:`PERSONA-ROTATION-STATE.md` line 24: rewrote E11-15d entry to remove "Closes the last English-only surface" + "uniformly Chinese-first"; added "P2 R1 IMPORTANT closure" note + same deferred-to-E11-15e list.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:33:`tests/test_workbench_approval_flow_polish.py` adds `test_e11_15d_surface_inventory_does_not_overclaim_closure` — asserts the forbidden phrases (`last English-only surface`, `uniformly Chinese-first`) cannot reappear in the SURFACE-INVENTORY outside the leading blockquote (which historically references them as forbidden).
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:46:- **Did R2 actually close the overclaim?** Re-grep the inventory + rotation-state for `last English-only surface` / `uniformly Chinese-first` outside the leading blockquote and confirm zero hits.
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-prompt.txt:48:- **Is the guard test sufficient?** It only catches reintroduction of those 2 specific phrases. Other overclaim phrasings (e.g., "the entire workbench Chinese-first work is done", "no English remains") would slip past. Acceptable trade-off for narrow IMPORTANT closure, OR should the guard be broader?
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-r2-output.md:233:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-r2-output.md:112:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-r2-output.md:127:899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)

exec
/bin/zsh -lc 'ls .planning/phases/E11-workbench-engineer-first-ux' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3780,3795p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_e11_15e_chinese_first_bundle.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
E11-00-PLAN.md
E11-01-BASELINE-PERSONA-REVIEW.md
E11-02-SURFACE-INVENTORY.md
E11-03-SURFACE-INVENTORY.md
E11-04-SURFACE-INVENTORY.md
E11-05-SURFACE-INVENTORY.md
E11-06-SURFACE-INVENTORY.md
E11-07-SURFACE-INVENTORY.md
E11-08-SURFACE-INVENTORY.md
E11-09-SURFACE-INVENTORY.md
E11-10-SURFACE-INVENTORY.md
E11-11-SURFACE-INVENTORY.md
E11-13-DRIFT-ACCEPTANCE.md
E11-13-SURFACE-INVENTORY.md
E11-14-SURFACE-INVENTORY.md
E11-15-SURFACE-INVENTORY.md
E11-15b-SURFACE-INVENTORY.md
E11-15c-SURFACE-INVENTORY.md
E11-15d-SURFACE-INVENTORY.md
E11-15e-SURFACE-INVENTORY.md
PERSONA-ROTATION-STATE.md
_E11-15e-prompt-shared-context.md
baseline-persona-outputs
persona-E11-05-shared-context.txt
persona-P1-E11-03-output.md
persona-P1-E11-03-prompt.txt
persona-P1-E11-03-r2-output.md
persona-P1-E11-03-r2-prompt.txt
persona-P1-E11-05-output.md
persona-P1-E11-05-prompt.txt
persona-P1-E11-05-r2-output.md
persona-P1-E11-05-r2-prompt.txt
persona-P1-E11-08-output.md
persona-P1-E11-08-prompt.txt
persona-P1-E11-10-R2-output.md
persona-P1-E11-10-R2-prompt.txt
persona-P1-E11-10-R3-output.md
persona-P1-E11-10-R3-prompt.txt
persona-P1-E11-10-output.md
persona-P1-E11-10-prompt.txt
persona-P1-E11-15e-output.md
persona-P1-E11-15e-prompt.txt
persona-P1-output.md
persona-P1-r2-output.md
persona-P1-r2-prompt.txt
persona-P1-r3-output.md
persona-P1-r3-prompt.txt
persona-P2-E11-03-output.md
persona-P2-E11-03-prompt.txt
persona-P2-E11-05-output.md
persona-P2-E11-05-prompt.txt
persona-P2-E11-05-r2-output.md
persona-P2-E11-05-r2-prompt.txt
persona-P2-E11-15-output.md
persona-P2-E11-15-prompt.txt
persona-P2-E11-15d-R2-output.md
persona-P2-E11-15d-R2-prompt.txt
persona-P2-E11-15d-R3-output.md
persona-P2-E11-15d-R3-prompt.txt
persona-P2-E11-15d-output.md
persona-P2-E11-15d-prompt.txt
persona-P2-E11-15e-output.md
persona-P2-E11-15e-prompt.txt
persona-P2-output.md
persona-P2-prompt.txt
persona-P2-r2-output.md
persona-P2-r2-prompt.txt
persona-P2-r3-output.md
persona-P2-r3-prompt.txt
persona-P3-E11-03-output.md
persona-P3-E11-03-prompt.txt
persona-P3-E11-04-output.md
persona-P3-E11-04-prompt.txt
persona-P3-E11-05-output.md
persona-P3-E11-05-prompt.txt
persona-P3-E11-15b-output.md
persona-P3-E11-15b-prompt.txt
persona-P3-E11-15e-output.md
persona-P3-E11-15e-prompt.txt
persona-P3-output.md
persona-P4-E11-03-output.md
persona-P4-E11-03-prompt.txt
persona-P4-E11-03-r2-output.md
persona-P4-E11-03-r2-prompt.txt
persona-P4-E11-05-output.md
persona-P4-E11-05-prompt.txt
persona-P4-E11-05-r2-output.md
persona-P4-E11-05-r2-prompt.txt
persona-P4-E11-06-output.md
persona-P4-E11-06-prompt.txt
persona-P4-E11-15c-output.md
persona-P4-E11-15c-prompt.txt
persona-P4-E11-15e-output.md
persona-P4-E11-15e-prompt.txt
persona-P4-output.md
persona-P5-E11-03-output.md
persona-P5-E11-03-prompt.txt
persona-P5-E11-03-r2-output.md
persona-P5-E11-03-r2-prompt.txt
persona-P5-E11-05-output.md
persona-P5-E11-05-prompt.txt
persona-P5-E11-05-r2-output.md
persona-P5-E11-05-r2-prompt.txt
persona-P5-E11-07-output.md
persona-P5-E11-07-prompt.txt
persona-P5-E11-11-output.md
persona-P5-E11-11-prompt.txt
persona-P5-E11-15e-output.md
persona-P5-E11-15e-prompt.txt
persona-P5-output.md

 succeeded in 0ms:
  3780	  if (!allowed.has(mode)) {
  3781	    return false;
  3782	  }
  3783	  const chip = document.getElementById("workbench-feedback-mode");
  3784	  if (chip) {
  3785	    chip.setAttribute("data-feedback-mode", mode);
  3786	    const label = chip.querySelector("strong");
  3787	    if (label) {
  3788	      label.textContent = mode === "truth_engine" ? "真值引擎 · Truth Engine" : "手动（仅参考）· Manual (advisory)";
  3789	    }
  3790	  }
  3791	  syncTrustBannerForMode(mode);
  3792	  return true;
  3793	}
  3794	
  3795	function installFeedbackModeAffordance() {

 succeeded in 0ms:
     1	"""E11-15e — Tier-A Chinese-first bundle regression lock.
     2	
     3	Bilingualizes 17 user-visible English-only surfaces enumerated by P2
     4	during the E11-15d review (see test_workbench_approval_flow_polish.py
     5	docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
     6	E11-15d-SURFACE-INVENTORY.md):
     7	
     8	  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
     9	  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
    10	  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
    11	                          open issues / advisory flag
    12	  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
    13	  Authority banner (1):   Truth Engine — Read Only headline
    14	  Trust dismiss (1):      Hide for session button
    15	  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
    16	  Reference packet (1):   Annotate column intro <p>
    17	  Inbox empty (1):        No proposals submitted yet.
    18	  Pending sign-off (1):   Pending Kogami sign-off
    19	
    20	Pattern: `<中文> · <English>` everywhere; English suffix is preserved
    21	verbatim so all prior `assert <english> in html` substring locks across
    22	test_workbench_trust_affordance, test_workbench_authority_banner,
    23	test_workbench_role_affordance, test_workbench_column_rename, and
    24	test_workbench_state_of_world_bar continue to pass without contract
    25	churn.
    26	
    27	Out of scope (deferred to a future Tier-A or constitutional decision):
    28	  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    29	    domain proper nouns coupled to value-attribute IDs and to the
    30	    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
    31	  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    32	    locked by tests/test_workbench_column_rename.py:170-172 — those are
    33	    a separate JS-side bilingualization with their own lockstep contract.
    34	  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    35	    </pre> flow diagram — visual phase-arrow, not English copy.
    36	  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    37	    that were already bilingualized in earlier sub-phases.
    38	
    39	Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
    40	"""
    41	
    42	from __future__ import annotations
    43	
    44	import http.client
    45	import threading
    46	from http.server import ThreadingHTTPServer
    47	from pathlib import Path
    48	
    49	import pytest
    50	
    51	from well_harness.demo_server import DemoRequestHandler
    52	
    53	
    54	REPO_ROOT = Path(__file__).resolve().parents[1]
    55	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    56	
    57	
    58	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    59	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    60	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    61	    thread.start()
    62	    return server, thread
    63	
    64	
    65	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    66	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    67	    connection.request("GET", path)
    68	    response = connection.getresponse()
    69	    return response.status, response.read().decode("utf-8")
    70	
    71	
    72	@pytest.fixture
    73	def server():
    74	    s, t = _start_demo_server()
    75	    try:
    76	        yield s
    77	    finally:
    78	        s.shutdown()
    79	        s.server_close()
    80	        t.join(timeout=2)
    81	
    82	
    83	# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────
    84	
    85	
    86	@pytest.mark.parametrize(
    87	    "bilingual",
    88	    [
    89	        # Topbar chip labels (5)
    90	        "<span>身份 · Identity</span>",
    91	        "<span>工单 · Ticket</span>",
    92	        "<span>反馈模式 · Feedback Mode</span>",
    93	        "<span>系统 · System</span>",
    94	        "<strong>手动（仅参考）· Manual (advisory)</strong>",
    95	        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
    96	        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
    97	        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
    98	        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
    99	        # State-of-world labels (4) + advisory flag (1)
   100	        "真值引擎 SHA · truth-engine SHA",
   101	        "最近 e2e · recent e2e",
   102	        "对抗样本 · adversarial",
   103	        "未关闭问题 · open issues",
   104	        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
   105	        # Trust banner body (3)
   106	        '这里"手动反馈"的含义 · What "manual feedback" means here:',
   107	        "该模式仅作参考 · That mode is advisory.",
   108	        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
   109	        # Trust banner dismiss (1)
   110	        "隐藏（本次会话）· Hide for session",
   111	        # Authority banner headline (1)
   112	        "真值引擎 · 只读 · Truth Engine — Read Only",
   113	        # Pre-hydration boot placeholders (3)
   114	        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
   115	        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
   116	        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
   117	        # Reference-packet intro (1)
   118	        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
   119	        # Inbox empty state (1)
   120	        "暂无已提交提案 · No proposals submitted yet.",
   121	        # Pending sign-off (1)
   122	        "等待 Kogami 签字 · Pending Kogami sign-off",
   123	    ],
   124	)
   125	def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
   126	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   127	    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"
   128	
   129	
   130	# ─── 2. Stale English-only surfaces are gone ─────────────────────────
   131	
   132	
   133	@pytest.mark.parametrize(
   134	    "stale",
   135	    [
   136	        # Bare topbar chip labels (no Chinese prefix) — must be replaced
   137	        "<span>Identity</span>",
   138	        "<span>Ticket</span>",
   139	        "<span>Feedback Mode</span>",
   140	        "<span>System</span>",
   141	        "<strong>Manual (advisory)</strong>",
   142	        # WOW h3 stale English-first ordering (E11-15c convention)
   143	        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
   144	        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
   145	        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
   146	        # Bare state-of-world labels (no Chinese prefix)
   147	        ">truth-engine SHA<",
   148	        ">recent e2e<",
   149	        ">adversarial<",
   150	        ">open issues<",
   151	        # Bare trust-banner body lines — these are now sentence-internal
   152	        # so we look for the line-leading position they used to hold.
   153	        "<em>What \"manual feedback\" means here:</em>",
   154	        "<strong>That mode is advisory.</strong>",
   155	        # Bare button + headline + boot placeholders
   156	        ">\n          Hide for session\n        <",
   157	        ">\n          Truth Engine — Read Only\n        <",
   158	        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
   159	        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
   160	        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
   161	        # Bare inbox + pending sign-off
   162	        "<li>No proposals submitted yet.</li>",
   163	        "<strong>Pending Kogami sign-off</strong>",
   164	    ],
   165	)
   166	def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
   167	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   168	    assert stale not in html, f"stale English-only surface still present: {stale}"
   169	
   170	
   171	# ─── 3. English suffixes preserved (substring locks unchanged) ───────
   172	
   173	
   174	@pytest.mark.parametrize(
   175	    "preserved_english_suffix",
   176	    [
   177	        # Anchors required by trust_affordance.py
   178	        "Manual (advisory)",
   179	        "Truth engine readings",
   180	        "Hide for session",
   181	        'What "manual feedback" means here',
   182	        "That mode is advisory.",
   183	        # Anchor required by authority_banner.py
   184	        "Truth Engine — Read Only",
   185	        # Anchor required by role_affordance.py
   186	        "Pending Kogami sign-off",
   187	        # Anchor required by state_of_world_bar.py
   188	        "advisory · not a live truth-engine reading",
   189	        # Anchors required by column_rename.py:118-120 (pre-hydration)
   190	        "Waiting for probe &amp; trace panel boot.",
   191	        "Waiting for annotate &amp; propose panel boot.",
   192	        "Waiting for hand off &amp; track panel boot.",
   193	    ],
   194	)
   195	def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
   196	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   197	    assert preserved_english_suffix in html, (
   198	        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
   199	    )
   200	
   201	
   202	# ─── 4. Structural anchors preserved ─────────────────────────────────
   203	
   204	
   205	@pytest.mark.parametrize(
   206	    "anchor",
   207	    [
   208	        'id="workbench-feedback-mode"',
   209	        'id="workbench-trust-banner"',
   210	        'id="workbench-authority-banner"',
   211	        'id="workbench-pending-signoff-affordance"',
   212	        'id="workbench-state-of-world-bar"',
   213	        'id="workbench-wow-starters"',
   214	        'data-trust-banner-dismiss',
   215	        'data-feedback-mode="manual_feedback_override"',
   216	    ],
   217	)
   218	def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
   219	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   220	    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"
   221	
   222	
   223	# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
   224	
   225	
   226	def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
   227	    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
   228	    switch. If the JS literal stays English-only, the very first mode
   229	    flip would silently revert the static HTML's bilingual chip back to
   230	    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
   231	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   232	    assert '"真值引擎 · Truth Engine"' in js, (
   233	        "JS feedback-mode `truth_engine` branch must use bilingual label"
   234	    )
   235	    assert '"手动（仅参考）· Manual (advisory)"' in js, (
   236	        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
   237	    )
   238	    # Stale English-only literals must not coexist (would imply duplicate
   239	    # write-paths or stale residue).
   240	    assert '"Truth Engine"' not in js, (
   241	        'stale English-only `"Truth Engine"` literal still in workbench.js'
   242	    )
   243	    assert '"Manual (advisory)"' not in js, (
   244	        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
   245	    )
   246	
   247	
   248	# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────
   249	
   250	
   251	def test_workbench_route_serves_e11_15e_bundle(server) -> None:
   252	    status, html = _get(server, "/workbench")
   253	    assert status == 200
   254	    # Spot-check one string from each surface category.
   255	    assert "身份 · Identity" in html
   256	    assert "因果链走读 · Causal Chain" in html
   257	    assert "真值引擎 SHA · truth-engine SHA" in html
   258	    assert "该模式仅作参考 · That mode is advisory." in html
   259	    assert "隐藏（本次会话）· Hide for session" in html
   260	    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html

codex
The main open question is whether the copy issues are merely stylistic or actually violate the previously established direction rule. I’m reading the E11-15c source of truth now and will run the targeted E11-15e bundle test once the line-level review is complete.
exec
/bin/zsh -lc "sed -n '1,220p' .planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
# E11-15c Surface Inventory — column h2 direction flip + h1/eyebrow dedup

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Direct closure of the 2 NITs raised by P3 Demo Presenter on E11-15b
> (`persona-P3-E11-15b-output.md:165-167`).

## NIT closure summary

| P3 NIT | Fix |
|---|---|
| #1: page eyebrow `控制逻辑工作台` immediately followed by h1 `控制逻辑工作台 · Control Logic Workbench` reads redundantly | Eyebrow flipped to `工程师工作区` so eyebrow + h1 read as category + title (two distinct semantic levels) |
| #2: column h2s are still English-first while the rest of the page is Chinese-first | 3 column h2s flipped from `<English> · <中文>` to `<中文> · <English>` for full-page direction consistency |

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Page eyebrow `控制逻辑工作台` → `工程师工作区` | [REWRITE] | `workbench.html:17` | Closes P3 NIT #1; eyebrow now reads as engineer-workspace sub-category, h1 stays as page title. |
| 2 | Column h2 `Probe & Trace · 探针与追踪` → `探针与追踪 · Probe & Trace` | [REWRITE] | `workbench.html:275` | Closes P3 NIT #2; English suffix preserved for substring locks. |
| 3 | Column h2 `Annotate & Propose · 标注与提案` → `标注与提案 · Annotate & Propose` | [REWRITE] | `workbench.html:295` | Same. |
| 4 | Column h2 `Hand off & Track · 移交与跟踪` → `移交与跟踪 · Hand off & Track` | [REWRITE] | `workbench.html:315` | Same. |

## Test contract updates (existing files touched in lockstep)

- `tests/test_workbench_column_rename.py`: 2 assertion blocks updated
  to expect Chinese-first column h2s (param values + live-route check).
- `tests/test_workbench_chinese_eyebrow_sweep.py`: page eyebrow lock
  updated from `控制逻辑工作台` to `工程师工作区`; truth-engine
  spot-check token list and live-route check updated to add
  `工程师工作区` while keeping `控制逻辑工作台` as a substring (still
  served via h1).
- `tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):
  positive locks for new strings, negative locks for stale, English suffix
  preservation, eyebrow-vs-h1 non-duplication invariant, live-served route,
  truth-engine isolation.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 4 → < 10
- **[REWRITE/DELETE] count** = 4 → ≥ 3

→ **Tier-B** (1-persona review). The first threshold (≥10) fails.

> **Verdict: Tier-B**. Persona = **P4 (V&V Engineer)** — round-robin
> successor of E11-15b's P3 AND content-fit: this sub-phase rewrites
> existing test contracts in lockstep with HTML changes, so the V&V
> lens (verifying invariants are preserved across the contract migration)
> is exactly right.

## Behavior contract (locked by tests)

`tests/test_workbench_chinese_direction_consistency.py` (NEW, 15 tests):

1. 3 column h2s positively asserted Chinese-first.
2. 3 stale English-first column h2 strings asserted absent.
3. Page eyebrow positively asserted as `工程师工作区`; old `控制逻辑工作台` eyebrow asserted absent.
4. h1 still carries `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` (E11-15b contract preserved).
5. Programmatic invariant: extracted eyebrow inner text != extracted h1 Chinese half — locks the dedup property.
6. 4 English suffixes preserved (`Probe & Trace</h2>`, etc.).
7. Live-served `/workbench` route serves all new strings.
8. Truth-engine isolation: new Chinese strings absent from `demo_server.py`/`controller.py`/`runner.py`/`models.py`/`workbench.js`/`workbench.css`.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — 4 strings flipped
- `tests/test_workbench_column_rename.py` — 2 assertion blocks updated
- `tests/test_workbench_chinese_eyebrow_sweep.py` — eyebrow + truth-engine token list + live-route assertions updated
- `tests/test_workbench_chinese_direction_consistency.py` — NEW (15 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15c-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.js`, `workbench.css`,
`demo_server.py`. Truth-engine boundary preserved.

exec
/bin/zsh -lc "nl -ba tests/test_workbench_chinese_direction_consistency.py | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.
     2	
     3	Two NIT closures from E11-15b (P3 Demo Presenter):
     4	
     5	NIT #1 — h1 + eyebrow duplication
     6	    `<p class="eyebrow">控制逻辑工作台</p>` immediately followed by
     7	    `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` reads redundantly.
     8	    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
     9	    eyebrow + h1 read as category + title.
    10	
    11	NIT #2 — direction asymmetry
    12	    Column-trio h2s were English-first (`Probe & Trace · 探针与追踪`)
    13	    while the rest of the page is Chinese-first. E11-15c flips them
    14	    to `<中文> · <English>` for full-page direction consistency.
    15	
    16	Net change is 4 [REWRITE] lines in workbench.html. Existing test files
    17	test_workbench_column_rename and test_workbench_chinese_eyebrow_sweep
    18	were updated in lockstep with the new strings.
    19	"""
    20	
    21	from __future__ import annotations
    22	
    23	import http.client
    24	import threading
    25	from http.server import ThreadingHTTPServer
    26	from pathlib import Path
    27	
    28	import pytest
    29	
    30	from well_harness.demo_server import DemoRequestHandler
    31	
    32	
    33	REPO_ROOT = Path(__file__).resolve().parents[1]
    34	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    35	
    36	
    37	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    38	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    39	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    40	    thread.start()
    41	    return server, thread
    42	
    43	
    44	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    45	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    46	    connection.request("GET", path)
    47	    response = connection.getresponse()
    48	    return response.status, response.read().decode("utf-8")
    49	
    50	
    51	@pytest.fixture
    52	def server():
    53	    s, t = _start_demo_server()
    54	    try:
    55	        yield s
    56	    finally:
    57	        s.shutdown()
    58	        s.server_close()
    59	        t.join(timeout=2)
    60	
    61	
    62	# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────
    63	
    64	
    65	@pytest.mark.parametrize(
    66	    "chinese_first_h2",
    67	    [
    68	        "<h2>探针与追踪 · Probe &amp; Trace</h2>",
    69	        "<h2>标注与提案 · Annotate &amp; Propose</h2>",
    70	        "<h2>移交与跟踪 · Hand off &amp; Track</h2>",
    71	    ],
    72	)
    73	def test_column_h2_is_chinese_first(chinese_first_h2: str) -> None:
    74	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    75	    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"
    76	
    77	
    78	@pytest.mark.parametrize(
    79	    "stale_english_first_h2",
    80	    [
    81	        "<h2>Probe &amp; Trace · 探针与追踪</h2>",
    82	        "<h2>Annotate &amp; Propose · 标注与提案</h2>",
    83	        "<h2>Hand off &amp; Track · 移交与跟踪</h2>",
    84	    ],
    85	)
    86	def test_stale_english_first_column_h2_removed(stale_english_first_h2: str) -> None:
    87	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    88	    assert stale_english_first_h2 not in html, (
    89	        f"stale English-first column h2 still present: {stale_english_first_h2}"
    90	    )
    91	
    92	
    93	# ─── 2. NIT #1: page eyebrow + h1 are no longer duplicates ───────────
    94	
    95	
    96	def test_page_eyebrow_is_engineer_workspace_not_h1_duplicate() -> None:
    97	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    98	    assert '<p class="eyebrow">工程师工作区</p>' in html
    99	    assert '<p class="eyebrow">控制逻辑工作台</p>' not in html
   100	
   101	
   102	def test_h1_still_carries_full_bilingual_title() -> None:
   103	    """E11-15b's h1 bilingualization must survive E11-15c — only the
   104	    sibling eyebrow changes; the h1 stays as the page-title source of
   105	    truth."""
   106	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   107	    assert "<h1>控制逻辑工作台 · Control Logic Workbench</h1>" in html
   108	
   109	
   110	def test_eyebrow_and_h1_are_not_chinese_duplicates() -> None:
   111	    """Closure of P3's NIT #1: extracting the eyebrow's Chinese and the
   112	    h1's Chinese, they must not match."""
   113	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   114	    eyebrow_inner = (
   115	        html.split('<div class="workbench-collab-brand">')[1]
   116	        .split('<p class="eyebrow">')[1]
   117	        .split("</p>")[0]
   118	    )
   119	    h1_inner = html.split("<h1>")[1].split("</h1>")[0]
   120	    h1_chinese = h1_inner.split(" · ")[0]
   121	    assert eyebrow_inner != h1_chinese, (
   122	        f"eyebrow ({eyebrow_inner!r}) duplicates h1 Chinese ({h1_chinese!r}) — "
   123	        "P3 NIT #1 not closed"
   124	    )
   125	
   126	
   127	# ─── 3. English suffixes preserved (no regression on substring locks) ─
   128	
   129	
   130	@pytest.mark.parametrize(
   131	    "preserved_english_suffix",
   132	    [
   133	        "Probe &amp; Trace</h2>",
   134	        "Annotate &amp; Propose</h2>",
   135	        "Hand off &amp; Track</h2>",
   136	        "Control Logic Workbench</h1>",
   137	    ],
   138	)
   139	def test_e11_15c_preserves_english_suffix(preserved_english_suffix: str) -> None:
   140	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   141	    assert preserved_english_suffix in html, (
   142	        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
   143	    )
   144	
   145	
   146	# ─── 4. Live-served route reflects E11-15c ───────────────────────────
   147	
   148	
   149	def test_workbench_route_reflects_direction_flip(server) -> None:
   150	    status, html = _get(server, "/workbench")
   151	    assert status == 200
   152	    assert "探针与追踪 · Probe" in html
   153	    assert "标注与提案 · Annotate" in html
   154	    assert "移交与跟踪 · Hand off" in html
   155	    assert "工程师工作区" in html
   156	
   157	
   158	# ─── 5. Truth-engine red line ────────────────────────────────────────
   159	
   160	
   161	def test_e11_15c_only_touches_static_html_and_tests() -> None:
   162	    """The fix is HTML + test-only. Demo server, controller, runner,
   163	    models, adapters, JS, and CSS must NOT carry any of the 4 new
   164	    strings.
   165	
   166	    P4 IMPORTANT closure (E11-15c review): every backend / JS / CSS /
   167	    adapters file is scanned against EVERY new string, not just a
   168	    subset.
   169	    """
   170	    repo_root = Path(__file__).resolve().parents[1]
   171	    well_harness_root = repo_root / "src" / "well_harness"
   172	
   173	    new_strings = [
   174	        "工程师工作区",
   175	        "探针与追踪 · Probe",
   176	        "标注与提案 · Annotate",
   177	        "移交与跟踪 · Hand off",
   178	    ]
   179	
   180	    scan_targets: list[Path] = [
   181	        well_harness_root / "demo_server.py",
   182	        well_harness_root / "controller.py",
   183	        well_harness_root / "runner.py",
   184	        well_harness_root / "models.py",
   185	        well_harness_root / "static" / "workbench.js",
   186	        well_harness_root / "static" / "workbench.css",
   187	    ]
   188	    adapters_dir = well_harness_root / "adapters"
   189	    if adapters_dir.is_dir():
   190	        scan_targets.extend(p for p in adapters_dir.rglob("*.py"))
   191	
   192	    for target in scan_targets:
   193	        if not target.exists():
   194	            continue
   195	        content = target.read_text(encoding="utf-8")
   196	        for new_string in new_strings:
   197	            assert new_string not in content, (
   198	                f"E11-15c string {new_string!r} unexpectedly leaked into "
   199	                f"{target.relative_to(repo_root)}"
   200	            )

exec
/bin/zsh -lc 'pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 795ms:
...................................................................      [100%]
67 passed in 0.60s

codex
I found a potentially real scope miss, not just a wording nit: the feedback-mode chip’s hover `title` is still English-only on the same DOM block that E11-15e bilingualized. I’m checking whether that surface was already deferred or tested before I decide the verdict.
exec
/bin/zsh -lc "rg -n \"Kogami / Engineer|data-identity-name|Identity</span>|feedback-mode|title=\\\"\" src/well_harness/static/workbench.html .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md tests/test_workbench_e11_15e_chinese_first_bundle.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:37:| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:84:| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
src/well_harness/static/workbench.html:24:          data-identity-name="Kogami"
src/well_harness/static/workbench.html:26:          <span>身份 · Identity</span>
src/well_harness/static/workbench.html:27:          <strong>Kogami / Engineer</strong>
src/well_harness/static/workbench.html:34:          id="workbench-feedback-mode"
src/well_harness/static/workbench.html:35:          class="workbench-collab-chip workbench-feedback-mode-chip"
src/well_harness/static/workbench.html:36:          data-feedback-mode="manual_feedback_override"
src/well_harness/static/workbench.html:39:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
src/well_harness/static/workbench.html:43:          <span class="workbench-feedback-mode-dot" aria-hidden="true"></span>
src/well_harness/static/workbench.html:64:              title="git rev-parse --short HEAD">
src/well_harness/static/workbench.html:70:              title="docs/coordination/qa_report.md (most recent test run)">
src/well_harness/static/workbench.html:76:              title="docs/coordination/qa_report.md (shared validation)">
src/well_harness/static/workbench.html:82:              title="docs/known-issues/ file count">
src/well_harness/static/workbench.html:202:        data-feedback-mode="manual_feedback_override"
src/well_harness/static/workbench.html:259:          title="v6.1 truth-engine red line — sourced from .planning/constitution.md"
tests/test_workbench_e11_15e_chinese_first_bundle.py:90:        "<span>身份 · Identity</span>",
tests/test_workbench_e11_15e_chinese_first_bundle.py:137:        "<span>Identity</span>",
tests/test_workbench_e11_15e_chinese_first_bundle.py:208:        'id="workbench-feedback-mode"',
tests/test_workbench_e11_15e_chinese_first_bundle.py:215:        'data-feedback-mode="manual_feedback_override"',
tests/test_workbench_e11_15e_chinese_first_bundle.py:223:# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──
tests/test_workbench_e11_15e_chinese_first_bundle.py:233:        "JS feedback-mode `truth_engine` branch must use bilingual label"
tests/test_workbench_e11_15e_chinese_first_bundle.py:236:        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"

exec
/bin/zsh -lc "rg -n \"Manual feedback override is advisory|truth engine readings remain authoritative|title=\\\"Manual feedback override\" -S src/well_harness/static tests .planning/phases/E11-workbench-engineer-first-ux" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15e-output.md:897:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
src/well_harness/static/workbench.html:39:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-output.md:687:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:834:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:252:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15b-output.md:1264:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:283:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-output.md:918:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:823:           title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-08-output.md:1520:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:652:           title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-15e-output.md:1316:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-03-output.md:580:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:1108:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-15e-output.md:1314:           title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-03-r2-output.md:494:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:993:           title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1949:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:383:src/well_harness/static/workbench.html:34:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:485:src/well_harness/static/workbench.html:34:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r3-output.md:633:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-15c-output.md:249:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1166:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15d-R2-output.md:1254:39: title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-output.md:1266:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:343:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:9297:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25:| 3 | Topbar chip tooltip | "Manual feedback override is advisory — truth engine readings remain authoritative." | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode title attribute) | [ANCHORED] |
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:318:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1269:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1450:/tmp/p1_workbench.html:34:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md:1500:src/well_harness/static/workbench.html:34:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-06-output.md:1102:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-03-output.md:328:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-r2-output.md:606:src/well_harness/static/workbench.html:34:          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:567:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:792:           title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-15e-output.md:998:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15-output.md:994:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-15e-output.md:1556:    39	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-r2-output.md:1990:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-03-r2-output.md:340:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-07-output.md:1944:    34	          title="Manual feedback override is advisory — truth engine readings remain authoritative."

codex
The hover-tooltip miss is real. Earlier E11 inventory already treated that `title` as a topbar chip surface, and E11-15e neither rewrote it nor deferred it, so this is an omitted bilingual surface rather than a deliberate exclusion.
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md | sed -n '18,32p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    18	
    19	## Inventory table
    20	
    21	| # | Surface | Claim text | Anchor | Status |
    22	|---|---------|-----------|--------|--------|
    23	| 1 | Topbar chip label | "Feedback Mode" (chip eyebrow) | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode chip span) | [ANCHORED] |
    24	| 2 | Topbar chip value | "Manual (advisory)" (chip strong) | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode chip strong) | [ANCHORED] |
    25	| 3 | Topbar chip tooltip | "Manual feedback override is advisory — truth engine readings remain authoritative." | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode title attribute) | [ANCHORED] |
    26	| 4 | Trust banner heading | "Manual feedback mode is advisory." | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner body strong) | [ANCHORED] |
    27	| 5 | Trust banner explanation | "Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative. Your manual feedback is recorded for diff/review but does not change source-of-truth values." | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner body span) | [ANCHORED] |
    28	| 6 | Trust banner dismiss button | "Hide for session" | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner button) | [ANCHORED] |
    29	| 7 | Truth-engine alt label | "Truth Engine" (chip strong when mode=truth_engine) | `src/well_harness/static/workbench.js:setFeedbackMode()` (mode === "truth_engine" branch) | [ANCHORED] |
    30	
    31	## No-rewrite confirmation
    32	

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md | sed -n '30,95p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    30	
    31	Pattern across all rows: `<中文> · <English>`. The English suffix is preserved
    32	verbatim so prior-sub-phase substring locks (`assert <english> in html`) keep
    33	passing without contract churn.
    34	
    35	| # | Surface | File:Line | Old (English-only) | New (bilingual) |
    36	|---|---------|-----------|---------------------|-----------------|
    37	| 1 | Identity chip label | workbench.html:26 | `<span>Identity</span>` | `<span>身份 · Identity</span>` |
    38	| 2 | Ticket chip label | workbench.html:30 | `<span>Ticket</span>` | `<span>工单 · Ticket</span>` |
    39	| 3 | Feedback Mode chip label | workbench.html:41 | `<span>Feedback Mode</span>` | `<span>反馈模式 · Feedback Mode</span>` |
    40	| 4 | Manual (advisory) chip text (HTML) | workbench.html:42 | `<strong>Manual (advisory)</strong>` | `<strong>手动（仅参考）· Manual (advisory)</strong>` |
    41	| 5 | Manual (advisory) chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Manual (advisory)"` literal | `"手动（仅参考）· Manual (advisory)"` |
    42	| 6 | Truth Engine chip text (JS, dynamic on mode switch) | workbench.js:3788 | `"Truth Engine"` literal | `"真值引擎 · Truth Engine"` |
    43	| 7 | System chip label | workbench.html:46 | `<span>System</span>` | `<span>系统 · System</span>` |
    44	| 8 | WOW h3 (wow_a) — direction flip | workbench.html:111 | `Causal Chain · 因果链走读` | `因果链走读 · Causal Chain` |
    45	| 9 | WOW h3 (wow_b) — direction flip | workbench.html:143 | `Monte Carlo · 1000-trial 可靠性` | `1000-trial 可靠性 · Monte Carlo` |
    46	| 10 | WOW h3 (wow_c) — direction flip | workbench.html:173 | `Reverse Diagnose · 反向诊断` | `反向诊断 · Reverse Diagnose` |
    47	| 11 | State-of-world label · sha | workbench.html:65 | `truth-engine SHA` | `真值引擎 SHA · truth-engine SHA` |
    48	| 12 | State-of-world label · e2e | workbench.html:71 | `recent e2e` | `最近 e2e · recent e2e` |
    49	| 13 | State-of-world label · adversarial | workbench.html:77 | `adversarial` | `对抗样本 · adversarial` |
    50	| 14 | State-of-world label · open issues | workbench.html:83 | `open issues` | `未关闭问题 · open issues` |
    51	| 15 | State-of-world advisory flag | workbench.html:87 | `advisory · not a live truth-engine reading` | `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` |
    52	| 16 | Trust banner scope `<em>` | workbench.html:209-211 | `<em>What "manual feedback" means here:</em> any value...` | `<em>这里"手动反馈"的含义 · What "manual feedback" means here:</em> 你在工作台中手动键入...` |
    53	| 17 | Trust banner advisory `<strong>` | workbench.html:213 | `<strong>That mode is advisory.</strong>` | `<strong>该模式仅作参考 · That mode is advisory.</strong>` |
    54	| 18 | Trust banner truth-engine `<span>` | workbench.html:215-217 | `Truth engine readings (logic gates L1–L4 ...)` | `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings ...` |
    55	| 19 | Trust banner dismiss button | workbench.html:225 | `Hide for session` | `隐藏（本次会话）· Hide for session` |
    56	| 20 | Authority banner headline | workbench.html:248 | `Truth Engine — Read Only` | `真值引擎 · 只读 · Truth Engine — Read Only` |
    57	| 21 | Pre-hydration boot status (control panel) | workbench.html:278 | `Waiting for probe & trace panel boot.` | `等待 probe & trace 面板启动 · Waiting for probe & trace panel boot.` |
    58	| 22 | Pre-hydration boot status (document panel) | workbench.html:298 | `Waiting for annotate & propose panel boot.` | `等待 annotate & propose 面板启动 · Waiting for annotate & propose panel boot.` |
    59	| 23 | Pre-hydration boot status (circuit panel) | workbench.html:318 | `Waiting for hand off & track panel boot.` | `等待 hand off & track 面板启动 · Waiting for hand off & track panel boot.` |
    60	| 24 | Reference packet intro `<p>` | workbench.html:301 | `Reference packet, clarification notes...` | `参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, ...` |
    61	| 25 | Annotation inbox empty state | workbench.html:337 | `<li>No proposals submitted yet.</li>` | `<li>暂无已提交提案 · No proposals submitted yet.</li>` |
    62	| 26 | Pending sign-off `<strong>` | workbench.html:363 | `<strong>Pending Kogami sign-off</strong>` | `<strong>等待 Kogami 签字 · Pending Kogami sign-off</strong>` |
    63	
    64	(22 rows after dedup of #5/#6 with their HTML siblings; the table uses 26 row IDs
    65	for line-of-evidence but treats #4+#5 and #11-#14+#15 as single `surface diff`
    66	counts in the metric table above.)
    67	
    68	---
    69	
    70	## 3. Out of scope (explicitly deferred — surface-honesty closure)
    71	
    72	E11-15e is **NOT** "the last English-only surface" on `/workbench`. The
    73	following surfaces remain English-only and are **deferred to future sub-phases
    74	or constitutional decisions**, not silently included:
    75	
    76	| Deferred surface | Why deferred | File:Line |
    77	|------------------|--------------|-----------|
    78	| `<option>` system values (`Thrust Reverser`, `Landing Gear`, `Bleed Air Valve`, `C919 E-TRAS`) | Domain proper nouns coupled to value-attribute IDs and the multi-system adapter dispatch in `tests/test_p19_api_multisystem.py`. Bilingualizing the option text would require coordinated changes to value-id parsing, locale-mapping, and the adapter contract. | workbench.html:48-51 |
    79	| Post-hydration JS boot status strings (`Probe & Trace ready. Scenario actions are staged for the next bundle.` × 3) | Locked by `tests/test_workbench_column_rename.py:170-172`; would require workbench.js bilingualization with its own lockstep test contract. **Note:** This is the string users actually see for most of session — the "Waiting for ... panel boot." strings E11-15e bilingualizes are pre-hydration only. Re-tier as Tier-A for a follow-up sub-phase. | workbench.js boot fns |
    80	| `<pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>` | Visual phase-arrow diagram, not English copy. Would require a Chinese arrow notation decision (e.g. `承接 → 澄清 → 回放 → 诊断 → 知识`); deferred to UX/copy decision. | workbench.html:302 |
    81	| `data-wow-id="wow_a"` attribute strings + `data-wow-action="run"` | Internal data-* attributes, not user-visible — out of bilingualization scope by design. | workbench.html:104-194 |
    82	| `wow_a/b/c` tag spans (`<span class="workbench-wow-tag">wow_a</span>`) | Card identifier sigil, not display copy; these literally name the API endpoint group. | workbench.html:110/142/172 |
    83	| Eyebrow `probe & trace` / `annotate & propose` / `hand off & track` (lowercase column eyebrows) | These are paired with the bilingual `<h2>` titles E11-15c shipped (e.g. `<h2>探针与追踪 · Probe & Trace</h2>`). Eyebrows are intentionally English-only for the column-key tag pattern; if revisited, would need its own constitutional pass. | workbench.html:274/294/314 |
    84	| `WB-E06-SHELL` ticket id, `Kogami / Engineer` identity | Identifiers/proper nouns, not display copy. | workbench.html:27/31 |
    85	
    86	**Surface-honesty pledge:** This sub-phase closes 22 surfaces. It does NOT close
    87	"all" or "the last". The deferred list above is **non-exhaustive** — if a
    88	reviewer finds another English-only user-visible surface not listed here that is
    89	neither REWRITE in this slice nor in the deferred table, that finding is
    90	**legitimate** and a CHANGES_REQUIRED is appropriate.
    91	
    92	---
    93	
    94	## 4. Truth-engine red line
    95	

codex
I have enough to issue the review. I’m just pulling the exact memory line I used for repo continuity so the final answer can include the required citation block, then I’ll give the verdict with line-cited findings and suggested wording fixes.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,856p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
**CHANGES_REQUIRED**

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:39>), [E11-13-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:88>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:86>)
  The feedback-mode chip hover `title` is still English-only: `Manual feedback override is advisory — truth engine readings remain authoritative.` This is not just an out-of-scope nit. E11-13 already anchored that `title` attribute as a user-visible topbar-chip surface, and E11-15e neither bilingualizes it nor defers it. Under E11-15e’s own surface-honesty pledge, that is a legitimate missed surface.
  Suggested fix: rewrite it to `手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative.` Then add a positive lock for the full bilingual `title=` string, a negative guard for the old exact `title="Manual feedback override ..."` form, and an inventory row for this surface.

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:143>), [test_workbench_chinese_direction_consistency.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:11>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:97>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45>)
  `1000-trial 可靠性 · Monte Carlo` is not actually Chinese-first. E11-15c established page-wide `<中文> · <English>` direction for consistency; this h3 still begins with an English token, and the new test/inventory currently lock that exception in place.
  Suggested fix: change it to `1000 次试验可靠性 · Monte Carlo` and update the positive/stale locks plus the inventory row to match. The wow_b description can stay as-is; it already aligns with that wording.

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:248>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:104>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:31>)
  Two strings break the phase’s own advertised `<中文> · <English>` pattern by using extra middots inside the Chinese half: `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` and `真值引擎 · 只读 · Truth Engine — Read Only`. They are readable, but they are not the strict convention the docs/tests claim.
  Suggested fix: collapse each Chinese side into one phrase and reserve the outer middot for the Chinese/English split:
  `仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading`
  `真值引擎（只读） · Truth Engine — Read Only`
  Then update tests and inventory so they stop asserting the multi-middot forms as convention-correct.

- `NIT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:209>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:106>)
  The trust-banner Chinese is understandable but not fully native. `这里"手动反馈"的含义` is awkward word order, and `仍然是权威` reads like a calque rather than engineer-facing Chinese.
  Suggested fix: use `此处“手动反馈”的含义 · What "manual feedback" means here:` and `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings ... remain authoritative.` If you touch that sentence, `不算 manual feedback` would also read better as `不属于“手动反馈”`.

I did not flag `身份 · Identity`, `工单 · Ticket`, `反馈模式 · Feedback Mode`, or `手动（仅参考）· Manual (advisory)`; those are acceptable register choices here. I also did not count `Kogami / Engineer` as a violation because E11-15e explicitly defers identifiers/proper nouns, unlike the untranslated feedback-mode tooltip.

Verification: `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py` passed (`67 passed`).


tokens used
83,895
**CHANGES_REQUIRED**

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:39>), [E11-13-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-13-SURFACE-INVENTORY.md:25>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:88>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:86>)
  The feedback-mode chip hover `title` is still English-only: `Manual feedback override is advisory — truth engine readings remain authoritative.` This is not just an out-of-scope nit. E11-13 already anchored that `title` attribute as a user-visible topbar-chip surface, and E11-15e neither bilingualizes it nor defers it. Under E11-15e’s own surface-honesty pledge, that is a legitimate missed surface.
  Suggested fix: rewrite it to `手动反馈覆盖仅作参考，仍以真值引擎读数为准 · Manual feedback override is advisory — truth engine readings remain authoritative.` Then add a positive lock for the full bilingual `title=` string, a negative guard for the old exact `title="Manual feedback override ..."` form, and an inventory row for this surface.

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:143>), [test_workbench_chinese_direction_consistency.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_chinese_direction_consistency.py:11>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:97>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:45>)
  `1000-trial 可靠性 · Monte Carlo` is not actually Chinese-first. E11-15c established page-wide `<中文> · <English>` direction for consistency; this h3 still begins with an English token, and the new test/inventory currently lock that exception in place.
  Suggested fix: change it to `1000 次试验可靠性 · Monte Carlo` and update the positive/stale locks plus the inventory row to match. The wow_b description can stay as-is; it already aligns with that wording.

- `IMPORTANT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:87>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:248>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:104>), [E11-15e-SURFACE-INVENTORY.md](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md:31>)
  Two strings break the phase’s own advertised `<中文> · <English>` pattern by using extra middots inside the Chinese half: `仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading` and `真值引擎 · 只读 · Truth Engine — Read Only`. They are readable, but they are not the strict convention the docs/tests claim.
  Suggested fix: collapse each Chinese side into one phrase and reserve the outer middot for the Chinese/English split:
  `仅参考，非真值引擎实时读数 · advisory · not a live truth-engine reading`
  `真值引擎（只读） · Truth Engine — Read Only`
  Then update tests and inventory so they stop asserting the multi-middot forms as convention-correct.

- `NIT` — [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:209>), [workbench.html](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:215>), [test_workbench_e11_15e_chinese_first_bundle.py](</Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_e11_15e_chinese_first_bundle.py:106>)
  The trust-banner Chinese is understandable but not fully native. `这里"手动反馈"的含义` is awkward word order, and `仍然是权威` reads like a calque rather than engineer-facing Chinese.
  Suggested fix: use `此处“手动反馈”的含义 · What "manual feedback" means here:` and `真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍以真值引擎读数为准 · Truth engine readings ... remain authoritative.` If you touch that sentence, `不算 manual feedback` would also read better as `不属于“手动反馈”`.

I did not flag `身份 · Identity`, `工单 · Ticket`, `反馈模式 · Feedback Mode`, or `手动（仅参考）· Manual (advisory)`; those are acceptable register choices here. I also did not count `Kogami / Engineer` as a violation because E11-15e explicitly defers identifiers/proper nouns, unlike the untranslated feedback-mode tooltip.

Verification: `pytest -q tests/test_workbench_e11_15e_chinese_first_bundle.py` passed (`67 passed`).


