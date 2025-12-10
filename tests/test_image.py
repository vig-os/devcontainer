"""
Container verification tests for Base Development Environment.

These tests verify the container image itself: installed tools, versions,
environment variables, and file structure. They do not require workspace
initialization.

Derived containers can inherit from these test classes to verify that
base functionality is preserved in their containers.
"""

import pytest

# Expected versions for installed tools
# These should be updated when the Containerfile is updated
EXPECTED_VERSIONS = {
    "git": "2.",  # Major version check (from apt package)
    "curl": "8.",  # Major version check (from apt package)
    "gh": "2.83.2",  # GitHub CLI (manually installed from latest release)
    "uv": "0.9.17",  # UV (manually installed from latest release)
    "python": "3.12",  # Python (from base image)
    "pre_commit": "4.5.0",  # pre-commit (installed via uv pip)
    "ruff": "0.14.8",  # ruff (installed via uv pip)
}


class TestSystemTools:
    """Test that system tools are installed with correct versions."""

    def test_git_installed(self, host):
        """Test that git is installed."""
        assert host.package("git").is_installed, "Git is not installed"

    def test_git_version(self, host):
        """Test that git version is correct."""
        result = host.run("git --version")
        assert result.rc == 0, "git --version failed"
        assert "git version" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["git"]
        assert expected in result.stdout, (
            f"Expected git {expected}x, got: {result.stdout}"
        )

    def test_curl_installed(self, host):
        """Test that curl is installed."""
        assert host.package("curl").is_installed, "curl is not installed"

    def test_curl_version(self, host):
        """Test that curl version is correct."""
        result = host.run("curl --version")
        assert result.rc == 0, "curl --version failed"
        assert "curl" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["curl"]
        assert expected in result.stdout, (
            f"Expected curl {expected}x, got: {result.stdout}"
        )

    def test_openssh_client_installed(self, host):
        """Test that openssh-client is installed."""
        assert host.package("openssh-client").is_installed, (
            "openssh-client is not installed"
        )

    def test_gh_installed(self, host):
        """Test that GitHub CLI (gh) is installed."""
        # gh is manually installed, so check for the binary file
        assert host.file("/usr/local/bin/gh").exists, "GitHub CLI (gh) binary not found"
        assert host.file("/usr/local/bin/gh").is_file, "GitHub CLI (gh) is not a file"

    def test_gh_version(self, host):
        """Test that gh version is correct."""
        result = host.run("gh --version")
        assert result.rc == 0, "gh --version failed"
        assert "gh version" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["gh"]
        assert expected in result.stdout, (
            f"Expected gh {expected}, got: {result.stdout}"
        )


class TestPythonEnvironment:
    """Test Python environment setup."""

    def test_python3_installed(self, host):
        """Test that python3 is available."""
        result = host.run("python3 --version")
        assert result.rc == 0, "python3 --version failed"
        expected = EXPECTED_VERSIONS["python"]
        assert f"Python {expected}" in result.stdout, (
            f"Expected Python {expected}, got: {result.stdout}"
        )

    def test_uv_installed(self, host):
        """Test that uv is installed."""
        result = host.run("uv --version")
        assert result.rc == 0, "uv --version failed"
        assert "uv" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["uv"]
        assert expected in result.stdout, (
            f"Expected uv {expected}, got: {result.stdout}"
        )


class TestDevelopmentTools:
    """Test that development tools are installed."""

    def test_pre_commit_installed(self, host):
        """Test that pre-commit is installed."""
        result = host.run("pre-commit --version")
        assert result.rc == 0, "pre-commit --version failed"
        assert "pre-commit" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["pre_commit"]
        assert expected in result.stdout, (
            f"Expected pre-commit {expected}, got: {result.stdout}"
        )

    def test_ruff_installed(self, host):
        """Test that ruff is installed."""
        result = host.run("ruff --version")
        assert result.rc == 0, "ruff --version failed"
        assert "ruff" in result.stdout.lower()
        expected = EXPECTED_VERSIONS["ruff"]
        assert expected in result.stdout, (
            f"Expected ruff {expected}, got: {result.stdout}"
        )


