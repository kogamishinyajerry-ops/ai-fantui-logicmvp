"""P48-04 — proposal_io: read PROP-*.json + brief markdown."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from well_harness.skill_executor.proposal_io import (
    ProposalIOError,
    brief_path,
    load_brief,
    load_proposal,
    proposal_path,
)


def _stash_proposal(tmp_path: Path, data: dict) -> str:
    """Write `data` to {tmp_path}/proposals/{id}.json + return the id."""
    pid = data["id"]
    props = tmp_path / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    (props / f"{pid}.json").write_text(
        json.dumps(data) + "\n", encoding="utf-8"
    )
    return pid


def _stash_brief(tmp_path: Path, pid: str, body: str) -> None:
    queue = tmp_path / "queue"
    queue.mkdir(parents=True, exist_ok=True)
    (queue / f"{pid}.md").write_text(body, encoding="utf-8")


@pytest.fixture(autouse=True)
def _isolate_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "queue"))
    yield


# ─── 1. load_proposal happy path ──────────────────────────────────────


def test_load_proposal_returns_dict(tmp_path):
    pid = _stash_proposal(
        tmp_path,
        {
            "id": "PROP-test",
            "system_id": "thrust-reverser",
            "kind": "modify",
            "interpretation": {"change_kind": "tighten_condition"},
            "status": "ACCEPTED",
        },
    )
    record = load_proposal(pid, repo_root=tmp_path)
    assert record["id"] == pid
    assert record["status"] == "ACCEPTED"


def test_load_proposal_revert_kind_required_fields(tmp_path):
    pid = _stash_proposal(
        tmp_path,
        {
            "id": "PROP-revert",
            "system_id": "thrust-reverser",
            "kind": "revert",
            "interpretation": {},
            "status": "ACCEPTED",
            "revert_of_proposal_id": "PROP-orig",
            "revert_target_sha": "abc1234",
        },
    )
    record = load_proposal(pid, repo_root=tmp_path)
    assert record["revert_target_sha"] == "abc1234"


# ─── 2. load_proposal rejection ───────────────────────────────────────


def test_load_proposal_missing_file_raises(tmp_path):
    with pytest.raises(ProposalIOError) as exc:
        load_proposal("PROP-does-not-exist", repo_root=tmp_path)
    assert "not found" in str(exc.value)


def test_load_proposal_invalid_json_raises(tmp_path):
    props = tmp_path / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    (props / "PROP-bad.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(ProposalIOError) as exc:
        load_proposal("PROP-bad", repo_root=tmp_path)
    assert "not valid JSON" in str(exc.value)


def test_load_proposal_missing_required_field_raises(tmp_path):
    pid = _stash_proposal(
        tmp_path,
        {
            "id": "PROP-incomplete",
            # missing system_id
            "kind": "modify",
            "interpretation": {},
            "status": "ACCEPTED",
        },
    )
    with pytest.raises(ProposalIOError) as exc:
        load_proposal(pid, repo_root=tmp_path)
    assert "system_id" in str(exc.value)


def test_load_proposal_non_accepted_status_rejected(tmp_path):
    """Executor refuses to run on OPEN or REJECTED proposals."""
    pid = _stash_proposal(
        tmp_path,
        {
            "id": "PROP-still-open",
            "system_id": "thrust-reverser",
            "kind": "modify",
            "interpretation": {},
            "status": "OPEN",
        },
    )
    with pytest.raises(ProposalIOError) as exc:
        load_proposal(pid, repo_root=tmp_path)
    assert "ACCEPTED" in str(exc.value)


def test_load_proposal_revert_missing_target_sha_raises(tmp_path):
    pid = _stash_proposal(
        tmp_path,
        {
            "id": "PROP-revert",
            "system_id": "thrust-reverser",
            "kind": "revert",
            "interpretation": {},
            "status": "ACCEPTED",
            "revert_of_proposal_id": "PROP-orig",
            # missing revert_target_sha
        },
    )
    with pytest.raises(ProposalIOError) as exc:
        load_proposal(pid, repo_root=tmp_path)
    assert "revert_target_sha" in str(exc.value)


# ─── 3. load_brief ────────────────────────────────────────────────────


def test_load_brief_happy_path(tmp_path):
    _stash_brief(tmp_path, "PROP-x", "# brief body\n")
    body = load_brief("PROP-x", repo_root=tmp_path)
    assert body == "# brief body\n"


def test_load_brief_missing_raises(tmp_path):
    with pytest.raises(ProposalIOError) as exc:
        load_brief("PROP-no-brief", repo_root=tmp_path)
    assert "not found" in str(exc.value)


# ─── 4. Path helpers honor env override ───────────────────────────────


def test_proposal_path_uses_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "custom"))
    assert proposal_path(
        "PROP-x", repo_root=Path("/whatever")
    ) == tmp_path / "custom" / "PROP-x.json"


def test_brief_path_uses_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "custom-q"))
    assert brief_path(
        "PROP-x", repo_root=Path("/whatever")
    ) == tmp_path / "custom-q" / "PROP-x.md"
