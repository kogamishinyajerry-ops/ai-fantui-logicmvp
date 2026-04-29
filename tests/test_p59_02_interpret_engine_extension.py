"""P59-02 — interpret_suggestion_text returns affected_outputs and a
recommended_work_order_zh / _en draft so the highlight chain (P59-03)
can target output cmd boxes by name and the workbench UI can show a
deterministic ticket draft.

Background: P59-01 added per-signal anchors to fantui_circuit.html.
But the engine that produces highlight targets only returned
affected_gates (L1..L4) + target_signals (input names). Output cmd
names mentioned in the user's text (e.g. "tls_115vac_cmd 时序要改") were
matched via gate-synonym scan and surfaced as the gate id only — the
cmd name itself was lost. P59-02 closes that with three new fields:

- affected_outputs: list[str] — explicit output cmd names from the
  text, derived from _GATE_SYNONYMS_BY_SYSTEM filtered by the "_cmd"
  suffix.
- recommended_work_order_zh / _en: str — template-driven draft built
  from (change_kind, gates, signals, outputs, source_text). Plain
  formatting, no LLM, deterministic.

Backwards compat: every existing return field (affected_gates,
target_signals, change_kind, change_kind_zh/en, confidence,
confidence_breakdown, vocabulary_hint, summary_zh/en, source_text) is
preserved unchanged. The proposal validator at /api/workbench/create-
proposal still requires the old 4 fields and does NOT require the new
3 — so historical proposals stored before P59-02 keep loading.

The LLM normalizer (interpret_suggestion_text_llm path) gets the same
3 new fields with the same templates, so frontend code can consume the
union schema regardless of strategy.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from well_harness.demo_server import (
    _GATE_SYNONYMS_BY_SYSTEM,
    _detect_affected_outputs,
    _normalize_llm_interpretation,
    _output_cmd_names_for,
    _render_recommended_work_order,
    _SIGNALS_BY_SYSTEM,
    interpret_suggestion_text,
)


# ── 1. _output_cmd_names_for derivation ──────────────────────


def test_output_cmd_names_thrust_reverser_matches_historical_set() -> None:
    """The 6 historically-known thrust-reverser output cmds must all
    be in the derived set. A regression that strips one would break
    the highlight target list silently."""
    derived = set(_output_cmd_names_for("thrust-reverser"))
    expected = {
        "tls_115vac_cmd",
        "etrac_540vdc_cmd",
        "eec_deploy_cmd",
        "pls_power_cmd",
        "pdu_motor_cmd",
        "throttle_electronic_lock_release_cmd",
    }
    assert expected.issubset(derived), (
        f"derived output cmds missing from thrust-reverser set: "
        f"{expected - derived}"
    )


def test_output_cmd_names_filter_excludes_non_cmd_synonyms() -> None:
    """Only names ending in '_cmd' are output cmds. Synonyms like
    'L1', 'TLS', '逻辑门 1', or 'throttle_unlock' (a summary id, not a
    cmd) must be filtered out."""
    derived = set(_output_cmd_names_for("thrust-reverser"))
    forbidden = {"L1", "L2", "L3", "L4", "TLS", "ETRAC", "EEC",
                 "throttle_unlock", "逻辑门 1", "门 1"}
    leaks = derived & forbidden
    assert not leaks, f"non-cmd synonyms leaked into output set: {leaks}"


def test_output_cmd_names_per_system_isolation() -> None:
    """Each system's derived output cmds must be distinct (no
    cross-system leakage)."""
    tr = set(_output_cmd_names_for("thrust-reverser"))
    c919 = set(_output_cmd_names_for("c919-etras"))
    lg = set(_output_cmd_names_for("landing-gear"))
    bav = set(_output_cmd_names_for("bleed-air-valve"))
    # thrust-reverser must NOT bleed into c919/landing-gear/bleed
    assert "tls_115vac_cmd" not in c919
    assert "tls_115vac_cmd" not in lg
    assert "tls_115vac_cmd" not in bav
    # c919 names should be there for c919
    assert {"etras_unlock_cmd", "etras_deploy_cmd", "etras_stow_cmd"
            }.issubset(c919)


# ── 2. _detect_affected_outputs scan ──────────────────────────


@pytest.mark.parametrize("text,expected", [
    ("tls_115vac_cmd 时序要改", ["tls_115vac_cmd"]),
    ("把 etrac_540vdc_cmd 推迟 100ms", ["etrac_540vdc_cmd"]),
    # Multi-mention preserves vocab order (insertion order in dict).
    ("eec_deploy_cmd 和 pls_power_cmd 都需要 review", [
        "eec_deploy_cmd", "pls_power_cmd",
    ]),
    # No cmd mention → empty.
    ("L1 应该放宽", []),
    # Pure input signal (no _cmd) → empty.
    ("tra_deg 阈值要改成 -10°", []),
    # Empty / whitespace inputs are safe.
    ("", []),
    ("   ", []),
])
def test_detect_affected_outputs(text: str, expected: list[str]) -> None:
    got = _detect_affected_outputs(text, "thrust-reverser")
    assert got == expected, (
        f"text={text!r}: expected {expected}, got {got}"
    )


# ── 3. interpret_suggestion_text returns the new fields ──────


def test_return_dict_includes_affected_outputs_field() -> None:
    """The new field must always be present (even when empty) so the
    frontend doesn't have to check for undefined."""
    result = interpret_suggestion_text(
        "L1 应该放宽", system_id="thrust-reverser",
    )
    assert "affected_outputs" in result, (
        "interpret_suggestion_text must return affected_outputs even "
        "when no output cmd is named (empty list)."
    )
    assert isinstance(result["affected_outputs"], list)
    assert result["affected_outputs"] == []


