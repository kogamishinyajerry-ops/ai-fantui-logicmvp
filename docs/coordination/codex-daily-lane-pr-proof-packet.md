# Codex Daily Lane PR Proof Packet

Every Codex Daily Lane PR must include this packet in the PR body.

```text
Linear: JER-XXX
Adapter: <project|thrust-reverser|c919-etras|...>
Layer: L<n>
Truth-level impact: none|demonstrative|certified
Red lines touched: none|R1|R2|R3|R4|R5
Test delta: <targeted pytest>; <default pytest>; <GSD validation>; <adversarial if UI/API>
```

## Editable Workbench Defaults

- Editable graph status is always `sandbox_candidate`.
- Hardware binding truth effect is always `none`.
- Candidate graph outputs are never certified truth.
- Baseline comparisons must cite the adapter/controller source used for the
  comparison.
- e2e 49/49 and `mypy --strict clean` must not be claimed unless those commands
  are explicitly run and pass in the current PR.

## Required Evidence

- Targeted tests for the changed subsystem.
- Default pytest or a documented scoped alternative when runtime makes full
  pytest impossible.
- `tools/run_gsd_validation_suite.py --format json` result.
- `src/well_harness/static/adversarial_test.py` for UI/API surfaces that can
  affect user-visible control-state interpretation.

## Record-Only Notion Policy

Notion comments/pages can record what happened, but they do not approve a Codex
Daily Lane PR. The daily merge gate is Linear issue contract plus GitHub PR plus
validation evidence.

