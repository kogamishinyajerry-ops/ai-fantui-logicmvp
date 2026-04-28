"""P57-04 — C919 E-TRAS state-coverage fixture sweep.

Six new fixtures exercise distinct paths through the §6 state machine
(S0..S10 + SF) and through the four most operationally-significant
fault classes from `_C919_FAULT_WHITELIST`. Together with the two
existing fixtures (c919_nominal_deploy → S5/S6, c919_tr_inhibited
→ SF), the timelines/ directory now covers:

    Nominal paths
      • S0→...→S5_DEPLOYED_IDLE_REVERSE  (existing nominal)
      • S0→...→S5_DEPLOYED_IDLE_REVERSE held (new: quick_deploy)
      • S0→...→S6_MAX_REVERSE             (new: max_reverse)
      • S0→S6→...→S10_STOWED_LOCKED_POWER_OFF (new: decel_to_stow)

    Fault paths
      • SF via tr_inhibited                (existing tr_inhibited)
      • SF via etras_over_temp_fault       (new: etras_over_temp)
      • Deploy stuck at S3 — unlock_confirmed dead via tls:sensor_fail
                                           (new: lock_disagreement)
      • Deploy stuck at S0 — selected_mlg_wow conservative FALSE
                                           (new: lgcu_invalid_blocks_deploy)
      • Wow filter underflow — lgcu1:disagree forces conservative FALSE
                                           (new: wow_filter_underflow)
      • Stow stuck at S7 — n1k_pct above max_n1k_stow_limit_pct
                                           (new: n1k_overrun)

The sweep is the foundation for P57-04's downstream visualization /
docs work (state-coverage matrix in the workstation page) and gives
future executor refactors a regression net per state path.

Each fixture is exercised end-to-end via TimelinePlayer +
C919ETRASExecutor. Tests assert (a) all in-fixture assert_condition
events pass, (b) the final state-machine state matches the fixture
intent, and (c) for fault fixtures the relevant downstream gate
stayed dormant.

All fault `target` values are sourced from `_C919_FAULT_WHITELIST`
in the executor — fake keys would be silently dropped per
`_build_fault_map` validation (P57-02 R1 H3 lesson).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from well_harness.timeline_engine import TimelinePlayer, parse_timeline
from well_harness.timeline_engine.executors.c919_etras import (
    C919ETRASExecutor,
    _C919_FAULT_WHITELIST,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "src" / "well_harness" / "timelines"


# ── Fixture catalog ──
# Each entry: (filename, expected_final_state, must_pass_assertions)

P57_04_FIXTURES = [
    "c919_max_reverse.json",
    "c919_decel_to_stow.json",
    "c919_quick_deploy.json",
    "c919_etras_over_temp.json",
    "c919_lock_disagreement.json",
    "c919_lgcu_invalid_blocks_deploy.json",
    "c919_wow_filter_underflow.json",
    "c919_n1k_overrun.json",
]


def _load_and_run(filename: str):
    path = FIXTURES_DIR / filename
    timeline = parse_timeline(json.loads(path.read_text("utf-8")))
    return TimelinePlayer(timeline, C919ETRASExecutor()).run()


# ── 1. All fixtures parse + execute without raising ──


@pytest.mark.parametrize("filename", P57_04_FIXTURES)
def test_fixture_parses_and_runs(filename: str) -> None:
    """Every P57-04 fixture must parse and execute end-to-end without
    raising. A schema/validator break here means the fixture is dead
    weight."""
    trace = _load_and_run(filename)
    assert trace is not None
    assert len(trace.frames) > 0, f"{filename}: no frames produced"


# ── 2. All in-fixture assertions pass ──


@pytest.mark.parametrize("filename", P57_04_FIXTURES)
def test_fixture_assertions_all_pass(filename: str) -> None:
    """Each fixture's assert_condition events must pass when run
    against the C919 executor — fixtures that lie about expected
    behavior are worse than no fixture."""
    trace = _load_and_run(filename)
    failures = [a for a in trace.assertions if not a.passed]
    assert not failures, (
        f"{filename}: {len(failures)} assertion(s) failed: "
        + ", ".join(f"{a.target}@{a.at_s}s expected={a.expected!r} got={a.observed!r}" for a in failures)
    )


# ── 3. Per-fixture state-path verification ──


def test_max_reverse_traverses_s6() -> None:
    """S6_MAX_REVERSE is a 1-tick transient: once TRA ≤ -25°, both
    microswitches go FALSE (TRA < -9.8°), and the next tick fires
    S6→S7. The fixture's contract is 'S6 was visited', not 'S6 is the
    terminal state'."""
    trace = _load_and_run("c919_max_reverse.json")
    states_seen = {f.outputs.get("state") for f in trace.frames}
    assert "S6_MAX_REVERSE" in states_seen, (
        f"c919_max_reverse must traverse S6, states seen: {sorted(states_seen)}"
    )


