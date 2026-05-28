"""Read-only DOCX-to-demo-circuit map for the thrust-reverser demo surface."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from well_harness.requirements_intake.logic_builder import THRUST_REVERSER_DEMO_CHAIN_CONTRACT


PAYLOAD_KIND = "ai-fantui-thrust-reverser-docx-sentence-circuit-map"
PAYLOAD_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOCX_SOURCE_RELATIVE_PATH = Path("uploads/20260409-thrust-reverser-control-logic.docx")
_DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", _DOCX_NS)).strip()


def _cell_text(cell: ET.Element) -> str:
    parts = []
    for paragraph in cell.findall(".//w:p", _DOCX_NS):
        text = _paragraph_text(paragraph)
        if text:
            parts.append(text)
    return " / ".join(parts)


def _read_docx(path: Path) -> tuple[list[str], list[list[list[str]]], str]:
    source_bytes = path.read_bytes()
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find("w:body", _DOCX_NS)
    if body is None:
        raise ValueError("DOCX word/document.xml is missing a body")

    paragraphs: list[str] = []
    tables: list[list[list[str]]] = []
    for child in body:
        tag_name = child.tag.rsplit("}", 1)[-1]
        if tag_name == "p":
            text = _paragraph_text(child)
            if text:
                paragraphs.append(text)
        elif tag_name == "tbl":
            rows: list[list[str]] = []
            for row in child.findall("w:tr", _DOCX_NS):
                rows.append([_cell_text(cell) for cell in row.findall("w:tc", _DOCX_NS)])
            tables.append(rows)

    return paragraphs, tables, hashlib.sha256(source_bytes).hexdigest()


def _contract_node_ids() -> set[str]:
    return {node["id"] for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]}


def _contract_wire_ids() -> set[str]:
    return {edge["id"] for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]}


def _sorted_known(values: set[str], known: set[str]) -> list[str]:
    return sorted(values & known)


def _nodes_for_text(text: str, known_nodes: set[str]) -> list[str]:
    matched: set[str] = set()
    rules: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
        (("SW1", "微动开关1"), ("sw1",)),
        (("SW2", "微动开关2"), ("sw2",)),
        (("6ft", "6英尺", "无线电高度"), ("radio_altitude_ft",)),
        (("地面状态", "着陆后"), ("aircraft_on_ground",)),
        (("发动机处于运行",), ("engine_running",)),
        (("N1k", "最大N1k"), ("n1k",)),
        (("EEC使能",), ("eec_enable",)),
        (("反推未被抑制", "非抑制", "未被抑制"), ("reverser_inhibited",)),
        (("DIU", "控制逻辑1", "工作逻辑1"), ("logic1", "tls115")),
        (("EICU", "540VDC", "控制逻辑2", "工作逻辑2"), ("logic2", "etrac_540v")),
        (("EEC将反推展开", "展开和收起指令", "控制逻辑3", "工作逻辑3"), ("logic3", "eec_deploy")),
        (("115VAC", "115 VAC", "TLS的供电"), ("tls115",)),
        (("TLS", "第三锁定系统"), ("tls115", "tls_unlocked")),
        (("VDT", "作动器的传感器", "90%", "反推完全展开"), ("vdt90",)),
        (("PLS", "主锁定系统"), ("pls_power",)),
        (("PDU", "电机"), ("pdu_motor",)),
        (("ETRAC", "电子反推作动控制器"), ("etrac_540v",)),
        (("反推电子锁", "最大反推", "控制逻辑4", "工作逻辑4"), ("logic4", "thr_lock")),
        (("TRA", "油门杆角度", "油门杆位于反推行程"), ("sw1", "sw2", "logic3", "logic4")),
    )
    for keywords, node_ids in rules:
        if any(keyword in text for keyword in keywords):
            matched.update(node_ids)
    return _sorted_known(matched, known_nodes)


def _role_for_anchor(anchor: str, text: str) -> str:
    if anchor.startswith("T"):
        return "设备/交联系统表"
    if anchor in {"P001", "P002"}:
        return "设备目录"
    if "输入信号" in text:
        return "输入信号目录"
    if "输出信号" in text:
        return "输出信号目录"
    if "需要监测" in text:
        return "监测信号目录"
    if "工作逻辑1" in text or anchor in {"P036", "P037"}:
        return "L1 条件"
    if "工作逻辑2" in text or anchor in {"P038", "P039"}:
        return "L2 条件"
    if "工作逻辑3" in text or anchor in {"P040", "P041"}:
        return "L3 条件"
    if "工作逻辑4" in text or anchor in {"P042", "P043"}:
        return "L4 条件"
    if "工作过程" in text or anchor == "P035":
        return "动作顺序"
    if "故障注入" in text:
        return "边界说明"
    return "源文档条目"


def _source_entries(
    paragraphs: list[str],
    tables: list[list[list[str]]],
    known_nodes: set[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for index, text in enumerate(paragraphs, start=1):
        anchor = f"P{index:03d}"
        entries.append(
            {
                "anchor": anchor,
                "entry_kind": "paragraph",
                "role": _role_for_anchor(anchor, text),
                "text": text,
                "node_ids": _nodes_for_text(text, known_nodes),
                "wire_ids": [],
                "authority": "source_docx",
            }
        )

    for table_index, rows in enumerate(tables, start=1):
        for row_index, cells in enumerate(rows, start=1):
            anchor = f"T{table_index}R{row_index}"
            text = " | ".join(cell for cell in cells if cell)
            entries.append(
                {
                    "anchor": anchor,
                    "entry_kind": "table_row",
                    "role": _role_for_anchor(anchor, text),
                    "text": text,
                    "node_ids": _nodes_for_text(text, known_nodes),
                    "wire_ids": [],
                    "authority": "source_docx",
                }
            )
    return entries


def _sequence_steps() -> list[dict[str, Any]]:
    return [
        {
            "anchor": "P035-S01",
            "title": "RA < 6 ft 与 SW1 进入 L1，TLS 115VAC 通电并解锁",
            "source_text": "飞机离地小于6ft时，DIU发出TLS解锁指令；微动开关1在[-1.4°, -6.2°]区间内触发，TLS通电后解锁。",
            "node_ids": ["radio_altitude_ft", "sw1", "reverser_inhibited", "logic1", "tls115", "tls_unlocked"],
            "wire_ids": [
                "wire_ra_logic1",
                "wire_sw1_logic1",
                "wire_inh_logic1",
                "wire_logic1_tls115",
                "wire_tls115_tls_unlocked",
            ],
            "folded_predicates": ["反推力装置未展开信号由 L1 条件折叠承载"],
        },
        {
            "anchor": "P035-S02",
            "title": "SW2、地面、发动机运行与 EEC 使能进入 L2，ETRAC 540VDC 通电",
            "source_text": "微动开关2在[-5°, -9.8°]区间内触发，EICU控制继电器，将540VDC供电给ETRAC。",
            "node_ids": ["aircraft_on_ground", "sw2", "engine_running", "eec_enable", "reverser_inhibited", "logic2", "etrac_540v"],
            "wire_ids": [
                "wire_ground_logic2",
                "wire_sw2_logic2",
                "wire_engine_logic2",
                "wire_eec_logic2",
                "wire_inh_logic2",
                "wire_logic2_etrac",
            ],
            "folded_predicates": [],
        },
        {
            "anchor": "P035-S03",
            "title": "TLS 已解锁、TRA <= -11.74° 与 N1K 限制进入 L3，输出 EEC/PLS/PDU",
            "source_text": "当油门杆角度小于-11.74°时，EEC将反推展开指令发送给ETRAC，ETRAC给左右PLS通电并将三相交流电供给电机。",
            "node_ids": [
                "tls_unlocked",
                "engine_running",
                "aircraft_on_ground",
                "n1k",
                "reverser_inhibited",
                "logic3",
                "eec_deploy",
                "pls_power",
                "pdu_motor",
            ],
            "wire_ids": [
                "wire_tls_unlocked_logic3",
                "wire_n1k_logic3",
                "wire_engine_logic3",
                "wire_ground_logic3",
                "wire_inh_logic3",
                "wire_logic3_eec",
                "wire_logic3_pls",
                "wire_logic3_pdu",
            ],
            "folded_predicates": ["TRA <= -11.74° 作为 L3 门限谓词展示"],
        },
        {
            "anchor": "P035-S04",
            "title": "PDU 电机带动滑动罩，VDT 到 90% 形成展开反馈",
            "source_text": "电机通电后带动反推滑动罩；当反推展开到90%，VDT90 反馈进入后级逻辑。",
            "node_ids": ["pdu_motor", "vdt90"],
            "wire_ids": ["wire_pdu_vdt90"],
            "folded_predicates": [],
        },
        {
            "anchor": "P035-S05",
            "title": "VDT90 与 L3 展开链路进入 L4，释放油门台反推电子锁",
            "source_text": "当反推展开到90%，油门台反推电子锁解锁（控制逻辑4），飞行员将反推力杆操纵至最大反推位。",
            "node_ids": ["vdt90", "logic3", "logic4", "thr_lock"],
            "wire_ids": ["wire_vdt90_logic4", "wire_logic3_logic4", "wire_logic4_thr_lock"],
            "folded_predicates": ["-32° < TRA < 0°、飞机在地面、发动机运行由 L4 条件行展示"],
        },
    ]


def build_thrust_reverser_docx_sentence_circuit_map(
    docx_path: Path | None = None,
) -> dict[str, Any]:
    """Build the read-only source coverage payload used by /demo-reconstruction."""

    source_path = docx_path or (REPO_ROOT / DEFAULT_DOCX_SOURCE_RELATIVE_PATH)
    paragraphs, tables, source_sha256 = _read_docx(source_path)
    known_nodes = _contract_node_ids()
    known_wires = _contract_wire_ids()
    entries = _source_entries(paragraphs, tables, known_nodes)
    steps = _sequence_steps()

    covered_nodes: set[str] = set()
    covered_wires: set[str] = set()
    for item in [*entries, *steps]:
        covered_nodes.update(item.get("node_ids", []))
        covered_wires.update(item.get("wire_ids", []))

    missing_nodes = sorted(known_nodes - covered_nodes)
    missing_wires = sorted(known_wires - covered_wires)
    if missing_nodes or missing_wires:
        raise ValueError(
            "DOCX sentence map does not cover the demo contract: "
            f"missing_nodes={missing_nodes}, missing_wires={missing_wires}"
        )

    table_row_count = sum(len(rows) for rows in tables)
    return {
        "kind": PAYLOAD_KIND,
        "version": PAYLOAD_VERSION,
        "source": {
            "path": str(DEFAULT_DOCX_SOURCE_RELATIVE_PATH),
            "absolute_path": str(source_path),
            "sha256": source_sha256,
            "paragraph_count": len(paragraphs),
            "table_count": len(tables),
            "table_row_count": table_row_count,
            "extraction": "stdlib_docx_xml",
            "authority": "original_uploaded_requirement_docx",
        },
        "circuit_contract": {
            "source": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["source"],
            "target": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["target"],
            "node_count": len(THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]),
            "wire_count": len(THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]),
            "node_ids": sorted(known_nodes),
            "wire_ids": sorted(known_wires),
        },
        "coverage": {
            "source_entry_count": len(entries),
            "paragraph_count": len(paragraphs),
            "table_row_count": table_row_count,
            "sequence_step_count": len(steps),
            "mapped_source_entry_count": sum(1 for item in entries if item["node_ids"]),
            "covered_node_count": len(covered_nodes),
            "covered_wire_count": len(covered_wires),
            "complete_demo_contract": True,
        },
        "source_entries": entries,
        "sequence_steps": steps,
        "boundary": {
            "controller_truth_modified": False,
            "truth_effect": "none",
            "fault_injection_scope": "P045 marks fault injection out of scope for this source-to-circuit slice.",
        },
    }
