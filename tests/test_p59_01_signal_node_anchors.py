"""P59-01 — every visible logic node in fantui_circuit.html carries a
machine-readable annotation anchor (data-signal-id / data-summary-id),
not just the four L1..L4 logic gates.

Background: P44-01 added data-gate-id to the four AND gates so the
workbench highlight chain (workbench.js highlightSuggestionGates) could
glow them on demand. But the user feedback (2026-04-29) called out that
this only covers the middle column — when the user says "TRA's interval
threshold needs to change", the actual TRA input node in the leftmost
column should also be highlightable. P59-01 patches fantui_circuit.html
so every input row, every output box, and the two summary aggregators
carry data-signal-id / data-summary-id anchors that downstream consumers
(workbench.js in P59-03, the suggestion interpreter in P59-02) can use.

This phase is anchor-only — it does NOT change the highlight JS or the
interpretation engine. Those land in P59-02 / P59-03. The contract here:

- _SIGNALS_BY_SYSTEM["thrust-reverser"] declares 12 input signals; every
  one must appear as data-signal-id on at least one element in
  fantui_circuit.html.
- _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"] declares the canonical
  output command names (tls_115vac_cmd, etrac_540vdc_cmd, …); every one
  that looks like an output cmd must also be present as data-signal-id.
- Reverse direction: every data-signal-id in the SVG must resolve to
  an entry in either dict — no orphan IDs.
- Every input/output rect carries a matching <text> with the same
  data-signal-id (so highlight applies to both the box and its label).
- data-context-gate must be one of L1..L4 on every signal anchor (so
  the engine can collapse "L3's TRA threshold" into the L3 instance,
  not the L4 instance).
- Existing data-gate-id="L1..L4" anchors are preserved verbatim — the
  workbench highlight chain (P44-01..P44-02) must keep working
  unchanged.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FANTUI_SVG = (
    REPO_ROOT / "src" / "well_harness" / "static" / "fantui_circuit.html"
)


def _read() -> str:
    return FANTUI_SVG.read_text(encoding="utf-8")


def _signal_ids_in_svg(body: str) -> list[str]:
    return re.findall(r'data-signal-id="([^"]+)"', body)


def _summary_ids_in_svg(body: str) -> list[str]:
    return re.findall(r'data-summary-id="([^"]+)"', body)


def _signal_dict() -> tuple[str, ...]:
    """Late import so test collection doesn't require the full server
    module if a teardown hook breaks; matches the pattern in
    test_workbench_p44_02_suggestion_flow."""
    from well_harness.demo_server import _SIGNALS_BY_SYSTEM
    return _SIGNALS_BY_SYSTEM["thrust-reverser"]


def _gate_synonyms() -> dict[str, tuple[str, ...]]:
    from well_harness.demo_server import _GATE_SYNONYMS_BY_SYSTEM
    return _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"]


# Output command names — everything in the gate-synonym tuples that
# looks like a command name (snake_case ending in _cmd or matching
# known output identifiers). These are the right-column output box
# labels that should be addressable by name.
OUTPUT_CMD_NAMES = {
    "tls_115vac_cmd",
    "etrac_540vdc_cmd",
    "eec_deploy_cmd",
    "pls_power_cmd",
    "pdu_motor_cmd",
    "throttle_electronic_lock_release_cmd",
}

# Summary aggregators on the right of the diagram (rendered as the
# "DEPLOY ENABLE" + "THROTTLE UNLOCK" badges). These are not single
# signals so they get data-summary-id, not data-signal-id.
SUMMARY_IDS = {"deploy_enable", "throttle_unlock"}


# ── 1. Forward direction: dict → SVG ──────────────────────────


@pytest.mark.parametrize("signal_id", [
    "radio_altitude_ft", "SW1", "SW2", "reverser_inhibited",
    "reverser_not_deployed_eec", "engine_running", "aircraft_on_ground",
    "eec_enable", "tls_unlocked_ls", "n1k", "tra_deg",
    "deploy_90_percent_vdt",
])
def test_every_input_signal_has_at_least_one_svg_anchor(signal_id: str) -> None:
    """Every input signal declared in _SIGNALS_BY_SYSTEM must appear at
    least once as data-signal-id in fantui_circuit.html. Otherwise the
    suggestion interpreter could resolve a user phrase to a signal name
    that the highlight layer has no way to point at."""
    body = _read()
    signal_ids = _signal_ids_in_svg(body)
    assert signal_id in signal_ids, (
        f"signal {signal_id!r} is in _SIGNALS_BY_SYSTEM['thrust-reverser'] "
        f"but no element in fantui_circuit.html carries "
        f"data-signal-id={signal_id!r}. The highlight chain has no DOM "
        f"target to glow."
    )


def test_every_dict_signal_appears_at_least_once() -> None:
    """Aggregate sanity check that mirrors the parametrized test —
    catches dict additions that forgot to add an SVG anchor."""
    body = _read()
    svg_ids = set(_signal_ids_in_svg(body))
    missing = [s for s in _signal_dict() if s not in svg_ids]
    assert not missing, (
        f"signals declared in _SIGNALS_BY_SYSTEM but missing from SVG: "
        f"{missing}. Add data-signal-id to the matching input rect+text "
        f"or remove from the dict."
    )


@pytest.mark.parametrize("output_cmd", sorted(OUTPUT_CMD_NAMES))
def test_every_gate_output_cmd_has_svg_anchor(output_cmd: str) -> None:
    """Output command names (tls_115vac_cmd, etrac_540vdc_cmd, …) live in
    _GATE_SYNONYMS_BY_SYSTEM as gate synonyms. They must also be
    addressable directly so a work-order phrased as 'tls_115vac_cmd
    timing should change' can highlight the L1 output box, not just L1
    itself."""
    body = _read()
    signal_ids = _signal_ids_in_svg(body)
    assert output_cmd in signal_ids, (
        f"output command {output_cmd!r} appears in _GATE_SYNONYMS but no "
        f"element in fantui_circuit.html carries "
        f"data-signal-id={output_cmd!r}."
    )


def test_output_cmds_match_gate_synonyms() -> None:
    """Sanity check: every name in OUTPUT_CMD_NAMES is actually a
    synonym in _GATE_SYNONYMS_BY_SYSTEM — guards against test drift if
    the dict is renamed."""
    synonyms_flat = {
        s for entries in _gate_synonyms().values() for s in entries
    }
    missing = OUTPUT_CMD_NAMES - synonyms_flat
    assert not missing, (
        f"OUTPUT_CMD_NAMES references {missing} which are not in "
        f"_GATE_SYNONYMS_BY_SYSTEM. Update either the dict or this test."
    )


# ── 2. Reverse direction: SVG → dict (no orphans) ─────────────


def test_no_orphan_signal_ids_in_svg() -> None:
    """Every data-signal-id in the SVG must correspond to either an
    input signal in _SIGNALS_BY_SYSTEM or an output command name in
    _GATE_SYNONYMS_BY_SYSTEM. An orphan ID would mean the SVG drifted
    from the SSOT and the highlight chain would point at a name that
    nothing in the backend can produce."""
    body = _read()
    svg_ids = set(_signal_ids_in_svg(body))
    valid = set(_signal_dict()) | OUTPUT_CMD_NAMES
    orphans = svg_ids - valid
    assert not orphans, (
        f"data-signal-id values in SVG with no SSOT entry: {orphans}. "
        f"Either add to _SIGNALS_BY_SYSTEM (if input) or to "
        f"_GATE_SYNONYMS_BY_SYSTEM (if output), or remove from SVG."
    )


def test_summary_ids_match_known_aggregators() -> None:
    """data-summary-id is a fixed two-value vocabulary
    (deploy_enable, throttle_unlock). Anything else is a typo."""
    body = _read()
    svg_summaries = set(_summary_ids_in_svg(body))
    unexpected = svg_summaries - SUMMARY_IDS
    assert not unexpected, (
        f"unexpected data-summary-id values: {unexpected}. Known "
        f"aggregators: {SUMMARY_IDS}."
    )
    missing = SUMMARY_IDS - svg_summaries
    assert not missing, (
        f"missing data-summary-id values: {missing}. The DEPLOY ENABLE "
        f"and THROTTLE UNLOCK badges must both carry an anchor."
    )


# ── 3. Rect+text pairing — both must carry the anchor ──────────


def test_every_input_rect_has_matching_text_anchor() -> None:
    """Each input row is a <rect> + a primary <text> label. Both must
    carry the same data-signal-id so a highlight class on the rect or
    on the text individually still styles the visible region. Mismatch
    would cause partial highlights (only the rect glows but not the
    label, or vice versa)."""
    body = _read()
    rect_ids = re.findall(
        r'<rect[^>]*data-node-kind="signal-input"[^>]*'
        r'data-signal-id="([^"]+)"',
        body,
    )
    text_ids = re.findall(
        r'<text[^>]*data-node-kind="signal-input"[^>]*'
        r'data-signal-id="([^"]+)"',
        body,
    )
    rc, tc = Counter(rect_ids), Counter(text_ids)
    assert rc == tc, (
        f"signal-input rect/text anchor counts diverge.\n"
        f"  rect-only delta: {rc - tc}\n"
        f"  text-only delta: {tc - rc}\n"
        f"Every input rect must have at least one matching <text> "
        f"with the same data-signal-id (and vice versa)."
    )


def test_every_signal_input_anchor_has_context_gate() -> None:
    """data-context-gate is mandatory on signal-input anchors so the
    interpreter can resolve "L3's tra_deg threshold" → just the L3
    instance, not all four duplicates of tra_deg."""
    body = _read()
    inputs = re.findall(
        r'(<(?:rect|text)[^>]*data-node-kind="signal-input"[^>]*>)',
        body,
    )
    assert inputs, "no signal-input anchors found — schema regression"
    bad = [tag for tag in inputs if 'data-context-gate=' not in tag]
    assert not bad, (
        f"{len(bad)} signal-input anchor(s) missing data-context-gate. "
        f"First offender: {bad[0][:200]}"
    )


def test_context_gate_values_are_in_known_set() -> None:
    """Every data-context-gate must be one of L1, L2, L3, L4. A typo
    like 'l3' or 'L33' would silently exclude that node from the
    matching highlight."""
    body = _read()
    gates = set(re.findall(r'data-context-gate="([^"]+)"', body))
    valid = {"L1", "L2", "L3", "L4"}
    unexpected = gates - valid
    assert not unexpected, (
        f"unexpected data-context-gate values: {unexpected}. "
        f"Allowed set: {valid}."
    )


# ── 4. Carry-forward: P44-01 gate anchors must remain ─────────


@pytest.mark.parametrize("gate_id", ["L1", "L2", "L3", "L4"])
def test_p44_01_gate_anchors_preserved(gate_id: str) -> None:
    """P44-01 contract: L1..L4 each have data-gate-id on the AND-gate
    <use> AND on the L# label <text>. The P59-01 changes are additive
    and must not have stripped these."""
    body = _read()
    needle = f'data-gate-id="{gate_id}"'
    occurrences = body.count(needle)
    assert occurrences >= 2, (
        f"data-gate-id={gate_id!r} appears only {occurrences} times in "
        f"fantui_circuit.html — P44-01 contract requires ≥2 (one on the "
        f"AND <use>, one on the L# <text> label)."
    )


def test_total_gate_id_anchors_unchanged() -> None:
    """The P44-01 anchor count is exactly 8 (4 gates × 2 elements).
    P59-01 must not have added or dropped any gate anchors."""
    body = _read()
    count = len(re.findall(r'data-gate-id="L\d"', body))
    assert count == 8, (
        f"data-gate-id anchor count is {count}, expected 8 (4 gates × "
        f"2 elements). P44-01 contract drift."
    )


# ── 5. Duplicate-instance accounting ──────────────────────────


@pytest.mark.parametrize("signal_id,expected_occurrences", [
    # Signals that appear in more than one gate's input column.
    # Counts are unique-(signal_id, context_gate) pairs, NOT total
    # data-signal-id markers (each instance is rect+text = 2 markers).
    ("engine_running", 3),     # L2, L3, L4
    ("aircraft_on_ground", 3), # L2, L3, L4
    ("reverser_inhibited", 3), # L1, L2, L3
    ("tra_deg", 2),            # L3 (threshold check), L4 (window check)
])
def test_duplicate_signal_distinct_context_gates(
    signal_id: str, expected_occurrences: int,
) -> None:
    """Some signals (engine_running, aircraft_on_ground, …) appear in
    more than one gate's input column. Each occurrence must carry a
    DISTINCT data-context-gate so the interpreter can distinguish
    "engine_running on L3" from "engine_running on L4"."""
    body = _read()
    pairs = set(re.findall(
        rf'data-signal-id="{re.escape(signal_id)}"\s+'
        rf'data-context-gate="([^"]+)"',
        body,
    ))
    assert len(pairs) == expected_occurrences, (
        f"signal {signal_id!r} expected to appear in "
        f"{expected_occurrences} distinct context gates, found "
        f"{len(pairs)}: {sorted(pairs)}"
    )


# ── 6. Annotation-anchor parity with P44-01 convention ─────────


def test_signal_inputs_carry_annotation_anchor_attribute() -> None:
    """P44-01 introduced data-annotation-anchor as a typed marker for
    annotation-overlay consumers. P59-01 extends the convention: every
    signal-input element should also carry
    data-annotation-anchor="signal_input"."""
    body = _read()
    inputs = re.findall(
        r'(<(?:rect|text)[^>]*data-node-kind="signal-input"[^>]*>)',
        body,
    )
    bad = [t for t in inputs
           if 'data-annotation-anchor="signal_input"' not in t]
    assert not bad, (
        f"{len(bad)} signal-input element(s) missing "
        f"data-annotation-anchor='signal_input'. First offender: "
        f"{bad[0][:200]}"
    )


def test_signal_outputs_carry_annotation_anchor_attribute() -> None:
    """Mirror of the input-side check for outputs."""
    body = _read()
    outputs = re.findall(
        r'(<(?:rect|text)[^>]*data-node-kind="signal-output"[^>]*>)',
        body,
    )
    bad = [t for t in outputs
           if 'data-annotation-anchor="signal_output"' not in t]
    assert not bad, (
        f"{len(bad)} signal-output element(s) missing "
        f"data-annotation-anchor='signal_output'. First offender: "
        f"{bad[0][:200]}"
    )


def test_summary_nodes_carry_annotation_anchor_attribute() -> None:
    """Summary aggregators get data-annotation-anchor='summary_node'."""
    body = _read()
    summaries = re.findall(
        r'(<(?:rect|text)[^>]*data-node-kind="summary"[^>]*>)',
        body,
    )
    bad = [t for t in summaries
           if 'data-annotation-anchor="summary_node"' not in t]
    assert not bad, (
        f"{len(bad)} summary element(s) missing "
        f"data-annotation-anchor='summary_node'. First offender: "
        f"{bad[0][:200]}"
    )


# ── 7. Workbench fragment endpoint stays in lockstep ──────────


def test_circuit_fragment_endpoint_carries_signal_anchors() -> None:
    """P44-01 contract: /api/workbench/circuit-fragment serves the SVG
    block extracted from fantui_circuit.html so the workbench hero
    never drifts. Therefore the new data-signal-id anchors must surface
    in the fragment endpoint too — otherwise the workbench page would
    not have the new highlight targets."""
    import http.client
    import threading
    from http.server import ThreadingHTTPServer

    from well_harness.demo_server import DemoRequestHandler

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5,
        )
        connection.request(
            "GET", "/api/workbench/circuit-fragment?system=thrust-reverser",
        )
        response = connection.getresponse()
        body_bytes = response.read()
        assert response.status == 200, (
            f"fragment endpoint returned {response.status}"
        )
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
    fragment = body_bytes.decode("utf-8")
    # Spot-check: tra_deg (the user's example) must be in the fragment
    # so the workbench page can find it.
    assert 'data-signal-id="tra_deg"' in fragment, (
        "fragment endpoint does not surface data-signal-id='tra_deg'. "
        "The workbench page would have nothing for the highlight layer "
        "to point at when the user mentions TRA."
    )
    # And at least one summary anchor for completeness.
    assert 'data-summary-id="deploy_enable"' in fragment, (
        "fragment endpoint missing data-summary-id='deploy_enable'."
    )
