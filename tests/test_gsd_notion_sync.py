import argparse
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.gsd_notion_sync import (
    CommandResult,
    NotionClient,
    NotionWritebackTimeout,
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
    render_repo_dev_handoff_markdown,
    derive_compact_success_summary,
    derive_compact_success_summary_from_text,
    strongest_repo_success_summary,
    stronger_success_summary,
    success_summary_metrics,
    build_fallback_run_snapshot,
    ensure_live_active_pages,
    ensure_live_databases,
    effective_default_plan,
    fetch_review_snapshot_from_repo_docs,
    sync_repo_docs_from_snapshot,
    prune_stale_active_sync_page_blocks,
    page_matches_rendered_blocks,
    align_snapshot_with_local_phase,
    should_prefer_page_snapshot,
    should_prefer_snapshot,
    should_preserve_prior_success_summary,
    summarize_results,
    sync_repo_documents,
    build_local_run_snapshot,
    handle_run,
    handle_prepare_opus_review,
    upsert_managed_markdown_section,
    write_current_opus_review_brief_from_snapshot,
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

    def test_derive_compact_success_summary_from_validation_suite_command(self):
        results = [
            CommandResult(
                command="python3 tools/run_gsd_validation_suite.py --format json",
                returncode=0,
                stdout="""
{
  "command_count": 8,
  "results": [
    {
      "name": "unit_tests",
      "command": "python3 -m unittest discover -s tests -p test_*.py",
      "stderr": "Ran 175 tests in 20.000s\\n\\nOK",
      "stdout": ""
    },
    {
      "name": "demo_path_smoke",
      "command": "python3 tools/demo_path_smoke.py --format json",
      "stderr": "",
      "stdout": "{\\"completed_scenarios\\": 10, \\"failed_scenario\\": null, \\"scenario_count\\": 10}"
    }
  ]
}
""".strip(),
                stderr="",
                started_at="2026-04-10T00:00:00+00:00",
                ended_at="2026-04-10T00:00:05+00:00",
            )
        ]

        summary = derive_compact_success_summary(results)

        self.assertEqual("175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.", summary)

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

    def test_derive_compact_success_summary_from_human_readable_text(self):
        text = "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass."

        summary = derive_compact_success_summary_from_text(text)

        self.assertEqual("175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.", summary)

    def test_derive_compact_success_summary_from_archive_style_text(self):
        text = "\n".join(
            [
                "## 当前稳定证据",
                "- 单元测试：`175 tests OK`",
                "- demo smoke：`10 scenarios pass`",
                "- 共享验证检查：`8 / 8 pass`",
            ]
        )

        summary = derive_compact_success_summary_from_text(text)

        self.assertEqual("175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.", summary)

    def test_success_summary_metrics_and_stronger_summary(self):
        stronger = "175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass."
        weaker = "1/1 shared validation checks pass."

        self.assertEqual((175, 10, 8), success_summary_metrics(stronger))
        self.assertEqual((0, 0, 1), success_summary_metrics(weaker))
        self.assertEqual(stronger, stronger_success_summary(weaker, stronger))

    def test_should_preserve_prior_success_summary_when_current_run_is_narrower(self):
        self.assertTrue(
            should_preserve_prior_success_summary(
                "PASS. 1/1 shared validation checks pass.",
                "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            )
        )

        self.assertFalse(
            should_preserve_prior_success_summary(
                "PASS. 176 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
                "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            )
        )

    def test_strongest_repo_success_summary_prefers_archive_baseline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            freeze_path = root / "docs" / "freeze"
            freeze_path.mkdir(parents=True)
            (freeze_path / "2026-04-10-freeze-demo-packet.md").write_text(
                "- 当前 QA 摘要：`PASS. 1/1 shared validation checks pass.`\n",
                encoding="utf-8",
            )
            archive_path = freeze_path / "archive"
            archive_path.mkdir(parents=True)
            (archive_path / "2026-04-10-freeze-demo-packet-history.md").write_text(
                "\n".join(
                    [
                        "## 当前稳定证据",
                        "- 单元测试：`175 tests OK`",
                        "- demo smoke：`10 scenarios pass`",
                        "- 共享验证检查：`8 / 8 pass`",
                    ]
                ),
                encoding="utf-8",
            )

            summary = strongest_repo_success_summary(root, "1/1 shared validation checks pass.")

        self.assertEqual("175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.", summary)

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

    def test_ensure_live_databases_unarchives_archived_database_blocks(self):
        config = {
            "databases": {
                "plans": "plans-db",
                "runs": "runs-db",
            }
        }
        client = unittest.mock.Mock()
        client.request.side_effect = [
            {"archived": True, "in_trash": True},
            {"archived": False, "in_trash": False},
            {"archived": False, "in_trash": False},
        ]

        restored = ensure_live_databases(client, config)

        self.assertEqual({"plans": "plans-db"}, restored)
        self.assertEqual(
            [
                unittest.mock.call("GET", "/v1/blocks/plans-db"),
                unittest.mock.call("PATCH", "/v1/blocks/plans-db", {"archived": False}),
                unittest.mock.call("GET", "/v1/blocks/runs-db"),
            ],
            client.request.call_args_list,
        )

    def test_prune_stale_active_sync_page_blocks_removes_only_old_active_surface_children(self):
        config = {
            "pages": {
                "dashboard": "dashboard-page",
                "status": "current-status",
                "opus_brief": "current-brief",
                "freeze_packet": "current-freeze",
            }
        }
        client = unittest.mock.Mock()
        client.list_block_children.return_value = [
            {"id": "current-status", "type": "child_page", "child_page": {"title": "01 当前状态（自动同步）"}},
            {"id": "stale-status", "type": "child_page", "child_page": {"title": "01 当前状态（自动同步）"}},
            {"id": "stale-brief", "type": "child_page", "child_page": {"title": "09C 当前 Opus 4.6 审查简报"}},
            {"id": "other-page", "type": "child_page", "child_page": {"title": "别的页面"}},
        ]

        deleted = prune_stale_active_sync_page_blocks(client, config)

        self.assertEqual(["stale-status", "stale-brief"], deleted)
        delete_calls = [call.args[1] for call in client.request.call_args_list]
        self.assertEqual(
            ["/v1/blocks/stale-status", "/v1/blocks/stale-brief"],
            delete_calls,
        )

    def test_page_matches_rendered_blocks_ignores_preserved_child_page_blocks(self):
        client = unittest.mock.Mock()
        client.list_block_children.return_value = [
            {
                "id": "callout-1",
                "type": "callout",
                "callout": {"rich_text": [{"plain_text": "AUTO-SYNCED DASHBOARD SNAPSHOT"}]},
            },
            {
                "id": "bullet-1",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"plain_text": "当前阶段：P6"}]},
            },
            {
                "id": "child-status",
                "type": "child_page",
                "child_page": {"title": "01 当前状态（自动同步）"},
            },
        ]
        rendered_blocks = [
            {
                "object": "block",
                "type": "callout",
                "callout": {"rich_text": [{"text": {"content": "AUTO-SYNCED DASHBOARD SNAPSHOT"}}]},
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": "当前阶段：P6"}}]},
            },
        ]

        self.assertTrue(page_matches_rendered_blocks(client, "dashboard-page", rendered_blocks))

    def test_page_matches_rendered_blocks_detects_link_target_changes(self):
        client = unittest.mock.Mock()
        client.list_block_children.return_value = [
            {
                "id": "freeze-link",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "plain_text": "10 Freeze Demo Packet",
                            "href": "https://www.notion.so/old-freeze",
                        }
                    ]
                },
            }
        ]
        rendered_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "10 Freeze Demo Packet",
                                "link": {"url": "https://www.notion.so/new-freeze"},
                            }
                        }
                    ]
                },
            }
        ]

        self.assertFalse(page_matches_rendered_blocks(client, "status-page", rendered_blocks))

    def test_write_current_opus_review_brief_second_pass_rewrites_cross_links_after_replacements(self):
        config = {
            "root_page_url": "https://www.notion.so/root",
            "pages": {
                "dashboard": "dashboard-page",
                "constitution": "constitution-page",
                "status": "old-status",
                "opus_brief": "old-brief",
                "freeze_packet": "old-freeze",
                "control_plane": "control-plane-page",
                "opus_protocol": "opus-protocol-page",
            },
            "databases": {
                "plans": "plans-db",
                "runs": "runs-db",
                "qa": "qa-db",
                "gates": "gates-db",
                "gaps": "gaps-db",
                "assets": "assets-db",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
            "default_plan": "P6-18 Refresh Active Sync Surfaces When Link Targets Move",
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
        }
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="Close stale control-plane drift.",
            active_phase_summary="P6 is active.",
            latest_verified_plan="P6-18 Refresh Active Sync Surfaces When Link Targets Move",
            latest_success_run="P6-18 active sync link target refresh",
            latest_failed_run=None,
            latest_passing_qa="P6-18 active sync link target refresh QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            latest_success_run_notes="Focused control-plane maintenance run passed.",
            latest_passing_qa_summary="PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
        )
        client = unittest.mock.Mock()
        replacement_ids = {
            "opus_brief": "new-brief",
            "status": "new-status",
            "freeze_packet": "new-freeze",
        }

        def fake_replace_active_sync_page(_client, live_config, *, key, title, blocks, config_path=None):
            live_config["pages"][key] = replacement_ids[key]
            return replacement_ids[key]

        with (
            patch("tools.gsd_notion_sync.replace_active_sync_page", side_effect=fake_replace_active_sync_page),
            patch("tools.gsd_notion_sync.prune_stale_active_sync_page_blocks"),
            patch("tools.gsd_notion_sync.page_matches_rendered_blocks", return_value=True),
        ):
            write_current_opus_review_brief_from_snapshot(
                client,
                config,
                snapshot=snapshot,
                activate_gate=False,
                config_path=Path("/tmp/notion_control_plane.json"),
            )

        rewritten_page_ids = [call.args[0] for call in client.replace_page_body.call_args_list]
        self.assertIn("new-brief", rewritten_page_ids)
        self.assertIn("new-status", rewritten_page_ids)
        self.assertIn("new-freeze", rewritten_page_ids)

    def test_replace_active_sync_page_updates_existing_writable_page_in_place(self):
        from tools.gsd_notion_sync import replace_active_sync_page

        config = {
            "pages": {
                "dashboard": "dashboard-page",
                "status": "live-status",
            }
        }
        client = unittest.mock.Mock()
        client.get_page.return_value = {"archived": False, "in_trash": False}
        blocks = [
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": "当前阶段：P6"}}]},
            }
        ]

        with patch("tools.gsd_notion_sync.page_matches_rendered_blocks", return_value=False):
            page_id_value = replace_active_sync_page(
                client,
                config,
                key="status",
                title="01 当前状态（自动同步）",
                blocks=blocks,
            )

        self.assertEqual("live-status", page_id_value)
        client.create_child_page.assert_not_called()
        client.update_page_properties.assert_called_once()
        client.replace_page_body.assert_called_once_with("live-status", blocks)
        self.assertEqual("live-status", config["pages"]["status"])

    def test_replace_active_sync_page_creates_new_page_when_existing_page_archived(self):
        from tools.gsd_notion_sync import replace_active_sync_page

        config = {
            "pages": {
                "dashboard": "dashboard-page",
                "status": "archived-status",
            }
        }
        client = unittest.mock.Mock()
        client.get_page.side_effect = [
            {"archived": True, "in_trash": True},
            {"archived": True, "in_trash": True},
        ]
        client.create_child_page.return_value = "new-status"
        blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": "new body"}}]},
            }
        ]

        page_id_value = replace_active_sync_page(
            client,
            config,
            key="status",
            title="01 当前状态（自动同步）",
            blocks=blocks,
        )

        self.assertEqual("new-status", page_id_value)
        client.create_child_page.assert_called_once_with("dashboard-page", "01 当前状态（自动同步）")
        self.assertEqual("new-status", config["pages"]["status"])

    def test_replace_active_sync_page_falls_back_to_new_page_when_in_place_rewrite_times_out(self):
        from tools.gsd_notion_sync import replace_active_sync_page

        config = {
            "pages": {
                "dashboard": "dashboard-page",
                "status": "live-status",
            }
        }
        client = unittest.mock.Mock()
        client.get_page.side_effect = [
            {"archived": False, "in_trash": False},
            {"archived": False, "in_trash": False},
        ]
        client.create_child_page.return_value = "replacement-status"
        client.request.return_value = {}
        blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": "replacement body"}}]},
            }
        ]

        with (
            patch("tools.gsd_notion_sync.page_matches_rendered_blocks", return_value=False),
            patch(
                "tools.gsd_notion_sync.rewrite_active_sync_page_body",
                side_effect=NotionWritebackTimeout("Notion writeback exceeded 90s deadline."),
            ),
        ):
            page_id_value = replace_active_sync_page(
                client,
                config,
                key="status",
                title="01 当前状态（自动同步）",
                blocks=blocks,
            )

        self.assertEqual("replacement-status", page_id_value)
        client.create_child_page.assert_called_once_with("dashboard-page", "01 当前状态（自动同步）")
        client.archive_page.assert_called_once_with("live-status")
        self.assertEqual("replacement-status", config["pages"]["status"])

    def test_clip_preserves_short_text_and_truncates_long_text(self):
        self.assertEqual("short", clip("short", limit=10))
        clipped = clip("x" * 30, limit=20)
        self.assertLessEqual(len(clipped), 20)
        self.assertIn("truncated", clipped)

    def test_effective_default_plan_prefers_latest_local_plan_from_active_phase(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            planning_dir = root / ".planning"
            phase_dir = planning_dir / "phases" / "06-reconcile-control-tower-and-freeze-demo-packet"
            phase_dir.mkdir(parents=True)
            (planning_dir / "ROADMAP.md").write_text(
                "\n".join(
                    [
                        "# Roadmap",
                        "",
                        "## Phase P5: Done Phase",
                        "",
                        "Status: Done",
                        "",
                        "## Phase P6: Reconcile Control Tower And Freeze Demo Packet",
                        "",
                        "Status: Active",
                    ]
                ),
                encoding="utf-8",
            )
            (phase_dir / "06-11-PLAN.md").write_text(
                "# P6-11 Plan - Let Repo Docs Follow The Fresher Dashboard Snapshot\n",
                encoding="utf-8",
            )
            (phase_dir / "06-12-PLAN.md").write_text(
                "# P6-12 Plan - De-duplicate Dashboard Active Surface Links\n",
                encoding="utf-8",
            )

            plan = effective_default_plan({"default_plan": "fallback-plan"}, cwd=root)

            self.assertEqual("P6-12 De-duplicate Dashboard Active Surface Links", plan)

    def test_effective_default_plan_falls_back_to_config_when_no_active_phase_plan_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".planning").mkdir(parents=True)
            (root / ".planning" / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")

            plan = effective_default_plan({"default_plan": "fallback-plan"}, cwd=root)

            self.assertEqual("fallback-plan", plan)

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
        self.assertIn("当前开发架构与执行规则", joined)
        self.assertIn("`runner.py` / `SimulationRunner`", joined)
        self.assertIn("FlyByWire / A320", joined)
        self.assertIn("`gsd_notion_sync.py run` 写回", joined)
        self.assertIn("control-plane gap / blocker", joined)
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
            evidence_mode="dashboard_fallback",
            evidence_note="共享数据库与独立活跃子页当前不可达；dashboard 仍是当前 live truth。",
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
        self.assertIn("当前证据模式：dashboard-only degraded mode", joined)
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

    def test_render_current_review_brief_blocks_include_evidence_mode_fact(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-21 显式化数据库降级证据模式",
            latest_success_run="GitHub GSD automation 24250000000",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24250000000 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="active_pages_fallback",
            evidence_note="共享 Notion 数据库当前不可达；当前快照由 dashboard 与活跃 status / 09C / freeze 页面恢复。",
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

        brief = build_current_review_brief(snapshot, config)
        blocks = render_current_review_brief_blocks(brief, snapshot, config)

        joined = "\n".join(
            item["text"]["content"]
            for block in blocks
            for payload in block.values()
            if isinstance(payload, dict) and "rich_text" in payload
            for item in payload["rich_text"]
        )

        self.assertIn("当前证据模式：active-page degraded mode", joined)
        self.assertIn("共享 Notion 数据库当前不可达", joined)

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
        self.assertIn("当前开发架构与执行规则", joined)
        self.assertIn("adapter interface", joined)
        self.assertIn("prepare-opus-review", joined)

    def test_render_status_page_blocks_switch_to_workbench_guidance_for_p7(self):
        snapshot = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="把 workbench primitive 收成连续工程流",
            active_phase_summary="P7 正在执行",
            latest_verified_plan="P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            latest_success_run="P7-07 workbench bundle baseline",
            latest_failed_run=None,
            latest_passing_qa="P7-07 workbench bundle baseline QA",
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

        joined = "\n".join(
            item["text"]["content"]
            for block in render_status_page_blocks(build_current_review_brief(snapshot, config), snapshot, config)
            for value in block.values()
            if isinstance(value, dict) and "rich_text" in value
            for item in value["rich_text"]
        )

        self.assertIn("统一 engineer-facing workflow", joined)
        self.assertIn("必要时把新的 workbench artifact 同步回 repo / Notion 控制面", joined)
        self.assertNotIn("在 P6 收口前，不继续扩大 P7 的实现面。", joined)

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
        self.assertIn("当前证据模式：`shared-database live mode`", text)
        self.assertIn("## 当前开发架构与执行规则", text)
        self.assertIn("FlyByWire / A320", text)
        self.assertIn("`prepare-opus-review`", text)

    def test_render_repo_coordination_plan_markdown_includes_fallback_evidence_note(self):
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-21 显式化数据库降级证据模式",
            latest_success_run="GitHub GSD automation 24250000000",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24250000000 QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="active_pages_fallback",
            evidence_note="共享 Notion 数据库当前不可达；当前快照由 dashboard 与活跃 status / 09C / freeze 页面恢复。",
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

        text = render_repo_coordination_plan_markdown(build_current_review_brief(snapshot, config), snapshot, config)

        self.assertIn("当前证据模式：`active-page degraded mode`", text)
        self.assertIn("共享 Notion 数据库当前不可达", text)

    def test_render_repo_coordination_plan_markdown_switches_to_workbench_focus_for_p7(self):
        snapshot = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="把 workbench primitive 收成连续工程流",
            active_phase_summary="P7 正在执行",
            latest_verified_plan="P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            latest_success_run="P7-07 workbench bundle baseline",
            latest_failed_run=None,
            latest_passing_qa="P7-07 workbench bundle baseline QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
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

        text = render_repo_coordination_plan_markdown(build_current_review_brief(snapshot, config), snapshot, config)

        self.assertIn("spec-driven workbench 收成统一 engineer-facing workflow", text)
        self.assertNotIn("继续收口控制塔与 freeze/demo packet 的残余漂移", text)

    def test_render_repo_dev_handoff_markdown_includes_guardrails(self):
        snapshot = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="把 workbench primitive 收成连续工程流",
            active_phase_summary="P7 正在执行",
            latest_verified_plan="P7-29 Harden Notion Control-Plane Development Rules",
            latest_success_run="P7-29 notion control-plane rules sync",
            latest_failed_run=None,
            latest_passing_qa="P7-29 notion control-plane rules sync QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
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

        text = render_repo_dev_handoff_markdown(build_current_review_brief(snapshot, config), snapshot, config)

        self.assertIn("## 当前开发架构与执行规则", text)
        self.assertIn("`gsd_notion_sync.py run` 写回", text)
        self.assertIn("adapter interface", text)
        self.assertIn("Notion 写回降级、部分失败或超时都应被当成 control-plane gap / blocker", text)

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
            self.assertIn("当前开发架构与执行规则", plan_text)
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

    def test_fetch_review_snapshot_compacts_verbose_validation_suite_summaries(self):
        long_validation_summary = "\n".join(
            [
                "$ python3 tools/run_gsd_validation_suite.py --format json",
                "",
                "exit=0",
                "",
                "stdout:",
                "{",
                '  "command_count": 8,',
                '  "results": [',
                "    {",
                '      "name": "unit_tests",',
                '      "command": "python3 -m unittest discover -s tests -p test_*.py",',
                '      "stderr": "Ran 175 tests in 23.695s\\n\\nOK",',
                '      "stdout": ""',
                "    },",
                "    {",
                '      "name": "demo_path_smoke",',
                '      "command": "python3 tools/demo_path_smoke.py --format json",',
                '      "stderr": "",',
                '      "stdout": "{\\"completed_scenarios\\": 10, \\"failed_scenario\\": null, \\"scenario_count\\": 10}"',
                "    }",
                "  ]",
                "}",
            ]
        )

        class FakeClient:
            def query_database(self, database_id, *, filter_payload=None, sorts=None, page_size=10):
                if database_id == "roadmap-db":
                    return [
                        {
                            "id": "phase-id",
                            "properties": {
                                "Round": {"type": "title", "title": [{"plain_text": "P7 Build A Spec-Driven Control Analysis Workbench"}]},
                                "Goal": {"type": "rich_text", "rich_text": [{"plain_text": "Make workbench sync reliable."}]},
                                "Summary": {"type": "rich_text", "rich_text": [{"plain_text": "P7 is active."}]},
                            },
                        }
                    ]
                if database_id == "plans-db":
                    return [
                        {
                            "id": "plan-id",
                            "properties": {
                                "Plan": {
                                    "type": "title",
                                    "title": [{"plain_text": "P7-16 Show Latest-Vs-Replay Differences In The Browser Workbench"}],
                                }
                            },
                        }
                    ]
                if database_id == "runs-db":
                    if filter_payload == {
                        "and": [
                            {"property": "Status", "select": {"equals": "Succeeded"}},
                            {"property": "Executor", "select": {"equals": "GitHub Action"}},
                        ]
                    }:
                        return [
                            {
                                "id": "run-id",
                                "properties": {
                                    "Run": {"type": "title", "title": [{"plain_text": "GitHub GSD automation 24237800855"}]},
                                    "Notes": {"type": "rich_text", "rich_text": [{"plain_text": long_validation_summary}]},
                                },
                            }
                        ]
                    if filter_payload == {
                        "and": [
                            {"property": "Status", "select": {"equals": "Failed"}},
                            {"property": "Executor", "select": {"equals": "GitHub Action"}},
                        ]
                    }:
                        return []
                    if filter_payload == {"property": "Status", "select": {"equals": "Succeeded"}}:
                        return []
                    if filter_payload == {"property": "Status", "select": {"equals": "Failed"}}:
                        return []
                if database_id == "qa-db":
                    if filter_payload == {"property": "Run", "title": {"equals": "GitHub GSD automation 24237800855 QA"}}:
                        return [
                            {
                                "id": "qa-id",
                                "properties": {
                                    "Run": {"type": "title", "title": [{"plain_text": "GitHub GSD automation 24237800855 QA"}]},
                                    "Summary": {"type": "rich_text", "rich_text": [{"plain_text": long_validation_summary}]},
                                },
                            }
                        ]
                    return []
                if database_id == "gates-db":
                    return [
                        {
                            "id": "gate-id",
                            "properties": {
                                "Gate": {"type": "title", "title": [{"plain_text": "OPUS-4.6 周期审查 Gate"}]},
                                "Status": {"type": "select", "select": {"name": "Approved"}},
                            },
                        }
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

        self.assertEqual(
            "175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            snapshot.latest_success_run_notes,
        )
        self.assertEqual(
            "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            snapshot.latest_passing_qa_summary,
        )

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

    def test_align_snapshot_with_local_phase_overrides_stale_database_live_phase(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            planning_dir = root / ".planning"
            planning_dir.mkdir(parents=True)
            (planning_dir / "ROADMAP.md").write_text(
                "\n".join(
                    [
                        "## Phase P6: Reconcile Control Tower And Freeze Demo Packet",
                        "",
                        "Status: Done",
                        "",
                        "## Phase P7: Build A Spec-Driven Control Analysis Workbench",
                        "",
                        "Status: Active",
                    ]
                ),
                encoding="utf-8",
            )
            snapshot = ReviewSnapshot(
                active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
                active_phase_goal="Close stale control-plane drift.",
                active_phase_summary="Shared database is reachable but its active phase row is stale.",
                latest_verified_plan="P7-16 Show Latest-Vs-Replay Differences In The Browser Workbench",
                latest_success_run="GitHub GSD automation 24237800855",
                latest_failed_run=None,
                latest_passing_qa="GitHub GSD automation 24237800855 QA",
                gate_page_id="gate-id",
                gate_name="OPUS-4.6 周期审查 Gate",
                gate_status="Approved",
                ready_task_id=None,
                ready_task=None,
                open_gap_titles=(),
                stale_gap_titles=(),
                evidence_mode="database_live",
                evidence_note="共享 Notion 数据库可达；phase / run / QA / gate 取自实时数据库记录。",
            )

            aligned = align_snapshot_with_local_phase(snapshot, cwd=root)

        self.assertEqual("P7 Build A Spec-Driven Control Analysis Workbench", aligned.active_phase)
        self.assertIn("本地 roadmap 纠偏", aligned.evidence_note)
        self.assertIsNone(aligned.latest_failed_run)
        self.assertEqual("Approved", aligned.gate_status)
        self.assertEqual("database_live", aligned.evidence_mode)

    def test_write_current_opus_review_brief_from_snapshot_aligns_review_target_with_local_phase(self):
        config = {
            "root_page_url": "https://www.notion.so/root",
            "pages": {
                "dashboard": "dashboard-page",
                "constitution": "constitution-page",
                "status": "status-page",
                "opus_brief": "brief-page",
                "freeze_packet": "freeze-page",
                "control_plane": "control-plane-page",
                "opus_protocol": "opus-protocol-page",
            },
            "databases": {
                "plans": "plans-db",
                "runs": "runs-db",
                "qa": "qa-db",
                "gates": "gates-db",
                "gaps": "gaps-db",
                "assets": "assets-db",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
            "default_plan": "P7-17 Add A Side-By-Side Replay Comparison Board To The Browser Workbench",
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
        }
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="Close stale control-plane drift.",
            active_phase_summary="Database row is stale.",
            latest_verified_plan="P7-17 Add A Side-By-Side Replay Comparison Board To The Browser Workbench",
            latest_success_run="P7-17 side-by-side replay comparison board",
            latest_failed_run=None,
            latest_passing_qa="P7-17 side-by-side replay comparison board QA",
            gate_page_id="gate-page-id",
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="database_live",
            evidence_note="共享 Notion 数据库可达；phase / run / QA / gate 取自实时数据库记录。",
        )
        client = unittest.mock.Mock()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            planning_dir = root / ".planning"
            planning_dir.mkdir(parents=True)
            (planning_dir / "ROADMAP.md").write_text(
                "\n".join(
                    [
                        "## Phase P6: Reconcile Control Tower And Freeze Demo Packet",
                        "",
                        "Status: Done",
                        "",
                        "## Phase P7: Build A Spec-Driven Control Analysis Workbench",
                        "",
                        "Status: Active",
                    ]
                ),
                encoding="utf-8",
            )

            with (
                patch("tools.gsd_notion_sync.replace_active_sync_page", side_effect=lambda _client, live_config, *, key, title, blocks, config_path=None: live_config["pages"][key]),
                patch("tools.gsd_notion_sync.prune_stale_active_sync_page_blocks"),
            ):
                payload = write_current_opus_review_brief_from_snapshot(
                    client,
                    config,
                    snapshot=snapshot,
                    activate_gate=False,
                    config_path=Path("/tmp/notion_control_plane.json"),
                    cwd=root,
                )

        self.assertEqual(
            "P7 Build A Spec-Driven Control Analysis Workbench / P7-17 Add A Side-By-Side Replay Comparison Board To The Browser Workbench",
            payload["review_target"],
        )

    def test_should_prefer_snapshot_prefers_higher_phase_when_other_evidence_is_similar(self):
        primary = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="",
            active_phase_summary="P6 snapshot",
            latest_verified_plan="P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            latest_success_run="P7-07 workbench bundle timeout fallback hardening",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="active_pages_fallback",
        )
        candidate = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="",
            active_phase_summary="P7 snapshot",
            latest_verified_plan="P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            latest_success_run="P7-07 workbench bundle timeout fallback hardening",
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="repo_docs_fallback",
        )

        self.assertTrue(
            should_prefer_snapshot(
                primary,
                candidate,
                {"default_plan": "P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact"},
            )
        )

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
        self.assertEqual("dashboard_fallback", snapshot.evidence_mode)

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
                patch(
                    "tools.gsd_notion_sync.sync_repo_docs_from_snapshot",
                    return_value=[],
                ) as repo_sync_mock,
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
        self.assertEqual("written", payload["repo_doc_sync"])
        self.assertIn("HTTP 404", payload["notion_error"])
        self.assertEqual("Succeeded", payload["status"])
        fallback_snapshot = fallback_mock.call_args.kwargs["snapshot"]
        self.assertEqual("P6-03 Freeze Demo Packet 自动快照同步", fallback_snapshot.latest_verified_plan)
        self.assertEqual("GitHub GSD automation 24239999999", fallback_snapshot.latest_success_run)
        self.assertEqual(fallback_snapshot, repo_sync_mock.call_args.args[1])

    def test_handle_run_success_syncs_repo_docs_from_success_snapshot(self):
        args = argparse.Namespace(
            cwd=".",
            plan_id="P6-14 为 run 写回链增加超时 fallback",
            title="GitHub GSD automation 24250000000",
            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
            dry_run=False,
            opus_gate=False,
            format="json",
            config=str(Path(".planning/notion_control_plane.json")),
        )
        config = {"default_plan": "fallback-plan"}
        results = [
            CommandResult(
                command=args.command[0],
                returncode=0,
                stdout="PASS",
                stderr="",
                started_at="2026-04-11T00:00:00+00:00",
                ended_at="2026-04-11T00:00:05+00:00",
            )
        ]
        success_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P6-14 为 run 写回链增加超时 fallback",
            latest_success_run="GitHub GSD automation 24250000000",
            latest_failed_run=None,
            latest_passing_qa="GitHub GSD automation 24250000000 QA",
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
                patch("tools.gsd_notion_sync.run_commands", return_value=results),
                patch("tools.gsd_notion_sync.ensure_live_active_pages"),
                patch("tools.gsd_notion_sync.write_notion_outcome", return_value={"opus_review_brief": {"intervention_kind": "当前无需 Opus 审查"}}),
                patch("tools.gsd_notion_sync.build_fallback_run_snapshot", return_value=success_snapshot),
                patch("tools.gsd_notion_sync.active_page_unavailable_keys", return_value=()),
                patch("tools.gsd_notion_sync.sync_repo_docs_from_snapshot", return_value=[]) as repo_sync_mock,
                patch("tools.gsd_notion_sync.output_run_result") as output_mock,
            ):
                exit_code = handle_run(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        payload = output_mock.call_args.args[1]
        self.assertEqual("written", payload["notion"])
        self.assertEqual("written", payload["repo_doc_sync"])
        self.assertEqual(success_snapshot, repo_sync_mock.call_args.args[1])

    def test_handle_run_restores_archived_databases_before_writeback(self):
        args = argparse.Namespace(
            cwd=".",
            plan_id="P7-16 Show Latest-Vs-Replay Differences In The Browser Workbench",
            title="P7-16 database restore verification",
            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
            dry_run=False,
            opus_gate=False,
            format="json",
            config=str(Path(".planning/notion_control_plane.json")),
        )
        config = {"default_plan": "fallback-plan"}
        results = [
            CommandResult(
                command=args.command[0],
                returncode=0,
                stdout="PASS",
                stderr="",
                started_at="2026-04-11T00:00:00+00:00",
                ended_at="2026-04-11T00:00:05+00:00",
            )
        ]
        success_snapshot = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="Make workbench acceptance trustworthy.",
            active_phase_summary="P7 正在执行",
            latest_verified_plan="P7-16 Show Latest-Vs-Replay Differences In The Browser Workbench",
            latest_success_run="P7-16 database restore verification",
            latest_failed_run=None,
            latest_passing_qa="P7-16 database restore verification QA",
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
                patch("tools.gsd_notion_sync.run_commands", return_value=results),
                patch("tools.gsd_notion_sync.ensure_live_databases", return_value={"plans": "plans-db"}) as restore_mock,
                patch("tools.gsd_notion_sync.ensure_live_active_pages"),
                patch("tools.gsd_notion_sync.write_notion_outcome", return_value={}),
                patch("tools.gsd_notion_sync.build_fallback_run_snapshot", return_value=success_snapshot),
                patch("tools.gsd_notion_sync.active_page_unavailable_keys", return_value=()),
                patch("tools.gsd_notion_sync.sync_repo_docs_from_snapshot", return_value=[]),
                patch("tools.gsd_notion_sync.output_run_result") as output_mock,
            ):
                exit_code = handle_run(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        restore_mock.assert_called_once()
        payload = output_mock.call_args.args[1]
        self.assertEqual({"plans": "plans-db"}, payload["restored_databases"])

    def test_handle_run_timeout_skips_followup_notion_calls_and_still_syncs_repo_docs(self):
        args = argparse.Namespace(
            cwd=".",
            plan_id="P6-14 Add Timeout Fallback To Run Writeback",
            title="P6-14 run writeback fallback baseline",
            command=["PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py"],
            dry_run=False,
            opus_gate=False,
            format="json",
            config=str(Path(".planning/notion_control_plane.json")),
        )
        config = {"default_plan": "fallback-plan"}
        results = [
            CommandResult(
                command=args.command[0],
                returncode=0,
                stdout="PASS",
                stderr="",
                started_at="2026-04-11T00:00:00+00:00",
                ended_at="2026-04-11T00:00:05+00:00",
            )
        ]
        timeout_snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="Recovered locally after timeout.",
            latest_verified_plan="P6-14 Add Timeout Fallback To Run Writeback",
            latest_success_run="P6-14 run writeback fallback baseline",
            latest_failed_run=None,
            latest_passing_qa="P6-14 run writeback fallback baseline QA",
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
                patch("tools.gsd_notion_sync.run_commands", return_value=results),
                patch("tools.gsd_notion_sync.ensure_live_active_pages"),
                patch(
                    "tools.gsd_notion_sync.write_notion_outcome",
                    side_effect=NotionWritebackTimeout("Notion writeback exceeded 12s deadline."),
                ),
                patch("tools.gsd_notion_sync.build_local_run_snapshot", return_value=timeout_snapshot) as local_snapshot_mock,
                patch("tools.gsd_notion_sync.build_fallback_run_snapshot") as network_fallback_mock,
                patch("tools.gsd_notion_sync.write_current_opus_review_brief_from_snapshot") as brief_mock,
                patch("tools.gsd_notion_sync.sync_repo_docs_from_snapshot", return_value=[]) as repo_sync_mock,
                patch("tools.gsd_notion_sync.output_run_result") as output_mock,
            ):
                exit_code = handle_run(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        payload = output_mock.call_args.args[1]
        self.assertEqual("partial", payload["notion"])
        self.assertEqual("skipped_after_timeout", payload["notion_fallback"])
        self.assertEqual("written", payload["repo_doc_sync"])
        self.assertIn("12s deadline", payload["notion_error"])
        local_snapshot_mock.assert_called_once()
        self.assertEqual(timeout_snapshot, repo_sync_mock.call_args.args[1])
        network_fallback_mock.assert_not_called()
        brief_mock.assert_not_called()

    def test_build_local_run_snapshot_uses_repo_docs_without_notion_client(self):
        results = [
            CommandResult(
                command="python3 -m unittest discover -s tests -p test_*.py",
                returncode=0,
                stdout="",
                stderr="Ran 187 tests in 21.157s\n\nOK",
                started_at="2026-04-10T00:00:00+00:00",
                ended_at="2026-04-10T00:00:05+00:00",
            )
        ]

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            freeze_path = root / "docs" / "freeze"
            freeze_path.mkdir(parents=True)
            (freeze_path / "2026-04-10-freeze-demo-packet.md").write_text(
                "\n".join(
                    [
                        "# Freeze Packet",
                        "",
                        "- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`",
                        "- 当前已验证 Plan：`P6-13 Make Default Plan Follow The Active Phase`",
                        "- 最近成功执行证据：`GitHub GSD automation 24250000000`",
                        "- 当前 Gate：`OPUS-4.6 周期审查 Gate（Approved）`",
                    ]
                ),
                encoding="utf-8",
            )

            snapshot = build_local_run_snapshot(
                {"default_plan": "fallback-plan", "default_review_gate": "OPUS-4.6 周期审查 Gate"},
                cwd=root,
                plan_id="P6-14 Add Timeout Fallback To Run Writeback",
                title="P6-14 run writeback fallback baseline",
                results=results,
                summary=summarize_results(results),
            )

        self.assertEqual("P6 Reconcile Control Tower And Freeze Demo Packet", snapshot.active_phase)
        self.assertEqual("P6-14 Add Timeout Fallback To Run Writeback", snapshot.latest_verified_plan)
        self.assertEqual("P6-14 run writeback fallback baseline", snapshot.latest_success_run)

    def test_build_local_run_snapshot_preserves_stronger_prior_validation_summary(self):
        results = [
            CommandResult(
                command="PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py",
                returncode=0,
                stdout="PASS",
                stderr="",
                started_at="2026-04-11T00:00:00+00:00",
                ended_at="2026-04-11T00:00:05+00:00",
            )
        ]

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            freeze_path = root / "docs" / "freeze"
            freeze_path.mkdir(parents=True)
            (freeze_path / "2026-04-10-freeze-demo-packet.md").write_text(
                "\n".join(
                    [
                        "# Freeze Packet",
                        "",
                        "- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`",
                        "- 当前已验证 Plan：`P6-13 Make Default Plan Follow The Active Phase`",
                        "- 最近成功执行证据：`GitHub GSD automation 24250000000`",
                        "- 当前 Gate：`OPUS-4.6 周期审查 Gate（Approved）`",
                        "- 当前 QA 摘要：`PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`",
                    ]
                ),
                encoding="utf-8",
            )

            snapshot = build_local_run_snapshot(
                {"default_plan": "fallback-plan", "default_review_gate": "OPUS-4.6 周期审查 Gate"},
                cwd=root,
                plan_id="P6-15 Preserve Stronger Validation Baseline",
                title="P6-15 validation baseline preservation",
                results=results,
                summary=summarize_results(results),
            )

        self.assertEqual(
            "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            snapshot.latest_passing_qa_summary,
        )
        self.assertIn("Carried forward the stronger shared validation baseline", snapshot.latest_success_run_notes)

    def test_build_fallback_run_snapshot_carries_forward_stronger_success_summary(self):
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
            "Focused control-plane maintenance run passed. Carried forward the stronger shared validation baseline: "
            "271 tests OK and 8/8 shared validation checks pass.",
            fallback.latest_success_run_notes,
        )
        self.assertEqual(
            "PASS. 271 tests OK and 8/8 shared validation checks pass.",
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

    def test_handle_prepare_opus_review_reports_restored_databases(self):
        args = argparse.Namespace(activate_gate=False, dry_run=True, format="json")
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            }
        }
        snapshot = ReviewSnapshot(
            active_phase="P7 Build A Spec-Driven Control Analysis Workbench",
            active_phase_goal="Keep workbench truth aligned.",
            active_phase_summary="P7 正在执行",
            latest_verified_plan="P7-16 Show Latest-Vs-Replay Differences In The Browser Workbench",
            latest_success_run="P7-16 latest-vs-replay workbench differences",
            latest_failed_run=None,
            latest_passing_qa="P7-16 latest-vs-replay workbench differences QA",
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
                patch("tools.gsd_notion_sync.ensure_live_databases", return_value={"plans": "plans-db"}) as restore_mock,
                patch("tools.gsd_notion_sync.fetch_review_snapshot", return_value=snapshot),
                patch("tools.gsd_notion_sync.output_review_result") as output_mock,
            ):
                exit_code = handle_prepare_opus_review(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        restore_mock.assert_called_once()
        payload = output_mock.call_args.args[1]
        self.assertEqual({"plans": "plans-db"}, payload["restored_databases"])

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
                patch(
                    "tools.gsd_notion_sync.fetch_review_snapshot_from_repo_docs",
                    side_effect=RuntimeError("Repo freeze packet missing"),
                ),
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

    def test_handle_prepare_opus_review_aligns_degraded_phase_with_local_roadmap(self):
        args = argparse.Namespace(activate_gate=False, dry_run=True, format="json")
        config = {
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
            "default_plan": "P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
        }
        snapshot = ReviewSnapshot(
            active_phase="P6 Reconcile Control Tower And Freeze Demo Packet",
            active_phase_goal="对齐控制塔真值与冻结包",
            active_phase_summary="P6 正在执行",
            latest_verified_plan="P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            latest_success_run="P7-07 workbench bundle timeout fallback hardening",
            latest_failed_run=None,
            latest_passing_qa="P7-07 workbench bundle timeout fallback hardening QA",
            gate_page_id=None,
            gate_name="OPUS-4.6 周期审查 Gate",
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="active_pages_fallback",
        )

        old_env = dict(os.environ)
        old_cwd = Path.cwd()
        try:
            os.environ["NOTION_API_KEY"] = "test-token"
            with tempfile.TemporaryDirectory() as temp_dir:
                cwd = Path(temp_dir)
                planning_dir = cwd / ".planning"
                planning_dir.mkdir(parents=True, exist_ok=True)
                (planning_dir / "ROADMAP.md").write_text(
                    "\n".join(
                        [
                            "## Phase P6: Reconcile Control Tower And Freeze Demo Packet",
                            "Status: Done",
                            "",
                            "## Phase P7: Build A Spec-Driven Control Analysis Workbench",
                            "Status: Active",
                        ]
                    ),
                    encoding="utf-8",
                )
                os.chdir(cwd)
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
            os.chdir(old_cwd)
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        self.assertEqual(1, fallback_mock.call_count)
        payload = output_mock.call_args.args[1]
        self.assertEqual(
            "P7 Build A Spec-Driven Control Analysis Workbench / P7-07 Bundle The Workbench Chain Into A Single Engineer Artifact",
            payload["review_target"],
        )

    def test_handle_prepare_opus_review_falls_back_to_repo_docs_on_timeout(self):
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
            active_phase_summary="Recovered from repo docs",
            latest_verified_plan="P6-15 Preserve The Stronger Validation Baseline",
            latest_success_run="P6-15 validation baseline preservation",
            latest_failed_run=None,
            latest_passing_qa="P6-15 validation baseline preservation QA",
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
                    side_effect=NotionWritebackTimeout("Notion writeback exceeded 18s deadline."),
                ),
                patch("tools.gsd_notion_sync.fetch_review_snapshot_from_repo_docs", return_value=snapshot) as repo_mock,
                patch("tools.gsd_notion_sync.output_review_result") as output_mock,
            ):
                exit_code = handle_prepare_opus_review(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        repo_mock.assert_called_once()
        payload = output_mock.call_args.args[1]
        self.assertEqual("P6-15 validation baseline preservation", payload["latest_success_run"])
        self.assertEqual("Approved", payload["gate_status"])

    def test_handle_prepare_opus_review_write_timeout_returns_timeout_fallback_payload(self):
        args = argparse.Namespace(activate_gate=False, dry_run=False, format="json", config=str(Path(".planning/notion_control_plane.json")))
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
            latest_verified_plan="P6-15 Preserve The Stronger Validation Baseline",
            latest_success_run="P6-15 validation baseline preservation",
            latest_failed_run=None,
            latest_passing_qa="P6-15 validation baseline preservation QA",
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
                patch("tools.gsd_notion_sync.fetch_review_snapshot", return_value=snapshot),
                patch(
                    "tools.gsd_notion_sync.ensure_live_active_pages",
                    side_effect=NotionWritebackTimeout("Notion writeback exceeded 18s deadline."),
                ),
                patch("tools.gsd_notion_sync.write_current_opus_review_brief_from_snapshot") as write_mock,
                patch("tools.gsd_notion_sync.output_review_result") as output_mock,
            ):
                exit_code = handle_prepare_opus_review(args, config)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        write_mock.assert_not_called()
        payload = output_mock.call_args.args[1]
        self.assertTrue(payload["notion"]["timeout_fallback"])
        self.assertEqual(
            "P8 Runtime Generalization Proof / P6-15 Preserve The Stronger Validation Baseline",
            payload["review_target"],
        )

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

    def test_fetch_review_snapshot_from_repo_docs_lifts_stronger_archive_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            freeze_path = cwd / "docs/freeze/2026-04-10-freeze-demo-packet.md"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(
                "# Freeze Packet\n\n"
                "- 当前阶段：`P6 Reconcile Control Tower And Freeze Demo Packet`\n"
                "- 当前已验证 Plan：`P6-15 Preserve The Stronger Validation Baseline`\n"
                "- 最近成功执行证据：`P6-15 validation baseline preservation`\n"
                "- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`\n"
                "- 当前 Opus 状态：`当前无需 Opus 审查`\n"
                "- Open Gap 数量：`0`\n"
                "- 当前 QA 摘要：`PASS. 1/1 shared validation checks pass.`\n"
                "- 当前运行摘要：`1/1 shared validation checks pass.`\n",
                encoding="utf-8",
            )
            archive_path = cwd / "docs/freeze/archive/2026-04-10-freeze-demo-packet-history.md"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(
                "\n".join(
                    [
                        "# Freeze Demo Packet History",
                        "## 当前稳定证据",
                        "- 单元测试：`175 tests OK`",
                        "- demo smoke：`10 scenarios pass`",
                        "- 共享验证检查：`8 / 8 pass`",
                    ]
                ),
                encoding="utf-8",
            )

            snapshot = fetch_review_snapshot_from_repo_docs(
                cwd,
                {"default_plan": "P6-15 Preserve The Stronger Validation Baseline"},
            )

        self.assertEqual(
            "PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.",
            snapshot.latest_passing_qa_summary,
        )
        self.assertIn("Stronger shared validation baseline remains", snapshot.latest_success_run_notes)

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

    def test_replace_page_body_patches_supported_blocks_in_place_when_structure_matches(self):
        class FakeClient(NotionClient):
            def __init__(self):
                super().__init__("test-token")
                self.calls = []

            def list_block_children(self, block_id):
                return [
                    {
                        "id": "phase-block",
                        "type": "bulleted_list_item",
                        "archived": False,
                        "in_trash": False,
                        "bulleted_list_item": {"rich_text": [{"plain_text": "当前阶段：P6"}]},
                    },
                    {
                        "id": "plan-block",
                        "type": "bulleted_list_item",
                        "archived": False,
                        "in_trash": False,
                        "bulleted_list_item": {"rich_text": [{"plain_text": "当前已验证 Plan：P6-16"}]},
                    },
                ]

            def request(self, method, path, payload=None):
                self.calls.append((method, path, payload))
                return {}

        client = FakeClient()

        client.replace_page_body(
            "page-123",
            [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"text": {"content": "当前阶段：P7"}}]},
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"text": {"content": "当前已验证 Plan：P6-16"}}]},
                },
            ],
        )

        self.assertEqual(
            [
                (
                    "PATCH",
                    "/v1/blocks/phase-block",
                    {
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": "当前阶段：P7"}}],
                        }
                    },
                )
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
