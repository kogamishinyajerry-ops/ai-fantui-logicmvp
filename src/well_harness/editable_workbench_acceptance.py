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
from well_harness.editable_workbench_run import build_workbench_sandbox_run_response
from well_harness.timeline_engine import Timeline


EDITABLE_ACCEPTANCE_BUNDLE_KIND = "well-harness-editable-workbench-acceptance-bundle"
EDITABLE_ACCEPTANCE_MANIFEST_KIND = "well-harness-editable-workbench-acceptance-manifest"
EDITABLE_ACCEPTANCE_VERSION = 1
REFERENCE_SAMPLE_SYSTEM_ID = "thrust-reverser"
CHANGE_REQUEST_LAYER = "L9"
ACCEPTANCE_FILE_KEYS = (
    "bundle_json",
    "model_json",
    "validation_report_json",
    "sandbox_run_json",
    "candidate_trace_json",
    "diff_report_json",
    "change_request_json",
    "known_blockers_json",
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
        "capture_ui_draft",
        "derive_baseline_draft",
        "canonicalize_editable_control_model",
        "validate_candidate_graph",
        "run_sandbox_timeline",
        "compare_baseline_diff",
        "generate_changerequest",
        "generate_pr_proof_packet",
        "archive_evidence_bundle",
    ]


def _default_validation_report() -> dict[str, Any]:
    return {
        "kind": "well-harness-workbench-graph-validation-report",
        "version": 1,
        "status": "pass",
        "issue_count": 0,
        "categories": {
            "invalid_edge": [],
            "dangling_port": [],
            "duplicate_edge": [],
            "unsafe_op": [],
            "missing_node": [],
        },
        "issues": [],
        "truth_level_impact": "none",
    }


def _default_known_blockers() -> list[dict[str, str]]:
    return [
        {
            "gate": "opt-in e2e workbench smoke",
            "status": "known_baseline_blocker",
            "evidence": 'Page.goto(... wait_until="networkidle") timeout; e2e 49/49 is not claimed.',
            "truth_effect": "none",
        },
        {
            "gate": "PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json",
            "status": "not_claimed_clean",
            "evidence": "Official Codex-lane mypy gate is defined by JER-171; current full-repo strict gate remains blocked by existing baseline typing errors.",
            "truth_effect": "none",
        },
    ]


def _sandbox_run_from_artifacts(
    *,
    scenario_id: str,
    model_hash: str,
    diff_report: dict[str, Any],
    validation_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kind": "well-harness-workbench-sandbox-run",
        "version": 1,
        "scenario_id": scenario_id,
        "verdict": diff_report["verdict"],
        "model_hash": model_hash,
        "truth_level_impact": "none",
        "validation_report": validation_report,
        "diff_report": diff_report,
    }


