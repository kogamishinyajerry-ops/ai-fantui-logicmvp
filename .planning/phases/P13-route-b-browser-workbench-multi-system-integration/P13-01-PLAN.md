---
phase: P13
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - src/well_harness/demo_server.py
  - src/well_harness/static/demo.html
  - src/well_harness/static/demo.js
  - src/well_harness/static/demo.css
autonomous: true
requirements:
  - P13-EXIT-01
  - P13-EXIT-02
  - P13-EXIT-03
  - P13-EXIT-04
  - P13-EXIT-05

must_haves:
  truths:
    - "System switcher exists in demo UI hero/header"
    - "Switching system clears chain-panel, HUD, and results to default state"
    - "Chain-panel renders dynamically from spec.logic_nodes + spec.components for each system"
    - "QA drawer shows GenericTruthEvaluation.summary + blocked_reasons for non-thrust-reverser systems"
  artifacts:
    - path: "src/well_harness/demo_server.py"
      provides: "SYSTEM_REGISTRY, /api/system-snapshot endpoint, _spec_to_nodes helper"
      exports: ["SYSTEM_REGISTRY", "system_snapshot_payload", "_spec_to_nodes"]
    - path: "src/well_harness/static/demo.html"
      provides: "System switcher <select> in hero section"
      contains: "id=\"system-selector\""
    - path: "src/well_harness/static/demo.js"
      provides: "System switch handler, renderChainMap(), resetUIState()"
      contains: "system-selector"
    - path: "src/well_harness/static/demo.css"
      provides: "System switcher styling"
      contains: ".system-selector"
  key_links:
    - from: "src/well_harness/static/demo.html"
      to: "demo.js"
      via: "onchange=\"handleSystemSwitch(this.value)\""
      pattern: "handleSystemSwitch"
    - from: "demo.js handleSystemSwitch()"
      to: "/api/system-snapshot"
      via: "fetch() call"
      pattern: "fetch.*system-snapshot"
    - from: "/api/system-snapshot response"
      to: "renderChainMap()"
      via: "nodes array from response.spec"
      pattern: "renderChainMap.*spec"
---

<objective>
Extend the single-system demo UI (thrust-reverser only) to support switching among three control systems: thrust-reverser, landing-gear, and bleed-air. Each system shares the GenericControllerTruthAdapter protocol, so the primary work is: (1) add system-switcher UI, (2) add /api/system-snapshot endpoint that serves spec-driven node arrays per system, (3) make chain-panel data-driven from spec instead of hardcoded HTML, (4) show GenericTruthEvaluation-based answer for non-thrust-reverser systems. Condition panel stays thrust-reverser-only (read-only for others per P13 decisions).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/well_harness/demo_server.py        # Add SYSTEM_REGISTRY + /api/system-snapshot + _spec_to_nodes
@src/well_harness/static/demo.html       # Add <select id="system-selector"> in hero
@src/well_harness/static/demo.js         # Add handleSystemSwitch, renderChainMap, resetUIState
@src/well_harness/static/demo.css        # Add .system-selector styling
@src/well_harness/controller_adapter.py  # GenericControllerTruthAdapter protocol, GenericTruthEvaluation
@src/well_harness/adapters/landing_gear_adapter.py  # LandingGearControllerAdapter.load_spec(), evaluate_snapshot()
@src/well_harness/adapters/bleed_air_adapter.py     # BleedAirValveControllerAdapter.load_spec(), evaluate_snapshot()

# Key types the executor needs:
GenericTruthEvaluation:
  system_id: str
  active_logic_node_ids: tuple[str, ...]
  asserted_component_values: dict[str, Any]
  completion_reached: bool
  blocked_reasons: tuple[str, ...]
  summary: str

ControlSystemWorkbenchSpec (from system_spec.py):
  components: tuple[ComponentSpec, ...]   # each has id, label, kind, state_shape, unit
  logic_nodes: tuple[LogicNodeSpec, ...]   # each has id, label, description, downstream_component_ids
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add /api/system-snapshot endpoint + SYSTEM_REGISTRY in demo_server.py</name>
  <files>src/well_harness/demo_server.py</files>
  <action>
