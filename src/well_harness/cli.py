from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from well_harness.demo import answer_demo_prompt, demo_answer_to_payload, render_demo_answer
from well_harness.document_intake import (
    assess_intake_packet,
    build_clarification_brief,
    intake_template_payload,
    load_intake_packet,
    render_clarification_brief_text,
    render_intake_assessment_text,
)
from well_harness.fault_diagnosis import (
    build_fault_diagnosis_report_from_intake_packet,
    render_fault_diagnosis_text,
)
from well_harness.knowledge_capture import build_knowledge_artifact, render_knowledge_artifact_text
from well_harness.runner import SimulationRunner
from well_harness.scenarios import BUILT_IN_SCENARIOS
from well_harness.scenario_playback import build_playback_report_from_intake_packet, render_playback_report_text
from well_harness.second_system_smoke import (
    build_second_system_smoke_report,
    render_second_system_smoke_text,
)
from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict
from well_harness.two_system_runtime_comparison import (
    build_two_system_runtime_comparison_report,
    render_two_system_runtime_comparison_text,
)
from well_harness.workbench_bundle import (
    archive_workbench_bundle,
    build_workbench_bundle,
    resolve_workbench_archive_manifest_files,
    render_workbench_bundle_text,
    validate_workbench_archive_manifest,
)

