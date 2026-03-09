---
type: issue
state: open
created: 2026-03-06T21:57:36Z
updated: 2026-03-08T19:28:38Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/236
comments: 2
labels: feature, area:workflow, effort:large
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-03-09T04:23:41.013Z
---

# [Issue 236]: [devc-remote gh:org/repo:branch — clone project repo and start devcontainer](https://github.com/vig-os/devcontainer/issues/236)

## Context

After `--bootstrap` (#235) prepares a remote host with the devcontainer image, we still need a way to clone a project repo and start its devcontainer in one command.

Refs: #70, #231, #235

## Proposal

Support a `gh:org/repo[:branch]` target syntax in `devc-remote.sh`:

```bash
# Clone fd5, checkout main, init-workspace, compose up, connect
devc-remote.sh ksb-meatgrinder gh:vig-os/fd5

# Clone at specific branch
devc-remote.sh ksb-meatgrinder gh:vig-os/fd5:feature/my-branch

# Existing path still works (current behavior)
devc-remote.sh ksb-meatgrinder:~/Projects/fd5
```

### Flow

1. Read remote config (`~/.config/devc-remote/config.yaml` from #235) for `projects_dir`
2. Clone `gh:org/repo` to `<projects_dir>/<repo>` (or fetch + checkout if already cloned)
3. Checkout `:branch` if specified, default branch otherwise
4. Run `init-workspace.sh` on remote (resolves `{{IMAGE_TAG}}`, `{{SHORT_NAME}}` templates)
5. Proceed with existing `compose up` + connect flow

### Re-run behavior

- Repo already cloned → `git fetch && git checkout <branch>` (no re-clone)
- Container already running on the right branch → skip compose restart, just connect
- Different branch requested → checkout, re-init if needed, `compose up`

### Config interaction

Uses `projects_dir` from remote config (#235) to determine clone location. Falls back to `~/Projects` if no config exists.

## Acceptance criteria

- [ ] `gh:org/repo` clones to `<projects_dir>/<repo>` on remote
- [ ] `gh:org/repo:branch` checks out specified branch
- [ ] Already-cloned repos are fetched, not re-cloned
- [ ] `init-workspace.sh` runs after clone/checkout
- [ ] Existing `host:path` syntax continues working
- [ ] Tests for arg parsing of `gh:` syntax
---

# [Comment #1]() by [gerchowl]()

_Posted on March 8, 2026 at 04:51 PM_

## Design

### Arg parsing changes (`parse_args`)

Detect `gh:` prefix on the second positional arg:
- `gh:org/repo` → `GH_REPO=org/repo`, `GH_BRANCH=""` (default branch)
- `gh:org/repo:branch` → `GH_REPO=org/repo`, `GH_BRANCH=branch`
- If `host:path` is also present, `REMOTE_PATH` is set from it. Otherwise resolved later from remote config.

New variables: `GH_REPO`, `GH_BRANCH`, `GH_MODE` (0/1).

### New function: `remote_clone_project()`

Inserted in `main()` after `check_ssh` but before `remote_preflight`. Only runs when `GH_MODE=1`.

Steps (single SSH call, remote bash script):
1. If `REMOTE_PATH` not set by user: read `projects_dir` from `~/.config/devc-remote/config.yaml`, fallback `~/Projects`. Set `target_dir=$projects_dir/$repo_name`.
2. If `target_dir` doesn't exist: `git clone https://github.com/org/repo.git target_dir`
3. If it exists: `cd target_dir && git fetch`
4. If branch specified: `git checkout $branch`
5. If fresh clone: run `init-workspace.sh --no-prompts` (derive `SHORT_NAME` from repo name)
6. Echo `CLONE_PATH=<resolved_path>` back to local script

Local side: parse `CLONE_PATH` from output, set `REMOTE_PATH` to it for the rest of the pipeline.

### Clone URL

Uses `https://github.com/${GH_REPO}.git` — works without SSH keys for public repos, with `gh auth` or git credential helpers for private ones.

### SSH call count impact

One new SSH call when `GH_MODE=1`, inserted before preflight. Test mocks need counter adjustment.

### init-workspace.sh

Only runs on fresh clone (not on re-connect or branch switch). Passes `--no-prompts` with `SHORT_NAME` derived from repo name.

### Test plan

- **Arg parsing:** `gh:org/repo`, `gh:org/repo:branch`, combined with `host:path`, missing repo, invalid format
- **Clone function:** fresh clone path, existing repo fetch path, branch checkout, init-workspace only on fresh clone
- **Integration:** full pipeline with `gh:` target flows through to compose up

---

# [Comment #2]() by [gerchowl]()

_Posted on March 8, 2026 at 05:23 PM_

## Implementation Plan

Issue: #236
Branch: `feature/236-remote-gh-clone-target`

### Tasks

- [x] Task 1: Test `parse_args` recognizes `gh:org/repo` as second positional arg — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 2: Test `parse_args` recognizes `gh:org/repo:branch` with branch extraction — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 3: Test `parse_args` accepts `host:path` combined with `gh:org/repo` — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 4: Test `parse_args` rejects `gh:` with missing repo — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 5: Implement `gh:` arg parsing in `parse_args` — set `GH_REPO`, `GH_BRANCH`, `GH_MODE` — `scripts/devc-remote.sh` — verify: `just test-bats` (GREEN)
- [x] Task 6: Test `remote_clone_project` fresh clone path (mocked SSH) — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 7: Test `remote_clone_project` existing repo fetch path — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 8: Test `remote_clone_project` branch checkout — `tests/bats/devc-remote.bats` — verify: `just test-bats` (RED)
- [x] Task 9: Implement `remote_clone_project` function — `scripts/devc-remote.sh` — verify: `just test-bats` (GREEN)
- [x] Task 10: Wire `remote_clone_project` into `main()` between `check_ssh` and `remote_preflight` — `scripts/devc-remote.sh` — verify: `just test-bats` (GREEN)
- [ ] Task 11: Update help text and usage examples with `gh:` syntax — `scripts/devc-remote.sh` — verify: `just test-bats`
- [ ] Task 12: Update CHANGELOG.md `## Unreleased` — `CHANGELOG.md` — verify: visual review

