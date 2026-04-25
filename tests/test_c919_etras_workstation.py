"""Phase C · static-asset and route tests for c919_etras_workstation.html.

Asserts structural invariants so the workstation page keeps its contract
with the adapter truth source (src/well_harness/adapters/c919_etras_adapter.py):

- Route serves 200 and contains key section IDs (lever, condition, HUD, outputs, SVG).
- SVG data-node ids are subset of the C919 ETRAS spec (components + logic_nodes).
- CSS + JS assets resolve at 200 and parse.
- Preset keys in HTML buttons match preset keys in the JS module.
- The 4 output cards exist and are keyed to the 4 FADEC/power signals.
"""
from __future__ import annotations

import http.client
import json
import re
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from well_harness.adapters.c919_etras_adapter import build_c919_etras_workbench_spec
from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = PROJECT_ROOT / "src" / "well_harness" / "static"
WORKSTATION_HTML = STATIC_DIR / "c919_etras_workstation.html"
WORKSTATION_CSS = STATIC_DIR / "c919_etras_workstation.css"
WORKSTATION_JS = STATIC_DIR / "c919_etras_workstation.js"


def _start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _http_get(port: int, path: str) -> tuple[int, str, str]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    content_type = resp.getheader("Content-Type", "")
    conn.close()
    return resp.status, content_type, body


