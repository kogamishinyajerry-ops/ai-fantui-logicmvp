# Phase P13: Route B — Browser Workbench Multi-System Integration

**Researched:** 2026-04-13
**Domain:** Browser UI multi-system switching for control-system workbench
**Confidence:** MEDIUM

## Summary

P13 extends the existing single-system demo UI (thrust-reverser only) to support switching among three onboarded control systems: thrust-reverser, landing-gear, and bleed-air valve. Each system shares the same `GenericControllerTruthAdapter` protocol interface (`load_spec()` + `evaluate_snapshot()`), so the server-side adapter boundary is already generalization-ready. The primary work is on the browser side: adding a system selector, making `chain-panel` and `result-grid` data-driven from the spec, and wiring a new API endpoint to serve system-specific snapshots.

**Primary recommendation:** Add a system-switcher dropdown to the hero/header, create one new `/api/system-snapshot` endpoint that accepts `{ system_id }` and returns `{ spec, nodes, summary }` (replacing the hardcoded thrust-reverser nodes array), and make the chain-panel HTML dynamic based on `spec.logic_nodes` instead of the current static HTML chain.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask / `http.server` | stdlib | `DemoRequestHandler` — existing API server | Already in `demo_server.py` |
| `GenericControllerTruthAdapter` protocol | v1 | Shared adapter interface across all three systems | Already established in P8/P10/P12 |
| `workbench_spec_to_dict()` | v1 | Serializes `ControlSystemWorkbenchSpec` to JSON | Already used for bootstrap payload |

### Three Systems (all share same adapter interface)
| System | Adapter Class | Key Inputs | Key Outputs |
|--------|--------------|------------|-------------|
| thrust-reverser | `ReferenceDeployControllerAdapter` | `ResolvedInputs` (21 fields) | `ControllerOutputs` (6 cmds) |
| landing-gear | `LandingGearControllerAdapter` | `gear_handle_position`, `hydraulic_pressure_psi`, `uplock_released`, `gear_position_percent`, `downlock_engaged` | `selector_valve_cmd`, `extend_actuator_cmd` |
| bleed-air valve | `BleedAirValveControllerAdapter` | `valve_position`, `inlet_pressure`, `outlet_pressure`, `control_unit_ready` | `valve_cmd` |

---

## Architecture Patterns

### Recommended Project Structure
```
src/well_harness/
  demo_server.py          # Add: /api/system-snapshot endpoint + system registry
  adapters/
    landing_gear_adapter.py   # Already exists
    bleed_air_adapter.py     # Already exists
    controller_adapter.py     # Reference adapter (thrust-reverser)
static/
  demo.html               # Add: system-switcher in hero/header
  demo.js                 # Refactor: chain-panel and nodes array to be data-driven
  demo.css                # Add: system-switcher styling
```

### Pattern 1: System Switcher (Browser-side)
- Add a `<select id="system-selector">` in the hero or panel header
- Three options: `thrust-reverser` / `landing-gear` / `bleed-air`
- On change: fetch `/api/system-snapshot?system_id=<id>`, then re-render chain-panel and reset condition inputs
- Default to `thrust-reverser` on page load (existing behavior unchanged)

### Pattern 2: New Server Endpoint
`GET /api/system-snapshot?system_id=<id>` returns:
```json
{
  "system_id": "landing_gear",
  "title": "Minimal Landing-Gear Extension Control",
  "spec": { /* full workbench spec dict from load_spec() */ },
  "nodes": [ /* spec-driven nodes array */ ],
  "default_snapshot": { /* a default/initial snapshot for the system */ },
  "inputs_config": { /* numeric/bool input definitions for the system */ }
}
```
The `nodes` array is built dynamically from `spec.logic_nodes` + `spec.components` — replacing the hardcoded 14-node array in `demo_server.py lever_snapshot_payload()`.

### Pattern 3: Chain-Panel Data-Driven Rendering
Current: `.chain-map` is a static HTML sequence of `<div data-node="sw1">SW1</div>` hardcoded for thrust-reverser.
Needed: JavaScript renders the chain from the spec's `logic_nodes` and `components` on system switch. Each system defines its own node topology — landing-gear has 2 logic nodes, bleed-air has 2, thrust-reverser has 4.

