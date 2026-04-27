"""P49-01a — auto-spawn skill_executor on proposal ACCEPTED.

Locks down: spawn_executor_for_proposal returns the right
SpawnStatus, writes an idempotent marker, captures stdout/stderr,
and is opt-in via env var.
"""

from __future__ import annotations

import json

import pytest

from well_harness.skill_executor.executor_spawner import (
    SpawnerError,
    SpawnResult,
    SpawnStatus,
    is_auto_spawn_enabled,
    spawn_executor_for_proposal,
    spawn_log_path,
    spawn_marker_path,
)


@pytest.fixture
def fake_runner():
    """Replace subprocess.Popen with a recorder. No real fork."""

    class FakeProc:
        def __init__(self, cmd, **kw):
            self.pid = 12345
            self.cmd = cmd
            self.kwargs = kw

    captured: list[FakeProc] = []

    def runner(cmd, *, stdout, stderr, cwd, env):
        proc = FakeProc(cmd, stdout=stdout, stderr=stderr, cwd=cwd, env=env)
        captured.append(proc)
        return proc

    runner.captured = captured  # type: ignore[attr-defined]
    return runner


# ─── 1. Env-var gating ────────────────────────────────────────────────


def test_disabled_by_default(tmp_path, fake_runner, monkeypatch):
    monkeypatch.delenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", raising=False)
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
    )
    assert result.status == SpawnStatus.DISABLED
    assert not fake_runner.captured  # didn't spawn


def test_enabled_via_env(tmp_path, fake_runner, monkeypatch):
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
    )
    assert result.status == SpawnStatus.SPAWNED
    assert len(fake_runner.captured) == 1


def test_require_enabled_false_bypass(tmp_path, fake_runner, monkeypatch):
    monkeypatch.delenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", raising=False)
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert result.status == SpawnStatus.SPAWNED


@pytest.mark.parametrize(
    "val,expected",
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("nope", False),
    ],
)
def test_is_auto_spawn_enabled_variants(val, expected):
    assert (
        is_auto_spawn_enabled({"WORKBENCH_AUTO_SPAWN_EXECUTOR": val}) is expected
    )


def test_is_auto_spawn_enabled_unset():
    assert is_auto_spawn_enabled({}) is False


# ─── 2. Marker + idempotency ──────────────────────────────────────────


def test_writes_spawn_marker_with_pid_and_cmd(tmp_path, fake_runner):
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    marker = result.marker_path
    assert marker is not None and marker.is_file()
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert data["proposal_id"] == "PROP-test"
    assert data["pid"] == 12345
    assert "spawned_at" in data
    assert "execute" in data["cmd"]
    assert "PROP-test" in data["cmd"]
    assert data["log"].endswith("PROP-test.log")


def test_idempotent_second_call(tmp_path, fake_runner):
    spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    result2 = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert result2.status == SpawnStatus.ALREADY_SPAWNED
    assert len(fake_runner.captured) == 1  # no second spawn
    assert result2.pid == 12345  # reads from marker
    assert result2.marker_path is not None and result2.marker_path.is_file()


