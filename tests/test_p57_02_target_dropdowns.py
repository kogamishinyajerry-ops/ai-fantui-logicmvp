"""P57-02 — system-aware target dropdowns + type-aware value inputs.

Builds on P57-01's visual event-table editor. Eliminates the
"target name typed wrong, find out 30 seconds later" footgun by:

  1. Replacing the free-text `target` cell with a system+kind-aware
     `<select>` populated from a catalog of valid input fields,
     fault ids, and assertion targets. A "(custom...)" option in the
     select flips the cell back to a free-text input for unknown
     targets so the user is not locked out.

  2. Rendering the `value` cell type-aware once the target is known:
     - bool target → checkbox
     - number target → number input
     - otherwise → text input

  3. Disabling the `duration_s` cell unless the kind uses it
     (ramp_input / inject_fault / start_deploy_sequence). The
     schema rejects duration_s on other kinds, so the editor should
     not invite it.

The catalogs (SYSTEM_CATALOGS) live in JS as plain constants and are
sourced from the executor whitelists / parse_c919_raw_inputs / the
fantui _PILOT_INPUT_KEYS so the dropdown lists match what the
backend will actually accept.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMELINE_SIM = (
    REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"
)


def _read() -> str:
    return TIMELINE_SIM.read_text(encoding="utf-8")


# ─── 1. SYSTEM_CATALOGS exists with both systems ───


def test_system_catalogs_constant_exists() -> None:
    """A JS constant named SYSTEM_CATALOGS must declare per-system
    catalog data (inputs, faults, assertions). Without a single
    source of truth the dropdown options scatter across the file."""
    body = _read()
    catalog = re.search(r"\bconst\s+SYSTEM_CATALOGS\s*=", body)
    assert catalog is not None, (
        "SYSTEM_CATALOGS const not declared in JS. P57-02 needs a "
        "single per-system catalog for target dropdown population."
    )


@pytest.mark.parametrize("system_id", ["fantui", "c919-etras"])
def test_system_catalogs_covers_both_systems(system_id: str) -> None:
    """Both fantui and c919-etras must appear as keys in SYSTEM_CATALOGS.
    A missing system key would silently render an empty dropdown."""
    body = _read()
    # Match the catalog key literally — both quoted forms acceptable.
    found = re.search(
        rf'SYSTEM_CATALOGS\s*=\s*\{{[\s\S]*?["\']{re.escape(system_id)}["\']\s*:',
        body,
    )
    assert found is not None, (
        f"SYSTEM_CATALOGS does not declare a {system_id!r} entry. "
        f"Both fantui and c919-etras must be covered."
    )


@pytest.mark.parametrize(
    "system_id, expected_input",
    [
        # FANTUI inputs (subset — _PILOT_INPUT_KEYS in fantui executor).
        ("fantui", "radio_altitude_ft"),
        ("fantui", "tra_deg"),
        ("fantui", "engine_running"),
        # C919 inputs (subset — c919_tick_api.parse_c919_raw_inputs).
        ("c919-etras", "tra_deg"),
        ("c919-etras", "lgcu1_mlg_wow"),
        ("c919-etras", "n1k_pct"),
    ],
)
def test_system_catalog_inputs_include_executor_truth(
    system_id: str, expected_input: str,
) -> None:
    """Each system's catalog.inputs must include canonical fields
    accepted by the executor. Otherwise the dropdown lies about
    what the backend will accept."""
    body = _read()
    # The system block in SYSTEM_CATALOGS is a JS object. Look for
    # the system key, then within ~3000 chars the input field name.
    pattern = (
        rf'["\']{re.escape(system_id)}["\']\s*:'
        rf'[\s\S]{{0,3000}}["\']{re.escape(expected_input)}["\']'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        f"SYSTEM_CATALOGS[{system_id!r}].inputs does not include "
        f"{expected_input!r}. Executor accepts this field; the "
        f"catalog must too."
    )


@pytest.mark.parametrize(
    "system_id, expected_fault",
    [
        # FANTUI faults (subset — _FANTUI_FAULT_WHITELIST).
        ("fantui", "sw1:stuck_off"),
        ("fantui", "logic1:logic_stuck_false"),
        # C919 faults (subset — _C919_FAULT_WHITELIST).
        ("c919-etras", "tr_inhibited:stuck_on"),
        ("c919-etras", "etras_over_temp_fault:stuck_on"),
    ],
)
def test_system_catalog_faults_match_executor_whitelist(
    system_id: str, expected_fault: str,
) -> None:
    """Catalog faults must match the executor whitelist verbatim
    ('node:type' format) so inject_fault dropdown picks always pass
    backend validation."""
    body = _read()
    pattern = (
        rf'["\']{re.escape(system_id)}["\']\s*:'
        rf'[\s\S]{{0,3000}}["\']{re.escape(expected_fault)}["\']'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        f"SYSTEM_CATALOGS[{system_id!r}].faults does not include "
        f"{expected_fault!r}. Backend whitelist accepts it; the "
        f"dropdown must offer it."
    )


# ─── 2. Target option resolver wired to system + kind ───


def test_target_options_function_exists() -> None:
    """A function (e.g. getTargetOptions) must take system + kind
    and return the appropriate catalog slice (inputs / faults /
    assertions / free-form)."""
    body = _read()
    found = re.search(
        r"function\s+getTargetOptions\s*\(", body,
    )
    assert found is not None, (
        "getTargetOptions(system, kind) function not found. "
        "P57-02 needs a single resolver so the renderer asks one "
        "place for the dropdown options."
    )


def test_target_options_resolver_routes_kinds_correctly() -> None:
    """The resolver must branch on kind: set_input/ramp_input → inputs,
    inject_fault/clear_fault → faults, assert_condition → assertions.
    Verify each branch exists by checking for both the kind literal
    and the catalog property in close proximity."""
    body = _read()
    # Extract the function body for getTargetOptions.
    fn_match = re.search(
        r'function\s+getTargetOptions\s*\([^)]*\)\s*\{(.*?)\n\}',
        body, re.DOTALL,
    )
    assert fn_match is not None, "getTargetOptions function not found"
    fn_body = fn_match.group(1)
    expected_branches = [
        ("set_input", "inputs"),
        ("inject_fault", "faults"),
        ("assert_condition", "assertions"),
    ]
    for kind, prop in expected_branches:
        # Either kind literal and prop appear in same body, OR the
        # resolver delegates via a structure like cat[propMap[kind]].
        has_kind = re.search(rf'["\']({re.escape(kind)})["\']', fn_body)
        has_prop = re.search(rf'\b{re.escape(prop)}\b', fn_body)
        assert has_kind is not None, (
            f"getTargetOptions does not branch on kind {kind!r}."
        )
        assert has_prop is not None, (
            f"getTargetOptions does not reference catalog property "
            f"{prop!r} (used for kind {kind!r})."
        )


# ─── 3. Target cell renders as <select> with custom escape hatch ───


def test_event_row_target_uses_select_with_custom_option() -> None:
    """The target table cell must be a `<select>` for known
    system+kind combinations (so users pick instead of typing) AND
    must include a "(custom...)" option that flips the cell back to
    free-text input. Without the escape hatch unknown targets are
    locked out."""
    body = _read()
    # Look for a target select with a custom option marker — could be
    # value="__custom__" or a hardcoded option text "(custom...)".
    has_custom_opt = re.search(
        r'value="__custom__"|>\s*\(custom\.\.\.\)\s*<|data-target-custom',
        body,
    )
    assert has_custom_opt is not None, (
        "no target-cell custom-option marker found. The target select "
        "must offer a '(custom...)' escape so unknown fields can still "
        "be entered — otherwise users are locked out for new targets."
    )


# ─── 4. Value cell type adapts to known input type ───


def test_value_input_type_resolver_exists() -> None:
    """A function (e.g. getValueInputType) maps target → 'checkbox' /
    'number' / 'text' so the value cell renders the right control
    when the target type is in the catalog."""
    body = _read()
    found = re.search(
        r"function\s+getValueInputType\s*\(", body,
    )
    assert found is not None, (
        "getValueInputType(system, kind, target) function not found. "
        "P57-02 makes the value cell type-aware (checkbox for bool, "
        "number for number, text otherwise)."
    )


def test_value_resolver_handles_bool_and_number_branches() -> None:
    """The resolver must return 'checkbox' for bool targets and
    'number' for number targets. Otherwise the type-aware value
    promise is hollow."""
    body = _read()
    fn_match = re.search(
        r'function\s+getValueInputType\s*\([^)]*\)\s*\{(.*?)\n\}',
        body, re.DOTALL,
    )
    assert fn_match is not None, "getValueInputType function not found"
    fn_body = fn_match.group(1)
    assert re.search(r'["\']checkbox["\']', fn_body), (
        "getValueInputType has no 'checkbox' return — bool branch "
        "missing."
    )
    assert re.search(r'["\']number["\']', fn_body), (
        "getValueInputType has no 'number' return — number branch "
        "missing."
    )


# ─── 5. duration_s cell visibility tracks kind ───


def test_kind_uses_duration_set_exists_and_covers_three_kinds() -> None:
    """The set/array `KIND_USES_DURATION` must list exactly the three
    kinds where duration_s is meaningful: ramp_input, inject_fault,
    start_deploy_sequence. Other kinds reject duration_s in the
    schema; the editor must mirror that."""
    body = _read()
    has_const = re.search(
        r'\b(?:const|let)\s+KIND_USES_DURATION\s*=', body,
    )
    assert has_const is not None, (
        "KIND_USES_DURATION constant not declared. Without it, the "
        "duration_s cell either lies (always shown) or breaks "
        "(never enabled)."
    )
    # Find the constant body (Set or array literal).
    const_match = re.search(
        r'KIND_USES_DURATION\s*=\s*(?:new\s+Set\s*\(\s*)?\[(.*?)\]',
        body, re.DOTALL,
    )
    assert const_match is not None, (
        "KIND_USES_DURATION not declared as Set or array literal."
    )
    const_body = const_match.group(1)
    for kind in ("ramp_input", "inject_fault", "start_deploy_sequence"):
        assert kind in const_body, (
            f"KIND_USES_DURATION missing {kind!r}. The schema accepts "
            f"duration_s on this kind; the editor must enable it."
        )


def test_duration_cell_renders_disabled_for_irrelevant_kinds() -> None:
    """When kind ∉ KIND_USES_DURATION, the duration_s input must
    be visually disabled (HTML `disabled` attr or a CSS class) so
    the user does not type a value the schema will reject."""
    body = _read()
    # Find renderEventRow body.
    fn_match = re.search(
        r'function\s+renderEventRow\s*\(\s*ev\s*,\s*i\s*\)\s*\{(.*?)\n\}',
        body, re.DOTALL,
    )
    assert fn_match is not None, "renderEventRow function not found"
    fn_body = fn_match.group(1)
    # The duration_s input element rendering must reference either a
    # `disabled` attribute or a conditional CSS class tied to
    # KIND_USES_DURATION.
    pattern = (
        r'duration_s[^"]*"[^>]*disabled'
        r'|disabled[^>]{0,80}duration_s'
        r'|KIND_USES_DURATION[\s\S]{0,200}duration_s'
        r'|duration_s[\s\S]{0,200}KIND_USES_DURATION'
    )
    found = re.search(pattern, fn_body)
    assert found is not None, (
        "renderEventRow does not gate duration_s rendering on "
        "KIND_USES_DURATION (either a disabled attr or class hook). "
        "Users will type values the schema rejects (Codex-style trap)."
    )
