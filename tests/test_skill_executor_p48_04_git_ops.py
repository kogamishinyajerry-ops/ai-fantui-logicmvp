"""P48-04 — git ops on a real tmp_path repo.

Locks down the executor's branch/commit/push subprocess wrappers.
Each test starts with `git init` in a tmp_path and exercises the
real git binary; push tests use a file:// remote so no network
is touched.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.git_ops import (
    GitError,
    commit_files,
    create_branch,
    current_branch,
    head_sha,
    push_branch,
)


# ─── Fixtures ──────────────────────────────────────────────────────────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def repo(tmp_path):
    """A tmp_path with `git init` + an initial commit so HEAD
    resolves and branches can fork from it."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-q", "-m", "initial commit")
    return tmp_path


@pytest.fixture
def repo_with_remote(repo, tmp_path):
    """`repo` + a sibling bare repo serving as `origin` over file://.
    Tests that need to test push without network use this fixture."""
    bare = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", "-q", str(bare)],
        check=True,
        capture_output=True,
    )
    _git(repo, "remote", "add", "origin", f"file://{bare}")
    _git(repo, "push", "-u", "origin", "main")
    return repo


# ─── 1. create_branch ─────────────────────────────────────────────────


def test_create_branch_checks_out_new_branch(repo):
    name = create_branch(repo_root=repo, branch_name="feat/exec-PROP-x-abc123")
    assert name == "feat/exec-PROP-x-abc123"
    assert current_branch(repo_root=repo) == "feat/exec-PROP-x-abc123"


def test_create_branch_rejects_unsafe_name(repo):
    with pytest.raises(GitError) as exc:
        create_branch(repo_root=repo, branch_name="bad name with spaces")
    assert "safe charset" in str(exc.value)


def test_create_branch_rejects_existing_branch(repo):
    create_branch(repo_root=repo, branch_name="dup")
    _git(repo, "checkout", "main")
    with pytest.raises(GitError) as exc:
        create_branch(repo_root=repo, branch_name="dup")
    assert exc.value.returncode != 0


# ─── 2. commit_files ──────────────────────────────────────────────────


def test_commit_files_single_file(repo):
    create_branch(repo_root=repo, branch_name="feat/x")
    p = repo / "new.py"
    p.write_text("print('hi')\n", encoding="utf-8")
    result = commit_files(
        repo_root=repo,
        files=["new.py"],
        message="feat: add new.py\n\nbody body",
    )
    assert result.sha
    assert result.message_first_line == "feat: add new.py"


def test_commit_files_multiline_message_preserved(repo):
    create_branch(repo_root=repo, branch_name="feat/multi")
    (repo / "a.py").write_text("a\n", encoding="utf-8")
    msg = "feat: multi-line\n\nThis line is in the body.\nAnother body line.\n\nExec-Id: EXEC-X"
    result = commit_files(repo_root=repo, files=["a.py"], message=msg)
    log = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    ).stdout
    assert "Exec-Id: EXEC-X" in log
    assert "Another body line." in log
    assert result.message_first_line == "feat: multi-line"


def test_commit_files_empty_list_raises(repo):
    create_branch(repo_root=repo, branch_name="feat/x")
    with pytest.raises(GitError) as exc:
        commit_files(repo_root=repo, files=[], message="x")
    assert "at least one file" in str(exc.value)


def test_commit_files_failed_add_raises(repo):
    create_branch(repo_root=repo, branch_name="feat/x")
    with pytest.raises(GitError):
        commit_files(
            repo_root=repo,
            files=["does/not/exist.py"],
            message="feat: bogus",
        )


# ─── 3. current_branch / head_sha ─────────────────────────────────────


def test_current_branch_after_create(repo):
    create_branch(repo_root=repo, branch_name="feat/y")
    assert current_branch(repo_root=repo) == "feat/y"


def test_head_sha_returns_full_sha(repo):
    sha = head_sha(repo_root=repo)
    assert len(sha) == 40
    assert all(c in "0123456789abcdef" for c in sha)


# ─── 4. push_branch ───────────────────────────────────────────────────


def test_push_branch_to_file_remote(repo_with_remote):
    create_branch(repo_root=repo_with_remote, branch_name="feat/push-test")
    (repo_with_remote / "newfile.py").write_text("x\n", encoding="utf-8")
    commit_files(
        repo_root=repo_with_remote,
        files=["newfile.py"],
        message="feat: push test",
    )
    push_branch(
        repo_root=repo_with_remote,
        branch_name="feat/push-test",
    )
    # Confirm the remote saw the push.
    proc = subprocess.run(
        ["git", "ls-remote", "origin", "feat/push-test"],
        cwd=str(repo_with_remote),
        capture_output=True,
        text=True,
    )
    assert "feat/push-test" in proc.stdout


def test_push_branch_failure_surfaces_stderr(repo):
    """No remote configured → push fails with stderr the audit can
    show."""
    create_branch(repo_root=repo, branch_name="feat/lonely")
    (repo / "file.py").write_text("x\n", encoding="utf-8")
    commit_files(
        repo_root=repo,
        files=["file.py"],
        message="feat: lonely",
    )
    with pytest.raises(GitError) as exc:
        push_branch(repo_root=repo, branch_name="feat/lonely")
    assert exc.value.stderr or exc.value.returncode != 0


# ─── 5. Custom git_runner injection (production-mode coverage) ────────


def test_create_branch_uses_injected_runner():
    captured = []

    def fake_runner(cmd, **kwargs):
        captured.append(cmd)
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="", stderr=""
        )

    create_branch(
        repo_root=Path("/fake"),
        branch_name="feat/injected",
        git_runner=fake_runner,
    )
    assert captured[0] == ["git", "checkout", "-b", "feat/injected"]