def test_different_proposals_each_get_own_marker(tmp_path, fake_runner):
    r1 = spawn_executor_for_proposal(
        "PROP-A",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    r2 = spawn_executor_for_proposal(
        "PROP-B",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert r1.status == r2.status == SpawnStatus.SPAWNED
    assert r1.marker_path != r2.marker_path
    assert len(fake_runner.captured) == 2


def test_idempotent_handles_corrupt_marker(tmp_path, fake_runner):
    """If a previous run wrote a non-JSON marker (e.g. crashed mid-write),
    the idempotency check still treats the marker as authoritative —
    we don't auto-clean. Engineer must rm the marker to retry."""
    audit_dir = tmp_path / "audits"
    audit_dir.mkdir(parents=True)
    marker = spawn_marker_path("PROP-X", audit_dir=audit_dir)
    marker.write_text("not valid json {{{", encoding="utf-8")
    result = spawn_executor_for_proposal(
        "PROP-X",
        repo_root=tmp_path,
        audit_dir=audit_dir,
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert result.status == SpawnStatus.ALREADY_SPAWNED
    assert result.pid is None  # couldn't parse
    assert not fake_runner.captured


# ─── 3. Subprocess invocation shape ──────────────────────────────────


def test_cmd_includes_module_invocation(tmp_path, fake_runner):
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    cmd = result.cmd
    assert "-m" in cmd
    assert "well_harness.skill_executor" in cmd
    assert "execute" in cmd
    assert "PROP-test" in cmd
    assert "--repo-root" in cmd
    assert "--audit-dir" in cmd


def test_extra_args_propagated(tmp_path, fake_runner):
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
        extra_args=["--skip-pr", "--skip-push"],
    )
    assert "--skip-pr" in result.cmd
    assert "--skip-push" in result.cmd


def test_python_bin_override(tmp_path, fake_runner):
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
        python_bin="/custom/python",
    )
    assert result.cmd[0] == "/custom/python"


def test_runner_receives_log_handle_for_stdout(tmp_path, fake_runner):
    spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    proc = fake_runner.captured[0]
    # stdout is the open file handle for the log
    assert hasattr(proc.kwargs["stdout"], "write")


def test_log_file_path_returned_and_in_audit_dir(tmp_path, fake_runner):
    audit_dir = tmp_path / "audits"
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=audit_dir,
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert result.log_path is not None
    assert result.log_path.name == "PROP-test.log"
    assert result.log_path.parent == audit_dir.resolve()


# ─── 4. Audit dir behavior ───────────────────────────────────────────


def test_audit_dir_created_if_missing(tmp_path, fake_runner):
    audit_dir = tmp_path / "deeper" / "nested" / "audits"
    assert not audit_dir.exists()
    spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=audit_dir,
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert audit_dir.is_dir()


def test_default_audit_dir_inside_repo(tmp_path, fake_runner):
    """When audit_dir omitted, defaults to <repo>/.planning/skill_executions."""
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    expected = (tmp_path / ".planning" / "skill_executions").resolve()
    assert result.marker_path is not None
    assert result.marker_path.parent == expected


# ─── 5. Path-helper public API ──────────────────────────────────────


def test_spawn_marker_path_helper(tmp_path):
    p = spawn_marker_path("PROP-X", audit_dir=tmp_path)
    assert p == tmp_path / "PROP-X.spawn"


def test_spawn_log_path_helper(tmp_path):
    p = spawn_log_path("PROP-X", audit_dir=tmp_path)
    assert p == tmp_path / "PROP-X.log"


# ─── 6. Errors ───────────────────────────────────────────────────────


def test_runner_oserror_raises_spawner_error(tmp_path, monkeypatch):
    def boom(cmd, **kwargs):
        raise OSError("fork failed: too many processes")

    with pytest.raises(SpawnerError) as exc:
        spawn_executor_for_proposal(
            "PROP-test",
            repo_root=tmp_path,
            audit_dir=tmp_path / "audits",
            spawn_runner=boom,
            require_enabled=False,
        )
    assert "fork failed" in str(exc.value)


# ─── 7. SpawnResult shape ────────────────────────────────────────────


def test_spawn_result_dataclass_fields(tmp_path, fake_runner):
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
        require_enabled=False,
    )
    assert isinstance(result, SpawnResult)
    assert result.proposal_id == "PROP-test"
    assert result.status == SpawnStatus.SPAWNED
    assert result.pid == 12345
    assert result.marker_path is not None
    assert result.log_path is not None
    assert result.cmd is not None


def test_disabled_result_has_explanatory_note(tmp_path, fake_runner, monkeypatch):
    monkeypatch.delenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", raising=False)
    result = spawn_executor_for_proposal(
        "PROP-test",
        repo_root=tmp_path,
        audit_dir=tmp_path / "audits",
        spawn_runner=fake_runner,
    )
    assert result.status == SpawnStatus.DISABLED
    assert "WORKBENCH_AUTO_SPAWN_EXECUTOR" in result.note
