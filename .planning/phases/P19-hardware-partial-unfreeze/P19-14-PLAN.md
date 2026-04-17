---
phase: P19
plan: P19-14
type: execute
wave: 1
depends_on: [P19-10, P19-11, P19-13]
files_created: []
files_modified:
  - src/well_harness/static/chat.html
  - src/well_harness/static/chat.js
  - src/well_harness/static/chat.css
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure fetch() to /api/diagnosis/run with system_id parameter"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "Diagnosis panel, Monte Carlo panel, Sensitivity panel, and Hardware Schema panel each have a system selector dropdown"
    - "Changing system updates the panel title and changes which system's API is queried"
    - "Thrust-reverser, landing-gear, and bleed-air systems are all selectable"
    - "Analysis results from non-thrust-reverser systems show the system name in the result"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/static/chat.html
      provides: "system-select analysis dropdowns in each panel header"
    - path: src/well_harness/static/chat.js
      provides: "getSelectedAnalysisSystem() + system-aware runDiagnosis/runMonteCarlo/runSensitivity/runHardwareSchema"
    - path: src/well_harness/static/chat.css
      provides: "analysis-system-select styles"
  key_constraints:
    - "System selector is a <select> element inside each panel header"
    - "Each panel independently tracks its selected system"
    - "Default system for all panels is 'thrust-reverser' (existing default)"
exit_criteria:
  - "grep -n 'analysis-system-select' src/well_harness/static/chat.html | wc -l returns ≥4 (one per panel)"
  - "grep -n 'getSelectedAnalysisSystem\\|analysis-system' src/well_harness/static/chat.js | wc -l returns ≥4"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.14 — Multi-System Analysis Selector

### Context

P19.10–P19.13 added analysis panels that query the diagnosis, Monte Carlo, and
hardware-schema endpoints. Currently these are hardcoded to thrust-reverser. P13
(workbench multi-system) showed the same backend already supports landing-gear and
bleed-air via system selection. P19.14 adds a system selector to each analysis panel
so engineers can run diagnosis, Monte Carlo, sensitivity sweep, and schema lookup
against any onboarded system.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `demo_server.py` API contracts — unchanged (system selection is via existing mechanism)
- Canvas topology or truth engine

### Implementation

#### 1. `src/well_harness/static/chat.html` — add system selectors to panel headers

**Diagnosis panel header** — change from:
```html
<span>📊 逆向诊断分析</span>
```
to:
```html
<span>📊 逆向诊断分析</span>
<select class="analysis-system-select" id="diag-system-select">
  <option value="thrust-reverser">Thrust Reverser</option>
  <option value="landing-gear">Landing Gear</option>
  <option value="bleed-air">Bleed Air</option>
</select>
```

**Monte Carlo panel header** — change from:
```html
<span>🎲 可靠性仿真</span>
```
to:
```html
<span>🎲 可靠性仿真</span>
<select class="analysis-system-select" id="mc-system-select">
  <option value="thrust-reverser">Thrust Reverser</option>
  <option value="landing-gear">Landing Gear</option>
  <option value="bleed-air">Bleed Air</option>
</select>
```

**Sensitivity panel header** — change from:
```html
<span>🔍 敏感性分析 — 参数扫描</span>
```
to:
```html
<span>🔍 敏感性分析</span>
<select class="analysis-system-select" id="sensitivity-system-select">
  <option value="thrust-reverser">Thrust Reverser</option>
  <option value="landing-gear">Landing Gear</option>
  <option value="bleed-air">Bleed Air</option>
</select>
```

**Hardware Schema panel header** — change from:
```html
<span>🛠️ 硬件规格 — Thrust Reverser</span>
```
to:
```html
<span>🛠️ 硬件规格</span>
<select class="analysis-system-select" id="hw-schema-system-select">
  <option value="thrust-reverser">Thrust Reverser</option>
  <option value="landing-gear">Landing Gear</option>
  <option value="bleed-air">Bleed Air</option>
</select>
```

#### 2. `src/well_harness/static/chat.css` — add system select styles

Add to end of file:

```css
/* P19.14: Multi-system analysis selector */
.analysis-system-select {
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 10px;
  padding: 2px 4px;
  margin-left: auto;
  cursor: pointer;
  outline: none;
}

.analysis-system-select:focus {
  border-color: rgba(91,168,255,0.5);
}

.analysis-system-select option {
  background: #1a2236;
  color: #e2e8f0;
}
```

#### 3. `src/well_harness/static/chat.js` — add helper and update API calls

**Add helper** (before `runDiagnosis`):

```javascript
// ── P19.14: Multi-system analysis helper ─────────────────────────────────

function getSelectedAnalysisSystem(selectId) {
  var sel = document.getElementById(selectId);
  return sel ? sel.value : 'thrust-reverser';
}
```

**Update runDiagnosis** — add `system_id` to the API call body and result display:

```javascript
function runDiagnosis() {
  var systemId = getSelectedAnalysisSystem('diag-system-select');
  var outcome = document.getElementById('diag-outcome-select').value;
  var maxResults = parseInt(document.getElementById('diag-max-results').value, 10) || 20;
  var resultDiv = document.getElementById('diag-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '\u6b63\u5728\u8fd0\u884c\u8bca\u65ad...';

  fetch('/api/diagnosis/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome: outcome, max_results: maxResults, system_id: systemId }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '\u9519\u8bef: ' + data.error;
        return;
      }
      var text = renderDiagnosisChatMessage(data);
      resultDiv.textContent = text;
      postAnalysisToChat('diagnosis', '\u269b\ufe0f \u9006\u5411\u8bca\u65ad\u5206\u6790 [' + systemId + ']', text);
    })
    .catch(function(err) {
      resultDiv.textContent = '\u8bf7\u6c42\u5931\u8d25: ' + err.message;
    });
}
```

