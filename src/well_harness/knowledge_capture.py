from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from well_harness.controller_adapter import GenericControllerTruthAdapter
from well_harness.document_intake import ControlSystemIntakePacket
from well_harness.fault_diagnosis import (
    FaultDiagnosisReport,
    build_fault_diagnosis_report_from_truth_adapter,
    build_fault_diagnosis_report_from_intake_packet,
    fault_diagnosis_report_to_dict,
)

KNOWLEDGE_ARTIFACT_KIND = "well-harness-knowledge-artifact"
KNOWLEDGE_ARTIFACT_VERSION = 1
KNOWLEDGE_ARTIFACT_SCHEMA_ID = "https://well-harness.local/json_schema/knowledge_artifact_v1.schema.json"


@dataclass(frozen=True)
class KnowledgeArtifact:
    system_id: str
    system_title: str
    scenario_id: str
    scenario_label: str
    fault_mode_id: str
    status: str
    generated_at_utc: str
    diagnosis_summary: str
    incident_record: dict[str, Any]
    resolution_record: dict[str, Any]
    optimization_record: dict[str, Any]
    diagnosis_report: FaultDiagnosisReport

    def to_dict(self) -> dict[str, Any]:
        return knowledge_artifact_to_dict(self)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def knowledge_artifact_to_dict(artifact: KnowledgeArtifact) -> dict[str, Any]:
    payload = {
        "system_id": artifact.system_id,
        "system_title": artifact.system_title,
        "scenario_id": artifact.scenario_id,
        "scenario_label": artifact.scenario_label,
        "fault_mode_id": artifact.fault_mode_id,
        "status": artifact.status,
        "generated_at_utc": artifact.generated_at_utc,
        "diagnosis_summary": artifact.diagnosis_summary,
        "incident_record": _json_safe_value(artifact.incident_record),
        "resolution_record": _json_safe_value(artifact.resolution_record),
        "optimization_record": _json_safe_value(artifact.optimization_record),
        "diagnosis_report": fault_diagnosis_report_to_dict(artifact.diagnosis_report),
    }
    return {
        "$schema": KNOWLEDGE_ARTIFACT_SCHEMA_ID,
        "kind": KNOWLEDGE_ARTIFACT_KIND,
        "version": KNOWLEDGE_ARTIFACT_VERSION,
        **payload,
    }


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _artifact_status(
    *,
    confirmed_root_cause: str | None,
    repair_action: str | None,
    validation_after_fix: str | None,
    residual_risk: str | None,
) -> str:
    if all(
        value and value.strip()
        for value in (
            confirmed_root_cause,
            repair_action,
            validation_after_fix,
            residual_risk,
        )
    ):
        return "resolved"
    return "diagnosed"


def _default_reliability_hypothesis(report: FaultDiagnosisReport) -> str:
    blocked = ", ".join(report.blocked_logic_node_ids) or "the downstream command path"
    return (
        f"If {report.target_component_id} is monitored with a clearer plausibility guard, "
        f"{blocked} should fail faster and with less ambiguity."
    )


def _default_guardrail_note(report: FaultDiagnosisReport) -> str:
    blocked = ", ".join(report.blocked_logic_node_ids) or "downstream actuation"
    return (
        f"Add an explicit guardrail or redundant observation around {report.target_component_id} "
        f"so {blocked} does not depend on a single silent failure mode."
    )


