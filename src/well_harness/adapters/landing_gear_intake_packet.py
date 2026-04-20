"""
Minimal Landing Gear Extension — Intake Packet Builder

Bridges the adapter path to the intake path for the landing-gear system.

FROZEN (2026-04-20) — demonstrative intake packet, no authoritative upstream spec.

This packet's SourceDocumentRef points to the adapter file itself (self-reference)
because no authoritative upstream document exists. Do not cite this packet as
audit truth. See docs/provenance/adapter_truth_levels.md.
"""
from __future__ import annotations

from well_harness.adapters.landing_gear_adapter import build_landing_gear_workbench_spec
from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_to_workbench_spec,
)
from well_harness.system_spec import workbench_spec_from_dict


def build_landing_gear_intake_packet() -> ControlSystemIntakePacket:
    """
    Build a ControlSystemIntakePacket for the landing-gear system.

    This bridges the adapter path to the intake path by converting the
    landing-gear workbench spec dict (produced by build_landing_gear_workbench_spec)
    into a typed ControlSystemIntakePacket.

    The intake packet re-uses the adapter's source_of_truth and adds placeholder
    source_documents (the adapter file itself) and empty clarification_answers,
    since the adapter already encodes the complete spec.
    """
    spec_dict = build_landing_gear_workbench_spec()
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="lg-001",
            kind="python-adapter",
            title="Landing Gear Controller Adapter",
            location="src/well_harness/adapters/landing_gear_adapter.py",
            role="truth_source",
            notes="P10-01 intake packet derived from landing_gear_adapter.py",
        ),
    )

    return ControlSystemIntakePacket(
        system_id=spec.system_id,
        title=spec.title,
        objective=spec.objective,
        source_of_truth=spec.source_of_truth,
        source_documents=source_document_refs,
        components=spec.components,
        logic_nodes=spec.logic_nodes,
        acceptance_scenarios=spec.acceptance_scenarios,
        fault_modes=spec.fault_modes,
        knowledge_capture=spec.knowledge_capture,
        clarification_answers=(),
        tags=spec.tags,
    )
