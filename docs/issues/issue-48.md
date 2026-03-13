---
type: issue
state: closed
created: 2026-02-06T15:54:31Z
updated: 2026-02-11T13:49:10Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/48
comments: 0
labels: feature
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:36.015Z
---

# [Issue 48]: [[FEATURE] Implement Automated Release Cycle with QMS Baseline Integration](https://github.com/vig-os/devcontainer/issues/48)

## Description

Implement a structured, auditable release cycle with automated release branch creation, semantic versioning enforcement, and QMS baseline documentation generation following IEC 62304 configuration management requirements.

## Problem Statement

Currently, the release process has several gaps:

1. **No formal release branch workflow** - Releases are created by manually pushing tags from `dev` branch
2. **Manual CHANGELOG finalization** - No automation to move Unreleased entries to versioned sections
3. **No QMS baseline documentation** - Missing configuration management documentation required for IEC 62304 audits
4. **Limited release testing** - No pre-release validation workflow before production deployment
5. **Broken tooling** - `just push` command references deleted `scripts/push.sh`
6. **Missing traceability artifacts** - No structured baseline reports linking issues → commits → tests → releases

This creates risks for:
- **Audit compliance**: Insufficient configuration management documentation
- **Quality**: Inadequate testing before production releases
- **Traceability**: Difficulty reconstructing what changed and why for specific releases
- **Consistency**: Manual processes lead to variations between releases

## Proposed Solution

Implement a comprehensive release management system based on Git Flow principles adapted for medical device software compliance.

### 1. Release Branch Workflow

**Minor/Major Releases** (e.g., 0.3.0, 1.0.0):
```
dev → release/X.Y.Z → main (tagged vX.Y.Z) → CI/CD publish → merge back to dev
```

**Patch Releases/Hotfixes** (e.g., 0.2.2):
```
main → hotfix/X.Y.Z → main (tagged vX.Y.Z) → CI/CD publish → merge back to dev
```

### 2. Automation Scripts

**`scripts/create-release.sh`**
- Creates release branch from `dev`
- Validates semantic version format
- Finalizes CHANGELOG (moves Unreleased → version section with date)
- Updates version references in documentation templates
- Generates QMS baseline documentation
- Creates standardized commit and draft PR to `main`

**`scripts/generate-baseline.sh`**
- Generates IEC 62304-compliant baseline documentation
- **Format considerations**:
  - Consider using Typst format (`.typ`) instead of Markdown for richer formatting, better PDF generation, and professional QMS documentation
  - Generate machine-readable exports (JSON/YAML) for QMS system integration
  - Outputs:
    - `docs/baselines/baseline-vX.Y.Z.typ` or `.md` (human-readable)
    - `docs/baselines/baseline-vX.Y.Z.json` (machine-readable for QMS import)
    - PDF generation via Typst if adopted
- Includes:
  - Configuration identification (version, git tag, SHA)
  - Change control (all commits with issue references since last release)
  - Status accounting (complete change history)
  - Test results summary
  - Configuration items inventory (all tool versions, dependencies)
  - Known defects/anomalies evaluation
  - Traceability matrix (issues → commits → tests)
- **QMS Integration**: All documentation created as importable assets for organization-wide QMS repository

**`scripts/finalize-release.sh`**
- Merges release PR to `main`
- Creates annotated git tag `vX.Y.Z`
- Waits for and verifies CI/CD completion
- Merges back to `dev`
- Deletes release branch
- Creates GitHub release with CHANGELOG notes

### 3. Just Recipe Updates

Replace broken `just push` with:
```just
create-release version    # Create and prepare release branch
finalize-release version  # Complete release (merge, tag, publish)
test-release version      # Test release build without publishing
```

### 4. Testing Strategy

**Pre-Release Testing:**
- Local validation: `just test` passes on release branch
- CI dry-run: Use GitHub workflow dispatch with `publish=false`
- Multi-architecture verification
- Integration testing with install script

**Release Validation:**
- Post-publish manifest verification
- Smoke test (pull and run published image)
- Documentation version consistency check

