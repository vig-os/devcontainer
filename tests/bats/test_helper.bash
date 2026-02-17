# BATS test helper — loads BATS libraries and performs project-specific setup
#
# Usage (in every .bats file):
#   setup() { load test_helper; }

# Resolve project root (two levels up from tests/bats/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PROJECT_ROOT

# Load BATS helper libraries from node_modules
load "${PROJECT_ROOT}/node_modules/bats-support/load"
load "${PROJECT_ROOT}/node_modules/bats-assert/load"
load "${PROJECT_ROOT}/node_modules/bats-file/load"
