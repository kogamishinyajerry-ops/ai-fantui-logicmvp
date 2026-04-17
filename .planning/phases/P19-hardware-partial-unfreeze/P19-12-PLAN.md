---
phase: P19
plan: P19-12
type: execute
wave: 1
depends_on: [P19-10, P19-11]
files_created: []
files_modified:
  - src/well_harness/static/chat.js
  - src/well_harness/static/chat.css
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure fetch() to existing REST endpoints"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "Diagnosis and Monte Carlo run results appear as styled chat messages in the chat-messages area (not just inside the inline panel divs)"
    - "Each analysis result is prepended to the chat as an AI message with a distinct visual style"
    - "Panel result divs are cleared after results are posted to chat"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/static/chat.js
      provides: "renderDiagnosisChatMessage() + renderMonteCarloChatMessage() + postAnalysisToChat()"
    - path: src/well_harness/static/chat.css
      provides: ".chat-message-analysis diagnosis / monte-carlo message styles"
  key_constraints:
    - "Results go to chat-messages area as .chat-message-analysis elements"
    - "Panel result divs clear after posting (hidden + text cleared)"
    - "Uses existing addMessage() infrastructure with custom content type"
exit_criteria:
  - "grep -n 'renderDiagnosisChatMessage\\|renderMonteCarloChatMessage' src/well_harness/static/chat.js returns ≥1 match"
  - "grep -n 'chat-message-analysis\\|.msg-analysis' src/well_harness/static/chat.css returns ≥1 match"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.12 — Analysis Results → Chat History

### Context

P19.10 wired diagnosis and Monte Carlo panels to fetch `/api/diagnosis/run` and
`/api/monte-carlo/run`, displaying results in `.analysis-result` divs inside the panels.
P19.12 moves those results into the **chat message history** as styled AI messages, so
they are part of the session record and scroll naturally with the conversation.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `demo_server.py` API contracts — unchanged
- Canvas topology or truth engine
- Panel HTML structure (panels stay, results also appear in chat)

### Implementation

#### 1. `src/well_harness/static/chat.css` — add analysis message styles

Add after existing `.chat-message-ai` styles or at end of file:

```css
/* P19.12: Analysis result chat messages */
.chat-message-analysis {
  background: rgba(91,168,255,0.06);
  border: 1px solid rgba(91,168,255,0.18);
  border-radius: 10px;
  padding: 10px 14px;
  margin: 6px 0;
}

.chat-message-analysis .chat-message-content {
  font-size: 12px;
  line-height: 1.6;
}

.msg-analysis-header {
  font-size: 11px;
  font-weight: 700;
  color: #5ba8ff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.msg-analysis-header::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #5ba8ff;
}

.msg-analysis-header.diagnosis {
  color: #a78bfa;
}
.msg-analysis-header.diagnosis::before {
  background: #a78bfa;
}

.msg-analysis-header.monte-carlo {
  color: #34d399;
}
.msg-analysis-header.monte-carlo::before {
  background: #34d399;
}

.msg-analysis-body {
  color: #e2e8f0;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 11px;
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
}
```

#### 2. `src/well_harness/static/chat.js` — add chat message renderers

Add helper functions and modify `runDiagnosis()` / `runMonteCarlo()` to post results
to the chat area. Insert before the closing `})();` of the IIFE (after the P19.11 wiring).

**Helper: renderDiagnosisChatMessage(data)**

```javascript
function renderDiagnosisChatMessage(data) {
  var lines = [];
  lines.push('目标结果: ' + data.outcome);
  lines.push('满足组合数: ' + data.total_combos_found + ' / ' + data.grid_resolution + '-step grid');
  lines.push('时间戳: ' + data.timestamp);
  if (data.results && data.results.length > 0) {
    lines.push('');
    lines.push('前 ' + Math.min(3, data.results.length) + ' 个示例组合:');
    data.results.slice(0, 3).forEach(function(r, i) {
      lines.push(
        '  [' + (i + 1) + '] RA=' + r.radio_altitude_ft.toFixed(1) +
        'ft  TRA=' + r.tra_deg.toFixed(2) + '\u00b0' +
        '  SW1=' + r.sw1_closed +
        '  SW2=' + r.sw2_closed +
        '  VDT=' + r.vdt_percent.toFixed(0) + '%'
      );
    });
  }
  return lines.join('\n');
}
```

