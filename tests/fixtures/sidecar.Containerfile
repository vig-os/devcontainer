# Test sidecar container for verifying multi-container devcontainer setups
# This sidecar is used to test Approach 1: Direct command execution via podman exec
FROM alpine:latest

# Install minimal tools for testing build workflows
RUN apk add --no-cache \
    bash \
    coreutils

# Create a test build directory
RUN mkdir -p /workspace/build-output

# Just keep the container alive - commands will be executed via podman exec
CMD ["sleep", "infinity"]
