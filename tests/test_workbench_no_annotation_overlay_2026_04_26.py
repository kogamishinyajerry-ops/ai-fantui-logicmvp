"""User-direction (2026-04-26): /workbench MUST NOT load the legacy
annotation overlay. Clicking the control logic panel was generating
stray green-dot markers — a leftover binding from the
point/area/link/text-range paradigm we ripped out in P44-02.

The current flow is suggestion-form ONLY:
  engineer types free-form text → /api/workbench/interpret-suggestion
  → highlight affected gate(s) → engineer confirms → POST to /api/proposals.

Locks down:
  - workbench.html does NOT include annotation_overlay.js
  - the circuit hero does NOT carry the data-annotation-surface
    attribute or workbench-annotation-surface class — those were
    the bind points the overlay used to attach click handlers
  - the legacy overlay file itself still EXISTS for the separate
    /workbench/bundle surface (not migrated yet); we only assert
    it isn't pulled into /workbench
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"


def _html() -> str:
    return WORKBENCH_HTML.read_text(encoding="utf-8")


def test_workbench_html_does_not_load_annotation_overlay_script():
    assert "annotation_overlay.js" not in _html() or "<script src=\"/annotation_overlay.js\"" not in _html(), (
        "/workbench is loading annotation_overlay.js again. That's "
        "the legacy point/area/link/text-range overlay; it makes "
        "every panel click drop a stray green-dot marker. P44-02 "
        "removed the toolbar UI; this script tag was the residual "
        "binding hook. Do NOT re-add."
    )


def test_workbench_html_does_not_load_annotation_overlay_script_strict():
    """Stricter form of the assertion above: literal script tag must
    be absent. The other test still passes if it appears only inside
    a comment, which is fine; this one fails if a real <script> tag
    is anywhere."""
    html = _html()
    assert '<script src="/annotation_overlay.js"></script>' not in html
    assert "<script src='/annotation_overlay.js'></script>" not in html


def _strip_html_comments(html: str) -> str:
    """Drop every <!-- ... --> block so substring assertions don't
    false-positive on the explanatory comment we left next to the
    removed binding."""
    out = []
    i = 0
    while i < len(html):
        start = html.find("<!--", i)
        if start < 0:
            out.append(html[i:])
            break
        out.append(html[i:start])
        end = html.find("-->", start)
        if end < 0:
            break  # unterminated comment, drop the rest
        i = end + 3
    return "".join(out)


def test_circuit_hero_no_longer_carries_annotation_surface_class():
    """The CSS class workbench-annotation-surface was the binding
    selector the overlay used to attach click handlers. Without the
    class, the overlay (if accidentally re-loaded by some other
    page) wouldn't bind to the /workbench hero. Comments are
    stripped before checking — the explanatory note next to the
    removal must not false-positive this assertion."""
    code = _strip_html_comments(_html())
    assert "workbench-annotation-surface" not in code, (
        "the legacy annotation surface class reappeared on the "
        "/workbench hero — defense in depth says strip it"
    )


def test_circuit_hero_no_longer_carries_annotation_surface_attribute():
    code = _strip_html_comments(_html())
    assert "data-annotation-surface" not in code, (
        "data-annotation-surface attribute reappeared — same "
        "binding hook as the class above"
    )


def test_overlay_file_itself_still_exists_for_bundle_page():
    """The overlay JS file stays in static/ for /workbench/bundle.
    Sanity check that we didn't accidentally delete something the
    bundle surface still depends on."""
    overlay = REPO_ROOT / "src" / "well_harness" / "static" / "annotation_overlay.js"
    assert overlay.is_file()


# ─── Sanity: the new suggestion flow IS still wired ────────────────


def test_workbench_html_still_carries_suggestion_form():
    """If a future cleanup PR strips the overlay AND breaks the
    suggestion form, /workbench has no engineer-input surface left.
    Spot-check the form anchors stayed."""
    html = _html()
    assert 'id="workbench-suggestion-form"' in html
    assert 'id="workbench-suggestion-input"' in html
    assert 'id="workbench-suggestion-interpret-btn"' in html


def test_workbench_html_still_loads_main_script():
    """workbench.js drives all the post-P44-02 functionality; if
    it gets dropped accidentally, the page is dead."""
    html = _html()
    assert '<script src="/workbench.js"></script>' in html
