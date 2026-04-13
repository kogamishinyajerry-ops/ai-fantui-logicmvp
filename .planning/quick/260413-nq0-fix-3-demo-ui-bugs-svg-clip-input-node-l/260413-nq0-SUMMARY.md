# Quick Task 260413-nq0: Fix 3 Demo UI Bugs

## Summary

Fixed 3 demo UI bugs in the thrust-reverser chain topology SVG and controller adapter.

### One-liner
SVG viewBox expanded to 480px, 9 input conditions exposed to frontend, and spurious NotDep node removed from the chain topology.

## Changes

### Task 1: Fix SVG viewBox height (320→480)
- **File:** `src/well_harness/static/demo.html`
- **Change:** `viewBox="0 0 900 320"` → `viewBox="0 0 900 480"` for the thrust-reverser SVG
- **Why:** TRA value text at y=432 and N1K/TRA rows were being clipped; 320px height was too small
- **Commit:** `e3f317c`

### Task 2: Add 9 input conditions to asserted_component_values
- **File:** `src/well_harness/controller_adapter.py`
- **Change:** Added 9 raw input signals to `asserted_component_values` in `ReferenceDeployControllerAdapter.evaluate_snapshot()`:
  - Boolean toggles: `sw1`, `sw2`, `engine_running`, `aircraft_on_ground`, `eec_enable`, `reverser_inhibited`
  - Numeric values: `radio_altitude_ft`, `n1k`, `tra_deg`
- **Why:** Frontend `applySystemNodeStates()` reads from `asserted_component_values` to light up input nodes; previously only output commands were included
- **Commit:** `5b8e9f0`

### Task 3: Remove NotDep SVG node + L1 connection line
- **File:** `src/well_harness/static/demo.html`
- **Change:** Removed `reverser_not_deployed_eec` node (rect, label, value text) and its `x1="82" y1="153" x2="110" y2="70"` L1 input connection line
- **Why:** `reverser_not_deployed_eec` is a plant output derived from `deploy_position_percent==0`, not an independent L1 input; rendering it as an input node was semantically incorrect
- **Commit:** `54c950f`

## Verification

**Automated checks:**
```bash
# Task 1
grep -n 'viewBox="0 0 900 480"' src/well_harness/static/demo.html  # FOUND at line 327

# Task 3
grep -c 'data-node="reverser_not_deployed_eec"' src/well_harness/static/demo.html  # 0 (removed)
```

**Test suite:** `python3 -m pytest tests/test_demo.py -v` → **92 passed**

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | `e3f317c` | fix(quick): increase SVG viewBox height from 320 to 480 |
| 2 | `5b8e9f0` | feat(quick): expose 9 input conditions in asserted_component_values |
| 3 | `54c950f` | fix(quick): remove NotDep node and its L1 connection line |

## Deviation from Plan

None - plan executed exactly as written.
