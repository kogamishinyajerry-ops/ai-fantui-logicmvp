from __future__ import annotations

import http.client
import json
import sys
import threading
from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.demo_server import DemoRequestHandler
from well_harness.models import HarnessConfig


OUTPUT_FORMATS = {"text", "json"}


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    status: str
    http_status: int
    details: str


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: demo_path_smoke.py [--format text|json]")


def start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def request_json(port: int, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(
            "POST",
            path,
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    return response.status, json.loads(body)


def pass_result(name: str, http_status: int, details: str) -> ScenarioResult:
    return ScenarioResult(name=name, status="pass", http_status=http_status, details=details)


def fail_result(name: str, http_status: int, details: str) -> ScenarioResult:
    return ScenarioResult(name=name, status="fail", http_status=http_status, details=details)


def scenario_demo_bridge_prompt(port: int) -> ScenarioResult:
    status, payload = request_json(port, "/api/demo", {"prompt": "logic4 和 throttle lock 有什么关系"})
    if status != 200:
        return fail_result("demo_bridge_prompt", status, f"expected HTTP 200 but got {status}")
    if payload.get("intent") != "logic4_thr_lock_bridge":
        return fail_result("demo_bridge_prompt", status, f"expected intent logic4_thr_lock_bridge but got {payload.get('intent')}")
    if payload.get("matched_node") != "logic4->thr_lock":
        return fail_result("demo_bridge_prompt", status, f"expected matched_node logic4->thr_lock but got {payload.get('matched_node')}")
    return pass_result(
        "demo_bridge_prompt",
        status,
        "demo prompt path returned the bridge intent and logic4->thr_lock association through POST /api/demo.",
    )


def scenario_lever_extreme_clamp(port: int) -> ScenarioResult:
    config = HarnessConfig()
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": "-999",
            "radio_altitude_ft": "-5",
            "n1k": "-10",
            "max_n1k_deploy_limit": "999",
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": "999",
            "engine_running": "true",
            "aircraft_on_ground": "1",
            "reverser_inhibited": "false",
            "eec_enable": "on",
        },
    )
    if status != 200:
        return fail_result("lever_extreme_clamp", status, f"expected HTTP 200 but got {status}")

    expected_checks = (
        (payload["input"]["requested_tra_deg"] == config.reverse_travel_min_deg, "requested_tra_deg should clamp to reverse_travel_min_deg"),
        (payload["input"]["tra_deg"] == config.reverse_travel_min_deg, "effective tra_deg should stay at reverse_travel_min_deg once the lock boundary is open"),
        (payload["input"]["radio_altitude_ft"] == 0.0, "radio_altitude_ft should clamp to 0.0"),
        (payload["input"]["n1k"] == 0.0, "n1k should clamp to 0.0"),
        (payload["input"]["max_n1k_deploy_limit"] == 120.0, "max_n1k_deploy_limit should clamp to 120.0"),
        (payload["input"]["deploy_position_percent"] == 100.0, "deploy_position_percent should clamp to 100.0"),
        (payload["input"]["engine_running"] is True, "engine_running should coerce from string true"),
        (payload["input"]["aircraft_on_ground"] is True, "aircraft_on_ground should coerce from string 1"),
        (payload["input"]["reverser_inhibited"] is False, "reverser_inhibited should coerce from string false"),
        (payload["input"]["eec_enable"] is True, "eec_enable should coerce from string on"),
        (payload["mode"] == "manual_feedback_override", "mode should stay on manual_feedback_override"),
        (payload["hud"]["deploy_90_percent_vdt"] is True, "manual override at 100 should activate VDT90"),
        (payload["tra_lock"]["locked"] is False, "the deep range should be open once the -14° lock boundary satisfies L4"),
        (payload["outputs"]["logic3_active"] is True, "logic3 should remain active after the clamped edge-case request"),
        ("tra_deg" in payload["logic"]["logic4"]["failed_conditions"], "logic4 should still expose the deep-angle tra_deg blocker at -32.0°"),
    )
    for passed, message in expected_checks:
        if not passed:
            return fail_result("lever_extreme_clamp", status, message)

    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
    if node_states.get("thr_lock") != "blocked":
        return fail_result("lever_extreme_clamp", status, "THR_LOCK should stay in a controlled blocked state once the deep range is open but logic4 falls back on tra_deg")

    return pass_result(
        "lever_extreme_clamp",
        status,
        "lever snapshot clamps extreme numeric inputs, coerces boolean-like strings, and keeps the full -32°..0° slider open once the -14° L4 lock boundary is satisfied, even if THR_LOCK later falls back to a controlled blocked state at -32°.",
    )


