2026-04-25T15:52:59.836721Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T15:52:59.836781Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc558-1ebd-72c1-96e6-ad8ee5824710
--------
user
You are Codex GPT-5.4 acting as **Persona P5 — Apps Engineer** (Tier-A 5-persona pipeline, E11-05 sub-phase).

# Shared context for E11-05 review (all 5 personas)

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-05-wow-starter-cards-20260425`
**PR:** #18
**Worktree HEAD:** `a02729a` (single commit on top of main `a17e744`)

## What E11-05 ships

Per `E11-00-PLAN.md` row E11-05: top-of-/workbench one-click starter cards for the three demo wow scenarios.

Files in scope:
- `src/well_harness/static/workbench.html` — NEW `<section id="workbench-wow-starters">` between topbar (line 49) and trust banner. Contains 3 cards keyed `data-wow-id="wow_{a,b,c}"`.
- `src/well_harness/static/workbench.css` — NEW selectors `.workbench-wow-starters*`, `.workbench-wow-card*`, `.workbench-wow-run-button`, `.workbench-wow-result*`.
- `src/well_harness/static/workbench.js` — NEW `WOW_SCENARIOS` const, `runWowScenario(wowId)`, `installWowStarters()`, plus 1 hook line in DOMContentLoaded.
- `src/well_harness/static/workbench_start.html` — 3 [REWRITE] lines updating stale claims that E11-05 hadn't shipped.
- `tests/test_workbench_wow_starters.py` — NEW (10 tests covering static HTML invariants, JS wiring, live endpoint contracts).
- `.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md` — NEW (records the [ANCHORED]/[REWRITE] taxonomy + Tier-A trigger).
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended E11-05 = Tier-A.

## Three scenarios

| ID | Endpoint | Payload sentinel | Source contract |
|---|---|---|---|
| wow_a | `POST /api/lever-snapshot` | `BEAT_DEEP_PAYLOAD` (tra=-35°, n1k=0.92, deploy=95%) | `tests/e2e/test_wow_a_causal_chain.py:51` |
| wow_b | `POST /api/monte-carlo/run` | `{system_id:"thrust-reverser", n_trials:1000, seed:42}` | `tests/e2e/test_wow_b_monte_carlo.py:_run` |
| wow_c | `POST /api/diagnosis/run` | `{system_id:"thrust-reverser", outcome:"deploy_confirmed", max_results:10}` | `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed_returns_nonempty_results` |

## Truth-engine red line (must hold)

Files NOT touched: `src/well_harness/controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. `git diff --name-only main..a02729a` should show only static/, tests/, and .planning/ paths.

## Verification status

- 913 / 913 pytest pass (10 new tests in `test_workbench_wow_starters.py`, 0 regression)
- `pytest tests/test_workbench_wow_starters.py -q` returns 10 passed in ~2s
- All three e2e contract tests for wow_a/b/c continue to pass against the same payloads the cards send

## Out of scope

- E11-06 status bar (truth-engine SHA, e2e status) — separate sub-phase
- E11-08 no-chrome demo mode — explicit follow-up sub-phase
- Stylistic font/color tuning beyond what's in the new selectors — E11-15 sweep scope
- Per-system payload variations (currently fixed `system_id="thrust-reverser"`) — flag as INFO/NIT only
- Backend changes to /api/lever-snapshot, /api/monte-carlo/run, /api/diagnosis/run — explicit out-of-scope (truth-engine red line)

## Your specific lens

Focus on: customer/repro perspective — can a customer follow this from outside, does the reverse-diagnose card help reproduce field reports, are integration points honest about residual_risk and probe nature.

Read the files listed under "Files in scope" above (full, not summarized). Form an independent verdict from your persona's perspective.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

For each finding, classify:
- **BLOCKER** — must fix before merge (regression, safety, contract violation)
- **IMPORTANT** — should fix in this PR or follow-up sub-phase
- **NIT** — minor, optional
- **INFO** — note for the record

Each finding should cite a file:line. If you raise out-of-scope findings (E11-06/E11-08/E11-15 territory or backend), label them INFO/NIT only — not BLOCKER.

If you live-probe (boot demo_server, curl, etc.), cite the probe.

Truth-engine red line check: confirm `git diff --name-only a17e744..a02729a` shows zero changes to controller.py / runner.py / models.py / src/well_harness/adapters/.

Sign as: **P5 — Apps Engineer (Tier-A, E11-05)**
codex
Reviewing PR #18 from the P5 customer/repro lens. I’m loading the repo-specific memory note, the review workflow guidance, and the exact files in scope before I decide whether to probe anything live.
exec
/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|E11-05|workbench wow|wow starters" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.agents/skills/gsd-code-review/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
Using `gsd-code-review` guidance for the review pass and the repo memory note only to recover prior demo-workbench context. Next I’m reading the exact scoped files plus the scenario contract tests and diff boundary to decide if a live probe is worth it.
exec
/bin/zsh -lc 'nl -ba src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    52	        id="workbench-wow-starters"
    53	        class="workbench-wow-starters"
    54	        aria-label="Canonical demo scenarios — one-click starter cards"
    55	      >
    56	        <header class="workbench-wow-starters-header">
    57	          <p class="eyebrow">canonical scenarios</p>
    58	          <h2>起手卡 · One-click 走读</h2>
    59	          <p class="workbench-wow-starters-sub">
    60	            预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口，落地 wow_a/b/c demo 弧。
    61	          </p>
    62	        </header>
    63	        <div class="workbench-wow-starters-grid">
    64	          <article
    65	            class="workbench-wow-card"
    66	            data-wow-id="wow_a"
    67	            aria-labelledby="workbench-wow-a-title"
    68	          >
    69	            <header>
    70	              <span class="workbench-wow-tag">wow_a</span>
    71	              <h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>
    72	            </header>
    73	            <p class="workbench-wow-card-desc">
    74	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
    75	              deploy=95%) — latches L1–L4 deep-deploy chain.
    76	            </p>
    77	            <button
    78	              type="button"
    79	              class="workbench-wow-run-button"
    80	              data-wow-action="run"
    81	              data-wow-id="wow_a"
    82	            >
    83	              一键运行 wow_a
    84	            </button>
    85	            <div
    86	              class="workbench-wow-result"
    87	              data-wow-result-for="wow_a"
    88	              role="status"
    89	              aria-live="polite"
    90	            >
    91	              尚未运行。
    92	            </div>
    93	          </article>
    94	          <article
    95	            class="workbench-wow-card"
    96	            data-wow-id="wow_b"
    97	            aria-labelledby="workbench-wow-b-title"
    98	          >
    99	            <header>
   100	              <span class="workbench-wow-tag">wow_b</span>
   101	              <h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>
   102	            </header>
   103	            <p class="workbench-wow-card-desc">
   104	              POST <code>/api/monte-carlo/run</code> with seed=42 — 1000 次抽样，输出
   105	              success_rate + failure_modes 分布。
   106	            </p>
   107	            <button
   108	              type="button"
   109	              class="workbench-wow-run-button"
   110	              data-wow-action="run"
   111	              data-wow-id="wow_b"
   112	            >
   113	              一键运行 wow_b
   114	            </button>
   115	            <div
   116	              class="workbench-wow-result"
   117	              data-wow-result-for="wow_b"
   118	              role="status"
   119	              aria-live="polite"
   120	            >
   121	              尚未运行。
   122	            </div>
   123	          </article>
   124	          <article
   125	            class="workbench-wow-card"
   126	            data-wow-id="wow_c"
   127	            aria-labelledby="workbench-wow-c-title"
   128	          >
   129	            <header>
   130	              <span class="workbench-wow-tag">wow_c</span>
   131	              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
   132	            </header>
   133	            <p class="workbench-wow-card-desc">
   134	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   135	              触发该 outcome 的参数组合（max_results=10）。
   136	            </p>
   137	            <button
   138	              type="button"
   139	              class="workbench-wow-run-button"
   140	              data-wow-action="run"
   141	              data-wow-id="wow_c"
   142	            >
   143	              一键运行 wow_c
   144	            </button>
   145	            <div
   146	              class="workbench-wow-result"
   147	              data-wow-result-for="wow_c"
   148	              role="status"
   149	              aria-live="polite"
   150	            >
   151	              尚未运行。
   152	            </div>
   153	          </article>
   154	        </div>
   155	      </section>
   156	
   157	      <aside
   158	        id="workbench-trust-banner"
   159	        class="workbench-trust-banner"
   160	        data-feedback-mode="manual_feedback_override"
   161	        role="note"
   162	        aria-label="Feedback mode trust affordance"
   163	      >
   164	        <span class="workbench-trust-banner-icon" aria-hidden="true">⚠</span>
   165	        <div class="workbench-trust-banner-body">
   166	          <span class="workbench-trust-banner-scope">
   167	            <em>What "manual feedback" means here:</em> any value you type into the workbench to override
   168	            an observed reading — for example, editing a snapshot input field before running a scenario.
   169	            Passive reads, replays, and audit-chain navigation do NOT count as manual feedback.
   170	          </span>
   171	          <strong>That mode is advisory.</strong>
   172	          <span>
   173	            Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative.
   174	            Your manual feedback is recorded for diff/review but does not change source-of-truth values.
   175	          </span>
   176	        </div>
   177	        <button
   178	          type="button"
   179	          class="workbench-trust-banner-dismiss"
   180	          aria-label="Hide trust banner for this session"
   181	          data-trust-banner-dismiss
   182	        >
   183	          Hide for session
   184	        </button>
   185	      </aside>
   186	
   187	      <section id="workbench-annotation-toolbar" class="workbench-annotation-toolbar" aria-label="Annotation tools">
   188	        <span class="workbench-annotation-toolbar-label">Annotation</span>
   189	        <button type="button" class="workbench-annotation-tool is-active" data-annotation-tool="point">Point</button>
   190	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="area">Area</button>
   191	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="link">Link</button>
   192	        <button type="button" class="workbench-annotation-tool" data-annotation-tool="text-range">Text Range</button>
   193	        <span id="workbench-annotation-active-tool" class="workbench-annotation-active-tool" aria-live="polite">
   194	          Point tool active
   195	        </span>
   196	      </section>
   197	
   198	      <section class="workbench-collab-grid" aria-label="Three-column collaboration workbench">
   199	        <article
   200	          id="workbench-control-panel"
   201	          class="workbench-collab-column workbench-annotation-surface"
   202	          data-column="control"
   203	          data-annotation-surface="control"
   204	          tabindex="0"
   205	        >
   206	          <header>
   207	            <p class="eyebrow">control panel</p>
   208	            <h2>Scenario Control</h2>
   209	          </header>
   210	          <div id="workbench-control-status" class="workbench-collab-status" aria-live="polite">
   211	            Waiting for control panel boot.
   212	          </div>
   213	          <div class="workbench-collab-control-list" aria-label="Control panel skeleton">
   214	            <button type="button" class="workbench-toolbar-button is-primary">Load Active Ticket</button>
   215	            <button type="button" class="workbench-toolbar-button">Snapshot Current State</button>
   216	          </div>
   217	        </article>
   218	
   219	        <article
   220	          id="workbench-document-panel"
   221	          class="workbench-collab-column workbench-annotation-surface"
   222	          data-column="document"
   223	          data-annotation-surface="document"
   224	          tabindex="0"
   225	        >
   226	          <header>
   227	            <p class="eyebrow">document</p>
   228	            <h2>Spec Review Surface</h2>
   229	          </header>
   230	          <div id="workbench-document-status" class="workbench-collab-status" aria-live="polite">
   231	            Waiting for document panel boot.
   232	          </div>
   233	          <div class="workbench-collab-document">
   234	            <p>Reference packet, clarification notes, and future text-range annotations will land here.</p>
   235	            <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge</pre>
   236	          </div>
   237	        </article>
   238	
   239	        <article
   240	          id="workbench-circuit-panel"
   241	          class="workbench-collab-column workbench-annotation-surface"
   242	          data-column="circuit"
   243	          data-annotation-surface="circuit"
   244	          tabindex="0"
   245	        >
   246	          <header>
   247	            <p class="eyebrow">circuit</p>
   248	            <h2>Logic Circuit Surface</h2>
   249	          </header>
   250	          <div id="workbench-circuit-status" class="workbench-collab-status" aria-live="polite">
   251	            Waiting for circuit panel boot.
   252	          </div>
   253	          <div class="workbench-collab-circuit" aria-label="Circuit skeleton">
   254	            <span>SW1</span>
   255	            <span>Logic 1</span>
   256	            <span>Logic 2</span>
   257	            <span>Logic 3</span>
   258	            <span>Logic 4</span>
   259	            <span>THR LOCK</span>
   260	          </div>
   261	        </article>
   262	      </section>
   263	
   264	      <aside id="annotation-inbox" class="workbench-annotation-inbox" aria-label="Annotation Inbox">
   265	        <header>
   266	          <p class="eyebrow">annotation inbox</p>
   267	          <h2>Review Queue</h2>
   268	        </header>
   269	        <ul id="annotation-inbox-list">
   270	          <li>No proposals submitted yet.</li>
   271	        </ul>
   272	      </aside>
   273	
   274	      <footer id="workbench-bottom-bar" class="workbench-collab-bottom-bar" aria-label="Workbench actions">
   275	        <button
   276	          id="approval-center-entry"
   277	          type="button"
   278	          class="workbench-toolbar-button"
   279	          data-role="KOGAMI"
   280	          aria-controls="approval-center-panel"
   281	        >
   282	          Approval Center
   283	        </button>
   284	        <span>Approval actions are Kogami-only.</span>
   285	      </footer>
   286	
   287	      <section
   288	        id="approval-center-panel"
   289	        class="workbench-approval-center"
   290	        data-approval-role="KOGAMI"
   291	        aria-labelledby="approval-center-title"
   292	      >
   293	        <header>
   294	          <p class="eyebrow">approval center</p>
   295	          <h2 id="approval-center-title">Kogami Proposal Triage</h2>
   296	        </header>
   297	        <div class="workbench-approval-grid">
   298	          <article class="workbench-approval-lane" data-approval-lane="pending">
   299	            <h3>Pending</h3>
   300	            <p>Submitted annotation proposals wait here before acceptance or rejection.</p>
   301	          </article>
   302	          <article class="workbench-approval-lane" data-approval-lane="accept">
   303	            <h3>Accept</h3>
   304	            <button type="button" class="workbench-toolbar-button" data-approval-action="accept">Accept Proposal</button>
   305	          </article>
   306	          <article class="workbench-approval-lane" data-approval-lane="reject">
   307	            <h3>Reject</h3>
   308	            <button type="button" class="workbench-toolbar-button" data-approval-action="reject">Reject Proposal</button>
   309	          </article>
   310	        </div>
   311	      </section>
   312	
   313	      <!-- E11-09 (2026-04-25): legacy "Workbench Bundle 验收台" content moved to /workbench/bundle. This page is now the Epic-06..10 shell only. -->
   314	    </main>
   315	
   316	    <script src="/annotation_overlay.js"></script>
   317	    <script src="/workbench.js"></script>
   318	  </body>
   319	</html>

exec
/bin/zsh -lc 'git diff --name-only a17e744..a02729a' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.css
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
src/well_harness/static/workbench_start.html
tests/test_workbench_wow_starters.py

exec
/bin/zsh -lc 'nl -ba src/well_harness/static/workbench_start.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'nl -ba tests/test_workbench_wow_starters.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
     2	
     3	Locks the contract for the top-of-/workbench wow starter cards so future
     4	shell edits don't silently regress the demo presenter's one-click 走读
     5	entrypoint. Per E11-00-PLAN row E11-05.
     6	
     7	Three contracts validated:
     8	  1. /workbench static HTML carries the three starter cards (one per
     9	     wow_id) with run buttons and result panes.
    10	  2. workbench.js declares WOW_SCENARIOS with all three endpoints and
    11	     payload-shape sentinels (BEAT_DEEP_PAYLOAD-equivalent for wow_a,
    12	     n_trials/seed for wow_b, outcome for wow_c).
    13	  3. The three POST endpoints behind the cards return 200 with the
    14	     contract fields the cards' summarize() functions read.
    15	
    16	Truth-engine red line: this is a thin UI affordance over already-public
    17	endpoints; no controller/runner/models/adapters changes.
    18	"""
    19	
    20	from __future__ import annotations
    21	
    22	import http.client
    23	import json
    24	import re
    25	import threading
    26	from http.server import ThreadingHTTPServer
    27	from pathlib import Path
    28	
    29	import pytest
    30	
    31	from well_harness.demo_server import DemoRequestHandler
    32	
    33	
    34	REPO_ROOT = Path(__file__).resolve().parents[1]
    35	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    36	
    37	
    38	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    39	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    40	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    41	    thread.start()
    42	    return server, thread
    43	
    44	
    45	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    46	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    47	    connection.request("GET", path)
    48	    response = connection.getresponse()
    49	    body = response.read().decode("utf-8")
    50	    return response.status, body
    51	
    52	
    53	def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
    54	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    55	    connection.request(
    56	        "POST",
    57	        path,
    58	        body=json.dumps(payload).encode("utf-8"),
    59	        headers={"Content-Type": "application/json"},
    60	    )
    61	    response = connection.getresponse()
    62	    body = json.loads(response.read().decode("utf-8") or "{}")
    63	    return response.status, body
    64	
    65	
    66	@pytest.fixture
    67	def server():
    68	    s, t = _start_demo_server()
    69	    try:
    70	        yield s
    71	    finally:
    72	        s.shutdown()
    73	        s.server_close()
    74	        t.join(timeout=2)
    75	
    76	
    77	# ─── 1. Static HTML carries all three starter cards ──────────────────
    78	
    79	
    80	def test_workbench_html_has_wow_starters_section() -> None:
    81	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    82	    assert 'id="workbench-wow-starters"' in html
    83	    assert "起手卡" in html
    84	
    85	
    86	@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
    87	def test_workbench_html_has_card_for_each_wow(wow_id: str) -> None:
    88	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    89	    # card article + run button + result pane all keyed by data-wow-id
    90	    assert f'data-wow-id="{wow_id}"' in html, f"missing card for {wow_id}"
    91	    assert (
    92	        f'data-wow-result-for="{wow_id}"' in html
    93	    ), f"missing result pane for {wow_id}"
    94	
    95	
    96	# ─── 2. workbench.js wires the three scenarios ───────────────────────
    97	
    98	
    99	def test_workbench_js_declares_wow_scenarios() -> None:
   100	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   101	    # The constants object is the single source of truth.
   102	    assert "const WOW_SCENARIOS" in js
   103	    # wow_a → /api/lever-snapshot with BEAT_DEEP_PAYLOAD shape.
   104	    assert "/api/lever-snapshot" in js
   105	    assert "tra_deg" in js and "deploy_position_percent" in js
   106	    # wow_b → /api/monte-carlo/run with seed.
   107	    assert "/api/monte-carlo/run" in js
   108	    assert "n_trials" in js
   109	    # wow_c → /api/diagnosis/run with outcome.
   110	    assert "/api/diagnosis/run" in js
   111	    assert "deploy_confirmed" in js
   112	
   113	
   114	def test_workbench_js_installWowStarters_wired_to_dom() -> None:
   115	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   116	    assert "function installWowStarters" in js
   117	    # Hooked into DOMContentLoaded (alongside the existing init calls).
   118	    assert re.search(r"installWowStarters\s*\(\s*\)", js) is not None
   119	
   120	
   121	# ─── 3. Live endpoint contracts the cards depend on ──────────────────
   122	
   123	
   124	def test_wow_a_live_endpoint_returns_nodes(server) -> None:
   125	    """wow_a card summarize() reads body.nodes — must be a list on 200."""
   126	    status, body = _post(server, "/api/lever-snapshot", {
   127	        "tra_deg": -35,
   128	        "radio_altitude_ft": 2,
   129	        "engine_running": True,
   130	        "aircraft_on_ground": True,
   131	        "reverser_inhibited": False,
   132	        "eec_enable": True,
   133	        "n1k": 0.92,
   134	        "feedback_mode": "auto_scrubber",
   135	        "deploy_position_percent": 95,
   136	    })
   137	    assert status == 200
   138	    assert isinstance(body.get("nodes"), list)
   139	    assert len(body["nodes"]) > 0
   140	
   141	
   142	def test_wow_b_live_endpoint_returns_success_rate(server) -> None:
   143	    """wow_b card summarize() reads body.success_rate / n_failures / n_trials."""
   144	    status, body = _post(server, "/api/monte-carlo/run", {
   145	        "system_id": "thrust-reverser",
   146	        "n_trials": 100,
   147	        "seed": 42,
   148	    })
   149	    assert status == 200
   150	    assert "success_rate" in body
   151	    assert "n_failures" in body
   152	    assert "n_trials" in body
   153	    assert body["n_trials"] == 100
   154	
   155	
   156	def test_wow_c_live_endpoint_returns_results(server) -> None:
   157	    """wow_c card summarize() reads body.outcome / total_combos_found / results / grid_resolution."""
   158	    status, body = _post(server, "/api/diagnosis/run", {
   159	        "system_id": "thrust-reverser",
   160	        "outcome": "deploy_confirmed",
   161	        "max_results": 5,
   162	    })
   163	    assert status == 200
   164	    assert body["outcome"] == "deploy_confirmed"
   165	    assert "total_combos_found" in body
   166	    assert "grid_resolution" in body
   167	    assert isinstance(body.get("results"), list)
   168	
   169	
   170	def test_workbench_html_serves_with_wow_section(server) -> None:
   171	    """Live-served /workbench page includes the wow starters section."""
   172	    status, html = _get(server, "/workbench")
   173	    assert status == 200
   174	    assert 'id="workbench-wow-starters"' in html
   175	    assert 'data-wow-id="wow_a"' in html
   176	    assert 'data-wow-id="wow_b"' in html
   177	    assert 'data-wow-id="wow_c"' in html

 succeeded in 0ms:
     1	<!DOCTYPE html>
     2	<html lang="zh-CN">
     3	<head>
     4	<meta charset="UTF-8">
     5	<meta name="viewport" content="width=device-width,initial-scale=1">
     6	<title>Workbench · 选择你的工作台入口</title>
     7	<link rel="stylesheet" href="/unified-nav.css">
     8	<link rel="stylesheet" href="/workbench_start.css">
     9	</head>
    10	<body class="unified-nav-enabled" data-nav-current="workbench-start">
    11	
    12	<header class="unified-nav" role="navigation" aria-label="FANTUI LogicMVP 主导航">
    13	  <a href="/index.html" class="unified-nav-brand" aria-label="返回主入口">FANTUI LogicMVP</a>
    14	  <div class="unified-nav-groups">
    15	    <div class="unified-nav-group">
    16	      <span class="unified-nav-group-label">工作台</span>
    17	      <a href="/workbench/start" class="unified-nav-link" data-nav-key="workbench-start" data-current="true">入口选择</a>
    18	      <a href="/workbench" class="unified-nav-link" data-nav-key="workbench">完整面板</a>
    19	    </div>
    20	  </div>
    21	</header>
    22	
    23	<main class="ws-main" id="workbench-start-main">
    24	  <section class="ws-hero" aria-labelledby="ws-hero-title">
    25	    <h1 id="ws-hero-title">先告诉我你今天来做什么</h1>
    26	    <p>
    27	      <strong>Workbench</strong> 是同一个 3 列面板，今天会承载 5 类工作。
    28	      下面 6 张卡片各自把你带进 <code>/workbench</code> 主面板，并附一个稳定的
    29	      <code>?intent=</code> 标记。 <em>本期 (E11-02) 还没有按 intent 自动重排面板</em>——
    30	      标记落地是为了 E11-05 / E11-08 / E11-11 这几期能基于它做角色化裁剪。
    31	      想跳过引导直接看完整面板？ <a href="/workbench" class="ws-skip-link">/workbench →</a>
    32	    </p>
    33	  </section>
    34	
    35	  <section class="ws-axes" aria-labelledby="ws-axes-title">
    36	    <h2 id="ws-axes-title">这页在按"角色 + 工作意图"两个维度组织入口</h2>
    37	    <ul>
    38	      <li>
    39	        <strong>P1–P5</strong> 是 E11-01 baseline 5-persona review 里的工程角色
    40	        （Junior FCS / Senior FCS / Demo Presenter / V&amp;V / Apps Engineer），
    41	        每个 persona 在主面板里有自己最常落地的起手任务。
    42	      </li>
    43	      <li>
    44	        <strong>KOGAMI</strong> 不是 persona，是项目内部的<em>审批权限</em>角色（仅 Kogami 可签发 proposal）。
    45	        与 P1–P5 同列展示，是因为审批入口和上面五种工作一样来自 Workbench。
    46	      </li>
    47	    </ul>
    48	  </section>
    49	
    50	  <section class="ws-tiles" aria-label="角色 + 意图入口">
    51	    <a href="/workbench?intent=learn-demo"
    52	       class="ws-tile"
    53	       data-persona="P1"
    54	       data-intent="learn-demo"
    55	       id="ws-tile-learn-demo">
    56	      <span class="ws-tile-kind">学习与演示</span>
    57	      <h2 class="ws-tile-title">跑 4 张一键验收预设</h2>
    58	      <p class="ws-tile-subtitle">P1 · Junior FCS · 30 分钟内上手</p>
    59	      <p class="ws-tile-desc">
    60	        落到 <code>/workbench</code>「一键预设验收卡」。 当前 4 张：
    61	        <em>通过并留档 / 阻塞演示 / 快速通过 / 留档复跑</em>，每张点完会自动跑
    62	        intake → bundle 真实链路；其中 ready_archived 与 archive_retry 还会
    63	        落 archive 目录，blocked_follow_up 与 ready_preview 不落 archive。
    64	        不要求先碰 JSON。
    65	      </p>
    66	      <ul class="ws-tile-bullets">
    67	        <li>4 张预设：ready_archived / blocked_follow_up / ready_preview / archive_retry</li>
    68	        <li>archiveBundle: true 仅 2/4（ready_archived + archive_retry）</li>
    69	        <li>wow_a/b/c 起手卡片已上线（E11-05），见 <code>/workbench</code> 顶部「起手卡」</li>
    70	      </ul>
    71	      <span class="ws-tile-arrow">→</span>
    72	    </a>
    73	
    74	    <a href="/workbench?intent=engineer-probe"
    75	       class="ws-tile"
    76	       data-persona="P2"
    77	       data-intent="engineer-probe"
    78	       id="ws-tile-engineer-probe">
    79	      <span class="ws-tile-kind">工程师调试</span>
    80	      <h2 class="ws-tile-title">读 3 列 shell + Raw JSON 抽屉</h2>
    81	      <p class="ws-tile-subtitle">P2 · Senior FCS · 真值只读 / 提案受签</p>
    82	      <p class="ws-tile-desc">
    83	        落到 <code>/workbench</code> 的 control / document / circuit 三列 shell + 「开发调试 / Raw JSON」
    84	        抽屉。 改动 spec 不会改真值，只能转成 ticket / proposal 走签批。
    85	        TRA / RA / N1k 等 lever 调参在 <code>/demo.html</code>，本期 <code>?intent=</code> 还没把它合入。
    86	      </p>
    87	      <ul class="ws-tile-bullets">
    88	        <li>truth-engine 是 read-only（红线见底部）</li>
    89	        <li>顶部 ticket / identity chrome 默认显示，可读不可改</li>
    90	        <li>L1–L4 着色 + 认证链 banner 在 E11-06/07 上线</li>
    91	      </ul>
    92	      <span class="ws-tile-arrow">→</span>
    93	    </a>
    94	
    95	    <a href="/workbench?intent=demo-stage"
    96	       class="ws-tile"
    97	       data-persona="P3"
    98	       data-intent="demo-stage"
    99	       id="ws-tile-demo-stage">
   100	      <span class="ws-tile-kind">立项 / 汇报演示</span>
   101	      <h2 class="ws-tile-title">用「通过并留档」预设走 happy path</h2>
   102	      <p class="ws-tile-subtitle">P3 · Demo Presenter · 上台前最后过一遍</p>
   103	      <p class="ws-tile-desc">
   104	        本期主面板还没有专门的 demo mode。 暂时推荐：先点
   105	        <em>「一键通过验收」（ready_archived）</em> 走通 happy path，
   106	        再点 <em>「一键看阻塞态」（blocked_follow_up）</em> 演示 clarification gate。
   107	        反推逻辑 lever-driven 演示（TRA / RA / N1k）在 <code>/demo.html</code>；
   108	        wow_a/b/c 起手卡 已在 <code>/workbench</code> 顶部上线（E11-05），可以一键走读
   109	        BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose。
   110	      </p>
   111	      <ul class="ws-tile-bullets">
   112	        <li>建议演示前隐藏浏览器侧栏 + 关闭 Approval Center 抽屉</li>
   113	        <li>"一键留档复跑" 适合演示同秒重复点也不崩</li>
   114	        <li>无-chrome demo mode 进入 E11-08 范围（wow_a 走读 已 E11-05 完成）</li>
   115	      </ul>
   116	      <span class="ws-tile-arrow">→</span>
   117	    </a>
   118	
   119	    <a href="/workbench?intent=customer-repro"
   120	       class="ws-tile"
   121	       data-persona="P5"
   122	       data-intent="customer-repro"
   123	       id="ws-tile-customer-repro">
   124	      <span class="ws-tile-kind">客户问题复现</span>
   125	      <h2 class="ws-tile-title">填 9 个 knowledge 字段</h2>
   126	      <p class="ws-tile-subtitle">P5 · Apps Engineer · intake → bundle → archive</p>
   127	      <p class="ws-tile-desc">
   128	        落到 <code>/workbench</code> 的 knowledge 区（"Resolution / Knowledge 字段"折叠面板）。 当前 schema 是 9 字段：
   129	        Observed Symptoms / Evidence Links / Confirmed Root Cause / Repair Action / Validation After Fix /
   130	        Residual Risk / Suggested Logic Change / Reliability Gain Hypothesis / Guardrail Note。
   131	        客户邮件原文 → ticket payload 的字段映射工具是 E11-08 范围，
   132	        本期暂时手抄进 Evidence Links。
   133	      </p>
   134	      <ul class="ws-tile-bullets">
   135	        <li>knowledge 字段已经在主面板渲染（dt/dd 列表）</li>
   136	        <li>customer_quote / repro_recipe / screenshot_refs 等扩展字段是 E11-08 范围</li>
   137	        <li>提交后转到 intake → bundle 真实链路，不新增第二套规则</li>
   138	      </ul>
   139	      <span class="ws-tile-arrow">→</span>
   140	    </a>
   141	
   142	    <a href="/workbench?intent=approval-review#approval-center-entry"
   143	       class="ws-tile"
   144	       data-persona="KOGAMI"
   145	       data-intent="approval-review"
   146	       id="ws-tile-approval-review">
   147	      <span class="ws-tile-kind">提案审核（Kogami）</span>
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
   165	
   166	    <a href="/workbench?intent=vv-trace"
   167	       class="ws-tile"
   168	       data-persona="P4"
   169	       data-intent="vv-trace"
   170	       id="ws-tile-vv-trace">
   171	      <span class="ws-tile-kind">V&amp;V 适航追溯</span>
   172	      <h2 class="ws-tile-title">沿 intake → bundle → archive 走读</h2>
   173	      <p class="ws-tile-subtitle">P4 · QA / V&amp;V · DO-178C 风格审计</p>
   174	      <p class="ws-tile-desc">
   175	        本期主面板还没有专门的 trace-matrix 视图。 当前能做的：
   176	        从某个 acceptance preset 跑出 bundle，去 archive 包里读结果，
   177	        对照 <code>controller.py</code> + <code>adapters/*.py</code> 找 requirement 引用。
   178	        CSV / JSONL trace 导出在 E11-09 后才上线。
   179	      </p>
   180	      <ul class="ws-tile-bullets">
   181	        <li>archive package 自带 timestamp + slug 目录 + SHA256 文件完整性哈希（不是 git commit SHA）</li>
   182	        <li>truth-engine SHA / adversarial 8/8 / e2e 状态条进入 E11-06 范围</li>
   183	        <li>本期产出物均为内部研究证据，不构成适航合规声明</li>
   184	      </ul>
   185	      <span class="ws-tile-arrow">→</span>
   186	    </a>
   187	  </section>
   188	
   189	  <section class="ws-redline" aria-labelledby="ws-redline-title">
   190	    <h2 id="ws-redline-title">红线 · 你点哪一张都不会改的东西</h2>
   191	    <ul>
   192	      <li><code>controller.py</code> · 19-node truth engine · 4 logic gates — <strong>read-only</strong></li>
   193	      <li><code>adapters/*.py</code> 真值出口 — <strong>read-only</strong></li>
   194	      <li>已签 audit event 的 hash chain — <strong>append-only</strong></li>
   195	      <li>wow_a fixture 的 BEAT_DEEP_PAYLOAD — <strong>frozen</strong></li>
   196	    </ul>
   197	    <p class="ws-redline-note">
   198	      所有"修改"都走 proposal → ticket → Kogami 签批 流程；
   199	      详见 <a href="/workbench?intent=approval-review#approval-center-entry">Approval Center</a>
   200	      与
   201	      <a href="/index.html">主入口 · 工作台总览</a>。
   202	    </p>
   203	  </section>
   204	</main>
   205	
   206	</body>
   207	</html>

 succeeded in 0ms:
     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
     2	
     3	> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
     4	>
     5	> Records every user-facing string introduced by E11-05 and classifies each per the [ANCHORED/REWRITE/DELETE] taxonomy so the Tier-A vs Tier-B routing decision is auditable.
     6	
     7	## Surface diff inventory
     8	
     9	| # | Surface | Type | Anchor | Notes |
    10	|---|---|---|---|---|
    11	| 1 | `<h2>起手卡 · One-click 走读</h2>` | [ANCHORED] | `workbench.html` `<section id="workbench-wow-starters">` (NEW) | Section heading; visible only on /workbench shell page. |
    12	| 2 | "预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口…" sub-header | [ANCHORED] | same section header | Description of what the cards do. |
    13	| 3 | `<h3>Causal Chain · 因果链走读</h3>` | [ANCHORED] | `workbench-wow-a-title` (NEW) | wow_a card title, anchored to `tests/e2e/test_wow_a_causal_chain.py`. |
    14	| 4 | wow_a description "POST /api/lever-snapshot with BEAT_DEEP_PAYLOAD…" | [ANCHORED] | `tests/e2e/test_wow_a_causal_chain.py:51` `BEAT_DEEP_PAYLOAD` | Truth claim about endpoint + payload shape. |
    15	| 5 | wow_a button "一键运行 wow_a" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
    16	| 6 | `<h3>Monte Carlo · 1000-trial 可靠性</h3>` | [ANCHORED] | `workbench-wow-b-title` (NEW) | wow_b card title, anchored to `tests/e2e/test_wow_b_monte_carlo.py`. |
    17	| 7 | wow_b description "POST /api/monte-carlo/run with seed=42…" | [ANCHORED] | `tests/e2e/test_wow_b_monte_carlo.py:_run` | Truth claim about endpoint + payload + seed. |
    18	| 8 | wow_b button "一键运行 wow_b" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
    19	| 9 | `<h3>Reverse Diagnose · 反向诊断</h3>` | [ANCHORED] | `workbench-wow-c-title` (NEW) | wow_c card title, anchored to `tests/e2e/test_wow_c_reverse_diagnose.py`. |
    20	| 10 | wow_c description "POST /api/diagnosis/run with outcome=deploy_confirmed…" | [ANCHORED] | `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed_returns_nonempty_results` | Truth claim about endpoint + outcome + max_results. |
    21	| 11 | wow_c button "一键运行 wow_c" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
    22	| 12 | "尚未运行。" placeholder × 3 | [ANCHORED] | per-card `data-wow-result-for=*` pane | Initial result-pane copy. |
    23	| 13 | `workbench_start.html` line ~69: "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" → "wow_a/b/c 起手卡片已上线（E11-05），见 /workbench 顶部「起手卡」" | [REWRITE] | `workbench_start.html:69` | Now that E11-05 ships, the placeholder is updated to a positive claim. |
    24	| 14 | `workbench_start.html` line ~108: "wow_a/b/c 目前只在 tests/e2e/test_wow_a_causal_chain.py 里有，没有 UI 走读 surface" → "wow_a/b/c 起手卡 已在 /workbench 顶部上线（E11-05）…" | [REWRITE] | `workbench_start.html:107-108` | Removes the negative claim that no UI走读 surface exists. |
    25	| 15 | `workbench_start.html` line ~113: "无-chrome demo mode + UI wow_a 走读 进入 E11-05/08 范围" → "无-chrome demo mode 进入 E11-08 范围（wow_a 走读 已 E11-05 完成）" | [REWRITE] | `workbench_start.html:113` | Removes the implicit claim that wow_a走读 is still pending; demarcates remaining E11-08 scope. |
    26	
    27	## Tier-trigger evaluation
    28	
    29	Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:
    30	
    31	> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.
    32	
    33	- **copy_diff_lines** = 15 (all enumerated rows above) → ≥ 10 ✓
    34	- **[REWRITE/DELETE] count** = 3 (rows 13, 14, 15) → ≥ 3 ✓ ← edge case
    35	
    36	> **Verdict: Tier-A** (5-persona review).
    37	
    38	Both thresholds are met: the 3 [REWRITE] lines on `workbench_start.html` are doc-truth corrections (placeholder copy that previously claimed E11-05 wasn't shipped). Per the rule's spirit — protect against stale copy reaching production — Tier-A is the conservative routing here.
    39	
    40	> **Action: dispatch all 5 personas (P1–P5) for E11-05.**
    41	
    42	## Truth-engine red line
    43	
    44	Files touched:
    45	- `src/well_harness/static/workbench.html` (NEW section only)
    46	- `src/well_harness/static/workbench.css` (NEW selectors only)
    47	- `src/well_harness/static/workbench.js` (NEW WOW_SCENARIOS const + runWowScenario + installWowStarters + 1 hook line in DOMContentLoaded)
    48	- `src/well_harness/static/workbench_start.html` (3 [REWRITE] lines documenting that E11-05 has shipped)
    49	- `tests/test_workbench_wow_starters.py` (NEW)
    50	
    51	Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.

exec
/bin/zsh -lc 'nl -ba src/well_harness/static/workbench.css' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
   108	   Top-of-/workbench placement so the demo presenter has a one-click
   109	   走读 entrypoint to BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose
   110	   without typing payloads by hand. */
   111	.workbench-wow-starters {
   112	  margin-bottom: 1rem;
   113	  padding: 1rem 1.1rem;
   114	  border: 1px solid rgba(120, 200, 255, 0.28);
   115	  border-radius: 12px;
   116	  background: rgba(12, 28, 48, 0.55);
   117	}
   118	
   119	.workbench-wow-starters-header {
   120	  margin-bottom: 0.85rem;
   121	}
   122	
   123	.workbench-wow-starters-header h2 {
   124	  margin: 0.2rem 0 0.35rem;
   125	  font-size: 1.15rem;
   126	  color: #d8ecff;
   127	}
   128	
   129	.workbench-wow-starters-sub {
   130	  margin: 0;
   131	  color: rgba(206, 223, 236, 0.78);
   132	  font-size: 0.85rem;
   133	}
   134	
   135	.workbench-wow-starters-grid {
   136	  display: grid;
   137	  grid-template-columns: repeat(3, minmax(0, 1fr));
   138	  gap: 0.85rem;
   139	}
   140	
   141	@media (max-width: 960px) {
   142	  .workbench-wow-starters-grid {
   143	    grid-template-columns: 1fr;
   144	  }
   145	}
   146	
   147	.workbench-wow-card {
   148	  display: flex;
   149	  flex-direction: column;
   150	  gap: 0.55rem;
   151	  padding: 0.85rem 0.95rem;
   152	  border: 1px solid rgba(120, 200, 255, 0.22);
   153	  border-radius: 10px;
   154	  background: rgba(8, 18, 34, 0.65);
   155	}
   156	
   157	.workbench-wow-card header {
   158	  display: flex;
   159	  align-items: baseline;
   160	  gap: 0.55rem;
   161	}
   162	
   163	.workbench-wow-card h3 {
   164	  margin: 0;
   165	  font-size: 1rem;
   166	  color: #e6f1ff;
   167	}
   168	
   169	.workbench-wow-tag {
   170	  padding: 0.1rem 0.45rem;
   171	  border-radius: 4px;
   172	  background: rgba(120, 200, 255, 0.18);
   173	  color: #9ed3ff;
   174	  font-family: "SFMono-Regular", "Menlo", monospace;
   175	  font-size: 0.72rem;
   176	  letter-spacing: 0.04em;
   177	  text-transform: lowercase;
   178	}
   179	
   180	.workbench-wow-card-desc {
   181	  margin: 0;
   182	  color: rgba(206, 223, 236, 0.84);
   183	  font-size: 0.85rem;
   184	  line-height: 1.45;
   185	}
   186	
   187	.workbench-wow-card-desc code {
   188	  padding: 0.05rem 0.3rem;
   189	  border-radius: 3px;
   190	  background: rgba(120, 200, 255, 0.12);
   191	  color: #b8e0ff;
   192	  font-size: 0.8rem;
   193	}
   194	
   195	.workbench-wow-run-button {
   196	  align-self: flex-start;
   197	  padding: 0.4rem 0.85rem;
   198	  border: 1px solid rgba(120, 200, 255, 0.5);
   199	  border-radius: 6px;
   200	  background: rgba(120, 200, 255, 0.16);
   201	  color: #d8ecff;
   202	  font-size: 0.85rem;
   203	  cursor: pointer;
   204	  transition: background 0.12s ease;
   205	}
   206	
   207	.workbench-wow-run-button:hover:not([disabled]) {
   208	  background: rgba(120, 200, 255, 0.28);
   209	}
   210	
   211	.workbench-wow-run-button[disabled] {
   212	  opacity: 0.55;
   213	  cursor: progress;
   214	}
   215	
   216	.workbench-wow-result {
   217	  min-height: 1.3rem;
   218	  padding: 0.5rem 0.65rem;
   219	  border-radius: 6px;
   220	  background: rgba(255, 255, 255, 0.04);
   221	  color: rgba(206, 223, 236, 0.82);
   222	  font-family: "SFMono-Regular", "Menlo", monospace;
   223	  font-size: 0.78rem;
   224	  line-height: 1.45;
   225	  white-space: pre-wrap;
   226	  word-break: break-word;
   227	}
   228	
   229	.workbench-wow-result[data-wow-state="ok"] {
   230	  border: 1px solid rgba(120, 220, 170, 0.35);
   231	  color: #d4f5e2;
   232	}
   233	
   234	.workbench-wow-result[data-wow-state="error"] {
   235	  border: 1px solid rgba(247, 144, 144, 0.5);
   236	  color: #ffd6d6;
   237	}
   238	
   239	/* E11-13: trust-affordance banner. Visible only when
   240	   data-feedback-mode = manual_feedback_override AND not session-dismissed.
   241	   Explains the advisory boundary so the user does not infer authority
   242	   from manual override. */
   243	.workbench-trust-banner {
   244	  display: flex;
   245	  align-items: flex-start;
   246	  gap: 0.85rem;
   247	  margin-bottom: 1rem;
   248	  padding: 0.85rem 1rem;
   249	  border: 1px solid rgba(247, 188, 92, 0.5);
   250	  border-radius: 10px;
   251	  background: rgba(247, 188, 92, 0.1);
   252	  color: #f7e2ba;
   253	}
   254	
   255	.workbench-trust-banner[data-feedback-mode="truth_engine"],
   256	.workbench-trust-banner[data-trust-banner-dismissed="true"] {
   257	  display: none;
   258	}
   259	
   260	.workbench-trust-banner-icon {
   261	  flex: 0 0 auto;
   262	  font-size: 1.2rem;
   263	  color: #f7d398;
   264	  line-height: 1;
   265	}
   266	
   267	.workbench-trust-banner-body {
   268	  flex: 1 1 auto;
   269	  display: flex;
   270	  flex-direction: column;
   271	  gap: 0.25rem;
   272	  font-size: 0.9rem;
   273	  line-height: 1.45;
   274	}
   275	
   276	.workbench-trust-banner-body strong {
   277	  color: #fbeacb;
   278	}
   279	
   280	.workbench-trust-banner-scope {
   281	  color: rgba(247, 226, 186, 0.86);
   282	  font-size: 0.85rem;
   283	}
   284	
   285	.workbench-trust-banner-scope em {
   286	  color: #fbeacb;
   287	  font-style: normal;
   288	  font-weight: 600;
   289	}
   290	
   291	.workbench-trust-banner-dismiss {
   292	  flex: 0 0 auto;
   293	  align-self: center;
   294	  padding: 0.35rem 0.7rem;
   295	  border: 1px solid rgba(247, 188, 92, 0.4);
   296	  border-radius: 6px;
   297	  background: transparent;
   298	  color: #fbeacb;
   299	  cursor: pointer;
   300	  font-size: 0.8rem;
   301	}
   302	
   303	.workbench-trust-banner-dismiss:hover {
   304	  background: rgba(247, 188, 92, 0.16);
   305	}
   306	
   307	.workbench-annotation-toolbar {
   308	  display: flex;
   309	  align-items: center;
   310	  gap: 0.65rem;
   311	  margin-bottom: 1rem;
   312	  padding: 0.75rem 1rem;
   313	}
   314	
   315	.workbench-annotation-toolbar-label {
   316	  color: rgba(206, 223, 236, 0.72);
   317	  font-size: 0.75rem;
   318	  letter-spacing: 0.06em;
   319	  text-transform: uppercase;
   320	}
   321	
   322	.workbench-annotation-tool {
   323	  border: 1px solid rgba(143, 214, 233, 0.22);
   324	  border-radius: 8px;
   325	  background: rgba(16, 31, 46, 0.88);
   326	  color: #edf8ff;
   327	  cursor: pointer;
   328	  padding: 0.55rem 0.72rem;
   329	}
   330	
   331	.workbench-annotation-tool.is-active,
   332	.workbench-annotation-tool[aria-pressed="true"] {
   333	  border-color: rgba(122, 224, 210, 0.58);
   334	  background: rgba(122, 224, 210, 0.16);
   335	  color: #f4fffc;
   336	}
   337	
   338	.workbench-annotation-active-tool {
   339	  margin-left: auto;
   340	  color: rgba(221, 234, 246, 0.78);
   341	  font-size: 0.9rem;
   342	}
   343	
   344	.workbench-collab-grid {
   345	  display: grid;
   346	  grid-template-columns: 0.82fr 1.12fr 1.06fr;
   347	  gap: 1rem;
   348	  margin-bottom: 1rem;
   349	  padding: 1rem;
   350	}
   351	
   352	.workbench-collab-column {
   353	  position: relative;
   354	  min-height: 20rem;
   355	  border: 1px solid rgba(143, 214, 233, 0.14);
   356	  border-radius: 8px;
   357	  background: rgba(5, 14, 23, 0.72);
   358	  padding: 1rem;
   359	}
   360	
   361	.workbench-annotation-surface {
   362	  outline: none;
   363	}
   364	
   365	.workbench-annotation-surface:focus {
   366	  border-color: rgba(122, 224, 210, 0.48);
   367	}
   368	
   369	.workbench-annotation-marker {
   370	  position: absolute;
   371	  z-index: 2;
   372	  min-width: 0.65rem;
   373	  min-height: 0.65rem;
   374	  border: 2px solid #7ae0d2;
   375	  border-radius: 999px;
   376	  background: rgba(122, 224, 210, 0.28);
   377	  pointer-events: none;
   378	}
   379	
   380	.workbench-annotation-marker[data-tool="area"] {
   381	  border-radius: 8px;
   382	  background: rgba(122, 224, 210, 0.08);
   383	}
   384	
   385	.workbench-annotation-marker[data-tool="link"],
   386	.workbench-annotation-marker[data-tool="text-range"] {
   387	  border-color: #ffd166;
   388	  background: rgba(255, 209, 102, 0.18);
   389	}
   390	
   391	.workbench-annotation-draft {
   392	  margin-top: 0.7rem;
   393	  border-left: 3px solid rgba(122, 224, 210, 0.58);
   394	  color: rgba(240, 247, 255, 0.84);
   395	  padding-left: 0.7rem;
   396	}
   397	
   398	.workbench-collab-status {
   399	  margin: 0.8rem 0;
   400	  border-radius: 8px;
   401	  border: 1px solid rgba(122, 224, 210, 0.18);
   402	  background: rgba(9, 21, 32, 0.72);
   403	  color: #dff9f2;
   404	  padding: 0.75rem;
   405	}
   406	
   407	.workbench-collab-control-list {
   408	  display: flex;
   409	  flex-direction: column;
   410	  align-items: flex-start;
   411	  gap: 0.65rem;
   412	}
   413	
   414	.workbench-collab-document {
   415	  color: rgba(240, 247, 255, 0.88);
   416	  line-height: 1.6;
   417	}
   418	
   419	.workbench-collab-document pre {
   420	  overflow: auto;
   421	  border-radius: 8px;
   422	  background: rgba(0, 0, 0, 0.22);
   423	  padding: 0.8rem;
   424	}
   425	
   426	.workbench-collab-circuit {
   427	  display: grid;
   428	  grid-template-columns: repeat(2, minmax(0, 1fr));
   429	  gap: 0.65rem;
   430	}
   431	
   432	.workbench-collab-circuit span {
   433	  border: 1px solid rgba(40, 244, 255, 0.2);
   434	  border-radius: 8px;
   435	  background: rgba(40, 244, 255, 0.08);
   436	  padding: 0.7rem;
   437	  text-align: center;
   438	}
   439	
   440	.workbench-annotation-inbox {
   441	  margin-bottom: 1rem;
   442	  padding: 1rem;
   443	}
   444	
   445	.workbench-annotation-inbox ul {
   446	  margin: 0.75rem 0 0;
   447	  padding-left: 1.1rem;
   448	  color: rgba(240, 247, 255, 0.82);
   449	}
   450	
   451	.workbench-collab-bottom-bar {
   452	  position: sticky;
   453	  bottom: 0;
   454	  z-index: 10;
   455	  display: flex;
   456	  align-items: center;
   457	  gap: 0.9rem;
   458	  margin-bottom: 1rem;
   459	  padding: 0.8rem 1rem;
   460	  color: rgba(206, 223, 236, 0.76);
   461	  backdrop-filter: blur(16px);
   462	}
   463	
   464	.workbench-approval-center {
   465	  margin-bottom: 1rem;
   466	  padding: 1rem;
   467	}
   468	
   469	.workbench-approval-center h2,
   470	.workbench-approval-center h3 {
   471	  margin: 0;
   472	}
   473	
   474	.workbench-approval-grid {
   475	  display: grid;
   476	  grid-template-columns: repeat(3, minmax(0, 1fr));
   477	  gap: 0.75rem;
   478	  margin-top: 1rem;
   479	}
   480	
   481	.workbench-approval-lane {
   482	  min-height: 7rem;
   483	  border: 1px solid rgba(143, 214, 233, 0.16);
   484	  border-radius: 8px;
   485	  background: rgba(5, 14, 23, 0.62);
   486	  padding: 0.85rem;
   487	}
   488	
   489	.workbench-approval-lane p {
   490	  color: rgba(240, 247, 255, 0.76);
   491	}
   492	
   493	@media (max-width: 1180px) {
   494	  .workbench-collab-topbar,
   495	  .workbench-collab-grid,
   496	  .workbench-approval-grid {
   497	    grid-template-columns: 1fr;
   498	  }
   499	}
   500	
   501	.workbench-nav-panel,
   502	.workbench-acceptance-panel {
   503	  display: flex;
   504	  align-items: center;
   505	  justify-content: space-between;
   506	  gap: 1rem;
   507	}
   508	
   509	.workbench-nav-link {
   510	  color: #c8fff1;
   511	  font-weight: 700;
   512	  text-decoration: none;
   513	}
   514	
   515	.workbench-nav-link:hover {
   516	  text-decoration: underline;
   517	}
   518	
   519	.workbench-nav-divider {
   520	  width: 1px;
   521	  align-self: stretch;
   522	  background: rgba(200, 255, 241, 0.2);
   523	}
   524	
   525	.workbench-nav-note {
   526	  color: rgba(232, 246, 255, 0.78);
   527	}
   528	
   529	.workbench-acceptance-list {
   530	  margin: 0;
   531	  padding-left: 1.25rem;
   532	  color: rgba(240, 247, 255, 0.92);
   533	}
   534	
   535	.workbench-route-strip {
   536	  margin-top: 1rem;
   537	}
   538	
   539	.workbench-layout {
   540	  display: grid;
   541	  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
   542	  gap: 1.25rem;
   543	  margin-top: 1.25rem;
   544	}
   545	
   546	.workbench-section-heading {
   547	  display: flex;
   548	  align-items: flex-start;
   549	  justify-content: space-between;
   550	  gap: 1rem;
   551	  margin-bottom: 1rem;
   552	}
   553	
   554	.workbench-section-note {
   555	  margin: 0;
   556	  color: rgba(221, 234, 246, 0.78);
   557	  text-align: right;
   558	}
   559	
   560	.workbench-toolbar {
   561	  display: flex;
   562	  flex-wrap: wrap;
   563	  gap: 0.75rem;
   564	  margin-bottom: 1rem;
   565	}
   566	
   567	.workbench-archive-restore-row {
   568	  display: flex;
   569	  align-items: flex-end;
   570	  gap: 0.75rem;
   571	  margin-bottom: 1rem;
   572	}
   573	
   574	.workbench-archive-restore-row .workbench-field {
   575	  flex: 1 1 auto;
   576	}
   577	
   578	.workbench-archive-restore-row .workbench-toolbar-button {
   579	  white-space: nowrap;
   580	}
   581	
   582	.workbench-recent-archives-board {
   583	  margin-bottom: 1rem;
   584	  padding: 1rem;
   585	  border: 1px solid rgba(143, 214, 233, 0.16);
   586	  border-radius: 20px;
   587	  background:
   588	    linear-gradient(135deg, rgba(8, 19, 31, 0.94), rgba(7, 15, 25, 0.9)),
   589	    radial-gradient(circle at 84% 18%, rgba(143, 214, 233, 0.12), transparent 18rem);
   590	}
   591	
   592	.workbench-recent-archives-header-actions {
   593	  display: flex;
   594	  align-items: center;
   595	  gap: 0.75rem;
   596	}
   597	
   598	.workbench-recent-archive-action {
   599	  display: inline-flex;
   600	  align-items: center;
   601	  justify-content: center;
   602	  margin-top: 0.35rem;
   603	}
   604	
   605	.workbench-toolbar-button,
   606	.workbench-run-button,
   607	.workbench-file-picker {
   608	  border: 1px solid rgba(122, 224, 210, 0.28);
   609	  border-radius: 999px;
   610	  background: rgba(9, 21, 32, 0.7);
   611	  color: #eff8ff;
   612	  padding: 0.75rem 1rem;
   613	  font: inherit;
   614	  cursor: pointer;
   615	  transition:
   616	    background var(--duration-fast) var(--ease-standard),
   617	    border-color var(--duration-fast) var(--ease-standard),
   618	    box-shadow var(--duration-fast) var(--ease-standard),
   619	    transform var(--duration-fast) var(--ease-standard);
   620	}
   621	
   622	.workbench-toolbar-button:hover,
   623	.workbench-run-button:hover,
   624	.workbench-file-picker:hover {
   625	  border-color: rgba(122, 224, 210, 0.55);
   626	  background: rgba(15, 32, 45, 0.88);
   627	  box-shadow: var(--shadow-sm);
   628	  transform: translateY(-1px);
   629	}
   630	
   631	.workbench-toolbar-button:active,
   632	.workbench-run-button:active,
   633	.workbench-file-picker:active {
   634	  transform: translateY(0);
   635	}
   636	
   637	.workbench-toolbar-button:focus-visible,
   638	.workbench-run-button:focus-visible,
   639	.workbench-file-picker:focus-visible {
   640	  outline: none;
   641	  border-color: var(--accent);
   642	  box-shadow:
   643	    0 0 0 1px rgba(40, 244, 255, 0.45),
   644	    0 0 0 4px rgba(40, 244, 255, 0.14);
   645	}
   646	
   647	.workbench-toolbar-button[disabled],
   648	.workbench-run-button[disabled],
   649	.workbench-file-picker[disabled] {
   650	  opacity: 0.55;
   651	  cursor: not-allowed;
   652	  transform: none;
   653	  box-shadow: none;
   654	}
   655	
   656	.workbench-toolbar-button.is-primary,
   657	.workbench-run-button {
   658	  background: linear-gradient(135deg, rgba(24, 153, 132, 0.95), rgba(26, 94, 119, 0.95));
   659	  border-color: rgba(145, 255, 230, 0.35);
   660	}
   661	
   662	.workbench-toolbar-button.is-primary:hover,
   663	.workbench-run-button:hover {
   664	  background: linear-gradient(135deg, rgba(30, 180, 155, 0.98), rgba(34, 112, 140, 0.98));
   665	}
   666	
   667	.workbench-file-picker {
   668	  cursor: pointer;
   669	  display: inline-flex;
   670	  align-items: center;
   671	  gap: 0.5rem;
   672	}
   673	
   674	.workbench-file-picker input {
   675	  display: none;
   676	}
   677	
   678	.workbench-packet-source-status {
   679	  margin: 0 0 1rem;
   680	  padding: 0.8rem 1rem;
   681	  border-radius: 16px;
   682	  border: 1px solid rgba(137, 211, 230, 0.16);
   683	  background: rgba(8, 18, 29, 0.82);
   684	  color: #dff9f2;
   685	}
   686	
   687	.workbench-field {
   688	  display: flex;
   689	  flex-direction: column;
   690	  gap: 0.4rem;
   691	}
   692	
   693	.workbench-field span {
   694	  font-weight: 700;
   695	  color: #f4fbff;
   696	}
   697	
   698	.workbench-field input,
   699	.workbench-field textarea {
   700	  width: 100%;
   701	  border: 1px solid rgba(143, 214, 233, 0.2);
   702	  border-radius: 16px;
   703	  background: rgba(8, 17, 28, 0.82);
   704	  color: #edf8ff;
   705	  padding: 0.85rem 1rem;
   706	  font: inherit;
   707	  transition:
   708	    border-color var(--duration-fast) var(--ease-standard),
   709	    box-shadow var(--duration-fast) var(--ease-standard),
   710	    background var(--duration-fast) var(--ease-standard);
   711	  resize: vertical;
   712	}
   713	
   714	.workbench-field textarea {
   715	  min-height: 7rem;
   716	}
   717	
   718	.workbench-field input:focus,
   719	.workbench-field textarea:focus {
   720	  outline: none;
   721	  border-color: var(--accent);
   722	  box-shadow:
   723	    0 0 0 1px rgba(40, 244, 255, 0.38),
   724	    0 0 0 4px rgba(40, 244, 255, 0.12);
   725	  background: rgba(10, 22, 34, 0.92);
   726	}
   727	
   728	.workbench-field input:hover:not(:focus),
   729	.workbench-field textarea:hover:not(:focus) {
   730	  border-color: rgba(143, 214, 233, 0.38);
   731	}
   732	
   733	.workbench-field-stack textarea {
   734	  min-height: 22rem;
   735	}
   736	
   737	.workbench-field small {
   738	  color: rgba(206, 223, 236, 0.72);
   739	}
   740	
   741	.workbench-form-grid {
   742	  display: grid;
   743	  grid-template-columns: repeat(4, minmax(0, 1fr));
   744	  gap: 0.85rem;
   745	  margin-bottom: 1rem;
   746	}
   747	
   748	.workbench-form-grid-wide {
   749	  grid-template-columns: repeat(2, minmax(0, 1fr));
   750	}
   751	
   752	.workbench-checkbox-field {
   753	  justify-content: center;
   754	  padding: 0.5rem 0.85rem;
   755	  border-radius: 16px;
   756	  background: rgba(10, 23, 36, 0.72);
   757	}
   758	
   759	.workbench-checkbox-field input {
   760	  width: auto;
   761	  margin: 0;
   762	}
   763	
   764	.workbench-checkbox-field span {
   765	  font-weight: 600;
   766	}
   767	
   768	.workbench-details {
   769	  border: 1px solid rgba(142, 208, 229, 0.15);
   770	  border-radius: 18px;
   771	  background: rgba(6, 16, 26, 0.72);
   772	  padding: 0.85rem 1rem 1rem;
   773	}
   774	
   775	.workbench-details summary {
   776	  cursor: pointer;
   777	  font-weight: 700;
   778	  color: #f4fbff;
   779	}
   780	
   781	.workbench-dev-details summary {
   782	  color: rgba(221, 234, 246, 0.86);
   783	}
   784	
   785	.workbench-action-row {
   786	  display: flex;
   787	  align-items: center;
   788	  gap: 1rem;
   789	  margin-top: 1rem;
   790	}
   791	
   792	.workbench-request-status {
   793	  margin: 0;
   794	  color: rgba(236, 245, 255, 0.8);
   795	}
   796	
   797	.workbench-request-status[data-tone="success"] {
   798	  color: #a3ffd6;
   799	}
   800	
   801	.workbench-request-status[data-tone="warning"] {
   802	  color: #ffe198;
   803	}
   804	
   805	.workbench-request-status[data-tone="error"] {
   806	  color: #ff9e9e;
   807	}
   808	
   809	.workbench-summary-grid {
   810	  display: grid;
   811	  grid-template-columns: repeat(4, minmax(0, 1fr));
   812	  gap: 0.85rem;
   813	  margin-bottom: 1rem;
   814	}
   815	
   816	.workbench-handoff-board {
   817	  margin-bottom: 1rem;
   818	  padding: 1rem;
   819	  border: 1px solid rgba(160, 214, 120, 0.18);
   820	  border-radius: 20px;
   821	  background:
   822	    linear-gradient(135deg, rgba(17, 29, 20, 0.95), rgba(9, 17, 25, 0.92)),
   823	    radial-gradient(circle at 82% 16%, rgba(160, 214, 120, 0.12), transparent 18rem);
   824	}
   825	
   826	.workbench-handoff-note-field textarea {
   827	  min-height: 6.5rem;
   828	}
   829	
   830	.workbench-handoff-actions {
   831	  display: flex;
   832	  align-items: center;
   833	  justify-content: space-between;
   834	  gap: 1rem;
   835	}
   836	
   837	.workbench-onboarding-board {
   838	  margin-bottom: 1rem;
   839	  padding: 1rem;
   840	  border: 1px solid rgba(122, 224, 210, 0.16);
   841	  border-radius: 20px;
   842	  background:
   843	    linear-gradient(135deg, rgba(9, 22, 34, 0.94), rgba(7, 15, 25, 0.9)),
   844	    radial-gradient(circle at 18% 18%, rgba(122, 224, 210, 0.12), transparent 20rem);
   845	}
   846	
   847	.workbench-onboarding-grid {
   848	  display: grid;
   849	  grid-template-columns: repeat(3, minmax(0, 1fr));
   850	  gap: 0.85rem;
   851	  margin-bottom: 0.85rem;
   852	}
   853	
   854	.workbench-onboarding-note {
   855	  margin: 0.45rem 0 0;
   856	  color: rgba(221, 234, 246, 0.78);
   857	  font-size: 0.8rem;
   858	}
   859	
   860	.workbench-onboarding-footer {
   861	  display: grid;
   862	  grid-template-columns: repeat(2, minmax(0, 1fr));
   863	  gap: 0.85rem;
   864	}
   865	
   866	.workbench-onboarding-footer > div {
   867	  border: 1px solid rgba(137, 211, 230, 0.14);
   868	  border-radius: 16px;
   869	  background: rgba(8, 18, 29, 0.74);
   870	  padding: 0.9rem 1rem;
   871	}
   872	
   873	.workbench-fingerprint-board {
   874	  margin-bottom: 1rem;
   875	  padding: 1rem;
   876	  border: 1px solid rgba(137, 211, 230, 0.16);
   877	  border-radius: 20px;
   878	  background:
   879	    linear-gradient(135deg, rgba(10, 22, 34, 0.94), rgba(8, 16, 27, 0.9)),
   880	    radial-gradient(circle at 82% 14%, rgba(79, 184, 255, 0.1), transparent 18rem);
   881	}
   882	
   883	.workbench-fingerprint-meta {
   884	  display: grid;
   885	  grid-template-columns: repeat(4, minmax(0, 1fr));
   886	  gap: 0.85rem;
   887	  margin-bottom: 0.85rem;
   888	}
   889	
   890	.workbench-fingerprint-panels {
   891	  display: grid;
   892	  grid-template-columns: repeat(2, minmax(0, 1fr));
   893	  gap: 0.85rem;
   894	}
   895	
   896	.workbench-fingerprint-panel {
   897	  border: 1px solid rgba(137, 211, 230, 0.14);
   898	  border-radius: 18px;
   899	  background: rgba(8, 18, 29, 0.78);
   900	  padding: 0.95rem 1rem;
   901	}
   902	
   903	.workbench-fingerprint-panel-header {
   904	  display: flex;
   905	  align-items: flex-start;
   906	  justify-content: space-between;
   907	  gap: 0.75rem;
   908	  margin-bottom: 0.75rem;
   909	}
   910	
   911	.workbench-fingerprint-panel-header h4 {
   912	  margin: 0.18rem 0 0;
   913	  color: #f7fcff;
   914	  font-size: 0.95rem;
   915	}
   916	
   917	.workbench-fingerprint-count {
   918	  display: inline-flex;
   919	  align-items: center;
   920	  padding: 0.38rem 0.68rem;
   921	  border-radius: 999px;
   922	  background: rgba(18, 53, 78, 0.52);
   923	  color: #d7f3ff;
   924	  font-size: 0.76rem;
   925	  font-weight: 700;
   926	}
   927	
   928	.workbench-fingerprint-list {
   929	  display: grid;
   930	  gap: 0.75rem;
   931	}
   932	
   933	.workbench-fingerprint-item {
   934	  border: 1px solid rgba(137, 211, 230, 0.14);
   935	  border-radius: 16px;
   936	  background: rgba(6, 14, 23, 0.82);
   937	  padding: 0.85rem 0.9rem;
   938	}
   939	
   940	.workbench-fingerprint-item.is-empty {
   941	  border-style: dashed;
   942	  background: rgba(6, 14, 23, 0.58);
   943	}
   944	
   945	.workbench-fingerprint-item-header {
   946	  display: flex;
   947	  align-items: flex-start;
   948	  justify-content: space-between;
   949	  gap: 0.75rem;
   950	}
   951	
   952	.workbench-fingerprint-item-title {
   953	  color: #f7fcff;
   954	  font-size: 0.9rem;
   955	}
   956	
   957	.workbench-fingerprint-chip-row {
   958	  display: flex;
   959	  flex-wrap: wrap;
   960	  justify-content: flex-end;
   961	  gap: 0.4rem;
   962	}
   963	
   964	.workbench-fingerprint-chip {
   965	  display: inline-flex;
   966	  align-items: center;
   967	  border-radius: 999px;
   968	  padding: 0.26rem 0.58rem;
   969	  background: rgba(13, 29, 43, 0.86);
   970	  color: #e6f5ff;
   971	  font-size: 0.72rem;
   972	  font-weight: 700;
   973	}
   974	
   975	.workbench-fingerprint-chip[data-tone="role"] {
   976	  background: rgba(52, 81, 38, 0.68);
   977	  color: #d9ffc8;
   978	}
   979	
   980	.workbench-fingerprint-chip[data-tone="signal"] {
   981	  background: rgba(22, 56, 84, 0.76);
   982	  color: #cfeeff;
   983	}
   984	
   985	.workbench-fingerprint-chip[data-tone="shape"] {
   986	  background: rgba(61, 39, 84, 0.72);
   987	  color: #ead9ff;
   988	}
   989	
   990	.workbench-fingerprint-chip[data-tone="unit"] {
   991	  background: rgba(84, 58, 18, 0.7);
   992	  color: #ffe7bc;
   993	}
   994	
   995	.workbench-fingerprint-chip[data-tone="blocked"] {
   996	  background: rgba(96, 50, 15, 0.74);
   997	  color: #ffe7bc;
   998	}
   999	
  1000	.workbench-fingerprint-chip[data-tone="ready"] {
  1001	  background: rgba(27, 88, 67, 0.76);
  1002	  color: #d9fff1;
  1003	}
  1004	
  1005	.workbench-fingerprint-item-detail,
  1006	.workbench-fingerprint-empty {
  1007	  margin: 0.55rem 0 0;
  1008	  color: rgba(221, 234, 246, 0.8);
  1009	  font-size: 0.8rem;
  1010	  word-break: break-word;
  1011	}
  1012	
  1013	.workbench-actions-board {
  1014	  margin-bottom: 1rem;
  1015	  padding: 1rem;
  1016	  border: 1px solid rgba(255, 176, 55, 0.16);
  1017	  border-radius: 20px;
  1018	  background:
  1019	    linear-gradient(135deg, rgba(18, 20, 31, 0.94), rgba(10, 14, 23, 0.9)),
  1020	    radial-gradient(circle at 16% 18%, rgba(255, 176, 55, 0.1), transparent 18rem);
  1021	}
  1022	
  1023	.workbench-actions-grid {
  1024	  display: grid;
  1025	  grid-template-columns: repeat(3, minmax(0, 1fr));
  1026	  gap: 0.85rem;
  1027	}
  1028	
  1029	.workbench-actions-panel {
  1030	  border: 1px solid rgba(255, 176, 55, 0.14);
  1031	  border-radius: 18px;
  1032	  background: rgba(9, 15, 24, 0.8);
  1033	  padding: 0.95rem 1rem;
  1034	}
  1035	
  1036	.workbench-actions-panel-header {
  1037	  display: flex;
  1038	  align-items: flex-start;
  1039	  justify-content: space-between;
  1040	  gap: 0.75rem;
  1041	  margin-bottom: 0.75rem;
  1042	}
  1043	
  1044	.workbench-actions-panel-header h4 {
  1045	  margin: 0.18rem 0 0;
  1046	  color: #fff7ea;
  1047	  font-size: 0.95rem;
  1048	}
  1049	
  1050	.workbench-actions-list {
  1051	  display: grid;
  1052	  gap: 0.75rem;
  1053	}
  1054	
  1055	.workbench-actions-item {
  1056	  border: 1px solid rgba(255, 176, 55, 0.14);
  1057	  border-radius: 16px;
  1058	  background: rgba(17, 14, 10, 0.78);
  1059	  padding: 0.82rem 0.9rem;
  1060	}
  1061	
  1062	.workbench-actions-item-header {
  1063	  display: flex;
  1064	  align-items: flex-start;
  1065	  justify-content: space-between;
  1066	  gap: 0.75rem;
  1067	}
  1068	
  1069	.workbench-actions-item-title {
  1070	  color: #fff7ea;
  1071	  font-size: 0.88rem;
  1072	}
  1073	
  1074	.workbench-actions-item-detail {
  1075	  margin: 0.55rem 0 0;
  1076	  color: rgba(244, 231, 214, 0.82);
  1077	  font-size: 0.8rem;
  1078	  word-break: break-word;
  1079	}
  1080	
  1081	.workbench-schema-workspace {
  1082	  margin-bottom: 1rem;
  1083	  padding: 1rem;
  1084	  border: 1px solid rgba(255, 176, 55, 0.16);
  1085	  border-radius: 20px;
  1086	  background:
  1087	    linear-gradient(135deg, rgba(21, 20, 15, 0.94), rgba(10, 14, 23, 0.9)),
  1088	    radial-gradient(circle at 18% 18%, rgba(255, 176, 55, 0.1), transparent 18rem);
  1089	}
  1090	
  1091	.workbench-schema-workspace-list {
  1092	  display: grid;
  1093	  gap: 0.85rem;
  1094	}
  1095	
  1096	.workbench-schema-card {
  1097	  border: 1px solid rgba(255, 176, 55, 0.14);
  1098	  border-radius: 18px;
  1099	  background: rgba(13, 14, 10, 0.82);
  1100	  padding: 0.95rem 1rem;
  1101	}
  1102	
  1103	.workbench-schema-card.is-empty {
  1104	  border-style: dashed;
  1105	  background: rgba(13, 14, 10, 0.62);
  1106	}
  1107	
  1108	.workbench-schema-card-header {
  1109	  display: flex;
  1110	  align-items: flex-start;
  1111	  justify-content: space-between;
  1112	  gap: 0.75rem;
  1113	}
  1114	
  1115	.workbench-schema-card strong {
  1116	  color: #fff7ea;
  1117	  font-size: 0.92rem;
  1118	}
  1119	
  1120	.workbench-schema-card p {
  1121	  margin: 0.45rem 0 0;
  1122	  color: rgba(244, 231, 214, 0.82);
  1123	  font-size: 0.82rem;
  1124	}
  1125	
  1126	.workbench-schema-card-meta {
  1127	  display: grid;
  1128	  gap: 0.32rem;
  1129	  margin-top: 0.8rem;
  1130	}
  1131	
  1132	.workbench-schema-card-meta span {
  1133	  color: rgba(240, 225, 202, 0.76);
  1134	  font-size: 0.78rem;
  1135	}
  1136	
  1137	.workbench-schema-workspace-footer {
  1138	  display: flex;
  1139	  align-items: center;
  1140	  justify-content: space-between;
  1141	  gap: 1rem;
  1142	  margin-top: 0.95rem;
  1143	}
  1144	
  1145	.workbench-schema-workspace-note {
  1146	  margin: 0;
  1147	  color: rgba(244, 231, 214, 0.78);
  1148	  font-size: 0.82rem;
  1149	}
  1150	
  1151	.workbench-schema-workspace-actions {
  1152	  display: flex;
  1153	  flex-wrap: wrap;
  1154	  gap: 0.65rem;
  1155	}
  1156	
  1157	.workbench-clarification-workspace {
  1158	  margin-bottom: 1rem;
  1159	  padding: 1rem;
  1160	  border: 1px solid rgba(122, 224, 210, 0.16);
  1161	  border-radius: 20px;
  1162	  background:
  1163	    linear-gradient(135deg, rgba(9, 24, 31, 0.94), rgba(7, 15, 23, 0.9)),
  1164	    radial-gradient(circle at 84% 18%, rgba(122, 224, 210, 0.11), transparent 18rem);
  1165	}
  1166	
  1167	.workbench-clarification-workspace-list {
  1168	  display: grid;
  1169	  gap: 0.85rem;
  1170	}
  1171	
  1172	.workbench-clarification-card {
  1173	  border: 1px solid rgba(122, 224, 210, 0.14);
  1174	  border-radius: 18px;
  1175	  background: rgba(8, 18, 29, 0.8);
  1176	  padding: 0.95rem 1rem;
  1177	}
  1178	
  1179	.workbench-clarification-card.is-empty {
  1180	  border-style: dashed;
  1181	  background: rgba(8, 18, 29, 0.62);
  1182	}
  1183	
  1184	.workbench-clarification-card strong {
  1185	  color: #f7fcff;
  1186	  font-size: 0.92rem;
  1187	}
  1188	
  1189	.workbench-clarification-card p {
  1190	  margin: 0.45rem 0 0;
  1191	  color: rgba(221, 234, 246, 0.82);
  1192	  font-size: 0.82rem;
  1193	}
  1194	
  1195	.workbench-clarification-card-header {
  1196	  display: flex;
  1197	  align-items: flex-start;
  1198	  justify-content: space-between;
  1199	  gap: 0.75rem;
  1200	}
  1201	
  1202	.workbench-clarification-card-meta {
  1203	  display: grid;
  1204	  gap: 0.32rem;
  1205	  margin: 0.8rem 0;
  1206	}
  1207	
  1208	.workbench-clarification-card-meta span {
  1209	  color: rgba(210, 231, 242, 0.76);
  1210	  font-size: 0.78rem;
  1211	}
  1212	
  1213	.workbench-clarification-card textarea {
  1214	  min-height: 6.5rem;
  1215	  border: 1px solid rgba(122, 224, 210, 0.16);
  1216	  border-radius: 14px;
  1217	  background: rgba(5, 10, 18, 0.92);
  1218	  color: #f6fbff;
  1219	  padding: 0.8rem 0.9rem;
  1220	  font: inherit;
  1221	  resize: vertical;
  1222	}
  1223	
  1224	.workbench-clarification-card textarea::placeholder {
  1225	  color: rgba(214, 229, 240, 0.4);
  1226	}
  1227	
  1228	.workbench-clarification-card textarea:focus-visible {
  1229	  outline: 2px solid rgba(122, 224, 210, 0.62);
  1230	  outline-offset: 2px;
  1231	}
  1232	
  1233	.workbench-clarification-card textarea:disabled {
  1234	  cursor: not-allowed;
  1235	  opacity: 0.7;
  1236	}
  1237	
  1238	.workbench-clarification-workspace-footer {
  1239	  display: flex;
  1240	  align-items: center;
  1241	  justify-content: space-between;
  1242	  gap: 1rem;
  1243	  margin-top: 0.95rem;
  1244	}
  1245	
  1246	.workbench-clarification-workspace-note {
  1247	  margin: 0;
  1248	  color: rgba(221, 234, 246, 0.78);
  1249	  font-size: 0.82rem;
  1250	}
  1251	
  1252	.workbench-clarification-workspace-actions {
  1253	  display: flex;
  1254	  flex-wrap: wrap;
  1255	  gap: 0.65rem;
  1256	}
  1257	
  1258	.workbench-summary-card,
  1259	.workbench-output-card {
  1260	  border: 1px solid rgba(137, 211, 230, 0.16);
  1261	  border-radius: 18px;
  1262	  background: rgba(8, 18, 29, 0.78);
  1263	  padding: 1rem;
  1264	}
  1265	
  1266	.workbench-summary-label {
  1267	  display: block;
  1268	  color: rgba(213, 228, 240, 0.72);
  1269	  margin-bottom: 0.35rem;
  1270	}
  1271	
  1272	.workbench-summary-card strong {
  1273	  color: #f7fcff;
  1274	  font-size: 1.05rem;
  1275	}
  1276	
  1277	.workbench-summary-note {
  1278	  margin: 0.4rem 0 0;
  1279	  color: rgba(213, 228, 240, 0.78);
  1280	  font-size: 0.8rem;
  1281	}
  1282	
  1283	.workbench-visual-board {
  1284	  margin-bottom: 1rem;
  1285	  padding: 1rem;
  1286	  border: 1px solid rgba(255, 176, 55, 0.18);
  1287	  border-radius: 20px;
  1288	  background:
  1289	    linear-gradient(135deg, rgba(14, 26, 40, 0.96), rgba(7, 14, 23, 0.94)),
  1290	    radial-gradient(circle at 12% 12%, rgba(255, 176, 55, 0.12), transparent 18rem);
  1291	}
  1292	
  1293	.workbench-history-board {
  1294	  margin-bottom: 1rem;
  1295	  padding: 1rem;
  1296	  border: 1px solid rgba(137, 211, 230, 0.16);
  1297	  border-radius: 20px;
  1298	  background: rgba(8, 18, 29, 0.82);
  1299	}
  1300	
  1301	.workbench-packet-history-board {
  1302	  margin-top: 1rem;
  1303	}
  1304	
  1305	.workbench-visual-header {
  1306	  display: flex;
  1307	  align-items: flex-start;
  1308	  justify-content: space-between;
  1309	  gap: 1rem;
  1310	  margin-bottom: 0.75rem;
  1311	}
  1312	
  1313	.workbench-visual-header h3 {
  1314	  color: #fff;
  1315	  font-size: 1rem;
  1316	}
  1317	
  1318	.workbench-visual-badge {
  1319	  display: inline-flex;
  1320	  align-items: center;
  1321	  justify-content: center;
  1322	  min-width: 7.25rem;
  1323	  padding: 0.65rem 0.9rem;
  1324	  border-radius: 999px;
  1325	  border: 1px solid rgba(255, 255, 255, 0.12);
  1326	  background: rgba(9, 21, 32, 0.82);
  1327	  color: #edf8ff;
  1328	  font-weight: 700;
  1329	}
  1330	
  1331	.workbench-visual-badge[data-state="idle"] {
  1332	  color: rgba(221, 234, 246, 0.9);
  1333	}
  1334	
  1335	.workbench-visual-badge[data-state="ready"] {
  1336	  color: #a3ffd6;
  1337	  border-color: rgba(145, 255, 230, 0.35);
  1338	  background: rgba(24, 153, 132, 0.16);
  1339	}
  1340	
  1341	.workbench-visual-badge[data-state="blocked"] {
  1342	  color: #ffe198;
  1343	  border-color: rgba(255, 176, 55, 0.35);
  1344	  background: rgba(255, 176, 55, 0.12);
  1345	}
  1346	
  1347	.workbench-visual-badge[data-state="archived"] {
  1348	  color: #9de7ff;
  1349	  border-color: rgba(79, 184, 255, 0.3);
  1350	  background: rgba(61, 126, 255, 0.14);
  1351	}
  1352	
  1353	.workbench-visual-summary {
  1354	  margin: 0 0 1rem;
  1355	  color: rgba(240, 247, 255, 0.92);
  1356	  font-size: 0.95rem;
  1357	}
  1358	
  1359	.workbench-history-view-bar {
  1360	  display: flex;
  1361	  align-items: center;
  1362	  justify-content: space-between;
  1363	  gap: 1rem;
  1364	  margin: 0 0 1rem;
  1365	  padding: 0.85rem 1rem;
  1366	  border: 1px solid rgba(137, 211, 230, 0.14);
  1367	  border-radius: 18px;
  1368	  background: rgba(8, 18, 29, 0.72);
  1369	}
  1370	
  1371	.workbench-history-view-bar strong {
  1372	  color: #f7fcff;
  1373	  font-size: 0.88rem;
  1374	}
  1375	
  1376	.workbench-packet-draft-bar {
  1377	  display: flex;
  1378	  align-items: flex-start;
  1379	  justify-content: space-between;
  1380	  gap: 1rem;
  1381	  margin: 0 0 1rem;
  1382	  padding: 0.85rem 1rem;
  1383	  border: 1px solid rgba(137, 211, 230, 0.14);
  1384	  border-radius: 18px;
  1385	  background: rgba(10, 19, 30, 0.78);
  1386	}
  1387	
  1388	.workbench-packet-draft-bar strong {
  1389	  display: block;
  1390	  color: #f7fcff;
  1391	  font-size: 0.86rem;
  1392	  margin-bottom: 0.35rem;
  1393	}
  1394	
  1395	.workbench-packet-draft-note {
  1396	  margin: 0;
  1397	  color: rgba(213, 228, 240, 0.8);
  1398	  font-size: 0.8rem;
  1399	  max-width: 52rem;
  1400	}
  1401	
  1402	.workbench-history-compare-bar {
  1403	  margin: 0 0 1rem;
  1404	  padding: 0.95rem 1rem;
  1405	  border: 1px solid rgba(255, 176, 55, 0.16);
  1406	  border-radius: 18px;
  1407	  background: rgba(36, 23, 10, 0.34);
  1408	}
  1409	
  1410	.workbench-history-compare-summary {
  1411	  margin: 0 0 0.8rem;
  1412	  color: rgba(255, 238, 205, 0.92);
  1413	  font-size: 0.86rem;
  1414	}
  1415	
  1416	.workbench-history-compare-grid {
  1417	  display: grid;
  1418	  grid-template-columns: repeat(4, minmax(0, 1fr));
  1419	  gap: 0.75rem;
  1420	}
  1421	
  1422	.workbench-history-compare-card {
  1423	  border: 1px solid rgba(255, 176, 55, 0.14);
  1424	  border-radius: 16px;
  1425	  background: rgba(11, 17, 27, 0.76);
  1426	  padding: 0.85rem 0.9rem;
  1427	}
  1428	
  1429	.workbench-history-compare-label {
  1430	  display: block;
  1431	  margin-bottom: 0.35rem;
  1432	  color: rgba(255, 220, 164, 0.72);
  1433	  font-size: 0.74rem;
  1434	}
  1435	
  1436	.workbench-history-compare-card strong {
  1437	  display: block;
  1438	  color: #fff3d5;
  1439	  font-size: 0.94rem;
  1440	}
  1441	
  1442	.workbench-history-compare-card p {
  1443	  margin: 0.32rem 0 0;
  1444	  color: rgba(240, 232, 218, 0.8);
  1445	  font-size: 0.78rem;
  1446	}
  1447	
  1448	.workbench-history-detail-board {
  1449	  margin: 0 0 1rem;
  1450	  padding: 1rem;
  1451	  border: 1px solid rgba(137, 211, 230, 0.14);
  1452	  border-radius: 18px;
  1453	  background: rgba(10, 19, 30, 0.84);
  1454	}
  1455	
  1456	.workbench-history-detail-grid {
  1457	  display: grid;
  1458	  grid-template-columns: repeat(2, minmax(0, 1fr));
  1459	  gap: 0.85rem;
  1460	}
  1461	
  1462	.workbench-history-detail-card {
  1463	  border: 1px solid rgba(137, 211, 230, 0.14);
  1464	  border-radius: 18px;
  1465	  background: rgba(7, 14, 23, 0.86);
  1466	  padding: 0.95rem 1rem;
  1467	}
  1468	
  1469	.workbench-history-detail-card-header {
  1470	  display: flex;
  1471	  align-items: flex-start;
  1472	  justify-content: space-between;
  1473	  gap: 0.75rem;
  1474	  margin-bottom: 0.85rem;
  1475	}
  1476	
  1477	.workbench-history-detail-card h4 {
  1478	  margin: 0.18rem 0 0;
  1479	  color: #f7fcff;
  1480	  font-size: 0.95rem;
  1481	}
  1482	
  1483	.workbench-history-detail-kicker {
  1484	  margin: 0;
  1485	  color: rgba(202, 220, 232, 0.72);
  1486	  font-size: 0.76rem;
  1487	  letter-spacing: 0.04em;
  1488	  text-transform: uppercase;
  1489	}
  1490	
  1491	.workbench-history-detail-chip {
  1492	  display: inline-flex;
  1493	  align-items: center;
  1494	  padding: 0.32rem 0.62rem;
  1495	  border-radius: 999px;
  1496	  border: 1px solid rgba(145, 255, 230, 0.2);
  1497	  background: rgba(20, 79, 94, 0.28);
  1498	  color: #dbfff5;
  1499	  font-size: 0.72rem;
  1500	  font-weight: 700;
  1501	}
  1502	
  1503	.workbench-history-detail-body {
  1504	  display: grid;
  1505	  gap: 0.65rem;
  1506	}
  1507	
  1508	.workbench-history-detail-row {
  1509	  display: flex;
  1510	  align-items: baseline;
  1511	  justify-content: space-between;
  1512	  gap: 1rem;
  1513	  padding-bottom: 0.55rem;
  1514	  border-bottom: 1px solid rgba(137, 211, 230, 0.08);
  1515	}
  1516	
  1517	.workbench-history-detail-row:last-child {
  1518	  padding-bottom: 0;
  1519	  border-bottom: 0;
  1520	}
  1521	
  1522	.workbench-history-detail-label {
  1523	  color: rgba(213, 228, 240, 0.72);
  1524	  font-size: 0.8rem;
  1525	}
  1526	
  1527	.workbench-history-detail-value {
  1528	  color: #f7fcff;
  1529	  font-size: 0.86rem;
  1530	  text-align: right;
  1531	}
  1532	
  1533	.workbench-history-detail-value[data-diff="changed"] {
  1534	  color: #fff3d5;
  1535	}
  1536	
  1537	.workbench-history-detail-value[data-diff="same"] {
  1538	  color: #aef8ea;
  1539	}
  1540	
  1541	.workbench-history-return-button {
  1542	  border: 1px solid rgba(122, 224, 210, 0.28);
  1543	  border-radius: 999px;
  1544	  background: rgba(9, 21, 32, 0.7);
  1545	  color: #eff8ff;
  1546	  padding: 0.55rem 0.9rem;
  1547	  font: inherit;
  1548	}
  1549	
  1550	.workbench-history-return-button:disabled {
  1551	  cursor: not-allowed;
  1552	  opacity: 0.52;
  1553	}
  1554	
  1555	.workbench-history-return-button:not(:disabled) {
  1556	  cursor: pointer;
  1557	  border-color: rgba(145, 255, 230, 0.35);
  1558	  background: linear-gradient(135deg, rgba(24, 153, 132, 0.95), rgba(26, 94, 119, 0.95));
  1559	}
  1560	
  1561	.workbench-history-note {
  1562	  color: rgba(213, 228, 240, 0.72);
  1563	  font-size: 0.8rem;
  1564	  text-align: right;
  1565	}
  1566	
  1567	.workbench-history-grid {
  1568	  display: grid;
  1569	  grid-template-columns: repeat(3, minmax(0, 1fr));
  1570	  gap: 0.85rem;
  1571	}
  1572	
  1573	.workbench-history-card {
  1574	  width: 100%;
  1575	  border: 1px solid rgba(137, 211, 230, 0.16);
  1576	  border-radius: 18px;
  1577	  background: rgba(8, 18, 29, 0.82);
  1578	  padding: 0.9rem 1rem;
  1579	  text-align: left;
  1580	  font: inherit;
  1581	  cursor: pointer;
  1582	  transition: border-color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
  1583	}
  1584	
  1585	.workbench-history-card:hover {
  1586	  border-color: rgba(145, 255, 230, 0.28);
  1587	  transform: translateY(-1px);
  1588	}
  1589	
  1590	.workbench-history-card:focus-visible {
  1591	  outline: 2px solid rgba(157, 231, 255, 0.88);
  1592	  outline-offset: 2px;
  1593	}
  1594	
  1595	.workbench-history-card[data-selected="true"] {
  1596	  border-color: rgba(145, 255, 230, 0.34);
  1597	  box-shadow: 0 0 0 1px rgba(145, 255, 230, 0.12);
  1598	}
  1599	
  1600	.workbench-history-card strong {
  1601	  display: block;
  1602	  color: #fff;
  1603	  font-size: 0.98rem;
  1604	  margin-bottom: 0.35rem;
  1605	}
  1606	
  1607	.workbench-history-card p {
  1608	  margin: 0.2rem 0 0;
  1609	  color: rgba(221, 234, 246, 0.82);
  1610	  font-size: 0.8rem;
  1611	}
  1612	
  1613	.workbench-history-action {
  1614	  display: inline-flex;
  1615	  margin-top: 0.7rem;
  1616	  color: #9de7ff;
  1617	  font-size: 0.75rem;
  1618	  font-weight: 700;
  1619	}
  1620	
  1621	.workbench-history-card[data-selected="true"] .workbench-history-action {
  1622	  color: #a3ffd6;
  1623	}
  1624	
  1625	.workbench-history-meta {
  1626	  display: flex;
  1627	  flex-wrap: wrap;
  1628	  gap: 0.4rem;
  1629	  margin-bottom: 0.5rem;
  1630	}
  1631	
  1632	.workbench-history-chip {
  1633	  display: inline-flex;
  1634	  align-items: center;
  1635	  justify-content: center;
  1636	  padding: 0.2rem 0.55rem;
  1637	  border-radius: 999px;
  1638	  background: rgba(221, 234, 246, 0.1);
  1639	  color: #edf8ff;
  1640	  font-size: 0.72rem;
  1641	}
  1642	
  1643	.workbench-history-chip[data-state="ready"] {
  1644	  background: rgba(24, 153, 132, 0.18);
  1645	  color: #a3ffd6;
  1646	}
  1647	
  1648	.workbench-history-chip[data-state="blocked"] {
  1649	  background: rgba(255, 176, 55, 0.16);
  1650	  color: #ffe198;
  1651	}
  1652	
  1653	.workbench-history-chip[data-state="failure"] {
  1654	  background: rgba(255, 82, 82, 0.16);
  1655	  color: #ffb3b3;
  1656	}
  1657	
  1658	.workbench-history-chip[data-state="archived"] {
  1659	  background: rgba(61, 126, 255, 0.18);
  1660	  color: #9de7ff;
  1661	}
  1662	
  1663	.workbench-history-card.is-empty {
  1664	  grid-column: 1 / -1;
  1665	  text-align: center;
  1666	}
  1667	
  1668	.workbench-spotlight-grid {
  1669	  display: grid;
  1670	  grid-template-columns: repeat(2, minmax(0, 1fr));
  1671	  gap: 0.85rem;
  1672	  margin-bottom: 1rem;
  1673	}
  1674	
  1675	.workbench-spotlight-card {
  1676	  border: 1px solid rgba(137, 211, 230, 0.16);
  1677	  border-radius: 18px;
  1678	  background: rgba(8, 18, 29, 0.82);
  1679	  padding: 0.95rem 1rem;
  1680	}
  1681	
  1682	.workbench-spotlight-label {
  1683	  display: block;
  1684	  margin-bottom: 0.35rem;
  1685	  color: rgba(213, 228, 240, 0.72);
  1686	}
  1687	
  1688	.workbench-spotlight-card strong {
  1689	  display: block;
  1690	  color: #fff;
  1691	  font-size: 1.05rem;
  1692	  margin-bottom: 0.35rem;
  1693	}
  1694	
  1695	.workbench-spotlight-card p {
  1696	  margin: 0;
  1697	  color: rgba(221, 234, 246, 0.82);
  1698	  font-size: 0.84rem;
  1699	}
  1700	
  1701	.workbench-stage-strip {
  1702	  margin: 0;
  1703	  padding: 0;
  1704	  list-style: none;
  1705	  display: grid;
  1706	  grid-template-columns: repeat(6, minmax(0, 1fr));
  1707	  gap: 0.75rem;
  1708	}
  1709	
  1710	.workbench-stage {
  1711	  display: grid;
  1712	  grid-template-columns: auto 1fr;
  1713	  gap: 0.7rem;
  1714	  align-items: start;
  1715	  padding: 0.8rem 0.9rem;
  1716	  border-radius: 18px;
  1717	  border: 1px solid rgba(137, 211, 230, 0.14);
  1718	  background: rgba(8, 18, 29, 0.78);
  1719	}
  1720	
  1721	.workbench-stage strong {
  1722	  color: #f7fcff;
  1723	  display: block;
  1724	  margin-bottom: 0.25rem;
  1725	}
  1726	
  1727	.workbench-stage p {
  1728	  margin: 0;
  1729	  color: rgba(221, 234, 246, 0.82);
  1730	  font-size: 0.78rem;
  1731	}
  1732	
  1733	.workbench-stage-step {
  1734	  display: inline-flex;
  1735	  align-items: center;
  1736	  justify-content: center;
  1737	  width: 1.8rem;
  1738	  height: 1.8rem;
  1739	  border-radius: 999px;
  1740	  background: rgba(221, 234, 246, 0.12);
  1741	  color: #edf8ff;
  1742	  font-weight: 700;
  1743	}
  1744	
  1745	.workbench-stage[data-state="idle"] .workbench-stage-step {
  1746	  background: rgba(221, 234, 246, 0.12);
  1747	}
  1748	
  1749	.workbench-stage[data-state="complete"] {
  1750	  border-color: rgba(145, 255, 230, 0.28);
  1751	  background: rgba(24, 153, 132, 0.12);
  1752	}
  1753	
  1754	.workbench-stage[data-state="complete"] .workbench-stage-step {
  1755	  background: rgba(145, 255, 230, 0.2);
  1756	  color: #a3ffd6;
  1757	}
  1758	
  1759	.workbench-stage[data-state="blocked"] {
  1760	  border-color: rgba(255, 176, 55, 0.28);
  1761	  background: rgba(255, 176, 55, 0.12);
  1762	}
  1763	
  1764	.workbench-stage[data-state="blocked"] .workbench-stage-step {
  1765	  background: rgba(255, 176, 55, 0.2);
  1766	  color: #ffe198;
  1767	}
  1768	
  1769	.workbench-stage[data-state="pending"] {
  1770	  border-color: rgba(79, 184, 255, 0.22);
  1771	  background: rgba(61, 126, 255, 0.1);
  1772	}
  1773	
  1774	.workbench-stage[data-state="pending"] .workbench-stage-step {
  1775	  background: rgba(79, 184, 255, 0.2);
  1776	  color: #9de7ff;
  1777	}
  1778	
  1779	#bundle-ready-state[data-state="ready"] {
  1780	  color: #9affc5;
  1781	}
  1782	
  1783	#bundle-ready-state[data-state="blocked"] {
  1784	  color: #ffd788;
  1785	}
  1786	
  1787	.workbench-output-grid {
  1788	  display: grid;
  1789	  grid-template-columns: repeat(2, minmax(0, 1fr));
  1790	  gap: 0.85rem;
  1791	  margin-bottom: 0.85rem;
  1792	}
  1793	
  1794	.workbench-output-card h3 {
  1795	  margin-top: 0;
  1796	}
  1797	
  1798	.workbench-bullet-list {
  1799	  margin: 0;
  1800	  padding-left: 1.2rem;
  1801	  color: rgba(240, 247, 255, 0.92);
  1802	}
  1803	
  1804	.workbench-data-list {
  1805	  margin: 0;
  1806	  display: grid;
  1807	  gap: 0.75rem;
  1808	}
  1809	
  1810	.workbench-data-list div {
  1811	  display: grid;
  1812	  gap: 0.2rem;
  1813	}
  1814	
  1815	.workbench-data-list dt {
  1816	  font-weight: 700;
  1817	  color: rgba(213, 228, 240, 0.72);
  1818	}
  1819	
  1820	.workbench-data-list dd {
  1821	  margin: 0;
  1822	  color: #f7fcff;
  1823	  white-space: pre-wrap;
  1824	  word-break: break-word;
  1825	}
  1826	
  1827	.workbench-archive-card {
  1828	  margin-bottom: 0.85rem;
  1829	}
  1830	
  1831	.workbench-json-output {
  1832	  margin: 0;
  1833	  padding: 1rem;
  1834	  border-radius: 16px;
  1835	  background: rgba(4, 10, 18, 0.92);
  1836	  color: #aef8ea;
  1837	  overflow: auto;
  1838	  max-height: 28rem;
  1839	}
  1840	
  1841	@media (max-width: 1100px) {
  1842	  .workbench-layout,
  1843	  .workbench-output-grid,
  1844	  .workbench-form-grid,
  1845	  .workbench-form-grid-wide,
  1846	  .workbench-summary-grid,
  1847	  .workbench-onboarding-grid,
  1848	  .workbench-onboarding-footer,
  1849	  .workbench-fingerprint-meta,
  1850	  .workbench-fingerprint-panels,
  1851	  .workbench-actions-grid,
  1852	  .workbench-history-compare-grid,
  1853	  .workbench-history-detail-grid,
  1854	  .workbench-spotlight-grid,
  1855	  .workbench-stage-strip,
  1856	  .workbench-history-grid {
  1857	    grid-template-columns: minmax(0, 1fr);
  1858	  }
  1859	
  1860	  .workbench-nav-panel,
  1861	  .workbench-acceptance-panel,
  1862	  .workbench-section-heading,
  1863	  .workbench-archive-restore-row,
  1864	  .workbench-action-row,
  1865	  .workbench-handoff-actions,
  1866	  .workbench-visual-header,
  1867	  .workbench-recent-archives-header-actions,
  1868	  .workbench-history-view-bar,
  1869	  .workbench-packet-draft-bar {
  1870	    flex-direction: column;
  1871	    align-items: flex-start;
  1872	  }
  1873	
  1874	  .workbench-section-note {
  1875	    text-align: left;
  1876	  }
  1877	
  1878	  .workbench-history-note {
  1879	    text-align: left;
  1880	  }
  1881	
  1882	  .workbench-history-detail-row {
  1883	    flex-direction: column;
  1884	    align-items: flex-start;
  1885	  }
  1886	
  1887	  .workbench-fingerprint-item-header {
  1888	    flex-direction: column;
  1889	  }
  1890	
  1891	  .workbench-fingerprint-chip-row {
  1892	    justify-content: flex-start;
  1893	  }
  1894	
  1895	  .workbench-actions-panel-header,
  1896	  .workbench-actions-item-header,
  1897	  .workbench-schema-card-header,
  1898	  .workbench-schema-workspace-footer,
  1899	  .workbench-clarification-card-header,
  1900	  .workbench-clarification-workspace-footer {
  1901	    flex-direction: column;
  1902	  }
  1903	
  1904	  .workbench-history-detail-value {
  1905	    text-align: left;
  1906	  }
  1907	}
  1908	
  1909	/* ── Beginner / Expert View Toggle ── */
  1910	.view-mode-btn {
  1911	  transition: background 0.2s, border-color 0.2s, color 0.2s;
  1912	  font-family: inherit;
  1913	}
  1914	
  1915	.view-mode-btn.is-active {
  1916	  background: rgba(40,244,255,0.15) !important;
  1917	  border-color: rgba(40,244,255,0.5) !important;
  1918	  color: #28f4ff !important;
  1919	}
  1920	
  1921	.view-mode-btn:hover:not(.is-active) {
  1922	  border-color: rgba(79,184,255,0.5) !important;
  1923	  color: #c8e8ff !important;
  1924	}
  1925	
  1926	/* Expert-only sections hidden in beginner mode */
  1927	[view="beginner"] {
  1928	  transition: opacity 0.3s, max-height 0.35s ease;
  1929	  overflow: hidden;
  1930	}
  1931	
  1932	/* In beginner mode, collapse expert sections */
  1933	body[data-view="beginner"] [view="beginner"] {
  1934	  display: none;
  1935	}
  1936	
  1937	/* Expert mode shows everything */
  1938	body[data-view="expert"] [view="beginner"] {
  1939	  display: block;
  1940	}
  1941	
  1942	/* Explain runtime observation board — operator-facing runtime status only,
  1943	   does not introduce new control truth. Reuses .workbench-visual-board +
  1944	   .workbench-summary-card idioms with a subtle cyan accent so operators can
  1945	   distinguish it from the primary verdict/acceptance board. */
  1946	.workbench-explain-runtime-board {
  1947	  margin-top: 1rem;
  1948	  border-color: rgba(79, 184, 255, 0.22);
  1949	  background:
  1950	    linear-gradient(135deg, rgba(12, 24, 40, 0.96), rgba(6, 14, 24, 0.94)),
  1951	    radial-gradient(circle at 88% 18%, rgba(79, 184, 255, 0.12), transparent 18rem);
  1952	}
  1953	
  1954	.workbench-explain-runtime-board .workbench-visual-badge[data-state="live"] {
  1955	  color: #d6efff;
  1956	  border-color: rgba(79, 184, 255, 0.3);
  1957	  background: rgba(61, 126, 255, 0.14);
  1958	}

exec
/bin/zsh -lc 'nl -ba .planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc 'nl -ba src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	const workbenchBootstrapPath = "/api/workbench/bootstrap";
     2	const workbenchBundlePath = "/api/workbench/bundle";
     3	const workbenchRepairPath = "/api/workbench/repair";
     4	const workbenchArchiveRestorePath = "/api/workbench/archive-restore";
     5	const workbenchRecentArchivesPath = "/api/workbench/recent-archives";
     6	const workbenchPacketWorkspaceStorageKey = "well-harness-workbench-packet-workspace-v1";
     7	const draftDesignStateKey = "draft_design_state";
     8	const workbenchPersistedFieldIds = [
     9	  "workbench-scenario-id",
    10	  "workbench-fault-mode-id",
    11	  "workbench-sample-period",
    12	  "workbench-archive-toggle",
    13	  "workbench-archive-manifest-path",
    14	  "workbench-handoff-note",
    15	  "workbench-observed-symptoms",
    16	  "workbench-evidence-links",
    17	  "workbench-root-cause",
    18	  "workbench-repair-action",
    19	  "workbench-validation-after-fix",
    20	  "workbench-residual-risk",
    21	  "workbench-logic-change",
    22	  "workbench-reliability-gain",
    23	  "workbench-guardrail-note",
    24	];
    25	
    26	const defaultReferenceResolution = {
    27	  rootCause: "Pressure sensor bias was confirmed during troubleshooting.",
    28	  repairAction: "Recalibrated the sensor path.",
    29	  validationAfterFix: "Acceptance replay completed after the repair.",
    30	  residualRisk: "Watch for future sensor drift.",
    31	  logicChange: "Add a pressure plausibility cross-check before enabling the deploy chain.",
    32	  reliabilityGain: "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
    33	  guardrailNote: "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
    34	};
    35	
    36	let bootstrapPayload = null;
    37	let latestWorkbenchRequestId = 0;
    38	let currentWorkbenchRunLabel = "手动生成";
    39	let workbenchRecentArchives = [];
    40	let workbenchRunHistory = [];
    41	let selectedWorkbenchHistoryId = "";
    42	let workbenchHistorySequence = 0;
    43	let currentWorkbenchViewMode = "empty";
    44	let workbenchPacketRevisionHistory = [];
    45	let selectedWorkbenchPacketRevisionId = "";
    46	let workbenchPacketRevisionSequence = 0;
    47	let suspendWorkbenchPacketWorkspacePersistence = false;
    48	const maxWorkbenchRunHistory = 6;
    49	const maxWorkbenchPacketRevisionHistory = 8;
    50	
    51	function bootWorkbenchColumnSafely(columnName, bootFn) {
    52	  try {
    53	    bootFn();
    54	  } catch (error) {
    55	    const status = workbenchElement(`workbench-${columnName}-status`);
    56	    if (status) {
    57	      status.textContent = `${columnName} panel failed independently: ${error.message || error}`;
    58	      status.dataset.tone = "warning";
    59	    }
    60	  }
    61	}
    62	
    63	function bootWorkbenchControlPanel() {
    64	  const status = workbenchElement("workbench-control-status");
    65	  if (status) {
    66	    status.textContent = "Control panel ready. Scenario actions are staged for E07+.";
    67	    status.dataset.tone = "ready";
    68	  }
    69	}
    70	
    71	function bootWorkbenchDocumentPanel() {
    72	  const status = workbenchElement("workbench-document-status");
    73	  if (status) {
    74	    status.textContent = "Document panel ready. Text-range annotation arrives in E07.";
    75	    status.dataset.tone = "ready";
    76	  }
    77	}
    78	
    79	function bootWorkbenchCircuitPanel() {
    80	  const status = workbenchElement("workbench-circuit-status");
    81	  if (status) {
    82	    status.textContent = "Circuit panel ready. Overlay annotation arrives in E07.";
    83	    status.dataset.tone = "ready";
    84	  }
    85	}
    86	
    87	function bootWorkbenchShell() {
    88	  bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
    89	  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
    90	  bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
    91	}
    92	
    93	// P43 authority contract — written only via assignFrozenSpec; never mutated directly
    94	let frozenSpec = null;
    95	
    96	// P43 workflow state machine (P43-03)
    97	let workflowState = "INIT";
    98	
    99	const _workflowTransitions = {
   100	  INIT:        { confirm_freeze: "FROZEN",      load_packet: "INIT" },
   101	  FROZEN:      { start_gen: "GENERATING",       confirm_freeze: "FROZEN",   reiterate: "INIT" },
   102	  GENERATING:  { gen_complete: "PANEL_READY",   gen_fail: "ERROR",          reiterate: "INIT" },
   103	  PANEL_READY: { final_approve: "APPROVING",    start_gen: "GENERATING",    reiterate: "INIT" },
   104	  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
   105	  APPROVED:    { archive: "ARCHIVING" },
   106	  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
   107	  ARCHIVED:    {},
   108	  ERROR:       { reiterate: "INIT" },
   109	};
   110	
   111	function dispatchWorkflowEvent(event) {
   112	  const next = (_workflowTransitions[workflowState] || {})[event];
   113	  if (next === undefined) {
   114	    return false;
   115	  }
   116	  workflowState = next;
   117	  updateWorkflowUI();
   118	  return true;
   119	}
   120	
   121	function updateWorkflowUI() {
   122	  const approveBtn  = workbenchElement("workbench-final-approve");
   123	  const startGenBtn = workbenchElement("workbench-start-gen");
   124	  const badge       = workbenchElement("workbench-workflow-state");
   125	
   126	  // "冻结审批 Spec" enabled when spec is not yet frozen or after generation
   127	  const approveEnabled = ["INIT", "PANEL_READY", "ANNOTATING", "WIRING"].includes(workflowState);
   128	  // "生成 (Frozen Spec)" enabled only when a frozen spec exists
   129	  const startGenEnabled = workflowState === "FROZEN";
   130	
   131	  if (approveBtn)  approveBtn.disabled  = !approveEnabled;
   132	  if (startGenBtn) startGenBtn.disabled = !startGenEnabled;
   133	  if (badge) {
   134	    badge.textContent    = workflowState;
   135	    badge.dataset.state  = workflowState.toLowerCase();
   136	  }
   137	}
   138	
   139	const workbenchPresets = {
   140	  ready_archived: {
   141	    label: "一键通过验收",
   142	    archiveBundle: true,
   143	    source: "reference",
   144	    sourceStatus: "当前样例：参考样例。系统会直接跑完整 happy path 并生成 archive。",
   145	    preparationMessage: "参考样例已就位，系统马上开始生成 ready bundle 并留档。",
   146	  },
   147	  blocked_follow_up: {
   148	    label: "一键看阻塞态",
   149	    archiveBundle: false,
   150	    source: "template",
   151	    sourceStatus: "当前样例：空白模板。系统会故意演示 clarification gate 如何把不完整 packet 拦下来。",
   152	    preparationMessage: "空白模板已就位，系统马上演示阻塞态。",
   153	  },
   154	  ready_preview: {
   155	    label: "一键快速预览",
   156	    archiveBundle: false,
   157	    source: "reference",
   158	    sourceStatus: "当前样例：参考样例。系统会直接跑 ready bundle，但不生成 archive。",
   159	    preparationMessage: "参考样例已就位，系统马上生成 ready bundle 供快速查看。",
   160	  },
   161	  archive_retry: {
   162	    label: "一键留档复跑",
   163	    archiveBundle: true,
   164	    source: "reference",
   165	    sourceStatus: "当前样例：参考样例。这个预设适合连续复跑，archive 会自动避开重名目录。",
   166	    preparationMessage: "参考样例已就位，系统马上做一次带 archive 的复跑。",
   167	  },
   168	};
   169	
   170	function workbenchElement(id) {
   171	  return document.getElementById(id);
   172	}
   173	
   174	function beginWorkbenchRequest() {
   175	  latestWorkbenchRequestId += 1;
   176	  return latestWorkbenchRequestId;
   177	}
   178	
   179	function isLatestWorkbenchRequest(requestId) {
   180	  return requestId === latestWorkbenchRequestId;
   181	}
   182	
   183	function setRequestStatus(message, tone = "neutral") {
   184	  const element = workbenchElement("workbench-request-status");
   185	  element.textContent = message;
   186	  element.dataset.tone = tone;
   187	}
   188	
   189	function setPacketSourceStatus(message) {
   190	  workbenchElement("workbench-packet-source-status").textContent = message;
   191	  persistWorkbenchPacketWorkspace();
   192	}
   193	
   194	function setResultMode(message) {
   195	  workbenchElement("workbench-result-mode").textContent = message;
   196	}
   197	
   198	function prettyJson(value) {
   199	  return JSON.stringify(value, null, 2);
   200	}
   201	
   202	function shortPath(path) {
   203	  if (!path) {
   204	    return "(none)";
   205	  }
   206	  const parts = String(path).split("/");
   207	  return parts[parts.length - 1] || String(path);
   208	}
   209	
   210	function cloneJson(value) {
   211	  return JSON.parse(JSON.stringify(value));
   212	}
   213	
   214	function normalizeRecentWorkbenchArchiveEntries(entries) {
   215	  if (!Array.isArray(entries)) {
   216	    return [];
   217	  }
   218	  return entries
   219	    .filter((entry) => entry && typeof entry === "object")
   220	    .map((entry) => ({
   221	      archive_dir: typeof entry.archive_dir === "string" ? entry.archive_dir : "",
   222	      manifest_path: typeof entry.manifest_path === "string" ? entry.manifest_path : "",
   223	      created_at_utc: typeof entry.created_at_utc === "string" ? entry.created_at_utc : "",
   224	      system_id: typeof entry.system_id === "string" ? entry.system_id : "unknown_system",
   225	      system_title: typeof entry.system_title === "string" ? entry.system_title : "",
   226	      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
   227	      ready_for_spec_build: Boolean(entry.ready_for_spec_build),
   228	      selected_scenario_id: typeof entry.selected_scenario_id === "string" ? entry.selected_scenario_id : "",
   229	      selected_fault_mode_id: typeof entry.selected_fault_mode_id === "string" ? entry.selected_fault_mode_id : "",
   230	      has_workspace_handoff: Boolean(entry.has_workspace_handoff),
   231	      has_workspace_snapshot: Boolean(entry.has_workspace_snapshot),
   232	    }))
   233	    .filter((entry) => entry.manifest_path || entry.archive_dir);
   234	}
   235	
   236	function summarizeRecentWorkbenchArchive(entry) {
   237	  const state = entry.ready_for_spec_build ? "ready" : "blocked";
   238	  const scenario = entry.selected_scenario_id || "未选 scenario";
   239	  const faultMode = entry.selected_fault_mode_id || "未选 fault mode";
   240	  const workspace = entry.has_workspace_snapshot
   241	    ? "带工作区快照"
   242	    : (entry.has_workspace_handoff ? "仅带交接摘要" : "仅带 bundle");
   243	  return {
   244	    badge: state === "ready" ? "可恢复 / ready" : "可恢复 / blocked",
   245	    summary: `${scenario} / ${faultMode}`,
   246	    detail: `${workspace} / ${shortPath(entry.archive_dir || entry.manifest_path)}`,
   247	  };
   248	}
   249	
   250	function buildRecentWorkbenchArchiveEntryFromBundlePayload(payload) {
   251	  const archive = payload && payload.archive ? payload.archive : null;
   252	  const bundle = payload && payload.bundle ? payload.bundle : {};
   253	  if (!archive) {
   254	    return null;
   255	  }
   256	  return {
   257	    archive_dir: archive.archive_dir || "",
   258	    manifest_path: archive.manifest_json_path || "",
   259	    created_at_utc: archive.created_at_utc || "",
   260	    system_id: bundle.system_id || "unknown_system",
   261	    system_title: bundle.system_title || "",
   262	    bundle_kind: bundle.bundle_kind || "",
   263	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   264	    selected_scenario_id: bundle.selected_scenario_id || "",
   265	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   266	    has_workspace_handoff: Boolean(archive.workspace_handoff_json_path),
   267	    has_workspace_snapshot: Boolean(archive.workspace_snapshot_json_path),
   268	  };
   269	}
   270	
   271	function buildRecentWorkbenchArchiveEntryFromRestorePayload(payload) {
   272	  const bundle = payload && payload.bundle ? payload.bundle : {};
   273	  const manifest = payload && payload.manifest ? payload.manifest : {};
   274	  const files = manifest && typeof manifest.files === "object" ? manifest.files : {};
   275	  return {
   276	    archive_dir: payload.archive_dir || "",
   277	    manifest_path: payload.manifest_path || "",
   278	    created_at_utc: typeof manifest.created_at_utc === "string" ? manifest.created_at_utc : "",
   279	    system_id: bundle.system_id || "unknown_system",
   280	    system_title: bundle.system_title || "",
   281	    bundle_kind: bundle.bundle_kind || "",
   282	    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
   283	    selected_scenario_id: bundle.selected_scenario_id || "",
   284	    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
   285	    has_workspace_handoff: Boolean(files.workspace_handoff_json),
   286	    has_workspace_snapshot: Boolean(files.workspace_snapshot_json),
   287	  };
   288	}
   289	
   290	function upsertRecentWorkbenchArchiveEntry(entry) {
   291	  if (!entry || (!entry.manifest_path && !entry.archive_dir)) {
   292	    return;
   293	  }
   294	  const dedupeKey = entry.manifest_path || entry.archive_dir;
   295	  workbenchRecentArchives = [
   296	    entry,
   297	    ...workbenchRecentArchives.filter((item) => (item.manifest_path || item.archive_dir) !== dedupeKey),
   298	  ].slice(0, 6);
   299	  renderRecentWorkbenchArchives();
   300	}
   301	
   302	function renderRecentWorkbenchArchives() {
   303	  const container = workbenchElement("workbench-recent-archives-list");
   304	  const summaryElement = workbenchElement("workbench-recent-archives-summary");
   305	  if (!workbenchRecentArchives.length) {
   306	    summaryElement.textContent = "这里会列出最近成功生成的 archive；你可以直接点“恢复这个 Archive”，不用再自己查本地路径。";
   307	    container.replaceChildren((() => {
   308	      const card = document.createElement("article");
   309	      card.className = "workbench-history-card is-empty";
   310	      const title = document.createElement("strong");
   311	      title.textContent = "暂无最近 Archive";
   312	      const detail = document.createElement("p");
   313	      detail.textContent = "等你先生成一份 archive，或把已有 archive 放到默认目录后，这里就会出现可恢复列表。";
   314	      card.append(title, detail);
   315	      return card;
   316	    })());
   317	    return;
   318	  }
   319	
   320	  summaryElement.textContent = "这些 archive 都来自默认 archive root；点卡片就会自动把它恢复回当前 workbench。";
   321	  container.replaceChildren(...workbenchRecentArchives.map((entry) => {
   322	    const card = document.createElement("article");
   323	    card.className = "workbench-history-card";
   324	
   325	    const meta = document.createElement("div");
   326	    meta.className = "workbench-history-meta";
   327	
   328	    const systemChip = document.createElement("span");
   329	    systemChip.className = "workbench-history-chip";
   330	    systemChip.textContent = entry.system_id || "unknown_system";
   331	
   332	    const stateChip = document.createElement("span");
   333	    stateChip.className = "workbench-history-chip";
   334	    stateChip.dataset.state = entry.ready_for_spec_build ? "ready" : "blocked";
   335	    stateChip.textContent = entry.ready_for_spec_build ? "ready" : "blocked";
   336	
   337	    const workspaceChip = document.createElement("span");
   338	    workspaceChip.className = "workbench-history-chip";
   339	    workspaceChip.textContent = entry.has_workspace_snapshot
   340	      ? "workspace"
   341	      : (entry.has_workspace_handoff ? "handoff" : "bundle");
   342	
   343	    meta.append(systemChip, stateChip, workspaceChip);
   344	
   345	    const title = document.createElement("strong");
   346	    title.textContent = entry.system_title
   347	      ? `${entry.system_id} - ${entry.system_title}`
   348	      : entry.system_id;
   349	
   350	    const summary = summarizeRecentWorkbenchArchive(entry);
   351	    const summaryText = document.createElement("p");
   352	    summaryText.textContent = `${summary.badge} / ${summary.summary}`;
   353	
   354	    const detail = document.createElement("p");
   355	    detail.textContent = `${summary.detail} / ${entry.created_at_utc || "时间未知"}`;
   356	
   357	    const action = document.createElement("button");
   358	    action.type = "button";
   359	    action.className = "workbench-history-return-button workbench-recent-archive-action";
   360	    action.textContent = "恢复这个 Archive";
   361	    action.addEventListener("click", () => {
   362	      workbenchElement("workbench-archive-manifest-path").value = entry.archive_dir || entry.manifest_path;
   363	      void restoreWorkbenchArchiveFromManifest();
   364	    });
   365	
   366	    card.append(meta, title, summaryText, detail, action);
   367	    return card;
   368	  }));
   369	}
   370	
   371	async function refreshRecentWorkbenchArchives() {
   372	  setRequestStatus("正在刷新最近 archive 列表...", "neutral");
   373	  try {
   374	    const response = await fetch(workbenchRecentArchivesPath, {method: "GET"});
   375	    const payload = await response.json();
   376	    if (!response.ok) {
   377	      throw new Error(payload.error || "recent archives request failed");
   378	    }
   379	    workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
   380	    renderRecentWorkbenchArchives();
   381	    if (payload.default_archive_root) {
   382	      workbenchElement("default-archive-root").textContent = payload.default_archive_root;
   383	    }
   384	    setRequestStatus("最近 archive 列表已刷新。", "success");
   385	  } catch (error) {
   386	    setRequestStatus(`刷新最近 archive 列表失败：${String(error.message || error)}`, "error");
   387	  }
   388	}
   389	
   390	// ─── P43 authority helpers ────────────────────────────────────────────────────
   391	
   392	function deepFreeze(obj) {
   393	  if (obj === null || typeof obj !== "object") {
   394	    return obj;
   395	  }
   396	  Object.getOwnPropertyNames(obj).forEach((name) => {
   397	    deepFreeze(obj[name]);
   398	  });
   399	  return Object.freeze(obj);
   400	}
   401	
   402	function assignFrozenSpec(spec, origin) {  // origin: "freeze-event" | "archive-restore"
   403	  frozenSpec = deepFreeze(JSON.parse(JSON.stringify(spec)));
   404	}
   405	
   406	async function handleStartGen() {
   407	  if (frozenSpec === null) {
   408	    setRequestStatus("未找到已冻结规格 — 请先审批 Spec 再生成。", "error");
   409	    return;
   410	  }
   411	  // Write frozenSpec into the packet editor so runWorkbenchBundle() submits
   412	  // the frozen content, never a post-approval draft edit (R4 authority boundary)
   413	  const packetEl = workbenchElement("workbench-packet-json");
   414	  if (packetEl) {
   415	    packetEl.value = prettyJson(frozenSpec);
   416	    renderWorkbenchPacketDraftState();
   417	  }
   418	  if (!dispatchWorkflowEvent("start_gen")) {
   419	    setRequestStatus("当前工作流状态不允许启动生成。", "error");
   420	    return;
   421	  }
   422	  setCurrentWorkbenchRunLabel("Frozen Spec 生成");
   423	  const genOk = await runWorkbenchBundle();
   424	  dispatchWorkflowEvent(genOk ? "gen_complete" : "gen_fail");
   425	}
   426	
   427	function validateDraftAgainstFrozen(draft, frozen) {
   428	  if (frozen === null) {
   429	    return { valid: true, deviations: [] };
   430	  }
   431	  if (draft === null || typeof draft !== "object" || typeof frozen !== "object") {
   432	    return { valid: false, deviations: [{ field: "(root)", reason: "draft or frozen is not an object" }] };
   433	  }
   434	  const deviations = [];
   435	  for (const key of Object.keys(frozen)) {
   436	    if (JSON.stringify(frozen[key]) !== JSON.stringify(draft[key])) {
   437	      deviations.push({ field: key, frozen: frozen[key], draft: draft[key] });
   438	    }
   439	  }
   440	  return { valid: deviations.length === 0, deviations };
   441	}
   442	
   443	function handleFinalApprove() {
   444	  const packetEl = workbenchElement("workbench-packet-json");
   445	  const raw = packetEl ? packetEl.value : "";
   446	  let currentSpec;
   447	  try {
   448	    currentSpec = JSON.parse(raw || "{}");
   449	  } catch (error) {
   450	    setRequestStatus(`审批失败：Packet JSON 解析错误 — ${String(error.message || error)}`, "error");
   451	    return;
   452	  }
   453	
   454	  // Freeze the approved spec (R3 — only authorised write path)
   455	  assignFrozenSpec(currentSpec, "freeze-event");
   456	
   457	  // Delete draft immediately after freezing (R6)
   458	  clearDraftDesignState();
   459	
   460	  // Dispatch correct state machine event based on current state:
   461	  // PANEL_READY/ANNOTATING → final_approve → APPROVING → approve_ok → APPROVED
   462	  // INIT/FROZEN → confirm_freeze → FROZEN
   463	  if (workflowState === "PANEL_READY" || workflowState === "ANNOTATING") {
   464	    dispatchWorkflowEvent("final_approve");
   465	    dispatchWorkflowEvent("approve_ok");
   466	  } else {
   467	    dispatchWorkflowEvent("confirm_freeze");
   468	  }
   469	
   470	  setRequestStatus("Spec 已冻结。草稿已清除。可执行生成。", "success");
   471	}
   472	
   473	// ─────────────────────────────────────────────────────────────────────────────
   474	
   475	function workbenchBrowserStorage() {
   476	  try {
   477	    return window.localStorage;
   478	  } catch (error) {
   479	    return null;
   480	  }
   481	}
   482	
   483	function withWorkbenchPacketWorkspacePersistenceSuspended(callback) {
   484	  const previous = suspendWorkbenchPacketWorkspacePersistence;
   485	  suspendWorkbenchPacketWorkspacePersistence = true;
   486	  try {
   487	    return callback();
   488	  } finally {
   489	    suspendWorkbenchPacketWorkspacePersistence = previous;
   490	  }
   491	}
   492	
   493	function readWorkbenchPersistedFieldValue(id) {
   494	  const field = workbenchElement(id);
   495	  if (!field) {
   496	    return null;
   497	  }
   498	  if (field.type === "checkbox") {
   499	    return Boolean(field.checked);
   500	  }
   501	  return field.value;
   502	}
   503	
   504	function applyWorkbenchPersistedFieldValue(id, value) {
   505	  const field = workbenchElement(id);
   506	  if (!field || value === undefined || value === null) {
   507	    return;
   508	  }
   509	  if (field.type === "checkbox") {
   510	    field.checked = Boolean(value);
   511	    return;
   512	  }
   513	  field.value = String(value);
   514	}
   515	
   516	function nextWorkbenchSequenceFromIds(entries, prefix) {
   517	  if (!Array.isArray(entries) || !entries.length) {
   518	    return 0;
   519	  }
   520	  return entries.reduce((maxValue, entry) => {
   521	    if (!entry || typeof entry.id !== "string" || !entry.id.startsWith(prefix)) {
   522	      return maxValue;
   523	    }
   524	    const sequence = Number(entry.id.slice(prefix.length));
   525	    if (!Number.isFinite(sequence)) {
   526	      return maxValue;
   527	    }
   528	    return Math.max(maxValue, sequence);
   529	  }, 0);
   530	}
   531	
   532	function activeWorkbenchPacketPayload() {
   533	  const parsed = parseWorkbenchPacketEditor();
   534	  if (parsed.payload) {
   535	    return parsed.payload;
   536	  }
   537	  const selectedEntry = selectedWorkbenchPacketRevisionEntry();
   538	  return selectedEntry ? selectedEntry.payload : null;
   539	}
   540	
   541	function activeWorkbenchHistoryEntry() {
   542	  if (!workbenchRunHistory.length) {
   543	    return null;
   544	  }
   545	  if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
   546	    return workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || latestWorkbenchHistoryEntry();
   547	  }
   548	  return latestWorkbenchHistoryEntry();
   549	}
   550	
   551	function buildWorkbenchHandoffSnapshot() {
   552	  const packetPayload = activeWorkbenchPacketPayload();
   553	  const packetEntry = selectedWorkbenchPacketRevisionEntry();
   554	  const packetSummary = packetPayload ? summarizePacketPayload(packetPayload) : null;
   555	  const resultEntry = activeWorkbenchHistoryEntry();
   556	  const resultSnapshot = detailedWorkbenchHistoryEntry(resultEntry);
   557	  const archive = resultEntry && resultEntry.payload ? resultEntry.payload.archive || null : null;
   558	  const note = String(readWorkbenchPersistedFieldValue("workbench-handoff-note") || "").trim();
   559	
   560	  let badgeState = "idle";
   561	  let badgeText = "等待载入";
   562	  let summary = "先载入 packet；系统才有可交接的当前状态。";
   563	
   564	  if (currentWorkbenchViewMode === "running") {
   565	    badgeState = "idle";
   566	    badgeText = "正在整理";
   567	    summary = note
   568	      ? "当前工作区正在生成新结果；你的交接备注会和最终状态一起留在导出快照里。"
   569	      : "当前工作区正在生成新结果；如果准备跨浏览器或交给别人，等结果出来后再补一段交接备注会更稳。";
   570	  } else if (resultEntry && resultEntry.archived) {
   571	    badgeState = "archived";
   572	    badgeText = "可交接";
   573	    summary = note
   574	      ? "当前工作区已经带交接备注，且结果已归档；导出快照后，接手人可以直接从这份状态继续。"
   575	      : "当前工作区已经具备可交接的 packet、结果和 archive 状态；如果要正式交接，建议再补一段备注。";
   576	  } else if (resultEntry && resultEntry.state === "ready") {
   577	    badgeState = "ready";
   578	    badgeText = "可交接";
   579	    summary = note
   580	      ? "当前工作区已经带交接备注；虽然这次没归档也可以继续交接，但备注里最好说明下一步要不要补 archive。"
   581	      : "当前工作区已经有 ready 结果；如果准备交给下一位，建议补一段备注说明是否还要 archive。";
   582	  } else if (resultEntry) {
   583	    badgeState = "blocked";
   584	    badgeText = resultEntry.state === "failure" ? "先修正" : "待补齐";
   585	    summary = note
   586	      ? "当前工作区已经带交接备注；接手人打开快照后会先看到现在卡在哪、为什么卡住。"
   587	      : "当前工作区已经明确告诉你卡在哪，但如果要跨浏览器或跨人交接，最好再补一段备注说明下一步。";
   588	  } else if (packetPayload) {
   589	    badgeState = "idle";
   590	    badgeText = "待运行";
   591	    summary = note
   592	      ? "当前只有 packet 和交接备注，还没有结果历史；接手人需要从这个输入基线继续跑 bundle。"
   593	      : "当前 packet 已就位，但还没有结果；如果你准备交接给下一位，建议先写备注说明为什么停在这里。";
   594	  }
   595	
   596	  return {
   597	    note,
   598	    badgeState,
   599	    badgeText,
   600	    summary,
   601	    system: packetPayload ? (packetPayload.system_id || "unknown_system") : "等待载入",
   602	    systemDetail: packetEntry
   603	      ? `${packetEntry.title} / ${packetEntry.timeLabel}`
   604	      : "当前输入区还没有已识别 packet 版本。",
   605	    packet: packetSummary
   606	      ? `${packetSummary.sourceDocuments} docs / ${packetSummary.logicNodes} logic / ${packetSummary.faultModes} faults`
   607	      : "等待载入",
   608	    packetDetail: packetSummary
   609	      ? `${packetSummary.components} components / ${packetSummary.scenarios} scenarios / ${packetSummary.clarificationAnswers} answers`
   610	      : "先载入 packet 后，这里会显示覆盖规模。",
   611	    result: currentWorkbenchViewMode === "running"
   612	      ? "正在生成"
   613	      : resultSnapshot
   614	        ? `${resultSnapshot.verdict} / ${resultSnapshot.scenario}`
   615	        : "等待第一次结果",
   616	    resultDetail: currentWorkbenchViewMode === "running"
   617	      ? "系统正在生成新结果；完成后这里会自动刷新。"
   618	      : resultSnapshot
   619	        ? resultSnapshot.blocker
   620	        : "还没有 bundle 结果。",
   621	    archive: archive ? "已留档" : (currentWorkbenchViewMode === "running" ? "处理中" : "未生成"),
   622	    archiveDetail: archive
   623	      ? shortPath(archive.archive_dir)
   624	      : resultSnapshot
   625	        ? resultSnapshot.archive
   626	        : "还没有 archive package。",
   627	    workspace: `${workbenchPacketRevisionHistory.length} 个 packet 版本 / ${workbenchRunHistory.length} 个结果`,
   628	    workspaceDetail:
   629	      currentWorkbenchViewMode === "history" && resultEntry
   630	        ? `当前在历史回看模式：${resultEntry.title} / ${resultEntry.timeLabel}`
   631	        : currentWorkbenchViewMode === "latest" && resultEntry
   632	          ? `当前主看板展示最新结果：${resultEntry.title} / ${resultEntry.timeLabel}`
   633	          : currentWorkbenchViewMode === "running"
   634	            ? "当前主看板正在生成新结果。"
   635	            : packetEntry
   636	              ? `当前 packet 基线：${packetEntry.title} / ${packetEntry.timeLabel}`
   637	              : "等待第一次 packet 载入。",
   638	  };
   639	}
   640	
   641	function renderWorkbenchHandoffBoard() {
   642	  const snapshot = buildWorkbenchHandoffSnapshot();
   643	  const badge = workbenchElement("workbench-handoff-badge");
   644	  badge.dataset.state = snapshot.badgeState;
   645	  badge.textContent = snapshot.badgeText;
   646	  renderValue("workbench-handoff-summary", snapshot.summary);
   647	  renderValue("workbench-handoff-system", snapshot.system);
   648	  renderValue("workbench-handoff-system-detail", snapshot.systemDetail);
   649	  renderValue("workbench-handoff-packet", snapshot.packet);
   650	  renderValue("workbench-handoff-packet-detail", snapshot.packetDetail);
   651	  renderValue("workbench-handoff-result", snapshot.result);
   652	  renderValue("workbench-handoff-result-detail", snapshot.resultDetail);
   653	  renderValue("workbench-handoff-archive", snapshot.archive);
   654	  renderValue("workbench-handoff-archive-detail", snapshot.archiveDetail);
   655	  renderValue("workbench-handoff-workspace", snapshot.workspace);
   656	  renderValue("workbench-handoff-workspace-detail", snapshot.workspaceDetail);
   657	}
   658	
   659	function workbenchHandoffBriefText() {
   660	  const snapshot = buildWorkbenchHandoffSnapshot();
   661	  const lines = [
   662	    "工作区交接摘要",
   663	    `- 状态：${snapshot.badgeText}`,
   664	    `- 系统：${snapshot.system}`,
   665	    `- 系统细节：${snapshot.systemDetail}`,
   666	    `- Packet 覆盖：${snapshot.packet}`,
   667	    `- Packet 细节：${snapshot.packetDetail}`,
   668	    `- 当前结果：${snapshot.result}`,
   669	    `- 结果细节：${snapshot.resultDetail}`,
   670	    `- Archive 状态：${snapshot.archive}`,
   671	    `- Archive 细节：${snapshot.archiveDetail}`,
   672	    `- 工作区规模：${snapshot.workspace}`,
   673	    `- 工作区细节：${snapshot.workspaceDetail}`,
   674	  ];
   675	  if (snapshot.note) {
   676	    lines.push(`- 交接备注：${snapshot.note}`);
   677	  }
   678	  return lines.join("\n");
   679	}
   680	
   681	async function copyWorkbenchHandoffBrief() {
   682	  const text = workbenchHandoffBriefText();
   683	  try {
   684	    if (navigator.clipboard && navigator.clipboard.writeText) {
   685	      await navigator.clipboard.writeText(text);
   686	    } else {
   687	      const textarea = document.createElement("textarea");
   688	      textarea.value = text;
   689	      textarea.setAttribute("readonly", "true");
   690	      textarea.style.position = "absolute";
   691	      textarea.style.left = "-9999px";
   692	      document.body.append(textarea);
   693	      textarea.select();
   694	      document.execCommand("copy");
   695	      textarea.remove();
   696	    }
   697	    setRequestStatus("当前工作区交接摘要已复制。", "success");
   698	  } catch (error) {
   699	    setRequestStatus(`复制交接摘要失败：${String(error.message || error)}`, "error");
   700	  }
   701	}
   702	
   703	function collectWorkbenchPacketWorkspaceState() {
   704	  return {
   705	    kind: "well-harness-workbench-browser-workspace",
   706	    version: 2,
   707	    exportedAt: new Date().toISOString(),
   708	    handoff: buildWorkbenchHandoffSnapshot(),
   709	    packetJsonText: workbenchElement("workbench-packet-json").value,
   710	    packetSourceStatus: workbenchElement("workbench-packet-source-status").textContent,
   711	    currentWorkbenchRunLabel,
   712	    selectedWorkbenchPacketRevisionId,
   713	    packetRevisionHistory: cloneJson(workbenchPacketRevisionHistory),
   714	    currentWorkbenchViewMode,
   715	    selectedWorkbenchHistoryId,
   716	    runHistory: cloneJson(workbenchRunHistory),
   717	    fields: Object.fromEntries(workbenchPersistedFieldIds.map((id) => [id, readWorkbenchPersistedFieldValue(id)])),
   718	  };
   719	}
   720	
   721	function persistWorkbenchPacketWorkspace() {
   722	  renderWorkbenchHandoffBoard();
   723	  if (suspendWorkbenchPacketWorkspacePersistence) {
   724	    return;
   725	  }
   726	  const storage = workbenchBrowserStorage();
   727	  if (!storage) {
   728	    return;
   729	  }
   730	  try {
   731	    storage.setItem(
   732	      workbenchPacketWorkspaceStorageKey,
   733	      JSON.stringify(collectWorkbenchPacketWorkspaceState()),
   734	    );
   735	  } catch (error) {
   736	    // Ignore persistence failures so the workbench stays usable in storage-limited environments.
   737	  }
   738	}
   739	
   740	function clearPersistedWorkbenchPacketWorkspace() {
   741	  const storage = workbenchBrowserStorage();
   742	  if (!storage) {
   743	    return;
   744	  }
   745	  try {
   746	    storage.removeItem(workbenchPacketWorkspaceStorageKey);
   747	  } catch (error) {
   748	    // Ignore storage cleanup failures.
   749	  }
   750	}
   751	
   752	function loadPersistedWorkbenchPacketWorkspace() {
   753	  const storage = workbenchBrowserStorage();
   754	  if (!storage) {
   755	    return null;
   756	  }
   757	  const raw = storage.getItem(workbenchPacketWorkspaceStorageKey);
   758	  if (!raw) {
   759	    return null;
   760	  }
   761	  try {
   762	    return JSON.parse(raw);
   763	  } catch (error) {
   764	    clearPersistedWorkbenchPacketWorkspace();
   765	    return null;
   766	  }
   767	}
   768	
   769	// ─── P43 draft_design_state persistence (UI-owned, never read by backend) ─────
   770	
   771	function saveDraftDesignState(draftObj) {
   772	  const storage = workbenchBrowserStorage();
   773	  if (!storage) {
   774	    return;
   775	  }
   776	  try {
   777	    storage.setItem(draftDesignStateKey, JSON.stringify(draftObj));
   778	  } catch (error) {
   779	    // Ignore persistence failures so the workbench stays usable.
   780	  }
   781	}
   782	
   783	function loadDraftDesignState() {
   784	  const storage = workbenchBrowserStorage();
   785	  if (!storage) {
   786	    return null;
   787	  }
   788	  const raw = storage.getItem(draftDesignStateKey);
   789	  if (!raw) {
   790	    return null;
   791	  }
   792	  try {
   793	    return JSON.parse(raw);
   794	  } catch (error) {
   795	    clearDraftDesignState();
   796	    return null;
   797	  }
   798	}
   799	
   800	function clearDraftDesignState() {
   801	  const storage = workbenchBrowserStorage();
   802	  if (!storage) {
   803	    return;
   804	  }
   805	  try {
   806	    storage.removeItem(draftDesignStateKey);
   807	  } catch (error) {
   808	    // Ignore cleanup failures.
   809	  }
   810	}
   811	
   812	// ─────────────────────────────────────────────────────────────────────────────
   813	
   814	function workspaceSnapshotDownloadName() {
   815	  const now = new Date();
   816	  const timestamp = [
   817	    now.getFullYear(),
   818	    String(now.getMonth() + 1).padStart(2, "0"),
   819	    String(now.getDate()).padStart(2, "0"),
   820	    "-",
   821	    String(now.getHours()).padStart(2, "0"),
   822	    String(now.getMinutes()).padStart(2, "0"),
   823	    String(now.getSeconds()).padStart(2, "0"),
   824	  ].join("");
   825	  return `well-harness-workbench-workspace-${timestamp}.json`;
   826	}
   827	
   828	function packetRevisionSignature(payload) {
   829	  return JSON.stringify(payload);
   830	}
   831	
   832	function nextWorkbenchHistoryId() {
   833	  workbenchHistorySequence += 1;
   834	  return `workbench-history-${workbenchHistorySequence}`;
   835	}
   836	
   837	function nextWorkbenchPacketRevisionId() {
   838	  workbenchPacketRevisionSequence += 1;
   839	  return `workbench-packet-revision-${workbenchPacketRevisionSequence}`;
   840	}
   841	
   842	function setActiveWorkbenchPreset(presetId) {
   843	  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
   844	    const selected = button.dataset.workbenchPreset === presetId;
   845	    button.classList.toggle("is-selected", selected);
   846	    button.setAttribute("aria-pressed", selected ? "true" : "false");
   847	  });
   848	}
   849	
   850	function setCurrentWorkbenchRunLabel(label) {
   851	  currentWorkbenchRunLabel = label || "手动生成";
   852	  persistWorkbenchPacketWorkspace();
   853	}
   854	
   855	function setPacketEditor(payload) {
   856	  workbenchElement("workbench-packet-json").value = prettyJson(payload);
   857	  persistWorkbenchPacketWorkspace();
   858	}
   859	
   860	function parseWorkbenchPacketEditor() {
   861	  const raw = workbenchElement("workbench-packet-json").value;
   862	  if (!raw.trim()) {
   863	    return {error: "当前 Packet JSON 为空。"};
   864	  }
   865	  try {
   866	    return {payload: JSON.parse(raw)};
   867	  } catch (error) {
   868	    return {error: String(error.message || error)};
   869	  }
   870	}
   871	
   872	function renderValue(elementId, value, fallbackText = "-") {
   873	  if (typeof value === "string") {
   874	    const text = value.trim();
   875	    workbenchElement(elementId).textContent = text || fallbackText;
   876	    return;
   877	  }
   878	  if (value === null || value === undefined) {
   879	    workbenchElement(elementId).textContent = fallbackText;
   880	    return;
   881	  }
   882	  workbenchElement(elementId).textContent = String(value);
   883	}
   884	
   885	function summarizePacketPayload(payload) {
   886	  return {
   887	    sourceDocuments: Array.isArray(payload.source_documents) ? payload.source_documents.length : 0,
   888	    components: Array.isArray(payload.components) ? payload.components.length : 0,
   889	    logicNodes: Array.isArray(payload.logic_nodes) ? payload.logic_nodes.length : 0,
   890	    scenarios: Array.isArray(payload.acceptance_scenarios) ? payload.acceptance_scenarios.length : 0,
   891	    faultModes: Array.isArray(payload.fault_modes) ? payload.fault_modes.length : 0,
   892	    clarificationAnswers: Array.isArray(payload.clarification_answers) ? payload.clarification_answers.length : 0,
   893	  };
   894	}
   895	
   896	function packetRevisionDetailText(payload) {
   897	  const summary = summarizePacketPayload(payload);
   898	  return `docs=${summary.sourceDocuments} / components=${summary.components} / logic=${summary.logicNodes} / scenarios=${summary.scenarios} / faults=${summary.faultModes} / answers=${summary.clarificationAnswers}`;
   899	}
   900	
   901	function latestWorkbenchPacketRevisionEntry() {
   902	  return workbenchPacketRevisionHistory.length ? workbenchPacketRevisionHistory[0] : null;
   903	}
   904	
   905	function selectedWorkbenchPacketRevisionEntry() {
   906	  return workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || latestWorkbenchPacketRevisionEntry();
   907	}
   908	
   909	function normalizeWorkbenchPacketRevisionHistory(entries) {
   910	  if (!Array.isArray(entries)) {
   911	    return [];
   912	  }
   913	  return entries
   914	    .filter((entry) => entry && typeof entry.id === "string" && entry.id && entry.payload)
   915	    .map((entry) => ({
   916	      id: entry.id,
   917	      timeLabel: entry.timeLabel || historyTimeLabel(),
   918	      title: entry.title || "Packet 更新",
   919	      payload: cloneJson(entry.payload),
   920	      summary: entry.summary || `${entry.payload.system_id || "unknown_system"} 已更新`,
   921	      detail: entry.detail || packetRevisionDetailText(entry.payload),
   922	      signature: packetRevisionSignature(entry.payload),
   923	    }))
   924	    .slice(0, maxWorkbenchPacketRevisionHistory);
   925	}
   926	
   927	function normalizeWorkbenchRunHistory(entries) {
   928	  if (!Array.isArray(entries)) {
   929	    return [];
   930	  }
   931	  return entries
   932	    .filter((entry) => entry && typeof entry.id === "string" && entry.id)
   933	    .map((entry) => ({
   934	      id: entry.id,
   935	      state: entry.state || "failure",
   936	      stateLabel: entry.stateLabel || (entry.state === "ready" ? "通过" : entry.state === "blocked" ? "阻塞" : "失败"),
   937	      archived: Boolean(entry.archived),
   938	      timeLabel: entry.timeLabel || historyTimeLabel(),
   939	      title: entry.title || "手动生成",
   940	      payload: entry.payload ? cloneJson(entry.payload) : null,
   941	      errorMessage: entry.errorMessage ? String(entry.errorMessage) : undefined,
   942	      summary: entry.summary || "请求未完成",
   943	      detail: entry.detail || "等待详情。",
   944	    }))
   945	    .slice(0, maxWorkbenchRunHistory);
   946	}
   947	
   948	function buildWorkbenchPacketRevisionEntry(payload, {
   949	  title,
   950	  summary,
   951	  detail,
   952	} = {}) {
   953	  return {
   954	    id: nextWorkbenchPacketRevisionId(),
   955	    timeLabel: historyTimeLabel(),
   956	    title: title || "Packet 更新",
   957	    payload: cloneJson(payload),
   958	    summary: summary || `${payload.system_id || "unknown_system"} 已更新`,
   959	    detail: detail || packetRevisionDetailText(payload),
   960	    signature: packetRevisionSignature(payload),
   961	  };
   962	}
   963	
   964	function splitLines(text) {
   965	  return text
   966	    .split("\n")
   967	    .map((item) => item.trim())
   968	    .filter(Boolean);
   969	}
   970	
   971	function setVisualBadge(state, text) {
   972	  const element = workbenchElement("workbench-visual-badge");
   973	  element.dataset.state = state;
   974	  element.textContent = text;
   975	}
   976	
   977	function setStageState(stageName, state, note) {
   978	  workbenchElement(`workbench-stage-${stageName}`).dataset.state = state;
   979	  workbenchElement(`workbench-stage-${stageName}-note`).textContent = note;
   980	}
   981	
   982	function setOnboardingBadge(state, text) {
   983	  const element = workbenchElement("workbench-onboarding-badge");
   984	  element.dataset.state = state;
   985	  element.textContent = text;
   986	}
   987	
   988	function setFingerprintBadge(state, text) {
   989	  const element = workbenchElement("workbench-fingerprint-badge");
   990	  element.dataset.state = state;
   991	  element.textContent = text;
   992	}
   993	
   994	function setActionsBadge(state, text) {
   995	  const element = workbenchElement("workbench-actions-badge");
   996	  element.dataset.state = state;
   997	  element.textContent = text;
   998	}
   999	
  1000	function setSchemaRepairBadge(state, text) {
  1001	  const element = workbenchElement("workbench-schema-workspace-badge");
  1002	  element.dataset.state = state;
  1003	  element.textContent = text;
  1004	}
  1005	
  1006	function setClarificationWorkspaceBadge(state, text) {
  1007	  const element = workbenchElement("workbench-clarification-workspace-badge");
  1008	  element.dataset.state = state;
  1009	  element.textContent = text;
  1010	}
  1011	
  1012	function uniqueValues(values) {
  1013	  return [...new Set(
  1014	    values
  1015	      .map((value) => (typeof value === "string" ? value.trim() : ""))
  1016	      .filter(Boolean),
  1017	  )];
  1018	}
  1019	
  1020	function joinWithFallback(values, fallbackText = "-") {
  1021	  return values.length ? values.join(" / ") : fallbackText;
  1022	}
  1023	
  1024	function documentKindLabel(kind) {
  1025	  const labels = {
  1026	    markdown: "Markdown",
  1027	    notion: "Notion",
  1028	    pdf: "PDF",
  1029	    spreadsheet: "表格",
  1030	  };
  1031	  return labels[kind] || kind || "未知来源";
  1032	}
  1033	
  1034	function documentRoleLabel(role) {
  1035	  const labels = {
  1036	    acceptance_evidence: "验收证据",
  1037	    logic_spec: "逻辑规格",
  1038	    troubleshooting_note: "排故说明",
  1039	    timeline_note: "时间线说明",
  1040	  };
  1041	  return labels[role] || role || "未标注角色";
  1042	}
  1043	
  1044	function signalKindLabel(kind) {
  1045	  const labels = {
  1046	    command: "命令",
  1047	    commanded_state: "命令状态",
  1048	    derived: "派生量",
  1049	    sensor: "传感器",
  1050	    switch: "开关",
  1051	  };
  1052	  return labels[kind] || kind || "未知类型";
  1053	}
  1054	
  1055	function stateShapeLabel(stateShape) {
  1056	  const labels = {
  1057	    analog: "连续量",
  1058	    binary: "二值",
  1059	    discrete: "离散态",
  1060	  };
  1061	  return labels[stateShape] || stateShape || "未知形态";
  1062	}
  1063	
  1064	function createFingerprintChip(text, tone = "neutral") {
  1065	  const chip = document.createElement("span");
  1066	  chip.className = "workbench-fingerprint-chip";
  1067	  chip.dataset.tone = tone;
  1068	  chip.textContent = text;
  1069	  return chip;
  1070	}
  1071	
  1072	function createFingerprintEmptyCard(message) {
  1073	  const card = document.createElement("article");
  1074	  card.className = "workbench-fingerprint-item is-empty";
  1075	
  1076	  const detail = document.createElement("p");
  1077	  detail.className = "workbench-fingerprint-empty";
  1078	  detail.textContent = message;
  1079	
  1080	  card.append(detail);
  1081	  return card;
  1082	}
  1083	
  1084	function createActionItemCard({
  1085	  title,
  1086	  detail,
  1087	  chipText,
  1088	  chipTone = "neutral",
  1089	}) {
  1090	  const card = document.createElement("article");
  1091	  card.className = "workbench-actions-item";
  1092	
  1093	  const header = document.createElement("div");
  1094	  header.className = "workbench-actions-item-header";
  1095	
  1096	  const strong = document.createElement("strong");
  1097	  strong.className = "workbench-actions-item-title";
  1098	  strong.textContent = title;
  1099	
  1100	  const chip = createFingerprintChip(chipText, chipTone);
  1101	
  1102	  header.append(strong, chip);
  1103	
  1104	  const body = document.createElement("p");
  1105	  body.className = "workbench-actions-item-detail";
  1106	  body.textContent = detail;
  1107	
  1108	  card.append(header, body);
  1109	  return card;
  1110	}
  1111	
  1112	function createClarificationWorkspaceCard({
  1113	  id,
  1114	  prompt,
  1115	  rationale,
  1116	  requiredFor,
  1117	  answer = "",
  1118	  status = "needs_answer",
  1119	  editable = true,
  1120	}) {
  1121	  const card = document.createElement("article");
  1122	  card.className = "workbench-clarification-card";
  1123	
  1124	  const header = document.createElement("div");
  1125	  header.className = "workbench-clarification-card-header";
  1126	
  1127	  const titleGroup = document.createElement("div");
  1128	  const title = document.createElement("strong");
  1129	  title.textContent = id || "clarification";
  1130	  const promptText = document.createElement("p");
  1131	  promptText.textContent = prompt || "等待补齐说明。";
  1132	  titleGroup.append(title, promptText);
  1133	
  1134	  const chip = createFingerprintChip(status === "answered" ? "已回答" : "待回答", status === "answered" ? "ready" : "blocked");
  1135	  header.append(titleGroup, chip);
  1136	
  1137	  const meta = document.createElement("div");
  1138	  meta.className = "workbench-clarification-card-meta";
  1139	
  1140	  const rationaleText = document.createElement("span");
  1141	  rationaleText.textContent = `为什么要补：${rationale || "等待说明。"}`;
  1142	  const requiredForText = document.createElement("span");
  1143	  requiredForText.textContent = `补齐后用于：${requiredFor || "spec_build"}`;
  1144	  meta.append(rationaleText, requiredForText);
  1145	
  1146	  const textarea = document.createElement("textarea");
  1147	  textarea.className = "workbench-clarification-answer";
  1148	  textarea.dataset.questionId = id || "";
  1149	  textarea.placeholder = "在这里填写工程答案，写回 packet 后可直接重跑。";
  1150	  textarea.value = answer || "";
  1151	  textarea.disabled = !editable;
  1152	
  1153	  card.append(header, meta, textarea);
  1154	  return card;
  1155	}
  1156	
  1157	function createSchemaRepairCard({
  1158	  title,
  1159	  detail,
  1160	  targetPath,
  1161	  expectedEffect,
  1162	  autofixAvailable = false,
  1163	}) {
  1164	  const card = document.createElement("article");
  1165	  card.className = "workbench-schema-card";
  1166	
  1167	  const header = document.createElement("div");
  1168	  header.className = "workbench-schema-card-header";
  1169	
  1170	  const titleGroup = document.createElement("div");
  1171	  const strong = document.createElement("strong");
  1172	  strong.textContent = title;
  1173	  const body = document.createElement("p");
  1174	  body.textContent = detail;
  1175	  titleGroup.append(strong, body);
  1176	
  1177	  const chip = createFingerprintChip(autofixAvailable ? "可自动补齐" : "需手工修复", autofixAvailable ? "ready" : "blocked");
  1178	  header.append(titleGroup, chip);
  1179	
  1180	  const meta = document.createElement("div");
  1181	  meta.className = "workbench-schema-card-meta";
  1182	
  1183	  const pathText = document.createElement("span");
  1184	  pathText.textContent = `目标位置：${targetPath || "packet JSON"}`;
  1185	  const effectText = document.createElement("span");
  1186	  effectText.textContent = `修复结果：${expectedEffect || "修复后再重跑验证。"}`;
  1187	  meta.append(pathText, effectText);
  1188	
  1189	  card.append(header, meta);
  1190	  return card;
  1191	}
  1192	
  1193	function renderFingerprintDocumentList(documents, fallbackText) {
  1194	  const container = workbenchElement("workbench-fingerprint-doc-list");
  1195	  if (!documents.length) {
  1196	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1197	    return;
  1198	  }
  1199	
  1200	  container.replaceChildren(...documents.map((document) => {
  1201	    const card = document.createElement("article");
  1202	    card.className = "workbench-fingerprint-item";
  1203	
  1204	    const header = document.createElement("div");
  1205	    header.className = "workbench-fingerprint-item-header";
  1206	
  1207	    const title = document.createElement("strong");
  1208	    title.className = "workbench-fingerprint-item-title";
  1209	    title.textContent = document.title || document.id || "未命名文档";
  1210	
  1211	    const chips = document.createElement("div");
  1212	    chips.className = "workbench-fingerprint-chip-row";
  1213	    chips.append(
  1214	      createFingerprintChip(documentKindLabel(document.kind), "source"),
  1215	      createFingerprintChip(documentRoleLabel(document.role), "role"),
  1216	    );
  1217	
  1218	    header.append(title, chips);
  1219	
  1220	    const location = document.createElement("p");
  1221	    location.className = "workbench-fingerprint-item-detail";
  1222	    location.textContent = document.location || "未提供路径";
  1223	
  1224	    card.append(header, location);
  1225	    return card;
  1226	  }));
  1227	}
  1228	
  1229	function renderFingerprintSignalList(signals, fallbackText) {
  1230	  const container = workbenchElement("workbench-fingerprint-signal-list");
  1231	  if (!signals.length) {
  1232	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1233	    return;
  1234	  }
  1235	
  1236	  container.replaceChildren(...signals.map((signal) => {
  1237	    const card = document.createElement("article");
  1238	    card.className = "workbench-fingerprint-item";
  1239	
  1240	    const header = document.createElement("div");
  1241	    header.className = "workbench-fingerprint-item-header";
  1242	
  1243	    const title = document.createElement("strong");
  1244	    title.className = "workbench-fingerprint-item-title";
  1245	    title.textContent = signal.label || signal.id || "未命名信号";
  1246	
  1247	    const chips = document.createElement("div");
  1248	    chips.className = "workbench-fingerprint-chip-row";
  1249	    chips.append(
  1250	      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
  1251	      createFingerprintChip(stateShapeLabel(signal.state_shape), "shape"),
  1252	      createFingerprintChip(signal.unit || "无单位", "unit"),
  1253	    );
  1254	
  1255	    header.append(title, chips);
  1256	
  1257	    const detail = document.createElement("p");
  1258	    detail.className = "workbench-fingerprint-item-detail";
  1259	    detail.textContent = signal.id ? `signal_id = ${signal.id}` : "未提供 signal_id";
  1260	
  1261	    card.append(header, detail);
  1262	    return card;
  1263	  }));
  1264	}
  1265	
  1266	function renderSystemFingerprint({
  1267	  badgeState = "idle",
  1268	  badgeText = "等待生成",
  1269	  summary = "这里会直接告诉你第二套系统到底长什么样，而不只是告诉你它能不能接。",
  1270	  systemId = "-",
  1271	  objective = "-",
  1272	  sourceMode = "-",
  1273	  sourceTruth = "-",
  1274	  documents = [],
  1275	  signals = [],
  1276	  documentFallback = "还没有来源文档。",
  1277	  signalFallback = "还没有关键信号定义。",
  1278	} = {}) {
  1279	  setFingerprintBadge(badgeState, badgeText);
  1280	  renderValue("workbench-fingerprint-summary", summary);
  1281	  renderValue("workbench-fingerprint-system-id", systemId);
  1282	  renderValue("workbench-fingerprint-objective", objective);
  1283	  renderValue("workbench-fingerprint-source-mode", sourceMode);
  1284	  renderValue("workbench-fingerprint-source-truth", sourceTruth);
  1285	  renderValue("workbench-fingerprint-doc-count", `${documents.length} 份文档`);
  1286	  renderValue("workbench-fingerprint-signal-count", `${signals.length} 个信号`);
  1287	  renderFingerprintDocumentList(documents, documentFallback);
  1288	  renderFingerprintSignalList(signals, signalFallback);
  1289	}
  1290	
  1291	function renderActionList(containerId, items, fallbackText) {
  1292	  const container = workbenchElement(containerId);
  1293	  if (!items.length) {
  1294	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1295	    return;
  1296	  }
  1297	  container.replaceChildren(...items);
  1298	}
  1299	
  1300	function renderOnboardingActions({
  1301	  badgeState = "idle",
  1302	  badgeText = "等待生成",
  1303	  summary = "这里会把接入动作拆成三列：先补澄清、再补结构、最后看解锁项。",
  1304	  followUps = [],
  1305	  blockers = [],
  1306	  unlocks = [],
  1307	  followUpFallback = "运行后这里会列出需要先回答的澄清项。",
  1308	  blockerFallback = "运行后这里会列出需要补的结构问题。",
  1309	  unlockFallback = "运行后这里会列出补齐后可解锁的能力。",
  1310	} = {}) {
  1311	  setActionsBadge(badgeState, badgeText);
  1312	  renderValue("workbench-actions-summary", summary);
  1313	  renderValue("workbench-actions-follow-up-count", `${followUps.length} 项`);
  1314	  renderValue("workbench-actions-schema-count", `${blockers.length} 项`);
  1315	  renderValue("workbench-actions-unlock-count", `${unlocks.length} 项`);
  1316	  renderActionList("workbench-actions-follow-up-list", followUps, followUpFallback);
  1317	  renderActionList("workbench-actions-schema-list", blockers, blockerFallback);
  1318	  renderActionList("workbench-actions-unlock-list", unlocks, unlockFallback);
  1319	}
  1320	
  1321	function setSchemaRepairActionState(disabled) {
  1322	  workbenchElement("workbench-apply-schema-repairs").disabled = disabled;
  1323	}
  1324	
  1325	function renderSchemaRepairWorkspace({
  1326	  badgeState = "idle",
  1327	  badgeText = "等待生成",
  1328	  summary = "这里会把 schema blocker 里的安全 autofix 项单独挑出来。",
  1329	  cards = [],
  1330	  fallbackTitle = "等待生成",
  1331	  fallbackText = "blocked bundle 出来后，这里会显示 repair suggestions。",
  1332	  note = "只有后端标记为 safe autofix 的修复才会开放一键应用。",
  1333	  actionsDisabled = true,
  1334	} = {}) {
  1335	  setSchemaRepairBadge(badgeState, badgeText);
  1336	  renderValue("workbench-schema-workspace-summary", summary);
  1337	  renderValue("workbench-schema-workspace-note", note);
  1338	  const container = workbenchElement("workbench-schema-workspace-list");
  1339	  if (!cards.length) {
  1340	    const emptyCard = document.createElement("article");
  1341	    emptyCard.className = "workbench-schema-card is-empty";
  1342	    const title = document.createElement("strong");
  1343	    title.textContent = fallbackTitle;
  1344	    const detail = document.createElement("p");
  1345	    detail.textContent = fallbackText;
  1346	    emptyCard.append(title, detail);
  1347	    container.replaceChildren(emptyCard);
  1348	  } else {
  1349	    container.replaceChildren(...cards);
  1350	  }
  1351	  setSchemaRepairActionState(actionsDisabled);
  1352	}
  1353	
  1354	function renderSchemaRepairWorkspaceFromPayload(payload) {
  1355	  const bundle = payload.bundle || {};
  1356	  const assessment = bundle.intake_assessment || {};
  1357	  const ready = Boolean(bundle.ready_for_spec_build);
  1358	  const repairSuggestions = Array.isArray(assessment.repair_suggestions) ? assessment.repair_suggestions : [];
  1359	  const safeSuggestions = repairSuggestions.filter((item) => item.autofix_available);
  1360	  const cards = repairSuggestions.map((item) => createSchemaRepairCard({
  1361	    title: item.title || item.id || "schema repair",
  1362	    detail: item.detail || item.blocking_reason || "等待修复说明。",
  1363	    targetPath: item.target_path || "packet JSON",
  1364	    expectedEffect: item.expected_effect,
  1365	    autofixAvailable: Boolean(item.autofix_available),
  1366	  }));
  1367	
  1368	  if (ready) {
  1369	    renderSchemaRepairWorkspace({
  1370	      badgeState: "ready",
  1371	      badgeText: "当前无需修复",
  1372	      summary: "这次 bundle 已经没有 schema blocker 需要修复；工作台保留为空，避免把当前 ready 状态误读成还有结构问题。",
  1373	      fallbackTitle: "当前无需 schema 修复",
  1374	      fallbackText: "schema blocker 已经清空，可以继续用当前 packet 跑 playback / diagnosis / knowledge。",
  1375	      note: "当前没有安全 schema 修复要应用。",
  1376	      actionsDisabled: true,
  1377	    });
  1378	    return;
  1379	  }
  1380	
  1381	  renderSchemaRepairWorkspace({
  1382	    badgeState: safeSuggestions.length ? "blocked" : "idle",
  1383	    badgeText: safeSuggestions.length ? "可安全修一点" : "暂时无安全修复",
  1384	    summary: safeSuggestions.length
  1385	      ? "这次 blocked bundle 里有后端确认安全的 schema autofix。你可以一键应用这些修复，然后马上重跑。"
  1386	      : "这次 blocked bundle 虽然还有 schema blocker，但当前没有被后端判定为 safe autofix 的修复项。",
  1387	    cards,
  1388	    fallbackTitle: "当前没有 repair suggestion",
  1389	    fallbackText: "当前没有额外 schema repair suggestion；如果仍阻塞，请直接检查 packet JSON。",
  1390	    note: safeSuggestions.length
  1391	      ? `当前共有 ${safeSuggestions.length} 条 safe autofix；工作台不会猜修复逻辑，只调用后端声明为安全的 patch。`
  1392	      : "剩余 schema blocker 需要手工修改 packet JSON 或工程语义后再重跑。",
  1393	    actionsDisabled: !safeSuggestions.length,
  1394	  });
  1395	}
  1396	
  1397	function setClarificationWorkspaceActionState(disabled) {
  1398	  workbenchElement("workbench-apply-clarifications").disabled = disabled;
  1399	  workbenchElement("workbench-apply-and-rerun").disabled = disabled;
  1400	}
  1401	
  1402	function renderClarificationWorkspace({
  1403	  badgeState = "idle",
  1404	  badgeText = "等待生成",
  1405	  summary = "这里会把需要补的 clarification 直接变成可填写表单，方便你写回当前 packet。",
  1406	  cards = [],
  1407	  fallbackTitle = "等待生成",
  1408	  fallbackText = "当 bundle 停在 clarification gate 时，这里会出现可直接填写的答案卡。",
  1409	  note = "先运行一次 blocked bundle，这里才会知道哪些问题还没回答。",
  1410	  actionsDisabled = true,
  1411	} = {}) {
  1412	  setClarificationWorkspaceBadge(badgeState, badgeText);
  1413	  renderValue("workbench-clarification-workspace-summary", summary);
  1414	  renderValue("workbench-clarification-workspace-note", note);
  1415	  const container = workbenchElement("workbench-clarification-workspace-list");
  1416	  if (!cards.length) {
  1417	    const emptyCard = document.createElement("article");
  1418	    emptyCard.className = "workbench-clarification-card is-empty";
  1419	    const title = document.createElement("strong");
  1420	    title.textContent = fallbackTitle;
  1421	    const detail = document.createElement("p");
  1422	    detail.textContent = fallbackText;
  1423	    emptyCard.append(title, detail);
  1424	    container.replaceChildren(emptyCard);
  1425	  } else {
  1426	    container.replaceChildren(...cards);
  1427	  }
  1428	  setClarificationWorkspaceActionState(actionsDisabled);
  1429	}
  1430	
  1431	function renderClarificationWorkspaceFromPayload(payload) {
  1432	  const bundle = payload.bundle || {};
  1433	  const clarification = bundle.clarification_brief || {};
  1434	  const ready = Boolean(bundle.ready_for_spec_build);
  1435	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  1436	  const unresolvedItems = followUpItems.filter((item) => item.status !== "answered");
  1437	  const cards = unresolvedItems.map((item) => createClarificationWorkspaceCard({
  1438	    id: item.id,
  1439	    prompt: item.prompt,
  1440	    rationale: item.rationale,
  1441	    requiredFor: item.required_for,
  1442	    answer: item.answer,
  1443	    status: item.status,
  1444	    editable: true,
  1445	  }));
  1446	
  1447	  if (ready) {
  1448	    renderClarificationWorkspace({
  1449	      badgeState: "ready",
  1450	      badgeText: "澄清已放行",
  1451	      summary: "这次 bundle 已经把 clarification gate 走通了；当前无需补答，如果要改问题答案，可以直接编辑 packet JSON 后重跑。",
  1452	      fallbackTitle: "当前无需回填",
  1453	      fallbackText: "clarification 问题已经补齐，当前链路可以继续往 playback / diagnosis / knowledge 走。",
  1454	      note: "当前 packet 已 ready；工作台按钮已关闭，避免把已通过状态误当成待补状态。",
  1455	      actionsDisabled: true,
  1456	    });
  1457	    return;
  1458	  }
  1459	
  1460	  renderClarificationWorkspace({
  1461	    badgeState: cards.length ? "blocked" : "idle",
  1462	    badgeText: cards.length ? "可直接回填" : "等待回填项",
  1463	    summary: cards.length
  1464	      ? "当前 bundle 停在 clarification gate；你可以直接在这里填写工程答案，写回 packet 后立即重跑。"
  1465	      : "这次虽然没 ready，但当前没有额外待回答的问题卡；如果仍阻塞，请优先看上方 schema blocker。",
  1466	    cards,
  1467	    fallbackTitle: "当前没有待答问题",
  1468	    fallbackText: "clarification 问题已经回答完毕，剩下的阻塞主要来自 schema / 结构问题。",
  1469	    note: cards.length
  1470	      ? `已加载 ${cards.length} 条待回答 clarification；“写回当前 Packet”不会新增前端规则，只会更新 packet JSON。`
  1471	      : "当前无待回答 clarification；请先修复 schema blocker 后再重跑。",
  1472	    actionsDisabled: !cards.length,
  1473	  });
  1474	}
  1475	
  1476	function currentClarificationWorkspaceAnswers() {
  1477	  return [...document.querySelectorAll(".workbench-clarification-answer")]
  1478	    .map((field) => ({
  1479	      questionId: field.dataset.questionId || "",
  1480	      answer: field.value.trim(),
  1481	    }))
  1482	    .filter((item) => item.questionId);
  1483	}
  1484	
  1485	function applyClarificationWorkspaceAnswersToPacket(packetPayload) {
  1486	  const nextPayload = cloneJson(packetPayload);
  1487	  const existingAnswers = Array.isArray(nextPayload.clarification_answers) ? nextPayload.clarification_answers : [];
  1488	  const answerMap = new Map(existingAnswers
  1489	    .filter((item) => item && typeof item.question_id === "string" && item.question_id.trim())
  1490	    .map((item) => [item.question_id.trim(), {
  1491	      question_id: item.question_id.trim(),
  1492	      answer: typeof item.answer === "string" ? item.answer : "",
  1493	      status: item.status || "answered",
  1494	    }]));
  1495	  const workspaceAnswers = currentClarificationWorkspaceAnswers();
  1496	  const workspaceIds = workspaceAnswers.map((item) => item.questionId);
  1497	
  1498	  workspaceAnswers.forEach((item) => {
  1499	    if (!item.answer) {
  1500	      answerMap.delete(item.questionId);
  1501	      return;
  1502	    }
  1503	    answerMap.set(item.questionId, {
  1504	      question_id: item.questionId,
  1505	      answer: item.answer,
  1506	      status: "answered",
  1507	    });
  1508	  });
  1509	
  1510	  nextPayload.clarification_answers = [
  1511	    ...workspaceIds
  1512	      .map((questionId) => answerMap.get(questionId))
  1513	      .filter(Boolean),
  1514	    ...[...answerMap.entries()]
  1515	      .filter(([questionId]) => !workspaceIds.includes(questionId))
  1516	      .map(([, answer]) => answer),
  1517	  ];
  1518	  return {
  1519	    packetPayload: nextPayload,
  1520	    answeredCount: workspaceAnswers.filter((item) => item.answer).length,
  1521	  };
  1522	}
  1523	
  1524	async function runWorkbenchSchemaSafeRepair() {
  1525	  let packetPayload;
  1526	  try {
  1527	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  1528	  } catch (error) {
  1529	    setRequestStatus(`当前 Packet JSON 无法应用 schema 修复：${String(error.message || error)}`, "error");
  1530	    return;
  1531	  }
  1532	
  1533	  setRequestStatus("正在应用安全 schema 修复...", "neutral");
  1534	  try {
  1535	    const response = await fetch(workbenchRepairPath, {
  1536	      method: "POST",
  1537	      headers: {"Content-Type": "application/json"},
  1538	      body: JSON.stringify({
  1539	        packet_payload: packetPayload,
  1540	        apply_all_safe: true,
  1541	      }),
  1542	    });
  1543	    const payload = await response.json();
  1544	    if (!response.ok) {
  1545	      throw new Error(payload.message || payload.error || "workbench safe repair request failed");
  1546	    }
  1547	    maybeAutoSnapshotCurrentPacketDraft("应用安全 schema 修复");
  1548	    setPacketEditor(payload.packet_payload);
  1549	    setPacketSourceStatus(`当前 packet 已应用 ${payload.applied_suggestion_ids.length} 条安全 schema 修复，并准备重跑。`);
  1550	    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.packet_payload, {
  1551	      title: "Schema 安全修复",
  1552	      summary: `已应用 ${payload.applied_suggestion_ids.length} 条 safe autofix`,
  1553	      detail: payload.applied_suggestion_ids.join(" / "),
  1554	    }));
  1555	    renderSystemFingerprintFromPacketPayload(payload.packet_payload, {
  1556	      badgeState: "idle",
  1557	      badgeText: "画像已更新",
  1558	      summary: "安全 schema 修复已经写回当前 packet；系统现在会基于修复后的 packet 继续重跑 bundle。",
  1559	    });
  1560	    setCurrentWorkbenchRunLabel("Schema 安全修复并重跑");
  1561	    setActiveWorkbenchPreset("");
  1562	    await runWorkbenchBundle();
  1563	  } catch (error) {
  1564	    setRequestStatus(`安全 schema 修复失败：${String(error.message || error)}`, "error");
  1565	  }
  1566	}
  1567	
  1568	async function applyClarificationWorkspace({
  1569	  rerun = false,
  1570	} = {}) {
  1571	  let packetPayload;
  1572	  try {
  1573	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  1574	  } catch (error) {
  1575	    setRequestStatus(`当前 Packet JSON 无法写回 clarification：${String(error.message || error)}`, "error");
  1576	    return;
  1577	  }
  1578	
  1579	  const {packetPayload: nextPayload, answeredCount} = applyClarificationWorkspaceAnswersToPacket(packetPayload);
  1580	  maybeAutoSnapshotCurrentPacketDraft("写回 clarification");
  1581	  setPacketEditor(nextPayload);
  1582	  setPacketSourceStatus(
  1583	    answeredCount
  1584	      ? `当前 packet 已写回 ${answeredCount} 条 clarification answer。`
  1585	      : "当前 packet 已清空这批 clarification answer。"
  1586	  );
  1587	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(nextPayload, {
  1588	    title: "Clarification 写回",
  1589	    summary: answeredCount
  1590	      ? `已写回 ${answeredCount} 条 clarification answer`
  1591	      : "已清空当前 clarification answer",
  1592	  }));
  1593	  renderSystemFingerprintFromPacketPayload(nextPayload, {
  1594	    badgeState: "idle",
  1595	    badgeText: "画像已更新",
  1596	    summary: "clarification 答案已经写回当前 packet；如果系统画像或文档方向没问题，可以直接重跑看 gate 是否放行。",
  1597	  });
  1598	  renderValue(
  1599	    "workbench-clarification-workspace-note",
  1600	    answeredCount
  1601	      ? `已把 ${answeredCount} 条答案写回当前 packet。${rerun ? "系统现在会直接重跑。" : "如需验证是否放行，可以点右侧按钮或主运行按钮重跑。"}`
  1602	      : "已清空当前工作台里的回答并写回 packet；如需验证，请重新运行。",
  1603	  );
  1604	  setRequestStatus(
  1605	    answeredCount
  1606	      ? (rerun ? "clarification 已写回，正在重跑 bundle..." : "clarification 已写回当前 packet。")
  1607	      : "clarification 修改已写回当前 packet。",
  1608	    rerun ? "neutral" : "success",
  1609	  );
  1610	
  1611	  if (rerun) {
  1612	    setCurrentWorkbenchRunLabel("Clarification 回填并重跑");
  1613	    setActiveWorkbenchPreset("");
  1614	    await runWorkbenchBundle();
  1615	  }
  1616	}
  1617	
  1618	function renderSystemFingerprintFromPacketPayload(packetPayload, {
  1619	  badgeState = "idle",
  1620	  badgeText = "画像已载入",
  1621	  summary = "样例已经装载。你现在就能先看这套系统的文档来源和关键信号，不用等 bundle 跑完。",
  1622	} = {}) {
  1623	  const documents = Array.isArray(packetPayload.source_documents) ? packetPayload.source_documents : [];
  1624	  const signals = Array.isArray(packetPayload.components) ? packetPayload.components : [];
  1625	  const documentKinds = uniqueValues(documents.map((document) => document.kind));
  1626	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
  1627	  if (documentKinds.length > 1) {
  1628	    sourceModeParts.push("混合来源");
  1629	  }
  1630	  if (documentKinds.includes("pdf")) {
  1631	    sourceModeParts.push("含 PDF");
  1632	  }
  1633	
  1634	  renderSystemFingerprint({
  1635	    badgeState,
  1636	    badgeText,
  1637	    summary,
  1638	    systemId: packetPayload.system_id || "-",
  1639	    objective: packetPayload.objective || "-",
  1640	    sourceMode: sourceModeParts.join(" / "),
  1641	    sourceTruth: packetPayload.source_of_truth || "等待工程真值说明",
  1642	    documents,
  1643	    signals,
  1644	    documentFallback: "当前 packet 还没有来源文档。",
  1645	    signalFallback: "当前 packet 还没有关键信号定义。",
  1646	  });
  1647	}
  1648	
  1649	function renderOnboardingReadiness({
  1650	  badgeState = "idle",
  1651	  badgeText = "等待生成",
  1652	  summary = "这里会直接告诉你：这份 packet 现在够不够支撑第二套控制逻辑进入 spec build。",
  1653	  docs = "-",
  1654	  docsDetail = "等待生成。",
  1655	  components = "-",
  1656	  componentsDetail = "等待生成。",
  1657	  logic = "-",
  1658	  logicDetail = "等待生成。",
  1659	  scenarios = "-",
  1660	  scenariosDetail = "等待生成。",
  1661	  faults = "-",
  1662	  faultsDetail = "等待生成。",
  1663	  clarifications = "-",
  1664	  clarificationsDetail = "等待生成。",
  1665	  unlocks = "-",
  1666	  gaps = "-",
  1667	} = {}) {
  1668	  setOnboardingBadge(badgeState, badgeText);
  1669	  renderValue("workbench-onboarding-summary", summary);
  1670	  renderValue("workbench-onboarding-docs", docs);
  1671	  renderValue("workbench-onboarding-docs-detail", docsDetail);
  1672	  renderValue("workbench-onboarding-components", components);
  1673	  renderValue("workbench-onboarding-components-detail", componentsDetail);
  1674	  renderValue("workbench-onboarding-logic", logic);
  1675	  renderValue("workbench-onboarding-logic-detail", logicDetail);
  1676	  renderValue("workbench-onboarding-scenarios", scenarios);
  1677	  renderValue("workbench-onboarding-scenarios-detail", scenariosDetail);
  1678	  renderValue("workbench-onboarding-faults", faults);
  1679	  renderValue("workbench-onboarding-faults-detail", faultsDetail);
  1680	  renderValue("workbench-onboarding-clarifications", clarifications);
  1681	  renderValue("workbench-onboarding-clarifications-detail", clarificationsDetail);
  1682	  renderValue("workbench-onboarding-unlocks", unlocks);
  1683	  renderValue("workbench-onboarding-gaps", gaps);
  1684	}
  1685	
  1686	function renderPreparationBoard(message) {
  1687	  setWorkbenchViewState("preparation");
  1688	  setVisualBadge("idle", "样例已就位");
  1689	  renderOnboardingReadiness({
  1690	    badgeState: "idle",
  1691	    badgeText: "样例待运行",
  1692	    summary: "样例已经装载，但还没有真正做 intake 检查；运行后这里才会告诉你第二套系统接入是否 ready。",
  1693	    gaps: "等待 intake",
  1694	  });
  1695	  renderValue("workbench-spotlight-verdict", "等待生成");
  1696	  renderValue("workbench-spotlight-verdict-detail", message);
  1697	  renderValue("workbench-spotlight-blocker", "尚未运行");
  1698	  renderValue("workbench-spotlight-blocker-detail", "点击“生成 Bundle”后，系统会告诉你卡在哪一步。");
  1699	  renderValue("workbench-spotlight-knowledge", "尚未形成");
  1700	  renderValue("workbench-spotlight-knowledge-detail", "还没有 diagnosis / knowledge 结果。");
  1701	  renderValue("workbench-spotlight-archive", "尚未归档");
  1702	  renderValue("workbench-spotlight-archive-detail", "如果勾选 archive，运行后这里会显示落档状态。");
  1703	  renderOnboardingActions({
  1704	    badgeState: "idle",
  1705	    badgeText: "等待动作生成",
  1706	    summary: "样例已经装载，但动作板还没真正跑 intake / clarification，所以先不猜下一步。",
  1707	  });
  1708	  renderSchemaRepairWorkspace({
  1709	    badgeState: "idle",
  1710	    badgeText: "等待修复项",
  1711	    summary: "样例虽然已经装载，但还没真正跑出 schema blocker，所以这里先不提前猜哪些结构问题能安全 autofix。",
  1712	    fallbackTitle: "等待第一次运行",
  1713	    fallbackText: "先跑一次 bundle；如果后端给出 repair suggestion，这里才会显示安全 schema 修复入口。",
  1714	    note: "当前只是样例准备阶段，还没有可应用的 schema repair。",
  1715	    actionsDisabled: true,
  1716	  });
  1717	  renderClarificationWorkspace({
  1718	    badgeState: "idle",
  1719	    badgeText: "等待回填项",
  1720	    summary: "样例虽然已经装载，但还没真正跑到 clarification gate，所以这里先不提前猜哪些问题要你回答。",
  1721	    fallbackTitle: "等待第一次运行",
  1722	    fallbackText: "先跑一次 bundle；如果它停在 clarification gate，这里就会出现可直接填写的答案卡。",
  1723	    note: "当前只是样例准备阶段，还没有需要写回的 clarification。",
  1724	    actionsDisabled: true,
  1725	  });
  1726	  renderValue(
  1727	    "workbench-visual-summary",
  1728	    "当前只是在准备样例。真正的验收结果会在你点击“生成 Bundle”之后出现在这里。",
  1729	  );
  1730	  setStageState("intake", "pending", "样例已装载，等待运行。");
  1731	  setStageState("clarification", "idle", "等待生成。");
  1732	  setStageState("playback", "idle", "等待生成。");
  1733	  setStageState("diagnosis", "idle", "等待生成。");
  1734	  setStageState("knowledge", "idle", "等待生成。");
  1735	  setStageState("archive", "idle", "等待生成。");
  1736	  renderWorkbenchHistoryViewBar();
  1737	  renderWorkbenchPacketHistoryViewBar();
  1738	}
  1739	
  1740	function pushWorkbenchRunHistory(entry) {
  1741	  setWorkbenchViewState("latest", entry.id);
  1742	  workbenchRunHistory = [entry, ...workbenchRunHistory].slice(0, maxWorkbenchRunHistory);
  1743	  renderWorkbenchRunHistory();
  1744	  persistWorkbenchPacketWorkspace();
  1745	}
  1746	
  1747	function renderWorkbenchPacketHistoryViewBar() {
  1748	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  1749	  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;
  1750	  const statusElement = workbenchElement("workbench-packet-history-status");
  1751	  const returnButton = workbenchElement("workbench-packet-history-return-latest");
  1752	
  1753	  if (!latestEntry) {
  1754	    statusElement.textContent = "当前 Packet：等待第一次载入";
  1755	    returnButton.disabled = true;
  1756	    renderWorkbenchPacketDraftState();
  1757	    renderWorkbenchPacketRevisionCompareBar();
  1758	    return;
  1759	  }
  1760	
  1761	  if (!selectedEntry || selectedEntry.id === latestEntry.id) {
  1762	    statusElement.textContent = `当前 Packet：最新版本 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
  1763	    returnButton.disabled = true;
  1764	    renderWorkbenchPacketDraftState();
  1765	    renderWorkbenchPacketRevisionCompareBar();
  1766	    return;
  1767	  }
  1768	
  1769	  statusElement.textContent = `当前 Packet：历史版本 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  1770	  returnButton.disabled = false;
  1771	  renderWorkbenchPacketDraftState();
  1772	  renderWorkbenchPacketRevisionCompareBar();
  1773	}
  1774	
  1775	function setPacketDraftActionState(disabled) {
  1776	  workbenchElement("workbench-save-packet-draft").disabled = disabled;
  1777	}
  1778	
  1779	function renderWorkbenchPacketDraftState() {
  1780	  const statusElement = workbenchElement("workbench-packet-draft-status");
  1781	  const noteElement = workbenchElement("workbench-packet-draft-note");
  1782	  const baselineEntry = selectedWorkbenchPacketRevisionEntry();
  1783	
  1784	  if (!baselineEntry) {
  1785	    const parsed = parseWorkbenchPacketEditor();
  1786	    if (parsed.error) {
  1787	      statusElement.textContent = "当前草稿：JSON 待修正";
  1788	      noteElement.textContent = `当前输入区已经恢复了草稿文本，但它还不是合法 JSON：${parsed.error}`;
  1789	      setPacketDraftActionState(true);
  1790	      return;
  1791	    }
  1792	    if (parsed.payload) {
  1793	      statusElement.textContent = "当前草稿：尚未建立版本基线";
  1794	      noteElement.textContent = "当前输入区已经有 packet，但还没进入已保存版本历史；你可以先把它保存成草稿，再继续切换样例或重跑。";
  1795	      setPacketDraftActionState(false);
  1796	      return;
  1797	    }
  1798	    statusElement.textContent = "当前草稿：等待第一次载入";
  1799	    noteElement.textContent = "先载入一个 packet；之后直接改 JSON 但还没运行时，也可以先把当前版本存成草稿。";
  1800	    setPacketDraftActionState(true);
  1801	    return;
  1802	  }
  1803	
  1804	  const parsed = parseWorkbenchPacketEditor();
  1805	  if (parsed.error) {
  1806	    statusElement.textContent = "当前草稿：JSON 暂不可保存";
  1807	    noteElement.textContent = `当前输入区还不是合法 JSON，所以版本历史暂时无法收纳它：${parsed.error}`;
  1808	    setPacketDraftActionState(true);
  1809	    return;
  1810	  }
  1811	
  1812	  if (baselineEntry.signature === packetRevisionSignature(parsed.payload)) {
  1813	    statusElement.textContent = `当前草稿：已与「${baselineEntry.title}」同步`;
  1814	    noteElement.textContent = "如果接下来切换样例、恢复旧版本或应用浏览器写回，系统会先检查是否存在新的有效草稿。";
  1815	    setPacketDraftActionState(true);
  1816	    return;
  1817	  }
  1818	
  1819	  statusElement.textContent = `当前草稿：有未保存改动（相对「${baselineEntry.title}」）`;
  1820	  noteElement.textContent = "你可以先手动保存这份 Packet 草稿；如果现在切换样例、恢复旧版本或应用浏览器写回，系统也会先自动保存这份有效草稿，刷新页面后也会继续恢复当前工作区。";
  1821	  setPacketDraftActionState(false);
  1822	}
  1823	
  1824	function restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  1825	  sourceStatusMessage = "已从浏览器恢复上次 packet 工作区。",
  1826	  sourceStatusMessageWithHistory = "已从浏览器恢复上次 packet 工作区和结果历史。",
  1827	  packetSourceFallback = "当前样例：已恢复工作区快照。",
  1828	  preparationMessage = "已恢复工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  1829	  fingerprintSummary = "已恢复工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  1830	  successMessage = "已恢复工作区快照。",
  1831	} = {}) {
  1832	  if (!workspace || typeof workspace !== "object") {
  1833	    return false;
  1834	  }
  1835	
  1836	  const normalizedHistory = normalizeWorkbenchPacketRevisionHistory(workspace.packetRevisionHistory);
  1837	  const normalizedRunHistory = normalizeWorkbenchRunHistory(workspace.runHistory);
  1838	  const fallbackPacketJsonText = normalizedHistory.length
  1839	    ? prettyJson(normalizedHistory[0].payload)
  1840	    : prettyJson(bootstrapPayload.reference_packet);
  1841	  const packetJsonText = typeof workspace.packetJsonText === "string" && workspace.packetJsonText.trim()
  1842	    ? workspace.packetJsonText
  1843	    : fallbackPacketJsonText;
  1844	
  1845	  withWorkbenchPacketWorkspacePersistenceSuspended(() => {
  1846	    workbenchPacketRevisionHistory = normalizedHistory;
  1847	    workbenchPacketRevisionSequence = nextWorkbenchSequenceFromIds(
  1848	      normalizedHistory,
  1849	      "workbench-packet-revision-",
  1850	    );
  1851	    workbenchRunHistory = normalizedRunHistory;
  1852	    workbenchHistorySequence = nextWorkbenchSequenceFromIds(
  1853	      normalizedRunHistory,
  1854	      "workbench-history-",
  1855	    );
  1856	    selectedWorkbenchPacketRevisionId = normalizedHistory.some((entry) => entry.id === workspace.selectedWorkbenchPacketRevisionId)
  1857	      ? workspace.selectedWorkbenchPacketRevisionId
  1858	      : (normalizedHistory[0] ? normalizedHistory[0].id : "");
  1859	    selectedWorkbenchHistoryId = normalizedRunHistory.some((entry) => entry.id === workspace.selectedWorkbenchHistoryId)
  1860	      ? workspace.selectedWorkbenchHistoryId
  1861	      : (normalizedRunHistory[0] ? normalizedRunHistory[0].id : "");
  1862	    currentWorkbenchViewMode = typeof workspace.currentWorkbenchViewMode === "string" && workspace.currentWorkbenchViewMode
  1863	      ? workspace.currentWorkbenchViewMode
  1864	      : (normalizedRunHistory.length ? "latest" : "preparation");
  1865	    currentWorkbenchRunLabel = typeof workspace.currentWorkbenchRunLabel === "string" && workspace.currentWorkbenchRunLabel.trim()
  1866	      ? workspace.currentWorkbenchRunLabel
  1867	      : "手动生成";
  1868	    workbenchElement("workbench-packet-json").value = packetJsonText;
  1869	    setPacketSourceStatus(
  1870	      typeof workspace.packetSourceStatus === "string" && workspace.packetSourceStatus.trim()
  1871	        ? workspace.packetSourceStatus
  1872	        : packetSourceFallback
  1873	    );
  1874	    const fields = workspace.fields && typeof workspace.fields === "object" ? workspace.fields : {};
  1875	    workbenchPersistedFieldIds.forEach((id) => {
  1876	      applyWorkbenchPersistedFieldValue(id, fields[id]);
  1877	    });
  1878	    renderWorkbenchPacketRevisionHistory();
  1879	  });
  1880	
  1881	  const parsed = parseWorkbenchPacketEditor();
  1882	  if (parsed.payload) {
  1883	    renderSystemFingerprintFromPacketPayload(parsed.payload, {
  1884	      badgeState: "idle",
  1885	      badgeText: "画像已恢复",
  1886	      summary: fingerprintSummary,
  1887	    });
  1888	  } else {
  1889	    renderSystemFingerprint({
  1890	      badgeState: "blocked",
  1891	      badgeText: "画像待修正",
  1892	      summary: `${successMessage} 但当前 JSON 还没恢复成合法 packet：${parsed.error}`,
  1893	      documentFallback: "先修正 JSON，再显示来源文档。",
  1894	      signalFallback: "先修正 JSON，再显示关键信号。",
  1895	    });
  1896	  }
  1897	  if (!normalizedRunHistory.length) {
  1898	    renderPreparationBoard(preparationMessage);
  1899	  } else if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
  1900	    restoreWorkbenchHistoryEntry(selectedWorkbenchHistoryId);
  1901	  } else {
  1902	    restoreLatestWorkbenchHistory();
  1903	  }
  1904	  setActiveWorkbenchPreset("");
  1905	  persistWorkbenchPacketWorkspace();
  1906	  setRequestStatus(
  1907	    normalizedRunHistory.length
  1908	      ? sourceStatusMessageWithHistory
  1909	      : sourceStatusMessage,
  1910	    "success",
  1911	  );
  1912	  return true;
  1913	}
  1914	
  1915	function restoreWorkbenchPacketWorkspaceFromBrowser() {
  1916	  const workspace = loadPersistedWorkbenchPacketWorkspace();
  1917	  if (!workspace) {
  1918	    return false;
  1919	  }
  1920	  return restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  1921	    sourceStatusMessage: "已从浏览器恢复上次 packet 工作区。",
  1922	    sourceStatusMessageWithHistory: "已从浏览器恢复上次 packet 工作区和结果历史。",
  1923	    packetSourceFallback: "当前样例：已从浏览器恢复上次 packet 工作区。",
  1924	    preparationMessage: "已从浏览器恢复上次 packet 工作区；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  1925	    fingerprintSummary: "已从浏览器恢复上次 packet 工作区。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  1926	    successMessage: "已从浏览器恢复上次 packet 工作区。",
  1927	  });
  1928	}
  1929	
  1930	function summarizeWorkbenchPacketRevisionEntry(entry) {
  1931	  if (!entry) {
  1932	    return null;
  1933	  }
  1934	  const summary = summarizePacketPayload(entry.payload);
  1935	  return {
  1936	    systemId: entry.payload.system_id || "unknown_system",
  1937	    docs: `${summary.sourceDocuments} 份`,
  1938	    logic: `${summary.logicNodes} logic / ${summary.components} components`,
  1939	    scenarios: `${summary.scenarios} scenarios / ${summary.faultModes} faults`,
  1940	    answers: `${summary.clarificationAnswers} answers`,
  1941	  };
  1942	}
  1943	
  1944	function renderWorkbenchPacketRevisionCompareBar() {
  1945	  const compareBar = workbenchElement("workbench-packet-history-compare-bar");
  1946	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  1947	  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;
  1948	
  1949	  if (!latestEntry || !selectedEntry || selectedEntry.id === latestEntry.id) {
  1950	    compareBar.hidden = true;
  1951	    return;
  1952	  }
  1953	
  1954	  const replay = summarizeWorkbenchPacketRevisionEntry(selectedEntry);
  1955	  const latest = summarizeWorkbenchPacketRevisionEntry(latestEntry);
  1956	
  1957	  workbenchElement("workbench-packet-history-compare-summary").textContent =
  1958	    `你正在回看「${selectedEntry.title}」，下面这些卡会直接告诉你它和最新 packet 在输入骨架上差在哪里。`;
  1959	  renderValue("workbench-packet-history-compare-system", `回看：${replay.systemId}`);
  1960	  renderValue("workbench-packet-history-compare-system-detail", `最新：${latest.systemId}`);
  1961	  renderValue("workbench-packet-history-compare-docs", `回看：${replay.docs}`);
  1962	  renderValue("workbench-packet-history-compare-docs-detail", `最新：${latest.docs}`);
  1963	  renderValue("workbench-packet-history-compare-logic", `回看：${replay.logic}`);
  1964	  renderValue("workbench-packet-history-compare-logic-detail", `最新：${latest.logic}`);
  1965	  renderValue("workbench-packet-history-compare-scenarios", `回看：${replay.scenarios}`);
  1966	  renderValue("workbench-packet-history-compare-scenarios-detail", `最新：${latest.scenarios}`);
  1967	  renderValue("workbench-packet-history-compare-answers", `回看：${replay.answers}`);
  1968	  renderValue("workbench-packet-history-compare-answers-detail", `最新：${latest.answers}`);
  1969	  compareBar.hidden = false;
  1970	}
  1971	
  1972	function renderWorkbenchPacketRevisionHistory() {
  1973	  const container = workbenchElement("workbench-packet-history-cards");
  1974	  if (!workbenchPacketRevisionHistory.length) {
  1975	    container.replaceChildren((() => {
  1976	      const card = document.createElement("article");
  1977	      card.className = "workbench-history-card is-empty";
  1978	      const title = document.createElement("strong");
  1979	      title.textContent = "暂无版本";
  1980	      const detail = document.createElement("p");
  1981	      detail.textContent = "先载入 reference/template、本地 JSON，或在页面里写回一次 packet。";
  1982	      card.append(title, detail);
  1983	      return card;
  1984	    })());
  1985	    renderWorkbenchPacketHistoryViewBar();
  1986	    return;
  1987	  }
  1988	
  1989	  container.replaceChildren(...workbenchPacketRevisionHistory.map((entry) => {
  1990	    const card = document.createElement("button");
  1991	    const selected = entry.id === selectedWorkbenchPacketRevisionId;
  1992	    const summary = summarizePacketPayload(entry.payload);
  1993	    card.type = "button";
  1994	    card.className = "workbench-history-card";
  1995	    card.dataset.selected = selected ? "true" : "false";
  1996	    card.setAttribute("aria-pressed", selected ? "true" : "false");
  1997	    card.addEventListener("click", () => {
  1998	      restoreWorkbenchPacketRevisionEntry(entry.id);
  1999	    });
  2000	
  2001	    const meta = document.createElement("div");
  2002	    meta.className = "workbench-history-meta";
  2003	
  2004	    const systemChip = document.createElement("span");
  2005	    systemChip.className = "workbench-history-chip";
  2006	    systemChip.textContent = entry.payload.system_id || "unknown_system";
  2007	
  2008	    const coverageChip = document.createElement("span");
  2009	    coverageChip.className = "workbench-history-chip";
  2010	    coverageChip.textContent = `${summary.logicNodes}L / ${summary.scenarios}S / ${summary.faultModes}F`;
  2011	
  2012	    const timeChip = document.createElement("span");
  2013	    timeChip.className = "workbench-history-chip";
  2014	    timeChip.textContent = entry.timeLabel;
  2015	
  2016	    meta.append(systemChip, coverageChip, timeChip);
  2017	
  2018	    const title = document.createElement("strong");
  2019	    title.textContent = entry.title;
  2020	
  2021	    const summaryText = document.createElement("p");
  2022	    summaryText.textContent = entry.summary;
  2023	
  2024	    const detail = document.createElement("p");
  2025	    detail.textContent = entry.detail;
  2026	
  2027	    const action = document.createElement("span");
  2028	    action.className = "workbench-history-action";
  2029	    action.textContent = selected ? "当前输入区正在使用这个 Packet 版本" : "点此恢复这个 Packet 版本";
  2030	
  2031	    card.append(meta, title, summaryText, detail, action);
  2032	    return card;
  2033	  }));
  2034	  renderWorkbenchPacketHistoryViewBar();
  2035	}
  2036	
  2037	function pushWorkbenchPacketRevision(entry) {
  2038	  selectedWorkbenchPacketRevisionId = entry.id;
  2039	  workbenchPacketRevisionHistory = [entry, ...workbenchPacketRevisionHistory].slice(0, maxWorkbenchPacketRevisionHistory);
  2040	  renderWorkbenchPacketRevisionHistory();
  2041	  persistWorkbenchPacketWorkspace();
  2042	}
  2043	
  2044	function captureCurrentWorkbenchPacketDraft({
  2045	  title,
  2046	  summary,
  2047	  detail = null,
  2048	} = {}) {
  2049	  const parsed = parseWorkbenchPacketEditor();
  2050	  if (parsed.error) {
  2051	    renderWorkbenchPacketDraftState();
  2052	    return {
  2053	      error: parsed.error,
  2054	      changed: false,
  2055	      entry: null,
  2056	      payload: null,
  2057	    };
  2058	  }
  2059	
  2060	  const baselineEntry = selectedWorkbenchPacketRevisionEntry();
  2061	  const signature = packetRevisionSignature(parsed.payload);
  2062	  if (baselineEntry && baselineEntry.signature === signature) {
  2063	    renderWorkbenchPacketDraftState();
  2064	    return {
  2065	      error: null,
  2066	      changed: false,
  2067	      entry: baselineEntry,
  2068	      payload: parsed.payload,
  2069	    };
  2070	  }
  2071	
  2072	  const entry = buildWorkbenchPacketRevisionEntry(parsed.payload, {
  2073	    title: title || "手动保存 Packet 草稿",
  2074	    summary: summary || "当前 packet 草稿已保存到版本历史。",
  2075	    detail,
  2076	  });
  2077	  pushWorkbenchPacketRevision(entry);
  2078	  return {
  2079	    error: null,
  2080	    changed: true,
  2081	    entry,
  2082	    payload: parsed.payload,
  2083	  };
  2084	}
  2085	
  2086	function maybeAutoSnapshotCurrentPacketDraft(reason) {
  2087	  return captureCurrentWorkbenchPacketDraft({
  2088	    title: `自动保存草稿 / ${reason}`,
  2089	    summary: `在${reason}前自动收纳当前 packet 草稿。`,
  2090	  });
  2091	}
  2092	
  2093	function saveCurrentWorkbenchPacketDraft() {
  2094	  const result = captureCurrentWorkbenchPacketDraft({
  2095	    title: "手动保存 Packet 草稿",
  2096	    summary: "当前 packet 草稿已手动保存到版本历史。",
  2097	  });
  2098	  if (result.error) {
  2099	    setRequestStatus(`当前 Packet 草稿无法保存：${result.error}`, "error");
  2100	    return;
  2101	  }
  2102	  if (!result.changed) {
  2103	    setRequestStatus("当前 Packet 已和已保存版本同步，无需重复保存草稿。", "warning");
  2104	    return;
  2105	  }
  2106	  setRequestStatus("当前 Packet 草稿已保存到版本历史。", "success");
  2107	}
  2108	
  2109	function downloadWorkbenchWorkspaceSnapshot() {
  2110	  const snapshot = collectWorkbenchPacketWorkspaceState();
  2111	  try {
  2112	    const blob = new Blob([prettyJson(snapshot)], {type: "application/json"});
  2113	    const objectUrl = URL.createObjectURL(blob);
  2114	    const anchor = document.createElement("a");
  2115	    anchor.href = objectUrl;
  2116	    anchor.download = workspaceSnapshotDownloadName();
  2117	    anchor.click();
  2118	    URL.revokeObjectURL(objectUrl);
  2119	    setRequestStatus("当前工作区快照已导出。", "success");
  2120	  } catch (error) {
  2121	    setRequestStatus(`导出工作区快照失败：${String(error.message || error)}`, "error");
  2122	  }
  2123	}
  2124	
  2125	async function importWorkbenchWorkspaceSnapshot(file) {
  2126	  if (!file) {
  2127	    return;
  2128	  }
  2129	  try {
  2130	    const rawText = await file.text();
  2131	    const workspace = JSON.parse(rawText);
  2132	    if (!workspace || typeof workspace !== "object") {
  2133	      throw new Error("快照不是有效对象。");
  2134	    }
  2135	    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
  2136	      throw new Error(`不支持的快照类型：${workspace.kind}`);
  2137	    }
  2138	    if (!restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  2139	      sourceStatusMessage: "已导入工作区快照。",
  2140	      sourceStatusMessageWithHistory: "已导入工作区快照和结果历史。",
  2141	      packetSourceFallback: `当前样例：已导入工作区快照 / ${file.name}。`,
  2142	      preparationMessage: "已导入工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  2143	      fingerprintSummary: "已导入工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  2144	      successMessage: "已导入工作区快照。",
  2145	    })) {
  2146	      throw new Error("快照内容不完整，无法恢复工作区。");
  2147	    }
  2148	  } catch (error) {
  2149	    setRequestStatus(`导入工作区快照失败：${String(error.message || error)}`, "error");
  2150	  }
  2151	}
  2152	
  2153	function archivePayloadFromRestoreResponse(payload) {
  2154	  const resolvedFiles = payload && typeof payload.resolved_files === "object" ? payload.resolved_files : {};
  2155	  return {
  2156	    archive_dir: payload.archive_dir || "",
  2157	    manifest_json_path: payload.manifest_path || "",
  2158	    bundle_json_path: resolvedFiles.bundle_json || null,
  2159	    summary_markdown_path: resolvedFiles.summary_markdown || null,
  2160	    intake_assessment_json_path: resolvedFiles.intake_assessment_json || null,
  2161	    clarification_brief_json_path: resolvedFiles.clarification_brief_json || null,
  2162	    playback_report_json_path: resolvedFiles.playback_report_json || null,
  2163	    fault_diagnosis_report_json_path: resolvedFiles.fault_diagnosis_report_json || null,
  2164	    knowledge_artifact_json_path: resolvedFiles.knowledge_artifact_json || null,
  2165	    workspace_handoff_json_path: resolvedFiles.workspace_handoff_json || null,
  2166	    workspace_snapshot_json_path: resolvedFiles.workspace_snapshot_json || null,
  2167	  };
  2168	}
  2169	
  2170	async function restoreWorkbenchArchiveFromManifest() {
  2171	  const requestId = beginWorkbenchRequest();
  2172	  const manifestPath = workbenchElement("workbench-archive-manifest-path").value.trim();
  2173	  if (!manifestPath) {
  2174	    setRequestStatus("请先填写 archive_manifest.json 或 archive 目录路径。", "warning");
  2175	    return;
  2176	  }
  2177	
  2178	  setActiveWorkbenchPreset("");
  2179	  setRequestStatus("正在从 archive 恢复工作区...", "neutral");
  2180	  try {
  2181	    const response = await fetch(workbenchArchiveRestorePath, {
  2182	      method: "POST",
  2183	      headers: {"Content-Type": "application/json"},
  2184	      body: JSON.stringify({manifest_path: manifestPath}),
  2185	    });
  2186	    const payload = await response.json();
  2187	    if (!isLatestWorkbenchRequest(requestId)) {
  2188	      return;
  2189	    }
  2190	    if (!response.ok) {
  2191	      throw new Error(payload.message || payload.error || "workbench archive restore request failed");
  2192	    }
  2193	
  2194	    workbenchElement("workbench-archive-manifest-path").value = payload.archive_dir || payload.manifest_path || manifestPath;
  2195	    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromRestorePayload(payload));
  2196	    const sourceMode = `当前来源：Archive 恢复 / ${shortPath(payload.manifest_path)}。`;
  2197	    if (payload.workspace_snapshot && restoreWorkbenchPacketWorkspaceSnapshot(payload.workspace_snapshot, {
  2198	      sourceStatusMessage: `已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
  2199	      sourceStatusMessageWithHistory: `已从 archive 恢复工作区和结果历史 / ${shortPath(payload.manifest_path)}。`,
  2200	      packetSourceFallback: `当前样例：已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
  2201	      preparationMessage: "已从 archive 恢复工作区；如需确认当前输入，可以先看 packet 历史、结果历史和交接摘要。",
  2202	      fingerprintSummary: "已从 archive 恢复工作区。你可以继续编辑、重跑 bundle，或直接沿用归档里的历史结果继续交接。",
  2203	      successMessage: "已从 archive 恢复工作区。",
  2204	    })) {
  2205	      try {
  2206	        const restoredPacketSpec = JSON.parse(payload.workspace_snapshot.packetJsonText || "{}");
  2207	        assignFrozenSpec(restoredPacketSpec, "archive-restore");
  2208	      } catch (_) {
  2209	        // Non-critical: frozen spec not updated if snapshot packet is unparseable
  2210	      }
  2211	      setResultMode(sourceMode);
  2212	      return;
  2213	    }
  2214	
  2215	    renderBundleResponse(
  2216	      {
  2217	        bundle: payload.bundle,
  2218	        archive: archivePayloadFromRestoreResponse(payload),
  2219	      },
  2220	      {
  2221	        sourceMode,
  2222	        requestStatusMessage: payload.workspace_snapshot
  2223	          ? "已从 archive 恢复 bundle，但工作区快照不完整；当前只恢复了结果摘要。"
  2224	          : "已从 archive 恢复 bundle 结果。",
  2225	        requestStatusTone: payload.workspace_snapshot ? "warning" : "success",
  2226	      },
  2227	    );
  2228	  } catch (error) {
  2229	    if (!isLatestWorkbenchRequest(requestId)) {
  2230	      return;
  2231	    }
  2232	    setRequestStatus(`从 archive 恢复工作区失败：${String(error.message || error)}`, "error");
  2233	  }
  2234	}
  2235	
  2236	function maybeCaptureCurrentPacketRevision({
  2237	  title,
  2238	  summary,
  2239	  detail = null,
  2240	} = {}) {
  2241	  let payload;
  2242	  try {
  2243	    payload = JSON.parse(workbenchElement("workbench-packet-json").value);
  2244	  } catch (error) {
  2245	    return null;
  2246	  }
  2247	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  2248	  const signature = packetRevisionSignature(payload);
  2249	  if (latestEntry && latestEntry.signature === signature) {
  2250	    return latestEntry;
  2251	  }
  2252	  const entry = buildWorkbenchPacketRevisionEntry(payload, {
  2253	    title,
  2254	    summary,
  2255	    detail,
  2256	  });
  2257	  pushWorkbenchPacketRevision(entry);
  2258	  return entry;
  2259	}
  2260	
  2261	function restoreWorkbenchPacketRevisionEntry(entryId) {
  2262	  const entry = workbenchPacketRevisionHistory.find((item) => item.id === entryId);
  2263	  if (!entry) {
  2264	    return;
  2265	  }
  2266	  maybeAutoSnapshotCurrentPacketDraft(`恢复 ${entry.title}`);
  2267	  selectedWorkbenchPacketRevisionId = entry.id;
  2268	  renderWorkbenchPacketRevisionHistory();
  2269	  setActiveWorkbenchPreset("");
  2270	  setPacketEditor(entry.payload);
  2271	  setPacketSourceStatus(`当前 packet：已恢复 ${entry.title} / ${entry.timeLabel}。建议重新运行 bundle 验证这个版本。`);
  2272	  renderPreparationBoard(`已恢复 packet 版本「${entry.title}」。重新运行后，主看板会按这个版本显示最新结果。`);
  2273	  renderSystemFingerprintFromPacketPayload(entry.payload, {
  2274	    badgeState: "idle",
  2275	    badgeText: "画像已恢复",
  2276	    summary: "你正在回看一个历史 packet 版本；如果这个版本更合适，可以直接在此基础上继续修和重跑。",
  2277	  });
  2278	  renderWorkbenchPacketRevisionHistory();
  2279	  setRequestStatus(`已恢复 packet 版本：${entry.title}`, "success");
  2280	}
  2281	
  2282	function restoreLatestWorkbenchPacketRevision() {
  2283	  const latestEntry = latestWorkbenchPacketRevisionEntry();
  2284	  if (!latestEntry) {
  2285	    return;
  2286	  }
  2287	  restoreWorkbenchPacketRevisionEntry(latestEntry.id);
  2288	}
  2289	
  2290	function setWorkbenchViewState(mode, historyId = "") {
  2291	  currentWorkbenchViewMode = mode;
  2292	  selectedWorkbenchHistoryId = historyId;
  2293	  persistWorkbenchPacketWorkspace();
  2294	}
  2295	
  2296	function latestWorkbenchHistoryEntry() {
  2297	  return workbenchRunHistory.length ? workbenchRunHistory[0] : null;
  2298	}
  2299	
  2300	function summarizeWorkbenchHistoryEntry(entry) {
  2301	  const bundle = entry && entry.payload ? entry.payload.bundle || {} : {};
  2302	  return {
  2303	    verdict: entry ? entry.stateLabel : "-",
  2304	    scenario: bundle.selected_scenario_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
  2305	    faultMode: bundle.selected_fault_mode_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
  2306	    archive: entry && entry.archived ? "已留档" : "未留档",
  2307	  };
  2308	}
  2309	
  2310	function detailedWorkbenchHistoryEntry(entry) {
  2311	  if (!entry) {
  2312	    return null;
  2313	  }
  2314	  if (!entry.payload) {
  2315	    return {
  2316	      title: `${entry.title} / ${entry.timeLabel}`,
  2317	      verdict: "失败",
  2318	      blocker: entry.detail || "请求未完成",
  2319	      scenario: "请求失败",
  2320	      faultMode: "请求失败",
  2321	      knowledge: "未生成",
  2322	      archive: "未留档",
  2323	    };
  2324	  }
  2325	
  2326	  const bundle = entry.payload.bundle || {};
  2327	  const clarification = bundle.clarification_brief || {};
  2328	  const knowledge = bundle.knowledge_artifact || {};
  2329	  const archive = entry.payload.archive || null;
  2330	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  2331	    ? bundle.intake_assessment.blocking_reasons
  2332	    : [];
  2333	  const ready = Boolean(bundle.ready_for_spec_build);
  2334	
  2335	  return {
  2336	    title: `${entry.title} / ${entry.timeLabel}`,
  2337	    verdict: ready ? "通过" : "阻塞",
  2338	    blocker: ready
  2339	      ? "当前无阻塞"
  2340	      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 仍未 ready。"),
  2341	    scenario: bundle.selected_scenario_id || "(none)",
  2342	    faultMode: bundle.selected_fault_mode_id || "(none)",
  2343	    knowledge: ready ? (knowledge.status || "已生成") : "尚未形成",
  2344	    archive: archive ? `已留档 / ${shortPath(archive.archive_dir)}` : "未留档",
  2345	  };
  2346	}
  2347	
  2348	function workbenchHistoryDetailFields(snapshot, compareSnapshot) {
  2349	  const compare = compareSnapshot || {};
  2350	  return [
  2351	    {label: "结论", value: snapshot.verdict, diff: snapshot.verdict === compare.verdict ? "same" : "changed"},
  2352	    {label: "当前卡点", value: snapshot.blocker, diff: snapshot.blocker === compare.blocker ? "same" : "changed"},
  2353	    {label: "Scenario", value: snapshot.scenario, diff: snapshot.scenario === compare.scenario ? "same" : "changed"},
  2354	    {label: "Fault Mode", value: snapshot.faultMode, diff: snapshot.faultMode === compare.faultMode ? "same" : "changed"},
  2355	    {label: "知识沉淀", value: snapshot.knowledge, diff: snapshot.knowledge === compare.knowledge ? "same" : "changed"},
  2356	    {label: "归档状态", value: snapshot.archive, diff: snapshot.archive === compare.archive ? "same" : "changed"},
  2357	  ];
  2358	}
  2359	
  2360	function renderWorkbenchHistoryDetailCard({
  2361	  titleElementId,
  2362	  bodyElementId,
  2363	  snapshot,
  2364	  compareSnapshot,
  2365	}) {
  2366	  workbenchElement(titleElementId).textContent = snapshot.title;
  2367	  const body = workbenchElement(bodyElementId);
  2368	  body.replaceChildren(...workbenchHistoryDetailFields(snapshot, compareSnapshot).map((field) => {
  2369	    const row = document.createElement("div");
  2370	    row.className = "workbench-history-detail-row";
  2371	
  2372	    const label = document.createElement("span");
  2373	    label.className = "workbench-history-detail-label";
  2374	    label.textContent = field.label;
  2375	
  2376	    const value = document.createElement("strong");
  2377	    value.className = "workbench-history-detail-value";
  2378	    value.dataset.diff = field.diff;
  2379	    value.textContent = field.value;
  2380	
  2381	    row.append(label, value);
  2382	    return row;
  2383	  }));
  2384	}
  2385	
  2386	function renderWorkbenchHistoryCompareBar() {
  2387	  const compareBar = workbenchElement("workbench-history-compare-bar");
  2388	  const latestEntry = latestWorkbenchHistoryEntry();
  2389	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2390	
  2391	  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry) {
  2392	    compareBar.hidden = true;
  2393	    return;
  2394	  }
  2395	
  2396	  const replay = summarizeWorkbenchHistoryEntry(selectedEntry);
  2397	  const latest = summarizeWorkbenchHistoryEntry(latestEntry);
  2398	
  2399	  workbenchElement("workbench-history-compare-summary").textContent =
  2400	    `你正在回看「${selectedEntry.title}」，下面这 4 项会直接告诉你它和最新结果差在哪里。`;
  2401	  renderValue("workbench-history-compare-verdict", `回看：${replay.verdict}`);
  2402	  renderValue("workbench-history-compare-verdict-detail", `最新：${latest.verdict}`);
  2403	  renderValue("workbench-history-compare-scenario", `回看：${replay.scenario}`);
  2404	  renderValue("workbench-history-compare-scenario-detail", `最新：${latest.scenario}`);
  2405	  renderValue("workbench-history-compare-fault", `回看：${replay.faultMode}`);
  2406	  renderValue("workbench-history-compare-fault-detail", `最新：${latest.faultMode}`);
  2407	  renderValue("workbench-history-compare-archive", `回看：${replay.archive}`);
  2408	  renderValue("workbench-history-compare-archive-detail", `最新：${latest.archive}`);
  2409	  compareBar.hidden = false;
  2410	}
  2411	
  2412	function renderWorkbenchHistoryDetailBoard() {
  2413	  const detailBoard = workbenchElement("workbench-history-detail-board");
  2414	  const latestEntry = latestWorkbenchHistoryEntry();
  2415	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2416	
  2417	  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry || latestEntry.id === selectedEntry.id) {
  2418	    detailBoard.hidden = true;
  2419	    return;
  2420	  }
  2421	
  2422	  const replaySnapshot = detailedWorkbenchHistoryEntry(selectedEntry);
  2423	  const latestSnapshot = detailedWorkbenchHistoryEntry(latestEntry);
  2424	  renderWorkbenchHistoryDetailCard({
  2425	    titleElementId: "workbench-history-detail-replay-title",
  2426	    bodyElementId: "workbench-history-detail-replay",
  2427	    snapshot: replaySnapshot,
  2428	    compareSnapshot: latestSnapshot,
  2429	  });
  2430	  renderWorkbenchHistoryDetailCard({
  2431	    titleElementId: "workbench-history-detail-latest-title",
  2432	    bodyElementId: "workbench-history-detail-latest",
  2433	    snapshot: latestSnapshot,
  2434	    compareSnapshot: replaySnapshot,
  2435	  });
  2436	  detailBoard.hidden = false;
  2437	}
  2438	
  2439	function renderWorkbenchHistoryViewBar() {
  2440	  const latestEntry = latestWorkbenchHistoryEntry();
  2441	  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  2442	  const statusElement = workbenchElement("workbench-history-view-status");
  2443	  const returnButton = workbenchElement("workbench-history-return-latest");
  2444	
  2445	  if (currentWorkbenchViewMode === "running") {
  2446	    statusElement.textContent = "当前查看：正在生成新结果";
  2447	    returnButton.disabled = true;
  2448	    renderWorkbenchHistoryCompareBar();
  2449	    renderWorkbenchHistoryDetailBoard();
  2450	    return;
  2451	  }
  2452	
  2453	  if (currentWorkbenchViewMode === "preparation") {
  2454	    statusElement.textContent = "当前查看：样例准备中";
  2455	    returnButton.disabled = true;
  2456	    renderWorkbenchHistoryCompareBar();
  2457	    renderWorkbenchHistoryDetailBoard();
  2458	    return;
  2459	  }
  2460	
  2461	  if (!latestEntry) {
  2462	    statusElement.textContent = "当前查看：等待第一次结果";
  2463	    returnButton.disabled = true;
  2464	    renderWorkbenchHistoryCompareBar();
  2465	    renderWorkbenchHistoryDetailBoard();
  2466	    return;
  2467	  }
  2468	
  2469	  if (currentWorkbenchViewMode !== "history" || !selectedEntry || selectedEntry.id === latestEntry.id) {
  2470	    statusElement.textContent = `当前查看：最新结果 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
  2471	    returnButton.disabled = true;
  2472	    renderWorkbenchHistoryCompareBar();
  2473	    renderWorkbenchHistoryDetailBoard();
  2474	    return;
  2475	  }
  2476	
  2477	  statusElement.textContent = `当前查看：历史回看 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  2478	  returnButton.disabled = false;
  2479	  renderWorkbenchHistoryCompareBar();
  2480	  renderWorkbenchHistoryDetailBoard();
  2481	}
  2482	
  2483	function renderWorkbenchRunHistory() {
  2484	  const container = workbenchElement("workbench-history-cards");
  2485	  if (!workbenchRunHistory.length) {
  2486	    container.replaceChildren((() => {
  2487	      const card = document.createElement("article");
  2488	      card.className = "workbench-history-card is-empty";
  2489	      const title = document.createElement("strong");
  2490	      title.textContent = "暂无结果";
  2491	      const detail = document.createElement("p");
  2492	      detail.textContent = "先点一个一键预设或手动生成一次 bundle。";
  2493	      card.append(title, detail);
  2494	      return card;
  2495	    })());
  2496	    renderWorkbenchHistoryViewBar();
  2497	    return;
  2498	  }
  2499	
  2500	  container.replaceChildren(...workbenchRunHistory.map((entry) => {
  2501	    const card = document.createElement("button");
  2502	    const selected = entry.id === selectedWorkbenchHistoryId;
  2503	    card.type = "button";
  2504	    card.className = "workbench-history-card";
  2505	    card.dataset.selected = selected ? "true" : "false";
  2506	    card.setAttribute("aria-pressed", selected ? "true" : "false");
  2507	    card.addEventListener("click", () => {
  2508	      restoreWorkbenchHistoryEntry(entry.id);
  2509	    });
  2510	
  2511	    const meta = document.createElement("div");
  2512	    meta.className = "workbench-history-meta";
  2513	
  2514	    const stateChip = document.createElement("span");
  2515	    stateChip.className = "workbench-history-chip";
  2516	    stateChip.dataset.state = entry.state;
  2517	    stateChip.textContent = entry.stateLabel;
  2518	
  2519	    const archiveChip = document.createElement("span");
  2520	    archiveChip.className = "workbench-history-chip";
  2521	    archiveChip.dataset.state = entry.archived ? "archived" : entry.state;
  2522	    archiveChip.textContent = entry.archived ? "已留档" : "未留档";
  2523	
  2524	    const timeChip = document.createElement("span");
  2525	    timeChip.className = "workbench-history-chip";
  2526	    timeChip.textContent = entry.timeLabel;
  2527	
  2528	    meta.append(stateChip, archiveChip, timeChip);
  2529	
  2530	    const title = document.createElement("strong");
  2531	    title.textContent = entry.title;
  2532	
  2533	    const summary = document.createElement("p");
  2534	    summary.textContent = entry.summary;
  2535	
  2536	    const detail = document.createElement("p");
  2537	    detail.textContent = entry.detail;
  2538	
  2539	    const action = document.createElement("span");
  2540	    action.className = "workbench-history-action";
  2541	    action.textContent = selected ? "当前主看板正在显示这次结果" : "点此回看这次结果";
  2542	
  2543	    card.append(meta, title, summary, detail, action);
  2544	    return card;
  2545	  }));
  2546	  renderWorkbenchHistoryViewBar();
  2547	}
  2548	
  2549	function historyTimeLabel() {
  2550	  return new Date().toLocaleTimeString("zh-CN", {
  2551	    hour: "2-digit",
  2552	    minute: "2-digit",
  2553	    second: "2-digit",
  2554	    hour12: false,
  2555	  });
  2556	}
  2557	
  2558	function buildWorkbenchHistoryEntryFromPayload(payload) {
  2559	  const bundle = payload.bundle || {};
  2560	  const clarification = bundle.clarification_brief || {};
  2561	  const archive = payload.archive || null;
  2562	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  2563	    ? bundle.intake_assessment.blocking_reasons
  2564	    : [];
  2565	  const ready = Boolean(bundle.ready_for_spec_build);
  2566	  return {
  2567	    id: nextWorkbenchHistoryId(),
  2568	    state: ready ? "ready" : "blocked",
  2569	    stateLabel: ready ? "通过" : "阻塞",
  2570	    archived: Boolean(archive),
  2571	    timeLabel: historyTimeLabel(),
  2572	    title: currentWorkbenchRunLabel,
  2573	    payload: cloneJson(payload),
  2574	    summary: ready
  2575	      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
  2576	      : `停在 ${clarification.gate_status || "clarification"}，等待补齐信息`,
  2577	    detail: ready
  2578	      ? (archive ? `archive：${shortPath(archive.archive_dir)}` : "本次未生成 archive。")
  2579	      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 尚未 ready。"),
  2580	  };
  2581	}
  2582	
  2583	function buildWorkbenchHistoryEntryFromFailure(message) {
  2584	  return {
  2585	    id: nextWorkbenchHistoryId(),
  2586	    state: "failure",
  2587	    stateLabel: "失败",
  2588	    archived: false,
  2589	    timeLabel: historyTimeLabel(),
  2590	    title: currentWorkbenchRunLabel,
  2591	    errorMessage: String(message),
  2592	    summary: "请求未完成",
  2593	    detail: message,
  2594	  };
  2595	}
  2596	
  2597	function workbenchHistoryTone(state) {
  2598	  if (state === "ready") {
  2599	    return "success";
  2600	  }
  2601	  if (state === "blocked") {
  2602	    return "warning";
  2603	  }
  2604	  return "error";
  2605	}
  2606	
  2607	function renderFailureResponse(message, {
  2608	  pushHistory = true,
  2609	  sourceMode = "当前来源：workbench bundle 请求失败。",
  2610	  requestStatusMessage = `生成失败：${String(message)}`,
  2611	  requestStatusTone = "error",
  2612	} = {}) {
  2613	  const normalizedMessage = String(message);
  2614	  setResultMode(sourceMode);
  2615	  workbenchElement("bundle-json-output").textContent = prettyJson({
  2616	    error: "workbench_bundle_failed",
  2617	    message: normalizedMessage,
  2618	  });
  2619	  renderExplainRuntime({});
  2620	  renderFailureBoard(normalizedMessage);
  2621	  if (pushHistory) {
  2622	    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromFailure(normalizedMessage));
  2623	  }
  2624	  setRequestStatus(requestStatusMessage, requestStatusTone);
  2625	}
  2626	
  2627	function restoreWorkbenchHistoryEntry(entryId) {
  2628	  const entry = workbenchRunHistory.find((item) => item.id === entryId);
  2629	  if (!entry) {
  2630	    return;
  2631	  }
  2632	  setWorkbenchViewState("history", entry.id);
  2633	  renderWorkbenchRunHistory();
  2634	  setActiveWorkbenchPreset("");
  2635	  if (entry.payload) {
  2636	    renderBundleResponse(entry.payload, {
  2637	      pushHistory: false,
  2638	      sourceMode: "当前来源：最近验收结果回看。",
  2639	      requestStatusMessage: `已回看：${entry.title}`,
  2640	      requestStatusTone: workbenchHistoryTone(entry.state),
  2641	    });
  2642	    return;
  2643	  }
  2644	  renderFailureResponse(entry.errorMessage || entry.detail, {
  2645	    pushHistory: false,
  2646	    sourceMode: "当前来源：最近验收结果回看。",
  2647	    requestStatusMessage: `已回看：${entry.title}`,
  2648	    requestStatusTone: workbenchHistoryTone(entry.state),
  2649	  });
  2650	}
  2651	
  2652	function restoreLatestWorkbenchHistory() {
  2653	  const latestEntry = latestWorkbenchHistoryEntry();
  2654	  if (!latestEntry) {
  2655	    return;
  2656	  }
  2657	  setWorkbenchViewState("latest", latestEntry.id);
  2658	  renderWorkbenchRunHistory();
  2659	  setActiveWorkbenchPreset("");
  2660	  if (latestEntry.payload) {
  2661	    renderBundleResponse(latestEntry.payload, {
  2662	      pushHistory: false,
  2663	      sourceMode: "当前来源：最新结果回看。",
  2664	      requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
  2665	      requestStatusTone: workbenchHistoryTone(latestEntry.state),
  2666	    });
  2667	    return;
  2668	  }
  2669	  renderFailureResponse(latestEntry.errorMessage || latestEntry.detail, {
  2670	    pushHistory: false,
  2671	    sourceMode: "当前来源：最新结果回看。",
  2672	    requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
  2673	    requestStatusTone: workbenchHistoryTone(latestEntry.state),
  2674	  });
  2675	}
  2676	
  2677	function renderRunningBoard(message) {
  2678	  setWorkbenchViewState("running");
  2679	  setVisualBadge("idle", "正在生成");
  2680	  renderOnboardingReadiness({
  2681	    badgeState: "idle",
  2682	    badgeText: "正在评估",
  2683	    summary: "系统正在检查这份 packet 能不能作为第二套控制逻辑的可靠起点。",
  2684	    gaps: "评估中",
  2685	  });
  2686	  renderValue("workbench-spotlight-verdict", "正在处理中");
  2687	  renderValue("workbench-spotlight-verdict-detail", message);
  2688	  renderValue("workbench-spotlight-blocker", "正在判定");
  2689	  renderValue("workbench-spotlight-blocker-detail", "系统正在检查当前 packet 是通过还是阻塞。");
  2690	  renderValue("workbench-spotlight-knowledge", "处理中");
  2691	  renderValue("workbench-spotlight-knowledge-detail", "如果 bundle ready，knowledge 结果会在本轮生成。");
  2692	  renderValue("workbench-spotlight-archive", "处理中");
  2693	  renderValue("workbench-spotlight-archive-detail", "如果本轮勾选 archive，系统会在生成后汇报落档结果。");
  2694	  renderOnboardingActions({
  2695	    badgeState: "idle",
  2696	    badgeText: "动作解析中",
  2697	    summary: "系统正在按真实 clarification / schema 结果生成动作板，不会在前端自己猜步骤。",
  2698	  });
  2699	  renderSchemaRepairWorkspace({
  2700	    badgeState: "idle",
  2701	    badgeText: "修复解析中",
  2702	    summary: "系统正在检查这次 blocked bundle 里有没有被后端判定为 safe autofix 的 schema 修复项。",
  2703	    fallbackTitle: "正在解析",
  2704	    fallbackText: "请稍等，系统正在决定这次 run 有没有可直接应用的安全 schema 修复。",
  2705	    note: "工作台只会接受后端明确给出的 repair suggestion。",
  2706	    actionsDisabled: true,
  2707	  });
  2708	  renderClarificationWorkspace({
  2709	    badgeState: "idle",
  2710	    badgeText: "回填解析中",
  2711	    summary: "系统正在读取真实 clarification gate 结果；只有后端确认的待答问题才会被放进这个回填工作台。",
  2712	    fallbackTitle: "正在解析",
  2713	    fallbackText: "请稍等，系统正在决定这次 run 有没有需要直接回填的 clarification。",
  2714	    note: "当前不会在前端凭空生成问题，只复用 bundle 真实返回的 follow_up_items。",
  2715	    actionsDisabled: true,
  2716	  });
  2717	  renderValue("workbench-visual-summary", "系统正在跑当前 bundle。以最后一次点击为准，旧响应不会覆盖新结果。");
  2718	  setStageState("intake", "pending", "正在读取当前 packet。");
  2719	  setStageState("clarification", "pending", "正在检查 clarification gate。");
  2720	  setStageState("playback", "idle", "等待前序结果。");
  2721	  setStageState("diagnosis", "idle", "等待前序结果。");
  2722	  setStageState("knowledge", "idle", "等待前序结果。");
  2723	  setStageState("archive", "idle", "等待前序结果。");
  2724	  renderWorkbenchHistoryViewBar();
  2725	}
  2726	
  2727	function renderFailureBoard(message) {
  2728	  setVisualBadge("blocked", "请求失败");
  2729	  renderOnboardingReadiness({
  2730	    badgeState: "blocked",
  2731	    badgeText: "请求失败",
  2732	    summary: "这次不是 packet 本身通过或阻塞，而是请求失败了，所以还不能判断第二套系统接入准备度。",
  2733	    gaps: "先修正请求",
  2734	  });
  2735	  renderValue("workbench-spotlight-verdict", "需要修正输入");
  2736	  renderValue("workbench-spotlight-verdict-detail", message);
  2737	  renderValue("workbench-spotlight-blocker", "请求未完成");
  2738	  renderValue("workbench-spotlight-blocker-detail", "先修正输入或请求错误，再重新运行。");
  2739	  renderValue("workbench-spotlight-knowledge", "未生成");
  2740	  renderValue("workbench-spotlight-knowledge-detail", "因为请求失败，所以没有下游结果。");
  2741	  renderValue("workbench-spotlight-archive", "未生成");
  2742	  renderValue("workbench-spotlight-archive-detail", "本次没有产生 archive package。");
  2743	  renderOnboardingActions({
  2744	    badgeState: "blocked",
  2745	    badgeText: "动作未生成",
  2746	    summary: `这次不是 clarification 阻塞，而是请求本身失败了，所以动作板也还不能可靠生成：${message}`,
  2747	    followUpFallback: "先修正请求，再显示澄清动作。",
  2748	    blockerFallback: "先修正请求，再显示结构 blocker。",
  2749	    unlockFallback: "先修正请求，再显示解锁项。",
  2750	  });
  2751	  renderSchemaRepairWorkspace({
  2752	    badgeState: "blocked",
  2753	    badgeText: "暂不可修复",
  2754	    summary: "这次请求没有成功，所以还不能可靠判断哪些 schema blocker 适合安全 autofix。",
  2755	    fallbackTitle: "先修正请求",
  2756	    fallbackText: "等请求恢复成功后，这里才会出现真实 schema repair suggestion。",
  2757	    note: "当前错误优先级高于 schema repair；先把请求恢复正常。",
  2758	    actionsDisabled: true,
  2759	  });
  2760	  renderClarificationWorkspace({
  2761	    badgeState: "blocked",
  2762	    badgeText: "暂不可回填",
  2763	    summary: "这次请求没有成功，所以工作台现在也不能可靠判断应该让你回答哪些 clarification。",
  2764	    fallbackTitle: "先修正请求",
  2765	    fallbackText: "等请求恢复成功后，这里才会出现真实的 clarification 回填项。",
  2766	    note: "当前错误优先级高于 clarification 回填；先把 JSON 或请求本身修好。",
  2767	    actionsDisabled: true,
  2768	  });
  2769	  renderValue("workbench-visual-summary", "这次不是 bundle 阻塞，而是请求本身没有成功。先修正输入，再重新点击“生成 Bundle”。");
  2770	  setStageState("intake", "blocked", "输入或请求存在问题。");
  2771	  setStageState("clarification", "idle", "等待请求恢复。");
  2772	  setStageState("playback", "idle", "等待请求恢复。");
  2773	  setStageState("diagnosis", "idle", "等待请求恢复。");
  2774	  setStageState("knowledge", "idle", "等待请求恢复。");
  2775	  setStageState("archive", "idle", "等待请求恢复。");
  2776	}
  2777	
  2778	function applyReferencePacketSelection({
  2779	  archiveBundle,
  2780	  sourceStatus,
  2781	  preparationMessage,
  2782	}) {
  2783	  if (!bootstrapPayload) {
  2784	    return false;
  2785	  }
  2786	  maybeAutoSnapshotCurrentPacketDraft("载入参考样例");
  2787	  setPacketEditor(bootstrapPayload.reference_packet);
  2788	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.reference_packet, {
  2789	    title: "载入参考样例",
  2790	    summary: "reference packet 已重新载入。",
  2791	  }));
  2792	  fillReferenceResolutionDefaults();
  2793	  workbenchElement("workbench-scenario-id").value = "";
  2794	  workbenchElement("workbench-fault-mode-id").value = "";
  2795	  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  2796	  setPacketSourceStatus(sourceStatus);
  2797	  renderPreparationBoard(preparationMessage);
  2798	  renderSystemFingerprintFromPacketPayload(bootstrapPayload.reference_packet, {
  2799	    badgeState: "idle",
  2800	    badgeText: "画像已载入",
  2801	    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  2802	  });
  2803	  return true;
  2804	}
  2805	
  2806	function applyTemplatePacketSelection({
  2807	  archiveBundle,
  2808	  sourceStatus,
  2809	  preparationMessage,
  2810	}) {
  2811	  if (!bootstrapPayload) {
  2812	    return false;
  2813	  }
  2814	  maybeAutoSnapshotCurrentPacketDraft("载入空白模板");
  2815	  setPacketEditor(bootstrapPayload.template_packet);
  2816	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.template_packet, {
  2817	    title: "载入空白模板",
  2818	    summary: "template packet 已载入，适合演示 blocked onboarding。",
  2819	  }));
  2820	  clearResolutionDefaults();
  2821	  workbenchElement("workbench-scenario-id").value = "";
  2822	  workbenchElement("workbench-fault-mode-id").value = "";
  2823	  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  2824	  setPacketSourceStatus(sourceStatus);
  2825	  renderPreparationBoard(preparationMessage);
  2826	  renderSystemFingerprintFromPacketPayload(bootstrapPayload.template_packet, {
  2827	    badgeState: "blocked",
  2828	    badgeText: "画像待补齐",
  2829	    summary: "空白模板已经装载。虽然它还没 ready，但你已经可以先确认它的文档方向、控制目标和关键信号占位是不是对的。",
  2830	  });
  2831	  return true;
  2832	}
  2833	
  2834	function runWorkbenchPreset(presetId) {
  2835	  const preset = workbenchPresets[presetId];
  2836	  if (!preset) {
  2837	    return;
  2838	  }
  2839	  if (!bootstrapPayload) {
  2840	    setRequestStatus("bootstrap 尚未加载完成，请稍后再点预设。", "warning");
  2841	    return;
  2842	  }
  2843	  const applied = preset.source === "template"
  2844	    ? applyTemplatePacketSelection(preset)
  2845	    : applyReferencePacketSelection(preset);
  2846	  if (!applied) {
  2847	    setRequestStatus("当前样例还没准备好，请稍后再试。", "warning");
  2848	    return;
  2849	  }
  2850	  setActiveWorkbenchPreset(presetId);
  2851	  setRequestStatus(`${preset.label}：正在自动生成结果...`, "neutral");
  2852	  void runWorkbenchBundle();
  2853	}
  2854	
  2855	function fillReferenceResolutionDefaults() {
  2856	  workbenchElement("workbench-root-cause").value = defaultReferenceResolution.rootCause;
  2857	  workbenchElement("workbench-repair-action").value = defaultReferenceResolution.repairAction;
  2858	  workbenchElement("workbench-validation-after-fix").value = defaultReferenceResolution.validationAfterFix;
  2859	  workbenchElement("workbench-residual-risk").value = defaultReferenceResolution.residualRisk;
  2860	  workbenchElement("workbench-logic-change").value = defaultReferenceResolution.logicChange;
  2861	  workbenchElement("workbench-reliability-gain").value = defaultReferenceResolution.reliabilityGain;
  2862	  workbenchElement("workbench-guardrail-note").value = defaultReferenceResolution.guardrailNote;
  2863	  workbenchElement("workbench-evidence-links").value = "";
  2864	  workbenchElement("workbench-observed-symptoms").value = "";
  2865	}
  2866	
  2867	function clearResolutionDefaults() {
  2868	  [
  2869	    "workbench-root-cause",
  2870	    "workbench-repair-action",
  2871	    "workbench-validation-after-fix",
  2872	    "workbench-residual-risk",
  2873	    "workbench-logic-change",
  2874	    "workbench-reliability-gain",
  2875	    "workbench-guardrail-note",
  2876	    "workbench-evidence-links",
  2877	    "workbench-observed-symptoms",
  2878	  ].forEach((id) => {
  2879	    workbenchElement(id).value = "";
  2880	  });
  2881	}
  2882	
  2883	function renderBulletList(containerId, items, fallbackText) {
  2884	  const container = workbenchElement(containerId);
  2885	  const effectiveItems = Array.isArray(items) && items.length ? items : [fallbackText];
  2886	  container.replaceChildren(
  2887	    ...effectiveItems.map((item) => {
  2888	      const li = document.createElement("li");
  2889	      li.textContent = String(item);
  2890	      return li;
  2891	    }),
  2892	  );
  2893	}
  2894	
  2895	function readExplainRuntimePayload(payload) {
  2896	  const runtime = payload
  2897	    && typeof payload === "object"
  2898	    && payload.explain_runtime
  2899	    && typeof payload.explain_runtime === "object"
  2900	    && !Array.isArray(payload.explain_runtime)
  2901	    ? payload.explain_runtime
  2902	    : null;
  2903	  if (!runtime) {
  2904	    return {
  2905	      reported: false,
  2906	      status: "",
  2907	      statusSource: "",
  2908	      backend: "",
  2909	      model: "",
  2910	      source: "",
  2911	      cachedAt: "",
  2912	      observedAt: "",
  2913	      cacheHits: null,
  2914	      expectedCount: null,
  2915	      backendMatch: null,
  2916	      requestedBackend: "",
  2917	      requestedModel: "",
  2918	      detail: "",
  2919	      boundaryNote: "",
  2920	    };
  2921	  }
  2922	  const toTrimmedString = (value) => (typeof value === "string" ? value.trim() : "");
  2923	  const toNonNegativeInt = (value) => {
  2924	    const parsed = Number(value);
  2925	    return Number.isFinite(parsed) && parsed >= 0 ? Math.floor(parsed) : null;
  2926	  };
  2927	  return {
  2928	    reported: true,
  2929	    status: toTrimmedString(runtime.status),
  2930	    statusSource: toTrimmedString(runtime.status_source),
  2931	    backend: toTrimmedString(runtime.llm_backend),
  2932	    model: toTrimmedString(runtime.llm_model),
  2933	    source: toTrimmedString(runtime.response_source || runtime.last_response_source),
  2934	    cachedAt: toTrimmedString(runtime.cached_at),
  2935	    observedAt: toTrimmedString(runtime.observed_at_utc),
  2936	    cacheHits: toNonNegativeInt(runtime.verified_cache_hits ?? runtime.cache_hits),
  2937	    expectedCount: toNonNegativeInt(runtime.expected_count),
  2938	    backendMatch: runtime.backend_match === true ? true : (runtime.backend_match === false ? false : null),
  2939	    requestedBackend: toTrimmedString(runtime.requested_backend),
  2940	    requestedModel: toTrimmedString(runtime.requested_model),
  2941	    detail: toTrimmedString(runtime.detail),
  2942	    boundaryNote: toTrimmedString(runtime.boundary_note),
  2943	  };
  2944	}
  2945	
  2946	function explainRuntimeSourceLabel(source) {
  2947	  if (source === "cached_llm") return "缓存命中";
  2948	  if (source === "live_llm") return "实时 LLM";
  2949	  if (source === "error") return "运行错误";
  2950	  return "未观察";
  2951	}
  2952	
  2953	function explainRuntimeBadgeState(runtime) {
  2954	  if (runtime.status === "shelved") return "shelved";
  2955	  if (!runtime.reported) return "idle";
  2956	  if (runtime.backendMatch === false || runtime.status === "warning") return "blocked";
  2957	  if (runtime.source === "cached_llm") return "ready";
  2958	  if (runtime.source === "error") return "blocked";
  2959	  if (runtime.source === "live_llm") return "live";
  2960	  return "idle";
  2961	}
  2962	
  2963	function explainRuntimeBadgeText(runtime) {
  2964	  if (runtime.status === "shelved") return "已搁置";
  2965	  if (!runtime.reported) return "未报告";
  2966	  if (runtime.backendMatch === false) return "后端不一致";
  2967	  if (runtime.status === "ready" && runtime.source === "cached_llm") return "缓存已验证";
  2968	  if (runtime.source === "live_llm") return "实时 explain";
  2969	  if (runtime.status === "warning") return "需要关注";
  2970	  return "待命";
  2971	}
  2972	
  2973	function renderExplainRuntime(payload) {
  2974	  const badge = workbenchElement("workbench-explain-runtime-badge");
  2975	  const summary = workbenchElement("workbench-explain-runtime-summary");
  2976	  const backendStrong = workbenchElement("workbench-explain-runtime-backend");
  2977	  const backendDetail = workbenchElement("workbench-explain-runtime-backend-detail");
  2978	  const sourceStrong = workbenchElement("workbench-explain-runtime-source");
  2979	  const sourceDetail = workbenchElement("workbench-explain-runtime-source-detail");
  2980	  const cacheStrong = workbenchElement("workbench-explain-runtime-cache");
  2981	  const cacheDetail = workbenchElement("workbench-explain-runtime-cache-detail");
  2982	  const boundaryStrong = workbenchElement("workbench-explain-runtime-boundary");
  2983	  if (!badge || !summary || !backendStrong || !sourceStrong || !cacheStrong || !boundaryStrong) {
  2984	    return;
  2985	  }
  2986	
  2987	  const runtime = readExplainRuntimePayload(payload);
  2988	  badge.dataset.state = explainRuntimeBadgeState(runtime);
  2989	  badge.textContent = explainRuntimeBadgeText(runtime);
  2990	
  2991	  // Phase A (2026-04-22): LLM features shelved. Short-circuit to a clean
  2992	  // "shelved" rendering so the cache/backend/source panels don't misreport
  2993	  // zero-counters as observed prewarm telemetry.
  2994	  if (runtime.status === "shelved") {
  2995	    summary.textContent = runtime.detail || "LLM explain 功能已搁置。";
  2996	    backendStrong.textContent = "已搁置";
  2997	    backendDetail.textContent = "LLM 后端已从活跃代码库搁置，见 archive/shelved/llm-features/SHELVED.md。";
  2998	    sourceStrong.textContent = "已搁置";
  2999	    sourceDetail.textContent = "explain 路由已移除，不会产生新的观察记录。";
  3000	    cacheStrong.textContent = "已搁置";
  3001	    cacheDetail.textContent = "LLM 缓存链路已停用；无 cached_at / 命中统计。";
  3002	    boundaryStrong.textContent = runtime.boundaryNote || "LLM 已搁置 — 非控制真值";
  3003	    return;
  3004	  }
  3005	
  3006	  if (!runtime.reported) {
  3007	    summary.textContent = "当前 workbench 响应还没带 explain runtime 观察值，所以这里只保留占位。";
  3008	  } else if (runtime.observedAt) {
  3009	    summary.textContent = `${runtime.detail || "已收到 explain runtime 观察值。"} 最近观测时间：${runtime.observedAt}。`;
  3010	  } else {
  3011	    summary.textContent = runtime.detail || "已收到 explain runtime 观察值。";
  3012	  }
  3013	
  3014	  if (runtime.backend || runtime.model) {
  3015	    const backendText = runtime.backend || "(未知 backend)";
  3016	    const modelText = runtime.model || "(未知 model)";
  3017	    backendStrong.textContent = `${backendText} · ${modelText}`;
  3018	    if (runtime.backendMatch === false) {
  3019	      const requestedBackendText = runtime.requestedBackend || "(未声明 backend)";
  3020	      const requestedModelText = runtime.requestedModel || "(auto)";
  3021	      backendDetail.textContent = `最近 pitch_prewarm 请求的是 ${requestedBackendText} · ${requestedModelText}，但当前观察到的运行后端不是这套，需要先纠正 demo_server。`;
  3022	    } else if (runtime.observedAt) {
  3023	      backendDetail.textContent = `这是最近一次 explain runtime 观测到的后端组合。观测时间：${runtime.observedAt}。`;
  3024	    } else {
  3025	      backendDetail.textContent = "这是当前 demo_server 暴露出来的 explain 后端组合；它只是操作者运行观察值，不改变任何控制真值。";
  3026	    }
  3027	  } else {
  3028	    backendStrong.textContent = "未报告";
  3029	    backendDetail.textContent = "后端暂未在 bootstrap / bundle 响应中提供 explain_runtime.llm_backend / llm_model，前端保留占位。";
  3030	  }
  3031	
  3032	  sourceStrong.textContent = explainRuntimeSourceLabel(runtime.source);
  3033	  if (runtime.backendMatch === false) {
  3034	    sourceDetail.textContent = "虽然最近预热流程有结果，但它对应的 backend / model 和当前期望不一致，所以这里会明确提醒，不把它误当成安全可用的缓存状态。";
  3035	  } else if (runtime.source === "cached_llm") {
  3036	    sourceDetail.textContent = "最近一次 explain 命中了预热缓存，说明 prewarm 生效；重启 demo_server 后需重新预热。";
  3037	  } else if (runtime.source === "live_llm") {
  3038	    sourceDetail.textContent = "最近一次 explain 走了实时 LLM（缓存未命中或未启用），请关注首次响应时延。";
  3039	  } else if (runtime.source === "error") {
  3040	    sourceDetail.textContent = "最近一次 explain 报错，详情请看 dev 抽屉 raw payload 或 server 日志。";
  3041	  } else {
  3042	    sourceDetail.textContent = "本轮还没观察到 explain 调用；一旦用户在 chat / demo 舱发起一次 explain，这里就会亮起。";
  3043	  }
  3044	
  3045	  if (runtime.cachedAt) {
  3046	    const hitsPart = runtime.cacheHits !== null ? ` · 验证命中 ${runtime.cacheHits}` : "";
  3047	    const expectedPart = runtime.expectedCount !== null ? `/${runtime.expectedCount}` : "";
  3048	    cacheStrong.textContent = runtime.cachedAt;
  3049	    cacheDetail.textContent = `cached_at 上报为 ${runtime.cachedAt}${hitsPart}${expectedPart}。explain 缓存只在 demo_server 进程内有效，重启或换 backend 都会清空，需要重新预热。`;
  3050	  } else if (runtime.cacheHits !== null || runtime.expectedCount !== null) {
  3051	    const parts = [];
  3052	    if (runtime.cacheHits !== null && runtime.expectedCount !== null) {
  3053	      parts.push(`验证命中 ${runtime.cacheHits}/${runtime.expectedCount}`);
  3054	    } else if (runtime.cacheHits !== null) {
  3055	      parts.push(`验证命中 ${runtime.cacheHits}`);
  3056	    } else if (runtime.expectedCount !== null) {
  3057	      parts.push(`预期 ${runtime.expectedCount}`);
  3058	    }
  3059	    cacheStrong.textContent = parts.join(" / ") || "待命";
  3060	    cacheDetail.textContent = "尚未看到 cached_at 时间戳，但最近 pitch_prewarm 已经回传了命中统计；仍可用来判断缓存是否在服务。";
  3061	  } else {
  3062	    cacheStrong.textContent = "待命";
  3063	    cacheDetail.textContent = "尚未看到 cached_at。若刚刚跑过 prewarm，请核对 demo_server 输出；否则这里会保持“待命”直到首次 explain 观察上报。";
  3064	  }
  3065	
  3066	  boundaryStrong.textContent = runtime.boundaryNote || "runtime status only";
  3067	}
  3068	
  3069	function renderArchiveSummary(archive) {
  3070	  const statusElement = workbenchElement("archive-status");
  3071	  if (!archive) {
  3072	    statusElement.textContent = "本次未生成 archive package。";
  3073	    renderBulletList("archive-files", [], "勾选“同时生成 archive package”后，成功运行会显示文件列表。");
  3074	    return;
  3075	  }
  3076	  statusElement.textContent = `已生成 archive package：${archive.archive_dir}`;
  3077	  const filePaths = [
  3078	    archive.manifest_json_path,
  3079	    archive.bundle_json_path,
  3080	    archive.summary_markdown_path,
  3081	    archive.intake_assessment_json_path,
  3082	    archive.clarification_brief_json_path,
  3083	    archive.playback_report_json_path,
  3084	    archive.fault_diagnosis_report_json_path,
  3085	    archive.knowledge_artifact_json_path,
  3086	    archive.workspace_handoff_json_path,
  3087	    archive.workspace_snapshot_json_path,
  3088	  ].filter(Boolean);
  3089	  renderBulletList("archive-files", filePaths, "Archive package 已生成。");
  3090	}
  3091	
  3092	function renderOnboardingReadinessFromPayload(payload) {
  3093	  const bundle = payload.bundle || {};
  3094	  const assessment = bundle.intake_assessment || {};
  3095	  const clarification = bundle.clarification_brief || {};
  3096	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  3097	  const sourceCount = Number(assessment.source_document_count || 0);
  3098	  const componentCount = Number(assessment.component_count || 0);
  3099	  const logicCount = Number(assessment.logic_node_count || 0);
  3100	  const scenarioCount = Number(assessment.acceptance_scenario_count || 0);
  3101	  const faultCount = Number(assessment.fault_mode_count || 0);
  3102	  const openQuestionCount = Number(clarification.open_question_count || 0);
  3103	  const blockingReasonCount = Number(clarification.blocking_reason_count || 0);
  3104	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  3105	  const answeredClarifications = followUpItems.filter((item) => item.status === "answered").length;
  3106	  const ready = Boolean(bundle.ready_for_spec_build);
  3107	  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
  3108	  const unlocks = Array.isArray(clarification.unlocks_after_completion) && clarification.unlocks_after_completion.length
  3109	    ? clarification.unlocks_after_completion.join(" / ")
  3110	    : (ready ? "spec_build / scenario_playback / fault_diagnosis / knowledge_capture" : "spec_build");
  3111	
  3112	  renderOnboardingReadiness({
  3113	    badgeState: ready ? "ready" : "blocked",
  3114	    badgeText: ready ? "可接第二套系统" : "还不能安全接入",
  3115	    summary: ready
  3116	      ? "这份 packet 已经具备进入第二套控制逻辑 spec build 的基本条件，可以继续往 playback、diagnosis、knowledge 走。"
  3117	      : "这份 packet 还不够完整。系统已经把“缺什么”拆出来了，先补齐再接第二套控制逻辑更稳。",
  3118	    docs: `${sourceCount} 份`,
  3119	    docsDetail: sourceCount
  3120	      ? `${sourceMode}${assessment.mixed_source_packet ? " / 混合来源" : ""}${assessment.includes_pdf_sources ? " / 含 PDF" : ""}`
  3121	      : "还没有来源文档。",
  3122	    components: `${componentCount} 项`,
  3123	    componentsDetail: componentCount ? "已有组件/信号定义。" : "还没有组件定义。",
  3124	    logic: `${logicCount} 个`,
  3125	    logicDetail: logicCount ? "已有逻辑节点结构。" : "还没有逻辑节点。",
  3126	    scenarios: `${scenarioCount} 个`,
  3127	    scenariosDetail: scenarioCount ? "已有可回放验收场景。" : "还没有验收场景。",
  3128	    faults: `${faultCount} 个`,
  3129	    faultsDetail: faultCount ? "已有故障模式可注入。" : "还没有故障模式。",
  3130	    clarifications: `${answeredClarifications}/${followUpItems.length || openQuestionCount || 0}`,
  3131	    clarificationsDetail: openQuestionCount
  3132	      ? `还有 ${openQuestionCount} 个澄清问题没回答。`
  3133	      : "澄清问题已补齐。",
  3134	    unlocks,
  3135	    gaps: `${blockingReasonCount} 个结构问题 / ${openQuestionCount} 个澄清问题`,
  3136	  });
  3137	}
  3138	
  3139	function renderSystemFingerprintFromPayload(payload) {
  3140	  const bundle = payload.bundle || {};
  3141	  const assessment = bundle.intake_assessment || {};
  3142	  const clarification = bundle.clarification_brief || {};
  3143	  const generatedSpec = assessment.generated_workbench_spec || {};
  3144	  const ready = Boolean(bundle.ready_for_spec_build);
  3145	  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  3146	  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];
  3147	
  3148	  if (assessment.mixed_source_packet) {
  3149	    sourceModeParts.push("混合来源");
  3150	  }
  3151	  if (assessment.includes_pdf_sources) {
  3152	    sourceModeParts.push("含 PDF");
  3153	  }
  3154	
  3155	  renderSystemFingerprint({
  3156	    badgeState: ready ? "ready" : "blocked",
  3157	    badgeText: ready ? "画像已识别" : "画像待补齐",
  3158	    summary: ready
  3159	      ? "这套系统已经不只是“能接入”，而是连文档覆盖、控制目标、工程真值和关键信号都已经清楚摊开了。"
  3160	      : "虽然这份 packet 还没 ready，但它的系统画像已经先展开了；你可以先确认方向对不对，再补缺口。",
  3161	    systemId: bundle.system_id || assessment.system_id || workbenchElement("workbench-fingerprint-system-id").textContent,
  3162	    objective: assessment.objective || workbenchElement("workbench-fingerprint-objective").textContent,
  3163	    sourceMode: sourceModeParts.join(" / "),
  3164	    sourceTruth: generatedSpec.source_of_truth || workbenchElement("workbench-fingerprint-source-truth").textContent,
  3165	    documents: Array.isArray(clarification.source_documents) ? clarification.source_documents : [],
  3166	    signals: Array.isArray(assessment.custom_signal_semantics) ? assessment.custom_signal_semantics : [],
  3167	    documentFallback: "当前 bundle 还没有识别出来源文档。",
  3168	    signalFallback: "当前 bundle 还没有识别出关键信号。",
  3169	  });
  3170	}
  3171	
  3172	function renderOnboardingActionsFromPayload(payload) {
  3173	  const bundle = payload.bundle || {};
  3174	  const assessment = bundle.intake_assessment || {};
  3175	  const clarification = bundle.clarification_brief || {};
  3176	  const ready = Boolean(bundle.ready_for_spec_build);
  3177	  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  3178	  const blockingReasons = Array.isArray(assessment.blocking_reasons) ? assessment.blocking_reasons : [];
  3179	  const unlocks = Array.isArray(clarification.unlocks_after_completion) ? clarification.unlocks_after_completion : [];
  3180	
  3181	  const pendingFollowUps = followUpItems
  3182	    .filter((item) => item.status !== "answered")
  3183	    .map((item) => createActionItemCard({
  3184	      title: item.id || "clarification",
  3185	      detail: item.prompt || "等待补齐说明。",
  3186	      chipText: "待回答",
  3187	      chipTone: "blocked",
  3188	    }));
  3189	
  3190	  const schemaBlockers = blockingReasons.map((reason, index) => createActionItemCard({
  3191	    title: `schema blocker ${index + 1}`,
  3192	    detail: reason,
  3193	    chipText: "待补结构",
  3194	    chipTone: "blocked",
  3195	  }));
  3196	
  3197	  const unlockItems = unlocks.map((item) => createActionItemCard({
  3198	    title: item,
  3199	    detail: ready
  3200	      ? "这项能力已经放行，可以继续往下走。"
  3201	      : "把左边两列补齐后，这项能力就会被解锁。",
  3202	    chipText: ready ? "已解锁" : "待解锁",
  3203	    chipTone: ready ? "ready" : "signal",
  3204	  }));
  3205	
  3206	  renderOnboardingActions({
  3207	    badgeState: ready ? "ready" : "blocked",
  3208	    badgeText: ready ? "接入路径已放行" : "接入路径待补齐",
  3209	    summary: ready
  3210	      ? "这套系统当前已经没有澄清或结构阻塞，动作板上只保留已放行的下一步能力。"
  3211	      : "这套系统还没 ready，但动作板已经把先补什么、再补什么、补完解锁什么拆开了。",
  3212	    followUps: pendingFollowUps,
  3213	    blockers: schemaBlockers,
  3214	    unlocks: unlockItems,
  3215	    followUpFallback: ready ? "澄清项都已回答。" : "当前没有待回答澄清项。",
  3216	    blockerFallback: ready ? "结构问题已补齐。" : "当前没有额外结构 blocker。",
  3217	    unlockFallback: "当前没有可展示的解锁项。",
  3218	  });
  3219	}
  3220	
  3221	function renderVisualAcceptanceBoard(payload) {
  3222	  const bundle = payload.bundle || {};
  3223	  const clarification = bundle.clarification_brief || {};
  3224	  const diagnosis = bundle.fault_diagnosis_report || {};
  3225	  const knowledge = bundle.knowledge_artifact || {};
  3226	  const archive = payload.archive || null;
  3227	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  3228	    ? bundle.intake_assessment.blocking_reasons
  3229	    : [];
  3230	  const ready = Boolean(bundle.ready_for_spec_build);
  3231	
  3232	  if (ready) {
  3233	    setVisualBadge(archive ? "archived" : "ready", archive ? "通过并已归档" : "可以验收");
  3234	    renderValue("workbench-spotlight-verdict", "链路已跑通");
  3235	    renderValue(
  3236	      "workbench-spotlight-verdict-detail",
  3237	      archive
  3238	        ? "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge，并已留下 archive。"
  3239	        : "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge。"
  3240	    );
  3241	    renderValue("workbench-spotlight-blocker", "当前无阻塞");
  3242	    renderValue(
  3243	      "workbench-spotlight-blocker-detail",
  3244	      bundle.selected_fault_mode_id
  3245	        ? `当前 fault mode：${bundle.selected_fault_mode_id}，可以直接看右侧卡片做验收。`
  3246	        : "当前没有 blocking reason。"
  3247	    );
  3248	    renderValue("workbench-spotlight-knowledge", knowledge.status || "已生成");
  3249	    renderValue(
  3250	      "workbench-spotlight-knowledge-detail",
  3251	      knowledge.diagnosis_summary || diagnosis.suspected_root_cause || "知识沉淀已生成。"
  3252	    );
  3253	    renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
  3254	    renderValue(
  3255	      "workbench-spotlight-archive-detail",
  3256	      archive
  3257	        ? `目录：${shortPath(archive.archive_dir)}`
  3258	        : "本次没有生成 archive package。"
  3259	    );
  3260	    renderValue(
  3261	      "workbench-visual-summary",
  3262	      "这次 bundle 已经走完整条 engineer workflow。你现在主要看步骤状态带和聚焦卡片，不必先看 Raw JSON。"
  3263	    );
  3264	    setStageState("intake", "complete", "packet 已通过 intake 检查。");
  3265	    setStageState("clarification", "complete", clarification.gate_status || "clarification 已放行。");
  3266	    setStageState("playback", "complete", "已生成可复盘的 playback。");
  3267	    setStageState("diagnosis", "complete", diagnosis.suspected_root_cause || "已生成 diagnosis。");
  3268	    setStageState("knowledge", "complete", knowledge.status ? `knowledge=${knowledge.status}` : "已生成 knowledge artifact。");
  3269	    setStageState("archive", archive ? "complete" : "pending", archive ? "archive package 已落档。" : "本次未归档，但可随时重跑。");
  3270	    return;
  3271	  }
  3272	
  3273	  setVisualBadge(archive ? "archived" : "blocked", archive ? "阻塞但已归档" : "当前阻塞");
  3274	  renderValue("workbench-spotlight-verdict", "需要补信息");
  3275	  renderValue(
  3276	    "workbench-spotlight-verdict-detail",
  3277	    "当前 packet 还没走到 playback / diagnosis / knowledge，先补齐 clarification gate 需要的信息。"
  3278	  );
  3279	  renderValue("workbench-spotlight-blocker", "Clarification Gate");
  3280	  renderValue(
  3281	    "workbench-spotlight-blocker-detail",
  3282	    blockingReasons.length ? blockingReasons[0] : clarification.gating_statement || "当前 packet 仍未 ready。"
  3283	  );
  3284	  renderValue("workbench-spotlight-knowledge", "尚未形成");
  3285	  renderValue("workbench-spotlight-knowledge-detail", "因为 clarification 还没过，所以 diagnosis / knowledge 还不会生成。");
  3286	  renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
  3287	  renderValue(
  3288	    "workbench-spotlight-archive-detail",
  3289	    archive
  3290	      ? `已把当前阻塞态留档到 ${shortPath(archive.archive_dir)}`
  3291	      : "如果你想保留这次阻塞态，可以勾选 archive 后重跑。"
  3292	  );
  3293	  renderValue(
  3294	    "workbench-visual-summary",
  3295	    "这次不是失败，而是系统在 clarification gate 主动停下来了。你只要看卡在哪一步，不需要读后面的专业输出。"
  3296	  );
  3297	  setStageState("intake", "complete", "packet 已被读取并检查。");
  3298	  setStageState("clarification", "blocked", clarification.gate_status || "clarification 仍未放行。");
  3299	  setStageState("playback", "idle", "clarification 未过，暂不继续。");
  3300	  setStageState("diagnosis", "idle", "clarification 未过，暂不继续。");
  3301	  setStageState("knowledge", "idle", "clarification 未过，暂不继续。");
  3302	  setStageState("archive", archive ? "complete" : "pending", archive ? "阻塞态也已成功归档。" : "当前未归档。");
  3303	}
  3304	
  3305	function renderBundleResponse(payload, {
  3306	  pushHistory = true,
  3307	  sourceMode = "当前来源：`POST /api/workbench/bundle`。",
  3308	  requestStatusMessage = null,
  3309	  requestStatusTone = null,
  3310	} = {}) {
  3311	  const bundle = payload.bundle || {};
  3312	  const clarification = bundle.clarification_brief || {};
  3313	  const playback = bundle.playback_report || {};
  3314	  const diagnosis = bundle.fault_diagnosis_report || {};
  3315	  const knowledge = bundle.knowledge_artifact || {};
  3316	  const resolution = knowledge.resolution_record || {};
  3317	  const optimization = knowledge.optimization_record || {};
  3318	  const ready = Boolean(bundle.ready_for_spec_build);
  3319	  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
  3320	  workbenchElement("bundle-ready-state").textContent = ready ? "Ready" : "Blocked";
  3321	  workbenchElement("bundle-ready-state").dataset.state = ready ? "ready" : "blocked";
  3322	  workbenchElement("bundle-scenario-id").textContent = bundle.selected_scenario_id || "(none)";
  3323	  workbenchElement("bundle-fault-mode-id").textContent = bundle.selected_fault_mode_id || "(none)";
  3324	  workbenchElement("clarification-gate-status").textContent = clarification.gate_status || "-";
  3325	  workbenchElement("clarification-gating-statement").textContent = clarification.gating_statement || "-";
  3326	  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
  3327	    ? bundle.intake_assessment.blocking_reasons
  3328	    : [];
  3329	  workbenchElement("bundle-blocking-reasons").textContent = blockingReasons.length
  3330	    ? blockingReasons.join(" | ")
  3331	    : "none";
  3332	
  3333	  renderOnboardingReadinessFromPayload(payload);
  3334	  renderSystemFingerprintFromPayload(payload);
  3335	  renderOnboardingActionsFromPayload(payload);
  3336	  renderSchemaRepairWorkspaceFromPayload(payload);
  3337	  renderClarificationWorkspaceFromPayload(payload);
  3338	  renderVisualAcceptanceBoard(payload);
  3339	  renderBulletList("bundle-next-actions", bundle.next_actions, "当前没有 next actions。");
  3340	  renderValue("playback-scenario-label", playback.scenario_label, ready ? "未提供 playback label。" : "Blocked bundle 不包含 playback。");
  3341	  renderValue("playback-completion", playback.completion_reached, ready ? "false" : "Blocked bundle 不包含 playback。");
  3342	  renderValue("playback-sampled-signals", Array.isArray(playback.signal_series) ? playback.signal_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  3343	  renderValue("playback-sampled-logic", Array.isArray(playback.logic_series) ? playback.logic_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  3344	  renderValue("diagnosis-fault-mode", diagnosis.fault_mode_id || bundle.selected_fault_mode_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3345	  renderValue("diagnosis-target-component", diagnosis.target_component_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3346	  renderValue("diagnosis-root-cause", diagnosis.suspected_root_cause, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  3347	  renderValue(
  3348	    "diagnosis-blocked-logic",
  3349	    Array.isArray(diagnosis.blocked_logic_node_ids) && diagnosis.blocked_logic_node_ids.length
  3350	      ? diagnosis.blocked_logic_node_ids.join(" | ")
  3351	      : null,
  3352	    ready ? "none" : "Blocked bundle 不包含 diagnosis。",
  3353	  );
  3354	  renderValue("knowledge-status", knowledge.status, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3355	  renderValue("knowledge-diagnosis-summary", knowledge.diagnosis_summary, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3356	  renderValue("knowledge-confirmed-root-cause", resolution.confirmed_root_cause, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3357	  renderValue("knowledge-repair-action", resolution.repair_action, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3358	  renderValue("knowledge-validation-after-fix", resolution.validation_after_fix, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3359	  renderValue("knowledge-residual-risk", resolution.residual_risk, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  3360	  renderValue("optimization-logic-change", optimization.suggested_logic_change, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  3361	  renderValue("optimization-reliability-gain", optimization.reliability_gain_hypothesis, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  3362	  renderValue(
  3363	    "optimization-guardrail-note",
  3364	    optimization.redundancy_reduction_or_guardrail_note,
  3365	    ready ? "(none)" : "Blocked bundle 不包含 optimization record。",
  3366	  );
  3367	  if (pushHistory) {
  3368	    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromPayload(payload));
  3369	  }
  3370	  if (payload.archive) {
  3371	    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromBundlePayload(payload));
  3372	  }
  3373	  renderArchiveSummary(payload.archive);
  3374	  renderExplainRuntime(payload);
  3375	  workbenchElement("bundle-json-output").textContent = prettyJson(payload);
  3376	  setResultMode(sourceMode);
  3377	  setRequestStatus(
  3378	    requestStatusMessage || (
  3379	      ready
  3380	        ? "Bundle 已生成，可直接拿右侧结果做验收。"
  3381	        : "Clarification follow-up bundle 已生成；当前 packet 仍被 schema / clarification gate 阻塞。"
  3382	    ),
  3383	    requestStatusTone || (ready ? "success" : "warning"),
  3384	  );
  3385	}
  3386	
  3387	function collectWorkbenchRequestPayload() {
  3388	  let packetPayload;
  3389	  try {
  3390	    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  3391	  } catch (error) {
  3392	    throw new Error(`packet JSON 解析失败：${String(error.message || error)}`);
  3393	  }
  3394	  return {
  3395	    packet_payload: packetPayload,
  3396	    scenario_id: workbenchElement("workbench-scenario-id").value.trim() || undefined,
  3397	    fault_mode_id: workbenchElement("workbench-fault-mode-id").value.trim() || undefined,
  3398	    sample_period_s: Number(workbenchElement("workbench-sample-period").value || "0.5"),
  3399	    archive_bundle: workbenchElement("workbench-archive-toggle").checked,
  3400	    workspace_handoff: buildWorkbenchHandoffSnapshot(),
  3401	    workspace_snapshot: collectWorkbenchPacketWorkspaceState(),
  3402	    observed_symptoms: workbenchElement("workbench-observed-symptoms").value.trim() || undefined,
  3403	    evidence_links: splitLines(workbenchElement("workbench-evidence-links").value),
  3404	    confirmed_root_cause: workbenchElement("workbench-root-cause").value.trim() || undefined,
  3405	    repair_action: workbenchElement("workbench-repair-action").value.trim() || undefined,
  3406	    validation_after_fix: workbenchElement("workbench-validation-after-fix").value.trim() || undefined,
  3407	    residual_risk: workbenchElement("workbench-residual-risk").value.trim() || undefined,
  3408	    suggested_logic_change: workbenchElement("workbench-logic-change").value.trim() || undefined,
  3409	    reliability_gain_hypothesis: workbenchElement("workbench-reliability-gain").value.trim() || undefined,
  3410	    guardrail_note: workbenchElement("workbench-guardrail-note").value.trim() || undefined,
  3411	  };
  3412	}
  3413	
  3414	function checkUrlIntakeParam() {
  3415	  try {
  3416	    const params = new URLSearchParams(window.location.search);
  3417	    const intakeRaw = params.get("intake");
  3418	    let intakePacket;
  3419	    let textarea;
  3420	    if (!intakeRaw) {
  3421	      return false;
  3422	    }
  3423	    try {
  3424	      intakePacket = JSON.parse(intakeRaw);
  3425	    } catch (parseError) {
  3426	      intakePacket = JSON.parse(decodeURIComponent(intakeRaw));
  3427	    }
  3428	    if (!intakePacket || typeof intakePacket !== "object") {
  3429	      return false;
  3430	    }
  3431	    setPacketEditor(intakePacket);
  3432	    textarea = workbenchElement("workbench-packet-json");
  3433	    if (textarea) {
  3434	      textarea.scrollTop = textarea.scrollHeight;
  3435	    }
  3436	    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(intakePacket, {
  3437	      title: "Pipeline 结果预载入",
  3438	      summary: "通过 URL intake 参数载入的 packet。",
  3439	    }));
  3440	    renderPreparationBoard("Pipeline 结果已经装载，系统会自动生成 bundle 并显示诊断结果。");
  3441	    renderSystemFingerprintFromPacketPayload(intakePacket, {
  3442	      badgeState: "idle",
  3443	      badgeText: "画像已载入",
  3444	      summary: "Pipeline 结果已经带入当前 workbench，系统会直接继续生成 bundle。",
  3445	    });
  3446	    setPacketSourceStatus("当前样例：来自 AI Document Analyzer 的 Pipeline 结果。页面会自动生成 Bundle。");
  3447	    setCurrentWorkbenchRunLabel("Pipeline 结果导入");
  3448	    setActiveWorkbenchPreset("");
  3449	    return true;
  3450	  } catch (error) {
  3451	    return false;
  3452	  }
  3453	}
  3454	
  3455	async function loadBootstrapPayload() {
  3456	  setRequestStatus("正在加载 bootstrap 样例...", "neutral");
  3457	  const response = await fetch(workbenchBootstrapPath, {method: "GET"});
  3458	  const payload = await response.json();
  3459	  if (!response.ok) {
  3460	    throw new Error(payload.error || "bootstrap request failed");
  3461	  }
  3462	  bootstrapPayload = payload;
  3463	  renderExplainRuntime(payload);
  3464	  workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
  3465	  renderRecentWorkbenchArchives();
  3466	  workbenchElement("default-archive-root").textContent = payload.default_archive_root || "(unknown)";
  3467	  if (restoreWorkbenchPacketWorkspaceFromBrowser()) {
  3468	    return;
  3469	  }
  3470	  setPacketEditor(payload.reference_packet);
  3471	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.reference_packet, {
  3472	    title: "默认参考样例",
  3473	    summary: "启动时自动载入的 reference packet。",
  3474	  }));
  3475	  fillReferenceResolutionDefaults();
  3476	  setPacketSourceStatus("当前样例：参考样例。适合直接点“生成 Bundle”做可视化 happy path 验收。");
  3477	  renderPreparationBoard("参考样例已经装载完毕，点击“生成 Bundle”即可进入可视化验收。");
  3478	  renderSystemFingerprintFromPacketPayload(payload.reference_packet, {
  3479	    badgeState: "idle",
  3480	    badgeText: "画像已载入",
  3481	    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  3482	  });
  3483	  setActiveWorkbenchPreset("");
  3484	  setRequestStatus("已载入 reference packet，直接点“生成 Bundle”即可跑 happy path。", "success");
  3485	}
  3486	
  3487	async function runWorkbenchBundle() {
  3488	  const requestId = beginWorkbenchRequest();
  3489	  let requestPayload;
  3490	  try {
  3491	    requestPayload = collectWorkbenchRequestPayload();
  3492	  } catch (error) {
  3493	    if (!isLatestWorkbenchRequest(requestId)) {
  3494	      return false;
  3495	    }
  3496	    renderFailureResponse(String(error.message || error), {
  3497	      sourceMode: "当前来源：输入解析失败。",
  3498	      requestStatusMessage: String(error.message || error),
  3499	    });
  3500	    return false;
  3501	  }
  3502	  maybeCaptureCurrentPacketRevision({
  3503	    title: `${currentWorkbenchRunLabel} / 运行前 Packet`,
  3504	    summary: "在本次 bundle 请求前捕获当前 packet 版本。",
  3505	  });
  3506	  renderSystemFingerprintFromPacketPayload(requestPayload.packet_payload, {
  3507	    badgeState: "idle",
  3508	    badgeText: "画像解析中",
  3509	    summary: "系统正在生成 bundle，但这套系统的文档来源、控制目标和关键信号已经先展开给你看了。",
  3510	  });
  3511	  renderRunningBoard(`${currentWorkbenchRunLabel}：正在生成 bundle，请直接看上方可视化验收板。`);
  3512	  setRequestStatus("正在生成 workbench bundle...", "neutral");
  3513	  try {
  3514	    const response = await fetch(workbenchBundlePath, {
  3515	      method: "POST",
  3516	      headers: {"Content-Type": "application/json"},
  3517	      body: JSON.stringify(requestPayload),
  3518	    });
  3519	    const payload = await response.json();
  3520	    if (!isLatestWorkbenchRequest(requestId)) {
  3521	      return false;
  3522	    }
  3523	    if (!response.ok) {
  3524	      throw new Error(payload.message || payload.error || "workbench bundle request failed");
  3525	    }
  3526	    renderBundleResponse(payload);
  3527	    return true;
  3528	  } catch (error) {
  3529	    if (!isLatestWorkbenchRequest(requestId)) {
  3530	      return false;
  3531	    }
  3532	    renderFailureResponse(String(error.message || error));
  3533	    return false;
  3534	  }
  3535	}
  3536	
  3537	function installPacketSourceHandlers() {
  3538	  workbenchElement("load-reference-packet").addEventListener("click", () => {
  3539	    if (!applyReferencePacketSelection({
  3540	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3541	      sourceStatus: "当前样例：参考样例。适合直接点 '生成 Bundle' 做可视化 happy path 验收。",
  3542	      preparationMessage: "参考样例已经装载完毕，点击 '生成 Bundle' 即可进入可视化验收。",
  3543	    })) {
  3544	      return;
  3545	    }
  3546	    setCurrentWorkbenchRunLabel("手动生成");
  3547	    setActiveWorkbenchPreset("");
  3548	    setRequestStatus("已载入 reference packet。", "success");
  3549	  });
  3550	
  3551	  workbenchElement("load-template-packet").addEventListener("click", () => {
  3552	    if (!applyTemplatePacketSelection({
  3553	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3554	      sourceStatus: "当前样例：空白模板。适合验证 clarification gate 是否会主动拦住不完整 packet。",
  3555	      preparationMessage: "空白模板已经装载完毕，运行后通常会在 clarification gate 停下。",
  3556	    })) {
  3557	      return;
  3558	    }
  3559	    setCurrentWorkbenchRunLabel("手动生成");
  3560	    setActiveWorkbenchPreset("");
  3561	    setRequestStatus("已载入空白模板。", "warning");
  3562	  });
  3563	
  3564	  workbenchElement("workbench-file-input").addEventListener("change", async (event) => {
  3565	    const input = event.currentTarget;
  3566	    const [file] = input.files || [];
  3567	    if (!file) {
  3568	      return;
  3569	    }
  3570	
  3571	    const text = await file.text();
  3572	    maybeAutoSnapshotCurrentPacketDraft("导入本地 JSON / " + file.name);
  3573	    workbenchElement("workbench-packet-json").value = text;
  3574	    setPacketSourceStatus("当前样例：本地文件 " + file.name + "。如果不是在调试，可以直接点 '生成 Bundle' 看可视化结果。");
  3575	    renderPreparationBoard("本地 JSON 已装载，运行后会把当前 packet 的通过/阻塞结果显示在上方看板。");
  3576	
  3577	    try {
  3578	      const packetPayload = JSON.parse(text);
  3579	      pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(packetPayload, {
  3580	        title: "导入本地 JSON / " + file.name,
  3581	        summary: "本地 packet 已导入输入区。",
  3582	      }));
  3583	      renderSystemFingerprintFromPacketPayload(packetPayload, {
  3584	        badgeState: "idle",
  3585	        badgeText: "画像已载入",
  3586	        summary: "本地 JSON 已装载。你现在就能先看这套系统的大致画像，再决定要不要继续生成 bundle。",
  3587	      });
  3588	    } catch (error) {
  3589	      renderSystemFingerprint({
  3590	        badgeState: "blocked",
  3591	        badgeText: "画像未识别",
  3592	        summary: "本地 JSON 还没解析成功，所以系统画像暂时无法展开：" + String(error.message || error),
  3593	        documentFallback: "先修正 JSON，再显示来源文档。",
  3594	        signalFallback: "先修正 JSON，再显示关键信号。",
  3595	      });
  3596	    }
  3597	
  3598	    setCurrentWorkbenchRunLabel("手动生成 / " + file.name);
  3599	    setActiveWorkbenchPreset("");
  3600	    setRequestStatus("已载入本地文件：" + file.name, "success");
  3601	    input.value = "";
  3602	  });
  3603	}
  3604	
  3605	function installWorkspaceSnapshotHandlers() {
  3606	  workbenchElement("export-workbench-workspace").addEventListener("click", () => {
  3607	    downloadWorkbenchWorkspaceSnapshot();
  3608	  });
  3609	
  3610	  workbenchElement("restore-workbench-archive").addEventListener("click", () => {
  3611	    void restoreWorkbenchArchiveFromManifest();
  3612	  });
  3613	
  3614	  workbenchElement("refresh-workbench-recent-archives").addEventListener("click", () => {
  3615	    void refreshRecentWorkbenchArchives();
  3616	  });
  3617	
  3618	  workbenchElement("copy-workbench-handoff-brief").addEventListener("click", () => {
  3619	    void copyWorkbenchHandoffBrief();
  3620	  });
  3621	
  3622	  workbenchElement("workbench-workspace-file-input").addEventListener("change", async (event) => {
  3623	    const input = event.currentTarget;
  3624	    const [file] = input.files || [];
  3625	    if (!file) {
  3626	      return;
  3627	    }
  3628	
  3629	    await importWorkbenchWorkspaceSnapshot(file);
  3630	    input.value = "";
  3631	  });
  3632	}
  3633	
  3634	function installExecutionHandlers() {
  3635	  workbenchElement("run-workbench-bundle").addEventListener("click", () => {
  3636	    setCurrentWorkbenchRunLabel("手动生成");
  3637	    setActiveWorkbenchPreset("");
  3638	    void runWorkbenchBundle();
  3639	  });
  3640	
  3641	  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
  3642	    button.addEventListener("click", () => {
  3643	      setCurrentWorkbenchRunLabel(button.textContent.trim());
  3644	      runWorkbenchPreset(button.dataset.workbenchPreset || "");
  3645	    });
  3646	  });
  3647	}
  3648	
  3649	function installP43Handlers() {
  3650	  const approveBtn = workbenchElement("workbench-final-approve");
  3651	  if (approveBtn) {
  3652	    approveBtn.addEventListener("click", () => { handleFinalApprove(); });
  3653	  }
  3654	  const startGenBtn = workbenchElement("workbench-start-gen");
  3655	  if (startGenBtn) {
  3656	    startGenBtn.addEventListener("click", () => { void handleStartGen(); });
  3657	  }
  3658	}
  3659	
  3660	function installPersistenceHandlers() {
  3661	  workbenchElement("workbench-packet-json").addEventListener("input", () => {
  3662	    renderWorkbenchPacketDraftState();
  3663	    persistWorkbenchPacketWorkspace();
  3664	    saveDraftDesignState({
  3665	      packetJsonText: workbenchElement("workbench-packet-json").value,
  3666	      savedAt: new Date().toISOString(),
  3667	    });
  3668	  });
  3669	
  3670	  workbenchPersistedFieldIds.forEach((id) => {
  3671	    const field = workbenchElement(id);
  3672	    const eventName = field && field.type === "checkbox" ? "change" : "input";
  3673	    field.addEventListener(eventName, () => {
  3674	      persistWorkbenchPacketWorkspace();
  3675	    });
  3676	  });
  3677	}
  3678	
  3679	function installRecoveryAndRepairHandlers() {
  3680	  workbenchElement("workbench-history-return-latest").addEventListener("click", () => {
  3681	    restoreLatestWorkbenchHistory();
  3682	  });
  3683	
  3684	  workbenchElement("workbench-packet-history-return-latest").addEventListener("click", () => {
  3685	    restoreLatestWorkbenchPacketRevision();
  3686	  });
  3687	
  3688	  workbenchElement("workbench-save-packet-draft").addEventListener("click", () => {
  3689	    saveCurrentWorkbenchPacketDraft();
  3690	  });
  3691	
  3692	  workbenchElement("workbench-apply-schema-repairs").addEventListener("click", () => {
  3693	    void runWorkbenchSchemaSafeRepair();
  3694	  });
  3695	
  3696	  workbenchElement("workbench-apply-clarifications").addEventListener("click", () => {
  3697	    void applyClarificationWorkspace({ rerun: false });
  3698	  });
  3699	
  3700	  workbenchElement("workbench-apply-and-rerun").addEventListener("click", () => {
  3701	    void applyClarificationWorkspace({ rerun: true });
  3702	  });
  3703	}
  3704	
  3705	function installToolbarHandlers() {
  3706	  installPacketSourceHandlers();
  3707	  installWorkspaceSnapshotHandlers();
  3708	  installExecutionHandlers();
  3709	  installPersistenceHandlers();
  3710	  installRecoveryAndRepairHandlers();
  3711	  installP43Handlers();
  3712	}
  3713	
  3714	function installViewModeHandlers() {
  3715	  function setViewMode(mode) {
  3716	    document.body.dataset.view = mode;
  3717	    workbenchElement("view-btn-beginner").classList.toggle("is-active", mode === "beginner");
  3718	    workbenchElement("view-btn-expert").classList.toggle("is-active", mode === "expert");
  3719	    workbenchElement("view-mode-hint").textContent = mode === "beginner"
  3720	      ? "— 专家工具默认折叠，适合先看结论"
  3721	      : "— 显示所有工具：JSON 编辑器 / schema repair / clarification";
  3722	  }
  3723	
  3724	  const beginnerBtn = workbenchElement("view-btn-beginner");
  3725	  const expertBtn = workbenchElement("view-btn-expert");
  3726	  if (!beginnerBtn || !expertBtn) {
  3727	    return;
  3728	  }
  3729	
  3730	  beginnerBtn.addEventListener("click", () => {
  3731	    setViewMode("beginner");
  3732	  });
  3733	  expertBtn.addEventListener("click", () => {
  3734	    setViewMode("expert");
  3735	  });
  3736	
  3737	  setViewMode("beginner");
  3738	}
  3739	
  3740	// E11-13 (2026-04-25): manual_feedback_override trust-affordance.
  3741	// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
  3742	// it onto #workbench-trust-banner so the banner shows only when mode =
  3743	// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
  3744	// (e.g., when the snapshot endpoint reports a different mode in future
  3745	// E11-14+). Banner dismissal is session-local (sessionStorage); chip + actual
  3746	// mode value remain visible across dismissals.
  3747	function syncTrustBannerForMode(mode) {
  3748	  const banner = document.getElementById("workbench-trust-banner");
  3749	  if (banner) {
  3750	    banner.setAttribute("data-feedback-mode", mode);
  3751	  }
  3752	}
  3753	
  3754	function setFeedbackMode(mode) {
  3755	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  3756	  if (!allowed.has(mode)) {
  3757	    return false;
  3758	  }
  3759	  const chip = document.getElementById("workbench-feedback-mode");
  3760	  if (chip) {
  3761	    chip.setAttribute("data-feedback-mode", mode);
  3762	    const label = chip.querySelector("strong");
  3763	    if (label) {
  3764	      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
  3765	    }
  3766	  }
  3767	  syncTrustBannerForMode(mode);
  3768	  return true;
  3769	}
  3770	
  3771	function installFeedbackModeAffordance() {
  3772	  const chip = document.getElementById("workbench-feedback-mode");
  3773	  const banner = document.getElementById("workbench-trust-banner");
  3774	  if (!chip || !banner) {
  3775	    return;
  3776	  }
  3777	  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
  3778	  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
  3779	    banner.setAttribute("data-trust-banner-dismissed", "true");
  3780	  }
  3781	  const dismiss = banner.querySelector("[data-trust-banner-dismiss]");
  3782	  if (dismiss) {
  3783	    dismiss.addEventListener("click", () => {
  3784	      banner.setAttribute("data-trust-banner-dismissed", "true");
  3785	      if (window.sessionStorage) {
  3786	        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
  3787	      }
  3788	    });
  3789	  }
  3790	}
  3791	
  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
  3793	// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py and the
  3794	// monte-carlo / reverse-diagnose API contracts from the matching e2e suites.
  3795	// One click → POST → single-line summary in the card's result area.
  3796	const WOW_SCENARIOS = {
  3797	  wow_a: {
  3798	    endpoint: "/api/lever-snapshot",
  3799	    payload: {
  3800	      tra_deg: -35,
  3801	      radio_altitude_ft: 2,
  3802	      engine_running: true,
  3803	      aircraft_on_ground: true,
  3804	      reverser_inhibited: false,
  3805	      eec_enable: true,
  3806	      n1k: 0.92,
  3807	      feedback_mode: "auto_scrubber",
  3808	      deploy_position_percent: 95,
  3809	    },
  3810	    summarize: (body) => {
  3811	      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
  3812	      const active = nodes.filter((n) => n && n.state === "active").length;
  3813	      return `nodes=${nodes.length} · active=${active} · L1–L4 chain latched.`;
  3814	    },
  3815	  },
  3816	  wow_b: {
  3817	    endpoint: "/api/monte-carlo/run",
  3818	    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
  3819	    summarize: (body) => {
  3820	      if (!body) return "(empty body)";
  3821	      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
  3822	      const failures = body.n_failures;
  3823	      const trials = body.n_trials;
  3824	      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
  3825	    },
  3826	  },
  3827	  wow_c: {
  3828	    endpoint: "/api/diagnosis/run",
  3829	    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
  3830	    summarize: (body) => {
  3831	      if (!body) return "(empty body)";
  3832	      const total = body.total_combos_found;
  3833	      const returned = Array.isArray(body.results) ? body.results.length : 0;
  3834	      const grid = body.grid_resolution;
  3835	      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
  3836	    },
  3837	  },
  3838	};
  3839	
  3840	async function runWowScenario(wowId) {
  3841	  const scenario = WOW_SCENARIOS[wowId];
  3842	  const button = document.querySelector(
  3843	    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  3844	  );
  3845	  const result = document.querySelector(
  3846	    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  3847	  );
  3848	  if (!scenario || !result) {
  3849	    return;
  3850	  }
  3851	  if (button) {
  3852	    button.disabled = true;
  3853	  }
  3854	  result.removeAttribute("data-wow-state");
  3855	  result.textContent = `POST ${scenario.endpoint} ...`;
  3856	  try {
  3857	    const t0 = performance.now();
  3858	    const response = await fetch(scenario.endpoint, {
  3859	      method: "POST",
  3860	      headers: { "Content-Type": "application/json" },
  3861	      body: JSON.stringify(scenario.payload),
  3862	    });
  3863	    const ms = Math.round(performance.now() - t0);
  3864	    let body = null;
  3865	    try {
  3866	      body = await response.json();
  3867	    } catch (_err) {
  3868	      body = null;
  3869	    }
  3870	    if (!response.ok) {
  3871	      result.setAttribute("data-wow-state", "error");
  3872	      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
  3873	      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
  3874	      return;
  3875	    }
  3876	    result.setAttribute("data-wow-state", "ok");
  3877	    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  3878	  } catch (err) {
  3879	    result.setAttribute("data-wow-state", "error");
  3880	    result.textContent = `network error: ${err && err.message ? err.message : err}`;
  3881	  } finally {
  3882	    if (button) {
  3883	      button.disabled = false;
  3884	    }
  3885	  }
  3886	}
  3887	
  3888	function installWowStarters() {
  3889	  const buttons = document.querySelectorAll(
  3890	    '.workbench-wow-run-button[data-wow-action="run"]',
  3891	  );
  3892	  buttons.forEach((btn) => {
  3893	    btn.addEventListener("click", () => {
  3894	      const wowId = btn.getAttribute("data-wow-id");
  3895	      if (wowId && WOW_SCENARIOS[wowId]) {
  3896	        void runWowScenario(wowId);
  3897	      }
  3898	    });
  3899	  });
  3900	}
  3901	
  3902	window.addEventListener("DOMContentLoaded", () => {
  3903	  bootWorkbenchShell();
  3904	  installViewModeHandlers();
  3905	  installFeedbackModeAffordance();
  3906	  installWowStarters();
  3907	
  3908	  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  3909	  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  3910	  // NOT contain bundle elements like #workbench-packet-json,
  3911	  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  3912	  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  3913	  // bundle DOM exists and would throw "Cannot read properties of null" on the
  3914	  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  3915	  // skip bundle boot entirely. This script is shared between both pages.
  3916	  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  3917	  if (!onBundlePage) {
  3918	    return;
  3919	  }
  3920	
  3921	  installToolbarHandlers();
  3922	  updateWorkflowUI();
  3923	  if (checkUrlIntakeParam()) {
  3924	    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
  3925	    if (bundleBtn) {
  3926	      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
  3927	      bundleBtn.click();
  3928	    }
  3929	    return;
  3930	  }
  3931	  void loadBootstrapPayload();
  3932	});

codex
I’ve got the UI/test surface and the truth-boundary diff. Now I’m reading the backing endpoint contracts and demo-server behavior, because the main review risk is whether the cards describe probe results too strongly from a customer-repro standpoint.
exec
/bin/zsh -lc "rg -n \"BEAT_DEEP_PAYLOAD|/api/lever-snapshot|/api/monte-carlo/run|/api/diagnosis/run|deploy_confirmed|total_combos_found|grid_resolution|feedback_mode|residual_risk\" tests/e2e src/well_harness -g '"'!src/well_harness/static/*'"'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/e2e/test_wow_b_monte_carlo.py:3:Locks the observable contract of /api/monte-carlo/run against a live
tests/e2e/test_wow_b_monte_carlo.py:26:    return api_post(base_url, "/api/monte-carlo/run",
src/well_harness/knowledge_capture.py:80:    residual_risk: str | None,
src/well_harness/knowledge_capture.py:88:            residual_risk,
src/well_harness/knowledge_capture.py:121:    residual_risk: str | None = None,
src/well_harness/knowledge_capture.py:137:        residual_risk=residual_risk,
src/well_harness/knowledge_capture.py:150:        "residual_risk": residual_risk or "",
src/well_harness/knowledge_capture.py:185:    residual_risk: str | None = None,
src/well_harness/knowledge_capture.py:201:        residual_risk=residual_risk,
src/well_harness/knowledge_capture.py:214:        "residual_risk": residual_risk or "",
tests/e2e/test_wow_a_causal_chain.py:6:observable is /api/lever-snapshot.
tests/e2e/test_wow_a_causal_chain.py:27:#           feedback_mode='auto_scrubber' the server-side canonical pullback
tests/e2e/test_wow_a_causal_chain.py:30:#           node flips True within a single /api/lever-snapshot call and logic4
tests/e2e/test_wow_a_causal_chain.py:49:    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
tests/e2e/test_wow_a_causal_chain.py:51:BEAT_DEEP_PAYLOAD = {
tests/e2e/test_wow_a_causal_chain.py:55:    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
tests/e2e/test_wow_a_causal_chain.py:66:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:80:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:95:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_EARLY_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:109:    plant VDT reach 90%"), feedback_mode='auto_scrubber' with tra_deg below
tests/e2e/test_wow_a_causal_chain.py:111:    ~4.4s of simulated time. Inside a single /api/lever-snapshot call the
tests/e2e/test_wow_a_causal_chain.py:121:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:138:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_BLOCKED_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:150:    status1, body1 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:151:    status2, body2 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:162:    api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)  # warmup
tests/e2e/test_wow_a_causal_chain.py:164:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:173:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
src/well_harness/second_system_smoke.py:206:        residual_risk=DEFAULT_RESIDUAL_RISK,
src/well_harness/second_system_smoke.py:272:        residual_risk=DEFAULT_RESIDUAL_RISK,
src/well_harness/two_system_runtime_comparison.py:113:        residual_risk=DEFAULT_RESIDUAL_RISK,
tests/e2e/fixtures/schema_snapshot.json:8:    "path": "/api/lever-snapshot",
tests/e2e/fixtures/schema_snapshot.json:16:    "path": "/api/monte-carlo/run",
tests/e2e/fixtures/schema_snapshot.json:25:    "path": "/api/diagnosis/run",
tests/e2e/fixtures/schema_snapshot.json:27:    "top_keys": ["grid_resolution", "outcome", "results", "timestamp", "total_combos_found"],
tests/e2e/fixtures/schema_snapshot.json:28:    "valid_outcomes": ["logic3_active", "logic1_active", "thr_lock_active", "deploy_confirmed", "tls_unlocked", "pls_unlocked"],
tests/e2e/test_wow_c_reverse_diagnose.py:3:Locks /api/diagnosis/run contract: valid outcome returns a list of parameter
tests/e2e/test_wow_c_reverse_diagnose.py:15:    "deploy_confirmed", "tls_unlocked", "pls_unlocked",
tests/e2e/test_wow_c_reverse_diagnose.py:27:def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:28:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:30:        "outcome": "deploy_confirmed",
tests/e2e/test_wow_c_reverse_diagnose.py:35:    assert body["outcome"] == "deploy_confirmed"
tests/e2e/test_wow_c_reverse_diagnose.py:36:    assert body["total_combos_found"] >= 1
tests/e2e/test_wow_c_reverse_diagnose.py:43:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:45:        "outcome": "deploy_confirmed",
tests/e2e/test_wow_c_reverse_diagnose.py:57:    """grid_resolution + timestamp must be present (audit trail for rehearsal)."""
tests/e2e/test_wow_c_reverse_diagnose.py:58:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:63:    assert "grid_resolution" in body
tests/e2e/test_wow_c_reverse_diagnose.py:64:    assert isinstance(body["grid_resolution"], int)
tests/e2e/test_wow_c_reverse_diagnose.py:65:    assert body["grid_resolution"] > 0
tests/e2e/test_wow_c_reverse_diagnose.py:73:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:84:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:98:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:107:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:109:        "outcome": "deploy_confirmed",
src/well_harness/system_spec.py:584:            "residual_risk",
tests/e2e/conftest.py:4:/api/lever-snapshot responds, then yields a base_url to the tests.
tests/e2e/conftest.py:41:        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
tests/e2e/conftest.py:47:            c.request("POST", "/api/lever-snapshot", body=probe_payload,
src/well_harness/workbench_bundle.py:548:    residual_risk: str | None = None,
src/well_harness/workbench_bundle.py:596:            residual_risk=residual_risk,
src/well_harness/demo_server.py:91:DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
src/well_harness/demo_server.py:93:MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
src/well_harness/demo_server.py:98:# The existing /api/lever-snapshot stays stateless; this triad is separate
src/well_harness/demo_server.py:117:    "deploy_confirmed",
src/well_harness/demo_server.py:125:        "deploy_confirmed",
src/well_harness/demo_server.py:280:            "/api/lever-snapshot",
src/well_harness/demo_server.py:325:        if parsed.path == "/api/lever-snapshot":
src/well_harness/demo_server.py:358:            # that bypasses the /api/lever-snapshot sign-off contract. The
src/well_harness/demo_server.py:363:            # The 409 message explains the alternative (use /api/lever-snapshot
src/well_harness/demo_server.py:375:                            "For authoritative manual feedback, use /api/lever-snapshot "
src/well_harness/demo_server.py:376:                            "with feedback_mode=manual_feedback_override + sign-off."
src/well_harness/demo_server.py:383:                        "residual_risk": (
src/well_harness/demo_server.py:642:def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
src/well_harness/demo_server.py:643:    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
src/well_harness/demo_server.py:647:            "field": "feedback_mode",
src/well_harness/demo_server.py:648:            "message": "feedback_mode must be a string.",
src/well_harness/demo_server.py:654:            "field": "feedback_mode",
src/well_harness/demo_server.py:655:            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
src/well_harness/demo_server.py:661:# When feedback_mode = manual_feedback_override, the request must include
src/well_harness/demo_server.py:666:def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str) -> dict | None:
src/well_harness/demo_server.py:669:    Only enforced when feedback_mode == "manual_feedback_override". For
src/well_harness/demo_server.py:672:    if feedback_mode != "manual_feedback_override":
src/well_harness/demo_server.py:695:            "residual_risk": (
src/well_harness/demo_server.py:1143:    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
src/well_harness/demo_server.py:1146:    lever_inputs["feedback_mode"] = feedback_mode
src/well_harness/demo_server.py:1202:    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
src/well_harness/demo_server.py:1360:    if outcome == "deploy_confirmed":
src/well_harness/demo_server.py:1425:                feedback_mode="manual_feedback_override",
src/well_harness/demo_server.py:1456:            "feedback_mode": "manual_feedback_override",
src/well_harness/demo_server.py:1571:    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
src/well_harness/demo_server.py:1616:            residual_risk=residual_risk,
src/well_harness/demo_server.py:1790:    feedback_mode: str,
src/well_harness/demo_server.py:1834:        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
src/well_harness/demo_server.py:1841:    elif feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:1887:    feedback_mode: str,
src/well_harness/demo_server.py:1950:    if feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:2495:    feedback_mode: str = "auto_scrubber",
src/well_harness/demo_server.py:2512:        feedback_mode=feedback_mode,
src/well_harness/demo_server.py:2526:        feedback_mode=feedback_mode,
src/well_harness/demo_server.py:2613:    summary = _lever_summary(effective_tra, inputs, sensors, outputs, explain, feedback_mode, tra_lock)
src/well_harness/demo_server.py:2616:        if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2623:            if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2638:            "feedback_mode": feedback_mode,
src/well_harness/demo_server.py:2662:            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
src/well_harness/demo_server.py:2663:            "feedback_mode": feedback_mode,
src/well_harness/fantui_tick.py:9:the C919 panel's stateful console. The stateless ``/api/lever-snapshot``
src/well_harness/reference_packets/custom_reverse_control_v1.json:159:      "residual_risk"
src/well_harness/reverse_diagnosis.py:30:    "deploy_confirmed",    # VDT >= 90% AND thr_lock active
src/well_harness/reverse_diagnosis.py:145:                            elif outcome == "deploy_confirmed":
src/well_harness/reverse_diagnosis.py:190:                "total_combos_found": len(results),
src/well_harness/reverse_diagnosis.py:191:                "grid_resolution": _GRID_RESOLUTION,
src/well_harness/reverse_diagnosis.py:201:            "total_combos_found": len(results),
src/well_harness/reverse_diagnosis.py:202:            "grid_resolution": _GRID_RESOLUTION,
src/well_harness/cli.py:726:            residual_risk=args.residual_risk,
src/well_harness/cli.py:749:                residual_risk=args.residual_risk,
src/well_harness/tools/specs/reference_thrust_reverser.spec.json:427:      "residual_risk"
src/well_harness/document_intake.py:262:            "resolution_fields": ["confirmed_root_cause", "repair_action", "validation_after_fix", "residual_risk"],
src/well_harness/adapters/c919_etras_adapter.py:1188:                "residual_risk",
src/well_harness/adapters/bleed_air_adapter.py:507:                "residual_risk",
src/well_harness/adapters/landing_gear_adapter.py:305:            optimization_fields=("residual_risk", "follow_up_monitoring"),

exec
/bin/zsh -lc 'nl -ba tests/e2e/test_wow_a_causal_chain.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E2E Wow A — causal chain via truth engine (no LLM dependency).
     2	
     3	The wow-A story is: given lever inputs that satisfy all deploy preconditions,
     4	the truth engine produces a coherent activated chain (logic1 → logic2 → logic3
     5	→ logic4 → thr_lock) over 19 nodes. LLM only narrates; the contract-bearing
     6	observable is /api/lever-snapshot.
     7	
     8	These tests pin the truth-engine contract end-to-end against a live
     9	demo_server on :8799, independent of any MiniMax availability.
    10	"""
    11	from __future__ import annotations
    12	
    13	import time
    14	
    15	import pytest
    16	
    17	EXPECTED_LOGIC_KEYS = {"logic1", "logic2", "logic3", "logic4"}
    18	EXPECTED_NODE_COUNT = 19
    19	
    20	# Domain semantics (probed from live demo_server post-a46e4e6 / 2ded020):
    21	#   logic1 = landing-regime detector: RA < threshold AND on_ground AND NOT inhibited
    22	#            AND reverser_not_deployed_eec; the last condition flips False once the
    23	#            plant fully deploys, so logic1 may de-activate during BEAT_DEEP.
    24	#   logic2 = TLS-unlock confirmation
    25	#   logic3 = deep-reverse commit: TRA crossed lock threshold AND logic2 AND SW2 closed
    26	#   logic4 = deploy-confirmed feedback: requires deploy_90_percent_vdt. Under
    27	#           feedback_mode='auto_scrubber' the server-side canonical pullback
    28	#           (demo_server._canonical_pullback_sequence, extended in commit a46e4e6)
    29	#           holds the lever long enough for plant VDT to reach 100%, so the feedback
    30	#           node flips True within a single /api/lever-snapshot call and logic4
    31	#           latches. Under manual_feedback_override mode, logic4 activates only when
    32	#           the caller supplies deploy_position_percent ≥ 90.
    33	#
    34	# Therefore wow-A locks what auto_scrubber delivers from a single POST:
    35	#   - BEAT_EARLY   (tra_deg=-5)  → logic1 + logic2 active; TRA never crosses the
    36	#                                  L3 threshold, so the plant remains at 0%
    37	#                                  deploy and logic3/4 remain inactive.
    38	#   - BEAT_DEEP    (tra_deg=-35) → logic2 + logic3 + logic4 active; the extended
    39	#                                  canonical pullback runs the plant to 100%
    40	#                                  deploy within ~4.4s, latching the full chain.
    41	#                                  logic1 de-activates as reverser_not_deployed_eec
    42	#                                  flips False mid-deploy.
    43	#   - BEAT_BLOCKED (airborne)   → all four inactive (chain broken at logic1).
    44	# These three beats together form the demo's causal-chain narrative.
    45	BEAT_EARLY_PAYLOAD = {
    46	    "tra_deg": -5, "radio_altitude_ft": 2,
    47	    "engine_running": True, "aircraft_on_ground": True,
    48	    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.8,
    49	    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
    50	}
    51	BEAT_DEEP_PAYLOAD = {
    52	    "tra_deg": -35, "radio_altitude_ft": 2,
    53	    "engine_running": True, "aircraft_on_ground": True,
    54	    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.92,
    55	    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
    56	}
    57	BEAT_BLOCKED_PAYLOAD = {
    58	    **BEAT_EARLY_PAYLOAD,
    59	    "radio_altitude_ft": 500,
    60	    "aircraft_on_ground": False,
    61	}
    62	
    63	
    64	@pytest.mark.e2e
    65	def test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields(demo_server, api_post):
    66	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    67	    assert status == 200
    68	    assert isinstance(body, dict)
    69	    assert "nodes" in body and isinstance(body["nodes"], list)
    70	    assert len(body["nodes"]) == EXPECTED_NODE_COUNT
    71	    for node in body["nodes"]:
    72	        assert isinstance(node, dict)
    73	        assert set(node.keys()) >= {"id", "state"}
    74	        assert isinstance(node["id"], str) and node["id"]
    75	        assert isinstance(node["state"], str)
    76	
    77	
    78	@pytest.mark.e2e
    79	def test_wow_a_lever_snapshot_exposes_four_logic_gates(demo_server, api_post):
    80	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    81	    assert status == 200
    82	    assert "logic" in body
    83	    logic = body["logic"]
    84	    assert isinstance(logic, dict)
    85	    assert set(logic.keys()) == EXPECTED_LOGIC_KEYS
    86	    for key, gate in logic.items():
    87	        assert isinstance(gate, dict), f"{key} must be a dict"
    88	        assert "active" in gate, f"{key} missing 'active'"
    89	        assert isinstance(gate["active"], bool), f"{key}.active must be bool"
    90	
    91	
    92	@pytest.mark.e2e
    93	def test_wow_a_beat_early_activates_logic1_and_logic2_only(demo_server, api_post):
    94	    """Demo beat 1: shallow TRA + landing → logic1 + logic2 active, 3/4 pending."""
    95	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_EARLY_PAYLOAD)
    96	    assert status == 200
    97	    logic = body["logic"]
    98	    active = {k for k, v in logic.items() if v.get("active") is True}
    99	    assert active == {"logic1", "logic2"}, (
   100	        f"BEAT_EARLY should activate exactly logic1+logic2, got {active}"
   101	    )
   102	
   103	
   104	@pytest.mark.e2e
   105	def test_wow_a_beat_deep_activates_logic2_and_logic3(demo_server, api_post):
   106	    """Demo beat 2: deep reverse under auto_scrubber drives the full chain.
   107	
   108	    Per commit a46e4e6 ("fix(scrubber): extend canonical pullback hold to let
   109	    plant VDT reach 90%"), feedback_mode='auto_scrubber' with tra_deg below
   110	    logic3_tra_deg_threshold runs the in-server plant to 100% deploy within
   111	    ~4.4s of simulated time. Inside a single /api/lever-snapshot call the
   112	    feedback node deploy_90_percent_vdt flips True and logic4 latches.
   113	
   114	    Test name retained for stability; the locked invariants are now:
   115	      (a) at least logic2 + logic3 are active (deep-reverse commit), and
   116	      (b) logic4 is also active under auto_scrubber (post-a46e4e6 reality).
   117	    The "single POST cannot activate logic4 without feedback" invariant is
   118	    a manual-mode concern; see manual_feedback_override path with
   119	    deploy_position_percent < 90 to probe it.
   120	    """
   121	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
   122	    assert status == 200
   123	    logic = body["logic"]
   124	    active = {k for k, v in logic.items() if v.get("active") is True}
   125	    assert {"logic2", "logic3"} <= active, (
   126	        f"BEAT_DEEP should at least activate logic2+logic3, got {active}"
   127	    )
   128	    assert logic["logic4"].get("active") is True, (
   129	        "logic4 must activate under auto_scrubber's extended canonical pullback "
   130	        "(plant VDT reaches 100% within the lever-snapshot window — see "
   131	        "demo_server._canonical_pullback_sequence and commit a46e4e6)"
   132	    )
   133	
   134	
   135	@pytest.mark.e2e
   136	def test_wow_a_beat_blocked_deactivates_entire_chain(demo_server, api_post):
   137	    """Demo beat 3 (negative control): airborne → entire chain inactive."""
   138	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_BLOCKED_PAYLOAD)
   139	    assert status == 200
   140	    logic = body["logic"]
   141	    active = {k for k, v in logic.items() if v.get("active") is True}
   142	    assert active == set(), (
   143	        f"BEAT_BLOCKED (airborne) should deactivate every gate, got active={active}"
   144	    )
   145	
   146	
   147	@pytest.mark.e2e
   148	def test_wow_a_truth_engine_is_deterministic(demo_server, api_post):
   149	    """Same lever inputs → byte-identical logic dict across two calls."""
   150	    status1, body1 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
   151	    status2, body2 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
   152	    assert status1 == 200 and status2 == 200
   153	    assert body1["logic"] == body2["logic"]
   154	    node_state_1 = {n["id"]: n["state"] for n in body1["nodes"]}
   155	    node_state_2 = {n["id"]: n["state"] for n in body2["nodes"]}
   156	    assert node_state_1 == node_state_2
   157	
   158	
   159	@pytest.mark.e2e
   160	def test_wow_a_response_under_500ms_warm(demo_server, api_post):
   161	    """Rehearsal budget: truth engine must return in <500ms after warmup."""
   162	    api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)  # warmup
   163	    t0 = time.monotonic()
   164	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
   165	    elapsed_ms = (time.monotonic() - t0) * 1000
   166	    assert status == 200
   167	    assert elapsed_ms < 500, f"lever-snapshot took {elapsed_ms:.0f}ms (budget 500ms)"
   168	
   169	
   170	@pytest.mark.e2e
   171	def test_wow_a_lever_snapshot_evidence_field_present(demo_server, api_post):
   172	    """Evidence is the LLM-facing narrative source; must exist for wow A narration."""
   173	    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
   174	    assert status == 200
   175	    assert "evidence" in body
   176	    assert "plant_state" in body
   177	    assert "outputs" in body

exec
/bin/zsh -lc 'nl -ba tests/e2e/test_wow_b_monte_carlo.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E2E Wow B — Monte Carlo reliability simulation.
     2	
     3	Locks the observable contract of /api/monte-carlo/run against a live
     4	demo_server on :8799: return shape, value ranges, timing budget, and
     5	deterministic seeding.
     6	"""
     7	from __future__ import annotations
     8	
     9	import time
    10	
    11	import pytest
    12	
    13	EXPECTED_TOP_KEYS = {
    14	    "n_trials", "n_failures", "success_rate",
    15	    "mean_cycles_to_failure", "mtbf_cycles", "seed",
    16	    "failure_modes", "sw1_window_crossings_mean", "sw2_window_crossings_mean",
    17	}
    18	
    19	# From src/well_harness/monte_carlo_engine.py failure-mode enum
    20	EXPECTED_FAILURE_MODE_KEYS = {
    21	    "ra_sensor_failure", "sw1_missed", "sw2_missed", "tra_stall",
    22	}
    23	
    24	
    25	def _run(api_post, base_url, n_trials, seed=42):
    26	    return api_post(base_url, "/api/monte-carlo/run",
    27	                    {"system_id": "thrust-reverser", "n_trials": n_trials, "seed": seed})
    28	
    29	
    30	@pytest.mark.e2e
    31	def test_wow_b_monte_carlo_returns_contract_shape(demo_server, api_post):
    32	    status, body = _run(api_post, demo_server, 1000)
    33	    assert status == 200
    34	    assert isinstance(body, dict)
    35	    missing = EXPECTED_TOP_KEYS - set(body.keys())
    36	    assert not missing, f"monte-carlo response missing keys: {missing}"
    37	
    38	
    39	@pytest.mark.e2e
    40	def test_wow_b_10k_trials_under_5s(demo_server, api_post):
    41	    """Rehearsal budget: 10k iters must complete well inside the demo window."""
    42	    t0 = time.monotonic()
    43	    status, body = _run(api_post, demo_server, 10000)
    44	    elapsed = time.monotonic() - t0
    45	    assert status == 200
    46	    assert elapsed < 5.0, f"10k MC took {elapsed:.2f}s (budget 5s)"
    47	    assert body["n_trials"] == 10000
    48	
    49	
    50	@pytest.mark.e2e
    51	def test_wow_b_success_rate_in_unit_interval(demo_server, api_post):
    52	    status, body = _run(api_post, demo_server, 2000)
    53	    assert status == 200
    54	    sr = body["success_rate"]
    55	    assert isinstance(sr, (int, float))
    56	    assert 0.0 <= sr <= 1.0, f"success_rate={sr} not in [0,1]"
    57	    # Consistency: n_failures + successes = n_trials
    58	    assert body["n_failures"] + round(sr * body["n_trials"]) == body["n_trials"] or \
    59	           abs(body["n_failures"] - (1 - sr) * body["n_trials"]) < 1
    60	
    61	
    62	@pytest.mark.e2e
    63	def test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys(demo_server, api_post):
    64	    status, body = _run(api_post, demo_server, 5000)
    65	    assert status == 200
    66	    modes = body["failure_modes"]
    67	    assert isinstance(modes, dict) and modes
    68	    assert set(modes.keys()) == EXPECTED_FAILURE_MODE_KEYS, (
    69	        f"failure_modes keys changed: {set(modes.keys())}"
    70	    )
    71	    for k, v in modes.items():
    72	        assert isinstance(v, (int, float)), f"{k} must be numeric, got {type(v).__name__}"
    73	        assert v >= 0, f"{k}={v} negative"
    74	
    75	
    76	@pytest.mark.e2e
    77	def test_wow_b_is_deterministic_under_fixed_seed(demo_server, api_post):
    78	    """Same seed → byte-identical body (critical for rehearsal repeatability)."""
    79	    s1, b1 = _run(api_post, demo_server, 1000, seed=42)
    80	    s2, b2 = _run(api_post, demo_server, 1000, seed=42)
    81	    assert s1 == 200 and s2 == 200
    82	    assert b1 == b2, "Monte Carlo must be deterministic under fixed seed"
    83	
    84	
    85	@pytest.mark.e2e
    86	def test_wow_b_n_trials_zero_is_clamped_to_min(demo_server, api_post):
    87	    """Known clamp behavior: n_trials=0 is auto-clamped to 1 (graceful, not 400).
    88	
    89	    If this changes (e.g. strict 400), update P20.1 contract layer.
    90	    """
    91	    status, body = _run(api_post, demo_server, 0)
    92	    assert status == 200
    93	    assert body["n_trials"] >= 1
    94	
    95	
    96	@pytest.mark.e2e
    97	def test_wow_b_n_trials_overflow_is_clamped_to_max(demo_server, api_post):
    98	    status, body = _run(api_post, demo_server, 1_500_000)
    99	    assert status == 200
   100	    assert body["n_trials"] <= 10000

exec
/bin/zsh -lc 'nl -ba tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E2E Wow C — reverse diagnosis parameter-combination search.
     2	
     3	Locks /api/diagnosis/run contract: valid outcome returns a list of parameter
     4	snapshots that satisfy the target, invalid outcome returns a structured 400.
     5	
     6	Note: The current response shape does NOT include probabilities or
     7	suggested_action fields. Those are candidates for P20.1 contract expansion.
     8	"""
     9	from __future__ import annotations
    10	
    11	import pytest
    12	
    13	VALID_OUTCOMES = {
    14	    "logic3_active", "logic1_active", "thr_lock_active",
    15	    "deploy_confirmed", "tls_unlocked", "pls_unlocked",
    16	}
    17	
    18	# Keys guaranteed by ParameterSnapshot dataclass in reverse_diagnosis.py
    19	EXPECTED_RESULT_KEYS = {
    20	    "radio_altitude_ft", "tra_deg",
    21	    "sw1_closed", "sw2_closed",
    22	    "tls_unlocked", "pls_unlocked",
    23	}
    24	
    25	
    26	@pytest.mark.e2e
    27	def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
    28	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    29	        "system_id": "thrust-reverser",
    30	        "outcome": "deploy_confirmed",
    31	        "max_results": 10,
    32	    })
    33	    assert status == 200
    34	    assert isinstance(body, dict)
    35	    assert body["outcome"] == "deploy_confirmed"
    36	    assert body["total_combos_found"] >= 1
    37	    assert isinstance(body["results"], list) and len(body["results"]) >= 1
    38	    assert len(body["results"]) <= 10
    39	
    40	
    41	@pytest.mark.e2e
    42	def test_wow_c_each_result_carries_required_parameter_keys(demo_server, api_post):
    43	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    44	        "system_id": "thrust-reverser",
    45	        "outcome": "deploy_confirmed",
    46	        "max_results": 5,
    47	    })
    48	    assert status == 200
    49	    for idx, snap in enumerate(body["results"]):
    50	        assert isinstance(snap, dict), f"result[{idx}] must be a dict"
    51	        missing = EXPECTED_RESULT_KEYS - set(snap.keys())
    52	        assert not missing, f"result[{idx}] missing keys: {missing}"
    53	
    54	
    55	@pytest.mark.e2e
    56	def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
    57	    """grid_resolution + timestamp must be present (audit trail for rehearsal)."""
    58	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    59	        "system_id": "thrust-reverser",
    60	        "outcome": "logic3_active",
    61	    })
    62	    assert status == 200
    63	    assert "grid_resolution" in body
    64	    assert isinstance(body["grid_resolution"], int)
    65	    assert body["grid_resolution"] > 0
    66	    assert "timestamp" in body and isinstance(body["timestamp"], str)
    67	
    68	
    69	@pytest.mark.e2e
    70	@pytest.mark.parametrize("outcome", sorted(VALID_OUTCOMES))
    71	def test_wow_c_all_valid_outcomes_return_200(demo_server, api_post, outcome):
    72	    """Every documented outcome must be reachable (no regression in enum coverage)."""
    73	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    74	        "system_id": "thrust-reverser",
    75	        "outcome": outcome,
    76	        "max_results": 1,
    77	    })
    78	    assert status == 200
    79	    assert body["outcome"] == outcome
    80	
    81	
    82	@pytest.mark.e2e
    83	def test_wow_c_invalid_outcome_returns_structured_400(demo_server, api_post):
    84	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    85	        "system_id": "thrust-reverser",
    86	        "outcome": "banana_outcome",
    87	    })
    88	    assert status == 400
    89	    assert isinstance(body, dict) and "error" in body
    90	    assert "Invalid outcome" in body["error"]
    91	    # Error message must name the valid set so operators can self-recover.
    92	    for valid in VALID_OUTCOMES:
    93	        assert valid in body["error"]
    94	
    95	
    96	@pytest.mark.e2e
    97	def test_wow_c_missing_outcome_returns_400(demo_server, api_post):
    98	    status, body = api_post(demo_server, "/api/diagnosis/run", {
    99	        "system_id": "thrust-reverser",
   100	    })
   101	    assert status == 400
   102	    assert isinstance(body, dict) and "error" in body
   103	
   104	
   105	@pytest.mark.e2e
   106	def test_wow_c_max_results_bound_is_respected(demo_server, api_post):
   107	    status, body = api_post(demo_server, "/api/diagnosis/run", {
   108	        "system_id": "thrust-reverser",
   109	        "outcome": "deploy_confirmed",
   110	        "max_results": 3,
   111	    })
   112	    assert status == 200
   113	    assert len(body["results"]) <= 3

exec
/bin/zsh -lc 'rg -n "def do_POST|/api/lever-snapshot|/api/monte-carlo/run|/api/diagnosis/run|Diagnosis|Monte|lever-snapshot|residual_risk|auto_scrubber|manual_feedback_override|truth_engine" src/well_harness/demo_server.py src/well_harness/*.py src/well_harness/*/*.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/cli.py:726:            residual_risk=args.residual_risk,
src/well_harness/cli.py:749:                residual_risk=args.residual_risk,
src/well_harness/models.py:288:class LogicTransitionDiagnosis:
src/well_harness/models.py:370:    def logic_transition_diagnostics(self, logic_name: str | None = None) -> List[LogicTransitionDiagnosis]:
src/well_harness/models.py:372:        diagnostics: List[LogicTransitionDiagnosis] = []
src/well_harness/models.py:382:                    LogicTransitionDiagnosis(
src/well_harness/knowledge_capture.py:10:    FaultDiagnosisReport,
src/well_harness/knowledge_capture.py:34:    diagnosis_report: FaultDiagnosisReport
src/well_harness/knowledge_capture.py:80:    residual_risk: str | None,
src/well_harness/knowledge_capture.py:88:            residual_risk,
src/well_harness/knowledge_capture.py:95:def _default_reliability_hypothesis(report: FaultDiagnosisReport) -> str:
src/well_harness/knowledge_capture.py:103:def _default_guardrail_note(report: FaultDiagnosisReport) -> str:
src/well_harness/knowledge_capture.py:121:    residual_risk: str | None = None,
src/well_harness/knowledge_capture.py:137:        residual_risk=residual_risk,
src/well_harness/knowledge_capture.py:150:        "residual_risk": residual_risk or "",
src/well_harness/knowledge_capture.py:185:    residual_risk: str | None = None,
src/well_harness/knowledge_capture.py:201:        residual_risk=residual_risk,
src/well_harness/knowledge_capture.py:214:        "residual_risk": residual_risk or "",
src/well_harness/demo_server.py:91:DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
src/well_harness/demo_server.py:92:# Monte Carlo reliability API (P19.7)
src/well_harness/demo_server.py:93:MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
src/well_harness/demo_server.py:98:# The existing /api/lever-snapshot stays stateless; this triad is separate
src/well_harness/demo_server.py:159:    "auto_scrubber",
src/well_harness/demo_server.py:160:    "manual_feedback_override",
src/well_harness/demo_server.py:276:    def do_POST(self):
src/well_harness/demo_server.py:280:            "/api/lever-snapshot",
src/well_harness/demo_server.py:325:        if parsed.path == "/api/lever-snapshot":
src/well_harness/demo_server.py:358:            # that bypasses the /api/lever-snapshot sign-off contract. The
src/well_harness/demo_server.py:363:            # The 409 message explains the alternative (use /api/lever-snapshot
src/well_harness/demo_server.py:373:                            "manual_feedback_override authority chain. To use it from "
src/well_harness/demo_server.py:375:                            "For authoritative manual feedback, use /api/lever-snapshot "
src/well_harness/demo_server.py:376:                            "with feedback_mode=manual_feedback_override + sign-off."
src/well_harness/demo_server.py:383:                        "residual_risk": (
src/well_harness/demo_server.py:443:            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
src/well_harness/demo_server.py:462:                engine = ReverseDiagnosisEngine(yaml_path)
src/well_harness/demo_server.py:469:        # P19.7: Monte Carlo reliability simulation
src/well_harness/demo_server.py:471:            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
src/well_harness/demo_server.py:491:                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
src/well_harness/demo_server.py:497:                engine = MonteCarloEngine(yaml_path)
src/well_harness/demo_server.py:643:    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
src/well_harness/demo_server.py:655:            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
src/well_harness/demo_server.py:660:# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
src/well_harness/demo_server.py:661:# When feedback_mode = manual_feedback_override, the request must include
src/well_harness/demo_server.py:669:    Only enforced when feedback_mode == "manual_feedback_override". For
src/well_harness/demo_server.py:670:    auto_scrubber, this returns None unconditionally (no extra fields needed).
src/well_harness/demo_server.py:672:    if feedback_mode != "manual_feedback_override":
src/well_harness/demo_server.py:686:                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
src/well_harness/demo_server.py:687:                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
src/well_harness/demo_server.py:695:            "residual_risk": (
src/well_harness/demo_server.py:703:        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
src/well_harness/demo_server.py:705:        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
src/well_harness/demo_server.py:710:            "manual_feedback_override requires a manual_override_signoff object.",
src/well_harness/demo_server.py:1200:    # auto_scrubber; returns 409 payload with `_status` hint when signoff
src/well_harness/demo_server.py:1201:    # missing/invalid for manual_feedback_override.
src/well_harness/demo_server.py:1425:                feedback_mode="manual_feedback_override",
src/well_harness/demo_server.py:1456:            "feedback_mode": "manual_feedback_override",
src/well_harness/demo_server.py:1571:    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
src/well_harness/demo_server.py:1616:            residual_risk=residual_risk,
src/well_harness/demo_server.py:1725:    deploy rate. Without this, auto_scrubber shows L4 permanently blocked on
src/well_harness/demo_server.py:1834:        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
src/well_harness/demo_server.py:1841:    elif feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:1950:    if feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:2495:    feedback_mode: str = "auto_scrubber",
src/well_harness/demo_server.py:2616:        if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2623:            if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2624:            else "manual_feedback_override"
src/well_harness/demo_server.py:2662:            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
src/well_harness/monte_carlo_engine.py:2:Monte Carlo reliability simulation engine for thrust-reverser system.
src/well_harness/monte_carlo_engine.py:29:    """Output of a Monte Carlo reliability simulation run."""
src/well_harness/monte_carlo_engine.py:63:class MonteCarloEngine:
src/well_harness/monte_carlo_engine.py:65:    Monte Carlo simulation engine for thrust-reverser reliability analysis.
src/well_harness/monte_carlo_engine.py:88:        Run Monte Carlo simulation for n_trials deployment cycles.
src/well_harness/monte_carlo_engine.py:91:            n_trials: Number of Monte Carlo trials to run.
src/well_harness/system_spec.py:584:            "residual_risk",
src/well_harness/demo_server.py:91:DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
src/well_harness/demo_server.py:92:# Monte Carlo reliability API (P19.7)
src/well_harness/demo_server.py:93:MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
src/well_harness/demo_server.py:98:# The existing /api/lever-snapshot stays stateless; this triad is separate
src/well_harness/demo_server.py:159:    "auto_scrubber",
src/well_harness/demo_server.py:160:    "manual_feedback_override",
src/well_harness/demo_server.py:276:    def do_POST(self):
src/well_harness/demo_server.py:280:            "/api/lever-snapshot",
src/well_harness/demo_server.py:325:        if parsed.path == "/api/lever-snapshot":
src/well_harness/demo_server.py:358:            # that bypasses the /api/lever-snapshot sign-off contract. The
src/well_harness/demo_server.py:363:            # The 409 message explains the alternative (use /api/lever-snapshot
src/well_harness/demo_server.py:373:                            "manual_feedback_override authority chain. To use it from "
src/well_harness/demo_server.py:375:                            "For authoritative manual feedback, use /api/lever-snapshot "
src/well_harness/demo_server.py:376:                            "with feedback_mode=manual_feedback_override + sign-off."
src/well_harness/demo_server.py:383:                        "residual_risk": (
src/well_harness/demo_server.py:443:            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
src/well_harness/demo_server.py:462:                engine = ReverseDiagnosisEngine(yaml_path)
src/well_harness/demo_server.py:469:        # P19.7: Monte Carlo reliability simulation
src/well_harness/demo_server.py:471:            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
src/well_harness/demo_server.py:491:                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
src/well_harness/demo_server.py:497:                engine = MonteCarloEngine(yaml_path)
src/well_harness/demo_server.py:643:    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
src/well_harness/demo_server.py:655:            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
src/well_harness/demo_server.py:660:# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
src/well_harness/demo_server.py:661:# When feedback_mode = manual_feedback_override, the request must include
src/well_harness/demo_server.py:669:    Only enforced when feedback_mode == "manual_feedback_override". For
src/well_harness/demo_server.py:670:    auto_scrubber, this returns None unconditionally (no extra fields needed).
src/well_harness/demo_server.py:672:    if feedback_mode != "manual_feedback_override":
src/well_harness/demo_server.py:686:                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
src/well_harness/demo_server.py:687:                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
src/well_harness/demo_server.py:695:            "residual_risk": (
src/well_harness/demo_server.py:703:        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
src/well_harness/demo_server.py:705:        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
src/well_harness/demo_server.py:710:            "manual_feedback_override requires a manual_override_signoff object.",
src/well_harness/demo_server.py:1200:    # auto_scrubber; returns 409 payload with `_status` hint when signoff
src/well_harness/demo_server.py:1201:    # missing/invalid for manual_feedback_override.
src/well_harness/demo_server.py:1425:                feedback_mode="manual_feedback_override",
src/well_harness/demo_server.py:1456:            "feedback_mode": "manual_feedback_override",
src/well_harness/demo_server.py:1571:    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
src/well_harness/demo_server.py:1616:            residual_risk=residual_risk,
src/well_harness/demo_server.py:1725:    deploy rate. Without this, auto_scrubber shows L4 permanently blocked on
src/well_harness/demo_server.py:1834:        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
src/well_harness/demo_server.py:1841:    elif feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:1950:    if feedback_mode == "manual_feedback_override":
src/well_harness/demo_server.py:2495:    feedback_mode: str = "auto_scrubber",
src/well_harness/demo_server.py:2616:        if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2623:            if feedback_mode == "auto_scrubber"
src/well_harness/demo_server.py:2624:            else "manual_feedback_override"
src/well_harness/demo_server.py:2662:            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
src/well_harness/workbench_bundle.py:17:    FaultDiagnosisReport,
src/well_harness/workbench_bundle.py:72:    fault_diagnosis_report: FaultDiagnosisReport | None = None
src/well_harness/workbench_bundle.py:548:    residual_risk: str | None = None,
src/well_harness/workbench_bundle.py:596:            residual_risk=residual_risk,
src/well_harness/workbench_bundle.py:739:                "## Fault Diagnosis",
src/well_harness/adapters/bleed_air_adapter.py:507:                "residual_risk",
src/well_harness/fantui_tick.py:9:the C919 panel's stateful console. The stateless ``/api/lever-snapshot``
src/well_harness/document_intake.py:262:            "resolution_fields": ["confirmed_root_cause", "repair_action", "validation_after_fix", "residual_risk"],
src/well_harness/fault_diagnosis.py:34:class FaultDiagnosisReport:
src/well_harness/fault_diagnosis.py:58:def fault_diagnosis_report_to_dict(report: FaultDiagnosisReport) -> dict[str, Any]:
src/well_harness/fault_diagnosis.py:248:) -> FaultDiagnosisReport:
src/well_harness/fault_diagnosis.py:303:    return FaultDiagnosisReport(
src/well_harness/fault_diagnosis.py:333:) -> FaultDiagnosisReport:
src/well_harness/fault_diagnosis.py:348:) -> FaultDiagnosisReport:
src/well_harness/fault_diagnosis.py:357:def render_fault_diagnosis_text(report: FaultDiagnosisReport) -> str:
src/well_harness/reverse_diagnosis.py:60:class ReverseDiagnosisEngine:
src/well_harness/two_system_runtime_comparison.py:113:        residual_risk=DEFAULT_RESIDUAL_RISK,
src/well_harness/static/adversarial_test.py:15:# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
src/well_harness/static/adversarial_test.py:16:# manual_override_signoff when feedback_mode = manual_feedback_override.
src/well_harness/static/adversarial_test.py:18:# using manual_feedback_override so the truth-engine resilience tests (which
src/well_harness/static/adversarial_test.py:37:    if isinstance(payload, dict) and payload.get("feedback_mode") == "manual_feedback_override":
src/well_harness/static/adversarial_test.py:73:    snap = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:79:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:111:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:114:    outputs = [api("/api/lever-snapshot", base_payload) for _ in range(5)]
src/well_harness/static/adversarial_test.py:124:    snap0 = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:130:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:136:    snap1 = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:142:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:154:    snap2 = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:160:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:179:        snap_t = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:185:            "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:202:        snap_v = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:208:            "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:237:            "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:240:        snap_i = api("/api/lever-snapshot", p)
src/well_harness/static/adversarial_test.py:270:    snap = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:276:        "feedback_mode": "manual_feedback_override",
src/well_harness/static/adversarial_test.py:294:    snap = api("/api/lever-snapshot", {
src/well_harness/static/adversarial_test.py:300:        "feedback_mode": "manual_feedback_override",
src/well_harness/demo.py:8:from well_harness.models import FieldChange, HarnessConfig, LogicTransitionDiagnosis, SimulationResult
src/well_harness/demo.py:762:) -> LogicTransitionDiagnosis | None:
src/well_harness/demo.py:838:def _all_context_change_summary(diagnosis: LogicTransitionDiagnosis) -> str:
src/well_harness/demo.py:888:    diagnosis: LogicTransitionDiagnosis | None,
src/well_harness/demo.py:1565:def _changed_condition_summary(diagnosis: LogicTransitionDiagnosis) -> str:
src/well_harness/demo.py:1578:    diagnosis: LogicTransitionDiagnosis,
src/well_harness/second_system_smoke.py:206:        residual_risk=DEFAULT_RESIDUAL_RISK,
src/well_harness/second_system_smoke.py:272:        residual_risk=DEFAULT_RESIDUAL_RISK,
src/well_harness/adapters/c919_etras_adapter.py:1188:                "residual_risk",
src/well_harness/adapters/landing_gear_adapter.py:305:            optimization_fields=("residual_risk", "follow_up_monitoring"),

exec
/bin/zsh -lc "sed -n '443,505p' src/well_harness/demo_server.py | nl -ba -v443" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '325,405p' src/well_harness/demo_server.py | nl -ba -v325" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '660,710p' src/well_harness/demo_server.py | nl -ba -v660" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   443	            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
   444	            outcome = str(request_payload.get("outcome", "")).strip()
   445	            if outcome not in VALID_OUTCOMES:
   446	                self._send_json(400, {
   447	                    "error": f"Invalid outcome: {outcome!r}. "
   448	                             f"Valid: {sorted(VALID_OUTCOMES)}"
   449	                })
   450	                return
   451	            max_results = min(int(request_payload.get("max_results", 1000)), 1000)
   452	            max_results = max(max_results, 0)
   453	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   454	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   455	                self._send_json(400, {
   456	                    "error": f"system_id {system_id!r} is not supported for diagnosis. "
   457	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   458	                })
   459	                return
   460	            yaml_path = self._hardware_yaml_path(system_id)
   461	            try:
   462	                engine = ReverseDiagnosisEngine(yaml_path)
   463	                report = engine.diagnose_and_report(outcome, max_results=max_results)
   464	                self._send_json(200, report)
   465	            except Exception as exc:
   466	                self._send_json(500, {"error": str(exc)})
   467	            return
   468	
   469	        # P19.7: Monte Carlo reliability simulation
   470	        if parsed.path == MONTE_CARLO_RUN_PATH:
   471	            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
   472	            n_trials_raw = request_payload.get("n_trials", 100)
   473	            try:
   474	                n_trials = int(n_trials_raw)
   475	            except (TypeError, ValueError):
   476	                self._send_json(400, {"error": "n_trials must be an integer"})
   477	                return
   478	            n_trials = max(1, min(n_trials, 10000))
   479	
   480	            seed = None
   481	            if "seed" in request_payload:
   482	                try:
   483	                    seed = int(request_payload["seed"])
   484	                except (TypeError, ValueError):
   485	                    self._send_json(400, {"error": "seed must be an integer"})
   486	                    return
   487	
   488	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   489	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   490	                self._send_json(400, {
   491	                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
   492	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   493	                })
   494	                return
   495	            yaml_path = self._hardware_yaml_path(system_id)
   496	            try:
   497	                engine = MonteCarloEngine(yaml_path)
   498	                result = engine.run(n_trials, seed=seed)
   499	                self._send_json(200, _reliability_result_to_dict(result))
   500	            except Exception as exc:
   501	                self._send_json(500, {"error": str(exc)})
   502	            return
   503	
   504	        if parsed.path == SENSITIVITY_SWEEP_PATH:
   505	            response_payload, error_payload = build_sensitivity_sweep_payload(request_payload)

 succeeded in 0ms:
   325	        if parsed.path == "/api/lever-snapshot":
   326	            lever_inputs, error_payload = parse_lever_snapshot_request(request_payload)
   327	            if error_payload is not None:
   328	                # E11-14: parser may attach `_status` (e.g., 409 for manual_override_unsigned);
   329	                # default to 400 for legacy parse errors.
   330	                status_code = error_payload.pop("_status", 400)
   331	                self._send_json(status_code, error_payload)
   332	                return
   333	
   334	            fault_injections = lever_inputs.pop("_fault_injections", None)
   335	            self._send_json(
   336	                200,
   337	                lever_snapshot_payload(
   338	                    **lever_inputs,
   339	                    fault_injections=fault_injections,
   340	                ),
   341	            )
   342	            return
   343	        if parsed.path == "/api/timeline-simulate":
   344	            result = _handle_timeline_simulate(request_payload)
   345	            status = result.pop("_status", 200)
   346	            self._send_json(status, result)
   347	            return
   348	        if parsed.path == FANTUI_TICK_PATH:
   349	            status, result = _handle_fantui_tick(request_payload)
   350	            self._send_json(status, result)
   351	            return
   352	        if parsed.path == FANTUI_RESET_PATH:
   353	            _FANTUI_SYSTEM.reset()
   354	            self._send_json(200, {"ok": True, "t_s": 0.0})
   355	            return
   356	        if parsed.path == FANTUI_SET_VDT_PATH:
   357	            # E11-14 R2 (P2 BLOCKER #2, 2026-04-25): set_vdt is a test probe
   358	            # that bypasses the /api/lever-snapshot sign-off contract. The
   359	            # endpoint stays available for the fan-console debug UI but now
   360	            # requires an explicit `test_probe_acknowledgment` field so a
   361	            # caller cannot accidentally use it to inject manual feedback
   362	            # while believing they're going through the authority chain.
   363	            # The 409 message explains the alternative (use /api/lever-snapshot
   364	            # with sign-off when authority semantics matter).
   365	            ack = request_payload.get("test_probe_acknowledgment")
   366	            if ack is not True:
   367	                self._send_json(
   368	                    409,
   369	                    {
   370	                        "error": "test_probe_unacknowledged",
   371	                        "message": (
   372	                            "/api/fantui/set_vdt is a test probe that bypasses the "
   373	                            "manual_feedback_override authority chain. To use it from "
   374	                            "tests/dev tooling, pass test_probe_acknowledgment=true. "
   375	                            "For authoritative manual feedback, use /api/lever-snapshot "
   376	                            "with feedback_mode=manual_feedback_override + sign-off."
   377	                        ),
   378	                        # E11-14 R3 (P2 R2 IMPORTANT #4 fix, 2026-04-25): every 409
   379	                        # path must disclose the deferred replay/freshness gap so
   380	                        # callers don't mistake structural validation for latched
   381	                        # authorization. set_vdt's bypass nature is itself a live
   382	                        # residual risk surface.
   383	                        "residual_risk": (
   384	                            "Test-probe bypass remains structural; "
   385	                            "test_probe_acknowledgment=true is not authentication. "
   386	                            "Replay/nonce/freshness validation and one-shot latching are "
   387	                            "scoped to E11-16 (approval endpoint hardening)."
   388	                        ),
   389	                    },
   390	                )
   391	                return
   392	            try:
   393	                pct = float(request_payload.get("deploy_position_percent", 0))
   394	            except (TypeError, ValueError):
   395	                self._send_json(400, {"error": "deploy_position_percent must be a number"})
   396	                return
   397	            try:
   398	                _FANTUI_SYSTEM.set_plant_position(pct)
   399	            except ValueError as exc:
   400	                self._send_json(400, {"error": str(exc)})
   401	                return
   402	            self._send_json(200, _FANTUI_SYSTEM.snapshot())
   403	            return
   404	        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
   405	            system_id = request_payload.get("system_id")

 succeeded in 0ms:
   660	# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
   661	# When feedback_mode = manual_feedback_override, the request must include
   662	# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
   663	# the endpoint returns 409 Conflict (paired with E11-13 UI affordance, this
   664	# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
   665	# stays put: no controller / runner / models / adapters/*.py changes.
   666	def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str) -> dict | None:
   667	    """Return error_payload (with `_status` 409) if signoff is missing/invalid; else None.
   668	
   669	    Only enforced when feedback_mode == "manual_feedback_override". For
   670	    auto_scrubber, this returns None unconditionally (no extra fields needed).
   671	    """
   672	    if feedback_mode != "manual_feedback_override":
   673	        return None
   674	
   675	    actor = request_payload.get("actor")
   676	    ticket_id = request_payload.get("ticket_id")
   677	    signoff = request_payload.get("manual_override_signoff")
   678	
   679	    def reject(field: str, message: str) -> dict:
   680	        return {
   681	            "_status": 409,
   682	            "error": "manual_override_unsigned",
   683	            "field": field,
   684	            "message": message,
   685	            "remediation": (
   686	                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
   687	                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   688	            ),
   689	            # E11-14 R2 (P2 IMPORTANT #4, 2026-04-25): residual risk disclosure.
   690	            # The current sign-off check is structural only — same triplet can
   691	            # authorize multiple override payloads (replay) and signed_at is
   692	            # not freshness-checked. One-shot latch / nonce / freshness is the
   693	            # E11-16 approval-endpoint hardening scope. Until E11-16 lands,
   694	            # this guard is "shape correct" not "latched authorization".
   695	            "residual_risk": (
   696	                "Sign-off is structural only. Replay across payloads is not blocked; "
   697	                "signed_at is not freshness-validated. One-shot latch + nonce + "
   698	                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
   699	            ),
   700	        }
   701	
   702	    if not isinstance(actor, str) or not actor.strip():
   703	        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
   704	    if not isinstance(ticket_id, str) or not ticket_id.strip():
   705	        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
   706	
   707	    if not isinstance(signoff, dict):
   708	        return reject(
   709	            "manual_override_signoff",
   710	            "manual_feedback_override requires a manual_override_signoff object.",

exec
/bin/zsh -lc "sed -n '1,120p' src/well_harness/reverse_diagnosis.py | nl -ba -v1" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '188,220p' src/well_harness/reverse_diagnosis.py | nl -ba -v188" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1360,1465p' src/well_harness/demo_server.py | nl -ba -v1360" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   188	            {
   189	                "outcome": outcome,
   190	                "total_combos_found": len(results),
   191	                "grid_resolution": _GRID_RESOLUTION,
   192	                "timestamp": "<ISO-8601>",
   193	                "results": [list of ParameterSnapshot dicts],
   194	            }
   195	        """
   196	        from datetime import datetime, timezone
   197	
   198	        results = self.diagnose(outcome, max_results=max_results)
   199	        return {
   200	            "outcome": outcome,
   201	            "total_combos_found": len(results),
   202	            "grid_resolution": _GRID_RESOLUTION,
   203	            "timestamp": datetime.now(timezone.utc).isoformat(),
   204	            "results": [_parameter_snapshot_to_dict(r) for r in results],
   205	        }
   206	
   207	
   208	# ─── Helpers ──────────────────────────────────────────────────────────────────
   209	
   210	
   211	def _parameter_snapshot_to_dict(snapshot: ParameterSnapshot) -> dict:
   212	    """Convert a ParameterSnapshot to a plain dict for JSON serialization."""
   213	    return {
   214	        "radio_altitude_ft": snapshot.radio_altitude_ft,
   215	        "tra_deg": snapshot.tra_deg,
   216	        "sw1_closed": snapshot.sw1_closed,
   217	        "sw2_closed": snapshot.sw2_closed,
   218	        "tls_unlocked": snapshot.tls_unlocked,
   219	        "pls_unlocked": snapshot.pls_unlocked,
   220	        "vdt_percent": snapshot.vdt_percent,

 succeeded in 0ms:
     1	"""
     2	Reverse diagnosis engine for thrust-reverser system.
     3	
     4	Given a desired outcome (e.g., "logic3_active"), enumerates all parameter
     5	combinations within YAML-defined ranges that satisfy the outcome.
     6	
     7	This is a DIAGNOSIS ANALYZER — it reads hardware YAML and produces enumerated
     8	possibilities. It does NOT call controller.py or affect truth engine behavior.
     9	"""
    10	from __future__ import annotations
    11	
    12	from dataclasses import dataclass
    13	from pathlib import Path
    14	from typing import Optional
    15	
    16	from well_harness.hardware_schema import (
    17	    ThrustReverserHardware,
    18	    load_thrust_reverser_hardware,
    19	)
    20	
    21	
    22	# ─── Constants ─────────────────────────────────────────────────────────────────
    23	
    24	MAX_COMBINATIONS = 1000  # Safety bound to prevent runaway enumeration
    25	
    26	VALID_OUTCOMES = {
    27	    "logic3_active",       # TRA <= threshold AND TLS unlocked AND SW2 closed
    28	    "logic1_active",       # RA < threshold AND SW1 closed AND not inhibited
    29	    "thr_lock_active",     # pls_power active AND pls_unlocked
    30	    "deploy_confirmed",    # VDT >= 90% AND thr_lock active
    31	    "tls_unlocked",       # tls_unlock_delay elapsed
    32	    "pls_unlocked",       # pls_unlock_delay elapsed
    33	}
    34	
    35	# Parameter grid resolution (number of steps per dimension)
    36	_GRID_RESOLUTION = 20  # Finer grid to capture switch windows (~1.6 deg steps)
    37	
    38	
    39	# ─── Dataclasses ──────────────────────────────────────────────────────────────
    40	
    41	
    42	@dataclass(frozen=True)
    43	class ParameterSnapshot:
    44	    """A parameter combination that satisfies the target outcome."""
    45	
    46	    radio_altitude_ft: float
    47	    tra_deg: float
    48	    sw1_closed: bool
    49	    sw2_closed: bool
    50	    tls_unlocked: bool
    51	    pls_unlocked: bool
    52	    vdt_percent: float
    53	    n1k: float
    54	    reverser_inhibited: bool
    55	
    56	
    57	# ─── Engine ───────────────────────────────────────────────────────────────────
    58	
    59	
    60	class ReverseDiagnosisEngine:
    61	    """
    62	    Reverse diagnosis engine for thrust-reverser parameter analysis.
    63	
    64	    Enumerates parameter combinations within YAML-defined ranges that satisfy
    65	    a given target outcome.
    66	
    67	    Deterministic — no randomness.
    68	
    69	    Args:
    70	        hardware_yaml_path: Path to thrust-reverser hardware YAML (P19.1 format).
    71	    """
    72	
    73	    def __init__(self, hardware_yaml_path: str | Path) -> None:
    74	        self.hardware = load_thrust_reverser_hardware(hardware_yaml_path)
    75	
    76	    def diagnose(
    77	        self,
    78	        outcome: str,
    79	        *,
    80	        max_results: int = MAX_COMBINATIONS,
    81	    ) -> list[ParameterSnapshot]:
    82	        """
    83	        Enumerate parameter combinations that satisfy the target outcome.
    84	
    85	        Args:
    86	            outcome: One of VALID_OUTCOMES (e.g., "logic3_active").
    87	            max_results: Maximum number of combinations to return.
    88	
    89	        Returns:
    90	            List of ParameterSnapshot, each satisfying the outcome.
    91	
    92	        Raises:
    93	            ValueError: Unknown outcome string.
    94	        """
    95	        if outcome not in VALID_OUTCOMES:
    96	            raise ValueError(
    97	                f"Unknown outcome: {outcome!r}. "
    98	                f"Valid outcomes: {sorted(VALID_OUTCOMES)}"
    99	            )
   100	
   101	        hw = self.hardware
   102	        results: list[ParameterSnapshot] = []
   103	
   104	        # ── Grid-enumerate within YAML parameter ranges ─────────────────────
   105	        ra_values = _linspace(0.0, hw.sensor.typical_range_ft, _GRID_RESOLUTION)
   106	        tra_values = _linspace(
   107	            hw.physical_limits.reverse_travel_min_deg,
   108	            hw.physical_limits.reverse_travel_max_deg,
   109	            _GRID_RESOLUTION,
   110	        )
   111	        vdt_values = _linspace(0.0, 100.0, _GRID_RESOLUTION)
   112	        n1k_values = [50.0, 80.0, 95.0]  # Representative N1K values
   113	
   114	        for ra in ra_values:
   115	            for tra in tra_values:
   116	                for vdt in vdt_values:
   117	                    for n1k in n1k_values:
   118	                        for inhibited in (False, True):
   119	                            # Compute derived states
   120	                            sw1_closed = _sw1_closed(tra, hw)

 succeeded in 0ms:
  1360	    if outcome == "deploy_confirmed":
  1361	        return bool(hud.get("deploy_90_percent_vdt"))
  1362	    if outcome == "tls_unlocked":
  1363	        return bool(hud.get("tls_unlocked_ls"))
  1364	    if outcome == "pls_unlocked":
  1365	        return bool(hud.get("pls_unlocked_ls"))
  1366	    raise ValueError(f"Unsupported outcome: {outcome}")
  1367	
  1368	
  1369	def build_sensitivity_sweep_payload(request_payload: dict) -> tuple[dict | None, dict | None]:
  1370	    system_id = str(request_payload.get("system_id", "thrust-reverser")).strip() or "thrust-reverser"
  1371	    if system_id != "thrust-reverser":
  1372	        return None, {
  1373	            "error": "unsupported_system",
  1374	            "message": "sensitivity sweep currently supports only 'thrust-reverser'.",
  1375	        }
  1376	
  1377	    radio_altitude_ft_values, error_payload = _optional_request_float_list(
  1378	        request_payload,
  1379	        "radio_altitude_ft_values",
  1380	        default=SENSITIVITY_SWEEP_DEFAULT_RA_VALUES,
  1381	    )
  1382	    if error_payload is not None:
  1383	        return None, error_payload
  1384	
  1385	    tra_deg_values, error_payload = _optional_request_float_list(
  1386	        request_payload,
  1387	        "tra_deg_values",
  1388	        default=SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES,
  1389	    )
  1390	    if error_payload is not None:
  1391	        return None, error_payload
  1392	
  1393	    outcomes, error_payload = _optional_request_string_list(request_payload, "outcomes")
  1394	    if error_payload is not None:
  1395	        error_payload["error"] = "invalid_sensitivity_sweep_request"
  1396	        return None, error_payload
  1397	    requested_outcomes = outcomes or SENSITIVITY_SWEEP_DEFAULT_OUTCOMES
  1398	    invalid_outcomes = [
  1399	        outcome
  1400	        for outcome in requested_outcomes
  1401	        if outcome not in SENSITIVITY_SWEEP_ALLOWED_OUTCOMES
  1402	    ]
  1403	    if invalid_outcomes:
  1404	        return None, {
  1405	            "error": "invalid_sensitivity_outcome",
  1406	            "message": (
  1407	                f"Unsupported outcomes: {invalid_outcomes}. "
  1408	                f"Valid: {sorted(SENSITIVITY_SWEEP_ALLOWED_OUTCOMES)}"
  1409	            ),
  1410	        }
  1411	
  1412	    matrix_counts: dict[str, dict[str, int]] = {}
  1413	    grid: dict[str, dict[str, dict[str, bool]]] = {}
  1414	    outcome_totals = {outcome: 0 for outcome in requested_outcomes}
  1415	
  1416	    for radio_altitude_ft in radio_altitude_ft_values:
  1417	        ra_key = _stable_numeric_key(radio_altitude_ft)
  1418	        matrix_counts[ra_key] = {}
  1419	        grid[ra_key] = {}
  1420	        for tra_deg in tra_deg_values:
  1421	            tra_key = _stable_numeric_key(tra_deg)
  1422	            snapshot = lever_snapshot_payload(
  1423	                tra_deg=tra_deg,
  1424	                radio_altitude_ft=radio_altitude_ft,
  1425	                feedback_mode="manual_feedback_override",
  1426	                deploy_position_percent=100.0,
  1427	            )
  1428	            matched_outcomes = {
  1429	                outcome: _sensitivity_outcome_matches(snapshot, outcome)
  1430	                for outcome in requested_outcomes
  1431	            }
  1432	            matrix_counts[ra_key][tra_key] = sum(
  1433	                1 for is_matched in matched_outcomes.values() if is_matched
  1434	            )
  1435	            grid[ra_key][tra_key] = matched_outcomes
  1436	            for outcome, is_matched in matched_outcomes.items():
  1437	                if is_matched:
  1438	                    outcome_totals[outcome] += 1
  1439	
  1440	    return {
  1441	        "system_id": system_id,
  1442	        "radio_altitude_ft_values": list(radio_altitude_ft_values),
  1443	        "tra_deg_values": list(tra_deg_values),
  1444	        "outcomes": list(requested_outcomes),
  1445	        "matrix_counts": matrix_counts,
  1446	        "outcome_totals": outcome_totals,
  1447	        "grid": grid,
  1448	        "scan_count": len(radio_altitude_ft_values) * len(tra_deg_values),
  1449	        "fixed_inputs": {
  1450	            "engine_running": True,
  1451	            "aircraft_on_ground": True,
  1452	            "reverser_inhibited": False,
  1453	            "eec_enable": True,
  1454	            "n1k": MONITOR_N1K,
  1455	            "max_n1k_deploy_limit": MONITOR_MAX_N1K_DEPLOY_LIMIT,
  1456	            "feedback_mode": "manual_feedback_override",
  1457	            "deploy_position_percent": 100.0,
  1458	        },
  1459	    }, None
  1460	
  1461	
  1462	def _optional_request_str(payload: dict, field_name: str) -> tuple[str | None, dict | None]:
  1463	    raw_value = payload.get(field_name)
  1464	    if raw_value is None:
  1465	        return None, None

codex
I’ve narrowed the likely review questions to two integration-truth points: whether the wow cards are discoverable for a customer repro flow, and whether wow_a is honest about running under `auto_scrubber` while the shell chrome says “Manual (advisory)”. I’m verifying both with a targeted test run and a small live probe.
exec
/bin/zsh -lc "rg -n \"setFeedbackMode\\(|feedback_mode.*workbench-feedback-mode|workbench-trust-banner|runWowScenario|WOW_SCENARIOS\" src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
3742:// it onto #workbench-trust-banner so the banner shows only when mode =
3743:// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
3748:  const banner = document.getElementById("workbench-trust-banner");
3754:function setFeedbackMode(mode) {
3773:  const banner = document.getElementById("workbench-trust-banner");
3778:  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
3786:        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
3796:const WOW_SCENARIOS = {
3840:async function runWowScenario(wowId) {
3841:  const scenario = WOW_SCENARIOS[wowId];
3895:      if (wowId && WOW_SCENARIOS[wowId]) {
3896:        void runWowScenario(wowId);

exec
/bin/zsh -lc "python - <<'PY'
import json, threading, http.client
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port

conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
conn.request('GET', '/workbench')
resp = conn.getresponse()
html = resp.read().decode('utf-8')
print('GET /workbench', resp.status)
for needle in [
    'data-feedback-mode=\"manual_feedback_override\"',
    'Manual (advisory)',
    'data-wow-id=\"wow_a\"',
]:
    print(needle, needle in html)

payload = {
    'tra_deg': -35,
    'radio_altitude_ft': 2,
    'engine_running': True,
    'aircraft_on_ground': True,
    'reverser_inhibited': False,
    'eec_enable': True,
    'n1k': 0.92,
    'feedback_mode': 'auto_scrubber',
    'deploy_position_percent': 95,
}
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('POST /api/lever-snapshot', resp.status)
print('response feedback_mode', body.get('feedback_mode'))
print('logic4 active', body.get('logic', {}).get('logic4', {}).get('active'))
print('summary starts', str(body.get('summary', ''))[:120])

conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/diagnosis/run', body=json.dumps({'system_id':'thrust-reverser','outcome':'deploy_confirmed','max_results':3}).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('POST /api/diagnosis/run', resp.status)
print('diagnosis keys', sorted(body.keys()))
print('first result keys', sorted(body['results'][0].keys()) if body.get('results') else [])
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'pytest tests/test_workbench_wow_starters.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 2305ms:
.......FF.                                                               [100%]
=================================== FAILURES ===================================
________________ test_wow_b_live_endpoint_returns_success_rate _________________

server = <http.server.ThreadingHTTPServer object at 0x109837550>

    def test_wow_b_live_endpoint_returns_success_rate(server) -> None:
        """wow_b card summarize() reads body.success_rate / n_failures / n_trials."""
>       status, body = _post(server, "/api/monte-carlo/run", {
            "system_id": "thrust-reverser",
            "n_trials": 100,
            "seed": 42,
        })

tests/test_workbench_wow_starters.py:144: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/test_workbench_wow_starters.py:61: in _post
    response = connection.getresponse()
               ^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:1415: in getresponse
    response.begin()
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:330: in begin
    version, status, reason = self._read_status()
                              ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <http.client.HTTPResponse object at 0x109111180>

    def _read_status(self):
        line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
        if len(line) > _MAXLINE:
            raise LineTooLong("status line")
        if self.debuglevel > 0:
            print("reply:", repr(line))
        if not line:
            # Presumably, the server closed the connection before
            # sending a valid response.
>           raise RemoteDisconnected("Remote end closed connection without"
                                     " response")
E           http.client.RemoteDisconnected: Remote end closed connection without response

/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:299: RemoteDisconnected
----------------------------- Captured stderr call -----------------------------
----------------------------------------
Exception occurred during processing of request from ('127.0.0.1', 63013)
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 691, in process_request_thread
    self.finish_request(request, client_address)
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 361, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 755, in __init__
    self.handle()
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/server.py", line 440, in handle
    self.handle_one_request()
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/server.py", line 428, in handle_one_request
    method()
  File "/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py", line 471, in do_POST
    from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
  File "/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/monte_carlo_engine.py", line 16, in <module>
    import numpy as np
ModuleNotFoundError: No module named 'numpy'
----------------------------------------
___________________ test_wow_c_live_endpoint_returns_results ___________________

server = <http.server.ThreadingHTTPServer object at 0x1092a5750>

    def test_wow_c_live_endpoint_returns_results(server) -> None:
        """wow_c card summarize() reads body.outcome / total_combos_found / results / grid_resolution."""
>       status, body = _post(server, "/api/diagnosis/run", {
            "system_id": "thrust-reverser",
            "outcome": "deploy_confirmed",
            "max_results": 5,
        })

tests/test_workbench_wow_starters.py:158: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/test_workbench_wow_starters.py:61: in _post
    response = connection.getresponse()
               ^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:1415: in getresponse
    response.begin()
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:330: in begin
    version, status, reason = self._read_status()
                              ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <http.client.HTTPResponse object at 0x1090f8df0>

    def _read_status(self):
        line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
        if len(line) > _MAXLINE:
            raise LineTooLong("status line")
        if self.debuglevel > 0:
            print("reply:", repr(line))
        if not line:
            # Presumably, the server closed the connection before
            # sending a valid response.
>           raise RemoteDisconnected("Remote end closed connection without"
                                     " response")
E           http.client.RemoteDisconnected: Remote end closed connection without response

/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/client.py:299: RemoteDisconnected
----------------------------- Captured stderr call -----------------------------
----------------------------------------
Exception occurred during processing of request from ('127.0.0.1', 63017)
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 691, in process_request_thread
    self.finish_request(request, client_address)
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 361, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/socketserver.py", line 755, in __init__
    self.handle()
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/server.py", line 440, in handle
    self.handle_one_request()
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/http/server.py", line 428, in handle_one_request
    method()
  File "/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py", line 443, in do_POST
    from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
  File "/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/reverse_diagnosis.py", line 16, in <module>
    from well_harness.hardware_schema import (
  File "/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/hardware_schema.py", line 18, in <module>
    import jsonschema
ModuleNotFoundError: No module named 'jsonschema'
----------------------------------------
=========================== short test summary info ============================
FAILED tests/test_workbench_wow_starters.py::test_wow_b_live_endpoint_returns_success_rate
FAILED tests/test_workbench_wow_starters.py::test_wow_c_live_endpoint_returns_results
2 failed, 8 passed in 2.09s

codex
The targeted wow-starter test file did not come back green in this checkout; it failed one test instead of the claimed 10/10. I’m pulling the exact failure now and then I’ll verify whether it’s an environment issue or a real regression in the new test/JS wiring.
exec
/bin/zsh -lc "python3 - <<'PY'
import json, threading, http.client
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port

conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
conn.request('GET', '/workbench')
resp = conn.getresponse()
html = resp.read().decode('utf-8')
print('GET /workbench', resp.status)
for needle in [
    'data-feedback-mode=\"manual_feedback_override\"',
    'Manual (advisory)',
    'data-wow-id=\"wow_a\"',
]:
    print(needle, needle in html)

payload = {
    'tra_deg': -35,
    'radio_altitude_ft': 2,
    'engine_running': True,
    'aircraft_on_ground': True,
    'reverser_inhibited': False,
    'eec_enable': True,
    'n1k': 0.92,
    'feedback_mode': 'auto_scrubber',
    'deploy_position_percent': 95,
}
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('POST /api/lever-snapshot', resp.status)
print('response feedback_mode', body.get('feedback_mode'))
print('logic4 active', body.get('logic', {}).get('logic4', {}).get('active'))
print('summary starts', str(body.get('summary', ''))[:120])

conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/diagnosis/run', body=json.dumps({'system_id':'thrust-reverser','outcome':'deploy_confirmed','max_results':3}).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('POST /api/diagnosis/run', resp.status)
print('diagnosis keys', sorted(body.keys()))
print('first result keys', sorted(body['results'][0].keys()) if body.get('results') else [])
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 628ms:
GET /workbench 200
data-feedback-mode="manual_feedback_override" False
Manual (advisory) False
data-wow-id="wow_a" False
POST /api/lever-snapshot 200
response feedback_mode None
logic4 active True
summary starts {'headline': 'TRA -32.0°：L4 已满足，THR_LOCK release command 已触发。', 'blocker': '当前无 L4 blocker。（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落
POST /api/diagnosis/run 200
diagnosis keys ['grid_resolution', 'outcome', 'results', 'timestamp', 'total_combos_found']
first result keys ['n1k', 'pls_unlocked', 'radio_altitude_ft', 'reverser_inhibited', 'sw1_closed', 'sw2_closed', 'tls_unlocked', 'tra_deg', 'vdt_percent']

codex
I hit a second inconsistency: the live `GET /workbench` probe did not match the literal strings from `workbench.html`, so I’m checking whether that was just a brittle string match or whether the served route is not actually exposing the new section.
exec
/bin/zsh -lc 'rg -n "workbench_start|workbench_bundle|/workbench|/workbench/start|workbench.html" src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
41:from well_harness.workbench_bundle import (
43:    archive_workbench_bundle,
44:    build_workbench_bundle,
70:WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
71:WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
72:WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
73:WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
74:WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
238:        if parsed.path in ("/workbench/start", "/workbench/start.html"):
239:            self._serve_static("workbench_start.html")
242:        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
243:            self._serve_static("workbench_bundle.html")
246:        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
247:            self._serve_static("workbench.html")
420:            response_payload, error_payload = build_workbench_bundle_response(request_payload)
1533:def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
1607:        bundle = build_workbench_bundle(
1630:        archive = archive_workbench_bundle(

exec
/bin/zsh -lc "sed -n '170,260p' src/well_harness/demo_server.py | nl -ba -v170" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,120p' tests/test_workbench_wow_starters.py | nl -ba -v1" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   170	    "n1k",
   171	    "tls115",
   172	    "logic1",
   173	    "logic2",
   174	    "logic3",
   175	    "logic4",
   176	    "thr_lock",
   177	    "vdt90",
   178	    "sw1_input",
   179	    "sw2_input",
   180	}
   181	LEVER_SNAPSHOT_FAULT_TYPES = {
   182	    "stuck_off",
   183	    "stuck_on",
   184	    "sensor_zero",
   185	    "logic_stuck_false",
   186	    "cmd_blocked",
   187	}
   188	FAULT_INJECTION_REASON = "fault_injection"
   189	
   190	# ── FANTUI stateful tick singleton ─────────────────────────────────────────
   191	# Module-level state. ``FantuiTickSystem`` is itself thread-safe — see its
   192	# internal ``_lock`` — so no outer lock is needed here. Restarting the server
   193	# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
   194	# ``_FANTUI_LOCK`` is kept as an alias to the system's internal lock for
   195	# backward-compatibility with any test that reached in directly.
   196	_FANTUI_SYSTEM = FantuiTickSystem()
   197	_FANTUI_LOCK = _FANTUI_SYSTEM._lock
   198	
   199	
   200	class DemoRequestHandler(BaseHTTPRequestHandler):
   201	    """Serve the static demo shell and a thin JSON API around DemoAnswer."""
   202	
   203	    server_version = "WellHarnessDemo/1.0"
   204	
   205	    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
   206	        return
   207	
   208	    def do_GET(self):
   209	        parsed = urlparse(self.path)
   210	        if parsed.path in STATIC_ROUTE_ALIASES:
   211	            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
   212	            return
   213	        if parsed.path == MONITOR_TIMELINE_PATH:
   214	            self._send_json(200, monitor_timeline_payload())
   215	            return
   216	        if parsed.path == WORKBENCH_BOOTSTRAP_PATH:
   217	            self._send_json(200, workbench_bootstrap_payload())
   218	            return
   219	        if parsed.path == SYSTEM_SNAPSHOT_PATH:
   220	            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
   221	            self._send_json(200, system_snapshot_payload(system_id))
   222	            return
   223	        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
   224	            self._send_json(200, workbench_recent_archives_payload())
   225	            return
   226	
   227	        # Default entry: unified landing page with 2x3 card grid
   228	        # (Phase A: chat.html shelved; Phase UI-C: root now serves index.html
   229	        # instead of demo.html so user can reach all 6 surfaces.)
   230	        if parsed.path in ("", "/"):
   231	            self._serve_static("index.html")
   232	            return
   233	
   234	        if parsed.path in ("/demo.html", "/expert/demo.html"):
   235	            self._serve_static("demo.html")
   236	            return
   237	
   238	        if parsed.path in ("/workbench/start", "/workbench/start.html"):
   239	            self._serve_static("workbench_start.html")
   240	            return
   241	
   242	        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
   243	            self._serve_static("workbench_bundle.html")
   244	            return
   245	
   246	        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
   247	            self._serve_static("workbench.html")
   248	            return
   249	
   250	        relative_path = unquote(parsed.path.lstrip("/"))
   251	        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
   252	            self._serve_static(relative_path)
   253	            return
   254	
   255	        # P19.8: Hardware schema discovery
   256	        if parsed.path == HARDWARE_SCHEMA_PATH:
   257	            system_id = parse_qs(parsed.query).get("system_id", ["thrust-reverser"])[0]
   258	            self._handle_hardware_schema(system_id=system_id)
   259	            return
   260	

 succeeded in 0ms:
     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
     2	
     3	Locks the contract for the top-of-/workbench wow starter cards so future
     4	shell edits don't silently regress the demo presenter's one-click 走读
     5	entrypoint. Per E11-00-PLAN row E11-05.
     6	
     7	Three contracts validated:
     8	  1. /workbench static HTML carries the three starter cards (one per
     9	     wow_id) with run buttons and result panes.
    10	  2. workbench.js declares WOW_SCENARIOS with all three endpoints and
    11	     payload-shape sentinels (BEAT_DEEP_PAYLOAD-equivalent for wow_a,
    12	     n_trials/seed for wow_b, outcome for wow_c).
    13	  3. The three POST endpoints behind the cards return 200 with the
    14	     contract fields the cards' summarize() functions read.
    15	
    16	Truth-engine red line: this is a thin UI affordance over already-public
    17	endpoints; no controller/runner/models/adapters changes.
    18	"""
    19	
    20	from __future__ import annotations
    21	
    22	import http.client
    23	import json
    24	import re
    25	import threading
    26	from http.server import ThreadingHTTPServer
    27	from pathlib import Path
    28	
    29	import pytest
    30	
    31	from well_harness.demo_server import DemoRequestHandler
    32	
    33	
    34	REPO_ROOT = Path(__file__).resolve().parents[1]
    35	STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
    36	
    37	
    38	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    39	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    40	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    41	    thread.start()
    42	    return server, thread
    43	
    44	
    45	def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    46	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    47	    connection.request("GET", path)
    48	    response = connection.getresponse()
    49	    body = response.read().decode("utf-8")
    50	    return response.status, body
    51	
    52	
    53	def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
    54	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    55	    connection.request(
    56	        "POST",
    57	        path,
    58	        body=json.dumps(payload).encode("utf-8"),
    59	        headers={"Content-Type": "application/json"},
    60	    )
    61	    response = connection.getresponse()
    62	    body = json.loads(response.read().decode("utf-8") or "{}")
    63	    return response.status, body
    64	
    65	
    66	@pytest.fixture
    67	def server():
    68	    s, t = _start_demo_server()
    69	    try:
    70	        yield s
    71	    finally:
    72	        s.shutdown()
    73	        s.server_close()
    74	        t.join(timeout=2)
    75	
    76	
    77	# ─── 1. Static HTML carries all three starter cards ──────────────────
    78	
    79	
    80	def test_workbench_html_has_wow_starters_section() -> None:
    81	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    82	    assert 'id="workbench-wow-starters"' in html
    83	    assert "起手卡" in html
    84	
    85	
    86	@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
    87	def test_workbench_html_has_card_for_each_wow(wow_id: str) -> None:
    88	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    89	    # card article + run button + result pane all keyed by data-wow-id
    90	    assert f'data-wow-id="{wow_id}"' in html, f"missing card for {wow_id}"
    91	    assert (
    92	        f'data-wow-result-for="{wow_id}"' in html
    93	    ), f"missing result pane for {wow_id}"
    94	
    95	
    96	# ─── 2. workbench.js wires the three scenarios ───────────────────────
    97	
    98	
    99	def test_workbench_js_declares_wow_scenarios() -> None:
   100	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   101	    # The constants object is the single source of truth.
   102	    assert "const WOW_SCENARIOS" in js
   103	    # wow_a → /api/lever-snapshot with BEAT_DEEP_PAYLOAD shape.
   104	    assert "/api/lever-snapshot" in js
   105	    assert "tra_deg" in js and "deploy_position_percent" in js
   106	    # wow_b → /api/monte-carlo/run with seed.
   107	    assert "/api/monte-carlo/run" in js
   108	    assert "n_trials" in js
   109	    # wow_c → /api/diagnosis/run with outcome.
   110	    assert "/api/diagnosis/run" in js
   111	    assert "deploy_confirmed" in js
   112	
   113	
   114	def test_workbench_js_installWowStarters_wired_to_dom() -> None:
   115	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   116	    assert "function installWowStarters" in js
   117	    # Hooked into DOMContentLoaded (alongside the existing init calls).
   118	    assert re.search(r"installWowStarters\s*\(\s*\)", js) is not None
   119	
   120	

exec
/bin/zsh -lc "python3 - <<'PY'
import threading, http.client
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
conn.request('GET', '/workbench')
resp = conn.getresponse()
html = resp.read().decode('utf-8')
print('status', resp.status)
print(html[:1200])
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 602ms:
status 200
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>协作工作台 · FANTUI LogicMVP</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/unified-nav.css">
  <link rel="stylesheet" href="/workbench_shell.css">
</head>
<body class="unified-nav-enabled" data-nav-current="workbench">

<!-- ── Unified Nav ─────────────────────────────────────────────────── -->
<header class="unified-nav" role="navigation" aria-label="FANTUI LogicMVP 主导航">
  <a href="/index.html" class="unified-nav-brand">FANTUI LogicMVP</a>
  <div class="unified-nav-groups">
    <div class="unified-nav-group">
      <span class="unified-nav-group-label">工作台</span>
      <a href="/demo.html" class="unified-nav-link" data-nav-key="demo">反推逻辑</a>
      <a href="/c919_etras_workstation.html" class="unified-nav-link" data-nav-key="etras">C919 E-TRAS</a>
    </div>
    <div class="unified-nav-group">
      <span class="unified-nav-group-label">协作</span>
      <a href="/workbench" class="unified-nav-link" data-nav-key="workbench" data-current="true">Workbench Shell</a>
    </div>
    <div clas

exec
/bin/zsh -lc "sed -n '260,325p' src/well_harness/demo_server.py | nl -ba -v260" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   260	
   261	        if parsed.path == FANTUI_LOG_PATH:
   262	            # records() is internally locked; the copy it returns is
   263	            # self-contained so JSON serialization can run unlocked.
   264	            recs = _FANTUI_SYSTEM.records()
   265	            self._send_json(200, recs)
   266	            return
   267	
   268	        if parsed.path == FANTUI_STATE_PATH:
   269	            # Atomic snapshot — one lock acquisition covers all fields
   270	            # so callers don't observe torn state.
   271	            self._send_json(200, _FANTUI_SYSTEM.snapshot())
   272	            return
   273	
   274	        self._send_json(404, {"error": "not_found"})
   275	
   276	    def do_POST(self):
   277	        parsed = urlparse(self.path)
   278	        if parsed.path not in {
   279	            "/api/demo",
   280	            "/api/lever-snapshot",
   281	            "/api/timeline-simulate",
   282	            SYSTEM_SNAPSHOT_POST_PATH,
   283	            WORKBENCH_BUNDLE_PATH,
   284	            WORKBENCH_REPAIR_PATH,
   285	            WORKBENCH_ARCHIVE_RESTORE_PATH,
   286	            DIAGNOSIS_RUN_PATH,
   287	            MONTE_CARLO_RUN_PATH,
   288	            HARDWARE_SCHEMA_PATH,
   289	            SENSITIVITY_SWEEP_PATH,
   290	            FANTUI_TICK_PATH,
   291	            FANTUI_RESET_PATH,
   292	            FANTUI_SET_VDT_PATH,
   293	        }:
   294	            self._send_json(404, {"error": "not_found"})
   295	            return
   296	
   297	        try:
   298	            content_length = int(self.headers.get("Content-Length", "0") or "0")
   299	        except ValueError:
   300	            self._send_json(400, {"error": "invalid_content_length"})
   301	            return
   302	
   303	        # Guard: reject oversized payloads before reading
   304	        if content_length and content_length > _MAX_DOCUMENT_BYTES:
   305	            self._send_json(413, {"error": "payload_too_large", "message": f"Request body exceeds maximum of {_MAX_DOCUMENT_BYTES} bytes."})
   306	            return
   307	
   308	        # Guard: enforce Content-Type whitelist (defense-in-depth; browser enforces this too)
   309	        content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
   310	        allowed_types = {"application/json"}
   311	        if content_type and content_type not in allowed_types:
   312	            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json."})
   313	            return
   314	
   315	        try:
   316	            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
   317	            request_payload = json.loads(body)
   318	        except (UnicodeDecodeError, json.JSONDecodeError):
   319	            self._send_json(400, {"error": "invalid_json"})
   320	            return
   321	        if not isinstance(request_payload, dict):
   322	            self._send_json(400, {"error": "invalid_json_object"})
   323	            return
   324	
   325	        if parsed.path == "/api/lever-snapshot":

exec
/bin/zsh -lc "rg --files -g 'workbench.html'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n \"def _serve_static|STATIC_DIR|static_root|Path\\(__file__\\).*static|workbench_shell.css|协作工作台\" src/well_harness/demo_server.py src/well_harness/static/workbench.html" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html

 succeeded in 0ms:
src/well_harness/demo_server.py:48:STATIC_DIR = Path(__file__).with_name("static")
src/well_harness/demo_server.py:566:    def _serve_static(self, relative_path: str):
src/well_harness/demo_server.py:567:        static_root = STATIC_DIR.resolve()
src/well_harness/demo_server.py:568:        target_path = (static_root / relative_path).resolve()
src/well_harness/demo_server.py:569:        # Path must live inside static_root (traversal guard) and exist as a file.
src/well_harness/demo_server.py:573:            target_path.relative_to(static_root)

exec
/bin/zsh -lc "sed -n '1,30p' src/well_harness/static/workbench.html" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'ls -l src/well_harness/static/workbench.html' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
-rw-r--r--@ 1 Zhuanz  staff  12811 Apr 25 23:44 src/well_harness/static/workbench.html

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
          <p class="eyebrow">control logic workbench</p>
          <h1>Control Logic Workbench</h1>
        </div>
        <div id="workbench-identity" class="workbench-collab-chip" data-role="ENGINEER">
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

exec
/bin/zsh -lc "sed -n '566,590p' src/well_harness/demo_server.py | nl -ba -v566" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   566	    def _serve_static(self, relative_path: str):
   567	        static_root = STATIC_DIR.resolve()
   568	        target_path = (static_root / relative_path).resolve()
   569	        # Path must live inside static_root (traversal guard) and exist as a file.
   570	        # Phase UI-F (2026-04-22): allow nested static paths like
   571	        # /c919_etras_panel/circuit.html so the unified-nav can link to them.
   572	        try:
   573	            target_path.relative_to(static_root)
   574	        except ValueError:
   575	            self._send_json(404, {"error": "not_found"})
   576	            return
   577	        if not target_path.is_file():
   578	            self._send_json(404, {"error": "not_found"})
   579	            return
   580	
   581	        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
   582	        self._send_bytes(200, target_path.read_bytes(), content_type)
   583	
   584	    def _send_json(self, status_code: int, payload: dict):
   585	        # Compact JSON: no indentation (machine-to-machine API, not human-readable)
   586	        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
   587	        self._send_bytes(status_code, response, "application/json; charset=utf-8")
   588	
   589	    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
   590	        self.send_response(status_code)

codex
The odd `/workbench` payload is likely a Python-path issue rather than a route bug in this checkout. I’m verifying whether the test run and probe hit an installed `well_harness` package instead of the local repo, because that changes how much weight the env-dependent failures deserve in the verdict.
exec
/bin/zsh -lc "python3 - <<'PY'
import sys, well_harness, well_harness.demo_server
print('well_harness', well_harness.__file__)
print('demo_server', well_harness.demo_server.__file__)
print('sys.path[0:5]', sys.path[:5])
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'which pytest && pytest --version && which python3 && python3 --version' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "python3 - <<'PY'
import pathlib
from well_harness.demo_server import STATIC_DIR
print('STATIC_DIR', STATIC_DIR)
print('resolved', STATIC_DIR.resolve())
print('workbench head:')
print((STATIC_DIR/'workbench.html').read_text(encoding='utf-8')[:220])
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/opt/homebrew/bin/pytest
pytest 9.0.2
/usr/bin/python3
Python 3.9.6

 succeeded in 108ms:
 succeeded in 113ms:
well_harness /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/__init__.py
demo_server /Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/demo_server.py
sys.path[0:5] ['', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python39.zip', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9', '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload', '/Users/Zhuanz/Library/Python/3.9/lib/python/site-packages']

codex
I found the source of the route mismatch: plain `python3` in this shell imports a different editable `well_harness` checkout from `/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP`, while `pytest` in this repo is path-adjusted into the local `src/`. I’m rerunning the probe against the local package explicitly and checking whether this repo has its own `.venv` for the dependency-backed tests.
exec
/bin/zsh -lc 'ls -d .venv venv env 2>/dev/null' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import threading, http.client, json
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/diagnosis/run', body=json.dumps({'system_id':'thrust-reverser','outcome':'deploy_confirmed','max_results':3}).encode('utf-8'), headers={'Content-Type':'application/json'})
resp = conn.getresponse()
raw = resp.read().decode('utf-8')
print('status', resp.status)
print(raw[:800])
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import threading, http.client, json
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
conn.request('GET', '/workbench')
resp = conn.getresponse()
html = resp.read().decode('utf-8')
print('GET /workbench', resp.status)
for needle in [
  'data-feedback-mode=\"manual_feedback_override\"',
  'Manual (advisory)',
  'data-wow-id=\"wow_a\"',
  'data-wow-id=\"wow_b\"',
  'data-wow-id=\"wow_c\"',
]:
  print(needle, needle in html)
print('title snippet', html.split('</title>',1)[0].split('<title>',1)[-1])

payload = {
    'tra_deg': -35,
    'radio_altitude_ft': 2,
    'engine_running': True,
    'aircraft_on_ground': True,
    'reverser_inhibited': False,
    'eec_enable': True,
    'n1k': 0.92,
    'feedback_mode': 'auto_scrubber',
    'deploy_position_percent': 95,
}
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('POST /api/lever-snapshot', resp.status)
print('top-level feedback_mode', body.get('feedback_mode'))
print('nodes', len(body.get('nodes', [])))
print('logic active', {k:v.get('active') for k,v in body.get('logic', {}).items()})
print('summary keys', sorted(body.get('summary', {}).keys()) if isinstance(body.get('summary'), dict) else type(body.get('summary')).__name__)
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 579ms:
status 200
{"outcome": "deploy_confirmed", "total_combos_found": 3, "grid_resolution": 20, "timestamp": "2026-04-25T15:57:24.215188+00:00", "results": [{"radio_altitude_ft": 0.0, "tra_deg": -32.0, "sw1_closed": false, "sw2_closed": false, "tls_unlocked": true, "pls_unlocked": true, "vdt_percent": 94.73684210526316, "n1k": 50.0, "reverser_inhibited": false}, {"radio_altitude_ft": 0.0, "tra_deg": -32.0, "sw1_closed": false, "sw2_closed": false, "tls_unlocked": true, "pls_unlocked": true, "vdt_percent": 94.73684210526316, "n1k": 50.0, "reverser_inhibited": true}, {"radio_altitude_ft": 0.0, "tra_deg": -32.0, "sw1_closed": false, "sw2_closed": false, "tls_unlocked": true, "pls_unlocked": true, "vdt_percent": 94.73684210526316, "n1k": 80.0, "reverser_inhibited": false}]}

 succeeded in 578ms:
GET /workbench 200
data-feedback-mode="manual_feedback_override" True
Manual (advisory) True
data-wow-id="wow_a" True
data-wow-id="wow_b" True
data-wow-id="wow_c" True
title snippet Control Logic Workbench
POST /api/lever-snapshot 200
top-level feedback_mode None
nodes 19
logic active {'logic1': False, 'logic2': True, 'logic3': True, 'logic4': True}
summary keys ['blocker', 'headline', 'next_step']

exec
/bin/zsh -lc 'rg -n "residual_risk|repro|reverse diagnose|反向诊断|grid_resolution|ParameterSnapshot|possibilit|enumerat|suggested_action|probabilities" src/well_harness/static/workbench.html src/well_harness/static/workbench.js src/well_harness/static/workbench_start.html src/well_harness/reverse_diagnosis.py tests/e2e/test_wow_c_reverse_diagnose.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.html:131:              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
src/well_harness/reverse_diagnosis.py:4:Given a desired outcome (e.g., "logic3_active"), enumerates all parameter
src/well_harness/reverse_diagnosis.py:7:This is a DIAGNOSIS ANALYZER — it reads hardware YAML and produces enumerated
src/well_harness/reverse_diagnosis.py:8:possibilities. It does NOT call controller.py or affect truth engine behavior.
src/well_harness/reverse_diagnosis.py:24:MAX_COMBINATIONS = 1000  # Safety bound to prevent runaway enumeration
src/well_harness/reverse_diagnosis.py:43:class ParameterSnapshot:
src/well_harness/reverse_diagnosis.py:81:    ) -> list[ParameterSnapshot]:
src/well_harness/reverse_diagnosis.py:90:            List of ParameterSnapshot, each satisfying the outcome.
src/well_harness/reverse_diagnosis.py:102:        results: list[ParameterSnapshot] = []
src/well_harness/reverse_diagnosis.py:104:        # ── Grid-enumerate within YAML parameter ranges ─────────────────────
src/well_harness/reverse_diagnosis.py:163:                                    ParameterSnapshot(
src/well_harness/reverse_diagnosis.py:191:                "grid_resolution": _GRID_RESOLUTION,
src/well_harness/reverse_diagnosis.py:193:                "results": [list of ParameterSnapshot dicts],
src/well_harness/reverse_diagnosis.py:202:            "grid_resolution": _GRID_RESOLUTION,
src/well_harness/reverse_diagnosis.py:211:def _parameter_snapshot_to_dict(snapshot: ParameterSnapshot) -> dict:
src/well_harness/reverse_diagnosis.py:212:    """Convert a ParameterSnapshot to a plain dict for JSON serialization."""
src/well_harness/static/workbench_start.html:119:    <a href="/workbench?intent=customer-repro"
src/well_harness/static/workbench_start.html:122:       data-intent="customer-repro"
src/well_harness/static/workbench_start.html:123:       id="ws-tile-customer-repro">
src/well_harness/static/workbench_start.html:136:        <li>customer_quote / repro_recipe / screenshot_refs 等扩展字段是 E11-08 范围</li>
tests/e2e/test_wow_c_reverse_diagnose.py:6:Note: The current response shape does NOT include probabilities or
tests/e2e/test_wow_c_reverse_diagnose.py:7:suggested_action fields. Those are candidates for P20.1 contract expansion.
tests/e2e/test_wow_c_reverse_diagnose.py:18:# Keys guaranteed by ParameterSnapshot dataclass in reverse_diagnosis.py
tests/e2e/test_wow_c_reverse_diagnose.py:49:    for idx, snap in enumerate(body["results"]):
tests/e2e/test_wow_c_reverse_diagnose.py:56:def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:57:    """grid_resolution + timestamp must be present (audit trail for rehearsal)."""
tests/e2e/test_wow_c_reverse_diagnose.py:63:    assert "grid_resolution" in body
tests/e2e/test_wow_c_reverse_diagnose.py:64:    assert isinstance(body["grid_resolution"], int)
tests/e2e/test_wow_c_reverse_diagnose.py:65:    assert body["grid_resolution"] > 0
src/well_harness/static/workbench.js:3359:  renderValue("knowledge-residual-risk", resolution.residual_risk, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
src/well_harness/static/workbench.js:3407:    residual_risk: workbenchElement("workbench-residual-risk").value.trim() || undefined,
src/well_harness/static/workbench.js:3834:      const grid = body.grid_resolution;

exec
/bin/zsh -lc "PYTHONPATH=src python3 - <<'PY'
import threading, http.client, json
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
payload = {
    'tra_deg': -35,
    'radio_altitude_ft': 2,
    'engine_running': True,
    'aircraft_on_ground': True,
    'reverser_inhibited': False,
    'eec_enable': True,
    'n1k': 0.92,
    'feedback_mode': 'auto_scrubber',
    'deploy_position_percent': 95,
}
conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
resp = conn.getresponse()
body = json.loads(resp.read().decode('utf-8'))
print('status', resp.status)
print('top keys', sorted(body.keys()))
for key in ['feedback_mode','inputs','hud','sensors','outputs','plant_state','summary']:
    print('KEY', key, type(body.get(key)).__name__)
    if isinstance(body.get(key), dict):
        sub = body.get(key)
        print('  subkeys', sorted(sub.keys())[:25])
        if 'feedback_mode' in sub:
            print('  feedback_mode=', sub['feedback_mode'])
server.shutdown(); server.server_close(); thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 571ms:
status 200
top keys ['evidence', 'hud', 'input', 'logic', 'mode', 'model_note', 'nodes', 'outputs', 'plant_state', 'risks', 'summary', 'time_s', 'tra_lock']
KEY feedback_mode NoneType
KEY inputs NoneType
KEY hud dict
  subkeys ['aircraft_on_ground', 'all_pls_unlocked_ls', 'deploy_90_percent_vdt', 'deploy_position_percent', 'eec_enable', 'engine_running', 'feedback_mode', 'max_n1k_deploy_limit', 'n1k', 'pls_unlocked_ls', 'radio_altitude_ft', 'requested_tra_deg', 'reverser_inhibited', 'sw1', 'sw2', 'tls_unlocked_ls', 'tra_deg']
  feedback_mode= auto_scrubber
KEY sensors NoneType
KEY outputs dict
  subkeys ['eec_deploy_cmd', 'etrac_540vdc_cmd', 'logic1_active', 'logic2_active', 'logic3_active', 'logic4_active', 'pdu_motor_cmd', 'pls_power_cmd', 'throttle_electronic_lock_release_cmd', 'tls_115vac_cmd']
KEY plant_state dict
  subkeys ['deploy_position_percent', 'pls_powered_s', 'pls_unlocked_ls', 'tls_powered_s', 'tls_unlocked_ls']
KEY summary dict
  subkeys ['blocker', 'headline', 'next_step']

codex
I’ve got enough to call it. I’m pulling one small memory citation range for the final note, then I’ll return the review with the concrete line-cited issues and the red-line check.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,880p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3750,3885p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3750	    banner.setAttribute("data-feedback-mode", mode);
  3751	  }
  3752	}
  3753	
  3754	function setFeedbackMode(mode) {
  3755	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  3756	  if (!allowed.has(mode)) {
  3757	    return false;
  3758	  }
  3759	  const chip = document.getElementById("workbench-feedback-mode");
  3760	  if (chip) {
  3761	    chip.setAttribute("data-feedback-mode", mode);
  3762	    const label = chip.querySelector("strong");
  3763	    if (label) {
  3764	      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
  3765	    }
  3766	  }
  3767	  syncTrustBannerForMode(mode);
  3768	  return true;
  3769	}
  3770	
  3771	function installFeedbackModeAffordance() {
  3772	  const chip = document.getElementById("workbench-feedback-mode");
  3773	  const banner = document.getElementById("workbench-trust-banner");
  3774	  if (!chip || !banner) {
  3775	    return;
  3776	  }
  3777	  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
  3778	  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
  3779	    banner.setAttribute("data-trust-banner-dismissed", "true");
  3780	  }
  3781	  const dismiss = banner.querySelector("[data-trust-banner-dismiss]");
  3782	  if (dismiss) {
  3783	    dismiss.addEventListener("click", () => {
  3784	      banner.setAttribute("data-trust-banner-dismissed", "true");
  3785	      if (window.sessionStorage) {
  3786	        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
  3787	      }
  3788	    });
  3789	  }
  3790	}
  3791	
  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
  3793	// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py and the
  3794	// monte-carlo / reverse-diagnose API contracts from the matching e2e suites.
  3795	// One click → POST → single-line summary in the card's result area.
  3796	const WOW_SCENARIOS = {
  3797	  wow_a: {
  3798	    endpoint: "/api/lever-snapshot",
  3799	    payload: {
  3800	      tra_deg: -35,
  3801	      radio_altitude_ft: 2,
  3802	      engine_running: true,
  3803	      aircraft_on_ground: true,
  3804	      reverser_inhibited: false,
  3805	      eec_enable: true,
  3806	      n1k: 0.92,
  3807	      feedback_mode: "auto_scrubber",
  3808	      deploy_position_percent: 95,
  3809	    },
  3810	    summarize: (body) => {
  3811	      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
  3812	      const active = nodes.filter((n) => n && n.state === "active").length;
  3813	      return `nodes=${nodes.length} · active=${active} · L1–L4 chain latched.`;
  3814	    },
  3815	  },
  3816	  wow_b: {
  3817	    endpoint: "/api/monte-carlo/run",
  3818	    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
  3819	    summarize: (body) => {
  3820	      if (!body) return "(empty body)";
  3821	      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
  3822	      const failures = body.n_failures;
  3823	      const trials = body.n_trials;
  3824	      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
  3825	    },
  3826	  },
  3827	  wow_c: {
  3828	    endpoint: "/api/diagnosis/run",
  3829	    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
  3830	    summarize: (body) => {
  3831	      if (!body) return "(empty body)";
  3832	      const total = body.total_combos_found;
  3833	      const returned = Array.isArray(body.results) ? body.results.length : 0;
  3834	      const grid = body.grid_resolution;
  3835	      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
  3836	    },
  3837	  },
  3838	};
  3839	
  3840	async function runWowScenario(wowId) {
  3841	  const scenario = WOW_SCENARIOS[wowId];
  3842	  const button = document.querySelector(
  3843	    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  3844	  );
  3845	  const result = document.querySelector(
  3846	    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  3847	  );
  3848	  if (!scenario || !result) {
  3849	    return;
  3850	  }
  3851	  if (button) {
  3852	    button.disabled = true;
  3853	  }
  3854	  result.removeAttribute("data-wow-state");
  3855	  result.textContent = `POST ${scenario.endpoint} ...`;
  3856	  try {
  3857	    const t0 = performance.now();
  3858	    const response = await fetch(scenario.endpoint, {
  3859	      method: "POST",
  3860	      headers: { "Content-Type": "application/json" },
  3861	      body: JSON.stringify(scenario.payload),
  3862	    });
  3863	    const ms = Math.round(performance.now() - t0);
  3864	    let body = null;
  3865	    try {
  3866	      body = await response.json();
  3867	    } catch (_err) {
  3868	      body = null;
  3869	    }
  3870	    if (!response.ok) {
  3871	      result.setAttribute("data-wow-state", "error");
  3872	      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
  3873	      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
  3874	      return;
  3875	    }
  3876	    result.setAttribute("data-wow-state", "ok");
  3877	    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  3878	  } catch (err) {
  3879	    result.setAttribute("data-wow-state", "error");
  3880	    result.textContent = `network error: ${err && err.message ? err.message : err}`;
  3881	  } finally {
  3882	    if (button) {
  3883	      button.disabled = false;
  3884	    }
  3885	  }

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '28,40p;72,76p;131,136p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
    72	            </header>
    73	            <p class="workbench-wow-card-desc">
    74	              POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
    75	              deploy=95%) — latches L1–L4 deep-deploy chain.
    76	            </p>
   131	              <h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>
   132	            </header>
   133	            <p class="workbench-wow-card-desc">
   134	              POST <code>/api/diagnosis/run</code> with outcome=deploy_confirmed — 反求
   135	              触发该 outcome 的参数组合（max_results=10）。
   136	            </p>

codex
CHANGES_REQUIRED

1. `IMPORTANT` — [workbench.html:74](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:74), [workbench.js:3810](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3810), `tests/e2e/test_wow_a_causal_chain.py:38-42,121-132` overstate wow_a as an `L1–L4` latched result. The pinned contract says `logic1` naturally drops back out during BEAT_DEEP after deploy, and my local live probe against the repo code (`PYTHONPATH=src`, local `DemoRequestHandler`) returned `logic1=false`, `logic2/3/4=true`. For a customer/demo surface, this is a truthfulness bug, not just wording.

2. `IMPORTANT` — [workbench.html:28](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:28), [workbench.js:3754](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3754), [workbench.js:3797](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3797), [workbench.js:3840](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3840) make wow_a look like it is running under the shell’s visible `Manual (advisory)` mode, but the actual POST uses `feedback_mode: "auto_scrubber"`. `runWowScenario()` never surfaces or syncs the returned mode, even though `setFeedbackMode()` exists. Same live probe: `GET /workbench` rendered `Manual (advisory)`, while `POST /api/lever-snapshot` returned `hud.feedback_mode=auto_scrubber`. From a customer-repro perspective, that is not honest about probe nature.

3. `NIT` — [workbench.html:133](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:133), [workbench.js:3830](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3830), `src/well_harness/reverse_diagnosis.py:4-8,198-205` promise parameter combinations for wow_c, but the card result pane only shows counts and grid size. That proves the analyzer ran, but it does not hand the user an actionable repro recipe.

`INFO` — truth-engine red line holds. `git diff --name-only a17e744..a02729a` only shows `.planning/`, `src/well_harness/static/`, and `tests/`; no `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/` changes.

`INFO` — I could not reproduce the claimed `10 passed` with the default shell `pytest` here because this machine’s default interpreter is missing `numpy` and `jsonschema`; I used `PYTHONPATH=src` live probes for the behavior checks above.

P5 — Apps Engineer (Tier-A, E11-05)

tokens used
139,205
CHANGES_REQUIRED

1. `IMPORTANT` — [workbench.html:74](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:74), [workbench.js:3810](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3810), `tests/e2e/test_wow_a_causal_chain.py:38-42,121-132` overstate wow_a as an `L1–L4` latched result. The pinned contract says `logic1` naturally drops back out during BEAT_DEEP after deploy, and my local live probe against the repo code (`PYTHONPATH=src`, local `DemoRequestHandler`) returned `logic1=false`, `logic2/3/4=true`. For a customer/demo surface, this is a truthfulness bug, not just wording.

2. `IMPORTANT` — [workbench.html:28](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:28), [workbench.js:3754](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3754), [workbench.js:3797](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3797), [workbench.js:3840](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3840) make wow_a look like it is running under the shell’s visible `Manual (advisory)` mode, but the actual POST uses `feedback_mode: "auto_scrubber"`. `runWowScenario()` never surfaces or syncs the returned mode, even though `setFeedbackMode()` exists. Same live probe: `GET /workbench` rendered `Manual (advisory)`, while `POST /api/lever-snapshot` returned `hud.feedback_mode=auto_scrubber`. From a customer-repro perspective, that is not honest about probe nature.

3. `NIT` — [workbench.html:133](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:133), [workbench.js:3830](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3830), `src/well_harness/reverse_diagnosis.py:4-8,198-205` promise parameter combinations for wow_c, but the card result pane only shows counts and grid size. That proves the analyzer ran, but it does not hand the user an actionable repro recipe.

`INFO` — truth-engine red line holds. `git diff --name-only a17e744..a02729a` only shows `.planning/`, `src/well_harness/static/`, and `tests/`; no `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/` changes.

`INFO` — I could not reproduce the claimed `10 passed` with the default shell `pytest` here because this machine’s default interpreter is missing `numpy` and `jsonschema`; I used `PYTHONPATH=src` live probes for the behavior checks above.

P5 — Apps Engineer (Tier-A, E11-05)

