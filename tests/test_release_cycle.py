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


class TestFinalizeReleaseScript:
    """Tests for scripts/finalize-release.sh - release finalization."""

    @pytest.fixture
    def script_path(self):
        """Path to finalize-release.sh."""
        return Path(__file__).resolve().parents[1] / "scripts" / "finalize-release.sh"

    @pytest.fixture
    def prepared_release_repo(self, tmp_path):
        """Create a git repo simulating state after prepare-release.sh ran.

        - On branch release/1.0.0
        - CHANGELOG has ## [1.0.0] - TBD
        - Clean working tree
        """
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

        # Create dev branch with initial commit
        subprocess.run(
            ["git", "checkout", "-b", "dev"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        changelog = repo / "CHANGELOG.md"
        changelog.write_text(GIT_REPO_CHANGELOG)
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create release branch (simulating prepare-release.sh)
        subprocess.run(
            ["git", "checkout", "-b", "release/1.0.0"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Write prepared CHANGELOG
        changelog.write_text(PREPARED_CHANGELOG)

        # Commit preparation changes
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: prepare release 1.0.0\n\nRefs: #48"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        return repo

    # ═══════════════════════════════════════════════════════════════════════════
    # Script Existence
    # ═══════════════════════════════════════════════════════════════════════════

    def test_script_exists(self, script_path):
        """finalize-release.sh should exist."""
        assert script_path.exists(), "finalize-release.sh should exist"

    # ═══════════════════════════════════════════════════════════════════════════
    # Version Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_rejects_invalid_semver_format(self, script_path, prepared_release_repo):
        """Should reject non-semantic version formats."""
        result = subprocess.run(
            [str(script_path), "1.2.3.4", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Should fail for invalid semver"
        output = result.stdout + result.stderr
        assert "Invalid version format" in output

    def test_rejects_version_with_v_prefix(self, script_path, prepared_release_repo):
        """Should reject versions with 'v' prefix."""
        result = subprocess.run(
            [str(script_path), "v1.2.3", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "Invalid version format" in output

    def test_accepts_valid_semver(self, script_path, prepared_release_repo):
        """Should accept valid semantic versions (with dry-run on matching branch)."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )
        # Should not fail on version validation
        output = result.stdout + result.stderr
        assert "Invalid version format" not in output

    # ═══════════════════════════════════════════════════════════════════════════
    # Branch Requirements
    # ═══════════════════════════════════════════════════════════════════════════

    def test_requires_release_branch(self, script_path, prepared_release_repo):
        """Should fail if not on release branch."""
        # Switch to dev
        subprocess.run(
            ["git", "checkout", "dev"],
            cwd=prepared_release_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail when not on release branch"
        output = result.stdout + result.stderr
        assert "release/1.0.0" in output.lower()

    def test_requires_matching_release_branch(self, script_path, prepared_release_repo):
        """Should fail if on wrong release branch for given version."""
        # Create and switch to a different release branch
        subprocess.run(
            ["git", "checkout", "-b", "release/2.0.0"],
            cwd=prepared_release_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "2.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        # Should fail because CHANGELOG has [1.0.0] - TBD, not [2.0.0] - TBD
        assert result.returncode != 0, "Should fail with mismatched version"
        output = result.stdout + result.stderr
        assert "2.0.0" in output

    # ═══════════════════════════════════════════════════════════════════════════
    # State Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_detects_uncommitted_changes(self, script_path, prepared_release_repo):
        """Should fail if uncommitted changes exist."""
        # Modify a tracked file without committing
        changelog = prepared_release_repo / "CHANGELOG.md"
        changelog.write_text(changelog.read_text() + "\n- Uncommitted change\n")

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail with uncommitted changes"
        output = result.stdout + result.stderr
        assert "uncommitted" in output.lower()

    def test_fails_if_changelog_missing_tbd(self, script_path, prepared_release_repo):
        """Should fail if CHANGELOG missing TBD entry for version."""
        # Replace TBD with an actual date (simulating already finalized)
        changelog = prepared_release_repo / "CHANGELOG.md"
        content = changelog.read_text().replace(
            "## [1.0.0] - TBD", "## [1.0.0] - 2026-01-01"
        )
        changelog.write_text(content)
        subprocess.run(
            ["git", "add", "CHANGELOG.md"],
            cwd=prepared_release_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Already finalized"],
            cwd=prepared_release_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail without TBD entry"
        output = result.stdout + result.stderr
        assert "TBD" in output or "prepare-release" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Actions
    # ═══════════════════════════════════════════════════════════════════════════

    def test_sets_release_date_in_changelog(self, script_path, prepared_release_repo):
        """Should replace TBD with actual date in CHANGELOG."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Script failed: {result.stdout}\n{result.stderr}"
        )

        # In dry-run mode, verify the script would perform the action
        output = result.stdout + result.stderr
        assert "Set release date" in output or "CHANGELOG" in output

    def test_creates_annotated_tag(self, script_path, prepared_release_repo):
        """Should create annotated tag v1.0.0."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Script failed: {result.stdout}\n{result.stderr}"
        )

        # In dry-run mode, verify the script would create the tag
        output = result.stdout + result.stderr
        assert "v1.0.0" in output or "tag" in output.lower()

    def test_commit_message_follows_standard(self, script_path, prepared_release_repo):
        """Finalization commit should follow commit message standard."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Script failed: {result.stdout}\n{result.stderr}"
        )

        # In dry-run mode, verify the script would create a commit
        output = result.stdout + result.stderr
        assert "commit" in output.lower() or "finalization" in output.lower()

    def test_prevents_duplicate_tag(self, script_path, prepared_release_repo):
        """Should fail if tag already exists."""
        # Create the tag first
        subprocess.run(
            ["git", "tag", "-a", "v1.0.0", "-m", "Existing tag"],
            cwd=prepared_release_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail if tag already exists"
        output = result.stdout + result.stderr
        assert "already exists" in output.lower() or "v1.0.0" in output

    # ═══════════════════════════════════════════════════════════════════════════
    # Dry-run Mode
    # ═══════════════════════════════════════════════════════════════════════════

    def test_dry_run_creates_no_tags(self, script_path, prepared_release_repo):
        """Dry-run should not create any tags."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Dry-run failed: {result.stdout}\n{result.stderr}"
        )

        # Check no tags were created
        tag_result = subprocess.run(
            ["git", "tag", "-l"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert tag_result.stdout.strip() == "", "Dry-run should not create tags"

    def test_dry_run_modifies_no_files(self, script_path, prepared_release_repo):
        """Dry-run should not modify any files."""
        result_before = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        result_after = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        assert result_before.stdout == result_after.stdout, (
            "Dry-run should not modify files"
        )

    def test_dry_run_shows_planned_actions(self, script_path, prepared_release_repo):
        """Dry-run should display what would be done."""
        result = subprocess.run(
            [str(script_path), "1.0.0", "--dry-run"],
            cwd=prepared_release_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Dry-run failed: {result.stdout}\n{result.stderr}"
        )

        output = result.stdout + result.stderr
        assert "dry run" in output.lower()
        assert "v1.0.0" in output
        # Should mention key actions
        assert "changelog" in output.lower() or "CHANGELOG" in output
        assert "tag" in output.lower()

        # Verify specific commands are shown
        assert "uv run python scripts/prepare-changelog.py finalize" in output
        assert "git add CHANGELOG.md" in output
        assert 'git commit -m "chore: finalize release 1.0.0' in output
        assert "Refs: #999" in output  # Placeholder PR number
        assert "git push origin" in output
        assert "gh workflow run sync-issues.yml" in output
        assert 'git tag -s "v1.0.0"' in output