def scenario_lever_mode_switch_reset(port: int) -> ScenarioResult:
    auto_before_status, auto_before = request_json(port, "/api/lever-snapshot", {"tra_deg": -14.0})
    manual_status, manual = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 95.0,
        },
    )
    auto_after_status, auto_after = request_json(port, "/api/lever-snapshot", {"tra_deg": -14.0})

    if auto_before_status != 200 or manual_status != 200 or auto_after_status != 200:
        return fail_result(
            "lever_mode_switch_reset",
            max(auto_before_status, manual_status, auto_after_status),
            "all three mode-switch smoke requests must return HTTP 200",
        )

    expected_checks = (
        (auto_before["mode"] == "canonical_pullback_scrubber", "auto_before should use canonical_pullback_scrubber"),
        (auto_before["outputs"]["logic4_active"] is False, "auto_before should keep logic4 blocked"),
        (manual["mode"] == "manual_feedback_override", "manual request should switch into manual feedback override"),
        (manual["outputs"]["logic4_active"] is True, "manual override 95 should activate logic4"),
        (auto_after["mode"] == "canonical_pullback_scrubber", "auto_after should return to canonical_pullback_scrubber"),
        (auto_after["outputs"]["logic4_active"] is False, "auto_after should drop logic4 back to blocked"),
        (auto_after["input"]["deploy_position_percent"] == 0.0, "auto_after should not retain stale manual deploy_position_percent"),
        (auto_after["hud"]["deploy_90_percent_vdt"] is False, "auto_after should not retain stale VDT90 state"),
    )
    for passed, message in expected_checks:
        if not passed:
            return fail_result("lever_mode_switch_reset", auto_after_status, message)

    return pass_result(
        "lever_mode_switch_reset",
        auto_after_status,
        "auto -> manual override -> auto sequence does not retain stale manual feedback state across requests.",
    )


def scenario_lever_l4_lock_gate(port: int) -> ScenarioResult:
    prelock_status, prelock = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": 0.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 95.0,
        },
    )
    locked_status, locked = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 95.0,
        },
    )
    unlocked_status, unlocked = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -20.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 95.0,
        },
    )

    if prelock_status != 200 or locked_status != 200 or unlocked_status != 200:
        return fail_result(
            "lever_l4_lock_gate",
            max(prelock_status, locked_status, unlocked_status),
            "all three lock-gate requests must return HTTP 200",
        )

    checks = (
        (prelock["input"]["tra_deg"] == 0.0, "prelock snapshot should preserve the shallow TRA position"),
        (prelock["tra_lock"]["boundary_unlock_ready"] is True, "prelock snapshot should detect that the lock boundary could unlock"),
        (prelock["tra_lock"]["locked"] is False, "prelock snapshot should expose the full range once the -14° lock boundary is satisfied"),
        (prelock["tra_lock"]["visual_reverse_min_deg"] == -32.0, "prelock snapshot should keep the full visual slider range"),
        (prelock["tra_lock"]["allowed_reverse_min_deg"] == -32.0, "prelock snapshot should expose the full drag range when the lock boundary is satisfied"),
        (locked["input"]["tra_deg"] == -14.0, "lock-boundary snapshot should reach -14.0"),
        (locked["tra_lock"]["locked"] is False, "lock-boundary snapshot should unlock once logic4 is truly active"),
        (locked["tra_lock"]["unlock_ready"] is True, "lock-boundary snapshot should report unlock_ready=True"),
        (locked["outputs"]["logic4_active"] is True, "lock-boundary snapshot should activate logic4"),
        (unlocked["input"]["tra_deg"] == -20.0, "unlocked snapshot should allow deeper reverse travel"),
        (unlocked["tra_lock"]["locked"] is False, "unlocked snapshot should report locked=False"),
        (unlocked["tra_lock"]["clamped"] is False, "unlocked snapshot should report clamped=False"),
        (unlocked["tra_lock"]["visual_reverse_min_deg"] == -32.0, "unlocked snapshot should preserve the full visual slider range"),
        (unlocked["outputs"]["logic4_active"] is True, "unlocked snapshot should keep logic4 active after the gate is satisfied"),
    )
    for passed, message in checks:
        if not passed:
            return fail_result("lever_l4_lock_gate", unlocked_status, message)

    return pass_result(
        "lever_l4_lock_gate",
        unlocked_status,
        "TRA now keeps the visual slider range at -32°..0°, while the -32°..-14° deep-reverse band opens only when the -14° lock boundary satisfies L4; otherwise requests are clamped back to -14°.",
    )


