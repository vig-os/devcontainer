---
type: issue
state: open
created: 2026-02-25T11:05:57Z
updated: 2026-02-25T11:08:07Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/202
comments: 0
labels: bug, area:workspace, effort:small, area:testing, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-26T04:22:23.976Z
---

# [Issue 202]: [[BUG] BATS detect_editor_cli 'neither cursor nor code' test is host-dependent](https://github.com/vig-os/devcontainer/issues/202)

### Description

The BATS test for `detect_editor_cli` assumes `PATH=\"/usr/bin:/bin\"` contains neither `cursor` nor `code`, but on some hosts `/usr/bin/code` exists. This makes the test fail for environment reasons rather than script logic.

### Steps to Reproduce

1. Check out branch `feature/70-remote-devc-orchestration`.
2. Run `just build no_cache`.
3. Run `just check`.
4. Observe failure in `tests/bats/devc-remote.bats` for:
   - `detect_editor_cli fails when neither cursor nor code in PATH`

### Expected Behavior

The test should deterministically validate the "neither editor CLI found" path, independent of host-installed binaries.

### Actual Behavior

On environments where `code` exists in `/usr/bin`, `detect_editor_cli` selects `code` and execution proceeds to SSH checks. The assertion expecting `Neither cursor nor code` fails.

### Environment

- **OS**: Linux 6.17.0-14-generic
- **Container Runtime**: N/A (failure occurs before remote runtime checks)
- **Image Version/Tag**: N/A
- **Architecture**: AMD64

### Additional Context

Observed output snippet:

- `ℹ  Detecting local editor CLI...`
- `✓  Using code`
- `ℹ  Checking SSH connectivity to myserver...`
- `✗  Cannot connect to myserver. Check your SSH config and network.`

Likely fix: isolate PATH in the test with an empty temp directory and invoke `/bin/bash "$DEVC_REMOTE"` under `env -i` to keep shebang behavior deterministic.

Related:
- PR #166
- Feature issue #152 (part of #70)

### Possible Solution

Update the failing test setup to avoid `/usr/bin:/bin` assumptions and use a controlled PATH with no `cursor`/`code` binaries.

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] Reproduced on host with `/usr/bin/code`
- [ ] Test updated to be environment-independent
- [ ] `tests/bats/devc-remote.bats` passes locally and in CI
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
