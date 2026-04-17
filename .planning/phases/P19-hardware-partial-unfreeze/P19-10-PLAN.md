---
phase: P19
plan: P19-10
type: execute
wave: 1
depends_on: [P19-06, P19-07, P19-08]
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
  - "No LLM calls — pure fetch() to new REST endpoints"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "Chat drawer toolbar has two new analysis buttons: '诊断分析' and '可靠性仿真'"
    - "Clicking '诊断分析' opens an inline outcome selector; submitting fetches /api/diagnosis/run and shows result count + sample combos"
    - "Clicking '可靠性仿真' opens an inline n_trials input; submitting fetches /api/monte-carlo/run and shows success_rate + MTBF"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/static/chat.html
      provides: "analysis toolbar buttons in chat-drawer-toolbar"
    - path: src/well_harness/static/chat.js
      provides: "openDiagnosisPanel() + openMonteCarloPanel() + runDiagnosis() + runMonteCarlo()"
    - path: src/well_harness/static/chat.css
      provides: "analysis panel styles"
  key_constraints:
    - "Inline panels slide open below toolbar inside chat-drawer — no modal, no new route"
    - "Analysis results render as plain text in the chat messages area"
    - "No changes to demo_server.py API contracts"
exit_criteria:
  - "grep -n 'openDiagnosisPanel\|openMonteCarloPanel' src/well_harness/static/chat.js returns ≥1 match"
  - "grep -n 'analysis-btn\|analysis-panel' src/well_harness/static/chat.css returns ≥1 match"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.10 — Analysis Tools Panel (Frontend Integration)

### Context

P19.6/P19.7/P19.8 created three REST endpoints. P19.10 connects the chat UI to
those endpoints via an "Analysis Tools" panel inside the existing chat drawer.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `demo_server.py` API contracts — unchanged
- Canvas topology or truth engine

### Implementation

#### 1. `src/well_harness/static/chat.html` — add analysis buttons

In the `.chat-drawer-toolbar` section (after existing buttons), add:

```html
<button type="button" class="drawer-tool-btn" id="chat-analysis-btn">📊 分析工具</button>
```

#### 2. `src/well_harness/static/chat.html` — add inline panels

After the `.chat-shortcut-strip` div (before `.chat-messages`), add two collapsible panels:

```html
<!-- Diagnosis panel -->
<div class="analysis-panel" id="diagnosis-panel" hidden>
  <div class="analysis-panel-header">
    <span>📊 逆向诊断分析</span>
    <button type="button" class="analysis-panel-close" data-close="diagnosis-panel">✕</button>
  </div>
  <div class="analysis-panel-body">
    <label for="diag-outcome-select">目标结果:</label>
    <select id="diag-outcome-select">
      <option value="logic1_active">logic1_active — RA&lt;6ft + SW1 closed</option>
      <option value="logic3_active">logic3_active — TRA≤-11.74 + SW2 closed</option>
      <option value="thr_lock_active">thr_lock_active — PLS unlocked</option>
      <option value="deploy_confirmed">deploy_confirmed — VDT≥90%</option>
      <option value="tls_unlocked">tls_unlocked</option>
      <option value="pls_unlocked">pls_unlocked</option>
    </select>
    <label for="diag-max-results">最大结果数:</label>
    <input type="number" id="diag-max-results" value="20" min="1" max="1000">
    <button type="button" class="analysis-run-btn" id="diag-run-btn">运行诊断</button>
    <div class="analysis-result" id="diag-result" hidden></div>
  </div>
</div>

<!-- Monte Carlo panel -->
<div class="analysis-panel" id="monte-carlo-panel" hidden>
  <div class="analysis-panel-header">
    <span>🎲 可靠性仿真</span>
    <button type="button" class="analysis-panel-close" data-close="monte-carlo-panel">✕</button>
  </div>
  <div class="analysis-panel-body">
    <label for="mc-n-trials">仿真次数:</label>
    <input type="number" id="mc-n-trials" value="100" min="1" max="10000">
    <label for="mc-seed">随机种子 (可选):</label>
    <input type="number" id="mc-seed" placeholder="留空使用随机">
    <button type="button" class="analysis-run-btn" id="mc-run-btn">运行仿真</button>
    <div class="analysis-result" id="mc-result" hidden></div>
  </div>
</div>
```

#### 3. `src/well_harness/static/chat.css` — add analysis panel styles

Add to end of chat.css:

```css
/* P19.10: Analysis tools panel */
.chat-drawer-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.analysis-panel {
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 10px 12px;
}

.analysis-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #5ba8ff;
  margin-bottom: 8px;
}

.analysis-panel-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
}

.analysis-panel-close:hover {
  color: rgba(255,255,255,0.8);
}

.analysis-panel-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.analysis-panel-body label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
}

.analysis-panel-body select,
.analysis-panel-body input[type="number"] {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 12px;
  padding: 5px 8px;
  width: 100%;
  box-sizing: border-box;
}

.analysis-run-btn {
  background: #5ba8ff;
  border: none;
  border-radius: 6px;
  color: #0a0f1e;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  text-align: center;
}

.analysis-run-btn:hover {
  background: #7dbfff;
}

.analysis-result {
  background: rgba(91,168,255,0.08);
  border: 1px solid rgba(91,168,255,0.2);
  border-radius: 6px;
  color: #e2e8f0;
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  line-height: 1.5;
  padding: 8px;
  white-space: pre-wrap;
}
```

#### 4. `src/well_harness/static/chat.js` — add analysis handlers

Add in the toolbar button initialization section (near where other drawer toolbar buttons are wired, around the DOMContentLoaded event handler or after `initChat()`):

