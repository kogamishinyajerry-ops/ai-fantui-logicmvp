# P6-11 Summary - Let Repo Docs Follow The Fresher Dashboard Snapshot

## Outcome

`P6-11` removes the last obvious repo-side lag inside P6: when the dashboard already reflects a fresher GitHub-backed snapshot than the locally visible Notion databases, repo-side handoff and freeze docs now follow the dashboard instead of getting stuck on stale database state.

## What Changed

- Added snapshot freshness comparison between database-backed and page-backed control-plane reads.
- Taught `sync-repo-docs` to prefer the fresher dashboard/page snapshot when it clearly outruns the database snapshot.
- Re-synced repo-side coordination and freeze docs so they can advance from the stale `P6-07` baseline to the current P6 baseline.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --format json`

## Notes

- This slice keeps database-backed snapshots as the default path; it only overrides them when the dashboard/page surface is demonstrably fresher.
