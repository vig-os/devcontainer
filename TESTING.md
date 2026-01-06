<!-- Auto-generated from docs/templates/TESTING.md.j2 - DO NOT EDIT DIRECTLY -->
<!-- Run 'just docs' to regenerate -->

# Testing

This document describes the testing strategy and structure for this project.

## Test Strategy

We use a three-tiered testing approach:

1. **Image Tests**: Verify the container image itself (installed tools, versions, environment variables, file structure)
2. **Integration Tests**: Verify that the container works correctly as a devcontainer (template initialization, configuration files, scripts, VS Code integration)
3. **Registry Tests**: Verify that the justfile's push, pull, and clean workflows work correctly without leaving artifacts

The tests are organized into three main files:

```text
tests/
├── conftest.py                              # Shared fixtures for all tests
├── test_image.py                            # Container image verification tests
├── test_integration.py                      # DevContainer integration tests
└── test_registry.py                         # Registry mechanism tests (push/pull/clean)
```

### Image Tests

These tests run against a running container instance to verify the image itself
(installed tools, versions, environment variables, file structure).

- `TestSystemTools` - git, curl, openssh-client, gh, just
- `TestPythonEnvironment` - Python 3.12, uv
- `TestDevelopmentTools` - pre-commit, ruff, just
- `TestEnvironmentVariables` - environment variables
- `TestFileStructure` - file structure

### Integration Tests

These tests run against an initialized workspace to verify that the container works correctly as a devcontainer
(template initialization, configuration files, scripts, VS Code integration, devcontainer deployment)

- `TestHostGitSignatureSetup` - git commit signing prerequisites on host
- `TestDevContainerStructure` - directory structure
- `TestDevContainerJson` - devcontainer.json validation
- `TestDevContainerScripts` - script existence/executability
- `TestDevContainerPlaceholders` - placeholder replacement
- `TestDevContainerGit` - git hooks/config
- `TestDevContainerUserConf` - user configuration files
- `TestDevContainerCLI` - devcontainer deployment and functionality
- `TestSidecarConnectivity` - sidecar container integration with just

### Registry Tests

These tests check that the justfile's push, pull, and clean workflows work correctly without leaving artifacts,
using a local temporary Docker registry.

- `test_just_push_mechanism` - verifies push workflow
- `test_just_pull_mechanism` - verifies pull workflow
- `test_just_clean_mechanism` - verifies clean workflow

### Test fixtures

Image and integration fixtures:

- `container_tag`: Container tag from `TEST_CONTAINER_TAG` environment variable (defaults to "dev")
- `container_image`: Full image name (e.g. `ghcr.io/vig-os/devcontainer:dev`)
- `test_container`: Running container instance for testing (session-scoped)
- `host`: Testinfra host connection to the container (session-scoped)
- `initialized_workspace`: Temporary workspace initialized with `init-workspace` script (session-scoped)
- `devcontainer_up`: DevContainer set up using devcontainer CLI, ready for testing (session-scoped)

Registry fixtures:

- `local_registry`: Local Docker registry for testing (session-scoped)
- `test_version`: Unique test version for registry tests (session-scoped)
- `git_clean_state`: Ensures git repository is clean before/after tests (session-scoped)
- `pushed_image`: Performs `just push` and verifies git tag creation and image existence (session-scoped)
- `pulled_image`: Depends on `pushed_image`, performs `just pull` and verifies the image was pulled (session-scoped)

**Note**: Session-scoped fixtures (like `devcontainer_up`) are set up once per test session and reused by all tests.
This is important for fixtures that take time to set up (e.g., `devcontainer_up` takes about a minute).
The fixtures automatically cleans up after all tests complete.

## Running Tests

Tests are run using just recipes. The `test` recipe runs all three test suites (image, integration, and registry):

```bash
# Run all test suites (image, integration, registry)
just test

# Run tests for a specific image version (must be locally available)
# Note: test-registry always uses a temporary local registry
just test version=1.0.0
```

### Individual Test Suites

You can also run individual test suites:

```bash
# Run only image tests (builds dev image if needed)
just test-image

# Run only integration tests (builds dev image if needed)
just test-integration

# Run only registry tests (doesn't require pre-built image)
just test-registry

# Run specific test suite for a locally available version
just test-image version=1.0.0
just test-integration version=1.0.0
```

### Notes

- `test-image` and `test-integration` automatically build the dev image if it doesn't exist (when `version=dev` or none),
  but they don't automatically update it
- `test-registry` uses its own local registry and doesn't require a pre-built image
- The `TEST_CONTAINER_TAG` environment variable is automatically set based on the `version` parameter (defaults to "dev")
- All tests use pytest with verbose output (`-v`) and short traceback format (`--tb=short`)
