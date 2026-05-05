from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_KIND = "well-harness-workbench-release-evidence-manifest"
MANIFEST_VERSION = 1
VALIDATION_KIND = "well-harness-workbench-release-evidence-manifest-validation"
REQUIRED_MATURITY_DIMENSIONS = (
    "local_operator_smoke",
    "release_manifest_validation",
    "unit_regression_gate",
    "full_opt_in_e2e_gate",
    "full_strict_mypy_gate",
    "deployment_packaging",
    "cloud_hosting",
    "certification_authority",
)
REQUIRED_MATURITY_STATUSES = ("pass", "rerun_required", "blocked", "not_claimed")
FIXED_MATURITY_STATUSES = {
    "unit_regression_gate": "rerun_required",
    "full_strict_mypy_gate": "blocked",
    "deployment_packaging": "not_claimed",
    "cloud_hosting": "not_claimed",
    "certification_authority": "not_claimed",
}
SENSITIVE_NAME_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "password",
    "secret",
    "token",
)


JsonObject = dict[str, Any]
GitRunner = Callable[[tuple[str, ...], Path], str]
Clock = Callable[[], datetime]


def _run_git(args: tuple[str, ...], repo_root: Path) -> str:
    completed = subprocess.run(
        ("git", *args),
        cwd=repo_root,
        capture_output=True,
        check=True,
        text=True,
    )
    return completed.stdout.strip()


def _git_metadata(repo_root: Path, git_runner: GitRunner) -> JsonObject:
    return {
        "sha": git_runner(("rev-parse", "HEAD"), repo_root),
        "short_sha": git_runner(("rev-parse", "--short=12", "HEAD"), repo_root),
        "branch": git_runner(("branch", "--show-current"), repo_root) or "detached",
    }


def _verification_commands() -> list[JsonObject]:
    return [
        {
            "id": "release_candidate_smoke_gate",
            "status": "pass",
            "status_basis": "recorded_evidence",
            "scope": "local_operator_flow",
            "command": (
                "uv run --locked --extra dev python "
                "tools/workbench_release_candidate_smoke.py --format json"
            ),
            "evidence_ref": "live Linear JER-242 / PR #235",
            "evidence_summary": (
                "Local smoke gate passed 6 steps: /workbench boot, archive bundle/list/restore, "
                "lever fault injection, and invalid archive-restore rejection."
            ),
            "external_services": [],
        },
        {
            "id": "full_opt_in_e2e",
            "status": "pass",
            "status_basis": "recorded_evidence",
            "scope": "browser_e2e",
            "command": (
                "uv run --locked --extra dev --extra e2e python -m pytest "
                "tests/ -m e2e -q --tb=short"
            ),
            "evidence_ref": "docs/coordination/JER-243-e2e-refresh.md",
            "evidence_summary": "93 passed / 3445 deselected in 149.97s on origin/main@9516fa6.",
            "external_services": [],
        },
        {
            "id": "unit_tests_validation_suite",
            "status": "pass",
            "status_basis": "rerun_required_for_current_release_candidate",
            "scope": "unit_regression",
            "command": (
                "uv run --locked --extra dev python "
                "tools/run_gsd_validation_suite.py --only unit_tests --format json"
            ),
            "evidence_ref": "JER-244 release candidate closeout evidence",
            "evidence_summary": (
                "This command must pass on the exact release candidate SHA before any handoff."
            ),
            "external_services": [],
        },
        {
            "id": "full_strict_mypy",
            "status": "blocked",
            "status_basis": "recorded_evidence",
            "scope": "typecheck",
            "command": (
                "uv run --locked --extra typecheck python "
                "tools/run_mypy_gate.py --format json --report-only"
            ),
            "evidence_ref": "live Linear JER-257 / PR #250",
            "evidence_summary": "Blocked: 4548 errors in 305 files. Do not claim mypy clean.",
            "external_services": [],
        },
    ]


def _required_environment() -> JsonObject:
    return {
        "required_env_vars_for_local_release_gates": [],
        "optional_env_vars": [
            {
                "name": "MINIMAX_API_KEY",
                "used_for": "Optional AI suggestion/planner endpoints only; not used by release smoke/e2e gates.",
            },
            {
                "name": "WORKBENCH_PROPOSALS_DIR",
                "used_for": "Optional local proposal storage override.",
            },
            {
                "name": "WORKBENCH_DEV_QUEUE_DIR",
                "used_for": "Optional local development queue storage override.",
            },
            {
                "name": "WORKBENCH_SKILL_EXECUTIONS_DIR",
                "used_for": "Optional local skill-execution audit storage override.",
            },
            {
                "name": "WORKBENCH_AUTO_SPAWN_EXECUTOR",
                "used_for": "Opt-in executor spawning. Leave unset for release smoke gates.",
            },
            {
                "name": "WORKBENCH_SLO_WEBHOOK_URL",
                "used_for": "Optional outbound SLO webhook. Not part of local production gate evidence.",
            },
        ],
        "secret_policy": "Manifest records environment variable names only, never values.",
    }


