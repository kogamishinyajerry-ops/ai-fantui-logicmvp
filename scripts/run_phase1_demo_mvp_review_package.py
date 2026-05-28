#!/usr/bin/env python3
"""Generate the Phase 1 demo MVP external review package."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-review-package")
PACKAGE_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_review_package_v0_1.schema.json"
)
PACKAGE_NAME = "phase1_demo_mvp_review_package_v0_1.json"
REPORT_NAME = "phase1_demo_mvp_review_report.md"
PACKAGE_ID = "phase1-demo-mvp-review-package-v0.1"
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 120) -> dict[str, Any]:
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


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
    for key in ("AI_FANTUI_PHASE1_DEMO_MVP_BASE_REF", "GITHUB_BASE_REF"):
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


def _command_pass(command: dict[str, Any]) -> bool:
    return command["returncode"] == 0 and command["payload"].get("status") == "pass"


def _screenshots_exist(browser_payload: dict[str, Any]) -> bool:
    screenshots = browser_payload.get("screenshots")
    if not isinstance(screenshots, dict) or not screenshots:
        return False
    return all(Path(path).exists() for path in screenshots.values())


def _demo_surface_from_gate(demo_payload: dict[str, Any]) -> dict[str, Any]:
    contract = demo_payload.get("contract", {})
    return {
        "route": "/demo-reconstruction",
        "title": "demo.html 复刻 MVP 控制台",
        "node_count": int(contract.get("expected_node_count", 0)),
        "wire_count": int(contract.get("expected_wire_count", 0)),
        "preset_count": int(contract.get("expected_preset_count", 0)),
        "status_output_count": int(contract.get("expected_status_output_count", 0)),
        "output_card_count": int(contract.get("expected_output_card_count", 0)),
    }


def _homepage_entry_from_gate(demo_payload: dict[str, Any]) -> dict[str, Any]:
    entry = demo_payload.get("homepage_entry")
    if isinstance(entry, dict):
        return {
            "route": str(entry.get("route", "")),
            "element_id": str(entry.get("element_id", "")),
            "priority": str(entry.get("priority", "")),
            "label": str(entry.get("label", "")),
        }
    return {
        "route": "/demo-reconstruction",
        "element_id": "home-first-phase-demo-entry",
        "priority": "first_phase_mvp",
        "label": "demo.html 复刻 MVP 控制台",
    }


def _residual_risks() -> list[dict[str, str]]:
    return [
        {
            "id": "PHASE1-RISK-001",
            "severity": "medium",
            "summary": "当前交付包证明 demo.html 复刻控制台可演示和可回归，不证明认证级控制律正确性。",
            "mitigation": "后续阶段继续通过 approved-task shell、Safety/Evidence gates 和人工审查推进。",
        }
    ]


def _non_certification_declaration() -> dict[str, str]:
    return {
        "certification_claim": "none",
        "dal_claim": "none",
        "production_readiness_claim": "none",
        "controller_truth_promotion": "none",
    }


def _review_boundaries(restricted: list[str]) -> dict[str, Any]:
    return {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": bool(
            [path for path in restricted if path in RESTRICTED_PATHS[:2]]
        ),
        "ui_layout_modified": bool(
            [path for path in restricted if path.startswith("src/well_harness/static/requirements_intake")]
        ),
    }


def _markdown_report(package: dict[str, Any]) -> str:
    screenshots = package["browser_acceptance"].get("screenshots", {})
    first_screen = screenshots.get("first_screen", "")
    chain_svg = screenshots.get("chain_svg", "")
    embedded_gate = package.get("visual_evidence", {}).get(
        "embedded_codex_light_palette",
        "fail",
    )
    return (
        "# Phase 1 Demo MVP Review Package\n\n"
        "## 交付物\n\n"
        "- demo.html 复刻 MVP 控制台\n"
        "- 路由：`/demo-reconstruction`\n"
        "- 首页入口：`home-first-phase-demo-entry`\n\n"
        "## 机器验收\n\n"
        f"- MVP gate: `{package['deterministic_gates']['demo_html_reconstruction_mvp']}`\n"
        f"- Browser acceptance: `{package['deterministic_gates']['browser_acceptance']}`\n"
        f"- Screenshots: `{package['deterministic_gates']['screenshots']}`\n\n"
        "## 截图证据\n\n"
        f"- 首屏：`{first_screen}`\n"
        f"- 链路图：`{chain_svg}`\n\n"
        "## Embedded Demo Light Evidence\n\n"
        f"- embedded_codex_light_palette: `{embedded_gate}`\n"
        f"- 浅色 embedded demo 首屏：`{first_screen}`\n\n"
        "## 残余风险\n\n"
        f"- {package['residual_risks'][0]['id']}: {package['residual_risks'][0]['summary']}\n\n"
        "## 非认证声明\n\n"
        "- certification_claim: `none`\n"
        "- dal_claim: `none`\n"
        "- production_readiness_claim: `none`\n"
        "- controller_truth_promotion: `none`\n"
    )


def build_phase1_demo_mvp_review_package(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    package_path = artifact_dir / PACKAGE_NAME
    report_path = artifact_dir / REPORT_NAME
    demo_gate_json_path = artifact_dir / "demo_html_reconstruction_mvp_gate.json"
    browser_json_path = artifact_dir / "demo_html_reconstruction_browser_acceptance.json"
    browser_artifact_dir = artifact_dir / "browser-acceptance"

    demo_gate = _run_json_command(
        [sys.executable, "scripts/verify_demo_html_reconstruction_mvp.py", "--format", "json"],
        timeout=60,
    )
    browser_acceptance = _run_json_command(
        [
            sys.executable,
            "scripts/verify_demo_html_reconstruction_browser_acceptance.py",
            "--artifact-dir",
            str(browser_artifact_dir),
            "--format",
            "json",
        ],
        timeout=120,
    )
    demo_payload = demo_gate["payload"]
    browser_payload = browser_acceptance["payload"]
    _write_json(demo_gate_json_path, demo_payload)
    _write_json(browser_json_path, browser_payload)

    restricted = _restricted_diff()
    gates = {
        "demo_html_reconstruction_mvp": "pass" if _command_pass(demo_gate) else "fail",
        "browser_acceptance": "pass" if _command_pass(browser_acceptance) else "fail",
        "screenshots": "pass" if _screenshots_exist(browser_payload) else "fail",
        "markdown_report": "pass",
        "boundary": "pass" if not restricted else "fail",
    }
    package = {
        "$schema": PACKAGE_SCHEMA_ID,
        "kind": "ai-fantui-phase1-demo-mvp-review-package",
        "package_id": PACKAGE_ID,
        "status": "pass" if all(value == "pass" for value in gates.values()) else "fail",
        "generated_at": _utc_now(),
        "demo_surface": _demo_surface_from_gate(demo_payload),
        "homepage_entry": _homepage_entry_from_gate(demo_payload),
        "deterministic_gates": gates,
        "artifact_paths": {
            "package": str(package_path),
            "markdown_report": str(report_path),
            "demo_gate_json": str(demo_gate_json_path),
            "browser_acceptance_json": str(browser_json_path),
        },
        "demo_gate": {
            "status": demo_payload.get("status", "fail"),
            "deterministic_gates": demo_payload.get("deterministic_gates", {}),
            "observed": demo_payload.get("observed", {}),
        },
        "browser_acceptance": {
            "status": browser_payload.get("status", "fail"),
            "deterministic_gates": browser_payload.get("deterministic_gates", {}),
            "embedded_palette": browser_payload.get("embedded_palette", {}),
            "screenshots": browser_payload.get("screenshots", {}),
            "first_screen_review": browser_payload.get("first_screen_review", {}),
            "pixel_visibility": browser_payload.get("pixel_visibility", {}),
            "interactions": browser_payload.get("interactions", {}),
        },
        "visual_evidence": {
            "embedded_codex_light_palette": browser_payload.get("deterministic_gates", {}).get(
                "embedded_codex_light_palette",
                "fail",
            ),
            "embedded_palette": browser_payload.get("embedded_palette", {}),
            "light_demo_first_screen": browser_payload.get("screenshots", {}).get(
                "first_screen",
                "",
            ),
            "browser_acceptance_json": str(browser_json_path),
        },
        "residual_risks": _residual_risks(),
        "non_certification_declaration": _non_certification_declaration(),
        "review_boundaries": _review_boundaries(restricted),
    }
    report_path.write_text(_markdown_report(package), encoding="utf-8")
    if not report_path.exists() or report_path.stat().st_size == 0:
        package["deterministic_gates"]["markdown_report"] = "fail"
        package["status"] = "fail"
    _write_json(package_path, package)
    return package


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Phase 1 demo MVP JSON and Markdown review artifacts.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP review package generated")
    else:
        failed = [
            key
            for key, value in payload.get("deterministic_gates", {}).items()
            if value != "pass"
        ]
        print(f"FAIL: phase1 demo MVP review package failed ({', '.join(failed)})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = build_phase1_demo_mvp_review_package(artifact_dir=args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-phase1-demo-mvp-review-package",
            "package_id": PACKAGE_ID,
            "status": "fail",
            "deterministic_gates": {
                "demo_html_reconstruction_mvp": "fail",
                "browser_acceptance": "fail",
                "screenshots": "fail",
                "markdown_report": "fail",
                "boundary": "fail",
            },
            "artifact_paths": {},
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
