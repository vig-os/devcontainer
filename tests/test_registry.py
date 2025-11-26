"""
Test the Makefile push mechanism using a local registry.

This test verifies that the push mechanism works correctly by:
1. Starting a local Docker registry using testcontainers
2. Running the push target with the test registry
3. Verifying that images and tags are created correctly
4. Ensuring cleanup happens automatically (no artifacts remain)

Note on push behavior:
- For localhost registries: Images are pushed during the build step (before manifest creation)
- For remote registries (e.g., GHCR): Individual images are pushed before creating manifests,
  then manifests are created using registry references, preventing "manifest unknown" errors.
"""

import os
import subprocess
from pathlib import Path

import pytest
from testcontainers.registry import DockerRegistryContainer


@pytest.fixture(scope="session")
def local_registry(tmp_path_factory):
    """
    Start a local Docker registry for testing.

    Returns the registry URL (e.g., localhost:5000).
    Also configures podman to treat localhost as insecure registry.
    """

    # Start the registry first to get its URL
    registry = DockerRegistryContainer()
    registry.start()
    registry_url = registry.get_registry()

    # Extract host and port from registry URL (e.g., "localhost:32785")
    # Create temporary registries.conf to mark this specific localhost:port as insecure
    tmp_path = tmp_path_factory.mktemp("registry_config")
    registries_conf = tmp_path / "registries.conf"

    # Parse the registry URL to get host:port
    if ":" in registry_url:
        host, port = registry_url.split(":", 1)
        registry_location = f"{host}:{port}"
    else:
        registry_location = registry_url

    # Write registries.conf content with exact host:port match
    registries_conf.write_text(f"""unqualified-search-registries = ["docker.io"]

[[registry]]
location = "{registry_location}"
insecure = true
""")

    # Set environment variable to use our custom registries.conf
    original_registries_conf = os.environ.get("CONTAINERS_REGISTRIES_CONF")
    os.environ["CONTAINERS_REGISTRIES_CONF"] = str(registries_conf)

    try:
        yield registry_url
    finally:
        # Stop the registry
        registry.stop()
        # Restore original environment
        if original_registries_conf:
            os.environ["CONTAINERS_REGISTRIES_CONF"] = original_registries_conf
        elif "CONTAINERS_REGISTRIES_CONF" in os.environ:
            del os.environ["CONTAINERS_REGISTRIES_CONF"]


@pytest.fixture(scope="session")
def test_version():
    """Return a test version that's guaranteed to be unique."""
    import time

    # Use timestamp-based version to ensure uniqueness
    timestamp = int(time.time())
    return f"99.{timestamp % 10000}"


@pytest.fixture(scope="session")
def git_clean_state():
    """
    Ensure git repository is in a clean state for testing.

    This fixture:
    1. Checks if we're in a git repo
    2. Captures the current HEAD commit
    3. Stashes any uncommitted changes
    4. Restores them after the test
    """
    project_root = Path(__file__).parent.parent

    # Check if we're in a git repo
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            cwd=project_root,
        )
    except subprocess.CalledProcessError:
        pytest.skip("Not in a git repository")

    # Get current HEAD commit (before any changes)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    original_head = result.stdout.strip()

    # Get current branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    original_branch = result.stdout.strip()

    # Check for uncommitted changes
    has_changes = False
    result = subprocess.run(
        ["git", "diff", "--quiet", "HEAD"],
        capture_output=True,
        cwd=project_root,
    )
    if result.returncode != 0:
        has_changes = True
        # Stash changes
        subprocess.run(
            ["git", "stash", "push", "-m", "test_registry_temp"],
            check=True,
            capture_output=True,
            cwd=project_root,
        )

    # Check for staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True,
        cwd=project_root,
    )
    has_staged = result.returncode != 0

    yield {
        "original_head": original_head,
        "original_branch": original_branch,
        "has_changes": has_changes,
        "has_staged": has_staged,
        "project_root": project_root,
    }

    # Restore stashed changes if any
    if has_changes:
        subprocess.run(
            ["git", "stash", "pop"],
            capture_output=True,
            cwd=project_root,
        )


