"""Regression guards for /c919_etras_panel/circuit.html SVG wire topology.

Locks in the fixes applied after a visual audit of the state-machine
diagram: stray input-column arrows, mis-aimed output arrows, overflowing
KEY PARAMETERS panel, and feedback-label overlap with the S4 DEPLOYED
rect.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CIRCUIT_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel" / "circuit.html"


def _load() -> str:
    return CIRCUIT_HTML.read_text(encoding="utf-8")


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


class C919CircuitWireTopologyTests(unittest.TestCase):

    def setUp(self):
        self.html = _load()
        self.lines = _lines(self.html)

    # ---- Input → filter column arrows must land on actual blocks ----

    def test_no_stray_arrow_at_y_244(self):
        """LOCK INPUTS trunk must not emit a horizontal arrow at y=244 into
        an empty spot (CMD3 starts at y=256, CMD2 ends at y=216). Only
        the down-trunk (132,244)→(132,410) followed by (132,410)→(220,410)
        feed LOCKS AGG."""
        stray = [l for l in self.lines
                 if l == (132.0, 244.0, 218.0, 244.0) or l == (132.0, 244.0, 220.0, 244.0)]
        self.assertEqual(stray, [],
                         msg="stray LOCK INPUTS horizontal arrow at y=244 must be removed")

    def test_etras_fault_routes_into_cmd3(self):
        """ETRAS FAULT must route into CMD3 SR LATCH (used by !etras_over_temp
        SET guard), not terminate in the empty strip at y=373. Path:
        (132,373)→(180,373)→(180,332)→(220,332)."""
        segs = set(self.lines)
        for seg in [
            (132.0, 373.0, 180.0, 373.0),
            (180.0, 373.0, 180.0, 332.0),
            (180.0, 332.0, 220.0, 332.0),
        ]:
            self.assertIn(seg, segs, msg=f"expected ETRAS FAULT routing segment {seg}")
        # Stray target-less arrow must be gone.
        self.assertNotIn((132.0, 373.0, 218.0, 373.0), segs)
        self.assertNotIn((132.0, 373.0, 220.0, 373.0), segs)

    # ---- Output arrows must hit box left edge cleanly (x=844) ----

    def test_output_arrow_endpoints_land_on_box_edge(self):
        """All six output-column arrows terminate at x=844 (left edge of
        output boxes), not at x=842 (2px short) or x=860 (inside box)."""
        # (source_x, source_y, target_y)
        expected = [
            (722, 170, 167),   # 1-PH UNLOCK PWR
            (722, 200, 207),   # 3-PH TRCU PWR
            (722, 234, 279),   # FADEC DEPLOY CMD (was x2=860 — inside box)
            (722, 352, 371),   # FADEC STOW CMD
            (722, 420, 419),   # UNLOCK CONFIRMED
            (722, 434, 459),   # TR STOWED+LOCKED
        ]
        for sx, sy, ty in expected:
            self.assertIn((float(sx), float(sy), 844.0, float(ty)), set(self.lines),
                          msg=f"output arrow from ({sx},{sy}) must end at (844,{ty})")

    def test_fadec_deploy_arrow_not_inside_box(self):
        """Specific guard against the x2=860 regression — the FADEC DEPLOY
        CMD box left edge is at x=844, so any endpoint x ≥ 844 would put
        the arrow-head inside the box."""
        for l in self.lines:
            _, _, x2, _ = l
            if x2 > 844:
                # Only non-output lines may legitimately go past x=844
                # (the output column itself, vertical spines etc.). The
                # six output arrows above are all tagged x2=844; anything
                # else crossing should NOT be one of the source→output lines.
                pass
        # Direct guard: no line from state col (x1=722) to x2>=845.
        bad = [l for l in self.lines if l[0] == 722 and l[2] > 844]
        self.assertEqual(bad, [],
                         msg=f"state-machine→output arrows must stop at x=844; bad: {bad}")

    # ---- tr_wow must feed state-machine S1, not the mid-column gap ----

    def test_tr_wow_lands_at_s1(self):
        """WOW FILTER → state-machine bus now ends at (522, 108), which
        is S1 GND_STOWED_LOCKED left-center. Previously it ended at
        (518, 200) — inside the S2/S3 divider gap."""
        self.assertIn((460.0, 108.0, 522.0, 108.0), set(self.lines),
                      msg="tr_wow bus must terminate at S1 left-center (522,108)")
        # Old mis-aimed terminus must be gone.
        self.assertNotIn((460.0, 200.0, 518.0, 200.0), set(self.lines))

    # ---- Text overflow / overlap guards ----

    def test_key_parameters_rect_tall_enough_for_four_rows(self):
        """Previously rect height=48 but the fourth line baseline y=549
        was below rect bottom y=548 — last row overflowed the box.
        After fix rect height=54."""
        self.assertIn('<rect x="522" y="500" width="200" height="54"', self.html,
                      msg="KEY PARAMETERS rect must be tall enough for four lines of text")

    def test_reset_feedback_label_outside_s4_box(self):
        """Previously the 'RESET feedback' label at (600, 312) sat on top
        of the S4 DEPLOYED rect bottom (y=310). After the fix the label
        lives in the filter/state gap at x=455, y=319 — clear of both S4
        and the 'TRA回收 / stow_cmd' label at (640, 328)."""
        self.assertIn('<text x="455" y="319"', self.html,
                      msg="RESET feedback label must be at (455,319) to avoid S4 overlap")
        self.assertNotIn('<text x="600" y="312"', self.html)


if __name__ == "__main__":
    unittest.main()
