2026-04-25T12:49:35.222049Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-research-deerflow/SKILL.md: missing YAML frontmatter delimited by ---
2026-04-25T12:49:35.222069Z ERROR codex_core::codex: failed to load skill /Users/Zhuanz/.agents/skills/cfd-report-pretext/SKILL.md: missing YAML frontmatter delimited by ---
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
session id: 019dc4b0-3b44-7bb3-b681-3f576c97ef58
--------
user
You are reviewing governance bundle #2 R3 fixes (PR #14, branch feat/governance-bundle-2-persona-tier-trigger-20260425, commit e259a42 on top of 419286b).

R2 (commit 419286b) returned CHANGES_REQUIRED with these findings:
- F1 partial: E11-00-PLAN hardcoded 5-persona closure/uniqueness/aggregator at lines 17, 256, 260, 302
- F2 partial: E11-00-PLAN:182 collapsed rollback to 2 actions, not RETRO §6.3's 3 actions
- F3 not resolved: constitution.md:343 + RETRO §6.2 still had old "default-P1 + owner rotation" wording
- NEW IMPORTANT: README:9 §Purpose said "pipeline ensures inter-persona finding uniqueness", false for Tier-B
- NIT: PERSONA-ROTATION-STATE.md not created (acceptable on first Tier-B sub-phase)

R3 fixes claim (commit e259a42):
1. F1 fix: Updated E11-00-PLAN §1 success criterion (Tier-A=5/5; Tier-B=1/1 + rotation), §6 Required output split tier-aware (within-PR uniqueness Tier-A only), §6 aggregator Tier-A only / Tier-B = single verdict file, §8 verification table tier-aware, §9 closure #3 tier-aware, §11 trailer tier-aware.
2. F2 fix: E11-00-PLAN:182 reproduced canonical RETRO §6.3 verbatim — 3 actions (rollback 3 sub-phases / open successor RETRO / re-engage Opus 4.7) + header "canonical = RETRO §6.3, constitution §Codex Persona Pipeline Tier-Trigger 引用".
3. F3 fix: constitution.md:343 + RETRO §6.2 line 148 both updated to cross-sub-phase round-robin P1→P2→P3→P4→P5→P1, default start P1, state file pointer, "no consecutive same persona". constitution.md additionally inlines the `git diff --stat` counting command so the canonical rule layer is self-contained.
4. NEW fix: README §Purpose split into Tier-A (within-PR uniqueness) + Tier-B (N/A, delegated to Surface Inventory + cross-sub-phase rotation + RETRO §6.3 rollback).
5. Consistency fan-out: E11-00-PLAN §3.6 candidate-rule line 165, Counterargument #2 line 215 (tier-aware anti-bias), risk table line 243 (tier-aware cost), constitution.md:11 changelog (rotation note added).

Files (R3 commit e259a42):
- .planning/codex_personas/README.md
- .planning/constitution.md
- .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
- .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md

Your task: Verify each R2 finding is genuinely closed AND no new spec drift was introduced. Pay attention to:
- Is rollback semantics now identical (3 actions verbatim) across constitution / RETRO §6.3 / E11-00-PLAN:182 / README §Cost? (no surviving 2-step or "re-evaluate" wording)
- Is rotation rule now identical (cross-sub-phase round-robin) across all 4 docs? (no surviving "same sub-phase no repeat" or "default P1 + owner rotation")
- Does §1 / §6 / §8 / §9 / §11 in E11-00-PLAN correctly distinguish Tier-A from Tier-B closure semantics?
- Does §Purpose in README accurately describe what Tier-B inherits vs what Tier-A inherits, without overpromising uniqueness?
- Counterargument #2's "(c) tier-aware anti-bias" claim accurate vs the actual rule layer?

Output format (verbatim):
```
VERDICT: APPROVE | CHANGES_REQUIRED
F1: [resolved | partial | not resolved] — <reason ≤2 lines>
F2: [resolved | partial | not resolved] — <reason ≤2 lines>
F3: [resolved | partial | not resolved] — <reason ≤2 lines>
NEW_R2_IMPORTANT: [resolved | partial | not resolved] — <reason ≤2 lines>
NEW_R3_FINDINGS:
- <none | severity + ≤2 line summary>
```

Be ruthless. Every cross-doc claim above must hold; if even one document still has stale wording, mark not-resolved. If the consistency fan-out introduced new drift (e.g., counterargument's tier-aware claim contradicts what's in §6 Required output), flag it.

