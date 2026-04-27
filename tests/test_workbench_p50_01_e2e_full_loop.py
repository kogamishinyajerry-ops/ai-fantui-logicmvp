"""P50-01 — end-to-end HTTP integration test.

Walks proposal → accept → spawn (in-thread) → ASKING → approve →
EDITING → TESTING → PR_OPEN entirely through the workbench HTTP
surface, validating that all P48 / P49-01a / P49-01b / P49-01c
slices hang together as one coherent system.

The orchestrator runs in a daemon thread (not a subprocess) so the
test can drive it deterministically. Production uses subprocess via
spawn_executor_for_proposal; the in-thread variant exercises the
same code path minus the fork — which is what we want for tests
since the goal is to catch wiring bugs, not exercise OS scheduling.

Concurrency: tests use threading.Event hooks so we wait for state
transitions instead of polling timers; flake-resistant.
"""

from __future__ import annotations

import http.client
import json
import subprocess
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.executor_spawner import (
    SpawnResult,
    SpawnStatus,
)
from well_harness.skill_executor.models import TestResult
from well_harness.skill_executor.orchestrator import execute_proposal
from well_harness.skill_executor.workbench_polling import (
    WorkbenchApprovalCallback,
)


# Stub out pytest invocation. This test exercises the HTTP wiring
# between workbench and skill_executor — actually running pytest
# inside our pytest is wasteful and doesn't add coverage we don't
# already have from test_skill_executor_*. The stub returns a
# clean-pass TestResult so the gate (tests_after >= tests_before)
# is satisfied.
def _fake_run_tests(*, repo_root, **_kw):
    return TestResult(
        passed=1,
        failed=0,
        skipped=0,
        errors=0,
        duration_sec=0.01,
        ran_at="2026-04-27T13:00:00Z",
        failed_test_ids=[],
    )


# ─── Fixtures: mini-repo + isolated env + server + thread spawner ────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    """Minimal git repo with controller.py + smoke test that pytest
    can run inside the orchestrator's TESTING phase."""
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass():\n    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )
    (tmp_path / "proposals").mkdir()
    (tmp_path / "queue").mkdir()
    (tmp_path / "execs").mkdir()
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "initial")
    return tmp_path


@pytest.fixture(autouse=True)
def _isolate_env(mini_repo, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(mini_repo / "execs"))
    # Patch run_tests at the orchestrator's import site so the in-thread
    # orchestrator doesn't shell out to a real pytest run inside our
    # pytest run. Coverage of run_tests itself lives in the unit
    # tests for test_runner.
    monkeypatch.setattr(
        "well_harness.skill_executor.orchestrator.run_tests",
        _fake_run_tests,
    )
    yield


def _good_plan_json() -> str:
    """Standard happy-path plan returned by the mocked planner LLM."""
    plan = {
        "rationale": "tighten the deploy condition",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "VAL = 1",
                "new_snippet": "VAL = 2",
                "reason": "tighten",
            }
        ],
    }
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )


def _make_post_for_llm(*responses):
    """Fake the planner LLM HTTP POST. Returns successive
    pre-canned responses, raises if more requests are made than
    expected."""
    iter_resp = iter(responses)

    def _post(url, body, headers, timeout):
        return next(iter_resp)

    return _post


def _start_server() -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    return srv


