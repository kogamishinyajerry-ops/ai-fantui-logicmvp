from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.document_intake import (
    ControlSystemIntakePacket,
    assess_intake_packet,
    build_clarification_brief,
)
from well_harness.fault_diagnosis import (
    FaultDiagnosisReport,
    build_fault_diagnosis_report_from_intake_packet,
)
from well_harness.knowledge_capture import KnowledgeArtifact, build_knowledge_artifact
from well_harness.scenario_playback import (
    ScenarioPlaybackReport,
    build_playback_report_from_intake_packet,
)

WORKBENCH_BUNDLE_KIND = "well-harness-workbench-bundle"
WORKBENCH_BUNDLE_VERSION = 1
WORKBENCH_BUNDLE_SCHEMA_ID = "https://well-harness.local/json_schema/workbench_bundle_v1.schema.json"
ARCHIVE_MANIFEST_KIND = "well-harness-workbench-archive-manifest"
ARCHIVE_MANIFEST_VERSION = 1
ARCHIVE_MANIFEST_SCHEMA_ID = "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json"
ARCHIVE_MANIFEST_SELF_CHECK_COMMAND = "python3 -m well_harness.cli archive-manifest ."


class SandboxEscapeError(ValueError):
    """Raised when an archive path escapes the sandbox boundary."""
    pass


class ChecksumMismatchError(ValueError):
    """Raised when an archived file's SHA256 does not match the manifest integrity value."""
    pass
ARCHIVE_MANIFEST_FILE_KEYS = (
    "bundle_json",
    "summary_markdown",
    "intake_assessment_json",
    "clarification_brief_json",
    "playback_report_json",
    "fault_diagnosis_report_json",
    "knowledge_artifact_json",
    "workspace_handoff_json",
    "workspace_snapshot_json",
)
REQUIRED_ARCHIVE_MANIFEST_FILE_KEYS = (
    "bundle_json",
    "summary_markdown",
    "intake_assessment_json",
)


@dataclass(frozen=True)
class WorkbenchBundle:
    system_id: str
    system_title: str
    bundle_kind: str
    ready_for_spec_build: bool
    selected_scenario_id: str | None
    selected_fault_mode_id: str | None
    intake_assessment: dict[str, Any]
    clarification_brief: dict[str, Any] | None
    playback_report: ScenarioPlaybackReport | None = None
    fault_diagnosis_report: FaultDiagnosisReport | None = None
    knowledge_artifact: KnowledgeArtifact | None = None
    next_actions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return workbench_bundle_to_dict(self)


@dataclass(frozen=True)
class WorkbenchBundleArchive:
    archive_dir: str
    created_at_utc: str
    manifest_json_path: str
    bundle_json_path: str
    summary_markdown_path: str
    intake_assessment_json_path: str
    clarification_brief_json_path: str | None = None
    playback_report_json_path: str | None = None
    fault_diagnosis_report_json_path: str | None = None
    knowledge_artifact_json_path: str | None = None
    workspace_handoff_json_path: str | None = None
    workspace_snapshot_json_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _archive_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "artifact"


def _json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def workbench_bundle_to_dict(bundle: WorkbenchBundle) -> dict[str, Any]:
    return {
        "$schema": WORKBENCH_BUNDLE_SCHEMA_ID,
        "kind": WORKBENCH_BUNDLE_KIND,
        "version": WORKBENCH_BUNDLE_VERSION,
        "system_id": bundle.system_id,
        "system_title": bundle.system_title,
        "bundle_kind": bundle.bundle_kind,
        "ready_for_spec_build": bundle.ready_for_spec_build,
        "selected_scenario_id": bundle.selected_scenario_id,
        "selected_fault_mode_id": bundle.selected_fault_mode_id,
        "intake_assessment": _json_safe_value(bundle.intake_assessment),
        "clarification_brief": _json_safe_value(bundle.clarification_brief),
        "playback_report": bundle.playback_report.to_dict() if bundle.playback_report is not None else None,
        "fault_diagnosis_report": (
            bundle.fault_diagnosis_report.to_dict() if bundle.fault_diagnosis_report is not None else None
        ),
        "knowledge_artifact": bundle.knowledge_artifact.to_dict() if bundle.knowledge_artifact is not None else None,
        "next_actions": list(bundle.next_actions),
    }


