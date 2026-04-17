---
phase: P19
plan: P19-11
type: execute
wave: 1
depends_on: [P19-08, P19-10]
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
  - "No LLM calls — pure fetch() to existing /api/hardware/schema endpoint"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "Chat drawer toolbar has a new '硬件规格' button alongside the '📊 分析工具' button"
    - "Clicking '硬件规格' fetches /api/hardware/schema and renders a formatted spec table inside the chat drawer"
    - "The rendered schema shows: sensor ranges, logic thresholds (RA/TRA/VDT), physical switch windows (SW1/SW2), and timing parameters"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/static/chat.html
      provides: "hardware-schema-btn in chat-drawer-toolbar"
    - path: src/well_harness/static/chat.js
      provides: "openHardwareSchemaPanel() + runHardwareSchema()"
    - path: src/well_harness/static/chat.css
      provides: "hardware-schema-panel styles"
  key_constraints:
    - "Inline panel below toolbar inside chat-drawer — no modal, no new route"
    - "Schema renders as plain text table (no new dependencies)"
    - "Panel can stay open alongside diagnosis/Monte Carlo panels (they stack)"
exit_criteria:
  - "grep -n 'openHardwareSchemaPanel\\|runHardwareSchema' src/well_harness/static/chat.js returns ≥1 match"
  - "grep -n 'hardware-schema-btn\\|hardware-schema-panel' src/well_harness/static/chat.css returns ≥1 match"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.11 — Hardware Schema Browser Panel

### Context

P19.8 created `GET /api/hardware/schema` which returns the full hardware YAML spec as JSON.
P19.10 added the Analysis Tools panel for diagnosis and Monte Carlo. P19.11 adds a "硬件规格"
browser button to the toolbar that fetches and renders the schema as a readable parameter table.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `demo_server.py` API contracts — unchanged
- Canvas topology or truth engine

### Implementation

#### 1. `src/well_harness/static/chat.html` — add hardware schema button

In `.chat-drawer-toolbar` (after the `chat-analysis-btn` added by P19.10):

```html
<button type="button" class="drawer-tool-btn" id="chat-hardware-schema-btn">🛠️ 硬件规格</button>
```

#### 2. `src/well_harness/static/chat.html` — add inline panel

After the `#monte-carlo-panel` div (before `#chat-messages`):

```html
<!-- Hardware schema panel -->
<div class="hardware-schema-panel" id="hardware-schema-panel" hidden>
  <div class="analysis-panel-header">
    <span>🛠️ 硬件规格 — Thrust Reverser</span>
    <button type="button" class="analysis-panel-close" data-close="hardware-schema-panel">✕</button>
  </div>
  <div class="analysis-panel-body">
    <button type="button" class="analysis-run-btn" id="hw-schema-fetch-btn">加载规格</button>
    <div class="analysis-result" id="hw-schema-result" hidden></div>
  </div>
</div>
```

#### 3. `src/well_harness/static/chat.css` — add hardware schema panel styles

Add after the P19.10 analysis panel styles (before the closing `}` or at end of file):

```css
/* P19.11: Hardware schema browser */
.hardware-schema-panel {
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 10px 12px;
}
```

The existing `.analysis-panel-header`, `.analysis-panel-body`, `.analysis-run-btn`,
`.analysis-result`, and `.analysis-panel-close` styles from P19.10 already cover
the hardware schema panel elements.

#### 4. `src/well_harness/static/chat.js` — add schema functions

Add inside the IIFE (same section as P19.10 functions, before the closing `})();`):

```javascript
// ── P19.11: Hardware schema browser ───────────────────────────────────────

function openHardwareSchemaPanel() {
  var panel = document.getElementById('hardware-schema-panel');
  if (panel) {
    panel.hidden = !panel.hidden;
  }
}

function runHardwareSchema() {
  var resultDiv = document.getElementById('hw-schema-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '正在加载硬件规格...';

  fetch('/api/hardware/schema')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '错误: ' + data.error;
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
        '  SW1 max TRA: ' + data.physical_limits.sw1_max_tra_deg + ' deg',
        '  SW2 max TRA: ' + data.physical_limits.sw2_max_tra_deg + ' deg',
        '',
        '━━━ Timing ━━━',
        '  pls_unlock_min_s: ' + data.timing.pls_unlock_min_s + ' s',
        '  vdt_deploy_s:     ' + data.timing.vdt_deploy_s + ' s',
        '  thr_lock_min_s:   ' + data.timing.thr_lock_min_s + ' s',
      ];
      resultDiv.textContent = lines.join('\n');
    })
    .catch(function(err) {
      resultDiv.textContent = '请求失败: ' + err.message;
    });
}
```

Then wire the button listeners (add to the P19.10 event wiring section or alongside it):

```javascript
// Wire hardware schema button
var hwSchemaBtn = document.getElementById('chat-hardware-schema-btn');
if (hwSchemaBtn) hwSchemaBtn.addEventListener('click', openHardwareSchemaPanel);

var hwSchemaFetchBtn = document.getElementById('hw-schema-fetch-btn');
if (hwSchemaFetchBtn) hwSchemaFetchBtn.addEventListener('click', runHardwareSchema);
```

### Tasks

#### Task 1: Add hardware schema button to chat.html toolbar

Add `<button ... id="chat-hardware-schema-btn">` alongside the analysis button.

#### Task 2: Add hardware schema panel to chat.html

Add `#hardware-schema-panel` div after `#monte-carlo-panel`.

#### Task 3: Add CSS to chat.css

Add `.hardware-schema-panel` wrapper style (header/body/result already inherited from P19.10).

#### Task 4: Add JS handlers to chat.js

Add `openHardwareSchemaPanel()`, `runHardwareSchema()` and wire `chat-hardware-schema-btn` + `hw-schema-fetch-btn` listeners.

#### Task 5: Verify exit gates

```bash
# Gate 1: JS functions exist
grep -n 'openHardwareSchemaPanel\|runHardwareSchema' src/well_harness/static/chat.js

# Gate 2: CSS exists
grep -n 'hardware-schema-btn\|hardware-schema-panel' src/well_harness/static/chat.css

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure fetch() to /api/hardware/schema |
| No breaking changes to existing API contracts | ✓ New UI only |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify all 3 gates above.
