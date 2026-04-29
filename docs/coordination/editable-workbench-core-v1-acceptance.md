# Editable Workbench Core v1 Acceptance

JER-160 closes the first editable-workbench milestone by proving the loop is
deterministic and auditable without turning sandbox output into certified truth.
JER-169 extends the same bundle into Runtime v3 by accepting `/workbench` UI
draft requests and archiving graph validation, sandbox run, and known gate
blocker evidence.

## Acceptance Path

1. Derive the thrust-reverser reference draft with
   `derive_baseline_draft()`.
2. Apply a deterministic sandbox edit with `apply_rule_threshold_edit()`.
3. Run the candidate through the existing timeline sandbox.
4. Compare candidate output against the certified
   `ReferenceDeployControllerAdapter` / `FantuiExecutor` baseline.
5. Generate a draft-only ChangeRequest and Codex PR proof packet.
6. Archive the evidence bundle with SHA256 checksums.

Runtime v3 can also start from `build_runtime_v3_acceptance_bundle_from_ui_draft()`,
which proves the UI draft -> canonical model -> validation report -> sandbox
diff -> archive handoff path.

## Evidence Bundle Files

`archive_editable_workbench_acceptance_bundle()` writes:

- `bundle.json`
- `model.json`
- `validation_report.json`
- `sandbox_run.json`
- `candidate_trace.json`
- `diff_report.json`
- `change_request.json`
- `known_blockers.json`
- `pr_proof_packet.md`
- `README.md`
- `manifest.json`

The manifest records SHA256 integrity for every evidence file. Validation uses
`validate_editable_workbench_acceptance_manifest()`.

## Stop Rules Exercised

The acceptance layer rejects:

- non-`thrust-reverser` candidates in this milestone path
- `truth_status="certified"` candidate claims
- `controller_truth_modified=true`
- `truth_level_impact != "none"`
- `dal_pssa_impact != "none"`
- non-`fantui` timelines
- checksum drift in archived files

## Boundaries

- `src/well_harness/controller.py` remains the certified thrust-reverser truth.
- C919 E-TRAS remains read-only/frozen.
- The bundle is evidence, not approval.
- No product LLM/chat path is restored.
