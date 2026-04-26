2026-04-26T01:56:42.699858Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-26T01:56:42.699936Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc780-d64c-71c0-9453-8f58b38e7410
--------
user
You are Codex GPT-5.4 acting as **Persona P5 — Apps Engineer** (Tier-B single-persona pipeline, E11-11 sub-phase).

# Context — E11-11 JS-boot e2e smoke + bundle-page bug fix

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-11-e2e-js-boot-smoke-20260426`
**PR:** #27
**Worktree HEAD:** `9da3d97` (single commit on top of main `060f698`)

## What E11-11 ships

This sub-phase has TWO components, both delivered together:

### Component 1 — e2e infra (the planned scope)

`tests/e2e/test_workbench_js_boot_smoke.py` (NEW, 8 Playwright tests):
- Marked `@pytest.mark.e2e` (default `pytest` run deselects it via
  `pyproject.toml addopts = "-m 'not e2e'"`; opt-in via `pytest -m e2e`)
- Auto-skips via `pytest.importorskip("playwright.sync_api")` if
  Playwright is absent, and via `pytest.skip(...)` if Chromium is absent
- Reuses the session-scoped `demo_server` fixture from
  `tests/e2e/conftest.py` (boots `well_harness.demo_server` on :8799)

E11-08 closure (4 tests): default Kogami visibility, `?identity=Engineer`
swap, `window.setWorkbenchIdentity` programmatic toggle, blank-string guard.

E11-13 closure (2 tests): shell + bundle pages both boot without JS errors.

E11-15c closure (2 tests): real-DOM headers + buttons all render Chinese-first.

### Component 2 — bundle-page bug surfaced + fixed in lockstep

The first run of `test_bundle_workbench_boots_without_js_errors`
crashed with:
```
TypeError: document.createElement is not a function
    at workbench.js:1225:27
    at Array.map (<anonymous>)
    at renderFingerprintDocumentList (workbench.js:1224)
    at renderSystemFingerprint (workbench.js:1311)
    at renderSystemFingerprintFromPacketPayload (workbench.js:1658)
    at loadBootstrapPayload (workbench.js:3502)
