from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
DRAFT_PATH = PROJECT_ROOT / "docs" / "thrust_reverser" / "l0_functional_requirements_v0_1.md"


def draft_text() -> str:
    return DRAFT_PATH.read_text(encoding="utf-8")


def requirement_ids(text: str) -> list[str]:
    return re.findall(r"^### (REQ-L0-\d{3})\b", text, flags=re.MULTILINE)


def requirement_sections(text: str) -> list[str]:
    parts = re.split(r"^### REQ-L0-\d{3}\b.*$", text, flags=re.MULTILINE)
    return [part for part in parts[1:] if part.strip()]


def test_l0_requirement_draft_has_bounded_record_count() -> None:
    ids = requirement_ids(draft_text())

    assert 3 <= len(ids) <= 5
    assert len(ids) == len(set(ids))


def test_each_l0_requirement_is_non_authoritative() -> None:
    for section in requirement_sections(draft_text()):
        assert "Level: L0" in section
        assert "Authority: non-authoritative draft" in section
        assert "DAL/PSSA: TBD / not assigned" in section
        assert "Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD" in section


def test_l0_draft_covers_required_topics() -> None:
    text = draft_text().lower()

    for phrase in (
        "reverse thrust",
        "safe enablement",
        "state and condition gating",
        "fault isolation",
        "response-time placeholder",
    ):
        assert phrase in text


def test_l0_draft_rejects_truth_claims() -> None:
    text = draft_text()

    assert "This draft does not change controller.py" in text
    assert "does not certify DAL" in text
    assert "does not promote truth-level" in text
    assert "does not supersede docs/thrust_reverser/requirements_supplement.md" in text
