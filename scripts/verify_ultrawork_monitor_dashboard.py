#!/usr/bin/env python3
"""Validate UltraWork monitor dashboard artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-ultrawork-monitor-dashboard")
DASHBOARD_NAME = "ultrawork_monitor_dashboard_v0_1.json"
SCHEMA_NAME = "ultrawork_monitor_dashboard_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify an UltraWork monitor dashboard artifact.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory containing ultrawork_monitor_dashboard_v0_1.json.",
    )
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=None,
        help="Explicit dashboard JSON path. Overrides --artifact-dir.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dashboard_path(*, artifact_dir: Path, dashboard_path: Path | None) -> Path:
    if dashboard_path is not None:
        return dashboard_path
    return artifact_dir / DASHBOARD_NAME


def verify_ultrawork_monitor_dashboard(dashboard_path: Path) -> dict[str, Any]:
    mismatches: list[str] = []
    try:
        payload = _load_json(dashboard_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "dashboard_path": str(dashboard_path),
            "schema_valid": False,
            "html_exists": False,
            "mismatches": [f"dashboard could not be loaded: {exc}"],
        }
    schema = _load_json(PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"dashboard schema validation failed{location}: {error.message}")

    artifact_paths = payload.get("artifact_paths", {})
    html_path = Path(str(artifact_paths.get("dashboard_html", ""))) if isinstance(artifact_paths, dict) else Path()
    html_exists = html_path.exists() and html_path.stat().st_size > 0
    if not html_exists:
        mismatches.append("dashboard_html artifact must exist and be non-empty")

    blockers = payload.get("blockers", [])
    if not any(
        isinstance(item, dict)
        and item.get("blocker_id") == "notion-control-plane-404"
        and item.get("status") == "external_blocker"
        for item in blockers
    ):
        mismatches.append("Notion 404 must remain recorded as an external blocker")

    summary = payload.get("summary", {})
    lanes = payload.get("agent_lanes", [])
    if isinstance(summary, dict) and isinstance(lanes, list):
        expected_minimum = int(summary.get("completed_count", 0)) + int(
            summary.get("open_approved_count", 0)
        )
        if len(lanes) < expected_minimum:
            mismatches.append("agent_lanes must cover completed and open approved records")

    return {
        "status": "pass" if not mismatches else "fail",
        "dashboard_path": str(dashboard_path),
        "schema_valid": not errors,
        "html_exists": html_exists,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    result = verify_ultrawork_monitor_dashboard(
        _dashboard_path(artifact_dir=args.artifact_dir, dashboard_path=args.dashboard),
    )
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for mismatch in result["mismatches"]:
            print(f"- {mismatch}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
