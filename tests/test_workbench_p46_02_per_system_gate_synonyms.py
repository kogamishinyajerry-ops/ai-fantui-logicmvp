"""P46-02 — per-system gate synonyms for the rules interpreter.

Before this phase, _GATE_SYNONYMS was thrust-reverser-only: typing
"主起放下要 add filter" while the dropdown was on landing-gear
returned affected_gates=[] from the rules path (the LLM path did
the right thing because its prompt is system-aware, but the rules
path is the demo's deterministic floor).

P46-02 introduces _GATE_SYNONYMS_BY_SYSTEM + _SIGNALS_BY_SYSTEM,
makes interpret_suggestion_text accept an optional system_id, and
threads system_id through the endpoint handler. Every system in the
P45-01 dropdown now has a domain-honest vocabulary; the
thrust-reverser entry is preserved verbatim so all P44 tests keep
passing without a rewrite.

Truth-engine red line: pure interpreter-layer addition. No new
endpoints, no new server state, no controller / runner / models /
adapters changes.
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
    _GATE_SYNONYMS,
    _GATE_SYNONYMS_BY_SYSTEM,
    _KNOWN_TARGET_SIGNALS,
    _SIGNALS_BY_SYSTEM,
    _gate_synonyms_for,
    _signals_for,
    interpret_suggestion_text,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── 1. Back-compat: thrust-reverser default unchanged ──────────────


def test_default_call_still_targets_thrust_reverser():
    """Calling without system_id MUST behave identically to the
    pre-P46-02 thrust-reverser-only interpreter so all P44 tests
    keep passing."""
    result = interpret_suggestion_text("L2 上的 SW2 应该 tighten")
    assert result["affected_gates"] == ["L2"]
    assert result["target_signals"] == ["SW2"]
    assert result["change_kind"] == "tighten_condition"


def test_legacy_aliases_still_resolve():
    """A handful of older tests import _GATE_SYNONYMS /
    _KNOWN_TARGET_SIGNALS by name. They must still work and carry
    the thrust-reverser vocabulary. Compare by value (==) not
    identity (is) — the P45-03 LLM tests reload the demo_server
    module which would otherwise break an `is` check across files."""
    assert "L1" in _GATE_SYNONYMS
    assert _GATE_SYNONYMS == _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"]
    assert _KNOWN_TARGET_SIGNALS == _SIGNALS_BY_SYSTEM["thrust-reverser"]


# ─── 2. Each system in the dropdown gets a vocabulary ──────────────


@pytest.mark.parametrize("system_id", ["thrust-reverser", "landing-gear", "bleed-air-valve", "c919-etras"])
def test_every_dropdown_system_has_gate_vocabulary(system_id):
    vocab = _gate_synonyms_for(system_id)
    assert isinstance(vocab, dict) and len(vocab) >= 2, (
        f"system {system_id!r} has no usable gate vocabulary"
    )


@pytest.mark.parametrize("system_id", ["thrust-reverser", "landing-gear", "bleed-air-valve", "c919-etras"])
def test_every_dropdown_system_has_signal_vocabulary(system_id):
    sigs = _signals_for(system_id)
    assert isinstance(sigs, tuple) and len(sigs) >= 1, (
        f"system {system_id!r} has no signal vocabulary"
    )


def test_unknown_system_falls_back_to_thrust_reverser():
    """Defensive default: a typo / future system_id resolves to TR
    rather than returning an empty vocabulary (which would silently
    make the rules path useless). Compare by value — module reloads
    elsewhere in the suite mean identity (`is`) can't be trusted."""
    assert _gate_synonyms_for("xenon-quark-engine") == _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"]
    assert _signals_for("xenon-quark-engine") == _SIGNALS_BY_SYSTEM["thrust-reverser"]


# ─── 3. Per-system interpretation behaves correctly ─────────────────


