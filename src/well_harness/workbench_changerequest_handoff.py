from __future__ import annotations

import hashlib
import json
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
