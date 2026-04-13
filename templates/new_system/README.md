# Template System — How to Use the New-System Templates

This directory contains template files for rapidly scaffolding a new control-system adapter. These are **documentation for the templates themselves** — the actual template files are managed by the T1 agent.

---

## Overview

When onboarding a new control system, you need **3 template files + 1 reference file**:

| Role | File | Purpose |
|------|------|---------|
| Template | `src/well_harness/adapters/your_system_adapter.py` | Python adapter implementing `GenericControllerTruthAdapter` |
| Template | `src/well_harness/adapters/your_system_intake_packet.py` | Builder function that produces a `ControlSystemIntakePacket` |
| Template | `templates/new_system/NEW_SYSTEM_SPEC.json` | JSON spec skeleton (for reference only — fill the Python adapter spec builder instead) |
| **Reference** | `src/well_harness/adapters/landing_gear_adapter.py` | Complete working implementation — study this to understand the full pattern |

**The 4th file is a reference, not a template.** Copy-paste from the templates; study landing_gear_adapter.py for the full working pattern.

---

## File Inventory and Descriptions

The actual files to create are in `src/well_harness/adapters/`:

### `{{system_id}}_adapter.py` Template

This template generates the Python adapter file. It contains:

**Module-level constants:**
- `{{SYSTEM_ID}}` — the unique system ID string (kebab-case, e.g. `hydraulic_brake_system`)
- `{{SYSTEM_UPPER}}_SOURCE_OF_TRUTH` — path to the adapter file itself (filled automatically)
- `{{SYSTEM_UPPER}}_THRESHOLD_*` — threshold constants derived from engineering specifications
- `{{SYSTEM_UPPER}}_CONTROLLER_METADATA` — a `ControllerTruthMetadata` dataclass

**Builder function:**
- `build_{{system_id}}_workbench_spec()` — returns a `ControlSystemWorkbenchSpec` dict conforming to `control_system_spec_v1.schema.json`

**Adapter class:**
- `{{SystemId}}ControllerAdapter` — implements `GenericControllerTruthAdapter` with:
  - `metadata` — class-level metadata instance
  - `load_spec()` — calls the builder function
  - `evaluate_snapshot(snapshot)` — pure function: `Mapping[str, Any] → GenericTruthEvaluation`
- Factory function: `build_{{system_id}}_controller_adapter()`

### `{{system_id}}_intake_packet.py` Template

This template generates the intake-packet builder file. It contains:

- `build_{{system_id}}_intake_packet()` — constructs and returns a `ControlSystemIntakePacket` from the adapter's spec
- Imports `SourceDocumentRef` from `well_harness.document_intake`
- Uses `workbench_spec_from_dict` to convert the adapter spec dict back into a typed spec

---

## Placeholder Reference

| Placeholder | Format | Example |
|-------------|--------|---------|
| `{{system_id}}` | kebab-case | `hydraulic_brake_system` |
| `{{SystemId}}` | PascalCase | `HydraulicBrakeSystem` |
| `{{SYSTEM_UPPER}}` | SCREAMING_SNAKE_CASE | `HYDRAULIC_BRAKE_SYSTEM` |
| `{{systemTitle}}` | Title Case | `Hydraulic Brake System` |
| `{{objective}}` | Natural language | `Release the brake and drive extension once the handle is selected and pressure is healthy.` |

---

## Filling In the Template — Quick Checklist

Before filling the adapter template, collect these values from your engineering docs:

**Component kinds** (from `ComponentSpec.kind` field):
- `sensor` — a measured signal (e.g., pressure, position, altitude)
- `command` — an output command to an actuator (e.g., valve_cmd, motor_cmd)
- `pilot_input` — a pilot-operated control (e.g., handle position, throttle)

**`fault_kind` values** (from `fault_taxonomy.py → SUPPORTED_FAULT_KINDS`):
- `stuck_low` — signal frozen at low end
- `stuck_high` — signal frozen at high end
- `misread_high` — sensor reads higher than actual
- `misread_low` — sensor reads lower than actual
- `intermittent` — signal drops out intermittently
- `noise` — signal has excessive random noise
- See `src/well_harness/fault_taxonomy.py` for the full enum

**Snapshot signal types** in `evaluate_snapshot()`:
- Boolean signals (True/False or 0/1) → use `_snapshot_bool()`
- Numeric signals (float/int) → use `_snapshot_float()`
- Discrete string signals ("OPEN"/"CLOSED", "IDLE"/"ACTIVE") → use `_snapshot_str()`
- The template adapter already includes all three helpers at lines 57–79

