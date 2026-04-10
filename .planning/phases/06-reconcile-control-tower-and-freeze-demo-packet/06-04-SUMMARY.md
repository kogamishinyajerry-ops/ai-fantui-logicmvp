# P6-04 Summary - Route Active Status Links To An Auto-Synced Replacement Page

## Outcome

`P6-04` removes the stale archived `01 当前状态` page from the active control-plane path by promoting a new auto-synced replacement page as the live status surface.

## What Changed

- Created a new `01 当前状态（自动同步）` page under the control-tower root where the current integrations have full write access.
- Pointed `pages.status` at that new page in the control-plane config.
- Extended `tools/gsd_notion_sync.py` so the replacement status page is fully regenerated from the same live review snapshot used by 09C, the dashboard, and the freeze packet.

## Verification

- Control-plane sync tests now cover the rendered replacement status page content.
- Dashboard, 09C, and freeze packet can all link to the new status page through the shared config pointer.
- The stale archived status page no longer needs to be user-facing, even though it still exists historically inside Notion.

## Notes

- The original `01 当前状态` page remains blocked by archived-ancestor constraints and is now treated as a historical artifact.
- P6 still has some archived-ancestor database rows that cannot be edited in place, but the user-facing status surface is no longer one of them.