def test_return_dict_includes_recommended_work_order_zh_en() -> None:
    result = interpret_suggestion_text(
        "tra_deg 在 L3 阈值要改成 -10",
        system_id="thrust-reverser",
    )
    assert "recommended_work_order_zh" in result
    assert "recommended_work_order_en" in result
    assert isinstance(result["recommended_work_order_zh"], str)
    assert isinstance(result["recommended_work_order_en"], str)
    assert result["recommended_work_order_zh"], (
        "zh work-order must not be empty"
    )
    assert result["recommended_work_order_en"], (
        "en work-order must not be empty"
    )


def test_affected_outputs_populated_when_cmd_named() -> None:
    """User's example: tls_115vac_cmd directly mentioned should yield
    affected_outputs=['tls_115vac_cmd'], affected_gates=['L1'] (because
    tls_115vac_cmd is also an L1 synonym)."""
    result = interpret_suggestion_text(
        "tls_115vac_cmd 时序应该改",
        system_id="thrust-reverser",
    )
    assert result["affected_outputs"] == ["tls_115vac_cmd"]
    assert "L1" in result["affected_gates"]


# ── 4. Work-order template rendering ──────────────────────────


def test_work_order_zh_includes_signal_and_gate_when_both_present() -> None:
    """User's primary example: 'TRA threshold should change' → the
    work order must mention BOTH the gate (L3) and the signal
    (tra_deg) so the engineer can paste it into a ticket without
    rewriting the scope."""
    result = interpret_suggestion_text(
        "tra_deg 应改成 -10°", system_id="thrust-reverser",
    )
    wo = result["recommended_work_order_zh"]
    # Note: this phrase doesn't include "L3" so affected_gates is
    # empty, but tra_deg should still anchor the work order.
    assert "tra_deg" in wo
    assert "原文" in wo


def test_work_order_zh_anchors_on_l3_when_l3_named() -> None:
    """Ensure the gate anchor surfaces when the user names it."""
    result = interpret_suggestion_text(
        "L3 的 tra_deg 阈值改为 -10°",
        system_id="thrust-reverser",
    )
    wo = result["recommended_work_order_zh"]
    assert "L3" in wo, f"work order missing L3: {wo}"
    assert "tra_deg" in wo, f"work order missing tra_deg: {wo}"


def test_work_order_falls_back_when_target_unidentified() -> None:
    """If neither a gate nor a signal can be detected, the work order
    must still produce a non-empty draft and include a clear "请在工单
    中明确" prompt so the engineer knows to clarify."""
    result = interpret_suggestion_text(
        "整个反推系统都需要重新评估",
        system_id="thrust-reverser",
    )
    wo = result["recommended_work_order_zh"]
    assert wo, "work order draft must not be empty"
    assert "请在工单中明确" in wo or "未识别" in wo, (
        f"work order should signal under-specification: {wo}"
    )


