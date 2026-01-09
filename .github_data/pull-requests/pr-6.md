---
type: pull_request
state: closed (merged)
branch: dev → main
created: 2025-11-26T18:28:22Z
updated: 2025-12-09T05:58:54Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/pull/6
comments: 9
labels: none
assignees: c-vigo
milestone: Initial release
projects: none
relationship: none
merged: 2025-12-09T05:58:54Z
synced: 2026-01-09T16:17:52.496Z
---

# [PR 6](https://github.com/vig-os/devcontainer/pull/6) Release Candidate 0.1 for the vigOS Development Environment

## Description

This PR introduces the **vigOS Development Environment** - a standardized, production-ready development container image designed for Python-based projects. This is the first official release (v0.1) of the devcontainer system, providing a complete, reproducible development environment with integrated tooling and automation.

The vigOS devcontainer provides:
- Standardized Python 3.12 development environment with minimal overhead (~450 MB)
- One-command project initialization using `init-workspace` script
- Automated Git configuration and commit signing setup
- Pre-configured development tools (pre-commit, ruff, uv)
- GitHub CLI integration for seamless workflow
- VS Code devcontainer template with Docker Compose orchestration
- Comprehensive three-tiered testing suite (image, integration, registry tests)

## Related Issue(s)

Closes #2
Closes #3

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Test updates

## Changes Made

### Core Infrastructure
- Containerfile with Python 3.12 base image (Debian Trixie)
- System tools installation (git, gh, curl, openssh-client, ca-certificates)
- Python environment with uv, pre-commit, and ruff
- init-workspace script for project initialization
- Multi-architecture support (AMD64, ARM64)

### Devcontainer Template
- VS Code devcontainer.json configuration
- Docker Compose orchestration (docker-compose.yml)
- Support for docker-compose.override.yml for custom mounts
- Post-attach automation scripts
- Automatic Git configuration synchronization from host
- Focused devcontainer README.md with version tracking and lifecycle documentation
- User-specific workspace.code-workspace.example for multi-root VS Code workspaces

### Git & GitHub Integration
- Automated git configuration copying from host
- SSH commit signing setup with signature verification
- Pre-commit hooks initialization
- GitHub issue templates (bug_report.yml, feature_request.yml, task.yml)
- Pull request template
- GitHub CLI integration

### Development Tools & Automation
- Makefile with build, test, push, pull, clean targets
- Setup script for development environment initialization
- Build script with multi-architecture support
- Push/pull scripts for registry operations
- Automatic README.md updates with version and image size during releases

### Testing Infrastructure
- Comprehensive test suite (conftest.py)
- Image tests (test_image.py) - 8 test classes verifying container image
- Integration tests (test_integration.py) - 13 test classes verifying devcontainer deployment
- Registry tests (test_registry.py) - validates push/pull/clean workflows and README updates
- Optimized registry tests using minimal Containerfile (10-20s builds vs 2min)

### Documentation
- README.md with usage and features
- CONTRIBUTE.md with development workflow
- TESTING.md with test strategy
- CHANGELOG.md with version history and GitHub release links
- `.devcontainer/README.md` - focused documentation for devcontainer lifecycle, mounts, and workspace configuration

## Testing

- [x] All tests pass locally (`make test` - runs image, integration, and registry tests)
- [ ] Image tests pass (`make test-image`)
- [ ] Integration tests pass (`make test-integration`)
- [ ] Registry tests pass (`make test-registry`)
- [ ] Manual testing performed (describe below)

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have updated the documentation accordingly (README.md, CONTRIBUTE.md, etc.)
- [x] I have updated the CHANGELOG.md in the `[Unreleased]` section
- [x] My changes generate no new warnings or errors
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] Any dependent changes have been merged and published

## Additional Notes

### Release Proposal: v0.1

This PR proposes the **first official release (0.1)** of the vigOS Development Environment.

**Release Artifacts**:
- Container Image: `ghcr.io/vig-os/devcontainer:0.1`
- Platforms: linux/amd64, linux/arm64
- Release Date: 2025-11-26

**Release Process** (after approval):
```bash
make push VERSION=0.1
```
This will create git tag, build multi-architecture images, push to GHCR, create GitHub release, and automatically update both main README.md and devcontainer README.md with version, release link, and date.

### Architecture Decisions

1. **Docker Compose over devcontainer.json volumes**: More flexibility for volume mounting
2. **Session-scoped test fixtures**: Reduces test execution time significantly
3. **Multi-stage authentication**: Supports multiple auth methods for flexibility
4. **Minimal base image**: Keeps size under 450 MB while providing full functionality
5. **Automatic README updates**: Push script updates version and image size automatically in both main README and devcontainer README
6. **Optimized registry tests**: Uses minimal Containerfile when TEST_REGISTRY is set, skips full test suite in registry test mode
7. **Build folder approach**: README updates happen in build/ folder during push, keeping source files clean
8. **User-specific workspace files**: workspace.code-workspace is gitignored, users copy from example


