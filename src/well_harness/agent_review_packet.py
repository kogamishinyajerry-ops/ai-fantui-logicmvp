"""Machine-readable candidate review packets for repair-loop evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CANDIDATE_REVIEW_PACKET_SCHEMA_ID = (
    "https://well-harness.local/json_schema/candidate_review_packet_v0_1.schema.json"
)
CANDIDATE_REVIEW_PACKET_SCHEMA_NAME = "candidate_review_packet_v0_1.schema.json"
CANDIDATE_REVIEW_PACKET_KIND = "ai-fantui-candidate-review-packet"
REVIEWER_AGENT_NAME = "CandidateReviewPacketAgent"
CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_ID = (
    "https://well-harness.local/json_schema/candidate_review_packet_export_v0_1.schema.json"
)
CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_NAME = "candidate_review_packet_export_v0_1.schema.json"
CANDIDATE_REVIEW_PACKET_EXPORT_KIND = "ai-fantui-candidate-review-packet-export"
CANDIDATE_REVIEW_PACKET_EXPORT_AGENT_NAME = "CandidateReviewPacketExportAgent"
CANDIDATE_REVIEW_PACKET_EXPORT_ID = "latest-candidate-review-packet"
CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE = "/logic-builder/candidate-review-packet.json"
CANDIDATE_REVIEW_PACKET_SOURCE_ROUTE = "/logic-builder"
CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_VERSION = "0.1"
REQUIRED_REVIEW_PACKET_FIELDS = {
    "$schema",
    "kind",
    "reviewer",
    "boundary",
    "source_artifacts",
    "summary",
    "finding_chains",
    "human_review_required",
}
REQUIRED_REVIEWER_FIELDS = {"agent_name", "status", "loop_count"}
REQUIRED_REVIEW_BOUNDARY_FIELDS = {
    "candidate_state",
    "truth_effect",
    "controller_truth_modified",
    "certification_claim",
}
REQUIRED_REVIEW_SUMMARY_FIELDS = {
    "total_findings",
    "loop_count",
    "converged_loops",
    "blocked_loops",
    "needs_followup_loops",
    "open_findings",
}
REQUIRED_REVIEW_PACKET_EXPORT_FIELDS = {
    "$schema",
    "kind",
    "exporter",
    "review_packet_ref",
    "boundary",
    "review_packet",
    "machine_readable",
    "human_review_required",
}
REQUIRED_REVIEW_PACKET_EXPORTER_FIELDS = {
    "agent_name",
    "schema_version",
    "export_id",
    "source_route",
    "export_route",
    "storage",
    "status",
}
REQUIRED_REVIEW_PACKET_REF_FIELDS = {"schema", "kind", "reviewer_status"}


class CandidateReviewPacketError(ValueError):
    """Raised when a candidate review packet violates schema or boundaries."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


REFERENCE_CANDIDATE_REVIEW_PACKET_EXPORT_PATH = (
    _project_root()
    / "src"
    / "well_harness"
    / "reference_packets"
    / CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_NAME.replace(".schema", "")
)


def _load_schema(schema_name: str) -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / schema_name
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(packet: dict[str, Any], *, schema_name: str, label: str) -> None:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        if exc.name not in {None, "jsonschema"}:
            raise
        _fallback_schema_validate(packet, schema_name=schema_name, label=label)
        return

    schema = _load_schema(schema_name)
    try:
        jsonschema.Draft202012Validator(schema).validate(packet)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise CandidateReviewPacketError(
            f"{label} schema validation failed{location}: {exc.message}"
        ) from exc


def _missing_fields(
    value: dict[str, Any],
    required: set[str],
    label: str,
) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise CandidateReviewPacketError(
            f"{label} missing required field(s): {', '.join(missing)}"
        )


def _validate_candidate_boundary(boundary: Any, label: str) -> None:
    if not isinstance(boundary, dict):
        raise CandidateReviewPacketError(f"{label} boundary must be an object")
    _missing_fields(boundary, REQUIRED_REVIEW_BOUNDARY_FIELDS, f"{label} boundary")
    if boundary.get("truth_effect") != "none":
        raise CandidateReviewPacketError(f"{label} truth_effect must remain none")
    if boundary.get("controller_truth_modified") is not False:
        raise CandidateReviewPacketError(f"{label} may not modify controller truth")
    if boundary.get("certification_claim") != "none":
        raise CandidateReviewPacketError(f"{label} may not claim certification")


