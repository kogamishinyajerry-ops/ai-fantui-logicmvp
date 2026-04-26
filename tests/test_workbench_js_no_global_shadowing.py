"""E11-11 — guard against variable shadowing of `document` global in workbench.js.

The renderFingerprintDocumentList loop originally bound the array element
to a parameter named `document`, which shadowed the global DOM `document`
and made `document.createElement(...)` call a method on the data object
instead. Bundle-page boot threw `TypeError: document.createElement is not a function`.

This test is a static-source guard so the regression is caught even when
the e2e suite is deselected (default `pytest` run).
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_no_map_callback_shadows_document_global() -> None:
    """No `.map((document) => ...)` or similar bindings of the literal
    name `document` inside an arrow / function body — that would shadow
    the global `document` and silently break createElement calls."""
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    # Catches arrow params: `(document)` `(document,` `, document)` `, document,`
    pattern = re.compile(r"\((?:[^)]*,\s*)?document(?:\s*,[^)]*)?\)\s*=>")
    matches = pattern.findall(js)
    assert not matches, (
        f"workbench.js contains an arrow callback that shadows global "
        f"`document`; rename the parameter (e.g. `doc`/`item`). Matches: {matches}"
    )


def test_no_function_param_shadows_document_global() -> None:
    """No `function name(document)` declarations that shadow the global."""
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    pattern = re.compile(r"function\s+\w+\s*\([^)]*\bdocument\b[^)]*\)")
    matches = pattern.findall(js)
    assert not matches, (
        f"workbench.js declares a function parameter named `document` "
        f"that shadows the global. Matches: {matches}"
    )