def scenario_preset_l3_waiting_vdt90(port: int) -> ScenarioResult:
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 0.0,
        },
    )
    if status != 200:
        return fail_result("preset_l3_waiting_vdt90", status, f"expected HTTP 200 but got {status}")

    checks = (
        (payload["mode"] == "manual_feedback_override", "preset should stay in manual_feedback_override"),
        (payload["outputs"]["logic3_active"] is True, "L3 waiting preset should keep logic3 active"),
        (payload["outputs"]["logic4_active"] is False, "L3 waiting preset should keep logic4 blocked"),
        (payload["hud"]["deploy_90_percent_vdt"] is False, "L3 waiting preset should keep VDT90 false"),
        ("deploy_90_percent_vdt" in payload["logic"]["logic4"]["failed_conditions"], "logic4 should explicitly wait on deploy_90_percent_vdt"),
        ("THR_LOCK 仍未释放" in payload["summary"]["blocker"], "summary blocker should describe the THR_LOCK wait state"),
    )
    for passed, message in checks:
        if not passed:
            return fail_result("preset_l3_waiting_vdt90", status, message)

    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
    if node_states.get("logic3") != "active" or node_states.get("thr_lock") != "blocked":
        return fail_result("preset_l3_waiting_vdt90", status, "preset should show active logic3 with blocked THR_LOCK")

    return pass_result(
        "preset_l3_waiting_vdt90",
        status,
        "visible preset L3 等待 VDT90 keeps L3 active while explicitly blocking L4 / THR_LOCK on deploy_90_percent_vdt.",
    )


def scenario_preset_ra_blocker(port: int) -> ScenarioResult:
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "radio_altitude_ft": 6.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 0.0,
        },
    )
    if status != 200:
        return fail_result("preset_ra_blocker", status, f"expected HTTP 200 but got {status}")

    checks = (
        (payload["mode"] == "manual_feedback_override", "RA blocker preset should stay in manual_feedback_override"),
        ("radio_altitude_ft" in payload["logic"]["logic1"]["failed_conditions"], "logic1 should surface radio_altitude_ft as the blocker"),
        ("当前卡在 L1" in payload["summary"]["blocker"], "summary blocker should describe the L1 wait state"),
        (payload["outputs"]["logic4_active"] is False, "RA blocker preset should keep logic4 inactive"),
    )
    for passed, message in checks:
        if not passed:
            return fail_result("preset_ra_blocker", status, message)

    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
    if node_states.get("logic1") != "blocked":
        return fail_result("preset_ra_blocker", status, "RA blocker preset should keep logic1 blocked")

    return pass_result(
        "preset_ra_blocker",
        status,
        "visible preset RA blocker keeps the chain blocked on logic1 with radio_altitude_ft called out in the summary and explain payload.",
    )


