"""
Tests for the release cycle scripts.

These tests verify:
- CHANGELOG preparation logic (prepare-changelog.py):
  extracting Unreleased content, creating versioned sections,
  cleaning up empty subsections, validation, and reset.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# region Test Data Constants

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

UNRELEASED_ONLY_CHANGELOG = """\
# Changelog

## Unreleased

### Added

- Brand new feature

### Fixed

- Important bugfix
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

# CHANGELOG after prepare-release.sh has run (for finalize-release tests)
PREPARED_CHANGELOG = """\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - TBD

### Added

- New feature X
- New feature Y

### Fixed

- Bug fix Z

## [0.2.0] - 2026-01-01

### Added

- Previous feature
"""

CHANGELOG_WITH_TBD = """\
# Changelog

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - TBD

### Added

- Feature X
- Feature Y

### Fixed

- Bug A

## [0.2.0] - 2026-01-01

### Added

- Old feature
"""

MULTIPLE_TBD_CHANGELOG = """\
# Changelog

## Unreleased

### Added

## [2.0.0] - TBD

### Added

- Feature Z

## [1.0.0] - TBD

### Added

- Feature X

## [0.1.0] - 2025-12-01

### Added

- Initial
"""

SPECIAL_CHARS_CHANGELOG = """\
# Changelog

## Unreleased

### Added

## [1.0.0] - TBD

### Added

- Feature with [brackets] and (parentheses)
- Feature with special $chars* and .dots

## [0.1.0] - 2025-12-01

### Added

- Initial
"""
# endregion


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

    def test_prepare_changelog_with_only_unreleased(self, script_path, tmp_path):
        """Should succeed when CHANGELOG has only Unreleased and no prior versions."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(UNRELEASED_ONLY_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "prepare", "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        content = changelog_file.read_text()
        # Should have the new version section
        assert "## [1.0.0] - TBD" in content
        # Content should be moved
        assert "- Brand new feature" in content
        assert "- Important bugfix" in content
        # Fresh Unreleased section should exist
        assert "## Unreleased" in content
        # Unreleased should come before the version
        assert content.index("## Unreleased") < content.index("## [1.0.0] - TBD")

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

    def test_validate_fails_for_empty_unreleased(self, script_path, tmp_path):
        """validate action should fail if Unreleased is empty."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(VALIDATE_EMPTY_UNRELEASED_CHANGELOG)

        result = subprocess.run(
            [sys.executable, str(script_path), "validate", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "empty" in result.stderr.lower()

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


class TestFinalizeCommand:
    """Tests for finalize command - setting release dates."""

    @pytest.fixture
    def script_path(self):
        """Path to prepare-changelog.py."""
        return Path(__file__).resolve().parents[1] / "scripts" / "prepare-changelog.py"

    @pytest.fixture
    def changelog_with_tbd(self):
        """CHANGELOG with a version section using TBD."""
        return CHANGELOG_WITH_TBD

    # ═══════════════════════════════════════════════════════════════════════════
    # Finalize Action Tests - Basic Functionality
    # ═══════════════════════════════════════════════════════════════════════════

    def test_replaces_tbd_with_date(self, script_path, changelog_with_tbd, tmp_path):
        """Should replace TBD with actual release date."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        content = changelog_file.read_text()
        assert "## [1.0.0] - 2026-02-11" in content
        assert "TBD" not in content

    def test_preserves_version_content(self, script_path, changelog_with_tbd, tmp_path):
        """Should preserve all content in version section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Check version section still has its content
        version_start = content.find("## [1.0.0] - 2026-02-11")
        version_end = content.find("## [0.2.0]")
        version_section = content[version_start:version_end]

        assert "- Feature X" in version_section
        assert "- Feature Y" in version_section
        assert "- Bug A" in version_section

    def test_preserves_other_sections(self, script_path, changelog_with_tbd, tmp_path):
        """Should not modify other version sections."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Old version should remain unchanged
        assert "## [0.2.0] - 2026-01-01" in content
        assert "- Old feature" in content

        # Unreleased should remain unchanged
        assert "## Unreleased" in content

    def test_outputs_success_message(self, script_path, changelog_with_tbd, tmp_path):
        """Should output success message with version and date."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1.0.0" in result.stdout
        assert "2026-02-11" in result.stdout

    # ═══════════════════════════════════════════════════════════════════════════
    # Finalize Action Tests - Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fails_if_version_not_found(
        self, script_path, changelog_with_tbd, tmp_path
    ):
        """Should fail if version section doesn't exist."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "2.0.0",  # Non-existent version
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "2.0.0" in result.stderr

    def test_fails_if_version_already_has_date(
        self, script_path, changelog_with_tbd, tmp_path
    ):
        """Should fail if version already has a release date (not TBD)."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "0.2.0",  # This version already has date 2026-01-01
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "TBD" in result.stderr

    def test_rejects_invalid_semver(self, script_path, changelog_with_tbd, tmp_path):
        """Should reject invalid semantic version format."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0",  # Invalid semver
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "Invalid" in result.stderr or "version" in result.stderr.lower()

    def test_rejects_version_with_v_prefix(
        self, script_path, changelog_with_tbd, tmp_path
    ):
        """Should reject versions with 'v' prefix."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "v1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "Invalid" in result.stderr or "version" in result.stderr.lower()

    def test_rejects_invalid_date_format(
        self, script_path, changelog_with_tbd, tmp_path
    ):
        """Should reject dates not in YYYY-MM-DD format."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog_with_tbd)

        invalid_dates = [
            "2026/02/11",  # Wrong separators
            "02-11-2026",  # Wrong order
            "2026-2-11",  # Missing leading zero
            "2026-02-1",  # Missing leading zero
            "11-02-2026",  # Wrong order
            "not-a-date",  # Completely invalid
        ]

        for invalid_date in invalid_dates:
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "finalize",
                    "1.0.0",
                    invalid_date,
                    str(changelog_file),
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0, f"Should fail for date: {invalid_date}"
            assert "Invalid" in result.stderr or "date" in result.stderr.lower(), (
                f"Should mention invalid date for: {invalid_date}"
            )

    def test_fails_if_changelog_missing(self, script_path, tmp_path):
        """Should fail gracefully if CHANGELOG file doesn't exist."""
        changelog_file = tmp_path / "nonexistent.md"

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert (
            "not found" in result.stderr.lower()
            or "No such file" in result.stderr
            or "FileNotFoundError" in result.stderr
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Finalize Action Tests - Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════

    def test_handles_multiple_tbd_versions(self, script_path, tmp_path):
        """Should only update the specified version when multiple TBD versions exist."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(MULTIPLE_TBD_CHANGELOG)

        # Finalize version 1.0.0
        subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Version 1.0.0 should be finalized
        assert "## [1.0.0] - 2026-02-11" in content

        # Version 2.0.0 should still have TBD
        assert "## [2.0.0] - TBD" in content

    def test_handles_version_with_special_characters_in_content(
        self, script_path, tmp_path
    ):
        """Should handle versions with special regex characters in content."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(SPECIAL_CHARS_CHANGELOG)

        subprocess.run(
            [
                sys.executable,
                str(script_path),
                "finalize",
                "1.0.0",
                "2026-02-11",
                str(changelog_file),
            ],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Should update correctly
        assert "## [1.0.0] - 2026-02-11" in content
        # Content should be preserved
        assert "- Feature with [brackets] and (parentheses)" in content
        assert "- Feature with special $chars* and .dots" in content
