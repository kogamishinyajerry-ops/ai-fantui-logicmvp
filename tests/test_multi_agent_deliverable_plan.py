from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-deliverable-plan-for-project-manager.md"


def test_project_manager_deliverable_plan_uses_crew_hours_for_first_milestone() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")

    assert "给项目总管的原话" in text
    assert "第一阶段性里程碑" in text
    assert "施工队工时" in text
    assert "不使用自然日估算" in text
    assert "M1" in text

    effort_rows = [
        line
        for line in text.splitlines()
        if line.startswith("| M") or line.startswith("| S")
    ]
    assert effort_rows, "deliverable plan must include milestone/slice effort rows"
    assert all("施工队工时" in line for line in effort_rows)
    assert all("天" not in line for line in effort_rows)
    assert any(re.search(r"\|\s*M1\s*\|", line) for line in effort_rows)


def test_project_manager_deliverable_plan_lists_verifiable_m1_deliverables() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")

    required_fragments = [
        "docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json",
        "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
        "make verify-approved-candidate-task-queue-expansion-contract",
        "make verify-approved-candidate-task-queue-artifact",
        "make test",
        "tools/run_gsd_validation_suite.py --format json --skip notion_control_plane",
        "M1 交付物",
        "M1 验收口径",
        "/goal",
        "Objective",
        "Scope",
        "Constraints",
        "Done when",
        "Stop if",
    ]
    for fragment in required_fragments:
        assert fragment in text

    assert "最终成品" in text
    assert "阶段性可验收包" in text


def test_project_manager_deliverable_plan_declares_demo_reconstruction_first_visible_mvp() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")

    required_fragments = [
        "当前第一阶段可演示包",
        "demo.html 复刻 MVP 控制台",
        "/demo-reconstruction",
        "make demo-html-reconstruction-mvp",
        "make demo-html-reconstruction-browser-acceptance",
        "make multi-agent-merge-readiness",
        "multi_agent_merge_readiness_v0_1.json",
        "multi_agent_merge_readiness_v0_1.html",
        "20/20 节点",
        "23/23 连线",
        "5 个预设",
        "6 类状态输出",
    ]
    for fragment in required_fragments:
        assert fragment in text

    first_visible_index = text.index("当前第一阶段可演示包")
    m1_index = text.index("## M1 交付物")
    assert first_visible_index < m1_index
