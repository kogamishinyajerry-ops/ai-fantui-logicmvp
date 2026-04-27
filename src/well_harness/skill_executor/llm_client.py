"""MiniMax HTTP client for the skill executor — typed return so the
planner captures full provenance (prompt, response, timing, model)
into the audit log.

Why a separate client (vs. importing demo_server's
`_call_minimax_chat_completion`):
  - skill_executor must not depend on the HTTP server module
  - we want a typed return value so audit fields are populated
    automatically, not by every caller wrapping the raw string

The on-the-wire shape is identical to demo_server's interpret-suggestion
path (same MiniMax /chat/completions endpoint, same prompt envelope).
P48-04 may de-dup once we've burned the planner in.
"""

from __future__ import annotations

import dataclasses
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import urllib.error as _urlerr
import urllib.request as _urlreq

from well_harness.skill_executor.errors import SkillExecutorError


MINIMAX_API_BASE: str = "https://api.minimaxi.com/v1"
MINIMAX_DEFAULT_MODEL: str = "MiniMax-M2.7-highspeed"
# Match demo_server.MINIMAX_REQUEST_TIMEOUT_SEC. Reasoning models eat
# ~30s before producing the first answer token; 60s is the headroom
# the user empirically validated.
MINIMAX_REQUEST_TIMEOUT_SEC: float = 60.0


class LLMUnavailableError(SkillExecutorError):
    """LLM service is currently unreachable. Covers:
      - no usable API key in env / fallback file
      - HTTP 5xx (server-side temporary failure)
      - HTTP 408/429 (request timeout, rate limit)
      - urllib URLError (DNS / connection refused / network down)
      - socket timeout

    The orchestrator's P50-03 retry loop catches this exception
    and reattempts with backoff, since by definition all of these
    are transient. PlannerError (schema/validation) and
    LLMResponseError (malformed JSON) are NOT retried — those
    stay deterministic across retries with the same prompt."""


class LLMResponseError(SkillExecutorError):
    """The HTTP call returned but the response shape was not the
    expected `{choices: [{message: {content: ...}}]}` envelope."""


@dataclasses.dataclass
class LLMResponse:
    """One round-trip's full provenance for the audit log."""

    content: str          # the cleaned model text (post-fence-strip)
    raw_content: str      # the model text exactly as returned
    prompt: str           # the prompt sent (for replay)
    model: str            # the model id used
    started_at: str       # ISO-8601 UTC with Z
    finished_at: str      # ISO-8601 UTC with Z
    duration_sec: float   # finished_at - started_at, seconds


def resolve_minimax_api_key() -> str | None:
    """Resolve a MiniMax key. Order:
      1. MINIMAX_API_KEY env
      2. Minimax_API_key env (the actual var name in the user's
         ~/.zshrc — preserve the case)
      3. ~/.minimax_key file
    Returns the trimmed key or None.
    """
    for env_name in ("MINIMAX_API_KEY", "Minimax_API_key"):
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()
    fallback = Path(os.path.expanduser("~/.minimax_key"))
    try:
        if fallback.is_file():
            text = fallback.read_text(encoding="utf-8").strip()
            if text:
                return text
    except OSError:
        pass
    return None


def strip_json_fences(raw: str) -> str:
    """Drop `<think>...</think>` reasoning blocks (MiniMax-M2.7
    emits them) and ```json ... ``` fences (some models add them
    even when told not to)."""
    text = raw.strip()
    while True:
        start = text.find("<think>")
        if start < 0:
            break
        end = text.find("</think>", start)
        if end < 0:
            text = text[:start]
            break
        text = (text[:start] + text[end + len("</think>"):]).strip()
    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def call_minimax(
    prompt: str,
    *,
    api_key: str,
    model: str = MINIMAX_DEFAULT_MODEL,
    timeout_sec: float = MINIMAX_REQUEST_TIMEOUT_SEC,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    request_post: callable | None = None,
) -> LLMResponse:
    """Call MiniMax /chat/completions. Returns a typed LLMResponse
    populated with everything the audit needs.

    `request_post` is an injection point for tests: pass a callable
    that takes (url, body_bytes, headers, timeout_sec) and returns
    the raw response body string. Default is urllib's stock POST.
    Production code never passes this; tests use it to avoid real
    network calls.

    Raises LLMResponseError on protocol/parse failure. Caller is
    responsible for catching urllib.error.URLError (subclass of
    OSError) for transport failures.
    """
    started_at = _now_iso()
    started_perf = datetime.now(timezone.utc)
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    ).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # P50-03: HTTP 5xx / network timeouts get classified as
    # LLMUnavailableError so the orchestrator's retry loop catches
    # them. Validation errors (bad JSON shape) stay LLMResponseError
    # because retrying with the same prompt won't help.
    try:
        if request_post is None:
            raw_body = _default_post(
                f"{MINIMAX_API_BASE}/chat/completions",
                body,
                headers,
                timeout_sec,
            )
        else:
            raw_body = request_post(
                f"{MINIMAX_API_BASE}/chat/completions",
                body,
                headers,
                timeout_sec,
            )
    except _urlerr.HTTPError as exc:
        raise LLMUnavailableError(
            f"MiniMax HTTP {exc.code}: {exc.reason}"
        ) from exc
    except (_urlerr.URLError, TimeoutError, OSError) as exc:
        raise LLMUnavailableError(
            f"MiniMax network error: {exc}"
        ) from exc
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(
            f"MiniMax response not valid JSON: {exc}"
        ) from exc
    choices = parsed.get("choices") or []
    if not choices:
        raise LLMResponseError("MiniMax response missing choices array")
    message = choices[0].get("message") or {}
    raw_content = message.get("content")
    if not isinstance(raw_content, str) or not raw_content.strip():
        raise LLMResponseError("MiniMax response missing message.content")
    cleaned = strip_json_fences(raw_content)
    finished_at = _now_iso()
    finished_perf = datetime.now(timezone.utc)
    return LLMResponse(
        content=cleaned,
        raw_content=raw_content,
        prompt=prompt,
        model=model,
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=(finished_perf - started_perf).total_seconds(),
    )


def _default_post(url: str, body: bytes, headers: dict, timeout_sec: float) -> str:
    request = _urlreq.Request(url, data=body, headers=headers, method="POST")
    with _urlreq.urlopen(request, timeout=timeout_sec) as response:
        return response.read().decode("utf-8")
