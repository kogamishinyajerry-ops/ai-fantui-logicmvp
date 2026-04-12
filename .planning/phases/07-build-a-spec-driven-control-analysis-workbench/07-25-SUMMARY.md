# P7-25 Summary - Protect Browser Packet Drafts Before Overwrite

- Added a packet draft status bar plus a manual “保存当前 Packet 草稿” action, so browser-side JSON edits can be snapshotted into packet history before any rerun.
- Sample switches, packet restores, clarification writebacks, schema autofix writebacks, and local JSON imports now auto-save valid unsaved packet drafts before they overwrite the current editor payload.
- The draft workflow stays honest: invalid JSON cannot be saved into history, and the save action stays disabled when the editor is already synced to the selected saved revision.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_demo.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py`