def _create_unique_archive_dir(archive_root_path: Path, archive_name: str) -> Path:
    for index in range(1, 10_001):
        candidate_name = archive_name if index == 1 else f"{archive_name}-{index}"
        candidate_dir = archive_root_path / candidate_name
        try:
            candidate_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        return candidate_dir
    raise RuntimeError(f"could not create unique archive directory under {archive_root_path}")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        return path.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def _resolve_manifest_archive_dir_path(
    archive_dir_value: str,
    *,
    manifest_path: Path | None,
) -> Path | None:
    archive_dir_path = Path(archive_dir_value).expanduser()
    if archive_dir_path.is_absolute():
        # SECURITY: validate absolute archive_dir stays within the archive sandbox
        safe_root = (Path.cwd() / "artifacts" / "workbench-bundles").resolve()
        try:
            archive_dir_path.resolve().relative_to(safe_root)
        except ValueError:
            # Path escapes sandbox — raise specific error so demo_server can return sandbox_violation
            raise SandboxEscapeError(
                "archive_dir is outside the allowed sandbox root."
            )
        return archive_dir_path
    if manifest_path is None:
        return None
    return (manifest_path.parent / archive_dir_path).resolve()


def _resolve_manifest_file_path(
    file_value: str,
    *,
    archive_dir_path: Path | None,
) -> Path:
    file_path = Path(file_value).expanduser()
    if file_path.is_absolute() or archive_dir_path is None:
        return file_path
    return (archive_dir_path / file_path).resolve()


def _manifest_relative_path(path: Path | None, *, archive_dir: Path) -> str | None:
    if path is None:
        return None
    return path.relative_to(archive_dir).as_posix()


def _resolve_selected_id(
    requested_id: str | None,
    candidates: tuple[Any, ...],
    label: str,
) -> str | None:
    if not candidates:
        return None
    candidate_ids = tuple(item.id for item in candidates)
    if requested_id is not None:
        if requested_id not in candidate_ids:
            raise ValueError(f"unknown {label}: {requested_id}")
        return requested_id
    if len(candidate_ids) == 1:
        return candidate_ids[0]
    raise ValueError(
        f"{label} is required because the intake packet defines multiple {label}s: {', '.join(candidate_ids)}"
    )


