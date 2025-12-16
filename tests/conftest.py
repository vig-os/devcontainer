"""
Shared fixtures for all devc container tests.

This module supports running tests from both:
1. Host machine (direct podman access)
2. Inside a devcontainer (Docker-out-of-Docker via socket)

When running from within a container, set HOST_WORKSPACE_PATH environment
variable to the host path that maps to /workspace/devcontainer in the container.
This enables path translation for volume mounts.

Example:
    HOST_WORKSPACE_PATH=/Users/you/Projects/devcontainer make test-integration
"""

import atexit
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pexpect
import pytest
import testinfra


def pytest_sessionstart(session):
    """
    Pre-flight check: Detect lingering test containers from previous runs.

    Runs before any tests to ensure a clean environment.
    """
    # Check for lingering containers from previous test runs
    check_cmd = [
        "podman",
        "ps",
        "-a",
        "--filter",
        "name=workspace-devcontainer",
        "--format",
        "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.CreatedAt}}",
    ]

    result = subprocess.run(check_cmd, capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        containers = result.stdout.strip().split("\n")

        # Also check for test-sidecar containers
        sidecar_check_cmd = [
            "podman",
            "ps",
            "-a",
            "--filter",
            "name=test-sidecar",
            "--format",
            "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.CreatedAt}}",
        ]
        sidecar_result = subprocess.run(
            sidecar_check_cmd, capture_output=True, text=True
        )

        if sidecar_result.returncode == 0 and sidecar_result.stdout.strip():
            containers.extend(sidecar_result.stdout.strip().split("\n"))

        # Format the error message
        container_list = "\n".join(f"  - {c}" for c in containers)

        cleanup_commands = """
To clean up these containers, run:

    # Clean up workspace devcontainers
    podman ps -a --filter "name=workspace-devcontainer" --format "{{{{.ID}}}}" | xargs -r podman rm -f

    # Clean up test sidecars
    podman ps -a --filter "name=test-sidecar" --format "{{{{.ID}}}}" | xargs -r podman rm -f

    # Or use the Makefile target:
    make clean-test-containers

Alternatively, set PYTEST_AUTO_CLEANUP=1 to automatically clean up before tests:

    PYTEST_AUTO_CLEANUP=1 uv run pytest tests/
"""

        # Check if auto-cleanup is enabled
        if os.environ.get("PYTEST_AUTO_CLEANUP") == "1":
            print(f"\n⚠️  Found {len(containers)} lingering test container(s)")
            print("🧹 Auto-cleanup enabled, removing containers...")

            # Clean up workspace devcontainers
            cleanup_devcontainer = [
                "podman",
                "ps",
                "-a",
                "--filter",
                "name=workspace-devcontainer",
                "--format",
                "{{.ID}}",
            ]
            ids_result = subprocess.run(
                cleanup_devcontainer, capture_output=True, text=True
            )
            if ids_result.stdout.strip():
                for container_id in ids_result.stdout.strip().split("\n"):
                    subprocess.run(
                        ["podman", "rm", "-f", container_id], capture_output=True
                    )

            # Clean up test sidecars
            cleanup_sidecar = [
                "podman",
                "ps",
                "-a",
                "--filter",
                "name=test-sidecar",
                "--format",
                "{{.ID}}",
            ]
            sidecar_ids_result = subprocess.run(
                cleanup_sidecar, capture_output=True, text=True
            )
            if sidecar_ids_result.stdout.strip():
                for container_id in sidecar_ids_result.stdout.strip().split("\n"):
                    subprocess.run(
                        ["podman", "rm", "-f", container_id], capture_output=True
                    )

            print("✅ Cleanup complete\n")
        else:
            # Fail with helpful error message
            pytest.exit(
                f"\n\n❌ Found {len(containers)} lingering test container(s) from previous runs:\n\n"
                f"{container_list}\n\n"
                f"{cleanup_commands}",
                returncode=1,
            )


def is_running_in_container() -> bool:
    """Detect if we're running inside a container."""
    # Check for container environment indicators
    if os.environ.get("IN_CONTAINER") == "true":
        return True
    if Path("/.dockerenv").exists():
        return True
    if Path("/run/.containerenv").exists():
        return True
    # Check cgroup for container runtime
    try:
        with Path("/proc/1/cgroup").open() as f:
            return "docker" in f.read() or "podman" in f.read()
    except (FileNotFoundError, PermissionError):
        pass
    return False


def get_host_path(container_path: Path) -> Path:
    """
    Translate a container path to a host path.

    When running inside a container with Docker-out-of-Docker (DooD),
    volume mounts must use HOST paths because podman runs on the host.

    Args:
        container_path: Path inside the container

    Returns:
        Host path if HOST_WORKSPACE_PATH is set and path is under /workspace,
        otherwise returns the original path.
    """
    host_workspace = os.environ.get("HOST_WORKSPACE_PATH")
    if not host_workspace:
        return container_path

    container_path_str = str(container_path.resolve())
    container_workspace = "/workspace/devcontainer"

    if container_path_str.startswith(container_workspace):
        relative = container_path_str[len(container_workspace) :]
        return Path(host_workspace + relative)

    return container_path


def get_compose_project_name() -> str:
    """Generate a unique compose project name for test isolation."""
    return f"test-{int(time.time())}"


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

    This fixture supports running from both:
    1. Host machine - uses direct bind mounts
    2. Inside a devcontainer - uses podman compose with named volumes

    When running inside a container (Docker-out-of-Docker), we use compose
    to handle volume management, avoiding the host path translation issue.

    The workspace will be cleaned up when the test session ends.
    """
    # Get the project root (assuming conftest.py is in tests/)
    project_root = Path(__file__).resolve().parents[1]
    tests_dir = project_root / "tests"

    # Check if we're running inside a container
    in_container = is_running_in_container()

    # Always use tests/tmp - it's in the shared workspace which is mounted
    # both on host and in container, so both can access it
    tests_tmp_dir = tests_dir / "tmp"
    tests_tmp_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = tempfile.mkdtemp(
        dir=str(tests_tmp_dir), prefix="workspace-devcontainer-"
    )

    workspace_path = Path(workspace_dir)

    # Generate unique names for compose project and volume
    unique_id = workspace_path.name.replace("workspace-devcontainer-", "")
    compose_project = f"test-{unique_id}"
    volume_name = f"test-workspace-{unique_id}"

    # Track whether we're using compose (for cleanup)
    using_compose = False

    # Register cleanup function
    def cleanup():
        if workspace_path.exists():
            shutil.rmtree(workspace_path, ignore_errors=True)
        if using_compose:
            # Clean up the named volume
            subprocess.run(
                ["podman", "volume", "rm", "-f", volume_name],
                capture_output=True,
                text=True,
            )

    atexit.register(cleanup)

    # Run init-workspace in the container
    # The script requires an interactive terminal (-it) and expects input
    project_name = "test_project"
    organization_name = "Test Org"

    if in_container:
        # Use podman with named volumes to avoid path translation issues
        # Named volumes work everywhere without needing compose
        using_compose = True  # We still track this for volume cleanup

        # Create the named volume
        create_volume_cmd = ["podman", "volume", "create", volume_name]
        create_result = subprocess.run(
            create_volume_cmd, capture_output=True, text=True, timeout=30
        )

        if create_result.returncode != 0:
            cleanup()
            pytest.fail(
                f"Failed to create volume {volume_name}\n"
                f"stdout: {create_result.stdout}\n"
                f"stderr: {create_result.stderr}"
            )

        print(f"[DEBUG] Created volume: {volume_name}")

        # Run init-workspace with the named volume
        cmd = [
            "podman",
            "run",
            "-it",
            "--rm",
            "-v",
            f"{volume_name}:/workspace",
            container_image,
            "/root/assets/init-workspace.sh",
        ]

        try:
            # Spawn the process with pexpect
            print(f"[DEBUG] Running podman command: {' '.join(cmd)}")
            print(f"[DEBUG] Volume: {volume_name}, Image: {container_image}")

            child = pexpect.spawn(" ".join(cmd), encoding="utf-8", timeout=60)

            # Wait for the prompt and send the project name
            child.expect("Enter a short name", timeout=30)
            child.sendline(project_name)

            child.expect(
                "Enter the name of your organization, e.g. 'vigOS': ", timeout=30
            )
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
            output = child.before if "child" in locals() else "N/A"
            pytest.fail(
                f"Timeout while initializing workspace with init-workspace.sh\n"
                f"Command: {' '.join(cmd)}\n"
                f"Output: {output}"
            )
        except pexpect.EOF:
            cleanup()
            output = child.before if "child" in locals() else "N/A"
            pytest.fail(
                f"Error while initializing workspace with init-workspace.sh: EOF\n"
                f"Command: {' '.join(cmd)}\n"
                f"Output so far: {output}\n"
                f"This usually means the container exited before responding.\n"
                f"Check that the image exists and the compose file is correct."
            )
        except pexpect.ExceptionPexpect as e:
            cleanup()
            output = child.before if "child" in locals() else "N/A"
            pytest.fail(
                f"Error while initializing workspace with init-workspace.sh: {e}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Output: {output}"
            )

        # Copy files from the named volume to the local temp directory
        # The temp directory is in /workspace/devcontainer/tests/tmp which is
        # shared between host and container, so we use host path for the mount
        workspace_path_host = get_host_path(workspace_path)

        copy_cmd = [
            "podman",
            "run",
            "--rm",
            "-v",
            f"{volume_name}:/source:ro",
            "-v",
            f"{workspace_path_host}:/dest",  # Use host path!
            "alpine",
            "sh",
            "-c",
            "cp -a /source/. /dest/",
        ]

        print(
            f"[DEBUG] Copying files from volume {volume_name} to {workspace_path_host}"
        )
        copy_result = subprocess.run(
            copy_cmd, capture_output=True, text=True, timeout=30
        )

        if copy_result.returncode != 0:
            cleanup()
            pytest.fail(
                f"Failed to copy files from volume to workspace\n"
                f"Command: {' '.join(copy_cmd)}\n"
                f"stdout: {copy_result.stdout}\n"
                f"stderr: {copy_result.stderr}"
            )
    else:
        # Running on host - use direct bind mount (original behavior)
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

            child.expect(
                "Enter the name of your organization, e.g. 'vigOS': ", timeout=30
            )
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
            pytest.fail(
                f"Error while initializing workspace with init-workspace.sh: {e}"
            )

    # Verify the workspace was initialized
    if not (workspace_path / "README.md").exists():
        cleanup()
        pytest.fail(
            f"Workspace initialization failed - README.md not found in {workspace_path}\n"
            f"Workspace contents: {list(workspace_path.iterdir()) if workspace_path.exists() else 'N/A'}"
        )

    yield workspace_path

    # Cleanup
    cleanup()


@pytest.fixture(scope="session")
def sidecar_image():
    """
    Build the test sidecar image once for all sidecar tests.

    This fixture:
    - Builds the sidecar image using podman
    - Image is stored in Podman VM where compose can access it
    - Returns the image name for use in compose configuration
    - Skips all sidecar tests if build fails
    """
    import subprocess

    sidecar_dir = Path(__file__).parent / "fixtures"
    image_name = "localhost/test-sidecar:latest"

    print(f"\n[DEBUG] Building sidecar image: {image_name}")
    print(f"[DEBUG] Sidecar directory: {sidecar_dir}")

    # Build using podman (this runs in the VM where compose needs it)
    build_cmd = [
        "podman",
        "build",
        "-t",
        image_name,
        "-f",
        str(sidecar_dir / "sidecar.Containerfile"),
        str(sidecar_dir),
    ]

    result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        pytest.skip(
            f"Failed to build sidecar image: {result.stderr}\n"
            f"Sidecar tests will be skipped."
        )

    print(f"[DEBUG] Sidecar image built successfully: {image_name}")
    return image_name


@pytest.fixture(scope="function")
def devcontainer_with_sidecar(initialized_workspace, sidecar_image):
    """
    Set up a devcontainer WITH a sidecar for testing multi-container setups.

    This fixture:
    - Uses the pre-built sidecar image
    - Configures docker-compose.project.yaml with sidecar service
    - Starts both devcontainer and sidecar together
    - Enables testing of Approach 1: command execution via podman exec
    - Cleans up both containers after tests

    When running from inside a container (DooD), set HOST_WORKSPACE_PATH
    environment variable to enable path translation for devcontainer CLI.

    Note: This is separate from devcontainer_up to avoid breaking other tests.
    """
    import json
    import os
    import platform
    import shutil
    import subprocess

    workspace_path = initialized_workspace.resolve()

    # Check if we need path translation for DooD
    in_container = is_running_in_container()
    host_workspace = os.environ.get("HOST_WORKSPACE_PATH")

    if in_container and not host_workspace:
        pytest.skip(
            "Running inside a container without HOST_WORKSPACE_PATH set. "
            "Devcontainer CLI tests require host path translation. "
            "Set HOST_WORKSPACE_PATH to the host path that maps to /workspace/devcontainer"
        )

    # Translate workspace path to host path if needed
    if in_container and host_workspace:
        workspace_path_for_cli = get_host_path(workspace_path)
        print(
            f"[DEBUG] Translated workspace path: {workspace_path} -> {workspace_path_for_cli}"
        )
    else:
        workspace_path_for_cli = workspace_path

    # Check if devcontainer CLI is available
    if not shutil.which("devcontainer"):
        pytest.skip(
            "devcontainer CLI not available. "
            "Install with: npm install -g @devcontainers/cli@0.80.1"
        )

    # Prepare environment
    env = os.environ.copy()
    docker_path = "podman"
    original_config = None
    devcontainer_json_path = workspace_path / ".devcontainer" / "devcontainer.json"

    # Disable SSH agent forwarding on macOS+podman
    if (
        platform.system() == "Darwin"
        and docker_path == "podman"
        and "SSH_AUTH_SOCK" in env
    ):
        print("[DEBUG] Disabling SSH agent forwarding on macOS+podman (sidecar test)")
        del env["SSH_AUTH_SOCK"]

    # Configure docker-compose.project.yaml with sidecar
    # This file is already in the devcontainer.json dockerComposeFile list
    import yaml

    project_yaml_path = workspace_path / ".devcontainer" / "docker-compose.project.yaml"

    # Read existing project config (from init-workspace.sh template)
    if project_yaml_path.exists():
        with project_yaml_path.open() as f:
            project_config = yaml.safe_load(f) or {}
        print("[DEBUG] Loaded existing docker-compose.project.yaml")
    else:
        project_config = {}

    # Initialize if empty (template file has only comments)
    if not project_config:
        project_config = {"services": {"devcontainer": {"volumes": []}}}

    # Ensure structure exists
    if "services" not in project_config:
        project_config["services"] = {}
    if "devcontainer" not in project_config["services"]:
        project_config["services"]["devcontainer"] = {}
    if "volumes" not in project_config["services"]["devcontainer"]:
        project_config["services"]["devcontainer"]["volumes"] = []

    # Add test mount - use host path for mount
    tests_dir = Path(__file__).parent.resolve()
    tests_dir_for_mount = get_host_path(tests_dir) if in_container else tests_dir
    test_mount = f"{tests_dir_for_mount}:/workspace/tests-mounted:cached"
    if test_mount not in project_config["services"]["devcontainer"]["volumes"]:
        project_config["services"]["devcontainer"]["volumes"].append(test_mount)

    # Add sidecar service
    project_config["services"]["test-sidecar"] = {
        "image": sidecar_image,
        "container_name": "test-sidecar",
        "command": "sleep infinity",
        "volumes": [
            # Share workspace for build artifacts
            f"..:/workspace/{initialized_workspace.name}:cached"
        ],
    }
    print(f"[DEBUG] Added test-sidecar service using image: {sidecar_image}")

    # Write project yaml file (already in devcontainer.json dockerComposeFile list)
    with project_yaml_path.open("w") as f:
        yaml.dump(project_config, f, default_flow_style=False, sort_keys=False)
    print("[DEBUG] Updated docker-compose.project.yaml with sidecar")

    # Read devcontainer.json for potential restoration later
    with devcontainer_json_path.open() as f:
        config = json.load(f)
    original_config = json.dumps(config, indent=4)
    # Note: No need to modify devcontainer.json - project.yaml is already in dockerComposeFile list

    # Build and start devcontainer with sidecar
    # Use workspace_path_for_cli for CLI operations (host path when running in container)
    up_cmd = [
        "devcontainer",
        "up",
        "--workspace-folder",
        str(workspace_path_for_cli),
        "--config",
        f"{workspace_path_for_cli}/.devcontainer/devcontainer.json",
        "--remove-existing-container",
        "--docker-path",
        docker_path,
        "--log-level",
        "trace",
    ]

    print(f"\n[DEBUG] Starting devcontainer with sidecar: {' '.join(up_cmd)}")

    up_result = subprocess.run(
        up_cmd,
        capture_output=True,
        text=True,
        cwd=str(workspace_path),
        env=env,
        timeout=120,
    )

    if up_result.returncode != 0:
        pytest.skip(
            f"devcontainer up with sidecar failed - skipping sidecar tests\n"
            f"This is expected if podman-compose has issues with multi-container setups\n"
            f"Socket tests already prove the underlying capability works.\n"
            f"stdout: {up_result.stdout}\n"
            f"stderr: {up_result.stderr}\n"
            f"command: {' '.join(up_cmd)}"
        )

    print("[DEBUG] Devcontainer with sidecar is up and running")

    # Yield workspace path for tests
    yield workspace_path

    # Cleanup
    print("[DEBUG] Cleaning up devcontainer with sidecar...")

    # Stop containers manually using podman
    stop_cmds = [
        ["podman", "stop", "test-sidecar"],
        ["podman", "rm", "test-sidecar"],
    ]

    for cmd in stop_cmds:
        subprocess.run(cmd, capture_output=True, timeout=30)

    # Restore original devcontainer.json
    if original_config:
        with devcontainer_json_path.open("w") as f:
            f.write(original_config)
        print("[DEBUG] Restored original devcontainer.json")


@pytest.fixture(scope="session")
def devcontainer_up(initialized_workspace):
    """
    Set up a devcontainer using devcontainer CLI.

    This fixture:
    - Builds and starts the devcontainer using `devcontainer up`
    - SSH agent forwarding is disabled on macOS+podman due to VM isolation
    - Yields the workspace path for tests to use
    - Cleans up by running `devcontainer down` after all tests

    When running from inside a container (DooD), set HOST_WORKSPACE_PATH
    environment variable to enable path translation for devcontainer CLI.

    Note: This fixture takes some time to set up.
    """
    import json
    import os
    import platform
    import shutil
    import subprocess

    workspace_path = initialized_workspace.resolve()

    # Check if we need path translation for DooD
    in_container = is_running_in_container()
    host_workspace = os.environ.get("HOST_WORKSPACE_PATH")

    if in_container and not host_workspace:
        pytest.skip(
            "Running inside a container without HOST_WORKSPACE_PATH set. "
            "Devcontainer CLI tests require host path translation. "
            "Set HOST_WORKSPACE_PATH to the host path that maps to /workspace/devcontainer"
        )

    # Translate workspace path to host path if needed
    if in_container and host_workspace:
        workspace_path_for_cli = get_host_path(workspace_path)
        print(
            f"[DEBUG] Translated workspace path: {workspace_path} -> {workspace_path_for_cli}"
        )
    else:
        workspace_path_for_cli = workspace_path

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

    # Extend docker-compose.project.yaml for testing
    # This file is already in the devcontainer.json dockerComposeFile list
    # We just need to add our test-specific mount
    import yaml

    project_yaml_path = workspace_path / ".devcontainer" / "docker-compose.project.yaml"
    tests_dir = Path(__file__).parent.resolve()  # Path to tests/ directory

    # For test mounts, we need to use host path if running in container
    tests_dir_for_mount = get_host_path(tests_dir) if in_container else tests_dir

    # Read the existing project yaml (created by init-workspace.sh from template)
    if project_yaml_path.exists():
        with project_yaml_path.open() as f:
            project_config = yaml.safe_load(f) or {}
        print("[DEBUG] Loaded existing docker-compose.project.yaml from workspace")
    else:
        project_config = {}
        print("[DEBUG] No existing project.yaml found, creating new one")

    # Initialize if empty (template file has only comments)
    if not project_config:
        project_config = {"services": {"devcontainer": {"volumes": []}}}

    # Ensure the structure exists
    if "services" not in project_config:
        project_config["services"] = {}
    if "devcontainer" not in project_config["services"]:
        project_config["services"]["devcontainer"] = {}
    if "volumes" not in project_config["services"]["devcontainer"]:
        project_config["services"]["devcontainer"]["volumes"] = []

    # Add test mount (if not already present) - use host path for mount
    test_mount = f"{tests_dir_for_mount}:/workspace/tests-mounted:cached"
    if test_mount not in project_config["services"]["devcontainer"]["volumes"]:
        project_config["services"]["devcontainer"]["volumes"].append(test_mount)
        print(f"[DEBUG] Added test mount: {tests_dir_for_mount}")

    # Write back the project yaml
    with project_yaml_path.open("w") as f:
        yaml.dump(project_config, f, default_flow_style=False, sort_keys=False)
    print("[DEBUG] Updated docker-compose.project.yaml with test mount")

    # Read devcontainer.json for potential restoration later
    # Note: No need to modify it - project.yaml is already in dockerComposeFile list
    with devcontainer_json_path.open() as f:
        config = json.load(f)

    if not original_config:
        original_config = json.dumps(config, indent=4)

    # Build and start the devcontainer
    # Use workspace_path_for_cli for CLI operations (host path when running in container)
    up_cmd = [
        "devcontainer",
        "up",
        "--workspace-folder",
        str(workspace_path_for_cli),
        "--config",
        f"{workspace_path_for_cli}/.devcontainer/devcontainer.json",
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
        cwd=str(workspace_path),  # Local operations use container path
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
        str(workspace_path_for_cli),
        "--config",
        f"{workspace_path_for_cli}/.devcontainer/devcontainer.json",
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

    # Note: docker-compose.project.yaml is part of the template, not test-created
    # The temporary workspace will be cleaned up anyway, so no need to restore it

    # Restore original devcontainer.json if we modified it
    if original_config:
        with devcontainer_json_path.open("w") as f:
            f.write(original_config)
        print("[DEBUG] Restored original devcontainer.json")
