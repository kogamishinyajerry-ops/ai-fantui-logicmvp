"""P49-02a — governance rule unit tests.

Locks down: evaluate_governance(proposal, plan) fires on the
right combinations (logic_truth namespace, red risk, expand
kind), is silent on safe combinations, and the env override
extends the guarded-namespace set without replacing it.
"""

from __future__ import annotations

import dataclasses

import pytest

from well_harness.skill_executor.governance import (
    DEFAULT_GUARDED_NAMESPACES,
    EXTRA_GUARDED_NAMESPACES_ENV,
    GOVERNANCE_ENABLED_ENV,
    GovernanceMatch,
    GovernanceVerdict,
    RULE_EXPAND_KIND,
    RULE_LOGIC_TRUTH_NAMESPACE,
    RULE_RED_RISK,
    evaluate_governance,
)


@pytest.fixture(autouse=True)
def _enable_governance(monkeypatch):
    """conftest disables the gate globally for the test suite;
    these tests explicitly opt back in to exercise the rules."""
    monkeypatch.setenv(GOVERNANCE_ENABLED_ENV, "1")


# Stand-ins so the unit test stays decoupled from real
# Proposal/PlannedChange shapes — evaluate_governance only reads
# attributes by getattr.
@dataclasses.dataclass
class _FakeProposal:
    kind: str = "modify"


@dataclasses.dataclass
class _FakePlan:
    affected_namespaces: list = dataclasses.field(default_factory=list)
    risk_assessment: dict = dataclasses.field(default_factory=dict)


# ─── 1. Default safe path: nothing fires ──────────────────────────


def test_clean_modify_plan_passes():
    """A modify-kind plan that doesn't touch logic_truth and has
    no red risk → no governance gate. Most everyday work should
    take this path."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(
            affected_namespaces=["logic_aux", "diagnostics"],
            risk_assessment={"logic_aux": "yellow"},
        ),
    )
    assert verdict.required is False
    assert verdict.matches == []


def test_empty_plan_passes():
    verdict = evaluate_governance(
        proposal=_FakeProposal(),
        plan=_FakePlan(),
    )
    assert verdict.required is False


# ─── 2. logic_truth namespace rule ───────────────────────────────


def test_logic_truth_in_affected_namespaces_triggers():
    """logic_truth is the safety-contract surface — touching it
    always requires human review, regardless of risk level."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(
            affected_namespaces=["logic_truth"],
            risk_assessment={"logic_truth": "yellow"},
        ),
    )
    assert verdict.required is True
    rule_ids = {m.rule_id for m in verdict.matches}
    assert RULE_LOGIC_TRUTH_NAMESPACE in rule_ids
    # Reason text mentions the namespace name so the workbench
    # card can show the operator exactly what triggered the gate
    msg = next(
        m for m in verdict.matches
        if m.rule_id == RULE_LOGIC_TRUTH_NAMESPACE
    )
    assert "logic_truth" in msg.reason


def test_other_namespaces_alone_do_not_trigger():
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(
            affected_namespaces=["logic_aux", "diagnostics"],
        ),
    )
    assert verdict.required is False


# ─── 3. Red-risk rule ────────────────────────────────────────────


def test_red_risk_triggers_regardless_of_namespace():
    """Even if the planner picked a non-guarded namespace, a
    self-assessed RED risk means the planner itself thinks the
    change is risky — defer to a human."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(
            affected_namespaces=["logic_aux"],
            risk_assessment={"logic_aux": "red"},
        ),
    )
    assert verdict.required is True
    assert any(
        m.rule_id == RULE_RED_RISK for m in verdict.matches
    )


def test_red_risk_case_insensitive():
    """Planner output isn't reliably lowercased; the rule
    normalizes."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(risk_assessment={"x": "RED"}),
    )
    assert verdict.required is True