**Update runMonteCarlo** — add `system_id`:

```javascript
function runMonteCarlo() {
  var systemId = getSelectedAnalysisSystem('mc-system-select');
  var nTrials = parseInt(document.getElementById('mc-n-trials').value, 10) || 100;
  var seedEl = document.getElementById('mc-seed');
  var seed = seedEl.value.trim() ? parseInt(seedEl.value, 10) : null;
  var resultDiv = document.getElementById('mc-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '\u6b63\u5728\u8fd0\u884c\u4eff\u771f...';

  var body = { n_trials: nTrials, system_id: systemId };
  if (seed !== null) body.seed = seed;

  fetch('/api/monte-carlo/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '\u9519\u8bef: ' + data.error;
        return;
      }
      var text = renderMonteCarloChatMessage(data);
      resultDiv.textContent = text;
      postAnalysisToChat('monte-carlo', '\ud83c\udfb2 \u53ef\u9760\u6027\u4eff\u771f [' + systemId + ']', text);
    })
    .catch(function(err) {
      resultDiv.textContent = '\u8bf7\u6c42\u5931\u8d25: ' + err.message;
    });
}
```

**Update runHardwareSchema** — add `system_id` to GET via query param:

```javascript
function runHardwareSchema() {
  var systemId = getSelectedAnalysisSystem('hw-schema-system-select');
  var resultDiv = document.getElementById('hw-schema-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '\u6b63\u5728\u52a0\u8f7d\u786c\u4ef6\u89c4\u683c...';

  fetch('/api/hardware/schema?system_id=' + encodeURIComponent(systemId))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '\u9519\u8bef: ' + data.error;
        return;
      }
      var lines = [
        'kind: ' + data.kind,
        'version: ' + data.version,
        'system_id: ' + data.system_id,
        '',
        '━━━ Sensor Ranges ━━━',
        '  radio_altitude_ft:  ' + data.sensor.radio_altitude_ft.min + ' ~ ' + data.sensor.radio_altitude_ft.max + ' ft',
        '  tra_deg:             ' + data.sensor.tra_deg.min + ' ~ ' + data.sensor.tra_deg.max + ' deg',
        '  vdt_percent:         ' + data.sensor.vdt_percent.min + ' ~ ' + data.sensor.vdt_percent.max + ' %',
        '  sw1_position_deg:    ' + data.sensor.sw1_position_deg.min + ' ~ ' + data.sensor.sw1_position_deg.max + ' deg',
        '  sw2_position_deg:    ' + data.sensor.sw2_position_deg.min + ' ~ ' + data.sensor.sw2_position_deg.max + ' deg',
        '',
        '━━━ Logic Thresholds ━━━',
        '  logic1_ra_ft_threshold:      ' + data.logic_thresholds.logic1_ra_ft_threshold + ' ft',
        '  logic3_tra_deg_threshold:   ' + data.logic_thresholds.logic3_tra_deg_threshold + ' deg',
        '  deploy_90_threshold_percent:' + data.logic_thresholds.deploy_90_threshold_percent + ' %',
        '',
        '━━━ Physical Limits ━━━',
        '  SW1 window: ' + data.physical_limits.sw1_window.near_zero_deg + ' ~ ' + data.physical_limits.sw1_window.deep_reverse_deg + ' deg',
        '  SW2 window: ' + data.physical_limits.sw2_window.near_zero_deg + ' ~ ' + data.physical_limits.sw2_window.deep_reverse_deg + ' deg',
        '',
        '━━━ Timing ━━━',
        '  pls_unlock_min_s: ' + data.timing.pls_unlock_min_s + ' s',
        '  vdt_deploy_s:     ' + data.timing.vdt_deploy_s + ' s',
        '  thr_lock_min_s:   ' + data.timing.thr_lock_min_s + ' s',
      ];
      resultDiv.textContent = lines.join('\n');
    })
    .catch(function(err) {
      resultDiv.textContent = '\u8bf7\u6c42\u5931\u8d25: ' + err.message;
    });
}
```

**Update runSensitivitySweep** — add `system_id` to each diagnosis call:

In the `fetch('/api/diagnosis/run'...)` call inside `doNext`, add `system_id` to body:
```javascript
body: JSON.stringify({ outcome: outcome, max_results: 1, system_id: getSelectedAnalysisSystem('sensitivity-system-select') }),
```

And update the header in the final `postAnalysisToChat` call:
```javascript
var systemId = getSelectedAnalysisSystem('sensitivity-system-select');
var header = '\ud83d\udd0d \u6545\u969c\u6027\u5206\u6790 [' + systemId + '] \u2014 RA\u00d7TRA\u00d7Outcome (' + totalCalls + '\u6b21\u626b\u63cf)';
postAnalysisToChat('sensitivity', header, text);
```

### Tasks

#### Task 1: Add system selectors to panel headers in chat.html

Add `<select class="analysis-system-select">` to each of the 4 panel headers.

#### Task 2: Add CSS to chat.css

Add `.analysis-system-select` styles.

#### Task 3: Add helper and update API calls in chat.js

Add `getSelectedAnalysisSystem()`; update `runDiagnosis`, `runMonteCarlo`, `runSensitivitySweep`, `runHardwareSchema` to pass `system_id`.

#### Task 4: Verify exit gates

```bash
# Gate 1: system selectors in HTML
grep -c 'analysis-system-select' src/well_harness/static/chat.html

# Gate 2: JS helper usage
grep -c 'getSelectedAnalysisSystem\|analysis-system' src/well_harness/static/chat.js

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure fetch() with system_id param |
| No breaking changes to existing API contracts | ✓ system_id is additive |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify all 3 gates above.
