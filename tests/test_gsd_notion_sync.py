import unittest

from tools.gsd_notion_sync import CommandResult, clip, summarize_results


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


if __name__ == "__main__":
    unittest.main()