def _not_claimed_gates() -> list[JsonObject]:
    return [
        {
            "id": "production_ready",
            "reason": (
                "This manifest and runbook are local readiness evidence only; deployment and "
                "operational ownership gates are not complete."
            ),
        },
        {
            "id": "cloud_deployment_ready",
            "reason": "No cloud deployment path, service account policy, or hosted runtime gate is merged.",
        },
        {
            "id": "certification_ready",
            "reason": "Workbench sandbox artifacts have truth_effect none and are not certification evidence.",
        },
        {
            "id": "full_strict_mypy_clean",
            "reason": "The official JER-171 mypy gate remains blocked.",
        },
    ]


def _unsupported_external_dependencies() -> list[JsonObject]:
    return [
        {
            "name": "browser_writes_to_linear_or_notion",
            "status": "unsupported",
            "reason": "The workbench UI must not perform live control-plane writes.",
        },
        {
            "name": "remote_llm_required_for_release_gate",
            "status": "unsupported",
            "reason": "Release smoke, e2e, unit tests, and manifest validation run without LLM services.",
        },
        {
            "name": "cloud_deploy",
            "status": "unsupported",
            "reason": "No production hosting or cloud deployment artifact is part of JER-244.",
        },
    ]


def _current_blockers() -> list[JsonObject]:
    return [
        {
            "id": "JER-171-full-strict-mypy",
            "status": "blocked",
            "summary": "Official strict mypy wrapper is still blocked at 4548 errors in 305 files.",
        },
        {
            "id": "deployment-packaging",
            "status": "not_started",
            "summary": "No service packaging, hosted deployment, rollback, or operator ownership gate is merged.",
        },
        {
            "id": "certification-authority",
            "status": "not_claimed",
            "summary": "Sandbox workbench evidence has truth_effect none and cannot certify controller behavior.",
        },
    ]


def _workbench_maturity_snapshot() -> JsonObject:
    return {
        "kind": "well-harness-workbench-maturity-snapshot",
        "version": 1,
        "live_linear_issue": "JER-258",
        "overall_status": "local_release_candidate_not_production_ready",
        "scope": "single_user_local_workbench",
        "truth_level_impact": "none",
        "certification_claim": "none",
        "status_policy": {
            "pass": "Recorded evidence exists, but exact release-candidate SHA reruns may still be required.",
            "rerun_required": "The gate must be rerun on the exact release-candidate SHA before handoff.",
            "blocked": "Known blocker remains active and must not be hidden by other pass evidence.",
            "not_claimed": "No readiness claim exists for this dimension.",
        },
        "dimensions": [
            {
                "id": "local_operator_smoke",
                "status": "pass",
                "required_for": "local_release_candidate",
                "command": (
                    "uv run --locked --extra dev python "
                    "tools/workbench_release_candidate_smoke.py --format json"
                ),
                "evidence_ref": "live Linear JER-242 / PR #235",
                "summary": "Local smoke covers /workbench boot, archive bundle/list/restore, lever fault injection, and invalid restore input.",
                "external_services": [],
            },
            {
                "id": "release_manifest_validation",
                "status": "pass",
                "required_for": "local_release_candidate",
                "command": (
                    "uv run --locked --extra dev python "
                    "tools/workbench_release_manifest.py --validate --format json"
                ),
                "evidence_ref": "live Linear JER-258",
                "summary": "Manifest validation enforces required maturity dimensions, no secret values, and explicit not-claimed gates.",
                "external_services": [],
            },
            {
                "id": "unit_regression_gate",
                "status": "rerun_required",
                "required_for": "release_handoff",
                "command": (
                    "uv run --locked --extra dev python "
                    "tools/run_gsd_validation_suite.py --only unit_tests --format json"
                ),
                "evidence_ref": "live Linear JER-257 / PR #250",
                "summary": "JER-257 branch evidence passed, but this gate must be rerun on the exact release-candidate SHA before handoff.",
                "external_services": [],
            },
            {
                "id": "full_opt_in_e2e_gate",
                "status": "pass",
                "required_for": "current_browser_e2e_claim",
                "command": (
                    "uv run --locked --extra dev --extra e2e python -m pytest "
                    "tests/ -m e2e -q --tb=short"
                ),
                "evidence_ref": "docs/coordination/JER-243-e2e-refresh.md",
                "summary": "Recorded current-main evidence: 93 passed / 3445 deselected in 149.97s on origin/main@9516fa6.",
                "external_services": [],
            },
            {
                "id": "full_strict_mypy_gate",
                "status": "blocked",
                "required_for": "full_typecheck_clean_claim",
                "command": (
                    "uv run --locked --extra typecheck python "
                    "tools/run_mypy_gate.py --format json --report-only"
                ),
                "evidence_ref": "live Linear JER-257 / PR #250",
                "summary": "Official wrapper remains blocked at 4548 errors in 305 files after tranche 15.",
                "external_services": [],
            },
            {
                "id": "deployment_packaging",
                "status": "not_claimed",
                "required_for": "production_ready_claim",
                "summary": "No service packaging, rollback, or operator ownership gate is merged.",
                "external_services": [],
            },
            {
                "id": "cloud_hosting",
                "status": "not_claimed",
                "required_for": "cloud_deployment_ready_claim",
                "summary": "No hosted runtime, service account policy, or cloud deployment artifact is merged.",
                "external_services": [],
            },
            {
                "id": "certification_authority",
                "status": "not_claimed",
                "required_for": "certification_ready_claim",
                "summary": "Sandbox workbench artifacts have truth_effect none and are not certification evidence.",
                "external_services": [],
            },
        ],
    }


