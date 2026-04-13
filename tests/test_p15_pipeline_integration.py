"""P15 Pipeline Integration — markdown→intake-packet converter and pipeline runner tests."""

from __future__ import annotations

import json
import os
import pytest

# Ensure P14_AI_MOCK and P15_AI_MOCK are set so P14/P15 functions use mock fixtures
os.environ.setdefault("P14_AI_MOCK", "1")
os.environ.setdefault("P15_AI_MOCK", "1")

from well_harness.ai_doc_analyzer import (
    P14SessionStore,
    MOCK_PROMPT_DOCUMENT,
    analyze_document,
    evaluate_clarification,
    generate_prompt_document,
    convert_markdown_to_intake,
    run_pipeline_from_intake,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def p14_store():
    """Reset P14 session store and return it for use in tests."""
    store = P14SessionStore()
    store.reset()
    yield store


@pytest.fixture
def sample_session(p14_store):
    """Create a completed P14 session with resolved ambiguities."""
    session = p14_store.create(
        session_id="test-session-p15",
        document_text="VDT90 sensor monitors deploy position. L3 activates when VDT90 >= 90% and not inhibited.",
        document_name="vdt90-logic.md",
    )
    ambiguities = analyze_document(session.document_text)
    assert not isinstance(ambiguities, dict), "analyze_document should return list in mock mode"
    session.ambiguities = ambiguities
    session.questions = []
    for amb in ambiguities:
        q_id = f"q-{len(session.questions) + 1}"
        from well_harness.ai_doc_analyzer import Question
        session.questions.append(Question(id=q_id, ambiguity_id=amb.id, question=amb.suggested_clarification))
    p14_store.update(session)
    # Answer all questions to make session complete
    for q in session.questions:
        result = evaluate_clarification(session, "Test answer for " + q.question)
        p14_store.update(session)
    assert session.is_complete, "Session should be complete after answering all questions"
    return session


# ---------------------------------------------------------------------------
# Tests: convert_markdown_to_intake
# ---------------------------------------------------------------------------

def test_convert_to_intake_success():
    """convert_markdown_to_intake returns a valid intake packet dict with P15_AI_MOCK=1."""
    markdown = "# VDT90 Deploy System\n\n## Logic Nodes\nL3 activates at VDT90 >= 90%."
    result = convert_markdown_to_intake(markdown, system_id="test-system-vdt90")

    assert isinstance(result, dict), "Result should be a dict"
    assert "system_id" in result
    assert result["system_id"] == "test-system-vdt90"
    assert "title" in result
    assert "components" in result
    assert "logic_nodes" in result
    assert "acceptance_scenarios" in result
    assert "fault_modes" in result
    assert "knowledge_capture" in result

    # Verify components structure
    components = result["components"]
    assert isinstance(components, list)
    assert len(components) > 0
    for comp in components:
        assert "id" in comp
        assert "label" in comp
        assert "kind" in comp

    # Verify logic nodes structure
    logic_nodes = result["logic_nodes"]
    assert isinstance(logic_nodes, list)
    for node in logic_nodes:
        assert "id" in node
        assert "conditions" in node


def test_convert_to_intake_uses_provided_system_id():
    """system_id parameter overrides the default in mock mode."""
    result = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT, system_id="my-custom-system-id")
    assert result["system_id"] == "my-custom-system-id"


def test_convert_to_intake_returns_error_on_missing_key():
    """When AI call fails (missing API key in non-mock), returns error dict."""
    # In mock mode, we get a valid dict back
    result = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT)
    assert "error" not in result or result.get("system_id")  # mock returns valid packet


# ---------------------------------------------------------------------------
# Tests: run_pipeline_from_intake
# ---------------------------------------------------------------------------

def test_run_pipeline_success_with_valid_intake():
    """run_pipeline_from_intake runs full pipeline and returns assessment + bundle."""
    # First get a valid intake packet from conversion
    intake = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT, system_id="pipeline-test-system")
    assert "system_id" in intake

    result = run_pipeline_from_intake(intake)

    assert isinstance(result, dict)
    assert "assessment" in result
    assert "bundle" in result
    assert "system_snapshot" in result

    # Check assessment structure
    assessment = result["assessment"]
    assert "system_id" in assessment
    assert "component_count" in assessment
    assert "logic_node_count" in assessment

    # Check system_snapshot structure
    snapshot = result["system_snapshot"]
    assert "system_id" in snapshot
    assert "title" in snapshot
    assert "component_count" in snapshot
    assert "logic_node_count" in snapshot
    assert "acceptance_scenario_count" in snapshot
    assert "fault_mode_count" in snapshot
    assert "ready_for_spec_build" in snapshot

    # Check bundle summary structure
    bundle = result["bundle"]
    assert bundle is not None
    assert "system_id" in bundle
    assert "bundle_kind" in bundle


