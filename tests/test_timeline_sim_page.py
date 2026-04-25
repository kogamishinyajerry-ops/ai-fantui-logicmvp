"""PR-4: /timeline-sim.html smoke tests (page served + preset markers present)."""

from __future__ import annotations

import http.client
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"


class TimelineSimPageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _get(self, path: str) -> tuple[int, str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body

    def test_page_served(self):
        status, body = self._get("/timeline-sim.html")
        self.assertEqual(status, 200)
        # Core UI markers must exist.
        self.assertIn("Timeline Simulator", body)
        self.assertIn('id="presetSelect"', body)
        self.assertIn('id="runBtn"', body)
        self.assertIn('id="timelineJson"', body)

    def test_all_four_demo_presets_present(self):
        _, body = self._get("/timeline-sim.html")
        # Each preset key should appear as an <option value=...> AND inside
        # the PRESETS object literal.
        for key in ("fantui_nominal", "fantui_sw1_stuck", "c919_nominal", "c919_tr_inhibited"):
            self.assertIn(f'value="{key}"', body, msg=f"missing option for {key}")
            self.assertIn(f"{key}:", body, msg=f"missing PRESETS entry for {key}")

    def test_page_routes_c919_to_9191(self):
        """The client-side router must POST c919-etras timelines to port 9191."""
        _, body = self._get("/timeline-sim.html")
        self.assertIn("C919_PORT = 9191", body)
        # Both endpoints referenced.
        self.assertIn("/api/timeline-simulate", body)

    def test_static_file_exists_on_disk(self):
        self.assertTrue(STATIC_HTML.is_file(),
                        msg=f"timeline-sim.html not present at {STATIC_HTML}")


if __name__ == "__main__":
    unittest.main()
