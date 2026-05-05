from __future__ import annotations

import argparse
import http.client
import json
import sys
import tempfile
import threading
from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from well_harness import demo_server
from well_harness.demo_server import DemoRequestHandler


JsonObject = dict[str, Any]


@dataclass(frozen=True)
class SmokeStep:
    name: str
    method: str
    path: str
    status: int
    ok: bool
    detail: str


class ReleaseSmokeFailure(AssertionError):
    def __init__(self, step: SmokeStep, payload: JsonObject | str) -> None:
        super().__init__(step.detail)
        self.step = step
        self.payload = payload


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _request(
    port: int,
    method: str,
    path: str,
    *,
    payload: JsonObject | list[Any] | None = None,
) -> tuple[int, JsonObject | str]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        body: bytes | None = None
        headers: dict[str, str] = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
        content_type = response.getheader("Content-Type", "")
        if "application/json" in content_type:
            return response.status, json.loads(raw)
        return response.status, raw
    finally:
        connection.close()


def _record(
    steps: list[SmokeStep],
    *,
    name: str,
    method: str,
    path: str,
    status: int,
    ok: bool,
    detail: str,
    payload: JsonObject | str,
) -> None:
    step = SmokeStep(name=name, method=method, path=path, status=status, ok=ok, detail=detail)
    steps.append(step)
    if not ok:
        raise ReleaseSmokeFailure(step, payload)


def _require_json(payload: JsonObject | str, *, step_name: str) -> JsonObject:
    if isinstance(payload, dict):
        return payload
    raise ReleaseSmokeFailure(
        SmokeStep(
            name=step_name,
            method="",
            path="",
            status=0,
            ok=False,
            detail=f"{step_name} expected JSON object, got text response.",
        ),
        payload,
    )


def _bundle_request() -> JsonObject:
    return {
        "packet_payload": demo_server.reference_workbench_packet_payload(),
        "archive_bundle": True,
        "workspace_handoff": {
            "badgeText": "release-smoke",
            "system": "custom_reverse_control_v1",
            "packet": "reference packet",
            "result": "smoke pass candidate",
            "archive": "recorded",
            "workspace": "release candidate smoke",
            "note": "Release-candidate smoke archive for local workbench gate.",
        },
        "workspace_snapshot": {
            "kind": "well-harness-workbench-browser-workspace",
            "version": 2,
            "release_smoke": True,
            "runHistory": [{"id": "release-smoke-run-1", "title": "release candidate smoke"}],
        },
        "confirmed_root_cause": "Release smoke confirmed reference bundle path.",
        "repair_action": "No repair action; smoke exercises archive pipeline.",
        "validation_after_fix": "Restore/readback path is checked by the smoke gate.",
        "residual_risk": "This is a local smoke gate, not a production-ready claim.",
    }


def _lever_fault_request() -> JsonObject:
    return {
        "tra_deg": -14.0,
        "radio_altitude_ft": 5.0,
        "engine_running": True,
        "aircraft_on_ground": True,
        "reverser_inhibited": False,
        "eec_enable": True,
        "n1k": 35.0,
        "max_n1k_deploy_limit": 60.0,
        "sw1": True,
        "fault_injections": [{"node_id": "sw1", "fault_type": "stuck_off"}],
    }


