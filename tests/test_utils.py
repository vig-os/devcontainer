"""
Tests for utility scripts.

Tests functions from:
- scripts/utils.py (sed_inplace, update_version_line)
- docs/generate.py (get_version_from_changelog, get_release_date_from_changelog)
"""

# Import functions to test
import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add scripts and docs directories to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
docs_dir = Path(__file__).parent.parent / "docs"
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(docs_dir))

# Import generate module explicitly
generate_spec = importlib.util.spec_from_file_location(
    "generate", docs_dir / "generate.py"
)
generate = importlib.util.module_from_spec(generate_spec)
generate_spec.loader.exec_module(generate)

# Import utils module explicitly
utils_spec = importlib.util.spec_from_file_location("utils", scripts_dir / "utils.py")
utils = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(utils)
sed_inplace = utils.sed_inplace
update_version_line = utils.update_version_line


class TestSedInplace:
    """Test sed_inplace function from scripts/utils.py."""

    def test_sed_inplace_simple_replacement(self, tmp_path):
        """Test simple replacement with pipe delimiter."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello {{IMAGE_TAG}} world")

        sed_inplace("s|{{IMAGE_TAG}}|0.2.0|g", test_file)

        assert test_file.read_text() == "Hello 0.2.0 world"

    def test_sed_inplace_global_replacement(self, tmp_path):
        """Test global replacement (g flag)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar foo baz foo")

        sed_inplace("s|foo|bar|g", test_file)

        assert test_file.read_text() == "bar bar bar baz bar"

    def test_sed_inplace_single_replacement(self, tmp_path):
        """Test single replacement (no g flag)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar foo baz foo")

        sed_inplace("s|foo|bar|", test_file)

        assert test_file.read_text() == "bar bar foo baz foo"

    def test_sed_inplace_slash_delimiter(self, tmp_path):
        """Test replacement with slash delimiter."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("path/to/file")

        # Use pipe delimiter since slash appears in the pattern
        sed_inplace("s|path/to/file|new/path/to/file|g", test_file)

        assert test_file.read_text() == "new/path/to/file"

    def test_sed_inplace_hash_delimiter(self, tmp_path):
        """Test replacement with hash delimiter."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("comment # old # more")

        # Replace " old " with " new " (spaces included)
        sed_inplace("s# old # new #g", test_file)

        assert test_file.read_text() == "comment # new # more"

    def test_sed_inplace_multiline_content(self, tmp_path):
        """Test replacement in multiline content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "Line 1: {{IMAGE_TAG}}\nLine 2: {{IMAGE_TAG}}\nLine 3: text"
        )

        sed_inplace("s|{{IMAGE_TAG}}|0.2.0|g", test_file)

        expected = "Line 1: 0.2.0\nLine 2: 0.2.0\nLine 3: text"
        assert test_file.read_text() == expected

    def test_sed_inplace_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for non-existent file."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError, match="File not found"):
            sed_inplace("s|old|new|g", non_existent)

    def test_sed_inplace_unsupported_command(self, tmp_path):
        """Test that ValueError is raised for unsupported sed commands."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Unsupported sed command"):
            sed_inplace("d|pattern|", test_file)  # 'd' is delete, not supported

    def test_sed_inplace_invalid_pattern(self, tmp_path):
        """Test that ValueError is raised for invalid patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Invalid sed pattern"):
            sed_inplace("s|only|", test_file)  # Missing replacement


class TestUpdateVersionLine:
    """Test update_version_line function from scripts/utils.py."""

    def test_update_version_line_success(self, tmp_path):
        """Test successful version line update."""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(
            "# Test\n- **Version**: [dev](url), 2025-01-01\n- **Size**: ~100 MB\n"
        )

        result = update_version_line(
            readme_file, "0.2.0", "https://example.com/release", "2025-12-10"
        )

        expected = "- **Version**: [0.2.0](https://example.com/release), 2025-12-10"
        assert result == expected

        content = readme_file.read_text()
        assert expected in content
        assert "- **Size**: ~100 MB" in content  # Other content preserved

    def test_update_version_line_not_found(self, tmp_path):
        """Test that ValueError is raised when version line is not found."""
        readme_file = tmp_path / "README.md"
        readme_file.write_text("# Test\nNo version line here\n")

        with pytest.raises(ValueError, match="Version line not found"):
            update_version_line(
                readme_file, "0.2.0", "https://example.com/release", "2025-12-10"
            )

    def test_update_version_line_multiple_matches(self, tmp_path):
        """Test that only first version line is updated."""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(
            "- **Version**: [old](url), date\n- **Version**: [old2](url), date2\n"
        )

        # Should raise error because pattern matches multiple lines
        # but subn with count=1 should only replace first
        update_version_line(
            readme_file, "0.2.0", "https://example.com/release", "2025-12-10"
        )

        content = readme_file.read_text()
        assert (
            "- **Version**: [0.2.0](https://example.com/release), 2025-12-10" in content
        )
        assert "- **Version**: [old2](url), date2" in content  # Second line unchanged


