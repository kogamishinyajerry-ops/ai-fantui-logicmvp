"""
Bleed Air Valve Control System — Intake Packet Builder

Builds a ControlSystemIntakePacket from the bleed-air adapter so it can flow
through the playback / diagnosis / knowledge capture pipeline stages.

Usage:
    from well_harness.adapters.bleed_air_intake_packet import build_bleed_air_intake_packet
    packet = build_bleed_air_intake_packet()

FROZEN (2026-04-20) — demonstrative intake packet, no authoritative upstream spec.

This packet's SourceDocumentRef points to the adapter file itself (self-reference)
because no authoritative upstream document exists. Do not cite this packet as
audit truth. See docs/provenance/adapter_truth_levels.md.
"""
from __future__ import annotations

from well_harness.adapters.bleed_air_adapter import (
    build_bleed_air_workbench_spec,
    BLEED_AIR_SYSTEM_ID,
)
from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_to_workbench_spec,
)
from well_harness.system_spec import workbench_spec_from_dict


def build_bleed_air_intake_packet() -> ControlSystemIntakePacket:
    """
    Build a ControlSystemIntakePacket for the bleed-air valve control system.

    The intake packet bridges the adapter path to the intake path by converting
    the workbench spec dict produced by build_bleed_air_workbench_spec() into
    a typed ControlSystemIntakePacket.

    Source documents reference the adapter file itself as the ground-truth source.
    Clarification answers are empty because the adapter fully encodes the spec.
    """
    spec_dict = build_bleed_air_workbench_spec()
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="bleed-air-001",
            kind="python-adapter",
            title="Bleed Air Valve Controller Adapter",
            location="src/well_harness/adapters/bleed_air_adapter.py",
            role="truth_source",
            notes=(
                "P12-01 intake packet derived from bleed_air_adapter.py. "
                "Encodes the complete spec for bleed-air valve control including "
                "valve open/close logic, pressure thresholds, acceptance scenarios, "
                "and fault modes."
            ),
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