def scenario_preset_n1k_blocker(port: int) -> ScenarioResult:
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "n1k": 60.0,
            "max_n1k_deploy_limit": 60.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 0.0,
        },
    )
    if status != 200:
        return fail_result("preset_n1k_blocker", status, f"expected HTTP 200 but got {status}")

    checks = (
        (payload["mode"] == "manual_feedback_override", "N1K blocker preset should stay in manual_feedback_override"),
        ("n1k" in payload["logic"]["logic3"]["failed_conditions"], "logic3 should surface n1k as the blocker"),
        ("当前卡在 L3" in payload["summary"]["blocker"], "summary blocker should describe the L3 wait state"),
        (payload["outputs"]["logic4_active"] is False, "N1K blocker preset should keep logic4 inactive"),
    )
    for passed, message in checks:
        if not passed:
            return fail_result("preset_n1k_blocker", status, message)

    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
    if node_states.get("logic3") != "blocked":
        return fail_result("preset_n1k_blocker", status, "N1K blocker preset should keep logic3 blocked")

    return pass_result(
        "preset_n1k_blocker",
        status,
        "visible preset N1K blocker keeps the chain blocked on logic3 with n1k called out in the summary and explain payload.",
    )


def scenario_preset_vdt90_ready(port: int) -> ScenarioResult:
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {
            "tra_deg": -14.0,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 95.0,
        },
    )
    if status != 200:
        return fail_result("preset_vdt90_ready", status, f"expected HTTP 200 but got {status}")

    checks = (
        (payload["mode"] == "manual_feedback_override", "VDT90 ready preset should stay in manual_feedback_override"),
        (payload["hud"]["deploy_90_percent_vdt"] is True, "VDT90 ready preset should activate VDT90"),
        (payload["outputs"]["logic4_active"] is True, "VDT90 ready preset should activate logic4"),
        (payload["outputs"]["throttle_electronic_lock_release_cmd"] is True, "VDT90 ready preset should activate THR_LOCK release"),
        ("L4 / THR_LOCK 已点亮" in payload["summary"]["headline"], "summary headline should describe the ready state"),
        ("当前无 L4 blocker" in payload["summary"]["blocker"], "summary blocker should explain the no-blocker ready state"),
    )
    for passed, message in checks:
        if not passed:
            return fail_result("preset_vdt90_ready", status, message)

    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
    if node_states.get("logic4") != "active" or node_states.get("thr_lock") != "active":
        return fail_result("preset_vdt90_ready", status, "VDT90 ready preset should light both logic4 and THR_LOCK")

    return pass_result(
        "preset_vdt90_ready",
        status,
        "visible preset VDT90 ready drives the ready-state summary and activates L4 / THR_LOCK through the existing manual override path.",
    )


