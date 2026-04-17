"""Regression tests for P18.5 canvas interaction improvements.

Verifies that:
  1. Fault injection UI has been removed from frontend (Option A)
  2. Hover scale animation is disabled (no transform: scale on hover)
  3. SVG container hit-box uses pointer-events: all

These are grep-level assertions that guard against reintroduction of:
  - Fault injection UI (⚡ lightning bolt buttons, fault bar, fault menus)
  - Hover scale transforms that interfere with click precision
  - Missing pointer-events on node containers
"""
import os
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).parent.parent / "src" / "well_harness" / "static"


class TestCanvasInteractionArtifacts(unittest.TestCase):
    """P18.5 canvas interaction regression tests."""

    def _read(self, filename: str) -> str:
        path = SRC_DIR / filename
        self.assertTrue(path.exists(), f"{filename} not found")
        return path.read_text(encoding="utf-8")

    # ── Fault Injection UI Removal (Option A) ─────────────────────────────────

    def test_no_fault_injection_ui_in_html(self):
        """HTML must not contain fault injection UI elements."""
        html = self._read("chat.html")
        artifacts = [
            "ndp-fault-section",
            "ndp-fault-info",
            "node-fault-btn",
            "fault-bar",
            "fault-presets",
            "fault-toggle",
            "id=\"chat-fault-bar\"",
        ]
        for artifact in artifacts:
            self.assertNotIn(artifact, html, f"Found '{artifact}' in chat.html")

    def test_no_fault_injection_ui_in_css(self):
        """CSS must not contain fault injection UI styles."""
        css = self._read("chat.css")
        artifacts = [
            "ndp-fault-section",
            "ndp-fault-info",
            "fault-bar",
            "fault-presets-menu",
            "fault-pill",
            "node-fault-btn",
            "faultDockPulse",
        ]
        for artifact in artifacts:
            self.assertNotIn(artifact, css, f"Found '{artifact}' in chat.css")

    def test_no_fault_injection_ui_in_js(self):
        """JS must not contain fault injection UI code."""
        js = self._read("chat.js")
        artifacts = [
            "FAULT_TYPES",
            "FAULT_PRESETS",
            "activeFaults",
            "isFaultBarExpanded",
            "faultUiBusy",
            "nodeFaultMenu",
            "nodeFaultBtn",
            "faultBar",
            "faultPills",
            "faultClearBtn",
            "faultToggleBtn",
            "showNodeFaultMenu",
            "hideNodeFaultButton",
            "toggleNodeFaultMenu",
            "injectFault",
            "removeFault",
            "serializeActiveFaults",
            "buildFaultAwareLeverPayload",
        ]
        for artifact in artifacts:
            self.assertNotIn(artifact, js, f"Found '{artifact}' in chat.js")

    def test_backend_fault_injection_api_preserved(self):
        """Backend fault injection API must remain functional.

        Option A removes only the frontend UI — the backend API and
        fault_injections payload field are preserved.
        """
        js = self._read("chat.js")
        # fault_injections field is still sent (empty array when no UI injection)
        self.assertIn("fault_injections:", js)
        # Backend server must still have the fault injection functions
        server_path = SRC_DIR.parent / "demo_server.py"
        self.assertTrue(server_path.exists())
        server = server_path.read_text(encoding="utf-8")
        self.assertIn("fault_injection", server)

    # ── Hover Scale Animation ─────────────────────────────────────────────────

    def test_no_hover_scale_transform_on_nodes(self):
        """Nodes must not scale on hover — scale interferes with click precision.

        The problematic value is scale(1.03) which was removed.
        scale(1) in tooltip rules is harmless (no-op).
        """
        css = self._read("chat.css")
        self.assertNotIn(
            "scale(1.03)",
            css,
            "scale(1.03) in hover rule interferes with click precision. "
            "Use filter: drop-shadow for hover feedback instead.",
        )

    # ── Hit-Box pointer-events ────────────────────────────────────────────────

    def test_svg_node_containers_have_pointer_events_all(self):
        """.chain-node-group and .logic-gate-group must have pointer-events: all."""
        css = self._read("chat.css")

        # Find the combined .chain-node-group,.logic-gate-group rule block
        idx = css.find(".chain-node-group,\n.logic-gate-group")
        if idx == -1:
            idx = css.find(".chain-node-group,\r\n.logic-gate-group")
        self.assertNotEqual(
            idx,
            -1,
            ".chain-node-group / .logic-gate-group rule not found",
        )

        # Scan forward for the closing }
        end_idx = css.find("}", idx)
        block = css[idx : end_idx + 1]
        self.assertIn(
            "pointer-events: all",
            block,
            ".chain-node-group / .logic-gate-group must include 'pointer-events: all'",
        )

    def test_svg_inner_elements_have_pointer_events_none(self):
        """SVG inner elements (svg, labels) must have pointer-events: none.

        This ensures clicks pass through to the container's pointer-events: all.
        """
        css = self._read("chat.css")
        # These elements should have pointer-events: none
        for selector in [".chain-node-svg", ".logic-gate-svg"]:
            # Find the rule
            idx = css.find(selector)
            if idx == -1:
                continue
            # Find the { after this selector
            brace_start = css.find("{", idx)
            brace_end = css.find("}", brace_start)
            block = css[brace_start : brace_end + 1]
            # If pointer-events is mentioned in this block, it should be none
            if "pointer-events" in block:
                self.assertIn(
                    "pointer-events: none",
                    block,
                    f"{selector} should have pointer-events: none, not auto",
                )

    def test_zoom_container_pan_end_handlers_are_registered(self):
        """zoomContainer must terminate panning on its own mouseup/mouseleave.

        Without these listeners, releasing the mouse over zoomContainer can leave
        wasPanning stuck true and block all later clicks on the canvas.
        """
        js = self._read("chat.js")
        self.assertIn("zoomContainer.addEventListener('mouseup', onPanEnd);", js)
        self.assertIn("zoomContainer.addEventListener('mouseleave', onPanEnd);", js)


if __name__ == "__main__":
    unittest.main()
