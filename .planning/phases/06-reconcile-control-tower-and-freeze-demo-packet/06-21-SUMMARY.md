# P6-21 Summary - Surface Database-Degraded Evidence Mode Across The Control Plane

- Added explicit `evidence_mode` / `evidence_note` metadata to `ReviewSnapshot`, so shared-database reads, active-page fallback, dashboard-only fallback, repo-doc fallback, and local-timeout fallback are now distinct control-plane states instead of implicit behavior.
- Rendered the current evidence mode into dashboard, status, freeze packet, 09C current review facts, and repo-side coordination docs, so a shared-database 404 now shows up as an explicit control-plane fact instead of a hidden implementation detail.
- Added regression coverage for active-page fallback, dashboard fallback, current-review brief rendering, and repo coordination markdown rendering.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py tests/test_validate_notion_control_plane.py`
