"""Shelved LLM test methods extracted from tests/test_demo.py.

Originally lines 870-1187 of tests/test_demo.py, class DemoIntentLayerTests.
Extracted during Phase A of the UI restructuring (2026-04-22) when LLM
functionality was removed from the active codebase.

These test methods target:
- demo_server._handle_chat_explain / _clear_chat_explain_cache
- chat.html / chat.js static assets (now in archive/shelved/llm-features/static/)
- well_harness.llm_client (now in archive/shelved/llm-features/src/)

To re-enable: restore the target modules/files to their original locations,
then paste these methods back into DemoIntentLayerTests in tests/test_demo.py.

Not runnable as-is (no class wrapper, no imports).
"""

# ============================================================================
# START OF EXTRACTED BLOCK (test_demo.py:870-1187)
# ============================================================================

    def test_chat_explain_parses_structured_minimax_json_and_includes_node_states(self):
        demo_server._clear_chat_explain_cache()
        captured_payload = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": (
                                        "```json\n"
                                        "{\"explanation\": \"L1 已激活，但 THR_LOCK 仍受 VDT90 阻塞。\", "
                                        "\"highlighted_nodes\": [\"L1\", \"THR_LOCK\"], "
                                        "\"suggestion_nodes\": [\"VDT90\"], "
                                        "\"confidence\": 0.95}\n"
                                        "```"
                                    )
                                }
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")

        def fake_urlopen(request, timeout=30):
            del timeout
            captured_payload["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse()

        from well_harness import llm_client as lc

        def _fixed_key(self):
            return "test-key"

        with mock.patch.object(lc.MiniMaxClient, "api_key", property(_fixed_key)):
            with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                response_payload, error_payload = demo_server._handle_chat_explain(
                    {
                        "question": "为什么 THR_LOCK 没释放？",
                        "system_id": "thrust-reverser",
                        "node_states": {"L1": "active", "THR_LOCK": "blocked"},
                        "lever_snapshot": {
                            "nodes": [
                                {"id": "L1", "state": "active"},
                                {"id": "THR_LOCK", "state": "blocked"},
                            ]
                        },
                    }
                )

        self.assertIsNone(error_payload)
        self.assertEqual(response_payload["explanation"], "L1 已激活，但 THR_LOCK 仍受 VDT90 阻塞。")
        self.assertEqual(response_payload["highlighted_nodes"], ["L1", "THR_LOCK"])
        self.assertEqual(response_payload["suggestion_nodes"], ["VDT90"])
        self.assertEqual(response_payload["confidence"], 0.95)

        minimax_payload = captured_payload["body"]
        self.assertEqual(minimax_payload["model"], "minimax-m2.7-highspeed")
        self.assertIn("当前 node_states（真值）", minimax_payload["messages"][0]["content"])
        self.assertIn("L1: active(已激活)", minimax_payload["messages"][0]["content"])
        self.assertIn("THR_LOCK: blocked(阻塞)", minimax_payload["messages"][0]["content"])

    def test_chat_explain_cache_reuses_identical_truth_context_with_transparent_source(self):
        demo_server._clear_chat_explain_cache()

        class FakeClient:
            def __init__(self):
                self.calls = 0

            def chat(self, messages, **kwargs):
                del messages, kwargs
                self.calls += 1
                return json.dumps(
                    {
                        "explanation": "THR_LOCK 没释放，因为 VDT90 还未满足。",
                        "highlighted_nodes": ["THR_LOCK", "VDT90"],
                        "suggestion_nodes": ["logic4"],
                        "confidence": 0.91,
                    },
                    ensure_ascii=False,
                )

        fake_client = FakeClient()
        payload = {
            "question": "为什么 THR_LOCK 没释放？",
            "system_id": "thrust-reverser",
            "node_states": {"THR_LOCK": "blocked", "VDT90": "inactive"},
            "lever_snapshot": {
                "nodes": [
                    {"id": "THR_LOCK", "state": "blocked"},
                    {"id": "VDT90", "state": "inactive"},
                ],
                "logic": {"logic4": {"active": False, "failed_conditions": ["VDT90"]}},
                "outputs": {"throttle_electronic_lock_release_cmd": False, "deploy_90_percent_vdt": False},
            },
        }

        with mock.patch.object(demo_server, "get_llm_client", return_value=fake_client):
            with mock.patch.dict(
                os.environ,
                {"LLM_BACKEND": "ollama", "OLLAMA_MODEL": "qwen2.5:7b-instruct"},
                clear=False,
            ):
                live_payload, live_error = demo_server._handle_chat_explain(payload)
                cached_payload, cached_error = demo_server._handle_chat_explain(payload)

        self.assertIsNone(live_error)
        self.assertIsNone(cached_error)
        self.assertEqual(fake_client.calls, 1)
        self.assertEqual(live_payload["response_source"], "live_llm")
        self.assertEqual(cached_payload["response_source"], "cached_llm")
        self.assertEqual(live_payload["cache_key"], cached_payload["cache_key"])
        self.assertEqual(cached_payload["llm_backend"], "ollama")
        self.assertEqual(cached_payload["llm_model"], "qwen2.5:7b-instruct")
        self.assertEqual(cached_payload["highlighted_nodes"], ["THR_LOCK", "VDT90"])

    def test_chat_explain_prewarm_reports_hits_and_misses(self):
        demo_server._clear_chat_explain_cache()

        class FakeClient:
            def __init__(self):
                self.calls = 0

            def chat(self, messages, **kwargs):
                self.calls += 1
                return json.dumps(
                    {
                        "explanation": f"response-{self.calls}",
                        "highlighted_nodes": ["L1"],
                        "suggestion_nodes": ["logic1"],
                        "confidence": 0.88,
                    },
                    ensure_ascii=False,
                )

        fake_client = FakeClient()
        repeated_payload = {
            "question": "L1门为什么active",
            "system_id": "thrust-reverser",
            "node_states": {"L1": "active"},
            "lever_snapshot": {
                "nodes": [{"id": "L1", "state": "active"}],
                "logic": {"logic1": {"active": True, "failed_conditions": []}},
                "outputs": {"throttle_electronic_lock_release_cmd": False, "deploy_90_percent_vdt": False},
            },
        }
        distinct_payload = {
            "question": "L3门为什么blocked",
            "system_id": "thrust-reverser",
            "node_states": {"L3": "blocked"},
            "lever_snapshot": {
                "nodes": [{"id": "L3", "state": "blocked"}],
                "logic": {"logic3": {"active": False, "failed_conditions": ["TRA"]}},
                "outputs": {"throttle_electronic_lock_release_cmd": False, "deploy_90_percent_vdt": False},
            },
        }

        with mock.patch.object(demo_server, "get_llm_client", return_value=fake_client):
            with mock.patch.dict(
                os.environ,
                {"LLM_BACKEND": "ollama", "OLLAMA_MODEL": "qwen2.5:7b-instruct"},
                clear=False,
            ):
                response_payload, error_payload = demo_server._handle_chat_explain_prewarm(
                    {"requests": [repeated_payload, repeated_payload, distinct_payload]}
                )

        self.assertIsNone(error_payload)
        self.assertEqual(fake_client.calls, 2)
        self.assertEqual(response_payload["requested_count"], 3)
        self.assertEqual(response_payload["warmed_count"], 3)
        self.assertEqual(response_payload["cache_hits"], 1)
        self.assertEqual(response_payload["cache_misses"], 2)
        self.assertEqual(response_payload["errors"], [])
        self.assertEqual(
            [item["response_source"] for item in response_payload["results"]],
            ["live_llm", "cached_llm", "live_llm"],
        )

    def test_chat_explain_without_truth_context_stays_live_and_out_of_cache(self):
        demo_server._clear_chat_explain_cache()

        class FakeClient:
            def __init__(self):
                self.calls = 0

            def chat(self, messages, **kwargs):
                del messages, kwargs
                self.calls += 1
                return json.dumps(
                    {
                        "explanation": f"live-{self.calls}",
                        "highlighted_nodes": [],
                        "suggestion_nodes": [],
                        "confidence": 0.5,
                    },
                    ensure_ascii=False,
                )

        fake_client = FakeClient()
        payload = {
            "question": "L3门为什么active",
            "system_id": "thrust-reverser",
        }

        with mock.patch.object(demo_server, "get_llm_client", return_value=fake_client):
            with mock.patch.dict(
                os.environ,
                {"LLM_BACKEND": "ollama", "OLLAMA_MODEL": "qwen2.5:7b-instruct"},
                clear=False,
            ):
                first_payload, first_error = demo_server._handle_chat_explain(payload)
                second_payload, second_error = demo_server._handle_chat_explain(payload)

        self.assertIsNone(first_error)
        self.assertIsNone(second_error)
        self.assertEqual(fake_client.calls, 2)
        self.assertEqual(first_payload["response_source"], "live_llm")
        self.assertEqual(second_payload["response_source"], "live_llm")
        self.assertEqual(first_payload["cache_key"], "")
        self.assertEqual(second_payload["cache_key"], "")
        self.assertEqual(first_payload["cached_at"], "")
        self.assertEqual(second_payload["cached_at"], "")

    def test_chat_static_assets_include_truth_first_ai_overlay_flow(self):
        script = (DEMO_UI_STATIC_DIR / "chat.js").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "chat.css").read_text(encoding="utf-8")

        for fragment in (
            "function extractNodeStates(snapshotData)",
            "function applySystemSnapshotToCanvas(snapshotData, inputSnapshot)",  # P43-02.5 Step C · signature extended (optional inputSnapshot arg · backward-compat at runtime)
            "function applyAiHighlights(highlightedNodes, suggestionNodes)",
            "function clearAiHighlights()",
            "requestJson('/api/system-snapshot?system_id=' + encodeURIComponent(qSystemId))",
            "node_states: nodeStates",
            "data-highlighted",
            "highlighted_nodes",
            "suggestion_nodes",
            "lastTruthPayloadBySystem",
            "function formatExplainResponseFootnote(aiData)",
            "response_source",
            "chat-message-footnote",
        ):
            self.assertIn(fragment, script)
        self.assertIn(".chat-message-footnote", css)

        for fragment in (
            ".chain-node-svg.ai-discussed",
            ".logic-gate-svg.ai-discussed",
            ".chain-node-svg.ai-suggested",
            ".logic-gate-svg.ai-suggested",
            ".chat-message[data-highlighted] .chat-message-content",
            "@keyframes aiDiscussedPulse",
            "@keyframes aiSuggestedPulse",
        ):
            self.assertIn(fragment, css)

    def test_chat_static_assets_include_persistent_explain_status_panel(self):
        html = (DEMO_UI_STATIC_DIR / "chat.html").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "chat.js").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "chat.css").read_text(encoding="utf-8")

        for fragment in (
            'id="explain-status-panel"',
            'id="explain-status-source"',
            'id="explain-status-backend"',
            'id="explain-status-cache"',
            'id="explain-status-updated"',
            'Explain 状态',
        ):
            self.assertIn(fragment, html)

        for fragment in (
            "var lastExplainStatusBySystem = {};",
            "function renderExplainStatusPanel()",
            "function syncExplainStatus(systemId, aiData)",
            "function markExplainStatusFailure(systemId, err)",
            "syncExplainStatus(qSystemId, aiData);",
            "markExplainStatusFailure(qSystemId, err);",
        ):
            self.assertIn(fragment, script)

        for fragment in (
            ".explain-status-panel",
            ".explain-status-pill.is-live",
            ".explain-status-pill.is-cached",
            ".explain-status-note",
        ):
            self.assertIn(fragment, css)

    def test_chat_static_assets_include_icon_links_and_live_global_controls(self):
        html = (DEMO_UI_STATIC_DIR / "chat.html").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "chat.js").read_text(encoding="utf-8")

        for fragment in (
            'rel="icon" href="/favicon.svg"',
            'rel="apple-touch-icon" href="/apple-touch-icon.svg"',
        ):
            self.assertIn(fragment, html)

        for fragment in (
            "function renderRequestFailure(err)",
            "function applyCanvasGlobalControls()",
            "function bindCanvasGlobalControls()",
            "fbSelect.addEventListener('change', function() {",
            "n1kSlider.addEventListener('change', function() {",
            "return currentSystem === 'thrust-reverser';",
        ):
            self.assertIn(fragment, script)


# ============================================================================
# END OF EXTRACTED BLOCK