def test_decel_to_stow_reaches_s10() -> None:
    trace = _load_and_run("c919_decel_to_stow.json")
    final = trace.frames[-1].outputs.get("state")
    # Full cycle: must traverse S6 then come back to S10.
    states_seen = {f.outputs.get("state") for f in trace.frames}
    assert "S6_MAX_REVERSE" in states_seen, (
        f"decel_to_stow must traverse S6, states seen: {sorted(states_seen)}"
    )
    assert final == "S10_STOWED_LOCKED_POWER_OFF", (
        f"decel_to_stow must end in S10, got {final!r}"
    )


def test_quick_deploy_holds_at_s5() -> None:
    trace = _load_and_run("c919_quick_deploy.json")
    final = trace.frames[-1].outputs.get("state")
    assert final == "S5_DEPLOYED_IDLE_REVERSE", (
        f"quick_deploy must hold at S5, got {final!r}"
    )


def test_etras_over_temp_preempts_to_sf() -> None:
    trace = _load_and_run("c919_etras_over_temp.json")
    final = trace.frames[-1].outputs.get("state")
    assert final == "SF_ABORT_OR_FAULT", (
        f"etras_over_temp must preempt to SF, got {final!r}"
    )


def test_lock_disagreement_blocks_deploy_chain() -> None:
    """tls:sensor_fail freezes unlock_confirmed=False. fadec_deploy_command
    requires unlock_confirmed → never fires → state machine never reaches
    S4_DEPLOYING."""
    trace = _load_and_run("c919_lock_disagreement.json")
    states_seen = {f.outputs.get("state") for f in trace.frames}
    assert "S4_DEPLOYING" not in states_seen, (
        f"lock_disagreement must NOT reach S4 (deploy is blocked), "
        f"states seen: {sorted(states_seen)}"
    )
    # fadec_deploy_command never goes active.
    assert "ln_fadec_deploy_command" not in trace.outcome.logic_first_active_t_s


def test_lgcu_invalid_blocks_deploy_at_s0() -> None:
    """lgcu_both:invalid forces selected_mlg_wow conservative FALSE.
    S0→S1 transition requires selected_mlg_wow → never fires → state
    machine stays at S0_AIR_STOWED_LOCKED for the entire run."""
    trace = _load_and_run("c919_lgcu_invalid_blocks_deploy.json")
    states_seen = {f.outputs.get("state") for f in trace.frames}
    assert states_seen == {"S0_AIR_STOWED_LOCKED"}, (
        f"lgcu_invalid must hold at S0, states seen: {sorted(states_seen)}"
    )


def test_wow_filter_underflow_blocks_deploy() -> None:
    """lgcu1:disagree → LGCU1 reports opposite of LGCU2. Both still
    valid → conservative AND → selected_mlg_wow=FALSE. Deploy chain
    blocked at S0."""
    trace = _load_and_run("c919_wow_filter_underflow.json")
    states_seen = {f.outputs.get("state") for f in trace.frames}
    # Filter must hold at S0 even though LGCU2 alone reports WOW=True.
    assert states_seen == {"S0_AIR_STOWED_LOCKED"}, (
        f"wow_filter_underflow must hold at S0, states seen: {sorted(states_seen)}"
    )


