from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


NOTION_VERSION = "2022-06-28"
DEFAULT_CONFIG_PATH = Path(".planning/notion_control_plane.json")
OUTPUT_FORMATS = {"text", "json"}
SKIP_REASON = "SKIP: NOTION_API_KEY is not set; control-plane access check was not run."
REQUIRED_DATABASE_KEYS = (
    "roadmap",
    "tasks",
    "sessions",
    "qa",
    "plans",
    "runs",
    "gates",
    "gaps",
    "decisions",
    "assets",
)
REQUIRED_PAGE_KEYS = (
    "dashboard",
    "constitution",
    "status",
    "control_plane",
    "opus_protocol",
    "opus_brief",
    "freeze_packet",
)
REQUIRED_URL_KEYS = (
    "github_repo",
    "github_actions",
)
REQUIRED_LEGACY_ARTIFACT_FIELDS = (
    "id",
    "kind",
    "title",
    "reason",
)


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_notion_control_plane.py [--format text|json]")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def validate_required_keys(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    databases = config.get("databases", {})
    pages = config.get("pages", {})
    urls = config.get("urls", {})

    for key in REQUIRED_DATABASE_KEYS:
        if not databases.get(key):
            errors.append(f"missing databases.{key}")
    for key in REQUIRED_PAGE_KEYS:
        if not pages.get(key):
            errors.append(f"missing pages.{key}")
    for key in REQUIRED_URL_KEYS:
        if not urls.get(key):
            errors.append(f"missing urls.{key}")
    if not config.get("default_plan"):
        errors.append("missing default_plan")
    if not config.get("default_review_gate"):
        errors.append("missing default_review_gate")
    for index, artifact in enumerate(config.get("legacy_review_artifacts", [])):
        for key in REQUIRED_LEGACY_ARTIFACT_FIELDS:
            if not artifact.get(key):
                errors.append(f"missing legacy_review_artifacts[{index}].{key}")
    return errors


def notion_request(token: str, path: str) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://api.notion.com" + path,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def check_remote_objects(
    config: dict[str, Any],
    *,
    request_get: Callable[[str, str], dict[str, Any]] = notion_request,
) -> list[dict[str, str]]:
    token = os.environ["NOTION_API_KEY"]
    results: list[dict[str, str]] = []

    for key in REQUIRED_PAGE_KEYS:
        page_id = config["pages"][key]
        request_get(token, f"/v1/pages/{page_id}")
        results.append({"kind": "page", "key": key, "id": page_id, "status": "ok"})

    for key in REQUIRED_DATABASE_KEYS:
        database_id = config["databases"][key]
        request_get(token, f"/v1/databases/{database_id}")
        results.append({"kind": "database", "key": key, "id": database_id, "status": "ok"})

    for index, artifact in enumerate(config.get("legacy_review_artifacts", [])):
        artifact_id = artifact["id"]
        request_get(token, f"/v1/pages/{artifact_id}")
        results.append(
            {
                "kind": "legacy_review_artifact",
                "key": f"{artifact['kind']}:{artifact['title']}",
                "id": artifact_id,
                "status": "ok",
                "index": str(index),
            }
        )

    return results


def validate_control_plane(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    request_get: Callable[[str, str], dict[str, Any]] = notion_request,
) -> tuple[int, dict[str, Any], list[str]]:
    config = load_config(config_path)
    key_errors = validate_required_keys(config)
    report: dict[str, Any] = {
        "status": "pass",
        "config_path": str(config_path),
        "checked_pages": 0,
        "checked_databases": 0,
        "checked_legacy_artifacts": 0,
        "results": [],
    }
    text_lines: list[str] = []

    if key_errors:
        report["status"] = "fail"
        report["reason"] = "config_missing_keys"
        report["errors"] = key_errors
        text_lines.extend(f"FAIL: {error}" for error in key_errors)
        return 1, report, text_lines

    token = os.environ.get("NOTION_API_KEY")
    if not token:
        report["status"] = "skip"
        report["reason"] = SKIP_REASON
        text_lines.append(SKIP_REASON)
        return 0, report, text_lines

    try:
        results = check_remote_objects(config, request_get=request_get)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        report["status"] = "fail"
        report["reason"] = f"HTTP {exc.code}"
        report["errors"] = [detail]
        text_lines.append(f"FAIL: Notion API returned HTTP {exc.code}")
        return 1, report, text_lines
    except Exception as exc:  # pragma: no cover - defensive path
        report["status"] = "fail"
        report["reason"] = str(exc)
        text_lines.append(f"FAIL: {exc}")
        return 1, report, text_lines

    report["results"] = results
    report["checked_pages"] = len([item for item in results if item["kind"] == "page"])
    report["checked_databases"] = len([item for item in results if item["kind"] == "database"])
    report["checked_legacy_artifacts"] = len([item for item in results if item["kind"] == "legacy_review_artifact"])
    text_lines.append(
        "PASS: validated "
        f"{report['checked_pages']} pages, "
        f"{report['checked_databases']} databases, and "
        f"{report['checked_legacy_artifacts']} legacy artifacts in the Notion control plane."
    )
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

    exit_code, report, text_lines = validate_control_plane()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