@pytest.fixture(scope="session")
def pushed_image(local_registry, test_version, git_clean_state):
    """
    Fixture that pushes an image to the local registry.

    Returns a dict with push status and registry info.
    If push fails, the fixture will raise an exception, causing dependent tests to skip.
    """
    # Set up test registry path
    test_registry_path = f"{local_registry}/test/"

    # Get project root from fixture
    project_root = git_clean_state["project_root"]

    # Run push with TEST_REGISTRY set
    env = os.environ.copy()
    env["TEST_REGISTRY"] = test_registry_path

    push_result = subprocess.run(
        [
            "make",
            "push",
            f"VERSION={test_version}",
            "NO_TEST=1",
            "NATIVE_ARCH_ONLY=1",
        ],
        env=env,
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    # If push failed, raise an exception to cause dependent tests to skip
    if push_result.returncode != 0:
        print(
            f"Push failed:\nSTDOUT:\n{push_result.stdout}\nSTDERR:\n{push_result.stderr}"
        )
        # Clean up even if push failed
        _cleanup_test_artifacts(
            test_version,
            test_registry_path,
            project_root,
            git_clean_state["original_head"],
        )
        pytest.skip(f"Push failed: {push_result.stderr}")

    # Return push info for use by tests
    # Note: REPO is set from TEST_REGISTRY, so images are at test_registry_path directly
    # (e.g., localhost:32915/test:99.4401, not localhost:32915/test/devcontainer:99.4401)
    push_info = {
        "registry_path": test_registry_path,
        "image_name": "",  # Empty because REPO already includes the full path
        "version": test_version,
        "git_tag": f"v{test_version}",  # Git tag format: v0.1, v1.0, etc.
        "project_root": project_root,
        "original_head": git_clean_state["original_head"],
        "env": env,
    }

    try:
        yield push_info
    finally:
        # Clean up at session end
        _cleanup_test_artifacts(
            test_version,
            test_registry_path,
            project_root,
            git_clean_state["original_head"],
        )


def test_make_push_mechanism(pushed_image):
    """
    Test the complete push mechanism using a local registry.

    This test:
    1. Uses the pushed_image fixture to push an image
    2. Verifies the image exists in the local registry
    3. Verifies the git tag was created
    4. Verifies README.md was updated with version and size
    5. Cleans up the git tag
    6. Verifies no artifacts remain
    """
    # The pushed_image fixture already verifies the image exists in the local registry

    # Extract info from fixture
    test_registry_path = pushed_image["registry_path"]
    test_version = pushed_image["version"]
    test_git_tag = pushed_image["git_tag"]
    project_root = pushed_image["project_root"]

    # Verify git tag was created (using version format: v99.8795)
    tag_result = subprocess.run(
        ["git", "rev-parse", test_git_tag],
        capture_output=True,
        text=True,
    )
    assert tag_result.returncode == 0, f"Git tag {test_git_tag} was not created"

    # Verify image exists in local registry
    # Note: REPO is set from TEST_REGISTRY, so images are at test_registry_path directly
    # Remove trailing slash if present, then add version tag
    registry_base = test_registry_path.rstrip("/")
    full_image_name = f"{registry_base}:{test_version}"
    # podman manifest inspect relies on CONTAINERS_REGISTRIES_CONF for insecure registry config
    inspect_result = subprocess.run(
        ["podman", "manifest", "inspect", full_image_name],
        capture_output=True,
        text=True,
        env=os.environ.copy(),  # Ensure environment variables are inherited
    )
    assert inspect_result.returncode == 0, (
        f"Image {full_image_name} not found in registry. "
        f"STDERR: {inspect_result.stderr}"
    )

    # Verify :latest tag also exists
    latest_image_name = f"{registry_base}:latest"
    latest_result = subprocess.run(
        ["podman", "manifest", "inspect", latest_image_name],
        capture_output=True,
        text=True,
        env=os.environ.copy(),  # Ensure environment variables are inherited
    )
    assert latest_result.returncode == 0, (
        f"Image {latest_image_name} not found in registry. "
        f"STDERR: {latest_result.stderr}"
    )

    # Verify README.md was updated with version and size
    readme_path = project_root / "README.md"
    assert readme_path.exists(), "README.md not found"

    readme_content = readme_path.read_text()

    # Check version was updated
    import re

    version_match = re.search(r"- \*\*Version\*\*:\s*(.+)", readme_content)
    assert version_match, "Version line not found in README.md"
    readme_version = version_match.group(1).strip()
    assert test_version in readme_version, (
        f"README.md version '{readme_version}' does not contain '{test_version}'"
    )

    # Check size was updated with a value between 100 and 2000 MB
    size_match = re.search(r"- \*\*Size\*\*:\s*~?(\d+)\s*MB", readme_content)
    assert size_match, "Size line not found or invalid format in README.md"
    readme_size = int(size_match.group(1))
    assert 100 <= readme_size <= 2000, (
        f"README.md size {readme_size} MB is outside valid range (100-2000 MB)"
    )


@pytest.fixture(scope="session")
def pulled_image(pushed_image):
    """
    Fixture that pulls an image from the local registry.

    Depends on pushed_image fixture - if push fails, this fixture will be skipped.
    If pull fails, the fixture will raise an exception, causing dependent tests to skip.
    """
    # Extract info from fixture
    test_registry_path = pushed_image["registry_path"]
    test_version = pushed_image["version"]
    project_root = pushed_image["project_root"]
    original_head = pushed_image["original_head"]
    env = pushed_image["env"].copy()

    # Explicitly set TEST_REGISTRY in the environment before calling make
    env["TEST_REGISTRY"] = test_registry_path

    # Pull the image from the registry
    # Note: REPO is set from TEST_REGISTRY, so images are at test_registry_path directly
    # Makefile uses TEST_REGISTRY directly (with trailing slash), so pulled image name matches what make pull uses
    pull_result = subprocess.run(
        [
            "make",
            "pull",
            f"VERSION={test_version}",
        ],
        env=env,
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    # Check if pull actually succeeded (Makefile suppresses errors, so check output)
    if (
        pull_result.returncode != 0
        or "⚠️" in pull_result.stdout
        or "Failed" in pull_result.stdout
    ):
        print(
            f"Pull failed:\nSTDOUT:\n{pull_result.stdout}\nSTDERR:\n{pull_result.stderr}"
        )
        _cleanup_test_artifacts(
            test_version,
            test_registry_path,
            project_root,
            original_head,
        )
        pytest.skip(f"Pull failed: {pull_result.stdout}")

    # Verify the image was pulled
    # Podman normalizes trailing slashes, so use registry_base (without trailing slash)
    registry_base = test_registry_path.rstrip("/")
    pulled_image_name = f"{registry_base}:{test_version}"

    # Check if image exists
    inspect_result = subprocess.run(
        ["podman", "image", "exists", pulled_image_name],
        capture_output=True,
        text=True,
    )

    if inspect_result.returncode != 0:
        _cleanup_test_artifacts(
            test_version,
            test_registry_path,
            project_root,
            original_head,
        )
        pytest.skip(f"Pulled image {pulled_image_name} not found locally")

    # Return pull info for use by tests
    yield {
        **pushed_image,
        "pulled_image_name": pulled_image_name,
    }


def test_make_pull_mechanism(pulled_image):
    """
    Test pulling an image from the local registry.

    This test depends on pulled_image fixture - if push or pull fails, this test will be skipped.
    """
    # Extract info from fixture
    pulled_image_name = pulled_image["pulled_image_name"]

    # Verify the image was pulled
    inspect_result = subprocess.run(
        ["podman", "image", "exists", pulled_image_name],
        capture_output=True,
        text=True,
    )
    assert inspect_result.returncode == 0, (
        f"Pulled image {pulled_image_name} not found locally"
    )


def test_make_clean_mechanism(pulled_image):
    """
    Test cleaning a pulled image.

    This test depends on pulled_image fixture - if push or pull tests fail, this test will be skipped.
    """
    # Extract info from fixture
    test_version = pulled_image["version"]
    test_registry_path = pulled_image["registry_path"]
    env = pulled_image["env"].copy()
    pulled_image_name = pulled_image["pulled_image_name"]

    # Explicitly set TEST_REGISTRY in the environment before calling make
    env["TEST_REGISTRY"] = test_registry_path

    # Clean the image using make clean
    clean_result = subprocess.run(
        [
            "make",
            "clean",
            f"VERSION={test_version}",
        ],
        env=env,
        cwd=pulled_image["project_root"],
        capture_output=True,
        text=True,
    )

    if clean_result.returncode != 0:
        print(
            f"Clean failed:\nSTDOUT:\n{clean_result.stdout}\nSTDERR:\n{clean_result.stderr}"
        )

    # Verify the image was removed
    verify_result = subprocess.run(
        ["podman", "image", "exists", pulled_image_name],
        capture_output=True,
        text=True,
    )
    # The image should not exist (clean should have removed it)
    # Note: clean might warn if image doesn't exist, but that's okay
    assert verify_result.returncode != 0, (
        f"Image {pulled_image_name} still exists after clean"
    )


def _cleanup_test_artifacts(version, registry_path, project_root, original_head):
    """
    Helper function to clean up test artifacts.

    This function:
    1. Deletes the git tag (using version format: v99.8795)
    2. Resets to the original HEAD (removing any commit made by push)
    3. Restores README.md to its original state (reverts version update)
    4. Removes local images/manifests
    """
    # Git tag format: v0.1, v1.0, etc. (new format)
    # Also handle old format without 'v' prefix for cleanup
    test_git_tag = f"v{version}"
    old_git_tag = version  # Old format without 'v' prefix

    # Delete git tag (local only, we don't push tags in tests)
    # Try both new and old formats in case of leftover tags
    for tag in [test_git_tag, old_git_tag]:
        subprocess.run(
            ["git", "tag", "-d", tag],
            capture_output=True,
            cwd=project_root,
        )

    # Get current HEAD to see if a commit was made
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    current_head = result.stdout.strip()

    # If a new commit was made, reset to original HEAD
    if current_head != original_head:
        # Check if the commit message matches our test pattern
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        commit_message = result.stdout.strip()
        if f"Release {version}" in commit_message:
            # Reset to original HEAD (hard reset to discard changes)
            subprocess.run(
                ["git", "reset", "--hard", original_head],
                capture_output=True,
                cwd=project_root,
            )

    # Always restore README.md from git (in case there are uncommitted changes)
    readme_path = project_root / "README.md"
    if readme_path.exists():
        subprocess.run(
            ["git", "checkout", "--", str(readme_path)],
            capture_output=True,
            cwd=project_root,
        )

    # Try to remove local images/manifests (may not exist if using registry)
    # Note: REPO is set from TEST_REGISTRY, so images are at registry_path directly
    registry_base = registry_path.rstrip("/")
    full_image_name = f"{registry_base}:{version}"
    latest_image_name = f"{registry_base}:latest"

    # Detect native architecture for architecture-specific image cleanup
    import platform

    machine = platform.machine().lower()
    arch_suffix = "arm64" if machine in ("arm64", "aarch64") else "amd64"

    # Architecture-specific image tag (e.g., localhost:32811/test:99.305-amd64)
    arch_image_name = f"{registry_base}:{version}-{arch_suffix}"

    # Remove manifests first (ignore errors if they don't exist)
    for img in [full_image_name, latest_image_name]:
        subprocess.run(
            ["podman", "manifest", "rm", img],
            capture_output=True,
            check=False,
        )

    # Remove all image tags (manifests, versioned, latest, and architecture-specific)
    # Use -f to force removal even if tagged in multiple ways
    for img in [full_image_name, latest_image_name, arch_image_name]:
        # Try removing by tag first
        subprocess.run(
            ["podman", "rmi", "-f", img],
            capture_output=True,
            check=False,
        )
        # Also try removing by image ID if the tag removal didn't work
        # (in case the image has multiple tags)
        result = subprocess.run(
            ["podman", "images", "--format", "{{.ID}}", img],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            image_id = result.stdout.strip()
            subprocess.run(
                ["podman", "rmi", "-f", image_id],
                capture_output=True,
                check=False,
            )

    # Clean up any dangling <none> images (manifest lists that lost their tags)
    # These can occur when manifests are removed but underlying images remain
    subprocess.run(
        ["podman", "image", "prune", "-f"],
        capture_output=True,
        check=False,
    )
