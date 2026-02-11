"""
Comprehensive unit tests for prepare-changelog.py (import-based, not subprocess).

These tests import the prepare-changelog module and test all functions directly,
replacing the subprocess-based approach with direct function calls for better coverage.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import prepare-changelog module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

prep_spec = importlib.util.spec_from_file_location(
    "prepare_changelog", scripts_dir / "prepare-changelog.py"
)
prep_module = importlib.util.module_from_spec(prep_spec)
prep_spec.loader.exec_module(prep_module)

extract_unreleased_content = prep_module.extract_unreleased_content
create_new_changelog = prep_module.create_new_changelog
validate_changelog = prep_module.validate_changelog
reset_unreleased = prep_module.reset_unreleased
prepare_changelog = prep_module.prepare_changelog
finalize_release_date = prep_module.finalize_release_date


# Shared fixtures
@pytest.fixture
def basic_changelog():
    """Basic CHANGELOG for testing."""
    return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- New feature X
- New feature Y

### Changed

- Updated component Z

### Fixed

- Bug fix A
- Bug fix B

## [0.2.0] - 2024-06-15

### Added

- Old feature from 0.2.0
"""


class TestExtractUnreleasedContent:
    """Test extract_unreleased_content function."""

    def test_extract_simple_unreleased(self):
        """Test extracting content from Unreleased section."""
        changelog = """# Changelog

## Unreleased

### Added

- New feature A

### Fixed

- Bug fix B
"""
        sections = extract_unreleased_content(changelog)
        assert "Added" in sections
        assert "Fixed" in sections
        assert "New feature A" in sections["Added"]
        assert "Bug fix B" in sections["Fixed"]

    def test_extract_multiline_content(self):
        """Test extracting multiline bullets."""
        changelog = """# Changelog

## Unreleased

### Added

- Feature with multiple lines
  that span across
  multiple lines
- Another feature
"""
        sections = extract_unreleased_content(changelog)
        assert "Added" in sections
        assert "that span across" in sections["Added"]

    def test_extract_empty_sections(self):
        """Test that empty sections are not extracted."""
        changelog = """# Changelog

## Unreleased

### Added

- Feature A

### Changed

### Fixed

- Fix X
"""
        sections = extract_unreleased_content(changelog)
        assert "Added" in sections
        assert "Fixed" in sections
        assert "Changed" not in sections

    def test_extract_fails_no_unreleased(self):
        """Test that ValueError is raised if Unreleased section missing."""
        changelog = """# Changelog

## [1.0.0] - 2024-01-01
"""
        with pytest.raises(ValueError, match="No.*Unreleased"):
            extract_unreleased_content(changelog)

    def test_extract_with_following_version(self):
        """Test extraction when Unreleased is followed by version."""
        changelog = """# Changelog

## Unreleased

### Added

- Feature A

## [1.0.0] - 2024-01-01

### Added

- Old feature
"""
        sections = extract_unreleased_content(changelog)
        assert "Added" in sections
        assert "Feature A" in sections["Added"]
        assert "Old feature" not in sections["Added"]

    def test_extract_nested_bullets(self):
        """Test extraction of nested/indented bullets."""
        changelog = """# Changelog

## Unreleased

### Added

- Feature A
  - Sub-point 1
  - Sub-point 2
- Feature B
"""
        sections = extract_unreleased_content(changelog)
        assert "Added" in sections
        assert "Feature A" in sections["Added"]
        assert "Sub-point 1" in sections["Added"]


