# P6-12 Summary - De-duplicate Dashboard Active Surface Links

- Added dashboard child-page pruning so stale `01 当前状态（自动同步）` / `09C 当前 Opus 4.6 审查简报` / `10 Freeze Demo Packet` blocks are removed once they are no longer the configured live active surfaces.
- Updated page-text comparison to ignore preserved `child_page` / `child_database` blocks, making dashboard sync idempotent again even when those embedded surfaces remain.
- Added focused tests covering stale active-surface pruning and preserved-child-page-safe equality checks.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_gsd_notion_sync.py`
