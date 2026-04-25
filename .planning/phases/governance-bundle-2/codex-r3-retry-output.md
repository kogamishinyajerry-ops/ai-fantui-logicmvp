2026-04-25T12:56:00.704190Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T12:56:00.704209Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc4b6-15c1-7a41-8434-fea12c1f5897
--------
user
You are reviewing governance bundle #2 R3-retry (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 58426cf on top of e259a42).

History:
- R1 (1f25bb5): CHANGES_REQUIRED — F1 BLOCKER tier-aware closure conflict, F2 IMPORTANT rollback divergence, F3 IMPORTANT trigger non-determinism
- R2 (419286b): R1 fixes applied. Codex R2 returned partial — F1/F2 partial (drift in E11-00-PLAN), F3 not resolved (drift in constitution + RETRO §6.2), + 1 NEW IMPORTANT (README §Purpose stale)
- R2-fix (e259a42): All R2 findings addressed across 4 docs (README + constitution + RETRO + E11-00-PLAN)
- R3 (process crashed mid-stream, no formal verdict; intermediate observations identified 2 residual drift in README §命令模板 + §Cost supersession note)
- R3-fix (58426cf, this PR): Both intermediate-observation drift addressed

R3-fix changes (1 file, 9+/9- lines):
1. README §命令模板 lines 73-81: Replaced "Tier-B (1 persona 默认 — P1 Junior FCS)" + "Tier-B 轮换" twin examples with single block using `PERSONA=` variable + comment chain pointing to PERSONA-ROTATION-STATE.md round-robin source-of-truth + append command.
2. README §Cost line 131: Removed "The earlier 'candidate §6.2 re-evaluate' framing is superseded — §6.3 is canonical." (Codex flagged the supersession sentence as itself drift — it kept the dead §6.2 string in the canonical spec.)

Files unchanged this round: .planning/constitution.md, .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md, .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md.

Your task: Issue formal R3 verdict on the bundle as it stands at 58426cf. Verify:

1. README §命令模板 now describes Tier-B per-sub-phase round-robin (no surviving "default P1 / owner override" mental model)
2. README §Cost / §Anti-bias / §Output convention / §Purpose all consistent with cross-sub-phase rotation rule (no mentions of dead §6.2 / "re-evaluate" / "default P1 + owner rotation" wording)
3. constitution.md §Codex Persona Pipeline Tier-Trigger and §Tier-trigger table fully match README §Invocation rule
4. RETRO-V61-054 §6.2 / §6.3 fully match constitution rollback semantics (3 actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7)
5. E11-00-PLAN §1, §3.6, §3.6.1, §6, §8, §9, §11 all tier-aware in alignment with new rule

Output format (verbatim):
```
VERDICT: APPROVE | CHANGES_REQUIRED
README §命令模板: [resolved | drift] — <≤2 lines>
README cross-section consistency (§Purpose / §Invocation / §Output / §Anti-bias / §Cost): [resolved | drift] — <≤2 lines>
constitution + README convergence: [resolved | drift] — <≤2 lines>
RETRO §6.2/§6.3 + constitution rollback convergence: [resolved | drift] — <≤2 lines>
E11-00-PLAN tier-aware: [resolved | drift] — <≤2 lines>
NEW_R3_FINDINGS:
- <none | severity + ≤2 line summary>
```

Be ruthless. If even one document still has stale wording, mark drift. If the rotation-state-file path appears different in different docs, flag it. If the counting command appears in README but not constitution, flag it (rule layer must be self-contained).

Reply only with structured output. No preamble.
codex
Reviewing PR #14 at `58426cf` as a correctness-only governance audit. I’m loading the repo’s review context and the five target documents, then I’ll check each requested convergence point against the current text with line-level evidence.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,240p' /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

 exited 1 in 0ms:
sed: /Users/Zhuanz/.codex/skills/gsd-code-review/SKILL.md: No such file or directory

