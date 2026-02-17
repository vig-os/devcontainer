# vig-utils

Reusable CLI utilities for vigOS development workflows.

## Installation

```bash
pip install vig-utils
```

## Tools

### `validate-commit-msg`

Validates commit messages against the vigOS commit message standard, ensuring consistent and well-structured commit history.

**Purpose:** Used as a Git `commit-msg` hook to enforce commit message conventions.

**Standard Reference:** See [docs/COMMIT_MESSAGE_STANDARD.md](../../docs/COMMIT_MESSAGE_STANDARD.md)

**Commit Message Format:**

```
type(scope)!: short description

[optional body]

Refs: #<issue> [, #<issue2>] [, REQ-..., RISK-..., SOP-...]
```

**Commit Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `chore` - Maintenance tasks (refs optional)
- `refactor` - Code refactoring
- `test` - Test additions/modifications
- `ci` - CI/CD configuration
- `build` - Build system changes
- `revert` - Revert a previous commit
- `style` - Code style changes (whitespace, formatting)

**Key Requirements:**
- First line must match `type(scope): short description` (scope is optional)
- Blank line required between subject and body/Refs
- Refs line is mandatory (except for `chore` type)
- Refs must include at least one GitHub issue (e.g., `#36`)
- Additional reference types: `REQ-...`, `RISK-...`, `SOP-...`

**Usage:**

```bash
# Validate a commit message file (Git hook usage)
validate-commit-msg .git/COMMIT_EDITMSG

# Exit codes:
#   0 — Validation passed
#   1 — Validation failed
#   2 — Usage error
```

**Examples:**

Valid:

```
feat(ci): add commit-msg validation hook

Refs: #36
```

Invalid (missing Refs):

```
feat(ci): add commit-msg validation hook
```

Invalid (wrong type):

```
feature(ci): add commit-msg validation hook

Refs: #36
```

---

### `check-action-pins`

Verifies that all external GitHub Actions in workflows are pinned to full commit SHAs, preventing accidental execution of mutable action versions.

**Purpose:** Security and reproducibility check for GitHub Actions workflows.

**Scope:**
- Scans: `.github/workflows/*.yml` and `.github/actions/*/action.yml`
- External actions (e.g., `actions/checkout@<ref>`)
- Local actions (starting with `./`) are excluded

**Valid Format:**

```yaml
uses: owner/action@<40-character-sha>  # v1.0.0 (comment with version)
```

**Why SHA Pinning?**
- Tags and branches can be changed/deleted
- SHAs are immutable and provide reproducibility
- Protects against supply chain attacks

**Usage:**

```bash
# Check all workflows in current directory
check-action-pins

# Verbose output showing all checks
check-action-pins --verbose

# Check specific repository
check-action-pins --repo-root /path/to/repo

# Exit codes:
#   0 — All external actions are properly SHA-pinned
#   1 — One or more actions use mutable references
```

**Example Output:**

Success:

```
All external actions are SHA-pinned (12 files checked)
```

Failure:

```
Found 2 unpinned action(s):

  .github/workflows/ci.yml:15: unpinned action: actions/checkout@v4 (expected 40-char SHA)
  .github/workflows/test.yml:8: missing version reference: actions/setup-python

All external GitHub Actions must be pinned to commit SHAs.
Format: uses: owner/action@<40-char-sha> # vX.Y.Z
```

---

### `prepare-changelog`

Manages CHANGELOG.md during the release workflow following [Keep a Changelog](https://keepachangelog.com) format.

**Purpose:** Automate changelog operations: validation, release preparation, date finalization, and section reset.

**Changelog Format:**

```markdown
# Changelog

...header...

## Unreleased

### Added
- ...

### Changed
- ...

### Deprecated
- ...

### Removed
- ...

### Fixed
- ...

### Security
- ...

## [1.0.0] - YYYY-MM-DD

### Added
- ...
```

**Standard Sections (in order):**
- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

**Commands:**

#### `validate`
Verifies that CHANGELOG has an Unreleased section with content.

```bash
prepare-changelog validate [FILE]
prepare-changelog validate CHANGELOG.md  # default

# Exit: 0 if valid, 1 if invalid
```

Checks:
- Unreleased section exists
- Section contains at least one item (starts with `-`)

#### `prepare <version>`
Prepares changelog for release by moving Unreleased content to a versioned section.

```bash
prepare-changelog prepare 1.0.0
prepare-changelog prepare 1.0.0 CHANGELOG.md  # with custom file
```

Actions:
1. Extracts content from Unreleased section
2. Moves it to `## [<version>] - TBD`
3. Creates fresh Unreleased section with all standard subsections
4. Preserves existing release sections

**Output:**

```
✓ Prepared CHANGELOG for version 1.0.0
✓ Moved 3 section(s) with content to [1.0.0] - TBD
  - Added
  - Fixed
  - Security
✓ Created fresh Unreleased section
```

#### `finalize <version> <date>`
Sets the actual release date for a version (replaces TBD placeholder).

```bash
prepare-changelog finalize 1.0.0 2026-02-13
```

Changes:

```markdown
# Before:
## [1.0.0] - TBD

# After:
## [1.0.0] - 2026-02-13
```

Requirements:
- Version must exist with `TBD` date
- Date format: `YYYY-MM-DD`

#### `reset`
Creates a fresh Unreleased section with empty subsections.

```bash
prepare-changelog reset
prepare-changelog reset CHANGELOG.md  # with custom file
```

**Use case:** After merging a release back to dev branch, when the Unreleased section has been removed.

Outputs:

```
✓ Reset Unreleased section in CHANGELOG.md
✓ Created fresh empty section for next release
```

**Release Workflow Example:**

```bash
# 1. In release branch: prepare changelog
prepare-changelog prepare 1.0.0

# 2. Review changes, make any manual edits

# 3. On release day: finalize the date
prepare-changelog finalize 1.0.0 2026-02-13

# 4. After merging release back to dev: reset
prepare-changelog reset
```

---

## Common Workflows

### Git Hook Setup

```bash
# Install vig-utils
pip install vig-utils

# Add to .git/hooks/commit-msg (or via pre-commit)
validate-commit-msg $1
```

### CI/CD Integration
All tools are designed for CI/CD pipelines:
- Exit with 0 on success
- Exit with non-zero on failure
- Structured output for parsing
- Verbose modes available

### Release Checklist
1. Validate: `prepare-changelog validate`
2. Check actions: `check-action-pins`
3. Prepare: `prepare-changelog prepare X.Y.Z`
4. Test, review, merge
5. Finalize: `prepare-changelog finalize X.Y.Z YYYY-MM-DD`
