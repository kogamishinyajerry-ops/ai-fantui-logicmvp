"""Regression tests for FANTUI stateful tick runtime and HTTP surface.

Covers:
  1. FantuiTickSystem in-process state evolution (switches, plant, controller).
  2. /api/fantui/tick + /api/fantui/log + /api/fantui/reset + /api/fantui/state
     over the demo_server http handler.
  3. /fan_console.html and /timeseries_chart.js are served.
  4. TimeseriesChart.buildPayload-style record field coverage (schema guard).
"""
from __future__ import annotations

import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from well_harness.demo_server import DemoRequestHandler
from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
from well_harness.models import PilotInputs


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = REPO_ROOT / "src" / "well_harness" / "static"


def _pilot(**overrides) -> PilotInputs:
    defaults = dict(
        radio_altitude_ft=4.0,
        tra_deg=0.0,
        engine_running=True,
        aircraft_on_ground=True,
        reverser_inhibited=False,
        eec_enable=True,
        n1k=55.0,
        max_n1k_deploy_limit=85.0,
    )
    defaults.update(overrides)
    return PilotInputs(**defaults)


class FantuiTickSystemUnitTests(unittest.TestCase):
    """Pure-Python tests: no HTTP, no server."""

    def test_reset_clears_time_plant_switches_and_log(self):
        sys_ = FantuiTickSystem()
        sys_.tick(_pilot(tra_deg=-8.0), 0.3)
        sys_.tick(_pilot(tra_deg=-15.0), 0.3)
        self.assertGreater(sys_.t_s, 0)
        self.assertGreater(len(sys_.records()), 0)
        sys_.reset()
        self.assertEqual(sys_.t_s, 0.0)
        self.assertEqual(len(sys_.records()), 0)
        self.assertFalse(sys_.switch_state.sw1)
        self.assertFalse(sys_.switch_state.sw2)
        self.assertEqual(sys_.plant_state.deploy_position_percent, 0.0)

    def test_tra_sweep_latches_switches_and_activates_gates(self):
        """Sweeping TRA from 0 → -25 across the SW1/SW2 windows should:
        (a) latch SW1 once the lever enters [-1.4, -6.2] and leave it latched
            as TRA moves deeper, (b) latch SW2 similarly for [-5, -9.8],
            (c) propagate to logic1/logic3 once supporting conditions are met.
        """
        sys_ = FantuiTickSystem()
        for tra in (0.0, -3.0, -8.0, -15.0, -25.0):
            sys_.tick(_pilot(tra_deg=tra), 0.3)

        recs = sys_.records()
        self.assertEqual(len(recs), 5)

        # TRA=-3° → SW1 latched; SW2 still false
        self.assertTrue(recs[1]["sw1"])
        self.assertFalse(recs[1]["sw2"])

        # TRA=-8° → both latched
        self.assertTrue(recs[2]["sw1"])
        self.assertTrue(recs[2]["sw2"])

        # TRA=-25° → both still latched (not reset until lever returns >-1.4°)
        self.assertTrue(recs[4]["sw1"])
        self.assertTrue(recs[4]["sw2"])

    def test_plant_advances_deploy_position_under_drive(self):
        """After logic3 arms the motor and TLS/PLS indications come true,
        the plant should start accumulating deploy_position_percent."""
        sys_ = FantuiTickSystem()
        # Drive repeatedly at TRA=-15° (below logic3 threshold -11.74°) with
        # TLS/PLS populated by the plant's power integrators.
        for _ in range(20):
            sys_.tick(_pilot(tra_deg=-15.0), 0.1)
        last = sys_.records()[-1]
        self.assertGreater(last["deploy_position_percent"], 0.0)
        # VDT90 sensor should eventually trip once position ≥90%.
        # (Default deploy_rate is 30%/s, 20 × 0.1 = 2s → ~60% by then, so we
        # only check non-trivial advancement here; full VDT90 below.)

    def test_plant_reaches_vdt90_with_enough_ticks(self):
        sys_ = FantuiTickSystem()
        # 4 seconds of continuous drive @ 30%/s = 120% (capped at 100%).
        for _ in range(40):
            sys_.tick(_pilot(tra_deg=-15.0), 0.1)
        last = sys_.records()[-1]
        self.assertTrue(last["deploy_90_percent_vdt"])
        self.assertGreaterEqual(last["deploy_position_percent"], 90.0)

    def test_tick_rejects_non_positive_dt(self):
        sys_ = FantuiTickSystem()
        with self.assertRaises(ValueError):
            sys_.tick(_pilot(), 0.0)
        with self.assertRaises(ValueError):
            sys_.tick(_pilot(), -0.1)

    def test_tick_rejects_non_finite_dt(self):
        """CRITICAL regression (Codex 2026-04-24): ``dt_s = NaN`` used to
        silently poison ``_t_s`` and emit non-standard-JSON responses."""
        import math as _m
        sys_ = FantuiTickSystem()
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                sys_.tick(_pilot(), bad)
        # tick_with_count applies the same guard.
        with self.assertRaises(ValueError):
            sys_.tick_with_count(_pilot(), float("nan"))
        # And state is untouched after the guards fire.
        self.assertTrue(_m.isfinite(sys_.t_s))
        self.assertEqual(len(sys_.records()), 0)

    def test_tick_accepts_dt_s_equal_to_one_second_boundary(self):
        """The HTTP ceiling is ``dt_s <= 1.0`` inclusive; the runtime must
        accept the exact boundary without raising."""
        sys_ = FantuiTickSystem()
        rec = sys_.tick(_pilot(), 1.0)
        self.assertAlmostEqual(rec.t_s, 1.0, places=6)
        self.assertEqual(len(sys_.records()), 1)

    def test_tick_concurrent_writers_and_readers_do_not_raise(self):
        """MAJOR regression (Codex 2026-04-24): ``records()`` iterating the
        deque while ``tick()`` appended used to raise
        ``RuntimeError: deque mutated during iteration``. With the internal
        lock the two paths are safe regardless of caller holding an outer
        lock.
        """
        import threading as _t
        sys_ = FantuiTickSystem()
        errors = []

        def writer():
            try:
                for _ in range(2000):
                    sys_.tick(_pilot(tra_deg=-8.0), 0.001)
            except Exception as exc:  # pragma: no cover
                errors.append(("writer", repr(exc)))

        def reader():
            try:
                for _ in range(2000):
                    sys_.records()
            except Exception as exc:  # pragma: no cover
                errors.append(("reader", repr(exc)))

        threads = [_t.Thread(target=writer) for _ in range(2)] + \
                  [_t.Thread(target=reader) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [], msg=f"concurrent access raised: {errors}")
        # All writers completed despite interleaved reads.
        self.assertEqual(len(sys_.records()), FantuiTickSystem.LOG_CAP)

    def test_snapshot_returns_coherent_atomic_state(self):
        sys_ = FantuiTickSystem()
        sys_.tick(_pilot(tra_deg=-8.0), 0.1)
        snap = sys_.snapshot()
        for k in ("t_s", "sw1", "sw2", "deploy_position_percent",
                  "tls_unlocked_ls", "sample_count"):
            self.assertIn(k, snap)
        self.assertEqual(snap["sample_count"], 1)

    def test_log_ring_buffer_caps_at_LOG_CAP(self):
        sys_ = FantuiTickSystem()
        cap = FantuiTickSystem.LOG_CAP
        for _ in range(cap + 50):
            sys_.tick(_pilot(), 0.05)
        recs = sys_.records()
        self.assertEqual(len(recs), cap)
        # The oldest surviving record should NOT be at t=0.05 (the first one
        # was dropped); first surviving t_s must be well past 50 ticks in.
        self.assertGreater(recs[0]["t_s"], 50 * 0.05 - 1e-6)

    def test_record_dict_has_every_field_chart_module_expects(self):
        """timeseries_chart.js C919 + FANTUI series definitions read these
        fields from each record. If the runtime drops any of them, the chart
        will render empty polylines silently — hence this explicit guard.
        """
        sys_ = FantuiTickSystem()
        sys_.tick(_pilot(tra_deg=-8.0), 0.1)
        rec = sys_.records()[-1]
        required = {
            "t_s", "radio_altitude_ft", "tra_deg",
            "engine_running", "aircraft_on_ground", "reverser_inhibited",
            "eec_enable", "n1k", "max_n1k_deploy_limit",
            "sw1", "sw2", "deploy_position_percent",
            "tls_unlocked_ls", "all_pls_unlocked_ls", "deploy_90_percent_vdt",
            "logic1_active", "logic2_active", "logic3_active", "logic4_active",
            "tls_115vac_cmd", "etrac_540vdc_cmd", "eec_deploy_cmd",
            "pls_power_cmd", "pdu_motor_cmd",
            "throttle_electronic_lock_release_cmd",
        }
        missing = required - set(rec.keys())
        self.assertEqual(missing, set(), msg=f"tick record missing: {missing}")


