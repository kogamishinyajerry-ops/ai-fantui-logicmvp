"""Input-validation regression tests for _handle_chat_operate (security Round 3).

Mirrors tests/test_chat_reason_input_validation.py one-to-one. Round 3 closed
BACKLOG entry C-sibling (HIGH, SECURITY-PENDING) by routing both /api/chat/reason
and /api/chat/operate through the shared module-level helper
``_validate_chat_payload``. These tests lock the operate-side surface to the
same 6 error codes / 6 rejection rules.

The bottom of the file also contains an EQUIVALENCE test that feeds the same
malformed payload to both handlers and asserts they return identical error
codes — preventing future drift between the two endpoints.
"""
import unittest

from well_harness.demo_server import _handle_chat_operate, _handle_chat_reason


INPUT_VALIDATION_ERRORS = {
    "invalid_question_type",
    "missing_question",
    "question_too_long",
    "invalid_system_id",
    "invalid_current_snapshot",
    "snapshot_nodes_too_large",
}


class ChatOperateInputValidationTests(unittest.TestCase):

    # ── question field ────────────────────────────────────────────────────
    def test_rejects_non_string_question_list(self):
        result, error = _handle_chat_operate({"question": ["injected", "list"]})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_non_string_question_dict(self):
        result, error = _handle_chat_operate({"question": {"$prompt": "x"}})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_non_string_question_int(self):
        result, error = _handle_chat_operate({"question": 42})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_question_type")

    def test_rejects_empty_question(self):
        result, error = _handle_chat_operate({"question": "   "})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "missing_question")

    def test_rejects_oversize_question_dos_vector(self):
        # 8001 chars — one over MAX_QUESTION_CHARS. Must not reach LLM API.
        result, error = _handle_chat_operate({"question": "A" * 8001})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "question_too_long")

    def test_accepts_question_at_exact_cap(self):
        # 8000 chars is the cap; must NOT be rejected as too long.
        result, error = _handle_chat_operate({"question": "A" * 8000})
        if error is not None:
            self.assertNotIn(error.get("error"), {"question_too_long", "invalid_question_type"})

    # ── system_id whitelist ───────────────────────────────────────────────
    def test_rejects_unknown_system_id_path_traversal(self):
        # Path-traversal style payload — exact attack vector mirrored from Round 2.
        result, error = _handle_chat_operate({
            "question": "把VDT调到90%",
            "system_id": "../../etc/passwd",
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_system_id")

    def test_rejects_non_string_system_id(self):
        result, error = _handle_chat_operate({"question": "hi", "system_id": 999})
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_system_id")

    # ── current_snapshot shape ────────────────────────────────────────────
    def test_rejects_non_dict_current_snapshot_list(self):
        result, error = _handle_chat_operate({
            "question": "hi",
            "current_snapshot": [1, 2, 3],
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_current_snapshot")

    def test_rejects_non_dict_current_snapshot_string(self):
        result, error = _handle_chat_operate({
            "question": "hi",
            "current_snapshot": "not-a-dict",
        })
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "invalid_current_snapshot")

    def test_rejects_oversize_snapshot_nodes_dos_vector(self):
        # 201 nodes — one over MAX_SNAPSHOT_NODES. Blocks JSON-bomb-style
        # unbounded iteration that would otherwise build a huge LLM prompt
        # and propagate to operator-facing "suggest_parameter_override" output.
        payload = {
            "question": "hi",
            "current_snapshot": {
                "nodes": [{"id": f"n{i}", "state": "active"} for i in range(201)],
            },
        }
        result, error = _handle_chat_operate(payload)
        self.assertIsNone(result)
        self.assertEqual(error.get("error"), "snapshot_nodes_too_large")

    # ── positive-path: valid payload reaches operate-specific layer ───────
    def test_valid_minimal_payload_passes_input_validation(self):
        # A valid payload must not be rejected by the shared input-validation
        # layer. In CI without a MiniMax key it falls through to
        # `minimax_api_key_missing` — that is acceptable proof that
        # _validate_chat_payload did not fire AND the operate-specific
        # downstream chain (allowed_override_fields / feedback_mode / auto_apply)
        # remains reachable.
        result, error = _handle_chat_operate({
            "question": "把VDT调节到90%",
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


class ChatReasonOperateEquivalenceTests(unittest.TestCase):
    """Lock the helper so the two endpoints can never silently diverge.

    For each malformed payload, _handle_chat_reason and _handle_chat_operate
    must return EXACTLY the same error code. If a future PR widens validation
    on one side without the other, this test breaks immediately.
    """

    EQUIVALENCE_PAYLOADS = [
        # (label, payload, expected_error_code)
        ("question is a list",                {"question": ["x"]},                                              "invalid_question_type"),
        ("question is an int",                {"question": 7},                                                  "invalid_question_type"),
        ("question is whitespace",            {"question": "   "},                                              "missing_question"),
        ("question over 8000 chars",          {"question": "A" * 8001},                                         "question_too_long"),
        ("system_id is path traversal",       {"question": "hi", "system_id": "../../etc/passwd"},              "invalid_system_id"),
        ("current_snapshot is a list",        {"question": "hi", "current_snapshot": [1, 2, 3]},                "invalid_current_snapshot"),
        ("snapshot.nodes too large",          {"question": "hi", "current_snapshot": {"nodes": [{"id": f"n{i}"} for i in range(201)]}}, "snapshot_nodes_too_large"),
    ]

    def test_both_endpoints_reject_with_identical_error_codes(self):
        for label, payload, expected in self.EQUIVALENCE_PAYLOADS:
            with self.subTest(case=label):
                _, reason_error = _handle_chat_reason(payload)
                _, operate_error = _handle_chat_operate(payload)

                self.assertIsNotNone(reason_error, f"reason did not reject: {label}")
                self.assertIsNotNone(operate_error, f"operate did not reject: {label}")

                self.assertEqual(
                    reason_error.get("error"),
                    expected,
                    msg=f"reason wrong code for {label!r}: {reason_error!r}",
                )
                self.assertEqual(
                    operate_error.get("error"),
                    expected,
                    msg=f"operate wrong code for {label!r}: {operate_error!r}",
                )
                # Strongest invariant: both endpoints' error codes are identical.
                self.assertEqual(
                    reason_error.get("error"),
                    operate_error.get("error"),
                    msg=f"endpoint divergence for {label!r}: "
                        f"reason={reason_error!r} operate={operate_error!r}",
                )


if __name__ == "__main__":
    unittest.main()
