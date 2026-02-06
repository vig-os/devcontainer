"""
Tests for scripts/prepare-changelog.py

These tests verify the CHANGELOG preparation logic:
- Extracting content from Unreleased section
- Moving content to versioned section with TBD date
- Creating fresh Unreleased section
- Cleaning up empty subsections
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestPrepareChangelog:
    """Tests for prepare-changelog.py script."""

    @pytest.fixture
    def script_path(self):
        """Path to prepare-changelog.py."""
        return Path(__file__).resolve().parents[1] / "scripts" / "prepare-changelog.py"

    @pytest.fixture
    def basic_changelog(self):
        """Basic CHANGELOG with Unreleased content."""
        return """# Changelog

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

    @pytest.fixture
    def empty_sections_changelog(self):
        """CHANGELOG with some empty sections."""
        return """# Changelog

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

    @pytest.fixture
    def minimal_changelog(self):
        """Minimal CHANGELOG with just one section."""
        return """# Changelog

## Unreleased

### Added

- Single feature

## [0.1.0] - 2025-12-01

### Added

- Initial release
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Basic Functionality
    # ═══════════════════════════════════════════════════════════════════════════

    def test_creates_new_version_section_with_tbd(
        self, script_path, basic_changelog, tmp_path
    ):
        """Should create version section with TBD date."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()

        # Should still have 0.2.0 section
        assert "## [0.2.0] - 2026-01-01" in content
        assert "- Previous feature" in content

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Version Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_rejects_invalid_semver(self, script_path, basic_changelog, tmp_path):
        """Should reject non-semantic version formats."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "1.2.3.4", str(changelog_file)],
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
            [sys.executable, str(script_path), "v1.2.3", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.2.3-alpha", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0

    def test_accepts_valid_semver(self, script_path, basic_changelog, tmp_path):
        """Should accept valid semantic versions."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "1.2.3", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Should accept valid semver: {result.stderr}"

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Error Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fails_for_missing_changelog(self, script_path, tmp_path):
        """Should fail gracefully if CHANGELOG doesn't exist."""
        nonexistent = tmp_path / "nonexistent.md"

        result = subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(nonexistent)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "exist" in result.stderr.lower()

    def test_fails_for_missing_unreleased_section(self, script_path, tmp_path):
        """Should fail if no Unreleased section exists."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text("""# Changelog

## [0.2.0] - 2026-01-01

### Added

- Old feature
""")

        result = subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "unreleased" in result.stderr.lower()

    def test_warns_for_empty_unreleased(self, script_path, tmp_path):
        """Should warn but succeed if Unreleased is empty."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text("""# Changelog

## Unreleased

### Added

### Changed

### Fixed

## [0.2.0] - 2026-01-01

### Added

- Old feature
""")

        result = subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        # Should succeed but warn
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "warn" in output.lower() or "no content" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Content Preservation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_preserves_multiline_bullets(self, script_path, tmp_path):
        """Should preserve multi-line bullet point formatting."""
        changelog = """# Changelog

## Unreleased

### Added

- New feature with
  multiple lines of description
  and even more details

## [0.1.0] - 2025-01-01
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()
        assert "multiple lines of description" in content
        assert "and even more details" in content

    def test_preserves_nested_bullets(self, script_path, tmp_path):
        """Should preserve nested bullet points."""
        changelog = """# Changelog

## Unreleased

### Added

- Main feature
  - Sub-feature A
  - Sub-feature B

## [0.1.0] - 2025-01-01
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            check=True,
            capture_output=True,
        )

        content = changelog_file.read_text()
        assert "- Main feature" in content
        assert "- Sub-feature A" in content
        assert "- Sub-feature B" in content

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Output Messages
    # ═══════════════════════════════════════════════════════════════════════════

    def test_reports_sections_moved(self, script_path, basic_changelog, tmp_path):
        """Should report which sections were moved."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        result = subprocess.run(
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
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
            [sys.executable, str(script_path), "1.0.0", str(changelog_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1.0.0" in result.stdout
        assert "✓" in result.stdout or "success" in result.stdout.lower()
