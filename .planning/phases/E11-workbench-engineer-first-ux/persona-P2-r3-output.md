2026-04-25T15:37:13.532427Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T15:37:13.532503Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc549-ae3d-7543-9b3f-4a0d833f9874
--------
user
You are Codex GPT-5.4 acting as **Persona P2 — Senior FCS Engineer** (Tier-B rotation slot, E11-14 sub-phase, R3 closure check).

# Context — E11-14 R3 (single-finding closure)

You returned **CHANGES_REQUIRED** on E11-14 R2 (commit `75070ee`) with exactly 1 OPEN finding:

> **IMPORTANT #4 OPEN** — `residual_risk` is not on every 409 path. The manual-override reject helper adds it, but the new `/api/fantui/set_vdt` 409 branch returns only `error` and `message`. Live probe confirmed `POST /api/fantui/set_vdt {"deploy_position_percent":73}` returns `409 test_probe_unacknowledged` with no `residual_risk`.

R3 (commit `6a519bb`) addresses exactly this. Your job: confirm closure or identify residual issue.

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-14-manual-feedback-server-guard-20260425`
**PR:** #17
**Worktree HEAD:** `6a519bb` (R3 single fix on top of R2 `75070ee`)

# R3 fix (verify)

`src/well_harness/demo_server.py` `/api/fantui/set_vdt` 409 reject branch (around line 365–390): now includes a `residual_risk` field with the same disclosure pattern as the manual-override reject helper, explicitly stating:
- `test_probe_acknowledgment=true` is not authentication
- replay/nonce/freshness validation deferred to E11-16

`tests/test_lever_snapshot_manual_override_guard.py` `test_set_vdt_requires_test_probe_acknowledgment`: asserts `residual_risk` body field contains `E11-16` and `structural`/`authentication` keyword.

# What you should NOT raise

- R1/R2 findings already CLOSED (BLOCKER #1, BLOCKER #2, IMPORTANT #3, IMPORTANT #5, NIT #6) — re-open only if you find R3 introduced regression.
- E11-16 scope items (replay/nonce hardening, signed_at freshness, cryptographic envelope sign) — explicit out-of-scope.
- /workbench UI surfaces — E11-13/E11-15 scope.
- Any net-new BLOCKER not flowing from R3's 1-line code delta.

# Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

State explicitly: IMPORTANT #4 → CLOSED / OPEN.

Live-probe the set_vdt 409 path: `curl POST /api/fantui/set_vdt` without ack, observe response includes `residual_risk` containing "E11-16". Cite the probe.

Truth-engine red line: confirm no `controller.py`/`runner.py`/`models.py`/`adapters/` changes in `75070ee..6a519bb` (single-commit delta, easy verify).

Sign as: **P2 — Senior FCS Engineer (Tier-B, E11-14 R3)**
codex
Reviewing R3 as a closure check only. I’m loading the repo-specific memory note, then I’ll verify the single-commit delta, inspect the 409 branch/test, and live-probe the endpoint before issuing a verdict.
exec
/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|E11-14|manual-feedback|manual override|set_vdt" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'git status --short --branch' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
## feat/e11-14-manual-feedback-server-guard-20260425
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r2-prompt.txt
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r3-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P2-r3-prompt.txt

exec
/bin/zsh -lc 'git log --oneline --decorate -n 8' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
6a519bb (HEAD -> feat/e11-14-manual-feedback-server-guard-20260425) phase(E11-14): R3 fix for P2 R2 IMPORTANT #4 — residual_risk on set_vdt 409
75070ee phase(E11-14): R2 fixes for P2 Tier-B BLOCKER (impersonation, set_vdt bypass, 400-vs-409)
00adad7 phase(E11-14): Surface Inventory + PERSONA-ROTATION-STATE update (P2)
e85ffb4 phase(E11-14): manual_feedback_override server-side role guard
4d1200b (origin/main, origin/HEAD, main) docs(audit-trail): commit governance-bundle-2 Codex audit + E11-13 P1 R1/R2/R3 outputs + Notion sync
9fd2ef8 phase(E11-13): manual_feedback_override UI trust-affordance (PR #16)
f596933 docs(notion-sync): mirror PR #14 + PR #15 landing into coordination docs
a40cb30 constitution v2.4 + RETRO-V61-055 — Recursive Coherence Drift Mitigation (PR #15)

codex
Using `gsd-code-review` for a correctness-only pass because this is a closure review, not an implementation task. I’ve confirmed the branch head and the claimed single-fix commit; next I’m checking the exact diff and the targeted test before probing the live endpoint.
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
/bin/zsh -lc 'git diff 75070ee..6a519bb -- src/well_harness/demo_server.py tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/demo_server.py b/src/well_harness/demo_server.py
index 2c6a0cc..1285361 100644
--- a/src/well_harness/demo_server.py
+++ b/src/well_harness/demo_server.py
@@ -375,6 +375,17 @@ class DemoRequestHandler(BaseHTTPRequestHandler):
                             "For authoritative manual feedback, use /api/lever-snapshot "
                             "with feedback_mode=manual_feedback_override + sign-off."
                         ),
+                        # E11-14 R3 (P2 R2 IMPORTANT #4 fix, 2026-04-25): every 409
+                        # path must disclose the deferred replay/freshness gap so
+                        # callers don't mistake structural validation for latched
+                        # authorization. set_vdt's bypass nature is itself a live
+                        # residual risk surface.
+                        "residual_risk": (
+                            "Test-probe bypass remains structural; "
+                            "test_probe_acknowledgment=true is not authentication. "
+                            "Replay/nonce/freshness validation and one-shot latching are "
+                            "scoped to E11-16 (approval endpoint hardening)."
+                        ),
                     },
                 )
                 return
diff --git a/tests/test_lever_snapshot_manual_override_guard.py b/tests/test_lever_snapshot_manual_override_guard.py
index e130a19..d605882 100644
--- a/tests/test_lever_snapshot_manual_override_guard.py
+++ b/tests/test_lever_snapshot_manual_override_guard.py
@@ -238,6 +238,11 @@ def test_set_vdt_requires_test_probe_acknowledgment(server) -> None:
     assert body.get("error") == "test_probe_unacknowledged"
     assert "test probe" in body.get("message", "").lower()
     assert "/api/lever-snapshot" in body.get("message", "")
+    # P2 R2 IMPORTANT #4 R3 fix: every 409 path must disclose deferred
+    # replay/freshness scope (not just /api/lever-snapshot).
+    risk = body.get("residual_risk", "")
+    assert "E11-16" in risk
+    assert "structural" in risk.lower() or "authentication" in risk.lower()
 
 
 def test_set_vdt_with_acknowledgment_succeeds(server) -> None:

exec
/bin/zsh -lc "git diff --stat 75070ee..6a519bb && printf '\\n---\\n' && git diff --name-only 75070ee..6a519bb && printf '\\n---\\n' && git diff -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 src/well_harness/demo_server.py                    | 11 +++++++++++
 tests/test_lever_snapshot_manual_override_guard.py |  5 +++++
 2 files changed, 16 insertions(+)

---
src/well_harness/demo_server.py
tests/test_lever_snapshot_manual_override_guard.py

---

codex
The delta is exactly two files, with no truth-engine edits in `controller.py`, `runner.py`, `models.py`, or `adapters/`. I’m reading the surrounding handler code and test harness now so I can run the targeted test and a real HTTP probe against the correct local server path.
exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '340,410p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   406	            snapshot = request_payload.get("snapshot")
   407	            if not system_id:
   408	                self._send_json(400, {"error": "missing system_id"})
   409	                return
   410	            if not isinstance(snapshot, dict):

exec
/bin/zsh -lc "nl -ba tests/test_lever_snapshot_manual_override_guard.py | sed -n '220,260p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   241	    # P2 R2 IMPORTANT #4 R3 fix: every 409 path must disclose deferred
   242	    # replay/freshness scope (not just /api/lever-snapshot).
   243	    risk = body.get("residual_risk", "")
   244	    assert "E11-16" in risk
   245	    assert "structural" in risk.lower() or "authentication" in risk.lower()
   246	
   247	
   248	def test_set_vdt_with_acknowledgment_succeeds(server) -> None:
   249	    """When the caller acknowledges the bypass nature, set_vdt works as before."""
   250	    status, body = _post(
   251	        server,
   252	        "/api/fantui/set_vdt",
   253	        {"deploy_position_percent": 73, "test_probe_acknowledgment": True},
   254	    )
   255	    assert status == 200
   256	    assert body.get("deploy_position_percent") == pytest.approx(73, abs=0.01)

exec
/bin/zsh -lc 'rg -n "DemoRequestHandler|HTTPServer|serve_forever|demo_server|set_vdt|pytest|manual_override_guard" -S src tests pyproject.toml README*' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
pyproject.toml:11:# Runtime stays stdlib-only — demo_server.py imports no third-party packages.
pyproject.toml:17:# Covers the pytest default lane + the schema-validation scripts under tools/.
pyproject.toml:19:    "pytest>=8.0",
pyproject.toml:20:    "pytest-subtests>=0.11",
pyproject.toml:32:[tool.pytest.ini_options]
pyproject.toml:33:# Default CI lane excludes e2e; opt-in with: pytest -m e2e (or pytest -m "e2e or not e2e")
pyproject.toml:37:# Make bare `pytest` work without requiring PYTHONPATH=src:. on the caller:
pyproject.toml:42:    "e2e: opt-in end-to-end tests that boot demo_server on :8799 (run with -m e2e)",
README.md:42:- `src/well_harness/demo_server.py`
README.md:142:PYTHONPATH=src python3 -m well_harness.demo_server
README.md:146:If you want the server to ask the standard-library browser launcher to open the URL after startup, run `PYTHONPATH=src python3 -m well_harness.demo_server --open`; this is only a launch convenience, not browser E2E automation.
tests/test_workbench_start.py:16:the demo_server route table.
tests/test_workbench_start.py:25:from http.server import ThreadingHTTPServer
tests/test_workbench_start.py:29:import pytest
tests/test_workbench_start.py:31:from well_harness.demo_server import DemoRequestHandler
tests/test_workbench_start.py:82:def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
tests/test_workbench_start.py:83:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_workbench_start.py:84:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_workbench_start.py:89:@pytest.mark.parametrize("path", ["/workbench/start", "/workbench/start.html"])
tests/test_workbench_start.py:91:    server, thread = _start_demo_server()
tests/test_workbench_start.py:109:    server, thread = _start_demo_server()
tests/test_workbench_start.py:194:    server, thread = _start_demo_server()
tests/test_workbench_approval_center.py:4:import pytest
tests/test_workbench_approval_center.py:50:    with pytest.raises(WorkbenchPermissionError, match="Kogami"):
src/well_harness/demo_server.py:13:from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
src/well_harness/demo_server.py:104:FANTUI_SET_VDT_PATH = "/api/fantui/set_vdt"
src/well_harness/demo_server.py:200:class DemoRequestHandler(BaseHTTPRequestHandler):
src/well_harness/demo_server.py:357:            # E11-14 R2 (P2 BLOCKER #2, 2026-04-25): set_vdt is a test probe
src/well_harness/demo_server.py:372:                            "/api/fantui/set_vdt is a test probe that bypasses the "
src/well_harness/demo_server.py:381:                        # authorization. set_vdt's bypass nature is itself a live
src/well_harness/demo_server.py:2740:    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
src/well_harness/demo_server.py:2747:        server.serve_forever()
tests/test_provenance_sha_integrity.py:2:P40-03 · Provenance SHA integrity regression guard (pytest default lane).
tests/test_provenance_sha_integrity.py:4:Runs scripts/verify_provenance_hashes.py as part of the default pytest suite.
tests/test_provenance_sha_integrity.py:27:import pytest
tests/test_provenance_sha_integrity.py:65:        pytest.skip("uploads/ directory absent; nothing to register")
tests/test_workbench_dual_route.py:22:from http.server import ThreadingHTTPServer
tests/test_workbench_dual_route.py:25:import pytest
tests/test_workbench_dual_route.py:27:from well_harness.demo_server import DemoRequestHandler
tests/test_workbench_dual_route.py:34:def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
tests/test_workbench_dual_route.py:35:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_workbench_dual_route.py:36:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_workbench_dual_route.py:41:def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
tests/test_workbench_dual_route.py:49:@pytest.mark.parametrize("path", ["/workbench", "/workbench.html", "/expert/workbench.html"])
tests/test_workbench_dual_route.py:52:    server, thread = _start_demo_server()
tests/test_workbench_dual_route.py:72:@pytest.mark.parametrize("path", ["/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"])
tests/test_workbench_dual_route.py:75:    server, thread = _start_demo_server()
tests/test_p43_authority_contract.py:24:import pytest
tests/test_p43_authority_contract.py:29:_DSV  = _REPO / "src" / "well_harness" / "demo_server.py"
tests/test_p43_authority_contract.py:36:@pytest.fixture(scope="module")
tests/test_p43_authority_contract.py:42:@pytest.fixture(scope="module")
tests/test_p43_authority_contract.py:48:@pytest.fixture(scope="module")
tests/test_p43_authority_contract.py:50:    assert _DSV.exists(), f"demo_server.py missing: {_DSV}"
tests/test_p43_authority_contract.py:72:    def test_r1_demo_server_no_draft_key(self, dsv: str):
tests/test_p43_authority_contract.py:73:        """demo_server.py must never write draft_design_state."""
tests/test_p43_authority_contract.py:76:            f"R1 VIOLATION: demo_server.py references draft key at lines {hits}. "
src/well_harness/static/adversarial_test.py:20:# Tests of the guard itself live in tests/test_lever_snapshot_manual_override_guard.py.
tests/test_demo_fault_injection.py:4:from tests.test_demo import start_demo_server
tests/test_demo_fault_injection.py:21:        cls.server, cls.thread = start_demo_server()
src/well_harness/static/workbench.js:3021:      backendDetail.textContent = `最近 pitch_prewarm 请求的是 ${requestedBackendText} · ${requestedModelText}，但当前观察到的运行后端不是这套，需要先纠正 demo_server。`;
src/well_harness/static/workbench.js:3025:      backendDetail.textContent = "这是当前 demo_server 暴露出来的 explain 后端组合；它只是操作者运行观察值，不改变任何控制真值。";
src/well_harness/static/workbench.js:3036:    sourceDetail.textContent = "最近一次 explain 命中了预热缓存，说明 prewarm 生效；重启 demo_server 后需重新预热。";
src/well_harness/static/workbench.js:3049:    cacheDetail.textContent = `cached_at 上报为 ${runtime.cachedAt}${hitsPart}${expectedPart}。explain 缓存只在 demo_server 进程内有效，重启或换 backend 都会清空，需要重新预热。`;
src/well_harness/static/workbench.js:3063:    cacheDetail.textContent = "尚未看到 cached_at。若刚刚跑过 prewarm，请核对 demo_server 输出；否则这里会保持“待命”直到首次 explain 观察上报。";
tests/test_timeline_fantui.py:10:from http.server import HTTPServer
tests/test_timeline_fantui.py:13:from well_harness.demo_server import DemoRequestHandler
tests/test_timeline_fantui.py:27:    server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_timeline_fantui.py:28:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_archive_restore_sandbox.py:4:  Layer 1 (demo_server.py): manifest_path must resolve inside archive_root
tests/test_archive_restore_sandbox.py:16:from well_harness.demo_server import build_workbench_archive_restore_response, default_workbench_archive_root
tests/test_adapter_freeze_banner.py:23:import pytest
tests/test_adapter_freeze_banner.py:57:@pytest.mark.parametrize("relpath", ALL_FROZEN_FILES)
tests/test_adapter_freeze_banner.py:68:@pytest.mark.parametrize("relpath", ALL_FROZEN_FILES)
tests/test_demo.py:11:from http.server import ThreadingHTTPServer
tests/test_demo.py:15:from well_harness import demo_server
tests/test_demo.py:18:from well_harness.demo_server import DemoRequestHandler
tests/test_demo.py:72:def start_demo_server():
tests/test_demo.py:73:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_demo.py:74:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_demo.py:301:    def test_demo_server_api_returns_demo_json_payload(self):
tests/test_demo.py:302:        server, thread = start_demo_server()
tests/test_demo.py:329:    def test_demo_server_api_missing_prompt_returns_readable_error_json(self):
tests/test_demo.py:330:        server, thread = start_demo_server()
tests/test_demo.py:350:    def test_demo_server_api_returns_lever_snapshot_payload_for_key_tra_values(self):
tests/test_demo.py:378:        server, thread = start_demo_server()
tests/test_demo.py:419:    def test_demo_server_api_accepts_extended_lever_snapshot_conditions(self):
tests/test_demo.py:465:        server, thread = start_demo_server()
tests/test_demo.py:493:    def test_demo_server_api_accepts_manual_feedback_override_for_vdt90_and_logic4(self):
tests/test_demo.py:573:        server, thread = start_demo_server()
tests/test_demo.py:609:    def test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready(self):
tests/test_demo.py:610:        server, thread = start_demo_server()
tests/test_demo.py:648:    def test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready(self):
tests/test_demo.py:649:        server, thread = start_demo_server()
tests/test_demo.py:687:    def test_demo_server_api_unlocks_deep_range_once_l4_boundary_probe_is_ready(self):
tests/test_demo.py:688:        server, thread = start_demo_server()
tests/test_demo.py:720:    def test_demo_server_api_returns_monitor_timeline_payload(self):
tests/test_demo.py:721:        server, thread = start_demo_server()
tests/test_demo.py:764:    def test_demo_server_api_monitor_timeline_matches_key_transition_times(self):
tests/test_demo.py:765:        server, thread = start_demo_server()
tests/test_demo.py:799:    def test_demo_server_api_rejects_invalid_extended_lever_snapshot_input(self):
tests/test_demo.py:800:        server, thread = start_demo_server()
tests/test_demo.py:820:    def test_demo_server_serves_static_shell(self):
tests/test_demo.py:821:        server, thread = start_demo_server()
tests/test_demo.py:900:    def test_demo_server_index_html_contains_all_six_surfaces(self):
tests/test_demo.py:917:    def test_demo_server_unified_nav_css_served(self):
tests/test_demo.py:919:        server, thread = start_demo_server()
tests/test_demo.py:933:    def test_demo_server_serves_workbench_acceptance_shell(self):
tests/test_demo.py:938:        server, thread = start_demo_server()
tests/test_demo.py:956:    def test_demo_server_serves_browser_icon_and_manifest_assets(self):
tests/test_demo.py:957:        server, thread = start_demo_server()
tests/test_demo.py:1217:    def test_demo_server_api_returns_workbench_bootstrap_payload(self):
tests/test_demo.py:1218:        server, thread = start_demo_server()
tests/test_demo.py:1239:    def test_demo_server_bootstrap_lists_recent_workbench_archives(self):
tests/test_demo.py:1241:            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
tests/test_demo.py:1250:            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
tests/test_demo.py:1253:                payload = demo_server.workbench_bootstrap_payload()
tests/test_demo.py:1266:        payload = demo_server.workbench_bootstrap_payload()
tests/test_demo.py:1300:    def test_demo_server_recent_archives_api_lists_recent_workbench_archives(self):
tests/test_demo.py:1302:            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
tests/test_demo.py:1311:            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
tests/test_demo.py:1313:                server, thread = start_demo_server()
tests/test_demo.py:1329:    def test_demo_server_api_returns_workbench_bundle_and_archive_payload(self):
tests/test_demo.py:1332:            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
tests/test_demo.py:1333:                server, thread = start_demo_server()
tests/test_demo.py:1338:                            "packet_payload": demo_server.reference_workbench_packet_payload(),
tests/test_demo.py:1422:    def test_demo_server_api_can_restore_workbench_archive_payload(self):
tests/test_demo.py:1424:            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
tests/test_demo.py:1462:            server, thread = start_demo_server()
tests/test_demo.py:1492:    def test_demo_server_api_can_apply_safe_schema_repairs_for_workbench_packet(self):
tests/test_demo.py:1493:        server, thread = start_demo_server()
tests/test_demo.py:1498:                    "packet_payload": demo_server.workbench_bootstrap_payload()["template_packet"],
tests/test_demo.py:1523:    def test_demo_server_open_browser_helper_reports_failures(self):
tests/test_demo.py:1524:        url = demo_server.demo_url("127.0.0.1", 8000)
tests/test_demo.py:1528:        self.assertTrue(demo_server.open_browser(url, opener=opener))
tests/test_demo.py:1533:            self.assertFalse(demo_server.open_browser(url, opener=mock.Mock(return_value=False)))
tests/test_demo.py:1540:                demo_server.open_browser(url, opener=mock.Mock(side_effect=RuntimeError("blocked")))
tests/test_demo.py:1545:    def test_demo_server_help_documents_optional_open_affordance(self):
tests/test_demo.py:1547:            [sys.executable, "-m", "well_harness.demo_server", "--help"],
tests/test_demo.py:1563:    def test_demo_server_main_open_affordance_uses_helper_and_continues_serving(self):
tests/test_demo.py:1571:                self.serve_forever_called = False
tests/test_demo.py:1574:            def serve_forever(self):
tests/test_demo.py:1575:                self.serve_forever_called = True
tests/test_demo.py:1585:        with mock.patch.object(demo_server, "ThreadingHTTPServer", side_effect=fake_server):
tests/test_demo.py:1586:            with mock.patch.object(demo_server, "open_browser", return_value=False) as open_browser:
tests/test_demo.py:1589:                    exit_code = demo_server.main(["--host", "127.0.0.1", "--port", "0", "--open"])
tests/test_demo.py:1593:        self.assertIs(created_servers[0].handler_class, DemoRequestHandler)
tests/test_demo.py:1594:        self.assertTrue(created_servers[0].serve_forever_called)
tests/test_demo.py:1599:        with mock.patch.object(demo_server, "ThreadingHTTPServer", side_effect=fake_server):
tests/test_demo.py:1600:            with mock.patch.object(demo_server, "open_browser") as open_browser:
tests/test_demo.py:1602:                    self.assertEqual(demo_server.main(["--host", "127.0.0.1", "--port", "0"]), 0)
tests/test_demo.py:1626:            "OK preset_vdt90_ready",
tests/test_demo.py:1660:                "preset_vdt90_ready",
tests/test_demo.py:1686:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
tests/test_demo.py:1687:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
tests/test_demo.py:1771:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
tests/test_demo.py:1772:        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
tests/test_demo.py:1867:            "PYTHONPATH=src python3 -m well_harness.demo_server",
tests/test_demo.py:1868:            "PYTHONPATH=src python3 -m well_harness.demo_server --open",
tests/test_timeline_sim_page.py:8:from http.server import HTTPServer
tests/test_timeline_sim_page.py:11:from well_harness.demo_server import DemoRequestHandler
tests/test_timeline_sim_page.py:22:        cls.server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_timeline_sim_page.py:23:        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
tests/test_hardware_schema.py:18:import pytest
tests/test_hardware_schema.py:179:        with pytest.raises(HardwareSchemaNotFoundError) as exc_info:
tests/test_hardware_schema.py:185:        with pytest.raises(FileNotFoundError):
tests/test_hardware_schema.py:195:        with pytest.raises(HardwareSchemaError):  # Could be ValidationError or base
tests/test_hardware_schema.py:206:        with pytest.raises(HardwareSchemaValidationError) as exc_info:
tests/test_hardware_schema.py:214:        with pytest.raises(HardwareSchemaValidationError):
tests/test_hardware_schema.py:225:        with pytest.raises(HardwareSchemaValidationError) as exc_info:
tests/test_hardware_schema.py:235:        with pytest.raises(HardwareSchemaValidationError):
tests/test_hardware_schema.py:242:        with pytest.raises(HardwareSchemaValidationError):
src/well_harness/static/demo.html:601:    <code>src/well_harness/demo_server.py::lever_snapshot_payload</code> →
tests/test_lever_snapshot_manual_override_guard.py:18:from http.server import ThreadingHTTPServer
tests/test_lever_snapshot_manual_override_guard.py:20:import pytest
tests/test_lever_snapshot_manual_override_guard.py:22:from well_harness.demo_server import DemoRequestHandler
tests/test_lever_snapshot_manual_override_guard.py:47:def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
tests/test_lever_snapshot_manual_override_guard.py:48:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_lever_snapshot_manual_override_guard.py:49:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_lever_snapshot_manual_override_guard.py:54:def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
tests/test_lever_snapshot_manual_override_guard.py:67:@pytest.fixture
tests/test_lever_snapshot_manual_override_guard.py:69:    s, t = _start_demo_server()
tests/test_lever_snapshot_manual_override_guard.py:228:# ─── P2 R1 BLOCKER #2 R2 fix: /api/fantui/set_vdt test-probe acknowledgment ──
tests/test_lever_snapshot_manual_override_guard.py:231:def test_set_vdt_requires_test_probe_acknowledgment(server) -> None:
tests/test_lever_snapshot_manual_override_guard.py:232:    """P2 BLOCKER #2 R2 fix: /api/fantui/set_vdt is a test probe; without
tests/test_lever_snapshot_manual_override_guard.py:236:    status, body = _post(server, "/api/fantui/set_vdt", {"deploy_position_percent": 73})
tests/test_lever_snapshot_manual_override_guard.py:248:def test_set_vdt_with_acknowledgment_succeeds(server) -> None:
tests/test_lever_snapshot_manual_override_guard.py:249:    """When the caller acknowledges the bypass nature, set_vdt works as before."""
tests/test_lever_snapshot_manual_override_guard.py:252:        "/api/fantui/set_vdt",
tests/test_lever_snapshot_manual_override_guard.py:256:    assert body.get("deploy_position_percent") == pytest.approx(73, abs=0.01)
tests/test_p19_api_endpoints.py:8:needed since DemoServer extends http.server.HTTPServer.
tests/test_p19_api_endpoints.py:19:import pytest
tests/test_p19_api_endpoints.py:26:    """Starts demo_server on a random port, yields (host, port), shuts down on exit."""
tests/test_p19_api_endpoints.py:37:        from http.server import ThreadingHTTPServer
tests/test_p19_api_endpoints.py:38:        from well_harness.demo_server import DemoRequestHandler
tests/test_p19_api_endpoints.py:46:        self._server = ThreadingHTTPServer((self.host, self.port), DemoRequestHandler)
tests/test_p19_api_endpoints.py:47:        self._thread = threading.Thread(target=self._server.serve_forever)
tests/test_p19_api_endpoints.py:86:@pytest.fixture
tests/test_lever_snapshot_boundaries.py:16:from well_harness.demo_server import lever_snapshot_payload
tests/test_lever_snapshot_boundaries.py:60:    """Regression guard for demo_server.py:2859 —
tests/test_lever_snapshot_boundaries.py:101:    """Regression guard for demo_server.py:2332 — allowed_reverse_min_deg
tests/test_workbench_trust_affordance.py:18:from http.server import ThreadingHTTPServer
tests/test_workbench_trust_affordance.py:21:import pytest
tests/test_workbench_trust_affordance.py:23:from well_harness.demo_server import DemoRequestHandler
tests/test_workbench_trust_affordance.py:30:def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
tests/test_workbench_trust_affordance.py:31:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_workbench_trust_affordance.py:32:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_workbench_trust_affordance.py:37:def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
tests/test_workbench_trust_affordance.py:121:    server, thread = _start_demo_server()
tests/test_workbench_trust_affordance.py:142:    server, thread = _start_demo_server()
tests/test_thrust_reverser_intake_packet.py:24:import pytest
tests/test_reverse_diagnosis.py:14:import pytest
tests/test_reverse_diagnosis.py:86:        with pytest.raises(ValueError) as exc_info:
tests/test_reverse_diagnosis.py:93:        with pytest.raises(ValueError):
src/well_harness/static/fan_console.html:416:  fetch('/api/fantui/set_vdt',{
src/well_harness/static/workbench_bundle.html:592:                  没看到 cached_at 时默认按"还未预热"显示；缓存只在 demo_server 进程内有效，重启需重新预热。
tests/test_controller_truth_metadata_schema_extension.py:26:# Ensure src/ is on path for direct imports when pytest runs without editable install.
tests/test_c919_etras_frozen_v1_unit.py:4:import pytest
tests/test_monte_carlo_engine.py:18:import pytest
tests/test_workbench_shell.py:8:from http.server import ThreadingHTTPServer
tests/test_workbench_shell.py:10:from well_harness.demo_server import DemoRequestHandler
tests/test_workbench_shell.py:39:def start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
tests/test_workbench_shell.py:40:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_workbench_shell.py:41:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_workbench_shell.py:47:    server, thread = start_demo_server()
tests/test_content_type_whitelist.py:1:"""Tests for Content-Type whitelist enforcement in demo_server.
tests/test_content_type_whitelist.py:12:from http.server import ThreadingHTTPServer
tests/test_content_type_whitelist.py:14:from well_harness.demo_server import DemoRequestHandler
tests/test_content_type_whitelist.py:17:def start_demo_server():
tests/test_content_type_whitelist.py:18:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_content_type_whitelist.py:19:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_content_type_whitelist.py:27:        server, thread = start_demo_server()
tests/test_content_type_whitelist.py:47:        server, thread = start_demo_server()
tests/test_content_type_whitelist.py:69:        server, thread = start_demo_server()
tests/test_content_type_whitelist.py:91:        server, thread = start_demo_server()
tests/conftest.py:7:import pytest
tests/conftest.py:21:# tests/test_lever_snapshot_manual_override_guard.py.
tests/conftest.py:98:@pytest.fixture
tests/conftest.py:103:@pytest.fixture
tests/e2e/test_wow_b_monte_carlo.py:4:demo_server on :8799: return shape, value ranges, timing budget, and
tests/e2e/test_wow_b_monte_carlo.py:11:import pytest
tests/e2e/test_wow_b_monte_carlo.py:30:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:31:def test_wow_b_monte_carlo_returns_contract_shape(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:32:    status, body = _run(api_post, demo_server, 1000)
tests/e2e/test_wow_b_monte_carlo.py:39:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:40:def test_wow_b_10k_trials_under_5s(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:43:    status, body = _run(api_post, demo_server, 10000)
tests/e2e/test_wow_b_monte_carlo.py:50:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:51:def test_wow_b_success_rate_in_unit_interval(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:52:    status, body = _run(api_post, demo_server, 2000)
tests/e2e/test_wow_b_monte_carlo.py:62:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:63:def test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:64:    status, body = _run(api_post, demo_server, 5000)
tests/e2e/test_wow_b_monte_carlo.py:76:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:77:def test_wow_b_is_deterministic_under_fixed_seed(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:79:    s1, b1 = _run(api_post, demo_server, 1000, seed=42)
tests/e2e/test_wow_b_monte_carlo.py:80:    s2, b2 = _run(api_post, demo_server, 1000, seed=42)
tests/e2e/test_wow_b_monte_carlo.py:85:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:86:def test_wow_b_n_trials_zero_is_clamped_to_min(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:91:    status, body = _run(api_post, demo_server, 0)
tests/e2e/test_wow_b_monte_carlo.py:96:@pytest.mark.e2e
tests/e2e/test_wow_b_monte_carlo.py:97:def test_wow_b_n_trials_overflow_is_clamped_to_max(demo_server, api_post):
tests/e2e/test_wow_b_monte_carlo.py:98:    status, body = _run(api_post, demo_server, 1_500_000)
tests/test_workbench_prompt_ticket_auth.py:4:import pytest
tests/test_workbench_prompt_ticket_auth.py:77:    with pytest.raises(RestrictedAuthError, match="Authorized Engineer"):
tests/test_workbench_prompt_ticket_auth.py:80:    with pytest.raises(RestrictedAuthError, match="Scope Files"):
tests/test_proposal_schema_store.py:4:import pytest
tests/test_proposal_schema_store.py:72:    with pytest.raises(ValueError, match="tool"):
tests/test_proposal_schema_store.py:76:    with pytest.raises(ValueError, match="proposal id"):
tests/test_nan_inf_clamp.py:7:from well_harness.demo_server import _optional_request_float
tests/e2e/test_wow_a_causal_chain.py:9:demo_server on :8799, independent of any MiniMax availability.
tests/e2e/test_wow_a_causal_chain.py:15:import pytest
tests/e2e/test_wow_a_causal_chain.py:20:# Domain semantics (probed from live demo_server post-a46e4e6 / 2ded020):
tests/e2e/test_wow_a_causal_chain.py:28:#           (demo_server._canonical_pullback_sequence, extended in commit a46e4e6)
tests/e2e/test_wow_a_causal_chain.py:64:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:65:def test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:66:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:78:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:79:def test_wow_a_lever_snapshot_exposes_four_logic_gates(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:80:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:92:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:93:def test_wow_a_beat_early_activates_logic1_and_logic2_only(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:95:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_EARLY_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:104:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:105:def test_wow_a_beat_deep_activates_logic2_and_logic3(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:121:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:131:        "demo_server._canonical_pullback_sequence and commit a46e4e6)"
tests/e2e/test_wow_a_causal_chain.py:135:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:136:def test_wow_a_beat_blocked_deactivates_entire_chain(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:138:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_BLOCKED_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:147:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:148:def test_wow_a_truth_engine_is_deterministic(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:150:    status1, body1 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:151:    status2, body2 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:159:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:160:def test_wow_a_response_under_500ms_warm(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:162:    api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)  # warmup
tests/e2e/test_wow_a_causal_chain.py:164:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/e2e/test_wow_a_causal_chain.py:170:@pytest.mark.e2e
tests/e2e/test_wow_a_causal_chain.py:171:def test_wow_a_lever_snapshot_evidence_field_present(demo_server, api_post):
tests/e2e/test_wow_a_causal_chain.py:173:    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
tests/test_fantui_tick_runtime.py:6:     over the demo_server http handler.
tests/test_fantui_tick_runtime.py:16:from http.server import ThreadingHTTPServer
tests/test_fantui_tick_runtime.py:19:from well_harness.demo_server import DemoRequestHandler
tests/test_fantui_tick_runtime.py:237:    """End-to-end checks against the DemoRequestHandler.
tests/test_fantui_tick_runtime.py:245:        from well_harness import demo_server
tests/test_fantui_tick_runtime.py:246:        demo_server._FANTUI_SYSTEM.reset()
tests/test_fantui_tick_runtime.py:247:        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_fantui_tick_runtime.py:248:        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
tests/test_fantui_tick_runtime.py:398:        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_fantui_tick_runtime.py:399:        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
tests/test_onboard_new_system_dry_run.py:19:import pytest
tests/e2e/fixtures/schema_snapshot.json:4:    "purpose": "Anchor for P20.0 wow-scenario e2e assertions. Fields below are the observed response shapes from a running demo_server on :8799. Any drift should either (a) fail existing e2e tests, or (b) drive an update to this file + asserting tests in the same commit.",
tests/e2e/fixtures/schema_snapshot.json:37:    "notes": "MiniMax URL hardcoded (api.minimax.chat). No env hook for mock. Tests force the 'minimax_api_key_missing' path by running a second demo_server subprocess with HOME=<empty tmp>."
src/well_harness/static/index.html:449:      <strong style="color:var(--home-text)">启动服务</strong>：<code>python3 -m well_harness.demo_server --host 127.0.0.1 --port 8002</code> ·
tests/test_gsd_notion_sync.py:2311:            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
tests/test_gsd_notion_sync.py:2373:            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
tests/test_gsd_notion_sync.py:2435:            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
tests/test_gsd_notion_sync.py:2547:                command="PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py",
src/well_harness/static/fantui_requirements.html:342:        <div class="trace-impl">demo_server.py:_build_tra_lock_payload() + demo.js:guardTraSlider()</div>
tests/test_timeline_c919_etras.py:12:from http.server import ThreadingHTTPServer
tests/test_timeline_c919_etras.py:219:        cls.server = ThreadingHTTPServer(("127.0.0.1", cls.port), cls.module.Handler)
tests/test_timeline_c919_etras.py:220:        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
tests/test_c919_etras_workstation.py:19:from http.server import ThreadingHTTPServer
tests/test_c919_etras_workstation.py:23:from well_harness.demo_server import DemoRequestHandler
tests/test_c919_etras_workstation.py:34:    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
tests/test_c919_etras_workstation.py:35:    thread = threading.Thread(target=server.serve_forever, daemon=True)
tests/test_c919_etras_workstation.py:258:    """Live-server integration tests (spin up demo_server in-process)."""
tests/e2e/test_wow_c_reverse_diagnose.py:11:import pytest
tests/e2e/test_wow_c_reverse_diagnose.py:26:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:27:def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:28:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:41:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:42:def test_wow_c_each_result_carries_required_parameter_keys(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:43:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:55:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:56:def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:58:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:69:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:70:@pytest.mark.parametrize("outcome", sorted(VALID_OUTCOMES))
tests/e2e/test_wow_c_reverse_diagnose.py:71:def test_wow_c_all_valid_outcomes_return_200(demo_server, api_post, outcome):
tests/e2e/test_wow_c_reverse_diagnose.py:73:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:82:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:83:def test_wow_c_invalid_outcome_returns_structured_400(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:84:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:96:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:97:def test_wow_c_missing_outcome_returns_400(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:98:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/e2e/test_wow_c_reverse_diagnose.py:105:@pytest.mark.e2e
tests/e2e/test_wow_c_reverse_diagnose.py:106:def test_wow_c_max_results_bound_is_respected(demo_server, api_post):
tests/e2e/test_wow_c_reverse_diagnose.py:107:    status, body = api_post(demo_server, "/api/diagnosis/run", {
tests/test_c919_etras_frozen_v1_integration.py:4:import pytest
tests/e2e/conftest.py:3:Boots well_harness.demo_server as a subprocess on port 8799, waits until
tests/e2e/conftest.py:6:All tests in this package must carry @pytest.mark.e2e so the default
tests/e2e/conftest.py:7:pytest run (639 passed) is not affected. Opt-in via: pytest -m e2e
tests/e2e/conftest.py:22:import pytest
tests/e2e/conftest.py:70:        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
tests/e2e/conftest.py:97:@pytest.fixture(scope="session")
tests/e2e/conftest.py:98:def demo_server():
tests/e2e/conftest.py:99:    """Boot demo_server on :8799 for the whole e2e session."""
tests/e2e/conftest.py:101:        pytest.fail(f"Port {PORT} is already in use; cannot start e2e demo_server")
tests/e2e/conftest.py:106:            pytest.fail(f"demo_server did not become ready on :{PORT} within {READY_TIMEOUT_S}s")
tests/e2e/conftest.py:112:@pytest.fixture
src/well_harness/fantui_tick.py:8:Used by demo_server's ``/api/fantui/tick`` endpoint as a live counterpart to
tests/test_p19_api_multisystem.py:22:import pytest
tests/test_p19_api_multisystem.py:26:    """Starts demo_server on a random port, yields (host, port), shuts down on exit."""
tests/test_p19_api_multisystem.py:36:        from http.server import ThreadingHTTPServer
tests/test_p19_api_multisystem.py:37:        from well_harness.demo_server import DemoRequestHandler
tests/test_p19_api_multisystem.py:44:        self._server = ThreadingHTTPServer((self.host, self.port), DemoRequestHandler)
tests/test_p19_api_multisystem.py:45:        self._thread = threading.Thread(target=self._server.serve_forever)
tests/test_p19_api_multisystem.py:83:@pytest.fixture
src/well_harness/tools/generate_adapter.py:256:        "max_n1k_deploy_limit": 60.0,  # demo_server default
src/well_harness/workbench_bundle.py:181:            # Path escapes sandbox — raise specific error so demo_server can return sandbox_violation
src/well_harness/workbench_bundle.py:259:            # Re-raise as SandboxEscapeError with formatted message so demo_server

codex
The code change itself is aligned with the requested scope. I’m verifying two things now: the targeted regression test passes, and the `residual_risk` wording is consistent with the existing 409 disclosure pattern rather than introducing a second, weaker contract.
exec
/bin/zsh -lc "rg -n 'residual_risk|test_probe_unacknowledged|manual_feedback_override authority chain|approval endpoint hardening' src/well_harness/demo_server.py tests/test_lever_snapshot_manual_override_guard.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/test_lever_snapshot_manual_override_guard.py:191:def test_residual_risk_disclosure_present_on_409(server) -> None:
tests/test_lever_snapshot_manual_override_guard.py:201:    risk = body.get("residual_risk", "")
tests/test_lever_snapshot_manual_override_guard.py:238:    assert body.get("error") == "test_probe_unacknowledged"
tests/test_lever_snapshot_manual_override_guard.py:243:    risk = body.get("residual_risk", "")
src/well_harness/demo_server.py:370:                        "error": "test_probe_unacknowledged",
src/well_harness/demo_server.py:373:                            "manual_feedback_override authority chain. To use it from "
src/well_harness/demo_server.py:383:                        "residual_risk": (
src/well_harness/demo_server.py:387:                            "scoped to E11-16 (approval endpoint hardening)."
src/well_harness/demo_server.py:695:            "residual_risk": (
src/well_harness/demo_server.py:698:                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
src/well_harness/demo_server.py:1571:    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
src/well_harness/demo_server.py:1616:            residual_risk=residual_risk,

exec
/bin/zsh -lc 'PYTHONPATH=src python3 -m pytest -q tests/test_lever_snapshot_manual_override_guard.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
codex
The targeted guard suite started cleanly; I’m waiting for the final result, then I’ll boot the demo server and hit the exact `curl` probe the finding called out.
 succeeded in 7833ms:
...............                                                          [100%]
15 passed in 7.60s

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '2710,2765p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  2710	    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
  2711	    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
  2712	    parser.add_argument(
  2713	        "--open",
  2714	        action="store_true",
  2715	        help=(
  2716	            "Open the local UI URL with Python's standard-library webbrowser.open; "
  2717	            "this is a launch convenience, not browser E2E automation."
  2718	        ),
  2719	    )
  2720	    return parser
  2721	
  2722	
  2723	def demo_url(host: str, port: int) -> str:
  2724	    return f"http://{host}:{port}/index.html"
  2725	
  2726	
  2727	def open_browser(url: str, opener=webbrowser.open) -> bool:
  2728	    try:
  2729	        opened = bool(opener(url))
  2730	    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
  2731	        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
  2732	        return False
  2733	    if not opened:
  2734	        print(f"Could not open browser automatically. Open {url} manually.")
  2735	    return opened
  2736	
  2737	
  2738	def main(argv: list[str] | None = None) -> int:
  2739	    args = build_parser().parse_args(argv)
  2740	    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
  2741	    host, port = server.server_address
  2742	    url = demo_url(host, port)
  2743	    print(f"Serving well-harness demo UI at {url}")
  2744	    if args.open:
  2745	        open_browser(url)
  2746	    try:
  2747	        server.serve_forever()
  2748	    except KeyboardInterrupt:
  2749	        print("\nStopping well-harness demo UI.")
  2750	    finally:
  2751	        server.server_close()
  2752	    return 0
  2753	
  2754	
  2755	if __name__ == "__main__":
  2756	    raise SystemExit(main())

exec
/bin/zsh -lc "python3 - <<'PY'
import socket
for port in (8798, 8799, 8002, 8770):
    s = socket.socket()
    try:
        s.bind(('127.0.0.1', port))
    except OSError:
        print(f'{port}:in_use')
    else:
        print(f'{port}:free')
    finally:
        s.close()
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
8798:free
8799:free
8002:free
8770:free

codex
I have a free local port and the server entrypoint. Next step is the actual probe: launch `demo_server` on a disposable port, POST the no-ack payload with `curl`, and capture the 409 body verbatim enough to confirm `residual_risk` now names `E11-16`.
exec
/bin/zsh -lc 'PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8798' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "curl -sS -i -X POST http://127.0.0.1:8798/api/fantui/set_vdt -H 'Content-Type: application/json' --data '{\"deploy_position_percent\":73}'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
HTTP/1.0 409 Conflict
Server: WellHarnessDemo/1.0 Python/3.9.6
Date: Sat, 25 Apr 2026 15:39:15 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 554
Cache-Control: no-store

{"error": "test_probe_unacknowledged", "message": "/api/fantui/set_vdt is a test probe that bypasses the manual_feedback_override authority chain. To use it from tests/dev tooling, pass test_probe_acknowledgment=true. For authoritative manual feedback, use /api/lever-snapshot with feedback_mode=manual_feedback_override + sign-off.", "residual_risk": "Test-probe bypass remains structural; test_probe_acknowledgment=true is not authentication. Replay/nonce/freshness validation and one-shot latching are scoped to E11-16 (approval endpoint hardening)."}
 succeeded in 16623ms:
^C
Stopping well-harness demo UI.

exec
/bin/zsh -lc "nl -ba src/well_harness/demo_server.py | sed -n '680,705p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

codex
The requested probe is complete: the live 409 response now carries `residual_risk` with the deferred `E11-16` disclosure. I’m doing one last pass on the exact line references and then I’ll issue the review verdict in the requested closure format.
exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '791,806p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc 'git rev-parse HEAD && git merge-base --is-ancestor 75070ee 6a519bb; echo $?' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
6a519bb4459948083585ef94462821e165ef9095
0

codex
**APPROVE**

IMPORTANT #4 -> CLOSED.

No findings in R3. In [src/well_harness/demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365) the `/api/fantui/set_vdt` 409 reject path now includes `residual_risk` at [lines 378-387](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:378), and the disclosure explicitly states `test_probe_acknowledgment=true` is not authentication and that replay/nonce/freshness hardening is deferred to `E11-16`. The companion check in [tests/test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:231) asserts `E11-16` plus `structural`/`authentication`, and the targeted suite passed: `15 passed in 7.60s`.

Live probe confirmed closure on the exact path called out: `curl -i -X POST http://127.0.0.1:8798/api/fantui/set_vdt -H 'Content-Type: application/json' --data '{"deploy_position_percent":73}'` returned `HTTP/1.0 409 Conflict` with `error: test_probe_unacknowledged` and a `residual_risk` body field containing `E11-16`. Truth-engine red line also holds: `git diff --name-only 75070ee..6a519bb` shows only `src/well_harness/demo_server.py` and `tests/test_lever_snapshot_manual_override_guard.py`; there are no changes in `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`.

