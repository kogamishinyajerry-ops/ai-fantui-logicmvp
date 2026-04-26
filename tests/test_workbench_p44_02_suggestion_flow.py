"""P44-02 — chrome slim + suggestion-input flow.

The 4-tool annotation toolbar (point/area/link/text-range) was a
design dead-end — engineers shouldn't have to learn a tool grammar.
This sub-phase replaces the toolbar with a free-form suggestion flow:

  1. Engineer types a modification suggestion at #workbench-suggestion-input
  2. POST /api/workbench/interpret-suggestion {text} returns
     {affected_gates, target_signals, change_kind, summary, confidence}
  3. UI renders the interpretation and adds .is-suggestion-target to the
     SVG <use data-gate-id="..."> elements that match affected_gates
  4. Engineer confirms the interpretation matches intent (or re-interprets)
  5. Submit ticket — P44-02 stops at session-draft echo; P44-03 will
     persist to a real proposal store

The trust banner + annotation toolbar + authority banner were removed
to free vertical space for the circuit hero. The truth-engine read-only
constraint is now expressed by a small chip in the topbar plus the
workflow itself (engineers PROPOSE, never edit truth).
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    interpret_suggestion_text,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read().decode("utf-8")
    return response.status, body, dict(response.getheaders())


def _post_json(
    server: ThreadingHTTPServer, path: str, payload: dict
) -> tuple[int, dict, dict]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(
        "POST",
        path,
        body=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
    )
    response = connection.getresponse()
    raw = response.read().decode("utf-8")
    headers = dict(response.getheaders())
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"raw": raw}
    return response.status, parsed, headers


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Chrome slim: trust banner + annotation toolbar + authority
#       banner are GONE, replaced by a single tiny chip ────────────


@pytest.mark.parametrize(
    "removed",
    [
        # Trust banner DOM
        'id="workbench-trust-banner"',
        'class="workbench-trust-banner"',
        'data-trust-banner-dismiss',
        '此处"手动反馈"的含义',
        "该模式仅作参考",
        "隐藏（本次会话）",
        # Annotation toolbar DOM
        'id="workbench-annotation-toolbar"',
        'data-annotation-tool="point"',
        'data-annotation-tool="area"',
        'data-annotation-tool="link"',
        'data-annotation-tool="text-range"',
        "工具激活",
        # Authority banner DOM
        'id="workbench-authority-banner"',
        'class="workbench-authority-banner"',
        "Propose 不修改",
        "v6.1 红线条款 →",
    ],
)
def test_workbench_html_drops_old_chrome(removed: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert removed not in html, (
        f"P44-02 expected to remove `{removed}` from /workbench but it is still present"
    )


def test_workbench_topbar_uses_compact_mode() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    # The compact modifier class on the topbar + brand keeps the
    # circuit hero in the first viewport.
    assert 'class="workbench-collab-topbar is-compact"' in html
    assert "workbench-collab-brand-compact" in html


def test_workbench_truth_engine_chip_replaces_banner() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-truth-engine-chip"' in html
    assert "🔒 真值引擎只读" in html
    # The chip's link must still point at the live in-repo route.
    chip_block = html.split('id="workbench-truth-engine-chip"')[1].split("</span>")[0]
    assert 'href="/v6.1-redline"' in chip_block


# ─── 2. Suggestion-input flow DOM is in place ────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-suggestion-flow"',
        'id="workbench-suggestion-form"',
        'id="workbench-suggestion-input"',
        'id="workbench-suggestion-interpret-btn"',
        'id="workbench-suggestion-interpretation"',
        'id="workbench-suggestion-interpretation-gates"',
        'id="workbench-suggestion-interpretation-change-kind"',
        'id="workbench-suggestion-interpretation-targets"',
        'id="workbench-suggestion-interpretation-summary"',
        'id="workbench-suggestion-interpretation-confidence"',
        'id="workbench-suggestion-confirm-btn"',
        'id="workbench-suggestion-reinterpret-btn"',
        'id="workbench-suggestion-cancel-btn"',
        'id="workbench-suggestion-status"',
        # Bilingual copy
        "提交修改建议 · Submit Change Proposal",
        "解读建议 · Interpret",
        "✅ 确认并提交工单",
        "↻ 重新解读",
    ],
)
def test_workbench_html_carries_suggestion_flow(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"missing P44-02 suggestion-flow anchor: {anchor}"


def test_workbench_suggestion_interpretation_starts_hidden() -> None:
    """The interpretation card must be hidden until the engineer clicks
    `解读建议` and the server returns a real interpretation."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    card_block = html.split('id="workbench-suggestion-interpretation"')[1].split(">")[0]
    assert "hidden" in card_block, (
        "interpretation card must be hidden by default; got block: " + card_block
    )


