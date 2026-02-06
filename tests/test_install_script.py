"""
Tests for the install.sh curl-based deployment script.

These tests verify that install.sh works correctly for deploying
the devcontainer to new projects without requiring interactive input.

Test categories:
1. Unit tests - test script logic without running containers
2. Integration tests - test full deployment workflow
"""

import atexit
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


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
    """Integration tests - actually deploy using install.sh.

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

    def test_install_creates_pre_commit_config(self, install_workspace):
        """Test .pre-commit-config.yaml is created."""
        precommit_config = install_workspace / ".pre-commit-config.yaml"
        assert precommit_config.exists(), ".pre-commit-config.yaml not created"
