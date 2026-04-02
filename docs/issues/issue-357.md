---
type: issue
state: closed
created: 2026-03-18T09:38:48Z
updated: 2026-03-18T21:57:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/357
comments: 0
labels: bug, priority:medium, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-19T04:27:46.487Z
---

# [Issue 357]: [[BUG] Add bounded retry for network-dependent setup and workflow API calls](https://github.com/vig-os/devcontainer/issues/357)

## Description
CI failed in run https://github.com/vig-os/devcontainer/actions/runs/23237386386/attempts/1 during `Project Checks` with `curl: (22) The requested URL returned error: 403`.

The failure happened in environment setup when fetching Taplo release metadata from GitHub API, and the step currently has no bounded retry/backoff. This makes the pipeline flaky for transient upstream/network/API issues.

## Steps to Reproduce
1. Run CI for a PR (e.g. run `23237386386`, attempt `1`).
2. Observe `Project Checks` fail in setup phase.
3. Failing command path is in `.github/actions/setup-env/action.yml` (`Install taplo`).
4. Error: `curl: (22) The requested URL returned error: 403` and step exits with code `22`.

## Expected Behavior
Network/API-dependent setup steps should tolerate transient failures using bounded retry with backoff and only fail after retry budget is exhausted.

## Actual Behavior
A single transient failure in external fetch (`curl`/`gh api`) fails the whole job immediately.

## Environment
- **OS**: GitHub-hosted runner (`ubuntu-22.04`)
- **Container Runtime**: N/A
- **Image Version/Tag**: GitHub-hosted runner image
- **Architecture**: x86_64

## Additional Context
Candidate additional locations where retry would be beneficial:
- `.github/actions/setup-env/action.yml`
  - `Install taplo`: release lookup + binary download (`curl`)
  - `Install hadolint`: binary + checksum download (`curl`)
- `.github/workflows/prepare-release.yml`
  - Multiple `gh api` reads for refs/changelog content without retry
- Keep parity with existing retry patterns already present in `.github/workflows/release.yml`.

- Related to #354 and #355 (same reliability class: transient CI/API failures)
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Possible Solution
Introduce a shared bounded retry helper for shell steps (max attempts + exponential backoff + transient/non-transient error classification), and apply it to high-value network-dependent calls (`curl`, `gh api`) in setup and release-prep paths.

## Changelog Category
Fixed
