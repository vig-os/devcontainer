---
type: issue
state: open
created: 2026-02-11T13:58:47Z
updated: 2026-02-11T13:58:47Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/50
comments: 0
labels: feature
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-11T13:59:09.769Z
---

# [Issue 50]: [[FEATURE] Harden CI/CD Security: SHA Pinning, Dependabot, and Security Policies](https://github.com/vig-os/devcontainer/issues/50)

### Description

Parent: #37 (Point 5 — Security Considerations)

Harden the repository's CI/CD supply chain and establish security policies.
This covers GitHub Actions SHA pinning, automated dependency updates, vulnerability disclosure,
code ownership enforcement, and CI-level guardrails to prevent regressions.

### Problem Statement

Currently, all 38 external GitHub Action references across 10 workflow and composite action files
use mutable version tags (e.g. `@v4`, `@v3.12.0`). This exposes the CI/CD pipeline to supply-chain
attacks — a compromised or force-pushed tag could inject malicious code into every workflow run.

Additionally:

- No Dependabot configuration exists, so dependency updates are entirely manual
- No `SECURITY.md` documents how to report vulnerabilities
- No `CODEOWNERS` enforces review requirements on critical paths (workflows, scripts)
- No automated check prevents future PRs from introducing unpinned action references

These gaps are inconsistent with IEC 62304 configuration management requirements and
GitHub's own security hardening guidelines for Actions.

### Proposed Solution

1. **Pin all GitHub Actions to commit SHAs**
   - Replace every external `uses:` tag reference with its full 40-character commit SHA
   - Preserve the original tag as a trailing comment for readability (e.g. `actions/checkout@<sha> # v4`)
   - Covers 18 unique actions across 5 workflows and 5 composite actions

2. **Add Dependabot configuration**
   - Create `.github/dependabot.yml` covering: `github-actions`, `pip`, `docker`, `npm`
   - Weekly schedule, targeting the `dev` branch
   - Group minor/patch updates to reduce PR noise

3. **Create SECURITY.md**
   - Supported versions table
   - Vulnerability reporting instructions (private disclosure, not public issues)
   - Response timeline expectations
   - Scope of security concerns (supply chain, container image, workflow permissions)

4. **Add CODEOWNERS**
   - Default ownership for all files
   - Stricter ownership for `.github/workflows/`, `.github/actions/`, and `scripts/`

5. **Add CI enforcement for SHA pinning**
   - Script to scan workflow files for unpinned external action references
   - Integrate into CI (`project-checks` job) and pre-commit hooks
   - Prevents regressions after initial pinning

### Alternatives Considered

- **Pin only critical actions (checkout, token generation):** Reduces effort but leaves supply-chain gaps; inconsistent with best practices for regulated environments.
- **Use a third-party tool like StepSecurity Harden-Runner:** Adds runtime protection but introduces another external dependency; SHA pinning is the foundational layer regardless.
- **Skip Dependabot, rely on manual updates:** Higher maintenance burden; SHA pins become stale without automated update PRs.

### Additional Context

- Branch protection is enforced via GitHub Enterprise (out of scope for this issue)
- No `pull_request_target` triggers exist in current workflows (good baseline)
- Workflow permissions are already reasonably scoped (CI is read-only)
- References: [GitHub Security Hardening for Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions), IEC 62304 Section 8 (Software Configuration Management)

### Impact

- **Beneficiaries:** All developers, QA, RA, auditors — immutable CI/CD traceability
- **Compatibility:** Fully backward-compatible; no functional changes to workflows
- **Risks:** Minimal; Dependabot will create update PRs that need periodic review
- **Compliance:** Addresses IEC 62304 configuration management and traceability requirements for build tooling
