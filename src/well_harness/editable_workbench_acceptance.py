"""End-to-end acceptance evidence bundles for the editable workbench.

The bundle proves a sandbox candidate workflow. It does not execute or approve
certified truth changes.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.editable_change_request import (
    build_editable_workbench_change_request,
    build_pr_proof_packet,
)
from well_harness.editable_control_model import (
    EditableControlModelValidationError,
    build_reference_editable_control_model,
    editable_control_model_hash,
    validate_editable_control_model,
)
from well_harness.editable_timeline_sandbox import (
    compare_editable_timeline_to_baseline,
    run_baseline_timeline_trace,
    run_editable_timeline_candidate,
)
from well_harness.timeline_engine import Timeline


EDITABLE_ACCEPTANCE_BUNDLE_KIND = "well-harness-editable-workbench-acceptance-bundle"
EDITABLE_ACCEPTANCE_MANIFEST_KIND = "well-harness-editable-workbench-acceptance-manifest"
EDITABLE_ACCEPTANCE_VERSION = 1
REFERENCE_SAMPLE_SYSTEM_ID = "thrust-reverser"
CHANGE_REQUEST_LAYER = "L9"
ACCEPTANCE_FILE_KEYS = (
    "bundle_json",
    "model_json",
    "candidate_trace_json",
    "diff_report_json",
    "change_request_json",
    "pr_proof_packet_markdown",
    "summary_markdown",
)


class EditableWorkbenchAcceptanceError(ValueError):
    """Raised when a candidate cannot produce a safe acceptance bundle."""


def _json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _manifest_self_checksum(manifest: dict[str, Any]) -> str:
    checksum_payload = copy.deepcopy(manifest)
    integrity = checksum_payload.get("integrity")
    if isinstance(integrity, dict):
        integrity.pop("manifest_json", None)
    return _sha256_bytes(_json_text(checksum_payload).encode("utf-8"))


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "artifact"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _now_archive_stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def _ensure_safe_candidate(model: dict[str, Any]) -> None:
    if model.get("system_id") != REFERENCE_SAMPLE_SYSTEM_ID:
        raise EditableWorkbenchAcceptanceError(
            f"{model.get('system_id')} is frozen or not the active reference sample; "
            "JER-160 acceptance only archives thrust-reverser sandbox candidates."
        )
    boundaries = model.get("boundaries") or {}
    if boundaries.get("truth_level_impact") != "none":
        raise EditableWorkbenchAcceptanceError("truth_level escalation is outside Codex lane")
    if boundaries.get("dal_pssa_impact") != "none":
        raise EditableWorkbenchAcceptanceError("dal escalation is outside Codex lane")
    try:
        validate_editable_control_model(model)
    except EditableControlModelValidationError as exc:
        raise EditableWorkbenchAcceptanceError(str(exc)) from exc


def derive_baseline_draft() -> dict[str, Any]:
    """Derive the reference sandbox draft without changing certified truth."""
    return build_reference_editable_control_model()


def apply_rule_threshold_edit(
    model: dict[str, Any],
    *,
    node_id: str,
    rule_name: str,
    threshold_value: Any,
    label: str | None = None,
) -> dict[str, Any]:
    """Apply a deterministic sandbox edit to one rule threshold."""
    candidate = copy.deepcopy(model)
    node = next((item for item in candidate["nodes"] if item["id"] == node_id), None)
    if node is None:
        raise EditableWorkbenchAcceptanceError(f"unknown node_id {node_id!r}")
    rule = next((item for item in node.get("rules", []) if item.get("name") == rule_name), None)
    if rule is None:
        raise EditableWorkbenchAcceptanceError(f"unknown rule_name {rule_name!r} for {node_id}")
    rule["threshold_value"] = threshold_value
    if label is not None:
        node["label"] = label
    _ensure_safe_candidate(candidate)
    return candidate


def _workflow_steps() -> list[str]:
    return [
        "derive_baseline_draft",
        "edit_candidate_graph",
        "run_sandbox_timeline",
        "compare_baseline_diff",
        "generate_changerequest",
        "generate_pr_proof_packet",
        "archive_evidence_bundle",
    ]


def build_editable_workbench_acceptance_bundle(
    model: dict[str, Any],
    timeline: Timeline,
    *,
    source_ref: str,
    created_at: str | None = None,
    test_delta: str = "JER-160 targeted acceptance pending",
) -> dict[str, Any]:
    """Build the deterministic Core v1 acceptance evidence bundle."""
    _ensure_safe_candidate(model)
    try:
        baseline_trace = run_baseline_timeline_trace(timeline)
        candidate_trace = run_editable_timeline_candidate(
            model,
            timeline,
            baseline_trace=baseline_trace,
        )
        scenario_id = timeline.title or "editable-workbench-acceptance"
        diff_report = compare_editable_timeline_to_baseline(
            model,
            timeline,
            scenario_id=scenario_id,
        )
    except ValueError as exc:
        raise EditableWorkbenchAcceptanceError(str(exc)) from exc
    change_request = build_editable_workbench_change_request(
        model,
        diff_report,
        title="Editable Workbench Core v1 acceptance handoff",
        source_ref=source_ref,
        layer=CHANGE_REQUEST_LAYER,
        created_at=created_at,
    )
    pr_proof_packet = build_pr_proof_packet(
        change_request,
        test_delta=test_delta,
    )
    model_hash = editable_control_model_hash(model)
    baseline_model = derive_baseline_draft()
    return {
        "kind": EDITABLE_ACCEPTANCE_BUNDLE_KIND,
        "version": EDITABLE_ACCEPTANCE_VERSION,
        "created_at_utc": created_at or _now_iso(),
        "source_ref": source_ref,
        "workflow": {
            "status": "sandbox_candidate_acceptance",
            "steps": _workflow_steps(),
        },
        "model": {
            "model_id": model["model_id"],
            "model_hash": model_hash,
            "system_id": model["system_id"],
            "truth_status": model["truth_status"],
            "view_status": model["view_status"],
        },
        "baseline_model": {
            "model_id": baseline_model["model_id"],
            "model_hash": editable_control_model_hash(baseline_model),
            "system_id": baseline_model["system_id"],
            "truth_status": baseline_model["truth_status"],
        },
        "candidate_model": {
            "model_id": model["model_id"],
            "model_hash": model_hash,
            "system_id": model["system_id"],
            "truth_status": model["truth_status"],
        },
        "model_payload": model,
        "baseline_trace": {
            "system_id": model["system_id"],
            "source_of_truth": "ReferenceDeployControllerAdapter/FantuiExecutor",
            "frame_count": len(baseline_trace.frames),
            "timeline_title": timeline.title,
        },
        "candidate_trace": candidate_trace,
        "diff_report": diff_report,
        "change_request": change_request,
        "pr_proof_packet": pr_proof_packet,
        "frozen_references": {
            "c919-etras": {
                "access": "read_only_frozen",
                "truth_effect": "none",
            }
        },
        "red_lines": {
            "controller_truth_modified": False,
            "frozen_adapter_modified": False,
            "truth_level_impact": "none",
            "dal_pssa_impact": "none",
            "product_llm_chat_restored": False,
        },
    }


def _summary_markdown(bundle: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Editable Workbench Acceptance Bundle",
            "",
            f"- Source Ref: `{bundle['source_ref']}`",
            f"- System: `{bundle['model']['system_id']}`",
            f"- Model Hash: `{bundle['model']['model_hash']}`",
            f"- Candidate Truth Status: `{bundle['model']['truth_status']}`",
            f"- Diff Verdict: `{bundle['diff_report']['verdict']}`",
            f"- Assertion Status: `{bundle['candidate_trace']['assertion_status']}`",
            "- Truth-level impact: `none`",
            "- DAL/PSSA impact: `none`",
            "- C919 E-TRAS: `read_only_frozen`",
            "",
            "## Files",
            "- `model.json`",
            "- `candidate_trace.json`",
            "- `diff_report.json`",
            "- `change_request.json`",
            "- `pr_proof_packet.md`",
            "- `manifest.json`",
            "",
        ]
    )


def _create_unique_archive_dir(root: Path, archive_name: str) -> Path:
    for index in range(1, 10_001):
        name = archive_name if index == 1 else f"{archive_name}-{index}"
        candidate = root / name
        try:
            candidate.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        return candidate
    raise EditableWorkbenchAcceptanceError(f"could not create archive under {root}")


def archive_editable_workbench_acceptance_bundle(
    bundle: dict[str, Any],
    archive_root: str | Path,
) -> dict[str, Any]:
    """Archive an acceptance bundle with a checksum manifest."""
    root = Path(archive_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    archive_name = "-".join(
        [
            _now_archive_stamp(),
            _slugify(bundle["source_ref"]),
            _slugify(bundle["model"]["system_id"]),
            bundle["model"]["model_hash"][:12],
        ]
    )
    archive_dir = _create_unique_archive_dir(root, archive_name)
    files = {
        "bundle_json": archive_dir / "bundle.json",
        "model_json": archive_dir / "model.json",
        "candidate_trace_json": archive_dir / "candidate_trace.json",
        "diff_report_json": archive_dir / "diff_report.json",
        "change_request_json": archive_dir / "change_request.json",
        "pr_proof_packet_markdown": archive_dir / "pr_proof_packet.md",
        "summary_markdown": archive_dir / "README.md",
    }
    files["bundle_json"].write_text(_json_text(bundle), encoding="utf-8")
    files["model_json"].write_text(_json_text(bundle["model_payload"]), encoding="utf-8")
    files["candidate_trace_json"].write_text(_json_text(bundle["candidate_trace"]), encoding="utf-8")
    files["diff_report_json"].write_text(_json_text(bundle["diff_report"]), encoding="utf-8")
    files["change_request_json"].write_text(_json_text(bundle["change_request"]), encoding="utf-8")
    files["pr_proof_packet_markdown"].write_text(bundle["pr_proof_packet"] + "\n", encoding="utf-8")
    files["summary_markdown"].write_text(_summary_markdown(bundle), encoding="utf-8")

    manifest = {
        "kind": EDITABLE_ACCEPTANCE_MANIFEST_KIND,
        "version": EDITABLE_ACCEPTANCE_VERSION,
        "created_at_utc": _now_iso(),
        "archive_dir": ".",
        "source_ref": bundle["source_ref"],
        "model_hash": bundle["model"]["model_hash"],
        "diff_verdict": bundle["diff_report"]["verdict"],
        "files": {
            key: path.relative_to(archive_dir).as_posix()
            for key, path in files.items()
        },
        "integrity": {
            key: _sha256_file(path)
            for key, path in files.items()
        },
    }
    manifest_path = archive_dir / "manifest.json"
    manifest["integrity"]["manifest_json"] = _manifest_self_checksum(manifest)
    manifest_path.write_text(_json_text(manifest), encoding="utf-8")
    return {
        "archive_dir": str(archive_dir),
        "manifest_path": str(manifest_path),
        "files": {
            key: str(path)
            for key, path in files.items()
        },
    }


def _resolve_manifest_file(file_value: str, *, archive_dir: Path) -> Path:
    path = (archive_dir / file_value).resolve()
    try:
        path.relative_to(archive_dir.resolve())
    except ValueError as exc:
        raise EditableWorkbenchAcceptanceError("manifest file escapes archive directory") from exc
    return path


def validate_editable_workbench_acceptance_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: str | Path | None = None,
    require_existing_files: bool = True,
) -> tuple[str, ...]:
    """Validate acceptance archive manifest fields and checksums."""
    issues: list[str] = []
    if manifest.get("kind") != EDITABLE_ACCEPTANCE_MANIFEST_KIND:
        issues.append(f"kind must be {EDITABLE_ACCEPTANCE_MANIFEST_KIND!r}.")
    if manifest.get("version") != EDITABLE_ACCEPTANCE_VERSION:
        issues.append(f"version must be {EDITABLE_ACCEPTANCE_VERSION}.")
    files = manifest.get("files")
    if not isinstance(files, dict):
        issues.append("files must be a JSON object.")
        files = {}
    integrity = manifest.get("integrity")
    if not isinstance(integrity, dict):
        issues.append("integrity must be a JSON object.")
        integrity = {}
    manifest_checksum = integrity.get("manifest_json")
    if not isinstance(manifest_checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", manifest_checksum):
        issues.append("integrity.manifest_json must be a 64-character SHA256 hex string.")
    elif _manifest_self_checksum(manifest) != manifest_checksum:
        issues.append("integrity.manifest_json: checksum mismatch")
    archive_dir = (
        Path(manifest_path).expanduser().resolve().parent
        if manifest_path is not None
        else None
    )
    for key in ACCEPTANCE_FILE_KEYS:
        value = files.get(key)
        if not isinstance(value, str) or not value:
            issues.append(f"files.{key} must be a non-empty string.")
            continue
        checksum = integrity.get(key)
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            issues.append(f"integrity.{key} must be a 64-character SHA256 hex string.")
        if archive_dir is None or not require_existing_files:
            continue
        try:
            artifact_path = _resolve_manifest_file(value, archive_dir=archive_dir)
        except EditableWorkbenchAcceptanceError as exc:
            issues.append(str(exc))
            continue
        if not artifact_path.is_file():
            issues.append(f"files.{key} does not exist: {value}")
            continue
        if checksum and _sha256_file(artifact_path) != checksum:
            issues.append(f"integrity.{key}: checksum mismatch")
    return tuple(issues)
