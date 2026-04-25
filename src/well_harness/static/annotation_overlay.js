(function () {
  const tools = ["point", "area", "link", "text-range"];
  const surfaces = ["control", "document", "circuit"];
  const draftStorageKey = "well-harness-workbench-annotation-drafts-v1";
  let activeTool = "point";
  let draftSequence = 0;

  function clampUnit(value) {
    if (!Number.isFinite(value)) {
      return 0;
    }
    return Math.max(0, Math.min(1, value));
  }

  function normalizePoint(event, element) {
    const bounds = element.getBoundingClientRect();
    return {
      x: clampUnit((event.clientX - bounds.left) / bounds.width),
      y: clampUnit((event.clientY - bounds.top) / bounds.height),
    };
  }

  function currentTicketId() {
    const ticket = document.getElementById("workbench-ticket");
    return ticket ? ticket.dataset.ticket || "WB-LOCAL" : "WB-LOCAL";
  }

  function currentSystemId() {
    const selector = document.getElementById("workbench-system-select");
    return selector ? selector.value : "thrust-reverser";
  }

  function currentAuthor() {
    const identity = document.getElementById("workbench-identity");
    if (!identity) {
      return "local-engineer";
    }
    const label = identity.querySelector("strong");
    return label ? label.textContent.trim() : "local-engineer";
  }

  function timestamp() {
    return new Date().toISOString();
  }

  function draftId() {
    draftSequence += 1;
    return `prop_local_${Date.now()}_${draftSequence}`;
  }

  function selectedTextAnchor(surfaceElement) {
    const selection = window.getSelection ? window.getSelection() : null;
    if (!selection || selection.rangeCount === 0 || !selection.toString().trim()) {
      return null;
    }
    const range = selection.getRangeAt(0);
    if (!surfaceElement.contains(range.commonAncestorContainer)) {
      return null;
    }
    return {
      selector: `#${surfaceElement.id}`,
      start_offset: 0,
      end_offset: selection.toString().length,
      text_quote: selection.toString().trim(),
    };
  }

  function createAnnotationDraft(input) {
    const observedAt = timestamp();
    return {
      id: input.id || draftId(),
      tool: input.tool,
      surface: input.surface,
      anchor: input.anchor,
      note: input.note || `${input.tool} annotation on ${input.surface}`,
      author: input.author || currentAuthor(),
      ticket_id: input.ticket_id || currentTicketId(),
      system_id: input.system_id || currentSystemId(),
      status: "pending",
      created_at: observedAt,
      updated_at: observedAt,
      source: {
        ui: "workbench.annotation_overlay",
      },
    };
  }

  function loadDrafts() {
    try {
      const raw = window.localStorage.getItem(draftStorageKey);
      return raw ? JSON.parse(raw) : [];
    } catch (error) {
      return [];
    }
  }

  function persistDraft(draft) {
    const drafts = loadDrafts();
    drafts.push(draft);
    window.localStorage.setItem(draftStorageKey, JSON.stringify(drafts.slice(-50)));
  }

  function renderMarker(surfaceElement, draft) {
    const marker = document.createElement("span");
    marker.className = "workbench-annotation-marker";
    marker.dataset.tool = draft.tool;
    marker.title = `${draft.tool} annotation`;
    marker.style.left = `${Math.round((draft.anchor.x || 0) * 100)}%`;
    marker.style.top = `${Math.round((draft.anchor.y || 0) * 100)}%`;
    if (draft.tool === "area") {
      marker.style.width = `${Math.round((draft.anchor.width || 0.16) * 100)}%`;
      marker.style.height = `${Math.round((draft.anchor.height || 0.12) * 100)}%`;
    }
    surfaceElement.appendChild(marker);
  }

  function renderInboxDraft(draft) {
    const list = document.getElementById("annotation-inbox-list");
    if (!list) {
      return;
    }
    if (list.children.length === 1 && list.children[0].textContent === "No proposals submitted yet.") {
      list.textContent = "";
    }
    const item = document.createElement("li");
    item.className = "workbench-annotation-draft";
    item.textContent = `${draft.tool} on ${draft.surface}: ${draft.note}`;
    list.prepend(item);
  }

  function buildAnchorForTool(tool, surfaceElement, event) {
    const point = normalizePoint(event, surfaceElement);
    if (tool === "area") {
      return { ...point, width: 0.22, height: 0.16 };
    }
    if (tool === "link") {
      return { ...point, href: window.location.href, selector: `#${surfaceElement.id}` };
    }
    if (tool === "text-range") {
      return selectedTextAnchor(surfaceElement) || { ...point, selector: `#${surfaceElement.id}`, text_quote: "" };
    }
    return point;
  }

  function handleSurfaceClick(event) {
    const surfaceElement = event.currentTarget;
    const surface = surfaceElement.dataset.annotationSurface;
    if (!surfaces.includes(surface)) {
      return;
    }
    const draft = createAnnotationDraft({
      tool: activeTool,
      surface,
      anchor: buildAnchorForTool(activeTool, surfaceElement, event),
    });
    persistDraft(draft);
    renderMarker(surfaceElement, draft);
    renderInboxDraft(draft);
  }

  function setActiveTool(tool) {
    if (!tools.includes(tool)) {
      return;
    }
    activeTool = tool;
    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
      const pressed = button.dataset.annotationTool === activeTool;
      button.classList.toggle("is-active", pressed);
      button.setAttribute("aria-pressed", String(pressed));
    });
    const status = document.getElementById("workbench-annotation-active-tool");
    if (status) {
      status.textContent = `${tool} tool active`;
    }
  }

  function installAnnotationOverlay() {
    document.querySelectorAll("[data-annotation-tool]").forEach((button) => {
      button.addEventListener("click", () => setActiveTool(button.dataset.annotationTool));
    });
    document.querySelectorAll("[data-annotation-surface]").forEach((surfaceElement) => {
      surfaceElement.addEventListener("click", handleSurfaceClick);
    });
    setActiveTool(activeTool);
  }

  window.WorkbenchAnnotationOverlay = {
    tools,
    surfaces,
    createAnnotationDraft,
    installAnnotationOverlay,
    setActiveTool,
  };

  window.addEventListener("DOMContentLoaded", installAnnotationOverlay);
})();
