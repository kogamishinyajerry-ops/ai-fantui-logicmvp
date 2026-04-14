/* ── chat.js — Phase A Canvas Shell ── */

(function() {
  var currentSystem = 'thrust-reverser';
  var chatMessages = document.getElementById('chat-messages');
  var chatInput = document.getElementById('chat-input');
  var sendBtn = document.getElementById('chat-send-btn');
  var inputDock = document.querySelector('.input-dock');
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
  var logicDiagram = document.getElementById('logic-diagram');
  var canvasTitle = logicDiagram ? logicDiagram.querySelector('h1') : null;
  var DEFAULT_INPUT_PLACEHOLDER = '输入你的控制逻辑问题...';
  var DEFAULT_SEND_TEXT = '发送';
  var LOADING_SEND_TEXT = 'AI 思考中...';
  var lastTruthPayloadBySystem = {};

  var SYSTEM_LABELS = {
    'thrust-reverser': '反推系统',
    'landing-gear': '起落架系统',
    'bleed-air': '引气阀系统',
    efds: '干扰弹系统',
  };

  var NODE_VALUE_KEYS = {
    tls115: 'tls_115vac_cmd',
    etrac_540v: 'etrac_540vdc_cmd',
    eec_deploy: 'eec_deploy_cmd',
    pls_power: 'pls_power_cmd',
    pdu_motor: 'pdu_motor_cmd',
    vdt90: 'deploy_90_percent_vdt',
    thr_lock: 'throttle_electronic_lock_release_cmd',
  };

  var FAILED_CONDITION_NODE_MAP = {
    radio_altitude_ft: 'radio_altitude_ft',
    sw1: 'sw1',
    reverser_inhibited: 'reverser_inhibited',
    engine_running: 'engine_running',
    aircraft_on_ground: 'aircraft_on_ground',
    sw2: 'sw2',
    eec_enable: 'eec_enable',
    n1k: 'n1k',
    tra_deg: 'tra_deg',
    deploy_90_percent_vdt: 'vdt90',
  };

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
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

  function finishChatRequest() {
    setInputLoading(false);
    if (chatInput) {
      chatInput.focus();
    }
  }

  function renderRequestFailure(err) {
    setTruthBadge('danger', '错误');
    if (truthEvalStatus) {
      truthEvalStatus.textContent = '请求失败';
    }
    if (truthEvalSummary) {
      truthEvalSummary.textContent = '⚠️ 请求失败: ' + err.message;
    }
  }

  function addMessage(role, text, highlight) {
    if (!chatMessages) {
      return;
    }

    var avatar = role === 'ai' ? '🤖' : '👤';
    var highlightedNodes = [];
    var suggestionNodes = [];
    var msg = document.createElement('article');

    if (Array.isArray(highlight)) {
      highlightedNodes = highlight;
    } else if (highlight) {
      highlightedNodes = Array.isArray(highlight.highlightedNodes) ? highlight.highlightedNodes : [];
      suggestionNodes = Array.isArray(highlight.suggestionNodes) ? highlight.suggestionNodes : [];
    }

    msg.className = 'chat-message chat-message-' + (role === 'ai' ? 'ai' : 'user');
    if (highlightedNodes.length > 0) {
      msg.setAttribute('data-highlighted', highlightedNodes.join(','));
    }
    if (suggestionNodes.length > 0) {
      msg.setAttribute('data-suggested', suggestionNodes.join(','));
    }
    msg.innerHTML =
      '<div class="chat-message-avatar">' + avatar + '</div>' +
      '<div class="chat-message-content"><p>' + escHtml(text).replace(/\n/g, '<br>') + '</p></div>';
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

    if (inputDock) {
      inputDock.classList.toggle('is-loading', loading);
    }
    if (chatLoadingStatus) {
      chatLoadingStatus.textContent = loading ? LOADING_SEND_TEXT : '就绪';
      chatLoadingStatus.classList.toggle('is-loading', loading);
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
        (data && typeof data.summary === 'string' ? data.summary : ''),
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

    if (merged.sw1 === undefined && typeof payload.tra_deg === 'number') {
      merged.sw1 = payload.tra_deg <= -14.0;
    }
    if (merged.sw2 === undefined && typeof merged.sw1 === 'boolean') {
      merged.sw2 = merged.sw1;
    }
    if (merged.deploy_90_percent_vdt === undefined && typeof payload.deploy_position_percent === 'number') {
      merged.deploy_90_percent_vdt = payload.deploy_position_percent >= 90.0;
    }

    return merged;
  }

  function resetCanvasState() {
    var nodes;
    var values;
    var i;

    clearAiHighlights();
    nodes = document.querySelectorAll('.canvas-wrapper [data-node]');
    values = document.querySelectorAll('.canvas-wrapper [data-value-for]');

    for (i = 0; i < nodes.length; i += 1) {
      nodes[i].classList.remove('is-active', 'is-blocked', 'is-inactive');
      nodes[i].classList.add('is-inactive');
      nodes[i].setAttribute('data-state', 'inactive');
    }

    for (i = 0; i < values.length; i += 1) {
      values[i].textContent = '—';
    }
  }

  function setNodeState(nodeId, state) {
    var els;
    var i;

    els = document.querySelectorAll('.canvas-wrapper [data-node="' + nodeId + '"]');
    for (i = 0; i < els.length; i += 1) {
      els[i].classList.remove('is-active', 'is-blocked', 'is-inactive');
      els[i].classList.add('is-' + state);
      els[i].setAttribute('data-state', state);
    }
  }

  function setNodeValue(nodeId, value) {
    var valueKey = NODE_VALUE_KEYS[nodeId] || nodeId;
    var els = document.querySelectorAll('.canvas-wrapper [data-value-for="' + valueKey + '"]');
    var i;

    for (i = 0; i < els.length; i += 1) {
      els[i].textContent = formatSignalValue(value);
    }
  }

  function clearAiHighlights() {
    var highlightedEls = document.querySelectorAll('.canvas-wrapper .ai-discussed, .canvas-wrapper .ai-suggested');
    var i;

    for (i = 0; i < highlightedEls.length; i += 1) {
      highlightedEls[i].classList.remove('ai-discussed', 'ai-suggested');
    }
  }

  function applyAiHighlights(highlightedNodes, suggestionNodes) {
    var discussed = dedupe(Array.isArray(highlightedNodes) ? highlightedNodes : []);
    var suggested = dedupe(Array.isArray(suggestionNodes) ? suggestionNodes : []);
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
        activeLogicNodeIds[truthEvaluation.active_logic_node_ids[i]] = true;
      }
    }

    for (i = 0; i < logicNodes.length; i += 1) {
      if (logicNodes[i] && logicNodes[i].id) {
        logicNodeIds[logicNodes[i].id] = true;
      }
    }

    for (i = 0; i < nodes.length; i += 1) {
      if (!nodes[i] || !nodes[i].id) {
        continue;
      }
      nodeId = nodes[i].id;
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
  }

  function applySnapshotToCanvas(data, payload) {
    var extracted = extractEvaluation(data);
    var componentValues = mergePayloadSignals(extracted.componentValues, payload);
    var blockedInputNodes = {};
    var activeLogicMap = {};
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
    var logicId;
    var conds;
    var i;
    var j;
    var nodeId;
    var valueKey;
    var value;
    var state;

    resetCanvasState();

    for (i = 0; i < extracted.activeIds.length; i += 1) {
      activeLogicMap[extracted.activeIds[i]] = true;
    }

    for (logicId in extracted.failed) {
      if (!Object.prototype.hasOwnProperty.call(extracted.failed, logicId)) {
        continue;
      }
      conds = extracted.failed[logicId] || [];
      for (j = 0; j < conds.length; j += 1) {
        nodeId = FAILED_CONDITION_NODE_MAP[conds[j]];
        if (nodeId) {
          blockedInputNodes[nodeId] = true;
        }
      }
    }

    for (i = 0; i < nodeIds.length; i += 1) {
      nodeId = nodeIds[i];
      if (/^logic\d+$/.test(nodeId)) {
        if (activeLogicMap[nodeId]) {
          setNodeState(nodeId, 'active');
        } else if (extracted.failed[nodeId] && extracted.failed[nodeId].length > 0) {
          setNodeState(nodeId, 'blocked');
        } else {
          setNodeState(nodeId, 'inactive');
        }
        continue;
      }

      valueKey = NODE_VALUE_KEYS[nodeId] || nodeId;
      value = componentValues[valueKey];
      // Non-logic-gate nodes: check extracted.failed (from nodes array) for blocked
      // state, since deriveComponentState can't render 'blocked' for intermediate
      // output nodes that aren't in componentValues (value=undefined).
      if (extracted.failed[nodeId] && extracted.failed[nodeId].length > 0) {
        setNodeState(nodeId, 'blocked');
      } else {
        state = deriveComponentState(value, !!blockedInputNodes[nodeId]);
        setNodeState(nodeId, state);
        if (value !== undefined) {
          setNodeValue(nodeId, value);
        }
      }
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

  if (drawerScrim) {
    drawerScrim.hidden = false;
  }

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
      syncSystemChrome();
      resetCanvasState();
      resetTruthEvalBar();
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

      setTimeout(function() {
        addMessage('ai', '步骤 1：设置 TRA = -14°（达到反推门槛）');
      }, 1400);

      setTimeout(function() {
        addMessage('ai', '步骤 2：设置 RA = 0ft（off-ground，altitude gate = false）');
      }, 2800);

      setTimeout(function() {
        addMessage('ai', '✅ SW1 已 latch，接下来可以观察 logic1 到 logic4 如何逐段亮起。');
      }, 4300);
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('.chat-shortcut-btn'), function(btn) {
    btn.addEventListener('click', function() {
      var prompt = btn.getAttribute('data-prompt');
      if (!prompt || !chatInput) {
        return;
      }
      chatInput.value = prompt;
      chatInput.focus();
      chatInput.style.height = 'auto';
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
    });
  }

  /* ── Response formatters ── */
  function formatLeverSnapshotAnswer(data, payload) {
    var extracted;
    var activeIds;
    var failed;
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
      ? requestJson('/api/lever-snapshot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(truthPayload),
        })
      : requestJson('/api/system-snapshot?system_id=' + encodeURIComponent(qSystemId));
    var fallbackFormatter = qSystemId === 'thrust-reverser'
      ? function(data) { return formatLeverSnapshotAnswer(data, truthPayload); }
      : function(data) { return formatSystemSnapshotAnswer(data, qSystemId); };

    truthRequest
      .then(function(snapshotData) {
        var nodeStates = extractNodeStates(snapshotData);
        var explainPayload;

        if (qSystemId === 'thrust-reverser') {
          lastTruthPayloadBySystem[qSystemId] = copyObject(truthPayload);
          applySnapshotToCanvas(snapshotData, truthPayload);
          renderTruthEvalFromSnapshot(snapshotData, truthPayload);
        } else {
          applySystemSnapshotToCanvas(snapshotData);
          renderTruthEvalFromSnapshot(snapshotData, null);
        }

        explainPayload = buildExplainPayload(qText, qSystemId, truthPayload, {
          lever_snapshot: snapshotData,
          node_states: nodeStates,
        });

        return requestJson('/api/chat/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(explainPayload),
        }).then(function(aiData) {
          var highlightedNodes = Array.isArray(aiData.highlighted_nodes) ? aiData.highlighted_nodes : [];
          var suggestionNodes = Array.isArray(aiData.suggestion_nodes) ? aiData.suggestion_nodes : [];

          applyAiHighlights(highlightedNodes, suggestionNodes);
          addMessage('ai', aiData.explanation || fallbackFormatter(snapshotData), {
            highlightedNodes: highlightedNodes,
            suggestionNodes: suggestionNodes,
          });
          finishChatRequest();
        }, function(err) {
          addMessage('ai', fallbackFormatter(snapshotData));
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

  function handleSend() {
    var text;
    var lowerText;
    var systemId;
    var payload;
    var useLeverSnapshot;
    var traMatch;
    var raMatch;

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

    payload = {
      prompt: text,
      system_id: systemId,
      tra_deg: 0.0,
      radio_altitude_ft: 5.0,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 35.0,
      max_n1k_deploy_limit: 60.0,
      feedback_mode: 'auto_scrubber',
      deploy_position_percent: 0.0,
    };

    useLeverSnapshot = false;

    // Phase C: Intercept general/explanatory questions before keyword routing
    if (isGeneralQuestion(text, lowerText)) {
      handleGeneralQuestion(text, systemId, payload);
      return;
    }

    if (systemId !== 'thrust-reverser') {
      handleGeneralQuestion(text, systemId, payload);
      return;
    }

    if (lowerText.includes('tls') || lowerText.includes('失效') || lowerText.includes('failure')) {
      payload.tra_deg = -14.0;
      payload.radio_altitude_ft = 5.0;
      payload.feedback_mode = 'auto_scrubber';
      useLeverSnapshot = true;
    } else if (lowerText.includes('vdt') || (lowerText.includes('90') && lowerText.includes('%'))) {
      payload.tra_deg = -14.0;
      payload.radio_altitude_ft = 5.0;
      payload.engine_running = true;
      payload.aircraft_on_ground = true;
      payload.reverser_inhibited = false;
      payload.eec_enable = true;
      payload.n1k = 35.0;
      payload.feedback_mode = 'auto_scrubber';
      useLeverSnapshot = true;
    } else if (lowerText.includes('throttle') || lowerText.includes('lock') || lowerText.includes('thr_lock')) {
      payload.tra_deg = -14.0;
      payload.radio_altitude_ft = 5.0;
      payload.feedback_mode = 'auto_scrubber';
      useLeverSnapshot = true;
    } else if (
      lowerText.includes('tra') &&
      (lowerText.includes('拉') || lowerText.includes('-14') || lowerText.includes('-20') || lowerText.includes('阈值'))
    ) {
      traMatch = text.match(/(-?\d+)[°]?/);
      if (traMatch) {
        payload.tra_deg = parseFloat(traMatch[1]);
      } else {
        payload.tra_deg = -14.0;
      }
      useLeverSnapshot = true;
    } else if (lowerText.includes('altitude') || lowerText.includes('ra ') || lowerText.includes('radio')) {
      raMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:ft|英尺)/);
      if (raMatch) {
        payload.radio_altitude_ft = parseFloat(raMatch[1]);
      } else if (lowerText.includes('0') || lowerText.includes('零')) {
        payload.radio_altitude_ft = 0.0;
      } else {
        payload.radio_altitude_ft = 5.0;
      }
      payload.tra_deg = -14.0;
      useLeverSnapshot = true;
    } else if (lowerText.includes('manual') || lowerText.includes('override')) {
      payload.tra_deg = -14.0;
      payload.feedback_mode = 'manual_feedback_override';
      payload.deploy_position_percent = 95.0;
      useLeverSnapshot = true;
    } else if (lowerText.includes('inhibit')) {
      payload.tra_deg = -14.0;
      payload.reverser_inhibited = true;
      useLeverSnapshot = true;
    } else if (lowerText.includes('l3') || lowerText.includes('eec') || lowerText.includes('pls') || lowerText.includes('pdu') || lowerText.includes('pms') || lowerText.includes('hydraulic') || lowerText.includes('bleed') || lowerText.includes('eec失效') || lowerText.includes('pdu故障') || lowerText.includes('pls失效') || lowerText.includes('发动机控制')) {
      payload.tra_deg = -14.0;
      payload.radio_altitude_ft = 5.0;
      payload.feedback_mode = 'auto_scrubber';
      useLeverSnapshot = true;
    } else if (lowerText.includes('n1') || lowerText.includes('转速') || lowerText.includes('engine')) {
      payload.tra_deg = -14.0;
      payload.radio_altitude_ft = 5.0;
      payload.feedback_mode = 'auto_scrubber';
      useLeverSnapshot = true;
    } else if (lowerText.includes('guided') || lowerText.includes('demo') || lowerText.includes('带我走')) {
      addMessage('ai', '▶ 点击抽屉里的“引导演示”，我会带你一步一步看完整的反推链路激活过程。');
      finishChatRequest();
      return;
    } else {
      payload.tra_deg = -14.0;
      useLeverSnapshot = true;
    }

    if (useLeverSnapshot) {
      requestJson('/api/lever-snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function(data) {
          var nodeStates;
          var explainPayload;
          var fallbackText;

          lastTruthPayloadBySystem[systemId] = copyObject(payload);
          // Step 1: SVG canvas + Truth Eval update synchronously (< 100ms)
          applySnapshotToCanvas(data, payload);
          renderTruthEvalFromSnapshot(data, payload);
          nodeStates = extractNodeStates(data);
          fallbackText = formatLeverSnapshotAnswer(data, payload);

          // Step 2: Call MiniMax LLM for contextual explanation (1-2s)
          explainPayload = buildExplainPayload(text, systemId, payload, {
            lever_snapshot: data,
            node_states: nodeStates,
          });
          requestJson('/api/chat/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(explainPayload),
          })
            .then(function(expData) {
              var highlightedNodes = Array.isArray(expData.highlighted_nodes) ? expData.highlighted_nodes : [];
              var suggestionNodes = Array.isArray(expData.suggestion_nodes) ? expData.suggestion_nodes : [];

              applyAiHighlights(highlightedNodes, suggestionNodes);
              addMessage('ai', expData.explanation || fallbackText, {
                highlightedNodes: highlightedNodes,
                suggestionNodes: suggestionNodes,
              });
              finishChatRequest();
            })
            .catch(function(err) {
              // Fallback to template if MiniMax API fails
              addMessage('ai', fallbackText);
              finishChatRequest();
            });
        })
        .catch(function(err) {
          renderRequestFailure(err);
          addMessage('ai', '⚠️ 请求失败: ' + err.message);
          finishChatRequest();
        });
    } else {
      requestJson('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function(data) {
          renderTruthEvalFromDemo(data);
          addMessage('ai', formatDemoAnswer(data));
          finishChatRequest();
        })
        .catch(function(err) {
          renderRequestFailure(err);
          addMessage('ai', '⚠️ 请求失败: ' + err.message);
          finishChatRequest();
        });
    }
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
  setFabTooltip('展开对话');

  if (logicDiagram && currentSystem === 'thrust-reverser') {
    setTruthBadge('idle', '空闲');
  }

  if (chatInput) {
    chatInput.focus();
  }
})();
