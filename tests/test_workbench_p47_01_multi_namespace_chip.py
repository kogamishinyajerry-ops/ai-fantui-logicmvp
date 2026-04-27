"""P47-01 — multi-namespace panel-version chip.

User direction (2026-04-27): the panel-version chip used to show only
the repo HEAD SHA, but `/workbench` actually surfaces three distinct
truth surfaces — the logic-circuit truth (controller/runner/models/
adapters), the requirements documents (markdown + rendered HTML), and
the simulation workbench (timeline-sim + sim-panel spec). Without a
per-namespace breakdown the engineer cannot tell whether (e.g.) the
requirements doc has drifted past the logic-circuit truth.

Locks down:
  - state-of-world payload carries `panel_namespaces[]` with three
    entries in fixed order: logic_truth / requirements /
    simulation_workbench
  - each entry exposes head_sha (7-char short), head_subject,
    head_committed_at (ISO-8601), files (list), label_zh/_en
  - workbench.html mounts a `#workbench-panel-namespaces` container
    so the JS render hook has a place to attach
  - workbench.js carries the `renderPanelNamespaces` function +
    invokes it from the existing chip installer
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from well_harness.demo_server import (
    _PANEL_NAMESPACES,
    _namespace_head_info,
    _panel_namespaces_payload,
    workbench_state_of_world_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── 1. Backend: namespace constant has the three contracted entries ──


def test_panel_namespaces_constant_has_three_entries():
    assert len(_PANEL_NAMESPACES) == 3


@pytest.mark.parametrize(
    "expected_namespace",
    ["logic_truth", "requirements", "simulation_workbench"],
)
def test_panel_namespaces_constant_includes_namespace(expected_namespace):
    namespaces = [ns["namespace"] for ns in _PANEL_NAMESPACES]
    assert expected_namespace in namespaces, (
        f"namespace {expected_namespace!r} missing from _PANEL_NAMESPACES "
        f"(got {namespaces!r})"
    )


def test_logic_truth_namespace_files_match_red_line():
    """The logic_truth namespace must cover exactly the truth-engine
    red-line modules — controller / models / runner / adapters/. If a
    future PR adds e.g. a real-time loop module to the truth boundary,
    update this list AND the namespace files in lockstep."""
    ns = next(n for n in _PANEL_NAMESPACES if n["namespace"] == "logic_truth")
    files = set(ns["files"])
    assert "src/well_harness/controller.py" in files
    assert "src/well_harness/models.py" in files
    assert "src/well_harness/runner.py" in files
    # adapters is a directory, not a single file — git log -- <dir>
    # walks the whole tree and is the right way to track it.
    assert "src/well_harness/adapters" in files


def test_requirements_namespace_files_match_doc_locations():
    ns = next(n for n in _PANEL_NAMESPACES if n["namespace"] == "requirements")
    files = set(ns["files"])
    assert "docs/thrust_reverser/requirements_supplement.md" in files
    assert "docs/c919_etras/requirements_v0_9.md" in files
    assert "src/well_harness/static/fantui_requirements.html" in files
    assert "src/well_harness/static/c919_requirements.html" in files


def test_simulation_workbench_namespace_files_match():
    ns = next(n for n in _PANEL_NAMESPACES if n["namespace"] == "simulation_workbench")
    files = set(ns["files"])
    assert "src/well_harness/static/timeline-sim.html" in files
    assert "docs/panels/sim_panel_requirements.md" in files


# ─── 2. Backend: per-namespace head info hits real git ────────────────


@pytest.mark.parametrize(
    "expected_namespace",
    ["logic_truth", "requirements", "simulation_workbench"],
)
def test_namespace_head_info_returns_short_sha_for_each_namespace(expected_namespace):
    ns = next(n for n in _PANEL_NAMESPACES if n["namespace"] == expected_namespace)
    info = _namespace_head_info(ns["files"])
    assert "head_sha" in info
    # The repo has a real git history with these files touched, so
    # `unknown` here means git failed or files were never committed.
    assert info["head_sha"] != "unknown", (
        f"namespace {expected_namespace!r} reports head_sha='unknown' — "
        f"either git is unavailable in the test environment OR the "
        f"file list points at paths that have never been committed"
    )
    assert re.match(r"^[0-9a-f]{6,12}$", info["head_sha"]), (
        f"head_sha {info['head_sha']!r} is not a valid short SHA"
    )
    assert info["head_subject"] not in ("", "—"), (
        f"namespace {expected_namespace!r} returned an empty subject"
    )


# ─── 3. Backend: state-of-world payload exposes the namespaces ────────


def test_state_of_world_payload_includes_panel_namespaces():
    payload = workbench_state_of_world_payload()
    assert "panel_namespaces" in payload
    assert isinstance(payload["panel_namespaces"], list)
    assert len(payload["panel_namespaces"]) == 3


def test_state_of_world_namespaces_in_fixed_order():
    """logic_truth must come first because it's the headline truth
    surface; requirements + simulation are subordinate."""
    payload = workbench_state_of_world_payload()
    namespaces = [ns["namespace"] for ns in payload["panel_namespaces"]]
    assert namespaces == ["logic_truth", "requirements", "simulation_workbench"]


def test_state_of_world_namespace_entries_have_full_shape():
    payload = workbench_state_of_world_payload()
    for entry in payload["panel_namespaces"]:
        for required in (
            "namespace",
            "label_zh",
            "label_en",
            "files",
            "head_sha",
            "head_subject",
            "head_committed_at",
            "head_source",
        ):
            assert required in entry, (
                f"namespace entry missing field {required!r}: {entry!r}"
            )


def test_state_of_world_top_level_truth_engine_sha_unchanged():
    """Backwards compat with E11-06 + P44-06: the top-level
    truth_engine_sha field is still the repo HEAD short SHA."""
    payload = workbench_state_of_world_payload()
    assert "truth_engine_sha" in payload
    assert payload["truth_engine_sha_source"] == "git rev-parse --short HEAD"


# ─── 4. HTML mounts the lineage container ─────────────────────────────


def test_workbench_html_mounts_panel_namespaces_container():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'id="workbench-panel-namespaces"' in html
    # Container should start hidden so it doesn't render an empty box
    # before the first fetch resolves.
    block = html.split('id="workbench-panel-namespaces"')[1].split(">", 1)[0]
    assert "hidden" in block, (
        "panel-namespaces container should start with the `hidden` "
        "attribute so we don't render an empty placeholder pre-fetch"
    )


def test_workbench_html_panel_namespaces_container_state_attribute():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'data-panel-namespaces-state="loading"' in html


# ─── 5. JS hook + render function exist ───────────────────────────────


def test_workbench_js_carries_render_panel_namespaces_function():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function renderPanelNamespaces" in js


def test_workbench_js_render_consumes_payload_field():
    """The render function must read from `panel_namespaces` (the
    contract field name), not e.g. `namespaces` or `panel_lineage`."""
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "body.panel_namespaces" in js


@pytest.mark.parametrize(
    "namespace_id",
    ["logic_truth", "requirements", "simulation_workbench"],
)
def test_workbench_js_does_not_hardcode_namespace_strings(namespace_id):
    """The render function must read namespace ids from the payload —
    not hardcode them. If a future PR adds a 4th namespace via the
    backend constant, the frontend should pick it up automatically.

    Smoke check: the namespace string should NOT appear as a literal
    in workbench.js. (CSS may still target specific namespaces by
    data-attribute, e.g. data-panel-namespace="logic_truth", which
    is fine — that's styling, not logic.)"""
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    # Allow it inside a comment line; check non-comment lines only.
    code_lines = [
        line
        for line in js.splitlines()
        if not line.lstrip().startswith("//")
    ]
    code_blob = "\n".join(code_lines)
    quoted_pattern = re.compile(r"""['"]""" + re.escape(namespace_id) + r"""['"]""")
    assert not quoted_pattern.search(code_blob), (
        f"namespace id {namespace_id!r} appears as a hardcoded string "
        f"in workbench.js — should come from the payload instead"
    )


# ─── 6. CSS carries the per-namespace row class ───────────────────────


def test_workbench_css_carries_panel_namespace_row_styles():
    css = WORKBENCH_CSS.read_text(encoding="utf-8")
    assert ".workbench-panel-namespaces" in css
    assert ".workbench-panel-namespace-row" in css


# ─── 7. Truth-engine red line — payload helper is read-only ───────────


def test_panel_namespaces_payload_is_read_only():
    """Calling _panel_namespaces_payload() must not mutate the
    _PANEL_NAMESPACES constant. If a future refactor accidentally
    converts the tuples to lists and mutates them, this test fires."""
    snapshot_namespaces = tuple(ns["namespace"] for ns in _PANEL_NAMESPACES)
    snapshot_files = tuple(tuple(ns["files"]) for ns in _PANEL_NAMESPACES)
    _ = _panel_namespaces_payload()
    after_namespaces = tuple(ns["namespace"] for ns in _PANEL_NAMESPACES)
    after_files = tuple(tuple(ns["files"]) for ns in _PANEL_NAMESPACES)
    assert snapshot_namespaces == after_namespaces
    assert snapshot_files == after_files
