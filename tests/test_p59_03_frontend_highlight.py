"""P59-03 — workbench frontend consumes the new P59-01 SVG anchors
and the P59-02 engine fields.

Three things in scope:

1. The highlight chain generalizes from gate-only to "any logic node".
   workbench.js now exposes highlightSuggestionNodes({gates, signals,
   outputs, summaries}) which queries [data-gate-id], [data-signal-id],
   [data-summary-id] in turn. The old highlightSuggestionGates name is
   preserved as a thin alias so any external caller keeps working.

2. The interpretation panel renders affected_outputs as its own row
   (distinct from target_signals) and shows a recommended_work_order
   draft block (collapsed <details>) with a "复制 · Copy" button.

3. The CSS selector for the highlight class .is-suggestion-target
   covers all three attribute kinds — the same drop-shadow + pulse
   animation glows on signals/outputs/summaries, not just gates.

Strict additive — zero existing UI element altered.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def _read_html() -> str:
    return WORKBENCH_HTML.read_text(encoding="utf-8")


def _read_js() -> str:
    return WORKBENCH_JS.read_text(encoding="utf-8")


def _read_css() -> str:
    return WORKBENCH_CSS.read_text(encoding="utf-8")


# ── 1. highlightSuggestionNodes exists and queries 3 selectors ────


def test_highlight_suggestion_nodes_function_defined() -> None:
    """The new entry point must exist as a top-level function."""
    body = _read_js()
    assert re.search(
        r"function\s+highlightSuggestionNodes\s*\(",
        body,
    ), "highlightSuggestionNodes function not found in workbench.js"


def test_highlight_suggestion_gates_still_callable_as_alias() -> None:
    """P44-01 / P44-02 contract: any external code path calling
    highlightSuggestionGates must keep working — the name lives on as
    a backwards-compat wrapper that delegates to
    highlightSuggestionNodes({ gates: gateIds })."""
    body = _read_js()
    fn = re.search(
        r"function\s+highlightSuggestionGates\s*\([^)]*\)\s*\{[\s\S]{0,500}?\}",
        body,
    )
    assert fn is not None, "highlightSuggestionGates removed entirely — breaks back-compat"
    assert "highlightSuggestionNodes" in fn.group(0), (
        "highlightSuggestionGates must delegate to "
        "highlightSuggestionNodes; got isolated implementation."
    )


@pytest.mark.parametrize("attr", [
    "data-gate-id", "data-signal-id", "data-summary-id",
])
def test_highlight_queries_all_three_attributes(attr: str) -> None:
    """The generalized highlight must querySelectorAll on all three
    attribute kinds. Otherwise affected_outputs (data-signal-id) and
    summary aggregators (data-summary-id) would silently never glow,
    and the user feedback "highlight all visible logic nodes" would
    only apply to gates."""
    body = _read_js()
    fn = re.search(
        r"function\s+highlightSuggestionNodes\s*\([^)]*\)\s*\{[\s\S]{0,3000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    pattern = (
        rf'querySelectorAll\s*\(\s*[`\'"]\s*\[\s*{re.escape(attr)}\s*='
    )
    assert re.search(pattern, chunk), (
        f"highlightSuggestionNodes does not querySelectorAll on "
        f"[{attr}=...] — the corresponding node kind cannot be lit up."
    )


def test_highlight_clears_previous_class_before_apply() -> None:
    """A re-interpret cycle must scrub the previous .is-suggestion-target
    classes before applying new ones, otherwise stale highlights
    accumulate from one interpretation to the next."""
    body = _read_js()
    fn = re.search(
        r"function\s+highlightSuggestionNodes\s*\([^)]*\)\s*\{[\s\S]{0,3000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    assert re.search(
        r'querySelectorAll\s*\(\s*"\.is-suggestion-target"\s*\)',
        chunk,
    ), "missing initial sweep over .is-suggestion-target before reapply"
    assert "classList.remove" in chunk, "missing classList.remove call"


# ── 2. Interpretation pipeline passes new fields ─────────────────


def test_interpret_call_site_passes_signals_and_outputs() -> None:
    """When the interpreter response lands, the highlight must pick
    up affected_gates AND target_signals AND affected_outputs — not
    just gates as before P59-03."""
    body = _read_js()
    # The `interpretation = await response.json()` block must
    # subsequently call highlightSuggestionNodes (not the alias) with
    # all three list fields.
    call = re.search(
        r"highlightSuggestionNodes\s*\(\s*\{[\s\S]{0,400}?\}\s*\)",
        body,
    )
    assert call is not None, (
        "no highlightSuggestionNodes({...}) call — call site likely "
        "still uses the old gate-only entry point."
    )
    args = call.group(0)
    for required in ("affected_gates", "target_signals", "affected_outputs"):
        assert required in args, (
            f"highlightSuggestionNodes call site does not pass "
            f"{required}: {args}"
        )


# ── 3. Outputs row in the interpretation panel ────────────────────


def test_interpretation_panel_has_outputs_row() -> None:
    """The panel must show a "命中输出 / Affected output(s)" row so the
    engineer sees which output cmd names the interpreter resolved."""
    body = _read_html()
    assert 'id="workbench-suggestion-interpretation-outputs"' in body, (
        "interpretation panel missing the affected_outputs <dd>"
    )
    # Sibling <dt> label must mention "命中输出" (Chinese) or
    # "Affected output" (English) so the row is human-labeled.
    assert re.search(
        r"<dt>\s*命中输出[\s\S]{0,80}?Affected output",
        body,
    ), "outputs row label missing the bilingual heading"


def test_render_function_populates_outputs_field() -> None:
    """renderSuggestionInterpretation must wire interpretation
    .affected_outputs into the new <dd> id. Otherwise the row stays
    at "—" forever."""
    body = _read_js()
    # Two strings must co-occur in the same setText call.
    pat = (
        r'setText\s*\(\s*\n?\s*"workbench-suggestion-interpretation-outputs"'
        r'[\s\S]{0,400}?affected_outputs'
    )
    assert re.search(pat, body), (
        "no setText('workbench-suggestion-interpretation-outputs', ...) "
        "wired to interpretation.affected_outputs"
    )


# ── 4. Recommendation draft block ────────────────────────────────


def test_recommendation_block_present_in_html() -> None:
    """The collapsible <details> block + its <pre> textarea + Copy
    button must all exist in workbench.html."""
    body = _read_html()
    assert 'id="workbench-suggestion-recommendation"' in body
    assert 'id="workbench-suggestion-recommendation-text"' in body
    assert 'id="workbench-suggestion-recommendation-copy-btn"' in body
    # <details> default-collapsed (no `open` attribute), default-hidden
    # (so an older server with no draft does not flash an empty box).
    rec = re.search(
        r'<details[^>]*id="workbench-suggestion-recommendation"[^>]*>',
        body,
    )
    assert rec is not None
    assert "hidden" in rec.group(0), (
        "recommendation <details> must start hidden so an empty draft "
        "or a pre-P59-02 server doesn't render an empty box"
    )


def test_render_recommended_work_order_function_defined() -> None:
    body = _read_js()
    assert re.search(
        r"function\s+renderRecommendedWorkOrder\s*\(",
        body,
    ), "renderRecommendedWorkOrder helper not found in workbench.js"


def test_render_recommended_work_order_called_from_render_panel() -> None:
    """renderSuggestionInterpretation must invoke
    renderRecommendedWorkOrder so the draft surfaces every time a
    fresh interpretation lands."""
    body = _read_js()
    fn = re.search(
        r"function\s+renderSuggestionInterpretation\s*\([^)]*\)\s*\{"
        r"[\s\S]{0,5000}?\n\}",
        body,
    )
    assert fn is not None
    assert "renderRecommendedWorkOrder" in fn.group(0), (
        "renderRecommendedWorkOrder is never invoked from the panel "
        "renderer — the work-order draft would never populate."
    )


def test_render_recommended_work_order_handles_empty_gracefully() -> None:
    """When recommended_work_order_zh / _en are both absent (older
    server / fallback path), the function must hide the wrap rather
    than render an empty box. This protects backwards-compat.

    Codex P59-03 NIT-03 fix: assert the BEHAVIOR (wrap.hidden = true
    on the empty path), not the exact guard syntax. An equivalent
    `if (!draft.length)` or `if (draft.trim() === "")` should still
    pass."""
    body = _read_js()
    fn = re.search(
        r"function\s+renderRecommendedWorkOrder\s*\([^)]*\)\s*\{"
        r"[\s\S]{0,2000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    # Must read both zh and en fields with || fallback.
    assert "recommended_work_order_zh" in chunk
    assert "recommended_work_order_en" in chunk
    # Must set wrap.hidden = true somewhere (the empty-draft path).
    # Don't pin the exact guard expression; just require the effect
    # to be present and a contemporaneous empty-state textContent
    # reset so a stale draft string doesn't outlive a hidden wrap.
    assert re.search(
        r"wrap\.hidden\s*=\s*true", chunk,
    ), "renderRecommendedWorkOrder does not set wrap.hidden = true on empty draft"
    assert re.search(
        r'textEl\.textContent\s*=\s*""', chunk,
    ), "renderRecommendedWorkOrder does not clear textEl.textContent on empty draft"


def test_render_resets_details_open_state_on_each_render() -> None:
    """Codex P59-03 NIT-02 regression: ↻ 重新解读 calls
    runSuggestionInterpret directly (not clearSuggestionInterpretation).
    If the engineer expanded the draft once, a subsequent
    interpretation would inherit the open state, contradicting the
    intended collapsed-by-default UX. renderRecommendedWorkOrder
    must remove the `open` attribute on every call so each new draft
    starts collapsed."""
    body = _read_js()
    fn = re.search(
        r"function\s+renderRecommendedWorkOrder\s*\([^)]*\)\s*\{"
        r"[\s\S]{0,2000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    assert re.search(
        r'wrap\.removeAttribute\s*\(\s*["\']open["\']\s*\)',
        chunk,
    ), (
        "renderRecommendedWorkOrder does not removeAttribute('open'). "
        "An expanded draft from a prior interpretation would persist."
    )


def test_copy_handler_clears_pending_reset_timer() -> None:
    """Codex P59-03 NIT-01 regression: rapid clicks on Copy must not
    capture a transient label as 'original' and leave the button
    stuck in the copied state. The handler should use a constant
    idle label and clear any pending reset timer before scheduling
    the next one."""
    body = _read_js()
    fn = re.search(
        r"function\s+installRecommendationCopyHandler\s*\([^)]*\)\s*\{"
        r"[\s\S]{0,4000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    # Must reference a stable idle label constant (avoids capturing
    # transient "已复制" as the next "original" label).
    assert re.search(
        r"RECOMMENDATION_COPY_IDLE_LABEL|✓ 已复制[\s\S]{0,400}?复制失败",
        chunk,
    ), (
        "Copy handler captures btn.textContent as the 'original' label "
        "rather than using a constant idle string — racey."
    )
    # Must call clearTimeout before scheduling a new reset.
    assert "clearTimeout" in chunk, (
        "Copy handler does not clearTimeout before scheduling a new "
        "reset — rapid clicks would stack timers and stick the button "
        "in the copied state."
    )
    # Must check execCommand return value (Codex NIT-01: legacy fallback
    # should treat false as a failure, not silent success).
    assert re.search(
        r"execCommand\s*\(\s*[\"']copy[\"']\s*\)\s*===?\s*true",
        chunk,
    ), (
        "Copy handler does not check the boolean return of "
        "document.execCommand('copy') — non-secure-context denials "
        "would silently appear successful."
    )


def test_copy_handler_installed_on_dom_ready() -> None:
    """installRecommendationCopyHandler must be wired into the
    DOMContentLoaded bootstrap so the Copy button works on first load
    without a re-interpret."""
    body = _read_js()
    assert re.search(
        r"function\s+installRecommendationCopyHandler\s*\(",
        body,
    ), "installRecommendationCopyHandler helper not defined"
    boot = re.search(
        r'window\.addEventListener\s*\(\s*"DOMContentLoaded"[\s\S]{0,3000}?\}\s*\)\s*;',
        body,
    )
    assert boot is not None
    assert "installRecommendationCopyHandler" in boot.group(0), (
        "DOMContentLoaded bootstrap does not call "
        "installRecommendationCopyHandler — Copy button stays inert."
    )


def test_copy_handler_uses_clipboard_with_legacy_fallback() -> None:
    """The Copy button should prefer navigator.clipboard.writeText and
    fall back to a hidden-textarea + execCommand path so it still
    works on older browsers and non-secure contexts."""
    body = _read_js()
    fn = re.search(
        r"function\s+installRecommendationCopyHandler\s*\([^)]*\)\s*\{"
        r"[\s\S]{0,3000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    assert "navigator.clipboard" in chunk, (
        "Copy handler should prefer navigator.clipboard.writeText"
    )
    assert "execCommand" in chunk or "document.execCommand" in chunk, (
        "Copy handler should have a non-clipboard fallback path"
    )


# ── 5. Clear path scrubs the new state ──────────────────────────


def test_clear_interpretation_uses_node_highlight_and_hides_recommendation() -> None:
    """clearSuggestionInterpretation (re-interpret / cancel) must
    sweep ALL highlights via the new entry point AND hide the
    recommendation block + clear its text. Otherwise stale
    highlights/draft survive between interpretations."""
    body = _read_js()
    fn = re.search(
        r"function\s+clearSuggestionInterpretation\s*\(\s*\)\s*\{"
        r"[\s\S]{0,2000}?\n\}",
        body,
    )
    assert fn is not None
    chunk = fn.group(0)
    assert "highlightSuggestionNodes" in chunk, (
        "clear function still uses the gate-only highlight — signal/"
        "output/summary highlights would persist."
    )
    assert "workbench-suggestion-recommendation" in chunk, (
        "clear function does not touch the recommendation block — "
        "stale draft would survive a re-interpret."
    )


# ── 6. CSS — selector covers all three attribute kinds ───────────


def test_css_highlight_selector_covers_signal_and_summary() -> None:
    """The .is-suggestion-target rule originally only matched
    [data-gate-id]. P59-03 must broaden the selector to also cover
    [data-signal-id] and [data-summary-id] so the same drop-shadow +
    pulse animation glows on every node kind."""
    body = _read_css()
    # Pattern: a selector list that includes all three forms before
    # the opening brace.
    rule = re.search(
        r"\.workbench-circuit-hero-mount\s+\[data-gate-id\]\.is-suggestion-target"
        r"[\s\S]{0,400}?\{",
        body,
    )
    assert rule is not None, "gate-id rule disappeared entirely"
    block = rule.group(0)
    assert "data-signal-id" in block, (
        ".is-suggestion-target CSS rule does not cover [data-signal-id] — "
        "input/output highlights would have no visual style."
    )
    assert "data-summary-id" in block, (
        ".is-suggestion-target CSS rule does not cover [data-summary-id] — "
        "summary aggregator highlights would have no visual style."
    )


def test_pulse_animation_keyframes_preserved() -> None:
    """P44-01 contract: workbench-gate-pulse keyframes must remain so
    the existing animation reference resolves."""
    body = _read_css()
    assert "@keyframes workbench-gate-pulse" in body, (
        "workbench-gate-pulse animation removed — gate highlight would "
        "stop pulsing."
    )


# ── 7. Layout invariance — no existing element id renamed ────────


@pytest.mark.parametrize("legacy_id", [
    "workbench-suggestion-interpretation",
    "workbench-suggestion-interpretation-gates",
    "workbench-suggestion-interpretation-targets",
    "workbench-suggestion-interpretation-summary",
    "workbench-suggestion-interpretation-change-kind",
    "workbench-suggestion-interpretation-strategy",
    "workbench-suggestion-interpretation-confidence",
    "workbench-suggestion-confirm-btn",
    "workbench-suggestion-reinterpret-btn",
    "workbench-suggestion-cancel-btn",
])
def test_legacy_panel_ids_preserved(legacy_id: str) -> None:
    """Strict additive-only mandate: every existing element id from
    the panel pre-P59-03 must still be present. A rename would break
    P44/P45/P54/P55 tests and any external bookmarklet."""
    body = _read_html()
    assert f'id="{legacy_id}"' in body, (
        f'pre-P59-03 element id="{legacy_id}" missing — additive-only '
        f"contract violated."
    )