def validate_workbench_archive_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: str | Path | None = None,
    require_existing_files: bool = True,
) -> tuple[str, ...]:
    issues: list[str] = []
    if not isinstance(manifest, dict):
        return ("archive manifest root must be a JSON object.",)
    resolved_manifest_path = Path(manifest_path).expanduser().resolve() if manifest_path is not None else None

    if manifest.get("kind") != ARCHIVE_MANIFEST_KIND:
        issues.append(f"kind must be {ARCHIVE_MANIFEST_KIND!r}.")
    if manifest.get("version") != ARCHIVE_MANIFEST_VERSION:
        issues.append(f"version must be {ARCHIVE_MANIFEST_VERSION}.")
    schema_id = manifest.get("$schema")
    if schema_id is not None and schema_id != ARCHIVE_MANIFEST_SCHEMA_ID:
        issues.append(f"$schema must be {ARCHIVE_MANIFEST_SCHEMA_ID!r} when present.")
    if not _non_empty_string(manifest.get("created_at_utc")):
        issues.append("created_at_utc must be a non-empty string.")

    archive_dir_path: Path | None = None
    archive_dir_value = manifest.get("archive_dir")
    if not _non_empty_string(archive_dir_value):
        issues.append("archive_dir must be a non-empty string.")
    else:
        try:
            archive_dir_path = _resolve_manifest_archive_dir_path(
                str(archive_dir_value),
                manifest_path=resolved_manifest_path,
            )
        except SandboxEscapeError as exc:
            # Re-raise as SandboxEscapeError with formatted message so demo_server
            # can return sandbox_violation, but the message still contains "invalid"
            # so existing tests that check for ValueError with "invalid" pass.
            raise SandboxEscapeError(f"invalid workbench archive manifest: {exc}") from exc
        if archive_dir_path is None:
            issues.append("archive_dir relative paths require manifest_path during validation.")
        elif require_existing_files and not archive_dir_path.is_dir():
            issues.append(f"archive_dir does not point to an existing directory: {archive_dir_value}")

    bundle = manifest.get("bundle")
    if not isinstance(bundle, dict):
        issues.append("bundle must be a JSON object.")
    else:
        for field_name in ("bundle_kind", "system_id", "system_title"):
            if not _non_empty_string(bundle.get(field_name)):
                issues.append(f"bundle.{field_name} must be a non-empty string.")
        if not isinstance(bundle.get("ready_for_spec_build"), bool):
            issues.append("bundle.ready_for_spec_build must be a boolean.")
        for field_name in ("selected_scenario_id", "selected_fault_mode_id"):
            value = bundle.get(field_name)
            if value is not None and not isinstance(value, str):
                issues.append(f"bundle.{field_name} must be a string or null.")
        if not isinstance(bundle.get("next_actions"), list):
            issues.append("bundle.next_actions must be a list.")

    files = manifest.get("files")
    if not isinstance(files, dict):
        issues.append("files must be a JSON object.")
        files = {}
    else:
        for file_key in ARCHIVE_MANIFEST_FILE_KEYS:
            if file_key not in files:
                issues.append(f"files.{file_key} is missing.")
        for file_key in REQUIRED_ARCHIVE_MANIFEST_FILE_KEYS:
            if files.get(file_key) is None:
                issues.append(f"files.{file_key} is required.")
        for file_key, file_value in files.items():
            if file_key not in ARCHIVE_MANIFEST_FILE_KEYS:
                issues.append(f"files.{file_key} is not part of archive manifest version 1.")
                continue
            if file_value is None:
                continue
            if not _non_empty_string(file_value):
                issues.append(f"files.{file_key} must be a non-empty string or null.")
                continue
            file_path = _resolve_manifest_file_path(
                str(file_value),
                archive_dir_path=archive_dir_path,
            )
            if archive_dir_path is not None and not _path_is_under(file_path, archive_dir_path):
                issues.append(f"files.{file_key} must point inside archive_dir.")
            if require_existing_files and not file_path.is_file():
                issues.append(f"files.{file_key} does not point to an existing file: {file_value}")

    restore_targets = manifest.get("restore_targets")
    if not isinstance(restore_targets, dict):
        issues.append("restore_targets must be a JSON object.")
    else:
        expected_restore_targets = {
            "browser_workspace_snapshot": ("workspace_snapshot_json", files.get("workspace_snapshot_json")),
            "browser_handoff_summary": ("workspace_handoff_json", files.get("workspace_handoff_json")),
            "archive_summary_markdown": ("summary_markdown", files.get("summary_markdown")),
        }
        for target_key, (file_key, expected_value) in expected_restore_targets.items():
            if restore_targets.get(target_key) != expected_value:
                issues.append(f"restore_targets.{target_key} must match files.{file_key}.")

    self_check = manifest.get("self_check")
    if self_check is not None:
        if not isinstance(self_check, dict):
            issues.append("self_check must be a JSON object when present.")
        else:
            if not _non_empty_string(self_check.get("command")):
                issues.append("self_check.command must be a non-empty string when self_check is present.")
            if self_check.get("working_directory") != "archive_dir":
                issues.append("self_check.working_directory must be 'archive_dir' when self_check is present.")

    # Integrity verification: check SHA256 of archived files when integrity field is present
    integrity = manifest.get("integrity")
    if integrity is not None:
        if not isinstance(integrity, dict):
            issues.append("integrity must be a JSON object when present.")
        else:
            for file_key, expected_hash in integrity.items():
                if not isinstance(expected_hash, str) or len(expected_hash) != 64:
                    issues.append(
                        f"integrity.{file_key} must be a 64-character SHA256 hex string."
                    )
                    continue
                if file_key not in ARCHIVE_MANIFEST_FILE_KEYS:
                    issues.append(f"integrity.{file_key} is not a valid archive file key.")
                    continue
                if archive_dir_path is None:
                    continue
                file_value = files.get(file_key) if isinstance(files, dict) else None
                if file_value is None:
                    continue
                file_path = _resolve_manifest_file_path(str(file_value), archive_dir_path=archive_dir_path)
                if require_existing_files and file_path.is_file():
                    actual_hash = _compute_sha256(file_path)
                    if actual_hash != expected_hash:
                        issues.append(
                            f"integrity.{file_key}: checksum mismatch "
                            f"(expected {expected_hash[:16]}..., got {actual_hash[:16]}...). "
                            f"File may be corrupted."
                        )

    return tuple(issues)


