# E11-04 Surface Inventory — annotation vocabulary upgrade

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Toolbar label: `Annotation` → `标注` | [REWRITE] | `workbench.html` `.workbench-annotation-toolbar-label` | Generic English noun → domain-anchored Chinese verb. |
| 2 | Button: `Point` → `标记信号` | [REWRITE] | `data-annotation-tool="point"` button | Mark a signal. |
| 3 | Button: `Area` → `圈选 logic gate` | [REWRITE] | `data-annotation-tool="area"` button | Encircle a logic gate. |
| 4 | Button: `Link` → `关联 spec` | [REWRITE] | `data-annotation-tool="link"` button | Link to a spec. |
| 5 | Button: `Text Range` → `引用 requirement 段` | [REWRITE] | `data-annotation-tool="text-range"` button | Cite a requirement section. |
| 6 | Default active-tool copy: `Point tool active` → `标记信号 工具激活` | [REWRITE] | `#workbench-annotation-active-tool` | Pre-hydration default. |
| 7 | JS active-tool template: `${tool} tool active` → `${label} 工具激活` | [REWRITE] | `annotation_overlay.js:setActiveTool` | Maps tool ID via TOOL_DOMAIN_LABEL. |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 7 → < 10
- **[REWRITE/DELETE] count** = 7 → ≥ 3

Both thresholds NOT met (copy_diff_lines fails). → **Tier-B** (1-persona review).

E11-00-PLAN row E11-04 row 275 explicitly classifies this as "NO Codex (mechanical relabel)". The strict tier-trigger rule on the books is Tier-B; running a single-persona review is the conservative middle ground that honors both constraints.

> **Verdict: Tier-B**. Per `PERSONA-ROTATION-STATE.md` round-robin successor, the next slot is determined after Tier-A E11-03 ran (rotation pointer unchanged).
>
> **Persona selection: P5 (Apps Engineer)** — domain-anchoring is exactly the customer/repro lens this relabel is meant to serve; P5 round-robin slot also follows P2 (the last Tier-B was E11-14 = P2; round-robin successor is P3, but E11-13 was P1 and E11-14 was P2 — actually next is P3). However content-fit weight: P3 (Demo Presenter) is a better content match for "domain-anchored vocabulary the engineer/customer reads on screen". Plan defers to round-robin: **P3 Demo Presenter**.

(Note: the constitution allows owner-override of round-robin when content motivates it. Either P3 or P5 is defensible; round-robin is the safer default.)

## Stable-ID invariants (must hold)

The plan explicitly says "UI 仍用 point/area/link/text-range 作为底层类型". Every one of these stays untouched:

- `data-annotation-tool="point"`
- `data-annotation-tool="area"`
- `data-annotation-tool="link"`
- `data-annotation-tool="text-range"`
- `id="workbench-annotation-toolbar"`
- `id="workbench-annotation-active-tool"`

`tests/test_workbench_annotation_vocab.py` locks all 6 stable anchors alongside the new visible copy.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.html` (1 [REWRITE] block, 6 visible-copy lines)
- `src/well_harness/static/annotation_overlay.js` (1 [REWRITE] for the status template + new TOOL_DOMAIN_LABEL map)
- `tests/test_workbench_annotation_vocab.py` (NEW, 20 tests)

Files NOT touched: `controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`. Truth-engine boundary preserved.
