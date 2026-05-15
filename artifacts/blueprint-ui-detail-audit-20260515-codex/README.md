# Blueprint UI Detail Audit - 2026-05-15

This audit is based on existing Codex blueprint screenshots only. It rejects the manually mocked V2 direction because its wires, boxes, and text fit were not faithful to the real circuit UI.

## Reference Screenshot Set

1. `artifacts/blueprint37-right-rail-20260515-codex/requirements-intake--desktop-1366x768.png`
2. `artifacts/blueprint37-right-rail-20260515-codex/logic-builder--desktop-1366x768.png`
3. `artifacts/blueprint37-right-rail-20260515-codex/fault-injection-prepare--desktop-1366x768.png`
4. `artifacts/blueprint37-right-rail-20260515-codex/sandbox-right-rail-desktop-1366x768.png`
5. `artifacts/deepseek-ui-visual-acceptance-20260515-blueprint37-wide-canvas-report-system-codex/fault-injection-sandbox-blueprint37-wide-canvas-report-system--desktop-1366x768.png`
6. `artifacts/deepseek-ui-visual-acceptance-20260515-blueprint37-main-canvas-report-rail-codex/fault-injection-sandbox-blueprint37-main-canvas-report-rail--desktop-1366x768.png`
7. `artifacts/blueprint37-right-rail-20260515-codex/fault-injection-sandbox--desktop-1366x768.png`

## Non-Negotiable Design Rules

- Do not hand-draw a separate illustrative circuit. Use the app's real graph renderer, real node coordinates, real port anchors, and real edge paths.
- Every visible wire endpoint must terminate at a visible port or node edge. No floating wire ends, no wires disappearing under boxes, no visual-only curves that do not map to the graph.
- Every text container must be measured against its longest expected Chinese and code-token string. If it cannot fit, choose a shorter label or move the detail to hover/details.
- The default workbench must explain the circuit through geometry first: node labels, directed wires, active path color, port badges, and one selected path. Text is secondary.
- The Codex minimal style is restrained, not empty: fewer panels, stable alignment, crisp grid, high canvas priority, no marketing copy, no decorative density.

## 1. Requirements Intake

What works:

- The top nav and step rhythm are clear.
- The source panel, verdict panel, and next-step panel form a usable first-screen story.
- The checklist row gives an early sense of the L1/SW/VDT logic vocabulary.

Issues:

- The page still carries too many boxed regions competing for attention before the user reaches drawing.
- The main source text area is visually large but semantically passive after the requirement is loaded.
- The small status chips in the verdict row have weak hierarchy and read as metadata clutter.

Target improvements:

- Keep this page as a source intake screen, not a design workbench.
- Collapse provider/runtime metadata into one status chip after success.
- Move the checklist row closer to the transition into drawing, because those terms become the graph nodes.
- The final visible promise should be: source -> L1-L4 chain -> draw next. Avoid extra explanatory lines.

## 2. Logic Builder Canvas

What works:

- This is the best source for the actual blueprint UI direction: central circuit graph, left source/history rail, right mode rail, bottom run strip.
- The red L1-L4 node groups make the logical layers readable.
- The tabs across the top align with the expected workbench modes: canvas, run, params, evidence, report.

Issues:

- The DeepSeek stream popover covers graph content. It blocks source nodes and makes the canvas feel untrustworthy.
- Several connectors visually pass under or into annotation boxes without clear port anchors. This is acceptable for a debug overlay, but not for a polished blueprint.
- The left input stack and inner join rail are cramped. Lines converge near the left edge and create a visual knot before entering L1/L2/L3.
- The right half has large empty dotted grid space while the graph itself is compressed to the left. Canvas real estate is not allocated according to the graph's shape.
- The bottom dark note/input bar is visually heavy and competes with the graph.
- Text in node cards is mixed: some labels are readable, some code/condition text is too small and low-contrast.

Target improvements:

- Treat the graph renderer as the truth source: node boxes, ports, and wires should be generated from the same layout data, not adjusted separately in CSS.
- Hide generation streams by default once drawing is complete. A small "DeepSeek completed" chip is enough; logs belong in details.
- Center the graph within the canvas after measuring its bounding box. If there is empty space, distribute it around the graph or use it for inspector space.
- Separate source input nodes from logic group nodes by a fixed horizontal gutter. Avoid early wire crossings before L1/L2/L3.
- Require every node label to fit in two lines at 1366 and 1280. Code-level details move to tooltip/inspector.
- Keep bottom run controls thin. The graph should remain the dominant object.

## 3. Fault Injection Prepare

What works:

- Candidate rows are useful: fault location, type, trigger, impact, covered path, risk, status.
- The right source/model output rail helps explain that this is still candidate-only.

Issues:

- The fault matrix uses too many small chips inside each row. It is technically rich but visually noisy.
- Row text mixes Chinese business labels with raw variable names, so neither novice nor expert scanning is ideal.
- The right rail repeats state and model output information while the primary table already expresses candidate state.
- The bottom action bar has several same-weight actions; only one next action should dominate.

Target improvements:

- Keep only fault ID, location, trigger, impact, and status in the row. Move covered path chips to hover or selected-row detail.
- Make one selected candidate drive a mini path preview, not multiple chips in every row.
- Distinguish "domain-readable" labels from raw IDs. Example: show "RA 门限" first, `ra_lt_6ft` second only in subdued monospace.
- Use one primary CTA: enter sandbox. Secondary actions stay compact and visually quieter.

## 4. Sandbox Right Rail

What works:

- The combined screen can tell the full workbench story: review canvas, evidence trace, diagnosis, report rail, timeline, and export.
- The right rail has the right conceptual pieces: diagnosis state, report preview, active review package, affected path, evidence trace.

Issues:

- The right rail is overpacked. At 1366 it reads as a stack of clipped cards rather than a selected-inspector surface.
- Report rows inside the rail show too many repeated sections. The rail should summarize the active section, not replicate the full report list.
- The diagnosis summary text is still too sentence-like. It competes with the graph instead of naming the active path.
- The affected path/input snapshot cards use long code tokens that truncate awkwardly.
- The evidence trace column in the middle and the right rail evidence trace duplicate each other.

Target improvements:

- Right rail should default to one active path card:
  - title: active review row, such as `SR-06`
  - path: compact node chain, such as `RA -> L1 -> LATCH`
  - evidence chips: `ET-04`, `RP-06`
  - result: pass/review/wait
- Full report preview should stay in the bottom report strip or export panel, not occupy the top rail by default.
- Use 1-line labels for status and 2-line max for explanations. Anything longer opens detail.
- Do not show both "diagnosis evidence links" and "evidence trace" in the same rail unless one is collapsed.
- Keep right rail width stable and measure all chips against `controller_truth_modified:false`, `certification_claim:none`, and Chinese labels.

## 5. Wide Canvas Sandbox Variant

What works:

- The wide canvas better emphasizes the graph and makes the sandbox feel like a workbench.
- The right rail is visually related to the report/action surface.

Issues:

- Some wires are visibly not semantically aligned: green/orange/red/blue paths cross in ways that imply logic relationships that may not be true.
- The canvas is partially hidden by upper panels; the graph starts too low and is clipped by the bottom report strip.
- The review row table remains below the graph and consumes height without adding first-screen understanding.

Target improvements:

- Only show a wire if the current graph renderer can prove its endpoints and layer ordering.
- Use active path emphasis instead of displaying all wires equally. In sandbox view, show the candidate failure path strongly and dim the rest.
- Move review table density behind selection. First screen needs graph + selected path + one decision, not every row.

## 6. Main Canvas + Report Rail Variant

What works:

- This variant shows the intended main structure clearly: graph center, diagnosis/report rail right, replay/report strip bottom.
- It is closer to the Codex minimal workbench target than the current right-rail-heavy screenshot.

Issues:

- The graph is compressed vertically and node labels are hard to read.
- A red wire appears to connect to the L1 warning path in a way that is visually ambiguous; the edge's source/target should be explicit.
- The report rail still repeats report sections before the user has selected a report intent.

Target improvements:

- Increase graph row height or reduce top process stack before changing rail content.
- Route emphasized wires orthogonally or with stable Bezier lanes that avoid node interiors.
- Replace report-section list with compact active report status unless the report tab is explicitly selected.

## 7. Report Package Preview

What works:

- The three-column review/evidence/report package shape is useful.
- It correctly communicates export readiness.

Issues:

- It is too dense for a first-screen workbench, but acceptable as a modal/export surface.
- Repeated pill links make the preview look more complicated than the package actually is.

Target improvements:

- Keep this as an explicit export/preview panel, not a default rail.
- Use grouped counts and active exceptions by default; list all rows only after user opens the package.

## Priority Fix List

P0 - Graph geometry correctness:

- Stop any manually mocked circuit screenshots from being treated as target UI.
- Use real graph model coordinates and port anchors for every screenshot and implementation iteration.
- Add visual checks for floating endpoints, wire-node overlaps, and edge paths crossing through unrelated nodes.

P1 - Text fitting:

- Define max visible labels per surface:
  - node: 1 short title + 1 compact value
  - right rail: active path + 3 evidence chips + result
  - bottom strip: timeline ticks + boundary chips
  - report modal: full rows allowed
- Add screenshot/e2e checks for `scrollWidth <= clientWidth` on node labels, rail chips, report chips, and CTA buttons.

P1 - Density hierarchy:

- Default view: canvas first.
- Selected view: one path in right rail.
- Details view: evidence/report rows.
- Export view: full package.

P2 - Visual rhythm:

- Reduce top process stack height before shrinking graph text.
- Preserve consistent 8px cards, but avoid cards inside cards.
- Use one active blue path, green pass states, amber review states, red only for true failure or blocked state.

## Proposed Next Implementation Slice

Implement a no-new-design polish pass against the real app renderer:

1. Capture the current real logic-builder and sandbox canvases at 1366 and 1280.
2. Add geometry assertions:
   - every rendered edge endpoint is within 4px of its declared port/node anchor;
   - no edge segment intersects a non-endpoint node's bounding box;
   - visible node labels fit their boxes;
   - selected path labels and rail chips fit without clipping.
3. Reduce default rail/report text using existing UI surfaces only:
   - right rail default: active path summary;
   - report list only when report/export is active;
   - long raw IDs behind details/tooltip.
4. Re-capture the same screenshot set and compare.
