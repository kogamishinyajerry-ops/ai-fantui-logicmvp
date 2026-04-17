---
phase: P19
plan: P19-04
type: execute
wave: 1
depends_on: [P19-03]
files_created: []
files_modified:
  - src/well_harness/static/chat.js
  - src/well_harness/static/chat.css
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — this is pure frontend visualization"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "AI causal chain connectors draw between sequentially discussed nodes on the SVG Canvas"
    - "Connectors are dashed blue lines with arrowheads showing causal direction"
    - "Connectors update whenever applyAiHighlights is called (both /api/chat/explain and /api/chat/reason)"
    - "Connectors are removed when clearAiHighlights is called"
    - "Connectors are removed when system is switched (no stale highlights)"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/static/chat.js
      provides: "drawCausalChainConnectors + clearCausalChainConnectors functions"
      min_lines: 80
    - path: src/well_harness/static/chat.css
      provides: "CSS for causal chain connector SVG elements"
      min_lines: 20
  key_constraints:
    - "chat.js: addConnectorLayer() creates persistent SVG layer; no DOM polling"
    - "Connectors drawn using SVG <line> and <marker> elements in canvas-wrapper"
    - "No changes to demo_server.py API contracts"
exit_criteria:
  - "grep -n 'drawCausalChainConnectors' src/well_harness/static/chat.js returns ≥1 match"
  - "grep -n 'causal-chain' src/well_harness/static/chat.css returns ≥1 match"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.4 — AI Causal Chain Canvas Highlights

### Context

P16 established the two-layer Canvas system:
- **Truth layer**: active/blocked/inactive node states from truth engine
- **AI discussion layer**: `.ai-discussed` (blue) and `.ai-suggested` (amber) CSS classes on discussed nodes

P19.4 adds the **causal chain connector layer**: SVG dashed lines with arrowheads
connecting sequentially discussed nodes, making the AI's causal reasoning visually explicit.

### Architecture

```
/ api/chat/reason or /api/chat/explain returns:
  { highlighted_nodes: ["SW1", "TLS115", "L2", "L3", "THR_LOCK"], ... }
                                    ↓
                           drawCausalChainConnectors()
                                    ↓
                           SVG layer: SW1 → TLS115 → L2 → L3 → THR_LOCK
                                    (dashed blue arrows between nodes)
```

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- API contracts (`/api/chat/reason`, `/api/chat/explain`)
- Existing CSS classes `.ai-discussed`, `.ai-suggested`

### Implementation

#### 1. `src/well_harness/static/chat.js` — additions

Add after `applyAiHighlights()` (~line 845):

```javascript
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
// called at the end of applyAiHighlights(), after node classes are set.
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
  for (var i = 0; i < nodeIds.length; i++) {
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
      // Center of the node element relative to .canvas-wrapper
      x: rect.left + rect.width / 2 - wrapperRect.left,
      y: rect.top + rect.height / 2 - wrapperRect.top,
    });
  }

  // Draw connector from each node to the next
  for (var j = 0; j < boxes.length - 1; j++) {
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

// Remove all causal chain connectors (call from clearAiHighlights)
function clearCausalChainConnectors() {
  var svg = document.getElementById('causal-chain-layer');
  if (!svg) return;
  var connectors = svg.querySelectorAll('.causal-connector, .causal-connector-label');
  connectors.forEach(function(el) { el.remove(); });
}
```

Modify `clearAiHighlights()` to also clear connectors:

```javascript
function clearAiHighlights() {
  var highlightedEls = document.querySelectorAll(
    '.canvas-wrapper .ai-discussed, .canvas-wrapper .ai-suggested'
  );
  for (var i = 0; i < highlightedEls.length; i += 1) {
    highlightedEls[i].classList.remove('ai-discussed', 'ai-suggested');
  }
  clearCausalChainConnectors();  // ← ADD THIS LINE
}
```

Modify `applyAiHighlights()` to draw connectors after setting classes:

```javascript
// At the end of applyAiHighlights(), after the two for-loops that add classes:
// (around line 845)
drawCausalChainConnectors(discussed);  // ← ADD THIS LINE
```

Also ensure connectors are cleared when system is switched — add to `applySystemSnapshotToCanvas` or the system-switch handler:

```javascript
// In system switch / applySystemSnapshotToCanvas:
clearAiHighlights();
```

#### 2. `src/well_harness/static/chat.css` — additions

Add to end of chat.css:

```css
/* P19.4: Causal chain connector SVG layer */
.causal-chain-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 20;
  overflow: visible;
}

.causal-connector {
  stroke: #5ba8ff;
  stroke-width: 2;
  stroke-dasharray: 5, 3;
  opacity: 0.75;
}

.causal-connector-label {
  fill: #5ba8ff;
  font-size: 10px;
  font-family: monospace;
  text-anchor: middle;
  opacity: 0.85;
}
```

### Tasks

#### Task 1: Modify `src/well_harness/static/chat.js`

- Add `getCausalChainLayer()` — creates persistent SVG overlay with arrowhead marker
- Add `drawCausalChainConnectors(highlightedNodes)` — draws dashed connectors between sequential nodes
- Add `clearCausalChainConnectors()` — removes all connectors
- Modify `clearAiHighlights()` to call `clearCausalChainConnectors()`
- Modify `applyAiHighlights()` to call `drawCausalChainConnectors(discussed)` at end

#### Task 2: Modify `src/well_harness/static/chat.css`

- Add `.causal-chain-layer`, `.causal-connector`, `.causal-connector-label` CSS rules

#### Task 3: Verify exit gates

```bash
# Gate 1: drawCausalChainConnectors exists in chat.js
grep -n 'drawCausalChainConnectors' src/well_harness/static/chat.js

# Gate 2: causal-chain CSS exists
grep -n 'causal-chain' src/well_harness/static/chat.css

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 604+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ Frontend only |
| No LLM calls | ✓ Pure SVG/JS |
| No breaking changes to existing API contracts | ✓ API unchanged |
| No changes to demo_server.py | ✓ Only chat.js + chat.css |

### Exit Gate

Verify all 3 gates above.
