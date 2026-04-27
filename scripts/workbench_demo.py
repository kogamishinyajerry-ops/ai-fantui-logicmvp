"""P51-03 — one-click workbench demo runner.

Walks the executor through one of four canonical scenarios so a
demo presenter can show the full pipeline with a single command:

  $ python3 scripts/workbench_demo.py --scenario nominal
  $ python3 scripts/workbench_demo.py --scenario governance-hold
  $ python3 scripts/workbench_demo.py --scenario transient-retry
  $ python3 scripts/workbench_demo.py --scenario hard-failure

Each scenario sets up a self-contained mini-repo under a tempdir,
files a canned proposal + brief, then invokes execute_proposal
with mocks tailored to drive the desired path. Real workbench HTTP
server is NOT required — the demo prints a summary so the
presenter can narrate progress while the workbench (if running on
:8002) shows the same execution in real time.

Why a script and not a pytest fixture: a presenter wants to
trigger demos from a terminal during the talk. The four
scenarios collectively exercise the four lifecycle outcomes the
audience needs to see (LANDED-equivalent · governance pause ·
retry recovery · hard fail with forensics).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SCENARIOS = ("nominal", "governance-hold", "transient-retry", "hard-failure")


def _git(repo_root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


def _make_mini_repo(tmp_root: Path) -> Path:
    """Build a fresh git repo with both namespaces present:
    `src/well_harness/controller.py` is in `logic_truth` and
    `docs/thrust_reverser/requirements_supplement.md` is in
    `requirements`. Scenarios pick the namespace they want by
    targeting the matching file."""
    repo = tmp_root / "demo_repo"
    repo.mkdir()
    (repo / "src" / "well_harness").mkdir(parents=True)
    (repo / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (repo / "docs" / "thrust_reverser").mkdir(parents=True)
    (repo / "docs" / "thrust_reverser" / "requirements_supplement.md").write_text(
        "REQ-DEMO-001: deploy threshold > 0.9\n", encoding="utf-8",
    )
    (repo / "tests").mkdir()
    (repo / "tests" / "test_smoke.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n", encoding="utf-8",
    )
    (repo / "proposals").mkdir()
    (repo / "queue").mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "demo@example")
    _git(repo, "config", "user.name", "demo")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "demo seed")
    return repo


def _file_proposal(repo: Path, *, prop_id: str, summary: str, namespaces: list[str]) -> None:
    """Drop a proposal JSON + brief markdown into the repo. The
    `namespaces` hint drives the planner's affected_namespaces
    field via the brief text — so namespace="logic_truth" trips
    the governance gate, "requirements" doesn't."""
    proposal = {
        "id": prop_id,
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "summary_zh": summary,
            "summary_en": summary,
        },
        "status": "ACCEPTED",
        "source_text": summary,
    }
    (repo / "proposals" / f"{prop_id}.json").write_text(
        json.dumps(proposal), encoding="utf-8",
    )
    brief = (
        f"# {prop_id}\n\n"
        f"summary: {summary}\n"
        f"target namespaces: {', '.join(namespaces)}\n"
    )
    (repo / "queue" / f"{prop_id}.md").write_text(brief, encoding="utf-8")


def _plan_response(*, namespaces: list[str], path: str, old: str, new: str) -> str:
    """Build a MiniMax-shaped JSON envelope carrying the plan. The
    test-injection hook returns this verbatim instead of calling
    the real LLM."""
    plan = {
        "rationale": "demo",
        "affected_namespaces": namespaces,
        "risk_assessment": {ns: "yellow" for ns in namespaces},
        "file_edits": [
            {
                "path": path,
                "old_snippet": old,
                "new_snippet": new,
                "reason": "demo",
            }
        ],
    }
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )


def _summary(label: str, result, started_at: float) -> dict:
    elapsed = time.monotonic() - started_at
    rec = result.record
    return {
        "scenario": label,
        "exec_id": rec.exec_id,
        "proposal_id": rec.proposal_id,
        "final_state": rec.state,
        "abort_reason": rec.abort_reason or "",
        "wall_clock_sec": round(elapsed, 2),
        "plan_steps_total": len(rec.plan_steps),
        "plan_steps_completed": sum(
            1 for s in rec.plan_steps if s.completed_at
        ),
        "events": [e.kind for e in rec.events][:24],
        "dry_run": getattr(rec, "dry_run", False),
        "governance_decision": (
            (rec.governance_review or {}).get("decision") if rec.governance_review else None
        ),
    }


# ─── Scenarios ────────────────────────────────────────────────────


def run_nominal(repo: Path, audit_dir: Path) -> dict:
    """Happy path: planner returns a clean plan, governance OFF
    (requirements namespace doesn't trip the gate), tests pass,
    dry_run=True so we end at DRY_RUN_COMPLETE without any push."""
    started = time.monotonic()
    prop_id = "PROP-demo-nominal"
    _file_proposal(
        repo, prop_id=prop_id,
        summary="修改参数 deploy threshold to 0.95",
        namespaces=["requirements"],
    )
    body = _plan_response(
        namespaces=["requirements"],
        path="docs/thrust_reverser/requirements_supplement.md",
        old="threshold > 0.9",
        new="threshold > 0.95",
    )
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id=prop_id,
        repo_root=repo,
        audit_dir=audit_dir,
        auto_approve=True,
        request_post_for_llm=lambda *a, **kw: body,
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    return _summary("nominal", result, started)