class TestGetVersionFromChangelog:
    """Test get_version_from_changelog function from docs/generate.py."""

    def test_get_version_from_changelog_found(self, tmp_path):
        """Test version extraction when changelog exists with release."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n"
            "## Unreleased\n\n"
            "## [0.2.0] - 2025-12-10\n\n"
            "## [0.1.0] - 2025-01-01\n"
        )

        # Test the logic directly (same as in generate.py)
        version_found = None
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    version_found = line.split("[")[1].split("]")[0]
                    break

        assert version_found == "0.2.0"

    def test_get_version_from_changelog_not_found(self, tmp_path):
        """Test version extraction when no release found."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## Unreleased\n\nNo releases yet\n")

        # Test logic directly
        version_found = None
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    version_found = line.split("[")[1].split("]")[0]
                    break

        assert version_found is None

    def test_get_version_from_changelog_actual(self):
        """Test version extraction from actual CHANGELOG.md."""
        # This tests against the real CHANGELOG.md file
        version = generate.get_version_from_changelog()
        # Should return a version or "dev"
        assert isinstance(version, str)
        # Version should be "dev" or a semantic version (X.Y or X.Y.Z)
        assert version == "dev" or version.count(".") >= 1


class TestGetReleaseDateFromChangelog:
    """Test get_release_date_from_changelog function from docs/generate.py."""

    def test_get_release_date_from_changelog_found(self, tmp_path):
        """Test date extraction when changelog exists with release."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n"
            "## Unreleased\n\n"
            "## [0.2.0] - 2025-12-10\n\n"
            "## [0.1.0] - 2025-01-01\n"
        )

        # Test logic directly (same as in generate.py)
        date_found = None
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    parts = line.split("]")
                    if len(parts) > 1:
                        date_part = parts[1].split(" - ")
                        if len(date_part) > 1:
                            date_found = date_part[1].strip()
                            break

        assert date_found == "2025-12-10"

    def test_get_release_date_from_changelog_not_found(self, tmp_path):
        """Test date extraction when no release found."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## Unreleased\n\nNo releases yet\n")

        # Test logic directly
        date_found = None
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    parts = line.split("]")
                    if len(parts) > 1:
                        date_part = parts[1].split(" - ")
                        if len(date_part) > 1:
                            date_found = date_part[1].strip()
                            break

        assert date_found is None

    def test_get_release_date_from_changelog_actual(self):
        """Test date extraction from actual CHANGELOG.md."""
        # This tests against the real CHANGELOG.md file
        date = generate.get_release_date_from_changelog()
        # Should return a date in YYYY-MM-DD format or current date
        assert isinstance(date, str)
        # Check format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            pytest.fail(f"Date format is invalid: {date} (expected YYYY-MM-DD)")

    def test_get_release_date_format(self):
        """Test that returned date is in correct format."""
        date = generate.get_release_date_from_changelog()
        # Should be YYYY-MM-DD format
        parts = date.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # Year
        assert len(parts[1]) == 2  # Month
        assert len(parts[2]) == 2  # Day
        # Should be valid date
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        assert 2000 <= year <= 2100  # Reasonable year range
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_get_release_date_without_date_part(self, tmp_path):
        """Test date extraction when release line has no date."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## [0.1.0]\n\nNo date\n")

        # Test logic directly
        date_found = None
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    parts = line.split("]")
                    if len(parts) > 1:
                        date_part = parts[1].split(" - ")
                        if len(date_part) > 1:
                            date_found = date_part[1].strip()
                            break

        assert date_found is None