LOGIC_CHOICES = ("logic1", "logic2", "logic3", "logic4")
JSON_SCHEMA_VERSION = "1.0"
JSON_SCHEMA_NAME = "well_harness.debug"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="well_harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a built-in scenario")
    run_parser.add_argument("scenario", choices=sorted(BUILT_IN_SCENARIOS))
    run_parser.add_argument(
        "--tail",
        type=int,
        default=20,
        help="Items to print from the end of the text view",
    )
    run_parser.add_argument(
        "--view",
        choices=("timeline", "events", "explain", "diagnose"),
        default="timeline",
        help="Choose the debug view to render",
    )
    run_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Choose human-readable text or structured JSON output",
    )
    run_parser.add_argument(
        "--full",
        action="store_true",
        help="Print the full text timeline or event list instead of only the tail",
    )
    run_parser.add_argument(
        "--logic",
        choices=LOGIC_CHOICES,
        help="Logic to explain when using --view explain",
    )
    run_parser.add_argument(
        "--time",
        type=float,
        help="Simulation time to inspect when using --view explain; nearest trace row is selected",
    )

    demo_parser = subparsers.add_parser("demo", help="Answer a controlled demo prompt")
    demo_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Choose human-readable text or structured JSON output",
    )
    demo_parser.add_argument(
        "prompt",
        nargs="+",
        help="Controlled demo prompt, e.g. '触发 logic3 会发生什么'",
    )

    spec_parser = subparsers.add_parser("spec", help="Export the current reference control-system spec")
    spec_parser.add_argument(
        "--format",
        choices=("json",),
        default="json",
        help="Export the reference spec as JSON",
    )

    intake_parser = subparsers.add_parser("intake", help="Assess a mixed-doc/PDF intake packet for a new control system")
    intake_parser.add_argument(
        "packet_path",
        nargs="?",
        help="Path to a JSON intake packet. Omit when using --template.",
    )
    intake_parser.add_argument(
        "--template",
        action="store_true",
        help="Print a starter JSON packet template instead of assessing a file.",
    )
    intake_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the intake report as text or JSON.",
    )
    intake_parser.add_argument(
        "--follow-up",
        action="store_true",
        help="Render an engineer-facing clarification brief instead of the basic intake assessment.",
    )
    playback_parser = subparsers.add_parser("playback", help="Compile an intake packet scenario into monitor-vs-time playback data")
    playback_parser.add_argument("packet_path", help="Path to a JSON intake packet.")
    playback_parser.add_argument("--scenario", required=True, help="Scenario id inside the intake packet to replay.")
    playback_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for the generated playback trace.",
    )
    playback_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the playback report as text or JSON.",
    )
    diagnosis_parser = subparsers.add_parser("diagnose-fault", help="Inject a fault mode and generate a chain diagnosis report")
    diagnosis_parser.add_argument("packet_path", help="Path to a JSON intake packet.")
    diagnosis_parser.add_argument("--scenario", required=True, help="Scenario id inside the intake packet to replay.")
    diagnosis_parser.add_argument("--fault-mode", required=True, help="Fault mode id inside the intake packet to inject.")
    diagnosis_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for the generated diagnostic playback traces.",
    )
    diagnosis_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the diagnosis report as text or JSON.",
    )
    knowledge_parser = subparsers.add_parser(
        "capture-knowledge",
        help="Turn a diagnosed fault scenario into a knowledge artifact with incident, resolution, and optimization fields",
    )
    knowledge_parser.add_argument("packet_path", help="Path to a JSON intake packet.")
    knowledge_parser.add_argument("--scenario", required=True, help="Scenario id inside the intake packet.")
    knowledge_parser.add_argument("--fault-mode", required=True, help="Fault mode id inside the intake packet.")
    knowledge_parser.add_argument("--observed-symptoms", help="Observed symptoms summary. Defaults to the fault-mode symptom.")
    knowledge_parser.add_argument(
        "--evidence-link",
        action="append",
        default=[],
        help="Repeat to attach evidence links for the incident record.",
    )
    knowledge_parser.add_argument("--confirmed-root-cause", help="Confirmed root cause after troubleshooting.")
    knowledge_parser.add_argument("--repair-action", help="Repair action taken by the engineer.")
    knowledge_parser.add_argument("--validation-after-fix", help="How the fix was validated.")
    knowledge_parser.add_argument("--residual-risk", help="Residual risk after the fix.")
    knowledge_parser.add_argument("--suggested-logic-change", help="Optional override for the suggested logic change field.")
    knowledge_parser.add_argument(
        "--reliability-gain-hypothesis",
        help="Optional override for the reliability gain hypothesis field.",
    )
    knowledge_parser.add_argument(
        "--guardrail-note",
        help="Optional override for the redundancy/guardrail note field.",
    )
    knowledge_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for the embedded diagnosis playback.",
    )
    knowledge_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the knowledge artifact as text or JSON.",
    )
    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Compile intake assessment, clarification, playback, diagnosis, and knowledge into one engineer-facing bundle",
    )
    bundle_parser.add_argument("packet_path", help="Path to a JSON intake packet.")
    bundle_parser.add_argument(
        "--scenario",
        help="Scenario id inside the intake packet. Defaults to the only scenario when exactly one exists.",
    )
    bundle_parser.add_argument(
        "--fault-mode",
        help="Fault mode id inside the intake packet. Defaults to the only fault mode when exactly one exists.",
    )
    bundle_parser.add_argument("--observed-symptoms", help="Observed symptoms summary. Defaults to the fault-mode symptom.")
    bundle_parser.add_argument(
        "--evidence-link",
        action="append",
        default=[],
        help="Repeat to attach evidence links for the bundle incident record.",
    )
    bundle_parser.add_argument("--confirmed-root-cause", help="Confirmed root cause after troubleshooting.")
    bundle_parser.add_argument("--repair-action", help="Repair action taken by the engineer.")
    bundle_parser.add_argument("--validation-after-fix", help="How the fix was validated.")
    bundle_parser.add_argument("--residual-risk", help="Residual risk after the fix.")
    bundle_parser.add_argument("--suggested-logic-change", help="Optional override for the suggested logic change field.")
    bundle_parser.add_argument(
        "--reliability-gain-hypothesis",
        help="Optional override for the reliability gain hypothesis field.",
    )
    bundle_parser.add_argument(
        "--guardrail-note",
        help="Optional override for the redundancy/guardrail note field.",
    )
    bundle_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for playback and diagnosis inside the bundle.",
    )
    bundle_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the bundle as text or JSON.",
    )
    bundle_parser.add_argument(
        "--archive-dir",
        help="Optional root directory under which the bundle should be archived as JSON + Markdown artifacts.",
    )
    manifest_parser = subparsers.add_parser(
        "archive-manifest",
        help="Validate and summarize a workbench archive_manifest.json file",
    )
    manifest_parser.add_argument(
        "manifest_path",
        help="Path to archive_manifest.json or to the archive directory that contains it.",
    )
    manifest_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the validation result as text or JSON.",
    )
    manifest_parser.add_argument(
        "--skip-file-check",
        action="store_true",
        help="Validate manifest shape without requiring referenced archive files to exist.",
    )
    second_system_smoke_parser = subparsers.add_parser(
        "second-system-smoke",
        help="Run the reusable second-system smoke proof against the default adapter-backed runtime path or an explicit intake packet",
    )
    second_system_smoke_parser.add_argument(
        "--proof-mode",
        choices=("truth-adapter", "intake-packet"),
        help="Choose whether the smoke proof should run the default adapter-backed runtime path or the legacy intake-packet bundle path.",
    )
    second_system_smoke_parser.add_argument(
        "--adapter-id",
        help="Optional truth-adapter id. Defaults to the landing-gear adapter when proof-mode is truth-adapter.",
    )
    second_system_smoke_parser.add_argument(
        "--packet-path",
        help="Optional path to a JSON intake packet. When provided without --proof-mode, the smoke proof switches to intake-packet mode.",
    )
    second_system_smoke_parser.add_argument(
        "--scenario",
        help="Optional scenario id override. Defaults to the only scenario when exactly one exists.",
    )
    second_system_smoke_parser.add_argument(
        "--fault-mode",
        help="Optional fault mode id override. Defaults to the only fault mode when exactly one exists.",
    )
    second_system_smoke_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for playback and diagnosis inside the smoke bundle.",
    )
    second_system_smoke_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the second-system smoke report as text or JSON.",
    )
    two_system_runtime_comparison_parser = subparsers.add_parser(
        "two-system-runtime-comparison",
        help="Compare the adapter-backed runtime proof chain across the reference thrust-reverser and landing-gear systems.",
    )
    two_system_runtime_comparison_parser.add_argument(
        "--sample-period",
        type=float,
        default=0.5,
        help="Sampling interval in seconds for playback and diagnosis inside the comparison proof.",
    )
    two_system_runtime_comparison_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the two-system runtime comparison report as text or JSON.",
    )
    return parser


