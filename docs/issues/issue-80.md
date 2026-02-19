---
type: issue
state: open
created: 2026-02-18T13:33:30Z
updated: 2026-02-18T16:30:55Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/80
comments: 1
labels: feature, priority:high, area:workflow, effort:small, semver:patch
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T00:08:07.534Z
---

# [Issue 80]: [[TASK] Reconcile issue template labels with repository labels](https://github.com/vig-os/devcontainer/issues/80)

### Description

The issue templates in `.github/ISSUE_TEMPLATE/` reference labels that either don't exist in the repository or conflict with the existing label names. This mismatch will cause issues when templates are used — GitHub silently drops labels that don't exist, so new issues won't be labelled correctly.

As noted by @c-vigo in [PR #68 comment](https://github.com/vig-os/devcontainer/pull/68#issuecomment-3920267853):

> There is a clash between the template labels in `.github/ISSUE_TEMPLATE` and the [default labels](https://github.com/organizations/vig-os/settings/repository-defaults) (which only apply to new repos, existing ones must be edited manually). The clash will only become visible when these changes are merged into `main`.

**Current mismatches:**

| Template | Label in template | Repo label exists? | Notes |
|---|---|---|---|
| `feature_request.yml` | `enhancement` | No (`feature` exists) | Name mismatch |
| `ci_build.yml` | `ci` | No | Missing |
| `refactor.yml` | `refactor` | No | Missing |
| `task.yml` | `task` | No | Missing |
| `documentation.yml` | `docs` | No (`documentation` exists) | Name mismatch |
| `bug_report.yml` | `bug` | Yes | OK |

### Acceptance Criteria

- [ ] Decide on canonical label names (align templates to repo, or repo to templates)
- [ ] Create missing labels in the repository (or update templates to match existing labels)
- [ ] Verify all issue templates reference labels that exist in the repo
- [ ] Consider adding a label provisioning script or documenting the required labels for new repos

### Implementation Notes

Two approaches:
1. **Update the repo labels** to match the templates — create `ci`, `refactor`, `task` labels and rename `feature` → `enhancement`, `documentation` → `docs`.
2. **Update the templates** to match existing repo labels — change `enhancement` → `feature`, `docs` → `documentation` in template files, and create the remaining missing labels.

A provisioning script (`create-gh-issue-labels.sh`) could also be added so that any new repo gets the expected label set automatically.

### Related Issues

Related to #68 (PR where the clash was identified), #67, #63, #61

### Priority

Medium

### Changelog Category

No changelog needed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 02:39 PM_

## Implementation Plan

Issue: #80
Branch: `feature/80-reconcile-template-labels`

### Tasks

- [x] Task 1: Create `.github/label-taxonomy.toml` — single source of truth for 7 canonical labels (name, description, color)
- [x] Task 2: Update repo labels via `gh` CLI — delete stale labels (`documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`), create/update canonical labels from taxonomy
- [x] Task 3: Rename and consolidate issue templates — `bug_report.yml` → `bug.yml`, `feature_request.yml` → `feature.yml` (fix `enhancement` → `feature`), `documentation.yml` → `docs.yml`, merge `ci_build.yml` + `task.yml` into `chore.yml`, keep `refactor.yml`
- [x] Task 4: Update `create-issue.md` command — new label mappings + reference to `.github/label-taxonomy.toml`
- [x] Task 5: Create `scripts/setup-labels.sh` — reads `.github/label-taxonomy.toml`, idempotent create/update, optional `--prune` to delete unlisted labels
- [x] Task 6: Add `.github/label-taxonomy.toml` to sync manifest — `scripts/sync_manifest.py`
- [x] Task 7: Run `just sync-workspace` — verified source and workspace templates match
- [x] Task 8: Commit

