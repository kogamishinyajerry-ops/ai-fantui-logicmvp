"""P21-01 LLM client adapter unit tests.

Covers MiniMaxClient and OllamaClient happy/error paths plus the
``get_llm_client`` factory / backend-selection contract. These tests
anchor the adapter boundary that demo_server now depends on.
"""
from __future__ import annotations

import json
import sys
import unittest
import unittest.mock
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness import llm_client as lc


def _fake_response(body: dict) -> unittest.mock.MagicMock:
    """Build a context-manager mock for urllib.request.urlopen."""
    mock_resp = unittest.mock.MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode("utf-8")
    mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = unittest.mock.MagicMock(return_value=None)
    return mock_resp


class TestMiniMaxClient(unittest.TestCase):
    def test_missing_api_key_raises(self):
        client = lc.MiniMaxClient(api_key="")
        with self.assertRaises(lc.LLMClientError) as ctx:
            client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "minimax_api_key_missing")

    def test_successful_chat_returns_content(self):
        client = lc.MiniMaxClient(api_key="test-key")
        resp = _fake_response({
            "choices": [{"message": {"content": "hello world"}}]
        })
        with unittest.mock.patch("urllib.request.urlopen", return_value=resp):
            out = client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(out, "hello world")

    def test_http_error_maps_to_http_error_code(self):
        client = lc.MiniMaxClient(api_key="test-key")
        err = urllib.error.HTTPError(lc.MiniMaxClient.URL, 429, "rate", {}, None)
        with unittest.mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "minimax_http_error")

    def test_generic_failure_maps_to_error_code(self):
        client = lc.MiniMaxClient(api_key="test-key")
        with unittest.mock.patch("urllib.request.urlopen", side_effect=RuntimeError("boom")):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "minimax_error")

    def test_empty_content_maps_to_empty_response(self):
        client = lc.MiniMaxClient(api_key="test-key")
        resp = _fake_response({"choices": [{"message": {"content": ""}}]})
        with unittest.mock.patch("urllib.request.urlopen", return_value=resp):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "minimax_empty_response")

    def test_api_key_falls_back_to_file(self):
        """api_key property reads ~/.minimax_key when no arg passed."""
        fake_home = Path("/tmp/_p21_minimax_home_test")
        fake_home.mkdir(exist_ok=True)
        (fake_home / ".minimax_key").write_text("file-loaded-key\n")
        try:
            with unittest.mock.patch.object(lc.Path, "home", return_value=fake_home):
                client = lc.MiniMaxClient()
                self.assertEqual(client.api_key, "file-loaded-key")
        finally:
            (fake_home / ".minimax_key").unlink()
            fake_home.rmdir()


class TestOllamaClient(unittest.TestCase):
    def test_successful_chat_returns_content(self):
        client = lc.OllamaClient()
        resp = _fake_response({"message": {"content": "local-reply"}})
        with unittest.mock.patch("urllib.request.urlopen", return_value=resp):
            out = client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(out, "local-reply")

    def test_unreachable_maps_to_unreachable_code(self):
        client = lc.OllamaClient()
        err = urllib.error.URLError("Connection refused")
        with unittest.mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "ollama_unreachable")

    def test_http_error_maps_to_http_error_code(self):
        client = lc.OllamaClient()
        err = urllib.error.HTTPError("http://x", 500, "err", {}, None)
        with unittest.mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "ollama_http_error")

    def test_generic_failure_maps_to_error_code(self):
        client = lc.OllamaClient()
        with unittest.mock.patch("urllib.request.urlopen", side_effect=RuntimeError("boom")):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "ollama_error")

    def test_empty_content_maps_to_empty_response(self):
        client = lc.OllamaClient()
        resp = _fake_response({"message": {"content": ""}})
        with unittest.mock.patch("urllib.request.urlopen", return_value=resp):
            with self.assertRaises(lc.LLMClientError) as ctx:
                client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(ctx.exception.code, "ollama_empty_response")

    def test_env_vars_override_defaults(self):
        with unittest.mock.patch.dict("os.environ", {
            "OLLAMA_URL": "http://host:9999/api/chat",
            "OLLAMA_MODEL": "glm4:9b-chat",
        }):
            client = lc.OllamaClient()
            self.assertEqual(client._url, "http://host:9999/api/chat")
            self.assertEqual(client._model, "glm4:9b-chat")


class TestGetLLMClientFactory(unittest.TestCase):
    def test_default_returns_minimax(self):
        with unittest.mock.patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("LLM_BACKEND", None)
            client = lc.get_llm_client()
        self.assertIsInstance(client, lc.MiniMaxClient)

    def test_explicit_minimax(self):
        self.assertIsInstance(lc.get_llm_client("minimax"), lc.MiniMaxClient)

    def test_explicit_ollama(self):
        self.assertIsInstance(lc.get_llm_client("ollama"), lc.OllamaClient)

    def test_env_ollama(self):
        with unittest.mock.patch.dict("os.environ", {"LLM_BACKEND": "ollama"}):
            client = lc.get_llm_client()
        self.assertIsInstance(client, lc.OllamaClient)

    def test_unknown_backend_raises_llm_backend_unknown(self):
        with self.assertRaises(lc.LLMClientError) as ctx:
            lc.get_llm_client("nonesuch")
        self.assertEqual(ctx.exception.code, "llm_backend_unknown")

    def test_supported_backends_lists_both(self):
        supported = tuple(lc.supported_backends())
        self.assertIn("minimax", supported)
        self.assertIn("ollama", supported)

    def test_case_insensitive_backend(self):
        self.assertIsInstance(lc.get_llm_client("OLLAMA"), lc.OllamaClient)
        self.assertIsInstance(lc.get_llm_client("MiniMax"), lc.MiniMaxClient)


if __name__ == "__main__":
    unittest.main()
