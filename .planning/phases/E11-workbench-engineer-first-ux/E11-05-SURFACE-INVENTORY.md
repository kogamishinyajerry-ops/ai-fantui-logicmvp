# E11-05 Surface Inventory — wow_a/b/c canonical-scenario starter cards

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Records every user-facing string introduced by E11-05 and classifies each per the [ANCHORED/REWRITE/DELETE] taxonomy so the Tier-A vs Tier-B routing decision is auditable.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | `<h2>起手卡 · One-click 走读</h2>` | [ANCHORED] | `workbench.html` `<section id="workbench-wow-starters">` (NEW) | Section heading; visible only on /workbench shell page. |
| 2 | "预填 BEAT_DEEP_PAYLOAD / Monte-Carlo / Reverse-Diagnose 入口…" sub-header | [ANCHORED] | same section header | Description of what the cards do. |
| 3 | `<h3>Causal Chain · 因果链走读</h3>` | [ANCHORED] | `workbench-wow-a-title` (NEW) | wow_a card title, anchored to `tests/e2e/test_wow_a_causal_chain.py`. |
| 4 | wow_a description "POST /api/lever-snapshot with BEAT_DEEP_PAYLOAD…" | [ANCHORED] | `tests/e2e/test_wow_a_causal_chain.py:51` `BEAT_DEEP_PAYLOAD` | Truth claim about endpoint + payload shape. |
| 5 | wow_a button "一键运行 wow_a" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
| 6 | `<h3>Monte Carlo · 1000-trial 可靠性</h3>` | [ANCHORED] | `workbench-wow-b-title` (NEW) | wow_b card title, anchored to `tests/e2e/test_wow_b_monte_carlo.py`. |
| 7 | wow_b description "POST /api/monte-carlo/run with seed=42…" | [ANCHORED] | `tests/e2e/test_wow_b_monte_carlo.py:_run` | Truth claim about endpoint + payload + seed. |
| 8 | wow_b button "一键运行 wow_b" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
| 9 | `<h3>Reverse Diagnose · 反向诊断</h3>` | [ANCHORED] | `workbench-wow-c-title` (NEW) | wow_c card title, anchored to `tests/e2e/test_wow_c_reverse_diagnose.py`. |
| 10 | wow_c description "POST /api/diagnosis/run with outcome=deploy_confirmed…" | [ANCHORED] | `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed_returns_nonempty_results` | Truth claim about endpoint + outcome + max_results. |
| 11 | wow_c button "一键运行 wow_c" | [ANCHORED] | `data-wow-action="run"` button | Action label. |
| 12 | "尚未运行。" placeholder × 3 | [ANCHORED] | per-card `data-wow-result-for=*` pane | Initial result-pane copy. |
| 13 | `workbench_start.html` line ~69: "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" → "wow_a/b/c 起手卡片已上线（E11-05），见 /workbench 顶部「起手卡」" | [REWRITE] | `workbench_start.html:69` | Now that E11-05 ships, the placeholder is updated to a positive claim. |
| 14 | `workbench_start.html` line ~108: "wow_a/b/c 目前只在 tests/e2e/test_wow_a_causal_chain.py 里有，没有 UI 走读 surface" → "wow_a/b/c 起手卡 已在 /workbench 顶部上线（E11-05）…" | [REWRITE] | `workbench_start.html:107-108` | Removes the negative claim that no UI走读 surface exists. |
| 15 | `workbench_start.html` line ~113: "无-chrome demo mode + UI wow_a 走读 进入 E11-05/08 范围" → "无-chrome demo mode 进入 E11-08 范围（wow_a 走读 已 E11-05 完成）" | [REWRITE] | `workbench_start.html:113` | Removes the implicit claim that wow_a走读 is still pending; demarcates remaining E11-08 scope. |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 15 (all enumerated rows above) → ≥ 10 ✓
- **[REWRITE/DELETE] count** = 3 (rows 13, 14, 15) → ≥ 3 ✓ ← edge case

> **Verdict: Tier-A** (5-persona review).

Both thresholds are met: the 3 [REWRITE] lines on `workbench_start.html` are doc-truth corrections (placeholder copy that previously claimed E11-05 wasn't shipped). Per the rule's spirit — protect against stale copy reaching production — Tier-A is the conservative routing here.

> **Action: dispatch all 5 personas (P1–P5) for E11-05.**

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` (NEW section only)
- `src/well_harness/static/workbench.css` (NEW selectors only)
- `src/well_harness/static/workbench.js` (NEW WOW_SCENARIOS const + runWowScenario + installWowStarters + 1 hook line in DOMContentLoaded)
- `src/well_harness/static/workbench_start.html` (3 [REWRITE] lines documenting that E11-05 has shipped)
- `tests/test_workbench_wow_starters.py` (NEW)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.
