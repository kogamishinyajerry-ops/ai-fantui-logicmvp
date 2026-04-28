"""P56-06 — unify fantui_circuit.html visual style with C919 ETRAS standard.

User report (2026-04-28): "反推逻辑控制电路的风格没有和C919 ETRAS的统一，
节点的文字说明也不足."

Two distinct gaps vs c919_etras_panel/circuit.html:

1. **Color palette**: fantui_circuit declares `--active: #00e5a0` (green)
   as the brand color, used for header h1, .badge, .info-card h3.
   The C919 standard uses `--cyan: #00c8f5` for those identity surfaces
   and reserves green for active signal lines. The unified palette
   (already in etras_chrome.css :root) is cyan-brand / green-active /
   amber-warn / red-fail. fantui_circuit must follow that convention.

2. **Node text descriptions**: each input node in fantui_circuit's SVG
   has a single line of code-style text (e.g. `radio_altitude_ft < 6 ft`).
   The C919 standard adds a Chinese gloss line below each input
   (e.g. `LGCU1 WOW` + `着陆传感器 1`) so a non-coder can read the
   diagram. fantui_circuit also lacks per-gate captions explaining
   the L1-L4 rows at-a-glance.

Fix:
  1. add `--cyan: #00c8f5` token to :root and switch header h1, .badge,
     and .info-card h3 to use it (signal lines stay `--active`/green)
  2. for each input node in the SVG, add a second `<text>` element
     with a Chinese gloss ≤ 7.5px font-size below the primary line
  3. add a short caption above each L1-L4 AND gate naming the row
     ("TLS 解锁起始 · 4 cond" etc.) so the gate's purpose is legible
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"
FANTUI_CIRCUIT = STATIC / "fantui_circuit.html"


def _strip_css_comments(css: str) -> str:
    """Strip /* ... */ comments so they don't interfere with rule matching."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _inline_css(html: str) -> str:
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
    return _strip_css_comments("\n".join(blocks))


# ─── 1. Cyan brand token declared and used for identity ───


def test_fantui_circuit_declares_cyan_brand_token() -> None:
    """The unified palette in etras_chrome.css uses --cyan as the brand.
    fantui_circuit's inline :root must declare a cyan token (either
    `--cyan: #00c8f5` directly, or `--active: #00c8f5`) so headers and
    badges match the C919 ETRAS standard."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    css = _inline_css(body)
    root_match = re.search(r":root\s*\{([^}]+)\}", css, re.DOTALL)
    assert root_match is not None, "fantui_circuit missing :root tokens"
    root_body = root_match.group(1)
    has_cyan = bool(
        re.search(r"--cyan\s*:\s*#00c8f5", root_body)
        or re.search(r"--active\s*:\s*#00c8f5", root_body)
    )
    assert has_cyan, (
        "fantui_circuit :root must declare cyan #00c8f5 (as --cyan or "
        "--active) to align with the C919 ETRAS palette in "
        "etras_chrome.css. Currently uses green as primary brand, which "
        "is what makes the page look out-of-style next to the C919 "
        "circuit."
    )


def test_fantui_circuit_header_uses_cyan_brand() -> None:
    """`header h1` (the page title) and `.badge` are identity surfaces;
    they must use the cyan brand token (var(--cyan) or var(--active)
    when --active is cyan), NOT green. Otherwise the page reads as
    a different system from the C919 ETRAS circuit."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    css = _inline_css(body)
    # Find header h1 rule.
    h1_match = re.search(
        r"header\s+h1\s*\{([^}]+)\}", css, re.DOTALL,
    )
    assert h1_match is not None, "header h1 rule missing"
    h1_body = h1_match.group(1)
    color_match = re.search(r"color\s*:\s*([^;}]+)", h1_body)
    assert color_match is not None, "header h1 must declare a color"
    color_val = color_match.group(1).strip()
    # Either var(--cyan) directly, or var(--active) where --active is cyan.
    assert "cyan" in color_val or "active" in color_val, (
        f"header h1 color is {color_val!r} — must reference the cyan "
        f"brand token (var(--cyan) or var(--active) when --active is "
        f"#00c8f5). Hard-coded green or other hex breaks unification."
    )


