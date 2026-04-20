"""
C919 E-TRAS — Intake Packet Builder

Builds a ControlSystemIntakePacket from the c919_etras_adapter so it can flow
through the playback / diagnosis / knowledge capture pipeline stages (same
bridge pattern as landing_gear_intake_packet / bleed_air_intake_packet).

Usage:
    from well_harness.adapters.c919_etras_intake_packet import (
        build_c919_etras_intake_packet,
    )
    packet = build_c919_etras_intake_packet()
"""
from __future__ import annotations

from well_harness.adapters.c919_etras_adapter import (
    build_c919_etras_workbench_spec,
    C919_ETRAS_SYSTEM_ID,
)
from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
)
from well_harness.system_spec import workbench_spec_from_dict


def build_c919_etras_intake_packet() -> ControlSystemIntakePacket:
    """
    Build a ControlSystemIntakePacket for the C919 E-TRAS control system.

    Source documents cite both the hand-written Python adapter (which is the
    executable truth) and the upstream 甲方 PDF requirement document (which is
    the audit reference). This lets P34-04 traceability matrix link every logic
    node / threshold / timing back to a specific PDF section.

    Clarification answers are empty because the adapter encodes the spec
    directly; future revisions (e.g. Q3 resolution for Max N1k Stow Limit)
    should replace this with explicit clarification items.
    """
    spec_dict = build_c919_etras_workbench_spec()
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="c919-etras-adapter-001",
            kind="python-adapter",
            title="C919 E-TRAS Controller Adapter",
            location="src/well_harness/adapters/c919_etras_adapter.py",
            role="truth_source",
            notes=(
                "P34 intake packet derived from c919_etras_adapter.py. "
                "Encodes the complete C919 E-TRAS control logic chain: EICU CMD2, "
                "EICU CMD3 (S-R flipflop), TR_Command3_Enable, FADEC Deploy Command, "
                "FADEC Stow Command. Step 1-10 timeline, 4 acceptance scenarios, "
                "5 fault modes."
            ),
        ),
        SourceDocumentRef(
            id="c919-etras-requirement-pdf-001",
            kind="pdf",
            title="C919 反推控制逻辑需求文档 (20260417)",
            location="uploads/20260417-C919反推控制逻辑需求文档.pdf",
            role="requirement_reference",
            notes=(
                "Authoritative 甲方 requirement PDF (10 pages). "
                "表1 component inventory, Figure 1 schematic, Figures 2-5 for "
                "EICU CMD2 / CMD3 / TR_Command3_Enable / FADEC Deploy Command, "
                "表2 MLG_WOW redundancy selection, Step 1-10 landing timeline. "
                "P34-04 traceability matrix maps each adapter symbol back to "
                "this PDF's section/figure."
            ),
        ),
        SourceDocumentRef(
            id="c919-etras-hardware-yaml-001",
            kind="yaml",
            title="C919 E-TRAS Hardware Parameters v1",
            location="config/hardware/c919_etras_hardware_v1.yaml",
            role="hardware_spec",
            notes=(
                "Sensor ranges, logic thresholds, physical limits, timing, and "
                "valid outcomes. Cross-verified with adapter constants."
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
