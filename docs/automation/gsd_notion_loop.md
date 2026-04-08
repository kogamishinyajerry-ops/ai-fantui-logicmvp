# GSD Notion Automation Loop

This repo now treats GitHub / the local checkout as the code truth plane and Notion as the control plane.

## Local Run

```bash
python3 tools/gsd_notion_sync.py run \
  --title "Local GSD automation smoke" \
  --command "PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'"
```

If `NOTION_API_KEY` is set, the run writes:

- `02B Execution Run 数据库`
- `05 QA / 验证数据库`
- `02A GSD Plan 数据库`
- `05A UAT Gap 数据库` on failure

Add `--opus-gate` only when the run should pause for manual Opus 4.6 review.

## GitHub Actions

`.github/workflows/gsd-automation.yml` reuses the same script.

Required repository secret:

- `NOTION_API_KEY`

If the secret is missing, the script still runs validation commands and skips Notion writeback, so CI remains safe while secrets are being configured.

## Manual Review Rule

The only intended manual stop is:

```text
04A Review Gate 数据库 -> Status = Awaiting Opus 4.6
```

Everything else should either pass automatically or create a UAT Gap that feeds back into the next GSD plan.
