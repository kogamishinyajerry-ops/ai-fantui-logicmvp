# Shelved: Multi-System Demo UI (2026-04-22)

## What was shelved

The **pre-unification** form of `src/well_harness/static/demo.html` (+ `demo.js`
+ `demo.css`) together with the multi-system switcher tests. These held the
"反推演示舱" as a monolithic demo with 3 non-thrust-reverser domains (landing
gear / bleed air / EFDS countermeasure flare) selectable via a dropdown, plus
extensive presenter narrative blocks.

## Why

User directive (2026-04-22):

> "虽然反推的逻辑演示舱功能完备，但是很多文字性的说明窗口全都是多余的，
>  尤其是演示路径、推理结果、结果摘要、诊断问答等等，我只想关注参数面板
>  和逻辑控制链路"
>
> "反推的逻辑演示舱里还是暴露了起落架、液压、干扰弹的控制链路，我已经不想
>  看到那些了"

Scope:
- Multi-system switcher (`#system-selector` + `landing-gear-inputs`,
  `bleed-air-inputs`, `efds-inputs`, `c919-etras` sections inside demo.html)
  is out-of-scope for the new slim thrust-reverser workstation
- Presenter narrative panels (`presenter-run-card`, `chain-inspector`,
  `result-grid`, `monitor-panel` / timeline) contained
  演示走查路径 / 推理结果 / 结果摘要 / 诊断问答 — all declared 废话 by user
- Timeline under `monitor-panel` is 搁置 (not deleted) — user said later
  development will need it back

Not reactivated unless explicit user request.

## Snapshot contents

### `static/` (verbatim pre-restructure copies)
| Archived file | Original path | Bytes |
|---|---|---|
| legacy-demo.html | src/well_harness/static/demo.html | 136 KB |
| legacy-demo.js | src/well_harness/static/demo.js | 82 KB |
| legacy-demo.css | src/well_harness/static/demo.css | 69 KB |

### `tests/` (moved)
| Archived file | Original path |
|---|---|
| test_system_switcher_smoke.py | tests/test_system_switcher_smoke.py |

*(Also: test_demo.py keeps non-archived tests in place; assertions on removed
sections are deleted.)*

### `docs/`
| Archived file | Original path |
|---|---|
| (none yet — add if user references archived docs) | — |

## Domain scopes shelved

### `landing-gear-inputs`
- Inputs: `gear_handle_position`, `hydraulic_pressure_psi`, `uplock_released`,
  `gear_position_percent`, `downlock_engaged`
- Adapter (live): `src/well_harness/adapters/landing_gear_adapter.py`
- Panel HTML: lines 472–560 of legacy-demo.html

### `bleed-air-inputs`
- Inputs: bleed-air valve controls (see `bleed_air_adapter.py`)
- Panel HTML: lines 563+ of legacy-demo.html

### `efds-inputs` (countermeasure flare / 干扰弹)
- Inputs: `pilot_arm_switch`, `mode_selector`, `deployment_enable`, etc.
- Adapter (live): `src/well_harness/adapters/efds_adapter.py`
- Panel HTML + FBD narrative: lines 648+ of legacy-demo.html

### Narrative UI blocks
- `presenter-run-card` (Presenter Run Card, 演示走查路径 + boundary hints)
- `chain-inspector` (高亮详细解释 + 当前结论 3-rail result summary)
- `result-grid` (结果摘要 + 推理结果 card)
- `monitor-panel` (状态 vs 时间 timeline)

## Restoration guide

If user requests revival:

1. Check user scope: full multi-system UI vs single panel back (e.g., just
   timeline under the new slim demo).

2. **Single-panel back** (most likely — timeline): extract the relevant
   `<section class="monitor-panel">` block from `legacy-demo.html` + its
   accompanying CSS + the timeline JS in `legacy-demo.js`. Graft into the
   current `src/well_harness/static/demo.html` ETRAS-style grid as an
   additional right-column panel. Keep a single-scope (thrust-reverser only)
   signal set.

3. **Full multi-system back**: `cp archive/shelved/multi-system-ui/static/legacy-demo.* src/well_harness/static/` then reconcile with any subsequent
   unified-nav / style changes. Adapters (`landing_gear_adapter.py`,
   `bleed_air_adapter.py`, `efds_adapter.py`) are still live — revival does
   not touch adapter code.

4. **Tests**: restore `tests/test_system_switcher_smoke.py` from
   `archive/shelved/multi-system-ui/tests/`. May need to update for any
   unified-nav changes.

## Live dependencies NOT shelved

- `src/well_harness/adapters/landing_gear_adapter.py` — still live
- `src/well_harness/adapters/bleed_air_adapter.py` — still live
- `src/well_harness/adapters/efds_adapter.py` — still live
- `src/well_harness/demo_server.py` — POST `/api/system-snapshot` still
  accepts `system_id=landing-gear / bleed-air / efds` for future revival
- Non-UI tests for these adapters (in `tests/`) — still run

## Related shelves

- `archive/shelved/llm-features/` — Phase A (2026-04-22) shelved chat/P14/P15
- This shelf complements it by removing non-thrust-reverser UI surfaces.
