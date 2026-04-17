"""Tests for Content-Type whitelist enforcement in demo_server.

Verifies that only application/json Content-Type is accepted; text/plain and
application/x-www-form-urlencoded are rejected with 415, while missing
Content-Type is allowed for backward compatibility.
"""

import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from well_harness.demo_server import DemoRequestHandler


def start_demo_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class TestContentTypeWhitelist(unittest.TestCase):
    def test_application_json_accepted(self):
        """POST with Content-Type: application/json should succeed."""
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "logic4 和 throttle lock 有什么关系"}).encode("utf-8")
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)

    def test_text_plain_rejected(self):
        """POST with Content-Type: text/plain should return 415."""
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "logic4 和 throttle lock 有什么关系"}).encode("utf-8")
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
                headers={"Content-Type": "text/plain"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 415)
        self.assertEqual(payload["error"], "unsupported_media_type")

    def test_form_urlencoded_rejected(self):
        """POST with Content-Type: application/x-www-form-urlencoded should return 415."""
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "logic4 和 throttle lock 有什么关系"}).encode("utf-8")
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 415)
        self.assertEqual(payload["error"], "unsupported_media_type")

    def test_missing_content_type_accepted(self):
        """POST without Content-Type header should still work (backward compat)."""
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "logic4 和 throttle lock 有什么关系"}).encode("utf-8")
            # No Content-Type header at all
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
            )
            response = connection.getresponse()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)


if __name__ == "__main__":
    unittest.main()
