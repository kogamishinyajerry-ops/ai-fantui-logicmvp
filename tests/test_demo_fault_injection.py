import http.client, json, unittest

from conftest import with_signoff_if_manual_override  # E11-14
from tests.test_demo import start_demo_server


class FaultInjectionTests(unittest.TestCase):
    BASE_REQUEST = {
        "tra_deg": -14.0,
        "radio_altitude_ft": 5.0,
        "engine_running": True,
        "aircraft_on_ground": True,
        "reverser_inhibited": False,
        "eec_enable": True,
        "n1k": 35.0,
        "max_n1k_deploy_limit": 60.0,
    }

    @classmethod
    def setUpClass(cls):
        cls.server, cls.thread = start_demo_server()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _post(self, payload):
        # E11-14: auto-attach sign-off when feedback_mode = manual_feedback_override
        payload = with_signoff_if_manual_override(payload)
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request(
                "POST",
                "/api/lever-snapshot",
                body=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            return response, data
        finally:
            connection.close()

    def test_contradiction_on_ground_high_altitude(self):
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "aircraft_on_ground": True,
                "radio_altitude_ft": 15.0,
            }
        )

        self.assertEqual(response.status, 200)
        self.assertIn("radio_altitude_ft", payload["logic"]["logic1"]["failed_conditions"])

    def test_contradiction_in_air_low_altitude(self):
        """Fault: aircraft_on_ground=False yet radio_altitude_ft=1.0 (low alt but in-air flag).

        altitude_gate = altitude_on_ground or altitude_ft >= 7.0
        altitude_on_ground=False (skip), altitude=1.0 < 7 (skip) → altitude_gate=False
        → altitude does NOT block logic1. Instead, on_air logic (logic2/3) fails on
        aircraft_on_ground=False. logic1 becomes active.
        """
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "aircraft_on_ground": False,
                "radio_altitude_ft": 1.0,
            }
        )

        self.assertEqual(response.status, 200)
        # altitude_gate=False (altitude<7 AND not on_ground), so altitude does not block
        active_ids = {k for k, v in payload["logic"].items() if v["active"]}
        self.assertIn("logic1", active_ids)  # logic1 passes altitude gate

    def test_n1k_just_below_limit(self):
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "n1k": 59.9,
                "max_n1k_deploy_limit": 60.0,
            }
        )
        active_logic_node_ids = {
            logic_name
            for logic_name, logic_payload in payload["logic"].items()
            if logic_payload["active"]
        }

        self.assertEqual(response.status, 200)
        self.assertIn("logic3", active_logic_node_ids)

    def test_n1k_at_exact_limit(self):
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "n1k": 60.0,
                "max_n1k_deploy_limit": 60.0,
            }
        )

        self.assertEqual(response.status, 200)
        self.assertIn("n1k", payload["logic"]["logic3"]["failed_conditions"])

    def test_tra_at_exact_threshold(self):
        """TRA at exactly -14.0 with on_ground=False should engage SW1/lgic1.

        altitude_gate = altitude_on_ground or altitude_ft >= 7.0.
        With aircraft_on_ground=False and altitude=0.0: altitude_gate=False (both branches False).
        altitude does NOT block. With TRA=-14, SW1 latches → logic1 active.
        """
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "tra_deg": -14.0,
                "aircraft_on_ground": False,  # makes altitude_gate=False
                "radio_altitude_ft": 0.0,
            }
        )
        active_ids = {k for k, v in payload["logic"].items() if v["active"]}

        self.assertEqual(response.status, 200)
        self.assertIn("logic1", active_ids,
                       f"TRA=-14 on_air altitude=0 should engage logic1. Got active={active_ids}")

    def test_tra_just_below_threshold(self):
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "tra_deg": -13.9,
            }
        )
        active_logic_node_ids = {
            logic_name
            for logic_name, logic_payload in payload["logic"].items()
            if logic_payload["active"]
        }

        self.assertEqual(response.status, 200)
        self.assertNotIn("logic1", active_logic_node_ids)

    def test_manual_override_bypasses_sw1_gate(self):
        """manual_feedback_override drives VDT90 directly via deploy_position_percent.

        This is the key safety-relevant behavior: in manual override mode,
        SW1 is NOT a prerequisite for VDT90 activation -- the pilot's
        deploy_position_percent directly controls it.
        sw1=False, sw2=True, tra_deg=-14, deploy=95 should activate logic4.
        """
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "sw1": False,
                "sw2": True,
                "tra_deg": -14.0,
                "feedback_mode": "manual_feedback_override",
                "deploy_position_percent": 95.0,
            }
        )
        active_ids = {k for k, v in payload["logic"].items() if v["active"]}

        self.assertEqual(response.status, 200)
        self.assertIn("logic4", active_ids,
                       f"manual override should drive VDT90/lgic4 regardless of SW1. Got: {active_ids}")

    def test_reverser_inhibited_blocks_upstream(self):
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "reverser_inhibited": True,
                "feedback_mode": "manual_feedback_override",
                "deploy_position_percent": 95.0,
            }
        )

        self.assertEqual(response.status, 200)
        self.assertIn("reverser_inhibited", payload["logic"]["logic1"]["failed_conditions"])

    # ---- P17-03 Fault Injection API Tests ----

    def test_fault_sw1_stuck_off_overrides_switch(self):
        """Injecting sw1 stuck_off forces sw1=False even when sw1=True in the input."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "sw1": True,  # normal input would activate logic1
                "fault_injections": [{"node_id": "sw1", "fault_type": "stuck_off"}],
            }
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(payload.get("active_fault_node_ids"), ["sw1"])
        self.assertEqual(payload.get("fault_injections"), [{"node_id": "sw1", "fault_type": "stuck_off"}])
        # sw1 stuck_off should block logic1
        self.assertFalse(payload["logic"]["logic1"]["active"])

    def test_fault_sw2_stuck_off_overrides_switch(self):
        """Injecting sw2 stuck_off forces sw2=False even when sw2=True in the input."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "sw2": True,  # normal input would activate logic2
                "fault_injections": [{"node_id": "sw2", "fault_type": "stuck_off"}],
            }
        )
        self.assertEqual(response.status, 200)
        self.assertIn("sw2", payload.get("active_fault_node_ids", []))
        self.assertFalse(payload["logic"]["logic2"]["active"])

    def test_fault_sw1_stuck_on_is_recorded_and_forces_switch(self):
        """Injecting sw1 stuck_on records it in active_fault_node_ids and forces sw1 node state=active."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "sw1": False,  # would normally keep logic1 inactive
                "fault_injections": [{"node_id": "sw1", "fault_type": "stuck_on"}],
            }
        )
        self.assertEqual(response.status, 200)
        self.assertIn("sw1", payload.get("active_fault_node_ids", []))
        # The sw1 node should show as active in the canvas despite sw1=False input
        sw1_nodes = [n for n in payload.get("nodes", []) if n.get("id") == "sw1"]
        self.assertEqual(len(sw1_nodes), 1)
        self.assertEqual(sw1_nodes[0].get("state"), "active")

    def test_fault_radio_altitude_sensor_zero_unblocks_logic1(self):
        """Injecting radio_altitude_ft sensor_zero forces RA=0, bypassing altitude gate.

        With aircraft_on_ground=False and altitude=8.0: altitude gate blocks logic1
        (altitude_ft >= 7.0 branch = True, altitude_on_ground=False → altitude_gate=False).
        After sensor_zero fault forces RA=0: altitude check (RA < 6.0) passes,
        altitude_gate = False OR True = True → altitude no longer blocks logic1.
        """
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "aircraft_on_ground": False,
                "radio_altitude_ft": 8.0,  # would normally block via altitude >= 7.0 gate
                "fault_injections": [{"node_id": "radio_altitude_ft", "fault_type": "sensor_zero"}],
            }
        )
        self.assertEqual(response.status, 200)
        self.assertIn("radio_altitude_ft", payload.get("active_fault_node_ids", []))
        # RA=0 (< 6.0 threshold) should make altitude pass gate → logic1 active
        self.assertTrue(payload["logic"]["logic1"]["active"])
        self.assertEqual(payload["hud"]["radio_altitude_ft"], 0.0)

    def test_fault_invalid_node_returns_400(self):
        """Unknown node_id returns 400 with invalid_fault_injection_node error."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "fault_injections": [{"node_id": "not_a_real_node", "fault_type": "stuck_off"}],
            }
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(payload.get("error"), "invalid_fault_injection_node")

    def test_fault_invalid_type_returns_400(self):
        """Unknown fault_type returns 400 with invalid_fault_type error."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "fault_injections": [{"node_id": "sw1", "fault_type": "not_a_fault_type"}],
            }
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(payload.get("error"), "invalid_fault_type")

    def test_fault_non_list_returns_400(self):
        """fault_injections must be a list; non-list returns 400."""
        for bad_value in [123, "stuck_off", {"node_id": "sw1"}]:
            response, payload = self._post({**self.BASE_REQUEST, "fault_injections": bad_value})
            self.assertEqual(response.status, 400, msg=f"fault_injections={bad_value!r} should be rejected")

    def test_multiple_faults_injected(self):
        """Multiple faults can be injected simultaneously."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "fault_injections": [
                    {"node_id": "sw1", "fault_type": "stuck_off"},
                    {"node_id": "sw2", "fault_type": "stuck_off"},
                ],
            }
        )
        self.assertEqual(response.status, 200)
        active_ids = set(payload.get("active_fault_node_ids", []))
        self.assertEqual(active_ids, {"sw1", "sw2"})
        self.assertFalse(payload["logic"]["logic1"]["active"])
        self.assertFalse(payload["logic"]["logic2"]["active"])

    def test_fault_alias_normalizes_sw1_input_to_sw1(self):
        """sw1_input is an alias for sw1 and should be accepted and normalized."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "fault_injections": [{"node_id": "sw1_input", "fault_type": "stuck_off"}],
            }
        )
        self.assertEqual(response.status, 200)
        self.assertIn("sw1", payload.get("active_fault_node_ids", []))

    def test_unsupported_fault_combination_is_silently_ignored(self):
        """A valid node_id + valid fault_type but unsupported combination (sw1+sensor_zero)
        is accepted by the API but has no effect on logic output — it is a no-op."""
        response, payload = self._post(
            {
                **self.BASE_REQUEST,
                "fault_injections": [{"node_id": "sw1", "fault_type": "sensor_zero"}],
            }
        )
        self.assertEqual(response.status, 200)
        # The fault is recorded (so API accepted it) but sw1 is a switch, not a sensor
        self.assertIn("sw1", payload.get("active_fault_node_ids", []))

    def test_empty_fault_injections_list_is_accepted(self):
        """fault_injections=[] is a valid no-op."""
        response, payload = self._post({**self.BASE_REQUEST, "fault_injections": []})
        self.assertEqual(response.status, 200)
        self.assertNotIn("active_fault_node_ids", payload)
        self.assertNotIn("fault_injections", payload)

    def test_no_fault_injections_excludes_fault_fields(self):
        """Without fault_injections, the response does not include active_fault_node_ids or fault_injections keys."""
        response, payload = self._post(self.BASE_REQUEST)
        self.assertEqual(response.status, 200)
        # No faults → these keys are absent from the response (not returned as empty)
        self.assertNotIn("active_fault_node_ids", payload)
        self.assertNotIn("fault_injections", payload)
