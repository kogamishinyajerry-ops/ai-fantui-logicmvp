2026-04-25T15:28:02.180724Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T15:28:02.180787Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc541-4485-7643-9bd3-8f9c02fafd6a
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B rotation slot, E11-14 sub-phase).

# Context — E11-14 R2 (focused re-review)

You returned **CHANGES_REQUIRED** on E11-14 R1 (commit `e85ffb4`) with 6 findings. R2 (commit `75070ee`) addresses each one. Your job: verify R2 closes the gaps you raised, with the same live-probe rigor you used in R1.

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-14-manual-feedback-server-guard-20260425`
**PR:** #17
**Worktree HEAD:** `75070ee` (R2 fixes on top of R1 `e85ffb4`)

# What changed since R1

Read these files at HEAD (full, no rg head_limit):
- `src/well_harness/demo_server.py` (R2 deltas to `_validate_manual_override_signoff`, `parse_lever_snapshot_request`, `do_POST` set_vdt path)
- `src/well_harness/static/fan_console.html` (set_vdt fetch now sends `test_probe_acknowledgment:true`)
- `src/well_harness/static/demo.js` (canned-data warning)
- `src/well_harness/static/adversarial_test.py` (canned-data warning)
- `tests/conftest.py` (canned-data warning on MANUAL_OVERRIDE_SIGNOFF)
- `tests/test_lever_snapshot_manual_override_guard.py` (7 new R2 test cases)

# R2 fixes per finding (verify each)

**BLOCKER #1 — Impersonation (actor ≠ signed_by):**
R1 accepted `actor=Mallory` + `signed_by=TestActor` if ticket_ids matched. R2 added a strip-equality check in `_validate_manual_override_signoff` that returns 409 with `field=actor` and `message` containing "impersonation". Verify by reading the function and confirming the binding is enforced *unconditionally* when `feedback_mode=manual_feedback_override`. Test: `test_actor_signed_by_mismatch_returns_409`.

**BLOCKER #2 — set_vdt bypass:**
R1 left `/api/fantui/set_vdt` as a parallel write path with no sign-off. R2 added a `test_probe_acknowledgment` field requirement: missing/false → 409 `test_probe_unacknowledged` with message pointing to `/api/lever-snapshot`. Verify the gate runs *before* any state mutation. Tests: `test_set_vdt_requires_test_probe_acknowledgment`, `test_set_vdt_with_acknowledgment_succeeds`.

**IMPORTANT #3 — 400-vs-409 precedence:**
R1 returned 409 even when the request was structurally malformed (e.g. `deploy_position_percent="oops"`). R2 moved the `_validate_manual_override_signoff` call to AFTER all field parsing in `parse_lever_snapshot_request`, so 400 `invalid_lever_snapshot_input` precedes 409. Verify control flow. Test: `test_400_precedes_409_when_other_fields_malformed`.

**IMPORTANT #4 — Replay residual risk disclosure:**
Replay/nonce/freshness validation is deferred to E11-16. R2 adds a `residual_risk` field on every 409 response disclosing this gap and pointing to E11-16. Verify the disclosure is present on *all* 409 paths (not just one). Test: `test_residual_risk_disclosure_present_on_409`.

**IMPORTANT #5 — Test gaps:**
R2 added 7 tests covering: actor/signer mismatch, 400-vs-409 precedence, residual_risk disclosure, signoff non-dict, signoff signed_at empty, set_vdt unack, set_vdt with ack. Verify the new tests are non-redundant and exercise the edge cases.

**NIT #6 — Canned-data labelling:**
R2 added "⚠ CANNED ... NOT REAL AUTHENTICATION" warnings to `demo.js`, `adversarial_test.py`, `conftest.py`. Verify presence + clarity.

# Out of R2 scope (do NOT raise as new BLOCKER)

- Replay/nonce/freshness validation — deferred to E11-16, disclosed in `residual_risk`. R2 only locks the *structural* contract.
- Cryptographic signing of the sign-off envelope — explicit E11-16 scope, not E11-14.
- /workbench UI surfaces beyond the trust-affordance chip — E11-13 / E11-15 scope.
- Truth-engine red line (no controller/runner/models/adapters changes) — must be preserved.

# Your verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

For each R1 finding, state explicitly: CLOSED / OPEN / DEFERRED-WITH-DISCLOSURE.

If you raise NEW findings (not on R1's list), classify each as in-scope or out-of-scope per "Out of R2 scope" above. Out-of-scope findings should be NIT/INFO only, not BLOCKER.

Live-probe at least one path you are unsure about (boot the demo server, send a curl request, observe response). Cite the probe.

Truth-engine red line check: confirm `controller.py` / `runner.py` / `models.py` / `adapters/` are unchanged in R2 delta `e85ffb4..75070ee`.

Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-14 R2)**
codex
Reviewing R2 as a re-review against the six R1 findings, with code inspection first and at least one live probe before verdict. I’ll confirm the guard behavior, response precedence, disclosure coverage, test coverage, and the red-line diff between `e85ffb4..75070ee`.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'rg -n "LogicMVP|manual_feedback|E11-14|manual override|MANUAL_OVERRIDE_SIGNOFF|set_vdt|75070ee|e85ffb4" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
862:- VDT 模式, VDT 反馈, deploy_position_percent, manual_feedback_override, logic-note, 结果摘要先下沉, 诊断问答 frozen, /api/lever-snapshot, THR_LOCK, deploy_90_percent_vdt
868:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, material rewrite plus local UI launch)
878:- rollout_summaries/2026-04-10T06-34-44-9twF-rewrite_material_and_start_ui.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/10/rollout-2026-04-10T14-34-44-019d7619-a293-7681-baa7-381fd6276d45.jsonl, updated_at=2026-04-12T05:24:57+00:00, thread_id=019d7619-a293-7681-baa7-381fd6276d45, `8000` conflict handled by switching to `8001`)
879:- rollout_summaries/2026-04-07T06-17-29-49ud-well_harness_cockpit_vdt_logicboard_refinement.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T14-17-29-019d6696-c420-7481-af73-35d6f2431385.jsonl, updated_at=2026-04-09T03:18:57+00:00, thread_id=019d6696-c420-7481-af73-35d6f2431385, stable demo launch path on `8770`)
889:- rollout_summaries/2026-04-08T15-04-09-7j1J-reconstruct_ai_coding_development_log_and_leadership_speech.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-04-09-019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf.jsonl, updated_at=2026-04-08T15:12:08+00:00, thread_id=019d6d9f-4dc6-7bb3-9d6b-c6e48273fbbf, detailed Chinese summary and 5-minute leadership speech)
899:- rollout_summaries/2026-04-07T13-54-20-rmrz-well_harness_cockpit_ui_direction_change.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T21-54-20-019d6839-0565-7861-977f-70c0668de86d.jsonl, updated_at=2026-04-08T08:57:03+00:00, thread_id=019d6839-0565-7861-977f-70c0668de86d, UI direction was rejected and redirected toward lever-first interaction)
900:- rollout_summaries/2026-04-07T05-30-48-VWde-thrust_reverser_harness_audit_and_control_freeze.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/07/rollout-2026-04-07T13-30-48-019d666c-0536-7403-80c3-1216c53a4944.jsonl, updated_at=2026-04-08T08:22:56+00:00, thread_id=019d666c-0536-7403-80c3-1216c53a4944, frozen controller truth and simplified-plant caveat)

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
/bin/zsh -lc 'git rev-parse --show-toplevel && git status --short && git rev-parse HEAD && git branch --show-current' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-prompt.txt
75070eef3e07d577f91ccf481db732326f115a32
feat/e11-14-manual-feedback-server-guard-20260425

codex
I’ve confirmed the worktree is at `75070ee` on the requested branch and pulled the repo-specific memory pointers. Next I’m reading the exact R2 files and the `e85ffb4..75070ee` diff to verify each finding against code, tests, and the red-line boundary.
Focused re-review of E11-14 R2 against the six prior findings plus one live probe and a red-line diff check.
  → Inspect R2 target files and commit diff for server guard, UI warnings, and red-line boundary
  • Verify each R1 finding against code paths and new tests
  • Run at least one live probe against the demo server to confirm runtime behavior
  • Deliver verdict with CLOSED/OPEN/DEFERRED status per finding and any residual nits
exec
/bin/zsh -lc 'git diff --name-only e85ffb4..75070ee -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git diff --name-only e85ffb4..75070ee' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-14-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-output.md
.planning/phases/E11-workbench-engineer-first-ux/persona-P2-prompt.txt
docs/coordination/dev_handoff.md
docs/coordination/plan.md
docs/coordination/qa_report.md
docs/freeze/2026-04-10-freeze-demo-packet.md
src/well_harness/demo_server.py
src/well_harness/static/adversarial_test.py
src/well_harness/static/demo.js
src/well_harness/static/fan_console.html
tests/conftest.py
tests/test_lever_snapshot_manual_override_guard.py

exec
/bin/zsh -lc 'wc -l src/well_harness/demo_server.py src/well_harness/static/fan_console.html src/well_harness/static/demo.js src/well_harness/static/adversarial_test.py tests/conftest.py tests/test_lever_snapshot_manual_override_guard.py && git diff --stat e85ffb4..75070ee' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
    2745 src/well_harness/demo_server.py
     687 src/well_harness/static/fan_console.html
     548 src/well_harness/static/demo.js
     326 src/well_harness/static/adversarial_test.py
     105 tests/conftest.py
     251 tests/test_lever_snapshot_manual_override_guard.py
    4662 total
 .../E11-14-SURFACE-INVENTORY.md                    |   62 +
 .../PERSONA-ROTATION-STATE.md                      |    1 +
 .../persona-P2-output.md                           | 3531 +++++++++++++++++++-
 .../persona-P2-prompt.txt                          |   57 +
 docs/coordination/dev_handoff.md                   |    2 +-
 docs/coordination/plan.md                          |    2 +-
 docs/coordination/qa_report.md                     |    2 +-
 docs/freeze/2026-04-10-freeze-demo-packet.md       |    2 +-
 src/well_harness/demo_server.py                    |   65 +-
 src/well_harness/static/adversarial_test.py        |    4 +
 src/well_harness/static/demo.js                    |   12 +-
 src/well_harness/static/fan_console.html           |    5 +-
 tests/conftest.py                                  |    4 +
 tests/test_lever_snapshot_manual_override_guard.py |   99 +
 14 files changed, 3806 insertions(+), 42 deletions(-)

codex
I’ve confirmed the truth-engine red-line files are untouched in `e85ffb4..75070ee`. I’m now reading the full HEAD contents of the requested server, static, and test files in numbered chunks so the verdict stays tied to exact line-level evidence rather than just the diff.
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1,350p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""Small local UI server for the deterministic demo reasoning layer."""
     2	
     3	from __future__ import annotations
     4	
     5	import argparse
     6	from dataclasses import replace
     7	from functools import lru_cache
     8	import json
     9	import math
    10	import re
    11	from typing import Any
    12	import webbrowser
    13	from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    14	from pathlib import Path
    15	from urllib.parse import parse_qs, unquote, urlparse
    16	
    17	from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
    18	from well_harness.controller_adapter import build_reference_controller_adapter
    19	from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
    20	from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
    21	from well_harness.adapters.efds_adapter import build_efds_controller_adapter
    22	from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
    23	from well_harness.document_intake import (
    24	    apply_safe_schema_repairs,
    25	    assess_intake_packet,
    26	    build_clarification_brief,
    27	    intake_packet_from_dict,
    28	    intake_packet_to_dict,
    29	    intake_template_payload,
    30	)
    31	from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
    32	from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
    33	from well_harness.plant import PlantState, SimplifiedDeployPlant
    34	from well_harness.switches import LatchedThrottleSwitches, SwitchState
    35	from well_harness.timeline_engine import (
    36	    TimelinePlayer,
    37	    ValidationError as TimelineValidationError,
    38	    parse_timeline,
    39	)
    40	from well_harness.timeline_engine.executors.fantui import FantuiExecutor
    41	from well_harness.workbench_bundle import (
    42	    SandboxEscapeError,
    43	    archive_workbench_bundle,
    44	    build_workbench_bundle,
    45	    load_workbench_archive_manifest,
    46	    load_workbench_archive_restore_payload,
    47	)
    48	STATIC_DIR = Path(__file__).with_name("static")
    49	REFERENCE_PACKET_DIR = Path(__file__).with_name("reference_packets")
    50	REFERENCE_PACKET_PATH = REFERENCE_PACKET_DIR / "custom_reverse_control_v1.json"
    51	REPO_ROOT = Path(__file__).resolve().parents[2]
    52	RUNS_DIR = REPO_ROOT / "runs"
    53	DEFAULT_HOST = "127.0.0.1"
    54	DEFAULT_PORT = 8000
    55	# Server-side DoS guard: 10 MB, aligned with browser client limit.
    56	_MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
    57	CONTENT_TYPES = {
    58	    ".html": "text/html; charset=utf-8",
    59	    ".css": "text/css; charset=utf-8",
    60	    ".js": "application/javascript; charset=utf-8",
    61	    ".json": "application/json; charset=utf-8",
    62	    ".svg": "image/svg+xml; charset=utf-8",
    63	    ".ico": "image/x-icon",
    64	    ".png": "image/png",
    65	}
    66	SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
    67	SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
    68	TRA_L4_LOCK_DEG = -14.0
    69	MONITOR_TIMELINE_PATH = "/api/monitor-timeline"
    70	WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
    71	WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
    72	WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
    73	WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
    74	WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
    75	MONITOR_RA_START_FT = 7.0
    76	MONITOR_RA_RATE_FT_PER_S = 1.0
    77	MONITOR_TRA_START_S = 1.0
    78	MONITOR_TRA_RATE_DEG_PER_S = 10.0
    79	MONITOR_TRA_LOCK_DEG = -14.0
    80	MONITOR_VDT_START_S = 2.4
    81	MONITOR_VDT_RATE_PERCENT_PER_S = 50.0
    82	MONITOR_ACTIVE_END_S = 4.4
    83	MONITOR_TIMELINE_END_S = 7.0
    84	MONITOR_TIMELINE_COMPRESSION_RATIO = 10.0
    85	MONITOR_ENGINE_RUNNING = True
    86	MONITOR_AIRCRAFT_ON_GROUND = True
    87	MONITOR_REVERSER_INHIBITED = False
    88	MONITOR_EEC_ENABLE = True
    89	
    90	# Reverse diagnosis API (P19.6)
    91	DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
    92	# Monte Carlo reliability API (P19.7)
    93	MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
    94	# Hardware schema discovery (P19.8)
    95	HARDWARE_SCHEMA_PATH = "/api/hardware/schema"
    96	SENSITIVITY_SWEEP_PATH = "/api/sensitivity-sweep"
    97	# FANTUI stateful tick endpoints — live counterpart to C919 /api/tick.
    98	# The existing /api/lever-snapshot stays stateless; this triad is separate
    99	# so the two surfaces don't fight each other or share global state.
   100	FANTUI_TICK_PATH = "/api/fantui/tick"
   101	FANTUI_RESET_PATH = "/api/fantui/reset"
   102	FANTUI_LOG_PATH = "/api/fantui/log"
   103	FANTUI_STATE_PATH = "/api/fantui/state"
   104	FANTUI_SET_VDT_PATH = "/api/fantui/set_vdt"
   105	
   106	STATIC_ROUTE_ALIASES = {
   107	    "/favicon.ico": "favicon.svg",
   108	    "/apple-touch-icon.png": "apple-touch-icon.svg",
   109	}
   110	
   111	SENSITIVITY_SWEEP_DEFAULT_RA_VALUES = (2.0, 5.0, 10.0, 20.0, 40.0)
   112	SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES = (-28.0, -20.0, -15.0, -11.0, -6.0)
   113	SENSITIVITY_SWEEP_DEFAULT_OUTCOMES = (
   114	    "logic1_active",
   115	    "logic3_active",
   116	    "thr_lock_active",
   117	    "deploy_confirmed",
   118	)
   119	SENSITIVITY_SWEEP_ALLOWED_OUTCOMES = frozenset(
   120	    {
   121	        "logic1_active",
   122	        "logic2_active",
   123	        "logic3_active",
   124	        "thr_lock_active",
   125	        "deploy_confirmed",
   126	        "tls_unlocked",
   127	        "pls_unlocked",
   128	    }
   129	)
   130	
   131	_SYSTEM_YAML_MAP = {
   132	    "thrust-reverser": "thrust_reverser_hardware_v1.yaml",
   133	    "landing-gear": "landing_gear_hardware_v1.yaml",
   134	    "bleed-air": "bleed_air_hardware_v1.yaml",
   135	    "c919-etras": "c919_etras_hardware_v1.yaml",
   136	}
   137	
   138	# Systems whose YAML format is loadable by load_thrust_reverser_hardware.
   139	# Landing-gear and bleed-air YAMLs use a different schema and cannot be loaded
   140	# by the thrust-reverser-specific engine; they are served via the generic loader
   141	# in _handle_hardware_schema only.
   142	_SUPPORTED_FOR_ANALYSIS = frozenset({"thrust-reverser"})
   143	
   144	MONITOR_N1K = 35.0
   145	MONITOR_MAX_N1K_DEPLOY_LIMIT = 60.0
   146	LEVER_NUMERIC_INPUTS = {
   147	    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
   148	    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
   149	    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
   150	    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
   151	}
   152	LEVER_BOOLEAN_INPUTS = {
   153	    "engine_running": True,
   154	    "aircraft_on_ground": True,
   155	    "reverser_inhibited": False,
   156	    "eec_enable": True,
   157	}
   158	LEVER_FEEDBACK_MODES = {
   159	    "auto_scrubber",
   160	    "manual_feedback_override",
   161	}
   162	LEVER_SNAPSHOT_FAULT_NODE_ALIASES = {
   163	    "sw1_input": "sw1",
   164	    "sw2_input": "sw2",
   165	}
   166	LEVER_SNAPSHOT_FAULT_NODES = {
   167	    "sw1",
   168	    "sw2",
   169	    "radio_altitude_ft",
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

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '351,700p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   378	                    },
   379	                )
   380	                return
   381	            try:
   382	                pct = float(request_payload.get("deploy_position_percent", 0))
   383	            except (TypeError, ValueError):
   384	                self._send_json(400, {"error": "deploy_position_percent must be a number"})
   385	                return
   386	            try:
   387	                _FANTUI_SYSTEM.set_plant_position(pct)
   388	            except ValueError as exc:
   389	                self._send_json(400, {"error": str(exc)})
   390	                return
   391	            self._send_json(200, _FANTUI_SYSTEM.snapshot())
   392	            return
   393	        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
   394	            system_id = request_payload.get("system_id")
   395	            snapshot = request_payload.get("snapshot")
   396	            if not system_id:
   397	                self._send_json(400, {"error": "missing system_id"})
   398	                return
   399	            if not isinstance(snapshot, dict):
   400	                self._send_json(400, {"error": "snapshot must be a dict"})
   401	                return
   402	            result = system_snapshot_post_payload(system_id, snapshot)
   403	            if result.get("error"):
   404	                self._send_json(404, result)
   405	                return
   406	            self._send_json(200, result)
   407	            return
   408	        if parsed.path == WORKBENCH_BUNDLE_PATH:
   409	            response_payload, error_payload = build_workbench_bundle_response(request_payload)
   410	            if error_payload is not None:
   411	                self._send_json(400, error_payload)
   412	                return
   413	            self._send_json(200, response_payload)
   414	            return
   415	        if parsed.path == WORKBENCH_REPAIR_PATH:
   416	            response_payload, error_payload = build_workbench_safe_repair_response(request_payload)
   417	            if error_payload is not None:
   418	                self._send_json(400, error_payload)
   419	                return
   420	            self._send_json(200, response_payload)
   421	            return
   422	        if parsed.path == WORKBENCH_ARCHIVE_RESTORE_PATH:
   423	            response_payload, error_payload = build_workbench_archive_restore_response(request_payload)
   424	            if error_payload is not None:
   425	                self._send_json(400, error_payload)
   426	                return
   427	            self._send_json(200, response_payload)
   428	            return
   429	
   430	        # P19.6: Reverse diagnosis run (uses already-parsed request_payload)
   431	        if parsed.path == DIAGNOSIS_RUN_PATH:
   432	            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
   433	            outcome = str(request_payload.get("outcome", "")).strip()
   434	            if outcome not in VALID_OUTCOMES:
   435	                self._send_json(400, {
   436	                    "error": f"Invalid outcome: {outcome!r}. "
   437	                             f"Valid: {sorted(VALID_OUTCOMES)}"
   438	                })
   439	                return
   440	            max_results = min(int(request_payload.get("max_results", 1000)), 1000)
   441	            max_results = max(max_results, 0)
   442	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   443	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   444	                self._send_json(400, {
   445	                    "error": f"system_id {system_id!r} is not supported for diagnosis. "
   446	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   447	                })
   448	                return
   449	            yaml_path = self._hardware_yaml_path(system_id)
   450	            try:
   451	                engine = ReverseDiagnosisEngine(yaml_path)
   452	                report = engine.diagnose_and_report(outcome, max_results=max_results)
   453	                self._send_json(200, report)
   454	            except Exception as exc:
   455	                self._send_json(500, {"error": str(exc)})
   456	            return
   457	
   458	        # P19.7: Monte Carlo reliability simulation
   459	        if parsed.path == MONTE_CARLO_RUN_PATH:
   460	            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
   461	            n_trials_raw = request_payload.get("n_trials", 100)
   462	            try:
   463	                n_trials = int(n_trials_raw)
   464	            except (TypeError, ValueError):
   465	                self._send_json(400, {"error": "n_trials must be an integer"})
   466	                return
   467	            n_trials = max(1, min(n_trials, 10000))
   468	
   469	            seed = None
   470	            if "seed" in request_payload:
   471	                try:
   472	                    seed = int(request_payload["seed"])
   473	                except (TypeError, ValueError):
   474	                    self._send_json(400, {"error": "seed must be an integer"})
   475	                    return
   476	
   477	            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
   478	            if system_id not in _SUPPORTED_FOR_ANALYSIS:
   479	                self._send_json(400, {
   480	                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
   481	                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
   482	                })
   483	                return
   484	            yaml_path = self._hardware_yaml_path(system_id)
   485	            try:
   486	                engine = MonteCarloEngine(yaml_path)
   487	                result = engine.run(n_trials, seed=seed)
   488	                self._send_json(200, _reliability_result_to_dict(result))
   489	            except Exception as exc:
   490	                self._send_json(500, {"error": str(exc)})
   491	            return
   492	
   493	        if parsed.path == SENSITIVITY_SWEEP_PATH:
   494	            response_payload, error_payload = build_sensitivity_sweep_payload(request_payload)
   495	            if error_payload is not None:
   496	                self._send_json(400, error_payload)
   497	                return
   498	            self._send_json(200, response_payload)
   499	            return
   500	
   501	        prompt = str(request_payload.get("prompt", "")).strip()
   502	        if not prompt:
   503	            self._send_json(400, {"error": "missing_prompt"})
   504	            return
   505	
   506	        answer = answer_demo_prompt(prompt)
   507	        self._send_json(200, demo_answer_to_payload(answer))
   508	
   509	    # ── P19.6: Reverse diagnosis endpoint ─────────────────────────────────────
   510	
   511	    def _hardware_yaml_path(self, system_id: str = "thrust-reverser") -> str:
   512	        """Return the path to the hardware YAML config for the given system_id."""
   513	        import pathlib as _pathlib
   514	        import well_harness as _wh
   515	        pkg_root = _pathlib.Path(_wh.__file__).parent
   516	        repo_root = pkg_root.parent.parent
   517	        filename = _SYSTEM_YAML_MAP.get(system_id)
   518	        if filename is None:
   519	            raise FileNotFoundError(
   520	                f"Unknown system_id: {system_id!r}. Valid: {sorted(_SYSTEM_YAML_MAP)}"
   521	            )
   522	        return str(repo_root / "config" / "hardware" / filename)
   523	
   524	    # ── P19.8: Hardware schema endpoint ───────────────────────────────────────
   525	
   526	    def _handle_hardware_schema(self, system_id: str = "thrust-reverser") -> None:
   527	        """Return the full hardware YAML as a JSON dict (P19.8)."""
   528	        try:
   529	            yaml_path = self._hardware_yaml_path(system_id)
   530	            if system_id == "thrust-reverser":
   531	                from well_harness.hardware_schema import (
   532	                    _hardware_to_dict,
   533	                    load_thrust_reverser_hardware,
   534	                )
   535	
   536	                hw = load_thrust_reverser_hardware(yaml_path)
   537	                result = _hardware_to_dict(hw)
   538	                result["system_id"] = system_id
   539	            else:
   540	                # Generic YAML loader for non-thrust-reverser systems
   541	                import yaml
   542	
   543	                with open(yaml_path, encoding="utf-8") as f:
   544	                    result = yaml.safe_load(f)
   545	                if not isinstance(result, dict):
   546	                    raise ValueError(f"YAML root must be a dict, got {type(result).__name__}")
   547	                result["system_id"] = system_id
   548	
   549	            self._send_json(200, result)
   550	        except FileNotFoundError as exc:
   551	            self._send_json(400, {"error": str(exc)})
   552	        except Exception as exc:
   553	            self._send_json(500, {"error": str(exc)})
   554	
   555	    def _serve_static(self, relative_path: str):
   556	        static_root = STATIC_DIR.resolve()
   557	        target_path = (static_root / relative_path).resolve()
   558	        # Path must live inside static_root (traversal guard) and exist as a file.
   559	        # Phase UI-F (2026-04-22): allow nested static paths like
   560	        # /c919_etras_panel/circuit.html so the unified-nav can link to them.
   561	        try:
   562	            target_path.relative_to(static_root)
   563	        except ValueError:
   564	            self._send_json(404, {"error": "not_found"})
   565	            return
   566	        if not target_path.is_file():
   567	            self._send_json(404, {"error": "not_found"})
   568	            return
   569	
   570	        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
   571	        self._send_bytes(200, target_path.read_bytes(), content_type)
   572	
   573	    def _send_json(self, status_code: int, payload: dict):
   574	        # Compact JSON: no indentation (machine-to-machine API, not human-readable)
   575	        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
   576	        self._send_bytes(status_code, response, "application/json; charset=utf-8")
   577	
   578	    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
   579	        self.send_response(status_code)
   580	        self.send_header("Content-Type", content_type)
   581	        self.send_header("Content-Length", str(len(body)))
   582	        self.send_header("Cache-Control", "no-store")
   583	        self.end_headers()
   584	        self.wfile.write(body)
   585	
   586	
   587	def _clamp_tra(tra_deg: float, config: HarnessConfig) -> float:
   588	    return max(config.reverse_travel_min_deg, min(config.reverse_travel_max_deg, tra_deg))
   589	
   590	
   591	def _clamp(value: float, minimum: float, maximum: float) -> float:
   592	    return max(minimum, min(maximum, value))
   593	
   594	
   595	def _parse_float_input(request_payload: dict, field_name: str, options: dict) -> tuple[float | None, dict | None]:
   596	    raw_value = request_payload.get(field_name, options["default"])
   597	    if isinstance(raw_value, bool):
   598	        return None, {
   599	            "error": "invalid_lever_snapshot_input",
   600	            "field": field_name,
   601	            "message": f"{field_name} must be numeric.",
   602	        }
   603	    try:
   604	        value = float(raw_value)
   605	    except (TypeError, ValueError):
   606	        return None, {
   607	            "error": "invalid_lever_snapshot_input",
   608	            "field": field_name,
   609	            "message": f"{field_name} must be numeric.",
   610	        }
   611	    return _clamp(value, options["min"], options["max"]), None
   612	
   613	
   614	def _parse_bool_input(request_payload: dict, field_name: str, default: bool) -> tuple[bool | None, dict | None]:
   615	    raw_value = request_payload.get(field_name, default)
   616	    if isinstance(raw_value, bool):
   617	        return raw_value, None
   618	    if isinstance(raw_value, str):
   619	        normalized = raw_value.strip().lower()
   620	        if normalized in {"true", "1", "yes", "on"}:
   621	            return True, None
   622	        if normalized in {"false", "0", "no", "off"}:
   623	            return False, None
   624	    return None, {
   625	        "error": "invalid_lever_snapshot_input",
   626	        "field": field_name,
   627	        "message": f"{field_name} must be boolean.",
   628	    }
   629	
   630	
   631	def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
   632	    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
   633	    if not isinstance(raw_value, str):
   634	        return None, {
   635	            "error": "invalid_lever_snapshot_input",
   636	            "field": "feedback_mode",
   637	            "message": "feedback_mode must be a string.",
   638	        }
   639	    normalized = raw_value.strip()
   640	    if normalized not in LEVER_FEEDBACK_MODES:
   641	        return None, {
   642	            "error": "invalid_lever_snapshot_input",
   643	            "field": "feedback_mode",
   644	            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
   645	        }
   646	    return normalized, None
   647	
   648	
   649	# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
   650	# When feedback_mode = manual_feedback_override, the request must include
   651	# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
   652	# the endpoint returns 409 Conflict (paired with E11-13 UI affordance, this
   653	# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
   654	# stays put: no controller / runner / models / adapters/*.py changes.
   655	def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str) -> dict | None:
   656	    """Return error_payload (with `_status` 409) if signoff is missing/invalid; else None.
   657	
   658	    Only enforced when feedback_mode == "manual_feedback_override". For
   659	    auto_scrubber, this returns None unconditionally (no extra fields needed).
   660	    """
   661	    if feedback_mode != "manual_feedback_override":
   662	        return None
   663	
   664	    actor = request_payload.get("actor")
   665	    ticket_id = request_payload.get("ticket_id")
   666	    signoff = request_payload.get("manual_override_signoff")
   667	
   668	    def reject(field: str, message: str) -> dict:
   669	        return {
   670	            "_status": 409,
   671	            "error": "manual_override_unsigned",
   672	            "field": field,
   673	            "message": message,
   674	            "remediation": (
   675	                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
   676	                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
   677	            ),
   678	            # E11-14 R2 (P2 IMPORTANT #4, 2026-04-25): residual risk disclosure.
   679	            # The current sign-off check is structural only — same triplet can
   680	            # authorize multiple override payloads (replay) and signed_at is
   681	            # not freshness-checked. One-shot latch / nonce / freshness is the
   682	            # E11-16 approval-endpoint hardening scope. Until E11-16 lands,
   683	            # this guard is "shape correct" not "latched authorization".
   684	            "residual_risk": (
   685	                "Sign-off is structural only. Replay across payloads is not blocked; "
   686	                "signed_at is not freshness-validated. One-shot latch + nonce + "
   687	                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
   688	            ),
   689	        }
   690	
   691	    if not isinstance(actor, str) or not actor.strip():
   692	        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
   693	    if not isinstance(ticket_id, str) or not ticket_id.strip():
   694	        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")
   695	
   696	    if not isinstance(signoff, dict):
   697	        return reject(
   698	            "manual_override_signoff",
   699	            "manual_feedback_override requires a manual_override_signoff object.",
   700	        )

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1051,1400p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '701,1050p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1051	        # Runtime errors (unknown fault id, bad set_input value, …) get
  1052	        # surfaced as a 400 rather than a 500 so the UI can show the
  1053	        # validation message inline (Codex PR-2 MAJOR #3).
  1054	        return {
  1055	            "_status": 400,
  1056	            "error": "invalid_timeline",
  1057	            "message": str(exc),
  1058	        }
  1059	    return _timeline_trace_to_json(trace)
  1060	
  1061	
  1062	def _timeline_trace_to_json(trace) -> dict:
  1063	    return {
  1064	        "timeline": {
  1065	            "system": trace.timeline.system,
  1066	            "step_s": trace.timeline.step_s,
  1067	            "duration_s": trace.timeline.duration_s,
  1068	            "title": trace.timeline.title,
  1069	            "description": trace.timeline.description,
  1070	        },
  1071	        "frames": [
  1072	            {
  1073	                "tick": f.tick,
  1074	                "t_s": f.t_s,
  1075	                "phase": f.phase,
  1076	                "inputs": f.inputs,
  1077	                "outputs": f.outputs,
  1078	                "logic_states": f.logic_states,
  1079	                "active_faults": f.active_faults,
  1080	                "events_fired": f.events_fired,
  1081	            }
  1082	            for f in trace.frames
  1083	        ],
  1084	        "transitions": [
  1085	            {
  1086	                "tick": f.tick,
  1087	                "t_s": f.t_s,
  1088	                "phase": f.phase,
  1089	                "logic_states": f.logic_states,
  1090	                "active_faults": f.active_faults,
  1091	            }
  1092	            for f in trace.transitions
  1093	        ],
  1094	        "assertions": [
  1095	            {
  1096	                "at_s": a.at_s,
  1097	                "target": a.target,
  1098	                "expected": a.expected,
  1099	                "observed": a.observed,
  1100	                "passed": a.passed,
  1101	                "note": a.note,
  1102	            }
  1103	            for a in trace.assertions
  1104	        ],
  1105	        "outcome": {
  1106	            "deployed_successfully": trace.outcome.deployed_successfully,
  1107	            "thr_lock_released": trace.outcome.thr_lock_released,
  1108	            "logic_first_active_t_s": trace.outcome.logic_first_active_t_s,
  1109	            "logic_first_blocked_t_s": trace.outcome.logic_first_blocked_t_s,
  1110	            "failure_cascade": trace.outcome.failure_cascade,
  1111	        },
  1112	    }
  1113	
  1114	
  1115	def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
  1116	    lever_inputs = {}
  1117	    for field_name, options in LEVER_NUMERIC_INPUTS.items():
  1118	        value, error_payload = _parse_float_input(request_payload, field_name, options)
  1119	        if error_payload is not None:
  1120	            return None, error_payload
  1121	        lever_inputs[field_name] = value
  1122	
  1123	    config = HarnessConfig()
  1124	    lever_inputs["tra_deg"] = _clamp_tra(lever_inputs["tra_deg"], config)
  1125	
  1126	    for field_name, default in LEVER_BOOLEAN_INPUTS.items():
  1127	        value, error_payload = _parse_bool_input(request_payload, field_name, default)
  1128	        if error_payload is not None:
  1129	            return None, error_payload
  1130	        lever_inputs[field_name] = value
  1131	
  1132	    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
  1133	    if error_payload is not None:
  1134	        return None, error_payload
  1135	    lever_inputs["feedback_mode"] = feedback_mode
  1136	
  1137	    # E11-14 R1 had the guard here; moved to the END of structural parsing
  1138	    # in R2 (P2 IMPORTANT #3, 2026-04-25): a malformed
  1139	    # deploy_position_percent="oops" + missing signoff used to return 409
  1140	    # manual_override_unsigned, masking the real 400. Authority guard now
  1141	    # runs on otherwise-well-formed manual-override requests only.
  1142	
  1143	    deploy_position_percent, error_payload = _parse_float_input(
  1144	        request_payload,
  1145	        "deploy_position_percent",
  1146	        {"default": 0.0, "min": 0.0, "max": 100.0},
  1147	    )
  1148	    if error_payload is not None:
  1149	        return None, error_payload
  1150	    lever_inputs["deploy_position_percent"] = deploy_position_percent
  1151	
  1152	    fault_injections = request_payload.get("fault_injections")
  1153	    if fault_injections is not None:
  1154	        if not isinstance(fault_injections, list):
  1155	            return None, {
  1156	                "error": "invalid_fault_injections",
  1157	                "message": "fault_injections must be a list",
  1158	            }
  1159	        normalized_faults = []
  1160	        for fault in fault_injections:
  1161	            if not isinstance(fault, dict):
  1162	                return None, {
  1163	                    "error": "invalid_fault_injections",
  1164	                    "message": "each fault_injection must be an object",
  1165	                }
  1166	            node_id = str(fault.get("node_id", "")).strip()
  1167	            fault_type = str(fault.get("fault_type", "")).strip()
  1168	            if node_id not in LEVER_SNAPSHOT_FAULT_NODES:
  1169	                return None, {
  1170	                    "error": "invalid_fault_injection_node",
  1171	                    "message": f"Unknown node_id: {node_id}",
  1172	                }
  1173	            if fault_type not in LEVER_SNAPSHOT_FAULT_TYPES:
  1174	                return None, {
  1175	                    "error": "invalid_fault_type",
  1176	                    "message": f"Unknown fault_type: {fault_type}",
  1177	                }
  1178	            normalized_faults.append(
  1179	                {
  1180	                    "node_id": _normalize_fault_injection_node_id(node_id),
  1181	                    "fault_type": fault_type,
  1182	                }
  1183	            )
  1184	        if normalized_faults:
  1185	            lever_inputs["_fault_injections"] = normalized_faults
  1186	
  1187	    # E11-14 R2 (P2 IMPORTANT #3): authority guard runs AFTER structural
  1188	    # parsing so 400 (malformed) precedes 409 (unsigned). No-op for
  1189	    # auto_scrubber; returns 409 payload with `_status` hint when signoff
  1190	    # missing/invalid for manual_feedback_override.
  1191	    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
  1192	    if signoff_error is not None:
  1193	        return None, signoff_error
  1194	
  1195	    return lever_inputs, None
  1196	
  1197	
  1198	def default_workbench_archive_root() -> Path:
  1199	    return (Path.cwd() / "artifacts" / "workbench-bundles").resolve()
  1200	
  1201	
  1202	def reference_workbench_packet_payload() -> dict:
  1203	    return json.loads(REFERENCE_PACKET_PATH.read_text(encoding="utf-8"))
  1204	
  1205	
  1206	def build_explain_runtime_payload() -> dict[str, Any]:
  1207	    # LLM features shelved in Phase A (2026-04-22). Return a stable idle payload
  1208	    # so workbench clients can still render the runtime panel without runtime error.
  1209	    return {
  1210	        "status": "shelved",
  1211	        "status_source": "runtime_config",
  1212	        "llm_backend": "",
  1213	        "llm_model": "",
  1214	        "response_source": "unknown",
  1215	        "cached_at": "",
  1216	        "observed_at_utc": "",
  1217	        "verified_cache_hits": 0,
  1218	        "expected_count": 0,
  1219	        "backend_match": None,
  1220	        "requested_backend": "",
  1221	        "requested_model": "",
  1222	        "detail": "LLM features shelved — see archive/shelved/llm-features/SHELVED.md.",
  1223	        "boundary_note": "这是 explain runtime / pitch 运维状态，不是新的控制真值。",
  1224	    }
  1225	
  1226	
  1227	def recent_workbench_archive_summaries(*, limit: int = 6) -> list[dict]:
  1228	    archive_root = default_workbench_archive_root()
  1229	    if not archive_root.is_dir():
  1230	        return []
  1231	
  1232	    summaries: list[dict] = []
  1233	    for archive_dir in archive_root.iterdir():
  1234	        if not archive_dir.is_dir():
  1235	            continue
  1236	        manifest_path = archive_dir / "archive_manifest.json"
  1237	        if not manifest_path.is_file():
  1238	            continue
  1239	        try:
  1240	            manifest = load_workbench_archive_manifest(manifest_path)
  1241	        except (OSError, ValueError, json.JSONDecodeError):
  1242	            continue
  1243	
  1244	        bundle = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
  1245	        files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
  1246	        summaries.append(
  1247	            {
  1248	                "archive_dir": str(archive_dir.resolve()),
  1249	                "manifest_path": str(manifest_path.resolve()),
  1250	                "created_at_utc": manifest.get("created_at_utc"),
  1251	                "system_id": bundle.get("system_id"),
  1252	                "system_title": bundle.get("system_title"),
  1253	                "bundle_kind": bundle.get("bundle_kind"),
  1254	                "ready_for_spec_build": bundle.get("ready_for_spec_build"),
  1255	                "selected_scenario_id": bundle.get("selected_scenario_id"),
  1256	                "selected_fault_mode_id": bundle.get("selected_fault_mode_id"),
  1257	                "has_workspace_handoff": files.get("workspace_handoff_json") is not None,
  1258	                "has_workspace_snapshot": files.get("workspace_snapshot_json") is not None,
  1259	            }
  1260	        )
  1261	
  1262	    summaries.sort(
  1263	        key=lambda item: (
  1264	            str(item.get("created_at_utc") or ""),
  1265	            str(item.get("archive_dir") or ""),
  1266	        ),
  1267	        reverse=True,
  1268	    )
  1269	    return summaries[:limit]
  1270	
  1271	
  1272	def workbench_bootstrap_payload() -> dict:
  1273	    return {
  1274	        "template_packet": intake_template_payload(),
  1275	        "reference_packet": reference_workbench_packet_payload(),
  1276	        "default_archive_root": str(default_workbench_archive_root()),
  1277	        "recent_archives": recent_workbench_archive_summaries(),
  1278	        "explain_runtime": build_explain_runtime_payload(),
  1279	    }
  1280	
  1281	
  1282	def workbench_recent_archives_payload() -> dict:
  1283	    return {
  1284	        "default_archive_root": str(default_workbench_archive_root()),
  1285	        "recent_archives": recent_workbench_archive_summaries(),
  1286	    }
  1287	
  1288	
  1289	def _optional_request_float_list(
  1290	    payload: dict,
  1291	    field_name: str,
  1292	    *,
  1293	    default: tuple[float, ...],
  1294	) -> tuple[tuple[float, ...], dict | None]:
  1295	    raw_value = payload.get(field_name)
  1296	    if raw_value is None:
  1297	        return default, None
  1298	    if not isinstance(raw_value, list) or not raw_value:
  1299	        return default, {
  1300	            "error": "invalid_sensitivity_sweep_request",
  1301	            "field": field_name,
  1302	            "message": f"{field_name} must be a non-empty list of finite numbers.",
  1303	        }
  1304	
  1305	    normalized: list[float] = []
  1306	    for item in raw_value:
  1307	        if isinstance(item, bool):
  1308	            return default, {
  1309	                "error": "invalid_sensitivity_sweep_request",
  1310	                "field": field_name,
  1311	                "message": f"{field_name} must be numeric.",
  1312	            }
  1313	        try:
  1314	            value = float(item)
  1315	        except (TypeError, ValueError):
  1316	            return default, {
  1317	                "error": "invalid_sensitivity_sweep_request",
  1318	                "field": field_name,
  1319	                "message": f"{field_name} must be numeric.",
  1320	            }
  1321	        if not math.isfinite(value):
  1322	            return default, {
  1323	                "error": "invalid_numeric_value",
  1324	                "field": field_name,
  1325	                "message": f"{field_name} must contain only finite numbers.",
  1326	            }
  1327	        normalized.append(value)
  1328	    return tuple(normalized), None
  1329	
  1330	
  1331	def _stable_numeric_key(value: float) -> str:
  1332	    numeric = float(value)
  1333	    if numeric.is_integer():
  1334	        return str(int(numeric))
  1335	    return format(numeric, "g")
  1336	
  1337	
  1338	def _sensitivity_outcome_matches(snapshot: dict, outcome: str) -> bool:
  1339	    outputs = snapshot.get("outputs") if isinstance(snapshot.get("outputs"), dict) else {}
  1340	    hud = snapshot.get("hud") if isinstance(snapshot.get("hud"), dict) else {}
  1341	    if outcome == "logic1_active":
  1342	        return bool(outputs.get("logic1_active"))
  1343	    if outcome == "logic2_active":
  1344	        return bool(outputs.get("logic2_active"))
  1345	    if outcome == "logic3_active":
  1346	        return bool(outputs.get("logic3_active"))
  1347	    if outcome == "thr_lock_active":
  1348	        return bool(outputs.get("throttle_electronic_lock_release_cmd"))
  1349	    if outcome == "deploy_confirmed":
  1350	        return bool(hud.get("deploy_90_percent_vdt"))
  1351	    if outcome == "tls_unlocked":
  1352	        return bool(hud.get("tls_unlocked_ls"))
  1353	    if outcome == "pls_unlocked":
  1354	        return bool(hud.get("pls_unlocked_ls"))
  1355	    raise ValueError(f"Unsupported outcome: {outcome}")
  1356	
  1357	
  1358	def build_sensitivity_sweep_payload(request_payload: dict) -> tuple[dict | None, dict | None]:
  1359	    system_id = str(request_payload.get("system_id", "thrust-reverser")).strip() or "thrust-reverser"
  1360	    if system_id != "thrust-reverser":
  1361	        return None, {
  1362	            "error": "unsupported_system",
  1363	            "message": "sensitivity sweep currently supports only 'thrust-reverser'.",
  1364	        }
  1365	
  1366	    radio_altitude_ft_values, error_payload = _optional_request_float_list(
  1367	        request_payload,
  1368	        "radio_altitude_ft_values",
  1369	        default=SENSITIVITY_SWEEP_DEFAULT_RA_VALUES,
  1370	    )
  1371	    if error_payload is not None:
  1372	        return None, error_payload
  1373	
  1374	    tra_deg_values, error_payload = _optional_request_float_list(
  1375	        request_payload,
  1376	        "tra_deg_values",
  1377	        default=SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES,
  1378	    )
  1379	    if error_payload is not None:
  1380	        return None, error_payload
  1381	
  1382	    outcomes, error_payload = _optional_request_string_list(request_payload, "outcomes")
  1383	    if error_payload is not None:
  1384	        error_payload["error"] = "invalid_sensitivity_sweep_request"
  1385	        return None, error_payload
  1386	    requested_outcomes = outcomes or SENSITIVITY_SWEEP_DEFAULT_OUTCOMES
  1387	    invalid_outcomes = [
  1388	        outcome
  1389	        for outcome in requested_outcomes
  1390	        if outcome not in SENSITIVITY_SWEEP_ALLOWED_OUTCOMES
  1391	    ]
  1392	    if invalid_outcomes:
  1393	        return None, {
  1394	            "error": "invalid_sensitivity_outcome",
  1395	            "message": (
  1396	                f"Unsupported outcomes: {invalid_outcomes}. "
  1397	                f"Valid: {sorted(SENSITIVITY_SWEEP_ALLOWED_OUTCOMES)}"
  1398	            ),
  1399	        }
  1400	

 succeeded in 0ms:
   701	    signed_by = signoff.get("signed_by")
   702	    signed_at = signoff.get("signed_at")
   703	    signoff_ticket = signoff.get("ticket_id")
   704	    if not isinstance(signed_by, str) or not signed_by.strip():
   705	        return reject(
   706	            "manual_override_signoff.signed_by",
   707	            "manual_override_signoff.signed_by must be a non-empty string.",
   708	        )
   709	    if not isinstance(signed_at, str) or not signed_at.strip():
   710	        return reject(
   711	            "manual_override_signoff.signed_at",
   712	            "manual_override_signoff.signed_at must be a non-empty timestamp string.",
   713	        )
   714	    if not isinstance(signoff_ticket, str) or not signoff_ticket.strip():
   715	        return reject(
   716	            "manual_override_signoff.ticket_id",
   717	            "manual_override_signoff.ticket_id must be a non-empty string.",
   718	        )
   719	    if signoff_ticket.strip() != ticket_id.strip():
   720	        return reject(
   721	            "manual_override_signoff.ticket_id",
   722	            "manual_override_signoff.ticket_id must match the request's ticket_id.",
   723	        )
   724	
   725	    # E11-14 R2 fix (P2 BLOCKER #1, 2026-04-25): actor must equal
   726	    # manual_override_signoff.signed_by. Without this binding, an attacker
   727	    # can submit `actor="Mallory"` with `signed_by="Kogami"` and the server
   728	    # would accept it (P2 verified via live probe). Bind requester identity
   729	    # to the signoff's signer.
   730	    if signed_by.strip() != actor.strip():
   731	        return reject(
   732	            "actor",
   733	            "actor must match manual_override_signoff.signed_by (impersonation guard).",
   734	        )
   735	
   736	    return None
   737	
   738	
   739	def _normalize_fault_injection_node_id(node_id: str) -> str:
   740	    normalized = str(node_id or "").strip()
   741	    return LEVER_SNAPSHOT_FAULT_NODE_ALIASES.get(normalized, normalized)
   742	
   743	
   744	def _fault_injection_map(fault_injections: list[dict] | None) -> dict[str, str]:
   745	    fault_map: dict[str, str] = {}
   746	    for fault in fault_injections or []:
   747	        node_id = _normalize_fault_injection_node_id(fault.get("node_id", ""))
   748	        fault_type = str(fault.get("fault_type", "")).strip()
   749	        if node_id and fault_type:
   750	            fault_map[node_id] = fault_type
   751	    return fault_map
   752	
   753	
   754	def _append_unique(values: list[str], value: str) -> None:
   755	    if value not in values:
   756	        values.append(value)
   757	
   758	
   759	def _apply_switch_fault_injections(
   760	    switch_state: SwitchState,
   761	    fault_map: dict[str, str],
   762	) -> SwitchState:
   763	    sw1 = switch_state.sw1
   764	    if fault_map.get("sw1") == "stuck_off":
   765	        sw1 = False
   766	    elif fault_map.get("sw1") == "stuck_on":
   767	        sw1 = True
   768	
   769	    sw2 = switch_state.sw2
   770	    if fault_map.get("sw2") == "stuck_off":
   771	        sw2 = False
   772	    elif fault_map.get("sw2") == "stuck_on":
   773	        sw2 = True
   774	
   775	    if sw1 == switch_state.sw1 and sw2 == switch_state.sw2:
   776	        return switch_state
   777	
   778	    return SwitchState(
   779	        previous_tra_deg=switch_state.previous_tra_deg,
   780	        sw1=sw1,
   781	        sw2=sw2,
   782	    )
   783	
   784	
   785	def _apply_sensor_fault_injections(sensors, fault_map: dict[str, str]):
   786	    sensor_updates = {}
   787	
   788	    if fault_map.get("tls115") == "sensor_zero":
   789	        sensor_updates["tls_unlocked_ls"] = False
   790	
   791	    if fault_map.get("vdt90") == "cmd_blocked":
   792	        sensor_updates["deploy_90_percent_vdt"] = False
   793	
   794	    if not sensor_updates:
   795	        return sensors
   796	
   797	    return replace(sensors, **sensor_updates)
   798	
   799	
   800	def _apply_output_fault_injections(outputs, fault_map: dict[str, str]):
   801	    output_updates = {}
   802	
   803	    if fault_map.get("tls115") == "sensor_zero":
   804	        output_updates["tls_115vac_cmd"] = False
   805	
   806	    if fault_map.get("logic1") == "logic_stuck_false":
   807	        output_updates["logic1_active"] = False
   808	        output_updates["tls_115vac_cmd"] = False
   809	
   810	    if fault_map.get("logic2") == "logic_stuck_false":
   811	        output_updates["logic2_active"] = False
   812	        output_updates["etrac_540vdc_cmd"] = False
   813	
   814	    if fault_map.get("logic3") == "logic_stuck_false":
   815	        output_updates["logic3_active"] = False
   816	        output_updates["eec_deploy_cmd"] = False
   817	        output_updates["pls_power_cmd"] = False
   818	        output_updates["pdu_motor_cmd"] = False
   819	
   820	    if fault_map.get("logic4") == "logic_stuck_false":
   821	        output_updates["logic4_active"] = False
   822	        output_updates["throttle_electronic_lock_release_cmd"] = False
   823	
   824	    if fault_map.get("thr_lock") == "cmd_blocked":
   825	        output_updates["throttle_electronic_lock_release_cmd"] = False
   826	
   827	    if not output_updates:
   828	        return outputs
   829	
   830	    return replace(outputs, **output_updates)
   831	
   832	
   833	def _fault_reason(fault_type: str) -> str:
   834	    return f"{FAULT_INJECTION_REASON}:{fault_type}"
   835	
   836	
   837	def _set_faulted_node_state(
   838	    node_payload: dict | None,
   839	    *,
   840	    state: str,
   841	    reason: str | None = None,
   842	) -> None:
   843	    if node_payload is None:
   844	        return
   845	    node_payload["state"] = state
   846	    if state == "blocked":
   847	        blocked_by = list(node_payload.get("blocked_by") or [])
   848	        if reason:
   849	            _append_unique(blocked_by, reason)
   850	        node_payload["blocked_by"] = blocked_by
   851	        return
   852	    node_payload["blocked_by"] = []
   853	
   854	
   855	def _apply_fault_injections_to_snapshot_payload(
   856	    result: dict,
   857	    fault_injections: list[dict] | None,
   858	) -> dict:
   859	    fault_map = _fault_injection_map(fault_injections)
   860	    if not fault_map:
   861	        return result
   862	
   863	    nodes_by_id = {
   864	        node["id"]: node
   865	        for node in result.get("nodes", [])
   866	        if isinstance(node, dict) and "id" in node
   867	    }
   868	    input_payload = result.get("input")
   869	    hud_payload = result.get("hud")
   870	    outputs_payload = result.get("outputs")
   871	    logic_payload = result.get("logic")
   872	
   873	    for node_id, fault_type in fault_map.items():
   874	        reason = _fault_reason(fault_type)
   875	
   876	        if node_id == "sw1":
   877	            active = fault_type == "stuck_on"
   878	            if isinstance(hud_payload, dict):
   879	                hud_payload["sw1"] = active
   880	            _set_faulted_node_state(
   881	                nodes_by_id.get("sw1"),
   882	                state="active" if active else "inactive",
   883	            )
   884	            continue
   885	
   886	        if node_id == "sw2":
   887	            active = fault_type == "stuck_on"
   888	            if isinstance(hud_payload, dict):
   889	                hud_payload["sw2"] = active
   890	            _set_faulted_node_state(
   891	                nodes_by_id.get("sw2"),
   892	                state="active" if active else "inactive",
   893	            )
   894	            continue
   895	
   896	        if node_id == "radio_altitude_ft" and fault_type == "sensor_zero":
   897	            if isinstance(input_payload, dict):
   898	                input_payload["radio_altitude_ft"] = 0.0
   899	            if isinstance(hud_payload, dict):
   900	                hud_payload["radio_altitude_ft"] = 0.0
   901	            _set_faulted_node_state(nodes_by_id.get("radio_altitude_ft"), state="inactive")
   902	            continue
   903	
   904	        if node_id == "n1k" and fault_type == "sensor_zero":
   905	            if isinstance(input_payload, dict):
   906	                input_payload["n1k"] = 0.0
   907	            if isinstance(hud_payload, dict):
   908	                hud_payload["n1k"] = 0.0
   909	            _set_faulted_node_state(nodes_by_id.get("n1k"), state="inactive")
   910	            continue
   911	
   912	        if node_id == "tls115" and fault_type == "sensor_zero":
   913	            if isinstance(outputs_payload, dict):
   914	                outputs_payload["tls_115vac_cmd"] = False
   915	            _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
   916	            continue
   917	
   918	        if node_id in {"logic1", "logic2", "logic3", "logic4"} and fault_type == "logic_stuck_false":
   919	            logic_entry = logic_payload.get(node_id) if isinstance(logic_payload, dict) else None
   920	            if isinstance(logic_entry, dict):
   921	                logic_entry["active"] = False
   922	                failed_conditions = list(logic_entry.get("failed_conditions") or [])
   923	                _append_unique(failed_conditions, reason)
   924	                logic_entry["failed_conditions"] = failed_conditions
   925	
   926	            if isinstance(outputs_payload, dict):
   927	                outputs_payload[f"{node_id}_active"] = False
   928	
   929	            _set_faulted_node_state(nodes_by_id.get(node_id), state="blocked", reason=reason)
   930	
   931	            if node_id == "logic1":
   932	                if isinstance(outputs_payload, dict):
   933	                    outputs_payload["tls_115vac_cmd"] = False
   934	                _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
   935	            elif node_id == "logic2":
   936	                if isinstance(outputs_payload, dict):
   937	                    outputs_payload["etrac_540vdc_cmd"] = False
   938	                _set_faulted_node_state(nodes_by_id.get("etrac_540v"), state="inactive")
   939	            elif node_id == "logic3":
   940	                if isinstance(outputs_payload, dict):
   941	                    outputs_payload["eec_deploy_cmd"] = False
   942	                    outputs_payload["pls_power_cmd"] = False
   943	                    outputs_payload["pdu_motor_cmd"] = False
   944	                _set_faulted_node_state(nodes_by_id.get("eec_deploy"), state="inactive")
   945	                _set_faulted_node_state(nodes_by_id.get("pls_power"), state="inactive")
   946	                _set_faulted_node_state(nodes_by_id.get("pdu_motor"), state="inactive")
   947	            elif node_id == "logic4":
   948	                if isinstance(outputs_payload, dict):
   949	                    outputs_payload["throttle_electronic_lock_release_cmd"] = False
   950	                _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
   951	            continue
   952	
   953	        if node_id == "thr_lock" and fault_type == "cmd_blocked":
   954	            if isinstance(outputs_payload, dict):
   955	                outputs_payload["throttle_electronic_lock_release_cmd"] = False
   956	            _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
   957	            continue
   958	
   959	        if node_id == "vdt90" and fault_type == "cmd_blocked":
   960	            if isinstance(hud_payload, dict):
   961	                hud_payload["deploy_90_percent_vdt"] = False
   962	            _set_faulted_node_state(nodes_by_id.get("vdt90"), state="blocked", reason=reason)
   963	
   964	    result["active_fault_node_ids"] = list(fault_map.keys())
   965	    result["fault_injections"] = fault_injections or []
   966	    return result
   967	
   968	
   969	_TIMELINE_MAX_DURATION_S = 600.0
   970	_TIMELINE_MIN_STEP_S = 0.01
   971	# Belt-and-braces cap so a user cannot request 600s / 0.01s = 60,000 ticks
   972	# just because each individual bound is within range (Codex PR-2 MINOR #1).
   973	_TIMELINE_MAX_TICKS = 20_000
   974	_TIMELINE_MAX_EVENTS = 500
   975	
   976	
   977	def _handle_fantui_tick(request_payload: dict) -> tuple[int, dict]:
   978	    """Advance the FANTUI stateful tick system one step and return a snapshot.
   979	
   980	    Paired with ``/api/fantui/reset`` and ``/api/fantui/log``. The response
   981	    mirrors what /api/log emits so the same ``timeseries_chart.js`` module can
   982	    render either panel's buffer.
   983	    """
   984	    try:
   985	        pilot = parse_pilot_inputs(request_payload)
   986	    except ValueError as exc:
   987	        return 400, {"error": "invalid_input", "message": str(exc)}
   988	    try:
   989	        dt_s = float(request_payload.get("dt_s", 0.1))
   990	    except (TypeError, ValueError):
   991	        return 400, {"error": "invalid_dt_s"}
   992	    # Guard: tick step must be positive, finite, and small enough to avoid
   993	    # jumping over switch windows. 1.0s is a conservative ceiling.
   994	    # ``math.isfinite`` rejects NaN / ±Inf before they can poison ``_t_s``
   995	    # (Codex review, 2026-04-24, CRITICAL).
   996	    if not math.isfinite(dt_s) or dt_s <= 0 or dt_s > 1.0:
   997	        return 400, {"error": "dt_s_out_of_range", "message": "0 < dt_s <= 1.0"}
   998	
   999	    rec, count = _FANTUI_SYSTEM.tick_with_count(pilot, dt_s)
  1000	    snapshot = rec.as_dict()
  1001	    snapshot["sample_count"] = count
  1002	    return 200, snapshot
  1003	
  1004	
  1005	def _handle_timeline_simulate(request_payload: dict) -> dict:
  1006	    """Run a Timeline against the FANTUI executor and return the trace as JSON.
  1007	
  1008	    Returns `_status` key for the HTTP code to use (200 / 400).
  1009	    """
  1010	    try:
  1011	        timeline = parse_timeline(request_payload)
  1012	    except TimelineValidationError as exc:
  1013	        return {"_status": 400, "error": "invalid_timeline", "field": exc.field, "message": exc.message}
  1014	
  1015	    if timeline.system != "fantui":
  1016	        return {
  1017	            "_status": 400,
  1018	            "error": "unsupported_system",
  1019	            "message": f"this endpoint only runs FANTUI timelines; got system={timeline.system!r}",
  1020	        }
  1021	    if timeline.duration_s > _TIMELINE_MAX_DURATION_S:
  1022	        return {
  1023	            "_status": 400,
  1024	            "error": "timeline_too_long",
  1025	            "message": f"duration_s must be <= {_TIMELINE_MAX_DURATION_S}s",
  1026	        }
  1027	    if timeline.step_s < _TIMELINE_MIN_STEP_S:
  1028	        return {
  1029	            "_status": 400,
  1030	            "error": "timeline_step_too_small",
  1031	            "message": f"step_s must be >= {_TIMELINE_MIN_STEP_S}s",
  1032	        }
  1033	    tick_count = int(timeline.duration_s / timeline.step_s) + 1
  1034	    if tick_count > _TIMELINE_MAX_TICKS:
  1035	        return {
  1036	            "_status": 400,
  1037	            "error": "timeline_too_many_ticks",
  1038	            "message": f"duration_s/step_s would produce {tick_count} ticks; max {_TIMELINE_MAX_TICKS}",
  1039	        }
  1040	    if len(timeline.events) > _TIMELINE_MAX_EVENTS:
  1041	        return {
  1042	            "_status": 400,
  1043	            "error": "timeline_too_many_events",
  1044	            "message": f"events list has {len(timeline.events)} entries; max {_TIMELINE_MAX_EVENTS}",
  1045	        }
  1046	
  1047	    try:
  1048	        executor = FantuiExecutor()
  1049	        trace = TimelinePlayer(timeline, executor).run()
  1050	    except (ValueError, TypeError) as exc:

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1401,1750p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1401	    matrix_counts: dict[str, dict[str, int]] = {}
  1402	    grid: dict[str, dict[str, dict[str, bool]]] = {}
  1403	    outcome_totals = {outcome: 0 for outcome in requested_outcomes}
  1404	
  1405	    for radio_altitude_ft in radio_altitude_ft_values:
  1406	        ra_key = _stable_numeric_key(radio_altitude_ft)
  1407	        matrix_counts[ra_key] = {}
  1408	        grid[ra_key] = {}
  1409	        for tra_deg in tra_deg_values:
  1410	            tra_key = _stable_numeric_key(tra_deg)
  1411	            snapshot = lever_snapshot_payload(
  1412	                tra_deg=tra_deg,
  1413	                radio_altitude_ft=radio_altitude_ft,
  1414	                feedback_mode="manual_feedback_override",
  1415	                deploy_position_percent=100.0,
  1416	            )
  1417	            matched_outcomes = {
  1418	                outcome: _sensitivity_outcome_matches(snapshot, outcome)
  1419	                for outcome in requested_outcomes
  1420	            }
  1421	            matrix_counts[ra_key][tra_key] = sum(
  1422	                1 for is_matched in matched_outcomes.values() if is_matched
  1423	            )
  1424	            grid[ra_key][tra_key] = matched_outcomes
  1425	            for outcome, is_matched in matched_outcomes.items():
  1426	                if is_matched:
  1427	                    outcome_totals[outcome] += 1
  1428	
  1429	    return {
  1430	        "system_id": system_id,
  1431	        "radio_altitude_ft_values": list(radio_altitude_ft_values),
  1432	        "tra_deg_values": list(tra_deg_values),
  1433	        "outcomes": list(requested_outcomes),
  1434	        "matrix_counts": matrix_counts,
  1435	        "outcome_totals": outcome_totals,
  1436	        "grid": grid,
  1437	        "scan_count": len(radio_altitude_ft_values) * len(tra_deg_values),
  1438	        "fixed_inputs": {
  1439	            "engine_running": True,
  1440	            "aircraft_on_ground": True,
  1441	            "reverser_inhibited": False,
  1442	            "eec_enable": True,
  1443	            "n1k": MONITOR_N1K,
  1444	            "max_n1k_deploy_limit": MONITOR_MAX_N1K_DEPLOY_LIMIT,
  1445	            "feedback_mode": "manual_feedback_override",
  1446	            "deploy_position_percent": 100.0,
  1447	        },
  1448	    }, None
  1449	
  1450	
  1451	def _optional_request_str(payload: dict, field_name: str) -> tuple[str | None, dict | None]:
  1452	    raw_value = payload.get(field_name)
  1453	    if raw_value is None:
  1454	        return None, None
  1455	    if not isinstance(raw_value, str):
  1456	        return None, {
  1457	            "error": "invalid_workbench_request",
  1458	            "field": field_name,
  1459	            "message": f"{field_name} must be a string when provided.",
  1460	        }
  1461	    normalized = raw_value.strip()
  1462	    return (normalized or None), None
  1463	
  1464	
  1465	def _optional_request_string_list(payload: dict, field_name: str) -> tuple[tuple[str, ...] | None, dict | None]:
  1466	    raw_value = payload.get(field_name)
  1467	    if raw_value is None:
  1468	        return None, None
  1469	    if not isinstance(raw_value, list) or any(not isinstance(item, str) for item in raw_value):
  1470	        return None, {
  1471	            "error": "invalid_workbench_request",
  1472	            "field": field_name,
  1473	            "message": f"{field_name} must be a list of strings when provided.",
  1474	        }
  1475	    return tuple(item.strip() for item in raw_value if item.strip()), None
  1476	
  1477	
  1478	def _optional_request_float(payload: dict, field_name: str, *, default: float) -> tuple[float, dict | None]:
  1479	    raw_value = payload.get(field_name, default)
  1480	    if isinstance(raw_value, bool):
  1481	        return default, {
  1482	            "error": "invalid_workbench_request",
  1483	            "field": field_name,
  1484	            "message": f"{field_name} must be numeric.",
  1485	        }
  1486	    try:
  1487	        value = float(raw_value)
  1488	    except (TypeError, ValueError):
  1489	        return default, {
  1490	            "error": "invalid_workbench_request",
  1491	            "field": field_name,
  1492	            "message": f"{field_name} must be numeric.",
  1493	        }
  1494	    if not math.isfinite(value):
  1495	        return default, {
  1496	            "error": "invalid_numeric_value",
  1497	            "field": field_name,
  1498	            "message": f"{field_name} must be a finite number.",
  1499	        }
  1500	    if value <= 0:
  1501	        return default, {
  1502	            "error": "invalid_workbench_request",
  1503	            "field": field_name,
  1504	            "message": f"{field_name} must be greater than zero.",
  1505	        }
  1506	    return value, None
  1507	
  1508	
  1509	def _optional_request_object(payload: dict, field_name: str) -> tuple[dict | None, dict | None]:
  1510	    raw_value = payload.get(field_name)
  1511	    if raw_value is None:
  1512	        return None, None
  1513	    if not isinstance(raw_value, dict):
  1514	        return None, {
  1515	            "error": "invalid_workbench_request",
  1516	            "field": field_name,
  1517	            "message": f"{field_name} must be a JSON object when provided.",
  1518	        }
  1519	    return raw_value, None
  1520	
  1521	
  1522	def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
  1523	    packet_payload = request_payload.get("packet_payload")
  1524	    if not isinstance(packet_payload, dict):
  1525	        return None, {
  1526	            "error": "invalid_workbench_request",
  1527	            "field": "packet_payload",
  1528	            "message": "packet_payload must be a JSON object.",
  1529	        }
  1530	    try:
  1531	        packet = intake_packet_from_dict(packet_payload)
  1532	    except ValueError as exc:
  1533	        return None, {
  1534	            "error": "invalid_workbench_packet",
  1535	            "field": "packet_payload",
  1536	            "message": str(exc),
  1537	        }
  1538	
  1539	    scenario_id, error_payload = _optional_request_str(request_payload, "scenario_id")
  1540	    if error_payload is not None:
  1541	        return None, error_payload
  1542	    fault_mode_id, error_payload = _optional_request_str(request_payload, "fault_mode_id")
  1543	    if error_payload is not None:
  1544	        return None, error_payload
  1545	    observed_symptoms, error_payload = _optional_request_str(request_payload, "observed_symptoms")
  1546	    if error_payload is not None:
  1547	        return None, error_payload
  1548	    evidence_links, error_payload = _optional_request_string_list(request_payload, "evidence_links")
  1549	    if error_payload is not None:
  1550	        return None, error_payload
  1551	    confirmed_root_cause, error_payload = _optional_request_str(request_payload, "confirmed_root_cause")
  1552	    if error_payload is not None:
  1553	        return None, error_payload
  1554	    repair_action, error_payload = _optional_request_str(request_payload, "repair_action")
  1555	    if error_payload is not None:
  1556	        return None, error_payload
  1557	    validation_after_fix, error_payload = _optional_request_str(request_payload, "validation_after_fix")
  1558	    if error_payload is not None:
  1559	        return None, error_payload
  1560	    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
  1561	    if error_payload is not None:
  1562	        return None, error_payload
  1563	    suggested_logic_change, error_payload = _optional_request_str(request_payload, "suggested_logic_change")
  1564	    if error_payload is not None:
  1565	        return None, error_payload
  1566	    reliability_gain_hypothesis, error_payload = _optional_request_str(
  1567	        request_payload,
  1568	        "reliability_gain_hypothesis",
  1569	    )
  1570	    if error_payload is not None:
  1571	        return None, error_payload
  1572	    guardrail_note, error_payload = _optional_request_str(request_payload, "guardrail_note")
  1573	    if error_payload is not None:
  1574	        return None, error_payload
  1575	    sample_period_s, error_payload = _optional_request_float(
  1576	        request_payload,
  1577	        "sample_period_s",
  1578	        default=0.5,
  1579	    )
  1580	    if error_payload is not None:
  1581	        return None, error_payload
  1582	    workspace_handoff, error_payload = _optional_request_object(request_payload, "workspace_handoff")
  1583	    if error_payload is not None:
  1584	        return None, error_payload
  1585	    workspace_snapshot, error_payload = _optional_request_object(request_payload, "workspace_snapshot")
  1586	    if error_payload is not None:
  1587	        return None, error_payload
  1588	    if workspace_handoff is None and workspace_snapshot is not None:
  1589	        derived_handoff = workspace_snapshot.get("handoff")
  1590	        if isinstance(derived_handoff, dict):
  1591	            workspace_handoff = derived_handoff
  1592	
  1593	    archive_bundle_raw = request_payload.get("archive_bundle", False)
  1594	    archive_bundle = isinstance(archive_bundle_raw, bool) and archive_bundle_raw is True
  1595	    try:
  1596	        bundle = build_workbench_bundle(
  1597	            packet,
  1598	            scenario_id=scenario_id,
  1599	            fault_mode_id=fault_mode_id,
  1600	            observed_symptoms=observed_symptoms,
  1601	            evidence_links=evidence_links or (),
  1602	            confirmed_root_cause=confirmed_root_cause,
  1603	            repair_action=repair_action,
  1604	            validation_after_fix=validation_after_fix,
  1605	            residual_risk=residual_risk,
  1606	            suggested_logic_change=suggested_logic_change,
  1607	            reliability_gain_hypothesis=reliability_gain_hypothesis,
  1608	            redundancy_reduction_or_guardrail_note=guardrail_note,
  1609	            sample_period_s=sample_period_s,
  1610	        )
  1611	    except ValueError as exc:
  1612	        return None, {
  1613	            "error": "invalid_workbench_selection",
  1614	            "message": str(exc),
  1615	        }
  1616	
  1617	    archive = None
  1618	    if archive_bundle:
  1619	        archive = archive_workbench_bundle(
  1620	            bundle,
  1621	            default_workbench_archive_root(),
  1622	            workspace_handoff=workspace_handoff,
  1623	            workspace_snapshot=workspace_snapshot,
  1624	        )
  1625	    return {
  1626	        "bundle": bundle.to_dict(),
  1627	        "archive": archive.to_dict() if archive is not None else None,
  1628	        "archive_bundle": archive_bundle,
  1629	        "default_archive_root": str(default_workbench_archive_root()),
  1630	        "explain_runtime": build_explain_runtime_payload(),
  1631	    }, None
  1632	
  1633	
  1634	def build_workbench_safe_repair_response(request_payload: dict) -> tuple[dict | None, dict | None]:
  1635	    packet_payload = request_payload.get("packet_payload")
  1636	    if not isinstance(packet_payload, dict):
  1637	        return None, {
  1638	            "error": "invalid_workbench_request",
  1639	            "field": "packet_payload",
  1640	            "message": "packet_payload must be a JSON object.",
  1641	        }
  1642	    if not request_payload.get("apply_all_safe", False):
  1643	        return None, {
  1644	            "error": "invalid_workbench_request",
  1645	            "field": "apply_all_safe",
  1646	            "message": "apply_all_safe must be true for safe schema repair requests.",
  1647	        }
  1648	    try:
  1649	        packet = intake_packet_from_dict(packet_payload)
  1650	    except ValueError as exc:
  1651	        return None, {
  1652	            "error": "invalid_workbench_packet",
  1653	            "field": "packet_payload",
  1654	            "message": str(exc),
  1655	        }
  1656	
  1657	    repaired_packet, applied_suggestion_ids = apply_safe_schema_repairs(packet)
  1658	    if not applied_suggestion_ids:
  1659	        return None, {
  1660	            "error": "no_safe_schema_repairs",
  1661	            "message": "No safe schema repair suggestions are currently available for this packet.",
  1662	        }
  1663	
  1664	    return {
  1665	        "packet_payload": intake_packet_to_dict(repaired_packet),
  1666	        "applied_suggestion_ids": list(applied_suggestion_ids),
  1667	        "intake_assessment": assess_intake_packet(repaired_packet),
  1668	        "clarification_brief": build_clarification_brief(repaired_packet),
  1669	    }, None
  1670	
  1671	
  1672	def build_workbench_archive_restore_response(request_payload: dict) -> tuple[dict | None, dict | None]:
  1673	    manifest_path, error_payload = _optional_request_str(request_payload, "manifest_path")
  1674	    if error_payload is not None:
  1675	        return None, error_payload
  1676	    if manifest_path is None:
  1677	        return None, {
  1678	            "error": "invalid_workbench_request",
  1679	            "field": "manifest_path",
  1680	            "message": "manifest_path must be a non-empty string.",
  1681	        }
  1682	
  1683	    # SECURITY: reject path traversal attempts in relative paths
  1684	    if not Path(manifest_path).is_absolute():
  1685	        if ".." in str(manifest_path):
  1686	            return None, {"error": "invalid_manifest_path", "message": "Relative manifest_path with traversal is not allowed."}
  1687	
  1688	    try:
  1689	        restore_payload = load_workbench_archive_restore_payload(manifest_path)
  1690	    except FileNotFoundError as exc:
  1691	        return None, {
  1692	            "error": "workbench_archive_not_found",
  1693	            "field": "manifest_path",
  1694	            "message": str(exc),
  1695	        }
  1696	    except SandboxEscapeError as exc:
  1697	        return None, {"error": "sandbox_violation", "message": str(exc)}
  1698	    except (OSError, json.JSONDecodeError, ValueError) as exc:
  1699	        return None, {
  1700	            "error": "invalid_workbench_archive",
  1701	            "field": "manifest_path",
  1702	            "message": str(exc),
  1703	        }
  1704	
  1705	    restore_payload["default_archive_root"] = str(default_workbench_archive_root())
  1706	    return restore_payload, None
  1707	
  1708	
  1709	def _canonical_pullback_sequence(tra_deg: float, config: HarnessConfig) -> list[float]:
  1710	    """Return a tiny canonical pullback path for the interactive UI scrubber.
  1711	
  1712	    When the pilot holds TRA in the deploy-cmd range (≤ logic3_tra_deg_threshold),
  1713	    hold the lever long enough for plant VDT to reach 90% under the default
  1714	    deploy rate. Without this, auto_scrubber shows L4 permanently blocked on
  1715	    `deploy_90_percent_vdt` because the scrubber window is too short for the
  1716	    plant to complete the deployment cycle.
  1717	    """
  1718	    target = _clamp_tra(tra_deg, config)
  1719	    if target >= 0.0:
  1720	        return [0.0]
  1721	
  1722	    sequence: list[float] = []
  1723	    if target <= config.sw1_window.near_zero_deg:
  1724	        sequence.extend([-2.0] * 4)
  1725	    if target <= config.sw2_window.near_zero_deg:
  1726	        sequence.extend([-7.0] * 4)
  1727	
  1728	    if target <= config.logic3_tra_deg_threshold:
  1729	        # Budget enough ticks for plant VDT to reach 90% (and a small margin
  1730	        # so L4 latches cleanly). deploy_rate_percent_per_s × step_s × N ≥ 100
  1731	        # → N ≥ 100 / (rate × step_s). +4 cushion covers L3-activation lag.
  1732	        deploy_ticks_needed = int(100.0 / max(1e-6, config.deploy_rate_percent_per_s * config.step_s)) + 4
  1733	        final_repeats = max(4, deploy_ticks_needed)
  1734	    else:
  1735	        final_repeats = 2
  1736	    sequence.extend([target] * final_repeats)
  1737	    return sequence
  1738	
  1739	
  1740	def _condition_payload(condition) -> dict:
  1741	    return {
  1742	        "name": condition.name,
  1743	        "current_value": condition.current_value,
  1744	        "comparison": condition.comparison,
  1745	        "threshold_value": condition.threshold_value,
  1746	        "passed": condition.passed,
  1747	    }
  1748	
  1749	
  1750	def _logic_payload(logic) -> dict:

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2101,2450p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '1751,2100p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2101	            n1k=MONITOR_N1K,
  2102	            max_n1k_deploy_limit=MONITOR_MAX_N1K_DEPLOY_LIMIT,
  2103	            tls_unlocked_ls=tls_unlocked_ls,
  2104	            all_pls_unlocked_ls=all_pls_unlocked_ls,
  2105	            reverser_not_deployed_eec=vdt_percent <= 0.0,
  2106	            reverser_fully_deployed_eec=vdt_percent >= 100.0,
  2107	            deploy_90_percent_vdt=vdt_percent >= config.deploy_90_threshold_percent,
  2108	        )
  2109	        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
  2110	
  2111	        rows.append(
  2112	            {
  2113	                "time_s": time_s,
  2114	                "ra": round(radio_altitude_ft, 3),
  2115	                "tra": round(tra_deg, 3),
  2116	                "sw1": 1.0 if inputs.sw1 else 0.0,
  2117	                "logic1": 1.0 if outputs.logic1_active else 0.0,
  2118	                "tls": 115.0 if outputs.tls_115vac_cmd else 0.0,
  2119	                "sw2": 1.0 if inputs.sw2 else 0.0,
  2120	                "logic2": 1.0 if outputs.logic2_active else 0.0,
  2121	                "etrac": 540.0 if outputs.etrac_540vdc_cmd else 0.0,
  2122	                "logic3": 1.0 if outputs.logic3_active else 0.0,
  2123	                "eec": 1.0 if outputs.eec_deploy_cmd else 0.0,
  2124	                "pls": 1.0 if outputs.pls_power_cmd else 0.0,
  2125	                "pdu": 1.0 if outputs.pdu_motor_cmd else 0.0,
  2126	                "vdt": round(vdt_percent, 3),
  2127	                "logic4": 1.0 if outputs.logic4_active else 0.0,
  2128	                "thr_lock": 1.0 if outputs.throttle_electronic_lock_release_cmd else 0.0,
  2129	                "logic4_failed_conditions": [condition.name for condition in explain.logic4.failed_conditions],
  2130	            }
  2131	        )
  2132	
  2133	        tls_powered_s = tls_powered_s + config.step_s if outputs.tls_115vac_cmd else 0.0
  2134	        tls_unlocked_ls = tls_unlocked_ls or (
  2135	            outputs.tls_115vac_cmd and tls_powered_s >= config.tls_unlock_delay_s
  2136	        )
  2137	
  2138	        pls_powered_s = pls_powered_s + config.step_s if outputs.pls_power_cmd else 0.0
  2139	        pls_ready = outputs.pls_power_cmd and pls_powered_s >= config.pls_unlock_delay_s
  2140	        all_pls_unlocked_ls = all_pls_unlocked_ls or pls_ready
  2141	
  2142	        if not (
  2143	            outputs.tls_115vac_cmd
  2144	            or outputs.etrac_540vdc_cmd
  2145	            or outputs.pls_power_cmd
  2146	            or outputs.pdu_motor_cmd
  2147	        ):
  2148	            tls_unlocked_ls = False
  2149	            all_pls_unlocked_ls = False
  2150	
  2151	    return rows
  2152	
  2153	
  2154	def monitor_timeline_payload() -> dict:
  2155	    config = HarnessConfig()
  2156	    rows = _monitor_rows(config)
  2157	    series = []
  2158	    for definition in _monitor_series_definition():
  2159	        samples = [[row["time_s"], row[definition["id"]]] for row in rows]
  2160	        series.append({**definition, "samples": samples})
  2161	
  2162	    l4_ready_time = _monitor_transition_time(rows, "logic4", 1.0)
  2163	    events = [
  2164	        {
  2165	            "time_s": 0.0,
  2166	            "label": "流程开始",
  2167	            "detail": "RA 从 7.0 ft 起步；TRA=0°；VDT=0%。",
  2168	        },
  2169	        {
  2170	            "time_s": 1.0,
  2171	            "label": "RA=6.0 ft",
  2172	            "detail": "TRA 从 0° 开始以 10°/s 推向 -14°。",
  2173	        },
  2174	        {
  2175	            "time_s": 2.4,
  2176	            "label": "TRA=-14°",
  2177	            "detail": "碰到 L4 条件限位；VDT 开始以 50%/s 从 0% 变化。",
  2178	        },
  2179	        {
  2180	            "time_s": 4.2,
  2181	            "label": "VDT90",
  2182	            "detail": "VDT 达到 90%，L4 / THR_LOCK 首次满足。",
  2183	        },
  2184	        {
  2185	            "time_s": MONITOR_ACTIVE_END_S,
  2186	            "label": "监测结束",
  2187	            "detail": "VDT=100%，主动监测流程完成。",
  2188	        },
  2189	        {
  2190	            "time_s": MONITOR_TIMELINE_END_S,
  2191	            "label": "RA=0 ft",
  2192	            "detail": "展示保持段：RA 继续匀速降到 0 ft 后保持。",
  2193	        },
  2194	    ]
  2195	
  2196	    return {
  2197	        "mode": "timeline_monitor",
  2198	        "title": "受控状态监控时间线",
  2199	        "time_start_s": 0.0,
  2200	        "time_end_s": MONITOR_TIMELINE_END_S,
  2201	        "active_end_s": MONITOR_ACTIVE_END_S,
  2202	        "compression_ratio": MONITOR_TIMELINE_COMPRESSION_RATIO,
  2203	        "step_s": config.step_s,
  2204	        "model_note": (
  2205	            "这条监控图按用户定义的 RA -> TRA -> VDT 受控时间线生成；"
  2206	            "整段时间已压缩为原来的 1/10；VDT 按现有 demo 反馈语义绘制为 0%-100% 监测量，"
  2207	            "控制逻辑仍由 DeployController 评估。"
  2208	        ),
  2209	        "timeline_summary": {
  2210	            "ra_start_ft": MONITOR_RA_START_FT,
  2211	            "ra_hits_six_ft_at_s": 1.0,
  2212	            "tra_lock_deg": MONITOR_TRA_LOCK_DEG,
  2213	            "tra_reaches_lock_at_s": 2.4,
  2214	            "vdt_reaches_90_percent_at_s": 4.2,
  2215	            "vdt_reaches_100_percent_at_s": MONITOR_ACTIVE_END_S,
  2216	            "ra_reaches_zero_ft_at_s": MONITOR_TIMELINE_END_S,
  2217	            "l4_ready_at_s": l4_ready_time,
  2218	        },
  2219	        "events": events,
  2220	        "series": series,
  2221	}
  2222	
  2223	
  2224	# ---------------------------------------------------------------------------
  2225	# Multi-system snapshot support (P13)
  2226	# ---------------------------------------------------------------------------
  2227	SYSTEM_REGISTRY = {
  2228	    "thrust-reverser": build_reference_controller_adapter,
  2229	    "landing-gear": build_landing_gear_controller_adapter,
  2230	    "bleed-air": build_bleed_air_controller_adapter,
  2231	    "efds": build_efds_controller_adapter,
  2232	    # P43-02.5 (2026-04-21): C919 E-TRAS · certified · P34+P38 真实 PDF 接入 ·
  2233	    # reference panel target for P43-05 AI panel generator validation
  2234	    "c919-etras": build_c919_etras_controller_adapter,
  2235	}
  2236	
  2237	# Cache built (stateless) adapters — avoid per-request instantiation overhead.
  2238	# P43-02.5: bumped maxsize 4→5 to accommodate c919-etras without evicting others.
  2239	@lru_cache(maxsize=5)
  2240	def _cached_adapter(system_id: str) -> Any:
  2241	    builder = SYSTEM_REGISTRY.get(system_id)
  2242	    if builder is None:
  2243	        return None
  2244	    return builder()
  2245	
  2246	SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
  2247	
  2248	
  2249	def _default_snapshot_for_system(system_id: str) -> dict:
  2250	    """Return a minimal/default snapshot for each registered system."""
  2251	    if system_id == "thrust-reverser":
  2252	        return {
  2253	            "radio_altitude_ft": 5.0,
  2254	            "tra_deg": 0.0,
  2255	            "sw1": False,
  2256	            "sw2": False,
  2257	            "engine_running": True,
  2258	            "aircraft_on_ground": True,
  2259	            "reverser_inhibited": False,
  2260	            "eec_enable": True,
  2261	            "n1k": 35.0,
  2262	            "max_n1k_deploy_limit": 60.0,
  2263	            "tls_unlocked_ls": False,
  2264	            "all_pls_unlocked_ls": False,
  2265	            "reverser_not_deployed_eec": True,
  2266	            "reverser_fully_deployed_eec": False,
  2267	            "deploy_90_percent_vdt": False,
  2268	        }
  2269	    elif system_id == "landing-gear":
  2270	        return {
  2271	            "gear_handle_position": "UP",
  2272	            "hydraulic_pressure_psi": 0.0,
  2273	            "uplock_released": False,
  2274	            "gear_position_percent": 0.0,
  2275	            "downlock_engaged": False,
  2276	        }
  2277	    elif system_id == "bleed-air":
  2278	        return {
  2279	            "valve_position": "CLOSED",
  2280	            "inlet_pressure": 0.0,
  2281	            "outlet_pressure": 0.0,
  2282	            "control_unit_ready": True,
  2283	        }
  2284	    elif system_id == "efds":
  2285	        return {
  2286	            "sensor.alt.radar": 5000.0,
  2287	            "sensor.alt.baro": 5200.0,
  2288	            "sensor.temp.external": 15.0,
  2289	            "sensor.threat.mls": "IDLE",
  2290	            "sensor.g.load": 1.0,
  2291	            "logic.armed_relay": "OPEN",
  2292	            "logic.firing_channel": "READY",
  2293	            "logic.crosslink_validator": "FALSE",
  2294	            "pilot.arm_switch": "SAFE",
  2295	            "pilot.manual_dispense": "RELEASED",
  2296	            "pilot.altitude_override": "AUTO",
  2297	            "actuator.flare_array": 24.0,
  2298	            "actuator.limiter_valve": "REGULATED",
  2299	        }
  2300	    elif system_id == "c919-etras":
  2301	        # P43-02.5 (2026-04-21): C919 E-TRAS default snapshot · nominal pre-deploy
  2302	        # state (aircraft on ground · engines at idle · TR fully stowed · no faults).
  2303	        # 34 fields aligned with c919_etras_adapter.py _snapshot_* helper calls.
  2304	        # PDF §1.1.x traceability preserved via hardware YAML (SHA256-locked).
  2305	        return {
  2306	            # --- A/C inputs ---
  2307	            "tra_deg": 0.0,                         # PDF §Step1 · throttle at forward idle
  2308	            "n1k_percent": 35.0,                    # Engine N1K at idle (adapter MONITOR_N1K)
  2309	            "engine_running": True,
  2310	            "tr_inhibited": False,                  # A/C bus · not inhibited
  2311	            # --- LGCU 双余度 MLG_WOW input (PDF 表2) ---
  2312	            "lgcu1_mlg_wow_value": True,            # LGCU1 reports on-ground
  2313	            "lgcu1_mlg_wow_valid": True,
  2314	            "lgcu2_mlg_wow_value": True,            # LGCU2 reports on-ground
  2315	            "lgcu2_mlg_wow_valid": True,
  2316	            # --- Selected TR_WOW (adapter _select_mlg_wow output · pre-computed for default) ---
  2317	            "tr_wow": True,
  2318	            # --- TLS (Translating Lock Sleeve · 双余度) · stowed=locked → unlocked=False ---
  2319	            "tls_ls_a_valid": True,
  2320	            "tls_ls_a_unlocked": False,
  2321	            "tls_ls_b_valid": True,
  2322	            "tls_ls_b_unlocked": False,
  2323	            # --- PLS (Primary Lock Sleeve · 双余度) · stowed=locked=True ---
  2324	            "pls_ls_a_locked": True,
  2325	            "pls_ls_b_locked": True,
  2326	            # --- Pylon locks (left+right · each 双余度) · stowed=locked → unlocked=False ---
  2327	            "left_pylon_ls_a_valid": True,
  2328	            "left_pylon_ls_a_unlocked": False,
  2329	            "left_pylon_ls_b_valid": True,
  2330	            "left_pylon_ls_b_unlocked": False,
  2331	            "right_pylon_ls_a_valid": True,
  2332	            "right_pylon_ls_a_unlocked": False,
  2333	            "right_pylon_ls_b_valid": True,
  2334	            "right_pylon_ls_b_unlocked": False,
  2335	            # --- Actuator/state inputs (nominal no-action) ---
  2336	            "apwtla": False,                        # All-pylons-wow-to-long-aggregate
  2337	            "atltla": False,                        # All-tls-long-to-long-aggregate
  2338	            # --- Sensors ---
  2339	            "vdt_sensor_valid": True,
  2340	            "e_tras_over_temp_fault": False,
  2341	            "trcu_power_on": True,
  2342	            # --- TR position (fully stowed at rest) ---
  2343	            "tr_position_percent": 0.0,
  2344	            # --- Command history (no prior EICU_CMD3 firing) ---
  2345	            "prev_eicu_cmd3": False,
  2346	            # --- Timing confirmation counters (accumulated dwell at nominal state) ---
  2347	            "comm2_timer_s": 0.0,
  2348	            "lock_unlock_confirm_s": 0.0,
  2349	            "tr_position_deployed_confirm_s": 0.0,
  2350	            "tr_stowed_locked_confirm_s": 2.0,      # ≥ 1.0s (TR_STOWED_LOCKED_CONFIRM_S) · nominal
  2351	        }
  2352	    return {}
  2353	
  2354	
  2355	def _spec_to_nodes(spec: dict, truth_evaluation: Any = None) -> list[dict]:
  2356	    """Build a nodes array from spec.components + spec.logic_nodes.
  2357	
  2358	    Nodes are ordered to reflect the control flow: input conditions first,
  2359	    then parallel logic gates, then merge gates, then final outputs.
  2360	    This ordering is derived from the spec's logic_node downstream relationships.
  2361	    """
  2362	    active_ids: set[str] = set()
  2363	    if truth_evaluation is not None:
  2364	        active_ids = set(truth_evaluation.active_logic_node_ids)
  2365	
  2366	    # Separate components into inputs vs intermediate/output components
  2367	    components = spec.get("components", [])
  2368	    logic_nodes = spec.get("logic_nodes", [])
  2369	
  2370	    # Identify which components are upstream inputs (no logic_node depends on them as downstream)
  2371	    downstream_ids: set[str] = set()
  2372	    for ln in logic_nodes:
  2373	        for cid in ln.get("downstream_component_ids", []):
  2374	            downstream_ids.add(cid)
  2375	
  2376	    # Components that appear as downstream of logic nodes → intermediate/output nodes
  2377	    # Components that don't → upstream input nodes
  2378	    upstream_input_ids: set[str] = set()
  2379	    intermediate_output_ids: set[str] = set()
  2380	    for comp in components:
  2381	        cid = comp["id"]
  2382	        if cid in downstream_ids:
  2383	            intermediate_output_ids.add(cid)
  2384	        else:
  2385	            upstream_input_ids.add(cid)
  2386	
  2387	    # Build ordered node list:
  2388	    # 1. Upstream input components (sensors/pilot inputs)
  2389	    # 2. Logic nodes in dependency order
  2390	    # 3. Intermediate/output components (commands/power)
  2391	    nodes: list[dict] = []
  2392	
  2393	    # Sort logic nodes by dependency: nodes whose downstream_component_ids feed into other logic nodes come first
  2394	    # For thrust-reverser: L1 and L2 are parallel (no cross-dependency), L3 depends on both, L4 depends on L3
  2395	    # Build a dependency graph to determine order
  2396	    node_ids = {ln["id"] for ln in logic_nodes}
  2397	    resolved: list[dict] = []
  2398	    remaining = list(logic_nodes)
  2399	    while remaining:
  2400	        made_progress = False
  2401	        for i, ln in enumerate(remaining):
  2402	            deps_met = True
  2403	            for cid in ln.get("downstream_component_ids", []):
  2404	                # Check if this component feeds into any remaining logic node
  2405	                for remaining_ln in remaining[i + 1:]:
  2406	                    if cid in remaining_ln.get("downstream_component_ids", []):
  2407	                        deps_met = False
  2408	                        break
  2409	                if not deps_met:
  2410	                    break
  2411	            if deps_met:
  2412	                resolved.append(remaining.pop(i))
  2413	                made_progress = True
  2414	                break
  2415	        if not made_progress:
  2416	            # Fallback: append remaining in order
  2417	            resolved.extend(remaining)
  2418	            break
  2419	
  2420	    # Layer 1: upstream input components
  2421	    for comp in components:
  2422	        if comp["id"] in upstream_input_ids:
  2423	            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))
  2424	
  2425	    # Layer 2: logic nodes in dependency order
  2426	    for ln in resolved:
  2427	        state = "active" if ln["id"] in active_ids else "inactive"
  2428	        nodes.append(_node(ln["id"], ln["label"], state, "spec.logic_nodes"))
  2429	
  2430	    # Layer 3: intermediate/output components (commands/power)
  2431	    for comp in components:
  2432	        if comp["id"] in intermediate_output_ids:
  2433	            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))
  2434	
  2435	    return nodes
  2436	
  2437	
  2438	def system_snapshot_payload(system_id: str) -> dict:
  2439	    """Build the payload for GET /api/system-snapshot."""
  2440	    adapter = _cached_adapter(system_id)
  2441	    if adapter is None:
  2442	        return {"error": "unknown_system", "system_id": system_id}
  2443	    spec = adapter.load_spec()
  2444	    default_snapshot = _default_snapshot_for_system(system_id)
  2445	    truth_eval = adapter.evaluate_snapshot(default_snapshot)
  2446	    nodes = _spec_to_nodes(spec, truth_eval)
  2447	    return {
  2448	        "system_id": system_id,
  2449	        "title": spec.get("title", system_id),
  2450	        "spec": spec,

 succeeded in 0ms:
  1751	    return {
  1752	        "logic_name": logic.logic_name,
  1753	        "active": logic.active,
  1754	        "failed_conditions": [condition.name for condition in logic.failed_conditions],
  1755	        "conditions": [_condition_payload(condition) for condition in logic.conditions],
  1756	    }
  1757	
  1758	
  1759	def _node(node_id: str, label: str, state: str, source: str, blocked_by: list[str] | None = None) -> dict:
  1760	    return {
  1761	        "id": node_id,
  1762	        "label": label,
  1763	        "state": state,
  1764	        "source": source,
  1765	        "blocked_by": blocked_by or [],
  1766	    }
  1767	
  1768	
  1769	def _logic_node_state(active: bool, completed: bool = False) -> str:
  1770	    return "active" if active or completed else "blocked"
  1771	
  1772	
  1773	def _lever_summary(
  1774	    tra_deg: float,
  1775	    inputs: ResolvedInputs,
  1776	    sensors,
  1777	    outputs,
  1778	    explain,
  1779	    feedback_mode: str,
  1780	    tra_lock: dict | None = None,
  1781	) -> dict:
  1782	    summary = None
  1783	    if not inputs.sw1:
  1784	        summary = {
  1785	            "headline": f"TRA {tra_deg:.1f}°：拉杆还没进入 SW1 窗口，反推链路保持待命。",
  1786	            "blocker": "当前卡在 SW1：继续拉入 -1.4° 到 -6.2° 窗口会触发第一段链路。",
  1787	            "next_step": "下一步：把拉杆继续向反推方向拉到 SW1 window。",
  1788	        }
  1789	    elif not outputs.logic1_active and not sensors.tls_unlocked_ls:
  1790	        failed = ", ".join(condition.name for condition in explain.logic1.failed_conditions)
  1791	        summary = {
  1792	            "headline": f"TRA {tra_deg:.1f}°：SW1 已触发，但 L1 / TLS115 尚未放行。",
  1793	            "blocker": f"当前卡在 L1：{failed or 'logic1 条件未完全满足'}。",
  1794	            "next_step": "下一步：恢复 RA / inhibited / EEC feedback 等 L1 条件，或回到默认演示条件。",
  1795	        }
  1796	    elif not inputs.sw2:
  1797	        summary = {
  1798	            "headline": f"TRA {tra_deg:.1f}°：SW1 / L1 / TLS115 已点亮，正在建立 TLS 解锁反馈。",
  1799	            "blocker": "当前卡在 SW2：还没有进入 -5.0° 到 -9.8° 窗口。",
  1800	            "next_step": "下一步：继续拉到 SW2 window，点亮 L2 / 540V。",
  1801	        }
  1802	    elif not outputs.logic2_active:
  1803	        failed = ", ".join(condition.name for condition in explain.logic2.failed_conditions)
  1804	        blocker_text = f"当前卡在 L2：{failed or 'logic2 条件未完全满足'}。"
  1805	        l3_shared = {c.name for c in explain.logic2.failed_conditions} & {"engine_running", "aircraft_on_ground"}
  1806	        if l3_shared:
  1807	            blocker_text += "（L3 对这些信号独立检查，同步被阻塞。）"
  1808	        summary = {
  1809	            "headline": f"TRA {tra_deg:.1f}°：SW2 已触发，但 L2 / 540V 尚未放行。",
  1810	            "blocker": blocker_text,
  1811	            "next_step": "下一步：恢复 engine / ground / inhibited / EEC enable 等 L2 条件。",
  1812	        }
  1813	    elif not outputs.logic3_active:
  1814	        failed = ", ".join(condition.name for condition in explain.logic3.failed_conditions)
  1815	        summary = {
  1816	            "headline": f"TRA {tra_deg:.1f}°：SW1、SW2 与 L2/540V 已点亮，L3 尚未放行。",
  1817	            "blocker": f"当前卡在 L3：{failed or 'logic3 条件未完全满足'}。",
  1818	            "next_step": "下一步：继续拉到 TRA <= -11.74°，并保持 N1K / TLS 等条件满足。",
  1819	        }
  1820	    elif not outputs.logic4_active:
  1821	        failed = ", ".join(condition.name for condition in explain.logic4.failed_conditions)
  1822	        next_step = "下一步：在受控轨迹中继续保持反推，等 deploy_90_percent_vdt / VDT90 反馈出现。"
  1823	        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
  1824	            next_step = "下一步：把 deploy feedback override 推到 >= 90%，演示 VDT90 -> L4 -> THR_LOCK。"
  1825	        summary = {
  1826	            "headline": f"TRA {tra_deg:.1f}°：L3 已点亮，EEC / PLS / PDU 命令正在驱动受控演示轨迹。",
  1827	            "blocker": f"THR_LOCK 仍未释放：L4 还在等待 {failed or 'VDT90 / plant feedback'}。",
  1828	            "next_step": next_step,
  1829	        }
  1830	    elif feedback_mode == "manual_feedback_override":
  1831	        l1_post_deploy_note = (
  1832	            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落，L1 属于首次解锁门，已完成使命。）"
  1833	            if (not outputs.logic1_active
  1834	                and {c.name for c in explain.logic1.failed_conditions} <= {"reverser_not_deployed_eec"}
  1835	                and sensors.deploy_position_percent > 0)
  1836	            else ""
  1837	        )
  1838	        summary = {
  1839	            "headline": f"TRA {tra_deg:.1f}°：manual feedback override 已把 VDT90 推到触发态，L4 / THR_LOCK 已点亮。",
  1840	            "blocker": "当前无 L4 blocker；这是 simplified plant feedback override 的诊断演示结果。" + l1_post_deploy_note,
  1841	            "next_step": "下一步：切回 auto scrubber，或降低 deploy feedback 观察 VDT90 / THR_LOCK 退回 blocked。",
  1842	        }
  1843	    else:
  1844	        l1_post_deploy_note = (
  1845	            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落。）"
  1846	            if (not outputs.logic1_active
  1847	                and {c.name for c in explain.logic1.failed_conditions} <= {"reverser_not_deployed_eec"}
  1848	                and sensors.deploy_position_percent > 0)
  1849	            else ""
  1850	        )
  1851	        summary = {
  1852	            "headline": f"TRA {tra_deg:.1f}°：L4 已满足，THR_LOCK release command 已触发。",
  1853	            "blocker": "当前无 L4 blocker。" + l1_post_deploy_note,
  1854	            "next_step": "下一步：查看证据或返回问答抽屉做诊断解释。",
  1855	        }
  1856	
  1857	    if tra_lock and tra_lock["clamped"]:
  1858	        summary["blocker"] = (
  1859	            f"{summary['blocker']} TRA 深拉区仍未开放：请求 {tra_lock['requested_tra_deg']:.1f}° "
  1860	            f"已被限制在 {tra_lock['lock_deg']:.1f}°，当前只开放 {tra_lock['lock_deg']:.1f}° 到 0.0° 的自由拖动范围。"
  1861	        )
  1862	    return summary
  1863	
  1864	
  1865	def _simulate_lever_state(
  1866	    target_tra: float,
  1867	    *,
  1868	    config: HarnessConfig,
  1869	    radio_altitude_ft: float,
  1870	    engine_running: bool,
  1871	    aircraft_on_ground: bool,
  1872	    reverser_inhibited: bool,
  1873	    eec_enable: bool,
  1874	    n1k: float,
  1875	    max_n1k_deploy_limit: float,
  1876	    feedback_mode: str,
  1877	    deploy_position_percent: float,
  1878	    fault_injections: list[dict] | None = None,
  1879	) -> dict:
  1880	    controller_adapter = build_reference_controller_adapter(config)
  1881	    switches = LatchedThrottleSwitches(config)
  1882	    plant = SimplifiedDeployPlant(config)
  1883	    switch_state = SwitchState(previous_tra_deg=0.0)
  1884	    plant_state = PlantState()
  1885	    fault_map = _fault_injection_map(fault_injections)
  1886	
  1887	    snapshot = None
  1888	    for tick, current_tra in enumerate(_canonical_pullback_sequence(target_tra, config)):
  1889	        switch_state = switches.update(switch_state, current_tra)
  1890	        switch_state = _apply_switch_fault_injections(switch_state, fault_map)
  1891	        sensors = plant_state.sensors(config)
  1892	        sensors = _apply_sensor_fault_injections(sensors, fault_map)
  1893	        pilot_inputs = PilotInputs(
  1894	            radio_altitude_ft=(
  1895	                0.0
  1896	                if fault_map.get("radio_altitude_ft") == "sensor_zero"
  1897	                else radio_altitude_ft
  1898	            ),
  1899	            tra_deg=current_tra,
  1900	            engine_running=engine_running,
  1901	            aircraft_on_ground=aircraft_on_ground,
  1902	            reverser_inhibited=reverser_inhibited,
  1903	            eec_enable=eec_enable,
  1904	            n1k=0.0 if fault_map.get("n1k") == "sensor_zero" else n1k,
  1905	            max_n1k_deploy_limit=max_n1k_deploy_limit,
  1906	        )
  1907	        resolved_inputs = ResolvedInputs(
  1908	            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
  1909	            tra_deg=pilot_inputs.tra_deg,
  1910	            sw1=switch_state.sw1,
  1911	            sw2=switch_state.sw2,
  1912	            engine_running=pilot_inputs.engine_running,
  1913	            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
  1914	            reverser_inhibited=pilot_inputs.reverser_inhibited,
  1915	            eec_enable=pilot_inputs.eec_enable,
  1916	            n1k=pilot_inputs.n1k,
  1917	            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
  1918	            tls_unlocked_ls=sensors.tls_unlocked_ls,
  1919	            all_pls_unlocked_ls=sensors.all_pls_unlocked,
  1920	            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
  1921	            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
  1922	            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
  1923	        )
  1924	        outputs, explain = controller_adapter.evaluate_with_explain(resolved_inputs)
  1925	        outputs = _apply_output_fault_injections(outputs, fault_map)
  1926	        snapshot = {
  1927	            "time_s": round(tick * config.step_s, 3),
  1928	            "plant_state": plant_state,
  1929	            "sensors": sensors,
  1930	            "pilot_inputs": pilot_inputs,
  1931	            "inputs": resolved_inputs,
  1932	            "outputs": outputs,
  1933	            "explain": explain,
  1934	        }
  1935	        plant_state = plant.advance(plant_state, outputs, config.step_s)
  1936	
  1937	    assert snapshot is not None
  1938	
  1939	    if feedback_mode == "manual_feedback_override":
  1940	        # In manual override mode the user directly drives the physical lever position.
  1941	        # deploy_position_percent is the target position set by the user — no longer
  1942	        # gated by pdu_motor_cmd, allowing VDT to be forced independently.
  1943	        deploy_position = deploy_position_percent
  1944	        manual_plant_state = PlantState(
  1945	            tls_powered_s=snapshot["plant_state"].tls_powered_s,
  1946	            pls_powered_s=snapshot["plant_state"].pls_powered_s,
  1947	            tls_unlocked_ls=snapshot["plant_state"].tls_unlocked_ls,
  1948	            pls_unlocked_ls=snapshot["plant_state"].pls_unlocked_ls,
  1949	            deploy_position_percent=deploy_position,
  1950	        )
  1951	        sensors = manual_plant_state.sensors(config)
  1952	        sensors = _apply_sensor_fault_injections(sensors, fault_map)
  1953	        pilot_inputs = snapshot["pilot_inputs"]
  1954	        inputs = ResolvedInputs(
  1955	            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
  1956	            tra_deg=pilot_inputs.tra_deg,
  1957	            sw1=snapshot["inputs"].sw1,
  1958	            sw2=snapshot["inputs"].sw2,
  1959	            engine_running=pilot_inputs.engine_running,
  1960	            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
  1961	            reverser_inhibited=pilot_inputs.reverser_inhibited,
  1962	            eec_enable=pilot_inputs.eec_enable,
  1963	            n1k=pilot_inputs.n1k,
  1964	            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
  1965	            tls_unlocked_ls=sensors.tls_unlocked_ls,
  1966	            all_pls_unlocked_ls=sensors.all_pls_unlocked,
  1967	            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
  1968	            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
  1969	            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
  1970	        )
  1971	        controller_adapter = build_reference_controller_adapter(config)
  1972	        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
  1973	        outputs = _apply_output_fault_injections(outputs, fault_map)
  1974	        snapshot.update(
  1975	            {
  1976	                "plant_state": manual_plant_state,
  1977	                "sensors": sensors,
  1978	                "inputs": inputs,
  1979	                "outputs": outputs,
  1980	                "explain": explain,
  1981	            }
  1982	        )
  1983	    return snapshot
  1984	
  1985	
  1986	def _build_tra_lock_payload(
  1987	    *,
  1988	    config: HarnessConfig,
  1989	    requested_tra_deg: float,
  1990	    effective_tra_deg: float,
  1991	    lock_deg: float,
  1992	    boundary_unlock_ready: bool,
  1993	    deep_range_open: bool,
  1994	    unlock_blockers: list[str],
  1995	) -> dict:
  1996	    blocker_text = " / ".join(unlock_blockers) if unlock_blockers else "L4 条件"
  1997	    locked = not deep_range_open
  1998	    clamped = effective_tra_deg != requested_tra_deg
  1999	    allowed_reverse_min_deg = config.reverse_travel_min_deg if deep_range_open else lock_deg
  2000	    if deep_range_open:
  2001	        message = (
  2002	            f"L4 已满足：TRA 现在可以在 {config.reverse_travel_min_deg:.1f}° 到 0.0° 区间自由拖动。"
  2003	        )
  2004	    elif clamped:
  2005	        message = (
  2006	            f"L4 未满足：请求 {requested_tra_deg:.1f}° 已锁回 {lock_deg:.1f}°；"
  2007	            f"当前只能在 {lock_deg:.1f}° 到 0.0° 范围内拖动。"
  2008	        )
  2009	    else:
  2010	        message = (
  2011	            f"L4 未满足：当前自由拖动范围只开放 {lock_deg:.1f}° 到 0.0°；"
  2012	            f"满足 {blocker_text} 后，{config.reverse_travel_min_deg:.1f}° 到 {lock_deg:.1f}° 深拉区间才开放。"
  2013	        )
  2014	    return {
  2015	        "locked": locked,
  2016	        "clamped": clamped,
  2017	        "unlock_ready": deep_range_open,
  2018	        "boundary_unlock_ready": boundary_unlock_ready,
  2019	        "lock_deg": lock_deg,
  2020	        "requested_tra_deg": requested_tra_deg,
  2021	        "effective_tra_deg": effective_tra_deg,
  2022	        "allowed_reverse_min_deg": allowed_reverse_min_deg,
  2023	        "visual_reverse_min_deg": config.reverse_travel_min_deg,
  2024	        "deep_reverse_limit_deg": config.reverse_travel_min_deg,
  2025	        "unlock_logic": "logic4",
  2026	        "unlock_blockers": unlock_blockers,
  2027	        "message": message,
  2028	    }
  2029	
  2030	
  2031	def _monitor_ra_ft(time_s: float) -> float:
  2032	    return max(0.0, MONITOR_RA_START_FT - MONITOR_RA_RATE_FT_PER_S * time_s)
  2033	
  2034	
  2035	def _monitor_tra_deg(time_s: float) -> float:
  2036	    if time_s < MONITOR_TRA_START_S:
  2037	        return 0.0
  2038	    return max(MONITOR_TRA_LOCK_DEG, -(time_s - MONITOR_TRA_START_S) * MONITOR_TRA_RATE_DEG_PER_S)
  2039	
  2040	
  2041	def _monitor_vdt_percent(time_s: float) -> float:
  2042	    if time_s < MONITOR_VDT_START_S:
  2043	        return 0.0
  2044	    return min(100.0, (time_s - MONITOR_VDT_START_S) * MONITOR_VDT_RATE_PERCENT_PER_S)
  2045	
  2046	
  2047	def _monitor_series_definition() -> list[dict]:
  2048	    return [
  2049	        {"id": "ra", "label": "RA", "unit": "ft", "display_min": 0.0, "display_max": 7.0, "color": "#ff6f91", "category": "input"},
  2050	        {"id": "tra", "label": "TRA", "unit": "deg", "display_min": -32.0, "display_max": 0.0, "color": "#ffaa33", "category": "input"},
  2051	        {"id": "sw1", "label": "SW1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
  2052	        {"id": "logic1", "label": "L1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
  2053	        {"id": "tls", "label": "TLS", "unit": "V", "display_min": 0.0, "display_max": 115.0, "color": "#7dff9a", "category": "power"},
  2054	        {"id": "sw2", "label": "SW2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
  2055	        {"id": "logic2", "label": "L2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
  2056	        {"id": "etrac", "label": "ETRAC", "unit": "V", "display_min": 0.0, "display_max": 540.0, "color": "#86ffbf", "category": "power"},
  2057	        {"id": "logic3", "label": "L3", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
  2058	        {"id": "eec", "label": "EEC", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
  2059	        {"id": "pls", "label": "PLS", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
  2060	        {"id": "pdu", "label": "PDU", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
  2061	        {"id": "vdt", "label": "VDT", "unit": "%", "display_min": 0.0, "display_max": 100.0, "color": "#b69dff", "category": "sensor"},
  2062	        {"id": "logic4", "label": "L4", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
  2063	        {"id": "thr_lock", "label": "THR_LOCK", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ff8c7a", "category": "command"},
  2064	    ]
  2065	
  2066	
  2067	def _monitor_transition_time(rows: list[dict], field_name: str, target_value) -> float | None:
  2068	    for row in rows:
  2069	        if row[field_name] == target_value:
  2070	            return row["time_s"]
  2071	    return None
  2072	
  2073	
  2074	def _monitor_rows(config: HarnessConfig) -> list[dict]:
  2075	    controller_adapter = build_reference_controller_adapter(config)
  2076	    switches = LatchedThrottleSwitches(config)
  2077	    switch_state = SwitchState(previous_tra_deg=0.0)
  2078	    tls_powered_s = 0.0
  2079	    pls_powered_s = 0.0
  2080	    tls_unlocked_ls = False
  2081	    all_pls_unlocked_ls = False
  2082	    rows: list[dict] = []
  2083	
  2084	    step_count = int(round(MONITOR_TIMELINE_END_S / config.step_s))
  2085	    for step_index in range(step_count + 1):
  2086	        time_s = round(step_index * config.step_s, 3)
  2087	        radio_altitude_ft = _monitor_ra_ft(time_s)
  2088	        tra_deg = _monitor_tra_deg(time_s)
  2089	        vdt_percent = _monitor_vdt_percent(time_s)
  2090	        switch_state = switches.update(switch_state, tra_deg)
  2091	
  2092	        inputs = ResolvedInputs(
  2093	            radio_altitude_ft=radio_altitude_ft,
  2094	            tra_deg=tra_deg,
  2095	            sw1=switch_state.sw1,
  2096	            sw2=switch_state.sw2,
  2097	            engine_running=MONITOR_ENGINE_RUNNING,
  2098	            aircraft_on_ground=MONITOR_AIRCRAFT_ON_GROUND,
  2099	            reverser_inhibited=MONITOR_REVERSER_INHIBITED,
  2100	            eec_enable=MONITOR_EEC_ENABLE,

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2451,2745p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2451	        "nodes": nodes,
  2452	        "truth_evaluation": truth_eval.to_dict(),
  2453	        "default_snapshot": default_snapshot,
  2454	    }
  2455	
  2456	
  2457	def system_snapshot_post_payload(system_id: str, snapshot: dict) -> dict:
  2458	    """Evaluate a user-modified snapshot for a given system. Used by non-thrust systems."""
  2459	    adapter = _cached_adapter(system_id)
  2460	    if adapter is None:
  2461	        return {"error": "unknown_system", "system_id": system_id}
  2462	    spec = adapter.load_spec()
  2463	    truth_eval = adapter.evaluate_snapshot(snapshot)
  2464	    nodes = _spec_to_nodes(spec, truth_eval)
  2465	    return {
  2466	        "system_id": system_id,
  2467	        "title": spec.get("title", system_id),
  2468	        "spec": spec,
  2469	        "nodes": nodes,
  2470	        "truth_evaluation": truth_eval.to_dict(),
  2471	        "snapshot": snapshot,
  2472	    }
  2473	
  2474	
  2475	def lever_snapshot_payload(
  2476	    tra_deg: float,
  2477	    radio_altitude_ft: float = 5.0,
  2478	    engine_running: bool = True,
  2479	    aircraft_on_ground: bool = True,
  2480	    reverser_inhibited: bool = False,
  2481	    eec_enable: bool = True,
  2482	    n1k: float = 35.0,
  2483	    max_n1k_deploy_limit: float = 60.0,
  2484	    feedback_mode: str = "auto_scrubber",
  2485	    deploy_position_percent: float = 0.0,
  2486	    fault_injections: list[dict] | None = None,
  2487	) -> dict:
  2488	    config = HarnessConfig()
  2489	    requested_tra = _clamp_tra(tra_deg, config)
  2490	    lock_deg = _clamp_tra(TRA_L4_LOCK_DEG, config)
  2491	    requested_snapshot = _simulate_lever_state(
  2492	        requested_tra,
  2493	        config=config,
  2494	        radio_altitude_ft=radio_altitude_ft,
  2495	        engine_running=engine_running,
  2496	        aircraft_on_ground=aircraft_on_ground,
  2497	        reverser_inhibited=reverser_inhibited,
  2498	        eec_enable=eec_enable,
  2499	        n1k=n1k,
  2500	        max_n1k_deploy_limit=max_n1k_deploy_limit,
  2501	        feedback_mode=feedback_mode,
  2502	        deploy_position_percent=deploy_position_percent,
  2503	        fault_injections=fault_injections,
  2504	    )
  2505	    lock_probe = _simulate_lever_state(
  2506	        lock_deg,
  2507	        config=config,
  2508	        radio_altitude_ft=radio_altitude_ft,
  2509	        engine_running=engine_running,
  2510	        aircraft_on_ground=aircraft_on_ground,
  2511	        reverser_inhibited=reverser_inhibited,
  2512	        eec_enable=eec_enable,
  2513	        n1k=n1k,
  2514	        max_n1k_deploy_limit=max_n1k_deploy_limit,
  2515	        feedback_mode=feedback_mode,
  2516	        deploy_position_percent=deploy_position_percent,
  2517	        fault_injections=fault_injections,
  2518	    )
  2519	    boundary_unlock_ready = lock_probe["outputs"].logic4_active
  2520	    effective_tra = (
  2521	        requested_tra
  2522	        if boundary_unlock_ready or requested_tra >= lock_deg
  2523	        else lock_deg
  2524	    )
  2525	    snapshot = (
  2526	        requested_snapshot
  2527	        if effective_tra == requested_tra
  2528	        else lock_probe
  2529	    )
  2530	
  2531	    time_s = snapshot["time_s"]
  2532	    plant_debug_state = snapshot["plant_state"]
  2533	    sensors = snapshot["sensors"]
  2534	    pilot_inputs = snapshot["pilot_inputs"]
  2535	    inputs = snapshot["inputs"]
  2536	    outputs = snapshot["outputs"]
  2537	    explain = snapshot["explain"]
  2538	    deep_range_open = boundary_unlock_ready
  2539	    tra_lock = _build_tra_lock_payload(
  2540	        config=config,
  2541	        requested_tra_deg=requested_tra,
  2542	        effective_tra_deg=effective_tra,
  2543	        lock_deg=lock_deg,
  2544	        boundary_unlock_ready=boundary_unlock_ready,
  2545	        deep_range_open=deep_range_open,
  2546	        unlock_blockers=[condition.name for condition in lock_probe["explain"].logic4.failed_conditions],
  2547	    )
  2548	    logic1_completed = sensors.tls_unlocked_ls
  2549	    logic4_blockers = [condition.name for condition in explain.logic4.failed_conditions]
  2550	    logic3_blockers = [condition.name for condition in explain.logic3.failed_conditions]
  2551	
  2552	    nodes = [
  2553	        # ── Input sensor / signal nodes ──────────────────────────────────────
  2554	        # These are the ground-level signals; their "active" state is
  2555	        # computed to match the condition thresholds used by the logic gates.
  2556	        _node("radio_altitude_ft", "RA", "active" if inputs.radio_altitude_ft < 6.0 else "inactive",
  2557	              "Input sensors: altitude < 6 ft threshold"),
  2558	        _node("reverser_inhibited", "REV_INH",
  2559	              "inactive" if not inputs.reverser_inhibited else "active",
  2560	              "Input signals: true = inhibit active (blocked)"),
  2561	        _node("engine_running", "ENG",
  2562	              "active" if inputs.engine_running else "inactive",
  2563	              "Input signals"),
  2564	        _node("aircraft_on_ground", "GND",
  2565	              "active" if inputs.aircraft_on_ground else "inactive",
  2566	              "Input signals"),
  2567	        _node("eec_enable", "EEC_EN",
  2568	              "active" if inputs.eec_enable else "inactive",
  2569	              "Input signals"),
  2570	        _node("sw1", "SW1", "active" if inputs.sw1 else "inactive", "LatchedThrottleSwitches"),
  2571	        _node("sw2", "SW2", "active" if inputs.sw2 else "inactive", "LatchedThrottleSwitches"),
  2572	        # ── Intermediate / output nodes ────────────────────────────────────────
  2573	        _node("logic1", "L1", _logic_node_state(outputs.logic1_active), "DeployController.explain(logic1)", [condition.name for condition in explain.logic1.failed_conditions]),
  2574	        _node("tls115", "TLS115", "active" if outputs.tls_115vac_cmd or sensors.tls_unlocked_ls else "inactive", "DeployController outputs"),
  2575	        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
  2576	        _node("logic2", "L2", _logic_node_state(outputs.logic2_active), "DeployController.explain(logic2)", [condition.name for condition in explain.logic2.failed_conditions]),
  2577	        _node("etrac_540v", "540V", "active" if outputs.etrac_540vdc_cmd else "inactive", "DeployController outputs"),
  2578	        _node("logic3", "L3", _logic_node_state(outputs.logic3_active), "DeployController.explain(logic3)", logic3_blockers),
  2579	        _node("eec_deploy", "EEC", "active" if outputs.eec_deploy_cmd else "inactive", "DeployController outputs"),
  2580	        _node("pls_power", "PLS", "active" if outputs.pls_power_cmd else "inactive", "DeployController outputs"),
  2581	        _node("pdu_motor", "PDU", "active" if outputs.pdu_motor_cmd else "inactive", "DeployController outputs"),
  2582	        _node("vdt90", "VDT90", "active" if sensors.deploy_90_percent_vdt and outputs.logic3_active else "inactive", "SimplifiedDeployPlant sensors + L3 causal gate"),
  2583	        _node("logic4", "L4", _logic_node_state(outputs.logic4_active), "DeployController.explain(logic4)", logic4_blockers),
  2584	        _node(
  2585	            "thr_lock",
  2586	            "THR_LOCK",
  2587	            "active"
  2588	            if outputs.throttle_electronic_lock_release_cmd
  2589	            else (
  2590	                "blocked"
  2591	                if explain.logic4.failed_conditions
  2592	                else "inactive"
  2593	            ),
  2594	            # Use explain.logic4.failed_conditions to determine "blocked" vs "inactive".
  2595	            # This correctly handles the causal chain: when L4 is blocked (has unmet
  2596	            # conditions like tra_deg), THR_LOCK is "blocked" (waiting on L4).
  2597	            # When L4 has no failed conditions but is simply not active, THR_LOCK is "inactive".
  2598	            "DeployController outputs",
  2599	            logic4_blockers if not outputs.throttle_electronic_lock_release_cmd else [],
  2600	        ),
  2601	    ]
  2602	    summary = _lever_summary(effective_tra, inputs, sensors, outputs, explain, feedback_mode, tra_lock)
  2603	    model_note = (
  2604	        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
  2605	        if feedback_mode == "auto_scrubber"
  2606	        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"
  2607	    )
  2608	
  2609	    result = {
  2610	        "mode": (
  2611	            "canonical_pullback_scrubber"
  2612	            if feedback_mode == "auto_scrubber"
  2613	            else "manual_feedback_override"
  2614	        ),
  2615	        "model_note": model_note,
  2616	        "tra_lock": tra_lock,
  2617	        "input": {
  2618	            "requested_tra_deg": requested_tra,
  2619	            "tra_deg": effective_tra,
  2620	            "radio_altitude_ft": inputs.radio_altitude_ft,
  2621	            "engine_running": inputs.engine_running,
  2622	            "aircraft_on_ground": inputs.aircraft_on_ground,
  2623	            "reverser_inhibited": inputs.reverser_inhibited,
  2624	            "eec_enable": inputs.eec_enable,
  2625	            "n1k": inputs.n1k,
  2626	            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
  2627	            "feedback_mode": feedback_mode,
  2628	            "deploy_position_percent": deploy_position_percent,
  2629	        },
  2630	        "time_s": time_s,
  2631	        "hud": {
  2632	            "requested_tra_deg": requested_tra,
  2633	            "tra_deg": effective_tra,
  2634	            "sw1": inputs.sw1,
  2635	            "sw2": inputs.sw2,
  2636	            "radio_altitude_ft": inputs.radio_altitude_ft,
  2637	            "engine_running": inputs.engine_running,
  2638	            "aircraft_on_ground": inputs.aircraft_on_ground,
  2639	            "reverser_inhibited": inputs.reverser_inhibited,
  2640	            "eec_enable": inputs.eec_enable,
  2641	            "n1k": inputs.n1k,
  2642	            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
  2643	            "tls_unlocked_ls": sensors.tls_unlocked_ls,
  2644	            "pls_unlocked_ls": sensors.pls_unlocked_ls,
  2645	            "all_pls_unlocked_ls": sensors.all_pls_unlocked,
  2646	            "deploy_position_percent": sensors.deploy_position_percent,
  2647	            # In manual override mode: gate VDT90 display on L3 being active.
  2648	            # The user can force deploy_position_percent>=90 manually, but that
  2649	            # doesn't mean the causal chain is satisfied — VDT90 requires L3
  2650	            # (EEC deploy command) to be active first.
  2651	            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
  2652	            "feedback_mode": feedback_mode,
  2653	        },
  2654	        "outputs": {
  2655	            "logic1_active": outputs.logic1_active,
  2656	            "logic2_active": outputs.logic2_active,
  2657	            "logic3_active": outputs.logic3_active,
  2658	            "logic4_active": outputs.logic4_active,
  2659	            "tls_115vac_cmd": outputs.tls_115vac_cmd,
  2660	            "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
  2661	            "eec_deploy_cmd": outputs.eec_deploy_cmd,
  2662	            "pls_power_cmd": outputs.pls_power_cmd,
  2663	            "pdu_motor_cmd": outputs.pdu_motor_cmd,
  2664	            "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
  2665	        },
  2666	        "logic": {
  2667	            "logic1": _logic_payload(explain.logic1),
  2668	            "logic2": _logic_payload(explain.logic2),
  2669	            "logic3": _logic_payload(explain.logic3),
  2670	            "logic4": _logic_payload(explain.logic4),
  2671	        },
  2672	        "plant_state": {
  2673	            "tls_powered_s": plant_debug_state.tls_powered_s,
  2674	            "pls_powered_s": plant_debug_state.pls_powered_s,
  2675	            "tls_unlocked_ls": plant_debug_state.tls_unlocked_ls,
  2676	            "pls_unlocked_ls": plant_debug_state.pls_unlocked_ls,
  2677	            "deploy_position_percent": plant_debug_state.deploy_position_percent,
  2678	        },
  2679	        "nodes": nodes,
  2680	        "summary": summary,
  2681	        "evidence": [
  2682	            "switches=LatchedThrottleSwitches.update(...)",
  2683	            "controller=DeployController.evaluate_with_explain(...)",
  2684	            "explain=DeployController.explain(...)",
  2685	            "plant=SimplifiedDeployPlant first-cut feedback model",
  2686	            "tra_lock=L4 gate at -14° before deeper reverse travel",
  2687	        ],
  2688	        "risks": [
  2689	            "PLS / VDT feedback comes from simplified first-cut plant timing.",
  2690	            "Manual feedback override is only a diagnostic demo control, not new control truth.",
  2691	            "THR_LOCK release must not be read as complete physical root-cause proof.",
  2692	        ],
  2693	    }
  2694	    return _apply_fault_injections_to_snapshot_payload(result, fault_injections)
  2695	
  2696	
  2697	def build_parser() -> argparse.ArgumentParser:
  2698	    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
  2699	    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
  2700	    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
  2701	    parser.add_argument(
  2702	        "--open",
  2703	        action="store_true",
  2704	        help=(
  2705	            "Open the local UI URL with Python's standard-library webbrowser.open; "
  2706	            "this is a launch convenience, not browser E2E automation."
  2707	        ),
  2708	    )
  2709	    return parser
  2710	
  2711	
  2712	def demo_url(host: str, port: int) -> str:
  2713	    return f"http://{host}:{port}/index.html"
  2714	
  2715	
  2716	def open_browser(url: str, opener=webbrowser.open) -> bool:
  2717	    try:
  2718	        opened = bool(opener(url))
  2719	    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
  2720	        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
  2721	        return False
  2722	    if not opened:
  2723	        print(f"Could not open browser automatically. Open {url} manually.")
  2724	    return opened
  2725	
  2726	
  2727	def main(argv: list[str] | None = None) -> int:
  2728	    args = build_parser().parse_args(argv)
  2729	    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
  2730	    host, port = server.server_address
  2731	    url = demo_url(host, port)
  2732	    print(f"Serving well-harness demo UI at {url}")
  2733	    if args.open:
  2734	        open_browser(url)
  2735	    try:
  2736	        server.serve_forever()
  2737	    except KeyboardInterrupt:
  2738	        print("\nStopping well-harness demo UI.")
  2739	    finally:
  2740	        server.server_close()
  2741	    return 0
  2742	
  2743	
  2744	if __name__ == "__main__":
  2745	    raise SystemExit(main())

exec
/bin/zsh -lc "nl -ba src/well_harness/static/fan_console.html | sed -n '1,220p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	<!DOCTYPE html>
     2	<html lang="zh-CN">
     3	<head>
     4	<meta charset="UTF-8">
     5	<meta name="viewport" content="width=device-width,initial-scale=1">
     6	<title>反推实时操作台 · FANTUI LogicMVP</title>
     7	<link rel="stylesheet" href="/unified-nav.css">
     8	<style>
     9	:root {
    10	  --bg0: #02080f;
    11	  --bg1: #071020;
    12	  --bg2: #0c1830;
    13	  --bg3: #112443;
    14	  --bg4: #182e52;
    15	  --b0: #1c2f4d;
    16	  --b1: #253d65;
    17	  --b2: #2e4a7d;
    18	  --text0: #e6ecf6;
    19	  --text1: #95adca;
    20	  --text2: #56708d;
    21	  --amber: #f5a623;
    22	  --amber-d: rgba(245,166,35,0.15);
    23	  --green: #4ade80;
    24	  --green-d: rgba(74,222,128,0.12);
    25	  --red: #f87171;
    26	  --red-d: rgba(248,113,113,0.12);
    27	  --cyan: #22d3ee;
    28	  --cyan-d: rgba(34,211,238,0.12);
    29	  --mono: 'JetBrains Mono','SF Mono',monospace;
    30	  --ui: 'Inter','PingFang SC',system-ui,sans-serif;
    31	  --nav-h: 48px;
    32	}
    33	*{box-sizing:border-box;margin:0;padding:0}
    34	html,body{height:100%;overflow:hidden}
    35	body{background:var(--bg0);color:var(--text0);font-family:var(--ui);font-size:12px;display:flex;flex-direction:column;padding-top:var(--nav-h)}
    36	
    37	.console-head{
    38	  height:44px;background:var(--bg1);border-bottom:1px solid var(--b1);
    39	  display:flex;align-items:center;padding:0 16px;gap:12px;flex-shrink:0;
    40	}
    41	.hbadge{
    42	  font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.1em;
    43	  padding:3px 10px;border-radius:3px;
    44	  background:linear-gradient(135deg,#0a1f40,#0b2d5a);
    45	  border:1px solid var(--cyan);color:var(--cyan);
    46	}
    47	.htitle{font-size:14px;font-weight:600}
    48	.hsub{font-size:10px;color:var(--text2);font-family:var(--mono)}
    49	.hgap{flex:1}
    50	.hcontrols{display:flex;align-items:center;gap:8px}
    51	.btn{
    52	  padding:4px 12px;border-radius:4px;border:1px solid var(--b2);
    53	  background:var(--bg3);color:var(--text1);cursor:pointer;font-size:11px;
    54	  transition:all .15s;font-family:var(--ui);
    55	}
    56	.btn:hover{border-color:var(--cyan);color:var(--cyan)}
    57	.btn.active{background:var(--cyan-d);border-color:var(--cyan);color:var(--cyan)}
    58	.btn.danger:hover{border-color:var(--red);color:var(--red)}
    59	.sim-dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 6px var(--red);transition:all .3s}
    60	.sim-dot.running{background:var(--green);box-shadow:0 0 8px var(--green);animation:blink 1s infinite}
    61	@keyframes blink{0%,100%{opacity:1}50%{opacity:.5}}
    62	.htime{font-family:var(--mono);font-size:12px;color:var(--amber);min-width:70px;text-align:right}
    63	
    64	/* ── LAYOUT ── */
    65	.workspace{
    66	  flex:1;overflow:hidden;display:grid;
    67	  grid-template-columns:310px 1fr 300px;gap:1px;background:var(--b0);
    68	}
    69	.panel{background:var(--bg1);overflow-y:auto;display:flex;flex-direction:column}
    70	
    71	.sec{border-bottom:1px solid var(--b0);padding:10px 12px;display:flex;flex-direction:column;gap:7px}
    72	.sec-title{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--text2);margin-bottom:3px}
    73	.row{display:flex;align-items:center;gap:6px}
    74	.row label{color:var(--text1);font-size:11px;flex:1;white-space:nowrap}
    75	.val{font-family:var(--mono);font-size:11px;color:var(--text1);min-width:58px;text-align:right}
    76	
    77	.tog{position:relative;display:inline-block;width:36px;height:18px;flex-shrink:0}
    78	.tog input{opacity:0;width:0;height:0}
    79	.tog span{position:absolute;inset:0;border-radius:9px;cursor:pointer;background:var(--bg4);border:1px solid var(--b1);transition:.2s}
    80	.tog span::after{content:'';position:absolute;width:12px;height:12px;border-radius:50%;background:var(--text2);top:2px;left:2px;transition:.2s}
    81	.tog input:checked+span{background:var(--green-d);border-color:var(--green)}
    82	.tog input:checked+span::after{background:var(--green);transform:translateX(18px)}
    83	.tog.warn input:checked+span{background:var(--red-d);border-color:var(--red)}
    84	.tog.warn input:checked+span::after{background:var(--red)}
    85	
    86	input[type=range]{
    87	  -webkit-appearance:none;height:4px;border-radius:2px;
    88	  background:var(--b2);outline:none;cursor:pointer;width:100%;
    89	}
    90	input[type=range]::-webkit-slider-thumb{
    91	  -webkit-appearance:none;width:14px;height:14px;border-radius:50%;
    92	  background:var(--amber);cursor:pointer;border:2px solid var(--bg2);
    93	}
    94	
    95	/* ── Logic gate cards ── */
    96	.gate-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:10px 12px}
    97	.gate-card{
    98	  padding:9px 10px;border-radius:5px;border:1px solid var(--b0);background:var(--bg2);
    99	  display:flex;flex-direction:column;gap:4px;transition:all .2s;
   100	}
   101	.gate-card.on{border-color:var(--green);background:var(--green-d)}
   102	.gate-card.on .g-name{color:var(--green)}
   103	.gate-card.on .g-val{color:var(--green)}
   104	.gate-card.off .g-name{color:var(--text2)}
   105	.g-name{font-size:9px;text-transform:uppercase;letter-spacing:.06em;font-weight:700}
   106	.g-val{font-family:var(--mono);font-size:13px;font-weight:700}
   107	.g-sub{font-size:9px;color:var(--text2);font-family:var(--mono)}
   108	
   109	.cmd-grid{display:flex;flex-direction:column;gap:4px;padding:6px 12px 12px}
   110	.cmd-row{
   111	  padding:7px 10px;border-radius:4px;border:1px solid var(--b0);background:var(--bg2);
   112	  display:flex;align-items:center;justify-content:space-between;gap:6px;transition:all .2s;
   113	}
   114	.cmd-row.on{border-color:var(--amber);background:var(--amber-d)}
   115	.cmd-row.on .c-val{color:var(--amber)}
   116	.c-name{font-size:10px;color:var(--text1)}
   117	.c-val{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--text2);transition:all .2s}
   118	
   119	/* ── Plant gauges ── */
   120	.gauges{display:flex;gap:8px;padding:10px 12px;justify-content:space-around;border-top:1px solid var(--b0)}
   121	.gauge{display:flex;flex-direction:column;align-items:center;gap:4px}
   122	.gauge svg{width:80px;height:50px}
   123	
   124	/* ── Log ── */
   125	.log-wrap{flex:1;overflow:hidden;display:flex;flex-direction:column;padding:0 12px 10px}
   126	.log-head{font-size:9px;color:var(--text2);text-transform:uppercase;letter-spacing:.08em;padding:6px 0;display:flex;justify-content:space-between}
   127	.log-body{
   128	  flex:1;overflow-y:auto;background:var(--bg0);border:1px solid var(--b0);border-radius:4px;
   129	  font-family:var(--mono);font-size:10px;color:var(--text2);padding:4px 6px;line-height:1.6;
   130	}
   131	.log-line.active{color:var(--green)}
   132	.log-line.armed{color:var(--amber)}
   133	
   134	/* ── Presets ── */
   135	.presets{
   136	  height:48px;border-top:1px solid var(--b0);background:var(--bg1);
   137	  display:flex;align-items:center;padding:0 14px;gap:8px;flex-shrink:0;overflow-x:auto;
   138	}
   139	.presets span{font-size:9px;color:var(--text2);text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;margin-right:4px}
   140	.preset-btn{
   141	  padding:4px 10px;border-radius:4px;border:1px solid var(--b1);
   142	  background:var(--bg3);color:var(--text2);cursor:pointer;font-size:10px;
   143	  white-space:nowrap;transition:all .15s;flex-shrink:0;font-family:var(--ui);
   144	}
   145	.preset-btn:hover{border-color:var(--amber);color:var(--amber);background:var(--amber-d)}
   146	
   147	/* ── Chart drawer ── */
   148	.tsc-drawer{
   149	  flex-shrink:0;background:var(--bg1);border-top:1px solid var(--b1);
   150	  max-height:0;overflow:hidden;transition:max-height .25s ease;
   151	}
   152	.tsc-drawer.open{max-height:320px;overflow:visible}
   153	.tsc-drawer-inner{padding:8px 12px 10px;display:flex;flex-direction:column;gap:6px}
   154	.tsc-drawer-head{display:flex;align-items:center;gap:10px;font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:.08em}
   155	.tsc-drawer-title{color:var(--cyan);font-family:var(--mono);font-weight:700}
   156	.tsc-drawer-chart{background:var(--bg0);border:1px solid var(--b0);border-radius:3px;overflow-x:auto}
   157	#tsc-svg{display:block;font-family:var(--mono)}
   158	.tsc-legend{display:flex;flex-wrap:wrap;gap:10px;font-size:10px;color:var(--text2);font-family:var(--mono)}
   159	.tsc-legend-item{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
   160	
   161	/* ── Series selector dropdown ── */
   162	.tsc-selector{position:relative;display:inline-block}
   163	.tsc-selector>summary{
   164	  cursor:pointer;list-style:none;padding:2px 10px;border-radius:3px;
   165	  border:1px solid var(--b1);background:var(--bg3);color:var(--cyan);
   166	  font-size:10px;font-family:var(--mono);user-select:none;
   167	}
   168	.tsc-selector>summary::-webkit-details-marker,.tsc-selector>summary::marker{display:none}
   169	.tsc-selector-panel{
   170	  position:absolute;top:calc(100% + 3px);left:0;z-index:300;
   171	  background:var(--bg2);border:1px solid var(--b1);border-radius:5px;
   172	  padding:8px 10px;display:grid;grid-template-columns:repeat(3,1fr);
   173	  gap:4px 14px;min-width:400px;box-shadow:0 6px 20px rgba(0,0,0,.6);
   174	}
   175	.tsc-sel-header{
   176	  grid-column:1/-1;display:flex;align-items:center;gap:8px;
   177	  margin-bottom:5px;border-bottom:1px solid var(--b0);padding-bottom:5px;
   178	}
   179	.tsc-sel-header span{font-size:9px;color:var(--text2);text-transform:uppercase;letter-spacing:.08em;flex:1}
   180	.tsc-sel-act{font-size:9px;color:var(--text2);cursor:pointer;text-decoration:underline;white-space:nowrap;background:none;border:none;padding:0;font-family:var(--mono)}
   181	.tsc-sel-act:hover{color:var(--cyan)}
   182	.tsc-sel-item{display:flex;align-items:center;gap:5px;cursor:pointer;font-size:10px;color:var(--text1);font-family:var(--mono);white-space:nowrap}
   183	.tsc-sel-item input[type=checkbox]{cursor:pointer;accent-color:var(--cyan);flex-shrink:0}
   184	.tsc-sel-swatch{width:18px;height:3px;border-radius:1px;display:inline-block;flex-shrink:0}
   185	
   186	::-webkit-scrollbar{width:4px;height:4px}
   187	::-webkit-scrollbar-track{background:transparent}
   188	::-webkit-scrollbar-thumb{background:var(--b2);border-radius:2px}
   189	</style>
   190	</head>
   191	<body class="unified-nav-enabled" data-nav-current="fan-console">
   192	
   193	<header class="unified-nav" role="navigation" aria-label="FANTUI LogicMVP 主导航">
   194	  <a href="/index.html" class="unified-nav-brand" aria-label="返回主入口">FANTUI LogicMVP</a>
   195	  <div class="unified-nav-groups">
   196	    <div class="unified-nav-group">
   197	      <span class="unified-nav-group-label">工作台</span>
   198	      <a href="/demo.html" class="unified-nav-link" data-nav-key="demo">反推逻辑</a>
   199	      <a href="/c919_etras_workstation.html" class="unified-nav-link" data-nav-key="etras">C919 E-TRAS</a>
   200	    </div>
   201	    <div class="unified-nav-group">
   202	      <span class="unified-nav-group-label">电路图</span>
   203	      <a href="/fantui_circuit.html" class="unified-nav-link" data-nav-key="fantui-circuit">反推电路</a>
   204	      <a href="/c919_etras_panel/circuit.html" class="unified-nav-link" data-nav-key="etras-circuit">E-TRAS 电路</a>
   205	    </div>
   206	    <div class="unified-nav-group">
   207	      <span class="unified-nav-group-label">仿真</span>
   208	      <a href="/fan_console.html" class="unified-nav-link" data-nav-key="fan-console" data-current="true">反推操作台</a>
   209	      <a href="http://127.0.0.1:9191/" class="unified-nav-link unified-nav-link-ext" data-nav-key="panel-9191">C919 MFD :9191</a>
   210	    </div>
   211	    <div class="unified-nav-group">
   212	      <span class="unified-nav-group-label">文档</span>
   213	      <a href="/fantui_requirements.html" class="unified-nav-link" data-nav-key="fantui-req">FANTUI 需求</a>
   214	      <a href="/c919_requirements.html" class="unified-nav-link" data-nav-key="c919-req">C919 需求</a>
   215	    </div>
   216	  </div>
   217	</header>
   218	
   219	<div class="console-head">
   220	  <div class="hbadge">FANTUI · LIVE</div>

exec
/bin/zsh -lc "nl -ba src/well_harness/static/demo.js | sed -n '1,300p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/fan_console.html | sed -n '221,440p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/demo.js | sed -n '301,548p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/fan_console.html | sed -n '441,687p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   221	  <div class="htitle">反推实时操作台</div>
   222	  <div class="hsub">POST /api/fantui/tick · stateful</div>
   223	  <div class="hgap"></div>
   224	  <div class="hcontrols">
   225	    <div class="sim-dot" id="simDot"></div>
   226	    <button class="btn" id="btnPlay" onclick="toggleSim()">▶ 仿真</button>
   227	    <button class="btn danger" onclick="resetSim()">↺ 重置</button>
   228	    <button class="btn" id="btnChart" onclick="toggleChart()">📈 时序图</button>
   229	    <div class="htime" id="hTime">T: 0.000s</div>
   230	  </div>
   231	</div>
   232	
   233	<div class="workspace">
   234	
   235	  <!-- LEFT: 输入杠杆 -->
   236	  <div class="panel">
   237	    <div class="sec">
   238	      <div class="sec-title">飞行环境</div>
   239	      <div class="row"><label>Radio Altitude</label><span class="val" id="v_ra">20 ft</span></div>
   240	      <div class="row"><input type="range" id="ra" min="0" max="50" step="0.5" value="20" oninput="syncRa()"></div>
   241	      <div class="row" style="margin-top:4px"><label>Aircraft On Ground</label><label class="tog"><input type="checkbox" id="onGround" checked onchange="sync()"><span></span></label></div>
   242	      <div class="row"><label>Engine Running</label><label class="tog"><input type="checkbox" id="engineRunning" onchange="sync()"><span></span></label></div>
   243	    </div>
   244	
   245	    <div class="sec">
   246	      <div class="sec-title">油门杆 · TRA</div>
   247	      <div class="row"><label>TRA 角度</label><span class="val" id="v_tra">0.0°</span></div>
   248	      <div class="row"><input type="range" id="tra" min="-32" max="2" step="0.1" value="0" oninput="syncTra()"></div>
   249	      <div class="row" style="margin-top:4px">
   250	        <label>SW1 (latched)</label>
   251	        <span class="val" id="v_sw1" style="min-width:32px">0</span>
   252	      </div>
   253	      <div class="row">
   254	        <label>SW2 (latched)</label>
   255	        <span class="val" id="v_sw2" style="min-width:32px">0</span>
   256	      </div>
   257	      <div style="font-size:9px;color:var(--text2);font-family:var(--mono);margin-top:2px">
   258	        SW1 window: [-1.4°, -6.2°] · SW2 window: [-5.0°, -9.8°]
   259	      </div>
   260	    </div>
   261	
   262	    <div class="sec">
   263	      <div class="sec-title">引擎参数 · N1k</div>
   264	      <div class="row"><label>N1k</label><span class="val" id="v_n1k">55%</span></div>
   265	      <div class="row"><input type="range" id="n1k" min="0" max="110" step="0.5" value="55" oninput="syncN1k()"></div>
   266	      <div class="row" style="margin-top:4px">
   267	        <label>Max N1k Deploy Limit</label>
   268	        <span class="val" id="v_n1klim">85%</span>
   269	      </div>
   270	      <div class="row"><input type="range" id="n1klim" min="60" max="100" step="1" value="85" oninput="syncN1kLim()"></div>
   271	    </div>
   272	
   273	    <div class="sec">
   274	      <div class="sec-title">抑制与使能</div>
   275	      <div class="row"><label>Reverser Inhibited</label><label class="tog warn"><input type="checkbox" id="inhibit" onchange="sync()"><span></span></label></div>
   276	      <div class="row"><label>EEC Enable</label><label class="tog"><input type="checkbox" id="eec" checked onchange="sync()"><span></span></label></div>
   277	    </div>
   278	
   279	    <div class="sec">
   280	      <div class="sec-title" style="color:var(--amber)">⚡ VDT 位置注入（plant 覆盖）</div>
   281	      <div class="row"><label>Deploy Position</label><span class="val" id="v_vdt_inj">0.0%</span></div>
   282	      <div class="row"><input type="range" id="vdt_inj" min="0" max="100" step="0.5" value="0" oninput="syncVdtInj()"></div>
   283	      <div style="font-size:9px;color:var(--text2);font-family:var(--mono);margin-top:2px">
   284	        直接写入 plant 位置，绕过电机积分。VDT≥90% 触发 VDT90 传感器。
   285	      </div>
   286	    </div>
   287	  </div>
   288	
   289	  <!-- CENTER: 逻辑门 + 命令 + 仪表 -->
   290	  <div class="panel">
   291	    <div style="padding:10px 12px 4px"><div class="sec-title">逻辑门 · 实时求值</div></div>
   292	    <div class="gate-grid">
   293	      <div class="gate-card off" id="gate_l1">
   294	        <div class="g-name">L1 · RA &lt; 6 ft · SW1 · !Inhibit · !Deployed_EEC</div>
   295	        <div class="g-val" id="gv_l1">FALSE</div>
   296	      </div>
   297	      <div class="gate-card off" id="gate_l2">
   298	        <div class="g-name">L2 · Engine · GND · !Inhibit · SW2 · EEC</div>
   299	        <div class="g-val" id="gv_l2">FALSE</div>
   300	      </div>
   301	      <div class="gate-card off" id="gate_l3">
   302	        <div class="g-name">L3 · Engine · GND · !Inhibit · TLS↑ · N1k &lt; max · TRA ≤ -11.74°</div>
   303	        <div class="g-val" id="gv_l3">FALSE</div>
   304	      </div>
   305	      <div class="gate-card off" id="gate_l4">
   306	        <div class="g-name">L4 · VDT90 · -32° ≤ TRA &lt; 0° · GND · Engine</div>
   307	        <div class="g-val" id="gv_l4">FALSE</div>
   308	      </div>
   309	    </div>
   310	
   311	    <div style="padding:8px 12px 4px;border-top:1px solid var(--b0)"><div class="sec-title">电气 / 作动命令</div></div>
   312	    <div class="cmd-grid">
   313	      <div class="cmd-row off" id="cmd_tls"><span class="c-name">TLS 115VAC</span><span class="c-val" id="cv_tls">OFF</span></div>
   314	      <div class="cmd-row off" id="cmd_etrac"><span class="c-name">ETRAC 540VDC</span><span class="c-val" id="cv_etrac">OFF</span></div>
   315	      <div class="cmd-row off" id="cmd_eec"><span class="c-name">EEC Deploy</span><span class="c-val" id="cv_eec">OFF</span></div>
   316	      <div class="cmd-row off" id="cmd_pls"><span class="c-name">PLS Power</span><span class="c-val" id="cv_pls">OFF</span></div>
   317	      <div class="cmd-row off" id="cmd_pdu"><span class="c-name">PDU Motor</span><span class="c-val" id="cv_pdu">OFF</span></div>
   318	      <div class="cmd-row off" id="cmd_thr"><span class="c-name">Throttle Unlock (THR_LOCK_RELEASE)</span><span class="c-val" id="cv_thr">OFF</span></div>
   319	    </div>
   320	
   321	    <div class="gauges">
   322	      <div class="gauge">
   323	        <svg viewBox="0 0 80 50">
   324	          <path d="M10,45 A35,35,0,0,1,70,45" fill="none" stroke="#1c2e4a" stroke-width="6" stroke-linecap="round"/>
   325	          <path id="gVdtArc" d="M10,45 A35,35,0,0,1,70,45" fill="none" stroke="#b69dff" stroke-width="6" stroke-linecap="round" stroke-dasharray="0,1000"/>
   326	          <text x="40" y="33" text-anchor="middle" fill="#b69dff" font-size="11" font-family="monospace" font-weight="700" id="gVdtTxt">0%</text>
   327	          <text x="40" y="48" text-anchor="middle" fill="#56708d" font-size="7">VDT (deploy%)</text>
   328	        </svg>
   329	      </div>
   330	      <div class="gauge">
   331	        <svg viewBox="0 0 80 50">
   332	          <path d="M10,45 A35,35,0,0,1,70,45" fill="none" stroke="#1c2e4a" stroke-width="6" stroke-linecap="round"/>
   333	          <path id="gTraArc" d="M10,45 A35,35,0,0,1,70,45" fill="none" stroke="#f5a623" stroke-width="6" stroke-linecap="round" stroke-dasharray="0,1000"/>
   334	          <text x="40" y="33" text-anchor="middle" fill="#f5a623" font-size="11" font-family="monospace" font-weight="700" id="gTraTxt">0.0°</text>
   335	          <text x="40" y="48" text-anchor="middle" fill="#56708d" font-size="7">TRA</text>
   336	        </svg>
   337	      </div>
   338	    </div>
   339	  </div>
   340	
   341	  <!-- RIGHT: plant 状态 + 日志 -->
   342	  <div class="panel">
   343	    <div class="sec">
   344	      <div class="sec-title">反推位置（plant 模型）</div>
   345	      <div class="row"><label>Deploy Position</label><span class="val" id="v_pos">0.0%</span></div>
   346	      <div class="row" style="font-size:9px;color:var(--text2)"><label>驱动条件</label><span class="val" id="v_drive">–</span></div>
   347	      <div class="row"><label>TLS 解锁</label><span class="val" id="v_tlsu">NO</span></div>
   348	      <div class="row"><label>PLS 全解锁</label><span class="val" id="v_plsu">NO</span></div>
   349	      <div class="row"><label>VDT ≥ 90%</label><span class="val" id="v_vdt90">NO</span></div>
   350	    </div>
   351	
   352	    <div class="log-wrap">
   353	      <div class="log-head">
   354	        <span>遥测日志 (最近 40 条)</span>
   355	        <span id="logCount" style="color:var(--text2)">0 ticks</span>
   356	      </div>
   357	      <div class="log-body" id="logBody"></div>
   358	    </div>
   359	  </div>
   360	</div>
   361	
   362	<!-- Chart drawer -->
   363	<div class="tsc-drawer" id="tscDrawer" aria-hidden="true">
   364	  <div class="tsc-drawer-inner">
   365	    <div class="tsc-drawer-head">
   366	      <span class="tsc-drawer-title">时间-状态曲线</span>
   367	      <span>数据源: /api/fantui/log · 最近 400 ticks</span>
   368	      <details class="tsc-selector" id="tscSelector">
   369	        <summary id="tscSelectorSummary">选择信号 ▾</summary>
   370	        <div class="tsc-selector-panel" id="tscSelectorPanel">
   371	          <div class="tsc-sel-header">
   372	            <span>显示的信号通道</span>
   373	            <button class="tsc-sel-act" onclick="selectAllSeries()">全选</button>
   374	            <button class="tsc-sel-act" onclick="clearAllSeries()">清空</button>
   375	          </div>
   376	        </div>
   377	      </details>
   378	      <span style="flex:1"></span>
   379	      <span id="tscCount" style="font-family:var(--mono)">0 samples</span>
   380	    </div>
   381	    <div class="tsc-drawer-chart">
   382	      <svg id="tsc-svg" viewBox="0 0 1100 240" width="1100" height="240"
   383	           role="img" aria-label="FANTUI 反推时间序列图"></svg>
   384	    </div>
   385	    <div id="tsc-legend" class="tsc-legend"></div>
   386	  </div>
   387	</div>
   388	
   389	<div class="presets">
   390	  <span>Preset</span>
   391	  <button class="preset-btn" onclick="loadPreset('air')">空中（RA=20, engine off）</button>
   392	  <button class="preset-btn" onclick="loadPreset('ground_idle')">接地怠速</button>
   393	  <button class="preset-btn" onclick="loadPreset('arm_sw1')">拉入 SW1 (-3°)</button>
   394	  <button class="preset-btn" onclick="loadPreset('arm_sw2')">拉入 SW2 (-8°)</button>
   395	  <button class="preset-btn" onclick="loadPreset('deploy')">展开指令 (-15°)</button>
   396	  <button class="preset-btn" onclick="loadPreset('full_rev')">全反推 (-28°)</button>
   397	  <button class="preset-btn" onclick="loadPreset('pull_back')">回杆</button>
   398	  <button class="preset-btn" onclick="loadPreset('inhibit')">⚠ 抑制</button>
   399	</div>
   400	
   401	<script src="/timeseries_chart.js"></script>
   402	<script>
   403	// ── helpers ─────────────────────────────────────────
   404	const $ = (id)=>document.getElementById(id);
   405	const get = (id)=>$(id).value;
   406	const getB = (id)=>$(id).checked;
   407	const num = (id)=>parseFloat($(id).value);
   408	
   409	function syncRa(){$('v_ra').textContent=num('ra').toFixed(1)+' ft';sync();}
   410	function syncTra(){$('v_tra').textContent=num('tra').toFixed(1)+'°';sync();}
   411	function syncN1k(){$('v_n1k').textContent=num('n1k').toFixed(1)+'%';sync();}
   412	function syncN1kLim(){$('v_n1klim').textContent=num('n1klim')+'%';sync();}
   413	function syncVdtInj(){
   414	  const pct=num('vdt_inj');
   415	  $('v_vdt_inj').textContent=pct.toFixed(1)+'%';
   416	  fetch('/api/fantui/set_vdt',{
   417	    method:'POST',
   418	    headers:{'Content-Type':'application/json'},
   419	    // E11-14 R2: explicit test-probe acknowledgment (this UI is a debug
   420	    // console; for authoritative manual feedback, use /api/lever-snapshot
   421	    // with sign-off via the workbench Approval Center).
   422	    body:JSON.stringify({deploy_position_percent:pct,test_probe_acknowledgment:true}),
   423	  }).then(r=>r.ok&&r.json()).then(snap=>{
   424	    if(snap&&snap.deploy_position_percent!=null)
   425	      $('v_pos').textContent=snap.deploy_position_percent.toFixed(1)+'%';
   426	  }).catch(()=>{});
   427	}
   428	
   429	function buildPayload(){
   430	  return {
   431	    radio_altitude_ft: num('ra'),
   432	    tra_deg: num('tra'),
   433	    engine_running: getB('engineRunning'),
   434	    aircraft_on_ground: getB('onGround'),
   435	    reverser_inhibited: getB('inhibit'),
   436	    eec_enable: getB('eec'),
   437	    n1k: num('n1k'),
   438	    max_n1k_deploy_limit: num('n1klim'),
   439	    dt_s: 0.1,
   440	  };

 succeeded in 0ms:
     1	/* FANTUI 反推逻辑演示舱 — demo.js
     2	 *
     3	 * Architecture: stateless signal-level evaluation via /api/lever-snapshot.
     4	 * User moves TRA slider / toggles → debounced POST → render chain SVG + HUD
     5	 * + output cards + status banner + tra_lock gate + fault injection.
     6	 *
     7	 * Phase UI-D (2026-04-22): replaced legacy ~2100-line demo.js.
     8	 * Phase UI-H (2026-04-22): wire state coloring + gate icons + TRA lock + fault panel.
     9	 * Legacy archived at archive/shelved/multi-system-ui/static/legacy-demo.js.
    10	 */
    11	(function () {
    12	  "use strict";
    13	
    14	  const API_URL = "/api/lever-snapshot";
    15	  const DEBOUNCE_MS = 120;
    16	
    17	  const $ = (id) => document.getElementById(id);
    18	
    19	  const inputs = {
    20	    tra:               $("fan-tra-lever"),
    21	    ra:                $("fan-ra"),
    22	    n1k:               $("fan-n1k"),
    23	    vdt:               $("fan-vdt"),
    24	    engineRunning:     $("fan-engine-running"),
    25	    aircraftOnGround:  $("fan-aircraft-on-ground"),
    26	    reverserInhibited: $("fan-reverser-inhibited"),
    27	    eecEnable:         $("fan-eec-enable"),
    28	  };
    29	
    30	  const readouts = {
    31	    traValue:        $("fan-tra-value"),
    32	    traZone:         $("fan-tra-zone"),
    33	    raValue:         $("fan-ra-value"),
    34	    n1kValue:        $("fan-n1k-value"),
    35	    vdtValue:        $("fan-vdt-value"),
    36	    statusBadge:     $("fan-status-badge"),
    37	    statusSummary:   $("fan-status-summary"),
    38	    completionFlag:  $("fan-completion-flag"),
    39	    hudSw1:          $("fan-hud-sw1"),
    40	    hudSw2:          $("fan-hud-sw2"),
    41	    hudTls:          $("fan-hud-tls"),
    42	    hudVdt90:        $("fan-hud-vdt90"),
    43	    hudLogic:        $("fan-hud-logic"),
    44	    hudThrLock:      $("fan-hud-thr-lock"),
    45	    outTls115:       $("fan-out-tls115"),
    46	    outTls115V:      $("fan-out-tls115-value"),
    47	    outEtrac:        $("fan-out-etrac"),
    48	    outEtracV:       $("fan-out-etrac-value"),
    49	    outEec:          $("fan-out-eec"),
    50	    outEecV:         $("fan-out-eec-value"),
    51	    outThr:          $("fan-out-thr"),
    52	    outThrV:         $("fan-out-thr-value"),
    53	    presetStatus:    $("fan-preset-status"),
    54	    traLockBadge:    $("fan-tra-lock-badge"),
    55	    traLockRange:    $("fan-tra-lock-range"),
    56	    traLockMsg:      $("fan-tra-lock-msg"),
    57	    faultCount:      $("fan-fault-count"),
    58	    faultActiveList: $("fan-fault-active-list"),
    59	    vdtHint:         $("fan-vdt-hint"),
    60	  };
    61	
    62	  const chainSvg = document.getElementById("fan-chain-svg");
    63	
    64	  // TRA deep-range lock state: -14° lock, -32° full range
    65	  const TRA_LOCK_DEG = -14.0;
    66	  let traLockActive = true;  // conservative default until first response
    67	
    68	  function numValue(el, fallback) {
    69	    if (!el) return fallback;
    70	    const v = parseFloat(el.value);
    71	    return Number.isFinite(v) ? v : fallback;
    72	  }
    73	  function checked(el) { return !!(el && el.checked); }
    74	
    75	  // ═══════════ Fault injection ═══════════
    76	
    77	  function buildFaultInjections() {
    78	    const result = [];
    79	    document.querySelectorAll(".fan-fault-check:checked").forEach((cb) => {
    80	      const nodeId = cb.getAttribute("data-node");
    81	      const faultType = cb.getAttribute("data-fault");
    82	      if (nodeId && faultType) result.push({ node_id: nodeId, fault_type: faultType });
    83	    });
    84	    return result;
    85	  }
    86	
    87	  function renderFaultPanel() {
    88	    const active = buildFaultInjections();
    89	    if (readouts.faultCount) {
    90	      readouts.faultCount.textContent = active.length > 0 ? `${active.length} 故障激活` : "0 故障";
    91	      readouts.faultCount.dataset.active = active.length > 0 ? "true" : "false";
    92	    }
    93	    if (readouts.faultActiveList) {
    94	      readouts.faultActiveList.textContent = active.length > 0
    95	        ? active.map((f) => `${f.node_id}:${f.fault_type}`).join("  ·  ")
    96	        : "";
    97	    }
    98	    // Highlight active rows
    99	    document.querySelectorAll(".fan-fault-row").forEach((row) => {
   100	      const cb = row.querySelector(".fan-fault-check");
   101	      row.dataset.active = cb && cb.checked ? "true" : "false";
   102	    });
   103	  }
   104	
   105	  // ═══════════ Request builder ═══════════
   106	
   107	  function buildRequest() {
   108	    // E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
   109	    // manual_override_signoff when feedback_mode = manual_feedback_override.
   110	    //
   111	    // ⚠ CANNED DEMO DATA — NOT REAL AUTHENTICATION. The values below are a
   112	    // hardcoded test-harness sign-off so the demo flow keeps working under
   113	    // the new server guard. Server today validates only field shape +
   114	    // actor↔signed_by binding + ticket cross-binding; replay/nonce/freshness
   115	    // hardening is E11-16 scope. Do NOT show these strings to customers as
   116	    // proof of authentication. Real sign-off via Approval Center post-E11-08.
   117	    return {
   118	      tra_deg:                  numValue(inputs.tra, 0),
   119	      radio_altitude_ft:        numValue(inputs.ra, 0),
   120	      n1k:                      numValue(inputs.n1k, 0.35) / 100,
   121	      engine_running:           checked(inputs.engineRunning),
   122	      aircraft_on_ground:       checked(inputs.aircraftOnGround),
   123	      reverser_inhibited:       checked(inputs.reverserInhibited),
   124	      eec_enable:               checked(inputs.eecEnable),
   125	      feedback_mode:            "manual_feedback_override",
   126	      actor:                    "Kogami",
   127	      ticket_id:                "WB-DEMO",
   128	      manual_override_signoff:  {
   129	        signed_by: "Kogami",
   130	        signed_at: "2026-04-25T00:00:00Z",
   131	        ticket_id: "WB-DEMO",
   132	      },
   133	      deploy_position_percent:  numValue(inputs.vdt, 0),
   134	      fault_injections:         buildFaultInjections(),
   135	    };
   136	  }
   137	
   138	  function zoneFromTra(tra) {
   139	    if (tra <= -25) return ["rev-range", "MAX REV"];
   140	    if (tra <= -13) return ["rev-range", "DEEP REV"];
   141	    if (tra <= -9)  return ["rev-range", "REV"];
   142	    if (tra < 0)    return ["rev-idle", "REV IDLE"];
   143	    return ["fwd", "FWD"];
   144	  }
   145	
   146	  function formatBool(value) {
   147	    if (value === true)  return "TRUE";
   148	    if (value === false) return "false";
   149	    return "—";
   150	  }
   151	
   152	  // ═══════════ Fetch pipeline ═══════════
   153	  let pending = null;
   154	  let inflight = false;
   155	  let nextRequest = false;
   156	
   157	  async function fetchEvaluation() {
   158	    if (inflight) { nextRequest = true; return; }
   159	    inflight = true;
   160	    const payload = buildRequest();
   161	    try {
   162	      const response = await fetch(API_URL, {
   163	        method: "POST",
   164	        headers: { "Content-Type": "application/json" },
   165	        body: JSON.stringify(payload),
   166	      });
   167	      if (!response.ok) { console.warn("[demo] snapshot eval failed:", response.status); return; }
   168	      const data = await response.json();
   169	      renderAll(data, payload);
   170	    } catch (err) {
   171	      console.warn("[demo] fetch error:", err);
   172	    } finally {
   173	      inflight = false;
   174	      if (nextRequest) { nextRequest = false; fetchEvaluation(); }
   175	    }
   176	  }
   177	
   178	  function scheduleFetch() {
   179	    if (pending) clearTimeout(pending);
   180	    pending = setTimeout(() => { pending = null; fetchEvaluation(); }, DEBOUNCE_MS);
   181	  }
   182	
   183	  // ═══════════ Rendering ═══════════
   184	  function renderAll(data, request) {
   185	    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
   186	    const nodeById = new Map(nodes.map((n) => [n.id, n]));
   187	
   188	    renderLeverHud(request, data);
   189	    renderTraLock(data);
   190	    renderChain(nodeById);
   191	    renderOutputs(nodeById);
   192	    renderHud(nodeById);
   193	    renderStatus(data, nodeById);
   194	    renderFaultPanel();
   195	  }
   196	
   197	  function renderLeverHud(req, data) {
   198	    if (readouts.traValue) readouts.traValue.textContent = req.tra_deg.toFixed(1) + "°";
   199	    if (readouts.traZone) {
   200	      const [zone, label] = zoneFromTra(req.tra_deg);
   201	      readouts.traZone.dataset.zone = zone;
   202	      readouts.traZone.textContent = label;
   203	    }
   204	    if (readouts.raValue)  readouts.raValue.textContent  = req.radio_altitude_ft.toFixed(0) + " ft";
   205	    if (readouts.n1kValue) readouts.n1kValue.textContent = (req.n1k * 100).toFixed(0) + "%";
   206	    if (readouts.vdtValue) {
   207	      // Prefer the backend's echoed VDT from hud.deploy_position_percent; fall
   208	      // back to the request slider if the response is missing it for any reason.
   209	      const hudVdt = data && data.hud && typeof data.hud.deploy_position_percent === "number"
   210	        ? data.hud.deploy_position_percent
   211	        : req.deploy_position_percent;
   212	      readouts.vdtValue.textContent = hudVdt.toFixed(0) + "%";
   213	    }
   214	  }
   215	
   216	  // ═══════════ TRA=-14° lock rendering ═══════════
   217	
   218	  function renderTraLock(data) {
   219	    const lock = data.tra_lock;
   220	    if (!lock || typeof lock !== "object") return;
   221	
   222	    const locked    = Boolean(lock.locked);
   223	    const unlockMsg = lock.message || (
   224	      locked
   225	        ? "TRA 自由区 -14°~0°；满足 VDT≥90% (L4) 后才开放 -32°~-14° 深拉区。"
   226	        : "L4 已满足：TRA 深拉区 -32°~-14° 已开放，可继续向左推进。"
   227	    );
   228	    const effectiveTra = Number(lock.effective_tra_deg ?? numValue(inputs.tra, 0));
   229	
   230	    traLockActive = locked;
   231	
   232	    // Clamp slider value to effective (server may have clamped request)
   233	    if (inputs.tra && Math.abs(parseFloat(inputs.tra.value) - effectiveTra) > 0.1) {
   234	      inputs.tra.value = String(effectiveTra);
   235	      if (readouts.traValue) readouts.traValue.textContent = effectiveTra.toFixed(1) + "°";
   236	    }
   237	
   238	    if (readouts.traLockBadge) {
   239	      readouts.traLockBadge.textContent = locked ? "深拉区关闭" : "深拉区已开放";
   240	      readouts.traLockBadge.dataset.locked = locked ? "true" : "false";
   241	    }
   242	    if (readouts.traLockRange) {
   243	      const visualMin = Number(lock.visual_reverse_min_deg ?? -32);
   244	      const gateMin   = Number(lock.allowed_reverse_min_deg ?? TRA_LOCK_DEG);
   245	      readouts.traLockRange.textContent = locked
   246	        ? `条件深拉区 ${visualMin.toFixed(0)}°~${gateMin.toFixed(0)}°（关闭）`
   247	        : `条件深拉区 ${visualMin.toFixed(0)}°~${gateMin.toFixed(0)}°（已开放）`;
   248	      readouts.traLockRange.dataset.locked = locked ? "true" : "false";
   249	    }
   250	    if (readouts.traLockMsg) readouts.traLockMsg.textContent = unlockMsg;
   251	  }
   252	
   253	  // Guard slider drag past -14° while locked
   254	  function guardTraSlider() {
   255	    if (!inputs.tra) return;
   256	    const v = parseFloat(inputs.tra.value);
   257	    if (traLockActive && v < TRA_LOCK_DEG) {
   258	      inputs.tra.value = String(TRA_LOCK_DEG);
   259	    }
   260	  }
   261	
   262	  // ═══════════ Chain SVG: nodes + wires + junctions ═══════════
   263	
   264	  function nodeActive(nodeById, id) {
   265	    if (!id) return false;
   266	    const n = nodeById.get(id);
   267	    return n ? n.state === "active" : false;
   268	  }
   269	
   270	  function renderChain(nodeById) {
   271	    if (!chainSvg) return;
   272	
   273	    // 1. Node / logic block state
   274	    chainSvg.querySelectorAll(".chain-node, .chain-logic").forEach((group) => {
   275	      const nodeId = group.getAttribute("data-node");
   276	      const node = nodeById.get(nodeId);
   277	      group.dataset.state = node ? (node.state || "idle") : "idle";
   278	    });
   279	
   280	    // 2. Wire state coloring
   281	    chainSvg.querySelectorAll(".chain-wire").forEach((wire) => {
   282	      const src = wire.getAttribute("data-src");
   283	      const dst = wire.getAttribute("data-dst");
   284	      const isFault = wire.getAttribute("data-fault") === "true";
   285	      const srcActive = nodeActive(nodeById, src);
   286	      const dstActive = nodeActive(nodeById, dst);
   287	
   288	      let state = "idle";
   289	      if (isFault && srcActive)          state = "fault";
   290	      else if (srcActive && dstActive)   state = "active";
   291	      else if (srcActive)                state = "active";  // src lit → wire lit even if dst not yet
   292	
   293	      wire.dataset.state = state;
   294	      if (state === "active")      wire.setAttribute("marker-end", "url(#fan-arr-active)");
   295	      else if (state === "fault")  wire.setAttribute("marker-end", "url(#fan-arr-fault)");
   296	      else                         wire.setAttribute("marker-end", "url(#fan-arr-idle)");
   297	    });
   298	
   299	    // 3. Junction dots inherit src state; fault-bus junctions turn red when source is asserted
   300	    chainSvg.querySelectorAll(".chain-junction").forEach((dot) => {

 succeeded in 0ms:
   301	      const src = dot.getAttribute("data-src");
   302	      const isFault = dot.getAttribute("data-fault") === "true";
   303	      const srcActive = nodeActive(nodeById, src);
   304	      if (isFault && srcActive) dot.dataset.state = "fault";
   305	      else dot.dataset.state = srcActive ? "active" : "idle";
   306	    });
   307	  }
   308	
   309	  function renderOutputs(nodeById) {
   310	    setOutputCard(readouts.outTls115, readouts.outTls115V, nodeById.get("tls115"));
   311	    setOutputCard(readouts.outEtrac,  readouts.outEtracV,  nodeById.get("etrac_540v"));
   312	    setOutputCard(readouts.outEec,    readouts.outEecV,    nodeById.get("eec_deploy"));
   313	    setOutputCard(readouts.outThr,    readouts.outThrV,    nodeById.get("thr_lock"));
   314	  }
   315	
   316	  function setOutputCard(card, valueEl, node) {
   317	    if (!card || !valueEl) return;
   318	    const state = node ? node.state : "idle";
   319	    card.dataset.state = state === "active" ? "active" : (state === "blocked" ? "blocked" : "idle");
   320	    valueEl.textContent = state === "active" ? "ON" : (state === "blocked" ? "BLOCKED" : "OFF");
   321	  }
   322	
   323	  function renderHud(nodeById) {
   324	    const sw1 = nodeById.get("sw1");
   325	    const sw2 = nodeById.get("sw2");
   326	    if (readouts.hudSw1) {
   327	      readouts.hudSw1.textContent = sw1 && sw1.state === "active" ? "CLOSED" : "open";
   328	      readouts.hudSw1.dataset.flag = sw1 && sw1.state === "active" ? "true" : "false";
   329	    }
   330	    if (readouts.hudSw2) {
   331	      readouts.hudSw2.textContent = sw2 && sw2.state === "active" ? "CLOSED" : "open";
   332	      readouts.hudSw2.dataset.flag = sw2 && sw2.state === "active" ? "true" : "false";
   333	    }
   334	    const tls = nodeById.get("tls_unlocked");
   335	    if (readouts.hudTls) {
   336	      readouts.hudTls.textContent = tls && tls.state === "active" ? "UNLOCKED" : "locked";
   337	      readouts.hudTls.dataset.flag = tls && tls.state === "active" ? "true" : "false";
   338	    }
   339	    const vdt90 = nodeById.get("vdt90");
   340	    if (readouts.hudVdt90) {
   341	      readouts.hudVdt90.textContent = vdt90 && vdt90.state === "active" ? "≥90%" : "pending";
   342	      readouts.hudVdt90.dataset.flag = vdt90 && vdt90.state === "active" ? "true" : "false";
   343	    }
   344	    if (readouts.hudLogic) {
   345	      const parts = ["logic1", "logic2", "logic3", "logic4"].map((id, i) => {
   346	        const n = nodeById.get(id);
   347	        const on = n && n.state === "active";
   348	        return `L${i+1}:${on ? "ON" : "—"}`;
   349	      });
   350	      readouts.hudLogic.textContent = parts.join(" · ");
   351	    }
   352	    const thr = nodeById.get("thr_lock");
   353	    if (readouts.hudThrLock) {
   354	      if (thr && thr.state === "active") {
   355	        readouts.hudThrLock.textContent = "RELEASED";
   356	        readouts.hudThrLock.dataset.flag = "true";
   357	      } else if (thr && thr.state === "blocked") {
   358	        readouts.hudThrLock.textContent = "BLOCKED";
   359	        readouts.hudThrLock.dataset.flag = "fault";
   360	      } else {
   361	        readouts.hudThrLock.textContent = "—";
   362	        readouts.hudThrLock.dataset.flag = "false";
   363	      }
   364	    }
   365	  }
   366	
   367	  function renderStatus(data, nodeById) {
   368	    const thr    = nodeById.get("thr_lock");
   369	    const logic4 = nodeById.get("logic4");
   370	    const logic3 = nodeById.get("logic3");
   371	    const inhibited = checked(inputs.reverserInhibited);
   372	    const faults    = buildFaultInjections();
   373	
   374	    let state = "idle";
   375	    let summary = "等待拉杆快照 …";
   376	    let reached = false;
   377	
   378	    if (faults.length > 0 && (thr ? thr.state !== "active" : true)) {
   379	      const names = faults.map((f) => `${f.node_id}:${f.fault_type}`).join(" + ");
   380	      if (thr && thr.state === "blocked") {
   381	        state = "fault";
   382	        summary = `故障注入激活 [${names}]：THR_LOCK 封锁。`;
   383	      } else {
   384	        state = "fault";
   385	        summary = `故障注入激活 [${names}]：链路降级。`;
   386	      }
   387	    } else if (inhibited) {
   388	      state = "fault";
   389	      summary = "反推被抑制 (reverser_inhibited=TRUE)：所有 deploy 链路阻塞。";
   390	    } else if (thr && thr.state === "active") {
   391	      state = "deployed";
   392	      summary = "L4 满足，THR_LOCK 释放。油门反向段解锁。";
   393	      reached = true;
   394	    } else if (logic4 && logic4.state === "blocked") {
   395	      state = "fault";
   396	      const blockers = (logic4.blockers || []).join(" / ") || "VDT90 / plant feedback";
   397	      summary = `L4 阻塞：${blockers}。`;
   398	    } else if (logic3 && logic3.state === "active") {
   399	      state = "deploying";
   400	      summary = "L3 激活：EEC deploy / PLS / PDU 通电。等待 VDT≥90% 解锁深拉区。";
   401	    } else if (nodeById.get("logic2") && nodeById.get("logic2").state === "active") {
   402	      state = "ready";
   403	      summary = "L2 激活：ETRAC 540VDC 已供电，等待 L3 条件。";
   404	    } else if (nodeById.get("logic1") && nodeById.get("logic1").state === "active") {
   405	      state = "ready";
   406	      summary = "L1 激活：TLS 115VAC 已供电。等待 L2 条件（SW2 + engine_running + TLS 解锁）。";
   407	    } else {
   408	      state = "idle";
   409	      summary = traLockActive
   410	        ? "TRA 在自由区（-14°~0°）；拉到 -14° 后等待 VDT≥90% 才能进入深拉区。"
   411	        : "等待输入：TRA / RA / aircraft_on_ground 未满足 L1 前置条件。";
   412	    }
   413	
   414	    if (readouts.statusBadge) {
   415	      readouts.statusBadge.dataset.state = state;
   416	      readouts.statusBadge.textContent = ({
   417	        idle: "IDLE", ready: "READY", deploying: "DEPLOYING",
   418	        deployed: "DEPLOYED", stowing: "STOWING", fault: "FAULT",
   419	      })[state] || "IDLE";
   420	    }
   421	    if (readouts.statusSummary) readouts.statusSummary.textContent = summary;
   422	    if (readouts.completionFlag) {
   423	      readouts.completionFlag.textContent = reached ? "已达成" : "未达成";
   424	      readouts.completionFlag.dataset.reached = reached ? "true" : "false";
   425	    }
   426	  }
   427	
   428	  // ═══════════ Scenario presets ═══════════
   429	  const presets = {
   430	    "nominal-fwd": {
   431	      label: "默认前向",
   432	      apply: () => {
   433	        setSlider(inputs.tra, 0);
   434	        setSlider(inputs.ra, 100);
   435	        setSlider(inputs.n1k, 35);
   436	        setSlider(inputs.vdt, 0);
   437	        setChecked(inputs.engineRunning, true);
   438	        setChecked(inputs.aircraftOnGround, false);
   439	        setChecked(inputs.reverserInhibited, false);
   440	        setChecked(inputs.eecEnable, true);
   441	        clearAllFaults();
   442	      },
   443	    },
   444	    "landing-deploy": {
   445	      label: "着陆展开全链路",
   446	      apply: () => {
   447	        presets["nominal-fwd"].apply();
   448	        setSlider(inputs.tra, -26);
   449	        setSlider(inputs.ra, 2);
   450	        setSlider(inputs.n1k, 70);
   451	        // VDT=0 at preset load: L1 (!DEP) + L2 + L3 all active, L4 waiting
   452	        // for VDT90. Drag VDT up to watch L1 correctly release (!DEP flips
   453	        // false after deployment) and L4 fire — the true deployment cycle.
   454	        setSlider(inputs.vdt, 0);
   455	        setChecked(inputs.aircraftOnGround, true);
   456	      },
   457	    },
   458	    "max-reverse": {
   459	      label: "最大反推（展开到位）",
   460	      apply: () => {
   461	        presets["landing-deploy"].apply();
   462	        // TRA=-32 is the mechanical stop and is inclusive in the L4 range
   463	        // [-32, 0), so L4 correctly engages at the slider's leftmost value.
   464	        setSlider(inputs.tra, -32);
   465	        setSlider(inputs.n1k, 80);
   466	        // VDT=100 shows the POST-deploy state: L4 active / THR_LOCK released.
   467	        // L1 correctly drops to blocked because `!DEP` flipped — L1 has
   468	        // already done its job and no longer asserts TLS unlock.
   469	        setSlider(inputs.vdt, 100);
   470	      },
   471	    },
   472	    "stow-return": {
   473	      label: "收起回杆",
   474	      apply: () => {
   475	        presets["nominal-fwd"].apply();
   476	        setSlider(inputs.tra, 0);
   477	        setSlider(inputs.ra, 2);
   478	        setSlider(inputs.n1k, 25);
   479	        setSlider(inputs.vdt, 30);
   480	        setChecked(inputs.aircraftOnGround, true);
   481	      },
   482	    },
   483	    "inhibit-block": {
   484	      label: "抑制位阻塞",
   485	      apply: () => {
   486	        presets["landing-deploy"].apply();
   487	        setChecked(inputs.reverserInhibited, true);
   488	      },
   489	    },
   490	  };
   491	
   492	  function setSlider(el, value) { if (el) el.value = String(value); }
   493	  function setChecked(el, value) { if (el) el.checked = !!value; }
   494	  function setSelect(el, value) { if (el) el.value = value; }
   495	
   496	  function clearAllFaults() {
   497	    document.querySelectorAll(".fan-fault-check").forEach((cb) => { cb.checked = false; });
   498	    renderFaultPanel();
   499	  }
   500	
   501	  function applyPreset(key) {
   502	    const preset = presets[key];
   503	    if (!preset) return;
   504	    preset.apply();
   505	    if (readouts.presetStatus) readouts.presetStatus.textContent = "当前场景：" + preset.label;
   506	    document.querySelectorAll(".fan-preset-btn").forEach((btn) => {
   507	      btn.setAttribute("aria-pressed", btn.dataset.preset === key ? "true" : "false");
   508	    });
   509	    fetchEvaluation();
   510	  }
   511	
   512	  // ═══════════ Wire listeners ═══════════
   513	  function installListeners() {
   514	    Object.values(inputs).forEach((el) => {
   515	      if (!el) return;
   516	      const evt = (el.type === "checkbox" || el.tagName === "SELECT") ? "change" : "input";
   517	      el.addEventListener(evt, scheduleFetch);
   518	    });
   519	
   520	    // TRA slider: guard deep-range while locked
   521	    if (inputs.tra) {
   522	      inputs.tra.addEventListener("input", guardTraSlider);
   523	    }
   524	
   525	    document.querySelectorAll(".fan-preset-btn").forEach((btn) => {
   526	      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
   527	    });
   528	
   529	    // Fault injection checkboxes
   530	    document.querySelectorAll(".fan-fault-check").forEach((cb) => {
   531	      cb.addEventListener("change", () => { renderFaultPanel(); scheduleFetch(); });
   532	    });
   533	
   534	    const clearBtn = $("fan-fault-clear");
   535	    if (clearBtn) clearBtn.addEventListener("click", () => { clearAllFaults(); scheduleFetch(); });
   536	  }
   537	
   538	  function boot() {
   539	    installListeners();
   540	    fetchEvaluation();
   541	  }
   542	
   543	  if (document.readyState === "loading") {
   544	    document.addEventListener("DOMContentLoaded", boot);
   545	  } else {
   546	    boot();
   547	  }
   548	})();

 succeeded in 0ms:
   441	}
   442	
   443	// ── state ───────────────────────────────────────────
   444	let simRunning=false, simTimer=null, tickCount=0;
   445	
   446	function toggleSim(){
   447	  simRunning=!simRunning;
   448	  const btn=$('btnPlay'), dot=$('simDot');
   449	  if(simRunning){
   450	    dot.classList.add('running');btn.textContent='⏸ 暂停';btn.classList.add('active');
   451	    simTimer=setInterval(doTick,100);
   452	  } else {
   453	    dot.classList.remove('running');btn.textContent='▶ 仿真';btn.classList.remove('active');
   454	    clearInterval(simTimer);
   455	  }
   456	}
   457	
   458	async function resetSim(){
   459	  if(simRunning) toggleSim();
   460	  tickCount=0;
   461	  $('logBody').innerHTML='';
   462	  $('logCount').textContent='0 ticks';
   463	  $('tscCount').textContent='0 samples';
   464	  if(chart) chart.clear();
   465	  $('vdt_inj').value=0; $('v_vdt_inj').textContent='0.0%';
   466	  await fetch('/api/fantui/reset',{method:'POST'});
   467	  doTick();
   468	}
   469	
   470	function sync(){ if(!simRunning) doTick(); }
   471	
   472	async function doTick(){
   473	  try{
   474	    const r = await fetch('/api/fantui/tick',{
   475	      method:'POST',
   476	      headers:{'Content-Type':'application/json'},
   477	      body: JSON.stringify(buildPayload()),
   478	    });
   479	    if(!r.ok){ const err=await r.json().catch(()=>({})); console.warn('tick err',err); return; }
   480	    const d = await r.json();
   481	    updateUI(d);
   482	  }catch(e){ console.warn(e); }
   483	}
   484	
   485	function setGate(id,v){
   486	  const el=$('gate_'+id);el.className='gate-card '+(v?'on':'off');
   487	  $('gv_'+id).textContent=v?'TRUE':'FALSE';
   488	}
   489	function setCmd(id,v){
   490	  const el=$('cmd_'+id);el.className='cmd-row '+(v?'on':'off');
   491	  $('cv_'+id).textContent=v?'ON':'OFF';
   492	}
   493	function setArc(arcId,txtId,val,max,unit,color,fmt){
   494	  const len=110, pct=Math.min(Math.max(val/max,0),1);
   495	  const dash=pct*len;
   496	  $(arcId).setAttribute('stroke-dasharray',dash+','+(len-dash+200));
   497	  $(arcId).setAttribute('stroke',pct>0.9?'#f87171':color);
   498	  $(txtId).textContent=(fmt||((v)=>v.toFixed(0)+unit))(val);
   499	}
   500	
   501	function updateUI(d){
   502	  $('hTime').textContent='T: '+(d.t_s||0).toFixed(2)+'s';
   503	  $('v_sw1').textContent=d.sw1?'1':'0';
   504	  $('v_sw2').textContent=d.sw2?'1':'0';
   505	  setGate('l1',d.logic1_active);
   506	  setGate('l2',d.logic2_active);
   507	  setGate('l3',d.logic3_active);
   508	  setGate('l4',d.logic4_active);
   509	  setCmd('tls',d.tls_115vac_cmd);
   510	  setCmd('etrac',d.etrac_540vdc_cmd);
   511	  setCmd('eec',d.eec_deploy_cmd);
   512	  setCmd('pls',d.pls_power_cmd);
   513	  setCmd('pdu',d.pdu_motor_cmd);
   514	  setCmd('thr',d.throttle_electronic_lock_release_cmd);
   515	  setArc('gVdtArc','gVdtTxt',d.deploy_position_percent||0,100,'%','#b69dff');
   516	  setArc('gTraArc','gTraTxt',d.tra_deg||0,32,'°','#f5a623',
   517	    (v)=>v.toFixed(1)+'°');
   518	  $('v_pos').textContent=(d.deploy_position_percent||0).toFixed(1)+'%';
   519	  // Plant drive-condition readout for pedagogical transparency
   520	  const driveOn = d.etrac_540vdc_cmd && d.pdu_motor_cmd && d.pls_power_cmd && d.tls_unlocked_ls && d.all_pls_unlocked_ls;
   521	  $('v_drive').textContent = driveOn ? 'ARMED' : _whyNotDriving(d);
   522	  $('v_tlsu').textContent=d.tls_unlocked_ls?'YES':'NO';
   523	  $('v_plsu').textContent=d.all_pls_unlocked_ls?'YES':'NO';
   524	  $('v_vdt90').textContent=d.deploy_90_percent_vdt?'YES':'NO';
   525	  appendLog(d);
   526	
   527	  const drawer=$('tscDrawer');
   528	  if(drawer && drawer.classList.contains('open')){
   529	    const now=Date.now();
   530	    if(now-_lastChartUpdate>400){ _lastChartUpdate=now; refreshChart(); }
   531	  }
   532	}
   533	
   534	function _whyNotDriving(d){
   535	  if(!d.etrac_540vdc_cmd) return 'ETRAC off (L2 blocked)';
   536	  if(!d.pdu_motor_cmd || !d.pls_power_cmd) return 'L3 blocked';
   537	  if(!d.tls_unlocked_ls) return 'TLS 未解锁';
   538	  if(!d.all_pls_unlocked_ls) return 'PLS 未解锁';
   539	  return '–';
   540	}
   541	
   542	// ── log ─────────────────────────────────────────────
   543	const logLines=[];
   544	function appendLog(d){
   545	  tickCount++;
   546	  $('logCount').textContent=tickCount+' ticks';
   547	  const gates='L'+(d.logic1_active?'1':'·')+(d.logic2_active?'2':'·')+(d.logic3_active?'3':'·')+(d.logic4_active?'4':'·');
   548	  const cls = d.logic4_active ? 'active' : (d.logic3_active||d.logic1_active ? 'armed' : '');
   549	  const line=`<span class="log-line ${cls}">[${(d.t_s||0).toFixed(2).padStart(7)}s] ${gates} TRA=${(d.tra_deg||0).toFixed(1)}° VDT=${(d.deploy_position_percent||0).toFixed(0)}% SW=${d.sw1?1:0}${d.sw2?1:0} TLS=${d.tls_unlocked_ls?'U':'L'}</span>`;
   550	  logLines.push(line);
   551	  if(logLines.length>40) logLines.shift();
   552	  const lb=$('logBody');
   553	  lb.innerHTML=logLines.join('\n');
   554	  lb.scrollTop=lb.scrollHeight;
   555	}
   556	
   557	// ── Chart ──────────────────────────────────────────
   558	const FANTUI_LANES = ['INPUT','LOGIC','POWER','SENSOR','CMD'];
   559	const FANTUI_SERIES_DEFS = [
   560	  {lane:'INPUT', id:'ra',  label:'RA',  color:'#ff6f91', unit:'ft',  display_min:0, display_max:50,  field:'radio_altitude_ft'},
   561	  {lane:'INPUT', id:'tra', label:'TRA', color:'#ffaa33', unit:'°',   display_min:-32, display_max:2,  field:'tra_deg'},
   562	  {lane:'LOGIC', id:'sw1', label:'SW1', color:'#28f4ff', field:'sw1'},
   563	  {lane:'LOGIC', id:'sw2', label:'SW2', color:'#86d9ff', field:'sw2'},
   564	  {lane:'LOGIC', id:'l1',  label:'L1',  color:'#34d4ff', field:'logic1_active'},
   565	  {lane:'LOGIC', id:'l2',  label:'L2',  color:'#5de0ff', field:'logic2_active'},
   566	  {lane:'LOGIC', id:'l3',  label:'L3',  color:'#7de8ff', field:'logic3_active'},
   567	  {lane:'LOGIC', id:'l4',  label:'L4',  color:'#b0f1ff', field:'logic4_active'},
   568	  {lane:'POWER', id:'tls', label:'TLS', color:'#7dff9a', field:'tls_115vac_cmd'},
   569	  {lane:'POWER', id:'et',  label:'ETRAC',color:'#86ffbf',field:'etrac_540vdc_cmd'},
   570	  {lane:'POWER', id:'pls', label:'PLS', color:'#b6ffd0', field:'pls_power_cmd'},
   571	  {lane:'SENSOR',id:'vdt', label:'VDT', color:'#b69dff', unit:'%', display_min:0, display_max:100, field:'deploy_position_percent'},
   572	  {lane:'SENSOR',id:'tlsu',label:'TLS↑',color:'#d5c3ff', field:'tls_unlocked_ls'},
   573	  {lane:'CMD',   id:'eec', label:'EEC', color:'#ffd65c', field:'eec_deploy_cmd'},
   574	  {lane:'CMD',   id:'pdu', label:'PDU', color:'#ffc48a', field:'pdu_motor_cmd'},
   575	  {lane:'CMD',   id:'thr', label:'THR_LOCK', color:'#ff8c7a', field:'throttle_electronic_lock_release_cmd'},
   576	];
   577	const FANTUI_LANE_SERIES = {};
   578	FANTUI_SERIES_DEFS.forEach(d=>{(FANTUI_LANE_SERIES[d.lane] ||= []).push(d.id);});
   579	
   580	let chart=null, _lastChartUpdate=0;
   581	function ensureChart(){
   582	  if(chart) return chart;
   583	  const svg=$('tsc-svg'), legend=$('tsc-legend');
   584	  if(!svg||!window.TimeseriesChart) return null;
   585	  chart = TimeseriesChart.create({
   586	    svg, legend, width:1100, height:240,
   587	    laneLabels: FANTUI_LANES, laneSeries: FANTUI_LANE_SERIES,
   588	  });
   589	  return chart;
   590	}
   591	async function refreshChart(){
   592	  const c = ensureChart(); if(!c) return;
   593	  try{
   594	    const r = await fetch('/api/fantui/log');
   595	    if(!r.ok) return;
   596	    const recs = await r.json();
   597	    const payload = TimeseriesChart.buildPayload(recs, FANTUI_SERIES_DEFS);
   598	    c.setData(payload);
   599	    $('tscCount').textContent = recs.length + ' samples';
   600	  }catch(e){}
   601	}
   602	function toggleChart(){
   603	  const dr=$('tscDrawer'), b=$('btnChart');
   604	  const open=!dr.classList.contains('open');
   605	  dr.classList.toggle('open',open);
   606	  dr.setAttribute('aria-hidden', open?'false':'true');
   607	  b.classList.toggle('active',open);
   608	  if(open){ ensureChart(); initSeriesSelector(); refreshChart(); }
   609	}
   610	
   611	// ── Series selector ────────────────────────────────
   612	const _DEFAULT_VISIBLE_FAN = new Set(['ra','tra','sw1','l1','l2','l3','l4','vdt']);
   613	let _selectorInited = false;
   614	
   615	function initSeriesSelector(){
   616	  if(_selectorInited) return;
   617	  _selectorInited = true;
   618	  const panel = $('tscSelectorPanel');
   619	  if(!panel) return;
   620	  FANTUI_SERIES_DEFS.forEach(def=>{
   621	    const lbl = document.createElement('label');
   622	    lbl.className = 'tsc-sel-item';
   623	    lbl.title = def.lane + (def.unit ? ' · ' + def.unit : ' · bool');
   624	    const cb = document.createElement('input');
   625	    cb.type = 'checkbox';
   626	    cb.dataset.seriesId = def.id;
   627	    cb.checked = _DEFAULT_VISIBLE_FAN.has(def.id);
   628	    cb.addEventListener('change', onSelectorChange);
   629	    const sw = document.createElement('span');
   630	    sw.className = 'tsc-sel-swatch';
   631	    sw.style.background = def.color || '#6a7d95';
   632	    lbl.appendChild(cb);
   633	    lbl.appendChild(sw);
   634	    lbl.appendChild(document.createTextNode(def.label + ' [' + def.lane + ']'));
   635	    panel.appendChild(lbl);
   636	  });
   637	  onSelectorChange();
   638	}
   639	
   640	function _getSelectedIds(){
   641	  return Array.from(document.querySelectorAll('#tscSelectorPanel input[type=checkbox]'))
   642	    .filter(c=>c.checked).map(c=>c.dataset.seriesId);
   643	}
   644	function onSelectorChange(){
   645	  if(!chart) return;
   646	  const ids = _getSelectedIds();
   647	  chart.setVisibleSeries(ids.length === FANTUI_SERIES_DEFS.length ? null : ids);
   648	  const summary = $('tscSelectorSummary');
   649	  if(summary) summary.textContent = '选择信号 (' + ids.length + '/' + FANTUI_SERIES_DEFS.length + ') ▾';
   650	}
   651	function selectAllSeries(){
   652	  document.querySelectorAll('#tscSelectorPanel input[type=checkbox]').forEach(c=>{c.checked=true;});
   653	  onSelectorChange();
   654	}
   655	function clearAllSeries(){
   656	  document.querySelectorAll('#tscSelectorPanel input[type=checkbox]').forEach(c=>{c.checked=false;});
   657	  onSelectorChange();
   658	}
   659	
   660	// ── presets ────────────────────────────────────────
   661	const PRESETS = {
   662	  air:       {ra:20, tra:0,   engineRunning:false, onGround:false, inhibit:false, eec:true, n1k:0,  n1klim:85},
   663	  ground_idle:{ra:4,tra:0,    engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:45, n1klim:85},
   664	  arm_sw1:   {ra:4, tra:-3,   engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:55, n1klim:85},
   665	  arm_sw2:   {ra:4, tra:-8,   engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:55, n1klim:85},
   666	  deploy:    {ra:4, tra:-15,  engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:60, n1klim:85},
   667	  full_rev:  {ra:4, tra:-28,  engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:70, n1klim:85},
   668	  pull_back: {ra:4, tra:0,    engineRunning:true,  onGround:true,  inhibit:false, eec:true, n1k:50, n1klim:85},
   669	  inhibit:   {ra:4, tra:-15,  engineRunning:true,  onGround:true,  inhibit:true,  eec:true, n1k:60, n1klim:85},
   670	};
   671	function loadPreset(key){
   672	  const p=PRESETS[key]; if(!p) return;
   673	  const setV=(id,v)=>{const el=$(id); if(!el) return; if(typeof v==='boolean') el.checked=v; else el.value=v;};
   674	  Object.entries(p).forEach(([k,v])=>setV(k,v));
   675	  syncRa();syncTra();syncN1k();syncN1kLim();
   676	  sync();
   677	}
   678	
   679	// ── boot ───────────────────────────────────────────
   680	(async()=>{
   681	  try{ await fetch('/api/fantui/reset',{method:'POST'}); }catch(e){}
   682	  syncRa();syncTra();syncN1k();syncN1kLim();
   683	  doTick();
   684	})();
   685	</script>
   686	</body>
   687	</html>

exec
/bin/zsh -lc "nl -ba src/well_harness/static/adversarial_test.py | sed -n '1,326p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""Adversarial test for well-harness truth engine + UI state reliability.
     3	
     4	Tests against the backend API directly to validate truth engine logic,
     5	then checks the frontend's applySnapshotToCanvas behavior.
     6	"""
     7	import http.client
     8	import json
     9	import os
    10	import time
    11	import sys
    12	
    13	PORT = int(os.environ.get("WELL_HARNESS_PORT", "8766"))
    14	
    15	# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
    16	# manual_override_signoff when feedback_mode = manual_feedback_override.
    17	# The api() helper auto-injects a fixed sign-off triplet for any payload
    18	# using manual_feedback_override so the truth-engine resilience tests (which
    19	# exercise the override path) keep working under the new server guard.
    20	# Tests of the guard itself live in tests/test_lever_snapshot_manual_override_guard.py.
    21	#
    22	# ⚠ CANNED ADVERSARIAL-TEST FIXTURE — NOT REAL AUTHENTICATION. These are
    23	# placeholder strings that make adversarial probes well-formed; they do not
    24	# represent any signed approval. Replay/nonce/freshness checks are E11-16.
    25	MANUAL_OVERRIDE_SIGNOFF = {
    26	    "actor": "AdversarialBot",
    27	    "ticket_id": "WB-ADVERSARIAL",
    28	    "manual_override_signoff": {
    29	        "signed_by": "AdversarialBot",
    30	        "signed_at": "2026-04-25T00:00:00Z",
    31	        "ticket_id": "WB-ADVERSARIAL",
    32	    },
    33	}
    34	
    35	
    36	def api(path, payload):
    37	    if isinstance(payload, dict) and payload.get("feedback_mode") == "manual_feedback_override":
    38	        # Auto-attach sign-off fields; explicit fields in the original payload
    39	        # take precedence so a test can still assert 409 by overriding actor=""
    40	        # or similar.
    41	        merged = {**MANUAL_OVERRIDE_SIGNOFF, **payload}
    42	        payload = merged
    43	    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    44	    conn.request("POST", path, body=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    45	    resp = conn.getresponse()
    46	    data = json.loads(resp.read().decode())
    47	    conn.close()
    48	    return data
    49	
    50	def node_map(snap):
    51	    return {n["id"]: {"state": n["state"], "value": n.get("value")} for n in snap.get("nodes", [])}
    52	
    53	def logic_map(snap):
    54	    return {k: v.get("active", False) for k, v in snap.get("logic", {}).items()}
    55	
    56	def check(label, condition, msg=""):
    57	    if condition:
    58	        print(f"  PASS  {label}")
    59	        return True
    60	    else:
    61	        print(f"  FAIL  {label}" + (f" — {msg}" if msg else ""))
    62	        return False
    63	
    64	def run():
    65	    print("=" * 70)
    66	    print("ADVERSARIAL TEST: truth engine + UI state reliability")
    67	    print("=" * 70)
    68	
    69	    failures = 0
    70	
    71	    # ── Test 1: All logic gates active (baseline full-chain) ──────────────
    72	    print("\n[Test 1] Full chain activation (all conditions satisfied)")
    73	    snap = api("/api/lever-snapshot", {
    74	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
    75	        "engine_running": True, "aircraft_on_ground": True,
    76	        "reverser_inhibited": False, "eec_enable": True,
    77	        "n1k": 50.0, "sw1": True, "sw2": True,
    78	        "deploy_position_percent": 95.0,
    79	        "feedback_mode": "manual_feedback_override",
    80	        "system_id": "thrust-reverser", "prompt": "baseline"
    81	    })
    82	    nm = node_map(snap)
    83	    lm = logic_map(snap)
    84	
    85	    expected = {
    86	        "sw1": "active", "logic1": "blocked", "tls115": "active", "tls_unlocked": "active",
    87	        "sw2": "active", "logic2": "active", "etrac_540v": "active",
    88	        "logic3": "active",
    89	        "eec_deploy": "active", "pls_power": "active", "pdu_motor": "active",
    90	        "logic4": "active", "thr_lock": "active", "vdt90": "active",
    91	    }
    92	    for node_id, exp_state in expected.items():
    93	        actual = nm.get(node_id, {}).get("state", "MISSING")
    94	        if not check(f"{node_id}={actual} (expected {exp_state})", actual == exp_state):
    95	            failures += 1
    96	
    97	    if len(nm) != 19:
    98	        print(f"  FAIL  node count={len(nm)} (expected 19)")
    99	        failures += 1
   100	    else:
   101	        print(f"  PASS  node count=19")
   102	
   103	    # ── Test 2: Idempotency ──────────────────────────────────────────────────
   104	    print("\n[Test 2] Idempotency: same payload x5 produces identical output")
   105	    base_payload = {
   106	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   107	        "engine_running": True, "aircraft_on_ground": True,
   108	        "reverser_inhibited": False, "eec_enable": True,
   109	        "n1k": 50.0, "sw1": True, "sw2": True,
   110	        "deploy_position_percent": 95.0,
   111	        "feedback_mode": "manual_feedback_override",
   112	        "system_id": "thrust-reverser", "prompt": "idempotent"
   113	    }
   114	    outputs = [api("/api/lever-snapshot", base_payload) for _ in range(5)]
   115	    snapshots_identical = all(
   116	        node_map(o) == node_map(outputs[0]) and logic_map(o) == logic_map(outputs[0])
   117	        for o in outputs[1:]
   118	    )
   119	    if not check("5 identical outputs", snapshots_identical):
   120	        failures += 1
   121	
   122	    # ── Test 3: Stepwise deactivation (no spurious activations) ───────────
   123	    print("\n[Test 3] Stepwise deactivation (no spurious activations)")
   124	    snap0 = api("/api/lever-snapshot", {
   125	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   126	        "engine_running": True, "aircraft_on_ground": True,
   127	        "reverser_inhibited": False, "eec_enable": True,
   128	        "n1k": 50.0, "sw1": True, "sw2": True,
   129	        "deploy_position_percent": 95.0,
   130	        "feedback_mode": "manual_feedback_override",
   131	        "system_id": "thrust-reverser", "prompt": "full"
   132	    })
   133	    nm0 = node_map(snap0)
   134	
   135	    # Remove sw1 → only L1 chain should break
   136	    snap1 = api("/api/lever-snapshot", {
   137	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   138	        "engine_running": True, "aircraft_on_ground": True,
   139	        "reverser_inhibited": False, "eec_enable": True,
   140	        "n1k": 50.0, "sw1": False, "sw2": True,
   141	        "deploy_position_percent": 95.0,
   142	        "feedback_mode": "manual_feedback_override",
   143	        "system_id": "thrust-reverser", "prompt": "no_sw1"
   144	    })
   145	    nm1 = node_map(snap1)
   146	
   147	    newly_active = [k for k, v in nm1.items()
   148	                    if v["state"] == "active" and nm0.get(k, {}).get("state") != "active"]
   149	    if not check("no spurious activations when sw1 removed", len(newly_active) == 0,
   150	                 f"newly active: {newly_active}"):
   151	        failures += 1
   152	
   153	    # Remove sw2 too
   154	    snap2 = api("/api/lever-snapshot", {
   155	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   156	        "engine_running": True, "aircraft_on_ground": True,
   157	        "reverser_inhibited": False, "eec_enable": True,
   158	        "n1k": 50.0, "sw1": False, "sw2": False,
   159	        "deploy_position_percent": 95.0,
   160	        "feedback_mode": "manual_feedback_override",
   161	        "system_id": "thrust-reverser", "prompt": "no_sw1_sw2"
   162	    })
   163	    nm2 = node_map(snap2)
   164	    newly_active2 = [k for k, v in nm2.items()
   165	                      if v["state"] == "active" and nm0.get(k, {}).get("state") != "active"]
   166	    if not check("no spurious activations when sw1+sw2 removed", len(newly_active2) == 0,
   167	                 f"newly active: {newly_active2}"):
   168	        failures += 1
   169	
   170	    # ── Test 4: TRA boundary ─────────────────────────────────────────────────
   171	    print("\n[Test 4] TRA boundary conditions")
   172	    tra_cases = [
   173	        (-14.0, "logic3", "active", "exact threshold"),
   174	        (-11.7, "logic3", "blocked", "just above threshold"),
   175	        (0.0, "logic3", "blocked", "positive TRA"),
   176	        (-32.0, "logic3", "active", "below min travel"),
   177	    ]
   178	    for tra_val, node_id, exp_state, desc in tra_cases:
   179	        snap_t = api("/api/lever-snapshot", {
   180	            "tra_deg": tra_val, "radio_altitude_ft": 5.0,
   181	            "engine_running": True, "aircraft_on_ground": True,
   182	            "reverser_inhibited": False, "eec_enable": True,
   183	            "n1k": 50.0, "sw1": True, "sw2": True,
   184	            "deploy_position_percent": 95.0,
   185	            "feedback_mode": "manual_feedback_override",
   186	            "system_id": "thrust-reverser", "prompt": f"tra={tra_val}"
   187	        })
   188	        actual = node_map(snap_t).get(node_id, {}).get("state", "MISSING")
   189	        if not check(f"TRA={tra_val}deg {node_id}={actual} ({desc})",
   190	                      actual == exp_state, f"expected={exp_state}"):
   191	            failures += 1
   192	
   193	    # ── Test 5: VDT threshold at 90% ───────────────────────────────────────
   194	    print("\n[Test 5] VDT 90% threshold")
   195	    vdt_cases = [
   196	        (95.0, "vdt90", "active"),
   197	        (90.0, "vdt90", "active"),
   198	        (89.9, "vdt90", "inactive"),
   199	        (50.0, "vdt90", "inactive"),
   200	    ]
   201	    for vdt, node_id, exp_state in vdt_cases:
   202	        snap_v = api("/api/lever-snapshot", {
   203	            "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   204	            "engine_running": True, "aircraft_on_ground": True,
   205	            "reverser_inhibited": False, "eec_enable": True,
   206	            "n1k": 50.0, "sw1": True, "sw2": True,
   207	            "deploy_position_percent": vdt,
   208	            "feedback_mode": "manual_feedback_override",
   209	            "system_id": "thrust-reverser", "prompt": f"vdt={vdt}"
   210	        })
   211	        actual = node_map(snap_v).get(node_id, {}).get("state", "MISSING")
   212	        if not check(f"VDT={vdt}% {node_id}={actual}", actual == exp_state):
   213	            failures += 1
   214	
   215	    # ── Test 6: Rapid cycling (10 iterations) ────────────────────────────────
   216	    print("\n[Test 6] Rapid cycling (10 iterations, stress test)")
   217	    configs = [
   218	        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   219	        {"tra_deg": -10.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 50.0},
   220	        {"tra_deg": -14.0, "n1k": 70.0, "sw1": True, "sw2": False, "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   221	        {"tra_deg": 0.0,   "n1k": 50.0, "sw1": False,"sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   222	        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": False, "deploy_position_percent": 95.0},
   223	        {"tra_deg": -13.5, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 90.0},
   224	        {"tra_deg": -14.0, "n1k": 30.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   225	        {"tra_deg": -11.5, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   226	        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 89.9},
   227	        {"tra_deg": -14.0, "n1k": 55.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
   228	    ]
   229	    iter_failures = 0
   230	    for i, cfg in enumerate(configs):
   231	        p = {
   232	            "tra_deg": cfg["tra_deg"], "radio_altitude_ft": 5.0,
   233	            "engine_running": True, "aircraft_on_ground": cfg["aircraft_on_ground"],
   234	            "reverser_inhibited": False, "eec_enable": True,
   235	            "n1k": cfg["n1k"], "sw1": cfg["sw1"], "sw2": cfg["sw2"],
   236	            "deploy_position_percent": cfg["deploy_position_percent"],
   237	            "feedback_mode": "manual_feedback_override",
   238	            "system_id": "thrust-reverser", "prompt": f"iter{i}"
   239	        }
   240	        snap_i = api("/api/lever-snapshot", p)
   241	        nm_i = node_map(snap_i)
   242	
   243	        if len(nm_i) != 19:
   244	            print(f"  FAIL  iter{i}: node count={len(nm_i)} (expected 19)")
   245	            iter_failures += 1
   246	        for node_id, data in nm_i.items():
   247	            if data["state"] not in ("active", "inactive", "blocked"):
   248	                print(f"  FAIL  iter{i} {node_id}: invalid state={data['state']}")
   249	                iter_failures += 1
   250	        # Logic node state must be consistent with node state
   251	        for logic_id in ("logic1", "logic2", "logic3", "logic4"):
   252	            node_state = nm_i.get(logic_id, {}).get("state", "?")
   253	            logic_active = logic_map(snap_i).get(logic_id, False)
   254	            consistent = (logic_active and node_state == "active") or (not logic_active and node_state != "active")
   255	            if not consistent:
   256	                print(f"  FAIL  iter{i} {logic_id}: logic_active={logic_active} but node_state={node_state}")
   257	                iter_failures += 1
   258	
   259	    if iter_failures == 0:
   260	        print(f"  PASS  all 10 iterations consistent")
   261	    else:
   262	        print(f"  FAIL  {iter_failures} inconsistencies across 10 iterations")
   263	        failures += iter_failures
   264	
   265	    # ── Test 7: Frontend state application via nodeStateMap ─────────────────
   266	    # The fix: frontend now uses data.nodes[].state directly (nodeStateMap) instead of
   267	    # deriving from nodeValueMap via deriveComponentState(undefined)=inactive.
   268	    # Backend still doesn't provide .value for intermediate nodes — that's OK now.
   269	    print("\n[Test 7] Frontend uses authoritative nodeStateMap (not deriveComponentState)")
   270	    snap = api("/api/lever-snapshot", {
   271	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   272	        "engine_running": True, "aircraft_on_ground": True,
   273	        "reverser_inhibited": False, "eec_enable": True,
   274	        "n1k": 50.0, "sw1": True, "sw2": True,
   275	        "deploy_position_percent": 95.0,
   276	        "feedback_mode": "manual_feedback_override",
   277	        "system_id": "thrust-reverser", "prompt": "frontend_test"
   278	    })
   279	    # Verify backend provides authoritative state for ALL 14 nodes (including intermediate).
   280	    # This is the contract: data.nodes[].state must be the source of truth.
   281	    all_nodes_have_state = all("state" in n for n in snap.get("nodes", []))
   282	    intermediate_states = {n["id"]: n["state"] for n in snap.get("nodes", []) if n["id"] in ("tls115", "etrac_540v", "vdt90", "thr_lock")}
   283	    if not all_nodes_have_state:
   284	        print(f"  FAIL  Some nodes lack .state field in backend response")
   285	        failures += 1
   286	    elif not check("all 19 nodes have authoritative .state", all_nodes_have_state):
   287	        failures += 1
   288	    else:
   289	        print(f"  PASS  all 19 nodes have authoritative .state in backend")
   290	        print(f"  intermediate node states: {intermediate_states}")
   291	
   292	    # ── Test 8: Full causal chain ──────────────────────────────────────────
   293	    print("\n[Test 8] Full causal chain verification")
   294	    snap = api("/api/lever-snapshot", {
   295	        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
   296	        "engine_running": True, "aircraft_on_ground": True,
   297	        "reverser_inhibited": False, "eec_enable": True,
   298	        "n1k": 50.0, "sw1": True, "sw2": True,
   299	        "deploy_position_percent": 95.0,
   300	        "feedback_mode": "manual_feedback_override",
   301	        "system_id": "thrust-reverser", "prompt": "chain"
   302	    })
   303	    nm = node_map(snap)
   304	    chain = [
   305	        ("sw1", "active"), ("logic1", "blocked"), ("tls115", "active"), ("tls_unlocked", "active"),
   306	        ("sw2", "active"), ("logic2", "active"), ("etrac_540v", "active"),
   307	        ("logic3", "active"),
   308	        ("eec_deploy", "active"), ("pls_power", "active"), ("pdu_motor", "active"),
   309	        ("vdt90", "active"), ("logic4", "active"), ("thr_lock", "active"),
   310	    ]
   311	    for node_id, exp_state in chain:
   312	        actual = nm.get(node_id, {}).get("state", "MISSING")
   313	        if not check(f"{node_id}={actual}", actual == exp_state):
   314	            failures += 1
   315	
   316	    # ── Summary ──────────────────────────────────────────────────────────────
   317	    print("\n" + "=" * 70)
   318	    if failures == 0:
   319	        print("ALL TESTS PASSED")
   320	    else:
   321	        print(f"TESTS COMPLETED — {failures} failure(s)")
   322	    print("=" * 70)
   323	    return failures
   324	
   325	if __name__ == "__main__":
   326	    sys.exit(run())

exec
/bin/zsh -lc "nl -ba tests/conftest.py | sed -n '1,200p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""测试辅助：C919 E-TRAS Frozen V1.0 单元/集成测试共用 fixtures。"""
     2	from __future__ import annotations
     3	
     4	import sys
     5	from pathlib import Path
     6	
     7	import pytest
     8	
     9	_SRC = Path(__file__).resolve().parents[1] / "src"
    10	if str(_SRC) not in sys.path:
    11	    sys.path.insert(0, str(_SRC))
    12	
    13	from well_harness.adapters.c919_etras_frozen_v1 import LockInputs, RawInputs
    14	
    15	
    16	# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
    17	# manual_override_signoff when feedback_mode = manual_feedback_override.
    18	# Tests that exercise the override path (not the guard itself) use this
    19	# helper to extend their request payload with a fixed sign-off triplet.
    20	# Tests of the guard itself (negative cases) live in
    21	# tests/test_lever_snapshot_manual_override_guard.py.
    22	#
    23	# ⚠ CANNED TEST FIXTURE — NOT REAL AUTHENTICATION. signed_by/ticket_id are
    24	# placeholder strings that satisfy the structural guard. Replay/nonce/
    25	# freshness checks are E11-16 scope.
    26	MANUAL_OVERRIDE_SIGNOFF = {
    27	    "actor": "TestSuite",
    28	    "ticket_id": "WB-TEST",
    29	    "manual_override_signoff": {
    30	        "signed_by": "TestSuite",
    31	        "signed_at": "2026-04-25T00:00:00Z",
    32	        "ticket_id": "WB-TEST",
    33	    },
    34	}
    35	
    36	
    37	def with_signoff_if_manual_override(payload: dict) -> dict:
    38	    """Return payload with sign-off attached when feedback_mode = manual_feedback_override.
    39	
    40	    Existing fields in payload take precedence (so a test setting actor=""
    41	    can still produce a 409 when intentionally exercising the guard).
    42	    """
    43	    if isinstance(payload, dict) and payload.get("feedback_mode") == "manual_feedback_override":
    44	        return {**MANUAL_OVERRIDE_SIGNOFF, **payload}
    45	    return payload
    46	
    47	
    48	def make_locks(
    49	    *,
    50	    tls: str = "locked",
    51	    pl_l: str = "locked",
    52	    pl_r: str = "locked",
    53	    pls_l: str = "locked",
    54	    pls_r: str = "locked",
    55	) -> LockInputs:
    56	    def pair(s: str):
    57	        if s == "locked":
    58	            return (True, False)
    59	        if s == "unlocked":
    60	            return (False, True)
    61	        return (False, False)
    62	
    63	    tl, tu = pair(tls)
    64	    l_l, l_u = pair(pl_l)
    65	    r_l, r_u = pair(pl_r)
    66	    pl_ll, pl_lu = pair(pls_l)
    67	    pl_rl, pl_ru = pair(pls_r)
    68	    return LockInputs(
    69	        tls_locked=tl, tls_unlocked=tu,
    70	        pylon_lock_l_locked=l_l, pylon_lock_l_unlocked=l_u,
    71	        pylon_lock_r_locked=r_l, pylon_lock_r_unlocked=r_u,
    72	        pls_l_locked=pl_ll, pls_l_unlocked=pl_lu,
    73	        pls_r_locked=pl_rl, pls_r_unlocked=pl_ru,
    74	    )
    75	
    76	
    77	def make_inputs(**overrides) -> RawInputs:
    78	    defaults = dict(
    79	        lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
    80	        lgcu1_valid=True, lgcu2_valid=True,
    81	        tra_deg=0.0,
    82	        atltla=False, apwtla=False,
    83	        tr_inhibited=False,
    84	        engine_running=True,
    85	        trcu_menu_mode=False,
    86	        maintenance_cycle_on_going=False,
    87	        tr_position_pct=0.0,
    88	        n1k_pct=50.0,
    89	        max_n1k_deploy_limit_pct=84.0,
    90	        max_n1k_stow_limit_pct=72.0,
    91	        etras_over_temp_fault=False,
    92	        locks=make_locks(),
    93	    )
    94	    defaults.update(overrides)
    95	    return RawInputs(**defaults)
    96	
    97	
    98	@pytest.fixture
    99	def inputs_factory():
   100	    return make_inputs
   101	
   102	
   103	@pytest.fixture
   104	def locks_factory():
   105	    return make_locks

exec
/bin/zsh -lc "nl -ba tests/test_lever_snapshot_manual_override_guard.py | sed -n '1,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-14 — server-side role guard for manual_feedback_override.
     2	
     3	Locks the contract: /api/lever-snapshot requires actor + ticket_id +
     4	manual_override_signoff when feedback_mode = manual_feedback_override.
     5	Returns 409 Conflict when any are missing/malformed; auto_scrubber path
     6	is unaffected.
     7	
     8	Per E11-00-PLAN §3 row E11-14: this is the second line of defense paired
     9	with E11-13's UI affordance. Truth-engine red line maintained — no
    10	controller/runner/models/adapters changes.
    11	"""
    12	
    13	from __future__ import annotations
    14	
    15	import http.client
    16	import json
    17	import threading
    18	from http.server import ThreadingHTTPServer
    19	
    20	import pytest
    21	
    22	from well_harness.demo_server import DemoRequestHandler
    23	
    24	
    25	VALID_BASE_PAYLOAD = {
    26	    "tra_deg": -14.0,
    27	    "radio_altitude_ft": 5.0,
    28	    "n1k": 0.5,
    29	    "engine_running": True,
    30	    "aircraft_on_ground": True,
    31	    "reverser_inhibited": False,
    32	    "eec_enable": True,
    33	    "deploy_position_percent": 95.0,
    34	}
    35	
    36	VALID_SIGNOFF = {
    37	    "actor": "TestActor",
    38	    "ticket_id": "WB-TEST-1",
    39	    "manual_override_signoff": {
    40	        "signed_by": "TestActor",
    41	        "signed_at": "2026-04-25T12:00:00Z",
    42	        "ticket_id": "WB-TEST-1",
    43	    },
    44	}
    45	
    46	
    47	def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    48	    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    49	    thread = threading.Thread(target=server.serve_forever, daemon=True)
    50	    thread.start()
    51	    return server, thread
    52	
    53	
    54	def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
    55	    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    56	    connection.request(
    57	        "POST",
    58	        path,
    59	        body=json.dumps(payload).encode("utf-8"),
    60	        headers={"Content-Type": "application/json"},
    61	    )
    62	    response = connection.getresponse()
    63	    body = json.loads(response.read().decode("utf-8") or "{}")
    64	    return response.status, body
    65	
    66	
    67	@pytest.fixture
    68	def server():
    69	    s, t = _start_demo_server()
    70	    try:
    71	        yield s
    72	    finally:
    73	        s.shutdown()
    74	        s.server_close()
    75	        t.join(timeout=2)
    76	
    77	
    78	def test_auto_scrubber_unaffected_by_guard(server) -> None:
    79	    """auto_scrubber path: no actor/ticket required, returns 200."""
    80	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "auto_scrubber"}
    81	    status, body = _post(server, "/api/lever-snapshot", payload)
    82	    assert status == 200, f"auto_scrubber should bypass guard, got {status}: {body}"
    83	    assert "nodes" in body
    84	
    85	
    86	def test_manual_override_with_valid_signoff_returns_200(server) -> None:
    87	    """manual_feedback_override + valid sign-off triplet → 200."""
    88	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override", **VALID_SIGNOFF}
    89	    status, body = _post(server, "/api/lever-snapshot", payload)
    90	    assert status == 200, f"valid sign-off should pass guard, got {status}: {body}"
    91	
    92	
    93	def test_manual_override_missing_actor_returns_409(server) -> None:
    94	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    95	    payload.update(VALID_SIGNOFF)
    96	    payload["actor"] = ""
    97	    status, body = _post(server, "/api/lever-snapshot", payload)
    98	    assert status == 409
    99	    assert body.get("error") == "manual_override_unsigned"
   100	    assert body.get("field") == "actor"
   101	
   102	
   103	def test_manual_override_missing_ticket_id_returns_409(server) -> None:
   104	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   105	    payload.update(VALID_SIGNOFF)
   106	    payload["ticket_id"] = ""
   107	    status, body = _post(server, "/api/lever-snapshot", payload)
   108	    assert status == 409
   109	    assert body.get("error") == "manual_override_unsigned"
   110	    assert body.get("field") == "ticket_id"
   111	
   112	
   113	def test_manual_override_missing_signoff_object_returns_409(server) -> None:
   114	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   115	    payload["actor"] = "TestActor"
   116	    payload["ticket_id"] = "WB-TEST-1"
   117	    # no manual_override_signoff key at all
   118	    status, body = _post(server, "/api/lever-snapshot", payload)
   119	    assert status == 409
   120	    assert body.get("error") == "manual_override_unsigned"
   121	    assert body.get("field") == "manual_override_signoff"
   122	
   123	
   124	def test_manual_override_signoff_missing_signed_by_returns_409(server) -> None:
   125	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   126	    payload.update(VALID_SIGNOFF)
   127	    payload["manual_override_signoff"] = {**VALID_SIGNOFF["manual_override_signoff"], "signed_by": ""}
   128	    status, body = _post(server, "/api/lever-snapshot", payload)
   129	    assert status == 409
   130	    assert body.get("field") == "manual_override_signoff.signed_by"
   131	
   132	
   133	def test_manual_override_signoff_ticket_mismatch_returns_409(server) -> None:
   134	    """signoff.ticket_id MUST equal request ticket_id; mismatch is rejected."""
   135	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   136	    payload.update(VALID_SIGNOFF)
   137	    payload["manual_override_signoff"] = {
   138	        **VALID_SIGNOFF["manual_override_signoff"],
   139	        "ticket_id": "WB-DIFFERENT",
   140	    }
   141	    status, body = _post(server, "/api/lever-snapshot", payload)
   142	    assert status == 409
   143	    assert body.get("field") == "manual_override_signoff.ticket_id"
   144	
   145	
   146	def test_remediation_message_present_on_409(server) -> None:
   147	    """409 response includes a remediation message pointing to Approval Center."""
   148	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   149	    status, body = _post(server, "/api/lever-snapshot", payload)
   150	    assert status == 409
   151	    assert "Approval Center" in body.get("remediation", "")
   152	    assert "auto_scrubber" in body.get("remediation", "")
   153	
   154	
   155	# ─── P2 R1 IMPORTANT #5: contract gap tests (R2 fixes) ───────────────────────
   156	
   157	
   158	def test_actor_signed_by_mismatch_returns_409(server) -> None:
   159	    """P2 BLOCKER #1 R2 fix: actor must equal manual_override_signoff.signed_by.
   160	
   161	    Without this binding, an attacker submits actor=Mallory + signed_by=Kogami
   162	    (matching ticket_id) and impersonates Kogami. Live-verified by P2 in R1.
   163	    """
   164	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   165	    payload.update(VALID_SIGNOFF)
   166	    payload["actor"] = "Mallory"  # different from signed_by="TestActor"
   167	    status, body = _post(server, "/api/lever-snapshot", payload)
   168	    assert status == 409
   169	    assert body.get("field") == "actor"
   170	    assert "impersonation" in body.get("message", "")
   171	
   172	
   173	def test_400_precedes_409_when_other_fields_malformed(server) -> None:
   174	    """P2 IMPORTANT #3 R2 fix: 400 (malformed) precedes 409 (unsigned).
   175	
   176	    A request with malformed deploy_position_percent + missing signoff used
   177	    to return 409 manual_override_unsigned (masking the real 400). After
   178	    R2 the guard runs after structural parsing; malformed numeric fields
   179	    surface as 400 first.
   180	    """
   181	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   182	    payload["deploy_position_percent"] = "oops"  # malformed
   183	    # signoff intentionally missing
   184	    status, body = _post(server, "/api/lever-snapshot", payload)
   185	    assert status == 400, (
   186	        f"Expected 400 for malformed payload (precedes 409), got {status}: {body}"
   187	    )
   188	    assert body.get("error") == "invalid_lever_snapshot_input"
   189	
   190	
   191	def test_residual_risk_disclosure_present_on_409(server) -> None:
   192	    """P2 IMPORTANT #4 R2 mitigation: 409 response discloses replay residual risk.
   193	
   194	    Replay/nonce/freshness hardening is deferred to E11-16. The guard
   195	    response must explicitly disclose this so callers don't mistake
   196	    structural validation for latched authorization.
   197	    """
   198	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   199	    status, body = _post(server, "/api/lever-snapshot", payload)
   200	    assert status == 409
   201	    risk = body.get("residual_risk", "")
   202	    assert "Replay" in risk or "replay" in risk
   203	    assert "E11-16" in risk
   204	
   205	
   206	def test_signoff_non_dict_returns_409(server) -> None:
   207	    """signoff field must be a dict; string/list/null all 409."""
   208	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   209	    payload["actor"] = "TestActor"
   210	    payload["ticket_id"] = "WB-TEST-1"
   211	    payload["manual_override_signoff"] = "not-a-dict"
   212	    status, body = _post(server, "/api/lever-snapshot", payload)
   213	    assert status == 409
   214	    assert body.get("field") == "manual_override_signoff"
   215	
   216	
   217	def test_signoff_signed_at_empty_returns_409(server) -> None:
   218	    """signed_at must be non-empty string. Note: freshness validation is
   219	    E11-16 scope; this only locks the structural non-empty check."""
   220	    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
   221	    payload.update(VALID_SIGNOFF)
   222	    payload["manual_override_signoff"] = {**VALID_SIGNOFF["manual_override_signoff"], "signed_at": ""}
   223	    status, body = _post(server, "/api/lever-snapshot", payload)
   224	    assert status == 409
   225	    assert body.get("field") == "manual_override_signoff.signed_at"
   226	
   227	
   228	# ─── P2 R1 BLOCKER #2 R2 fix: /api/fantui/set_vdt test-probe acknowledgment ──
   229	
   230	
   231	def test_set_vdt_requires_test_probe_acknowledgment(server) -> None:
   232	    """P2 BLOCKER #2 R2 fix: /api/fantui/set_vdt is a test probe; without
   233	    explicit test_probe_acknowledgment=true it returns 409 explaining the
   234	    bypass and pointing callers to /api/lever-snapshot for authoritative
   235	    manual feedback."""
   236	    status, body = _post(server, "/api/fantui/set_vdt", {"deploy_position_percent": 73})
   237	    assert status == 409
   238	    assert body.get("error") == "test_probe_unacknowledged"
   239	    assert "test probe" in body.get("message", "").lower()
   240	    assert "/api/lever-snapshot" in body.get("message", "")
   241	
   242	
   243	def test_set_vdt_with_acknowledgment_succeeds(server) -> None:
   244	    """When the caller acknowledges the bypass nature, set_vdt works as before."""
   245	    status, body = _post(
   246	        server,
   247	        "/api/fantui/set_vdt",
   248	        {"deploy_position_percent": 73, "test_probe_acknowledgment": True},
   249	    )
   250	    assert status == 200
   251	    assert body.get("deploy_position_percent") == pytest.approx(73, abs=0.01)

codex
The main server and test surfaces are read. One point I’m checking carefully now is whether the residual-risk disclosure really covers every intended 409 path, because the lever-snapshot guard and the `set_vdt` probe use separate 409 branches.
exec
/bin/zsh -lc 'git diff e85ffb4..75070ee -- src/well_harness/demo_server.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/demo_server.py b/src/well_harness/demo_server.py
index 0fdae98..2c6a0cc 100644
--- a/src/well_harness/demo_server.py
+++ b/src/well_harness/demo_server.py
@@ -354,6 +354,30 @@ class DemoRequestHandler(BaseHTTPRequestHandler):
             self._send_json(200, {"ok": True, "t_s": 0.0})
             return
         if parsed.path == FANTUI_SET_VDT_PATH:
+            # E11-14 R2 (P2 BLOCKER #2, 2026-04-25): set_vdt is a test probe
+            # that bypasses the /api/lever-snapshot sign-off contract. The
+            # endpoint stays available for the fan-console debug UI but now
+            # requires an explicit `test_probe_acknowledgment` field so a
+            # caller cannot accidentally use it to inject manual feedback
+            # while believing they're going through the authority chain.
+            # The 409 message explains the alternative (use /api/lever-snapshot
+            # with sign-off when authority semantics matter).
+            ack = request_payload.get("test_probe_acknowledgment")
+            if ack is not True:
+                self._send_json(
+                    409,
+                    {
+                        "error": "test_probe_unacknowledged",
+                        "message": (
+                            "/api/fantui/set_vdt is a test probe that bypasses the "
+                            "manual_feedback_override authority chain. To use it from "
+                            "tests/dev tooling, pass test_probe_acknowledgment=true. "
+                            "For authoritative manual feedback, use /api/lever-snapshot "
+                            "with feedback_mode=manual_feedback_override + sign-off."
+                        ),
+                    },
+                )
+                return
             try:
                 pct = float(request_payload.get("deploy_position_percent", 0))
             except (TypeError, ValueError):
@@ -651,6 +675,17 @@ def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str)
                 "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
                 "Acquire sign-off via Approval Center, or switch to auto_scrubber."
             ),
+            # E11-14 R2 (P2 IMPORTANT #4, 2026-04-25): residual risk disclosure.
+            # The current sign-off check is structural only — same triplet can
+            # authorize multiple override payloads (replay) and signed_at is
+            # not freshness-checked. One-shot latch / nonce / freshness is the
+            # E11-16 approval-endpoint hardening scope. Until E11-16 lands,
+            # this guard is "shape correct" not "latched authorization".
+            "residual_risk": (
+                "Sign-off is structural only. Replay across payloads is not blocked; "
+                "signed_at is not freshness-validated. One-shot latch + nonce + "
+                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
+            ),
         }
 
     if not isinstance(actor, str) or not actor.strip():
@@ -687,6 +722,17 @@ def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str)
             "manual_override_signoff.ticket_id must match the request's ticket_id.",
         )
 
+    # E11-14 R2 fix (P2 BLOCKER #1, 2026-04-25): actor must equal
+    # manual_override_signoff.signed_by. Without this binding, an attacker
+    # can submit `actor="Mallory"` with `signed_by="Kogami"` and the server
+    # would accept it (P2 verified via live probe). Bind requester identity
+    # to the signoff's signer.
+    if signed_by.strip() != actor.strip():
+        return reject(
+            "actor",
+            "actor must match manual_override_signoff.signed_by (impersonation guard).",
+        )
+
     return None
 
 
@@ -1088,11 +1134,11 @@ def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, di
         return None, error_payload
     lever_inputs["feedback_mode"] = feedback_mode
 
-    # E11-14: enforce server-side role guard on manual_feedback_override.
-    # No-op for auto_scrubber; returns 409 payload when signoff missing/invalid.
-    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
-    if signoff_error is not None:
-        return None, signoff_error
+    # E11-14 R1 had the guard here; moved to the END of structural parsing
+    # in R2 (P2 IMPORTANT #3, 2026-04-25): a malformed
+    # deploy_position_percent="oops" + missing signoff used to return 409
+    # manual_override_unsigned, masking the real 400. Authority guard now
+    # runs on otherwise-well-formed manual-override requests only.
 
     deploy_position_percent, error_payload = _parse_float_input(
         request_payload,
@@ -1137,6 +1183,15 @@ def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, di
             )
         if normalized_faults:
             lever_inputs["_fault_injections"] = normalized_faults
+
+    # E11-14 R2 (P2 IMPORTANT #3): authority guard runs AFTER structural
+    # parsing so 400 (malformed) precedes 409 (unsigned). No-op for
+    # auto_scrubber; returns 409 payload with `_status` hint when signoff
+    # missing/invalid for manual_feedback_override.
+    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
+    if signoff_error is not None:
+        return None, signoff_error
+
     return lever_inputs, None
 
 

exec
/bin/zsh -lc 'git diff e85ffb4..75070ee -- src/well_harness/static/fan_console.html src/well_harness/static/demo.js src/well_harness/static/adversarial_test.py tests/conftest.py tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/adversarial_test.py b/src/well_harness/static/adversarial_test.py
index 3d6892a..fe3d60d 100644
--- a/src/well_harness/static/adversarial_test.py
+++ b/src/well_harness/static/adversarial_test.py
@@ -18,6 +18,10 @@ PORT = int(os.environ.get("WELL_HARNESS_PORT", "8766"))
 # using manual_feedback_override so the truth-engine resilience tests (which
 # exercise the override path) keep working under the new server guard.
 # Tests of the guard itself live in tests/test_lever_snapshot_manual_override_guard.py.
+#
+# ⚠ CANNED ADVERSARIAL-TEST FIXTURE — NOT REAL AUTHENTICATION. These are
+# placeholder strings that make adversarial probes well-formed; they do not
+# represent any signed approval. Replay/nonce/freshness checks are E11-16.
 MANUAL_OVERRIDE_SIGNOFF = {
     "actor": "AdversarialBot",
     "ticket_id": "WB-ADVERSARIAL",
diff --git a/src/well_harness/static/demo.js b/src/well_harness/static/demo.js
index f7881a3..74028d7 100644
--- a/src/well_harness/static/demo.js
+++ b/src/well_harness/static/demo.js
@@ -105,11 +105,15 @@
   // ═══════════ Request builder ═══════════
 
   function buildRequest() {
-    // E11-14 (2026-04-25): /api/lever-snapshot now requires actor + ticket_id +
+    // E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
     // manual_override_signoff when feedback_mode = manual_feedback_override.
-    // Demo flow ships canned sign-off matching the demo Approval Center exit
-    // state (Kogami signed WB-DEMO at deploy). Real UI will fill these from
-    // the sign-off ticket post-E11-08.
+    //
+    // ⚠ CANNED DEMO DATA — NOT REAL AUTHENTICATION. The values below are a
+    // hardcoded test-harness sign-off so the demo flow keeps working under
+    // the new server guard. Server today validates only field shape +
+    // actor↔signed_by binding + ticket cross-binding; replay/nonce/freshness
+    // hardening is E11-16 scope. Do NOT show these strings to customers as
+    // proof of authentication. Real sign-off via Approval Center post-E11-08.
     return {
       tra_deg:                  numValue(inputs.tra, 0),
       radio_altitude_ft:        numValue(inputs.ra, 0),
diff --git a/src/well_harness/static/fan_console.html b/src/well_harness/static/fan_console.html
index 518a274..cd76f35 100644
--- a/src/well_harness/static/fan_console.html
+++ b/src/well_harness/static/fan_console.html
@@ -416,7 +416,10 @@ function syncVdtInj(){
   fetch('/api/fantui/set_vdt',{
     method:'POST',
     headers:{'Content-Type':'application/json'},
-    body:JSON.stringify({deploy_position_percent:pct}),
+    // E11-14 R2: explicit test-probe acknowledgment (this UI is a debug
+    // console; for authoritative manual feedback, use /api/lever-snapshot
+    // with sign-off via the workbench Approval Center).
+    body:JSON.stringify({deploy_position_percent:pct,test_probe_acknowledgment:true}),
   }).then(r=>r.ok&&r.json()).then(snap=>{
     if(snap&&snap.deploy_position_percent!=null)
       $('v_pos').textContent=snap.deploy_position_percent.toFixed(1)+'%';
diff --git a/tests/conftest.py b/tests/conftest.py
index fadc2e1..13c5bd6 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -19,6 +19,10 @@ from well_harness.adapters.c919_etras_frozen_v1 import LockInputs, RawInputs
 # helper to extend their request payload with a fixed sign-off triplet.
 # Tests of the guard itself (negative cases) live in
 # tests/test_lever_snapshot_manual_override_guard.py.
+#
+# ⚠ CANNED TEST FIXTURE — NOT REAL AUTHENTICATION. signed_by/ticket_id are
+# placeholder strings that satisfy the structural guard. Replay/nonce/
+# freshness checks are E11-16 scope.
 MANUAL_OVERRIDE_SIGNOFF = {
     "actor": "TestSuite",
     "ticket_id": "WB-TEST",
diff --git a/tests/test_lever_snapshot_manual_override_guard.py b/tests/test_lever_snapshot_manual_override_guard.py
index 067fd85..e130a19 100644
--- a/tests/test_lever_snapshot_manual_override_guard.py
+++ b/tests/test_lever_snapshot_manual_override_guard.py
@@ -150,3 +150,102 @@ def test_remediation_message_present_on_409(server) -> None:
     assert status == 409
     assert "Approval Center" in body.get("remediation", "")
     assert "auto_scrubber" in body.get("remediation", "")
+
+
+# ─── P2 R1 IMPORTANT #5: contract gap tests (R2 fixes) ───────────────────────
+
+
+def test_actor_signed_by_mismatch_returns_409(server) -> None:
+    """P2 BLOCKER #1 R2 fix: actor must equal manual_override_signoff.signed_by.
+
+    Without this binding, an attacker submits actor=Mallory + signed_by=Kogami
+    (matching ticket_id) and impersonates Kogami. Live-verified by P2 in R1.
+    """
+    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
+    payload.update(VALID_SIGNOFF)
+    payload["actor"] = "Mallory"  # different from signed_by="TestActor"
+    status, body = _post(server, "/api/lever-snapshot", payload)
+    assert status == 409
+    assert body.get("field") == "actor"
+    assert "impersonation" in body.get("message", "")
+
+
+def test_400_precedes_409_when_other_fields_malformed(server) -> None:
+    """P2 IMPORTANT #3 R2 fix: 400 (malformed) precedes 409 (unsigned).
+
+    A request with malformed deploy_position_percent + missing signoff used
+    to return 409 manual_override_unsigned (masking the real 400). After
+    R2 the guard runs after structural parsing; malformed numeric fields
+    surface as 400 first.
+    """
+    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
+    payload["deploy_position_percent"] = "oops"  # malformed
+    # signoff intentionally missing
+    status, body = _post(server, "/api/lever-snapshot", payload)
+    assert status == 400, (
+        f"Expected 400 for malformed payload (precedes 409), got {status}: {body}"
+    )
+    assert body.get("error") == "invalid_lever_snapshot_input"
+
+
+def test_residual_risk_disclosure_present_on_409(server) -> None:
+    """P2 IMPORTANT #4 R2 mitigation: 409 response discloses replay residual risk.
+
+    Replay/nonce/freshness hardening is deferred to E11-16. The guard
+    response must explicitly disclose this so callers don't mistake
+    structural validation for latched authorization.
+    """
+    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
+    status, body = _post(server, "/api/lever-snapshot", payload)
+    assert status == 409
+    risk = body.get("residual_risk", "")
+    assert "Replay" in risk or "replay" in risk
+    assert "E11-16" in risk
+
+
+def test_signoff_non_dict_returns_409(server) -> None:
+    """signoff field must be a dict; string/list/null all 409."""
+    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
+    payload["actor"] = "TestActor"
+    payload["ticket_id"] = "WB-TEST-1"
+    payload["manual_override_signoff"] = "not-a-dict"
+    status, body = _post(server, "/api/lever-snapshot", payload)
+    assert status == 409
+    assert body.get("field") == "manual_override_signoff"
+
+
+def test_signoff_signed_at_empty_returns_409(server) -> None:
+    """signed_at must be non-empty string. Note: freshness validation is
+    E11-16 scope; this only locks the structural non-empty check."""
+    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
+    payload.update(VALID_SIGNOFF)
+    payload["manual_override_signoff"] = {**VALID_SIGNOFF["manual_override_signoff"], "signed_at": ""}
+    status, body = _post(server, "/api/lever-snapshot", payload)
+    assert status == 409
+    assert body.get("field") == "manual_override_signoff.signed_at"
+
+
+# ─── P2 R1 BLOCKER #2 R2 fix: /api/fantui/set_vdt test-probe acknowledgment ──
+
+
+def test_set_vdt_requires_test_probe_acknowledgment(server) -> None:
+    """P2 BLOCKER #2 R2 fix: /api/fantui/set_vdt is a test probe; without
+    explicit test_probe_acknowledgment=true it returns 409 explaining the
+    bypass and pointing callers to /api/lever-snapshot for authoritative
+    manual feedback."""
+    status, body = _post(server, "/api/fantui/set_vdt", {"deploy_position_percent": 73})
+    assert status == 409
+    assert body.get("error") == "test_probe_unacknowledged"
+    assert "test probe" in body.get("message", "").lower()
+    assert "/api/lever-snapshot" in body.get("message", "")
+
+
+def test_set_vdt_with_acknowledgment_succeeds(server) -> None:
+    """When the caller acknowledges the bypass nature, set_vdt works as before."""
+    status, body = _post(
+        server,
+        "/api/fantui/set_vdt",
+        {"deploy_position_percent": 73, "test_probe_acknowledgment": True},
+    )
+    assert status == 200
+    assert body.get("deploy_position_percent") == pytest.approx(73, abs=0.01)

codex
I’ve diffed R2 directly against R1. The only potential ambiguity left is semantic: whether “all 409 paths” for residual-risk disclosure was meant to cover only the manual-override signoff guard or also the unrelated `set_vdt` probe guard. I’m verifying runtime behavior now so the verdict is evidence-backed, not inferred.
exec
/bin/zsh -lc "PYTHONPATH=src python - <<'PY'
from well_harness.demo_server import _validate_manual_override_signoff
payload = {
  'feedback_mode':'manual_feedback_override',
  'actor':'Mallory',
  'ticket_id':'WB-TEST-1',
  'manual_override_signoff': {
    'signed_by':'TestActor',
    'signed_at':'2026-04-25T12:00:00Z',
    'ticket_id':'WB-TEST-1',
  }
}
print(_validate_manual_override_signoff(payload, 'manual_feedback_override'))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'PYTHONPATH=src pytest -q tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
codex
The environment doesn’t have `python`; it does have the interpreter behind `pytest`, so I’m switching the live probe to `python3`/server process and letting the targeted guard suite finish in parallel.
 succeeded in 7784ms:
...............                                                          [100%]
15 passed in 7.62s

exec
/bin/zsh -lc 'PYTHONPATH=src python3 src/well_harness/demo_server.py --host 127.0.0.1 --port 8766' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "curl -s -i -X POST http://127.0.0.1:8766/api/fantui/set_vdt -H 'Content-Type: application/json' --data '{\"deploy_position_percent\":73}'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "curl -s -i -X POST http://127.0.0.1:8766/api/lever-snapshot -H 'Content-Type: application/json' --data '{\"tra_deg\":-14.0,\"radio_altitude_ft\":5.0,\"n1k\":0.5,\"engine_running\":true,\"aircraft_on_ground\":true,\"reverser_inhibited\":false,\"eec_enable\":true,\"deploy_position_percent\":95.0,\"feedback_mode\":\"manual_feedback_override\",\"actor\":\"Mallory\",\"ticket_id\":\"WB-TEST-1\",\"manual_override_signoff\":{\"signed_by\":\"TestActor\",\"signed_at\":\"2026-04-25T12:00:00Z\",\"ticket_id\":\"WB-TEST-1\"}}'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
HTTP/1.0 409 Conflict
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 15:30:53 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 334
Cache-Control: no-store

{"error": "test_probe_unacknowledged", "message": "/api/fantui/set_vdt is a test probe that bypasses the manual_feedback_override authority chain. To use it from tests/dev tooling, pass test_probe_acknowledgment=true. For authoritative manual feedback, use /api/lever-snapshot with feedback_mode=manual_feedback_override + sign-off."}
 succeeded in 0ms:
HTTP/1.0 409 Conflict
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 15:30:53 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 529
Cache-Control: no-store

{"error": "manual_override_unsigned", "field": "actor", "message": "actor must match manual_override_signoff.signed_by (impersonation guard).", "remediation": "manual_feedback_override requires actor + ticket_id + manual_override_signoff. Acquire sign-off via Approval Center, or switch to auto_scrubber.", "residual_risk": "Sign-off is structural only. Replay across payloads is not blocked; signed_at is not freshness-validated. One-shot latch + nonce + server-issued approvals scoped to E11-16 (approval endpoint hardening)."}
exec
/bin/zsh -lc "curl -s -i -X POST http://127.0.0.1:8766/api/fantui/set_vdt -H 'Content-Type: application/json' --data '{\"deploy_position_percent\":73,\"test_probe_acknowledgment\":true}'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
HTTP/1.0 200 OK
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 15:30:53 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 118
Cache-Control: no-store

{"t_s": 0.0, "sw1": false, "sw2": false, "deploy_position_percent": 73.0, "tls_unlocked_ls": false, "sample_count": 0}
codex
I have the runtime evidence now. The signoff impersonation guard works live, the `set_vdt` bypass guard works live, and that same live probe also exposed the remaining gap: the `set_vdt` 409 path still omits the `residual_risk` disclosure that R2 claimed would be present on every 409 response.
codex
Using `gsd-code-review` for a findings-first re-review and `using-superpowers` to ensure the review workflow is applied before verdict.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '848,862p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "curl -s -i -X POST http://127.0.0.1:8766/api/lever-snapshot -H 'Content-Type: application/json' --data '{\"tra_deg\":-14.0,\"radio_altitude_ft\":5.0,\"n1k\":0.5,\"engine_running\":true,\"aircraft_on_ground\":true,\"reverser_inhibited\":false,\"eec_enable\":true,\"deploy_position_percent\":\"oops\",\"feedback_mode\":\"manual_feedback_override\"}'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
HTTP/1.0 400 Bad Request
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 15:31:39 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 132
Cache-Control: no-store

{"error": "invalid_lever_snapshot_input", "field": "deploy_position_percent", "message": "deploy_position_percent must be numeric."}
 succeeded in 63592ms:
^C
Stopping well-harness demo UI.

Inspection, targeted test run, and live probes are complete. One R1 finding remains open due to the missing residual-risk disclosure on the set_vdt 409 path.
  ✓ Inspect R2 target files and commit diff for server guard, UI warnings, and red-line boundary
  ✓ Verify each R1 finding against code paths and new tests
  ✓ Run at least one live probe against the demo server to confirm runtime behavior
  → Deliver verdict with CLOSED/OPEN/DEFERRED status per finding and any residual nits
codex
**CHANGES_REQUIRED**

1. IMPORTANT #4 OPEN — `residual_risk` is not on every 409 path. The manual-override reject helper adds it in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:668), but the new `/api/fantui/set_vdt` 409 branch in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365) returns only `error` and `message`. Live probe against the local server confirmed `POST /api/fantui/set_vdt {"deploy_position_percent":73}` returns `409 test_probe_unacknowledged` with no `residual_risk`. Since R2 acceptance claimed disclosure on every 409 response and asked for all 409 paths to be checked, this remains open.

**Status**
- BLOCKER #1 CLOSED — the actor/signer bind is now unconditional for `manual_feedback_override` at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:725). `actor != signed_by` rejects on `field=actor` with an impersonation message. Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:158) and confirmed live: `actor=Mallory`, `signed_by=TestActor` returned 409.
- BLOCKER #2 CLOSED — the `set_vdt` probe gate runs before numeric parsing and before `_FANTUI_SYSTEM.set_plant_position(...)` in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365). The debug UI now sends `test_probe_acknowledgment:true` in [fan_console.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/fan_console.html:416). Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:231) and [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:243), and confirmed live: no ack -> 409, ack -> 200 with `deploy_position_percent: 73.0`.
- IMPORTANT #3 CLOSED — signoff validation moved to the end of structural parsing in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1115) and now executes at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1191). Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:173) and confirmed live: malformed `deploy_position_percent:"oops"` returned 400 `invalid_lever_snapshot_input`, not 409.
- IMPORTANT #4 OPEN — partial only. `/api/lever-snapshot` 409s disclose the deferred replay/freshness gap, but `/api/fantui/set_vdt` 409 does not.
- IMPORTANT #5 CLOSED — the 7 added tests in [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:158) are non-redundant and map cleanly to the missing edges: actor/signer mismatch, 400-vs-409 precedence, residual-risk disclosure, non-dict signoff, empty `signed_at`, `set_vdt` unack, and `set_vdt` ack success. Targeted run: `15 passed in 7.62s`.
- NIT #6 CLOSED — canned-data warnings are present and explicit in [demo.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/demo.js:107), [adversarial_test.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/adversarial_test.py:22), and [conftest.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/conftest.py:23).

Truth-engine red line check: confirmed preserved. `git diff --name-only e85ffb4..75070ee -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters` returned no paths.

No new in-scope findings beyond R1 #4.

**P2 — Senior FCS Engineer (Tier-B, E11-14 R2)**


tokens used
163,324
**CHANGES_REQUIRED**

1. IMPORTANT #4 OPEN — `residual_risk` is not on every 409 path. The manual-override reject helper adds it in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:668), but the new `/api/fantui/set_vdt` 409 branch in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365) returns only `error` and `message`. Live probe against the local server confirmed `POST /api/fantui/set_vdt {"deploy_position_percent":73}` returns `409 test_probe_unacknowledged` with no `residual_risk`. Since R2 acceptance claimed disclosure on every 409 response and asked for all 409 paths to be checked, this remains open.

**Status**
- BLOCKER #1 CLOSED — the actor/signer bind is now unconditional for `manual_feedback_override` at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:725). `actor != signed_by` rejects on `field=actor` with an impersonation message. Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:158) and confirmed live: `actor=Mallory`, `signed_by=TestActor` returned 409.
- BLOCKER #2 CLOSED — the `set_vdt` probe gate runs before numeric parsing and before `_FANTUI_SYSTEM.set_plant_position(...)` in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365). The debug UI now sends `test_probe_acknowledgment:true` in [fan_console.html](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/fan_console.html:416). Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:231) and [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:243), and confirmed live: no ack -> 409, ack -> 200 with `deploy_position_percent: 73.0`.
- IMPORTANT #3 CLOSED — signoff validation moved to the end of structural parsing in [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1115) and now executes at [demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:1191). Covered by [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:173) and confirmed live: malformed `deploy_position_percent:"oops"` returned 400 `invalid_lever_snapshot_input`, not 409.
- IMPORTANT #4 OPEN — partial only. `/api/lever-snapshot` 409s disclose the deferred replay/freshness gap, but `/api/fantui/set_vdt` 409 does not.
- IMPORTANT #5 CLOSED — the 7 added tests in [test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:158) are non-redundant and map cleanly to the missing edges: actor/signer mismatch, 400-vs-409 precedence, residual-risk disclosure, non-dict signoff, empty `signed_at`, `set_vdt` unack, and `set_vdt` ack success. Targeted run: `15 passed in 7.62s`.
- NIT #6 CLOSED — canned-data warnings are present and explicit in [demo.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/demo.js:107), [adversarial_test.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/adversarial_test.py:22), and [conftest.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/conftest.py:23).

Truth-engine red line check: confirmed preserved. `git diff --name-only e85ffb4..75070ee -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters` returned no paths.

No new in-scope findings beyond R1 #4.

**P2 — Senior FCS Engineer (Tier-B, E11-14 R2)**