def _candidate_trace_summary(
    *,
    scenario_id: str,
    candidate_trace: dict[str, Any] | None,
    diff_report: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    if candidate_trace is not None:
        trace = copy.deepcopy(candidate_trace)
        trace.setdefault("source", source)
        return trace
    scenario_result = diff_report.get("scenario_result") or {}
    return {
        "source": source,
        "scenario_id": scenario_result.get("scenario_id", scenario_id),
        "assertion_status": scenario_result.get("assertion_status", "not_run"),
        "frame_count": scenario_result.get("frame_count", 0),
    }


def _build_acceptance_bundle_from_artifacts(
    model: dict[str, Any],
    *,
    source_ref: str,
    scenario_id: str,
    baseline_trace_frame_count: int,
    baseline_trace_title: str | None,
    candidate_trace: dict[str, Any] | None,
    diff_report: dict[str, Any],
    validation_report: dict[str, Any] | None = None,
    sandbox_run: dict[str, Any] | None = None,
    created_at: str | None = None,
    test_delta: str = "JER-169 targeted acceptance pending; e2e 49/49 not claimed; mypy clean not claimed",
    known_blockers: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a deterministic Runtime v3 acceptance evidence bundle."""
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
    validation_payload = validation_report or _default_validation_report()
    sandbox_payload = sandbox_run or _sandbox_run_from_artifacts(
        scenario_id=scenario_id,
        model_hash=model_hash,
        diff_report=diff_report,
        validation_report=validation_payload,
    )
    candidate_trace_payload = _candidate_trace_summary(
        scenario_id=scenario_id,
        candidate_trace=candidate_trace,
        diff_report=diff_report,
        source="acceptance_artifact",
    )
    blockers = list(known_blockers or _default_known_blockers())
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
            "frame_count": baseline_trace_frame_count,
            "timeline_title": baseline_trace_title,
        },
        "validation_report": validation_payload,
        "sandbox_run": sandbox_payload,
        "candidate_trace": candidate_trace_payload,
        "diff_report": diff_report,
        "change_request": change_request,
        "pr_proof_packet": pr_proof_packet,
        "known_blockers": blockers,
        "gate_claims": {
            "default_pytest": "required",
            "gsd_validation": "required",
            "adversarial": "required",
            "e2e_49_49": "not_claimed",
            "mypy_strict_clean": "not_claimed",
        },
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


def build_editable_workbench_acceptance_bundle(
    model: dict[str, Any],
    timeline: Timeline,
    *,
    source_ref: str,
    created_at: str | None = None,
    test_delta: str = "JER-169 targeted acceptance pending; e2e 49/49 not claimed; mypy clean not claimed",
    known_blockers: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build the deterministic acceptance evidence bundle from a model."""
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
    model_hash = editable_control_model_hash(model)
    validation_report = _default_validation_report()
    sandbox_run = _sandbox_run_from_artifacts(
        scenario_id=scenario_id,
        model_hash=model_hash,
        diff_report=diff_report,
        validation_report=validation_report,
    )
    return _build_acceptance_bundle_from_artifacts(
        model,
        source_ref=source_ref,
        scenario_id=scenario_id,
        baseline_trace_frame_count=len(baseline_trace.frames),
        baseline_trace_title=timeline.title,
        candidate_trace=candidate_trace,
        diff_report=diff_report,
        validation_report=validation_report,
        sandbox_run=sandbox_run,
        created_at=created_at,
        test_delta=test_delta,
        known_blockers=known_blockers,
    )


def build_runtime_v3_acceptance_bundle_from_ui_draft(
    request_payload: dict[str, Any],
    *,
    source_ref: str = "JER-169",
    created_at: str | None = None,
    test_delta: str = "JER-169 targeted acceptance pending; e2e 49/49 not claimed; mypy clean not claimed",
    known_blockers: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build the Runtime v3 acceptance bundle from a `/workbench` draft request."""
    sandbox_run, _ = build_workbench_sandbox_run_response(request_payload)
    verdict = sandbox_run.get("verdict")
    if verdict in {"invalid_model", "invalid_scenario"}:
        raise EditableWorkbenchAcceptanceError(str(sandbox_run.get("error") or verdict))
    model = sandbox_run.get("canonical_model")
    if not isinstance(model, dict):
        raise EditableWorkbenchAcceptanceError("sandbox run did not return canonical_model")
    _ensure_safe_candidate(model)
    diff_report = sandbox_run.get("diff_report")
    if not isinstance(diff_report, dict):
        raise EditableWorkbenchAcceptanceError("sandbox run did not return diff_report")
    validation_report = sandbox_run.get("validation_report") or _default_validation_report()
    summary = sandbox_run.get("summary") or {}
    candidate_trace = {
        "source": "workbench_sandbox_run_response",
        "scenario_id": sandbox_run.get("scenario_id", "nominal_landing"),
        "assertion_status": summary.get("assertion_status", "not_run"),
        "frame_count": summary.get("frame_count", 0),
        "first_divergence": summary.get("first_divergence"),
    }
    return _build_acceptance_bundle_from_artifacts(
        model,
        source_ref=source_ref,
        scenario_id=str(sandbox_run.get("scenario_id") or "nominal_landing"),
        baseline_trace_frame_count=summary.get("frame_count", 0),
        baseline_trace_title=str(sandbox_run.get("scenario_id") or "nominal_landing"),
        candidate_trace=candidate_trace,
        diff_report=diff_report,
        validation_report=validation_report,
        sandbox_run=sandbox_run,
        created_at=created_at,
        test_delta=test_delta,
        known_blockers=known_blockers,
    )


def _summary_markdown(bundle: dict[str, Any]) -> str:
    blockers = bundle.get("known_blockers") or []
    blocker_lines = [
        f"- `{item['gate']}`: `{item['status']}`"
        for item in blockers
        if isinstance(item, dict) and "gate" in item and "status" in item
    ]
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
            f"- Graph Validation: `{bundle['validation_report']['status']}`",
            "- Truth-level impact: `none`",
            "- DAL/PSSA impact: `none`",
            "- C919 E-TRAS: `read_only_frozen`",
            "",
            "## Files",
            "- `model.json`",
            "- `validation_report.json`",
            "- `sandbox_run.json`",
            "- `candidate_trace.json`",
            "- `diff_report.json`",
            "- `change_request.json`",
            "- `known_blockers.json`",
            "- `pr_proof_packet.md`",
            "- `manifest.json`",
            "",
            "## Known Blockers",
            *(blocker_lines or ["- None"]),
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
        "validation_report_json": archive_dir / "validation_report.json",
        "sandbox_run_json": archive_dir / "sandbox_run.json",
        "candidate_trace_json": archive_dir / "candidate_trace.json",
        "diff_report_json": archive_dir / "diff_report.json",
        "change_request_json": archive_dir / "change_request.json",
        "known_blockers_json": archive_dir / "known_blockers.json",
        "pr_proof_packet_markdown": archive_dir / "pr_proof_packet.md",
        "summary_markdown": archive_dir / "README.md",
    }
    files["bundle_json"].write_text(_json_text(bundle), encoding="utf-8")
    files["model_json"].write_text(_json_text(bundle["model_payload"]), encoding="utf-8")
    files["validation_report_json"].write_text(_json_text(bundle["validation_report"]), encoding="utf-8")
    files["sandbox_run_json"].write_text(_json_text(bundle["sandbox_run"]), encoding="utf-8")
    files["candidate_trace_json"].write_text(_json_text(bundle["candidate_trace"]), encoding="utf-8")
    files["diff_report_json"].write_text(_json_text(bundle["diff_report"]), encoding="utf-8")
    files["change_request_json"].write_text(_json_text(bundle["change_request"]), encoding="utf-8")
    files["known_blockers_json"].write_text(_json_text(bundle["known_blockers"]), encoding="utf-8")
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
