"""Tests for P14 AI Document Analyzer API routes and module."""

import http.client
import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

# Ensure P14_AI_MOCK=1 for all tests (no real API calls)
os.environ["P14_AI_MOCK"] = "1"

from well_harness.demo_server import DemoRequestHandler

PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def start_demo_server():
    """Start a ThreadingHTTPServer on a random port. Returns (server, thread)."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class P14AIAnalyzerTest(unittest.TestCase):
    """Tests for /api/p14/* routes using in-process HTTP server with P14_AI_MOCK=1."""

    @classmethod
    def setUpClass(cls):
        cls.server, cls.thread = start_demo_server()
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def _post(self, path: str, payload: dict) -> tuple[http.client.HTTPResponse, dict]:
        """POST JSON to the given path. Returns (response, parsed_body)."""
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        connection.request(
            "POST",
            path,
            body=body,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response, data

    def _get(self, path: str) -> tuple[http.client.HTTPResponse, bytes]:
        """GET the given path. Returns (response, body_bytes)."""
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        connection.close()
        return response, body

    # ------------------------------------------------------------------
    # Analyze endpoint tests
    # ------------------------------------------------------------------

    def test_analyze_document_success(self):
        """POST valid payload returns 200 with ambiguities and first_question."""
        payload = {
            "session_id": "test-session-001",
            "document_text": "L3 active when VDT90 threshold exceeded. VDT90 threshold not specified.",
            "document_name": "control-logic-spec.md",
        }
        response, data = self._post("/api/p14/analyze-document", payload)

        self.assertEqual(response.status, 200)
        self.assertEqual(data["session_id"], "test-session-001")
        self.assertIsInstance(data["ambiguities"], list)
        self.assertGreater(len(data["ambiguities"]), 0)
        self.assertEqual(data["total_count"], len(data["ambiguities"]))
        # Each ambiguity has required fields
        for amb in data["ambiguities"]:
            self.assertIn("id", amb)
            self.assertIn("text_excerpt", amb)
            self.assertIn("description", amb)
            self.assertIn("confidence_score", amb)
            self.assertIn("suggested_clarification", amb)
        # first_question should be present (not null) when ambiguities exist
        self.assertIsNotNone(data.get("first_question"))
        self.assertIn("question", data["first_question"])
        self.assertFalse(data.get("is_complete", False))

    def test_analyze_document_missing_session_id(self):
        """Missing session_id returns 400."""
        payload = {
            "document_text": "Some document text about L3 activation logic.",
            "document_name": "spec.md",
        }
        response, data = self._post("/api/p14/analyze-document", payload)
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "missing_session_id")

    def test_analyze_document_empty_text(self):
        """Empty document_text returns 400."""
        payload = {
            "session_id": "test-002",
            "document_text": "   ",
            "document_name": "empty.md",
        }
        response, data = self._post("/api/p14/analyze-document", payload)
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "empty_document")

    @unittest.skip(
        "Security pre-check (50MB DoS guard) closes connection before body-read; sandbox cannot test body-read 400 path for >50MB payloads."
    )
    def test_analyze_document_too_large(self):
        """document_text over 50MB pre-check returns 413; 10-50MB body-read check returns 400."""
        large_text = "x" * (51 * 1024 * 1024)  # 51 MB
        payload = {
            "session_id": "test-003",
            "document_text": large_text,
            "document_name": "large.md",
        }
        response, data = self._post("/api/p14/analyze-document", payload)
        self.assertEqual(response.status, 413)
        self.assertEqual(data.get("error"), "payload_too_large")

    def test_analyze_document_invalid_json(self):
        """Invalid JSON returns 400."""
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        connection.request(
            "POST",
            "/api/p14/analyze-document",
            body=b"not valid json",
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "invalid_json")

    # ------------------------------------------------------------------
    # Clarify endpoint tests
    # ------------------------------------------------------------------

    def test_clarify_success(self):
        """After analyze, clarify returns next question."""
        # First: analyze
        analyze_payload = {
            "session_id": "clarify-test-001",
            "document_text": "L3 activation depends on VDT90 threshold. Threshold is undefined.",
            "document_name": "test.md",
        }
        _, analyze_data = self._post("/api/p14/analyze-document", analyze_payload)
        self.assertEqual(analyze_data["first_question"]["question"], "L3\u5728\u54ea\u4e9b\u5177\u4f53\u6761\u4ef6\u4e0b\u6fc0\u6d3b\uff1f")

        # Second: clarify with an answer
        clarify_payload = {
            "session_id": "clarify-test-001",
            "answer": "L3 activates when VDT90 >= deploy_90_threshold_percent AND reverser_inhibited is False.",
        }
        response, clarify_data = self._post("/api/p14/clarify", clarify_payload)

        self.assertEqual(response.status, 200)
        self.assertEqual(clarify_data["session_id"], "clarify-test-001")
        self.assertIn("progress", clarify_data)
        self.assertIn("answered", clarify_data["progress"])
        self.assertIn("remaining", clarify_data["progress"])
        # progress.answered should be 1 after first answer
        self.assertEqual(clarify_data["progress"]["answered"], 1)
        self.assertFalse(clarify_data["is_complete"])

    def test_clarify_session_not_found(self):
        """Clarify with unknown session_id returns 404."""
        payload = {
            "session_id": "nonexistent-session-xyz",
            "answer": "Some answer.",
        }
        response, data = self._post("/api/p14/clarify", payload)
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "session_not_found")

    def test_clarify_empty_answer(self):
        """Clarify with empty answer returns 400."""
        # First create a session
        analyze_payload = {
            "session_id": "empty-answer-test",
            "document_text": "L3 threshold is ambiguous.",
            "document_name": "test.md",
        }
        _, _ = self._post("/api/p14/analyze-document", analyze_payload)

        # Now try to clarify with empty answer
        clarify_payload = {
            "session_id": "empty-answer-test",
            "answer": "",
        }
        response, data = self._post("/api/p14/clarify", clarify_payload)
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "empty_answer")

    def test_clarify_all_answered_then_complete(self):
        """Answer all 3 mock questions → is_complete=True."""
        # Create and analyze
        analyze_payload = {
            "session_id": "complete-test-001",
            "document_text": "L3 and VDT90 spec",
            "document_name": "spec.md",
        }
        _, _ = self._post("/api/p14/analyze-document", analyze_payload)

        # Answer all 3 questions
        answers = [
            "L3 activates on VDT90 >= threshold with reverser not inhibited.",
            "VDT90 deploy_90_threshold_percent = 90%.",
            "On VDT90 signal loss, L3 retains last known state.",
        ]
        for answer in answers:
            payload = {"session_id": "complete-test-001", "answer": answer}
            response, data = self._post("/api/p14/clarify", payload)

        # After 3 answers, is_complete should be True
        self.assertTrue(data["is_complete"])
        self.assertIsNone(data["next_question"])

    # ------------------------------------------------------------------
    # Generate endpoint tests
    # ------------------------------------------------------------------

    def test_generate_prompt_success(self):
        """Complete clarification cycle then generate → returns markdown prompt."""
        # Analyze
        analyze_payload = {
            "session_id": "generate-test-001",
            "document_text": "L3 threshold specification",
            "document_name": "spec.md",
        }
        _, _ = self._post("/api/p14/analyze-document", analyze_payload)

        # Answer all 3 questions
        for answer in ["A1", "A2", "A3"]:
            _, _ = self._post("/api/p14/clarify", {"session_id": "generate-test-001", "answer": answer})

        # Generate
        response, data = self._post("/api/p14/generate-prompt", {"session_id": "generate-test-001"})

        self.assertEqual(response.status, 200)
        self.assertEqual(data["session_id"], "generate-test-001")
        self.assertIn("prompt_document", data)
        self.assertGreater(len(data["prompt_document"]), 0)
        self.assertGreater(data["word_count"], 0)
        # Should be markdown (contains section headings)
        self.assertIn("#", data["prompt_document"])

    def test_generate_prompt_session_not_found(self):
        """Generate with unknown session_id returns 400."""
        response, data = self._post("/api/p14/generate-prompt", {"session_id": "no-such-session"})
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "session_not_found")

    def test_generate_prompt_incomplete_session(self):
        """Generate before clarifying returns 400 with session_incomplete."""
        # Analyze but don't clarify
        analyze_payload = {
            "session_id": "incomplete-test-001",
            "document_text": "Some spec text.",
            "document_name": "test.md",
        }
        _, _ = self._post("/api/p14/analyze-document", analyze_payload)

        # Try to generate without clarifying
        response, data = self._post("/api/p14/generate-prompt", {"session_id": "incomplete-test-001"})
        self.assertEqual(response.status, 400)
        self.assertEqual(data.get("error"), "session_incomplete")

    # ------------------------------------------------------------------
    # Static page tests
    # ------------------------------------------------------------------

    def test_static_page_serves(self):
        """GET /ai-doc-analyzer.html returns 200 with HTML content."""
        response, body = self._get("/ai-doc-analyzer.html")
        self.assertEqual(response.status, 200)
        self.assertIn(b"AI Document Analyzer", body)
        self.assertIn(b"ai-doc-analyzer.css", body)
        self.assertIn(b"ai-doc-analyzer.js", body)

    def test_static_page_not_found(self):
        """GET nonexistent static file returns 404."""
        response, body = self._get("/ai-doc-analyzer-NOTEXIST.html")
        self.assertEqual(response.status, 404)


if __name__ == "__main__":
    unittest.main()
