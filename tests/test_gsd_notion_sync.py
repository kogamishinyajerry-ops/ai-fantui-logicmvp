import argparse
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.gsd_notion_sync import (
    CommandResult,
    NotionClient,
    ReviewSnapshot,
    build_gate_update_properties,
    build_current_review_brief,
    render_current_review_brief_blocks,
    render_dashboard_blocks,
    render_freeze_packet_blocks,
    render_status_page_blocks,
    upsert_dashboard_snapshot_section,
    upsert_freeze_packet_snapshot_section,
    retire_legacy_review_artifacts,
    fetch_review_snapshot,
    fetch_review_snapshot_from_pages,
    fetch_review_snapshot_from_dashboard_page,
    build_superseded_gap_fix_plan,
    clip,
    write_notion_outcome,
    resolve_superseded_failure_gaps,
    render_repo_coordination_plan_markdown,
    derive_compact_success_summary,
    derive_compact_success_summary_from_text,
    build_fallback_run_snapshot,
    ensure_live_active_pages,
    fetch_review_snapshot_from_repo_docs,
    should_prefer_page_snapshot,
    summarize_results,
    sync_repo_documents,
    handle_run,
    handle_prepare_opus_review,
    upsert_managed_markdown_section,
)


class GsdNotionSyncTests(unittest.TestCase):
    def test_summarize_successful_results(self):
        summary = summarize_results(
            [
                CommandResult(
                    command="python -m unittest",
                    returncode=0,
                    stdout="OK",
                    stderr="",
                    started_at="2026-04-09T00:00:00+00:00",
                    ended_at="2026-04-09T00:00:01+00:00",
                )
            ]
        )

        self.assertTrue(summary.succeeded)
        self.assertEqual(summary.status, "Succeeded")
        self.assertEqual(summary.qa_result, "PASS")
        self.assertIsNone(summary.first_failed_command)
        self.assertIn("python -m unittest", summary.output_digest)

    def test_summarize_failed_results(self):
        summary = summarize_results(
            [
                CommandResult(
                    command="python -m unittest",
                    returncode=1,
                    stdout="",
                    stderr="FAIL",
                    started_at="2026-04-09T00:00:00+00:00",
                    ended_at="2026-04-09T00:00:01+00:00",
                )
            ]
        )

        self.assertFalse(summary.succeeded)
        self.assertEqual(summary.status, "Failed")
        self.assertEqual(summary.qa_result, "FAIL")
        self.assertEqual(summary.first_failed_command, "python -m unittest")
        self.assertIn("stderr:", summary.output_digest)

    def test_derive_compact_success_summary_from_validation_results(self):
        results = [
            CommandResult(
                command="python3 -m unittest discover -s tests -p test_*.py",
                returncode=0,
                stdout="",
                stderr="Ran 187 tests in 21.157s\n\nOK",
                started_at="2026-04-10T00:00:00+00:00",
                ended_at="2026-04-10T00:00:05+00:00",
            ),
            CommandResult(
                command="python3 tools/demo_path_smoke.py --format json",
                returncode=0,
                stdout='{"completed_scenarios": 10, "failed_scenario": null, "scenario_count": 10}',
                stderr="",
                started_at="2026-04-10T00:00:05+00:00",
                ended_at="2026-04-10T00:00:10+00:00",
            ),
        ]

        summary = derive_compact_success_summary(results)

        self.assertEqual("187 tests OK, 10 demo smoke scenarios pass, and 2/2 shared validation checks pass.", summary)

    def test_derive_compact_success_summary_from_text(self):
        text = """
Ran 189 tests in 20.897s
{
  "command_count": 8,
  "completed_scenarios": 10
}
"""

        summary = derive_compact_success_summary_from_text(text)

        self.assertEqual("189 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.", summary)

    def test_ensure_live_active_pages_recreates_archived_targets_and_persists_config(self):
        config = {
            "pages": {
                "dashboard": "dashboard-page",
                "status": "archived-status",
                "opus_brief": "live-brief",
                "freeze_packet": "archived-freeze",
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "notion_control_plane.json"
            config_path.write_text("{}", encoding="utf-8")

            client = unittest.mock.Mock()
            client.get_page.side_effect = [
                {"archived": False, "in_trash": False},
                {"archived": True, "in_trash": True},
                {"archived": False, "in_trash": False},
                {"archived": False, "in_trash": False},
                {"archived": True, "in_trash": True},
                {"archived": False, "in_trash": False},
            ]
            client.create_child_page.side_effect = ["new-status", "new-freeze"]

            replacements = ensure_live_active_pages(client, config, config_path=config_path)

            self.assertEqual(
                {
                    "status": {"old_id": "archived-status", "new_id": "new-status"},
                    "freeze_packet": {"old_id": "archived-freeze", "new_id": "new-freeze"},
                },
                replacements,
            )
            self.assertEqual("new-status", config["pages"]["status"])
            self.assertEqual("new-freeze", config["pages"]["freeze_packet"])
            persisted = config_path.read_text(encoding="utf-8")
            self.assertIn("new-status", persisted)
            self.assertIn("new-freeze", persisted)

    def test_clip_preserves_short_text_and_truncates_long_text(self):
        self.assertEqual("short", clip("short", limit=10))
        clipped = clip("x" * 30, limit=20)
        self.assertLessEqual(len(clipped), 20)
        self.assertIn("truncated", clipped)

    def test_build_current_review_brief_targets_stale_gap_adjudication(self):
        snapshot = ReviewSnapshot(
            active_phase="P1 建立 Notion + GitHub 的 Opus 审查闭环",
            active_phase_goal="让主观审查完全通过 Notion 页面 + GitHub 仓库完成",
            active_phase_summary="P1 已转成 Notion + GitHub 的 Opus 审查闭环",
            latest_verified_plan="P1-01 建立自动执行 / QA 回写闭环",
            latest_success_run="GitHub GSD automation 24149997671",
            latest_failed_run="GitHub GSD automation 24148804383",
            latest_passing_qa="GitHub GSD automation 24149997671 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Standby",
            ready_task_id="task-page-id",
            ready_task="在 Notion 中手动触发 Opus 4.6 审查",
            open_gap_titles=(
                "Automation failure: P1-01 建立自动执行 / QA 回写闭环",
                "Automation failure: P1-01 建立自动执行 / QA 回写闭环",
            ),
            stale_gap_titles=(
                "Automation failure: P1-01 建立自动执行 / QA 回写闭环",
                "Automation failure: P1-01 建立自动执行 / QA 回写闭环",
            ),
        )
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }

        brief = build_current_review_brief(snapshot, config)

        self.assertTrue(brief.review_required)
        self.assertEqual("P1 phase readiness + 旧失败 Gap 裁决", brief.intervention_kind)
        self.assertIn("旧失败遗留", brief.why_now)
        self.assertIn("不要引用任何本地终端文件", brief.copy_prompt)
        self.assertIn("resolve / merge", brief.copy_prompt)

    def test_build_current_review_brief_targets_failure_triage_when_no_success_cover(self):
        snapshot = ReviewSnapshot(
            active_phase="P1 建立 Notion + GitHub 的 Opus 审查闭环",
            active_phase_goal="让主观审查完全通过 Notion 页面 + GitHub 仓库完成",
            active_phase_summary="P1 正在执行",
            latest_verified_plan="P1-01 建立自动执行 / QA 回写闭环",
            latest_success_run=None,
            latest_failed_run="GitHub GSD automation 24148804383",
            latest_passing_qa=None,
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Standby",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=("Automation failure: P1-01 建立自动执行 / QA 回写闭环",),
            stale_gap_titles=(),
        )
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }

        brief = build_current_review_brief(snapshot, config)

        self.assertTrue(brief.review_required)
        self.assertEqual("失败阻塞分流审查", brief.intervention_kind)
        self.assertIn("当前仍存在未解决的 open gap", brief.why_now)
        self.assertIn("最小修复路径", brief.copy_prompt)

    def test_build_current_review_brief_skips_review_when_gate_is_not_waiting(self):
        snapshot = ReviewSnapshot(
            active_phase="P3 减少控制面漂移",
            active_phase_goal="保持自动开发闭环稳定",
            active_phase_summary="P3 正在推进",
            latest_verified_plan="P3-02 统一验证入口",
            latest_success_run="Local hardening: unify validation entrypoint",
            latest_failed_run=None,
            latest_passing_qa="Local hardening: unify validation entrypoint QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }

        brief = build_current_review_brief(snapshot, config)

        self.assertFalse(brief.review_required)
        self.assertEqual("当前无需 Opus 审查", brief.intervention_kind)
        self.assertIn("当前无需触发 Notion AI Opus 4.6", brief.copy_prompt)

    def test_build_current_review_brief_phase_closeout_mentions_current_phase(self):
        snapshot = ReviewSnapshot(
            active_phase="P5 Demo Polish And Edge-Case Hardening",
            active_phase_goal="把 demo 的残余边缘风险收口成 GitHub 可验证证据",
            active_phase_summary="P5 已覆盖 smoke、preset 和 toggle hardening",
            latest_verified_plan="P5-04 快速条件 toggle smoke sweep",
            latest_success_run="GitHub GSD automation 24172898166",
            latest_failed_run="GitHub GSD automation 24148804383",
            latest_passing_qa="GitHub GSD automation 24172898166 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Awaiting Opus 4.6",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }

        brief = build_current_review_brief(snapshot, config, force_review=True)

        self.assertTrue(brief.review_required)
        self.assertEqual("Phase 收口与下一步优先级审查", brief.intervention_kind)
        self.assertIn("P5 Demo Polish And Edge-Case Hardening 是否可以正式收口", brief.why_now)

    def test_build_gate_update_properties_preserves_decision_notes_when_not_activating_gate(self):
        brief = build_current_review_brief(
            ReviewSnapshot(
                active_phase="P3 减少控制面漂移",
                active_phase_goal="保持自动开发闭环稳定",
                active_phase_summary="P3 正在推进",
                latest_verified_plan="P3-02 统一验证入口",
                latest_success_run="Local hardening: unify validation entrypoint",
                latest_failed_run=None,
                latest_passing_qa="Local hardening: unify validation entrypoint QA",
                gate_page_id="gate-page-id",
                gate_name="OPUS-4.6 周期审查 Gate",
                gate_status="Approved",
                ready_task_id=None,
                ready_task=None,
                open_gap_titles=(),
                stale_gap_titles=(),
            ),
            {
                "urls": {
                    "github_repo": "https://github.com/example/repo",
                    "github_actions": "https://github.com/example/repo/actions",
                }
            },
        )

        properties = build_gate_update_properties(brief, activate_gate=False)

        self.assertNotIn("Decision Notes", properties)
        self.assertIn("继续自动开发", properties["Next Action"]["rich_text"][0]["text"]["content"])

    def test_render_dashboard_blocks_reflects_live_phase_and_review_state(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-01 同步控制塔真值与 freeze packet 基线",
            latest_success_run="GitHub GSD automation 24234580061",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24234580061 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="175 tests OK; 10 demo smoke scenarios pass.",
            latest_passing_qa_summary="PASS. 8 validation commands all green.",
        )
        config = {
            "pages": {
                "constitution": "constitution-id",
                "status": "status-id",
                "control_plane": "control-plane-id",
                "opus_protocol": "opus-protocol-id",
                "opus_brief": "opus-brief-id",
                "freeze_packet": "freeze-packet-id",
            },
            "databases": {
                "roadmap": "roadmap-id",
                "plans": "plans-id",
                "runs": "runs-id",
                "qa": "qa-id",
                "gates": "gates-id",
                "gaps": "gaps-id",
                "assets": "assets-id",
            },
            "default_plan": "P6-02 控制塔首页快照自动同步",
        }
        brief = build_current_review_brief(
            snapshot,
            {
                "urls": {
                    "github_repo": "https://github.com/example/repo",
                    "github_actions": "https://github.com/example/repo/actions",
                }
            },
        )

        blocks = render_dashboard_blocks(brief, snapshot, config)
        text_fragments = []
        for block in blocks:
            for value in block.values():
                if isinstance(value, dict) and "rich_text" in value:
                    text_fragments.extend(item["text"]["content"] for item in value["rich_text"])

        joined = "\n".join(text_fragments)
        self.assertIn("P6 Reconcile Control Tower And Freeze Demo Packet", joined)
        self.assertIn("P6-01 同步控制塔真值与 freeze packet 基线", joined)
        self.assertIn("当前无需 Opus 审查", joined)
        self.assertIn("继续自动开发；当前无需手动触发 Opus 4.6。", joined)
        self.assertIn("文档定位", joined)
        self.assertIn("五层架构", joined)
        self.assertIn("实时证据入口", joined)
        self.assertIn("历史总览（自动同步）", joined)
        self.assertIn("标准闭环", joined)
        self.assertIn("P7-05：把 diagnosis + repair outcome 收成 reusable knowledge artifact。", joined)

    def test_render_dashboard_blocks_switches_to_dashboard_only_mode_when_active_subpages_are_unavailable(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-10 显式化 dashboard-only degraded mode",
            latest_success_run="GitHub GSD automation 24243230588",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24243230588 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        config = {
            "pages": {
                "status": "status-id",
                "opus_brief": "opus-brief-id",
                "freeze_packet": "freeze-packet-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
            "default_plan": "P6-10 显式化 dashboard-only degraded mode",
        }
        brief = build_current_review_brief(
            snapshot,
            {
                "urls": {
                    "github_repo": "https://github.com/example/repo",
                    "github_actions": "https://github.com/example/repo/actions",
                }
            },
        )

        blocks = render_dashboard_blocks(
            brief,
            snapshot,
            config,
            unavailable_page_keys=("status", "opus_brief", "freeze_packet"),
        )

        joined = "\n".join(
            item["text"]["content"]
            for block in blocks
            for payload in block.values()
            if isinstance(payload, dict) and "rich_text" in payload
            for item in payload["rich_text"]
        )
        self.assertIn("dashboard-only degraded mode", joined)
        self.assertIn("当前受 Notion archived page 限制暂不可直写", joined)
        self.assertIn("历史总览（自动同步）", joined)

    def test_render_current_review_brief_blocks_use_database_urls_for_database_refs(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-07 数据库写回失败时仍推进活动页快照",
            latest_success_run="GitHub GSD automation 24241080590",
            latest_failed_run="GitHub GSD automation 24238577807",
            latest_passing_qa="GitHub GSD automation 24241080590 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        config = {
            "pages": {
                "constitution": "constitution-page-id",
                "status": "status-page-id",
                "control_plane": "control-plane-page-id",
                "opus_protocol": "opus-protocol-page-id",
            },
            "databases": {
                "plans": "plans-db-page-id",
                "runs": "runs-db-page-id",
                "qa": "qa-db-page-id",
                "gates": "gates-db-page-id",
                "gaps": "gaps-db-page-id",
                "assets": "assets-db-page-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
        }
        old_env = dict(os.environ)
        try:
            os.environ["NOTION_GSD_GAP_DATABASE_ID"] = "gaps-data-source-id"
            brief = build_current_review_brief(snapshot, config)
            blocks = render_current_review_brief_blocks(brief, snapshot, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        paragraph_texts = []
        for block in blocks:
            payload = block.get("paragraph")
            if not isinstance(payload, dict):
                continue
            for item in payload.get("rich_text", []):
                text = item.get("text", {})
                if text.get("link", {}).get("url"):
                    paragraph_texts.append(text["link"]["url"])
        self.assertIn("https://www.notion.so/gapsdbpageid", paragraph_texts)
        self.assertNotIn("https://www.notion.so/gapsdatasourceid", paragraph_texts)

    def test_render_freeze_packet_blocks_reflects_live_baseline(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-02 控制塔首页快照自动同步",
            latest_success_run="GitHub GSD automation 24237800855",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24237800855 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="175 tests OK; 10 demo smoke scenarios pass.",
            latest_passing_qa_summary="PASS. 8 validation commands all green.",
        )
        config = {
            "pages": {
                "status": "status-id",
                "constitution": "constitution-id",
                "opus_brief": "opus-brief-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
        }
        brief = build_current_review_brief(snapshot, config)

        blocks = render_freeze_packet_blocks(brief, snapshot, config)
        text_fragments = []
        for block in blocks:
            for value in block.values():
                if isinstance(value, dict) and "rich_text" in value:
                    text_fragments.extend(item["text"]["content"] for item in value["rich_text"])

        joined = "\n".join(text_fragments)
        self.assertIn("P6 Reconcile Control Tower And Freeze Demo Packet", joined)
        self.assertIn("P6-02 控制塔首页快照自动同步", joined)
        self.assertIn("175 tests OK; 10 demo smoke scenarios pass.", joined)
        self.assertIn("PASS. 8 validation commands all green.", joined)

    def test_render_status_page_blocks_reflects_live_baseline_and_links(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-04 用可自动同步状态页旁路旧 archived status 页面",
            latest_success_run="GitHub GSD automation 24238846145",
            latest_failed_run="GitHub GSD automation 24238577807",
            latest_passing_qa="GitHub GSD automation 24238846145 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="Notion 404 writeback now degrades instead of failing CI.",
            latest_passing_qa_summary="175 tests OK, 10 demo smoke scenarios pass, 8/8 checks pass.",
        )
        config = {
            "pages": {
                "dashboard": "dashboard-id",
                "freeze_packet": "freeze-id",
                "opus_brief": "brief-id",
                "constitution": "constitution-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
        }
        brief = build_current_review_brief(snapshot, config)

        blocks = render_status_page_blocks(brief, snapshot, config)
        text_fragments = []
        for block in blocks:
            for value in block.values():
                if isinstance(value, dict) and "rich_text" in value:
                    text_fragments.extend(item["text"]["content"] for item in value["rich_text"])

        joined = "\n".join(text_fragments)
        self.assertIn("P6 Reconcile Control Tower And Freeze Demo Packet", joined)
        self.assertIn("P6-04 用可自动同步状态页旁路旧 archived status 页面", joined)
        self.assertIn("GitHub GSD automation 24238846145", joined)
        self.assertIn("当前无需手动触发 Opus 4.6。", joined)

    def test_render_repo_coordination_plan_markdown_reflects_live_baseline(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-04 用可自动同步状态页旁路旧 archived status 页面",
            latest_success_run="GitHub GSD automation 24239357493",
            latest_failed_run="GitHub GSD automation 24238577807",
            latest_passing_qa="GitHub GSD automation 24239357493 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="Dashboard/status/freeze links now converge on the auto-synced status page.",
            latest_passing_qa_summary="175 tests OK, 10 demo smoke scenarios pass, 8/8 checks pass.",
        )
        config = {
            "root_page_url": "https://www.notion.so/control-tower",
            "pages": {
                "status": "status-id",
                "opus_brief": "brief-id",
                "freeze_packet": "freeze-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
        }
        brief = build_current_review_brief(snapshot, config)

        text = render_repo_coordination_plan_markdown(brief, snapshot, config)

        self.assertIn("P6 Reconcile Control Tower And Freeze Demo Packet", text)
        self.assertIn("P6-04 用可自动同步状态页旁路旧 archived status 页面", text)
        self.assertIn("GitHub GSD automation 24239357493", text)
        self.assertIn("当前无需手动触发 Opus 4.6", text)

    def test_upsert_managed_markdown_section_replaces_existing_block(self):
        existing = (
            "# Coordination Plan\n\n"
            "<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT START -->\n"
            "old\n"
            "<!-- AUTO-SYNCED COORDINATION PLAN SNAPSHOT END -->\n\n"
            "## 历史记录\n"
            "legacy\n"
        )

        updated = upsert_managed_markdown_section(
            existing,
            "AUTO-SYNCED COORDINATION PLAN SNAPSHOT",
            "## 当前自动同步快照\n\n- new",
        )

        self.assertIn("## 当前自动同步快照", updated)
        self.assertIn("- new", updated)
        self.assertIn("## 历史记录", updated)
        self.assertNotIn("\nold\n", updated)

    def test_sync_repo_documents_updates_active_docs_with_managed_sections(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-05 同步 repo 侧交接文档快照",
            latest_success_run="GitHub GSD automation 24240000000",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24240000000 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="Repo-side docs now share the same live snapshot.",
            latest_passing_qa_summary="175 tests OK, 10 demo smoke scenarios pass, 8/8 checks pass.",
        )
        config = {
            "root_page_url": "https://www.notion.so/control-tower",
            "pages": {
                "status": "status-id",
                "opus_brief": "brief-id",
                "freeze_packet": "freeze-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
        }
        brief = build_current_review_brief(snapshot, config)

        with tempfile.TemporaryDirectory() as tempdir:
            root = os.path.join(tempdir, "repo")
            os.makedirs(os.path.join(root, "docs", "coordination"), exist_ok=True)
            os.makedirs(os.path.join(root, "docs", "freeze"), exist_ok=True)
            for relative_path, title in (
                ("docs/coordination/plan.md", "# Coordination Plan\n\nlegacy\n"),
                ("docs/coordination/dev_handoff.md", "# Dev Handoff\n\nlegacy\n"),
                ("docs/coordination/qa_report.md", "# QA Report\n\nlegacy\n"),
                ("docs/freeze/2026-04-10-freeze-demo-packet.md", "# Freeze Packet\n\nlegacy\n"),
            ):
                with open(os.path.join(root, relative_path), "w", encoding="utf-8") as handle:
                    handle.write(title)

            synced = sync_repo_documents(Path(root), brief, snapshot, config)

            self.assertEqual(4, len(synced))
            with open(os.path.join(root, "docs", "coordination", "plan.md"), encoding="utf-8") as handle:
                plan_text = handle.read()
            self.assertIn("AUTO-SYNCED COORDINATION PLAN SNAPSHOT START", plan_text)
            self.assertIn("P6-05 同步 repo 侧交接文档快照", plan_text)
            self.assertIn("legacy", plan_text)

    def test_fetch_review_snapshot_prefers_github_runs_and_matching_qa(self):
        class FakeClient:
            def query_database(self, database_id, *, filter_payload=None, sorts=None, page_size=10):
                if database_id == "roadmap-db":
                    return [
                        {"id": "phase-id", "properties": {"Round": {"type": "title", "title": [{"plain_text": "P3 减少控制面漂移"}]}}},
                    ]
                if database_id == "plans-db":
                    return [
                        {"id": "plan-id", "properties": {"Plan": {"type": "title", "title": [{"plain_text": "P3-04 优先 GitHub 审查证据"}]}}},
                    ]
                if database_id == "runs-db":
                    if filter_payload == {
                        "and": [
                            {"property": "Status", "select": {"equals": "Succeeded"}},
                            {"property": "Executor", "select": {"equals": "GitHub Action"}},
                        ]
                    }:
                        return [
                            {"id": "run-github-success", "properties": {"Run": {"type": "title", "title": [{"plain_text": "GitHub GSD automation 24153107164"}]}}},
                        ]
                    if filter_payload == {
                        "and": [
                            {"property": "Status", "select": {"equals": "Failed"}},
                            {"property": "Executor", "select": {"equals": "GitHub Action"}},
                        ]
                    }:
                        return [
                            {"id": "run-github-fail", "properties": {"Run": {"type": "title", "title": [{"plain_text": "GitHub GSD automation 24148804383"}]}}},
                        ]
                    if filter_payload == {"property": "Status", "select": {"equals": "Succeeded"}}:
                        return [
                            {"id": "run-local-success", "properties": {"Run": {"type": "title", "title": [{"plain_text": "Local hardening: no-review-aware Opus brief"}]}}},
                        ]
                    if filter_payload == {"property": "Status", "select": {"equals": "Failed"}}:
                        return []
                if database_id == "qa-db":
                    if filter_payload == {"property": "Run", "title": {"equals": "GitHub GSD automation 24153107164 QA"}}:
                        return [
                            {"id": "qa-github", "properties": {"Run": {"type": "title", "title": [{"plain_text": "GitHub GSD automation 24153107164 QA"}]}}},
                        ]
                    return []
                if database_id == "gates-db":
                    return [
                        {"id": "gate-id", "properties": {"Gate": {"type": "title", "title": [{"plain_text": "OPUS-4.6 周期审查 Gate"}]}, "Status": {"type": "select", "select": {"name": "Approved"}}}},
                    ]
                if database_id == "tasks-db":
                    return []
                if database_id == "gaps-db":
                    return []
                return []

        snapshot = fetch_review_snapshot(
            FakeClient(),
            {
                "databases": {
                    "roadmap": "roadmap-db",
                    "plans": "plans-db",
                    "runs": "runs-db",
                    "qa": "qa-db",
                    "gates": "gates-db",
                    "tasks": "tasks-db",
                    "gaps": "gaps-db",
                },
                "default_plan": "fallback-plan",
                "default_review_gate": "OPUS-4.6 周期审查 Gate",
            },
        )

        self.assertEqual("GitHub GSD automation 24153107164", snapshot.latest_success_run)
        self.assertEqual("GitHub GSD automation 24153107164 QA", snapshot.latest_passing_qa)
        self.assertEqual("GitHub GSD automation 24148804383", snapshot.latest_failed_run)

    def test_fetch_review_snapshot_from_pages_uses_active_page_surfaces(self):
        class FakeClient:
            def list_block_children(self, page_id):
                pages = {
                    "dashboard-id": [
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前阶段：P6 Reconcile Control Tower And Freeze Demo Packet"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前已验证 Plan：P6-04 用可自动同步状态页旁路旧 archived status 页面"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 最近成功执行证据：GitHub GSD automation 24239357493"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前 Gate：OPUS-4.6 周期审查 Gate（Approved）"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- Open Gap 数量：0"}]},
                        },
                    ],
                    "brief-id": [
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 最近失败历史证据：GitHub GSD automation 24238577807"}]},
                        }
                    ],
                    "freeze-id": [
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前 QA 摘要：175 tests OK, 10 demo smoke scenarios pass, 8/8 checks pass."}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前运行摘要：Active links now land on the auto-synced status page."}]},
                        },
                    ],
                    "status-id": [],
                }
                return pages[page_id]

        snapshot = fetch_review_snapshot_from_pages(
            FakeClient(),  # type: ignore[arg-type]
            {
                "pages": {
                    "dashboard": "dashboard-id",
                    "opus_brief": "brief-id",
                    "freeze_packet": "freeze-id",
                    "status": "status-id",
                },
                "default_plan": "fallback-plan",
            },
        )

        self.assertEqual("P6 Reconcile Control Tower And Freeze Demo Packet", snapshot.active_phase)
        self.assertEqual("P6-04 用可自动同步状态页旁路旧 archived status 页面", snapshot.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24239357493", snapshot.latest_success_run)
        self.assertEqual("GitHub GSD automation 24238577807", snapshot.latest_failed_run)
        self.assertEqual("Approved", snapshot.gate_status)

    def test_fetch_review_snapshot_from_dashboard_page_works_when_subpages_are_unavailable(self):
        class FakeClient:
            def list_block_children(self, page_id):
                pages = {
                    "dashboard-id": [
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前阶段：P6 Reconcile Control Tower And Freeze Demo Packet"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前已验证 Plan：P6-10 显式化 dashboard-only degraded mode"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 最近成功执行证据：GitHub GSD automation 24243804732"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- 当前 Gate：OPUS-4.6 周期审查 Gate（Approved）"}]},
                        },
                        {
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"plain_text": "- Open Gap 数量：0"}]},
                        },
                    ]
                }
                return pages[page_id]

        snapshot = fetch_review_snapshot_from_dashboard_page(
            FakeClient(),  # type: ignore[arg-type]
            {
                "pages": {"dashboard": "dashboard-id"},
                "default_plan": "fallback-plan",
            },
        )

        self.assertEqual("P6 Reconcile Control Tower And Freeze Demo Packet", snapshot.active_phase)
        self.assertEqual("P6-10 显式化 dashboard-only degraded mode", snapshot.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24243804732", snapshot.latest_success_run)
        self.assertEqual("Approved", snapshot.gate_status)

    def test_should_prefer_page_snapshot_when_dashboard_run_is_newer(self):
        primary_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="",
            active_phase_summary="db snapshot",
            latest_verified_plan="P6-07 数据库写回失败时仍推进活动页快照",
            latest_success_run="GitHub GSD automation 24241382132",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        page_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="",
            active_phase_summary="page snapshot",
            latest_verified_plan="P6-10 显式化 dashboard-only degraded mode",
            latest_success_run="GitHub GSD automation 24243804732",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )

        self.assertTrue(
            should_prefer_page_snapshot(
                primary_snapshot,
                page_snapshot,
                {"default_plan": "P6-10 显式化 dashboard-only degraded mode"},
            )
        )

    def test_should_prefer_page_snapshot_when_it_matches_current_default_plan(self):
        primary_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="",
            active_phase_summary="db snapshot",
            latest_verified_plan="P6-07 数据库写回失败时仍推进活动页快照",
            latest_success_run="GitHub GSD automation 24243804732",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        page_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="",
            active_phase_summary="page snapshot",
            latest_verified_plan="P6-11 让 repo docs 跟随更新鲜的 dashboard 快照",
            latest_success_run="GitHub GSD automation 24243804732",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )

        self.assertTrue(
            should_prefer_page_snapshot(
                primary_snapshot,
                page_snapshot,
                {"default_plan": "P6-11 让 repo docs 跟随更新鲜的 dashboard 快照"},
            )
        )

    def test_write_notion_outcome_uses_exact_github_run_url_for_artifacts(self):
        class FakeClient:
            def __init__(self):
                self.calls = []
                self.updated = []

            def upsert_page(self, database_id, title_prop, title, properties):
                self.calls.append((database_id, title_prop, title, properties))
                return f"{database_id}:{title}"

            def query_database(self, database_id, *, filter_payload=None, page_size=10, sorts=None):
                return []

            def update_page_properties(self, page_id, properties):
                self.updated.append((page_id, properties))

        client = FakeClient()
        config = {
            "databases": {
                "plans": "plans-db",
                "runs": "runs-db",
                "qa": "qa-db",
                "gaps": "gaps-db",
                "gates": "gates-db",
            },
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
        }
        summary = summarize_results(
            [
                CommandResult(
                    command="python3 tools/run_gsd_validation_suite.py --format json",
                    returncode=0,
                    stdout="PASS",
                    stderr="",
                    started_at="2026-04-09T00:00:00+00:00",
                    ended_at="2026-04-09T00:00:05+00:00",
                )
            ]
        )

        old_env = dict(os.environ)
        try:
            os.environ["GITHUB_ACTIONS"] = "true"
            os.environ["GITHUB_SERVER_URL"] = "https://github.com"
            os.environ["GITHUB_REPOSITORY"] = "owner/repo"
            os.environ["GITHUB_RUN_ID"] = "12345"
            write_notion_outcome(
                client,  # type: ignore[arg-type]
                config,
                title="GitHub GSD automation 12345",
                plan_id="P3-04 优先 GitHub 审查证据",
                commands=["python3 tools/run_gsd_validation_suite.py --format json"],
                results=[
                    CommandResult(
                        command="python3 tools/run_gsd_validation_suite.py --format json",
                        returncode=0,
                        stdout="PASS",
                        stderr="",
                        started_at="2026-04-09T00:00:00+00:00",
                        ended_at="2026-04-09T00:00:05+00:00",
                    )
                ],
                summary=summary,
                opus_gate=False,
            )
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        run_call = next(call for call in client.calls if call[0] == "runs-db")
        self.assertEqual(
            "https://github.com/owner/repo/actions/runs/12345",
            run_call[3]["Artifacts"]["rich_text"][0]["text"]["content"],
        )

    def test_handle_run_degrades_successful_ci_when_notion_writeback_fails(self):
        args = argparse.Namespace(
            cwd=".",
            plan_id="P6-03 Freeze Demo Packet 自动快照同步",
            title="GitHub GSD automation 24239999999",
            command=["python3 tools/run_gsd_validation_suite.py --format json"],
            dry_run=False,
            opus_gate=False,
            format="json",
        )
        config = {
            "default_plan": "P6-03 Freeze Demo Packet 自动快照同步",
        }
        results = [
            CommandResult(
                command="python3 tools/run_gsd_validation_suite.py --format json",
                returncode=0,
                stdout="PASS",
                stderr="",
                started_at="2026-04-10T00:00:00+00:00",
                ended_at="2026-04-10T00:00:05+00:00",
            )
        ]

        old_env = dict(os.environ)
        try:
            os.environ["NOTION_API_KEY"] = "test-token"
            with (
                patch("tools.gsd_notion_sync.run_commands", return_value=results),
                patch(
                    "tools.gsd_notion_sync.write_notion_outcome",
                    side_effect=RuntimeError("Notion API request failed: HTTP 404 /v1/databases/test/query"),
                ),
                patch(
                    "tools.gsd_notion_sync.fetch_review_snapshot_from_pages",
                    return_value=ReviewSnapshot(
                        active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
                        active_phase_goal="对齐控制塔真值与冻结包",
                        active_phase_summary="P6 正在执行",
                        latest_verified_plan="P6-05 同步 repo 侧交接文档快照",
                        latest_success_run="GitHub GSD automation 24239973670",
                        latest_failed_run="GitHub GSD automation 24238577807",
                        latest_passing_qa="GitHub GSD automation 24239973670 QA",
                        gate_page_id="gate-page-id",
                        gate_name="OPUS-4.6 周期审查 Gate",
                        gate_status="Approved",
                        ready_task_id=None,
                        ready_task=None,
                        open_gap_titles=(),
                        stale_gap_titles=(),
                        latest_success_run_notes="185 tests OK",
                        latest_passing_qa_summary="PASS. 8 validation commands all green.",
                    ),
                ),
                patch(
                    "tools.gsd_notion_sync.write_current_opus_review_brief_from_snapshot",
                    return_value={"intervention_kind": "当前无需 Opus 审查", "review_target": "P6 / P6-06"},
                ) as fallback_mock,
                patch("tools.gsd_notion_sync.output_run_result") as output_mock,
            ):
                exit_code = handle_run(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        payload = output_mock.call_args.args[1]
        self.assertEqual("partial", payload["notion"])
        self.assertEqual("written", payload["notion_fallback"])
        self.assertIn("HTTP 404", payload["notion_error"])
        self.assertEqual("Succeeded", payload["status"])
        fallback_snapshot = fallback_mock.call_args.kwargs["snapshot"]
        self.assertEqual("P6-03 Freeze Demo Packet 自动快照同步", fallback_snapshot.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24239999999", fallback_snapshot.latest_success_run)

    def test_build_fallback_run_snapshot_uses_compact_success_summary(self):
        results = [
            CommandResult(
                command="python3 -m unittest discover -s tests -p test_*.py",
                returncode=0,
                stdout="",
                stderr="Ran 187 tests in 21.157s\n\nOK",
                started_at="2026-04-10T00:00:00+00:00",
                ended_at="2026-04-10T00:00:05+00:00",
            ),
            CommandResult(
                command="python3 tools/demo_path_smoke.py --format json",
                returncode=0,
                stdout='{"completed_scenarios": 10, "failed_scenario": null, "scenario_count": 10}',
                stderr="",
                started_at="2026-04-10T00:00:05+00:00",
                ended_at="2026-04-10T00:00:10+00:00",
            ),
        ]
        summary = summarize_results(results)
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-06 将历史 repo 交接正文移出活跃文档",
            latest_success_run="GitHub GSD automation 24240811595",
            latest_failed_run="GitHub GSD automation 24238577807",
            latest_passing_qa="GitHub GSD automation 24240811595 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="old notes",
            latest_passing_qa_summary="old qa",
        )

        with patch("tools.gsd_notion_sync.fetch_review_snapshot_from_pages", return_value=snapshot):
            fallback = build_fallback_run_snapshot(
                None,
                {},
                cwd=Path("."),
                plan_id="P6-07 数据库写回失败时仍推进活动页快照",
                title="GitHub GSD automation 24241080590",
                results=results,
                summary=summary,
            )

        self.assertEqual("P6-07 数据库写回失败时仍推进活动页快照", fallback.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24241080590", fallback.latest_success_run)
        self.assertEqual(
            "187 tests OK, 10 demo smoke scenarios pass, and 2/2 shared validation checks pass.",
            fallback.latest_success_run_notes,
        )
        self.assertEqual(
            "PASS. 187 tests OK, 10 demo smoke scenarios pass, and 2/2 shared validation checks pass.",
            fallback.latest_passing_qa_summary,
        )

    def test_handle_prepare_opus_review_falls_back_to_active_pages_when_db_unshared(self):
        args = argparse.Namespace(activate_gate=False, dry_run=True, format="json")
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-06 将历史 repo 交接正文移出活跃文档",
            latest_success_run="GitHub GSD automation 24240641848",
            latest_failed_run="GitHub GSD automation 24238577807",
            latest_passing_qa="GitHub GSD automation 24240641848 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )

        old_env = dict(os.environ)
        try:
            os.environ["NOTION_API_KEY"] = "test-token"
            with (
                patch(
                    "tools.gsd_notion_sync.fetch_review_snapshot",
                    side_effect=RuntimeError("Notion API request failed: HTTP 404 /v1/databases/test/query"),
                ),
                patch("tools.gsd_notion_sync.fetch_review_snapshot_from_pages", return_value=snapshot) as fallback_mock,
                patch("tools.gsd_notion_sync.output_review_result") as output_mock,
            ):
                exit_code = handle_prepare_opus_review(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fallback_mock.call_count)
        payload = output_mock.call_args.args[1]
        self.assertEqual("当前无需 Opus 审查", payload["intervention_kind"])
        self.assertEqual("Approved", payload["gate_status"])

    def test_handle_prepare_opus_review_falls_back_when_db_is_rate_limited(self):
        args = argparse.Namespace(activate_gate=False, dry_run=True, format="json")
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P7-05 捕获 fault resolution knowledge artifact",
            latest_success_run="P7-05 Knowledge artifact baseline",
            latest_failed_run=None,
            latest_passing_qa="P7-05 Knowledge artifact baseline QA",
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )

        old_env = dict(os.environ)
        try:
            os.environ["NOTION_API_KEY"] = "test-token"
            with (
                patch(
                    "tools.gsd_notion_sync.fetch_review_snapshot",
                    side_effect=RuntimeError("Notion API request failed: HTTP 429 /v1/databases/test/query: rate_limited"),
                ),
                patch("tools.gsd_notion_sync.fetch_review_snapshot_from_pages", return_value=snapshot) as fallback_mock,
                patch("tools.gsd_notion_sync.output_review_result") as output_mock,
            ):
                exit_code = handle_prepare_opus_review(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fallback_mock.call_count)
        payload = output_mock.call_args.args[1]
        self.assertEqual("P7-05 Knowledge artifact baseline", payload["latest_success_run"])

    def test_fetch_review_snapshot_from_repo_docs_uses_freeze_packet_seed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            freeze_path = cwd / "docs/freeze/2026-04-10-freeze-demo-packet.md"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(
                "# Freeze Packet\n\n"
                "- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`\n"
                "- 当前已验证 Plan：`P6-07 数据库写回失败时仍推进活动页快照`\n"
                "- 最近成功执行证据：`GitHub GSD automation 24241382132`\n"
                "- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`\n"
                "- 当前 Opus 状态：`当前无需 Opus 审查`\n"
                "- Open Gap 数量：`0`\n"
                "Ran 189 tests in 20.897s\n"
                "{\"command_count\": 8, \"completed_scenarios\": 10}\n",
                encoding="utf-8",
            )

            snapshot = fetch_review_snapshot_from_repo_docs(
                cwd,
                {"default_plan": "P6-07 数据库写回失败时仍推进活动页快照"},
            )

        self.assertEqual("P6 Reconcile Control Tower And Freeze Demo Packet", snapshot.active_phase)
        self.assertEqual("P6-07 数据库写回失败时仍推进活动页快照", snapshot.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24241382132", snapshot.latest_success_run)
        self.assertEqual("Approved", snapshot.gate_status)
        self.assertEqual(
            "189 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            snapshot.latest_success_run_notes,
        )

    def test_build_superseded_gap_fix_plan_marks_duplicates(self):
        self.assertEqual(
            "Superseded by successful run GitHub GSD automation 24150884053.",
            build_superseded_gap_fix_plan("GitHub GSD automation 24150884053"),
        )
        self.assertEqual(
            "Superseded by successful run GitHub GSD automation 24150884053. Duplicate of sibling gap record.",
            build_superseded_gap_fix_plan("GitHub GSD automation 24150884053", duplicate=True),
        )

    def test_resolve_superseded_failure_gaps_updates_open_matching_rows_only(self):
        class FakeClient:
            def __init__(self):
                self.updated = []

            def query_database(self, database_id, *, filter_payload=None, page_size=10, sorts=None):
                self.database_id = database_id
                self.filter_payload = filter_payload
                return [
                    {
                        "id": "gap-open-1",
                        "properties": {
                            "Gap": {"type": "title", "title": [{"plain_text": "Automation failure: P1-01 建立自动执行 / QA 回写闭环"}]},
                            "Status": {"type": "select", "select": {"name": "Open"}},
                        },
                    },
                    {
                        "id": "gap-open-2",
                        "properties": {
                            "Gap": {"type": "title", "title": [{"plain_text": "Automation failure: P1-01 建立自动执行 / QA 回写闭环"}]},
                            "Status": {"type": "select", "select": {"name": "Open"}},
                        },
                    },
                    {
                        "id": "gap-resolved",
                        "properties": {
                            "Gap": {"type": "title", "title": [{"plain_text": "Automation failure: P1-01 建立自动执行 / QA 回写闭环"}]},
                            "Status": {"type": "select", "select": {"name": "Resolved"}},
                        },
                    },
                ]

            def update_page_properties(self, page_id, properties):
                self.updated.append((page_id, properties))

        client = FakeClient()
        config = {"databases": {"gaps": "gaps-db-id"}}

        resolved = resolve_superseded_failure_gaps(
            client,
            config,
            plan_id="P1-01 建立自动执行 / QA 回写闭环",
            success_run_title="GitHub GSD automation 24150884053",
        )

        self.assertEqual(["gap-open-1", "gap-open-2"], resolved)
        self.assertEqual("gaps-db-id", client.database_id)
        self.assertEqual(
            {"property": "Gap", "title": {"equals": "Automation failure: P1-01 建立自动执行 / QA 回写闭环"}},
            client.filter_payload,
        )
        self.assertEqual(2, len(client.updated))
        self.assertEqual("Resolved", client.updated[0][1]["Status"]["select"]["name"])
        self.assertEqual(
            "Superseded by successful run GitHub GSD automation 24150884053.",
            client.updated[0][1]["Fix Plan"]["rich_text"][0]["text"]["content"],
        )
        self.assertEqual(
            "Superseded by successful run GitHub GSD automation 24150884053. Duplicate of sibling gap record.",
            client.updated[1][1]["Fix Plan"]["rich_text"][0]["text"]["content"],
        )

    def test_retire_legacy_review_artifacts_archives_only_active_configured_pages(self):
        class FakeClient:
            def __init__(self):
                self.archived = []

            def get_page(self, page_id):
                pages = {
                    "gate-legacy": {"id": "gate-legacy", "archived": False, "in_trash": False},
                    "plan-legacy": {"id": "plan-legacy", "archived": False, "in_trash": False},
                    "already-archived": {"id": "already-archived", "archived": True, "in_trash": True},
                }
                return pages[page_id]

            def archive_page(self, page_id):
                self.archived.append(page_id)

        snapshot = ReviewSnapshot(
            active_phase="P3 减少控制面漂移",
            active_phase_goal="保持自动开发闭环稳定",
            active_phase_summary="P3 正在推进",
            latest_verified_plan="P3-06 Notion 控制面自检",
            latest_success_run="GitHub GSD automation 24167870634",
            latest_failed_run="GitHub GSD automation 24148804383",
            latest_passing_qa="GitHub GSD automation 24167870634 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
        )
        brief = build_current_review_brief(
            snapshot,
            {
                "urls": {
                    "github_repo": "https://github.com/example/repo",
                    "github_actions": "https://github.com/example/repo/actions",
                }
            },
        )

        retired = retire_legacy_review_artifacts(
            FakeClient(),
            {
                "legacy_review_artifacts": [
                    {"id": "gate-legacy", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "superseded"},
                    {"id": "plan-legacy", "kind": "plan", "title": "P1-02 消除手动浏览器 QA 依赖", "reason": "superseded"},
                    {"id": "already-archived", "kind": "plan", "title": "Archived already", "reason": "superseded"},
                ]
            },
            snapshot=snapshot,
            brief=brief,
        )

        self.assertEqual(["gate-legacy", "plan-legacy"], retired)

    def test_retire_legacy_review_artifacts_skips_when_review_is_still_required(self):
        class FakeClient:
            def __init__(self):
                self.archived = []

            def get_page(self, page_id):
                return {"id": page_id, "archived": False, "in_trash": False}

            def archive_page(self, page_id):
                self.archived.append(page_id)

        snapshot = ReviewSnapshot(
            active_phase="P1 建立 Notion + GitHub 的 Opus 审查闭环",
            active_phase_goal="让主观审查完全通过 Notion 页面 + GitHub 仓库完成",
            active_phase_summary="P1 正在执行",
            latest_verified_plan="P1-01 建立自动执行 / QA 回写闭环",
            latest_success_run=None,
            latest_failed_run="GitHub GSD automation 24148804383",
            latest_passing_qa=None,
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Standby",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=("Automation failure: P1-01 建立自动执行 / QA 回写闭环",),
            stale_gap_titles=(),
        )
        brief = build_current_review_brief(
            snapshot,
            {
                "urls": {
                    "github_repo": "https://github.com/example/repo",
                    "github_actions": "https://github.com/example/repo/actions",
                }
            },
        )
        client = FakeClient()

        retired = retire_legacy_review_artifacts(
            client,
            {
                "legacy_review_artifacts": [
                    {"id": "gate-legacy", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "superseded"},
                ]
            },
            snapshot=snapshot,
            brief=brief,
        )

        self.assertEqual([], retired)
        self.assertEqual([], client.archived)

    def test_replace_page_body_skips_archived_children_when_clearing_page(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {"id": "active-block", "archived": False, "in_trash": False},
                    {"id": "archived-block", "archived": True, "in_trash": False},
                    {"id": "trashed-block", "archived": False, "in_trash": True},
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                return {}

        client = FakeClient()

        client.replace_page_body("page-123", [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}])

        self.assertEqual(
            [
                ("DELETE", "/v1/blocks/active-block", None),
                (
                    "PATCH",
                    "/v1/blocks/page-123/children",
                    {
                        "children": [
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}},
                        ],
                        "position": {"type": "start"},
                    },
                ),
            ],
            client.calls,
        )

    def test_replace_page_body_preserves_child_pages_and_child_databases(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {"id": "narrative-block", "type": "paragraph", "archived": False, "in_trash": False},
                    {"id": "child-page-block", "type": "child_page", "archived": False, "in_trash": False},
                    {"id": "child-db-block", "type": "child_database", "archived": False, "in_trash": False},
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                return {}

        client = FakeClient()

        client.replace_page_body("page-123", [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}])

        self.assertEqual(
            [
                ("DELETE", "/v1/blocks/narrative-block", None),
                (
                    "PATCH",
                    "/v1/blocks/page-123/children",
                    {
                        "children": [
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}},
                        ],
                        "position": {"type": "start"},
                    },
                ),
            ],
            client.calls,
        )

    def test_replace_page_body_ignores_archived_delete_errors_from_notion(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {"id": "ghost-archived-block", "type": "paragraph", "archived": False, "in_trash": False},
                    {"id": "live-block", "type": "paragraph", "archived": False, "in_trash": False},
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                if method == "DELETE" and path == "/v1/blocks/ghost-archived-block":
                    raise RuntimeError(
                        'Notion API request failed: HTTP 400 /v1/blocks/ghost-archived-block: '
                        '{"message":"Can\'t edit block that is archived."}'
                    )
                return {}

        client = FakeClient()

        client.replace_page_body("page-123", [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}])

        self.assertEqual(
            [
                ("DELETE", "/v1/blocks/ghost-archived-block", None),
                ("DELETE", "/v1/blocks/live-block", None),
                (
                    "PATCH",
                    "/v1/blocks/page-123/children",
                    {
                        "children": [
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}},
                        ],
                        "position": {"type": "start"},
                    },
                ),
            ],
            client.calls,
        )

    def test_upsert_dashboard_snapshot_section_replaces_previous_managed_snapshot_only(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {
                        "id": "managed-callout",
                        "type": "callout",
                        "archived": False,
                        "in_trash": False,
                        "callout": {"rich_text": [{"plain_text": "AUTO-SYNCED DASHBOARD SNAPSHOT — old"}]},
                    },
                    {
                        "id": "managed-heading",
                        "type": "heading_2",
                        "archived": False,
                        "in_trash": False,
                        "heading_2": {"rich_text": [{"plain_text": "当前快照（自动同步）"}]},
                    },
                    {
                        "id": "managed-divider",
                        "type": "divider",
                        "archived": False,
                        "in_trash": False,
                        "divider": {},
                    },
                    {
                        "id": "historical-block",
                        "type": "paragraph",
                        "archived": False,
                        "in_trash": False,
                        "paragraph": {"rich_text": [{"plain_text": "legacy content"}]},
                    },
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                return {}

        client = FakeClient()
        blocks = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}]

        upsert_dashboard_snapshot_section(client, "dashboard-page", blocks)

        self.assertEqual(
            [
                ("DELETE", "/v1/blocks/managed-callout", None),
                ("DELETE", "/v1/blocks/managed-heading", None),
                ("DELETE", "/v1/blocks/managed-divider", None),
                (
                    "PATCH",
                    "/v1/blocks/dashboard-page/children",
                    {"children": blocks, "position": {"type": "start"}},
                ),
            ],
            client.calls,
        )

    def test_upsert_freeze_packet_snapshot_section_replaces_previous_managed_snapshot_only(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {
                        "id": "managed-callout",
                        "type": "callout",
                        "archived": False,
                        "in_trash": False,
                        "callout": {"rich_text": [{"plain_text": "AUTO-SYNCED FREEZE PACKET SNAPSHOT — old"}]},
                    },
                    {
                        "id": "managed-heading",
                        "type": "heading_2",
                        "archived": False,
                        "in_trash": False,
                        "heading_2": {"rich_text": [{"plain_text": "当前冻结基线（自动同步）"}]},
                    },
                    {
                        "id": "managed-divider",
                        "type": "divider",
                        "archived": False,
                        "in_trash": False,
                        "divider": {},
                    },
                    {
                        "id": "historical-block",
                        "type": "paragraph",
                        "archived": False,
                        "in_trash": False,
                        "paragraph": {"rich_text": [{"plain_text": "legacy content"}]},
                    },
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                return {}

        client = FakeClient()
        blocks = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}]

        upsert_freeze_packet_snapshot_section(client, "freeze-packet-page", blocks)

        self.assertEqual(
            [
                ("DELETE", "/v1/blocks/managed-callout", None),
                ("DELETE", "/v1/blocks/managed-heading", None),
                ("DELETE", "/v1/blocks/managed-divider", None),
                (
                    "PATCH",
                    "/v1/blocks/freeze-packet-page/children",
                    {"children": blocks, "position": {"type": "start"}},
                ),
            ],
            client.calls,
        )


if __name__ == "__main__":
    unittest.main()
