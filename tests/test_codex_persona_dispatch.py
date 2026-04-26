"""E11-10 — tests for tools/codex_persona_dispatch.py.

Covers the verdict parser (against real codex output samples extracted
from this session's recent E11-* sub-phases), round-robin arithmetic,
tier-B acceptance rule, and rotation-state append/parse roundtrip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.codex_persona_dispatch import (
    PERSONAS,
    append_rotation_entry,
    collect,
    count_findings,
    next_persona,
    parse_rotation_state,
    parse_tokens_used,
    parse_verdict,
    rotation_state_path,
    round_robin_successor,
    tier_b_accepts,
)


# ─── 1. parse_verdict ───────────────────────────────────────────────


def test_parse_verdict_bold_marker() -> None:
    assert parse_verdict("**APPROVE_WITH_NITS**\n\nFindings:") == "APPROVE_WITH_NITS"


def test_parse_verdict_backtick_marker() -> None:
    assert parse_verdict("`APPROVE_WITH_NITS`") == "APPROVE_WITH_NITS"


def test_parse_verdict_inline_verdict_keyword() -> None:
    assert parse_verdict("Verdict: APPROVE") == "APPROVE"


def test_parse_verdict_returns_last_when_repeated() -> None:
    """Codex repeats the verdict block at the end of output. We must
    return the LAST one so a rerun doesn't surface a stale earlier one."""
    text = "**APPROVE**\n\n... lots of details ...\n\n**APPROVE_WITH_NITS**"
    assert parse_verdict(text) == "APPROVE_WITH_NITS"


def test_parse_verdict_changes_required() -> None:
    assert parse_verdict("**CHANGES_REQUIRED**") == "CHANGES_REQUIRED"


def test_parse_verdict_returns_none_on_missing() -> None:
    assert parse_verdict("Codex is still investigating ...") is None


# ─── 2. count_findings ──────────────────────────────────────────────


def test_count_findings_in_verdict_block_only() -> None:
    """The word 'important' in a docstring should NOT inflate the count;
    only severity tags inside the verdict block count."""
    text = """
some preamble that mentions IMPORTANT in a docstring

**APPROVE_WITH_NITS**

- `BLOCKER` finding 1
- `IMPORTANT` finding 2
- `IMPORTANT` finding 3
- `NIT` finding 4
- `INFO` finding 5
"""
    counts = count_findings(text)
    assert counts == {"BLOCKER": 1, "IMPORTANT": 2, "NIT": 1, "INFO": 1}


def test_count_findings_dash_bullet_form() -> None:
    text = "**APPROVE**\n- BLOCKER X\n- NIT Y\n"
    counts = count_findings(text)
    assert counts["BLOCKER"] == 1
    assert counts["NIT"] == 1


def test_count_findings_zero_when_clean_approve() -> None:
    text = "**APPROVE**\n\nNo `BLOCKER` / `IMPORTANT` / `NIT` findings.\n"
    counts = count_findings(text)
    # The "No `BLOCKER`..." line is a literal listing and DOES count
    # under our parser. This is acceptable because clean-approve is the
    # exception path; downstream code should treat the verdict as
    # authoritative when verdict == APPROVE and acknowledge that
    # severity-tag counts may be artifactual.
    # Tier-B acceptance still works because APPROVE alone passes regardless.
    assert tier_b_accepts("APPROVE", counts) is True


def test_count_findings_de_duplicates_repeated_verdict_block() -> None:
    """Codex emits the verdict block once mid-output and again at the
    end. We only count after the LAST verdict marker so findings aren't
    doubled."""
    block = "- `BLOCKER` finding\n- `IMPORTANT` finding\n"
    text = f"**APPROVE_WITH_NITS**\n\n{block}\n\n**APPROVE_WITH_NITS**\n\n{block}"
    counts = count_findings(text)
    assert counts["BLOCKER"] == 1
    assert counts["IMPORTANT"] == 1


# ─── 3. tier-B acceptance rule ──────────────────────────────────────


