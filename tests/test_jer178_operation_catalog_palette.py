from __future__ import annotations

from pathlib import Path

from well_harness.editable_control_model import (  # type: ignore[import-untyped]
    build_reference_editable_control_model,
    validate_editable_control_model,
)
from well_harness.editable_workbench_run import (  # type: ignore[import-untyped]
    canonicalize_workbench_ui_draft,
)


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "well_harness" / "static"


APPROVED_OPS = ("and", "or", "compare", "between", "delay", "latch")


def _html() -> str:
    return (STATIC / "workbench.html").read_text(encoding="utf-8")


def _js() -> str:
    return (STATIC / "workbench.js").read_text(encoding="utf-8")


def _css() -> str:
    return (STATIC / "workbench.css").read_text(encoding="utf-8")


def test_operation_catalog_palette_exposes_only_approved_sandbox_ops() -> None:
    html = _html()
    assert 'id="workbench-op-catalog"' in html
    for op in APPROVED_OPS:
        assert f'data-op-catalog-op="{op}"' in html
    assert "python" not in html.lower()
    assert "import" not in html.lower().split('id="workbench-op-catalog"', 1)[1].split("</aside>", 1)[0]


def test_operation_catalog_js_preserves_sandbox_contract_metadata() -> None:
    js = _js()
    assert 'const editableOperationCatalogVersion = "editable-control-ops.v1"' in js
    assert "const approvedOperationCatalog = {" in js
    assert "function buildOperationCatalogSummary()" in js
    assert "operation_catalog: operationCatalog" in js
    assert "operation_catalog_checksum" in js
    assert "portContractForCatalogNode(nodeId, catalogEntry)" in js
    assert 'sourceRef: `ui_draft.op_catalog.${catalogEntry.op}.${nodeId}`' in js
    assert 'truth_effect: "none"' in js


def test_operation_catalog_palette_has_stable_compact_styles() -> None:
    css = _css()
    assert ".workbench-op-catalog" in css
    assert ".workbench-op-catalog button[aria-pressed=\"true\"]" in css
    assert ".workbench-op-catalog-status" in css


def test_catalog_derived_node_canonicalizes_as_truth_neutral_sandbox_model() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "draft_node_1",
                "label": "Draft Between window",
                "op": "between",
                "draftNode": True,
                "op_catalog_entry": "between",
                "op_catalog_version": "editable-control-ops.v1",
                "sourceRef": "ui_draft.op_catalog.between.draft_node_1",
                "port_contract": {
                    "input_signal_id": "draft_node_1_between_input",
                    "output_signal_id": "draft_node_1_between_output",
                    "value_type": "number",
                    "required": True,
                    "source_ref": "ui_draft.op_catalog.between.port_contract",
                    "truth_effect": "none",
                },
            }
        ],
        "typed_ports": [
            {
                "id": "draft_node_1:out",
                "node_id": "draft_node_1",
                "direction": "out",
                "signal_id": "draft_node_1_between_output",
                "value_type": "number",
                "unit": "",
                "required": True,
                "source_ref": "ui_draft.op_catalog.between.port_contract",
                "truth_effect": "none",
            }
        ],
        "edges": [],
        "operation_catalog": {
            "version": "editable-control-ops.v1",
            "approved_ops": list(APPROVED_OPS),
            "selected_op": "between",
            "truth_effect": "none",
        },
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    node = next(item for item in model["nodes"] if item["id"] == "draft_node_1")
    ports = {port["id"]: port for port in model["ports"]}
    assert node["op"] == "between"
    assert node["source_ref"] == "ui_draft.op_catalog.between.draft_node_1"
    assert ports["draft_node_1:out"]["signal_id"] == "draft_node_1_between_output"
    assert ports["draft_node_1:out"]["value_type"] == "number"
    assert ports["draft_node_1:out"]["required"] is True
    assert model["boundaries"]["truth_level_impact"] == "none"
