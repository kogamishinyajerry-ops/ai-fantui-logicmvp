/* C919 E-TRAS Logic Workstation — JS runtime.
 *
 * Architecture: stateless signal-level evaluation.
 * - User moves inputs (TRA slider / N1K / lock toggles / timing inputs).
 * - Debounced → POST /api/system-snapshot with system_id=c919-etras + snapshot.
 * - Backend adapter returns truth_evaluation (active logic ids + asserted values).
 * - Render: HUD values, SVG node states, output cards, overall status banner.
 *
 * Not stateful: no tick loop, no state machine replay. For dynamic state
 * machine visualization, use the :9191 simulation panel.
 */
(function () {
  "use strict";

  const API_URL = "/api/system-snapshot";
  const SYSTEM_ID = "c919-etras";
  const DEBOUNCE_MS = 120;

  // ═══════════ Input DOM references ═══════════
  const $ = (id) => document.getElementById(id);

  const inputs = {
    tra:                 $("etras-tra-lever"),
    n1k:                 $("etras-n1k"),
    engineRunning:       $("etras-engine-running"),
    trInhibited:         $("etras-tr-inhibited"),
    overTempFault:       $("etras-over-temp-fault"),
    trcuPowerOn:         $("etras-trcu-power-on"),
    vdtValid:            $("etras-vdt-valid"),
    lgcu1Value:          $("etras-lgcu1-value"),
    lgcu1Valid:          $("etras-lgcu1-valid"),
    lgcu2Value:          $("etras-lgcu2-value"),
    lgcu2Valid:          $("etras-lgcu2-valid"),
    tlsAUnlocked:        $("etras-tls-a-unlocked"),
    tlsBUnlocked:        $("etras-tls-b-unlocked"),
    plsALocked:          $("etras-pls-a-locked"),
    plsBLocked:          $("etras-pls-b-locked"),
    leftPylonAUnlocked:  $("etras-left-pylon-a-unlocked"),
    leftPylonBUnlocked:  $("etras-left-pylon-b-unlocked"),
    rightPylonAUnlocked: $("etras-right-pylon-a-unlocked"),
    rightPylonBUnlocked: $("etras-right-pylon-b-unlocked"),
    trPosition:          $("etras-tr-position"),
    comm2Timer:          $("etras-comm2-timer"),
    unlockConfirm:       $("etras-unlock-confirm"),
    deployedConfirm:     $("etras-deployed-confirm"),
    stowedConfirm:       $("etras-stowed-confirm"),
    prevCmd3:            $("etras-prev-cmd3"),
    trWow:               $("etras-tr-wow"),
  };

  // ═══════════ Output DOM references ═══════════
  const readouts = {
    traValue:         $("etras-tra-value"),
    traZone:          $("etras-tra-zone"),
    n1kValue:         $("etras-n1k-value"),
    trPositionValue:  $("etras-tr-position-value"),
    statusBadge:      $("etras-status-badge"),
    statusSummary:    $("etras-status-summary"),
    completionFlag:   $("etras-completion-flag"),
    hudMlgWow:        $("hud-mlg-wow"),
    hudTrWow:         $("hud-tr-wow"),
    hudSwitches:      $("hud-switches"),
    hudLockState:     $("hud-lock-state"),
    hudCmd2Timer:     $("hud-cmd2-timer"),
    hudCmd3Latch:     $("hud-cmd3-latch"),
    hudCmd3Enable:    $("hud-cmd3-enable"),
    hudTrPosition:    $("hud-tr-position"),
    hudN1k:           $("hud-n1k"),
    hudFaults:        $("hud-faults"),
    outSinglePhase:   $("output-single-phase"),
    outThreePhase:    $("output-three-phase"),
    outFadecDeploy:   $("output-fadec-deploy"),
    outFadecStow:     $("output-fadec-stow"),
    outSinglePhaseV:  $("output-single-phase-value"),
    outThreePhaseV:   $("output-three-phase-value"),
    outFadecDeployV:  $("output-fadec-deploy-value"),
    outFadecStowV:    $("output-fadec-stow-value"),
    presetStatus:     $("etras-preset-status"),
    probabilityNodeList: $("etras-probability-node-list"),
    simTrials:        $("etras-sim-trials"),
    simSeed:          $("etras-sim-seed"),
    simScope:         $("etras-sim-scope"),
    simRunButton:     $("etras-run-simulation"),
    bulkProbability:  $("etras-bulk-probability"),
    bulkApplyButton:  $("etras-apply-bulk-probability"),
    simSuccessRate:   $("etras-sim-success-rate"),
    simFailureCount:  $("etras-sim-failure-count"),
    simAnalyticalRate: $("etras-sim-analytical-rate"),
    simScopeLabel:    $("etras-sim-scope-label"),
    simTopCauses:     $("etras-sim-top-causes"),
    simFailureSamples: $("etras-sim-failure-samples"),
  };

  const chainSvg = document.getElementById("etras-logic-chain");

  const RELIABILITY_NODES = [
    { id: "mlg_wow", kind: "INPUT", label: "mlg_wow · WOW 仲裁", normalProbability: 0.9990 },
    { id: "tr_wow", kind: "INPUT", label: "tr_wow · 2.25s SET", normalProbability: 0.9990 },
    { id: "atltla", kind: "INPUT", label: "atltla · SW1", normalProbability: 0.9990 },
    { id: "tra_deg", kind: "INPUT", label: "tra_deg · 油门角度", normalProbability: 0.9990 },
    { id: "tr_inhibited", kind: "INPUT", label: "tr_inhibited · 抑制位", normalProbability: 0.9990 },
    { id: "ln_eicu_cmd2", kind: "LOGIC", label: "EICU_CMD2 · 单相解锁", normalProbability: 0.9990 },
    { id: "eicu_cmd2", kind: "OUTPUT", label: "eicu_cmd2 · 1-φ unlock", normalProbability: 0.9990 },
    { id: "apwtla", kind: "INPUT", label: "apwtla · SW2", normalProbability: 0.9990 },
    { id: "ln_eicu_cmd3", kind: "LOGIC", label: "EICU_CMD3 · 三相 TRCU", normalProbability: 0.9990 },
    { id: "eicu_cmd3", kind: "OUTPUT", label: "eicu_cmd3 · 3-φ TRCU", normalProbability: 0.9990 },
    { id: "lock_state", kind: "INPUT", label: "lock_state · 锁聚合", normalProbability: 0.9990 },
    { id: "ln_tr_command3_enable", kind: "LOGIC", label: "TR_Command3_Enable", normalProbability: 0.9990 },
    { id: "tr_command3_enable", kind: "OUTPUT", label: "tr_command3_enable", normalProbability: 0.9990 },
    { id: "n1k_percent", kind: "INPUT", label: "n1k_percent · 转速", normalProbability: 0.9990 },
    { id: "tr_position_percent", kind: "INPUT", label: "tr_position_percent · VDT", normalProbability: 0.9990 },
    { id: "ln_fadec_deploy_command", kind: "LOGIC", label: "FADEC_Deploy · 展开命令", normalProbability: 0.9990 },
    { id: "fadec_deploy_command", kind: "OUTPUT", label: "fadec_deploy_command", normalProbability: 0.9990 },
    { id: "ln_fadec_stow_command", kind: "LOGIC", label: "FADEC_Stow · 收起命令", normalProbability: 0.9990 },
    { id: "fadec_stow_command", kind: "OUTPUT", label: "fadec_stow_command", normalProbability: 0.9990 },
  ];
  const RELIABILITY_NODE_BY_ID = new Map(RELIABILITY_NODES.map((node) => [node.id, node]));
  let lastEvaluationContext = { activeIds: new Set(), asserted: {} };

  // ═══════════ Helpers ═══════════
  function checked(el) { return !!(el && el.checked); }
  function numValue(el, fallback) {
    if (!el) return fallback;
    const v = parseFloat(el.value);
    return Number.isFinite(v) ? v : fallback;
  }

  function buildSnapshot() {
    return {
      tra_deg:                    numValue(inputs.tra, 0),
      n1k_percent:                numValue(inputs.n1k, 35),
      engine_running:             checked(inputs.engineRunning),
      tr_inhibited:               checked(inputs.trInhibited),
      lgcu1_mlg_wow_value:        checked(inputs.lgcu1Value),
      lgcu1_mlg_wow_valid:        checked(inputs.lgcu1Valid),
      lgcu2_mlg_wow_value:        checked(inputs.lgcu2Value),
      lgcu2_mlg_wow_valid:        checked(inputs.lgcu2Valid),
      tr_wow:                     checked(inputs.trWow),
      tls_ls_a_valid:             true,
      tls_ls_a_unlocked:          checked(inputs.tlsAUnlocked),
      tls_ls_b_valid:             true,
      tls_ls_b_unlocked:          checked(inputs.tlsBUnlocked),
      pls_ls_a_locked:            checked(inputs.plsALocked),
      pls_ls_b_locked:            checked(inputs.plsBLocked),
      left_pylon_ls_a_valid:      true,
      left_pylon_ls_a_unlocked:   checked(inputs.leftPylonAUnlocked),
      left_pylon_ls_b_valid:      true,
      left_pylon_ls_b_unlocked:   checked(inputs.leftPylonBUnlocked),
      right_pylon_ls_a_valid:     true,
      right_pylon_ls_a_unlocked:  checked(inputs.rightPylonAUnlocked),
      right_pylon_ls_b_valid:     true,
      right_pylon_ls_b_unlocked:  checked(inputs.rightPylonBUnlocked),
      apwtla:                     computeApwtla(numValue(inputs.tra, 0)),
      atltla:                     computeAtltla(numValue(inputs.tra, 0)),
      vdt_sensor_valid:           checked(inputs.vdtValid),
      e_tras_over_temp_fault:     checked(inputs.overTempFault),
      trcu_power_on:              checked(inputs.trcuPowerOn),
      tr_position_percent:        numValue(inputs.trPosition, 0),
      prev_eicu_cmd3:             checked(inputs.prevCmd3),
      comm2_timer_s:              numValue(inputs.comm2Timer, 0),
      lock_unlock_confirm_s:      numValue(inputs.unlockConfirm, 0),
      tr_position_deployed_confirm_s: numValue(inputs.deployedConfirm, 0),
      tr_stowed_locked_confirm_s: numValue(inputs.stowedConfirm, 2),
    };
  }

  // SW1: ATLTLA closes when TRA ∈ [-6.2, -1.4]
  function computeAtltla(tra) { return tra <= -1.4 && tra >= -6.2; }
  // SW2: APWTLA closes when TRA ∈ [-9.8, -5.0]
  function computeApwtla(tra) { return tra <= -5.0 && tra >= -9.8; }

  function zoneFromTra(tra) {
    if (tra <= -25)   return ["max-rev",  "MAX REV"];
    if (tra <= -11.74)return ["rev-idle", "REV IDLE"];
    if (tra <= -6.2)  return ["sw2",      "SW1+SW2"];
    if (tra <= -5.0)  return ["sw2",      "SW2 ONLY"];
    if (tra <= -1.4)  return ["sw1",      "SW1 ONLY"];
    if (tra < 0)      return ["fwd-idle", "FWD IDLE"];
    return ["fwd", "FWD"];
  }

  function formatBool(value) {
    if (value === true)  return "TRUE";
    if (value === false) return "false";
    return "—";
  }
  function formatPct(value, digits = 0) {
    if (typeof value !== "number") return "—";
    return value.toFixed(digits) + "%";
  }

  // ═══════════ Fetch + render pipeline ═══════════
  let pending = null;
  let inflight = false;
  let nextRequest = null;

  async function fetchEvaluation() {
    if (inflight) {
      nextRequest = true;
      return;
    }
    inflight = true;
    const snapshot = buildSnapshot();
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ system_id: SYSTEM_ID, snapshot }),
      });
      if (!response.ok) {
        console.warn("[c919-workstation] snapshot eval failed:", response.status);
        return;
      }
      const payload = await response.json();
      renderAll(payload, snapshot);
    } catch (err) {
      console.warn("[c919-workstation] fetch error:", err);
    } finally {
      inflight = false;
      if (nextRequest) {
        nextRequest = false;
        fetchEvaluation();
      }
    }
  }

  function scheduleFetch() {
    if (pending) clearTimeout(pending);
    pending = setTimeout(() => {
      pending = null;
      fetchEvaluation();
    }, DEBOUNCE_MS);
  }

  // ═══════════ Rendering ═══════════
  function renderAll(payload, snapshot) {
    const evaluation = payload.truth_evaluation || {};
    const asserted   = evaluation.asserted_component_values || {};
    const activeIds  = new Set(evaluation.active_logic_node_ids || []);
    const summary    = evaluation.summary || "";
    const completion = evaluation.completion_reached === true;
    lastEvaluationContext = { activeIds, asserted };

    renderLeverHud(snapshot);
    renderHud(asserted, snapshot);
    renderOutputs(asserted);
    renderChainSvg(activeIds, asserted);
    renderStatusBanner(summary, completion, asserted);
  }

  function renderLeverHud(snapshot) {
    if (readouts.traValue) readouts.traValue.textContent = snapshot.tra_deg.toFixed(1) + "°";
    if (readouts.n1kValue) readouts.n1kValue.textContent = snapshot.n1k_percent.toFixed(0) + "%";
    if (readouts.trPositionValue) readouts.trPositionValue.textContent = snapshot.tr_position_percent.toFixed(0) + "%";
    if (readouts.traZone) {
      const [zone, label] = zoneFromTra(snapshot.tra_deg);
      readouts.traZone.dataset.zone = zone;
      readouts.traZone.textContent = label;
    }
  }

  function renderHud(asserted, snapshot) {
    setHud(readouts.hudMlgWow, asserted.mlg_wow);
    setHud(readouts.hudTrWow,  asserted.tr_wow);
    if (readouts.hudSwitches) {
      const sw1 = asserted.atltla ? "SW1:ON" : "SW1:off";
      const sw2 = asserted.apwtla ? "SW2:ON" : "SW2:off";
      readouts.hudSwitches.textContent = `${sw1} · ${sw2}`;
      readouts.hudSwitches.dataset.flag = (asserted.atltla || asserted.apwtla) ? "true" : "false";
    }
    if (readouts.hudLockState) {
      readouts.hudLockState.textContent = asserted.lock_state || "—";
      readouts.hudLockState.dataset.flag = (asserted.lock_state === "UNLOCKED_CONFIRMED") ? "true" : "false";
    }
    if (readouts.hudCmd2Timer) {
      readouts.hudCmd2Timer.textContent = snapshot.comm2_timer_s.toFixed(1) + " / 30.0";
    }
    if (readouts.hudCmd3Latch) {
      readouts.hudCmd3Latch.textContent = snapshot.prev_eicu_cmd3 ? "latched" : "reset";
      readouts.hudCmd3Latch.dataset.flag = snapshot.prev_eicu_cmd3 ? "true" : "false";
    }
    setHud(readouts.hudCmd3Enable, asserted.tr_command3_enable);
    if (readouts.hudTrPosition) {
      const pct = typeof asserted.tr_position_percent === "number"
        ? asserted.tr_position_percent : snapshot.tr_position_percent;
      readouts.hudTrPosition.textContent = `${pct.toFixed(0)}% / 80%`;
      readouts.hudTrPosition.dataset.flag = pct >= 80 ? "true" : "false";
    }
    if (readouts.hudN1k) {
      const n1k = typeof asserted.n1k_percent === "number" ? asserted.n1k_percent : snapshot.n1k_percent;
      readouts.hudN1k.textContent = `${n1k.toFixed(0)}% / 84%`;
      readouts.hudN1k.dataset.flag = n1k <= 84 ? "true" : "false";
    }
    if (readouts.hudFaults) {
      const parts = [];
      if (asserted.e_tras_over_temp_fault) parts.push("过温");
      if (asserted.tr_inhibited) parts.push("抑制");
      readouts.hudFaults.textContent = parts.length ? parts.join(" / ") : "正常";
      readouts.hudFaults.dataset.flag = parts.length ? "fault" : "true";
    }
  }

  function setHud(el, value) {
    if (!el) return;
    el.textContent = formatBool(value);
    el.dataset.flag = value === true ? "true" : "false";
  }

  function renderOutputs(asserted) {
    setOutputCard(readouts.outSinglePhase,  readouts.outSinglePhaseV, asserted.eicu_cmd2,             "active");
    setOutputCard(readouts.outThreePhase,   readouts.outThreePhaseV,  asserted.eicu_cmd3,             "active");
    setOutputCard(readouts.outFadecDeploy,  readouts.outFadecDeployV, asserted.fadec_deploy_command,  "active");
    setOutputCard(readouts.outFadecStow,    readouts.outFadecStowV,   asserted.fadec_stow_command,    "stow");
  }

  function setOutputCard(card, valueEl, asserted, activeState) {
    if (!card || !valueEl) return;
    const on = asserted === true;
    card.dataset.state = on ? activeState : "idle";
    valueEl.textContent = on ? "ON" : "OFF";
  }

  function renderChainSvg(activeIds, asserted) {
    if (!chainSvg) return;
    clearSimulationMarkers();
    // Logic gates
    chainSvg.querySelectorAll(".chain-logic").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      group.dataset.state = activeIds.has(nodeId) ? "active" : "idle";
    });
    // Input / output chain nodes keyed by component id
    chainSvg.querySelectorAll(".chain-node").forEach((group) => {
      const nodeId = group.getAttribute("data-node");
      const value = asserted[nodeId];
      const active = isTruthyComponent(nodeId, value);
      group.dataset.state = active ? "active" : "idle";
    });
  }

  function isTruthyComponent(id, value) {
    if (value === true) return true;
    if (id === "lock_state") return value === "UNLOCKED_CONFIRMED";
    if (id === "tra_deg") return typeof value === "number" && value < -1.4;
    if (id === "tr_position_percent") return typeof value === "number" && value > 0;
    if (id === "n1k_percent") return typeof value === "number" && value > 0;
    return false;
  }

  function renderStatusBanner(summary, completion, asserted) {
    if (readouts.statusSummary && summary) readouts.statusSummary.textContent = summary;
    if (readouts.completionFlag) {
      readouts.completionFlag.textContent = completion ? "已达成" : "未达成";
      readouts.completionFlag.dataset.reached = completion ? "true" : "false";
    }
    if (readouts.statusBadge) {
      const state = inferBadgeState(asserted, completion);
      readouts.statusBadge.dataset.state = state;
      readouts.statusBadge.textContent = badgeText(state);
    }
  }

  function inferBadgeState(asserted, completion) {
    if (asserted.e_tras_over_temp_fault || asserted.tr_inhibited) return "fault";
    if (asserted.fadec_deploy_command && completion) return "deployed";
    if (asserted.fadec_deploy_command) return "deploying";
    if (asserted.fadec_stow_command) return "stowing";
    if (asserted.eicu_cmd3 || asserted.eicu_cmd2) return "ready";
    return "idle";
  }

  function badgeText(state) {
    return ({
      idle:      "IDLE",
      ready:     "READY",
      deploying: "DEPLOYING",
      deployed:  "DEPLOYED",
      stowing:   "STOWING",
      fault:     "FAULT",
    })[state] || "IDLE";
  }

  // ═══════════ Scenario presets ═══════════
  const presets = {
    "nominal-stowed": {
      label: "默认（空中收起上锁）",
      apply: () => {
        setSlider(inputs.tra, 0);
        setSlider(inputs.n1k, 35);
        setSlider(inputs.trPosition, 0);
        setChecked(inputs.engineRunning, true);
        setChecked(inputs.trInhibited, false);
        setChecked(inputs.overTempFault, false);
        setChecked(inputs.trcuPowerOn, true);
        setChecked(inputs.vdtValid, true);
        setChecked(inputs.lgcu1Value, true);
        setChecked(inputs.lgcu1Valid, true);
        setChecked(inputs.lgcu2Value, true);
        setChecked(inputs.lgcu2Valid, true);
        setChecked(inputs.trWow, true);
        setChecked(inputs.tlsAUnlocked, false);
        setChecked(inputs.tlsBUnlocked, false);
        setChecked(inputs.plsALocked, true);
        setChecked(inputs.plsBLocked, true);
        setChecked(inputs.leftPylonAUnlocked, false);
        setChecked(inputs.leftPylonBUnlocked, false);
        setChecked(inputs.rightPylonAUnlocked, false);
        setChecked(inputs.rightPylonBUnlocked, false);
        setChecked(inputs.prevCmd3, false);
        setNumber(inputs.comm2Timer, 0);
        setNumber(inputs.unlockConfirm, 0);
        setNumber(inputs.deployedConfirm, 0);
        setNumber(inputs.stowedConfirm, 2);
      },
    },
    "landing-deploy": {
      label: "着陆展开全链路",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, -25.0);
        setSlider(inputs.n1k, 60);
        setSlider(inputs.trPosition, 85);
        // Unlocks propagated
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, true);
        setChecked(inputs.rightPylonBUnlocked, true);
        // Timing passed
        setNumber(inputs.comm2Timer, 1.0);
        setNumber(inputs.unlockConfirm, 0.5);
        setNumber(inputs.deployedConfirm, 0.5);
        setNumber(inputs.stowedConfirm, 0);
        setChecked(inputs.prevCmd3, true);
      },
    },
    "max-reverse": {
      label: "最大反推（MAX REV）",
      apply: () => {
        presets["landing-deploy"].apply();
        setSlider(inputs.tra, -32.0);
        setSlider(inputs.n1k, 90);
        setSlider(inputs.trPosition, 100);
      },
    },
    "stow-return": {
      label: "收起回杆",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, 0);
        setSlider(inputs.n1k, 45);
        setSlider(inputs.trPosition, 30);  // mid-stow
        setChecked(inputs.prevCmd3, true);
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, true);
        setChecked(inputs.rightPylonBUnlocked, true);
        setNumber(inputs.stowedConfirm, 0);
      },
    },
    "over-temp-abort": {
      label: "过温中断",
      apply: () => {
        presets["landing-deploy"].apply();
        setChecked(inputs.overTempFault, true);
      },
    },
    "lock-fault": {
      label: "锁传感器故障（解锁不一致）",
      apply: () => {
        presets["nominal-stowed"].apply();
        setSlider(inputs.tra, -15.0);
        setSlider(inputs.n1k, 60);
        // Partial unlock — TLS yes but pylons still locked
        setChecked(inputs.tlsAUnlocked, true);
        setChecked(inputs.tlsBUnlocked, true);
        setChecked(inputs.plsALocked, false);
        setChecked(inputs.plsBLocked, false);
        setChecked(inputs.leftPylonAUnlocked, true);
        setChecked(inputs.leftPylonBUnlocked, true);
        setChecked(inputs.rightPylonAUnlocked, false);  // fault: right pylon did not unlock
        setChecked(inputs.rightPylonBUnlocked, false);
        setNumber(inputs.comm2Timer, 1.0);
      },
    },
  };

  function setSlider(el, value) { if (el) el.value = String(value); }
  function setNumber(el, value) { if (el) el.value = String(value); }
  function setChecked(el, value) { if (el) el.checked = !!value; }

  function applyPreset(key) {
    const preset = presets[key];
    if (!preset) return;
    preset.apply();
    if (readouts.presetStatus) {
      readouts.presetStatus.textContent = "当前场景：" + preset.label;
    }
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.preset === key ? "true" : "false");
    });
    // Immediate fetch after preset (no debounce — single batched snapshot)
    fetchEvaluation();
  }

  // ═══════════ Reliability simulation candidate ═══════════
  function renderProbabilityRows() {
    if (!readouts.probabilityNodeList) return;
    readouts.probabilityNodeList.innerHTML = RELIABILITY_NODES.map((node) => {
      const pct = (node.normalProbability * 100).toFixed(2);
      return `
        <label class="probability-node-row" data-prob-row="${escapeAttr(node.id)}">
          <span class="probability-node-label">
            <span class="probability-node-kind">${escapeHtml(node.kind)}</span>${escapeHtml(node.label)}
          </span>
          <input class="probability-input" type="number" min="0" max="100" step="0.01"
                 value="${pct}" data-prob-node="${escapeAttr(node.id)}"
                 aria-label="${escapeAttr(node.label)} 正常运行概率百分比">
        </label>
      `;
    }).join("");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/'/g, "&#39;");
  }

  function readProbability(nodeId) {
    const input = document.querySelector(`[data-prob-node="${cssEscape(nodeId)}"]`);
    const raw = input ? parseFloat(input.value) : NaN;
    const pct = Number.isFinite(raw) ? raw : (RELIABILITY_NODE_BY_ID.get(nodeId)?.normalProbability || 0) * 100;
    return clamp(pct, 0, 100) / 100;
  }

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
    return String(value).replace(/"/g, '\\"');
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function selectedReliabilityNodeIds() {
    const scope = readouts.simScope ? readouts.simScope.value : "all";
    if (scope !== "active") return RELIABILITY_NODES.map((node) => node.id);

    const ids = new Set();
    if (chainSvg) {
      chainSvg.querySelectorAll('[data-node][data-state="active"]').forEach((el) => {
        const id = el.getAttribute("data-node");
        if (RELIABILITY_NODE_BY_ID.has(id)) ids.add(id);
      });
    }
    lastEvaluationContext.activeIds.forEach((id) => {
      if (RELIABILITY_NODE_BY_ID.has(id)) ids.add(id);
    });
    if (lastEvaluationContext.activeIds.has("ln_eicu_cmd2")) ids.add("tr_inhibited");
    if (lastEvaluationContext.activeIds.has("ln_tr_command3_enable")) ids.add("lock_state");
    return ids.size ? Array.from(ids) : RELIABILITY_NODES.map((node) => node.id);
  }

  function runReliabilitySimulation() {
    try {
      const nTrials = clamp(parseInt(readouts.simTrials ? readouts.simTrials.value : "10000", 10) || 10000, 1, 50000);
      const seed = parseInt(readouts.simSeed ? readouts.simSeed.value : "42", 10) || 0;
      if (readouts.simTrials) readouts.simTrials.value = String(nTrials);
      if (readouts.simSeed) readouts.simSeed.value = String(seed);

      const nodeIds = selectedReliabilityNodeIds();
      const rng = seededRandom(seed);
      const primaryFailureCounts = new Map(nodeIds.map((id) => [id, 0]));
      const involvedFailureCounts = new Map(nodeIds.map((id) => [id, 0]));
      const failureSamples = [];
      let successCount = 0;

      for (let runIndex = 1; runIndex <= nTrials; runIndex += 1) {
        const failedNodeIds = [];
        nodeIds.forEach((nodeId) => {
          if (rng() > readProbability(nodeId)) failedNodeIds.push(nodeId);
        });
        if (!failedNodeIds.length) {
          successCount += 1;
          continue;
        }
        const primary = failedNodeIds[0];
        primaryFailureCounts.set(primary, (primaryFailureCounts.get(primary) || 0) + 1);
        failedNodeIds.forEach((nodeId) => {
          involvedFailureCounts.set(nodeId, (involvedFailureCounts.get(nodeId) || 0) + 1);
        });
        if (failureSamples.length < 6) {
          failureSamples.push({ runIndex, failedNodeIds });
        }
      }

      const failureCount = nTrials - successCount;
      const successRate = successCount / nTrials;
      const analyticalRate = nodeIds.reduce((product, nodeId) => product * readProbability(nodeId), 1);
      const topCauses = Array.from(primaryFailureCounts.entries())
        .filter(([, count]) => count > 0)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6);

      renderReliabilityResults({
        nTrials,
        nodeIds,
        successRate,
        analyticalRate,
        failureCount,
        topCauses,
        involvedFailureCounts,
        failureSamples,
      });
      markSimulationCauses(topCauses.map(([nodeId]) => nodeId).slice(0, 3));
    } catch (err) {
      console.warn("[c919-workstation] reliability simulation failed:", err);
      if (readouts.simScopeLabel) readouts.simScopeLabel.textContent = "仿真失败：" + (err && err.message ? err.message : String(err));
    }
  }

  function seededRandom(seed) {
    let state = seed >>> 0;
    return function nextRandom() {
      state += 0x6D2B79F5;
      let t = state;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function renderReliabilityResults(result) {
    if (readouts.simSuccessRate) readouts.simSuccessRate.textContent = formatProbability(result.successRate);
    if (readouts.simFailureCount) readouts.simFailureCount.textContent = `${result.failureCount} / ${result.nTrials}`;
    if (readouts.simAnalyticalRate) readouts.simAnalyticalRate.textContent = formatProbability(result.analyticalRate);
    if (readouts.simScopeLabel) {
      const scopeLabel = readouts.simScope && readouts.simScope.value === "active" ? "当前激活链路" : "全节点";
      readouts.simScopeLabel.textContent = `${scopeLabel} · ${result.nodeIds.length} 个节点 · 固定 seed 本地仿真`;
    }
    if (readouts.simTopCauses) {
      if (!result.topCauses.length) {
        readouts.simTopCauses.innerHTML = '<div class="simulation-cause-row"><span>无失败样本</span><strong>0</strong></div>';
      } else {
        readouts.simTopCauses.innerHTML = result.topCauses.map(([nodeId, count]) => {
          const share = result.failureCount ? count / result.failureCount : 0;
          const involved = result.involvedFailureCounts.get(nodeId) || count;
          return `
            <div class="simulation-cause-row">
              <span>${escapeHtml(nodeLabel(nodeId))}</span>
              <strong>${count} primary · ${involved} involved · ${formatProbability(share)}</strong>
            </div>
          `;
        }).join("");
      }
    }
    if (readouts.simFailureSamples) {
      readouts.simFailureSamples.innerHTML = result.failureSamples.map((sample) => `
        <div class="simulation-sample-row">
          <span>#${sample.runIndex}: ${escapeHtml(sample.failedNodeIds.map(nodeLabel).join(" / "))}</span>
          <strong>${sample.failedNodeIds.length}</strong>
        </div>
      `).join("");
    }
  }

  function nodeLabel(nodeId) {
    return RELIABILITY_NODE_BY_ID.get(nodeId)?.label || nodeId;
  }

  function formatProbability(value) {
    if (!Number.isFinite(value)) return "—";
    return (value * 100).toFixed(value >= 0.999 ? 3 : 2) + "%";
  }

  function markSimulationCauses(nodeIds) {
    clearSimulationMarkers();
    nodeIds.forEach((nodeId) => {
      if (!chainSvg) return;
      const el = chainSvg.querySelector(`[data-node="${cssEscape(nodeId)}"]`);
      if (el) el.dataset.simCause = "top";
    });
  }

  function clearSimulationMarkers() {
    if (!chainSvg) return;
    chainSvg.querySelectorAll("[data-sim-cause]").forEach((el) => {
      delete el.dataset.simCause;
    });
  }

  function applyBulkProbability() {
    const raw = readouts.bulkProbability ? parseFloat(readouts.bulkProbability.value) : 99.9;
    const pct = clamp(Number.isFinite(raw) ? raw : 99.9, 0, 100);
    if (readouts.bulkProbability) readouts.bulkProbability.value = pct.toFixed(2);
    document.querySelectorAll("[data-prob-node]").forEach((input) => {
      input.value = pct.toFixed(2);
    });
  }

  // ═══════════ Wire input listeners ═══════════
  function installListeners() {
    Object.values(inputs).forEach((el) => {
      if (!el) return;
      const evt = el.type === "checkbox" ? "change" : "input";
      el.addEventListener(evt, scheduleFetch);
    });
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });
    const runButton = $("etras-run-simulation");
    const bulkButton = $("etras-apply-bulk-probability");
    if (runButton) {
      runButton.addEventListener("click", runReliabilitySimulation);
    }
    if (bulkButton) {
      bulkButton.addEventListener("click", applyBulkProbability);
    }
  }

  // ═══════════ Bootstrap ═══════════
  function boot() {
    renderProbabilityRows();
    installListeners();
    fetchEvaluation();  // initial render
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
