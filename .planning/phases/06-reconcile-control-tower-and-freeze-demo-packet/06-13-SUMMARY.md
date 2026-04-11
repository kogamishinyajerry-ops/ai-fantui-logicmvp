# P6-13 Summary - Make Default Plan Follow The Active Phase

- Added active-phase default-plan resolution from `.planning/ROADMAP.md` plus the newest local plan file under that phase, so sync commands no longer rely on a stale static `default_plan`.
- Updated `gsd_notion_sync.py` entrypoints to persist the resolved plan back into `notion_control_plane.json` before rendering dashboard or repo-doc snapshots.
- Added focused tests covering active-phase resolution and fallback behavior when no active plan is available.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py prepare-opus-review --format json`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --format json`