def build_release_manifest(
    *,
    repo_root: Path = PROJECT_ROOT,
    git_runner: GitRunner = _run_git,
    clock: Clock | None = None,
) -> JsonObject:
    now = (clock or (lambda: datetime.now(timezone.utc)))()
    return {
        "kind": MANIFEST_KIND,
        "version": MANIFEST_VERSION,
        "generated_at": now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repository": {
            "name": "ai-fantui-logicmvp",
            "path_hint": str(repo_root),
            "truth_plane": "repo_and_github",
        },
        "git": _git_metadata(repo_root, git_runner),
        "release_candidate": {
            "scope": "local_workbench_release_candidate",
            "live_linear_issue": "JER-244",
            "truth_level_impact": "none",
            "certification_claim": "none",
        },
        "required_environment": _required_environment(),
        "verification_commands": _verification_commands(),
        "workbench_maturity_snapshot": _workbench_maturity_snapshot(),
        "not_claimed_gates": _not_claimed_gates(),
        "unsupported_external_dependencies": _unsupported_external_dependencies(),
        "current_blockers": _current_blockers(),
    }


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    return []


def validate_release_manifest(manifest: JsonObject) -> list[str]:
    issues: list[str] = []
    if manifest.get("kind") != MANIFEST_KIND:
        issues.append(f"kind must be {MANIFEST_KIND!r}.")
    if manifest.get("version") != MANIFEST_VERSION:
        issues.append(f"version must be {MANIFEST_VERSION}.")
    git = manifest.get("git")
    if not isinstance(git, dict) or not git.get("sha") or not git.get("short_sha"):
        issues.append("git.sha and git.short_sha are required.")
    verification_commands = manifest.get("verification_commands")
    if not isinstance(verification_commands, list) or not verification_commands:
        issues.append("verification_commands must be a non-empty list.")
    else:
        statuses = {item.get("status") for item in verification_commands if isinstance(item, dict)}
        if "pass" not in statuses:
            issues.append("at least one verification command must record pass evidence.")
        if "blocked" not in statuses:
            issues.append("at least one verification command must record a blocked gate.")
        for item in verification_commands:
            if not isinstance(item, dict) or not item.get("id") or not item.get("command"):
                issues.append("each verification command needs id and command.")
                break
            if item.get("external_services") != []:
                issues.append(f"{item.get('id', 'unknown')} must not require external services.")
                break
    not_claimed_gates = manifest.get("not_claimed_gates")
    if not isinstance(not_claimed_gates, list) or not not_claimed_gates:
        issues.append("not_claimed_gates must be a non-empty list.")
    else:
        gate_ids = {item.get("id") for item in not_claimed_gates if isinstance(item, dict)}
        for required_gate in (
            "production_ready",
            "cloud_deployment_ready",
            "certification_ready",
            "full_strict_mypy_clean",
        ):
            if required_gate not in gate_ids:
                issues.append(f"not_claimed_gates must include {required_gate}.")
    required_environment = manifest.get("required_environment")
    if not isinstance(required_environment, dict):
        issues.append("required_environment is required.")
    elif required_environment.get("required_env_vars_for_local_release_gates") != []:
        issues.append("local release gates must not require secret environment variables.")

    maturity_snapshot = manifest.get("workbench_maturity_snapshot")
    if not isinstance(maturity_snapshot, dict):
        issues.append("workbench_maturity_snapshot is required.")
    else:
        if maturity_snapshot.get("overall_status") == "production_ready":
            issues.append("workbench_maturity_snapshot.overall_status must not claim production_ready.")
        dimensions = maturity_snapshot.get("dimensions")
        if not isinstance(dimensions, list) or not dimensions:
            issues.append("workbench_maturity_snapshot.dimensions must be a non-empty list.")
        else:
            dimension_by_id: dict[str, JsonObject] = {}
            maturity_statuses: set[str] = set()
            for item in dimensions:
                if not isinstance(item, dict) or not item.get("id") or not item.get("status") or not item.get("summary"):
                    issues.append("each workbench maturity dimension needs id, status, and summary.")
                    break
                dimension_id = str(item["id"])
                status = str(item["status"])
                dimension_by_id[dimension_id] = item
                maturity_statuses.add(status)
                if status not in REQUIRED_MATURITY_STATUSES:
                    issues.append(f"workbench_maturity_snapshot.{dimension_id} has unsupported status {status!r}.")
                if item.get("external_services") not in ([], None):
                    issues.append(f"workbench_maturity_snapshot.{dimension_id} must not require external services.")
            missing_dimensions = sorted(set(REQUIRED_MATURITY_DIMENSIONS) - set(dimension_by_id))
            if missing_dimensions:
                issues.append(
                    "workbench_maturity_snapshot is missing required dimension(s): "
                    + ", ".join(missing_dimensions)
                    + "."
                )
            for required_status in REQUIRED_MATURITY_STATUSES:
                if required_status not in maturity_statuses:
                    issues.append(f"workbench_maturity_snapshot must include {required_status!r} status evidence.")
            for dimension_id, expected_status in FIXED_MATURITY_STATUSES.items():
                actual = dimension_by_id.get(dimension_id, {}).get("status")
                if actual is not None and actual != expected_status:
                    issues.append(f"workbench_maturity_snapshot.{dimension_id} must remain {expected_status}.")

    strings = _walk_strings(manifest)
    lowered_strings = [text.lower() for text in strings]
    suspicious_literals = []
    for index, text in enumerate(strings):
        lowered = lowered_strings[index]
        if any(part in lowered for part in SENSITIVE_NAME_PARTS) and "=" in text:
            suspicious_literals.append(text)
    if suspicious_literals:
        issues.append("manifest must not embed secret-like key/value strings.")
    return issues


