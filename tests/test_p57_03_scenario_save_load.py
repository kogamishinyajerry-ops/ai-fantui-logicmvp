"""P57-03 — save/load custom scenarios + import/export to disk.

Builds on P57-01's editor and P57-02's catalogs. Without persistence,
every browser refresh wipes the user's hand-crafted timeline. P57-03
adds:

  1. **Save Scratch** — saves the current timeline to localStorage
     under `well-harness:timeline-scenarios.<name>` (user prompted
     for `<name>`).
  2. **Load** — preset dropdown grows two groups: "系统内置"
     (built-in PRESETS) and "用户暂存" (user-saved scenarios from
     localStorage). Loading either populates the editor.
  3. **Delete Saved** — for user scratch only; built-in presets
     can't be deleted.
  4. **Export JSON** — triggers browser download of the current
     timeline as `<title>.timeline.json`.
  5. **Import JSON** — file picker accepts `.json` and replaces
     the editor's currentTimeline + textarea.

The localStorage key namespace prevents clashes with other pages.
The dropdown's grouped <optgroup> separates blessed presets (which
get committed to the repo) from scratch (browser-only).

Build-time blessed fixtures stay the source of truth — localStorage
is the dev-iteration scratchpad. P57-04 (state-coverage sweep) is
where the editor gets its real workout authoring fixtures the user
can then export and check in to `src/well_harness/timelines/`.
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


# ─── 1. Toolbar surfaces ───


@pytest.mark.parametrize(
    "btn_id",
    ["saveScenarioBtn", "exportJsonBtn", "importJsonBtn"],
)
def test_toolbar_buttons_exist(btn_id: str) -> None:
    """Three toolbar controls must exist in the DOM:
        - Save Scratch (saveScenarioBtn)
        - Export JSON (exportJsonBtn)
        - Import JSON (importJsonBtn)
    The Load action piggybacks on the existing presetSelect (which
    gains a 用户暂存 optgroup), not a new button."""
    body = _read()
    found = re.search(
        rf'<button[^>]*\bid="{btn_id}"|<input[^>]*\bid="{btn_id}"',
        body,
    )
    assert found is not None, (
        f"toolbar button id={btn_id!r} not found. P57-03 needs all "
        f"three controls so users can save/export/import scenarios."
    )


def test_import_json_uses_file_picker_input() -> None:
    """Import must use `<input type="file" accept=".json">` so the
    OS file picker opens. A plain button without a file input would
    require manual JSON paste, defeating the import affordance."""
    body = _read()
    found = re.search(
        r'<input[^>]*type="file"[^>]*\baccept="\.json"'
        r'|<input[^>]*\baccept="\.json"[^>]*type="file"',
        body,
    )
    assert found is not None, (
        "no `<input type=\"file\" accept=\".json\">` in the DOM. "
        "Import must open the OS file picker; a plain button does "
        "not give that affordance."
    )


# ─── 2. localStorage namespace + key format ───


def test_localstorage_namespace_is_well_harness() -> None:
    """The localStorage key prefix must be 'well-harness:' so
    different apps on the same origin (workbench / panel / etc.)
    don't clash. Bare 'timeline-scenarios.<name>' would be too
    generic."""
    body = _read()
    pattern = (
        r'["\']well-harness:timeline-scenarios'
        r'|["\']well-harness:[\w-]+:scenarios'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        "localStorage key prefix 'well-harness:timeline-scenarios' "
        "not found. Generic keys would clash with sibling pages."
    )


def test_save_handler_writes_to_localstorage() -> None:
    """The save handler must call localStorage.setItem with the
    namespaced key. A handler that only updates DOM but never
    writes localStorage means the scratch dies on refresh.

    Accept either the literal prefix string OR a SCRATCH_PREFIX
    constant — the contract is "call setItem with the namespaced
    key", however the source structures the prefix."""
    body = _read()
    pattern = (
        r'localStorage\.setItem\s*\([^)]*(?:well-harness|SCRATCH_PREFIX)'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        "save handler does not call localStorage.setItem with the "
        "namespaced key (literal or SCRATCH_PREFIX). Without it, "
        "save is a no-op."
    )


