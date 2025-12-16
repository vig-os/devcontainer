# Use Python 3.12 as base image
FROM python:3.12-slim-trixie

# Add metadata
# By default, we build the dev version unless specified as an argument
ARG IMAGE_TAG="dev"
LABEL maintainer="Carlos Vigo <carlos.vigo@exoma.ch>"
LABEL description="vigOS development environment"
LABEL version="${IMAGE_TAG}"

# OCI standard labels
LABEL org.opencontainers.image.title="vigOS development environment"
LABEL org.opencontainers.image.description="Development environment with common tools and utilities"
LABEL org.opencontainers.image.version="${IMAGE_TAG}"
LABEL org.opencontainers.image.authors="Carlos Vigo <carlos.vigo@exoma.ch>, Lars Gerchow <lars.gerchow@exoma.ch>"
LABEL org.opencontainers.image.vendor="vigOS"
LABEL org.opencontainers.image.source="https://github.com/vig-os/devcontainer"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://github.com/vig-os/devcontainer/blob/main/README.md"
LABEL org.opencontainers.image.url="https://github.com/vig-os/devcontainer"

# Build and runtime information (injected at build time)
ARG BUILD_DATE=""
ARG VCS_REF=""
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.ref.name="${IMAGE_TAG}"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    openssh-client \
    locales \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Generate en_US.UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# Set locale environment variables
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install Podman client for Docker-out-of-Docker (DooD) pattern
# This allows the container to communicate with the host's Podman daemon via mounted socket
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        podman \
    && rm -rf /var/lib/apt/lists/*; \
    podman --version

# Install latest GitHub CLI manually from releases
ARG TARGETARCH=amd64
RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) ARCH=linux_amd64 ;; \
        arm64) ARCH=linux_arm64 ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    GH_VERSION="$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | sed -n 's/.*"tag_name": *"v\?\([^"]*\)".*/\1/p')"; \
    URL=https://github.com/cli/cli/releases/download; \
    BINARY="${URL}/v${GH_VERSION}/gh_${GH_VERSION}_${ARCH}.tar.gz"; \
    CHECKSUM=$(curl -fsSL "${URL}/v${GH_VERSION}/gh_${GH_VERSION}_checksums.txt" | grep "gh_${GH_VERSION}_${ARCH}.tar.gz" | awk '{print $1}'); \
    FILE=gh.tar.gz; \
    curl -fsSL "$BINARY" -o "$FILE"; \
    echo "${CHECKSUM}  ${FILE}" | sha256sum -c -; \
    tar -xzf "$FILE"; \
    mv "gh_${GH_VERSION}_${ARCH}/bin/gh" /usr/local/bin/gh; \
    chmod +x /usr/local/bin/gh; \
    rm -rf "gh_${GH_VERSION}_${ARCH}" "$FILE"; \
    gh --version;

# Install latest uv verifying checksum
RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) ARCH=x86_64-unknown-linux-gnu ;; \
        arm64) ARCH=aarch64-unknown-linux-gnu ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    UV_VERSION="$(curl -fsSL https://api.github.com/repos/astral-sh/uv/releases/latest | sed -n 's/.*"tag_name": *"v\?\([^"]*\)".*/\1/p')"; \
    URL=https://github.com/astral-sh/uv/releases/download; \
    BINARY="${URL}/${UV_VERSION}/uv-${ARCH}.tar.gz"; \
    CHECKSUM=$(curl -fsSL "${BINARY}.sha256" | awk '{print $1}'); \
    FILE=uv.tar.gz; \
    curl -fsSL "$BINARY" -o "$FILE"; \
    echo "${CHECKSUM}  ${FILE}" | sha256sum -c -; \
    tar -xzf "$FILE" -C /usr/local/bin --strip-components=1; \
    rm "$FILE";

# Install Python development tools directly into system using uv
RUN uv pip install --system \
    pre-commit \
    ruff

# Copy assets into container image
COPY assets /root/assets

# Set execute permissions on all shell scripts in the assets
RUN find /root/assets -type f -name "*.sh" -exec chmod +x {} \;

# Note: Container socket configuration is now handled at runtime
# The initialize.sh script detects the host OS and writes CONTAINER_SOCKET_PATH to .env
# docker-compose.yml uses this environment variable for the socket mount

# Generate build-time manifest of files containing placeholders
# This avoids expensive runtime searching in init-workspace.sh
RUN grep -rl '{{SHORT_NAME}}\|{{ORG_NAME}}\|{{IMAGE_TAG}}' /root/assets/workspace/ \
    --exclude-dir=.git \
    --exclude-dir=.venv \
    --exclude-dir=.pre-commit-cache \
    2>/dev/null > /root/assets/.placeholder-manifest.txt || true

# Pre-initialize pre-commit hooks to system cache location
# This cache is used by the container (not copied to workspace by init-workspace.sh)
# Host users will use their own cache (~/.cache/pre-commit or project-local)
WORKDIR /root/assets/workspace
RUN git init && \
    PRE_COMMIT_HOME=/opt/pre-commit-cache \
    pre-commit install-hooks && \
    rm -rf .git

# Pre-build Python virtual environment with template dependencies
# This venv is used directly via UV_PROJECT_ENVIRONMENT (not copied to workspace)
# Temporarily replace {{SHORT_NAME}} placeholder for uv sync, then restore for init-workspace.sh
RUN sed -i 's/{{SHORT_NAME}}/template_project/g' pyproject.toml && \
    uv sync --all-extras --no-install-project && \
    uv pip list && \
    sed -i 's/template_project/{{SHORT_NAME}}/g' pyproject.toml

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Set environment variables
ENV PYTHONUNBUFFERED="1"
ENV IN_CONTAINER="true"

# Create aliases for pre-commit
RUN echo 'alias precommit="pre-commit run"' >> /root/.bashrc

# Default command - interactive shell
CMD ["/bin/bash"]
