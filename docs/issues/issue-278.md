---
type: issue
state: closed
created: 2026-03-12T13:36:04Z
updated: 2026-03-12T17:33:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/278
comments: 0
labels: chore, priority:medium, area:ci, area:workspace, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:57.334Z
---

# [Issue 278]: [[CHORE] Add sync-main-to-dev workflow to manifest sync](https://github.com/vig-os/devcontainer/issues/278)

## Chore Type
CI / Build change

## Description
Add `.github/workflows/sync-main-to-dev.yml` to `scripts/manifest.toml` so the workflow is included in workspace sync output and remains consistent between the root repo and workspace template.

## Acceptance Criteria
- [ ] Add a new manifest entry for `.github/workflows/sync-main-to-dev.yml` in `scripts/manifest.toml`
- [ ] Verify the manifest entry appears in `uv run python scripts/sync_manifest.py list`
- [ ] Sync output includes the workflow in workspace artifacts as expected

## Implementation Notes
- Target file: `scripts/manifest.toml`
- Keep the change minimal (single new `[[entries]]` item, no unrelated manifest edits)

## Related Issues
Related to #169

## Priority
Medium

## Changelog Category
No changelog needed

## Additional Context
This keeps shipped workflow files aligned with the manifest-driven sync process and reduces drift risk.
