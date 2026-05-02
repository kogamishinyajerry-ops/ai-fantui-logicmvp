from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


CHANGE_REQUEST_HANDOFF_KIND = "well-harness-workbench-changerequest-handoff-packet"
CHANGE_REQUEST_HANDOFF_VERSION = 1
CHANGE_REQUEST_HANDOFF_SCHEMA_ID = (
    "https://well-harness.local/json_schema/workbench_changerequest_handoff_v1.schema.json"
)
CHANGE_REQUEST_HANDOFF_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "json_schema"
    / "workbench_changerequest_handoff_v1.schema.json"
)
CHANGE_REQUEST_HANDOFF_CANONICALIZATION = "json.sort_keys.separators.v1"
CHANGE_REQUEST_HANDOFF_CHECKSUM_ALGORITHM = "ui_fnv1a32_over_canonical_json"
CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_NOT_PRESENT = "not_present"
CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_PASS = "pass"
CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL = "fail"
CHANGE_REQUEST_HANDOFF_UI_CHECKSUM_PREFIX = "ui_draft_"
FOUNDATION_REVIEW_ARCHIVE_KIND = "well-harness-workbench-foundation-review-archive"
FOUNDATION_REVIEW_ARCHIVE_VERSION = "workbench-foundation-review-archive.v1"
FOUNDATION_REVIEW_ARCHIVE_VALIDATION_KIND = (
    "well-harness-workbench-foundation-review-archive-validation-report"
)
FOUNDATION_REVIEW_ARCHIVE_VALIDATION_VERSION = (
    "workbench-foundation-review-archive-validation.v1"
)
FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS = (
    "workspace_document",
    "editable_graph_document",
    "model_json",
    "diff_summary",
    "candidate_baseline_diff_review_v2",
    "sandbox_test_bench",
    "sandbox_test_run_report",
    "candidate_debugger_view",
    "preflight_analyzer_report",
    "hardware_bindings",
    "hardware_evidence_v2",
    "interface_matrix",
    "connector_pin_map",
    "hardware_interface_designer",
    "hardware_interface_designer_validation",
    "changerequest_body",
    "pr_proof_packet",
    "changerequest_proof_packet",
    "changerequest_handoff_packet",
    "gate_claims",
    "known_blockers",
    "red_line_metadata",
)

_CONST_FIELDS: tuple[tuple[str, Any], ...] = (
    ("$schema", CHANGE_REQUEST_HANDOFF_SCHEMA_ID),
    ("kind", CHANGE_REQUEST_HANDOFF_KIND),
    ("version", CHANGE_REQUEST_HANDOFF_VERSION),
    ("packet_state", "draft"),
    ("candidate_state", "sandbox_candidate"),
    ("certification_claim", "none"),
    ("truth_effect", "none"),
    ("live_linear_mutation", False),
    ("controller_truth_modified", False),
    ("frozen_assets_modified", False),
    ("truth_level_impact", "none"),
    ("dal_pssa_impact", "none"),
    ("red_lines_touched", "none"),
    ("artifact_scope", "browser_local_draft"),
    ("truth_scope", "evidence_only"),
    ("runtime_mutates_truth", False),
)

