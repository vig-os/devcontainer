---
type: pull_request
state: closed (merged)
branch: c-vigo/issue3 → dev
created: 2025-11-26T16:14:03Z
updated: 2025-11-26T16:15:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/pull/4
comments: 0
labels: none
assignees: c-vigo
milestone: Initial release
projects: none
relationship: none
merged: 2025-11-26T16:15:10Z
synced: 2026-02-18T08:57:16.550Z
---

# [PR 4](https://github.com/vig-os/devcontainer/pull/4) [BREAKING] Add multi-project support via subdirectory mounting and compose overrides

## Description

This PR implements the ability to mount projects in subdirectories of `/workspace` instead of directly at `/workspace`. This enables multi-project development by allowing multiple repositories to be mounted simultaneously in a single devcontainer.

The implementation includes:
- Project mounting to `/workspace/<project_name>` subdirectory structure
- Docker Compose override support for mounting additional folders
- Comprehensive documentation and examples
- Full integration test coverage

## Related Issue(s)

Closes #3

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [x] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update
- [ ] Refactoring (no functional changes)
- [x] Test updates

## Changes Made

### Core Mount Structure Changes
- Changed default project mount from `/workspace` to `/workspace/<project_name>` subdirectory
- Updated `workspaceFolder` in devcontainer.json to `/workspace/{{SHORT_NAME}}`
- Modified `docker-compose.yml` to use relative path (`..`) for project mounting
- Updated `postAttachCommand` path to match new subdirectory structure
- Adjust all initialization scripts (`init-git.sh`, `init-precommit.sh`, `setup-git-conf.sh`, `post-attach.sh`)

### Environment Variable Cleanup
- Removed redundant `PYTHONUNBUFFERED` and `IN_CONTAINER` from docker-compose.yml (inherited from base image)
- Removed `PRE_COMMIT_HOME` from Containerfile (now project-specific, set in docker-compose.yml)
- Added `PROJECT_ROOT` environment variable for script consistency

### Docker Compose Override Support
- Added `.devcontainer/.gitignore` to ignore user-specific override files
- Created `docker-compose.override.yml.example` template with common mount patterns
- Added comprehensive `MOUNTS.md` documentation (169 lines) covering:
  - Quick start guide
  - Mount patterns (sibling projects, home directory, absolute paths, read-only)
  - Troubleshooting and performance considerations
  - Real-world examples (monorepo, frontend+backend, reference docs)
- Updated README.md with mounting section and quick start

### Testing Infrastructure
- Modified `conftest.py` fixture to test override functionality:
  - Creates test override file mounting tests directory
  - Updates devcontainer.json to include override (required for devcontainer CLI)
  - Proper cleanup after tests
- Added `TestDockerComposeOverride` test class with 4 integration tests:
  - Directory existence verification
  - File accessibility checks
  - File reading operations
  - Directory listing and multiple file validation

### Test Updates
- Updated 15+ integration tests to expect subdirectory mount structure
- Modified tests to check for relative path (`..`) in volumes
- Updated all path references from `/workspace` to `/workspace/test_project`
- Removed `test_pre_commit_home_set` from image tests (no longer in base image)
- Added test for no redundant `containerEnv` in devcontainer.json

## Testing

- [x] Tests pass locally (`make test`)
- [x] Image tests pass (`make test-image`)
- [x] Integration tests pass (`make test-integration`)
- [ ] Registry tests pass (`make test-registry`) (if applicable)
- [x] Manual testing performed (describe below)

### Manual Testing Details

1. **Subdirectory Mounting**: Verified project mounts to `/workspace/<project_name>` correctly
2. **Override Functionality**: Tested mounting additional folders using `docker-compose.override.yml`:
   - Mounted sibling project successfully
   - Verified file access and permissions
   - Confirmed directory listing works
3. **Script Execution**: All initialization scripts (`init-git.sh`, `init-precommit.sh`, `post-attach.sh`) run without errors
4. **VS Code Integration**: Dev Container opens to correct workspace folder
5. **Multi-project Setup**: Successfully mounted and accessed multiple projects simultaneously

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have updated the documentation accordingly (README.md, CONTRIBUTE.md, etc.)
- [ ] I have updated the CHANGELOG.md in the `[Unreleased]` section
- [x] My changes generate no new warnings or errors
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

### Breaking Change Notice
This is a **breaking change** from any previous devcontainer setup (though no official release exists yet). Projects using the old structure will need to:
1. Update their `.devcontainer` configuration with the new template
2. Adjust any scripts referencing `/workspace` to use the new subdirectory structure

### Key Implementation Details

**Mount Resolution**: The implementation uses `..` (relative path) instead of `${localWorkspaceFolder}` because:
- The devcontainer CLI doesn't expand `${localWorkspaceFolder}` correctly with podman-compose
- Relative paths work consistently across Docker and Podman
- The path is relative to the `.devcontainer` directory

**Override File Handling**: For the devcontainer CLI to use override files, they must be explicitly listed in `devcontainer.json`:
"dockerComposeFile": [
  "docker-compose.yml",
  "docker-compose.override.yml"
]VS Code's Dev Containers extension handles this automatically, but manual CLI usage requires explicit configuration.

### Benefits
- Enables multi-project development workflows
- Better workspace organization
- Supports monorepo and microservices architectures
- Per-developer customization without git conflicts
- Standard Docker Compose patterns
- Comprehensive documentation and examples


---
---

## Commits

### Commit 1: [682e548](https://github.com/vig-os/devcontainer/commit/682e5486832697b94a6cb489ff151b65f18bbba5) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 02:10 PM
switch to docker-compose for devcontainer orchestration, 248 files modified (assets/workspace/.devcontainer/devcontainer.json, assets/workspace/.devcontainer/docker-compose.yml, tests/test_integration.py)

### Commit 2: [05892d7](https://github.com/vig-os/devcontainer/commit/05892d79dd98c3bf0a98ee437c35fd23b4f24b8a) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 02:14 PM
update uv version to 0.9.12, 4 files modified (scripts/setup.sh, tests/test_image.py)

### Commit 3: [fe798c4](https://github.com/vig-os/devcontainer/commit/fe798c4e1d08bec0880c04f1b760fe20b91d7659) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 03:40 PM
Mount project to /workspace subdirectory instead of root, 158 files modified

### Commit 4: [5a11186](https://github.com/vig-os/devcontainer/commit/5a111866eaddfc52ae67dd056f2e51a14c4167d0) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:06 PM
Add docker-compose override support for mounting additional folders, 440 files modified
