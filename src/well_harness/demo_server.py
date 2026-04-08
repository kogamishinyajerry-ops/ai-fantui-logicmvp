"""Small local UI server for the deterministic demo reasoning layer."""

from __future__ import annotations

import argparse
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
from well_harness.controller import DeployController
from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState


STATIC_DIR = Path(__file__).with_name("static")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}
LEVER_NUMERIC_INPUTS = {
    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
}
LEVER_BOOLEAN_INPUTS = {
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
}
LEVER_FEEDBACK_MODES = {
    "auto_scrubber",
    "manual_feedback_override",
}


class DemoRequestHandler(BaseHTTPRequestHandler):
    """Serve the static demo shell and a thin JSON API around DemoAnswer."""

    server_version = "WellHarnessDemo/1.0"

    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("", "/", "/demo.html"):
            self._serve_static("demo.html")
            return

        relative_path = unquote(parsed.path.lstrip("/"))
        if relative_path in {"demo.css", "demo.js"}:
            self._serve_static(relative_path)
            return

        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/demo", "/api/lever-snapshot"}:
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            request_payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(request_payload, dict):
            self._send_json(400, {"error": "invalid_json_object"})
            return

        if parsed.path == "/api/lever-snapshot":
            lever_inputs, error_payload = parse_lever_snapshot_request(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return

            self._send_json(200, lever_snapshot_payload(**lever_inputs))
            return

        prompt = str(request_payload.get("prompt", "")).strip()
        if not prompt:
            self._send_json(400, {"error": "missing_prompt"})
            return

        answer = answer_demo_prompt(prompt)
        self._send_json(200, demo_answer_to_payload(answer))

    def _serve_static(self, relative_path: str):
        static_root = STATIC_DIR.resolve()
        target_path = (static_root / relative_path).resolve()
        if target_path.parent != static_root or not target_path.is_file():
            self._send_json(404, {"error": "not_found"})
            return

        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
        self._send_bytes(200, target_path.read_bytes(), content_type)

    def _send_json(self, status_code: int, payload: dict):
        response = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self._send_bytes(status_code, response, "application/json; charset=utf-8")

    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def _clamp_tra(tra_deg: float, config: HarnessConfig) -> float:
    return max(config.reverse_travel_min_deg, min(config.reverse_travel_max_deg, tra_deg))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _parse_float_input(request_payload: dict, field_name: str, options: dict) -> tuple[float | None, dict | None]:
    raw_value = request_payload.get(field_name, options["default"])
    if isinstance(raw_value, bool):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    return _clamp(value, options["min"], options["max"]), None


def _parse_bool_input(request_payload: dict, field_name: str, default: bool) -> tuple[bool | None, dict | None]:
    raw_value = request_payload.get(field_name, default)
    if isinstance(raw_value, bool):
        return raw_value, None
    if isinstance(raw_value, str):
        normalized = raw_value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True, None
        if normalized in {"false", "0", "no", "off"}:
            return False, None
    return None, {
        "error": "invalid_lever_snapshot_input",
        "field": field_name,
        "message": f"{field_name} must be boolean.",
    }


def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
    if not isinstance(raw_value, str):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be a string.",
        }
    normalized = raw_value.strip()
    if normalized not in LEVER_FEEDBACK_MODES:
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
        }
    return normalized, None


def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
    lever_inputs = {}
    for field_name, options in LEVER_NUMERIC_INPUTS.items():
        value, error_payload = _parse_float_input(request_payload, field_name, options)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    config = HarnessConfig()
    lever_inputs["tra_deg"] = _clamp_tra(lever_inputs["tra_deg"], config)

    for field_name, default in LEVER_BOOLEAN_INPUTS.items():
        value, error_payload = _parse_bool_input(request_payload, field_name, default)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
    if error_payload is not None:
        return None, error_payload
    lever_inputs["feedback_mode"] = feedback_mode

    deploy_position_percent, error_payload = _parse_float_input(
        request_payload,
        "deploy_position_percent",
        {"default": 0.0, "min": 0.0, "max": 100.0},
    )
    if error_payload is not None:
        return None, error_payload
    lever_inputs["deploy_position_percent"] = deploy_position_percent
    return lever_inputs, None


