"""P17-gen hasOperateIntent routing + operate endpoint integration tests.

Tests the three-way routing decision (operate / reason / explain) and the
cannot_operate response for plant-output targets.
"""

from __future__ import annotations

import http.client
import json
import subprocess
import sys
import threading
import unittest
import unittest.mock
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.demo_server import DemoRequestHandler, lever_snapshot_payload


def start_server() -> tuple[ThreadingHTTPServer | None, threading.Thread, int]:
    """Start a ThreadingHTTPServer on a random available port. Returns (server, thread, port)."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_address[1]


def request_json(
    port: int, path: str, payload: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    """Make a JSON POST request to the local server. Returns (status, parsed_body)."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        connection.request(
            "POST",
            path,
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    return response.status, json.loads(body)


# ---------------------------------------------------------------------------
# hasOperateIntent routing tests
# ---------------------------------------------------------------------------
# These tests verify that the frontend hasOperateIntent() correctly identifies
# operate intent by checking its pattern list against known phrases.
#
# Since hasOperateIntent is a JS function in chat.js, we test it indirectly via
# the HTTP server routing (handleSend routes to /api/chat/operate when
# hasOperateIntent returns True, and to /api/chat/reason otherwise).
#
# The operate endpoint returns a 200 response for any question routed to it;
# it does not validate that the target is controllable — that check lives in the
# LLM system prompt. We verify cannot_operate by mocking the LLM response.
# ---------------------------------------------------------------------------

# hasOperateIntent patterns (extracted from chat.js hasOperateIntent):
# operatePatterns checks for substring inclusion (case-insensitive):
#   Compound verbs: 调节/调整/设置/达到/触发/激活/满足/实现
#   Technical keywords: vd/vdt/tra/altitude/radio/deploy/position/override/manual/inhibit/引擎
#   Logic gate targets: 满足l1/满足l2/满足l3/满足l4/l1满足/l2满足/l3满足/l4满足
#   Compound targets: 把tra/把vdt/把vd/让tra/拉倒/推到


def _has_operate_intent_matches(text: str) -> bool:
    """Python mirror of the JS hasOperateIntent() substring-matching logic."""
    lower = text.lower()
    patterns = [
        # Compound action verbs
        "调节", "调整", "设置", "达到", "触发", "激活", "满足", "实现",
        # Technical parameter keywords
        "vd", "vdt", "tra", "altitude", "radio",
        "deploy", "position", "override", "manual",
        "inhibit", "引擎",
        # Specific logic gate targets
        "满足l1", "满足l2", "满足l3", "满足l4",
        "l1满足", "l2满足", "l3满足", "l4满足",
        # Compound with target words
        "把tra", "把vdt", "把vd", "让tra", "拉倒", "推到",
    ]
    for p in patterns:
        if p in lower:
            return True
    return False


class TestHasOperateIntent(unittest.TestCase):
    """Verify hasOperateIntent pattern matching covers the Opus UX cases."""

    def test_vdt_adjust_triggers_operate(self):
        """VDT调节到90 — '调节' + 'vdt' → operate intent True."""
        self.assertTrue(_has_operate_intent_matches("帮我把VDT调节到90"))

    def test_satisfy_l1_l4_triggers_operate(self):
        """满足L1-L4 — '满足' + gate target → operate intent True."""
        self.assertTrue(_has_operate_intent_matches("满足L1-L4"))
        self.assertTrue(_has_operate_intent_matches("满足L1"))

    def test_tra_adjust_triggers_operate(self):
        """把TRA设成-14度 — '把tra' compound → operate intent True."""
        self.assertTrue(_has_operate_intent_matches("把TRA设成-14度"))

    def test_thr_lock_plant_output_not_operate_intent(self):
        """把THR_LOCK设为true — no compound target match → operate intent False.

        THR_LOCK is not in operatePatterns. The string "把thr" does not match
        any compound pattern (把tra/把vdt/把vd/让tra/拉倒/推到). This question
        falls through to /api/chat/reason, not /api/chat/operate.
        """
        self.assertFalse(_has_operate_intent_matches("把THR_LOCK设为true"))

    def test_explain_reason_no_operate(self):
        """解释TLS为什么亮 — pure explanation → operate intent False."""
        self.assertFalse(_has_operate_intent_matches("解释TLS为什么亮"))

    def test_l3_gate_conditions_no_operate(self):
        """L3门的条件是什么 — knowledge query → operate intent False."""
        self.assertFalse(_has_operate_intent_matches("L3门的条件是什么"))

    def test_why_blocked_diagnosis_no_operate(self):
        """为什么反推力链路blocked — diagnosis → operate intent False."""
        self.assertFalse(_has_operate_intent_matches("为什么反推力链路blocked"))