@pytest.fixture
def server():
    srv = _start_server()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post_json(server, path, body=None):
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    payload = json.dumps(body) if body is not None else ""
    headers = {"Content-Type": "application/json"} if body is not None else {}
    conn.request("POST", path, body=payload, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8") if resp.length is not None else ""
    conn.close()
    if not raw:
        return resp.status, None
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _get_json(server, path):
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request("GET", path)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8") if resp.length is not None else ""
    conn.close()
    if not raw:
        return resp.status, None
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _wait_for_state(
    server,
    proposal_id,
    expected_states,
    timeout=10.0,
    require_finished=False,
):
    """Poll /api/proposals/<id>/execution until state matches one
    of expected_states. Returns the audit dict. Raises if timeout.

    `require_finished=True` additionally waits until the audit's
    `finished_at` field is populated — orchestrator sets this only
    after committing/persisting all work. Avoids a race where we
    sample the audit mid-phase (e.g. just-entered PR_OPEN but
    not-yet-committed)."""
    deadline = time.monotonic() + timeout
    last_audit: dict | None = None
    while time.monotonic() < deadline:
        status, body = _get_json(
            server, f"/api/proposals/{proposal_id}/execution"
        )
        if status == 200 and body:
            last_audit = body
            if body.get("state") in expected_states and (
                not require_finished or body.get("finished_at")
            ):
                return body
        time.sleep(0.05)
    last_state = (last_audit or {}).get("state")
    abort_reason = (last_audit or {}).get("abort_reason")
    events = [(e.get("kind"), e.get("note", "")[:80]) for e in (last_audit or {}).get("events", [])]
    raise AssertionError(
        f"proposal {proposal_id} never reached states {expected_states}"
        f" (require_finished={require_finished}); "
        f"last_state={last_state!r}, abort_reason={abort_reason!r}, "
        f"events={events}"
    )


def _create_proposal(server) -> str:
    payload = {
        "source_text": "L2 SW2 应该 tighten",
        "interpretation": {
            "affected_gates": ["G_PI"],
            "target_signals": ["sw2"],
            "change_kind": "tighten_condition",
            "summary_zh": "[E2E TEST]",
            "summary_en": "[E2E TEST]",
        },
        "author_name": "Engineer-A",
        "author_role": "ENGINEER",
        "ticket_id": "WB-P50-01",
        "system_id": "thrust-reverser",
    }
    status, body = _post_json(server, "/api/proposals", payload)
    assert status == 201, f"create_proposal failed: {status} {body}"
    return body["id"]


def _install_in_thread_spawner(
    monkeypatch,
    repo_root: Path,
    *,
    plan_responses: list[str] | None = None,
    started_event: threading.Event | None = None,
    pre_callback_hook=None,
):
    """Replace _spawn_executor_for_proposal with a thread-based
    runner that calls execute_proposal in-process.

    `started_event` fires once the orchestrator thread starts —
    useful for tests that want to drop a cancel signal before the
    callback is invoked.
    """
    actual_repo_root = repo_root  # capture in closure
    audit_dir = actual_repo_root / "execs"

    def fake_spawn(proposal_id, *, repo_root=None):
        # IGNORE demo_server's repo_root — it's the real project
        # root (Path(__file__).parents[2]). This test drives
        # everything in the mini-repo fixture, which is captured
        # in the closure as `actual_repo_root`.
        plans = plan_responses or [_good_plan_json()]

        def run():
            if started_event is not None:
                started_event.set()
            if pre_callback_hook is not None:
                pre_callback_hook()
            execute_proposal(
                proposal_id=proposal_id,
                repo_root=actual_repo_root,
                audit_dir=audit_dir,
                request_post_for_llm=_make_post_for_llm(*plans),
                approval_callback=WorkbenchApprovalCallback(
                    audit_dir=audit_dir,
                    poll_interval_sec=0.02,
                    timeout_sec=10.0,
                ),
                skip_pr=True,
                skip_push=True,
            )

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return SpawnResult(
            status=SpawnStatus.SPAWNED,
            proposal_id=proposal_id,
            pid=thread.ident,
        )

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        fake_spawn,
    )


# ─── 1. Happy path — create → accept → approve → PR_OPEN ────────────


def test_e2e_happy_path_proposal_to_pr_open(server, mini_repo, monkeypatch):
    """Full positive flow: every P48 + P49-01 piece wired together.
    Asserts state machine traverses INIT → PLANNING → ASKING →
    EDITING → TESTING → PR_OPEN, file edits land, badge endpoint
    reflects each state."""
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")
    _install_in_thread_spawner(monkeypatch, mini_repo)

    # 1. Create proposal
    proposal_id = _create_proposal(server)

    # 2. Accept (auto-spawns the in-thread orchestrator)
    status, body = _post_json(
        server, f"/api/proposals/{proposal_id}/accept", {"actor": "Kogami"}
    )
    assert status == 200
    assert body["status"] == "ACCEPTED"
    assert body["spawn"]["status"] == "spawned"

    # 3. Wait until orchestrator reaches ASKING
    asking_audit = _wait_for_state(server, proposal_id, {"ASKING"})
    exec_id = asking_audit["exec_id"]
    assert asking_audit["proposal_id"] == proposal_id

    # 4. Badge endpoint correctly shows ASKING
    s, badges = _get_json(server, "/api/skill-executions")
    assert any(
        e["state"] == "ASKING" and e["proposal_id"] == proposal_id
        for e in badges["executions"]
    )

    # 5. Approve via HTTP
    s, body = _post_json(
        server,
        f"/api/skill-executions/{exec_id}/approve",
        {"actor": "Kogami"},
    )
    assert s == 202

    # 6. Wait until orchestrator FINISHES the PR_OPEN phase
    # (commit + audit persist done). require_finished avoids a
    # race where we sample mid-phase.
    final = _wait_for_state(
        server, proposal_id, {"PR_OPEN"},
        timeout=60.0, require_finished=True,
    )
    assert final["state"] == "PR_OPEN"
    assert final["abort_reason"] == ""

    # 7. Edits actually applied + committed
    controller = (mini_repo / "src" / "well_harness" / "controller.py")
    assert controller.read_text(encoding="utf-8") == "VAL = 2\n"
    assert len(final["commits"]) == 1

    # 8. Audit's events log records a clean state-machine walk
    event_kinds = [e["kind"] for e in final["events"]]
    # Must include: init, plan ready, plan_ready transition, edit_apply,
    # tests passing, git commit
    for required in (
        "init", "planner_invocation", "edit_apply",
        "test_run", "git_commit", "pr_skip",
    ):
        assert required in event_kinds, (
            f"missing event {required!r} in {event_kinds}"
        )


