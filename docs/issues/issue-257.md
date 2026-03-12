---
type: issue
state: closed
created: 2026-03-11T09:01:57Z
updated: 2026-03-11T12:18:04Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/257
comments: 1
labels: feature, area:workspace, effort:medium, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-12T07:59:30.003Z
---

# [Issue 257]: [[FEATURE] Root .vig-os config file as SSoT for devcontainer version](https://github.com/vig-os/devcontainer/issues/257)

### Description

Introduce a committed key=value config file (`.vig-os`) at the project root that becomes the single source of truth for the devcontainer image version. Today, the version is baked into `docker-compose.yml` at build time via the `{{IMAGE_TAG}}` placeholder; downstream consumers (version-check, CI, smoke tests) must grep-parse `docker-compose.yml` to discover it.

### Problem Statement

1. **Fragile version detection** -- `version-check.sh` extracts the version by grep-parsing the `image:` line in `docker-compose.yml`. Any format change breaks it.
2. **No single source of truth** -- the version lives inside a generated line of `docker-compose.yml`. Nothing else can reference it without parsing that file.
3. **Smoke-test CI can't discover the RC tag** -- `ci-container.yml` defaults to `latest` on PR triggers because there is no input. A config file would let CI read the intended tag.
4. **`initialize.sh` already writes `.devcontainer/.env`** for docker-compose interpolation (`CONTAINER_SOCKET_PATH`), so the infrastructure for env-var-based image tags already exists.

### Proposed Solution

Add `.vig-os` (key=value format) to `assets/workspace/` as a template file:

```
# vig-os devcontainer configuration
DEVCONTAINER_VERSION={{IMAGE_TAG}}
```

**Data flow:**

```
.vig-os (committed, project root)
    │
    ├── initialize.sh sources it on host
    │       └── writes DEVCONTAINER_VERSION to .devcontainer/.env
    │               └── docker-compose.yml: image: ...${DEVCONTAINER_VERSION:-latest}
    │
    ├── version-check.sh reads it directly (replaces grep-parsing)
    │
    └── CI / smoke-test reads it directly
```

**Key design choice: key=value format** -- `initialize.sh` runs on the **host** before the container starts. The host may not have Python, ruling out TOML. Key=value is shell-sourceable, docker-compose-friendly, and trivially readable by CI.

**Files to change:**

- **New**: `assets/workspace/.vig-os` -- template with `DEVCONTAINER_VERSION={{IMAGE_TAG}}`
- **Modify**: `assets/workspace/.devcontainer/docker-compose.yml` -- `{{IMAGE_TAG}}` → `${DEVCONTAINER_VERSION:-latest}`
- **Modify**: `assets/workspace/.devcontainer/scripts/initialize.sh` -- source `.vig-os`, write to `.env`
- **Modify**: `assets/workspace/.devcontainer/scripts/version-check.sh` -- read from `.vig-os` instead of grep
- **No change**: `scripts/prepare-build.sh` -- existing `{{IMAGE_TAG}}` loop catches `.vig-os` automatically
- **Tests**: update `test_integration.py`, `test_install_script.py`, `test_image.py` assertions

### Alternatives Considered

- **TOML (`.vig-os.toml`)** -- more structured, Python-native (`tomllib`), but `initialize.sh` runs on the host where Python may not be available. Shell parsing of TOML is fragile.
- **Extend `.devcontainer/.env`** -- `.env` is gitignored and generated at runtime. A committed config requires a separate file.
- **`pyproject.toml [tool.vig-os]`** -- requires Python to parse; same host portability problem.

### Additional Context

- Related to #169 (smoke-test repo). The `.vig-os` file enables the smoke-test deploy workflow to write the RC tag to a known location.
- `initialize.sh` already writes `CONTAINER_SOCKET_PATH` to `.devcontainer/.env` -- adding `DEVCONTAINER_VERSION` follows the same pattern.
- The `.vig-os` file is extensible for future config (e.g., registry URL, org name) without changing the mechanism.

### Impact

