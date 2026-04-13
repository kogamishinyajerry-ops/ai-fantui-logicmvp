"""
NewSystem Intake Packet Builder

Builds a ControlSystemIntakePacket from your system adapter so it can flow
through the playback / diagnosis / knowledge capture pipeline stages.

Usage:
    from well_harness.adapters.your_system_intake_packet import build_new_system_intake_packet
    packet = build_new_system_intake_packet()

See landing_gear_intake_packet.py for a complete reference implementation.
"""
from __future__ import annotations

from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_to_workbench_spec,
)

# ---------------------------------------------------------------------------
# Import your system's adapter — replace with your actual adapter module
# ---------------------------------------------------------------------------
# TODO: Uncomment and point to your adapter:
# from well_harness.adapters.your_system_adapter import (
#     build_your_system_workbench_spec,
#     YOUR_SYSTEM_SYSTEM_ID,
# )


def build_new_system_intake_packet() -> ControlSystemIntakePacket:
    """
    Build a ControlSystemIntakePacket for the new system.

    The intake packet bridges the adapter path to the intake path by converting
    the workbench spec dict (produced by build_your_system_workbench_spec) into
    a typed ControlSystemIntakePacket.

    The packet re-uses the adapter's source_of_truth and adds placeholder
    source_documents (pointing to the adapter file itself) and empty
    clarification_answers, since the adapter already encodes the complete spec.

    TODO: Fill in the source_document_refs with your actual source documents.
          Each SourceDocumentRef identifies a document that provides
          engineering ground truth for this system.

    Parameters
    ----------
    None — all information is sourced from the adapter's workbench spec.

    Returns
    -------
    ControlSystemIntakePacket
        A fully-populated intake packet ready for:
          - assess_intake_packet()        (structural validation)
          - build_playback_report_from_intake_packet()
          - build_fault_diagnosis_report_from_intake_packet()
          - build_knowledge_artifact()
    """
    # TODO: Uncomment and call your adapter's spec builder:
    # spec_dict = build_your_system_workbench_spec()
    # spec = workbench_spec_from_dict(spec_dict)
    #
    # (workbench_spec_from_dict is imported from well_harness.system_spec)

    # TODO: Replace with your actual source document references.
    # Each entry corresponds to one engineering document that informs the spec.
    # Examples of 'kind' values: "pdf", "markdown", "notion", "python-adapter",
    #                            "spreadsheet", "word", "json-spec"
    # Examples of 'role' values: "truth_source", "logic_spec", "acceptance_evidence",
    #                           "wiring_diagram", "maintenance_manual"
    source_document_refs = (
        SourceDocumentRef(
            id="YOUR-DOC-ID-001",
            kind="pdf",
            title="Your System Logic Specification",
            location="docs/your-system-logic-spec.pdf",
            role="truth_source",
            notes="Primary engineering source for control logic and acceptance criteria.",
        ),
        # TODO: Add more SourceDocumentRef entries as needed:
        # SourceDocumentRef(
        #     id="YOUR-DOC-ID-002",
        #     kind="markdown",
        #     title="Your System Acceptance Test Timeline",
        #     location="docs/acceptance-timeline.md",
        #     role="acceptance_evidence",
        #     notes="Engineer-supplied A/B process timelines for playback.",
        # ),
    )

    # TODO: Uncomment once your adapter spec builder is wired up:
    # return ControlSystemIntakePacket(
    #     system_id=spec.system_id,
    #     title=spec.title,
    #     objective=spec.objective,
    #     source_of_truth=spec.source_of_truth,
    #     source_documents=source_document_refs,
    #     components=spec.components,
    #     logic_nodes=spec.logic_nodes,
    #     acceptance_scenarios=spec.acceptance_scenarios,
    #     fault_modes=spec.fault_modes,
    #     knowledge_capture=spec.knowledge_capture,
    #     clarification_answers=(),
    #     tags=spec.tags,
    # )

    # Stub — replace with the real return above
    raise NotImplementedError(
        "build_new_system_intake_packet is not yet implemented. "
        "Uncomment the import and return statement above after "
        "creating your system adapter."
    )