def render_rows(rows, tail: int, full: bool = False) -> str:
    selected = rows if full else rows[-tail:]
    header = (
        " time   TRA   SW1 SW2 TLS  PLS  VDT  POS%  L1 L2 L3 L4  TLS_s PLS_s"
        "  TLS115  540V  EEC  PLSPWR MOTOR THR_LOCK"
    )
    lines = [header]
    for row in selected:
        lines.append(
            f"{row.time_s:5.1f} "
            f"{row.tra_deg:6.1f} "
            f"{int(row.sw1):4d} "
            f"{int(row.sw2):3d} "
            f"{int(row.tls_unlocked_ls):3d} "
            f"{int(row.all_pls_unlocked_ls):3d} "
            f"{int(row.deploy_90_percent_vdt):3d} "
            f"{row.deploy_position_percent:5.1f} "
            f"{int(row.logic1_active):3d} "
            f"{int(row.logic2_active):2d} "
            f"{int(row.logic3_active):2d} "
            f"{int(row.logic4_active):2d} "
            f"{row.plant_state.tls_powered_s:6.2f} "
            f"{row.plant_state.pls_powered_s:5.2f} "
            f"{int(row.tls_115vac_cmd):7d} "
            f"{int(row.etrac_540vdc_cmd):5d} "
            f"{int(row.eec_deploy_cmd):4d} "
            f"{int(row.pls_power_cmd):7d} "
            f"{int(row.pdu_motor_cmd):6d} "
            f"{int(row.throttle_lock_release_cmd):9d}"
        )
    return "\n".join(lines)


def render_events(events, tail: int, full: bool = False) -> str:
    selected = events if full else events[-tail:]
    lines = [" time  changes"]
    for event in selected:
        change_text = ", ".join(
            f"{change.field_name}:{_format_event_value(change.before)}->{_format_event_value(change.after)}"
            for change in event.changes
        )
        lines.append(f"{event.time_s:5.1f}  {change_text}")
    if len(lines) == 1:
        lines.append(" (no tracked transitions)")
    return "\n".join(lines)


def render_explain(row, logic_name: str) -> str:
    logic_explain = row.controller_explain.by_logic_name(logic_name)
    lines = [
        (
            f"time={_format_debug_value(row.time_s)} logic={logic_explain.logic_name} "
            f"active={_format_debug_value(logic_explain.active)}"
        ),
        "condition current comparison threshold passed",
    ]
    for condition in logic_explain.conditions:
        lines.append(
            f"{condition.name} "
            f"{_format_debug_value(condition.current_value)} "
            f"{condition.comparison} "
            f"{_format_debug_value(condition.threshold_value)} "
            f"{_format_debug_value(condition.passed)}"
        )
    failed_names = ", ".join(condition.name for condition in logic_explain.failed_conditions)
    lines.append(f"failed: {failed_names or '(none)'}")
    return "\n".join(lines)


