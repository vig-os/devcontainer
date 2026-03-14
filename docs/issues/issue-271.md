---
type: issue
state: closed
created: 2026-03-12T12:17:38Z
updated: 2026-03-12T12:49:02Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/271
comments: 0
labels: bug, priority:high, area:ci, area:docs, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:58.248Z
---

# [Issue 271]: [[BUG] generate-docs selects unreleased changelog version and fails release branch CI](https://github.com/vig-os/devcontainer/issues/271)

## Description
The release branch CI fails in `Project Checks` because the `generate-docs` pre-commit hook modifies `README.md` during CI.

The generated \"Latest Version\" line is changed from the last released tag (`0.2.1 - 2026-01-28`) to an unreleased entry (`0.3.0 - TBD`), which causes a dirty diff and fails the job.

## Steps to Reproduce
1. Run prepare-release workflow for `release/0.3.0`.
2. Run `pre-commit run --all-files` (or let CI run `Project Checks`).
3. Observe `generate-docs` modifies `README.md` with:
   - `- **Latest Version**: [0.3.0](...) - TBD`
4. CI exits non-zero due to hook-modified files.

## Expected Behavior
`generate-docs` should resolve \"Latest Version\" from the latest **released** changelog entry (with a real date), not from unreleased/TBD entries.

## Actual Behavior
`docs/generate.py` reads the first `## [x.y.z]` heading in `CHANGELOG.md`, which can point to a TBD/unreleased version and produce unstable generated docs in release CI.

## Environment
- **OS**: GitHub Actions `ubuntu-latest`
- **Container Runtime**: N/A (workflow execution context)
- **Image Version/Tag**: release branch `release/0.3.0`
- **Architecture**: AMD64
- **Workflow Run**: https://github.com/vig-os/devcontainer/actions/runs/23001181161
- **Failing Job**: https://github.com/vig-os/devcontainer/actions/runs/23001181161/job/66785817335?pr=270

## Additional Context
- Failure occurs at pre-commit hook `generate-docs` in `Project Checks`.
- CI shows hook-generated diff in `README.md` for the latest-version line.
- Related code: `docs/generate.py` function `get_version_from_changelog()`.

### Acceptance Criteria
- [ ] `get_version_from_changelog()` returns the latest version that has a real release date (not `TBD`)
- [ ] Generated docs are stable across local and CI runs on release branches
- [ ] `pre-commit run --all-files` passes without modifying docs after prepare-release
- [ ] Add regression test covering changelog parsing for released vs unreleased/TBD entries
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Possible Solution
Update `docs/generate.py` (`get_version_from_changelog`) to parse changelog entries and choose the latest version whose heading includes a concrete date, excluding `TBD`/unreleased entries.

## Changelog Category
Fixed