Reply only with the structured output. No preamble.
codex
Reviewing the four planning docs and the R3 commit against the R2 findings. I’m checking the current text, the prior base commit, and any surviving stale wording across the bundle before I decide whether this closes cleanly.
exec
/bin/zsh -lc 'rg -n "LogicMVP|governance bundle|persona|rotation|Tier-A|Tier-B|RETRO-V61-054|E11-00-PLAN|README.md" /Users/Zhuanz/.codex/memories/MEMORY.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
49:# Task Group: AI FANTUI LogicMVP governance-first audit and Claude Code handoff packaging
52:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s coordination-docs, control-plane drift, and Claude Code handoff workflow, but exact baselines, GitHub settings, and Notion page drift are checkout-specific.
58:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, governance-first drift audit and coordination package)
68:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, single copy-paste prompt delivered for Claude Code)
78:- rollout_summaries/2026-04-22T13-49-36-w0BD-claude_code_pivot_report_and_handoff_prompt.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T21-49-36-019db574-11df-7c20-8119-dc6ee735487d.jsonl, updated_at=2026-04-22T14:31:33+00:00, thread_id=019db574-11df-7c20-8119-dc6ee735487d, factual framing tightened after Claude critique)
95:- In this repo, high-signal truth anchors for governance drift were `python3 tools/run_gsd_validation_suite.py --format json` and `python3 tools/validate_notion_control_plane.py --format json` plus direct reads of `README.md`, `.github/workflows/gsd-automation.yml`, `pyproject.toml`, `.planning/STATE.md`, `.planning/notion_control_plane.json`, and `tools/gsd_notion_sync.py` [Task 1]
109:# Task Group: AI FANTUI LogicMVP C919 E-TRAS reliability simulation candidates and adoption handoff
112:applies_to: cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP; reuse_rule=safe for this repo’s C919 E-TRAS workstation and candidate-handoff workflow, but branch names, commit SHAs, Notion pages, and demo URLs are checkout-specific.
118:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, candidate UI shipped on isolated branch after runtime fix)
128:- rollout_summaries/2026-04-22T04-17-29-5Lxl-c919_etras_reliability_simulation_candidate_handoff.md (cwd=/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP, rollout_path=/Users/Zhuanz/.codex/sessions/2026/04/22/rollout-2026-04-22T12-17-29-019db368-49c2-7091-9813-ac5513754a07.jsonl, updated_at=2026-04-22T04:38:31+00:00, thread_id=019db368-49c2-7091-9813-ac5513754a07, Notion/GitHub handoff completed with pushed branch and final fix commit)
168:- AI Coding Assets, Context Asset Manager, Development Cockpit, 调整整个项目的开发文档、计划, 像游戏一样, 小日报, team agent架构, README.md, AGENTS.md, .planning/ROADMAP.md, .planning/PROJECT.md, project_state/handoff-docs-cockpit-roadmap.md
192:- when the user asked to "调整整个项目的开发文档、计划" -> future work should update the complete planning surface (`README.md`, `AGENTS.md`, `.planning/*`, and handoff docs), not only a README refresh [Task 1]
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
920:- For this repo’s leadership narrative, the durable evidence sources are `docs/coordination/dev_handoff.md`, `docs/coordination/qa_report.md`, `docs/coordination/plan.md`, `README.md`, and `docs/demo_presenter_talk_track.md`, not Git history [Task 4]
968:- independent planning review, do not write acceptance_audit_log.yaml, do not modify freeze_gate_status.yaml, accepted_for_review, freeze-complete, docs incomplete, README routing, docs/README.md, MILESTONE_BOARD.md
1573:- Symptom: a request drifts into "use my other codex account’s quota" automation -> cause: account switching and subprocess orchestration were conflated with quota-bypass goals -> fix: keep the boundary explicit, support legitimate local switch-and-resume workflows, and do not build automatic quota-exhaustion rotation or pooling logic [Task 2]
1627:- Official Claude cloud-local handoff is not a one-click sync of local Claude Code sessions/memory/`.claude` config; the practical route is GitHub repo + Claude Project / GitHub integration / Claude Code on the web, with project rules separated from personal machine config [Task 3]