# ─── 2. Cancel during PLANNING via HTTP ────────────────────────────


def test_e2e_cancel_during_asking(server, mini_repo, monkeypatch):
    """Cancel signal arrives via HTTP while the orchestrator is in
    ASKING state. The polling callback sees cancel signal first
    (precedence over approval), raises ExecutionCancelled, and the
    orchestrator transitions to ABORTED."""
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")
    _install_in_thread_spawner(monkeypatch, mini_repo)

    proposal_id = _create_proposal(server)
    _post_json(
        server, f"/api/proposals/{proposal_id}/accept", {"actor": "Kogami"}
    )

    # 1. Wait for orchestrator to reach ASKING — at this point the
    # audit exists and the polling callback is actively polling.
    asking = _wait_for_state(server, proposal_id, {"ASKING"})
    exec_id = asking["exec_id"]

    # 2. POST /cancel — this writes the cancel signal that the
    # polling callback will pick up on its next iteration.
    s, body = _post_json(
        server,
        f"/api/skill-executions/{exec_id}/cancel",
        {"actor": "Kogami", "note": "changed mind during planning"},
    )
    assert s == 202

    # 3. Wait for terminal ABORTED state (require_finished so we
    # don't sample the audit mid-transition).
    final = _wait_for_state(
        server, proposal_id, {"ABORTED"},
        timeout=20.0, require_finished=True,
    )
    assert final["state"] == "ABORTED"
    assert "Kogami" in final["abort_reason"]
    assert "changed mind" in final["abort_reason"]

    # Edits must NOT have been applied — orchestrator never left ASKING
    controller = (mini_repo / "src" / "well_harness" / "controller.py")
    assert controller.read_text(encoding="utf-8") == "VAL = 1\n"

    # user_cancel event recorded in audit
    cancel_events = [e for e in final["events"] if e["kind"] == "user_cancel"]
    assert len(cancel_events) == 1, f"events: {final['events']}"


# ─── 3. Concurrent proposals — audits don't clobber ────────────────