**`GenericControllerTruthAdapter` protocol** — defined in `src/well_harness/controller_adapter.py`:
```python
class GenericControllerTruthAdapter(Protocol):
    metadata: ControllerTruthMetadata
    def load_spec(self) -> dict[str, Any]: ...
    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation: ...
```

---

## Filling In the Template — Landing-Gear Example

Below is a side-by-side showing which template slots were filled for the landing-gear system.

### `{{system_id}}_adapter.py` filled for landing-gear

```python
# Module constants
LANDING_GEAR_SYSTEM_ID = "minimal_landing_gear_extension"
LANDING_GEAR_SOURCE_OF_TRUTH = "src/well_harness/adapters/landing_gear_adapter.py"
LANDING_GEAR_PRESSURE_THRESHOLD_PSI = 2200.0
LANDING_GEAR_COMPLETE_POSITION_PERCENT = 99.0

# Spec builder produces components, logic_nodes, acceptance_scenarios, fault_modes
# matching the schema in docs/json_schema/control_system_spec_v1.schema.json

# Adapter class
class LandingGearControllerAdapter:
    metadata = LANDING_GEAR_CONTROLLER_METADATA  # ControllerTruthMetadata instance

    def load_spec(self) -> dict[str, Any]:
        return build_landing_gear_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        # Reads: gear_handle_position (str), hydraulic_pressure_psi (float),
        #        uplock_released (bool), gear_position_percent (float), downlock_engaged (bool)
        # Asserts: selector_valve_cmd, extend_actuator_cmd
        # Returns: GenericTruthEvaluation with active_logic_node_ids, blocked_reasons, etc.
        ...
```

### `{{system_id}}_intake_packet.py` filled for landing-gear

```python
from well_harness.adapters.landing_gear_adapter import build_landing_gear_workbench_spec
from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_to_workbench_spec,
)
from well_harness.system_spec import workbench_spec_from_dict

def build_landing_gear_intake_packet() -> ControlSystemIntakePacket:
    spec_dict = build_landing_gear_workbench_spec()
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="lg-001",
            kind="python-adapter",
            title="Landing Gear Controller Adapter",
            location="src/well_harness/adapters/landing_gear_adapter.py",
            role="truth_source",
            notes="P10-01 intake packet derived from landing_gear_adapter.py",
        ),
    )

    return ControlSystemIntakePacket(
        system_id=spec.system_id,
        title=spec.title,
        objective=spec.objective,
        source_of_truth=spec.source_of_truth,
        source_documents=source_document_refs,
        components=spec.components,
        logic_nodes=spec.logic_nodes,
        acceptance_scenarios=spec.acceptance_scenarios,
        fault_modes=spec.fault_modes,
        knowledge_capture=spec.knowledge_capture,
        clarification_answers=(),
        tags=spec.tags,
    )
```

---

## How to Apply the Templates

1. **Identify your system ID** — choose a kebab-case string, e.g. `fuel_boost_pump`
2. **Collect engineering inputs:**
   - List all sensor, command, and pilot-input signals with their units, ranges, and states
   - Identify the logic gate conditions and downstream command dependencies
   - Define at least one nominal acceptance scenario (with timing)
   - Define at least one fault mode with symptom description
3. **Fill the adapter template:**
   - Set threshold constants from engineering specs
   - Implement `evaluate_snapshot()` — the core truth-evaluation function
   - Populate `build_{{system_id}}_workbench_spec()` with all components, logic nodes, scenarios, and fault modes
4. **Fill the intake-packet template:**
   - Call your adapter's spec builder
   - Provide at least one `SourceDocumentRef`
5. **Validate** by running your new system's validation script (see `docs/onboarding/README.md`).

---

## Important Constraints

- **Signal IDs** in `snapshot` keys passed to `evaluate_snapshot()` must match exactly the `id` fields in your `ComponentSpec` definitions (case-sensitive).
- **Threshold values** in `LogicConditionSpec.threshold_value` must be of the correct type: string for discrete/binary comparisons, numeric for analog comparisons.
- **`kind` values** for `ComponentSpec` must be one of: `sensor`, `command`, `pilot_input` (not free-form strings).
- **`fault_kind` values** for `FaultModeSpec` must be from `SUPPORTED_FAULT_KINDS` in `fault_taxonomy.py` (e.g., `stuck_low`, `misread_high`) — arbitrary strings will fail schema validation.
- **Every `LogicNodeSpec.downstream_component_ids`** entry must reference a component with `kind="command"`.
- **`acceptance_scenarios[].monitored_signal_ids`** must be a subset of all component IDs.
- **`fault_modes[].target_component_id`** must reference an existing component.
