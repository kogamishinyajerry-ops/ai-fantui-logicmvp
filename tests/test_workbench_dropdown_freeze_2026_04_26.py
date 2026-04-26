"""User-direction freeze (2026-04-26): dropdown exposes only the
two systems we actually demo against — thrust-reverser and
c919-etras. landing-gear and bleed-air-valve are NOT relevant
cases for this product and must not appear in the engineer-facing
selector.

The backend routing + per-system synonym tables for the frozen
systems remain in the codebase as architectural demonstrators
(adding a new system later is still a one-line change). They're
just no longer reachable via the visible dropdown.

Locks down:
  - workbench.html dropdown carries exactly the active two options
  - workbench.html does NOT advertise the frozen options
  - the LLM timeout is set to the bumped value (60s, not the
    original 30s) so reasoning-style MiniMax responses don't trip
    a premature timeout in production
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from well_harness import demo_server as ds


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"


# ─── Dropdown options ──────────────────────────────────────────────


def _dropdown_options(html: str) -> list[str]:
    """Pull every <option value="..."> inside #workbench-system-select."""
    block_match = re.search(
        r'<select id="workbench-system-select">(.+?)</select>',
        html,
        re.DOTALL,
    )
    assert block_match, "workbench-system-select block not found"
    return re.findall(r'<option value="([^"]+)"', block_match.group(1))


def test_dropdown_includes_thrust_reverser():
    options = _dropdown_options(WORKBENCH_HTML.read_text(encoding="utf-8"))
    assert "thrust-reverser" in options


def test_dropdown_includes_c919_etras():
    options = _dropdown_options(WORKBENCH_HTML.read_text(encoding="utf-8"))
    assert "c919-etras" in options


@pytest.mark.parametrize("frozen_system", ["landing-gear", "bleed-air-valve"])
def test_dropdown_excludes_frozen_systems(frozen_system):
    """A future PR re-adding either of these to the dropdown must
    fail this test loudly. To re-expose: also re-add a regression
    case here showing the user-approved decision was reversed."""
    options = _dropdown_options(WORKBENCH_HTML.read_text(encoding="utf-8"))
    assert frozen_system not in options, (
        f"system {frozen_system!r} reappeared in the dropdown — "
        f"it was frozen out 2026-04-26 per user direction. If you "
        f"need to re-expose it, also update this test."
    )


def test_dropdown_options_count_locked():
    """Exactly 2 options. If a third system gets demoed, both add
    the option and update this assertion in the same PR."""
    options = _dropdown_options(WORKBENCH_HTML.read_text(encoding="utf-8"))
    assert len(options) == 2, (
        f"dropdown has {len(options)} options ({options!r}); the "
        f"freeze 2026-04-26 expects exactly thrust-reverser + c919-etras"
    )


# ─── Backend kept for architectural completeness ───────────────────


def test_frozen_systems_still_routable_via_api():
    """The placeholder SVG endpoint must still respond for frozen
    systems — the architecture stays general; the freeze is purely
    a visibility decision."""
    fragment = ds._circuit_placeholder_fragment("landing-gear")
    assert "landing-gear" in fragment
    fragment = ds._circuit_placeholder_fragment("bleed-air-valve")
    assert "bleed-air-valve" in fragment


def test_frozen_systems_keep_their_synonym_vocab():
    """If a future PR removes the synonym tables for the frozen
    systems, the multi-system architecture story collapses. Keep
    the vocab and just hide them from the dropdown."""
    assert "landing-gear" in ds._GATE_SYNONYMS_BY_SYSTEM
    assert "bleed-air-valve" in ds._GATE_SYNONYMS_BY_SYSTEM
    assert "G1" in ds._GATE_SYNONYMS_BY_SYSTEM["landing-gear"]
    assert "V1" in ds._GATE_SYNONYMS_BY_SYSTEM["bleed-air-valve"]


# ─── LLM timeout bump ──────────────────────────────────────────────


def test_minimax_request_timeout_is_60s():
    """User reported a real-session timeout. Bumped 30s → 60s so
    MiniMax-M2.7-highspeed reasoning + JSON answer fits without
    falling back to rules. Lock the value so a future cleanup PR
    doesn't silently drop it back."""
    assert ds.MINIMAX_REQUEST_TIMEOUT_SEC == 60.0, (
        f"MINIMAX_REQUEST_TIMEOUT_SEC dropped to "
        f"{ds.MINIMAX_REQUEST_TIMEOUT_SEC}; the user-reported timeout "
        f"will recur. Re-bump to 60s or longer."
    )
