import json
from pathlib import Path

import pytest

from well_harness.workbench.proposals import (
    ProposalStore,
    build_annotation_proposal,
    validate_annotation_proposal,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_annotation_proposal_schema_defines_tools_and_surfaces():
    schema = json.loads((PROJECT_ROOT / "schemas/annotation_proposal.schema.json").read_text(encoding="utf-8"))

    assert schema["properties"]["tool"]["enum"] == ["point", "area", "link", "text-range"]
    assert schema["properties"]["surface"]["enum"] == ["control", "document", "circuit"]
    assert {
        "id",
        "tool",
        "surface",
        "anchor",
        "note",
        "author",
        "ticket_id",
        "system_id",
        "status",
        "created_at",
        "updated_at",
    }.issubset(set(schema["required"]))


def test_proposal_store_persists_valid_annotation_proposal(tmp_path):
    proposal = build_annotation_proposal(
        proposal_id="prop_test_001",
        tool="area",
        surface="circuit",
        anchor={"x": 0.12, "y": 0.2, "width": 0.4, "height": 0.28},
        note="Logic 3 should be reviewed against the selected detent threshold.",
        author="engineer-a",
        ticket_id="WB-E07-ANNOTATE",
        system_id="thrust-reverser",
        created_at="2026-04-25T08:00:00Z",
    )

    validate_annotation_proposal(proposal)
    store = ProposalStore(tmp_path)
    saved_path = store.save(proposal)

    assert saved_path == tmp_path / "prop_test_001.json"
    assert json.loads(saved_path.read_text(encoding="utf-8"))["status"] == "pending"
    assert store.load("prop_test_001") == proposal
    assert store.list_ids() == ["prop_test_001"]


def test_proposal_validation_rejects_unknown_tool_and_unsafe_ids(tmp_path):
    proposal = build_annotation_proposal(
        proposal_id="prop_test_002",
        tool="point",
        surface="control",
        anchor={"x": 0.5, "y": 0.25},
        note="Review the loaded ticket state.",
        author="engineer-a",
        ticket_id="WB-E07-ANNOTATE",
        system_id="thrust-reverser",
        created_at="2026-04-25T08:00:00Z",
    )

    with pytest.raises(ValueError, match="tool"):
        validate_annotation_proposal({**proposal, "tool": "freehand"})

    store = ProposalStore(tmp_path)
    with pytest.raises(ValueError, match="proposal id"):
        store.load("../escape")
