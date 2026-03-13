---
type: issue
state: closed
created: 2026-02-20T15:44:14Z
updated: 2026-02-20T16:26:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/123
comments: 1
labels: chore, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-20T16:48:51.776Z
---

# [Issue 123]: [[CHORE] Fix .github/ workflow and configuration issues from review](https://github.com/vig-os/devcontainer/issues/123)

## Chore Type

CI / Build change

## Description

Thorough review of the `.github/` directory identified several issues across workflows, composite actions, and repository settings. No HIGH-severity items — the three MEDIUM items are bugs in workflow files, and the rest are LOW-priority consistency improvements.

## Acceptance Criteria

- [ ] W1: `security-scan.yml` version step outputs `release_date` and `build_timestamp` (currently undefined, passing empty strings to build-image action)
- [ ] W2: `scorecard.yml` codeql-action updated from v3 to v4 SHA (matches all other workflows)
- [ ] W3: `post-release.yml` commit message `Refs:` line has no spurious indentation
- [ ] W4: `ci.yml` uses `$GITHUB_REPOSITORY` instead of hardcoded `vig-os/devcontainer` in release URL
- [ ] W5: `release.yml` rollback issue labels use only labels from `label-taxonomy.toml` (currently uses undeclared `release` label)
- [ ] W6: Verify `ubuntu-22.04-arm` is a valid runner name for GitHub ARM builds in `release.yml`
- [ ] W7: `prepare-release.yml` commit message includes `Refs:` if a tracking issue exists
- [ ] A1: `build-image/action.yml` OCI source label uses dynamic `github.server_url`/`github.repository` instead of hardcoded URL
- [ ] S1: Enable `deleteBranchOnMerge` in repo settings
- [ ] S2: Disable wiki in repo settings
- [ ] S3: Evaluate setting `sha_pinning_required: true` for actions
- [ ] S4: Consider creating a `production` environment with required reviewers for release publish

## Implementation Notes

- W1–W5, W7, A1 are straightforward file edits
- W6 is verification only — confirm runner name or update to `ubuntu-24.04-arm` if needed
- S1–S4 are GitHub repo/org settings, not code changes
- All code changes are in `.github/` — no impact on the container image or tests

## Related Issues

N/A

## Priority

Medium

## Changelog Category

No changelog needed

## Additional Context

N/A
---

# [Comment #1]() by [c-vigo]()

_Posted on February 20, 2026 at 03:45 PM_

## Implementation Plan

### W1: Fix undefined outputs in `security-scan.yml`

Add `release_date` and `build_timestamp` to the version step (lines 46–51), matching the pattern in `ci.yml` lines 68–76:

```yaml
RELEASE_DATE=$(date -u +%Y-%m-%d)
BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "release_date=$RELEASE_DATE" >> $GITHUB_OUTPUT
echo "build_timestamp=$BUILD_TIMESTAMP" >> $GITHUB_OUTPUT
```

### W2: Update `scorecard.yml` codeql-action to v4

Replace line 47:

```
github/codeql-action/upload-sarif@b5ebac6f4c00c8ccddb7cdcd45fdb248329f808a  # v3
```

with:

```
github/codeql-action/upload-sarif@45cbd0c69e560cd9e7cd7f8c32362050c9b7ded2  # v4
```

### W3: Fix `post-release.yml` commit message indentation

Lines 121–126 produce a `Refs:` line with 10 spaces of YAML indentation. Rewrite using a newline escape or heredoc to eliminate whitespace:

```yaml
COMMIT_MSG="chore: sync dev with main after merge"
if [ -n "$PR_NUMBER" ]; then
  COMMIT_MSG="${COMMIT_MSG}

Refs: #${PR_NUMBER}"
fi
```

### W4: Replace hardcoded URL in `ci.yml`

Line 71 — change:

```bash
RELEASE_URL="https://github.com/vig-os/devcontainer/commit/$(git rev-parse HEAD)"
```

to:

```bash
RELEASE_URL="https://github.com/${GITHUB_REPOSITORY}/commit/$(git rev-parse HEAD)"
```

### W5: Fix undeclared label in `release.yml`

Line 854 uses `['bug', 'release']` but `release` is not in `label-taxonomy.toml`. Replace with `['bug', 'area:ci']`.

### W6: Verify ARM runner name in `release.yml`

Line 401 uses `ubuntu-22.04-arm`. Verify this is a valid GitHub-hosted runner name. If not, update to the correct name (e.g., `ubuntu-24.04-arm`).

### W7: Add `Refs:` to `prepare-release.yml` commit

Lines 215–220 — the commit message omits `Refs:`. Since this issue (#123) now exists as a tracking issue, the prepare-release commit template should include `Refs:` when a PR number is available. However, since the prepare-release commit is generated before the PR exists, this may be intentionally omitted. **Verify intent and skip if by design.**

### A1: Replace hardcoded source URL in `build-image/action.yml`

Line 121 — change:

```yaml
org.opencontainers.image.source=https://github.com/vig-os/devcontainer
```

to:

```yaml
org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
```

### S1–S4: Repository settings (manual)

- **S1:** `gh api repos/vig-os/devcontainer -X PATCH -F delete_branch_on_merge=true`
- **S2:** `gh api repos/vig-os/devcontainer -X PATCH -F has_wiki=false`
- **S3:** Evaluate `sha_pinning_required` at org level — may require org admin
- **S4:** Evaluate `production` environment with required reviewers — deferred unless release process warrants it

