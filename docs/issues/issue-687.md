---
type: issue
state: closed
created: 2026-06-24T14:08:10Z
updated: 2026-07-01T11:17:52Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/687
comments: 1
labels: bug, priority:high, area:workspace, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:05.949Z
---

# [Issue 687]: [[BUG] just test fails on NixOS hosts: #!/bin/bash shebang in host scripts (install.sh, initialize.sh, version-check.sh)](https://github.com/vig-os/devkit/issues/687)

## Description

On a **NixOS host**, a fresh `just build && just test` fails three host-executed-script tests because the scripts carry a non-portable `#!/bin/bash` shebang. NixOS does **not** provide `/bin/bash` (it ships `/bin/sh` only; bash lives in `/nix/store/...`), so any attempt to execute these scripts directly fails before a single line runs.

The failure is easy to misread: Python's `subprocess` reports `FileNotFoundError` pointing at the **script path itself**, even though the script exists. That is the canonical signature of a missing *interpreter* in the shebang line, not a missing file. (`install.sh` provably exists at the repo root, yet the test still raises `FileNotFoundError: .../install.sh`.)

This is the same NixOS-onboarding class of bug as #683 (uv CPython) and #685 (podman `policy.json`): things that "just work" on the Debian-based CI runner and inside the container, but break on a NixOS host.

## Affected scripts (host-executed)

These three run on the **host** and are the ones the failing tests execute directly:

- `install.sh` — the host installer (`#!/bin/bash`)
- `assets/workspace/.devcontainer/scripts/initialize.sh` — wired as devcontainer `initializeCommand`, which runs on the host before the container starts (`#!/bin/bash`)
- `assets/workspace/.devcontainer/scripts/version-check.sh` — run on the host via `just check` (`justfile.devc`) and by the test suite (`#!/bin/bash`)

Precedent for the fix already exists in the repo: `scripts/init.sh`, `scripts/clean.sh`, and `assets/workspace/.devcontainer/scripts/copy-host-user-conf.sh` already use the portable `#!/usr/bin/env bash`.

## Steps to Reproduce

1. On a NixOS host (no `/bin/bash`), inside the flake dev-shell.
2. Run `just build && just test`.
3. Observe the three failures below.

## Expected Behavior

Host-executed scripts run on a NixOS host; `just test` does not fail on shebang resolution.

## Actual Behavior

```
tests/test_install_script.py::TestInstallScriptIntegration::test_install_creates_devcontainer_directory
  FileNotFoundError: [Errno 2] No such file or directory: '.../devcontainer/install.sh'

tests/test_integration.py::TestVigOsConfig::test_initialize_writes_devcontainer_version_to_env
  FileNotFoundError: [Errno 2] No such file or directory: '.../.devcontainer/scripts/initialize.sh'

tests/test_integration.py::TestVersionCheckScript::test_enable_command
  FileNotFoundError: [Errno 2] No such file or directory: '.../.devcontainer/scripts/version-check.sh'
```

(All three scripts are present on disk — `init-workspace.sh` rsyncs the workspace tree into the target — so this is interpreter resolution, not a missing file.)

## Environment

- **OS**: NixOS 26.05 (Yarara)
- **Container Runtime**: Podman (flake dev-shell)
- **Image Version/Tag**: `dev` (`just build`)
- **Architecture**: x86_64

## Root cause

`#!/bin/bash` is non-portable. NixOS does not create `/bin/bash`; only `/bin/sh` is provided. The kernel cannot resolve the interpreter, so `execve` returns `ENOENT`, surfaced by `subprocess` as `FileNotFoundError` against the script path.

## Suggested fix

Change the shebang of the three host-executed scripts to the portable form already used elsewhere in the repo:

```sh
#!/usr/bin/env bash
```

- `install.sh`
- `assets/workspace/.devcontainer/scripts/initialize.sh`
- `assets/workspace/.devcontainer/scripts/version-check.sh`

### Optional consistency sweep (separate concern)

For SSoT consistency, the remaining `#!/bin/bash` scripts could be converted too, but they are **not** the cause of these failures — they run **inside** the Debian-based container (lifecycle hooks `post-create.sh`, `post-start.sh`, `post-attach.sh`, `init-git.sh`, `init-precommit.sh`, `setup-gh-repo.sh`, `setup-git-conf.sh`, `verify-auth.sh`) or inside the image (`assets/init-workspace.sh`), where `/bin/bash` exists. Converting them is harmless but out of scope for the test failures.

### Workaround

Run the scripts through an explicit interpreter, e.g. `bash install.sh ...`, or provide `/bin/bash` on the host.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:17 AM_

Resolved on `dev` by PR #690 (`fix(setup): use portable #!/usr/bin/env bash in host scripts`). `install.sh`, `initialize.sh`, and `version-check.sh` now use `#!/usr/bin/env bash`, with a bats assertion enforcing the portable shebang.

