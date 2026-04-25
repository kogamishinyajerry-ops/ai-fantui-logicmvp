import json
from pathlib import Path

import pytest

from well_harness.collab.restricted_auth import RestrictedAuthError, validate_push_attempt
from well_harness.workbench.prompting import publish_ticket, render_claude_code_prompt
from well_harness.workbench.proposals import build_annotation_proposal


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _proposal() -> dict:
    return build_annotation_proposal(
        proposal_id="prop_prompt_001",
        tool="link",
        surface="document",
        anchor={"selector": "#workbench-document-panel", "href": "https://example.test/spec"},
        note="Create a scoped implementation handoff for the document annotation.",
        author="engineer-a",
        ticket_id="WB-E09-PROMPT",
        system_id="thrust-reverser",
        created_at="2026-04-25T10:00:00Z",
    )


def test_prompt_renderer_uses_four_required_sections():
    prompt = render_claude_code_prompt(
        _proposal(),
        authorized_engineer="claude-code",
        scope_files=["src/well_harness/workbench/**", "docs/workbench/**"],
        template_path=PROJECT_ROOT / "templates/claude_code_prompt.md.j2",
    )

    assert "## anchor" in prompt
    assert "## scope" in prompt
    assert "## acceptance" in prompt
    assert "## non-goals" in prompt
    assert "prop_prompt_001" in prompt
    assert "src/well_harness/workbench/**" in prompt


def test_ticket_publisher_writes_file_and_stdout_json(tmp_path, capsys):
    ticket_path = publish_ticket(
        _proposal(),
        authorized_engineer="claude-code",
        scope_files=["src/well_harness/workbench/**"],
        ticket_root=tmp_path / "tickets",
        template_path=PROJECT_ROOT / "templates/claude_code_prompt.md.j2",
    )

    stdout_payload = json.loads(capsys.readouterr().out)
    saved_payload = json.loads(ticket_path.read_text(encoding="utf-8"))

    assert ticket_path == tmp_path / "tickets/WB-E09-PROMPT.json"
    for field in ["Type", "Source Proposal", "Authorized Engineer", "Scope Files", "Generated Prompt", "PR URL", "Verdict"]:
        assert field in stdout_payload
        assert field in saved_payload
    assert stdout_payload["Source Proposal"] == "prop_prompt_001"
    assert stdout_payload["Authorized Engineer"] == "claude-code"


def test_restricted_auth_allows_only_authorized_engineer_and_scope_files():
    ticket = {
        "Authorized Engineer": "claude-code",
        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
    }

    decision = validate_push_attempt(
        ticket,
        engineer="claude-code",
        changed_files=["src/well_harness/workbench/prompting.py", "docs/workbench/HANDOVER.md"],
    )
    assert decision["allowed"] is True

    with pytest.raises(RestrictedAuthError, match="Authorized Engineer"):
        validate_push_attempt(ticket, engineer="other-agent", changed_files=["src/well_harness/workbench/prompting.py"])

    with pytest.raises(RestrictedAuthError, match="Scope Files"):
        validate_push_attempt(ticket, engineer="claude-code", changed_files=["src/well_harness/controller.py"])
