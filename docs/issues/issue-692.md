---
type: issue
state: open
created: 2026-06-24T15:22:18Z
updated: 2026-06-24T15:25:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/692
comments: 0
labels: bug, priority:high, area:testing
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:55.858Z
---

# [Issue 692]: [[BUG] testinfra init fixture times out on uv sync of heavy extras (30s 'completed' wait)](https://github.com/vig-os/devcontainer/issues/692)

## Description

The session-scoped `initialized_workspace` fixture in `tests/conftest.py` times
out during the **`syncing_deps` → `completed`** transition, causing an `ERROR at
setup` that cascades to **every** test depending on it (`TestDevContainerStructure`,
etc.).

The init pipeline reaches `Syncing dependencies...` (emitted by
`assets/init-workspace.sh:398`), which runs `just sync` →
`uv sync --all-extras --all-groups` (`assets/workspace/justfile.project:59-60`).
The test-project's optional dependencies are heavy scientific packages
(`numpy==2.5.0`, `scipy==1.18.0`, `pandas==3.0.3`, `matplotlib==3.11.0`,
`jupyter==1.1.1`/`jupyterlab`), totalling tens of MB. The image ships **no warm
`uv` cache**, so on a cold/slow network the download is still in flight when the
**30s** timeout for `"Workspace initialized successfully"` fires
(`tests/conftest.py:350`).

The captured `before` buffer shows the failure mid-download:

```
⠹ Preparing packages... (114/119)
pandas      ------ 10.22 MiB/10.41 MiB
matplotlib  ------ 10.08 MiB/10.61 MiB
numpy       ------ 10.32 MiB/15.88 MiB
jupyterlab  ------ 10.09 MiB/16.35 MiB
scipy       ------ 10.34 MiB/33.65 MiB
```

```
Current stage: syncing_deps
Time in stage: 30.0s (timeout: 30s)
✗ completed: not reached
```

This is a flaky-by-network failure: it passes when PyPI is fast or the uv cache
is warm, and fails on a cold/slow run. It is **infrastructure flakiness, not a
product defect** in the init script itself.

## Steps to Reproduce

1. Cold `uv` cache (fresh image / no prior sync), unthrottled-but-realistic network.
2. Run the testinfra suite, e.g. `just test` / `pytest tests/` against
   `ghcr.io/vig-os/devcontainer:dev`.
3. The `initialized_workspace` fixture setup runs the interactive init.
4. Observe `ERROR at setup of ...` with `pexpect.exceptions.TIMEOUT` at the
   `"Workspace initialized successfully"` wait.

## Expected Behavior

The init fixture completes deterministically regardless of how long
`uv sync` spends downloading the test-project's heavy extras, and dependent
tests run.

## Actual Behavior

The 30s `completed` timeout fires while `uv sync` is still downloading
numpy/scipy/pandas/matplotlib/jupyterlab, the session fixture errors, and all
dependent tests are reported as `ERROR at setup`.

## Environment

- **OS**: Linux
- **Container Runtime**: Podman 5.8.2 (Nix store path)
- **Image Version/Tag**: `ghcr.io/vig-os/devcontainer:dev`
- **Architecture**: AMD64
- **Python**: CPython 3.14

## Additional Context

- Relevant code:
  - `tests/conftest.py:346-351` — `stage_patterns_after_copy`, `completed` timeout = 30s
  - `tests/conftest.py:442-474` — the timeout/`pytest.fail` path
  - `assets/init-workspace.sh:398-402` — `Syncing dependencies...` → `just sync`
  - `assets/workspace/justfile.project:59-60` — `uv sync --all-extras --all-groups`
  - `assets/workspace/pyproject.toml` — heavy optional deps
- Because `initialized_workspace` is **session-scoped**, one slow sync errors the
  whole suite, matching the "many tests fail like this" symptom.
- Closely related to **#635** (make the testinfra suite portable / TEST ADAPTATION).

## Possible Solution

One or more of:

1. **Raise / make configurable** the `completed` (and `syncing_deps`) timeout in
   `tests/conftest.py` to cover a cold-cache download (e.g. env-overridable, with
   a generous default like 180–300s). Lowest-effort fix.
2. **Warm the `uv` cache in the image build** (prefetch the test-project extras
   into `UV_CACHE_DIR`) so `uv sync` is offline-fast and deterministic — aligns
   with the Nix-built-image work.
3. **Trim the test-project's `--all-extras`** for the init smoke path, or sync
   `--no-install-project`/offline, so the structure tests don't pay for the full
   scientific stack.

Prefer (1) for an immediate unblock; (2) for the durable fix under the Nix image.

## Changelog Category

No changelog needed (test infrastructure).

