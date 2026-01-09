---
type: issue
state: closed
created: 2025-12-18T12:47:15Z
updated: 2026-01-06T14:17:27Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/21
comments: 1
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-09T16:17:31.528Z
---

# [Issue 21]: [Add curl-based install script for quick devcontainer deployment](https://github.com/vig-os/devcontainer/issues/21)

## Overview

Create a `curl | sh` style install script similar to `curl -LsSf https://astral.sh/uv/install.sh | sh` for quick devcontainer deployment to new projects.

## Usage

```bash
# Basic: Initialize current directory
curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh

# With options
curl -sSf ... | sh -s -- [OPTIONS] [PATH]
```

## Features

### 1. Sensible Defaults (Zero Config)
- **Target path**: Current directory (`.`)
- **Project name**: Derived from folder name
- **SHORT_NAME**: Auto-generated from folder name using sanitization algorithm:
  ```bash
  # lowercase, replace hyphens/spaces with underscore, remove special chars
  SHORT_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed 's/[ -]/_/g' | sed 's/[^a-z0-9_]/_/g')
  ```
- **ORG_NAME**: Deprecated - hardcode to "vigOS/devc" (users can change post-install if needed)

### 2. CLI Options
| Flag | Description |
|------|-------------|
| `--force` | Overwrite existing files (for upgrades) |
| `--version VER` | Use specific version (default: `latest`) |
| `--docker` | Force docker runtime |
| `--podman` | Force podman runtime (default if available) |
| `--dry-run` | Show what would be done |
| `--name NAME` | Override project/SHORT_NAME |
| `-h, --help` | Show help |

### 3. Container Runtime Detection
- Auto-detect podman or docker
- Prefer podman if both available
- Allow override via `--docker` / `--podman` flags
- Clear error message with install instructions if neither found

### 4. Interactive Terminal Handling
- Use `< /dev/tty` for user input when stdin is consumed by curl pipe
- Graceful fallback with instructions if not interactive

### 5. Version Selection
```bash
# Latest (default)
curl -sSf ... | sh

# Specific version
curl -sSf ... | sh -s -- --version 1.0.0
```

### 6. Progress & UX
- Pull image first with progress display
- Colored output (disabled if not tty)
- Clear success message with next steps
- `--dry-run` to preview without executing

## Implementation Tasks

- [ ] Create `install.sh` script in repo root or `scripts/`
- [ ] Modify `init-workspace.sh` to accept env vars / CLI args instead of interactive prompts
  - `PROJECT_NAME` / `SHORT_NAME` from folder name
  - `ORG_NAME` hardcoded to "vigOS/devc"
  - Keep interactive mode as fallback for edge cases
- [ ] Remove `ORG_NAME` prompt (deprecate)
- [ ] Add SHORT_NAME auto-generation algorithm
- [ ] Set up hosting for install script (GitHub Pages or raw GitHub URL)
- [ ] Update README.md Quick Start section with new curl command
- [ ] Update `.devcontainer/README.md` template

## Example Workflow

```bash
# Create new project
mkdir my-awesome-project && cd my-awesome-project

# Deploy devcontainer (non-interactive!)
curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh

# Result:
# - SHORT_NAME = my_awesome_project
# - ORG_NAME = vigOS/devc
# - .devcontainer/ fully configured
# - Ready to open in VS Code
```

## Breaking Changes

- **ORG_NAME prompt removed**: Now defaults to "vigOS/devc". Users who need different org name must edit `LICENSE` file manually after install.

## Related

Replaces the current verbose command:
```bash
podman run -it --rm -v "PATH_TO_PROJECT:/workspace" \
  ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh
```
---

# [Comment #1]() by [gerchowl]()

_Posted on January 6, 2026 at 02:17 PM_

Implemented in commits:
- `5336071` feat: add curl-based install script for quick devcontainer deployment
- `2371451` feat: add --no-prompts flag to init-workspace.sh for non-interactive use
- `2463606` test: add test suite for install.sh script
- `a2cfcd6` docs: update README with curl-based install as primary quick start
- `4a6df60` docs: add install script feature to CHANGELOG

All features implemented:
✅ install.sh with --force, --version, --name, --dry-run, --docker, --podman flags
✅ Auto-detection of podman/docker runtime
✅ OS-specific installation instructions when runtime missing
✅ Runtime health check with troubleshooting advice
✅ SHORT_NAME auto-derived from folder name (sanitized)
✅ ORG_NAME defaults to 'vigOS/devc'
✅ --no-prompts flag for init-workspace.sh (CI/automation support)
✅ 19 tests (8 unit + 11 integration)
✅ Documentation updated (README, CHANGELOG)

