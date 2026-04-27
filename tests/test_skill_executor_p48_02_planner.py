"""P48-02 — planner: brief → typed PlannedChange via mocked MiniMax.

Real LLM calls are slow + cost API budget, so all tests in this
module inject a `request_post` callable that returns a canned
response body. The shape of the canned body matches MiniMax's
real chat/completions envelope: `{choices: [{message: {content:
"..."}}]}`.

One smoke test that hits real MiniMax is at the bottom, gated on
the API key being available in the env.
"""

from __future__ import annotations

import json
import os

import pytest

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.llm_client import (
    LLMResponse,
    LLMUnavailableError,
)
from well_harness.skill_executor.planner import (
    PlannerError,
    plan_from_brief,
)


# ─── Mock helpers ──────────────────────────────────────────────────────


def _mock_response_body(content: str) -> str:
    """Wrap raw assistant content into MiniMax's response envelope."""
    return json.dumps(
        {
            "choices": [
                {"message": {"role": "assistant", "content": content}}
            ]
        }
    )


def _make_mock_post(
    responses: list[str],
):
    """Returns a callable suitable for plan_from_brief's
    request_post. `responses` is a list of raw assistant content
    strings — each call pops the next one. Useful for testing
    retry behavior where the first response is bad and the second
    is good.
    """
    iter_responses = iter(responses)

    def _post(url: str, body: bytes, headers: dict, timeout: float) -> str:
        try:
            return _mock_response_body(next(iter_responses))
        except StopIteration:
            raise AssertionError(
                "mock_post called more times than canned responses"
            )

    return _post


def _modify_proposal(
    *,
    proposal_id: str = "PROP-test",
    system_id: str = "thrust-reverser",
) -> dict:
    return {
        "id": proposal_id,
        "system_id": system_id,
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "affected_gates": ["L2"],
            "target_signals": ["SW2"],
            "summary_zh": "紧 L2 SW2",
            "summary_en": "tighten L2 SW2",
        },
    }


def _revert_proposal() -> dict:
    return {
        "id": "PROP-revert",
        "system_id": "thrust-reverser",
        "kind": "revert",
        "revert_target_sha": "abc1234",
        "revert_of_proposal_id": "PROP-original",
        "interpretation": {
            "change_kind": "revert",
            "affected_gates": ["L2"],
            "target_signals": ["SW2"],
            "summary_zh": "[REVERT]",
            "summary_en": "[REVERT]",
        },
    }


def _good_plan_json() -> str:
    return json.dumps(
        {
            "rationale": "Add hysteresis check on SW2 condition for L2",
            "affected_namespaces": ["logic_truth"],
            "risk_assessment": {"logic_truth": "yellow"},
            "estimated_loc": 10,
            "file_edits": [
                {
                    "path": "src/well_harness/controller.py",
                    "old_snippet": "if sw2:",
                    "new_snippet": "if sw2 and tra > -5.5:",
                    "reason": "tighten condition per proposal",
                }
            ],
            "test_changes": [],
        }
    )


# ─── 1. Happy path ─────────────────────────────────────────────────────


def test_planner_returns_validated_plan():
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="brief body",
        api_key="fake-key",
        request_post=_make_mock_post([_good_plan_json()]),
    )
    assert plan.rationale.startswith("Add hysteresis")
    assert plan.affected_namespaces == ["logic_truth"]
    assert plan.risk_assessment == {"logic_truth": "yellow"}
    assert plan.estimated_loc == 10
    assert len(plan.file_edits) == 1
    assert plan.file_edits[0].path == "src/well_harness/controller.py"
    # Provenance fields populated
    assert plan.planner_prompt  # non-empty
    assert plan.planner_response  # non-empty
    assert plan.planner_started_at
    assert plan.planner_finished_at
    assert plan.llm_backend  # model id


def test_planner_handles_response_with_think_block():
    """Real MiniMax-M2.7-highspeed wraps answers in
    <think>...</think>. The fence stripper must handle it before
    JSON parse runs."""
    response = (
        "<think>Let me figure out which file to edit...</think>\n"
        + _good_plan_json()
    )
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([response]),
    )
    assert plan.rationale.startswith("Add hysteresis")


