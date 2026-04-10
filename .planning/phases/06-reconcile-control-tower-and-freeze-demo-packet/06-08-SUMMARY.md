# P6-08 Summary - Clean Duplicate Active-Page Bodies And Bloated Run Summaries

## Outcome

`P6-08` removes the last major readability drift in the active control-plane surfaces: successful validation evidence is now summarized in short human-readable lines, repo-side handoff docs stay slim, and the Notion sync loop no longer dies just because one of the active status-style pages has drifted into an archived block state.

## What Changed

- Replaced raw success-digest reuse with compact summary extraction for successful runs, so run / QA / freeze / handoff snapshots now prefer lines like test count, smoke coverage, and shared-check pass count.
- Switched dashboard and freeze-packet page refreshes to full-body rewrites, removing duplicated old snapshot prose from the active user-facing surfaces.
- Added repo-doc fallback parsing so the sync loop can recover a current snapshot even when shared Notion databases and the old active pages are both unavailable.
- Hardened `prepare-opus-review` and run fallback paths so missing/archived active-page targets degrade into dashboard-first refresh behavior instead of aborting the whole control-plane sync.
- Added active-page replacement attempts plus archived-page write detection, so the loop can keep moving even when the integration only has a partially usable Notion page surface.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py prepare-opus-review --format json`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- The dashboard is currently the most reliable live Notion surface under the local integration; separate status / 09C / freeze page targets can still behave like archived blocks even after replacement attempts.
- That residual Notion behavior no longer blocks autonomous development, because the repo-side docs and dashboard snapshot remain refreshable from the same GitHub-backed truth.