### Known Limitations

- Multi-architecture builds require QEMU on Linux
- Registry tests require Docker/Podman registry support
- SSH commit signing requires host-side key setup

### Review Focus Areas

Please pay special attention to:
1. **Testing Strategy**: Is the three-tiered approach comprehensive enough?
2. **Documentation**: Are setup instructions clear for new contributors?
3. **init-workspace Script**: Does the user experience feel smooth?
4. **Release Process**: Is v0.1 ready for public release?

### Quick Demo
```bash
# Build development image locally
make build

# One-command project initialization
podman run -it --rm -v "./:/workspace" ghcr.io/vig-os/devcontainer:dev /root/assets/init-workspace.sh

# Open in VS Code
code .

# Use Command Palette: "Dev Containers: Reopen in Container"
```



---
---

## Comments (9)

### [Comment #1](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3605990335) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 09:53 AM_

> ```
>    podman run -it --rm -v "PATH_TO_PROJECT:/workspace" \
>      ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh
> ```
> 
> is idle for some time, ~min might wanna do some 'progress' to show it is not stalled for UX

For me this takes less than 5 seconds running with "dev" tag, maybe it had to build the image first?

---

### [Comment #2](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606003142) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 09:56 AM_

> @docker-compose.yml does not replace IMAGE_TAG when after init. Wanted?

For me:

```bash
carlosvigo@vigolaptop:/tmp$ podman run -it --rm -v "/tmp/tmppp/:/workspace"      ghcr.io/vig-os/devcontainer:dev /root/assets/init-workspace.sh
carlosvigo@vigolaptop:/tmp$ cat /tmp/tmppp/.devcontainer/docker-compose.yml 
---
version: '3.8'

services:
  devcontainer:
    image: ghcr.io/vig-os/devcontainer:dev
    volumes:
      # Mount the project folder to a subdirectory of workspace
      - ..:/workspace/my_proj:cached
    environment:
      # Override default paths to match project subdirectory structure
      - PRE_COMMIT_HOME=/workspace/my_proj/.pre-commit-cache
    # Keep container running for VS Code to attach
    command: sleep infinity
    # Use root user (default from image)
    user: root
    # Keep stdin open and allocate a pseudo-TTY for interactive use
    stdin_open: true
    tty: true
 ```

---

### [Comment #3](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606043989) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 10:06 AM_

@gerchowl your last commit is unsigned, I have now added a rule to enforce this, but we cannot merge until the commit is signed. You will have to:
```bash
git commit --amend -S
git push --force-with-lease
```

---

### [Comment #4](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606082389) by [@gerchowl](https://github.com/gerchowl)

_Posted on December 3, 2025 at 10:15 AM_

> @gerchowl your last commit is unsigned, I have now added a rule to enforce this, but we cannot merge until the commit is signed. You will have to:
> 
> ```shell
> git commit --amend -S
> git push --force-with-lease
> ```

done but doesnt seem to have solved it

history looks correct though?!
```
git log --show-signature
commit 6f3a7e800fd7b08d741f99f5b565406281736762 (HEAD -> dev, origin/dev)
Good "git" signature with ED25519 key SHA256:iqMREhRavNggQFTHVe1E1vDSVjoiruT1snmdT/MsaEw
No principal matched.
Author: gerchowl <gerchowl@ethz.ch>
Date:   Tue Dec 2 18:15:23 2025 +0100

    Fix: Use 'uv run' for pytest commands in Makefile
    
    - Updated test-image, test-integration, and test-registry targets
    - Ensures pytest runs in the correct uv-managed virtual environment
    - Fixes 'pytest: command not found' error when running make test
```

---

### [Comment #5](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606101015) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 10:18 AM_