def test_yellow_risk_does_not_trigger():
    """Only RED triggers — yellow is the planner saying 'mind it,
    but not blocking'."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(risk_assessment={"x": "yellow"}),
    )
    assert verdict.required is False


def test_multiple_red_namespaces_each_match():
    """Each red namespace gets its own match entry so the
    workbench card lists all the risky surfaces, not just one."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(risk_assessment={
            "logic_aux": "red",
            "diagnostics": "red",
            "alert_layer": "yellow",
        }),
    )
    red_matches = [m for m in verdict.matches if m.rule_id == RULE_RED_RISK]
    assert len(red_matches) == 2
    details = {m.detail for m in red_matches}
    assert details == {"logic_aux", "diagnostics"}


# ─── 4. expand kind rule ─────────────────────────────────────────


def test_expand_kind_triggers():
    """Creating new control logic is bigger blast radius than
    modifying existing — always reviewable."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="expand"),
        plan=_FakePlan(),
    )
    assert verdict.required is True
    assert any(
        m.rule_id == RULE_EXPAND_KIND for m in verdict.matches
    )


def test_modify_kind_does_not_trigger():
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(),
    )
    assert verdict.required is False


def test_expand_kind_case_insensitive():
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="EXPAND"),
        plan=_FakePlan(),
    )
    assert verdict.required is True


# ─── 5. Multiple rules can stack ──────────────────────────────────


def test_all_three_rules_can_fire_at_once():
    """A plan that hits everything: expand kind + logic_truth +
    red risk. Verdict should list all matches so the workbench
    can render the full picture."""
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="expand"),
        plan=_FakePlan(
            affected_namespaces=["logic_truth", "diagnostics"],
            risk_assessment={
                "logic_truth": "red",
                "diagnostics": "yellow",
            },
        ),
    )
    assert verdict.required is True
    rule_ids = {m.rule_id for m in verdict.matches}
    assert rule_ids == {
        RULE_EXPAND_KIND,
        RULE_LOGIC_TRUTH_NAMESPACE,
        RULE_RED_RISK,
    }


# ─── 6. Env override extends guarded namespaces ──────────────────


def test_env_override_adds_extra_guarded_namespace(monkeypatch):
    """Ops can pin extra namespaces to the gate without code
    changes. The override ADDS — it doesn't replace logic_truth."""
    monkeypatch.setenv(
        EXTRA_GUARDED_NAMESPACES_ENV,
        "alert_layer, recovery_logic",
    )
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(affected_namespaces=["alert_layer"]),
    )
    assert verdict.required is True
    # logic_truth is still guarded
    verdict2 = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(affected_namespaces=["logic_truth"]),
    )
    assert verdict2.required is True


def test_env_override_blank_treated_as_unset(monkeypatch):
    monkeypatch.setenv(EXTRA_GUARDED_NAMESPACES_ENV, "   ,   , ")
    # logic_aux not in defaults, no extras → no trigger
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="modify"),
        plan=_FakePlan(affected_namespaces=["logic_aux"]),
    )
    assert verdict.required is False


def test_default_guarded_set_includes_logic_truth():
    """Lock down the floor: even if env is set to nothing
    extreme, logic_truth always belongs to the guarded set."""
    assert "logic_truth" in DEFAULT_GUARDED_NAMESPACES


# ─── 7. JSON shape lockdown ──────────────────────────────────────


def test_verdict_to_json_shape():
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="expand"),
        plan=_FakePlan(),
    )
    j = verdict.to_json()
    assert set(j.keys()) == {"required", "matches"}
    assert j["required"] is True
    assert isinstance(j["matches"], list)
    for m in j["matches"]:
        assert set(m.keys()) == {"rule_id", "reason", "detail"}


def test_verdict_reasons_helper():
    verdict = evaluate_governance(
        proposal=_FakeProposal(kind="expand"),
        plan=_FakePlan(affected_namespaces=["logic_truth"]),
    )
    reasons = verdict.reasons()
    assert len(reasons) == 2  # expand + logic_truth
    assert all(isinstance(r, str) and r for r in reasons)


def test_match_dataclass_round_trip():
    m = GovernanceMatch(
        rule_id=RULE_EXPAND_KIND,
        reason="proposal kind is 'expand'",
        detail="expand",
    )
    assert m.to_json() == {
        "rule_id": RULE_EXPAND_KIND,
        "reason": "proposal kind is 'expand'",
        "detail": "expand",
    }