def _run_against_server(port: int) -> list[SmokeStep]:
    steps: list[SmokeStep] = []

    status, payload = _request(port, "GET", "/workbench")
    html = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
    _record(
        steps,
        name="workbench_boot",
        method="GET",
        path="/workbench",
        status=status,
        ok=status == 200 and "Control Logic Workbench" in html and 'id="workbench-circuit-hero"' in html,
        detail="Expected /workbench HTML shell with circuit hero.",
        payload=payload,
    )

    status, payload = _request(port, "POST", "/api/workbench/bundle", payload=_bundle_request())
    bundle_payload = _require_json(payload, step_name="archive_bundle")
    archive_payload = bundle_payload.get("archive")
    manifest_path = archive_payload.get("manifest_json_path") if isinstance(archive_payload, dict) else None
    _record(
        steps,
        name="archive_bundle",
        method="POST",
        path="/api/workbench/bundle",
        status=status,
        ok=(
            status == 200
            and bundle_payload.get("bundle", {}).get("bundle_kind") == "full_workbench_bundle"
            and isinstance(manifest_path, str)
            and Path(manifest_path).exists()
        ),
        detail="Expected archived workbench bundle with manifest path.",
        payload=bundle_payload,
    )

    status, payload = _request(port, "GET", "/api/workbench/recent-archives")
    recent_payload = _require_json(payload, step_name="recent_archives")
    recent_archives = recent_payload.get("recent_archives")
    listed_manifest_paths = {
        item.get("manifest_path")
        for item in recent_archives
        if isinstance(item, dict) and item.get("restore_available") is True
    } if isinstance(recent_archives, list) else set()
    _record(
        steps,
        name="recent_archives",
        method="GET",
        path="/api/workbench/recent-archives",
        status=status,
        ok=status == 200 and manifest_path in listed_manifest_paths,
        detail="Expected recent archives list to include the just-created restore-available manifest.",
        payload=recent_payload,
    )

    status, payload = _request(port, "POST", "/api/workbench/archive-restore", payload={"manifest_path": manifest_path})
    restore_payload = _require_json(payload, step_name="archive_restore")
    _record(
        steps,
        name="archive_restore",
        method="POST",
        path="/api/workbench/archive-restore",
        status=status,
        ok=(
            status == 200
            and restore_payload.get("manifest_path") == str(Path(str(manifest_path)).resolve())
            and restore_payload.get("bundle", {}).get("bundle_kind") == "full_workbench_bundle"
            and restore_payload.get("workspace_snapshot", {}).get("release_smoke") is True
        ),
        detail="Expected archive restore/readback to return the smoke workspace snapshot.",
        payload=restore_payload,
    )

    status, payload = _request(port, "POST", "/api/lever-snapshot", payload=_lever_fault_request())
    lever_payload = _require_json(payload, step_name="lever_fault_injection")
    _record(
        steps,
        name="lever_fault_injection",
        method="POST",
        path="/api/lever-snapshot",
        status=status,
        ok=(
            status == 200
            and lever_payload.get("active_fault_node_ids") == ["sw1"]
            and lever_payload.get("logic", {}).get("logic1", {}).get("active") is False
        ),
        detail="Expected sw1 stuck_off fault to be recorded and block logic1.",
        payload=lever_payload,
    )

    status, payload = _request(port, "POST", "/api/workbench/archive-restore", payload={})
    invalid_payload = _require_json(payload, step_name="invalid_archive_restore")
    _record(
        steps,
        name="invalid_archive_restore",
        method="POST",
        path="/api/workbench/archive-restore",
        status=status,
        ok=(
            status == 400
            and invalid_payload.get("error") == "invalid_workbench_request"
            and invalid_payload.get("field") == "manifest_path"
        ),
        detail="Expected missing manifest_path to be rejected with an actionable field.",
        payload=invalid_payload,
    )

    return steps


def run_release_candidate_smoke(
    *,
    archive_root: Path | None = None,
    archive_root_factory: Callable[[], Path] | None = None,
) -> JsonObject:
    if archive_root is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="workbench-release-smoke-")
        root = Path(temp_dir.name).resolve()
    else:
        temp_dir = None
        root = archive_root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    original_archive_root = demo_server.default_workbench_archive_root
    demo_server.default_workbench_archive_root = archive_root_factory or (lambda: root)
    server, thread = _start_demo_server()
    try:
        steps = _run_against_server(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        demo_server.default_workbench_archive_root = original_archive_root
        if temp_dir is not None:
            temp_dir.cleanup()

    return {
        "kind": "well-harness-workbench-release-candidate-smoke-report",
        "version": 1,
        "status": "pass",
        "truth_level_impact": "none",
        "certification_claim": "none",
        "external_services": [],
        "archive_root": str(root),
        "step_count": len(steps),
        "steps": [step.__dict__ for step in steps],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local workbench release-candidate smoke gate.")
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = run_release_candidate_smoke(archive_root=args.archive_root)
    except ReleaseSmokeFailure as exc:
        report = {
            "kind": "well-harness-workbench-release-candidate-smoke-report",
            "version": 1,
            "status": "fail",
            "truth_level_impact": "none",
            "certification_claim": "none",
            "failed_step": exc.step.__dict__,
            "payload": exc.payload,
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"PASS workbench release-candidate smoke ({report['step_count']} steps)")
        for step in report["steps"]:
            print(f"- {step['name']}: {step['method']} {step['path']} -> {step['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
