"""P45-03 — LLM-backed interpreter via MiniMax-M2.7-highspeed.

The default interpretation strategy stays "rules" so every existing
caller is unaffected. With strategy="llm", the server calls
MiniMax-M2.7-highspeed (OpenAI-compatible at api.minimaxi.com/v1)
and returns the same canonical schema augmented with
interpreter_strategy. On any LLM failure (no API key, network,
parse error) the function transparently falls back to the rules
interpreter and tags the result with
interpreter_strategy="llm_fallback_to_rules" + llm_error.

Truth-engine red line: this is still a workbench-layer feature.
The LLM call is an outbound request whose result is normalized
back into the canonical interpretation schema; nothing in
controller / runner / models / adapters is touched.
"""

from __future__ import annotations

import http.client
import io
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError

import pytest

from well_harness import demo_server as ds


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── Test isolation: scrub LLM env so tests are deterministic ──────


@pytest.fixture(autouse=True)
def _scrub_minimax_env(monkeypatch):
    """Strip every MiniMax env var the resolver looks at, AND
    redirect ~/.minimax_key to a non-existent path. Each test
    re-installs only what it needs."""
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("Minimax_API_key", raising=False)
    # Steer the file fallback at a guaranteed-missing path
    monkeypatch.setattr(
        ds,
        "_resolve_minimax_api_key",
        lambda: ds.os.environ.get("MINIMAX_API_KEY")
        or ds.os.environ.get("Minimax_API_key")
        or None,
    )


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), ds.DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post(server, path: str, body: dict):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request(
        "POST", path,
        body=json.dumps(body),
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(raw)


# ─── Helper: mock urlopen response ──────────────────────────────────


class _FakeResponse:
    def __init__(self, body: bytes):
        self._buf = io.BytesIO(body)

    def read(self):
        return self._buf.getvalue()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _ok_minimax_response(content: dict) -> bytes:
    """Wrap a content dict in MiniMax's OpenAI-compatible envelope."""
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(content, ensure_ascii=False),
                }
            }
        ]
    }
    return json.dumps(payload).encode("utf-8")


# ─── 1. Strategy = rules (zero regression) ──────────────────────────


def test_endpoint_default_strategy_is_rules(server):
    """The default strategy MUST stay "rules" so every existing
    caller (and every passing P44-02..06 test) keeps working."""
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L2 SW2 应该 tighten"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "rules"
    # Schema should still match the rules interpreter.
    assert body["affected_gates"] == ["L2"]
    assert body["change_kind"] == "tighten_condition"


def test_endpoint_explicit_strategy_rules_does_not_call_llm(server, monkeypatch):
    """Setting strategy="rules" explicitly must not touch the LLM
    call site at all. Spy by patching the LLM caller to assert
    it was never invoked."""
    sentinel = {"called": False}
    def _spy(*args, **kwargs):
        sentinel["called"] = True
        raise AssertionError("LLM should not run for strategy=rules")
    monkeypatch.setattr(ds, "_call_minimax_chat_completion", _spy)
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L1 SW1 应该 tighten", "strategy": "rules"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "rules"
    assert sentinel["called"] is False


def test_endpoint_unknown_strategy_falls_back_to_rules(server):
    """Permissive: a typoed strategy doesn't 400 — it falls back to
    rules so the demo stays resilient."""
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L1 SW1", "strategy": "neural-cortex-9000"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "rules"


# ─── 2. Strategy = llm with mocked successful call ──────────────────


