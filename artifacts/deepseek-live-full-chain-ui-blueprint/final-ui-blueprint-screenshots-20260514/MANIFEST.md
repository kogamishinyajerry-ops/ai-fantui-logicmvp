# Final UI Blueprint Screenshot Pack

Generated: 2026-05-14

Source image folder:

`/Users/Zhuanz/.codex/generated_images/019e249a-982c-7480-8468-0d44ae38d19d`

Pack folder:

`/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/requirements-intake-webui/artifacts/deepseek-live-full-chain-ui-blueprint/final-ui-blueprint-screenshots-20260514`

## Structure

- `screenshots/`: all 39 generated blueprint screenshots, renamed in generation order.
- `selected-final-set/`: 14 curated screenshots for the final UI blueprint handoff.
- `MANIFEST.md`: this file.
- `BLUEPRINT_UI_DEVELOPMENT_BRIEF.md`: implementation brief plus copy-paste prompt for a new Codex session.

## Selected Final Set

1. `14-selected-overview-board.png`
2. `27-global-nav-default-workbench.png`
3. `28-command-palette-advanced-entry.png`
4. `29-blank-canvas-template-entry.png`
5. `30-docx-template-generated-canvas.png`
6. `31-running-signal-propagation.png`
7. `32-parameter-drawer-final.png`
8. `33-fault-injection-final.png`
9. `34-failure-diagnosis-path.png`
10. `35-evidence-trace-final.png`
11. `36-sandbox-review-final.png`
12. `37-replay-report-final.png`
13. `38-panel-state-strategy-final.png`
14. `39-concept-video-storyboard.png`

## Implementation Intent

This pack defines the target UI direction for the DeepSeek V4 Pro driven reverse-logic demo flow:

- default canvas-first workspace
- only five default exposed entries: canvas, run, parameters, evidence, report
- advanced actions through command palette, drawers, tabs, and inspectors
- reduced web viewport with no required vertical scrolling
- collapsible left rail and right inspector
- bottom parameter/simulation drawer
- preserved simulation, fault injection, sandbox review, evidence trace, replay, and report flows
- sandbox-only framing: `truth_effect:none`, `candidate_state:sandbox_candidate`, `certification_claim:none`, `controller_truth_modified:false`

## Notes

The original generated images remain in the Codex generated-images folder. This pack is a project-local copy for implementation planning, handoff, and review.
