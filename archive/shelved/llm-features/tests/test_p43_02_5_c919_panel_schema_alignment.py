"""P43-02.5 Delta 1 · C919 reference panel schema alignment test (static).

Asserts that every truth-tracked `data-node` value in
`#chain-topology-c919-etras` SVG ⊂ (adapter spec `components` id set ∪
`logic_nodes` id set). Annotation nodes (data-annotation="true") do NOT
participate in this assertion — they are decorative.

Blocks YAML/adapter-spec drift from silently breaking the hand-crafted
reference panel. Runtime DOM/event/POST flow coverage is handled by
Delta 3 (tests/e2e/test_p43_02_5_c919_panel_deploy_flow.py).

Whitelist authority: P43-00 v9 amend Delta 1 (pending Kogami approval).
"""
from __future__ import annotations

import re
from pathlib import Path

from well_harness.adapters.c919_etras_adapter import build_c919_etras_workbench_spec


CHAT_HTML = (
    Path(__file__).resolve().parent.parent
    / "src" / "well_harness" / "static" / "chat.html"
)

C919_SECTION_START = re.compile(r'id="chain-topology-c919-etras"')
C919_SECTION_END = re.compile(r'id="node-detail-panel"')


def _extract_c919_section(html: str) -> str:
    start_m = C919_SECTION_START.search(html)
    end_m = C919_SECTION_END.search(html)
    assert start_m is not None, "chain-topology-c919-etras not found in chat.html"
    assert end_m is not None, "node-detail-panel sentinel not found"
    assert start_m.start() < end_m.start()
    return html[start_m.start():end_m.start()]


def _collect_spec_ids() -> set[str]:
    spec = build_c919_etras_workbench_spec()
    component_ids = {c["id"] for c in spec.get("components", []) if c.get("id")}
    logic_node_ids = {ln["id"] for ln in spec.get("logic_nodes", []) if ln.get("id")}
    return component_ids | logic_node_ids


def test_c919_panel_data_nodes_subset_of_spec_ids():
    """Every data-node in c919 panel ⊂ spec.components ∪ spec.logic_nodes."""
    html = CHAT_HTML.read_text(encoding="utf-8")
    section = _extract_c919_section(html)
    # Match data-node="..." excluding data-annotation="true"
    data_nodes = re.findall(r'data-node="([^"]+)"', section)
    assert len(data_nodes) >= 22, (
        f"expected >=22 truth-tracked data-node values in c919 panel, got {len(data_nodes)}"
    )
    actual_ids = set(data_nodes)
    spec_ids = _collect_spec_ids()
    leaked = actual_ids - spec_ids
    assert not leaked, (
        f"panel data-node values leaked beyond adapter spec: {sorted(leaked)}\n"
        f"spec ids: {sorted(spec_ids)}"
    )


def test_c919_panel_annotation_nodes_absent_data_node():
    """data-annotation='true' elements must NOT have data-node attr (decoupling)."""
    html = CHAT_HTML.read_text(encoding="utf-8")
    section = _extract_c919_section(html)
    # Find all elements with data-annotation="true"
    # Simple regex: match opening <g|<polygon|<rect ... data-annotation="true" ... /> or >
    # and check the tag does NOT also have data-node
    annotation_tags = re.findall(
        r'<[^>]*data-annotation="true"[^>]*>', section
    )
    assert len(annotation_tags) >= 8, (
        f"expected >=8 annotation elements, got {len(annotation_tags)}"
    )
    for tag in annotation_tags:
        assert "data-node=" not in tag, (
            f"annotation element must not have data-node (truth/annotation mixing): {tag[:120]}"
        )


def test_c919_panel_defs_ids_scoped_with_c919_prefix():
    """All <defs> child id attrs must use c919- prefix (no global name leak)."""
    html = CHAT_HTML.read_text(encoding="utf-8")
    section = _extract_c919_section(html)
    # Extract the <defs>...</defs> block
    defs_match = re.search(r"<defs>(.*?)</defs>", section, re.DOTALL)
    assert defs_match is not None, "c919 panel must have <defs> block"
    defs = defs_match.group(1)
    ids = re.findall(r'id="([^"]+)"', defs)
    assert len(ids) >= 4, f"expected >=4 <defs> children with id, got {len(ids)}"
    leaks = [i for i in ids if not i.startswith("c919-")]
    assert not leaks, (
        f"<defs> child ids leak global namespace (v4.2 C11): {leaks}\n"
        "All marker/filter/clipPath/symbol/linearGradient ids must be c919- prefixed."
    )


def test_c919_panel_connection_lines_count():
    """Connection lines >= 40 (per v4.2 Exit #9)."""
    html = CHAT_HTML.read_text(encoding="utf-8")
    section = _extract_c919_section(html)
    line_count = len(re.findall(r'<line class="conn-line', section))
    assert line_count >= 40, f"expected >=40 conn-line, got {line_count}"


def test_c919_panel_viewbox_dimensions():
    """SVG viewBox matches v4.2 §2a: 1100 × 640."""
    html = CHAT_HTML.read_text(encoding="utf-8")
    section = _extract_c919_section(html)
    vb = re.search(r'viewBox="0 0 1100 640"', section)
    assert vb is not None, "c919 panel SVG viewBox must be '0 0 1100 640' per §2a"
