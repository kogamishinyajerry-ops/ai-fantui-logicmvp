# P6-10 Summary - Make Dashboard-Only Degraded Mode Explicit

## Outcome

`P6-10` makes the control-plane health model honest end-to-end: the validator now distinguishes between a real control-plane failure and the known dashboard-only degraded mode, and the dashboard snapshot itself stops pretending the archived status-style subpages are still live entrypoints.

## What Changed

- Added degraded-mode reporting to `validate_notion_control_plane.py` for archived `status / 09C / freeze` pages while keeping the dashboard as the canonical live surface.
- Kept hard failures for genuinely broken states such as an archived dashboard or required archived databases.
- Updated dashboard snapshot rendering to announce dashboard-only degraded mode and suppress dead Notion subpage links.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_validate_notion_control_plane.py tests/test_gsd_notion_sync.py`
- `python3 tools/validate_notion_control_plane.py --format json`
- `python3 tools/gsd_notion_sync.py prepare-opus-review --format json`

## Notes

- This slice does not restore direct write access to the archived subpages themselves; it makes the live dashboard and validation surfaces truthful about the current limitation.
