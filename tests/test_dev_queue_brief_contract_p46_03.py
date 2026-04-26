"""P46-03 — dev-queue brief schema contract.

The /gsd-execute-phase-from-brief Claude Code skill (see
docs/skills/gsd-execute-phase-from-brief.md) parses the markdown
brief written by demo_server.write_dev_queue_brief() to:
  - confirm Status is ACCEPTED before doing anything
  - extract System / Affected gates / Target signals / Change kind
    so the implementer knows which truth-engine file(s) to touch
  - quote the engineer's original suggestion in the eventual
    commit message
  - mention the linked proposal JSON path in its plan

If a future refactor of write_dev_queue_brief drops a field the
skill expects, the loop breaks silently (the skill would parse
None where it expected text and likely emit a confusing plan).
This contract test catches that the moment it ships.

The test asserts the BRIEF FORMAT, not the skill itself — the
skill lives in ~/.claude/commands/ outside this repo, so we lock
what it CONSUMES. The skill's spec at
docs/skills/gsd-execute-phase-from-brief.md is the human-readable
counterpart.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from well_harness.demo_server import (
    create_proposal,
    interpret_suggestion_text,
    update_proposal_status,
    write_dev_queue_brief,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "dev_queue"))
    yield


def _accepted_brief_text(text: str = "L2 SW2 应该 tighten") -> tuple[Path, str]:
    """Drive a proposal through OPEN → ACCEPTED so a real brief
    lands on disk; return (brief_path, brief_text)."""
    interp = interpret_suggestion_text(text)
    record = create_proposal(
        source_text=text,
        interpretation=interp,
        author_name="Engineer-X",
        author_role="ENGINEER",
        ticket_id="WB-CONTRACT-TEST",
    )
    update_proposal_status(record["id"], new_status="ACCEPTED", actor="Kogami")
    from well_harness.demo_server import dev_queue_dir
    path = dev_queue_dir() / f"{record['id']}.md"
    return path, path.read_text(encoding="utf-8")


# ─── 1. Schema fields the skill REQUIRES ────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Step 2 of the skill: must read the status line to verify
        # it is ACCEPTED before doing anything.
        "**Status**: ACCEPTED",
        # Step 2: must read the system to drive truth-engine file
        # selection (controller.py vs adapter, etc).
        "**System**:",
        # Step 2: must read affected_gates + target_signals to know
        # what the change targets.
        "**Affected gates**:",
        "**Target signals**:",
        # Step 2: change_kind drives the verb in the commit message.
        "**Change kind**:",
        # Step 7 commit message: "Engineer suggestion: <quote>" lifts
        # this section.
        "## Engineer's original suggestion · 工程师原始建议",
        # Step 7 commit body: "System interpretation: <summary_zh>"
        # lifts this.
        "## System interpretation · 系统解读",
        # Step 5 branch name + Step 7 PR title both reference the
        # proposal id; the brief must echo it in the H1 so the skill
        # can extract the id even if invoked via 'pick the oldest'
        # rather than an explicit arg.
        "# Proposal PROP-",
        # Step 7 commit body links to dev-queue brief — must match
        # this exact path so the link doesn't 404 on GitHub.
        ".planning/dev_queue/",
        # Step 7 commit body links to proposal JSON for full audit.
        ".planning/proposals/",
        # Step 4 confirmation gate references the spec. The brief
        # itself doesn't have to mention /gsd-execute-phase, but
        # historically did so the skill could verify "this is a
        # brief I'm authorized to act on" — keep that.
        "/gsd-execute-phase",
    ],
)
def test_brief_carries_field_the_skill_parses(needle):
    _, text = _accepted_brief_text()
    assert needle in text, (
        f"dev-queue brief missing field '{needle}' that the "
        f"/gsd-execute-phase-from-brief skill parses. If you are "
        f"changing write_dev_queue_brief schema, also update "
        f"docs/skills/gsd-execute-phase-from-brief.md to match."
    )


# ─── 2. Schema versioning ──────────────────────────────────────────


def test_brief_carries_schema_version_marker():
    """The brief embeds a `schema v{N}` HTML comment so the skill
    can refuse to act on a future incompatible version rather than
    misparse it. v1 is the only version today; bumping requires
    updating the skill in lockstep."""
    _, text = _accepted_brief_text()
    assert "schema v1" in text, (
        "brief schema marker missing — skills can no longer detect "
        "version drift. Either restore the marker in "
        "write_dev_queue_brief() or bump + update both sides."
    )


def test_brief_marker_is_html_comment():
    """The schema marker must be an HTML comment so it doesn't
    render in GitHub's markdown preview (clutters the PR view)."""
    _, text = _accepted_brief_text()
    schema_line_idx = text.find("schema v")
    # Walk backward to find the start of the comment.
    pre = text.rfind("<!--", 0, schema_line_idx)
    post = text.find("-->", schema_line_idx)
    assert pre >= 0 and post > pre, "schema marker is not wrapped in <!-- ... -->"


# ─── 3. Engineer's text round-trips verbatim (audit fidelity) ──────


def test_engineer_source_text_appears_verbatim_in_brief():
    """The skill's commit message lifts the engineer's first-sentence
    suggestion. The brief must carry the source_text verbatim so the
    quote is faithful — paraphrasing here would silently re-author
    the engineer's request."""
    raw = "L1 上的 SW1 condition should be tightened to ≥ 50ms duration"
    _, text = _accepted_brief_text(raw)
    assert raw in text


# ─── 4. Skill snapshot stays in sync with installed copy ───────────


def test_repo_snapshot_matches_skill_or_explains_drift():
    """docs/skills/gsd-execute-phase-from-brief.md is a versioned
    snapshot of the user-level skill. They can drift legitimately
    (the user might be iterating on the skill before checking it
    in), but if they do, the README should explain how to refresh.

    We assert the snapshot exists + is non-trivial. If you want a
    stricter "snapshot must match installed copy" check, run it
    locally; we don't enforce in CI because the home-dir copy
    isn't a checked-in artifact."""
    snapshot = REPO_ROOT / "docs" / "skills" / "gsd-execute-phase-from-brief.md"
    assert snapshot.is_file(), (
        "docs/skills/gsd-execute-phase-from-brief.md missing — the "
        "in-repo snapshot of the skill spec is required for "
        "discoverability"
    )
    text = snapshot.read_text(encoding="utf-8")
    assert len(text) > 1000, "skill snapshot suspiciously short"
    # Spot-check: the snapshot should describe the truth-engine
    # red line. If a future cleanup PR strips this discussion,
    # the safety story is no longer in the repo.
    assert "Truth-engine red line" in text or "truth-engine red line" in text.lower()


def test_skill_readme_points_at_the_skill_file():
    readme = REPO_ROOT / "docs" / "skills" / "README.md"
    assert readme.is_file()
    text = readme.read_text(encoding="utf-8")
    # Should reference the skill by its slash-command name + the
    # install path so users can find it.
    assert "/gsd-execute-phase-from-brief" in text
    assert "~/.claude/commands/" in text
