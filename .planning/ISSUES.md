# Deferred Issues

## Browser Hand-Check Automation

Status: Open

The cockpit UI still has a manual browser hand-check gap. Phase P2 should replace it with a reproducible validation path that can write results through `tools/gsd_notion_sync.py`.

## GitHub Remote Push

Status: Open

The local repo can be initialized now, but this process currently does not see `GITHUB_TOKEN` or `GH_TOKEN`, and `gh` is not authenticated. Create/push the GitHub remote after authentication is available.