def test_n1k_overrun_blocks_stow_at_s7() -> None:
    """n1k_pct above max_n1k_stow_limit_pct prevents fadec_stow_command
    from firing. State machine reaches S7_DECEL_WAIT_STOW after the
    pilot returns TRA, but cannot transition to S8_STOWING."""
    trace = _load_and_run("c919_n1k_overrun.json")
    states_seen = {f.outputs.get("state") for f in trace.frames}
    final = trace.frames[-1].outputs.get("state")
    assert "S7_DECEL_WAIT_STOW" in states_seen, (
        f"n1k_overrun must traverse S7, states seen: {sorted(states_seen)}"
    )
    assert final == "S7_DECEL_WAIT_STOW", (
        f"n1k_overrun must hold at S7 (stow blocked), got {final!r}"
    )
    # fadec_stow_command never fires.
    assert "ln_fadec_stow_command" not in trace.outcome.logic_first_active_t_s


# ── 4. Fault-key whitelist hygiene (P57-02 R1 H3 carry-forward) ──


@pytest.mark.parametrize(
    "filename",
    [
        "c919_etras_over_temp.json",
        "c919_lock_disagreement.json",
        "c919_lgcu_invalid_blocks_deploy.json",
        "c919_wow_filter_underflow.json",
        "c919_n1k_overrun.json",
    ],
)
def test_fault_targets_are_whitelisted(filename: str) -> None:
    """Every inject_fault target in a fault fixture must parse to a
    `(node_id, fault_type)` pair present in `_C919_FAULT_WHITELIST`.
    Fake fault keys are silently dropped by `_build_fault_map`, so a
    typo would make the fixture appear nominal instead of failing
    loudly. (P57-02 R1 H3 carry-forward.)"""
    path = FIXTURES_DIR / filename
    spec = json.loads(path.read_text("utf-8"))
    inject_targets = [
        ev["target"]
        for ev in spec.get("events", [])
        if ev.get("kind") == "inject_fault"
    ]
    # n1k_overrun is value-driven (no fault), so it may have zero injects.
    if filename == "c919_n1k_overrun.json":
        return
    assert inject_targets, (
        f"{filename}: fault fixture must have at least one inject_fault event"
    )
    for target in inject_targets:
        if ":" not in target:
            pytest.fail(
                f"{filename}: fault target {target!r} missing ':' "
                f"(format must be 'node:fault_type')"
            )
        node_id, fault_type = target.split(":", 1)
        assert (node_id, fault_type) in _C919_FAULT_WHITELIST, (
            f"{filename}: fault target {target!r} not in "
            f"_C919_FAULT_WHITELIST. Fake keys are silently dropped — "
            f"the fixture would run as nominal."
        )


# ── 5. All fixtures share the c919-etras system tag ──


@pytest.mark.parametrize("filename", P57_04_FIXTURES)
def test_fixture_system_tag(filename: str) -> None:
    """Every P57-04 fixture must declare `system: c919-etras` so the
    workbench preset dropdown filters them into the right group and
    the executor selection is unambiguous."""
    path = FIXTURES_DIR / filename
    spec = json.loads(path.read_text("utf-8"))
    assert spec.get("system") == "c919-etras", (
        f"{filename}: system tag must be 'c919-etras', got {spec.get('system')!r}"
    )


# ── 6. Workbench preset dropdown wiring ──


TIMELINE_SIM_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"


PRESET_KEY_TO_FIXTURE = {
    "c919_max_reverse": "c919_max_reverse.json",
    "c919_decel_to_stow": "c919_decel_to_stow.json",
    "c919_quick_deploy": "c919_quick_deploy.json",
    "c919_etras_over_temp": "c919_etras_over_temp.json",
    "c919_lock_disagreement": "c919_lock_disagreement.json",
    "c919_lgcu_invalid_blocks_deploy": "c919_lgcu_invalid_blocks_deploy.json",
    "c919_wow_filter_underflow": "c919_wow_filter_underflow.json",
    "c919_n1k_overrun": "c919_n1k_overrun.json",
}


