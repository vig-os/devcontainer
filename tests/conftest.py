"""
Shared fixtures for all devc container tests.
"""

import atexit
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pexpect
import pytest
import testinfra


@pytest.fixture(scope="session")
def container_tag():
    """
    Get the container tag from TEST_CONTAINER_TAG environment variable.
    Defaults to 'dev' if not set.
    """
    return os.environ.get("TEST_CONTAINER_TAG", "dev")


@pytest.fixture(scope="session")
def container_image(container_tag):
    """
    Construct the full container image name and verify it exists.
    """
    image_name = f"ghcr.io/vig-os/devcontainer:{container_tag}"

    # Check if image exists
    result = subprocess.run(
        ["podman", "image", "exists", image_name], capture_output=True, text=True
    )

    if result.returncode != 0:
        pytest.fail(
            f"Podman image {image_name} not found. "
            f"Please build it first with 'make build'"
        )

    return image_name


@pytest.fixture(scope="session")
def test_container(container_image):
    """
    Start a container from the image and return its name.
    The container will be cleaned up after all tests.
    """
    # Create a unique container name
    import time

    container_id = f"test-devcontainer-{int(time.time())}"

    # Start the container in detached mode
    result = subprocess.run(
        [
            "podman",
            "run",
            "-d",
            "--name",
            container_id,
            container_image,
            "sleep",
            "infinity",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Failed to start container from {container_image}\nstderr: {result.stderr}"
        )

    # Register cleanup function
    def cleanup():
        subprocess.run(["podman", "stop", container_id], capture_output=True, text=True)
        subprocess.run(["podman", "rm", container_id], capture_output=True, text=True)

    atexit.register(cleanup)

    yield container_id

    # Cleanup
    cleanup()


@pytest.fixture(scope="session")
def host(test_container):
    """
    Create a testinfra connection to the running container.
    This fixture is used by all testinfra tests.
    """
    # Create a podman connection to the running container
    # We use 'podman://' prefix to tell testinfra to use podman
    connection_string = f"podman://{test_container}"

    # Create the host connection
    host = testinfra.host.get_host(connection_string)

    return host


@pytest.fixture(scope="session")
def initialized_workspace(container_image):
    """
    Create a temporary workspace directory and initialize it with init-workspace.

    The workspace is created within the project directory for gitconfig reasons.
    It will be cleaned up when the test session ends.
    """
    # Get the project root (assuming conftest.py is in tests/)
    project_root = Path(__file__).resolve().parents[1]

    # Create a temporary directory within the project for gitconfig reasons
    tests_tmp_dir = project_root / "tests" / "tmp"
    tests_tmp_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique temporary directory for this test session
    workspace_dir = tempfile.mkdtemp(
        dir=str(tests_tmp_dir), prefix="workspace-devcontainer-"
    )
    workspace_path = Path(workspace_dir)

    # Register cleanup function
    def cleanup():
        if workspace_path.exists():
            shutil.rmtree(workspace_path, ignore_errors=True)

    atexit.register(cleanup)

    # Run init-workspace in the container
    # The script requires an interactive terminal (-it) and expects input
    project_name = "test_project"
    organization_name = "Test Org"

    # Use pexpect to handle interactive terminal input
    cmd = [
        "podman",
        "run",
        "-it",
        "--rm",
        "-v",
        f"{workspace_path}:/workspace",
        container_image,
        "/root/assets/init-workspace.sh",
    ]

    try:
        # Spawn the process with pexpect
        child = pexpect.spawn(" ".join(cmd), encoding="utf-8", timeout=60)

        # Wait for the prompt and send the project name
        child.expect("Enter a short name", timeout=30)
        child.sendline(project_name)

        child.expect("Enter the name of your organization, e.g. 'vigOS': ", timeout=30)
        child.sendline(organization_name)

        # Wait for the process to complete
        child.expect(pexpect.EOF, timeout=60)
        child.close()

        # Check return code
        if child.exitstatus != 0:
            cleanup()
            pytest.fail(
                f"Failed to initialize workspace with init-workspace.sh\n"
                f"Return code: {child.exitstatus}\n"
                f"Output: {child.before}"
            )
    except pexpect.TIMEOUT:
        cleanup()
        pytest.fail(
            f"Timeout while initializing workspace with init-workspace.sh\n"
            f"Output: {child.before if 'child' in locals() else 'N/A'}"
        )
    except pexpect.ExceptionPexpect as e:
        cleanup()
        pytest.fail(f"Error while initializing workspace with init-workspace.sh: {e}")

    # Verify the workspace was initialized
    if not (workspace_path / "README.md").exists():
        cleanup()
        pytest.fail(
            f"Workspace initialization failed - README.md not found in {workspace_path}\n"
            f"Workspace contents: {list[Path](workspace_path.iterdir())}"
        )

    yield workspace_path

    # Cleanup
    cleanup()


@pytest.fixture(scope="session")
def devcontainer_up(initialized_workspace):
    """
    Set up a devcontainer using devcontainer CLI.

    This fixture:
    - Builds and starts the devcontainer using `devcontainer up`
    - SSH agent forwarding is disabled on macOS+podman due to VM isolation
    - Yields the workspace path for tests to use
    - Cleans up by running `devcontainer down` after all tests

    Note: This fixture takes some time to set up.
    """
    import json
    import os
    import platform
    import shutil
    import subprocess

    workspace_path = initialized_workspace.resolve()

    # Check if devcontainer CLI is available
    if not shutil.which("devcontainer"):
        pytest.skip(
            "devcontainer CLI not available. "
            "Install with: npm install -g @devcontainers/cli@0.80.1"
        )

    # Prepare environment for devcontainer CLI
    env = os.environ.copy()

    # On macOS with podman, disable SSH agent forwarding
    # Podman runs in a VM that cannot access /private/tmp/com.apple.launchd.*
    # VS Code Dev Containers extension handles this automatically, but devcontainer
    # CLI does not. Since tests don't require SSH operations, we disable it.
    docker_path = "podman"
    original_config = None
    devcontainer_json_path = workspace_path / ".devcontainer" / "devcontainer.json"
    if (
        platform.system() == "Darwin"
        and docker_path == "podman"
        and "SSH_AUTH_SOCK" in env
    ):
        print("[DEBUG] Disabling SSH agent forwarding on macOS+podman")
        print("[DEBUG] (VM isolation prevents socket mounting)")
        del env["SSH_AUTH_SOCK"]
    elif "SSH_AUTH_SOCK" in env and Path(env["SSH_AUTH_SOCK"]).exists():
        print("[DEBUG] Setting up SSH agent forwarding in devcontainer.json")
        # Read the devcontainer.json
        with devcontainer_json_path.open() as f:
            config = json.load(f)

        # Store original config for restoration
        original_config = json.dumps(config, indent=4)

        # Add SSH agent forwarding if not already present
        if "mounts" not in config:
            config["mounts"] = []
        if "remoteEnv" not in config:
            config["remoteEnv"] = {}

        # Track if we made changes
        ssh_agent_added = False

        # Check if SSH agent mount already exists
        ssh_mount = (
            f"source={env['SSH_AUTH_SOCK']},target=/tmp/ssh-agent.sock,type=bind"
        )
        if ssh_mount not in config["mounts"]:
            config["mounts"].append(ssh_mount)
            ssh_agent_added = True

        # Set SSH_AUTH_SOCK environment variable
        if config["remoteEnv"].get("SSH_AUTH_SOCK") != "/tmp/ssh-agent.sock":
            config["remoteEnv"]["SSH_AUTH_SOCK"] = "/tmp/ssh-agent.sock"
            ssh_agent_added = True

        # Write back the modified config
        if ssh_agent_added:
            with devcontainer_json_path.open("w") as f:
                json.dump(config, f, indent=4)
            print("[DEBUG] Added SSH agent forwarding to devcontainer.json")

    # Create docker-compose.override.yml for testing additional mounts
    override_path = workspace_path / ".devcontainer" / "docker-compose.override.yml"
    tests_dir = Path(__file__).parent.resolve()  # Path to tests/ directory
    override_content = f"""version: '3.8'

services:
  devcontainer:
    volumes:
      # Mount tests directory for testing override functionality
      - {tests_dir}:/workspace/tests-mounted:cached
"""
    with override_path.open("w") as f:
        f.write(override_content)
    print(f"[DEBUG] Created docker-compose.override.yml mounting {tests_dir}")

    # Modify devcontainer.json to include the override file
    # The devcontainer CLI doesn't auto-discover override files like docker-compose does
    with devcontainer_json_path.open() as f:
        config = json.load(f)

    if not original_config:
        original_config = json.dumps(config, indent=4)

    # Change dockerComposeFile to an array including the override
    if isinstance(config.get("dockerComposeFile"), str):
        config["dockerComposeFile"] = [
            config["dockerComposeFile"],
            "docker-compose.override.yml",
        ]
    elif isinstance(config.get("dockerComposeFile"), list):
        config["dockerComposeFile"].append("docker-compose.override.yml")

    with devcontainer_json_path.open("w") as f:
        json.dump(config, f, indent=4)
    print("[DEBUG] Updated devcontainer.json to include docker-compose.override.yml")

    # Build and start the devcontainer
    up_cmd = [
        "devcontainer",
        "up",
        "--workspace-folder",
        str(workspace_path),
        "--config",
        f"{workspace_path}/.devcontainer/devcontainer.json",
        "--remove-existing-container",
        "--docker-path",
        docker_path,
        "--log-level",
        "trace",
    ]

    print(f"\n[DEBUG] Setting up devcontainer: {' '.join(up_cmd)}")
    print("[DEBUG] This may take about a minute...")

    up_result = subprocess.run(
        up_cmd,
        capture_output=True,
        text=True,
        cwd=str(workspace_path),
        env=env,  # Use environment without SSH_AUTH_SOCK on macOS
        timeout=120,
    )

    if up_result.returncode != 0:
        pytest.fail(
            f"devcontainer up failed\n"
            f"stdout: {up_result.stdout}\n"
            f"stderr: {up_result.stderr}\n"
            f"command: {' '.join(up_cmd)}"
        )

    print("[DEBUG] Devcontainer is up and running")

    yield workspace_path

    # Clean up: stop the devcontainer
    print("\n[DEBUG] Cleaning up devcontainer...")
    down_cmd = [
        "devcontainer",
        "down",
        "--workspace-folder",
        str(workspace_path),
        "--config",
        f"{workspace_path}/.devcontainer/devcontainer.json",
        "--docker-path",
        docker_path,
    ]
    down_result = subprocess.run(
        down_cmd,
        capture_output=True,
        text=True,
        cwd=str(workspace_path),
        env=os.environ.copy(),
    )

    if down_result.returncode != 0:
        print(
            f"[WARNING] devcontainer down failed (non-fatal):\n"
            f"stdout: {down_result.stdout}\n"
            f"stderr: {down_result.stderr}\n"
        )

    # Clean up docker-compose.override.yml if it exists
    override_path = workspace_path / ".devcontainer" / "docker-compose.override.yml"
    if override_path.exists():
        override_path.unlink()
        print("[DEBUG] Removed docker-compose.override.yml")

    # Restore original devcontainer.json if we modified it
    if original_config:
        with devcontainer_json_path.open("w") as f:
            f.write(original_config)
        print("[DEBUG] Restored original devcontainer.json")
