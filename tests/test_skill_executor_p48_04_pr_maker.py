"""P48-04 — pr_maker: gh wrapper + EXEC-id stamp builder/parser.

The stamp is the contract the P48-05 GitHub Action will parse.
build_exec_stamp() and parse_exec_stamp() must round-trip
exactly; the test count here is heavy because this is the
attack surface for "is this PR really from the executor?"
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.pr_maker import (
    EXEC_STAMP_DELIMITER,
    PRDetails,
    PRMakerError,
    build_exec_stamp,
    open_pr,
    parse_exec_stamp,
)


# ─── 1. build_exec_stamp / parse_exec_stamp round-trip ────────────────


def test_stamp_round_trip():
    stamp = build_exec_stamp(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-foo",
        audit_path=".planning/skill_executions/EXEC-20260427T120000123456-abc123.json",
        executor_version="0.1.0",
    )
    parsed = parse_exec_stamp(stamp)
    assert parsed == {
        "exec_id": "EXEC-20260427T120000123456-abc123",
        "proposal": "PROP-foo",
        "audit": ".planning/skill_executions/EXEC-20260427T120000123456-abc123.json",
        "skill_executor_version": "0.1.0",
    }


def test_stamp_starts_with_delimiter():
    """The leading `---` is what tells the parser where the stamp
    begins. Lock it down."""
    stamp = build_exec_stamp(
        exec_id="EXEC-x", proposal_id="P", audit_path="a", executor_version="v"
    )
    first_line = stamp.split("\n", 1)[0]
    assert first_line == EXEC_STAMP_DELIMITER


def test_stamp_with_pr_body_prefix_round_trips():
    body = (
        "## Summary\n\nbody body body\n\n"
        + build_exec_stamp(
            exec_id="EXEC-x",
            proposal_id="P",
            audit_path="a.json",
            executor_version="0.1.0",
        )
    )
    parsed = parse_exec_stamp(body)
    assert parsed is not None
    assert parsed["exec_id"] == "EXEC-x"


# ─── 2. parse_exec_stamp rejection cases ──────────────────────────────


def test_parse_returns_none_for_no_stamp():
    assert parse_exec_stamp("just a regular PR description") is None


def test_parse_returns_none_for_missing_field():
    body = (
        "## Summary\n\n---\nExec-Id: EXEC-x\nProposal: P\n"
        # missing Audit + Skill-Executor-Version
    )
    assert parse_exec_stamp(body) is None


def test_parse_takes_last_delimiter_block():
    """PR bodies often have multiple `---` (markdown horizontal
    rules). The parser must pick the LAST one — that's where the
    executor stamp goes."""
    body = (
        "## Summary\n\n---\n\nblah\n\n---\n"
        + "Exec-Id: EXEC-real\n"
        + "Audit: a.json\n"
        + "Proposal: P\n"
        + "Skill-Executor-Version: 0.1.0\n"
    )
    parsed = parse_exec_stamp(body)
    assert parsed is not None
    assert parsed["exec_id"] == "EXEC-real"


def test_parse_returns_none_for_non_string():
    assert parse_exec_stamp(None) is None
    assert parse_exec_stamp(42) is None


def test_parse_tolerates_extra_whitespace():
    body = (
        "---\n"
        "Exec-Id:    EXEC-spaced\n"
        "Audit:  a.json\n"
        "Proposal:   P\n"
        "Skill-Executor-Version: 0.1.0\n"
    )
    parsed = parse_exec_stamp(body)
    assert parsed["exec_id"] == "EXEC-spaced"


# ─── 3. open_pr happy path (mocked gh) ────────────────────────────────


def test_open_pr_invokes_gh_with_expected_args():
    captured: dict = {}

    def fake_gh(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["input"] = kwargs.get("input")
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout="https://github.com/o/r/pull/99\n",
            stderr="",
        )

    result = open_pr(
        repo_root=Path("/fake"),
        title="feat: x",
        body="body with stamp",
        head="feat/branch",
        base="main",
        gh_runner=fake_gh,
    )
    assert isinstance(result, PRDetails)
    assert result.url == "https://github.com/o/r/pull/99"
    assert result.body == "body with stamp"
    assert "gh" in captured["cmd"][0]
    assert "pr" in captured["cmd"]
    assert "create" in captured["cmd"]
    assert "--head" in captured["cmd"]
    assert "feat/branch" in captured["cmd"]
    assert "--base" in captured["cmd"]
    assert "main" in captured["cmd"]
    # body sent via stdin (--body-file -)
    assert captured["input"] == "body with stamp"


def test_open_pr_passes_draft_flag():
    def fake_gh(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=0,
            stdout="https://github.com/o/r/pull/1\n", stderr=""
        )

    captured = []

    def capture_gh(cmd, **kwargs):
        captured.append(cmd)
        return fake_gh(cmd, **kwargs)

    open_pr(
        repo_root=Path("/x"), title="t", body="b", head="h",
        draft=True, gh_runner=capture_gh,
    )
    assert "--draft" in captured[0]


# ─── 4. open_pr error paths ───────────────────────────────────────────


def test_open_pr_raises_on_gh_failure():
    def fake_gh(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr="gh: not authenticated"
        )

    with pytest.raises(PRMakerError) as exc:
        open_pr(
            repo_root=Path("/x"), title="t", body="b", head="h",
            gh_runner=fake_gh,
        )
    assert "not authenticated" in exc.value.stderr


def test_open_pr_raises_when_no_url_in_output():
    """gh exited 0 but printed something we couldn't parse — still
    a failure since we have no PR URL to record in audit."""
    def fake_gh(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="something else\n", stderr=""
        )

    with pytest.raises(PRMakerError) as exc:
        open_pr(
            repo_root=Path("/x"), title="t", body="b", head="h",
            gh_runner=fake_gh,
        )
    assert "no PR URL parsed" in str(exc.value)