def render_diagnostics(diagnostics, tail: int, full: bool = False) -> str:
    selected = diagnostics if full else diagnostics[-tail:]
    lines = ["logic transition diagnoses"]
    for diagnosis in selected:
        lines.append(
            f"time={_format_debug_value(diagnosis.time_s)} "
            f"logic={diagnosis.logic_name} "
            f"active={_format_debug_value(diagnosis.before_active)}->{_format_debug_value(diagnosis.after_active)} "
            f"rows={_format_debug_value(diagnosis.before_time_s)}->{_format_debug_value(diagnosis.after_time_s)}"
        )
        lines.append(f"  before_failed: {_format_condition_names(diagnosis.before_failed_conditions)}")
        lines.append(f"  after_failed: {_format_condition_names(diagnosis.after_failed_conditions)}")
        lines.append(f"  changed: {_format_condition_changes(diagnosis.changed_conditions)}")
        lines.append(f"  context: {_format_context_changes(diagnosis.context_changes)}")
    if len(lines) == 1:
        lines.append(" (no logic transitions)")
    return "\n".join(lines)


def render_json(result, view: str, logic_name: str | None = None, time_s: float | None = None) -> str:
    if view == "timeline":
        payload = {
            "schema": _schema_metadata(result.scenario_name, view),
            "scenario_name": result.scenario_name,
            "row_count": len(result.rows),
            "rows": [asdict(row) for row in result.rows],
        }
    elif view == "events":
        events = result.events()
        payload = {
            "schema": _schema_metadata(result.scenario_name, view),
            "scenario_name": result.scenario_name,
            "event_count": len(events),
            "events": [asdict(event) for event in events],
        }
    elif view == "explain":
        row = select_trace_row(result.rows, time_s)
        payload = {
            "schema": _schema_metadata(result.scenario_name, view),
            "scenario_name": result.scenario_name,
            "time_s": row.time_s,
            "logic": asdict(row.controller_explain.by_logic_name(logic_name or "")),
        }
    else:
        diagnostics = result.logic_transition_diagnostics(logic_name=logic_name)
        payload = {
            "schema": _schema_metadata(result.scenario_name, view),
            "scenario_name": result.scenario_name,
            "diagnostic_count": len(diagnostics),
            "diagnostics": [asdict(diagnosis) for diagnosis in diagnostics],
        }
    return json.dumps(payload, indent=2, sort_keys=True)


def _format_event_value(value) -> str:
    if isinstance(value, bool):
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def _schema_metadata(scenario_name: str, view: str) -> dict[str, str]:
    return {
        "name": JSON_SCHEMA_NAME,
        "scenario_name": scenario_name,
        "schema_version": JSON_SCHEMA_VERSION,
        "view": view,
    }


def _format_debug_value(value) -> str:
    if isinstance(value, bool):
        return str(int(value))
    if isinstance(value, float):
        text = f"{value:.3f}".rstrip("0").rstrip(".")
        return text or "0"
    if isinstance(value, tuple):
        return "(" + ", ".join(_format_debug_value(item) for item in value) + ")"
    return str(value)


def _format_condition_names(names) -> str:
    return ", ".join(names) if names else "(none)"


def _format_condition_changes(changes) -> str:
    if not changes:
        return "(none)"
    return ", ".join(
        (
            f"{change.name}:passed={_format_debug_value(change.before_passed)}->"
            f"{_format_debug_value(change.after_passed)} "
            f"current={_format_debug_value(change.before_current_value)}->"
            f"{_format_debug_value(change.after_current_value)} "
            f"threshold={_format_debug_value(change.threshold_value)}"
        )
        for change in changes
    )


def _format_context_changes(changes) -> str:
    if not changes:
        return "(none)"
    return ", ".join(
        (
            f"{change.field_group}.{change.field_name}:"
            f"{_format_debug_value(change.before_value)}->"
            f"{_format_debug_value(change.after_value)}"
        )
        for change in changes
    )


def select_trace_row(rows, time_s: float | None):
    if not rows:
        raise ValueError("Cannot select a trace row from an empty result")
    if time_s is None:
        return rows[-1]
    return min(rows, key=lambda row: abs(row.time_s - time_s))


