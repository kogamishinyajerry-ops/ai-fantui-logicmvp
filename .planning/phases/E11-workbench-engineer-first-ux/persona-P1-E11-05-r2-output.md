2026-04-25T17:10:54.225825Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T17:10:54.225910Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc59f-7212-7a50-89aa-780d194ac75f
--------
user
You are Codex GPT-5.4 acting as **Persona P1 — Junior FCS Engineer** (Tier-A pipeline, E11-05 R2 closure check).

# Shared R2 context for E11-05 closure check

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-05-wow-starter-cards-20260425`
**PR:** #18
**R2 HEAD:** `8882b7b` (single fix commit on top of R1 `a02729a`)

## Your R1 verdict (recap)

You returned CHANGES_REQUIRED on R1 (commit `a02729a`). R2 (`8882b7b`) addresses every BLOCKER and IMPORTANT raised by ANY persona. Verify your specific findings closed.

## What R2 ships (per-persona summary)

**Convergent BLOCKERs fixed (raised by 3 of 5 personas):**

1. **wow_a "L1–L4 latched" claim is dishonest** (P1+P2+P5):
   - `workbench.html` description rewritten to spell out the actual e2e contract: "L2/L3/L4 active under auto_scrubber pullback (L1 drops out)"
   - `workbench.js` `summarize()` now reads `body.logic.{logic1..logic4}.active` and prints the real active set verbatim (e.g. `nodes=19 · active=[logic2+logic3+logic4] · mode=auto_scrubber`)
   - `tests/test_workbench_wow_starters.py::test_wow_a_live_endpoint_with_exact_card_payload` asserts `{logic2,logic3,logic4} ⊆ active`

2. **No fetch timeout / abort path** (P1):
   - Added `WOW_REQUEST_TIMEOUT_MS = 10000` constant + `AbortController`
   - AbortError branch renders distinct copy: `timed out after Nms · click again to retry`
   - Button re-enabled on every exit path (success / error / abort)
   - `test_workbench_js_runWowScenario_handles_http_error_and_timeout` locks the contract

3. **Tests don't lock exact canonical payloads** (P1+P2+P4):
   - New `WOW_{A,B,C}_FROZEN_PAYLOAD` constants + `_extract_wow_scenarios_payloads_from_js()` parses workbench.js and asserts every literal matches frozen e2e contracts
   - Live probes now use EXACT card payloads (n_trials=1000, max_results=10, n1k=0.92, full BEAT_DEEP_PAYLOAD)

**IMPORTANTs fixed:**

- (P3) Result-pane font-size 0.78rem → 0.92rem with tighter padding for projector readability
- (P4) Selector contract test added — every card has `<button class="workbench-wow-run-button" data-wow-action="run" data-wow-id="wow_X">`
- (P4) `workbench_start.html` [REWRITE] copy locked (positive claim "已上线" must appear; "暂未上线" + "没有 UI 走读 surface" must NOT appear)
- (P1) Error-path test verifies AbortController + WOW_REQUEST_TIMEOUT_MS ≥ 1000 + AbortError branch + button re-enable
- (P5) `summarize()` for wow_a now prints `mode=auto_scrubber` explicitly so the card is honest about not honoring the chip's manual_feedback_override

**Out-of-scope deferrals (NIT/IMPORTANT only, per spec scope):**

- P3 IMPORTANT (presenter routing on `/workbench/start`): defers to E11-08/E11-15
- P3 NIT (raw-error copy "HTTP 500"): defers to E11-15 string sweep
- P5 NIT (wow_c parameter combinations in result pane): future enhancement

## Verification

- 919/919 pytest pass (16 in test_workbench_wow_starters.py, +6 new vs R1)
- Truth-engine red line preserved: `git diff --name-only main..8882b7b` shows zero changes to `controller.py`/`runner.py`/`models.py`/`src/well_harness/adapters/`

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

For each R1 finding YOU raised, state explicitly: CLOSED / OPEN / DEFERRED-WITH-DISCLOSURE.

Live-probe at least one path you're unsure about. Cite the probe.

If you raise NEW findings (not on R1's list), classify in-scope or out-of-scope per the deferrals above. Out-of-scope findings should be NIT/INFO only — not BLOCKER.

Sign as: **{your persona ID and role} (Tier-A, E11-05 R2)**
codex
我会按你给的 R2 closure check 口径做一次只读验收：先恢复这个 repo 的相关上下文和我自己在 R1 关心的点，再核对 `8882b7b` 的改动、跑至少一个 live probe，并给出明确的 `APPROVE`/`APPROVE_WITH_NITS`/`CHANGES_REQUIRED` 结论。
exec
/bin/zsh -lc 'rg -n "ai-fantui-logicmvp|LogicMVP|E11-05|wow starter|wow_a|workbench_start|workbench_wow" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'git rev-parse --abbrev-ref HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git rev-parse --short HEAD' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
feat/e11-05-wow-starter-cards-20260425

 succeeded in 0ms:
8882b7b

codex
我已经确认工作副本就是目标分支和 R2 头 `8882b7b`。接下来按 review 模式核对我在 R1 提过的点，只检查闭环，不做实现。
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
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/skills/auto-compression-agent/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
---
name: auto-compression-agent
description: >
  An always-active intelligent context compression skill for all coding and research sessions.
  Activates automatically on any development task — multi-file coding, bug fixing, repo exploration,
  research synthesis, or long-running agent sessions. Monitors 6 real-time signals and triggers
  layered compression before drift occurs. Never miss a compression opportunity.
---

# Auto-Compression Agent

An intelligent, always-on context compression system that monitors 6 signals in real-time and
triggers layered compression BEFORE drift becomes severe. This is not a reactive checkpoint tool —
it is a proactive monitoring and compression framework.

## Core Principle

**Compress before you drift, not after you already drifted.**

Your baseline data proves the old model (50% threshold, compress when things feel noisy) is too slow.
Evidence drift appears in the **first minute** of failing sessions. By the time you hit 50% context,
you've already lost.

---

## The 6 Real-Time Signals

After EVERY significant interaction, silently evaluate these signals:

### Signal 1: Evidence Drift Count (EARLIEST WARNING)
**Trigger: ≥2 uncertain expressions in a single response**

Uncertain expressions: "可能是", "大概是", "应该是", "估计", "也许", "可能", "不确定", "凭感觉"

**This is your free early warning system.** Evidence drift often appears 5-10 minutes before
any other drift type. When you catch 2 in one response, compress immediately.

### Signal 2: Context Pressure
**Trigger: ≥20% context usage**

Monitor token_count events. The thresholds:
- **20%**: Mini compression (one-line state reset)
- **35%**: Standard compression (structured checkpoint)
- **50%**: Deep compression (full phase summary) + forced rebuild
- **65%**: Emergency — stop, compress everything, rebuild from scratch

### Signal 3: Phase Transition
**Trigger: Moving between exploration → implementation → validation**

Every time you shift phases:
- Exploration ended, implementation starting → compress exploration findings
- Implementation ended, testing/validation starting → compress implementation state
- Validation ended, cleanup/refinement → compress validation results

### Signal 4: Tool Failure Cascade
**Trigger: ≥2 consecutive tool failures without a strategy change**

If you try the same approach 2+ times and it keeps failing, compress the failed-attempt log
and the current state before trying a third time.

### Signal 5: Constraint Forget
**Trigger: Re-reading a file you've already read, or reasking for information already provided**

If the user says "as I mentioned before" or you catch yourself re-reading the same file,
compress immediately — your context has a gap.

### Signal 6: Plan Oscillation
**Trigger: ≥3 "改成" / "推翻" / "重新" signals within 10 minutes**

This means the plan is unstable. Compress the decision ledger and force a firm next action.

---

## The Three Compression Tiers

### Tier 1: Mini Compression (20% context OR 2 evidence drift signals)

One-line state reset. Output this format:

```
[COMPRESS-1] <objective> | <3 stable facts> | <next action> | <1 open risk>
```

Example:
```
[COMPRESS-1] Fix pricing.py discount order | tier before promo | confirmed current-rules.md authoritative | Test: test_pricing.py::test_multiplicative | risk: historical-notes.md still in context
```

### Tier 2: Standard Compression (35% context OR phase transition OR tool failure cascade)

Full structured checkpoint. Use the template in `references/checkpoint-templates.md`.
This is the most common compression type.

Output a checkpoint AND immediately continue from it — do not wait.

### Tier 3: Deep Compression (50%+ context OR emergency signal)

Full phase summary + context rebuild. This compresses everything accumulated so far
and produces a clean-slate restart recipe.

Steps:
1. Write the deep checkpoint using the full template
2. Acknowledge the compression to the user
3. Rebuild the minimum working context from the checkpoint
4. Continue with only the checkpoint + immediate needs

---

## The Five-Layer Working Model

At all times, maintain these five layers. Compressions preserve layers 1-3
and replace large layer-4 artifacts with references.

```
Layer 1: Working Context — only what the NEXT step needs
Layer 2: Task State — goal, constraints, completion criteria
Layer 3: Decision Ledger — what you decided, why, what you rejected
Layer 4: Artifact Index — files, URLs, commands, docs (with paths/references)
Layer 5: Open Loops — unresolved questions, risks, failed attempts
```

Compression is successful when Layer 1 is executable without reading Layer 4 artifacts.

---

## Checkpoint Quality Standards

Every checkpoint MUST pass the **Stranger Test**:

> "A colleague who has never seen this conversation could read this checkpoint,
> reopen 1-2 artifacts, and continue the task in under 5 minutes with no additional questions."

Checklist before finalizing any checkpoint:
- [ ] Contains exactly one concrete **next action** (not "keep going")
- [ ] Stable facts are separated from hypotheses
- [ ] Rejected paths include WHY they were rejected
- [ ] File references are absolute paths, not descriptions
- [ ] Open risks are explicitly named, not just implied
- [ ] No raw tool output or terminal logs
- [ ] Shorter than the material it replaces

---

## Anti-Patterns (Never Do These)

1. **Hour-by-hour narrative** — compress events, not timelines
2. **Raw tool output** — rerun commands, don't paste their output
3. **Confirmed + guessed mixed** — mark uncertainty explicitly
4. **"Just in case" files** — only keep files that change the next action
5. **Vague next actions** — "keep working on X" is not a next action
6. **Dropping failed attempts** — the rejected path IS the value

---

## Context Pressure Dashboard

After every compression, briefly note the current state using this compact format:

```
[CP: XX%] [PHASE: explore/impl/valid] [DRIFT: evidence:N goal:N plan:N] [NEXT: <1 sentence>]
```

This goes in your working context and is updated after every compression.
You can output this silently in commentary.

---

## When to Output Compression Status

You do NOT need to announce every compression to the user.
Only announce when:
- You are triggering a Tier 2 or Tier 3 compression
- The compression reveals something important about the task state
- The user asks about progress or context

Otherwise, compress silently and continue.

---

## Running Summary Requirement

When you finish a session, output:

```
## Session Summary
- Checkpoints created: N
- Compression triggers: <list the signal types that fired>
- Final context pressure: XX%
- Unresolved risks: <1-3 bullets>
- Next session starting point: <checkpoint location or recreation recipe>
```

This is required for any task that took more than 15 minutes or 3 tool calls.

---

## Relationship to context-compression-agent

The `context-compression-agent` skill provides the foundational framework.
This skill (`auto-compression-agent`) overrides it when both are available,
because it provides earlier triggers, multi-tier compression, and proactive monitoring.

If you need the full checkpoint templates or eval protocol,
those are in `references/` alongside this skill.

## References

- `references/checkpoint-templates.md` — Full templates for all three tiers
- `references/eval-protocol.md` — How to measure if compression is working
- `references/trigger-logic.md` — Decision tree for which compression tier to use

codex
我在按 `gsd-code-review` 的只读审查方式走，并把这次上下文压缩在最小范围内：只看 R2 触及的 workbench UI、测试、以及 live endpoint 的真实性。
  → Collect R2 scope and inspect diffs for the R1 findings relevant to P1
  • Verify each P1 R1 finding against code and targeted tests
  • Run at least one live probe for an uncertain path and form final verdict
exec
/bin/zsh -lc 'git diff --name-only main..8882b7b' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git diff --name-only a02729a..8882b7b' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/persona-E11-05-shared-context.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-prompt.txt
src/well_harness/static/workbench.css
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
tests/test_workbench_wow_starters.py

 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
.planning/phases/E11-workbench-engineer-first-ux/persona-E11-05-shared-context.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-prompt.txt
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-prompt.txt
src/well_harness/static/workbench.css
src/well_harness/static/workbench.html
src/well_harness/static/workbench.js
src/well_harness/static/workbench_start.html
tests/test_workbench_wow_starters.py

exec
/bin/zsh -lc 'git diff --stat a02729a..8882b7b' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../persona-E11-05-shared-context.txt              |    45 +
 .../persona-P1-E11-05-output.md                    | 10297 +++++++++++++++++++
 .../persona-P1-E11-05-prompt.txt                   |    71 +
 .../persona-P2-E11-05-output.md                    |  9726 ++++++++++++++++++
 .../persona-P2-E11-05-prompt.txt                   |    71 +
 .../persona-P3-E11-05-output.md                    |  7889 ++++++++++++++
 .../persona-P3-E11-05-prompt.txt                   |    71 +
 .../persona-P4-E11-05-output.md                    |  8719 ++++++++++++++++
 .../persona-P4-E11-05-prompt.txt                   |    71 +
 .../persona-P5-E11-05-output.md                    |  9346 +++++++++++++++++
 .../persona-P5-E11-05-prompt.txt                   |    71 +
 src/well_harness/static/workbench.css              |    10 +-
 src/well_harness/static/workbench.html             |     4 +-
 src/well_harness/static/workbench.js               |    45 +-
 tests/test_workbench_wow_starters.py               |   180 +-
 15 files changed, 46576 insertions(+), 40 deletions(-)

exec
/bin/zsh -lc 'rg -n "BLOCKER|IMPORTANT|CHANGES_REQUIRED|APPROVE|timeout|canonical|latched|manual_feedback_override|AbortController|frozen payload|exact" .planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
72:Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.
75:- **BLOCKER** — must fix before merge (regression, safety, contract violation)
76:- **IMPORTANT** — should fix in this PR or follow-up sub-phase
80:Each finding should cite a file:line. If you raise out-of-scope findings (E11-06/E11-08/E11-15 territory or backend), label them INFO/NIT only — not BLOCKER.
103:<EXTREMELY-IMPORTANT>
109:</EXTREMELY-IMPORTANT>
152:    "Follow skill exactly" [shape=box];
166:    "Has checklist?" -> "Follow skill exactly" [label="no"];
167:    "Create TodoWrite todo per item" -> "Follow skill exactly";
202:**Rigid** (TDD, debugging): Follow exactly. Don't adapt away discipline.
346:- [ ] Contains exactly one concrete **next action** (not "keep going")
488:52:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
496:304:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP plus machine-level Claude/Codex config under `~/.claude`, `~/.codex`, `~/.cc-switch`; reuse_rule=safe for local Claude/Codex auth-routing diagnosis on this machine, but treat exact repo-planning references as checkout-specific.
501:794:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
502:800:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
503:804:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
509:851:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
520:Using `gsd-code-review` for the review workflow and `auto-compression-agent` to keep the inspection tight. I’ve finished the quick memory pass; next I’m validating the exact file scope against the red line and then reading the changed artifacts with line numbers.
589:+# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
743:+/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
876:    data-feedback-mode = manual_feedback_override AND not session-dismissed.
990:           data-feedback-mode="manual_feedback_override"
1016:+          <p class="eyebrow">canonical scenarios</p>
1119:         data-feedback-mode="manual_feedback_override"
1229: // E11-13 (2026-04-25): manual_feedback_override trust-affordance.
1232: // manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
1244:   const allowed = new Set(["manual_feedback_override", "truth_engine"]);
1266:   syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
1281:+// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
1302:+      return `nodes=${nodes.length} · active=${active} · L1–L4 chain latched.`;
1630:+"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
1675:+    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
1683:+    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
1703:+        t.join(timeout=2)
1946:    31	          data-feedback-mode="manual_feedback_override"
1972:    57	          <p class="eyebrow">canonical scenarios</p>
2075:   160	        data-feedback-mode="manual_feedback_override"
2351:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
2396:    46	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
2404:    54	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
2424:    74	        t.join(timeout=2)
2604:3777:  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
2644:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
2807:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
2940:   240	   data-feedback-mode = manual_feedback_override AND not session-dismissed.
5282:   104	  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
5283:   105	  APPROVED:    { archive: "ARCHIVING" },
5284:   106	  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
5639:   461	  // PANEL_READY/ANNOTATING → final_approve → APPROVING → approve_ok → APPROVED
7940:  3740	// E11-13 (2026-04-25): manual_feedback_override trust-affordance.
7943:  3743	// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
7955:  3755	  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
7977:  3777	  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
7992:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
8013:  3813	      return `nodes=${nodes.length} · active=${active} · L1–L4 chain latched.`;
8667:    27	#           feedback_mode='auto_scrubber' the server-side canonical pullback
8668:    28	#           (demo_server._canonical_pullback_sequence, extended in commit a46e4e6)
8671:    31	#           latches. Under manual_feedback_override mode, logic4 activates only when
8679:    39	#                                  canonical pullback runs the plant to 100%
8740:   100	        f"BEAT_EARLY should activate exactly logic1+logic2, got {active}"
8748:   108	    Per commit a46e4e6 ("fix(scrubber): extend canonical pullback hold to let
8758:   118	    a manual-mode concern; see manual_feedback_override path with
8769:   129	        "logic4 must activate under auto_scrubber's extended canonical pullback "
8771:   131	        "demo_server._canonical_pullback_sequence and commit a46e4e6)"
8783:/bin/zsh -lc 'rg -n "AbortController|timeout|Failed to fetch|network error|response.ok" src/well_harness/static/workbench.js' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
9207:.planning/phases/E11-workbench-engineer-first-ux/E11-05-SURFACE-INVENTORY.md:1:# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9226:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:342:a02729a (HEAD -> feat/e11-05-wow-starter-cards-20260425) phase(E11-05): wow_a/b/c canonical-scenario starter cards on /workbench
9240:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:433:tests/test_workbench_wow_starters.py:1:"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9244:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:578:src/well_harness/static/workbench.js:3792:// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9250:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1124:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9260:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:1305:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9270:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:2003:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9271:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:6646:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9279:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8417:+# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9289:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8489:+/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9291:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8757:+// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9301:.planning/phases/E11-workbench-engineer-first-ux/persona-P2-E11-05-output.md:8920:+"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9312:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:135:3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
9316:.planning/phases/governance-bundle-2/codex-r4-output.md:551: 3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
9323:.planning/phases/governance-bundle-2/codex-r5-output.md:735:   135	3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
9355:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:782:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9365:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:963:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9375:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:1141:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9377:.planning/phases/E11-workbench-engineer-first-ux/persona-P3-E11-05-output.md:6862:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9392:.planning/phases/governance-bundle-2/codex-r6-output.md:610:   135	3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
9397:.planning/phases/governance-bundle-2/codex-r3-retry-output.md:1876:   135	3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
9431:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:589:+# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9441:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:743:+/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9443:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1281:+// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9454:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:1630:+"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9468:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2351:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9484:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2644:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9493:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:2807:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9494:.planning/phases/E11-workbench-engineer-first-ux/persona-P1-E11-05-output.md:7992:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9526:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:355:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9543:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1093:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9552:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:1658:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9553:.planning/phases/E11-workbench-engineer-first-ux/persona-P4-E11-05-output.md:7345:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9571:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:648:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9584:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1036:     1	# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards
9593:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:1197:   107	/* E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9595:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:6861:  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
9603:.planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-05-output.md:8582:     1	"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.
9646:    30	    timeout-minutes: 8
10205:src/well_harness/static/workbench.js:3743:// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
10215:I have enough to close the review. The code stays on the UI side of the red line, and the same-button click path is basically safe, but I’m landing on `CHANGES_REQUIRED` because there are two front-end honesty/resilience gaps in the new wow handler that are easy to miss in happy-path testing.
10226:   851	applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s demo/presentation workflow, but ports, exact UI files, and report docs are checkout-specific.
10237:   862	- VDT 模式, VDT 反馈, deploy_position_percent, manual_feedback_override, logic-note, 结果摘要先下沉, 诊断问答 frozen, /api/lever-snapshot, THR_LOCK, deploy_90_percent_vdt
10258:**CHANGES_REQUIRED**
10260:- **BLOCKER** — `src/well_harness/static/workbench.js:3810`  
10261:  `wow_a` always reports `L1–L4 chain latched.` but it never reads the contract-bearing gate fields. The summary only counts `body.nodes`; the actual truth for that claim lives in `body.logic.logic1..logic4` (`tests/e2e/test_wow_a_causal_chain.py:79`, `tests/e2e/test_wow_a_causal_chain.py:121`). If `/api/lever-snapshot` ever returns a partial chain on `200`, the UI will still overstate success.
10263:- **BLOCKER** — `src/well_harness/static/workbench.js:3851`  
10264:  The click path disables the button and waits on raw `fetch()` with no timeout or abort path. If an endpoint stalls instead of failing fast, the card stays stuck in `POST ...` and the operator cannot retry until the browser/network stack gives up. For a top-of-workbench demo starter, that is too brittle; it needs a bounded timeout and deterministic recovery text.
10266:- **IMPORTANT** — `tests/test_workbench_wow_starters.py:99`, `tests/test_workbench_wow_starters.py:114`, `tests/test_workbench_wow_starters.py:142`, `tests/test_workbench_wow_starters.py:156`  
10267:  The new regression lock is weaker than advertised. It does not assert the exact wow_b/wow_c sentinels (`seed=42`, `n_trials=1000`, `max_results=10`), and it does not exercise the new failure path in `runWowScenario()` at all: no HTTP-error rendering, no network-error rendering, no button re-enable check. Those are the highest-risk drift points in this PR.
10279:**CHANGES_REQUIRED**
10281:- **BLOCKER** — `src/well_harness/static/workbench.js:3810`  
10282:  `wow_a` always reports `L1–L4 chain latched.` but it never reads the contract-bearing gate fields. The summary only counts `body.nodes`; the actual truth for that claim lives in `body.logic.logic1..logic4` (`tests/e2e/test_wow_a_causal_chain.py:79`, `tests/e2e/test_wow_a_causal_chain.py:121`). If `/api/lever-snapshot` ever returns a partial chain on `200`, the UI will still overstate success.
10284:- **BLOCKER** — `src/well_harness/static/workbench.js:3851`  
10285:  The click path disables the button and waits on raw `fetch()` with no timeout or abort path. If an endpoint stalls instead of failing fast, the card stays stuck in `POST ...` and the operator cannot retry until the browser/network stack gives up. For a top-of-workbench demo starter, that is too brittle; it needs a bounded timeout and deterministic recovery text.
10287:- **IMPORTANT** — `tests/test_workbench_wow_starters.py:99`, `tests/test_workbench_wow_starters.py:114`, `tests/test_workbench_wow_starters.py:142`, `tests/test_workbench_wow_starters.py:156`  
10288:  The new regression lock is weaker than advertised. It does not assert the exact wow_b/wow_c sentinels (`seed=42`, `n_trials=1000`, `max_results=10`), and it does not exercise the new failure path in `runWowScenario()` at all: no HTTP-error rendering, no network-error rendering, no button re-enable check. Those are the highest-risk drift points in this PR.

exec
/bin/zsh -lc 'git diff a02729a..8882b7b -- src/well_harness/static/workbench.html src/well_harness/static/workbench.js src/well_harness/static/workbench.css src/well_harness/static/workbench_start.html tests/test_workbench_wow_starters.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.css b/src/well_harness/static/workbench.css
index cf760a7..98c7ba0 100644
--- a/src/well_harness/static/workbench.css
+++ b/src/well_harness/static/workbench.css
@@ -214,14 +214,16 @@
 }
 
 .workbench-wow-result {
+  /* P3 R2 IMPORTANT fix: bump font-size from 0.78rem → 0.92rem so the
+     live-summary line is readable from across the room on a projector. */
   min-height: 1.3rem;
-  padding: 0.5rem 0.65rem;
+  padding: 0.55rem 0.7rem;
   border-radius: 6px;
   background: rgba(255, 255, 255, 0.04);
-  color: rgba(206, 223, 236, 0.82);
+  color: rgba(206, 223, 236, 0.86);
   font-family: "SFMono-Regular", "Menlo", monospace;
-  font-size: 0.78rem;
-  line-height: 1.45;
+  font-size: 0.92rem;
+  line-height: 1.5;
   white-space: pre-wrap;
   word-break: break-word;
 }
diff --git a/src/well_harness/static/workbench.html b/src/well_harness/static/workbench.html
index 547bf52..39a3194 100644
--- a/src/well_harness/static/workbench.html
+++ b/src/well_harness/static/workbench.html
@@ -72,7 +72,9 @@
             </header>
             <p class="workbench-wow-card-desc">
               POST <code>/api/lever-snapshot</code> with BEAT_DEEP_PAYLOAD (tra=-35°, n1k=0.92,
-              deploy=95%) — latches L1–L4 deep-deploy chain.
+              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
+              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
+              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
             </p>
             <button
               type="button"
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index c214228..dc66e55 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -3790,12 +3790,21 @@ function installFeedbackModeAffordance() {
 }
 
 // E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
-// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py and the
-// monte-carlo / reverse-diagnose API contracts from the matching e2e suites.
-// One click → POST → single-line summary in the card's result area.
+// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
+// the monte-carlo / reverse-diagnose API contracts from the matching e2e
+// suites. One click → POST (with bounded timeout) → single-line summary in
+// the card's result area.
+//
+// The exact card payloads are FROZEN — tests/test_workbench_wow_starters.py
+// asserts byte-equality against this object; do not silently re-tune
+// n_trials, max_results, n1k, or BEAT_DEEP_PAYLOAD shape without updating
+// the regression lock and the surface-inventory drift acceptance.
+const WOW_REQUEST_TIMEOUT_MS = 10000;
+
 const WOW_SCENARIOS = {
   wow_a: {
     endpoint: "/api/lever-snapshot",
+    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
     payload: {
       tra_deg: -35,
       radio_altitude_ft: 2,
@@ -3807,10 +3816,19 @@ const WOW_SCENARIOS = {
       feedback_mode: "auto_scrubber",
       deploy_position_percent: 95,
     },
+    // P1+P2+P5 R2 fix: read actual logic-gate states from the response
+    // instead of overstating "L1–L4 latched". Under auto_scrubber pullback
+    // the e2e contract says BEAT_DEEP latches at minimum {logic2, logic3,
+    // logic4} with logic1 dropping out (reverser_not_deployed_eec flips
+    // false mid-deploy). Print the live active set verbatim so the card
+    // never overstates the truth.
     summarize: (body) => {
+      const logic = body && typeof body.logic === "object" ? body.logic : {};
+      const order = ["logic1", "logic2", "logic3", "logic4"];
+      const active = order.filter((k) => logic[k] && logic[k].active === true);
       const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
-      const active = nodes.filter((n) => n && n.state === "active").length;
-      return `nodes=${nodes.length} · active=${active} · L1–L4 chain latched.`;
+      const activeStr = active.length === 0 ? "none" : active.join("+");
+      return `nodes=${nodes.length} · active=[${activeStr}] · mode=auto_scrubber`;
     },
   },
   wow_b: {
@@ -3853,12 +3871,20 @@ async function runWowScenario(wowId) {
   }
   result.removeAttribute("data-wow-state");
   result.textContent = `POST ${scenario.endpoint} ...`;
+  // P1 R2 BLOCKER fix: bounded timeout via AbortController so a stalled
+  // endpoint cannot freeze the card mid-demo.
+  const controller =
+    typeof AbortController !== "undefined" ? new AbortController() : null;
+  const timeoutHandle = controller
+    ? setTimeout(() => controller.abort(), WOW_REQUEST_TIMEOUT_MS)
+    : null;
   try {
     const t0 = performance.now();
     const response = await fetch(scenario.endpoint, {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify(scenario.payload),
+      signal: controller ? controller.signal : undefined,
     });
     const ms = Math.round(performance.now() - t0);
     let body = null;
@@ -3877,8 +3903,15 @@ async function runWowScenario(wowId) {
     result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
   } catch (err) {
     result.setAttribute("data-wow-state", "error");
-    result.textContent = `network error: ${err && err.message ? err.message : err}`;
+    if (err && err.name === "AbortError") {
+      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
+    } else {
+      result.textContent = `network error: ${err && err.message ? err.message : err}`;
+    }
   } finally {
+    if (timeoutHandle !== null) {
+      clearTimeout(timeoutHandle);
+    }
     if (button) {
       button.disabled = false;
     }
diff --git a/tests/test_workbench_wow_starters.py b/tests/test_workbench_wow_starters.py
index 27bebea..ca0c072 100644
--- a/tests/test_workbench_wow_starters.py
+++ b/tests/test_workbench_wow_starters.py
@@ -121,50 +121,172 @@ def test_workbench_js_installWowStarters_wired_to_dom() -> None:
 # ─── 3. Live endpoint contracts the cards depend on ──────────────────
 
 
-def test_wow_a_live_endpoint_returns_nodes(server) -> None:
-    """wow_a card summarize() reads body.nodes — must be a list on 200."""
-    status, body = _post(server, "/api/lever-snapshot", {
-        "tra_deg": -35,
-        "radio_altitude_ft": 2,
-        "engine_running": True,
-        "aircraft_on_ground": True,
-        "reverser_inhibited": False,
-        "eec_enable": True,
-        "n1k": 0.92,
-        "feedback_mode": "auto_scrubber",
-        "deploy_position_percent": 95,
-    })
+# ─── P1+P2+P4 R2 BLOCKER fix: lock exact canonical card payloads ─────
+#
+# The exact payloads are FROZEN via these literals. If workbench.js drifts
+# (e.g. n_trials → 50, max_results → 5, n1k → 0.5), the test below catches
+# it before it reaches a live demo.
+WOW_A_FROZEN_PAYLOAD = {
+    "tra_deg": -35,
+    "radio_altitude_ft": 2,
+    "engine_running": True,
+    "aircraft_on_ground": True,
+    "reverser_inhibited": False,
+    "eec_enable": True,
+    "n1k": 0.92,
+    "feedback_mode": "auto_scrubber",
+    "deploy_position_percent": 95,
+}
+WOW_B_FROZEN_PAYLOAD = {"system_id": "thrust-reverser", "n_trials": 1000, "seed": 42}
+WOW_C_FROZEN_PAYLOAD = {
+    "system_id": "thrust-reverser",
+    "outcome": "deploy_confirmed",
+    "max_results": 10,
+}
+
+
+def _extract_wow_scenarios_payloads_from_js() -> dict[str, dict]:
+    """Parse the WOW_SCENARIOS block out of workbench.js so the exact card
+    literals can be compared against the frozen e2e contracts."""
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    out: dict[str, dict] = {}
+    for wow_id, frozen in (
+        ("wow_a", WOW_A_FROZEN_PAYLOAD),
+        ("wow_b", WOW_B_FROZEN_PAYLOAD),
+        ("wow_c", WOW_C_FROZEN_PAYLOAD),
+    ):
+        # Each scenario is keyed by `<wow_id>: { ... }` inside WOW_SCENARIOS.
+        # We don't need a full JS parser: assert each frozen field appears
+        # in the file in a payload key:value form near the wow_id.
+        anchor = js.find(f"{wow_id}:")
+        assert anchor != -1, f"WOW_SCENARIOS missing entry for {wow_id}"
+        # Take a slice large enough to contain the whole payload object.
+        slice_ = js[anchor : anchor + 1200]
+        for k, v in frozen.items():
+            if isinstance(v, bool):
+                literal = "true" if v else "false"
+            elif isinstance(v, str):
+                literal = f'"{v}"'
+            else:
+                literal = str(v)
+            assert (
+                f"{k}: {literal}" in slice_
+            ), f"{wow_id}.{k} drift: expected `{k}: {literal}` near {wow_id}: in workbench.js"
+        out[wow_id] = frozen
+    return out
+
+
+def test_workbench_js_freezes_exact_canonical_payloads() -> None:
+    """Lock every shipped wow_a/b/c payload literal against the e2e contract.
+
+    P1+P2+P4 R2 BLOCKER fix — without this, n_trials/seed/max_results/n1k
+    can silently drift in workbench.js and the cards would no longer match
+    `tests/e2e/test_wow_a_causal_chain.py:51`,
+    `tests/e2e/test_wow_b_monte_carlo.py:_run`, or
+    `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed`.
+    """
+    _extract_wow_scenarios_payloads_from_js()
+
+
+def test_wow_a_live_endpoint_with_exact_card_payload(server) -> None:
+    """wow_a card POSTs the EXACT BEAT_DEEP_PAYLOAD; assert e2e contract."""
+    status, body = _post(server, "/api/lever-snapshot", WOW_A_FROZEN_PAYLOAD)
     assert status == 200
     assert isinstance(body.get("nodes"), list)
     assert len(body["nodes"]) > 0
+    # P1+P2+P5 R2 BLOCKER fix: the card no longer overstates "L1–L4
+    # latched"; verify the actual e2e contract holds — under auto_scrubber
+    # BEAT_DEEP must latch logic2+logic3+logic4 (logic1 may drop out).
+    logic = body.get("logic", {}) or {}
+    assert isinstance(logic, dict), "wow_a response must expose `logic` dict"
+    active = {k for k, v in logic.items() if isinstance(v, dict) and v.get("active") is True}
+    assert {"logic2", "logic3", "logic4"} <= active, (
+        f"BEAT_DEEP must latch at least logic2+logic3+logic4, got {active}"
+    )
 
 
-def test_wow_b_live_endpoint_returns_success_rate(server) -> None:
-    """wow_b card summarize() reads body.success_rate / n_failures / n_trials."""
-    status, body = _post(server, "/api/monte-carlo/run", {
-        "system_id": "thrust-reverser",
-        "n_trials": 100,
-        "seed": 42,
-    })
+def test_wow_b_live_endpoint_with_exact_card_payload(server) -> None:
+    """wow_b card POSTs n_trials=1000, seed=42 — probe with the SAME values."""
+    status, body = _post(server, "/api/monte-carlo/run", WOW_B_FROZEN_PAYLOAD)
     assert status == 200
+    assert body["n_trials"] == 1000  # exact card value, not 100
     assert "success_rate" in body
     assert "n_failures" in body
-    assert "n_trials" in body
-    assert body["n_trials"] == 100
 
 
-def test_wow_c_live_endpoint_returns_results(server) -> None:
-    """wow_c card summarize() reads body.outcome / total_combos_found / results / grid_resolution."""
-    status, body = _post(server, "/api/diagnosis/run", {
-        "system_id": "thrust-reverser",
-        "outcome": "deploy_confirmed",
-        "max_results": 5,
-    })
+def test_wow_c_live_endpoint_with_exact_card_payload(server) -> None:
+    """wow_c card POSTs max_results=10 — probe with the SAME value."""
+    status, body = _post(server, "/api/diagnosis/run", WOW_C_FROZEN_PAYLOAD)
     assert status == 200
     assert body["outcome"] == "deploy_confirmed"
     assert "total_combos_found" in body
     assert "grid_resolution" in body
     assert isinstance(body.get("results"), list)
+    assert len(body["results"]) <= 10  # bounded by max_results
+
+
+# ─── P4 R2 IMPORTANT fix: lock selector contract ─────────────────────
+
+
+@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
+def test_workbench_html_card_has_run_button_selector(wow_id: str) -> None:
+    """The click handler binds via .workbench-wow-run-button[data-wow-action="run"];
+    if the selector contract drifts the card becomes inert."""
+    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
+    # Each card must have a button with class workbench-wow-run-button,
+    # data-wow-action="run", and matching data-wow-id.
+    pattern = re.compile(
+        r'<button[^>]*?class="workbench-wow-run-button"[^>]*?'
+        r'data-wow-action="run"[^>]*?data-wow-id="' + re.escape(wow_id) + r'"',
+        re.DOTALL,
+    )
+    alt_pattern = re.compile(
+        r'<button[^>]*?data-wow-id="' + re.escape(wow_id) + r'"[^>]*?'
+        r'class="workbench-wow-run-button"[^>]*?data-wow-action="run"',
+        re.DOTALL,
+    )
+    assert pattern.search(html) or alt_pattern.search(html), (
+        f"wow card {wow_id} is missing the click-binding selector contract"
+    )
+
+
+# ─── P4 R2 IMPORTANT fix: lock workbench_start.html [REWRITE] copy ───
+
+
+def test_workbench_start_reflects_e11_05_shipped() -> None:
+    """The 3 [REWRITE] lines on workbench_start.html must claim E11-05 has shipped,
+    not the stale 'not yet shipped' text."""
+    html = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
+    # Positive claim (must appear): cards are live on /workbench.
+    assert "wow_a/b/c 起手卡片已上线（E11-05）" in html
+    # Negative claim (must NOT appear): the stale "not yet shipped" line.
+    assert "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" not in html
+    # Negative claim (must NOT appear): "no UI 走读 surface".
+    assert "没有 UI 走读 surface" not in html
+
+
+# ─── P1 R2 IMPORTANT fix: error-path UI assertions ──────────────────
+
+
+def test_workbench_js_runWowScenario_handles_http_error_and_timeout() -> None:
+    """The click handler must render HTTP-error and abort/timeout failures
+    distinctly, never a stuck `POST ... ` placeholder.
+
+    P1 R2 BLOCKER fix — without bounded timeout + abort path, the card
+    freezes mid-demo when an endpoint stalls.
+    """
+    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
+    # AbortController + bounded timeout
+    assert "AbortController" in js, "no abort path; stalled requests freeze the card"
+    assert "WOW_REQUEST_TIMEOUT_MS" in js, "no bounded timeout constant"
+    assert "AbortError" in js, "AbortError branch must render distinct copy"
+    # HTTP-error branch
+    assert 'data-wow-state", "error"' in js
+    # Re-enable the button on every exit (success / error / abort)
+    assert "button.disabled = false" in js
+    # Sanity: the timeout constant has a real numeric value, not 0.
+    m = re.search(r"WOW_REQUEST_TIMEOUT_MS\s*=\s*(\d+)", js)
+    assert m and int(m.group(1)) >= 1000, "timeout must be ≥ 1000ms"
 
 
 def test_workbench_html_serves_with_wow_section(server) -> None:

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench_start.html | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3790,3918p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.css | sed -n '214,232p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.html | sed -n '64,96p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  3790	}
  3791	
  3792	// E11-05 (2026-04-25): wow_a/b/c canonical-scenario starter cards.
  3793	// Mirrors BEAT_DEEP_PAYLOAD from tests/e2e/test_wow_a_causal_chain.py:51 and
  3794	// the monte-carlo / reverse-diagnose API contracts from the matching e2e
  3795	// suites. One click → POST (with bounded timeout) → single-line summary in
  3796	// the card's result area.
  3797	//
  3798	// The exact card payloads are FROZEN — tests/test_workbench_wow_starters.py
  3799	// asserts byte-equality against this object; do not silently re-tune
  3800	// n_trials, max_results, n1k, or BEAT_DEEP_PAYLOAD shape without updating
  3801	// the regression lock and the surface-inventory drift acceptance.
  3802	const WOW_REQUEST_TIMEOUT_MS = 10000;
  3803	
  3804	const WOW_SCENARIOS = {
  3805	  wow_a: {
  3806	    endpoint: "/api/lever-snapshot",
  3807	    // BEAT_DEEP_PAYLOAD per tests/e2e/test_wow_a_causal_chain.py:51
  3808	    payload: {
  3809	      tra_deg: -35,
  3810	      radio_altitude_ft: 2,
  3811	      engine_running: true,
  3812	      aircraft_on_ground: true,
  3813	      reverser_inhibited: false,
  3814	      eec_enable: true,
  3815	      n1k: 0.92,
  3816	      feedback_mode: "auto_scrubber",
  3817	      deploy_position_percent: 95,
  3818	    },
  3819	    // P1+P2+P5 R2 fix: read actual logic-gate states from the response
  3820	    // instead of overstating "L1–L4 latched". Under auto_scrubber pullback
  3821	    // the e2e contract says BEAT_DEEP latches at minimum {logic2, logic3,
  3822	    // logic4} with logic1 dropping out (reverser_not_deployed_eec flips
  3823	    // false mid-deploy). Print the live active set verbatim so the card
  3824	    // never overstates the truth.
  3825	    summarize: (body) => {
  3826	      const logic = body && typeof body.logic === "object" ? body.logic : {};
  3827	      const order = ["logic1", "logic2", "logic3", "logic4"];
  3828	      const active = order.filter((k) => logic[k] && logic[k].active === true);
  3829	      const nodes = Array.isArray(body && body.nodes) ? body.nodes : [];
  3830	      const activeStr = active.length === 0 ? "none" : active.join("+");
  3831	      return `nodes=${nodes.length} · active=[${activeStr}] · mode=auto_scrubber`;
  3832	    },
  3833	  },
  3834	  wow_b: {
  3835	    endpoint: "/api/monte-carlo/run",
  3836	    payload: { system_id: "thrust-reverser", n_trials: 1000, seed: 42 },
  3837	    summarize: (body) => {
  3838	      if (!body) return "(empty body)";
  3839	      const sr = typeof body.success_rate === "number" ? body.success_rate.toFixed(4) : body.success_rate;
  3840	      const failures = body.n_failures;
  3841	      const trials = body.n_trials;
  3842	      return `trials=${trials} · success_rate=${sr} · failures=${failures}`;
  3843	    },
  3844	  },
  3845	  wow_c: {
  3846	    endpoint: "/api/diagnosis/run",
  3847	    payload: { system_id: "thrust-reverser", outcome: "deploy_confirmed", max_results: 10 },
  3848	    summarize: (body) => {
  3849	      if (!body) return "(empty body)";
  3850	      const total = body.total_combos_found;
  3851	      const returned = Array.isArray(body.results) ? body.results.length : 0;
  3852	      const grid = body.grid_resolution;
  3853	      return `outcome=${body.outcome} · total_combos=${total} · returned=${returned} · grid=${grid}`;
  3854	    },
  3855	  },
  3856	};
  3857	
  3858	async function runWowScenario(wowId) {
  3859	  const scenario = WOW_SCENARIOS[wowId];
  3860	  const button = document.querySelector(
  3861	    `.workbench-wow-run-button[data-wow-id="${wowId}"]`,
  3862	  );
  3863	  const result = document.querySelector(
  3864	    `.workbench-wow-result[data-wow-result-for="${wowId}"]`,
  3865	  );
  3866	  if (!scenario || !result) {
  3867	    return;
  3868	  }
  3869	  if (button) {
  3870	    button.disabled = true;
  3871	  }
  3872	  result.removeAttribute("data-wow-state");
  3873	  result.textContent = `POST ${scenario.endpoint} ...`;
  3874	  // P1 R2 BLOCKER fix: bounded timeout via AbortController so a stalled
  3875	  // endpoint cannot freeze the card mid-demo.
  3876	  const controller =
  3877	    typeof AbortController !== "undefined" ? new AbortController() : null;
  3878	  const timeoutHandle = controller
  3879	    ? setTimeout(() => controller.abort(), WOW_REQUEST_TIMEOUT_MS)
  3880	    : null;
  3881	  try {
  3882	    const t0 = performance.now();
  3883	    const response = await fetch(scenario.endpoint, {
  3884	      method: "POST",
  3885	      headers: { "Content-Type": "application/json" },
  3886	      body: JSON.stringify(scenario.payload),
  3887	      signal: controller ? controller.signal : undefined,
  3888	    });
  3889	    const ms = Math.round(performance.now() - t0);
  3890	    let body = null;
  3891	    try {
  3892	      body = await response.json();
  3893	    } catch (_err) {
  3894	      body = null;
  3895	    }
  3896	    if (!response.ok) {
  3897	      result.setAttribute("data-wow-state", "error");
  3898	      const errMsg = body && body.error ? body.error : `HTTP ${response.status}`;
  3899	      result.textContent = `${response.status} · ${errMsg} · ${ms}ms`;
  3900	      return;
  3901	    }
  3902	    result.setAttribute("data-wow-state", "ok");
  3903	    result.textContent = `200 OK · ${scenario.summarize(body)} · ${ms}ms`;
  3904	  } catch (err) {
  3905	    result.setAttribute("data-wow-state", "error");
  3906	    if (err && err.name === "AbortError") {
  3907	      result.textContent = `timed out after ${WOW_REQUEST_TIMEOUT_MS}ms · click again to retry`;
  3908	    } else {
  3909	      result.textContent = `network error: ${err && err.message ? err.message : err}`;
  3910	    }
  3911	  } finally {
  3912	    if (timeoutHandle !== null) {
  3913	      clearTimeout(timeoutHandle);
  3914	    }
  3915	    if (button) {
  3916	      button.disabled = false;
  3917	    }
  3918	  }

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
   214	}
   215	
   216	.workbench-wow-result {
   217	  /* P3 R2 IMPORTANT fix: bump font-size from 0.78rem → 0.92rem so the
   218	     live-summary line is readable from across the room on a projector. */
   219	  min-height: 1.3rem;
   220	  padding: 0.55rem 0.7rem;
   221	  border-radius: 6px;
   222	  background: rgba(255, 255, 255, 0.04);
   223	  color: rgba(206, 223, 236, 0.86);
   224	  font-family: "SFMono-Regular", "Menlo", monospace;
   225	  font-size: 0.92rem;
   226	  line-height: 1.5;
   227	  white-space: pre-wrap;
   228	  word-break: break-word;
   229	}
   230	
   231	.workbench-wow-result[data-wow-state="ok"] {
   232	  border: 1px solid rgba(120, 220, 170, 0.35);

 succeeded in 0ms:
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
    75	              deploy=95%, feedback_mode=auto_scrubber) — under auto_scrubber pullback the
    76	              gates that latch are L2/L3/L4 (L1 drops out as reverser_not_deployed_eec
    77	              flips false mid-deploy, per <code>tests/e2e/test_wow_a_causal_chain.py</code>).
    78	            </p>
    79	            <button
    80	              type="button"
    81	              class="workbench-wow-run-button"
    82	              data-wow-action="run"
    83	              data-wow-id="wow_a"
    84	            >
    85	              一键运行 wow_a
    86	            </button>
    87	            <div
    88	              class="workbench-wow-result"
    89	              data-wow-result-for="wow_a"
    90	              role="status"
    91	              aria-live="polite"
    92	            >
    93	              尚未运行。
    94	            </div>
    95	          </article>
    96	          <article

exec
/bin/zsh -lc "nl -ba tests/test_workbench_wow_starters.py | sed -n '120,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   120	
   121	# ─── 3. Live endpoint contracts the cards depend on ──────────────────
   122	
   123	
   124	# ─── P1+P2+P4 R2 BLOCKER fix: lock exact canonical card payloads ─────
   125	#
   126	# The exact payloads are FROZEN via these literals. If workbench.js drifts
   127	# (e.g. n_trials → 50, max_results → 5, n1k → 0.5), the test below catches
   128	# it before it reaches a live demo.
   129	WOW_A_FROZEN_PAYLOAD = {
   130	    "tra_deg": -35,
   131	    "radio_altitude_ft": 2,
   132	    "engine_running": True,
   133	    "aircraft_on_ground": True,
   134	    "reverser_inhibited": False,
   135	    "eec_enable": True,
   136	    "n1k": 0.92,
   137	    "feedback_mode": "auto_scrubber",
   138	    "deploy_position_percent": 95,
   139	}
   140	WOW_B_FROZEN_PAYLOAD = {"system_id": "thrust-reverser", "n_trials": 1000, "seed": 42}
   141	WOW_C_FROZEN_PAYLOAD = {
   142	    "system_id": "thrust-reverser",
   143	    "outcome": "deploy_confirmed",
   144	    "max_results": 10,
   145	}
   146	
   147	
   148	def _extract_wow_scenarios_payloads_from_js() -> dict[str, dict]:
   149	    """Parse the WOW_SCENARIOS block out of workbench.js so the exact card
   150	    literals can be compared against the frozen e2e contracts."""
   151	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   152	    out: dict[str, dict] = {}
   153	    for wow_id, frozen in (
   154	        ("wow_a", WOW_A_FROZEN_PAYLOAD),
   155	        ("wow_b", WOW_B_FROZEN_PAYLOAD),
   156	        ("wow_c", WOW_C_FROZEN_PAYLOAD),
   157	    ):
   158	        # Each scenario is keyed by `<wow_id>: { ... }` inside WOW_SCENARIOS.
   159	        # We don't need a full JS parser: assert each frozen field appears
   160	        # in the file in a payload key:value form near the wow_id.
   161	        anchor = js.find(f"{wow_id}:")
   162	        assert anchor != -1, f"WOW_SCENARIOS missing entry for {wow_id}"
   163	        # Take a slice large enough to contain the whole payload object.
   164	        slice_ = js[anchor : anchor + 1200]
   165	        for k, v in frozen.items():
   166	            if isinstance(v, bool):
   167	                literal = "true" if v else "false"
   168	            elif isinstance(v, str):
   169	                literal = f'"{v}"'
   170	            else:
   171	                literal = str(v)
   172	            assert (
   173	                f"{k}: {literal}" in slice_
   174	            ), f"{wow_id}.{k} drift: expected `{k}: {literal}` near {wow_id}: in workbench.js"
   175	        out[wow_id] = frozen
   176	    return out
   177	
   178	
   179	def test_workbench_js_freezes_exact_canonical_payloads() -> None:
   180	    """Lock every shipped wow_a/b/c payload literal against the e2e contract.
   181	
   182	    P1+P2+P4 R2 BLOCKER fix — without this, n_trials/seed/max_results/n1k
   183	    can silently drift in workbench.js and the cards would no longer match
   184	    `tests/e2e/test_wow_a_causal_chain.py:51`,
   185	    `tests/e2e/test_wow_b_monte_carlo.py:_run`, or
   186	    `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed`.
   187	    """
   188	    _extract_wow_scenarios_payloads_from_js()
   189	
   190	
   191	def test_wow_a_live_endpoint_with_exact_card_payload(server) -> None:
   192	    """wow_a card POSTs the EXACT BEAT_DEEP_PAYLOAD; assert e2e contract."""
   193	    status, body = _post(server, "/api/lever-snapshot", WOW_A_FROZEN_PAYLOAD)
   194	    assert status == 200
   195	    assert isinstance(body.get("nodes"), list)
   196	    assert len(body["nodes"]) > 0
   197	    # P1+P2+P5 R2 BLOCKER fix: the card no longer overstates "L1–L4
   198	    # latched"; verify the actual e2e contract holds — under auto_scrubber
   199	    # BEAT_DEEP must latch logic2+logic3+logic4 (logic1 may drop out).
   200	    logic = body.get("logic", {}) or {}
   201	    assert isinstance(logic, dict), "wow_a response must expose `logic` dict"
   202	    active = {k for k, v in logic.items() if isinstance(v, dict) and v.get("active") is True}
   203	    assert {"logic2", "logic3", "logic4"} <= active, (
   204	        f"BEAT_DEEP must latch at least logic2+logic3+logic4, got {active}"
   205	    )
   206	
   207	
   208	def test_wow_b_live_endpoint_with_exact_card_payload(server) -> None:
   209	    """wow_b card POSTs n_trials=1000, seed=42 — probe with the SAME values."""
   210	    status, body = _post(server, "/api/monte-carlo/run", WOW_B_FROZEN_PAYLOAD)
   211	    assert status == 200
   212	    assert body["n_trials"] == 1000  # exact card value, not 100
   213	    assert "success_rate" in body
   214	    assert "n_failures" in body
   215	
   216	
   217	def test_wow_c_live_endpoint_with_exact_card_payload(server) -> None:
   218	    """wow_c card POSTs max_results=10 — probe with the SAME value."""
   219	    status, body = _post(server, "/api/diagnosis/run", WOW_C_FROZEN_PAYLOAD)
   220	    assert status == 200
   221	    assert body["outcome"] == "deploy_confirmed"
   222	    assert "total_combos_found" in body
   223	    assert "grid_resolution" in body
   224	    assert isinstance(body.get("results"), list)
   225	    assert len(body["results"]) <= 10  # bounded by max_results
   226	
   227	
   228	# ─── P4 R2 IMPORTANT fix: lock selector contract ─────────────────────
   229	
   230	
   231	@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
   232	def test_workbench_html_card_has_run_button_selector(wow_id: str) -> None:
   233	    """The click handler binds via .workbench-wow-run-button[data-wow-action="run"];
   234	    if the selector contract drifts the card becomes inert."""
   235	    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
   236	    # Each card must have a button with class workbench-wow-run-button,
   237	    # data-wow-action="run", and matching data-wow-id.
   238	    pattern = re.compile(
   239	        r'<button[^>]*?class="workbench-wow-run-button"[^>]*?'
   240	        r'data-wow-action="run"[^>]*?data-wow-id="' + re.escape(wow_id) + r'"',
   241	        re.DOTALL,
   242	    )
   243	    alt_pattern = re.compile(
   244	        r'<button[^>]*?data-wow-id="' + re.escape(wow_id) + r'"[^>]*?'
   245	        r'class="workbench-wow-run-button"[^>]*?data-wow-action="run"',
   246	        re.DOTALL,
   247	    )
   248	    assert pattern.search(html) or alt_pattern.search(html), (
   249	        f"wow card {wow_id} is missing the click-binding selector contract"
   250	    )
   251	
   252	
   253	# ─── P4 R2 IMPORTANT fix: lock workbench_start.html [REWRITE] copy ───
   254	
   255	
   256	def test_workbench_start_reflects_e11_05_shipped() -> None:
   257	    """The 3 [REWRITE] lines on workbench_start.html must claim E11-05 has shipped,
   258	    not the stale 'not yet shipped' text."""
   259	    html = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
   260	    # Positive claim (must appear): cards are live on /workbench.
   261	    assert "wow_a/b/c 起手卡片已上线（E11-05）" in html
   262	    # Negative claim (must NOT appear): the stale "not yet shipped" line.
   263	    assert "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" not in html
   264	    # Negative claim (must NOT appear): "no UI 走读 surface".
   265	    assert "没有 UI 走读 surface" not in html
   266	
   267	
   268	# ─── P1 R2 IMPORTANT fix: error-path UI assertions ──────────────────
   269	
   270	
   271	def test_workbench_js_runWowScenario_handles_http_error_and_timeout() -> None:
   272	    """The click handler must render HTTP-error and abort/timeout failures
   273	    distinctly, never a stuck `POST ... ` placeholder.
   274	
   275	    P1 R2 BLOCKER fix — without bounded timeout + abort path, the card
   276	    freezes mid-demo when an endpoint stalls.
   277	    """
   278	    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
   279	    # AbortController + bounded timeout
   280	    assert "AbortController" in js, "no abort path; stalled requests freeze the card"
   281	    assert "WOW_REQUEST_TIMEOUT_MS" in js, "no bounded timeout constant"
   282	    assert "AbortError" in js, "AbortError branch must render distinct copy"
   283	    # HTTP-error branch
   284	    assert 'data-wow-state", "error"' in js
   285	    # Re-enable the button on every exit (success / error / abort)
   286	    assert "button.disabled = false" in js
   287	    # Sanity: the timeout constant has a real numeric value, not 0.
   288	    m = re.search(r"WOW_REQUEST_TIMEOUT_MS\s*=\s*(\d+)", js)
   289	    assert m and int(m.group(1)) >= 1000, "timeout must be ≥ 1000ms"
   290	
   291	
   292	def test_workbench_html_serves_with_wow_section(server) -> None:
   293	    """Live-served /workbench page includes the wow starters section."""
   294	    status, html = _get(server, "/workbench")
   295	    assert status == 200
   296	    assert 'id="workbench-wow-starters"' in html
   297	    assert 'data-wow-id="wow_a"' in html
   298	    assert 'data-wow-id="wow_b"' in html
   299	    assert 'data-wow-id="wow_c"' in html

codex
我已经看到 R2 的代码层面闭环：`wow_a` 文案和摘要现在都按真实 logic gate 输出，timeout/abort 也在点击路径里了。下一步我会跑定向测试，再做一个真实 HTTP probe 确认 `logic2/3/4` 的 live 返回。
exec
/bin/zsh -lc 'pytest -q tests/test_workbench_wow_starters.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'pytest -q tests/e2e/test_wow_a_causal_chain.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 5 in 174ms:

8 deselected in 0.01s

 exited 1 in 2233ms:
........FF......                                                         [100%]
=================================== FAILURES ===================================
_______________ test_wow_b_live_endpoint_with_exact_card_payload _______________

server = <http.server.ThreadingHTTPServer object at 0x10939a4d0>

    def test_wow_b_live_endpoint_with_exact_card_payload(server) -> None:
        """wow_b card POSTs n_trials=1000, seed=42 — probe with the SAME values."""
>       status, body = _post(server, "/api/monte-carlo/run", WOW_B_FROZEN_PAYLOAD)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_workbench_wow_starters.py:210: 
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

self = <http.client.HTTPResponse object at 0x108e21270>

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
Exception occurred during processing of request from ('127.0.0.1', 64129)
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
_______________ test_wow_c_live_endpoint_with_exact_card_payload _______________

server = <http.server.ThreadingHTTPServer object at 0x10938b850>

    def test_wow_c_live_endpoint_with_exact_card_payload(server) -> None:
        """wow_c card POSTs max_results=10 — probe with the SAME value."""
>       status, body = _post(server, "/api/diagnosis/run", WOW_C_FROZEN_PAYLOAD)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_workbench_wow_starters.py:219: 
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

self = <http.client.HTTPResponse object at 0x108c1b3a0>

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
Exception occurred during processing of request from ('127.0.0.1', 64136)
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
FAILED tests/test_workbench_wow_starters.py::test_wow_b_live_endpoint_with_exact_card_payload
FAILED tests/test_workbench_wow_starters.py::test_wow_c_live_endpoint_with_exact_card_payload
2 failed, 14 passed in 2.06s

codex
定向回归里出现了一个失败项；我先把具体失败拿出来，判断是闭环没做好还是测试环境/选择器层面的偏差。另一条 e2e 目标文件被 pytest 配置整体 deselect 了，所以我会用 repo 内建的本地 HTTP probe 路径来补 live 验证。
codex
回归失败不是 R2 逻辑回归，而是本机测试环境缺库：`wow_b` 依赖 `numpy`，`wow_c` 依赖 `jsonschema`，本地直接炸在 import 阶段。我要把这和代码闭环分开处理，继续跑不依赖这两个包的 P1 相关路径，并补一个真实 `wow_a` HTTP probe。
exec
/bin/zsh -lc "nl -ba tests/test_workbench_wow_starters.py | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc "pytest -q tests/test_workbench_wow_starters.py -k 'wow_a_live_endpoint_with_exact_card_payload or workbench_js_freezes_exact_canonical_payloads or runWowScenario_handles_http_error_and_timeout or workbench_start_reflects_e11_05_shipped'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 715ms:
....                                                                     [100%]
4 passed, 12 deselected in 0.54s

exec
/bin/zsh -lc "python - <<'PY'
import http.client, json, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

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
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=10)
    conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    resp = conn.getresponse()
    body = json.loads(resp.read().decode('utf-8') or '{}')
    logic = body.get('logic') or {}
    active = [k for k in ('logic1','logic2','logic3','logic4') if isinstance(logic.get(k), dict) and logic[k].get('active') is True]
    print(json.dumps({
        'status': resp.status,
        'nodes_count': len(body.get('nodes') or []),
        'active_logic': active,
        'feedback_mode': body.get('feedback_mode'),
        'summary_preview': f\"nodes={len(body.get('nodes') or [])} · active=[{'+'.join(active) if active else 'none'}] · mode=auto_scrubber\",
    }, ensure_ascii=False))
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

codex
本机默认没有 `python` 别名，只有 `python3`。我直接改用 `python3` 继续做 live probe。
exec
/bin/zsh -lc "python3 - <<'PY'
import http.client, json, threading
from http.server import ThreadingHTTPServer
from well_harness.demo_server import DemoRequestHandler

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
server = ThreadingHTTPServer(('127.0.0.1', 0), DemoRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=10)
    conn.request('POST', '/api/lever-snapshot', body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    resp = conn.getresponse()
    body = json.loads(resp.read().decode('utf-8') or '{}')
    logic = body.get('logic') or {}
    active = [k for k in ('logic1','logic2','logic3','logic4') if isinstance(logic.get(k), dict) and logic[k].get('active') is True]
    print(json.dumps({
        'status': resp.status,
        'nodes_count': len(body.get('nodes') or []),
        'active_logic': active,
        'feedback_mode': body.get('feedback_mode'),
        'summary_preview': f\"nodes={len(body.get('nodes') or [])} · active=[{'+'.join(active) if active else 'none'}] · mode=auto_scrubber\",
    }, ensure_ascii=False))
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 638ms:
{"status": 200, "nodes_count": 19, "active_logic": ["logic2", "logic3", "logic4"], "feedback_mode": null, "summary_preview": "nodes=19 · active=[logic2+logic3+logic4] · mode=auto_scrubber"}

exec
/bin/zsh -lc "python3 - <<'PY'
from pathlib import Path
import subprocess
repo = Path('.')
out = subprocess.check_output(['git', 'diff', '--name-only', 'main..8882b7b'], text=True, cwd=repo)
paths = [p for p in out.splitlines() if any(token in p for token in ['controller.py','runner.py','models.py','src/well_harness/adapters/'])]
print('\\n'.join(paths) if paths else 'NO_TRUTH_ENGINE_TOUCHES')
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
NO_TRUTH_ENGINE_TOUCHES

R2 scope inspected, P1-specific findings checked against code/tests, and a live /api/lever-snapshot probe confirmed the wow_a active-set contract.
  ✓ Collect R2 scope and inspect diffs for the R1 findings relevant to P1
  ✓ Verify each P1 R1 finding against code and targeted tests
  ✓ Run at least one live probe for an uncertain path and form final verdict
codex
我已经有结论了。最后补一处 memory 引用定位，然后按你要的 closure-check 格式直接给 verdict。
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '791,822p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   805	
   806	## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查
   807	
   808	### rollout_summary_files
   809	
   810	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   811	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
   812	
   813	### keywords
   814	
   815	- 根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查, 当前无需 Opus 审查, Gate status: Approved, tools/gsd_notion_sync.py run, NOTION_WRITEBACK_TIMEOUT_S, P7-19, P7-20, P8-05, P8-06
   816	
   817	## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts
   818	
   819	### rollout_summary_files
   820	
   821	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
   822	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,879p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

codex
**APPROVE**

- `CLOSED` R1 `BLOCKER`: dishonest `wow_a` “L1–L4 latched” claim. The card copy now states the real auto-scrubber contract, and the summary is derived from `body.logic.logic1..logic4` instead of a hardcoded latch claim. See [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:74), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3825), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:191).

- `CLOSED` R1 `BLOCKER`: no fetch timeout / abort path. `runWowScenario()` now has `WOW_REQUEST_TIMEOUT_MS`, `AbortController`, distinct `AbortError` copy, and unconditional button re-enable in `finally`. See [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3802), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3874), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:271).

- `CLOSED` R1 `IMPORTANT`: regression lock was too weak. R2 freezes the shipped `wow_a/b/c` payload literals, probes `wow_a` with the exact card payload, and locks the HTTP-error / timeout contract. See [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:129), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:208), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:271), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3804).

- No new in-scope findings.

- Live probe cited: I ran a local `DemoRequestHandler` HTTP POST to `/api/lever-snapshot` with the shipped `wow_a` payload. It returned `200`, `nodes_count=19`, `active_logic=["logic2","logic3","logic4"]`, which matches the new UI summary contract `nodes=19 · active=[logic2+logic3+logic4] · mode=auto_scrubber`.

- Verification note: the exact P1 closure checks passed locally (`4 passed`). A full local repro of the `wow_b` / `wow_c` live-endpoint tests in this shell was blocked by missing `numpy` and `jsonschema`, so I did not treat that as an R2 regression. I also verified `main..8882b7b` does not touch `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/`.

**P1 — Junior FCS Engineer** (Tier-A, E11-05 R2)

tokens used
114,821
**APPROVE**

- `CLOSED` R1 `BLOCKER`: dishonest `wow_a` “L1–L4 latched” claim. The card copy now states the real auto-scrubber contract, and the summary is derived from `body.logic.logic1..logic4` instead of a hardcoded latch claim. See [workbench.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.html:74), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3825), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:191).

- `CLOSED` R1 `BLOCKER`: no fetch timeout / abort path. `runWowScenario()` now has `WOW_REQUEST_TIMEOUT_MS`, `AbortController`, distinct `AbortError` copy, and unconditional button re-enable in `finally`. See [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3802), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3874), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:271).

- `CLOSED` R1 `IMPORTANT`: regression lock was too weak. R2 freezes the shipped `wow_a/b/c` payload literals, probes `wow_a` with the exact card payload, and locks the HTTP-error / timeout contract. See [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:129), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:208), [test_workbench_wow_starters.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_workbench_wow_starters.py:271), [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:3804).

- No new in-scope findings.

- Live probe cited: I ran a local `DemoRequestHandler` HTTP POST to `/api/lever-snapshot` with the shipped `wow_a` payload. It returned `200`, `nodes_count=19`, `active_logic=["logic2","logic3","logic4"]`, which matches the new UI summary contract `nodes=19 · active=[logic2+logic3+logic4] · mode=auto_scrubber`.

- Verification note: the exact P1 closure checks passed locally (`4 passed`). A full local repro of the `wow_b` / `wow_c` live-endpoint tests in this shell was blocked by missing `numpy` and `jsonschema`, so I did not treat that as an R2 regression. I also verified `main..8882b7b` does not touch `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/`.

**P1 — Junior FCS Engineer** (Tier-A, E11-05 R2)

