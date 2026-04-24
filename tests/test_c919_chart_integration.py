"""Regression guards for the C919 E-TRAS panel time-series chart drawer
and the shared timeseries_chart.js asset served from both servers.

These tests assert structural wiring (HTML markup + route table) rather
than runtime rendering behavior — the chart itself is tested via its
Python-driven data contract in test_fantui_tick_runtime.py.
"""
from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
C919_INDEX = REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel" / "index.html"
C919_PANEL_SERVER = REPO_ROOT / "scripts" / "c919_etras_panel_server.py"
TIMESERIES_JS = REPO_ROOT / "src" / "well_harness" / "static" / "timeseries_chart.js"


class C919ChartDrawerMarkupTests(unittest.TestCase):

    def setUp(self):
        self.html = C919_INDEX.read_text(encoding="utf-8")

    def test_drawer_container_present(self):
        self.assertIn('id="tscDrawer"', self.html)
        self.assertIn('class="tsc-drawer"', self.html)
        self.assertIn('id="tsc-svg"', self.html)
        self.assertIn('id="tsc-legend"', self.html)

    def test_shared_chart_script_is_loaded_before_panel_script(self):
        idx_chart = self.html.find('src="/timeseries_chart.js"')
        # Compare against the STATES constant — first identifier the panel IIFE
        # references. Must come AFTER the external chart module is loaded.
        idx_states_const = self.html.find("const STATES = [")
        self.assertGreater(idx_chart, 0, "/timeseries_chart.js must be included")
        self.assertGreater(idx_states_const, 0, "STATES constant must exist")
        self.assertLess(idx_chart, idx_states_const,
                        msg="chart module must load before the panel IIFE")

    def test_toggle_button_wired(self):
        self.assertIn('id="btnChart"', self.html)
        self.assertIn('onclick="toggleChart()"', self.html)
        # Drawer opens by toggling the `open` class
        self.assertIn("drawer.classList.toggle('open'", self.html)

    def test_reset_clears_chart_buffer_and_samples_counter(self):
        # When resetSim runs, it must: call chart.clear(), reset TR buffer,
        # reset the sample counter, and POST /api/reset.
        reset_fn_start = self.html.find("async function resetSim")
        reset_fn_end = self.html.find("function sync()", reset_fn_start)
        reset_body = self.html[reset_fn_start:reset_fn_end]
        self.assertIn("_resetTrPos()", reset_body)
        self.assertIn("c919Chart.clear()", reset_body)
        self.assertIn("'0 samples'", reset_body)
        self.assertIn("/api/reset", reset_body)

    def test_tick_throttling_guard_present(self):
        """Drawer-closed → no refresh; drawer-open → refresh throttled to >400ms."""
        self.assertIn("_lastChartUpdate", self.html)
        self.assertIn("> 400", self.html)

    def test_chart_lanes_match_state_machine_code_space(self):
        """C919_STATE_INDEX must map the 12 known states S0..S10 + SF."""
        for state in ("S0_AIR_STOWED_LOCKED", "S10_STOWED_LOCKED_POWER_OFF",
                      "SF_ABORT_OR_FAULT", "S4_DEPLOYING", "S6_MAX_REVERSE"):
            self.assertIn(f"'{state}'", self.html,
                          msg=f"chart state map must cover {state}")


class C919PanelServerAssetRoutingTests(unittest.TestCase):
    """Route-table assertion: the :9191 server must serve the shared chart
    module from the parent static dir so the panel UI can `<script src>`
    it without cross-origin."""

    def test_panel_server_serves_timeseries_chart_js(self):
        src = C919_PANEL_SERVER.read_text(encoding="utf-8")
        self.assertIn('path == "/timeseries_chart.js"', src)
        self.assertIn('SHARED_STATIC_ROOT / "timeseries_chart.js"', src)

    def test_shared_js_file_exists(self):
        self.assertTrue(TIMESERIES_JS.is_file(),
                        msg=f"shared chart module missing at {TIMESERIES_JS}")


if __name__ == "__main__":
    unittest.main()
