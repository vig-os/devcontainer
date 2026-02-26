---
type: issue
state: open
created: 2026-02-24T15:47:43Z
updated: 2026-02-24T15:49:15Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/183
comments: 0
labels: bug, area:workflow, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:52.659Z
---

# [Issue 183]: [[BUG] worktree-start swallows derive-branch-summary error messages](https://github.com/vig-os/devcontainer/issues/183)

## Description

When `derive-branch-summary.sh` fails (e.g. `agent --print` times out), the error message is silently swallowed by `worktree-start`. The user sees only:

```
[*] No linked branch for issue #178. Creating one...
error: Recipe `worktree-start` failed with exit code 1
```

No indication of *what* failed or *why*.

## Steps to Reproduce

1. Run `just wt-start <issue>` for an issue with no linked branch
2. Wait for `agent --print` to time out (or have it fail for any reason)
3. Observe that no error details are shown

## Expected Behavior

The error message from `derive-branch-summary.sh` should be visible to the user. On first failure, the script should retry with a higher-tier model before giving up, e.g.:

```
[*] No linked branch for issue #178. Creating one...
[!] Lightweight model failed. Retrying with standard model...
[OK] Branch summary: idle-worktree-status
```

Or, if both fail:

```
[*] No linked branch for issue #178. Creating one...
[!] Lightweight model failed. Retrying with standard model...
[ERROR] Failed to derive branch summary from title: ...
        Create one manually: gh issue develop <ISSUE> --base dev --name <type>/<issue>-<summary>
```

## Actual Behavior

The `2>/dev/null` on the first invocation (line 148 of `justfile.worktree`) suppresses stderr, hiding the script's error output. The retry on line 151 redirects stdout to `/dev/null` and also swallows the exit code with `|| true`, producing no useful output either. There is no fallback to a higher-tier model.

## Environment

- macOS 24.5.0
- Cursor agent CLI
- justfile.worktree (introduced in #154 / PR #165)

## Additional Context

Regression introduced by fix(worktree): add agent timeout and gh preflight to worktree-start (#154). The fix correctly added a timeout but the error-handling wiring in the justfile suppresses the diagnostics.

Model tiers are defined in `.cursor/agent-models.toml`. The fallback chain should be: `lightweight` -> `standard` (one level up). No further escalation to `autonomous` — that tier is too expensive for a single branch name.

## Possible Solution

### In `derive-branch-summary.sh`:
1. Accept an optional `MODEL` parameter (or env var `BRANCH_SUMMARY_MODEL`) instead of always reading the `lightweight` tier
2. On timeout/failure, the calling code retries with the next tier

### In `justfile.worktree`:
1. Remove `2>/dev/null` from the first invocation so stderr reaches the user
2. Replace the broken retry logic with: try `lightweight` model, on failure try `standard` model, on second failure print error and exit
3. Read both model values from `.cursor/agent-models.toml`

## Acceptance Criteria

- [ ] When `derive-branch-summary.sh` fails with the lightweight model, it retries with the standard model
- [ ] Error messages from `derive-branch-summary.sh` are visible in terminal output
- [ ] The manual workaround hint (`gh issue develop ...`) is printed if both attempts fail
- [ ] Existing BATS tests still pass; new test covers the retry path
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Fixed
