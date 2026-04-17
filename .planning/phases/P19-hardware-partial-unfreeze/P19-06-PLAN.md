---
phase: P19
plan: P19-06
type: execute
wave: 1
depends_on: [P19-05]
files_created: []
files_modified:
  - src/well_harness/demo_server.py
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure data transformation"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "New POST /api/diagnosis/run endpoint accepts outcome parameter"
    - "Endpoint returns serializable JSON report from diagnose_and_report()"
    - "Input validated: outcome must be one of VALID_OUTCOMES"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/demo_server.py
      provides: "POST /api/diagnosis/run route — runs reverse diagnosis and returns report JSON"
      min_lines: 40
  key_constraints:
    - "Use _validate_chat_payload style input validation"
    - "Hardware YAML path from config, not hardcoded"
    - "Engine instance created fresh per request (stateless)"
    - "Error cases return 400 with error message"
exit_criteria:
  - "python3 -c 'import requests; r=requests.post(\"http://127.0.0.1:8000/api/diagnosis/run\", json={\"outcome\":\"logic1_active\"}); print(r.status_code, r.json()[\"total_combos_found\"])' → 200 and combos count"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.6 — Reverse Diagnosis API Endpoint

### Context

P19.3 created `ReverseDiagnosisEngine` (pure Python, no Flask route).
P19.5 added `diagnose_and_report()` returning a serializable dict.
P19.6 exposes this to the browser via a new `/api/diagnosis/run` POST endpoint.

### Architecture

```
Browser POST /api/diagnosis/run
  { "outcome": "logic1_active", "max_results": 100 }
                    ↓
           demo_server.py route
                    ↓
        ReverseDiagnosisEngine(hardware_yaml)
                    ↓
        engine.diagnose_and_report(outcome)
                    ↓
         { outcome, total_combos_found,
           grid_resolution, timestamp, results[] }
```

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- Existing API contracts (all routes unchanged)
- `reverse_diagnosis.py` — unchanged, just imported

### Implementation

#### `src/well_harness/demo_server.py`

Add route constant after the other paths (~line 95):

```python
DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
```

Register route in `do_GET` / `do_POST` (~line 206-210):

```python
elif parsed.path == DIAGNOSIS_RUN_PATH:
    self._handle_diagnosis_run()
```

Add handler method:

```python
def _handle_diagnosis_run(self) -> None:
    """Run reverse diagnosis and return a JSON report."""
    import json
    from well_harness.reverse_diagnosis import (
        VALID_OUTCOMES,
        ReverseDiagnosisEngine,
    )

    # Read body
    content_length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(content_length).decode("utf-8")

    # Parse JSON
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        self._send_json_response(400, {"error": "Invalid JSON"})
        return

    # Validate outcome
    outcome = payload.get("outcome", "").strip()
    if outcome not in VALID_OUTCOMES:
        self._send_json_response(400, {
            "error": f"Invalid outcome: {outcome!r}. "
                     f"Valid: {sorted(VALID_OUTCOMES)}"
        })
        return

    max_results = min(int(payload.get("max_results", 1000)), 1000)
    max_results = max(max_results, 0)

    # Run diagnosis — hardware YAML path from the server's config
    yaml_path = self._hardware_yaml_path()
    try:
        engine = ReverseDiagnosisEngine(yaml_path)
        report = engine.diagnose_and_report(outcome, max_results=max_results)
        self._send_json_response(200, report)
    except Exception as exc:
        self._send_json_response(500, {"error": str(exc)})


def _hardware_yaml_path(self) -> str:
    """Return the path to the thrust-reverser hardware YAML config."""
    # Resolve relative to the repo root (parent of src/)
    import pathlib, well_harness
    pkg_root = pathlib.Path(well_harness.__file__).parent
    repo_root = pkg_root.parent.parent
    return str(repo_root / "config" / "hardware" / "thrust_reverser_hardware_v1.yaml")
```

### Tasks

#### Task 1: Add `DIAGNOSIS_RUN_PATH` constant

Add `DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"` near `CHAT_REASON_PATH` (~line 95).

#### Task 2: Register route in `do_POST`

In `do_POST`, add the route handler after `CHAT_REASON_PATH` registration.

#### Task 3: Implement `_handle_diagnosis_run()`

Add the handler method. Use `VALID_OUTCOMES` from `reverse_diagnosis` for input validation. Add `_hardware_yaml_path()` helper.

#### Task 4: Verify exit gates

```bash
# Gate 1: Manual smoke (requires server running)
# Start: PYTHONPATH=src python3 -m well_harness.demo_server
# Then: curl -s -X POST http://127.0.0.1:8000/api/diagnosis/run \
#        -H "Content-Type: application/json" \
#        -d '{"outcome":"logic1_active"}' | python3 -c \
#        "import sys,json; d=json.load(sys.stdin); print(d['outcome'], d['total_combos_found'])"

# Gate 2: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 604+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure data query |
| No breaking changes to existing API contracts | ✓ New route only |
| Uses input validation style | ✓ outcome validated against VALID_OUTCOMES |

### Exit Gate

Verify Gate 2 (Gate 1 is a manual smoke — run it if server is available).
