#!/usr/bin/env python3
"""Build a read-only external review handoff for project-owner acceptance."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-project-owner-external-review-handoff")
HANDOFF_JSON_NAME = "project_owner_external_review_handoff.json"
HANDOFF_PROMPT_NAME = "project_owner_external_review_prompt.md"
HANDOFF_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "project-owner-external-review-handoff.md"
)
EXPECTED_PACKET_STATUS = "ready_for_project_owner_decision"
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
        description="Generate the read-only project-owner external review handoff.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 540) -> dict[str, Any]:
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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _path_exists(path_value: Any) -> bool:
    return isinstance(path_value, str) and bool(path_value) and Path(path_value).exists()


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


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


def _handoff_doc_check() -> dict[str, Any]:
    if not HANDOFF_DOC_PATH.exists():
        return {
            "status": "fail",
            "path": str(HANDOFF_DOC_PATH),
            "mismatches": ["project-owner-external-review-handoff.md is missing"],
        }
    text = HANDOFF_DOC_PATH.read_text(encoding="utf-8")
    markers = [
        "Project Owner External Review Handoff",
        "make project-owner-external-review-handoff",
        "ready_for_read_only_external_review",
        "accept_evidence",
        "needs_changes",
        "reject_evidence",
        "logic circuit diagram",
        "20 nodes / 23 wires",
        "certification",
    ]
    mismatches = [f"missing marker: {marker}" for marker in markers if marker not in text]
    return {
        "status": "pass" if not mismatches else "fail",
        "path": str(HANDOFF_DOC_PATH),
        "mismatches": mismatches,
    }


def _first_screenshot(packet: dict[str, Any], role: str) -> str:
    screenshots = packet.get("packet_contents", {}).get("screenshots", [])
    for item in screenshots:
        if item.get("role") == role and _path_exists(item.get("packet_path")):
            return item["packet_path"]
    return ""


def _packet_paths(packet: dict[str, Any]) -> dict[str, str]:
    contents = packet.get("packet_contents", {})
    logic_circuit = contents.get("logic_circuit_diagram", {})
    return {
        "packet_json": contents.get("packet_json", ""),
        "packet_markdown": contents.get("packet_markdown", ""),
        "closeout_json": contents.get("closeout_json", ""),
        "closeout_markdown": contents.get("closeout_markdown", ""),
        "project_status_html": contents.get("project_status_html", ""),
        "logic_circuit_screenshot": logic_circuit.get("screenshot", ""),
        "demo_first_screen_screenshot": _first_screenshot(packet, "demo-first-screen"),
    }


def _reviewer_constraints() -> list[str]:
    return [
        "read-only review only",
        "do not modify repository files",
        "do not approve controller truth promotion",
        "do not claim production readiness",
        "do not claim certification or DAL readiness",
        "do not claim customer deployment readiness",
        "base findings only on the listed evidence artifacts",
    ]


def _review_questions() -> list[str]:
    return [
        "Does the packet contain closeout JSON and Markdown?",
        "Does the logic circuit diagram evidence exist and show 20 nodes / 23 wires?",
        "Does the /demo-reconstruction route have browser screenshot evidence?",
        "Are non-claims and boundaries clear enough to prevent over-claiming?",
        "Is this evidence safe to send for project-owner acceptance?",
    ]


def _expected_review_output() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-project-owner-external-review-result",
        "review_mode": "read_only",
        "verdict": "accept_evidence | needs_changes | reject_evidence",
        "blocking_findings": [],
        "non_blocking_findings": [],
        "boundary_assessment": "",
        "next_decision_recommendation": "accept | external_review | demo_polish",
        "reviewed_artifacts": [
            {"id": "<required_reading.id>", "path": "<required_reading.path>", "status": "reviewed"}
        ],
        "boundary_claims": {
            "certification_claim": "none",
            "controller_truth_promotion": False,
            "production_readiness": False,
            "customer_deployment_readiness": False,
        },
    }


def _required_reading(packet_paths: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "id": "project_owner_packet_json",
            "label": "Project-owner acceptance packet JSON",
            "path": packet_paths["packet_json"],
        },
        {
            "id": "project_owner_packet_markdown",
            "label": "Project-owner acceptance packet Markdown",
            "path": packet_paths["packet_markdown"],
        },
        {
            "id": "customer_demo_closeout_json",
            "label": "Customer Demo MVP closeout JSON",
            "path": packet_paths["closeout_json"],
        },
        {
            "id": "customer_demo_closeout_markdown",
            "label": "Customer Demo MVP closeout Markdown",
            "path": packet_paths["closeout_markdown"],
        },
        {
            "id": "project_status_html",
            "label": "Project status HTML entrypoint",
            "path": packet_paths["project_status_html"],
        },
        {
            "id": "logic_circuit_diagram_screenshot",
            "label": "Demo cockpit logic circuit diagram screenshot",
            "path": packet_paths["logic_circuit_screenshot"],
        },
        {
            "id": "demo_first_screen_screenshot",
            "label": "Demo first-screen browser screenshot",
            "path": packet_paths["demo_first_screen_screenshot"],
        },
    ]


def _markdown_prompt(payload: dict[str, Any]) -> str:
    required_reading = "\n".join(
        f"- {item['label']}: `{item['path']}`"
        for item in payload["required_reading"]
    )
    constraints = "\n".join(f"- {item}" for item in payload["reviewer_constraints"])
    questions = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(payload["review_questions"], start=1)
    )
    return (
        "# Project Owner External Review Prompt\n\n"
        "你是外部审查 reviewer。请只做证据审查，不要修改仓库，不要运行会改变仓库状态的命令。\n\n"
        "## Review Mode\n\n"
        "- mode: `read_only`\n"
        f"- source packet status: `{payload['source_packet_status']}`\n"
        "- required verdict: choose exactly one of "
        "`accept_evidence`, `needs_changes`, or `reject_evidence`\n\n"
        "## Required Reading\n\n"
        f"{required_reading}\n\n"
        "## Must Check\n\n"
        f"{questions}\n\n"
        "## Hard Boundaries\n\n"
        f"{constraints}\n"
        "- The logic circuit diagram must remain evidence-only: expected surface is "
        "20 nodes / 23 wires.\n"
        "- Do not treat this as certification, DAL, production, or deployment approval.\n\n"
        "## Expected Output\n\n"
        "Return a compact JSON-like review with these fields:\n\n"
        "```json\n"
        f"{json.dumps(payload['expected_review_output'], ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def _collect_mismatches(gates: dict[str, str], doc_check: dict[str, Any]) -> list[str]:
    mismatches = [
        f"{name}=fail"
        for name, value in gates.items()
        if name != "local_gate" and value != "pass"
    ]
    for mismatch in doc_check.get("mismatches", []):
        mismatches.append(f"handoff_doc.{mismatch}")
    return mismatches


def run_project_owner_external_review_handoff(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    packet_artifact_dir = artifact_dir / "project-owner-acceptance-review-packet"
    handoff_json_path = artifact_dir / HANDOFF_JSON_NAME
    handoff_prompt_path = artifact_dir / HANDOFF_PROMPT_NAME

    packet_command = _run_json_command(
        [
            sys.executable,
            "scripts/run_project_owner_acceptance_review_packet.py",
            "--format",
            "json",
            "--artifact-dir",
            str(packet_artifact_dir),
        ],
        timeout=540,
    )
    packet = packet_command["payload"]
    packet_paths = _packet_paths(packet)
    required_reading = _required_reading(packet_paths)
    restricted = _restricted_diff()
    doc_check = _handoff_doc_check()
    logic_circuit = packet.get("packet_contents", {}).get("logic_circuit_diagram", {})

    packet_ok = (
        packet_command["returncode"] == 0
        and packet.get("status") == "pass"
        and packet.get("packet_status") == EXPECTED_PACKET_STATUS
    )
    logic_circuit_ok = (
        _path_exists(logic_circuit.get("screenshot"))
        and logic_circuit.get("node_count") == 20
        and logic_circuit.get("wire_count") == 23
    )
    required_artifacts_ok = all(_path_exists(item["path"]) for item in required_reading)
    boundary_ok = (
        not restricted
        and packet.get("review_boundaries") == EXPECTED_REVIEW_BOUNDARIES
        and "no certification or DAL readiness claim" in packet.get("non_claims", [])
        and "no controller truth promotion" in packet.get("non_claims", [])
    )

    payload: dict[str, Any] = {
        "kind": "ai-fantui-project-owner-external-review-handoff",
        "version": 1,
        "status": "fail",
        "handoff_status": "blocked",
        "review_mode": "read_only",
        "source_packet_status": packet.get("packet_status", ""),
        "decision_request": (
            "External reviewer must choose exactly one: accept_evidence, "
            "needs_changes, or reject_evidence."
        ),
        "reviewer_constraints": _reviewer_constraints(),
        "required_reading": required_reading,
        "review_questions": _review_questions(),
        "expected_review_output": _expected_review_output(),
        "artifact_paths": {
            "handoff_json": str(handoff_json_path),
            "handoff_prompt": str(handoff_prompt_path),
            "handoff_doc": str(HANDOFF_DOC_PATH),
            "source_packet_json": packet_paths["packet_json"],
            "source_packet_markdown": packet_paths["packet_markdown"],
            "logic_circuit_screenshot": packet_paths["logic_circuit_screenshot"],
            "demo_first_screen_screenshot": packet_paths["demo_first_screen_screenshot"],
        },
        "source_packet": {
            "returncode": packet_command["returncode"],
            "status": packet.get("status", "fail"),
            "packet_status": packet.get("packet_status", ""),
            "decision_options": packet.get("decision_options", []),
            "deterministic_gates": packet.get("deterministic_gates", {}),
        },
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "deterministic_gates": {
            "project_owner_packet": _gate_status(packet_ok),
            "logic_circuit_diagram": _gate_status(logic_circuit_ok),
            "required_artifacts": _gate_status(required_artifacts_ok),
            "review_prompt": "fail",
            "handoff_doc": doc_check["status"],
            "boundary": _gate_status(boundary_ok),
            "local_gate": "fail",
        },
        "mismatches": [],
        "recommended_next_step": (
            "Send this handoff to a read-only external reviewer, then choose "
            "accept, external_review, or demo_polish from the project-owner packet."
        ),
    }

    _write_text(handoff_prompt_path, _markdown_prompt(payload))
    prompt_text = handoff_prompt_path.read_text(encoding="utf-8")
    prompt_ok = (
        handoff_prompt_path.exists()
        and all(
            token in prompt_text
            for token in (
                "只做证据审查",
                "不要修改仓库",
                "accept_evidence",
                "needs_changes",
                "reject_evidence",
                "logic circuit diagram",
                "20 nodes / 23 wires",
                "certification",
            )
        )
    )
    payload["deterministic_gates"]["review_prompt"] = _gate_status(prompt_ok)
    payload["mismatches"] = _collect_mismatches(payload["deterministic_gates"], doc_check)
    status = (
        "pass"
        if all(
            value == "pass"
            for key, value in payload["deterministic_gates"].items()
            if key != "local_gate"
        )
        and not payload["mismatches"]
        else "fail"
    )
    payload["status"] = status
    payload["handoff_status"] = (
        "ready_for_read_only_external_review" if status == "pass" else "blocked"
    )
    payload["deterministic_gates"]["local_gate"] = status
    _write_json(handoff_json_path, payload)
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: project-owner external review handoff generated")
        print(f"handoff_status: {payload['handoff_status']}")
        print(f"handoff: {payload['artifact_paths']['handoff_json']}")
        print(f"prompt: {payload['artifact_paths']['handoff_prompt']}")
    else:
        print(
            "FAIL: project-owner external review handoff failed "
            f"({', '.join(payload['mismatches'])})"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = run_project_owner_external_review_handoff(artifact_dir=args.artifact_dir)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