- **Who benefits**: All downstream projects using the devcontainer template. Version detection becomes reliable and centralized.
- **Compatibility**: Backward compatible. Existing workspaces without `.vig-os` fall back to `latest` via the `${DEVCONTAINER_VERSION:-latest}` default.

### Changelog Category

Added
---

# [Comment #1]() by [c-vigo]()

_Posted on March 11, 2026 at 09:02 AM_

## Implementation Plan

### 1. Add `.vig-os` template file

Create `assets/workspace/.vig-os`:

```
# vig-os devcontainer configuration
DEVCONTAINER_VERSION={{IMAGE_TAG}}
```

The `{{IMAGE_TAG}}` placeholder is replaced at build time by `prepare-build.sh` (the existing replacement loop catches all files in `assets/workspace/` automatically -- no change to `prepare-build.sh` needed).

### 2. Switch `docker-compose.yml` to env-var interpolation

In `assets/workspace/.devcontainer/docker-compose.yml`, change:

```yaml
# Before
image: ghcr.io/vig-os/devcontainer:{{IMAGE_TAG}}

# After
image: ghcr.io/vig-os/devcontainer:${DEVCONTAINER_VERSION:-latest}
```

Docker-compose reads `DEVCONTAINER_VERSION` from `.devcontainer/.env` (populated by `initialize.sh` in step 3).

### 3. Update `initialize.sh` to source `.vig-os`

In `assets/workspace/.devcontainer/scripts/initialize.sh`, add before `configure_socket_path`:

```bash
load_vig_os_config() {
    local config_file="$DEVCONTAINER_DIR/../../.vig-os"
    local env_file="$DEVCONTAINER_DIR/.env"
    if [[ -f "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
        if [[ -n "${DEVCONTAINER_VERSION:-}" ]]; then
            echo "DEVCONTAINER_VERSION=${DEVCONTAINER_VERSION}" >> "$env_file"
        fi
    fi
}

load_vig_os_config
```

This follows the existing pattern: `initialize.sh` already writes `CONTAINER_SOCKET_PATH` to `.devcontainer/.env`.

### 4. Update `version-check.sh`

Replace the fragile `grep -o` parsing of `docker-compose.yml` (lines 194-210) with:

```bash
get_current_version() {
    local config_file
    config_file="$(dirname "$DEVCONTAINER_DIR")/.vig-os"
    if [[ -f "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
        if [[ -n "${DEVCONTAINER_VERSION:-}" && "$DEVCONTAINER_VERSION" != "dev" && "$DEVCONTAINER_VERSION" != "latest" ]]; then
            echo "$DEVCONTAINER_VERSION"
            return 0
        fi
    fi
    return 1
}
```

### 5. Update tests

- **`test_integration.py`** (`TestDevContainerDockerCompose`): the `image` field is now `ghcr.io/vig-os/devcontainer:${DEVCONTAINER_VERSION:-latest}`, not a concrete version. Adjust the assertion to check for `${DEVCONTAINER_VERSION` instead of a pinned tag. Also verify `.vig-os` contains the concrete version.
- **`test_install_script.py`** (`test_install_replaces_image_tag_placeholder`): verify `.vig-os` has the concrete version and `docker-compose.yml` no longer has `{{IMAGE_TAG}}`.
- **`test_image.py`** (`test_image_tag_replaced`): verify `.vig-os` is replaced. `docker-compose.yml` now has `${DEVCONTAINER_VERSION}` (no placeholder to replace).

### Files unchanged (confirmed)

- `scripts/prepare-build.sh` -- existing `{{IMAGE_TAG}}` loop handles `.vig-os` automatically
- `scripts/manifest.toml` -- `.vig-os` is a template file, not a synced file
- `.gitignore` -- `.vig-os` is a different name from `.env`, not gitignored

### Open questions

- **Fallback behavior**: when `.vig-os` is missing (e.g., older workspace not yet upgraded), `docker-compose.yml` defaults to `latest` via `${DEVCONTAINER_VERSION:-latest}`. Acceptable?
- **`Containerfile` manifest generation**: the `grep -rl` in the Containerfile that builds `manifest.toml` already searches for `{{IMAGE_TAG}}` -- `.vig-os` will be included. No change needed.

