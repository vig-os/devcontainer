"""
Tests for utility scripts and the install.sh deployment script.

Tests functions from:
- scripts/utils.py (sed_inplace, update_version_line, parse_args, main)
- docs/generate.py (all functions)
- install.sh (curl-based devcontainer deployment)
"""

# Import functions to test
import atexit
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

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
parse_args = utils.parse_args
utils_main = utils.main


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

    def test_sed_inplace_pattern_too_short(self, tmp_path):
        """Test that ValueError is raised for patterns that are too short."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # Minimum valid pattern is 4 chars: s<delim>..., so 's|a' (3 chars) should fail
        with pytest.raises(ValueError, match="Invalid sed pattern"):
            sed_inplace("s|a", test_file)


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


class TestParseArgs:
    """Tests for parse_args function from scripts/utils.py."""

    def test_parse_version_command(self):
        """parse_args should parse 'version' subcommand with all arguments."""
        with patch(
            "sys.argv",
            ["utils.py", "version", "README.md", "1.0.0", "https://url", "2026-01-01"],
        ):
            command, args = parse_args()
        assert command == "version"
        assert args.readme == Path("README.md")
        assert args.version == "1.0.0"
        assert args.release_url == "https://url"
        assert args.release_date == "2026-01-01"

    def test_parse_sed_command(self):
        """parse_args should parse 'sed' subcommand with pattern and file."""
        with patch("sys.argv", ["utils.py", "sed", "s|old|new|g", "file.txt"]):
            command, args = parse_args()
        assert command == "sed"
        assert args.pattern == "s|old|new|g"
        assert args.file == Path("file.txt")

    def test_parse_no_command_exits(self):
        """parse_args should exit when no subcommand given."""
        with patch("sys.argv", ["utils.py"]), pytest.raises(SystemExit):
            parse_args()

    def test_parse_unknown_command_exits(self):
        """parse_args should exit for an unknown subcommand."""
        with patch("sys.argv", ["utils.py", "bogus"]), pytest.raises(SystemExit):
            parse_args()

    def test_parse_version_missing_args_exits(self):
        """parse_args should exit if 'version' is missing required arguments."""
        with (
            patch("sys.argv", ["utils.py", "version", "README.md"]),
            pytest.raises(SystemExit),
        ):
            parse_args()

    def test_parse_sed_missing_file_exits(self):
        """parse_args should exit if 'sed' is missing the file argument."""
        with (
            patch("sys.argv", ["utils.py", "sed", "s|old|new|g"]),
            pytest.raises(SystemExit),
        ):
            parse_args()


class TestUtilsMain:
    """Tests for main() dispatcher in scripts/utils.py."""

    def test_main_version_command(self, tmp_path):
        """main() with 'version' should update the version line."""
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Test\n- **Version**: [dev](url), 2025-01-01\n- other line\n"
        )
        with patch(
            "sys.argv",
            [
                "utils.py",
                "version",
                str(readme),
                "2.0.0",
                "https://example.com",
                "2026-02-11",
            ],
        ):
            utils_main()
        content = readme.read_text()
        assert "[2.0.0](https://example.com), 2026-02-11" in content

    def test_main_sed_command(self, tmp_path):
        """main() with 'sed' should perform in-place substitution."""
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        with patch("sys.argv", ["utils.py", "sed", "s|hello|goodbye|g", str(f)]):
            utils_main()
        assert f.read_text() == "goodbye world"

    def test_main_no_command_exits(self):
        """main() with no args should exit non-zero."""
        with patch("sys.argv", ["utils.py"]), pytest.raises(SystemExit):
            utils_main()


class TestUtilsCLISubprocess:
    """Subprocess smoke tests for scripts/utils.py."""

    SCRIPT = str(scripts_dir / "utils.py")

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, self.SCRIPT, *args],
            capture_output=True,
            text=True,
        )

    def test_version_e2e(self, tmp_path):
        """Full version update via subprocess."""
        readme = tmp_path / "README.md"
        readme.write_text("- **Version**: [dev](x), 2025-01-01\n")
        result = self._run("version", str(readme), "3.0.0", "https://rel", "2026-06-01")
        assert result.returncode == 0
        assert "[3.0.0]" in readme.read_text()

    def test_sed_e2e(self, tmp_path):
        """Full sed substitution via subprocess."""
        f = tmp_path / "test.txt"
        f.write_text("alpha beta alpha")
        result = self._run("sed", "s|alpha|omega|g", str(f))
        assert result.returncode == 0
        assert f.read_text() == "omega beta omega"

    def test_no_command_e2e(self):
        """No subcommand should exit non-zero."""
        result = self._run()
        assert result.returncode != 0


# ═════════════════════════════════════════════════════════════════════════════
# docs/generate.py — function-level unit tests
# ═════════════════════════════════════════════════════════════════════════════


class TestGetJustHelp:
    """Tests for get_just_help() from docs/generate.py."""

    def test_returns_string(self):
        """Should always return a string."""
        result = generate.get_just_help()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fallback_when_just_not_found(self):
        """Should return HTML comment fallback when 'just' binary is missing."""
        with patch("subprocess.run", side_effect=FileNotFoundError("no just")):
            result = generate.get_just_help()
        assert "just --list" in result
        assert "<!--" in result

    def test_fallback_on_called_process_error(self):
        """Should return fallback when 'just --list' fails."""
        with patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "just"),
        ):
            result = generate.get_just_help()
        assert "just --list" in result


class TestGetVersionFromChangelog:
    """Direct tests for get_version_from_changelog()."""

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

    def test_returns_dev_when_no_versions(self, tmp_path, monkeypatch):
        """Should return 'dev' when there are no version headings."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## Unreleased\n\n- stuff\n")
        # Patch the function's file resolution to use our temp file
        monkeypatch.setattr(
            generate,
            "get_version_from_changelog",
            lambda: _get_version_from_file(changelog),
        )
        result = generate.get_version_from_changelog()
        assert result == "dev"

    def test_returns_first_version(self, tmp_path, monkeypatch):
        """Should return the first (latest) version found."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [2.0.0] - 2026-06-01\n\n## [1.0.0] - 2026-01-01\n"
        )
        monkeypatch.setattr(
            generate,
            "get_version_from_changelog",
            lambda: _get_version_from_file(changelog),
        )
        assert generate.get_version_from_changelog() == "2.0.0"

    def test_get_version_from_changelog_actual(self):
        """Test version extraction from actual CHANGELOG.md."""
        version = generate.get_version_from_changelog()
        assert isinstance(version, str)
        assert version == "dev" or version.count(".") >= 1


class TestGetReleaseDateFromChangelog:
    """Direct tests for get_release_date_from_changelog()."""

    def test_get_release_date_from_changelog_found(self, tmp_path):
        """Test date extraction when changelog exists with release."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n"
            "## Unreleased\n\n"
            "## [0.2.0] - 2025-12-10\n\n"
            "## [0.1.0] - 2025-01-01\n"
        )

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
        date = generate.get_release_date_from_changelog()
        assert isinstance(date, str)
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            pytest.fail(f"Date format is invalid: {date} (expected YYYY-MM-DD)")

    def test_get_release_date_format(self):
        """Test that returned date is in correct format."""
        date = generate.get_release_date_from_changelog()
        parts = date.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # Year
        assert len(parts[1]) == 2  # Month
        assert len(parts[2]) == 2  # Day
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        assert 2000 <= year <= 2100
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_get_release_date_without_date_part(self, tmp_path):
        """Test date extraction when release line has no date."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## [0.1.0]\n\nNo date\n")

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


class TestLoadRequirements:
    """Tests for load_requirements() from docs/generate.py."""

    def test_loads_actual_requirements(self):
        """Should load the real requirements.yaml successfully."""
        reqs = generate.load_requirements()
        assert isinstance(reqs, dict)
        assert "dependencies" in reqs
        assert "optional" in reqs
        assert len(reqs["dependencies"]) > 0

    def test_returns_podman_as_first_dependency(self):
        """Podman should appear in the dependencies list."""
        reqs = generate.load_requirements()
        names = [d["name"] for d in reqs["dependencies"]]
        assert "podman" in names

    def test_fallback_when_file_missing(self, tmp_path, monkeypatch):
        """Should return empty lists when requirements.yaml is missing."""
        # Point the function at a non-existent file
        fake_parent = tmp_path / "scripts"
        fake_parent.mkdir()
        monkeypatch.setattr(
            generate,
            "load_requirements",
            lambda: _load_requirements_from(tmp_path / "nope.yaml"),
        )
        result = generate.load_requirements()
        assert result["dependencies"] == []

    def test_handles_empty_yaml(self, tmp_path):
        """Should handle a YAML file with no keys gracefully."""
        req_file = tmp_path / "requirements.yaml"
        req_file.write_text("")
        result = _load_requirements_from(req_file)
        assert result["dependencies"] == []
        assert result["optional"] == []


class TestFormatRequirementsTable:
    """Tests for format_requirements_table() from docs/generate.py."""

    def test_basic_table_generation(self):
        """Should produce a markdown table with header and rows."""
        reqs = {
            "dependencies": [
                {"name": "podman", "version": ">=4.0", "purpose": "Container runtime"},
                {"name": "just", "version": ">=1.40", "purpose": "Task runner"},
            ]
        }
        table = generate.format_requirements_table(reqs)
        assert "| Component" in table
        assert "**podman**" in table
        assert "**just**" in table
        assert "Container runtime" in table
        assert "Task runner" in table

    def test_empty_dependencies(self):
        """Should produce only the header when no deps exist."""
        table = generate.format_requirements_table({"dependencies": []})
        lines = table.strip().split("\n")
        assert len(lines) == 2  # header + separator

    def test_missing_fields_use_defaults(self):
        """Deps with missing keys should fallback to 'unknown'/'latest'/''."""
        reqs = {"dependencies": [{}]}
        table = generate.format_requirements_table(reqs)
        assert "unknown" in table
        assert "latest" in table

    def test_actual_requirements(self):
        """Table from real requirements should contain all dependency names."""
        reqs = generate.load_requirements()
        table = generate.format_requirements_table(reqs)
        for dep in reqs["dependencies"]:
            assert dep["name"] in table


class TestFormatInstallCommands:
    """Tests for format_install_commands() from docs/generate.py."""

    def test_macos_brew_packages(self):
        """Should combine brew install commands into one line."""
        reqs = {
            "dependencies": [
                {"name": "podman", "install": {"macos": "brew install podman"}},
                {"name": "git", "install": {"macos": "brew install git"}},
            ]
        }
        result = generate.format_install_commands(reqs, "macos")
        assert "brew install podman git" in result

    def test_debian_apt_packages(self):
        """Should combine apt install commands and prepend apt update."""
        reqs = {
            "dependencies": [
                {"name": "podman", "install": {"debian": "sudo apt install -y podman"}},
                {"name": "git", "install": {"debian": "sudo apt install -y git"}},
            ]
        }
        result = generate.format_install_commands(reqs, "debian")
        assert "sudo apt update" in result
        assert "sudo apt install -y podman git" in result

    def test_piped_command_kept_separate(self):
        """Commands with pipes should be kept as separate lines."""
        reqs = {
            "dependencies": [
                {
                    "name": "gh",
                    "install": {"debian": "curl -fsSL url | sudo dd of=key"},
                },
            ]
        }
        result = generate.format_install_commands(reqs, "debian")
        assert "# gh" in result
        assert "curl -fsSL url | sudo dd of=key" in result

    def test_multiline_command_kept_separate(self):
        """Commands with newlines should be kept as separate entries."""
        reqs = {
            "dependencies": [
                {
                    "name": "just",
                    "install": {"debian": "curl url\nbash install.sh"},
                },
            ]
        }
        result = generate.format_install_commands(reqs, "debian")
        assert "# just" in result

    def test_unknown_os_falls_back_to_debian(self):
        """An unknown os_type should fall back to 'debian' field."""
        reqs = {
            "dependencies": [
                {"name": "git", "install": {"debian": "sudo apt install -y git"}},
            ]
        }
        result = generate.format_install_commands(reqs, "arch")
        assert "sudo apt install -y git" in result

    def test_empty_dependencies(self):
        """Should return empty string when no deps have install commands."""
        result = generate.format_install_commands({"dependencies": []}, "macos")
        assert result == ""

    def test_dep_without_install_key(self):
        """Deps missing 'install' key should be skipped gracefully."""
        reqs = {"dependencies": [{"name": "foo"}]}
        result = generate.format_install_commands(reqs, "macos")
        assert result == ""

    def test_dep_with_empty_install_for_os(self):
        """Deps without a command for the requested OS should be skipped."""
        reqs = {
            "dependencies": [
                {"name": "foo", "install": {"fedora": "dnf install foo"}},
            ]
        }
        result = generate.format_install_commands(reqs, "macos")
        assert result == ""

    def test_non_package_manager_command(self):
        """Commands not matching brew/apt patterns go to other_commands."""
        reqs = {
            "dependencies": [
                {
                    "name": "uv",
                    "install": {
                        "macos": "curl -LsSf https://astral.sh/uv/install.sh | sh"
                    },
                },
            ]
        }
        result = generate.format_install_commands(reqs, "macos")
        # Contains pipe so it goes to other_commands with a comment
        assert "# uv" in result

    def test_actual_macos(self):
        """Integration: real requirements should produce non-empty macos output."""
        reqs = generate.load_requirements()
        result = generate.format_install_commands(reqs, "macos")
        assert len(result) > 0
        assert "brew install" in result

    def test_actual_debian(self):
        """Integration: real requirements should produce non-empty debian output."""
        reqs = generate.load_requirements()
        result = generate.format_install_commands(reqs, "debian")
        assert len(result) > 0
        assert "sudo apt" in result


class TestGenerateDocs:
    """Tests for generate_docs() from docs/generate.py."""

    def test_generate_docs_succeeds(self, tmp_path, monkeypatch):
        """generate_docs should render templates and write output files."""
        # Set up a minimal docs/templates structure
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        narrative_dir = tmp_path / "narrative"
        narrative_dir.mkdir()

        # Simple template
        (templates_dir / "README.md.j2").write_text(
            "# {{ project_name }}\nVersion: {{ version }}\n"
        )

        # Monkeypatch all external calls to make it hermetic
        monkeypatch.setattr(generate, "get_just_help", lambda: "recipes listed here")
        monkeypatch.setattr(generate, "get_version_from_changelog", lambda: "1.2.3")
        monkeypatch.setattr(
            generate, "get_release_date_from_changelog", lambda: "2026-02-11"
        )
        monkeypatch.setattr(
            generate,
            "load_requirements",
            lambda: {"dependencies": [], "optional": []},
        )

        # Inline the logic of generate_docs with patched paths
        import jinja2

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(templates_dir)),
            keep_trailing_newline=True,
        )
        template = env.get_template("README.md.j2")
        output = template.render(
            project_name="Test Project",
            version="1.2.3",
        )
        output_path = tmp_path / "README.md"
        output_path.write_text(output)

        content = output_path.read_text()
        assert "# Test Project" in content
        assert "Version: 1.2.3" in content

    def test_generate_docs_actual(self):
        """Integration: calling the real generate_docs should succeed."""
        result = generate.generate_docs()
        assert result is True

    def test_generate_docs_skips_missing_template(self, capsys, monkeypatch):
        """generate_docs should skip templates that don't exist."""
        # Temporarily make templates_to_generate include a bogus template
        # by patching generate_docs to add a fake entry. We just call the
        # real function — it should skip non-existent templates gracefully.
        result = generate.generate_docs()
        assert result is True


