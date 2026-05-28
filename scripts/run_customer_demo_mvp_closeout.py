#!/usr/bin/env python3
"""Run the Customer Demo MVP closeout gate."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-customer-demo-mvp-closeout")
CLOSEOUT_JSON_NAME = "customer_demo_mvp_closeout.json"
CLOSEOUT_MARKDOWN_NAME = "customer_demo_mvp_closeout.md"
CLOSEOUT_DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "customer-demo-mvp-closeout.md"
EXPECTED_DEMO_ROUTE = "/demo-reconstruction"
M21_C919_FANOUT_SCENARIO = "c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake"
M21_DEMO_FANOUT_SCENARIO = "fantui_demo_fanout_junction"
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Customer Demo MVP closeout from visibility and demo gates.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 360) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _command_pass(command: dict[str, Any]) -> bool:
    return command["returncode"] == 0 and command["payload"].get("status") == "pass"


def _git_diff_names(diff_args: list[str]) -> tuple[int, list[str]]:
    result = subprocess.run(
        ["git", "diff", "--name-only", *diff_args, "--", *RESTRICTED_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    paths = [line for line in result.stdout.splitlines() if line.strip()]
    return result.returncode, paths


def _current_pr_base_ref() -> str | None:
    try:
        result = subprocess.run(
            ["gh", "pr", "view", "--json", "baseRefName"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    base_ref = payload.get("baseRefName")
    return base_ref if isinstance(base_ref, str) and base_ref else None


def _pr_base_ref() -> str | None:
    for key in (
        "AI_FANTUI_CUSTOMER_DEMO_MVP_BASE_REF",
        "AI_FANTUI_PHASE1_DEMO_MVP_BASE_REF",
        "GITHUB_BASE_REF",
    ):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return _current_pr_base_ref()


def _base_ref_candidates(base_ref: str) -> list[str]:
    if base_ref.startswith("origin/"):
        return [base_ref]
    return [f"origin/{base_ref}", base_ref]


def _fetch_base_ref(base_ref: str) -> bool:
    remote_ref = base_ref.removeprefix("origin/")
    if not remote_ref or remote_ref.startswith("-") or any(char.isspace() for char in remote_ref):
        return False
    result = subprocess.run(
        ["git", "fetch", "--quiet", "origin", f"{remote_ref}:refs/remotes/origin/{remote_ref}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    return result.returncode == 0


def _restricted_paths_from_base_ref(base_ref: str) -> list[str] | None:
    for candidate in _base_ref_candidates(base_ref):
        returncode, paths = _git_diff_names([f"{candidate}...HEAD"])
        if returncode == 0:
            return paths
    return None


def _dedupe_paths(paths: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if path not in seen:
            unique.append(path)
            seen.add(path)
    return unique


def _restricted_diff() -> list[str]:
    restricted: list[str] = []
    base_ref = _pr_base_ref()
    if base_ref:
        base_paths = _restricted_paths_from_base_ref(base_ref)
        if base_paths is None and _fetch_base_ref(base_ref):
            base_paths = _restricted_paths_from_base_ref(base_ref)
        if base_paths is None:
            return ["<git base diff failed>"]
        restricted.extend(base_paths)

    for diff_args in ([], ["--cached"]):
        returncode, paths = _git_diff_names(diff_args)
        if returncode != 0:
            return ["<git diff failed>"]
        restricted.extend(paths)

    return _dedupe_paths(restricted)


def _closeout_doc_check() -> dict[str, Any]:
    if not CLOSEOUT_DOC_PATH.exists():
        return {
            "status": "fail",
            "path": str(CLOSEOUT_DOC_PATH),
            "mismatches": ["customer-demo-mvp-closeout.md is missing"],
        }
    text = CLOSEOUT_DOC_PATH.read_text(encoding="utf-8")
    markers = [
        "Customer Demo MVP Closeout",
        "make customer-demo-mvp-closeout",
        "make project-visibility-mvp-gate",
        "make phase1-demo-mvp-gate",
        "M21 Pure Canvas Evidence",
        "default-display: logic-circuit-only",
        "pure_canvas_presentation_contract",
        "M21 Natural Language Workbench Evidence",
        "natural_language_workbench_contract",
        "M21 Natural Language Step Confirmation Evidence",
        "natural_language_streamed_confirmation_contract",
        EXPECTED_DEMO_ROUTE,
        "ready_for_project_owner_acceptance",
    ]
    mismatches = [f"missing marker: {marker}" for marker in markers if marker not in text]
    return {
        "status": "pass" if not mismatches else "fail",
        "path": str(CLOSEOUT_DOC_PATH),
        "mismatches": mismatches,
    }


def _path_exists(path_value: Any) -> bool:
    return isinstance(path_value, str) and bool(path_value) and Path(path_value).exists()


def _screenshot_paths(payload: dict[str, Any]) -> list[str]:
    paths = payload.get("artifact_paths", {})
    screenshots = paths.get("screenshots", [])
    if isinstance(screenshots, list):
        return [str(path) for path in screenshots]
    return []


def _light_demo_screenshot(paths: list[str]) -> str:
    for path in paths:
        if "first-screen" in Path(path).name:
            return path
    return ""


def _m21_pure_canvas_gate_ok(command: dict[str, Any]) -> bool:
    payload = command.get("payload", {})
    gates = payload.get("deterministic_gates", {})
    observed = payload.get("observed", {})
    return (
        command.get("returncode") == 0
        and payload.get("status") == "pass"
        and gates.get("pure_canvas_presentation_contract") == "pass"
        and gates.get("pure_canvas_framing_contract") == "pass"
        and gates.get("circuit_only_default_display_contract") == "pass"
        and observed.get("canvas_default_display") == "logic-circuit-only"
        and observed.get("presentation_mode_for_screenshot") == "circuit-only"
        and observed.get("chain_wire_visible_label_count") == 0
        and observed.get("chain_node_desc_count") == 0
        and observed.get("chain_node_code_count") == 0
        and observed.get("chain_node_anchor_count") == 0
        and _path_exists(payload.get("artifact_paths", {}).get("screenshot", ""))
        and _path_exists(payload.get("artifact_paths", {}).get("summary", ""))
    )


def _m21_natural_language_workbench_gate_ok(command: dict[str, Any]) -> bool:
    payload = command.get("payload", {})
    gates = payload.get("deterministic_gates", {})
    observed = payload.get("observed", {})
    return (
        command.get("returncode") == 0
        and payload.get("status") == "pass"
        and gates.get("natural_language_workbench_contract") == "pass"
        and observed.get("natural_language_interaction_mode") == "natural-language"
        and observed.get("natural_language_input_model") == "natural-language"
        and observed.get("natural_language_input_visible") is True
        and int(observed.get("natural_language_visible_button_count", 999)) <= 3
        and observed.get("natural_language_command_trigger_display") == "none"
        and observed.get("natural_language_mode_dock_display") == "none"
        and observed.get("natural_language_bottom_run_display") == "none"
    )


def _m21_natural_language_step_confirmation_gate_ok(command: dict[str, Any]) -> bool:
    payload = command.get("payload", {})
    gates = payload.get("deterministic_gates", {})
    observed = payload.get("observed", {})
    return (
        command.get("returncode") == 0
        and payload.get("status") == "pass"
        and gates.get("natural_language_streamed_confirmation_contract") == "pass"
        and gates.get("one_candidate_per_natural_language_submit_contract") == "pass"
        and gates.get("natural_language_step_visual_framing_contract") == "pass"
        and gates.get("natural_language_step_confirmation_screenshot") == "pass"
        and gates.get("feedback_revision_frontstage_contract") == "pass"
        and gates.get("feedback_revision_confirmation_screenshot") == "pass"
        and observed.get("natural_language_streamed_launch_source") == "natural-language"
        and observed.get("natural_language_streamed_panel_visibility_after_submit") == "expanded"
        and observed.get("natural_language_streamed_source_highlight") == "active"
        and observed.get("natural_language_streamed_logic_highlight") == "active"
        and observed.get("natural_language_streamed_highlight_count", 0) > 0
        and observed.get("natural_language_streamed_replay_event_count") == 0
        and observed.get("natural_language_canvas_height_after_submit", 0) >= 420
        and observed.get("natural_language_active_target_visible_in_canvas") is True
        and observed.get("natural_language_active_target_hit_test_visible") is True
        and observed.get("feedback_revision_feedback_matches") is True
        and observed.get("feedback_revision_replay_event_count") == 1
        and observed.get("feedback_revision_active_target_hit_test_visible") is True
        and observed.get("natural_language_streamed_confirm_enabled") is True
        and _path_exists(
            payload.get("artifact_paths", {}).get("step_confirmation_screenshot", "")
        )
        and _path_exists(
            payload.get("artifact_paths", {}).get("revision_confirmation_screenshot", "")
        )
    )


def _m21_pure_canvas_entry(command: dict[str, Any]) -> dict[str, Any]:
    payload = command.get("payload", {})
    observed = payload.get("observed", {})
    paths = payload.get("artifact_paths", {})
    return {
        "scenario": payload.get("scenario", observed.get("scenario", "")),
        "status": payload.get("status", "fail"),
        "screenshot": paths.get("screenshot", ""),
        "gate_summary": paths.get("summary", ""),
        "canvas_default_display": observed.get("canvas_default_display", ""),
        "presentation_mode_for_screenshot": observed.get(
            "presentation_mode_for_screenshot",
            "",
        ),
        "pure_canvas_presentation_contract": payload.get("deterministic_gates", {}).get(
            "pure_canvas_presentation_contract",
            "fail",
        ),
        "pure_canvas_framing_contract": payload.get("deterministic_gates", {}).get(
            "pure_canvas_framing_contract",
            "fail",
        ),
        "wire_count": observed.get("chain_wire_count", 0),
        "junction_count": observed.get("chain_junction_count", 0),
        "visible_wire_label_count": observed.get("chain_wire_visible_label_count", 0),
        "visible_node_desc_count": observed.get("chain_node_desc_count", 0),
        "visible_node_code_count": observed.get("chain_node_code_count", 0),
        "visible_node_anchor_count": observed.get("chain_node_anchor_count", 0),
        "controller_truth_modified": payload.get("controller_truth_modified"),
        "requirements_document_modified": payload.get("requirements_document_modified"),
        "truth_effect": payload.get("truth_effect", ""),
    }


def _m21_natural_language_workbench_entry(command: dict[str, Any]) -> dict[str, Any]:
    payload = command.get("payload", {})
    observed = payload.get("observed", {})
    gates = payload.get("deterministic_gates", {})
    return {
        "scenario": payload.get("scenario", observed.get("scenario", "")),
        "status": payload.get("status", "fail"),
        "natural_language_workbench_contract": gates.get(
            "natural_language_workbench_contract",
            "fail",
        ),
        "interaction_mode": observed.get("natural_language_interaction_mode", ""),
        "input_model": observed.get("natural_language_input_model", ""),
        "visible_button_count": observed.get("natural_language_visible_button_count", 0),
        "input_visible": observed.get("natural_language_input_visible"),
        "command_trigger_display": observed.get(
            "natural_language_command_trigger_display",
            "",
        ),
        "mode_dock_display": observed.get("natural_language_mode_dock_display", ""),
        "bottom_run_display": observed.get("natural_language_bottom_run_display", ""),
    }


def _m21_natural_language_step_confirmation_entry(command: dict[str, Any]) -> dict[str, Any]:
    payload = command.get("payload", {})
    observed = payload.get("observed", {})
    gates = payload.get("deterministic_gates", {})
    paths = payload.get("artifact_paths", {})
    return {
        "scenario": payload.get("scenario", observed.get("scenario", "")),
        "status": payload.get("status", "fail"),
        "step_confirmation_screenshot": paths.get("step_confirmation_screenshot", ""),
        "revision_confirmation_screenshot": paths.get(
            "revision_confirmation_screenshot",
            "",
        ),
        "natural_language_streamed_confirmation_contract": gates.get(
            "natural_language_streamed_confirmation_contract",
            "fail",
        ),
        "one_candidate_per_natural_language_submit_contract": gates.get(
            "one_candidate_per_natural_language_submit_contract",
            "fail",
        ),
        "natural_language_step_visual_framing_contract": gates.get(
            "natural_language_step_visual_framing_contract",
            "fail",
        ),
        "natural_language_step_confirmation_screenshot": gates.get(
            "natural_language_step_confirmation_screenshot",
            "fail",
        ),
        "feedback_revision_frontstage_contract": gates.get(
            "feedback_revision_frontstage_contract",
            "fail",
        ),
        "feedback_revision_confirmation_screenshot": gates.get(
            "feedback_revision_confirmation_screenshot",
            "fail",
        ),
        "launch_source": observed.get("natural_language_streamed_launch_source", ""),
        "panel_visibility_after_submit": observed.get(
            "natural_language_streamed_panel_visibility_after_submit",
            "",
        ),
        "step_confirmation": observed.get(
            "natural_language_streamed_step_confirmation",
            "",
        ),
        "current_confirmation": observed.get(
            "natural_language_streamed_current_confirmation",
            "",
        ),
        "source_highlight": observed.get("natural_language_streamed_source_highlight", ""),
        "logic_highlight": observed.get("natural_language_streamed_logic_highlight", ""),
        "highlight_count": observed.get("natural_language_streamed_highlight_count", 0),
        "canvas_height_after_submit": observed.get(
            "natural_language_canvas_height_after_submit",
            0,
        ),
        "active_target_visible_in_canvas": observed.get(
            "natural_language_active_target_visible_in_canvas",
            False,
        ),
        "active_target_hit_test_visible": observed.get(
            "natural_language_active_target_hit_test_visible",
            False,
        ),
        "step_screenshot_clip": observed.get(
            "natural_language_step_screenshot_clip",
            {},
        ),
        "feedback_revision_matches": observed.get(
            "feedback_revision_feedback_matches",
            False,
        ),
        "feedback_revision_replay_event_count": observed.get(
            "feedback_revision_replay_event_count",
            -1,
        ),
        "feedback_revision_panel_flow": observed.get(
            "feedback_revision_panel_flow",
            "",
        ),
        "feedback_revision_active_target_hit_test_visible": observed.get(
            "feedback_revision_active_target_hit_test_visible",
            False,
        ),
        "feedback_revision_screenshot_clip": observed.get(
            "feedback_revision_screenshot_clip",
            {},
        ),
        "active_target_id": observed.get("natural_language_streamed_active_target_id", ""),
        "active_sequence_index": observed.get(
            "natural_language_streamed_active_sequence_index",
            "",
        ),
        "replay_event_count_before_confirmation": observed.get(
            "natural_language_streamed_replay_event_count",
            -1,
        ),
    }


def _m21_logic_circuit_presentation(
    c919_command: dict[str, Any],
    demo_command: dict[str, Any],
) -> dict[str, Any]:
    c919 = _m21_pure_canvas_entry(c919_command)
    demo = _m21_pure_canvas_entry(demo_command)
    return {
        "acceptance_standard": (
            "default-display: logic-circuit-only; pure_canvas_presentation_contract "
            "and pure_canvas_framing_contract must pass; node descriptions, source "
            "anchors, visible node IDs, and wire labels must not render by default."
        ),
        "c919_fanout": c919,
        "demo_fanout": demo,
        "screenshots": [
            path
            for path in (c919.get("screenshot", ""), demo.get("screenshot", ""))
            if path
        ],
        "gate_summaries": [
            path
            for path in (c919.get("gate_summary", ""), demo.get("gate_summary", ""))
            if path
        ],
    }


def _m21_natural_language_workbench(
    c919_command: dict[str, Any],
    demo_command: dict[str, Any],
) -> dict[str, Any]:
    return {
        "acceptance_standard": (
            "default workbench interaction model must be natural-language; visible "
            "buttons must be <= 3; command palette, mode dock, and bottom run strip "
            "must be hidden by default."
        ),
        "c919_fanout": _m21_natural_language_workbench_entry(c919_command),
        "demo_fanout": _m21_natural_language_workbench_entry(demo_command),
    }


def _m21_natural_language_step_confirmation(
    c919_command: dict[str, Any],
    demo_command: dict[str, Any],
) -> dict[str, Any]:
    return {
        "acceptance_standard": (
            "a natural-language prompt must open exactly one pending candidate, "
            "highlight the active graph object and source/logic context, and keep "
            "the replay empty until the engineer confirms or requests revision."
        ),
        "c919_fanout": _m21_natural_language_step_confirmation_entry(c919_command),
        "demo_fanout": _m21_natural_language_step_confirmation_entry(demo_command),
    }


def _collect_mismatches(
    *,
    gates: dict[str, str],
    project_visibility: dict[str, Any],
    phase1_gate: dict[str, Any],
    phase1_verification: dict[str, Any],
    closeout_doc: dict[str, Any],
) -> list[str]:
    mismatches = [
        f"{name}=fail"
        for name, value in gates.items()
        if name != "local_gate" and value != "pass"
    ]
    for name, payload in (
        ("project_visibility", project_visibility),
        ("phase1_gate", phase1_gate),
        ("phase1_verification", phase1_verification),
    ):
        for mismatch in payload.get("mismatches", []):
            mismatches.append(f"{name}.{mismatch}")
    for mismatch in closeout_doc.get("mismatches", []):
        mismatches.append(f"closeout_doc.{mismatch}")
    return mismatches


def _markdown_report(payload: dict[str, Any]) -> str:
    gates = "\n".join(
        f"- {name}: `{status}`"
        for name, status in payload["deterministic_gates"].items()
    )
    screenshots = "\n".join(
        f"- `{path}`" for path in payload["artifact_paths"]["screenshots"]
    )
    m21 = payload["m21_logic_circuit_presentation"]
    m21_lines = "\n".join(
        f"- {label}: screenshot `{entry['screenshot']}`, summary `{entry['gate_summary']}`, "
        f"presentation `{entry['presentation_mode_for_screenshot']}`, "
        f"default `{entry['canvas_default_display']}`"
        for label, entry in (
            ("C919 fan-out", m21["c919_fanout"]),
            ("Demo fan-out", m21["demo_fanout"]),
        )
    )
    natural_language = payload["m21_natural_language_workbench"]
    natural_language_lines = "\n".join(
        f"- {label}: `natural_language_workbench_contract={entry['natural_language_workbench_contract']}`, "
        f"visible buttons `{entry['visible_button_count']}`, input visible `{entry['input_visible']}`, "
        f"command palette `{entry['command_trigger_display']}`"
        for label, entry in (
            ("C919 fan-out", natural_language["c919_fanout"]),
            ("Demo fan-out", natural_language["demo_fanout"]),
        )
    )
    step_confirmation = payload["m21_natural_language_step_confirmation"]
    step_confirmation_lines = "\n".join(
        f"- {label}: `natural_language_streamed_confirmation_contract={entry['natural_language_streamed_confirmation_contract']}`, "
        f"`one_candidate_per_natural_language_submit_contract={entry['one_candidate_per_natural_language_submit_contract']}`, "
        f"`natural_language_step_visual_framing_contract={entry['natural_language_step_visual_framing_contract']}`, "
        f"`feedback_revision_frontstage_contract={entry['feedback_revision_frontstage_contract']}`, "
        f"highlight count `{entry['highlight_count']}`, canvas height `{entry['canvas_height_after_submit']}`, "
        f"step screenshot `{entry['step_confirmation_screenshot']}`, "
        f"revision screenshot `{entry['revision_confirmation_screenshot']}`"
        for label, entry in (
            ("C919 fan-out", step_confirmation["c919_fanout"]),
            ("Demo fan-out", step_confirmation["demo_fanout"]),
        )
    )
    return (
        "# Customer Demo MVP Closeout\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Closeout status: `{payload['closeout_status']}`\n\n"
        "## Claim\n\n"
        f"{payload['claim']}\n\n"
        "## Demo Surface\n\n"
        f"- Route: `{payload['demo_surface']['route']}`\n"
        f"- Nodes: `{payload['demo_surface']['node_count']}`\n"
        f"- Wires: `{payload['demo_surface']['wire_count']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Screenshot Evidence\n\n"
        f"{screenshots}\n\n"
        "## Embedded Demo Light Evidence\n\n"
        f"- embedded_codex_light_palette: `{payload['visual_evidence']['embedded_codex_light_palette']}`\n"
        f"- First screen: `{payload['visual_evidence']['light_demo_first_screen']}`\n\n"
        "## M21 Pure Canvas Evidence\n\n"
        f"- Acceptance standard: {m21['acceptance_standard']}\n"
        f"{m21_lines}\n\n"
        "## M21 Natural Language Workbench Evidence\n\n"
        f"- Acceptance standard: {natural_language['acceptance_standard']}\n"
        f"{natural_language_lines}\n\n"
        "## M21 Natural Language Step Confirmation Evidence\n\n"
        f"- Acceptance standard: {step_confirmation['acceptance_standard']}\n"
        f"{step_confirmation_lines}\n\n"
        "## Next Decision\n\n"
        f"{payload['recommended_next_step']}\n"
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def run_customer_demo_mvp_closeout(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    closeout_json_path = artifact_dir / CLOSEOUT_JSON_NAME
    closeout_markdown_path = artifact_dir / CLOSEOUT_MARKDOWN_NAME

    project_visibility_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_project_visibility_mvp_acceptance.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "project-visibility-mvp-acceptance"),
        ],
        timeout=360,
    )
    phase1_gate_dir = artifact_dir / "phase1-demo-mvp-gate"
    phase1_gate_command = _run_json_command(
        [
            sys.executable,
            "scripts/run_phase1_demo_mvp_gate.py",
            "--format",
            "json",
            "--artifact-dir",
            str(phase1_gate_dir),
        ],
        timeout=360,
    )
    phase1_gate_summary_path = phase1_gate_dir / "phase1_demo_mvp_gate_summary.json"
    phase1_verification_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_gate_summary.py",
            "--format",
            "json",
            "--summary",
            str(phase1_gate_summary_path),
        ],
        timeout=120,
    )
    m21_c919_pure_canvas_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_m21_streamed_authoring_revision_browser_gate.py",
            "--scenario",
            M21_C919_FANOUT_SCENARIO,
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "m21-c919-fanout-pure-canvas-gate"),
        ],
        timeout=480,
    )
    m21_demo_fanout_pure_canvas_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_m21_streamed_authoring_revision_browser_gate.py",
            "--scenario",
            M21_DEMO_FANOUT_SCENARIO,
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "m21-demo-fanout-pure-canvas-gate"),
        ],
        timeout=480,
    )
    closeout_doc = _closeout_doc_check()
    restricted = _restricted_diff()

    project_visibility = project_visibility_command["payload"]
    phase1_gate = phase1_gate_command["payload"]
    phase1_verification = phase1_verification_command["payload"]
    demo_surface = phase1_gate.get("demo_surface", {})
    project_visibility_screenshot = project_visibility.get("artifact_paths", {}).get(
        "screenshot_desktop",
        "",
    )
    phase1_screenshots = _screenshot_paths(phase1_gate)
    visual_evidence = phase1_gate.get("visual_evidence", {})
    light_demo_screenshot = _light_demo_screenshot(phase1_screenshots)
    m21_logic_circuit_presentation = _m21_logic_circuit_presentation(
        m21_c919_pure_canvas_command,
        m21_demo_fanout_pure_canvas_command,
    )
    m21_natural_language_workbench = _m21_natural_language_workbench(
        m21_c919_pure_canvas_command,
        m21_demo_fanout_pure_canvas_command,
    )
    m21_natural_language_step_confirmation = _m21_natural_language_step_confirmation(
        m21_c919_pure_canvas_command,
        m21_demo_fanout_pure_canvas_command,
    )
    m21_screenshots = [
        str(path)
        for path in m21_logic_circuit_presentation.get("screenshots", [])
        if isinstance(path, str) and path
    ]
    m21_step_screenshots = [
        str(path)
        for path in (
            m21_natural_language_step_confirmation["c919_fanout"].get(
                "step_confirmation_screenshot",
                "",
            ),
            m21_natural_language_step_confirmation["c919_fanout"].get(
                "revision_confirmation_screenshot",
                "",
            ),
            m21_natural_language_step_confirmation["demo_fanout"].get(
                "step_confirmation_screenshot",
                "",
            ),
            m21_natural_language_step_confirmation["demo_fanout"].get(
                "revision_confirmation_screenshot",
                "",
            ),
        )
        if isinstance(path, str) and path
    ]
    screenshots = [
        str(project_visibility_screenshot),
        *phase1_screenshots,
        *m21_step_screenshots,
        *m21_screenshots,
    ]
    screenshot_paths_valid = all(_path_exists(path) for path in screenshots)
    boundary_ok = (
        not restricted
        and project_visibility.get("review_boundaries", {}).get("controller_truth_modified") is False
        and project_visibility.get("review_boundaries", {}).get("ui_layout_modified") is False
        and phase1_gate.get("review_boundaries") == EXPECTED_REVIEW_BOUNDARIES
    )

    gates = {
        "project_visibility_mvp_gate": _gate_status(_command_pass(project_visibility_command)),
        "phase1_demo_mvp_gate": _gate_status(_command_pass(phase1_gate_command)),
        "phase1_gate_summary_verification": _gate_status(
            _command_pass(phase1_verification_command)
        ),
        "m21_c919_pure_canvas_gate": _gate_status(
            _m21_pure_canvas_gate_ok(m21_c919_pure_canvas_command)
        ),
        "m21_demo_fanout_pure_canvas_gate": _gate_status(
            _m21_pure_canvas_gate_ok(m21_demo_fanout_pure_canvas_command)
        ),
        "m21_pure_canvas_acceptance": _gate_status(
            _m21_pure_canvas_gate_ok(m21_c919_pure_canvas_command)
            and _m21_pure_canvas_gate_ok(m21_demo_fanout_pure_canvas_command)
        ),
        "m21_c919_natural_language_workbench_gate": _gate_status(
            _m21_natural_language_workbench_gate_ok(m21_c919_pure_canvas_command)
        ),
        "m21_demo_natural_language_workbench_gate": _gate_status(
            _m21_natural_language_workbench_gate_ok(m21_demo_fanout_pure_canvas_command)
        ),
        "m21_natural_language_workbench_acceptance": _gate_status(
            _m21_natural_language_workbench_gate_ok(m21_c919_pure_canvas_command)
            and _m21_natural_language_workbench_gate_ok(
                m21_demo_fanout_pure_canvas_command
            )
        ),
        "m21_c919_natural_language_step_confirmation_gate": _gate_status(
            _m21_natural_language_step_confirmation_gate_ok(
                m21_c919_pure_canvas_command
            )
        ),
        "m21_demo_natural_language_step_confirmation_gate": _gate_status(
            _m21_natural_language_step_confirmation_gate_ok(
                m21_demo_fanout_pure_canvas_command
            )
        ),
        "m21_natural_language_step_confirmation_acceptance": _gate_status(
            _m21_natural_language_step_confirmation_gate_ok(
                m21_c919_pure_canvas_command
            )
            and _m21_natural_language_step_confirmation_gate_ok(
                m21_demo_fanout_pure_canvas_command
            )
        ),
        "closeout_doc": closeout_doc["status"],
        "demo_surface": _gate_status(demo_surface.get("route") == EXPECTED_DEMO_ROUTE),
        "embedded_light_demo": _gate_status(
            visual_evidence.get("embedded_codex_light_palette") == "pass"
            and _path_exists(light_demo_screenshot)
        ),
        "screenshots": _gate_status(bool(screenshots) and screenshot_paths_valid),
        "boundary": _gate_status(boundary_ok),
        "local_gate": "fail",
    }
    mismatches = _collect_mismatches(
        gates=gates,
        project_visibility=project_visibility,
        phase1_gate=phase1_gate,
        phase1_verification=phase1_verification,
        closeout_doc=closeout_doc,
    )
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        and not mismatches
        else "fail"
    )
    gates["local_gate"] = status
    closeout_status = (
        "ready_for_project_owner_acceptance" if status == "pass" else "blocked"
    )

    payload = {
        "kind": "ai-fantui-customer-demo-mvp-closeout",
        "version": 1,
        "status": status,
        "closeout_status": closeout_status,
        "claim": (
            "The current /demo-reconstruction surface is ready for project-owner "
            "acceptance as the Customer Demo MVP candidate."
        ),
        "non_claims": [
            "no production readiness claim",
            "no certification or DAL readiness claim",
            "no controller truth promotion",
            "no external reviewer acceptance claim",
        ],
        "demo_surface": {
            "route": str(demo_surface.get("route", "")),
            "title": str(demo_surface.get("title", "")),
            "node_count": int(demo_surface.get("node_count", 0) or 0),
            "wire_count": int(demo_surface.get("wire_count", 0) or 0),
        },
        "entrypoints": {
            "project_visibility_gate": "make project-visibility-mvp-gate",
            "project_visibility_html": project_visibility.get("entrypoint", {}).get("html", ""),
            "phase1_demo_gate": "make phase1-demo-mvp-gate",
            "phase1_demo_route": EXPECTED_DEMO_ROUTE,
            "closeout_gate": "make customer-demo-mvp-closeout",
        },
        "deterministic_gates": gates,
        "checks": {
            "project_visibility": {
                "returncode": project_visibility_command["returncode"],
                "status": project_visibility.get("status", "fail"),
                "deterministic_gates": project_visibility.get("deterministic_gates", {}),
            },
            "phase1_demo_mvp_gate": {
                "returncode": phase1_gate_command["returncode"],
                "status": phase1_gate.get("status", "fail"),
                "deterministic_gates": phase1_gate.get("deterministic_gates", {}),
            },
            "phase1_gate_summary_verification": {
                "returncode": phase1_verification_command["returncode"],
                "status": phase1_verification.get("status", "fail"),
                "deterministic_gates": phase1_verification.get("deterministic_gates", {}),
            },
            "m21_c919_pure_canvas_gate": {
                "returncode": m21_c919_pure_canvas_command["returncode"],
                "status": m21_c919_pure_canvas_command["payload"].get("status", "fail"),
                "deterministic_gates": m21_c919_pure_canvas_command["payload"].get(
                    "deterministic_gates",
                    {},
                ),
            },
            "m21_demo_fanout_pure_canvas_gate": {
                "returncode": m21_demo_fanout_pure_canvas_command["returncode"],
                "status": m21_demo_fanout_pure_canvas_command["payload"].get(
                    "status",
                    "fail",
                ),
                "deterministic_gates": m21_demo_fanout_pure_canvas_command["payload"].get(
                    "deterministic_gates",
                    {},
                ),
            },
            "closeout_doc": closeout_doc,
        },
        "visual_evidence": {
            "embedded_codex_light_palette": visual_evidence.get(
                "embedded_codex_light_palette",
                "fail",
            ),
            "embedded_palette": visual_evidence.get("embedded_palette", {}),
            "light_demo_first_screen": light_demo_screenshot,
            "browser_acceptance_status": visual_evidence.get(
                "browser_acceptance_status",
                "fail",
            ),
            "m21_pure_canvas_acceptance": gates["m21_pure_canvas_acceptance"],
            "m21_natural_language_workbench_acceptance": gates[
                "m21_natural_language_workbench_acceptance"
            ],
            "m21_natural_language_step_confirmation_acceptance": gates[
                "m21_natural_language_step_confirmation_acceptance"
            ],
            "m21_logic_circuit_presentation": m21_logic_circuit_presentation,
            "m21_natural_language_workbench": m21_natural_language_workbench,
            "m21_natural_language_step_confirmation": (
                m21_natural_language_step_confirmation
            ),
        },
        "m21_logic_circuit_presentation": m21_logic_circuit_presentation,
        "m21_natural_language_workbench": m21_natural_language_workbench,
        "m21_natural_language_step_confirmation": (
            m21_natural_language_step_confirmation
        ),
        "artifact_paths": {
            "closeout_summary": str(closeout_json_path),
            "closeout_markdown": str(closeout_markdown_path),
            "closeout_doc": str(CLOSEOUT_DOC_PATH),
            "project_visibility_acceptance": project_visibility.get("artifact_paths", {}).get(
                "acceptance_summary",
                "",
            ),
            "project_visibility_html": project_visibility.get("entrypoint", {}).get("html", ""),
            "phase1_gate_summary": phase1_gate.get("artifact_paths", {}).get(
                "gate_summary",
                str(phase1_gate_summary_path),
            ),
            "phase1_release_summary": phase1_gate.get("artifact_paths", {}).get(
                "release_summary",
                "",
            ),
            "embedded_light_demo_screenshot": light_demo_screenshot,
            "browser_acceptance_json": phase1_gate.get("artifact_paths", {}).get(
                "browser_acceptance_json",
                "",
            ),
            "m21_logic_circuit_presentation": m21_logic_circuit_presentation,
            "screenshots": screenshots,
        },
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "mismatches": mismatches,
        "next_decision_options": [
            "accept the Customer Demo MVP candidate for project-owner review",
            "request external review before acceptance",
            "reject closeout and return to demo polish",
        ],
        "recommended_next_step": (
            "Request project-owner acceptance or external review before M21 queue expansion."
        ),
    }
    _write_text(closeout_markdown_path, _markdown_report(payload))
    if not closeout_markdown_path.exists() or closeout_markdown_path.stat().st_size == 0:
        payload["deterministic_gates"]["local_gate"] = "fail"
        payload["status"] = "fail"
        payload["closeout_status"] = "blocked"
        payload["mismatches"].append("closeout_markdown missing")
    _write_json(closeout_json_path, payload)
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: Customer Demo MVP closeout passed")
        print(f"closeout_status: {payload['closeout_status']}")
        print(f"summary: {payload['artifact_paths']['closeout_summary']}")
    else:
        print(f"FAIL: Customer Demo MVP closeout failed ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = run_customer_demo_mvp_closeout(artifact_dir=args.artifact_dir)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