def test_llm_strategy_returns_normalized_llm_response(server, monkeypatch):
    """Mock both the API key resolver and urlopen so the LLM call
    "succeeds" with a canonical-shaped payload. Verify the response
    carries interpreter_strategy="llm" + llm_model + the LLM's
    affected_gates."""
    monkeypatch.setattr(ds, "_resolve_minimax_api_key", lambda: "sk-test-fake-key")
    captured = {}
    def _fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = request.data.decode("utf-8") if request.data else ""
        captured["timeout"] = timeout
        content = {
            "affected_gates": ["L2", "L3"],
            "target_signals": ["SW2"],
            "change_kind": "tighten_condition",
            "change_kind_zh": "收紧判据",
            "change_kind_en": "tighten condition",
            "confidence": 0.9,
            "summary_zh": "在 L2、L3 上对 SW2 收紧判据",
            "summary_en": "Tighten the SW2 condition on gates L2 and L3",
        }
        return _FakeResponse(_ok_minimax_response(content))
    monkeypatch.setattr(ds.urllib.request if hasattr(ds, "urllib") else __import__("urllib.request").request, "urlopen", _fake_urlopen)
    # The function imports urllib.request locally (`import urllib.request as _urlreq`),
    # so patch the real module too.
    import urllib.request as _ur
    monkeypatch.setattr(_ur, "urlopen", _fake_urlopen)

    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L2 L3 上的 SW2 都应该 tighten", "strategy": "llm"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "llm"
    assert body["llm_model"] == "MiniMax-M2.7-highspeed"
    assert body["affected_gates"] == ["L2", "L3"]
    assert body["target_signals"] == ["SW2"]
    assert body["change_kind"] == "tighten_condition"
    assert body["confidence"] == 0.9
    # Verify the outbound call used the right endpoint + Bearer auth.
    assert captured["url"].endswith("/chat/completions")
    auth = dict(captured["headers"]).get("Authorization", "")
    assert auth == "Bearer sk-test-fake-key"
    # Body must include the requested model name.
    assert '"model": "MiniMax-M2.7-highspeed"' in captured["body"]
    # 60s lets the reasoning-style MiniMax-M2.7-highspeed finish
    # without prematurely tripping the urllib timeout (raised from
    # 30s after a real session showed the call running long).
    assert captured["timeout"] == 60.0


def test_strip_json_fences_drops_minimax_think_block():
    """MiniMax-M2.7-highspeed wraps its reasoning in <think>...</think>
    BEFORE the answer — the parser must strip these so the JSON
    parse step works."""
    raw = (
        "<think>\n"
        "Engineer wants to tighten L2 SW2. I'll classify as "
        "tighten_condition with high confidence.\n"
        "</think>\n"
        + json.dumps({"affected_gates": ["L2"], "change_kind": "tighten_condition"})
    )
    cleaned = ds._strip_json_fences(raw)
    parsed = json.loads(cleaned)
    assert parsed["affected_gates"] == ["L2"]


def test_strip_json_fences_handles_think_then_fence():
    """Belt + suspenders: a model that emits BOTH a <think> block AND
    a ```json fence around the answer must still parse."""
    raw = (
        "<think>reasoning here</think>\n"
        "```json\n"
        + json.dumps({"affected_gates": ["L1"]})
        + "\n```"
    )
    cleaned = ds._strip_json_fences(raw)
    parsed = json.loads(cleaned)
    assert parsed["affected_gates"] == ["L1"]


def test_llm_strategy_strips_markdown_json_fences(monkeypatch):
    """LLMs sometimes wrap JSON in ```json ... ``` despite being told
    not to. The interpreter must strip those before parsing so a
    decorated response still works."""
    monkeypatch.setattr(ds, "_resolve_minimax_api_key", lambda: "sk-test")
    fenced = (
        "```json\n"
        + json.dumps({
            "affected_gates": ["L1"],
            "target_signals": [],
            "change_kind": "modify_condition",
            "change_kind_zh": "修改判据",
            "change_kind_en": "modify condition",
            "confidence": 0.7,
            "summary_zh": "修改 L1 判据",
            "summary_en": "Modify L1 condition",
        })
        + "\n```"
    )
    payload = json.dumps({
        "choices": [{"message": {"role": "assistant", "content": fenced}}]
    }).encode("utf-8")
    import urllib.request as _ur
    monkeypatch.setattr(_ur, "urlopen", lambda req, timeout=None: _FakeResponse(payload))
    result = ds.interpret_suggestion_text_llm("L1 改判据", system_id="thrust-reverser")
    assert result["interpreter_strategy"] == "llm"
    assert result["affected_gates"] == ["L1"]


# ─── 3. Failure modes → fall back to rules ──────────────────────────


def test_no_api_key_falls_back_to_rules_with_explicit_error(server):
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L1 SW1 应该 tighten", "strategy": "llm"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "llm_fallback_to_rules"
    assert body["llm_error"] == "missing_api_key"
    # Rules result still came through underneath.
    assert body["affected_gates"] == ["L1"]
    assert body["change_kind"] == "tighten_condition"


def test_network_error_falls_back_to_rules(server, monkeypatch):
    monkeypatch.setattr(ds, "_resolve_minimax_api_key", lambda: "sk-test")
    import urllib.request as _ur
    def _boom(req, timeout=None):
        raise URLError("connection refused")
    monkeypatch.setattr(_ur, "urlopen", _boom)
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L2 SW2 应该 tighten", "strategy": "llm"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "llm_fallback_to_rules"
    assert "URLError" in body["llm_error"]
    assert body["affected_gates"] == ["L2"]


