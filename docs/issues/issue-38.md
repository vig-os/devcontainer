---
type: issue
state: closed
created: 2026-01-30T10:29:19Z
updated: 2026-02-03T10:04:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/38
comments: 1
labels: feature
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:37.668Z
---

# [Issue 38]: [[FEATURE] Standardize Branching Strategy and Enforcement](https://github.com/vig-os/devcontainer/issues/38)

### Description

Introduce a standardized branching strategy and enforcement across repositories created from this template. This includes defining standard branch names, applying branch protection rules programmatically, requiring signed commits and PR reviews, and enforcing naming conventions via CI.

Parent: #37

### Problem Statement

Without a defined branching strategy and enforcement:

- Branch names and workflows vary by developer or project, reducing traceability
- Critical branches (e.g. `main`, `develop`) may lack protection, increasing risk of direct pushes or unreviewed changes
- Unsigned commits and unreviewed PRs weaken audit trails and compliance with change control expectations (e.g. IEC 62304, ISO 13485)
- Inconsistent branch naming makes automation, reporting, and baselining harder

We need a reproducible, template-driven setup so every new repository gets the same branching rules and safeguards from day one.

### Proposed Solution

- **Standard branches:** `main`, `develop`, and convention-based topic branches: `release/*`, `hotfix/*`, `feature/*`, `bugfix/*` (and optionally `docs/*`, `test/*`, `refactor/*` as already used in this repo).
- **Branch protection rules:** Applied programmatically (e.g. via GitHub API, Terraform, or repo configuration) for `main` and `develop`: require PR reviews, block force-push/delete, optional status checks.
- **Signed commits:** Require signed commits (e.g. GPG or S/MIME) for protected branches where feasible.
- **PR reviews:** Require at least one approval before merge on protected branches.
- **Naming enforcement:** Enforce branch naming conventions in CI (e.g. regex or existing rules such as `.cursor/rules/branch-naming.mdc`) and optionally via branch protection or GitHub Actions.

Deliverables can include: documentation of the strategy, scripts or config to apply branch protection, and CI jobs that validate branch names on push or PR.

### Alternatives Considered

- Relying only on documentation: insufficient without enforcement.
- Manual setup per repository: error-prone and inconsistent.
- Third-party tools only: adds dependency; prefer native GitHub features plus minimal CI where needed.

### Additional Context

- Aligns with commit message standardization (#36) and the broader repo setup automation (#37).
- Branch naming conventions are already partially defined in this repo (e.g. branch-naming rule); this issue extends to enforcement and protection.
- Related: release cycle (#37 point 3), default GitHub Actions (#37 point 4), security (#37 point 5).

### Impact

- **Beneficiaries:** Developers (clear workflow), QA/RA (audit trail, change control), auditors (consistent branching and protection).
- **Compatibility:** Backward compatible; new rules apply to repos created or updated from the template.
- **Risks:** Low; mainly adoption of signed commits and branch protection in existing repos that adopt the template.

---

# [Comment #1]() by [c-vigo]()

_Posted on January 30, 2026 at 02:59 PM_

### Organization Rules

Using GitHub Enterprise, we set rules across all repositories for any organization within the Enterprise.
Currently:

- **Main Branch Protection**
  - Protection against force push and deletion
  - PR merging only, with at least one reviewer and review resolution required
- **Dev Branch Protection**:
  - Protection against force push and deletion
  - PR merging only, with review resolution required
- **Signed Commits**: commits in any branch must be signed

