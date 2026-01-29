---
type: issue
state: open
created: 2026-01-29T09:44:01Z
updated: 2026-01-29T09:44:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/37
comments: 0
labels: enhancement
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-29T09:44:19.875Z
---

# [Issue 37]: [[FEATURE] Automate and Standardize Repository Setup for Devcontainer Template](https://github.com/vig-os/devcontainer/issues/37)

### Description

Create a fully automated and standardized repository setup.
This setup will serve as a reproducible starting point for all projects (software, QMS, others),
enforcing best practices for medical-device compliance, code quality, and security.


### Problem Statement

Currently, each repository setup is manual, inconsistent, and may lack compliance and security best practices.
This leads to:

- Inconsistent commit and branch practices
- Poor traceability and audit-readiness
- Risk of non-compliance with IEC 62304 / ISO 13485 for QMS projects
- Security exposure from unpinned actions or unreviewed workflows
- Inconsistent code quality, CI/CD, and release processes

We need a fully automated, reproducible repository template that embeds these standards,
so all projects start compliant and maintainable from day one.

### Proposed Solution

Automatically configure new repositories with:

1. **Commit Message Standardization** #36 
   - Conventional Commits–based, restricted types
   - Mandatory references to issues, requirements, risks, or SOPs
   - Git commit template included
   - Cursor integration instructions
   - Local commit-msg hook
   - CI validation

2. **Branching Strategy & Enforcement**
   - Standard branches: `main`, `develop`, `release/*`, `hotfix/*`, `feature/*`, `bugfix/*`
   - Branch protection rules programmatically applied
   - Require signed commits
   - Require PR reviews
   - Enforce naming conventions via CI

3. **Release Cycle**
   - Automated release branch creation templates
   - Recommended tagging conventions
   - Integration with QMS baselining for audits

4. **Default GitHub Actions / CI**
   - Commit message enforcement
   - Tests / linting
   - Branch naming enforcement
   - Code coverage
   - Optional: semantic version checks
   - Automatically pinned actions to specific SHA commits

5. **Security Considerations**
   - Pin all GitHub Actions to commit SHAs
   - Require review/approval for workflows submitted by external contributors
   - Enforce branch protection for critical branches
   - Optional: dependabot for dependencies

6. **Code Quality & Other Useful Features**
   - Linters and formatters (ruff, black, clang-format, etc.)
   - Optional pre-commit hooks for code style
   - PR templates for traceability (linking to requirements/issues)
   - Default issue templates for features, bugs, and QMS artifacts
   - Optional GitHub discussion or projects enabled

The goal is that any new repository created from this devcontainer template
**installs itself and is audit-ready** with all enforced best practices.


### Alternatives Considered

- Manual repository setup per project → inconsistent, error-prone, not auditable  
- Individual tooling setup for each project → high maintenance overhead  
- Using separate templates for software vs QMS → complicates maintenance and consistency  


### Additional Context

- This is intended as the **base template** for all new projects.  
- Sub-issues will be created for each component (commit standard, branch enforcement, CI, security, release cycle, etc.)  
- Links / references for best practices: IEC 62304, ISO 13485, GitHub security guidelines, GitHub Actions best practices


### Impact

- **Beneficiaries:** All developers, QA, RA, auditors  
- **Compatibility:** Backward-compatible with existing projects; all future repos standardized  
- **Risks:** Minor; mostly tool adoption and learning curve for developers  
- **Compliance:** Aligns repository setup with medical device QMS and software configuration requirements