### Pattern 4: Result Grid — QA Answer per System
Current: `demo.py` `answer_demo_prompt()` is hardcoded to thrust-reverser `NODE_CATALOG`. For P13, the QA drawer either:
- A) Stays thrust-reverser-only (acceptable per exit criteria — only chain-panel and snapshot state need multi-system support)
- B) Gets a simplified per-system answer path using `GenericTruthEvaluation.blocked_reasons` and `GenericTruthEvaluation.summary`

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Multi-system snapshot | Custom per-system evaluation code paths | `GenericTruthEvaluation` from `evaluate_snapshot()` | Already returns `system_id`, `active_logic_node_ids`, `blocked_reasons`, `summary` generically |
| Chain visualization | New SVG/canvas renderer | Build chain from `spec.components` + `spec.logic_nodes` dynamically | Spec already contains all node IDs, labels, downstream relationships |
| System routing | Hardcoded if/elif on system_id | Factory registry dict: `SYSTEMS = {"thrust-reverser": build_reference_controller_adapter(), "landing-gear": build_landing_gear_controller_adapter(), "bleed-air": build_bleed_air_controller_adapter()}` | Adding new systems only requires adding one entry |

---

## Common Pitfalls

### Pitfall 1: Chain-Panel Hardcoded for Thrust-Reverser
**What goes wrong:** The `.chain-map` HTML and the `nodes` array in `lever_snapshot_payload()` are entirely hardcoded for thrust-reverser (14 nodes, specific IDs like `sw1`, `logic1`, etc.).
**How to avoid:** On system switch, regenerate both the spec-driven node list and the HTML chain from `spec.logic_nodes` + `spec.components`. Do not try to reuse the existing static HTML structure across systems.

### Pitfall 2: Condition Panel Inputs Don't Match Non-Thrust-Reverser Systems
**What goes wrong:** The current condition panel (`#condition-ra`, `#condition-n1k`, toggles) is specific to thrust-reverser `ResolvedInputs`. Landing-gear needs `gear_handle_position`, `hydraulic_pressure_psi`; bleed-air needs `inlet_pressure`, `valve_position`, `control_unit_ready`.
**How to avoid:** Either (a) replace the condition panel with a generic input form rendered from `spec.components` on system switch, or (b) accept that only thrust-reverser has the full interactive condition panel and other systems show a read-only snapshot state. Option (b) is simpler and acceptable for P13.

### Pitfall 3: `demo.py` `NODE_CATALOG` is Single-System
**What goes wrong:** `answer_demo_prompt()` and the QA drawer are entirely coupled to the thrust-reverser `NODE_CATALOG` and `DemoNode` definitions. These cannot serve landing-gear or bleed-air without a complete rewrite.
**Mitigation:** P13 exit criteria only requires chain-panel + snapshot state + answer payload per system. The QA drawer can remain thrust-reverser-only for P13, with a follow-on phase extending `answer_demo_prompt()` per-system or replacing it with `GenericTruthEvaluation`-based answers.

### Pitfall 4: Session State Not Isolated Between System Switches
**What goes wrong:** If a user switches systems while a lever position or condition is active, stale thrust-reverser state bleeds into the new system's view.
**How to avoid:** On system switch, reset all HUD, chain-panel, and result areas to the `default_snapshot` from `/api/system-snapshot`. Treat system switch as a full state reset.

---

## Code Examples

### New endpoint skeleton in `demo_server.py`
```python
SYSTEM_REGISTRY = {
    "thrust-reverser": build_reference_controller_adapter,
    "landing-gear": build_landing_gear_controller_adapter,
    "bleed-air": build_bleed_air_controller_adapter,
}

def system_snapshot_payload(system_id: str) -> dict:
    builder = SYSTEM_REGISTRY.get(system_id)
    if builder is None:
        return {"error": "unknown_system"}
    adapter = builder()
    spec = adapter.load_spec()
    # Build nodes from spec dynamically
    nodes = _spec_to_nodes(spec)
    default_snapshot = _default_snapshot_for_system(system_id)
    return {
        "system_id": system_id,
        "title": spec["title"],
        "spec": spec,
        "nodes": nodes,
        "default_snapshot": default_snapshot,
    }
```

### Chain-panel HTML rendered dynamically from spec (JS)
```javascript
function renderChainMap(spec) {
  const chainMap = document.querySelector('.chain-map');
  chainMap.innerHTML = '';
  for (const node of spec.components) {
    const div = document.createElement('div');
    div.className = 'chain-node';
    div.dataset.node = node.id;
    div.textContent = node.label;
    chainMap.appendChild(div);
  }
}
```

