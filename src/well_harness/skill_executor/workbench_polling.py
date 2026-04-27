"""Polling-based approval callback — bridges the CLI executor to
the workbench UI per Q4(b) + Q-sub (i) (2026-04-27).

How it works:
  1. CLI starts execute_proposal(...).
  2. orchestrator reaches ASKING state, calls our callback.
  3. We poll the file `<audit_dir>/<exec_id>.approval` once per
     second.
  4. Workbench UI shows the user the pending ask. They click
     Approve/Reject; demo_server writes the file with content
     `approved` or `rejected`.
  5. Callback reads + deletes the file, returns the matching
     AskResponse.
  6. CLI process continues.

Why a file (not direct HTTP polling): CLI and HTTP server are
separate processes. A file in the audit dir is the smallest
inter-process channel that works without coordinating ports/auth.
Tests can write the file directly without spinning up a server.

Default timeout: 60 minutes. After that the callback raises so
the orchestrator can transition to FAILED with abort_reason
"approval timed out".
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.models import Ask, AskResponse, ExecutionRecord


_VALID_RESPONSES = {"approved", "rejected"}


class ApprovalTimeoutError(SkillExecutorError):
    """The poll loop hit the timeout without seeing a signal
    file. The orchestrator catches this via its top-level
    exception handler and records FAILED with abort_reason."""


def approval_signal_path(*, audit_dir: Path, exec_id: str) -> Path:
    """Canonical signal-file path for an exec_id. Lives next to
    the audit JSON so a glance at the audit dir tells you both
    'what happened' (audit) and 'what's pending' (signal)."""
    return Path(audit_dir) / f"{exec_id}.approval"


def write_approval_signal(
    *,
    audit_dir: Path,
    exec_id: str,
    response: str,
) -> None:
    """Write `approved` or `rejected` to the signal file. Used by
    demo_server when the user clicks the workbench button.

    Atomic via tmp+rename so a partial write can't be misread by
    a polling callback that happens to look between the open and
    the flush.
    """
    if response not in _VALID_RESPONSES:
        raise SkillExecutorError(
            f"invalid response {response!r}; must be one of "
            f"{sorted(_VALID_RESPONSES)}"
        )
    target = approval_signal_path(audit_dir=audit_dir, exec_id=exec_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".approval.tmp")
    tmp.write_text(response, encoding="utf-8")
    os.replace(tmp, target)


def read_and_clear_approval(
    *,
    audit_dir: Path,
    exec_id: str,
) -> str | None:
    """Atomically take the signal: read it, delete it, return
    contents. Returns None if no signal present.

    Reading and clearing in one shot means a stale signal from a
    previous run can't accidentally approve the next one.
    """
    target = approval_signal_path(audit_dir=audit_dir, exec_id=exec_id)
    if not target.is_file():
        return None
    try:
        text = target.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    try:
        target.unlink()
    except OSError:
        pass
    if text not in _VALID_RESPONSES:
        return None
    return text


class WorkbenchApprovalCallback:
    """Callable matching orchestrator's ApprovalCallback signature.

    Usage:

        callback = WorkbenchApprovalCallback(
            audit_dir=audit_dir,
            poll_interval_sec=1.0,
            timeout_sec=3600,
        )
        result = execute_proposal(
            proposal_id=...,
            repo_root=...,
            audit_dir=audit_dir,
            approval_callback=callback,
        )
    """

    def __init__(
        self,
        *,
        audit_dir: Path,
        poll_interval_sec: float = 1.0,
        timeout_sec: float = 3600.0,
        sleep: Callable[[float], None] | None = None,
        now: Callable[[], float] | None = None,
    ) -> None:
        self.audit_dir = Path(audit_dir)
        self.poll_interval_sec = poll_interval_sec
        self.timeout_sec = timeout_sec
        self._sleep = sleep or time.sleep
        self._now = now or time.monotonic

    def __call__(
        self,
        record: ExecutionRecord,
        ask: Ask,
    ) -> AskResponse:
        """Block until the workbench writes a signal file for this
        exec_id, OR raise ApprovalTimeoutError after timeout.

        Each poll iteration calls read_and_clear_approval; the
        first non-None return wins.
        """
        deadline = self._now() + self.timeout_sec
        while True:
            response = read_and_clear_approval(
                audit_dir=self.audit_dir,
                exec_id=record.exec_id,
            )
            if response == "approved":
                return AskResponse.APPROVED
            if response == "rejected":
                return AskResponse.REJECTED
            if self._now() >= deadline:
                raise ApprovalTimeoutError(
                    f"no approval signal for {record.exec_id} after "
                    f"{self.timeout_sec}s"
                )
            self._sleep(self.poll_interval_sec)
