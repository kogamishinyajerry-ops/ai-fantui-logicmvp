from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_review_package_v0_1.schema.json"
)
RELEASE_SUMMARY_SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_release_summary_v0_1.schema.json"
)
GATE_SUMMARY_SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_gate_summary_v0_1.schema.json"
)
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "phase1_demo_mvp_review_package_v0_1.json"
RELEASE_SUMMARY_FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "phase1_demo_mvp_release_summary_v0_1.json"
)
GATE_SUMMARY_FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "phase1_demo_mvp_gate_summary_v0_1.json"
)
RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_phase1_demo_mvp_review_package.py"
VERIFIER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_review_package.py"
CI_ARTIFACT_VERIFIER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_ci_artifact.py"
)
RELEASE_RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_phase1_demo_mvp_release_checklist.py"
RELEASE_SUMMARY_VERIFIER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_release_summary.py"
)
GATE_RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_phase1_demo_mvp_gate.py"
GATE_SUMMARY_VERIFIER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_gate_summary.py"
)
GATE_ARTIFACT_VERIFIER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_gate_artifact.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
CONSUMPTION_RUNBOOK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "phase1-demo-mvp-artifact-consumption-runbook.md"
)
RELEASE_CHECKLIST_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "phase1-demo-mvp-release-checklist.md"
)
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_review_package_v0_1.schema.json"
)
RELEASE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_release_summary_v0_1.schema.json"
)
GATE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_gate_summary_v0_1.schema.json"
)


