---
phase: P19
plan: P19-16
type: execute
wave: 1
depends_on: [P15]
files_created: []
files_modified:
  - src/well_harness/demo_server.py
  - src/well_harness/static/chat.js
  - src/well_harness/static/chat.css
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — deterministic validation only"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "GET /api/hardware/schema?system_id=invalid returns HTTP 400 with clear error message"
    - "POST /api/diagnosis/run with system_id=invalid returns HTTP 400"
    - "POST /api/monte-carlo/run with system_id=invalid returns HTTP 400"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/demo_server.py
      provides: "_SYSTEM_YAML_MAP validation, 400 on unknown system_id (all 3 endpoints)"
    - path: src/well_harness/static/chat.js
      provides: "runDiagnosis/runMonteCarlo/runHardwareSchema/runSensitivitySweep: loading state + error display"
  key_constraints:
    - "Invalid system_id → friendly 400 error (not silent 500)"
    - "UI buttons disabled during API call (prevent double-submit)"
    - "Panel error messages shown inline, not only in console"
exit_criteria:
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
  - "grep -n '_SYSTEM_YAML_MAP' src/well_harness/demo_server.py confirms system_id validation"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.16 — Analysis API Robustness + UI Error Handling

### Context

P19.15 added multi-system YAML support, but the backend returns a 500 (Internal Server Error) when an unknown `system_id` is passed — because `FileNotFoundError` from a missing YAML bubbles up uncaught. P19.16 adds proper `system_id` validation (400 + clear message) on all three endpoints and adds frontend loading states + error display to the analysis panels.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `chat.html` — no structural changes
- API contract — error responses are additive (400 replaces 500, not a breaking change)
- Functional behavior — only error paths change

### Implementation

#### 1. `src/well_harness/demo_server.py` — validate system_id on all 3 endpoints

**Update `_hardware_yaml_path()` to raise `FileNotFoundError` on unknown system_id:**

```python
def _hardware_yaml_path(self, system_id: str = "thrust-reverser") -> str:
    import pathlib as _pathlib
    import well_harness as _wh
    pkg_root = _pathlib.Path(_wh.__file__).parent
    repo_root = pkg_root.parent.parent
    filename = _SYSTEM_YAML_MAP.get(system_id)
    if filename is None:
        raise FileNotFoundError(f"Unknown system_id: {system_id!r}. Valid: {sorted(_SYSTEM_YAML_MAP)}")
    return str(repo_root / "config" / "hardware" / filename)
```

**Update DIAGNOSIS_RUN_PATH handler to catch FileNotFoundError → 400:**

```python
yaml_path = self._hardware_yaml_path(system_id)
try:
    engine = ReverseDiagnosisEngine(yaml_path)
    ...
except FileNotFoundError as exc:
    self._send_json(400, {"error": str(exc)})
except Exception as exc:
    self._send_json(500, {"error": str(exc)})
```

**Update MONTE_CARLO_RUN_PATH handler — same pattern:**

```python
except FileNotFoundError as exc:
    self._send_json(400, {"error": str(exc)})
except Exception as exc:
    self._send_json(500, {"error": str(exc)})
```

**Update `_handle_hardware_schema()` to catch FileNotFoundError → 400:**

```python
except FileNotFoundError as exc:
    self._send_json(400, {"error": str(exc)})
except Exception as exc:
    self._send_json(500, {"error": str(exc)})
```

#### 2. `src/well_harness/static/chat.js` — loading state + error display

**Pattern for all 4 run functions** (`runDiagnosis`, `runMonteCarlo`, `runHardwareSchema`, `runSensitivitySweep`):

Before `fetch()`:
```javascript
runBtn.disabled = true;
runBtn.textContent = "运行中...";
```

On `fetch` error:
```javascript
} catch (err) {
    showPanelError(panelId, "请求失败: " + err.message);
} finally {
    runBtn.disabled = false;
    runBtn.textContent = originalText;
}
```

On API error response (non-ok):
```javascript
if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    showPanelError(panelId, "错误 " + response.status + ": " + (errData.error || response.statusText));
    return;
}
```

**New helper function:**
```javascript
function showPanelError(panelId, message) {
    var panel = document.getElementById(panelId);
    if (!panel) return;
    var existing = panel.querySelector('.analysis-panel-error');
    if (existing) existing.remove();
    var errEl = document.createElement('div');
    errEl.className = 'analysis-panel-error';
    errEl.textContent = message;
    panel.querySelector('.analysis-panel-body').appendChild(errEl);
}
```

#### 3. `src/well_harness/static/chat.css` — error style

```css
.analysis-panel-error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 4px;
    color: #fca5a5;
    font-size: 12px;
    padding: 8px 12px;
    margin-top: 8px;
}
```

### Tasks

#### Task 1: Update `_hardware_yaml_path()` to raise `FileNotFoundError` on unknown system_id

Add validation inside the method.

#### Task 2: Add `FileNotFoundError` → 400 handling to all 3 endpoint handlers

DIAGNOSIS_RUN_PATH, MONTE_CARLO_RUN_PATH, `_handle_hardware_schema`.

#### Task 3: Add loading state + error display to all 4 JS run functions

`showPanelError()` helper + btn disabled during fetch + error display in panel body.

#### Task 4: Add `.analysis-panel-error` CSS

Red tinted error box.

#### Task 5: Verify exit gates

```bash
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Deterministic validation only |
| No breaking changes to existing API contracts | ✓ 400 replaces 500 (more informative), existing paths unchanged |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify `python3 -m pytest -x --tb=short -q 2>&1 | tail -3` shows 619+ passed.