def build_knowledge_artifact(
    packet: ControlSystemIntakePacket,
    *,
    scenario_id: str,
    fault_mode_id: str,
    observed_symptoms: str | None = None,
    evidence_links: tuple[str, ...] = (),
    confirmed_root_cause: str | None = None,
    repair_action: str | None = None,
    validation_after_fix: str | None = None,
    residual_risk: str | None = None,
    suggested_logic_change: str | None = None,
    reliability_gain_hypothesis: str | None = None,
    redundancy_reduction_or_guardrail_note: str | None = None,
    sample_period_s: float = 0.5,
) -> KnowledgeArtifact:
    diagnosis = build_fault_diagnosis_report_from_intake_packet(
        packet,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        sample_period_s=sample_period_s,
    )
    status = _artifact_status(
        confirmed_root_cause=confirmed_root_cause,
        repair_action=repair_action,
        validation_after_fix=validation_after_fix,
        residual_risk=residual_risk,
    )
    incident_record = {
        "system_id": packet.system_id,
        "scenario_id": scenario_id,
        "fault_mode_id": fault_mode_id,
        "observed_symptoms": observed_symptoms or diagnosis.symptom,
        "evidence_links": list(evidence_links),
    }
    resolution_record = {
        "confirmed_root_cause": confirmed_root_cause or "",
        "repair_action": repair_action or "",
        "validation_after_fix": validation_after_fix or "",
        "residual_risk": residual_risk or "",
    }
    optimization_record = {
        "suggested_logic_change": suggested_logic_change or diagnosis.optimization_suggestion,
        "reliability_gain_hypothesis": reliability_gain_hypothesis or _default_reliability_hypothesis(diagnosis),
        "redundancy_reduction_or_guardrail_note": (
            redundancy_reduction_or_guardrail_note or _default_guardrail_note(diagnosis)
        ),
    }
    return KnowledgeArtifact(
        system_id=packet.system_id,
        system_title=packet.title,
        scenario_id=scenario_id,
        scenario_label=diagnosis.scenario_label,
        fault_mode_id=fault_mode_id,
        status=status,
        generated_at_utc=_now_utc_iso(),
        diagnosis_summary=diagnosis.suspected_root_cause,
        incident_record=incident_record,
        resolution_record=resolution_record,
        optimization_record=optimization_record,
        diagnosis_report=diagnosis,
    )


def build_knowledge_artifact_from_truth_adapter(
    adapter: GenericControllerTruthAdapter,
    *,
    scenario_id: str,
    fault_mode_id: str,
    observed_symptoms: str | None = None,
    evidence_links: tuple[str, ...] = (),
    confirmed_root_cause: str | None = None,
    repair_action: str | None = None,
    validation_after_fix: str | None = None,
    residual_risk: str | None = None,
    suggested_logic_change: str | None = None,
    reliability_gain_hypothesis: str | None = None,
    redundancy_reduction_or_guardrail_note: str | None = None,
    sample_period_s: float = 0.5,
) -> KnowledgeArtifact:
    diagnosis = build_fault_diagnosis_report_from_truth_adapter(
        adapter,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        sample_period_s=sample_period_s,
    )
    status = _artifact_status(
        confirmed_root_cause=confirmed_root_cause,
        repair_action=repair_action,
        validation_after_fix=validation_after_fix,
        residual_risk=residual_risk,
    )
    incident_record = {
        "system_id": diagnosis.system_id,
        "scenario_id": scenario_id,
        "fault_mode_id": fault_mode_id,
        "observed_symptoms": observed_symptoms or diagnosis.symptom,
        "evidence_links": list(evidence_links),
    }
    resolution_record = {
        "confirmed_root_cause": confirmed_root_cause or "",
        "repair_action": repair_action or "",
        "validation_after_fix": validation_after_fix or "",
        "residual_risk": residual_risk or "",
    }
    optimization_record = {
        "suggested_logic_change": suggested_logic_change or diagnosis.optimization_suggestion,
        "reliability_gain_hypothesis": reliability_gain_hypothesis or _default_reliability_hypothesis(diagnosis),
        "redundancy_reduction_or_guardrail_note": (
            redundancy_reduction_or_guardrail_note or _default_guardrail_note(diagnosis)
        ),
    }
    return KnowledgeArtifact(
        system_id=diagnosis.system_id,
        system_title=diagnosis.system_title,
        scenario_id=scenario_id,
        scenario_label=diagnosis.scenario_label,
        fault_mode_id=fault_mode_id,
        status=status,
        generated_at_utc=_now_utc_iso(),
        diagnosis_summary=diagnosis.suspected_root_cause,
        incident_record=incident_record,
        resolution_record=resolution_record,
        optimization_record=optimization_record,
        diagnosis_report=diagnosis,
    )


def render_knowledge_artifact_text(artifact: KnowledgeArtifact) -> str:
    lines = [
        f"system: {artifact.system_id} - {artifact.system_title}",
        f"scenario: {artifact.scenario_id} - {artifact.scenario_label}",
        f"fault_mode: {artifact.fault_mode_id}",
        f"status: {artifact.status}",
        f"generated_at_utc: {artifact.generated_at_utc}",
        f"diagnosis_summary: {artifact.diagnosis_summary}",
        "incident_record:",
    ]
    lines.extend(f"  - {key}: {value}" for key, value in artifact.incident_record.items())
    lines.append("resolution_record:")
    lines.extend(f"  - {key}: {value}" for key, value in artifact.resolution_record.items())
    lines.append("optimization_record:")
    lines.extend(f"  - {key}: {value}" for key, value in artifact.optimization_record.items())
    return "\n".join(lines)
