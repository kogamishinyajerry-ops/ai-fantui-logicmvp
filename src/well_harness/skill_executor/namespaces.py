"""Truth-engine namespace definitions — single source of truth for
the three "things /workbench shows you can edit through proposals".

Lifted out of demo_server.py so the skill executor's planner can do
the cross-check "does this file_edit fall within an
affected_namespace?" without importing the HTTP server module.

Tests:
  - tests/test_workbench_p47_01_multi_namespace_chip.py (P47-01 contract)
  - tests/test_skill_executor_p48_02_namespaces.py (validation helpers)
"""

from __future__ import annotations

from pathlib import PurePosixPath


# Each namespace declares a set of "files" — these may be exact file
# paths (e.g. "src/well_harness/controller.py") OR directory roots
# (e.g. "src/well_harness/adapters"). Path matching is prefix-based:
# a file is "in" a namespace if it equals one of the declared paths
# OR is a descendant of one of the declared directory paths.
PANEL_NAMESPACES: tuple[dict, ...] = (
    {
        "namespace": "logic_truth",
        "label_zh": "逻辑电路真值",
        "label_en": "Logic truth",
        "files": (
            "src/well_harness/controller.py",
            "src/well_harness/models.py",
            "src/well_harness/runner.py",
            "src/well_harness/adapters",
        ),
    },
    {
        "namespace": "requirements",
        "label_zh": "需求文档",
        "label_en": "Requirements",
        "files": (
            "docs/thrust_reverser/requirements_supplement.md",
            "docs/c919_etras/requirements_v0_9.md",
            "src/well_harness/static/fantui_requirements.html",
            "src/well_harness/static/c919_requirements.html",
        ),
    },
    {
        "namespace": "simulation_workbench",
        "label_zh": "仿真工作台",
        "label_en": "Simulation panel",
        "files": (
            "src/well_harness/static/timeline-sim.html",
            "docs/panels/sim_panel_requirements.md",
        ),
    },
)

# Pre-built lookup so callers can ask "give me namespace X" without
# scanning the tuple. Empty fallback for unknown ids — caller's
# responsibility to handle.
PANEL_NAMESPACES_BY_ID: dict[str, dict] = {ns["namespace"]: ns for ns in PANEL_NAMESPACES}


def namespace_for_path(path: str) -> str | None:
    """Return the namespace id whose `files` cover `path`, or None
    if no namespace claims it. Path is treated as posix-style with
    forward slashes (the format git produces).

    A file is "covered" by a namespace if:
      - the path matches one of the namespace's `files` exactly, OR
      - one of the namespace's `files` is a directory prefix of the
        path (the directory case — `adapters/` covers everything
        under it)
    """
    if not isinstance(path, str) or not path:
        return None
    posix = PurePosixPath(path)
    posix_str = posix.as_posix()
    for ns in PANEL_NAMESPACES:
        for declared in ns["files"]:
            if posix_str == declared:
                return ns["namespace"]
            # Directory-prefix match — the declared "file" is
            # actually a directory and `path` lives under it.
            declared_dir = declared.rstrip("/") + "/"
            if posix_str.startswith(declared_dir):
                return ns["namespace"]
    return None


def validate_edit_path(
    path: str,
    *,
    affected_namespaces: list[str] | tuple[str, ...],
) -> tuple[bool, str | None]:
    """Check that `path` falls within one of the
    `affected_namespaces`. Returns (ok, reason).

    Used by the planner to refuse plans that try to edit files
    outside the namespaces the proposal claimed it was going to
    touch — that's the structural defense against an LLM
    hallucinating a "while I'm in here, let me also patch the
    demo_server" sneaky edit.
    """
    if not affected_namespaces:
        return False, "plan declared no affected_namespaces"
    declared_ns_set = set(affected_namespaces)
    matched_ns = namespace_for_path(path)
    if matched_ns is None:
        return (
            False,
            f"path {path!r} is not covered by any known namespace "
            f"(known: {sorted(PANEL_NAMESPACES_BY_ID)})",
        )
    if matched_ns not in declared_ns_set:
        return (
            False,
            f"path {path!r} is in namespace {matched_ns!r} but the "
            f"plan only declared {sorted(declared_ns_set)}",
        )
    return True, None
