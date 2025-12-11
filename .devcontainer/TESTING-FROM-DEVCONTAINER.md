# Testing from Within a Devcontainer

This document explains how to run the devcontainer integration tests from within the devcontainer itself.

## The Problem

When running tests from inside a devcontainer (Docker-out-of-Docker / DooD),
the original test code failed with errors like:

```text
statfs /workspace/devcontainer/tests/tmp/workspace-devcontainer-qpmyh0nl:
no such file or directory
```

**Root Cause**: The tests created temp directories at container paths (e.g.,
`/workspace/devcontainer/tests/tmp/...`) and tried to mount them with
`podman run -v /container/path:/workspace`. But when running inside a
devcontainer, the `podman` command talks to the **host's podman daemon**,
which doesn't have access to paths that only exist inside the devcontainer.

## The Solution

The test infrastructure now automatically detects when it's running inside a container and switches strategies:

### 1. Use Podman with Named Volumes

Instead of direct bind mounts with host paths, we use **named volumes**:

```bash
# Create a named volume
podman volume create test-workspace-XXXX

# Run with named volume - no host path needed!
podman run -it --rm \
  -v test-workspace-XXXX:/workspace \
  ghcr.io/vig-os/devcontainer:dev \
  /root/assets/init-workspace.sh
```

**Benefits**:

- Named volumes work everywhere without compose dependency
- Avoids path translation issues entirely
- Works from both host and container environments
- No need to know the host path

### 2. Container Detection

The test fixtures detect the container environment by checking:

```python
def is_running_in_container() -> bool:
    """Detect if we're running inside a container."""
    if os.environ.get("IN_CONTAINER") == "true":
        return True
    if Path("/.dockerenv").exists():
        return True
    if Path("/run/.containerenv").exists():
        return True
    try:
        with open("/proc/1/cgroup", "r") as f:
            return "docker" in f.read() or "podman" in f.read()
    except (FileNotFoundError, PermissionError):
        pass
    return False
```

### 3. Path Translation (Optional)

For devcontainer CLI tests that need host paths, set `HOST_WORKSPACE_PATH`:

```bash
export HOST_WORKSPACE_PATH=/Users/you/Projects/devcontainer
```

The `get_host_path()` function translates container paths to host paths:

```python
def get_host_path(container_path: Path) -> Path:
    """Translate container path to host path for DooD."""
    host_workspace = os.environ.get("HOST_WORKSPACE_PATH")
    if not host_workspace:
        return container_path

    # Translate /workspace/devcontainer/... to host path
    container_path_str = str(container_path.resolve())
    if container_path_str.startswith("/workspace/devcontainer"):
        relative = container_path_str[len("/workspace/devcontainer"):]
        return Path(host_workspace + relative)

    return container_path
```

## Test Workflow

### Basic Tests (No Configuration Needed)

```bash
cd /workspace/devcontainer
make test-integration
```

The `initialized_workspace` fixture:
1. Detects it's in a container
2. Creates a named volume with `podman volume create`
3. Runs `podman run -v volume:/workspace` to initialize the workspace
4. Copies files from the named volume to a temp directory for inspection
5. Cleans up the volume after tests complete

### Devcontainer CLI Tests (Automatic in This Devcontainer)

For **this devcontainer** (developing the devcontainer itself), `HOST_WORKSPACE_PATH` is **automatically set** via `.devcontainer/devcontainer.json`:

```json
"remoteEnv": {
    "HOST_WORKSPACE_PATH": "${localWorkspaceFolder}"
}
```

VS Code expands `${localWorkspaceFolder}` to the host path, so you can just run:

```bash
make test-integration
```

The `devcontainer_up` and `devcontainer_with_sidecar` fixtures:
1. Detect they're in a container
2. Use `HOST_WORKSPACE_PATH` environment variable (automatically set)
3. Translate paths using `get_host_path()`
4. Pass host paths to devcontainer CLI commands

**For other devcontainers**: If running these tests elsewhere, manually set:

```bash
export HOST_WORKSPACE_PATH=/path/on/host/to/workspace
```

Without `HOST_WORKSPACE_PATH`, these tests are skipped (but basic tests still run).

## Files Changed

### New Files

- `tests/docker-compose.test.yml` - Reference compose file (tests use direct podman commands)
- `tests/README.md` - Test running documentation
- `.devcontainer/TESTING-FROM-DEVCONTAINER.md` - This file

### Modified Files

- `tests/conftest.py` - Added container detection and named volume-based workspace initialization
- `.devcontainer/devcontainer.json` - Added `remoteEnv` with `HOST_WORKSPACE_PATH` for automatic path translation

## Benefits

1. **Develop from within itself**: You can now develop and test the devcontainer from inside the devcontainer
2. **Fully automatic for this devcontainer**: `HOST_WORKSPACE_PATH` is automatically set via `remoteEnv` in devcontainer.json
3. **No manual configuration needed**: Just open the devcontainer and run tests
4. **Works for everyone**: `${localWorkspaceFolder}` expands to the correct host path for any developer
5. **Backward compatible**: Tests still work from the host without any changes
6. **Only affects this devcontainer**: Workspaces created FROM this image don't inherit this setting

## Example Session

```bash
# Open the devcontainer
code /workspace/devcontainer

# Inside the devcontainer:
cd /workspace/devcontainer

# Build the image (via DooD)
make build

# Run ALL integration tests (including devcontainer CLI tests)
make test-integration
# ✅ Works! HOST_WORKSPACE_PATH is automatically set via remoteEnv
# - Basic tests use compose with named volumes
# - Devcontainer CLI tests use automatic path translation
```

## Architecture Diagram

```text
┌─────────────────────────────────────────────────────┐
│ Host Machine                                        │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Your Devcontainer (where you run tests)     │  │
│  │                                              │  │
│  │  $ make test-integration                    │  │
│  │    ↓                                         │  │
│  │  1. Detect: "I'm in a container"            │  │
│  │  2. Use: podman compose + named volumes     │  │
│  │  3. Talk to: Host's podman daemon (socket)  │  │
│  │                 ↓                            │  │
│  └─────────────────┼────────────────────────────┘  │
│                    ↓ (via socket)                   │
│  ┌─────────────────────────────────────────────┐   │
│  │ Host Podman Daemon                          │   │
│  │                                             │   │
│  │  • Creates named volume                     │   │
│  │  • Runs test container                      │   │
│  │  • Mounts volume → /workspace               │   │
│  │  • Returns results                          │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Key Insight

The breakthrough was realizing that when you use `podman` from inside a devcontainer, you're not talking to podman *inside* the container - you're talking to the **host's podman daemon** via the socket. So:

- ❌ Bind mounts with container paths fail (host can't see them)
- ✅ Named volumes work (compose manages them on the host)
- ✅ Path translation works (convert container → host paths)

This is the same pattern used for builder sidecars in `SIDECAR-TESTING.md` - it's all Docker-out-of-Docker (DooD)!