class ParsePilotInputsTests(unittest.TestCase):

    def test_defaults_fill_in_missing_fields(self):
        pilot = parse_pilot_inputs({})
        self.assertEqual(pilot.radio_altitude_ft, 0.0)
        self.assertTrue(pilot.aircraft_on_ground)
        self.assertTrue(pilot.eec_enable)
        self.assertEqual(pilot.n1k, 50.0)

    def test_rejects_non_numeric_field(self):
        with self.assertRaises(ValueError):
            parse_pilot_inputs({"n1k": "abc"})
        with self.assertRaises(ValueError):
            parse_pilot_inputs({"tra_deg": None})

    def test_rejects_non_boolean_field(self):
        with self.assertRaises(ValueError):
            parse_pilot_inputs({"engine_running": "yes"})


class FantuiHttpEndpointTests(unittest.TestCase):
    """End-to-end checks against the DemoRequestHandler.

    Each test starts a fresh server on a random port because the fantui
    singleton is module-level and persists otherwise.
    """

    def setUp(self):
        # Reset the module-level singleton so previous tests' state doesn't leak.
        from well_harness import demo_server
        demo_server._FANTUI_SYSTEM.reset()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _req(self, method, path, body=None):
        conn = http.client.HTTPConnection(self.host, self.port, timeout=5)
        if body is None:
            conn.request(method, path)
        else:
            conn.request(method, path, body=json.dumps(body),
                         headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        status = resp.status
        payload = resp.read().decode("utf-8")
        conn.close()
        try:
            parsed = json.loads(payload) if payload else None
        except json.JSONDecodeError:
            parsed = payload
        return status, parsed

    def test_tick_post_advances_state_and_log_accumulates(self):
        status, _ = self._req("POST", "/api/fantui/reset")
        self.assertEqual(status, 200)

        for tra in (-3.0, -8.0, -15.0):
            s, body = self._req("POST", "/api/fantui/tick",
                                {"tra_deg": tra, "engine_running": True,
                                 "aircraft_on_ground": True, "n1k": 55.0,
                                 "max_n1k_deploy_limit": 85.0, "dt_s": 0.3})
            self.assertEqual(s, 200)
            self.assertIn("t_s", body)

        s, log = self._req("GET", "/api/fantui/log")
        self.assertEqual(s, 200)
        self.assertEqual(len(log), 3)
        self.assertGreater(log[-1]["t_s"], 0)
        self.assertTrue(log[-1]["sw1"])
        self.assertTrue(log[-1]["sw2"])

    def test_reset_clears_log(self):
        self._req("POST", "/api/fantui/tick", {"tra_deg": -8.0, "dt_s": 0.3})
        _, log_before = self._req("GET", "/api/fantui/log")
        self.assertGreaterEqual(len(log_before), 1)

        s, body = self._req("POST", "/api/fantui/reset")
        self.assertEqual(s, 200)
        self.assertEqual(body, {"ok": True, "t_s": 0.0})

        _, log_after = self._req("GET", "/api/fantui/log")
        self.assertEqual(log_after, [])

    def test_state_endpoint_reports_current_snapshot(self):
        self._req("POST", "/api/fantui/reset")
        self._req("POST", "/api/fantui/tick", {"tra_deg": -8.0, "dt_s": 0.3})
        s, body = self._req("GET", "/api/fantui/state")
        self.assertEqual(s, 200)
        self.assertAlmostEqual(body["t_s"], 0.3, places=3)
        self.assertTrue(body["sw1"])
        self.assertTrue(body["sw2"])
        self.assertEqual(body["sample_count"], 1)

    def test_tick_rejects_out_of_range_dt(self):
        for bad_dt in (0.0, -0.1, 2.0, 100.0):
            s, body = self._req("POST", "/api/fantui/tick", {"dt_s": bad_dt})
            self.assertEqual(s, 400, msg=f"dt_s={bad_dt} should be 400")
            self.assertEqual(body.get("error"), "dt_s_out_of_range")

    def test_tick_accepts_dt_s_boundary_one(self):
        """dt_s=1.0 is the documented inclusive ceiling — must return 200."""
        s, body = self._req("POST", "/api/fantui/tick",
                            {"tra_deg": -8.0, "dt_s": 1.0, "engine_running": True})
        self.assertEqual(s, 200, msg=body)
        self.assertAlmostEqual(body["t_s"], 1.0, places=3)

    def test_tick_rejects_non_finite_dt_via_raw_json(self):
        """CRITICAL regression (Codex 2026-04-24): raw JSON ``NaN`` /
        ``Infinity`` tokens are accepted by Python's ``json.loads`` and used
        to permanently corrupt the tick clock. Must be rejected with 400.
        """
        # json.dumps(..., allow_nan=True) emits non-standard ``NaN`` / ``Infinity``
        # tokens that Python can parse back (but browsers cannot). The handler
        # must short-circuit before the value reaches ``FantuiTickSystem``.
        import http.client as _c

        for raw_body in (b'{"dt_s": NaN}',
                         b'{"dt_s": Infinity}',
                         b'{"dt_s": -Infinity}',
                         b'{"n1k": NaN}'):
            conn = _c.HTTPConnection(self.host, self.port, timeout=5)
            conn.request("POST", "/api/fantui/tick",
                         body=raw_body,
                         headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            conn.close()
            self.assertEqual(status, 400,
                             msg=f"raw {raw_body!r} should be rejected")
            self.assertIn(body.get("error"),
                          {"dt_s_out_of_range", "invalid_input"},
                          msg=f"unexpected error shape for {raw_body!r}: {body}")

        # After all the bad requests, the system clock is still finite.
        import math as _m
        s, state = self._req("GET", "/api/fantui/state")
        self.assertEqual(s, 200)
        self.assertTrue(_m.isfinite(state["t_s"]))

    def test_tick_rejects_invalid_input_types(self):
        s, body = self._req("POST", "/api/fantui/tick", {"n1k": "abc"})
        self.assertEqual(s, 400)
        self.assertEqual(body.get("error"), "invalid_input")

    def test_tick_endpoint_does_not_touch_existing_lever_snapshot_surface(self):
        """The stateless /api/lever-snapshot must be independent of the
        stateful tick state; driving one must not leak into the other."""
        # Advance fantui-tick
        for _ in range(3):
            self._req("POST", "/api/fantui/tick", {"tra_deg": -15.0, "dt_s": 0.1})
        # lever-snapshot should still evaluate from its own (stateless) input
        s, snap = self._req("POST", "/api/lever-snapshot", {
            "radio_altitude_ft": 100.0, "tra_deg": 0.0,  # clearly air/forward
            "engine_running": False, "aircraft_on_ground": False,
            "reverser_inhibited": False, "eec_enable": True,
            "n1k": 50.0, "max_n1k_deploy_limit": 85.0,
            "feedback_mode": "manual_feedback_override",
            # E11-14 sign-off triplet
            "actor": "FantuiTest",
            "ticket_id": "WB-FANTUI",
            "manual_override_signoff": {
                "signed_by": "FantuiTest",
                "signed_at": "2026-04-25T00:00:00Z",
                "ticket_id": "WB-FANTUI",
            },
        })
        self.assertEqual(s, 200)
        # Whatever the exact response shape, it must not claim L1-L4 are active
        # (we gave it air + forward throttle).
        txt = json.dumps(snap)
        self.assertNotIn('"logic1_active": true', txt.lower())


class StaticAssetRoutingTests(unittest.TestCase):

    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _get(self, path):
        conn = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()
        return resp.status, body

    def test_fan_console_html_is_served(self):
        status, body = self._get("/fan_console.html")
        self.assertEqual(status, 200)
        self.assertIn("反推实时操作台", body)
        self.assertIn("/api/fantui/tick", body)
        self.assertIn('src="/timeseries_chart.js"', body)

    def test_timeseries_chart_js_is_served(self):
        status, body = self._get("/timeseries_chart.js")
        self.assertEqual(status, 200)
        self.assertIn("TimeseriesChart", body)
        self.assertIn("buildPayload", body)

    def test_demo_html_nav_links_to_fan_console(self):
        status, body = self._get("/demo.html")
        self.assertEqual(status, 200)
        self.assertIn('data-nav-key="fan-console"', body)
        self.assertIn('href="/fan_console.html"', body)


class TimeseriesChartFileStructureTests(unittest.TestCase):
    """Static assertions about the shared chart module so that a renaming
    refactor tripping the contract trips CI."""

    JS_PATH = STATIC_ROOT / "timeseries_chart.js"

    def test_exports_create_and_buildPayload(self):
        src = self.JS_PATH.read_text(encoding="utf-8")
        self.assertIn("global.TimeseriesChart = { create, buildPayload }", src)

    def test_supports_payload_shape_fields(self):
        src = self.JS_PATH.read_text(encoding="utf-8")
        for marker in ("time_start_s", "time_end_s", "series",
                       "display_min", "display_max", "samples"):
            self.assertIn(marker, src, msg=f"chart module missing {marker!r}")

    def test_buildPayload_filters_non_finite_samples(self):
        """Codex 2026-04-24 MINOR finding: ``buildPayload`` must skip
        NaN/Infinity ``t_s`` and ``v`` so a single bad sample does not
        blank the entire polyline."""
        src = self.JS_PATH.read_text(encoding="utf-8")
        self.assertIn("Number.isFinite(rec.t_s)", src,
                      msg="buildPayload must guard rec.t_s against NaN/Infinity")
        self.assertIn("Number.isFinite(v)", src,
                      msg="buildPayload must guard sample value against NaN/Infinity")


if __name__ == "__main__":
    unittest.main()