Add a SYSTEM_REGISTRY dict mapping system_id strings to adapter factory functions:
  "thrust-reverser" -> build_reference_controller_adapter
  "landing-gear" -> build_landing_gear_controller_adapter  (import from adapters.landing_gear_adapter)
  "bleed-air" -> build_bleed_air_controller_adapter        (import from adapters.bleed_air_adapter)

Add GET /api/system-snapshot handler in DemoRequestHandler.do_GET():
  Route: parsed.path == "/api/system-snapshot"
  Parse system_id from query param (default: "thrust-reverser")
  Look up builder in SYSTEM_REGISTRY; return 400 if unknown system_id
  Call builder() to get adapter, then adapter.load_spec() to get spec dict
  Call _spec_to_nodes(spec) to build the nodes array (see below)
  Call evaluate_snapshot with a default/minimal snapshot for the system to get GenericTruthEvaluation
  Return: { system_id, title, spec, nodes, truth_evaluation }

Add _spec_to_nodes(spec: dict) -> list[dict]:
  Build nodes from spec["components"] + spec["logic_nodes"]:
  - For each ComponentSpec: _node(component.id, component.label, "inactive", "spec.components")
  - For each LogicNodeSpec: _node(node.id, node.label, "inactive", "spec.logic_nodes")
  - Set state="active" for logic nodes that appear in truth_evaluation.active_logic_node_ids
  - Sort: components first in spec order, then logic nodes in spec order

Add a default snapshot generator per system:
  thrust-reverser: all False/0/float defaults (no engagement)
  landing-gear: gear_handle_position="UP", hydraulic_pressure_psi=0, uplock_released=False, gear_position_percent=0, downlock_engaged=False
  bleed-air: valve_position="CLOSED", inlet_pressure=0, outlet_pressure=0, control_unit_ready=True

Wire it into DemoRequestHandler.do_GET() routing after the existing GET routes.
</action>
  <verify>cd /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP && python3 -c "from well_harness.demo_server import SYSTEM_REGISTRY, system_snapshot_payload; r=system_snapshot_payload('landing-gear'); print('landing-gear title:', r.get('title')); r2=system_snapshot_payload('bleed-air'); print('bleed-air title:', r2.get('title')); r3=system_snapshot_payload('thrust-reverser'); print('thrust-reverser title:', r3.get('title'))"</verify>
  <done>GET /api/system-snapshot?system_id=landing-gear returns valid payload with title, spec, nodes, truth_evaluation. Same for bleed-air and thrust-reverser (default).</done>
</task>

<task type="auto">
  <name>Task 2: Add system-switcher UI to demo.html hero + demo.css</name>
  <files>
    - src/well_harness/static/demo.html
    - src/well_harness/static/demo.css
  </files>
  <action>
In demo.html hero section (inside the first <div> after <section class="hero">), add a <select id="system-selector"> with three <option> elements:
  <option value="thrust-reverser">Thrust Reverser (反推)</option>
  <option value="landing-gear">Landing Gear (起落架)</option>
  <option value="bleed-air">Bleed Air Valve (引气)</option>
Style it with a class="system-selector" and wrap in a <label>.

In demo.css, add .system-selector styling:
  - Display as inline-block or flex with the hero text
  - Font size matching the eyebrow text
  - Margin-left: auto to push it right in the hero flex layout
  - Add a subtle border or background to distinguish from surrounding text

The switcher should be visible in the hero area, below the eyebrow text.
</action>
  <verify>grep -c 'system-selector' /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP/src/well_harness/static/demo.html && grep -c '.system-selector' /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP/src/well_harness/static/demo.css</verify>
  <done>System selector appears in the demo UI hero, shows all three system options, has basic styling.</done>
</task>

<task type="auto">
  <name>Task 3: Make chain-panel data-driven from spec in demo.js</name>
  <files>src/well_harness/static/demo.js</files>
  <action>
Add handleSystemSwitch(systemId) function:
  - Fetch /api/system-snapshot?system_id=<systemId>
  - On success: call resetUIState() then renderChainMap(response.nodes), then renderTruthEvaluation(response.truth_evaluation)
  - Update the hero title to show the system title from response.title
  - Store current system_id in a module-level variable

Add resetUIState() function:
  - Clear all .chain-node classes to remove is-active/is-blocked states
  - Reset HUD values to "-"
  - Clear result-grid content
  - Reset lever input values to defaults

