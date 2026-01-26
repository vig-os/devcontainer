---
type: pull_request
state: closed (merged)
branch: c-vigo/issue2 → dev
created: 2025-11-26T16:58:45Z
updated: 2025-11-26T16:59:05Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/pull/5
comments: 0
labels: none
assignees: c-vigo
milestone: Initial release
projects: none
relationship: none
merged: 2025-11-26T16:59:02Z
synced: 2026-01-09T16:17:54.240Z
---

# [PR 5](https://github.com/vig-os/devcontainer/pull/5) Add GitHub templates for issues and pull requests

## Description

This PR adds GitHub issue and PR templates for better project contribution workflow, and enhances test coverage to verify the complete workspace asset structure including all template files and scripts.

## Related Issue(s)

Closes #2

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update
- [ ] Refactoring (no functional changes)
- [x] Test updates

## Changes Made

### GitHub Templates
- Added issue templates using GitHub Forms (YAML) format:
  - `bug_report.yml` - structured bug reporting with environment details and reproduction steps
  - `feature_request.yml` - feature proposals with problem statement and impact analysis
  - `task.yml` - task tracking with acceptance criteria and priority selection
- Added `pull_request_template.md` with testing checklist and change type classification
- Templates added to both main repository and workspace template (assets/workspace/)

### Test Enhancements
- Enhanced `test_assets_workspace_structure` in `test_image.py`:
  - Comprehensive validation of all workspace asset directories (workspace root, .devcontainer, scripts, githooks)
  - Validates all template files exist (gitignore, configs, documentation, scripts)
  - Verifies shell script executability for all .sh files
  - Uses arrays and loops for maintainable test structure
- Added `test_docker_compose_override_example_exists` to verify override template file
- Added `test_docker_compose_gitignore` to verify gitignore configuration
- Removed redundant `test_workspace_template_pre_commit_config_exists` (covered by structure test)

### Bug Fixes
- Fixed error message for uv version check in test to show correct expected version (0.9.12)

## Testing

- [x] Tests pass locally (`make test`)
- [x] Image tests pass (`make test-image`)
- [x] Integration tests pass (`make test-integration`)
- [x] Registry tests pass (`make test-registry`) (if applicable)
- [x] Manual testing performed (describe below)

### Manual Testing Details

1. **Template Validation**: Verified all GitHub templates render correctly in GitHub UI
2. **Asset Structure**: Confirmed all workspace template files are present and properly structured
3. **Test Coverage**: All new tests pass and properly validate expected structure
4. **Shell Scripts**: Verified executable permissions are checked correctly

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have updated the documentation accordingly (README.md, CONTRIBUTE.md, etc.)
- [ ] I have updated the CHANGELOG.md in the `[Unreleased]` section
- [x] My changes generate no new warnings or errors
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] Any dependent changes have been merged and published

## Additional Notes

### Statistics
- 9 files changed: 583 insertions, 14 deletions
- 8 new template files (4 for main repo, 4 for workspace template)
- Enhanced test coverage with structural validation

### Template Files Added
**Main Repository:**
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/task.yml`
- `.github/pull_request_template.md`

**Workspace Template:**
- `assets/workspace/.github/ISSUE_TEMPLATE/bug_report.yml`
- `assets/workspace/.github/ISSUE_TEMPLATE/feature_request.yml`
- `assets/workspace/.github/ISSUE_TEMPLATE/task.yml`
- `assets/workspace/.github/pull_request_template.md`

### Benefits
- Standardized issue and PR submission process
- Better contributor experience with guided templates
- Comprehensive asset structure validation prevents deployment issues
- Enhanced test maintainability with array-based validation


---
---

## Commits

### Commit 1: [f8c4522](https://github.com/vig-os/devcontainer/commit/f8c45227866e42b7f55c3e3a68594c023c5144b3) by [c-vigo](https://github.com/c-vigo) on November 25, 2025 at 09:44 AM
Add GitHub issue and PR templates for this project, 258 files modified (.github/ISSUE_TEMPLATE/bug_report.yml, .github/ISSUE_TEMPLATE/feature_request.yml, .github/ISSUE_TEMPLATE/task.yml, .github/pull_request_template.md)

### Commit 2: [ef2d3ea](https://github.com/vig-os/devcontainer/commit/ef2d3ea39d0cb1630486341594b1c3b0d1d684e2) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:34 PM
add issue and PR templates to assets, 258 files modified

### Commit 3: [7b1b183](https://github.com/vig-os/devcontainer/commit/7b1b183f9ceb0e593b077f0c7bff669bf8285877) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:39 PM
add tests to verify all files inside assets, 65 files modified (tests/test_image.py)

### Commit 4: [118060c](https://github.com/vig-os/devcontainer/commit/118060c5e70c7cafb963da1a0d076d6a9f178cd2) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:45 PM
Merge branch 'dev' into c-vigo/issue2, 818 files modified

### Commit 5: [0615c81](https://github.com/vig-os/devcontainer/commit/0615c81905758757352c6dc6bdf07db6767b2a6f) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:49 PM
fix error message for uv version, 2 files modified (tests/test_image.py)

### Commit 6: [68bf2ab](https://github.com/vig-os/devcontainer/commit/68bf2ab16949b84a151ca291e93097326865f735) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:50 PM
add docker-compose override file check, 1 file modified (tests/test_image.py)

### Commit 7: [1cb9b11](https://github.com/vig-os/devcontainer/commit/1cb9b113246fc5f8dd0adee7e3c4d0e631141da4) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:50 PM
add check for gitignored stuff, 13 files modified (tests/test_image.py)