def _load_phase1_review_runner_module():
    spec = importlib.util.spec_from_file_location(
        "phase1_demo_mvp_review_package_runner",
        RUNNER_SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _make_downloaded_phase1_artifact(tmp_path: Path) -> Path:
    source_artifact = tmp_path / "source-artifact"
    downloaded_artifact = tmp_path / "downloaded-phase1-demo-mvp-review-package"
    run = subprocess.run(
        [
            sys.executable,
            str(RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(source_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert run.returncode == 0, run.stderr

    shutil.copytree(source_artifact, downloaded_artifact)
    package_path = downloaded_artifact / "phase1_demo_mvp_review_package_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    ci_root = "artifacts/phase1-demo-mvp-review-package"
    package["artifact_paths"] = {
        "package": f"{ci_root}/phase1_demo_mvp_review_package_v0_1.json",
        "markdown_report": f"{ci_root}/phase1_demo_mvp_review_report.md",
        "demo_gate_json": f"{ci_root}/demo_html_reconstruction_mvp_gate.json",
        "browser_acceptance_json": (
            f"{ci_root}/demo_html_reconstruction_browser_acceptance.json"
        ),
    }
    package["browser_acceptance"]["screenshots"] = {
        name: f"{ci_root}/browser-acceptance/{Path(path).name}"
        for name, path in package["browser_acceptance"]["screenshots"].items()
    }
    package_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return downloaded_artifact


def _make_downloaded_phase1_gate_artifact(tmp_path: Path) -> Path:
    source_artifact = tmp_path / "source-gate-artifact"
    downloaded_artifact = tmp_path / "downloaded-phase1-demo-mvp-gate-artifact"
    run = subprocess.run(
        [
            sys.executable,
            str(GATE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(source_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert run.returncode == 0, run.stderr

    shutil.copytree(source_artifact, downloaded_artifact)
    ci_root = "artifacts/phase1-demo-mvp-review-package"
    common_artifact_paths = {
        "gate_summary": f"{ci_root}/phase1_demo_mvp_gate_summary.json",
        "release_summary": f"{ci_root}/phase1_demo_mvp_release_summary.json",
        "standalone_browser_acceptance_dir": f"{ci_root}/standalone-browser-acceptance",
        "package": f"{ci_root}/phase1_demo_mvp_review_package_v0_1.json",
        "markdown_report": f"{ci_root}/phase1_demo_mvp_review_report.md",
        "demo_gate_json": f"{ci_root}/demo_html_reconstruction_mvp_gate.json",
        "browser_acceptance_json": (
            f"{ci_root}/demo_html_reconstruction_browser_acceptance.json"
        ),
    }

    gate_summary_path = downloaded_artifact / "phase1_demo_mvp_gate_summary.json"
    gate_summary = json.loads(gate_summary_path.read_text(encoding="utf-8"))
    gate_summary["artifact_paths"] = {
        **common_artifact_paths,
        "screenshots": [
            f"{ci_root}/browser-acceptance/{Path(path).name}"
            for path in gate_summary["artifact_paths"]["screenshots"]
        ],
    }
    gate_summary_path.write_text(
        json.dumps(gate_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    release_summary_path = downloaded_artifact / "phase1_demo_mvp_release_summary.json"
    release_summary = json.loads(release_summary_path.read_text(encoding="utf-8"))
    release_summary["artifact_paths"] = {
        "release_summary": common_artifact_paths["release_summary"],
        "standalone_browser_acceptance_dir": common_artifact_paths[
            "standalone_browser_acceptance_dir"
        ],
        "package": common_artifact_paths["package"],
        "markdown_report": common_artifact_paths["markdown_report"],
        "demo_gate_json": common_artifact_paths["demo_gate_json"],
        "browser_acceptance_json": common_artifact_paths["browser_acceptance_json"],
        "screenshots": [
            f"{ci_root}/browser-acceptance/{Path(path).name}"
            for path in release_summary["artifact_paths"]["screenshots"]
        ],
    }
    release_summary_path.write_text(
        json.dumps(release_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    package_path = downloaded_artifact / "phase1_demo_mvp_review_package_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["artifact_paths"] = {
        "package": common_artifact_paths["package"],
        "markdown_report": common_artifact_paths["markdown_report"],
        "demo_gate_json": common_artifact_paths["demo_gate_json"],
        "browser_acceptance_json": common_artifact_paths["browser_acceptance_json"],
    }
    package["browser_acceptance"]["screenshots"] = {
        name: f"{ci_root}/browser-acceptance/{Path(path).name}"
        for name, path in package["browser_acceptance"]["screenshots"].items()
    }
    package_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return downloaded_artifact


def test_phase1_demo_mvp_review_package_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-phase1-demo-mvp-review-package"
    assert fixture["package_id"] == "phase1-demo-mvp-review-package-v0.1"
    assert fixture["status"] == "pass"
    assert fixture["demo_surface"]["route"] == "/demo-reconstruction"
    assert fixture["homepage_entry"]["element_id"] == "home-first-phase-demo-entry"
    assert fixture["deterministic_gates"] == {
        "demo_html_reconstruction_mvp": "pass",
        "browser_acceptance": "pass",
        "screenshots": "pass",
        "markdown_report": "pass",
        "boundary": "pass",
    }
    assert fixture["non_certification_declaration"] == {
        "certification_claim": "none",
        "dal_claim": "none",
        "production_readiness_claim": "none",
        "controller_truth_promotion": "none",
    }
    assert fixture["review_boundaries"]["controller_truth_modified"] is False
    assert fixture["review_boundaries"]["ui_layout_modified"] is False


def test_phase1_demo_mvp_release_summary_schema_validates_fixture() -> None:
    schema = json.loads(RELEASE_SUMMARY_SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(RELEASE_SUMMARY_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == RELEASE_SUMMARY_SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["$schema"] == RELEASE_SUMMARY_SCHEMA_ID
    assert fixture["kind"] == "ai-fantui-phase1-demo-mvp-release-summary"
    assert fixture["release_status"] == "pass"
    assert fixture["status"] == "pass"
    assert fixture["route"] == "/demo-reconstruction"
    assert fixture["demo_surface"]["node_count"] == 20
    assert fixture["demo_surface"]["wire_count"] == 23
    assert fixture["deterministic_gates"] == {
        "browser_acceptance": "pass",
        "review_package": "pass",
        "review_package_verification": "pass",
        "ci_artifact": "pass",
        "documentation": "pass",
        "boundary": "pass",
    }
    assert fixture["mismatches"] == []
    assert fixture["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_phase1_demo_mvp_gate_summary_schema_validates_fixture() -> None:
    schema = json.loads(GATE_SUMMARY_SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(GATE_SUMMARY_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == GATE_SUMMARY_SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["$schema"] == GATE_SUMMARY_SCHEMA_ID
    assert fixture["kind"] == "ai-fantui-phase1-demo-mvp-gate-summary"
    assert fixture["status"] == "pass"
    assert fixture["route"] == "/demo-reconstruction"
    assert fixture["demo_surface"]["node_count"] == 20
    assert fixture["demo_surface"]["wire_count"] == 23
    assert fixture["deterministic_gates"] == {
        "release_checklist": "pass",
        "release_summary_verification": "pass",
        "ci_artifact": "pass",
        "browser_acceptance": "pass",
        "boundary": "pass",
    }
    assert fixture["mismatches"] == []
    assert fixture["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_phase1_demo_mvp_review_package_runner_generates_json_and_markdown(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    package_path = Path(payload["artifact_paths"]["package"])
    report_path = Path(payload["artifact_paths"]["markdown_report"])
    assert package_path.exists()
    assert report_path.exists()

    package = json.loads(package_path.read_text(encoding="utf-8"))
    assert package["status"] == "pass"
    assert package["homepage_entry"]["route"] == "/demo-reconstruction"
    assert package["demo_surface"]["route"] == "/demo-reconstruction"
    assert package["demo_surface"]["node_count"] == 20
    assert package["demo_surface"]["wire_count"] == 23
    assert package["browser_acceptance"]["first_screen_review"]["operator_guide_visible"] is True
    assert package["browser_acceptance"]["deterministic_gates"]["embedded_codex_light_palette"] == "pass"
    assert package["browser_acceptance"]["embedded_palette"]["palette"] == "codex-light"
    assert package["visual_evidence"]["embedded_codex_light_palette"] == "pass"
    assert Path(package["visual_evidence"]["light_demo_first_screen"]).exists()
    assert package["browser_acceptance"]["pixel_visibility"]["chain_svg"]["status"] == "pass"
    assert package["browser_acceptance"]["interactions"]["max-reverse"]["outputs"]["thr_lock"] == "ON"
    assert package["browser_acceptance"]["interactions"]["inhibit-block"]["outputs"]["thr_lock"] != "ON"
    assert all(Path(path).exists() for path in package["browser_acceptance"]["screenshots"].values())
    assert package["residual_risks"] == [
        {
            "id": "PHASE1-RISK-001",
            "severity": "medium",
            "summary": "当前交付包证明 demo.html 复刻控制台可演示和可回归，不证明认证级控制律正确性。",
            "mitigation": "后续阶段继续通过 approved-task shell、Safety/Evidence gates 和人工审查推进。",
        }
    ]
    assert "demo.html 复刻 MVP 控制台" in report_path.read_text(encoding="utf-8")
    assert "embedded_codex_light_palette" in report_path.read_text(encoding="utf-8")
    assert "非认证声明" in report_path.read_text(encoding="utf-8")


def test_phase1_demo_mvp_review_package_boundary_checks_pr_base(
    monkeypatch,
) -> None:
    runner = _load_phase1_review_runner_module()
    restricted_path = "src/well_harness/static/requirements_intake/index.html"
    calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if "origin/codex/multi-agent-active-route-wiring...HEAD" in args:
            return subprocess.CompletedProcess(args, 0, restricted_path + "\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setenv("GITHUB_BASE_REF", "codex/multi-agent-active-route-wiring")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    assert runner._restricted_diff() == [restricted_path]
    assert any(
        "origin/codex/multi-agent-active-route-wiring...HEAD" in args
        for args in calls
    )


def test_phase1_demo_mvp_review_package_fetches_missing_pr_base(
    monkeypatch,
) -> None:
    runner = _load_phase1_review_runner_module()
    restricted_path = "src/well_harness/static/requirements_intake/index.html"
    calls: list[list[str]] = []
    origin_diff_attempts = 0

    def fake_run(args, **kwargs):
        nonlocal origin_diff_attempts
        calls.append(args)
        if args[:3] == ["git", "diff", "--name-only"]:
            if "origin/codex/multi-agent-active-route-wiring...HEAD" in args:
                origin_diff_attempts += 1
                if origin_diff_attempts == 1:
                    return subprocess.CompletedProcess(args, 128, "", "fatal: bad revision")
                return subprocess.CompletedProcess(args, 0, restricted_path + "\n", "")
            if any(str(arg).endswith("...HEAD") for arg in args):
                return subprocess.CompletedProcess(args, 128, "", "fatal: bad revision")
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:4] == ["git", "fetch", "--quiet", "origin"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setenv("GITHUB_BASE_REF", "codex/multi-agent-active-route-wiring")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    assert runner._restricted_diff() == [restricted_path]
    assert [
        "git",
        "fetch",
        "--quiet",
        "origin",
        "codex/multi-agent-active-route-wiring:refs/remotes/origin/codex/multi-agent-active-route-wiring",
    ] in calls
    assert origin_diff_attempts == 2


def test_phase1_demo_mvp_review_package_verifier_accepts_generated_package(
    tmp_path: Path,
) -> None:
    run = subprocess.run(
        [
            sys.executable,
            str(RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert run.returncode == 0, run.stderr
    package_path = Path(json.loads(run.stdout)["artifact_paths"]["package"])

    verify = subprocess.run(
        [
            sys.executable,
            str(VERIFIER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["status"] == "pass"
    assert payload["deterministic_gates"] == {
        "schema": "pass",
        "demo_gate": "pass",
        "browser_acceptance": "pass",
        "screenshots": "pass",
        "markdown_report": "pass",
        "boundary": "pass",
    }


def test_phase1_demo_mvp_ci_artifact_checker_accepts_downloaded_artifact_directory(
    tmp_path: Path,
) -> None:
    downloaded_artifact = _make_downloaded_phase1_artifact(tmp_path)

    verify = subprocess.run(
        [
            sys.executable,
            str(CI_ARTIFACT_VERIFIER_SCRIPT_PATH),
            "--artifact-dir",
            str(downloaded_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["kind"] == "ai-fantui-phase1-demo-mvp-ci-artifact-verification"
    assert payload["status"] == "pass"
    assert payload["artifact_paths"]["package"] == str(
        downloaded_artifact / "phase1_demo_mvp_review_package_v0_1.json"
    )
    assert payload["deterministic_gates"] == {
        "package": "pass",
        "markdown_report": "pass",
        "child_json": "pass",
        "screenshots": "pass",
        "browser_acceptance": "pass",
        "boundary": "pass",
    }
    assert all(Path(path).exists() for path in payload["required_files"])
    assert all(Path(path).exists() for path in payload["artifact_paths"]["screenshots"])


def test_phase1_demo_mvp_ci_artifact_checker_resolves_stale_absolute_paths_by_basename(
    tmp_path: Path,
) -> None:
    downloaded_artifact = _make_downloaded_phase1_artifact(tmp_path)
    package_path = downloaded_artifact / "phase1_demo_mvp_review_package_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    stale_ci_root = tmp_path / "stale-ci-runner-output"
    package["artifact_paths"] = {
        "package": str(stale_ci_root / "phase1_demo_mvp_review_package_v0_1.json"),
        "markdown_report": str(stale_ci_root / "phase1_demo_mvp_review_report.md"),
        "demo_gate_json": str(stale_ci_root / "demo_html_reconstruction_mvp_gate.json"),
        "browser_acceptance_json": str(
            stale_ci_root / "demo_html_reconstruction_browser_acceptance.json"
        ),
    }
    package["browser_acceptance"]["screenshots"] = {
        name: str(stale_ci_root / "browser-acceptance" / Path(path).name)
        for name, path in package["browser_acceptance"]["screenshots"].items()
    }
    package_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(CI_ARTIFACT_VERIFIER_SCRIPT_PATH),
            "--artifact-dir",
            str(downloaded_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["status"] == "pass"
    assert payload["artifact_paths"]["markdown_report"] == str(
        downloaded_artifact / "phase1_demo_mvp_review_report.md"
    )
    assert payload["artifact_paths"]["browser_acceptance_json"] == str(
        downloaded_artifact / "demo_html_reconstruction_browser_acceptance.json"
    )
    assert all(
        str(downloaded_artifact) in path
        for path in payload["artifact_paths"]["screenshots"]
    )


def test_phase1_demo_mvp_ci_artifact_checker_rejects_missing_screenshot(
    tmp_path: Path,
) -> None:
    downloaded_artifact = _make_downloaded_phase1_artifact(tmp_path)
    removed_screenshot = next((downloaded_artifact / "browser-acceptance").glob("*.png"))
    removed_screenshot.unlink()

    verify = subprocess.run(
        [
            sys.executable,
            str(CI_ARTIFACT_VERIFIER_SCRIPT_PATH),
            "--artifact-dir",
            str(downloaded_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 1
    payload = json.loads(verify.stdout)
    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["screenshots"] == "fail"
    assert any("screenshots" in mismatch for mismatch in payload["mismatches"])


def test_phase1_demo_mvp_review_package_make_target_is_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    release_runner = RELEASE_RUNNER_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "PHASE1_DEMO_MVP_REVIEW_PACKAGE_ARTIFACT_DIR" in makefile
    assert "PHASE1_DEMO_MVP_CI_ARTIFACT_DIR" in makefile
    assert "\nphase1-demo-mvp-review-package:\n" in makefile
    assert "\nphase1-demo-mvp-ci-artifact:\n" in makefile
    assert "\nverify-phase1-demo-mvp-ci-artifact:\n" in makefile
    assert "scripts/run_phase1_demo_mvp_review_package.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_review_package.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_ci_artifact.py" in makefile
    assert "scripts/run_phase1_demo_mvp_release_checklist.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_release_summary.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_gate_summary.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_gate_artifact.py" in makefile
    assert "scripts/verify_demo_html_reconstruction_browser_acceptance.py" in release_runner
    assert "scripts/run_phase1_demo_mvp_review_package.py" in release_runner
    assert "scripts/verify_phase1_demo_mvp_review_package.py" in release_runner
    assert "scripts/verify_phase1_demo_mvp_ci_artifact.py" in release_runner

    verify_target = makefile.split("\nverify-phase1-demo-mvp-ci-artifact:\n", maxsplit=1)[1].split(
        "\n\n",
        maxsplit=1,
    )[0]
    assert "scripts/verify_phase1_demo_mvp_ci_artifact.py" in verify_target
    assert "scripts/run_phase1_demo_mvp_review_package.py" not in verify_target


def test_phase1_demo_mvp_gate_is_the_ci_entrypoint_after_standalone_demo_preflight() -> None:
    workflow = GSD_AUTOMATION_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "pip install -e '.[dev,e2e]'" in workflow
    assert "Install Playwright Chromium" in workflow
    assert "python3 -m playwright install --with-deps chromium" in workflow
    assert "Verify demo.html reconstruction MVP" in workflow
    assert "scripts/verify_demo_html_reconstruction_mvp.py --format json" in workflow
    assert "Run Phase 1 demo MVP gate" in workflow
    assert (
        "PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR=artifacts/phase1-demo-mvp-review-package "
        "make phase1-demo-mvp-gate"
    ) in workflow
    assert "Verify Phase 1 demo MVP gate artifact" in workflow
    assert (
        "PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR=artifacts/phase1-demo-mvp-review-package "
        "make verify-phase1-demo-mvp-gate-artifact"
    ) in workflow
    assert workflow.index("Verify demo.html reconstruction MVP") < workflow.index(
        "Run Phase 1 demo MVP gate"
    )
    assert workflow.index("Run Phase 1 demo MVP gate") < workflow.index(
        "Verify Phase 1 demo MVP gate artifact"
    )
    assert workflow.index("Verify Phase 1 demo MVP gate artifact") < workflow.index(
        "Upload Phase 1 demo MVP review package"
    )
    assert "Run Phase 1 demo MVP release checklist" not in workflow
    assert "Run Phase 1 demo MVP review package" not in workflow
    assert "Verify Phase 1 demo MVP review package" not in workflow
    assert "Verify Phase 1 demo MVP CI artifact directory" not in workflow
    assert "Upload Phase 1 demo MVP review package" in workflow
    assert "name: phase1-demo-mvp-review-package" in workflow
    assert "path: artifacts/phase1-demo-mvp-review-package/**/*" in workflow
    assert "if-no-files-found: error" in workflow


def test_phase1_demo_mvp_artifact_consumption_runbook_is_actionable() -> None:
    runbook = CONSUMPTION_RUNBOOK_PATH.read_text(encoding="utf-8")

    required_fragments = [
        "phase1-demo-mvp-review-package",
        "gh run download",
        "scripts/verify_phase1_demo_mvp_ci_artifact.py --format json --artifact-dir",
        "ai-fantui-phase1-demo-mvp-ci-artifact-verification",
        '"status": "pass"',
        '"mismatches": []',
        "phase1_demo_mvp_review_package_v0_1.json",
        "phase1_demo_mvp_gate_summary.json",
        "phase1_demo_mvp_gate_summary_v0_1.schema.json",
        "make verify-phase1-demo-mvp-gate-artifact",
        "scripts/verify_phase1_demo_mvp_gate_summary.py --format json --summary",
        "scripts/verify_phase1_demo_mvp_gate_artifact.py --format json --artifact-dir",
        "ai-fantui-phase1-demo-mvp-gate-artifact-verification",
        "ai-fantui-phase1-demo-mvp-gate-summary",
        "phase1_demo_mvp_release_summary.json",
        "phase1_demo_mvp_release_summary_v0_1.schema.json",
        "scripts/verify_phase1_demo_mvp_release_summary.py --format json --summary",
        "ai-fantui-phase1-demo-mvp-release-summary",
        '"release_status": "pass"',
        "phase1_demo_mvp_review_report.md",
        "demo_html_reconstruction_mvp_gate.json",
        "demo_html_reconstruction_browser_acceptance.json",
        "browser-acceptance/*.png",
        '"package": "pass"',
        '"markdown_report": "pass"',
        '"child_json": "pass"',
        '"screenshots": "pass"',
        '"browser_acceptance": "pass"',
        '"boundary": "pass"',
        "不依赖原始 CI 工作目录",
        "controller truth",
        "certification_claim: none",
    ]
    for fragment in required_fragments:
        assert fragment in runbook


def test_phase1_demo_mvp_release_checklist_is_single_entry_acceptance_contract() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    release_runner = RELEASE_RUNNER_SCRIPT_PATH.read_text(encoding="utf-8")
    checklist = RELEASE_CHECKLIST_PATH.read_text(encoding="utf-8")

    assert "PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR" in makefile
    assert "phase1-demo-mvp-gate" in makefile
    assert "scripts/run_phase1_demo_mvp_gate.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_gate_summary.py" in makefile
    assert "verify-phase1-demo-mvp-gate-artifact" in makefile
    assert "scripts/verify_phase1_demo_mvp_gate_artifact.py" in makefile
    assert "PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR" in makefile
    assert "phase1-demo-mvp-release-checklist" in makefile
    assert "scripts/run_phase1_demo_mvp_release_checklist.py" in makefile
    assert "scripts/verify_phase1_demo_mvp_release_summary.py" in makefile
    assert "scripts/verify_demo_html_reconstruction_browser_acceptance.py" in release_runner
    assert "scripts/run_phase1_demo_mvp_review_package.py" in release_runner
    assert "scripts/verify_phase1_demo_mvp_ci_artifact.py" in release_runner
    assert "phase1-demo-mvp-artifact-consumption-runbook.md" in release_runner

    required_fragments = [
        "make phase1-demo-mvp-gate",
        "phase1_demo_mvp_gate_summary.json",
        "phase1_demo_mvp_gate_summary_v0_1.schema.json",
        "verify_phase1_demo_mvp_gate_summary.py",
        "verify-phase1-demo-mvp-gate-artifact",
        "make phase1-demo-mvp-release-checklist",
        "phase1_demo_mvp_release_summary.json",
        "demo-html-reconstruction-browser-acceptance",
        "phase1-demo-mvp-review-package",
        "verify-phase1-demo-mvp-ci-artifact",
        "phase1-demo-mvp-artifact-consumption-runbook.md",
        "/demo-reconstruction",
        "20 nodes",
        "23 wires",
        "release_status",
        '"pass"',
        "controller truth",
        "certification_claim: none",
        "不证明认证级控制律正确性",
    ]
    for fragment in required_fragments:
        assert fragment in checklist


def test_phase1_demo_mvp_gate_runner_generates_ci_ready_single_summary(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(GATE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    gate_summary_path = tmp_path / "phase1_demo_mvp_gate_summary.json"
    release_summary_path = tmp_path / "phase1_demo_mvp_release_summary.json"
    assert gate_summary_path.exists()
    assert release_summary_path.exists()
    assert payload == json.loads(gate_summary_path.read_text(encoding="utf-8"))
    assert payload["$schema"] == GATE_SUMMARY_SCHEMA_ID
    assert payload["kind"] == "ai-fantui-phase1-demo-mvp-gate-summary"
    assert payload["status"] == "pass"
    assert payload["route"] == "/demo-reconstruction"
    assert payload["demo_surface"] == {
        "route": "/demo-reconstruction",
        "title": "demo.html 复刻 MVP 控制台",
        "node_count": 20,
        "wire_count": 23,
        "preset_count": 5,
        "status_output_count": 6,
        "output_card_count": 4,
    }
    assert payload["deterministic_gates"] == {
        "release_checklist": "pass",
        "release_summary_verification": "pass",
        "ci_artifact": "pass",
        "browser_acceptance": "pass",
        "boundary": "pass",
    }
    assert payload["artifact_paths"]["gate_summary"] == str(gate_summary_path)
    assert payload["artifact_paths"]["release_summary"] == str(release_summary_path)
    assert payload["checks"]["release_checklist"]["kind"] == (
        "ai-fantui-phase1-demo-mvp-release-summary"
    )
    assert payload["checks"]["release_summary_verification"]["kind"] == (
        "ai-fantui-phase1-demo-mvp-release-summary-verification"
    )
    assert payload["checks"]["ci_artifact"]["kind"] == (
        "ai-fantui-phase1-demo-mvp-ci-artifact-verification"
    )
    assert payload["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["mismatches"] == []


def test_phase1_demo_mvp_gate_summary_verifier_accepts_generated_summary(
    tmp_path: Path,
) -> None:
    run = subprocess.run(
        [
            sys.executable,
            str(GATE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert run.returncode == 0, run.stderr
    summary_path = tmp_path / "phase1_demo_mvp_gate_summary.json"

    verify = subprocess.run(
        [
            sys.executable,
            str(GATE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["kind"] == "ai-fantui-phase1-demo-mvp-gate-summary-verification"
    assert payload["status"] == "pass"
    assert payload["deterministic_gates"] == {
        "schema": "pass",
        "gate_status": "pass",
        "deterministic_gates": "pass",
        "artifact_paths": "pass",
        "boundary": "pass",
    }
    assert payload["mismatches"] == []


def test_phase1_demo_mvp_gate_summary_verifier_accepts_downloaded_artifact_directory(
    tmp_path: Path,
) -> None:
    source_artifact = tmp_path / "source-gate"
    downloaded_artifact = tmp_path / "downloaded-gate"
    run = subprocess.run(
        [
            sys.executable,
            str(GATE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(source_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert run.returncode == 0, run.stderr
    shutil.copytree(source_artifact, downloaded_artifact)
    summary_path = downloaded_artifact / "phase1_demo_mvp_gate_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    ci_root = "artifacts/phase1-demo-mvp-review-package"
    summary["artifact_paths"] = {
        "gate_summary": f"{ci_root}/phase1_demo_mvp_gate_summary.json",
        "release_summary": f"{ci_root}/phase1_demo_mvp_release_summary.json",
        "standalone_browser_acceptance_dir": f"{ci_root}/standalone-browser-acceptance",
        "package": f"{ci_root}/phase1_demo_mvp_review_package_v0_1.json",
        "markdown_report": f"{ci_root}/phase1_demo_mvp_review_report.md",
        "demo_gate_json": f"{ci_root}/demo_html_reconstruction_mvp_gate.json",
        "browser_acceptance_json": (
            f"{ci_root}/demo_html_reconstruction_browser_acceptance.json"
        ),
        "screenshots": [
            f"{ci_root}/browser-acceptance/{Path(path).name}"
            for path in summary["artifact_paths"]["screenshots"]
        ],
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(GATE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["status"] == "pass"
    assert payload["deterministic_gates"]["artifact_paths"] == "pass"


def test_phase1_demo_mvp_gate_summary_verifier_rejects_failed_status(
    tmp_path: Path,
) -> None:
    summary = json.loads(GATE_SUMMARY_FIXTURE_PATH.read_text(encoding="utf-8"))
    summary["status"] = "fail"
    summary["deterministic_gates"]["ci_artifact"] = "fail"
    summary["mismatches"] = ["ci_artifact=fail"]
    summary_path = tmp_path / "phase1_demo_mvp_gate_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(GATE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 1
    payload = json.loads(verify.stdout)
    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["gate_status"] == "fail"
    assert payload["deterministic_gates"]["deterministic_gates"] == "fail"
    assert any("status" in mismatch for mismatch in payload["mismatches"])


def test_phase1_demo_mvp_gate_artifact_checker_accepts_downloaded_artifact_directory(
    tmp_path: Path,
) -> None:
    downloaded_artifact = _make_downloaded_phase1_gate_artifact(tmp_path)

    verify = subprocess.run(
        [
            sys.executable,
            str(GATE_ARTIFACT_VERIFIER_SCRIPT_PATH),
            "--artifact-dir",
            str(downloaded_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["kind"] == "ai-fantui-phase1-demo-mvp-gate-artifact-verification"
    assert payload["status"] == "pass"
    assert payload["artifact_paths"]["gate_summary"] == str(
        downloaded_artifact / "phase1_demo_mvp_gate_summary.json"
    )
    assert payload["deterministic_gates"] == {
        "gate_summary": "pass",
        "release_summary": "pass",
        "review_package": "pass",
        "screenshots": "pass",
        "boundary": "pass",
    }
    assert payload["mismatches"] == []
    assert all(Path(path).exists() for path in payload["required_files"])


def test_phase1_demo_mvp_gate_artifact_checker_rejects_missing_release_summary(
    tmp_path: Path,
) -> None:
    downloaded_artifact = _make_downloaded_phase1_gate_artifact(tmp_path)
    (downloaded_artifact / "phase1_demo_mvp_release_summary.json").unlink()

    verify = subprocess.run(
        [
            sys.executable,
            str(GATE_ARTIFACT_VERIFIER_SCRIPT_PATH),
            "--artifact-dir",
            str(downloaded_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert verify.returncode == 1
    payload = json.loads(verify.stdout)
    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["release_summary"] == "fail"
    assert any("release_summary" in mismatch for mismatch in payload["mismatches"])


def test_phase1_demo_mvp_gate_artifact_make_target_uses_downloaded_directory_only() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    target = makefile.split("verify-phase1-demo-mvp-gate-artifact:", 1)[1].split(
        "\n\n",
        1,
    )[0]

    assert "scripts/verify_phase1_demo_mvp_gate_artifact.py" in target
    assert "--artifact-dir" in target
    assert "$(PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR)" in target
    assert "scripts/run_phase1_demo_mvp_gate.py" not in target
    assert "scripts/run_phase1_demo_mvp_release_checklist.py" not in target


def test_phase1_demo_mvp_release_runner_generates_single_summary(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RELEASE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    summary_path = tmp_path / "phase1_demo_mvp_release_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload == summary
    assert summary["$schema"] == RELEASE_SUMMARY_SCHEMA_ID
    assert summary["kind"] == "ai-fantui-phase1-demo-mvp-release-summary"
    assert summary["release_status"] == "pass"
    assert summary["status"] == "pass"
    assert summary["route"] == "/demo-reconstruction"
    assert summary["demo_surface"] == {
        "route": "/demo-reconstruction",
        "title": "demo.html 复刻 MVP 控制台",
        "node_count": 20,
        "wire_count": 23,
        "preset_count": 5,
        "status_output_count": 6,
        "output_card_count": 4,
    }
    assert summary["deterministic_gates"] == {
        "browser_acceptance": "pass",
        "review_package": "pass",
        "review_package_verification": "pass",
        "ci_artifact": "pass",
        "documentation": "pass",
        "boundary": "pass",
    }
    assert summary["checks"]["browser_acceptance"]["status"] == "pass"
    assert summary["checks"]["review_package"]["status"] == "pass"
    assert summary["checks"]["review_package_verification"]["status"] == "pass"
    assert summary["checks"]["ci_artifact"]["status"] == "pass"
    assert summary["checks"]["documentation"] == {
        "status": "pass",
        "consumption_runbook_exists": True,
        "release_checklist_exists": True,
    }
    assert summary["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert summary["mismatches"] == []
    assert Path(summary["artifact_paths"]["release_summary"]).exists()
    assert Path(summary["artifact_paths"]["package"]).exists()
    assert Path(summary["artifact_paths"]["markdown_report"]).exists()


def test_phase1_demo_mvp_release_summary_verifier_accepts_generated_summary(
    tmp_path: Path,
) -> None:
    run = subprocess.run(
        [
            sys.executable,
            str(RELEASE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert run.returncode == 0, run.stderr
    summary_path = tmp_path / "phase1_demo_mvp_release_summary.json"

    verify = subprocess.run(
        [
            sys.executable,
            str(RELEASE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["kind"] == "ai-fantui-phase1-demo-mvp-release-summary-verification"
    assert payload["status"] == "pass"
    assert payload["deterministic_gates"] == {
        "schema": "pass",
        "release_status": "pass",
        "deterministic_gates": "pass",
        "artifact_paths": "pass",
        "boundary": "pass",
    }
    assert payload["mismatches"] == []


def test_phase1_demo_mvp_release_summary_verifier_accepts_downloaded_artifact_directory(
    tmp_path: Path,
) -> None:
    source_artifact = tmp_path / "source-release"
    downloaded_artifact = tmp_path / "downloaded-release"
    run = subprocess.run(
        [
            sys.executable,
            str(RELEASE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(source_artifact),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert run.returncode == 0, run.stderr
    shutil.copytree(source_artifact, downloaded_artifact)
    summary_path = downloaded_artifact / "phase1_demo_mvp_release_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    ci_root = "artifacts/phase1-demo-mvp-review-package"
    summary["artifact_paths"] = {
        "release_summary": f"{ci_root}/phase1_demo_mvp_release_summary.json",
        "standalone_browser_acceptance_dir": f"{ci_root}/standalone-browser-acceptance",
        "package": f"{ci_root}/phase1_demo_mvp_review_package_v0_1.json",
        "markdown_report": f"{ci_root}/phase1_demo_mvp_review_report.md",
        "demo_gate_json": f"{ci_root}/demo_html_reconstruction_mvp_gate.json",
        "browser_acceptance_json": (
            f"{ci_root}/demo_html_reconstruction_browser_acceptance.json"
        ),
        "screenshots": [
            f"{ci_root}/browser-acceptance/{Path(path).name}"
            for path in summary["artifact_paths"]["screenshots"]
        ],
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(RELEASE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads(verify.stdout)
    assert payload["status"] == "pass"
    assert payload["deterministic_gates"]["artifact_paths"] == "pass"


def test_phase1_demo_mvp_release_summary_verifier_rejects_failed_status(
    tmp_path: Path,
) -> None:
    summary = json.loads(RELEASE_SUMMARY_FIXTURE_PATH.read_text(encoding="utf-8"))
    summary["release_status"] = "fail"
    summary["status"] = "fail"
    summary["deterministic_gates"]["ci_artifact"] = "fail"
    summary["mismatches"] = ["ci_artifact=fail"]
    summary_path = tmp_path / "phase1_demo_mvp_release_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(RELEASE_SUMMARY_VERIFIER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert verify.returncode == 1
    payload = json.loads(verify.stdout)
    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["release_status"] == "fail"
    assert payload["deterministic_gates"]["deterministic_gates"] == "fail"
    assert any("release_status" in mismatch for mismatch in payload["mismatches"])
