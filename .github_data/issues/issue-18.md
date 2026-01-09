---
type: issue
state: open
created: 2025-12-16T12:07:03Z
updated: 2025-12-18T09:22:57Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/18
comments: 0
labels: none
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-01-09T16:17:33.030Z
---

# [Issue 18]: [feat: Auto-cleanup test containers on failure with --keep-containers flag](https://github.com/vig-os/devcontainer/issues/18)

## Problem

Test containers are left behind when tests fail because fixture cleanup doesn't always run on hard failures or interrupts. This causes:
- Resource accumulation
- `make test` failures due to lingering container detection
- Manual cleanup required after debugging

## Proposed Solution

### 1. Add pytest option `--keep-containers`

```python
def pytest_addoption(parser):
    parser.addoption(
        "--keep-containers",
        action="store_true",
        default=False,
        help="Keep test containers after test completion (for debugging failed tests)",
    )
```

### 2. Use `request.addfinalizer()` for reliable cleanup

Replace `yield`-based cleanup with `addfinalizer()` which runs even on test failures:

```python
@pytest.fixture(scope="function")
def devcontainer_up(initialized_workspace, request):
    # ... setup code ...
    
    def cleanup():
        if request.config.getoption("--keep-containers"):
            print(f"\n⚠️  Keeping container for debugging: {container_name}")
            return
        # ... existing cleanup code (podman compose down, etc.) ...
    
    request.addfinalizer(cleanup)
    
    yield workspace_path
```

## Usage

```bash
# Normal run - auto-cleanup on success AND failure
make test-integration

# Debug mode - keep containers for investigation  
uv run pytest tests/test_integration.py --keep-containers -x

# Inspect the failed container
podman exec -it <container_name> bash

# Clean up manually when done
make clean-test-containers
```

## Benefits

- Containers cleaned up reliably even on failures
- `--keep-containers` flag for debugging
- Works with `-x` (stop on first failure) for debugging
- No more manual cleanup after failed test runs

## Affected Fixtures

- `devcontainer_up`
- `devcontainer_with_sidecar`
- `initialized_workspace`
- Any other fixtures that create containers
