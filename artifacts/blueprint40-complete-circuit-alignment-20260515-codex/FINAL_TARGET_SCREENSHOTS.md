# Final Target Screenshots

Source artifact: `artifacts/blueprint40-complete-circuit-alignment-20260515-codex`.

Selection rule: use the current Codex minimal workbench screenshots at `desktop-1366x768` as the canonical visual targets. The `desktop-1280x820` captures remain responsive guard evidence only.

## Selected Target Set

| ID | Route state | Target screenshot | Acceptance role |
|---|---|---|---|
| T01 | Requirements intake default | `requirements-intake--desktop-1366x768.png` | Source intake, provider/status rhythm, and first transition into drawing. |
| T02 | Logic builder real circuit canvas | `logic-builder--desktop-1366x768.png` | Primary real graph renderer target: full `20 circuit nodes / 23 wires`, compact stream chip, and canvas-first layout. |
| T03 | Fault injection preparation | `fault-injection-prepare--desktop-1366x768.png` | Candidate fault matrix, compact top process, selected candidate path, and right inspector balance. |
| T04 | Sandbox default workbench | `fault-injection-sandbox-default--desktop-1366x768.png` | Main sandbox target: replay canvas, active path, status-only right report rail, and compact evidence trace. |
| T05 | Sandbox report package preview | `fault-injection-sandbox--desktop-1366x768.png` | Explicit export/report package state with full review, evidence, and report rows. |

## Guard-Only Captures

These files are not final visual targets, but keep the selected targets honest across viewport and audit contexts:

- `requirements-intake--desktop-1280x820.png`
- `logic-builder--desktop-1280x820.png`
- `fault-injection-prepare--desktop-1280x820.png`
- `fault-injection-sandbox-default--desktop-1280x820.png`
- `fault-injection-sandbox--desktop-1280x820.png`
- `reference-current-contact-sheet.png`

## Style Lock

- The selected target set is Codex minimal workbench style: white shell, restrained blue/green state color, compact nav/process bars, and no decorative mock illustration.
- Targets are current UI captures, not manually mocked V2 images.
- `visual-acceptance-summary.json` reports all five selected route states as `ok=true` at `desktop-1366x768`.
