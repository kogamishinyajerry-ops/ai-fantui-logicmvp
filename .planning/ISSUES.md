# Deferred Issues

## Auto-Supersede Legacy Gaps

Status: Done

The control-plane rule now detects superseding success evidence and marks same-plan legacy gaps as resolved automatically, with duplicate sibling records labeled as duplicates.

## Unified Validation Entrypoint

Status: Done

Local runs, GitHub Actions, and Notion writeback now share `tools/run_gsd_validation_suite.py`, so the validation command list no longer drifts across automation surfaces.

## GitHub-First Review Evidence

Status: Done

Review snapshots and current Opus briefs now prefer GitHub Action runs and matching GitHub QA records over local Codex runs, and GitHub-backed run rows carry the exact Actions run URL.

## GitHub Actions Node24 Compatibility

Status: Done

The workflow now uses Node24-compatible GitHub Actions versions and opts into `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`, so the control loop stays ahead of the Node20 runner deprecation.

## Opus Review Brief Maintenance

Status: Open

The current Opus 4.6 review brief generator must stay aligned with the latest Notion control-tower structure and the GitHub repo URL. If the review inputs change, update the brief generator and the 09C page first.

## GitHub Remote Push

Status: Done

The local repo is now pushed to GitHub and the automation workflow is live.