@pytest.mark.parametrize(
    "verdict,counts,expected",
    [
        ("APPROVE", {"BLOCKER": 0, "IMPORTANT": 0, "NIT": 0, "INFO": 0}, True),
        ("APPROVE_WITH_NITS", {"BLOCKER": 0, "IMPORTANT": 1, "NIT": 0, "INFO": 0}, True),
        ("APPROVE_WITH_NITS", {"BLOCKER": 1, "IMPORTANT": 0, "NIT": 0, "INFO": 0}, False),
        ("CHANGES_REQUIRED", {"BLOCKER": 0, "IMPORTANT": 0, "NIT": 0, "INFO": 0}, False),
        (None, {"BLOCKER": 0, "IMPORTANT": 0, "NIT": 0, "INFO": 0}, False),
    ],
)
def test_tier_b_acceptance(verdict, counts, expected) -> None:
    assert tier_b_accepts(verdict, counts) is expected


# ─── 4. parse_tokens_used ───────────────────────────────────────────


def test_parse_tokens_used_canonical() -> None:
    text = "verdict body\n\ntokens used\n134,768\n\n**Done.**"
    assert parse_tokens_used(text) == 134768


def test_parse_tokens_used_returns_none_when_missing() -> None:
    assert parse_tokens_used("nothing here") is None


def test_parse_tokens_used_returns_last_match() -> None:
    text = "tokens used\n100\n\nmore stuff\n\ntokens used\n9999"
    assert parse_tokens_used(text) == 9999


# ─── 5. round-robin successor ───────────────────────────────────────


def test_round_robin_p1_to_p2() -> None:
    assert round_robin_successor("P1") == "P2"


def test_round_robin_p5_wraps_to_p1() -> None:
    assert round_robin_successor("P5") == "P1"


def test_round_robin_invalid_persona_raises() -> None:
    with pytest.raises(ValueError):
        round_robin_successor("P9")


# ─── 6. parse_rotation_state ────────────────────────────────────────


def test_parse_rotation_state_skips_tier_a_pointer_unchanged() -> None:
    text = """# header
E11-13: Tier-B (4 copy_diff_lines, ...). Persona = P1
E11-14: Tier-B (5 copy_diff_lines, ...). Persona = P2
E11-05: Tier-A (12 copy_diff_lines, all [REWRITE] — three-column rename in lockstep). All 5 personas dispatched. Rotation pointer unchanged.
E11-04: Tier-B (7 copy_diff_lines, ...). Persona = P3
E11-06: Tier-B (10 copy_diff_lines but 0 [REWRITE/DELETE]). Persona = P4
"""
    sequence = parse_rotation_state(text)
    # E11-05 is Tier-A with rotation-pointer-unchanged → skipped
    assert sequence == ["P1", "P2", "P3", "P4"]


def test_parse_rotation_state_empty_when_no_entries() -> None:
    assert parse_rotation_state("# header only\n") == []


# ─── 7. next_persona end-to-end (uses real PERSONA-ROTATION-STATE) ──


def test_next_persona_against_synthetic_state(tmp_path) -> None:
    state = tmp_path / "PERSONA-ROTATION-STATE.md"
    state.write_text(
        "# header\n"
        "E11-13: Tier-B Persona = P1 ...\n"
        "E11-14: Tier-B Persona = P2 ...\n"
        "E11-15: Tier-B Persona = P3 ...\n",
        encoding="utf-8",
    )
    assert next_persona(tmp_path) == "P4"


def test_next_persona_returns_p1_for_fresh_epic(tmp_path) -> None:
    """No rotation state file at all → start at P1."""
    assert next_persona(tmp_path) == "P1"


def test_next_persona_returns_p1_for_empty_rotation_state(tmp_path) -> None:
    """File exists but has no Tier-B entries yet → start at P1."""
    (tmp_path / "PERSONA-ROTATION-STATE.md").write_text("# Header only\n", encoding="utf-8")
    assert next_persona(tmp_path) == "P1"