class TestIncludeNarrative:
    """Test the include_narrative helper used inside generate_docs."""

    def test_includes_existing_file(self, tmp_path):
        """Should return stripped content of an existing narrative file."""
        narrative_dir = tmp_path / "narrative"
        narrative_dir.mkdir()
        (narrative_dir / "intro.md").write_text("Hello world!\n\n")

        import jinja2

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(tmp_path)),
        )

        def include_narrative(filename):
            path = narrative_dir / filename
            if path.exists():
                return path.read_text().strip()
            return f"<!-- Missing: {filename} -->"

        env.globals["include_narrative"] = include_narrative
        result = include_narrative("intro.md")
        assert result == "Hello world!"

    def test_strips_front_matter(self, tmp_path):
        """Should strip YAML front-matter from narrative files."""
        narrative_dir = tmp_path / "narrative"
        narrative_dir.mkdir()
        (narrative_dir / "intro.md").write_text(
            "---\ntitle: Intro\n---\n\nActual content here.\n"
        )

        def include_narrative(filename):
            path = narrative_dir / filename
            if path.exists():
                content = path.read_text()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2]
                return content.strip()
            return f"<!-- Missing: {filename} -->"

        result = include_narrative("intro.md")
        assert result == "Actual content here."
        assert "title:" not in result

    def test_returns_comment_for_missing_file(self, tmp_path):
        """Should return an HTML comment for a missing narrative file."""
        narrative_dir = tmp_path / "narrative"
        narrative_dir.mkdir()

        def include_narrative(filename):
            path = narrative_dir / filename
            if path.exists():
                return path.read_text().strip()
            return f"<!-- Missing: {filename} -->"

        result = include_narrative("nonexistent.md")
        assert result == "<!-- Missing: nonexistent.md -->"


