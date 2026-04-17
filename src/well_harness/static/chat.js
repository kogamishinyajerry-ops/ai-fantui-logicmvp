/* ── chat.js — Phase A Canvas Shell ── */

(function() {
  var currentSystem = 'thrust-reverser';
  var chatMessages = document.getElementById('chat-messages');
  var chatInput = document.getElementById('chat-input');
  var sendBtn = document.getElementById('chat-send-btn');
  var inputDock = document.querySelector('.input-dock');
  var inputDockMain = document.querySelector('.input-dock-main');
  var chatLoadingStatus = document.getElementById('chat-loading-status');
  var fileUpload = document.getElementById('chat-file-upload');
  var drawer = document.getElementById('chat-drawer');
  var drawerFab = document.getElementById('drawer-fab');
  var drawerClose = document.getElementById('drawer-close');
  var drawerScrim = document.getElementById('drawer-scrim');
  var systemSelect = document.getElementById('chat-system-select');
  var sidebarCurrentSystem = document.getElementById('sidebar-current-system');
  var systemShellStatus = document.getElementById('system-shell-status');
  var guidedDemoBtn = document.getElementById('chat-guided-demo-btn');
  var truthEvalStatus = document.getElementById('truth-eval-status');
  var truthEvalBadge = document.getElementById('truth-eval-badge');
  var truthEvalSummary = document.getElementById('truth-eval-summary');
  var truthEvalActive = document.getElementById('truth-eval-active');
  var truthEvalBlockers = document.getElementById('truth-eval-blockers');
  var canvasTitle = logicDiagram ? logicDiagram.querySelector('h1') : null;
  var DEFAULT_INPUT_PLACEHOLDER = '输入你的控制逻辑问题...';
  var DEFAULT_SEND_TEXT = '发送';
  var LOADING_SEND_TEXT = 'AI 思考中...';
  var lastTruthPayloadBySystem = {};
  var _chatRequestSeq = 0;
  var nodeRefHighlightTimer = null;
    deploy_90_percent_vdt: 'vdt90',
    // Truth-only condition aliases (from controller.py ground truth)
    tls_unlocked: 'tls_unlocked',
    tls_unlocked_ls: 'tls_unlocked',
    reverser_not_deployed_eec: 'reverser_not_deployed_eec',
  };

  // Maps each logic gate to the command node(s) it directly drives.
  // Used to derive intermediate command-node visual state from gate activation state.
  var GATE_TO_COMMAND_MAP = {
    logic1: 'tls115',
    logic2: 'etrac_540v',
    logic3: ['eec_deploy', 'pls_power', 'pdu_motor'],
    logic4: 'thr_lock',
  };

  var NODE_REFERENCE_ALIASES = {
    radio_altitude_ft: 'radio_altitude_ft',
    ra: 'radio_altitude_ft',
    sw1: 'sw1',
    reverser_inhibited: 'reverser_inhibited',
    engine_running: 'engine_running',
    eng: 'engine_running',
    aircraft_on_ground: 'aircraft_on_ground',
    gnd: 'aircraft_on_ground',
    sw2: 'sw2',
    eec_enable: 'eec_enable',
    n1k: 'n1k',
    tra: 'tra_deg',
    tra_deg: 'tra_deg',
    logic1: 'logic1',
    l1: 'logic1',
    tls: 'tls115',
    tls115: 'tls115',
    logic2: 'logic2',
    l2: 'logic2',
    etrac_540v: 'etrac_540v',
    '540v': 'etrac_540v',
    logic3: 'logic3',
    l3: 'logic3',
    eec: 'eec_deploy',
    eec_deploy: 'eec_deploy',
    pls: 'pls_power',
    pls_power: 'pls_power',
    pdu: 'pdu_motor',
    pdu_motor: 'pdu_motor',
    vdt90: 'vdt90',
    logic4: 'logic4',
    l4: 'logic4',
    thr_lock: 'thr_lock',
    thrlock: 'thr_lock',
    // Truth-only nodes
    tls_unlocked: 'tls_unlocked',
    tls_unlocked_ls: 'tls_unlocked',
    reverser_not_deployed_eec: 'reverser_not_deployed_eec',
  };

  var CONNECTION_DEFINITIONS = [
    { from: 'radio_altitude_ft', to: 'logic1', kind: 'conn-input' },
    { from: 'sw1', to: 'logic1', kind: 'conn-input' },
    { from: 'reverser_inhibited', to: 'logic1', kind: 'conn-input' },
    { from: 'logic1', to: 'tls115', kind: 'conn-logic' },
    { from: 'tls115', to: 'logic3', kind: 'conn-merge' },
    { from: 'engine_running', to: 'logic2', kind: 'conn-input' },
    { from: 'aircraft_on_ground', to: 'logic2', kind: 'conn-input' },
    { from: 'sw2', to: 'logic2', kind: 'conn-input' },
    { from: 'eec_enable', to: 'logic2', kind: 'conn-input' },
    { from: 'logic2', to: 'etrac_540v', kind: 'conn-logic' },
    { from: 'etrac_540v', to: 'logic3', kind: 'conn-merge' },
    { from: 'n1k', to: 'logic3', kind: 'conn-input' },
    { from: 'tra_deg', to: 'logic3', kind: 'conn-input' },
    { from: 'logic3', to: 'eec_deploy', kind: 'conn-logic' },
    { from: 'logic3', to: 'pls_power', kind: 'conn-logic' },
    { from: 'logic3', to: 'pdu_motor', kind: 'conn-logic' },
    { from: 'eec_deploy', to: 'vdt90', kind: 'conn-logic' },
    { from: 'vdt90', to: 'logic4', kind: 'conn-logic' },
    { from: 'logic4', to: 'thr_lock', kind: 'conn-final' },
  ];

  var nodeRefPattern = null;

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escapeRegex(str) {
    return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function normalizeNodeKey(nodeId) {
    return String(nodeId || '')
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, '_');
  }

  function normalizeNodeId(nodeId) {
    var normalizedKey = normalizeNodeKey(nodeId);
    return NODE_REFERENCE_ALIASES[normalizedKey] || null;
  }

  function normalizeNodeList(nodeIds) {
    var normalized = [];
    var i;
    var nodeId;

    for (i = 0; i < (nodeIds || []).length; i += 1) {
      nodeId = normalizeNodeId(nodeIds[i]);
      if (nodeId) {
        normalized.push(nodeId);
      }
    }

    return dedupe(normalized);
  }

  function getNodeReferencePattern() {
    var aliasKeys;

    if (nodeRefPattern) {
      return nodeRefPattern;
    }

    aliasKeys = Object.keys(NODE_REFERENCE_ALIASES).sort(function(a, b) {
      return b.length - a.length;
    });
    nodeRefPattern = new RegExp(
      '(^|[^A-Za-z0-9_])(' + aliasKeys.map(escapeRegex).join('|') + ')(?=$|[^A-Za-z0-9_])',
      'gi'
    );
    return nodeRefPattern;
  }

  function renderMessageMarkup(text, role) {
    var rendered = escHtml(text);

    if (role === 'assistant') {
      rendered = rendered.replace(getNodeReferencePattern(), function(match, prefix, token) {
        var nodeId = normalizeNodeId(token);

        if (!nodeId) {
          return match;
        }

        return (
          prefix +
          '<span class="node-ref" data-ref="' + nodeId + '" tabindex="0">' + token + '</span>'
        );
      });
    }

    return rendered.replace(/\n/g, '<br>');
  }

  function getMessageRoleMeta(role) {
    if (role === 'user') {
      return {
        avatar: '👤',
        roleClass: 'user',
        legacyClass: 'chat-message-user',
      };
    }

    if (role === 'system') {
      return {
        avatar: '◆',
        roleClass: 'system',
        legacyClass: 'chat-message-system',
      };
    }

    return {
      avatar: '🤖',
      roleClass: 'assistant',
      legacyClass: 'chat-message-ai',
    };
  }

  function dedupe(list) {
    var seen = {};
    var out = [];
    var i;

    for (i = 0; i < list.length; i += 1) {
      if (!list[i] || seen[list[i]]) {
        continue;
      }
      seen[list[i]] = true;
      out.push(list[i]);
    }

    return out;
  }

  function copyObject(obj) {
    var copy = {};
    var key;

    if (!obj) {
      return copy;
    }

    for (key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        copy[key] = obj[key];
      }
    }

    return copy;
  }

  function buildDefaultLeverPayload(promptText, systemId) {
    return {
      prompt: promptText || '',
      system_id: systemId || 'thrust-reverser',
      tra_deg: 0.0,
      radio_altitude_ft: 5.0,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 35.0,
      max_n1k_deploy_limit: 60.0,
      feedback_mode: 'manual_feedback_override',
      deploy_position_percent: 0.0,
    };
  }

  // Build canonical payload from backend snapshot's input+hud sections (not the request payload).
  // This ensures sw1/sw2/effective_tra values match what the backend actually computed,
  // not what the frontend guessed or requested.
  function buildCanonicalLeverPayloadFromSnapshot(data, fallback) {
    var input = (data && data.input) || {};
    var hud = (data && data.hud) || {};
    return {
      prompt: (fallback && fallback.prompt) || '',
      system_id: (fallback && fallback.system_id) || 'thrust-reverser',
      tra_deg: input.tra_deg !== undefined ? input.tra_deg : fallback.tra_deg,
      radio_altitude_ft: input.radio_altitude_ft !== undefined ? input.radio_altitude_ft : fallback.radio_altitude_ft,
      engine_running: input.engine_running !== undefined ? input.engine_running : fallback.engine_running,
      aircraft_on_ground: input.aircraft_on_ground !== undefined ? input.aircraft_on_ground : fallback.aircraft_on_ground,
      reverser_inhibited: input.reverser_inhibited !== undefined ? input.reverser_inhibited : fallback.reverser_inhibited,
      eec_enable: input.eec_enable !== undefined ? input.eec_enable : fallback.eec_enable,
      n1k: input.n1k !== undefined ? input.n1k : fallback.n1k,
      max_n1k_deploy_limit: input.max_n1k_deploy_limit !== undefined ? input.max_n1k_deploy_limit : fallback.max_n1k_deploy_limit,
      feedback_mode: input.feedback_mode || fallback.feedback_mode,
      deploy_position_percent: hud.deploy_position_percent !== undefined ? hud.deploy_position_percent : fallback.deploy_position_percent,
    };
  }


  function getCurrentTopologyElement() {
    return document.getElementById('chain-topology-' + currentSystem);
  }







  function requestJson(url, options) {
    return fetch(url, options).then(function(r) {
      return r.json().catch(function() {
        return {};
      }).then(function(data) {
        if (!r.ok) {
          throw new Error((data && (data.message || data.error)) || 'request_failed');
        }
        return data;
      });
    });
  }

  function _sendLeverSnapshot(payload) {
    var requestPayload = payload;

    return requestJson('/api/lever-snapshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestPayload),
    }).then(function(data) {
      var canonicalPayload = buildCanonicalLeverPayloadFromSnapshot(data, requestPayload);
      lastTruthPayloadBySystem['thrust-reverser'] = copyObject(canonicalPayload);
      lastTruthSnapshot = data;
      applySnapshotToCanvas(data, requestPayload);
      renderTruthEvalFromSnapshot(data, requestPayload);
    // fault UI removed
      refreshDetailPanel();

      return {
        snapshotData: data,
        requestPayload: requestPayload,
        nodeStates: extractNodeStates(data),
        fallbackText: formatLeverSnapshotAnswer(data, requestPayload),
      };
    });
  }

