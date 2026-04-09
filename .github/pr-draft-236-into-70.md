## Description

Add `gh:org/repo[:branch]` target syntax to `devc-remote.sh`, enabling one-command clone-and-start of a project's devcontainer on a remote host. Existing `host:path` syntax continues to work unchanged.

## Type of Change

- [x] `feat` -- New feature
- [ ] `fix` -- Bug fix
- [ ] `docs` -- Documentation only
- [ ] `chore` -- Maintenance task (deps, config, etc.)
- [ ] `refactor` -- Code restructuring (no behavior change)
- [ ] `test` -- Adding or updating tests
- [ ] `ci` -- CI/CD pipeline changes
- [ ] `build` -- Build system or dependency changes
- [ ] `revert` -- Reverts a previous commit
- [ ] `style` -- Code style (formatting, whitespace)

### Modifiers

- [ ] Breaking change (`!`) -- This change breaks backward compatibility

## Changes Made

- `scripts/devc-remote.sh` — Extended `parse_args` to recognize `gh:org/repo[:branch]` as second positional arg; new `remote_clone_project` function (single SSH call: clone or fetch, optional branch checkout, config-based path resolution); wired into `main()` between `check_ssh` and `remote_preflight`; updated help text with new syntax and examples
- `assets/workspace/scripts/devc-remote.sh` — Synced copy via manifest
- `tests/bats/devc-remote.bats` — 7 new tests: 4 for arg parsing (gh:org/repo, gh:org/repo:branch, host:path+gh:, invalid gh:), 3 for clone function (fresh clone, fetch existing, branch checkout)
- `CHANGELOG.md` — Added entry under Unreleased

## Changelog Entry

### Added
- **`gh:org/repo[:branch]` target for devc-remote** ([#236](https://github.com/vig-os/devcontainer/issues/236))
  - Clone a GitHub repo on the remote host and start its devcontainer in one command
  - Supports `gh:org/repo` (default branch) and `gh:org/repo:branch` (specific branch)
  - Already-cloned repos are fetched, not re-cloned
  - Clone location resolved from remote config `projects_dir` or overridden via `host:path`

## Testing

- [x] Tests pass locally (`just test`)
- [ ] Manual testing performed (describe below)

### Manual Testing Details

N/A

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated the documentation accordingly (edit `docs/templates/`, then run `just docs`)
- [x] I have updated `CHANGELOG.md` in the `[Unreleased]` section (and pasted the entry above)
- [x] My changes generate no new warnings or errors
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

Design: https://github.com/vig-os/devcontainer/issues/236#issuecomment-4019537584

Refs: #236
