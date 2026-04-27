"""Edit applier — write FileEdits to disk with all-or-nothing
semantics + revert support.

The applier owns "what does it mean to apply a plan to the working
tree". It does NOT own git (that's P48-04) — files are modified in
place; the caller wraps the result in a commit if the test gate
passes.

Critical invariants:

  1. **Atomic across edits**: if any edit in the batch fails (file
     missing, snippet doesn't match, OS error), every edit applied
     so far is reverted before the error is raised. The working
     tree returns to its pre-batch state.

  2. **Snapshot-based revert**: pre-edit content is read fully into
     memory and stored on the AppliedEdit record so revert is just
     `path.write_text(snapshot)`. If snapshot capture fails (e.g.
     read permission), the whole batch is rejected before any
     write happens.

  3. **Idempotency**: if a file already contains `new_snippet`
     literally and does NOT contain `old_snippet`, the edit is
     marked SKIPPED (presumed already applied) — useful when an
     executor crashes mid-batch and is re-run.

  4. **No git, no tests**: this module just modifies files. The
     test gate (gate.py) and the PR pipeline (P48-04) are
     orthogonal.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.models import FileEdit


class ApplyError(SkillExecutorError):
    """An edit could not be applied. The applier has already
    reverted any partial state. The error message names the
    specific edit + the failure mode."""


@dataclasses.dataclass
class AppliedEdit:
    """One successfully-applied (or deliberately-skipped) edit
    plus everything we'd need to revert it."""

    edit: FileEdit
    abs_path: Path
    pre_content: str          # Snapshot before write — None if skipped
    post_content: str         # Content after write
    skipped: bool = False     # True if new_snippet was already present
    skipped_reason: str = ""


@dataclasses.dataclass
class ApplyResult:
    """Outcome of apply_edits() — list of applied edits in the
    order they were attempted, plus the original repo root the
    applier was rooted at. revert_edits(result) puts the working
    tree back."""

    applied: list[AppliedEdit]
    repo_root: Path


def apply_edits(
    edits: list[FileEdit],
    *,
    repo_root: Path,
) -> ApplyResult:
    """Apply each FileEdit to the working tree under `repo_root`.

    On any failure: revert every successful edit done so far + raise
    ApplyError. The resulting state is "exactly as before the call".

    Returns an ApplyResult on full success. Caller persists the
    result to the audit log + can call revert_edits(result) later
    to put the tree back (e.g. if the test gate fails downstream).

    Empty `edits` list is a no-op success — useful for revert
    proposals where the planner declared no edits (which itself
    would have been rejected by P48-02's "file_edits cannot be
    empty" validator, but defensive).
    """
    if not isinstance(repo_root, Path):
        repo_root = Path(repo_root)
    repo_root = repo_root.resolve()

    applied: list[AppliedEdit] = []
    for edit in edits:
        try:
            applied.append(_apply_single(edit, repo_root=repo_root))
        except ApplyError:
            # Roll back what we've done so far before re-raising.
            _revert_list(applied)
            raise
        except OSError as exc:
            _revert_list(applied)
            raise ApplyError(
                f"OS error applying edit to {edit.path!r}: {exc}"
            ) from exc
    return ApplyResult(applied=applied, repo_root=repo_root)


def revert_edits(result: ApplyResult) -> None:
    """Restore every applied edit's file to its pre-edit content.
    Skipped edits are no-ops (they didn't change the file in the
    first place).

    Best-effort: if a single revert fails (e.g. file deleted by
    something else), continue trying the rest. The caller should
    consider the working tree dirty in that case and bail to git.
    """
    _revert_list(result.applied)


# ─── Internals ────────────────────────────────────────────────────────


def _apply_single(edit: FileEdit, *, repo_root: Path) -> AppliedEdit:
    abs_path = (repo_root / edit.path).resolve()
    # Path traversal guard — the resolved path must still live
    # under repo_root. Without this, an edit like "../../etc/passwd"
    # could escape the workspace.
    try:
        abs_path.relative_to(repo_root)
    except ValueError as exc:
        raise ApplyError(
            f"edit path {edit.path!r} escapes repo root "
            f"({abs_path}): {exc}"
        ) from exc

    if not abs_path.is_file():
        raise ApplyError(
            f"file does not exist: {edit.path!r} "
            f"(resolved to {abs_path})"
        )
    pre_content = abs_path.read_text(encoding="utf-8")

    # Idempotency: if new_snippet already present AND old_snippet
    # absent, treat as already-applied.
    if edit.old_snippet not in pre_content and edit.new_snippet in pre_content:
        return AppliedEdit(
            edit=edit,
            abs_path=abs_path,
            pre_content=pre_content,
            post_content=pre_content,
            skipped=True,
            skipped_reason="new_snippet already present, old_snippet absent",
        )

    # Strict-match contract: old_snippet must appear verbatim. We
    # don't do fuzzy match — if the planner can't produce an exact
    # match, the planner's prompt or context is the bug.
    if edit.old_snippet not in pre_content:
        raise ApplyError(
            f"old_snippet not found in {edit.path!r}; the planner's "
            f"context for this file may be stale or wrong. "
            f"old_snippet[:60] = {edit.old_snippet[:60]!r}"
        )

    occurrences = pre_content.count(edit.old_snippet)
    if occurrences > 1:
        raise ApplyError(
            f"old_snippet appears {occurrences} times in {edit.path!r}; "
            f"applier requires unique matches. The planner should "
            f"include enough surrounding context to disambiguate."
        )

    post_content = pre_content.replace(edit.old_snippet, edit.new_snippet, 1)
    abs_path.write_text(post_content, encoding="utf-8")
    return AppliedEdit(
        edit=edit,
        abs_path=abs_path,
        pre_content=pre_content,
        post_content=post_content,
        skipped=False,
    )


def _revert_list(applied: list[AppliedEdit]) -> None:
    # Walk in reverse so the most recent change goes back first —
    # if two edits touched the same file, this keeps invariants
    # closer to "the file was X before any edit ran".
    for entry in reversed(applied):
        if entry.skipped:
            continue
        try:
            entry.abs_path.write_text(entry.pre_content, encoding="utf-8")
        except OSError:
            # Best-effort revert; don't crash the cleanup path.
            continue
