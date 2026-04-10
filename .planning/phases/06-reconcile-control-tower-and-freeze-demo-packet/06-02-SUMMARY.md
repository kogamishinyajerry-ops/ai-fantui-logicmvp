# P6-02 Summary - Sync The Control-Tower Homepage Snapshot Automatically

## Outcome

`P6-02` moved the Notion cockpit homepage into a repo-managed live snapshot path, so the main dashboard no longer depends entirely on the frozen manual snapshot from an older phase.

## What Changed

- Added the dashboard page and freeze packet page to the control-plane config as first-class tracked pages.
- Extended `tools/gsd_notion_sync.py` with a managed dashboard-snapshot section that can be refreshed without rewriting the entire homepage body.
- Added tests to protect the homepage rendering path and the stronger control-plane validation contract.

## Verification

- The shared validation suite still passes against the current P5 baseline.
- The Notion homepage now shows a repo-managed top snapshot that supersedes the stale `P1 / 134 tests / Awaiting Opus` summary below it.

## Notes

- This is still P6 reconciliation work, not a new product-surface feature.
- The local `NOTION_API_KEY` integration can write the dashboard page directly, but full repo-side refreshes that query every control-plane database still depend on broader integration sharing.
