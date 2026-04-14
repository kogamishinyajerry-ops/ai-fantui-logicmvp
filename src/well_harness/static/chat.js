/* ── chat.js — Minimal chat shell for AI FANTUI Logic ── */

(function() {
  // ── State ──
  var currentSystem = 'thrust-reverser';
  var chatMessages = document.getElementById('chat-messages');
  var chatInput = document.getElementById('chat-input');
  var sendBtn = document.getElementById('chat-send-btn');
  var fileUpload = document.getElementById('chat-file-upload');
  var sidebar = document.getElementById('chat-sidebar');
  var sidebarToggle = document.getElementById('sidebar-toggle');
  var sidebarClose = document.getElementById('sidebar-close');
  var systemSelect = document.getElementById('chat-system-select');
  var sidebarCurrentSystem = document.getElementById('sidebar-current-system');
  var logicDiagram = document.getElementById('logic-diagram');
  var guidedDemoBtn = document.getElementById('chat-guided-demo-btn');

  // System labels
  var SYSTEM_LABELS = {
    'thrust-reverser': 'Thrust Reverser (反推)',
    'landing-gear': 'Landing Gear (起落架)',
    'bleed-air': 'Bleed Air Valve (引气)',
    efds: 'Emergency Flare (干扰弹)',
  };

  // ── Helpers ──
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function addMessage(role, text) {
    if (!chatMessages) {
      return;
    }

    var avatar = role === 'ai' ? '🤖' : '👤';
    var msg = document.createElement('article');
    msg.className = 'chat-message chat-message-' + (role === 'ai' ? 'ai' : 'user');
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
    sendBtn.textContent = loading ? '...' : '▶';
  }

  // ── Sidebar toggle ──
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
    });
  }

  if (sidebarClose && sidebar) {
    sidebarClose.addEventListener('click', function() {
      sidebar.classList.add('collapsed');
    });
  }

  // ── System switch ──
  if (systemSelect) {
    systemSelect.addEventListener('change', function() {
      currentSystem = systemSelect.value;
      if (sidebarCurrentSystem) {
        sidebarCurrentSystem.textContent = SYSTEM_LABELS[currentSystem] || currentSystem;
      }
      updateLogicDiagram();
    });
  }

  function updateLogicDiagram() {
    if (!logicDiagram) {
      return;
    }

    // Show system name as placeholder — in Phase 2 this will render the actual SVG
    var label = SYSTEM_LABELS[currentSystem] || currentSystem;
    logicDiagram.innerHTML =
      '<div style="text-align:center">' +
      '<div style="font-size:1.2rem;margin-bottom:6px">⚙️</div>' +
      '<div style="color:var(--accent-cyan);font-size:0.85rem;font-weight:600">' + escHtml(label) + '</div>' +
      '<div style="color:var(--text-muted);font-size:0.75rem;margin-top:4px">在下方输入问题，或切换系统查看不同链路</div>' +
      '</div>';
  }

  // ── Guided Demo ──
  if (guidedDemoBtn) {
    guidedDemoBtn.addEventListener('click', function() {
      addMessage('ai', '▶ 启动 Guided Demo，正在切换到 Thrust Reverser 系统...');

      if (systemSelect) {
        systemSelect.value = 'thrust-reverser';
      }
      currentSystem = 'thrust-reverser';
      if (sidebarCurrentSystem) {
        sidebarCurrentSystem.textContent = SYSTEM_LABELS[currentSystem] || currentSystem;
      }
      updateLogicDiagram();

      // Run the guided demo sequence (simplified version)
      setTimeout(function() {
        addMessage('ai', '步骤 1：设置 TRA = -14°（达到反推门槛）');
      }, 1500);
      setTimeout(function() {
        addMessage('ai', '步骤 2：设置 RA = 0ft（off-ground，altitude gate = false）');
      }, 3000);
      setTimeout(function() {
        addMessage('ai', '✅ SW1 已 latch！logic1 链路激活。\n现在尝试把 RA 改大到 10ft，看看 altitude gate 如何阻止 logic1。');
      }, 5000);
    });
  }

  // ── Shortcut buttons ──
  Array.prototype.forEach.call(document.querySelectorAll('.chat-shortcut-btn'), function(btn) {
    btn.addEventListener('click', function() {
      var prompt = btn.getAttribute('data-prompt');
      if (prompt && chatInput) {
        chatInput.value = prompt;
        chatInput.focus();
      }
    });
  });

  // ── File upload ──
  if (fileUpload) {
    fileUpload.addEventListener('change', function(e) {
      var files = e.target && e.target.files;
      var file = files && files[0];
      if (!file) {
        return;
      }

      var reader = new FileReader();
      reader.onload = function(ev) {
        var text = (ev.target && ev.target.result) || '';
        addMessage('user', '📎 ' + file.name + ' (' + Math.round(String(text).length / 1024) + 'KB)');
        addMessage('ai', '已收到文档，正在分析...\n（Phase 2: AI 文档分析将在这里集成）');
        // Auto-send to demo analyzer in Phase 2
      };
      reader.readAsText(file);
      fileUpload.value = '';
    });
  }

  /* ── Response formatters ── */
  function formatLeverSnapshotAnswer(data, payload) {
    if (!data) {
      return '⚠️ 未收到有效响应，请检查输入参数。';
    }

    var ev = data.truth_evaluation || null;
    var activeIds = [];
    var failed = {};

    if (ev) {
      activeIds = ev.active_logic_node_ids || [];
      failed = ev.failed_conditions || {};
    } else if (data.logic) {
      ['logic1', 'logic2', 'logic3', 'logic4'].forEach(function(nodeId) {
        var logicNode = data.logic[nodeId];
        if (!logicNode) {
          return;
        }

        if (logicNode.active) {
          activeIds.push(nodeId);
        }

        if (logicNode.failed_conditions && logicNode.failed_conditions.length > 0) {
          failed[nodeId] = logicNode.failed_conditions;
        }
      });
    } else {
      return '⚠️ 未收到有效响应，请检查输入参数。';
    }

    var lines = [];
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
      for (var nodeId in failed) {
        if (!Object.prototype.hasOwnProperty.call(failed, nodeId)) {
          continue;
        }
        var conds = failed[nodeId] || [];
        if (conds.length > 0) {
          lines.push('  ' + nodeId + ': ' + conds.join(', '));
        }
      }
    }

    if (data.summary) {
      lines.push('');
      lines.push('摘要: ' + data.summary);
    }

    lines.push('');
    lines.push('详细链路:');
    lines.push('  SW1 → L1 → SW2 → L2(540V) → L3(EEC+PLS+PDU) → VDT90 → L4/THR_LOCK');
    lines.push('');
    lines.push('💡 尝试修改上方参数（如把RA改大到10ft）观察链路变化。');

    return lines.join('\n');
  }

  function formatDemoAnswer(data) {
    if (!data) {
      return '⚠️ 未收到有效响应。';
    }
    if (data.error) {
      return '⚠️ 请求失败: ' + (data.message || data.error);
    }

    var answer = data.answer || data.reasoning || JSON.stringify(data).substring(0, 300);
    if (typeof answer !== 'string') {
      answer = String(answer);
    }
    return answer.substring(0, 800);
  }

  // ── Send message ──
  function handleSend() {
    if (!chatInput) {
      return;
    }

    var text = chatInput.value.trim();
    if (!text) {
      return;
    }

    addMessage('user', text);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    setInputLoading(true);

    // ── Real API integration ──
    // Detect intent and call the appropriate API
    var lowerText = text.toLowerCase();
    var systemId = currentSystem;

    var payload = {
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

    var useLeverSnapshot = false;

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
    } else if (lowerText.includes('tra') && (lowerText.includes('拉') || lowerText.includes('-14') || lowerText.includes('-20') || lowerText.includes('阈值'))) {
      var traMatch = text.match(/(-?\d+)[°]?/);
      if (traMatch) {
        payload.tra_deg = parseFloat(traMatch[1]);
      } else {
        payload.tra_deg = -14.0;
      }
      useLeverSnapshot = true;
    } else if (lowerText.includes('altitude') || lowerText.includes('ra ') || lowerText.includes('radio')) {
      var raMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:ft|英尺)/);
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
    } else if (lowerText.includes('l3') || lowerText.includes('eec') || lowerText.includes('pls') || lowerText.includes('pdu')) {
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
      addMessage('ai', '▶ 点击左侧"Guided Demo — 带我走一遍"，我会带你一步一步看完整的反推链路激活过程。');
      setInputLoading(false);
      chatInput.focus();
      return;
    } else if (systemId !== 'thrust-reverser') {
      fetch('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function(r) {
          return r.json().then(function(data) {
            if (!r.ok) {
              throw new Error((data && (data.message || data.error)) || 'request_failed');
            }
            return data;
          });
        })
        .then(function(data) {
          addMessage('ai', formatDemoAnswer(data));
          setInputLoading(false);
          chatInput.focus();
        })
        .catch(function(err) {
          addMessage('ai', '⚠️ 请求失败: ' + err.message);
          setInputLoading(false);
          chatInput.focus();
        });
      return;
    } else {
      payload.tra_deg = -14.0;
      useLeverSnapshot = true;
    }

    if (useLeverSnapshot) {
      fetch('/api/lever-snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function(r) {
          return r.json().then(function(data) {
            if (!r.ok) {
              throw new Error((data && (data.message || data.error)) || 'request_failed');
            }
            return data;
          });
        })
        .then(function(data) {
          addMessage('ai', formatLeverSnapshotAnswer(data, payload));
          setInputLoading(false);
          chatInput.focus();
        })
        .catch(function(err) {
          addMessage('ai', '⚠️ 请求失败: ' + err.message);
          setInputLoading(false);
          chatInput.focus();
        });
    } else {
      fetch('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function(r) {
          return r.json().then(function(data) {
            if (!r.ok) {
              throw new Error((data && (data.message || data.error)) || 'request_failed');
            }
            return data;
          });
        })
        .then(function(data) {
          addMessage('ai', formatDemoAnswer(data));
          setInputLoading(false);
          chatInput.focus();
        })
        .catch(function(err) {
          addMessage('ai', '⚠️ 请求失败: ' + err.message);
          setInputLoading(false);
          chatInput.focus();
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

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
  }

  // ── Initialize ──
  updateLogicDiagram();
  if (sidebarCurrentSystem) {
    sidebarCurrentSystem.textContent = SYSTEM_LABELS[currentSystem] || currentSystem;
  }
  if (chatInput) {
    chatInput.focus();
  }
})();
