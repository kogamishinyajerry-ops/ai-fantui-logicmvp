# Blueprint 40 Coverage

Source reference list: `artifacts/blueprint-ui-detail-audit-20260515-codex/README.md`.

Acceptance summary: `visual-acceptance-summary.json` reports `ok=true`, `route_count=5`, and `screenshot_count=10`.

Final selected targets: `FINAL_TARGET_SCREENSHOTS.md` narrows the canonical Codex minimal target set to five `desktop-1366x768` screenshots.

## Reference To Current Mapping

| # | Reference screenshot | Current counterpart |
|---|---|---|
| 1 | `artifacts/blueprint37-right-rail-20260515-codex/requirements-intake--desktop-1366x768.png` | `requirements-intake--desktop-1366x768.png` |
| 2 | `artifacts/blueprint37-right-rail-20260515-codex/logic-builder--desktop-1366x768.png` | `logic-builder--desktop-1366x768.png` |
| 3 | `artifacts/blueprint37-right-rail-20260515-codex/fault-injection-prepare--desktop-1366x768.png` | `fault-injection-prepare--desktop-1366x768.png` |
| 4 | `artifacts/blueprint37-right-rail-20260515-codex/sandbox-right-rail-desktop-1366x768.png` | `fault-injection-sandbox-default--desktop-1366x768.png` |
| 5 | `artifacts/deepseek-ui-visual-acceptance-20260515-blueprint37-wide-canvas-report-system-codex/fault-injection-sandbox-blueprint37-wide-canvas-report-system--desktop-1366x768.png` | `fault-injection-sandbox-default--desktop-1366x768.png` |
| 6 | `artifacts/deepseek-ui-visual-acceptance-20260515-blueprint37-main-canvas-report-rail-codex/fault-injection-sandbox-blueprint37-main-canvas-report-rail--desktop-1366x768.png` | `fault-injection-sandbox-default--desktop-1366x768.png` |
| 7 | `artifacts/blueprint37-right-rail-20260515-codex/fault-injection-sandbox--desktop-1366x768.png` | `fault-injection-sandbox--desktop-1366x768.png` |

## Current State Notes

- The visual acceptance seed now imports the real L1-L4 circuit builder from `src/`, so the logic-builder screenshots use the full `20 circuit nodes / 23 wires` renderer instead of the fallback 3-node graph.
- The sandbox route is captured in two states: default workbench (`fault-injection-sandbox-default`) and explicit report package preview (`fault-injection-sandbox`).
- The default sandbox right rail keeps all report/evidence rows in the DOM, but only the active report and active trace are visible in `status-only` mode.
- The contact sheet `reference-current-contact-sheet.png` pairs every reference screenshot with its current counterpart.
