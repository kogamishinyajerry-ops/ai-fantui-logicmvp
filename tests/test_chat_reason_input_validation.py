"""Input-validation regression tests for _handle_chat_reason (security Round 2).

Covers:
  * question type / length caps
  * system_id whitelist
  * current_snapshot shape enforcement
  * current_snapshot.nodes length cap

These tests exercise validation ONLY — no MiniMax API key is required because
the validation block now runs before the api_key check. Valid payloads fall
through to the api_key gate and return `minimax_api_key_missing` in CI, which
is accepted here as proof that validation did not wrongly reject the input.
"""
import unittest

from well_harness.demo_server import _handle_chat_reason


INPUT_VALIDATION_ERRORS = {
    "invalid_question_type",
    "missing_question",
    "question_too_long",
    "invalid_system_id",
    "invalid_current_snapshot",
    "snapshot_nodes_too_large",
}


class ChatReasonInputValidationTests(unittest.TestCase):

    # ── question field ────────────────────────────────────────────────────
    def test_rejects_non_string_question_list(self):
        result, error = _handle_chat_reason({"question": ["injected", "list"]})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_non_string_question_dict(self):
        result, error = _handle_chat_reason({"question": {"$prompt": "x"}})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_non_string_question_int(self):
        result, error = _handle_chat_reason({"question": 42})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_empty_question(self):
        result, error = _handle_chat_reason({"question": "   "})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "missing_question")

    def test_rejects_oversize_question_dos_vector(self):
        # 8001 chars — one over MAX_QUESTION_CHARS. Must not reach LLM API.
        result, error = _handle_chat_reason({"question": "A" * 8001})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "question_too_long")

    def test_accepts_question_at_exact_cap(self):
        # 8000 chars is the cap; must NOT be rejected as too long.
        result, error = _handle_chat_reason({"question": "A" * 8000})
        if error is not None:
            self.assertNotIn(error.get("error"), {"question_too_long", "invalid_question_type"})

    # ── system_id whitelist ───────────────────────────────────────────────
    def test_rejects_unknown_system_id(self):
        result, error = _handle_chat_reason({
            "question": "hi",
            "system_id": "../../etc/passwd",
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_system_id")

    def test_rejects_non_string_system_id(self):
        result, error = _handle_chat_reason({"question": "hi", "system_id": 999})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_system_id")

    # ── current_snapshot shape ────────────────────────────────────────────
    def test_rejects_non_dict_current_snapshot_list(self):
        result, error = _handle_chat_reason({
            "question": "hi",
            "current_snapshot": [1, 2, 3],
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_current_snapshot")

    def test_rejects_non_dict_current_snapshot_string(self):
        result, error = _handle_chat_reason({
            "question": "hi",
            "current_snapshot": "not-a-dict",
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_current_snapshot")

    def test_rejects_oversize_snapshot_nodes_dos_vector(self):
        # 201 nodes — one over MAX_SNAPSHOT_NODES. Blocks JSON-bomb-style
        # unbounded iteration that would otherwise build a huge LLM prompt.
        payload = {
            "question": "hi",
            "current_snapshot": {
                "nodes": [{"id": f"n{i}", "state": "active"} for i in range(201)],
            },
        }
        result, error = _handle_chat_reason(payload)
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "snapshot_nodes_too_large")

    # ── positive-path: validation does NOT reject valid shapes ───────────
    def test_valid_minimal_payload_passes_input_validation(self):
        # A valid payload must not be rejected by the input-validation layer.
        # In CI without a MiniMax key, it falls through to `minimax_api_key_missing`
        # — that is acceptable proof the validation layer did not fire.
        result, error = _handle_chat_reason({
            "question": "logic1 为什么阻塞？",
            "system_id": "thrust-reverser",
            "current_snapshot": {
                "nodes": [{"id": "logic1", "state": "blocked"}],
                "logic": {"logic1": {"active": False, "failed_conditions": ["tra_deg"]}},
            },
        })
        if error is not None:
            self.assertNotIn(
                error.get("error"),
                INPUT_VALIDATION_ERRORS,
                msg=f"valid payload was wrongly blocked by input validation: {error!r}",
            )


if __name__ == "__main__":
    unittest.main()
