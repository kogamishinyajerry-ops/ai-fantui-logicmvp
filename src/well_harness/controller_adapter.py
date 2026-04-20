from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Protocol

from well_harness.controller import DeployController
from well_harness.models import ControllerExplain, ControllerOutputs, HarnessConfig, ResolvedInputs


CONTROLLER_TRUTH_ADAPTER_METADATA_KIND = "well-harness-controller-truth-adapter-metadata"
CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION = 1
CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID = (
    "https://well-harness.local/json_schema/controller_truth_adapter_metadata_v1.schema.json"
)


@dataclass(frozen=True)
class ControllerTruthMetadata:
    adapter_id: str
    system_id: str
    truth_kind: str
    source_of_truth: str
    description: str
    # P42 (2026-04-20) governance fields · None sentinel = pre-P42/unclassified.
    # Production adapters MUST set both explicitly (enforced by
    # tests/test_metadata_registry_consistency.py). Dataclass defaults exist
    # only for forward-compat loader paths and test fixtures.
    truth_level: str | None = None
    status: str | None = None

    def to_dict(self) -> dict:
        return controller_truth_metadata_to_dict(self)


_GOVERNANCE_FIELDS = ("truth_level", "status")


def controller_truth_metadata_to_dict(metadata: ControllerTruthMetadata) -> dict:
    payload = {
        "$schema": CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
        "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
        "version": CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
        **asdict(metadata),
    }
    # P42: drop None-valued governance fields so v1 payload shape is byte-
    # identical to pre-P42 when governance unset. 字段缺失 = pre-P42/unclassified;
    # downstream consumers MUST NOT treat missing field as "already governed".
    for field in _GOVERNANCE_FIELDS:
        if payload.get(field) is None:
            payload.pop(field, None)
    return payload


@dataclass(frozen=True)
class GenericTruthEvaluation:
    system_id: str
    active_logic_node_ids: tuple[str, ...]
    asserted_component_values: dict[str, Any]
    completion_reached: bool
    blocked_reasons: tuple[str, ...]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return generic_truth_evaluation_to_dict(self)


def generic_truth_evaluation_to_dict(evaluation: GenericTruthEvaluation) -> dict[str, Any]:
    return {
        "system_id": evaluation.system_id,
        "active_logic_node_ids": list(evaluation.active_logic_node_ids),
        "asserted_component_values": dict(evaluation.asserted_component_values),
        "completion_reached": evaluation.completion_reached,
        "blocked_reasons": list(evaluation.blocked_reasons),
        "summary": evaluation.summary,
    }


class ControllerTruthAdapter(Protocol):
    metadata: ControllerTruthMetadata

    def explain(self, inputs: ResolvedInputs) -> ControllerExplain:
        ...

    def evaluate(self, inputs: ResolvedInputs) -> ControllerOutputs:
        ...

    def evaluate_with_explain(self, inputs: ResolvedInputs) -> tuple[ControllerOutputs, ControllerExplain]:
        ...


class GenericControllerTruthAdapter(Protocol):
    metadata: ControllerTruthMetadata

    def load_spec(self) -> dict[str, Any]:
        ...

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        ...


REFERENCE_DEPLOY_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="reference-deploy-controller",
    system_id="reference_thrust_reverser_deploy",
    truth_kind="python-controller-adapter",
    source_of_truth="src/well_harness/controller.py",
    description="Wraps DeployController as the current reference system truth adapter.",
    truth_level="certified",  # P42: aligned with docs/provenance/adapter_truth_levels.yaml row "thrust-reverser"
    status="In use",
)


