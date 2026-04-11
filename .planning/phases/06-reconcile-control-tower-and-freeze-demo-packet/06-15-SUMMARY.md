# P6-15 Summary - Preserve The Stronger Validation Baseline

- Extended compact success-summary parsing so repo-side recovery can read both raw validation logs and the human-readable QA summaries already written into freeze/handoff docs.
- Added success-evidence selection that preserves the prior richer shared validation baseline when the current run is a narrower control-plane maintenance slice.
- Added focused tests for compact-summary parsing, preservation heuristics, and local fallback snapshot behavior.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `NOTION_WRITEBACK_TIMEOUT_S=12 python3 tools/gsd_notion_sync.py run --plan-id "P6-15 Preserve The Stronger Validation Baseline" --title "P6-15 validation baseline preservation" --command "PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py" --format json`