def test_planner_handles_response_with_markdown_fence():
    response = "```json\n" + _good_plan_json() + "\n```"
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([response]),
    )
    assert plan.affected_namespaces == ["logic_truth"]


# ─── 2. Schema validation rejects malformed responses ─────────────────


def test_planner_rejects_invalid_json_after_retry():
    """Two bad attempts → PlannerError. The second attempt sees
    a retry prompt that re-states the schema."""
    bad = "this is not JSON at all"
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad, bad]),
        )
    assert len(exc.value.attempts) == 2
    assert "not valid JSON" in exc.value.last_validation_error


def test_planner_recovers_on_retry():
    """First response is unparseable, second is valid → planner
    succeeds with the second."""
    bad = "definitely not json"
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([bad, _good_plan_json()]),
    )
    assert plan.rationale.startswith("Add hysteresis")


def test_planner_rejects_missing_required_field():
    bad_plan = json.dumps({"rationale": "x", "affected_namespaces": ["logic_truth"]})
    # missing file_edits
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "file_edits" in exc.value.last_validation_error


def test_planner_rejects_empty_file_edits():
    bad_plan = json.dumps(
        {
            "rationale": "no-op plan",
            "affected_namespaces": ["logic_truth"],
            "file_edits": [],
        }
    )
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "file_edits cannot be empty" in exc.value.last_validation_error


def test_planner_rejects_unknown_namespace():
    bad_plan = json.dumps(
        {
            "rationale": "x",
            "affected_namespaces": ["fictional_namespace"],
            "file_edits": [
                {"path": "x.py", "old_snippet": "a", "new_snippet": "b"}
            ],
        }
    )
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "unknown namespace" in exc.value.last_validation_error


def test_planner_rejects_empty_affected_namespaces():
    bad_plan = json.dumps(
        {
            "rationale": "x",
            "affected_namespaces": [],
            "file_edits": [
                {"path": "x.py", "old_snippet": "a", "new_snippet": "b"}
            ],
        }
    )
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "affected_namespaces" in exc.value.last_validation_error


def test_planner_rejects_response_not_json_object():
    bad_plan = json.dumps(["this", "is", "an", "array"])
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "JSON object" in exc.value.last_validation_error


# ─── 3. Namespace cross-check rejects out-of-scope edits ──────────────


def test_planner_rejects_edit_outside_declared_namespace():
    """LLM declares affected_namespaces=['logic_truth'] but tries
    to edit demo_server.py, which is in NO namespace. Hard reject."""
    bad_plan = json.dumps(
        {
            "rationale": "let me also rewrite the server",
            "affected_namespaces": ["logic_truth"],
            "file_edits": [
                {
                    "path": "src/well_harness/controller.py",  # ok
                    "old_snippet": "a",
                    "new_snippet": "b",
                },
                {
                    "path": "src/well_harness/demo_server.py",  # NOT in any ns
                    "old_snippet": "c",
                    "new_snippet": "d",
                },
            ],
        }
    )
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "demo_server.py" in exc.value.last_validation_error
    assert "not covered by any known namespace" in exc.value.last_validation_error


def test_planner_rejects_edit_in_undeclared_namespace():
    """LLM declared logic_truth only but tries to edit a
    requirements file. The file IS in a namespace, just not the
    declared one — should still reject so reviewers know exactly
    what got changed."""
    bad_plan = json.dumps(
        {
            "rationale": "while we're here, update docs",
            "affected_namespaces": ["logic_truth"],
            "file_edits": [
                {
                    "path": "docs/thrust_reverser/requirements_supplement.md",
                    "old_snippet": "a",
                    "new_snippet": "b",
                }
            ],
        }
    )
    with pytest.raises(PlannerError) as exc:
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            api_key="fake-key",
            request_post=_make_mock_post([bad_plan, bad_plan]),
        )
    assert "requirements" in exc.value.last_validation_error


def test_planner_accepts_multi_namespace_plan():
    """If the plan honestly declares both namespaces and only edits
    files within them, that's fine."""
    multi_plan = json.dumps(
        {
            "rationale": "controller change + req doc update both needed",
            "affected_namespaces": ["logic_truth", "requirements"],
            "file_edits": [
                {
                    "path": "src/well_harness/controller.py",
                    "old_snippet": "a",
                    "new_snippet": "b",
                },
                {
                    "path": "docs/thrust_reverser/requirements_supplement.md",
                    "old_snippet": "c",
                    "new_snippet": "d",
                },
            ],
        }
    )
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([multi_plan]),
    )
    assert sorted(plan.affected_namespaces) == ["logic_truth", "requirements"]
    assert len(plan.file_edits) == 2


