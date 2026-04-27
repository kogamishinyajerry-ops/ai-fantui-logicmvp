"""P48-03 — applier: write FileEdits to disk with all-or-nothing
semantics + revert support.

Locks down the contract that the executor uses to mutate files
without leaving the working tree in a half-applied state. The
applier is purely filesystem; no git, no tests, no LLM.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from well_harness.skill_executor.applier import (
    AppliedEdit,
    ApplyError,
    ApplyResult,
    apply_edits,
    revert_edits,
)
from well_harness.skill_executor.models import FileEdit


# ─── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def workspace(tmp_path):
    """Build a tiny repo-shaped directory tree."""
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "controller.py").write_text(
        "def main():\n    if foo:\n        return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pkg" / "models.py").write_text(
        "VALUE = 42\n",
        encoding="utf-8",
    )
    return tmp_path


# ─── 1. Single-edit happy path ─────────────────────────────────────────


def test_single_edit_applies(workspace):
    edit = FileEdit(
        path="src/pkg/controller.py",
        old_snippet="if foo:",
        new_snippet="if foo and bar:",
    )
    result = apply_edits([edit], repo_root=workspace)
    text = (workspace / "src/pkg/controller.py").read_text(encoding="utf-8")
    assert "if foo and bar:" in text
    assert "if foo:" not in text
    assert len(result.applied) == 1
    assert result.applied[0].skipped is False


def test_single_edit_preserves_pre_content_for_revert(workspace):
    edit = FileEdit(
        path="src/pkg/models.py",
        old_snippet="VALUE = 42",
        new_snippet="VALUE = 99",
    )
    result = apply_edits([edit], repo_root=workspace)
    assert result.applied[0].pre_content == "VALUE = 42\n"
    assert result.applied[0].post_content == "VALUE = 99\n"


def test_revert_restores_original(workspace):
    edit = FileEdit(
        path="src/pkg/models.py",
        old_snippet="VALUE = 42",
        new_snippet="VALUE = 99",
    )
    result = apply_edits([edit], repo_root=workspace)
    revert_edits(result)
    assert (workspace / "src/pkg/models.py").read_text(encoding="utf-8") == "VALUE = 42\n"


# ─── 2. Multi-edit atomicity ──────────────────────────────────────────


def test_multi_edit_all_succeed(workspace):
    edits = [
        FileEdit(
            path="src/pkg/controller.py",
            old_snippet="if foo:",
            new_snippet="if foo and bar:",
        ),
        FileEdit(
            path="src/pkg/models.py",
            old_snippet="VALUE = 42",
            new_snippet="VALUE = 99",
        ),
    ]
    result = apply_edits(edits, repo_root=workspace)
    assert "and bar" in (workspace / "src/pkg/controller.py").read_text(encoding="utf-8")
    assert "VALUE = 99" in (workspace / "src/pkg/models.py").read_text(encoding="utf-8")
    assert len(result.applied) == 2


def test_multi_edit_atomic_rollback_on_second_failure(workspace):
    """First edit succeeds, second fails — must revert the first."""
    edits = [
        FileEdit(
            path="src/pkg/controller.py",
            old_snippet="if foo:",
            new_snippet="if foo and bar:",
        ),
        FileEdit(
            path="src/pkg/models.py",
            old_snippet="DOES_NOT_EXIST",  # will fail
            new_snippet="x",
        ),
    ]
    with pytest.raises(ApplyError):
        apply_edits(edits, repo_root=workspace)
    # First edit must have been reverted.
    text = (workspace / "src/pkg/controller.py").read_text(encoding="utf-8")
    assert "if foo:" in text
    assert "and bar" not in text
    # Second file untouched.
    text2 = (workspace / "src/pkg/models.py").read_text(encoding="utf-8")
    assert text2 == "VALUE = 42\n"


def test_multi_edit_atomic_rollback_on_first_failure(workspace):
    """If the very first edit fails, second is never attempted."""
    edits = [
        FileEdit(
            path="src/pkg/controller.py",
            old_snippet="DOES_NOT_EXIST",
            new_snippet="x",
        ),
        FileEdit(
            path="src/pkg/models.py",
            old_snippet="VALUE = 42",
            new_snippet="VALUE = 99",
        ),
    ]
    with pytest.raises(ApplyError):
        apply_edits(edits, repo_root=workspace)
    assert (workspace / "src/pkg/models.py").read_text(encoding="utf-8") == "VALUE = 42\n"


# ─── 3. old_snippet matching contract ─────────────────────────────────


def test_missing_old_snippet_raises(workspace):
    edit = FileEdit(
        path="src/pkg/models.py",
        old_snippet="this string is not in the file",
        new_snippet="x",
    )
    with pytest.raises(ApplyError) as exc:
        apply_edits([edit], repo_root=workspace)
    assert "old_snippet not found" in str(exc.value)


def test_ambiguous_old_snippet_raises(workspace):
    """If old_snippet appears more than once, the planner has to
    include more context. Refuse rather than guess."""
    (workspace / "src/pkg/dup.py").write_text("x\nx\n", encoding="utf-8")
    edit = FileEdit(
        path="src/pkg/dup.py",
        old_snippet="x",
        new_snippet="y",
    )
    with pytest.raises(ApplyError) as exc:
        apply_edits([edit], repo_root=workspace)
    assert "appears 2 times" in str(exc.value)


def test_missing_file_raises(workspace):
    edit = FileEdit(
        path="src/pkg/does_not_exist.py",
        old_snippet="a",
        new_snippet="b",
    )
    with pytest.raises(ApplyError) as exc:
        apply_edits([edit], repo_root=workspace)
    assert "does not exist" in str(exc.value)


# ─── 4. Path traversal guard ───────────────────────────────────────────


def test_path_traversal_rejected(workspace, tmp_path):
    """An edit pointing at ../ outside the repo must be rejected
    even if the resolved file would otherwise exist."""
    # Create a "neighboring" file outside the workspace.
    (tmp_path.parent / "victim.py").write_text("secret\n", encoding="utf-8")
    edit = FileEdit(
        path="../victim.py",
        old_snippet="secret",
        new_snippet="oh no",
    )
    with pytest.raises(ApplyError) as exc:
        apply_edits([edit], repo_root=workspace)
    assert "escape" in str(exc.value).lower()


# ─── 5. Idempotency ───────────────────────────────────────────────────


def test_already_applied_edit_skipped(workspace):
    """If new_snippet is already present and old_snippet absent,
    the edit is treated as already-applied — useful when an
    executor crashes mid-batch and is re-run."""
    # Manually apply the edit first.
    p = workspace / "src/pkg/models.py"
    p.write_text("VALUE = 99\n", encoding="utf-8")
    edit = FileEdit(
        path="src/pkg/models.py",
        old_snippet="VALUE = 42",
        new_snippet="VALUE = 99",
    )
    result = apply_edits([edit], repo_root=workspace)
    assert result.applied[0].skipped is True
    assert "already" in result.applied[0].skipped_reason


def test_skipped_edit_revert_is_noop(workspace):
    """Reverting a skipped edit must NOT touch the file (since the
    applier didn't either)."""
    p = workspace / "src/pkg/models.py"
    p.write_text("VALUE = 99\n", encoding="utf-8")
    edit = FileEdit(
        path="src/pkg/models.py",
        old_snippet="VALUE = 42",
        new_snippet="VALUE = 99",
    )
    result = apply_edits([edit], repo_root=workspace)
    revert_edits(result)
    # File should still have new content because the edit was a no-op
    assert p.read_text(encoding="utf-8") == "VALUE = 99\n"


# ─── 6. Empty input ───────────────────────────────────────────────────


def test_empty_edits_list_is_noop(workspace):
    result = apply_edits([], repo_root=workspace)
    assert result.applied == []


# ─── 7. Repeat edit + same target ─────────────────────────────────────


def test_two_edits_same_file_in_order(workspace):
    """Two edits to the same file should compose in order. Revert
    must walk reverse-order to restore."""
    edits = [
        FileEdit(
            path="src/pkg/controller.py",
            old_snippet="if foo:",
            new_snippet="if foo and bar:",
        ),
        FileEdit(
            path="src/pkg/controller.py",
            old_snippet="return 1",
            new_snippet="return 2",
        ),
    ]
    result = apply_edits(edits, repo_root=workspace)
    text = (workspace / "src/pkg/controller.py").read_text(encoding="utf-8")
    assert "if foo and bar:" in text
    assert "return 2" in text
    revert_edits(result)
    text = (workspace / "src/pkg/controller.py").read_text(encoding="utf-8")
    assert text == "def main():\n    if foo:\n        return 1\n"
