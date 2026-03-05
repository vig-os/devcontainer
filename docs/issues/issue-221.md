---
type: issue
state: open
created: 2026-03-04T20:06:26Z
updated: 2026-03-04T20:06:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/221
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-05T04:18:18.005Z
---

# [Issue 221]: [[BUG] PR fingerprint check falsely flags ".cursor" file paths in PR body](https://github.com/vig-os/devcontainer/issues/221)

### Description

The `PR Title Check` workflow fails when a PR body includes file paths containing `.cursor/`, even when there is no AI identity disclosure in the message itself.

Current behavior blocks valid PRs that reference repository paths, for example:
- `.cursor/rules/changelog.mdc`
- `assets/workspace/.cursor/rules/changelog.mdc`

### Steps to Reproduce

1. Open or edit a PR body to include a file path containing `.cursor/`.
2. Trigger `PR Title Check` (e.g., edit PR description or push a commit).
3. Observe failure in step `Check PR for agent fingerprints`.

Example failing run:
- https://github.com/vig-os/devcontainer/actions/runs/22684595448/job/65764006478?pr=220

### Expected Behavior

The fingerprint check should detect actual agent identity disclosures (e.g., `Co-authored-by`, agent emails, explicit identity phrases), but should **not** fail on legitimate repository paths like `.cursor/...`.

### Actual Behavior

The check fails with:
`PR title or body contains blocked AI agent fingerprint: 'cursor'. Remove agent identity from the PR.`

### Environment

- GitHub Actions workflow: `PR Title Check`
- Script: `scripts/check-pr-agent-fingerprints.py`
- Blocklist source: `.github/agent-blocklist.toml`

### Additional Context

Likely related to broad substring matching in `names = [\"cursor\", ...]` against full PR body text.
Suggested fix direction:
- use token-aware or context-aware matching
- ignore fenced code / file paths / dot-prefixed directory names
- keep strict matching for trailers/emails and explicit identity phrases

Related to #163.

### Possible Solution

Narrow the matching logic so `cursor` is not matched inside technical path tokens such as `.cursor/`.
For example:
- keep strict regex checks for trailers/emails
- for name checks, require word boundaries and/or contextual phrases indicating identity
- add regression tests covering `.cursor/...` path references in PR title/body

### Changelog Category

Fixed

- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