Add renderChainMap(nodes: list[dict]) function:
  - Find the .chain-map element
  - Clear existing children (remove hardcoded HTML chain nodes)
  - For each node in the nodes array:
    - Create a div.chain-node with class based on node.state (is-active / is-blocked / is-inactive)
    - Set data-node=node.id and textContent=node.label
    - Append to .chain-map
  - Add chain-arrow "➜" elements between nodes

Add renderTruthEvaluation(evaluation: dict) function:
  - Read evaluation.summary and blocked_reasons
  - Find or create a truth-eval section in the UI (add to the result-grid or as a new card)
  - Display: system_id badge, summary text, blocked_reasons as a list
  - For thrust-reverser: keep existing QA drawer behavior unchanged
  - For landing-gear and bleed-air: show this truth evaluation card as the answer (no full answer_demo_prompt)

Add condition-panel handling:
  - When system is NOT "thrust-reverser": hide or disable the condition-panel section (#condition-panel)
  - Show a simple read-only summary card for non-thrust-reverser systems instead

Wire handleSystemSwitch to the system-selector onchange event.
On page load (DOMContentLoaded), call handleSystemSwitch('thrust-reverser') to bootstrap with the default system.
</action>
  <verify>grep -c 'handleSystemSwitch' /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP/src/well_harness/static/demo.js && grep -c 'renderChainMap' /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP/src/well_harness/static/demo.js</verify>
  <done>Switching system clears chain-panel, renders new nodes from spec, shows truth evaluation as answer. Non-thrust-reverser condition panel is hidden.</done>
</task>

<task type="auto">
  <name>Task 4: Regression — verify 23 shared validation commands still pass</name>
  <files>tools/run_gsd_validation_suite.py</files>
  <action>
Run the full shared validation suite:
  cd /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP && python3 tools/run_gsd_validation_suite.py

If any command fails, diagnose and fix. The most likely regressions:
  - demo_server.py imports: ensure new imports (landing_gear_adapter, bleed_air_adapter) do not break existing paths
  - SYSTEM_REGISTRY lookup: ensure "thrust-reverser" key matches what demo.js sends
  - _spec_to_nodes: ensure it handles all three spec shapes (different component counts)

Also verify the demo server still starts:
  python3 -c "from well_harness.demo_server import main; print('import ok')"
</action>
  <verify>cd /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP && python3 tools/run_gsd_validation_suite.py 2>&1 | tail -10</verify>
  <done>All 23 shared validation commands pass. Demo server imports and starts without error.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| browser -> demo_server | Untrusted: system_id query param, fetch requests from browser |
| demo_server -> adapters | Trusted: internal Python function calls, SYSTEM_REGISTRY dict |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-P13-01 | S+Repudiation | /api/system-snapshot | mitigate | Validate system_id against SYSTEM_REGISTRY keys before lookup; return 400 for unknown system_id |
| T-P13-02 | Information Disclosure | /api/system-snapshot | accept | Spec data is already in the repo; no sensitive data exposed |
| T-P13-03 | Denial of Service | system switch | accept | Switching systems only rebuilds in-memory state; no resource exhaustion vectors introduced |
</threat_model>

<verification>
1. Start demo server: python3 -m well_harness.demo_server --open
2. Open http://127.0.0.1:8000/demo.html
3. Verify system switcher appears in hero with 3 options
4. Select "Landing Gear" — chain-panel should show 2 nodes (LG-L1, LG-L2), truth evaluation card appears
5. Select "Bleed Air Valve" — chain-panel should show 2 nodes (LN-Open, LN-Close), truth evaluation card appears
6. Select "Thrust Reverser" — chain-panel restores 14-node chain, full lever/condition panel returns
7. Verify condition panel is hidden for non-thrust-reverser systems
8. Run python3 tools/run_gsd_validation_suite.py — all 23 commands pass
</verification>

<success_criteria>
- System switcher exists in hero with all 3 options
- Switching to landing-gear shows LG-L1/LG-L2 nodes and truth evaluation answer
- Switching to bleed-air shows LN-Open/LN-Close nodes and truth evaluation answer
- Switching to thrust-reverser restores full 14-node chain and lever/condition panel
- Condition panel hidden for non-thrust-reverser systems
- All 23 shared validation commands pass
</success_criteria>

<output>
After completion, create `.planning/phases/P13-route-b-browser-workbench-multi-system-integration/P13-01-SUMMARY.md`
</output>
