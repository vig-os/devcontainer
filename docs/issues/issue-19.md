---
type: issue
state: closed
created: 2025-12-16T13:17:38Z
updated: 2026-01-30T15:17:32Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/19
comments: 0
labels: bug
assignees: gerchowl
milestone: 0.2
projects: none
relationship: none
synced: 2026-02-18T08:56:41.191Z
---

# [Issue 19]: [[BUG] Missing docker-compose.local.yaml causes test failures](https://github.com/vig-os/devcontainer/issues/19)

### Description

The `devcontainer.json` references `docker-compose.local.yaml` in the `dockerComposeFile` array, but this file does not exist in the workspace template. This causes:

1. **Image tests to fail**: The test expects the file to exist at `/root/assets/workspace/.devcontainer/docker-compose.local.yaml`
2. **Integration tests to fail**: Podman compose validation fails when trying to validate the devcontainer configuration because the referenced file is missing

### Steps to Reproduce

1. Run `make test-image`
2. Observe failure in `TestFileStructure.test_assets_workspace_structure`:
   \`\`\`
   AssertionError: Expected file not found: /root/assets/workspace/.devcontainer/docker-compose.local.yaml
   \`\`\`

3. Run `make test-integration`
4. Observe multiple test failures with error:
   \`\`\`
   missing files: ['/home/carlosvigo/Documents/vigOS/devcontainer/tests/tmp/workspace-devcontainer-*/.devcontainer/docker-compose.local.yaml']
   Error: executing /usr/bin/podman-compose ... exit status 1
   \`\`\`

### Expected Behavior

- Image tests should pass - the file should exist in the workspace template
- Integration tests should pass - podman compose should be able to validate the configuration
- The file should be created as an empty/commented template file (similar to `docker-compose.project.yaml`) since it's meant for user-specific local overrides

### Actual Behavior

- Image test fails because the expected file doesn't exist
- Integration tests fail because podman compose cannot validate a configuration referencing a missing file
- All 17 integration tests fail due to the devcontainer setup failure

### Environment

- **OS**: Linux 6.14.0-37-generic (Ubuntu)
- **Container Runtime**: Podman 4.9.3, podman-compose 1.0.6
- **Image Version/Tag**: dev
- **Architecture**: AMD64
- **Dev Containers CLI**: @devcontainers/cli 0.80.1

### Additional Context

**Test Output:**

\`\`\`
make test-image:
FAILED tests/test_image.py::TestFileStructure::test_assets_workspace_structure
AssertionError: Expected file not found: /root/assets/workspace/.devcontainer/docker-compose.local.yaml

make test-integration:
ERROR tests/test_integration.py::TestPodmanSocketAccess::test_simple_image_build
Failed: devcontainer up failed
missing files: ['.../docker-compose.local.yaml']
Error: executing /usr/bin/podman-compose ... exit status 1

37 passed, 4 skipped, 17 errors in 12.43s
\`\`\`

**Current State:**
- `docker-compose.project.yaml` exists in the template (for team-shared config)
- `docker-compose.local.yaml` is referenced in `devcontainer.json` but doesn't exist
- The file is intended to be gitignored (user-specific, not shared)
- Docker Compose requires all files in `dockerComposeFile` array to exist, even if empty

**Related Files:**
- `assets/workspace/.devcontainer/devcontainer.json` - references the missing file
- `assets/workspace/.devcontainer/docker-compose.project.yaml` - example of similar file
- `tests/test_image.py:277` - test expects the file to exist
- `assets/workspace/.devcontainer/.gitignore` - should ignore `docker-compose.local.yaml`

### Possible Solution

1. **Create an empty template file** `assets/workspace/.devcontainer/docker-compose.local.yaml` with:
   - Comments explaining it's for user-specific local overrides
   - Instructions that it's gitignored
   - Similar structure to `docker-compose.project.yaml` but for local use

2. **Ensure `.gitignore` excludes it** (already done, but verify):
   - The file should be in `.gitignore` so users can create their own local overrides

3. **Update `init-workspace.sh`** (if needed):
   - Ensure the file is copied/created during workspace initialization
   - Or create it if missing during initialization

4. **Alternative approach** (if docker-compose supports optional files):
   - Make the file optional in `devcontainer.json` if the devcontainers spec supports it
   - However, this may not be supported by docker-compose itself

**Recommended approach:** Create an empty template file with helpful comments, similar to `docker-compose.project.yaml`, so docker-compose validation succeeds while still allowing users to customize it locally.