def archive_manifest_validation_payload(
    manifest_path: str,
    *,
    require_existing_files: bool = True,
) -> dict:
    input_path = Path(manifest_path).expanduser()
    path = input_path / "archive_manifest.json" if input_path.is_dir() else input_path
    payload = {
        "input_path": str(input_path),
        "manifest_path": str(path),
        "valid": False,
        "issues": [],
    }
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        payload["issues"] = [f"could not read archive manifest: {exc}"]
        return payload
    except json.JSONDecodeError as exc:
        payload["issues"] = [f"archive manifest is not valid JSON: {exc.msg}"]
        return payload

    issues = validate_workbench_archive_manifest(
        manifest,
        manifest_path=path,
        require_existing_files=require_existing_files,
    )
    payload["valid"] = not issues
    payload["issues"] = list(issues)
    if not isinstance(manifest, dict):
        return payload
    try:
        resolved_files = resolve_workbench_archive_manifest_files(
            manifest,
            manifest_path=path,
        )
    except ValueError:
        resolved_files = {}

    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    bundle = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
    payload.update(
        {
            "kind": manifest.get("kind"),
            "version": manifest.get("version"),
            "schema": manifest.get("$schema"),
            "archive_dir": manifest.get("archive_dir"),
            "bundle": {
                "bundle_kind": bundle.get("bundle_kind"),
                "system_id": bundle.get("system_id"),
                "system_title": bundle.get("system_title"),
                "ready_for_spec_build": bundle.get("ready_for_spec_build"),
            },
            "files": files,
            "resolved_files": resolved_files,
            "file_count": len([file_path for file_path in files.values() if file_path is not None]),
            "restore_targets": manifest.get("restore_targets") if isinstance(manifest.get("restore_targets"), dict) else {},
            "self_check": manifest.get("self_check") if isinstance(manifest.get("self_check"), dict) else {},
        }
    )
    return payload