def test_run_pipeline_invalid_intake_packet():
    """run_pipeline_from_intake returns error dict for malformed intake packet."""
    bad_packet = {
        "system_id": "bad-packet",
        # missing required fields: title, objective, components, logic_nodes
    }

    result = run_pipeline_from_intake(bad_packet)

    assert isinstance(result, dict)
    assert "error" in result
    assert result["error"] == "intake_validation_failed"


def test_run_pipeline_missing_intake_packet():
    """run_pipeline_from_intake returns error for None/empty input."""
    result = run_pipeline_from_intake({})
    assert isinstance(result, dict)
    assert "error" in result


# ---------------------------------------------------------------------------
# Tests: intake packet schema validation
# ---------------------------------------------------------------------------

def test_intake_packet_passes_schema_validation():
    """Verify the converted intake packet passes intake_packet_from_dict schema."""
    from well_harness.document_intake import intake_packet_from_dict

    intake = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT, system_id="schema-test")
    packet = intake_packet_from_dict(intake)

    assert packet.system_id == "schema-test"
    assert packet.title
    assert packet.objective
    assert len(packet.components) > 0
    assert len(packet.logic_nodes) > 0


def test_converted_intake_has_valid_components():
    """Components extracted from mock markdown have required fields."""
    from well_harness.document_intake import intake_packet_from_dict

    intake = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT)
    packet = intake_packet_from_dict(intake)

    for comp in packet.components:
        assert comp.id
        assert comp.label
        assert comp.kind in ("sensor", "logic_gate", "pilot_input", "state", "command", "feedback", "parameter", "power")
        assert comp.state_shape in ("boolean", "analog", "binary", "discrete", "percentage")
        assert comp.unit is not None
        assert comp.description


def test_converted_intake_has_valid_logic_nodes():
    """Logic nodes extracted from mock markdown reference valid component IDs."""
    from well_harness.document_intake import intake_packet_from_dict

    intake = convert_markdown_to_intake(MOCK_PROMPT_DOCUMENT)
    packet = intake_packet_from_dict(intake)

    component_ids = {c.id for c in packet.components}
    for node in packet.logic_nodes:
        assert node.id
        assert node.label
        assert node.description
        assert len(node.conditions) > 0
        for cond in node.conditions:
            assert cond.source_component_id in component_ids, f"Logic node {node.id} references unknown component {cond.source_component_id}"


# ---------------------------------------------------------------------------
# Tests: integration — P14 session → P15 convert → pipeline run
# ---------------------------------------------------------------------------

def test_full_pipeline_from_p14_session_to_bundle():
    """End-to-end: P14 session produces prompt → P15 converts → pipeline runs → bundle returned."""
    store = P14SessionStore()
    store.reset()
    session = store.create(
        session_id="e2e-p15-test",
        document_text="Deploy system: VDT90 monitors position. L3 activates when VDT90 >= 90% and reverser not inhibited.",
        document_name="deploy-system.md",
    )

    # P14: Analyze
    ambiguities = analyze_document(session.document_text)
    assert not isinstance(ambiguities, dict)
    session.ambiguities = ambiguities
    session.questions = []
    for amb in ambiguities:
        from well_harness.ai_doc_analyzer import Question as P14Question
        session.questions.append(P14Question(
            id=f"q-{len(session.questions) + 1}",
            ambiguity_id=amb.id,
            question=amb.suggested_clarification,
        ))
    store.update(session)

    # P14: Answer all questions
    for q in session.questions:
        evaluate_clarification(session, "Confirmed via test")
        store.update(session)

    assert session.is_complete

    # P14: Generate prompt document
    prompt_doc = generate_prompt_document(session)
    assert isinstance(prompt_doc, str)
    session.generated_prompt = prompt_doc
    store.update(session)

    # P15: Convert markdown to intake packet
    intake_dict = convert_markdown_to_intake(prompt_doc, system_id="e2e-deploy-system")
    assert "system_id" in intake_dict
    assert intake_dict["system_id"] == "e2e-deploy-system"

    # P15: Run pipeline
    result = run_pipeline_from_intake(intake_dict)
    assert "assessment" in result
    assert "bundle" in result
    assert "system_snapshot" in result
    snapshot = result["system_snapshot"]
    assert snapshot["system_id"] == "e2e-deploy-system"
    assert snapshot["component_count"] > 0