def run_governance_hold(repo: Path, audit_dir: Path) -> dict:
    """Governance-required path: namespace=logic_truth trips the
    gate. We auto-approve so the run continues to completion."""
    started = time.monotonic()
    prop_id = "PROP-demo-governance"
    _file_proposal(
        repo, prop_id=prop_id,
        summary="修改 logic_truth 真值表门 G7",
        namespaces=["logic_truth"],
    )
    body = _plan_response(
        namespaces=["logic_truth"],
        path="src/well_harness/controller.py",
        old="VAL = 1",
        new="VAL = 3",
    )
    os.environ["WORKBENCH_GOVERNANCE_ENABLED"] = "1"
    try:
        from well_harness.skill_executor.orchestrator import execute_proposal
        result = execute_proposal(
            proposal_id=prop_id,
            repo_root=repo,
            audit_dir=audit_dir,
            auto_approve=True,
            auto_approve_governance=True,
            request_post_for_llm=lambda *a, **kw: body,
            skip_pr=True,
            skip_push=True,
            sleep_fn=lambda _s: None,
            dry_run=True,
        )
    finally:
        os.environ.pop("WORKBENCH_GOVERNANCE_ENABLED", None)
    return _summary("governance-hold", result, started)


def run_transient_retry(repo: Path, audit_dir: Path) -> dict:
    """Planner LLM returns a transient error on the first attempt
    then a valid plan on the second. The retry loop recovers and
    the run completes."""
    started = time.monotonic()
    prop_id = "PROP-demo-transient"
    _file_proposal(
        repo, prop_id=prop_id,
        summary="加测试 cover edge case",
        namespaces=["requirements"],
    )
    body = _plan_response(
        namespaces=["requirements"],
        path="docs/thrust_reverser/requirements_supplement.md",
        old="threshold > 0.9",
        new="threshold > 0.97",
    )
    call_count = {"n": 0}

    def flaky_post(*a, **kw):
        call_count["n"] += 1
        if call_count["n"] == 1:
            from well_harness.skill_executor.llm_client import (
                LLMUnavailableError,
            )
            raise LLMUnavailableError("simulated transient 503")
        return body

    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id=prop_id,
        repo_root=repo,
        audit_dir=audit_dir,
        auto_approve=True,
        request_post_for_llm=flaky_post,
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        max_planner_retries=3,
        planner_retry_delay_sec=0.0,
        dry_run=True,
    )
    out = _summary("transient-retry", result, started)
    out["llm_calls_made"] = call_count["n"]
    return out


def run_hard_failure(repo: Path, audit_dir: Path) -> dict:
    """Hard-failure path: plan references a snippet that doesn't
    exist in the file → applier raises ApplyError → run ends in
    FAILED. Caller can download the forensics bundle for triage."""
    started = time.monotonic()
    prop_id = "PROP-demo-fail"
    _file_proposal(
        repo, prop_id=prop_id,
        summary="修复 bug intentional fail",
        namespaces=["requirements"],
    )
    body = _plan_response(
        namespaces=["requirements"],
        path="docs/thrust_reverser/requirements_supplement.md",
        old="DOES_NOT_EXIST_IN_FILE",
        new="x",
    )
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id=prop_id,
        repo_root=repo,
        audit_dir=audit_dir,
        auto_approve=True,
        request_post_for_llm=lambda *a, **kw: body,
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    return _summary("hard-failure", result, started)


SCENARIO_DISPATCH = {
    "nominal": run_nominal,
    "governance-hold": run_governance_hold,
    "transient-retry": run_transient_retry,
    "hard-failure": run_hard_failure,
}


def run_scenario(name: str, *, keep_workspace: bool = False) -> dict:
    """Build a fresh workspace, run one scenario, return the summary
    dict. When keep_workspace=True the tempdir is left on disk so
    the presenter can browse the audit JSON afterwards."""
    if name not in SCENARIO_DISPATCH:
        raise ValueError(
            f"unknown scenario: {name!r}; choose from {sorted(SCENARIOS)}"
        )
    tmp_root = Path(tempfile.mkdtemp(prefix="workbench-demo-"))
    try:
        repo = _make_mini_repo(tmp_root)
        audit_dir = tmp_root / "execs"
        os.environ["WORKBENCH_PROPOSALS_DIR"] = str(repo / "proposals")
        os.environ["WORKBENCH_DEV_QUEUE_DIR"] = str(repo / "queue")
        os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"] = str(audit_dir)
        os.environ.setdefault("MINIMAX_API_KEY", "demo-fake-key")
        out = SCENARIO_DISPATCH[name](repo, audit_dir)
        out["workspace"] = str(tmp_root)
        return out
    finally:
        if not keep_workspace:
            shutil.rmtree(tmp_root, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario", choices=SCENARIOS, default="nominal",
        help="which lifecycle path to walk through",
    )
    parser.add_argument(
        "--keep-workspace", action="store_true",
        help="don't clean up the tempdir on exit",
    )
    args = parser.parse_args(argv)
    summary = run_scenario(
        args.scenario, keep_workspace=args.keep_workspace,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    # Exit code: 0 for any reachable terminal state. Hard-failure
    # is a SUCCESSFUL demo of the failure path, so we don't want
    # the script to red-light when it ends in FAILED.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
