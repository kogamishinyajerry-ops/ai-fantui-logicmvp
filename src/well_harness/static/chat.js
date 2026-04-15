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
  var faultBar = document.getElementById('chat-fault-bar');
  var faultPills = document.getElementById('chat-fault-pills');
  var faultPresetsBtn = document.getElementById('chat-fault-presets');
  var faultClearBtn = document.getElementById('chat-fault-clear');
  var faultToggleBtn = document.getElementById('chat-fault-toggle');
  var faultPresetsMenu = document.getElementById('chat-fault-presets-menu');
  var logicDiagram = document.getElementById('logic-diagram');
  var canvasStage = document.querySelector('.canvas-stage');
  var nodeFaultBtn = document.getElementById('node-fault-btn');
  var nodeFaultMenu = document.getElementById('node-fault-menu');
  var canvasTitle = logicDiagram ? logicDiagram.querySelector('h1') : null;
  var DEFAULT_INPUT_PLACEHOLDER = '输入你的控制逻辑问题...';
  var DEFAULT_SEND_TEXT = '发送';
  var LOADING_SEND_TEXT = 'AI 思考中...';
  var FAULT_REEVAL_TEXT = '故障重评估中...';
  var lastTruthPayloadBySystem = {};
  var nodeRefHighlightTimer = null;
  var activeFaults = new Map();
  var isFaultBarExpanded = false;
  var hoveredFaultNodeId = null;
  var currentFaultMenuNodeId = null;
  var faultUiBusy = false;

  var SYSTEM_LABELS = {
    'thrust-reverser': '反推系统',
    'landing-gear': '起落架系统',
    'bleed-air': '引气阀系统',
    efds: '干扰弹系统',
  };

  var FAULT_TYPES = {
    stuck_off: { label: '卡关(OFF)', icon: '⚡', nodes: ['sw1', 'sw2'] },
    stuck_on: { label: '卡开(ON)', icon: '⚡', nodes: ['sw1', 'sw2'] },
    sensor_zero: { label: '传感器失效', icon: '⚡', nodes: ['tls115', 'radio_altitude_ft'] },
    logic_stuck_false: { label: '逻辑卡死', icon: '⚡', nodes: ['logic1', 'logic2', 'logic3', 'logic4'] },
    cmd_blocked: { label: '命令阻塞', icon: '⚡', nodes: ['thr_lock', 'vdt90'] },
  };

  var FAULT_PRESETS = [
    {
      id: 'sw2-stuck-off',
      label: 'SW2 卡关',
      faults: [{ nodeId: 'sw2', faultType: 'stuck_off' }],
    },
    {
      id: 'tls-sensor-zero',
      label: 'TLS 失效',
      faults: [{ nodeId: 'tls115', faultType: 'sensor_zero' }],
    },
    {
      id: 'full-chain-break',
      label: '全链路断裂',
      faults: [
        { nodeId: 'sw1', faultType: 'stuck_off' },
        { nodeId: 'sw2', faultType: 'stuck_off' },
      ],
    },
  ];

  var FAULT_NODE_LABELS = {
    radio_altitude_ft: 'RA',
    sw1: 'SW1',
    sw2: 'SW2',
    tls115: 'TLS',
    logic1: 'L1',
    logic2: 'L2',
    logic3: 'L3',
    logic4: 'L4',
    vdt90: 'VDT90',
    thr_lock: 'THR_LOCK',
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
      feedback_mode: 'auto_scrubber',
      deploy_position_percent: 0.0,
    };
  }

  function isFaultUiEnabled() {
    return currentSystem === 'thrust-reverser';
  }

  function getCurrentTopologyElement() {
    return document.getElementById('chain-topology-' + currentSystem);
  }

  function getFaultTypeOptionsForNode(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var options = [];
    var faultType;
    var def;

    if (!normalizedNodeId) {
      return options;
    }

    for (faultType in FAULT_TYPES) {
      if (!Object.prototype.hasOwnProperty.call(FAULT_TYPES, faultType)) {
        continue;
      }
      def = FAULT_TYPES[faultType];
      if (def.nodes.indexOf(normalizedNodeId) !== -1) {
        options.push(faultType);
      }
    }

    return options;
  }

  function getFaultNodeLabel(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);

    if (!normalizedNodeId) {
      return String(nodeId || '');
    }

    return FAULT_NODE_LABELS[normalizedNodeId] || normalizedNodeId.toUpperCase();
  }

  function getFaultDisplayLabel(nodeId, faultType) {
    var faultDef = FAULT_TYPES[faultType];
    return getFaultNodeLabel(nodeId) + ' · ' + (faultDef ? faultDef.label : faultType);
  }

  function serializeActiveFaults() {
    var serialized = [];

    activeFaults.forEach(function(faultType, nodeId) {
      var faultDef = FAULT_TYPES[faultType];

      if (!faultDef) {
        return;
      }

      serialized.push({
        node_id: nodeId,
        fault_type: faultType,
        label: faultDef.label,
        icon: faultDef.icon,
      });
    });

    serialized.sort(function(a, b) {
      return String(a.node_id).localeCompare(String(b.node_id));
    });
    return serialized;
  }

  function buildFaultAwareLeverPayload(payload) {
    var nextPayload = copyObject(payload || buildDefaultLeverPayload('', 'thrust-reverser'));
    var serializedFaults = serializeActiveFaults();
    var nodeFaultMap = {};
    var i;

    delete nextPayload.fault_injections;
    delete nextPayload.node_fault_map;
    delete nextPayload.sw1;
    delete nextPayload.sw2;
    delete nextPayload.tls115;
    delete nextPayload.logic1;
    delete nextPayload.logic2;
    delete nextPayload.logic3;
    delete nextPayload.logic4;
    delete nextPayload.vdt90;
    delete nextPayload.thr_lock;

    if (serializedFaults.length === 0) {
      return nextPayload;
    }

    for (i = 0; i < serializedFaults.length; i += 1) {
      nodeFaultMap[serializedFaults[i].node_id] = serializedFaults[i].fault_type;
    }

    nextPayload.fault_injections = serializedFaults;
    nextPayload.node_fault_map = nodeFaultMap;

    if (nodeFaultMap.sw1 === 'stuck_off') {
      nextPayload.sw1 = false;
    } else if (nodeFaultMap.sw1 === 'stuck_on') {
      nextPayload.sw1 = true;
    }

    if (nodeFaultMap.sw2 === 'stuck_off') {
      nextPayload.sw2 = false;
    } else if (nodeFaultMap.sw2 === 'stuck_on') {
      nextPayload.sw2 = true;
    }

    if (nodeFaultMap.radio_altitude_ft === 'sensor_zero') {
      nextPayload.radio_altitude_ft = 0.0;
    }

    if (nodeFaultMap.tls115 === 'sensor_zero') {
      nextPayload.tls115 = 0.0;
    }

    if (nodeFaultMap.logic1 === 'logic_stuck_false') {
      nextPayload.logic1 = false;
    }
    if (nodeFaultMap.logic2 === 'logic_stuck_false') {
      nextPayload.logic2 = false;
    }
    if (nodeFaultMap.logic3 === 'logic_stuck_false') {
      nextPayload.logic3 = false;
    }
    if (nodeFaultMap.logic4 === 'logic_stuck_false') {
      nextPayload.logic4 = false;
    }

    if (nodeFaultMap.vdt90 === 'cmd_blocked') {
      nextPayload.vdt90 = false;
    }
    if (nodeFaultMap.thr_lock === 'cmd_blocked') {
      nextPayload.thr_lock = false;
    }

    return nextPayload;
  }

  function setFaultUiBusy(loading) {
    faultUiBusy = !!loading;

    if (faultPresetsBtn) {
      faultPresetsBtn.disabled = loading;
    }
    if (faultClearBtn) {
      faultClearBtn.disabled = loading || activeFaults.size === 0;
    }
    if (faultToggleBtn) {
      faultToggleBtn.disabled = loading || !isFaultUiEnabled();
    }
    if (nodeFaultBtn) {
      nodeFaultBtn.disabled = loading;
    }

    if (!sendBtn || sendBtn.disabled) {
      return;
    }

    if (chatLoadingStatus) {
      chatLoadingStatus.textContent = loading ? FAULT_REEVAL_TEXT : '就绪';
      chatLoadingStatus.classList.toggle('is-loading', loading);
    }
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
    var requestPayload = buildFaultAwareLeverPayload(payload);

    return requestJson('/api/lever-snapshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestPayload),
    }).then(function(data) {
      lastTruthPayloadBySystem['thrust-reverser'] = copyObject(requestPayload);
      applySnapshotToCanvas(data, requestPayload);
      renderTruthEvalFromSnapshot(data, requestPayload);
      updateChainWithFaults();

      return {
        snapshotData: data,
        requestPayload: requestPayload,
        nodeStates: extractNodeStates(data),
        fallbackText: formatLeverSnapshotAnswer(data, requestPayload),
      };
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

  function clearAiHighlights() {
    var highlightedEls = document.querySelectorAll('.canvas-wrapper .ai-discussed, .canvas-wrapper .ai-suggested');
    var i;

    for (i = 0; i < highlightedEls.length; i += 1) {
      highlightedEls[i].classList.remove('ai-discussed', 'ai-suggested');
    }
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
    var blockedInputNodes = {};
    var activeLogicMap = {};
    var failedByNodeId = {};
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
    var normalizedLogicId;
    var conds;
    var i;
    var j;
    var nodeId;
    var valueKey;
    var value;
    var state;

    resetCanvasState();

    for (i = 0; i < extracted.activeIds.length; i += 1) {
      nodeId = normalizeNodeId(extracted.activeIds[i]) || extracted.activeIds[i];
      activeLogicMap[nodeId] = true;
    }

    for (logicId in extracted.failed) {
      if (!Object.prototype.hasOwnProperty.call(extracted.failed, logicId)) {
        continue;
      }
      normalizedLogicId = normalizeNodeId(logicId) || logicId;
      conds = extracted.failed[logicId] || [];
      failedByNodeId[normalizedLogicId] = conds.slice();
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
        } else if (failedByNodeId[nodeId] && failedByNodeId[nodeId].length > 0) {
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
      if (failedByNodeId[nodeId] && failedByNodeId[nodeId].length > 0) {
        setNodeState(nodeId, 'blocked');
      } else {
        state = deriveComponentState(value, !!blockedInputNodes[nodeId]);
        setNodeState(nodeId, state);
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

  function hideNodeFaultButton(force) {
    if (!nodeFaultBtn) {
      return;
    }

    if (!force && currentFaultMenuNodeId) {
      return;
    }

    hoveredFaultNodeId = null;
    nodeFaultBtn.hidden = true;
    nodeFaultBtn.removeAttribute('data-node-id');
    nodeFaultBtn.classList.remove('is-active');
  }

  function hideNodeFaultMenu() {
    currentFaultMenuNodeId = null;
    if (!nodeFaultMenu) {
      return;
    }

    nodeFaultMenu.hidden = true;
    nodeFaultMenu.innerHTML = '';
    nodeFaultMenu.removeAttribute('data-node-id');
  }

  function renderNodeFaultMenu(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var options = getFaultTypeOptionsForNode(normalizedNodeId);
    var selectedFaultType = activeFaults.get(normalizedNodeId);
    var html = [];
    var i;
    var faultType;
    var faultDef;

    if (!nodeFaultMenu || !normalizedNodeId || options.length === 0) {
      return;
    }

    if (selectedFaultType) {
      html.push(
        '<button type="button" data-remove-fault="' + normalizedNodeId + '">' +
        '移除 ' + escHtml(getFaultNodeLabel(normalizedNodeId)) + ' 故障' +
        '</button>'
      );
    }

    for (i = 0; i < options.length; i += 1) {
      faultType = options[i];
      faultDef = FAULT_TYPES[faultType];
      html.push(
        '<button type="button" ' +
        'data-node-fault-type="' + faultType + '" ' +
        'data-node-id="' + normalizedNodeId + '" ' +
        'class="' + (selectedFaultType === faultType ? 'is-selected' : '') + '">' +
        escHtml(faultDef.icon + ' ' + faultDef.label) +
        '</button>'
      );
    }

    nodeFaultMenu.innerHTML = html.join('');
    nodeFaultMenu.setAttribute('data-node-id', normalizedNodeId);
  }

  function showNodeFaultMenu(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var anchor = resolveNodeAnchor(normalizedNodeId);

    if (!nodeFaultMenu || !normalizedNodeId || !anchor) {
      return;
    }

    renderNodeFaultMenu(normalizedNodeId);
    currentFaultMenuNodeId = normalizedNodeId;
    nodeFaultMenu.hidden = false;
    positionFloatingMenu(nodeFaultMenu, anchor);
  }

  function toggleNodeFaultMenu(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);

    if (!normalizedNodeId) {
      return;
    }

    if (currentFaultMenuNodeId === normalizedNodeId && nodeFaultMenu && !nodeFaultMenu.hidden) {
      hideNodeFaultMenu();
      hideNodeFaultButton(true);
      return;
    }

    showNodeFaultMenu(normalizedNodeId);
  }

  function handleNodeHover(nodeId, event) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var anchor;

    if (!isFaultUiEnabled() || !normalizedNodeId || getFaultTypeOptionsForNode(normalizedNodeId).length === 0) {
      hideNodeFaultButton(true);
      return;
    }

    anchor = resolveNodeAnchor(normalizedNodeId, event && event.target);
    if (!anchor || !nodeFaultBtn) {
      return;
    }

    hoveredFaultNodeId = normalizedNodeId;
    nodeFaultBtn.hidden = false;
    nodeFaultBtn.setAttribute('data-node-id', normalizedNodeId);
    nodeFaultBtn.classList.toggle('is-active', activeFaults.has(normalizedNodeId));
    positionFloatingButton(nodeFaultBtn, anchor);
  }

  function updateChainWithFaults() {
    var nodes = document.querySelectorAll('.canvas-wrapper [data-node]');
    var i;

    for (i = 0; i < nodes.length; i += 1) {
      nodes[i].classList.remove('is-faulted');
      nodes[i].removeAttribute('data-fault-type');
    }

    if (!isFaultUiEnabled()) {
      if (nodeFaultBtn) {
        nodeFaultBtn.classList.remove('is-active');
      }
      return;
    }

    activeFaults.forEach(function(faultType, nodeId) {
      var els = document.querySelectorAll('.canvas-wrapper [data-node="' + nodeId + '"]');
      var j;

      for (j = 0; j < els.length; j += 1) {
        els[j].classList.add('is-faulted');
        els[j].setAttribute('data-fault-type', faultType);
      }
    });

    if (nodeFaultBtn && nodeFaultBtn.getAttribute('data-node-id')) {
      nodeFaultBtn.classList.toggle(
        'is-active',
        activeFaults.has(nodeFaultBtn.getAttribute('data-node-id'))
      );
    }
  }

  function faultBarShouldBeVisible() {
    return isFaultUiEnabled() && (isFaultBarExpanded || activeFaults.size > 0);
  }

  function renderFaultPresetsMenu() {
    var html = [];
    var i;
    var preset;

    if (!faultPresetsMenu) {
      return;
    }

    for (i = 0; i < FAULT_PRESETS.length; i += 1) {
      preset = FAULT_PRESETS[i];
      html.push(
        '<button type="button" data-fault-preset="' + preset.id + '">' +
        escHtml(preset.label) +
        '</button>'
      );
    }

    faultPresetsMenu.innerHTML = html.join('');
  }

  function toggleFaultBar(forceExpanded) {
    if (!isFaultUiEnabled()) {
      isFaultBarExpanded = false;
      renderFaultBar();
      return;
    }

    if (typeof forceExpanded === 'boolean') {
      isFaultBarExpanded = forceExpanded;
    } else {
      isFaultBarExpanded = !isFaultBarExpanded;
    }

    renderFaultBar();
  }

  function renderFaultBar() {
    var serializedFaults = serializeActiveFaults();
    var html = [];
    var i;
    var faultItem;
    var isVisible = faultBarShouldBeVisible();

    if (faultBar) {
      faultBar.hidden = !isVisible;
    }

    if (faultToggleBtn) {
      faultToggleBtn.setAttribute('aria-expanded', isVisible ? 'true' : 'false');
      faultToggleBtn.classList.toggle('has-active-faults', serializedFaults.length > 0);
      faultToggleBtn.title = isVisible ? '收起故障注入栏' : '展开故障注入栏';
      faultToggleBtn.setAttribute('aria-label', isVisible ? '收起故障注入栏' : '展开故障注入栏');
      faultToggleBtn.disabled = faultUiBusy || !isFaultUiEnabled();
    }

    if (faultPills) {
      if (serializedFaults.length === 0) {
        faultPills.innerHTML = '<span class="truth-chip is-muted">未注入故障</span>';
      } else {
        for (i = 0; i < serializedFaults.length; i += 1) {
          faultItem = serializedFaults[i];
          html.push(
            '<div class="fault-pill">' +
            '<span class="fault-pill-label">' +
            escHtml(getFaultDisplayLabel(faultItem.node_id, faultItem.fault_type)) +
            '</span>' +
            '<button type="button" ' +
            'data-remove-fault="' + faultItem.node_id + '" ' +
            'aria-label="移除 ' + escHtml(getFaultDisplayLabel(faultItem.node_id, faultItem.fault_type)) + '"' +
            '>×</button>' +
            '</div>'
          );
        }
        faultPills.innerHTML = html.join('');
      }
    }

    if (faultClearBtn) {
      faultClearBtn.disabled = faultUiBusy || serializedFaults.length === 0;
    }

    if (!isVisible && faultPresetsMenu) {
      faultPresetsMenu.hidden = true;
      if (faultPresetsBtn) {
        faultPresetsBtn.setAttribute('aria-expanded', 'false');
      }
    }
  }

  function applyFaultPreset(presetId) {
    var i;
    var j;
    var preset;

    for (i = 0; i < FAULT_PRESETS.length; i += 1) {
      if (FAULT_PRESETS[i].id === presetId) {
        preset = FAULT_PRESETS[i];
        break;
      }
    }

    if (!preset) {
      return;
    }

    for (j = 0; j < preset.faults.length; j += 1) {
      activeFaults.set(preset.faults[j].nodeId, preset.faults[j].faultType);
    }

    renderFaultBar();
    updateChainWithFaults();
    faultPresetsMenu.hidden = true;
    if (faultPresetsBtn) {
      faultPresetsBtn.setAttribute('aria-expanded', 'false');
    }
    triggerFaultReevaluation();
  }

  function triggerFaultReevaluation() {
    var basePayload;

    if (!isFaultUiEnabled()) {
      return Promise.resolve(null);
    }

    basePayload = copyObject(
      lastTruthPayloadBySystem['thrust-reverser'] || buildDefaultLeverPayload('故障重评估', 'thrust-reverser')
    );
    basePayload.prompt = '故障重评估';
    basePayload.system_id = 'thrust-reverser';

    setFaultUiBusy(true);
    return _sendLeverSnapshot(basePayload)
      .then(function(result) {
        setFaultUiBusy(false);
        renderFaultBar();
        return result;
      })
      .catch(function(err) {
        setFaultUiBusy(false);
        renderRequestFailure(err);
        return null;
      });
  }

  function injectFault(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);
    var faultType = arguments.length > 1 ? arguments[1] : null;
    var options = getFaultTypeOptionsForNode(normalizedNodeId);

    if (!normalizedNodeId || options.length === 0) {
      return;
    }

    if (!faultType) {
      if (options.length === 1) {
        faultType = options[0];
      } else {
        showNodeFaultMenu(normalizedNodeId);
        return;
      }
    }

    if (options.indexOf(faultType) === -1) {
      return;
    }

    activeFaults.set(normalizedNodeId, faultType);
    hideNodeFaultMenu();
    renderFaultBar();
    updateChainWithFaults();
    triggerFaultReevaluation();
  }

  function removeFault(nodeId) {
    var normalizedNodeId = normalizeNodeId(nodeId);

    if (!normalizedNodeId || !activeFaults.has(normalizedNodeId)) {
      return;
    }

    activeFaults.delete(normalizedNodeId);
    if (currentFaultMenuNodeId === normalizedNodeId) {
      hideNodeFaultMenu();
    }
    renderFaultBar();
    updateChainWithFaults();
    triggerFaultReevaluation();
  }

  function clearAllFaults() {
    if (activeFaults.size === 0) {
      return;
    }

    activeFaults.clear();
    hideNodeFaultMenu();
    renderFaultBar();
    updateChainWithFaults();
    triggerFaultReevaluation();
  }

  function findFaultTargetFromEvent(target) {
    var targetEl;
    var nodeId;

    if (!target || !target.closest || !isFaultUiEnabled()) {
      return null;
    }

    targetEl = target.closest('[data-node], [data-node-label]');
    if (!targetEl || (nodeFaultBtn && nodeFaultBtn.contains(targetEl)) || (nodeFaultMenu && nodeFaultMenu.contains(targetEl))) {
      return null;
    }

    if (targetEl.hasAttribute('data-node')) {
      nodeId = targetEl.getAttribute('data-node');
    } else {
      nodeId = targetEl.getAttribute('data-node-label');
    }

    nodeId = normalizeNodeId(nodeId);
    if (!nodeId || getFaultTypeOptionsForNode(nodeId).length === 0) {
      return null;
    }

    return {
      nodeId: nodeId,
      element: resolveNodeAnchor(nodeId, target),
    };
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
  renderFaultPresetsMenu();
  renderFaultBar();

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

    if (e.key === 'Escape') {
      hideNodeFaultMenu();
      if (faultPresetsMenu) {
        faultPresetsMenu.hidden = true;
      }
      if (faultPresetsBtn) {
        faultPresetsBtn.setAttribute('aria-expanded', 'false');
      }
    }
  });

  document.addEventListener('click', function(e) {
    if (
      faultPresetsMenu &&
      !faultPresetsMenu.hidden &&
      !faultPresetsMenu.contains(e.target) &&
      (!faultPresetsBtn || !faultPresetsBtn.contains(e.target))
    ) {
      faultPresetsMenu.hidden = true;
      if (faultPresetsBtn) {
        faultPresetsBtn.setAttribute('aria-expanded', 'false');
      }
    }

    if (
      nodeFaultMenu &&
      !nodeFaultMenu.hidden &&
      !nodeFaultMenu.contains(e.target) &&
      (!nodeFaultBtn || !nodeFaultBtn.contains(e.target))
    ) {
      hideNodeFaultMenu();
      hideNodeFaultButton(true);
    }
  });

  if (systemSelect) {
    systemSelect.addEventListener('change', function() {
      currentSystem = systemSelect.value;
      hideNodeFaultMenu();
      hideNodeFaultButton(true);
      syncSystemChrome();
      resetCanvasState();
      resetTruthEvalBar();
      renderFaultBar();
      updateChainWithFaults();
    });
  }

  if (faultToggleBtn) {
    faultToggleBtn.addEventListener('click', function() {
      toggleFaultBar();
    });
  }

  if (faultPresetsBtn) {
    faultPresetsBtn.addEventListener('click', function(e) {
      if (!faultPresetsMenu) {
        return;
      }

      e.preventDefault();
      faultPresetsMenu.hidden = !faultPresetsMenu.hidden;
      faultPresetsBtn.setAttribute('aria-expanded', faultPresetsMenu.hidden ? 'false' : 'true');
    });
  }

  if (faultClearBtn) {
    faultClearBtn.addEventListener('click', function() {
      clearAllFaults();
    });
  }

  if (faultPills) {
    faultPills.addEventListener('click', function(e) {
      var target = e.target.closest('[data-remove-fault]');

      if (!target) {
        return;
      }

      removeFault(target.getAttribute('data-remove-fault'));
    });
  }

  if (faultPresetsMenu) {
    faultPresetsMenu.addEventListener('click', function(e) {
      var target = e.target.closest('[data-fault-preset]');

      if (!target) {
        return;
      }

      applyFaultPreset(target.getAttribute('data-fault-preset'));
    });
  }

  if (nodeFaultBtn) {
    nodeFaultBtn.addEventListener('click', function(e) {
      var nodeId = nodeFaultBtn.getAttribute('data-node-id');

      e.preventDefault();
      if (!nodeId) {
        return;
      }
      toggleNodeFaultMenu(nodeId);
    });
  }

  if (nodeFaultMenu) {
    nodeFaultMenu.addEventListener('click', function(e) {
      var removeTarget = e.target.closest('[data-remove-fault]');
      var injectTarget = e.target.closest('[data-node-fault-type]');

      if (removeTarget) {
        removeFault(removeTarget.getAttribute('data-remove-fault'));
        return;
      }

      if (!injectTarget) {
        return;
      }

      injectFault(
        injectTarget.getAttribute('data-node-id'),
        injectTarget.getAttribute('data-node-fault-type')
      );
    });
  }

  if (canvasStage) {
    canvasStage.addEventListener('mousemove', function(e) {
      var faultTarget;

      if (
        (nodeFaultBtn && nodeFaultBtn.contains(e.target)) ||
        (nodeFaultMenu && nodeFaultMenu.contains(e.target))
      ) {
        return;
      }

      faultTarget = findFaultTargetFromEvent(e.target);
      if (!faultTarget || !faultTarget.element) {
        if (!currentFaultMenuNodeId) {
          hideNodeFaultButton(true);
        }
        return;
      }

      handleNodeHover(faultTarget.nodeId, e);
    });

    canvasStage.addEventListener('mouseleave', function(e) {
      if (
        (nodeFaultBtn && nodeFaultBtn.contains(e.relatedTarget)) ||
        (nodeFaultMenu && nodeFaultMenu.contains(e.relatedTarget))
      ) {
        return;
      }
      hideNodeFaultMenu();
      hideNodeFaultButton(true);
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
      renderFaultBar();
      updateChainWithFaults();

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

  if (chatMessages) {
    chatMessages.addEventListener('click', function(e) {
      var target = e.target.closest('.node-ref');

      if (!target) {
        return;
      }

      highlightNodeReference(target.getAttribute('data-ref'));
    });

    chatMessages.addEventListener('keydown', function(e) {
      var target = e.target;

      if (!target || !target.classList || !target.classList.contains('node-ref')) {
        return;
      }

      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        highlightNodeReference(target.getAttribute('data-ref'));
      }
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
          fault_injections: serializeActiveFaults(),
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

    payload = buildDefaultLeverPayload(text, systemId);

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
      _sendLeverSnapshot(payload)
        .then(function(result) {
          var data = result.snapshotData;
          var requestPayload = result.requestPayload;
          var nodeStates = result.nodeStates;
          var explainPayload;
          var fallbackText = result.fallbackText;

          // Step 2: Call MiniMax LLM for contextual explanation (1-2s)
          explainPayload = buildExplainPayload(text, systemId, requestPayload, {
            lever_snapshot: data,
            node_states: nodeStates,
            fault_injections: serializeActiveFaults(),
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
  renderFaultBar();
  updateChainWithFaults();
  setFabTooltip('展开对话');

  if (logicDiagram && currentSystem === 'thrust-reverser') {
    setTruthBadge('idle', '空闲');
  }

  if (chatInput) {
    chatInput.focus();
  }
})();
