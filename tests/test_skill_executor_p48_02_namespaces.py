"""P48-02 — namespace coverage helpers.

Locks down the cross-check the planner uses to refuse plans whose
file_edits stray outside their declared affected_namespaces. This is
the structural defense against an LLM hallucinating "while I'm here,
let me also patch demo_server.py" sneaky edits.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.namespaces import (
    PANEL_NAMESPACES,
    PANEL_NAMESPACES_BY_ID,
    namespace_for_path,
    validate_edit_path,
)


# ─── 1. Constant shape ─────────────────────────────────────────────────


def test_panel_namespaces_has_three_entries():
    assert len(PANEL_NAMESPACES) == 3


def test_panel_namespaces_by_id_index():
    assert set(PANEL_NAMESPACES_BY_ID) == {
        "logic_truth",
        "requirements",
        "simulation_workbench",
    }


def test_demo_server_uses_same_constant():
    """The demo_server's `_PANEL_NAMESPACES` alias must point at
    the lifted constant — single source of truth across the
    workbench backend and the skill executor."""
    from well_harness import demo_server as ds
    assert ds._PANEL_NAMESPACES is PANEL_NAMESPACES


# ─── 2. namespace_for_path: exact-file matches ─────────────────────────


@pytest.mark.parametrize(
    "path,expected",
    [
        ("src/well_harness/controller.py", "logic_truth"),
        ("src/well_harness/models.py", "logic_truth"),
        ("src/well_harness/runner.py", "logic_truth"),
        ("docs/thrust_reverser/requirements_supplement.md", "requirements"),
        ("docs/c919_etras/requirements_v0_9.md", "requirements"),
        ("src/well_harness/static/fantui_requirements.html", "requirements"),
        ("src/well_harness/static/c919_requirements.html", "requirements"),
        ("src/well_harness/static/timeline-sim.html", "simulation_workbench"),
        ("docs/panels/sim_panel_requirements.md", "simulation_workbench"),
    ],
)
def test_namespace_for_exact_files(path, expected):
    assert namespace_for_path(path) == expected


# ─── 3. namespace_for_path: directory-prefix matches ───────────────────


@pytest.mark.parametrize(
    "path",
    [
        "src/well_harness/adapters/foo.py",
        "src/well_harness/adapters/sub/deep.py",
        "src/well_harness/adapters/__init__.py",
    ],
)
def test_directory_prefix_match_logic_truth(path):
    assert namespace_for_path(path) == "logic_truth"


def test_directory_match_requires_trailing_slash_semantics():
    """`src/well_harness/adapters` covers `adapters/X` but should
    NOT spuriously match `src/well_harness/adapters_foo.py` —
    that's a different file with a confusable prefix."""
    assert namespace_for_path("src/well_harness/adapters_foo.py") is None


# ─── 4. namespace_for_path: rejection cases ────────────────────────────


@pytest.mark.parametrize(
    "path",
    [
        "src/well_harness/demo_server.py",  # workbench server, NOT in any ns
        "src/well_harness/static/workbench.html",  # workbench UI, not in ns
        "tests/test_foo.py",  # tests are not a truth namespace
        ".github/workflows/ci.yml",  # CI not a truth ns
        "Makefile",
        "",
        "/",
        "../escape.py",
    ],
)
def test_unknown_paths_return_none(path):
    assert namespace_for_path(path) is None


def test_namespace_for_non_string_returns_none():
    """Defensive — caller may pass random data; we shouldn't
    crash."""
    assert namespace_for_path(None) is None
    assert namespace_for_path(123) is None


# ─── 5. validate_edit_path: happy path ─────────────────────────────────


def test_validate_edit_in_declared_namespace_ok():
    ok, reason = validate_edit_path(
        "src/well_harness/controller.py",
        affected_namespaces=["logic_truth"],
    )
    assert ok is True
    assert reason is None


def test_validate_directory_prefix_in_declared_namespace_ok():
    ok, reason = validate_edit_path(
        "src/well_harness/adapters/sensor.py",
        affected_namespaces=["logic_truth"],
    )
    assert ok is True


def test_validate_multi_namespace_plan_ok():
    """A plan can declare multiple namespaces if it actually
    needs to touch files in each."""
    ok, _ = validate_edit_path(
        "src/well_harness/controller.py",
        affected_namespaces=["logic_truth", "simulation_workbench"],
    )
    assert ok is True


# ─── 6. validate_edit_path: rejection cases ────────────────────────────


def test_validate_rejects_path_not_in_any_namespace():
    ok, reason = validate_edit_path(
        "src/well_harness/demo_server.py",
        affected_namespaces=["logic_truth"],
    )
    assert ok is False
    assert "not covered by any known namespace" in reason


def test_validate_rejects_path_in_undeclared_namespace():
    """The file IS in a namespace, but the plan only declared a
    different one — that's the LLM trying to sneak an edit past
    the declared scope."""
    ok, reason = validate_edit_path(
        "src/well_harness/controller.py",
        affected_namespaces=["requirements"],
    )
    assert ok is False
    assert "logic_truth" in reason
    assert "requirements" in reason


def test_validate_rejects_empty_affected_namespaces():
    ok, reason = validate_edit_path(
        "src/well_harness/controller.py",
        affected_namespaces=[],
    )
    assert ok is False
    assert "no affected_namespaces" in reason


def test_validate_accepts_tuple_input():
    """`affected_namespaces` should accept a tuple as well as a
    list — the planner may produce either depending on the
    LLM serializer."""
    ok, _ = validate_edit_path(
        "src/well_harness/controller.py",
        affected_namespaces=("logic_truth",),
    )
    assert ok is True


# ─── 7. Coverage of every defined namespace ────────────────────────────


def test_every_declared_namespace_has_at_least_one_resolvable_path():
    """Sanity — if a namespace has zero matching files in tree,
    something's wrong with the declaration. Every declared
    namespace must have at least one file in PANEL_NAMESPACES whose
    path resolves back to itself via namespace_for_path."""
    for ns in PANEL_NAMESPACES:
        any_match = False
        for declared in ns["files"]:
            # For directory-style entries, probe with a fake child
            test_path = declared if "." in declared else f"{declared}/__test_probe__.py"
            if namespace_for_path(test_path) == ns["namespace"]:
                any_match = True
                break
        assert any_match, (
            f"namespace {ns['namespace']!r} has no file in its `files` "
            f"that resolves back to it via namespace_for_path"
        )
