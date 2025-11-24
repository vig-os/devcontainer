# Variables
# Allow TEST_REGISTRY to override REPO for testing (e.g., localhost:5000/test/)
# Strip trailing slashes from REPO to avoid invalid image references
REPO = $(if $(TEST_REGISTRY),$(patsubst %/,%,$(TEST_REGISTRY)),ghcr.io/vig-os/devcontainer)

# Multi-arch support: build for both AMD64 and ARM64
PLATFORMS = linux/amd64,linux/arm64

# Detect native platform for local builds
NATIVE_ARCH := $(shell uname -m)
ifeq ($(NATIVE_ARCH),arm64)
    NATIVE_PLATFORM := linux/arm64
else ifeq ($(NATIVE_ARCH),aarch64)
    NATIVE_PLATFORM := linux/arm64
else
    NATIVE_PLATFORM := linux/amd64
endif

# Build process uses build/ folder - templates are copied and modified there, source files remain unchanged

# Helper functions for help text
define print_help_header
	@echo "Available targets:"
endef

define print_help_targets
	@echo "  info        - Show information about the image"
	@echo "  setup       - Setup configuration"
	@echo "  login       - Login to GitHub Container Registry"
	@echo "  build       - Build local development image"
	@echo "  test        - Run all tests (image, integration, registry)"
	@echo "  test-image  - Run image tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-registry - Run registry tests only"
	@echo "  push VERSION=X.Y     - Build, test, commit, push & tag image:X.Y"
	@echo "  push VERSION=X.Y NO_TEST=1 - Build, commit, push & tag image:X.Y (skip tests)"
	@echo "  push VERSION=X.Y NATIVE_ARCH_ONLY=1 - Build only for native architecture"
	@echo "  pull VERSION={VER}   - Pull image:{VER} (default: latest)"
	@echo "  clean VERSION={VER}  - Remove image:{VER} (default: dev)"
	@echo "  "
	@echo "Examples:"
	@echo "  make build                    # Build local development version"
	@echo "  make push VERSION=1.0        # Build, test, commit, push & tag image:1.0"
	@echo "  make push VERSION=1.0 NO_TEST=1  # Skip tests during push"
	@echo "  make push VERSION=1.0 NATIVE_ARCH_ONLY=1  # Build only native arch"
	@echo "  make pull VERSION=1.0         # Pull image:1.0"
	@echo "  make clean                   # Remove image:dev"
endef

# Default target
.PHONY: help
help:
	$(call print_help_header)
	$(call print_help_targets)

# "all" target shows help
.PHONY: all
all: help

# Show information about the image
.PHONY: info
info:
	@echo "Image: $(REPO)"
	@echo "Containerfile: Containerfile"

# Setup configuration for this project
.PHONY: setup
setup:
	@echo "Setting up configuration..."
	@./scripts/setup.sh

# Test login to GHCR
.PHONY: login
login:
	@echo "Logging in to GitHub Container Registry..."
	@podman login ghcr.io

# Build target: dev
.PHONY: build
build:
	@./scripts/build.sh dev "$(REPO)" "$(NATIVE_PLATFORM)"

# Test targets
# Default VERSION is "dev" if not specified
TEST_VERSION := $(if $(VERSION),$(VERSION),dev)

# Helper to ensure dev image exists before running image/integration tests
.PHONY: _ensure-dev-image
_ensure-dev-image:
	@if ! podman image exists "$(REPO):$(TEST_VERSION)"; then \
		if [ "$(TEST_VERSION)" = "dev" ]; then \
			echo "Building dev image..."; \
			$(MAKE) build; \
		else \
			echo "❌ Image $(REPO):$(TEST_VERSION) not found. Please build it first."; \
			exit 1; \
		fi; \
	fi

# Test image target: runs image tests
.PHONY: test-image
test-image: _ensure-dev-image
	@TEST_CONTAINER_TAG=$(TEST_VERSION) pytest tests/test_image.py -v --tb=short

# Test integration target: runs integration tests
.PHONY: test-integration
test-integration: _ensure-dev-image
	@TEST_CONTAINER_TAG=$(TEST_VERSION) pytest tests/test_integration.py -v --tb=short

# Test registry target: runs registry tests (doesn't need image)
.PHONY: test-registry
test-registry:
	@pytest tests/test_registry.py -v --tb=short

# Test target: runs image and integration tests
.PHONY: test
test: test-image test-integration

# Push target: build, (optionally) test, commit, push & tag a versioned release
# Use NO_TEST=1 to skip tests
.PHONY: push
push:
	@./scripts/push.sh "$(VERSION)" "$(REPO)" "$(NATIVE_PLATFORM)" "$(PLATFORMS)" "$(NO_TEST)" "$(NATIVE_ARCH_ONLY)"

# Pull target: VERSION=latest (default) or VERSION=X.Y
# Uses TEST_REGISTRY if set (via REPO variable)
.PHONY: pull
pull:
	@if [ -z "$(VERSION)" ]; then \
		VERSION="latest"; \
	fi; \
	echo "Pulling image $(REPO):$$VERSION..."; \
	if ! podman pull "$(REPO):$$VERSION" 2>/dev/null; then echo "⚠️  Failed to pull $(REPO):$$VERSION"; fi

# Clean target: VERSION=dev (default) or VERSION=[X.Y, latest]
.PHONY: clean
clean:
	@if [ -z "$(VERSION)" ]; then \
		./scripts/clean.sh dev "$(REPO)"; \
	else \
		./scripts/clean.sh "$(VERSION)" "$(REPO)"; \
	fi
