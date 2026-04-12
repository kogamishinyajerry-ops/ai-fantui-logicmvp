# P7-14 Summary - Make Recent Acceptance Results Reopenable In The Browser Workbench

- Turned recent acceptance history cards into clickable replay entries, so users can restore an earlier pass, block, or failure result back onto the main board without rerunning it.
- Reused the existing bundle and failure renderers for history replay, which keeps the detailed cards, archive summary, raw JSON drawer, and top verdict board aligned with the same result payload.
- Added selected-state styling and clearer card copy so the history strip reads like a visual “回看入口” instead of a passive audit log.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py tests/test_document_intake.py tests/test_scenario_playback.py tests/test_fault_diagnosis.py tests/test_knowledge_capture.py`
- `curl -s http://127.0.0.1:8010/workbench.html | rg -n "最近验收结果|点一张卡即可把那次结果重新放回主看板"`
- `curl -s http://127.0.0.1:8010/workbench.js | rg -n "restoreWorkbenchHistoryEntry|点此回看这次结果|当前来源：最近验收结果回看"`
