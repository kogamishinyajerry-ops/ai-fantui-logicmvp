# E11-07 Surface Inventory — Authority Contract banner

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Banner icon `🔒` | [ANCHORED] | `#workbench-authority-banner` (NEW) | Always-visible truth-engine seal. |
| 2 | Banner headline `Truth Engine — Read Only` | [ANCHORED] | same section | Names the contract directly. |
| 3 | Banner rule `Propose 不修改 · 工程师只能提交 ticket / proposal，不能直接改真值` | [ANCHORED] | same section | The actual rule — propose only, never mutate. |
| 4 | Banner link label `v6.1 红线条款 →` | [ANCHORED] | `<a href="/v6.1-redline">` | Anchored to the new route. |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 4 → < 10
- **[REWRITE/DELETE] count** = 0 → < 3

Both thresholds NOT met. → **Tier-B** (1-persona review).

E11-00-PLAN row E11-07 explicitly says "不（仅 UI banner，不动 code）". Tier-B with one persona review is the conservative middle ground.

> **Verdict: Tier-B**. Persona = **P5 (Apps Engineer)** — round-robin successor of E11-06's P4 AND content-fit: the banner is the customer/repro-facing authority contract; P5 should validate the messaging is unambiguous from the customer/new-engineer perspective and that the link target is real.

## New endpoint contract

`GET /v6.1-redline` (and `/v6.1-redline.txt`) returns 200 plain-text excerpt of the v6.1 truth-engine red-line clause. Sourced live from `.planning/constitution.md` so the rendered text never drifts from the constitution's words. Falls back to a small static excerpt if the constitution is unreachable, so the banner never produces a 404.

The excerpt MUST name at least one of the four off-limits paths (controller / runner / models / adapters) — locked by `test_v61_redline_excerpt_carries_truth_engine_paths`.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` — NEW `<aside id="workbench-authority-banner">` between annotation toolbar and 3-column grid
- `src/well_harness/static/workbench.css` — NEW `.workbench-authority-banner*` selectors
- `src/well_harness/demo_server.py` — NEW route `/v6.1-redline` + `_serve_v61_redline_excerpt()` helper. **Read-only**: never mutates state, only reads `.planning/constitution.md`.
- `tests/test_workbench_authority_banner.py` — NEW (12 tests)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new banner *names* the truth-engine red line — this is the meta-statement, not a violation.
