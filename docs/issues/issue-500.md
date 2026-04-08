---
type: issue
state: closed
created: 2026-04-07T18:31:48Z
updated: 2026-04-07T21:45:58Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/500
comments: 0
labels: bug, priority:high, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-08T04:42:42.283Z
---

# [Issue 500]: [[BUG] Release rollback fails silently -- retry exit-code bug and branch protection conflict](https://github.com/vig-os/devcontainer/issues/500)

### Description

The rollback job in `release.yml` fails silently due to two compounding bugs:

1. **`retry` helper always returns exit 0.** In `.github/actions/setup-env/action.yml` (lines 157–216), the pattern `if "$@"; then return 0; fi; rc=$?` captures `$?` of the `fi` statement (always 0), not the command's exit code. Every workflow step that relies on `retry` to propagate failures is affected.

2. **Force-push rollback blocked by repository rulesets.** The rollback step uses `gh api PATCH refs/heads/release/... -F force=true`, which is rejected with HTTP 422 ("Cannot force-push to this branch — Changes must be made through a pull request"). Combined with bug 1 and `continue-on-error: true`, the failure is completely invisible — the job reports success while the finalize commit remains on the branch.

### Steps to Reproduce

1. Trigger the release workflow (final) on a protected `release/*` branch.
2. Let the finalize job commit changes via API (commit-action succeeds because it creates commits, not force-pushes).
3. Let a subsequent finalize step fail (in this case, "Check if publish tag already exists at finalize SHA" found a stale `0.3.2` tag from a prior attempt pointing to `059bde7`, not the new finalize SHA `10e2ff3`).
4. Observe the rollback job: all 3 `retry` attempts return HTTP 422, but `retry` reports `exit 0` each time and the script prints "Release branch rolled back to ...".
5. The auto-created failure issue (#499) reports "Branch rollback: success" despite the branch still having the finalize commit.

### Expected Behavior

- `retry` should return the last non-zero exit code when all attempts fail, and report the correct exit code in retry messages.
- The rollback mechanism should successfully undo finalization changes on protected branches, or clearly report that rollback failed.

### Actual Behavior

- `retry` returns 0 after exhausting all attempts.
- Rollback is silently blocked by rulesets; the finalize commit `10e2ff3` remains on `origin/release/0.3.2`.

### Environment

- **OS**: ubuntu-22.04 (GitHub Actions runner)
- **Shell**: bash
- **Files**: `.github/actions/setup-env/action.yml` (retry helper), `.github/workflows/release.yml` (rollback job)
- **Branch protection**: Repository rulesets on `release/*` branches prevent force-push

### Additional Context

Discovered via [release run #24088003035](https://github.com/vig-os/devcontainer/actions/runs/24088003035). See #499 for the auto-created incident report.

**`retry` bug detail:** the function uses:
```bash
if "$@"; then
  return 0
fi
rc=$?
```
`$?` after `if ... fi` is always 0 (exit status of `fi`). Fix: `"$@" && return 0; rc=$?`.

### Possible Solution

**retry fix:** replace `if "$@"; then return 0; fi; rc=$?` with `"$@" && return 0; rc=$?`.

**Rollback fix — options to evaluate:**
1. Create a revert commit via the API instead of force-pushing (compatible with branch protection).
2. Grant the release GitHub App a ruleset bypass for force-push.
3. Move the tag-existence check before the finalize commit (fail earlier, nothing to rollback).

### TO-DO (manual cleanup for the current release)

- [ ] Revert commit `10e2ff3be1e1e123f720e68a8fe2536d8ee0e58e` from `release/0.3.2` (the orphaned finalize commit left by the failed rollback)
- [ ] Delete stale tag `0.3.2` if it still exists on the remote (it pointed to `059bde7` from a prior attempt) — appears already cleaned up, verify
- [ ] Re-run the release workflow after fixes are applied

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
