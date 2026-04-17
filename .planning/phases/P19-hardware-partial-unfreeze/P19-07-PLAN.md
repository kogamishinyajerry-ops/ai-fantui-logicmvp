---
phase: P19
plan: P19-07
type: execute
wave: 1
depends_on: [P19-02]
files_created: []
files_modified:
  - src/well_harness/monte_carlo_engine.py
  - src/well_harness/demo_server.py
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure numerical computation"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "POST /api/monte-carlo/run accepts n_trials and optional seed, returns ReliabilityResult as dict"
    - "ReliabilityResult is serialized to plain dict via _reliability_result_to_dict()"
    - "Input validation: n_trials capped at 10000, seed is optional integer"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/monte_carlo_engine.py
      provides: "_reliability_result_to_dict() helper + POST /api/monte-carlo/run route"
      min_lines: 20
  key_constraints:
    - "Only add — do NOT modify run() behavior"
    - "Frozen dataclass not available — ReliabilityResult is plain dataclass (no frozen=True)"
    - "Hardware YAML path resolved dynamically from package root"
    - "Error cases return 400/500 with error message"
exit_criteria:
  - "python3 -c 'from well_harness.monte_carlo_engine import _reliability_result_to_dict, MonteCarloEngine, ReliabilityResult; e=MonteCarloEngine(\"config/hardware/thrust_reverser_hardware_v1.yaml\"); r=e.run(10, seed=42); print(_reliability_result_to_dict(r))' runs without error"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.7 — Monte Carlo Reliability API Endpoint

### Context

P19.2 created `MonteCarloEngine.run()` returning `ReliabilityResult`.
P19.6 exposed the diagnosis engine via `/api/diagnosis/run`.
P19.7 mirrors that pattern for the Monte Carlo engine via `/api/monte-carlo/run`.

### Architecture

```
Browser POST /api/monte-carlo/run
  { "n_trials": 1000, "seed": 42 }
                    ↓
         demo_server.py route
                    ↓
         MonteCarloEngine(hardware_yaml)
                    ↓
         engine.run(n_trials, seed)
                    ↓
         _reliability_result_to_dict(result) → JSON
```

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `MonteCarloEngine.run()` — unchanged
- Existing API contracts

### Implementation

#### 1. `src/well_harness/monte_carlo_engine.py` — add serializer helper

Add before the `MonteCarloEngine` class:

```python
def _reliability_result_to_dict(result: ReliabilityResult) -> dict:
    """Convert a ReliabilityResult to a plain dict for JSON serialization."""
    return {
        "n_trials": result.n_trials,
        "n_failures": result.n_failures,
        "success_rate": result.success_rate,
        "mean_cycles_to_failure": result.mean_cycles_to_failure,
        "mtbf_cycles": result.mtbf_cycles,
        "seed": result.seed,
        "failure_modes": result.failure_modes,
        "sw1_window_crossings_mean": result.sw1_window_crossings_mean,
        "sw2_window_crossings_mean": result.sw2_window_crossings_mean,
    }
```

#### 2. `src/well_harness/demo_server.py` — add Flask route

Add path constant:

```python
MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
```

Register in `do_POST` 404 guard set:

```python
MONTE_CARLO_RUN_PATH,
```

Add handler in `do_POST` routing block (after `DIAGNOSIS_RUN_PATH`):

```python
# P19.7: Monte Carlo reliability simulation
if parsed.path == MONTE_CARLO_RUN_PATH:
    n_trials_raw = request_payload.get("n_trials", 100)
    try:
        n_trials = int(n_trials_raw)
    except (TypeError, ValueError):
        self._send_json(400, {"error": "n_trials must be an integer"})
        return
    n_trials = max(1, min(n_trials, 10000))  # cap at 10000

    seed = None
    if "seed" in request_payload:
        try:
            seed = int(request_payload["seed"])
        except (TypeError, ValueError):
            self._send_json(400, {"error": "seed must be an integer"})
            return

    yaml_path = self._hardware_yaml_path()
    try:
        engine = MonteCarloEngine(yaml_path)
        result = engine.run(n_trials, seed=seed)
        self._send_json(200, _reliability_result_to_dict(result))
    except Exception as exc:
        self._send_json(500, {"error": str(exc)})
    return
```

Import at top of do_POST handler section (after other well_harness imports):

```python
from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
```

### Tasks

#### Task 1: Add `_reliability_result_to_dict()` to `monte_carlo_engine.py`

Add standalone helper before `MonteCarloEngine`.

#### Task 2: Add `MONTE_CARLO_RUN_PATH` constant and route to `demo_server.py`

- Add path constant near `DIAGNOSIS_RUN_PATH`
- Register in 404 guard set
- Import `MonteCarloEngine` and `_reliability_result_to_dict` in `do_POST`
- Add handler block after `DIAGNOSIS_RUN_PATH` handler

#### Task 3: Verify exit gates

```bash
# Gate 1: Module import + round-trip
python3 -c 'from well_harness.monte_carlo_engine import _reliability_result_to_dict, MonteCarloEngine; \
  e=MonteCarloEngine("config/hardware/thrust_reverser_hardware_v1.yaml"); \
  r=e.run(10, seed=42); \
  d=_reliability_result_to_dict(r); \
  print("success_rate:", d["success_rate"], "n_trials:", d["n_trials"], "seed:", d["seed"])'

# Gate 2: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 604+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure numerical simulation |
| No breaking changes to existing API contracts | ✓ New route only |
| Input validation | ✓ n_trials capped 1-10000, seed optional int |

### Exit Gate

Verify both gates above.