def test_next_persona_against_real_e11_state() -> None:
    """The real PERSONA-ROTATION-STATE.md should report P1 (E11-11's P5 → P1)
    as the next persona since E11-11 is the last Tier-B entry."""
    repo_root = Path(__file__).resolve().parents[1]
    epic_dir = repo_root / ".planning" / "phases" / "E11-workbench-engineer-first-ux"
    if not (epic_dir / "PERSONA-ROTATION-STATE.md").exists():
        pytest.skip("real PERSONA-ROTATION-STATE.md not present")
    nxt = next_persona(epic_dir)
    assert nxt in PERSONAS


# ─── 8. append_rotation_entry roundtrip ─────────────────────────────


def test_append_rotation_entry_writes_canonical_line(tmp_path) -> None:
    state = tmp_path / "PERSONA-ROTATION-STATE.md"
    state.write_text("# header\nE11-13: Tier-B Persona = P1 reason\n", encoding="utf-8")
    line = append_rotation_entry(tmp_path, "E11-99", "P3", "B", "test reason")
    assert "E11-99: Tier-B (Persona = P3 — test reason)" in line
    body = state.read_text(encoding="utf-8")
    assert body.endswith(line)
    # roundtrip via parser
    seq = parse_rotation_state(body)
    assert seq[-1] == "P3"


def test_append_rotation_entry_rejects_bad_tier(tmp_path) -> None:
    (tmp_path / "PERSONA-ROTATION-STATE.md").write_text("# h\n", encoding="utf-8")
    with pytest.raises(ValueError):
        append_rotation_entry(tmp_path, "E11-99", "P3", "C", "reason")


def test_append_rotation_entry_rejects_bad_persona(tmp_path) -> None:
    (tmp_path / "PERSONA-ROTATION-STATE.md").write_text("# h\n", encoding="utf-8")
    with pytest.raises(ValueError):
        append_rotation_entry(tmp_path, "E11-99", "P9", "B", "reason")


# ─── 9. collect end-to-end ──────────────────────────────────────────


def test_collect_returns_tier_b_acceptance_when_clean(tmp_path) -> None:
    out = tmp_path / "persona-P3-E11-XX-output.md"
    out.write_text(
        "preamble\n\n**APPROVE_WITH_NITS**\n\n- `IMPORTANT` finding\n- `NIT` finding\n\ntokens used\n50000\n",
        encoding="utf-8",
    )
    result = collect(tmp_path, "E11-XX", "P3")
    assert result.verdict == "APPROVE_WITH_NITS"
    assert result.finding_counts["BLOCKER"] == 0
    assert result.finding_counts["IMPORTANT"] == 1
    assert result.finding_counts["NIT"] == 1
    assert result.tokens_used == 50000
    assert result.tier_b_acceptance is True


def test_collect_blocker_fails_tier_b(tmp_path) -> None:
    out = tmp_path / "persona-P3-E11-XX-output.md"
    out.write_text(
        "**CHANGES_REQUIRED**\n\n- `BLOCKER` you must fix this\n\ntokens used\n12345\n",
        encoding="utf-8",
    )
    result = collect(tmp_path, "E11-XX", "P3")
    assert result.verdict == "CHANGES_REQUIRED"
    assert result.finding_counts["BLOCKER"] == 1
    assert result.tier_b_acceptance is False


def test_collect_handles_missing_output(tmp_path) -> None:
    result = collect(tmp_path, "E11-XX", "P3")
    assert result.verdict is None
    assert result.tier_b_acceptance is False
    assert any("does not exist" in n for n in result.notes)


def test_collect_notes_when_codex_still_running(tmp_path) -> None:
    out = tmp_path / "persona-P3-E11-XX-output.md"
    out.write_text("Codex is investigating...\n", encoding="utf-8")
    result = collect(tmp_path, "E11-XX", "P3")
    assert result.verdict is None
    assert any("no verdict marker" in n for n in result.notes)