@pytest.mark.parametrize("change_kind_phrase,kind_zh,not_in_wo", [
    # Codex R1 §F fix: distinguish add vs remove (both previously
    # asserted the same "建议在" prefix and would not catch a swap).
    # Each branch must contain a UNIQUE phrase AND must NOT contain
    # phrases from sibling branches.
    ("放宽", "建议放宽", "建议收紧"),
    ("收紧", "建议收紧", "建议放宽"),
    ("删除", "中删除", "中新增"),
    ("新增", "中新增", "中删除"),
    ("调整", "建议调整", "建议修改"),
    ("改成", "建议修改", "建议调整"),
])
def test_work_order_template_picks_change_kind_specific_action(
    change_kind_phrase: str, kind_zh: str, not_in_wo: str,
) -> None:
    """Each change_kind branch must produce a distinct action verb in
    the zh work order. Otherwise loosen/tighten/remove/etc. all
    collapse to the same generic propose_change template and the
    engineer can't tell which direction was intended.

    Codex R1 §F: also assert sibling-branch phrases are NOT present so
    a future template swap (loosen ↔ tighten, add ↔ remove,
    tune ↔ modify) fails this test instead of passing silently."""
    text = f"L1 应该{change_kind_phrase}判据"
    result = interpret_suggestion_text(text, system_id="thrust-reverser")
    wo = result["recommended_work_order_zh"]
    assert kind_zh in wo, (
        f"change_kind={result['change_kind']!r} produced work order "
        f"that does not contain action prefix {kind_zh!r}: {wo}"
    )
    assert not_in_wo not in wo, (
        f"change_kind={result['change_kind']!r} work order leaked "
        f"sibling-branch phrase {not_in_wo!r}: {wo}"
    )


def test_work_order_normalizes_whitespace_in_source_quote() -> None:
    """Codex R1 §G fix: source paste with mixed whitespace
    (\\r, \\t, NBSP, zero-width chars) must collapse to single spaces
    so a 199-char paste cannot expand to >200 visible chars."""
    # NBSP =  , zero-width space = ​, ZWNJ = ‌
    weird = "L1  应该\t放宽\r\nSW1​ 的判据"
    result = interpret_suggestion_text(weird, system_id="thrust-reverser")
    wo = result["recommended_work_order_zh"]
    match = re.search(r"「([^」]*)」", wo)
    assert match is not None
    quoted = match.group(1)
    # No tab, CR, NBSP, ZWSP, ZWNJ should remain in the quoted block.
    forbidden = ("\t", "\r", "\n", " ", "​", "‌", "‍")
    for ch in forbidden:
        assert ch not in quoted, (
            f"quoted source still contains {ch!r} after normalization"
        )


def test_work_order_quotes_truncate_long_source() -> None:
    """A 2000-char source paste must not blow up the work order. The
    quoted excerpt should cap at 200 chars + ellipsis."""
    long_text = "L1 应该放宽 " + "x" * 1000
    result = interpret_suggestion_text(long_text, system_id="thrust-reverser")
    wo = result["recommended_work_order_zh"]
    # Find what's between 「 and 」 (the quoted source excerpt).
    match = re.search(r"「([^」]*)」", wo)
    assert match is not None, "work order missing 「...」 quote block"
    quoted = match.group(1)
    assert len(quoted) <= 200, (
        f"quoted source not truncated: len={len(quoted)}"
    )
    if len(long_text) > 200:
        assert quoted.endswith("…"), (
            "long source must end with U+2026 ellipsis, got "
            f"{quoted[-5:]!r}"
        )


# ── 5. Backwards-compatibility ───────────────────────────────


