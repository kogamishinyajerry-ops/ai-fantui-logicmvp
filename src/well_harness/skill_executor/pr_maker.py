"""PR maker — `gh pr create` wrapper that stamps the PR body
with the EXEC-id audit trail block.

The stamp is the contract the P48-05 GitHub Action will look for:

    ---
    Exec-Id: EXEC-20260427T120000123456-abc123
    Audit: .planning/skill_executions/EXEC-20260427T120000123456-abc123.json
    Proposal: PROP-20260426T075902988411-e27a6e
    Skill-Executor-Version: 0.1.0

The Action parses these lines, locates the audit file, validates
the schema, and refuses to merge if anything's amiss. So this
module doesn't just open a PR — it produces the PR shape
downstream defenses depend on.
"""

from __future__ import annotations

import dataclasses
import re
import subprocess
from typing import Callable

from well_harness.skill_executor.errors import SkillExecutorError


class PRMakerError(SkillExecutorError):
    """gh pr create failed. Stderr captured for the audit."""

    def __init__(self, message: str, *, returncode: int = 0, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


GhRunner = Callable[..., subprocess.CompletedProcess]

# Block format ⇆ parser. Any change here must update both the
# stamp builder (build_exec_stamp) and the parser
# (parse_exec_stamp) in lockstep.
EXEC_STAMP_DELIMITER = "---"
_EXEC_STAMP_LINE_KEYS = (
    "Exec-Id",
    "Audit",
    "Proposal",
    "Skill-Executor-Version",
)


@dataclasses.dataclass
class PRDetails:
    """Outcome of open_pr — the URL that gh returned + the body
    actually posted (so the audit log can capture the verbatim
    text)."""

    url: str
    body: str


def build_exec_stamp(
    *,
    exec_id: str,
    proposal_id: str,
    audit_path: str,
    executor_version: str,
) -> str:
    """Return the trailing PR-body block the P48-05 gate parses.

    Format:
        ---
        Exec-Id: EXEC-...
        Audit: .planning/skill_executions/EXEC-...json
        Proposal: PROP-...
        Skill-Executor-Version: 0.1.0
    """
    lines = [
        EXEC_STAMP_DELIMITER,
        f"Exec-Id: {exec_id}",
        f"Audit: {audit_path}",
        f"Proposal: {proposal_id}",
        f"Skill-Executor-Version: {executor_version}",
    ]
    return "\n".join(lines)


def parse_exec_stamp(body: str) -> dict | None:
    """Extract the EXEC-id stamp from a PR body. Returns a dict
    with the keys (`exec_id`, `audit`, `proposal`,
    `skill_executor_version`) on success, None if no stamp present
    or malformed.

    The CI gate uses this to find the audit file path; this
    function is the canonical parser, so keep it the only one.
    """
    if not isinstance(body, str):
        return None
    # Locate the LAST `---` followed by stamp keys (PRs may have
    # other `---` lines used as section separators).
    parts = body.rsplit(EXEC_STAMP_DELIMITER, 1)
    if len(parts) != 2:
        return None
    tail = parts[1]
    out: dict[str, str] = {}
    for line in tail.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9-]*)\s*:\s*(.+)$", line)
        if not m:
            continue
        out[m.group(1)] = m.group(2).strip()
    if not all(k in out for k in _EXEC_STAMP_LINE_KEYS):
        return None
    return {
        "exec_id": out["Exec-Id"],
        "audit": out["Audit"],
        "proposal": out["Proposal"],
        "skill_executor_version": out["Skill-Executor-Version"],
    }


def open_pr(
    *,
    repo_root,
    title: str,
    body: str,
    head: str,
    base: str = "main",
    draft: bool = False,
    gh_runner: GhRunner | None = None,
) -> PRDetails:
    """Run `gh pr create` and return PRDetails with the URL.

    `body` should already include the exec stamp (caller's
    responsibility — usually built via build_exec_stamp).

    Raises PRMakerError on gh failure.
    """
    runner = gh_runner or _default_runner

    cmd = [
        "gh", "pr", "create",
        "--title", title,
        "--body-file", "-",
        "--head", head,
        "--base", base,
    ]
    if draft:
        cmd.append("--draft")

    proc = runner(
        cmd,
        cwd=str(repo_root),
        input=body,
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    if proc.returncode != 0:
        raise PRMakerError(
            f"gh pr create failed (exit {proc.returncode})",
            returncode=proc.returncode,
            stderr=proc.stderr or proc.stdout,
        )

    # gh prints the new PR URL on its last line of stdout.
    url = ""
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("https://github.com/") and "/pull/" in line:
            url = line
            break
    if not url:
        raise PRMakerError(
            f"gh pr create succeeded but no PR URL parsed from stdout: "
            f"{proc.stdout[:200]!r}"
        )
    return PRDetails(url=url, body=body)


# ─── Internals ────────────────────────────────────────────────────────


def _default_runner(
    cmd: list[str],
    *,
    cwd: str,
    input: str | None = None,
    capture_output: bool = False,
    text: bool = False,
    timeout: float = 60.0,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        input=input,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
    )