### 5. Documentation Updates

- **CONTRIBUTE.md**: Update "Release Workflow" section with new process
- **docs/RELEASE_PROCESS.md**: Create detailed release runbook with step-by-step checklist
- **CHANGELOG.md**: Add release management guidelines in header

## QMS/IEC 62304 Compliance

The proposed solution addresses IEC 62304 Section 5.8 (Software Release) requirements:

**Configuration Identification** (IEC 62304 5.1.1):
- Git tags provide unique version identification
- Baseline documents capture complete configuration at release

**Change Control** (IEC 62304 5.1.3):
- All changes traceable via commit messages referencing issues
- Release branch workflow enforces review before `main` merge
- Automated baseline generation ensures no changes are undocumented

**Configuration Status Accounting** (IEC 62304 5.1.4):
- Baseline documents provide complete change history
- CHANGELOG maintains human-readable change summary
- Traceability matrix links requirements (issues) to implementation (commits) to verification (tests)

**Release Documentation** (IEC 62304 5.8):
- Baseline document archives released version and creation method
- All verification activities completion tracked
- Residual anomalies documented and evaluated

## Alternatives Considered

1. **Semantic Release Bot** - Fully automated but lacks medical device compliance documentation
2. **Manual Process Documentation Only** - Cheaper but error-prone, not scalable
3. **Organization-Wide QMS System** - A separate, centralized QMS repository for the entire organization is planned for future implementation. This release cycle will generate baseline documentation in formats that can be imported by that system (JSON/YAML exports, structured data). The decision on whether to keep repository-level baselines or migrate to centralized QMS will be made when that system is available.
4. **Commercial QMS Tools** - Expensive, vendor lock-in, may not integrate well with GitHub-based workflow

## Additional Context

**Industry Best Practices Incorporated:**
- Git Flow branching strategy (adapted)
- Semantic Versioning (MAJOR.MINOR.PATCH)
- Conventional Commits (already implemented)
- Continuous Integration testing gates
- Configuration Management per IEC 62304
- Audit-ready traceability documentation

**Implementation Priority:**

**High (blocks releases):**
- Fix/remove broken `just push`
- Create `create-release.sh` script
- Update CONTRIBUTE.md

**Medium (improves quality):**
- Create `generate-baseline.sh` (decide on Typst vs Markdown format)
- Create `finalize-release.sh`
- Create RELEASE_PROCESS.md runbook
- Define machine-readable export formats (JSON/YAML schemas) for QMS integration

**Low (nice to have):**
- Automate branch protection updates
- Integrate semantic-release tooling
- Automated rollback procedures

**Testing the Strategy:**
- Test scripts with `--dry-run` flags
- Validate with `0.0.0-test` pre-release versions
- Use workflow dispatch with `publish=false`
- Full workflow test with next planned release (0.3.0)

## Success Metrics

- 100% of releases have complete QMS baseline documentation
- All releases follow consistent process (measured by checklist completion)
- Zero failed releases due to process issues
- Baselines contain all IEC 62304 required information (auditor validation)
- Release process requires < 30 minutes manual effort

## Impact

**Beneficiaries:**
- Developers: Clear, automated release process
- QA/RA: Complete traceability and baseline documentation
- Auditors: Ready-made configuration management evidence
- Users: More reliable, well-tested releases

**Compatibility:**
- Backward compatible with existing CI/CD workflow
- Extends current branching strategy (no breaking changes)
- Leverages existing commit message standards

**Risks:**
- Low: Main risk is initial learning curve for release managers
- Mitigation: Detailed runbook and dry-run testing before first real release

**Compliance:**
- Directly addresses IEC 62304 Section 5.1 (Configuration Management) and 5.8 (Release)
- Provides audit-ready documentation for ISO 13485 compliance
- Establishes foundation for 21 CFR Part 11 traceability if needed

## Related Issues

- Parent: #37 (Automate and Standardize Repository Setup)
- Related: #36 (Commit Message Standardization) - provides traceability foundation
- Related: #38 (Branching Strategy & Enforcement) - branch protection for release branches