function _applySuggestedOverrides(overrides) {
    var basePayload = lastTruthPayloadBySystem[currentSystem]
        ? copyObject(lastTruthPayloadBySystem[currentSystem])
        : buildDefaultLeverPayload('', currentSystem);
    var key;
    for (key in overrides) {
      if (Object.prototype.hasOwnProperty.call(overrides, key)) {
        basePayload[key] = overrides[key];
      }
    }

    // Enforce tra_lock: if L4 is not satisfied, clamp TRA to allowed_reverse_min_deg
    // before sending to backend. This mirrors backend logic at demo_server.py:2796.
    if (
      typeof basePayload.tra_deg === 'number' &&
      lastTruthSnapshot &&
      lastTruthSnapshot.tra_lock &&
      lastTruthSnapshot.tra_lock.locked
    ) {
      basePayload.tra_deg = Math.max(
        basePayload.tra_deg,
        lastTruthSnapshot.tra_lock.allowed_reverse_min_deg
      );
    }

    return _sendLeverSnapshot(basePayload);
  }

  function handleOperateResponse(operateResult) {
    var actionType = operateResult.action_type || 'cannot_operate';
    var explanation = operateResult.ai_explanation || operateResult.reasoning || '';
    var overrides = operateResult.parameter_overrides || {};
    var trajectorySteps = operateResult.trajectory_steps || [];
    var gatePlan = operateResult.gate_plan || {};
    var confidence = operateResult.confidence || 0.5;
    var autoApply = operateResult.auto_apply === true;
    var suggestionChip;

    addMessage('ai', explanation);

    if (actionType === 'suggest_parameter_override' && Object.keys(overrides).length > 0) {
      suggestionChip = document.createElement('button');
      suggestionChip.className = 'suggestion-chip';
      suggestionChip.innerHTML = '<span>⚡ 一键应用</span>';
      suggestionChip.title = '参数: ' + JSON.stringify(overrides);
      suggestionChip.addEventListener('click', function() {
        suggestionChip.disabled = true;
        suggestionChip.querySelector('span').textContent = '⏳ 应用中...';
        _applySuggestedOverrides(overrides).then(function() {
          addMessage('ai', '✅ 已应用：' + Object.keys(overrides).join(', '));
          suggestionChip.remove();
        }).catch(function(err) {
          suggestionChip.disabled = false;
          suggestionChip.querySelector('span').textContent = '⚡ 重试';
          addMessage('ai', '⚠️ 应用失败: ' + err.message);
        });
      });
      if (chatMessages) {
        chatMessages.appendChild(suggestionChip);
        scrollChatToBottom();
        suggestionChip.focus();
      }
      // auto_apply: apply immediately without requiring a click
      if (autoApply) {
        suggestionChip.click();
      }
    } else if (actionType === 'manual_steps' && trajectorySteps.length > 0) {
      suggestionChip = document.createElement('button');
      suggestionChip.className = 'suggestion-chip';
      suggestionChip.innerHTML = '<span>📋 查看操作步骤</span>';
      suggestionChip.addEventListener('click', function() {
        suggestionChip.disabled = true;
        suggestionChip.querySelector('span').textContent = '✓ 已展开';
        var stepsText = trajectorySteps.map(function(step, i) {
          return (i + 1) + '. ' + (typeof step === 'object' ? (step.description || JSON.stringify(step)) : step);
        }).join('\n');
        addMessage('ai', '📋 操作步骤：\n' + stepsText);
      });
      if (chatMessages) {
        chatMessages.appendChild(suggestionChip);
        scrollChatToBottom();
      }
    } else if (Object.keys(gatePlan).length > 0) {
      // Display gate_plan returned for "满足L1-L4" type requests
      var gatePlanLines = [];
      var gateId;
      for (gateId in gatePlan) {
        if (Object.prototype.hasOwnProperty.call(gatePlan, gateId)) {
          gatePlanLines.push(gateId + ': ' + (typeof gatePlan[gateId] === 'object' ? JSON.stringify(gatePlan[gateId]) : gatePlan[gateId]));
        }
      }
      if (gatePlanLines.length > 0) {
        addMessage('ai', '🔓 逻辑门依赖项：\n' + gatePlanLines.join('\n'));
      }
    }
    // else: cannot_operate — explanation already shown above; no chip needed
  }

  function addMessage(role, text, highlight) {
    if (!chatMessages) {
      return;
    }

    var roleMeta = getMessageRoleMeta(role);
    var highlightedNodes = [];
    var suggestionNodes = [];
    var msg = document.createElement('article');
    var avatarEl = document.createElement('div');
    var contentEl = document.createElement('div');
    var bodyEl = document.createElement('p');

    if (Array.isArray(highlight)) {
      highlightedNodes = normalizeNodeList(highlight);
    } else if (highlight) {
      highlightedNodes = normalizeNodeList(highlight.highlightedNodes);
      suggestionNodes = normalizeNodeList(highlight.suggestionNodes);
    }

    msg.className = 'chat-message ' + roleMeta.legacyClass + ' ' + roleMeta.roleClass;
    if (highlightedNodes.length > 0) {
      msg.setAttribute('data-highlighted', highlightedNodes.join(','));
    }
    if (suggestionNodes.length > 0) {
      msg.setAttribute('data-suggested', suggestionNodes.join(','));
    }

    avatarEl.className = 'chat-message-avatar';
    avatarEl.textContent = roleMeta.avatar;
    contentEl.className = 'chat-message-content';
    bodyEl.setAttribute('data-raw-text', text);
    bodyEl.innerHTML = renderMessageMarkup(text, roleMeta.roleClass);
    contentEl.appendChild(bodyEl);
    msg.appendChild(avatarEl);
    msg.appendChild(contentEl);
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function setInputLoading(loading) {
    if (!chatInput || !sendBtn) {
      return;
    }

    chatInput.disabled = loading;
    sendBtn.disabled = loading;
    chatInput.placeholder = loading ? LOADING_SEND_TEXT : DEFAULT_INPUT_PLACEHOLDER;
    sendBtn.textContent = loading ? LOADING_SEND_TEXT : DEFAULT_SEND_TEXT;
    sendBtn.classList.toggle('is-loading', loading);
    sendBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
    sendBtn.setAttribute('aria-label', loading ? LOADING_SEND_TEXT : DEFAULT_SEND_TEXT);
    sendBtn.title = loading ? LOADING_SEND_TEXT : DEFAULT_SEND_TEXT;

    if (inputDock) {
      inputDock.classList.toggle('is-loading', loading);
    }
    if (chatLoadingStatus) {
      chatLoadingStatus.textContent = loading ? LOADING_SEND_TEXT : '就绪';
      chatLoadingStatus.classList.toggle('is-loading', loading);
    }
  }

  function finishChatRequest() {
    setInputLoading(false);
    if (chatInput) {
      chatInput.focus();
    }
  }

  function scrollChatToBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function setFabTooltip(text) {
    if (!drawerFab) {
      return;
    }

    drawerFab.title = text;
    drawerFab.setAttribute('data-tooltip-text', text);
  }

  function openDrawer() {
    document.body.classList.add('drawer-open');
    if (drawer) {
      drawer.setAttribute('aria-hidden', 'false');
    }
    if (drawerFab) {
      drawerFab.setAttribute('aria-expanded', 'true');
      drawerFab.setAttribute('aria-label', '收起对话抽屉');
    }
    setFabTooltip('收起对话');
  }

  function closeDrawer() {
    document.body.classList.remove('drawer-open');
    if (drawer) {
      drawer.setAttribute('aria-hidden', 'true');
    }
    if (drawerFab) {
      drawerFab.setAttribute('aria-expanded', 'false');
      drawerFab.setAttribute('aria-label', '打开对话抽屉');
    }
    setFabTooltip('展开对话');
  }

  function toggleDrawer() {
    if (document.body.classList.contains('drawer-open')) {
      closeDrawer();
      return;
    }
    openDrawer();
  }

  function setTruthBadge(mode, text) {
    if (!truthEvalBadge) {
      return;
    }

    truthEvalBadge.className = 'truth-eval-badge';
    truthEvalBadge.classList.add('is-' + mode);
    truthEvalBadge.textContent = text;
  }

  function renderChipList(container, items, className) {
    var html = [];
    var i;

    if (!container) {
      return;
    }

    if (!items || items.length === 0) {
      container.innerHTML = '<span class="truth-chip is-muted">—</span>';
      return;
    }

    for (i = 0; i < items.length; i += 1) {
      html.push(
        '<span class="truth-chip ' + className + '">' + escHtml(String(items[i])) + '</span>'
      );
    }

    container.innerHTML = html.join('');
  }

  function formatSignalValue(value) {
    if (value === null || value === undefined) {
      return '—';
    }
    if (typeof value === 'boolean') {
      return value ? '开' : '关';
    }
    if (typeof value === 'number') {
      if (!isFinite(value)) {
        return '—';
      }
      return value % 1 === 0 ? String(value) : value.toFixed(1);
    }
    return String(value);
  }

  function normalizeBlockedReason(reason) {
    var parts;
    var logicId;
    var conditionId;

    if (!reason) {
      return null;
    }

    parts = String(reason).split(':');
    if (parts.length !== 2) {
      return {
        label: String(reason),
        logicId: null,
        conditionId: String(reason),
      };
    }

    logicId = parts[0];
    conditionId = parts[1];
    return {
      label: logicId + ': ' + conditionId,
      logicId: logicId,
      conditionId: conditionId,
    };
  }

  function extractEvaluation(data) {
    var ev = data && data.truth_evaluation ? data.truth_evaluation : null;
    var activeIds = [];
    var failed = {};
    var blockedReasons = [];
    var componentValues = {};
    var logicKey;
    var logicNode;
    var entries;
    var i;
    var j;
    var normalized;

    if (ev) {
      activeIds = (ev.active_logic_node_ids || []).slice();
      blockedReasons = (ev.blocked_reasons || []).slice();
      if (ev.asserted_component_values) {
        for (logicKey in ev.asserted_component_values) {
          if (Object.prototype.hasOwnProperty.call(ev.asserted_component_values, logicKey)) {
            componentValues[logicKey] = ev.asserted_component_values[logicKey];
          }
        }
      }
    }

    // Also read from nodes array for per-component active/blocked states
    // API returns {nodes: [{id, state, blocked_by}]} where state is 'active'|'inactive'|'blocked'
    if (data && data.nodes && Array.isArray(data.nodes)) {
      for (i = 0; i < data.nodes.length; i += 1) {
        var node = data.nodes[i];
        if (node.state === 'active') {
          activeIds.push(node.id);
        } else if (node.state === 'blocked' && node.blocked_by && node.blocked_by.length > 0) {
          // Mark which logic gate this blocks
          failed[node.id] = node.blocked_by.slice();
        }
      }
    }

    if (data && data.logic) {
      entries = ['logic1', 'logic2', 'logic3', 'logic4'];
      for (i = 0; i < entries.length; i += 1) {
        logicKey = entries[i];
        logicNode = data.logic[logicKey];
        if (!logicNode) {
          continue;
        }

        if (logicNode.active) {
          activeIds.push(logicKey);
        }

        if (logicNode.failed_conditions && logicNode.failed_conditions.length > 0) {
          failed[logicKey] = logicNode.failed_conditions.slice();
        }
      }
    }

    for (j = 0; j < blockedReasons.length; j += 1) {
      normalized = normalizeBlockedReason(blockedReasons[j]);
      if (!normalized || !normalized.logicId || !normalized.conditionId) {
        continue;
      }
      if (!failed[normalized.logicId]) {
        failed[normalized.logicId] = [];
      }
      if (failed[normalized.logicId].indexOf(normalized.conditionId) === -1) {
        failed[normalized.logicId].push(normalized.conditionId);
      }
    }

    return {
      activeIds: dedupe(activeIds),
      failed: failed,
      blockedReasons: blockedReasons,
      componentValues: componentValues,
      completionReached: !!(ev && ev.completion_reached),
      summary:
        (ev && ev.summary) ||
        (data && data.summary && typeof data.summary === 'object'
          ? [data.summary.headline, data.summary.blocker, data.summary.next_step].filter(Boolean).join(' ')
          : (data && typeof data.summary === 'string' ? data.summary : '')),
    };
  }

  function mergePayloadSignals(componentValues, payload) {
    var merged = {};
    var key;
    var fallbackKeys = [
      'radio_altitude_ft',
      'tra_deg',
      'engine_running',
      'aircraft_on_ground',
      'reverser_inhibited',
      'eec_enable',
      'n1k',
      'sw1',
      'sw2',
      'deploy_90_percent_vdt',
      'max_n1k_deploy_limit',
    ];
    var i;

    for (key in componentValues) {
      if (Object.prototype.hasOwnProperty.call(componentValues, key)) {
        merged[key] = componentValues[key];
      }
    }

    if (!payload) {
      return merged;
    }

    for (i = 0; i < fallbackKeys.length; i += 1) {
      key = fallbackKeys[i];
      if (merged[key] === undefined && payload[key] !== undefined) {
        merged[key] = payload[key];
      }
    }

    // Read authoritative sw1/sw2 from hud (backend-computed sensor values),
    // not from guessing via tra_deg threshold.
    if (merged.sw1 === undefined) {
      merged.sw1 = (payload.hud && payload.hud.sw1 !== undefined) ? payload.hud.sw1 : merged.sw1;
    }
    if (merged.sw2 === undefined) {
      merged.sw2 = (payload.hud && payload.hud.sw2 !== undefined) ? payload.hud.sw2 : merged.sw2;
    }
    if (merged.deploy_90_percent_vdt === undefined) {
      merged.deploy_90_percent_vdt = (payload.hud && payload.hud.deploy_90_percent_vdt !== undefined)
        ? payload.hud.deploy_90_percent_vdt
        : (typeof payload.deploy_position_percent === 'number' ? payload.deploy_position_percent >= 90.0 : merged.deploy_90_percent_vdt);
    }
    // Bug fix: deploy_position_percent lives in hud, not in truth_evaluation.componentValues.
    // Without this, the VDT slider always resets to min (0) after Apply because
    // truth_evaluation.asserted_component_values is never populated by the backend.
    if (merged.deploy_position_percent === undefined && payload.hud && typeof payload.hud.deploy_position_percent === 'number') {
      merged.deploy_position_percent = payload.hud.deploy_position_percent;
    }

    return merged;
  }

  function resetCanvasState() {
    var nodes;
    var values;
    var i;

    clearAiHighlights();
    clearNodeReferenceHighlights();
    nodes = document.querySelectorAll('.canvas-wrapper [data-node]');
    values = document.querySelectorAll('.canvas-wrapper [data-value-for]');

    for (i = 0; i < nodes.length; i += 1) {
      nodes[i].classList.remove('is-active', 'is-blocked', 'is-inactive', 'is-faulted');
      nodes[i].classList.add('is-inactive');
      nodes[i].setAttribute('data-state', 'inactive');
      nodes[i].removeAttribute('data-fault-type');
    }

    for (i = 0; i < values.length; i += 1) {
      values[i].textContent = '—';
    }

    updateConnectionStates();
  }

  function setNodeState(nodeId, state) {
    var els;
    var i;

    nodeId = normalizeNodeId(nodeId) || nodeId;
    els = document.querySelectorAll('.canvas-wrapper [data-node="' + nodeId + '"]');
    for (i = 0; i < els.length; i += 1) {
      els[i].classList.remove('is-active', 'is-blocked', 'is-inactive');
      els[i].classList.add('is-' + state);
      els[i].setAttribute('data-state', state);
    }
  }

  function setNodeValue(nodeId, value) {
    nodeId = normalizeNodeId(nodeId) || nodeId;
    var valueKey = NODE_VALUE_KEYS[nodeId] || nodeId;
    var els = document.querySelectorAll('.canvas-wrapper [data-value-for="' + valueKey + '"]');
    var i;

    for (i = 0; i < els.length; i += 1) {
      els[i].textContent = formatSignalValue(value);
    }
  }

// ── P19.4: Causal chain connector layer ────────────────────────────────────

// Create or retrieve the causal chain SVG overlay layer inside .canvas-wrapper
function getCausalChainLayer() {
  var wrapper = document.querySelector('.canvas-wrapper');
  if (!wrapper) return null;
  var existing = document.getElementById('causal-chain-layer');
  if (existing) return existing;

  var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('id', 'causal-chain-layer');
  svg.setAttribute('class', 'causal-chain-layer');
  svg.style.cssText = (
    'position:absolute;top:0;left:0;width:100%;height:100%;' +
    'pointer-events:none;z-index:20;overflow:visible;'
  );

  // Arrowhead marker definition
  var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  var marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
  marker.setAttribute('id', 'causal-arrow');
  marker.setAttribute('markerWidth', '8');
  marker.setAttribute('markerHeight', '6');
  marker.setAttribute('refX', '8');
  marker.setAttribute('refY', '3');
  marker.setAttribute('orient', 'auto');
  var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', 'M0,0 L0,6 L8,3 z');
  path.setAttribute('fill', '#5ba8ff');
  marker.appendChild(path);
  defs.appendChild(marker);
  svg.appendChild(defs);

  wrapper.appendChild(svg);
  return svg;
}

// Draw dashed causal chain connectors between highlighted nodes in sequence order.
function drawCausalChainConnectors(highlightedNodes) {
  var svg = getCausalChainLayer();
  if (!svg) return;

  // Remove existing connector lines
  var existingLines = svg.querySelectorAll('.causal-connector');
  existingLines.forEach(function(l) { l.remove(); });

  if (!Array.isArray(highlightedNodes) || highlightedNodes.length < 2) return;

  // Get bounding boxes of discussed nodes in order
  var nodeIds = highlightedNodes;
  var boxes = [];
  var i;
  for (i = 0; i < nodeIds.length; i++) {
    var els = document.querySelectorAll(
      '.canvas-wrapper [data-node="' + nodeIds[i] + '"]'
    );
    if (els.length === 0) continue;
    var firstEl = els[0];
    var rect = firstEl.getBoundingClientRect();
    var wrapperRect = (
      document.querySelector('.canvas-wrapper') || document.body
    ).getBoundingClientRect();
    boxes.push({
      id: nodeIds[i],
      x: rect.left + rect.width / 2 - wrapperRect.left,
      y: rect.top + rect.height / 2 - wrapperRect.top,
    });
  }

  // Draw connector from each node to the next
  var j;
  for (j = 0; j < boxes.length - 1; j++) {
    var from = boxes[j];
    var to = boxes[j + 1];

    var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('class', 'causal-connector');
    line.setAttribute('x1', String(from.x));
    line.setAttribute('y1', String(from.y));
    line.setAttribute('x2', String(to.x));
    line.setAttribute('y2', String(to.y));
    line.setAttribute('stroke', '#5ba8ff');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-dasharray', '5,3');
    line.setAttribute('marker-end', 'url(#causal-arrow)');
    line.setAttribute('opacity', '0.75');
    svg.appendChild(line);

    // Step label showing causal step number
    if (j < boxes.length - 2) {
      var midX = (from.x + to.x) / 2;
      var midY = (from.y + to.y) / 2 - 8;
      var label = document.createElementNS(
        'http://www.w3.org/2000/svg', 'text'
      );
      label.setAttribute('class', 'causal-connector-label');
      label.setAttribute('x', String(midX));
      label.setAttribute('y', String(midY));
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('fill', '#5ba8ff');
      label.setAttribute('font-size', '10');
      label.setAttribute('font-family', 'monospace');
      label.textContent = String(j + 1);
      svg.appendChild(label);
    }
  }
}

// Remove all causal chain connectors
function clearCausalChainConnectors() {
  var svg = document.getElementById('causal-chain-layer');
  if (!svg) return;
  var connectors = svg.querySelectorAll('.causal-connector, .causal-connector-label');
  connectors.forEach(function(el) { el.remove(); });
}

function clearAiHighlights() {
    var highlightedEls = document.querySelectorAll('.canvas-wrapper .ai-discussed, .canvas-wrapper .ai-suggested');
    var i;

    for (i = 0; i < highlightedEls.length; i += 1) {
      highlightedEls[i].classList.remove('ai-discussed', 'ai-suggested');
    }
    clearCausalChainConnectors();
  }

  function applyAiHighlights(highlightedNodes, suggestionNodes) {
    var discussed = normalizeNodeList(highlightedNodes);
    var suggested = normalizeNodeList(suggestionNodes);
    var i;
    var els;
    var j;

    clearAiHighlights();

    for (i = 0; i < discussed.length; i += 1) {
      els = document.querySelectorAll('.canvas-wrapper [data-node="' + discussed[i] + '"]');
      for (j = 0; j < els.length; j += 1) {
        els[j].classList.add('ai-discussed');
      }
    }

    for (i = 0; i < suggested.length; i += 1) {
      els = document.querySelectorAll('.canvas-wrapper [data-node="' + suggested[i] + '"]');
      for (j = 0; j < els.length; j += 1) {
        els[j].classList.add('ai-suggested');
      }
    }
    drawCausalChainConnectors(discussed);
  }

  function clearNodeReferenceHighlights() {
    var highlightedEls = document.querySelectorAll('.canvas-wrapper .node-ref-target');
    var i;

    if (nodeRefHighlightTimer) {
      window.clearTimeout(nodeRefHighlightTimer);
      nodeRefHighlightTimer = null;
    }

    for (i = 0; i < highlightedEls.length; i += 1) {
      highlightedEls[i].classList.remove('node-ref-target');
    }
  }

  function highlightNodeReference(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var els;
    var i;

    if (!normalizedNodeId) {
      return;
    }

    clearNodeReferenceHighlights();
    els = document.querySelectorAll('.canvas-wrapper [data-node="' + normalizedNodeId + '"]');

    for (i = 0; i < els.length; i += 1) {
      els[i].classList.add('node-ref-target');
    }

    if (els.length > 0) {
      nodeRefHighlightTimer = window.setTimeout(clearNodeReferenceHighlights, 1800);
    }
  }

  function deriveComponentState(value, isBlocked) {
    if (isBlocked) {
      return 'blocked';
    }
    if (typeof value === 'boolean') {
      return value ? 'active' : 'inactive';
    }
    if (value === null || value === undefined || value === '') {
      return 'inactive';
    }
    return 'active';
  }

  function flattenFailedReasons(failed) {
    var items = [];
    var logicId;
    var conditions;
    var i;

    for (logicId in failed) {
      if (!Object.prototype.hasOwnProperty.call(failed, logicId)) {
        continue;
      }
      conditions = failed[logicId] || [];
      for (i = 0; i < conditions.length; i += 1) {
        items.push(logicId + ': ' + conditions[i]);
      }
    }

    return items;
  }

  function renderTruthEvalFromSnapshot(data, payload) {
    var extracted = extractEvaluation(data);
    var activeIds = extracted.activeIds;
    var blockerLabels = [];
    var i;
    var normalized;

    if (truthEvalStatus) {
      if (extracted.completionReached) {
        truthEvalStatus.textContent = '链路完成';
      } else if ((extracted.blockedReasons || []).length > 0 || Object.keys(extracted.failed).length > 0) {
        truthEvalStatus.textContent = '链路阻塞';
      } else if (activeIds.length > 0) {
        truthEvalStatus.textContent = '链路激活';
      } else {
        truthEvalStatus.textContent = '等待快照';
      }
    }

    if (extracted.completionReached) {
      setTruthBadge('success', '完成');
    } else if ((extracted.blockedReasons || []).length > 0 || Object.keys(extracted.failed).length > 0) {
      setTruthBadge('danger', '阻塞');
    } else if (activeIds.length > 0) {
      setTruthBadge('live', '激活');
    } else {
      setTruthBadge('idle', '空闲');
    }

    if (truthEvalSummary) {
      if (extracted.summary) {
        truthEvalSummary.textContent = extracted.summary;
      } else if (payload) {
        truthEvalSummary.textContent =
          'TRA=' + payload.tra_deg + '° / RA=' + payload.radio_altitude_ft +
          'ft / 反馈模式=' + payload.feedback_mode + '。';
      } else {
        truthEvalSummary.textContent = '等待新的快照。';
      }
    }

    renderChipList(truthEvalActive, activeIds, 'is-active');

    if (extracted.blockedReasons && extracted.blockedReasons.length > 0) {
      for (i = 0; i < extracted.blockedReasons.length; i += 1) {
        normalized = normalizeBlockedReason(extracted.blockedReasons[i]);
        blockerLabels.push(normalized ? normalized.label : String(extracted.blockedReasons[i]));
      }
    } else {
      blockerLabels = flattenFailedReasons(extracted.failed);
    }

    renderChipList(truthEvalBlockers, blockerLabels, 'is-blocked');
  }

  function renderTruthEvalFromDemo(data) {
    var answer = formatDemoAnswer(data);

    if (truthEvalStatus) {
      truthEvalStatus.textContent = (SYSTEM_LABELS[currentSystem] || currentSystem) + ' 已路由';
    }
    setTruthBadge('live', '已路由');

    if (truthEvalSummary) {
      truthEvalSummary.textContent =
        '当前画布继续显示参考反推链路；本次问题已按所选系统路由。' +
        answer;
    }

    renderChipList(truthEvalActive, [SYSTEM_LABELS[currentSystem] || currentSystem], 'is-active');
    renderChipList(truthEvalBlockers, ['仅显示参考画布'], 'is-muted');
  }

  function extractNodeStates(snapshotData) {
    var nodeStates = {};
    var truthEvaluation = snapshotData && snapshotData.truth_evaluation ? snapshotData.truth_evaluation : null;
    var activeLogicNodeIds = {};
    var logicNodeIds = {};
    var nodes = snapshotData && Array.isArray(snapshotData.nodes) ? snapshotData.nodes : [];
    var logicNodes = snapshotData && snapshotData.spec && Array.isArray(snapshotData.spec.logic_nodes)
      ? snapshotData.spec.logic_nodes
      : [];
    var hasBlockedReasons = !!(
      truthEvaluation &&
      Array.isArray(truthEvaluation.blocked_reasons) &&
      truthEvaluation.blocked_reasons.length > 0
    );
    var i;
    var nodeId;
    var state;

    if (truthEvaluation && Array.isArray(truthEvaluation.active_logic_node_ids)) {
      for (i = 0; i < truthEvaluation.active_logic_node_ids.length; i += 1) {
        nodeId = normalizeNodeId(truthEvaluation.active_logic_node_ids[i]) || truthEvaluation.active_logic_node_ids[i];
        activeLogicNodeIds[nodeId] = true;
      }
    }

    for (i = 0; i < logicNodes.length; i += 1) {
      if (logicNodes[i] && logicNodes[i].id) {
        nodeId = normalizeNodeId(logicNodes[i].id) || logicNodes[i].id;
        logicNodeIds[nodeId] = true;
      }
    }

    for (i = 0; i < nodes.length; i += 1) {
      if (!nodes[i] || !nodes[i].id) {
        continue;
      }
      nodeId = normalizeNodeId(nodes[i].id) || nodes[i].id;
      state = nodes[i].state || 'inactive';
      if (activeLogicNodeIds[nodeId]) {
        state = 'active';
      } else if (logicNodeIds[nodeId] && state !== 'blocked' && hasBlockedReasons) {
        state = 'blocked';
      }
      nodeStates[nodeId] = state;
    }

    for (nodeId in activeLogicNodeIds) {
      if (Object.prototype.hasOwnProperty.call(activeLogicNodeIds, nodeId) && !nodeStates[nodeId]) {
        nodeStates[nodeId] = 'active';
      }
    }

    return nodeStates;
  }

  function applySystemSnapshotToCanvas(snapshotData) {
    var truthEvaluation = snapshotData && snapshotData.truth_evaluation ? snapshotData.truth_evaluation : null;
    var componentValues = truthEvaluation && truthEvaluation.asserted_component_values
      ? truthEvaluation.asserted_component_values
      : {};
    var nodeStates = extractNodeStates(snapshotData);
    var nodes = document.querySelectorAll('.canvas-wrapper [data-node]');
    var i;
    var nodeId;
    var valueKey;
    var value;

    resetCanvasState();

    for (i = 0; i < nodes.length; i += 1) {
      nodeId = nodes[i].getAttribute('data-node');
      if (!nodeId) {
        continue;
      }
      setNodeState(nodeId, nodeStates[nodeId] || 'inactive');
      valueKey = NODE_VALUE_KEYS[nodeId] || nodeId;
      value = componentValues[valueKey];
      if (value === undefined) {
        value = componentValues[nodeId];
      }
      if (value !== undefined) {
        setNodeValue(nodeId, value);
      }
    }

    updateConnectionStates();
  }

  function applySnapshotToCanvas(data, payload) {
    var extracted = extractEvaluation(data);
    var componentValues = mergePayloadSignals(extracted.componentValues, payload);
    var nodeIds = [
      'radio_altitude_ft',
      'sw1',
      'reverser_inhibited',
      'engine_running',
      'aircraft_on_ground',
      'sw2',
      'eec_enable',
      'n1k',
      'tra_deg',
      'logic1',
      'tls115',
      'logic2',
      'etrac_540v',
      'logic3',
      'eec_deploy',
      'pls_power',
      'pdu_motor',
      'vdt90',
      'logic4',
      'thr_lock',
    ];
    var i;
    var nodeId;
    var valueKey;
    var value;

    resetCanvasState();

    // Build authoritative state map directly from backend's data.nodes[].
    // The backend returns {id, state: 'active'|'inactive'|'blocked'} for all 14 nodes.
    // This is the ground truth — use it instead of deriving from truth_evaluation which
    // has empty active_logic_node_ids for lever-snapshot.
    var nodeStateMap = {};
    if (data && data.nodes && Array.isArray(data.nodes)) {
      for (i = 0; i < data.nodes.length; i += 1) {
        nodeStateMap[data.nodes[i].id] = data.nodes[i].state || 'inactive';
      }
    }

    // Build authoritative value map from data.nodes[] (backend-reported values).
    // Used for setNodeValue() display of numeric sensor/command values.
    var nodeValueMap = {};
    if (data && data.nodes && Array.isArray(data.nodes)) {
      for (i = 0; i < data.nodes.length; i += 1) {
        if (data.nodes[i].value !== undefined) {
          nodeValueMap[data.nodes[i].id] = data.nodes[i].value;
        }
      }
    }

    // ── Authoritative state application ─────────────────────────────────────
    // The backend's data.nodes[] array is the single source of truth for ALL
    // node states (active / inactive / blocked). Apply them directly — no
    // derivation, no deriveComponentState(), no GATE_TO_COMMAND_MAP inference.
    // This fixes the critical bug where intermediate nodes (tls115, etrac_540v,
    // vdt90, thr_lock) always appeared inactive because their .value was
    // undefined → deriveComponentState(undefined) returned 'inactive'.
    for (i = 0; i < nodeIds.length; i += 1) {
      nodeId = nodeIds[i];
      // Apply authoritative state from backend's data.nodes[].
      setNodeState(nodeId, nodeStateMap[nodeId] || 'inactive');
      // For input/sensor nodes that carry numeric values, propagate display value.
      // Skip logic gate nodes and intermediate output nodes (no numeric display).
      // Special case: vdt90's deploy_position_percent lives in lastTruthPayloadBySystem
      // (not in truth_evaluation.asserted_component_values which is empty for lever-snapshot).
      if (nodeId === 'vdt90') {
        var vdtPayload = lastTruthPayloadBySystem[currentSystem];
        if (vdtPayload && vdtPayload.deploy_position_percent !== undefined) {
          setNodeValue(nodeId, vdtPayload.deploy_position_percent);
        }
      } else if (!/^logic\d+$/.test(nodeId) && nodeId !== 'tls115' && nodeId !== 'etrac_540v' && nodeId !== 'thr_lock') {
        valueKey = NODE_VALUE_KEYS[nodeId] || nodeId;
        value = nodeValueMap[nodeId] !== undefined ? nodeValueMap[nodeId] : componentValues[valueKey];
        if (value !== undefined) {
          setNodeValue(nodeId, value);
        }
      }
    }

    updateConnectionStates();
  }

  function bootstrapConnectionMetadata() {
    var lines = document.querySelectorAll('.canvas-wrapper .conn-line');
    var i;
    var def;

    for (i = 0; i < lines.length; i += 1) {
      def = CONNECTION_DEFINITIONS[i];
      if (!def) {
        continue;
      }

      lines[i].setAttribute('data-conn-from', def.from);
      lines[i].setAttribute('data-conn-to', def.to);
      if (def.kind && !lines[i].classList.contains(def.kind)) {
        lines[i].classList.add(def.kind);
      }
    }
  }

  function getRenderedNodeState(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId) || nodeId;
    var el = document.querySelector('.canvas-wrapper [data-node="' + normalizedNodeId + '"]');

    if (!el) {
      return 'inactive';
    }

    return el.getAttribute('data-state') || 'inactive';
  }

  function deriveConnectionState(fromState, toState) {
    if (fromState === 'blocked' || toState === 'blocked') {
      return 'blocked';
    }
    if (fromState === 'active' && toState === 'active') {
      return 'active';
    }
    return 'inactive';
  }

  function updateConnectionStates() {
    var lines = document.querySelectorAll('.canvas-wrapper .conn-line[data-conn-from][data-conn-to]');
    var i;
    var fromState;
    var toState;
    var state;

    for (i = 0; i < lines.length; i += 1) {
      fromState = getRenderedNodeState(lines[i].getAttribute('data-conn-from'));
      toState = getRenderedNodeState(lines[i].getAttribute('data-conn-to'));
      state = deriveConnectionState(fromState, toState);
      lines[i].classList.remove('is-active', 'is-blocked', 'is-inactive');
      lines[i].classList.add('is-' + state);
    }
  }

  function resolveNodeAnchor(nodeId, fallbackTarget) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var topology = getCurrentTopologyElement();
    var anchor = null;

    if (!normalizedNodeId || !topology) {
      return null;
    }

    if (fallbackTarget && fallbackTarget.closest) {
      anchor = fallbackTarget.closest('[data-node="' + normalizedNodeId + '"]');
      if (!anchor) {
        anchor = fallbackTarget.closest('[data-node-label="' + normalizedNodeId + '"]');
      }
    }

    if (!anchor || !anchor.hasAttribute || !anchor.hasAttribute('data-node')) {
      anchor = topology.querySelector('[data-node="' + normalizedNodeId + '"]') || anchor;
    }

    return anchor || null;
  }

  function positionFloatingButton(buttonEl, anchorEl) {
    var stageRect;
    var anchorRect;
    var halfWidth;
    var halfHeight;
    var nextLeft;
    var nextTop;

    if (!buttonEl || !anchorEl || !canvasStage) {
      return;
    }

    stageRect = canvasStage.getBoundingClientRect();
    anchorRect = anchorEl.getBoundingClientRect();
    halfWidth = (buttonEl.offsetWidth || 34) / 2;
    halfHeight = (buttonEl.offsetHeight || 34) / 2;
    nextLeft = anchorRect.right - stageRect.left + 8;
    nextTop = anchorRect.top - stageRect.top + 8;
    nextLeft = Math.max(halfWidth + 10, Math.min(nextLeft, stageRect.width - halfWidth - 10));
    nextTop = Math.max(halfHeight + 10, Math.min(nextTop, stageRect.height - halfHeight - 10));
    buttonEl.style.left = nextLeft + 'px';
    buttonEl.style.top = nextTop + 'px';
  }

  function positionFloatingMenu(menuEl, anchorEl) {
    var stageRect;
    var anchorRect;
    var menuWidth;
    var menuHeight;
    var nextLeft;
    var nextTop;

    if (!menuEl || !anchorEl || !canvasStage) {
      return;
    }

    stageRect = canvasStage.getBoundingClientRect();
    anchorRect = anchorEl.getBoundingClientRect();
    menuWidth = menuEl.offsetWidth || 190;
    menuHeight = menuEl.offsetHeight || 140;
    nextLeft = anchorRect.right - stageRect.left + 14;
    nextTop = anchorRect.top - stageRect.top - 4;

    if (nextLeft + menuWidth > stageRect.width - 12) {
      nextLeft = anchorRect.left - stageRect.left - menuWidth - 14;
    }
    if (nextLeft < 12) {
      nextLeft = 12;
    }
    if (nextTop + menuHeight > stageRect.height - 12) {
      nextTop = stageRect.height - menuHeight - 12;
    }
    if (nextTop < 12) {
      nextTop = 12;
    }

    menuEl.style.left = nextLeft + 'px';
    menuEl.style.top = nextTop + 'px';
  }


















  function hydrateExistingMessages() {
    var messages = document.querySelectorAll('.chat-message');
    var i;
    var roleMeta;
    var bodyEl;
    var rawText;

    for (i = 0; i < messages.length; i += 1) {
      if (messages[i].classList.contains('chat-message-user')) {
        roleMeta = getMessageRoleMeta('user');
      } else if (messages[i].classList.contains('chat-message-system')) {
        roleMeta = getMessageRoleMeta('system');
      } else {
        roleMeta = getMessageRoleMeta('ai');
      }

      messages[i].classList.add(roleMeta.roleClass, roleMeta.legacyClass);
      bodyEl = messages[i].querySelector('.chat-message-content p');
      if (!bodyEl) {
        continue;
      }

      rawText = bodyEl.getAttribute('data-raw-text') || bodyEl.textContent || '';
      bodyEl.setAttribute('data-raw-text', rawText);
      bodyEl.innerHTML = renderMessageMarkup(rawText, roleMeta.roleClass);
    }
  }

  function syncSystemChrome() {
    var label = SYSTEM_LABELS[currentSystem] || currentSystem;

    if (sidebarCurrentSystem) {
      sidebarCurrentSystem.textContent = label;
    }
    if (systemShellStatus) {
      systemShellStatus.textContent = label;
    }
    if (canvasTitle) {
      canvasTitle.textContent = label + '链路';
    }
  }

  function resetTruthEvalBar() {
    if (truthEvalStatus) {
      truthEvalStatus.textContent = '等待快照';
    }
    setTruthBadge('idle', '空闲');
    if (truthEvalSummary) {
      if (currentSystem === 'thrust-reverser') {
        truthEvalSummary.textContent =
          '选择系统并发送问题，返回的真值评估会在这里汇总为激活、阻塞、完成三个信号面。';
      } else {
        truthEvalSummary.textContent =
          '当前画布保持参考反推链路；问题会继续按所选系统路由到对应适配器。';
      }
    }
    if (truthEvalActive) {
      truthEvalActive.innerHTML = '<span class="truth-chip is-muted">—</span>';
    }
    if (truthEvalBlockers) {
      truthEvalBlockers.innerHTML = '<span class="truth-chip is-muted">—</span>';
    }
  }

  /* ── Zoom & Pan Functions ── */
  function clampPan(x, y, zoom) {
    if (!zoomContainer) return { x: 0, y: 0 };
    var rect = zoomContainer.getBoundingClientRect();
    var scaledW = rect.width * zoom;
    var scaledH = rect.height * zoom;
    var maxX = Math.max(0, (scaledW - rect.width) / 2);
    var maxY = Math.max(0, (scaledH - rect.height) / 2);
    return {
      x: Math.max(-maxX, Math.min(maxX, x)),
      y: Math.max(-maxY, Math.min(maxY, y)),
    };
  }

  function applyZoomTransform() {
    if (!zoomContainer) return;
    var clamped = clampPan(panX, panY, currentZoom);
    panX = clamped.x;
    panY = clamped.y;
    zoomContainer.style.transform = 'translate(' + panX + 'px, ' + panY + 'px) scale(' + currentZoom + ')';
    if (zoomLevelEl) {
      zoomLevelEl.textContent = Math.round(currentZoom * 100) + '%';
    }
  }

  function resetZoom() {
    currentZoom = 1.0;
    panX = 0;
    panY = 0;
    applyZoomTransform();
  }

  function onWheelZoom(e) {
    e.preventDefault();
    var delta = e.deltaY || e.detail || 0;
    var zoomFactor = delta > 0 ? 0.92 : 1.08;
    var newZoom = Math.min(2.0, Math.max(0.5, currentZoom * zoomFactor));
    if (newZoom !== currentZoom) {
      var rect = zoomContainer.getBoundingClientRect();
      var mouseX = e.clientX - rect.left - rect.width / 2;
      var mouseY = e.clientY - rect.top - rect.height / 2;
      var scaleDiff = newZoom - currentZoom;
      panX -= (mouseX - panX) * (scaleDiff / currentZoom);
      panY -= (mouseY - panY) * (scaleDiff / currentZoom);
      currentZoom = newZoom;
      applyZoomTransform();
    }
  }

  function onPanStart(e) {
    if (e.button !== 0) return;
    isPanning = true;
    wasPanning = false;
    panStartX = e.clientX - panX;
    panStartY = e.clientY - panY;
    e.preventDefault();
  }

  function onPanMove(e) {
    if (!isPanning) return;
    var dx = e.clientX - panStartX;
    var dy = e.clientY - panStartY;
    if (Math.sqrt(dx * dx + dy * dy) > 5) {
      wasPanning = true;
    }
    panX = e.clientX - panStartX;
    panY = e.clientY - panStartY;
    applyZoomTransform();
  }

  function onPanEnd() {
    isPanning = false;
    // wasPanning stays true until next click is processed
  }

  /* ── Node Detail Panel Functions ── */
  function showDetailPanel(nodeId) {
    var panel = document.getElementById('node-detail-panel');
    var stage = document.querySelector('.canvas-stage');
    if (!panel || !stage) return;
    // fault UI removed
    currentDetailNodeId = nodeId;
    stage.classList.add('panel-open');
    panel.hidden = false;
    renderDetailPanelContent(nodeId);
  }

  function hideDetailPanel() {
    var panel = document.getElementById('node-detail-panel');
    var stage = document.querySelector('.canvas-stage');
    if (!panel || !stage) return;
    stage.classList.remove('panel-open');
    panel.hidden = true;
    currentDetailNodeId = null;
  }

  function renderDetailPanelContent(nodeId) {
    var idEl = document.getElementById('ndp-node-id');
    var badgeEl = document.getElementById('ndp-state-badge');
    var descEl = document.getElementById('ndp-description');
    var conditionsEl = document.getElementById('ndp-conditions');

    if (!idEl) return;

    idEl.textContent = nodeId || '—';

    var nodeState = 'inactive';
    var nodeDesc = '节点描述不可用';
    var conditions = [];

    if (lastTruthSnapshot) {
      var snapshot = lastTruthSnapshot;
      var nodes = snapshot.nodes || [];
      nodes.forEach(function(n) {
        if (n.id === nodeId) {
          nodeState = n.state || 'inactive';
          nodeDesc = n.description || n.tooltip || n.label || nodeDesc;
        }
      });
      var logic = snapshot.logic || {};
      Object.keys(logic).forEach(function(logicId) {
        var logicNode = logic[logicId];
        if (logicNode.node_id === nodeId || logicId === nodeId) {
          // Use logic.conditions array (backend returns {name, passed, current_value, comparison, threshold_value})
          // This replaces the non-existent failed_conditions/passed_conditions fields
          if (logicNode.conditions && logicNode.conditions.length) {
            logicNode.conditions.forEach(function(cond) {
              conditions.push({
                name: cond.name,
                passed: !!cond.passed,
                current_value: cond.current_value,
                comparison: cond.comparison,
                threshold_value: cond.threshold_value,
              });
            });
          } else {
            // Fallback: legacy failed_conditions field (array of strings)
            if (logicNode.failed_conditions && logicNode.failed_conditions.length) {
              logicNode.failed_conditions.forEach(function(cond) {
                conditions.push({ name: cond, passed: false, value: null });
              });
            }
          }
        }
      });
    }

    badgeEl.className = 'ndp-state-badge';
    if (nodeState === 'active') {
      badgeEl.classList.add('is-active');
      badgeEl.textContent = '激活';
    } else if (nodeState === 'blocked') {
      badgeEl.classList.add('is-blocked');
      badgeEl.textContent = '阻塞';
    } else {
      badgeEl.classList.add('is-inactive');
      badgeEl.textContent = '未激活';
    }

    if (descEl) descEl.textContent = nodeDesc;

    if (conditionsEl) {
      conditionsEl.innerHTML = '';
      if (conditions.length === 0) {
        conditionsEl.innerHTML = '<li class="ndp-condition-item"><span class="ndp-condition-name" style="color:var(--text-dim)">无可用条件</span></li>';
      } else {
        conditions.forEach(function(c) {
          var li = document.createElement('li');
          li.className = 'ndp-condition-item';
          // Show condition name + comparison logic (current_value comparison threshold_value)
          var meta = '';
          if (c.current_value !== undefined && c.comparison !== undefined && c.threshold_value !== undefined) {
            meta = escHtml(String(c.current_value) + ' ' + c.comparison + ' ' + String(c.threshold_value));
          }
          li.innerHTML =
            '<span class="ndp-condition-name">' + escHtml(c.name) + '</span>' +
            (meta ? '<span class="ndp-condition-meta">' + meta + '</span>' : '') +
            '<span class="' + (c.passed ? 'ndp-condition-pass' : 'ndp-condition-fail') + '"></span>';
          conditionsEl.appendChild(li);
        });
      }
    }


    // ── Parameter Adjustment Section ─────────────────────────────────
    var adjustSection = document.getElementById('ndp-adjust-section');
    var adjustParamRow = document.getElementById('ndp-adjust-param-row');
    if (adjustSection && adjustParamRow) {
      // Node IDs that map to an adjustable lever parameter
      var ADJUSTABLE_NODES = {
        radio_altitude_ft: { type: 'float', label: '无线电高度', unit: 'ft',
          min: 0, max: 20, step: 1, key: 'radio_altitude_ft' },
        engine_running:     { type: 'bool', label: '发动机运转', unit: null, key: 'engine_running' },
        aircraft_on_ground: { type: 'bool', label: '飞机在地面', unit: null, key: 'aircraft_on_ground' },
        reverser_inhibited: { type: 'bool', label: '反推抑制', unit: null, key: 'reverser_inhibited' },
        eec_enable:         { type: 'bool', label: 'EEC 使能', unit: null, key: 'eec_enable' },
        n1k:                { type: 'float', label: 'N1 转速', unit: '%',
          min: 0, max: 120, step: 1, key: 'n1k' },
        tra_deg:            { type: 'float', label: 'TRA 角度', unit: '°',
          min: -32, max: 0, step: 0.1, key: 'tra_deg' },
        vdt90:               { type: 'float', label: 'VDT 部署位置', unit: '%',
          min: 0, max: 100, step: 1, key: 'deploy_position_percent' },
      };

      var cfg = ADJUSTABLE_NODES[nodeId];
      adjustSection.hidden = false;
      if (cfg) {
        adjustParamRow.innerHTML = '';

        var currentVal = null;
        // For deploy_position_percent (VDT): read directly from lastTruthPayloadBySystem
        // since truth_evaluation.asserted_component_values is empty for lever-snapshot.
        // buildCanonicalLeverPayloadFromSnapshot stores the correct value from hud.
        var payload = lastTruthPayloadBySystem[currentSystem] || {};
        if (payload[cfg.key] !== undefined) {
          currentVal = parseFloat(payload[cfg.key]);
        } else if (lastTruthSnapshot) {
          // Fallback to mergePayloadSignals for other float/bool params
          var extracted = extractEvaluation(lastTruthSnapshot);
          var comp = mergePayloadSignals(extracted.componentValues, payload);
          var valueKey = cfg.key;
          if (cfg.type === 'bool' && comp[valueKey] === undefined) {
            var floatVal = parseFloat(comp[valueKey]);
            if (!isNaN(floatVal)) currentVal = floatVal > 0.5;
          } else if (cfg.type === 'float') {
            currentVal = parseFloat(comp[valueKey]);
          } else {
            currentVal = comp[valueKey];
          }
        }
        if (currentVal === null || currentVal === undefined || isNaN(currentVal)) {
          currentVal = cfg.type === 'float' ? cfg.min : 0;
        }

        if (cfg.type === 'bool') {
          // Toggle switch row
          var isOn = !!(currentVal === true || currentVal === 1 || currentVal === '1');
          var toggleId = 'ndp-toggle-' + nodeId;
          var row = document.createElement('div');
          row.className = 'ndp-param-toggle';
          row.innerHTML =
            '<span class="ndp-param-label">' + escHtml(cfg.label) + '</span>' +
            '<div class="ndp-toggle-switch" id="' + toggleId + '" data-param="' + cfg.key + '">' +
              '<input type="checkbox" class="ndp-toggle-input" ' + (isOn ? 'checked' : '') + '>' +
              '<span class="ndp-toggle-track"><span class="ndp-toggle-thumb"></span></span>' +
            '</div>';
          adjustParamRow.appendChild(row);
          // Immediately toggle the hidden checkbox when the track is clicked (CSS-only
          // toggle relies on :checked which doesn't update until the browser processes
          // the click on the hidden input — JS toggle ensures the input state is current
          // and the visual state reflects it immediately.
          var toggleTrack = row.querySelector('.ndp-toggle-track');
          if (toggleTrack) {
            toggleTrack.addEventListener('click', function() {
              var cb = row.querySelector('.ndp-toggle-input');
              if (cb) cb.checked = !cb.checked;
            });
          }
        } else {
          // Slider row
          if (isNaN(currentVal)) currentVal = cfg.min;
          var sliderId = 'ndp-slider-' + nodeId;
          var displayVal = (cfg.step < 1) ? currentVal.toFixed(1) : currentVal;
          var effectiveMin = cfg.min;
          var lockHint = '';
          // For TRA slider: respect backend tra_lock constraint (allowed_reverse_min_deg).
          // When locked, TRA cannot go below allowed_reverse_min_deg until L4 activates.
          if (nodeId === 'tra_deg' && lastTruthSnapshot && lastTruthSnapshot.tra_lock) {
            var traLock = lastTruthSnapshot.tra_lock;
            if (traLock.locked) {
              effectiveMin = traLock.allowed_reverse_min_deg;
              lockHint = '<span class="ndp-param-hint" style="color:var(--warning)">🔒 L4 未满足，TRA 最低只能到 ' + effectiveMin.toFixed(1) + '°；需先满足 L4 条件</span>';
            }
          }
          var hintHtml = cfg.key === 'deploy_position_percent'
            ? '<span class="ndp-param-hint">auto_scrubber 由 plant 物理仿真驱动；manual_feedback_override 可快速推到 90%</span>'
            : (lockHint || '');
          var row = document.createElement('div');
          row.className = 'ndp-param-slider';
          row.innerHTML =
            '<div class="ndp-slider-header">' +
              '<div>' +
                '<span class="ndp-param-label">' + escHtml(cfg.label) + '</span>' +
                hintHtml +
              '</div>' +
              '<span class="ndp-param-value" id="' + sliderId + '-val">' + displayVal + (cfg.unit ? cfg.unit : '') + '</span>' +
            '</div>' +
            '<input type="range" class="ndp-range" id="' + sliderId + '" ' +
              'data-param="' + cfg.key + '" ' +
              'min="' + effectiveMin + '" max="' + cfg.max + '" step="' + cfg.step + '" ' +
              'value="' + currentVal + '">' +
            '<div class="ndp-range-labels">' +
              '<span>' + effectiveMin + (cfg.unit ? cfg.unit : '') + '</span>' +
              '<span>' + cfg.max + (cfg.unit ? cfg.unit : '') + '</span>' +
            '</div>';
          adjustParamRow.appendChild(row);
          // Live value update on range input
          var rangeEl = row.querySelector('input[type="range"]');
          var valEl = row.querySelector('.ndp-param-value');
          if (rangeEl && valEl) {
            rangeEl.addEventListener('input', function() {
              var v = parseFloat(this.value);
              var shown = (cfg.step < 1) ? v.toFixed(1) : v;
              valEl.textContent = shown + (cfg.unit ? cfg.unit : '');
            });
          }
        }
      } else {
        // No node-specific param — but keep section visible for global params
        adjustParamRow.innerHTML = '';
      }
    }
  }

  function refreshDetailPanel() {
    if (currentDetailNodeId) {
      renderDetailPanelContent(currentDetailNodeId);
    }
  }

  // ── Canvas Global Controls (always-visible floating widget) ─────────────
  function initCanvasGlobalControls() {
    var payload = lastTruthPayloadBySystem[currentSystem] || {};
    var extracted = lastTruthSnapshot ? extractEvaluation(lastTruthSnapshot) : { componentValues: {} };
    var comp = mergePayloadSignals(extracted.componentValues, payload);

    // feedback_mode: top-level string in payload
    var fbMode = payload.feedback_mode || 'manual_feedback_override';
    var fbSelect = document.getElementById('cgc-feedback-mode');
    if (fbSelect) {
      fbSelect.value = fbMode;
    }

    // max_n1k_deploy_limit: fallback to payload root
    var n1kLimit = (comp.max_n1k_deploy_limit !== undefined)
      ? parseFloat(comp.max_n1k_deploy_limit)
      : (payload.max_n1k_deploy_limit !== undefined ? parseFloat(payload.max_n1k_deploy_limit) : 60.0);
    if (isNaN(n1kLimit)) n1kLimit = 60.0;

    var n1kSlider = document.getElementById('cgc-n1k-limit');
    var n1kVal = document.getElementById('cgc-n1k-limit-val');
    if (n1kSlider) {
      n1kSlider.value = n1kLimit;
    }
    if (n1kVal) {
      n1kVal.textContent = n1kLimit.toFixed(1) + '%';
    }

    // Live value update for the N1K limit slider
    if (n1kSlider && n1kVal) {
      n1kSlider.oninput = function() {
        var v = parseFloat(this.value);
        n1kVal.textContent = v.toFixed(1) + '%';
      };
    }
  }

  function initZoomAndPanel() {
    zoomContainer = document.getElementById('zoom-container');
    zoomLevelEl = document.getElementById('canvas-zoom-level');
    var resetBtn = document.getElementById('canvas-zoom-reset');
    var stage = document.querySelector('.canvas-stage');
    var panel = document.getElementById('node-detail-panel');
    var ndpClose = document.getElementById('ndp-close');

    if (zoomContainer) {
      zoomContainer.addEventListener('wheel', onWheelZoom, { passive: false });
      zoomContainer.addEventListener('mousedown', onPanStart);
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', resetZoom);
    }
    if (stage) {
      stage.addEventListener('mousemove', onPanMove);
      stage.addEventListener('mouseup', onPanEnd);
      stage.addEventListener('mouseleave', onPanEnd);
      stage.addEventListener('click', function(e) {
        if (wasPanning) { wasPanning = false; return; }
        var nodeEl = e.target.closest('[data-node]');
    // fault UI removed
          var nodeId = nodeEl.getAttribute('data-node');
          if (currentDetailNodeId === nodeId) {
            hideDetailPanel();
          } else {
            showDetailPanel(nodeId);
          }
        }
      });
    }
    if (ndpClose) {
      ndpClose.addEventListener('click', hideDetailPanel);
    }

    // ── Canvas Global Controls init (always-visible floating widget) ────
    initCanvasGlobalControls();

    if (panel) {
      panel.addEventListener('click', function(e) {
        if (e.target === panel) hideDetailPanel();
      });
    }
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && currentDetailNodeId) {
        hideDetailPanel();
      }
    });

    // ── Parameter Adjustment Buttons ─────────────────────────────────
    var applyBtn = document.getElementById('ndp-apply-btn');
    var cancelBtn = document.getElementById('ndp-cancel-btn');

    if (applyBtn) {
      applyBtn.addEventListener('click', function() {
        var overrides = {};
        // Collect all slider values
        document.querySelectorAll('input[type="range"].ndp-range').forEach(function(slider) {
          var param = slider.getAttribute('data-param');
          if (param) overrides[param] = parseFloat(slider.value);
        });
        // Collect all toggle states
        document.querySelectorAll('.ndp-toggle-switch .ndp-toggle-input').forEach(function(toggle) {
          var param = toggle.closest('.ndp-toggle-switch').getAttribute('data-param');
          if (param) overrides[param] = toggle.checked;
        });
        // feedback_mode and max_n1k_deploy_limit are now in canvas-global-controls
        var fbSelect = document.getElementById('cgc-feedback-mode');
        if (fbSelect) {
          var param = fbSelect.getAttribute('data-param');
          if (param) overrides[param] = fbSelect.value;
        }
        var n1kSlider = document.getElementById('cgc-n1k-limit');
        if (n1kSlider) {
          var param = n1kSlider.getAttribute('data-param');
          if (param) overrides[param] = parseFloat(n1kSlider.value);
        }

        if (Object.keys(overrides).length === 0) {
          addMessage('ai', '⚠️ 未检测到任何参数变化');
          return;
        }

        applyBtn.disabled = true;
        applyBtn.textContent = '应用...';
        _applySuggestedOverrides(overrides).then(function() {
          addMessage('ai', '✅ 已应用参数：' + Object.keys(overrides).join(', '));
          applyBtn.disabled = false;
          applyBtn.textContent = '应用';
          hideDetailPanel();
        }).catch(function(err) {
          addMessage('ai', '⚠️ 应用失败：' + (err.message || String(err)));
          applyBtn.disabled = false;
          applyBtn.textContent = '应用';
        });
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', hideDetailPanel);
    }
  }

  if (drawerScrim) {
    drawerScrim.hidden = false;
  }

  if (inputDockMain) {
    inputDockMain.classList.add('chat-input-area');
  }

  if (sendBtn) {
    sendBtn.classList.add('chat-send-btn');
    sendBtn.setAttribute('aria-label', DEFAULT_SEND_TEXT);
    sendBtn.title = DEFAULT_SEND_TEXT;
  }

  bootstrapConnectionMetadata();
  hydrateExistingMessages();
    // fault UI removed
    // fault UI removed

  if (drawerFab) {
    drawerFab.addEventListener('click', toggleDrawer);
  }

  if (drawerClose) {
    drawerClose.addEventListener('click', closeDrawer);
  }

  if (drawerScrim) {
    drawerScrim.addEventListener('click', closeDrawer);
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && document.body.classList.contains('drawer-open')) {
      closeDrawer();
    }

  });


  if (systemSelect) {
    systemSelect.addEventListener('change', function() {
      currentSystem = systemSelect.value;
    // fault UI removed
      hideDetailPanel();
      syncSystemChrome();
      resetCanvasState();
      resetTruthEvalBar();
    // fault UI removed
    // fault UI removed
    });
  }





  if (guidedDemoBtn) {
    guidedDemoBtn.addEventListener('click', function() {
      openDrawer();
      addMessage('ai', '▶ 启动引导演示，正在切换到反推系统...');

      currentSystem = 'thrust-reverser';
      if (systemSelect) {
        systemSelect.value = 'thrust-reverser';
      }
      syncSystemChrome();
      resetCanvasState();
      resetTruthEvalBar();

      chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
      openDrawer();
    });
  });

  if (fileUpload) {
    fileUpload.addEventListener('change', function(e) {
      var files = e.target && e.target.files;
      var file = files && files[0];
      var reader;

      if (!file) {
        return;
      }

      openDrawer();
      reader = new FileReader();
      reader.onload = function(ev) {
        var text = (ev.target && ev.target.result) || '';
        addMessage('user', '📎 ' + file.name + ' (' + Math.round(String(text).length / 1024) + 'KB)');
        addMessage('ai', '已收到文档，正在分析...\n（当前阶段只做界面增强，文档深分析仍走现有后端能力。）');
      };
      reader.readAsText(file);
      fileUpload.value = '';
    var lines;
    var nodeId;
    var conds;

    if (!data) {
      return '⚠️ 未收到有效响应，请检查输入参数。';
    }

    extracted = extractEvaluation(data);
    activeIds = extracted.activeIds;
    failed = extracted.failed;

    if (activeIds.length === 0 && Object.keys(failed).length === 0 && !extracted.summary) {
      return '⚠️ 未收到有效响应，请检查输入参数。';
    }

    lines = [];
    lines.push('📊 链路状态分析:');
    lines.push('');
    lines.push('TRA=' + payload.tra_deg + '°  RA=' + payload.radio_altitude_ft + 'ft');

    if (activeIds.length > 0) {
      lines.push('');
      lines.push('✅ 已激活: ' + activeIds.join(', '));
    }

    if (failed && Object.keys(failed).length > 0) {
      lines.push('');
      lines.push('❌ 未通过条件:');
      for (nodeId in failed) {
        if (!Object.prototype.hasOwnProperty.call(failed, nodeId)) {
          continue;
        }
        conds = failed[nodeId] || [];
        if (conds.length > 0) {
          lines.push('  ' + nodeId + ': ' + conds.join(', '));
        }
      }
    }

    if (extracted.summary) {
      lines.push('');
      lines.push('摘要: ' + extracted.summary);
    }

    lines.push('');
    lines.push('详细链路:');
    lines.push('  SW1 → L1 → SW2 → L2(540V) → L3(EEC+PLS+PDU) → VDT90 → L4/THR_LOCK');
    lines.push('');
    lines.push('💡 尝试修改上方参数（如把RA改大到10ft）观察链路变化。');

    return lines.join('\n');
  }

  function formatDemoAnswer(data) {
    var answer;

    if (!data) {
      return '⚠️ 未收到有效响应。';
    }
    if (data.error) {
      return '⚠️ 请求失败: ' + (data.message || data.error);
    }

    answer = data.answer || data.reasoning || JSON.stringify(data).substring(0, 300);
    if (typeof answer !== 'string') {
      answer = String(answer);
    }
    return answer.substring(0, 800);
  }

  function formatSystemSnapshotAnswer(data, systemId) {
    var extracted;
    var lines;

    if (!data) {
      return '⚠️ 未收到有效系统快照。';
    }

    extracted = extractEvaluation(data);
    lines = [];
    lines.push('📊 ' + (SYSTEM_LABELS[systemId] || systemId) + ' 状态分析:');

    if (extracted.activeIds.length > 0) {
      lines.push('');
      lines.push('✅ 已激活: ' + extracted.activeIds.join(', '));
    }

    if (extracted.blockedReasons && extracted.blockedReasons.length > 0) {
      lines.push('');
      lines.push('❌ 阻塞原因:');
      lines.push('  ' + extracted.blockedReasons.join('\n  '));
    }

    if (extracted.summary) {
      lines.push('');
      lines.push('摘要: ' + extracted.summary);
    }

    return lines.join('\n');
  }

  function buildExplainPayload(question, systemId, payload, extraFields) {
    var explainPayload = {
      question: question,
      system_id: systemId,
      prompt: question,
      tra_deg: payload.tra_deg,
      radio_altitude_ft: payload.radio_altitude_ft,
      engine_running: payload.engine_running,
      aircraft_on_ground: payload.aircraft_on_ground,
      reverser_inhibited: payload.reverser_inhibited,
      eec_enable: payload.eec_enable,
      n1k: payload.n1k,
      feedback_mode: payload.feedback_mode,
      lever_snapshot: null,
      node_states: {},
    };
    var key;

    if (!extraFields) {
      return explainPayload;
    }

    for (key in extraFields) {
      if (Object.prototype.hasOwnProperty.call(extraFields, key)) {
        explainPayload[key] = extraFields[key];
      }
    }

    return explainPayload;
  }

  // ── Phase P16: General question handler ────────────────────────────────────
  // Truth engine first: fetch a live snapshot, update canvas immediately, then
  // call AI explain with node_states so the blue discussion ring stays advisory.
  function handleGeneralQuestion(qText, qSystemId, qPayload) {
    var truthPayload = qSystemId === 'thrust-reverser'
      ? copyObject(lastTruthPayloadBySystem[qSystemId] || qPayload)
      : copyObject(qPayload);
    var truthRequest = qSystemId === 'thrust-reverser'
      ? _sendLeverSnapshot(truthPayload)
      : requestJson('/api/system-snapshot?system_id=' + encodeURIComponent(qSystemId));
    var fallbackFormatter = qSystemId === 'thrust-reverser'
      ? null
      : function(data) { return formatSystemSnapshotAnswer(data, qSystemId); };

    truthRequest
      .then(function(snapshotResult) {
        var snapshotData = qSystemId === 'thrust-reverser'
          ? snapshotResult.snapshotData
          : snapshotResult;
        var requestPayload = qSystemId === 'thrust-reverser'
          ? snapshotResult.requestPayload
          : truthPayload;
        var nodeStates = qSystemId === 'thrust-reverser'
          ? snapshotResult.nodeStates
          : extractNodeStates(snapshotData);
        var fallbackText = qSystemId === 'thrust-reverser'
          ? snapshotResult.fallbackText
          : fallbackFormatter(snapshotData);
        var explainPayload;

        if (qSystemId !== 'thrust-reverser') {
          applySystemSnapshotToCanvas(snapshotData);
          renderTruthEvalFromSnapshot(snapshotData, null);
        }

        explainPayload = buildExplainPayload(qText, qSystemId, requestPayload, {
          lever_snapshot: snapshotData,
          node_states: nodeStates,
          fault_injections: [],
        });

        return requestJson('/api/chat/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(explainPayload),
        }).then(function(aiData) {
          var highlightedNodes = Array.isArray(aiData.highlighted_nodes) ? aiData.highlighted_nodes : [];
          var suggestionNodes = Array.isArray(aiData.suggestion_nodes) ? aiData.suggestion_nodes : [];

          applyAiHighlights(highlightedNodes, suggestionNodes);
          addMessage('ai', aiData.explanation || fallbackText, {
            highlightedNodes: highlightedNodes,
            suggestionNodes: suggestionNodes,
          });
          finishChatRequest();
        }, function(err) {
          addMessage('ai', fallbackText);
          finishChatRequest();
          return null;
        });
      })
      .catch(function(err) {
        renderRequestFailure(err);
        addMessage('ai', '⚠️ 真值快照请求失败: ' + err.message + '。请稍后重试。');
        finishChatRequest();
      });
  }

  // ── Phase C: Enhanced intent router ─────────────────────────────────────────
  // Detects non-condition "why / what / how" questions and routes them to
  // handleGeneralQuestion() so they don't incorrectly trigger lever-snapshot.
function hasOperateIntent(qText, qLower) {
    // Patterns indicating user wants to change/regulate/adjust parameters
    var operatePatterns = [
      // Compound action verbs
      '调节', '调整', '设置', '达到', '触发', '激活', '满足', '实现',
      // Technical parameter keywords (minimum 3 chars to avoid short noise)
      'vd', 'vdt', 'tra', 'altitude', 'radio',
      'deploy', 'position', 'override', 'manual',
      'inhibit', '引擎',
      // Specific logic gate targets
      '满足l1', '满足l2', '满足l3', '满足l4',
      'l1满足', 'l2满足', 'l3满足', 'l4满足',
      // Compound with target words (these require a target, won't match standalone nouns)
      '把tra', '把vdt', '把vd', '让tra', '拉倒', '推到',
    ];
    var i;
    for (i = 0; i < operatePatterns.length; i += 1) {
      if (qLower.includes(operatePatterns[i])) {
        return true;
      }
    }
    return false;
  }

  function handleOperateIntent(text, systemId) {
    var operatePayload = {
      question: text,
      system_id: systemId,
      current_snapshot: lastTruthPayloadBySystem[systemId] || null,
    };
    setInputLoading(true);
    clearAiHighlights();
    openDrawer();
    requestJson('/api/chat/operate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(operatePayload),
    })
      .then(function(operateResult) {
        handleOperateResponse(operateResult);
        finishChatRequest();
      })
      .catch(function(err) {
        addMessage('ai', '⚠️ 操作请求失败: ' + err.message);
        finishChatRequest();
      });
  }

