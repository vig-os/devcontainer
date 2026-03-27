---
type: issue
state: closed
created: 2026-03-09T09:41:21Z
updated: 2026-03-09T13:12:47Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/243
comments: 1
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:45.906Z
---

# [Issue 243]: [chore: manual integration tests for remote devcontainer features](https://github.com/vig-os/devcontainer/issues/243)

## Context

PR #166 consolidates all remote devcontainer features into `feature/70-remote-devc-orchestration`. Unit tests pass but manual integration testing on a real remote host is needed before merge.

Parent: #70

## Test Matrix

All tests require a real remote host with podman/docker installed (e.g. ksb-meatgrinder).

### 1. Core orchestration (`devc-remote.sh`)
- [x] `devc-remote.sh myserver:~/Projects/fd5` — SSH, preflight, compose up _(tested via `gh:` target, IDE open tested separately)_
- [x] Re-run with container already running — skips compose up, opens editor
- [x] Re-run with container stopped — restarts and opens
- [x] `--open none` — infra only, no IDE launch
- [x] `--open ssh` — waits for Tailscale, prints hostname
- [x] `--open code` — opens VS Code instead of Cursor
- [x] `--yes` flag — auto-accepts prompts (reuse running container)

### 2. Tailscale SSH integration (#208, #230)
- [x] With `TS_CLIENT_ID` + `TS_CLIENT_SECRET` set — generates ephemeral key, injects into remote compose
- [x] Container joins tailnet after compose up
- [x] `--open ssh` mode — polls `tailscale status`, prints hostname when ready
- [x] Without TS env vars — silently skips (no error)

### 3. Claude Code CLI (#70)
- [x] With `CLAUDE_CODE_OAUTH_TOKEN` set — injects token into remote compose
- [x] `setup-claude.sh install` inside container — installs CLI, creates `claude` user
- [x] `claude` wrapper auto-switches to non-root user when run as root
- [x] `setup-claude.sh start` — refreshes workspace permissions
- [x] Without token — silently skips (no error)

### 4. Container lifecycle execution (#70)
- [x] Fresh container — runs `post-create.sh` then `post-start.sh` inside container
- [x] Existing running container — runs only `post-start.sh` (skips post-create)
- [x] Lifecycle scripts not present — skips gracefully with log message

### 5. `--bootstrap` (#235)
- [x] First run on clean host — prompts for `projects_dir`, creates config, forwards GHCR auth, clones devcontainer repo, builds image _(build fails without `uv` — see bugs)_
- [x] `--bootstrap --yes` — uses defaults without prompting
- [x] Re-run — reads existing config, skips prompts, pulls latest, rebuilds
- [x] GHCR auth forwarding — podman credentials or `GHCR_TOKEN` copied to remote

**Note:** Bootstrap will likely be simplified or removed post-release. GHCR auth forwarding should move into the normal deploy flow. See #246.

### 6. `gh:org/repo[:branch]` (#236)
- [x] `devc-remote.sh myserver gh:vig-os/fd5` — clones to `~/Projects/fd5`, starts devcontainer
- [x] `devc-remote.sh myserver gh:vig-os/fd5:feature/my-branch` — clones and checks out branch
- [x] Re-run with repo already cloned — fetches, doesn't re-clone
- [x] `devc-remote.sh myserver:~/custom/path gh:vig-os/fd5` — overrides clone location
- [x] Branch switch on existing clone — checks out new branch

### 7. Compose file parsing (#70)
- [x] `read_compose_files()` correctly reads `dockerComposeFile` array from devcontainer.json
- [x] `compose_cmd_with_files()` builds correct `-f` flags
- [x] Works with single file string and multi-file array

### 8. Edge cases
- [ ] Low disk space warning (<2GB) shown
- [ ] Remote host without compose — clear error message
- [ ] Remote host without container runtime — clear error message
- [x] SSH connection failure — clear error message
- [ ] macOS remote host — warning shown

### Summary: 36/39 passed

Remaining 3 items (8.1–8.3, 8.5) require special host conditions that are already covered by unit tests.

## Bugs Found

1. **SSH drops empty args / expands `~`** — Fixed with sentinel values `_NONE_` / `_DEFAULT_`.
2. **Stopped container runs post-create** — `CONTAINER_FRESH=1` set on restart, not just creation. Idempotent but wasteful.
3. **Bootstrap `build.sh` fails without `uv` in PATH** — `prepare-build.sh` requires `uv` which isn't in default PATH on remote.
4. **Bootstrap `registry` config field is unused** — Stored but never passed to `build.sh`. Likely should be removed entirely (see #246).

## Design Decisions (from testing session)

- **GHCR auth should forward on every deploy** — idempotent, ensures remote always has valid creds. No separate bootstrap step needed. See #246.
- **`--bootstrap` can be removed post-release** — once image is on GHCR, no need to build from source on remote. See #246.
- **`just remote-devc <server>` is the target DX** — auto-detect repo+branch, guard unpushed commits, single command. See #246.

Refs: #70

---

# [Comment #1]() by [gerchowl]()

_Posted on March 9, 2026 at 01:12 PM_

Integration testing complete — 36/39 items verified on ksb-meatgrinder. Remaining 3 edge cases (low disk, no compose, no runtime) are covered by unit tests. Two bugs found and fixed in feature/70-remote-devc-orchestration (commits 17ca79f, 9280224). GHCR auth forwarding moved into normal deploy flow. See #246 for follow-up (simplify bootstrap, just remote-devc recipe).

