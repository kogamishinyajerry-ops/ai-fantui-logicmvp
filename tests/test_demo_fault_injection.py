import http.client, json, unittest

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
