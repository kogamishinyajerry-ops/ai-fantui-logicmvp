"""P21 LLM client adapter — MiniMax cloud + Ollama local, selectable via env.

demo_server.py routes (/api/chat/explain, /api/chat/operate, /api/chat/reason)
go through ``get_llm_client().chat(messages, ...)``. The client returns a raw
content str; JSON shape validation stays in the route handlers, keeping the
adapter surface minimal.

Backend selection: ``LLM_BACKEND`` env var.
  - "minimax" (default): MiniMax cloud API, auth from ``~/.minimax_key``
  - "ollama":            local Ollama HTTP API (default http://localhost:11434)

Errors are raised as ``LLMClientError`` with a stable ``code`` string. The
codes mirror the existing demo_server error dict shape so that the front-end
degraded-notice UI (``minimax_api_key_missing`` etc.) continues to fire with
no template changes.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable


class LLMClientError(Exception):
    """Structured error raised by any LLMClient implementation.

    ``code`` maps onto the ``error`` field returned to the front-end by the
    route handlers; ``message`` maps onto ``message``.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@runtime_checkable
class LLMClient(Protocol):
    def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: float = 30.0,
    ) -> str: ...


def _post_json(url: str, payload: dict, headers: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class MiniMaxClient:
    """MiniMax cloud backend — OpenAI-compatible v2 chat/completions shape."""

    URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    DEFAULT_MODEL = "minimax-m2.7-highspeed"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key
        self._model = model or os.environ.get("MINIMAX_MODEL") or self.DEFAULT_MODEL

    @property
    def api_key(self) -> str:
        if self._api_key is None:
            key_path = Path.home() / ".minimax_key"
            if key_path.exists():
                self._api_key = key_path.read_text().strip()
            else:
                self._api_key = ""
        return self._api_key

    def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: float = 30.0,
    ) -> str:
        if not self.api_key:
            raise LLMClientError(
                "minimax_api_key_missing",
                "MiniMax API key not found. Add to ~/.minimax_key.",
            )

        payload = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            result = _post_json(self.URL, payload, headers, timeout)
        except urllib.error.HTTPError as e:
            raise LLMClientError(
                "minimax_http_error",
                f"MiniMax API returned HTTP {e.code}.",
            ) from e
        except Exception:
            raise LLMClientError(
                "minimax_error",
                "MiniMax API request failed.",
            )

        choices = result.get("choices") or []
        if choices:
            content = (choices[0].get("message") or {}).get("content", "") or ""
            if not content:
                content = choices[0].get("text", "") or ""
        else:
            content = ""

        if not content:
            raise LLMClientError(
                "minimax_empty_response",
                "MiniMax returned empty response.",
            )
        return content


class OllamaClient:
    """Local Ollama backend — http://localhost:11434/api/chat by default.

    Supports 国产开源 instruct-tuned models: qwen2.5:7b-instruct,
    glm4:9b-chat, deepseek-v2.5-lite, etc. The chat payload follows
    Ollama's native shape; content is extracted from message.content.

    Error codes mirror MiniMax semantics so the front-end degraded-notice
    path fires identically:
      - ollama_unreachable   ↔  minimax_api_key_missing  (no-backend case)
      - ollama_http_error    ↔  minimax_http_error
      - ollama_error         ↔  minimax_error
      - ollama_empty_response ↔ minimax_empty_response
    """

    DEFAULT_URL = "http://localhost:11434/api/chat"
    DEFAULT_MODEL = "qwen2.5:7b"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self._url = base_url or os.environ.get("OLLAMA_URL", self.DEFAULT_URL)
        self._model = model or os.environ.get("OLLAMA_MODEL", self.DEFAULT_MODEL)

    def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: float = 30.0,
    ) -> str:
        payload = {
            "model": self._model,
            "messages": list(messages),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        headers = {"Content-Type": "application/json"}

        try:
            result = _post_json(self._url, payload, headers, timeout)
        except urllib.error.HTTPError as e:
            raise LLMClientError(
                "ollama_http_error",
                f"Ollama API returned HTTP {e.code}.",
            ) from e
        except urllib.error.URLError as e:
            raise LLMClientError(
                "ollama_unreachable",
                f"Ollama not reachable at {self._url}: {e.reason}.",
            ) from e
        except Exception:
            raise LLMClientError(
                "ollama_error",
                "Ollama API request failed.",
            )

        message = result.get("message") or {}
        content = message.get("content", "") or ""
        if not content:
            raise LLMClientError(
                "ollama_empty_response",
                "Ollama returned empty response.",
            )
        return content


_BACKENDS: dict[str, type] = {
    "minimax": MiniMaxClient,
    "ollama": OllamaClient,
}


def supported_backends() -> Iterable[str]:
    return tuple(_BACKENDS.keys())


def get_llm_client(backend: str | None = None) -> LLMClient:
    """Factory: select backend via arg or ``LLM_BACKEND`` env (default minimax)."""
    chosen = (backend or os.environ.get("LLM_BACKEND") or "minimax").lower()
    cls = _BACKENDS.get(chosen)
    if cls is None:
        raise LLMClientError(
            "llm_backend_unknown",
            f"Unknown LLM_BACKEND={chosen!r}. Supported: {', '.join(_BACKENDS)}.",
        )
    return cls()
