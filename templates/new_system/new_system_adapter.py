"""
NewSystem Controller Adapter

Follow this pattern to wire your physical system into the well_harness pipeline.
Replace all `# TODO: implement` comments with your system's actual logic.

To use this adapter:
  1. Copy this file to src/well_harness/adapters/your_system_adapter.py
  2. Fill in the TODO sections below
  3. Import and use build_your_system_controller_adapter() in your intake packet builder
  4. Run tools/onboard_new_system_dry_run.py --spec-file src/well_harness/adapters/your_system_adapter.py
"""
from __future__ import annotations

from typing import Any, Mapping

from well_harness.controller_adapter import (
    ControllerTruthMetadata,
    GenericTruthEvaluation,
    GenericControllerTruthAdapter,
)

# ---------------------------------------------------------------------------
# Adapter metadata — edit these constants for your system
# ---------------------------------------------------------------------------
NEW_SYSTEM_ADAPTER_ID = "YOUR-SYSTEM-ADAPTER-ID"
NEW_SYSTEM_SYSTEM_ID = "YOUR_SYSTEM_ID"
NEW_SYSTEM_SOURCE_OF_TRUTH = "src/well_harness/adapters/your_system_adapter.py"
NEW_SYSTEM_DESCRIPTION = "Your system description — what it controls and why."

# TODO: Define any system-specific threshold constants here, e.g.:
# THRESHOLD_PRESSURE_PSI = 2200.0
# COMPLETION_POSITION_PERCENT = 99.0

# ---------------------------------------------------------------------------
# Metadata object — used by the harness for identification and auditing
# ---------------------------------------------------------------------------
NEW_SYSTEM_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id=NEW_SYSTEM_ADAPTER_ID,
    system_id=NEW_SYSTEM_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=NEW_SYSTEM_SOURCE_OF_TRUTH,
    description=NEW_SYSTEM_DESCRIPTION,
)


# ---------------------------------------------------------------------------
# Helper: snapshot value extractors
# ---------------------------------------------------------------------------
def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
    """Return the value for key from snapshot, or raise KeyError."""
    if key not in snapshot:
        raise KeyError(f"missing snapshot value: {key}")
    return snapshot[key]


def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise TypeError(f"snapshot value {key!r} must be a bool-compatible value")