function isGeneralQuestion(qText, qLower) {
    // "为什么会失效" / "TLS是什么" / "怎么工作" / "哪些条件" etc.
    var generalPatterns = [
      '为什么', '怎么', '是什么', '哪些', '介绍一下', '解释一下',
      '说明一下', '告诉我', '帮我', '如何', '怎样', '什么意思',
      '有什么用', '工作原理', '系统介绍', '科普',
    ];
    var i;
    for (i = 0; i < generalPatterns.length; i += 1) {
      if (qLower.includes(generalPatterns[i])) {
        return true;
      }
    }
    // Standalone "?" in a short message is usually a general question
    if (qText.trim().length < 60 && qText.includes('?')) {
      return true;
    }
    return false;
  }

  // ── P17-gen: Deep reasoning response handler ─────────────────────────────────
  // response_type: 'refusal' | 'operation_suggestion' | 'analysis' | 'explanation'
  function handleReasonResponse(reasonData, responseType) {
    var highlightedNodes = Array.isArray(reasonData.highlighted_nodes) ? reasonData.highlighted_nodes : [];
    var suggestionNodes = Array.isArray(reasonData.suggestion_nodes) ? reasonData.suggestion_nodes : [];
    var deepReasoning = reasonData.deep_reasoning || '';
    var explanation = reasonData.explanation || '';

    if (responseType === 'refusal') {
      applyAiHighlights(highlightedNodes, suggestionNodes);
      // Show explanation first if present (backend may include useful context even in refusal)
      if (explanation) {
        addMessage('ai', explanation + '\n\n⚠️ ' + (reasonData.refusal_reason || '这个问题超出本工具的分析范围。') + '\n\n建议：尝试询问与反推系统控制逻辑直接相关的问题，例如某个链路节点为什么激活/被阻塞、参数阈值含义、故障诊断等。');
      } else {
        addMessage('ai', '⚠️ ' + (reasonData.refusal_reason || '这个问题超出本工具的分析范围。') + '\n\n建议：尝试询问与反推系统控制逻辑直接相关的问题，例如某个链路节点为什么激活/被阻塞、参数阈值含义、故障诊断等。');
      }
      return;
    }

    if (responseType === 'operation_suggestion') {
      // Apply node highlights before showing operate response
      applyAiHighlights(highlightedNodes, suggestionNodes);
      handleOperateResponse({
        action_type: 'suggest_parameter_override',
        ai_explanation: explanation,
        parameter_overrides: reasonData.parameter_overrides || {},
        auto_apply: reasonData.auto_apply === true,
        confidence: reasonData.confidence || 0.5,
      });
      if (deepReasoning) {
        appendDeepReasoning(deepReasoning);
      }
      return;
    }

    // analysis | explanation — show explanation with highlights + optional deep reasoning
    applyAiHighlights(highlightedNodes, suggestionNodes);
    addMessage('ai', explanation, {
      highlightedNodes: highlightedNodes,
      suggestionNodes: suggestionNodes,
    });
    if (deepReasoning) {
      appendDeepReasoning(deepReasoning);
    }
  }

  // Append collapsible deep reasoning section below the last AI message
  function appendDeepReasoning(reasoningText) {
    var toggleBtn = document.createElement('button');
    toggleBtn.className = 'deep-reasoning-toggle';
    toggleBtn.setAttribute('aria-expanded', 'false');
    toggleBtn.innerHTML = '🔍 <span>展开推理过程</span>';

    var content = document.createElement('div');
    content.className = 'deep-reasoning-content';
    content.style.display = 'none';
    content.textContent = reasoningText;

    toggleBtn.addEventListener('click', function() {
      var expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
      toggleBtn.setAttribute('aria-expanded', String(!expanded));
      toggleBtn.querySelector('span').textContent = expanded ? '展开推理过程' : '收起推理过程';
      content.style.display = expanded ? 'none' : 'block';
    });

    if (chatMessages) {
      chatMessages.appendChild(toggleBtn);
      chatMessages.appendChild(content);
      scrollChatToBottom();
    }
  }

  function handleSend() {
    var text;
    var lowerText;
    var systemId;
    var payload;

    if (!chatInput) {
      return;
    }

    text = chatInput.value.trim();
    if (!text) {
      return;
    }

    openDrawer();
    addMessage('user', text);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    setInputLoading(true);
    clearAiHighlights();

    lowerText = text.toLowerCase();
    systemId = currentSystem;

    payload = buildDefaultLeverPayload(text, systemId);

    // Phase C: Intercept general/explanatory questions before keyword routing
    if (isGeneralQuestion(text, lowerText)) {
      handleGeneralQuestion(text, systemId, payload);
      return;
    }

    // Detect operate intent: user wants to change/adjust/regulate lever parameters
    if (hasOperateIntent(text, lowerText)) {
      handleOperateIntent(text, systemId);
      return;
    }

    if (systemId !== 'thrust-reverser') {
      handleGeneralQuestion(text, systemId, payload);
      return;
    }

    // Guided/demo shortcut — short-circuit without AI reasoning
    if (lowerText.includes('guided') || lowerText.includes('demo') || lowerText.includes('带我走')) {
      addMessage('ai', '▶ 点击抽屉里的”引导演示”，我会带你一步一步看完整的反推链路激活过程。');
      finishChatRequest();
      return;
    }

    // All other thrust-reverser input → unified deep AI reasoning
    // Use cached truth payload so canvas state is preserved; fall back to defaults if no cache
    var cachedPayload = lastTruthPayloadBySystem['thrust-reverser'] || payload;
    var reqSeq = ++_chatRequestSeq;

    requestJson('/api/lever-snapshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cachedPayload),
    })
      .then(function(snapshotData) {
        if (reqSeq !== _chatRequestSeq) { finishChatRequest(); return; }
        var reasonPayload = {
          question: text,
          system_id: systemId,
          current_snapshot: snapshotData,
          fault_injections: [],
        };

        requestJson('/api/chat/reason', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reasonPayload),
        })
          .then(function(reasonData) {
            if (reqSeq !== _chatRequestSeq) { finishChatRequest(); return; }
            handleReasonResponse(reasonData, reasonData.response_type);
            finishChatRequest();
          })
          .catch(function(err) {
            if (reqSeq !== _chatRequestSeq) { finishChatRequest(); return; }
            applyAiHighlights([], []);
            addMessage('ai', formatLeverSnapshotAnswer(snapshotData, cachedPayload));
            finishChatRequest();
          });
      })
      .catch(function(err) {
        renderRequestFailure(err);
        addMessage('ai', '⚠️ 请求失败: ' + err.message);
        finishChatRequest();
      });
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', handleSend);
  }

  if (chatInput) {
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    chatInput.addEventListener('input', function() {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
    });
  }

  resetCanvasState();
  resetTruthEvalBar();
  syncSystemChrome();
    // fault UI removed
    // fault UI removed
  setFabTooltip('展开对话');
  initZoomAndPanel();

  if (logicDiagram && currentSystem === 'thrust-reverser') {
    setTruthBadge('idle', '空闲');
  }

  if (chatInput) {
    chatInput.focus();
  }

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
            'ft  TRA=' + r.tra_deg.toFixed(2) + '\u00b0' +
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

  // Wire analysis panel buttons
  var analysisBtn = document.getElementById('chat-analysis-btn');
  if (analysisBtn) analysisBtn.addEventListener('click', function() {
    var diagPanel = document.getElementById('diagnosis-panel');
    var mcPanel = document.getElementById('monte-carlo-panel');
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

  // Wire hardware schema button
  var hwSchemaBtn = document.getElementById('chat-hardware-schema-btn');
  if (hwSchemaBtn) hwSchemaBtn.addEventListener('click', openHardwareSchemaPanel);

  var hwSchemaFetchBtn = document.getElementById('hw-schema-fetch-btn');
  if (hwSchemaFetchBtn) hwSchemaFetchBtn.addEventListener('click', runHardwareSchema);
})();