class TestEnvironmentVariables:
    """Test that environment variables are set correctly."""

    def test_pythonunbuffered_set(self, host):
        """Test that PYTHONUNBUFFERED is set."""
        result = host.run("echo $PYTHONUNBUFFERED")
        assert result.rc == 0, "Failed to read PYTHONUNBUFFERED"
        assert result.stdout.strip() == "1", (
            f"Expected PYTHONUNBUFFERED=1, got: {result.stdout.strip()}"
        )

    def test_in_container_set(self, host):
        """Test that IN_CONTAINER is set."""
        result = host.run("echo $IN_CONTAINER")
        assert result.rc == 0, "Failed to read IN_CONTAINER"
        assert result.stdout.strip() == "true", (
            f"Expected IN_CONTAINER=true, got: {result.stdout.strip()}"
        )

    def test_locale_set(self, host):
        """Test that locale environment variables are set."""
        result = host.run("echo $LANG")
        assert result.rc == 0, "Failed to read LANG"
        assert "en_US.UTF-8" in result.stdout, (
            f"Expected LANG=en_US.UTF-8, got: {result.stdout.strip()}"
        )


class TestFileStructure:
    """Test that expected files and directories exist."""

    def test_workspace_directory_exists(self, host):
        """Test that workspace directory exists."""
        assert host.file("/workspace").is_directory, "Workspace directory not found"

    def test_precommit_alias_in_bashrc(self, host):
        """Test that precommit alias is defined in .bashrc."""
        bashrc = host.file("/root/.bashrc")
        assert bashrc.exists, ".bashrc not found"
        assert "alias precommit=" in bashrc.content_string, (
            "precommit alias not found in .bashrc"
        )

    def test_assets_directory_exists(self, host):
        """Test that assets directory exists."""
        assert host.file("/root/assets").is_directory, "Assets directory not found"

    def test_assets_workspace_structure(self, host):
        """Test that assets/workspace directory structure is complete."""
        # Define expected directories
        expected_dirs = [
            "/root/assets/workspace",
            "/root/assets/workspace/.devcontainer",
            "/root/assets/workspace/.devcontainer/scripts",
            "/root/assets/workspace/.githooks",
        ]

        # Define expected files
        expected_files = [
            # Workspace root files
            "/root/assets/workspace/.gitignore",
            "/root/assets/workspace/.pre-commit-config.yaml",
            "/root/assets/workspace/.pymarkdown",
            "/root/assets/workspace/.pymarkdown.config.md",
            "/root/assets/workspace/.yamllint",
            "/root/assets/workspace/CHANGELOG.md",
            "/root/assets/workspace/README.md",
            "/root/assets/workspace/LICENSE",
            # .devcontainer files
            "/root/assets/workspace/.devcontainer/.gitignore",
            "/root/assets/workspace/.devcontainer/README.md",
            "/root/assets/workspace/.devcontainer/devcontainer.json",
            "/root/assets/workspace/.devcontainer/docker-compose.yml",
            "/root/assets/workspace/.devcontainer/docker-compose.override.yml",  # Auto-generated in Containerfile
            "/root/assets/workspace/.devcontainer/docker-compose.override.yml.example",
            "/root/assets/workspace/.devcontainer/workspace.code-workspace.example",
            # .devcontainer/scripts files
            "/root/assets/workspace/.devcontainer/scripts/post-create.sh",
            "/root/assets/workspace/.devcontainer/scripts/initialize.sh",
            "/root/assets/workspace/.devcontainer/scripts/post-attach.sh",
            "/root/assets/workspace/.devcontainer/scripts/copy-host-user-conf.sh",
            "/root/assets/workspace/.devcontainer/scripts/init-git.sh",
            "/root/assets/workspace/.devcontainer/scripts/init-precommit.sh",
            "/root/assets/workspace/.devcontainer/scripts/setup-git-conf.sh",
            # Git hooks
            "/root/assets/workspace/.githooks/pre-commit",
        ]

        # Define files and folders that should be gitignored (user-specific, not in image)
        gitignored_content = [
            "/root/assets/workspace/.devcontainer/docker-compose.local.yml",
            "/root/assets/workspace/.devcontainer/.conf",
            "/root/assets/workspace/.devcontainer/workspace.code-workspace",
        ]

        # Check all directories exist
        for dir_path in expected_dirs:
            assert host.file(dir_path).is_directory, (
                f"Expected directory not found: {dir_path}"
            )

        # Check all files exist
        for file_path in expected_files:
            assert host.file(file_path).exists, f"Expected file not found: {file_path}"
            assert host.file(file_path).is_file, (
                f"Expected file is not a regular file: {file_path}"
            )
            # Check shell scripts are executable
            if file_path.endswith(".sh"):
                assert host.file(file_path).mode & 0o111, (
                    f"Expected shell script is not executable: {file_path}"
                )

        # Check that gitignored files and folders are gitignored
        for file_path in gitignored_content:
            assert not host.file(file_path).exists, (
                f"Expected file not found: {file_path}"
            )

    def test_workspace_template_pre_commit_hooks_initialized(self, host):
        """Test that pre-commit hooks are pre-initialized in workspace template."""
        cache_dir = host.file("/root/assets/workspace/.pre-commit-cache")
        assert cache_dir.exists, (
            "Pre-commit cache directory not found in workspace template"
        )
        assert cache_dir.is_directory, "Pre-commit cache is not a directory"
        # Verify the cache directory is not empty (contains installed hooks)
        result = host.run(
            'test -n "$(ls -A /root/assets/workspace/.pre-commit-cache 2>/dev/null)"'
        )
        assert result.rc == 0, (
            "Pre-commit cache directory is empty - hooks were not initialized"
        )

    def test_docker_compose_override_arch_specific(self, host):
        """Test that docker-compose.override.yml has correct socket for architecture."""
        override_file = (
            "/root/assets/workspace/.devcontainer/docker-compose.override.yml"
        )

        # Verify file exists
        assert host.file(override_file).exists, "docker-compose.override.yml not found"

        # Get architecture
        arch_result = host.run("uname -m")
        assert arch_result.rc == 0, "Failed to determine architecture"
        arch = arch_result.stdout.strip()

        # Read override file content
        content_result = host.run(f"cat {override_file}")
        assert content_result.rc == 0, "Failed to read override file"
        content = content_result.stdout

        # Verify correct socket path based on architecture
        if arch in ("aarch64", "arm64"):
            # arm64 → macOS socket path (UID 501)
            assert "/run/user/501/podman/podman.sock" in content, (
                f"Expected macOS socket path for {arch} architecture"
            )
        elif arch in ("x86_64", "amd64"):
            # amd64 → Linux socket path (UID 1000)
            assert "/run/user/1000/podman/podman.sock" in content, (
                f"Expected Linux socket path for {arch} architecture"
            )
        else:
            pytest.fail(f"Unexpected architecture: {arch}")


class TestPlaceholders:
    """Test that placeholders are replaced correctly."""

    def test_image_tag_replaced(self, host):
        """Test that {{IMAGE_TAG}} placeholder is replaced in all asset files."""
        workspace_root = "/root/assets/workspace"

        # Hard-coded list of paths to exclude
        excluded_paths = [
            ".pre-commit-cache",
            ".ruff_cache",
        ]

        # Build find command with exclusions
        exclude_patterns = " -o ".join(
            [f"-path '*/{path}/*'" for path in excluded_paths]
        )
        find_cmd = (
            f"find {workspace_root} "
            f"\\( {exclude_patterns} \\) -prune "
            r"-o -type f -print"
        )

        result = host.run(find_cmd)
        assert result.rc == 0, f"Failed to find files in {workspace_root}"
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        for file_path in files:
            file = host.file(file_path)
            if file.exists and file.is_file:
                try:
                    content = file.content_string
                    assert "{{IMAGE_TAG}}" not in content, (
                        f"{{IMAGE_TAG}} placeholder not replaced in {file_path}"
                    )
                except UnicodeDecodeError:
                    # Skip binary files
                    continue
