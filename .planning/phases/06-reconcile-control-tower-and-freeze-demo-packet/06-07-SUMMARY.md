# P6-07 Summary - Promote Active Snapshot Even When Database Writeback Fails

## Outcome

`P6-07` removes a real P6 control-plane drift trap: a successful docs-only or control-plane run no longer has to leave the dashboard/status/09C/freeze surfaces stuck on the previous plan just because the shared Notion database path raised a 404.

## What Changed

- Added a page-based fallback snapshot builder for successful runs, so the active Notion surfaces can still be promoted to the current plan/run summary even when the shared database writeback path fails.
- Refactored the active-page writer so both the normal review-brief flow and the new fallback path use the same rendering logic.
- Extended `prepare-opus-review` and `sync-repo-docs` to treat both `Could not find database` and `HTTP 404 /v1/databases/...` as page-fallback conditions.
- Added regression tests covering:
  - successful run degradation into partial writeback plus active-page promotion
  - `prepare-opus-review` page fallback under unshared-database 404s

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 -m py_compile tools/gsd_notion_sync.py`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- This slice hardens control-plane reliability rather than product behavior.
- The new fallback does not pretend the databases were written; it keeps the run visible on the user-facing active pages so the current truth can advance while the underlying integration scope is repaired later.
