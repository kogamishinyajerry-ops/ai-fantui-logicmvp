from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.tools.generate_adapter import spec_to_adapter_source

SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"
SPEC_PATH = PROJECT_ROOT / "src" / "well_harness" / "tools" / "specs" / "reference_thrust_reverser.spec.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate generator-adapter spec payloads."
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(SCHEMA_PATH),
        "spec_path": relative_path(SPEC_PATH),
        "status": status,
    }


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result: dict[str, Any] = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


# Key parity snapshots — same as test_generator_parity.py TC01/TC02/TC10
_PARITY_SNAPSHOTS: list[dict[str, Any]] = [
    {
        "name": "full_activation",
        "snap": {
            "radio_altitude_ft": 5.0,
            "tra_deg": -14.0,
            "sw1": True,
            "sw2": True,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 50.0,
            "max_n1k_deploy_limit": 60.0,
            "tls_unlocked_ls": True,
            "all_pls_unlocked_ls": True,
            "reverser_not_deployed_eec": True,
            "reverser_fully_deployed_eec": False,
            "deploy_position_percent": 95.0,
            "deploy_90_percent_vdt": True,
        },
        "expected_active": ("logic1", "logic2", "logic3", "logic4"),
        "expected_completion": True,
    },
    {
        "name": "altitude_gate_blocked",
        "snap": {
            "radio_altitude_ft": 6.0,
            "tra_deg": -14.0,
            "sw1": True,
            "sw2": True,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 50.0,
            "max_n1k_deploy_limit": 60.0,
            "tls_unlocked_ls": True,
            "all_pls_unlocked_ls": True,
            "reverser_not_deployed_eec": True,
            "reverser_fully_deployed_eec": False,
            "deploy_position_percent": 95.0,
            "deploy_90_percent_vdt": True,
        },
        "expected_active": ("logic2", "logic3", "logic4"),
        "expected_completion": True,
    },
    {
        "name": "sw1_off",
        "snap": {
            "radio_altitude_ft": 5.0,
            "tra_deg": -14.0,
            "sw1": False,
            "sw2": True,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 50.0,
            "max_n1k_deploy_limit": 60.0,
            "tls_unlocked_ls": True,
            "all_pls_unlocked_ls": True,
            "reverser_not_deployed_eec": True,
            "reverser_fully_deployed_eec": False,
            "deploy_position_percent": 95.0,
            "deploy_90_percent_vdt": True,
        },
        "expected_active": ("logic2", "logic3", "logic4"),
        "expected_completion": True,
    },
]


def validate_generator_adapter() -> tuple[int, dict, list[str]]:
    report = make_report()

    # ── Load spec ────────────────────────────────────────────────────────────
    try:
        spec_payload = load_json(SPEC_PATH)
    except Exception as exc:
        report["failure_kind"] = "spec_load"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL: unable to load spec from {relative_path(SPEC_PATH)}: {exc}"]

    report["results"].append(
        make_result("spec_load", "pass", spec_system_id=spec_payload.get("system_id"), spec_path=relative_path(SPEC_PATH))
    )

    # ── Schema validation ────────────────────────────────────────────────────
    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to load {relative_path(SCHEMA_PATH)}: {exc}"]

    validator = Draft202012Validator(schema)
    schema_errors = sorted(
        validator.iter_errors(spec_payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if schema_errors:
        formatted_errors = [format_validation_error(e) for e in schema_errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("spec_schema", "fail", error_count=len(schema_errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        return 1, report, [f"FAIL spec_schema:"] + [f"  - {e}" for e in formatted_errors]

    report["results"].append(
        make_result("spec_schema", "pass", error_count=0, errors=[], logic_node_count=len(spec_payload.get("logic_nodes", [])))
    )

    # ── Generate adapter from spec ──────────────────────────────────────────
    try:
        adapter_source = spec_to_adapter_source(spec_payload, source_path=relative_path(SPEC_PATH))
    except Exception as exc:
        report["failure_kind"] = "adapter_generation"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL adapter_generation: spec_to_adapter_source raised: {exc}"]

    report["results"].append(make_result("adapter_generation", "pass", source_length_chars=len(adapter_source)))

    # ── Instantiate generated adapter via exec ────────────────────────────────
    ns: dict = {}
    try:
        exec(adapter_source, ns)
    except Exception as exc:
        report["failure_kind"] = "adapter_compilation"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL adapter_compilation: exec raised: {exc}"]

    class_name = spec_payload["system_id"].replace("-", "_") + "_controller_adapter"
    if class_name not in ns:
        report["failure_kind"] = "adapter_class_missing"
        report["reason"] = f"generated class {class_name!r} not found in exec namespace"
        report["status"] = "fail"
        return 1, report, [f"FAIL adapter_class_missing: {class_name!r} not in ns"]

    GeneratedAdapterCls = ns[class_name]
    generated_adapter = GeneratedAdapterCls(spec_payload)

    # ── Reference adapter ────────────────────────────────────────────────────
    ref_adapter = build_reference_controller_adapter()

    # ── Parity checks ───────────────────────────────────────────────────────
    text_lines = [
        f"OK spec_load: loaded {spec_payload['system_id']}",
        f"OK spec_schema: passed jsonschema validation ({len(spec_payload.get('logic_nodes', []))} logic nodes)",
        f"OK adapter_generation: produced {len(adapter_source)} chars of Python",
        f"OK adapter_compilation: {class_name} instantiated",
    ]

    for case in _PARITY_SNAPSHOTS:
        snap = case["snap"]
        gen_eval = generated_adapter.evaluate_snapshot(snap)
        ref_eval = ref_adapter.evaluate_snapshot(snap)

        gen_active = tuple(gen_eval.active_logic_node_ids)
        ref_active = tuple(ref_eval.active_logic_node_ids)
        blocked_count_match = len(gen_eval.blocked_reasons) == len(ref_eval.blocked_reasons)

        parity_ok = (
            gen_active == ref_active
            and gen_eval.completion_reached == ref_eval.completion_reached
            and blocked_count_match
        )

        if not parity_ok:
            failure = (
                f"active mismatch: gen={gen_active} ref={ref_active}; "
                f"completion mismatch: gen={gen_eval.completion_reached} ref={ref_eval.completion_reached}; "
                f"blocked count: gen={len(gen_eval.blocked_reasons)} ref={len(ref_eval.blocked_reasons)}"
            )
            report["failure_kind"] = "parity_mismatch"
            report["results"].append(
                make_result(
                    f"parity:{case['name']}",
                    "fail",
                    error_count=1,
                    errors=[failure],
                    gen_active=list(gen_active),
                    ref_active=list(ref_active),
                    gen_completion=gen_eval.completion_reached,
                    ref_completion=ref_eval.completion_reached,
                )
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL parity:{case['name']}: {failure}"]

        report["results"].append(
            make_result(
                f"parity:{case['name']}",
                "pass",
                gen_active=list(gen_active),
                ref_active=list(ref_active),
                gen_completion=gen_eval.completion_reached,
                ref_completion=ref_eval.completion_reached,
                blocked_count=len(gen_eval.blocked_reasons),
            )
        )
        text_lines.append(
            f"OK parity:{case['name']}: "
            f"active={gen_active} completion={gen_eval.completion_reached}"
        )

    text_lines.append("PASS: generated adapter parity with reference controller")
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_generator_adapter.py [--format text|json]")


def emit_report(report: dict, text_lines: list[str], output_format: str) -> None:
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

    exit_code, report, text_lines = validate_generator_adapter()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