```

Root cause: `documents.map((document) => { ... })` shadowed the global
DOM `document`, so `document.createElement(...)` called a method on the
plain data object instead of the DOM. The bundle page was silently
rendering nothing for the System Fingerprint document list.

Fix: rename the loop parameter `document → doc` at TWO sites:
- `workbench.js:1224` `renderFingerprintDocumentList` (the crashing site)
- `workbench.js:1649` `renderSystemFingerprintFromPacketPayload` (sibling
  anti-pattern; didn't crash because it doesn't call `document.X`, but
  same shadow pattern, eliminated for hygiene + to satisfy the new
  guard test)

Both edits are pure variable-rename refactors — zero behavior change in
any non-shadowed code path; the bundle code path is restored to its
intended behavior.

`tests/test_workbench_js_no_global_shadowing.py` (NEW, 2 tests in
default lane): static-source regex guard against arrow-callback and
named-function shadowing of the `document` global. So even if the e2e
suite is deselected, the regression is caught.

## Files in scope

- `src/well_harness/static/workbench.js` — 2 loop-parameter renames (BUGFIX)
- `tests/e2e/test_workbench_js_boot_smoke.py` — NEW (8 e2e tests)
- `tests/test_workbench_js_no_global_shadowing.py` — NEW (2 guard tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

## Your specific lens (P5 Apps Engineer)

Focus on:
- **Reproducibility**: can a fresh checkout (`pip install -e . && playwright install chromium && pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py`) reproduce 8/8 pass? Are there hidden environment assumptions (e.g., must run from repo root, must have port 8799 free, must have specific Python version)?
- **Browser boot health**: are there other latent JS bugs the e2e suite SHOULD have caught but didn't? (e.g., other shadow patterns, race conditions in `loadBootstrapPayload`, console warnings that aren't pageerror-level but indicate trouble.)
- **Bug fix correctness**: are the 2 renames truly behavior-preserving? Specifically — is there ANY caller that depends on the original `document` shadow being in scope inside that closure? (e.g., closures captured via assignment to outer-scope refs, JSON serialization that captures the shadowed name.)
- **Bug fix completeness**: I claim 2 shadow sites; have I missed any? The static-source guard test is a regex; verify it actually covers the cases by independently grepping `\(.*document.*\)\s*=>` and `function\s+\w+\s*\(.*document.*\)` patterns in workbench.js / annotation_overlay.js / any other JS.
- **e2e suite resilience**: do the tests pass deterministically across reruns? Does any test rely on timing rather than `wait_until="networkidle"` or explicit waits? (I added 500ms waits for the no-error tests to give async handlers a chance to throw — is that sufficient or should it be longer / event-driven?)
- **Default-lane safety**: confirm the new e2e suite does NOT run in the default `pytest` lane (since CI-level integrations may not have Chromium). Verify by `pytest --collect-only` showing the e2e tests as deselected.
- **Cross-impact on existing e2e**: do `tests/e2e/test_wow_*.py` still pass under `pytest -m e2e`? (The session-scoped `demo_server` fixture is shared.)

## Verification status

- 1080 / 1080 default-lane pytest pass (35 deselected = the new e2e suite + existing wow_a/b/c)
- 8 / 8 e2e suite pass under `pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py` locally (Playwright + Chromium 145.0.7632.6)
- 2 / 2 new shadow-guard tests pass

## Out of scope (deliberately deferred)

- **Existing wow_a/b/c e2e tests** — not modified.
- **JS smoke for `/workbench/start` or other static pages** — narrow scope to /workbench (shell + bundle).
- **CI integration** (auto-running e2e in GitHub Actions) — local infra only for now.

## Verdict format

Return one of: **APPROVE** / **APPROVE_WITH_NITS** / **CHANGES_REQUIRED**.

Each finding: BLOCKER / IMPORTANT / NIT / INFO with file:line citation. Out-of-scope items → NIT/INFO only.

Live-probe at least one path. Cite the probe.

Truth-engine red line: confirm `git diff --name-only main..9da3d97` shows no changes to `controller.py` / `runner.py` / `models.py` / `src/well_harness/adapters/` / `workbench.html` / `workbench.css` / `demo_server.py`.

Sign as: **P5 — Apps Engineer (Tier-B, E11-11)**
codex
Reviewing PR #27 as P5 Apps Engineer. I’m loading the repo-specific review workflow and checking the exact diff, test wiring, and one live browser/probe path before I decide whether the claims hold.
exec
/bin/zsh -lc "sed -n '1,220p' /Users/Zhuanz/.codex/plugins/cache/openai-curated/superpowers/421657af0e7e94573f3a5f2c51091df43668da94/skills/using-superpowers/SKILL.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
/bin/zsh -lc 'rg -n "LogicMVP|ai-fantui-logicmvp|E11-11|workbench_js_boot_smoke|global shadow|shadowing" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
842:# Task Group: AI FANTUI LogicMVP autonomous Notion-synced development
844:scope: Continue AI FANTUI LogicMVP automatically from `.planning` and Notion-synced state, keep the control tower current, and use approved/no-review gate state to decide whether to keep moving.
845:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s autonomous GSD + Notion workflow, but exact phase numbers and page text are repo-specific.
851:- rollout_summaries/2026-04-08T15-29-03-VmzV-notion_api_hub_and_p6_sync_timeout_baseline_restore.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/08/rollout-2026-04-08T23-29-03-019d6db6-16ac-7431-9092-63393e7770a3.jsonl, updated_at=2026-04-11T04:03:27+00:00, thread_id=019d6db6-16ac-7431-9092-63393e7770a3, isolated hub and P6 timeout/baseline recovery)
855:- AI FANTUI LogicMVP 控制塔, NOTION_API_KEY, gsd_notion_sync.py, prepare-opus-review, writeback timeout, stronger QA baseline, 175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass
861:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
862:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
872:- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
873:- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
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

codex
Using `superpowers:using-superpowers` to enforce skill selection and `gsd-code-review` as the review workflow. I’ve also done the repo memory quick pass; next I’m checking the exact changed files, JS shadow patterns, and the e2e collection/runtime behavior.
  → Inspect diff scope and truth-engine red-line files against main..9da3d97
  • Review JS bug fix and independently search for missed document-shadow patterns
  • Probe pytest collection and run targeted live verification for boot/e2e behavior
  • Assess reproducibility, determinism, and write review verdict with citations
exec
/bin/zsh -lc 'git diff --name-only main..9da3d97' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md
.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md
src/well_harness/static/workbench.js
tests/e2e/test_workbench_js_boot_smoke.py
tests/test_workbench_js_no_global_shadowing.py

exec
/bin/zsh -lc 'git status --short' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-output.md
?? .planning/phases/E11-workbench-engineer-first-ux/persona-P5-E11-11-prompt.txt

exec
/bin/zsh -lc 'git diff --stat main..9da3d97' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'git log --oneline --decorate -n 5' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
 .../E11-11-SURFACE-INVENTORY.md                    | 106 +++++++++++
 .../PERSONA-ROTATION-STATE.md                      |   1 +
 src/well_harness/static/workbench.js               |  12 +-
 tests/e2e/test_workbench_js_boot_smoke.py          | 206 +++++++++++++++++++++
 tests/test_workbench_js_no_global_shadowing.py     |  44 +++++
 5 files changed, 363 insertions(+), 6 deletions(-)

 succeeded in 0ms:
9da3d97 (HEAD -> feat/e11-11-e2e-js-boot-smoke-20260426) phase(E11-11): JS-boot e2e smoke + bundle-page bug fix surfaced by it
060f698 (origin/main, origin/HEAD, main) docs(E11-15c): bump coordination evidence — PR #26 merged with P4 APPROVE_WITH_NITS
393bccf phase(E11-15c): closure of P3 NITs — column h2 dir flip + h1/eyebrow dedup (#26)
62e58fb docs(E11-15b): bump coordination evidence — PR #25 merged with Tier-B P3 APPROVE_WITH_NITS
92af49a phase(E11-15b): Chinese-first iter 2 — h1/h2/buttons/caption bilingualized (#25)

codex
The diff scope is clean against the truth-engine red line so far: only the five claimed files changed, and none of `controller.py`, `runner.py`, `models.py`, `adapters/`, `workbench.html`, `workbench.css`, or `demo_server.py` appear in `main..9da3d97`. I’m pulling the actual hunks plus the pytest/e2e fixture wiring now.
exec
/bin/zsh -lc "sed -n '1,220p' pyproject.toml" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "well-harness"
version = "0.1.0"
description = "Engineering workbench for aviation control logic: requirements to runtime verification evidence"
readme = "README.md"
requires-python = ">=3.9"
# Runtime stays stdlib-only — demo_server.py imports no third-party packages.
# Third-party deps land in [project.optional-dependencies] groups below so
# they can be installed explicitly for test/tooling lanes.

[project.optional-dependencies]
# Install with: pip install -e '.[dev]'
# Covers the pytest default lane + the schema-validation scripts under tools/.
dev = [
    "pytest>=8.0",
    "pytest-subtests>=0.11",
    "jsonschema>=4.17",
    "numpy>=1.24",
    "pyyaml>=6.0",
]

[tool.setuptools.package-dir]
"" = "src"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
# Default CI lane excludes e2e; opt-in with: pytest -m e2e (or pytest -m "e2e or not e2e")
addopts = "-m 'not e2e'"
# Constrain discovery to tests/ so shelved archive trees are never collected.
testpaths = ["tests"]
# Make bare `pytest` work without requiring PYTHONPATH=src:. on the caller:
# - src: well_harness package imports
# - . (repo root): tools.* and tests.* imports from a few cross-file suites
pythonpath = ["src", "."]
markers = [
    "e2e: opt-in end-to-end tests that boot demo_server on :8799 (run with -m e2e)",
]

exec
/bin/zsh -lc 'git diff main..9da3d97 -- src/well_harness/static/workbench.js tests/e2e/test_workbench_js_boot_smoke.py tests/test_workbench_js_no_global_shadowing.py' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/src/well_harness/static/workbench.js b/src/well_harness/static/workbench.js
index 20a820f..375e6c9 100644
--- a/src/well_harness/static/workbench.js
+++ b/src/well_harness/static/workbench.js
@@ -1221,7 +1221,7 @@ function renderFingerprintDocumentList(documents, fallbackText) {
     return;
   }
 
-  container.replaceChildren(...documents.map((document) => {
+  container.replaceChildren(...documents.map((doc) => {
     const card = document.createElement("article");
     card.className = "workbench-fingerprint-item";
 
@@ -1230,20 +1230,20 @@ function renderFingerprintDocumentList(documents, fallbackText) {
 
     const title = document.createElement("strong");
     title.className = "workbench-fingerprint-item-title";
-    title.textContent = document.title || document.id || "未命名文档";
+    title.textContent = doc.title || doc.id || "未命名文档";
 
     const chips = document.createElement("div");
     chips.className = "workbench-fingerprint-chip-row";
     chips.append(
-      createFingerprintChip(documentKindLabel(document.kind), "source"),
-      createFingerprintChip(documentRoleLabel(document.role), "role"),
+      createFingerprintChip(documentKindLabel(doc.kind), "source"),
+      createFingerprintChip(documentRoleLabel(doc.role), "role"),
     );
 
     header.append(title, chips);
 
     const location = document.createElement("p");
     location.className = "workbench-fingerprint-item-detail";
-    location.textContent = document.location || "未提供路径";
+    location.textContent = doc.location || "未提供路径";
 
     card.append(header, location);
     return card;
@@ -1646,7 +1646,7 @@ function renderSystemFingerprintFromPacketPayload(packetPayload, {
 } = {}) {
   const documents = Array.isArray(packetPayload.source_documents) ? packetPayload.source_documents : [];
   const signals = Array.isArray(packetPayload.components) ? packetPayload.components : [];
-  const documentKinds = uniqueValues(documents.map((document) => document.kind));
+  const documentKinds = uniqueValues(documents.map((doc) => doc.kind));
   const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
   if (documentKinds.length > 1) {
     sourceModeParts.push("混合来源");
diff --git a/tests/e2e/test_workbench_js_boot_smoke.py b/tests/e2e/test_workbench_js_boot_smoke.py
new file mode 100644
index 0000000..b51e6b5
--- /dev/null
+++ b/tests/e2e/test_workbench_js_boot_smoke.py
@@ -0,0 +1,206 @@
+"""E11-11 — JS-boot smoke tests for /workbench (Playwright + Chromium).
+
+Closes deferred JS verification debt accumulated across:
+- E11-08 (role affordance — applyRoleAffordance + setWorkbenchIdentity +
+  ?identity= URL param parsing — only structural-static tests until now)
+- E11-13 (bundle/shell sentinel guard — only static-source check until now)
+- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
+  until now; this verifies the strings actually render in a real DOM)
+
+Marked `@pytest.mark.e2e` (the suite is deselected by the default
+addopts in pyproject.toml `-m 'not e2e'`). Runs only when invoked
+explicitly via `pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py`.
+
+Reuses the session-scoped `demo_server` fixture from
+`tests/e2e/conftest.py` which boots `well_harness.demo_server` on
+port 8799.
+
+Skips gracefully if Playwright + chromium are not installed.
+"""
+
+from __future__ import annotations
+
+import pytest
+
+pytestmark = pytest.mark.e2e
+
+# Skip the whole module if Playwright sync API or its browsers are missing.
+playwright_sync_api = pytest.importorskip("playwright.sync_api")
+from playwright.sync_api import sync_playwright  # noqa: E402
+
+
+@pytest.fixture(scope="module")
+def browser():
+    with sync_playwright() as pw:
+        try:
+            b = pw.chromium.launch()
+        except Exception as exc:
+            pytest.skip(f"chromium browser not installed: {exc}")
+        try:
+            yield b
+        finally:
+            b.close()
+
+
+def _new_page_with_error_capture(browser):
+    page = browser.new_page()
+    errors: list[str] = []
+    page.on("pageerror", lambda exc: errors.append(str(exc)))
+    return page, errors
+
+
+# ─── E11-08 closure: role affordance JS toggle (4 tests) ─────────────
+
+
+def test_default_identity_kogami_shows_approval_center(demo_server, browser):
+    page, errors = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    state = page.evaluate(
+        """
+        () => ({
+          identityAttr: document.getElementById('workbench-identity')
+            ?.getAttribute('data-identity-name'),
+          entryHidden: document.getElementById('approval-center-entry')?.hidden,
+          panelHidden: document.getElementById('approval-center-panel')?.hidden,
+          affState: document.getElementById('workbench-pending-signoff-affordance')
+            ?.getAttribute('data-pending-signoff'),
+        })
+        """
+    )
+    assert errors == [], f"page JS errors: {errors}"
+    assert state["identityAttr"] == "Kogami"
+    assert state["entryHidden"] is False
+    assert state["panelHidden"] is False
+    assert state["affState"] == "hidden"
+
+
+def test_engineer_identity_url_param_swaps_to_pending_affordance(demo_server, browser):
+    page, errors = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench?identity=Engineer", wait_until="networkidle")
+    state = page.evaluate(
+        """
+        () => ({
+          identityAttr: document.getElementById('workbench-identity')
+            ?.getAttribute('data-identity-name'),
+          entryHidden: document.getElementById('approval-center-entry')?.hidden,
+          entryAriaDisabled: document.getElementById('approval-center-entry')
+            ?.getAttribute('aria-disabled'),
+          panelHidden: document.getElementById('approval-center-panel')?.hidden,
+          affState: document.getElementById('workbench-pending-signoff-affordance')
+            ?.getAttribute('data-pending-signoff'),
+        })
+        """
+    )
+    assert errors == [], f"page JS errors: {errors}"
+    assert state["identityAttr"] == "Engineer"
+    assert state["entryHidden"] is True
+    assert state["entryAriaDisabled"] == "true"
+    assert state["panelHidden"] is True
+    assert state["affState"] == "visible"
+
+
+def test_set_workbench_identity_window_function_toggles_dom(demo_server, browser):
+    page, errors = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    after = page.evaluate(
+        """
+        () => {
+          const ok = window.setWorkbenchIdentity('Engineer');
+          return {
+            ok,
+            affState: document.getElementById('workbench-pending-signoff-affordance')
+              ?.getAttribute('data-pending-signoff'),
+            entryHidden: document.getElementById('approval-center-entry')?.hidden,
+          };
+        }
+        """
+    )
+    assert errors == [], f"page JS errors: {errors}"
+    assert after["ok"] is True
+    assert after["affState"] == "visible"
+    assert after["entryHidden"] is True
+
+
+def test_set_workbench_identity_blank_returns_false(demo_server, browser):
+    page, _ = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    result = page.evaluate("() => window.setWorkbenchIdentity('   ')")
+    assert result is False
+
+
+# ─── E11-13 closure: bundle/shell sentinel guard (2 tests) ───────────
+
+
+def test_shell_workbench_boots_without_js_errors(demo_server, browser):
+    """E11-13 R1 BLOCKER fix: the shell page must not throw on bundle-only
+    DOM (the sentinel `getElementById("workbench-packet-json")` early-returns
+    before bundle-bound handlers run)."""
+    page, errors = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    page.wait_for_timeout(500)
+    assert errors == [], f"shell boot threw JS errors: {errors}"
+
+
+def test_bundle_workbench_boots_without_js_errors(demo_server, browser):
+    """E11-13: the bundle page must boot fully — sentinel guard does NOT
+    block it because #workbench-packet-json IS present on /workbench/bundle."""
+    page, errors = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench/bundle", wait_until="networkidle")
+    page.wait_for_timeout(500)
+    assert errors == [], f"bundle boot threw JS errors: {errors}"
+
+
+# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
+
+
+def test_workbench_renders_chinese_first_headers_in_dom(demo_server, browser):
+    """E11-15/15b/15c locked HTML-string contracts; this verifies the
+    actual rendered DOM after browser parse + JS boot also delivers
+    Chinese-first across every header surface."""
+    page, _ = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    headers = page.evaluate(
+        """
+        () => ({
+          h1: document.querySelector('.workbench-collab-brand h1')?.textContent.trim(),
+          pageEyebrow: document.querySelector('.workbench-collab-brand .eyebrow')?.textContent.trim(),
+          probeH2: document.querySelector('#workbench-control-panel h2')?.textContent.trim(),
+          docH2: document.querySelector('#workbench-document-panel h2')?.textContent.trim(),
+          circuitH2: document.querySelector('#workbench-circuit-panel h2')?.textContent.trim(),
+          reviewH2: document.querySelector('#annotation-inbox h2')?.textContent.trim(),
+          approvalH2: document.querySelector('#approval-center-title')?.textContent.trim(),
+        })
+        """
+    )
+    # h1: "控制逻辑工作台 · Control Logic Workbench"
+    assert headers["h1"].startswith("控制逻辑工作台"), headers["h1"]
+    assert "Control Logic Workbench" in headers["h1"]
+    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
+    assert headers["pageEyebrow"] == "工程师工作区"
+    # column h2s: Chinese-first per E11-15c
+    assert headers["probeH2"].startswith("探针与追踪"), headers["probeH2"]
+    assert headers["docH2"].startswith("标注与提案"), headers["docH2"]
+    assert headers["circuitH2"].startswith("移交与跟踪"), headers["circuitH2"]
+    # inbox + approval h2: bilingual per E11-15b
+    assert headers["reviewH2"].startswith("审核队列"), headers["reviewH2"]
+    assert headers["approvalH2"].startswith("Kogami 提案审批"), headers["approvalH2"]
+
+
+def test_workbench_buttons_render_chinese_first_in_dom(demo_server, browser):
+    """E11-15b bilingualized 2 control-panel buttons + the Approval Center
+    entry button. Verify rendered text starts with the Chinese half."""
+    page, _ = _new_page_with_error_capture(browser)
+    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
+    button_texts = page.evaluate(
+        """
+        () => Array.from(document.querySelectorAll('button.workbench-toolbar-button'))
+          .map(b => b.textContent.trim())
+        """
+    )
+    # Find the 3 known bilingual buttons by their Chinese prefix.
+    has_load = any(t.startswith("加载当前工单") for t in button_texts)
+    has_snapshot = any(t.startswith("快照当前状态") for t in button_texts)
+    has_approval = any(t.startswith("审批中心") for t in button_texts)
+    assert has_load, f"missing 加载当前工单 button; got: {button_texts}"
+    assert has_snapshot, f"missing 快照当前状态 button; got: {button_texts}"
+    assert has_approval, f"missing 审批中心 button; got: {button_texts}"
diff --git a/tests/test_workbench_js_no_global_shadowing.py b/tests/test_workbench_js_no_global_shadowing.py
new file mode 100644
index 0000000..c96a190
--- /dev/null
+++ b/tests/test_workbench_js_no_global_shadowing.py
@@ -0,0 +1,44 @@
+"""E11-11 — guard against variable shadowing of `document` global in workbench.js.
+
+The renderFingerprintDocumentList loop originally bound the array element
+to a parameter named `document`, which shadowed the global DOM `document`
+and made `document.createElement(...)` call a method on the data object
+instead. Bundle-page boot threw `TypeError: document.createElement is not a function`.
+
+This test is a static-source guard so the regression is caught even when
+the e2e suite is deselected (default `pytest` run).
+"""
+
+from __future__ import annotations
+
+import re
+from pathlib import Path
+
+
+REPO_ROOT = Path(__file__).resolve().parents[1]
+WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
+
+
+def test_no_map_callback_shadows_document_global() -> None:
+    """No `.map((document) => ...)` or similar bindings of the literal
+    name `document` inside an arrow / function body — that would shadow
+    the global `document` and silently break createElement calls."""
+    js = WORKBENCH_JS.read_text(encoding="utf-8")
+    # Catches arrow params: `(document)` `(document,` `, document)` `, document,`
+    pattern = re.compile(r"\((?:[^)]*,\s*)?document(?:\s*,[^)]*)?\)\s*=>")
+    matches = pattern.findall(js)
+    assert not matches, (
+        f"workbench.js contains an arrow callback that shadows global "
+        f"`document`; rename the parameter (e.g. `doc`/`item`). Matches: {matches}"
+    )
+
+
+def test_no_function_param_shadows_document_global() -> None:
+    """No `function name(document)` declarations that shadow the global."""
+    js = WORKBENCH_JS.read_text(encoding="utf-8")
+    pattern = re.compile(r"function\s+\w+\s*\([^)]*\bdocument\b[^)]*\)")
+    matches = pattern.findall(js)
+    assert not matches, (
+        f"workbench.js declares a function parameter named `document` "
+        f"that shadows the global. Matches: {matches}"
+    )

exec
/bin/zsh -lc "sed -n '1,240p' tests/e2e/conftest.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
"""Shared fixtures for P20.0 e2e tests.

Boots well_harness.demo_server as a subprocess on port 8799, waits until
/api/lever-snapshot responds, then yields a base_url to the tests.

All tests in this package must carry @pytest.mark.e2e so the default
pytest run (639 passed) is not affected. Opt-in via: pytest -m e2e
"""
from __future__ import annotations

import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8799
BASE_URL = f"http://127.0.0.1:{PORT}"
READY_TIMEOUT_S = 10.0


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, deadline_s: float) -> bool:
    probe_payload = json.dumps({
        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
        "aircraft_on_ground": True, "reverser_inhibited": False,
        "eec_enable": True, "n1k": 0.5,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
    }).encode()
    start = time.monotonic()
    while time.monotonic() - start < deadline_s:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            c.request("POST", "/api/lever-snapshot", body=probe_payload,
                      headers={"Content-Type": "application/json"})
            resp = c.getresponse()
            resp.read()
            c.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.15)
    return False


def _spawn_server(port: int, home_override: str | None = None) -> subprocess.Popen:
    env = os.environ.copy()
    # Force module discovery via PYTHONPATH so HOME overrides don't break
    # user-site resolution of the editable-installed well_harness package.
    src_path = str(REPO_ROOT / "src")
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing_pp if existing_pp else "")
    if home_override is not None:
        env["HOME"] = home_override
    proc = subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return proc


def _kill_server(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait(timeout=2.0)


@pytest.fixture(scope="session")
def demo_server():
    """Boot demo_server on :8799 for the whole e2e session."""
    if not _port_free(PORT):
        pytest.fail(f"Port {PORT} is already in use; cannot start e2e demo_server")
    proc = _spawn_server(PORT)
    try:
        if not _wait_ready(PORT, READY_TIMEOUT_S):
            _kill_server(proc)
            pytest.fail(f"demo_server did not become ready on :{PORT} within {READY_TIMEOUT_S}s")
        yield BASE_URL
    finally:
        _kill_server(proc)


@pytest.fixture
def api_post() -> Callable[[str, str, dict, float], tuple[int, object]]:
    """Return a helper that POSTs JSON and returns (status, parsed_body)."""
    def _post(base_url: str, path: str, payload: dict, timeout: float = 15.0):
        host = base_url.replace("http://", "").split(":")[0]
        port = int(base_url.rsplit(":", 1)[1])
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        try:
            conn.request(
                "POST", path,
                body=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw
            return resp.status, body
        finally:
            conn.close()
    return _post

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1200,1265p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1200	
  1201	  const chip = createFingerprintChip(autofixAvailable ? "可自动补齐" : "需手工修复", autofixAvailable ? "ready" : "blocked");
  1202	  header.append(titleGroup, chip);
  1203	
  1204	  const meta = document.createElement("div");
  1205	  meta.className = "workbench-schema-card-meta";
  1206	
  1207	  const pathText = document.createElement("span");
  1208	  pathText.textContent = `目标位置：${targetPath || "packet JSON"}`;
  1209	  const effectText = document.createElement("span");
  1210	  effectText.textContent = `修复结果：${expectedEffect || "修复后再重跑验证。"}`;
  1211	  meta.append(pathText, effectText);
  1212	
  1213	  card.append(header, meta);
  1214	  return card;
  1215	}
  1216	
  1217	function renderFingerprintDocumentList(documents, fallbackText) {
  1218	  const container = workbenchElement("workbench-fingerprint-doc-list");
  1219	  if (!documents.length) {
  1220	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1221	    return;
  1222	  }
  1223	
  1224	  container.replaceChildren(...documents.map((doc) => {
  1225	    const card = document.createElement("article");
  1226	    card.className = "workbench-fingerprint-item";
  1227	
  1228	    const header = document.createElement("div");
  1229	    header.className = "workbench-fingerprint-item-header";
  1230	
  1231	    const title = document.createElement("strong");
  1232	    title.className = "workbench-fingerprint-item-title";
  1233	    title.textContent = doc.title || doc.id || "未命名文档";
  1234	
  1235	    const chips = document.createElement("div");
  1236	    chips.className = "workbench-fingerprint-chip-row";
  1237	    chips.append(
  1238	      createFingerprintChip(documentKindLabel(doc.kind), "source"),
  1239	      createFingerprintChip(documentRoleLabel(doc.role), "role"),
  1240	    );
  1241	
  1242	    header.append(title, chips);
  1243	
  1244	    const location = document.createElement("p");
  1245	    location.className = "workbench-fingerprint-item-detail";
  1246	    location.textContent = doc.location || "未提供路径";
  1247	
  1248	    card.append(header, location);
  1249	    return card;
  1250	  }));
  1251	}
  1252	
  1253	function renderFingerprintSignalList(signals, fallbackText) {
  1254	  const container = workbenchElement("workbench-fingerprint-signal-list");
  1255	  if (!signals.length) {
  1256	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1257	    return;
  1258	  }
  1259	
  1260	  container.replaceChildren(...signals.map((signal) => {
  1261	    const card = document.createElement("article");
  1262	    card.className = "workbench-fingerprint-item";
  1263	
  1264	    const header = document.createElement("div");
  1265	    header.className = "workbench-fingerprint-item-header";

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1635,1665p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1635	  if (rerun) {
  1636	    setCurrentWorkbenchRunLabel("Clarification 回填并重跑");
  1637	    setActiveWorkbenchPreset("");
  1638	    await runWorkbenchBundle();
  1639	  }
  1640	}
  1641	
  1642	function renderSystemFingerprintFromPacketPayload(packetPayload, {
  1643	  badgeState = "idle",
  1644	  badgeText = "画像已载入",
  1645	  summary = "样例已经装载。你现在就能先看这套系统的文档来源和关键信号，不用等 bundle 跑完。",
  1646	} = {}) {
  1647	  const documents = Array.isArray(packetPayload.source_documents) ? packetPayload.source_documents : [];
  1648	  const signals = Array.isArray(packetPayload.components) ? packetPayload.components : [];
  1649	  const documentKinds = uniqueValues(documents.map((doc) => doc.kind));
  1650	  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
  1651	  if (documentKinds.length > 1) {
  1652	    sourceModeParts.push("混合来源");
  1653	  }
  1654	  if (documentKinds.includes("pdf")) {
  1655	    sourceModeParts.push("含 PDF");
  1656	  }
  1657	
  1658	  renderSystemFingerprint({
  1659	    badgeState,
  1660	    badgeText,
  1661	    summary,
  1662	    systemId: packetPayload.system_id || "-",
  1663	    objective: packetPayload.objective || "-",
  1664	    sourceMode: sourceModeParts.join(" / "),
  1665	    sourceTruth: packetPayload.source_of_truth || "等待工程真值说明",

exec
/bin/zsh -lc "rg -n \"\\((?:["'^)]*,'"\\s*)?document(?:\\s*,["'^)]*)?'"\\)\\s*=>|function\\s+\\w+\\s*\\(["'^)]*'"\\bdocument\\b["'^)]*'"\\)\" src/well_harness/static" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n \"document\\s*=>|\\(document\\)|,\\s*document\\b|\\bdocument\\b\" src/well_harness/static/workbench.js src/well_harness/static/annotation_overlay.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
 succeeded in 0ms:
src/well_harness/static/annotation_overlay.js:3:  const surfaces = ["control", "document", "circuit"];
src/well_harness/static/annotation_overlay.js:24:    const ticket = document.getElementById("workbench-ticket");
src/well_harness/static/annotation_overlay.js:29:    const selector = document.getElementById("workbench-system-select");
src/well_harness/static/annotation_overlay.js:34:    const identity = document.getElementById("workbench-identity");
src/well_harness/static/annotation_overlay.js:104:    const marker = document.createElement("span");
src/well_harness/static/annotation_overlay.js:118:    const list = document.getElementById("annotation-inbox-list");
src/well_harness/static/annotation_overlay.js:125:    const item = document.createElement("li");
src/well_harness/static/annotation_overlay.js:177:    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
src/well_harness/static/annotation_overlay.js:182:    const status = document.getElementById("workbench-annotation-active-tool");
src/well_harness/static/annotation_overlay.js:190:    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
src/well_harness/static/annotation_overlay.js:193:    document.querySelectorAll("[data-annotation-surface]").forEach((surfaceElement) => {
src/well_harness/static/workbench.js:52:// token (control/document/circuit) into the user-facing engineer-task
src/well_harness/static/workbench.js:57:  document: "Annotate & Propose",
src/well_harness/static/workbench.js:94:  const status = workbenchElement("workbench-document-status");
src/well_harness/static/workbench.js:113:  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
src/well_harness/static/workbench.js:195:  return document.getElementById(id);
src/well_harness/static/workbench.js:332:      const card = document.createElement("article");
src/well_harness/static/workbench.js:334:      const title = document.createElement("strong");
src/well_harness/static/workbench.js:336:      const detail = document.createElement("p");
src/well_harness/static/workbench.js:346:    const card = document.createElement("article");
src/well_harness/static/workbench.js:349:    const meta = document.createElement("div");
src/well_harness/static/workbench.js:352:    const systemChip = document.createElement("span");
src/well_harness/static/workbench.js:356:    const stateChip = document.createElement("span");
src/well_harness/static/workbench.js:361:    const workspaceChip = document.createElement("span");
src/well_harness/static/workbench.js:369:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:375:    const summaryText = document.createElement("p");
src/well_harness/static/workbench.js:378:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:381:    const action = document.createElement("button");
src/well_harness/static/workbench.js:711:      const textarea = document.createElement("textarea");
src/well_harness/static/workbench.js:716:      document.body.append(textarea);
src/well_harness/static/workbench.js:718:      document.execCommand("copy");
src/well_harness/static/workbench.js:867:  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
src/well_harness/static/workbench.js:1089:  const chip = document.createElement("span");
src/well_harness/static/workbench.js:1097:  const card = document.createElement("article");
src/well_harness/static/workbench.js:1100:  const detail = document.createElement("p");
src/well_harness/static/workbench.js:1114:  const card = document.createElement("article");
src/well_harness/static/workbench.js:1117:  const header = document.createElement("div");
src/well_harness/static/workbench.js:1120:  const strong = document.createElement("strong");
src/well_harness/static/workbench.js:1128:  const body = document.createElement("p");
src/well_harness/static/workbench.js:1145:  const card = document.createElement("article");
src/well_harness/static/workbench.js:1148:  const header = document.createElement("div");
src/well_harness/static/workbench.js:1151:  const titleGroup = document.createElement("div");
src/well_harness/static/workbench.js:1152:  const title = document.createElement("strong");
src/well_harness/static/workbench.js:1154:  const promptText = document.createElement("p");
src/well_harness/static/workbench.js:1161:  const meta = document.createElement("div");
src/well_harness/static/workbench.js:1164:  const rationaleText = document.createElement("span");
src/well_harness/static/workbench.js:1166:  const requiredForText = document.createElement("span");
src/well_harness/static/workbench.js:1170:  const textarea = document.createElement("textarea");
src/well_harness/static/workbench.js:1188:  const card = document.createElement("article");
src/well_harness/static/workbench.js:1191:  const header = document.createElement("div");
src/well_harness/static/workbench.js:1194:  const titleGroup = document.createElement("div");
src/well_harness/static/workbench.js:1195:  const strong = document.createElement("strong");
src/well_harness/static/workbench.js:1197:  const body = document.createElement("p");
src/well_harness/static/workbench.js:1204:  const meta = document.createElement("div");
src/well_harness/static/workbench.js:1207:  const pathText = document.createElement("span");
src/well_harness/static/workbench.js:1209:  const effectText = document.createElement("span");
src/well_harness/static/workbench.js:1225:    const card = document.createElement("article");
src/well_harness/static/workbench.js:1228:    const header = document.createElement("div");
src/well_harness/static/workbench.js:1231:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:1235:    const chips = document.createElement("div");
src/well_harness/static/workbench.js:1244:    const location = document.createElement("p");
src/well_harness/static/workbench.js:1261:    const card = document.createElement("article");
src/well_harness/static/workbench.js:1264:    const header = document.createElement("div");
src/well_harness/static/workbench.js:1267:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:1271:    const chips = document.createElement("div");
src/well_harness/static/workbench.js:1281:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:1364:    const emptyCard = document.createElement("article");
src/well_harness/static/workbench.js:1366:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:1368:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:1441:    const emptyCard = document.createElement("article");
src/well_harness/static/workbench.js:1443:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:1445:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:1501:  return [...document.querySelectorAll(".workbench-clarification-answer")]
src/well_harness/static/workbench.js:2000:      const card = document.createElement("article");
src/well_harness/static/workbench.js:2002:      const title = document.createElement("strong");
src/well_harness/static/workbench.js:2004:      const detail = document.createElement("p");
src/well_harness/static/workbench.js:2014:    const card = document.createElement("button");
src/well_harness/static/workbench.js:2025:    const meta = document.createElement("div");
src/well_harness/static/workbench.js:2028:    const systemChip = document.createElement("span");
src/well_harness/static/workbench.js:2032:    const coverageChip = document.createElement("span");
src/well_harness/static/workbench.js:2036:    const timeChip = document.createElement("span");
src/well_harness/static/workbench.js:2042:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:2045:    const summaryText = document.createElement("p");
src/well_harness/static/workbench.js:2048:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:2051:    const action = document.createElement("span");
src/well_harness/static/workbench.js:2138:    const anchor = document.createElement("a");
src/well_harness/static/workbench.js:2393:    const row = document.createElement("div");
src/well_harness/static/workbench.js:2396:    const label = document.createElement("span");
src/well_harness/static/workbench.js:2400:    const value = document.createElement("strong");
src/well_harness/static/workbench.js:2511:      const card = document.createElement("article");
src/well_harness/static/workbench.js:2513:      const title = document.createElement("strong");
src/well_harness/static/workbench.js:2515:      const detail = document.createElement("p");
src/well_harness/static/workbench.js:2525:    const card = document.createElement("button");
src/well_harness/static/workbench.js:2535:    const meta = document.createElement("div");
src/well_harness/static/workbench.js:2538:    const stateChip = document.createElement("span");
src/well_harness/static/workbench.js:2543:    const archiveChip = document.createElement("span");
src/well_harness/static/workbench.js:2548:    const timeChip = document.createElement("span");
src/well_harness/static/workbench.js:2554:    const title = document.createElement("strong");
src/well_harness/static/workbench.js:2557:    const summary = document.createElement("p");
src/well_harness/static/workbench.js:2560:    const detail = document.createElement("p");
src/well_harness/static/workbench.js:2563:    const action = document.createElement("span");
src/well_harness/static/workbench.js:2912:      const li = document.createElement("li");
src/well_harness/static/workbench.js:3665:  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
src/well_harness/static/workbench.js:3740:    document.body.dataset.view = mode;
src/well_harness/static/workbench.js:3772:  const banner = document.getElementById("workbench-trust-banner");
src/well_harness/static/workbench.js:3783:  const chip = document.getElementById("workbench-feedback-mode");
src/well_harness/static/workbench.js:3796:  const chip = document.getElementById("workbench-feedback-mode");
src/well_harness/static/workbench.js:3797:  const banner = document.getElementById("workbench-trust-banner");
src/well_harness/static/workbench.js:3884:  const button = document.querySelector(
src/well_harness/static/workbench.js:3887:  const result = document.querySelector(
src/well_harness/static/workbench.js:3946:  const buttons = document.querySelectorAll(
src/well_harness/static/workbench.js:3965:  const chip = document.getElementById("workbench-identity");
src/well_harness/static/workbench.js:3971:  const entry = document.getElementById("approval-center-entry");
src/well_harness/static/workbench.js:3972:  const panel = document.getElementById("approval-center-panel");
src/well_harness/static/workbench.js:3973:  const affordance = document.getElementById(
src/well_harness/static/workbench.js:3992:  const chip = document.getElementById("workbench-identity");
src/well_harness/static/workbench.js:4021:  const bar = document.getElementById("workbench-state-of-world-bar");
src/well_harness/static/workbench.js:4082:  const onBundlePage = document.getElementById("workbench-packet-json") !== null;

exec
/bin/zsh -lc "rg -n '\\(["'^)]*'"\\bdocument\\b["'^)]*'"\\)\\s*=>' src/well_harness/static/*.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc "rg -n 'function\\s+\\w+\\s*\\(["'^)]*'"\\bdocument\\b["'^)]*'"\\)' src/well_harness/static/*.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc "sed -n '1,240p' tests/e2e/test_wow_a.py && printf '\\n__SPLIT__\\n' && sed -n '1,240p' tests/e2e/test_wow_b.py && printf '\\n__SPLIT__\\n' && sed -n '1,260p' tests/e2e/test_wow_c.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
sed: tests/e2e/test_wow_a.py: No such file or directory

exec
/bin/zsh -lc 'rg --files tests/e2e | sort' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
tests/e2e/__init__.py
tests/e2e/conftest.py
tests/e2e/fixtures/schema_snapshot.json
tests/e2e/test_workbench_js_boot_smoke.py
tests/e2e/test_wow_a_causal_chain.py
tests/e2e/test_wow_b_monte_carlo.py
tests/e2e/test_wow_c_reverse_diagnose.py

codex
The existing e2e files are `test_wow_a_causal_chain.py`, `test_wow_b_monte_carlo.py`, and `test_wow_c_reverse_diagnose.py`, so I’m checking those next against the shared `demo_server` fixture. I’m also re-running the shadow-pattern grep with a narrower shell expression to verify the regex guard isn’t missing another JS file.
exec
/bin/zsh -lc "rg -n '\\(["'^)]*'"\\bdocument\\b["'^)]*'"\\)\\s*=>' src/well_harness/static" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "sed -n '1,240p' tests/e2e/test_wow_a_causal_chain.py && printf '\\n__SPLIT__\\n' && sed -n '1,260p' tests/e2e/test_wow_b_monte_carlo.py && printf '\\n__SPLIT__\\n' && sed -n '1,260p' tests/e2e/test_wow_c_reverse_diagnose.py" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
 succeeded in 0ms:
"""E2E Wow A — causal chain via truth engine (no LLM dependency).

The wow-A story is: given lever inputs that satisfy all deploy preconditions,
the truth engine produces a coherent activated chain (logic1 → logic2 → logic3
→ logic4 → thr_lock) over 19 nodes. LLM only narrates; the contract-bearing
observable is /api/lever-snapshot.

These tests pin the truth-engine contract end-to-end against a live
demo_server on :8799, independent of any MiniMax availability.
"""
from __future__ import annotations

import time

import pytest

EXPECTED_LOGIC_KEYS = {"logic1", "logic2", "logic3", "logic4"}
EXPECTED_NODE_COUNT = 19

# Domain semantics (probed from live demo_server post-a46e4e6 / 2ded020):
#   logic1 = landing-regime detector: RA < threshold AND on_ground AND NOT inhibited
#            AND reverser_not_deployed_eec; the last condition flips False once the
#            plant fully deploys, so logic1 may de-activate during BEAT_DEEP.
#   logic2 = TLS-unlock confirmation
#   logic3 = deep-reverse commit: TRA crossed lock threshold AND logic2 AND SW2 closed
#   logic4 = deploy-confirmed feedback: requires deploy_90_percent_vdt. Under
#           feedback_mode='auto_scrubber' the server-side canonical pullback
#           (demo_server._canonical_pullback_sequence, extended in commit a46e4e6)
#           holds the lever long enough for plant VDT to reach 100%, so the feedback
#           node flips True within a single /api/lever-snapshot call and logic4
#           latches. Under manual_feedback_override mode, logic4 activates only when
#           the caller supplies deploy_position_percent ≥ 90.
#
# Therefore wow-A locks what auto_scrubber delivers from a single POST:
#   - BEAT_EARLY   (tra_deg=-5)  → logic1 + logic2 active; TRA never crosses the
#                                  L3 threshold, so the plant remains at 0%
#                                  deploy and logic3/4 remain inactive.
#   - BEAT_DEEP    (tra_deg=-35) → logic2 + logic3 + logic4 active; the extended
#                                  canonical pullback runs the plant to 100%
#                                  deploy within ~4.4s, latching the full chain.
#                                  logic1 de-activates as reverser_not_deployed_eec
#                                  flips False mid-deploy.
#   - BEAT_BLOCKED (airborne)   → all four inactive (chain broken at logic1).
# These three beats together form the demo's causal-chain narrative.
BEAT_EARLY_PAYLOAD = {
    "tra_deg": -5, "radio_altitude_ft": 2,
    "engine_running": True, "aircraft_on_ground": True,
    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.8,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
}
BEAT_DEEP_PAYLOAD = {
    "tra_deg": -35, "radio_altitude_ft": 2,
    "engine_running": True, "aircraft_on_ground": True,
    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.92,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
}
BEAT_BLOCKED_PAYLOAD = {
    **BEAT_EARLY_PAYLOAD,
    "radio_altitude_ft": 500,
    "aircraft_on_ground": False,
}


@pytest.mark.e2e
def test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields(demo_server, api_post):
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert isinstance(body, dict)
    assert "nodes" in body and isinstance(body["nodes"], list)
    assert len(body["nodes"]) == EXPECTED_NODE_COUNT
    for node in body["nodes"]:
        assert isinstance(node, dict)
        assert set(node.keys()) >= {"id", "state"}
        assert isinstance(node["id"], str) and node["id"]
        assert isinstance(node["state"], str)


@pytest.mark.e2e
def test_wow_a_lever_snapshot_exposes_four_logic_gates(demo_server, api_post):
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert "logic" in body
    logic = body["logic"]
    assert isinstance(logic, dict)
    assert set(logic.keys()) == EXPECTED_LOGIC_KEYS
    for key, gate in logic.items():
        assert isinstance(gate, dict), f"{key} must be a dict"
        assert "active" in gate, f"{key} missing 'active'"
        assert isinstance(gate["active"], bool), f"{key}.active must be bool"


@pytest.mark.e2e
def test_wow_a_beat_early_activates_logic1_and_logic2_only(demo_server, api_post):
    """Demo beat 1: shallow TRA + landing → logic1 + logic2 active, 3/4 pending."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_EARLY_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert active == {"logic1", "logic2"}, (
        f"BEAT_EARLY should activate exactly logic1+logic2, got {active}"
    )


@pytest.mark.e2e
def test_wow_a_beat_deep_activates_logic2_and_logic3(demo_server, api_post):
    """Demo beat 2: deep reverse under auto_scrubber drives the full chain.

    Per commit a46e4e6 ("fix(scrubber): extend canonical pullback hold to let
    plant VDT reach 90%"), feedback_mode='auto_scrubber' with tra_deg below
    logic3_tra_deg_threshold runs the in-server plant to 100% deploy within
    ~4.4s of simulated time. Inside a single /api/lever-snapshot call the
    feedback node deploy_90_percent_vdt flips True and logic4 latches.

    Test name retained for stability; the locked invariants are now:
      (a) at least logic2 + logic3 are active (deep-reverse commit), and
      (b) logic4 is also active under auto_scrubber (post-a46e4e6 reality).
    The "single POST cannot activate logic4 without feedback" invariant is
    a manual-mode concern; see manual_feedback_override path with
    deploy_position_percent < 90 to probe it.
    """
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert {"logic2", "logic3"} <= active, (
        f"BEAT_DEEP should at least activate logic2+logic3, got {active}"
    )
    assert logic["logic4"].get("active") is True, (
        "logic4 must activate under auto_scrubber's extended canonical pullback "
        "(plant VDT reaches 100% within the lever-snapshot window — see "
        "demo_server._canonical_pullback_sequence and commit a46e4e6)"
    )


@pytest.mark.e2e
def test_wow_a_beat_blocked_deactivates_entire_chain(demo_server, api_post):
    """Demo beat 3 (negative control): airborne → entire chain inactive."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_BLOCKED_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert active == set(), (
        f"BEAT_BLOCKED (airborne) should deactivate every gate, got active={active}"
    )


@pytest.mark.e2e
def test_wow_a_truth_engine_is_deterministic(demo_server, api_post):
    """Same lever inputs → byte-identical logic dict across two calls."""
    status1, body1 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    status2, body2 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status1 == 200 and status2 == 200
    assert body1["logic"] == body2["logic"]
    node_state_1 = {n["id"]: n["state"] for n in body1["nodes"]}
    node_state_2 = {n["id"]: n["state"] for n in body2["nodes"]}
    assert node_state_1 == node_state_2


@pytest.mark.e2e
def test_wow_a_response_under_500ms_warm(demo_server, api_post):
    """Rehearsal budget: truth engine must return in <500ms after warmup."""
    api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)  # warmup
    t0 = time.monotonic()
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    elapsed_ms = (time.monotonic() - t0) * 1000
    assert status == 200
    assert elapsed_ms < 500, f"lever-snapshot took {elapsed_ms:.0f}ms (budget 500ms)"


@pytest.mark.e2e
def test_wow_a_lever_snapshot_evidence_field_present(demo_server, api_post):
    """Evidence is the LLM-facing narrative source; must exist for wow A narration."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert "evidence" in body
    assert "plant_state" in body
    assert "outputs" in body

__SPLIT__
"""E2E Wow B — Monte Carlo reliability simulation.

Locks the observable contract of /api/monte-carlo/run against a live
demo_server on :8799: return shape, value ranges, timing budget, and
deterministic seeding.
"""
from __future__ import annotations

import time

import pytest

EXPECTED_TOP_KEYS = {
    "n_trials", "n_failures", "success_rate",
    "mean_cycles_to_failure", "mtbf_cycles", "seed",
    "failure_modes", "sw1_window_crossings_mean", "sw2_window_crossings_mean",
}

# From src/well_harness/monte_carlo_engine.py failure-mode enum
EXPECTED_FAILURE_MODE_KEYS = {
    "ra_sensor_failure", "sw1_missed", "sw2_missed", "tra_stall",
}


def _run(api_post, base_url, n_trials, seed=42):
    return api_post(base_url, "/api/monte-carlo/run",
                    {"system_id": "thrust-reverser", "n_trials": n_trials, "seed": seed})


@pytest.mark.e2e
def test_wow_b_monte_carlo_returns_contract_shape(demo_server, api_post):
    status, body = _run(api_post, demo_server, 1000)
    assert status == 200
    assert isinstance(body, dict)
    missing = EXPECTED_TOP_KEYS - set(body.keys())
    assert not missing, f"monte-carlo response missing keys: {missing}"


@pytest.mark.e2e
def test_wow_b_10k_trials_under_5s(demo_server, api_post):
    """Rehearsal budget: 10k iters must complete well inside the demo window."""
    t0 = time.monotonic()
    status, body = _run(api_post, demo_server, 10000)
    elapsed = time.monotonic() - t0
    assert status == 200
    assert elapsed < 5.0, f"10k MC took {elapsed:.2f}s (budget 5s)"
    assert body["n_trials"] == 10000


@pytest.mark.e2e
def test_wow_b_success_rate_in_unit_interval(demo_server, api_post):
    status, body = _run(api_post, demo_server, 2000)
    assert status == 200
    sr = body["success_rate"]
    assert isinstance(sr, (int, float))
    assert 0.0 <= sr <= 1.0, f"success_rate={sr} not in [0,1]"
    # Consistency: n_failures + successes = n_trials
    assert body["n_failures"] + round(sr * body["n_trials"]) == body["n_trials"] or \
           abs(body["n_failures"] - (1 - sr) * body["n_trials"]) < 1


@pytest.mark.e2e
def test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys(demo_server, api_post):
    status, body = _run(api_post, demo_server, 5000)
    assert status == 200
    modes = body["failure_modes"]
    assert isinstance(modes, dict) and modes
    assert set(modes.keys()) == EXPECTED_FAILURE_MODE_KEYS, (
        f"failure_modes keys changed: {set(modes.keys())}"
    )
    for k, v in modes.items():
        assert isinstance(v, (int, float)), f"{k} must be numeric, got {type(v).__name__}"
        assert v >= 0, f"{k}={v} negative"


@pytest.mark.e2e
def test_wow_b_is_deterministic_under_fixed_seed(demo_server, api_post):
    """Same seed → byte-identical body (critical for rehearsal repeatability)."""
    s1, b1 = _run(api_post, demo_server, 1000, seed=42)
    s2, b2 = _run(api_post, demo_server, 1000, seed=42)
    assert s1 == 200 and s2 == 200
    assert b1 == b2, "Monte Carlo must be deterministic under fixed seed"


@pytest.mark.e2e
def test_wow_b_n_trials_zero_is_clamped_to_min(demo_server, api_post):
    """Known clamp behavior: n_trials=0 is auto-clamped to 1 (graceful, not 400).

    If this changes (e.g. strict 400), update P20.1 contract layer.
    """
    status, body = _run(api_post, demo_server, 0)
    assert status == 200
    assert body["n_trials"] >= 1


@pytest.mark.e2e
def test_wow_b_n_trials_overflow_is_clamped_to_max(demo_server, api_post):
    status, body = _run(api_post, demo_server, 1_500_000)
    assert status == 200
    assert body["n_trials"] <= 10000

__SPLIT__
"""E2E Wow C — reverse diagnosis parameter-combination search.

Locks /api/diagnosis/run contract: valid outcome returns a list of parameter
snapshots that satisfy the target, invalid outcome returns a structured 400.

Note: The current response shape does NOT include probabilities or
suggested_action fields. Those are candidates for P20.1 contract expansion.
"""
from __future__ import annotations

import pytest

VALID_OUTCOMES = {
    "logic3_active", "logic1_active", "thr_lock_active",
    "deploy_confirmed", "tls_unlocked", "pls_unlocked",
}

# Keys guaranteed by ParameterSnapshot dataclass in reverse_diagnosis.py
EXPECTED_RESULT_KEYS = {
    "radio_altitude_ft", "tra_deg",
    "sw1_closed", "sw2_closed",
    "tls_unlocked", "pls_unlocked",
}


@pytest.mark.e2e
def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 10,
    })
    assert status == 200
    assert isinstance(body, dict)
    assert body["outcome"] == "deploy_confirmed"
    assert body["total_combos_found"] >= 1
    assert isinstance(body["results"], list) and len(body["results"]) >= 1
    assert len(body["results"]) <= 10


@pytest.mark.e2e
def test_wow_c_each_result_carries_required_parameter_keys(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 5,
    })
    assert status == 200
    for idx, snap in enumerate(body["results"]):
        assert isinstance(snap, dict), f"result[{idx}] must be a dict"
        missing = EXPECTED_RESULT_KEYS - set(snap.keys())
        assert not missing, f"result[{idx}] missing keys: {missing}"


@pytest.mark.e2e
def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
    """grid_resolution + timestamp must be present (audit trail for rehearsal)."""
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "logic3_active",
    })
    assert status == 200
    assert "grid_resolution" in body
    assert isinstance(body["grid_resolution"], int)
    assert body["grid_resolution"] > 0
    assert "timestamp" in body and isinstance(body["timestamp"], str)


@pytest.mark.e2e
@pytest.mark.parametrize("outcome", sorted(VALID_OUTCOMES))
def test_wow_c_all_valid_outcomes_return_200(demo_server, api_post, outcome):
    """Every documented outcome must be reachable (no regression in enum coverage)."""
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": outcome,
        "max_results": 1,
    })
    assert status == 200
    assert body["outcome"] == outcome


@pytest.mark.e2e
def test_wow_c_invalid_outcome_returns_structured_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "banana_outcome",
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body
    assert "Invalid outcome" in body["error"]
    # Error message must name the valid set so operators can self-recover.
    for valid in VALID_OUTCOMES:
        assert valid in body["error"]


@pytest.mark.e2e
def test_wow_c_missing_outcome_returns_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body


@pytest.mark.e2e
def test_wow_c_max_results_bound_is_respected(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 3,
    })
    assert status == 200
    assert len(body["results"]) <= 3

exec
/bin/zsh -lc "rg -n 'function\\s+\\w+\\s*\\(["'^)]*'"\\bdocument\\b["'^)]*'"\\)' src/well_harness/static" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
codex
I’ve confirmed the fixture-level portability story is mostly good: the server fixture resolves `REPO_ROOT` from `tests/e2e/conftest.py`, so the tests themselves don’t depend on the current shell directory once pytest finds the repo config. Next I’m running the actual suites plus a Playwright console/pageerror probe to see whether there are latent boot-time warnings beyond the original crash.
exec
/bin/zsh -lc "rg -n \"console\\.(error|warn|log)|loadBootstrapPayload|workbench-packet-json|pageerror|addEventListener\\(\\s*['\\\"]error['\\\"]\" src/well_harness/static/workbench.js src/well_harness/static/annotation_overlay.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
src/well_harness/static/workbench.js:437:  const packetEl = workbenchElement("workbench-packet-json");
src/well_harness/static/workbench.js:468:  const packetEl = workbenchElement("workbench-packet-json");
src/well_harness/static/workbench.js:733:    packetJsonText: workbenchElement("workbench-packet-json").value,
src/well_harness/static/workbench.js:880:  workbenchElement("workbench-packet-json").value = prettyJson(payload);
src/well_harness/static/workbench.js:885:  const raw = workbenchElement("workbench-packet-json").value;
src/well_harness/static/workbench.js:1551:    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
src/well_harness/static/workbench.js:1597:    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
src/well_harness/static/workbench.js:1892:    workbenchElement("workbench-packet-json").value = packetJsonText;
src/well_harness/static/workbench.js:2267:    payload = JSON.parse(workbenchElement("workbench-packet-json").value);
src/well_harness/static/workbench.js:3414:    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
src/well_harness/static/workbench.js:3456:    textarea = workbenchElement("workbench-packet-json");
src/well_harness/static/workbench.js:3479:async function loadBootstrapPayload() {
src/well_harness/static/workbench.js:3597:    workbenchElement("workbench-packet-json").value = text;
src/well_harness/static/workbench.js:3685:  workbenchElement("workbench-packet-json").addEventListener("input", () => {
src/well_harness/static/workbench.js:3689:      packetJsonText: workbenchElement("workbench-packet-json").value,
src/well_harness/static/workbench.js:4076:  // NOT contain bundle elements like #workbench-packet-json,
src/well_harness/static/workbench.js:4078:  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
src/well_harness/static/workbench.js:4082:  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
src/well_harness/static/workbench.js:4097:  void loadBootstrapPayload();

exec
/bin/zsh -lc 'pytest tests/test_workbench_js_no_global_shadowing.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'pytest --collect-only -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 167ms:
..                                                                       [100%]
2 passed in 0.01s

 exited 2 in 472ms:
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/bleed_air_adapter.py]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/efds_adapter.py]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/landing_gear_adapter.py]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/bleed_air_intake_packet.py]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[src/well_harness/adapters/landing_gear_intake_packet.py]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[config/hardware/bleed_air_hardware_v1.yaml]
tests/test_adapter_freeze_banner.py::test_frozen_keywords_present[config/hardware/landing_gear_hardware_v1.yaml]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/bleed_air_adapter.py]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/efds_adapter.py]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/landing_gear_adapter.py]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/bleed_air_intake_packet.py]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[src/well_harness/adapters/landing_gear_intake_packet.py]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[config/hardware/bleed_air_hardware_v1.yaml]
tests/test_adapter_freeze_banner.py::test_registry_pointer_present[config/hardware/landing_gear_hardware_v1.yaml]
tests/test_adapter_freeze_banner.py::test_registry_file_exists_and_lists_frozen_systems
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_archive_includes_integrity_field_in_manifest
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_checksum_computed_for_all_present_files
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_corrupted_file_detected_by_integrity_check
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_invalid_sha256_in_integrity_field_reported
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_missing_integrity_field_is_allowed
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_schema_accepts_integrity_field
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_schema_rejects_integrity_with_invalid_hash
tests/test_archive_integrity.py::TestArchiveIntegrityChecksums::test_valid_archive_passes_integrity_validation
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_absolute_manifest_path_outside_archive_root
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_absolute_manifest_path_with_dotdot_escape
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_legitimate_absolute_manifest_inside_root
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_legitimate_relative_manifest_inside_root
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_manifest_archive_dir_absolute_etc
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_manifest_archive_dir_root_slash
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_symlink_within_archive_is_allowed
tests/test_archive_restore_sandbox.py::ArchiveRestoreSandboxTests::test_valid_nested_archive_dir
tests/test_archive_restore_sandbox.py::WorkbenchBundleLayer2Tests::test_archive_dir_root_slash_causes_sandbox_escape_error
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_chart_lanes_match_state_machine_code_space
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_drawer_container_present
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_reset_clears_chart_buffer_and_samples_counter
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_shared_chart_script_is_loaded_before_panel_script
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_tick_throttling_guard_present
tests/test_c919_chart_integration.py::C919ChartDrawerMarkupTests::test_toggle_button_wired
tests/test_c919_chart_integration.py::C919PanelServerAssetRoutingTests::test_panel_server_serves_timeseries_chart_js
tests/test_c919_chart_integration.py::C919PanelServerAssetRoutingTests::test_shared_js_file_exists
tests/test_c919_chart_integration.py::C919PanelScriptSyntaxTests::test_panel_index_iife_parses_as_valid_js
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_etras_fault_routes_into_cmd3
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_fadec_deploy_arrow_not_inside_box
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_key_parameters_rect_tall_enough_for_four_rows
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_no_stray_arrow_at_y_244
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_output_arrow_endpoints_land_on_box_edge
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_reset_feedback_label_outside_s4_box
tests/test_c919_circuit_wires.py::C919CircuitWireTopologyTests::test_tr_wow_lands_at_s1
tests/test_c919_etras_adapter.py::C919ETRASMetadataTests::test_adapter_exposes_expected_metadata
tests/test_c919_etras_adapter.py::C919ETRASMetadataTests::test_load_spec_exposes_schema_aware_payload
tests/test_c919_etras_adapter.py::C919ETRASMetadataTests::test_metadata_serializes_to_schema_aware_payload
tests/test_c919_etras_adapter.py::C919ETRASMetadataTests::test_optional_jsonschema_validates_payloads_when_installed
tests/test_c919_etras_adapter.py::C919ETRASSpecShapeTests::test_fadec_deploy_logic_node_has_six_conditions
tests/test_c919_etras_adapter.py::C919ETRASSpecShapeTests::test_spec_has_acceptance_scenarios_for_landing_and_stow_and_rto_and_inhibited
tests/test_c919_etras_adapter.py::C919ETRASSpecShapeTests::test_spec_has_all_five_fault_modes_by_id
tests/test_c919_etras_adapter.py::C919ETRASSpecShapeTests::test_spec_has_all_five_logic_nodes_by_id
tests/test_c919_etras_adapter.py::C919ETRASSpecShapeTests::test_spec_has_expected_counts
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_both_invalid_returns_conservative_false
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_both_valid_and_agree_false_returns_false
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_both_valid_and_agree_true_returns_true
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_both_valid_and_disagree_returns_conservative_false
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_only_lgcu1_valid_uses_lgcu1
tests/test_c919_etras_adapter.py::MLGWOWRedundancySelectionTests::test_only_lgcu2_valid_uses_lgcu2
tests/test_c919_etras_adapter.py::EICUCMD2TruthTableTests::test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited
tests/test_c919_etras_adapter.py::EICUCMD2TruthTableTests::test_cmd2_blocked_when_both_switches_open
tests/test_c919_etras_adapter.py::EICUCMD2TruthTableTests::test_cmd2_blocked_when_mlg_wow_false
tests/test_c919_etras_adapter.py::EICUCMD2TruthTableTests::test_cmd2_blocked_when_tr_inhibited
tests/test_c919_etras_adapter.py::EICUCMD3FlipflopTests::test_cmd3_holds_when_neither_set_nor_reset
tests/test_c919_etras_adapter.py::EICUCMD3FlipflopTests::test_cmd3_reset_wins_over_set
tests/test_c919_etras_adapter.py::EICUCMD3FlipflopTests::test_cmd3_resets_immediately_on_tr_inhibited
tests/test_c919_etras_adapter.py::EICUCMD3FlipflopTests::test_cmd3_resets_when_stowed_locked_1s_confirmed
tests/test_c919_etras_adapter.py::EICUCMD3FlipflopTests::test_cmd3_sets_when_deploy_entry_conditions_met
tests/test_c919_etras_adapter.py::TRCommand3EnableGatingTests::test_enable_asserts_under_nominal_conditions
tests/test_c919_etras_adapter.py::TRCommand3EnableGatingTests::test_enable_blocked_by_over_temp
tests/test_c919_etras_adapter.py::TRCommand3EnableGatingTests::test_enable_blocked_by_stowed_locked_1s
tests/test_c919_etras_adapter.py::TRCommand3EnableGatingTests::test_enable_blocked_by_tra_at_or_above_fwd_idle
tests/test_c919_etras_adapter.py::TRCommand3EnableGatingTests::test_enable_requires_eicu_cmd3
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_asserts_exactly_at_reverse_idle_boundary
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_asserts_when_all_six_gates_pass
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_engine_not_running
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_lock_unlock_confirm_below_400ms
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_n1k_at_or_above_deploy_limit
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_no_cmd3_enable
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_position_below_80pct
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_position_confirm_below_0_5s
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_tr_wow_false
tests/test_c919_etras_adapter.py::FADECDeployCommandGatingTests::test_deploy_blocked_by_tra_above_reverse_idle
tests/test_c919_etras_adapter.py::FADECStowCommandGatingTests::test_stow_asserts_when_throttle_back_and_n1k_below_limit
tests/test_c919_etras_adapter.py::FADECStowCommandGatingTests::test_stow_blocked_when_engine_not_running
tests/test_c919_etras_adapter.py::FADECStowCommandGatingTests::test_stow_blocked_when_n1k_above_stow_limit
tests/test_c919_etras_adapter.py::FADECStowCommandGatingTests::test_stow_blocked_when_throttle_still_below_fwd_idle
tests/test_c919_etras_adapter.py::FADECStowCommandGatingTests::test_stow_not_active_simultaneously_with_deploy
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_both_sensors_valid_and_unlocked_passes
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_both_tls_sensors_invalid_fails_fallback
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_both_tls_sensors_locked_fails_fallback
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_each_pylon_sees_1of2_passes
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_one_of_two_tls_sensors_invalid_still_passes
tests/test_c919_etras_adapter.py::LockFallbackTruthTableTests::test_one_pylon_fully_failed_blocks_deploy
tests/test_c919_etras_adapter.py::StepTimelineScenarioTests::test_nominal_deploy_reaches_completion
tests/test_c919_etras_adapter.py::StepTimelineScenarioTests::test_rto_rapid_deploy_no_mlg_transition_needed
tests/test_c919_etras_adapter.py::StepTimelineScenarioTests::test_stow_phase_ends_with_latch_reset_and_stow_active
tests/test_c919_etras_adapter.py::FaultInjectionTests::test_fault_e_tras_over_temp_emergency
tests/test_c919_etras_adapter.py::FaultInjectionTests::test_fault_lock_sensor_fallback_failure
tests/test_c919_etras_adapter.py::FaultInjectionTests::test_fault_mlg_wow_redundancy_disagree
tests/test_c919_etras_adapter.py::FaultInjectionTests::test_fault_tr_stuck_deployed
tests/test_c919_etras_adapter.py::FaultInjectionTests::test_fault_vdt_sensor_bias_low
tests/test_c919_etras_adapter.py::IntakePacketTests::test_intake_packet_document_roles
tests/test_c919_etras_adapter.py::IntakePacketTests::test_intake_packet_has_three_source_documents
tests/test_c919_etras_adapter.py::HardwareYAMLSchemaTests::test_hardware_yaml_exists_and_has_expected_shape
tests/test_c919_etras_adapter.py::HardwareYAMLSchemaTests::test_hardware_yaml_system_id_matches_adapter
tests/test_c919_etras_adapter.py::HardwareYAMLSchemaTests::test_hardware_yaml_validates_against_schema_when_jsonschema_installed
tests/test_c919_etras_frozen_v1_integration.py::TestFullHappyPath::test_ground_landing_to_stowed_locked_power_off
tests/test_c919_etras_frozen_v1_integration.py::TestSafetyPreemption::test_inhibit_forces_sf_from_s4
tests/test_c919_etras_frozen_v1_integration.py::TestSafetyPreemption::test_overtemp_forces_sf_and_kills_3phase
tests/test_c919_etras_frozen_v1_integration.py::TestPlsInterlock::test_pls_missing_blocks_s10
tests/test_c919_etras_frozen_v1_integration.py::TestWowConflictSafeSide::test_conflict_keeps_selected_false
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_both_valid_consistent_true
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_both_valid_consistent_false
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_both_valid_conflict_forces_air
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_only_lgcu1_valid
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_only_lgcu2_valid
tests/test_c919_etras_frozen_v1_unit.py::TestWowSelector::test_neither_valid
tests/test_c919_etras_frozen_v1_unit.py::TestTrWowFilter::test_set_after_2p25s
tests/test_c919_etras_frozen_v1_unit.py::TestTrWowFilter::test_reset_after_120ms
tests/test_c919_etras_frozen_v1_unit.py::TestTrWowFilter::test_jitter_holds_state
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2::test_cmd2_active_normal
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2::test_cmd2_blocked_by_inhibit
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2::test_cmd2_blocked_when_80pct
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2::test_cmd2_timer_30s_limit
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2::test_cmd2_timer_reset_on_rising_edge
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_set_by_rising_conditions
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_hold_after_apwtla_drops
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_reset_by_stowed_and_locked
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_reset_by_overtemp
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_airborne_apwtla_fault_does_not_energize_three_phase
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_set_blocked_when_engine_off
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_set_blocked_when_inhibited
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_set_blocked_when_airborne
tests/test_c919_etras_frozen_v1_unit.py::TestCmd3Latch::test_set_allowed_in_trcu_menu_mode_engine_off
tests/test_c919_etras_frozen_v1_unit.py::TestDeploy::test_deploy_happy
tests/test_c919_etras_frozen_v1_unit.py::TestDeploy::test_deploy_blocked_by_inhibit
tests/test_c919_etras_frozen_v1_unit.py::TestDeploy::test_deploy_blocked_without_unlock
tests/test_c919_etras_frozen_v1_unit.py::TestDeploy::test_deploy_blocked_without_tr_wow
tests/test_c919_etras_frozen_v1_unit.py::TestDeploy::test_deploy_blocked_tra_not_past_idle
tests/test_c919_etras_frozen_v1_unit.py::TestStow::test_stow_happy
tests/test_c919_etras_frozen_v1_unit.py::TestStow::test_stow_blocked_by_apwtla_high
tests/test_c919_etras_frozen_v1_unit.py::TestStow::test_stow_blocked_tra_below_zero
tests/test_c919_etras_frozen_v1_unit.py::TestStow::test_stow_blocked_no_3phase
tests/test_c919_etras_frozen_v1_unit.py::TestStow::test_stow_blocked_already_stowed_and_locked
tests/test_c919_etras_frozen_v1_unit.py::TestLockAggregator::test_unlock_confirmed_all_five_locks
tests/test_c919_etras_frozen_v1_unit.py::TestLockAggregator::test_unlock_not_confirmed_when_pls_locked
tests/test_c919_etras_frozen_v1_unit.py::TestLockAggregator::test_unlock_not_confirmed_when_tls_locked
tests/test_c919_etras_frozen_v1_unit.py::TestLockAggregator::test_stowed_and_locked_requires_1s_dwell
tests/test_c919_etras_frozen_v1_unit.py::TestLockAggregator::test_stowed_and_locked_fails_when_pls_missing
tests/test_c919_etras_frozen_v1_unit.py::TestThreePhaseHoldOnThrottleBack::test_three_phase_holds_after_apwtla_drops
tests/test_c919_etras_frozen_v1_unit.py::TestOverTempProtection::test_overtemp_forces_power_off_and_sf
tests/test_c919_etras_frozen_v1_unit.py::TestCmd2DroppedAt80Pct::test_cmd2_off_at_80pct
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_demo_html_links_to_workstation
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_every_visible_svg_node_has_probability_model
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_preset_buttons_match_js_preset_keys
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_css_exists
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_html_exists_and_has_key_section_ids
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_js_exists_and_posts_to_system_snapshot
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_js_reliability_loop_uses_continue_not_return
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_js_renders_sw1_sw2_hint_window
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_js_uses_explicit_sw1_sw2_inputs
tests/test_c919_etras_workstation.py::C919EtrasWorkstationStaticTests::test_workstation_svg_data_nodes_subset_of_adapter_spec
tests/test_c919_etras_workstation.py::C919EtrasWorkstationServerTests::test_assets_serve_200
tests/test_c919_etras_workstation.py::C919EtrasWorkstationServerTests::test_route_serves_html_200
tests/test_c919_etras_workstation.py::C919EtrasWorkstationServerTests::test_system_snapshot_post_landing_deploy_activates_all_four_logic_nodes
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_landing_deploy_reaches_completion
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_lock_fault_does_not_complete_deploy
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_max_reverse_n1k_at_old_buggy_value_breaks_deploy
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_max_reverse_n1k_below_deploy_gate
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_stow_return_blocked_when_n1k_exceeds_stow_limit
tests/test_c919_etras_workstation.py::C919EtrasWorkstationPresetAdapterIntegrationTests::test_preset_stow_return_reaches_stow_command
tests/test_cli.py::StructuredTraceTests::test_events_capture_initial_true_states
tests/test_cli.py::StructuredTraceTests::test_events_capture_key_state_transitions
tests/test_cli.py::StructuredTraceTests::test_trace_rows_include_nested_debug_sections
tests/test_cli.py::CliDebugOutputTests::test_diagnose_view_renders_logic_transition_explain_delta
tests/test_cli.py::CliDebugOutputTests::test_event_view_renders_transition_lines
tests/test_cli.py::CliDebugOutputTests::test_explain_view_renders_failed_threshold_condition
tests/test_cli.py::CliDebugOutputTests::test_json_diagnose_output_is_structured
tests/test_cli.py::CliDebugOutputTests::test_json_events_output_contains_schema_metadata_and_contract_fields
tests/test_cli.py::CliDebugOutputTests::test_json_explain_output_contains_schema_metadata_and_contract_fields
tests/test_cli.py::CliDebugOutputTests::test_json_output_is_deterministic_for_same_command
tests/test_cli.py::CliDebugOutputTests::test_json_outputs_match_contract_assets
tests/test_cli.py::CliDebugOutputTests::test_json_schema_context_field_sets_match_contract_and_runtime_fields
tests/test_cli.py::CliDebugOutputTests::test_json_schema_document_matches_contract_fixtures
tests/test_cli.py::CliDebugOutputTests::test_json_schema_nested_defs_match_contract_representative_fields
tests/test_cli.py::CliDebugOutputTests::test_json_timeline_output_contains_structured_trace
tests/test_cli.py::CliDebugOutputTests::test_optional_jsonschema_validates_contract_payloads_when_installed
tests/test_cli.py::CliDebugOutputTests::test_optional_jsonschema_validates_validation_report_payloads_when_installed
tests/test_cli.py::CliDebugOutputTests::test_optional_jsonschema_validates_validation_schema_checker_report_payloads_when_installed
tests/test_cli.py::CliDebugOutputTests::test_optional_jsonschema_validates_validation_schema_runner_report_payloads_when_installed
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_document_matches_asset
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_standalone_script_forced_skip
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_standalone_script_json_fail_output
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_standalone_script_json_pass_output
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_standalone_script_json_skip_output
tests/test_cli.py::CliDebugOutputTests::test_validation_report_schema_standalone_script_smoke
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_checker_report_schema_document_matches_asset
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_checker_report_schema_standalone_script_forced_skip
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_checker_report_schema_standalone_script_smoke
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_document_matches_asset
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_standalone_script_forced_skip
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_standalone_script_json_fail_output
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_standalone_script_json_pass_output
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_standalone_script_json_skip_output
tests/test_cli.py::CliDebugOutputTests::test_validation_schema_runner_report_schema_standalone_script_smoke
tests/test_cli.py::CliDebugOutputTests::test_validation_script_json_fail_output
tests/test_cli.py::CliDebugOutputTests::test_validation_script_json_outputs_match_contract_asset
tests/test_cli.py::CliDebugOutputTests::test_validation_script_json_pass_output
tests/test_cli.py::CliDebugOutputTests::test_validation_script_json_skip_output
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_cli_failure
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_fail
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_invalid_logic_choice
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_invalid_scenario_choice
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_schema_validation_failure
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_skip
tests/test_cli.py::CliDebugOutputTests::test_validation_script_smoke_forced_unclassified_cli_failure
tests/test_content_type_whitelist.py::TestContentTypeWhitelist::test_application_json_accepted
tests/test_content_type_whitelist.py::TestContentTypeWhitelist::test_form_urlencoded_rejected
tests/test_content_type_whitelist.py::TestContentTypeWhitelist::test_missing_content_type_accepted
tests/test_content_type_whitelist.py::TestContentTypeWhitelist::test_text_plain_rejected
tests/test_control_system_spec_schema.py::ControlSystemSpecSchemaValidationScriptTests::test_control_system_spec_schema_standalone_script_json_pass_output
tests/test_control_system_spec_schema.py::ControlSystemSpecSchemaValidationScriptTests::test_control_system_spec_schema_standalone_script_json_skip_output
tests/test_control_system_spec_schema.py::ControlSystemSpecSchemaValidationScriptTests::test_control_system_spec_schema_standalone_script_smoke
tests/test_controller.py::DeployControllerTests::test_logic1_ra_threshold_is_strictly_below_six_feet
tests/test_controller.py::DeployControllerTests::test_logic1_requires_all_confirmed_conditions
tests/test_controller.py::DeployControllerTests::test_logic3_blocks_commands_when_tra_has_not_reached_threshold
tests/test_controller.py::DeployControllerTests::test_logic3_explain_includes_threshold_details
tests/test_controller.py::DeployControllerTests::test_logic3_requires_n1k_below_deploy_limit
tests/test_controller.py::DeployControllerTests::test_logic3_uses_tls_unlock_and_tra_threshold
tests/test_controller.py::DeployControllerTests::test_logic4_requires_deploy_90_percent_vdt
tests/test_controller.py::SwitchModelTests::test_sw1_sw2_latches_hold_until_reverse_selection_returns_near_zero
tests/test_controller.py::SimplifiedPlantTests::test_deploy_motion_waits_for_all_pls_unlocks_in_first_cut_plant
tests/test_controller.py::SimplifiedPlantTests::test_reverser_not_deployed_eec_is_first_cut_position_simplification
tests/test_controller.py::RunnerTests::test_logic_transition_diagnostics_capture_failed_and_changed_conditions
tests/test_controller.py::RunnerTests::test_logic_transition_diagnostics_include_context_changes
tests/test_controller.py::RunnerTests::test_nominal_deploy_reaches_logic4
tests/test_controller.py::RunnerTests::test_retract_reset_clears_switches_and_logic
tests/test_controller.py::RunnerTests::test_runner_accepts_injected_controller_adapter
tests/test_controller_adapter.py::ControllerAdapterTests::test_controller_truth_adapter_metadata_schema_documents_generated_payload_shape
tests/test_controller_adapter.py::ControllerAdapterTests::test_optional_jsonschema_validates_reference_adapter_metadata_when_installed
tests/test_controller_adapter.py::ControllerAdapterTests::test_reference_adapter_evaluate_snapshot_emits_generic_truth_evaluation
tests/test_controller_adapter.py::ControllerAdapterTests::test_reference_adapter_exposes_reference_truth_metadata
tests/test_controller_adapter.py::ControllerAdapterTests::test_reference_adapter_load_spec_exposes_reference_workbench_spec
tests/test_controller_adapter.py::ControllerAdapterTests::test_reference_adapter_matches_deploy_controller_outputs_and_explain
tests/test_controller_adapter.py::ControllerAdapterTests::test_reference_adapter_metadata_serializes_to_schema_aware_payload
tests/test_controller_truth_adapter_metadata_schema.py::ControllerTruthAdapterMetadataSchemaValidationScriptTests::test_controller_truth_adapter_metadata_schema_standalone_script_json_pass_output
tests/test_controller_truth_adapter_metadata_schema.py::ControllerTruthAdapterMetadataSchemaValidationScriptTests::test_controller_truth_adapter_metadata_schema_standalone_script_json_skip_output
tests/test_controller_truth_adapter_metadata_schema.py::ControllerTruthAdapterMetadataSchemaValidationScriptTests::test_controller_truth_adapter_metadata_schema_standalone_script_smoke
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_additional_properties_still_false
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_governance_fields_are_optional
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_schema_id_version_unchanged
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_status_property_shape
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_top_level_description_codifies_missing_field_semantic
tests/test_controller_truth_metadata_schema_extension.py::JSONSchemaExtensionTests::test_truth_level_property_shape
tests/test_controller_truth_metadata_schema_extension.py::SerializerStripNoneTests::test_explicit_governance_fields_serialized
tests/test_controller_truth_metadata_schema_extension.py::SerializerStripNoneTests::test_none_governance_yields_pre_p42_payload_shape
tests/test_controller_truth_metadata_schema_extension.py::SerializerStripNoneTests::test_partial_governance_strips_only_none_field
tests/test_controller_truth_metadata_schema_extension.py::SchemaEnumRejectionTests::test_bogus_status_rejected
tests/test_controller_truth_metadata_schema_extension.py::SchemaEnumRejectionTests::test_bogus_truth_level_rejected
tests/test_controller_truth_metadata_schema_extension.py::SchemaEnumRejectionTests::test_valid_governance_values_pass
tests/test_controller_truth_metadata_schema_extension.py::GeneratorTemplateP42DefaultsTests::test_central_import_preserved
tests/test_controller_truth_metadata_schema_extension.py::GeneratorTemplateP42DefaultsTests::test_emitted_metadata_declares_P42_defaults
tests/test_controller_truth_metadata_schema_extension.py::GeneratorTemplateP42DefaultsTests::test_emitted_metadata_is_not_In_use_by_default
tests/test_controller_truth_metadata_schema_extension.py::GeneratorTemplateP42DefaultsTests::test_no_shadow_ControllerTruthMetadata
tests/test_controller_truth_metadata_schema_extension.py::GeneratorTemplateP42DefaultsTests::test_no_shadow_GenericTruthEvaluation
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_540v_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_does_not_break_existing_throttle_lock_diagnosis_prompt
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_logic1_uses_explain_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_logic2_uses_explain_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_logic3_uses_explain_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_logic4_uses_explain_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_sw1_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_sw2_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_thr_lock_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_tls115_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_tls_unlocked_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_blocked_state_vdt90_uses_pre_trigger_checkpoint_comparison
tests/test_demo.py::DemoIntentLayerTests::test_demo_answer_schema_standalone_script_forced_skip
tests/test_demo.py::DemoIntentLayerTests::test_demo_answer_schema_standalone_script_json_forced_skip_output
tests/test_demo.py::DemoIntentLayerTests::test_demo_answer_schema_standalone_script_json_pass_output
tests/test_demo.py::DemoIntentLayerTests::test_demo_answer_schema_standalone_script_smoke
tests/test_demo.py::DemoIntentLayerTests::test_demo_answers_match_lightweight_fixture_contract
tests/test_demo.py::DemoIntentLayerTests::test_demo_cli_json_bridge_summary_output
tests/test_demo.py::DemoIntentLayerTests::test_demo_cli_json_logic4_blocked_state_output
tests/test_demo.py::DemoIntentLayerTests::test_demo_cli_renders_structured_answer
tests/test_demo.py::DemoIntentLayerTests::test_demo_html_slim_workstation_structure
tests/test_demo.py::DemoIntentLayerTests::test_demo_js_posts_to_lever_snapshot
tests/test_demo.py::DemoIntentLayerTests::test_demo_json_output_schema_document_matches_fixture_contract
tests/test_demo.py::DemoIntentLayerTests::test_demo_json_outputs_match_lightweight_fixture_contract
tests/test_demo.py::DemoIntentLayerTests::test_demo_path_smoke_script_json_output
tests/test_demo.py::DemoIntentLayerTests::test_demo_path_smoke_script_smoke
tests/test_demo.py::DemoIntentLayerTests::test_demo_presenter_talk_track_covers_core_flow
tests/test_demo.py::DemoIntentLayerTests::test_demo_presenter_talk_track_includes_readiness_run_card
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_accepts_extended_lever_snapshot_conditions
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_accepts_manual_feedback_override_for_vdt90_and_logic4
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_can_apply_safe_schema_repairs_for_workbench_packet
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_can_restore_workbench_archive_payload
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_missing_prompt_returns_readable_error_json
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_monitor_timeline_matches_key_transition_times
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_rejects_invalid_extended_lever_snapshot_input
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_returns_demo_json_payload
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_returns_lever_snapshot_payload_for_key_tra_values
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_returns_monitor_timeline_payload
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_returns_workbench_bootstrap_payload
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_returns_workbench_bundle_and_archive_payload
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_unlocks_deep_range_once_l4_boundary_probe_is_ready
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_bootstrap_lists_recent_workbench_archives
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_help_documents_optional_open_affordance
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_index_html_contains_all_six_surfaces
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_main_open_affordance_uses_helper_and_continues_serving
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_open_browser_helper_reports_failures
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_recent_archives_api_lists_recent_workbench_archives
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_serves_browser_icon_and_manifest_assets
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_serves_static_shell
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_serves_workbench_acceptance_shell
tests/test_demo.py::DemoIntentLayerTests::test_demo_server_unified_nav_css_served
tests/test_demo.py::DemoIntentLayerTests::test_demo_ui_handcheck_script_help_documents_manual_scope
tests/test_demo.py::DemoIntentLayerTests::test_demo_ui_handcheck_script_outputs_manual_checklist
tests/test_demo.py::DemoIntentLayerTests::test_demo_ui_handcheck_script_outputs_presenter_walkthrough
tests/test_demo.py::DemoIntentLayerTests::test_logic3_threshold_change_is_dry_run_only
tests/test_demo.py::DemoIntentLayerTests::test_logic4_throttle_lock_bridge_summary_links_gate_and_release
tests/test_demo.py::DemoIntentLayerTests::test_logic4_throttle_lock_bridge_summary_matches_joint_problem_prompt
tests/test_demo.py::DemoIntentLayerTests::test_node_catalog_covers_expected_chain_nodes
tests/test_demo.py::DemoIntentLayerTests::test_non_logic_trigger_answers_include_specific_upstream_blocker_hints
tests/test_demo.py::DemoIntentLayerTests::test_non_logic_trigger_answers_include_upstream_status_table
tests/test_demo.py::DemoIntentLayerTests::test_optional_jsonschema_validates_demo_json_payloads_when_installed
tests/test_demo.py::DemoIntentLayerTests::test_remaining_command_and_switch_triggers_include_upstream_status_table
tests/test_demo.py::DemoIntentLayerTests::test_throttle_lock_diagnosis_maps_to_logic4_blockers
tests/test_demo.py::DemoIntentLayerTests::test_trigger_logic3_answer_uses_nominal_chain_evidence
tests/test_demo.py::DemoIntentLayerTests::test_trigger_logic4_answer_uses_vdt_and_throttle_lock_evidence
tests/test_demo.py::DemoIntentLayerTests::test_trigger_sw1_answer_uses_catalog_event_evidence
tests/test_demo.py::DemoIntentLayerTests::test_trigger_thr_lock_answer_uses_catalog_event_evidence
tests/test_demo.py::DemoIntentLayerTests::test_trigger_tls_unlocked_answer_uses_catalog_event_evidence
tests/test_demo.py::DemoIntentLayerTests::test_trigger_vdt90_answer_uses_catalog_event_evidence
tests/test_demo.py::DemoIntentLayerTests::test_workbench_bootstrap_explain_runtime_returns_shelved_payload
tests/test_demo.py::DemoIntentLayerTests::test_workbench_js_renders_shelved_explain_runtime_with_distinct_copy
tests/test_demo.py::DemoIntentLayerTests::test_workbench_static_assets_include_explain_runtime_board
tests/test_demo.py::DemoIntentLayerTests::test_workbench_static_assets_include_history_replay_hooks
tests/test_demo.py::DemoIntentLayerTests::test_workbench_static_shell_contains_key_acceptance_sections
tests/test_demo_fault_injection.py::FaultInjectionTests::test_contradiction_in_air_low_altitude
tests/test_demo_fault_injection.py::FaultInjectionTests::test_contradiction_on_ground_high_altitude
tests/test_demo_fault_injection.py::FaultInjectionTests::test_empty_fault_injections_list_is_accepted
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_alias_normalizes_sw1_input_to_sw1
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_invalid_node_returns_400
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_invalid_type_returns_400
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_non_list_returns_400
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_radio_altitude_sensor_zero_unblocks_logic1
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_sw1_stuck_off_overrides_switch
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_sw1_stuck_on_is_recorded_and_forces_switch
tests/test_demo_fault_injection.py::FaultInjectionTests::test_fault_sw2_stuck_off_overrides_switch
tests/test_demo_fault_injection.py::FaultInjectionTests::test_manual_override_bypasses_sw1_gate
tests/test_demo_fault_injection.py::FaultInjectionTests::test_multiple_faults_injected
tests/test_demo_fault_injection.py::FaultInjectionTests::test_n1k_at_exact_limit
tests/test_demo_fault_injection.py::FaultInjectionTests::test_n1k_just_below_limit
tests/test_demo_fault_injection.py::FaultInjectionTests::test_no_fault_injections_excludes_fault_fields
tests/test_demo_fault_injection.py::FaultInjectionTests::test_reverser_inhibited_blocks_upstream
tests/test_demo_fault_injection.py::FaultInjectionTests::test_tra_at_exact_threshold
tests/test_demo_fault_injection.py::FaultInjectionTests::test_tra_just_below_threshold
tests/test_demo_fault_injection.py::FaultInjectionTests::test_unsupported_fault_combination_is_silently_ignored
tests/test_document_intake.py::MixedDocumentIntakeTests::test_apply_safe_schema_repairs_converts_template_to_clarification_only_block
tests/test_document_intake.py::MixedDocumentIntakeTests::test_assess_intake_packet_includes_safe_schema_repair_suggestions_for_template_gaps
tests/test_document_intake.py::MixedDocumentIntakeTests::test_assess_intake_packet_reports_ready_when_answers_are_complete
tests/test_document_intake.py::MixedDocumentIntakeTests::test_assess_intake_packet_surfaces_missing_clarifications_as_blocking_follow_up
tests/test_document_intake.py::MixedDocumentIntakeTests::test_cli_can_export_reference_spec_json
tests/test_document_intake.py::MixedDocumentIntakeTests::test_cli_can_render_intake_template_and_json_assessment
tests/test_document_intake.py::MixedDocumentIntakeTests::test_intake_packet_rejects_unknown_fault_kind
tests/test_document_intake.py::MixedDocumentIntakeTests::test_load_intake_packet_supports_mixed_docs_and_custom_signal_semantics
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_deploy_enable_spine_single_vertical
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_every_gate_has_correctly_labeled_input_row
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_gate_entry_arrows
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_gate_outputs_enter_correct_boxes
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l1_has_four_input_wires
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l2_has_five_input_wires
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l3_fanout_delivers_three_arrows
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l3_gate_output_trunk_to_fanout_junction
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l3_has_six_input_wires
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_l4_has_four_input_wires
tests/test_fantui_circuit_wires.py::FantuiCircuitWireTopologyTests::test_throttle_unlock_connector_lands_on_badge_center
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_log_ring_buffer_caps_at_LOG_CAP
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_plant_advances_deploy_position_under_drive
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_plant_reaches_vdt90_with_enough_ticks
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_record_dict_has_every_field_chart_module_expects
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_reset_clears_time_plant_switches_and_log
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_snapshot_returns_coherent_atomic_state
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_tick_accepts_dt_s_equal_to_one_second_boundary
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_tick_concurrent_writers_and_readers_do_not_raise
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_tick_rejects_non_finite_dt
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_tick_rejects_non_positive_dt
tests/test_fantui_tick_runtime.py::FantuiTickSystemUnitTests::test_tra_sweep_latches_switches_and_activates_gates
tests/test_fantui_tick_runtime.py::ParsePilotInputsTests::test_defaults_fill_in_missing_fields
tests/test_fantui_tick_runtime.py::ParsePilotInputsTests::test_rejects_non_boolean_field
tests/test_fantui_tick_runtime.py::ParsePilotInputsTests::test_rejects_non_numeric_field
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_reset_clears_log
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_state_endpoint_reports_current_snapshot
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_accepts_dt_s_boundary_one
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_endpoint_does_not_touch_existing_lever_snapshot_surface
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_post_advances_state_and_log_accumulates
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_rejects_invalid_input_types
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_rejects_non_finite_dt_via_raw_json
tests/test_fantui_tick_runtime.py::FantuiHttpEndpointTests::test_tick_rejects_out_of_range_dt
tests/test_fantui_tick_runtime.py::StaticAssetRoutingTests::test_demo_html_nav_links_to_fan_console
tests/test_fantui_tick_runtime.py::StaticAssetRoutingTests::test_fan_console_html_is_served
tests/test_fantui_tick_runtime.py::StaticAssetRoutingTests::test_timeseries_chart_js_is_served
tests/test_fantui_tick_runtime.py::TimeseriesChartFileStructureTests::test_buildPayload_filters_non_finite_samples
tests/test_fantui_tick_runtime.py::TimeseriesChartFileStructureTests::test_exports_create_and_buildPayload
tests/test_fantui_tick_runtime.py::TimeseriesChartFileStructureTests::test_supports_payload_shape_fields
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_adapter_backed_fault_diagnosis_reports_landing_gear_divergence
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_cli_fault_diagnosis_outputs_machine_readable_json
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_fault_diagnosis_report_serializes_to_schema_aware_payload
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_fault_diagnosis_reports_blocked_logic_chain
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_fault_diagnosis_schema_documents_generated_payload_shape
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_optional_jsonschema_validates_adapter_backed_fault_diagnosis_when_installed
tests/test_fault_diagnosis.py::FaultDiagnosisTests::test_optional_jsonschema_validates_generated_fault_diagnosis_when_installed
tests/test_fault_diagnosis_schema.py::FaultDiagnosisSchemaValidationScriptTests::test_fault_diagnosis_schema_standalone_script_json_pass_output
tests/test_fault_diagnosis_schema.py::FaultDiagnosisSchemaValidationScriptTests::test_fault_diagnosis_schema_standalone_script_json_skip_output
tests/test_fault_diagnosis_schema.py::FaultDiagnosisSchemaValidationScriptTests::test_fault_diagnosis_schema_standalone_script_smoke
tests/test_fault_taxonomy.py::FaultTaxonomyTests::test_fault_taxonomy_lists_supported_fault_kinds
tests/test_fault_taxonomy.py::FaultTaxonomyTests::test_fault_taxonomy_schema_documents_generated_payload_shape
tests/test_fault_taxonomy.py::FaultTaxonomyTests::test_optional_jsonschema_validates_generated_fault_taxonomy_when_installed
tests/test_fault_taxonomy.py::FaultTaxonomyTests::test_unknown_fault_kind_raises_helpful_error
tests/test_fault_taxonomy_schema.py::FaultTaxonomySchemaValidationScriptTests::test_fault_taxonomy_schema_standalone_script_json_pass_output
tests/test_fault_taxonomy_schema.py::FaultTaxonomySchemaValidationScriptTests::test_fault_taxonomy_schema_standalone_script_json_skip_output
tests/test_fault_taxonomy_schema.py::FaultTaxonomySchemaValidationScriptTests::test_fault_taxonomy_schema_standalone_script_smoke
tests/test_generator_parity.py::GeneratorParityTests::test_aircraft_not_on_ground
tests/test_generator_parity.py::GeneratorParityTests::test_all_cases_via_subTest
tests/test_generator_parity.py::GeneratorParityTests::test_altitude_at_10ft
tests/test_generator_parity.py::GeneratorParityTests::test_altitude_gate_blocked
tests/test_generator_parity.py::GeneratorParityTests::test_baseline_full_chain_minus14
tests/test_generator_parity.py::GeneratorParityTests::test_eec_disabled
tests/test_generator_parity.py::GeneratorParityTests::test_engine_off
tests/test_generator_parity.py::GeneratorParityTests::test_full_activation
tests/test_generator_parity.py::GeneratorParityTests::test_max_n1k_deploy_limit_different
tests/test_generator_parity.py::GeneratorParityTests::test_multiple_blockers_sw1_and_engine
tests/test_generator_parity.py::GeneratorParityTests::test_multiple_blockers_sw1_and_sw2
tests/test_generator_parity.py::GeneratorParityTests::test_n1_at_50_boundary
tests/test_generator_parity.py::GeneratorParityTests::test_n1_at_60_boundary
tests/test_generator_parity.py::GeneratorParityTests::test_n1_below_lower_threshold
tests/test_generator_parity.py::GeneratorParityTests::test_n1_too_high
tests/test_generator_parity.py::GeneratorParityTests::test_pls_not_all_unlocked
tests/test_generator_parity.py::GeneratorParityTests::test_reverser_fully_deployed
tests/test_generator_parity.py::GeneratorParityTests::test_reverser_inhibited
tests/test_generator_parity.py::GeneratorParityTests::test_reverser_not_deployed_eec_false
tests/test_generator_parity.py::GeneratorParityTests::test_sw1_off
tests/test_generator_parity.py::GeneratorParityTests::test_sw1_true_sw2_false
tests/test_generator_parity.py::GeneratorParityTests::test_sw2_off
tests/test_generator_parity.py::GeneratorParityTests::test_tls_locked
tests/test_generator_parity.py::GeneratorParityTests::test_tra_at_exact_threshold_minus14
tests/test_generator_parity.py::GeneratorParityTests::test_tra_at_zero
tests/test_generator_parity.py::GeneratorParityTests::test_tra_below_threshold_minus20
tests/test_generator_parity.py::GeneratorParityTests::test_tra_between_minus14_and_minus11_7
tests/test_generator_parity.py::GeneratorParityTests::test_tra_just_above_minus11_7
tests/test_generator_parity.py::GeneratorParityTests::test_tra_positive_5deg
tests/test_generator_parity.py::GeneratorParityTests::test_vdt_at_90_percent
tests/test_generator_parity.py::GeneratorParityTests::test_vdt_below_90_percent
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_align_snapshot_with_local_phase_fills_missing_phase_from_latest_verified_plan
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_align_snapshot_with_local_phase_overrides_stale_database_live_phase
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_current_review_brief_phase_closeout_mentions_current_phase
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_current_review_brief_skips_review_when_gate_is_not_waiting
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_current_review_brief_targets_failure_triage_when_no_success_cover
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_current_review_brief_targets_stale_gap_adjudication
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_fallback_run_snapshot_carries_forward_stronger_success_summary
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_gate_update_properties_preserves_decision_notes_when_not_activating_gate
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_local_run_snapshot_preserves_stronger_prior_validation_summary
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_local_run_snapshot_uses_repo_docs_without_notion_client
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_build_superseded_gap_fix_plan_marks_duplicates
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_clip_preserves_short_text_and_truncates_long_text
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_derive_compact_success_summary_from_archive_style_text
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_derive_compact_success_summary_from_human_readable_text
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_derive_compact_success_summary_from_text
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_derive_compact_success_summary_from_validation_results
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_derive_compact_success_summary_from_validation_suite_command
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_effective_default_plan_falls_back_to_config_when_no_active_phase_plan_exists
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_effective_default_plan_prefers_latest_local_plan_from_active_phase
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_effective_default_plan_uses_latest_done_phase_when_no_active_phase_exists
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_ensure_live_active_pages_recreates_archived_targets_and_persists_config
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_ensure_live_databases_unarchives_archived_database_blocks
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_compacts_verbose_validation_suite_summaries
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_from_dashboard_page_works_when_subpages_are_unavailable
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_from_pages_uses_active_page_surfaces
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_from_repo_docs_lifts_stronger_archive_summary
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_from_repo_docs_uses_freeze_packet_seed
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_prefers_fresher_local_run_when_newer_than_github
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_fetch_review_snapshot_prefers_github_runs_and_matching_qa
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_aligns_degraded_phase_with_local_roadmap
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_falls_back_to_active_pages_when_db_unshared
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_falls_back_to_repo_docs_on_timeout
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_falls_back_when_db_is_rate_limited
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_reports_restored_databases
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_prepare_opus_review_write_timeout_returns_timeout_fallback_payload
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_run_degrades_successful_ci_when_notion_writeback_fails
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_run_restores_archived_databases_before_writeback
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_run_success_syncs_repo_docs_from_success_snapshot
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_handle_run_timeout_skips_followup_notion_calls_and_still_syncs_repo_docs
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_page_matches_rendered_blocks_detects_link_target_changes
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_page_matches_rendered_blocks_ignores_preserved_child_page_blocks
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_prune_stale_active_sync_page_blocks_removes_only_old_active_surface_children
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_current_review_brief_blocks_include_evidence_mode_fact
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_current_review_brief_blocks_use_database_urls_for_database_refs
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_dashboard_blocks_reflects_live_phase_and_review_state
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_dashboard_blocks_switches_to_dashboard_only_mode_when_active_subpages_are_unavailable
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_freeze_packet_blocks_reflects_live_baseline
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_repo_coordination_plan_markdown_includes_fallback_evidence_note
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_repo_coordination_plan_markdown_reflects_live_baseline
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_repo_coordination_plan_markdown_switches_to_workbench_focus_for_p7
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_repo_dev_handoff_markdown_includes_guardrails
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_status_page_blocks_reflects_live_baseline_and_links
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_render_status_page_blocks_switch_to_workbench_guidance_for_p7
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_active_sync_page_creates_new_page_when_existing_page_archived
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_active_sync_page_falls_back_to_new_page_when_in_place_rewrite_times_out
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_active_sync_page_updates_existing_writable_page_in_place
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_page_body_ignores_archived_delete_errors_from_notion
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_page_body_patches_supported_blocks_in_place_when_structure_matches
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_page_body_preserves_child_pages_and_child_databases
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_replace_page_body_skips_archived_children_when_clearing_page
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_resolve_superseded_failure_gaps_updates_open_matching_rows_only
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_retire_legacy_review_artifacts_archives_only_active_configured_pages
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_retire_legacy_review_artifacts_skips_when_review_is_still_required
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_should_prefer_page_snapshot_when_dashboard_run_is_newer
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_should_prefer_page_snapshot_when_it_matches_current_default_plan
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_should_prefer_snapshot_prefers_higher_phase_when_other_evidence_is_similar
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_should_preserve_prior_success_summary_when_current_run_is_narrower
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_strongest_repo_success_summary_prefers_archive_baseline
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_success_summary_metrics_and_stronger_summary
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_summarize_failed_results
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_summarize_successful_results
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_sync_repo_documents_updates_active_docs_with_managed_sections
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_upsert_dashboard_snapshot_section_replaces_previous_managed_snapshot_only
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_upsert_freeze_packet_snapshot_section_replaces_previous_managed_snapshot_only
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_upsert_managed_markdown_section_replaces_existing_block
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_write_current_opus_review_brief_from_snapshot_aligns_review_target_with_local_phase
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_write_current_opus_review_brief_second_pass_rewrites_cross_links_after_replacements
tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_write_notion_outcome_uses_exact_github_run_url_for_artifacts
tests/test_knowledge_artifact_schema.py::KnowledgeArtifactSchemaValidationScriptTests::test_knowledge_artifact_schema_standalone_script_json_pass_output
tests/test_knowledge_artifact_schema.py::KnowledgeArtifactSchemaValidationScriptTests::test_knowledge_artifact_schema_standalone_script_json_skip_output
tests/test_knowledge_artifact_schema.py::KnowledgeArtifactSchemaValidationScriptTests::test_knowledge_artifact_schema_standalone_script_smoke
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_adapter_backed_knowledge_artifact_preserves_landing_gear_diagnosis_chain
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_build_knowledge_artifact_captures_resolution_and_optimization
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_cli_capture_knowledge_outputs_json_artifact
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_knowledge_artifact_schema_documents_generated_payload_shape
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_knowledge_artifact_serializes_to_schema_aware_payload
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_optional_jsonschema_validates_adapter_backed_knowledge_artifact_when_installed
tests/test_knowledge_capture.py::KnowledgeCaptureTests::test_optional_jsonschema_validates_generated_knowledge_artifact_when_installed
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_blocks_low_pressure_snapshot
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_blocks_when_uplock_is_not_released
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_evaluates_nominal_snapshot
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_exposes_expected_metadata
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_load_spec_exposes_schema_aware_second_system_spec
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_landing_gear_adapter_metadata_serializes_to_schema_aware_payload
tests/test_landing_gear_adapter.py::LandingGearAdapterTests::test_optional_jsonschema_validates_landing_gear_adapter_payloads_when_installed
tests/test_landing_gear_adapter_validation.py::LandingGearAdapterValidationScriptTests::test_landing_gear_adapter_validation_script_json_pass_output
tests/test_landing_gear_adapter_validation.py::LandingGearAdapterValidationScriptTests::test_landing_gear_adapter_validation_script_json_skip_output
tests/test_landing_gear_adapter_validation.py::LandingGearAdapterValidationScriptTests::test_landing_gear_adapter_validation_script_smoke
tests/test_landing_gear_diagnosis_validation.py::LandingGearDiagnosisValidationScriptTests::test_landing_gear_diagnosis_validation_script_json_pass_output
tests/test_landing_gear_diagnosis_validation.py::LandingGearDiagnosisValidationScriptTests::test_landing_gear_diagnosis_validation_script_json_skip_output
tests/test_landing_gear_diagnosis_validation.py::LandingGearDiagnosisValidationScriptTests::test_landing_gear_diagnosis_validation_script_smoke
tests/test_landing_gear_full_pipeline_validation.py::LandingGearFullPipelineValidationTests::test_pipeline_script_bad_format_exits_2
tests/test_landing_gear_full_pipeline_validation.py::LandingGearFullPipelineValidationTests::test_pipeline_script_json_pass_output
tests/test_landing_gear_full_pipeline_validation.py::LandingGearFullPipelineValidationTests::test_pipeline_script_json_skip_output
tests/test_landing_gear_full_pipeline_validation.py::LandingGearFullPipelineValidationTests::test_pipeline_script_smoke_text
tests/test_landing_gear_full_pipeline_validation.py::LandingGearFullPipelineValidationTests::test_pipeline_script_text_mode_output
tests/test_landing_gear_knowledge_validation.py::LandingGearKnowledgeValidationScriptTests::test_landing_gear_knowledge_validation_script_json_pass_output
tests/test_landing_gear_knowledge_validation.py::LandingGearKnowledgeValidationScriptTests::test_landing_gear_knowledge_validation_script_json_skip_output
tests/test_landing_gear_knowledge_validation.py::LandingGearKnowledgeValidationScriptTests::test_landing_gear_knowledge_validation_script_smoke
tests/test_landing_gear_playback_validation.py::LandingGearPlaybackValidationScriptTests::test_landing_gear_playback_validation_script_json_pass_output
tests/test_landing_gear_playback_validation.py::LandingGearPlaybackValidationScriptTests::test_landing_gear_playback_validation_script_json_skip_output
tests/test_landing_gear_playback_validation.py::LandingGearPlaybackValidationScriptTests::test_landing_gear_playback_validation_script_smoke
tests/test_lever_snapshot_boundaries.py::Sw1ThresholdBoundaryTests::test_sw1_does_not_latch_just_above_threshold_minus_1_39
tests/test_lever_snapshot_boundaries.py::Sw1ThresholdBoundaryTests::test_sw1_latches_exactly_at_threshold_minus_1_4
tests/test_lever_snapshot_boundaries.py::Sw1ThresholdBoundaryTests::test_sw1_latches_just_below_threshold_minus_1_41
tests/test_lever_snapshot_boundaries.py::Sw2ThresholdBoundaryTests::test_sw2_does_not_latch_just_above_threshold_minus_4_99
tests/test_lever_snapshot_boundaries.py::Sw2ThresholdBoundaryTests::test_sw2_latches_exactly_at_threshold_minus_5_0
tests/test_lever_snapshot_boundaries.py::Sw2ThresholdBoundaryTests::test_sw2_latches_just_below_threshold_minus_5_01
tests/test_lever_snapshot_boundaries.py::Vdt90CausalGatingTests::test_vdt90_active_when_full_chain_satisfied
tests/test_lever_snapshot_boundaries.py::Vdt90CausalGatingTests::test_vdt90_inactive_below_90_percent_even_when_chain_active
tests/test_lever_snapshot_boundaries.py::Vdt90CausalGatingTests::test_vdt90_inactive_when_l3_blocked_even_at_95_percent
tests/test_lever_snapshot_boundaries.py::TraLockBoundaryTests::test_tra_lock_clamps_and_reports_lock_deg_when_l4_blocked
tests/test_lever_snapshot_boundaries.py::TraLockBoundaryTests::test_tra_lock_opens_deep_range_when_l4_satisfied
tests/test_lever_snapshot_manual_override_guard.py::test_auto_scrubber_unaffected_by_guard
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_with_valid_signoff_returns_200
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_missing_actor_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_missing_ticket_id_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_missing_signoff_object_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_signoff_missing_signed_by_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_manual_override_signoff_ticket_mismatch_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_remediation_message_present_on_409
tests/test_lever_snapshot_manual_override_guard.py::test_actor_signed_by_mismatch_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_400_precedes_409_when_other_fields_malformed
tests/test_lever_snapshot_manual_override_guard.py::test_residual_risk_disclosure_present_on_409
tests/test_lever_snapshot_manual_override_guard.py::test_signoff_non_dict_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_signoff_signed_at_empty_returns_409
tests/test_lever_snapshot_manual_override_guard.py::test_set_vdt_requires_test_probe_acknowledgment
tests/test_lever_snapshot_manual_override_guard.py::test_set_vdt_with_acknowledgment_succeeds
tests/test_metadata_registry_consistency.py::RegistryYamlShapeTests::test_every_entry_declares_required_fields
tests/test_metadata_registry_consistency.py::RegistryYamlShapeTests::test_every_entry_uses_valid_enum_values
tests/test_metadata_registry_consistency.py::RegistryYamlShapeTests::test_metadata_consts_are_unique
tests/test_metadata_registry_consistency.py::RegistryYamlShapeTests::test_system_ids_are_unique
tests/test_metadata_registry_consistency.py::RegistryYamlShapeTests::test_yaml_has_at_least_one_entry
tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_every_runtime_instance_has_a_yaml_entry
tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_every_yaml_entry_has_a_runtime_instance
tests/test_metadata_registry_consistency.py::YamlRuntimeBidirectionalTests::test_yaml_modules_match_known_runtime_modules
tests/test_metadata_registry_consistency.py::ProductionInstancesDeclareGovernanceTests::test_no_production_instance_has_none_status
tests/test_metadata_registry_consistency.py::ProductionInstancesDeclareGovernanceTests::test_no_production_instance_has_none_truth_level
tests/test_metadata_registry_consistency.py::MarkdownTableSanityTests::test_every_yaml_system_id_appears_in_markdown
tests/test_metadata_registry_consistency.py::MarkdownTableSanityTests::test_markdown_table_row_count_matches_yaml
tests/test_nan_inf_clamp.py::TestOptionalRequestFloatNaNInf::test_infinity_returns_error
tests/test_nan_inf_clamp.py::TestOptionalRequestFloatNaNInf::test_nan_returns_error
tests/test_nan_inf_clamp.py::TestOptionalRequestFloatNaNInf::test_negative_infinity_returns_error
tests/test_nan_inf_clamp.py::TestOptionalRequestFloatNaNInf::test_valid_positive_value_works
tests/test_nan_inf_clamp.py::TestOptionalRequestFloatNaNInf::test_zero_uses_default
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_infinity_raises_value_error
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_nan_raises_value_error
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_negative_infinity_raises_value_error
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_negative_value_raises_value_error
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_valid_positive_period_works
tests/test_nan_inf_clamp.py::TestSampleTimesGuard::test_zero_raises_value_error
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunValidSpec::test_exit_zero_with_valid_spec
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunValidSpec::test_output_json_is_well_formed
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunValidSpec::test_all_four_stages_pass
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunValidSpec::test_format_text
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunValidSpec::test_format_json
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunInvalidSpec::test_exit_nonzero_with_invalid_spec
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunInvalidSpec::test_overall_status_is_fail
tests/test_onboard_new_system_dry_run.py::TestOnboardDryRunInvalidSpec::test_spec_validation_errors_are_reported
tests/test_p19_api_endpoints.py::TestDiagnosisRun::test_valid_outcome_returns_200
tests/test_p19_api_endpoints.py::TestDiagnosisRun::test_max_results_limit
tests/test_p19_api_endpoints.py::TestDiagnosisRun::test_invalid_outcome_returns_400
tests/test_p19_api_endpoints.py::TestDiagnosisRun::test_pls_unlocked_satisfiable
tests/test_p19_api_endpoints.py::TestDiagnosisRun::test_empty_body_default
tests/test_p19_api_endpoints.py::TestMonteCarloRun::test_valid_run_returns_200
tests/test_p19_api_endpoints.py::TestMonteCarloRun::test_seed_reproducibility
tests/test_p19_api_endpoints.py::TestMonteCarloRun::test_n_trials_must_be_integer
tests/test_p19_api_endpoints.py::TestMonteCarloRun::test_n_trials_capped_at_10000
tests/test_p19_api_endpoints.py::TestMonteCarloRun::test_seed_must_be_integer
tests/test_p19_api_endpoints.py::TestHardwareSchema::test_returns_200
tests/test_p19_api_endpoints.py::TestHardwareSchema::test_returns_json_dict
tests/test_p19_api_endpoints.py::TestHardwareSchema::test_has_expected_top_level_keys
tests/test_p19_api_endpoints.py::TestHardwareSchema::test_logic_thresholds_are_floats
tests/test_p19_api_endpoints.py::TestHardwareSchema::test_switch_windows_present
tests/test_p19_api_endpoints.py::TestSensitivitySweep::test_returns_200_with_default_grid
tests/test_p19_api_endpoints.py::TestSensitivitySweep::test_rejects_unsupported_system
tests/test_p19_api_multisystem.py::TestDiagnosisSystemId::test_thrust_reverser_returns_200
tests/test_p19_api_multisystem.py::TestDiagnosisSystemId::test_landing_gear_returns_400_not_supported
tests/test_p19_api_multisystem.py::TestDiagnosisSystemId::test_bleed_air_returns_400_not_supported
tests/test_p19_api_multisystem.py::TestDiagnosisSystemId::test_invalid_system_returns_400
tests/test_p19_api_multisystem.py::TestDiagnosisSystemId::test_default_is_thrust_reverser
tests/test_p19_api_multisystem.py::TestMonteCarloSystemId::test_thrust_reverser_returns_200
tests/test_p19_api_multisystem.py::TestMonteCarloSystemId::test_landing_gear_returns_400_not_supported
tests/test_p19_api_multisystem.py::TestMonteCarloSystemId::test_bleed_air_returns_400_not_supported
tests/test_p19_api_multisystem.py::TestMonteCarloSystemId::test_invalid_system_returns_400
tests/test_p19_api_multisystem.py::TestMonteCarloSystemId::test_default_is_thrust_reverser
tests/test_p19_api_multisystem.py::TestHardwareSchemaSystemId::test_landing_gear_returns_200
tests/test_p19_api_multisystem.py::TestHardwareSchemaSystemId::test_bleed_air_returns_200
tests/test_p19_api_multisystem.py::TestHardwareSchemaSystemId::test_thrust_reverser_returns_200
tests/test_p19_api_multisystem.py::TestHardwareSchemaSystemId::test_invalid_system_returns_400
tests/test_p19_api_multisystem.py::TestHardwareSchemaSystemId::test_default_is_thrust_reverser
tests/test_p43_authority_contract.py::TestR1BackendNoDraftWrite::test_r1_demo_server_no_draft_key
tests/test_p43_authority_contract.py::TestR1BackendNoDraftWrite::test_r1_workbench_bundle_no_draft_emit
tests/test_p43_authority_contract.py::TestR2FinalApproveNoDraftRead::test_r2_final_approve_handler_exists
tests/test_p43_authority_contract.py::TestR2FinalApproveNoDraftRead::test_r2_handler_no_draft_getitem
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_assign_frozen_spec_declared
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_deepfreeze_declared
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_bare_frozenspec_assignment
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_alias_mutate_patterns
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_draft_origin
tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_deepfreeze_called_in_assign
tests/test_p43_authority_contract.py::TestR4GeneratorFrozenOnly::test_r4_generator_exists
tests/test_p43_authority_contract.py::TestR4GeneratorFrozenOnly::test_r4_generator_no_draft_read
tests/test_p43_authority_contract.py::TestR5ValidatorSingleton::test_r5_singleton_declared
tests/test_p43_authority_contract.py::TestR6LifecycleBoundary::test_r6_final_approve_removes_draft
tests/test_p43_authority_contract.py::TestR6LifecycleBoundary::test_r6_archive_bundle_excludes_draft
tests/test_p43_authority_contract.py::TestR6LifecycleBoundary::test_r6_bundle_no_draft_substring
tests/test_p43_authority_contract.py::TestAuthorityContractTool::test_tool_exists_and_is_runnable
tests/test_p43_authority_contract.py::TestAuthorityContractTool::test_tool_covers_all_six_rules
tests/test_p43_authority_contract.py::TestAuthorityContractTool::test_tool_r1_returns_pass
tests/test_p43_authority_contract.py::TestAuthorityContractTool::test_tool_r6b_returns_pass
tests/test_pitch_citations.py::test_pitch_materials_exist
tests/test_pitch_citations.py::test_pitch_citations_resolve
tests/test_pitch_citations.py::test_placeholder_skip_works
tests/test_pitch_citations.py::test_real_path_extraction_works
tests/test_playback_trace_schema.py::PlaybackTraceSchemaValidationScriptTests::test_playback_trace_schema_standalone_script_json_pass_output
tests/test_playback_trace_schema.py::PlaybackTraceSchemaValidationScriptTests::test_playback_trace_schema_standalone_script_json_skip_output
tests/test_playback_trace_schema.py::PlaybackTraceSchemaValidationScriptTests::test_playback_trace_schema_standalone_script_smoke
tests/test_pr_close_loop.py::test_extract_changed_files_from_unified_diff
tests/test_pr_close_loop.py::test_pr_review_accepts_in_scope_diff
tests/test_pr_close_loop.py::test_pr_review_rejects_out_of_scope_diff
tests/test_pr_close_loop.py::test_merge_close_stub_appends_pr_and_ticket_events
tests/test_proposal_schema_store.py::test_annotation_proposal_schema_defines_tools_and_surfaces
tests/test_proposal_schema_store.py::test_proposal_store_persists_valid_annotation_proposal
tests/test_proposal_schema_store.py::test_proposal_validation_rejects_unknown_tool_and_unsafe_ids
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_adapter_backed_playback_supports_discrete_landing_gear_states
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_build_playback_report_compiles_signal_and_logic_series
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_cli_playback_outputs_machine_readable_json
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_module_entrypoint_emits_playback_text
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_optional_jsonschema_validates_adapter_backed_landing_gear_playback_when_installed
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_optional_jsonschema_validates_generated_playback_trace_when_installed
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_playback_report_serializes_to_schema_aware_payload
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_playback_trace_schema_documents_generated_payload_shape
tests/test_scenario_playback.py::ScenarioPlaybackTests::test_reference_adapter_backed_playback_accepts_percent_completion_conditions
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_cli_second_system_smoke_outputs_machine_readable_json
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_optional_jsonschema_validates_generated_second_system_smoke_when_installed
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_second_system_smoke_report_can_still_run_legacy_intake_packet_path
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_second_system_smoke_report_defaults_to_adapter_backed_runtime_chain
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_second_system_smoke_report_serializes_default_payload_to_schema_aware_json
tests/test_second_system_smoke.py::SecondSystemSmokeTests::test_second_system_smoke_schema_documents_generated_payload_shape
tests/test_second_system_smoke_schema.py::SecondSystemSmokeSchemaValidationScriptTests::test_second_system_smoke_schema_standalone_script_json_pass_output
tests/test_second_system_smoke_schema.py::SecondSystemSmokeSchemaValidationScriptTests::test_second_system_smoke_schema_standalone_script_json_skip_output
tests/test_second_system_smoke_schema.py::SecondSystemSmokeSchemaValidationScriptTests::test_second_system_smoke_schema_standalone_script_smoke
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_control_system_spec_schema_documents_generated_payload_shape
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_current_reference_spec_captures_required_components
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_current_reference_spec_exposes_logic_fault_and_acceptance_layers
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_optional_jsonschema_validates_generated_control_system_spec_when_installed
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_workbench_spec_from_dict_round_trips_reference_payload
tests/test_system_spec.py::ControlSystemWorkbenchSpecTests::test_workbench_spec_serializes_to_json_safe_payload
tests/test_thrust_reverser_intake_packet.py::test_thrust_reverser_intake_packet_imports_clean
tests/test_thrust_reverser_intake_packet.py::test_thrust_reverser_intake_packet_matches_d1a_lean
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_full_deploy_stow_cycle_reaches_s10
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_logic_states_cmd3_blocked_in_menu_mode_with_inhibit
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_nominal_deploy_fixture_reaches_fadec_deploy
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_outcome_extra_populated_for_c919
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_over_temp_fault_aborts_deploy_mid_cycle
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_tr_inhibited_fixture_blocks_everything
tests/test_timeline_c919_etras.py::C919ExecutorDirectTests::test_unknown_fault_raises
tests/test_timeline_c919_etras.py::C919TimelineApiTests::test_nominal_deploy_api_roundtrip
tests/test_timeline_c919_etras.py::C919TimelineApiTests::test_rejects_fantui_system
tests/test_timeline_c919_etras.py::C919TimelineApiTests::test_unknown_fault_returns_400
tests/test_timeline_engine.py::ValidatorTests::test_accepts_minimal_timeline
tests/test_timeline_engine.py::ValidatorTests::test_rejects_nonpositive_step_s
tests/test_timeline_engine.py::ValidatorTests::test_rejects_ramp_without_duration
tests/test_timeline_engine.py::ValidatorTests::test_rejects_unknown_system
tests/test_timeline_engine.py::ValidatorTests::test_sorts_events_by_time
tests/test_timeline_engine.py::FaultScheduleTests::test_compile_active_faults_half_open
tests/test_timeline_engine.py::FaultScheduleTests::test_inject_then_clear_half_open
tests/test_timeline_engine.py::FaultScheduleTests::test_inject_with_duration
tests/test_timeline_engine.py::FaultScheduleTests::test_inject_without_clear_holds_until_end
tests/test_timeline_engine.py::PlayerTickOrderTests::test_fault_half_open_reaches_executor
tests/test_timeline_engine.py::PlayerTickOrderTests::test_set_input_fires_before_executor_tick
tests/test_timeline_engine.py::PlayerRampTests::test_ramp_input_linearly_interpolates
tests/test_timeline_engine.py::PlayerAssertionTests::test_assertion_on_logic_state_records_pass_and_fail
tests/test_timeline_engine.py::PlayerOutcomeTests::test_executor_system_id_mismatch_raises
tests/test_timeline_engine.py::PlayerOutcomeTests::test_failure_cascade_records_first_broken_gate
tests/test_timeline_engine.py::PlayerOutcomeTests::test_transitions_compression
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_logic_stuck_false_marks_gate_blocked_not_idle
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_nominal_deploy_records_no_false_cascade
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_nominal_landing_timeline_reaches_l4
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_scrubber_and_timeline_agree_on_final_state
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_sw1_stuck_at_touchdown_blocks_chain
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_time_varying_fault_cleared_mid_sim
tests/test_timeline_fantui.py::FantuiExecutorDirectTests::test_unknown_fault_id_raises
tests/test_timeline_fantui.py::FantuiTimelineApiTests::test_nominal_landing_api_roundtrip
tests/test_timeline_fantui.py::FantuiTimelineApiTests::test_rejects_invalid_timeline
tests/test_timeline_fantui.py::FantuiTimelineApiTests::test_rejects_non_fantui_system
tests/test_timeline_fantui.py::FantuiTimelineApiTests::test_unknown_fault_returns_400_invalid_timeline
tests/test_timeline_sim_page.py::TimelineSimPageTests::test_all_four_demo_presets_present
tests/test_timeline_sim_page.py::TimelineSimPageTests::test_page_routes_c919_to_9191
tests/test_timeline_sim_page.py::TimelineSimPageTests::test_page_served
tests/test_timeline_sim_page.py::TimelineSimPageTests::test_static_file_exists_on_disk
tests/test_two_system_runtime_comparison.py::TwoSystemRuntimeComparisonTests::test_build_two_system_runtime_comparison_report_proves_both_systems_share_runtime_chain
tests/test_two_system_runtime_comparison.py::TwoSystemRuntimeComparisonTests::test_cli_two_system_runtime_comparison_outputs_machine_readable_json
tests/test_two_system_runtime_comparison.py::TwoSystemRuntimeComparisonTests::test_optional_jsonschema_validates_runtime_comparison_payload_when_installed
tests/test_two_system_runtime_comparison.py::TwoSystemRuntimeComparisonTests::test_runtime_comparison_report_serializes_to_schema_aware_payload
tests/test_two_system_runtime_comparison.py::TwoSystemRuntimeComparisonTests::test_runtime_comparison_schema_documents_generated_payload_shape
tests/test_two_system_runtime_comparison_schema.py::TwoSystemRuntimeComparisonSchemaValidationScriptTests::test_two_system_runtime_comparison_script_json_pass_output
tests/test_two_system_runtime_comparison_schema.py::TwoSystemRuntimeComparisonSchemaValidationScriptTests::test_two_system_runtime_comparison_script_json_skip_output
tests/test_two_system_runtime_comparison_schema.py::TwoSystemRuntimeComparisonSchemaValidationScriptTests::test_two_system_runtime_comparison_script_smoke
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_control_plane_fails_when_dashboard_is_archived
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_control_plane_passes_when_pages_and_databases_are_accessible
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_control_plane_reports_archived_databases_as_degraded_not_failure
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_control_plane_reports_dashboard_only_degraded_mode_for_archived_active_pages
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_control_plane_skips_without_token
tests/test_validate_notion_control_plane.py::ValidateNotionControlPlaneTests::test_validate_required_keys_flags_missing_entries
tests/test_validation_suite.py::ValidationSuiteTests::test_build_child_env_prepends_repo_src_to_pythonpath
tests/test_validation_suite.py::ValidationSuiteTests::test_build_default_commands_contains_expected_checks
tests/test_validation_suite.py::ValidationSuiteTests::test_build_default_commands_uses_stable_python3_label_by_default
tests/test_validation_suite.py::ValidationSuiteTests::test_run_suite_reports_success_when_all_checks_pass
tests/test_validation_suite.py::ValidationSuiteTests::test_run_suite_stops_after_first_failure
tests/test_workbench_annotation_static.py::test_workbench_loads_annotation_overlay_and_four_tools
tests/test_workbench_annotation_static.py::test_workbench_exposes_three_annotation_surfaces
tests/test_workbench_annotation_static.py::test_annotation_overlay_js_exports_bootstrap_and_draft_contracts
tests/test_workbench_annotation_vocab.py::test_workbench_html_carries_domain_label[>\u6807\u6ce8<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_carries_domain_label[>\u6807\u8bb0\u4fe1\u53f7<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_carries_domain_label[>\u5708\u9009 logic gate<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_carries_domain_label[>\u5173\u8054 spec<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_carries_domain_label[>\u5f15\u7528 requirement \u6bb5<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_default_active_tool_uses_domain_label
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[>Annotation<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[>Point<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[>Area<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[>Link<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[>Text Range<]
tests/test_workbench_annotation_vocab.py::test_workbench_html_drops_stale_generic_label[Point tool active]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[data-annotation-tool="point"]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[data-annotation-tool="area"]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[data-annotation-tool="link"]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[data-annotation-tool="text-range"]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[id="workbench-annotation-toolbar"]
tests/test_workbench_annotation_vocab.py::test_workbench_html_preserves_stable_tool_anchor[id="workbench-annotation-active-tool"]
tests/test_workbench_annotation_vocab.py::test_annotation_overlay_uses_tool_domain_label_map
tests/test_workbench_annotation_vocab.py::test_workbench_route_serves_relabel
tests/test_workbench_approval_center.py::test_approval_center_submits_proposal_and_appends_audit_event
tests/test_workbench_approval_center.py::test_approval_center_rejects_non_kogami_triage
tests/test_workbench_approval_center.py::test_approval_center_accepts_and_rejects_with_hash_chain
tests/test_workbench_approval_center.py::test_workbench_static_approval_center_exposes_triage_lanes
tests/test_workbench_archive_manifest_schema.py::WorkbenchArchiveManifestSchemaValidationScriptTests::test_workbench_archive_manifest_schema_standalone_script_json_pass_output
tests/test_workbench_archive_manifest_schema.py::WorkbenchArchiveManifestSchemaValidationScriptTests::test_workbench_archive_manifest_schema_standalone_script_json_skip_output
tests/test_workbench_archive_manifest_schema.py::WorkbenchArchiveManifestSchemaValidationScriptTests::test_workbench_archive_manifest_schema_standalone_script_smoke
tests/test_workbench_authority_banner.py::test_workbench_html_has_authority_banner
tests/test_workbench_authority_banner.py::test_workbench_html_banner_carries_canonical_copy[\U0001f512]
tests/test_workbench_authority_banner.py::test_workbench_html_banner_carries_canonical_copy[Truth Engine \u2014 Read Only]
tests/test_workbench_authority_banner.py::test_workbench_html_banner_carries_canonical_copy[Propose \u4e0d\u4fee\u6539]
tests/test_workbench_authority_banner.py::test_workbench_html_banner_carries_canonical_copy[\u5de5\u7a0b\u5e08\u53ea\u80fd\u63d0\u4ea4 ticket / proposal]
tests/test_workbench_authority_banner.py::test_workbench_html_banner_carries_canonical_copy[v6.1 \u7ea2\u7ebf\u6761\u6b3e]
tests/test_workbench_authority_banner.py::test_workbench_html_banner_links_to_v61_redline_route
tests/test_workbench_authority_banner.py::test_v61_redline_route_returns_200_text
tests/test_workbench_authority_banner.py::test_v61_redline_excerpt_carries_truth_engine_paths
tests/test_workbench_authority_banner.py::test_v61_redline_route_alias_with_extension
tests/test_workbench_authority_banner.py::test_workbench_route_serves_authority_banner
tests/test_workbench_authority_banner.py::test_workbench_banner_appears_before_collab_grid
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_manifest_remains_valid_after_archive_directory_is_moved
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_manifest_resolves_files_and_workspace_metadata_after_move
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_manifest_schema_documents_generated_manifest_shape
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_manifest_validation_reports_invalid_self_check_metadata
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_manifest_validation_reports_missing_core_file
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_readme_self_check_command_runs_from_archive_directory
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_workbench_bundle_avoids_name_collisions_within_same_second
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_workbench_bundle_can_capture_browser_handoff_snapshot
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_archive_workbench_bundle_can_capture_browser_workspace_snapshot
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_blocked_workbench_bundle_serializes_to_schema_aware_payload
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_build_workbench_bundle_returns_clarification_follow_up_for_blocked_packet
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_build_workbench_bundle_stitches_ready_chain_into_single_bundle
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_archive_manifest_accepts_archive_directory_and_prints_restore_targets
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_archive_manifest_reports_invalid_generated_archive
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_archive_manifest_validates_generated_archive
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_bundle_can_archive_blocked_follow_up_bundle
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_bundle_outputs_follow_up_for_blocked_packet
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_cli_bundle_outputs_json_for_ready_packet
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_load_workbench_archive_bundle_payload_returns_bundle_json_object
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_load_workbench_archive_manifest_rejects_malformed_manifest
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_load_workbench_archive_restore_payload_reopens_moved_archive
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_optional_jsonschema_validates_generated_archive_manifest_when_installed
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_optional_jsonschema_validates_generated_workbench_bundles_when_installed
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_render_workbench_bundle_markdown_and_archive_capture_ready_bundle
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_render_workbench_bundle_text_summarizes_blocked_and_ready_states
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_workbench_bundle_schema_documents_generated_payload_shape
tests/test_workbench_bundle.py::WorkbenchBundleTests::test_workbench_bundle_serializes_to_schema_aware_payload
tests/test_workbench_bundle_schema.py::WorkbenchBundleSchemaValidationScriptTests::test_workbench_bundle_schema_standalone_script_json_pass_output
tests/test_workbench_bundle_schema.py::WorkbenchBundleSchemaValidationScriptTests::test_workbench_bundle_schema_standalone_script_json_skip_output
tests/test_workbench_bundle_schema.py::WorkbenchBundleSchemaValidationScriptTests::test_workbench_bundle_schema_standalone_script_smoke
tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u63a2\u9488\u4e0e\u8ffd\u8e2a \xb7 Probe &amp; Trace</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u6807\u6ce8\u4e0e\u63d0\u6848 \xb7 Annotate &amp; Propose</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_column_h2_is_chinese_first[<h2>\u79fb\u4ea4\u4e0e\u8ddf\u8e2a \xb7 Hand off &amp; Track</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Probe &amp; Trace \xb7 \u63a2\u9488\u4e0e\u8ffd\u8e2a</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Annotate &amp; Propose \xb7 \u6807\u6ce8\u4e0e\u63d0\u6848</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_stale_english_first_column_h2_removed[<h2>Hand off &amp; Track \xb7 \u79fb\u4ea4\u4e0e\u8ddf\u8e2a</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_page_eyebrow_is_engineer_workspace_not_h1_duplicate
tests/test_workbench_chinese_direction_consistency.py::test_h1_still_carries_full_bilingual_title
tests/test_workbench_chinese_direction_consistency.py::test_eyebrow_and_h1_are_not_chinese_duplicates
tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Probe &amp; Trace</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Annotate &amp; Propose</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Hand off &amp; Track</h2>]
tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_preserves_english_suffix[Control Logic Workbench</h1>]
tests/test_workbench_chinese_direction_consistency.py::test_workbench_route_reflects_direction_flip
tests/test_workbench_chinese_direction_consistency.py::test_e11_15c_only_touches_static_html_and_tests
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_carries_chinese_eyebrow[<p class="eyebrow">\u5de5\u7a0b\u5e08\u5de5\u4f5c\u533a</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_carries_chinese_eyebrow[<span class="workbench-sow-eyebrow">\u5f53\u524d\u73b0\u72b6</span>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_carries_chinese_eyebrow[<p class="eyebrow">\u4e3b\u6d41\u573a\u666f</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_carries_chinese_eyebrow[<p class="eyebrow">\u6807\u6ce8\u6536\u4ef6\u7bb1</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_carries_chinese_eyebrow[<p class="eyebrow">\u5ba1\u6279\u4e2d\u5fc3</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_does_not_carry_stale_english_eyebrow[<p class="eyebrow">control logic workbench</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_does_not_carry_stale_english_eyebrow[<span class="workbench-sow-eyebrow">state of world</span>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_does_not_carry_stale_english_eyebrow[<p class="eyebrow">canonical scenarios</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_does_not_carry_stale_english_eyebrow[<p class="eyebrow">annotation inbox</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_html_does_not_carry_stale_english_eyebrow[<p class="eyebrow">approval center</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_03_column_eyebrows_preserved[<p class="eyebrow">probe &amp; trace</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_03_column_eyebrows_preserved[<p class="eyebrow">annotate &amp; propose</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_03_column_eyebrows_preserved[<p class="eyebrow">hand off &amp; track</p>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[<h1>\u63a7\u5236\u903b\u8f91\u5de5\u4f5c\u53f0 \xb7 Control Logic Workbench</h1>]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[id="workbench-state-of-world-bar"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[id="workbench-wow-starters"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[id="annotation-inbox"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[id="approval-center-panel"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[class="eyebrow"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_preserves_structural_anchors[class="workbench-sow-eyebrow"]
tests/test_workbench_chinese_eyebrow_sweep.py::test_workbench_route_serves_chinese_eyebrows
tests/test_workbench_chinese_eyebrow_sweep.py::test_e11_15_only_touches_static_html
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[<h1>\u63a7\u5236\u903b\u8f91\u5de5\u4f5c\u53f0 \xb7 Control Logic Workbench</h1>]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[>\u52a0\u8f7d\u5f53\u524d\u5de5\u5355 \xb7 Load Active Ticket<]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[>\u5feb\u7167\u5f53\u524d\u72b6\u6001 \xb7 Snapshot Current State<]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[<h2>\u5ba1\u6838\u961f\u5217 \xb7 Review Queue</h2>]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[\u5ba1\u6279\u4e2d\u5fc3 \xb7 Approval Center]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[\u5ba1\u6279\u64cd\u4f5c\u4ec5\u9650 Kogami \xb7 Approval actions are Kogami-only.]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_carries_bilingual_string[Kogami \u63d0\u6848\u5ba1\u6279 \xb7 Kogami Proposal Triage]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_does_not_carry_stale_english_only[<h1>Control Logic Workbench</h1>]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_does_not_carry_stale_english_only[>Load Active Ticket<]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_does_not_carry_stale_english_only[>Snapshot Current State<]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_does_not_carry_stale_english_only[<h2>Review Queue</h2>]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_html_does_not_carry_stale_english_only[<h2 id="approval-center-title">Kogami Proposal Triage</h2>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Control Logic Workbench</h1>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Load Active Ticket</button>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Snapshot Current State</button>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Review Queue</h2>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Approval Center\n]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Approval actions are Kogami-only.]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_english_suffix[Kogami Proposal Triage</h2>]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[id="approval-center-entry"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[id="approval-center-panel"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[id="approval-center-title"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[id="annotation-inbox"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[class="workbench-toolbar-button is-primary"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[data-role="KOGAMI"]
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_preserves_structural_anchors[data-approval-role="KOGAMI"]
tests/test_workbench_chinese_h2_button_sweep.py::test_workbench_route_serves_bilingual_strings
tests/test_workbench_chinese_h2_button_sweep.py::test_e11_15b_does_not_touch_api_remediation_message
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_column_title[\u63a2\u9488\u4e0e\u8ffd\u8e2a \xb7 Probe &amp; Trace]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_column_title[\u6807\u6ce8\u4e0e\u63d0\u6848 \xb7 Annotate &amp; Propose]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_column_title[\u79fb\u4ea4\u4e0e\u8ddf\u8e2a \xb7 Hand off &amp; Track]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_eyebrow[probe &amp; trace]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_eyebrow[annotate &amp; propose]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_eyebrow[hand off &amp; track]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[<h2>Scenario Control</h2>]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[<h2>Spec Review Surface</h2>]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[<h2>Logic Circuit Surface</h2>]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[>control panel<]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[>document<]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[>circuit<]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[Waiting for control panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[Waiting for document panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_does_not_carry_stale_column_title[Waiting for circuit panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_boot_status[Waiting for probe &amp; trace panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_boot_status[Waiting for annotate &amp; propose panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_carries_new_boot_status[Waiting for hand off &amp; track panel boot.]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-control-panel"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-document-panel"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-circuit-panel"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-column="control"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-column="document"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-column="circuit"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-annotation-surface="control"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-annotation-surface="document"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[data-annotation-surface="circuit"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-control-status"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-document-status"]
tests/test_workbench_column_rename.py::test_workbench_html_preserves_stable_anchor[id="workbench-circuit-status"]
tests/test_workbench_column_rename.py::test_workbench_js_boot_status_uses_new_names[Probe & Trace ready. Scenario actions are staged for the next bundle.]
tests/test_workbench_column_rename.py::test_workbench_js_boot_status_uses_new_names[Annotate & Propose ready. Text-range annotation is staged for the next bundle.]
tests/test_workbench_column_rename.py::test_workbench_js_boot_status_uses_new_names[Hand off & Track ready. Overlay annotation is staged for the next bundle.]
tests/test_workbench_column_rename.py::test_workbench_js_boot_status_drops_stale_names
tests/test_workbench_column_rename.py::test_workbench_js_boot_status_drops_internal_phase_tokens
tests/test_workbench_column_rename.py::test_workbench_js_failure_fallback_uses_task_verb_label
tests/test_workbench_column_rename.py::test_workbench_route_serves_renamed_columns
tests/test_workbench_dual_route.py::test_workbench_route_serves_shell_only[/workbench]
tests/test_workbench_dual_route.py::test_workbench_route_serves_shell_only[/workbench.html]
tests/test_workbench_dual_route.py::test_workbench_route_serves_shell_only[/expert/workbench.html]
tests/test_workbench_dual_route.py::test_workbench_bundle_route_serves_bundle_only[/workbench/bundle]
tests/test_workbench_dual_route.py::test_workbench_bundle_route_serves_bundle_only[/workbench/bundle.html]
tests/test_workbench_dual_route.py::test_workbench_bundle_route_serves_bundle_only[/workbench_bundle.html]
tests/test_workbench_dual_route.py::test_shell_and_bundle_files_share_no_h1
tests/test_workbench_dual_route.py::test_workbench_js_has_bundle_sentinel_guard
tests/test_workbench_js_no_global_shadowing.py::test_no_map_callback_shadows_document_global
tests/test_workbench_js_no_global_shadowing.py::test_no_function_param_shadows_document_global
tests/test_workbench_prompt_ticket_auth.py::test_prompt_renderer_uses_four_required_sections
tests/test_workbench_prompt_ticket_auth.py::test_ticket_publisher_writes_file_and_stdout_json
tests/test_workbench_prompt_ticket_auth.py::test_restricted_auth_allows_only_authorized_engineer_and_scope_files
tests/test_workbench_role_affordance.py::test_workbench_identity_chip_carries_data_identity_name
tests/test_workbench_role_affordance.py::test_workbench_html_has_pending_signoff_affordance_section
tests/test_workbench_role_affordance.py::test_pending_signoff_affordance_explains_replacement_of_disabled_ui
tests/test_workbench_role_affordance.py::test_pending_signoff_css_default_hidden_visible_toggle
tests/test_workbench_role_affordance.py::test_workbench_js_has_apply_role_affordance
tests/test_workbench_role_affordance.py::test_workbench_js_affordance_toggles_on_kogami_check
tests/test_workbench_role_affordance.py::test_workbench_js_honors_url_identity_param
tests/test_workbench_role_affordance.py::test_workbench_route_serves_role_affordance_section
tests/test_workbench_role_affordance.py::test_default_html_keeps_approval_center_visible_for_kogami
tests/test_workbench_role_affordance.py::test_e11_08_only_touches_ui_layer
tests/test_workbench_shell.py::test_workbench_route_serves_shell
tests/test_workbench_shell.py::test_workbench_shell_has_three_independent_columns
tests/test_workbench_shell.py::test_workbench_shell_has_identity_ticket_and_system_topbar
tests/test_workbench_shell.py::test_workbench_shell_has_annotation_inbox_skeleton
tests/test_workbench_shell.py::test_workbench_shell_has_kogami_approval_entry
tests/test_workbench_shell.py::test_workbench_javascript_exposes_failure_isolation_hooks
tests/test_workbench_start.py::test_workbench_start_route_serves_html[/workbench/start]
tests/test_workbench_start.py::test_workbench_start_route_serves_html[/workbench/start.html]
tests/test_workbench_start.py::test_workbench_start_static_assets_resolve
tests/test_workbench_start.py::test_workbench_start_has_six_entry_tiles
tests/test_workbench_start.py::test_workbench_start_tiles_carry_persona_metadata
tests/test_workbench_start.py::test_workbench_start_tiles_deep_link_into_workbench
tests/test_workbench_start.py::test_workbench_start_tile_hash_targets_exist_or_absent
tests/test_workbench_start.py::test_workbench_route_ignores_arbitrary_intent_param
tests/test_workbench_start.py::test_workbench_start_displays_redline_section
tests/test_workbench_start.py::test_workbench_start_explains_persona_vs_role_axis
tests/test_workbench_state_of_world_bar.py::test_state_of_world_payload_has_required_fields
tests/test_workbench_state_of_world_bar.py::test_state_of_world_kind_is_advisory
tests/test_workbench_state_of_world_bar.py::test_state_of_world_open_issues_is_int
tests/test_workbench_state_of_world_bar.py::test_state_of_world_truth_engine_sha_is_short
tests/test_workbench_state_of_world_bar.py::test_state_of_world_generated_at_is_iso
tests/test_workbench_state_of_world_bar.py::test_state_of_world_endpoint_returns_200
tests/test_workbench_state_of_world_bar.py::test_workbench_html_has_state_of_world_bar
tests/test_workbench_state_of_world_bar.py::test_workbench_html_bar_has_field_slot[truth_engine_sha]
tests/test_workbench_state_of_world_bar.py::test_workbench_html_bar_has_field_slot[recent_e2e_label]
tests/test_workbench_state_of_world_bar.py::test_workbench_html_bar_has_field_slot[adversarial_label]
tests/test_workbench_state_of_world_bar.py::test_workbench_html_bar_has_field_slot[open_known_issues_count]
tests/test_workbench_state_of_world_bar.py::test_workbench_html_bar_has_advisory_flag
tests/test_workbench_state_of_world_bar.py::test_workbench_js_hydrate_state_of_world_bar_wired
tests/test_workbench_state_of_world_bar.py::test_workbench_route_serves_state_of_world_bar
tests/test_workbench_state_of_world_bar.py::test_state_of_world_endpoint_is_read_only
tests/test_workbench_trust_affordance.py::test_static_html_has_feedback_mode_chip
tests/test_workbench_trust_affordance.py::test_static_html_has_trust_banner
tests/test_workbench_trust_affordance.py::test_static_css_has_feedback_mode_styling
tests/test_workbench_trust_affordance.py::test_static_js_has_feedback_mode_handler
tests/test_workbench_trust_affordance.py::test_topbar_grid_accommodates_third_chip
tests/test_workbench_trust_affordance.py::test_workbench_route_serves_chip_and_banner
tests/test_workbench_trust_affordance.py::test_bundle_route_does_not_serve_shell_chip
tests/test_workbench_wow_starters.py::test_workbench_html_has_wow_starters_section
tests/test_workbench_wow_starters.py::test_workbench_html_has_card_for_each_wow[wow_a]
tests/test_workbench_wow_starters.py::test_workbench_html_has_card_for_each_wow[wow_b]
tests/test_workbench_wow_starters.py::test_workbench_html_has_card_for_each_wow[wow_c]
tests/test_workbench_wow_starters.py::test_workbench_js_declares_wow_scenarios
tests/test_workbench_wow_starters.py::test_workbench_js_installWowStarters_wired_to_dom
tests/test_workbench_wow_starters.py::test_workbench_js_freezes_exact_canonical_payloads
tests/test_workbench_wow_starters.py::test_wow_a_live_endpoint_with_exact_card_payload
tests/test_workbench_wow_starters.py::test_wow_b_live_endpoint_with_exact_card_payload
tests/test_workbench_wow_starters.py::test_wow_c_live_endpoint_with_exact_card_payload
tests/test_workbench_wow_starters.py::test_workbench_html_card_has_run_button_selector[wow_a]
tests/test_workbench_wow_starters.py::test_workbench_html_card_has_run_button_selector[wow_b]
tests/test_workbench_wow_starters.py::test_workbench_html_card_has_run_button_selector[wow_c]
tests/test_workbench_wow_starters.py::test_workbench_start_reflects_e11_05_shipped
tests/test_workbench_wow_starters.py::test_workbench_js_runWowScenario_handles_http_error_and_timeout
tests/test_workbench_wow_starters.py::test_workbench_html_serves_with_wow_section

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_hardware_schema.py ________________
ImportError while importing test module '/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_hardware_schema.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_hardware_schema.py:17: in <module>
    import jsonschema
E   ModuleNotFoundError: No module named 'jsonschema'
______________ ERROR collecting tests/test_monte_carlo_engine.py _______________
ImportError while importing test module '/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_monte_carlo_engine.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_monte_carlo_engine.py:17: in <module>
    import numpy as np
E   ModuleNotFoundError: No module named 'numpy'
___________ ERROR collecting tests/test_provenance_sha_integrity.py ____________
ImportError while importing test module '/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_provenance_sha_integrity.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_provenance_sha_integrity.py:28: in <module>
    import yaml
E   ModuleNotFoundError: No module named 'yaml'
_______________ ERROR collecting tests/test_reverse_diagnosis.py _______________
ImportError while importing test module '/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/test_reverse_diagnosis.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_reverse_diagnosis.py:16: in <module>
    from well_harness.reverse_diagnosis import (
src/well_harness/reverse_diagnosis.py:16: in <module>
    from well_harness.hardware_schema import (
src/well_harness/hardware_schema.py:18: in <module>
    import jsonschema
E   ModuleNotFoundError: No module named 'jsonschema'
=========================== short test summary info ============================
ERROR tests/test_hardware_schema.py
ERROR tests/test_monte_carlo_engine.py
ERROR tests/test_provenance_sha_integrity.py
ERROR tests/test_reverse_diagnosis.py
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
1034/1061 tests collected (27 deselected), 4 errors in 0.30s

codex
A real reproducibility gap has shown up already: this shell environment can run `pytest`, but the repo config still treats core test deps as optional, and Playwright is not declared in project metadata at all. I’m verifying whether the new suite actually runs here or only skips, and whether the user’s proposed fresh-checkout command is sufficient without unstated global packages.
exec
/bin/zsh -lc 'which python && python --version && which pytest && pytest --version && (which playwright || true)' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
python not found

exec
/bin/zsh -lc "python - <<'PY'
import importlib.util
mods=['playwright','playwright.sync_api','numpy','jsonschema','yaml']
for name in mods:
    print(name, bool(importlib.util.find_spec(name)))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc 'pytest tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 5 in 172ms:

1 skipped in 0.01s

 exited 5 in 175ms:

1 skipped in 0.01s

codex
The current shell is not the same environment as the user’s verification snapshot: `pytest` is present, but `python` is not on `PATH`, and the new e2e module currently skips immediately here. I’m locating the actual interpreter and skip reason now, because that directly affects the “fresh checkout / reproducible rerun” claim.
exec
/bin/zsh -lc 'ls -d .venv venv env 2>/dev/null || true' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.venv

exec
/bin/zsh -lc "find .. -maxdepth 3 \\( -path '*/bin/pytest' -o -path '*/bin/python' -o -path '*/bin/python3' \\) | sort | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
exec
/bin/zsh -lc 'command -v python3 && python3 --version && command -v pytest && head -n 1 "$(command -v pytest)"' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/usr/bin/python3
Python 3.9.6
/opt/homebrew/bin/pytest
#!/opt/homebrew/opt/python@3.11/bin/python3.11

exec
/bin/zsh -lc 'pytest -rs tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 5 in 159ms:

=========================== short test summary info ============================
SKIPPED [1] tests/e2e/test_workbench_js_boot_smoke.py:28: could not import 'playwright.sync_api': No module named 'playwright'
1 skipped in 0.01s

exec
/bin/zsh -lc "ls -l .venv/bin | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
total 136
-rw-r--r--@ 1 Zhuanz  staff  4182 Apr 26 01:13 activate
-rw-r--r--@ 1 Zhuanz  staff  2750 Apr 26 01:13 activate.bat
-rw-r--r--@ 1 Zhuanz  staff  2712 Apr 26 01:13 activate.csh
-rw-r--r--@ 1 Zhuanz  staff  4284 Apr 26 01:13 activate.fish
-rw-r--r--@ 1 Zhuanz  staff  3854 Apr 26 01:13 activate.nu
-rw-r--r--@ 1 Zhuanz  staff  2786 Apr 26 01:13 activate.ps1
-rw-r--r--@ 1 Zhuanz  staff  2395 Apr 26 01:13 activate_this.py
-rw-r--r--@ 1 Zhuanz  staff  1730 Apr 26 01:13 deactivate.bat
-rwxr-xr-x@ 1 Zhuanz  staff   400 Apr 26 01:13 f2py
-rwxr-xr-x@ 1 Zhuanz  staff   397 Apr 26 01:13 jsonschema
-rwxr-xr-x@ 1 Zhuanz  staff   400 Apr 26 01:13 numpy-config
-rwxr-xr-x@ 1 Zhuanz  staff   405 Apr 26 01:13 py.test
-rw-r--r--@ 1 Zhuanz  staff  1217 Apr 26 01:13 pydoc.bat
-rwxr-xr-x@ 1 Zhuanz  staff   399 Apr 26 01:13 pygmentize
-rwxr-xr-x@ 1 Zhuanz  staff   405 Apr 26 01:13 pytest
lrwxr-xr-x@ 1 Zhuanz  staff    83 Apr 26 01:13 python -> /Users/Zhuanz/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
lrwxr-xr-x@ 1 Zhuanz  staff     6 Apr 26 01:13 python3 -> python
lrwxr-xr-x@ 1 Zhuanz  staff     6 Apr 26 01:13 python3.12 -> python

exec
/bin/zsh -lc ".venv/bin/python - <<'PY'
import importlib.util
mods=['playwright','playwright.sync_api','numpy','jsonschema','yaml']
for name in mods:
    print(name, bool(importlib.util.find_spec(name)))
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
  File "<frozen importlib.util>", line 91, in find_spec
playwright False
ModuleNotFoundError: No module named 'playwright'

exec
/bin/zsh -lc '.venv/bin/python --version && .venv/bin/pytest --version' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
Python 3.12.13
pytest 9.0.3

codex
The repo-local `.venv` is present and has the default-lane deps, but not Playwright. That means the new e2e suite is currently “skip-clean” rather than runnable from this checkout unless Playwright is installed separately, so I’m installing the missing browser stack in the repo venv to do the live boot probe rather than relying on the skipped state.
exec
/bin/zsh -lc '.venv/bin/pip install playwright' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 127 in 0ms:
zsh:1: no such file or directory: .venv/bin/pip

exec
/bin/zsh -lc '.venv/bin/python -m pip install playwright' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.venv/bin/python: No module named pip

exec
/bin/zsh -lc 'command -v uv || true' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/.local/bin/uv

exec
/bin/zsh -lc '.venv/bin/python -m ensurepip --version' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
pip 25.0.1

exec
/bin/zsh -lc 'command -v pip3 && pip3 --version' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 148ms:
pip 26.0.1 from /Users/Zhuanz/Library/Python/3.9/lib/python/site-packages/pip (python 3.9)

exec
/bin/zsh -lc '.venv/bin/python -m ensurepip && .venv/bin/python -m pip install playwright' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
codex
The repo venv was missing `pip` entirely, which is another concrete reproducibility clue. I’ve bootstrapped `pip` inside `.venv` and am finishing the Playwright install so I can test the claimed 8/8 path in the intended environment instead of the system pytest shim.
 succeeded in 9691ms:
Looking in links: /var/folders/q4/859yhpgn6x3fx6kv4mj5gmv40000gp/T/tmpfxlujrtc
Processing /var/folders/q4/859yhpgn6x3fx6kv4mj5gmv40000gp/T/tmpfxlujrtc/pip-25.0.1-py3-none-any.whl
Installing collected packages: pip
Successfully installed pip-25.0.1
Collecting playwright
  Downloading playwright-1.58.0-py3-none-macosx_11_0_arm64.whl.metadata (3.5 kB)
Collecting pyee<14,>=13 (from playwright)
  Downloading pyee-13.0.1-py3-none-any.whl.metadata (3.0 kB)
Collecting greenlet<4.0.0,>=3.1.1 (from playwright)
  Downloading greenlet-3.4.0-cp312-cp312-macosx_11_0_universal2.whl.metadata (3.7 kB)
Requirement already satisfied: typing-extensions in ./.venv/lib/python3.12/site-packages (from pyee<14,>=13->playwright) (4.15.0)
Downloading playwright-1.58.0-py3-none-macosx_11_0_arm64.whl (41.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.0/41.0 MB 10.2 MB/s eta 0:00:00
Downloading greenlet-3.4.0-cp312-cp312-macosx_11_0_universal2.whl (286 kB)
Downloading pyee-13.0.1-py3-none-any.whl (15 kB)
Installing collected packages: pyee, greenlet, playwright
Successfully installed greenlet-3.4.0 playwright-1.58.0 pyee-13.0.1

[notice] A new release of pip is available: 25.0.1 -> 26.0.1
[notice] To update, run: /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/.venv/bin/python -m pip install --upgrade pip

exec
/bin/zsh -lc '.venv/bin/python -m playwright install chromium' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 4457ms:
codex
I now have the intended browser stack in the repo venv. I’m using `.venv/bin/pytest` from here forward so the verification matches the branch’s real local workflow instead of the partial system installation that initially hid the e2e path behind skips.
exec
/bin/zsh -lc '.venv/bin/pytest tests/e2e/test_workbench_js_boot_smoke.py -q -rs' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 5 in 1654ms:

8 deselected in 1.54s

exec
/bin/zsh -lc '.venv/bin/pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 6700ms:
........                                                                 [100%]
8 passed in 6.58s

exec
/bin/zsh -lc '.venv/bin/pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 6611ms:
........                                                                 [100%]
8 passed in 6.50s

exec
/bin/zsh -lc '.venv/bin/pytest -m e2e tests/e2e -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 7052ms:
...................................                                      [100%]
35 passed in 6.93s

codex
The targeted suite is now 8/8 twice in the repo venv, which is a good determinism signal. I’m running the whole `tests/e2e` marker lane next to make sure the shared `demo_server` fixture still behaves when the legacy wow tests and the new browser smoke tests coexist.
exec
/bin/zsh -lc "rg --files src/well_harness/static -g '*.js' | sort" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "rg -n --pcre2 'function\\s+\\w+\\s*\\(["'^'"\\n)]*\\bdocument\\b["'^'"\\n)]*\\)' src/well_harness/static/*.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
 succeeded in 0ms:
src/well_harness/static/annotation_overlay.js
src/well_harness/static/c919_etras_workstation.js
src/well_harness/static/demo.js
src/well_harness/static/timeseries_chart.js
src/well_harness/static/workbench.js

exec
/bin/zsh -lc "rg -n --pcre2 '\\(["'^'"\\n)]*\\bdocument\\b["'^'"\\n)]*\\)\\s*=>' src/well_harness/static/*.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
codex
The grep pass across all static JS files is clean so far: no arrow or named-function parameter bindings of literal `document` remain in `workbench.js`, `annotation_overlay.js`, or the other shipped JS assets. I’m doing one manual browser-console probe now to check for boot-time warnings that the pageerror-only tests would miss.
exec
/bin/zsh -lc "rg -n 'map\\s*\\(\\s*\\(\\s*document\\b|forEach\\s*\\(\\s*\\(\\s*document\\b|filter\\s*\\(\\s*\\(\\s*document\\b|reduce\\s*\\(\\s*\\(\\s*document\\b|find\\s*\\(\\s*\\(\\s*document\\b|function\\s+\\w+\\s*\\(["'^)]*'"\\bdocument\\b' src/well_harness/static" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 1 in 0ms:
exec
/bin/zsh -lc "rg -n 'function renderSystemFingerprintFromPacketPayload|function renderSystemFingerprint|function loadBootstrapPayload|function workbenchElement|function bootWorkbench' src/well_harness/static/workbench.js" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
61:function bootWorkbenchColumnSafely(columnName, bootFn) {
84:function bootWorkbenchControlPanel() {
93:function bootWorkbenchDocumentPanel() {
102:function bootWorkbenchCircuitPanel() {
111:function bootWorkbenchShell() {
194:function workbenchElement(id) {
1290:function renderSystemFingerprint({
1642:function renderSystemFingerprintFromPacketPayload(packetPayload, {
3163:function renderSystemFingerprintFromPayload(payload) {
3479:async function loadBootstrapPayload() {

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '1290,1360p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '3470,3615p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  1290	function renderSystemFingerprint({
  1291	  badgeState = "idle",
  1292	  badgeText = "等待生成",
  1293	  summary = "这里会直接告诉你第二套系统到底长什么样，而不只是告诉你它能不能接。",
  1294	  systemId = "-",
  1295	  objective = "-",
  1296	  sourceMode = "-",
  1297	  sourceTruth = "-",
  1298	  documents = [],
  1299	  signals = [],
  1300	  documentFallback = "还没有来源文档。",
  1301	  signalFallback = "还没有关键信号定义。",
  1302	} = {}) {
  1303	  setFingerprintBadge(badgeState, badgeText);
  1304	  renderValue("workbench-fingerprint-summary", summary);
  1305	  renderValue("workbench-fingerprint-system-id", systemId);
  1306	  renderValue("workbench-fingerprint-objective", objective);
  1307	  renderValue("workbench-fingerprint-source-mode", sourceMode);
  1308	  renderValue("workbench-fingerprint-source-truth", sourceTruth);
  1309	  renderValue("workbench-fingerprint-doc-count", `${documents.length} 份文档`);
  1310	  renderValue("workbench-fingerprint-signal-count", `${signals.length} 个信号`);
  1311	  renderFingerprintDocumentList(documents, documentFallback);
  1312	  renderFingerprintSignalList(signals, signalFallback);
  1313	}
  1314	
  1315	function renderActionList(containerId, items, fallbackText) {
  1316	  const container = workbenchElement(containerId);
  1317	  if (!items.length) {
  1318	    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
  1319	    return;
  1320	  }
  1321	  container.replaceChildren(...items);
  1322	}
  1323	
  1324	function renderOnboardingActions({
  1325	  badgeState = "idle",
  1326	  badgeText = "等待生成",
  1327	  summary = "这里会把接入动作拆成三列：先补澄清、再补结构、最后看解锁项。",
  1328	  followUps = [],
  1329	  blockers = [],
  1330	  unlocks = [],
  1331	  followUpFallback = "运行后这里会列出需要先回答的澄清项。",
  1332	  blockerFallback = "运行后这里会列出需要补的结构问题。",
  1333	  unlockFallback = "运行后这里会列出补齐后可解锁的能力。",
  1334	} = {}) {
  1335	  setActionsBadge(badgeState, badgeText);
  1336	  renderValue("workbench-actions-summary", summary);
  1337	  renderValue("workbench-actions-follow-up-count", `${followUps.length} 项`);
  1338	  renderValue("workbench-actions-schema-count", `${blockers.length} 项`);
  1339	  renderValue("workbench-actions-unlock-count", `${unlocks.length} 项`);
  1340	  renderActionList("workbench-actions-follow-up-list", followUps, followUpFallback);
  1341	  renderActionList("workbench-actions-schema-list", blockers, blockerFallback);
  1342	  renderActionList("workbench-actions-unlock-list", unlocks, unlockFallback);
  1343	}
  1344	
  1345	function setSchemaRepairActionState(disabled) {
  1346	  workbenchElement("workbench-apply-schema-repairs").disabled = disabled;
  1347	}
  1348	
  1349	function renderSchemaRepairWorkspace({
  1350	  badgeState = "idle",
  1351	  badgeText = "等待生成",
  1352	  summary = "这里会把 schema blocker 里的安全 autofix 项单独挑出来。",
  1353	  cards = [],
  1354	  fallbackTitle = "等待生成",
  1355	  fallbackText = "blocked bundle 出来后，这里会显示 repair suggestions。",
  1356	  note = "只有后端标记为 safe autofix 的修复才会开放一键应用。",
  1357	  actionsDisabled = true,
  1358	} = {}) {
  1359	  setSchemaRepairBadge(badgeState, badgeText);
  1360	  renderValue("workbench-schema-workspace-summary", summary);

 succeeded in 0ms:
  3470	    setPacketSourceStatus("当前样例：来自 AI Document Analyzer 的 Pipeline 结果。页面会自动生成 Bundle。");
  3471	    setCurrentWorkbenchRunLabel("Pipeline 结果导入");
  3472	    setActiveWorkbenchPreset("");
  3473	    return true;
  3474	  } catch (error) {
  3475	    return false;
  3476	  }
  3477	}
  3478	
  3479	async function loadBootstrapPayload() {
  3480	  setRequestStatus("正在加载 bootstrap 样例...", "neutral");
  3481	  const response = await fetch(workbenchBootstrapPath, {method: "GET"});
  3482	  const payload = await response.json();
  3483	  if (!response.ok) {
  3484	    throw new Error(payload.error || "bootstrap request failed");
  3485	  }
  3486	  bootstrapPayload = payload;
  3487	  renderExplainRuntime(payload);
  3488	  workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
  3489	  renderRecentWorkbenchArchives();
  3490	  workbenchElement("default-archive-root").textContent = payload.default_archive_root || "(unknown)";
  3491	  if (restoreWorkbenchPacketWorkspaceFromBrowser()) {
  3492	    return;
  3493	  }
  3494	  setPacketEditor(payload.reference_packet);
  3495	  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.reference_packet, {
  3496	    title: "默认参考样例",
  3497	    summary: "启动时自动载入的 reference packet。",
  3498	  }));
  3499	  fillReferenceResolutionDefaults();
  3500	  setPacketSourceStatus("当前样例：参考样例。适合直接点“生成 Bundle”做可视化 happy path 验收。");
  3501	  renderPreparationBoard("参考样例已经装载完毕，点击“生成 Bundle”即可进入可视化验收。");
  3502	  renderSystemFingerprintFromPacketPayload(payload.reference_packet, {
  3503	    badgeState: "idle",
  3504	    badgeText: "画像已载入",
  3505	    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  3506	  });
  3507	  setActiveWorkbenchPreset("");
  3508	  setRequestStatus("已载入 reference packet，直接点“生成 Bundle”即可跑 happy path。", "success");
  3509	}
  3510	
  3511	async function runWorkbenchBundle() {
  3512	  const requestId = beginWorkbenchRequest();
  3513	  let requestPayload;
  3514	  try {
  3515	    requestPayload = collectWorkbenchRequestPayload();
  3516	  } catch (error) {
  3517	    if (!isLatestWorkbenchRequest(requestId)) {
  3518	      return false;
  3519	    }
  3520	    renderFailureResponse(String(error.message || error), {
  3521	      sourceMode: "当前来源：输入解析失败。",
  3522	      requestStatusMessage: String(error.message || error),
  3523	    });
  3524	    return false;
  3525	  }
  3526	  maybeCaptureCurrentPacketRevision({
  3527	    title: `${currentWorkbenchRunLabel} / 运行前 Packet`,
  3528	    summary: "在本次 bundle 请求前捕获当前 packet 版本。",
  3529	  });
  3530	  renderSystemFingerprintFromPacketPayload(requestPayload.packet_payload, {
  3531	    badgeState: "idle",
  3532	    badgeText: "画像解析中",
  3533	    summary: "系统正在生成 bundle，但这套系统的文档来源、控制目标和关键信号已经先展开给你看了。",
  3534	  });
  3535	  renderRunningBoard(`${currentWorkbenchRunLabel}：正在生成 bundle，请直接看上方可视化验收板。`);
  3536	  setRequestStatus("正在生成 workbench bundle...", "neutral");
  3537	  try {
  3538	    const response = await fetch(workbenchBundlePath, {
  3539	      method: "POST",
  3540	      headers: {"Content-Type": "application/json"},
  3541	      body: JSON.stringify(requestPayload),
  3542	    });
  3543	    const payload = await response.json();
  3544	    if (!isLatestWorkbenchRequest(requestId)) {
  3545	      return false;
  3546	    }
  3547	    if (!response.ok) {
  3548	      throw new Error(payload.message || payload.error || "workbench bundle request failed");
  3549	    }
  3550	    renderBundleResponse(payload);
  3551	    return true;
  3552	  } catch (error) {
  3553	    if (!isLatestWorkbenchRequest(requestId)) {
  3554	      return false;
  3555	    }
  3556	    renderFailureResponse(String(error.message || error));
  3557	    return false;
  3558	  }
  3559	}
  3560	
  3561	function installPacketSourceHandlers() {
  3562	  workbenchElement("load-reference-packet").addEventListener("click", () => {
  3563	    if (!applyReferencePacketSelection({
  3564	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3565	      sourceStatus: "当前样例：参考样例。适合直接点 '生成 Bundle' 做可视化 happy path 验收。",
  3566	      preparationMessage: "参考样例已经装载完毕，点击 '生成 Bundle' 即可进入可视化验收。",
  3567	    })) {
  3568	      return;
  3569	    }
  3570	    setCurrentWorkbenchRunLabel("手动生成");
  3571	    setActiveWorkbenchPreset("");
  3572	    setRequestStatus("已载入 reference packet。", "success");
  3573	  });
  3574	
  3575	  workbenchElement("load-template-packet").addEventListener("click", () => {
  3576	    if (!applyTemplatePacketSelection({
  3577	      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
  3578	      sourceStatus: "当前样例：空白模板。适合验证 clarification gate 是否会主动拦住不完整 packet。",
  3579	      preparationMessage: "空白模板已经装载完毕，运行后通常会在 clarification gate 停下。",
  3580	    })) {
  3581	      return;
  3582	    }
  3583	    setCurrentWorkbenchRunLabel("手动生成");
  3584	    setActiveWorkbenchPreset("");
  3585	    setRequestStatus("已载入空白模板。", "warning");
  3586	  });
  3587	
  3588	  workbenchElement("workbench-file-input").addEventListener("change", async (event) => {
  3589	    const input = event.currentTarget;
  3590	    const [file] = input.files || [];
  3591	    if (!file) {
  3592	      return;
  3593	    }
  3594	
  3595	    const text = await file.text();
  3596	    maybeAutoSnapshotCurrentPacketDraft("导入本地 JSON / " + file.name);
  3597	    workbenchElement("workbench-packet-json").value = text;
  3598	    setPacketSourceStatus("当前样例：本地文件 " + file.name + "。如果不是在调试，可以直接点 '生成 Bundle' 看可视化结果。");
  3599	    renderPreparationBoard("本地 JSON 已装载，运行后会把当前 packet 的通过/阻塞结果显示在上方看板。");
  3600	
  3601	    try {
  3602	      const packetPayload = JSON.parse(text);
  3603	      pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(packetPayload, {
  3604	        title: "导入本地 JSON / " + file.name,
  3605	        summary: "本地 packet 已导入输入区。",
  3606	      }));
  3607	      renderSystemFingerprintFromPacketPayload(packetPayload, {
  3608	        badgeState: "idle",
  3609	        badgeText: "画像已载入",
  3610	        summary: "本地 JSON 已装载。你现在就能先看这套系统的大致画像，再决定要不要继续生成 bundle。",
  3611	      });
  3612	    } catch (error) {
  3613	      renderSystemFingerprint({
  3614	        badgeState: "blocked",
  3615	        badgeText: "画像未识别",

exec
/bin/zsh -lc "nl -ba src/well_harness/static/workbench.js | sed -n '4068,4105p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
  4068	      applyRoleAffordance();
  4069	    }
  4070	  } catch (_err) {
  4071	    applyRoleAffordance();
  4072	  }
  4073	
  4074	  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  4075	  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  4076	  // NOT contain bundle elements like #workbench-packet-json,
  4077	  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  4078	  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  4079	  // bundle DOM exists and would throw "Cannot read properties of null" on the
  4080	  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  4081	  // skip bundle boot entirely. This script is shared between both pages.
  4082	  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  4083	  if (!onBundlePage) {
  4084	    return;
  4085	  }
  4086	
  4087	  installToolbarHandlers();
  4088	  updateWorkflowUI();
  4089	  if (checkUrlIntakeParam()) {
  4090	    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
  4091	    if (bundleBtn) {
  4092	      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
  4093	      bundleBtn.click();
  4094	    }
  4095	    return;
  4096	  }
  4097	  void loadBootstrapPayload();
  4098	});

exec
/bin/zsh -lc ".venv/bin/python - <<'PY'
from __future__ import annotations
import http.client, json, os, signal, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

repo = Path.cwd()
port = 8800
base = f'http://127.0.0.1:{port}'
env = os.environ.copy()
env['PYTHONPATH'] = str(repo / 'src') + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
proc = subprocess.Popen([
    str(repo / '.venv' / 'bin' / 'python'), '-m', 'well_harness.demo_server', '--port', str(port)
], cwd=repo, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def kill():
    if proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=3)

def wait_ready(timeout=10.0):
    payload = json.dumps({
        'tra_deg': 0, 'radio_altitude_ft': 100, 'engine_running': True,
        'aircraft_on_ground': True, 'reverser_inhibited': False,
        'eec_enable': True, 'n1k': 0.5,
        'feedback_mode': 'auto_scrubber', 'deploy_position_percent': 0,
    }).encode()
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            c = http.client.HTTPConnection('127.0.0.1', port, timeout=1.0)
            c.request('POST', '/api/lever-snapshot', body=payload, headers={'Content-Type': 'application/json'})
            r = c.getresponse(); r.read(); c.close()
            if r.status == 200:
                return
        except Exception:
            pass
        time.sleep(0.1)
    raise SystemExit('server not ready')

try:
    wait_ready()
    report = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for path in ['/workbench', '/workbench/bundle']:
            page = browser.new_page()
            page_errors = []
            console_msgs = []
            failed = []
            page.on('pageerror', lambda exc, pe=page_errors: pe.append(str(exc)))
            page.on('console', lambda msg, cm=console_msgs: cm.append({'type': msg.type, 'text': msg.text}))
            page.on('requestfailed', lambda req, rf=failed: rf.append({'url': req.url, 'failure': req.failure}))
            page.goto(base + path, wait_until='networkidle')
            page.wait_for_timeout(1000)
            dom = page.evaluate(\"\"\"
            () => ({
              title: document.title,
              bundleSentinel: document.getElementById('workbench-packet-json') "'!== null,
              identity: document.getElementById('"'workbench-identity')?.getAttribute('data-identity-name'),
              fingerprintDocCards: document.querySelectorAll('#workbench-fingerprint-doc-list .workbench-fingerprint-item').length,
              fingerprintSignalCards: document.querySelectorAll('#workbench-fingerprint-signal-list .workbench-fingerprint-item').length,
            })
            \"\"\")
            report[path] = {
                'page_errors': page_errors,
                'console': [m for m in console_msgs if m['type'] in {'warning','error'}],
                'requestfailed': failed,
                'dom': dom,
            }
            page.close()
        browser.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
finally:
    kill()
PY" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 4005ms:
{
  "/workbench": {
    "page_errors": [],
    "console": [],
    "requestfailed": [],
    "dom": {
      "title": "Control Logic Workbench",
      "bundleSentinel": false,
      "identity": "Kogami",
      "fingerprintDocCards": 0,
      "fingerprintSignalCards": 0
    }
  },
  "/workbench/bundle": {
    "page_errors": [],
    "console": [],
    "requestfailed": [],
    "dom": {
      "title": "Well Harness Workbench Bundle 验收台",
      "bundleSentinel": true,
      "identity": null,
      "fingerprintDocCards": 2,
      "fingerprintSignalCards": 3
    }
  }
}

exec
/bin/zsh -lc '.venv/bin/pytest --collect-only tests/e2e/test_workbench_js_boot_smoke.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 exited 5 in 143ms:

no tests collected (8 deselected) in 0.04s

exec
/bin/zsh -lc '.venv/bin/pytest tests/test_workbench_js_no_global_shadowing.py -q' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 111ms:
exec
/bin/zsh -lc "nl -ba pyproject.toml | sed -n '1,80p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/e2e/conftest.py | sed -n '1,140p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	[build-system]
     2	requires = ["setuptools>=68"]
     3	build-backend = "setuptools.build_meta"
     4	
     5	[project]
     6	name = "well-harness"
     7	version = "0.1.0"
     8	description = "Engineering workbench for aviation control logic: requirements to runtime verification evidence"
     9	readme = "README.md"
    10	requires-python = ">=3.9"
    11	# Runtime stays stdlib-only — demo_server.py imports no third-party packages.
    12	# Third-party deps land in [project.optional-dependencies] groups below so
    13	# they can be installed explicitly for test/tooling lanes.
    14	
    15	[project.optional-dependencies]
    16	# Install with: pip install -e '.[dev]'
    17	# Covers the pytest default lane + the schema-validation scripts under tools/.
    18	dev = [
    19	    "pytest>=8.0",
    20	    "pytest-subtests>=0.11",
    21	    "jsonschema>=4.17",
    22	    "numpy>=1.24",
    23	    "pyyaml>=6.0",
    24	]
    25	
    26	[tool.setuptools.package-dir]
    27	"" = "src"
    28	
    29	[tool.setuptools.packages.find]
    30	where = ["src"]
    31	
    32	[tool.pytest.ini_options]
    33	# Default CI lane excludes e2e; opt-in with: pytest -m e2e (or pytest -m "e2e or not e2e")
    34	addopts = "-m 'not e2e'"
    35	# Constrain discovery to tests/ so shelved archive trees are never collected.
    36	testpaths = ["tests"]
    37	# Make bare `pytest` work without requiring PYTHONPATH=src:. on the caller:
    38	# - src: well_harness package imports
    39	# - . (repo root): tools.* and tests.* imports from a few cross-file suites
    40	pythonpath = ["src", "."]
    41	markers = [
    42	    "e2e: opt-in end-to-end tests that boot demo_server on :8799 (run with -m e2e)",
    43	]

 succeeded in 0ms:
     1	"""Shared fixtures for P20.0 e2e tests.
     2	
     3	Boots well_harness.demo_server as a subprocess on port 8799, waits until
     4	/api/lever-snapshot responds, then yields a base_url to the tests.
     5	
     6	All tests in this package must carry @pytest.mark.e2e so the default
     7	pytest run (639 passed) is not affected. Opt-in via: pytest -m e2e
     8	"""
     9	from __future__ import annotations
    10	
    11	import http.client
    12	import json
    13	import os
    14	import signal
    15	import socket
    16	import subprocess
    17	import sys
    18	import time
    19	from pathlib import Path
    20	from typing import Callable
    21	
    22	import pytest
    23	
    24	REPO_ROOT = Path(__file__).resolve().parents[2]
    25	PORT = 8799
    26	BASE_URL = f"http://127.0.0.1:{PORT}"
    27	READY_TIMEOUT_S = 10.0
    28	
    29	
    30	def _port_free(port: int) -> bool:
    31	    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    32	        s.settimeout(0.2)
    33	        return s.connect_ex(("127.0.0.1", port)) != 0
    34	
    35	
    36	def _wait_ready(port: int, deadline_s: float) -> bool:
    37	    probe_payload = json.dumps({
    38	        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
    39	        "aircraft_on_ground": True, "reverser_inhibited": False,
    40	        "eec_enable": True, "n1k": 0.5,
    41	        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
    42	    }).encode()
    43	    start = time.monotonic()
    44	    while time.monotonic() - start < deadline_s:
    45	        try:
    46	            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
    47	            c.request("POST", "/api/lever-snapshot", body=probe_payload,
    48	                      headers={"Content-Type": "application/json"})
    49	            resp = c.getresponse()
    50	            resp.read()
    51	            c.close()
    52	            if resp.status == 200:
    53	                return True
    54	        except (ConnectionRefusedError, socket.timeout, OSError):
    55	            pass
    56	        time.sleep(0.15)
    57	    return False
    58	
    59	
    60	def _spawn_server(port: int, home_override: str | None = None) -> subprocess.Popen:
    61	    env = os.environ.copy()
    62	    # Force module discovery via PYTHONPATH so HOME overrides don't break
    63	    # user-site resolution of the editable-installed well_harness package.
    64	    src_path = str(REPO_ROOT / "src")
    65	    existing_pp = env.get("PYTHONPATH", "")
    66	    env["PYTHONPATH"] = src_path + (os.pathsep + existing_pp if existing_pp else "")
    67	    if home_override is not None:
    68	        env["HOME"] = home_override
    69	    proc = subprocess.Popen(
    70	        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
    71	        cwd=str(REPO_ROOT),
    72	        env=env,
    73	        stdout=subprocess.DEVNULL,
    74	        stderr=subprocess.DEVNULL,
    75	        start_new_session=True,
    76	    )
    77	    return proc
    78	
    79	
    80	def _kill_server(proc: subprocess.Popen) -> None:
    81	    if proc.poll() is not None:
    82	        return
    83	    try:
    84	        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    85	    except (ProcessLookupError, PermissionError):
    86	        pass
    87	    try:
    88	        proc.wait(timeout=3.0)
    89	    except subprocess.TimeoutExpired:
    90	        try:
    91	            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    92	        except (ProcessLookupError, PermissionError):
    93	            pass
    94	        proc.wait(timeout=2.0)
    95	
    96	
    97	@pytest.fixture(scope="session")
    98	def demo_server():
    99	    """Boot demo_server on :8799 for the whole e2e session."""
   100	    if not _port_free(PORT):
   101	        pytest.fail(f"Port {PORT} is already in use; cannot start e2e demo_server")
   102	    proc = _spawn_server(PORT)
   103	    try:
   104	        if not _wait_ready(PORT, READY_TIMEOUT_S):
   105	            _kill_server(proc)
   106	            pytest.fail(f"demo_server did not become ready on :{PORT} within {READY_TIMEOUT_S}s")
   107	        yield BASE_URL
   108	    finally:
   109	        _kill_server(proc)
   110	
   111	
   112	@pytest.fixture
   113	def api_post() -> Callable[[str, str, dict, float], tuple[int, object]]:
   114	    """Return a helper that POSTs JSON and returns (status, parsed_body)."""
   115	    def _post(base_url: str, path: str, payload: dict, timeout: float = 15.0):
   116	        host = base_url.replace("http://", "").split(":")[0]
   117	        port = int(base_url.rsplit(":", 1)[1])
   118	        conn = http.client.HTTPConnection(host, port, timeout=timeout)
   119	        try:
   120	            conn.request(
   121	                "POST", path,
   122	                body=json.dumps(payload).encode("utf-8"),
   123	                headers={"Content-Type": "application/json"},
   124	            )
   125	            resp = conn.getresponse()
   126	            raw = resp.read().decode("utf-8")
   127	            try:
   128	                body = json.loads(raw)
   129	            except json.JSONDecodeError:
   130	                body = raw
   131	            return resp.status, body
   132	        finally:
   133	            conn.close()
   134	    return _post

exec
/bin/zsh -lc "nl -ba tests/e2e/test_workbench_js_boot_smoke.py | sed -n '1,240p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba tests/test_workbench_js_no_global_shadowing.py | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
     1	"""E11-11 — guard against variable shadowing of `document` global in workbench.js.
     2	
     3	The renderFingerprintDocumentList loop originally bound the array element
     4	to a parameter named `document`, which shadowed the global DOM `document`
     5	and made `document.createElement(...)` call a method on the data object
     6	instead. Bundle-page boot threw `TypeError: document.createElement is not a function`.
     7	
     8	This test is a static-source guard so the regression is caught even when
     9	the e2e suite is deselected (default `pytest` run).
    10	"""
    11	
    12	from __future__ import annotations
    13	
    14	import re
    15	from pathlib import Path
    16	
    17	
    18	REPO_ROOT = Path(__file__).resolve().parents[1]
    19	WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
    20	
    21	
    22	def test_no_map_callback_shadows_document_global() -> None:
    23	    """No `.map((document) => ...)` or similar bindings of the literal
    24	    name `document` inside an arrow / function body — that would shadow
    25	    the global `document` and silently break createElement calls."""
    26	    js = WORKBENCH_JS.read_text(encoding="utf-8")
    27	    # Catches arrow params: `(document)` `(document,` `, document)` `, document,`
    28	    pattern = re.compile(r"\((?:[^)]*,\s*)?document(?:\s*,[^)]*)?\)\s*=>")
    29	    matches = pattern.findall(js)
    30	    assert not matches, (
    31	        f"workbench.js contains an arrow callback that shadows global "
    32	        f"`document`; rename the parameter (e.g. `doc`/`item`). Matches: {matches}"
    33	    )
    34	
    35	
    36	def test_no_function_param_shadows_document_global() -> None:
    37	    """No `function name(document)` declarations that shadow the global."""
    38	    js = WORKBENCH_JS.read_text(encoding="utf-8")
    39	    pattern = re.compile(r"function\s+\w+\s*\([^)]*\bdocument\b[^)]*\)")
    40	    matches = pattern.findall(js)
    41	    assert not matches, (
    42	        f"workbench.js declares a function parameter named `document` "
    43	        f"that shadows the global. Matches: {matches}"
    44	    )

 succeeded in 0ms:
     1	"""E11-11 — JS-boot smoke tests for /workbench (Playwright + Chromium).
     2	
     3	Closes deferred JS verification debt accumulated across:
     4	- E11-08 (role affordance — applyRoleAffordance + setWorkbenchIdentity +
     5	  ?identity= URL param parsing — only structural-static tests until now)
     6	- E11-13 (bundle/shell sentinel guard — only static-source check until now)
     7	- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
     8	  until now; this verifies the strings actually render in a real DOM)
     9	
    10	Marked `@pytest.mark.e2e` (the suite is deselected by the default
    11	addopts in pyproject.toml `-m 'not e2e'`). Runs only when invoked
    12	explicitly via `pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py`.
    13	
    14	Reuses the session-scoped `demo_server` fixture from
    15	`tests/e2e/conftest.py` which boots `well_harness.demo_server` on
    16	port 8799.
    17	
    18	Skips gracefully if Playwright + chromium are not installed.
    19	"""
    20	
    21	from __future__ import annotations
    22	
    23	import pytest
    24	
    25	pytestmark = pytest.mark.e2e
    26	
    27	# Skip the whole module if Playwright sync API or its browsers are missing.
    28	playwright_sync_api = pytest.importorskip("playwright.sync_api")
    29	from playwright.sync_api import sync_playwright  # noqa: E402
    30	
    31	
    32	@pytest.fixture(scope="module")
    33	def browser():
    34	    with sync_playwright() as pw:
    35	        try:
    36	            b = pw.chromium.launch()
    37	        except Exception as exc:
    38	            pytest.skip(f"chromium browser not installed: {exc}")
    39	        try:
    40	            yield b
    41	        finally:
    42	            b.close()
    43	
    44	
    45	def _new_page_with_error_capture(browser):
    46	    page = browser.new_page()
    47	    errors: list[str] = []
    48	    page.on("pageerror", lambda exc: errors.append(str(exc)))
    49	    return page, errors
    50	
    51	
    52	# ─── E11-08 closure: role affordance JS toggle (4 tests) ─────────────
    53	
    54	
    55	def test_default_identity_kogami_shows_approval_center(demo_server, browser):
    56	    page, errors = _new_page_with_error_capture(browser)
    57	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    58	    state = page.evaluate(
    59	        """
    60	        () => ({
    61	          identityAttr: document.getElementById('workbench-identity')
    62	            ?.getAttribute('data-identity-name'),
    63	          entryHidden: document.getElementById('approval-center-entry')?.hidden,
    64	          panelHidden: document.getElementById('approval-center-panel')?.hidden,
    65	          affState: document.getElementById('workbench-pending-signoff-affordance')
    66	            ?.getAttribute('data-pending-signoff'),
    67	        })
    68	        """
    69	    )
    70	    assert errors == [], f"page JS errors: {errors}"
    71	    assert state["identityAttr"] == "Kogami"
    72	    assert state["entryHidden"] is False
    73	    assert state["panelHidden"] is False
    74	    assert state["affState"] == "hidden"
    75	
    76	
    77	def test_engineer_identity_url_param_swaps_to_pending_affordance(demo_server, browser):
    78	    page, errors = _new_page_with_error_capture(browser)
    79	    page.goto(f"{demo_server}/workbench?identity=Engineer", wait_until="networkidle")
    80	    state = page.evaluate(
    81	        """
    82	        () => ({
    83	          identityAttr: document.getElementById('workbench-identity')
    84	            ?.getAttribute('data-identity-name'),
    85	          entryHidden: document.getElementById('approval-center-entry')?.hidden,
    86	          entryAriaDisabled: document.getElementById('approval-center-entry')
    87	            ?.getAttribute('aria-disabled'),
    88	          panelHidden: document.getElementById('approval-center-panel')?.hidden,
    89	          affState: document.getElementById('workbench-pending-signoff-affordance')
    90	            ?.getAttribute('data-pending-signoff'),
    91	        })
    92	        """
    93	    )
    94	    assert errors == [], f"page JS errors: {errors}"
    95	    assert state["identityAttr"] == "Engineer"
    96	    assert state["entryHidden"] is True
    97	    assert state["entryAriaDisabled"] == "true"
    98	    assert state["panelHidden"] is True
    99	    assert state["affState"] == "visible"
   100	
   101	
   102	def test_set_workbench_identity_window_function_toggles_dom(demo_server, browser):
   103	    page, errors = _new_page_with_error_capture(browser)
   104	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
   105	    after = page.evaluate(
   106	        """
   107	        () => {
   108	          const ok = window.setWorkbenchIdentity('Engineer');
   109	          return {
   110	            ok,
   111	            affState: document.getElementById('workbench-pending-signoff-affordance')
   112	              ?.getAttribute('data-pending-signoff'),
   113	            entryHidden: document.getElementById('approval-center-entry')?.hidden,
   114	          };
   115	        }
   116	        """
   117	    )
   118	    assert errors == [], f"page JS errors: {errors}"
   119	    assert after["ok"] is True
   120	    assert after["affState"] == "visible"
   121	    assert after["entryHidden"] is True
   122	
   123	
   124	def test_set_workbench_identity_blank_returns_false(demo_server, browser):
   125	    page, _ = _new_page_with_error_capture(browser)
   126	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
   127	    result = page.evaluate("() => window.setWorkbenchIdentity('   ')")
   128	    assert result is False
   129	
   130	
   131	# ─── E11-13 closure: bundle/shell sentinel guard (2 tests) ───────────
   132	
   133	
   134	def test_shell_workbench_boots_without_js_errors(demo_server, browser):
   135	    """E11-13 R1 BLOCKER fix: the shell page must not throw on bundle-only
   136	    DOM (the sentinel `getElementById("workbench-packet-json")` early-returns
   137	    before bundle-bound handlers run)."""
   138	    page, errors = _new_page_with_error_capture(browser)
   139	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
   140	    page.wait_for_timeout(500)
   141	    assert errors == [], f"shell boot threw JS errors: {errors}"
   142	
   143	
   144	def test_bundle_workbench_boots_without_js_errors(demo_server, browser):
   145	    """E11-13: the bundle page must boot fully — sentinel guard does NOT
   146	    block it because #workbench-packet-json IS present on /workbench/bundle."""
   147	    page, errors = _new_page_with_error_capture(browser)
   148	    page.goto(f"{demo_server}/workbench/bundle", wait_until="networkidle")
   149	    page.wait_for_timeout(500)
   150	    assert errors == [], f"bundle boot threw JS errors: {errors}"
   151	
   152	
   153	# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────
   154	
   155	
   156	def test_workbench_renders_chinese_first_headers_in_dom(demo_server, browser):
   157	    """E11-15/15b/15c locked HTML-string contracts; this verifies the
   158	    actual rendered DOM after browser parse + JS boot also delivers
   159	    Chinese-first across every header surface."""
   160	    page, _ = _new_page_with_error_capture(browser)
   161	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
   162	    headers = page.evaluate(
   163	        """
   164	        () => ({
   165	          h1: document.querySelector('.workbench-collab-brand h1')?.textContent.trim(),
   166	          pageEyebrow: document.querySelector('.workbench-collab-brand .eyebrow')?.textContent.trim(),
   167	          probeH2: document.querySelector('#workbench-control-panel h2')?.textContent.trim(),
   168	          docH2: document.querySelector('#workbench-document-panel h2')?.textContent.trim(),
   169	          circuitH2: document.querySelector('#workbench-circuit-panel h2')?.textContent.trim(),
   170	          reviewH2: document.querySelector('#annotation-inbox h2')?.textContent.trim(),
   171	          approvalH2: document.querySelector('#approval-center-title')?.textContent.trim(),
   172	        })
   173	        """
   174	    )
   175	    # h1: "控制逻辑工作台 · Control Logic Workbench"
   176	    assert headers["h1"].startswith("控制逻辑工作台"), headers["h1"]
   177	    assert "Control Logic Workbench" in headers["h1"]
   178	    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
   179	    assert headers["pageEyebrow"] == "工程师工作区"
   180	    # column h2s: Chinese-first per E11-15c
   181	    assert headers["probeH2"].startswith("探针与追踪"), headers["probeH2"]
   182	    assert headers["docH2"].startswith("标注与提案"), headers["docH2"]
   183	    assert headers["circuitH2"].startswith("移交与跟踪"), headers["circuitH2"]
   184	    # inbox + approval h2: bilingual per E11-15b
   185	    assert headers["reviewH2"].startswith("审核队列"), headers["reviewH2"]
   186	    assert headers["approvalH2"].startswith("Kogami 提案审批"), headers["approvalH2"]
   187	
   188	
   189	def test_workbench_buttons_render_chinese_first_in_dom(demo_server, browser):
   190	    """E11-15b bilingualized 2 control-panel buttons + the Approval Center
   191	    entry button. Verify rendered text starts with the Chinese half."""
   192	    page, _ = _new_page_with_error_capture(browser)
   193	    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
   194	    button_texts = page.evaluate(
   195	        """
   196	        () => Array.from(document.querySelectorAll('button.workbench-toolbar-button'))
   197	          .map(b => b.textContent.trim())
   198	        """
   199	    )
   200	    # Find the 3 known bilingual buttons by their Chinese prefix.
   201	    has_load = any(t.startswith("加载当前工单") for t in button_texts)
   202	    has_snapshot = any(t.startswith("快照当前状态") for t in button_texts)
   203	    has_approval = any(t.startswith("审批中心") for t in button_texts)
   204	    assert has_load, f"missing 加载当前工单 button; got: {button_texts}"
   205	    assert has_snapshot, f"missing 快照当前状态 button; got: {button_texts}"
   206	    assert has_approval, f"missing 审批中心 button; got: {button_texts}"

exec
/bin/zsh -lc "nl -ba /Users/Zhuanz/.codex/memories/MEMORY.md | sed -n '842,930p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   857	## Task 2: Keep advancing automatically when Notion says Approved / 当前无需 Opus 审查
   858	
   859	### rollout_summary_files
   860	
   861	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, P7 workbench slices synced with dashboard/status/09C/freeze)
   862	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, P8 runtime-generalization work stayed autonomous through Notion writeback and gate recheck)
   863	
   864	### keywords
   865	
   866	- 根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查, 当前无需 Opus 审查, Gate status: Approved, tools/gsd_notion_sync.py run, NOTION_WRITEBACK_TIMEOUT_S, P7-19, P7-20, P8-05, P8-06
   867	
   868	## Task 3: Use existing payloads and validators for workbench/runtime slices instead of inventing new contracts
   869	
   870	### rollout_summary_files
   871	
   872	- rollout_summaries/2026-04-11T04-03-50-dFwS-p7_workbench_fingerprint_and_onboarding_action_boards.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/11/rollout-2026-04-11T12-03-50-019d7ab5-d6c6-7410-bfa2-4eba486a2b52.jsonl, updated_at=2026-04-11T16:50:13+00:00, thread_id=019d7ab5-d6c6-7410-bfa2-4eba486a2b52, fingerprint and onboarding boards built from existing payloads)
   873	- rollout_summaries/2026-04-11T17-50-40-lu8p-p8_runtime_generalization_two_system_comparison_and_notion_s.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/12/rollout-2026-04-12T01-50-40-019d7daa-d46d-7c22-8981-9f154f925879.jsonl, updated_at=2026-04-12T19:08:18+00:00, thread_id=019d7daa-d46d-7c22-8981-9f154f925879, runtime comparison extended existing validation surfaces to 23/23 pass)
   874	
   875	### keywords
   876	
   877	- 第二套系统画像, 第二套系统接入动作板, clarification_brief, blocking_reasons, unlocks_after_completion, second-system-smoke, two_system_runtime_comparison, scenario_playback, 23/23 pass
   878	
   879	## User preferences
   880	
   881	- the user’s repeated instruction was: "根据Notion上下文、开发规则，继续全自动推进，不要停止，除非需要我手动让Opus 4.6介入审查" -> default to uninterrupted autonomous execution when the gate is approved, and only interrupt for manual Opus review [Task 2][Task 3]
   882	- when the user asked to use Notion as the development center and avoid copying prompts, they were asking for a durable control plane, not an ad hoc note dump [Task 1]
   883	- once the control tower says `Approved` / `当前无需 Opus 审查`, do not stop for routine permission between small slices [Task 2]
   884	
   885	## Reusable knowledge
   886	
   887	- `tools/gsd_notion_sync.py run` can partially succeed even when live writeback times out; repo-doc sync may still complete, and a retry with higher `NOTION_WRITEBACK_TIMEOUT_S` can finish the Notion update [Task 1][Task 2]
   888	- The stronger QA baseline in this repo is not necessarily the most recent narrow maintenance run; the P6 recovery established that homepage/freeze text may need to prefer archived stronger evidence such as `175 tests OK, 10 demo smoke scenarios pass, 8/8 shared validation checks pass` [Task 1]
   889	- The workbench’s fingerprint board and onboarding action board both reused existing payload fields; future UI additions should prefer wiring into current payloads over new backend contracts [Task 3]
   890	- The P8 runtime comparison work exposed real parser/spec gaps and fixed them in `scenario_playback` and reference specs; the resulting shared baseline was `23/23 pass` [Task 3]
   891	- Related skill: `skills/notion-api-fallback-sync/SKILL.md` [Task 1]
   892	
   893	## Failures and how to do differently
   894	
   895	- Symptom: Notion writeback times out at 60s -> cause: slow Notion window, not necessarily a failed repo sync -> fix: retry with a larger timeout budget before concluding the write failed [Task 1][Task 2]
   896	- Symptom: homepage/freeze text suddenly shows a weaker QA baseline -> cause: the latest maintenance slice overwrote the stronger shared baseline summary -> fix: mine archive/history docs and deliberately preserve the stronger verified baseline in top surfaces [Task 1]
   897	- Symptom: a new feature idea suggests adding fresh payload contracts -> cause: overlooking the richness of current bundle payloads -> fix: inspect `clarification_brief`, `blocking_reasons`, `unlocks_after_completion`, and current packet/report artifacts first [Task 3]
   898	
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
**APPROVE_WITH_NITS**

- `IMPORTANT` — The advertised “fresh checkout” path is not actually self-contained. [pyproject.toml](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/pyproject.toml:15) keeps `pytest` in the optional `dev` extra, and there is no declared Playwright dependency at all, while [tests/e2e/test_workbench_js_boot_smoke.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:10) presents this as a runnable opt-in suite and [line 28](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:28) assumes the Python package is already present. In a truly clean env, `pip install -e . && playwright install chromium && pytest ...` is insufficient; you also need undeclared tooling/packages.
- `NIT` — The two “boots without JS errors” tests only listen for `pageerror` and then sleep for a fixed 500 ms. [_new_page_with_error_capture`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:45) does not fail on `console.error` or `requestfailed`, and the no-error assertions at [shell boot](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:134) / [bundle boot](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:144) are timing-based rather than event-based. My live probe found both routes clean today, so this is coverage debt, not a current bug.
- `INFO` — Port `8799` must be free for the shared fixture; the suite hard-fails otherwise rather than selecting an ephemeral port. See [tests/e2e/conftest.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/conftest.py:25) and the fixture gate at [lines 97-106](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/conftest.py:97).

