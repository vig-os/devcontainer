---
type: issue
state: closed
created: 2026-03-12T12:18:38Z
updated: 2026-03-12T13:15:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/272
comments: 0
labels: bug, priority:blocking, area:testing, security
assignees: none
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:58.019Z
---

# [Issue 272]: [[BUG] Fix high-severity CodeQL URL sanitization alerts in integration tests](https://github.com/vig-os/devcontainer/issues/272)

## Description
The CodeQL check run for PR #270 (`check_run_id=66785943362`) failed with **3 new high-severity** alerts:
- **Incomplete URL substring sanitization** (3 occurrences)

All alerts are reported in `tests/test_integration.py`.

## Steps to Reproduce
1. Open PR checks for `https://github.com/vig-os/devcontainer/pull/270/checks`.
2. Open the failed **CodeQL** run (`check_run_id=66785943362`).
3. Inspect annotations and observe 3 findings titled **Incomplete URL substring sanitization**.
4. See findings on:
   - `tests/test_integration.py` (line ~1200)
   - `tests/test_integration.py` (line ~1214)
   - `tests/test_integration.py` (line ~1468)

## Expected Behavior
CodeQL security analysis passes with no high-severity URL sanitization alerts.

## Actual Behavior
CodeQL reports 3 high-severity alerts and fails the check.

## Environment
- **OS**: GitHub Actions runner (Linux)
- **Container Runtime**: Podman (invoked by integration tests)
- **Image Version/Tag**: PR `#270` head (`release/0.3.0`)
- **Architecture**: x86_64 (CI default)

## Additional Context
- PR: https://github.com/vig-os/devcontainer/pull/270
- Check run: https://github.com/vig-os/devcontainer/runs/66785943362
- Branch alerts query: https://github.com/vig-os/devcontainer/security/code-scanning?query=pr%3A270+tool%3ACodeQL+is%3Aopen

## Possible Solution
Replace substring-based URL trust checks with structured URL parsing and strict host validation (e.g., parse hostname and compare against an allowlist), then update tests accordingly so CodeQL no longer flags the pattern.

## Changelog Category
Security

## Acceptance Criteria
- [x] All 3 CodeQL alerts are resolved for PR #270.
- [x] CodeQL check passes for the branch.
- [x] TDD compliance (see `.cursor/rules/tdd.mdc`)