def test_all_legacy_fields_still_present() -> None:
    """No P44 / P46 / P54 contract field may be dropped. The new
    fields are added; nothing is removed."""
    result = interpret_suggestion_text(
        "L1 应该放宽 SW1 的窗口",
        system_id="thrust-reverser",
    )
    legacy_fields = {
        "affected_gates", "target_signals", "change_kind",
        "change_kind_zh", "change_kind_en", "confidence",
        "confidence_breakdown", "vocabulary_hint", "summary_zh",
        "summary_en", "source_text",
    }
    missing = legacy_fields - set(result.keys())
    assert not missing, f"legacy fields dropped: {missing}"


def test_proposal_validator_still_accepts_pre_p59_payload() -> None:
    """A proposal payload without the new fields must still pass the
    /api/workbench/create-proposal validator. Adding the new fields
    to the required set would break historical proposals on reload."""
    import http.client
    import json
    import threading
    from http.server import ThreadingHTTPServer

    from well_harness.demo_server import DemoRequestHandler

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps({
            "source_text": "L1 should be relaxed",
            "interpretation": {
                # Pre-P59-02 shape — no affected_outputs,
                # no recommended_work_order_*.
                "affected_gates": ["L1"],
                "target_signals": [],
                "change_kind": "loosen_condition",
                "summary_zh": "测试",
            },
        }).encode("utf-8")
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5,
        )
        connection.request(
            "POST", "/api/proposals", body=body,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        status = response.status
        response.read()
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
    # 201 on first-time create OR 4xx for legitimate non-validator
    # reasons (file write etc.). The KEY requirement is we do NOT
    # 400 on missing affected_outputs / missing recommended_work_*.
    assert status != 400 or True, (
        "proposal validator rejected pre-P59-02 payload — required-"
        "field set should not have grown."
    )
    # More direct check: status should be 201 (success). If something
    # else fails, surface it loudly.
    assert status == 201, (
        f"create-proposal returned {status}; expected 201 for a "
        f"pre-P59-02 payload."
    )


# ── 6. _render_recommended_work_order is a pure function ─────


def test_render_work_order_pure_function_zero_targets() -> None:
    """Helper must produce valid output even when every list is empty
    (caller can hand it nothing if detection failed)."""
    zh, en = _render_recommended_work_order(
        change_kind="propose_change",
        affected_gates=[],
        target_signals=[],
        affected_outputs=[],
        source_text="",
    )
    assert zh
    assert en
    assert "请在工单中明确" in zh or "未识别" in zh
    assert "no specific target identified" in en or "clarify" in en


def test_render_work_order_handles_unknown_change_kind() -> None:
    """An unknown change_kind value must not crash — falls back to
    propose_change template."""
    zh, en = _render_recommended_work_order(
        change_kind="bogus_kind_not_in_taxonomy",
        affected_gates=["L1"],
        target_signals=["SW1"],
        affected_outputs=[],
        source_text="hello",
    )
    assert zh
    assert en
    # Both should mention the scope (SW1 in L1) since fallback still
    # uses the renderer's scope-resolution logic.
    assert "SW1" in zh and "L1" in zh


# ── 7. LLM normalizer parity ────────────────────────────────


def test_llm_normalizer_returns_new_fields() -> None:
    """The LLM-path return shape must include the same new fields so
    callers can consume either strategy uniformly."""
    raw = {
        "affected_gates": ["L1"],
        "target_signals": ["SW1"],
        "change_kind": "loosen_condition",
        "change_kind_zh": "放宽判据",
        "change_kind_en": "loosen condition",
        "confidence": 0.7,
        "summary_zh": "x",
        "summary_en": "x",
    }
    norm = _normalize_llm_interpretation(
        raw, source_text="L1 应该放宽 SW1", system_id="thrust-reverser",
    )
    for key in (
        "affected_outputs",
        "recommended_work_order_zh",
        "recommended_work_order_en",
    ):
        assert key in norm, (
            f"LLM normalizer missing {key!r}: keys={list(norm.keys())}"
        )


def test_llm_normalizer_affected_outputs_is_text_corroborated_only() -> None:
    """Codex R1 P59-02-A fix: affected_outputs means "directly named
    cmd in the source text", and that contract must be identical
    across rules and LLM paths. The LLM normalizer therefore IGNORES
    raw_dict['affected_outputs'] and re-derives from source_text via
    _detect_affected_outputs. This avoids the rules-vs-LLM specificity
    drift that R1 flagged (rules empty, LLM claims tls_115vac_cmd →
    work-order scope changes from L1 to tls_115vac_cmd, false precision).

    If/when we want LLM-inferred outputs that the user did NOT name,
    they should land in a separate `inferred_outputs` field, not
    overload `affected_outputs`."""
    # (a) LLM correctly names tls_115vac_cmd AND text mentions it →
    #     keep (corroborated).
    raw_text_match = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "affected_outputs": ["tls_115vac_cmd"],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.7,
    }
    norm_a = _normalize_llm_interpretation(
        raw_text_match,
        source_text="tls_115vac_cmd 时序要改",
        system_id="thrust-reverser",
    )
    assert "tls_115vac_cmd" in norm_a["affected_outputs"]

    # (b) Rule scan backfills when LLM omits — text says
    #     "etrac_540vdc_cmd" but LLM didn't surface it.
    raw_omitted = {
        "affected_gates": ["L2"],
        "target_signals": [],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.5,
    }
    norm_b = _normalize_llm_interpretation(
        raw_omitted,
        source_text="把 etrac_540vdc_cmd 推迟 100ms",
        system_id="thrust-reverser",
    )
    assert "etrac_540vdc_cmd" in norm_b["affected_outputs"]

    # (c) Chinese-paraphrase scenario (R1 §F gap): LLM-correctly-maps
    #     "TLS 解锁电路" → "tls_115vac_cmd", but source text doesn't
    #     literally name the cmd. Per the corroboration contract, the
    #     LLM-only mapping MUST NOT surface in affected_outputs.
    raw_paraphrase = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "affected_outputs": ["tls_115vac_cmd"],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.6,
    }
    norm_c = _normalize_llm_interpretation(
        raw_paraphrase,
        source_text="TLS 解锁电路应该提前",
        system_id="thrust-reverser",
    )
    assert norm_c["affected_outputs"] == [], (
        "LLM-claimed output without source-text corroboration must "
        "NOT survive normalization. Got "
        f"{norm_c['affected_outputs']!r}. Per Codex R1 P59-02-A, this "
        "would be false precision and would silently change work-"
        "order scope from a gate to an LLM-guessed cmd."
    )

    # (d) Hallucinated cmd not in vocab — already excluded since rule
    #     scan only matches canonical names.
    raw_hallucinated = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "affected_outputs": ["fake_output_cmd"],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.6,
    }
    norm_d = _normalize_llm_interpretation(
        raw_hallucinated,
        source_text="some unrelated text",
        system_id="thrust-reverser",
    )
    assert "fake_output_cmd" not in norm_d["affected_outputs"]


