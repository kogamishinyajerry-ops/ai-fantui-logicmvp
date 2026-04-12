# P7-16 Summary - Show Latest-Vs-Replay Differences In The Browser Workbench

- Added a latest-vs-replay comparison strip that appears during historical replay and highlights verdict, scenario, fault mode, and archive differences against the newest stored result.
- Tightened the browser-side view-state handling so the workbench now distinguishes preparation, running, latest, and historical replay states before deciding what guidance to show.
- Kept the feature fully frontend-side and truth-preserving by deriving comparison data from the same stored history payloads already used for replay.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py tests/test_document_intake.py tests/test_scenario_playback.py tests/test_fault_diagnosis.py tests/test_knowledge_capture.py`
- `curl -s http://127.0.0.1:8010/workbench.html | rg -n "当前查看：等待第一次结果|回到最新结果|历史回看与最新结果差异|点一张卡即可把那次结果重新放回主看板"`
- `curl -s http://127.0.0.1:8010/workbench.js | rg -n "renderWorkbenchHistoryCompareBar|当前查看：历史回看|你正在回看|restoreLatestWorkbenchHistory"`
