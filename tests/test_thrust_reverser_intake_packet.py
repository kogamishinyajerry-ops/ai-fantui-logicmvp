"""
P41-02 · Thrust-reverser intake packet minimal regression guard.

Locks the D1=A Lean invariants of `thrust_reverser_intake_packet.py` so
future edits don't silently break the Lean design choice (P36β-02 ·
preserved through P37-02).

Tests:
  1. Packet imports clean, returns a ControlSystemIntakePacket with 4
     SourceDocumentRef entries (controller + docx + yaml + supplement).
  2. D1=A Lean invariants: components / logic_nodes / acceptance_scenarios /
     fault_modes / clarification_answers are all empty tuples (full spec
     lives elsewhere in system_spec.current_reference_workbench_spec, per
     P41 Discovery doc'd in supplement §1.4 and registry row 1 notes).

If Lean is ever broken (business fields populated without updating the
supplement §8 4-way relationship and registry row 1 notes), this test
fails immediately with an actionable message.

Authority: P41 scope C · Kogami 2026-04-20 "Go C".
"""
from __future__ import annotations

import pytest

from well_harness.adapters.thrust_reverser_intake_packet import (
    THRUST_REVERSER_SOURCE_OF_TRUTH,
    THRUST_REVERSER_SYSTEM_ID,
    build_thrust_reverser_intake_packet,
)
from well_harness.document_intake import ControlSystemIntakePacket


def test_thrust_reverser_intake_packet_imports_clean() -> None:
    assert THRUST_REVERSER_SYSTEM_ID == "thrust-reverser"
    assert THRUST_REVERSER_SOURCE_OF_TRUTH == "src/well_harness/controller.py"

    packet = build_thrust_reverser_intake_packet()
    assert isinstance(packet, ControlSystemIntakePacket)
    assert packet.system_id == THRUST_REVERSER_SYSTEM_ID

    assert len(packet.source_documents) == 4, (
        f"Expected 4 SourceDocumentRef (controller + docx + yaml + supplement "
        f"post P37-02), got {len(packet.source_documents)}"
    )
    kinds = {sd.kind for sd in packet.source_documents}
    assert kinds == {"python-controller", "docx", "yaml", "markdown"}, (
        f"Expected 4 kinds (python-controller / docx / yaml / markdown), got {kinds}"
    )


def test_thrust_reverser_intake_packet_matches_d1a_lean() -> None:
    """D1=A Lean invariant: business fields all empty tuples.

    If this test fails, either:
      (a) business fields were populated on purpose → switch to D1=B mode,
          which requires updating supplement §1.4 / §8 / registry row 1 notes
          + a dedicated Phase; or
      (b) the change was accidental → revert.
    """
    packet = build_thrust_reverser_intake_packet()
    assert packet.components == (), (
        f"D1=A Lean broken: components not empty; got {packet.components}. "
        f"Full spec lives in system_spec.current_reference_workbench_spec."
    )
    assert packet.logic_nodes == (), (
        f"D1=A Lean broken: logic_nodes not empty; got {packet.logic_nodes}."
    )
    assert packet.acceptance_scenarios == (), (
        f"D1=A Lean broken: acceptance_scenarios not empty."
    )
    assert packet.fault_modes == (), (
        f"D1=A Lean broken: fault_modes not empty (docx §58 '不考虑')."
    )
    assert packet.clarification_answers == ()
    assert "lean-intake" in packet.tags, (
        f"Expected 'lean-intake' tag, got {packet.tags}"
    )
