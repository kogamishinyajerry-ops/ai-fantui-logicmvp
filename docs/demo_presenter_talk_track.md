# Well Harness UI Demo Presenter Talk Track

This is a one-page presenter talk track for the local UI demo shell. It is manual demo guidance, not browser E2E automation, not a screenshot script, and not a new answer payload or control truth.

## 30-Second Opening

[Say] "This is a deterministic controlled demo layer for the thrust-reverser deploy chain. It is not an open-ended LLM and not a complete physical model."

[Point] Show the fixed control chain and the prompt examples. Mention that answers are generated from the existing `DemoAnswer` path and the UI calls the same `POST /api/demo` endpoint used by the local server.

[Point] Follow the page callout labels while presenting: `[Input]`, `[Chain]`, `[Highlight]`, `[Structured answer]`, and `[Raw JSON]` mark the same areas used in this talk track.

[Point] Use the screenshot-free presenter route strip as the visual path: `[Input] -> [Chain] -> [Highlight] -> [Structured answer] -> [Raw JSON]`. It is a manual walkthrough guide that replaces screenshot annotations; it is not browser E2E automation, not a screenshot annotation tool, and not a control-truth source.

[Point] The first screen now mirrors the same `Presenter Run Card` as four clickable bridge / diagnose / trigger / proposal steps. It is a manual presenter aid that reuses the existing prompt flow; it is not an automatic readiness detector.

[Point] If you need to jump the lever cockpit to a key live-demo state, use the visible `演示场景预设` row for `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready`. Those buttons only refill the existing `POST /api/lever-snapshot` inputs; they do not create a second state machine or a new control truth.

[Point] If the audience asks what the answer fields mean, open the `Audience answer-field legend` in the structured answer area. It explains `intent`, `matched_node`, `target_logic`, `evidence`, `outcome`, `possible_causes`, `required_changes`, `risks`, and raw JSON as a reading aid, not a new schema, payload, or control truth.

[Point] The legend and `Answer sections` summary now sit together as the compact answer guide, so field definitions and live section counts read as one guide for the same `DemoAnswer` payload.

[Point] On mobile / narrow screens, follow that same compact answer guide top-to-bottom; the field legend and `Answer sections` chips stack for touch-friendly scanning without changing the payload.

[Boundary] "The answers are based on built-in `nominal-deploy` / `retract-reset` scenarios and a simplified first-cut plant. Highlights are answer association, not a complete causal proof."

## Presenter Readiness Run Card

This run card is a manual pre-demo check. It is not browser E2E automation, not an automatic readiness detector, and not a new answer payload or control truth.

1. Start the local UI server:
   `PYTHONPATH=src python3 -m well_harness.demo_server`
2. Open the local URL printed by the server, usually `http://127.0.0.1:8000/`. If you want a launch convenience, use `PYTHONPATH=src python3 -m well_harness.demo_server --open`; it only calls the standard-library browser launcher and is not browser E2E automation.
3. First run the bridge prompt: `logic4 和 throttle lock 有什么关系`.
4. Confirm the page callout labels are visible and aligned with this talk track: `[Input]`, `[Chain]`, `[Highlight]`, `[Structured answer]`, and `[Raw JSON]`.
5. Confirm the screenshot-free presenter route strip is visible and reads `[Input] -> [Chain] -> [Highlight] -> [Structured answer] -> [Raw JSON]`.
6. Confirm the visible `Presenter Run Card` shows the same bridge / diagnose / trigger / proposal order as this talk track and uses clickable steps instead of a separate presenter-only payload.
7. Confirm the visible `演示场景预设` can jump to `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready` without introducing a separate presenter-only state machine.
8. Confirm the control chain highlights `logic4 / THR_LOCK`, the highlight explanation names the answer association, the structured answer is readable, and the `Answer sections` summary shows counts.
9. Expand or review the raw JSON debug panel when you need the machine-readable `DemoAnswer` payload.
10. If the UI shows loading, empty prompt, API error, or network error, treat that as a UI state, not a control-logic conclusion.
11. Restate the boundary before presenting: deterministic controlled demo layer, built-in `nominal-deploy` / `retract-reset` scenarios, simplified first-cut plant, not a full LLM, and not a complete physical model.

## Demo Path

1. Prompt: `logic4 和 throttle lock 有什么关系`

[Say] "This bridges the upstream `logic4` gate to the downstream `THR_LOCK` release command."

[Point] Use the control chain to show the `logic4 / THR_LOCK` highlight. Then point to `highlight explanation` and the `raw JSON` panel so the audience can see `matched_node` / `target_logic` driving the highlight.

2. Prompt: `为什么 throttle lock 没释放`

[Say] "This is the controlled diagnosis path for the release window: if throttle lock has not released yet, we check the logic4 gate and the deploy feedback evidence."

[Point] Use the `structured answer` area, especially `possible_causes`, `evidence`, and `risks`. Keep the `raw JSON` panel visible as the machine-readable debug view.

3. Prompt: `触发 logic3 会发生什么`

[Say] "This shows a trigger-node answer: `logic3` becoming active fans out to EEC deploy, PLS power, and PDU motor commands."

[Point] Use the control chain to show `logic3` plus the `EEC / PLS / PDU` command subnode highlights. Then point to `structured answer` for the evidence and outcome window.

4. Prompt: `把 logic3 的 TRA 阈值改成 -8 会发生什么`

[Say] "This is a dry-run proposal, not an edit. It explains the impact of a hypothetical TRA threshold change without modifying `controller.py`."

[Point] Use `structured answer` to show the dry-run proposal, `required_changes`, and `risks`. Then point to `raw JSON` to show the same answer fields as arrays.

## Closing

[Boundary] "The result is based on built-in `nominal-deploy` / `retract-reset` and the simplified first-cut plant. The proposal does not directly modify `controller.py`; it only reports impact."

[Boundary] "If the UI shows loading, empty prompt, API error, or network error, treat that as a UI state. It is not a control-logic conclusion and not a physical diagnosis."

[Boundary] "For deeper manual checks, run `PYTHONPATH=src python3 tools/demo_ui_handcheck.py`; for the shorter presenter flow, run `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`."
