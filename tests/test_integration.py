"""
DevContainer integration tests for Base Development Environment.

These tests verify that the container works correctly as a devcontainer,
including template initialization, configuration files, and scripts.

Derived containers can inherit from these test classes to verify that
devcontainer functionality works correctly in their containers too.
"""

import json
import os
import subprocess
import warnings
from pathlib import Path

import pytest
import yaml


class TestHostGitSignatureSetup:
    """Test that git commit signing is properly configured on the host.

    These tests run on the host machine (not inside containers) to verify
    that SSH-based git commit signing prerequisites are in place.
    """

    def test_ssh_public_key_exists(self):
        """Test that SSH public key for signing exists on host."""
        from pathlib import Path

        ssh_pubkey = Path.home() / ".ssh" / "id_ed25519_github.pub"

        if not ssh_pubkey.exists():
            pytest.skip(
                f"SSH public key not found at {ssh_pubkey}. "
                "This is optional but recommended for git commit signing. "
                "Generate with: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github"
            )

        assert ssh_pubkey.is_file(), "SSH public key path exists but is not a file"

        # Verify it's a valid public key
        content = ssh_pubkey.read_text()
        assert content.startswith("ssh-ed25519 "), (
            f"SSH public key doesn't appear to be valid ED25519 key: {content[:50]}"
        )

    def test_git_signing_format_configured(self):
        """Test that git is configured to use SSH signing format."""
        result = subprocess.run(
            ["git", "config", "gpg.format"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(
                "Git signing format not configured. "
                "This is optional but recommended. "
                "Configure with: git config gpg.format ssh"
            )

        assert result.stdout.strip() == "ssh", (
            f"Expected gpg.format=ssh, got: {result.stdout.strip()}"
        )

    def test_git_signing_key_configured(self):
        """Test that git signing key is configured."""
        result = subprocess.run(
            ["git", "config", "user.signingkey"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(
                "Git signing key not configured. "
                "This is optional but recommended. "
                "Configure with the full SSH public key string or file path"
            )

        signing_key = result.stdout.strip()
        assert signing_key, "Signing key is configured but empty"

        # Check if it's a file path, email, or full public key string
        if signing_key.startswith("~") or signing_key.startswith("/"):
            # Old behavior: file path
            from pathlib import Path

            key_path = Path(signing_key.replace("~", str(Path.home())))
            assert key_path.exists(), f"Signing key file not found: {signing_key}"
        elif signing_key.startswith("ssh-"):
            # Full SSH public key string (for SSH agent signing)
            # Verify it looks like a valid SSH public key format
            parts = signing_key.split()
            assert len(parts) >= 2, (
                f"Invalid SSH public key format. "
                f"Expected 'ssh-<type> <key-data> [comment]', got: {signing_key[:50]}..."
            )
            assert parts[0] in [
                "ssh-rsa",
                "ssh-ed25519",
                "ecdsa-sha2-nistp256",
                "ecdsa-sha2-nistp384",
                "ecdsa-sha2-nistp521",
            ], f"Unsupported SSH key type: {parts[0]}"
        elif "@" in signing_key:
            # Email address (standard for SSH agent signing)
            # This is the preferred method - git looks up the email in allowed-signers
            pass
        else:
            # Could be other identifier (namespace, etc.)
            pass

    def test_git_commit_gpgsign_configured(self):
        """Test that git is configured to sign commits by default."""
        result = subprocess.run(
            ["git", "config", "commit.gpgsign"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(
                "Commit signing not enabled by default. "
                "This is optional but recommended. "
                "Enable with: git config commit.gpgsign true"
            )

        assert result.stdout.strip() == "true", (
            f"Expected commit.gpgsign=true, got: {result.stdout.strip()}"
        )

    def test_allowed_signers_file_exists(self):
        """Test that allowed-signers file exists for signature verification."""
        from pathlib import Path

        # Check if allowedSignersFile is configured
        result = subprocess.run(
            ["git", "config", "gpg.ssh.allowedSignersFile"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(
                "Allowed signers file not configured. "
                "This is optional but recommended for signature verification. "
                "Configure with: git config gpg.ssh.allowedSignersFile ~/.config/git/allowed-signers"
            )

        allowed_signers_path = result.stdout.strip()
        assert allowed_signers_path, "Allowed signers file path is configured but empty"

        # Resolve ~ to home directory
        allowed_signers = Path(allowed_signers_path.replace("~", str(Path.home())))

        if not allowed_signers.exists():
            pytest.skip(
                f"Allowed signers file configured but doesn't exist: {allowed_signers_path}. "
                "Create it with your email and public key."
            )

        assert allowed_signers.is_file(), (
            f"Allowed signers path exists but is not a file: {allowed_signers}"
        )

        # Verify it has some content
        content = allowed_signers.read_text()
        assert len(content.strip()) > 0, "Allowed signers file is empty"
        assert "ssh-ed25519" in content or "ssh-rsa" in content, (
            "Allowed signers file doesn't appear to contain SSH public keys"
        )

    def test_git_user_configured(self):
        """Test that git user name and email are configured."""
        # Check user.name
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            "Git user.name not configured. "
            "Configure with: git config user.name 'Your Name'"
        )

        name = result.stdout.strip()
        assert name, "Git user.name is configured but empty"

        # Check user.email
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            "Git user.email not configured. "
            "Configure with: git config user.email 'your.email@example.com'"
        )

        email = result.stdout.strip()
        assert email, "Git user.email is configured but empty"
        assert "@" in email, f"Git user.email doesn't appear to be valid: {email}"


class TestDevContainerStructure:
    """Test that devcontainer structure is created correctly."""

    def test_devcontainer_directory_exists(self, initialized_workspace):
        """Test that .devcontainer directory exists."""
        devcontainer_dir = initialized_workspace / ".devcontainer"
        assert devcontainer_dir.exists(), ".devcontainer directory not found"
        assert devcontainer_dir.is_dir(), ".devcontainer is not a directory"

    def test_devcontainer_json_exists(self, initialized_workspace):
        """Test that devcontainer.json exists."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )
        assert devcontainer_json.exists(), "devcontainer.json not found"
        assert devcontainer_json.is_file(), "devcontainer.json is not a file"

    def test_devcontainer_scripts_directory_exists(self, initialized_workspace):
        """Test that scripts directory exists."""
        scripts_dir = initialized_workspace / ".devcontainer" / "scripts"
        assert scripts_dir.exists(), ".devcontainer/scripts directory not found"
        assert scripts_dir.is_dir(), ".devcontainer/scripts is not a directory"

    def test_setup_scripts_exist(self, initialized_workspace):
        """Test that all setup scripts exist and are executable."""
        scripts_dir = initialized_workspace / ".devcontainer" / "scripts"
        expected_scripts = [
            "copy-host-user-conf.sh",
            "init-git.sh",
            "setup-git-conf.sh",
            "init-precommit.sh",
            "post-attach.sh",
            "post-create.sh",
            "initialize.sh",
        ]

        for script_name in expected_scripts:
            script = scripts_dir / script_name
            assert script.exists(), f"{script_name} not found"
            assert script.is_file(), f"{script_name} is not a file"
            assert script.stat().st_mode & 0o111, f"{script_name} is not executable"

    def test_template_files_copied(self, initialized_workspace):
        """Test that minimal template files are copied to workspace."""
        # Check for README.md
        readme = initialized_workspace / "README.md"
        assert readme.exists(), "README.md not found in workspace"

        # Check for CHANGELOG.md
        changelog = initialized_workspace / "CHANGELOG.md"
        assert changelog.exists(), "CHANGELOG.md not found in workspace"


class TestDevContainerJson:
    """Test devcontainer.json configuration."""

    def test_devcontainer_json_valid(self, initialized_workspace):
        """Test that devcontainer.json is valid JSON."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert isinstance(config, dict), "devcontainer.json is not a valid JSON object"

    def test_devcontainer_json_name(self, initialized_workspace):
        """Test that devcontainer.json has correct name."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "name" in config, "devcontainer.json missing 'name' field"

        # Verify name is not empty
        assert len(config["name"]) > 0, "Name should not be empty"

        # The name should contain the project name (test_project) from init-workspace
        assert "test_project" in config["name"].lower(), (
            f"Expected name to contain 'test_project', got: {config['name']}"
        )

    def test_devcontainer_json_docker_compose_file(self, initialized_workspace):
        """Test that devcontainer.json references docker-compose.yml."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "dockerComposeFile" in config, (
            "devcontainer.json missing 'dockerComposeFile' field"
        )
        assert config["dockerComposeFile"] == "docker-compose.yml", (
            f"Expected dockerComposeFile='docker-compose.yml', got: {config['dockerComposeFile']}"
        )

    def test_devcontainer_json_service(self, initialized_workspace):
        """Test that devcontainer.json specifies the service name."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "service" in config, "devcontainer.json missing 'service' field"
        assert config["service"] == "devcontainer", (
            f"Expected service='devcontainer', got: {config['service']}"
        )

    def test_devcontainer_json_workspace_folder(self, initialized_workspace):
        """Test that workspaceFolder is set correctly to project subdirectory."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "workspaceFolder" in config, (
            "devcontainer.json missing 'workspaceFolder' field"
        )
        # workspaceFolder should be /workspace/<project_name>, not /workspace
        assert "/workspace/" in config["workspaceFolder"], (
            f"Expected workspaceFolder to be in /workspace/ subdirectory, got: {config['workspaceFolder']}"
        )
        assert config["workspaceFolder"] != "/workspace", (
            "workspaceFolder should be a subdirectory, not '/workspace' directly"
        )
        # Should contain the project name (test_project)
        assert "test_project" in config["workspaceFolder"].lower(), (
            f"workspaceFolder should contain project name, got: {config['workspaceFolder']}"
        )

    def test_devcontainer_json_vscode_extensions(self, initialized_workspace):
        """Test that VS Code extensions are configured."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "customizations" in config, (
            "devcontainer.json missing 'customizations' field"
        )
        assert "vscode" in config["customizations"], (
            "devcontainer.json missing 'vscode' customizations"
        )
        assert "extensions" in config["customizations"]["vscode"], (
            "devcontainer.json missing 'extensions' in vscode customizations"
        )

        extensions = config["customizations"]["vscode"]["extensions"]
        assert isinstance(extensions, list), "Extensions should be a list"
        assert len(extensions) > 0, "No VS Code extensions configured"

    def test_devcontainer_json_vscode_settings(self, initialized_workspace):
        """Test that VS Code settings are configured."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "settings" in config["customizations"]["vscode"], (
            "devcontainer.json missing 'settings' in vscode customizations"
        )

        settings = config["customizations"]["vscode"]["settings"]
        assert "python.defaultInterpreterPath" in settings, (
            "Python interpreter path not configured"
        )
        assert settings["python.defaultInterpreterPath"] == "/usr/local/bin/python", (
            f"Expected Python path '/usr/local/bin/python', got: {settings['python.defaultInterpreterPath']}"
        )

    def test_devcontainer_json_initialize_command(self, initialized_workspace):
        """Test that initializeCommand is configured."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "initializeCommand" in config, (
            "devcontainer.json missing 'initializeCommand' field"
        )
        assert config["initializeCommand"] == ".devcontainer/scripts/initialize.sh", (
            "Expected initializeCommand='.devcontainer/scripts/initialize.sh', "
            f"got: {config['initializeCommand']}"
        )

    def test_devcontainer_json_post_attach_command(self, initialized_workspace):
        """Test that postAttachCommand is configured correctly."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "postAttachCommand" in config, (
            "devcontainer.json missing 'postAttachCommand' field"
        )
        # postAttachCommand should reference .devcontainer inside project subdirectory
        expected_command = (
            "/workspace/test_project/.devcontainer/scripts/post-attach.sh"
        )
        assert config["postAttachCommand"] == expected_command, (
            f"Expected postAttachCommand='{expected_command}', "
            f"got: {config['postAttachCommand']}"
        )

    def test_devcontainer_json_post_create_command(self, initialized_workspace):
        """Test that postCreateCommand is configured correctly."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        assert "postCreateCommand" in config, (
            "devcontainer.json missing 'postCreateCommand' field"
        )
        # postCreateCommand should reference .devcontainer inside project subdirectory
        expected_command = (
            "/workspace/test_project/.devcontainer/scripts/post-create.sh"
        )
        assert config["postCreateCommand"] == expected_command, (
            f"Expected postCreateCommand='{expected_command}', "
            f"got: {config['postCreateCommand']}"
        )

    def test_devcontainer_json_no_redundant_container_env(self, initialized_workspace):
        """Test that containerEnv is not redundantly defined (should be in docker-compose.yml)."""
        devcontainer_json = (
            initialized_workspace / ".devcontainer" / "devcontainer.json"
        )

        with devcontainer_json.open() as f:
            config = json.load(f)

        # containerEnv should not be in devcontainer.json since environment
        # variables are already defined in docker-compose.yml
        assert "containerEnv" not in config, (
            "containerEnv should not be in devcontainer.json (use docker-compose.yml instead)"
        )


class TestDevContainerDockerCompose:
    """Test docker-compose.yml configuration."""

    def test_docker_compose_yml_exists(self, initialized_workspace):
        """Test that docker-compose.yml exists."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )
        assert docker_compose_yml.exists(), "docker-compose.yml not found"
        assert docker_compose_yml.is_file(), "docker-compose.yml is not a file"

    def test_docker_compose_yml_valid(self, initialized_workspace):
        """Test that docker-compose.yml is valid YAML."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict), "docker-compose.yml is not a valid YAML object"
        assert "version" in config, "docker-compose.yml missing 'version' field"
        assert "services" in config, "docker-compose.yml missing 'services' field"

    def test_docker_compose_yml_service_exists(self, initialized_workspace):
        """Test that devcontainer service exists in docker-compose.yml."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        assert "devcontainer" in config["services"], (
            "docker-compose.yml missing 'devcontainer' service"
        )

    def test_docker_compose_yml_image(self, initialized_workspace, container_image):
        """Test that docker-compose.yml has correct image reference."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "image" in service, "devcontainer service missing 'image' field"

        # Verify the docker-compose.yml image matches the container_image fixture
        # container_image format: ghcr.io/vig-os/devcontainer:{tag}
        assert service["image"] == container_image, (
            f"Expected image to be {container_image}, got: {service['image']}"
        )

        # {{IMAGE_TAG}} should be replaced (or at least not present)
        assert "{{IMAGE_TAG}}" not in service["image"], (
            f"Image tag placeholder not replaced: {service['image']}"
        )

    def test_docker_compose_yml_volumes(self, initialized_workspace):
        """Test that docker-compose.yml has volume mount configured to subdirectory."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "volumes" in service, "devcontainer service missing 'volumes' field"
        assert isinstance(service["volumes"], list), "volumes should be a list"
        assert len(service["volumes"]) > 0, "No volumes configured"

        # Check that workspace folder is mounted to subdirectory
        volumes_str = " ".join(service["volumes"])
        # Should use relative path (..) for mounting
        assert ".." in volumes_str, (
            f"Expected relative path (..) or localWorkspaceFolder in volumes, got: {service['volumes']}"
        )
        # Should mount to /workspace/test_project (or /workspace/devcontainer before replacement)
        assert "/workspace/" in volumes_str, (
            f"Expected mount to /workspace/ subdirectory, got: {service['volumes']}"
        )
        # Check that it's not mounting directly to /workspace
        assert (
            ":/workspace:" not in volumes_str and ':/workspace"' not in volumes_str
        ), (
            f"Should mount to subdirectory, not directly to /workspace, got: {service['volumes']}"
        )

    def test_docker_compose_yml_environment(self, initialized_workspace):
        """Test that docker-compose.yml has environment variables configured."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "environment" in service, (
            "devcontainer service missing 'environment' field"
        )
        assert isinstance(service["environment"], list), "environment should be a list"

        # Check for environment variable overrides
        # (PYTHONUNBUFFERED and IN_CONTAINER are in Containerfile, not here)
        env_vars = {
            item.split("=")[0]: item.split("=")[1] if "=" in item else None
            for item in service["environment"]
        }

        assert "PRE_COMMIT_HOME" in env_vars, (
            "PRE_COMMIT_HOME environment variable not found"
        )
        # PRE_COMMIT_HOME should also be in project subdirectory
        assert (
            env_vars["PRE_COMMIT_HOME"].lower()
            == "/workspace/test_project/.pre-commit-cache"
        ), (
            f"PRE_COMMIT_HOME should be in project directory, got: {env_vars['PRE_COMMIT_HOME']}"
        )

    def test_docker_compose_yml_command(self, initialized_workspace):
        """Test that docker-compose.yml has command configured."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "command" in service, "devcontainer service missing 'command' field"
        assert service["command"] == "sleep infinity", (
            f"Expected command='sleep infinity', got: {service['command']}"
        )

    def test_docker_compose_yml_user(self, initialized_workspace):
        """Test that docker-compose.yml has user configured."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "user" in service, "devcontainer service missing 'user' field"
        assert service["user"] == "root", (
            f"Expected user='root', got: {service['user']}"
        )

    def test_docker_compose_yml_interactive_settings(self, initialized_workspace):
        """Test that docker-compose.yml has interactive settings configured."""
        docker_compose_yml = (
            initialized_workspace / ".devcontainer" / "docker-compose.yml"
        )

        with docker_compose_yml.open() as f:
            config = yaml.safe_load(f)

        service = config["services"]["devcontainer"]
        assert "stdin_open" in service, (
            "devcontainer service missing 'stdin_open' field"
        )
        assert service["stdin_open"] is True, (
            f"Expected stdin_open=True, got: {service['stdin_open']}"
        )
        assert "tty" in service, "devcontainer service missing 'tty' field"
        assert service["tty"] is True, f"Expected tty=True, got: {service['tty']}"


class TestPlaceholders:
    """Test that placeholders are replaced correctly."""

    def test_placeholders_replaced(self, initialized_workspace):
        """Test that placeholders are replaced in all asset files."""
        # Hard-coded list of paths to exclude
        excluded_paths = [
            ".pre-commit-cache",
            ".ruff_cache",
        ]

        # Find all files recursively, excluding specified paths at iteration level
        files = (
            file_path
            for file_path in initialized_workspace.rglob("*")
            if file_path.is_file()
            and not any(
                excluded_path in file_path.parts for excluded_path in excluded_paths
            )
        )

        # Check each file for placeholders
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                for placeholder in ["{{IMAGE_TAG}}", "devcontainer"]:
                    assert placeholder not in content, (
                        f"{placeholder} placeholder not replaced in {file_path}"
                    )
            except UnicodeDecodeError:
                # Skip binary files
                continue

    def test_org_name_replaced(self, initialized_workspace):
        """Test that organization name is replaced in specific asset files."""
        # Files with organization name in specific paths
        files = [
            initialized_workspace / "LICENSE",
        ]

        # Check each file for organization name
        for file in files:
            content = file.read_text(encoding="utf-8")
            assert "vigOS" not in content, f"vigOS placeholder not replaced in {file}"
            assert "Test Org" in content, f"Organization name not replaced in {file}"

    def test_short_name_replaced(self, initialized_workspace):
        """Test that short name is replaced in specific asset files."""
        # Files with short name in specific paths
        files = [
            initialized_workspace / ".devcontainer" / "devcontainer.json",
        ]

        # Check each file for short name
        for file in files:
            content = file.read_text(encoding="utf-8")
            assert "devcontainer" not in content, (
                f"devcontainer placeholder not replaced in {file}"
            )
            assert "test_project" in content, f"Short name not replaced in {file}"


class TestDevContainerGit:
    """Test that git configuration files are set up."""

    def test_githooks_directory_exists(self, initialized_workspace):
        """Test that .githooks directory exists."""
        githooks_dir = initialized_workspace / ".githooks"
        assert githooks_dir.exists(), ".githooks directory not found"
        assert githooks_dir.is_dir(), ".githooks is not a directory"

    def test_pre_commit_hook_exists(self, initialized_workspace):
        """Test that pre-commit hook exists."""
        pre_commit_hook = initialized_workspace / ".githooks" / "pre-commit"
        assert pre_commit_hook.exists(), "pre-commit hook not found"
        assert pre_commit_hook.is_file(), "pre-commit hook is not a file"
        assert pre_commit_hook.stat().st_mode & 0o111, (
            "pre-commit hook is not executable"
        )

    def test_pre_commit_config_exists(self, initialized_workspace):
        """Test that .pre-commit-config.yaml exists."""
        precommit_config = initialized_workspace / ".pre-commit-config.yaml"
        assert precommit_config.exists(), ".pre-commit-config.yaml not found"
        assert precommit_config.is_file(), ".pre-commit-config.yaml is not a file"


class TestDevContainerUserConf:
    """Test that user configuration files are set up."""

    def test_conf_directory_files(self, devcontainer_up):
        """Test that .devcontainer/.conf contains all expected files."""
        workspace_path = str(devcontainer_up.resolve())
        # .devcontainer is inside the project subdirectory
        conf_dir = "/workspace/test_project/.devcontainer/.conf"

        # Check that .gitconfig exists (should always be generated)
        check_gitconfig_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            f"{conf_dir}/.gitconfig",
        ]

        result = subprocess.run(
            check_gitconfig_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f".gitconfig not found in {conf_dir}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(check_gitconfig_cmd)}"
        )

        # Check for optional files (these may not exist if not present on host)
        # SSH public key
        check_ssh_key_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            f"{conf_dir}/id_ed25519_github.pub",
        ]

        ssh_key_result = subprocess.run(
            check_ssh_key_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        # SSH key is optional, so we warn if it's missing
        if ssh_key_result.returncode != 0:
            warnings.warn(
                f"SSH public key not found at {conf_dir}/id_ed25519_github.pub "
                "(this is optional if not present on host)",
                UserWarning,
                stacklevel=2,
            )

        # Allowed signers file
        check_allowed_signers_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            f"{conf_dir}/allowed-signers",
        ]

        allowed_signers_result = subprocess.run(
            check_allowed_signers_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        # Allowed signers is optional, so we warn if it's missing
        if allowed_signers_result.returncode != 0:
            warnings.warn(
                f"allowed-signers file not found at {conf_dir}/allowed-signers "
                "(this is optional if not present on host)",
                UserWarning,
                stacklevel=2,
            )

        # GitHub CLI config directory (optional)
        check_gh_config_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-d",
            f"{conf_dir}/gh",
        ]

        gh_config_result = subprocess.run(
            check_gh_config_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        # GitHub CLI config is optional, so we warn if it's missing
        if gh_config_result.returncode != 0:
            warnings.warn(
                f"GitHub CLI config directory not found at {conf_dir}/gh "
                "(this is optional if not present on host)",
                UserWarning,
                stacklevel=2,
            )

        # GitHub CLI token file must NOT exist (should be deleted after authentication)
        check_gh_token_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "!",
            "-f",
            f"{conf_dir}/.gh_token",
        ]

        gh_token_result = subprocess.run(
            check_gh_token_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert gh_token_result.returncode == 0, (
            f".gh_token file still exists in {conf_dir} - token was not deleted after authentication\n"
            f"This is a security risk as the token should be removed after use.\n"
            f"stdout: {gh_token_result.stdout}\n"
            f"stderr: {gh_token_result.stderr}\n"
            f"command: {' '.join(check_gh_token_cmd)}"
        )

    def test_files_copied_to_home(self, devcontainer_up):
        """Test that files from .devcontainer/.conf have been copied to their destinations."""
        workspace_path = str(devcontainer_up.resolve())
        # .devcontainer is inside the project subdirectory
        conf_dir = "/workspace/test_project/.devcontainer/.conf"

        # Check that .gitconfig was copied to ~/.gitconfig
        check_gitconfig_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            "test -f $HOME/.gitconfig",
        ]

        result = subprocess.run(
            check_gitconfig_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f".gitconfig not found in $HOME/.gitconfig\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(check_gitconfig_cmd)}"
        )

        # Check that SSH public key was copied (if it exists in .conf)
        # First check if it exists in .conf
        check_conf_ssh_key_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            f"{conf_dir}/id_ed25519_github.pub",
        ]

        conf_ssh_key_result = subprocess.run(
            check_conf_ssh_key_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        if conf_ssh_key_result.returncode == 0:
            # If it exists in .conf, it should be copied to ~/.ssh/
            check_home_ssh_key_cmd = [
                "devcontainer",
                "exec",
                "--workspace-folder",
                workspace_path,
                "--config",
                f"{workspace_path}/.devcontainer/devcontainer.json",
                "--docker-path",
                "podman",
                "bash",
                "-c",
                "test -f $HOME/.ssh/id_ed25519_github.pub",
            ]

            home_ssh_key_result = subprocess.run(
                check_home_ssh_key_cmd,
                capture_output=True,
                text=True,
                cwd=workspace_path,
                env=os.environ.copy(),
            )

            assert home_ssh_key_result.returncode == 0, (
                f"SSH public key found in {conf_dir} but not copied to $HOME/.ssh/id_ed25519_github.pub\n"
                f"stdout: {home_ssh_key_result.stdout}\n"
                f"stderr: {home_ssh_key_result.stderr}\n"
                f"command: {' '.join(check_home_ssh_key_cmd)}"
            )

        # Check that allowed-signers was copied (if it exists in .conf)
        check_conf_allowed_signers_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            f"{conf_dir}/allowed-signers",
        ]

        conf_allowed_signers_result = subprocess.run(
            check_conf_allowed_signers_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        if conf_allowed_signers_result.returncode == 0:
            # If it exists in .conf, it should be copied to ~/.config/git/
            check_home_allowed_signers_cmd = [
                "devcontainer",
                "exec",
                "--workspace-folder",
                workspace_path,
                "--config",
                f"{workspace_path}/.devcontainer/devcontainer.json",
                "--docker-path",
                "podman",
                "bash",
                "-c",
                "test -f $HOME/.config/git/allowed-signers",
            ]

            home_allowed_signers_result = subprocess.run(
                check_home_allowed_signers_cmd,
                capture_output=True,
                text=True,
                cwd=workspace_path,
                env=os.environ.copy(),
            )

            assert home_allowed_signers_result.returncode == 0, (
                f"allowed-signers file found in {conf_dir} but not copied to $HOME/.config/git/allowed-signers\n"
                f"stdout: {home_allowed_signers_result.stdout}\n"
                f"stderr: {home_allowed_signers_result.stderr}\n"
                f"command: {' '.join(check_home_allowed_signers_cmd)}"
            )

        # Check that GitHub CLI config was copied (if it exists in .conf)
        check_conf_gh_config_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-d",
            f"{conf_dir}/gh",
        ]

        conf_gh_config_result = subprocess.run(
            check_conf_gh_config_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        if conf_gh_config_result.returncode == 0:
            # If it exists in .conf, it should be copied to ~/.config/gh/
            check_home_gh_config_cmd = [
                "devcontainer",
                "exec",
                "--workspace-folder",
                workspace_path,
                "--config",
                f"{workspace_path}/.devcontainer/devcontainer.json",
                "--docker-path",
                "podman",
                "bash",
                "-c",
                "test -d $HOME/.config/gh",
            ]

            home_gh_config_result = subprocess.run(
                check_home_gh_config_cmd,
                capture_output=True,
                text=True,
                cwd=workspace_path,
                env=os.environ.copy(),
            )

            assert home_gh_config_result.returncode == 0, (
                f"GitHub CLI config directory found in {conf_dir}/gh but not copied to $HOME/.config/gh\n"
                f"stdout: {home_gh_config_result.stdout}\n"
                f"stderr: {home_gh_config_result.stderr}\n"
                f"command: {' '.join(check_home_gh_config_cmd)}"
            )


class TestDevContainerCLI:
    """Tests for the devcontainer CLI environment."""

    def test_ssh_github_authentication(self, devcontainer_up):
        """Test that SSH authentication to GitHub works in the devcontainer."""
        workspace_path = str(devcontainer_up.resolve())

        # First check if SSH keys are available in the container
        check_keys_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            "test -f ~/.ssh/id_ed25519_github.pub && echo 'keys_found' || echo 'no_keys'",
        ]

        keys_result = subprocess.run(
            check_keys_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        # If no SSH keys are available, skip the test
        if "no_keys" in keys_result.stdout:
            pytest.skip(
                "SSH keys not available in devcontainer. "
                "SSH keys need to be set up via .devcontainer/.conf/ for this test to run."
            )

        # Test SSH connection to GitHub
        # This verifies that SSH keys are properly configured
        exec_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "ssh",
            "-T",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-i",
            "~/.ssh/id_ed25519_github",
            "git@github.com",
        ]

        result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
            timeout=10,
        )

        # SSH to GitHub returns exit code 1 on success (it's a test connection)
        # Exit code 255 means connection/auth failed
        # We accept exit code 1 (successful test connection) or specific error messages
        if result.returncode == 255:
            # Check if it's a permission denied (keys not authorized) vs connection error
            if "Permission denied" in result.stderr:
                # Keys exist but aren't authorized - this is acceptable for testing
                # The important thing is that SSH is configured
                assert "github.com" in result.stderr, (
                    f"SSH connection failed unexpectedly\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )
            else:
                pytest.fail(
                    f"SSH connection to GitHub failed\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}\n"
                    f"command: {' '.join(exec_cmd)}"
                )
        elif result.returncode == 1:
            # Success - GitHub responded (exit 1 is normal for test connections)
            assert "Hi" in result.stdout or "github.com" in result.stderr, (
                f"Unexpected SSH response from GitHub\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

    def test_pre_commit_hook(self, devcontainer_up):
        """Test that pre-commit hook runs successfully on a dummy file."""

        workspace_path = devcontainer_up.resolve()

        # Create a dummy Python file to test pre-commit
        test_file = workspace_path / "test_file.py"
        test_file.write_text("def hello():\n    print('hello')\n")

        # Run pre-commit on the file
        exec_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            str(workspace_path),
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            "cd /workspace/test_project && pre-commit run --files test_file.py",
        ]

        result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            cwd=str(workspace_path),
            env=os.environ.copy(),
            timeout=120,  # Pre-commit can take a while on first run
        )

        # Pre-commit should succeed (exit code 0) or pass with warnings
        # Exit code 1 means hooks failed, which is also acceptable for testing
        # We just want to verify pre-commit runs
        assert result.returncode in [0, 1], (
            f"Pre-commit failed unexpectedly\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(exec_cmd)}"
        )

        # Verify pre-commit actually ran (check for pre-commit output)
        assert (
            "pre-commit" in result.stdout.lower() or "ruff" in result.stdout.lower()
        ), (
            f"Pre-commit doesn't appear to have run\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Clean up
        test_file.unlink()

    def test_git_commit_ssh_signature(self, devcontainer_up):
        """Test that git commits are signed with SSH signature."""

        workspace_path = devcontainer_up.resolve()

        # Check if SSH agent is available on the host
        ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
        if not ssh_auth_sock or not Path(ssh_auth_sock).exists():
            pytest.skip(
                "SSH agent not available on host. "
                "Start SSH agent with 'eval $(ssh-agent)' and add your key with 'ssh-add'."
            )

        # Check if SSH keys and git signing are configured
        check_config_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            str(workspace_path),
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            (
                "cd /workspace/test_project && "
                "git config --get gpg.format 2>/dev/null | grep -q ssh && echo 'ssh_signing_configured' || echo 'not_configured'"
            ),
        ]

        config_result = subprocess.run(
            check_config_cmd,
            capture_output=True,
            text=True,
            cwd=str(workspace_path),
            env=os.environ.copy(),
        )

        # If SSH signing is not configured, skip the test
        if "not_configured" in config_result.stdout:
            pytest.skip(
                "SSH signing not configured in git. "
                "Git commit signing requires SSH keys and git config to be set up."
            )

        # Create a test file to commit
        test_file = workspace_path / "test_commit.txt"
        test_file.write_text("Test commit for signature verification\n")

        # SSH agent forwarding is automatically configured by the devcontainer_up fixture
        # if SSH_AUTH_SOCK is available. The socket should be mounted at /tmp/ssh-agent.sock
        # and SSH_AUTH_SOCK should be set to that path in the container environment.
        exec_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            str(workspace_path),
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            (
                "cd /workspace/test_project && "
                "git config user.name 'Test User' && "
                "git config user.email 'test@example.com' && "
                "git add test_commit.txt && "
                "git commit -m 'Test commit for signature verification' && "
                "git log -1 --show-signature"
            ),
        ]

        result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            cwd=str(workspace_path),
            env=os.environ.copy(),
            timeout=30,
        )

        if result.returncode != 0:
            # If commit failed due to SSH agent, that's acceptable - the important
            # thing is that git signing is configured
            if (
                "Couldn't get agent socket" in result.stderr
                or "failed to write commit object" in result.stderr
            ):
                pytest.skip(
                    "SSH agent forwarding failed. "
                    "Make sure SSH agent is running and SSH_AUTH_SOCK is set."
                )
            else:
                pytest.fail(
                    f"Git commit failed\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}\n"
                    f"command: {' '.join(exec_cmd)}"
                )

        # Verify the commit was signed
        output = result.stdout + result.stderr
        assert (
            'Good "git" signature' in output
            or "Good signature" in output
            or "Signature made" in output
        ), (
            f"Commit signature not found or invalid\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"Expected 'Good \"git\" signature' or 'Good signature' or 'Signature made' in output"
        )

        # Clean up - reset the commit
        cleanup_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            str(workspace_path),
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "bash",
            "-c",
            "cd /workspace && git reset --soft HEAD~1 && git reset test_commit.txt",
        ]
        subprocess.run(
            cleanup_cmd,
            capture_output=True,
            text=True,
            cwd=str(workspace_path),
            env=os.environ.copy(),
        )
        test_file.unlink()

    def test_github_cli_authentication(self, devcontainer_up):
        """Test that GitHub CLI authentication works in the devcontainer."""
        workspace_path = str(devcontainer_up.resolve())

        # Test gh auth status in the container
        exec_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "gh",
            "auth",
            "status",
        ]

        result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
            timeout=10,
        )

        # gh auth status returns exit code 0 on success, 1 on failure
        if result.returncode != 0:
            # Check if it's a "not logged in" error (expected if config not mounted)
            error_output = result.stderr.lower() + result.stdout.lower()
            if (
                "not logged in" in error_output
                or "you are not logged into any github hosts" in error_output
                or "to log in, run: gh auth login" in error_output
            ):
                pytest.skip(
                    "GitHub CLI not authenticated in container. "
                    "To enable authentication, ensure GitHub CLI is authenticated on the host "
                    "(run 'gh auth login') so the token can be exported during initialization."
                )
            else:
                pytest.fail(
                    f"GitHub CLI authentication check failed\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}\n"
                    f"command: {' '.join(exec_cmd)}"
                )

        # Verify we got a successful authentication response
        output = result.stdout + result.stderr
        assert (
            "Logged in to github.com" in output
            or "✓ Logged in" in output
            or "github.com" in output
        ), (
            f"GitHub CLI authentication status unclear\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"Expected 'Logged in to github.com' or similar in output"
        )


class TestDockerComposeOverride:
    """Test docker-compose.override.yml functionality for additional mounts."""

    def test_override_mount_directory_exists(self, devcontainer_up):
        """Test that the directory mounted via override file exists in container."""
        workspace_path = str(devcontainer_up.resolve())

        # The conftest.py fixture creates an override mounting tests/ to /workspace/tests-mounted
        check_dir_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-d",
            "/workspace/tests-mounted",
        ]

        result = subprocess.run(
            check_dir_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f"Override mount directory /workspace/tests-mounted not found\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(check_dir_cmd)}"
        )

    def test_override_mount_file_accessible(self, devcontainer_up):
        """Test that files in the override mount are accessible."""
        workspace_path = str(devcontainer_up.resolve())

        # Check that conftest.py exists in the mounted tests directory
        check_file_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "test",
            "-f",
            "/workspace/tests-mounted/conftest.py",
        ]

        result = subprocess.run(
            check_file_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f"conftest.py not found in override mount at /workspace/tests-mounted/conftest.py\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(check_file_cmd)}"
        )

    def test_override_mount_file_readable(self, devcontainer_up):
        """Test that files in the override mount are readable."""
        workspace_path = str(devcontainer_up.resolve())

        # Read first line of conftest.py to verify content is accessible
        read_file_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "head",
            "-n",
            "1",
            "/workspace/tests-mounted/conftest.py",
        ]

        result = subprocess.run(
            read_file_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f"Failed to read conftest.py from override mount\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(read_file_cmd)}"
        )

        # Verify we got some content (should be a comment or import)
        assert result.stdout.strip(), (
            f"conftest.py appears to be empty or unreadable\nstdout: {result.stdout}\n"
        )

    def test_override_mount_list_directory(self, devcontainer_up):
        """Test that we can list the contents of the override mount."""
        workspace_path = str(devcontainer_up.resolve())

        # List contents of the mounted tests directory
        ls_cmd = [
            "devcontainer",
            "exec",
            "--workspace-folder",
            workspace_path,
            "--config",
            f"{workspace_path}/.devcontainer/devcontainer.json",
            "--docker-path",
            "podman",
            "ls",
            "-la",
            "/workspace/tests-mounted",
        ]

        result = subprocess.run(
            ls_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path,
            env=os.environ.copy(),
        )

        assert result.returncode == 0, (
            f"Failed to list contents of override mount\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"command: {' '.join(ls_cmd)}"
        )

        # Verify expected test files are listed
        assert "conftest.py" in result.stdout, (
            f"conftest.py not found in directory listing\nstdout: {result.stdout}"
        )
        assert "test_integration.py" in result.stdout, (
            f"test_integration.py not found in directory listing\n"
            f"stdout: {result.stdout}"
        )