def validation_report(manifest: JsonObject) -> JsonObject:
    issues = validate_release_manifest(manifest)
    maturity_snapshot = manifest.get("workbench_maturity_snapshot")
    maturity_dimensions = (
        maturity_snapshot.get("dimensions", [])
        if isinstance(maturity_snapshot, dict) and isinstance(maturity_snapshot.get("dimensions"), list)
        else []
    )
    return {
        "kind": VALIDATION_KIND,
        "version": 1,
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "manifest_kind": manifest.get("kind"),
        "manifest_version": manifest.get("version"),
        "manifest_git": manifest.get("git", {}),
        "verification_command_count": len(manifest.get("verification_commands", [])),
        "not_claimed_gate_count": len(manifest.get("not_claimed_gates", [])),
        "maturity_dimension_count": len(maturity_dimensions),
    }


def render_text(manifest: JsonObject) -> str:
    git = manifest["git"]
    commands = manifest["verification_commands"]
    not_claimed = manifest["not_claimed_gates"]
    maturity_dimensions = manifest["workbench_maturity_snapshot"]["dimensions"]
    lines = [
        f"release_manifest: {manifest['kind']} v{manifest['version']}",
        f"git: {git['short_sha']} ({git['branch']})",
        f"verification_commands: {len(commands)}",
        f"maturity_dimensions: {len(maturity_dimensions)}",
        f"not_claimed_gates: {', '.join(item['id'] for item in not_claimed)}",
    ]
    for command in commands:
        lines.append(f"- {command['id']}: {command['status']} [{command['status_basis']}]")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or validate the local workbench release evidence manifest.")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the generated manifest shape and emit a validation report.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    manifest = build_release_manifest()
    if args.validate:
        report = validation_report(manifest)
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"{report['status'].upper()} release manifest validation ({report['verification_command_count']} commands)")
            for issue in report["issues"]:
                print(f"- {issue}")
        return 0 if report["status"] == "pass" else 1
    if args.format == "json":
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(render_text(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