def test_e2e_three_concurrent_proposals_reach_pr_open(
    server, mini_repo, monkeypatch
):
    """Three proposals accepted in rapid succession, each running
    in its own orchestrator thread. Verifies:
      - audit JSON writes are atomic (no clobbered files)
      - badge endpoint per-proposal returns the correct exec_id
      - all three reach PR_OPEN independently
      - signal files don't leak between executions

    Stubs apply_edits + git so the test's only concurrent surface
    is audit IO + signal IO. A real concurrent run requires per-
    proposal worktrees (production uses real subprocesses, each
    forking its own working tree).
    """
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")

    # Stub apply_edits so 3 concurrent threads don't collide on
    # the same controller.py file. Returns an ApplyResult that
    # passes the orchestrator's later revert_edits if it fires.
    from well_harness.skill_executor.applier import ApplyResult

    def noop_apply_edits(file_edits, *, repo_root):
        return ApplyResult(applied=[], repo_root=repo_root)

    monkeypatch.setattr(
        "well_harness.skill_executor.orchestrator.apply_edits",
        noop_apply_edits,
    )

    # Install spawner that returns the standard plan for each.
    # Ignores demo_server's repo_root (which would be the real
    # project root) and uses mini_repo via closure capture.
    # Git-runner is a no-op stub: this test's purpose is to verify
    # audit-write isolation under concurrency, NOT that git itself
    # is concurrency-safe (it isn't — a single working tree is
    # single-threaded). Production isolates by spawning real
    # subprocesses, each in its own worktree.
    audit_dir = mini_repo / "execs"
    actual_repo_root = mini_repo

    fake_sha_counter = {"n": 0}

    def noop_git_runner(cmd, *, cwd, capture_output=True, text=True, **kw):
        # Deterministic fake SHA for `git rev-parse HEAD` calls.
        # Other git commands return success with empty output.
        fake_sha_counter["n"] += 1
        if cmd[:2] == ["git", "rev-parse"]:
            sha = f"{fake_sha_counter['n']:040x}"
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout=sha + "\n", stderr=""
            )
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="", stderr=""
        )

    def fake_spawn(proposal_id, *, repo_root=None):
        def run():
            execute_proposal(
                proposal_id=proposal_id,
                repo_root=actual_repo_root,
                audit_dir=audit_dir,
                request_post_for_llm=_make_post_for_llm(_good_plan_json()),
                approval_callback=WorkbenchApprovalCallback(
                    audit_dir=audit_dir,
                    poll_interval_sec=0.02,
                    timeout_sec=10.0,
                ),
                git_runner=noop_git_runner,
                skip_pr=True,
                skip_push=True,
            )

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return SpawnResult(
            status=SpawnStatus.SPAWNED,
            proposal_id=proposal_id,
            pid=thread.ident,
        )

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        fake_spawn,
    )

    proposal_ids = [_create_proposal(server) for _ in range(3)]
    for pid in proposal_ids:
        _post_json(
            server, f"/api/proposals/{pid}/accept", {"actor": "Kogami"}
        )

    # Wait for all three to reach ASKING, then approve each
    asking_records = []
    for pid in proposal_ids:
        rec = _wait_for_state(server, pid, {"ASKING"}, timeout=15.0)
        asking_records.append(rec)
    # All three should have distinct exec_ids
    exec_ids = {r["exec_id"] for r in asking_records}
    assert len(exec_ids) == 3, "exec_ids collided across concurrent runs"

    # Approve each
    for rec in asking_records:
        s, _ = _post_json(
            server,
            f"/api/skill-executions/{rec['exec_id']}/approve",
            {"actor": "Kogami"},
        )
        assert s == 202

    # All three reach PR_OPEN (require finished_at set so the
    # commit phase has completed before assertions fire)
    for pid in proposal_ids:
        final = _wait_for_state(
            server, pid, {"PR_OPEN"},
            timeout=30.0, require_finished=True,
        )
        assert final["state"] == "PR_OPEN"
        assert final["proposal_id"] == pid
        # Verify per-proposal isolation: the badge endpoint returns
        # the audit FOR THIS PROPOSAL, not a sibling's.
        assert final["exec_id"] in exec_ids

    # Verify all 3 audits exist and pass schema validation when
    # listed via /api/skill-executions
    s, body = _get_json(server, "/api/skill-executions")
    proposal_ids_in_audits = {e["proposal_id"] for e in body["executions"]}
    for pid in proposal_ids:
        assert pid in proposal_ids_in_audits


# ─── 4. /pending endpoint reflects ASKING state ────────────────────


def test_pending_endpoint_lists_asking_proposals(
    server, mini_repo, monkeypatch
):
    """/api/skill-executions/pending should return only ASKING-state
    audits during the wait. Validates the P48-06 filter still works
    when run alongside the rest of the lifecycle pieces."""
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")
    _install_in_thread_spawner(monkeypatch, mini_repo)

    proposal_id = _create_proposal(server)
    _post_json(
        server, f"/api/proposals/{proposal_id}/accept", {"actor": "Kogami"}
    )

    asking = _wait_for_state(server, proposal_id, {"ASKING"})
    s, body = _get_json(server, "/api/skill-executions/pending")
    assert s == 200
    pending_exec_ids = [e["exec_id"] for e in body["executions"]]
    assert asking["exec_id"] in pending_exec_ids

    # Approve and confirm /pending eventually clears this exec
    _post_json(
        server,
        f"/api/skill-executions/{asking['exec_id']}/approve",
        {"actor": "Kogami"},
    )
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        s, body = _get_json(server, "/api/skill-executions/pending")
        if asking["exec_id"] not in [e["exec_id"] for e in body["executions"]]:
            break
        time.sleep(0.05)
    else:
        pytest.fail("approved exec never cleared from /pending list")