def scenario_condition_toggle_sweep(port: int) -> ScenarioResult:
    cases = (
        (
            "engine_running",
            {"tra_deg": -14.0, "engine_running": False, "feedback_mode": "manual_feedback_override", "deploy_position_percent": 0.0},
            "logic2",
            "engine_running",
            "当前卡在 L2",
        ),
        (
            "aircraft_on_ground",
            {"tra_deg": -14.0, "aircraft_on_ground": False, "feedback_mode": "manual_feedback_override", "deploy_position_percent": 0.0},
            "logic2",
            "aircraft_on_ground",
            "当前卡在 L2",
        ),
        (
            "reverser_inhibited",
            {"tra_deg": -14.0, "reverser_inhibited": True, "feedback_mode": "manual_feedback_override", "deploy_position_percent": 0.0},
            "logic1",
            "reverser_inhibited",
            "当前卡在 L1",
        ),
        (
            "eec_enable",
            {"tra_deg": -14.0, "eec_enable": False, "feedback_mode": "manual_feedback_override", "deploy_position_percent": 0.0},
            "logic2",
            "eec_enable",
            "当前卡在 L2",
        ),
    )

    for toggle_name, request_payload, blocked_logic, expected_failed, blocker_prefix in cases:
        status, payload = request_json(port, "/api/lever-snapshot", request_payload)
        if status != 200:
            return fail_result("condition_toggle_sweep", status, f"{toggle_name} expected HTTP 200 but got {status}")

        failed_conditions = payload["logic"][blocked_logic]["failed_conditions"]
        if expected_failed not in failed_conditions:
            return fail_result(
                "condition_toggle_sweep",
                status,
                f"{toggle_name} should surface {expected_failed} in {blocked_logic} failed_conditions",
            )
        if blocker_prefix not in payload["summary"]["blocker"]:
            return fail_result(
                "condition_toggle_sweep",
                status,
                f"{toggle_name} should keep the summary blocker aligned with {blocked_logic}",
            )

        node_states = {node["id"]: node["state"] for node in payload["nodes"]}
        if node_states.get(blocked_logic) != "blocked":
            return fail_result(
                "condition_toggle_sweep",
                status,
                f"{toggle_name} should keep {blocked_logic} blocked in the chain state snapshot",
            )

    return pass_result(
        "condition_toggle_sweep",
        200,
        "visible blocker toggles for engine, ground, reverser inhibit, and EEC enable all keep their expected blocker semantics through POST /api/lever-snapshot.",
    )


def scenario_invalid_feedback_mode(port: int) -> ScenarioResult:
    status, payload = request_json(
        port,
        "/api/lever-snapshot",
        {"tra_deg": -14.0, "feedback_mode": "bad_mode"},
    )
    if status != 400:
        return fail_result("invalid_feedback_mode", status, f"expected HTTP 400 but got {status}")
    if payload.get("error") != "invalid_lever_snapshot_input":
        return fail_result("invalid_feedback_mode", status, f"expected invalid_lever_snapshot_input but got {payload.get('error')}")
    if payload.get("field") != "feedback_mode":
        return fail_result("invalid_feedback_mode", status, f"expected field feedback_mode but got {payload.get('field')}")
    return pass_result(
        "invalid_feedback_mode",
        status,
        "invalid feedback_mode returns a controlled 400 error instead of silently drifting the demo path.",
    )


def run_smoke_suite() -> tuple[int, dict[str, Any], list[str]]:
    report: dict[str, Any] = {
        "status": "pass",
        "scenario_count": 10,
        "completed_scenarios": 0,
        "failed_scenario": None,
        "scenarios": [],
    }
    text_lines: list[str] = []

    server, thread = start_demo_server()
    try:
        scenarios = (
            scenario_demo_bridge_prompt,
            scenario_lever_extreme_clamp,
            scenario_lever_mode_switch_reset,
            scenario_lever_l4_lock_gate,
            scenario_preset_l3_waiting_vdt90,
            scenario_preset_ra_blocker,
            scenario_preset_n1k_blocker,
            scenario_preset_vdt90_ready,
            scenario_condition_toggle_sweep,
            scenario_invalid_feedback_mode,
        )
        for scenario in scenarios:
            result = scenario(server.server_port)
            report["scenarios"].append(
                {
                    "name": result.name,
                    "status": result.status,
                    "http_status": result.http_status,
                    "details": result.details,
                }
            )
            report["completed_scenarios"] += 1
            prefix = "OK" if result.status == "pass" else "FAIL"
            text_lines.append(f"{prefix} {result.name}: {result.details}")
            if result.status != "pass":
                report["status"] = "fail"
                report["failed_scenario"] = result.name
                return 1, report, text_lines
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    text_lines.append("PASS: validated 10 demo smoke scenarios through the local HTTP demo surface.")
    return 0, report, text_lines


def emit_report(report: dict[str, Any], text_lines: list[str], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for line in text_lines:
        print(line)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    exit_code, report, text_lines = run_smoke_suite()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