exec
/bin/zsh -lc 'rg -n "LogicMVP|governance|constitution|RETRO-V61-054|E11-00-PLAN|README" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
49:# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
51:scope: Audit repo/GitHub/Notion drift, tighten source-of-truth framing, and hand off a governance-first Chinese execution package to Claude Code without silently turning analysis into code edits.
52:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
58:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)
62:- Claude Code, Opus 4.7, governance-first, repo 是代码真相, GitHub 是对外工程面, Notion 是控制中枢, docs/coordination, run_gsd_validation_suite.py, validate_notion_control_plane.py, gsd_notion_sync.py, DEFAULT_PAGES, default_plan, qa_report.md, 人工 GitHub 设置清单
68:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, single copy-paste prompt delivered for Claude Code)
78:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, factual framing tightened after Claude critique)
95:- In this repo, high-signal truth anchors for governance drift were `python3 tools/run_gsd_validation_suite.py --format json` and `python3 tools/validate_notion_control_plane.py --format json` plus direct reads of `README.md`, `.github/workflows/gsd-automation.yml`, `pyproject.toml`, `.planning/STATE.md`, `.planning/notion_control_plane.json`, and `tools/gsd_notion_sync.py` [Task 1]
96:- `docs/coordination/` is the right landing zone for a governance/transition package intended for Claude Code or another executor to consume directly [Task 1]
105:- Symptom: coordination docs stay internally inconsistent after a governance refresh -> cause: only `plan.md` and `dev_handoff.md` were checked while `qa_report.md` kept the older baseline text -> fix: review the full coordination-doc set together when baseline wording or control-plane truth changes [Task 1][Task 3]
109:# Task Group: AI FANTUI LogicMVP C919 E-TRAS reliability simulation candidates and adoption handoff
112:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s C919 E-TRAS workstation and candidate-handoff workflow, but branch names, commit SHAs, Notion pages, and demo URLs are checkout-specific.
118:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, candidate UI shipped on isolated branch after runtime fix)
128:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, Notion/GitHub handoff completed with pushed branch and final fix commit)
168:- AI Coding Assets, Context Asset Manager, Development Cockpit, 调整整个项目的开发文档、计划, 像游戏一样, 小日报, team agent架构, README.md, AGENTS.md, .planning/ROADMAP.md, .planning/PROJECT.md, project_state/handoff-docs-cockpit-roadmap.md
192:- when the user asked to "调整整个项目的开发文档、计划" -> future work should update the complete planning surface (`README.md`, `AGENTS.md`, `.planning/*`, and handoff docs), not only a README refresh [Task 1]
213:- Symptom: docs pass is too narrow -> cause: the user’s ask was a route-map to a cockpit product, not just README polish -> fix: create/update `PROJECT/ROADMAP/STATE` artifacts and handoff docs immediately when this repo gets "计划/文档调整" [Task 1]
304:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
310:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, useful when Notion MCP or Computer Use is unavailable)
320:- rollout_summaries/2026-04-18T16-09-41-mAqs-claude_official_auth_and_provider_routing_recovery.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/19/rollout-2026-04-19T00-09-41-019da15a-e528-7861-97cf-de68dd62dbf8.jsonl, updated_at=2026-04-19T03:01:02+00:00, thread_id=019da15a-e528-7861-97cf-de68dd62dbf8, partial recovery; auth still blocked by browser-login completion)
452:# Task Group: AI-Notebooklm V4.2 governance stabilization
455:applies_to: cwd=/Users/Zhuanz/AI-Notebooklm and isolated worktree `/Users/Zhuanz/AI-Notebooklm-v4-2-t1`; reuse_rule=safe for this repo’s governance/auth test stabilization, but branch names and local artifact cleanup are checkout-specific.
475:- DailyUploadQuota, NotebookCountCap, core/governance/quota_store.py, UPSERT, T4 T5 T6 T7 T8 T14, daily_limit=expected_total, concurrent accumulation
485:- slowapi, limits, principal.principal_id, Retry-After: 60, Rate limit exceeded: chat_requests, core/governance/rate_limit.py, request parameter literally named request, auth_disabled_falls_back_to_ip
527:- Symptom: new governance work starts on a dirty branch -> cause: existing branch already contains unrelated work -> fix: fork a clean worktree from `origin/main` and keep Step 1 schema work as its own commit [Task 1]
590:- Local completion was substantial in the V4.0 rollout: retrieval eval tooling, RRF tuning, staging/UAT runbooks, README updates, Notion artifact/task/review rows, and `210 passed` regression validation [Task 4]
629:- after the assessment, the user chose "演示工作台优先" and "削弱 Notion/治理面" -> future recommendations for this repo should narrow toward demo-first viability rather than governance-heavy productization [Task 1][Task 2]
644:- Symptom: the repo gets described as one coherent ready-to-demo product -> cause: multiple hot surfaces (`/learn`, Pro Workbench, governance/Notion, audit/reporting) were flattened into one storyline -> fix: choose a single demo narrative and explicitly demote the secondary surfaces [Task 1]
647:- Symptom: the executor drifts back into platform/governance breadth -> cause: the handoff did not make postponements explicit -> fix: name what is intentionally delayed, keep Notion/governance weight low, and anchor the work on 2-3 demo cases instead of full breadth [Task 2]
649:# Task Group: cfd-harness-unified governance closeout and planning gates
654:## Task 1: Close Phase 8 and reconcile stale governance evidence
702:# Task Group: Jerry AI CFD command protocol and Notion-centered governance
705:applies_to: cwd=/Users/Zhuanz/Documents/20260330 Jerry AI CFD Project; reuse_rule=safe for this repo’s command-proxy and Notion-governance workflow, but phase names and page IDs are repo-specific.
775:- The key repo-side state surfaces are `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `docs/governance/PROJECT_STATUS_BOARD.md`, and `docs/governance/CURRENT_PHASE_CHECKPOINT.md` [Task 2]
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
910:- the user twice said "排除Notion中枢管控的巧思设计，单论这个控制逻辑智能化" -> when writing materials, strip governance/control-tower framing if they ask for the core technical story only [Task 2]
920:- For this repo’s leadership narrative, the durable evidence sources are `docs/coordination/dev_handoff.md`, `docs/coordination/qa_report.md`, `docs/coordination/plan.md`, `README.md`, and `docs/demo_presenter_talk_track.md`, not Git history [Task 4]
934:# Task Group: AI ControlLogicMaster Notion control tower and freeze-signoff governance
937:applies_to: cwd=/Users/Zhuanz/20260402 AI ControlLogicMaster; reuse_rule=safe for this repo’s Notion/GSD/freeze-governance workflow, but page URLs, phase numbers, and freeze artifact names are checkout-specific.
960:## Task 3: Review final-freeze governance packages as read-only and block on stale routing text
964:- rollout_summaries/2026-04-07T14-48-14-t3g6-post_phase7_final_freeze_signoff_governance_planning_review.md (cwd=/Users/Zhuanz/20260402 AI ControlLogicMaster, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T22-48-14-019d686a-5f10-79f2-9918-ff5cdc98e6aa.jsonl, updated_at=2026-04-08T15:13:06+00:00, thread_id=019d686a-5f10-79f2-9918-ff5cdc98e6aa, initial rejection then accepted rerun after README/docs routing fix)
968:- independent planning review, do not write acceptance_audit_log.yaml, do not modify freeze_gate_status.yaml, accepted_for_review, freeze-complete, docs incomplete, README routing, docs/README.md, MILESTONE_BOARD.md
989:- POST_PHASE7_MANUAL_REVIEW_INTAKE_REQUEST.md, POST_PHASE7_MANUAL_REVIEW_INTAKE_REQUEST_REVIEW_INPUT.md, markdown-only, must not write manual intake state, must not be valid input to any CLI command, 50 files, acceptance_audit_log.yaml [], freeze-readiness rc=1, docs/README routing
996:- for freeze-signoff governance review, the user required a strict independent review with no writes to freeze artifacts -> treat this as review-only until the user explicitly changes scope [Task 3]
1001:- when choosing the next bounded governance move, the user wanted the "最小正确下一包" rather than a broad governance roadmap -> select the smallest legitimate package, especially when only docs/checklist completeness remains [Task 3][Task 4]
1009:- In freeze-governance review, README/docs/milestone-board routing is a real acceptance criterion; stale navigation can block acceptance even when substantive planning logic is correct [Task 3]
1012:- In this governance family, `freeze_gate_status.yaml` and historical approval YAML are effectively immutable unless the task explicitly authorizes touching them; integrity is often tracked by the unchanged SHA-256 hash [Task 3][Task 4]
1013:- The manual review intake request package in this repo is a non-executable artifact pair: `docs/POST_PHASE7_MANUAL_REVIEW_INTAKE_REQUEST.md` and `docs/POST_PHASE7_MANUAL_REVIEW_INTAKE_REQUEST_REVIEW_INPUT.md`, with README/docs routing updated so the next step is independent review rather than manual intake or freeze [Task 5]
1020:- Symptom: a governance review package seems technically sound but still should not be accepted -> cause: operator-facing docs still route users to the wrong gate -> fix: verify README/docs index/milestone-board navigation before acceptance [Task 3]
1023:- Symptom: a manual-review-intake packet accidentally starts behaving like an executable step -> cause: the request package, action review, and freeze flows were collapsed together -> fix: keep the packet markdown-only, keep `.aplh` state untouched, and re-read rendered README/docs routing after patching [Task 5]
1221:- rollout_summaries/2026-04-07T13-39-39-hXpB-p4_04_governance_engine.md (cwd=/Users/Zhuanz/Desktop/notion-cfd-harness, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-39-39-019d682b-91b4-7613-b247-7ab65a1724f7.jsonl, updated_at=2026-04-07T13:53:49+00:00, thread_id=019d682b-91b4-7613-b247-7ab65a1724f7, governance engine plus registry persistence fix)
1292:- The Phase 4 lifecycle contract is `register -> propagate -> govern -> sync`, and `MemoryNetwork.register_change()` returns structured outputs including the `UnitVersion`, `MemoryNode`, governance decision, propagation result, code mappings, and `PropagationEvent` [Task 4]
1303:- Symptom: governance or executable validation is slow or noisy -> cause: Matplotlib cache/font setup in the sandbox -> fix: set `MPLCONFIGDIR` to a writable temp path before running the full lifecycle tests [Task 4]
1707:- when the user asked "深度审查此项目，给我目前的项目评估报告" -> give an architecture/risk assessment grounded in actual runtime paths, not only README claims [Task 1]

codex
I found the repo memory hit and a narrow governance-review pattern: acceptance can still be blocked by stale operator-facing routing text. I’m now reading the actual review workflow guidance, then I’ll inspect the five docs at `58426cf` with line numbers rather than relying on history prose.
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
/bin/zsh -lc "nl -ba README.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	# Well Harness
     2	
     3	## Project Status: `main@433949d` · P43-03 DONE · 726 tests green (updated 2026-04-22)
     4	
     5	**Current work**: P43-02 Batch execution (P43-03 complete · P43-04 pending). See `.planning/STATE.md` for the current phase, `.planning/ROADMAP.md` for phase history.
     6	
     7	**Branch note**: Active development is on `main`. The `claude/c919-etras-frozen-v1-migration` branch carried the C919 E-TRAS frozen_v1 reference engine and has been merged. The original `main` was frozen at Milestone 9 (2026-04-15) after P0-P16; scope has since expanded through P43. LLM chat/P14/P15 removed from active code, see `archive/shelved/llm-features/SHELVED.md`.
     8	
     9	`well-harness` is an engineering workbench for aviation control logic — from requirements and specifications to runtime verification evidence. The core workflow is:
    10	
    11	`requirements / source material → spec clarification → adapter truth → playback → diagnosis → knowledge artifact → bundle/archive → traceability`
    12	
    13	The reference system is the C919 thrust reverser deploy control logic. The workbench currently covers:
    14	
    15	- adapter-backed control logic evaluation (logic 1 through 4)
    16	- playback simulation with throttle lever, SW1 / SW2 latch model, and plant feedback
    17	- diagnosis traces linking logic transitions to before/after condition evidence
    18	- knowledge artifact and workbench bundle generation for archiving and review
    19	- a deterministic demo layer (`well_harness demo`) for controlled live reasoning — not a full AI system
    20	- a CLI and local UI shell for engineering debugging and presenter walkthroughs
    21	
    22	The simplified plant model (TLS / PLS / VDT feedback) is an intentional first-cut for control sequencing. It is not a complete physical actuator model. The confirmed control truth lives in `controller.py` and is not modified by the demo or UI layers.
    23	
    24	## Architecture
    25	
    26	- `src/well_harness/models.py`
    27	  Shared dataclasses for pilot inputs, resolved inputs, plant state, outputs, traces, trace events, and logic explain data.
    28	- `src/well_harness/controller.py`
    29	  Pure deploy-logic evaluation for logic 1 through 4.
    30	- `src/well_harness/switches.py`
    31	  Interval-based SW1 / SW2 latch model driven by TRA.
    32	- `src/well_harness/plant.py`
    33	  Simplified deploy-side plant and sensor feedback model.
    34	- `src/well_harness/scenarios.py`
    35	  Built-in scenarios for nominal deploy and retract/reset checks.
    36	- `src/well_harness/runner.py`
    37	  Simulation loop that combines pilot command, switch model, controller, and plant.
    38	- `src/well_harness/cli.py`
    39	  CLI for running scenarios and printing readable timeline, events, or structured JSON traces.
    40	- `src/well_harness/demo.py`
    41	  Deterministic controlled-intent layer for demo-facing trigger, diagnosis, and dry-run proposal answers.
    42	- `src/well_harness/demo_server.py`
    43	  Standard-library local HTTP server and static UI shell for the demo reasoning layer.
    44	
    45	## Commands
    46	
    47	Run the built-in nominal deploy scenario:
    48	
    49	```bash
    50	PYTHONPATH=src python3 -m well_harness run nominal-deploy
    51	```
    52	
    53	Run the built-in retract/reset scenario:
    54	
    55	```bash
    56	PYTHONPATH=src python3 -m well_harness run retract-reset
    57	```
    58	
    59	Show the full state-transition event list for faster fault isolation:
    60	
    61	```bash
    62	PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --full
    63	```
    64	
    65	Show logic transition diagnoses with before / after explain deltas and window context:
    66	
    67	```bash
    68	PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --full
    69	```
    70	
    71	Filter the diagnosis view to one logic and emit machine-readable JSON:
    72	
    73	```bash
    74	PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json
    75	```
    76	
    77	Export the full structured trace as JSON:
    78	
    79	```bash
    80	PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json
    81	```
    82	
    83	All JSON views include deterministic schema metadata:
    84	
    85	```json
    86	{
    87	  "schema": {
    88	    "name": "well_harness.debug",
    89	    "schema_version": "1.0",
    90	    "view": "timeline",
    91	    "scenario_name": "nominal-deploy"
    92	  }
    93	}
    94	```
    95	
    96	Explain why one logic is true or false at a specific simulation tick:
    97	
    98	```bash
    99	PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8
   100	```
   101	
   102	The explain view selects the nearest trace row to `--time` and prints each condition with current value, comparison, threshold / target value, and pass state.
   103	
   104	Run the deterministic demo intent layer:
   105	
   106	```bash
   107	PYTHONPATH=src python3 -m well_harness demo "触发 SW1 会发生什么"
   108	PYTHONPATH=src python3 -m well_harness demo "触发 logic3 会发生什么"
   109	PYTHONPATH=src python3 -m well_harness demo "触发 VDT90 会发生什么"
   110	PYTHONPATH=src python3 -m well_harness demo "触发 THR_LOCK 会发生什么"
   111	PYTHONPATH=src python3 -m well_harness demo "为什么 SW1 还没触发"
   112	PYTHONPATH=src python3 -m well_harness demo "为什么 SW2 还没触发"
   113	PYTHONPATH=src python3 -m well_harness demo "为什么 TLS115 还没触发"
   114	PYTHONPATH=src python3 -m well_harness demo "为什么 logic1 还没满足"
   115	PYTHONPATH=src python3 -m well_harness demo "为什么 logic2 还没满足"
   116	PYTHONPATH=src python3 -m well_harness demo "为什么 logic3 还没满足"
   117	PYTHONPATH=src python3 -m well_harness demo "为什么 logic4 还没满足"
   118	PYTHONPATH=src python3 -m well_harness demo "logic4 和 throttle lock 有什么关系"
   119	PYTHONPATH=src python3 -m well_harness demo --format json "logic4 和 throttle lock 有什么关系"
   120	PYTHONPATH=src python3 -m well_harness demo "为什么 TLS unlocked 还没触发"
   121	PYTHONPATH=src python3 -m well_harness demo "为什么 540V 还没触发"
   122	PYTHONPATH=src python3 -m well_harness demo "为什么 VDT90 还没触发"
   123	PYTHONPATH=src python3 -m well_harness demo "为什么 THR_LOCK 还没释放"
   124	PYTHONPATH=src python3 -m well_harness demo "为什么 throttle lock 没释放"
   125	PYTHONPATH=src python3 -m well_harness demo "如果把 logic3 的 TRA 阈值从 -11.74 改成 -8，会发生什么"
   126	```
   127	
   128	The demo layer is a controlled reasoning surface, not a full natural-language AI system. It maps supported short prompts to deterministic `trigger_node`, `blocked_state`, `diagnose_problem`, `logic4_thr_lock_bridge`, or `propose_logic_change` answers using the built-in scenarios and simplified first-cut plant. The controlled trigger-node catalog covers the current chain nodes `SW1`, `logic1`, `TLS115`, `TLS unlocked`, `SW2`, `logic2`, `540V`, `logic3`, `EEC deploy`, `PLS power`, `PDU motor`, `VDT90`, `logic4`, and `THR_LOCK`; non-logic trigger answers include upstream dependency hints and a small `upstream_status` table that point back to existing `events`, `explain`, `diagnose`, and trace evidence, but they are not complete root-cause proofs. For `SW1` / `SW2`, the table reports observed TRA / switch-event trace evidence from the interval-triggered latch model, not a unique hardware contact point. Threshold-change prompts return a dry-run proposal report and do not modify `controller.py`.
   129	The controlled demo layer also supports a narrow blocked-state / pre-trigger comparison for prompts such as `为什么 SW1 还没触发`, `为什么 SW2 还没触发`, `为什么 TLS115 还没触发`, `为什么 logic1 还没满足`, `为什么 logic2 还没满足`, `为什么 logic3 还没满足`, `为什么 logic4 还没满足`, `为什么 TLS unlocked 还没触发`, `为什么 540V 还没触发`, `为什么 VDT90 还没触发`, and `为什么 THR_LOCK 还没释放`. Those answers are based on the built-in `nominal-deploy` checkpoint just before the node's first observed trigger, so they are deterministic evidence comparisons rather than full anomaly simulations or physical root-cause proofs. For `SW1` / `SW2`, the comparison still uses interval-triggered latch-model trace evidence rather than a unique hardware contact-point claim; for logic gates, the blocker table comes directly from the checkpoint row's `DeployController.explain(...)` conditions rather than a second copied rule set; for `logic4`, this means the answer stays tied to the checkpoint row's `deploy_90_percent_vdt` gate instead of inventing a separate throttle-lock truth; for `TLS unlocked`, it still uses simplified timer / sensor evidence.
   130	For `logic4` and `THR_LOCK`, the demo also has a small bridge summary such as `logic4 和 throttle lock 有什么关系`. It links the logic4 blocked-state checkpoint, the downstream `throttle_lock_release_cmd`, and the `5.0s` event window in one deterministic answer without replacing the separate blocked-state or diagnose views.
   131	Use `well_harness demo --format json "..."` when automation needs the same `DemoAnswer` fields as arrays; default `demo "..."` output remains the human-readable text format.
   132	Key demo answers are regression-protected by the lightweight fixture `tests/fixtures/demo_answer_asset_v1.json`; this is an executable test asset for stable prompt / intent / evidence fragments, not a formal JSON Schema.
   133	The demo JSON output is separately regression-protected by `tests/fixtures/demo_json_output_asset_v1.json`; this is also a lightweight executable fixture contract, not a formal JSON Schema.
   134	The demo JSON output structure is documented by `docs/json_schema/demo_answer_v1.schema.json`; that schema is the machine-readable field/type reference, while `tests/fixtures/demo_json_output_asset_v1.json` is the executable prompt/fragments regression contract.
   135	If `jsonschema` is installed locally, run `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_optional_jsonschema_validates_demo_json_payloads_when_installed` to validate real demo JSON payloads against `docs/json_schema/demo_answer_v1.schema.json`; without that optional package, the test explicitly skips and normal commands do not depend on it.
   136	For a non-unittest entrypoint to the same demo answer schema check, run `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`; it reuses `tests/fixtures/demo_json_output_asset_v1.json` and real `well_harness demo --format json` payloads, and prints a clear `SKIP` with a successful exit if `jsonschema` is unavailable.
   137	That validator defaults to human-readable text; for automation, run `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json` to emit top-level `status`, `schema_path`, `asset_path`, and per-prompt `results`.
   138	
   139	Start the local UI demo shell:
   140	
   141	```bash
   142	PYTHONPATH=src python3 -m well_harness.demo_server
   143	```
   144	
   145	Open the printed local URL to use the first-screen demo UI. The UI posts prompts to `POST /api/demo`, reuses the same deterministic `DemoAnswer` payload as `well_harness demo --format json`, highlights the fixed control chain, and keeps a raw JSON debug panel visible. It is a local UI shell for the controlled demo layer, not a full natural-language AI product or complete physical simulation.
   146	If you want the server to ask the standard-library browser launcher to open the URL after startup, run `PYTHONPATH=src python3 -m well_harness.demo_server --open`; this is only a launch convenience, not browser E2E automation.
   147	The current browser surface is tuned for a Chinese live demo: the first screen presents a compact `反推逻辑演示舱`, an interactive reverse-lever cockpit, a game-like `逻辑主板`, Chinese result labels, and a folded `原始 JSON 调试` inspector while preserving the existing `POST /api/demo` and `DemoAnswer` payload.
   148	The browser surface is arranged as a lever cockpit showcase: throttle lever, HUD, control chain, and current-result summary share the first-screen demo flow, while raw JSON is kept as a lower-priority debug inspector. The lever cockpit uses `POST /api/lever-snapshot` for a controlled pullback scrubber, supports a `manual_feedback_override` mode for `deploy_position_percent`, and keeps the original diagnosis Q&A in a frozen secondary drawer.
   149	The lever cockpit also includes a compact 条件面板 for `radio_altitude_ft`, `engine_running`, `aircraft_on_ground`, `reverser_inhibited`, `eec_enable`, `n1k`, `max_n1k_deploy_limit`, `feedback_mode`, and `deploy_position_percent`; `SW1 / SW2` still come from the existing switch model, and deploy / VDT feedback remains a folded simplified-plant diagnostic override rather than a new control truth.
   150	The UI includes a small loading / empty-prompt / API-error state and highlights logic / command subnodes such as `logic4`, `THR_LOCK`, `TLS115`, `540V`, `EEC`, `PLS`, and `PDU`; highlights show answer association, not a complete causal proof.
   151	Example prompt buttons expose a selected state, the control chain uses a narrow-screen scroll rail, and the raw JSON debug payload lives in an expandable panel.
   152	Example prompts are grouped by bridge / diagnose / trigger / proposal use, the prompt box supports `Cmd/Ctrl+Enter` without stealing normal Enter newlines, and the UI includes a compact help note about the controlled demo boundary.
   153	The UI also includes a small highlight explanation that names the `matched_node` / `target_logic` fields and the highlighted chain nodes; this explanation is answer association only, not a causal proof.
   154	The structured answer panel includes an `Answer sections` summary that counts the existing `DemoAnswer` arrays, marks empty sections, and lets each chip focus its matching answer section; arrow keys move between section chips without changing the demo JSON payload.
   155	
   156	For a lightweight presenter checklist before a demo, run:
   157	
   158	```bash
   159	PYTHONPATH=src python3 tools/demo_ui_handcheck.py
   160	```
   161	
   162	This helper prints the local UI start command, core prompts with guided expected observations, UI checkpoints, and boundary reminders; it is only a presenter aid, not browser E2E automation and not part of the formal GSD approval flow.
   163	For a shorter presenter script, run `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`; it prints concise callouts for the bridge / diagnose / trigger / proposal flow and remains a presenter aid, not browser automation or a new control-truth source.
   164	The one-page presenter talk track lives at `docs/demo_presenter_talk_track.md` and keeps the same presenter-only boundary.
   165	The UI section headers include matching presenter callout labels (`[Input]`, `[Chain]`, `[Highlight]`, `[Structured answer]`, `[Raw JSON]`) so the talk track maps directly to visible page regions.
   166	The UI also includes a screenshot-free presenter route strip (`[Input] -> [Chain] -> [Highlight] -> [Structured answer] -> [Raw JSON]`) as a visual guide for the talk track; it is not browser automation or a screenshot annotation tool.
   167	The first screen now also includes a clickable `Presenter Run Card` with the same bridge / diagnose / trigger / proposal order as the talk track; it reuses the existing prompt flow and `DemoAnswer` payload rather than inventing a new presenter-only surface.
   168	The lever cockpit also includes visible `演示场景预设` buttons for `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready`; they only refill the existing `POST /api/lever-snapshot` inputs and do not create a second state machine.
   169	The chain panel now also exposes a visible `状态图例 / truth boundary` strip so a live audience can read `Active / Blocked / Inactive` state colors and distinguish controller truth from simplified plant feedback without treating the color map as a causal proof.
   170	The lever `当前结论` card now also renders as fixed presenter reading rails for `Headline`, `Blocker`, and `Next step`; those three rows still come from the same lever snapshot payload instead of a second presenter-only explanation layer.
   171	The `结果摘要` card now also exposes a visible source note that distinguishes `POST /api/demo / DemoAnswer` from `POST /api/lever-snapshot`, while reminding the presenter that the visible panes still share one payload at a time.
   172	When the page is showing `DemoAnswer`, the lever `当前结论` rail now drops into a visible hold state instead of silently reusing the previous lever snapshot. That keeps the left-side rails aligned with the active payload source.
   173	The structured answer area also has a compact audience answer-field legend for explaining `intent`, `matched_node`, `evidence`, `risks`, and raw JSON as reading aids rather than a new schema or second answer payload.
   174	The legend is grouped with `Answer sections` as a compact answer guide so field meanings and section counts stay together without changing the `DemoAnswer` payload.
   175	On narrow screens, that compact answer guide stacks the legend and section chips with touch-friendly spacing while keeping the same payload and field semantics.
   176	That same presenter run card remains a manual presenter aid, not browser automation or an automatic readiness detector.
   177	For GitHub-verifiable demo-path confidence, run `python3 tools/demo_path_smoke.py` or `python3 tools/demo_path_smoke.py --format json`; it exercises the HTTP demo surface across the bridge prompt path, clamped extreme lever inputs, auto/manual mode switches, and one expected invalid-input error without relying on browser automation.
   178	
   179	The browser shell also now treats the newest prompt or lever interaction as the only response allowed to repaint the shared result surface, so a slower older request cannot overwrite a newer presenter action during rapid edits.
   180	That HTTP smoke suite also verifies the visible presenter presets for `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready`, so the most common live-demo jump points are covered by GitHub-verifiable evidence instead of manual browser-only confidence.
   181	It also sweeps the visible blocker toggles for engine, ground, reverser inhibit, and EEC enable, so the cockpit's key fast-toggle blocker states stay covered by the same automated evidence plane.
   182	Formal subjective review now happens through Notion AI Opus 4.6 using the Notion control tower plus the GitHub repo, not by citing local terminal file paths.
   183	Older repo notes about browser hand-checks remain historical presenter/archive material, not the current approval contract.
   184	
   185	Run the unit tests:
   186	
   187	```bash
   188	PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
   189	```
   190	
   191	Optionally run offline JSON Schema validation for all four JSON views if `jsonschema` is installed locally:
   192	
   193	```bash
   194	PYTHONPATH=src python3 -m unittest tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_contract_payloads_when_installed
   195	```
   196	
   197	Or run the standalone validation script:
   198	
   199	```bash
   200	PYTHONPATH=src python3 tools/validate_debug_json_schema.py
   201	```
   202	
   203	Or emit the validation result as machine-readable JSON for automation:
   204	
   205	```bash
   206	PYTHONPATH=src python3 tools/validate_debug_json_schema.py --format json
   207	```
   208	
   209	Run the standalone validation-report schema check:
   210	
   211	```bash
   212	PYTHONPATH=src python3 tools/validate_validation_report_schema.py
   213	```
   214	
   215	Emit the validation-report schema check result as machine-readable JSON:
   216	
   217	```bash
   218	PYTHONPATH=src python3 tools/validate_validation_report_schema.py --format json
   219	```
   220	

exec
/bin/zsh -lc 'git rev-parse --short HEAD && git status --short && git branch --show-current' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
58426cf
?? .planning/phases/governance-bundle-2/
feat/governance-bundle-2-persona-tier-trigger-20260425

codex
The root `README.md` is not the governance bundle the user described, so I’m switching to the actual bundle artifacts and checking the current branch tree for the README/constitution/RETRO/E11 files referenced by the review brief.
exec
/bin/zsh -lc "rg --files | rg 'README|constitution|RETRO-V61-054|E11-00-PLAN|PERSONA-ROTATION-STATE|governance-bundle-2'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
README.md
runs/workbench_e2e_20260425T040608Z/README.md
tickets/README.md
tests/fixtures/p43_spike/real_pdf_happy_path/README.md
data/proposals/README.md
templates/new_system/README.md
docs/onboarding/README.md
docs/architecture/constitution-v2.md

exec
/bin/zsh -lc "find .planning -maxdepth 4 -type f | sort | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/ISSUES.md
.planning/PROJECT.md
.planning/ROADMAP.md
.planning/STATE.md
.planning/V2_OPEN_QUESTIONS.md
.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md
.planning/audit/P31-orphan-4474505-audit.md
.planning/audit/bundles/README.md
.planning/audit/bundles/p31-orphan-triage.bundle
.planning/audit/bundles/p32-provenance-backfill-README.md
.planning/audit/bundles/p32-provenance-backfill.bundle
.planning/codebase/ARCHITECTURE.md
.planning/codebase/CONCERNS.md
.planning/codebase/CONVENTIONS.md
.planning/codebase/INTEGRATIONS.md
.planning/codebase/STACK.md
.planning/codebase/TESTING.md
.planning/codex_personas/P1-junior-fcs.md
.planning/codex_personas/P2-senior-fcs.md
.planning/codex_personas/P3-demo-presenter.md
.planning/codex_personas/P4-qa-vv.md
.planning/codex_personas/P5-apps-engineer.md
.planning/codex_personas/README.md
.planning/config.json
.planning/constitution.md
.planning/notion_control_plane.json
.planning/phases/02-p15-pipeline-integration/.gitkeep
.planning/phases/04-elevate-cockpit-demo-to-presenter-ready/.gitkeep
.planning/phases/05-demo-polish-and-edge-case-hardening/05-01-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-01-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-02-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-02-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-03-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-03-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-04-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-04-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-05-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-05-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-06-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-06-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-07-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-07-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-08-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-08-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-09-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-09-SUMMARY.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-10-PLAN.md
.planning/phases/05-demo-polish-and-edge-case-hardening/05-10-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-01-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-01-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-02-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-02-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-03-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-03-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-04-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-04-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-05-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-05-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-06-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-06-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-07-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-07-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-08-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-08-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-09-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-09-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-10-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-10-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-11-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-11-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-12-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-12-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-13-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-13-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-14-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-14-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-15-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-15-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-16-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-16-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-17-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-17-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-18-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-18-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-19-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-19-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-20-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-20-SUMMARY.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-21-PLAN.md
.planning/phases/06-reconcile-control-tower-and-freeze-demo-packet/06-21-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-01-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-01-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-02-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-02-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-03-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-03-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-04-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-04-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-05-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-05-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-06-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-06-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-07-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-07-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-08-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-08-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-09-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-09-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-10-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-10-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-11-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-11-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-12-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-12-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-13-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-13-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-14-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-14-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-15-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-15-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-16-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-16-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-17-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-17-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-18-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-18-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-19-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-19-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-20-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-20-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-21-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-21-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-22-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-22-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-23-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-23-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-24-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-24-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-25-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-25-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-26-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-26-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-27-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-27-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-28-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-28-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-29-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-29-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-30-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-30-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-31-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-31-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-32-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-32-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-33-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-33-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-34-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-34-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-35-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-35-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-36-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-36-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-37-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-37-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-38-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-38-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-39-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-39-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-40-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-40-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-41-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-41-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-42-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-42-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-43-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-43-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-44-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-44-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-45-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-45-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-46-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-46-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-47-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-47-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-48-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-48-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-49-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-49-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-50-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-50-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-51-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-51-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-52-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-52-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-53-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-53-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-54-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-54-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-55-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-55-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-56-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-56-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-57-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-57-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-58-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-58-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-59-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-59-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-60-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-60-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-61-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-61-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-62-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-62-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-63-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-63-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-64-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-64-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-65-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-65-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-66-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-66-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-67-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-67-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-68-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-68-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-69-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-69-SUMMARY.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-70-PLAN.md
.planning/phases/07-build-a-spec-driven-control-analysis-workbench/07-70-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-01-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-01-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-02-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-02-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-03-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-03-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-04-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-04-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-05-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-05-SUMMARY.md
.planning/phases/08-runtime-generalization-proof/08-06-PLAN.md
.planning/phases/08-runtime-generalization-proof/08-06-SUMMARY.md
.planning/phases/09-automation-hardening-evidence-pipeline/09-01-PLAN.md
.planning/phases/09-automation-hardening-evidence-pipeline/09-02-PLAN.md
.planning/phases/09-automation-hardening-evidence-pipeline/09-03-AUDIT.md
.planning/phases/09-automation-hardening-evidence-pipeline/09-03-PLAN.md
.planning/phases/10-second-system-runtime-pipeline/10-01-PLAN.md
.planning/phases/E06-workbench-shell/E06-00-PLAN.md
.planning/phases/E06-workbench-shell/E06-05-CLOSURE.md
.planning/phases/E07-canvas-annotations/E07-00-PLAN.md
.planning/phases/E07-canvas-annotations/E07-05-CLOSURE.md
.planning/phases/E08-approval-center/E08-00-PLAN.md
.planning/phases/E08-approval-center/E08-05-CLOSURE.md
.planning/phases/E09-prompt-ticket-auth/E09-00-PLAN.md
.planning/phases/E09-prompt-ticket-auth/E09-05-CLOSURE.md
.planning/phases/E10-pr-review-close-loop/E10-00-PLAN.md
.planning/phases/E10-pr-review-close-loop/E10-05-CLOSURE.md
.planning/phases/E11-workbench-engineer-first-ux/.gitignore
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
.planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md

exec
/bin/zsh -lc "find .planning -path '*RETRO-V61-054*' -o -path '*governance-bundle-2*' | sort" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/governance-bundle-2
.planning/phases/governance-bundle-2/codex-r2-output.md
.planning/phases/governance-bundle-2/codex-r2-prompt.txt
.planning/phases/governance-bundle-2/codex-r3-output.md
.planning/phases/governance-bundle-2/codex-r3-prompt.txt
.planning/phases/governance-bundle-2/codex-r3-retry-output.md
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md

exec
/bin/zsh -lc 'rg -n "Tier-B|default P1|owner override|re-evaluate|PERSONA-ROTATION-STATE|round-robin|append command|命令模板|Anti-bias|Output convention|Purpose|Invocation rule|tier-trigger|rollback|successor RETRO|Opus 4.7" README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md .planning/phases/governance-bundle-2 2>/dev/null' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:1:# RETRO-V61-054 — UI-COPY-PROBE birth (E11-02 4-round arc + Opus 4.7 root-cause)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:3:> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:18:Opus 4.7 异步会话 (Notion @Opus 4.7, 2026-04-25) returned a 3-layer causal stack and a complete v2.3 §UI-COPY-PROBE rule. This retro logs the arc, the diagnosis, and the legislative output.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:43:## 2. Opus 4.7 异步根因诊断 (≤200 字)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:45:> Verbatim from Notion @Opus 4.7 session, 2026-04-25:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:80:**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:123:Opus 4.7 §1 strategic review (2026-04-25) set E11-09 dual-h1 fix as the **leading indicator** for whether v2.3 UI-COPY-PROBE has been amortized. Decision rule:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:129:| ≥ 4 轮 | governance 失效 | Opus 4.7 再介入诊断 |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:142:### 6.2 governance bundle #2 — persona pipeline tier-trigger
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:**
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:153:- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:165:2. Open a successor RETRO-V61-* documenting the failed amortization
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:166:3. Re-engage Opus 4.7 strategic review
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:200:- Opus 4.7 异步会话 transcript: Notion `@Opus 4.7` session 2026-04-25 (内部链接，本仓库不留 binary copy)
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:3:> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:106:| **E11-13** | manual_feedback_override **trust-affordance 修复（UI/可视化层）** — 加警示 banner + 模式标识 chip + 失谐告警，让用户*看起来不再越权*。**不是** authority-chain breach 修复（873 + adversarial 8/8 已证 truth-engine 实际未被越权），而是 UI affordance 让用户对真值失去信任的"可视污染"修复。Opus 4.7 (2026-04-25) reframe；详见 §3.5。 | E11-01（P2-1 Reading B locked） | 不 |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:120:## 3.5 执行排序（Opus 4.7 strategic input · 2026-04-25）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:122:> 数据源：Notion @Opus 4.7 异步会话，2026-04-25。审查范围 = E11-02 + v2.3 governance bundle 落地后的 strategic review。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:131:**逐项理由**（Opus 4.7 verbatim）：
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:140:### Opus 4.7 拒绝的备选
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:147:不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:153:> Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:161:| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:168:**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:178:- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:188:## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:221:**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:233:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:243:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:259:5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:265:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:293:**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:345:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/constitution.md:3:> **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append + governance bundle #2 persona tier-trigger amortization)
.planning/constitution.md:9:> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:125:Between 2026-04-15 and 2026-04-18, under the v4.0 Extended Autonomy Mode then-in-force, **14 Phases (P17 → P30) landed above the freeze line**, each individually self-signed by the Executor (Codex / MiniMax-2.7 / Claude Code Opus 4.7) and accepted by Kogami through point-Gate decisions (`GATE-P23-CLOSURE: Approved`, `GATE-P24-CLOSURE: Approved`, etc.). These Gate approvals collectively satisfied Resume Criterion #1 「产品方向决策」 — Kogami's on-the-record directives to continue with 立项 demo hardening, co-development kit, then pitch script rehearsal constitute the required 产品方向 evidence.
.planning/constitution.md:132:- **Claude App Opus 4.7 (Solo Executor, v5.2):** solo-signed 2026-04-20 via `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`
.planning/constitution.md:144:- **v3.0 双 Opus (2026-04-xx → 2026-04-17):** Claude Code Opus 4.7 as Executor; Notion AI Opus 4.7 as independent Gate reviewer. Retired when v4.0 Extended Autonomy allowed Executor self-signing.
.planning/constitution.md:147:- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
.planning/constitution.md:150:- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。
.planning/constitution.md:151:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/constitution.md:175:Every commit by Claude App Opus 4.7 under v5.2 must include the trailer:
.planning/constitution.md:184:Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD
.planning/constitution.md:329:- Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
.planning/constitution.md:334:**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/constitution.md:374:3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:1:You are reviewing governance bundle #2 R3 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit e259a42 on top of 419286b).
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:5:- F2 partial: E11-00-PLAN:182 collapsed rollback to 2 actions, not RETRO §6.3's 3 actions
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:7:- NEW IMPORTANT: README:9 §Purpose said "pipeline ensures inter-persona finding uniqueness", false for Tier-B
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:8:- NIT: PERSONA-ROTATION-STATE.md not created (acceptable on first Tier-B sub-phase)
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:11:1. F1 fix: Updated E11-00-PLAN §1 success criterion (Tier-A=5/5; Tier-B=1/1 + rotation), §6 Required output split tier-aware (within-PR uniqueness Tier-A only), §6 aggregator Tier-A only / Tier-B = single verdict file, §8 verification table tier-aware, §9 closure #3 tier-aware, §11 trailer tier-aware.
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:12:2. F2 fix: E11-00-PLAN:182 reproduced canonical RETRO §6.3 verbatim — 3 actions (rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7) + header "canonical = RETRO §6.3, constitution §Codex Persona Pipeline Tier-Trigger 引用".
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:13:3. F3 fix: constitution.md:343 + RETRO §6.2 line 148 both updated to cross-sub-phase round-robin P1→P2→P3→P4→P5→P1, default start P1, state file pointer, "no consecutive same persona". constitution.md additionally inlines the `git diff --stat` counting command so the canonical rule layer is self-contained.
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:14:4. NEW fix: README §Purpose split into Tier-A (within-PR uniqueness) + Tier-B (N/A, delegated to Surface Inventory + cross-sub-phase rotation + RETRO §6.3 rollback).
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:24:- Is rollback semantics now identical (3 actions verbatim) across constitution / RETRO §6.3 / E11-00-PLAN:182 / README §Cost? (no surviving 2-step or "re-evaluate" wording)
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:25:- Is rotation rule now identical (cross-sub-phase round-robin) across all 4 docs? (no surviving "same sub-phase no repeat" or "default P1 + owner rotation")
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:26:- Does §1 / §6 / §8 / §9 / §11 in E11-00-PLAN correctly distinguish Tier-A from Tier-B closure semantics?
.planning/phases/governance-bundle-2/codex-r3-prompt.txt:27:- Does §Purpose in README accurately describe what Tier-B inherits vs what Tier-A inherits, without overpromising uniqueness?
.planning/phases/governance-bundle-2/codex-r2-output.md:16:You are reviewing governance bundle #2 R2 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 419286b on top of 1f25bb5).
.planning/phases/governance-bundle-2/codex-r2-output.md:19:- F1 BLOCKER: tier-B "1 persona" conflicts with §Output convention (5 verdicts assumed) + §Anti-bias safeguard (uniqueness check impossible) + E11-00-PLAN closure
.planning/phases/governance-bundle-2/codex-r2-output.md:20:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-output.md:21:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
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
.planning/phases/governance-bundle-2/codex-r2-output.md:219:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:80:**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。
.planning/phases/governance-bundle-2/codex-r2-output.md:222:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/phases/governance-bundle-2/codex-r2-output.md:225:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r2-output.md:227:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r2-output.md:229:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/phases/governance-bundle-2/codex-r2-output.md:230:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r2-output.md:231:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/phases/governance-bundle-2/codex-r2-output.md:232:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r2-output.md:240:.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:246:.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:247:.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:248:.planning/codex_personas/README.md:78:## Output convention
.planning/phases/governance-bundle-2/codex-r2-output.md:251:.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:253:.planning/codex_personas/README.md:98:- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:255:.planning/codex_personas/README.md:102:## Anti-bias safeguard
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
.planning/phases/governance-bundle-2/codex-r2-output.md:290: > Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r2-output.md:294: ## Purpose
.planning/phases/governance-bundle-2/codex-r2-output.md:312: > **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r2-output.md:322:+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:345: ### 命令模板
.planning/phases/governance-bundle-2/codex-r2-output.md:356: # Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:361: # Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:367: ## Output convention
.planning/phases/governance-bundle-2/codex-r2-output.md:381:+### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:388:+- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:392: ## Anti-bias safeguard
.planning/phases/governance-bundle-2/codex-r2-output.md:400:+**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:403:+3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:407: **Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r2-output.md:411: **Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r2-output.md:413: - Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:416:-If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce post-merge defects in user-facing copy, re-evaluate whether tier-trigger conditions are too lax (RETRO-V61-054 §6.2 candidate trigger).
.planning/phases/governance-bundle-2/codex-r2-output.md:417:+If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:473: - Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
.planning/phases/governance-bundle-2/codex-r2-output.md:478: **前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/phases/governance-bundle-2/codex-r2-output.md:487: | 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:501: **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:503:-**回滚条件：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE 失效条件被触发） → 自动回滚到 5-persona 默认 + 入 RETRO-V61-054 §6.2 候选触发位置。
.planning/phases/governance-bundle-2/codex-r2-output.md:504:+**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:506:+1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:508:+3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/phases/governance-bundle-2/codex-r2-output.md:546:The first pass already shows one likely coherence problem: `README.md` was updated, but `constitution.md` still appears to keep the old Tier-B selector text in the rule table. I’m opening the exact sections with line numbers and checking whether the rollback canon and the new rotation-state mechanism are actually enforceable in-tree.
.planning/phases/governance-bundle-2/codex-r2-output.md:556:   142	### 6.2 governance bundle #2 — persona pipeline tier-trigger
.planning/phases/governance-bundle-2/codex-r2-output.md:560:   146	**5-persona pipeline → tier-trigger:**
.planning/phases/governance-bundle-2/codex-r2-output.md:562:   148	- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r2-output.md:567:   153	- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
.planning/phases/governance-bundle-2/codex-r2-output.md:577:   163	If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r2-output.md:579:   165	2. Open a successor RETRO-V61-* documenting the failed amortization
.planning/phases/governance-bundle-2/codex-r2-output.md:580:   166	3. Re-engage Opus 4.7 strategic review
.planning/phases/governance-bundle-2/codex-r2-output.md:584:   170	- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/phases/governance-bundle-2/codex-r2-output.md:585:   171	- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r2-output.md:586:   172	- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/phases/governance-bundle-2/codex-r2-output.md:588:   174	- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r2-output.md:593:   334	**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/phases/governance-bundle-2/codex-r2-output.md:602:   343	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:616:   357	**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:618:   359	**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:620:   361	1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:622:   363	3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/phases/governance-bundle-2/codex-r2-output.md:636:     3	> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r2-output.md:640:     7	## Purpose
.planning/phases/governance-bundle-2/codex-r2-output.md:658:    25	> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r2-output.md:667:    34	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:681:    48	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:689:    56	### 命令模板
.planning/phases/governance-bundle-2/codex-r2-output.md:700:    67	# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:705:    72	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:711:    78	## Output convention
.planning/phases/governance-bundle-2/codex-r2-output.md:724:    91	### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:731:    98	- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r2-output.md:733:   100	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:735:   102	## Anti-bias safeguard
.planning/phases/governance-bundle-2/codex-r2-output.md:742:   109	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:743:   110	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:745:   112	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:749:   116	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r2-output.md:753:   120	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r2-output.md:755:   122	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:758:   125	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:761:/bin/zsh -lc "rg -n \"§6\\.2|§6\\.3|rollback|Tier-B|PERSONA-ROTATION-STATE|copy_diff_lines|git diff --stat\" .planning" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:763:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/phases/governance-bundle-2/codex-r2-output.md:766:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r2-output.md:767:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r2-output.md:768:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r2-output.md:769:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r2-output.md:770:.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r2-output.md:771:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:772:.planning/constitution.md:357:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:773:.planning/constitution.md:359:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:774:.planning/constitution.md:361:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:776:.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:779:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:780:.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:781:.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:782:.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:783:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:784:.planning/codex_personas/README.md:109:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:785:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:786:.planning/codex_personas/README.md:112:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:787:.planning/codex_personas/README.md:122:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:788:.planning/codex_personas/README.md:125:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:789:.planning/phases/P43-control-logic-workbench/P43-00-PLAN.md:248:- **Side-effect ordering（v3 新补）**：`final_approve` event 触发 side-effect 序：① localStorage state → APPROVING · ② server-side adapter emit + registry row append（原子）· ③ `archive_workbench_bundle` manifest append · ④ localStorage state → APPROVED。任何一步失败 · 回退到 ① 前状态 · 上报 error taxonomy `partial_approve_rollback`
.planning/phases/governance-bundle-2/codex-r2-output.md:790:.planning/phases/governance-bundle-2/codex-r2-output.md:20:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-output.md:791:.planning/phases/governance-bundle-2/codex-r2-output.md:21:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
.planning/phases/governance-bundle-2/codex-r2-output.md:793:.planning/phases/governance-bundle-2/codex-r2-output.md:29:1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
.planning/phases/governance-bundle-2/codex-r2-output.md:794:.planning/phases/governance-bundle-2/codex-r2-output.md:30:2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
.planning/phases/governance-bundle-2/codex-r2-output.md:795:.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:796:.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:797:.planning/phases/governance-bundle-2/codex-r2-output.md:49:Reviewing the R2 governance bundle as a correctness-only pass. I’m checking the cited files plus cross-doc references for `§6.2`, `§6.3`, rollback, Tier-A/Tier-B output rules, and the new trigger/rotation definitions before I issue the verdict.
.planning/phases/governance-bundle-2/codex-r2-output.md:798:.planning/phases/governance-bundle-2/codex-r2-output.md:51:/bin/zsh -lc "rg -n \"ai-fantui-logicmvp|LogicMVP|governance bundle|persona|rollback|RETRO-V61-054|§6\\.3|§6\\.2\" /Users/Zhuanz/.codex/memories/MEMORY.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:799:.planning/phases/governance-bundle-2/codex-r2-output.md:67:542:- rollout_summaries/2026-04-15T09-02-39-gtWf-notion_v3_stabilization_s15a_s16a_s16b_opus_escalation.md (cwd=/Users/Zhuanz/AI-Notebooklm, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/15/rollout-2026-04-15T17-02-39-019d9060-d7f8-7841-b99d-96cd4b18ce5f.jsonl, updated_at=2026-04-15T10:23:11+00:00, thread_id=019d9060-d7f8-7841-b99d-96cd4b18ce5f, per-space scoping and rollback baseline with Opus escalation boundary)
.planning/phases/governance-bundle-2/codex-r2-output.md:800:.planning/phases/governance-bundle-2/codex-r2-output.md:68:546:- ReviewHold, Opus 4.6, ParameterRegistry, AntiHallucinationGateway, space_id, rollback, .gitignore, draft PR, core/storage/space_resolver.py, core/llm/client.py
.planning/phases/governance-bundle-2/codex-r2-output.md:801:.planning/phases/governance-bundle-2/codex-r2-output.md:212:I’ve got the repo context and I’m staying in read-only review mode. Next I’m diffing `1f25bb5..419286b` and grepping the governance docs for Tier-A/Tier-B, rollback, `§6.2`/`§6.3`, the copy-count command, and rotation-state references to see whether the fixes actually converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:802:.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:803:.planning/phases/governance-bundle-2/codex-r2-output.md:225:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r2-output.md:804:.planning/phases/governance-bundle-2/codex-r2-output.md:227:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r2-output.md:805:.planning/phases/governance-bundle-2/codex-r2-output.md:230:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r2-output.md:806:.planning/phases/governance-bundle-2/codex-r2-output.md:232:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r2-output.md:807:.planning/phases/governance-bundle-2/codex-r2-output.md:240:.planning/codex_personas/README.md:34:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:810:.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:811:.planning/phases/governance-bundle-2/codex-r2-output.md:246:.planning/codex_personas/README.md:67:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:812:.planning/phases/governance-bundle-2/codex-r2-output.md:247:.planning/codex_personas/README.md:72:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:813:.planning/phases/governance-bundle-2/codex-r2-output.md:251:.planning/codex_personas/README.md:91:### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:814:.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:815:.planning/phases/governance-bundle-2/codex-r2-output.md:257:.planning/codex_personas/README.md:109:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:816:.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:817:.planning/phases/governance-bundle-2/codex-r2-output.md:260:.planning/codex_personas/README.md:112:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:818:.planning/phases/governance-bundle-2/codex-r2-output.md:262:.planning/codex_personas/README.md:122:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:819:.planning/phases/governance-bundle-2/codex-r2-output.md:264:.planning/codex_personas/README.md:125:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:820:.planning/phases/governance-bundle-2/codex-r2-output.md:265:.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r2-output.md:821:.planning/phases/governance-bundle-2/codex-r2-output.md:272:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:822:.planning/phases/governance-bundle-2/codex-r2-output.md:275:.planning/constitution.md:357:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:823:.planning/phases/governance-bundle-2/codex-r2-output.md:276:.planning/constitution.md:359:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:824:.planning/phases/governance-bundle-2/codex-r2-output.md:277:.planning/constitution.md:361:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:826:.planning/phases/governance-bundle-2/codex-r2-output.md:322:+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r2-output.md:829:.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:830:.planning/phases/governance-bundle-2/codex-r2-output.md:356: # Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r2-output.md:831:.planning/phases/governance-bundle-2/codex-r2-output.md:361: # Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r2-output.md:832:.planning/phases/governance-bundle-2/codex-r2-output.md:381:+### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r2-output.md:833:.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:834:.planning/phases/governance-bundle-2/codex-r2-output.md:400:+**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r2-output.md:835:.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:836:.planning/phases/governance-bundle-2/codex-r2-output.md:403:+3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r2-output.md:837:.planning/phases/governance-bundle-2/codex-r2-output.md:413: - Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r2-output.md:838:.planning/phases/governance-bundle-2/codex-r2-output.md:416:-If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce post-merge defects in user-facing copy, re-evaluate whether tier-trigger conditions are too lax (RETRO-V61-054 §6.2 candidate trigger).
.planning/phases/governance-bundle-2/codex-r2-output.md:839:.planning/phases/governance-bundle-2/codex-r2-output.md:417:+If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-output.md:840:.planning/phases/governance-bundle-2/codex-r2-output.md:487: | 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r2-output.md:841:.planning/phases/governance-bundle-2/codex-r2-output.md:501: **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r2-output.md:842:.planning/phases/governance-bundle-2/codex-r2-output.md:503:-**回滚条件：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE 失效条件被触发） → 自动回滚到 5-persona 默认 + 入 RETRO-V61-054 §6.2 候选触发位置。
.planning/phases/governance-bundle-2/codex-r2-output.md:843:.planning/phases/governance-bundle-2/codex-r2-output.md:504:+**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r2-output.md:844:.planning/phases/governance-bundle-2/codex-r2-output.md:506:+1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r2-output.md:846:.planning/phases/governance-bundle-2/codex-r2-output.md:546:The first pass already shows one likely coherence problem: `README.md` was updated, but `constitution.md` still appears to keep the old Tier-B selector text in the rule table. I’m opening the exact sections with line numbers and checking whether the rollback canon and the new rotation-state mechanism are actually enforceable in-tree.
.planning/phases/governance-bundle-2/codex-r2-output.md:847:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:5:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-output.md:848:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:6:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
.planning/phases/governance-bundle-2/codex-r2-output.md:850:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:14:1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
.planning/phases/governance-bundle-2/codex-r2-output.md:851:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:15:2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
.planning/phases/governance-bundle-2/codex-r2-output.md:852:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:853:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:860:/bin/zsh -lc 'rg -n "persona|Aggregator|unique|uniqueness|5 verdict|5 persona|Tier-A|Tier-B|closure|phase-CLOSURE|E11-04-PERSONA-REVIEW-RESULTS" .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:868:147:不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
.planning/phases/governance-bundle-2/codex-r2-output.md:869:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/governance-bundle-2/codex-r2-output.md:871:163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/governance-bundle-2/codex-r2-output.md:874:178:- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/governance-bundle-2/codex-r2-output.md:876:182:**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/phases/governance-bundle-2/codex-r2-output.md:880:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) 加 anti-bias safeguard：每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding，否则 review 不算 valid（pipeline 强制项）。结论：bias 风险存在但已通过 distinct context + cross-persona uniqueness 要求 mitigated。
.planning/phases/governance-bundle-2/codex-r2-output.md:881:221:**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
.planning/phases/governance-bundle-2/codex-r2-output.md:882:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/governance-bundle-2/codex-r2-output.md:883:233:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/governance-bundle-2/codex-r2-output.md:891:314:3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
.planning/phases/governance-bundle-2/codex-r2-output.md:898:   161	| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
.planning/phases/governance-bundle-2/codex-r2-output.md:900:   163	**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/governance-bundle-2/codex-r2-output.md:905:   168	**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
.planning/phases/governance-bundle-2/codex-r2-output.md:915:   178	- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/governance-bundle-2/codex-r2-output.md:919:   182	**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/phases/governance-bundle-2/codex-r2-output.md:925:   188	## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
.planning/phases/governance-bundle-2/codex-r2-output.md:950:/bin/zsh -lc "find .planning/phases -name 'PERSONA-ROTATION-STATE.md' -print" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:966:   257	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
.planning/phases/governance-bundle-2/codex-r2-output.md:999:   290	**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
.planning/phases/governance-bundle-2/codex-r2-output.md:1023:   314	3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
.planning/phases/governance-bundle-2/codex-r2-output.md:1034:     3	> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r2-output.md:1064:/bin/zsh -lc 'rg -n "copy_diff_lines|PERSONA-ROTATION-STATE|round-robin|discarded and the full 5-persona|re-executes|Tier-B.*upgrade|upgrade.*Tier-A" .planning' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:1066:.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:1067:.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:1068:.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:1070:.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1071:.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1072:.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1074:.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1075:.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1076:.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1078:.planning/phases/governance-bundle-2/codex-r2-output.md:681:    48	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1079:.planning/phases/governance-bundle-2/codex-r2-output.md:733:   100	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1080:.planning/phases/governance-bundle-2/codex-r2-output.md:743:   110	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1081:.planning/phases/governance-bundle-2/codex-r2-output.md:761:/bin/zsh -lc "rg -n \"§6\\.2|§6\\.3|rollback|Tier-B|PERSONA-ROTATION-STATE|copy_diff_lines|git diff --stat\" .planning" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:1083:.planning/phases/governance-bundle-2/codex-r2-output.md:779:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1084:.planning/phases/governance-bundle-2/codex-r2-output.md:783:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1085:.planning/phases/governance-bundle-2/codex-r2-output.md:785:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1086:.planning/phases/governance-bundle-2/codex-r2-output.md:795:.planning/phases/governance-bundle-2/codex-r2-output.md:31:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:1087:.planning/phases/governance-bundle-2/codex-r2-output.md:796:.planning/phases/governance-bundle-2/codex-r2-output.md:45:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:1088:.planning/phases/governance-bundle-2/codex-r2-output.md:802:.planning/phases/governance-bundle-2/codex-r2-output.md:214:/bin/zsh -lc "rg -n \"Tier-A|Tier-B|Output convention|Anti-bias|uniqueness|rollback|§6\\.2|§6\\.3|copy_diff_lines|git diff --stat|PERSONA-ROTATION-STATE|round-robin|scope-expands|discarded|aggregator|Surface Inventory|same persona|sub-phase|P1->P2->P3->P4->P5->P1\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:1090:.planning/phases/governance-bundle-2/codex-r2-output.md:810:.planning/phases/governance-bundle-2/codex-r2-output.md:243:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1091:.planning/phases/governance-bundle-2/codex-r2-output.md:814:.planning/phases/governance-bundle-2/codex-r2-output.md:254:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1092:.planning/phases/governance-bundle-2/codex-r2-output.md:816:.planning/phases/governance-bundle-2/codex-r2-output.md:258:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1094:.planning/phases/governance-bundle-2/codex-r2-output.md:829:.planning/phases/governance-bundle-2/codex-r2-output.md:337:+**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1095:.planning/phases/governance-bundle-2/codex-r2-output.md:833:.planning/phases/governance-bundle-2/codex-r2-output.md:390:+If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1096:.planning/phases/governance-bundle-2/codex-r2-output.md:835:.planning/phases/governance-bundle-2/codex-r2-output.md:401:+1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1097:.planning/phases/governance-bundle-2/codex-r2-output.md:852:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:1098:.planning/phases/governance-bundle-2/codex-r2-output.md:853:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:1099:.planning/phases/governance-bundle-2/codex-r2-output.md:950:/bin/zsh -lc "find .planning/phases -name 'PERSONA-ROTATION-STATE.md' -print" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r2-output.md:1100:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-output.md:1101:.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r2-output.md:1103:.planning/codex_personas/README.md:48:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r2-output.md:1104:.planning/codex_personas/README.md:100:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r2-output.md:1105:.planning/codex_personas/README.md:110:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r2-output.md:1137:F1: partial — README now splits Tier-A/Tier-B output correctly, but E11-00-PLAN still hardcodes 5-persona closure/uniqueness/aggregator semantics at lines 17, 256, 260, 302.
.planning/phases/governance-bundle-2/codex-r2-output.md:1138:F2: partial — README, constitution, and RETRO §6.3 now align, but E11-00-PLAN:182 still reduces rollback to “5-persona default + retro successor” and omits the 3-sub-phase + Opus steps.
.planning/phases/governance-bundle-2/codex-r2-output.md:1139:F3: not resolved — deterministic counting/round-robin exists only in README; constitution.md:343 and RETRO §6.2 still preserve the old default-P1/owner-rotation wording, so the canonical rule is still ambiguous.
.planning/phases/governance-bundle-2/codex-r2-output.md:1141:- IMPORTANT: .planning/codex_personas/README.md:9 still says the pipeline "ensures inter-persona finding uniqueness", which is false for Tier-B where uniqueness is explicitly N/A.
.planning/phases/governance-bundle-2/codex-r2-output.md:1142:- NIT: `PERSONA-ROTATION-STATE.md` is referenced but not created; acceptable if seeded on first Tier-B sub-phase, so not the blocker here.
.planning/phases/governance-bundle-2/codex-r2-output.md:1149:F1: partial — README now splits Tier-A/Tier-B output correctly, but E11-00-PLAN still hardcodes 5-persona closure/uniqueness/aggregator semantics at lines 17, 256, 260, 302.
.planning/phases/governance-bundle-2/codex-r2-output.md:1150:F2: partial — README, constitution, and RETRO §6.3 now align, but E11-00-PLAN:182 still reduces rollback to “5-persona default + retro successor” and omits the 3-sub-phase + Opus steps.
.planning/phases/governance-bundle-2/codex-r2-output.md:1151:F3: not resolved — deterministic counting/round-robin exists only in README; constitution.md:343 and RETRO §6.2 still preserve the old default-P1/owner-rotation wording, so the canonical rule is still ambiguous.
.planning/phases/governance-bundle-2/codex-r2-output.md:1153:- IMPORTANT: .planning/codex_personas/README.md:9 still says the pipeline "ensures inter-persona finding uniqueness", which is false for Tier-B where uniqueness is explicitly N/A.
.planning/phases/governance-bundle-2/codex-r2-output.md:1154:- NIT: `PERSONA-ROTATION-STATE.md` is referenced but not created; acceptable if seeded on first Tier-B sub-phase, so not the blocker here.
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:1:You are reviewing governance bundle #2 R3-retry (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 58426cf on top of e259a42).
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:4:- R1 (1f25bb5): CHANGES_REQUIRED — F1 BLOCKER tier-aware closure conflict, F2 IMPORTANT rollback divergence, F3 IMPORTANT trigger non-determinism
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:5:- R2 (419286b): R1 fixes applied. Codex R2 returned partial — F1/F2 partial (drift in E11-00-PLAN), F3 not resolved (drift in constitution + RETRO §6.2), + 1 NEW IMPORTANT (README §Purpose stale)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:7:- R3 (process crashed mid-stream, no formal verdict; intermediate observations identified 2 residual drift in README §命令模板 + §Cost supersession note)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:11:1. README §命令模板 lines 73-81: Replaced "Tier-B (1 persona 默认 — P1 Junior FCS)" + "Tier-B 轮换" twin examples with single block using `PERSONA=` variable + comment chain pointing to PERSONA-ROTATION-STATE.md round-robin source-of-truth + append command.
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:12:2. README §Cost line 131: Removed "The earlier 'candidate §6.2 re-evaluate' framing is superseded — §6.3 is canonical." (Codex flagged the supersession sentence as itself drift — it kept the dead §6.2 string in the canonical spec.)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:18:1. README §命令模板 now describes Tier-B per-sub-phase round-robin (no surviving "default P1 / owner override" mental model)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:19:2. README §Cost / §Anti-bias / §Output convention / §Purpose all consistent with cross-sub-phase rotation rule (no mentions of dead §6.2 / "re-evaluate" / "default P1 + owner rotation" wording)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:20:3. constitution.md §Codex Persona Pipeline Tier-Trigger and §Tier-trigger table fully match README §Invocation rule
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:21:4. RETRO-V61-054 §6.2 / §6.3 fully match constitution rollback semantics (3 actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7)
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:27:README §命令模板: [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:28:README cross-section consistency (§Purpose / §Invocation / §Output / §Anti-bias / §Cost): [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-retry-prompt.txt:30:RETRO §6.2/§6.3 + constitution rollback convergence: [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-output.md:16:You are reviewing governance bundle #2 R3 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit e259a42 on top of 419286b).
.planning/phases/governance-bundle-2/codex-r3-output.md:20:- F2 partial: E11-00-PLAN:182 collapsed rollback to 2 actions, not RETRO §6.3's 3 actions
.planning/phases/governance-bundle-2/codex-r3-output.md:22:- NEW IMPORTANT: README:9 §Purpose said "pipeline ensures inter-persona finding uniqueness", false for Tier-B
.planning/phases/governance-bundle-2/codex-r3-output.md:23:- NIT: PERSONA-ROTATION-STATE.md not created (acceptable on first Tier-B sub-phase)
.planning/phases/governance-bundle-2/codex-r3-output.md:26:1. F1 fix: Updated E11-00-PLAN §1 success criterion (Tier-A=5/5; Tier-B=1/1 + rotation), §6 Required output split tier-aware (within-PR uniqueness Tier-A only), §6 aggregator Tier-A only / Tier-B = single verdict file, §8 verification table tier-aware, §9 closure #3 tier-aware, §11 trailer tier-aware.
.planning/phases/governance-bundle-2/codex-r3-output.md:27:2. F2 fix: E11-00-PLAN:182 reproduced canonical RETRO §6.3 verbatim — 3 actions (rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7) + header "canonical = RETRO §6.3, constitution §Codex Persona Pipeline Tier-Trigger 引用".
.planning/phases/governance-bundle-2/codex-r3-output.md:28:3. F3 fix: constitution.md:343 + RETRO §6.2 line 148 both updated to cross-sub-phase round-robin P1→P2→P3→P4→P5→P1, default start P1, state file pointer, "no consecutive same persona". constitution.md additionally inlines the `git diff --stat` counting command so the canonical rule layer is self-contained.
.planning/phases/governance-bundle-2/codex-r3-output.md:29:4. NEW fix: README §Purpose split into Tier-A (within-PR uniqueness) + Tier-B (N/A, delegated to Surface Inventory + cross-sub-phase rotation + RETRO §6.3 rollback).
.planning/phases/governance-bundle-2/codex-r3-output.md:39:- Is rollback semantics now identical (3 actions verbatim) across constitution / RETRO §6.3 / E11-00-PLAN:182 / README §Cost? (no surviving 2-step or "re-evaluate" wording)
.planning/phases/governance-bundle-2/codex-r3-output.md:40:- Is rotation rule now identical (cross-sub-phase round-robin) across all 4 docs? (no surviving "same sub-phase no repeat" or "default P1 + owner rotation")
.planning/phases/governance-bundle-2/codex-r3-output.md:41:- Does §1 / §6 / §8 / §9 / §11 in E11-00-PLAN correctly distinguish Tier-A from Tier-B closure semantics?
.planning/phases/governance-bundle-2/codex-r3-output.md:42:- Does §Purpose in README accurately describe what Tier-B inherits vs what Tier-A inherits, without overpromising uniqueness?
.planning/phases/governance-bundle-2/codex-r3-output.md:62:/bin/zsh -lc 'rg -n "LogicMVP|governance bundle|persona|rotation|Tier-A|Tier-B|RETRO-V61-054|E11-00-PLAN|README.md" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r3-output.md:106:/bin/zsh -lc "rg -n \"rotation|owner rotation|default start P1|default P1|no consecutive same persona|same sub-phase|within-PR uniqueness|uniqueness|rollback|re-evaluate|re-engage Opus 4\\.7|round-robin|single verdict file|Tier-A|Tier-B|Surface Inventory|§6\\.3|Counterargument #2|anti-bias|candidate-rule\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r3-output.md:110:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:80:**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。
.planning/phases/governance-bundle-2/codex-r3-output.md:113:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/phases/governance-bundle-2/codex-r3-output.md:116:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/phases/governance-bundle-2/codex-r3-output.md:118:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r3-output.md:119:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r3-output.md:120:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/phases/governance-bundle-2/codex-r3-output.md:121:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r3-output.md:126:.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/phases/governance-bundle-2/codex-r3-output.md:129:.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r3-output.md:131:.planning/codex_personas/README.md:54:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r3-output.md:134:.planning/codex_personas/README.md:73:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r3-output.md:135:.planning/codex_personas/README.md:78:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r3-output.md:138:.planning/codex_personas/README.md:97:### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r3-output.md:140:.planning/codex_personas/README.md:104:- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r3-output.md:141:.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r3-output.md:143:.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r3-output.md:144:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r3-output.md:146:.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r3-output.md:148:.planning/codex_personas/README.md:128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r3-output.md:150:.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r3-output.md:151:.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r3-output.md:158:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/phases/governance-bundle-2/codex-r3-output.md:162:.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r3-output.md:163:.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r3-output.md:164:.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r3-output.md:166:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/governance-bundle-2/codex-r3-output.md:170:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/governance-bundle-2/codex-r3-output.md:172:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/governance-bundle-2/codex-r3-output.md:175:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/governance-bundle-2/codex-r3-output.md:177:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:179:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/governance-bundle-2/codex-r3-output.md:180:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:243:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/governance-bundle-2/codex-r3-output.md:182:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/governance-bundle-2/codex-r3-output.md:184:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/governance-bundle-2/codex-r3-output.md:185:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:265:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/governance-bundle-2/codex-r3-output.md:187:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/governance-bundle-2/codex-r3-output.md:188:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/governance-bundle-2/codex-r3-output.md:189:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:345:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/phases/governance-bundle-2/codex-r3-output.md:207:     3	> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r3-output.md:211:     7	## Purpose
.planning/phases/governance-bundle-2/codex-r3-output.md:215:    11	**Anti-bias model (governance bundle #2, 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:217:    13	- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/phases/governance-bundle-2/codex-r3-output.md:235:    31	> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r3-output.md:244:    40	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r3-output.md:258:    54	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r3-output.md:266:    62	### 命令模板
.planning/phases/governance-bundle-2/codex-r3-output.md:277:    73	# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r3-output.md:282:    78	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r3-output.md:288:    84	## Output convention
.planning/phases/governance-bundle-2/codex-r3-output.md:301:    97	### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r3-output.md:308:   104	- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r3-output.md:310:   106	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r3-output.md:312:   108	## Anti-bias safeguard
.planning/phases/governance-bundle-2/codex-r3-output.md:319:   115	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r3-output.md:320:   116	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r3-output.md:322:   118	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r3-output.md:326:   122	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:330:   126	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r3-output.md:332:   128	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r3-output.md:335:   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r3-output.md:342:   142	### 6.2 governance bundle #2 — persona pipeline tier-trigger
.planning/phases/governance-bundle-2/codex-r3-output.md:346:   146	**5-persona pipeline → tier-trigger:**
.planning/phases/governance-bundle-2/codex-r3-output.md:348:   148	- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/phases/governance-bundle-2/codex-r3-output.md:353:   153	- Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
.planning/phases/governance-bundle-2/codex-r3-output.md:363:   163	If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r3-output.md:365:   165	2. Open a successor RETRO-V61-* documenting the failed amortization
.planning/phases/governance-bundle-2/codex-r3-output.md:366:   166	3. Re-engage Opus 4.7 strategic review
.planning/phases/governance-bundle-2/codex-r3-output.md:370:   170	- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/phases/governance-bundle-2/codex-r3-output.md:371:   171	- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/phases/governance-bundle-2/codex-r3-output.md:372:   172	- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/phases/governance-bundle-2/codex-r3-output.md:374:   174	- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/phases/governance-bundle-2/codex-r3-output.md:384:   334	**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/phases/governance-bundle-2/codex-r3-output.md:393:   343	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/phases/governance-bundle-2/codex-r3-output.md:418:   368	**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r3-output.md:420:   370	**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r3-output.md:422:   372	1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r3-output.md:424:   374	3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/phases/governance-bundle-2/codex-r3-output.md:447:     3	> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r3-output.md:461:    17	2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/governance-bundle-2/codex-r3-output.md:489:   159	| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/governance-bundle-2/codex-r3-output.md:491:   161	| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
.planning/phases/governance-bundle-2/codex-r3-output.md:493:   163	**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/governance-bundle-2/codex-r3-output.md:495:   165	- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/governance-bundle-2/codex-r3-output.md:498:   168	**未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
.planning/phases/governance-bundle-2/codex-r3-output.md:508:   178	- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/governance-bundle-2/codex-r3-output.md:512:   182	**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/governance-bundle-2/codex-r3-output.md:518:   188	## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
.planning/phases/governance-bundle-2/codex-r3-output.md:545:   215	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:559:   258	   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/governance-bundle-2/codex-r3-output.md:560:   259	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
.planning/phases/governance-bundle-2/codex-r3-output.md:564:   263	- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/governance-bundle-2/codex-r3-output.md:566:   265	- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/governance-bundle-2/codex-r3-output.md:594:   293	**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
.planning/phases/governance-bundle-2/codex-r3-output.md:606:   305	| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/governance-bundle-2/codex-r3-output.md:618:   317	3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/governance-bundle-2/codex-r3-output.md:627:   345	> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/phases/governance-bundle-2/codex-r3-output.md:639: > Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r3-output.md:643: ## Purpose
.planning/phases/governance-bundle-2/codex-r3-output.md:648:+**Anti-bias model (governance bundle #2, 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:650:+- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/phases/governance-bundle-2/codex-r3-output.md:668: > **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r3-output.md:680: > **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append + governance bundle #2 persona tier-trigger amortization)
.planning/phases/governance-bundle-2/codex-r3-output.md:686: > **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
.planning/phases/governance-bundle-2/codex-r3-output.md:688:-> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r3-output.md:689:+> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r3-output.md:717: - Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
.planning/phases/governance-bundle-2/codex-r3-output.md:722: **前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/phases/governance-bundle-2/codex-r3-output.md:731:-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
.planning/phases/governance-bundle-2/codex-r3-output.md:732:+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/phases/governance-bundle-2/codex-r3-output.md:758: **估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r3-output.md:760: **回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/phases/governance-bundle-2/codex-r3-output.md:762: 1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r3-output.md:764: 3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
.planning/phases/governance-bundle-2/codex-r3-output.md:778: > **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r3-output.md:793:+2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/governance-bundle-2/codex-r3-output.md:817: 不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
.planning/phases/governance-bundle-2/codex-r3-output.md:823: > Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。
.planning/phases/governance-bundle-2/codex-r3-output.md:829: | ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/governance-bundle-2/codex-r3-output.md:831: | ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
.planning/phases/governance-bundle-2/codex-r3-output.md:833: **5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/governance-bundle-2/codex-r3-output.md:836:+- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/governance-bundle-2/codex-r3-output.md:839: **未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
.planning/phases/governance-bundle-2/codex-r3-output.md:849: - 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/governance-bundle-2/codex-r3-output.md:853:-**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/phases/governance-bundle-2/codex-r3-output.md:854:+**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/governance-bundle-2/codex-r3-output.md:860: ## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
.planning/phases/governance-bundle-2/codex-r3-output.md:887:-**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) 加 anti-bias safeguard：每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding，否则 review 不算 valid（pipeline 强制项）。结论：bias 风险存在但已通过 distinct context + cross-persona uniqueness 要求 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:888:+**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:894: **Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
.planning/phases/governance-bundle-2/codex-r3-output.md:904: **反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/governance-bundle-2/codex-r3-output.md:906: **Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/governance-bundle-2/codex-r3-output.md:917:+| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/governance-bundle-2/codex-r3-output.md:933:+   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/governance-bundle-2/codex-r3-output.md:934: 5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
.planning/phases/governance-bundle-2/codex-r3-output.md:940:+- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/governance-bundle-2/codex-r3-output.md:943:+- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/governance-bundle-2/codex-r3-output.md:971: **Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
.planning/phases/governance-bundle-2/codex-r3-output.md:984:+| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/governance-bundle-2/codex-r3-output.md:996:-3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
.planning/phases/governance-bundle-2/codex-r3-output.md:997:+3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/governance-bundle-2/codex-r3-output.md:1026:+> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/phases/governance-bundle-2/codex-r3-output.md:1031:@@ -127,42 +127,42 @@ Opus 4.7 §1 strategic review (2026-04-25) set E11-09 dual-h1 fix as the **leadi
.planning/phases/governance-bundle-2/codex-r3-output.md:1032: | ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/phases/governance-bundle-2/codex-r3-output.md:1034: | ≥ 4 轮 | governance 失效 | Opus 4.7 再介入诊断 |
.planning/phases/governance-bundle-2/codex-r3-output.md:1047: ### 6.2 governance bundle #2 — persona pipeline tier-trigger
.planning/phases/governance-bundle-2/codex-r3-output.md:1051: **5-persona pipeline → tier-trigger:**
.planning/phases/governance-bundle-2/codex-r3-output.md:1053:-- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
.planning/phases/governance-bundle-2/codex-r3-output.md:1055:+- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/phases/governance-bundle-2/codex-r3-output.md:1060: - Governance Mode Timeline entry "governance bundle #2 persona tier-trigger" (this PR)
.planning/phases/governance-bundle-2/codex-r3-output.md:1070: If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/phases/governance-bundle-2/codex-r3-output.md:1072: 2. Open a successor RETRO-V61-* documenting the failed amortization
.planning/phases/governance-bundle-2/codex-r3-output.md:1073: 3. Re-engage Opus 4.7 strategic review
.planning/phases/governance-bundle-2/codex-r3-output.md:1078:The main rule sections are aligned enough to compare now. I’m doing one more pass for buried stale phrases like `re-evaluate`, `default P1`, or old same-sub-phase rotation language, because one leftover sentence is enough to keep this at `CHANGES_REQUIRED`.
.planning/phases/governance-bundle-2/codex-r3-output.md:1080:/bin/zsh -lc "rg -n \"re-evaluate|default P1|default.*P1|owner rotation|same sub-phase|同一 sub-phase|no repeat|rotation to P2|Tier-B.*default P1|2-step|two actions|rollback.*2|re-engage Opus 4\\.7 strategic review|open successor RETRO|next 3 sub-phases|cross-sub-phase round-robin|P1 ?→ ?P2 ?→ ?P3 ?→ ?P4 ?→ ?P5 ?→ ?P1|within-PR uniqueness|single verdict file|aggregator\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r3-output.md:1082:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/phases/governance-bundle-2/codex-r3-output.md:1083:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/phases/governance-bundle-2/codex-r3-output.md:1085:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/governance-bundle-2/codex-r3-output.md:1086:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:1088:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/governance-bundle-2/codex-r3-output.md:1090:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/governance-bundle-2/codex-r3-output.md:1091:.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/phases/governance-bundle-2/codex-r3-output.md:1092:.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r3-output.md:1095:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r3-output.md:1096:.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r3-output.md:1097:.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r3-output.md:1110:   178	- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
.planning/phases/governance-bundle-2/codex-r3-output.md:1114:   182	**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
.planning/phases/governance-bundle-2/codex-r3-output.md:1120:   188	## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）
.planning/phases/governance-bundle-2/codex-r3-output.md:1130:   257	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
.planning/phases/governance-bundle-2/codex-r3-output.md:1158:   314	3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
.planning/phases/governance-bundle-2/codex-r3-output.md:1171:     3	> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
.planning/phases/governance-bundle-2/codex-r3-output.md:1175:     7	## Purpose
.planning/phases/governance-bundle-2/codex-r3-output.md:1193:    25	> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r3-output.md:1202:    34	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r3-output.md:1216:    48	**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/phases/governance-bundle-2/codex-r3-output.md:1224:    56	### 命令模板
.planning/phases/governance-bundle-2/codex-r3-output.md:1235:    67	# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1240:    72	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1246:    78	## Output convention
.planning/phases/governance-bundle-2/codex-r3-output.md:1259:    91	### Tier-B（1-persona 默认）
.planning/phases/governance-bundle-2/codex-r3-output.md:1266:    98	- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/phases/governance-bundle-2/codex-r3-output.md:1268:   100	If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r3-output.md:1270:   102	## Anti-bias safeguard
.planning/phases/governance-bundle-2/codex-r3-output.md:1277:   109	**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r3-output.md:1278:   110	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r3-output.md:1280:   112	3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/phases/governance-bundle-2/codex-r3-output.md:1284:   116	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1288:   120	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1293:   120	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1295:   122	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r3-output.md:1298:   125	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r3-output.md:1301:I found two likely drift spots outside the headline sections: the README command templates still read like “default P1 / owner override,” and the README cost note still mentions the old `re-evaluate` framing. I’m confirming there aren’t parallel leftovers elsewhere before I finalize the verdict.
.planning/phases/governance-bundle-2/codex-r3-output.md:1303:/bin/zsh -lc 'rg -n "默认.?P1|default.?P1|owner 选择|owner 可按|当期 owner|re-evaluate|P1→P5|P1 -> P5|P1 → P5|P1→P2→P3→P4→P5→P1|P1 → P2 → P3 → P4 → P5 → P1|5-persona|single verdict|无 aggregator|Tier-A only|Tier-B:" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
.planning/phases/governance-bundle-2/codex-r3-output.md:1305:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/phases/governance-bundle-2/codex-r3-output.md:1306:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:**
.planning/phases/governance-bundle-2/codex-r3-output.md:1307:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/phases/governance-bundle-2/codex-r3-output.md:1309:.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/phases/governance-bundle-2/codex-r3-output.md:1311:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/governance-bundle-2/codex-r3-output.md:1312:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/governance-bundle-2/codex-r3-output.md:1314:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1315:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/governance-bundle-2/codex-r3-output.md:1318:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/governance-bundle-2/codex-r3-output.md:1319:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:1320:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/governance-bundle-2/codex-r3-output.md:1321:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:233:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/governance-bundle-2/codex-r3-output.md:1323:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/governance-bundle-2/codex-r3-output.md:1324:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/governance-bundle-2/codex-r3-output.md:1325:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/governance-bundle-2/codex-r3-output.md:1326:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/governance-bundle-2/codex-r3-output.md:1328:.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/phases/governance-bundle-2/codex-r3-output.md:1329:.planning/codex_personas/README.md:31:> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/phases/governance-bundle-2/codex-r3-output.md:1330:.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/phases/governance-bundle-2/codex-r3-output.md:1331:.planning/codex_personas/README.md:78:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1334:.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/phases/governance-bundle-2/codex-r3-output.md:1335:.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/phases/governance-bundle-2/codex-r3-output.md:1336:.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/phases/governance-bundle-2/codex-r3-output.md:1337:.planning/codex_personas/README.md:122:**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1341:.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r3-output.md:1342:.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/phases/governance-bundle-2/codex-r3-output.md:1343:.planning/constitution.md:151:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/phases/governance-bundle-2/codex-r3-output.md:1344:.planning/constitution.md:334:**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/phases/governance-bundle-2/codex-r3-output.md:1345:.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/phases/governance-bundle-2/codex-r3-output.md:1346:.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/phases/governance-bundle-2/codex-r3-output.md:1347:.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/governance-bundle-2/codex-r3-output.md:1359:   215	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/governance-bundle-2/codex-r3-output.md:1364:   317	3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/governance-bundle-2/codex-r3-output.md:1368:    62	### 命令模板
.planning/phases/governance-bundle-2/codex-r3-output.md:1379:    73	# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1384:    78	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/phases/governance-bundle-2/codex-r3-output.md:1390:    84	## Output convention
.planning/phases/governance-bundle-2/codex-r3-output.md:1393:   122	**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1397:   126	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
.planning/phases/governance-bundle-2/codex-r3-output.md:1399:   128	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/phases/governance-bundle-2/codex-r3-output.md:1402:   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:1:You are reviewing governance bundle #2 R2 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 419286b on top of 1f25bb5).
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:4:- F1 BLOCKER: tier-B "1 persona" conflicts with §Output convention (5 verdicts assumed) + §Anti-bias safeguard (uniqueness check impossible) + E11-00-PLAN closure
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:5:- F2 IMPORTANT: rollback divergence — constitution.md:359 / RETRO §6.2 / README §Cost give 3 different rollback definitions
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:6:- F3 IMPORTANT: trigger non-determinism — "copy diff ≥10 行" no counting command; "同一 sub-phase 不重复同一 persona" rotation rule vacuous for Tier-B
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:14:1. F1 fix: Split §Output convention into Tier-A (aggregator) + Tier-B (1 verdict, no aggregator, no within-PR uniqueness, anti-bias delegated to Surface Inventory + cross-sub-phase rotation + rollback). Anti-bias safeguard same split.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:15:2. F2 fix: Picked RETRO §6.3 as canonical (3 explicit actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus). constitution.md and README now both reference §6.3 with same 3 actions or invoke it explicitly.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:16:3. F3 fix: Added explicit `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` counting command + PR-body requirement to print `copy_diff_lines=N (insertions=X, deletions=Y)`. Redefined rotation as cross-sub-phase round-robin P1->P2->P3->P4->P5->P1 with state file `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`.
.planning/phases/governance-bundle-2/codex-r2-prompt.txt:30:Be ruthless. If the upgrade-path "if Tier-B mid-PR scope-expands to Tier-A, prior verdict discarded" is hand-wavy, flag it. If the rotation state file doesn't exist yet (it's referenced but not created in this PR), decide whether that's a BLOCKER (rule unenforceable) or NIT (file gets created on first Tier-B sub-phase). If anti-bias is genuinely weaker for Tier-B and the fix doesn't honestly say so, flag it. Cross-doc grep: every reference to rollback / §6.3 / §6.2 must converge.
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:16:You are reviewing governance bundle #2 R3-retry (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit 58426cf on top of e259a42).
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:19:- R1 (1f25bb5): CHANGES_REQUIRED — F1 BLOCKER tier-aware closure conflict, F2 IMPORTANT rollback divergence, F3 IMPORTANT trigger non-determinism
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:20:- R2 (419286b): R1 fixes applied. Codex R2 returned partial — F1/F2 partial (drift in E11-00-PLAN), F3 not resolved (drift in constitution + RETRO §6.2), + 1 NEW IMPORTANT (README §Purpose stale)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:22:- R3 (process crashed mid-stream, no formal verdict; intermediate observations identified 2 residual drift in README §命令模板 + §Cost supersession note)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:26:1. README §命令模板 lines 73-81: Replaced "Tier-B (1 persona 默认 — P1 Junior FCS)" + "Tier-B 轮换" twin examples with single block using `PERSONA=` variable + comment chain pointing to PERSONA-ROTATION-STATE.md round-robin source-of-truth + append command.
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:27:2. README §Cost line 131: Removed "The earlier 'candidate §6.2 re-evaluate' framing is superseded — §6.3 is canonical." (Codex flagged the supersession sentence as itself drift — it kept the dead §6.2 string in the canonical spec.)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:33:1. README §命令模板 now describes Tier-B per-sub-phase round-robin (no surviving "default P1 / owner override" mental model)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:34:2. README §Cost / §Anti-bias / §Output convention / §Purpose all consistent with cross-sub-phase rotation rule (no mentions of dead §6.2 / "re-evaluate" / "default P1 + owner rotation" wording)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:35:3. constitution.md §Codex Persona Pipeline Tier-Trigger and §Tier-trigger table fully match README §Invocation rule
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:36:4. RETRO-V61-054 §6.2 / §6.3 fully match constitution rollback semantics (3 actions: rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7)
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:42:README §命令模板: [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:43:README cross-section consistency (§Purpose / §Invocation / §Output / §Anti-bias / §Cost): [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:45:RETRO §6.2/§6.3 + constitution rollback convergence: [resolved | drift] — <≤2 lines>
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:189:62:- Claude Code, Opus 4.7, governance-first, repo 是代码真相, GitHub 是对外工程面, Notion 是控制中枢, docs/coordination, run_gsd_validation_suite.py, validate_notion_control_plane.py, gsd_notion_sync.py, DEFAULT_PAGES, default_plan, qa_report.md, 人工 GitHub 设置清单
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:549:feat/governance-bundle-2-persona-tier-trigger-20260425
.planning/phases/governance-bundle-2/codex-r3-retry-output.md:554:/bin/zsh -lc "rg --files | rg 'README|constitution|RETRO-V61-054|E11-00-PLAN|PERSONA-ROTATION-STATE|governance-bundle-2'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp

codex
I’ve identified the actual README under review as `.planning/codex_personas/README.md`. Next pass is a tight line-by-line check of that README plus the three unchanged rule docs, because any surviving stale phrase in those files should still block approval.
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '320,410p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md | sed -n '136,180p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   341	|---|---|---|
   342	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
   343	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
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
   371	
   372	1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
   373	2. 开新 RETRO-V61-* 文件记录失败摊销，链接到 RETRO-V61-054
   374	3. 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件
   375	
   376	详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
   377	
   378	**详细文档：** `.planning/codex_personas/README.md` §Invocation 表，更新于本 bundle。RETRO-V61-054 §6 amortization 实证记录。
   379	
   380	### Verbatim Exception（继承 v6.0，五条件 AND）
   381	
   382	允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。
   383	
   384	### Self-Pass-Rate 强制
   385	
   386	任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。
   387	
   388	### Hard Stop Points
   389	
   390	- 需要修红线 → 停 + 索取 Kogami explicit "truth-engine 修复 logic-X" 字面授权
   391	- Codex returns BLOCKER 不能 verbatim 修 → 停 + 升级到 Kogami
   392	- 三轨任一连续 ≥3 次新增失败且非 inherited → 停 + 写 forensics + 升级
   393	- 意外触红线（grep 命中 `controller.py` 在 `git diff` 中）→ `git checkout` 撤销 + 立即停车汇报
   394	
   395	### Commit Trailer (v6.1)
   396	
   397	```
   398	Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
   399	```
   400	
   401	### 撤销条件
   402	
   403	- Kogami chat 中显式 "撤销 v6.1 / 收回授权 / 暂停自驱"
   404	- Claude Code 自评发现已超出能力边界（含红线无法绕开） → 自请暂停 + 升级

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
    29	### Tier-trigger（governance bundle #2 落地，2026-04-25 起生效）
    30	
    31	> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
    32	>
    33	> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
    34	
    35	按下表决定调多少 persona：
    36	
    37	| 子 phase 特征 | persona 数 | 选哪个 |
    38	|---|---|---|
    39	| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
    40	| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
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
   116	1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
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
   146	**5-persona pipeline → tier-trigger:**
   147	- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
   148	- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
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
   177	
   178	The Leading Indicator pattern (set a binary outcome that determines next governance action *before* the first observation) is itself a methodology artifact worth retaining. It avoids both extremes:
   179	- "Codify rules pre-emptively" (v2.3 PR's 5-round trap — the rule had to be defined while applied to itself)
   180	- "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '1,340p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   155	**E11-09 是 governance machinery 是否过载的实证 gate**：
   156	
   157	| E11-09 Codex 轮数 | 解读 | Action |
   158	|---|---|---|
   159	| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
   160	| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
   161	| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
   162	
   163	**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
   164	- 触发条件 = (a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE]
   165	- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
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
   182	**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
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
   211	### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
   212	
   213	**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
   214	
   215	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
   216	
   217	### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"
   218	
   219	**反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。
   220	
   221	**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
   222	
   223	### Counterargument C-UI: "本期 copy 里我是否写了一个 src/ 还没 ship 的 surface？"
   224	
   225	**反对论点**（v2.3 立法后强制必答）: landing / tile / banner / tooltip 的 copy 是否描述了某个 feature / field / role-gate / behavior，而该 surface 在当前 commit 的 src/ 里其实不存在或只存在于计划态？
   226	
   227	**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
   228	
   229	### Counterargument C-Opus: "我是否在 governance 投资曲线已经 over-process 的情况下还在加新规则？"
   230	
   231	**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
   232	
   233	**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
   234	
   235	---
   236	
   237	## 5. Risk register
   238	
   239	| Risk | Severity | Mitigation |
   240	|---|---|---|
   241	| 改 workbench.html 大量 selector 导致 e2e + adversarial 测试失败 | High | 每 sub-phase 末跑三轨；保留底层 `id` 和 `data-*` selector 不动，只改 visible label / class / 排版 |
   242	| 新 onboarding flow 与已有 ticket 流程冲突 | Med | E11-02 的 `/workbench/start` 单纯是入口，导向已有按钮；不替换底层 prompt/ticket 逻辑 |
   243	| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
   244	| 工程师在 Authority Contract banner 之外仍误以为可改 truth | Med | E11-07 banner + E11-04 annotation 词汇双重锁；同时不提供任何会让工程师以为"在 UI 改 truth-engine"的 affordance |
   245	| 角色 affordance E11-08 暴露 Kogami-only 操作的 implementation detail | Low | 仅展示 "Awaiting Kogami sign-off" 文案，不暴露内部 actor 列表 |
   246	
   247	---
   248	
   249	## 6. Codex Persona Review Pipeline
   250	
   251	详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
   252	
   253	1. **Persona 背景** — role / experience / mental model
   254	2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
   255	3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
   256	4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
   257	   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
   258	   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
   259	5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
   260	
   261	每轮 review 跑完后（tier-aware）：
   262	- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
   263	- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
   264	- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
   265	- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
   266	
   267	---
   268	
   269	## 7. Sequencing & estimated effort
   270	
   271	| Sub-phase | Type | LOC est | Time est | Codex required? |
   272	|---|---|---|---|---|
   273	| E11-01 | doc | ~300 | 30min | NO |
   274	| E11-02 | code (HTML/JS) | ~200 | 1h | YES (UI 交互模式变更) |
   275	| E11-03 | refactor (HTML/CSS) | ~150 | 45min | YES (UI 交互模式变更) |
   276	| E11-04 | doc + code | ~100 | 30min | NO (mechanical relabel) |
   277	| E11-05 | code (JS) | ~150 | 1h | YES (UI 交互模式变更) |
   278	| E11-06 | code (HTML/JS) | ~120 | 45min | YES (新 API 调用 / 状态聚合) |
   279	| E11-07 | code (HTML/CSS) | ~80 | 30min | NO (添加 banner，无逻辑) |
   280	| E11-08 | code (JS) | ~60 | 30min | NO (单 conditional 文案) |
   281	| E11-09 | refactor (routing) | ~200 | 1h | YES (路由变更 → 用户导航 mode) |
   282	| E11-10 | doc | ~600 (5 prompts) | 1.5h | self-review only |
   283	| E11-11 | test | ~150 | 1h | YES (新 e2e 期望) |
   284	| E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
   285	| E11-13 | code (HTML/CSS) | ~100 | 45min | YES (UI 交互模式变更 + manual mode trust 可视化) |
   286	| E11-14 | code (Python endpoint guard) | ~80 | 1h | YES (server-side guard, adapter boundary 内) |
   287	| E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
   288	| E11-16 | code (Python) | ~120 | 1h | YES (approval endpoint 三元绑定) |
   289	| E11-17 | code (HTML/CSS/JS) | ~180 | 1h | YES (presenter mode toggle = UI 交互模式变更) |
   290	| E11-18 | code (HTML/JS) | ~150 | 1h | YES (logic-gate trace tuple + schema 升级) |
   291	| E11-19 | code (HTML/JS + schema) | ~250 | 1.5h | YES (UI 交互模式变更 + ticket schema enrichment) |
   292	
   293	**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
   294	
   295	---
   296	
   297	## 8. Verification protocol (E11 closure 前必跑)
   298	
   299	| 维度 | 标准 | 锚点 |
   300	|---|---|---|
   301	| Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
   302	| E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
   303	| Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
   304	| Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
   305	| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
   306	| Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
   307	| EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |
   308	
   309	---
   310	
   311	## 9. CLOSURE 退出条件
   312	
   313	E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：
   314	
   315	1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
   316	2. ✅ §8 verification protocol 全部通过
   317	3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
   318	4. ✅ truth-engine 红线 0 触碰
   319	5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
   320	6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
   321	7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria
   322	8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
   323	9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
   324	
   325	---
   326	
   327	## 10. Open Questions（pending Kogami input · 不阻塞启动）
   328	
   329	1. 5 personas 的 specific company / 项目 context 要不要 fictionalize？（默认: 是，避免暗示真实客户）
   330	2. Onboarding flow 是 modal 还是单独路由？（默认: 单独路由 `/workbench/start`，可深链可分享）
   331	3. 三列 verb 命名候选 "Probe & Trace / Annotate & Propose / Hand off & Track" 还是更激进的 "What-If / Mark / Hand off"？（默认: 前者，与现有 button 文案对齐）
   332	4. 双 h1 修复时把旧 bundle 验收台搬到 `/workbench/bundle` 还是直接 deprecate？（默认: 搬到子路径，保留访问路径以免破坏旧 demo 习惯）
   333	5. Authority Contract banner 是 sticky 还是 dismissable？（默认: sticky 在 truth-engine surfaces 周围，dismissable 在其他位置以免审美干扰）
   334	
   335	> 本 phase 启动不依赖以上 Q 解决；Q 在 E11-01 journey map 阶段会迭代回到 plan 里 confirm。
   336	
   337	---
   338	
   339	## 11. Trailer
   340	

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '339,380p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   339	## 11. Trailer
   340	
   341	```
   342	Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
   343	```
   344	
   345	> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc "rg -n \"owner|默认起点|default P1|re-evaluate|§6\\.2|candidate|round-robin|P1→P2→P3→P4→P5→P1|P1→P5|Tier-B\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:243:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:265:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:345:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:54:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:73:# Tier-B（1 persona，跨-sub-phase 轮换 P1 → P2 → P3 → P4 → P5 → P1，起点 P1）：
.planning/codex_personas/README.md:74:# 启动新 epic 第一个 Tier-B sub-phase 跑 P1；后续按 PERSONA-ROTATION-STATE.md 末行下一个值轮换。
.planning/codex_personas/README.md:76:PERSONA=P3  # 由 .planning/phases/<epic>/PERSONA-ROTATION-STATE.md 决定，不得与上一行 Tier-B sub-phase 重复
.planning/codex_personas/README.md:81:# echo "<phase-id>: ${PERSONA} (<reason — content fit / round-robin>)" >> .planning/phases/<epic>/PERSONA-ROTATION-STATE.md
.planning/codex_personas/README.md:97:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

exec
/bin/zsh -lc 'git show --stat --oneline 58426cf -- .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
58426cf docs(governance): bundle #2 R3 fixes — README command-template + cost-note residual drift
 .planning/codex_personas/README.md | 18 +++++++++---------
 1 file changed, 9 insertions(+), 9 deletions(-)

codex
I’ve isolated the likely blockers: the command-template fix landed, but the rule text still needs one more pass for consistency. I’m verifying the exact memory line I used and then I’ll issue the formal verdict in the user’s requested schema with no extra prose.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '49,58p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '90,106p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

 succeeded in 0ms:
    90	- when the user asked for “我要一键复制的交给Claude code（Opus 4.7驱动）的提示词” -> deliver a single copy-paste block as a first-class artifact, not just a report summary [Task 2]
    91	- when later corrections stayed at “先收口治理，不动代码真值，不扩功能” -> preserve truth-layer immutability and anti-feature-creep boundaries in follow-up prompts and revisions [Task 2][Task 3]
    92	
    93	## Reusable knowledge
    94	
    95	- In this repo, high-signal truth anchors for governance drift were `python3 tools/run_gsd_validation_suite.py --format json` and `python3 tools/validate_notion_control_plane.py --format json` plus direct reads of `README.md`, `.github/workflows/gsd-automation.yml`, `pyproject.toml`, `.planning/STATE.md`, `.planning/notion_control_plane.json`, and `tools/gsd_notion_sync.py` [Task 1]
    96	- `docs/coordination/` is the right landing zone for a governance/transition package intended for Claude Code or another executor to consume directly [Task 1]
    97	- The GitHub Actions `validation` failure here came from dependency-install drift, not immediately from core logic regression: the workflow installed only `jsonschema pytest`, while `pyproject.toml` dev deps also include `numpy`, `pyyaml`, and `pytest-subtests` [Task 1]
    98	- `tools/gsd_notion_sync.py` normal runtime reads JSON config `pages` and `page_id(config, key)`; `DEFAULT_PAGES` is a fallback/maintenance risk, not by itself proof of a live wrong-page write path [Task 1][Task 3]
    99	- `.planning/STATE.md` holds multiple baseline narratives (`853 tests green`, older `800 passed`, and `796 passed` references), so any next-agent handoff should first lock the current measured green baseline before rewriting coordination docs [Task 2][Task 3]
   100	- The effective prompt shape here was: role/goal -> required reading -> already-known facts -> can/can't do list -> priorities -> required phases -> boundaries -> acceptance criteria -> output format [Task 2]
   101	
   102	## Failures and how to do differently
   103	
   104	- Symptom: a config/default drift gets overstated as a confirmed runtime bug -> cause: analysis relied on static symbol presence before proving the actual execution path -> fix: trace the live path first, then label the issue as live bug vs fallback/maintenance risk [Task 1][Task 3]
   105	- Symptom: coordination docs stay internally inconsistent after a governance refresh -> cause: only `plan.md` and `dev_handoff.md` were checked while `qa_report.md` kept the older baseline text -> fix: review the full coordination-doc set together when baseline wording or control-plane truth changes [Task 1][Task 3]
   106	- Symptom: the next executor jumps straight into patches -> cause: the handoff prompt lacks a hard rule that the first response must be a phased plan only -> fix: explicitly ban immediate patching and require a plan-first first response [Task 2]

codex
VERDICT: CHANGES_REQUIRED
README §命令模板: resolved — `.planning/codex_personas/README.md:73-81` now uses `PERSONA=` + `PERSONA-ROTATION-STATE.md`; the old twin "default P1 / rotation override" examples are gone.
README cross-section consistency (§Purpose / §Invocation / §Output / §Anti-bias / §Cost): drift — `.planning/codex_personas/README.md:40` and `:116` still say "默认起点 P1 / Owner 可覆盖", so README still conflicts with its own state-file-driven Tier-B template at `:73-81`.
constitution + README convergence: drift — `.planning/constitution.md:343-354` codifies the same owner-override model as README `:40`, while README `:73-81` now makes `PERSONA-ROTATION-STATE.md` the Tier-B selector; rule text and execution template diverge.
RETRO §6.2/§6.3 + constitution rollback convergence: resolved — `RETRO-V61-054-ui-copy-probe-birth.md:163-166` and `.planning/constitution.md:370-376` carry the same 3 rollback actions; no dead §6.2 / "re-evaluate" rollback wording survives in the canonical clauses.
E11-00-PLAN tier-aware: drift — `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159-168` still frames tier-trigger as a candidate / pre-codification rule, while `:174-182` says PR #14 already landed; §3.6 is temporally stale inside the live plan.
NEW_R3_FINDINGS:
- IMPORTANT — Tier-B selection semantics still drift across docs: README/constitution/RETRO keep "默认起点 P1 + owner override" text (`.planning/codex_personas/README.md:40,116`, `.planning/constitution.md:343`, `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148`).
- IMPORTANT — `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159-168` still presents governance bundle #2 as pending, conflicting with the landed-state text at `:174-182`.


tokens used
63,906
VERDICT: CHANGES_REQUIRED
README §命令模板: resolved — `.planning/codex_personas/README.md:73-81` now uses `PERSONA=` + `PERSONA-ROTATION-STATE.md`; the old twin "default P1 / rotation override" examples are gone.
README cross-section consistency (§Purpose / §Invocation / §Output / §Anti-bias / §Cost): drift — `.planning/codex_personas/README.md:40` and `:116` still say "默认起点 P1 / Owner 可覆盖", so README still conflicts with its own state-file-driven Tier-B template at `:73-81`.
constitution + README convergence: drift — `.planning/constitution.md:343-354` codifies the same owner-override model as README `:40`, while README `:73-81` now makes `PERSONA-ROTATION-STATE.md` the Tier-B selector; rule text and execution template diverge.
RETRO §6.2/§6.3 + constitution rollback convergence: resolved — `RETRO-V61-054-ui-copy-probe-birth.md:163-166` and `.planning/constitution.md:370-376` carry the same 3 rollback actions; no dead §6.2 / "re-evaluate" rollback wording survives in the canonical clauses.
E11-00-PLAN tier-aware: drift — `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159-168` still frames tier-trigger as a candidate / pre-codification rule, while `:174-182` says PR #14 already landed; §3.6 is temporally stale inside the live plan.
NEW_R3_FINDINGS:
- IMPORTANT — Tier-B selection semantics still drift across docs: README/constitution/RETRO keep "默认起点 P1 + owner override" text (`.planning/codex_personas/README.md:40,116`, `.planning/constitution.md:343`, `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148`).
- IMPORTANT — `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159-168` still presents governance bundle #2 as pending, conflicting with the landed-state text at `:174-182`.


