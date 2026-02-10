"""
Tests for the release cycle scripts.

These tests verify:
- CHANGELOG preparation logic (prepare-changelog.py):
  extracting Unreleased content, creating versioned sections,
  cleaning up empty subsections, validation, and reset.
- Release management scripts (prepare-release.sh, finalize-release.sh):
  version validation, branch requirements, CHANGELOG requirements,
  and dry-run mode.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Constants
# ═══════════════════════════════════════════════════════════════════════════════

BASIC_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- New feature X
- New feature Y

### Changed

- Updated component Z

### Deprecated

### Removed

### Fixed

- Bug fix A
- Bug fix B

### Security

## [0.2.0] - 2026-01-01

### Added

- Previous feature
"""

EMPTY_SECTIONS_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- New feature

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2026-01-01

### Added

- Old feature
"""

MINIMAL_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- Single feature

## [0.1.0] - 2025-12-01

### Added

- Initial release
"""

NO_UNRELEASED_CHANGELOG = """\
# Changelog

## [0.2.0] - 2026-01-01

### Added

- Old feature
"""

EMPTY_UNRELEASED_CHANGELOG = """\
# Changelog

## Unreleased

### Added

### Changed

### Fixed

## [0.2.0] - 2026-01-01

### Added

- Old feature
"""

MULTILINE_BULLETS_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- New feature with
  multiple lines of description
  and even more details

## [0.1.0] - 2025-01-01
"""

NESTED_BULLETS_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- Main feature
  - Sub-feature A
  - Sub-feature B

## [0.1.0] - 2025-01-01
"""

VALIDATE_EMPTY_UNRELEASED_CHANGELOG = """\
# Changelog

## Unreleased

### Added

### Changed

## [0.2.0] - 2026-01-01
"""

RELEASED_ONLY_CHANGELOG = """\
# Changelog

## [1.0.0] - 2026-02-06

### Added

- Released feature

## [0.2.0] - 2026-01-01

### Added

- Old feature
"""

GIT_REPO_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- New feature X
- New feature Y

### Fixed

- Bug fix Z

## [0.2.0] - 2026-01-01

### Added

