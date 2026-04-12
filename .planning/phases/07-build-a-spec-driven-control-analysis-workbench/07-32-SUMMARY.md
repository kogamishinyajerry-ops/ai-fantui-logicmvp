# P7-32 Summary - Archive Browser Workspace Handoff Context

- The browser workbench now sends `workspace_handoff` metadata with bundle requests, and backend archive generation can persist that context as `workspace_handoff.json` inside the archive package.
- Archive README files now include a browser handoff section when that metadata is present, so saved bundle artifacts preserve the same packet/result/archive/note context the UI showed at archive time.
- The browser archive file list and backend/demo tests now cover the new handoff artifact, keeping the handoff chain visible from UI to saved archive.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py`
