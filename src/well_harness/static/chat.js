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

    // Simple intent detection
    var lowerText = text.toLowerCase();
    var response = '';

    if (lowerText.includes('tls') || lowerText.includes('失效') || lowerText.includes('failure')) {
      response = 'TLS（Thrust Reverser Latch System，115PSI 液压锁）在以下条件下失效：\n· 液压压力 < 115PSI\n· Reverser Inhibited = True\n· TRA 未达到 -14° 门槛\n\n失效后 SW1 断开，链路卡在 L1，后续 SW2/L3/VDT90 均不激活。';
    } else if (lowerText.includes('vdt') || lowerText.includes('90')) {
      response = 'VDT90（Variable Displacement Table）激活条件：\n· L3 必须已激活（SW1 + SW2 + EEC + PLS + PDU 全部到位）\n· deploy_position >= 90%\n\nVDT90 激活后驱动 L4（THR_LOCK），最终释放反推锁。manual_feedback_override 模式可绕过 SW1 直接驱动 VDT90。';
    } else if (lowerText.includes('throttle') || lowerText.includes('lock') || lowerText.includes('thr_lock')) {
      response = 'Throttle Lock（THR_LOCK）释放链路：\nL4 → THR_LOCK cmd → 解锁反推装置\n\n常见阻塞原因：\n1. SW1 未闭合（TRA < -14°）\n2. SW2 未闭合（L1 未解锁）\n3. L3 未激活（EEC/PLS/PDU 任一未就绪）\n4. VDT90 < 90%（manual override 可绕过）\n5. Reverser Inhibited = True';
    } else if (lowerText.includes('tra') || lowerText.includes('阈值') || lowerText.includes('threshold')) {
      response = 'TRA（Thrust Reverser Actuation）关键阈值：\n· -14°：SW1 闭合门槛（精确值，-13.9° 不够）\n· -20°：最深作动位置\n\nTRA 拉到 -14° 后：SW1 latch → L1 → TLS 解锁 → SW2 → L2(540V) → L3(EEC+PLS+PDU) → VDT90 → L4/THR_LOCK';
    } else if (lowerText.includes('l3') || lowerText.includes('eec') || lowerText.includes('pls') || lowerText.includes('pdu')) {
      response = 'L3（Logic Node 3）是扇出节点，同时激活三个下游命令：\n· EEC：Electronic Engine Controller，发动机控制电脑\n· PLS：Pressure Limit Switch，压力限制开关\n· PDU：Power Drive Unit，电机驱动单元\n\n三路全部就绪后，VDT90 才能被激活。';
    } else if (lowerText.includes('altitude') || lowerText.includes('ra ') || lowerText.includes('radio')) {
      response = 'Altitude Gate 逻辑：\naltitude_gate = aircraft_on_ground OR radio_altitude_ft >= 7.0\n\n当 altitude_gate = True 时，altitude 条件会阻止 logic1 激活。\n\n关键：on_ground=True 且 altitude=0ft → altitude_gate=True → altitude 不阻止（因为已经在地面）。\non_ground=False 且 altitude=0ft → altitude_gate=False → altitude 不阻止（in-air 但低于 7ft）。';
    } else if (lowerText.includes('guided') || lowerText.includes('demo') || lowerText.includes('带我走')) {
      response = '▶ 点击左侧"Guided Demo — 带我走一遍"，我会带你一步一步看完整的反推链路激活过程。';
    } else {
      response = '我理解了。\n\n当前支持的分析类型：\n· 链路解释（TLS/VDT90/THR_LOCK/L3/EEC/PLS/PDU）\n· 阈值分析（TRA/Altitude/N1K）\n· 故障诊断（失效条件/阻塞原因）\n· Guided Demo（左侧按钮）\n\nPhase 2 将支持上传文档后自动分析规格。';
    }

    // Simulate AI thinking delay
    setTimeout(function() {
      addMessage('ai', response);
      setInputLoading(false);
      if (chatInput) {
        chatInput.focus();
      }
    }, 400 + Math.random() * 300);
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