def _canonical_pullback_sequence(tra_deg: float, config: HarnessConfig) -> list[float]:
    """Return a tiny canonical pullback path for the interactive UI scrubber."""
    target = _clamp_tra(tra_deg, config)
    if target >= 0.0:
        return [0.0]

    sequence: list[float] = []
    if target <= config.sw1_window.near_zero_deg:
        sequence.extend([-2.0] * 4)
    if target <= config.sw2_window.near_zero_deg:
        sequence.extend([-7.0] * 4)

    final_repeats = 4 if target <= config.logic3_tra_deg_threshold else 2
    sequence.extend([target] * final_repeats)
    return sequence


def _condition_payload(condition) -> dict:
    return {
        "name": condition.name,
        "current_value": condition.current_value,
        "comparison": condition.comparison,
        "threshold_value": condition.threshold_value,
        "passed": condition.passed,
    }


def _logic_payload(logic) -> dict:
    return {
        "logic_name": logic.logic_name,
        "active": logic.active,
        "failed_conditions": [condition.name for condition in logic.failed_conditions],
        "conditions": [_condition_payload(condition) for condition in logic.conditions],
    }


def _node(node_id: str, label: str, state: str, source: str, blocked_by: list[str] | None = None) -> dict:
    return {
        "id": node_id,
        "label": label,
        "state": state,
        "source": source,
        "blocked_by": blocked_by or [],
    }


def _logic_node_state(active: bool, completed: bool = False) -> str:
    return "active" if active or completed else "blocked"


def _lever_summary(
    tra_deg: float,
    inputs: ResolvedInputs,
    sensors,
    outputs,
    explain,
    feedback_mode: str,
) -> dict:
    if not inputs.sw1:
        return {
            "headline": f"TRA {tra_deg:.1f}°：拉杆还没进入 SW1 窗口，反推链路保持待命。",
            "blocker": "当前卡在 SW1：继续拉入 -1.4° 到 -6.2° 窗口会触发第一段链路。",
            "next_step": "下一步：把拉杆继续向反推方向拉到 SW1 window。",
        }
    if not outputs.logic1_active and not sensors.tls_unlocked_ls:
        failed = ", ".join(condition.name for condition in explain.logic1.failed_conditions)
        return {
            "headline": f"TRA {tra_deg:.1f}°：SW1 已触发，但 L1 / TLS115 尚未放行。",
            "blocker": f"当前卡在 L1：{failed or 'logic1 条件未完全满足'}。",
            "next_step": "下一步：恢复 RA / inhibited / EEC feedback 等 L1 条件，或回到默认演示条件。",
        }
    if not inputs.sw2:
        return {
            "headline": f"TRA {tra_deg:.1f}°：SW1 / L1 / TLS115 已点亮，正在建立 TLS 解锁反馈。",
            "blocker": "当前卡在 SW2：还没有进入 -5.0° 到 -9.8° 窗口。",
            "next_step": "下一步：继续拉到 SW2 window，点亮 L2 / 540V。",
        }
    if not outputs.logic2_active:
        failed = ", ".join(condition.name for condition in explain.logic2.failed_conditions)
        return {
            "headline": f"TRA {tra_deg:.1f}°：SW2 已触发，但 L2 / 540V 尚未放行。",
            "blocker": f"当前卡在 L2：{failed or 'logic2 条件未完全满足'}。",
            "next_step": "下一步：恢复 engine / ground / inhibited / EEC enable 等 L2 条件。",
        }
    if not outputs.logic3_active:
        failed = ", ".join(condition.name for condition in explain.logic3.failed_conditions)
        return {
            "headline": f"TRA {tra_deg:.1f}°：SW1、SW2 与 L2/540V 已点亮，L3 尚未放行。",
            "blocker": f"当前卡在 L3：{failed or 'logic3 条件未完全满足'}。",
            "next_step": "下一步：继续拉到 TRA <= -11.74°，并保持 N1K / TLS 等条件满足。",
        }
    if not outputs.logic4_active:
        failed = ", ".join(condition.name for condition in explain.logic4.failed_conditions)
        next_step = "下一步：在受控轨迹中继续保持反推，等 deploy_90_percent_vdt / VDT90 反馈出现。"
        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
            next_step = "下一步：把 deploy feedback override 推到 >= 90%，演示 VDT90 -> L4 -> THR_LOCK。"
        return {
            "headline": f"TRA {tra_deg:.1f}°：L3 已点亮，EEC / PLS / PDU 命令正在驱动受控演示轨迹。",
            "blocker": f"THR_LOCK 仍未释放：L4 还在等待 {failed or 'VDT90 / plant feedback'}。",
            "next_step": next_step,
        }
    if feedback_mode == "manual_feedback_override":
        return {
            "headline": f"TRA {tra_deg:.1f}°：manual feedback override 已把 VDT90 推到触发态，L4 / THR_LOCK 已点亮。",
            "blocker": "当前无 L4 blocker；这是 simplified plant feedback override 的诊断演示结果。",
            "next_step": "下一步：切回 auto scrubber，或降低 deploy feedback 观察 VDT90 / THR_LOCK 退回 blocked。",
        }
    return {
        "headline": f"TRA {tra_deg:.1f}°：L4 已满足，THR_LOCK release command 已触发。",
        "blocker": "当前无 L4 blocker。",
        "next_step": "下一步：查看证据或返回问答抽屉做诊断解释。",
    }