def _fallback_review_packet_validate(packet: dict[str, Any], label: str) -> None:
    if packet.get("$schema") != CANDIDATE_REVIEW_PACKET_SCHEMA_ID:
        raise CandidateReviewPacketError(f"{label} $schema is invalid")
    if packet.get("kind") != CANDIDATE_REVIEW_PACKET_KIND:
        raise CandidateReviewPacketError(f"{label} kind is invalid")
    _missing_fields(packet, REQUIRED_REVIEW_PACKET_FIELDS, label)

    reviewer = packet.get("reviewer")
    if not isinstance(reviewer, dict):
        raise CandidateReviewPacketError(f"{label} reviewer must be an object")
    _missing_fields(reviewer, REQUIRED_REVIEWER_FIELDS, f"{label} reviewer")
    if reviewer.get("agent_name") != REVIEWER_AGENT_NAME:
        raise CandidateReviewPacketError(f"{label} reviewer.agent_name is invalid")

    _validate_candidate_boundary(packet.get("boundary"), label)

    for field_name in ("source_artifacts", "summary"):
        if not isinstance(packet.get(field_name), dict):
            raise CandidateReviewPacketError(f"{label} {field_name} must be an object")
    _missing_fields(packet["summary"], REQUIRED_REVIEW_SUMMARY_FIELDS, f"{label} summary")
    if not isinstance(packet["summary"].get("open_findings"), list):
        raise CandidateReviewPacketError(f"{label} summary.open_findings must be a list")
    if not isinstance(packet.get("finding_chains"), list):
        raise CandidateReviewPacketError(f"{label} finding_chains must be a list")
    if not isinstance(packet.get("human_review_required"), bool):
        raise CandidateReviewPacketError(f"{label} human_review_required must be a boolean")


def _fallback_review_packet_export_validate(packet: dict[str, Any], label: str) -> None:
    if packet.get("$schema") != CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_ID:
        raise CandidateReviewPacketError(f"{label} $schema is invalid")
    if packet.get("kind") != CANDIDATE_REVIEW_PACKET_EXPORT_KIND:
        raise CandidateReviewPacketError(f"{label} kind is invalid")
    _missing_fields(packet, REQUIRED_REVIEW_PACKET_EXPORT_FIELDS, label)

    exporter = packet.get("exporter")
    if not isinstance(exporter, dict):
        raise CandidateReviewPacketError(f"{label} exporter must be an object")
    _missing_fields(exporter, REQUIRED_REVIEW_PACKET_EXPORTER_FIELDS, f"{label} exporter")
    if exporter.get("agent_name") != CANDIDATE_REVIEW_PACKET_EXPORT_AGENT_NAME:
        raise CandidateReviewPacketError(f"{label} exporter.agent_name is invalid")

    ref = packet.get("review_packet_ref")
    if not isinstance(ref, dict):
        raise CandidateReviewPacketError(f"{label} review_packet_ref must be an object")
    _missing_fields(ref, REQUIRED_REVIEW_PACKET_REF_FIELDS, f"{label} review_packet_ref")
    if ref.get("schema") != CANDIDATE_REVIEW_PACKET_SCHEMA_ID:
        raise CandidateReviewPacketError(f"{label} review_packet_ref schema mismatch")
    if ref.get("kind") != CANDIDATE_REVIEW_PACKET_KIND:
        raise CandidateReviewPacketError(f"{label} review_packet_ref kind mismatch")

    _validate_candidate_boundary(packet.get("boundary"), label)
    review_packet = packet.get("review_packet")
    if not isinstance(review_packet, dict):
        raise CandidateReviewPacketError(f"{label} review_packet must be an object")
    _fallback_review_packet_validate(review_packet, "candidate review packet")
    if packet.get("machine_readable") is not True:
        raise CandidateReviewPacketError(f"{label} machine_readable must be true")
    if not isinstance(packet.get("human_review_required"), bool):
        raise CandidateReviewPacketError(f"{label} human_review_required must be a boolean")


