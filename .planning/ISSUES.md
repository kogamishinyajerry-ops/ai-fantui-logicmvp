# Deferred Issues

## Auto-Supersede Legacy Gaps

Status: Done

The control-plane rule now detects superseding success evidence and marks same-plan legacy gaps as resolved automatically, with duplicate sibling records labeled as duplicates.

## Unified Validation Entrypoint

Status: Done

Local runs, GitHub Actions, and Notion writeback now share `tools/run_gsd_validation_suite.py`, so the validation command list no longer drifts across automation surfaces.

## Opus Review Brief Maintenance

Status: Open

The current Opus 4.6 review brief generator must stay aligned with the latest Notion control-tower structure and the GitHub repo URL. If the review inputs change, update the brief generator and the 09C page first.

## GitHub Remote Push

Status: Done

The local repo is now pushed to GitHub and the automation workflow is live.