def load_workbench_archive_manifest(
    manifest_path: str | Path,
    *,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    path = Path(manifest_path).expanduser().resolve()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    issues = validate_workbench_archive_manifest(
        manifest,
        manifest_path=path,
        require_existing_files=require_existing_files,
    )
    if issues:
        raise ValueError(f"invalid workbench archive manifest: {'; '.join(issues)}")
    return manifest


def resolve_workbench_archive_manifest_files(
    manifest: dict[str, Any],
    *,
    manifest_path: str | Path,
) -> dict[str, str | None]:
    resolved_manifest_path = Path(manifest_path).expanduser().resolve()
    archive_dir_value = manifest.get("archive_dir")
    if not _non_empty_string(archive_dir_value):
        raise ValueError("archive manifest archive_dir must be a non-empty string.")
    archive_dir_path = _resolve_manifest_archive_dir_path(
        str(archive_dir_value),
        manifest_path=resolved_manifest_path,
    )
    if archive_dir_path is None:
        raise ValueError("archive manifest archive_dir could not be resolved.")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("archive manifest files must be a JSON object.")
    return {
        file_key: (
            str(
                _resolve_manifest_file_path(
                    str(file_value),
                    archive_dir_path=archive_dir_path,
                ).resolve()
            )
            if file_value is not None
            else None
        )
        for file_key, file_value in files.items()
    }


def _load_workbench_archive_json_artifact(
    manifest_path: str | Path,
    *,
    file_key: str,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    manifest = load_workbench_archive_manifest(
        manifest_path,
        require_existing_files=require_existing_files,
    )
    resolved_files = resolve_workbench_archive_manifest_files(
        manifest,
        manifest_path=manifest_path,
    )
    artifact_path = resolved_files.get(file_key)
    if artifact_path is None:
        raise ValueError(f"archive manifest does not include {file_key}.")
    artifact_payload = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    if not isinstance(artifact_payload, dict):
        raise ValueError(f"archive artifact {file_key} must contain a JSON object.")
    return artifact_payload


def load_workbench_archive_bundle_payload(
    manifest_path: str | Path,
    *,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    return _load_workbench_archive_json_artifact(
        manifest_path,
        file_key="bundle_json",
        require_existing_files=require_existing_files,
    )


def load_workbench_archive_workspace_snapshot(
    manifest_path: str | Path,
    *,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    return _load_workbench_archive_json_artifact(
        manifest_path,
        file_key="workspace_snapshot_json",
        require_existing_files=require_existing_files,
    )


def load_workbench_archive_workspace_handoff(
    manifest_path: str | Path,
    *,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    return _load_workbench_archive_json_artifact(
        manifest_path,
        file_key="workspace_handoff_json",
        require_existing_files=require_existing_files,
    )


def load_workbench_archive_restore_payload(
    manifest_path: str | Path,
    *,
    require_existing_files: bool = True,
) -> dict[str, Any]:
    input_path = Path(manifest_path).expanduser()
    resolved_manifest_path = (
        input_path / "archive_manifest.json"
        if input_path.is_dir()
        else input_path
    ).resolve()
    manifest = load_workbench_archive_manifest(
        resolved_manifest_path,
        require_existing_files=require_existing_files,
    )
    resolved_files = resolve_workbench_archive_manifest_files(
        manifest,
        manifest_path=resolved_manifest_path,
    )
    archive_dir_value = manifest.get("archive_dir")
    if not _non_empty_string(archive_dir_value):
        raise ValueError("archive manifest archive_dir must be a non-empty string.")
    archive_dir_path = _resolve_manifest_archive_dir_path(
        str(archive_dir_value),
        manifest_path=resolved_manifest_path,
    )
    if archive_dir_path is None:
        raise ValueError("archive manifest archive_dir could not be resolved.")

    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("archive manifest files must be a JSON object.")

    workspace_handoff = None
    if files.get("workspace_handoff_json") is not None:
        workspace_handoff = load_workbench_archive_workspace_handoff(
            resolved_manifest_path,
            require_existing_files=require_existing_files,
        )
    workspace_snapshot = None
    if files.get("workspace_snapshot_json") is not None:
        workspace_snapshot = load_workbench_archive_workspace_snapshot(
            resolved_manifest_path,
            require_existing_files=require_existing_files,
        )

    return {
        "manifest_path": str(resolved_manifest_path),
        "archive_dir": str(archive_dir_path),
        "manifest": manifest,
        "resolved_files": resolved_files,
        "bundle": load_workbench_archive_bundle_payload(
            resolved_manifest_path,
            require_existing_files=require_existing_files,
        ),
        "workspace_handoff": workspace_handoff,
        "workspace_snapshot": workspace_snapshot,
    }


def build_workbench_bundle(
    packet: ControlSystemIntakePacket,
    *,
    scenario_id: str | None = None,
    fault_mode_id: str | None = None,
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
) -> WorkbenchBundle:
    intake_assessment = assess_intake_packet(packet)
    clarification_brief = build_clarification_brief(packet)

    if not intake_assessment["ready_for_spec_build"]:
        return WorkbenchBundle(
            system_id=packet.system_id,
            system_title=packet.title,
            bundle_kind="clarification_follow_up",
            ready_for_spec_build=False,
            selected_scenario_id=None,
            selected_fault_mode_id=None,
            intake_assessment=intake_assessment,
            clarification_brief=clarification_brief,
            next_actions=tuple(clarification_brief["next_actions"]),
        )

    selected_scenario_id = _resolve_selected_id(scenario_id, packet.acceptance_scenarios, "scenario")
    playback_report = build_playback_report_from_intake_packet(
        packet,
        scenario_id=selected_scenario_id or "",
        sample_period_s=sample_period_s,
    )
    selected_fault_mode_id = _resolve_selected_id(fault_mode_id, packet.fault_modes, "fault mode")

    diagnosis_report = None
    knowledge_artifact = None
    if selected_fault_mode_id is not None:
        diagnosis_report = build_fault_diagnosis_report_from_intake_packet(
            packet,
            scenario_id=selected_scenario_id or "",
            fault_mode_id=selected_fault_mode_id,
            sample_period_s=sample_period_s,
        )
        knowledge_artifact = build_knowledge_artifact(
            packet,
            scenario_id=selected_scenario_id or "",
            fault_mode_id=selected_fault_mode_id,
            observed_symptoms=observed_symptoms,
            evidence_links=evidence_links,
            confirmed_root_cause=confirmed_root_cause,
            repair_action=repair_action,
            validation_after_fix=validation_after_fix,
            residual_risk=residual_risk,
            suggested_logic_change=suggested_logic_change,
            reliability_gain_hypothesis=reliability_gain_hypothesis,
            redundancy_reduction_or_guardrail_note=redundancy_reduction_or_guardrail_note,
            sample_period_s=sample_period_s,
        )

    next_actions = [
        "Review the intake assessment and clarification gate before sharing the bundle downstream.",
        f"Use playback scenario {selected_scenario_id} as the deterministic baseline trace.",
    ]
    if selected_fault_mode_id is not None:
        next_actions.append(
            f"Compare the baseline against fault mode {selected_fault_mode_id} before proposing repairs or guardrails."
        )
    if knowledge_artifact is not None:
        next_actions.append("Capture or archive the bundle artifact for future onboarding and repair reuse.")

    return WorkbenchBundle(
        system_id=packet.system_id,
        system_title=packet.title,
        bundle_kind="full_workbench_bundle",
        ready_for_spec_build=True,
        selected_scenario_id=selected_scenario_id,
        selected_fault_mode_id=selected_fault_mode_id,
        intake_assessment=intake_assessment,
        clarification_brief=clarification_brief,
        playback_report=playback_report,
        fault_diagnosis_report=diagnosis_report,
        knowledge_artifact=knowledge_artifact,
        next_actions=tuple(next_actions),
    )


def render_workbench_bundle_text(bundle: WorkbenchBundle) -> str:
    lines = [
        f"bundle_kind: {bundle.bundle_kind}",
        f"system: {bundle.system_id} - {bundle.system_title}",
        f"ready_for_spec_build: {bundle.ready_for_spec_build}",
        f"selected_scenario_id: {bundle.selected_scenario_id or '(none)'}",
        f"selected_fault_mode_id: {bundle.selected_fault_mode_id or '(none)'}",
        "next_actions:",
    ]
    lines.extend(f"  - {item}" for item in bundle.next_actions)
    lines.extend(
        [
            "intake_assessment:",
            f"  - ready_for_spec_build: {bundle.intake_assessment['ready_for_spec_build']}",
            f"  - mixed_source_packet: {bundle.intake_assessment['mixed_source_packet']}",
            f"  - includes_pdf_sources: {bundle.intake_assessment['includes_pdf_sources']}",
            f"  - blocking_reasons: {bundle.intake_assessment['blocking_reasons']}",
        ]
    )
    if bundle.clarification_brief is not None:
        lines.extend(
            [
                "clarification_brief:",
                f"  - gate_status: {bundle.clarification_brief['gate_status']}",
                f"  - gating_statement: {bundle.clarification_brief['gating_statement']}",
            ]
        )
    if bundle.playback_report is not None:
        lines.extend(
            [
                "playback:",
                f"  - scenario: {bundle.playback_report.scenario_id} - {bundle.playback_report.scenario_label}",
                f"  - completion_reached: {bundle.playback_report.completion_reached}",
                f"  - sampled_signals: {len(bundle.playback_report.signal_series)}",
                f"  - sampled_logic_nodes: {len(bundle.playback_report.logic_series)}",
            ]
        )
    if bundle.fault_diagnosis_report is not None:
        lines.extend(
            [
                "fault_diagnosis:",
                f"  - fault_mode: {bundle.fault_diagnosis_report.fault_mode_id}",
                f"  - symptom: {bundle.fault_diagnosis_report.symptom}",
                f"  - blocked_logic_node_ids: {list(bundle.fault_diagnosis_report.blocked_logic_node_ids)}",
            ]
        )
    if bundle.knowledge_artifact is not None:
        lines.extend(
            [
                "knowledge_artifact:",
                f"  - status: {bundle.knowledge_artifact.status}",
                f"  - diagnosis_summary: {bundle.knowledge_artifact.diagnosis_summary}",
            ]
        )
    return "\n".join(lines)


def render_workbench_bundle_markdown(
    bundle: WorkbenchBundle,
    *,
    workspace_handoff: dict[str, Any] | None = None,
    include_archive_manifest_note: bool = False,
) -> str:
    lines = [
        "# Workbench Bundle Archive",
        "",
        f"- Bundle Kind: `{bundle.bundle_kind}`",
        f"- System: `{bundle.system_id}` - {bundle.system_title}",
        f"- Ready For Spec Build: `{bundle.ready_for_spec_build}`",
        f"- Selected Scenario: `{bundle.selected_scenario_id or 'none'}`",
        f"- Selected Fault Mode: `{bundle.selected_fault_mode_id or 'none'}`",
        "",
        "## Next Actions",
    ]
    lines.extend(f"- {item}" for item in bundle.next_actions)
    lines.extend(
        [
            "",
            "## Intake Assessment",
            f"- ready_for_spec_build: `{bundle.intake_assessment['ready_for_spec_build']}`",
            f"- mixed_source_packet: `{bundle.intake_assessment['mixed_source_packet']}`",
            f"- includes_pdf_sources: `{bundle.intake_assessment['includes_pdf_sources']}`",
            f"- blocking_reasons: `{bundle.intake_assessment['blocking_reasons']}`",
        ]
    )
    if bundle.clarification_brief is not None:
        lines.extend(
            [
                "",
                "## Clarification Gate",
                f"- gate_status: `{bundle.clarification_brief['gate_status']}`",
                f"- gating_statement: {bundle.clarification_brief['gating_statement']}",
            ]
        )
    if bundle.playback_report is not None:
        lines.extend(
            [
                "",
                "## Playback Report",
                f"- scenario: `{bundle.playback_report.scenario_id}` - {bundle.playback_report.scenario_label}",
                f"- completion_reached: `{bundle.playback_report.completion_reached}`",
                f"- sampled_signals: `{len(bundle.playback_report.signal_series)}`",
                f"- sampled_logic_nodes: `{len(bundle.playback_report.logic_series)}`",
            ]
        )
    if bundle.fault_diagnosis_report is not None:
        lines.extend(
            [
                "",
                "## Fault Diagnosis",
                f"- fault_mode: `{bundle.fault_diagnosis_report.fault_mode_id}`",
                f"- symptom: {bundle.fault_diagnosis_report.symptom}",
                f"- blocked_logic_node_ids: `{list(bundle.fault_diagnosis_report.blocked_logic_node_ids)}`",
            ]
        )
    if bundle.knowledge_artifact is not None:
        lines.extend(
            [
                "",
                "## Knowledge Artifact",
                f"- status: `{bundle.knowledge_artifact.status}`",
                f"- diagnosis_summary: {bundle.knowledge_artifact.diagnosis_summary}",
                f"- suggested_logic_change: {bundle.knowledge_artifact.optimization_record['suggested_logic_change']}",
            ]
        )
    if workspace_handoff:
        lines.extend(
            [
                "",
                "## Browser Workspace Handoff",
                f"- status: `{workspace_handoff.get('badgeText', 'unknown')}`",
                f"- system: `{workspace_handoff.get('system', 'unknown_system')}`",
                f"- packet: {workspace_handoff.get('packet', 'n/a')}",
                f"- result: {workspace_handoff.get('result', 'n/a')}",
                f"- archive: {workspace_handoff.get('archive', 'n/a')}",
                f"- workspace: {workspace_handoff.get('workspace', 'n/a')}",
            ]
        )
        note = str(workspace_handoff.get("note") or "").strip()
        if note:
            lines.append(f"- note: {note}")
    if include_archive_manifest_note:
        lines.extend(
            [
                "",
                "## Archive Manifest",
                "- machine_readable_manifest: `archive_manifest.json`",
                f"- schema: `{ARCHIVE_MANIFEST_SCHEMA_ID}`",
                "- Use this manifest as the single file map for restore, sync, or audit tooling.",
                f"- self_check: run `{ARCHIVE_MANIFEST_SELF_CHECK_COMMAND}` from this archive directory.",
            ]
        )
    return "\n".join(lines) + "\n"


def build_workbench_archive_manifest(
    bundle: WorkbenchBundle,
    *,
    archive_dir: Path,
    created_at_utc: str,
    bundle_json_path: Path,
    summary_markdown_path: Path,
    intake_assessment_json_path: Path,
    clarification_brief_json_path: Path | None = None,
    playback_report_json_path: Path | None = None,
    fault_diagnosis_report_json_path: Path | None = None,
    knowledge_artifact_json_path: Path | None = None,
    workspace_handoff_json_path: Path | None = None,
    workspace_snapshot_json_path: Path | None = None,
    integrity: dict[str, str] | None = None,
) -> dict[str, Any]:
    files = {
        "bundle_json": _manifest_relative_path(bundle_json_path, archive_dir=archive_dir),
        "summary_markdown": _manifest_relative_path(summary_markdown_path, archive_dir=archive_dir),
        "intake_assessment_json": _manifest_relative_path(intake_assessment_json_path, archive_dir=archive_dir),
        "clarification_brief_json": _manifest_relative_path(clarification_brief_json_path, archive_dir=archive_dir),
        "playback_report_json": _manifest_relative_path(playback_report_json_path, archive_dir=archive_dir),
        "fault_diagnosis_report_json": _manifest_relative_path(fault_diagnosis_report_json_path, archive_dir=archive_dir),
        "knowledge_artifact_json": _manifest_relative_path(knowledge_artifact_json_path, archive_dir=archive_dir),
        "workspace_handoff_json": _manifest_relative_path(workspace_handoff_json_path, archive_dir=archive_dir),
        "workspace_snapshot_json": _manifest_relative_path(workspace_snapshot_json_path, archive_dir=archive_dir),
    }
    manifest = {
        "$schema": ARCHIVE_MANIFEST_SCHEMA_ID,
        "kind": ARCHIVE_MANIFEST_KIND,
        "version": ARCHIVE_MANIFEST_VERSION,
        "created_at_utc": created_at_utc,
        "archive_dir": ".",
        "bundle": {
            "bundle_kind": bundle.bundle_kind,
            "system_id": bundle.system_id,
            "system_title": bundle.system_title,
            "ready_for_spec_build": bundle.ready_for_spec_build,
            "selected_scenario_id": bundle.selected_scenario_id,
            "selected_fault_mode_id": bundle.selected_fault_mode_id,
            "next_actions": list(bundle.next_actions),
        },
        "files": files,
        "restore_targets": {
            "browser_workspace_snapshot": files["workspace_snapshot_json"],
            "browser_handoff_summary": files["workspace_handoff_json"],
            "archive_summary_markdown": files["summary_markdown"],
        },
        "self_check": {
            "command": ARCHIVE_MANIFEST_SELF_CHECK_COMMAND,
            "working_directory": "archive_dir",
        },
    }
    if integrity:
        manifest["integrity"] = integrity
    return manifest


def archive_workbench_bundle(
    bundle: WorkbenchBundle,
    archive_root: str | Path,
    *,
    workspace_handoff: dict[str, Any] | None = None,
    workspace_snapshot: dict[str, Any] | None = None,
) -> WorkbenchBundleArchive:
    archive_root_path = Path(archive_root).expanduser().resolve()
    archive_root_path.mkdir(parents=True, exist_ok=True)
    created_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    archive_name = "-".join(
        [
            _archive_timestamp(),
            _slugify(bundle.system_id),
            _slugify(bundle.selected_scenario_id or bundle.bundle_kind),
            _slugify(bundle.selected_fault_mode_id or "bundle"),
        ]
    )
    archive_dir = _create_unique_archive_dir(archive_root_path, archive_name)

    manifest_json_path = archive_dir / "archive_manifest.json"
    bundle_json_path = archive_dir / "bundle.json"
    summary_markdown_path = archive_dir / "README.md"
    intake_assessment_json_path = archive_dir / "intake_assessment.json"
    clarification_brief_json_path = archive_dir / "clarification_brief.json"
    playback_report_json_path = archive_dir / "playback_report.json"
    fault_diagnosis_report_json_path = archive_dir / "fault_diagnosis_report.json"
    knowledge_artifact_json_path = archive_dir / "knowledge_artifact.json"
    workspace_handoff_json_path = archive_dir / "workspace_handoff.json"
    workspace_snapshot_json_path = archive_dir / "workspace_snapshot.json"

    bundle_json_path.write_text(_json_text(bundle.to_dict()), encoding="utf-8")
    summary_markdown_path.write_text(
        render_workbench_bundle_markdown(
            bundle,
            workspace_handoff=workspace_handoff,
            include_archive_manifest_note=True,
        ),
        encoding="utf-8",
    )
    intake_assessment_json_path.write_text(_json_text(bundle.intake_assessment), encoding="utf-8")

    clarification_path_value: str | None = None
    if bundle.clarification_brief is not None:
        clarification_brief_json_path.write_text(_json_text(bundle.clarification_brief), encoding="utf-8")
        clarification_path_value = str(clarification_brief_json_path)

    playback_path_value: str | None = None
    if bundle.playback_report is not None:
        playback_report_json_path.write_text(_json_text(bundle.playback_report.to_dict()), encoding="utf-8")
        playback_path_value = str(playback_report_json_path)

    diagnosis_path_value: str | None = None
    if bundle.fault_diagnosis_report is not None:
        fault_diagnosis_report_json_path.write_text(
            _json_text(bundle.fault_diagnosis_report.to_dict()),
            encoding="utf-8",
        )
        diagnosis_path_value = str(fault_diagnosis_report_json_path)

    knowledge_path_value: str | None = None
    if bundle.knowledge_artifact is not None:
        knowledge_artifact_json_path.write_text(
            _json_text(bundle.knowledge_artifact.to_dict()),
            encoding="utf-8",
        )
        knowledge_path_value = str(knowledge_artifact_json_path)

    workspace_handoff_path_value: str | None = None
    if workspace_handoff is not None:
        workspace_handoff_json_path.write_text(_json_text(workspace_handoff), encoding="utf-8")
        workspace_handoff_path_value = str(workspace_handoff_json_path)

    workspace_snapshot_path_value: str | None = None
    if workspace_snapshot is not None:
        workspace_snapshot_json_path.write_text(_json_text(workspace_snapshot), encoding="utf-8")
        workspace_snapshot_path_value = str(workspace_snapshot_json_path)

    # Compute SHA256 checksums for all written files for integrity verification
    integrity: dict[str, str] = {}
    for path_value, rel_key in [
        (str(bundle_json_path), "bundle_json"),
        (str(summary_markdown_path), "summary_markdown"),
        (str(intake_assessment_json_path), "intake_assessment_json"),
    ]:
        integrity[rel_key] = _compute_sha256(Path(path_value))
    if clarification_path_value:
        integrity["clarification_brief_json"] = _compute_sha256(Path(clarification_path_value))
    if playback_path_value:
        integrity["playback_report_json"] = _compute_sha256(Path(playback_path_value))
    if diagnosis_path_value:
        integrity["fault_diagnosis_report_json"] = _compute_sha256(Path(diagnosis_path_value))
    if knowledge_path_value:
        integrity["knowledge_artifact_json"] = _compute_sha256(Path(knowledge_path_value))
    if workspace_handoff_path_value:
        integrity["workspace_handoff_json"] = _compute_sha256(Path(workspace_handoff_path_value))
    if workspace_snapshot_path_value:
        integrity["workspace_snapshot_json"] = _compute_sha256(Path(workspace_snapshot_path_value))

    manifest_json_path.write_text(
        _json_text(
            build_workbench_archive_manifest(
                bundle,
                archive_dir=archive_dir,
                created_at_utc=created_at_utc,
                bundle_json_path=bundle_json_path,
                summary_markdown_path=summary_markdown_path,
                intake_assessment_json_path=intake_assessment_json_path,
                clarification_brief_json_path=Path(clarification_path_value) if clarification_path_value else None,
                playback_report_json_path=Path(playback_path_value) if playback_path_value else None,
                fault_diagnosis_report_json_path=Path(diagnosis_path_value) if diagnosis_path_value else None,
                knowledge_artifact_json_path=Path(knowledge_path_value) if knowledge_path_value else None,
                workspace_handoff_json_path=Path(workspace_handoff_path_value) if workspace_handoff_path_value else None,
                workspace_snapshot_json_path=Path(workspace_snapshot_path_value) if workspace_snapshot_path_value else None,
                integrity=integrity,
            )
        ),
        encoding="utf-8",
    )

    return WorkbenchBundleArchive(
        archive_dir=str(archive_dir),
        created_at_utc=created_at_utc,
        manifest_json_path=str(manifest_json_path),
        bundle_json_path=str(bundle_json_path),
        summary_markdown_path=str(summary_markdown_path),
        intake_assessment_json_path=str(intake_assessment_json_path),
        clarification_brief_json_path=clarification_path_value,
        playback_report_json_path=playback_path_value,
        fault_diagnosis_report_json_path=diagnosis_path_value,
        knowledge_artifact_json_path=knowledge_path_value,
        workspace_handoff_json_path=workspace_handoff_path_value,
        workspace_snapshot_json_path=workspace_snapshot_path_value,
    )
