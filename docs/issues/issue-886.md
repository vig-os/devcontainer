---
type: issue
state: closed
created: 2026-07-07T09:16:22Z
updated: 2026-07-08T07:41:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/886
comments: 1
labels: feature, priority:medium, area:workspace, effort:medium, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:29.068Z
---

# [Issue 886]: [feat(workspace): preflight guard for scaffold upgrades — require a dedicated clean branch, add diff preview](https://github.com/vig-os/devkit/issues/886)

### Description

Scaffold upgrades (`just devc-upgrade`, or `curl … install.sh | bash -s -- --force .`) mutate and delete files in the consumer repo — rsync over the working tree, mode-dependent pruning (`rm -rf .devcontainer/` in direnv mode), placeholder substitution, `sed -i` on `.vig-os`. Today they run against **any branch and any tree state**: nothing stops an upgrade landing directly on `main`/`dev` or on top of uncommitted work, entangling a large mechanical diff with unrelated changes and making a bad upgrade hard to review or revert.

Add a preflight guard so an **upgrade** only proceeds on a dedicated working branch with a clean tree, plus a first-class diff preview. Fresh installs are exempt.

Field context: the 0.4.0 consumer validation (EXOMA/hyrr, EXOMA/talys — see #877, #878) showed exactly why isolation matters: upgrades silently clobbered `.pre-commit-config.yaml` and stranded recipes, and recovery relied on the upgrade being a distinguishable diff. A guard makes every upgrade a single revertible, reviewable commit series on its own branch by construction.

### Problem Statement

- `install.sh --force` (which `devc-upgrade` wraps: `.devcontainer/justfile.devc:77`) performs no git checks at all before letting `init-workspace.sh` rewrite the tree.
- `init-workspace.sh` shows a conflict report (`assets/init-workspace.sh:223-281`) but with `--no-prompts` — the only mode `install.sh` uses — it proceeds without confirmation.
- An upgrade on a dirty tree mixes scaffold changes with WIP; an upgrade on `main`/`dev` violates the org's issue → branch → PR flow and can't be PR-reviewed.
- `install.sh --dry-run` only prints the container command (`install.sh:490-499`); there is no "what files would change" preview short of running the real thing.

### Proposed Solution

**Placement: host-side in `install.sh`, gating the `--force` (upgrade) path.** Both supported entry points funnel through it (`devc-upgrade` → `curl install.sh | bash -s -- --force .`). The host is also the only place git state is reliably visible: the container mounts only `$PROJECT_PATH`, so in a **git worktree** (where `.git` is a file pointing at an unmounted gitdir) git is unusable inside the container — an in-container guard would misfire exactly in the worktree-heavy flows this org uses.

Guard logic (runs only when `--force` is given, i.e. upgrades; plain installs into empty dirs are untouched):

1. **Not a git repo / git unavailable** → warn loudly ("no VCS safety net — cannot revert a bad upgrade") and require explicit confirmation (or `--skip-preflight`) to continue.
2. **Branch check** — resolve `git -C "$PROJECT_PATH" rev-parse --abbrev-ref HEAD`:
   - Refuse on `main`, `dev`, `release/*` (prefix match), and detached `HEAD`.
   - On a protected branch with a clean tree, **offer to create and switch to `chore/devkit-upgrade-<version>`** and proceed there (chore branches carry no issue number per the branch-naming convention, so no issue is required). Non-interactively: refuse with that command as the hint.
   - Any other branch (e.g. an existing `feature/…`) → allowed.
3. **Clean-tree check** — require empty `git status --porcelain` output: no staged/unstaged changes and no untracked-unignored files. Gitignored clutter (`.venv/`, `.direnv/`, editor dirs) does not count as dirty, so real-world repos pass. Dirty tree → hard refusal (commit/stash first).
4. **Escape hatch** — a single `--skip-preflight` flag bypasses both checks (it cannot be `--force`, which already means "upgrade"). Printed in every refusal message.
5. **Exemptions:**
   - `--smoke-test` runs skip the guard entirely — the downstream smoke-test CI checks out `dev` and runs `install.sh --version <tag> --smoke-test --force --docker .` headless (devcontainer-smoke-test `repository-dispatch.yml:205`); without the exemption the guard would break the release gate.
   - Fresh installs (no `--force`) are exempt; the existing "workspace not empty" refusal (`assets/init-workspace.sh:142-147`) already covers accidental re-runs. If a user re-runs the installer intending a fresh start over an existing scaffold, they are by definition on the `--force` path and get the guard.

**Diff preview:** add `--preview` that runs the existing conflict-report machinery (`assets/init-workspace.sh:223-281` already computes OVERWRITTEN/PRESERVED sets) and **exits before mutating anything**, extended to also list mode-prune **deletions** (e.g. `.devcontainer/` removal in direnv mode). `install.sh` forwards it. This is distinct from the existing `install.sh --dry-run`, which prints the container command only — document the difference in `--help`.

#### Tasks

- [ ] `install.sh`: preflight function (repo detection, branch check with `release/*` prefix and detached-HEAD handling, `git status --porcelain` clean check), wired to the `--force` path only
- [ ] `install.sh`: interactive offer to create + switch to `chore/devkit-upgrade-<version>`; non-interactive refusal with hint
- [ ] `install.sh`: `--skip-preflight` flag; `--smoke-test` exemption; warn+confirm path for non-git directories
- [ ] `init-workspace.sh`: `--preview` mode — existing conflict report + prune-deletion listing, then exit 0 without touching the tree; forwarded from `install.sh`
- [ ] `devc-upgrade` recipe: surface the new flags in its help text (no logic change — it inherits the guard via install.sh)
- [ ] Docs: `docs/MIGRATION.md` upgrade section + `install.sh --help` text
- [ ] Tests: `tests/bats/install.bats` (guard: protected branches, dirty tree, detached HEAD, worktree fixture, `--skip-preflight`, `--smoke-test` exemption, non-git dir) and `tests/bats/init-workspace.bats` (`--preview` leaves tree untouched, lists deletions)
- [ ] CHANGELOG `## Unreleased` → Added

#### Acceptance criteria

- `install.sh --force` on `main`, `dev`, `release/*`, or detached HEAD refuses (exit ≠ 0) with an actionable message; on other branches with a clean tree it proceeds.
- Dirty tree (tracked change **or** untracked-unignored file) refuses; gitignored files do not trip it.
- Guard works in a git worktree (`.git` file) on the host.
- `--skip-preflight` bypasses; `--smoke-test` is unaffected end-to-end (smoke CI stays green).
- `--preview` produces the add/overwrite/preserve/delete report and leaves the tree byte-identical.
- Fresh install into an empty directory is unchanged.
- bats suites green.

### Alternatives Considered

- **Guard inside `init-workspace.sh` (in-container):** rejected as primary — git worktrees mount without their gitdir, so branch/status detection fails exactly where this org works most; also `--smoke-test` internally sets `FORCE=true` (`assets/init-workspace.sh:104-108`), making exemption logic messier. A best-effort in-container warning could be added later for direct `podman run … init-workspace.sh --force` invocations, which bypass the host guard (accepted residual gap).
- **Denylist by exact names only (`main`, `dev`, `release`):** too brittle — release branches are `release/X.Y.Z` (prefix), and detached HEAD has no name at all. Refuse protected names/prefixes + detached HEAD, allow the rest.
- **Require an issue-numbered branch (`<type>/<issue>-…`):** over-strict; the branch-naming convention explicitly allows `chore/<summary>` without an issue for routine maintenance, which a scaffold upgrade is.
- **Split escape flags (`--allow-branch` / `--allow-dirty`):** more precise but two knobs for one rare action; a single `--skip-preflight` keeps the mental model simple.
- **Hard refusal on non-git directories:** a non-repo consumer is unusual but legitimate; refusing outright would strand them with no VCS to protect anyway. Warn + confirm instead.

### Additional Context

- Relates: #877, #878 (0.4.0 upgrade-path defects this guard would have contained), and #885 (declarative `.vig-os` manifest), whose mode-switch case (`devcontainer` → `direnv`/`bare` deletes `.devcontainer/`) is the sharpest destructive path and should default to `--preview` first (owned there).
- Entry-point map: `just devc-upgrade` (`assets/workspace/.devcontainer/justfile.devc:35-77`) → `curl install.sh | bash -s -- --force .` → `podman|docker run … /root/assets/init-workspace.sh --no-prompts --force` (`install.sh:467-488`).
- CI audit: `nix-image.yml:198` runs `init-workspace.sh` directly against a fresh `mktemp -d` (host guard not in path — unaffected); smoke-test dispatch uses `--smoke-test --force` headless on a `dev` checkout (exempted above). No other automated `install.sh` consumers found; Renovate only bumps pins and never runs upgrades.

### Impact

- Everyone running scaffold upgrades benefits: upgrades become isolated, reviewable, revertible diffs on their own branch, in line with the issue → branch → PR convention.
- Backward compatible for fresh installs and smoke-test automation. Behavior change only for `--force` upgrades on protected branches or dirty trees — which is the point; `--skip-preflight` restores the old behavior. SemVer: **minor**.

### Changelog Category

Added

Refs: #877, #878, #885

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #903 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

