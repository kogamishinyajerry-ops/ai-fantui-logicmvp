"""P50-03 — call_minimax classifies HTTP/network errors as
transient (LLMUnavailableError) so the orchestrator's retry loop
fires.

Before this slice, urllib's HTTPError / URLError would propagate
uncaught to execute_proposal's outer 'unhandled' branch, bypassing
the retry. After this slice they're explicitly mapped.

Validation errors (bad JSON shape) stay LLMResponseError because
retrying with the same prompt won't change the model's output.
"""

from __future__ import annotations

import io
import socket
import urllib.error

import pytest

from well_harness.skill_executor.llm_client import (
    LLMResponseError,
    LLMUnavailableError,
    call_minimax,
)


def _post_raises(exc: Exception):
    def _post(url, body, headers, timeout):
        raise exc
    return _post


def _post_returns(payload: str):
    def _post(url, body, headers, timeout):
        return payload
    return _post


# ─── HTTP errors → LLMUnavailableError ──────────────────────────────


def test_http_503_raises_llm_unavailable():
    err = urllib.error.HTTPError(
        "https://api.minimaxi.com", 503, "Service Unavailable",
        hdrs=None, fp=io.BytesIO(b""),
    )
    with pytest.raises(LLMUnavailableError) as exc:
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(err),
        )
    assert "503" in str(exc.value)


def test_http_429_raises_llm_unavailable():
    """Rate limit is transient — retry helps."""
    err = urllib.error.HTTPError(
        "https://api.minimaxi.com", 429, "Too Many Requests",
        hdrs=None, fp=io.BytesIO(b""),
    )
    with pytest.raises(LLMUnavailableError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(err),
        )


def test_http_408_request_timeout_is_transient():
    err = urllib.error.HTTPError(
        "https://api.minimaxi.com", 408, "Request Timeout",
        hdrs=None, fp=io.BytesIO(b""),
    )
    with pytest.raises(LLMUnavailableError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(err),
        )


# ─── Network / OS errors → LLMUnavailableError ──────────────────────


def test_url_error_raises_llm_unavailable():
    """Connection refused, DNS failure, etc."""
    err = urllib.error.URLError("Connection refused")
    with pytest.raises(LLMUnavailableError) as exc:
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(err),
        )
    assert "Connection refused" in str(exc.value)


def test_timeout_raises_llm_unavailable():
    with pytest.raises(LLMUnavailableError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(TimeoutError("read timed out")),
        )


def test_socket_timeout_raises_llm_unavailable():
    """socket.timeout is a subclass of OSError, classified as
    transient. Same as a TimeoutError."""
    with pytest.raises(LLMUnavailableError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_raises(socket.timeout("timed out")),
        )


# ─── Validation errors stay LLMResponseError (NOT transient) ───────


def test_bad_json_raises_llm_response_error_not_unavailable():
    """Schema/parse errors aren't transient — same prompt produces
    same bad output. Must stay LLMResponseError so the orchestrator
    DOESN'T retry."""
    with pytest.raises(LLMResponseError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_returns("not valid json {{"),
        )


def test_missing_choices_raises_llm_response_error():
    """Response is valid JSON but the shape is wrong — also
    deterministic per-prompt, so NOT transient."""
    with pytest.raises(LLMResponseError):
        call_minimax(
            "prompt", api_key="x",
            request_post=_post_returns('{"foo": "bar"}'),
        )


# ─── Successful response unaffected ────────────────────────────────


def test_successful_response_returns_llm_response():
    """Sanity check: P50-03's exception handling didn't break
    the happy path."""
    response_body = (
        '{"choices": [{"message": '
        '{"content": "{\\"plan\\": \\"x\\"}"}}]}'
    )
    out = call_minimax(
        "prompt", api_key="x",
        request_post=_post_returns(response_body),
    )
    assert out.raw_content == '{"plan": "x"}'
