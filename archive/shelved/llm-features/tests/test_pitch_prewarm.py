"""Pitch prewarm workflow regression tests."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from well_harness import demo_server
from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
PITCH_PREWARM_SCRIPT_PATH = REPO_ROOT / "scripts" / "pitch_prewarm.py"
PITCH_READINESS_SCRIPT_PATH = REPO_ROOT / "scripts" / "pitch_readiness.py"


def _load_script_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pitch_prewarm = _load_script_module("pitch_prewarm_test_module", PITCH_PREWARM_SCRIPT_PATH)
pitch_readiness = _load_script_module("pitch_readiness_test_module", PITCH_READINESS_SCRIPT_PATH)


def start_demo_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class PitchPrewarmWorkflowTests(unittest.TestCase):
    def setUp(self):
        demo_server._clear_chat_explain_cache()

    def test_run_prewarm_creates_verified_cache_artifact(self):
        class FakeClient:
            def __init__(self):
                self.calls = 0

            def chat(self, messages, **kwargs):
                del messages, kwargs
                self.calls += 1
                return json.dumps(
                    {
                        "explanation": f"cached-response-{self.calls}",
                        "highlighted_nodes": ["L1"],
                        "suggestion_nodes": ["logic1"],
                        "confidence": 0.9,
                    },
                    ensure_ascii=False,
                )

        fake_client = FakeClient()
        server, thread = start_demo_server()
        original_runs_dir = pitch_prewarm.RUNS_DIR
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                pitch_prewarm.RUNS_DIR = Path(tmpdir)
                with mock.patch.object(demo_server, "get_llm_client", return_value=fake_client):
                    with mock.patch.dict(
                        os.environ,
                        {"LLM_BACKEND": "ollama", "OLLAMA_MODEL": "qwen2.5:7b-instruct"},
                        clear=False,
                    ):
                        report, out_dir = pitch_prewarm.run_prewarm(
                            backend="ollama",
                            model="qwen2.5:7b-instruct",
                            port=server.server_port,
                        )

                self.assertEqual("GREEN", report["verdict"])
                self.assertTrue(report["reused_running_server"])
                self.assertEqual(2, report["summary"]["verified_cache_hits"])
                self.assertEqual(2, report["summary"]["expected_count"])
                self.assertEqual(2, report["rounds"][0]["cache_misses"])
                self.assertEqual(2, report["rounds"][1]["cache_hits"])
                self.assertEqual(2, fake_client.calls)
                self.assertTrue((out_dir / "report.json").exists())
                self.assertTrue((out_dir / "summary.md").exists())
        finally:
            pitch_prewarm.RUNS_DIR = original_runs_dir
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_run_prewarm_marks_reused_server_backend_mismatch_yellow(self):
        class FakeClient:
            def __init__(self):
                self.calls = 0

            def chat(self, messages, **kwargs):
                del messages, kwargs
                self.calls += 1
                return json.dumps(
                    {
                        "explanation": f"backend-mismatch-{self.calls}",
                        "highlighted_nodes": ["L1"],
                        "suggestion_nodes": ["logic1"],
                        "confidence": 0.9,
                    },
                    ensure_ascii=False,
                )

        fake_client = FakeClient()
        server, thread = start_demo_server()
        original_runs_dir = pitch_prewarm.RUNS_DIR
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                pitch_prewarm.RUNS_DIR = Path(tmpdir)
                with mock.patch.object(demo_server, "get_llm_client", return_value=fake_client):
                    with mock.patch.dict(
                        os.environ,
                        {
                            "LLM_BACKEND": "minimax",
                            "MINIMAX_MODEL": "minimax-m2.7-highspeed",
                        },
                        clear=False,
                    ):
                        report, _out_dir = pitch_prewarm.run_prewarm(
                            backend="ollama",
                            model="qwen2.5:7b-instruct",
                            port=server.server_port,
                        )

                self.assertEqual("YELLOW", report["verdict"])
                self.assertEqual("backend_mismatch", report["error"])
                self.assertFalse(report["summary"]["backend_match"])
                self.assertEqual("ollama", report["summary"]["requested_backend"])
                self.assertEqual("qwen2.5:7b-instruct", report["summary"]["requested_model"])
                self.assertEqual("minimax", report["summary"]["llm_backend"])
                self.assertEqual("minimax-m2.7-highspeed", report["summary"]["llm_model"])
        finally:
            pitch_prewarm.RUNS_DIR = original_runs_dir
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_run_prewarm_unreachable_does_not_claim_backend_mismatch(self):
        original_runs_dir = pitch_prewarm.RUNS_DIR
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                pitch_prewarm.RUNS_DIR = Path(tmpdir)
                with mock.patch.object(pitch_prewarm, "_port_free", return_value=False):
                    with mock.patch.object(pitch_prewarm, "_wait_ready", return_value=(False, 123.4)):
                        report, _out_dir = pitch_prewarm.run_prewarm(
                            backend="ollama",
                            model="qwen2.5:7b-instruct",
                            port=8799,
                        )

                self.assertEqual("YELLOW", report["verdict"])
                self.assertEqual("demo_server_unreachable", report["error"])
                self.assertIsNone(report["summary"]["backend_match"])
        finally:
            pitch_prewarm.RUNS_DIR = original_runs_dir


class PitchReadinessIntegrationTests(unittest.TestCase):
    def test_pitch_prewarm_reader_is_registered(self):
        prefixes = [prefix for prefix, _label in pitch_readiness.DRILL_PREFIXES]
        self.assertIn("pitch_prewarm_", prefixes)
        self.assertIn("pitch_prewarm_", pitch_readiness.DRILL_READERS)

    def test_read_pitch_prewarm_green_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "verdict": "GREEN",
                        "summary": {
                            "verified_cache_hits": 2,
                            "expected_count": 2,
                            "llm_backend": "ollama",
                            "llm_model": "qwen2.5:7b-instruct",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = pitch_readiness._read_pitch_prewarm(Path(tmpdir))
        self.assertEqual("GREEN", result["verdict"])
        self.assertIn("cache verified 2/2", result["detail"])
        self.assertIn("backend=ollama", result["detail"])

    def test_read_pitch_prewarm_missing_report_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pitch_readiness._read_pitch_prewarm(Path(tmpdir))
        self.assertEqual("UNKNOWN", result["verdict"])

    def test_read_pitch_prewarm_mismatch_detail_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "verdict": "YELLOW",
                        "summary": {
                            "verified_cache_hits": 2,
                            "expected_count": 2,
                            "llm_backend": "minimax",
                            "llm_model": "minimax-m2.7-highspeed",
                            "requested_backend": "ollama",
                            "requested_model": "qwen2.5:7b-instruct",
                            "backend_match": False,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = pitch_readiness._read_pitch_prewarm(Path(tmpdir))
        self.assertEqual("YELLOW", result["verdict"])
        self.assertIn("requested=ollama / qwen2.5:7b-instruct (mismatch)", result["detail"])


if __name__ == "__main__":
    unittest.main()
