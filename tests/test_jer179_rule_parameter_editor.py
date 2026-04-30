from __future__ import annotations

from pathlib import Path

import pytest

from well_harness.editable_control_model import (  # type: ignore[import-untyped]
    build_reference_editable_control_model,
    validate_editable_control_model,
)
from well_harness.editable_workbench_run import (  # type: ignore[import-untyped]
    WorkbenchGraphValidationError,
    canonicalize_workbench_ui_draft,
)


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "well_harness" / "static"


def _html() -> str:
    return (STATIC / "workbench.html").read_text(encoding="utf-8")


def _js() -> str:
    return (STATIC / "workbench.js").read_text(encoding="utf-8")


def _css() -> str:
    return (STATIC / "workbench.css").read_text(encoding="utf-8")


def test_rule_parameter_editor_controls_are_sandbox_only() -> None:
    html = _html()
    assert 'id="workbench-rule-parameter-editor"' in html
    assert 'id="workbench-rule-name"' in html
    assert 'id="workbench-rule-source-signal"' in html
    assert 'id="workbench-rule-comparison"' in html
    assert 'id="workbench-rule-threshold"' in html
    assert 'id="workbench-apply-rule-parameter-btn"' in html
    assert "Local sandbox rule only. Truth effect: none." in html


def test_rule_parameter_editor_exports_archive_metadata() -> None:
    js = _js()
    assert "function normalizeNodeDraftRule" in js
    assert "function applySelectedRuleParameter" in js
    assert "function buildRuleParameterSummary" in js
    assert "rule_parameter_summary: ruleParameterSummary" in js
    assert "rule_parameter_summary_checksum" in js
    assert 'truth_effect: "none"' in js


def test_rule_parameter_editor_has_stable_layout_styles() -> None:
    css = _css()
    assert ".workbench-rule-parameter-editor" in css
    assert ".workbench-rule-parameter-grid" in css


def test_ui_rule_parameters_canonicalize_into_editable_model_rules() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "draft_node_1",
                "label": "Draft compare threshold",
                "op": "compare",
                "draftNode": True,
                "sourceRef": "ui_draft.rule_parameters.draft_node_1",
                "rules": [
                    {
                        "name": "draft_tra_threshold",
                        "source_signal_id": "tra_deg",
                        "comparison": ">=",
                        "threshold_value": -11.74,
                        "truth_effect": "none",
                    }
                ],
            }
        ],
        "edges": [],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    node = next(item for item in model["nodes"] if item["id"] == "draft_node_1")
    assert node["op"] == "compare"
    assert node["rules"] == [
        {
            "name": "draft_tra_threshold",
            "source_signal_id": "tra_deg",
            "comparison": ">=",
            "threshold_value": -11.74,
        }
    ]
    assert model["boundaries"]["truth_level_impact"] == "none"


def test_ui_rule_parameters_reject_unsupported_comparison() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "draft_node_1",
                "label": "Draft unsafe rule",
                "op": "compare",
                "draftNode": True,
                "rules": [
                    {
                        "name": "unsafe_rule",
                        "source_signal_id": "tra_deg",
                        "comparison": "python_eval",
                        "threshold_value": "x",
                        "truth_effect": "none",
                    }
                ],
            }
        ],
        "edges": [],
    }

    with pytest.raises(WorkbenchGraphValidationError) as exc_info:
        canonicalize_workbench_ui_draft(base, draft)

    report = exc_info.value.validation_report
    assert report["truth_level_impact"] == "none"
    assert report["categories"]["unsafe_op"][0]["code"] == "unsupported_rule_comparison"