**P2 — Senior FCS Engineer (Tier-B, E11-14 R3)**


tokens used
53,588
**APPROVE**

IMPORTANT #4 -> CLOSED.

No findings in R3. In [src/well_harness/demo_server.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:365) the `/api/fantui/set_vdt` 409 reject path now includes `residual_risk` at [lines 378-387](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/demo_server.py:378), and the disclosure explicitly states `test_probe_acknowledgment=true` is not authentication and that replay/nonce/freshness hardening is deferred to `E11-16`. The companion check in [tests/test_lever_snapshot_manual_override_guard.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_lever_snapshot_manual_override_guard.py:231) asserts `E11-16` plus `structural`/`authentication`, and the targeted suite passed: `15 passed in 7.60s`.

Live probe confirmed closure on the exact path called out: `curl -i -X POST http://127.0.0.1:8798/api/fantui/set_vdt -H 'Content-Type: application/json' --data '{"deploy_position_percent":73}'` returned `HTTP/1.0 409 Conflict` with `error: test_probe_unacknowledged` and a `residual_risk` body field containing `E11-16`. Truth-engine red line also holds: `git diff --name-only 75070ee..6a519bb` shows only `src/well_harness/demo_server.py` and `tests/test_lever_snapshot_manual_override_guard.py`; there are no changes in `controller.py`, `runner.py`, `models.py`, or `src/well_harness/adapters/`.

**P2 — Senior FCS Engineer (Tier-B, E11-14 R3)**


