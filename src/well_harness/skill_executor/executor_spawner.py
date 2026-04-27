"""Auto-spawn skill_executor on proposal ACCEPTED.

P49-01a (2026-04-27): closes the trigger loop. Before this slice,
the engineer had to manually run

    python3 -m well_harness.skill_executor execute PROP-XXX

after accepting a proposal in the workbench. Now the workbench's
accept endpoint hands off automatically.

Design
------
Spawning is **opt-in** via WORKBENCH_AUTO_SPAWN_EXECUTOR=1. Default
OFF so existing dev workflows don't break. When enabled, on each
OPEN→ACCEPTED transition the demo_server invokes
spawn_executor_for_proposal which:

  1. Checks for `<audit_dir>/<proposal_id>.spawn` marker; if it
     exists, returns ALREADY_SPAWNED (idempotent retry).
  2. Otherwise launches the skill_executor CLI as a detached
     subprocess (start_new_session=True) so it survives demo_server
     restart.
  3. Redirects stdout+stderr to `<audit_dir>/<proposal_id>.log`
     for postmortem debugging.
  4. Atomically writes the spawn marker (pid, cmd, timestamp).

What this does NOT do (deferred to later slices):
  - Track child PID liveness — if the child dies the marker stays.
    Engineer runs `rm <marker>` to retry.
  - Concurrency limits — every ACCEPTED proposal spawns its own
    process. P49-01a is the happy single-execution path.
  - Auto-cleanup of stale markers on demo_server restart.

Why opt-in: spawning a child process from a web request handler
is a meaningful behavior change. Explicit env var means an
operator who hasn't read the runbook doesn't get surprised by
concurrent executor processes piling up.
"""

from __future__ import annotations

import dataclasses
import enum
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from well_harness.skill_executor.errors import SkillExecutorError


class SpawnerError(SkillExecutorError):
    """Raised when spawn fails for a reason that should bubble back
    to the caller (e.g. audit_dir unwritable, OS-level fork error).
    Idempotency hits don't raise — they return
    SpawnStatus.ALREADY_SPAWNED."""


class SpawnStatus(str, enum.Enum):
    SPAWNED = "spawned"
    ALREADY_SPAWNED = "already_spawned"
    DISABLED = "disabled"


@dataclasses.dataclass
class SpawnResult:
    status: SpawnStatus
    proposal_id: str
    pid: int | None = None
    marker_path: Path | None = None
    log_path: Path | None = None
    cmd: list[str] | None = None
    note: str = ""


_AUTO_SPAWN_ENV_VAR = "WORKBENCH_AUTO_SPAWN_EXECUTOR"


def is_auto_spawn_enabled(env: dict[str, str] | None = None) -> bool:
    """True iff the env var is set to a recognized truthy value."""
    env = env if env is not None else os.environ
    return env.get(_AUTO_SPAWN_ENV_VAR, "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def spawn_marker_path(proposal_id: str, *, audit_dir: Path) -> Path:
    return Path(audit_dir) / f"{proposal_id}.spawn"


def spawn_log_path(proposal_id: str, *, audit_dir: Path) -> Path:
    return Path(audit_dir) / f"{proposal_id}.log"


def _default_spawn_runner(cmd, *, stdout, stderr, cwd, env):
    return subprocess.Popen(
        cmd,
        stdout=stdout,
        stderr=stderr,
        cwd=cwd,
        env=env,
        start_new_session=True,
    )


def spawn_executor_for_proposal(
    proposal_id: str,
    *,
    repo_root: Path,
    audit_dir: Path | None = None,
    python_bin: str | None = None,
    extra_args: list[str] | None = None,
    env: dict[str, str] | None = None,
    spawn_runner: Callable | None = None,
    require_enabled: bool = True,
) -> SpawnResult:
    """Spawn skill_executor for an ACCEPTED proposal.

    Returns a SpawnResult; caller decides whether to log/raise/ignore
    based on `status`. Caller MUST already have transitioned the
    proposal to ACCEPTED — this function does not check proposal
    state (separation of concerns: workbench owns lifecycle).

    Parameters
    ----------
    proposal_id : str
    repo_root : Path
    audit_dir : Path | None
        Defaults to <repo_root>/.planning/skill_executions.
    python_bin : str | None
        Override sys.executable (useful for venv tests).
    extra_args : list[str] | None
        Appended to the CLI invocation. e.g. ["--skip-pr"].
    env : dict | None
        Environment for the child. Defaults to os.environ.
    spawn_runner : callable | None
        Inject a fake for tests. Default = subprocess.Popen.
    require_enabled : bool
        If True (default), respects WORKBENCH_AUTO_SPAWN_EXECUTOR.
        Tests pass False to bypass the env-var gate.
    """
    env_dict = env if env is not None else dict(os.environ)

    if require_enabled and not is_auto_spawn_enabled(env_dict):
        return SpawnResult(
            status=SpawnStatus.DISABLED,
            proposal_id=proposal_id,
            note=f"{_AUTO_SPAWN_ENV_VAR} not set",
        )

    repo_root = Path(repo_root).resolve()
    audit_dir = (
        Path(audit_dir).resolve()
        if audit_dir is not None
        else repo_root / ".planning" / "skill_executions"
    )
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SpawnerError(
            f"audit_dir {audit_dir} not creatable: {exc}"
        ) from exc

    marker = spawn_marker_path(proposal_id, audit_dir=audit_dir)
    log = spawn_log_path(proposal_id, audit_dir=audit_dir)

    if marker.exists():
        existing: dict = {}
        try:
            existing = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
        return SpawnResult(
            status=SpawnStatus.ALREADY_SPAWNED,
            proposal_id=proposal_id,
            pid=existing.get("pid"),
            marker_path=marker,
            log_path=log,
            note=f"spawn marker exists at {marker}",
        )

    cmd = [
        python_bin or sys.executable,
        "-m", "well_harness.skill_executor",
        "execute", proposal_id,
        "--repo-root", str(repo_root),
        "--audit-dir", str(audit_dir),
    ]
    if extra_args:
        cmd.extend(extra_args)

    runner = spawn_runner or _default_spawn_runner
    log_handle = open(log, "ab", buffering=0)
    try:
        proc = runner(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(repo_root),
            env=env_dict,
        )
    except OSError as exc:
        log_handle.close()
        raise SpawnerError(
            f"failed to spawn executor for {proposal_id!r}: {exc}"
        ) from exc

    pid = getattr(proc, "pid", None)
    marker_data = {
        "proposal_id": proposal_id,
        "pid": pid,
        "spawned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cmd": cmd,
        "log": str(log),
    }
    tmp = marker.with_suffix(".spawn.tmp")
    tmp.write_text(
        json.dumps(marker_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, marker)

    return SpawnResult(
        status=SpawnStatus.SPAWNED,
        proposal_id=proposal_id,
        pid=pid,
        marker_path=marker,
        log_path=log,
        cmd=cmd,
    )
