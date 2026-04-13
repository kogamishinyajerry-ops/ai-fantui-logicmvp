"""
NewSystem Skeleton — Adapter + Intake Packet in one file.

Use this as a minimal starting point if you want a single-file implementation.
For a full multi-file project, copy new_system_adapter.py and
new_system_intake_packet.py separately.

This file combines:
  - NewSystemControllerAdapter  (from new_system_adapter.py)
  - build_new_system_intake_packet()  (from new_system_intake_packet.py)

Quick start:
  1. Copy this file to src/well_harness/adapters/your_system_skeleton.py
  2. Search for "TODO" and fill in your system's specifics
  3. Run: python3 tools/onboard_new_system_dry_run.py --spec-file src/well_harness/adapters/your_system_skeleton.py
"""
from __future__ import annotations

from typing import Any, Mapping

from well_harness.controller_adapter import (
    ControllerTruthMetadata,
    GenericTruthEvaluation,
)

# ---------------------------------------------------------------------------
# Section 1: Metadata — edit these for your system
# ---------------------------------------------------------------------------
SKELETON_ADAPTER_ID = "YOUR-SYSTEM-SKELETON-ADAPTER-ID"
SKELETON_SYSTEM_ID = "YOUR_SYSTEM_ID"
SKELETON_SOURCE_OF_TRUTH = "src/well_harness/adapters/your_system_skeleton.py"
SKELETON_DESCRIPTION = "Your system description."

SKELETON_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id=SKELETON_ADAPTER_ID,
    system_id=SKELETON_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=SKELETON_SOURCE_OF_TRUTH,
    description=SKELETON_DESCRIPTION,
)


# ---------------------------------------------------------------------------
# Section 2: Snapshot helpers — copy from adapter if you need custom types
# ---------------------------------------------------------------------------
def _snapshot_float(snapshot: Mapping[str, Any], key: str) -> float:
    value = snapshot.get(key)
    if isinstance(value, bool):
        raise TypeError(f"snapshot value {key!r} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"snapshot value {key!r} must be numeric")


def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
    value = snapshot.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise TypeError(f"snapshot value {key!r} must be bool-compatible")


# ---------------------------------------------------------------------------
# Section 3: Workbench spec builder — mirrors your JSON spec
# ---------------------------------------------------------------------------
def build_your_system_workbench_spec() -> dict[str, Any]:
    """
    TODO: Replace with your actual spec builder.
    See templates/new_system/new_system_adapter.py for the full template.
    """
    from well_harness.system_spec import (
        AcceptanceScenarioSpec,
        ComponentSpec,
        ControlSystemWorkbenchSpec,
        FaultModeSpec,
        KnowledgeCaptureSpec,
        LogicConditionSpec,
        LogicNodeSpec,
        SteadySignalSpec,
        TimedTransitionSpec,
        default_workbench_clarification_questions,
        workbench_spec_to_dict,
    )

    # TODO: Replace with your components
    components = (
        ComponentSpec(
            id="YOUR_COMPONENT_ID",
            label="Your Label",
            kind="sensor",
            state_shape="analog",
            unit="unit",
            description="Signal description.",
            allowed_range=(0.0, 100.0),
            allowed_states=(),
            monitor_priority="required",
        ),
    )

    # TODO: Replace with your logic nodes
    logic_nodes = (
        LogicNodeSpec(
            id="YOUR_LOGIC_NODE",
            label="LN1",
            description="Gate description.",
            conditions=(
                LogicConditionSpec(
                    name="YOUR_COMPONENT_ID",
                    source_component_id="YOUR_COMPONENT_ID",
                    comparison=">=",
                    threshold_value=1.0,
                    note="Condition note.",
                ),
            ),
            downstream_component_ids=(),
            evidence_priority="high",
        ),
    )

    # TODO: Replace with your acceptance scenarios
    acceptance_scenarios = (
        AcceptanceScenarioSpec(
            id="YOUR_SCENARIO",
            label="Your Scenario",
            description="Scenario description.",
            time_scale_factor=1.0,
            total_duration_s=5.0,
            monitored_signal_ids=("YOUR_COMPONENT_ID",),
            transitions=(
                TimedTransitionSpec(
                    signal_id="YOUR_COMPONENT_ID",
                    start_s=0.0,
                    end_s=5.0,
                    start_value=0.0,
                    end_value=100.0,
                    unit="unit",
                    note="Trajectory note.",
                ),
            ),
            completion_condition="YOUR_COMPONENT_ID >= 100.0",
            steady_signals=(
                SteadySignalSpec(
                    signal_id="YOUR_COMPONENT_ID",
                    value=0.0,
                    unit="unit",
                    note="Baseline note.",
                ),
            ),
        ),
    )

    # TODO: Replace with your fault modes
    fault_modes = (
        FaultModeSpec(
            id="YOUR_FAULT_MODE",
            target_component_id="YOUR_COMPONENT_ID",
            fault_kind="stuck_low",
            symptom="Symptom description.",
            reasoning_scope_component_ids=("YOUR_COMPONENT_ID",),
            expected_diagnostic_sections=("symptoms", "repair_hint"),
            optimization_prompt="Guardrail suggestion.",
        ),
    )

    spec = ControlSystemWorkbenchSpec(
        system_id=SKELETON_SYSTEM_ID,
        title="Your System Title",
        objective="Your system objective.",
        source_of_truth=SKELETON_SOURCE_OF_TRUTH,
        components=components,
        logic_nodes=logic_nodes,
        acceptance_scenarios=acceptance_scenarios,
        fault_modes=fault_modes,
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=("system_id", "scenario_id", "fault_mode_id", "observed_symptoms", "evidence_links"),
            resolution_fields=("confirmed_root_cause", "repair_action", "validation_after_fix", "residual_risk"),
            optimization_fields=("suggested_logic_change", "reliability_gain_hypothesis", "redundancy_reduction_or_guardrail_note"),
        ),
        tags=("your-system-tag",),
    )
    return workbench_spec_to_dict(spec)


# ---------------------------------------------------------------------------
# Section 4: Controller adapter class
# ---------------------------------------------------------------------------
class YourSystemControllerAdapter:
    """
    TODO: Implement evaluate_snapshot() with your actual control logic.
    See LandingGearControllerAdapter in landing_gear_adapter.py for reference.
    """

    metadata = SKELETON_CONTROLLER_METADATA

    def load_spec(self) -> dict[str, Any]:
        return build_your_system_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        # TODO: Replace with your actual evaluation logic
        return GenericTruthEvaluation(
            system_id=SKELETON_SYSTEM_ID,
            active_logic_node_ids=(),
            asserted_component_values={},
            completion_reached=False,
            blocked_reasons=("TODO: implement evaluate_snapshot()",),
            summary="TODO: implement with actual system logic",
        )


def build_your_system_controller_adapter() -> YourSystemControllerAdapter:
    return YourSystemControllerAdapter()


# ---------------------------------------------------------------------------
# Section 5: Intake packet builder
# ---------------------------------------------------------------------------
def build_your_system_intake_packet():
    """
    TODO: Replace with your actual intake packet builder.
    See templates/new_system/new_system_intake_packet.py for reference.
    """
    from well_harness.document_intake import (
        ControlSystemIntakePacket,
        SourceDocumentRef,
        intake_packet_from_dict,
    )

    spec_dict = build_your_system_workbench_spec()
    spec = intake_packet_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="YOUR-DOC-001",
            kind="pdf",
            title="Your System Logic Specification",
            location="docs/your-system-logic-spec.pdf",
            role="truth_source",
            notes="Primary engineering source.",
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