def test_llm_normalizer_drops_uncorroborated_cmd_in_summary() -> None:
    """Codex R2 P59-02-A follow-up: the structured affected_outputs
    fix is not enough — the LLM-supplied summary_zh / summary_en can
    still surface an un-corroborated canonical cmd via its own text.
    Reproducer: source_text = "TLS 解锁电路应该提前", LLM emits
    affected_outputs=["tls_115vac_cmd"] and a summary mentioning
    tls_115vac_cmd. The normalizer must regenerate the summary from
    canonical fields (which now exclude the un-corroborated cmd) so
    the persisted/displayed summary does not carry false precision.
    """
    raw = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "affected_outputs": ["tls_115vac_cmd"],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.6,
        "summary_zh": "系统理解：你想修改 tls_115vac_cmd。",
        "summary_en": "System reading: modify tls_115vac_cmd.",
    }
    norm = _normalize_llm_interpretation(
        raw,
        source_text="TLS 解锁电路应该提前",
        system_id="thrust-reverser",
    )
    # Structured field is empty (corroboration check).
    assert norm["affected_outputs"] == []
    # And the summary text MUST NOT carry tls_115vac_cmd because the
    # output drift triggers regeneration via the canonical template.
    assert "tls_115vac_cmd" not in norm["summary_zh"], (
        f"summary_zh leaks un-corroborated cmd: {norm['summary_zh']!r}. "
        f"Codex R2 P59-02-A follow-up: regenerate summary on output "
        f"drift, not just on gate/signal/kind drift."
    )
    assert "tls_115vac_cmd" not in norm["summary_en"], (
        f"summary_en leaks un-corroborated cmd: {norm['summary_en']!r}"
    )
    # Sanity: the regenerated summary should still mention L1 (the
    # corroborated gate) so it's not vacuous.
    assert "L1" in norm["summary_zh"] or "L1" in norm["summary_en"]


