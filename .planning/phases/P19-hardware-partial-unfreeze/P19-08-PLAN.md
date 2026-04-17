---
phase: P19
plan: P19-08
type: execute
wave: 1
depends_on: [P19-01, P19-06, P19-07]
files_created: []
files_modified:
  - src/well_harness/demo_server.py
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure data serialization"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "GET /api/hardware/schema returns the full hardware YAML as a serializable dict"
    - "Route is GET (not POST) — no request body needed"
    - "Dict includes: sensor ranges, switch windows, logic thresholds, timing delays, actuator specs"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/demo_server.py
      provides: "GET /api/hardware/schema route — returns YAML as JSON dict"
      min_lines: 30
  key_constraints:
    - "Read-only — does not modify any state"
    - "Hardware YAML path resolved dynamically from package root"
    - "Returns 200 with JSON dict; error returns 500"
exit_criteria:
  - "python3 -c 'import json; from well_harness.hardware_schema import load_thrust_reverser_hardware; import pathlib, well_harness; pkg_root=pathlib.Path(well_harness.__file__).parent; hw=load_thrust_reverser_hardware(str(pkg_root.parent.parent/\"config\"/\"hardware\"/\"thrust_reverser_hardware_v1.yaml\")); print(list(hw.model_dump().keys()))' runs without error"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.8 — Hardware Schema Discovery Endpoint

### Context

P19.1 created the hardware YAML schema. P19.6 and P19.7 exposed diagnosis and Monte Carlo endpoints. P19.8 completes the trio with a **schema discovery endpoint** so the browser can:
- Discover available parameter ranges for building UI sliders/inputs
- Populate dropdowns for `outcome` selection (valid outcomes)
- Show hardware specs in a "system info" panel

### Architecture

```
Browser GET /api/hardware/schema
                    ↓
         demo_server.py route
                    ↓
         load_thrust_reverser_hardware(yaml_path)
                    ↓
         hw.model_dump() → dict → JSON
```

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- Existing API contracts
- Hardware YAML is read-only

### Implementation

#### `src/well_harness/demo_server.py`

Add path constant:

```python
HARDWARE_SCHEMA_PATH = "/api/hardware/schema"
```

Register in both `do_GET` and `do_POST` 404 guard sets:

```python
# In do_GET:
elif parsed.path == HARDWARE_SCHEMA_PATH:
    self._handle_hardware_schema()
    return

# In do_POST:
HARDWARE_SCHEMA_PATH,
```

Add handler method:

```python
def _handle_hardware_schema(self) -> None:
    """Return the full hardware YAML as a JSON dict (P19.8)."""
    yaml_path = self._hardware_yaml_path()
    try:
        from well_harness.hardware_schema import load_thrust_reverser_hardware
        hw = load_thrust_reverser_hardware(yaml_path)
        self._send_json(200, hw.model_dump())
    except Exception as exc:
        self._send_json(500, {"error": str(exc)})
```

### Tasks

#### Task 1: Add `HARDWARE_SCHEMA_PATH` constant

Add near `MONTE_CARLO_RUN_PATH`.

#### Task 2: Register in `do_GET` 404 guard

Find `do_GET` method and add handler registration in its 404 set, plus the routing branch.

#### Task 3: Register in `do_POST` 404 guard

Add `HARDWARE_SCHEMA_PATH` to the POST 404 guard set.

#### Task 4: Implement `_handle_hardware_schema()`

Add method to the class. Use `_hardware_yaml_path()` helper from P19.6.

#### Task 5: Verify exit gates

```bash
# Gate 1: Module smoke — hw.model_dump() works
python3 -c 'from well_harness.hardware_schema import load_thrust_reverser_hardware; \
  import pathlib, well_harness; \
  pkg_root=pathlib.Path(well_harness.__file__).parent; \
  hw=load_thrust_reverser_hardware(str(pkg_root.parent.parent/"config"/"hardware"/"thrust_reverser_hardware_v1.yaml")); \
  keys=list(hw.model_dump().keys()); print("top-level keys:", keys); \
  print("logic_thresholds:", list(hw.logic_thresholds.model_dump().keys())); \
  print("physical_limits:", list(hw.physical_limits.model_dump().keys()))'

# Gate 2: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 604+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ Read-only endpoint |
| No LLM calls | ✓ Pure data serialization |
| No breaking changes to existing API contracts | ✓ New GET route only |
| Hardware YAML is read-only | ✓ Only calls model_dump() |

### Exit Gate

Verify both gates above.
