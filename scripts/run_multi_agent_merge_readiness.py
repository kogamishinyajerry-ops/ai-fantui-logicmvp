#!/usr/bin/env python3
"""Generate the M29 multi-agent merge-readiness packet."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import sync_playwright

from well_harness.multi_agent_merge_readiness import (
    JSON_NAME,
    build_multi_agent_merge_readiness,
    write_multi_agent_merge_readiness_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-merge-readiness")
DEFAULT_VALIDATION_EVIDENCE_PATH = (
    Path("/tmp/ai-fantui-multi-agent-validation-evidence")
    / "multi_agent_validation_evidence_v0_1.json"
)
DEFAULT_GEOMETRY_DIR = Path("/tmp/ai-fantui-m29-merge-readiness-geometry")


GEOMETRY_PAGES = [
    (
        "ultrawork",
        Path("/tmp/ai-fantui-ultrawork-monitor-dashboard/ultrawork_monitor_dashboard_v0_1.html"),
        ["UltraWork Monitor", "RUN-QUEUE-011", "No active blockers"],
    ),
    (
        "cockpit",
        Path("/tmp/ai-fantui-multi-agent-operator-cockpit/multi_agent_operator_cockpit_v0_1.html"),
        ["Multi-Agent Operator Cockpit", "RUN-QUEUE-011", "repo_github_local_artifacts"],
    ),
    (
        "packaging",
        Path("/tmp/ai-fantui-multi-agent-packaging-consolidation/multi_agent_packaging_consolidation_v0_1.html"),
        ["Multi-Agent Packaging Consolidation", "multi-agent-cursor-baseline-v0-2", "repo-github-local-artifacts"],
    ),
    (
        "preflight",
        Path("/tmp/ai-fantui-multi-agent-pr-preflight/multi_agent_pr_preflight_v0_1.html"),
        ["Multi-Agent PR Preflight", "multi-agent-cursor-baseline-v0-2-01", "git add -f --"],
    ),
    (
        "evidence",
        Path("/tmp/ai-fantui-multi-agent-validation-evidence/multi_agent_validation_evidence_v0_1.html"),
        ["Multi-Agent Validation Evidence", "multi-agent-cursor-baseline-v0-2-01", "21 validation commands passed"],
    ),
]
VIEWPORTS = [
    ("desktop", 1440, 1000),
    ("mobile", 390, 900),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate M29 merge-readiness artifacts from local evidence and PR state.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--validation-evidence", type=Path, default=DEFAULT_VALIDATION_EVIDENCE_PATH)
    parser.add_argument("--geometry-dir", type=Path, default=DEFAULT_GEOMETRY_DIR)
    parser.add_argument("--pr-status-json", type=Path, default=None)
    parser.add_argument("--pr-number", type=int, default=270)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    env.setdefault("AI_FANTUI_QUEUE_PREFLIGHT_MODE", "fixture")
    return env


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_json(command: list[str], *, timeout: int = 120) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    if result.returncode != 0:
        return {
            "number": 0,
            "url": "",
            "state": "UNKNOWN",
            "isDraft": False,
            "mergeable": "UNKNOWN",
            "headRefOid": "",
            "statusCheckRollup": [],
            "reviews": [],
            "comments": [],
            "error": result.stderr.strip() or result.stdout.strip(),
        }
    return json.loads(result.stdout)


def _load_pr_status(pr_status_json: Path | None, *, pr_number: int) -> dict[str, Any]:
    if pr_status_json is not None:
        return _load_json(pr_status_json)
    return _run_json(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,url,state,isDraft,mergeable,headRefOid,baseRefName,statusCheckRollup,reviews,comments,files",
        ],
        timeout=120,
    )


def _changed_paths_from_pr_status(pr_status: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    base_ref = pr_status.get("baseRefName")
    if isinstance(base_ref, str) and base_ref:
        for candidate in (f"origin/{base_ref}", base_ref):
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{candidate}...HEAD"],
                cwd=PROJECT_ROOT,
                env=_env(),
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if result.returncode == 0:
                paths.extend(line for line in result.stdout.splitlines() if line)
                break

    files = pr_status.get("files", [])
    if not paths and isinstance(files, list):
        paths.extend(
            str(item.get("path"))
            for item in files
            if isinstance(item, dict) and item.get("path")
        )

    paths.extend(_changed_paths_from_worktree())
    return _dedupe_paths(paths)


def _changed_paths_from_worktree() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        path = path.strip('"')
        if path:
            paths.append(path)
    return paths


def _dedupe_paths(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for path in paths:
        if path not in seen:
            unique.append(path)
            seen.add(path)
    return unique


def _ensure_source_html() -> None:
    commands = [
        ["make", "verify-ultrawork-monitor-dashboard"],
        ["make", "verify-multi-agent-operator-cockpit"],
        ["make", "verify-multi-agent-packaging-consolidation"],
        ["make", "verify-multi-agent-pr-preflight"],
        ["make", "verify-multi-agent-validation-evidence"],
    ]
    for command in commands:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=_env(),
            capture_output=True,
            text=True,
            check=False,
            timeout=420,
        )
        if result.returncode != 0:
            raise RuntimeError(f"source HTML refresh failed: {' '.join(command)}\n{result.stderr}")


def _pixel_sample_count(path: Path) -> int:
    image = Image.open(path).convert("RGB")
    pixels = list(image.getdata())
    if not pixels:
        return 0
    sample = pixels[:: max(1, len(pixels) // 25000)]
    return len(set(sample))


def _run_geometry_gate(geometry_dir: Path) -> list[dict[str, Any]]:
    geometry_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for page_name, html_path, markers in GEOMETRY_PAGES:
            if not html_path.exists():
                results.append(
                    {
                        "page": page_name,
                        "viewport": "source",
                        "status": "fail",
                        "missing": [str(html_path)],
                        "overflow_px": 0,
                        "unique_sampled_colors": 0,
                        "screenshot": "",
                    }
                )
                continue
            for viewport_name, width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(html_path.resolve().as_uri(), wait_until="load")
                text = page.locator("body").inner_text(timeout=5000)
                missing = [marker for marker in markers if marker not in text]
                geometry = page.evaluate(
                    """() => ({
                        scrollWidth: document.documentElement.scrollWidth,
                        clientWidth: document.documentElement.clientWidth,
                        bodyScrollWidth: document.body.scrollWidth,
                        bodyClientWidth: document.body.clientWidth
                    })"""
                )
                screenshot_path = geometry_dir / f"{page_name}-{viewport_name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                page.close()
                overflow_px = max(
                    int(geometry["scrollWidth"]) - int(geometry["clientWidth"]),
                    int(geometry["bodyScrollWidth"]) - int(geometry["bodyClientWidth"]),
                )
                unique_colors = _pixel_sample_count(screenshot_path)
                status = "pass" if not missing and overflow_px <= 1 and unique_colors >= 20 else "fail"
                results.append(
                    {
                        "page": page_name,
                        "viewport": viewport_name,
                        "status": status,
                        "missing": missing,
                        "overflow_px": overflow_px,
                        "unique_sampled_colors": unique_colors,
                        "screenshot": str(screenshot_path),
                    }
                )
        browser.close()
    return results


def run_multi_agent_merge_readiness(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    validation_evidence_path: Path = DEFAULT_VALIDATION_EVIDENCE_PATH,
    geometry_dir: Path = DEFAULT_GEOMETRY_DIR,
    pr_status_json: Path | None = None,
    pr_number: int = 269,
) -> dict[str, Any]:
    if not validation_evidence_path.exists():
        raise FileNotFoundError(
            f"validation evidence is missing: {validation_evidence_path}. "
            "Run make multi-agent-validation-evidence first."
        )
    _ensure_source_html()
    validation_evidence = _load_json(validation_evidence_path)
    pr_status = _load_pr_status(pr_status_json, pr_number=pr_number)
    changed_paths = _changed_paths_from_pr_status(pr_status)
    if changed_paths:
        validation_evidence = dict(validation_evidence)
        validation_evidence["changed_paths"] = changed_paths
    geometry_results = _run_geometry_gate(geometry_dir)
    payload = build_multi_agent_merge_readiness(
        validation_evidence=validation_evidence,
        pr_status=pr_status,
        geometry_results=geometry_results,
        geometry_dir=str(geometry_dir),
    )
    return write_multi_agent_merge_readiness_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_merge_readiness(
        artifact_dir=args.artifact_dir,
        validation_evidence_path=args.validation_evidence,
        geometry_dir=args.geometry_dir,
        pr_status_json=args.pr_status_json,
        pr_number=args.pr_number,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"readiness: {payload['artifact_paths']['readiness_html']}")
        print(f"json: {payload['artifact_paths'].get('readiness_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
