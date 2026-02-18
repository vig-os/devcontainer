---
type: issue
state: open
created: 2026-02-18T01:46:51Z
updated: 2026-02-18T01:46:51Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/71
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T01:47:06.433Z
---

# [Issue 71]: [[FEATURE] Expand justfile.base with devcontainer, quality, security, docs, info, and git recipes](https://github.com/vig-os/devcontainer/issues/71)

### Description

Expand `assets/workspace/.devcontainer/justfile.base` with ~18 new recipes covering devcontainer lifecycle, code quality, security scanning, documentation, environment info, git helpers, and release utilities. Also add commented-out stubs to `assets/workspace/justfile.project` for opinionated recipes teams can customize.

### Problem Statement

The current `justfile.base` ships only 9 recipes (lint, format, precommit, test-pytest, test-cov, sync, update, clean-artifacts, sidecars/sidecar). Developers in downstream projects must manually run docker compose commands to start/stop the devcontainer, have no local CI mirror, no security scanning shortcuts, and no quick environment diagnostics. This leads to inconsistent workflows and repeated boilerplate across projects.

### Proposed Solution

Add the following recipes to `justfile.base` (managed by devcontainer, replaced on upgrade):

**devcontainer group (7 recipes):**
- `up` — start devcontainer + sidecars via compose (auto-detect podman/docker)
- `open` — open Cursor/VS Code attached to the running container
- `down` — stop and remove containers
- `status` — show container status
- `logs *args` — tail container logs
- `shell` — open bash in running container
- `restart *args` — restart service(s)

**quality group (2 new recipes, extending existing):**
- `check` — run lint + format-check + test-pytest (local CI mirror)
- `format-check` — verify formatting without changing files

**security group (2 recipes):**
- `audit` — dependency vulnerability scan via pip-audit
- `scan` — static security analysis via bandit

**docs group (2 recipes):**
- `docs` — live-preview documentation via mkdocs serve
- `docs-build` — build docs with strict mode (for CI validation)

**info group (3 recipes):**
- `env-info` — print Python/uv/OS versions and key env vars
- `outdated` — show stale dependencies
- `version` — print current project version from pyproject.toml

**git group (2 recipes):**
- `log` — pretty one-line git log (last 20 commits)
- `branch` — show current branch + list recent branches

**release group (1 recipe):**
- `changelog` — print the Unreleased section of CHANGELOG.md

**justfile.project stubs (commented-out):**
- `run`, `serve`, `migrate`, `seed`, `docs-deploy`

Container runtime auto-detection: try `podman compose` first, fall back to `docker compose`.

### Alternatives Considered

- **Keep justfile.base minimal**: Let each project add its own recipes. Downside: duplicated boilerplate, inconsistent UX across projects.
- **Ship a large opinionated justfile.base**: Include framework-specific recipes (FastAPI, alembic, etc.). Downside: not universal — would break for non-matching projects.
- **Chosen approach**: Universal recipes in `justfile.base` + commented-out stubs in `justfile.project` for opinionated patterns.

### Impact

- Benefits all downstream projects using the vigOS devcontainer
- Backward compatible — adds new recipes, does not modify existing ones
- Recipes that depend on optional tools (mkdocs, pip-audit, bandit) fail gracefully if the tool is not installed

### Changelog Category

Added