def test_landing_gear_interprets_main_gear_phrase():
    """Domain phrase that didn't trigger anything before P46-02."""
    result = interpret_suggestion_text(
        "主起落架放下应该 add filter，避免误触发",
        system_id="landing-gear",
    )
    assert "G1" in result["affected_gates"]
    assert result["change_kind"] == "add_condition"


def test_bleed_air_valve_interprets_bleed_open_phrase():
    result = interpret_suggestion_text(
        "bleed open 判据需要 tighten",
        system_id="bleed-air-valve",
    )
    assert "V1" in result["affected_gates"]
    assert result["change_kind"] == "tighten_condition"


def test_c919_etras_interprets_etras_deploy_phrase():
    result = interpret_suggestion_text(
        "ETRAS deploy 判据要 tune 调整",
        system_id="c919-etras",
    )
    assert "E2" in result["affected_gates"]


def test_landing_gear_does_not_match_thrust_reverser_gates():
    """Typing 'L1' on landing-gear should NOT highlight L1 — that
    gate id doesn't exist in the landing-gear vocabulary. This is
    the whole point of per-system tables."""
    result = interpret_suggestion_text(
        "L1 上需要 add filter",
        system_id="landing-gear",
    )
    assert "L1" not in result["affected_gates"]
    # G-series gates also don't accidentally fire on bare "L1".
    for g in ("G1", "G2", "G3", "G4"):
        assert g not in result["affected_gates"]


def test_signal_vocabulary_is_per_system():
    """SW1 belongs to thrust-reverser; weight_on_wheels belongs to
    landing-gear. Each must be detected in its own system and NOT
    in the other (the strings don't appear in the other vocab)."""
    tr = interpret_suggestion_text("SW1 应该 tighten", system_id="thrust-reverser")
    assert "SW1" in tr["target_signals"]

    lg = interpret_suggestion_text(
        "weight_on_wheels 信号要 add filter",
        system_id="landing-gear",
    )
    assert "weight_on_wheels" in lg["target_signals"]
    # weight_on_wheels isn't in thrust-reverser's vocab.
    tr_sig = interpret_suggestion_text(
        "weight_on_wheels 信号要 add filter",
        system_id="thrust-reverser",
    )
    assert "weight_on_wheels" not in tr_sig["target_signals"]


# ─── 4. HTTP endpoint plumbs system_id into the rules path ─────────


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post(server, path, body):
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


def test_endpoint_rules_strategy_honors_system_id(server):
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "主起落架放下要 add filter", "strategy": "rules", "system_id": "landing-gear"},
    )
    assert status == 200
    assert body["interpreter_strategy"] == "rules"
    assert "G1" in body["affected_gates"]
    assert body["change_kind"] == "add_condition"


def test_endpoint_default_system_still_thrust_reverser(server):
    """Omitting system_id keeps the original behavior — important
    because plenty of older clients (and tests) don't send it."""
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L2 SW2 应该 tighten"},
    )
    assert status == 200
    assert body["affected_gates"] == ["L2"]
    assert body["target_signals"] == ["SW2"]


def test_endpoint_unknown_system_falls_back_to_thrust_reverser_vocab(server):
    """A typoed system_id should still return a useful interpretation
    (using TR vocab), not a 400 or empty result."""
    status, body = _post(
        server, "/api/workbench/interpret-suggestion",
        {"text": "L1 上要 tighten", "strategy": "rules", "system_id": "wing-flap-actuator"},
    )
    assert status == 200
    assert body["affected_gates"] == ["L1"]


# ─── 5. Truth-engine red line ──────────────────────────────────────


def test_p46_02_does_not_leak_into_truth_engine():
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "_GATE_SYNONYMS_BY_SYSTEM",
        "_SIGNALS_BY_SYSTEM",
        "_gate_synonyms_for",
        "_signals_for",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P46-02 token "
                f"'{token}' — per-system vocab must stay in the "
                f"interpreter layer"
            )