# ─── 3. workbench.js wires the flow end-to-end ───────────────────────


@pytest.mark.parametrize(
    "js_anchor",
    [
        "function installSuggestionFlow",
        "function runSuggestionInterpret",
        "function renderSuggestionInterpretation",
        "function highlightSuggestionGates",
        "function submitSuggestionTicket",
        '"/api/workbench/interpret-suggestion"',
        "is-suggestion-target",
        # The boot path must call the installer
        "installSuggestionFlow();",
    ],
)
def test_workbench_js_installs_suggestion_flow(js_anchor: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert js_anchor in js, f"missing P44-02 JS hook: {js_anchor}"


# ─── 4. /api/workbench/interpret-suggestion endpoint contract ────────


def test_interpret_suggestion_endpoint_happy_path(server) -> None:
    status, body, headers = _post_json(
        server,
        "/api/workbench/interpret-suggestion",
        {"text": "L1 的 SW1 == True 判据应该改成持续 50ms"},
    )
    assert status == 200
    assert "application/json" in headers.get("Content-Type", "")
    assert body["affected_gates"] == ["L1"]
    assert "SW1" in body["target_signals"]
    assert body["change_kind"] == "modify_condition"
    assert body["change_kind_zh"] == "修改判据"
    assert body["change_kind_en"] == "modify condition"
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["confidence"] >= 0.8  # gate + signal + verb all match
    assert "L1" in body["summary_zh"]
    assert "SW1" in body["summary_en"]
    assert body["source_text"] == "L1 的 SW1 == True 判据应该改成持续 50ms"


def test_interpret_suggestion_endpoint_rejects_empty_text(server) -> None:
    status, body, _ = _post_json(server, "/api/workbench/interpret-suggestion", {"text": ""})
    assert status == 400
    assert body["error"] == "missing_or_empty_text"


def test_interpret_suggestion_endpoint_rejects_missing_text(server) -> None:
    status, body, _ = _post_json(server, "/api/workbench/interpret-suggestion", {})
    assert status == 400
    assert body["error"] == "missing_or_empty_text"


def test_interpret_suggestion_endpoint_rejects_invalid_json(server) -> None:
    body = b"not json"
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(
        "POST",
        "/api/workbench/interpret-suggestion",
        body=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
    )
    response = connection.getresponse()
    raw = response.read().decode("utf-8")
    assert response.status == 400
    assert json.loads(raw)["error"] == "invalid_json"


def test_interpret_suggestion_endpoint_rejects_oversized_text(server) -> None:
    status, body, _ = _post_json(
        server, "/api/workbench/interpret-suggestion", {"text": "x" * 5001}
    )
    assert status == 400
    assert body["error"] == "text_too_long"


# ─── 5. interpret_suggestion_text pure function (unit-level) ─────────


def test_interpret_suggestion_text_detects_each_gate() -> None:
    for gate_id in ("L1", "L2", "L3", "L4"):
        result = interpret_suggestion_text(f"建议在 {gate_id} 上调整判据")
        assert gate_id in result["affected_gates"], (
            f"interpreter failed to detect {gate_id}: {result}"
        )


def test_interpret_suggestion_text_detects_synonyms() -> None:
    # Plain-language synonym
    r1 = interpret_suggestion_text("逻辑门 2 的 SW2 应该 tighten")
    assert r1["affected_gates"] == ["L2"]
    assert "SW2" in r1["target_signals"]
    assert r1["change_kind"] == "tighten_condition"
    # Output-signal synonym (L2 corresponds to etrac_540vdc_cmd)
    r2 = interpret_suggestion_text("etrac_540vdc_cmd should be loosen for engine restart cases")
    assert r2["affected_gates"] == ["L2"]
    assert r2["change_kind"] == "loosen_condition"


@pytest.mark.parametrize(
    "verb_text,expected_kind",
    [
        ("应该改成 X", "modify_condition"),
        ("应改为 X", "modify_condition"),
        ("update to X", "modify_condition"),
        ("去掉 SW1", "remove_condition"),
        ("remove SW1", "remove_condition"),
        ("增加 SW3", "add_condition"),
        ("放宽 tra_deg", "loosen_condition"),
        ("收紧判据", "tighten_condition"),
        ("调整 n1k 阈值", "tune_condition"),
        ("建议把这里改进一下", "propose_change"),
    ],
)
def test_interpret_suggestion_text_classifies_change_kind(
    verb_text: str, expected_kind: str
) -> None:
    result = interpret_suggestion_text(verb_text)
    assert result["change_kind"] == expected_kind, (
        f"expected {expected_kind} for {verb_text!r}, got {result['change_kind']!r}"
    )


def test_interpret_suggestion_text_low_confidence_when_no_gate() -> None:
    # No gate id, no signal, no change verb — should be lowest confidence.
    result = interpret_suggestion_text("总体感觉还不错")
    assert result["affected_gates"] == []
    assert result["target_signals"] == []
    assert result["change_kind"] == "propose_change"
    assert result["confidence"] == 0.0


def test_interpret_suggestion_text_full_match_high_confidence() -> None:
    # gate + signal + change verb all match → confidence = 1.0.
    # Note: "更严格" classifies as tighten_condition (more specific than
    # the generic 应该改成/modify_condition); the test verifies the
    # specificity ordering that P44-02 deliberately picked.
    result = interpret_suggestion_text("L3 的 n1k 应该改成更严格的阈值")
    assert result["affected_gates"] == ["L3"]
    assert "n1k" in result["target_signals"]
    assert result["change_kind"] == "tighten_condition"
    assert result["confidence"] == 1.0


# ─── 6. Truth-engine red line preserved ──────────────────────────────


def test_p44_02_does_not_leak_into_truth_engine() -> None:
    """The interpreter and the suggestion flow only READ the engineer's
    text and return a structured restatement; they never mutate
    controller / runner / models / adapters."""
    repo_root = Path(__file__).resolve().parents[1]
    well_harness_dir = repo_root / "src" / "well_harness"
    backend_paths: list[Path] = [
        well_harness_dir / "controller.py",
        well_harness_dir / "runner.py",
        well_harness_dir / "models.py",
    ]
    adapters_dir = well_harness_dir / "adapters"
    if adapters_dir.is_dir():
        backend_paths.extend(
            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
        )
    new_phrases = [
        "提交修改建议 · Submit Change Proposal",
        "解读建议 · Interpret",
        "确认并提交工单",
        "interpret_suggestion_text",
        "_GATE_SYNONYMS",
        "_KNOWN_TARGET_SIGNALS",
        "_CHANGE_KIND_HINTS",
    ]
    for backend in backend_paths:
        text = backend.read_text(encoding="utf-8")
        for phrase in new_phrases:
            assert phrase not in text, (
                f"P44-02 phrase {phrase!r} unexpectedly leaked into "
                f"{backend.relative_to(repo_root)} — truth-engine red-line breach"
            )