**Helper: renderMonteCarloChatMessage(data)**

```javascript
function renderMonteCarloChatMessage(data) {
  var rate = (data.success_rate * 100).toFixed(1);
  var lines = [];
  lines.push('仿真次数: ' + data.n_trials + (data.seed !== null ? '  seed=' + data.seed : '  (random)'));
  lines.push('成功率: ' + rate + '%');
  lines.push('MTBF: ' + data.mtbf_cycles.toFixed(1) + ' cycles');
  lines.push('');
  lines.push('故障模式:');
  lines.push('  SW1 missed: ' + (data.failure_modes.sw1_missed || 0));
  lines.push('  SW2 missed: ' + (data.failure_modes.sw2_missed || 0));
  lines.push('  TRA stall: ' + (data.failure_modes.tra_stall || 0));
  lines.push('  RA sensor: ' + (data.failure_modes.ra_sensor_failure || 0));
  lines.push('');
  lines.push('平均开关窗口通过次数:');
  lines.push('  SW1: ' + data.sw1_window_crossings_mean.toFixed(2));
  lines.push('  SW2: ' + data.sw2_window_crossings_mean.toFixed(2));
  return lines.join('\n');
}
```

**Helper: postAnalysisToChat(type, header, bodyText)**

```javascript
function postAnalysisToChat(type, header, bodyText) {
  var messagesDiv = document.getElementById('chat-messages');
  if (!messagesDiv) return;

  var article = document.createElement('article');
  article.className = 'chat-message chat-message-ai chat-message-analysis';

  var avatar = document.createElement('div');
  avatar.className = 'chat-message-avatar';
  avatar.textContent = type === 'diagnosis' ? '🔬' : '🎲';

  var content = document.createElement('div');
  content.className = 'chat-message-content';

  var hdr = document.createElement('div');
  hdr.className = 'msg-analysis-header ' + type;
  hdr.textContent = header;

  var body = document.createElement('p');
  body.className = 'msg-analysis-body';
  body.textContent = bodyText;

  content.appendChild(hdr);
  content.appendChild(body);
  article.appendChild(avatar);
  article.appendChild(content);
  messagesDiv.appendChild(article);

  // Scroll to bottom
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
```

**Modify runDiagnosis()** — after displaying in the result div, also post to chat:

Replace the `.then` success block in `runDiagnosis()` with:

```javascript
      .then(function(data) {
        if (data.error) {
          resultDiv.textContent = '错误: ' + data.error;
          return;
        }
        var text = renderDiagnosisChatMessage(data);
        resultDiv.textContent = text;
        // Also post to chat history
        postAnalysisToChat('diagnosis', '\u269b\ufe0f 逆向诊断分析', text);
      })
```

**Modify runMonteCarlo()** — same pattern:

```javascript
      .then(function(data) {
        if (data.error) {
          resultDiv.textContent = '错误: ' + data.error;
          return;
        }
        var text = renderMonteCarloChatMessage(data);
        resultDiv.textContent = text;
        // Also post to chat history
        postAnalysisToChat('monte-carlo', '\ud83c\udfb2 可靠性仿真', text);
      })
```

### Tasks

#### Task 1: Add CSS to chat.css

Add `.chat-message-analysis`, `.msg-analysis-header`, `.msg-analysis-body` styles.

#### Task 2: Add JS renderers to chat.js

Add `renderDiagnosisChatMessage()`, `renderMonteCarloChatMessage()`, `postAnalysisToChat()` helpers.

#### Task 3: Modify runDiagnosis() and runMonteCarlo()

Call `postAnalysisToChat()` after populating the result div.

#### Task 4: Verify exit gates

```bash
# Gate 1: JS functions exist
grep -n 'renderDiagnosisChatMessage\|renderMonteCarloChatMessage' src/well_harness/static/chat.js

# Gate 2: CSS exists
grep -n 'chat-message-analysis\|\.msg-analysis' src/well_harness/static/chat.css

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure fetch() + local render |
| No breaking changes to existing API contracts | ✓ Results still display in panels |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify all 3 gates above.
