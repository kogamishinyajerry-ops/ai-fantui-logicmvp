# E11-03 Surface Inventory — three-column rename

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Column 1 title: `Scenario Control` → `Probe & Trace · 探针与追踪` | [REWRITE] | `workbench.html` `#workbench-control-panel <h2>` | Engineer-task verb pair replaces technical noun. |
| 2 | Column 1 eyebrow: `control panel` → `probe & trace` | [REWRITE] | `workbench.html` `#workbench-control-panel .eyebrow` | Lowercase match for visible chrome consistency. |
| 3 | Column 1 boot status: `Waiting for control panel boot.` → `Waiting for probe & trace panel boot.` | [REWRITE] | `workbench.html` `#workbench-control-status` | Default copy before JS hydrates. |
| 4 | Column 1 JS boot: `Control panel ready. Scenario actions are staged for E07+.` → `Probe & Trace ready. Scenario actions are staged for E07+.` | [REWRITE] | `workbench.js:bootWorkbenchControlPanel` | Status after hydration. |
| 5 | Column 2 title: `Spec Review Surface` → `Annotate & Propose · 标注与提案` | [REWRITE] | `workbench.html` `#workbench-document-panel <h2>` | Maps to text-range annotation flow. |
| 6 | Column 2 eyebrow: `document` → `annotate & propose` | [REWRITE] | `workbench.html` `#workbench-document-panel .eyebrow` | |
| 7 | Column 2 boot status: `Waiting for document panel boot.` → `Waiting for annotate & propose panel boot.` | [REWRITE] | `workbench.html` `#workbench-document-status` | |
| 8 | Column 2 JS boot: `Document panel ready. Text-range annotation arrives in E07.` → `Annotate & Propose ready. Text-range annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchDocumentPanel` | |
| 9 | Column 3 title: `Logic Circuit Surface` → `Hand off & Track · 移交与跟踪` | [REWRITE] | `workbench.html` `#workbench-circuit-panel <h2>` | Maps to ticket handoff flow. |
| 10 | Column 3 eyebrow: `circuit` → `hand off & track` | [REWRITE] | `workbench.html` `#workbench-circuit-panel .eyebrow` | |
| 11 | Column 3 boot status: `Waiting for circuit panel boot.` → `Waiting for hand off & track panel boot.` | [REWRITE] | `workbench.html` `#workbench-circuit-status` | |
| 12 | Column 3 JS boot: `Circuit panel ready. Overlay annotation arrives in E07.` → `Hand off & Track ready. Overlay annotation arrives in E07.` | [REWRITE] | `workbench.js:bootWorkbenchCircuitPanel` | |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 12 → ≥ 10 ✓
- **[REWRITE/DELETE] count** = 12 (all rows) → ≥ 3 ✓

> **Verdict: Tier-A** (5-persona review).

This is exactly the rename-pure case the Tier-A trigger was designed for: every visible string on three structural surfaces is being rewritten in lockstep. Tier-A is the conservative routing.

## Stable-ID invariants (must hold)

The plan explicitly says "保留底层 ID 不变以免 e2e 测试失效" — every one of these anchors stays untouched:

- `id="workbench-control-panel"`, `id="workbench-document-panel"`, `id="workbench-circuit-panel"`
- `data-column="control"`, `data-column="document"`, `data-column="circuit"`
- `data-annotation-surface="control"`, `data-annotation-surface="document"`, `data-annotation-surface="circuit"`
- `id="workbench-control-status"`, `id="workbench-document-status"`, `id="workbench-circuit-status"`

`tests/test_workbench_column_rename.py` locks all 12 stable anchors alongside the new visible copy so a future "polish" pass can't silently regress either side.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` (3 [REWRITE] blocks, 12 visible-copy lines)
- `src/well_harness/static/workbench.js` (3 [REWRITE] boot status strings)
- `tests/test_workbench_column_rename.py` (NEW)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.