@pytest.mark.parametrize("preset_key", sorted(PRESET_KEY_TO_FIXTURE.keys()))
def test_preset_in_timeline_sim_html(preset_key: str) -> None:
    """Each fixture must be inlined as a built-in preset in
    timeline-sim.html so the workbench dropdown can offer it without
    a server round-trip. (timeline-sim.html ships PRESETS as inline
    JS — see existing c919_nominal / c919_tr_inhibited.) Without this
    wiring, the new fixtures only run from disk via tests but are
    invisible from the UI."""
    body = TIMELINE_SIM_HTML.read_text(encoding="utf-8")
    # Preset object key + a label entry in BUILTIN_LABELS.
    has_preset = re.search(rf'\b{re.escape(preset_key)}:\s*\{{', body)
    has_label = re.search(rf'\b{re.escape(preset_key)}:\s*"[^"]+"\s*,', body)
    assert has_preset is not None, (
        f"preset {preset_key!r} not found in PRESETS in timeline-sim.html"
    )
    assert has_label is not None, (
        f"preset {preset_key!r} missing a BUILTIN_LABELS entry — "
        f"the dropdown would show the raw key instead of a label"
    )


def _extract_preset_block(body: str, preset_key: str) -> str | None:
    """Pull the `<key>: { ... }` substring for a single PRESETS entry.
    Returns None if not found. Brace-counts to handle nested objects
    (the c919_decel_to_stow preset has a nested `locks` object)."""
    start_match = re.search(rf'\b{re.escape(preset_key)}:\s*\{{', body)
    if not start_match:
        return None
    open_idx = start_match.end() - 1  # position of the opening brace
    depth = 0
    for i in range(open_idx, len(body)):
        ch = body[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return body[start_match.start():i + 1]
    return None


def _js_object_literal_to_json(src: str) -> str:
    """Convert a JS object-literal substring to JSON text.

    Handles the project's PRESETS subset:
      - bare identifier keys (key:)             → "key":
      - true / false / null                     → kept as-is
      - single-quote string literals            → double-quoted
      - trailing commas before } or ]           → stripped
      - escaped chars inside strings            → preserved

    Does NOT handle: function values, comments, template literals,
    spread operator. The PRESETS block uses none of these — verified
    on the current source. If the editor convention drifts to use
    them, this converter must be tightened.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    in_string = False
    quote_char = ""
    while i < n:
        ch = src[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(src[i + 1])
                i += 2
                continue
            if ch == quote_char:
                in_string = False
                # Normalize to double-quote: rewrite the closing quote.
                if quote_char == "'":
                    out[-1] = '"'
            i += 1
            continue

        if ch in ('"', "'"):
            in_string = True
            quote_char = ch
            out.append('"' if ch == "'" else ch)
            i += 1
            continue

        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            ident = src[i:j]
            # Skip whitespace to peek at next non-space char.
            k = j
            while k < n and src[k].isspace():
                k += 1
            is_key = k < n and src[k] == ":"
            if ident in ("true", "false", "null"):
                out.append(ident)
            elif is_key:
                out.append(f'"{ident}"')
            else:
                # Bare identifier as a value is invalid JS in a literal context;
                # fall through verbatim so json.loads surfaces it.
                out.append(ident)
            i = j
            continue

        out.append(ch)
        i += 1

    result = "".join(out)
    # Strip trailing commas before } or ].
    result = re.sub(r",(\s*[}\]])", r"\1", result)
    return result


def _extract_preset_value(body: str, preset_key: str) -> str | None:
    """Pull the `{ ... }` value substring for a single PRESETS entry
    (i.e., everything to the right of `<key>:`)."""
    block = _extract_preset_block(body, preset_key)
    if block is None:
        return None
    # block looks like `<key>: { ... }`. Find the first `{`.
    brace_idx = block.find("{")
    return block[brace_idx:] if brace_idx != -1 else None


def _strip_cosmetic(obj):
    """Recursively drop cosmetic fields (description, note) so structural
    comparison ignores free-text drift but catches data drift."""
    if isinstance(obj, dict):
        return {
            k: _strip_cosmetic(v)
            for k, v in obj.items()
            if k not in ("description", "note")
        }
    if isinstance(obj, list):
        return [_strip_cosmetic(v) for v in obj]
    return obj


@pytest.mark.parametrize("preset_key", sorted(PRESET_KEY_TO_FIXTURE.keys()))
def test_preset_block_matches_disk_fixture_shape(preset_key: str) -> None:
    """Strict structural parity: the inline PRESETS object in
    timeline-sim.html must match the disk JSON fixture for the same
    key, after stripping cosmetic free-text fields (description, note).

    The full events array, initial_inputs object, and top-level
    title/system/step_s/duration_s are all deep-compared. Drift in
    target/value/kind/order/initial_inputs payload will fail this
    test (the R2 fix for Codex's structural-parity finding — the
    earlier shallow count-only check let those slip).

    The PRESETS value is JS-object-literal syntax (bare keys, bare
    booleans, possibly trailing commas). _js_object_literal_to_json
    converts the project's subset to JSON; the conversion is
    state-machine-based (string-aware) so colons inside string values
    don't get mistaken for key delimiters.
    """
    body = TIMELINE_SIM_HTML.read_text(encoding="utf-8")
    js_value_src = _extract_preset_value(body, preset_key)
    assert js_value_src is not None, f"PRESETS[{preset_key!r}] not found"

    json_src = _js_object_literal_to_json(js_value_src)
    try:
        js_obj = json.loads(json_src)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"{preset_key}: JS-to-JSON conversion produced invalid JSON: "
            f"{e}\n\nConverted text:\n{json_src[:500]}"
        )

    fixture_path = FIXTURES_DIR / PRESET_KEY_TO_FIXTURE[preset_key]
    disk_obj = json.loads(fixture_path.read_text("utf-8"))

    js_clean = _strip_cosmetic(js_obj)
    disk_clean = _strip_cosmetic(disk_obj)

    # Compare top-level keys we care about (skip anything not in the
    # disk fixture's vocabulary — e.g., a future PRESETS-only field).
    structural_keys = ("title", "system", "step_s", "duration_s",
                       "initial_inputs", "events")
    for key in structural_keys:
        assert key in js_clean, f"{preset_key}: PRESETS missing {key!r}"
        assert key in disk_clean, f"{preset_key}: disk fixture missing {key!r}"
        assert js_clean[key] == disk_clean[key], (
            f"{preset_key}: structural drift on {key!r}.\n"
            f"  PRESETS: {js_clean[key]!r}\n"
            f"  disk:    {disk_clean[key]!r}"
        )


def test_state_in_c919_assertion_catalog() -> None:
    """The c919-etras assertion catalog must include 'state' so the
    SF preempt fixture (and any future state-machine assertions)
    populate the visual editor's dropdown without forcing the user
    into '(custom...)' mode."""
    body = TIMELINE_SIM_HTML.read_text(encoding="utf-8")
    # Simple containment check — the catalog block ends at the closing
    # brace of c919-etras's assertions list.
    catalog_match = re.search(
        r'"c919-etras":\s*\{[\s\S]*?assertions:\s*\[([^\]]*)\]',
        body,
    )
    assert catalog_match is not None, "c919-etras assertions catalog not found"
    assertions_block = catalog_match.group(1)
    assert '"state"' in assertions_block, (
        "'state' missing from c919-etras assertions catalog. "
        "Loading c919_etras_over_temp fixture would force the user "
        "into '(custom...)' mode for the SF assertion."
    )


# Register `re` import (kept here so the module-level import order
# matches the existing `import re` if a future linter rearranges).
