---
type: issue
state: closed
created: 2026-04-07T11:27:26Z
updated: 2026-04-07T14:47:30Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/496
comments: 0
labels: feature, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-08T04:42:43.133Z
---

# [Issue 496]: [[FEATURE] Add release tag link to CHANGELOG heading during finalize-release](https://github.com/vig-os/devcontainer/issues/496)

### Description

The `finalize_release_date` function in `prepare_changelog.py` currently replaces `## [X.Y.Z] - TBD` with `## [X.Y.Z] - YYYY-MM-DD`, but does not add a link to the GitHub Release tag. The link has been added manually in separate post-release commits for every past release (e.g. `7acaab4` for 0.3.1, `0217d7d` for 0.3.0).

### Problem Statement

Every release requires a manual follow-up commit to transform `## [X.Y.Z] - DATE` into `## [X.Y.Z](https://github.com/vig-os/devcontainer/releases/tag/X.Y.Z) - DATE`. This is easy to forget and adds unnecessary toil.

### Proposed Solution

Update `finalize_release_date()` in `packages/vig-utils/src/vig_utils/prepare_changelog.py` to produce the replacement string with the release tag URL:

```python
replacement = f"## [{version}](https://github.com/{repo}/releases/tag/{version}) - {release_date}"
```

The repo URL should be derived from a parameter or environment variable (e.g. `GITHUB_REPOSITORY`) rather than hardcoded, so the same tool works for downstream workspaces.

### Alternatives Considered

- Add the link in a separate post-finalize step in `release.yml` using `sed`. This keeps `prepare_changelog.py` simpler but scatters changelog logic across shell and Python.
- Add the link during `promote-release`. The tag exists by then, but it delays the link until after the release is already published as draft.

### Impact

- No breaking change. The only difference is the heading format in CHANGELOG.md gaining a link.
- Benefits every release going forward by eliminating a manual step.
- The downstream workspace `prepare_changelog` would also benefit if the same change is applied to the workspace template.

### Changelog Category

Changed

### Acceptance Criteria

- [ ] `finalize_release_date()` produces headings with the release tag URL
- [ ] Repo URL is configurable (not hardcoded)
- [ ] Existing tests updated; new tests cover the link format
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
