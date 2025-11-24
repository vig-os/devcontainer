#!/bin/bash

# Testinfra test runner for single image repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
    esac
}

# Argument: optional tag (default: dev)
TAG=${1:-dev}

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration - single image repository
IMAGE_NAME="ghcr.io/vig-os/devcontainer:$TAG"
CONTAINER_NAME="test-devcontainer"

echo -e "${BLUE}Starting Tests Suite for Container image:devcontainer:$TAG${NC}"
echo "================================================================"

# Function to cleanup containers
cleanup() {
    print_status "info" "Cleaning up test containers..."
    podman stop "$CONTAINER_NAME" 2>/dev/null || true
    podman rm "$CONTAINER_NAME" 2>/dev/null || true
}

# Set up cleanup on exit
trap cleanup EXIT

# Check prerequisites
print_status "info" "Checking prerequisites..."

# Check if podman is available
if ! command -v podman &> /dev/null; then
    print_status "error" "podman is not installed or not in PATH"
    exit 1
fi

# Check if image exists
if ! podman image exists "$IMAGE_NAME"; then
    print_status "error" "Image $IMAGE_NAME not found. Please build it first with 'make build'"
    exit 1
fi

# Check if tests directory exists
if [[ ! -d tests ]]; then
    print_status "error" "Missing tests directory: tests/"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_status "warning" "Virtual environment not activated. Activating..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

# Note: Container will be created by pytest fixtures
print_status "info" "Test container will be created by pytest fixtures..."

# Run Testinfra tests
print_status "info" "Running tests..."

# Run tests - pass container name and tag as environment variables
# conftest.py expects TEST_CONTAINER_NAME and TEST_CONTAINER_TAG
if ! TEST_CONTAINER_NAME=devcontainer TEST_CONTAINER_TAG=$TAG pytest tests/ \
    --tb=short \
    -v; then
    print_status "error" "Tests failed"
    exit 1
fi

# If we get here, all tests passed
print_status "success" "All tests passed!"
echo ""
print_status "info" "Image devcontainer:$TAG is ready for deployment to GHCR"
echo ""
print_status "info" "Next steps:"
echo "  1. Check access to GHCR with:   make login"
echo "  2. Push the image with:         make push VERSION=X.Y"
