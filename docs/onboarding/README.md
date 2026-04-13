# AI FANTUI LogicMVP — Onboarding Guide

This guide helps external engineers onboard a new control system to the well-harness pipeline without insider knowledge.

---

## What This Project Does

The well-harness pipeline takes a **control-system specification** and runs it through a four-stage runtime pipeline that produces structured, machine-readable artifacts for diagnosis and knowledge capture.

It supports two entry paths into that pipeline:

| Path | Description |
|------|-------------|
| **Adapter path** | You supply a Python adapter class that encodes the ground-truth control logic directly. The adapter implements `evaluate_snapshot()` — a pure function that maps a signal snapshot to an evaluation result. |
| **Intake path** | You supply a JSON/YAML intake packet that describes the system declaratively. The pipeline parses it into a `ControlSystemWorkbenchSpec`, then runs all four stages. |

Both paths converge at Stage 1 (intake-to-spec) and share the remaining stages.

---

## The Four Pipeline Stages

```
Stage 1: Intake → Spec
  ControlSystemIntakePacket  →  ControlSystemWorkbenchSpec
  Validated against: docs/json_schema/control_system_spec_v1.schema.json

Stage 2: Intake → Playback
  ControlSystemIntakePacket  →  ScenarioPlaybackReport
  Validated against: docs/json_schema/playback_trace_v1.schema.json

Stage 3: Intake → Diagnosis
  ControlSystemIntakePacket  →  FaultDiagnosisReport
  Validated against: docs/json_schema/fault_diagnosis_v1.schema.json

Stage 4: Intake → Knowledge
  ControlSystemIntakePacket  →  KnowledgeArtifact
  Validated against: docs/json_schema/knowledge_artifact_v1.schema.json
```

Stage 2 replays an acceptance scenario timeline step-by-step and verifies completion.
Stage 3 injects a fault mode and produces a structured diagnosis.
Stage 4 synthesizes a reusable knowledge artifact from the diagnosis.

---

## Prerequisites

- **Python 3.9+**
- **No external dependencies required** for the core pipeline. The following are optional:
  - `jsonschema` — required only if you want schema validation in the validation suite
  - Other runtime dependencies are listed in `requirements.txt` or `pyproject.toml`

To install the package in development mode (required before running any scripts):

```bash
pip install -e .
```

---

## Onboarding a New System — Step by Step

### Step 1 — Create a Spec File

Define your system in a JSON file that conforms to the v1 schema.

**Schema location:** `docs/json_schema/control_system_spec_v1.schema.json`

**Minimal required fields:**

```json
{
  "$schema": "https://well-harness.local/json_schema/control_system_spec_v1.schema.json",
  "kind": "well-harness-control-system-spec",
  "version": 1,
  "system_id": "your_system_id",
  "title": "Your System Title",
  "objective": "What the system must control or protect.",
  "source_of_truth": "engineer-supplied mixed docs/PDF packet",
  "components": [],
  "logic_nodes": [],
  "acceptance_scenarios": [],
  "fault_modes": [],
  "onboarding_questions": [],
  "knowledge_capture": {
    "incident_fields": [],
    "resolution_fields": [],
    "optimization_fields": []
  },
  "tags": []
}
```

Each `ComponentSpec` must declare:
- `id` — unique signal identifier
- `kind` — one of: `sensor`, `command`, `pilot_input`
- `state_shape` — one of: `analog`, `binary`, `discrete`
- `allowed_range` — required for `analog` signals (`[min, max]`)
- `allowed_states` — required for `binary` / `discrete` signals

**Reference:** See `src/well_harness/adapters/landing_gear_adapter.py` for a complete worked example (function `build_landing_gear_workbench_spec()`).

---

### Step 2 — Create an Adapter

The adapter is a Python class that implements `GenericControllerTruthAdapter`. It is the **adapter path** entry point. Even if you use the intake path, an adapter is needed to evaluate signal snapshots during playback and diagnosis.

**Interface:**

```python
class GenericControllerTruthAdapter(Protocol):
    metadata: ControllerTruthMetadata

    def load_spec(self) -> dict[str, Any]:
        """Return the system spec as a dict conforming to control_system_spec_v1.schema.json."""
        ...

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        """
        Evaluate a full signal snapshot and return a truth evaluation.

        Args:
            snapshot: A dict of signal_id -> value, matching the components
                      declared in load_spec().

        Returns:
            GenericTruthEvaluation with:
              - system_id
              - active_logic_node_ids: which logic gates are currently satisfied
              - asserted_component_values: derived signal values (e.g. commands)
              - completion_reached: bool
              - blocked_reasons: tuple of human-readable blocking reasons
              - summary: one-line status string
        """
        ...
```