exec
/bin/zsh -lc "rg -n \"rotation|owner rotation|default start P1|default P1|no consecutive same persona|same sub-phase|within-PR uniqueness|uniqueness|rollback|re-evaluate|re-engage Opus 4\\.7|round-robin|single verdict file|Tier-A|Tier-B|Surface Inventory|§6\\.3|Counterargument #2|anti-bias|candidate-rule\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:7:> **Output artefacts:** constitution v2.3 §UI-COPY-PROBE; E11-00-PLAN §1.5 Surface Inventory template + 3 small differentials; `E11-02-SURFACE-INVENTORY.md` worked example
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:64:2. **强制 stage**：写完之后、commit 之前作者必须执行 claim-to-source sweep，三选一处置 [ANCHORED] / [REWRITE → planned for `<Phase-ID>`] / [DELETE]，结果登记到本期 §Surface Inventory。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:80:**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:89:| `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` 加 §1.5 Surface Inventory + Acceptance #5 + Scope 硬约束 + Counterargument C-UI | ✅ 本 PR |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:91:| 后续所有含 user-facing copy 的子 phase（E11-03..09 / E11-13..14 等）必填 §Surface Inventory | 进入 E11 phase 总验收清单（见 E11-00-PLAN.md §0 Acceptance #5） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:140:**Interpretation:** ≤2 rounds met. The R1 BLOCKER was *not* an honesty-class finding (which would have indicated v2.3 reflex still incomplete) — it was a real reactive bug catch. v2.3 § Surface Inventory worked: 4-row inventory landed verbatim, all anchors empirically verified, 0 fabricated surface claims found. **v2.3 amortization confirmed.**
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:147:- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:157:- v2.3 §UI-COPY-PROBE triggers / §Surface Inventory mandate / §Anchor 格式细则
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:163:If two consecutive Tier-B sub-phases produce ≥1 fabricated surface claim caught at post-merge time (per v2.3 §UI-COPY-PROBE §失效条件), automatically:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:171:- Post-tier-trigger Tier-B default: ~200k tokens / sub-phase  
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:172:- Post-tier-trigger Tier-A (rare, expected ~1 in 4-5): ~1M tokens / sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:174:- E11-15..19 still pending (5 sub-phases). At 4 Tier-B + 1 Tier-A: ~1.8M tokens vs default 5M. Savings ~64%, conservative.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:188:- **Q1**：是否要把 §Surface Inventory 抽象成 `tools/inventory_check.py` 自动化校验脚本（grep 锚点行真实存在）？现状是手动 + Codex 抽查。
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:192:- **Q3**：v2.3 §Surface Inventory 与现有 GSD `gsd-ui-checker` agent 是否重叠？
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:193:  - 倾向：**不重叠**。`gsd-ui-checker` 验 6 维度 design contract（layout / a11y / 等），是产品质量层；§Surface Inventory 验 honesty boundary（claim → src 锚点），是事实层。两者并列存在合理。
.planning/codex_personas/README.md:12:- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:33:> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。
.planning/codex_personas/README.md:39:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:52:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/codex_personas/README.md:54:**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。
.planning/codex_personas/README.md:56:**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
.planning/codex_personas/README.md:65:# Tier-A（5 persona 并行，仅在条件满足时跑）：
.planning/codex_personas/README.md:73:# Tier-B（1 persona 默认 — P1 Junior FCS）：
.planning/codex_personas/README.md:78:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/codex_personas/README.md:88:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:93:- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
.planning/codex_personas/README.md:97:### Tier-B（1-persona 默认）
.planning/codex_personas/README.md:99:No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
.planning/codex_personas/README.md:104:- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:117:2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/codex_personas/README.md:128:- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
.planning/codex_personas/README.md:129:- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:250:   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
.planning/constitution.md:251:   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
.planning/constitution.md:316:- 评审者（Codex / 第二视角）有权要求作者贴出 §Surface Inventory；缺失或残缺直接 CHANGES_REQUIRED，不进入逐字 ripgrep round-trip。
.planning/constitution.md:317:- 评审者抽查 §Surface Inventory 中任意一行的锚点是否真实成立；命中 fabricated 锚点 → 视为伪造证据（同 v5.2 反假装条款）。
.planning/constitution.md:320:- 作者声称已做 sweep 但 §Surface Inventory 缺失 / 行数与 copy 不对应 / 锚点 line 不存在 → 当轮 review 视为未做自审，要求重做（不是逐条修）。
.planning/constitution.md:342:| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5 (Tier-A，全 P1–P5 并行)** | 全跑 |
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/constitution.md:354:读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
.planning/constitution.md:360:**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
.planning/constitution.md:364:- v2.3 §UI-COPY-PROBE 的全部触发条件 + §Anchor 格式细则 + §Surface Inventory 强制
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:370:**回滚条件（canonical = RETRO-V61-054 §6.3）：** 连续两个 Tier-B 子 phase 的 user-facing copy 在 post-merge 阶段被发现 ≥1 条 fabricated surface（即 v2.3 §UI-COPY-PROBE §失效条件被触发） → 自动执行三项动作：
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）
.planning/constitution.md:376:详细 codification 在 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.3，本条款是规则层引用；两处不一致以 RETRO §6.3 为准。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:20:5. **(v2.3) 每个子 phase 的 user-facing copy 在 §Surface Inventory 全数登记**，锚点 line 真实存在；评审者抽查 1-3 行命中率 100%。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:44:## 1.5 Surface Inventory（v2.3 UI-COPY-PROBE 强制）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:116:> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:164:- 触发条件 = (a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE]
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:166:- v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:180:**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:211:### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:227:**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:243:| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:262:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:265:- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:287:| E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:345:> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc 'pwd && git status --short && git rev-parse --short HEAD && git rev-parse --short 419286b''^{commit} && git rev-parse --short e259a42''^{commit}' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
/Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
?? .planning/phases/governance-bundle-2/
e259a42
419286b
e259a42

codex
I have the current branch at `e259a42` and there’s an unrelated untracked `.planning/phases/governance-bundle-2/` directory, so I’m keeping the review read-only. Next I’m opening the exact sections in the four docs and diffing them against `419286b` to catch any stale wording that `rg` might have missed.
exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '1,140p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
    73	# Tier-B（1 persona 默认 — P1 Junior FCS）：
    74	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    75	  "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
    76	  > .planning/phases/<phase-id>/persona-P1-output.md 2>&1
    77	
    78	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
    79	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    80	  "$(cat .planning/codex_personas/P3-demo-presenter.md)" \
    81	  > .planning/phases/<phase-id>/persona-P3-output.md 2>&1
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
   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.