The actual bug fix is sound. I found no remaining `document`-parameter shadow sites across `src/well_harness/static/*.js`, and the two renames in [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:1224) and [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:1649) are behavior-preserving local callback-parameter changes only. `git diff --name-only main..9da3d97` showed only the five claimed files, so the truth-engine red line is intact.

Verification:
- `.venv/bin/pytest --collect-only tests/e2e/test_workbench_js_boot_smoke.py -q` → `no tests collected (8 deselected)`
- `.venv/bin/pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py -q` → `8 passed in 6.58s`
- Same command rerun → `8 passed in 6.50s`
- `.venv/bin/pytest -m e2e tests/e2e -q` → `35 passed in 6.93s`
- `.venv/bin/pytest tests/test_workbench_js_no_global_shadowing.py -q` → `2 passed in 0.02s`
- Live probe: repo-venv Playwright against a temporary `demo_server` on `:8800` loaded `/workbench` and `/workbench/bundle` with no `pageerror`, no console warnings/errors, no failed requests; `/workbench/bundle` rendered `2` fingerprint document cards and `3` signal cards, which is the path that previously crashed.

**P5 — Apps Engineer (Tier-B, E11-11)**


tokens used
127,979
**APPROVE_WITH_NITS**

- `IMPORTANT` — The advertised “fresh checkout” path is not actually self-contained. [pyproject.toml](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/pyproject.toml:15) keeps `pytest` in the optional `dev` extra, and there is no declared Playwright dependency at all, while [tests/e2e/test_workbench_js_boot_smoke.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:10) presents this as a runnable opt-in suite and [line 28](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:28) assumes the Python package is already present. In a truly clean env, `pip install -e . && playwright install chromium && pytest ...` is insufficient; you also need undeclared tooling/packages.
- `NIT` — The two “boots without JS errors” tests only listen for `pageerror` and then sleep for a fixed 500 ms. [_new_page_with_error_capture`](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:45) does not fail on `console.error` or `requestfailed`, and the no-error assertions at [shell boot](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:134) / [bundle boot](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/test_workbench_js_boot_smoke.py:144) are timing-based rather than event-based. My live probe found both routes clean today, so this is coverage debt, not a current bug.
- `INFO` — Port `8799` must be free for the shared fixture; the suite hard-fails otherwise rather than selecting an ephemeral port. See [tests/e2e/conftest.py](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/conftest.py:25) and the fixture gate at [lines 97-106](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/tests/e2e/conftest.py:97).

The actual bug fix is sound. I found no remaining `document`-parameter shadow sites across `src/well_harness/static/*.js`, and the two renames in [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:1224) and [workbench.js](/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp/src/well_harness/static/workbench.js:1649) are behavior-preserving local callback-parameter changes only. `git diff --name-only main..9da3d97` showed only the five claimed files, so the truth-engine red line is intact.

Verification:
- `.venv/bin/pytest --collect-only tests/e2e/test_workbench_js_boot_smoke.py -q` → `no tests collected (8 deselected)`
- `.venv/bin/pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py -q` → `8 passed in 6.58s`
- Same command rerun → `8 passed in 6.50s`
- `.venv/bin/pytest -m e2e tests/e2e -q` → `35 passed in 6.93s`
- `.venv/bin/pytest tests/test_workbench_js_no_global_shadowing.py -q` → `2 passed in 0.02s`
- Live probe: repo-venv Playwright against a temporary `demo_server` on `:8800` loaded `/workbench` and `/workbench/bundle` with no `pageerror`, no console warnings/errors, no failed requests; `/workbench/bundle` rendered `2` fingerprint document cards and `3` signal cards, which is the path that previously crashed.

**P5 — Apps Engineer (Tier-B, E11-11)**


