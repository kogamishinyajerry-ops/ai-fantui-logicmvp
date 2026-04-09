# GSD Notion Automation Loop

This repo now treats GitHub / the local checkout as the code truth plane and Notion as the control plane.

Current GitHub repo:

- `https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp`

## Local Run

```bash
python3 tools/run_gsd_validation_suite.py --format json

python3 tools/gsd_notion_sync.py run \
  --title "Local GSD automation smoke" \
  --command "python3 tools/run_gsd_validation_suite.py --format json"
```

If `NOTION_API_KEY` is set, the run writes:

- `02B Execution Run 数据库`
- `05 QA / 验证数据库`
- `02A GSD Plan 数据库`
- `05A UAT Gap 数据库` on failure

Add `--opus-gate` only when the run should pause for an Opus 4.6 intervention that uses Notion pages plus the GitHub repo as evidence.

## GitHub Actions

`.github/workflows/gsd-automation.yml` reuses the same bridge command, and `tools/run_gsd_validation_suite.py` is the shared validation entrypoint behind it.

Required repository secret:

- `NOTION_API_KEY`

If the secret is missing, the script still runs validation commands and skips Notion writeback, so CI remains safe while secrets are being configured.

The validation suite stops on the first failing check and emits a compact JSON report, so a single command can feed both GitHub Actions evidence and Notion QA digests without drifting command lists.

The active plan is routed from `.planning/notion_control_plane.json` instead of being hardcoded in the GitHub workflow, which keeps future phase changes aligned across local runs, CI, and Notion writeback.

When 09C is refreshed, the control plane now prefers GitHub Action Execution Run rows and their matching QA records over newer local Codex runs. This keeps current Opus briefs aligned with the GitHub evidence plane instead of drifting toward local-only diagnostic artifacts.

GitHub-backed run rows also store the exact Actions run URL, and the shared validation suite emits stable `python3 ...` command labels so local machine paths do not leak into Notion evidence summaries.

## Manual Review Rule

The only intended manual stop is:

```text
04A Review Gate 数据库 -> Status = Awaiting Opus 4.6
```

Everything else should either pass automatically or create a UAT Gap that feeds back into the next GSD plan.

## Current Brief Refresh

Before you manually trigger Opus 4.6, refresh the current brief:

```bash
python3 tools/gsd_notion_sync.py prepare-opus-review --activate-gate
```

That command reads the current Notion state and rewrites `09C 当前 Opus 4.6 审查简报` so Opus gets a situational request, not a frozen prompt template.

If the current state does not actually require subjective review, the refreshed brief now explicitly says `当前无需 Opus 审查` and tells you to keep the loop moving. A non-activating refresh also preserves existing Review Gate decision notes instead of wiping approved conclusions.

## Legacy Gap Cleanup

If a plan previously produced one or more `Automation failure: <plan>` gap records, a later successful run for that same plan now auto-resolves those open legacy gaps. Duplicate sibling records are marked as duplicates in the resolution note so the audit trail stays intact without leaving stale blockers open.

## Opus Packet Rule

When you manually trigger Opus 4.6 inside Notion AI:

- Use the Notion control tower pages and databases as the state source.
- Use the GitHub repo and GitHub Actions runs as the code/evidence source.
- Do not cite local terminal file paths, local shell output, or unstaged local-only context.
- Treat older browser hand-check notes in archived repo docs as historical context only, not as the current approval workflow.
- Do not use a generic canned prompt; always start from the freshly generated `09C 当前 Opus 4.6 审查简报`.