_REQUIRED_TOP_LEVEL_FIELDS = tuple(field_name for field_name, _expected in _CONST_FIELDS) + (
    "serialization",
    "outcome",
    "context",
    "acceptance",
    "boundaries",
    "evidence_required",
    "red_line_metadata",
    "metadata",
    "artifacts",
    "linear_issue_body",
    "pr_proof_packet",
    "changerequest_proof_packet",
)
_ALLOWED_TOP_LEVEL_FIELDS = frozenset(_REQUIRED_TOP_LEVEL_FIELDS)
_SERIALIZATION_FIELDS = frozenset(("canonicalization", "checksum_algorithm"))
_RED_LINE_METADATA_FIELDS = frozenset(
    (
        "red_lines_touched",
        "truth_level_impact",
        "dal_pssa_impact",
        "controller_truth_modified",
        "frozen_assets_modified",
        "live_linear_mutation",
    )
)
_METADATA_FIELDS = frozenset(
    (
        "linear_issue",
        "linear_project",
        "adapter",
        "layer",
        "selected_scenario_id",
        "selected_node_id",
        "changed_model_hash",
        "sandbox_verdict",
        "diff_review_v2",
        "test_delta",
        "agent_eligible",
    )
)
_TEST_DELTA_FIELDS = frozenset(
    (
        "targeted_pytest",
        "default_pytest",
        "gsd_validation_suite",
        "adversarial_8_8",
        "e2e_49_49",
        "mypy_strict_clean",
        "truth_effect",
    )
)
_ARTIFACT_FIELDS = frozenset(
    (
        "linear_issue_body_checksum",
        "pr_proof_packet_checksum",
        "changerequest_proof_packet_checksum",
        "diff_review_v2_checksum",
    )
)


def load_changerequest_handoff_schema() -> dict[str, Any]:
    with CHANGE_REQUEST_HANDOFF_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    if not isinstance(schema, dict):
        raise ValueError("ChangeRequest handoff schema root must be a JSON object.")
    return schema


def canonical_changerequest_handoff_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def changerequest_handoff_hash(payload: Mapping[str, Any]) -> str:
    canonical_text = canonical_changerequest_handoff_json(payload)
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def stable_evidence_archive_json(value: Any) -> str:
    return json.dumps(
        _normalize_evidence_archive_value(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def changerequest_handoff_ui_checksum(payload: Mapping[str, Any]) -> str:
    return _ui_draft_fnv1a32(stable_evidence_archive_json(payload))


def validate_changerequest_handoff_archive_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return _archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL,
            source_path="archive",
            issues=("archive payload must be a JSON object.",),
        )

    source_path = "changerequest_handoff_packet"
    packet_candidate = payload.get("changerequest_handoff_packet")
    if packet_candidate is None:
        model_json = payload.get("model_json")
        if isinstance(model_json, Mapping) and model_json.get("changerequest_handoff_packet") is not None:
            source_path = "model_json.changerequest_handoff_packet"
            packet_candidate = model_json.get("changerequest_handoff_packet")

    if packet_candidate is None:
        return _archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_NOT_PRESENT,
            source_path="changerequest_handoff_packet",
            issues=(),
        )

    if not isinstance(packet_candidate, Mapping):
        return _archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL,
            source_path=source_path,
            issues=(f"{source_path} must be a JSON object when present.",),
        )

    issues = list(validate_changerequest_handoff_packet(packet_candidate))
    expected_ui_checksum = changerequest_handoff_ui_checksum(packet_candidate)
    recorded_ui_checksum = _recorded_handoff_ui_checksum(payload)
    checksum_status = "not_recorded"

    if recorded_ui_checksum is None:
        if payload.get("kind") == "well-harness-workbench-evidence-archive":
            issues.append(
                "checksums.changerequest_handoff_packet_checksum is required "
                "when an evidence archive contains changerequest_handoff_packet."
            )
            checksum_status = "missing"
    elif recorded_ui_checksum != expected_ui_checksum:
        issues.append(
            "checksums.changerequest_handoff_packet_checksum mismatch "
            f"(expected {expected_ui_checksum}, got {recorded_ui_checksum})."
        )
        checksum_status = "mismatch"
    else:
        checksum_status = "pass"

    status = (
        CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL
        if issues
        else CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_PASS
    )
    return _archive_validation_report(
        status=status,
        source_path=source_path,
        issues=tuple(issues),
        canonical_hash=changerequest_handoff_hash(packet_candidate),
        ui_checksum=expected_ui_checksum,
        recorded_ui_checksum=recorded_ui_checksum,
        checksum_status=checksum_status,
    )


def assert_valid_changerequest_handoff_archive_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    report = validate_changerequest_handoff_archive_payload(payload)
    if report["status"] == CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL:
        issues = "; ".join(str(issue) for issue in report["issues"])
        raise ValueError(f"invalid ChangeRequest handoff archive payload: {issues}")
    return report