def render_archive_manifest_validation_text(payload: dict) -> str:
    status = "OK" if payload["valid"] else "INVALID"
    lines = [
        f"archive_manifest: {status}",
        f"path: {payload['manifest_path']}",
    ]
    if payload.get("kind") is not None:
        lines.append(f"kind: {payload['kind']}")
    if payload.get("version") is not None:
        lines.append(f"version: {payload['version']}")
    if payload.get("schema") is not None:
        lines.append(f"schema: {payload['schema']}")
    if payload.get("archive_dir") is not None:
        lines.append(f"archive_dir: {payload['archive_dir']}")
    bundle = payload.get("bundle")
    if isinstance(bundle, dict) and bundle:
        lines.append(f"bundle: {bundle.get('system_id')} / {bundle.get('bundle_kind')}")
    if payload.get("file_count") is not None:
        lines.append(f"file_count: {payload['file_count']}")
    restore_targets = payload.get("restore_targets")
    if isinstance(restore_targets, dict) and restore_targets:
        lines.append("restore_targets:")
        for target_name, target_path in sorted(restore_targets.items()):
            lines.append(f"- {target_name}: {target_path or '(none)'}")
    self_check = payload.get("self_check")
    if isinstance(self_check, dict) and self_check.get("command"):
        lines.append(f"self_check: {self_check['command']}")
    if payload["issues"]:
        lines.append("issues:")
        lines.extend(f"- {issue}" for issue in payload["issues"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        if args.view == "explain" and args.logic is None:
            parser.error("--logic is required with --view explain")
        scenario = BUILT_IN_SCENARIOS[args.scenario]()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))
        if args.format == "json":
            print(render_json(result, args.view, logic_name=args.logic, time_s=args.time))
        elif args.view == "explain":
            row = select_trace_row(result.rows, args.time)
            print(render_explain(row, args.logic))
        elif args.view == "diagnose":
            print(
                render_diagnostics(
                    result.logic_transition_diagnostics(logic_name=args.logic),
                    args.tail,
                    full=args.full,
                )
            )
        elif args.view == "events":
            print(render_events(result.events(), args.tail, full=args.full))
        else:
            print(render_rows(result.rows, args.tail, full=args.full))
        return 0
    if args.command == "demo":
        prompt = " ".join(args.prompt)
        answer = answer_demo_prompt(prompt)
        if args.format == "json":
            print(json.dumps(demo_answer_to_payload(answer), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_demo_answer(answer))
        return 0
    if args.command == "spec":
        print(json.dumps(workbench_spec_to_dict(current_reference_workbench_spec()), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "intake":
        if args.template:
            print(json.dumps(intake_template_payload(), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if not args.packet_path:
            parser.error("packet_path is required unless --template is set")
        packet = load_intake_packet(args.packet_path)
        report = build_clarification_brief(packet) if args.follow_up else assess_intake_packet(packet)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_clarification_brief_text(report) if args.follow_up else render_intake_assessment_text(report))
        return 0
    if args.command == "playback":
        packet = load_intake_packet(args.packet_path)
        report = assess_intake_packet(packet)
        if not report["ready_for_spec_build"]:
            if args.format == "json":
                print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(render_intake_assessment_text(report))
            return 1
        playback_report = build_playback_report_from_intake_packet(
            packet,
            scenario_id=args.scenario,
            sample_period_s=args.sample_period,
        )
        if args.format == "json":
            print(json.dumps(playback_report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_playback_report_text(playback_report))
        return 0
    if args.command == "diagnose-fault":
        packet = load_intake_packet(args.packet_path)
        report = assess_intake_packet(packet)
        if not report["ready_for_spec_build"]:
            if args.format == "json":
                print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(render_intake_assessment_text(report))
            return 1
        diagnosis_report = build_fault_diagnosis_report_from_intake_packet(
            packet,
            scenario_id=args.scenario,
            fault_mode_id=args.fault_mode,
            sample_period_s=args.sample_period,
        )
        if args.format == "json":
            print(json.dumps(diagnosis_report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_fault_diagnosis_text(diagnosis_report))
        return 0
    if args.command == "capture-knowledge":
        packet = load_intake_packet(args.packet_path)
        report = assess_intake_packet(packet)
        if not report["ready_for_spec_build"]:
            if args.format == "json":
                print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(render_intake_assessment_text(report))
            return 1
        artifact = build_knowledge_artifact(
            packet,
            scenario_id=args.scenario,
            fault_mode_id=args.fault_mode,
            observed_symptoms=args.observed_symptoms,
            evidence_links=tuple(args.evidence_link),
            confirmed_root_cause=args.confirmed_root_cause,
            repair_action=args.repair_action,
            validation_after_fix=args.validation_after_fix,
            residual_risk=args.residual_risk,
            suggested_logic_change=args.suggested_logic_change,
            reliability_gain_hypothesis=args.reliability_gain_hypothesis,
            redundancy_reduction_or_guardrail_note=args.guardrail_note,
            sample_period_s=args.sample_period,
        )
        if args.format == "json":
            print(json.dumps(artifact.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_knowledge_artifact_text(artifact))
        return 0
    if args.command == "bundle":
        packet = load_intake_packet(args.packet_path)
        try:
            bundle = build_workbench_bundle(
                packet,
                scenario_id=args.scenario,
                fault_mode_id=args.fault_mode,
                observed_symptoms=args.observed_symptoms,
                evidence_links=tuple(args.evidence_link),
                confirmed_root_cause=args.confirmed_root_cause,
                repair_action=args.repair_action,
                validation_after_fix=args.validation_after_fix,
                residual_risk=args.residual_risk,
                suggested_logic_change=args.suggested_logic_change,
                reliability_gain_hypothesis=args.reliability_gain_hypothesis,
                redundancy_reduction_or_guardrail_note=args.guardrail_note,
                sample_period_s=args.sample_period,
            )
        except ValueError as exc:
            parser.error(str(exc))
        archive = None
        if args.archive_dir:
            archive = archive_workbench_bundle(bundle, args.archive_dir)
        if args.format == "json":
            payload = bundle.to_dict()
            if archive is not None:
                payload["archive"] = archive.to_dict()
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            text = render_workbench_bundle_text(bundle)
            if archive is not None:
                text = "\n".join(
                    [
                        text,
                        f"archive_dir: {archive.archive_dir}",
                        f"archive_bundle_json: {archive.bundle_json_path}",
                        f"archive_summary_markdown: {archive.summary_markdown_path}",
                    ]
                )
            print(text)
        return 0 if bundle.ready_for_spec_build else 1
    if args.command == "archive-manifest":
        payload = archive_manifest_validation_payload(
            args.manifest_path,
            require_existing_files=not args.skip_file_check,
        )
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_archive_manifest_validation_text(payload))
        return 0 if payload["valid"] else 1
    if args.command == "second-system-smoke":
        report = build_second_system_smoke_report(
            packet_path=args.packet_path,
            scenario_id=args.scenario,
            fault_mode_id=args.fault_mode,
            sample_period_s=args.sample_period,
            proof_mode=args.proof_mode,
            adapter_id=args.adapter_id,
        )
        if args.format == "json":
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_second_system_smoke_text(report))
        return 0 if report.smoke_passed else 1
    if args.command == "two-system-runtime-comparison":
        report = build_two_system_runtime_comparison_report(sample_period_s=args.sample_period)
        if args.format == "json":
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_two_system_runtime_comparison_text(report))
        return 0 if report.both_reach_playback_completion and report.both_block_fault_path else 1
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
