"""Read proposal JSON + dev-queue brief markdown for the executor.

The executor consumes two artifacts produced by the workbench:
  - .planning/proposals/PROP-*.json     (P44-03 schema)
  - .planning/dev_queue/PROP-*.md       (P44-05 schema)

Both are independently produced by demo_server (the workbench) —
this module just reads them. Skill executor never writes back to
either; the only feedback channel is the /landed POST (P48-04
caller's responsibility, not this module).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from well_harness.skill_executor.errors import SkillExecutorError


class ProposalIOError(SkillExecutorError):
    """Proposal or brief missing / malformed / unreadable."""


def proposal_path(proposal_id: str, *, repo_root: Path) -> Path:
    """Locate the proposal JSON. Honors WORKBENCH_PROPOSALS_DIR
    env override (matches demo_server.proposals_dir behavior) so
    test isolation works the same way."""
    override = os.environ.get("WORKBENCH_PROPOSALS_DIR")
    if override:
        return Path(override).expanduser() / f"{proposal_id}.json"
    return Path(repo_root) / ".planning" / "proposals" / f"{proposal_id}.json"


def brief_path(proposal_id: str, *, repo_root: Path) -> Path:
    """Locate the dev-queue brief markdown. Honors
    WORKBENCH_DEV_QUEUE_DIR env override."""
    override = os.environ.get("WORKBENCH_DEV_QUEUE_DIR")
    if override:
        return Path(override).expanduser() / f"{proposal_id}.md"
    return Path(repo_root) / ".planning" / "dev_queue" / f"{proposal_id}.md"


def load_proposal(proposal_id: str, *, repo_root: Path) -> dict:
    """Read + parse the proposal JSON. Raises ProposalIOError on
    any IO/parse problem so the orchestrator's error path is
    uniform.

    Required fields (the executor reads these directly):
      id, system_id, kind, interpretation, source_text, status

    For revert kind, ALSO required:
      revert_of_proposal_id, revert_target_sha
    """
    path = proposal_path(proposal_id, repo_root=Path(repo_root))
    if not path.is_file():
        raise ProposalIOError(f"proposal not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProposalIOError(f"proposal unreadable: {path}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProposalIOError(
            f"proposal not valid JSON: {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise ProposalIOError(
            f"proposal is not a JSON object: {path}"
        )
    for required in ("id", "system_id", "kind", "interpretation", "status"):
        if required not in data:
            raise ProposalIOError(
                f"proposal {proposal_id!r} missing field {required!r}"
            )
    if data["status"] != "ACCEPTED":
        raise ProposalIOError(
            f"proposal {proposal_id!r} is not ACCEPTED "
            f"(status={data['status']!r}); the executor only runs "
            f"on ACCEPTED proposals"
        )
    if data["kind"] == "revert":
        for f in ("revert_of_proposal_id", "revert_target_sha"):
            if not data.get(f):
                raise ProposalIOError(
                    f"revert proposal {proposal_id!r} missing {f!r}"
                )
    return data


def load_brief(proposal_id: str, *, repo_root: Path) -> str:
    """Read the dev-queue brief markdown. Raises ProposalIOError
    if not found or unreadable. Empty-string brief is allowed
    (some demo flows may not produce a brief)."""
    path = brief_path(proposal_id, repo_root=Path(repo_root))
    if not path.is_file():
        raise ProposalIOError(f"brief not found: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProposalIOError(f"brief unreadable: {path}: {exc}") from exc