**Reference implementation:** `src/well_harness/adapters/landing_gear_adapter.py` — `LandingGearControllerAdapter` class.

**Key patterns from the reference:**
- Define module-level constants for threshold values (e.g., `LANDING_GEAR_PRESSURE_THRESHOLD_PSI = 2200.0`)
- Use helper functions (`_snapshot_bool`, `_snapshot_float`, `_snapshot_str`) that raise `TypeError` on type mismatches
- Build `blocked_reasons` by checking preconditions in order, so the most actionable reason appears first
- Set `active_logic_node_ids` to record which logic gates are satisfied at this snapshot

---

### Step 3 — Create an Intake Packet Builder

Create a file `src/well_harness/adapters/<your_system>_intake_packet.py` that builds a `ControlSystemIntakePacket`.

**Reference:** `src/well_harness/adapters/landing_gear_intake_packet.py`

```python
from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_to_workbench_spec,
)
from well_harness.system_spec import workbench_spec_from_dict

def build_your_system_intake_packet() -> ControlSystemIntakePacket:
    spec_dict = your_build_function()          # calls load_spec() on your adapter
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="<short-id>",
            kind="python-adapter",             # or "pdf", "markdown", "notion"
            title="Your System Adapter",
            location="src/well_harness/adapters/your_adapter.py",
            role="truth_source",
            notes="P10-01 intake packet derived from your_adapter.py",
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
        clarification_answers=(),              # or provide answers
        tags=spec.tags,
    )
```

**`ControlSystemIntakePacket` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `system_id` | `str` | Unique identifier, e.g. `minimal_landing_gear_extension` |
| `title` | `str` | Human-readable title |
| `objective` | `str` | One-sentence description of what the system does |
| `source_of_truth` | `str` | Path or description of the authoritative source |
| `source_documents` | `tuple[SourceDocumentRef, ...]` | Reference documents (PDF, Notion, etc.) |
| `components` | `tuple[ComponentSpec, ...]` | All signals (sensors, commands, pilot inputs) |
| `logic_nodes` | `tuple[LogicNodeSpec, ...]` | Logic gates and their conditions |
| `acceptance_scenarios` | `tuple[AcceptanceScenarioSpec, ...]` | Nominal operation timelines |
| `fault_modes` | `tuple[FaultModeSpec, ...]` | Known failure modes |
| `knowledge_capture` | `KnowledgeCaptureSpec` | Field names for incident/resolution/optimization records |
| `clarification_answers` | `tuple[ClarificationAnswer, ...]` | Answers to standard onboarding questions |
| `tags` | `tuple[str, ...]` | Arbitrary tags for filtering |

---

### Step 4 — Run the Dry-Run Validation

```bash
python tools/validate_landing_gear_full_pipeline.py
```

To validate a new system, create a similar script:

```python
# tools/validate_your_system_full_pipeline.py
from well_harness.adapters.your_system_intake_packet import build_your_system_intake_packet
from well_harness.document_intake import intake_packet_to_workbench_spec
from well_harness.scenario_playback import build_playback_report_from_intake_packet
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
from well_harness.knowledge_capture import build_knowledge_artifact
from well_harness.system_spec import workbench_spec_to_dict

# Stage 1
packet = build_your_system_intake_packet()
spec = intake_packet_to_workbench_spec(packet)
spec_dict = workbench_spec_to_dict(spec)

# Stage 2
playback = build_playback_report_from_intake_packet(packet, scenario_id="<your_scenario_id>", sample_period_s=0.5)

# Stage 3
diagnosis = build_fault_diagnosis_report_from_intake_packet(
    packet, scenario_id="<your_scenario_id>", fault_mode_id="<your_fault_id>", sample_period_s=0.5
)

# Stage 4
knowledge = build_knowledge_artifact(
    packet, scenario_id="<your_scenario_id>", fault_mode_id="<your_fault_id>", sample_period_s=0.5
)

print("All 4 stages completed successfully.")
```

The validation script (`validate_landing_gear_full_pipeline.py`) also performs JSON schema validation against all four output schemas. Install the optional `jsonschema` dependency to enable this:

```bash
pip install jsonschema
```

---

## How to Run the Validation Suite

The reference validation script exercises the full pipeline end-to-end for the landing-gear system:

```bash
# Text output (default)
python tools/validate_landing_gear_full_pipeline.py

# JSON output
python tools/validate_landing_gear_full_pipeline.py --format json
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | All schema validations passed |
| 1 | One or more schema failures |
| 2 | Bad arguments |

**To skip schema validation** (when `jsonschema` is not installed), the script automatically detects the missing dependency and exits gracefully with status 0 and a `skip` reason.

---

## Common Issues and Troubleshooting

### 1. `KeyError: missing snapshot value: <signal_id>`

**Cause:** Your adapter's `evaluate_snapshot()` received a snapshot that is missing a required signal.

**Fix:** Ensure all signals declared in `components` are present in every snapshot your runtime sends to the adapter. Check the signal ID spelling matches exactly (case-sensitive).

### 2. `TypeError: snapshot value '<signal_id>' must be numeric`

**Cause:** Your adapter calls `_snapshot_float()` on a signal that is a string or boolean.

**Fix:** Use `_snapshot_bool()` for binary signals and `_snapshot_str()` for discrete/string signals. See the reference adapter for examples of each type.

### 3. `blocking_reasons` is empty but `completion_reached` is False

**Cause:** Logic evaluation did not find any unmet preconditions — but some downstream condition was also not satisfied.

**Fix:** Verify that `downstream_component_ids` in your `LogicNodeSpec` actually produce the signals checked in `completion_condition`. Trace the signal flow from inputs through intermediate commands to the final completion signal.

### 4. Schema validation fails on Stage 1 output

**Cause:** The spec dict produced by `load_spec()` does not conform to `control_system_spec_v1.schema.json`.

**Fix:**
- `allowed_range` is required for `analog` components; set to `null` if not applicable (the schema allows `null`)
- `allowed_states` is required for `binary` and `discrete` components
- `onboarding_questions` must be an array; use `default_workbench_clarification_questions()` from `well_harness.system_spec` to populate it
- All required fields at the top level must be present (`$schema`, `kind`, `version`, `system_id`, etc.)

### 5. Schema validation fails on Stage 2 output (`ScenarioPlaybackReport`)

**Cause:** The `monitored_signal_ids` in an acceptance scenario include a signal ID that has no corresponding component definition.

**Fix:** Every signal in `monitored_signal_ids`, `steady_signals`, and `transitions` must match a component `id` in the spec.

### 6. Fault diagnosis produces no diagnostic sections

**Cause:** The `fault_modes` entry is missing required fields or references a non-existent component.

**Fix:** Verify each `FaultModeSpec` has:
- `target_component_id` pointing to an existing component
- `reasoning_scope_component_ids` covering all signals checked in the fault scenario
- `expected_diagnostic_sections` (must be non-empty)

### 7. Pipeline silently produces empty output

**Cause:** `clarification_answers` is empty and the system has unanswered required questions, blocking spec build.

**Fix:** Provide non-empty `clarification_answers` for all required onboarding questions, or use the `assess_intake_packet()` function from `well_harness.document_intake` to identify which questions are unanswered.

---

## Project Structure

```
src/well_harness/
  adapters/
    landing_gear_adapter.py       # Reference truth adapter
    landing_gear_intake_packet.py # Reference intake packet builder
  controller_adapter.py           # GenericTruthAdapter protocol definition
  document_intake.py              # ControlSystemIntakePacket dataclass + intake pipeline
  scenario_playback.py            # Stage 2: ScenarioPlaybackReport
  fault_diagnosis.py              # Stage 3: FaultDiagnosisReport
  knowledge_capture.py            # Stage 4: KnowledgeArtifact
  system_spec.py                  # ControlSystemWorkbenchSpec dataclasses
docs/
  json_schema/
    control_system_spec_v1.schema.json    # Stage 1 output schema
    playback_trace_v1.schema.json          # Stage 2 output schema
    fault_diagnosis_v1.schema.json         # Stage 3 output schema
    knowledge_artifact_v1.schema.json       # Stage 4 output schema
  onboarding/
    README.md                    # This file
templates/
  new_system/
    README.md                    # Template usage guide
tools/
  validate_landing_gear_full_pipeline.py  # Reference validation script
```