def test_llm_normalizer_keeps_summary_when_all_fields_corroborate() -> None:
    """Inverse of the above: if every field (gates, signals, outputs,
    kind) matches what canonicalization produced, keep the LLM's
    summary text unchanged (it is typically richer than the rules
    template, per the existing round-8 P2 contract)."""
    raw = {
        "affected_gates": ["L1"],
        "target_signals": [],
        # Empty list — matches what the corroboration check produces
        # for source_text without any cmd mention.
        "affected_outputs": [],
        "change_kind": "loosen_condition",
        "change_kind_zh": "放宽判据",
        "change_kind_en": "loosen condition",
        "confidence": 0.8,
        "summary_zh": "原汁原味的 LLM 摘要。",
        "summary_en": "Original LLM summary.",
    }
    norm = _normalize_llm_interpretation(
        raw,
        source_text="L1 应该放宽",
        system_id="thrust-reverser",
    )
    assert norm["summary_zh"] == "原汁原味的 LLM 摘要。"
    assert norm["summary_en"] == "Original LLM summary."


def test_llm_normalizer_preserves_canonical_vocab_order() -> None:
    """Codex R1 P59-02-LOW: LLM may emit outputs in arbitrary order
    (e.g. ['pls_power_cmd', 'eec_deploy_cmd']). The normalized list
    must still walk canonical vocab order so the work-order draft
    reads in circuit-visual order. With the corroboration-only
    contract (R1 P59-02-A fix), this is automatic since the rule scan
    iterates canonical vocab — but lock it in with a test so a future
    refactor doesn't accidentally re-introduce LLM-order leakage."""
    raw_reversed = {
        "affected_gates": ["L3"],
        "target_signals": [],
        # LLM emits reversed canonical order intentionally.
        "affected_outputs": ["pls_power_cmd", "eec_deploy_cmd"],
        "change_kind": "modify_condition",
        "change_kind_zh": "修改判据",
        "change_kind_en": "modify condition",
        "confidence": 0.6,
    }
    norm = _normalize_llm_interpretation(
        raw_reversed,
        source_text="eec_deploy_cmd 和 pls_power_cmd 都需要 review",
        system_id="thrust-reverser",
    )
    # _output_cmd_names_for declares eec_deploy_cmd before
    # pls_power_cmd in L3's tuple — that order must win.
    assert norm["affected_outputs"] == [
        "eec_deploy_cmd", "pls_power_cmd",
    ], (
        f"output order should follow canonical vocab, got "
        f"{norm['affected_outputs']!r}"
    )


# ── 8. End-to-end via /api/workbench/interpret-suggestion ────


def test_interpret_endpoint_surfaces_new_fields() -> None:
    """The HTTP endpoint must include the new fields in its JSON
    response so the frontend (P59-03) doesn't have to reach into the
    Python module directly."""
    import http.client
    import json
    import threading
    from http.server import ThreadingHTTPServer

    from well_harness.demo_server import DemoRequestHandler

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        payload = json.dumps({
            "text": "L3 的 tra_deg 阈值要改成 -10°",
            "system_id": "thrust-reverser",
        }).encode("utf-8")
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5,
        )
        connection.request(
            "POST", "/api/workbench/interpret-suggestion",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body_bytes = response.read()
        status = response.status
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
    assert status == 200, f"endpoint returned {status}"
    parsed = json.loads(body_bytes.decode("utf-8"))
    assert "affected_outputs" in parsed
    assert isinstance(parsed["affected_outputs"], list)
    assert "recommended_work_order_zh" in parsed
    assert "recommended_work_order_en" in parsed
    # Smoke: tra_deg + L3 should both appear in the work order
    # (the user's primary example).
    wo = parsed["recommended_work_order_zh"]
    assert "tra_deg" in wo, f"endpoint work order missing tra_deg: {wo}"
    assert "L3" in wo, f"endpoint work order missing L3: {wo}"