exec
/bin/zsh -lc "nl -ba .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md | sed -n '140,175p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba .planning/constitution.md | sed -n '330,390p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '1,40p;155,220p;250,320p;340,350p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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
   340	
   341	```
   342	Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
   343	```
   344	
   345	> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

exec
/bin/zsh -lc 'git diff --unified=20 419286b e259a42 -- .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
diff --git a/.planning/codex_personas/README.md b/.planning/codex_personas/README.md
index 5f195b6..d1b9ce0 100644
--- a/.planning/codex_personas/README.md
+++ b/.planning/codex_personas/README.md
@@ -1,29 +1,35 @@
 # Codex Persona Review Pipeline
 
 > Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
 > Date: 2026-04-25
 > Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6
 
 ## Purpose
 
-5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).
+5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape.
+
+**Anti-bias model (governance bundle #2, 2026-04-25):**
+- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
+- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
+
+See §Tier-trigger below for which tier fires when.
 
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
diff --git a/.planning/constitution.md b/.planning/constitution.md
index ecc7188..783a994 100644
--- a/.planning/constitution.md
+++ b/.planning/constitution.md
@@ -1,31 +1,31 @@
 # AI FANTUI LogicMVP Constitution
 
 > **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append + governance bundle #2 persona tier-trigger amortization)
 >
 > **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
 >
 > **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
 >
 > **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。
 >
-> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 默认 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
+> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
 
 ## Milestone Hold (historical, 2026-04-13)
 
 **Declared:** 2026-04-13
 **Scope:** Milestone 4 (Phases P4–P11)
 **Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**
 
 All P0 through P11 phases are complete. The project is at a natural pause point.
 
 ### What This Hold Means
 
 - No active development phases.
 - Base code frozen; only regression fixes and documentation corrections permitted.
 - Notion control tower and GitHub repo remain accessible as read-only reference.
 - Opus 4.6 review gate is not active.
 
 ### Reason
 
 All P0→P11 capabilities have been delivered:
 - Deterministic control-logic analysis workbench (thrust-reverser reference system)
@@ -323,47 +323,58 @@ scope=src/well_harness/static/workbench.js (grep "approval-action\|data-approval
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
-| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |
+| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
+
+**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**
+
+```bash
+git diff --stat $(git merge-base HEAD main)..HEAD -- \
+  'src/well_harness/static/*.html' \
+  'src/well_harness/static/*.js' \
+  'src/well_harness/static/*.css'
+```
+
+读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。
 
 **例外（仍跑全 5）：**
 - 该子 phase 触发 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
 - Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）
 
-**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。
+**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。
 
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
diff --git a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
index e1f77ac..2dad3c0 100644
--- a/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
+++ b/.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md
@@ -1,37 +1,37 @@
 # E11 — Workbench Engineer-First UX Overhaul (PLAN)
 
 > **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
 > **Date:** 2026-04-25
 > **Governance:** v6.1 (DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT)
 > **Trigger:** Kogami 2026-04-25 verbatim — "你现在的项目工作台，如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难，没有清晰的指引，面板操作困难，设计不够简约……深度思考解决方案。"
 > **Truth-engine red lines:** unchanged — `controller.py` / 19-node / 4 logic gates / `adapters/` 全程不动。
 
 ---
 
 ## 0. Goal Statement
 
 把 `/workbench` 从 Epic-06..10 留下的"功能完整但无引导的脚手架"重做为**真飞机控制逻辑工程师在 30 分钟内能产出第一份有用工作的工具**，且整个改造**完全不触碰真值层**（所有红线维持）。
 
 成功标准（goal-backward verifier）：
 1. 一个第一次接触 Workbench 的飞机控制工程师，**不读代码、不看 HANDOVER**，凭页面 affordance 能在 30 分钟内独立完成：(a) 选一个 wow-scenario 跑通，(b) 在某个 logic gate 边上贴一条 domain-anchored annotation，(c) 把这条 annotation 转成 Claude Code prompt 输出给同事。
-2. 5 个 Codex personas 各自跑一次 review，BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2 个/persona。
+2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
 3. main 三轨绿（default ≥ 863 / e2e 27 passed / adversarial 8/8）。
 4. truth-engine 红线 0 触碰。
 5. **(v2.3) 每个子 phase 的 user-facing copy 在 §Surface Inventory 全数登记**，锚点 line 真实存在；评审者抽查 1-3 行命中率 100%。
 
 ---
 
 ## 1. Current State — 反向 audit (probed 2026-04-25, main HEAD eea8065)
 
 | 维度 | 现状 | 工程师视角问题 |
 |---|---|---|
 | 页面入口 `/workbench` | 1078 行 HTML / 1717 行 CSS / 3754 行 JS / 22 个 data-attributed widgets | 信息密度过高，无层级 |
 | 页面身份 | 同一页 2 个 `<h1>`：上半 "Control Logic Workbench" (Epic-06 shell) + 下半 "Workbench Bundle 验收台" (旧 bundle 页) | 分裂的产品身份，工程师无法分辨"我在哪" |
 | 三列抽象 | "Scenario Control" / "Spec Review Surface" / "Logic Circuit Surface" | UI surface 命名，不是工程师任务命名 |
 | Annotation 词汇 | "Point / Area / Link / Text Range" | 通用 UI primitive，无领域含义；工程师不会自然说"在 logic3 上 point" |
 | 入口 button 标签 | "Load Active Ticket" / "Snapshot Current State" / "通过并留档" / "阻塞演示" / "快速通过" / "留档复跑" | 动作明显但无 `WHEN` 提示，混杂中英 |
 | 角色提示 | `data-role="ENGINEER"` 在身份 chip 上 | 没有 affordance 反映 ENGINEER 实际能/不能做什么 |
 | Approval Center | "Kogami Proposal Triage" 三个 lane (Pending/Accept/Reject) | 非 Kogami 角色看到 disabled UI 无解释 |
 | 主流程进度 | `<aside id="annotation-inbox">` Review Queue 是个空 skeleton | 工程师不知道 annotation → proposal → ticket → PR 整条链路是怎么走的 |
 | 红线告知 | 无任何 UI surface 告诉工程师"controller.py / 19-node 是只读的，你只能 propose 不能 commit" | 工程师可能误以为 button click 会改 truth；没有契约可视化 |
 | Domain anchoring | wow_a/wow_b/wow_c 三个 demo scenarios 在 `docs/demo/` 但 UI 上没有"从已知场景开始"按钮 | 工程师必须自己造 lever 输入；高门槛 |
@@ -145,198 +145,201 @@ E11-09 → E11-13/14 → E11-05 → E11-03 → E11-04 → E11-06
 ### E11-15..19 的位置
 
 不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。
 
 ---
 
 ## 3.6 Leading Indicator · E11-09 ≤ 2 Codex 轮 = governance 摊销证据
 
 > Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。
 
 **E11-09 是 governance machinery 是否过载的实证 gate**：
 
 | E11-09 Codex 轮数 | 解读 | Action |
 |---|---|---|
 | ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
 | 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
 | ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |
 
 **5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
 - 触发条件 = (a) 子 phase 含 user-facing copy diff ≥ 10 行 **AND** (b) 该子 phase 的 §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE]
-- 否则降为 1-persona（任选 P1/P2/P3/P4/P5 之一，默认 P1 + 当期 owner 视情况轮换）
+- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
 - v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**
 
 **未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性*取决于* E11-09 结果——E11-09 跑完前不写进 constitution。
 
 ### 3.6.1 Leading Indicator OUTCOME — fired ≤2 rounds (2026-04-25)
 
 E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。R1 的 BLOCKER 不是 honesty 类（不是 fabricated surface claim），是**真实 runtime bug**（workbench.js 共享 shell + bundle 但 binding bundle-only 元素无 null guard），属于 reactive review 正常工作。
 
 **Action 触发**：governance bundle #2 已通过 PR #14 落地（2026-04-25）：
 
 - `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
 - `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
 - 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default
 
 **Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
 
-**回滚条件（已写入 constitution v2.3）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface → 自动回滚 5-persona 默认 + 起 retro 后继。
+**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
 
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
 
 **Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。
 
 ### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
 
 **反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
 
-**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) 加 anti-bias safeguard：每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding，否则 review 不算 valid（pipeline 强制项）。结论：bias 风险存在但已通过 distinct context + cross-persona uniqueness 要求 mitigated。
+**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
 
 ### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"
 
 **反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。
 
 **Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。
 
 ### Counterargument C-UI: "本期 copy 里我是否写了一个 src/ 还没 ship 的 surface？"
 
 **反对论点**（v2.3 立法后强制必答）: landing / tile / banner / tooltip 的 copy 是否描述了某个 feature / field / role-gate / behavior，而该 surface 在当前 commit 的 src/ 里其实不存在或只存在于计划态？
 
 **Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。
 
 ### Counterargument C-Opus: "我是否在 governance 投资曲线已经 over-process 的情况下还在加新规则？"
 
 **反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
 
 **Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
 
 ---
 
 ## 5. Risk register
 
 | Risk | Severity | Mitigation |
 |---|---|---|
 | 改 workbench.html 大量 selector 导致 e2e + adversarial 测试失败 | High | 每 sub-phase 末跑三轨；保留底层 `id` 和 `data-*` selector 不动，只改 visible label / class / 排版 |
 | 新 onboarding flow 与已有 ticket 流程冲突 | Med | E11-02 的 `/workbench/start` 单纯是入口，导向已有按钮；不替换底层 prompt/ticket 逻辑 |