def validate_foundation_review_archive_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return _foundation_archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL,
            source_path="archive",
            issues=("archive payload must be a JSON object.",),
        )

    source_path = "foundation_review_archive"
    review_archive = payload.get("foundation_review_archive")
    if review_archive is None:
        model_json = payload.get("model_json")
        if isinstance(model_json, Mapping) and model_json.get("foundation_review_archive") is not None:
            source_path = "model_json.foundation_review_archive"
            review_archive = model_json.get("foundation_review_archive")

    if review_archive is None:
        return _foundation_archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_NOT_PRESENT,
            source_path="foundation_review_archive",
            issues=(),
        )

    if not isinstance(review_archive, Mapping):
        return _foundation_archive_validation_report(
            status=CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL,
            source_path=source_path,
            issues=(f"{source_path} must be a JSON object when present.",),
        )

    issues = list(validate_foundation_review_archive_bundle(review_archive))
    expected_ui_checksum = changerequest_handoff_ui_checksum(review_archive)
    recorded_ui_checksum = _recorded_foundation_review_archive_ui_checksum(payload)
    checksum_status = "not_recorded"

    if recorded_ui_checksum is None:
        if payload.get("kind") == "well-harness-workbench-evidence-archive":
            issues.append(
                "checksums.foundation_review_archive_checksum is required "
                "when an evidence archive contains foundation_review_archive."
            )
            checksum_status = "missing"
    elif recorded_ui_checksum != expected_ui_checksum:
        issues.append(
            "checksums.foundation_review_archive_checksum mismatch "
            f"(expected {expected_ui_checksum}, got {recorded_ui_checksum})."
        )
        checksum_status = "mismatch"
    else:
        checksum_status = "pass"

    status = (
        CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL
        if issues
        else CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_PASS
    )
    return _foundation_archive_validation_report(
        status=status,
        source_path=source_path,
        issues=tuple(issues),
        canonical_hash=changerequest_handoff_hash(review_archive),
        ui_checksum=expected_ui_checksum,
        recorded_ui_checksum=recorded_ui_checksum,
        checksum_status=checksum_status,
    )


def assert_valid_foundation_review_archive_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    report = validate_foundation_review_archive_payload(payload)
    if report["status"] == CHANGE_REQUEST_HANDOFF_ARCHIVE_STATUS_FAIL:
        issues = "; ".join(str(issue) for issue in report["issues"])
        raise ValueError(f"invalid foundation review archive payload: {issues}")
    return report


