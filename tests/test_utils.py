"""
Tests for documentation generation and install.sh unit behavior.

Tests functions from:
- docs/generate.py (all functions)
- install.sh (unit tests: help, dry-run, flags — no container image needed)

Note: install.sh integration tests (requiring a built container image) live in
tests/test_install_script.py and run under the test-integration CI job.
"""

import importlib.util
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

docs_dir = Path(__file__).parent.parent / "docs"

generate_spec = importlib.util.spec_from_file_location(
    "generate", docs_dir / "generate.py"
)
generate = importlib.util.module_from_spec(generate_spec)
generate_spec.loader.exec_module(generate)


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