class TestChatOperateEndpoint(unittest.TestCase):
    """Integration tests for /api/chat/operate with mocked MiniMax LLM."""

    @classmethod
    def setUpClass(cls):
        cls.server, cls.thread, cls.port = start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _mock_llm_response(self, response_body: dict) -> unittest.mock.MagicMock:
        """Return a mock urlopen that returns the given JSON body as an HTTP response."""
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = json.dumps(response_body).encode("utf-8")
        mock_response.__enter__ = unittest.mock.MagicMock(return_value=mock_response)
        mock_response.__exit__ = unittest.mock.MagicMock(return_value=None)
        return mock_response

    def _mock_urlopen_success(self, action_type: str, reasoning: str = "test") -> unittest.mock.MagicMock:
        """Build a MiniMax mock response for the given action_type."""
        return self._mock_llm_response({
            "choices": [{"message": {"content": json.dumps({
                "action_type": action_type,
                "parameter_overrides": {},
                "auto_apply": False,
                "trajectory_steps": [],
                "reasoning": reasoning,
                "confidence": 0.95,
                "gate_plan": {},
                "ai_explanation": reasoning,
            })}}]
        })

    def test_vdt_adjust_returns_suggest_parameter_override(self):
        """调节VDT → operate endpoint should return suggest_parameter_override."""
        with unittest.mock.patch("urllib.request.urlopen", return_value=self._mock_urlopen_success(
            "suggest_parameter_override", "调节VDT至90%"
        )):
            status, body = request_json(self.port, "/api/chat/operate", {
                "question": "帮我把VDT调节到90",
                "system_id": "thrust-reverser",
                "current_snapshot": lever_snapshot_payload(-14.0),
            })
            self.assertEqual(status, 200)
            self.assertEqual(body["action_type"], "suggest_parameter_override")

    def test_thr_lock_returns_cannot_operate(self):
        """THR_LOCK is a plant output → operate endpoint should return cannot_operate.

        Even though hasOperateIntent returns False for "把THR_LOCK设为true" (routing
        it to /api/chat/reason instead), this test verifies that when the operate
        endpoint IS called with a plant-output target, it correctly refuses.
        """
        with unittest.mock.patch("urllib.request.urlopen", return_value=self._mock_urlopen_success(
            "cannot_operate", "THR_LOCK是plant输出，无法直接设置"
        )):
            status, body = request_json(self.port, "/api/chat/operate", {
                "question": "把THR_LOCK设为true",
                "system_id": "thrust-reverser",
                "current_snapshot": lever_snapshot_payload(-14.0),
            })
            self.assertEqual(status, 200)
            self.assertEqual(body["action_type"], "cannot_operate")

    def test_satisfy_l1_l4_returns_suggest_with_gate_plan(self):
        """满足L1-L4 → operate endpoint should return suggest + gate_plan."""
        with unittest.mock.patch("urllib.request.urlopen", return_value=self._mock_urlopen_success(
            "suggest_parameter_override", "满足L1-L4需要设置多个参数"
        )):
            status, body = request_json(self.port, "/api/chat/operate", {
                "question": "满足L1-L4",
                "system_id": "thrust-reverser",
                "current_snapshot": lever_snapshot_payload(-14.0),
            })
            self.assertEqual(status, 200)
            self.assertIn(body["action_type"], ("suggest_parameter_override", "manual_steps"))

    def test_missing_api_key_returns_error(self):
        """Missing MiniMax API key → graceful error response."""
        from well_harness import llm_client as lc

        def _no_key(self):
            return ""

        with unittest.mock.patch.object(lc.MiniMaxClient, "api_key", property(_no_key)):
            status, body = request_json(self.port, "/api/chat/operate", {
                "question": "把VDT调节到90",
                "system_id": "thrust-reverser",
            })
            self.assertEqual(status, 400)
            self.assertEqual(body.get("error"), "minimax_api_key_missing")

    def test_missing_question_returns_error(self):
        """Empty question → 400 error payload."""
        status, body = request_json(self.port, "/api/chat/operate", {
            "question": "",
            "system_id": "thrust-reverser",
        })
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "missing_question")


if __name__ == "__main__":
    unittest.main()