class ReferenceDeployControllerAdapter:
    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()
        self.metadata = REFERENCE_DEPLOY_CONTROLLER_METADATA
        self._controller = DeployController(self.config)

    def explain(self, inputs: ResolvedInputs) -> ControllerExplain:
        return self._controller.explain(inputs)

    def evaluate(self, inputs: ResolvedInputs) -> ControllerOutputs:
        return self._controller.evaluate(inputs)

    def evaluate_with_explain(self, inputs: ResolvedInputs) -> tuple[ControllerOutputs, ControllerExplain]:
        return self._controller.evaluate_with_explain(inputs)

    def load_spec(self) -> dict[str, Any]:
        from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict

        return workbench_spec_to_dict(current_reference_workbench_spec(self.config))

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        inputs = resolved_inputs_from_snapshot(snapshot)
        outputs, explain = self.evaluate_with_explain(inputs)
        logic_rows = (explain.logic1, explain.logic2, explain.logic3, explain.logic4)
        active_logic_node_ids = tuple(logic.logic_name for logic in logic_rows if logic.active)
        blocked_reasons = tuple(
            f"{logic.logic_name}:{condition.name}"
            for logic in logic_rows
            if not logic.active
            for condition in logic.failed_conditions
        )
        return GenericTruthEvaluation(
            system_id=self.metadata.system_id,
            active_logic_node_ids=active_logic_node_ids,
            asserted_component_values={
                # Input conditions (raw signals from snapshot)
                "sw1": inputs.sw1,
                "sw2": inputs.sw2,
                "radio_altitude_ft": inputs.radio_altitude_ft,
                "engine_running": inputs.engine_running,
                "aircraft_on_ground": inputs.aircraft_on_ground,
                "eec_enable": inputs.eec_enable,
                "n1k": inputs.n1k,
                "tra_deg": inputs.tra_deg,
                "reverser_inhibited": inputs.reverser_inhibited,
                # Plant feedback (drives VDT90 / L4 condition)
                "deploy_90_percent_vdt": inputs.deploy_90_percent_vdt,
                # Output commands
                "tls_115vac_cmd": outputs.tls_115vac_cmd,
                "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
                "eec_deploy_cmd": outputs.eec_deploy_cmd,
                "pls_power_cmd": outputs.pls_power_cmd,
                "pdu_motor_cmd": outputs.pdu_motor_cmd,
                "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
            },
            completion_reached=outputs.throttle_electronic_lock_release_cmd,
            blocked_reasons=blocked_reasons,
            summary=(
                f"Reference deploy truth evaluated with {len(active_logic_node_ids)} active logic nodes; "
                f"completion={'yes' if outputs.throttle_electronic_lock_release_cmd else 'no'}."
            ),
        )


def build_reference_controller_adapter(config: HarnessConfig | None = None) -> ReferenceDeployControllerAdapter:
    return ReferenceDeployControllerAdapter(config)


def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
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


def resolved_inputs_from_snapshot(snapshot: Mapping[str, Any]) -> ResolvedInputs:
    return ResolvedInputs(
        radio_altitude_ft=_snapshot_float(snapshot, "radio_altitude_ft"),
        tra_deg=_snapshot_float(snapshot, "tra_deg"),
        sw1=_snapshot_bool(snapshot, "sw1"),
        sw2=_snapshot_bool(snapshot, "sw2"),
        engine_running=_snapshot_bool(snapshot, "engine_running"),
        aircraft_on_ground=_snapshot_bool(snapshot, "aircraft_on_ground"),
        reverser_inhibited=_snapshot_bool(snapshot, "reverser_inhibited"),
        eec_enable=_snapshot_bool(snapshot, "eec_enable"),
        n1k=_snapshot_float(snapshot, "n1k"),
        max_n1k_deploy_limit=_snapshot_float(snapshot, "max_n1k_deploy_limit"),
        tls_unlocked_ls=_snapshot_bool(snapshot, "tls_unlocked_ls"),
        all_pls_unlocked_ls=_snapshot_bool(snapshot, "all_pls_unlocked_ls"),
        reverser_not_deployed_eec=_snapshot_bool(snapshot, "reverser_not_deployed_eec"),
        reverser_fully_deployed_eec=_snapshot_bool(snapshot, "reverser_fully_deployed_eec"),
        deploy_90_percent_vdt=_snapshot_bool(snapshot, "deploy_90_percent_vdt"),
    )
