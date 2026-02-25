---
type: issue
state: open
created: 2026-02-24T16:00:23Z
updated: 2026-02-24T16:00:23Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/185
comments: 0
labels: chore, priority:medium, area:image, area:workspace, effort:medium, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:52.357Z
---

# [Issue 185]: [[CHORE] Make container scripts callable via PATH and manifest sync](https://github.com/vig-os/devcontainer/issues/185)

## Chore Type
Configuration change

## Description
Create a dedicated scripts folder inside the container image, add it to `PATH`, and reorganize script locations so runtime/deploy script usage is explicit.

Goal: scripts that should run inside the devcontainer are directly callable without path prefixes, while deploy-only scripts are moved out of the local-tooling path.

## Acceptance Criteria
- [ ] A scripts directory exists in the container image and is added to `PATH`
- [ ] Deploy-only tools are moved to `assets/scripts` (including `assets/init-workspace.sh` as applicable)
- [ ] Scripts intended for both local tooling and deploy usage are declared in `scripts/manifest.toml` for sync
- [ ] Devcontainer session can invoke intended scripts directly by command name (no relative path required)
- [ ] Documentation/config references are updated to match the new locations

## Implementation Notes
- Update container build/runtime config to export the scripts directory in `PATH`
- Move deploy-only assets to `assets/scripts` and keep naming/permissions consistent
- Use `scripts/manifest.toml` as the source of truth for scripts that must be synced into the devcontainer workspace/runtime
- Validate behavior by entering the devcontainer and calling moved/synced commands directly

## Related Issues
- Related to #70
- Related to #89

## Priority
Medium

## Changelog Category
Changed

## Additional Context
Requested outcome: “scripts are callable from within the devcontainer”.