def test_load_path_reads_from_localstorage() -> None:
    """The load path (preset dropdown change + initial population)
    must read from localStorage. Otherwise saved scratch is
    invisible across reloads."""
    body = _read()
    pattern = (
        r'localStorage\.getItem\s*\([^)]*well-harness'
        r'|Object\.keys\(localStorage\)'
        r'|for\s*\(\s*let\s+i\s*=\s*0[^)]*localStorage\.length'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        "load path does not read from localStorage. The 用户暂存 "
        "optgroup will be empty across reloads."
    )


# ─── 3. Preset dropdown grows the 用户暂存 optgroup ───


def test_preset_dropdown_has_user_saved_optgroup() -> None:
    """When the user has saved scenarios, the preset <select> must
    use <optgroup label="用户暂存"> (or equivalent) to separate
    them from the built-in PRESETS group. Flat options would
    confuse blessed vs scratch."""
    body = _read()
    # The optgroup may be created in JS at render time; look for
    # either the literal HTML or a JS string referencing it.
    pattern = (
        r'<optgroup\s+label="[^"]*用户暂存'
        r'|<optgroup\s+label="[^"]*scratch'
        r'|optgroup[^>]*label[^>]*用户暂存'
        r'|createElement\(\s*["\']optgroup'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        "preset dropdown does not declare a 用户暂存 / scratch "
        "<optgroup>. Flat user-saved options would mix with "
        "blessed presets and confuse the user."
    )


def test_preset_dropdown_has_system_builtin_optgroup() -> None:
    """Mirror group for blessed presets. Without the 系统内置
    optgroup, the structure is asymmetric (only saved is grouped)."""
    body = _read()
    pattern = (
        r'<optgroup\s+label="[^"]*系统内置'
        r'|<optgroup\s+label="[^"]*built-?in'
        r'|optgroup[^>]*label[^>]*系统内置'
    )
    found = re.search(pattern, body)
    assert found is not None, (
        "preset dropdown does not declare a 系统内置 optgroup. "
        "If 用户暂存 is grouped but built-ins aren't, the "
        "dropdown looks broken."
    )


# ─── 4. Export uses Blob + download attribute ───


def test_export_uses_blob_and_anchor_download() -> None:
    """Export must:
        - Create a Blob with type "application/json"
        - Use an <a download="..."> click trigger
    A simple `window.open(data:json…)` would fall over for big
    payloads."""
    body = _read()
    has_blob = re.search(
        r'new\s+Blob\s*\([^)]*application/json',
        body, re.DOTALL,
    )
    has_anchor = re.search(
        r'\.download\s*=\s*["\'][^"\']*\.timeline\.json'
        r'|\.download\s*=\s*[a-zA-Z_]\w*\s*\+\s*["\']\.timeline\.json'
        r'|\.download\s*=\s*`[^`]*\.timeline\.json',
        body,
    )
    assert has_blob is not None, (
        "export path doesn't construct a Blob with application/json "
        "MIME. Big timelines need Blob + URL.createObjectURL, not a "
        "data: URL."
    )
    assert has_anchor is not None, (
        "export path doesn't set anchor.download with a "
        "*.timeline.json filename. The browser default would be "
        "'download' with no extension."
    )


# ─── 5. Import handler updates currentTimeline + textarea ───


def test_import_handler_calls_renderall() -> None:
    """After parsing the imported file, the handler must update the
    in-memory model and re-render so both Visual and Raw tabs
    reflect the imported content. A handler that only writes to
    the textarea would leave Visual stale until next tab switch."""
    body = _read()
    # Look for a function that handles the file change event AND
    # calls renderAll() (the model+UI sync helper from P57-01).
    pattern = (
        r'FileReader\s*\(\s*\)|readAsText'
    )
    has_filereader = re.search(pattern, body)
    assert has_filereader is not None, (
        "import handler does not use FileReader. Without async "
        "file read, the .json picker can't load."
    )
    # And renderAll (or equivalent re-render path) must be called
    # somewhere in the import flow — either inline or via a
    # function that wraps the parse+render+sync.
    pattern2 = (
        r'(?:onload|onChange|importJson)[\s\S]{0,400}renderAll'
    )
    has_render = re.search(pattern2, body)
    assert has_render is not None, (
        "import handler does not call renderAll() after parsing. "
        "Visual tab would stay stale showing the previous timeline."
    )