-| Codex 5 personas pipeline 跑一轮 ≈ 5 × 10min ≈ 1h CPU 时间 | Low | 后台跑（已有先例），分 batch；persona 失败 retry 1 次后转 manual review |
+| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
 | 工程师在 Authority Contract banner 之外仍误以为可改 truth | Med | E11-07 banner + E11-04 annotation 词汇双重锁；同时不提供任何会让工程师以为"在 UI 改 truth-engine"的 affordance |
 | 角色 affordance E11-08 暴露 Kogami-only 操作的 implementation detail | Low | 仅展示 "Awaiting Kogami sign-off" 文案，不暴露内部 actor 列表 |
 
 ---
 
 ## 6. Codex Persona Review Pipeline
 
 详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：
 
 1. **Persona 背景** — role / experience / mental model
 2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
 3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
-4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings + ≥1 finding NOT covered by other personas
+4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
+   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
+   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
 5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"
 
-每轮 review 跑完后：
-- Claude Code 汇总 5 份 verdict 进 `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md`
+每轮 review 跑完后（tier-aware）：
+- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
+- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
 - 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
-- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一
+- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）
 
 ---
 
 ## 7. Sequencing & estimated effort
 
 | Sub-phase | Type | LOC est | Time est | Codex required? |
 |---|---|---|---|---|
 | E11-01 | doc | ~300 | 30min | NO |
 | E11-02 | code (HTML/JS) | ~200 | 1h | YES (UI 交互模式变更) |
 | E11-03 | refactor (HTML/CSS) | ~150 | 45min | YES (UI 交互模式变更) |
 | E11-04 | doc + code | ~100 | 30min | NO (mechanical relabel) |
 | E11-05 | code (JS) | ~150 | 1h | YES (UI 交互模式变更) |
 | E11-06 | code (HTML/JS) | ~120 | 45min | YES (新 API 调用 / 状态聚合) |
 | E11-07 | code (HTML/CSS) | ~80 | 30min | NO (添加 banner，无逻辑) |
 | E11-08 | code (JS) | ~60 | 30min | NO (单 conditional 文案) |
 | E11-09 | refactor (routing) | ~200 | 1h | YES (路由变更 → 用户导航 mode) |
 | E11-10 | doc | ~600 (5 prompts) | 1.5h | self-review only |
 | E11-11 | test | ~150 | 1h | YES (新 e2e 期望) |
 | E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
 | E11-13 | code (HTML/CSS) | ~100 | 45min | YES (UI 交互模式变更 + manual mode trust 可视化) |
 | E11-14 | code (Python endpoint guard) | ~80 | 1h | YES (server-side guard, adapter boundary 内) |
 | E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
 | E11-16 | code (Python) | ~120 | 1h | YES (approval endpoint 三元绑定) |
 | E11-17 | code (HTML/CSS/JS) | ~180 | 1h | YES (presenter mode toggle = UI 交互模式变更) |
 | E11-18 | code (HTML/JS) | ~150 | 1h | YES (logic-gate trace tuple + schema 升级) |
 | E11-19 | code (HTML/JS + schema) | ~250 | 1.5h | YES (UI 交互模式变更 + ticket schema enrichment) |
 
 **Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)
 
 ---
 
 ## 8. Verification protocol (E11 closure 前必跑)
 
 | 维度 | 标准 | 锚点 |
 |---|---|---|
 | Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
 | E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
 | Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
 | Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
