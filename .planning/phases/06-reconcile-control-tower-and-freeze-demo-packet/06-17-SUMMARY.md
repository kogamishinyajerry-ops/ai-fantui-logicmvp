# P6-17 Summary - Lift The Stronger QA Baseline Back To The Homepage

- Extended compact-summary parsing so repo history text such as `10 scenarios pass` and `8 / 8 pass` can be normalized into the shared QA baseline format.
- Added repo-history QA baseline recovery that scans current and archived freeze/QA artifacts, then carries the strongest validation summary back into live snapshot rendering.
- Updated snapshot preference so a same-run snapshot with a stronger QA baseline now wins over a weaker maintenance-only summary.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
- `python3 tools/gsd_notion_sync.py sync-repo-docs --format json`
- `python3 tools/gsd_notion_sync.py prepare-opus-review --format json`
