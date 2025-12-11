# Testing Sidecars in This Devcontainer

This devcontainer includes a test-sidecar to demonstrate and verify the
Approach 1 (podman exec) pattern for builder sidecars.

**Important**: This setup uses **Docker-out-of-Docker (DooD)**. The devcontainer
shares the host's Podman socket, so all containers (including sidecars) run at
the host level, not inside the devcontainer. This means the sidecar should be
managed via docker-compose, not manual `podman run` commands.

## What's Included

The `docker-compose.override.yml` includes a `test-sidecar` service that:

- Uses the `localhost/test-sidecar:latest` image
- Stays alive with `sleep infinity`
- Shares the workspace volume
- Is on the same network as the devcontainer

## How to Test (After Opening Devcontainer)

### 1. Verify the sidecar is running

```bash
podman ps --filter name=test-sidecar
```

Expected output:

```text
CONTAINER ID  IMAGE                          COMMAND
...           localhost/test-sidecar:latest  sleep infinity
X minutes ago Up X minutes test-sidecar
```

**Note**: The container name may be `test-sidecar` or `devcontainer-test-sidecar` depending on your compose configuration.

### 2. Execute the test script in the sidecar

```bash
podman exec devcontainer-test-sidecar test-build.sh
```

Expected output:

```text
Hello from sidecar test script
Sidecar is ready for build commands
Communication verified!
```

**Note**: If you get "executable file not found", the sidecar image needs to be rebuilt. See [Need to rebuild the sidecar?](#need-to-rebuild-the-sidecar) below.

### 3. Execute arbitrary commands

```bash
# Check what's in the sidecar
podman exec test-sidecar ls -la /workspace/devcontainer

# Run bash commands
podman exec test-sidecar bash -c "echo 'Building...' && sleep 1 && echo 'Done!'"

# Access shared workspace
podman exec test-sidecar cat /workspace/devcontainer/README.md
```

### 4. Simulate a build workflow

```bash
# Create build artifacts in the sidecar
podman exec test-sidecar bash -c "
  mkdir -p /workspace/devcontainer/build-output
  echo 'Built artifact' > /workspace/devcontainer/build-output/result.txt
  cat /workspace/devcontainer/build-output/result.txt
"

# Verify from devcontainer
cat build-output/result.txt
```

## Real-World Pattern

This demonstrates how you would use builder sidecars:

```yaml
# docker-compose.override.yml
services:
  rust-builder:
    image: rust:1.75-slim
    command: sleep infinity
    volumes:
      - ..:/workspace/myproject:cached
```

Then trigger builds:

```bash
podman exec rust-builder cargo build --release
podman exec rust-builder cargo test
```

## Troubleshooting

### Sidecar not running?

```bash
# Check compose status
podman compose -f .devcontainer/docker-compose.yml \
               -f .devcontainer/docker-compose.override.yml ps

# Restart the sidecar
podman restart test-sidecar
```

### Can't execute commands?

First, verify the script exists in the container:

```bash
# Check if test-build.sh is installed
podman exec test-sidecar which test-build.sh

# Or check the expected location
podman exec test-sidecar ls -la /usr/local/bin/test-build.sh
```

If the script is not found, you need to rebuild the sidecar image (see below).

Make sure the Podman socket is accessible:

```bash
ls -la /var/run/docker.sock
podman version
```

### Need to rebuild the sidecar?

If `test-build.sh` is not found in the container, the image wasn't built or is outdated:

```bash
# Build the sidecar image
cd /workspace/devcontainer/tests/fixtures
podman build -t localhost/test-sidecar:latest -f sidecar.Containerfile .

# Restart the container to use the new image
podman restart test-sidecar
```

**Important**: This devcontainer uses Docker-out-of-Docker (DooD). The `podman`
commands inside the devcontainer communicate with the host's Podman daemon.
The sidecar is managed by docker-compose, so use compose commands to recreate
it properly:

```bash
# From within the devcontainer - specify the compose files
podman compose -f .devcontainer/docker-compose.yml \
               -f .devcontainer/docker-compose.override.yml \
               restart test-sidecar
```

Or simply close and reopen the devcontainer to automatically recreate all services with the new image.

## Cleanup

The sidecar will be automatically stopped when you close the devcontainer.

To manually stop:

```bash
podman stop test-sidecar
podman rm test-sidecar
```