def _fallback_schema_validate(
    packet: dict[str, Any],
    *,
    schema_name: str,
    label: str,
) -> None:
    """Runtime-safe structural checks used when optional jsonschema is absent."""
    if schema_name == CANDIDATE_REVIEW_PACKET_SCHEMA_NAME:
        _fallback_review_packet_validate(packet, label)
        return
    if schema_name == CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_NAME:
        _fallback_review_packet_export_validate(packet, label)
        return
    raise CandidateReviewPacketError(f"unsupported fallback schema: {schema_name}")


def _logic_ir_packet(agent_outputs: dict[str, Any]) -> dict[str, Any]:
    packet = agent_outputs.get("logic_ir")
    return packet if isinstance(packet, dict) else {}


def _agent_output(packet: dict[str, Any]) -> dict[str, Any]:
    agent_output = packet.get("agent_output")
    return agent_output if isinstance(agent_output, dict) else {}


def _boundary(agent_outputs: dict[str, Any]) -> dict[str, Any]:
    boundary = _agent_output(_logic_ir_packet(agent_outputs)).get("boundary")
    if isinstance(boundary, dict):
        return {
            "candidate_state": str(boundary.get("candidate_state", "")),
            "truth_effect": boundary.get("truth_effect"),
            "controller_truth_modified": boundary.get("controller_truth_modified"),
            "certification_claim": boundary.get("certification_claim"),
        }
    return {
        "candidate_state": "",
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
    }


def _source_artifacts(
    agent_outputs: dict[str, Any],
    *,
    task_package: dict[str, Any],
    execution_plan: dict[str, Any],
    execution_evidence_package: dict[str, Any],
) -> dict[str, str]:
    agent_output = _agent_output(_logic_ir_packet(agent_outputs))
    return {
        "logic_ir_agent": str(agent_output.get("agent_name", "")),
        "logic_ir_task_id": str(agent_output.get("task_id", "")),
        "task_package_status": str(task_package.get("chief_engineer", {}).get("status", "")),
        "execution_plan_status": str(execution_plan.get("planner", {}).get("status", "")),
        "execution_evidence_status": str(
            execution_evidence_package.get("executor", {}).get("status", "")
        ),
    }