class TestCreateNewChangelog:
    """Test create_new_changelog function."""

    def test_create_basic(self):
        """Test creating basic changelog structure."""
        old_sections = {"Added": "- Feature A\n"}
        result = create_new_changelog("1.0.0", old_sections, "\n")

        assert "## Unreleased" in result
        assert "## [1.0.0] - TBD" in result
        assert "- Feature A" in result
        assert "### Added" in result
        assert "### Changed" in result
        assert "### Fixed" in result

    def test_create_multiple_sections(self):
        """Test changelog with multiple sections."""
        old_sections = {
            "Added": "- Feature A\n",
            "Fixed": "- Bug fix B\n",
        }
        result = create_new_changelog("2.0.0", old_sections, "\n")

        assert "## [2.0.0] - TBD" in result
        assert "- Feature A" in result
        assert "- Bug fix B" in result

    def test_create_empty_sections(self):
        """Test that empty old sections are not added."""
        old_sections = {}
        result = create_new_changelog("1.0.0", old_sections, "\n")

        assert "## [1.0.0] - TBD" in result
        assert "### Added" in result
        assert "### Changed" in result

    def test_create_preserves_rest_of_changelog(self):
        """Test that rest_of_changelog is preserved."""
        old_sections = {}
        rest = "\n## [0.9.0] - 2023-12-01\n\n### Added\n\n- Old feature\n"
        result = create_new_changelog("1.0.0", old_sections, rest)

        assert "## [0.9.0] - 2023-12-01" in result
        assert "Old feature" in result

    def test_create_ordering(self):
        """Test that Unreleased appears before version section."""
        old_sections = {"Added": "- Feature\n"}
        result = create_new_changelog("1.0.0", old_sections, "")

        unreleased_idx = result.index("## Unreleased")
        version_idx = result.index("## [1.0.0] - TBD")
        assert unreleased_idx < version_idx

    def test_create_contains_all_sections(self):
        """Test that all standard sections exist in result."""
        result = create_new_changelog("1.0.0", {}, "")

        for section in [
            "Added",
            "Changed",
            "Deprecated",
            "Removed",
            "Fixed",
            "Security",
        ]:
            assert f"### {section}" in result


class TestValidateChangelog:
    """Test validate_changelog function (file-based)."""

    def test_validate_with_content(self, tmp_path, basic_changelog):
        """Test validation succeeds with content in Unreleased."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        has_section, has_content = validate_changelog(str(changelog_file))

        assert has_section is True
        assert has_content is True

    def test_validate_fails_missing_unreleased(self, tmp_path):
        """Test validation fails if Unreleased section missing."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text("""# Changelog

## [1.0.0] - 2024-01-01
""")
        has_section, has_content = validate_changelog(str(changelog_file))

        assert has_section is False

    def test_validate_fails_empty_unreleased(self, tmp_path):
        """Test validation when Unreleased has no content."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text("""# Changelog

## Unreleased

### Added

### Fixed
""")
        has_section, has_content = validate_changelog(str(changelog_file))

        assert has_section is True
        assert has_content is False

    def test_validate_missing_file(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        missing_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError, match="CHANGELOG not found"):
            validate_changelog(str(missing_file))


class TestPrepareChangelog:
    """Test prepare_changelog function (full file-based workflow)."""

    def test_prepare_creates_version_section(self, tmp_path, basic_changelog):
        """Test that prepare_changelog creates a version section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        prepare_changelog("1.0.0", str(changelog_file))

        result = changelog_file.read_text()
        assert "## [1.0.0] - TBD" in result
        assert "- New feature X" in result
        assert "- New feature Y" in result
        assert "- Updated component Z" in result
        assert "- Bug fix A" in result
        assert "- Bug fix B" in result

    def test_prepare_creates_fresh_unreleased(self, tmp_path, basic_changelog):
        """Test that prepare_changelog creates fresh Unreleased section."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        prepare_changelog("1.0.0", str(changelog_file))

        result = changelog_file.read_text()
        # Count unreleased sections
        unreleased_count = result.count("## Unreleased")
        assert unreleased_count == 1
        # Unreleased should come before version
        assert result.index("## Unreleased") < result.index("## [1.0.0]")

    def test_prepare_removes_empty_subsections(self, tmp_path):
        """Test that empty subsections from version are removed."""
        changelog = """# Changelog

## Unreleased

### Added

- Feature A

### Changed

### Fixed

"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        prepare_changelog("1.0.0", str(changelog_file))

        result = changelog_file.read_text()
        # Find the version section - look between first [1.0.0] and next ##
        version_start = result.find("## [1.0.0]")
        next_heading = result.find("\n## ", version_start + 1)
        if next_heading == -1:
            version_section = result[version_start:]
        else:
            version_section = result[version_start:next_heading]

        # Only Added should be in version (Changed and Fixed were empty)
        assert "### Added" in version_section
        assert "- Feature A" in version_section
        # Changed and Fixed should not appear in this version section
        assert (
            "### Changed" not in version_section
            or version_section.find("### Changed") < 0
        )
        assert (
            "### Fixed" not in version_section or version_section.find("### Fixed") < 0
        )

    def test_prepare_preserves_previous_versions(self, tmp_path, basic_changelog):
        """Test that previous versions are preserved."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        prepare_changelog("1.0.0", str(changelog_file))

        result = changelog_file.read_text()
        assert "## [0.2.0] - 2024-06-15" in result
        assert "Old feature from 0.2.0" in result

    def test_prepare_rejects_invalid_semver(self, tmp_path, basic_changelog):
        """Test that prepare_changelog rejects invalid semver."""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(basic_changelog)

        with pytest.raises(ValueError, match="Invalid semantic version"):
            prepare_changelog("1.0.0.4", str(changelog_file))

        with pytest.raises(ValueError, match="Invalid semantic version"):
            prepare_changelog("v1.0.0", str(changelog_file))

    def test_prepare_fails_missing_changelog(self, tmp_path):
        """Test that FileNotFoundError is raised for missing CHANGELOG."""
        missing_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError, match="CHANGELOG not found"):
            prepare_changelog("1.0.0", str(missing_file))


class TestResetUnreleased:
    """Test reset_unreleased function."""

    def test_reset_creates_unreleased(self, tmp_path):
        """Test that reset_unreleased creates fresh Unreleased section."""
        changelog = """# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-01