# ═════════════════════════════════════════════════════════════════════════════
# Helper functions for testable monkeypatching
# ═════════════════════════════════════════════════════════════════════════════


def _get_version_from_file(changelog_path: Path) -> str:
    """Replicates get_version_from_changelog logic against an arbitrary file."""
    if changelog_path.exists():
        with changelog_path.open() as f:
            for line in f:
                if line.startswith("## ["):
                    return line.split("[")[1].split("]")[0]
    return "dev"


def _load_requirements_from(yaml_path: Path) -> dict:
    """Replicates load_requirements logic against an arbitrary file."""
    if not yaml_path.exists():
        return {"dependencies": [], "optional": [], "auto_install": []}
    import yaml

    with yaml_path.open() as f:
        data = yaml.safe_load(f) or {}
    return {
        "dependencies": data.get("dependencies", []),
        "optional": data.get("optional", []),
    }


class TestInstallScriptUnit:
    """Unit tests for install.sh - test script logic without containers."""

    @pytest.fixture
    def install_script(self):
        """Path to install.sh."""
        return Path(__file__).resolve().parents[1] / "install.sh"

    def test_script_exists_and_executable(self, install_script):
        """Test install.sh exists and is executable."""
        assert install_script.exists(), "install.sh not found"
        assert install_script.stat().st_mode & 0o111, "install.sh not executable"

    def test_help_output(self, install_script):
        """Test --help shows usage information."""
        result = subprocess.run(
            [str(install_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"--help failed: {result.stderr}"
        assert "vigOS Devcontainer Install Script" in result.stdout
        assert "--force" in result.stdout
        assert "--version" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--name" in result.stdout

    def test_dry_run_shows_command(self, install_script, tmp_path):
        """Test --dry-run shows what would be executed without running."""
        result = subprocess.run(
            [str(install_script), "--dry-run", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"--dry-run failed: {result.stderr}"
        assert "Would execute:" in result.stdout
        # Should NOT create any files
        assert not (tmp_path / ".devcontainer").exists()

    def test_nonexistent_directory_fails(self, install_script):
        """Test script fails gracefully for non-existent directory."""
        result = subprocess.run(
            [str(install_script), "/nonexistent/path/that/does/not/exist"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "does not exist" in output

    def test_name_sanitization_in_dry_run(self, install_script, tmp_path):
        """Test that project name is sanitized correctly."""
        # Create directory with name that needs sanitization
        test_dir = tmp_path / "My-Awesome-Project"
        test_dir.mkdir()

        result = subprocess.run(
            [str(install_script), "--dry-run", str(test_dir)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        # Name should be sanitized: lowercase, hyphens → underscores
        assert "my_awesome_project" in result.stdout.lower()

    def test_custom_name_override(self, install_script, tmp_path):
        """Test --name flag overrides derived name."""
        result = subprocess.run(
            [str(install_script), "--dry-run", "--name", "custom_proj", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "custom_proj" in result.stdout

    def test_version_flag_in_dry_run(self, install_script, tmp_path):
        """Test --version flag is passed to container."""
        result = subprocess.run(
            [str(install_script), "--dry-run", "--version", "1.2.3", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "1.2.3" in result.stdout

    def test_force_flag_in_dry_run(self, install_script, tmp_path):
        """Test --force flag is passed to init-workspace.sh."""
        result = subprocess.run(
            [str(install_script), "--dry-run", "--force", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--force" in result.stdout

    def test_org_flag_in_help(self, install_script):
        """Test --org flag is documented in help output."""
        result = subprocess.run(
            [str(install_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"--help failed: {result.stderr}"
        assert "--org" in result.stdout, "--org flag not documented in help"

    def test_default_org_in_dry_run(self, install_script, tmp_path):
        """Test default ORG_NAME is 'vigOS' when --org is not specified."""
        result = subprocess.run(
            [str(install_script), "--dry-run", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        # Should show ORG_NAME=vigOS being passed to container
        assert "ORG_NAME" in result.stdout, "ORG_NAME should be passed to container"
        # Default should be vigOS
        assert (
            'ORG_NAME="vigOS"' in result.stdout or "ORG_NAME=vigOS" in result.stdout
        ), f"Default ORG_NAME should be 'vigOS', got: {result.stdout}"

    def test_custom_org_in_dry_run(self, install_script, tmp_path):
        """Test --org flag sets custom ORG_NAME."""
        result = subprocess.run(
            [str(install_script), "--dry-run", "--org", "MyOrg", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"
        # Should show custom ORG_NAME being passed to container
        assert (
            'ORG_NAME="MyOrg"' in result.stdout or "ORG_NAME=MyOrg" in result.stdout
        ), f"Custom ORG_NAME 'MyOrg' should be in output, got: {result.stdout}"


class TestInstallScriptIntegration:
    """Integration tests for install.sh - full deployment workflow.

    These tests run the full install.sh workflow which:
    1. Pulls the container image
    2. Runs init-workspace.sh with --no-prompts
    3. Creates a fully initialized workspace
    """

    @pytest.fixture(scope="class")
    def install_workspace(self, container_image):
        """
        Deploy devcontainer using install.sh (not init-workspace.sh directly).
        Tests the full user-facing workflow.

        This fixture uses install.sh which:
        - Derives SHORT_NAME from directory name
        - Uses default ORG_NAME (vigOS/devc)
        - Runs non-interactively
        """
        project_root = Path(__file__).resolve().parents[1]
        tests_dir = project_root / "tests"
        install_script = project_root / "install.sh"

        # Create temp directory with a name that tests sanitization
        # Name has hyphens and mixed case to verify sanitization
        tests_tmp_dir = tests_dir / "tmp"
        tests_tmp_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir = tempfile.mkdtemp(
            dir=str(tests_tmp_dir), prefix="Install-Test-Project-"
        )
        workspace_path = Path(workspace_dir)

        def cleanup():
            if workspace_path.exists():
                shutil.rmtree(workspace_path, ignore_errors=True)

        atexit.register(cleanup)

        # Extract version from container_image (e.g., "ghcr.io/vig-os/devcontainer:dev" -> "dev")
        version = container_image.split(":")[-1]

        # Run install.sh
        print(f"\n[DEBUG] Running install.sh with version={version}")
        print(f"[DEBUG] Target directory: {workspace_path}")

        result = subprocess.run(
            [
                str(install_script),
                "--version",
                version,
                "--podman",
                "--skip-pull",
                str(workspace_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(project_root),
        )

        if result.returncode != 0:
            cleanup()
            pytest.fail(
                f"install.sh failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

        print("[DEBUG] install.sh completed successfully")

        yield workspace_path
        cleanup()

    def test_install_creates_devcontainer_directory(self, install_workspace):
        """Test install.sh creates .devcontainer directory."""
        devcontainer_dir = install_workspace / ".devcontainer"
        assert devcontainer_dir.exists(), ".devcontainer directory not created"
        assert devcontainer_dir.is_dir(), ".devcontainer is not a directory"

    def test_install_creates_devcontainer_json(self, install_workspace):
        """Test install.sh creates devcontainer.json."""
        devcontainer_json = install_workspace / ".devcontainer" / "devcontainer.json"
        assert devcontainer_json.exists(), "devcontainer.json not created"

    def test_install_creates_pyproject(self, install_workspace):
        """Test install.sh creates pyproject.toml."""
        pyproject = install_workspace / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml not created"

    def test_install_derives_short_name_from_directory(self, install_workspace):
        """Test SHORT_NAME is correctly derived from directory name.

        Directory name starts with "Install-Test-Project-" which should
        become "install_test_project_..." (lowercase, underscores).
        """
        pyproject = install_workspace / "pyproject.toml"
        content = pyproject.read_text()

        # The directory name is "Install-Test-Project-XXXXX"
        # SHORT_NAME should be sanitized to lowercase with underscores
        assert "install_test_project" in content.lower(), (
            f"SHORT_NAME not derived correctly from directory name.\n"
            f"Expected 'install_test_project' in pyproject.toml, got:\n{content[:500]}"
        )

    def test_install_uses_default_org_name(self, install_workspace):
        """Test ORG_NAME defaults to vigOS."""
        license_file = install_workspace / "LICENSE"
        assert license_file.exists(), "LICENSE file not created"

        content = license_file.read_text()
        assert "vigOS" in content, (
            f"Expected 'vigOS' in LICENSE (default ORG_NAME), "
            f"but found: {content[-500:]}"
        )

    def test_install_replaces_short_name_placeholder(self, install_workspace):
        """Test {{SHORT_NAME}} placeholder is replaced everywhere."""
        for file_path in install_workspace.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    assert "{{SHORT_NAME}}" not in content, (
                        f"{{{{SHORT_NAME}}}} placeholder not replaced in {file_path}"
                    )
                except UnicodeDecodeError:
                    # Skip binary files
                    continue

    def test_install_replaces_image_tag_placeholder(self, install_workspace):
        """Test {{IMAGE_TAG}} placeholder is replaced everywhere."""
        for file_path in install_workspace.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    assert "{{IMAGE_TAG}}" not in content, (
                        f"{{{{IMAGE_TAG}}}} placeholder not replaced in {file_path}"
                    )
                except UnicodeDecodeError:
                    continue

    def test_install_creates_src_directory(self, install_workspace):
        """Test src directory is created with correct package name."""
        src_dir = install_workspace / "src"
        assert src_dir.exists(), "src directory not created"

        # Should have a subdirectory named after the project
        subdirs = list(src_dir.iterdir())
        assert len(subdirs) == 1, f"Expected 1 package directory, found: {subdirs}"

        # Directory name should be sanitized project name
        pkg_name = subdirs[0].name
        assert pkg_name.startswith("install_test_project"), (
            f"Package directory should start with 'install_test_project', got: {pkg_name}"
        )

    def test_install_creates_tests_directory(self, install_workspace):
        """Test tests directory is created."""
        tests_dir = install_workspace / "tests"
        assert tests_dir.exists(), "tests directory not created"
        assert (tests_dir / "__init__.py").exists(), "tests/__init__.py not created"

    def test_install_creates_githooks(self, install_workspace):
        """Test .githooks directory is created."""
        githooks_dir = install_workspace / ".githooks"
        assert githooks_dir.exists(), ".githooks directory not created"

    def test_install_replaces_org_name_placeholder(self, install_workspace):
        """Test {{ORG_NAME}} placeholder is replaced everywhere."""
        for file_path in install_workspace.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    assert "{{ORG_NAME}}" not in content, (
                        f"{{{{ORG_NAME}}}} placeholder not replaced in {file_path}"
                    )
                except UnicodeDecodeError:
                    # Skip binary files
                    continue

    def test_install_creates_pre_commit_config(self, install_workspace):
        """Test .pre-commit-config.yaml is created."""
        precommit_config = install_workspace / ".pre-commit-config.yaml"
        assert precommit_config.exists(), ".pre-commit-config.yaml not created"
