---
type: issue
state: open
created: 2026-02-24T16:00:23Z
updated: 2026-03-04T08:57:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/185
comments: 1
labels: chore, priority:medium, area:image, area:workspace, effort:medium, semver:minor
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-05T04:18:19.861Z
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
---

# [Comment #1]() by [c-vigo]()

_Posted on March 4, 2026 at 07:00 AM_

Subsumed by #217: [REFACTOR] Reorganize scripts/ — project-specific vs shared vig-utils. Path/callability changes are now tracked under the consolidated reorganization issue.