def validate_foundation_review_archive_bundle(payload: Mapping[str, Any]) -> tuple[str, ...]:
    issues: list[str] = []
    if not isinstance(payload, Mapping):
        return ("foundation_review_archive must be a JSON object.",)

    expected_constants = {
        "kind": FOUNDATION_REVIEW_ARCHIVE_KIND,
        "version": FOUNDATION_REVIEW_ARCHIVE_VERSION,
        "candidate_state": "sandbox_candidate",
        "certification_claim": "none",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "runtime_truth_effect": "none",
        "truth_effect": "none",
    }
    for key, expected_value in expected_constants.items():
        if payload.get(key) != expected_value:
            issues.append(f"foundation_review_archive.{key} must be {expected_value!r}.")
    for key in ("controller_truth_modified", "frozen_assets_modified", "live_linear_mutation"):
        if payload.get(key) is not False:
            issues.append(f"foundation_review_archive.{key} must be False.")

    required_sections = payload.get("required_sections")
    if not isinstance(required_sections, list):
        issues.append("foundation_review_archive.required_sections must be an array.")
    else:
        missing_required_section_names = [
            section
            for section in FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS
            if section not in required_sections
        ]
        if missing_required_section_names:
            issues.append(
                "foundation_review_archive.required_sections missing "
                f"{missing_required_section_names!r}."
            )

    missing_sections = payload.get("missing_sections")
    if missing_sections not in ([], ()):
        issues.append("foundation_review_archive.missing_sections must be empty.")

    sections = payload.get("sections")
    if not isinstance(sections, Mapping):
        issues.append("foundation_review_archive.sections must be a JSON object.")
    else:
        for section_name in FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS:
            section = sections.get(section_name)
            if not isinstance(section, Mapping):
                issues.append(f"foundation_review_archive.sections.{section_name} must be a JSON object.")
                continue
            if section.get("status") != "present":
                issues.append(f"foundation_review_archive.sections.{section_name}.status must be 'present'.")
            if not _non_empty_string(section.get("checksum")) or section.get("checksum") == "missing":
                issues.append(f"foundation_review_archive.sections.{section_name}.checksum must be recorded.")
            if section.get("truth_effect") != "none":
                issues.append(f"foundation_review_archive.sections.{section_name}.truth_effect must be 'none'.")

    linear_ready = payload.get("linear_ready")
    if not isinstance(linear_ready, Mapping):
        issues.append("foundation_review_archive.linear_ready must be a JSON object.")
    else:
        if linear_ready.get("live_linear_mutation") is not False:
            issues.append("foundation_review_archive.linear_ready.live_linear_mutation must be False.")
        if linear_ready.get("browser_mutates_linear") is not False:
            issues.append("foundation_review_archive.linear_ready.browser_mutates_linear must be False.")
        if linear_ready.get("truth_effect") != "none":
            issues.append("foundation_review_archive.linear_ready.truth_effect must be 'none'.")

    for field_name in ("review_packet", "restore_contract", "preflight_summary"):
        field_value = payload.get(field_name)
        if not isinstance(field_value, Mapping):
            issues.append(f"foundation_review_archive.{field_name} must be a JSON object.")
        elif field_value.get("truth_effect") != "none":
            issues.append(f"foundation_review_archive.{field_name}.truth_effect must be 'none'.")

    return tuple(issues)


