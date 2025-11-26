"""
Container verification tests for Base Development Environment.

These tests verify the container image itself: installed tools, versions,
environment variables, and file structure. They do not require workspace
initialization.

Derived containers can inherit from these test classes to verify that
base functionality is preserved in their containers.
"""


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
        # Check for version 2.x (from Containerfile: git=1:2.47.3-0+deb13u1)
        assert "2." in result.stdout, f"Expected git 2.x, got: {result.stdout}"

    def test_curl_installed(self, host):
        """Test that curl is installed."""
        assert host.package("curl").is_installed, "curl is not installed"

    def test_curl_version(self, host):
        """Test that curl version is correct."""
        result = host.run("curl --version")
        assert result.rc == 0, "curl --version failed"
        assert "curl" in result.stdout.lower()
        # Check for version 8.x (from Containerfile: curl=8.14.1-2)
        assert "8." in result.stdout, f"Expected curl 8.x, got: {result.stdout}"

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
        # Check for version 2.83.1
        assert "2.83.1" in result.stdout, f"Expected gh 2.83.0, got: {result.stdout}"


class TestPythonEnvironment:
    """Test Python environment setup."""

    def test_python3_installed(self, host):
        """Test that python3 is available."""
        result = host.run("python3 --version")
        assert result.rc == 0, "python3 --version failed"
        assert "Python 3.12" in result.stdout, (
            f"Expected Python 3.12, got: {result.stdout}"
        )

    def test_uv_installed(self, host):
        """Test that uv is installed."""
        result = host.run("uv --version")
        assert result.rc == 0, "uv --version failed"
        assert "uv" in result.stdout.lower()
        # Check for version
        assert "0.9.12" in result.stdout, f"Expected uv 0.9.11, got: {result.stdout}"


class TestDevelopmentTools:
    """Test that development tools are installed."""

    def test_pre_commit_installed(self, host):
        """Test that pre-commit is installed."""
        result = host.run("pre-commit --version")
        assert result.rc == 0, "pre-commit --version failed"
        assert "pre-commit" in result.stdout.lower()
        # Check for version 4.3.0 (from Containerfile: pre-commit==4.3.0)
        assert "4.5.0" in result.stdout, (
            f"Expected pre-commit 4.3.0, got: {result.stdout}"
        )

    def test_ruff_installed(self, host):
        """Test that ruff is installed."""
        result = host.run("ruff --version")
        assert result.rc == 0, "ruff --version failed"
        assert "ruff" in result.stdout.lower()
        # Check for version
        assert "0.14.6" in result.stdout, f"Expected ruff 0.14.6, got: {result.stdout}"


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

    def test_pre_commit_home_set(self, host):
        """Test that PRE_COMMIT_HOME is set."""
        result = host.run("echo $PRE_COMMIT_HOME")
        assert result.rc == 0, "Failed to read PRE_COMMIT_HOME"
        assert result.stdout.strip() == "/workspace/.pre-commit-cache", (
            f"Expected PRE_COMMIT_HOME=/workspace/.pre-commit-cache, got: {result.stdout.strip()}"
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

    def test_init_workspace_script_exists(self, host):
        """Test that init-workspace script exists and is executable."""
        init_script = host.file("/root/assets/init-workspace.sh")
        assert init_script.exists, "init-workspace script not found"
        assert init_script.mode == 0o755, "init-workspace script is not executable"

    def test_workspace_template_pre_commit_config_exists(self, host):
        """Test that .pre-commit-config.yaml exists in workspace template."""
        precommit_config = host.file("/root/assets/workspace/.pre-commit-config.yaml")
        assert precommit_config.exists, (
            ".pre-commit-config.yaml not found in workspace template"
        )
        assert precommit_config.is_file, ".pre-commit-config.yaml is not a file"

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
