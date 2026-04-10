from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from well_harness.demo import answer_demo_prompt, demo_answer_to_payload, render_demo_answer
from well_harness.document_intake import (
    assess_intake_packet,
    intake_template_payload,
    load_intake_packet,
    render_intake_assessment_text,
)
from well_harness.runner import SimulationRunner
from well_harness.scenarios import BUILT_IN_SCENARIOS
from well_harness.scenario_playback import build_playback_report_from_intake_packet, render_playback_report_text
from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict

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
        report = assess_intake_packet(packet)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_intake_assessment_text(report))
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
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
