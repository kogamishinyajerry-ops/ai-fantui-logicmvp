# P6-05 Summary - Sync Repo-Side Coordination Docs From The Live Snapshot

## Outcome

`P6-05` brings the repo-side coordination packet onto the same live snapshot contract as the active Notion control-plane pages, so current handoff docs no longer start by telling the reader `129 tests OK` and `manual browser QA` as if that were still the live baseline.

## What Changed

- Extended `tools/gsd_notion_sync.py` with a repo-doc sync path that writes managed markdown sections into the active coordination docs and freeze packet.
- Added a page-derived fallback snapshot path so repo-doc sync can still work when the local Notion token can read the active pages but not the shared plan/run databases.
- Regenerated:
  - `docs/coordination/plan.md`
  - `docs/coordination/dev_handoff.md`
  - `docs/coordination/qa_report.md`
  - `docs/freeze/2026-04-10-freeze-demo-packet.md`

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py tests/test_validate_notion_control_plane.py`
- `python3 -m py_compile tools/gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --cwd . --format json`

## Notes

- Older Round-based notes are still present below the managed sections as historical context; the new auto-synced blocks are now the authoritative repo-side baseline.
- The local integration still cannot query some shared Notion databases directly, so the fallback-to-pages path remains part of the intended P6 behavior rather than an incidental workaround.