# ─── 1b. .badge and .info-card h3 also switch to the cyan brand ───
# Codex R1 (PR #116) flagged: header h1 was covered, but .badge and
# .info-card h3 were not. A future edit could revert either to the
# old green and the suite would still pass.


@pytest.mark.parametrize(
    "selector",
    [
        # `.badge` matches both `color:` and `border:` — assert the rule
        # references the cyan brand somewhere (cyan or cyan-d).
        r"\.badge",
        r"\.info-card\s+h3",
    ],
)
def test_fantui_circuit_identity_surfaces_use_cyan(selector: str) -> None:
    """`.badge` and `.info-card h3` are identity surfaces alongside
    `header h1`. They must reference the cyan brand token (--cyan or
    --cyan-d) so the page reads as the unified palette, not the old
    green-everywhere palette."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    css = _inline_css(body)
    rule = re.search(selector + r"\s*\{([^}]+)\}", css, re.DOTALL)
    assert rule is not None, f"selector {selector!r} not found in CSS"
    rule_body = rule.group(1)
    assert "cyan" in rule_body, (
        f"{selector!r} CSS rule does not reference --cyan or --cyan-d. "
        f"Identity surfaces must use the cyan brand to match the C919 "
        f"ETRAS standard. Rule body:\n{rule_body!r}"
    )


# ─── 1c. Active-signal SVG strokes/fills stay green; L4 final-release stays amber ───
# Codex R1 (PR #116) flagged: the cyan switch is for IDENTITY only.
# Active signal lines must still be #00e5a0 (green) and L4's final
# release output must still be #f5c518 (amber). Add a coarse guard so
# a future edit cannot accidentally swap signal colors for brand colors.


def test_fantui_circuit_active_signal_strokes_stay_green() -> None:
    """The L1-L3 controller-output rect strokes are explicitly
    `stroke="#00e5a0"`. There must be at least 3 such strokes
    in the SVG (one per output box: tls / etrac / eec_deploy or
    pls or pdu). This catches a future edit that accidentally
    converted active-signal green → cyan along with the brand."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    green_strokes = re.findall(r'stroke="#00e5a0"', body)
    assert len(green_strokes) >= 3, (
        f"only {len(green_strokes)} green (#00e5a0) strokes found — "
        f"L1-L3 active-signal output boxes / wires must stay green. "
        f"The cyan switch is for identity surfaces (header / badge / "
        f"info-card titles) only."
    )


