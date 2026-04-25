"""Regression guards for /fantui_circuit.html SVG wire topology.

These tests lock in the shape of the static circuit diagram so that
silent drift (missing inputs, stray lines, shifted boxes) trips CI
instead of reaching the browser. They are deliberately structural —
they count wires per gate and sanity-check connector endpoints against
the gate/box centers — rather than pixel-exact so small cosmetic tweaks
stay unblocked.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CIRCUIT_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "fantui_circuit.html"


def _load() -> str:
    return CIRCUIT_HTML.read_text(encoding="utf-8")


# Regex picks up `<line x1="N" y1="N" x2="N" y2="N" ...>`.
_LINE_RE = re.compile(
    r'<line\s+x1="(?P<x1>-?\d+(?:\.\d+)?)"\s+y1="(?P<y1>-?\d+(?:\.\d+)?)"\s+'
    r'x2="(?P<x2>-?\d+(?:\.\d+)?)"\s+y2="(?P<y2>-?\d+(?:\.\d+)?)"',
    re.MULTILINE,
)


def _lines(html: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(m["x1"]), float(m["y1"]), float(m["x2"]), float(m["y2"]))
        for m in _LINE_RE.finditer(html)
    ]


class FantuiCircuitWireTopologyTests(unittest.TestCase):

    def setUp(self):
        self.html = _load()
        self.lines = _lines(self.html)

    # ---- Input fan-ins (one horizontal wire per input row into the spine) ----

    def _count_horizontal_into_spine(self, expected_ys: list[float], tolerance: float = 0.5) -> list[float]:
        """Return the subset of expected_ys that have a horizontal wire
        from x1=230 to x2=370 (input-row → spine)."""
        hits: list[float] = []
        for x1, y1, x2, y2 in self.lines:
            if not (x1 == 230 and x2 == 370 and y1 == y2):
                continue
            for ey in expected_ys:
                if abs(y1 - ey) < tolerance:
                    hits.append(ey)
                    break
        return hits

    def test_l1_has_four_input_wires(self):
        hits = self._count_horizontal_into_spine([62, 90, 118, 146])
        self.assertEqual(sorted(hits), [62, 90, 118, 146],
                         msg="L1 must have 4 horizontal input→spine wires at y=62/90/118/146")

    def test_l2_has_five_input_wires(self):
        hits = self._count_horizontal_into_spine([184, 212, 240, 268, 296])
        self.assertEqual(sorted(hits), [184, 212, 240, 268, 296],
                         msg="L2 must have 5 horizontal input→spine wires")

    def test_l3_has_six_input_wires(self):
        hits = self._count_horizontal_into_spine([332, 360, 388, 416, 444, 472])
        self.assertEqual(sorted(hits), [332, 360, 388, 416, 444, 472],
                         msg="L3 must have 6 horizontal input→spine wires")

    def test_l4_has_four_input_wires(self):
        hits = self._count_horizontal_into_spine([508, 536, 564, 592])
        self.assertEqual(sorted(hits), [508, 536, 564, 592],
                         msg="L4 must have 4 horizontal input→spine wires")

    # ---- Gate entry arrows (spine → gate left edge at x=380) ----

    def test_gate_entry_arrows(self):
        # Each gate has exactly one horizontal entry arrow from x=370 to
        # x=380 at the gate's vertical center y.
        expected_centers = {"L1": 104, "L2": 240, "L3": 402, "L4": 550}
        entries = [
            (x1, y1, x2, y2)
            for (x1, y1, x2, y2) in self.lines
            if x1 == 370 and x2 == 380 and y1 == y2
        ]
        ys = sorted(y for _, y, _, _ in entries)
        self.assertEqual(ys, sorted(expected_centers.values()),
                         msg=f"gate entry arrows mismatch — got y={ys}")

    # ---- Gate output → output box arrows ----

    def test_gate_outputs_enter_correct_boxes(self):
        # L1→tls (y=104), L2→etrac (y=240), L4→throttle (y=550): each is
        # a single horizontal wire from x=428 to x=560 at the gate center.
        expected_ys = [104, 240, 550]
        outs = [
            (x1, y1, x2, y2)
            for (x1, y1, x2, y2) in self.lines
            if x1 == 428 and x2 == 560 and y1 == y2
        ]
        self.assertEqual(sorted(y for _, y, _, _ in outs), expected_ys,
                         msg=f"gate→output arrows mismatch — got {outs}")

    def test_l3_gate_output_trunk_to_fanout_junction(self):
        # L3 feeds the fanout trunk at x=428..555 y=402 (NOT 428..560).
        matches = [
            l for l in self.lines
            if l == (428.0, 402.0, 555.0, 402.0)
        ]
        self.assertEqual(len(matches), 1,
                         msg="L3 must have exactly one gate-output trunk (428,402)→(555,402)")

    # ---- L3 three-way fanout ----

    def test_l3_fanout_delivers_three_arrows(self):
        # Three short arrows from x=555 to x=560 at y=370 / 402 / 434
        # (eec_deploy_cmd / pls_power_cmd / pdu_motor_cmd).
        expected_ys = [370, 402, 434]
        fanout_arrows = [
            y1 for (x1, y1, x2, y2) in self.lines
            if x1 == 555 and x2 == 560 and y1 == y2
        ]
        self.assertEqual(sorted(fanout_arrows), expected_ys,
                         msg=f"L3 fanout branches mismatch — got y={fanout_arrows}")

    # ---- Summary-badge spine at x=885 ----

    def test_deploy_enable_spine_single_vertical(self):
        # After the PR-3 review fix the spine from tls out to badge top
        # is a single (885, 104)→(885, 300) line. The previously redundant
        # (885, 240)→(885, 300) subset must NOT be present.
        spine_verticals = [
            (y1, y2) for (x1, y1, x2, y2) in self.lines
            if x1 == 885 and x2 == 885
        ]
        # Exactly two vertical spine segments: (104→300) top and (356→402) bottom
        self.assertEqual(
            sorted(spine_verticals),
            sorted([(104.0, 300.0), (356.0, 402.0)]),
            msg=f"DEPLOY ENABLE spine must have two non-overlapping verticals; got {spine_verticals}"
        )

    def test_throttle_unlock_connector_lands_on_badge_center(self):
        # Connector runs (760, 550)→(800, 550). Badge must be a rect with
        # vertical midline at y=550 (rect y=527, height=46 → center 550).
        self.assertIn(
            '<rect x="800" y="527" width="170" height="46"', self.html,
            msg="THROTTLE UNLOCK badge must be centered on y=550 (rect y=527, h=46)"
        )
        # And the connector must exist.
        self.assertIn(
            '<line x1="760" y1="550" x2="800" y2="550"',
            self.html,
        )

    # ---- Sanity: each input row has its rectangle ----

    def test_every_gate_has_correctly_labeled_input_row(self):
        required_labels = [
            # L1
            "radio_altitude_ft &lt; 6 ft",
            # L2
            "engine_running == True",
            "aircraft_on_ground == True",
            # L3 — same labels reuse; we check via substring count
            "tls_unlocked_ls == True",
            "n1k &lt; max_n1k_deploy_limit",
            "tra_deg ≤ −11.74°",
            # L4
            "deploy_90_percent_vdt",
            "−32° ≤ tra_deg &lt; 0°",
        ]
        for label in required_labels:
            self.assertIn(label, self.html, msg=f"circuit missing label: {label}")

        # aircraft_on_ground must appear in the SVG input nodes for
        # L2/L3/L4 (3 occurrences inside <svg>). The info cards below
        # echo the same labels, so total html occurrences ≥ 3.
        svg_block = self.html.split("<svg")[1].split("</svg>")[0]
        self.assertEqual(svg_block.count("aircraft_on_ground == True"), 3,
                         msg="aircraft_on_ground must appear as an SVG input node "
                             "in L2, L3, and L4 (3 total inside <svg>)")


if __name__ == "__main__":
    unittest.main()
