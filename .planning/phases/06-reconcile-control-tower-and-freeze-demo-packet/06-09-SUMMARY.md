# P6-09 Summary - Make Repo Entrypoints Aware Of Archived Notion Active Pages

## Outcome

`P6-09` aligns the repo-side handoff surface with the real health of the Notion control plane: when the separate status / 09C / freeze pages behave like archived targets, repo docs now say so plainly and route the user through the dashboard plus GitHub instead of linking to dead pages.

## What Changed

- Added archived-page health checks to repo-doc sync.
- Updated coordination/freeze handoff renderers so they degrade to a dashboard-first note when those separate Notion active pages are unavailable.
- Kept GitHub repo and Actions links stable as the fallback evidence plane under the same degraded mode.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --format json`

## Notes

- This slice does not “fix” the archived Notion subpages themselves; it makes the repo-side operator surface honest about that constraint.
- The dashboard remains the reliable live entry while the local integration continues to see the separate status-style pages as archived.
