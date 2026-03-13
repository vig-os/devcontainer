---
type: issue
state: closed
created: 2026-02-21T17:50:57Z
updated: 2026-02-24T15:26:51Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/138
comments: 5
labels: bug, priority:blocking, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:58.234Z
---

# [Issue 138]: [[BUG] CodeQL CI fails on all PRs due to conflicting default setup and advanced workflow](https://github.com/vig-os/devcontainer/issues/138)

## Description

CodeQL Analysis (python) was failing on every PR that touches Python files. The SARIF upload was rejected with:

> `Code Scanning could not process the submitted SARIF file: CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled`

The repo had both GitHub's **default CodeQL setup** (enabled in repo settings) and a custom **advanced workflow** (`.github/workflows/codeql.yml`) active simultaneously. GitHub rejects SARIF uploads from the advanced workflow when the default setup is also enabled.

## Steps to Reproduce

1. Open any PR that includes Python file changes (e.g. #136, #131, #129)
2. Wait for CI to complete
3. Observe `CodeQL Analysis (python)` check fails

## Expected Behavior

CodeQL Analysis passes without configuration conflicts.

## Actual Behavior

The analysis itself completes successfully, but the SARIF upload fails:
`Code Scanning could not process the submitted SARIF file: CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled`

## Environment

- GitHub Actions hosted runner
- CodeQL Action v4.32.2
- `.github/workflows/codeql.yml` (advanced config) + repo default setup both active

## Additional Context

Affected PRs: #136, #131, #129 (all open PRs with Python changes). PR #135 was unaffected (no Python files changed).

**Fix applied:** Disabled the default CodeQL setup via the API:
```bash
gh api repos/vig-os/devcontainer/code-scanning/default-setup -X PATCH -f state="not-configured"
```

**Verified:** Re-ran the failed CodeQL job on PR #136 — it now passes with conclusion `success`.

## Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on February 21, 2026 at 05:54 PM_

Is this fixed now?

---

# [Comment #2]() by [gerchowl]()

_Posted on February 21, 2026 at 05:55 PM_

## Verified — Fix confirmed

Re-ran the failed CodeQL jobs on all 3 affected PRs after disabling the default setup. Results:

| PR | CodeQL Analysis (python) |
|----|--------------------------|
| #136 | :white_check_mark: success |
| #131 | :white_check_mark: success |
| #129 | :white_check_mark: success |

The conflict between default setup and the advanced workflow (`.github/workflows/codeql.yml`) was the sole cause. No code changes were needed — only the repo-level setting was toggled via:

```bash
gh api repos/vig-os/devcontainer/code-scanning/default-setup -X PATCH -f state="not-configured"
```

All open PRs are now unblocked. Closing this issue.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 24, 2026 at 01:13 PM_

@c-vigo Did you revert this? The default CodeQL setup is back to `configured` (re-enabled today at 12:26 UTC):

```bash
gh api repos/vig-os/devcontainer/code-scanning/default-setup
# → {"state": "configured", "languages": ["actions", "python"], "query_suite": "default", "updated_at": "2026-02-24T12:26:26Z"}
```

This conflicts with the advanced workflow in `.github/workflows/codeql.yml` — same issue as before. All PRs with Python changes are failing CodeQL again (e.g. PR #164).

The fix was:
```bash
gh api repos/vig-os/devcontainer/code-scanning/default-setup -X PATCH -f state="not-configured"
```

---

# [Comment #4]() by [c-vigo]()

_Posted on February 24, 2026 at 01:16 PM_

I did, but then I set it back to `No configuration`.
I used the web interface [here](https://github.com/organizations/vig-os/settings/security_products)

---

# [Comment #5]() by [gerchowl]()

_Posted on February 24, 2026 at 03:26 PM_

Took default conf of gh and allowed for custom codeQL in repos.
Then had to disable default codeQL in 'devcontainer' repo via gh API because the website would always want to commit a new boilerplate 'codeql.yml' which was less specific then ours.

