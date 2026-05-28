(function () {
  "use strict";

  const DOCX_MAP_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;

  const $ = (id) => document.getElementById(id);
  const sourcePath = $("docx-circuit-source-path");
  const sourceCount = $("docx-circuit-source-count");
  const nodeCount = $("docx-circuit-node-count");
  const wireCount = $("docx-circuit-wire-count");
  const sequenceCount = $("docx-circuit-sequence-count");
  const sequenceList = $("docx-circuit-sequence-list");

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function appendChips(container, values, kind) {
    if (!Array.isArray(values) || values.length === 0) return;
    const row = document.createElement("div");
    row.className = "docx-circuit-chip-row";
    values.forEach((value) => {
      const chip = document.createElement("span");
      chip.className = "docx-circuit-chip";
      chip.dataset.kind = kind;
      chip.textContent = value;
      row.appendChild(chip);
    });
    container.appendChild(row);
  }

  function renderSequence(steps) {
    if (!sequenceList) return;
    sequenceList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "未能读取 P035 到 L1-L4 的链路拆解。";
      sequenceList.appendChild(empty);
      return;
    }
    steps.forEach((step) => {
      const item = document.createElement("li");
      item.dataset.sourceAnchor = step.anchor || "";
      const title = document.createElement("strong");
      title.textContent = `${step.anchor || "step"} · ${step.title || ""}`;
      const text = document.createElement("p");
      text.textContent = step.source_text || "";
      item.appendChild(title);
      item.appendChild(text);
      appendChips(item, step.node_ids, "node");
      appendChips(item, step.wire_ids, "wire");
      sequenceList.appendChild(item);
    });
  }

  function renderPayload(payload) {
    const source = payload && payload.source ? payload.source : {};
    const coverage = payload && payload.coverage ? payload.coverage : {};
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    setText(sourcePath, source.path || "uploads/20260409-thrust-reverser-control-logic.docx");
    setText(
      sourceCount,
      `${coverage.paragraph_count || 0} 段 · ${source.table_count || 0} 表 · ${coverage.source_entry_count || 0} 条`,
    );
    setText(nodeCount, `${coverage.covered_node_count || 0}/${contract.node_count || EXPECTED_NODE_COUNT}`);
    setText(wireCount, `${coverage.covered_wire_count || 0}/${contract.wire_count || EXPECTED_WIRE_COUNT}`);
    setText(sequenceCount, `P035 · ${coverage.sequence_step_count || 0} 步`);
    renderSequence(payload && payload.sequence_steps);
  }

  async function boot() {
    try {
      const response = await fetch(DOCX_MAP_ENDPOINT, {headers: {"Accept": "application/json"}});
      if (!response.ok) throw new Error("docx map unavailable");
      renderPayload(await response.json());
    } catch (error) {
      renderSequence([]);
    }
  }

  boot();
})();
