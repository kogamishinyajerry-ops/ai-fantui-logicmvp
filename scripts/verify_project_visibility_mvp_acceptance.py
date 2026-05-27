#!/usr/bin/env python3
"""Browser screenshot acceptance gate for the Project Visibility MVP entrypoint."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-project-visibility-mvp-acceptance")
SUMMARY_NAME = "project_visibility_mvp_acceptance.json"
ACCEPTANCE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "project-visibility-mvp-acceptance.md"
)
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]
REQUIRED_TEXT = [
    "Project Manager Status Summary",
    "Multi-Agent Candidate Repair Pipeline MVP",
    "RUN-QUEUE-011",
    "CHECK_OUTPUT_COMMAND_CONFLICT_001",
    "Project Visibility MVP",
    "Do not continue M21 immediately.",
    "On track",
]


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_project_manager_summary(artifact_dir: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_project_manager_status_summary.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "project-manager-status-summary"),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _restricted_diff() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *RESTRICTED_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ["<git status failed>"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _acceptance_doc_check() -> dict[str, Any]:
    if not ACCEPTANCE_DOC_PATH.exists():
        return {
            "status": "fail",
            "path": str(ACCEPTANCE_DOC_PATH),
            "mismatches": ["project-visibility-mvp-acceptance.md is missing"],
        }
    text = ACCEPTANCE_DOC_PATH.read_text(encoding="utf-8")
    markers = [
        "Project Visibility MVP Acceptance",
        "make project-visibility-mvp-gate",
        "project_manager_status_summary.html",
        "RUN-QUEUE-011",
        "CHECK_OUTPUT_COMMAND_CONFLICT_001",
    ]
    mismatches = [f"missing marker: {marker}" for marker in markers if marker not in text]
    return {
        "status": "pass" if not mismatches else "fail",
        "path": str(ACCEPTANCE_DOC_PATH),
        "mismatches": mismatches,
    }


def _screenshot_pixels(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = list(image.getdata())
    if not pixels:
        return {
            "status": "fail",
            "width": width,
            "height": height,
            "different_from_background_pixels": 0,
            "sampled_unique_colors": 0,
        }
    reference = pixels[0]
    different = sum(
        1
        for pixel in pixels
        if sum(abs(pixel[index] - reference[index]) for index in range(3)) > 25
    )
    sampled = pixels[:: max(1, len(pixels) // 25000)]
    unique_colors = len(set(sampled))
    status = (
        "pass"
        if width >= 1000
        and height >= 700
        and different > 12000
        and unique_colors >= 20
        else "fail"
    )
    return {
        "status": status,
        "width": width,
        "height": height,
        "different_from_background_pixels": different,
        "sampled_unique_colors": unique_colors,
    }


def _browser_check(html_path: Path, screenshot_path: Path) -> dict[str, Any]:
    console_errors: list[str] = []
    observed: dict[str, Any] = {
        "required_text": {},
        "title": "",
        "h1": "",
    }
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 980})
            page.on("pageerror", lambda exc: console_errors.append(str(exc)))
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type == "error"
                else None,
            )
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.wait_for_selector("h1", timeout=5000)
            observed["title"] = page.title()
            observed["h1"] = page.locator("h1").inner_text(timeout=5000).strip()
            for marker in REQUIRED_TEXT:
                observed["required_text"][marker] = page.get_by_text(
                    marker,
                    exact=False,
                ).count() > 0
            page.screenshot(path=str(screenshot_path), full_page=True)
        finally:
            browser.close()
    screenshot_exists = screenshot_path.exists() and screenshot_path.stat().st_size > 0
    pixel_visibility = _screenshot_pixels(screenshot_path) if screenshot_exists else {
        "status": "fail",
        "width": 0,
        "height": 0,
        "different_from_background_pixels": 0,
        "sampled_unique_colors": 0,
    }
    all_required_text = all(observed["required_text"].values())
    return {
        "status": "pass"
        if not console_errors
        and screenshot_exists
        and pixel_visibility["status"] == "pass"
        and all_required_text
        else "fail",
        "console_errors": console_errors,
        "observed": observed,
        "screenshot_exists": screenshot_exists,
        "pixel_visibility": pixel_visibility,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def verify_project_visibility_mvp_acceptance(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / SUMMARY_NAME
    screenshot_path = artifact_dir / f"project-visibility-mvp-entrypoint-{_utc_stamp()}.png"

    summary_result = _run_project_manager_summary(artifact_dir)
    summary_payload = summary_result["payload"]
    html_path_text = str(summary_payload.get("artifact_paths", {}).get("summary_html", ""))
    html_path = Path(html_path_text) if html_path_text else None
    restricted = _restricted_diff()
    doc_check = _acceptance_doc_check()
    browser_check = (
        _browser_check(html_path, screenshot_path)
        if html_path is not None and html_path.exists() and html_path.is_file()
        else {
            "status": "fail",
            "console_errors": ["summary_html is missing"],
            "observed": {"required_text": {}, "title": "", "h1": ""},
            "screenshot_exists": False,
            "pixel_visibility": {
                "status": "fail",
                "width": 0,
                "height": 0,
                "different_from_background_pixels": 0,
                "sampled_unique_colors": 0,
            },
        }
    )

    required_text = browser_check["observed"].get("required_text", {})
    gates = {
        "project_manager_status_summary": _gate_status(
            summary_result["returncode"] == 0
            and summary_payload.get("status") == "pass"
        ),
        "acceptance_doc": doc_check["status"],
        "html_entrypoint": _gate_status(
            html_path is not None
            and html_path.exists()
            and html_path.is_file()
            and html_path.stat().st_size > 0
        ),
        "browser_render": _gate_status(
            browser_check["status"] == "pass"
            and browser_check["observed"].get("h1") == "Project Manager Status Summary"
        ),
        "screenshots": _gate_status(browser_check["screenshot_exists"]),
        "pixel_visibility": browser_check["pixel_visibility"]["status"],
        "key_content": _gate_status(
            bool(required_text) and all(required_text.values())
        ),
        "boundary": _gate_status(not restricted),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        else "fail"
    )
    gates["local_gate"] = status

    payload = {
        "kind": "ai-fantui-project-visibility-mvp-acceptance",
        "version": 1,
        "status": status,
        "entrypoint": {
            "name": "Project Manager Status Summary",
            "html": str(html_path or ""),
            "command": "make project-visibility-mvp-gate",
        },
        "deterministic_gates": gates,
        "checks": {
            "project_manager_status_summary": {
                "returncode": summary_result["returncode"],
                "status": summary_payload.get("status", "fail"),
                "deterministic_gates": summary_payload.get("deterministic_gates", {}),
            },
            "acceptance_doc": doc_check,
            "browser": browser_check,
        },
        "artifact_paths": {
            "acceptance_summary": str(summary_path),
            "acceptance_doc": str(ACCEPTANCE_DOC_PATH),
            "status_summary_json": str(
                summary_payload.get("artifact_paths", {}).get("summary_json", "")
            ),
            "status_summary_markdown": str(
                summary_payload.get("artifact_paths", {}).get("summary_markdown", "")
            ),
            "status_summary_html": str(html_path or ""),
            "screenshot_desktop": str(screenshot_path),
        },
        "review_boundaries": {
            "controller_truth_modified": bool(
                [path for path in restricted if path in RESTRICTED_PATHS[:2]]
            ),
            "ui_layout_modified": bool(
                [
                    path
                    for path in restricted
                    if path.startswith("src/well_harness/static/requirements_intake")
                ]
            ),
            "truth_effect": "none",
            "certification_claim": "none",
        },
        "next_decision_options": [
            "accept",
            "external_review",
            "demo_polish",
        ],
        "recommended_next_step": (
            "Use this gate as the formal Project Visibility MVP entrypoint, "
            "then choose accept, external_review, or demo_polish. M21 remains "
            "blocked unless accept succeeds."
        ),
    }
    _write_json(summary_path, payload)
    return payload


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Project Visibility MVP browser screenshot acceptance.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: Project Visibility MVP acceptance gate passed")
        print(f"entrypoint: {payload['entrypoint']['html']}")
        print(f"screenshot: {payload['artifact_paths']['screenshot_desktop']}")
    else:
        failed = [
            key
            for key, value in payload.get("deterministic_gates", {}).items()
            if value != "pass"
        ]
        print(f"FAIL: Project Visibility MVP acceptance gate failed: {failed}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = verify_project_visibility_mvp_acceptance(artifact_dir=args.artifact_dir)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
