---
type: issue
state: open
created: 2026-06-24T14:37:01Z
updated: 2026-06-24T15:20:53Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/691
comments: 0
labels: bug, priority:low, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:56.202Z
---

# [Issue 691]: [[BUG] pytest 10 will break install-script tests: class-scoped fixture defined as instance method](https://github.com/vig-os/devcontainer/issues/691)

## Description

The test suite emits a `PytestRemovedIn10Warning` from the class-scoped `install_workspace` fixture in `tests/test_install_script.py`:

```
PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
Instance attributes set in this fixture will NOT be visible to test methods,
as each test gets a new instance while the fixture runs only once per class.
Use @classmethod decorator and set attributes on cls instead.
```

Today this is **cosmetic** — the fixture only `yield`s a value that the 17 tests consume via the fixture parameter; it never sets `self.` attributes that tests read, and warnings are not escalated to errors. But it is **latent forward-breakage**: the project pins `pytest==9.1.1`, and pytest **10 removes** this pattern. When Renovate/Dependabot bumps pytest to 10, the fixture will error at collection and take out the entire `TestInstallScriptIntegration` suite.

Filing as low-priority to fix proactively before the pytest 10 bump lands.

## Steps to Reproduce

1. Run any test that touches `TestInstallScriptIntegration`, e.g.:
   ```bash
   TEST_CONTAINER_TAG=dev uv run pytest tests/test_install_script.py -v
   ```
2. Observe the `PytestRemovedIn10Warning` in the warnings summary.
3. To confirm it will break under pytest 10, escalate it to an error:
   ```bash
   TEST_CONTAINER_TAG=dev uv run pytest tests/test_install_script.py -W error::pytest.PytestRemovedIn10Warning
   ```

## Expected Behavior

No deprecation warning; the install-script integration tests remain collectable and green under pytest 9 and 10.

## Actual Behavior

`PytestRemovedIn10Warning` is emitted. Under a future pytest 10, the deprecated pattern is removed and collection of `TestInstallScriptIntegration` fails.

## Environment

- **OS**: NixOS 26.05 (Yarara)
- **pytest**: 9.1.1 (pinned in `pyproject.toml`)
- **Architecture**: x86_64

## Root cause

`tests/test_install_script.py:32` defines a class-scoped fixture as an instance method:

```python
class TestInstallScriptIntegration:
    @pytest.fixture(scope="class")
    def install_workspace(self, container_image):
        ...
        yield workspace_path
```

pytest deprecated (and will remove in v10) class-scoped fixtures defined as instance methods, because each test gets a fresh instance while the fixture runs once per class — making `self`-based state unreliable. This is the **only** fixture in `tests/` matching the pattern (conftest, test_integration, test_utils, test_image, test_flake_devshell are all clear).

## Suggested fix

Convert `install_workspace` so it no longer relies on the deprecated instance-method form, while preserving the "run `install.sh` once per class" intent. Either:

1. Make it a `@classmethod` (or `@staticmethod`) keeping `scope="class"`, taking `container_image` as a fixture arg and `yield`-ing as today (no `self`); or
2. Lift it to a module-level fixture (`scope="module"` ≈ class scope here, since only one class uses it).

Tests already consume it via the fixture parameter, so no test-method changes are needed.

Verify the fix with the warning escalated to an error:

```bash
TEST_CONTAINER_TAG=dev uv run pytest tests/test_install_script.py \
  -W error::pytest.PytestRemovedIn10Warning -v --tb=short
```

## Changelog Category

Fixed