### Added

- Feature A
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        reset_unreleased(str(changelog_file))

        result = changelog_file.read_text()
        assert "## Unreleased" in result
        assert result.index("## Unreleased") < result.index("## [1.0.0]")

    def test_reset_fails_if_unreleased_exists(self, tmp_path):
        """Test that reset fails if Unreleased already exists."""
        changelog = """# Changelog

## Unreleased

### Added

## [1.0.0] - 2024-01-01
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        with pytest.raises(ValueError, match="already exists"):
            reset_unreleased(str(changelog_file))

    def test_reset_preserves_versions(self, tmp_path):
        """Test that reset preserves existing version sections."""
        changelog = """# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-01

### Added

- Feature A

## [0.9.0] - 2023-12-01

### Added

- Old feature
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        reset_unreleased(str(changelog_file))

        result = changelog_file.read_text()
        assert "## [1.0.0]" in result
        assert "## [0.9.0]" in result
        assert "Feature A" in result
        assert "Old feature" in result


class TestFinalizeReleaseDate:
    """Test finalize_release_date function."""

    def test_finalize_replaces_tbd(self, tmp_path):
        """Test that finalize_release_date replaces TBD with date."""
        changelog = """# Changelog

## [1.0.0] - TBD

### Added

- Feature A
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        finalize_release_date("1.0.0", "2024-12-15", str(changelog_file))

        result = changelog_file.read_text()
        assert "## [1.0.0] - 2024-12-15" in result
        assert "TBD" not in result

    def test_finalize_fails_version_not_found(self, tmp_path):
        """Test that finalize fails if version not found."""
        changelog = """# Changelog

## [1.0.0] - TBD
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        with pytest.raises(ValueError, match="not found"):
            finalize_release_date("2.0.0", "2024-12-15", str(changelog_file))

    def test_finalize_fails_invalid_date(self, tmp_path):
        """Test that finalize fails if date format is invalid."""
        changelog = """# Changelog

## [1.0.0] - TBD
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        with pytest.raises(ValueError, match="Invalid date"):
            finalize_release_date("1.0.0", "12-15-2024", str(changelog_file))

    def test_finalize_fails_already_finalized(self, tmp_path):
        """Test that finalize fails if version already has a date."""
        changelog = """# Changelog

## [1.0.0] - 2024-01-01
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        with pytest.raises(ValueError, match="not found"):
            finalize_release_date("1.0.0", "2024-12-15", str(changelog_file))

    def test_finalize_missing_file(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        missing_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError, match="CHANGELOG not found"):
            finalize_release_date("1.0.0", "2024-12-15", str(missing_file))

    def test_finalize_handles_multiple_tbd_versions(self, tmp_path):
        """Test finalize when multiple versions have TBD (only targets specific version)."""
        changelog = """# Changelog

## [2.0.0] - TBD

### Added

- Feature for 2.0

## [1.5.0] - TBD

### Added

- Feature for 1.5
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        finalize_release_date("1.5.0", "2024-06-15", str(changelog_file))

        result = changelog_file.read_text()
        assert "## [1.5.0] - 2024-06-15" in result
        assert "## [2.0.0] - TBD" in result  # 2.0.0 should still have TBD

    def test_finalize_preserves_content(self, tmp_path):
        """Test that finalize preserves all content."""
        changelog = """# Changelog

## [1.0.0] - TBD

### Added

- Feature A with special chars: (parentheses) [brackets]

### Fixed

- Bug fix
"""
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(changelog)

        finalize_release_date("1.0.0", "2024-12-15", str(changelog_file))

        result = changelog_file.read_text()
        assert "- Feature A with special chars: (parentheses) [brackets]" in result
        assert "- Bug fix" in result
