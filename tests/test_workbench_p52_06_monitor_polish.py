"""P52-06 — monitor drawer deep polish.

Polishes the inner panels of the monitor drawer (introduced in P52-03):
- 4-col metric grid → 2×2 so cards have room to breathe inside the
  380px drawer
- Bigger headline numbers (the digit is the data; the label is the
  garnish — flip the visual weight)
- Hairline borders + 10/12px radius for cards (post-P52-02 ladder)
- Terminal log block gets a proper inset border + mono font lock-in
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


def _rule(selector: str) -> str:
    pattern = re.compile(
        r'(?<![\w-])' + re.escape(selector) + r'\s*\{[^}]*\}',
        re.DOTALL,
    )
    m = pattern.search(CSS)
    assert m is not None, f"CSS rule for {selector!r} not found"
    return m.group(0)


def test_metric_grid_collapses_to_two_columns():
    """4-column @ 380px drawer = 75px cards = unreadable. P52-06
    drops the layout to a 2×2 grid so each card can hold a
    non-cramped number + label."""
    body = _rule(".workbench-metrics-grid")
    assert (
        "repeat(2," in body
        or "repeat(2 ," in body
    ), (
        f"metric grid should be 2-column at the drawer width; "
        f"rule was: {body[:300]!r}"
    )


def test_metric_card_uses_p52_radius():
    body = _rule(".workbench-metrics-card")
    assert (
        "border-radius: 10px" in body
        or "border-radius:10px" in body
        or "border-radius: 12px" in body
        or "border-radius:12px" in body
    ), f"metric card radius should be 10–12px; rule was: {body[:300]!r}"


def test_metric_card_uses_hairline_token():
    body = _rule(".workbench-metrics-card")
    assert "var(--wb-hairline)" in body, (
        f"metric card border must use --wb-hairline; rule was: "
        f"{body[:300]!r}"
    )


def test_metric_value_is_bigger_than_label():
    """The actual data point should dominate visually — label is
    the explainer, number is the read. P52-06 bumps the value to
    ~1.3rem (was 0.95rem), label stays small."""
    body = _rule(".workbench-metrics-card strong")
    # match a font-size of 1.2rem or higher
    m = re.search(r"font-size:\s*([\d.]+)rem", body)
    assert m is not None, f"font-size missing on card strong: {body[:200]!r}"
    size = float(m.group(1))
    assert size >= 1.2, (
        f"metric value font-size should be ≥1.2rem (data-first); "
        f"got {size}rem"
    )


def test_metrics_panel_uses_hairline_token():
    body = _rule(".workbench-metrics-panel")
    assert "var(--wb-hairline)" in body, (
        f"metrics panel border must use --wb-hairline; rule was: "
        f"{body[:300]!r}"
    )


def test_metrics_panel_uses_p52_radius():
    body = _rule(".workbench-metrics-panel")
    assert (
        "border-radius: 10px" in body
        or "border-radius:10px" in body
        or "border-radius: 12px" in body
        or "border-radius:12px" in body
    ), f"metrics panel radius should be 10–12px; rule was: {body[:300]!r}"


def test_live_log_stream_uses_mono_font():
    """The terminal log MUST use a monospace font for vertical
    alignment — proportional fonts make tabular log columns
    look ragged."""
    body = _rule(".workbench-live-log-stream")
    assert (
        "monospace" in body.lower()
        or "menlo" in body.lower()
        or "consolas" in body.lower()
        or 'sf mono' in body.lower()
    ), (
        f"live-log stream must use a monospace font stack; "
        f"rule was: {body[:300]!r}"
    )
