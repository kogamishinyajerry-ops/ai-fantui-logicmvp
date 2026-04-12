# P7-18 Summary - Add A Visual Second-System Onboarding Readiness Board To The Browser Workbench

- Added a visual second-system onboarding readiness board to the browser workbench so users can immediately judge whether a new control-logic packet is complete enough to enter spec build.
- Reused the existing `intake_assessment` and `clarification_brief` payloads to surface source-document coverage, component/logic/scenario/fault counts, clarification progress, unlocks, and current gaps without adding a new backend contract.
- Kept the feature aligned with the existing visual acceptance direction by making second-system readiness readable as a board instead of forcing users to infer it from raw JSON or scattered cards.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py tests/test_document_intake.py tests/test_scenario_playback.py tests/test_fault_diagnosis.py tests/test_knowledge_capture.py`
- `curl -s http://127.0.0.1:8010/workbench.html | rg -n "第二套系统接入准备度|workbench-onboarding-badge|workbench-onboarding-docs|workbench-onboarding-unlocks"`
- `curl -s http://127.0.0.1:8010/workbench.js | rg -n "renderOnboardingReadinessFromPayload|可接第二套系统|workbench-onboarding"`