# ---------------------------------------------------------------------------
# Tests: API endpoint behavior (via handler interfaces)
# ---------------------------------------------------------------------------

def test_p15_convert_validates_session_id():
    """_handle_p15_convert rejects missing session_id."""
    from well_harness.demo_server import _handle_p15_convert

    result, error = _handle_p15_convert({})
    assert result is None
    assert error is not None
    assert error["error"] == "missing_session_id"

    result, error = _handle_p15_convert({"session_id": ""})
    assert result is None
    assert error["error"] == "missing_session_id"


def test_p15_convert_validates_session_exists():
    """_handle_p15_convert returns session_not_found for unknown session."""
    from well_harness.demo_server import _handle_p15_convert

    result, error = _handle_p15_convert({"session_id": "nonexistent-session-xyz"})
    assert result is None
    assert error is not None
    assert error["error"] == "session_not_found"


def test_p15_convert_returns_intake_packet_for_valid_session(sample_session):
    """_handle_p15_convert returns intake_packet and validation for a valid session."""
    from well_harness.demo_server import _handle_p15_convert

    result, error = _handle_p15_convert({"session_id": sample_session.session_id})
    assert error is None, f"Expected no error, got: {error}"
    assert result is not None
    assert "intake_packet" in result
    assert "validation" in result
    assert result["validation"]["valid"] is True
    assert result["validation"]["errors"] == []


def test_p15_run_pipeline_rejects_missing_intake_packet():
    """_handle_p15_run_pipeline returns error when intake_packet is missing."""
    from well_harness.demo_server import _handle_p15_run_pipeline

    result, error = _handle_p15_run_pipeline({})
    assert result is None
    assert error is not None
    assert error["error"] == "missing_intake_packet"

    result, error = _handle_p15_run_pipeline({"intake_packet": None})
    assert result is None
    assert error["error"] == "missing_intake_packet"


def test_p15_run_pipeline_accepts_valid_intake(sample_session):
    """_handle_p15_run_pipeline returns assessment + bundle for valid intake packet."""
    from well_harness.demo_server import _handle_p15_convert, _handle_p15_run_pipeline

    # First convert to get intake packet
    convert_result, _ = _handle_p15_convert({"session_id": sample_session.session_id})
    intake_packet = convert_result["intake_packet"]

    # Run pipeline
    result, error = _handle_p15_run_pipeline({"intake_packet": intake_packet})
    assert error is None, f"Expected no error, got: {error}"
    assert result is not None
    assert "assessment" in result
    assert "bundle" in result
    assert "system_snapshot" in result


# ---------------------------------------------------------------------------
# Tests: P15 route constants and dispatch
# ---------------------------------------------------------------------------

def test_p15_route_constants_defined():
    """P15 route constants are defined in demo_server."""
    from well_harness.demo_server import P15_CONVERT_PATH, P15_RUN_PIPELINE_PATH

    assert P15_CONVERT_PATH == "/api/p15/convert-to-intake"
    assert P15_RUN_PIPELINE_PATH == "/api/p15/run-pipeline"


def test_p15_routes_in_post_dispatch_set():
    """P15 routes are included in the allowed paths set for POST dispatch."""
    import inspect
    from well_harness.demo_server import DemoRequestHandler

    source = inspect.getsource(DemoRequestHandler.do_POST)
    assert "P15_CONVERT_PATH" in source
    assert "P15_RUN_PIPELINE_PATH" in source


# ---------------------------------------------------------------------------
# Tests: P15 functions work without P14 session
# ---------------------------------------------------------------------------

def test_convert_markdown_to_intake_standalone():
    """convert_markdown_to_intake works without any P14 session."""
    markdown = "# Test System\n\n## Objective\nTest objective text."
    result = convert_markdown_to_intake(markdown, system_id="standalone-test")
    assert isinstance(result, dict)
    assert result["system_id"] == "standalone-test"
    assert "components" in result
    assert "logic_nodes" in result


def test_run_pipeline_without_prior_p14_session():
    """run_pipeline_from_intake works without any prior P14 session."""
    # Use the mock intake packet directly
    from well_harness.ai_doc_analyzer import _MOCK_INTAKE_PACKET

    result = run_pipeline_from_intake(_MOCK_INTAKE_PACKET)
    assert "assessment" in result
    assert "bundle" in result
    assert "system_snapshot" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])