def test_fantui_circuit_l4_final_release_stays_amber() -> None:
    """The L4 → throttle_unlock final release path is the only amber
    surface in the SVG. Confirm at least one `#f5c518` stroke remains
    (the L4 wire to throttle output box, plus the THROTTLE UNLOCK
    summary badge stroke)."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    amber_strokes = re.findall(r'stroke="#f5c518"', body)
    assert len(amber_strokes) >= 2, (
        f"only {len(amber_strokes)} amber (#f5c518) strokes found — "
        f"L4 final-release path must stay amber to convey the "
        f"deeper-than-L1/2/3 authority semantic."
    )


# ─── 2. Each L1-L4 input row carries a Chinese gloss next to it ───


@pytest.mark.parametrize(
    "label, gloss_keywords",
    [
        ("radio_altitude_ft", ["无线电", "高度"]),
        ("SW1 == True", ["机械开关", "SW1"]),
        ("reverser_inhibited", ["抑制"]),
        ("engine_running", ["发动机", "引擎"]),
        ("aircraft_on_ground", ["地面", "落地"]),
        ("tls_unlocked_ls", ["TLS", "位置反馈", "解锁"]),
        ("n1k &lt;", ["风扇", "转速", "N1k"]),
        ("tra_deg", ["油门", "TRA", "角度"]),
        ("deploy_90_percent_vdt", ["VDT", "位置传感器"]),
    ],
    ids=lambda v: v[:30] if isinstance(v, str) else "kw",
)
def test_fantui_circuit_input_node_has_chinese_gloss(
    label: str, gloss_keywords: list[str],
) -> None:
    """Each input node in the SVG must have a Chinese description
    text near it (within ~30px vertically). The C919 circuit puts a
    7.5px gloss line directly under each input name; fantui_circuit
    must do the same so non-coders can read it."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    # Find the first text element containing the label.
    label_pattern = re.escape(label)
    label_match = re.search(
        r'<text[^>]*?\by\s*=\s*"(\d+(?:\.\d+)?)"[^>]*>[^<]*?'
        + label_pattern,
        body,
    )
    assert label_match is not None, (
        f"input label {label!r} not found in SVG — diagram changed "
        f"shape; update the test."
    )
    label_y = float(label_match.group(1))
    # Look for any text element within +4 to +18 px of the label
    # whose content contains at least one of the gloss keywords.
    nearby_texts = re.findall(
        r'<text[^>]*?\by\s*=\s*"(\d+(?:\.\d+)?)"[^>]*>([^<]+)</text>',
        body,
    )
    glosses_found = [
        text for y_str, text in nearby_texts
        if 0 < float(y_str) - label_y <= 20
        and any(kw in text for kw in gloss_keywords)
    ]
    assert glosses_found, (
        f"no Chinese gloss within 20px below {label!r} (label y="
        f"{label_y}). Expected text containing one of {gloss_keywords}. "
        f"The C919 circuit standard puts a description line directly "
        f"under each input name so non-coders can read the diagram."
    )


# ─── 3. Each L1-L4 AND gate has a caption naming its purpose ───


@pytest.mark.parametrize(
    "gate_id, caption_keywords",
    [
        ("L1", ["TLS", "解锁"]),
        ("L2", ["ETRAC", "上电"]),
        ("L3", ["展开", "授权"]),
        ("L4", ["油门", "解锁"]),
    ],
)
def test_fantui_circuit_gate_has_caption(
    gate_id: str, caption_keywords: list[str],
) -> None:
    """Each L1-L4 AND gate must have a short Chinese caption next to
    it (within ~40px) explaining its row's purpose. Without this,
    the four AND gates are visually identical and the diagram doesn't
    self-document at-a-glance — a reader has to scroll to the
    info-card grid to learn what each gate does."""
    body = FANTUI_CIRCUIT.read_text(encoding="utf-8")
    # Find the L# gate label text — it has data-gate-id="L#".
    gate_label_pattern = (
        rf'<text[^>]*data-gate-id="{gate_id}"[^>]*'
        rf'\by\s*=\s*"(\d+(?:\.\d+)?)"'
        rf'|<text[^>]*\by\s*=\s*"(\d+(?:\.\d+)?)"[^>]*data-gate-id="'
        rf'{gate_id}"'
    )
    m = re.search(gate_label_pattern, body)
    assert m is not None, f"gate {gate_id} label not found"
    gate_y = float(m.group(1) or m.group(2))
    # Search any text within ±50px of the gate label for one of the
    # caption keywords.
    nearby = re.findall(
        r'<text[^>]*?\by\s*=\s*"(\d+(?:\.\d+)?)"[^>]*>([^<]+)</text>',
        body,
    )
    captions = [
        text for y_str, text in nearby
        if abs(float(y_str) - gate_y) <= 50
        and any(kw in text for kw in caption_keywords)
        and len(text.strip()) > 4  # filter out single-letter gate labels
    ]
    assert captions, (
        f"gate {gate_id} has no Chinese caption within 50px (gate y="
        f"{gate_y}). Expected text containing one of {caption_keywords}. "
        f"Add a small caption above/next to the gate so its purpose "
        f"reads at-a-glance."
    )