def test_malformed_llm_json_falls_back_to_rules(monkeypatch):
    monkeypatch.setattr(ds, "_resolve_minimax_api_key", lambda: "sk-test")
    import urllib.request as _ur
    bad = json.dumps({
        "choices": [{"message": {"role": "assistant", "content": "{not json"}}]
    }).encode("utf-8")
    monkeypatch.setattr(_ur, "urlopen", lambda req, timeout=None: _FakeResponse(bad))
    result = ds.interpret_suggestion_text_llm("L1", system_id="thrust-reverser")
    assert result["interpreter_strategy"] == "llm_fallback_to_rules"
    assert "JSONDecodeError" in result["llm_error"]


def test_llm_response_missing_choices_falls_back(monkeypatch):
    monkeypatch.setattr(ds, "_resolve_minimax_api_key", lambda: "sk-test")
    import urllib.request as _ur
    empty = json.dumps({"choices": []}).encode("utf-8")
    monkeypatch.setattr(_ur, "urlopen", lambda req, timeout=None: _FakeResponse(empty))
    result = ds.interpret_suggestion_text_llm("L1", system_id="thrust-reverser")
    assert result["interpreter_strategy"] == "llm_fallback_to_rules"
    assert "ValueError" in result["llm_error"]


# ─── 4. API key resolver order ──────────────────────────────────────


def test_resolver_prefers_uppercase_env(monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "  sk-uppercase-canonical  ")
    monkeypatch.setenv("Minimax_API_key", "sk-mixedcase-fallback")
    # Re-bind the real resolver (autouse fixture above stubbed it)
    monkeypatch.setattr(
        ds, "_resolve_minimax_api_key",
        ds._resolve_minimax_api_key.__wrapped__ if hasattr(ds._resolve_minimax_api_key, "__wrapped__") else None,
        raising=False,
    )
    # Use the actual function directly to bypass the autouse stub.
    from importlib import reload
    reload(ds)
    monkeypatch.setenv("MINIMAX_API_KEY", "  sk-uppercase-canonical  ")
    monkeypatch.setenv("Minimax_API_key", "sk-mixedcase-fallback")
    assert ds._resolve_minimax_api_key() == "sk-uppercase-canonical"


def test_resolver_falls_back_to_mixed_case(monkeypatch):
    from importlib import reload
    reload(ds)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.setenv("Minimax_API_key", "sk-mixed-only")
    assert ds._resolve_minimax_api_key() == "sk-mixed-only"


# ─── 5. Frontend wiring ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Topbar/section toggle button anchor.
        'id="workbench-interpreter-strategy-toggle"',
        'data-interpreter-strategy="rules"',
        "📜 规则解读 · Rules",
        # Result panel badge slot.
        'id="workbench-suggestion-interpretation-strategy"',
        # Bilingual chip body.
        "解读策略 · Interpreter",
        # MiniMax + key requirement called out in the chip title.
        "MiniMax-M2.7-highspeed",
    ],
)
def test_workbench_html_carries_strategy_toggle(needle):
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert needle in html, f"workbench.html missing P45-03 hook: {needle}"


@pytest.mark.parametrize(
    "needle",
    [
        # Toggle plumbing
        "function toggleInterpreterStrategy()",
        "function currentInterpreterStrategy()",
        # POST body now carries strategy + system_id
        "JSON.stringify({ text, strategy, system_id })",
        # Result panel populates the strategy badge
        "interpretation.interpreter_strategy",
        # The 3 badge text variants
        "🤖 via ${interpretation.llm_model",
        "📜 via rules",
        "fell back to rules",
    ],
)
def test_workbench_js_wires_strategy_toggle(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing P45-03 wiring: {needle}"


# ─── 6. Truth-engine red line ──────────────────────────────────────


def test_p45_03_does_not_leak_into_truth_engine():
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "interpret_suggestion_text_llm",
        "_resolve_minimax_api_key",
        "MINIMAX_API_BASE",
        "MiniMax-M2.7-highspeed",
        "toggleInterpreterStrategy",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P45-03 token "
                f"'{token}' — LLM interpreter must stay in the "
                f"workbench layer (demo_server + workbench static)"
            )
