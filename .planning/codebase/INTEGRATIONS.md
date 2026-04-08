# Integrations

## Notion

The Notion control tower is configured in `.planning/notion_control_plane.json`.
`tools/gsd_notion_sync.py` reads `NOTION_API_KEY` and writes GSD run state into the control tower databases.

## GitHub

`.github/workflows/gsd-automation.yml` runs the same automation bridge in CI.
Configure the repository secret `NOTION_API_KEY` before expecting Notion writeback from GitHub Actions.