I still see it unsigned [here](https://github.com/vig-os/devcontainer/compare/main...dev)

<img width="1223" height="199" alt="image" src="https://github.com/user-attachments/assets/c4df0657-d5e0-48bb-8145-2f465505e0ee" />


---

### [Comment #6](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606106742) by [@gerchowl](https://github.com/gerchowl)

_Posted on December 3, 2025 at 10:20 AM_

> > @docker-compose.yml does not replace IMAGE_TAG when after init. Wanted?
> 
> For me:
> 
> ```shell
> carlosvigo@vigolaptop:/tmp$ podman run -it --rm -v "/tmp/tmppp/:/workspace"      ghcr.io/vig-os/devcontainer:dev /root/assets/init-workspace.sh
> carlosvigo@vigolaptop:/tmp$ cat /tmp/tmppp/.devcontainer/docker-compose.yml 
> ---
> version: '3.8'
> 
> services:
>   devcontainer:
>     image: ghcr.io/vig-os/devcontainer:dev
>     volumes:
>       # Mount the project folder to a subdirectory of workspace
>       - ..:/workspace/my_proj:cached
>     environment:
>       # Override default paths to match project subdirectory structure
>       - PRE_COMMIT_HOME=/workspace/my_proj/.pre-commit-cache
>     # Keep container running for VS Code to attach
>     command: sleep infinity
>     # Use root user (default from image)
>     user: root
>     # Keep stdin open and allocate a pseudo-TTY for interactive use
>     stdin_open: true
>     tty: true
> ```



```
larsgerchow@pharma-hci-dock-stat-402 test % time podman run -it --rm -v "./:/workspace" ghcr.io/vig-os/devcontainer:dev /root/assets/init-workspace.sh --force
Enter a short name for your project (letters/numbers only, e.g. my_proj): test
Project short name set to: test
Warning: --force flag detected. Existing files may be overwritten.
Continue? (y/N): y
Initializing workspace from template...
Copying files from /root/assets/workspace to /workspace...

Setting executable permissions on shell scripts and hooks...
Workspace initialized successfully!

You can now start developing in your workspace.
```
I checked folder while creation, files also created immediately. Script 'hangs' for some time between 'Copy ..' and 'Setting..'

```
larsgerchow@pharma-hci-dock-stat-402 test % cat .devcontainer/docker-compose.yml 
---
version: '3.8'

services:
  devcontainer:
    image: ghcr.io/vig-os/devcontainer:{{IMAGE_TAG}}
    volumes:
      # Mount the project folder to a subdirectory of workspace
      - ..:/workspace/test:cached
    environment:
      # Override default paths to match project subdirectory structure
      - PRE_COMMIT_HOME=/workspace/test/.pre-commit-cache
    # Keep container running for VS Code to attach
    command: sleep infinity
    # Use root user (default from image)
    user: root
    # Keep stdin open and allocate a pseudo-TTY for interactive use
    stdin_open: true
    tty: true
```



---

### [Comment #7](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606161603) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 10:32 AM_

## Build time
No clue, I tried with --force and it is still fast in my test. Maybe the problem is the "find" command in line 100 of init_workspace.sh?

## {{IMAGE_TAG}}
- did you use make build?
- do the tests pass? in particular, TestDevContainerPlaceholders in test_integration.py

---

### [Comment #8](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3606269248) by [@gerchowl](https://github.com/gerchowl)

_Posted on December 3, 2025 at 10:54 AM_

> ## Build time
> No clue, I tried with --force and it is still fast in my test. Maybe the problem is the "find" command in line 100 of init_workspace.sh?
> 
> ## {{IMAGE_TAG}}
> * did you use make build?
> * do the tests pass? in particular, TestDevContainerPlaceholders in test_integration.py

i had to, since its not pushed to ghcr.

```
devcontainer % make test
=============================================================================== test session starts ===============================================================================
platform darwin -- Python 3.12.10, pytest-9.0.1, pluggy-1.6.0 -- /Users/larsgerchow/Projects/eXoma/devcontainer/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/larsgerchow/Projects/eXoma/devcontainer
configfile: pyproject.toml
plugins: docker-3.2.5, testinfra-10.2.2
collected 19 items                                                                                                                                                                

tests/test_image.py::TestSystemTools::test_git_installed PASSED                                                                                                             [  5%]
tests/test_image.py::TestSystemTools::test_git_version PASSED                                                                                                               [ 10%]
tests/test_image.py::TestSystemTools::test_curl_installed PASSED                                                                                                            [ 15%]
tests/test_image.py::TestSystemTools::test_curl_version PASSED                                                                                                              [ 21%]
tests/test_image.py::TestSystemTools::test_openssh_client_installed PASSED                                                                                                  [ 26%]
tests/test_image.py::TestSystemTools::test_gh_installed PASSED                                                                                                              [ 31%]
tests/test_image.py::TestSystemTools::test_gh_version PASSED                                                                                                                [ 36%]
tests/test_image.py::TestPythonEnvironment::test_python3_installed PASSED                                                                                                   [ 42%]
tests/test_image.py::TestPythonEnvironment::test_uv_installed FAILED                                                                                                        [ 47%]
tests/test_image.py::TestDevelopmentTools::test_pre_commit_installed PASSED                                                                                                 [ 52%]
tests/test_image.py::TestDevelopmentTools::test_ruff_installed FAILED                                                                                                       [ 57%]
tests/test_image.py::TestEnvironmentVariables::test_pythonunbuffered_set PASSED                                                                                             [ 63%]
tests/test_image.py::TestEnvironmentVariables::test_in_container_set PASSED                                                                                                 [ 68%]
tests/test_image.py::TestEnvironmentVariables::test_locale_set PASSED                                                                                                       [ 73%]
tests/test_image.py::TestFileStructure::test_workspace_directory_exists PASSED                                                                                              [ 78%]
tests/test_image.py::TestFileStructure::test_precommit_alias_in_bashrc PASSED                                                                                               [ 84%]
tests/test_image.py::TestFileStructure::test_assets_directory_exists PASSED                                                                                                 [ 89%]
tests/test_image.py::TestFileStructure::test_assets_workspace_structure PASSED                                                                                              [ 94%]
tests/test_image.py::TestFileStructure::test_workspace_template_pre_commit_hooks_initialized PASSED                                                                         [100%]

==================================================================================== FAILURES =====================================================================================
_____________________________________________________________________ TestPythonEnvironment.test_uv_installed _____________________________________________________________________
tests/test_image.py:97: in test_uv_installed
    assert expected in result.stdout, (
E   AssertionError: Expected uv 0.9.13, got: uv 0.9.14
E     
E   assert '0.9.13' in 'uv 0.9.14\n'
E    +  where 'uv 0.9.14\n' = CommandResult(backend=<testinfra.backend.podman.PodmanBackend object at 0x1016402c0>, exit_status=0, command=b'uv --version', _stdout=b'uv 0.9.14\n', _stderr=b'').stdout
____________________________________________________________________ TestDevelopmentTools.test_ruff_installed _____________________________________________________________________
tests/test_image.py:121: in test_ruff_installed
    assert expected in result.stdout, (
E   AssertionError: Expected ruff 0.14.6, got: ruff 0.14.7
E     
E   assert '0.14.6' in 'ruff 0.14.7\n'
E    +  where 'ruff 0.14.7\n' = CommandResult(backend=<testinfra.backend.podman.PodmanBackend object at 0x1016402c0>, exit_status=0, command=b'ruff --version', _stdout=b'ruff 0.14.7\n', _stderr=b'').stdout
============================================================================= short test summary info =============================================================================
FAILED tests/test_image.py::TestPythonEnvironment::test_uv_installed - AssertionError: Expected uv 0.9.13, got: uv 0.9.14
FAILED tests/test_image.py::TestDevelopmentTools::test_ruff_installed - AssertionError: Expected ruff 0.14.6, got: ruff 0.14.7
========================================================================== 2 failed, 17 passed in 20.11s ==========================================================================
make: *** [test-image] Error 1
```
`make test` doesnt run the integrations. maybe because already of the version mismatch?

make test-integrations fails hard.
```
============================================================================= short test summary info =============================================================================
FAILED tests/test_integration.py::TestDevContainerDockerCompose::test_docker_compose_yml_image - AssertionError: Expected image to be ghcr.io/vig-os/devcontainer:dev, got: ghcr.io/vig-os/devcontainer:{{IMAGE_TAG}}
FAILED tests/test_integration.py::TestDevContainerDockerCompose::test_docker_compose_yml_placeholders_replaced - AssertionError: {{IMAGE_TAG}} placeholder not replaced in docker-compose.yml
FAILED tests/test_integration.py::TestDevContainerPlaceholders::test_image_tag_replaced - AssertionError: {{IMAGE_TAG}} placeholder not replaced in docker-compose.yml
ERROR tests/test_integration.py::TestDevContainerUserConf::test_conf_directory_files - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDevContainerUserConf::test_files_copied_to_home - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDevContainerCLI::test_ssh_github_authentication - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDevContainerCLI::test_pre_commit_hook - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDevContainerCLI::test_git_commit_ssh_signature - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDevContainerCLI::test_github_cli_authentication - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDockerComposeOverride::test_override_mount_directory_exists - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDockerComposeOverride::test_override_mount_file_accessible - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDockerComposeOverride::test_override_mount_file_readable - Failed: devcontainer up failed
ERROR tests/test_integration.py::TestDockerComposeOverride::test_override_mount_list_directory - Failed: devcontainer up failed
==================================================================== 3 failed, 33 passed, 10 errors in 48.55s =====================================================================
make: *** [test-integration] Error 1
```

---

### [Comment #9](https://github.com/vig-os/devcontainer/pull/6#issuecomment-3607479024) by [@c-vigo](https://github.com/c-vigo)

_Posted on December 3, 2025 at 03:42 PM_

@gerchowl may I ask for one final run of `make clean && make test`

---
---

## Commits

### Commit 1: [071e738](https://github.com/vig-os/devcontainer/commit/071e738c94c7fb895569e0dbd44c53f944faae25) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 02:18 PM
project setup with development tools to build the image, 872 files modified (.githooks/pre-commit, .github/scripts/sync-prs-issues.sh, .gitignore, .hadolint.yaml, .pre-commit-config.yaml, .pymarkdown, .pymarkdown.config.md, pyproject.toml, uv.lock)

### Commit 2: [13e9664](https://github.com/vig-os/devcontainer/commit/13e9664e8e87e63351dc0a9f550824f68bb707c8) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 02:24 PM
add utility scripts, 873 files modified (Makefile, scripts/backup_template.sh, scripts/build.sh, scripts/clean.sh, scripts/push.sh, scripts/restore_template.sh, scripts/run_tests.sh, scripts/setup.sh)

### Commit 3: [f86234b](https://github.com/vig-os/devcontainer/commit/f86234b1ac1973c61cf33e007c0a99022a0979d4) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 02:57 PM
refurbish toolchain to use temporary build folder, 194 files modified (.gitignore, Makefile, scripts/backup_template.sh, scripts/build.sh, scripts/push.sh, scripts/restore_template.sh, scripts/run_tests.sh)

### Commit 4: [4bb05b5](https://github.com/vig-os/devcontainer/commit/4bb05b5b457a776c388cca23e5fc3e365ab39a61) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 03:02 PM
add initial version of the image, 3312 files modified

### Commit 5: [763808a](https://github.com/vig-os/devcontainer/commit/763808a2019648b4106186008fdf7598c183eebb) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 03:17 PM
pre-initialize pre-commit hooks, 30 files modified (Containerfile, tests/test_image.py)

### Commit 6: [49da00b](https://github.com/vig-os/devcontainer/commit/49da00bf10cec08d15a809be09a023ef641d464c) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 04:26 PM
add README for tests, 90 files modified (tests/README.md)

### Commit 7: [5013d07](https://github.com/vig-os/devcontainer/commit/5013d07f58383119df9af2eff12a9d14eeccb510) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 04:57 PM
fix registry mechanisms and testing, 180 files modified (Makefile, scripts/push.sh, tests/test_registry.py)

### Commit 8: [9ef0ffa](https://github.com/vig-os/devcontainer/commit/9ef0ffa73af092ad9889eda45edb90e0cd166fe0) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 06:12 PM
switch vig-OS to vigOS, fix URLs, 14 files modified (Containerfile, LICENSE)

### Commit 9: [f2a5dca](https://github.com/vig-os/devcontainer/commit/f2a5dca7f8a0f95cbdc414b5149b2501353ae6fa) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 06:23 PM
implement modular testing, 84 files modified (Makefile, scripts/push.sh, tests/README.md)

### Commit 10: [3f14dd5](https://github.com/vig-os/devcontainer/commit/3f14dd5c079a5fa3761a571b7ffbf1cf5530d8d7) by [c-vigo](https://github.com/c-vigo) on November 24, 2025 at 06:24 PM
update GH issues, 33 files modified (.github_data/issues/1.md, .github_data/issues/2.md)

### Commit 11: [3a01710](https://github.com/vig-os/devcontainer/commit/3a0171009aae638c64b8b16e658bfe9edf053298) by [c-vigo](https://github.com/c-vigo) on November 25, 2025 at 09:23 AM
immprove documentation, 391 files modified (CHANGELOG.md, CONTRIBUTE.md, Makefile, README.md, TESTING.md)

### Commit 12: [f8c4522](https://github.com/vig-os/devcontainer/commit/f8c45227866e42b7f55c3e3a68594c023c5144b3) by [c-vigo](https://github.com/c-vigo) on November 25, 2025 at 09:44 AM
Add GitHub issue and PR templates for this project, 258 files modified (.github/ISSUE_TEMPLATE/bug_report.yml, .github/ISSUE_TEMPLATE/feature_request.yml, .github/ISSUE_TEMPLATE/task.yml, .github/pull_request_template.md)

### Commit 13: [682e548](https://github.com/vig-os/devcontainer/commit/682e5486832697b94a6cb489ff151b65f18bbba5) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 02:10 PM
switch to docker-compose for devcontainer orchestration, 248 files modified (assets/workspace/.devcontainer/devcontainer.json, assets/workspace/.devcontainer/docker-compose.yml, tests/test_integration.py)

### Commit 14: [05892d7](https://github.com/vig-os/devcontainer/commit/05892d79dd98c3bf0a98ee437c35fd23b4f24b8a) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 02:14 PM
update uv version to 0.9.12, 4 files modified (scripts/setup.sh, tests/test_image.py)

### Commit 15: [fe798c4](https://github.com/vig-os/devcontainer/commit/fe798c4e1d08bec0880c04f1b760fe20b91d7659) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 03:40 PM
Mount project to /workspace subdirectory instead of root, 158 files modified

### Commit 16: [5a11186](https://github.com/vig-os/devcontainer/commit/5a111866eaddfc52ae67dd056f2e51a14c4167d0) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:06 PM
Add docker-compose override support for mounting additional folders, 440 files modified

### Commit 17: [e762793](https://github.com/vig-os/devcontainer/commit/e76279358ad629657eaa2f6a1c869a128b3d1567) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:15 PM
Merge pull request #4 from vig-os/c-vigo/issue3, 814 files modified

### Commit 18: [d1fd154](https://github.com/vig-os/devcontainer/commit/d1fd15444316710a902428a5b4e9586056ad92ea) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:16 PM
install development dependencies when running "make setup", 4 files modified (scripts/setup.sh)

### Commit 19: [ef2d3ea](https://github.com/vig-os/devcontainer/commit/ef2d3ea39d0cb1630486341594b1c3b0d1d684e2) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:34 PM
add issue and PR templates to assets, 258 files modified

### Commit 20: [7b1b183](https://github.com/vig-os/devcontainer/commit/7b1b183f9ceb0e593b077f0c7bff669bf8285877) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:39 PM
add tests to verify all files inside assets, 65 files modified (tests/test_image.py)

### Commit 21: [118060c](https://github.com/vig-os/devcontainer/commit/118060c5e70c7cafb963da1a0d076d6a9f178cd2) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:45 PM
Merge branch 'dev' into c-vigo/issue2, 818 files modified

### Commit 22: [0615c81](https://github.com/vig-os/devcontainer/commit/0615c81905758757352c6dc6bdf07db6767b2a6f) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:49 PM
fix error message for uv version, 2 files modified (tests/test_image.py)

### Commit 23: [68bf2ab](https://github.com/vig-os/devcontainer/commit/68bf2ab16949b84a151ca291e93097326865f735) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:50 PM
add docker-compose override file check, 1 file modified (tests/test_image.py)

### Commit 24: [1cb9b11](https://github.com/vig-os/devcontainer/commit/1cb9b113246fc5f8dd0adee7e3c4d0e631141da4) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:50 PM
add check for gitignored stuff, 13 files modified (tests/test_image.py)

### Commit 25: [dd82f7e](https://github.com/vig-os/devcontainer/commit/dd82f7e3838ce17573142b9b0033d9eb1ee3eb7e) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 04:59 PM
Merge pull request #5 from vig-os/c-vigo/issue2, 597 files modified

### Commit 26: [b0b941d](https://github.com/vig-os/devcontainer/commit/b0b941d4a5e8b779b5ad180be5590ca533d7e8a8) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 05:09 PM
remove size placeholder from README, 2 files modified (README.md)

### Commit 27: [4bbb095](https://github.com/vig-os/devcontainer/commit/4bbb095cbe9e52ffc392f4f449ea46439853c498) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 05:29 PM
fix bug with version bumping in push workflow, 82 files modified (scripts/push.sh, tests/test_registry.py)

### Commit 28: [16bdcae](https://github.com/vig-os/devcontainer/commit/16bdcae2a5ceb5a03fcde494fb7da26854ca476f) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:01 PM
use minimal Containerfile for registry tests to speed up tests, 40 files modified (scripts/push.sh, tests/test_registry.py)

### Commit 29: [7c294ef](https://github.com/vig-os/devcontainer/commit/7c294ef1a923902fcd029dc7d5b5222c3df46b62) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:04 PM
switch "make test" target to run all test suites, 32 files modified (.github/pull_request_template.md, CONTRIBUTE.md, Makefile, TESTING.md)

### Commit 30: [aaaef69](https://github.com/vig-os/devcontainer/commit/aaaef69e813d4995db3580f8c236618c0fa2f23b) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:07 PM
update issues and PRs, 278 files modified (.github_data/issues/3.md, .github_data/prs/4.md, .github_data/prs/5.md)

### Commit 31: [7bd9dcb](https://github.com/vig-os/devcontainer/commit/7bd9dcbb0789d77572101be557582824343f027b) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:08 PM
candidate version 0.1, 48 files modified (CHANGELOG.md)

### Commit 32: [7f632ab](https://github.com/vig-os/devcontainer/commit/7f632ab3d3162bd2ca7ea59bfd521ae4123873ed) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:21 PM
update docs for init_workspace location, 8 files modified (README.md, assets/init-workspace.sh)

### Commit 33: [755ed3c](https://github.com/vig-os/devcontainer/commit/755ed3cf1476873bc529a391b2a86b1d869d88a7) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:22 PM
update uv to 0.9.13, 4 files modified (scripts/setup.sh, tests/test_image.py)

### Commit 34: [ec8d7af](https://github.com/vig-os/devcontainer/commit/ec8d7af658dff71225230e8bf1748788e2815134) by [c-vigo](https://github.com/c-vigo) on November 26, 2025 at 06:26 PM
reduce verbosity of registry tests, 21 files modified (tests/test_registry.py)

### Commit 35: [d3326ea](https://github.com/vig-os/devcontainer/commit/d3326ea5b5a5419d6a028910990a4c193f266f30) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 08:15 AM
add workspace configuration to allow browsing and editing sibling projects within VS Code, 38 files modified (assets/workspace/.devcontainer/.gitignore, assets/workspace/.devcontainer/workspace.code-workspace.example, tests/test_image.py)

### Commit 36: [89e61f6](https://github.com/vig-os/devcontainer/commit/89e61f6ac9a9b1f051d952fe5f05f58fd5c38dbd) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 08:30 AM
update README, 67 files modified (README.md)

### Commit 37: [aec05be](https://github.com/vig-os/devcontainer/commit/aec05bebcc0bc45434eb8195750ff0f406b8eead) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 10:15 AM
move post-attach and initialize scripts to scripts folder, 133 files modified

### Commit 38: [33858bb](https://github.com/vig-os/devcontainer/commit/33858bb24af27dcfcef59169535d502a62fb5bac) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 10:39 AM
Add helper to patch README metadata plus coverage in tests., 142 files modified (README.md, scripts/__init__.py, scripts/push.sh, scripts/update_readme.py, tests/test_registry.py)

### Commit 39: [f2ae69c](https://github.com/vig-os/devcontainer/commit/f2ae69cdf853e03cb7a34a1952d46cd998862956) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 11:41 AM
include a focused README in the devcontainer assets, 389 files modified (assets/workspace/.devcontainer/README.md, scripts/push.sh, scripts/update_readme.py, tests/test_image.py, tests/test_registry.py)

### Commit 40: [2d2a4da](https://github.com/vig-os/devcontainer/commit/2d2a4da688592fcb6464f664af85bc6f1e5b09c4) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 01:36 PM
simplify make push arguments for registry testing, 124 files modified (Makefile, scripts/push.sh, scripts/update_readme.py, tests/test_registry.py)

### Commit 41: [c9f7e89](https://github.com/vig-os/devcontainer/commit/c9f7e89a6e12bbb4f2a35ab9c18857577391513d) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 02:28 PM
remove legacy MOUNTS.md documentation, 169 files modified (assets/workspace/.devcontainer/MOUNTS.md)

### Commit 42: [40f1f76](https://github.com/vig-os/devcontainer/commit/40f1f764640c1088db848675c6d1a755976ea8a3) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 02:29 PM
update github data, 164 files modified (.github_data/prs/6.md)

### Commit 43: [06fab1c](https://github.com/vig-os/devcontainer/commit/06fab1cc8c5d928bd289858d1fa8c8b5054e6655) by [c-vigo](https://github.com/c-vigo) on November 27, 2025 at 02:30 PM
update CHANGELOG, release candidate 0.1, 38 files modified (CHANGELOG.md)

### Commit 44: [3576a92](https://github.com/vig-os/devcontainer/commit/3576a9237887458f13f5081fd0b1f2e7a0a8f43e) by [gerchowl](https://github.com/gerchowl) on December 2, 2025 at 05:15 PM
Fix: Use 'uv run' for pytest commands in Makefile, 6 files modified (Makefile)

### Commit 45: [a4cf193](https://github.com/vig-os/devcontainer/commit/a4cf1937497e1f5c7ff2faa9b75e0522a4a54999) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:27 AM
pr gh updates, 4 files modified (.github_data/prs/6.md)

### Commit 46: [3ffa4aa](https://github.com/vig-os/devcontainer/commit/3ffa4aaf61f9aed6386ebe11cd2b302e818b483d) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:39 AM
fix: use -d instead of -f to check for .pre-commit-cache directory, 2 files modified (assets/workspace/.devcontainer/scripts/init-precommit.sh)

### Commit 47: [cb5bffd](https://github.com/vig-os/devcontainer/commit/cb5bffda53abe13421187f462da8e2b78d78c546) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:39 AM
fix: use exit instead of return in init-precommit.sh, 2 files modified (assets/workspace/.devcontainer/scripts/init-precommit.sh)

### Commit 48: [2dde06d](https://github.com/vig-os/devcontainer/commit/2dde06d4acf1620d8e11987eecc692ffbea146a5) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:42 AM
refactor: centralize version expectations in test_image.py, 53 files modified (tests/test_image.py)

### Commit 49: [f096bf5](https://github.com/vig-os/devcontainer/commit/f096bf586e6165b8ba018db63155075f0ad4634d) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:44 AM
fix: correct service name in workspace pre-commit hook, 2 files modified (assets/workspace/.githooks/pre-commit)

### Commit 50: [cdcdf73](https://github.com/vig-os/devcontainer/commit/cdcdf73a1d4f9959049460e3183d1254be7d3384) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:45 AM
fix: initialize ssh_agent_added variable before conditionals, 3 files modified (tests/conftest.py)

### Commit 51: [a5a36b5](https://github.com/vig-os/devcontainer/commit/a5a36b5468dbf2ed4fb8366f54a0eff1729ea58b) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 10:53 AM
Release 99.9204, 4 files modified (README.md)

### Commit 52: [78ff3b3](https://github.com/vig-os/devcontainer/commit/78ff3b32895b07870b306c2e3d63a32a2cf1f358) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 11:13 AM
fix: update versions in test to match latest releases, 4 files modified (tests/test_image.py)

### Commit 53: [fad8dbd](https://github.com/vig-os/devcontainer/commit/fad8dbd9cabfb19aeb560f8a7e263b3203f158e6) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 11:16 AM
Add cross-platform compatibility for build scripts, 154 files modified (scripts/build.sh, scripts/push.sh, scripts/setup.sh, scripts/utils.sh)

### Commit 54: [c851c74](https://github.com/vig-os/devcontainer/commit/c851c74142b013355685aa1185c46f0bbf36d834) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 11:16 AM
Merge branch 'dev' of github.com:vig-os/devcontainer into dev, 4 files modified (tests/test_image.py)

### Commit 55: [ef9478b](https://github.com/vig-os/devcontainer/commit/ef9478b297e6ebf0a64842dce685f045c8496273) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 12:17 PM
Release 99.4250, 2 files modified (README.md)

### Commit 56: [6e272ee](https://github.com/vig-os/devcontainer/commit/6e272ee970fb77b8ba042a4e3b314fd70771cc1d) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 12:19 PM
Fix git tag creation in automated environments by disabling GPG signing, 3 files modified (scripts/push.sh)

### Commit 57: [4fccfcf](https://github.com/vig-os/devcontainer/commit/4fccfcf51b214dea79db79506c2fe387f23c5e0d) by [gerchowl](https://github.com/gerchowl) on December 3, 2025 at 01:29 PM
Fix registry tests: add TLS verification support for pull, 37 files modified (Makefile, tests/test_registry.py)

### Commit 58: [e9ce595](https://github.com/vig-os/devcontainer/commit/e9ce59587c30c3cbea5698b127034ed6f8e3a837) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:20 PM
add LICENSE to assets, 201 files modified (assets/workspace/LICENSE)

### Commit 59: [5d76204](https://github.com/vig-os/devcontainer/commit/5d76204b9995c00594ce54d45d84db10bb4af28f) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:25 PM
add org input to init-workspace script, 159 files modified (assets/init-workspace.sh, tests/conftest.py, tests/test_image.py, tests/test_integration.py)

### Commit 60: [43c25ce](https://github.com/vig-os/devcontainer/commit/43c25ce7dd9c36d581dfcd87db98223400393109) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:25 PM
fix git hook directory, 6 files modified (assets/workspace/.devcontainer/scripts/setup-git-conf.sh)

### Commit 61: [3a809c9](https://github.com/vig-os/devcontainer/commit/3a809c91abfcd0cc2460427419b4ecbc1bc729b2) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:26 PM
fix SSH env check, 2 files modified (tests/conftest.py)

### Commit 62: [2ebfa10](https://github.com/vig-os/devcontainer/commit/2ebfa1050c0d588f9088ba91d66638d40d4fb310) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:32 PM
fix project README updated by mistake during some test, 6 files modified (README.md)

### Commit 63: [d510745](https://github.com/vig-os/devcontainer/commit/d51074572a96bb6c62a89fd0ebac0e766016782b) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:33 PM
fix inconsistency in asset pre-commit hook, 15 files modified (assets/workspace/.githooks/pre-commit)

### Commit 64: [ff9847a](https://github.com/vig-os/devcontainer/commit/ff9847a28473bb6079fbcf7b7955ccbf97ceb558) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:55 PM
add "-x" flag to shellcheck to follow sourced files, 1 file modified (.pre-commit-config.yaml)

### Commit 65: [a1f964e](https://github.com/vig-os/devcontainer/commit/a1f964ed26e5afe8c02164ebafac1ffa112642b8) by [c-vigo](https://github.com/c-vigo) on December 3, 2025 at 03:55 PM
Fix leading space in BUILT_PLATFORMS causing empty string iteration, 6 files modified (scripts/push.sh)

### Commit 66: [7104d59](https://github.com/vig-os/devcontainer/commit/7104d590dd093943db6aa4d3871623e15683fbda) by [c-vigo](https://github.com/c-vigo) on December 5, 2025 at 01:17 PM
fix typos in asset CHANGELOG, 9 files modified (assets/workspace/CHANGELOG.md)

### Commit 67: [8429ac1](https://github.com/vig-os/devcontainer/commit/8429ac1c2f2d3c8a1e9fa5cfb224d61cbb1ca3ca) by [c-vigo](https://github.com/c-vigo) on December 5, 2025 at 02:16 PM
feat: add post-create script for devcontainer lifecycle, 63 files modified

### Commit 68: [7055c2d](https://github.com/vig-os/devcontainer/commit/7055c2d4f424c5336c3619fa9d709579bcdb28f3) by [c-vigo](https://github.com/c-vigo) on December 8, 2025 at 08:49 AM
bump versions in tests, 4 files modified (tests/test_image.py)

### Commit 69: [ad9e854](https://github.com/vig-os/devcontainer/commit/ad9e854a14cb54d5939414a7c05280bc63e3a3b4) by [gerchowl](https://github.com/gerchowl) on December 8, 2025 at 03:11 PM
fixes for sed -i mac compatibility, 12 files modified (.github_data/prs/6.md, assets/init-workspace.sh)

### Commit 70: [470a8fa](https://github.com/vig-os/devcontainer/commit/470a8fa62aa60fe4bfdb784ea3627156a7b30364) by [c-vigo](https://github.com/c-vigo) on December 9, 2025 at 05:52 AM
update CHANGELOG for release 0.1, 36 files modified (CHANGELOG.md)

### Commit 71: [611e0c3](https://github.com/vig-os/devcontainer/commit/611e0c367f5d440fb943dfe155c5864c729d4c67) by [c-vigo](https://github.com/c-vigo) on December 9, 2025 at 05:57 AM
Release 0.1, 4 files modified (README.md)