def _http_post_json(port: int, path: str, payload: dict) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    body = json.dumps(payload)
    conn.request("POST", path, body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(data) if data else {}


class C919EtrasWorkstationStaticTests(unittest.TestCase):
    """Static-file invariants that don't need a running server."""

    def test_workstation_html_exists_and_has_key_section_ids(self):
        self.assertTrue(WORKSTATION_HTML.is_file(), "c919_etras_workstation.html missing")
        html = WORKSTATION_HTML.read_text(encoding="utf-8")
        for fragment in (
            "<title>C919 E-TRAS 逻辑控制工作台</title>",
            'id="etras-status-banner"',
            'id="etras-tra-lever"',
            'id="etras-n1k"',
            'id="etras-logic-chain"',
            'id="output-single-phase"',
            'id="output-three-phase"',
            'id="output-fadec-deploy"',
            'id="output-fadec-stow"',
            'id="etras-preset-status"',
            'id="etras-probability-node-list"',
            'id="etras-run-simulation"',
            'id="etras-sim-success-rate"',
            'id="etras-sim-top-causes"',
        ):
            self.assertIn(fragment, html, f"missing fragment: {fragment}")

    def test_workstation_css_exists(self):
        self.assertTrue(WORKSTATION_CSS.is_file(), "c919_etras_workstation.css missing")
        css = WORKSTATION_CSS.read_text(encoding="utf-8")
        # CSS custom properties for the aviation theme
        self.assertIn("--etras-accent:", css)
        self.assertIn("--etras-active:", css)
        self.assertIn(".chain-node[data-state=\"active\"]", css)
        self.assertIn(".chain-logic[data-state=\"active\"]", css)
        self.assertIn(".probability-node-row", css)
        self.assertIn("[data-sim-cause=\"top\"]", css)

    def test_workstation_js_exists_and_posts_to_system_snapshot(self):
        self.assertTrue(WORKSTATION_JS.is_file(), "c919_etras_workstation.js missing")
        js = WORKSTATION_JS.read_text(encoding="utf-8")
        self.assertIn('const API_URL = "/api/system-snapshot"', js)
        self.assertIn('const SYSTEM_ID = "c919-etras"', js)
        self.assertIn("buildSnapshot()", js)
        self.assertIn("renderChainSvg(", js)
        self.assertIn("const RELIABILITY_NODES = [", js)
        self.assertIn("function runReliabilitySimulation()", js)
        self.assertIn("function seededRandom(seed)", js)
        self.assertNotIn('"/api/monte-carlo/run"', js)

    def test_workstation_js_renders_sw1_sw2_hint_window(self):
        """SW1/SW2 'in window' hint spans must be wired in renderLeverHud.

        Codex round#2 P2: HTML exposed `etras-sw1-hint-window` /
        `etras-sw2-hint-window` but JS never updated them — TRA slider movement
        left the hint stuck at 'off' forever, misleading operators.
        """
        js = WORKSTATION_JS.read_text(encoding="utf-8")
        # Refs registered
        self.assertRegex(js, r'sw1HintWindow\s*:\s*\$\("etras-sw1-hint-window"\)',
                         "sw1HintWindow ref missing")
        self.assertRegex(js, r'sw2HintWindow\s*:\s*\$\("etras-sw2-hint-window"\)',
                         "sw2HintWindow ref missing")
        # renderLeverHud writes them based on TRA window membership
        self.assertIn("readouts.sw1HintWindow", js,
                      "renderLeverHud must update sw1HintWindow")
        self.assertIn("readouts.sw2HintWindow", js,
                      "renderLeverHud must update sw2HintWindow")
        # Window thresholds match adapter spec: SW1 [-6.2, -1.4], SW2 [-9.8, -5.0]
        self.assertIn("-6.2", js, "SW1 lower threshold -6.2 missing")
        self.assertIn("-1.4", js, "SW1 upper threshold -1.4 missing")
        self.assertIn("-9.8", js, "SW2 lower threshold -9.8 missing")
        self.assertIn("-5.0", js, "SW2 upper threshold -5.0 missing")

    def test_workstation_js_uses_explicit_sw1_sw2_inputs(self):
        """SW1/SW2 must come from explicit DOM checkboxes, not auto-derived from TRA.

        Reason: adapter requires explicit atltla/apwtla snapshot fields. Auto-deriving
        them from TRA bypasses the latch semantics — once SW1/SW2 close during the
        lever sweep they stay set, and the adapter consumes the latched state directly.
        Codex C-7 BUG#1/#2 caught this; the regression check guards against revival.

        Whitespace-tolerant — keyed on identifiers, not column spacing.
        """
        js = WORKSTATION_JS.read_text(encoding="utf-8")
        # Inputs object refs (whitespace-tolerant)
        self.assertRegex(js, r'atltla\s*:\s*\$\("etras-atltla"\)',
                         "atltla input ref missing from `inputs` object")
        self.assertRegex(js, r'apwtla\s*:\s*\$\("etras-apwtla"\)',
                         "apwtla input ref missing from `inputs` object")
        # buildSnapshot reads from explicit inputs (whitespace-tolerant)
        self.assertRegex(js, r'apwtla\s*:\s*checked\(inputs\.apwtla\)',
                         "buildSnapshot must read apwtla from inputs.apwtla")
        self.assertRegex(js, r'atltla\s*:\s*checked\(inputs\.atltla\)',
                         "buildSnapshot must read atltla from inputs.atltla")
        self.assertNotIn("computeAtltla", js,
                         "auto-derive helper computeAtltla must be removed")
        self.assertNotIn("computeApwtla", js,
                         "auto-derive helper computeApwtla must be removed")

    def test_workstation_js_reliability_loop_uses_continue_not_return(self):
        """Monte Carlo trial loop must use `continue` on success, not `return`.

        Reason: Codex C-7 BUG#4 — early `return` exited the whole simulation on the
        first successful trial, producing successCount=1 / failureCount=nTrials-1.
        Loop body MUST iterate all trials.

        Uses regex on the whole success branch, robust to refactors that preserve
        semantics.
        """
        js = WORKSTATION_JS.read_text(encoding="utf-8")
        # Match the success branch as a whole: { successCount += 1; continue; }
        # Whitespace and intermediate statements tolerated, but `continue;` mandatory
        # and `return` (any form) within the same branch forbidden.
        success_branch_re = re.compile(
            r"if\s*\(\s*!failedNodeIds\.length\s*\)\s*\{(?P<body>[^}]*)\}",
            re.DOTALL,
        )
        match = success_branch_re.search(js)
        self.assertIsNotNone(match, "success branch `if (!failedNodeIds.length) { ... }` not found")
        body = match.group("body")
        self.assertIn("continue", body,
                      "success branch must continue to next trial, not return")
        self.assertNotRegex(body, r"\breturn\b",
                            "success branch must NOT contain return — bug regression")

    def test_workstation_svg_data_nodes_subset_of_adapter_spec(self):
        """Every data-node in the chain SVG ⊂ adapter spec components ∪ logic_nodes.

        Same contract that P43-02.5 enforced on chat.html's c919 section.
        """
        html = WORKSTATION_HTML.read_text(encoding="utf-8")
        # Extract data-node values from the SVG section only
        svg_start = html.find('id="etras-logic-chain"')
        svg_end = html.find("</svg>", svg_start)
        self.assertGreater(svg_end, svg_start, "chain SVG bounds not found")
        svg_section = html[svg_start:svg_end]

        node_ids = set(re.findall(r'data-node="([a-z0-9_]+)"', svg_section))
        self.assertGreater(len(node_ids), 0, "no data-node ids found in SVG")

        spec = build_c919_etras_workbench_spec()
        component_ids = {c["id"] for c in spec.get("components", [])}
        logic_node_ids = {ln["id"] for ln in spec.get("logic_nodes", [])}
        allowed = component_ids | logic_node_ids

        unknown = node_ids - allowed
        self.assertFalse(
            unknown,
            f"data-node ids not in adapter spec: {sorted(unknown)}\n"
            f"allowed: {sorted(allowed)}",
        )

    def test_every_visible_svg_node_has_probability_model(self):
        """Every visible chain node gets a normal-operation probability input."""
        html = WORKSTATION_HTML.read_text(encoding="utf-8")
        js = WORKSTATION_JS.read_text(encoding="utf-8")

        svg_start = html.find('id="etras-logic-chain"')
        svg_end = html.find("</svg>", svg_start)
        self.assertGreater(svg_end, svg_start, "chain SVG bounds not found")
        svg_section = html[svg_start:svg_end]
        svg_node_ids = set(re.findall(r'data-node="([a-z0-9_]+)"', svg_section))

        reliability_start = js.find("const RELIABILITY_NODES = [")
        reliability_end = js.find("const RELIABILITY_NODE_BY_ID", reliability_start)
        self.assertGreater(reliability_end, reliability_start, "RELIABILITY_NODES block not found")
        reliability_section = js[reliability_start:reliability_end]
        probability_node_ids = set(re.findall(r'id:\s*"([a-z0-9_]+)"', reliability_section))

        self.assertEqual(
            svg_node_ids,
            probability_node_ids,
            "Normal-operation probability coverage must match every visible SVG data-node.",
        )

    def test_preset_buttons_match_js_preset_keys(self):
        """HTML <button data-preset> keys must match the JS `presets` object keys."""
        html = WORKSTATION_HTML.read_text(encoding="utf-8")
        js = WORKSTATION_JS.read_text(encoding="utf-8")

        html_keys = set(re.findall(r'data-preset="([a-z0-9\-]+)"', html))
        # Extract the keys from the JS `presets = { ... }` object header lines.
        # Match lines like `  "nominal-stowed": {` within the presets block.
        js_keys = set(re.findall(r'"([a-z0-9\-]+)":\s*\{\s*\n\s*label:', js))

        self.assertEqual(
            html_keys, js_keys,
            f"HTML preset buttons {sorted(html_keys)} do not match JS keys {sorted(js_keys)}",
        )

    def test_demo_html_links_to_workstation(self):
        """demo.html unified nav should include a link to the E-TRAS workstation."""
        demo_html_path = STATIC_DIR / "demo.html"
        demo_html = demo_html_path.read_text(encoding="utf-8")
        self.assertIn("/c919_etras_workstation.html", demo_html)
        # Phase UI-D (2026-04-22): unified nav uses "C919 E-TRAS" (not 逻辑工作台).
        self.assertIn("C919 E-TRAS", demo_html)


class C919EtrasWorkstationServerTests(unittest.TestCase):
    """Live-server integration tests (spin up demo_server in-process)."""

    def test_route_serves_html_200(self):
        server, thread = _start_server()
        try:
            port = server.server_port
            status, content_type, body = _http_get(port, "/c919_etras_workstation.html")
            self.assertEqual(status, 200)
            self.assertIn("text/html", content_type)
            self.assertIn("C919 E-TRAS 逻辑控制工作台", body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_assets_serve_200(self):
        server, thread = _start_server()
        try:
            port = server.server_port
            for path, ct_hint in (
                ("/c919_etras_workstation.css", "text/css"),
                ("/c919_etras_workstation.js",  "application/javascript"),
            ):
                status, content_type, body = _http_get(port, path)
                self.assertEqual(status, 200, f"{path} returned {status}")
                self.assertIn(ct_hint, content_type, f"{path} content-type={content_type}")
                self.assertGreater(len(body), 0, f"{path} body empty")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_system_snapshot_post_landing_deploy_activates_all_four_logic_nodes(self):
        """Sanity: landing-deploy-like snapshot reaches completion_reached=True."""
        server, thread = _start_server()
        try:
            port = server.server_port
            snapshot = {
                "tra_deg": -25.0,
                "n1k_percent": 60.0,
                "engine_running": True,
                "tr_inhibited": False,
                "lgcu1_mlg_wow_value": True, "lgcu1_mlg_wow_valid": True,
                "lgcu2_mlg_wow_value": True, "lgcu2_mlg_wow_valid": True,
                "tr_wow": True,
                "tls_ls_a_valid": True, "tls_ls_a_unlocked": True,
                "tls_ls_b_valid": True, "tls_ls_b_unlocked": True,
                "pls_ls_a_locked": False, "pls_ls_b_locked": False,
                "left_pylon_ls_a_valid": True, "left_pylon_ls_a_unlocked": True,
                "left_pylon_ls_b_valid": True, "left_pylon_ls_b_unlocked": True,
                "right_pylon_ls_a_valid": True, "right_pylon_ls_a_unlocked": True,
                "right_pylon_ls_b_valid": True, "right_pylon_ls_b_unlocked": True,
                "apwtla": True, "atltla": True,
                "vdt_sensor_valid": True,
                "e_tras_over_temp_fault": False,
                "trcu_power_on": True,
                "tr_position_percent": 85.0,
                "prev_eicu_cmd3": True,
                "comm2_timer_s": 1.0,
                "lock_unlock_confirm_s": 0.5,
                "tr_position_deployed_confirm_s": 0.5,
                "tr_stowed_locked_confirm_s": 0.0,
            }
            status, payload = _http_post_json(port, "/api/system-snapshot", {
                "system_id": "c919-etras",
                "snapshot": snapshot,
            })
            self.assertEqual(status, 200)
            self.assertIn("truth_evaluation", payload)
            evaluation = payload["truth_evaluation"]
            active = set(evaluation.get("active_logic_node_ids", []))
            self.assertEqual(
                active,
                {"ln_eicu_cmd2", "ln_eicu_cmd3", "ln_tr_command3_enable", "ln_fadec_deploy_command"},
                f"unexpected active set: {active}",
            )
            self.assertTrue(evaluation.get("completion_reached"), "should reach completion")
            asserted = evaluation.get("asserted_component_values", {})
            self.assertTrue(asserted.get("fadec_deploy_command"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


class C919EtrasWorkstationPresetAdapterIntegrationTests(unittest.TestCase):
    """Integration: each JS preset's snapshot reaches the documented adapter outcome.

    Mirrors the JS preset definitions in c919_etras_workstation.js. If a preset is
    edited, this test must be updated. Catches the regression Codex C-7 found:
    presets that auto-derived atltla/apwtla from TRA appeared to work in the smoke
    test (which hardcoded both true) but failed in real preset-driven flows.
    """

    # Baseline matches the JS `nominal-stowed` preset.
    NOMINAL_STOWED_SNAPSHOT = {
        "tra_deg": 0.0,
        "n1k_percent": 35.0,
        "engine_running": True,
        "tr_inhibited": False,
        "lgcu1_mlg_wow_value": True, "lgcu1_mlg_wow_valid": True,
        "lgcu2_mlg_wow_value": True, "lgcu2_mlg_wow_valid": True,
        "tr_wow": True,
        "tls_ls_a_valid": True, "tls_ls_a_unlocked": False,
        "tls_ls_b_valid": True, "tls_ls_b_unlocked": False,
        "pls_ls_a_locked": True, "pls_ls_b_locked": True,
        "left_pylon_ls_a_valid": True, "left_pylon_ls_a_unlocked": False,
        "left_pylon_ls_b_valid": True, "left_pylon_ls_b_unlocked": False,
        "right_pylon_ls_a_valid": True, "right_pylon_ls_a_unlocked": False,
        "right_pylon_ls_b_valid": True, "right_pylon_ls_b_unlocked": False,
        "apwtla": False, "atltla": False,
        "vdt_sensor_valid": True,
        "e_tras_over_temp_fault": False,
        "trcu_power_on": True,
        "tr_position_percent": 0.0,
        "prev_eicu_cmd3": False,
        "comm2_timer_s": 0.0,
        "lock_unlock_confirm_s": 0.0,
        "tr_position_deployed_confirm_s": 0.0,
        "tr_stowed_locked_confirm_s": 2.0,
    }

    def _post_snapshot(self, snapshot: dict) -> dict:
        server, thread = _start_server()
        try:
            port = server.server_port
            status, payload = _http_post_json(port, "/api/system-snapshot", {
                "system_id": "c919-etras",
                "snapshot": snapshot,
            })
            self.assertEqual(status, 200, f"snapshot POST returned {status}")
            return payload["truth_evaluation"]
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_preset_landing_deploy_reaches_completion(self):
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": -25.0,
            "n1k_percent": 60.0,
            "tr_position_percent": 85.0,
            "atltla": True, "apwtla": True,
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": True, "right_pylon_ls_b_unlocked": True,
            "comm2_timer_s": 1.0,
            "lock_unlock_confirm_s": 0.5,
            "tr_position_deployed_confirm_s": 0.5,
            "tr_stowed_locked_confirm_s": 0.0,
            "prev_eicu_cmd3": True,
        })
        evaluation = self._post_snapshot(snap)
        active = set(evaluation.get("active_logic_node_ids", []))
        self.assertEqual(
            active,
            {"ln_eicu_cmd2", "ln_eicu_cmd3", "ln_tr_command3_enable", "ln_fadec_deploy_command"},
            "landing-deploy preset must light all 4 deploy logic nodes",
        )
        self.assertTrue(evaluation.get("completion_reached"))
        asserted = evaluation.get("asserted_component_values", {})
        self.assertTrue(asserted.get("fadec_deploy_command"))
        self.assertFalse(asserted.get("fadec_stow_command"))

    def test_preset_stow_return_reaches_stow_command(self):
        """stow-return: n1k=25 (< adapter MAX_N1K_STOW_LIMIT_PERCENT=30) is required."""
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": 0.0,
            "n1k_percent": 25.0,
            "tr_position_percent": 30.0,
            "atltla": False, "apwtla": False,
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": True, "right_pylon_ls_b_unlocked": True,
            "prev_eicu_cmd3": True,
            "tr_stowed_locked_confirm_s": 0.0,
        })
        evaluation = self._post_snapshot(snap)
        asserted = evaluation.get("asserted_component_values", {})
        self.assertTrue(
            asserted.get("fadec_stow_command"),
            "stow-return preset must trigger fadec_stow_command (n1k must be < 30%)",
        )

    def test_preset_max_reverse_n1k_below_deploy_gate(self):
        """max-reverse must keep n1k below adapter deploy limit (84%).

        Codex round#2 caught: original n1k=90 exceeded the gate, dropping
        fadec_deploy_command and breaking the preset's intended outcome.
        """
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": -32.0,
            "n1k_percent": 82.0,  # corrected value — must be < 84%
            "tr_position_percent": 100.0,
            "atltla": True, "apwtla": True,
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": True, "right_pylon_ls_b_unlocked": True,
            "comm2_timer_s": 1.0,
            "lock_unlock_confirm_s": 0.5,
            "tr_position_deployed_confirm_s": 0.5,
            "tr_stowed_locked_confirm_s": 0.0,
            "prev_eicu_cmd3": True,
        })
        evaluation = self._post_snapshot(snap)
        asserted = evaluation.get("asserted_component_values", {})
        self.assertTrue(
            asserted.get("fadec_deploy_command"),
            "max-reverse n1k=82 must still pass the < 84% deploy gate",
        )
        self.assertTrue(evaluation.get("completion_reached"),
                        "max-reverse must reach completion (deploy fully asserted)")

    def test_preset_max_reverse_n1k_at_old_buggy_value_breaks_deploy(self):
        """Old max-reverse value (n1k=90) must NOT trigger fadec_deploy_command —
        confirms adapter deploy gate is < 84%."""
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": -32.0,
            "n1k_percent": 90.0,  # the buggy value Codex round#2 P1 flagged
            "tr_position_percent": 100.0,
            "atltla": True, "apwtla": True,
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": True, "right_pylon_ls_b_unlocked": True,
            "comm2_timer_s": 1.0,
            "lock_unlock_confirm_s": 0.5,
            "tr_position_deployed_confirm_s": 0.5,
            "tr_stowed_locked_confirm_s": 0.0,
            "prev_eicu_cmd3": True,
        })
        evaluation = self._post_snapshot(snap)
        asserted = evaluation.get("asserted_component_values", {})
        self.assertFalse(
            asserted.get("fadec_deploy_command"),
            "n1k=90% must NOT pass deploy gate — adapter limit is < 84%",
        )

    def test_preset_lock_fault_does_not_complete_deploy(self):
        """lock-fault: partial unlock (right pylon stuck locked) must block deploy.

        Codex round#2 P1 caught: inheriting tr_stowed_locked_confirm_s=2.0 from
        nominal-stowed forced eicu_cmd3=False via the adapter reset path, so the
        preset never reached the intended fault state. Fix: zero stowedConfirm.
        """
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": -15.0,
            "n1k_percent": 60.0,
            "atltla": True, "apwtla": True,
            "prev_eicu_cmd3": True,
            "tr_stowed_locked_confirm_s": 0.0,  # the fix
            # Partial unlock — right pylon stuck locked
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": False,  # fault
            "right_pylon_ls_b_unlocked": False,
            "comm2_timer_s": 1.0,
        })
        evaluation = self._post_snapshot(snap)
        asserted = evaluation.get("asserted_component_values", {})
        # eicu_cmd3 should be reachable (SR latch path is open)
        active = set(evaluation.get("active_logic_node_ids", []))
        self.assertIn("ln_eicu_cmd3", active,
                      "lock-fault: SR latch path must be open (no stow reset)")
        # But fadec_deploy_command must NOT fire — partial unlock blocks tr_command3_enable
        self.assertFalse(
            asserted.get("fadec_deploy_command"),
            "lock-fault: partial unlock must block fadec_deploy_command",
        )
        self.assertFalse(
            evaluation.get("completion_reached"),
            "lock-fault: must NOT reach completion (this is the fault scenario)",
        )

    def test_preset_stow_return_blocked_when_n1k_exceeds_stow_limit(self):
        """Old stow-return value (n1k=45) must NOT trigger stow command — adapter limit is 30%."""
        snap = dict(self.NOMINAL_STOWED_SNAPSHOT)
        snap.update({
            "tra_deg": 0.0,
            "n1k_percent": 45.0,  # the buggy value Codex C-7 BUG#3 flagged
            "tr_position_percent": 30.0,
            "tls_ls_a_unlocked": True, "tls_ls_b_unlocked": True,
            "pls_ls_a_locked": False, "pls_ls_b_locked": False,
            "left_pylon_ls_a_unlocked": True, "left_pylon_ls_b_unlocked": True,
            "right_pylon_ls_a_unlocked": True, "right_pylon_ls_b_unlocked": True,
            "prev_eicu_cmd3": True,
        })
        evaluation = self._post_snapshot(snap)
        asserted = evaluation.get("asserted_component_values", {})
        self.assertFalse(
            asserted.get("fadec_stow_command"),
            "n1k=45% must NOT pass stow gate — confirms adapter MAX_N1K_STOW_LIMIT_PERCENT=30",
        )


if __name__ == "__main__":
    unittest.main()
