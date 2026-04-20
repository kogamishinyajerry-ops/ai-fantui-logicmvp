"""
Thrust Reverser (DeployController) — Intake Packet Builder (Lean · D1=A)

Bridges the thrust-reverser truth path (lives in src/well_harness/controller.py
as the DeployController class + HarnessConfig in models.py, NOT under the
adapters/*_adapter.py pattern) to the intake pipeline so the docx requirement
document can be registered as an authoritative upstream reference.

Design decision: **D1=A Lean** (Kogami 2026-04-20).
The thrust_reverser chain does NOT have a standard workbench spec
(build_thrust_reverser_workbench_spec), so components / logic_nodes /
acceptance_scenarios / fault_modes / clarification_answers are all empty.
The three SourceDocumentRef entries are the whole value-add here: they make
the docx → code → yaml traceability explicit and queryable.

The actual 4 work-logic traceability (docx working-logic 1~4 ↔ DeployController
logic1~4_conditions) is captured in docs/thrust_reverser/traceability_matrix.md
(P36β-04), NOT in LogicNodeSpec objects here.

Upgrade path: a future Phase (e.g. P37 · thrust-reverser workbench spec) may
replace this lean packet with a full build_thrust_reverser_workbench_spec()
that materializes the 4 logic nodes as LogicNodeSpec; this packet is designed
to be trivially replaceable.

Usage:
    from well_harness.adapters.thrust_reverser_intake_packet import (
        build_thrust_reverser_intake_packet,
    )
    packet = build_thrust_reverser_intake_packet()
    # packet.source_documents contains 3 refs: controller.py / docx / YAML
"""
from __future__ import annotations

from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
)
from well_harness.system_spec import KnowledgeCaptureSpec


THRUST_REVERSER_SYSTEM_ID = "thrust-reverser"
THRUST_REVERSER_SOURCE_OF_TRUTH = "src/well_harness/controller.py"


def build_thrust_reverser_intake_packet() -> ControlSystemIntakePacket:
    """
    Build a lean (D1=A) ControlSystemIntakePacket for the thrust-reverser chain.

    Three SourceDocumentRef entries establish the provenance triangle:
      1. controller.py (python-controller, truth_source) — the executable truth
      2. docx (docx, requirement_reference) — the upstream authority (Kogami 自裁)
      3. yaml (yaml, hardware_spec) — the cross-verified constants table

    Business fields (components / logic_nodes / acceptance_scenarios /
    fault_modes) are empty by design: thrust_reverser does NOT use the
    workbench spec pipeline (P36β non-goal per D1=A). All 4 work-logic
    traceability is captured in docs/thrust_reverser/traceability_matrix.md
    instead of LogicNodeSpec objects.
    """
    source_document_refs = (
        SourceDocumentRef(
            id="thrust-reverser-controller-001",
            kind="python-controller",
            title="Thrust Reverser Deploy Controller (controller.py)",
            location="src/well_harness/controller.py",
            role="truth_source",
            notes=(
                "DeployController class implements 4 logic groups (logic1..4_conditions) "
                "encoding the docx working-logic 1..4. logic1 has 4 conditions (docx 3 + "
                "sw1 DIU trigger); logic2/3/4 are 1:1 with docx (5/6/4 conditions). "
                "13 threshold constants live in HarnessConfig (models.py:22-43) and "
                "are cross-verified with docx in traceability matrix table 5."
            ),
        ),
        SourceDocumentRef(
            id="thrust-reverser-requirement-docx-001",
            kind="docx",
            title="反推控制逻辑 (2026-04-09)",
            location="uploads/20260409-thrust-reverser-control-logic.docx",
            role="requirement_reference",
            notes=(
                "SHA256 6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5 · "
                "230930 bytes · 57 paragraphs · 2 tables (11-row device inventory + "
                "5-row cross-system device list) · 1 embedded media (word/media/image1.emf). "
                "Covers 8 input signals / 5 output signals / 15 monitored signals / "
                "4 working logics (logic1-4) / 10-step work process descriptor. "
                "Fault injection explicitly out-of-scope per docx §58: "
                "'故障注入目前暂时不考虑，很复杂。' "
                "Authority: Kogami 自裁 (Q5=A) · specific sign-off party pending "
                "docs/thrust_reverser/traceability_matrix.md Appendix A.6."
            ),
        ),
        SourceDocumentRef(
            id="thrust-reverser-hardware-yaml-001",
            kind="yaml",
            title="Thrust Reverser Hardware Parameters v1",
            location="config/hardware/thrust_reverser_hardware_v1.yaml",
            role="hardware_spec",
            notes=(
                "13 threshold constants cross-verified with docx (see traceability matrix "
                "table 5). 7 constants 1:1 with docx (radio<6ft / SW1 ±1.4°/-6.2° / "
                "TRA≤-11.74° / travel -32°/0°). 2 constants Executor assumed (SW2 "
                "±5.0°/-9.8° mirroring SW1 pattern; Appendix A.1). 4 constants Kogami "
                "待仲裁 (deploy_90 90.0 / tls_delay 0.3 / pls_delay 0.2 / deploy_rate "
                "30.0; Appendix A.2-A.4). YAML values themselves unchanged in P36β."
            ),
        ),
    )

    knowledge_capture = KnowledgeCaptureSpec(
        incident_fields=(),
        resolution_fields=(),
        optimization_fields=(),
    )

    return ControlSystemIntakePacket(
        system_id=THRUST_REVERSER_SYSTEM_ID,
        title="Thrust Reverser Deploy Controller",
        objective=(
            "Command the deploy side of the thrust-reverser chain (TLS 115VAC, "
            "ETRAC 540VDC, EEC deploy/stow, PLS power, PDU motor, throttle "
            "electronic lock release) per 4 working logics described in "
            "uploads/20260409-thrust-reverser-control-logic.docx. Truth lives in "
            "src/well_harness/controller.py::DeployController; this packet is the "
            "provenance anchor, not a workbench spec."
        ),
        source_of_truth=THRUST_REVERSER_SOURCE_OF_TRUTH,
        source_documents=source_document_refs,
        components=(),
        logic_nodes=(),
        acceptance_scenarios=(),
        fault_modes=(),
        knowledge_capture=knowledge_capture,
        clarification_answers=(),
        tags=("thrust-reverser", "deploy-side", "certified", "lean-intake"),
    )