def _snapshot_float(snapshot: Mapping[str, Any], key: str) -> float:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        raise TypeError(f"snapshot value {key!r} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"snapshot value {key!r} must be numeric")


def _snapshot_str(snapshot: Mapping[str, Any], key: str) -> str:
    value = _require_snapshot_value(snapshot, key)
    if not isinstance(value, str):
        raise TypeError(f"snapshot value {key!r} must be a string")
    return value


# ---------------------------------------------------------------------------
# Workbench spec builder — mirrors the structure defined in your JSON spec
# ---------------------------------------------------------------------------
def build_new_system_workbench_spec() -> dict[str, Any]:
    """
    TODO: Implement this function to return a workbench spec dict.

    Replace the stub below with the actual spec derived from your system docs.
    See landing_gear_adapter.py for a complete reference implementation.

    Returns
    -------
    dict
        A dict conforming to control_system_spec_v1.schema.json, as produced
        by well_harness.system_spec.workbench_spec_to_dict().
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

    # TODO: Replace these placeholder components with your actual system components
    components = (
        ComponentSpec(
            id="YOUR_COMPONENT_ID_1",
            label="Your Component Label",
            kind="sensor",
            state_shape="analog",
            unit="unit",
            description="Describe this signal.",
            allowed_range=(0.0, 100.0),
            allowed_states=(),
            monitor_priority="required",
        ),
    )

    # TODO: Replace with your actual logic nodes
    logic_nodes = (
        LogicNodeSpec(
            id="YOUR_LOGIC_NODE_ID",
            label="LN1",
            description="Describe what this logic gate does.",
            conditions=(
                LogicConditionSpec(
                    name="YOUR_COMPONENT_ID_1",
                    source_component_id="YOUR_COMPONENT_ID_1",
                    comparison=">=",
                    threshold_value=1.0,
                    note="Describe this condition.",
                ),
            ),
            downstream_component_ids=(),
            evidence_priority="high",
        ),
    )

    # TODO: Replace with your acceptance scenarios
    acceptance_scenarios = (
        AcceptanceScenarioSpec(
            id="YOUR_SCENARIO_ID",
            label="Your Scenario",
            description="Describe what this scenario verifies.",
            time_scale_factor=1.0,
            total_duration_s=5.0,
            monitored_signal_ids=("YOUR_COMPONENT_ID_1",),
            transitions=(
                TimedTransitionSpec(
                    signal_id="YOUR_COMPONENT_ID_1",
                    start_s=0.0,
                    end_s=5.0,
                    start_value=0.0,
                    end_value=100.0,
                    unit="unit",
                    note="Describe the expected trajectory.",
                ),
            ),
            completion_condition="YOUR_COMPONENT_ID_1 >= 100.0",
            steady_signals=(
                SteadySignalSpec(
                    signal_id="YOUR_COMPONENT_ID_1",
                    value=0.0,
                    unit="unit",
                    note="Baseline before transition.",
                ),
            ),
        ),
    )

    # TODO: Replace with your fault modes
    fault_modes = (
        FaultModeSpec(
            id="YOUR_FAULT_MODE_ID",
            target_component_id="YOUR_COMPONENT_ID_1",
            fault_kind="stuck_low",
            symptom="Describe what the operator observes.",
            reasoning_scope_component_ids=("YOUR_COMPONENT_ID_1",),
            expected_diagnostic_sections=("symptoms", "repair_hint"),
            optimization_prompt="Describe what guardrail should be added.",
        ),
    )

    spec = ControlSystemWorkbenchSpec(
        system_id=NEW_SYSTEM_SYSTEM_ID,
        title="Your System Title",
        objective="Describe what this system controls or protects.",
        source_of_truth=NEW_SYSTEM_SOURCE_OF_TRUTH,
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
        tags=("YOUR-SYSTEM-TAG",),
    )
    return workbench_spec_to_dict(spec)


# ---------------------------------------------------------------------------
# Controller adapter class
# ---------------------------------------------------------------------------
class NewSystemControllerAdapter:
    """
    TODO: Implement the controller adapter for your physical system.

    This class bridges your physical system's sensor/actuator interface to
    the well_harness pipeline. It must expose:

      metadata       — a ControllerTruthMetadata instance (class attribute)
      load_spec()    — returns the workbench spec dict
      evaluate_snapshot(snapshot) — evaluates a sensor snapshot and returns
                                     a GenericTruthEvaluation

    See GenericControllerTruthAdapter in controller_adapter.py for the protocol.
    See LandingGearControllerAdapter in landing_gear_adapter.py for a complete
    reference implementation.
    """

    metadata = NEW_SYSTEM_CONTROLLER_METADATA

    def load_spec(self) -> dict[str, Any]:
        return build_new_system_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        """
        TODO: Implement snapshot evaluation.

        This method receives a dict of signal_id -> value pairs (the current
        sensor state) and must return a GenericTruthEvaluation describing:
          - which logic nodes are active
          - the asserted values of key signals
          - whether completion has been reached
          - any blocked reasons
          - a human-readable summary

        Parameters
        ----------
        snapshot: Mapping[str, Any]
            Keys are component IDs; values are the current signal values.
            For boolean signals use True/False or 0/1.
            For analog signals use float.

        Returns
        -------
        GenericTruthEvaluation

        Example stub logic (replace with your actual control logic):

            active_logic_node_ids: list[str] = []
            asserted_component_values: dict[str, Any] = {}
            blocked_reasons: list[str] = []

            # TODO: Replace with your actual evaluation logic
            your_signal = _snapshot_float(snapshot, "YOUR_COMPONENT_ID_1")
            completion_reached = your_signal >= 100.0

            if completion_reached:
                active_logic_node_ids.append("YOUR_LOGIC_NODE_ID")

            return GenericTruthEvaluation(
                system_id=NEW_SYSTEM_SYSTEM_ID,
                active_logic_node_ids=tuple(active_logic_node_ids),
                asserted_component_values={
                    "YOUR_COMPONENT_ID_1": your_signal,
                },
                completion_reached=completion_reached,
                blocked_reasons=tuple(blocked_reasons),
                summary="New system evaluation summary.",
            )
        """
        # --- Extract your signals from the snapshot ---
        # TODO: Replace with your actual signal extraction
        #
        # Example:
        #   your_signal = _snapshot_float(snapshot, "YOUR_COMPONENT_ID_1")

        # --- Compute your control logic ---
        # TODO: Replace with your actual logic evaluation
        #
        # Example:
        #   completion_reached = your_signal >= 100.0

        # --- Build the evaluation result ---
        # TODO: Return the actual GenericTruthEvaluation
        active_logic_node_ids: list[str] = []
        asserted_component_values: dict[str, Any] = {}
        blocked_reasons: list[str] = []
        completion_reached = False

        return GenericTruthEvaluation(
            system_id=NEW_SYSTEM_SYSTEM_ID,
            active_logic_node_ids=tuple(active_logic_node_ids),
            asserted_component_values=asserted_component_values,
            completion_reached=completion_reached,
            blocked_reasons=tuple(blocked_reasons),
            summary="TODO: implement with actual system logic",
        )


def build_new_system_controller_adapter() -> NewSystemControllerAdapter:
    """Factory function — call this to get a ready-to-use adapter instance."""
    return NewSystemControllerAdapter()