def _finding_codes_from_reports(agent_outputs: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for key in ("safety_guardian", "evidence", "requirements"):
        report = agent_outputs.get(key)
        if not isinstance(report, dict):
            continue
        for finding in report.get("findings", []):
            if not isinstance(finding, dict):
                continue
            code = finding.get("code")
            if isinstance(code, str) and code not in codes:
                codes.append(code)
    return codes


def _artifact_statuses(artifacts: dict[str, Any]) -> dict[str, str]:
    statuses = {
        "safety_status": str(artifacts.get("safety_guardian", {}).get("status", "")),
        "evidence_status": str(artifacts.get("evidence", {}).get("status", "")),
        "task_package_status": str(
            artifacts.get("task_package", {}).get("chief_engineer", {}).get("status", "")
        ),
        "execution_plan_status": str(
            artifacts.get("execution_plan", {}).get("planner", {}).get("status", "")
        ),
        "execution_evidence_status": str(
            artifacts.get("execution_evidence_package", {}).get("executor", {}).get("status", "")
        ),
    }
    if "requirements" in artifacts:
        statuses["requirements_status"] = str(artifacts.get("requirements", {}).get("status", ""))
    return statuses


def _approval(loop_result: dict[str, Any]) -> dict[str, str]:
    approval = (
        loop_result.get("before", {})
        .get("execution_evidence_package", {})
        .get("approval", {})
    )
    return {
        "status": str(approval.get("status", "")),
        "approval_id": str(approval.get("approval_id", "")),
        "approved_task_id": str(approval.get("approved_task_id", "")),
        "approved_by": str(approval.get("approved_by", "")),
    }


def _finding(loop_result: dict[str, Any]) -> dict[str, Any]:
    selected = loop_result.get("selected_finding")
    if not isinstance(selected, dict):
        return {}
    finding = {}
    for key in ("code", "severity", "task_id", "transition_id", "scenario_id", "requirement_id"):
        value = selected.get(key)
        if isinstance(value, str):
            finding[key] = value
    return finding


def _chain(loop_result: dict[str, Any]) -> dict[str, Any]:
    actions = loop_result.get("repair_actions", [])
    if not isinstance(actions, list):
        actions = []
    after = loop_result.get("after")
    convergence = loop_result.get("convergence")
    return {
        "loop_kind": str(loop_result.get("kind", "")),
        "status": str(loop_result.get("status", "")),
        "finding": _finding(loop_result),
        "approval": _approval(loop_result),
        "repair": {
            "actions": [item for item in actions if isinstance(item, dict)],
            "performed": bool(actions),
        },
        "before": _artifact_statuses(loop_result.get("before", {})),
        "after": _artifact_statuses(after) if isinstance(after, dict) else {},
        "convergence": convergence if isinstance(convergence, dict) else {},
    }


def _open_findings(
    report_codes: list[str],
    chains: list[dict[str, Any]],
) -> list[str]:
    if not chains:
        return list(report_codes)
    open_codes: list[str] = []
    for chain in chains:
        status = chain.get("status")
        convergence = chain.get("convergence")
        if status == "converged":
            if isinstance(convergence, dict):
                for code in convergence.get("after_findings", []):
                    if isinstance(code, str) and code not in open_codes:
                        open_codes.append(code)
            continue
        if isinstance(convergence, dict) and convergence.get("after_findings"):
            for code in convergence.get("after_findings", []):
                if isinstance(code, str) and code not in open_codes:
                    open_codes.append(code)
            continue
        code = chain.get("finding", {}).get("code")
        if isinstance(code, str) and code and code not in open_codes:
            open_codes.append(code)
    return open_codes


def _review_status(
    *,
    loop_count: int,
    blocked_loops: int,
    needs_followup_loops: int,
    open_findings: list[str],
) -> str:
    if loop_count == 0 and not open_findings:
        return "no_findings"
    if blocked_loops:
        if any(code.startswith("CHECK_") for code in open_findings):
            return "blocked_pending_approval"
        return "blocked_pending_approval"
    if needs_followup_loops:
        return "needs_followup"
    if loop_count and not open_findings:
        return "converged"
    return "open_findings"


def build_candidate_review_packet(
    agent_outputs: dict[str, Any],
    *,
    task_package: dict[str, Any],
    execution_plan: dict[str, Any],
    execution_evidence_package: dict[str, Any],
    repair_loop_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build machine-readable finding -> approval -> repair -> convergence evidence."""
    loops = [item for item in repair_loop_results or [] if isinstance(item, dict)]
    chains = [_chain(loop_result) for loop_result in loops]
    report_codes = _finding_codes_from_reports(agent_outputs)
    open_findings = _open_findings(report_codes, chains)
    loop_count = len(chains)
    converged_loops = sum(1 for chain in chains if chain.get("status") == "converged")
    blocked_loops = sum(
        1
        for chain in chains
        if str(chain.get("status", "")).startswith("blocked")
    )
    needs_followup_loops = sum(
        1 for chain in chains if chain.get("status") == "needs_followup"
    )
    summary = {
        "total_findings": len(report_codes) if report_codes else len(open_findings),
        "loop_count": loop_count,
        "converged_loops": converged_loops,
        "blocked_loops": blocked_loops,
        "needs_followup_loops": needs_followup_loops,
        "open_findings": open_findings,
    }
    packet = {
        "$schema": CANDIDATE_REVIEW_PACKET_SCHEMA_ID,
        "kind": CANDIDATE_REVIEW_PACKET_KIND,
        "reviewer": {
            "agent_name": REVIEWER_AGENT_NAME,
            "status": _review_status(
                loop_count=loop_count,
                blocked_loops=blocked_loops,
                needs_followup_loops=needs_followup_loops,
                open_findings=open_findings,
            ),
            "loop_count": loop_count,
        },
        "boundary": _boundary(agent_outputs),
        "source_artifacts": _source_artifacts(
            agent_outputs,
            task_package=task_package,
            execution_plan=execution_plan,
            execution_evidence_package=execution_evidence_package,
        ),
        "summary": summary,
        "finding_chains": chains,
        "human_review_required": bool(open_findings or blocked_loops or needs_followup_loops),
    }
    validate_candidate_review_packet(packet)
    return packet


def validate_candidate_review_packet(packet: dict[str, Any]) -> None:
    """Validate schema and hard candidate-only boundary invariants."""
    _schema_validate(
        packet,
        schema_name=CANDIDATE_REVIEW_PACKET_SCHEMA_NAME,
        label="candidate review packet",
    )
    boundary = packet.get("boundary", {})
    if boundary.get("truth_effect") != "none":
        raise CandidateReviewPacketError("candidate review packet truth_effect must remain none")
    if boundary.get("controller_truth_modified") is not False:
        raise CandidateReviewPacketError("candidate review packet may not modify controller truth")
    if boundary.get("certification_claim") != "none":
        raise CandidateReviewPacketError("candidate review packet may not claim certification")


def build_candidate_review_packet_export(
    review_packet: dict[str, Any],
    *,
    export_id: str = CANDIDATE_REVIEW_PACKET_EXPORT_ID,
    source_route: str = CANDIDATE_REVIEW_PACKET_SOURCE_ROUTE,
    export_route: str = CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE,
    storage: str = "reference_packet",
) -> dict[str, Any]:
    """Wrap a candidate review packet in a stable external export envelope."""
    validate_candidate_review_packet(review_packet)
    packet = {
        "$schema": CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_ID,
        "kind": CANDIDATE_REVIEW_PACKET_EXPORT_KIND,
        "exporter": {
            "agent_name": CANDIDATE_REVIEW_PACKET_EXPORT_AGENT_NAME,
            "schema_version": CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_VERSION,
            "export_id": export_id,
            "source_route": source_route,
            "export_route": export_route,
            "storage": storage,
            "status": "available",
        },
        "review_packet_ref": {
            "schema": CANDIDATE_REVIEW_PACKET_SCHEMA_ID,
            "kind": CANDIDATE_REVIEW_PACKET_KIND,
            "reviewer_status": str(review_packet.get("reviewer", {}).get("status", "")),
        },
        "boundary": dict(review_packet.get("boundary", {})),
        "review_packet": review_packet,
        "machine_readable": True,
        "human_review_required": bool(review_packet.get("human_review_required")),
    }
    validate_candidate_review_packet_export(packet)
    return packet


def validate_candidate_review_packet_export(packet: dict[str, Any]) -> None:
    """Validate a stable external candidate-review-packet export envelope."""
    _schema_validate(
        packet,
        schema_name=CANDIDATE_REVIEW_PACKET_EXPORT_SCHEMA_NAME,
        label="candidate review packet export",
    )
    review_packet = packet.get("review_packet")
    if not isinstance(review_packet, dict):
        raise CandidateReviewPacketError("candidate review packet export must embed review_packet")
    validate_candidate_review_packet(review_packet)
    if packet.get("machine_readable") is not True:
        raise CandidateReviewPacketError("candidate review packet export must be machine_readable")
    if packet.get("boundary") != review_packet.get("boundary"):
        raise CandidateReviewPacketError(
            "candidate review packet export boundary must match embedded review_packet"
        )
    ref = packet.get("review_packet_ref", {})
    if ref.get("schema") != CANDIDATE_REVIEW_PACKET_SCHEMA_ID:
        raise CandidateReviewPacketError("candidate review packet export ref schema mismatch")
    if ref.get("kind") != CANDIDATE_REVIEW_PACKET_KIND:
        raise CandidateReviewPacketError("candidate review packet export ref kind mismatch")
    if ref.get("reviewer_status") != review_packet.get("reviewer", {}).get("status"):
        raise CandidateReviewPacketError("candidate review packet export reviewer status mismatch")


def load_candidate_review_packet_export(path: Path | None = None) -> dict[str, Any]:
    """Load the stable file-backed review packet export used by external checks."""
    export_path = path or REFERENCE_CANDIDATE_REVIEW_PACKET_EXPORT_PATH
    packet = json.loads(export_path.read_text(encoding="utf-8"))
    validate_candidate_review_packet_export(packet)
    return packet
