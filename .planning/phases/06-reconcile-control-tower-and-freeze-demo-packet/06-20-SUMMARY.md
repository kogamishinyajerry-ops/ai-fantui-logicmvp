# P6-20 Summary - Keep Active Sync Page URLs Stable Across Snapshot Refreshes

- Changed `replace_active_sync_page()` so writable active sync pages are updated in place instead of being replaced with a new child page every time the snapshot content changes.
- Preserved the self-healing path for archived or missing active pages, so the dashboard can still mint a fresh replacement when Notion has actually invalidated the old page.
- Added regression coverage for both the in-place update case and the archived-page replacement case.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py tests/test_validate_notion_control_plane.py`