# ─── 4. Revert proposals ───────────────────────────────────────────────


def test_planner_handles_revert_kind():
    """Revert proposals must produce plans the same way; the
    prompt builder adds context about the target SHA but doesn't
    change the schema."""
    plan = plan_from_brief(
        proposal_record=_revert_proposal(),
        brief_text="undo PR #48",
        api_key="fake-key",
        request_post=_make_mock_post([_good_plan_json()]),
    )
    assert plan.affected_namespaces == ["logic_truth"]


def test_planner_revert_prompt_mentions_target_sha():
    """The retry prompt is built off the original prompt, so the
    revert addendum is critical context the LLM needs. Check it
    travels."""
    captured: list[str] = []

    def _capture_post(url, body, headers, timeout):
        captured.append(json.loads(body)["messages"][0]["content"])
        return _mock_response_body(_good_plan_json())

    plan_from_brief(
        proposal_record=_revert_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_capture_post,
    )
    assert "abc1234" in captured[0]
    assert "REVERT" in captured[0]


# ─── 5. LLMUnavailableError when no API key ───────────────────────────


def test_planner_raises_when_no_api_key(monkeypatch, tmp_path):
    """No silent fallback to rules — the planner FAILS LOUD if the
    LLM isn't reachable. (Audit trail integrity matters more than
    'just give the user something'.)"""
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("Minimax_API_key", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))  # no ~/.minimax_key
    with pytest.raises(LLMUnavailableError):
        plan_from_brief(
            proposal_record=_modify_proposal(),
            brief_text="b",
            # no api_key passed
            request_post=lambda *a, **kw: _mock_response_body(_good_plan_json()),
        )


# ─── 6. Provenance: prompt + response captured for audit ──────────────


def test_planner_captures_full_prompt_in_plan():
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="THE_BRIEF_BODY_TOKEN",
        api_key="fake-key",
        request_post=_make_mock_post([_good_plan_json()]),
    )
    assert "THE_BRIEF_BODY_TOKEN" in plan.planner_prompt
    # The proposal id should also be in there
    assert "PROP-test" in plan.planner_prompt


def test_planner_captures_raw_response_in_plan():
    raw = "<think>thinking…</think>\n" + _good_plan_json()
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([raw]),
    )
    # Raw includes the <think> block — important for audit replay
    assert "<think>" in plan.planner_response
    assert "thinking" in plan.planner_response


def test_planner_captures_timing():
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text="b",
        api_key="fake-key",
        request_post=_make_mock_post([_good_plan_json()]),
    )
    # ISO-8601 with 'Z'
    assert plan.planner_started_at.endswith("Z")
    assert plan.planner_finished_at.endswith("Z")
    assert plan.planner_started_at <= plan.planner_finished_at


# ─── 7. Live MiniMax smoke (skipped without API key) ──────────────────


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM") != "1",
    reason="live LLM smoke is opt-in — set RUN_LIVE_LLM=1 to enable",
)
def test_planner_real_minimax_smoke():
    """Live call against MiniMax. Opt-in only (set
    `RUN_LIVE_LLM=1`) so CI doesn't burn API budget every run.

    Cost: one MiniMax-M2.7-highspeed inference (~30-60s, ~2k tokens).
    Run before merging any planner-touching PR to confirm the live
    path still parses end-to-end.
    """
    plan = plan_from_brief(
        proposal_record=_modify_proposal(),
        brief_text=(
            "## Engineer's original suggestion\n"
            "L2 SW2 should tighten — currently too many false-OK signals.\n"
            "## Handoff\n"
            "Add a hysteresis check to L2's SW2 condition."
        ),
    )
    # Don't pin specific edits — MiniMax may reasonably propose
    # different paths/snippets. Just assert structural validity.
    assert plan.rationale  # non-empty
    assert plan.affected_namespaces  # at least one
    assert plan.file_edits  # at least one
    for edit in plan.file_edits:
        assert edit.path
        assert edit.old_snippet
        assert edit.new_snippet
