# P6-06 Summary - Move Historical Repo Handoff Prose Out Of Active Docs

## Outcome

`P6-06` finishes the repo-side packet cleanup started in `P6-05`: the active coordination docs and repo freeze packet now lead with the live auto-synced snapshot and only a short current-use note, while older Round prose has been moved into dedicated archive files.

## What Changed

- Created dedicated archive files for the previous long-form repo handoff content:
  - `docs/coordination/archive/plan-history.md`
  - `docs/coordination/archive/dev-handoff-history.md`
  - `docs/coordination/archive/qa-report-history.md`
  - `docs/freeze/archive/2026-04-10-freeze-demo-packet-history.md`
- Slimmed the active repo surfaces so they now contain:
  - the managed current snapshot generated from the live control-plane state
  - a short explanation of what the active file is for
  - a pointer to the matching archive file
- Refreshed the repo-doc sync after the split so the active docs still advertise the current P6 baseline instead of freezing an outdated inline body.

## Verification

- `python3 tools/gsd_notion_sync.py sync-repo-docs --cwd . --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- This slice intentionally changes repo-side information architecture, not product behavior.
- The archive files preserve the older Round narrative for audit and retrospective use, but the active docs now make it much harder to mistake that history for the current baseline.
