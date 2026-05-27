#!/usr/bin/env python3
"""Build the final project-owner acceptance review packet."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-project-owner-acceptance-review-packet")
PACKET_JSON_NAME = "project_owner_acceptance_review_packet.json"
PACKET_MARKDOWN_NAME = "project_owner_acceptance_review_packet.md"
PACKET_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "project-owner-acceptance-review-packet.md"
)
EXPECTED_CLOSEOUT_STATUS = "ready_for_project_owner_acceptance"
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
        description="Generate the final project-owner acceptance review packet.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 480) -> dict[str, Any]:
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


def _restricted_diff() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *RESTRICTED_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ["<git diff failed>"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _packet_doc_check() -> dict[str, Any]:
    if not PACKET_DOC_PATH.exists():
        return {
            "status": "fail",
            "path": str(PACKET_DOC_PATH),
            "mismatches": ["project-owner-acceptance-review-packet.md is missing"],
        }
    text = PACKET_DOC_PATH.read_text(encoding="utf-8")
    markers = [
        "Project Owner Acceptance Review Packet",
        "make project-owner-acceptance-review-packet",
        EXPECTED_CLOSEOUT_STATUS,
        "Accept",
        "External review",
        "Demo polish",
        "M21 Pure Canvas Evidence",
        "pure_canvas_presentation_contract",
        "M21 Natural Language Workbench Evidence",
        "natural_language_workbench_contract",
        "M21 Natural Language Step Confirmation Evidence",
        "natural_language_streamed_confirmation_contract",
    ]
    mismatches = [f"missing marker: {marker}" for marker in markers if marker not in text]
    return {
        "status": "pass" if not mismatches else "fail",
        "path": str(PACKET_DOC_PATH),
        "mismatches": mismatches,
    }


def _load_json(path_value: str) -> dict[str, Any]:
    return json.loads(Path(path_value).read_text(encoding="utf-8"))


def _copy_file(src_value: Any, dst: Path) -> str:
    if not isinstance(src_value, str) or not src_value:
        return ""
    src = Path(src_value)
    if not src.exists() or not src.is_file():
        return ""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return str(dst)


def _copy_screenshots(paths: list[str], screenshot_dir: Path) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    for index, path_value in enumerate(paths, start=1):
        src = Path(path_value)
        if not src.exists() or not src.is_file():
            copied.append(
                {
                    "source": str(path_value),
                    "packet_path": "",
                    "role": "missing",
                }
            )
            continue
        role = _screenshot_role(src.name)
        dst = screenshot_dir / f"{index:02d}-{role}-{src.name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(
            {
                "source": str(src),
                "packet_path": str(dst),
                "role": role,
            }
        )
    return copied


def _screenshot_role(filename: str) -> str:
    if "feedback-revision" in filename and "c919_etras_mlg_wow_cmd2_cmd3_fanout" in filename:
        return "m21-c919-feedback-revision"
    if "feedback-revision" in filename and "fantui_demo_fanout_junction" in filename:
        return "m21-demo-feedback-revision"
    if "natural-language-step" in filename and "c919_etras_mlg_wow_cmd2_cmd3_fanout" in filename:
        return "m21-c919-natural-language-step"
    if "natural-language-step" in filename and "fantui_demo_fanout_junction" in filename:
        return "m21-demo-natural-language-step"
    if "c919_etras_mlg_wow_cmd2_cmd3_fanout" in filename:
        return "m21-c919-pure-canvas"
    if "fantui_demo_fanout_junction" in filename:
        return "m21-demo-fanout-pure-canvas"
    if "project-visibility" in filename:
        return "project-status"
    if "first-screen" in filename:
        return "demo-first-screen"
    if "chain-svg" in filename:
        return "demo-chain"
    if "max-reverse" in filename:
        return "demo-max-reverse"
    if "inhibit-block" in filename:
        return "demo-inhibit"
    return "screenshot"


def _copied_packet_path_for_source(
    copied_screenshots: list[dict[str, str]],
    source_path: str,
) -> str:
    if not source_path:
        return ""
    for item in copied_screenshots:
        if item.get("source") == source_path:
            return item.get("packet_path", "")
    return ""


def _path_exists(path_value: Any) -> bool:
    return isinstance(path_value, str) and bool(path_value) and Path(path_value).exists()


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _natural_language_entry_ok(entry: dict[str, Any]) -> bool:
    try:
        visible_button_count = int(entry.get("visible_button_count", 999))
    except (TypeError, ValueError):
        visible_button_count = 999
    return (
        entry.get("natural_language_workbench_contract") == "pass"
        and entry.get("interaction_mode") == "natural-language"
        and entry.get("input_model") == "natural-language"
        and entry.get("input_visible") is True
        and visible_button_count <= 3
        and entry.get("command_trigger_display") == "none"
        and entry.get("mode_dock_display") == "none"
        and entry.get("bottom_run_display") == "none"
    )


def _natural_language_step_entry_ok(entry: dict[str, Any]) -> bool:
    try:
        highlight_count = int(entry.get("highlight_count", 0))
    except (TypeError, ValueError):
        highlight_count = 0
    return (
        entry.get("natural_language_streamed_confirmation_contract") == "pass"
        and entry.get("one_candidate_per_natural_language_submit_contract") == "pass"
        and entry.get("natural_language_step_visual_framing_contract") == "pass"
        and entry.get("feedback_revision_frontstage_contract") == "pass"
        and entry.get("feedback_revision_confirmation_screenshot") == "pass"
        and entry.get("launch_source") == "natural-language"
        and entry.get("panel_visibility_after_submit") == "expanded"
        and entry.get("source_highlight") == "active"
        and entry.get("logic_highlight") == "active"
        and highlight_count > 0
        and entry.get("canvas_height_after_submit", 0) >= 420
        and entry.get("active_target_visible_in_canvas") is True
        and entry.get("active_target_hit_test_visible") is True
        and entry.get("feedback_revision_matches") is True
        and entry.get("feedback_revision_replay_event_count") == 1
        and entry.get("feedback_revision_active_target_hit_test_visible") is True
        and entry.get("replay_event_count_before_confirmation") == 0
        and _path_exists(entry.get("step_confirmation_screenshot", ""))
        and _path_exists(entry.get("revision_confirmation_screenshot", ""))
    )


def _decision_options() -> list[dict[str, str]]:
    return [
        {
            "id": "accept",
            "label": "接受",
            "decision": "accept_customer_demo_mvp_candidate",
            "meaning": "Accept the Customer Demo MVP candidate for project-owner review.",
        },
        {
            "id": "external_review",
            "label": "外部 review",
            "decision": "request_external_review_before_acceptance",
            "meaning": "Freeze this packet and request external review before acceptance.",
        },
        {
            "id": "demo_polish",
            "label": "返回 demo polish",
            "decision": "return_to_demo_polish",
            "meaning": "Reject closeout for now and return to demo polish.",
        },
    ]


def _collect_mismatches(gates: dict[str, str], packet_doc: dict[str, Any]) -> list[str]:
    mismatches = [
        f"{name}=fail"
        for name, value in gates.items()
        if name != "local_gate" and value != "pass"
    ]
    for mismatch in packet_doc.get("mismatches", []):
        mismatches.append(f"packet_doc.{mismatch}")
    return mismatches


def _markdown_packet(payload: dict[str, Any]) -> str:
    copied_screenshots = "\n".join(
        f"- {item['role']}: `{item['packet_path']}`"
        for item in payload["packet_contents"]["screenshots"]
    )
    decisions = "\n".join(
        f"{index}. {option['label']}: `{option['decision']}` - {option['meaning']}"
        for index, option in enumerate(payload["decision_options"], start=1)
    )
    non_claims = "\n".join(f"- {item}" for item in payload["non_claims"])
    gates = "\n".join(
        f"- {name}: `{status}`"
        for name, status in payload["deterministic_gates"].items()
    )
    m21 = payload["packet_contents"]["m21_pure_canvas_evidence"]
    m21_lines = "\n".join(
        f"- {label}: `{entry['packet_screenshot']}` "
        f"(source `{entry['screenshot']}`, summary `{entry['gate_summary']}`)"
        for label, entry in (
            ("C919 fan-out", m21["c919_fanout"]),
            ("Demo fan-out", m21["demo_fanout"]),
        )
    )
    natural_language = payload["packet_contents"][
        "m21_natural_language_workbench_evidence"
    ]
    natural_language_lines = "\n".join(
        f"- {label}: `natural_language_workbench_contract={entry['natural_language_workbench_contract']}`, "
        f"visible buttons `{entry['visible_button_count']}`, command palette `{entry['command_trigger_display']}`"
        for label, entry in (
            ("C919 fan-out", natural_language["c919_fanout"]),
            ("Demo fan-out", natural_language["demo_fanout"]),
        )
    )
    step_confirmation = payload["packet_contents"][
        "m21_natural_language_step_confirmation_evidence"
    ]
    step_confirmation_lines = "\n".join(
        f"- {label}: `natural_language_streamed_confirmation_contract={entry['natural_language_streamed_confirmation_contract']}`, "
        f"`one_candidate_per_natural_language_submit_contract={entry['one_candidate_per_natural_language_submit_contract']}`, "
        f"`natural_language_step_visual_framing_contract={entry['natural_language_step_visual_framing_contract']}`, "
        f"`feedback_revision_frontstage_contract={entry['feedback_revision_frontstage_contract']}`, "
        f"highlight count `{entry['highlight_count']}`, canvas height `{entry['canvas_height_after_submit']}`, "
        f"step screenshot `{entry['packet_screenshot']}`, "
        f"revision screenshot `{entry['packet_revision_screenshot']}`"
        for label, entry in (
            ("C919 fan-out", step_confirmation["c919_fanout"]),
            ("Demo fan-out", step_confirmation["demo_fanout"]),
        )
    )
    return (
        "# Project Owner Acceptance Review Packet\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Packet status: `{payload['packet_status']}`\n\n"
        "## Decision Required\n\n"
        f"{payload['decision_required']}\n\n"
        f"{decisions}\n\n"
        "## Closeout Summary\n\n"
        f"- Status: `{payload['source_closeout']['closeout_status']}`\n"
        f"- Demo route: `{payload['source_closeout']['demo_route']}`\n"
        f"- Demo surface: `{payload['source_closeout']['node_count']} nodes / "
        f"{payload['source_closeout']['wire_count']} wires`\n\n"
        "## Packet Contents\n\n"
        f"- Closeout JSON: `{payload['packet_contents']['closeout_json']}`\n"
        f"- Closeout Markdown: `{payload['packet_contents']['closeout_markdown']}`\n"
        f"- Project status HTML: `{payload['packet_contents']['project_status_html']}`\n"
        f"- Project status page source: `{payload['packet_contents']['project_status_source_html']}`\n\n"
        "## Logic Circuit Diagram\n\n"
        f"- Screenshot: `{payload['packet_contents']['logic_circuit_diagram']['screenshot']}`\n"
        f"- Nodes: `{payload['packet_contents']['logic_circuit_diagram']['node_count']}`\n"
        f"- Wires: `{payload['packet_contents']['logic_circuit_diagram']['wire_count']}`\n\n"
        "## M21 Pure Canvas Evidence\n\n"
        f"- Acceptance standard: {m21['acceptance_standard']}\n"
        f"{m21_lines}\n\n"
        "## M21 Natural Language Workbench Evidence\n\n"
        f"- Acceptance standard: {natural_language['acceptance_standard']}\n"
        f"{natural_language_lines}\n\n"
        "## M21 Natural Language Step Confirmation Evidence\n\n"
        f"- Acceptance standard: {step_confirmation['acceptance_standard']}\n"
        f"{step_confirmation_lines}\n\n"
        "## Embedded Demo Light Evidence\n\n"
        f"- Screenshot: `{payload['packet_contents']['embedded_light_demo']['screenshot']}`\n"
        f"- embedded_codex_light_palette: `{payload['packet_contents']['embedded_light_demo']['embedded_codex_light_palette']}`\n\n"
        "## Screenshot Evidence\n\n"
        f"{copied_screenshots}\n\n"
        "## Non-Claims\n\n"
        f"{non_claims}\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Stop Condition\n\n"
        "Do not continue M21 queue expansion until one decision option is selected.\n"
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def run_project_owner_acceptance_review_packet(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    packet_json_path = artifact_dir / PACKET_JSON_NAME
    packet_markdown_path = artifact_dir / PACKET_MARKDOWN_NAME
    evidence_dir = artifact_dir / "evidence"
    screenshot_dir = artifact_dir / "screenshots"

    closeout_command = _run_json_command(
        [
            sys.executable,
            "scripts/run_customer_demo_mvp_closeout.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "customer-demo-mvp-closeout"),
        ],
        timeout=480,
    )
    closeout = closeout_command["payload"]
    closeout_paths = closeout.get("artifact_paths", {})
    closeout_json_copy = _copy_file(
        closeout_paths.get("closeout_summary"),
        evidence_dir / "customer_demo_mvp_closeout.json",
    )
    closeout_markdown_copy = _copy_file(
        closeout_paths.get("closeout_markdown"),
        evidence_dir / "customer_demo_mvp_closeout.md",
    )
    project_status_html_copy = _copy_file(
        closeout_paths.get("project_visibility_html"),
        evidence_dir / "project_manager_status_summary.html",
    )
    copied_screenshots = _copy_screenshots(
        [
            str(path)
            for path in closeout_paths.get("screenshots", [])
            if isinstance(path, str)
        ],
        screenshot_dir,
    )
    packet_doc = _packet_doc_check()
    restricted = _restricted_diff()
    closeout_status_ok = (
        closeout_command["returncode"] == 0
        and closeout.get("status") == "pass"
        and closeout.get("closeout_status") == EXPECTED_CLOSEOUT_STATUS
    )
    copied_screenshot_paths = [item["packet_path"] for item in copied_screenshots]
    project_status_screenshot_ok = any(
        item["role"] == "project-status" and _path_exists(item["packet_path"])
        for item in copied_screenshots
    )
    embedded_light_demo = next(
        (item for item in copied_screenshots if item["role"] == "demo-first-screen"),
        {"packet_path": "", "source": "", "role": "demo-first-screen"},
    )
    logic_circuit_diagram = next(
        (item for item in copied_screenshots if item["role"] == "demo-chain"),
        {"packet_path": "", "source": "", "role": "demo-chain"},
    )
    m21_source = closeout.get("m21_logic_circuit_presentation", {})
    m21_c919_source = (
        m21_source.get("c919_fanout", {})
        if isinstance(m21_source.get("c919_fanout"), dict)
        else {}
    )
    m21_demo_source = (
        m21_source.get("demo_fanout", {})
        if isinstance(m21_source.get("demo_fanout"), dict)
        else {}
    )
    m21_c919_packet_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(m21_c919_source.get("screenshot", "")),
    )
    m21_demo_packet_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(m21_demo_source.get("screenshot", "")),
    )
    m21_pure_canvas_evidence = {
        "acceptance_standard": m21_source.get("acceptance_standard", ""),
        "c919_fanout": {
            **m21_c919_source,
            "packet_screenshot": m21_c919_packet_screenshot,
        },
        "demo_fanout": {
            **m21_demo_source,
            "packet_screenshot": m21_demo_packet_screenshot,
        },
    }
    natural_language_source = closeout.get("m21_natural_language_workbench", {})
    natural_language_c919 = (
        natural_language_source.get("c919_fanout", {})
        if isinstance(natural_language_source.get("c919_fanout"), dict)
        else {}
    )
    natural_language_demo = (
        natural_language_source.get("demo_fanout", {})
        if isinstance(natural_language_source.get("demo_fanout"), dict)
        else {}
    )
    m21_natural_language_workbench_evidence = {
        "acceptance_standard": natural_language_source.get("acceptance_standard", ""),
        "c919_fanout": natural_language_c919,
        "demo_fanout": natural_language_demo,
    }
    step_confirmation_source = closeout.get(
        "m21_natural_language_step_confirmation",
        {},
    )
    step_confirmation_c919 = (
        step_confirmation_source.get("c919_fanout", {})
        if isinstance(step_confirmation_source.get("c919_fanout"), dict)
        else {}
    )
    step_confirmation_demo = (
        step_confirmation_source.get("demo_fanout", {})
        if isinstance(step_confirmation_source.get("demo_fanout"), dict)
        else {}
    )
    step_confirmation_c919_packet_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(step_confirmation_c919.get("step_confirmation_screenshot", "")),
    )
    step_confirmation_c919_packet_revision_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(step_confirmation_c919.get("revision_confirmation_screenshot", "")),
    )
    step_confirmation_demo_packet_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(step_confirmation_demo.get("step_confirmation_screenshot", "")),
    )
    step_confirmation_demo_packet_revision_screenshot = _copied_packet_path_for_source(
        copied_screenshots,
        str(step_confirmation_demo.get("revision_confirmation_screenshot", "")),
    )
    m21_natural_language_step_confirmation_evidence = {
        "acceptance_standard": step_confirmation_source.get("acceptance_standard", ""),
        "c919_fanout": {
            **step_confirmation_c919,
            "packet_screenshot": step_confirmation_c919_packet_screenshot,
            "packet_revision_screenshot": (
                step_confirmation_c919_packet_revision_screenshot
            ),
        },
        "demo_fanout": {
            **step_confirmation_demo,
            "packet_screenshot": step_confirmation_demo_packet_screenshot,
            "packet_revision_screenshot": (
                step_confirmation_demo_packet_revision_screenshot
            ),
        },
    }
    logic_circuit_ok = (
        _path_exists(logic_circuit_diagram["packet_path"])
        and closeout.get("demo_surface", {}).get("node_count") == 20
        and closeout.get("demo_surface", {}).get("wire_count") == 23
    )
    m21_pure_canvas_ok = (
        closeout.get("deterministic_gates", {}).get("m21_pure_canvas_acceptance")
        == "pass"
        and m21_c919_source.get("pure_canvas_presentation_contract") == "pass"
        and m21_c919_source.get("pure_canvas_framing_contract") == "pass"
        and m21_demo_source.get("pure_canvas_presentation_contract") == "pass"
        and m21_demo_source.get("pure_canvas_framing_contract") == "pass"
        and m21_c919_source.get("canvas_default_display") == "logic-circuit-only"
        and m21_demo_source.get("canvas_default_display") == "logic-circuit-only"
        and _path_exists(m21_c919_packet_screenshot)
        and _path_exists(m21_demo_packet_screenshot)
    )
    m21_natural_language_ok = (
        closeout.get("deterministic_gates", {}).get(
            "m21_natural_language_workbench_acceptance"
        )
        == "pass"
        and _natural_language_entry_ok(natural_language_c919)
        and _natural_language_entry_ok(natural_language_demo)
    )
    m21_natural_language_step_ok = (
        closeout.get("deterministic_gates", {}).get(
            "m21_natural_language_step_confirmation_acceptance"
        )
        == "pass"
        and _natural_language_step_entry_ok(step_confirmation_c919)
        and _natural_language_step_entry_ok(step_confirmation_demo)
        and _path_exists(step_confirmation_c919_packet_screenshot)
        and _path_exists(step_confirmation_demo_packet_screenshot)
        and _path_exists(step_confirmation_c919_packet_revision_screenshot)
        and _path_exists(step_confirmation_demo_packet_revision_screenshot)
    )
    demo_screenshot_ok = any(
        item["role"].startswith("demo-") and _path_exists(item["packet_path"])
        for item in copied_screenshots
    )
    embedded_light_demo_ok = (
        closeout.get("visual_evidence", {}).get("embedded_codex_light_palette") == "pass"
        and _path_exists(embedded_light_demo["packet_path"])
    )
    boundary_ok = (
        not restricted
        and closeout.get("review_boundaries") == EXPECTED_REVIEW_BOUNDARIES
    )
    packet_artifacts_ok = all(
        _path_exists(path)
        for path in (
            closeout_json_copy,
            closeout_markdown_copy,
            project_status_html_copy,
        )
    )
    screenshots_ok = (
        bool(copied_screenshot_paths)
        and all(_path_exists(path) for path in copied_screenshot_paths)
        and project_status_screenshot_ok
        and demo_screenshot_ok
    )

    gates = {
        "customer_demo_mvp_closeout": _gate_status(closeout_status_ok),
        "packet_doc": packet_doc["status"],
        "packet_artifacts": _gate_status(packet_artifacts_ok),
        "logic_circuit_diagram": _gate_status(logic_circuit_ok),
        "m21_pure_canvas_evidence": _gate_status(m21_pure_canvas_ok),
        "m21_natural_language_workbench_evidence": _gate_status(
            m21_natural_language_ok
        ),
        "m21_natural_language_step_confirmation_evidence": _gate_status(
            m21_natural_language_step_ok
        ),
        "embedded_light_demo": _gate_status(embedded_light_demo_ok),
        "screenshots": _gate_status(screenshots_ok),
        "non_claim_boundaries": _gate_status(boundary_ok),
        "decision_options": _gate_status(
            [option["id"] for option in _decision_options()]
            == ["accept", "external_review", "demo_polish"]
        ),
        "local_gate": "fail",
    }
    mismatches = _collect_mismatches(gates, packet_doc)
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        and not mismatches
        else "fail"
    )
    gates["local_gate"] = status
    packet_status = "ready_for_project_owner_decision" if status == "pass" else "blocked"
    source_demo = closeout.get("demo_surface", {})

    payload = {
        "kind": "ai-fantui-project-owner-acceptance-review-packet",
        "version": 1,
        "status": status,
        "packet_status": packet_status,
        "decision_required": (
            "Select exactly one: accept, external_review, or demo_polish."
        ),
        "decision_options": _decision_options(),
        "source_closeout": {
            "status": closeout.get("status", "fail"),
            "closeout_status": closeout.get("closeout_status", ""),
            "demo_route": source_demo.get("route", ""),
            "node_count": source_demo.get("node_count", 0),
            "wire_count": source_demo.get("wire_count", 0),
            "source_json": closeout_paths.get("closeout_summary", ""),
            "source_markdown": closeout_paths.get("closeout_markdown", ""),
        },
        "packet_contents": {
            "packet_json": str(packet_json_path),
            "packet_markdown": str(packet_markdown_path),
            "packet_doc": str(PACKET_DOC_PATH),
            "closeout_json": closeout_json_copy,
            "closeout_markdown": closeout_markdown_copy,
            "project_status_html": project_status_html_copy,
            "project_status_source_html": closeout_paths.get("project_visibility_html", ""),
            "logic_circuit_diagram": {
                "screenshot": logic_circuit_diagram["packet_path"],
                "source_screenshot": logic_circuit_diagram["source"],
                "node_count": source_demo.get("node_count", 0),
                "wire_count": source_demo.get("wire_count", 0),
                "claim": "demo cockpit logic circuit diagram evidence",
            },
            "m21_pure_canvas_evidence": m21_pure_canvas_evidence,
            "m21_natural_language_workbench_evidence": (
                m21_natural_language_workbench_evidence
            ),
            "m21_natural_language_step_confirmation_evidence": (
                m21_natural_language_step_confirmation_evidence
            ),
            "embedded_light_demo": {
                "screenshot": embedded_light_demo["packet_path"],
                "source_screenshot": embedded_light_demo["source"],
                "embedded_codex_light_palette": closeout.get("visual_evidence", {}).get(
                    "embedded_codex_light_palette",
                    "fail",
                ),
                "embedded_palette": closeout.get("visual_evidence", {}).get(
                    "embedded_palette",
                    {},
                ),
                "claim": "embedded demo rendered in codex-light presentation mode",
            },
            "screenshots": copied_screenshots,
        },
        "non_claims": [
            "no production readiness claim",
            "no certification or DAL readiness claim",
            "no controller truth promotion",
            "no Safety Guardian final acceptance claim",
            "no external reviewer acceptance claim",
            "no customer deployment readiness claim",
        ],
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "deterministic_gates": gates,
        "checks": {
            "closeout": {
                "returncode": closeout_command["returncode"],
                "status": closeout.get("status", "fail"),
                "closeout_status": closeout.get("closeout_status", ""),
                "deterministic_gates": closeout.get("deterministic_gates", {}),
            },
            "packet_doc": packet_doc,
            "copied_artifacts": {
                "closeout_json": _path_exists(closeout_json_copy),
                "closeout_markdown": _path_exists(closeout_markdown_copy),
                "project_status_html": _path_exists(project_status_html_copy),
                "screenshot_count": len(
                    [item for item in copied_screenshots if _path_exists(item["packet_path"])]
                ),
            },
        },
        "mismatches": mismatches,
        "recommended_next_step": (
            "Choose accept, external_review, or demo_polish before any M21 queue expansion."
        ),
    }
    _write_text(packet_markdown_path, _markdown_packet(payload))
    if not packet_markdown_path.exists() or packet_markdown_path.stat().st_size == 0:
        payload["deterministic_gates"]["local_gate"] = "fail"
        payload["status"] = "fail"
        payload["packet_status"] = "blocked"
        payload["mismatches"].append("packet_markdown missing")
    _write_json(packet_json_path, payload)
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: project-owner acceptance review packet generated")
        print(f"packet_status: {payload['packet_status']}")
        print(f"packet: {payload['packet_contents']['packet_json']}")
    else:
        print(
            "FAIL: project-owner acceptance review packet failed "
            f"({', '.join(payload['mismatches'])})"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = run_project_owner_acceptance_review_packet(artifact_dir=args.artifact_dir)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
