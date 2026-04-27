"""Git operations — subprocess wrappers for the executor's
branch / commit / push needs.

Why subprocess and not a library (gitpython, dulwich): zero new
dependencies, transparent behavior, easy to test by injecting a
fake `git_runner`.

What this module does NOT do:
  - Resolve merge conflicts (the executor's plan is supposed to
    be conflict-free against main; if it isn't, we abort)
  - Force-push (refused; would clobber upstream history)
  - --no-verify (refused; if a hook fails, that's signal)
  - Push to remotes other than `origin` (out of scope; configurable
    later if needed)
"""

from __future__ import annotations

import dataclasses
import os
import re
import subprocess
from pathlib import Path
from typing import Callable

from well_harness.skill_executor.errors import SkillExecutorError


class GitError(SkillExecutorError):
    """A git command exited non-zero. The error carries the stderr
    so a human reading the audit can see what broke."""

    def __init__(self, message: str, *, returncode: int = 0, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


# Type alias — `git_runner(cmd, cwd) -> CompletedProcess` is the
# injection point for tests.
GitRunner = Callable[..., subprocess.CompletedProcess]

_BRANCH_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._/\-]+$")


@dataclasses.dataclass
class CommitResult:
    """One commit's identifying info."""

    sha: str
    message_first_line: str


def create_branch(
    *,
    repo_root: Path,
    branch_name: str,
    git_runner: GitRunner | None = None,
) -> str:
    """Create + check out a new branch from current HEAD. Returns
    the branch name. Raises GitError if branch already exists or
    git is unavailable.

    Branch name validated against a conservative charset
    (alphanumerics + `._/-`). Slashes allowed for the
    `feat/exec-PROP-XXX-...` convention; anything weirder
    refused.
    """
    if not _BRANCH_NAME_PATTERN.match(branch_name):
        raise GitError(
            f"branch name {branch_name!r} contains characters outside "
            f"the safe charset [A-Za-z0-9._/-]"
        )
    runner = git_runner or _default_runner
    proc = runner(
        ["git", "checkout", "-b", branch_name],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(
            f"git checkout -b {branch_name!r} failed",
            returncode=proc.returncode,
            stderr=proc.stderr or proc.stdout,
        )
    return branch_name


def commit_files(
    *,
    repo_root: Path,
    files: list[str],
    message: str,
    git_runner: GitRunner | None = None,
) -> CommitResult:
    """Stage the named files (relative to repo_root) and commit
    them with `message`. Returns CommitResult with the new HEAD
    SHA. Raises GitError on add or commit failure.

    The message is passed via `git commit -F -` from stdin so
    multi-line, special-char-containing messages survive intact.

    --no-verify is NOT used; if a pre-commit hook fails, the
    executor honors that and aborts. Hooks are signal.
    """
    runner = git_runner or _default_runner

    if not files:
        raise GitError("commit_files requires at least one file")

    # Stage each named file.
    add_proc = runner(
        ["git", "add", "--", *files],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if add_proc.returncode != 0:
        raise GitError(
            f"git add failed for {files!r}",
            returncode=add_proc.returncode,
            stderr=add_proc.stderr or add_proc.stdout,
        )

    # Commit with the message via stdin.
    commit_proc = runner(
        ["git", "commit", "-F", "-"],
        cwd=str(repo_root),
        input=message,
        capture_output=True,
        text=True,
    )
    if commit_proc.returncode != 0:
        raise GitError(
            "git commit failed",
            returncode=commit_proc.returncode,
            stderr=commit_proc.stderr or commit_proc.stdout,
        )

    # Get the new HEAD SHA.
    sha_proc = runner(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if sha_proc.returncode != 0:
        raise GitError(
            "git rev-parse HEAD failed after commit",
            returncode=sha_proc.returncode,
            stderr=sha_proc.stderr,
        )
    sha = (sha_proc.stdout or "").strip()
    first_line = message.split("\n", 1)[0] if message else ""
    return CommitResult(sha=sha, message_first_line=first_line)


def push_branch(
    *,
    repo_root: Path,
    branch_name: str,
    remote: str = "origin",
    git_runner: GitRunner | None = None,
) -> None:
    """Push the current branch to `remote` with `-u` (set upstream).
    Refuses --force; if upstream has diverged, the push fails and
    the executor aborts.

    Tests pass a `git_runner` that points at a file:// remote so
    no network is touched.
    """
    runner = git_runner or _default_runner
    proc = runner(
        ["git", "push", "-u", remote, branch_name],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(
            f"git push -u {remote} {branch_name} failed",
            returncode=proc.returncode,
            stderr=proc.stderr or proc.stdout,
        )


def current_branch(
    *,
    repo_root: Path,
    git_runner: GitRunner | None = None,
) -> str:
    """Return the name of the currently-checked-out branch.
    Empty string if detached HEAD."""
    runner = git_runner or _default_runner
    proc = runner(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(
            "git rev-parse --abbrev-ref HEAD failed",
            returncode=proc.returncode,
            stderr=proc.stderr,
        )
    name = (proc.stdout or "").strip()
    if name == "HEAD":
        return ""
    return name


def head_sha(
    *,
    repo_root: Path,
    git_runner: GitRunner | None = None,
) -> str:
    """Full SHA of HEAD."""
    runner = git_runner or _default_runner
    proc = runner(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(
            "git rev-parse HEAD failed",
            returncode=proc.returncode,
            stderr=proc.stderr,
        )
    return (proc.stdout or "").strip()


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
    """Default subprocess wrapper. Tests pass their own runner
    that may capture commands without invoking git."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        input=input,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
        env=_clean_env(),
    )


def _clean_env() -> dict:
    """Strip env vars that could confuse git (e.g. GIT_DIR set by
    a test fixture for a different repo). Inherit everything else
    so user creds / SSH agent still work."""
    bad_keys = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}
    return {k: v for k, v in os.environ.items() if k not in bad_keys}
