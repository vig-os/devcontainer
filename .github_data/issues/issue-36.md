---
type: issue
state: open
created: 2026-01-29T09:18:36Z
updated: 2026-01-29T09:18:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/36
comments: 0
labels: enhancement
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-29T09:18:55.090Z
---

# [Issue 36]: [[FEATURE] Standardize and Enforce Commit Message Format](https://github.com/vig-os/devcontainer/issues/36)

### Description

Introduce a standardized commit message format across to ensure consistency, traceability, and compliance with QMS requirements.
This includes defining a commit message convention, configuring tooling (Cursor + Git), and enforcing the standard locally and in CI.

### Problem Statement

Currently, commit messages are free-form and inconsistently structured. This creates several problems:

- Reduced traceability between changes, requirements, risks, and issues
- Increased review effort due to unclear commit intent
- Difficulty demonstrating controlled change management during audits
- Risk of non-compliance with IEC 62304 / ISO 13485 expectations regarding software configuration management and change control

Commit messages are a critical part of any audit trail and must be standardized and enforceable.

### Proposed Solution

Adopt and enforce a restricted Conventional Commits–based standard with mandatory traceability references.

The solution includes:

- Define a commit message standard
  - Format:
  ``` ini
   type(scope): short description
   Refs: <IDs>
   ```
   - Limited, approved commit types
   - Mandatory references to issues, requirements, risks, or SOPs
- Document the standard
   - Add a document describing rules and examples
- Tooling support
    - Git commit message template (.gitmessage)
    - Cursor Source Control configuration to auto-generate compliant messages
- Enforcement
    - Local commit-msg git hook
    - CI validation on pull requests
- Governance
   - Squash-merge PRs so the final commit message becomes the approved change record

This ensures every change is human-readable, machine-checkable, and audit-ready

### Alternatives Considered

- Free-form commit messages + PR descriptions: Rejected due to inconsistent enforcement and weak traceability.
- Relying solely on PR titles: Insufficient, as commits are the atomic change units referenced during audits and investigations.
- Per-developer guidelines without enforcement: Rejected; process must be enforceable and reproducible.
- Using emojis or semantic-release–style commits: Rejected as inappropriate for regulated environments.

### Additional Context

- Commit messages are treated as quality records.
- Cursor’s AI-generated commit messages are helpful but must be constrained to avoid non-compliant output.
- This issue supports future work on:
   - automated traceability reports
   - release baselining
   - audit evidence extraction
- Related standards:
  - IEC 62304 — Software configuration and change management
  - ISO 13485 — Documented procedures and records
  - FDA design control expectations (change traceability)

### Impact

### Beneficiaries

- Developers (clear expectations, less review friction)
- QA / RA (clean audit trail, easier evidence extraction)
- Auditors (clear, consistent change rationale)

### Compatibility

- Backward compatible with existing Git history
- New enforcement applies only to future commits

### Risk

- Minimal implementation risk
- High positive impact on compliance and maintainability
