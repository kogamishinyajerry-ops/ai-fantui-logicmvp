# P6-18 Summary - Refresh Active Sync Surfaces When Link Targets Move

- Updated `tools/gsd_notion_sync.py` so active-page equality checks now compare both rich-text labels and their linked URLs, which lets the sync replace stale `status` / `09C` / `freeze_packet` links after active pages rotate to new IDs.
- Brought the script's fallback active-page defaults onto the current live control-plane page IDs, reducing the chance that a partial config or recovery path points back at historical targets.
- Added a regression test for same-label/different-link drift and marked the repo-side Notion bootstrap guide as historical/reference-only so old `Round 92` / `129 tests OK` setup examples stop reading like live truth.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_validate_notion_control_plane.py`
- `python3 tools/gsd_notion_sync.py prepare-opus-review --format json`
