#!/usr/bin/env python3
"""
Spec-to-SVG Code Generator for AI FANTUI LogicMVP.

Reads a control_system_spec_v1 JSON file and emits an SVG HTML fragment
representing the topology of the control logic system.

Usage:
    python -m well_harness.tools.generate_svg path/to/spec.json -o output.svg.html

The output is a self-contained HTML `<g>` element containing:
  - Node groups (<g class="node-group" data-node="...">) for every component
  - Connection lines (<line data-conn-from="..." data-conn-to="...">) for every edge
  - Color scheme: input=cyan, logic=orange, command=blue, final=green (legacy chat.html palette; chat.html shelved 2026-04-22)

Layout algorithm: hierarchical grid with topological sorting.
  - Level 0: root/input components (no logic condition sources them)
  - Level N+1: logic nodes whose all condition sources are in levels ≤ N
  - Fan-out components placed one level after their controlling logic node
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def spec_to_svg_source(
    spec: dict[str, Any],
    *,
    source_path: str = "",
    viewbox_width: float = 900,
    viewbox_height: float = 480,
) -> str:
    """
    Convert a parsed control_system_spec_v1 dict into an SVG HTML fragment.
    Returns the string content of the SVG group (no outer <svg> wrapper).
    """
    system_id = spec.get("system_id", "unknown")
    title = spec.get("title", system_id)

    # ── Build graph ─────────────────────────────────────────────────────────
    # node_infos[id] = {id, label, kind, state_shape, level, col, row}
    components = {c["id"]: c for c in spec.get("components", [])}
    logic_nodes = spec.get("logic_nodes", [])

    # Build edges: source_component → logic_node
    logic_conditions: dict[str, list[dict]] = defaultdict(list)
    for ln in logic_nodes:
        for cond in ln.get("conditions", []):
            logic_conditions[ln["id"]].append(cond)

    # downstream: logic_node → [component_ids]
    downstream_map: dict[str, list[str]] = {}
    for ln in logic_nodes:
        downstream_map[ln["id"]] = list(ln.get("downstream_component_ids", []))

    # Determine root components (used as condition sources but not as downstream targets)
    all_sources: set[str] = set()
    all_downstream: set[str] = set()
    for ln in logic_nodes:
        for cond in logic_conditions[ln["id"]]:
            all_sources.add(cond["source_component_id"])
        all_downstream.update(downstream_map.get(ln["id"], []))
    root_component_ids = sorted(all_sources - all_downstream)

    # ── Level assignment (Kahn-style BFS) ──────────────────────────────────
    # A logic node's level = 1 + max level of its upstream components
    # A component's level = 1 + max level of its upstream logic node
    node_levels: dict[str, int] = {}

    def component_level(comp_id: str) -> int:
        if comp_id in node_levels:
            return node_levels[comp_id]
        if comp_id in root_component_ids:
            node_levels[comp_id] = 0
            return 0
        # Find which logic nodes produce this as downstream
        for ln_id, downstream in downstream_map.items():
            if comp_id in downstream:
                lvl = logic_node_level(ln_id) + 1
                node_levels[comp_id] = lvl
                return lvl
        node_levels[comp_id] = 0
        return 0

    def logic_node_level(ln_id: str) -> int:
        if ln_id in node_levels:
            return node_levels[ln_id]
        conds = logic_conditions.get(ln_id, [])
        if not conds:
            node_levels[ln_id] = 1
            return 1
        max_src_lvl = max(component_level(c["source_component_id"]) for c in conds)
        lvl = max_src_lvl + 1
        node_levels[ln_id] = lvl
        return lvl

    # Assign levels to all logic nodes
    for ln in logic_nodes:
        logic_node_level(ln["id"])

    # Assign levels to all components
    for comp_id in components:
        component_level(comp_id)

    # ── Grid layout ─────────────────────────────────────────────────────────
    # Group nodes by level
    level_groups: dict[int, list[str]] = defaultdict(list)
    for node_id, lvl in node_levels.items():
        level_groups[lvl].append(node_id)

    # Sort nodes within each level by a stable key (kind priority + label)
    KIND_PRIORITY = {
        "sensor": 0,
        "pilot_input": 1,
        "switch": 2,
        "state": 3,
        "parameter": 4,
        "power": 5,
        "feedback": 6,
        "command": 7,
        "logic": 8,
    }

    def sort_key(node_id: str) -> tuple[int, str]:
        kind = ""
        if node_id in components:
            kind = components[node_id].get("kind", "command")
        elif node_id in {ln["id"] for ln in logic_nodes}:
            kind = "logic"
        return (KIND_PRIORITY.get(kind, 9), node_id)

    for lvl in level_groups:
        level_groups[lvl].sort(key=sort_key)

    # Determine column count (one column per level)
    max_level = max(level_groups.keys()) if level_groups else 0
    num_cols = max_level + 1

    # Determine row height and starting positions
    NODE_HEIGHT = 36
    NODE_MIN_WIDTH = 72
    LABEL_PADDING = 8
    ROW_SPACING = 14
    COL_WIDTH = 140
    COL_START_X = 10
    ROW_START_Y = 10

    # Calculate row positions
    row_positions: dict[str, float] = {}
    current_row: dict[int, int] = {}  # level → row offset within level

    for lvl in sorted(level_groups):
        nodes = level_groups[lvl]
        current_row[lvl] = 0
        for node_id in nodes:
            row_positions[node_id] = ROW_START_Y + current_row[lvl] * (NODE_HEIGHT + ROW_SPACING)
            current_row[lvl] += 1

    # Calculate column (x) positions
    col_positions: dict[str, float] = {}
    for lvl in sorted(level_groups):
        x = COL_START_X + lvl * COL_WIDTH
        for node_id in level_groups[lvl]:
            col_positions[node_id] = x

    # Calculate node widths based on label
    def node_width(node_id: str) -> float:
        label = ""
        if node_id in components:
            label = components[node_id].get("label", node_id)
        else:
            for ln in logic_nodes:
                if ln["id"] == node_id:
                    label = ln.get("label", node_id)
                    break
        return max(NODE_MIN_WIDTH, len(label) * 7 + LABEL_PADDING * 2)

    # ── Generate SVG content ─────────────────────────────────────────────────
    lines: list[str] = []

    # SVG viewBox and definitions
    lines.append(f'  <svg xmlns="http://www.w3.org/2000/svg" '
                 f'viewBox="0 0 {viewbox_width} {viewbox_height}" '
                 f'width="{viewbox_width}" height="{viewbox_height}">')
    lines.append("")
    lines.append('  <defs>')
    lines.append('    <marker id="arrow-professional" viewBox="0 0 10 10" '
                'refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    lines.append('      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4dc8ff" opacity="0.8"/>')
    lines.append("    </marker>")
    lines.append('    <marker id="arrow-green" viewBox="0 0 10 10" '
                'refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    lines.append('      <path d="M 0 0 L 10 5 L 0 10 z" fill="#53ff92" opacity="0.9"/>')
    lines.append("    </marker>")
    lines.append("  </defs>")
    lines.append("")

    # ── Zone backgrounds ────────────────────────────────────────────────────
    # Input zone (level 0)
    input_zone_width = COL_WIDTH - 10
    lines.append(f'  <rect class="zone-bg" x="0" y="0" '
                 f'width="{input_zone_width}" height="{viewbox_height}" '
                 f'fill="rgba(74,144,217,0.03)" rx="4"/>')

    # L1/L2 unlock zone
    if max_level >= 1:
        unlock_zone_x = COL_START_X + 1 * COL_WIDTH
        lines.append(f'  <rect class="zone-bg" x="{unlock_zone_x}" y="0" '
                     f'width="{COL_WIDTH}" height="{viewbox_height}" '
                     f'fill="rgba(255,180,0,0.02)" rx="4"/>')

    # L3 fanout zone
    if max_level >= 2:
        fanout_zone_x = COL_START_X + 2 * COL_WIDTH
        lines.append(f'  <rect class="zone-bg" x="{fanout_zone_x}" y="0" '
                     f'width="{COL_WIDTH * (max_level - 1)}" height="{viewbox_height}" '
                     f'fill="rgba(0,200,100,0.02)" rx="4"/>')

    # Zone labels
    lines.append(f'  <text x="5" y="14" class="section-label">输入条件</text>')
    lines.append(f'  <text x="{COL_START_X + 1 * COL_WIDTH + 5}" y="14" class="section-label">逻辑链路</text>')

    # ── Connection lines ─────────────────────────────────────────────────────
    # Build connection list: (from_id, to_id, kind)
    connections: list[tuple[str, str, str]] = []
    for ln in logic_nodes:
        ln_id = ln["id"]
        for cond in logic_conditions.get(ln_id, []):
            src_id = cond["source_component_id"]
            connections.append((src_id, ln_id, "input"))
        for downstream_id in downstream_map.get(ln_id, []):
            connections.append((ln_id, downstream_id, "logic"))

    for from_id, to_id, kind in connections:
        x1 = _line_x1(from_id, col_positions, node_width)
        y1 = _line_y(from_id, row_positions, NODE_HEIGHT)
        x2 = _line_x2(to_id, col_positions, node_width)
        y2 = _line_y(to_id, row_positions, NODE_HEIGHT)

        kind_class = "conn-input" if kind == "input" else "conn-logic"
        marker = 'marker-end="url(#arrow-professional)"'
        cls = f"conn-line {kind_class}"

        if x1 == x2 or y1 == y2:
            lines.append(f'  <line data-conn-from="{from_id}" data-conn-to="{to_id}" '
                         f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                         f'class="{cls}" {marker}/>')
        else:
            # Polyline for bent paths
            mid_x = (x1 + x2) / 2
            lines.append(f'  <polyline data-conn-from="{from_id}" data-conn-to="{to_id}" '
                         f'points="{x1:.1f},{y1:.1f} {mid_x:.1f},{y1:.1f} {mid_x:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" '
                         f'class="{cls}" fill="none" {marker}/>')

    lines.append("")

    # ── Node groups ──────────────────────────────────────────────────────────
    def node_tag(kind: str) -> str:
        tag_map = {
            "sensor": "SNS",
            "pilot_input": "IN",
            "switch": "SW",
            "state": "STS",
            "parameter": "Prm",
            "power": "PWR",
            "feedback": "Fdbk",
            "command": "CMD",
            "logic": "LOG",
            "final": "FIN",
        }
        return tag_map.get(kind, kind[:3].upper())

    def node_cls(kind: str) -> str:
        cls_map = {
            "sensor": "input-node-svg",
            "pilot_input": "input-node-svg",
            "switch": "input-node-svg",
            "state": "input-node-svg",
            "parameter": "input-node-svg",
            "power": "command-node-svg",
            "feedback": "sensor-node-svg",
            "command": "command-node-svg",
            "logic": "logic-node-svg",
        }
        return cls_map.get(kind, "chain-node-svg")

    def node_kind_type_tag(kind: str) -> str:
        if kind in ("sensor", "pilot_input", "switch", "state", "parameter"):
            return "input"
        if kind == "logic":
            return "logic"
        if kind in ("power", "feedback"):
            return "intermediate"
        if kind == "command":
            return "command"
        return "unknown"

    # Root components
    for comp_id in root_component_ids:
        if comp_id not in components:
            continue
        comp = components[comp_id]
        x = col_positions.get(comp_id, COL_START_X)
        y = row_positions.get(comp_id, 10)
        w = node_width(comp_id)
        h = NODE_HEIGHT
        label = comp.get("label", comp_id)
        kind = comp.get("kind", "sensor")
        cls = node_cls(kind)
        type_tag = node_tag(kind)
        node_type = node_kind_type_tag(kind)

        lines.append(f'  <g class="node-group" data-node="{comp_id}" data-node-type="{node_type}">')
        lines.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="6" class="chain-node-svg {cls}" data-node="{comp_id}"/>')
        lines.append(f'    <text x="{(x + w/2):.1f}" y="{(y + h/2 - 3):.1f}" '
                     f'class="chain-node-label" text-anchor="middle">{label}</text>')
        lines.append(f'    <text x="{(x + w - 4):.1f}" y="{(y + 12):.1f}" '
                     f'class="node-type-tag" text-anchor="end">{type_tag}</text>')
        lines.append(f'    <text x="{(x + w/2):.1f}" y="{(y + h/2 + 10):.1f}" '
                     f'class="chain-node-value" text-anchor="middle" '
                     f'data-value-for="{comp_id}">—</text>')
        lines.append("  </g>")

    # Logic nodes and their downstream components
    drawn_components = set(root_component_ids)

    for ln in logic_nodes:
        ln_id = ln["id"]
        x = col_positions.get(ln_id, COL_START_X + 100)
        y = row_positions.get(ln_id, 100)
        w = node_width(ln_id)
        h = NODE_HEIGHT
        label = ln.get("label", ln_id)
        cls = node_cls("logic")
        type_tag = node_tag("logic")

        lines.append(f'  <g class="node-group" data-node="{ln_id}" data-node-type="logic">')
        lines.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="6" class="chain-node-svg {cls}" data-node="{ln_id}"/>')
        lines.append(f'    <text x="{(x + w/2):.1f}" y="{(y + h/2 - 3):.1f}" '
                     f'class="chain-node-label" text-anchor="middle">{label}</text>')
        lines.append(f'    <text x="{(x + w - 4):.1f}" y="{(y + 12):.1f}" '
                     f'class="node-type-tag" text-anchor="end">{type_tag}</text>')
        lines.append(f'    <text x="{(x + w/2):.1f}" y="{(y + h/2 + 10):.1f}" '
                     f'class="chain-node-value" text-anchor="middle" '
                     f'data-value-for="{ln_id}">—</text>')
        lines.append("  </g>")

        # Downstream components of this logic node
        for downstream_id in downstream_map.get(ln_id, []):
            if downstream_id in drawn_components:
                continue
            drawn_components.add(downstream_id)
            if downstream_id not in components:
                continue
            comp = components[downstream_id]
            x2 = col_positions.get(downstream_id, x + COL_WIDTH)
            y2 = row_positions.get(downstream_id, y)
            w2 = node_width(downstream_id)
            h2 = NODE_HEIGHT
            label2 = comp.get("label", downstream_id)
            kind2 = comp.get("kind", "command")
            cls2 = node_cls(kind2)
            type_tag2 = node_tag(kind2)
            node_type2 = node_kind_type_tag(kind2)

            lines.append(f'  <g class="node-group" data-node="{downstream_id}" data-node-type="{node_type2}">')
            lines.append(f'    <rect x="{x2:.1f}" y="{y2:.1f}" width="{w2:.1f}" height="{h2:.1f}" '
                         f'rx="6" class="chain-node-svg {cls2}" data-node="{downstream_id}"/>')
            lines.append(f'    <text x="{(x2 + w2/2):.1f}" y="{(y2 + h2/2 - 3):.1f}" '
                         f'class="chain-node-label" text-anchor="middle">{label2}</text>')
            lines.append(f'    <text x="{(x2 + w2 - 4):.1f}" y="{(y2 + 12):.1f}" '
                         f'class="node-type-tag" text-anchor="end">{type_tag2}</text>')
            lines.append(f'    <text x="{(x2 + w2/2):.1f}" y="{(y2 + h2/2 + 10):.1f}" '
                         f'class="chain-node-value" text-anchor="middle" '
                         f'data-value-for="{downstream_id}">—</text>')
            lines.append("  </g>")

    lines.append("</svg>")

    return "\n".join(lines)


def write_svg_from_spec(
    spec_path: str | Path,
    output_path: str | Path,
    *,
    source_path: str | None = None,
) -> None:
    """Read spec_path, write SVG HTML fragment to output_path."""
    spec_path = Path(spec_path)
    output_path = Path(output_path)

    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    try:
        spec = json.loads(spec_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {spec_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    svg = spec_to_svg_source(spec, source_path=str(spec_path))

    # Wrap in a comment header
    wrapped = (
        f"<!--\n"
        f"  Auto-generated SVG topology fragment\n"
        f"  System: {spec.get('system_id', 'unknown')}\n"
        f"  Source: {spec_path}\n"
        f"  Generated: {datetime.datetime.now().isoformat()}\n"
        f"  DO NOT EDIT BY HAND — re-run generate_svg.py\n"
        f"-->\n"
        f"{svg}\n"
    )

    try:
        output_path.write_text(wrapped)
    except OSError as exc:
        print(f"ERROR: failed to write {output_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"Wrote: {output_path}")


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _line_x1(node_id: str, col_positions: dict, node_widths) -> float:
    # node_widths is a callable(node_id) -> float
    return col_positions.get(node_id, 10) + node_widths(node_id)


def _line_x2(node_id: str, col_positions: dict, node_widths) -> float:
    return col_positions.get(node_id, 10)


def _line_y(node_id: str, row_positions: dict, node_height: float) -> float:
    base_y = row_positions.get(node_id, 10)
    return base_y + node_height / 2


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an SVG topology HTML fragment from a control_system_spec_v1 JSON file.",
    )
    parser.add_argument("spec", type=Path, help="Path to the control_system_spec_v1 JSON file")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output path (default: <system_id>_topology.svg.html next to spec)",
    )
    args = parser.parse_args()

    output = args.output
    if output is None:
        stem = args.spec.stem
        output = args.spec.parent / f"{stem}_topology.svg.html"

    write_svg_from_spec(args.spec, output)


if __name__ == "__main__":
    _main()
