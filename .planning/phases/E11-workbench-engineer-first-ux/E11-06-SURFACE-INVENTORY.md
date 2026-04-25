# E11-06 Surface Inventory — state-of-the-world status bar

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Section eyebrow `state of world` | [ANCHORED] | `workbench.html` `#workbench-state-of-world-bar` (NEW) | Section identifier. |
| 2 | Field label `truth-engine SHA` | [ANCHORED] | `data-sow-field="truth_engine_sha"` | Sourced from `git rev-parse --short HEAD`. |
| 3 | Field label `recent e2e` | [ANCHORED] | `data-sow-field="recent_e2e"` | Sourced from `docs/coordination/qa_report.md`. |
| 4 | Field label `adversarial` | [ANCHORED] | `data-sow-field="adversarial"` | Sourced from `docs/coordination/qa_report.md`. |
| 5 | Field label `open issues` | [ANCHORED] | `data-sow-field="known_issues"` | Sourced from `docs/known-issues/` file count. |
| 6-9 | 4 placeholder values `…` | [ANCHORED] | `data-sow-value="…"` slots | Replaced by JS hydration. |
| 10 | Advisory flag `advisory · not a live truth-engine reading` | [ANCHORED] | trailing `.workbench-sow-flag` | Honesty contract — bar is NEVER a live truth-engine reading. |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 10 → ≥ 10 ✓
- **[REWRITE/DELETE] count** = 0 → < 3

Threshold not met (zero rewrites — this is a NEW section). → **Tier-B** (1-persona review).

E11-00-PLAN row E11-06 row 277 explicitly says "YES Codex (新 API 调用 / 状态聚合)". Tier-B with full 1-persona review honors that.

> **Verdict: Tier-B**. Persona = **P4 (V&V Engineer)** — round-robin successor of E11-04's P3, AND content-fit: this introduces a new endpoint (`/api/workbench/state-of-world`) with read-only contract that V&V should validate (status codes, payload shape, idempotency, no truth-engine mutation).

## Endpoint contract (locked by tests)

`GET /api/workbench/state-of-world` returns 200 with:

```json
{
  "kind": "advisory",
  "truth_engine_sha": "<git short sha>" | "unknown",
  "truth_engine_sha_source": "git rev-parse --short HEAD",
  "recent_e2e_label": "<X tests OK>" | "—",
  "recent_e2e_source": "docs/coordination/qa_report.md",
  "adversarial_label": "<X/X shared validation pass>" | "—",
  "adversarial_source": "docs/coordination/qa_report.md",
  "open_known_issues_count": <int >= 0>,
  "open_known_issues_source": "docs/known-issues/ (file count)",
  "last_executed_evidence": "<latest stamp>" | "—",
  "generated_at": "<ISO8601 Z>"
}
```

`POST /api/workbench/state-of-world` must return 404 or 405 (no mutation possible).

## Truth-engine red line

Files touched:
- `src/well_harness/demo_server.py` — adds `WORKBENCH_STATE_OF_WORLD_PATH` constant, `_truth_engine_short_sha()`, `_read_recent_evidence_lines()`, `_open_known_issues_count()`, `workbench_state_of_world_payload()`, GET handler. **Read-only**: never mutates state, only aggregates.
- `src/well_harness/static/workbench.html` — NEW status-bar section before wow starters
- `src/well_harness/static/workbench.css` — NEW `.workbench-state-of-world-bar*` selectors
- `src/well_harness/static/workbench.js` — NEW `hydrateStateOfWorldBar()` + DOMContentLoaded hook
- `tests/test_workbench_state_of_world_bar.py` — NEW (15 tests)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved. The new endpoint is explicitly classified as `kind: "advisory"` — it never claims to be a live truth-engine reading.