### `GenericTruthEvaluation` is already system-agnostic
```python
# All three adapters return this shape:
GenericTruthEvaluation(
    system_id="landing_gear",          # which system
    active_logic_node_ids=("lg_l1_handle_and_pressure",),  # which nodes active
    asserted_component_values={...},  # all component values
    completion_reached=False,
    blocked_reasons=("uplock_released is still false",),
    summary="Landing gear extension remains blocked or incomplete.",
)
```

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The condition panel can be simplified to read-only for non-thrust-reverser systems in P13 | Common Pitfalls | If users expect full interactivity for all three systems, this is insufficient |
| A2 | QA drawer remains thrust-reverser-only for P13 | Common Pitfalls | If P13 exit criteria require full multi-system QA, this underdelivers |
| A3 | No changes needed to `well_harness/controller.py` or `demo.py` for P13 | Don't Hand-Roll | If QA or demo answers need multi-system support, these files require changes |

---

## Open Questions

1. **Should the condition panel be interactive for landing-gear and bleed-air, or read-only?**
   - What we know: Landing-gear needs `gear_handle_position` (UP/DOWN toggle) and `hydraulic_pressure_psi` (slider). Bleed-air needs `inlet_pressure`, `outlet_pressure`, `control_unit_ready`. These differ significantly from thrust-reverser's 9 inputs.
   - What's unclear: Whether P13 exit criteria require full interactive condition panels for all three systems, or read-only display is acceptable.
   - Recommendation: Build a minimal interactive form for landing-gear (2-3 inputs) and read-only display for bleed-air, as a middle path.

2. **What should the QA drawer show for non-thrust-reverser systems?**
   - What we know: `GenericTruthEvaluation` provides `summary` and `blocked_reasons` generically.
   - What's unclear: Whether a generic `blocked_reasons` + `summary` display satisfies the "answer payload per system" exit criterion, or whether a full `answer_demo_prompt()` equivalent is needed.
   - Recommendation: Show `GenericTruthEvaluation.summary` and `blocked_reasons` as a simple read-only answer for non-thrust-reverser systems.

3. **Should system switch reset all UI state or preserve cross-system context?**
   - What's unclear: Whether users expect to compare systems side-by-side or whether each switch is a clean slate.
   - Recommendation: Full reset on switch (cleanest, simplest for P13).

---

## Environment Availability

Step 2.6: SKIPPED (no external dependencies beyond the existing Python environment already validated in P8/P10/P12).

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pytest.ini` at repo root |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P13-01 | System-switcher UI element exists | smoke | `grep 'system-selector' src/well_harness/static/demo.html` | TBD |
| P13-02 | `/api/system-snapshot` returns valid spec for all 3 systems | unit | `pytest tests/test_demo_server.py::test_system_snapshot_all_systems -x` | TBD |
| P13-03 | Chain-panel renders from spec on system switch | smoke | `grep 'renderChainMap' src/well_harness/static/demo.js` | TBD |
| P13-04 | Landing-gear and bleed-air adapters pass `load_spec()` without error | unit | `pytest tests/test_adapters.py -k "bleed_air or landing_gear" -x` | existing |
| P13-05 | 23 shared validation commands continue to pass | regression | `make validate 2>&1 | tail -5` | existing |

### Wave 0 Gaps
- [ ] `tests/test_demo_server.py` — add `test_system_snapshot_all_systems`
- [ ] `tests/test_demo_server.py` — add `test_system_switcher_ui_present`
- [ ] `src/well_harness/static/demo.js` — add `renderChainMap` function
- [ ] Framework install: already present (pytest confirmed in P8/P10/P12)

---

## Sources

### Primary (HIGH confidence)
- `src/well_harness/demo_server.py` — current API endpoints, `lever_snapshot_payload()` with hardcoded nodes
- `src/well_harness/static/demo.html` — current hardcoded chain-panel HTML structure
- `src/well_harness/controller_adapter.py` — `GenericControllerTruthAdapter` protocol and `GenericTruthEvaluation` dataclass
- `src/well_harness/adapters/landing_gear_adapter.py` — landing-gear adapter implementing the generic protocol
- `src/well_harness/adapters/bleed_air_adapter.py` — bleed-air adapter implementing the generic protocol

### Secondary (MEDIUM confidence)
- `.planning/ROADMAP.md` P13 exit criteria — confirms what needs to be delivered

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all three systems share the same `GenericControllerTruthAdapter` protocol confirmed by reading all three adapter files
- Architecture: MEDIUM — chain-panel data-driven rendering approach is sound but the condition panel strategy for non-thrust-reverser systems needs user decision
- Pitfalls: MEDIUM — `demo.py` QA coupling to thrust-reverser is a real gap but may be acceptable per exit criteria

**Research date:** 2026-04-13
**Valid until:** 2026-05-13 (30 days — system architecture is stable)