- Previous feature
"""


# ═══════════════════════════════════════════════════════════════════════════════
# prepare-changelog.py Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPrepareChangelog:
    """Tests for prepare-changelog.py script."""

    @pytest.fixture
    def script_path(self):
        """Path to prepare-changelog.py."""
        return Path(__file__).resolve().parents[1] / "scripts" / "prepare-changelog.py"

    @pytest.fixture
    def basic_changelog(self):
        """Basic CHANGELOG with Unreleased content."""
        return BASIC_CHANGELOG

    @pytest.fixture
    def empty_sections_changelog(self):
        """CHANGELOG with some empty sections."""
        return EMPTY_SECTIONS_CHANGELOG

    @pytest.fixture
    def minimal_changelog(self):
        """Minimal CHANGELOG with just one section."""
        return MINIMAL_CHANGELOG

    # ═══════════════════════════════════════════════════════════════════════════
    # Prepare Action Tests - Basic Functionality
    # ═══════════════════════════════════════════════════════════════════════════

    def test_creates_new_version_section_with_tbd(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should create version section with TBD date."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        content = changelog_file.read_text()
        assert "## [1.0.0] - TBD" in content, "Should have version with TBD date"

    def test_moves_content_to_version_section(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should move Unreleased content to version section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Find version section
        version_start = content.find("## [1.0.0] - TBD")
        version_end = content.find("## [0.2.0]")
        version_section = content[version_start:version_end]

        # Verify content moved
        assert "- New feature X" in version_section
        assert "- New feature Y" in version_section
        assert "- Updated component Z" in version_section
        assert "- Bug fix A" in version_section
        assert "- Bug fix B" in version_section

    def test_creates_fresh_unreleased_section(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should create fresh empty Unreleased section at top."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Find Unreleased section
        unreleased_start = content.find("## Unreleased")
        version_start = content.find("## [1.0.0]")
        unreleased_section = content[unreleased_start:version_start]

        # Should have all standard headers
        assert "### Added" in unreleased_section
        assert "### Changed" in unreleased_section
        assert "### Deprecated" in unreleased_section
        assert "### Removed" in unreleased_section
        assert "### Fixed" in unreleased_section
        assert "### Security" in unreleased_section

        # Should be empty (no bullet points)
        assert "- " not in unreleased_section

    def test_removes_empty_sections_from_version(
        self, script_path, empty_sections_changelog, tmp_path
    ):
        """Should not include empty sections in version."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(empty_sections_changelog)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Find version section
        version_start = content.find("## [1.0.0] - TBD")
        version_end = content.find("## [0.2.0]")
        version_section = content[version_start:version_end]

        # Should only have Added section (the one with content)
        assert "### Added" in version_section
        assert "- New feature" in version_section

        # Should NOT have empty sections
        assert "### Changed" not in version_section
        assert "### Deprecated" not in version_section
        assert "### Removed" not in version_section
        assert "### Fixed" not in version_section
        assert "### Security" not in version_section

    def test_preserves_previous_versions(self, script_path, basic_changelog, tmp_path):
        """Should preserve all previous version sections."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Should still have 0.2.0 section
        assert "## [0.2.0] - 2026-01-01" in content
        assert "- Previous feature" in content

    # ═══════════════════════════════════════════════════════════════════════════
    # Prepare Action Tests - Version Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_rejects_invalid_semver(self, script_path, basic_changelog, tmp_path):
        """Should reject non-semantic version formats."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "prepare",
                "1.2.3.4",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail for invalid semver"
        assert "Invalid" in result.stderr or "version" in result.stderr.lower()

    def test_rejects_version_with_v_prefix(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should reject versions with 'v' prefix."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "prepare",
                "v1.2.3",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "Invalid" in result.stderr or "version" in result.stderr.lower()

    def test_rejects_version_with_prerelease(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should reject versions with pre-release suffixes."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "prepare",
                "1.2.3-alpha",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0

    def test_accepts_valid_semver(self, script_path, basic_changelog, tmp_path):
        """Should accept valid semantic versions."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.2.3", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Should accept valid semver: {result.stderr}"

    # ═══════════════════════════════════════════════════════════════════════════
    # Prepare Action Tests - Error Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fails_for_missing_changelog(self, script_path, tmp_path):
        """Should fail gracefully if CHANGELOG doesn't exist."""
        nonexistent = tmp_path / "nonexistent.md"

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(nonexistent)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "exist" in result.stderr.lower()

    def test_fails_for_missing_unreleased_section(self, script_path, tmp_path):
        """Should fail if no Unreleased section exists."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(NO_UNRELEASED_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "unreleased" in result.stderr.lower()

    def test_warns_for_empty_unreleased(self, script_path, tmp_path):
        """Should warn but succeed if Unreleased is empty."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(EMPTY_UNRELEASED_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        # Should succeed but warn
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "warn" in output.lower() or "no content" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Prepare Action Tests - Content Preservation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_preserves_multiline_bullets(self, script_path, tmp_path):
        """Should preserve multi-line bullet point formatting."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(MULTILINE_BULLETS_CHANGELOG)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()
        assert "multiple lines of description" in content
        assert "and even more details" in content

    def test_preserves_nested_bullets(self, script_path, tmp_path):
        """Should preserve nested bullet points."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(NESTED_BULLETS_CHANGELOG)

        subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()
        assert "- Main feature" in content
        assert "- Sub-feature A" in content
        assert "- Sub-feature B" in content

    # ═══════════════════════════════════════════════════════════════════════════
    # Prepare Action Tests - Output Messages
    # ═══════════════════════════════════════════════════════════════════════════

    def test_reports_sections_moved(self, script_path, basic_changelog, tmp_path):
        """Should report which sections were moved."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout
        assert "Added" in output
        assert "Changed" in output
        assert "Fixed" in output

    def test_reports_success_message(self, script_path, basic_changelog, tmp_path):
        """Should report success with version."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1.0.0" in result.stdout
        assert "✓" in result.stdout or "success" in result.stdout.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Validate Action Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_validate_passes_with_unreleased_content(
        self, script_path, basic_changelog, tmp_path
    ):
        """validate action should pass when Unreleased has content."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "validate", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Should pass validation: {result.stderr}"
        assert "✓" in result.stdout or "valid" in result.stdout.lower()

    def test_validate_fails_without_unreleased_section(self, script_path, tmp_path):
        """validate action should fail if no Unreleased section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(NO_UNRELEASED_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "validate", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "unreleased" in result.stderr.lower()

    def test_validate_warns_for_empty_unreleased(self, script_path, tmp_path):
        """validate action should warn if Unreleased is empty."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(VALIDATE_EMPTY_UNRELEASED_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "validate", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        # Should succeed but warn
        assert result.returncode == 0
        output = result.stdout.lower()
        assert "warn" in output or "empty" in output

    # ═══════════════════════════════════════════════════════════════════════════
    # Reset Action Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_reset_creates_fresh_unreleased_section(self, script_path, tmp_path):
        """reset action should create fresh Unreleased section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(RELEASED_ONLY_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "reset", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        content = changelog_file.read_text()
        assert "## Unreleased" in content

        # Check all standard sections are present
        unreleased_section = content.split("## [1.0.0]")[0]
        assert "### Added" in unreleased_section
        assert "### Changed" in unreleased_section
        assert "### Deprecated" in unreleased_section
        assert "### Removed" in unreleased_section
        assert "### Fixed" in unreleased_section
        assert "### Security" in unreleased_section

    def test_reset_preserves_existing_versions(self, script_path, tmp_path):
        """reset action should not modify existing version sections."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(RELEASED_ONLY_CHANGELOG)

        subprocess.run(
            [sys.executable, str(script_path), "reset", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()
        assert "## [1.0.0] - 2026-02-06" in content
        assert "## [0.2.0] - 2026-01-01" in content
        assert "- Released feature" in content
        assert "- Old feature" in content

    def test_reset_fails_if_unreleased_exists(
        self, script_path, basic_changelog, tmp_path
    ):
        """reset action should fail if Unreleased section already exists."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "reset", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert (
            "already exists" in result.stderr.lower()
            or "unreleased" in result.stderr.lower()
        )


# ═══════════════════════════════════════════════════════════════════════════════
# prepare-release.sh Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPrepareReleaseScript:
    """Tests for scripts/prepare-release.sh - release branch preparation."""

    @pytest.fixture
    def script_path(self):
        """Path to prepare-release.sh."""
        return Path(__file__).resolve().parents[1] / "scripts" / "prepare-release.sh"

    @pytest.fixture
    def minimal_git_repo(self, tmp_path):
        """Create a minimal git repository for testing."""
        repo = tmp_path / "test-repo"
        repo.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create dev branch
        subprocess.run(
            ["git", "checkout", "-b", "dev"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create CHANGELOG.md with Unreleased section
        changelog = repo / "CHANGELOG.md"
        changelog.write_text(GIT_REPO_CHANGELOG)

        # Create initial commit
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        return repo

    # ═══════════════════════════════════════════════════════════════════════════
    # Version Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_rejects_invalid_semver_format(self, script_path, minimal_git_repo):
        """Should reject non-semantic version formats."""
        result = subprocess.run(
            [str(script_path), "1.2.3.4", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Should fail for invalid semver"
        assert (
            "Invalid version format" in result.stdout
            or "Invalid version format" in result.stderr
        )

    def test_rejects_version_with_v_prefix(self, script_path, minimal_git_repo):
        """Should reject versions with 'v' prefix."""
        result = subprocess.run(
            [str(script_path), "v1.2.3", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "Invalid version format" in output or "1.2.3" in output

    def test_rejects_version_with_prerelease_suffix(
        self, script_path, minimal_git_repo
    ):
        """Should reject versions with pre-release suffixes."""
        result = subprocess.run(
            [str(script_path), "1.2.3-alpha", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert (
            "Invalid version format" in result.stdout
            or "Invalid version format" in result.stderr
        )

    def test_accepts_valid_semver(self, script_path, minimal_git_repo):
        """Should accept valid semantic versions."""
        # Test with dry-run to avoid actually creating branches
        result = subprocess.run(
            [str(script_path), "1.2.3", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        # Should not fail on version validation
        assert "Invalid version format" not in (result.stdout + result.stderr)

    # ═══════════════════════════════════════════════════════════════════════════
    # Branch Requirements
    # ═══════════════════════════════════════════════════════════════════════════

    def test_requires_dev_branch(self, script_path, minimal_git_repo):
        """Should fail if not on dev branch."""
        # Create and checkout a different branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/test"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail when not on dev branch"
        output = result.stdout + result.stderr
        assert "dev branch" in output.lower()

    def test_detects_uncommitted_changes(self, script_path, minimal_git_repo):
        """Should fail if uncommitted changes exist."""
        # Modify CHANGELOG without committing
        changelog = minimal_git_repo / "CHANGELOG.md"
        changelog.write_text(changelog.read_text() + "\n- Uncommitted change\n")

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail with uncommitted changes"
        output = result.stdout + result.stderr
        assert "uncommitted" in output.lower() or "changes" in output.lower()

    def test_prevents_duplicate_release_branch(self, script_path, minimal_git_repo):
        """Should fail if release branch already exists."""
        # Create a release branch
        subprocess.run(
            ["git", "checkout", "-b", "release/1.0.0"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "dev"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail if release branch exists"
        output = result.stdout + result.stderr
        assert "already exists" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # CHANGELOG Requirements
    # ═══════════════════════════════════════════════════════════════════════════

    def test_requires_unreleased_section(self, script_path, minimal_git_repo):
        """Should fail if no Unreleased section in CHANGELOG."""
        # Remove Unreleased section
        changelog = minimal_git_repo / "CHANGELOG.md"
        content = changelog.read_text().replace("## Unreleased", "## Old Section")
        changelog.write_text(content)
        subprocess.run(
            ["git", "add", "CHANGELOG.md"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Remove Unreleased"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail without Unreleased section"
        output = result.stdout + result.stderr
        assert "unreleased" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Dry-run Mode
    # ═══════════════════════════════════════════════════════════════════════════

    def test_dry_run_creates_no_branches(self, script_path, minimal_git_repo):
        """Dry-run should not create any branches."""
        # Get current branches
        result_before = subprocess.run(
            ["git", "branch", "--list"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        branches_before = set(result_before.stdout.strip().split("\n"))

        # Run prepare-release in dry-run mode
        subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        # Check branches after
        result_after = subprocess.run(
            ["git", "branch", "--list"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        branches_after = set(result_after.stdout.strip().split("\n"))

        assert branches_before == branches_after, "Dry-run should not create branches"

    def test_dry_run_modifies_no_files(self, script_path, minimal_git_repo):
        """Dry-run should not modify any files."""
        # Get current git status
        result_before = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        # Run prepare-release in dry-run mode
        subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        # Check git status after
        result_after = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        assert result_before.stdout == result_after.stdout, (
            "Dry-run should not modify files"
        )

    def test_dry_run_shows_planned_actions(self, script_path, minimal_git_repo):
        """Dry-run should display what would be done."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr
        assert "dry run" in output.lower() or "would" in output.lower()
        assert "release/1.0.0" in output


# ═══════════════════════════════════════════════════════════════════════════════
# finalize-release.sh Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFinalizeReleaseScript:
    """Tests for scripts/finalize-release.sh - release finalization.

    These tests will be implemented after prepare-release.sh is working.
    """

    @pytest.fixture
    def script_path(self):
        """Path to finalize-release.sh."""
        return Path(__file__).resolve().parents[1] / "scripts" / "finalize-release.sh"

    def test_script_exists(self, script_path):
        """finalize-release.sh should exist (placeholder test)."""
        # This will fail until we create the script
        assert script_path.exists(), "finalize-release.sh not yet created"