def lever_snapshot_payload(
    tra_deg: float,
    radio_altitude_ft: float = 5.0,
    engine_running: bool = True,
    aircraft_on_ground: bool = True,
    reverser_inhibited: bool = False,
    eec_enable: bool = True,
    n1k: float = 35.0,
    max_n1k_deploy_limit: float = 60.0,
    feedback_mode: str = "auto_scrubber",
    deploy_position_percent: float = 0.0,
) -> dict:
    config = HarnessConfig()
    controller = DeployController(config)
    switches = LatchedThrottleSwitches(config)
    plant = SimplifiedDeployPlant(config)
    switch_state = SwitchState(previous_tra_deg=0.0)
    plant_state = PlantState()
    target_tra = _clamp_tra(tra_deg, config)

    snapshot = None
    for tick, current_tra in enumerate(_canonical_pullback_sequence(target_tra, config)):
        switch_state = switches.update(switch_state, current_tra)
        sensors = plant_state.sensors(config)
        pilot_inputs = PilotInputs(
            radio_altitude_ft=radio_altitude_ft,
            tra_deg=current_tra,
            engine_running=engine_running,
            aircraft_on_ground=aircraft_on_ground,
            reverser_inhibited=reverser_inhibited,
            eec_enable=eec_enable,
            n1k=n1k,
            max_n1k_deploy_limit=max_n1k_deploy_limit,
        )
        resolved_inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        outputs, explain = controller.evaluate_with_explain(resolved_inputs)
        snapshot = (round(tick * config.step_s, 3), plant_state, sensors, pilot_inputs, resolved_inputs, outputs, explain)
        plant_state = plant.advance(plant_state, outputs, config.step_s)

    assert snapshot is not None
    time_s, plant_debug_state, sensors, pilot_inputs, inputs, outputs, explain = snapshot
    if feedback_mode == "manual_feedback_override":
        plant_debug_state = PlantState(
            tls_powered_s=plant_debug_state.tls_powered_s,
            pls_powered_s=plant_debug_state.pls_powered_s,
            tls_unlocked_ls=plant_debug_state.tls_unlocked_ls,
            pls_unlocked_ls=plant_debug_state.pls_unlocked_ls,
            deploy_position_percent=deploy_position_percent,
        )
        sensors = plant_debug_state.sensors(config)
        inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        outputs, explain = controller.evaluate_with_explain(inputs)
    logic1_completed = sensors.tls_unlocked_ls
    logic4_blockers = [condition.name for condition in explain.logic4.failed_conditions]
    logic3_blockers = [condition.name for condition in explain.logic3.failed_conditions]

    nodes = [
        _node("sw1", "SW1", "active" if inputs.sw1 else "inactive", "LatchedThrottleSwitches"),
        _node("logic1", "L1", _logic_node_state(outputs.logic1_active, logic1_completed), "DeployController.explain(logic1)", [condition.name for condition in explain.logic1.failed_conditions]),
        _node("tls115", "TLS115", "active" if outputs.tls_115vac_cmd or sensors.tls_unlocked_ls else "inactive", "DeployController outputs"),
        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
        _node("sw2", "SW2", "active" if inputs.sw2 else "inactive", "LatchedThrottleSwitches"),
        _node("logic2", "L2", _logic_node_state(outputs.logic2_active), "DeployController.explain(logic2)", [condition.name for condition in explain.logic2.failed_conditions]),
        _node("etrac_540v", "540V", "active" if outputs.etrac_540vdc_cmd else "inactive", "DeployController outputs"),
        _node("logic3", "L3", _logic_node_state(outputs.logic3_active), "DeployController.explain(logic3)", logic3_blockers),
        _node("eec_deploy", "EEC", "active" if outputs.eec_deploy_cmd else "inactive", "DeployController outputs"),
        _node("pls_power", "PLS", "active" if outputs.pls_power_cmd else "inactive", "DeployController outputs"),
        _node("pdu_motor", "PDU", "active" if outputs.pdu_motor_cmd else "inactive", "DeployController outputs"),
        _node("vdt90", "VDT90", "active" if sensors.deploy_90_percent_vdt else "inactive", "SimplifiedDeployPlant sensors"),
        _node("logic4", "L4", _logic_node_state(outputs.logic4_active), "DeployController.explain(logic4)", logic4_blockers),
        _node(
            "thr_lock",
            "THR_LOCK",
            "active"
            if outputs.throttle_electronic_lock_release_cmd
            else ("blocked" if (outputs.logic3_active or sensors.deploy_90_percent_vdt) else "inactive"),
            "DeployController outputs",
            logic4_blockers if not outputs.throttle_electronic_lock_release_cmd else [],
        ),
    ]
    summary = _lever_summary(target_tra, inputs, sensors, outputs, explain, feedback_mode)
    model_note = (
        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
        if feedback_mode == "auto_scrubber"
        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"
    )

    return {
        "mode": (
            "canonical_pullback_scrubber"
            if feedback_mode == "auto_scrubber"
            else "manual_feedback_override"
        ),
        "model_note": model_note,
        "input": {
            "tra_deg": target_tra,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "feedback_mode": feedback_mode,
            "deploy_position_percent": deploy_position_percent,
        },
        "time_s": time_s,
        "hud": {
            "tra_deg": target_tra,
            "sw1": inputs.sw1,
            "sw2": inputs.sw2,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "tls_unlocked_ls": sensors.tls_unlocked_ls,
            "pls_unlocked_ls": sensors.pls_unlocked_ls,
            "all_pls_unlocked_ls": sensors.all_pls_unlocked,
            "deploy_position_percent": sensors.deploy_position_percent,
            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt,
            "feedback_mode": feedback_mode,
        },
        "outputs": {
            "logic1_active": outputs.logic1_active,
            "logic2_active": outputs.logic2_active,
            "logic3_active": outputs.logic3_active,
            "logic4_active": outputs.logic4_active,
            "tls_115vac_cmd": outputs.tls_115vac_cmd,
            "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
            "eec_deploy_cmd": outputs.eec_deploy_cmd,
            "pls_power_cmd": outputs.pls_power_cmd,
            "pdu_motor_cmd": outputs.pdu_motor_cmd,
            "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
        },
        "logic": {
            "logic1": _logic_payload(explain.logic1),
            "logic2": _logic_payload(explain.logic2),
            "logic3": _logic_payload(explain.logic3),
            "logic4": _logic_payload(explain.logic4),
        },
        "plant_state": {
            "tls_powered_s": plant_debug_state.tls_powered_s,
            "pls_powered_s": plant_debug_state.pls_powered_s,
            "tls_unlocked_ls": plant_debug_state.tls_unlocked_ls,
            "pls_unlocked_ls": plant_debug_state.pls_unlocked_ls,
            "deploy_position_percent": plant_debug_state.deploy_position_percent,
        },
        "nodes": nodes,
        "summary": summary,
        "evidence": [
            "switches=LatchedThrottleSwitches.update(...)",
            "controller=DeployController.evaluate_with_explain(...)",
            "explain=DeployController.explain(...)",
            "plant=SimplifiedDeployPlant first-cut feedback model",
        ],
        "risks": [
            "PLS / VDT feedback comes from simplified first-cut plant timing.",
            "Manual feedback override is only a diagnostic demo control, not new control truth.",
            "THR_LOCK release must not be read as complete physical root-cause proof.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
    parser.add_argument(
        "--open",
        action="store_true",
        help=(
            "Open the local UI URL with Python's standard-library webbrowser.open; "
            "this is a launch convenience, not browser E2E automation."
        ),
    )
    return parser


def demo_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/"


def open_browser(url: str, opener=webbrowser.open) -> bool:
    try:
        opened = bool(opener(url))
    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
        return False
    if not opened:
        print(f"Could not open browser automatically. Open {url} manually.")
    return opened


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
    host, port = server.server_address
    url = demo_url(host, port)
    print(f"Serving well-harness demo UI at {url}")
    if args.open:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping well-harness demo UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
