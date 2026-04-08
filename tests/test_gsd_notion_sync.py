import unittest

from tools.gsd_notion_sync import (
    CommandResult,
    ReviewSnapshot,
    build_current_review_brief,
    clip,
    summarize_results,
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

        self.assertEqual("失败阻塞分流审查", brief.intervention_kind)
        self.assertIn("当前仍存在未解决的 open gap", brief.why_now)
        self.assertIn("最小修复路径", brief.copy_prompt)


if __name__ == "__main__":
    unittest.main()
