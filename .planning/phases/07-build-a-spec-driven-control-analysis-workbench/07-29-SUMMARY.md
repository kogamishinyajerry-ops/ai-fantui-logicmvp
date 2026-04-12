# P7-29 Summary - Harden Notion Control-Plane Development Rules

- `tools/gsd_notion_sync.py` now injects a shared “当前开发架构与执行规则” section into the dashboard snapshot, status page, repo coordination plan, dev handoff, and QA report, so the anti-drift contract is part of the synced control plane instead of living only in chat.
- The synced dashboard loop now spells out that a slice only closes after `gsd_notion_sync.py run` writes back live state, `prepare-opus-review` re-checks the gate/review need, and any writeback degradation is treated as a control-plane blocker rather than silently ignored.
- Control-plane tests now assert those guardrails are present, so future drift in the synced templates fails CI before it can mislead a new Codex session.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py tests/test_validate_notion_control_plane.py`