```javascript
// ── P19.10: Analysis tools panel ─────────────────────────────────────────

function openDiagnosisPanel() {
  var panel = document.getElementById('diagnosis-panel');
  var mcPanel = document.getElementById('monte-carlo-panel');
  if (panel) {
    panel.hidden = !panel.hidden;
  }
  if (mcPanel) {
    mcPanel.hidden = true;
  }
}

function openMonteCarloPanel() {
  var panel = document.getElementById('monte-carlo-panel');
  var diagPanel = document.getElementById('diagnosis-panel');
  if (panel) {
    panel.hidden = !panel.hidden;
  }
  if (diagPanel) {
    diagPanel.hidden = true;
  }
}

function runDiagnosis() {
  var outcome = document.getElementById('diag-outcome-select').value;
  var maxResults = parseInt(document.getElementById('diag-max-results').value, 10) || 20;
  var resultDiv = document.getElementById('diag-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '正在运行诊断...';

  fetch('/api/diagnosis/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome: outcome, max_results: maxResults }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '错误: ' + data.error;
        return;
      }
      var lines = [
        '目标结果: ' + data.outcome,
        '满足组合数: ' + data.total_combos_found + ' / ' + data.grid_resolution + '-step grid',
        '时间戳: ' + data.timestamp,
        '',
        '前 3 个示例组合:',
      ];
      data.results.slice(0, 3).forEach(function(r, i) {
        lines.push(
          '  [' + (i + 1) + '] RA=' + r.radio_altitude_ft.toFixed(1) +
          'ft  TRA=' + r.tra_deg.toFixed(2) + '°' +
          '  SW1=' + r.sw1_closed +
          '  SW2=' + r.sw2_closed +
          '  VDT=' + r.vdt_percent.toFixed(0) + '%'
        );
      });
      resultDiv.textContent = lines.join('\n');
    })
    .catch(function(err) {
      resultDiv.textContent = '请求失败: ' + err.message;
    });
}

function runMonteCarlo() {
  var nTrials = parseInt(document.getElementById('mc-n-trials').value, 10) || 100;
  var seedEl = document.getElementById('mc-seed');
  var seed = seedEl.value.trim() ? parseInt(seedEl.value, 10) : null;
  var resultDiv = document.getElementById('mc-result');
  resultDiv.hidden = false;
  resultDiv.textContent = '正在运行仿真...';

  var body = { n_trials: nTrials };
  if (seed !== null) body.seed = seed;

  fetch('/api/monte-carlo/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        resultDiv.textContent = '错误: ' + data.error;
        return;
      }
      var rate = (data.success_rate * 100).toFixed(1);
      var lines = [
        '仿真次数: ' + data.n_trials + (data.seed !== null ? '  seed=' + data.seed : '  (random)'),
        '成功率: ' + rate + '%',
        'MTBF: ' + data.mtbf_cycles.toFixed(1) + ' cycles',
        '',
        '故障模式:',
        '  SW1 missed: ' + (data.failure_modes.sw1_missed || 0),
        '  SW2 missed: ' + (data.failure_modes.sw2_missed || 0),
        '  TRA stall: ' + (data.failure_modes.tra_stall || 0),
        '  RA sensor: ' + (data.failure_modes.ra_sensor_failure || 0),
        '',
        '平均开关窗口通过次数:',
        '  SW1: ' + data.sw1_window_crossings_mean.toFixed(2),
        '  SW2: ' + data.sw2_window_crossings_mean.toFixed(2),
      ];
      resultDiv.textContent = lines.join('\n');
    })
    .catch(function(err) {
      resultDiv.textContent = '请求失败: ' + err.message;
    });
}
```

Then wire up the event listeners (add at end of `initChat()` or inside `DOMContentLoaded`):

```javascript
// Wire analysis panel buttons
var analysisBtn = document.getElementById('chat-analysis-btn');
if (analysisBtn) analysisBtn.addEventListener('click', function() {
  var diagPanel = document.getElementById('diagnosis-panel');
  var mcPanel = document.getElementById('monte-carlo-panel');
  // Toggle: if both hidden, open diagnosis; otherwise toggle each
  if (diagPanel && diagPanel.hidden && mcPanel && mcPanel.hidden) {
    diagPanel.hidden = false;
  } else if (diagPanel) {
    diagPanel.hidden = !diagPanel.hidden;
  }
});

var diagRunBtn = document.getElementById('diag-run-btn');
if (diagRunBtn) diagRunBtn.addEventListener('click', runDiagnosis);

var mcRunBtn = document.getElementById('mc-run-btn');
if (mcRunBtn) mcRunBtn.addEventListener('click', runMonteCarlo);

// Wire close buttons
document.querySelectorAll('.analysis-panel-close').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var panelId = btn.getAttribute('data-close');
    var panel = document.getElementById(panelId);
    if (panel) panel.hidden = true;
  });
});
```

### Tasks

#### Task 1: Add analysis button to chat.html toolbar

Add `📊 分析工具` button in `.chat-drawer-toolbar`.

#### Task 2: Add inline panels to chat.html

Add diagnosis and Monte Carlo panels after `.chat-shortcut-strip`.

#### Task 3: Add CSS to chat.css

Add analysis panel styles.

#### Task 4: Add JS handlers to chat.js

Add `openDiagnosisPanel()`, `openMonteCarloPanel()`, `runDiagnosis()`, `runMonteCarlo()` functions and wire event listeners in `initChat()`.

#### Task 5: Verify exit gates

```bash
# Gate 1: JS functions exist
grep -n 'openDiagnosisPanel\|openMonteCarloPanel' src/well_harness/static/chat.js

# Gate 2: CSS exists
grep -n 'analysis-btn\|analysis-panel' src/well_harness/static/chat.css

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure fetch() to REST endpoints |
| No breaking changes to existing API contracts | ✓ New UI only |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify all 3 gates above.