def validate_changerequest_handoff_packet(payload: Mapping[str, Any]) -> tuple[str, ...]:
    issues: list[str] = []
    if not isinstance(payload, Mapping):
        return ("ChangeRequest handoff packet root must be a JSON object.",)

    issues.extend(_validate_allowed_keys("root", payload, _ALLOWED_TOP_LEVEL_FIELDS))

    for field_name in _REQUIRED_TOP_LEVEL_FIELDS:
        if field_name not in payload:
            issues.append(f"{field_name} is required.")

    for field_name, expected_value in _CONST_FIELDS:
        actual_value = payload.get(field_name)
        if actual_value != expected_value:
            issues.append(f"{field_name} must be {expected_value!r}.")

    serialization = payload.get("serialization")
    if not isinstance(serialization, Mapping):
        issues.append("serialization must be a JSON object.")
    else:
        issues.extend(_validate_allowed_keys("serialization", serialization, _SERIALIZATION_FIELDS))
        if serialization.get("canonicalization") != CHANGE_REQUEST_HANDOFF_CANONICALIZATION:
            issues.append(f"serialization.canonicalization must be {CHANGE_REQUEST_HANDOFF_CANONICALIZATION!r}.")
        if serialization.get("checksum_algorithm") != CHANGE_REQUEST_HANDOFF_CHECKSUM_ALGORITHM:
            issues.append(f"serialization.checksum_algorithm must be {CHANGE_REQUEST_HANDOFF_CHECKSUM_ALGORITHM!r}.")

    for field_name in ("outcome", "context", "linear_issue_body", "pr_proof_packet"):
        if not _non_empty_string(payload.get(field_name)):
            issues.append(f"{field_name} must be a non-empty string.")

    for field_name in ("acceptance", "boundaries", "evidence_required"):
        issues.extend(_validate_non_empty_string_list(field_name, payload.get(field_name)))

    red_line_metadata = payload.get("red_line_metadata")
    if isinstance(red_line_metadata, Mapping):
        issues.extend(_validate_allowed_keys("red_line_metadata", red_line_metadata, _RED_LINE_METADATA_FIELDS))
    issues.extend(
        _validate_constant_object(
            "red_line_metadata",
            red_line_metadata,
            {
                "red_lines_touched": "none",
                "truth_level_impact": "none",
                "dal_pssa_impact": "none",
                "controller_truth_modified": False,
                "frozen_assets_modified": False,
                "live_linear_mutation": False,
            },
        )
    )

    metadata = payload.get("metadata")
    if not isinstance(metadata, Mapping):
        issues.append("metadata must be a JSON object.")
    else:
        issues.extend(_validate_allowed_keys("metadata", metadata, _METADATA_FIELDS))
        for field_name in (
            "linear_issue",
            "linear_project",
            "adapter",
            "layer",
            "selected_scenario_id",
            "selected_node_id",
            "changed_model_hash",
            "sandbox_verdict",
            "agent_eligible",
        ):
            if not _non_empty_string(metadata.get(field_name)):
                issues.append(f"metadata.{field_name} must be a non-empty string.")
        if not isinstance(metadata.get("diff_review_v2"), Mapping):
            issues.append("metadata.diff_review_v2 must be a JSON object.")
        test_delta = metadata.get("test_delta")
        issues.extend(_validate_test_delta(test_delta))

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, Mapping):
        issues.append("artifacts must be a JSON object.")
    else:
        issues.extend(_validate_allowed_keys("artifacts", artifacts, _ARTIFACT_FIELDS))
        for field_name in (
            "linear_issue_body_checksum",
            "pr_proof_packet_checksum",
            "changerequest_proof_packet_checksum",
            "diff_review_v2_checksum",
        ):
            if not _non_empty_string(artifacts.get(field_name)):
                issues.append(f"artifacts.{field_name} must be a non-empty string.")

    proof_packet = payload.get("changerequest_proof_packet")
    if not isinstance(proof_packet, Mapping):
        issues.append("changerequest_proof_packet must be a JSON object.")
    else:
        issues.extend(
            _validate_constant_object(
                "changerequest_proof_packet",
                proof_packet,
                {
                    "candidate_state": "sandbox_candidate",
                    "certification_claim": "none",
                    "truth_level_impact": "none",
                    "dal_pssa_impact": "none",
                    "red_lines_touched": "none",
                    "controller_truth_modified": False,
                    "frozen_assets_modified": False,
                    "truth_effect": "none",
                },
            )
        )
        linear = proof_packet.get("linear")
        if not isinstance(linear, Mapping):
            issues.append("changerequest_proof_packet.linear must be a JSON object.")
        elif linear.get("live_mutation") is not False:
            issues.append("changerequest_proof_packet.linear.live_mutation must be False.")

    return tuple(issues)


def assert_valid_changerequest_handoff_packet(payload: Mapping[str, Any]) -> None:
    issues = validate_changerequest_handoff_packet(payload)
    if issues:
        raise ValueError(f"invalid ChangeRequest handoff packet: {'; '.join(issues)}")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_allowed_keys(
    field_name: str,
    value: Mapping[str, Any],
    allowed_keys: frozenset[str],
) -> tuple[str, ...]:
    issues: list[str] = []
    for key in value:
        if key not in allowed_keys:
            prefix = "" if field_name == "root" else f"{field_name}."
            issues.append(f"{prefix}{key} is not part of ChangeRequest handoff packet version 1.")
    return tuple(issues)