-| Codex personas | 5/5 verdict in {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER count = 0 across all | `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md` |
+| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
 | Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
 | EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |
 
 ---
 
 ## 9. CLOSURE 退出条件
 
 E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：
 
 1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
 2. ✅ §8 verification protocol 全部通过
-3. ✅ Codex persona review 给出 0 BLOCKER（人选数量按 §3.6 leading indicator 决出的 5-persona-或-tier-trigger 规则跑）
+3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
 4. ✅ truth-engine 红线 0 触碰
 5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
 6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
 7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria
 8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
 9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
 
 ---
 
 ## 10. Open Questions（pending Kogami input · 不阻塞启动）
 
 1. 5 personas 的 specific company / 项目 context 要不要 fictionalize？（默认: 是，避免暗示真实客户）
 2. Onboarding flow 是 modal 还是单独路由？（默认: 单独路由 `/workbench/start`，可深链可分享）
 3. 三列 verb 命名候选 "Probe & Trace / Annotate & Propose / Hand off & Track" 还是更激进的 "What-If / Mark / Hand off"？（默认: 前者，与现有 button 文案对齐）
 4. 双 h1 修复时把旧 bundle 验收台搬到 `/workbench/bundle` 还是直接 deprecate？（默认: 搬到子路径，保留访问路径以免破坏旧 demo 习惯）
 5. Authority Contract banner 是 sticky 还是 dismissable？（默认: sticky 在 truth-engine surfaces 周围，dismissable 在其他位置以免审美干扰）
 
 > 本 phase 启动不依赖以上 Q 解决；Q 在 E11-01 journey map 阶段会迭代回到 plan 里 confirm。
 
 ---
 
 ## 11. Trailer
 
 ```
 Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
 ```
 
-> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 5-persona Codex review 结果。
+> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。
diff --git a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
index 28b6006..cd17ce7 100644
--- a/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
+++ b/.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md
@@ -127,42 +127,42 @@ Opus 4.7 §1 strategic review (2026-04-25) set E11-09 dual-h1 fix as the **leadi
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
-- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows
-- Tier-B (1 persona, default P1; rotation to P2/P3/P4/P5 by phase owner): all other cases
+- Tier-A (5 personas, all parallel): user-facing copy diff ≥ 10 lines **AND** §Surface Inventory ≥ 3 [REWRITE/DELETE] rows. "copy diff ≥10 lines" is computed by `git diff --stat $(git merge-base HEAD main)..HEAD -- 'src/well_harness/static/*.{html,js,css}'` (X+Y from the last summary line); the number is printed in PR body for reviewer reproducibility.
+- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
 
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

codex
The main rule sections are aligned enough to compare now. I’m doing one more pass for buried stale phrases like `re-evaluate`, `default P1`, or old same-sub-phase rotation language, because one leftover sentence is enough to keep this at `CHANGES_REQUIRED`.
exec
/bin/zsh -lc "rg -n \"re-evaluate|default P1|default.*P1|owner rotation|same sub-phase|同一 sub-phase|no repeat|rotation to P2|Tier-B.*default P1|2-step|two actions|rollback.*2|re-engage Opus 4\\.7 strategic review|open successor RETRO|next 3 sub-phases|cross-sub-phase round-robin|P1 ?→ ?P2 ?→ ?P3 ?→ ?P4 ?→ ?P5 ?→ ?P1|within-PR uniqueness|single verdict file|aggregator\" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:164:1. Roll back to default 5-persona for the next 3 sub-phases
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:262:- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:99:No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
.planning/codex_personas/README.md:110:**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:118:3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.

exec
/bin/zsh -lc "git show 419286b:.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | nl -ba | sed -n '170,190p;250,270p;300,320p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
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
   319	8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
   320	9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）

exec
/bin/zsh -lc "git show 419286b:.planning/codex_personas/README.md | nl -ba | sed -n '1,120p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
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

exec
/bin/zsh -lc "git show 419286b:.planning/codex_personas/README.md | nl -ba | sed -n '120,140p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   120	**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
   121	- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
   122	- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
   123	- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
   124	
   125	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.

codex
I found two likely drift spots outside the headline sections: the README command templates still read like “default P1 / owner override,” and the README cost note still mentions the old `re-evaluate` framing. I’m confirming there aren’t parallel leftovers elsewhere before I finalize the verdict.
exec
/bin/zsh -lc 'rg -n "默认.?P1|default.?P1|owner 选择|owner 可按|当期 owner|re-evaluate|P1→P5|P1 -> P5|P1 → P5|P1→P2→P3→P4→P5→P1|P1 → P2 → P3 → P4 → P5 → P1|5-persona|single verdict|无 aggregator|Tier-A only|Tier-B:" .planning/codex_personas/README.md .planning/constitution.md .planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md' in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:127:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（governance bundle #2） |
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:146:**5-persona pipeline → tier-trigger:**
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:148:- Tier-B (1 persona, cross-sub-phase round-robin P1→P2→P3→P4→P5→P1): all other cases. Owner may override per sub-phase content, but must not repeat the same persona on two consecutive Tier-B sub-phases. State recorded in `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`; sequence resets per epic.
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:164:1. Roll back to default 5-persona for the next 3 sub-phases
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:170:- Pre-tier-trigger (default 5-persona): ~1M Codex tokens / user-facing UI sub-phase
.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md:180:- "Wait for retrospective" (would require N completed sub-phases under default 5-persona before deciding to soften)
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:17:2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Persona 数量按 §3.6 leading indicator 决出的 tier-trigger 规则跑（Tier-A = 5/5；Tier-B = 1/1，跨-sub-phase 轮换 P1→P5）。governance bundle #2 落地于 2026-04-25（PR #14），E11-13..19 默认按 tier-trigger。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:159:| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（candidate `governance bundle #2`） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:160:| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（候选：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:163:**5-persona pipeline tier-trigger 候选规则**（待 E11-09 实证后立法 / 否决）：
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:165:- 否则降为 1-persona Tier-B（跨-sub-phase 轮换 P1→P2→P3→P4→P5→P1；状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`；不得在连续两个 Tier-B sub-phase 上跑同一 persona）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:177:- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:180:**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:182:**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:215:**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:231:**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:233:**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**未立即立法 tier-trigger 的原因**：Opus 自己警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。当前 phase 用 §3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 决定是否启动 governance bundle #2 软化。Phase Owner 在每个新子 phase 启动前必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:257:   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:258:   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:263:- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:305:| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:317:3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md:323:9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）
.planning/codex_personas/README.md:13:- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.
.planning/codex_personas/README.md:31:> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
.planning/codex_personas/README.md:40:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona** |
.planning/codex_personas/README.md:78:# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
.planning/codex_personas/README.md:88:### Tier-A（5-persona 并行）
.planning/codex_personas/README.md:99:No aggregator runs (single verdict file = the review record). Closure precondition collapses to:
.planning/codex_personas/README.md:106:If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.
.planning/codex_personas/README.md:115:**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
.planning/codex_personas/README.md:116:1. **Cross-sub-phase rotation** — owner selects persona per round-robin (P1 → P2 → P3 → P4 → P5 → P1) so consecutive Tier-B sub-phases don't share reviewer perspective. Owner may override based on sub-phase content (e.g., demo-arc-heavy sub-phase → P3) but must not run the same persona on two consecutive Tier-B sub-phases.
.planning/codex_personas/README.md:122:**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
.planning/codex_personas/README.md:124:- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).
.planning/codex_personas/README.md:127:- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
.planning/codex_personas/README.md:129:- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.
.planning/codex_personas/README.md:131:If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.
.planning/constitution.md:11:> **governance bundle #2 (2026-04-25):** v2.3 §UI-COPY-PROBE 触发条件、§Surface Inventory 强制、§Anchor 格式细则 全部不动。本次仅在 v2.3 节内追加 §Codex Persona Pipeline Tier-Trigger 子节——把"每个 user-facing UI 子 phase 默认跑全 5-persona Codex review"软化为"copy diff ≥10 行 AND ≥3 [REWRITE/DELETE] → 跑全 5 (Tier-A)；否则跑 1 (Tier-B 跨-sub-phase 轮换 P1→P5→P1，起点 P1)"。触发条件：E11-09 PR #13 ≤2 轮 Codex APPROVE 实证 v2.3 已摊销（leading indicator fired）。详见 RETRO-V61-054 §6 + `.planning/codex_personas/README.md` §Invocation。
.planning/constitution.md:151:- **governance bundle #2 persona tier-trigger (2026-04-25, active):** v2.3 触发条件不动，仅追加 §Codex Persona Pipeline Tier-Trigger 子节。E11-09 PR #13 leading indicator fired (≤2 Codex 轮 APPROVE) → 5-persona 默认软化为 tier-trigger（copy diff ≥10 + ≥3 [REWRITE/DELETE] = 5；否则 1）。预期 Codex token 节约 ~70–80% on persona pipeline。详见 v2.3 §Codex Persona Pipeline Tier-Trigger、RETRO-V61-054 §6。
.planning/constitution.md:334:**前情：** E11-01 baseline review 引入 5-persona Codex pipeline，默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。Opus 4.7 §1 strategic review (2026-04-25) 判断"governance 正好偏过 5–10%"，5-persona 默认是真冗余——5 个 persona 的 marginal value 在第二个子 phase 就递减；E11-02 的 4 轮 round-trip 没有任何一条声称"persona-3 抓到 persona-1 漏的"。Opus 设了一个 leading indicator：E11-09 ≤2 轮 Codex APPROVE 即证 v2.3 已摊销，可以软化 5-persona。
.planning/constitution.md:343:| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1 (Tier-B)** | 跨-sub-phase 轮换：P1 → P2 → P3 → P4 → P5 → P1（默认起点 P1 Junior FCS）。Owner 可按 sub-phase 内容覆盖（demo-arc 重 → P3；适航 trace 重 → P4 等），但**不得在连续两个 Tier-B sub-phase 上跑同一 persona**。轮换状态记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`，新 epic 重置为 P1） |
.planning/constitution.md:368:**估计成本节约：** Tier-B 单 persona ~200k tokens / 子 phase；vs 默认 5-persona ~1M tokens / 子 phase。E11 phase 大致 4-5 个子 phase 中有 1 个会触发 Tier-A，其余 Tier-B → ~70–80% Codex token 节约 on persona pipeline。
.planning/constitution.md:372:1. 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B）

exec
/bin/zsh -lc "nl -ba .planning/codex_personas/README.md | sed -n '62,84p;120,133p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
exec
/bin/zsh -lc "nl -ba .planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md | sed -n '210,216p;314,318p'" in /Users/Zhuanz/Documents/Codex/2026-04-18-computer-use-plugin-computer-use-openai/ai-fantui-logicmvp
 succeeded in 0ms:
   210	
   211	### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"
   212	
   213	**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。
   214	
   215	**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware（governance bundle #2, 2026-04-25 起生效）：**Tier-A** 时每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding（within-PR uniqueness）；**Tier-B** 时 within-PR uniqueness N/A，bias 由跨-sub-phase 轮换（P1→P5→P1）+ §Surface Inventory grep 锚点 + RETRO §6.3 rollback 三层兜底承担。结论：bias 风险存在但已通过 distinct context + tier-aware anti-bias 机制 mitigated。
   216	
   314	
   315	1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
   316	2. ✅ §8 verification protocol 全部通过
   317	3. ✅ Codex persona review 给出 0 BLOCKER（每个 sub-phase 按 tier-trigger 决出的 Tier-A 5/5 或 Tier-B 1/1 verdict；governance bundle #2 后 Tier-B 跨-sub-phase 轮换 P1→P5）
   318	4. ✅ truth-engine 红线 0 触碰

 succeeded in 0ms:
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
    73	# Tier-B（1 persona 默认 — P1 Junior FCS）：
    74	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    75	  "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
    76	  > .planning/phases/<phase-id>/persona-P1-output.md 2>&1
    77	
    78	# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
    79	cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    80	  "$(cat .planning/codex_personas/P3-demo-presenter.md)" \
    81	  > .planning/phases/<phase-id>/persona-P3-output.md 2>&1
    82	```
    83	
    84	## Output convention
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
   131	If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7). The earlier "candidate §6.2 re-evaluate" framing is superseded — §6.3 is canonical.