def _validate_non_empty_string_list(field_name: str, value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        return (f"{field_name} must be a non-empty array.",)
    issues: list[str] = []
    for index, item in enumerate(value):
        if not _non_empty_string(item):
            issues.append(f"{field_name}[{index}] must be a non-empty string.")
    return tuple(issues)


def _validate_constant_object(
    field_name: str,
    value: Any,
    expected_values: Mapping[str, Any],
) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return (f"{field_name} must be a JSON object.",)
    issues: list[str] = []
    for key, expected_value in expected_values.items():
        if value.get(key) != expected_value:
            issues.append(f"{field_name}.{key} must be {expected_value!r}.")
    return tuple(issues)


def _validate_test_delta(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("metadata.test_delta must be a JSON object.",)
    issues: list[str] = []
    issues.extend(_validate_allowed_keys("metadata.test_delta", value, _TEST_DELTA_FIELDS))
    for field_name in _TEST_DELTA_FIELDS:
        if field_name not in value:
            issues.append(f"metadata.test_delta.{field_name} is required.")
    if value.get("e2e_49_49") != "not_claimed":
        issues.append("metadata.test_delta.e2e_49_49 must be 'not_claimed'.")
    if value.get("mypy_strict_clean") != "not_claimed":
        issues.append("metadata.test_delta.mypy_strict_clean must be 'not_claimed'.")
    if value.get("truth_effect") != "none":
        issues.append("metadata.test_delta.truth_effect must be 'none'.")
    return tuple(issues)


def _normalize_evidence_archive_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_evidence_archive_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple):
        return [_normalize_evidence_archive_value(item) for item in value]
    if isinstance(value, list):
        return [_normalize_evidence_archive_value(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _ui_draft_fnv1a32(text: str) -> str:
    hash_value = 2166136261
    utf16_units = text.encode("utf-16-le")
    for index in range(0, len(utf16_units), 2):
        code_unit = int.from_bytes(utf16_units[index : index + 2], "little")
        hash_value ^= code_unit
        hash_value = (hash_value * 16777619) & 0xFFFFFFFF
    return f"{CHANGE_REQUEST_HANDOFF_UI_CHECKSUM_PREFIX}{hash_value:08x}"


def _recorded_handoff_ui_checksum(payload: Mapping[str, Any]) -> str | None:
    checksums = payload.get("checksums")
    if not isinstance(checksums, Mapping):
        return None
    value = checksums.get("changerequest_handoff_packet_checksum")
    if isinstance(value, str) and value.strip():
        return value
    return None


def _recorded_foundation_review_archive_ui_checksum(payload: Mapping[str, Any]) -> str | None:
    checksums = payload.get("checksums")
    if not isinstance(checksums, Mapping):
        return None
    value = checksums.get("foundation_review_archive_checksum")
    if isinstance(value, str) and value.strip():
        return value
    return None


def _archive_validation_report(
    *,
    status: str,
    source_path: str,
    issues: tuple[str, ...],
    canonical_hash: str | None = None,
    ui_checksum: str | None = None,
    recorded_ui_checksum: str | None = None,
    checksum_status: str = "not_applicable",
) -> dict[str, Any]:
    return {
        "kind": "well-harness-workbench-changerequest-handoff-archive-validation",
        "version": 1,
        "status": status,
        "source_path": source_path,
        "issue_count": len(issues),
        "issues": list(issues),
        "canonical_hash": canonical_hash,
        "ui_checksum": ui_checksum,
        "recorded_ui_checksum": recorded_ui_checksum,
        "checksum_status": checksum_status,
        "truth_effect": "none",
    }


def _foundation_archive_validation_report(
    *,
    status: str,
    source_path: str,
    issues: tuple[str, ...],
    canonical_hash: str | None = None,
    ui_checksum: str | None = None,
    recorded_ui_checksum: str | None = None,
    checksum_status: str = "not_applicable",
) -> dict[str, Any]:
    return {
        "kind": FOUNDATION_REVIEW_ARCHIVE_VALIDATION_KIND,
        "version": FOUNDATION_REVIEW_ARCHIVE_VALIDATION_VERSION,
        "status": status,
        "source_path": source_path,
        "issue_count": len(issues),
        "issues": list(issues),
        "canonical_hash": canonical_hash,
        "ui_checksum": ui_checksum,
        "recorded_ui_checksum": recorded_ui_checksum,
        "checksum_status": checksum_status,
        "candidate_state": "sandbox_candidate",
        "certification_claim": "none",
        "truth_effect": "none",
    }
